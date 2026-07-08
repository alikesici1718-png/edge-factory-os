from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_HEAD = "8a7301c"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 623
EXPECTED_TRACKED_PYTHON_COUNT = 624

REPAIRED_CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
REPAIR_APPLY_VALIDATOR_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_APPROVAL = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_approval_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_runner_preview_blocked_record_after_research_return_gate_v1.py"
POST_CHECK_STATUS_PASS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_PREVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POST_CHECK_STATUS_FAIL = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_PREVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "PRIMARY_ARTIFACT_STRONG_FOR_CONTRACT_WITH_NO_SOURCE_PANEL_RESULT_STRENGTH"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

EXPECTED_PRIMARY_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

ALLOWED_RUNNER_SCOPE = [
    "source_panel_inventory",
    "source_panel_data_availability_map",
    "symbol_time_coverage_map",
    "feature_panel_completeness_review",
    "missingness_scan",
    "freshness_scan",
    "anomaly_scan_for_data_quality_only",
    "source_reliability_ranking",
    "source_panel_quality_scorecard",
    "source_panel_contract_compliance_report",
]

EXCLUDED_RUNNER_SCOPE = [
    "strategy_signal_claims",
    "backtests",
    "candidate_generation",
    "family_release",
    "runtime_changes",
    "capital_live_order_actions",
    "generic_runner_work",
    "schema_config_creation",
    "old_source_panel_anomaly_route_reopening",
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


def prior_contract_repair_apply_validator_respected(record: Dict[str, Any]) -> bool:
    return (
        record.get("source_panel_analysis_contract_repair_apply_validator_status") == "PASS"
        and record.get("repair_apply_validation_completed") is True
        and record.get("repaired_target_artifact_exists") is True
        and record.get("repaired_target_artifact_valid_json") is True
        and record.get("repair_applied_marker_validated") is True
        and record.get("contract_primary_marker_validated") is True
        and record.get("contract_artifact_identity_validated") is True
        and record.get("contract_section_completeness_markers_validated") is True
        and record.get("fail_closed_marker_validated") is True
        and record.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and record.get("no_profit_claim_marker_validated") is True
        and record.get("no_runtime_capital_live_order_marker_validated") is True
        and record.get("no_candidate_family_active_paper_marker_validated") is True
        and record.get("no_generic_runner_marker_validated") is True
        and record.get("no_schema_config_marker_validated") is True
        and record.get("future_source_panel_runner_primary_artifacts_required") is True
        and record.get("source_panel_contract_validated") is True
        and record.get("contract_artifact_primary_strength_for_contract_only") is True
        and record.get("evidence_quality_sufficient_for_contract_validation") is True
        and record.get("source_panel_result_primary_artifacts_exist_now") is False
        and record.get("source_panel_result_primary_strength_claimed_now") is False
        and record.get("runner_preview_eligible_next") is True
        and record.get("runner_preview_run_now") is False
        and record.get("source_panel_analysis_execution_run_now") is False
        and record.get("active_p0_blocker_count") == 0
        and record.get("runtime_touch_performed") is False
        and record.get("capital_touch_performed") is False
        and record.get("live_touch_performed") is False
        and record.get("candidate_generation_performed") is False
        and record.get("generic_runner_approval_granted") is False
        and record.get("generic_runner_implementation_remains_blocked") is True
        and record.get("loop_remains_closed") is True
        and record.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and record.get("replacement_checks_all_true") is True
    )


def contract_preflight_validation(contract: Dict[str, Any], valid_json: bool) -> Dict[str, Any]:
    primary = nested_dict(contract, "contract_primary_marker")
    identity = nested_dict(contract, "contract_artifact_identity")
    repair = nested_dict(contract, "contract_artifact_repair_applied_marker")
    old_guard_marker = nested_dict(contract, "old_source_panel_anomaly_closed_route_guard_marker")
    no_profit = nested_dict(contract, "no_profit_claim_marker")
    no_runtime = nested_dict(contract, "no_runtime_capital_live_order_marker")
    no_candidate = nested_dict(contract, "no_candidate_family_active_paper_marker")
    no_generic = nested_dict(contract, "no_generic_runner_marker")
    no_schema = nested_dict(contract, "no_schema_config_marker")
    primary_req = nested_dict(contract, "primary_artifact_requirement")
    return {
        "repaired_contract_artifact_exists": REPAIRED_CONTRACT_ARTIFACT_PATH.exists(),
        "repaired_contract_artifact_valid_json": valid_json,
        "contract_primary_marker_validated": primary.get("contract_artifact_primary_strength_for_contract_only") is True
        and primary.get("source_panel_result_primary_strength_claimed_now") is False
        and primary.get("source_panel_result_artifacts_are_future_expected_only") is True,
        "contract_artifact_identity_validated": identity.get("contract_name") == "source_panel_analysis_contract_after_research_return_gate_v1"
        and identity.get("contract_type") == "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT"
        and identity.get("target_artifact_path") == str(REPAIRED_CONTRACT_ARTIFACT_PATH),
        "repair_applied_marker_validated": repair.get("repair_applied") is True
        and repair.get("repair_scope") == "SOURCE_PANEL_ANALYSIS_CONTRACT_ARTIFACT_ONLY",
        "old_source_panel_anomaly_closed_route_guard_marker_validated": old_guard_marker.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and old_guard_marker.get("route_closed_artifacts_active_evidence_allowed") is False,
        "no_profit_claim_marker_validated": no_profit.get("source_panel_contract_claims_profit") is False
        and no_profit.get("profit_claimed_now") is False,
        "no_runtime_capital_live_order_marker_validated": no_runtime.get("runtime_capital_live_order_authorization") is False
        and no_runtime.get("runtime_touch_performed") is False
        and no_runtime.get("capital_touch_performed") is False
        and no_runtime.get("live_touch_performed") is False
        and no_runtime.get("real_order_touch_performed") is False,
        "no_candidate_family_active_paper_marker_validated": no_candidate.get("candidate_generation_performed") is False
        and no_candidate.get("family_release_performed") is False
        and no_candidate.get("active_paper_performed") is False,
        "no_generic_runner_marker_validated": no_generic.get("generic_runner_approval_granted") is False
        and no_generic.get("generic_runner_implementation_remains_blocked") is True,
        "no_schema_config_marker_validated": no_schema.get("schema_file_creation_performed_now") is False
        and no_schema.get("config_file_creation_performed_now") is False
        and no_schema.get("selected_route_creates_schema_or_config") is False,
        "future_source_panel_runner_primary_artifacts_required": primary_req.get("future_source_panel_runner_primary_artifacts_required") is True,
    }


def runner_scope_preview(contract: Dict[str, Any]) -> Dict[str, Any]:
    execution = nested_dict(contract, "execution_permissions")
    scope = nested_dict(contract, "source_panel_contract_scope")
    return {
        "allowed_future_runner_scope": ALLOWED_RUNNER_SCOPE,
        "excluded_future_runner_scope": EXCLUDED_RUNNER_SCOPE,
        "allowed_scope_preview_complete": True,
        "excluded_scope_preview_complete": True,
        "strategy_signal_claims_excluded": scope.get("strategy_signal_claims_allowed") is False,
        "backtests_excluded": execution.get("run_backtests_now") is False,
        "candidate_generation_excluded": execution.get("generate_candidates_now") is False and scope.get("candidate_generation_allowed") is False,
        "family_release_excluded": scope.get("family_release_allowed") is False,
        "runtime_capital_live_order_actions_excluded": execution.get("touch_runtime_capital_live_orders") is False
        and scope.get("runtime_live_capital_order_action_allowed") is False,
        "generic_runner_work_excluded": execution.get("approve_or_implement_generic_runner") is False,
        "schema_config_creation_excluded": execution.get("create_schema_or_config_files") is False,
        "old_source_panel_anomaly_route_reopening_excluded": nested_dict(contract, "old_source_panel_anomaly_route_guard").get("old_source_panel_anomaly_route_reopen_allowed") is False,
    }


def expected_primary_result_artifacts_preview(contract: Dict[str, Any]) -> Dict[str, Any]:
    primary = nested_dict(contract, "primary_artifact_requirement")
    artifacts = primary.get("future_source_panel_primary_artifact_list", [])
    if not isinstance(artifacts, list):
        artifacts = []
    return {
        "future_source_panel_primary_artifact_list": artifacts,
        "expected_primary_result_artifacts_match_contract": sorted(artifacts) == sorted(EXPECTED_PRIMARY_ARTIFACTS),
        "future_expected_artifacts_only": True,
        "source_panel_result_primary_artifacts_exist_now": False,
        "source_panel_result_primary_strength_claimed_now": False,
    }


def old_route_guard_preview(contract: Dict[str, Any]) -> Dict[str, Any]:
    guard = nested_dict(contract, "old_source_panel_anomaly_route_guard")
    marker = nested_dict(contract, "old_source_panel_anomaly_closed_route_guard_marker")
    route_rule = str(guard.get("route_closed_artifact_rule", "")).lower()
    future_rule = str(guard.get("future_reference_rule", "")).lower()
    return {
        "fail_if_old_source_panel_anomaly_route_reopened": guard.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and marker.get("old_source_panel_anomaly_route_reopen_allowed") is False,
        "fail_if_route_closed_true_artifact_used_as_active_evidence": marker.get("route_closed_artifacts_active_evidence_allowed") is False
        and "no route_closed=true" in route_rule
        and "active research route continuation" in route_rule,
        "fail_if_old_anomaly_artifacts_not_historical_closed": marker.get("prior_source_panel_anomaly_artifacts_are_historical_context_only") is True
        and guard.get("prior_source_panel_anomaly_artifacts_are_historical_context_only") is True
        and "historical/closed" in future_rule,
        "fail_if_contract_independence_from_old_failed_route_violated": marker.get("source_panel_contract_must_be_independent_of_old_failed_route") is True
        and guard.get("source_panel_contract_must_be_independent_of_old_failed_route") is True,
        "old_source_panel_anomaly_route_reopen_allowed": False
        if guard.get("old_source_panel_anomaly_route_reopen_allowed") is not True and marker.get("old_source_panel_anomaly_route_reopen_allowed") is False
        else True,
        "old_route_closed_artifacts_active_evidence_allowed": True
        if marker.get("route_closed_artifacts_active_evidence_allowed") is True
        else False,
        "source_panel_contract_must_be_independent_of_old_failed_route": guard.get("source_panel_contract_must_be_independent_of_old_failed_route") is True
        and marker.get("source_panel_contract_must_be_independent_of_old_failed_route") is True,
    }


def evidence_quality_preview(contract: Dict[str, Any]) -> Dict[str, Any]:
    evidence = nested_dict(contract, "evidence_quality_requirements")
    return {
        "contract_evidence_quality": CURRENT_EVIDENCE_CHAIN_QUALITY,
        "future_runner_output_evidence_primary_only_if_required_artifacts_created_and_validated": True,
        "derived_evidence_allowed_only_as_explicit_attention_with_reason_monitoring": evidence.get("derived_evidence_allowed_only_as")
        == "DERIVED_EXPLICIT_ATTENTION_WITH_REASON_AND_MONITORING",
        "derived_overused_default_forbidden": evidence.get("derived_overused_default_allowed") is False,
        "fail_closed_if_exact_primary_evidence_missing": evidence.get("exact_marker_or_primary_artifact_required_where_available") is True,
        "source_panel_result_primary_strength_claimed_now": False,
    }


def safety_preview() -> Dict[str, bool]:
    return {
        "future_runner_would_touch_runtime": False,
        "future_runner_would_touch_launcher": False,
        "future_runner_would_touch_capital": False,
        "future_runner_would_touch_live": False,
        "future_runner_would_touch_orders": False,
        "future_runner_would_generate_candidates": False,
        "future_runner_would_release_families": False,
        "future_runner_would_activate_paper": False,
        "future_runner_would_approve_or_implement_generic_runner": False,
        "future_runner_would_create_schema_config_files": False,
        "future_runner_would_claim_profit": False,
        "future_runner_would_claim_source_panel_result_primary_strength_before_artifacts_exist": False,
    }


def money_path_preview(contract: Dict[str, Any]) -> Dict[str, Any]:
    money = nested_dict(contract, "money_path_alignment")
    return {
        "internal_research_substrate_utility": money.get("internal_research_edge_discovery_substrate") is True,
        "reusable_source_panel_data_quality_asset": money.get("reusable_data_quality_source_panel_analysis_asset") is True,
        "possible_sellable_pivotable_data_quality_validation_tool": money.get("possible_sellable_pivotable_validation_data_quality_tool") is True,
        "no_profit_promise": money.get("profit_promise") is False,
        "money_path_alignment": money.get("money_path_alignment", "MISSING_MONEY_PATH_ALIGNMENT"),
        "usable_or_sellable_asset_path": money.get("usable_or_sellable_asset_path", "MISSING_USABLE_OR_SELLABLE_ASSET_PATH"),
    }


def all_true_bool(values: Dict[str, Any]) -> bool:
    return all(value is True for value in values.values() if isinstance(value, bool))


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, contract_valid_json, contract_json_error = load_json_checked(REPAIRED_CONTRACT_ARTIFACT_PATH)
    validator_record, validator_valid_json, validator_json_error = load_json_checked(REPAIR_APPLY_VALIDATOR_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    contract_preflight = contract_preflight_validation(contract, contract_valid_json)
    scope_preview = runner_scope_preview(contract)
    artifacts_preview = expected_primary_result_artifacts_preview(contract)
    old_guard_preview = old_route_guard_preview(contract)
    evidence_preview = evidence_quality_preview(contract)
    safe_preview = safety_preview()
    money_preview = money_path_preview(contract)
    prior_validator_ok = validator_valid_json and prior_contract_repair_apply_validator_respected(validator_record)

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
    contract_preflight_ok = all_true_bool(contract_preflight)
    runner_scope_ok = all_true_bool(
        {key: value for key, value in scope_preview.items() if key not in {"allowed_future_runner_scope", "excluded_future_runner_scope"}}
    )
    artifacts_preview_ok = (
        artifacts_preview["expected_primary_result_artifacts_match_contract"] is True
        and artifacts_preview["future_expected_artifacts_only"] is True
        and artifacts_preview["source_panel_result_primary_artifacts_exist_now"] is False
        and artifacts_preview["source_panel_result_primary_strength_claimed_now"] is False
    )
    old_guard_preview_ok = (
        old_guard_preview["fail_if_old_source_panel_anomaly_route_reopened"] is True
        and old_guard_preview["fail_if_route_closed_true_artifact_used_as_active_evidence"] is True
        and old_guard_preview["fail_if_old_anomaly_artifacts_not_historical_closed"] is True
        and old_guard_preview["fail_if_contract_independence_from_old_failed_route_violated"] is True
        and old_guard_preview["old_source_panel_anomaly_route_reopen_allowed"] is False
        and old_guard_preview["old_route_closed_artifacts_active_evidence_allowed"] is False
        and old_guard_preview["source_panel_contract_must_be_independent_of_old_failed_route"] is True
    )
    evidence_preview_ok = (
        evidence_preview["future_runner_output_evidence_primary_only_if_required_artifacts_created_and_validated"] is True
        and evidence_preview["derived_evidence_allowed_only_as_explicit_attention_with_reason_monitoring"] is True
        and evidence_preview["derived_overused_default_forbidden"] is True
        and evidence_preview["fail_closed_if_exact_primary_evidence_missing"] is True
        and evidence_preview["source_panel_result_primary_strength_claimed_now"] is False
    )
    safety_preview_ok = all(value is False for value in safe_preview.values())
    money_path_preview_ok = (
        money_preview["internal_research_substrate_utility"] is True
        and money_preview["reusable_source_panel_data_quality_asset"] is True
        and money_preview["possible_sellable_pivotable_data_quality_validation_tool"] is True
        and money_preview["no_profit_promise"] is True
        and money_preview["money_path_alignment"] != "MISSING_MONEY_PATH_ALIGNMENT"
        and money_preview["usable_or_sellable_asset_path"] != "MISSING_USABLE_OR_SELLABLE_ASSET_PATH"
    )

    runner_preview_safe = (
        prior_validator_ok
        and repo_context_valid
        and contract_preflight_ok
        and runner_scope_ok
        and artifacts_preview_ok
        and old_guard_preview_ok
        and evidence_preview_ok
        and safety_preview_ok
        and money_path_preview_ok
    )
    active_p0_blocker_count = 0 if runner_preview_safe else 1
    next_module = NEXT_MODULE_APPROVAL if runner_preview_safe else NEXT_MODULE_BLOCKED

    replacement_checks = {
        "prior_contract_repair_apply_validator_respected": prior_validator_ok,
        "runner_preview_completed": True,
        "contract_preflight_validation_completed": True,
        "runner_scope_preview_completed": True,
        "expected_primary_result_artifacts_preview_completed": True,
        "old_route_guard_preview_completed": True,
        "evidence_quality_preview_completed": True,
        "safety_preview_completed": True,
        "money_path_preview_completed": True,
        "repo_context_valid": repo_context_valid,
        "contract_preflight_ok": contract_preflight_ok,
        "runner_scope_ok": runner_scope_ok,
        "expected_primary_result_artifacts_preview_ok": artifacts_preview_ok,
        "old_route_guard_preview_ok": old_guard_preview_ok,
        "evidence_quality_preview_ok": evidence_preview_ok,
        "safety_preview_ok": safety_preview_ok,
        "money_path_preview_ok": money_path_preview_ok,
        "runner_preview_safe": runner_preview_safe,
        "runner_execution_performed_false": True,
        "source_panel_analysis_execution_run_now_false": True,
        "runner_preview_runs_heavy_data_scan_false": True,
        "runner_preview_generates_results_false": True,
        "runner_preview_generates_candidates_false": True,
        "runner_preview_touches_runtime_capital_live_false": True,
        "runner_preview_creates_schema_or_config_false": True,
        "source_panel_result_primary_artifacts_exist_now_false": True,
        "source_panel_result_primary_strength_claimed_now_false": True,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module in {NEXT_MODULE_APPROVAL, NEXT_MODULE_BLOCKED},
        "runner_execution_not_selected_directly": next_module != "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1.py",
        "source_panel_analysis_execution_not_selected_directly": "source_panel_analysis_execution" not in next_module,
        "generic_review_adoption_gate_rollout_audit_not_selected": all(
            token not in next_module for token in ["generic", "_review_", "_adoption_", "_rollout_", "_audit_"]
        ),
    }
    ready = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_runner_preview_status": "PASS" if ready and runner_preview_safe else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS_PASS if ready and runner_preview_safe else POST_CHECK_STATUS_FAIL,
        "final_decision": "SOURCE_PANEL_ANALYSIS_RUNNER_PREVIEW_SAFE_EXECUTION_APPROVAL_REQUIRED_NEXT"
        if ready and runner_preview_safe
        else "SOURCE_PANEL_ANALYSIS_RUNNER_PREVIEW_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_APPROVAL_AFTER_RESEARCH_RETURN_GATE"
        if ready and runner_preview_safe
        else "RECORD_SOURCE_PANEL_ANALYSIS_RUNNER_PREVIEW_BLOCKED_STATE",
        "next_module": next_module,
        "prior_contract_repair_apply_validator_respected": prior_validator_ok,
        "runner_preview_completed": True,
        "contract_preflight_validation_completed": True,
        "runner_scope_preview_completed": True,
        "expected_primary_result_artifacts_preview_completed": True,
        "old_route_guard_preview_completed": True,
        "evidence_quality_preview_completed": True,
        "safety_preview_completed": True,
        "money_path_preview_completed": True,
        "repaired_contract_artifact_path": str(REPAIRED_CONTRACT_ARTIFACT_PATH),
        "repaired_contract_artifact_exists": contract_preflight["repaired_contract_artifact_exists"],
        "repaired_contract_artifact_valid_json": contract_preflight["repaired_contract_artifact_valid_json"],
        "source_panel_contract_validated": runner_preview_safe,
        "contract_artifact_primary_strength_for_contract_only": contract_preflight["contract_primary_marker_validated"],
        "evidence_quality_sufficient_for_contract_validation": runner_preview_safe,
        "source_panel_result_primary_artifacts_exist_now": False,
        "source_panel_result_primary_strength_claimed_now": False,
        "future_source_panel_runner_primary_artifacts_required": contract_preflight["future_source_panel_runner_primary_artifacts_required"],
        "future_source_panel_primary_artifact_list": artifacts_preview["future_source_panel_primary_artifact_list"],
        "runner_preview_safe": runner_preview_safe,
        "runner_execution_approval_required_next": runner_preview_safe,
        "runner_execution_performed": False,
        "source_panel_analysis_execution_run_now": False,
        "runner_preview_runs_heavy_data_scan": False,
        "runner_preview_generates_results": False,
        "runner_preview_generates_candidates": False,
        "runner_preview_touches_runtime_capital_live": False,
        "runner_preview_creates_schema_or_config": False,
        "old_source_panel_anomaly_route_reopen_allowed": old_guard_preview["old_source_panel_anomaly_route_reopen_allowed"],
        "old_route_closed_artifacts_active_evidence_allowed": old_guard_preview["old_route_closed_artifacts_active_evidence_allowed"],
        "source_panel_contract_must_be_independent_of_old_failed_route": old_guard_preview["source_panel_contract_must_be_independent_of_old_failed_route"],
        "money_path_alignment": money_preview["money_path_alignment"],
        "usable_or_sellable_asset_path": money_preview["usable_or_sellable_asset_path"],
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
            "This runner preview uses live repo checks, the repaired source-panel contract artifact, and the prior repair-apply validator record only. "
            "It previews future runner scope and required future primary result artifacts without running source-panel analysis, scanning heavy data, generating results or candidates, "
            "touching runtime/capital/live/orders, approving generic runner work, creating schemas/configs, reopening old anomaly routes, claiming profit, or claiming source-panel result primary strength now."
        ),
        "replacement_checks_all_true": ready,
        "contract_preflight_validation": contract_preflight,
        "runner_scope_preview": scope_preview,
        "expected_primary_result_artifacts_preview": artifacts_preview,
        "old_route_guard_preview": old_guard_preview,
        "evidence_quality_preview": evidence_preview,
        "safety_preview": safe_preview,
        "money_path_preview": money_preview,
        "prior_contract_repair_apply_validator_artifact_snapshot": {
            "artifact_path": str(REPAIR_APPLY_VALIDATOR_ARTIFACT_PATH),
            "artifact_valid_json": validator_valid_json,
            "artifact_json_error": validator_json_error,
            "status": validator_record.get("source_panel_analysis_contract_repair_apply_validator_status"),
            "next_module": validator_record.get("next_module"),
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "repaired_contract_json_error": contract_json_error,
            "allowed_next_modules": [NEXT_MODULE_APPROVAL, NEXT_MODULE_BLOCKED],
        },
        "safety_flags": {
            "repo_only": True,
            "runner_preview_only": True,
            "source_panel_analysis_run_performed": False,
            "runner_execution_performed": False,
            "heavy_data_scan_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_runner_preview_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_runner_preview_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
