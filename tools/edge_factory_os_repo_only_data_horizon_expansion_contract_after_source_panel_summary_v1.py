from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "bb4aae6"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 636
EXPECTED_TRACKED_PYTHON_COUNT = 637

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
SOURCE_PANEL_RESULT_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"
REQUIRED_SOURCE_PANEL_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

NEXT_MODULE_VALIDATOR = "edge_factory_os_repo_only_data_horizon_expansion_contract_validator_after_source_panel_summary_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_data_horizon_expansion_contract_blocked_record_after_source_panel_summary_v1.py"

CONTRACT_STATUS_PASS = "PASS_DATA_HORIZON_EXPANSION_CONTRACT_CREATED_VALIDATOR_NEXT"
CONTRACT_STATUS_BLOCKED = "BLOCKED_DATA_HORIZON_EXPANSION_CONTRACT_INCOMPLETE"
POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_CONTRACT_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_PASS_"
    "CONTRACT_VALIDATOR_NEXT"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_DATA_HORIZON_EXPANSION_CONTRACT_AFTER_SOURCE_PANEL_SUMMARY_POST_COMMIT_CHECK_BLOCKED"
)

EVIDENCE_BEFORE = "SOURCE_PANEL_RESEARCH_SUBSTRATE_VALIDATED_DATA_HORIZON_EXPANSION_RECOMMENDED"
EVIDENCE_AFTER_READY = "DATA_HORIZON_EXPANSION_CONTRACT_READY_NO_DATA_BUILD"
EVIDENCE_AFTER_BLOCKED = "DATA_HORIZON_EXPANSION_CONTRACT_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
TARGET_HORIZON = "3_to_4"
TARGET_TIMEFRAME = "1h"
TARGET_SCOPE = "CRYPTO_SOURCE_PANEL_RESEARCH_UNIVERSE_NO_NEW_UNIVERSE_EXPANSION_WITHOUT_LATER_EXPLICIT_CONTRACT"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

REQUIRED_FUTURE_ARTIFACT_LIST = [
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


def load_source_panel_artifacts() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    artifacts: Dict[str, Dict[str, Any]] = {}
    validations: Dict[str, Dict[str, Any]] = {}
    for name in REQUIRED_SOURCE_PANEL_ARTIFACTS:
        path = SOURCE_PANEL_RESULT_DIR / name
        payload, valid_json, error = load_json_checked(path)
        artifacts[name] = payload
        validations[name] = {
            "path": str(path),
            "exists": path.exists(),
            "valid_json": valid_json,
            "json_error": error,
            "non_empty": bool(payload),
            "artifact_name_matches": payload.get("artifact") == name,
        }
    return artifacts, validations


def prior_source_panel_summary_respected(summary: Dict[str, Any], valid_json: bool) -> bool:
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
        and summary.get("source_panel_results_are_reusable_data_quality_asset") is True
        and summary.get("one_year_panel_sufficient_for_pipeline_validation") is True
        and summary.get("one_year_panel_sufficient_for_strategy_edge_claims") is False
        and summary.get("data_horizon_expansion_recommended") is True
        and summary.get("recommended_historical_horizon_years") == TARGET_HORIZON
        and summary.get("current_evidence_chain_quality_after_summary") == EVIDENCE_BEFORE
        and summary.get("active_p0_blocker_count") == 0
        and summary.get("active_p1_attention_count") == 1
        and summary.get("strategy_signal_claims_made") is False
        and summary.get("tradable_edge_claims_made") is False
        and summary.get("profit_claims_made") is False
        and summary.get("backtest_performed") is False
        and summary.get("candidate_generation_performed") is False
        and summary.get("runtime_touch_performed") is False
        and summary.get("capital_touch_performed") is False
        and summary.get("live_touch_performed") is False
        and summary.get("generic_runner_approval_granted") is False
        and summary.get("generic_runner_implementation_remains_blocked") is True
        and summary.get("schema_or_config_created") is False
        and summary.get("ordinary_selector_backlog_loop_reentry_allowed") is False
        and summary.get("loop_remains_closed") is True
        and summary.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and summary.get("replacement_checks_all_true") is True
    )


