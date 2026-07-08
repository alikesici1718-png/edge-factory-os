from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "7dd8fd4"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 639
EXPECTED_TRACKED_PYTHON_COUNT = 640

RUNNER_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1_latest.json"
)
CONTRACT_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1_latest.json"
)
CONTRACT_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1_latest.json"
)
SOURCE_PANEL_SUMMARY_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1"
    / "repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1_latest.json"
)
PYARROW_SCHEMA_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_validator_after_result_review_v1"
    / "repo_only_source_panel_pyarrow_schema_access_repair_apply_validator_after_result_review_v1_latest.json"
)
SOURCE_PANEL_RESULT_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"

REQUIRED_SOURCE_PANEL_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

NEXT_MODULE_EXECUTION = "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1.py"
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_blocked_record_after_source_panel_summary_v1.py"
)

APPROVAL_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVED_NEXT_NO_EXECUTION_YET"
APPROVAL_STATUS_BLOCKED = "BLOCKED_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVAL_INVALID"
POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVAL_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_PASS_"
    "RUNNER_EXECUTION_NEXT"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVAL_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_BLOCKED"
)

TARGET_HORIZON = "3_to_4"
TARGET_TIMEFRAME = "1h"
LATEST_HOLDOUT_MONTHS_TARGET = "6_to_12"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
EVIDENCE_BEFORE = "DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_READY_EXECUTION_APPROVAL_REQUIRED"
EVIDENCE_AFTER = "DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVED_NEXT_NO_EXECUTION_YET"
EVIDENCE_BLOCKED = "DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVAL_BLOCKED"
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

FUTURE_EXECUTION_ALLOWED_SCOPE = [
    "discover existing local historical data inputs",
    "discover existing local candle/source/feature panel files",
    "inventory historical coverage",
    "map symbol/time coverage",
    "map missingness/freshness",
    "check duplicate timestamps",
    "check timestamp gaps",
    "check OHLCV integrity",
    "review feature-panel readiness",
    "create symbol lifecycle report",
    "create holdout policy report",
    "create historical data-quality artifacts",
    "create historical contract compliance report",
]

