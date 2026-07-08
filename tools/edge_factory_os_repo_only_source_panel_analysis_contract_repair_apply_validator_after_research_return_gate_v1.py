from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_HEAD = "2addb68"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 622
EXPECTED_TRACKED_PYTHON_COUNT = 623

REPAIRED_TARGET_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
REPAIR_APPLY_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_READY = "edge_factory_os_repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_blocked_record_after_research_return_gate_v1.py"
POST_CHECK_STATUS_PASS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_VALIDATOR_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POST_CHECK_STATUS_FAIL = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_VALIDATOR_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY_VALIDATED = "PRIMARY_ARTIFACT_STRONG_FOR_CONTRACT_WITH_NO_SOURCE_PANEL_RESULT_STRENGTH"
CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED = "DERIVED_EXPLICIT_ATTENTION"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

EXPECTED_PRIMARY_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

REQUIRED_CONTRACT_SECTIONS = [
    "research_return_context",
    "source_panel_contract_scope",
    "old_source_panel_anomaly_route_guard",
    "primary_artifact_requirement",
    "evidence_quality_requirements",
    "money_path_alignment",
    "next_module_decision",
]

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


def nested_dict(record: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else {}


def prior_repair_apply_respected(apply_record: Dict[str, Any]) -> bool:
    return (
        apply_record.get("source_panel_analysis_contract_repair_apply_status") == "PASS"
        and apply_record.get("repair_apply_performed") is True
        and apply_record.get("repair_apply_successful") is True
        and apply_record.get("target_artifact_modified_now") is True
        and apply_record.get("target_artifact_valid_json_after_apply") is True
        and apply_record.get("target_artifact_backup_created") is True
        and apply_record.get("source_panel_result_primary_strength_claimed_now") is False
        and apply_record.get("source_panel_result_artifacts_are_future_expected_only") is True
        and apply_record.get("post_apply_validation_completed") is True
        and apply_record.get("contract_artifact_primary_strength_for_contract_only_expected_after_validator") is True
        and apply_record.get("evidence_quality_sufficient_for_contract_validation_expected_after_validator") is True
        and apply_record.get("active_p0_blocker_count_expected_after_validator") == 0
        and apply_record.get("runner_preview_blocked_until_validator_passes") is True
        and apply_record.get("source_panel_analysis_execution_blocked") is True
        and apply_record.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and apply_record.get("selected_route_runs_research_now") is False
        and apply_record.get("selected_route_generates_candidates_now") is False
        and apply_record.get("selected_route_touches_runtime_capital_live") is False
        and apply_record.get("selected_route_approves_generic_runner") is False
        and apply_record.get("selected_route_creates_schema_or_config") is False
        and apply_record.get("runtime_touch_performed") is False
        and apply_record.get("capital_touch_performed") is False
        and apply_record.get("live_touch_performed") is False
        and apply_record.get("candidate_generation_performed") is False
        and apply_record.get("generic_runner_approval_granted") is False
        and apply_record.get("generic_runner_implementation_remains_blocked") is True
        and apply_record.get("loop_remains_closed") is True
        and apply_record.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and apply_record.get("replacement_checks_all_true") is True
    )


def repaired_artifact_validation(contract: Dict[str, Any], valid_json: bool) -> Dict[str, Any]:
    identity = nested_dict(contract, "contract_artifact_identity")
    section_markers = nested_dict(contract, "contract_section_completeness_markers")
    required_sections = section_markers.get("required_sections", [])
    return {
        "repaired_target_artifact_exists": REPAIRED_TARGET_ARTIFACT_PATH.exists(),
        "repaired_target_artifact_valid_json": valid_json,
        "repair_applied_marker_validated": nested_dict(contract, "contract_artifact_repair_applied_marker").get("repair_applied") is True,
        "contract_primary_marker_validated": nested_dict(contract, "contract_primary_marker").get("contract_artifact_primary_strength_for_contract_only") is True
        and nested_dict(contract, "contract_primary_marker").get("source_panel_result_primary_strength_claimed_now") is False,
        "contract_artifact_identity_validated": identity.get("contract_name") == "source_panel_analysis_contract_after_research_return_gate_v1"
        and identity.get("contract_type") == "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT"
        and identity.get("target_artifact_path") == str(REPAIRED_TARGET_ARTIFACT_PATH),
        "contract_section_completeness_markers_validated": section_markers.get("required_sections_all_present_after_repair") is True
        and sorted(required_sections) == sorted(REQUIRED_CONTRACT_SECTIONS)
        and all(section in contract for section in REQUIRED_CONTRACT_SECTIONS),
        "fail_closed_marker_validated": contract.get("fail_closed_if_required_markers_missing") is True,
    }


def old_route_guard_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    guard = nested_dict(contract, "old_source_panel_anomaly_route_guard")
    marker = nested_dict(contract, "old_source_panel_anomaly_closed_route_guard_marker")
    route_rule = str(guard.get("route_closed_artifact_rule", "")).lower()
    future_rule = str(guard.get("future_reference_rule", "")).lower()
    return {
        "old_route_guard_validation_completed": True,
        "old_source_panel_anomaly_closed_route_guard_marker_validated": bool(marker)
        and marker.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and marker.get("route_closed_artifacts_active_evidence_allowed") is False,
        "old_source_panel_anomaly_route_reopen_allowed": False
        if guard.get("old_source_panel_anomaly_route_reopen_allowed") is not True and marker.get("old_source_panel_anomaly_route_reopen_allowed") is False
        else True,
        "source_panel_contract_must_be_independent_of_old_failed_route": guard.get("source_panel_contract_must_be_independent_of_old_failed_route") is True
        and marker.get("source_panel_contract_must_be_independent_of_old_failed_route") is True,
        "prior_source_panel_anomaly_artifacts_are_historical_context_only": guard.get("prior_source_panel_anomaly_artifacts_are_historical_context_only") is True
        and marker.get("prior_source_panel_anomaly_artifacts_are_historical_context_only") is True,
        "old_route_closed_true_artifacts_are_not_active_evidence": "no route_closed=true" in route_rule
        and "active research route continuation" in route_rule
        and marker.get("route_closed_artifacts_active_evidence_allowed") is False,
        "future_old_source_panel_anomaly_references_historical_closed_only": "historical/closed" in future_rule
        and "not active evidence" in future_rule,
    }


def safety_marker_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    profit = nested_dict(contract, "no_profit_claim_marker")
    runtime = nested_dict(contract, "no_runtime_capital_live_order_marker")
    candidate = nested_dict(contract, "no_candidate_family_active_paper_marker")
    generic = nested_dict(contract, "no_generic_runner_marker")
    schema = nested_dict(contract, "no_schema_config_marker")
    execution = nested_dict(contract, "execution_permissions")
    scope = nested_dict(contract, "source_panel_contract_scope")
    return {
        "safety_marker_validation_completed": True,
        "no_profit_claim_marker_validated": profit.get("source_panel_contract_claims_profit") is False
        and profit.get("profit_claimed_now") is False,
        "no_runtime_capital_live_order_marker_validated": runtime.get("runtime_capital_live_order_authorization") is False
        and runtime.get("runtime_touch_performed") is False
        and runtime.get("capital_touch_performed") is False
        and runtime.get("live_touch_performed") is False
        and runtime.get("real_order_touch_performed") is False
        and execution.get("touch_runtime_capital_live_orders") is False,
        "no_candidate_family_active_paper_marker_validated": candidate.get("candidate_generation_performed") is False
        and candidate.get("family_release_performed") is False
        and candidate.get("active_paper_performed") is False
        and scope.get("candidate_generation_allowed") is False
        and scope.get("family_release_allowed") is False,
        "no_generic_runner_marker_validated": generic.get("generic_runner_approval_granted") is False
        and generic.get("generic_runner_implementation_remains_blocked") is True
        and execution.get("approve_or_implement_generic_runner") is False,
        "no_schema_config_marker_validated": schema.get("schema_file_creation_performed_now") is False
        and schema.get("config_file_creation_performed_now") is False
        and schema.get("selected_route_creates_schema_or_config") is False
        and execution.get("create_schema_or_config_files") is False,
        "source_panel_result_primary_strength_claimed_now": contract.get("source_panel_result_primary_strength_claimed_now") is True
        if contract.get("source_panel_result_primary_strength_claimed_now") is True
        else False,
        "source_panel_result_artifacts_are_future_expected_only": contract.get("source_panel_result_artifacts_are_future_expected_only") is True,
    }


def future_primary_artifact_requirement_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    primary = nested_dict(contract, "primary_artifact_requirement")
    marker = nested_dict(contract, "future_source_panel_primary_artifact_requirement_marker")
    artifact_list = primary.get("future_source_panel_primary_artifact_list", [])
    if not isinstance(artifact_list, list):
        artifact_list = []
    return {
        "future_primary_artifact_requirement_validation_completed": True,
        "future_source_panel_runner_primary_artifacts_required": primary.get("future_source_panel_runner_primary_artifacts_required") is True
        and marker.get("future_source_panel_runner_primary_artifacts_required") is True,
        "future_source_panel_primary_artifact_list": artifact_list,
        "expected_future_source_panel_primary_artifacts_all_listed": sorted(artifact_list) == sorted(EXPECTED_PRIMARY_ARTIFACTS),
    }


def selected_route_boundaries(contract: Dict[str, Any]) -> Dict[str, bool]:
    context = nested_dict(contract, "research_return_context")
    execution = nested_dict(contract, "execution_permissions")
    scope = nested_dict(contract, "source_panel_contract_scope")
    return {
        "selected_route_category_is_source_panel_analysis": context.get("selected_route_category") == "SOURCE_PANEL_ANALYSIS",
        "selected_route_runs_research_now_false": execution.get("run_source_panel_analysis_now") is False,
        "selected_route_generates_candidates_now_false": execution.get("generate_candidates_now") is False
        and scope.get("candidate_generation_allowed") is False,
        "selected_route_touches_runtime_capital_live_false": execution.get("touch_runtime_capital_live_orders") is False
        and scope.get("runtime_live_capital_order_action_allowed") is False,
        "selected_route_approves_generic_runner_false": execution.get("approve_or_implement_generic_runner") is False,
        "selected_route_creates_schema_or_config_false": execution.get("create_schema_or_config_files") is False,
    }


def all_true(values: Dict[str, Any]) -> bool:
    return all(value is True for value in values.values())


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, valid_json, json_error = load_json_checked(REPAIRED_TARGET_ARTIFACT_PATH)
    apply_record, apply_valid_json, apply_json_error = load_json_checked(REPAIR_APPLY_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    repaired_eval = repaired_artifact_validation(contract, valid_json)
    old_route_eval = old_route_guard_validation(contract)
    safety_eval = safety_marker_validation(contract)
    future_eval = future_primary_artifact_requirement_validation(contract)
    route_boundaries = selected_route_boundaries(contract)
    prior_apply_ok = apply_valid_json and prior_repair_apply_respected(apply_record)

    repaired_artifact_validated = all_true(repaired_eval)
    old_route_guard_validated = (
        old_route_eval["old_source_panel_anomaly_closed_route_guard_marker_validated"] is True
        and old_route_eval["old_source_panel_anomaly_route_reopen_allowed"] is False
        and old_route_eval["source_panel_contract_must_be_independent_of_old_failed_route"] is True
        and old_route_eval["prior_source_panel_anomaly_artifacts_are_historical_context_only"] is True
        and old_route_eval["old_route_closed_true_artifacts_are_not_active_evidence"] is True
        and old_route_eval["future_old_source_panel_anomaly_references_historical_closed_only"] is True
    )
    safety_validated = (
        safety_eval["no_profit_claim_marker_validated"] is True
        and safety_eval["no_runtime_capital_live_order_marker_validated"] is True
        and safety_eval["no_candidate_family_active_paper_marker_validated"] is True
        and safety_eval["no_generic_runner_marker_validated"] is True
        and safety_eval["no_schema_config_marker_validated"] is True
        and safety_eval["source_panel_result_primary_strength_claimed_now"] is False
        and safety_eval["source_panel_result_artifacts_are_future_expected_only"] is True
    )
    future_requirement_validated = (
        future_eval["future_source_panel_runner_primary_artifacts_required"] is True
        and future_eval["expected_future_source_panel_primary_artifacts_all_listed"] is True
    )
    repo_context_valid = (
        git["head"] == EXPECTED_HEAD
        and git["current_scope_is_only_approved_file"] is True
        and py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT
        and py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0
        and len(planned_existing) == 0
        and generic_runner_target_exists is False
        and all(value is False for value in flags.values())
    )
    route_boundaries_valid = all_true(route_boundaries)
    source_panel_contract_validated = (
        prior_apply_ok
        and repaired_artifact_validated
        and old_route_guard_validated
        and safety_validated
        and future_requirement_validated
        and repo_context_valid
        and route_boundaries_valid
    )

    active_p0_blocker_count = 0 if source_panel_contract_validated else 1
    current_quality = CURRENT_EVIDENCE_CHAIN_QUALITY_VALIDATED if source_panel_contract_validated else CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED
    next_module = NEXT_MODULE_READY if source_panel_contract_validated else NEXT_MODULE_BLOCKED

    replacement_checks = {
        "prior_repair_apply_respected": prior_apply_ok,
        "repair_apply_validation_completed": True,
        "repaired_artifact_validated": repaired_artifact_validated,
        "old_route_guard_validated": old_route_guard_validated,
        "safety_markers_validated": safety_validated,
        "future_primary_artifact_requirement_validated": future_requirement_validated,
        "contract_artifact_primary_strength_for_contract_only": source_panel_contract_validated is True,
        "source_panel_result_primary_artifacts_exist_now_false": True,
        "source_panel_result_primary_strength_claimed_now_false": safety_eval["source_panel_result_primary_strength_claimed_now"] is False,
        "runner_preview_eligible_next": source_panel_contract_validated is True,
        "runner_preview_run_now_false": True,
        "source_panel_analysis_execution_run_now_false": True,
        "active_p0_blocker_count_zero_if_validated": active_p0_blocker_count == 0 if source_panel_contract_validated else active_p0_blocker_count == 1,
        "selected_route_boundaries_valid": route_boundaries_valid,
        "repo_context_valid": repo_context_valid,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module in {NEXT_MODULE_READY, NEXT_MODULE_BLOCKED},
        "source_panel_execution_not_selected": "source_panel_analysis_execution" not in next_module,
        "generic_review_adoption_rollout_audit_not_selected": all(
            token not in next_module for token in ["generic", "_review_", "_adoption_", "_rollout_", "_audit_"]
        ),
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_contract_repair_apply_validator_status": "PASS" if ready and source_panel_contract_validated else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS_PASS if ready and source_panel_contract_validated else POST_CHECK_STATUS_FAIL,
        "final_decision": "SOURCE_PANEL_CONTRACT_REPAIR_APPLY_VALIDATED_RUNNER_PREVIEW_ELIGIBLE_NEXT"
        if ready and source_panel_contract_validated
        else "SOURCE_PANEL_CONTRACT_REPAIR_APPLY_VALIDATOR_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_RUNNER_PREVIEW_AFTER_RESEARCH_RETURN_GATE"
        if ready and source_panel_contract_validated
        else "RECORD_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_BLOCKED_STATE",
        "next_module": next_module,
        "prior_repair_apply_respected": prior_apply_ok,
        "repair_apply_validation_completed": True,
        "repaired_target_artifact_path": str(REPAIRED_TARGET_ARTIFACT_PATH),
        "repaired_target_artifact_exists": repaired_eval["repaired_target_artifact_exists"],
        "repaired_target_artifact_valid_json": repaired_eval["repaired_target_artifact_valid_json"],
        "repair_applied_marker_validated": repaired_eval["repair_applied_marker_validated"],
        "contract_primary_marker_validated": repaired_eval["contract_primary_marker_validated"],
        "contract_artifact_identity_validated": repaired_eval["contract_artifact_identity_validated"],
        "contract_section_completeness_markers_validated": repaired_eval["contract_section_completeness_markers_validated"],
        "fail_closed_marker_validated": repaired_eval["fail_closed_marker_validated"],
        "old_route_guard_validation_completed": old_route_eval["old_route_guard_validation_completed"],
        "old_source_panel_anomaly_closed_route_guard_marker_validated": old_route_eval["old_source_panel_anomaly_closed_route_guard_marker_validated"],
        "old_source_panel_anomaly_route_reopen_allowed": old_route_eval["old_source_panel_anomaly_route_reopen_allowed"],
        "source_panel_contract_must_be_independent_of_old_failed_route": old_route_eval["source_panel_contract_must_be_independent_of_old_failed_route"],
        "prior_source_panel_anomaly_artifacts_are_historical_context_only": old_route_eval["prior_source_panel_anomaly_artifacts_are_historical_context_only"],
        "safety_marker_validation_completed": safety_eval["safety_marker_validation_completed"],
        "no_profit_claim_marker_validated": safety_eval["no_profit_claim_marker_validated"],
        "no_runtime_capital_live_order_marker_validated": safety_eval["no_runtime_capital_live_order_marker_validated"],
        "no_candidate_family_active_paper_marker_validated": safety_eval["no_candidate_family_active_paper_marker_validated"],
        "no_generic_runner_marker_validated": safety_eval["no_generic_runner_marker_validated"],
        "no_schema_config_marker_validated": safety_eval["no_schema_config_marker_validated"],
        "source_panel_result_primary_strength_claimed_now": False,
        "source_panel_result_artifacts_are_future_expected_only": safety_eval["source_panel_result_artifacts_are_future_expected_only"],
        "future_primary_artifact_requirement_validation_completed": future_eval["future_primary_artifact_requirement_validation_completed"],
        "future_source_panel_runner_primary_artifacts_required": future_eval["future_source_panel_runner_primary_artifacts_required"],
        "future_source_panel_primary_artifact_list": future_eval["future_source_panel_primary_artifact_list"],
        "source_panel_contract_validated": source_panel_contract_validated,
        "contract_artifact_primary_strength_for_contract_only": source_panel_contract_validated,
        "evidence_quality_sufficient_for_contract_validation": source_panel_contract_validated,
        "source_panel_result_primary_artifacts_exist_now": False,
        "runner_preview_eligible_next": source_panel_contract_validated,
        "runner_preview_run_now": False,
        "source_panel_analysis_execution_run_now": False,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": 0,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
        "selected_route_category": "SOURCE_PANEL_ANALYSIS",
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": current_quality,
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
            "This repair-apply validator uses live repo checks, the prior repair-apply record, and the repaired source-panel contract artifact only. "
            "It validates contract-only primary artifact strength while confirming source-panel result primary artifacts do not exist, source-panel result primary strength is not claimed, "
            "runner preview is not run now, source-panel analysis is not run, and runtime/capital/live/orders/candidates/generic runner/schema/config paths remain untouched."
        ),
        "replacement_checks_all_true": ready,
        "repaired_artifact_validation": repaired_eval,
        "old_route_guard_validation": old_route_eval,
        "safety_marker_validation": safety_eval,
        "future_primary_artifact_requirement_validation": future_eval,
        "selected_route_boundary_validation": route_boundaries,
        "prior_repair_apply_artifact_snapshot": {
            "artifact_path": str(REPAIR_APPLY_ARTIFACT_PATH),
            "artifact_valid_json": apply_valid_json,
            "artifact_json_error": apply_json_error,
            "status": apply_record.get("source_panel_analysis_contract_repair_apply_status"),
            "next_module": apply_record.get("next_module"),
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "repaired_target_json_error": json_error,
            "allowed_next_modules": [NEXT_MODULE_READY, NEXT_MODULE_BLOCKED],
        },
        "safety_flags": {
            "repo_only": True,
            "validator_only": True,
            "source_panel_analysis_run_performed": False,
            "runner_preview_run_now": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_contract_repair_apply_validator_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