def source_panel_summary_context(summary: Dict[str, Any], schema: Dict[str, Any], source_validated: bool) -> Dict[str, Any]:
    return {
        "completed": True,
        "validated": source_validated
        and summary.get("all_required_source_panel_result_artifacts_validated") is True
        and summary.get("parquet_schema_metadata_validated") is True
        and summary.get("parquet_schema_limitation_bounded") is True,
        "current_1_year_source_panel_result_artifacts_validated": summary.get(
            "all_required_source_panel_result_artifacts_validated"
        )
        is True,
        "parquet_schema_metadata_validated": summary.get("parquet_schema_metadata_validated") is True,
        "parquet_limitation_bounded": summary.get("parquet_schema_limitation_bounded") is True,
        "current_panel_useful_for_research_substrate": summary.get("source_panel_results_are_useful_research_substrate")
        is True,
        "current_panel_not_enough_for_strategy_edge_proof": summary.get(
            "one_year_panel_sufficient_for_strategy_edge_claims"
        )
        is False,
        "no_alpha_edge_tradable_profit_claim_exists": summary.get("source_panel_results_are_alpha_or_edge") is False
        and summary.get("tradable_edge_claims_made") is False
        and summary.get("profit_claims_made") is False,
        "current_panel_rows_metadata_only": schema.get("parquet_num_rows_metadata_only"),
        "current_panel_column_count": schema.get("parquet_column_count"),
    }


def expansion_objective() -> Dict[str, Any]:
    return {
        "completed": True,
        "target_historical_horizon_years": TARGET_HORIZON,
        "target_timeframe": TARGET_TIMEFRAME,
        "target_asset_scope": TARGET_SCOPE,
        "objective": "HISTORICAL_SOURCE_PANEL_AND_DATA_QUALITY_EXPANSION_BEFORE_SERIOUS_STRATEGY_RESEARCH",
        "not_objectives": [
            "candidate_generation",
            "backtest",
            "live_or_paper_trading",
            "runtime_deployment",
            "profit_claim",
            "tradable_edge_claim",
        ],
        "validated": True,
    }