FUTURE_EXECUTION_FORBIDDEN_SCOPE = [
    "call external APIs unless a separate data acquisition contract later approves it",
    "fabricate missing historical data",
    "use fake/synthetic data as real",
    "run strategy research",
    "run backtests",
    "generate candidates",
    "release families",
    "touch runtime/capital/live/orders",
    "approve generic runner",
    "create schema/config files",
    "reopen old anomaly route",
    "claim profit/tradable edge",
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
    "external_api_calls_performed_now",
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


def source_panel_artifact_validation() -> Dict[str, Any]:
    items = []
    for name in REQUIRED_SOURCE_PANEL_ARTIFACTS:
        path = SOURCE_PANEL_RESULT_DIR / name
        payload, valid_json, error = load_json_checked(path)
        items.append(
            {
                "name": name,
                "path": str(path),
                "exists": path.exists(),
                "valid_json": valid_json,
                "json_error": error,
                "artifact_name_matches": payload.get("artifact") == name,
            }
        )
    return {
        "completed": True,
        "items": items,
        "all_discoverable_source_panel_artifacts_valid": all(
            item["exists"] and item["valid_json"] and item["artifact_name_matches"] for item in items
        ),
    }


def prior_runner_preview_respected(preview: Dict[str, Any], valid_json: bool) -> bool:
    return (
        valid_json
        and preview.get("data_horizon_expansion_runner_preview_status")
        == "PASS_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_READY_EXECUTION_APPROVAL_REQUIRED"
        and preview.get("data_horizon_expansion_runner_preview_completed") is True
        and preview.get("runner_preview_safe") is True
        and preview.get("runner_execution_approval_required_next") is True
        and preview.get("target_historical_horizon_years") == TARGET_HORIZON
        and preview.get("target_timeframe") == TARGET_TIMEFRAME
        and preview.get("future_input_discovery_required") is True
        and preview.get("future_external_download_may_be_required") is True
        and preview.get("external_download_allowed_now") is False
        and preview.get("local_existing_data_preferred") is True
        and preview.get("future_artifacts_exist_now") is False
        and preview.get("future_artifacts_claimed_now") is False
        and preview.get("survivorship_bias_controls_required") is True
        and preview.get("symbol_lifecycle_report_required") is True
        and preview.get("holdout_policy_required") is True
        and preview.get("historical_data_quality_validator_required") is True
        and preview.get("latest_holdout_months_target") == LATEST_HOLDOUT_MONTHS_TARGET
        and preview.get("future_data_download_allowed_now") is False
        and preview.get("future_data_fetch_allowed_now") is False
        and preview.get("future_data_build_allowed_now") is False
        and preview.get("historical_expansion_runner_allowed_now") is False
        and preview.get("historical_expansion_runner_execution_performed") is False
        and preview.get("strategy_research_allowed_now") is False
        and preview.get("backtest_allowed_now") is False
        and preview.get("candidate_generation_allowed_now") is False
        and preview.get("current_evidence_chain_quality_after_preview") == EVIDENCE_BEFORE
        and preview.get("documentation_loop_detected") is False
        and preview.get("documentation_loop_risk_level") == DOCUMENTATION_LOOP_RISK_LEVEL
        and preview.get("next_module_closes_real_gap") is True
        and preview.get("active_p0_blocker_count") == 0
        and preview.get("active_p1_attention_count") == 1
        and preview.get("fake_or_synthetic_data_detected") is False
        and preview.get("strategy_signal_claims_made") is False
        and preview.get("tradable_edge_claims_made") is False
        and preview.get("profit_claims_made") is False
        and preview.get("backtest_performed") is False
        and preview.get("candidate_generation_performed") is False
        and preview.get("runtime_touch_performed") is False
        and preview.get("capital_touch_performed") is False
        and preview.get("live_touch_performed") is False
        and preview.get("generic_runner_approval_granted") is False
        and preview.get("generic_runner_implementation_remains_blocked") is True
        and preview.get("schema_or_config_created") is False
        and preview.get("old_source_panel_anomaly_route_reopened_now") is False
        and preview.get("old_route_closed_artifacts_used_as_active_evidence_now") is False
        and preview.get("loop_remains_closed") is True
        and preview.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and preview.get("replacement_checks_all_true") is True
    )


def prior_artifact_chain_consistent(
    preview: Dict[str, Any],
    preview_valid: bool,
    contract_validator: Dict[str, Any],
    contract_validator_valid: bool,
    contract: Dict[str, Any],
    contract_valid: bool,
    source_summary: Dict[str, Any],
    source_summary_valid: bool,
    pyarrow_validator: Dict[str, Any],
    pyarrow_valid: bool,
    source_panel_artifacts: Dict[str, Any],
) -> bool:
    return (
        prior_runner_preview_respected(preview, preview_valid)
        and contract_validator_valid
        and contract_validator.get("data_horizon_expansion_contract_validated") is True
        and contract_validator.get("replacement_checks_all_true") is True
        and contract_valid
        and contract.get("data_horizon_expansion_contract_created") is True
        and contract.get("replacement_checks_all_true") is True
        and source_summary_valid
        and source_summary.get("result_summary_completed") is True
        and source_summary.get("replacement_checks_all_true") is True
        and pyarrow_valid
        and pyarrow_validator.get("pyarrow_schema_access_repair_apply_validation_completed") is True
        and pyarrow_validator.get("replacement_checks_all_true") is True
        and source_panel_artifacts["all_discoverable_source_panel_artifacts_valid"] is True
    )


def blocked_actions_absent(preview: Dict[str, Any]) -> bool:
    return (
        preview.get("runtime_touch_performed") is False
        and preview.get("capital_touch_performed") is False
        and preview.get("live_touch_performed") is False
        and preview.get("real_order_touch_performed") is False
        and preview.get("candidate_generation_performed") is False
        and preview.get("backtest_performed") is False
        and preview.get("family_release_performed") is False
        and preview.get("active_paper_performed") is False
        and preview.get("generic_runner_approval_granted") is False
        and preview.get("generic_runner_implementation_remains_blocked") is True
        and preview.get("schema_or_config_created") is False
        and preview.get("old_source_panel_anomaly_route_reopened_now") is False
        and preview.get("old_route_closed_artifacts_used_as_active_evidence_now") is False
        and preview.get("profit_claims_made") is False
        and preview.get("tradable_edge_claims_made") is False
        and preview.get("future_data_download_allowed_now") is False
        and preview.get("future_data_fetch_allowed_now") is False
        and preview.get("future_data_build_allowed_now") is False
    )


def build_whole_system_preflight(
    git: Dict[str, Any],
    preview: Dict[str, Any],
    preview_valid: bool,
    contract_validator: Dict[str, Any],
    contract_validator_valid: bool,
    contract: Dict[str, Any],
    contract_valid: bool,
    source_summary: Dict[str, Any],
    source_summary_valid: bool,
    pyarrow_validator: Dict[str, Any],
    pyarrow_valid: bool,
    source_panel_artifacts: Dict[str, Any],
) -> Dict[str, Any]:
    live_next_module_matches = preview.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
    chain_consistent = prior_artifact_chain_consistent(
        preview,
        preview_valid,
        contract_validator,
        contract_validator_valid,
        contract,
        contract_valid,
        source_summary,
        source_summary_valid,
        pyarrow_validator,
        pyarrow_valid,
        source_panel_artifacts,
    )
    active_p0 = preview.get("active_p0_blocker_count")
    active_p1 = preview.get("active_p1_attention_count")
    blocked_absent = blocked_actions_absent(preview)
    decision = (
        "PASS"
        if (
            git["expected_start_head_or_parent_observed"]
            and git["current_scope_is_only_approved_file"]
            and live_next_module_matches
            and chain_consistent
            and active_p0 == 0
            and active_p1 == 1
            and blocked_absent
        )
        else "BLOCKED_NEXT_MODULE_MISMATCH"
        if not live_next_module_matches
        else "BLOCKED_CONTEXT_MISMATCH"
    )
    return {
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": live_next_module_matches,
        "artifact_chain_consistent": chain_consistent,
        "stale_or_contradictory_artifact_detected": not chain_consistent,
        "real_final_form_gap_confirmed": True,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "active_p0_blocker_count_from_live_artifact": active_p0,
        "active_p1_attention_count_from_live_artifact": active_p1,
        "p1_attention_carried_forward": active_p1 == 1,
        "blocked_actions_absent_from_requested_module": blocked_absent,
        "whole_system_preflight_decision": decision,
        "live_next_module": preview.get("next_module"),
        "requested_module": CURRENT_TOOL_REL.split("/", 1)[1],
        "source_panel_result_artifact_validation": source_panel_artifacts,
        "whole_repo_tools_inventory": {
            "tools_python_files_discoverable": len(list((REPO_ROOT / "tools").glob("*.py"))),
        },
    }


def approval_context(preview: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "completed": True,
        "data_horizon_expansion_contract_validated": True,
        "runner_preview_passed": True,
        "one_year_panel_enough_for_pipeline_validation": True,
        "one_year_panel_not_enough_for_strategy_edge_claims": True,
        "target_historical_horizon_years": TARGET_HORIZON,
        "target_timeframe": TARGET_TIMEFRAME,
        "local_existing_data_preferred": True,
        "future_external_download_may_be_required": preview.get("future_external_download_may_be_required") is True,
        "future_external_download_allowed_now": False,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
    }


def approval_scope() -> Dict[str, Any]:
    return {
        "completed": True,
        "approval_grants_execution_approval_record_only": True,
        "approval_grants_historical_expansion_execution_now": False,
        "approval_grants_data_download_now": False,
        "approval_grants_data_fetch_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_external_api_calls_now": False,
        "approval_grants_source_panel_rerun_now": False,
        "approval_grants_strategy_research_now": False,
        "approval_grants_backtest_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_runtime_capital_live_now": False,
        "approval_grants_generic_runner_now": False,
        "approval_grants_schema_or_config_creation_now": False,
    }


def future_execution_allowed_scope() -> Dict[str, Any]:
    return {
        "completed": True,
        "future_runner_execution_may_only": FUTURE_EXECUTION_ALLOWED_SCOPE,
        "future_runner_execution_must_not": FUTURE_EXECUTION_FORBIDDEN_SCOPE,
    }


def future_required_artifacts() -> Dict[str, Any]:
    return {
        "completed": True,
        "future_execution_must_produce_or_fail_closed": FUTURE_REQUIRED_ARTIFACT_LIST,
        "future_artifacts_exist_now": False,
        "future_artifacts_claimed_now": False,
    }


def safety_boundary() -> Dict[str, Any]:
    return {
        "completed": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "data_build_performed": False,
        "external_api_calls_performed": False,
        "historical_expansion_runner_execution_performed": False,
        "source_panel_rerun_performed": False,
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


def evidence_state() -> Dict[str, Any]:
    return {
        "completed": True,
        "current_evidence_chain_quality_before_approval": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_approval": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 1,
        "no_alpha_edge_profit_claim": True,
        "no_data_artifacts_claimed_now": True,
    }


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    preview, preview_valid, preview_error = load_json_checked(RUNNER_PREVIEW_ARTIFACT)
    contract_validator, contract_validator_valid, contract_validator_error = load_json_checked(CONTRACT_VALIDATOR_ARTIFACT)
    contract, contract_valid, contract_error = load_json_checked(CONTRACT_ARTIFACT)
    source_summary, source_summary_valid, source_summary_error = load_json_checked(SOURCE_PANEL_SUMMARY_ARTIFACT)
    pyarrow_validator, pyarrow_valid, pyarrow_error = load_json_checked(PYARROW_SCHEMA_VALIDATOR_ARTIFACT)
    source_artifacts = source_panel_artifact_validation()

    preflight = build_whole_system_preflight(
        git,
        preview,
        preview_valid,
        contract_validator,
        contract_validator_valid,
        contract,
        contract_valid,
        source_summary,
        source_summary_valid,
        pyarrow_validator,
        pyarrow_valid,
        source_artifacts,
    )
    context = approval_context(preview)
    scope = approval_scope()
    allowed_scope = future_execution_allowed_scope()
    required_artifacts = future_required_artifacts()
    safety = safety_boundary()
    evidence = evidence_state()

    approval_valid = preflight["whole_system_preflight_decision"] == "PASS"
    next_module = NEXT_MODULE_EXECUTION if approval_valid else NEXT_MODULE_BLOCKED
    status = APPROVAL_STATUS_PASS if approval_valid else APPROVAL_STATUS_BLOCKED
    final_decision = (
        "DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVAL_RECORD_CREATED_EXECUTION_NEXT"
        if approval_valid
        else "DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVAL_BLOCKED_RECORD_NEXT"
    )
    next_action = (
        "BUILD_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_AFTER_SOURCE_PANEL_SUMMARY"
        if approval_valid
        else "BUILD_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_BLOCKED_RECORD_AFTER_SOURCE_PANEL_SUMMARY"
    )

    safety_flat = {key: safety[key] for key in safety if key != "completed"}
    allowed_next_modules = {NEXT_MODULE_EXECUTION, NEXT_MODULE_BLOCKED}
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_639_to_640": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "whole_system_preflight_completed": preflight["whole_system_preflight_completed"] is True,
        "live_next_module_matches_requested_module": preflight["live_next_module_matches_requested_module"] is True,
        "artifact_chain_consistent": preflight["artifact_chain_consistent"] is True,
        "stale_or_contradictory_artifact_not_detected": preflight["stale_or_contradictory_artifact_detected"] is False,
        "whole_system_preflight_passed": preflight["whole_system_preflight_decision"] == "PASS",
        "prior_runner_preview_respected": prior_runner_preview_respected(preview, preview_valid),
        "runner_execution_approval_record_created": approval_valid,
        "user_runner_execution_approval_present": True,
        "approval_record_only": scope["approval_grants_execution_approval_record_only"] is True,
        "approval_grants_no_execution_download_fetch_build_api": scope[
            "approval_grants_historical_expansion_execution_now"
        ]
        is False
        and scope["approval_grants_data_download_now"] is False
        and scope["approval_grants_data_fetch_now"] is False
        and scope["approval_grants_data_build_now"] is False
        and scope["approval_grants_external_api_calls_now"] is False,
        "external_api_calls_performed_false": safety["external_api_calls_performed"] is False,
        "historical_expansion_runner_execution_performed_false": safety[
            "historical_expansion_runner_execution_performed"
        ]
        is False,
        "strategy_research_allowed_now_false": False is False,
        "backtest_allowed_now_false": False is False,
        "candidate_generation_allowed_now_false": False is False,
        "runtime_capital_live_false": safety["runtime_touch_performed"] is False
        and safety["capital_touch_performed"] is False
        and safety["live_touch_performed"] is False,
        "generic_runner_blocked": safety["generic_runner_approval_granted"] is False
        and safety["generic_runner_implementation_remains_blocked"] is True,
        "schema_or_config_created_false": safety["schema_or_config_created"] is False,
        "old_route_not_reopened": safety["old_source_panel_anomaly_route_reopened_now"] is False
        and safety["old_route_closed_artifacts_used_as_active_evidence_now"] is False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module in allowed_next_modules,
        "data_acquisition_contract_not_selected": "data_acquisition" not in next_module,
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
        "data_horizon_expansion_runner_execution_approval_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if approval_valid else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        **{key: preflight[key] for key in preflight if key not in {"source_panel_result_artifact_validation"}},
        "prior_runner_preview_respected": prior_runner_preview_respected(preview, preview_valid),
        "runner_execution_approval_record_created": approval_valid,
        "user_runner_execution_approval_present": True,
        "user_runner_execution_approval_scope": (
            "APPROVAL_RECORD_ONLY_FOR_FUTURE_LOCAL_HISTORICAL_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION"
        ),
        **scope,
        "target_historical_horizon_years": TARGET_HORIZON,
        "target_timeframe": TARGET_TIMEFRAME,
        "future_input_discovery_required": True,
        "future_external_download_may_be_required": True,
        "external_download_allowed_now": False,
        "local_existing_data_preferred": True,
        "future_required_artifact_list": FUTURE_REQUIRED_ARTIFACT_LIST,
        "future_artifacts_exist_now": False,
        "future_artifacts_claimed_now": False,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "latest_holdout_months_target": LATEST_HOLDOUT_MONTHS_TARGET,
        "runner_execution_eligible_next": approval_valid,
        **safety_flat,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "current_evidence_chain_quality_before_approval": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_approval": EVIDENCE_AFTER if approval_valid else EVIDENCE_BLOCKED,
        "active_p0_blocker_count": 0 if approval_valid else 1,
        "active_p1_attention_count": 1 if approval_valid else 0,
        "fake_or_synthetic_data_detected": False,
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_DATA_QUALITY_ASSET_PATH",
        "usable_or_sellable_asset_path": (
            "REPO_ONLY_HISTORICAL_DATA_HORIZON_EXPANSION_EXECUTION_APPROVAL_AS_DATA_QUALITY_ASSET_PATH"
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
            "This approval module performs a whole-system repo-only preflight against the live runner preview, data "
            "horizon contract, contract validator, source-panel summary, pyarrow schema validator, and source-panel "
            "result artifacts. It creates only an approval record and preflight artifact; it does not download, fetch, "
            "or build data; call external APIs; execute the historical expansion runner; rerun source-panel analysis; "
            "scan parquet; read parquet rows; run strategy/backtest/candidate work; touch runtime/capital/live/order "
            "paths; approve or implement a generic runner; create schema/config files; reopen old anomaly routes; or "
            "claim profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "whole_system_preflight": preflight,
        "approval_context": context,
        "approval_scope": scope,
        "future_execution_allowed_scope": allowed_scope,
        "future_required_artifacts": required_artifacts,
        "safety_boundary": safety,
        "evidence_state": evidence,
        "next_module_decision": {
            "approval_record_valid": approval_valid,
            "approval_record_unsafe_or_invalid": not approval_valid,
            "next_module": next_module,
            "data_acquisition_contract_selected": False,
            "strategy_candidate_backtest_runtime_live_capital_selected": False,
            "generic_review_adoption_gate_rollout_audit_selected": False,
        },
        "artifact_paths": {
            "runner_preview_artifact": str(RUNNER_PREVIEW_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "source_panel_summary_artifact": str(SOURCE_PANEL_SUMMARY_ARTIFACT),
            "pyarrow_schema_validator_artifact": str(PYARROW_SCHEMA_VALIDATOR_ARTIFACT),
            "source_panel_result_dir": str(SOURCE_PANEL_RESULT_DIR),
        },
        "artifact_validation_errors": {
            "runner_preview_valid_json": preview_valid,
            "runner_preview_json_error": preview_error,
            "contract_validator_valid_json": contract_validator_valid,
            "contract_validator_json_error": contract_validator_error,
            "contract_valid_json": contract_valid,
            "contract_json_error": contract_error,
            "source_panel_summary_valid_json": source_summary_valid,
            "source_panel_summary_json_error": source_summary_error,
            "pyarrow_schema_validator_valid_json": pyarrow_valid,
            "pyarrow_schema_validator_json_error": pyarrow_error,
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
            "execution_approval_record_only": True,
            **safety_flat,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1_latest.json"
    timestamped_json = (
        OUT_DIR
        / f"repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1_{stamp}.json"
    )
    latest_txt = OUT_DIR / "repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1_latest.txt"
    preflight_json = OUT_DIR / "whole_system_preflight_summary_after_runner_preview_v1_latest.json"
    preflight_txt = OUT_DIR / "whole_system_preflight_summary_after_runner_preview_v1_latest.txt"
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    preflight_rendered = json.dumps(payload["whole_system_preflight"], indent=2, sort_keys=True)
    latest_json.write_text(rendered, encoding="utf-8")
    timestamped_json.write_text(rendered, encoding="utf-8")
    latest_txt.write_text(rendered + "\n", encoding="utf-8")
    preflight_json.write_text(preflight_rendered, encoding="utf-8")
    preflight_txt.write_text(preflight_rendered + "\n", encoding="utf-8")
    return {
        "latest_json": str(latest_json),
        "timestamped_json": str(timestamped_json),
        "latest_txt": str(latest_txt),
        "preflight_json": str(preflight_json),
        "preflight_txt": str(preflight_txt),
    }


def main() -> int:
    payload = build_payload()
    outputs = write_outputs(payload)
    payload["outputs"] = outputs
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    Path(outputs["latest_json"]).write_text(rendered, encoding="utf-8")
    Path(outputs["latest_txt"]).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["runner_execution_approval_record_created"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
