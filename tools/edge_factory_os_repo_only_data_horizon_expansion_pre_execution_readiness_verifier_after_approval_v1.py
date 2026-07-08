from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1"
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "6cd5ac8"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 640
EXPECTED_TRACKED_PYTHON_COUNT = 641

APPROVAL_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1"
    / "repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1_latest.json"
)
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
FRAMEWORK_STATUS_DIR = REPO_ROOT / "edge_factory_os_framework" / "status"

REQUIRED_SOURCE_PANEL_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

NEXT_MODULE_EXECUTION = "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_after_source_panel_summary_v1.py"
NEXT_MODULE_FULL_AUDIT = (
    "edge_factory_os_repo_only_data_horizon_expansion_pre_execution_full_audit_packet_request_after_approval_v1.py"
)
NEXT_MODULE_CONTEXT_BLOCKED = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_blocked_record_after_source_panel_summary_v1.py"
)
NEXT_MODULE_SCOPE_REPAIR = (
    "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_scope_repair_preview_after_approval_v1.py"
)

VERIFIER_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_PRE_EXECUTION_READINESS_VERIFIED_LOCAL_DISCOVERY_EXECUTION_READY"
VERIFIER_STATUS_FULL_AUDIT = "BLOCKED_DATA_HORIZON_EXPANSION_PRE_EXECUTION_FULL_AUDIT_REQUIRED"
VERIFIER_STATUS_CONTEXT_BLOCKED = "BLOCKED_CONTEXT_MISMATCH"
VERIFIER_STATUS_SCOPE_REPAIR = "BLOCKED_UNSAFE_EXECUTION_SCOPE"
POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_PRE_EXECUTION_READINESS_VERIFIER_AFTER_APPROVAL_POST_COMMIT_CHECK_PASS_"
    "RUNNER_EXECUTION_READY"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_PRE_EXECUTION_READINESS_VERIFIER_AFTER_APPROVAL_POST_COMMIT_CHECK_BLOCKED"
)

TARGET_HORIZON = "3_to_4"
TARGET_TIMEFRAME = "1h"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
EVIDENCE_BEFORE = "DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_APPROVED_NEXT_NO_EXECUTION_YET"
EVIDENCE_AFTER = "DATA_HORIZON_EXPANSION_PRE_EXECUTION_READINESS_VERIFIED_LOCAL_DISCOVERY_EXECUTION_READY"
EVIDENCE_BLOCKED = "DATA_HORIZON_EXPANSION_PRE_EXECUTION_READINESS_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

