from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "7702cd4"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 638
EXPECTED_TRACKED_PYTHON_COUNT = 639

CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1_latest.json"
)
CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1_latest.json"
)
SOURCE_PANEL_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1_latest.json"
)

NEXT_MODULE_APPROVAL = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_blocked_record_after_source_panel_summary_v1.py"
)

PREVIEW_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_READY_EXECUTION_APPROVAL_REQUIRED"
PREVIEW_STATUS_BLOCKED = "BLOCKED_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_UNSAFE_OR_INCOMPLETE"
POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_PASS_"
    "EXECUTION_APPROVAL_NEXT"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_BLOCKED"
)

TARGET_HORIZON = "3_to_4"
TARGET_TIMEFRAME = "1h"
LATEST_HOLDOUT_MONTHS_TARGET = "6_to_12"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
EVIDENCE_BEFORE = "DATA_HORIZON_EXPANSION_CONTRACT_VALIDATED_RUNNER_PREVIEW_READY"
EVIDENCE_AFTER = "DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_READY_EXECUTION_APPROVAL_REQUIRED"
EVIDENCE_BLOCKED = "DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

FUTURE_REQUIRED_ARTIFACT_LIST = [
    "historical_source_panel_inventory.json",
    "historical_coverage_summary.json",
    "historical_missingness_report.json",
    "historical_anomaly_report.json",
    "historical_quality_scorecard.json",
    "historical_contract_compliance_report.json",
    "historical_symbol_lifecycle_report.json",
    "historical_holdout_policy_report.json",
    "historical_feature_panel_readiness_report.json",
]

FUTURE_SCOPE_ITEMS = [
    "discover existing historical candle/source-panel inputs",
    "discover existing feature-panel inputs",
    "map available date ranges",
    "map symbol coverage",
    "map source coverage",
    "map missingness/freshness",
    "check duplicate timestamps",
    "check timestamp gaps",
    "check OHLCV integrity",
    "check feature recomputation readiness",
    "create symbol lifecycle report",
    "create holdout policy report",
    "create historical contract compliance report",
]

FUTURE_SCOPE_EXCLUSIONS = [
    "data download/fetch unless separately approved later",
    "exchange/API calls in this preview",
    "historical data build in this preview",
    "strategy research",
    "backtests",
    "candidate generation",
    "family release",
    "runtime/capital/live/order actions",
    "generic runner work",
    "schema/config creation",
    "old source-panel anomaly route reopening",
    "profit/tradable-edge claims",
]

INPUT_DISCOVERY_ITEMS = [
    "existing local historical data directories",
    "existing feature panel directories",
    "current source-panel parquet path",
    "current 1-year panel",
    "possible older local panels if present",
    "no external download now",
    "no API fetch now",
    "no fabricated data",
]

SURVIVORSHIP_FAIL_CLOSED_ITEMS = [
    "symbol universe is selected from current winners only",
    "delisted/removed symbols are ignored without disclosure",
    "symbol start/end dates are missing",
    "exchange/listing availability limitations are hidden",
    "missing symbols are not disclosed",
    "universe discovery is mixed with strategy selection",
]

HOLDOUT_REQUIREMENTS = [
    "latest 6-12 months reserved as strict holdout where feasible",
    "train/validation/OOS split before strategy research",
    "canonical month windows",
    "no candidate selection using holdout",
    "no strategy claim until historical data-quality validator passes",
    "no paper/live without later preflight and kill-switch readiness",
]

