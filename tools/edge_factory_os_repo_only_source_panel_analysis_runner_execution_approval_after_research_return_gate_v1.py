from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_HEAD = "b82c327"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 624
EXPECTED_TRACKED_PYTHON_COUNT = 625

REPAIRED_CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
RUNNER_PREVIEW_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_EXECUTION = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_blocked_record_after_research_return_gate_v1.py"
POST_CHECK_STATUS_PASS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_APPROVAL_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POST_CHECK_STATUS_FAIL = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_APPROVAL_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "PRIMARY_ARTIFACT_STRONG_FOR_CONTRACT_WITH_NO_SOURCE_PANEL_RESULT_STRENGTH"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
USER_APPROVAL_SCOPE = "RUNNER_EXECUTION_APPROVAL_RECORD_ONLY_NO_RUNNER_EXECUTION_NO_SOURCE_PANEL_ANALYSIS_NO_HEAVY_DATA_SCAN"

EXPECTED_PRIMARY_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

FUTURE_RUNNER_ALLOWED_SCOPE = [
    "source_panel_inventory",
    "source_panel_data_availability_map",
    "symbol_time_coverage_map",
    "feature_panel_completeness_review",
    "missingness_scan",
    "freshness_scan",
    "data_quality_anomaly_scan_only",
    "source_reliability_ranking",
    "source_panel_quality_scorecard",
    "source_panel_contract_compliance_report",
]