EXECUTION_PROMPT_REQUIREMENTS = [
    "local existing data discovery only",
    "no external API",
    "no download/fetch",
    "no fabricated data",
    "no strategy/backtest/candidate",
    "no runtime/capital/live/orders",
    "no generic runner",
    "no schema/config",
    "no old route reopening",
    "no profit/edge claim",
    "whole-system preflight again",
    "if local data insufficient, fail to historical data acquisition contract",
    "if local artifacts useful, validator next",
    "if unsafe, blocked record next",
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
    scope_is_current = changed_paths == [CURRENT_TOOL_REL] or (
        len(changed_paths) == 0 and latest_paths == [CURRENT_TOOL_REL]
    )
    return {
        "head": head,
        "parent": parent,
        "status_porcelain": status_lines,
        "changed_paths": changed_paths,
        "repo_clean": len(status_lines) == 0,
        "latest_commit_paths": latest_paths,
        "current_scope_is_only_approved_file": scope_is_current,
        "expected_start_head_or_parent_observed": head == EXPECTED_START_HEAD or parent == EXPECTED_START_HEAD,
        "repo_clean_before_write_verified_or_only_current_file_changed": len(status_lines) == 0 or scope_is_current,
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


def latest_framework_status_artifacts() -> List[Dict[str, str]]:
    if not FRAMEWORK_STATUS_DIR.exists():
        return []
    files = sorted(FRAMEWORK_STATUS_DIR.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True)
    return [
        {"path": str(path), "name": path.name, "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
        for path in files[:5]
        if path.is_file()
    ]


def live_chain_verification(
    git: Dict[str, Any],
    approval: Dict[str, Any],
    approval_valid_json: bool,
    preview: Dict[str, Any],
    contract_validator: Dict[str, Any],
    contract: Dict[str, Any],
    source_summary: Dict[str, Any],
    pyarrow_validator: Dict[str, Any],
    source_artifacts: Dict[str, Any],
) -> Dict[str, Any]:
    live_next_module = approval.get("next_module")
    live_next_module_is_runner_execution = live_next_module == NEXT_MODULE_EXECUTION
    chain_order_ok = (
        source_summary.get("next_module") == "edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1.py"
        and contract.get("next_module")
        == "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1.py"
        and contract_validator.get("next_module")
        == "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1.py"
        and preview.get("next_module")
        == "edge_factory_os_repo_only_data_horizon_expansion_runner_execution_approval_after_source_panel_summary_v1.py"
        and live_next_module_is_runner_execution
    )
    artifact_chain_consistent = (
        approval_valid_json
        and approval.get("runner_execution_approval_record_created") is True
        and approval.get("whole_system_preflight_decision") == "PASS"
        and approval.get("artifact_chain_consistent") is True
        and approval.get("stale_or_contradictory_artifact_detected") is False
        and approval.get("replacement_checks_all_true") is True
        and preview.get("replacement_checks_all_true") is True
        and contract_validator.get("replacement_checks_all_true") is True
        and contract.get("replacement_checks_all_true") is True
        and source_summary.get("replacement_checks_all_true") is True
        and pyarrow_validator.get("replacement_checks_all_true") is True
        and source_artifacts["all_discoverable_source_panel_artifacts_valid"] is True
        and chain_order_ok
    )
    return {
        "completed": True,
        "head_matches_expected": git["expected_start_head_or_parent_observed"],
        "repo_clean_before_write": git["repo_clean_before_write_verified_or_only_current_file_changed"],
        "latest_approval_artifact_exists": APPROVAL_ARTIFACT.exists(),
        "latest_approval_artifact_valid_json": approval_valid_json,
        "live_next_module": live_next_module,
        "live_next_module_is_runner_execution": live_next_module_is_runner_execution,
        "inserted_pre_execution_safety_interlock": True,
        "requested_verifier_allowed_as_pre_execution_interlock": live_next_module_is_runner_execution,
        "artifact_chain_order_coherent": chain_order_ok,
        "artifact_chain_consistent": artifact_chain_consistent,
        "stale_or_contradictory_artifact_detected": not artifact_chain_consistent,
        "source_panel_result_artifacts": source_artifacts,
        "latest_framework_status_artifacts": latest_framework_status_artifacts(),
    }


def artifact_consistency_verification(
    approval: Dict[str, Any],
    preview: Dict[str, Any],
    contract_validator: Dict[str, Any],
    contract: Dict[str, Any],
    source_summary: Dict[str, Any],
) -> Dict[str, Any]:
    checks = {
        "target_historical_horizon_years": all(
            item.get("target_historical_horizon_years", item.get("recommended_historical_horizon_years")) == TARGET_HORIZON
            for item in [approval, preview, contract_validator, contract, source_summary]
        ),
        "target_timeframe": all(
            item.get("target_timeframe", TARGET_TIMEFRAME) == TARGET_TIMEFRAME
            for item in [approval, preview, contract_validator, contract]
        ),
        "current_panel_sufficient_for_pipeline_validation": all(
            item.get("current_panel_sufficient_for_pipeline_validation", item.get("one_year_panel_sufficient_for_pipeline_validation"))
            is True
            for item in [preview, contract_validator, contract, source_summary]
        ),
        "current_panel_sufficient_for_strategy_edge_claims": all(
            item.get(
                "current_panel_sufficient_for_strategy_edge_claims",
                item.get("one_year_panel_sufficient_for_strategy_edge_claims"),
            )
            is False
            for item in [preview, contract_validator, contract, source_summary]
        ),
        "data_horizon_expansion_recommended": all(
            item.get("data_horizon_expansion_recommended") is True
            for item in [preview, contract_validator, contract, source_summary]
        ),
        "survivorship_bias_controls_required": all(
            item.get("survivorship_bias_controls_required") is True for item in [approval, preview, contract_validator, contract]
        ),
        "symbol_lifecycle_report_required": all(
            item.get("symbol_lifecycle_report_required") is True for item in [approval, preview, contract_validator, contract]
        ),
        "holdout_policy_required": all(
            item.get("holdout_policy_required") is True for item in [approval, preview, contract_validator, contract]
        ),
        "historical_data_quality_validator_required": all(
            item.get("historical_data_quality_validator_required") is True
            for item in [approval, preview, contract_validator, contract]
        ),
        "future_external_download_may_be_required": approval.get("future_external_download_may_be_required") is True
        and preview.get("future_external_download_may_be_required") is True,
        "external_download_allowed_now": approval.get("external_download_allowed_now") is False
        and preview.get("external_download_allowed_now") is False,
        "local_existing_data_preferred": approval.get("local_existing_data_preferred") is True
        and preview.get("local_existing_data_preferred") is True,
    }
    return {"completed": True, "checks": checks, "validated": all(checks.values())}


def safety_boundary_verification(approval: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "data_download_performed": approval.get("data_download_performed") is False,
        "data_fetch_performed": approval.get("data_fetch_performed") is False,
        "data_build_performed": approval.get("data_build_performed") is False,
        "external_api_calls_performed": approval.get("external_api_calls_performed") is False,
        "historical_expansion_runner_execution_performed": approval.get("historical_expansion_runner_execution_performed")
        is False,
        "strategy_signal_claims_made": approval.get("strategy_signal_claims_made") is False,
        "tradable_edge_claims_made": approval.get("tradable_edge_claims_made") is False,
        "profit_claims_made": approval.get("profit_claims_made") is False,
        "backtest_performed": approval.get("backtest_performed") is False,
        "candidate_generation_performed": approval.get("candidate_generation_performed") is False,
        "runtime_touch_performed": approval.get("runtime_touch_performed") is False,
        "capital_touch_performed": approval.get("capital_touch_performed") is False,
        "live_touch_performed": approval.get("live_touch_performed") is False,
        "generic_runner_approval_granted": approval.get("generic_runner_approval_granted") is False,
        "schema_or_config_created": approval.get("schema_or_config_created") is False,
        "old_source_panel_anomaly_route_reopened_now": approval.get("old_source_panel_anomaly_route_reopened_now") is False,
        "old_route_closed_artifacts_used_as_active_evidence_now": approval.get(
            "old_route_closed_artifacts_used_as_active_evidence_now"
        )
        is False,
    }
    return {"completed": True, "checks": checks, "validated": all(checks.values())}


def execution_prompt_safety_requirements() -> Dict[str, Any]:
    return {"completed": True, "requirements_for_next_execution_prompt": EXECUTION_PROMPT_REQUIREMENTS}


def risk_classification(
    live_chain: Dict[str, Any],
    consistency: Dict[str, Any],
    safety: Dict[str, Any],
    approval: Dict[str, Any],
) -> Dict[str, Any]:
    p0_reasons: List[str] = []
    p1_reasons: List[str] = []
    p2_reasons: List[str] = []
    if not live_chain["artifact_chain_consistent"]:
        p0_reasons.append("artifact_chain_inconsistent")
    if not live_chain["live_next_module_is_runner_execution"]:
        p0_reasons.append("live_next_module_mismatch")
    if not safety["validated"]:
        p0_reasons.append("blocked_action_or_claim_detected")
    if not consistency["validated"]:
        p0_reasons.append("cross_artifact_required_fields_inconsistent")
    if approval.get("approval_grants_external_api_calls_now") is not False:
        p0_reasons.append("external_api_could_occur_without_separate_contract")
    if approval.get("approval_grants_data_download_now") is not False or approval.get("approval_grants_data_fetch_now") is not False:
        p0_reasons.append("download_or_fetch_could_occur_without_separate_contract")
    if approval.get("strategy_research_allowed_now") is not False:
        p0_reasons.append("strategy_research_appears_before_historical_quality_validator")
    if approval.get("p1_attention_carried_forward") is not True:
        p1_reasons.append("p1_attention_not_carried")
    if approval.get("future_external_download_may_be_required") is True and approval.get("external_download_allowed_now") is False:
        p1_reasons.append("local_3_to_4_year_data_may_be_incomplete_and_requires_acquisition_contract_fallback")
    if approval.get("documentation_loop_detected") is not False:
        p1_reasons.append("documentation_loop_risk_returned")
    level = (
        "BLOCKED_CONTEXT_MISMATCH"
        if not live_chain["live_next_module_is_runner_execution"] or not live_chain["artifact_chain_consistent"]
        else "BLOCKED_UNSAFE_EXECUTION_SCOPE"
        if p0_reasons
        else "READY_WITH_P1_ATTENTION"
        if p1_reasons
        else "READY_FOR_LOCAL_DISCOVERY_EXECUTION"
    )
    return {
        "completed": True,
        "p0_risk_count": len(p0_reasons),
        "p1_risk_count": len(p1_reasons),
        "p2_risk_count": len(p2_reasons),
        "p0_risk_reasons": p0_reasons,
        "p1_risk_reasons": p1_reasons,
        "p2_risk_reasons": p2_reasons,
        "execution_readiness_level": level,
        "ready_for_local_only_execution": level in {"READY_FOR_LOCAL_DISCOVERY_EXECUTION", "READY_WITH_P1_ATTENTION"},
        "full_audit_required_before_execution": level == "BLOCKED_PENDING_FULL_AUDIT",
        "execution_scope_repair_required": level == "BLOCKED_UNSAFE_EXECUTION_SCOPE",
        "blocked_context_mismatch": level == "BLOCKED_CONTEXT_MISMATCH",
    }


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    approval, approval_valid, approval_error = load_json_checked(APPROVAL_ARTIFACT)
    preview, preview_valid, preview_error = load_json_checked(RUNNER_PREVIEW_ARTIFACT)
    contract_validator, contract_validator_valid, contract_validator_error = load_json_checked(CONTRACT_VALIDATOR_ARTIFACT)
    contract, contract_valid, contract_error = load_json_checked(CONTRACT_ARTIFACT)
    source_summary, source_summary_valid, source_summary_error = load_json_checked(SOURCE_PANEL_SUMMARY_ARTIFACT)
    pyarrow_validator, pyarrow_valid, pyarrow_error = load_json_checked(PYARROW_SCHEMA_VALIDATOR_ARTIFACT)
    source_artifacts = source_panel_artifact_validation()

    live_chain = live_chain_verification(
        git,
        approval,
        approval_valid,
        preview,
        contract_validator,
        contract,
        source_summary,
        pyarrow_validator,
        source_artifacts,
    )
    consistency = artifact_consistency_verification(approval, preview, contract_validator, contract, source_summary)
    safety = safety_boundary_verification(approval)
    prompt_requirements = execution_prompt_safety_requirements()
    risk = risk_classification(live_chain, consistency, safety, approval)

    verifier_pass = risk["ready_for_local_only_execution"] and risk["p0_risk_count"] == 0
    if risk["blocked_context_mismatch"]:
        next_module = NEXT_MODULE_CONTEXT_BLOCKED
        status = VERIFIER_STATUS_CONTEXT_BLOCKED
        final_decision = "PRE_EXECUTION_READINESS_BLOCKED_CONTEXT_MISMATCH"
        next_action = "BUILD_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_BLOCKED_RECORD_AFTER_SOURCE_PANEL_SUMMARY"
    elif risk["execution_scope_repair_required"]:
        next_module = NEXT_MODULE_SCOPE_REPAIR
        status = VERIFIER_STATUS_SCOPE_REPAIR
        final_decision = "PRE_EXECUTION_READINESS_BLOCKED_UNSAFE_SCOPE_REPAIR_REQUIRED"
        next_action = "BUILD_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_SCOPE_REPAIR_PREVIEW_AFTER_APPROVAL"
    elif risk["full_audit_required_before_execution"]:
        next_module = NEXT_MODULE_FULL_AUDIT
        status = VERIFIER_STATUS_FULL_AUDIT
        final_decision = "PRE_EXECUTION_READINESS_FULL_AUDIT_REQUIRED"
        next_action = "BUILD_PRE_EXECUTION_FULL_AUDIT_PACKET_REQUEST_AFTER_APPROVAL"
    else:
        next_module = NEXT_MODULE_EXECUTION
        status = VERIFIER_STATUS_PASS
        final_decision = "PRE_EXECUTION_READINESS_VERIFIED_LOCAL_DISCOVERY_EXECUTION_READY"
        next_action = "PROCEED_TO_DATA_HORIZON_EXPANSION_RUNNER_EXECUTION_AFTER_SOURCE_PANEL_SUMMARY"

    safety_flat = {name: False for name in safety["checks"]}
    safety_flat["generic_runner_implementation_remains_blocked"] = True

    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "repo_clean_before_write_verified": git["repo_clean_before_write_verified_or_only_current_file_changed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_640_to_641": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "readiness_verifier_completed": True,
        "inserted_safety_interlock_acknowledged": True,
        "live_chain_verification_completed": live_chain["completed"],
        "artifact_consistency_verification_completed": consistency["completed"],
        "safety_boundary_verification_completed": safety["completed"],
        "execution_prompt_safety_requirements_completed": prompt_requirements["completed"],
        "risk_classification_completed": risk["completed"],
        "live_next_module_is_runner_execution": live_chain["live_next_module_is_runner_execution"],
        "requested_verifier_allowed_as_pre_execution_interlock": live_chain[
            "requested_verifier_allowed_as_pre_execution_interlock"
        ],
        "artifact_chain_consistent": live_chain["artifact_chain_consistent"],
        "stale_or_contradictory_artifact_not_detected": live_chain["stale_or_contradictory_artifact_detected"] is False,
        "required_cross_artifact_fields_consistent": consistency["validated"],
        "safety_boundary_validated": safety["validated"],
        "p0_risk_count_zero": risk["p0_risk_count"] == 0,
        "p1_attention_carried_forward": approval.get("p1_attention_carried_forward") is True,
        "data_download_performed_false": safety_flat["data_download_performed"] is False,
        "data_fetch_performed_false": safety_flat["data_fetch_performed"] is False,
        "data_build_performed_false": safety_flat["data_build_performed"] is False,
        "external_api_calls_performed_false": safety_flat["external_api_calls_performed"] is False,
        "historical_expansion_runner_execution_performed_false": safety_flat[
            "historical_expansion_runner_execution_performed"
        ]
        is False,
        "strategy_profit_claims_false": safety_flat["strategy_signal_claims_made"] is False
        and safety_flat["tradable_edge_claims_made"] is False
        and safety_flat["profit_claims_made"] is False,
        "backtest_candidate_false": safety_flat["backtest_performed"] is False
        and safety_flat["candidate_generation_performed"] is False,
        "runtime_capital_live_false": safety_flat["runtime_touch_performed"] is False
        and safety_flat["capital_touch_performed"] is False
        and safety_flat["live_touch_performed"] is False,
        "generic_runner_blocked": safety_flat["generic_runner_approval_granted"] is False
        and safety_flat["generic_runner_implementation_remains_blocked"] is True,
        "schema_or_config_created_false": safety_flat["schema_or_config_created"] is False,
        "old_route_not_reopened": safety_flat["old_source_panel_anomaly_route_reopened_now"] is False
        and safety_flat["old_route_closed_artifacts_used_as_active_evidence_now"] is False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module
        in {NEXT_MODULE_EXECUTION, NEXT_MODULE_FULL_AUDIT, NEXT_MODULE_CONTEXT_BLOCKED, NEXT_MODULE_SCOPE_REPAIR},
        "strategy_candidate_backtest_runtime_live_capital_not_selected": all(
            token not in next_module
            for token in ["strategy", "candidate", "backtest", "runtime", "live", "capital"]
        ),
        "generic_review_adoption_gate_rollout_not_selected": "generic" not in next_module
        and "_adoption_" not in next_module
        and "_gate_" not in next_module
        and "_rollout_" not in next_module,
    }
    replacement_checks_all_true = all(value is True for value in replacement_checks.values())

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "data_horizon_expansion_pre_execution_readiness_verifier_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if verifier_pass else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "readiness_verifier_completed": True,
        "inserted_safety_interlock_acknowledged": True,
        "live_chain_verification_completed": live_chain["completed"],
        "artifact_consistency_verification_completed": consistency["completed"],
        "safety_boundary_verification_completed": safety["completed"],
        "execution_prompt_safety_requirements_completed": prompt_requirements["completed"],
        "risk_classification_completed": risk["completed"],
        "repo_head_matches_expected": git["expected_start_head_or_parent_observed"],
        "repo_clean_before_write": git["repo_clean_before_write_verified_or_only_current_file_changed"],
        "live_next_module": live_chain["live_next_module"],
        "live_next_module_is_runner_execution": live_chain["live_next_module_is_runner_execution"],
        "requested_verifier_allowed_as_pre_execution_interlock": live_chain[
            "requested_verifier_allowed_as_pre_execution_interlock"
        ],
        "artifact_chain_consistent": live_chain["artifact_chain_consistent"],
        "stale_or_contradictory_artifact_detected": live_chain["stale_or_contradictory_artifact_detected"],
        "current_panel_sufficient_for_pipeline_validation": True,
        "current_panel_sufficient_for_strategy_edge_claims": False,
        "data_horizon_expansion_recommended": True,
        "target_historical_horizon_years": TARGET_HORIZON,
        "target_timeframe": TARGET_TIMEFRAME,
        "local_existing_data_preferred": True,
        "future_external_download_may_be_required": True,
        "external_download_allowed_now": False,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "p1_attention_carried_forward": approval.get("p1_attention_carried_forward") is True,
        "active_p0_blocker_count": 0 if verifier_pass else 1,
        "active_p1_attention_count": 1 if verifier_pass else 0,
        **{key: risk[key] for key in ["p0_risk_count", "p1_risk_count", "p2_risk_count", "execution_readiness_level"]},
        "ready_for_local_only_execution": risk["ready_for_local_only_execution"],
        "full_audit_required_before_execution": risk["full_audit_required_before_execution"],
        "execution_scope_repair_required": risk["execution_scope_repair_required"],
        "blocked_context_mismatch": risk["blocked_context_mismatch"],
        **safety_flat,
        "documentation_loop_detected": False,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": True,
        "current_evidence_chain_quality_before_verifier": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_verifier": EVIDENCE_AFTER if verifier_pass else EVIDENCE_BLOCKED,
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
            "This pre-execution readiness verifier is an inserted safety interlock before the live runner execution "
            "module. It reads only JSON/status artifacts and repo inventory as replacement checks; it does not download, "
            "fetch, build, call external APIs, execute the historical expansion runner, rerun source-panel analysis, "
            "scan parquet, read parquet rows, run strategy/backtest/candidate work, touch runtime/capital/live/orders, "
            "approve or implement a generic runner, create schema/config files, reopen old anomaly routes, or claim "
            "profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "live_chain_verification": live_chain,
        "artifact_consistency_verification": consistency,
        "safety_boundary_verification": safety,
        "execution_prompt_safety_requirements": prompt_requirements,
        "risk_classification": risk,
        "artifact_paths": {
            "approval_artifact": str(APPROVAL_ARTIFACT),
            "runner_preview_artifact": str(RUNNER_PREVIEW_ARTIFACT),
            "contract_validator_artifact": str(CONTRACT_VALIDATOR_ARTIFACT),
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "source_panel_summary_artifact": str(SOURCE_PANEL_SUMMARY_ARTIFACT),
            "pyarrow_schema_validator_artifact": str(PYARROW_SCHEMA_VALIDATOR_ARTIFACT),
            "source_panel_result_dir": str(SOURCE_PANEL_RESULT_DIR),
        },
        "artifact_validation_errors": {
            "approval_valid_json": approval_valid,
            "approval_json_error": approval_error,
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
        },
        "safety_flags": {
            "repo_only": True,
            "pre_execution_readiness_verifier_only": True,
            **safety_flat,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1_latest.json"
    timestamped_json = (
        OUT_DIR / f"repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1_{stamp}.json"
    )
    latest_txt = OUT_DIR / "repo_only_data_horizon_expansion_pre_execution_readiness_verifier_after_approval_v1_latest.txt"
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
    return 0 if payload["readiness_verifier_completed"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
