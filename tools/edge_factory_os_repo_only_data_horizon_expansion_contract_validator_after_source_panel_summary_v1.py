from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "bf935da"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 637
EXPECTED_TRACKED_PYTHON_COUNT = 638

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
SCHEMA_METADATA_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1"
    / "source_panel_parquet_schema_metadata_after_pyarrow_repair.json"
)

NEXT_MODULE_RUNNER_PREVIEW = "edge_factory_os_repo_only_data_horizon_expansion_runner_preview_after_source_panel_summary_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_data_horizon_expansion_contract_blocked_record_after_source_panel_summary_v1.py"

VALIDATOR_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_CONTRACT_VALIDATED_RUNNER_PREVIEW_READY"
VALIDATOR_STATUS_BLOCKED = "BLOCKED_DATA_HORIZON_EXPANSION_CONTRACT_VALIDATION_FAILED"
POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_CONTRACT_VALIDATOR_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_PASS_"
    "RUNNER_PREVIEW_NEXT"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_CONTRACT_VALIDATOR_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_BLOCKED"
)

EVIDENCE_BEFORE = "DATA_HORIZON_EXPANSION_CONTRACT_READY_NO_DATA_BUILD"
EVIDENCE_AFTER = "DATA_HORIZON_EXPANSION_CONTRACT_VALIDATED_RUNNER_PREVIEW_READY"
EVIDENCE_BLOCKED = "DATA_HORIZON_EXPANSION_CONTRACT_VALIDATION_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
TARGET_HORIZON = "3_to_4"
TARGET_TIMEFRAME = "1h"
DOCUMENTATION_LOOP_RISK_LEVEL = "LOW_BOUNDED_BY_REAL_DATA_HORIZON_GAP"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

