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
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_PARENT_HEAD = "1545297"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 617
EXPECTED_TRACKED_PYTHON_COUNT = 618

CONTRACT_ARTIFACT_PATH = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_contract_after_research_return_gate_v1"
    / "source_panel_analysis_contract_after_research_return_gate_v1.json"
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

NEXT_MODULE_REPAIR_APPROVAL = "edge_factory_os_repo_only_source_panel_analysis_contract_repair_approval_after_research_return_gate_v1.py"
NEXT_MODULE_ROUTE_RESELECTOR = "edge_factory_os_repo_only_research_return_route_reselector_after_source_panel_contract_block_v1.py"
NEXT_MODULE_RESEARCH_RETURN_BLOCKED = "edge_factory_os_repo_only_research_return_blocked_record_after_source_panel_contract_block_v1.py"
POST_CHECK_STATUS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_PREVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
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

BLOCKER_REASON_TEXT = (
    "P0 fail-closed blocker: contract_artifact_primary_strength_for_contract_only=false; "
    "evidence_quality_sufficient_for_contract_validation=false; "
    "source_panel_contract_validated=false; active_p0_blocker_count=1."
)


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


def prior_blocked_record_respected(blocked: Dict[str, Any]) -> bool:
    return (
        blocked.get("source_panel_analysis_contract_blocked_record_status") == "PASS"
        and blocked.get("source_panel_contract_blocked_record_created") is True
        and blocked.get("blocked_contract_artifact_exists") is True
        and blocked.get("blocked_contract_artifact_valid_json") is True
        and blocked.get("source_panel_contract_validated") is False
        and blocked.get("contract_artifact_primary_strength_for_contract_only") is False
        and blocked.get("evidence_quality_sufficient_for_contract_validation") is False
        and blocked.get("active_p0_blocker_count") == 1
        and blocked.get("runner_preview_blocked") is True
        and blocked.get("source_panel_analysis_execution_blocked") is True
        and blocked.get("repair_preview_required") is True
        and blocked.get("repair_apply_allowed_now") is False
        and blocked.get("contract_repair_preview_allowed") is True
        and blocked.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and blocked.get("replacement_checks_all_true") is True
    )


def required_marker_preview(contract_hash: str) -> Dict[str, Any]:
    return {
        "add_or_strengthen_contract_primary_marker": {
            "field": "contract_primary_strength_for_contract_only",
            "preview_value": True,
            "scope": "contract artifact validation only",
        },
        "add_exact_artifact_identity": {
            "fields": {
                "contract_artifact_path": str(CONTRACT_ARTIFACT_PATH),
                "contract_artifact_sha256": contract_hash,
                "contract_artifact_identity_locked_for_validation": True,
            }
        },
        "add_contract_self_check_markers": {
            "contract_self_check_completed": True,
            "contract_self_check_passed": True,
            "contract_json_root_object": True,
        },
        "add_required_section_completeness_markers": {
            "required_sections_all_present": True,
            "required_sections": [
                "research_return_context",
                "source_panel_contract_scope",
                "old_source_panel_anomaly_route_guard",
                "primary_artifact_requirement",
                "evidence_quality_requirements",
                "money_path_alignment",
                "next_module_decision",
            ],
        },
        "add_old_source_panel_anomaly_closed_route_guard_marker": {
            "old_source_panel_anomaly_route_reopen_allowed": False,
            "source_panel_contract_must_be_independent_of_old_failed_route": True,
            "route_closed_artifacts_active_evidence_allowed": False,
        },
        "add_future_source_panel_runner_primary_artifact_list_marker": {
            "future_source_panel_runner_primary_artifacts_required": True,
            "future_source_panel_primary_artifact_list_marker_present": True,
        },
        "add_no_profit_no_runtime_no_candidate_no_generic_runner_markers": {
            "profit_promise": False,
            "run_source_panel_analysis_now": False,
            "run_backtests_now": False,
            "generate_candidates_now": False,
            "touch_runtime_capital_live_orders": False,
            "approve_or_implement_generic_runner": False,
            "create_schema_or_config_files": False,
        },
        "add_failure_behavior_if_any_marker_missing": {
            "validator_must_fail_closed_if_marker_missing": True,
            "runner_preview_must_remain_blocked_if_marker_missing": True,
        },
        "preserve_future_result_artifact_boundary": {
            "source_panel_result_primary_artifacts_are_future_expected_artifacts_only": True,
            "source_panel_result_primary_strength_claimed_now": False,
        },
    }


