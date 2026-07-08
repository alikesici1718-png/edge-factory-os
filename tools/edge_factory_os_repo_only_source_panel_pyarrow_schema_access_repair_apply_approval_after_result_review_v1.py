from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_approval_after_result_review_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_approval_after_result_review_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "1cee76d"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 632
EXPECTED_TRACKED_PYTHON_COUNT = 633

PARQUET_INPUT_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_feature_panels"
    r"\market_panic_rebound_long_v1\market_panic_rebound_long_v1_feature_panel_1h.parquet"
)
EXPECTED_PARQUET_SIZE_BYTES = 99504547

PRIOR_PREVIEW_DIR = (
    LAB_ROOT / "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_preview_after_result_review_v1"
)
PRIOR_PREVIEW_LATEST_ARTIFACT = (
    PRIOR_PREVIEW_DIR
    / "repo_only_source_panel_pyarrow_schema_access_repair_apply_preview_after_result_review_v1_latest.json"
)

NEXT_MODULE_APPLY = "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1.py"
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_source_panel_analysis_result_review_blocked_record_after_research_return_gate_v1.py"
)

POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_APPROVAL_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_PASS_APPLY_NEXT"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_APPROVAL_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_BLOCKED"
)
APPROVAL_STATUS_PASS = "PASS_APPLY_APPROVAL_RECORD_CREATED_APPLY_NEXT"
APPROVAL_STATUS_FAIL = "FAIL_CLOSED_APPLY_APPROVAL_RECORD_INVALID"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
EVIDENCE_PARTIAL_P1 = "PRIMARY_ARTIFACT_PARTIAL_WITH_P1_ATTENTION_SOURCE_PANEL_RESULTS"
LIMITATION_P1 = "P1_REPAIR_PREVIEW_REQUIRED"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
INSTALL_COMMAND_PREVIEW = "python -m pip install --user pyarrow"
INSTALL_SCOPE_PREVIEW = "LOCAL_USER_OR_ISOLATED_ENVIRONMENT_ONLY_NOT_GLOBAL_IF_AVOIDABLE"

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
    if args and args[0] == "git":
        safe_args = ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", *args[1:]]
    else:
        safe_args = args
    result = subprocess.run(
        safe_args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
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
    head = run_cmd(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    parent = run_cmd(["git", "rev-parse", "--short", "HEAD^"]).stdout.strip()
    return {
        "head": head,
        "parent": parent,
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": changed_paths == [CURRENT_TOOL_REL]
        or (len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL]),
        "expected_start_head_or_parent_observed": head == EXPECTED_START_HEAD or parent == EXPECTED_START_HEAD,
    }


def planned_schema_existing_files() -> List[str]:
    return sorted(rel for rel in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel).exists())


def dangerous_flags() -> Dict[str, bool]:
    return {flag: False for flag in DANGEROUS_FLAGS}