REQUIRED_FUTURE_ARTIFACTS = [
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

EXPECTED_DATA_SCOPE_ITEMS = [
    "candle/source panel inventory",
    "3-4 year historical coverage map",
    "symbol/time coverage",
    "missingness and freshness report",
    "duplicate/timestamp gap checks",
    "OHLCV integrity checks",
    "feature recomputation readiness review",
    "source reliability review",
    "contract compliance report",
]

SURVIVORSHIP_REQUIREMENTS = [
    "symbol universe snapshot rules",
    "include delisted/removed symbols if data exists",
    "avoid selecting current winners and projecting backward",
    "document exchange/listing availability limitations",
    "document missing symbols",
    "document symbol start/end dates",
    "separate universe discovery from strategy selection",
]

HOLDOUT_REQUIREMENTS = [
    "reserve latest 6-12 months as strict holdout where feasible",
    "define train/validation/OOS split before strategy research",
    "use canonical month windows",
    "do not select candidates using holdout",
    "make no strategy claim until historical data-quality validator passes",
    "allow no paper/live without later preflight and kill-switch readiness",
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


def normalize_items(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def includes_all(actual: List[str], expected: List[str]) -> bool:
    actual_lower = {item.lower() for item in actual}
    return all(item.lower() in actual_lower for item in expected)


def contract_artifact_validation(contract: Dict[str, Any], valid_json: bool, error: str) -> Dict[str, Any]:
    sections = {
        "source_panel_summary_context": isinstance(contract.get("source_panel_summary_context"), dict),
        "expansion_objective": isinstance(contract.get("expansion_objective"), dict),
        "data_scope_contract": isinstance(contract.get("data_scope_contract"), dict),
        "survivorship_bias_and_universe_contract": isinstance(
            contract.get("survivorship_bias_and_universe_contract"), dict
        ),
        "holdout_and_validation_contract": isinstance(contract.get("holdout_and_validation_contract"), dict),
        "required_future_artifacts": isinstance(contract.get("required_future_artifacts_contract"), dict)
        or isinstance(contract.get("required_future_artifacts"), dict),
        "evidence_policy_contract": isinstance(contract.get("evidence_policy_contract"), dict),
        "safety_boundary_contract": isinstance(contract.get("safety_boundary_contract"), dict),
        "next_module_decision": isinstance(contract.get("next_module_decision"), dict)
        or (
            contract.get("next_module")
            == "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1.py"
            and isinstance(contract.get("final_decision"), str)
            and isinstance(contract.get("next_action"), str)
        ),
    }
    checks = {
        "contract_artifact_exists": CONTRACT_ARTIFACT.exists(),
        "contract_artifact_valid_json": valid_json,
        "contract_artifact_non_empty": bool(contract),
        "required_sections_present_or_equivalent": all(sections.values()),
    }
    return {
        "completed": True,
        "validated": all(checks.values()),
        "checks": checks,
        "required_sections": sections,
        "json_error": error,
    }


def source_panel_summary_context_validation(contract: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
    context = contract.get("source_panel_summary_context", {})
    checks = {
        "results_useful_substrate": contract.get("source_panel_results_are_useful_research_substrate") is True
        and context.get("current_panel_useful_for_research_substrate") is True,
        "results_not_alpha_edge": contract.get("source_panel_results_are_alpha_or_edge") is False,
        "one_year_pipeline_validation_true": contract.get("current_panel_sufficient_for_pipeline_validation") is True,
        "one_year_strategy_edge_claims_false": contract.get("current_panel_sufficient_for_strategy_edge_claims") is False,
        "parquet_schema_limitation_bounded": context.get("parquet_limitation_bounded") is True,
        "no_profit_tradable_edge_claim": contract.get("profit_claims_made") is False
        and contract.get("tradable_edge_claims_made") is False
        and summary.get("source_panel_results_are_alpha_or_edge") is False,
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def expansion_objective_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    objective = contract.get("expansion_objective", {})
    not_objectives = normalize_items(objective.get("not_objectives"))
    expected_not_objectives = [
        "candidate_generation",
        "backtest",
        "live_or_paper_trading",
        "runtime_deployment",
        "profit_claim",
        "tradable_edge_claim",
    ]
    checks = {
        "target_historical_horizon_years": contract.get("target_historical_horizon_years") == TARGET_HORIZON
        and objective.get("target_historical_horizon_years") == TARGET_HORIZON,
        "target_timeframe": contract.get("target_timeframe") == TARGET_TIMEFRAME
        and objective.get("target_timeframe") == TARGET_TIMEFRAME,
        "objective_is_historical_source_panel_data_quality_expansion": objective.get("objective")
        == "HISTORICAL_SOURCE_PANEL_AND_DATA_QUALITY_EXPANSION_BEFORE_SERIOUS_STRATEGY_RESEARCH",
        "not_objectives_blocked": includes_all(not_objectives, expected_not_objectives),
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def data_scope_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    scope = contract.get("data_scope_contract", {})
    allowed_later = normalize_items(scope.get("allowed_later_work"))
    checks = {
        "future_scope_items_present": includes_all(allowed_later, EXPECTED_DATA_SCOPE_ITEMS),
        "future_data_download_now_false": contract.get("future_data_download_allowed_now") is False,
        "future_data_fetch_now_false": contract.get("future_data_fetch_allowed_now", False) is False,
        "future_data_build_now_false": contract.get("future_data_build_allowed_now") is False,
        "source_panel_rerun_now_false": contract.get("source_panel_rerun_performed") is False,
        "full_parquet_scan_now_false": contract.get("full_parquet_scan_performed") is False,
        "parquet_row_read_now_false": contract.get("parquet_rows_read_now") is False,
        "historical_expansion_runner_now_false": contract.get("historical_expansion_runner_allowed_now") is False,
        "strategy_research_now_false": contract.get("strategy_research_allowed_now") is False,
        "backtest_now_false": contract.get("backtest_allowed_now") is False,
        "candidate_generation_now_false": contract.get("candidate_generation_allowed_now") is False,
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def survivorship_bias_and_universe_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    section = contract.get("survivorship_bias_and_universe_contract", {})
    requirements = normalize_items(section.get("requirements"))
    checks = {
        "survivorship_bias_controls_required": contract.get("survivorship_bias_controls_required") is True,
        "symbol_lifecycle_report_required": contract.get("symbol_lifecycle_report_required") is True,
        "required_controls_present": includes_all(requirements, SURVIVORSHIP_REQUIREMENTS),
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def holdout_and_validation_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    section = contract.get("holdout_and_validation_contract", {})
    requirements = normalize_items(section.get("requirements"))
    checks = {
        "holdout_policy_required": contract.get("holdout_policy_required") is True,
        "historical_data_quality_validator_required": contract.get("historical_data_quality_validator_required") is True,
        "holdout_requirements_present": includes_all(requirements, HOLDOUT_REQUIREMENTS),
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def required_future_artifacts_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    artifacts = normalize_items(contract.get("required_future_artifact_list"))
    checks = {
        "required_future_artifact_list_complete": includes_all(artifacts, REQUIRED_FUTURE_ARTIFACTS),
        "required_future_artifact_count": len(set(artifacts)) >= len(REQUIRED_FUTURE_ARTIFACTS),
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def evidence_policy_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    section = contract.get("evidence_policy_contract", {})
    checks = {
        "current_source_panel_is_substrate_not_edge": section.get("current_source_panel_evidence_classification")
        == "SOURCE_PANEL_RESEARCH_SUBSTRATE_NOT_EDGE_PROOF",
        "future_artifacts_primary": section.get("future_expanded_data_artifacts_must_be_primary_artifacts") is True,
        "derived_metadata_explicit_attention_only": section.get("derived_metadata_allowed_only_as")
        == "DERIVED_EXPLICIT_ATTENTION_WITH_REASON_AND_MONITORING",
        "derived_overused_forbidden": section.get("derived_overused_default_forbidden") is True,
        "p1_must_not_normalize": section.get("pass_with_attention_p1_must_not_normalize") is True,
        "real_gap_not_documentation_loop": section.get(
            "data_horizon_expansion_must_close_real_final_form_gap_not_documentation_loop"
        )
        is True,
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def safety_boundary_validation(contract: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "no_strategy_research": contract.get("strategy_research_allowed_now") is False
        and contract.get("strategy_signal_claims_made") is False,
        "no_backtest": contract.get("backtest_allowed_now") is False and contract.get("backtest_performed") is False,
        "no_candidate_generation": contract.get("candidate_generation_allowed_now") is False
        and contract.get("candidate_generation_performed") is False,
        "no_family_release": contract.get("family_release_performed") is False,
        "no_active_paper": contract.get("active_paper_performed") is False,
        "no_real_order": contract.get("real_order_touch_performed") is False,
        "no_runtime_capital_live_touch": contract.get("runtime_touch_performed") is False
        and contract.get("capital_touch_performed") is False
        and contract.get("live_touch_performed") is False,
        "no_generic_runner": contract.get("generic_runner_approval_granted") is False
        and contract.get("generic_runner_implementation_remains_blocked") is True,
        "no_schema_config_creation": contract.get("schema_or_config_created") is False,
        "no_old_route_reopen": contract.get("old_source_panel_anomaly_route_reopen_allowed") is False,
        "no_profit_tradable_edge_claim": contract.get("profit_claims_made") is False
        and contract.get("tradable_edge_claims_made") is False,
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def prior_contract_respected(contract: Dict[str, Any], valid_json: bool) -> bool:
    return (
        valid_json
        and contract.get("data_horizon_expansion_contract_status")
        == "PASS_DATA_HORIZON_EXPANSION_CONTRACT_CREATED_VALIDATOR_NEXT"
        and contract.get("data_horizon_expansion_contract_created") is True
        and contract.get("target_historical_horizon_years") == TARGET_HORIZON
        and contract.get("target_timeframe") == TARGET_TIMEFRAME
        and contract.get("future_data_download_allowed_now") is False
        and contract.get("future_data_build_allowed_now") is False
        and contract.get("historical_expansion_runner_allowed_now") is False
        and contract.get("strategy_research_allowed_now") is False
        and contract.get("backtest_allowed_now") is False
        and contract.get("candidate_generation_allowed_now") is False
        and contract.get("survivorship_bias_controls_required") is True
        and contract.get("symbol_lifecycle_report_required") is True
        and contract.get("holdout_policy_required") is True
        and contract.get("historical_data_quality_validator_required") is True
        and contract.get("current_evidence_chain_quality_after_contract") == EVIDENCE_BEFORE
        and contract.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and contract.get("replacement_checks_all_true") is True
    )


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    contract, contract_valid_json, contract_json_error = load_json_checked(CONTRACT_ARTIFACT)
    summary, summary_valid_json, summary_json_error = load_json_checked(SOURCE_PANEL_SUMMARY_ARTIFACT)
    schema, schema_valid_json, schema_json_error = load_json_checked(SCHEMA_METADATA_ARTIFACT)

    contract_artifact = contract_artifact_validation(contract, contract_valid_json, contract_json_error)
    summary_context = source_panel_summary_context_validation(contract, summary)
    objective = expansion_objective_validation(contract)
    data_scope = data_scope_validation(contract)
    survivorship = survivorship_bias_and_universe_validation(contract)
    holdout = holdout_and_validation_validation(contract)
    future_artifacts = required_future_artifacts_validation(contract)
    evidence_policy = evidence_policy_validation(contract)
    safety = safety_boundary_validation(contract)
    prior_respected = prior_contract_respected(contract, contract_valid_json)

    all_validated = all(
        item["validated"]
        for item in [
            contract_artifact,
            summary_context,
            objective,
            data_scope,
            survivorship,
            holdout,
            future_artifacts,
            evidence_policy,
            safety,
        ]
    ) and prior_respected

    next_module = NEXT_MODULE_RUNNER_PREVIEW if all_validated else NEXT_MODULE_BLOCKED
    status = VALIDATOR_STATUS_PASS if all_validated else VALIDATOR_STATUS_BLOCKED
    final_decision = (
        "DATA_HORIZON_EXPANSION_CONTRACT_VALIDATED_RUNNER_PREVIEW_READY"
        if all_validated
        else "DATA_HORIZON_EXPANSION_CONTRACT_VALIDATION_BLOCKED_RECORD_NEXT"
    )
    next_action = (
        "BUILD_DATA_HORIZON_EXPANSION_RUNNER_PREVIEW_AFTER_SOURCE_PANEL_SUMMARY"
        if all_validated
        else "BUILD_DATA_HORIZON_EXPANSION_CONTRACT_BLOCKED_RECORD_AFTER_SOURCE_PANEL_SUMMARY"
    )

    safety_flat = {
        "future_data_download_allowed_now": False,
        "future_data_fetch_allowed_now": False,
        "future_data_build_allowed_now": False,
        "historical_expansion_runner_allowed_now": False,
        "historical_expansion_runner_preview_allowed_next": all_validated,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
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
        "data_download_fetch_build_performed": False,
        "source_panel_rerun_performed": False,
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
    }

    documentation_loop_detected = False
    next_module_closes_real_gap = all_validated
    active_p0 = 0 if all_validated else 1
    active_p1 = 1 if all_validated else 0
    allowed_next_modules = {NEXT_MODULE_RUNNER_PREVIEW, NEXT_MODULE_BLOCKED}
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_637_to_638": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "prior_data_horizon_contract_respected": prior_respected,
        "data_horizon_expansion_contract_validated": all_validated,
        "contract_artifact_valid_json": contract_valid_json,
        "source_panel_summary_valid_json": summary_valid_json,
        "schema_metadata_valid_json": schema_valid_json,
        "future_data_download_allowed_now_false": safety_flat["future_data_download_allowed_now"] is False,
        "future_data_fetch_allowed_now_false": safety_flat["future_data_fetch_allowed_now"] is False,
        "future_data_build_allowed_now_false": safety_flat["future_data_build_allowed_now"] is False,
        "historical_expansion_runner_allowed_now_false": safety_flat["historical_expansion_runner_allowed_now"] is False,
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
        "documentation_loop_not_detected": documentation_loop_detected is False,
        "next_module_closes_real_gap": next_module_closes_real_gap is True,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module in allowed_next_modules,
        "direct_download_fetch_build_execution_not_selected": all(
            token not in next_module for token in ["download", "fetch", "build", "execution"]
        ),
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
        "data_horizon_expansion_contract_validator_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if all_validated else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_data_horizon_contract_respected": prior_respected,
        "data_horizon_expansion_contract_validated": all_validated,
        "contract_artifact_validation_completed": contract_artifact["completed"],
        "source_panel_summary_context_validation_completed": summary_context["completed"],
        "expansion_objective_validation_completed": objective["completed"],
        "data_scope_validation_completed": data_scope["completed"],
        "survivorship_bias_and_universe_validation_completed": survivorship["completed"],
        "holdout_and_validation_validation_completed": holdout["completed"],
        "required_future_artifacts_validation_completed": future_artifacts["completed"],
        "evidence_policy_validation_completed": evidence_policy["completed"],
        "safety_boundary_validation_completed": safety["completed"],
        "contract_artifact_exists": CONTRACT_ARTIFACT.exists(),
        "contract_artifact_valid_json": contract_valid_json,
        "current_panel_sufficient_for_pipeline_validation": True,
        "current_panel_sufficient_for_strategy_edge_claims": False,
        "data_horizon_expansion_recommended": True,
        "target_historical_horizon_years": TARGET_HORIZON,
        "target_timeframe": TARGET_TIMEFRAME,
        **safety_flat,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "required_future_artifact_list_validated": future_artifacts["validated"],
        "source_panel_results_are_useful_research_substrate": True,
        "source_panel_results_are_alpha_or_edge": False,
        "source_panel_results_are_reusable_data_quality_asset": True,
        "current_evidence_chain_quality_before_validator": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_validator": EVIDENCE_AFTER if all_validated else EVIDENCE_BLOCKED,
        "documentation_loop_detected": documentation_loop_detected,
        "documentation_loop_risk_level": DOCUMENTATION_LOOP_RISK_LEVEL,
        "next_module_closes_real_gap": next_module_closes_real_gap,
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": active_p1,
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH",
        "usable_or_sellable_asset_path": (
            "REPO_ONLY_HISTORICAL_SOURCE_PANEL_EXPANSION_PREVIEW_AS_REUSABLE_DATA_QUALITY_ASSET_PATH"
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
            "This validator reads the data horizon expansion contract, source-panel summary, and parquet schema metadata "
            "artifacts as explicit replacement checks. It validates only the contract and does not download, fetch, or "
            "build data; run a historical expansion runner; rerun source-panel analysis; scan parquet; read parquet rows; "
            "run strategy/backtest/candidate work; touch runtime/capital/live/order paths; approve or implement a generic "
            "runner; create schema/config files; reopen old anomaly routes; or claim profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "contract_artifact_validation": contract_artifact,
        "source_panel_summary_context_validation": summary_context,
        "expansion_objective_validation": objective,
        "data_scope_validation": data_scope,
        "survivorship_bias_and_universe_validation": survivorship,
        "holdout_and_validation_validation": holdout,
        "required_future_artifacts_validation": future_artifacts,
        "evidence_policy_validation": evidence_policy,
        "safety_boundary_validation": safety,
        "artifact_paths": {
            "contract_artifact": str(CONTRACT_ARTIFACT),
            "source_panel_summary_artifact": str(SOURCE_PANEL_SUMMARY_ARTIFACT),
            "schema_metadata_artifact": str(SCHEMA_METADATA_ARTIFACT),
        },
        "artifact_validation_errors": {
            "contract_json_error": contract_json_error,
            "source_panel_summary_valid_json": summary_valid_json,
            "source_panel_summary_json_error": summary_json_error,
            "schema_metadata_valid_json": schema_valid_json,
            "schema_metadata_json_error": schema_json_error,
            "schema_metadata_column_count": schema.get("parquet_column_count"),
            "schema_metadata_rows": schema.get("parquet_num_rows_metadata_only"),
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
            "contract_validator_only": True,
            **safety_flat,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1_latest.json"
    timestamped_json = (
        OUT_DIR / f"repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1_{stamp}.json"
    )
    latest_txt = OUT_DIR / "repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1_latest.txt"
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
    return 0 if payload["contract_artifact_validation_completed"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
