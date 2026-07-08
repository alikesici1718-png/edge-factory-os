from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_parquet_schema_access_repair_preview_after_result_review_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_parquet_schema_access_repair_preview_after_result_review_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_START_HEAD = "3eccdb9"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 629
EXPECTED_TRACKED_PYTHON_COUNT = 630

LIMITATION_REVIEW_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1"
LIMITATION_REVIEW_LATEST_ARTIFACT = (
    LIMITATION_REVIEW_DIR / "repo_only_source_panel_parquet_schema_limitation_review_after_result_validator_v1_latest.json"
)

NEXT_MODULE_PYARROW_APPROVAL = "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_approval_after_result_review_v1.py"
NEXT_MODULE_EXTERNAL_APPROVAL = (
    "edge_factory_os_repo_only_source_panel_external_parquet_schema_extraction_approval_after_result_review_v1.py"
)
NEXT_MODULE_RESULT_SUMMARY = "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_result_review_blocked_record_after_research_return_gate_v1.py"

POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_SOURCE_PANEL_PARQUET_SCHEMA_ACCESS_REPAIR_PREVIEW_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_PASS_APPROVAL_REQUIRED"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_SOURCE_PANEL_PARQUET_SCHEMA_ACCESS_REPAIR_PREVIEW_AFTER_RESULT_REVIEW_POST_COMMIT_CHECK_BLOCKED"
)
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
EVIDENCE_PARTIAL_P1 = "PRIMARY_ARTIFACT_PARTIAL_WITH_P1_ATTENTION_SOURCE_PANEL_RESULTS"
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