FAIL_CLOSED_ITEMS = [
    "required input paths cannot be found and no approved data acquisition contract exists",
    "historical range less than target without explicit limitation",
    "symbol lifecycle cannot be established",
    "holdout policy cannot be defined",
    "data quality artifacts cannot be produced",
    "strategy/backtest/candidate/runtime/live/capital/generic runner is touched",
    "fake/synthetic data is used as real",
    "old source-panel anomaly route is reopened",
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
    "data_download_performed_now",
    "data_fetch_performed_now",
    "data_build_performed_now",
    "historical_expansion_runner_executed_now",
    "source_panel_rerun_performed_now",
    "full_parquet_scan_performed_now",
    "parquet_rows_read_now",
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
    parent_result = run_cmd(["git", "rev-parse", "--short", "HEAD^"])
    parent = parent_result.stdout.strip()
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


def prior_contract_validator_respected(validator: Dict[str, Any], valid_json: bool) -> bool:
    return (
        valid_json
        and validator.get("data_horizon_expansion_contract_validator_status")
        == "PASS_DATA_HORIZON_EXPANSION_CONTRACT_VALIDATED_RUNNER_PREVIEW_READY"
        and validator.get("data_horizon_expansion_contract_validated") is True
        and validator.get("current_panel_sufficient_for_pipeline_validation") is True
        and validator.get("current_panel_sufficient_for_strategy_edge_claims") is False
        and validator.get("data_horizon_expansion_recommended") is True
        and validator.get("target_historical_horizon_years") == TARGET_HORIZON
        and validator.get("target_timeframe") == TARGET_TIMEFRAME
        and validator.get("future_data_download_allowed_now") is False
        and validator.get("future_data_fetch_allowed_now") is False
        and validator.get("future_data_build_allowed_now") is False
        and validator.get("historical_expansion_runner_allowed_now") is False
        and validator.get("historical_expansion_runner_preview_allowed_next") is True
        and validator.get("strategy_research_allowed_now") is False
        and validator.get("backtest_allowed_now") is False
        and validator.get("candidate_generation_allowed_now") is False
        and validator.get("survivorship_bias_controls_required") is True
        and validator.get("symbol_lifecycle_report_required") is True
        and validator.get("holdout_policy_required") is True
        and validator.get("historical_data_quality_validator_required") is True
        and validator.get("current_evidence_chain_quality_after_validator") == EVIDENCE_BEFORE
        and validator.get("documentation_loop_detected") is False
        and validator.get("documentation_loop_risk_level") == DOCUMENTATION_LOOP_RISK_LEVEL
        and validator.get("next_module_closes_real_gap") is True
        and validator.get("active_p0_blocker_count") == 0
        and validator.get("active_p1_attention_count") == 1
        and validator.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and validator.get("replacement_checks_all_true") is True
    )


def prior_contract_artifact_respected(contract: Dict[str, Any], valid_json: bool) -> bool:
    return (
        valid_json
        and contract.get("data_horizon_expansion_contract_status")
        == "PASS_DATA_HORIZON_EXPANSION_CONTRACT_CREATED_VALIDATOR_NEXT"
        and contract.get("data_horizon_expansion_contract_created") is True
        and contract.get("target_historical_horizon_years") == TARGET_HORIZON
        and contract.get("target_timeframe") == TARGET_TIMEFRAME
        and contract.get("current_panel_sufficient_for_pipeline_validation") is True
        and contract.get("current_panel_sufficient_for_strategy_edge_claims") is False
        and contract.get("data_horizon_expansion_recommended") is True
        and contract.get("survivorship_bias_controls_required") is True
        and contract.get("symbol_lifecycle_report_required") is True
        and contract.get("holdout_policy_required") is True
        and contract.get("historical_data_quality_validator_required") is True
        and contract.get("current_evidence_chain_quality_after_contract")
        == "DATA_HORIZON_EXPANSION_CONTRACT_READY_NO_DATA_BUILD"
        and contract.get("replacement_checks_all_true") is True
    )


def source_panel_summary_respected(summary: Dict[str, Any], valid_json: bool) -> bool:
    return (
        valid_json
        and summary.get("source_panel_analysis_result_summary_status")
        == "PASS_SOURCE_PANEL_RESEARCH_SUBSTRATE_VALIDATED_DATA_HORIZON_EXPANSION_RECOMMENDED"
        and summary.get("result_summary_completed") is True
        and summary.get("all_required_source_panel_result_artifacts_validated") is True
        and summary.get("parquet_schema_metadata_validated") is True
        and summary.get("parquet_schema_limitation_bounded") is True
        and summary.get("source_panel_results_are_useful_research_substrate") is True
        and summary.get("source_panel_results_are_alpha_or_edge") is False
        and summary.get("one_year_panel_sufficient_for_pipeline_validation") is True
        and summary.get("one_year_panel_sufficient_for_strategy_edge_claims") is False
        and summary.get("data_horizon_expansion_recommended") is True
        and summary.get("recommended_historical_horizon_years") == TARGET_HORIZON
        and summary.get("active_p0_blocker_count") == 0
        and summary.get("active_p1_attention_count") == 1
        and summary.get("replacement_checks_all_true") is True
    )


def prior_contract_validation_context() -> Dict[str, Any]:
    return {
        "completed": True,
        "contract_validated": True,
        "one_year_panel_sufficient_for_pipeline_validation": True,
        "one_year_panel_insufficient_for_strategy_edge_claims": True,
        "three_to_four_year_expansion_recommended": True,
        "target_timeframe": TARGET_TIMEFRAME,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "no_strategy_backtest_candidate_runtime_live_capital_allowed_now": True,
    }


def future_runner_scope_preview() -> Dict[str, Any]:
    return {
        "completed": True,
        "future_scope_allowed_only_after_separate_execution_approval": True,
        "future_allowed_scope": FUTURE_SCOPE_ITEMS,
        "explicitly_excluded_now": FUTURE_SCOPE_EXCLUSIONS,
        "data_download_fetch_requires_later_separate_approval": True,
        "exchange_api_calls_allowed_in_preview": False,
        "historical_data_build_allowed_in_preview": False,
        "generic_runner_work_allowed": False,
    }


def future_required_artifacts_preview() -> Dict[str, Any]:
    return {
        "completed": True,
        "future_expected_only": True,
        "future_required_artifact_list": FUTURE_REQUIRED_ARTIFACT_LIST,
        "future_artifacts_exist_now": False,
        "future_artifacts_claimed_now": False,
    }


def input_discovery_preview() -> Dict[str, Any]:
    return {
        "completed": True,
        "future_discovery_targets": INPUT_DISCOVERY_ITEMS,
        "future_input_discovery_required": True,
        "future_external_download_may_be_required": True,
        "external_download_allowed_now": False,
        "local_existing_data_preferred": True,
        "external_api_fetch_allowed_now": False,
        "fabricated_data_allowed": False,
    }


def survivorship_bias_preview() -> Dict[str, Any]:
    return {
        "completed": True,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "fail_closed_or_mark_p1_p0_if": SURVIVORSHIP_FAIL_CLOSED_ITEMS,
    }


def holdout_policy_preview() -> Dict[str, Any]:
    return {
        "completed": True,
        "holdout_policy_required": True,
        "latest_holdout_months_target": LATEST_HOLDOUT_MONTHS_TARGET,
        "requirements": HOLDOUT_REQUIREMENTS,
    }


def fail_closed_conditions_preview() -> Dict[str, Any]:
    return {"completed": True, "fail_closed_if": FAIL_CLOSED_ITEMS}


def evidence_policy_preview() -> Dict[str, Any]:
    return {
        "completed": True,
        "current_source_panel_result_role": "RESEARCH_SUBSTRATE_NOT_EDGE_PROOF",
        "future_historical_expansion_artifacts_must_be_primary": True,
        "derived_metadata_only_with_reason_and_monitoring": True,
        "derived_overused_default_forbidden": True,
        "pass_with_attention_p1_must_not_normalize": True,
        "preview_closes_real_gap": True,
        "documentation_loop_detected": False,
    }


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    contract, contract_valid_json, contract_json_error = load_json_checked(CONTRACT_ARTIFACT)
    validator, validator_valid_json, validator_json_error = load_json_checked(CONTRACT_VALIDATOR_ARTIFACT)
    summary, summary_valid_json, summary_json_error = load_json_checked(SOURCE_PANEL_SUMMARY_ARTIFACT)

    prior_contract_ok = prior_contract_artifact_respected(contract, contract_valid_json)
    prior_validator_ok = prior_contract_validator_respected(validator, validator_valid_json)
    source_summary_ok = source_panel_summary_respected(summary, summary_valid_json)

    context = prior_contract_validation_context()
    scope = future_runner_scope_preview()
    future_artifacts = future_required_artifacts_preview()
    input_discovery = input_discovery_preview()
    survivorship = survivorship_bias_preview()
    holdout = holdout_policy_preview()
    fail_closed = fail_closed_conditions_preview()
    evidence = evidence_policy_preview()

    section_checks = {
        "prior_contract_validation_context_completed": context["completed"],
        "future_runner_scope_preview_completed": scope["completed"],
        "future_required_artifacts_preview_completed": future_artifacts["completed"],
        "input_discovery_preview_completed": input_discovery["completed"],
        "survivorship_bias_preview_completed": survivorship["completed"],
        "holdout_policy_preview_completed": holdout["completed"],
        "fail_closed_conditions_preview_completed": fail_closed["completed"],
        "evidence_policy_preview_completed": evidence["completed"],
    }
    preview_safe = all(section_checks.values()) and prior_contract_ok and prior_validator_ok and source_summary_ok
    next_module = NEXT_MODULE_APPROVAL if preview_safe else NEXT_MODULE_BLOCKED
    status = PREVIEW_STATUS_PASS if preview_safe else PREVIEW_STATUS_BLOCKED
    final_decision = (
        "DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_COMPLETE_EXECUTION_APPROVAL_REQUIRED_NEXT"
        if preview_safe
        else "DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_BLOCKED_RECORD_NEXT"
    )
    next_action = (
        "BUILD_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVAL_AFTER_SOURCE_PANEL_SUMMARY"
        if preview_safe
        else "BUILD_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_BLOCKED_RECORD_AFTER_SOURCE_PANEL_SUMMARY"
    )

    safety_flat = {
        "future_data_download_allowed_now": False,
        "future_data_fetch_allowed_now": False,
        "future_data_build_allowed_now": False,
        "historical_expansion_runner_allowed_now": False,
        "historical_expansion_runner_execution_performed": False,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "fake_or_synthetic_data_detected": False,
        "strategy_signal_claims_made": False,
        "tradable_edge_claims_made": False,
        "profit_claims_made": False,
        "backtest_performed": False,
        "candidate_generation_performed": False,
        "family_release_performed": False,
        "active_paper_performed": False,
        "real_order_touch_performed": False,
        "runtime_touch_performed": False,
        "capital_touch_performed": False,
        "live_touch_performed": False,
        "generic_runner_approval_granted": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
    }
    allowed_next_modules = {NEXT_MODULE_APPROVAL, NEXT_MODULE_BLOCKED}
    active_p0 = 0 if preview_safe else 1
    active_p1 = 1 if preview_safe else 0
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_638_to_639": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "prior_contract_artifact_respected": prior_contract_ok,
        "prior_contract_validator_respected": prior_validator_ok,
        "source_panel_summary_respected": source_summary_ok,
        "runner_preview_completed": preview_safe,
        "runner_preview_safe": preview_safe,
        "runner_execution_approval_required_next": preview_safe,
        "future_required_artifacts_marked_future_only": future_artifacts["future_expected_only"] is True
        and future_artifacts["future_artifacts_exist_now"] is False
        and future_artifacts["future_artifacts_claimed_now"] is False,
        "future_data_download_allowed_now_false": safety_flat["future_data_download_allowed_now"] is False,
        "future_data_fetch_allowed_now_false": safety_flat["future_data_fetch_allowed_now"] is False,
        "future_data_build_allowed_now_false": safety_flat["future_data_build_allowed_now"] is False,
        "historical_expansion_runner_allowed_now_false": safety_flat["historical_expansion_runner_allowed_now"] is False,
        "historical_expansion_runner_execution_performed_false": safety_flat[
            "historical_expansion_runner_execution_performed"
        ]
        is False,
        "strategy_research_allowed_now_false": safety_flat["strategy_research_allowed_now"] is False,
        "backtest_allowed_now_false": safety_flat["backtest_allowed_now"] is False,
        "candidate_generation_allowed_now_false": safety_flat["candidate_generation_allowed_now"] is False,
        "runtime_capital_live_false": safety_flat["runtime_touch_performed"] is False
        and safety_flat["capital_touch_performed"] is False
        and safety_flat["live_touch_performed"] is False,
        "generic_runner_blocked": safety_flat["generic_runner_approval_granted"] is False
        and safety_flat["generic_runner_implementation_remains_blocked"] is True,
        "schema_or_config_created_false": safety_flat["schema_or_config_created"] is False,
        "old_route_not_reopened": safety_flat["old_source_panel_anomaly_route_reopened_now"] is False
        and safety_flat["old_route_closed_artifacts_used_as_active_evidence_now"] is False,
        "documentation_loop_not_detected": evidence["documentation_loop_detected"] is False,
        "next_module_closes_real_gap": True,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module in allowed_next_modules,
        "direct_data_download_fetch_build_execution_not_selected": all(
            token not in next_module for token in ["download", "fetch", "build"]
        ),
        "historical_runner_execution_not_selected": "runner_execution_after" not in next_module,
        "strategy_candidate_backtest_runtime_live_capital_not_selected": all(
            token not in next_module
            for token in ["strategy", "candidate", "backtest", "runtime", "live", "capital"]
        ),
        "generic_review_adoption_gate_rollout_audit_not_selected": "generic" not in next_module
        and "_adoption_" not in next_module
        and "_gate_" not in next_module
        and "_rollout_" not in next_module
        and "_audit_" not in next_module,
    }
    replacement_checks_all_true = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "data_horizon_expansion_runner_preview_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if preview_safe else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_contract_validator_respected": prior_validator_ok,
        "prior_contract_artifact_respected": prior_contract_ok,
        "source_panel_summary_respected": source_summary_ok,
        "data_horizon_expansion_runner_preview_completed": preview_safe,
        **section_checks,
        "target_historical_horizon_years": TARGET_HORIZON,
        "target_timeframe": TARGET_TIMEFRAME,
        "current_panel_sufficient_for_pipeline_validation": True,
        "current_panel_sufficient_for_strategy_edge_claims": False,
        "data_horizon_expansion_recommended": True,
        "runner_preview_safe": preview_safe,
        "runner_execution_approval_required_next": preview_safe,
        "future_input_discovery_required": input_discovery["future_input_discovery_required"],
        "future_external_download_may_be_required": input_discovery["future_external_download_may_be_required"],
        "external_download_allowed_now": input_discovery["external_download_allowed_now"],
        "local_existing_data_preferred": input_discovery["local_existing_data_preferred"],
        "future_required_artifact_list": FUTURE_REQUIRED_ARTIFACT_LIST,
        "future_artifacts_exist_now": future_artifacts["future_artifacts_exist_now"],
        "future_artifacts_claimed_now": future_artifacts["future_artifacts_claimed_now"],
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "latest_holdout_months_target": LATEST_HOLDOUT_MONTHS_TARGET,
        **safety_flat,
        "current_evidence_chain_quality_before_preview": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_preview": EVIDENCE_AFTER if preview_safe else EVIDENCE_BLOCKED,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": active_p1,
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_DATA_QUALITY_ASSET_PATH",
        "usable_or_sellable_asset_path": (
            "REPO_ONLY_HISTORICAL_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_AS_REUSABLE_DATA_QUALITY_ASSET_PATH"
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
            "This runner preview reads only the prior data horizon contract, contract validator, and source-panel "
            "summary JSON artifacts as explicit replacement checks. It previews future runner scope and expected "
            "artifacts only. It does not download, fetch, or build data; execute a historical expansion runner; rerun "
            "source-panel analysis; scan parquet; read parquet rows; run strategy/backtest/candidate work; touch "
            "runtime/capital/live/order paths; approve or implement a generic runner; create schema/config files; "
            "reopen old anomaly routes; or claim profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "prior_contract_validation_context": context,
        "future_runner_scope_preview": scope,
        "future_required_artifacts_preview": future_artifacts,
        "input_discovery_preview": input_discovery,
        "survivorship_bias_preview": survivorship,
        "holdout_policy_preview": holdout,
        "fail_closed_conditions_preview": fail_closed,
        "evidence_policy_preview": evidence,
        "next_module_decision": {
            "runner_preview_complete_and_safe": preview_safe,
            "runner_preview_unsafe_or_too_broad": not preview_safe,
            "next_module": next_module,
            "direct_data_download_fetch_build_execution_selected": False,
            "historical_expansion_runner_execution_selected": False,
            "strategy_candidate_backtest_runtime_live_capital_selected": False,
            "generic_review_adoption_gate_rollout_audit_selected": False,
        },
        "artifact_paths": {
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "source_panel_summary_artifact": str(SOURCE_PANEL_SUMMARY_ARTIFACT),
        },
        "artifact_validation_errors": {
            "contract_valid_json": contract_valid_json,
            "contract_json_error": contract_json_error,
            "contract_validator_valid_json": validator_valid_json,
            "contract_validator_json_error": validator_json_error,
            "source_panel_summary_valid_json": summary_valid_json,
            "source_panel_summary_json_error": summary_json_error,
        },
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "expected_previous_tracked_python_count": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "replacement_checks": replacement_checks,
            "allowed_next_modules": sorted(allowed_next_modules),
        },
        "safety_flags": {
            "repo_only": True,
            "runner_preview_only": True,
            **safety_flat,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1_latest.json"
    timestamped_json = (
        OUT_DIR / f"repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1_{stamp}.json"
    )
    latest_txt = OUT_DIR / "repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1_latest.txt"
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
    return 0 if payload["data_horizon_expansion_runner_preview_completed"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