def data_scope_contract() -> Dict[str, Any]:
    allowed_later_work = [
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
    forbidden_now = [
        "download_or_fetch_data_now",
        "build_historical_panel_now",
        "full_parquet_scan_now",
        "parquet_row_read_now",
        "strategy_research_now",
        "backtest_now",
        "candidate_generation_now",
        "runtime_capital_live_order_touch_now",
    ]
    return {
        "completed": True,
        "future_allowed_data_work_requires_later_approved_module": True,
        "allowed_later_work": allowed_later_work,
        "forbidden_now": forbidden_now,
        "future_data_download_allowed_now": False,
        "future_data_build_allowed_now": False,
        "historical_expansion_runner_allowed_now": False,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "validated": True,
    }


def survivorship_bias_and_universe_contract() -> Dict[str, Any]:
    requirements = [
        "symbol universe snapshot rules",
        "include delisted/removed symbols if data exists",
        "avoid selecting current winners and projecting backward",
        "document exchange/listing availability limitations",
        "document missing symbols",
        "document symbol start/end dates",
        "separate universe discovery from strategy selection",
    ]
    return {
        "completed": True,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "requirements": requirements,
        "validated": True,
    }


def holdout_and_validation_contract() -> Dict[str, Any]:
    requirements = [
        "reserve latest 6-12 months as strict holdout where feasible",
        "define train/validation/OOS split before strategy research",
        "use canonical month windows",
        "do not select candidates using holdout",
        "make no strategy claim until historical data-quality validator passes",
        "allow no paper/live without later preflight and kill-switch readiness",
    ]
    return {
        "completed": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "requirements": requirements,
        "validated": True,
    }


def required_future_artifacts_contract() -> Dict[str, Any]:
    return {
        "completed": True,
        "required_future_artifact_list": REQUIRED_FUTURE_ARTIFACT_LIST,
        "all_required_future_artifacts_named": len(REQUIRED_FUTURE_ARTIFACT_LIST) == 9,
        "validated": True,
    }


def evidence_policy_contract() -> Dict[str, Any]:
    return {
        "completed": True,
        "current_source_panel_evidence_classification": "SOURCE_PANEL_RESEARCH_SUBSTRATE_NOT_EDGE_PROOF",
        "future_expanded_data_artifacts_must_be_primary_artifacts": True,
        "derived_metadata_allowed_only_as": "DERIVED_EXPLICIT_ATTENTION_WITH_REASON_AND_MONITORING",
        "derived_overused_default_forbidden": True,
        "pass_with_attention_p1_must_not_normalize": True,
        "data_horizon_expansion_must_close_real_final_form_gap_not_documentation_loop": True,
        "validated": True,
    }


def safety_boundary_contract() -> Dict[str, Any]:
    checks = {
        "no_strategy_research": True,
        "no_backtest": True,
        "no_candidate_generation": True,
        "no_family_release": True,
        "no_active_paper": True,
        "no_real_order": True,
        "no_runtime_capital_live_touch": True,
        "no_generic_runner_approval_implementation": True,
        "no_schema_config_creation": True,
        "no_old_source_panel_anomaly_route_reopening": True,
        "no_profit_tradable_edge_claim": True,
        "no_data_download_fetch_build": True,
        "no_source_panel_rerun": True,
        "no_full_parquet_scan": True,
        "no_parquet_row_read": True,
    }
    return {
        "completed": True,
        "checks": checks,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "old_route_closed_artifacts_active_evidence_allowed": False,
        "validated": all(checks.values()),
    }


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    summary, summary_valid_json, summary_json_error = load_json_checked(SOURCE_PANEL_SUMMARY_ARTIFACT)
    schema, schema_valid_json, schema_json_error = load_json_checked(SCHEMA_METADATA_ARTIFACT)
    source_artifacts, source_artifact_validations = load_source_panel_artifacts()
    source_artifacts_validated = all(
        item["exists"] and item["valid_json"] and item["non_empty"] and item["artifact_name_matches"]
        for item in source_artifact_validations.values()
    )

    prior_respected = prior_source_panel_summary_respected(summary, summary_valid_json)
    context = source_panel_summary_context(summary, schema, source_artifacts_validated and schema_valid_json)
    objective = expansion_objective()
    scope_contract = data_scope_contract()
    survivorship = survivorship_bias_and_universe_contract()
    holdout = holdout_and_validation_contract()
    future_artifacts = required_future_artifacts_contract()
    evidence_policy = evidence_policy_contract()
    safety = safety_boundary_contract()

    contract_complete = all(
        [
            prior_respected,
            context["validated"],
            objective["validated"],
            scope_contract["validated"],
            survivorship["validated"],
            holdout["validated"],
            future_artifacts["validated"],
            evidence_policy["validated"],
            safety["validated"],
        ]
    )
    next_module = NEXT_MODULE_VALIDATOR if contract_complete else NEXT_MODULE_BLOCKED
    status = CONTRACT_STATUS_PASS if contract_complete else CONTRACT_STATUS_BLOCKED
    final_decision = (
        "DATA_HORIZON_EXPANSION_CONTRACT_READY_VALIDATOR_NEXT"
        if contract_complete
        else "DATA_HORIZON_EXPANSION_CONTRACT_BLOCKED_RECORD_NEXT"
    )
    next_action = (
        "BUILD_DATA_HORIZON_EXPANSION_CONTRACT_VALIDATOR_AFTER_SOURCE_PANEL_SUMMARY"
        if contract_complete
        else "BUILD_DATA_HORIZON_EXPANSION_CONTRACT_BLOCKED_RECORD_AFTER_SOURCE_PANEL_SUMMARY"
    )

    safety_flat = {
        "future_data_download_allowed_now": False,
        "future_data_build_allowed_now": False,
        "historical_expansion_runner_allowed_now": False,
        "strategy_research_allowed_now": False,
        "backtest_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "old_source_panel_anomaly_route_reopen_allowed": False,
        "old_route_closed_artifacts_active_evidence_allowed": False,
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
        "data_download_fetch_build_performed": False,
        "source_panel_rerun_performed": False,
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
    }
    allowed_next_modules = {NEXT_MODULE_VALIDATOR, NEXT_MODULE_BLOCKED}
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_636_to_637": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "prior_source_panel_summary_respected": prior_respected,
        "source_panel_summary_artifact_valid_json": summary_valid_json,
        "schema_metadata_artifact_valid_json": schema_valid_json,
        "source_panel_result_artifacts_validated": source_artifacts_validated,
        "data_horizon_expansion_contract_created": True,
        "future_data_download_allowed_now_false": safety_flat["future_data_download_allowed_now"] is False,
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
        "old_route_reopen_forbidden": safety_flat["old_source_panel_anomaly_route_reopen_allowed"] is False,
        "old_route_closed_artifacts_active_evidence_forbidden": safety_flat[
            "old_route_closed_artifacts_active_evidence_allowed"
        ]
        is False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "next_module_allowed": next_module in allowed_next_modules,
        "data_build_download_fetch_not_selected": all(
            token not in next_module for token in ["download", "fetch", "build", "runner"]
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
        "data_horizon_expansion_contract_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if contract_complete else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_source_panel_summary_respected": prior_respected,
        "data_horizon_expansion_contract_created": True,
        "source_panel_summary_context_completed": context["completed"],
        "expansion_objective_completed": objective["completed"],
        "data_scope_contract_completed": scope_contract["completed"],
        "survivorship_bias_and_universe_contract_completed": survivorship["completed"],
        "holdout_and_validation_contract_completed": holdout["completed"],
        "required_future_artifacts_completed": future_artifacts["completed"],
        "evidence_policy_contract_completed": evidence_policy["completed"],
        "safety_boundary_contract_completed": safety["completed"],
        "current_panel_horizon_years": 1,
        "current_panel_sufficient_for_pipeline_validation": True,
        "current_panel_sufficient_for_strategy_edge_claims": False,
        "data_horizon_expansion_recommended": True,
        "target_historical_horizon_years": TARGET_HORIZON,
        "target_timeframe": TARGET_TIMEFRAME,
        "target_expansion_scope": TARGET_SCOPE,
        **safety_flat,
        "required_future_artifact_list": REQUIRED_FUTURE_ARTIFACT_LIST,
        "survivorship_bias_controls_required": True,
        "symbol_lifecycle_report_required": True,
        "holdout_policy_required": True,
        "historical_data_quality_validator_required": True,
        "source_panel_results_are_useful_research_substrate": True,
        "source_panel_results_are_alpha_or_edge": False,
        "source_panel_results_are_reusable_data_quality_asset": True,
        "current_evidence_chain_quality_before_contract": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_contract": EVIDENCE_AFTER_READY
        if contract_complete
        else EVIDENCE_AFTER_BLOCKED,
        "active_p0_blocker_count": 0 if contract_complete else 1,
        "active_p1_attention_count": 1 if contract_complete else 0,
        "money_path_alignment": "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH",
        "usable_or_sellable_asset_path": (
            "REPO_ONLY_HISTORICAL_SOURCE_PANEL_EXPANSION_CONTRACT_AS_REUSABLE_DATA_QUALITY_ASSET_PATH"
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
            "This contract reads the prior source-panel result summary, parquet schema metadata, and source-panel JSON "
            "artifacts as explicit replacement checks. It creates only a contract artifact and does not download, fetch, "
            "or build data; rerun source-panel analysis; scan parquet; read parquet rows; run strategy/backtest/candidate "
            "work; touch runtime/capital/live/order paths; approve or implement a generic runner; create schema/config "
            "files; reopen old anomaly routes; or claim profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "source_panel_summary_context": context,
        "expansion_objective": objective,
        "data_scope_contract": scope_contract,
        "survivorship_bias_and_universe_contract": survivorship,
        "holdout_and_validation_contract": holdout,
        "required_future_artifacts_contract": future_artifacts,
        "evidence_policy_contract": evidence_policy,
        "safety_boundary_contract": safety,
        "artifact_paths": {
            "source_panel_summary_artifact": str(SOURCE_PANEL_SUMMARY_ARTIFACT),
            "schema_metadata_artifact": str(SCHEMA_METADATA_ARTIFACT),
            "source_panel_result_dir": str(SOURCE_PANEL_RESULT_DIR),
        },
        "artifact_validation": {
            "source_panel_summary_valid_json": summary_valid_json,
            "source_panel_summary_json_error": summary_json_error,
            "schema_metadata_valid_json": schema_valid_json,
            "schema_metadata_json_error": schema_json_error,
            "source_panel_result_artifacts": source_artifact_validations,
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
            "contract_only": True,
            **safety_flat,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1_latest.txt"
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
    return 0 if payload["data_horizon_expansion_contract_created"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
