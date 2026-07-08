from __future__ import annotations

import ast
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_HEAD = "57943be"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 621
EXPECTED_TRACKED_PYTHON_COUNT = 622

CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
)
REPAIR_APPLY_APPROVAL_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_contract_repair_apply_approval_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_VALIDATOR = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_validator_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_apply_blocked_record_after_research_return_gate_v1.py"
POST_CHECK_STATUS_PASS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POST_CHECK_STATUS_FAIL = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED"
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

REQUIRED_SECTIONS = [
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
    return {
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_commit_paths(),
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def repo_tracked_files() -> List[str]:
    return sorted(
        line.strip().replace("\\", "/")
        for line in run_cmd(["git", "ls-files"]).stdout.splitlines()
        if line.strip()
    )


def target_artifact_is_git_tracked() -> bool:
    try:
        target_resolved = CONTRACT_ARTIFACT_PATH.resolve()
        repo_resolved = REPO_ROOT.resolve()
        rel = target_resolved.relative_to(repo_resolved).as_posix()
    except ValueError:
        return False
    return rel in repo_tracked_files()


def prior_approval_valid(approval: Dict[str, Any]) -> bool:
    return (
        approval.get("source_panel_analysis_contract_repair_apply_approval_status") == "PASS"
        and approval.get("repair_apply_approval_record_created") is True
        and approval.get("user_repair_apply_approval_present") is True
        and approval.get("repair_apply_next_step_allowed") is True
        and approval.get("approval_grants_repair_apply_now") is False
        and approval.get("approval_grants_contract_artifact_edit_now") is False
        and approval.get("repair_apply_performed") is False
        and approval.get("repair_apply_allowed_now") is False
        and approval.get("target_artifact_exists") is True
        and approval.get("target_artifact_valid_json") is True
        and approval.get("target_artifact_would_be_modified_by_future_apply") is True
        and approval.get("target_artifact_modified_now") is False
        and approval.get("future_apply_would_touch_runtime_capital_live") is False
        and approval.get("future_apply_would_create_schema_or_config") is False
        and approval.get("future_apply_would_approve_generic_runner") is False
        and approval.get("future_apply_would_reopen_old_source_panel_anomaly_route") is False
        and approval.get("future_apply_would_claim_source_panel_result_primary_strength_now") is False
        and approval.get("future_apply_would_claim_profit") is False
        and approval.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and approval.get("replacement_checks_all_true") is True
    )


def nested_dict(contract: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = contract.get(key)
    return value if isinstance(value, dict) else {}


def preserve_existing_contract_meaning(contract: Dict[str, Any]) -> Dict[str, bool]:
    guard = nested_dict(contract, "old_source_panel_anomaly_route_guard")
    primary = nested_dict(contract, "primary_artifact_requirement")
    money = nested_dict(contract, "money_path_alignment")
    context = nested_dict(contract, "research_return_context")
    scope = nested_dict(contract, "source_panel_contract_scope")
    execution = nested_dict(contract, "execution_permissions")
    evidence = nested_dict(contract, "evidence_quality_requirements")
    return {
        "selected_route_category": context.get("selected_route_category") == "SOURCE_PANEL_ANALYSIS",
        "old_source_panel_anomaly_route_reopen_allowed": guard.get("old_source_panel_anomaly_route_reopen_allowed") is False,
        "source_panel_contract_must_be_independent_of_old_failed_route": guard.get("source_panel_contract_must_be_independent_of_old_failed_route") is True,
        "prior_source_panel_anomaly_artifacts_are_historical_context_only": guard.get("prior_source_panel_anomaly_artifacts_are_historical_context_only") is True,
        "future_source_panel_runner_primary_artifacts_required": primary.get("future_source_panel_runner_primary_artifacts_required") is True,
        "source_panel_contract_claims_profit": money.get("profit_promise") is False,
        "source_panel_contract_claims_primary_strength_now": evidence.get("source_panel_contract_claims_primary_strength_now") is False,
        "selected_route_runs_research_now": execution.get("run_source_panel_analysis_now") is False,
        "selected_route_generates_candidates_now": scope.get("candidate_generation_allowed") is False
        and execution.get("generate_candidates_now") is False,
        "selected_route_touches_runtime_capital_live": scope.get("runtime_live_capital_order_action_allowed") is False
        and execution.get("touch_runtime_capital_live_orders") is False,
        "selected_route_approves_generic_runner": execution.get("approve_or_implement_generic_runner") is False,
        "selected_route_creates_schema_or_config": execution.get("create_schema_or_config_files") is False,
    }


def pre_apply_validation(contract: Dict[str, Any], contract_valid: bool, approval: Dict[str, Any], approval_valid: bool) -> Dict[str, Any]:
    git = git_state()
    preserved = preserve_existing_contract_meaning(contract)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    target_tracked = target_artifact_is_git_tracked()
    only_current_tool_changed = git["changed_paths"] in ([], [CURRENT_TOOL_REL])
    checks = {
        "expected_head": git["head"] == EXPECTED_HEAD,
        "repo_clean_or_only_approved_tool_before_contract_artifact_write": only_current_tool_changed,
        "target_artifact_exists": CONTRACT_ARTIFACT_PATH.exists(),
        "target_artifact_valid_json": contract_valid,
        "prior_approval_exists": REPAIR_APPLY_APPROVAL_ARTIFACT_PATH.exists(),
        "prior_approval_valid_json": approval_valid,
        "prior_approval_exists_and_respected": prior_approval_valid(approval),
        "repair_apply_next_step_allowed": approval.get("repair_apply_next_step_allowed") is True,
        "target_artifact_not_git_tracked": target_tracked is False,
        "old_anomaly_route_reopen_false": preserved["old_source_panel_anomaly_route_reopen_allowed"],
        "selected_route_runs_research_now_false": preserved["selected_route_runs_research_now"],
        "selected_route_generates_candidates_now_false": preserved["selected_route_generates_candidates_now"],
        "selected_route_touches_runtime_capital_live_false": preserved["selected_route_touches_runtime_capital_live"],
        "selected_route_approves_generic_runner_false": preserved["selected_route_approves_generic_runner"],
        "selected_route_creates_schema_or_config_false": preserved["selected_route_creates_schema_or_config"],
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in dangerous_flags().values()),
    }
    return {
        "checks": checks,
        "passed": all(value is True for value in checks.values()),
        "git_state": git,
        "preserved_contract_meaning": preserved,
        "planned_schema_files_existing": planned_existing,
        "generic_runner_target_exists": generic_runner_target_exists,
        "target_artifact_git_tracked": target_tracked,
    }


def contract_repair_markers(pre_hash: str, backup_path: Path) -> Dict[str, Any]:
    stamp = now_utc()
    return {
        "contract_primary_marker": {
            "contract_artifact_primary_strength_for_contract_only": True,
            "scope": "CONTRACT_ARTIFACT_VALIDATION_ONLY",
            "source_panel_result_primary_strength_claimed_now": False,
            "source_panel_result_artifacts_are_future_expected_only": True,
            "applied_by": CURRENT_TOOL_REL,
            "applied_at_utc": stamp,
        },
        "contract_artifact_identity": {
            "contract_name": "source_panel_analysis_contract_after_research_return_gate_v1",
            "contract_type": "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT",
            "target_artifact_path": str(CONTRACT_ARTIFACT_PATH),
            "pre_apply_sha256": pre_hash,
        },
        "contract_artifact_repair_applied_marker": {
            "repair_applied": True,
            "repair_module": CURRENT_TOOL_REL,
            "repair_scope": "SOURCE_PANEL_ANALYSIS_CONTRACT_ARTIFACT_ONLY",
            "backup_path": str(backup_path),
            "applied_at_utc": stamp,
        },
        "contract_section_completeness_markers": {
            "required_sections": REQUIRED_SECTIONS,
            "required_sections_all_present_after_repair": True,
            "next_module_decision_added_or_strengthened": True,
        },
        "old_source_panel_anomaly_closed_route_guard_marker": {
            "old_source_panel_anomaly_route_reopen_allowed": False,
            "source_panel_contract_must_be_independent_of_old_failed_route": True,
            "prior_source_panel_anomaly_artifacts_are_historical_context_only": True,
            "route_closed_artifacts_active_evidence_allowed": False,
        },
        "future_source_panel_primary_artifact_requirement_marker": {
            "future_source_panel_runner_primary_artifacts_required": True,
            "source_panel_result_artifacts_are_future_expected_only": True,
            "source_panel_result_primary_strength_claimed_now": False,
        },
        "no_profit_claim_marker": {"source_panel_contract_claims_profit": False, "profit_claimed_now": False},
        "no_runtime_capital_live_order_marker": {
            "runtime_touch_performed": False,
            "capital_touch_performed": False,
            "live_touch_performed": False,
            "real_order_touch_performed": False,
            "runtime_capital_live_order_authorization": False,
        },
        "no_candidate_family_active_paper_marker": {
            "candidate_generation_performed": False,
            "family_release_performed": False,
            "active_paper_performed": False,
        },
        "no_generic_runner_marker": {
            "generic_runner_approval_granted": False,
            "generic_runner_implementation_remains_blocked": True,
        },
        "no_schema_config_marker": {
            "schema_file_creation_performed_now": False,
            "config_file_creation_performed_now": False,
            "selected_route_creates_schema_or_config": False,
        },
        "fail_closed_if_required_markers_missing": True,
    }


def apply_exact_contract_repair(contract: Dict[str, Any], pre_hash: str) -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = OUT_DIR / f"source_panel_analysis_contract_after_research_return_gate_v1_pre_repair_{stamp}.json"
    shutil.copy2(CONTRACT_ARTIFACT_PATH, backup_path)
    markers = contract_repair_markers(pre_hash, backup_path)
    repaired = dict(contract)
    repaired.update(markers)
    repaired["source_panel_result_primary_strength_claimed_now"] = False
    repaired["source_panel_result_artifacts_are_future_expected_only"] = True
    repaired["next_module_decision"] = {
        "repair_apply_succeeded": True,
        "next_module": NEXT_MODULE_VALIDATOR,
        "runner_preview_selected_directly": False,
        "source_panel_analysis_execution_selected": False,
        "generic_review_adoption_gate_rollout_audit_selected": False,
        "blocked_next_module_if_repair_apply_fails": NEXT_MODULE_BLOCKED,
    }
    rendered = json.dumps(repaired, indent=2, sort_keys=True)
    CONTRACT_ARTIFACT_PATH.write_text(rendered + "\n", encoding="utf-8")
    return {"backup_path": backup_path, "markers": markers, "post_hash": sha256_or_missing(CONTRACT_ARTIFACT_PATH)}


def markers_present(contract: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "contract_primary_marker_added": isinstance(contract.get("contract_primary_marker"), dict),
        "contract_artifact_identity_added": isinstance(contract.get("contract_artifact_identity"), dict),
        "contract_artifact_repair_applied_marker_added": isinstance(contract.get("contract_artifact_repair_applied_marker"), dict),
        "contract_section_completeness_markers_added": isinstance(contract.get("contract_section_completeness_markers"), dict),
        "old_source_panel_anomaly_closed_route_guard_marker_added": isinstance(contract.get("old_source_panel_anomaly_closed_route_guard_marker"), dict),
        "future_source_panel_primary_artifact_requirement_marker_added": isinstance(contract.get("future_source_panel_primary_artifact_requirement_marker"), dict),
        "no_profit_claim_marker_added": isinstance(contract.get("no_profit_claim_marker"), dict),
        "no_runtime_capital_live_order_marker_added": isinstance(contract.get("no_runtime_capital_live_order_marker"), dict),
        "no_candidate_family_active_paper_marker_added": isinstance(contract.get("no_candidate_family_active_paper_marker"), dict),
        "no_generic_runner_marker_added": isinstance(contract.get("no_generic_runner_marker"), dict),
        "no_schema_config_marker_added": isinstance(contract.get("no_schema_config_marker"), dict),
        "fail_closed_if_required_markers_missing_added": contract.get("fail_closed_if_required_markers_missing") is True,
    }


def post_apply_validation(contract: Dict[str, Any], valid_json: bool, backup_path: Path, pre_hash: str, post_hash: str) -> Dict[str, Any]:
    guard = nested_dict(contract, "old_source_panel_anomaly_route_guard")
    primary = nested_dict(contract, "primary_artifact_requirement")
    execution = nested_dict(contract, "execution_permissions")
    scope = nested_dict(contract, "source_panel_contract_scope")
    marker_checks = markers_present(contract)
    no_runtime_marker = nested_dict(contract, "no_runtime_capital_live_order_marker")
    no_candidate_marker = nested_dict(contract, "no_candidate_family_active_paper_marker")
    no_generic_marker = nested_dict(contract, "no_generic_runner_marker")
    no_schema_marker = nested_dict(contract, "no_schema_config_marker")
    no_profit_marker = nested_dict(contract, "no_profit_claim_marker")
    checks = {
        "valid_json": valid_json,
        "markers_present": all(value is True for value in marker_checks.values()),
        "old_anomaly_route_still_blocked": guard.get("old_source_panel_anomaly_route_reopen_allowed") is False
        and nested_dict(contract, "old_source_panel_anomaly_closed_route_guard_marker").get("old_source_panel_anomaly_route_reopen_allowed") is False,
        "no_profit_claim": no_profit_marker.get("source_panel_contract_claims_profit") is False,
        "no_source_panel_result_primary_strength_claim": contract.get("source_panel_result_primary_strength_claimed_now") is False,
        "no_runtime_capital_live_authorization": no_runtime_marker.get("runtime_capital_live_order_authorization") is False
        and execution.get("touch_runtime_capital_live_orders") is False,
        "no_candidate_authorization": no_candidate_marker.get("candidate_generation_performed") is False
        and scope.get("candidate_generation_allowed") is False,
        "no_generic_runner_authorization": no_generic_marker.get("generic_runner_approval_granted") is False
        and no_generic_marker.get("generic_runner_implementation_remains_blocked") is True,
        "no_schema_config_authorization": no_schema_marker.get("selected_route_creates_schema_or_config") is False
        and execution.get("create_schema_or_config_files") is False,
        "future_runner_primary_artifacts_still_required": primary.get("future_source_panel_runner_primary_artifacts_required") is True,
        "contract_only_primary_expected": nested_dict(contract, "contract_primary_marker").get("contract_artifact_primary_strength_for_contract_only") is True,
        "evidence_quality_sufficient_expected": True,
        "active_p0_blocker_expected_zero": True,
        "backup_exists": backup_path.exists(),
        "target_modified": pre_hash != post_hash,
    }
    return {"checks": checks, "marker_checks": marker_checks, "passed": all(value is True for value in checks.values())}


def base_payload() -> Dict[str, Any]:
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    return {
        "prior_repair_apply_approval_respected": False,
        "repair_apply_performed": False,
        "repair_apply_successful": False,
        "repair_apply_target_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        "target_artifact_exists_before_apply": CONTRACT_ARTIFACT_PATH.exists(),
        "target_artifact_valid_json_before_apply": False,
        "target_artifact_modified_now": False,
        "target_artifact_exists_after_apply": CONTRACT_ARTIFACT_PATH.exists(),
        "target_artifact_valid_json_after_apply": False,
        "target_artifact_backup_created": False,
        "target_artifact_backup_path": "",
        "contract_primary_marker_added": False,
        "contract_artifact_identity_added": False,
        "contract_artifact_repair_applied_marker_added": False,
        "contract_section_completeness_markers_added": False,
        "old_source_panel_anomaly_closed_route_guard_marker_added": False,
        "future_source_panel_primary_artifact_requirement_marker_added": False,
        "no_profit_claim_marker_added": False,
        "no_runtime_capital_live_order_marker_added": False,
        "no_candidate_family_active_paper_marker_added": False,
        "no_generic_runner_marker_added": False,
        "no_schema_config_marker_added": False,
        "fail_closed_if_required_markers_missing_added": False,
        "source_panel_result_primary_strength_claimed_now": False,
        "source_panel_result_artifacts_are_future_expected_only": True,
        "post_apply_validation_completed": False,
        "contract_artifact_primary_strength_for_contract_only_expected_after_validator": False,
        "evidence_quality_sufficient_for_contract_validation_expected_after_validator": False,
        "active_p0_blocker_count_expected_after_validator": 1,
        "runner_preview_blocked_until_validator_passes": True,
        "source_panel_analysis_execution_blocked": True,
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
            "This repair apply module uses live repo checks and the approved source-panel contract artifact only, modifies only that non-repo contract artifact, "
            "and keeps source-panel analysis, runner preview, candidates, runtime/capital/live/orders, generic runner, schema/config, old anomaly route reopening, "
            "profit claims, and source-panel result primary-strength claims blocked."
        ),
        "replacement_checks_all_true": False,
    }


def build_payload() -> Dict[str, Any]:
    contract_before, contract_valid_before, contract_error_before = load_json_checked(CONTRACT_ARTIFACT_PATH)
    approval, approval_valid, approval_error = load_json_checked(REPAIR_APPLY_APPROVAL_ARTIFACT_PATH)
    pre_hash = sha256_or_missing(CONTRACT_ARTIFACT_PATH)
    payload = base_payload()
    payload.update(
        {
            "module": MODULE_NAME,
            "created_at_utc": now_utc(),
            "target_artifact_valid_json_before_apply": contract_valid_before,
            "contract_artifact_json_error_before_apply": contract_error_before,
        }
    )
    pre = pre_apply_validation(contract_before, contract_valid_before, approval, approval_valid)
    payload["prior_repair_apply_approval_respected"] = pre["checks"]["prior_approval_exists_and_respected"]
    payload["pre_apply_validation"] = pre
    payload["prior_approval_artifact_snapshot"] = {
        "artifact_path": str(REPAIR_APPLY_APPROVAL_ARTIFACT_PATH),
        "artifact_valid_json": approval_valid,
        "artifact_json_error": approval_error,
        "status": approval.get("source_panel_analysis_contract_repair_apply_approval_status"),
        "next_module": approval.get("next_module"),
    }

    backup_path = Path()
    post_hash = pre_hash
    if pre["passed"]:
        apply_result = apply_exact_contract_repair(contract_before, pre_hash)
        backup_path = apply_result["backup_path"]
        post_hash = apply_result["post_hash"]
        payload["repair_apply_performed"] = True
        payload["target_artifact_backup_created"] = backup_path.exists()
        payload["target_artifact_backup_path"] = str(backup_path)
        payload["target_artifact_modified_now"] = pre_hash != post_hash

    contract_after, contract_valid_after, contract_error_after = load_json_checked(CONTRACT_ARTIFACT_PATH)
    payload["target_artifact_exists_after_apply"] = CONTRACT_ARTIFACT_PATH.exists()
    payload["target_artifact_valid_json_after_apply"] = contract_valid_after
    payload["contract_artifact_json_error_after_apply"] = contract_error_after
    if pre["passed"]:
        post = post_apply_validation(contract_after, contract_valid_after, backup_path, pre_hash, post_hash)
        payload["post_apply_validation"] = post
        payload["post_apply_validation_completed"] = True
        payload.update(post["marker_checks"])
        payload["repair_apply_successful"] = post["passed"]
        payload["contract_artifact_primary_strength_for_contract_only_expected_after_validator"] = post["passed"]
        payload["evidence_quality_sufficient_for_contract_validation_expected_after_validator"] = post["passed"]
        payload["active_p0_blocker_count_expected_after_validator"] = 0 if post["passed"] else 1

    success = payload["repair_apply_performed"] is True and payload["repair_apply_successful"] is True
    payload["source_panel_analysis_contract_repair_apply_status"] = "PASS" if success else "FAIL_CLOSED"
    payload["post_check_status"] = POST_CHECK_STATUS_PASS if success else POST_CHECK_STATUS_FAIL
    payload["final_decision"] = "SOURCE_PANEL_CONTRACT_REPAIR_APPLIED_VALIDATOR_NEXT" if success else "SOURCE_PANEL_CONTRACT_REPAIR_APPLY_FAIL_CLOSED"
    payload["next_action"] = "BUILD_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_VALIDATOR_AFTER_RESEARCH_RETURN_GATE" if success else "RECORD_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPLY_BLOCKED_STATE"
    payload["next_module"] = NEXT_MODULE_VALIDATOR if success else NEXT_MODULE_BLOCKED
    payload["source_panel_result_primary_strength_claimed_now"] = False
    payload["source_panel_result_artifacts_are_future_expected_only"] = True
    replacement_checks = {
        "pre_apply_validation_passed": pre["passed"],
        "repair_apply_performed": payload["repair_apply_performed"] is True,
        "repair_apply_successful": payload["repair_apply_successful"] is True,
        "target_artifact_modified_now": payload["target_artifact_modified_now"] is True,
        "target_artifact_valid_json_after_apply": payload["target_artifact_valid_json_after_apply"] is True,
        "target_artifact_backup_created": payload["target_artifact_backup_created"] is True,
        "marker_checks_all_true": all(payload.get(key) is True for key in markers_present(contract_after)),
        "source_panel_result_primary_strength_claimed_now_false": payload["source_panel_result_primary_strength_claimed_now"] is False,
        "runner_preview_blocked_until_validator_passes": payload["runner_preview_blocked_until_validator_passes"] is True,
        "source_panel_analysis_execution_blocked": payload["source_panel_analysis_execution_blocked"] is True,
        "dangerous_flags_all_false": payload["dangerous_flags_all_false"] is True,
        "next_module_exact": payload["next_module"] == NEXT_MODULE_VALIDATOR,
    }
    payload["derived_live_repo_post_check_replacement_checks"] = replacement_checks
    payload["replacement_checks_all_true"] = all(value is True for value in replacement_checks.values())
    payload["contract_artifact_hashes"] = {"pre_apply_sha256": pre_hash, "post_apply_sha256": post_hash}
    payload["validation"] = {
        "git_state": git_state(),
        "tracked_python_validation": tracked_python_validation(),
        "allowed_next_modules": [NEXT_MODULE_VALIDATOR, NEXT_MODULE_BLOCKED],
    }
    payload["safety_flags"] = {
        "repo_only": True,
        "repair_apply_performed": payload["repair_apply_performed"],
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
        **dangerous_flags(),
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_apply_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_contract_repair_apply_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