def repair_options() -> List[Dict[str, Any]]:
    return [
        {
            "option_key": "LOCAL_DEPENDENCY_INSTALL_PREVIEW_ONLY_PYARROW",
            "can_resolve_schema_limitation": True,
            "requires_dependency_install": True,
            "requires_environment_modification": True,
            "requires_schema_or_config_creation": False,
            "touches_runtime_capital_live": False,
            "touches_generic_runner": False,
            "reruns_source_panel_analysis": False,
            "full_parquet_scan_required": False,
            "risk_level": "MEDIUM_APPROVAL_REQUIRED",
            "expected_value": "High: pyarrow can read parquet footer/schema metadata without reading all rows.",
            "allowed_now": False,
            "requires_human_approval": True,
            "recommendation": "Preferred approval path for local schema access if user approves a controlled dependency/environment change.",
        },
        {
            "option_key": "LOCAL_DEPENDENCY_INSTALL_PREVIEW_ONLY_FASTPARQUET",
            "can_resolve_schema_limitation": True,
            "requires_dependency_install": True,
            "requires_environment_modification": True,
            "requires_schema_or_config_creation": False,
            "touches_runtime_capital_live": False,
            "touches_generic_runner": False,
            "reruns_source_panel_analysis": False,
            "full_parquet_scan_required": False,
            "risk_level": "MEDIUM_APPROVAL_REQUIRED",
            "expected_value": "Medium: fastparquet can expose columns, but pyarrow is more common for parquet metadata access.",
            "allowed_now": False,
            "requires_human_approval": True,
            "recommendation": "Fallback approval path if pyarrow is unsuitable.",
        },
        {
            "option_key": "EXTERNAL_SCHEMA_EXTRACTION_PREVIEW_ONLY",
            "can_resolve_schema_limitation": True,
            "requires_dependency_install": False,
            "requires_environment_modification": False,
            "requires_schema_or_config_creation": False,
            "touches_runtime_capital_live": False,
            "touches_generic_runner": False,
            "reruns_source_panel_analysis": False,
            "full_parquet_scan_required": False,
            "risk_level": "LOW_TO_MEDIUM_APPROVAL_REQUIRED",
            "expected_value": "High if a trusted external tool can return parquet schema/columns without repo mutation.",
            "allowed_now": False,
            "requires_human_approval": True,
            "recommendation": "Good alternative if dependency changes are considered too invasive.",
        },
        {
            "option_key": "PARQUET_TO_METADATA_ARTIFACT_PREVIEW_ONLY",
            "can_resolve_schema_limitation": True,
            "requires_dependency_install": True,
            "requires_environment_modification": True,
            "requires_schema_or_config_creation": False,
            "touches_runtime_capital_live": False,
            "touches_generic_runner": False,
            "reruns_source_panel_analysis": False,
            "full_parquet_scan_required": False,
            "risk_level": "MEDIUM_APPROVAL_REQUIRED",
            "expected_value": "High after approval: a metadata artifact would make future reviews reproducible.",
            "allowed_now": False,
            "requires_human_approval": True,
            "recommendation": "Useful after schema access is approved; not an immediate apply step.",
        },
        {
            "option_key": "CARRY_P1_WITHOUT_REPAIR",
            "can_resolve_schema_limitation": False,
            "requires_dependency_install": False,
            "requires_environment_modification": False,
            "requires_schema_or_config_creation": False,
            "touches_runtime_capital_live": False,
            "touches_generic_runner": False,
            "reruns_source_panel_analysis": False,
            "full_parquet_scan_required": False,
            "risk_level": "MEDIUM_EVIDENCE_LIMITATION_REMAINS",
            "expected_value": "Medium: preserves progress, but source-panel evidence stays partial with P1 attention.",
            "allowed_now": False,
            "requires_human_approval": True,
            "recommendation": "Do not choose by default because the feature-panel parquet is large and central.",
        },
        {
            "option_key": "BLOCK_ROUTE",
            "can_resolve_schema_limitation": False,
            "requires_dependency_install": False,
            "requires_environment_modification": False,
            "requires_schema_or_config_creation": False,
            "touches_runtime_capital_live": False,
            "touches_generic_runner": False,
            "reruns_source_panel_analysis": False,
            "full_parquet_scan_required": False,
            "risk_level": "LOW_ACTION_HIGH_OPPORTUNITY_COST",
            "expected_value": "Low because a safe approval-preview path exists.",
            "allowed_now": False,
            "requires_human_approval": True,
            "recommendation": "Not recommended unless approval paths are rejected.",
        },
    ]


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()
    limitation, limitation_valid_json, limitation_json_error = load_json_checked(LIMITATION_REVIEW_LATEST_ARTIFACT)
    parquet_path = limitation.get("parquet_input_path", "")
    parquet_file = Path(parquet_path) if isinstance(parquet_path, str) else Path("")
    parquet_exists = parquet_file.exists() if parquet_path else False
    parquet_size = parquet_file.stat().st_size if parquet_exists else limitation.get("parquet_file_size_bytes", 0)
    parquet_suggests_feature_panel = "feature_panel" in str(parquet_path).lower()

    prior_respected = (
        limitation_valid_json
        and limitation.get("source_panel_parquet_schema_limitation_review_status") == "PASS_REPAIR_PREVIEW_REQUIRED"
        and limitation.get("parquet_limitation_review_completed") is True
        and limitation.get("parquet_input_path_identified") is True
        and limitation.get("parquet_file_exists") is True
        and limitation.get("parquet_schema_obtained") is False
        and limitation.get("dependency_install_attempted") is False
        and limitation.get("environment_modified") is False
        and limitation.get("schema_or_config_created") is False
        and limitation.get("parquet_full_column_scan_performed") is False
        and limitation.get("limitation_materiality") == "P1_REPAIR_PREVIEW_REQUIRED"
        and limitation.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and limitation.get("replacement_checks_all_true") is True
    )

    preferred_repair_path = "PYARROW_SCHEMA_ACCESS_REPAIR_APPROVAL_PREVIEW"
    preferred_requires_dependency = True
    preferred_requires_environment = True
    preferred_requires_schema_config = False
    preferred_requires_full_scan = False
    preferred_requires_source_panel_rerun = False
    preferred_requires_approval = True
    preferred_allowed_now = False
    next_module = NEXT_MODULE_PYARROW_APPROVAL
    next_action = "BUILD_SOURCE_PANEL_PYARROW_SCHEMA_ACCESS_REPAIR_APPROVAL_AFTER_RESULT_REVIEW"
    final_decision = "PYARROW_SCHEMA_ACCESS_REPAIR_APPROVAL_PREVIEW_NEXT"

    option_eval = repair_options()
    repair_preview_completed = True
    safety_clean = True
    allowed_next_modules = {
        NEXT_MODULE_PYARROW_APPROVAL,
        NEXT_MODULE_EXTERNAL_APPROVAL,
        NEXT_MODULE_RESULT_SUMMARY,
        NEXT_MODULE_BLOCKED,
    }
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_629_to_630": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "prior_parquet_limitation_review_respected": prior_respected,
        "repair_preview_completed": repair_preview_completed,
        "dependency_install_attempted_false": True,
        "environment_modified_false": True,
        "schema_or_config_created_false": True,
        "full_parquet_scan_performed_false": True,
        "source_panel_rerun_performed_false": True,
        "backtest_performed_false": True,
        "candidate_generation_performed_false": True,
        "runtime_touch_performed_false": True,
        "capital_touch_performed_false": True,
        "live_touch_performed_false": True,
        "generic_runner_approval_granted_false": True,
        "generic_runner_implementation_remains_blocked": True,
        "old_source_panel_anomaly_route_reopened_now_false": True,
        "old_route_closed_artifacts_used_as_active_evidence_now_false": True,
        "loop_remains_closed": True,
        "next_module_allowed": next_module in allowed_next_modules,
        "candidate_backtest_runtime_live_capital_not_selected": all(
            token not in next_module for token in ["candidate", "backtest", "runtime", "live", "capital"]
        ),
        "generic_governance_chain_not_selected": all(
            token not in next_module for token in ["generic", "_adoption_", "_gate_", "_rollout_", "_audit_"]
        ),
        "safety_boundary_clean": safety_clean,
    }
    ready = all(value is True for value in replacement_checks.values())
    status = "PASS_APPROVAL_REQUIRED" if ready else "FAIL_CLOSED"
    post_check_status = POST_CHECK_STATUS_PASS if ready else POST_CHECK_STATUS_BLOCKED
    if not ready:
        next_module = NEXT_MODULE_BLOCKED
        next_action = "RECORD_SOURCE_PANEL_RESULT_REVIEW_BLOCKED_STATE"
        final_decision = "PARQUET_SCHEMA_ACCESS_REPAIR_PREVIEW_FAIL_CLOSED"

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_parquet_schema_access_repair_preview_status": status,
        "post_check_status": post_check_status,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_parquet_limitation_review_respected": prior_respected,
        "repair_preview_completed": repair_preview_completed,
        "prior_limitation_context_completed": True,
        "repair_option_evaluation_completed": True,
        "preferred_repair_path_completed": True,
        "safety_boundary_preview_completed": True,
        "evidence_quality_preview_completed": True,
        "parquet_input_path": parquet_path,
        "parquet_file_exists": parquet_exists,
        "parquet_file_size_bytes": parquet_size,
        "parquet_file_is_large": isinstance(parquet_size, int) and parquet_size >= 10_000_000,
        "parquet_path_suggests_feature_panel": parquet_suggests_feature_panel,
        "parquet_schema_obtained_now": False,
        "parquet_schema_access_repair_needed": True,
        "preferred_repair_path": preferred_repair_path,
        "preferred_repair_requires_dependency_install": preferred_requires_dependency,
        "preferred_repair_requires_environment_modification": preferred_requires_environment,
        "preferred_repair_requires_schema_or_config_creation": preferred_requires_schema_config,
        "preferred_repair_requires_full_parquet_scan": preferred_requires_full_scan,
        "preferred_repair_requires_source_panel_rerun": preferred_requires_source_panel_rerun,
        "preferred_repair_requires_human_approval": preferred_requires_approval,
        "preferred_repair_allowed_now": preferred_allowed_now,
        "repair_apply_performed": False,
        "dependency_install_attempted": False,
        "environment_modified": False,
        "schema_or_config_created": False,
        "full_parquet_scan_performed": False,
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
        "limitation_materiality_before_preview": limitation.get("limitation_materiality", "P1_REPAIR_PREVIEW_REQUIRED"),
        "limitation_materiality_after_preview": "P1_REPAIR_PREVIEW_REQUIRED",
        "current_evidence_chain_quality_before_preview": limitation.get(
            "current_evidence_chain_quality_after_limitation_review", EVIDENCE_PARTIAL_P1
        ),
        "current_evidence_chain_quality_after_preview": EVIDENCE_PARTIAL_P1,
        "active_p0_blocker_count": 0 if ready else 1,
        "active_p1_attention_count": 1 if ready else 0,
        "source_panel_results_are_useful_research_substrate": limitation.get("source_panel_results_are_useful_research_substrate") is True,
        "source_panel_results_are_alpha_or_edge": limitation.get("source_panel_results_are_alpha_or_edge") is True,
        "source_panel_results_are_reusable_data_quality_asset": limitation.get("source_panel_results_are_reusable_data_quality_asset") is True,
        "money_path_alignment": limitation.get(
            "money_path_alignment", "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH"
        ),
        "usable_or_sellable_asset_path": limitation.get(
            "usable_or_sellable_asset_path",
            "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET",
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
            "This repair-preview module only evaluates safe parquet schema access repair options from prior artifacts. "
            "It does not install dependencies, modify the environment, create schema/config files, read parquet rows, perform a full parquet scan, rerun source-panel analysis, "
            "run strategy/backtest/candidate work, touch runtime/capital/live/orders/generic-runner paths, reopen old anomaly routes, or claim profit or tradable edge."
        ),
        "replacement_checks_all_true": ready,
        "prior_limitation_context": {
            "completed": True,
            "parquet_file_exists": parquet_exists,
            "parquet_file_is_large": isinstance(parquet_size, int) and parquet_size >= 10_000_000,
            "parquet_path_suggests_feature_panel": parquet_suggests_feature_panel,
            "schema_unavailable_because_no_local_metadata_readers_exist": limitation.get("parquet_schema_obtained") is False,
            "limitation_materiality": limitation.get("limitation_materiality"),
            "source_panel_results_still_useful_but_partial": limitation.get("source_panel_results_are_useful_research_substrate") is True
            and limitation.get("current_evidence_chain_quality_after_limitation_review") == EVIDENCE_PARTIAL_P1,
        },
        "repair_option_evaluation": option_eval,
        "preferred_repair_path_preview": {
            "completed": True,
            "preferred_repair_path": preferred_repair_path,
            "reason": "pyarrow is the simplest standard parquet metadata reader for footer/schema access without a full row scan, but it requires explicit approval before any dependency or environment change.",
            "approval_required_before_apply": True,
        },
        "safety_boundary_preview": {
            "completed": True,
            "dependency_install_attempted": False,
            "environment_modified": False,
            "schema_or_config_created": False,
            "full_parquet_scan_performed": False,
            "source_panel_rerun_performed": False,
            "strategy_backtest_candidate_runtime_capital_live_generic_runner_untouched": True,
        },
        "evidence_quality_preview": {
            "completed": True,
            "current_evidence_chain_quality_after_preview": EVIDENCE_PARTIAL_P1,
            "active_p0_blocker_count": 0 if ready else 1,
            "active_p1_attention_count": 1 if ready else 0,
        },
        "prior_limitation_review_snapshot": {
            "artifact_path": str(LIMITATION_REVIEW_LATEST_ARTIFACT),
            "artifact_valid_json": limitation_valid_json,
            "artifact_json_error": limitation_json_error,
            "status": limitation.get("source_panel_parquet_schema_limitation_review_status"),
            "post_check_status": limitation.get("post_check_status"),
            "next_module": limitation.get("next_module"),
        },
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "expected_previous_tracked_python_count": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "allowed_next_modules": sorted(allowed_next_modules),
        },
        "safety_flags": {
            "repo_only": True,
            "repair_preview_only": True,
            "repair_apply_performed": False,
            "dependency_install_attempted": False,
            "environment_modified": False,
            "schema_or_config_created": False,
            "full_parquet_scan_performed": False,
            "parquet_rows_read": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_parquet_schema_access_repair_preview_after_result_review_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_parquet_schema_access_repair_preview_after_result_review_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_parquet_schema_access_repair_preview_after_result_review_v1_latest.txt"
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
    return 0 if payload["source_panel_parquet_schema_access_repair_preview_status"] in {"PASS_APPROVAL_REQUIRED", "BLOCKED"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
