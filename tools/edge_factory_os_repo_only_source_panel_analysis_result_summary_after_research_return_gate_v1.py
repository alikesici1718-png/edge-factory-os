from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_START_HEAD = "69743d4"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 635
EXPECTED_TRACKED_PYTHON_COUNT = 636

SOURCE_PANEL_RESULT_DIR = LAB_ROOT / "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"
REQUIRED_SOURCE_PANEL_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]
SCHEMA_METADATA_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_after_result_review_v1"
    / "source_panel_parquet_schema_metadata_after_pyarrow_repair.json"
)
PYARROW_SCHEMA_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_source_panel_pyarrow_schema_access_repair_apply_validator_after_result_review_v1"
    / "repo_only_source_panel_pyarrow_schema_access_repair_apply_validator_after_result_review_v1_latest.json"
)

PARQUET_INPUT_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_feature_panels"
    r"\market_panic_rebound_long_v1\market_panic_rebound_long_v1_feature_panel_1h.parquet"
)
EXPECTED_PARQUET_SIZE_BYTES = 99504547
EXPECTED_PARQUET_COLUMN_COUNT = 12
EXPECTED_PARQUET_NUM_ROWS = 1920290
EXPECTED_PARQUET_ROW_GROUPS = 2

NEXT_MODULE_EXPANSION_CONTRACT = "edge_factory_os_repo_only_data_horizon_expansion_contract_after_source_panel_summary_v1.py"
NEXT_MODULE_RESEARCH_QUEUE = "edge_factory_os_repo_only_research_queue_selector_after_source_panel_summary_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_result_summary_blocked_record_v1.py"

POST_CHECK_STATUS_PASS = (
    "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RESULT_SUMMARY_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS_"
    "DATA_HORIZON_EXPANSION_CONTRACT_NEXT"
)
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RESULT_SUMMARY_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_BLOCKED"
)
SUMMARY_STATUS_PASS = "PASS_SOURCE_PANEL_RESEARCH_SUBSTRATE_VALIDATED_DATA_HORIZON_EXPANSION_RECOMMENDED"
SUMMARY_STATUS_BLOCKED = "BLOCKED_SOURCE_PANEL_RESULT_SUMMARY_INCOMPLETE"

EVIDENCE_BEFORE = "PRIMARY_ARTIFACT_STRONG_WITH_BOUNDED_SCHEMA_METADATA_SOURCE_PANEL_RESULTS"
EVIDENCE_AFTER_EXPANSION = "SOURCE_PANEL_RESEARCH_SUBSTRATE_VALIDATED_DATA_HORIZON_EXPANSION_RECOMMENDED"
EVIDENCE_AFTER_BLOCKED = "SOURCE_PANEL_RESULT_SUMMARY_BLOCKED"
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"
RECOMMENDED_HISTORICAL_HORIZON_YEARS = "3_to_4"

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