def module_availability() -> Dict[str, bool]:
    return {
        "pyarrow_installed_now": importlib.util.find_spec("pyarrow") is not None,
        "fastparquet_installed_now": importlib.util.find_spec("fastparquet") is not None,
        "duckdb_installed_now": importlib.util.find_spec("duckdb") is not None,
    }


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    prior, prior_valid_json, prior_json_error = load_json_checked(PRIOR_PREVIEW_LATEST_ARTIFACT)
    availability = module_availability()

    parquet_exists = PARQUET_INPUT_PATH.exists()
    parquet_size = PARQUET_INPUT_PATH.stat().st_size if parquet_exists else 0
    parquet_suggests_feature_panel = "feature_panel" in str(PARQUET_INPUT_PATH).lower()
    schema_unavailable = not any(availability.values())

    prior_apply_preview_respected = (
        prior_valid_json
        and prior.get("source_panel_pyarrow_schema_access_repair_apply_preview_status")
        == "PASS_APPLY_PREVIEW_CREATED_APPROVAL_REQUIRED"
        and prior.get("post_check_status")
        == "REPO_ONLY_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_PREVIEW_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_PASS_APPLY_APPROVAL_NEXT"
        and prior.get("repair_apply_preview_completed") is True
        and prior.get("parquet_input_path") == str(PARQUET_INPUT_PATH)
        and prior.get("parquet_file_exists") is True
        and prior.get("parquet_schema_obtained_now") is False
        and prior.get("parquet_schema_access_repair_needed") is True
        and prior.get("dependency_candidate") == "pyarrow"
        and prior.get("install_command_preview") == INSTALL_COMMAND_PREVIEW
        and prior.get("install_scope_preview") == INSTALL_SCOPE_PREVIEW
        and prior.get("future_apply_requires_human_approval") is True
        and prior.get("future_apply_allowed_now") is False
        and prior.get("repair_apply_performed") is False
        and prior.get("dependency_install_attempted") is False
        and prior.get("environment_modified") is False
        and prior.get("schema_or_config_created") is False
        and prior.get("full_parquet_scan_performed") is False
        and prior.get("parquet_rows_read_now") is False
        and prior.get("source_panel_rerun_performed") is False
        and prior.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and prior.get("replacement_checks_all_true") is True
    )

    approval_scope = {
        "approval_grants_pyarrow_repair_apply_approval_record_only": True,
        "approval_grants_dependency_install_now": False,
        "approval_grants_environment_modification_now": False,
        "approval_grants_pyarrow_install_now": False,
        "approval_grants_schema_or_config_creation_now": False,
        "approval_grants_full_parquet_scan_now": False,
        "approval_grants_parquet_row_read_now": False,
        "approval_grants_source_panel_rerun_now": False,
        "approval_grants_backtest_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_generic_runner_now": False,
    }

    current_safety_boundary = {
        "repair_apply_performed": False,
        "dependency_install_attempted": False,
        "environment_modified": False,
        "pyarrow_install_attempted": False,
        "schema_or_config_created": False,
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
        "source_panel_rerun_performed": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
    }

    future_apply_boundary = {
        "may_install_pyarrow_in_local_user_or_isolated_environment_only": True,
        "must_log_interpreter_path": True,
        "must_log_pip_version_and_package_list_before_and_after": True,
        "must_log_pyarrow_version_and_install_result": True,
        "may_attempt_parquet_schema_metadata_read_only": True,
        "may_write_schema_metadata_artifact_only": True,
        "must_avoid_full_row_scan": True,
        "must_avoid_source_panel_rerun": True,
        "must_avoid_strategy_backtest_candidate_runtime_capital_live_generic_runner_schema_config": True,
    }

    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_632_to_633": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "prior_apply_preview_respected": prior_apply_preview_respected,
        "parquet_file_exists": parquet_exists,
        "parquet_file_size_matches_expected": parquet_size == EXPECTED_PARQUET_SIZE_BYTES,
        "parquet_file_is_large": parquet_size >= 10_000_000,
        "parquet_path_suggests_feature_panel": parquet_suggests_feature_panel,
        "parquet_schema_unavailable_now": schema_unavailable,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "approval_record_only": approval_scope["approval_grants_pyarrow_repair_apply_approval_record_only"] is True,
        "approval_grants_no_current_install_or_environment_change": all(
            [
                approval_scope["approval_grants_dependency_install_now"] is False,
                approval_scope["approval_grants_environment_modification_now"] is False,
                approval_scope["approval_grants_pyarrow_install_now"] is False,
                current_safety_boundary["dependency_install_attempted"] is False,
                current_safety_boundary["environment_modified"] is False,
                current_safety_boundary["pyarrow_install_attempted"] is False,
            ]
        ),
        "approval_grants_no_schema_config_scan_row_read_rerun": all(
            [
                approval_scope["approval_grants_schema_or_config_creation_now"] is False,
                approval_scope["approval_grants_full_parquet_scan_now"] is False,
                approval_scope["approval_grants_parquet_row_read_now"] is False,
                approval_scope["approval_grants_source_panel_rerun_now"] is False,
                current_safety_boundary["schema_or_config_created"] is False,
                current_safety_boundary["full_parquet_scan_performed"] is False,
                current_safety_boundary["parquet_rows_read_now"] is False,
                current_safety_boundary["source_panel_rerun_performed"] is False,
            ]
        ),
        "no_strategy_backtest_candidate_runtime_capital_live_generic_runner_now": all(
            [
                approval_scope["approval_grants_backtest_now"] is False,
                approval_scope["approval_grants_candidate_generation_now"] is False,
                approval_scope["approval_grants_runtime_capital_live_now"] is False,
                approval_scope["approval_grants_generic_runner_now"] is False,
                current_safety_boundary["strategy_signal_claims_made"] is False,
                current_safety_boundary["tradable_edge_claims_made"] is False,
                current_safety_boundary["profit_claims_made"] is False,
                current_safety_boundary["backtest_performed"] is False,
                current_safety_boundary["candidate_generation_performed"] is False,
                current_safety_boundary["runtime_touch_performed"] is False,
                current_safety_boundary["capital_touch_performed"] is False,
                current_safety_boundary["live_touch_performed"] is False,
                current_safety_boundary["generic_runner_approval_granted"] is False,
                current_safety_boundary["generic_runner_implementation_remains_blocked"] is True,
            ]
        ),
        "old_anomaly_route_stays_closed": current_safety_boundary["old_source_panel_anomaly_route_reopened_now"] is False
        and current_safety_boundary["old_route_closed_artifacts_used_as_active_evidence_now"] is False,
        "future_apply_boundary_restricted_to_schema_metadata": all(value is True for value in future_apply_boundary.values()),
        "next_module_is_apply_not_result_summary": NEXT_MODULE_APPLY.endswith("_apply_after_result_review_v1.py"),
        "loop_remains_closed": True,
    }
    ready = all(value is True for value in replacement_checks.values())

    next_module = NEXT_MODULE_APPLY if ready else NEXT_MODULE_BLOCKED
    status = APPROVAL_STATUS_PASS if ready else APPROVAL_STATUS_FAIL
    final_decision = (
        "PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_APPROVAL_RECORD_CREATED_APPLY_NEXT"
        if ready
        else "PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_APPROVAL_FAIL_CLOSED"
    )
    next_action = (
        "BUILD_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPLY_AFTER_RESULT_REVIEW"
        if ready
        else "RECORD_SOURCE_PANEL_RESULT_REVIEW_BLOCKED_STATE"
    )

    approval_context = {
        "parquet_file_exists_and_is_large": parquet_exists and parquet_size >= 10_000_000,
        "path_suggests_feature_panel": parquet_suggests_feature_panel,
        "parquet_schema_remains_unavailable": schema_unavailable,
        "apply_preview_recommended_pyarrow": prior.get("dependency_candidate") == "pyarrow",
        "install_command_preview_exists": prior.get("install_command_preview") == INSTALL_COMMAND_PREVIEW,
        "future_apply_requires_human_approval": True,
        "install_or_apply_occurs_now": False,
    }

    evidence_state = {
        "current_evidence_chain_quality": EVIDENCE_PARTIAL_P1,
        "limitation_materiality": LIMITATION_P1,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "no_upgrade_until_future_apply_and_validator": True,
    }

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_pyarrow_schema_access_repair_apply_approval_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if ready else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_apply_preview_respected": prior_apply_preview_respected,
        "pyarrow_schema_access_repair_apply_approval_record_created": ready,
        "user_pyarrow_repair_apply_approval_present": True,
        "user_pyarrow_repair_apply_approval_scope": (
            "APPLY_APPROVAL_RECORD_ONLY_FUTURE_LOCAL_OR_ISOLATED_PYARROW_SCHEMA_METADATA_ACCESS_NO_INSTALL_NOW"
        ),
        **approval_scope,
        "parquet_input_path": str(PARQUET_INPUT_PATH),
        "parquet_file_exists": parquet_exists,
        "parquet_file_size_bytes": parquet_size,
        "parquet_file_size_matches_expected": parquet_size == EXPECTED_PARQUET_SIZE_BYTES,
        "parquet_file_is_large": parquet_size >= 10_000_000,
        "parquet_path_suggests_feature_panel": parquet_suggests_feature_panel,
        "parquet_schema_obtained_now": False,
        "parquet_schema_access_repair_needed": True,
        "dependency_candidate": "pyarrow",
        "install_command_preview": INSTALL_COMMAND_PREVIEW,
        "install_scope_preview": INSTALL_SCOPE_PREVIEW,
        "future_apply_requires_human_approval": True,
        "pyarrow_repair_apply_allowed_next": ready,
        **current_safety_boundary,
        "limitation_materiality_before_approval": LIMITATION_P1,
        "limitation_materiality_after_approval": LIMITATION_P1,
        "current_evidence_chain_quality_before_approval": EVIDENCE_PARTIAL_P1,
        "current_evidence_chain_quality_after_approval": EVIDENCE_PARTIAL_P1,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "source_panel_results_are_useful_research_substrate": True,
        "source_panel_results_are_alpha_or_edge": False,
        "source_panel_results_are_reusable_data_quality_asset": True,
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH",
        "usable_or_sellable_asset_path": (
            "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET"
        ),
        "evidence_chain_policy_level": POLICY_LEVEL,
        "future_modules_must_classify_evidence_quality": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
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
            "This apply-approval module creates only a repo-only approval record for a future pyarrow schema-access "
            "repair apply step. It does not install pyarrow or any dependency, modify the environment, create schema/"
            "config files, read parquet rows, perform a full parquet scan, rerun source-panel analysis, run strategy/"
            "backtest/candidate work, touch runtime/capital/live/order paths, approve or implement the generic runner, "
            "reopen the old anomaly route, or claim profit/tradable edge."
        ),
        "replacement_checks_all_true": ready,
        "approval_context": approval_context,
        "approval_scope": approval_scope,
        "future_apply_boundary": future_apply_boundary,
        "current_safety_boundary": {
            **current_safety_boundary,
            "strategy_backtest_candidate_runtime_capital_live_generic_runner_untouched": True,
            "old_anomaly_route_not_reopened": True,
        },
        "evidence_state": evidence_state,
        "next_module_decision": {
            "approval_record_valid": ready,
            "next_module_if_valid": NEXT_MODULE_APPLY,
            "next_module_if_unsafe": NEXT_MODULE_BLOCKED,
            "selected_next_module": next_module,
            "result_summary_selected": False,
            "source_panel_rerun_selected": False,
            "candidate_backtest_runtime_live_capital_generic_runner_schema_config_selected": False,
            "generic_review_adoption_gate_rollout_audit_selected": False,
        },
        "prior_apply_preview_snapshot": {
            "artifact_path": str(PRIOR_PREVIEW_LATEST_ARTIFACT),
            "artifact_valid_json": prior_valid_json,
            "artifact_json_error": prior_json_error,
            "status": prior.get("source_panel_pyarrow_schema_access_repair_apply_preview_status"),
            "post_check_status": prior.get("post_check_status"),
            "repair_apply_preview_completed": prior.get("repair_apply_preview_completed"),
            "next_module": prior.get("next_module"),
        },
        "schema_reader_availability": {
            **availability,
            "parquet_tools_available_now": False,
            "schema_readers_unavailable": schema_unavailable,
            "schema_reader_check_did_not_import_pyarrow": True,
            "schema_reader_check_did_not_read_parquet": True,
        },
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "expected_previous_tracked_python_count": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "replacement_checks": replacement_checks,
        },
        "safety_flags": {
            "repo_only": True,
            "apply_approval_record_only": True,
            "repair_apply_performed": False,
            "dependency_install_attempted": False,
            "environment_modified": False,
            "pyarrow_install_attempted": False,
            "schema_or_config_created": False,
            "full_parquet_scan_performed": False,
            "parquet_rows_read_now": False,
            "source_panel_rerun_performed": False,
            "strategy_research_run_performed": False,
            "backtest_performed": False,
            "candidate_generation_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_pyarrow_schema_access_repair_apply_approval_after_result_review_v1_latest.json"
    timestamped_json = (
        OUT_DIR / f"repo_only_source_panel_pyarrow_schema_access_repair_apply_approval_after_result_review_v1_{stamp}.json"
    )
    latest_txt = OUT_DIR / "repo_only_source_panel_pyarrow_schema_access_repair_apply_approval_after_result_review_v1_latest.txt"
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
    return 0 if payload["source_panel_pyarrow_schema_access_repair_apply_approval_status"] == APPROVAL_STATUS_PASS else 3


if __name__ == "__main__":
    raise SystemExit(main())