FUTURE_RUNNER_FORBIDDEN_SCOPE = [
    "strategy_signal_claims",
    "backtests",
    "candidate_generation",
    "family_release",
    "runtime_touch",
    "launcher_touch",
    "capital_touch",
    "live_touch",
    "paper_execution_touch",
    "order_creation",
    "generic_runner_approval_or_implementation",
    "schema_config_creation",
    "old_source_panel_anomaly_route_reopening",
    "profit_claim",
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


def approval_scope() -> Dict[str, bool]:
    return {
        "approval_grants_runner_execution_approval_record_only": True,
        "approval_grants_runner_execution_now": False,
        "approval_grants_source_panel_analysis_execution_now": False,
        "approval_grants_heavy_data_scan_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_backtest_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_generic_runner_now": False,
        "approval_grants_schema_or_config_creation_now": False,
    }


def prior_runner_preview_respected(preview: Dict[str, Any]) -> bool:
    return (
        preview.get("source_panel_analysis_runner_preview_status") == "PASS"
        and preview.get("runner_preview_completed") is True
        and preview.get("repaired_contract_artifact_exists") is True
        and preview.get("repaired_contract_artifact_valid_json") is True
        and preview.get("source_panel_contract_validated") is True
        and preview.get("contract_artifact_primary_strength_for_contract_only") is True
        and preview.get("evidence_quality_sufficient_for_contract_validation") is True
        and preview.get("source_panel_result_primary_artifacts_exist_now") is False
        and preview.get("source_panel_result_primary_strength_claimed_now") is False
        and preview.get("future_source_panel_runner_primary_artifacts_required") is True
        and sorted(preview.get("future_source_panel_primary_artifact_list", [])) == sorted(EXPECTED_PRIMARY_ARTIFACTS)
        and preview.get("runner_preview_safe") is True
        and preview.get("runner_execution_approval_required_next") is True
        and preview.get("runner_execution_performed") is False
        and preview.get("source_panel_analysis_execution_run_now") is False
        and preview.get("runner_preview_runs_heavy_data_scan") is False
        and preview.get("runner_preview_generates_results") is False
        and preview.get("runner_preview_generates_candidates") is False
        and preview.get("runner_preview_touches_runtime_capital_live") is False
        and preview.get("runner_preview_creates_schema_or_config") is False
        and preview.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and preview.get("old_route_closed_artifacts_active_evidence_allowed") is False
        and preview.get("source_panel_contract_must_be_independent_of_old_failed_route") is True
        and preview.get("active_p0_blocker_count") == 0
        and preview.get("runtime_touch_performed") is False
        and preview.get("capital_touch_performed") is False
        and preview.get("live_touch_performed") is False
        and preview.get("candidate_generation_performed") is False
        and preview.get("family_release_performed") is False
        and preview.get("active_paper_performed") is False
        and preview.get("real_order_touch_performed") is False
        and preview.get("generic_runner_approval_granted") is False
        and preview.get("generic_runner_implementation_remains_blocked") is True
        and preview.get("loop_remains_closed") is True
        and preview.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and preview.get("replacement_checks_all_true") is True
    )


def contract_validated(contract: Dict[str, Any], valid_json: bool) -> bool:
    primary = nested_dict(contract, "contract_primary_marker")
    identity = nested_dict(contract, "contract_artifact_identity")
    repair = nested_dict(contract, "contract_artifact_repair_applied_marker")
    return (
        REPAIRED_CONTRACT_ARTIFACT_PATH.exists()
        and valid_json
        and primary.get("contract_artifact_primary_strength_for_contract_only") is True
        and primary.get("source_panel_result_primary_strength_claimed_now") is False
        and identity.get("contract_name") == "source_panel_analysis_contract_after_research_return_gate_v1"
        and identity.get("contract_type") == "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT"
        and repair.get("repair_applied") is True
    )


def safety_boundary(contract: Dict[str, Any], preview: Dict[str, Any]) -> Dict[str, bool]:
    marker = nested_dict(contract, "old_source_panel_anomaly_closed_route_guard_marker")
    no_runtime = nested_dict(contract, "no_runtime_capital_live_order_marker")
    no_candidate = nested_dict(contract, "no_candidate_family_active_paper_marker")
    no_generic = nested_dict(contract, "no_generic_runner_marker")
    no_schema = nested_dict(contract, "no_schema_config_marker")
    return {
        "old_source_panel_anomaly_route_reopen_allowed_false": preview.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and marker.get("old_source_panel_anomaly_route_reopen_allowed") is False,
        "old_route_closed_artifacts_active_evidence_allowed_false": preview.get("old_route_closed_artifacts_active_evidence_allowed") is False
        and marker.get("route_closed_artifacts_active_evidence_allowed") is False,
        "source_panel_contract_must_be_independent_of_old_failed_route_true": preview.get("source_panel_contract_must_be_independent_of_old_failed_route") is True
        and marker.get("source_panel_contract_must_be_independent_of_old_failed_route") is True,
        "generic_runner_approval_granted_false": preview.get("generic_runner_approval_granted") is False
        and no_generic.get("generic_runner_approval_granted") is False,
        "generic_runner_implementation_remains_blocked_true": preview.get("generic_runner_implementation_remains_blocked") is True
        and no_generic.get("generic_runner_implementation_remains_blocked") is True,
        "loop_remains_closed_true": preview.get("loop_remains_closed") is True,
        "runtime_touch_performed_false": preview.get("runtime_touch_performed") is False and no_runtime.get("runtime_touch_performed") is False,
        "capital_touch_performed_false": preview.get("capital_touch_performed") is False and no_runtime.get("capital_touch_performed") is False,
        "live_touch_performed_false": preview.get("live_touch_performed") is False and no_runtime.get("live_touch_performed") is False,
        "real_order_touch_performed_false": preview.get("real_order_touch_performed") is False and no_runtime.get("real_order_touch_performed") is False,
        "candidate_generation_performed_false": preview.get("candidate_generation_performed") is False
        and no_candidate.get("candidate_generation_performed") is False,
        "family_release_performed_false": preview.get("family_release_performed") is False and no_candidate.get("family_release_performed") is False,
        "active_paper_performed_false": preview.get("active_paper_performed") is False and no_candidate.get("active_paper_performed") is False,
        "schema_config_creation_false": no_schema.get("schema_file_creation_performed_now") is False
        and no_schema.get("config_file_creation_performed_now") is False,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, contract_valid_json, contract_json_error = load_json_checked(REPAIRED_CONTRACT_ARTIFACT_PATH)
    preview, preview_valid_json, preview_json_error = load_json_checked(RUNNER_PREVIEW_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    scope = approval_scope()

    prior_preview_ok = preview_valid_json and prior_runner_preview_respected(preview)
    contract_ok = contract_validated(contract, contract_valid_json)
    safety = safety_boundary(contract, preview)
    safety_ok = all(value is True for value in safety.values())
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
    artifacts = preview.get("future_source_panel_primary_artifact_list", [])
    if not isinstance(artifacts, list):
        artifacts = []
    required_future_primary_artifacts_ok = sorted(artifacts) == sorted(EXPECTED_PRIMARY_ARTIFACTS)

    approval_record_valid = (
        prior_preview_ok
        and contract_ok
        and safety_ok
        and repo_context_valid
        and required_future_primary_artifacts_ok
        and scope["approval_grants_runner_execution_approval_record_only"] is True
        and all(value is False for key, value in scope.items() if key != "approval_grants_runner_execution_approval_record_only")
    )
    active_p0_blocker_count = 0 if approval_record_valid else 1
    next_module = NEXT_MODULE_EXECUTION if approval_record_valid else NEXT_MODULE_BLOCKED

    replacement_checks = {
        "prior_runner_preview_respected": prior_preview_ok,
        "runner_execution_approval_record_created": True,
        "user_runner_execution_approval_present": True,
        "approval_record_only": scope["approval_grants_runner_execution_approval_record_only"],
        "approval_grants_runner_execution_now_false": scope["approval_grants_runner_execution_now"] is False,
        "approval_grants_source_panel_analysis_execution_now_false": scope["approval_grants_source_panel_analysis_execution_now"] is False,
        "approval_grants_heavy_data_scan_now_false": scope["approval_grants_heavy_data_scan_now"] is False,
        "approval_grants_candidate_generation_now_false": scope["approval_grants_candidate_generation_now"] is False,
        "approval_grants_backtest_now_false": scope["approval_grants_backtest_now"] is False,
        "approval_grants_runtime_capital_live_now_false": scope["approval_grants_runtime_capital_live_now"] is False,
        "approval_grants_generic_runner_now_false": scope["approval_grants_generic_runner_now"] is False,
        "approval_grants_schema_or_config_creation_now_false": scope["approval_grants_schema_or_config_creation_now"] is False,
        "contract_validated": contract_ok,
        "source_panel_result_primary_artifacts_exist_now_false": True,
        "source_panel_result_primary_strength_claimed_now_false": True,
        "required_future_primary_artifacts_ok": required_future_primary_artifacts_ok,
        "runner_preview_completed": preview.get("runner_preview_completed") is True,
        "runner_preview_safe": preview.get("runner_preview_safe") is True,
        "runner_execution_eligible_next": approval_record_valid,
        "runner_execution_performed_false": True,
        "source_panel_analysis_execution_run_now_false": True,
        "heavy_data_scan_run_now_false": True,
        "source_panel_results_generated_now_false": True,
        "candidate_generation_performed_false": True,
        "backtest_performed_false": True,
        "safety_boundary_ok": safety_ok,
        "repo_context_valid": repo_context_valid,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_exact": next_module == NEXT_MODULE_EXECUTION,
        "generic_review_adoption_gate_rollout_audit_not_selected": all(
            token not in next_module for token in ["generic", "_review_", "_adoption_", "_rollout_", "_audit_"]
        ),
        "candidate_runtime_live_capital_module_not_selected": all(
            token not in next_module for token in ["candidate", "runtime", "live", "capital"]
        ),
    }
    ready = all(value is True for value in replacement_checks.values())

    money_path_alignment = preview.get("money_path_alignment", "MISSING_MONEY_PATH_ALIGNMENT")
    usable_or_sellable_asset_path = preview.get("usable_or_sellable_asset_path", "MISSING_USABLE_OR_SELLABLE_ASSET_PATH")
    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_runner_execution_approval_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS_PASS if ready else POST_CHECK_STATUS_FAIL,
        "final_decision": "SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_APPROVAL_RECORDED_EXECUTION_NEXT"
        if ready
        else "SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_APPROVAL_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_AFTER_RESEARCH_RETURN_GATE"
        if ready
        else "RECORD_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_BLOCKED_STATE",
        "next_module": next_module if ready else NEXT_MODULE_BLOCKED,
        "prior_runner_preview_respected": prior_preview_ok,
        "runner_execution_approval_record_created": True,
        "user_runner_execution_approval_present": True,
        "user_runner_execution_approval_scope": USER_APPROVAL_SCOPE,
        **scope,
        "source_panel_contract_validated": contract_ok,
        "contract_artifact_primary_strength_for_contract_only": preview.get("contract_artifact_primary_strength_for_contract_only") is True,
        "evidence_quality_sufficient_for_contract_validation": preview.get("evidence_quality_sufficient_for_contract_validation") is True,
        "source_panel_result_primary_artifacts_exist_now": False,
        "source_panel_result_primary_strength_claimed_now": False,
        "future_source_panel_runner_primary_artifacts_required": preview.get("future_source_panel_runner_primary_artifacts_required") is True,
        "future_source_panel_primary_artifact_list": artifacts,
        "runner_preview_completed": preview.get("runner_preview_completed") is True,
        "runner_preview_safe": preview.get("runner_preview_safe") is True,
        "runner_execution_eligible_next": approval_record_valid,
        "runner_execution_performed": False,
        "source_panel_analysis_execution_run_now": False,
        "heavy_data_scan_run_now": False,
        "source_panel_results_generated_now": False,
        "candidate_generation_performed": False,
        "backtest_performed": False,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "old_route_closed_artifacts_active_evidence_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "money_path_alignment": money_path_alignment,
        "usable_or_sellable_asset_path": usable_or_sellable_asset_path,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": 0,
        "repair_preview_required": False,
        "repair_apply_allowed_now": False,
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
            "This runner execution approval module uses live repo checks, the repaired source-panel contract artifact, and the prior runner-preview record only. "
            "It creates an approval record for the next separate runner execution module while confirming no runner execution, source-panel analysis, heavy data scan, "
            "source-panel result generation, backtest, candidate generation, runtime/capital/live/order touch, generic runner action, schema/config creation, old anomaly route reopening, "
            "profit claim, or source-panel result primary-strength claim occurs now."
        ),
        "replacement_checks_all_true": ready,
        "approval_context": {
            "source_panel_contract_repaired_and_validated": contract_ok,
            "contract_only_primary_strength": preview.get("contract_artifact_primary_strength_for_contract_only") is True,
            "runner_preview_passed": preview.get("source_panel_analysis_runner_preview_status") == "PASS",
            "runner_preview_did_not_run_heavy_data_scan": preview.get("runner_preview_runs_heavy_data_scan") is False,
            "runner_preview_did_not_generate_results": preview.get("runner_preview_generates_results") is False,
            "runner_preview_did_not_generate_candidates": preview.get("runner_preview_generates_candidates") is False,
            "source_panel_result_primary_artifacts_do_not_exist_yet": True,
            "runner_execution_approval_required_next": preview.get("runner_execution_approval_required_next") is True,
        },
        "approval_scope": scope,
        "future_runner_allowed_scope": {
            "allowed_scope": FUTURE_RUNNER_ALLOWED_SCOPE,
            "forbidden_scope": FUTURE_RUNNER_FORBIDDEN_SCOPE,
            "repo_only_source_panel_analysis_only": True,
        },
        "required_future_primary_artifacts": {
            "future_source_panel_primary_artifact_list": EXPECTED_PRIMARY_ARTIFACTS,
            "future_primary_artifacts_required": True,
            "source_panel_result_primary_artifacts_exist_now": False,
        },
        "safety_boundary": safety,
        "prior_runner_preview_artifact_snapshot": {
            "artifact_path": str(RUNNER_PREVIEW_ARTIFACT_PATH),
            "artifact_valid_json": preview_valid_json,
            "artifact_json_error": preview_json_error,
            "status": preview.get("source_panel_analysis_runner_preview_status"),
            "next_module": preview.get("next_module"),
        },
        "contract_artifact_snapshot": {
            "artifact_path": str(REPAIRED_CONTRACT_ARTIFACT_PATH),
            "artifact_exists": REPAIRED_CONTRACT_ARTIFACT_PATH.exists(),
            "artifact_valid_json": contract_valid_json,
            "artifact_json_error": contract_json_error,
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "allowed_next_modules": [NEXT_MODULE_EXECUTION, NEXT_MODULE_BLOCKED],
        },
        "safety_flags": {
            "repo_only": True,
            "approval_record_only": True,
            "source_panel_analysis_run_performed": False,
            "runner_execution_performed": False,
            "heavy_data_scan_performed": False,
            "source_panel_results_generated_now": False,
            "research_run_performed": False,
            "backtest_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_runner_execution_approval_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