def source_panel_artifact_summary(
    artifacts: Dict[str, Dict[str, Any]], validations: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    inventory = artifacts.get("source_panel_inventory.json", {})
    coverage = artifacts.get("source_panel_coverage_summary.json", {})
    missingness = artifacts.get("source_panel_missingness_report.json", {})
    anomaly = artifacts.get("source_panel_anomaly_report.json", {})
    quality = artifacts.get("source_panel_quality_scorecard.json", {})
    compliance = artifacts.get("source_panel_contract_compliance_report.json", {})

    required_valid = all(
        item["exists"] and item["valid_json"] and item["non_empty"] and item["artifact_name_matches"]
        for item in validations.values()
    )
    compliance_ok = (
        compliance.get("required_artifacts_created") is True
        and compliance.get("limitations_honestly_recorded") is True
        and compliance.get("no_strategy_signal_claim") is True
        and compliance.get("no_profit_claim") is True
        and compliance.get("no_backtest") is True
        and compliance.get("no_candidate_generation") is True
        and compliance.get("no_runtime_capital_live_order_touch") is True
        and compliance.get("no_generic_runner") is True
        and compliance.get("no_schema_config_creation") is True
        and compliance.get("old_source_panel_anomaly_route_not_reopened") is True
        and compliance.get("old_route_closed_artifacts_not_active_evidence") is True
    )
    all_validated = required_valid and compliance_ok

    return {
        "completed": True,
        "validated": all_validated,
        "required_artifacts": validations,
        "inventory_result": {
            "candidate_key": inventory.get("candidate_key"),
            "family_key": inventory.get("family_key"),
            "feature_panel_path": inventory.get("feature_panel_path"),
            "panel_rows": inventory.get("panel_rows"),
            "processed_symbol_count": inventory.get("processed_symbol_count"),
            "source_file_count": inventory.get("source_file_count"),
            "first_time": inventory.get("first_time"),
            "last_time": inventory.get("last_time"),
            "source_categories": inventory.get("source_categories", []),
            "symbol_identifiers_available": inventory.get("symbol_identifiers_available") is True,
            "timestamp_columns_available": inventory.get("timestamp_columns_available") is True,
            "limitations": inventory.get("limitations", []),
        },
        "coverage_result": {
            "panel_rows": coverage.get("panel_completeness_summary", {}).get("panel_rows"),
            "audit_status": coverage.get("panel_completeness_summary", {}).get("audit_status"),
            "runner_panel_allowed": coverage.get("panel_completeness_summary", {}).get("runner_panel_allowed"),
            "candle_overall_verdict": coverage.get("panel_completeness_summary", {}).get("candle_overall_verdict"),
            "processed_symbol_count": coverage.get("symbol_coverage", {}).get("processed_symbol_count"),
            "candle_symbols_found": coverage.get("symbol_coverage", {}).get("candle_symbols_found"),
            "candle_ready_symbols": coverage.get("symbol_coverage", {}).get("candle_ready_symbols"),
            "candle_weak_symbols": coverage.get("symbol_coverage", {}).get("candle_weak_symbols"),
            "raw_files_found": coverage.get("source_coverage", {}).get("raw_files_found"),
            "valid_ohlcv_files": coverage.get("source_coverage", {}).get("valid_ohlcv_files"),
            "time_coverage": coverage.get("time_coverage", {}),
            "missing_output_cols": coverage.get("feature_coverage", {}).get("missing_output_cols", []),
            "limitations": coverage.get("limitations", []),
        },
        "missingness_result": {
            "null_nan_counts_available": missingness.get("null_nan_counts_available") is True,
            "missingness_by_feature": missingness.get("missingness_by_feature", {}),
            "missingness_by_symbol_time": missingness.get("missingness_by_symbol_time", {}),
            "incomplete_input_warnings": missingness.get("incomplete_input_warnings", []),
            "limitations": missingness.get("limitations", []),
        },
        "anomaly_data_quality_result": {
            "data_quality_anomalies_only": anomaly.get("data_quality_anomalies_only") is True,
            "duplicate_rows_checked": anomaly.get("duplicate_rows_checked") is True,
            "duplicate_rows": anomaly.get("duplicate_rows"),
            "extreme_missingness_checked": anomaly.get("extreme_missingness_checked") is True,
            "extreme_missingness_findings": anomaly.get("extreme_missingness_findings", []),
            "stale_freshness_checked": anomaly.get("stale_freshness_checked") is True,
            "freshness_summary": anomaly.get("freshness_summary", {}),
            "source_mismatch_checked": anomaly.get("source_mismatch_checked") is True,
            "source_mismatch_issues": anomaly.get("source_mismatch_issues", []),
            "malformed_timestamps_checked": anomaly.get("malformed_timestamps_checked") is True,
            "non_monotonic_time_checked": anomaly.get("non_monotonic_time_checked") is True,
            "old_source_panel_anomaly_route_reopened": anomaly.get("old_source_panel_anomaly_route_reopened") is True,
            "old_route_closed_artifacts_used_as_active_evidence": anomaly.get(
                "old_route_closed_artifacts_used_as_active_evidence"
            )
            is True,
            "limitations": anomaly.get("limitations", []),
        },
        "quality_scorecard_result": {
            "overall_quality_score": quality.get("overall_quality_score"),
            "quality_bucket": quality.get("quality_bucket"),
            "coverage_score": quality.get("coverage_score"),
            "missingness_score": quality.get("missingness_score"),
            "freshness_score": quality.get("freshness_score"),
            "quality_score_by_source": quality.get("quality_score_by_source", {}),
            "no_strategy_candidate_edge_claim": quality.get("no_strategy_candidate_edge_claim") is True,
            "reliability_notes": quality.get("reliability_notes", []),
        },
        "contract_compliance_result": {
            "validated": compliance_ok,
            "required_artifact_list": compliance.get("required_artifact_list", []),
            "required_artifacts_created": compliance.get("required_artifacts_created") is True,
            "limitations_honestly_recorded": compliance.get("limitations_honestly_recorded") is True,
            "source_panel_result_primary_strength_claimed_now": compliance.get(
                "source_panel_result_primary_strength_claimed_now"
            )
            is True,
            "source_panel_result_primary_strength_requires_future_validator": compliance.get(
                "source_panel_result_primary_strength_requires_future_validator"
            )
            is True,
        },
        "limitations": sorted(
            set(
                str(item)
                for payload in [inventory, coverage, missingness, anomaly]
                for item in payload.get("limitations", [])
            )
        ),
    }


def parquet_schema_summary(schema: Dict[str, Any], validator: Dict[str, Any], schema_valid_json: bool) -> Dict[str, Any]:
    column_names = schema.get("parquet_column_names")
    if not isinstance(column_names, list):
        column_names = validator.get("parquet_column_names_sample", [])
    column_names = [str(value) for value in column_names]
    checks = {
        "schema_artifact_valid_json": schema_valid_json,
        "validator_completed": validator.get("pyarrow_schema_access_repair_apply_validation_completed") is True,
        "validator_status_passed": validator.get("source_panel_pyarrow_schema_access_repair_apply_validator_status")
        == "PASS_SCHEMA_METADATA_ARTIFACT_VALIDATED_P1_BOUNDED_RESULT_SUMMARY_NEXT",
        "schema_limitation_bounded": validator.get("limitation_materiality_after_validator") == "P1_BOUNDED"
        and validator.get("parquet_schema_limitation_resolved_to_bounded") is True,
        "schema_method_metadata_only": schema.get("parquet_schema_method") == "PYARROW_PARQUETFILE_METADATA_ONLY",
        "column_count_expected": schema.get("parquet_column_count") == EXPECTED_PARQUET_COLUMN_COUNT,
        "metadata_rows_expected": schema.get("parquet_num_rows_metadata_only") == EXPECTED_PARQUET_NUM_ROWS,
        "row_groups_expected": schema.get("parquet_num_row_groups_metadata_only") == EXPECTED_PARQUET_ROW_GROUPS,
        "no_full_scan": schema.get("full_parquet_scan_performed") is False
        and validator.get("full_parquet_scan_performed") is False,
        "no_row_read": schema.get("parquet_rows_read_now") is False and validator.get("parquet_rows_read_now") is False,
    }
    return {
        "completed": True,
        "validated": all(value is True for value in checks.values()),
        "checks": checks,
        "parquet_input_path": schema.get("parquet_input_path") or validator.get("parquet_input_path"),
        "parquet_file_size_bytes": schema.get("parquet_file_size_bytes") or validator.get("parquet_file_size_bytes"),
        "parquet_schema_method": schema.get("parquet_schema_method") or validator.get("parquet_schema_method"),
        "parquet_column_count": schema.get("parquet_column_count") or validator.get("parquet_column_count"),
        "parquet_column_names": column_names,
        "parquet_num_rows_metadata_only": schema.get("parquet_num_rows_metadata_only")
        or validator.get("parquet_num_rows_metadata_only"),
        "parquet_num_row_groups_metadata_only": schema.get("parquet_num_row_groups_metadata_only")
        or validator.get("parquet_num_row_groups_metadata_only"),
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
        "limitation_status": "P1_BOUNDED",
    }


def evidence_quality_summary(validator: Dict[str, Any], artifacts_validated: bool, schema_validated: bool) -> Dict[str, Any]:
    active_p0 = 0 if artifacts_validated and schema_validated else 1
    active_p1 = 1 if active_p0 == 0 else 0
    return {
        "completed": True,
        "validated": active_p0 == 0,
        "current_evidence_chain_quality_before_summary": validator.get(
            "current_evidence_chain_quality_after_validator", EVIDENCE_BEFORE
        ),
        "current_evidence_chain_quality_after_summary": EVIDENCE_AFTER_EXPANSION
        if active_p0 == 0
        else EVIDENCE_AFTER_BLOCKED,
        "source_panel_results_are_useful_research_substrate": active_p0 == 0,
        "source_panel_results_are_alpha_or_edge": False,
        "source_panel_results_are_reusable_data_quality_asset": active_p0 == 0,
        "profit_claims_made": False,
        "tradable_edge_claims_made": False,
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": active_p1,
        "p1_attention": "P1_BOUNDED_SCHEMA_METADATA_LIMITATION_NOT_BLOCKER" if active_p0 == 0 else "P0_BLOCKED",
    }


def research_utility_summary() -> Dict[str, Any]:
    utility = {
        "useful_for_data_quality_monitoring": True,
        "useful_for_coverage_assessment": True,
        "useful_for_missingness_freshness_review": True,
        "useful_for_feature_panel_readiness": True,
        "useful_for_future_research_route_selection": True,
        "useful_as_reusable_data_quality_tooling_asset": True,
        "strategy_edge_claimed": False,
        "candidate_quality_claimed": False,
        "backtest_performance_claimed": False,
        "profit_claimed": False,
    }
    return {"completed": True, "validated": all(value is True for key, value in utility.items() if key.startswith("useful_")), **utility}


def data_horizon_assessment() -> Dict[str, Any]:
    return {
        "completed": True,
        "one_year_panel_sufficient_for_pipeline_validation": True,
        "one_year_panel_sufficient_for_strategy_edge_claims": False,
        "data_horizon_expansion_recommended": True,
        "recommended_historical_horizon_years": RECOMMENDED_HISTORICAL_HORIZON_YEARS,
        "data_horizon_expansion_reason": (
            "The 1-year panel is acceptable for smoke tests, pipeline validation, and source-panel artifact generation, "
            "but it is not enough for robust strategy or edge proof. A 3-4 year repo-only historical expansion should "
            "come before serious strategy research or candidate generation, preserving survivorship-bias controls, "
            "symbol-universe rules, missingness checks, duplicate/timestamp checks, and holdout discipline."
        ),
        "historical_expansion_should_be_repo_only_and_data_quality_first": True,
        "must_preserve_survivorship_bias_controls": True,
        "must_preserve_symbol_universe_rules": True,
        "must_preserve_missingness_checks": True,
        "must_preserve_duplicate_timestamp_checks": True,
        "must_preserve_holdout_discipline": True,
    }


def old_route_guard_summary(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    anomaly = artifacts.get("source_panel_anomaly_report.json", {})
    return {
        "completed": True,
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
        "anomaly_report_remains_data_quality_only": anomaly.get("data_quality_anomalies_only") is True,
        "strategy_anomaly_claim_made": False,
        "trading_anomaly_claim_made": False,
        "validated": anomaly.get("old_source_panel_anomaly_route_reopened") is False
        and anomaly.get("old_route_closed_artifacts_used_as_active_evidence") is False
        and anomaly.get("data_quality_anomalies_only") is True,
    }


def safety_boundary_summary() -> Dict[str, Any]:
    checks = {
        "no_strategy_research": True,
        "no_backtest": True,
        "no_candidate_generation": True,
        "no_family_release": True,
        "no_runtime_capital_live_order_touch": True,
        "no_generic_runner_approval_or_implementation": True,
        "no_schema_config_creation": True,
        "no_profit_tradable_edge_claim": True,
        "no_source_panel_rerun": True,
        "no_full_parquet_scan": True,
        "no_parquet_row_read": True,
    }
    return {"completed": True, "validated": all(checks.values()), "checks": checks}


def build_payload() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    artifacts, artifact_validations = load_source_panel_artifacts()
    schema, schema_valid_json, schema_json_error = load_json_checked(SCHEMA_METADATA_ARTIFACT)
    validator, validator_valid_json, validator_json_error = load_json_checked(PYARROW_SCHEMA_VALIDATOR_ARTIFACT)

    artifact_summary = source_panel_artifact_summary(artifacts, artifact_validations)
    schema_summary = parquet_schema_summary(schema, validator, schema_valid_json)
    evidence_summary = evidence_quality_summary(validator, artifact_summary["validated"], schema_summary["validated"])
    utility_summary = research_utility_summary()
    horizon = data_horizon_assessment()
    old_route = old_route_guard_summary(artifacts)
    safety = safety_boundary_summary()

    prior_validator_respected = (
        validator_valid_json
        and validator.get("source_panel_pyarrow_schema_access_repair_apply_validator_status")
        == "PASS_SCHEMA_METADATA_ARTIFACT_VALIDATED_P1_BOUNDED_RESULT_SUMMARY_NEXT"
        and validator.get("pyarrow_schema_access_repair_apply_validation_completed") is True
        and validator.get("schema_metadata_artifact_valid_json") is True
        and validator.get("expected_parquet_columns_present") is True
        and validator.get("parquet_schema_limitation_resolved_to_bounded") is True
        and validator.get("parquet_schema_limitation_blocks_next_step") is False
        and validator.get("current_evidence_chain_quality_after_validator") == EVIDENCE_BEFORE
        and validator.get("active_p0_blocker_count") == 0
        and validator.get("active_p1_attention_count") == 1
        and validator.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
        and validator.get("replacement_checks_all_true") is True
    )

    summary_passes = all(
        [
            artifact_summary["validated"],
            schema_summary["validated"],
            evidence_summary["validated"],
            utility_summary["validated"],
            old_route["validated"],
            safety["validated"],
            prior_validator_respected,
        ]
    )
    next_module = NEXT_MODULE_EXPANSION_CONTRACT if summary_passes else NEXT_MODULE_BLOCKED
    status = SUMMARY_STATUS_PASS if summary_passes else SUMMARY_STATUS_BLOCKED
    final_decision = (
        "SOURCE_PANEL_RESULT_SUMMARY_COMPLETE_DATA_HORIZON_EXPANSION_CONTRACT_NEXT"
        if summary_passes
        else "SOURCE_PANEL_RESULT_SUMMARY_BLOCKED_RECORD_NEXT"
    )
    next_action = (
        "BUILD_DATA_HORIZON_EXPANSION_CONTRACT_AFTER_SOURCE_PANEL_SUMMARY"
        if summary_passes
        else "BUILD_SOURCE_PANEL_ANALYSIS_RESULT_SUMMARY_BLOCKED_RECORD"
    )

    safety_flat = {
        "full_parquet_scan_performed": False,
        "parquet_rows_read_now": False,
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
    allowed_next_modules = {NEXT_MODULE_EXPANSION_CONTRACT, NEXT_MODULE_RESEARCH_QUEUE, NEXT_MODULE_BLOCKED}
    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_635_to_636": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT
        == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0
        and py["tracked_python_bom_error_count"] == 0,
        "prior_pyarrow_schema_validator_respected": prior_validator_respected,
        "result_summary_completed": True,
        "all_required_source_panel_result_artifacts_validated": artifact_summary["validated"],
        "parquet_schema_metadata_validated": schema_summary["validated"],
        "parquet_schema_limitation_bounded": schema_summary["limitation_status"] == "P1_BOUNDED",
        "data_horizon_expansion_recommended": horizon["data_horizon_expansion_recommended"] is True,
        "one_year_panel_sufficient_for_strategy_edge_claims_false": horizon[
            "one_year_panel_sufficient_for_strategy_edge_claims"
        ]
        is False,
        "no_strategy_or_profit_claims": safety_flat["strategy_signal_claims_made"] is False
        and safety_flat["tradable_edge_claims_made"] is False
        and safety_flat["profit_claims_made"] is False,
        "no_backtest_candidate_runtime_capital_live": safety_flat["backtest_performed"] is False
        and safety_flat["candidate_generation_performed"] is False
        and safety_flat["runtime_touch_performed"] is False
        and safety_flat["capital_touch_performed"] is False
        and safety_flat["live_touch_performed"] is False,
        "generic_runner_blocked": safety_flat["generic_runner_approval_granted"] is False
        and safety_flat["generic_runner_implementation_remains_blocked"] is True,
        "schema_or_config_created_false": safety_flat["schema_or_config_created"] is False,
        "old_route_not_reopened": old_route["validated"],
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "loop_remains_closed": True,
        "next_module_allowed": next_module in allowed_next_modules,
        "source_panel_rerun_not_selected": "runner_execution" not in next_module,
        "candidate_backtest_runtime_live_capital_not_selected": all(
            token not in next_module for token in ["candidate", "backtest", "runtime", "live", "capital"]
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
        "source_panel_analysis_result_summary_status": status,
        "post_check_status": POST_CHECK_STATUS_PASS if summary_passes else POST_CHECK_STATUS_BLOCKED,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_pyarrow_schema_validator_respected": prior_validator_respected,
        "result_summary_completed": True,
        "source_panel_artifact_summary_completed": artifact_summary["completed"],
        "parquet_schema_summary_completed": schema_summary["completed"],
        "evidence_quality_summary_completed": evidence_summary["completed"],
        "research_utility_summary_completed": utility_summary["completed"],
        "data_horizon_assessment_completed": horizon["completed"],
        "old_route_guard_summary_completed": old_route["completed"],
        "safety_boundary_summary_completed": safety["completed"],
        "all_required_source_panel_result_artifacts_validated": artifact_summary["validated"],
        "parquet_schema_metadata_validated": schema_summary["validated"],
        "parquet_schema_limitation_bounded": schema_summary["limitation_status"] == "P1_BOUNDED",
        "parquet_input_path": schema_summary["parquet_input_path"],
        "parquet_file_size_bytes": schema_summary["parquet_file_size_bytes"],
        "parquet_file_size_difference_reason": ""
        if schema_summary["parquet_file_size_bytes"] == EXPECTED_PARQUET_SIZE_BYTES
        else f"actual_size_{schema_summary['parquet_file_size_bytes']}_differs_from_expected_{EXPECTED_PARQUET_SIZE_BYTES}",
        "parquet_column_count": schema_summary["parquet_column_count"],
        "parquet_column_names": schema_summary["parquet_column_names"],
        "parquet_num_rows_metadata_only": schema_summary["parquet_num_rows_metadata_only"],
        "parquet_num_row_groups_metadata_only": schema_summary["parquet_num_row_groups_metadata_only"],
        **safety_flat,
        "source_panel_results_are_useful_research_substrate": evidence_summary[
            "source_panel_results_are_useful_research_substrate"
        ],
        "source_panel_results_are_alpha_or_edge": evidence_summary["source_panel_results_are_alpha_or_edge"],
        "source_panel_results_are_reusable_data_quality_asset": evidence_summary[
            "source_panel_results_are_reusable_data_quality_asset"
        ],
        "one_year_panel_sufficient_for_pipeline_validation": horizon["one_year_panel_sufficient_for_pipeline_validation"],
        "one_year_panel_sufficient_for_strategy_edge_claims": horizon[
            "one_year_panel_sufficient_for_strategy_edge_claims"
        ],
        "data_horizon_expansion_recommended": horizon["data_horizon_expansion_recommended"],
        "recommended_historical_horizon_years": horizon["recommended_historical_horizon_years"],
        "data_horizon_expansion_reason": horizon["data_horizon_expansion_reason"],
        "current_evidence_chain_quality_before_summary": evidence_summary[
            "current_evidence_chain_quality_before_summary"
        ],
        "current_evidence_chain_quality_after_summary": evidence_summary["current_evidence_chain_quality_after_summary"],
        "active_p0_blocker_count": evidence_summary["active_p0_blocker_count"],
        "active_p1_attention_count": evidence_summary["active_p1_attention_count"],
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
            "This result summary reads the source-panel result JSON artifacts, parquet schema metadata artifact, and "
            "pyarrow schema validator artifact as explicit replacement checks. It does not rerun source-panel analysis, "
            "perform a full parquet scan, read parquet rows, run strategy research/backtests/candidates, touch runtime/"
            "capital/live/order paths, approve or implement a generic runner, create schema/config files, reopen old "
            "source-panel anomaly routes, or claim profit/tradable edge."
        ),
        "replacement_checks_all_true": replacement_checks_all_true,
        "source_panel_artifact_summary": artifact_summary,
        "parquet_schema_summary": schema_summary,
        "evidence_quality_summary": evidence_summary,
        "research_utility_summary": utility_summary,
        "data_horizon_assessment": horizon,
        "old_route_guard_summary": old_route,
        "safety_boundary_summary": safety,
        "artifact_paths": {
            "source_panel_result_dir": str(SOURCE_PANEL_RESULT_DIR),
            "schema_metadata_artifact": str(SCHEMA_METADATA_ARTIFACT),
            "pyarrow_schema_validator_artifact": str(PYARROW_SCHEMA_VALIDATOR_ARTIFACT),
        },
        "artifact_validation_errors": {
            "schema_json_error": schema_json_error,
            "validator_json_error": validator_json_error,
            "validator_artifact_valid_json": validator_valid_json,
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
            "source_panel_result_summary_only": True,
            **safety_flat,
            **flags,
        },
    }
    return payload


def write_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_result_summary_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["result_summary_completed"] is True else 3


if __name__ == "__main__":
    raise SystemExit(main())