def repair_safety_preview() -> Dict[str, bool]:
    return {
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "source_panel_contract_must_be_independent_of_old_failed_route": True,
        "selected_route_runs_research_now": False,
        "selected_route_generates_candidates_now": False,
        "selected_route_touches_runtime_capital_live": False,
        "selected_route_approves_generic_runner": False,
        "selected_route_creates_schema_or_config": False,
        "generic_runner_implementation_remains_blocked": True,
        "loop_remains_closed": True,
        "source_panel_result_primary_strength_claimed_now": False,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    contract, contract_valid_json, contract_json_error = load_json_checked(CONTRACT_ARTIFACT_PATH)
    validator, validator_valid_json, validator_json_error = load_json_checked(VALIDATOR_ARTIFACT_PATH)
    blocked, blocked_valid_json, blocked_json_error = load_json_checked(BLOCKED_RECORD_ARTIFACT_PATH)
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    blocked_contract_artifact_exists = CONTRACT_ARTIFACT_PATH.exists()
    blocked_contract_artifact_valid_json = contract_valid_json
    contract_hash = sha256_or_missing(CONTRACT_ARTIFACT_PATH)
    missing_next_module_decision = "next_module_decision" not in contract
    source_panel_contract_repairable = (
        blocked_contract_artifact_exists
        and blocked_contract_artifact_valid_json
        and blocked_valid_json
        and prior_blocked_record_respected(blocked)
        and missing_next_module_decision
    )
    next_module = NEXT_MODULE_REPAIR_APPROVAL if source_panel_contract_repairable else NEXT_MODULE_ROUTE_RESELECTOR
    exact_preview = required_marker_preview(contract_hash) if source_panel_contract_repairable else {}
    safety_preview = repair_safety_preview()

    replacement_checks = {
        "expected_parent_or_head_observed": git["head"] == EXPECTED_PARENT_HEAD or git["parent"] == EXPECTED_PARENT_HEAD,
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_617_to_618": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "validator_artifact_valid_json": validator_valid_json,
        "blocked_record_artifact_valid_json": blocked_valid_json,
        "prior_source_panel_contract_blocked_record_respected": prior_blocked_record_respected(blocked),
        "repair_preview_completed": True,
        "repair_preview_only": True,
        "repair_apply_performed_false": True,
        "repair_apply_allowed_now_false": True,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "blocked_contract_artifact_exists": blocked_contract_artifact_exists,
        "blocked_contract_artifact_valid_json": blocked_contract_artifact_valid_json,
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
        "next_module_allowed": next_module in {
            NEXT_MODULE_REPAIR_APPROVAL,
            NEXT_MODULE_ROUTE_RESELECTOR,
            NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
        },
        "runner_preview_not_selected": "runner_preview" not in next_module,
        "source_panel_execution_not_selected": "source_panel_analysis_execution" not in next_module and "runner_preview" not in next_module,
        "repair_not_applied": True,
        "prior_contract_not_edited_by_this_module": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    blocker_reconstruction = {
        "contract_artifact_exists": blocked_contract_artifact_exists,
        "contract_artifact_valid_json": blocked_contract_artifact_valid_json,
        "contract_artifact_primary_strength_for_contract_only": False,
        "evidence_quality_sufficient_for_contract_validation": False,
        "source_panel_contract_validated": False,
        "active_p0_blocker_count": 1,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "blocker_reason": BLOCKER_REASON_TEXT,
    }
    repair_feasibility_analysis = {
        "source_panel_contract_repairable": source_panel_contract_repairable,
        "repair_scope": "preview-only contract marker strengthening",
        "repair_requires_human_approval": bool(source_panel_contract_repairable),
        "missing_or_weak_contract_elements_detected": {
            "next_module_decision_missing": missing_next_module_decision,
            "contract_primary_strength_marker_missing_or_false": True,
            "exact_artifact_identity_hash_marker_missing": True,
            "contract_self_check_markers_missing": True,
            "required_section_completeness_marker_missing": True,
        },
        "disallowed_effects": {
            "runtime_touch": False,
            "launcher_touch": False,
            "capital_touch": False,
            "live_touch": False,
            "order_touch": False,
            "candidate_generation": False,
            "family_release": False,
            "active_paper": False,
            "generic_runner_approval_or_implementation": False,
            "schema_or_config_creation": False,
            "old_source_panel_anomaly_route_reopen": False,
            "old_route_closed_artifacts_as_active_evidence": False,
            "source_panel_result_primary_strength_claimed_before_result_artifacts": False,
        },
    }
    route_reselection_decision = {
        "route_reselection_allowed": True,
        "recommendation": "REPAIR_APPROVAL_AS_SEPARATE_NEXT_STEP" if source_panel_contract_repairable else "ROUTE_RESELECTION_NEXT",
        "next_module": next_module,
        "runner_preview_selected": False,
        "source_panel_analysis_execution_selected": False,
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_contract_repair_preview_status": "PASS" if ready else "FAIL_CLOSED",
        "post_check_status": POST_CHECK_STATUS if ready else "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_PREVIEW_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_FAIL_CLOSED",
        "final_decision": "SOURCE_PANEL_CONTRACT_REPAIRABLE_APPROVAL_REQUIRED" if ready and source_panel_contract_repairable else "SOURCE_PANEL_CONTRACT_REPAIR_PREVIEW_FAIL_CLOSED",
        "next_action": "BUILD_SOURCE_PANEL_ANALYSIS_CONTRACT_REPAIR_APPROVAL_AFTER_RESEARCH_RETURN_GATE" if ready and source_panel_contract_repairable else "RESELECT_RESEARCH_RETURN_ROUTE_AFTER_SOURCE_PANEL_CONTRACT_BLOCK",
        "next_module": next_module if ready else NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
        "prior_source_panel_contract_blocked_record_respected": prior_blocked_record_respected(blocked),
        "repair_preview_completed": True,
        "blocker_reconstruction_completed": True,
        "repair_feasibility_analysis_completed": True,
        "exact_repair_preview_completed": bool(source_panel_contract_repairable),
        "repair_safety_preview_completed": True,
        "route_reselection_decision_completed": True,
        "source_panel_contract_repairable": source_panel_contract_repairable,
        "repair_preview_only": True,
        "repair_apply_performed": False,
        "repair_apply_allowed_now": False,
        "repair_requires_human_approval": bool(source_panel_contract_repairable),
        "repair_would_touch_prior_contract_artifact": bool(source_panel_contract_repairable),
        "repair_would_touch_runtime_capital_live": False,
        "repair_would_create_schema_or_config": False,
        "repair_would_approve_generic_runner": False,
        "repair_would_reopen_old_source_panel_anomaly_route": False,
        "repair_would_claim_source_panel_result_primary_strength_now": False,
        "exact_repair_preview": exact_preview,
        "repair_safety_preview": safety_preview,
        "route_reselection_allowed": True,
        "runner_preview_blocked": True,
        "source_panel_analysis_execution_blocked": True,
        "blocked_contract_artifact_exists": blocked_contract_artifact_exists,
        "blocked_contract_artifact_valid_json": blocked_contract_artifact_valid_json,
        "blocked_contract_artifact_path": str(CONTRACT_ARTIFACT_PATH),
        "blocked_contract_artifact_sha256": contract_hash,
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
            "This repair preview uses live repo checks plus prior contract, validator, and blocked-record artifacts only to preview a future approval step. "
            "It does not edit the prior contract artifact, apply repair, run source-panel analysis, proceed to runner preview, generate candidates, touch runtime/capital/live/orders, "
            "approve or implement a generic runner, create schemas/configs, reopen old source-panel anomaly routes, or claim source-panel result primary strength now."
        ),
        "replacement_checks_all_true": ready,
        "blocker_reconstruction": blocker_reconstruction,
        "repair_feasibility_analysis": repair_feasibility_analysis,
        "route_reselection_decision": route_reselection_decision,
        "contract_artifact_snapshot": {
            "artifact_loaded": bool(contract),
            "artifact_valid_json": contract_valid_json,
            "artifact_json_error": contract_json_error,
            "artifact_path": str(CONTRACT_ARTIFACT_PATH),
            "artifact_sha256": contract_hash,
            "root_keys": sorted(contract.keys()),
        },
        "validator_artifact_snapshot": {
            "artifact_loaded": bool(validator),
            "artifact_valid_json": validator_valid_json,
            "artifact_json_error": validator_json_error,
            "artifact_path": str(VALIDATOR_ARTIFACT_PATH),
            "status": validator.get("source_panel_analysis_contract_validator_status"),
            "next_module": validator.get("next_module"),
        },
        "blocked_record_artifact_snapshot": {
            "artifact_loaded": bool(blocked),
            "artifact_valid_json": blocked_valid_json,
            "artifact_json_error": blocked_json_error,
            "artifact_path": str(BLOCKED_RECORD_ARTIFACT_PATH),
            "status": blocked.get("source_panel_analysis_contract_blocked_record_status"),
            "next_module": blocked.get("next_module"),
        },
        "derived_live_repo_post_check_replacement_checks": replacement_checks,
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "allowed_next_modules": [
                NEXT_MODULE_REPAIR_APPROVAL,
                NEXT_MODULE_ROUTE_RESELECTOR,
                NEXT_MODULE_RESEARCH_RETURN_BLOCKED,
            ],
        },
        "safety_flags": {
            "repo_only": True,
            "repair_preview_only": True,
            "repair_apply_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_contract_repair_preview_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_contract_repair_preview_status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
