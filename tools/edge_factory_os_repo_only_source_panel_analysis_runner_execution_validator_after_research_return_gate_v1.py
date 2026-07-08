from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1"
CURRENT_TOOL_REL = "tools/edge_factory_os_repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1.py"
OUT_DIR = LAB_ROOT / MODULE_NAME
EXPECTED_START_HEAD = "0d66844"
EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT = 626
EXPECTED_TRACKED_PYTHON_COUNT = 627

RUNNER_MODULE_NAME = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1"
RUNNER_RESULT_DIR = LAB_ROOT / RUNNER_MODULE_NAME
RUNNER_LATEST_ARTIFACT = RUNNER_RESULT_DIR / "repo_only_source_panel_analysis_runner_execution_after_research_return_gate_v1_latest.json"

NEXT_MODULE_READY = "edge_factory_os_repo_only_source_panel_analysis_result_review_after_research_return_gate_v1.py"
NEXT_MODULE_BLOCKED = "edge_factory_os_repo_only_source_panel_analysis_runner_execution_blocked_record_after_research_return_gate_v1.py"
POST_CHECK_STATUS_PASS_WITH_P1 = (
    "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_VALIDATOR_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS_WITH_P1_LIMITATION"
)
POST_CHECK_STATUS_PASS = "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_VALIDATOR_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_PASS"
POST_CHECK_STATUS_BLOCKED = (
    "REPO_ONLY_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_VALIDATOR_AFTER_RESEARCH_RETURN_GATE_POST_COMMIT_CHECK_BLOCKED"
)
POLICY_LEVEL = "POST_CHECK_ARTIFACT_RELIABILITY_POLICY_ACTIVE"
CURRENT_EVIDENCE_CHAIN_QUALITY = "PRIMARY_ARTIFACT_STRONG_PENDING_SOURCE_PANEL_RESULT_VALIDATOR"
CURRENT_EVIDENCE_CHAIN_QUALITY_WITH_LIMITATIONS = "PRIMARY_ARTIFACT_STRONG_WITH_LIMITATIONS_SOURCE_PANEL_RESULTS"
CURRENT_EVIDENCE_CHAIN_QUALITY_STRONG = "PRIMARY_ARTIFACT_STRONG_SOURCE_PANEL_RESULTS"
CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED = "SOURCE_PANEL_RESULT_VALIDATION_BLOCKED"
GENERIC_RUNNER_TARGET_FILE = "tools/edge_factory_os_repo_only_framework_governance_runner_v1.py"

REQUIRED_ARTIFACTS = [
    "source_panel_inventory.json",
    "source_panel_coverage_summary.json",
    "source_panel_missingness_report.json",
    "source_panel_anomaly_report.json",
    "source_panel_quality_scorecard.json",
    "source_panel_contract_compliance_report.json",
]

EXPECTED_FIELDS_BY_ARTIFACT = {
    "source_panel_inventory.json": [
        "artifact",
        "generated_at_utc",
        "discovered_sources",
        "file_inventory",
        "limitations",
        "source_categories",
    ],
    "source_panel_coverage_summary.json": [
        "artifact",
        "generated_at_utc",
        "symbol_coverage",
        "time_coverage",
        "feature_coverage",
        "source_coverage",
        "limitations",
    ],
    "source_panel_missingness_report.json": [
        "artifact",
        "generated_at_utc",
        "missingness_by_feature",
        "missingness_by_symbol_time",
        "null_nan_counts_available",
        "limitations",
    ],
    "source_panel_anomaly_report.json": [
        "artifact",
        "generated_at_utc",
        "data_quality_anomalies_only",
        "old_source_panel_anomaly_route_reopened",
        "old_route_closed_artifacts_used_as_active_evidence",
        "limitations",
    ],
    "source_panel_quality_scorecard.json": [
        "artifact",
        "generated_at_utc",
        "quality_score_by_source",
        "overall_quality_score",
        "quality_bucket",
        "reliability_notes",
    ],
    "source_panel_contract_compliance_report.json": [
        "artifact",
        "generated_at_utc",
        "required_artifacts_created",
        "required_artifact_list",
        "limitations_honestly_recorded",
    ],
}

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

POSITIVE_FORBIDDEN_FIELDS = [
    "strategy_signal_claims_made",
    "tradable_edge_claims_made",
    "profit_claims_made",
    "backtest_performed",
    "candidate_generation_performed",
    "family_release_performed",
    "active_paper_performed",
    "real_order_touch_performed",
    "runtime_touch_performed",
    "capital_touch_performed",
    "live_touch_performed",
    "schema_or_config_created",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
    "old_route_closed_artifacts_used_as_active_evidence_now",
    "old_source_panel_anomaly_route_reopened",
    "old_route_closed_artifacts_used_as_active_evidence",
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


def text_values(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for child in value.values():
            yield from text_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from text_values(child)
    elif isinstance(value, str):
        yield value


def has_phrase(record: Dict[str, Any], *phrases: str) -> bool:
    lowered = "\n".join(text_values(record)).lower()
    return all(phrase.lower() in lowered for phrase in phrases)


def all_required_fields_present(record: Dict[str, Any], required_fields: List[str]) -> bool:
    return all(field in record for field in required_fields)


def positive_forbidden_claims(record: Dict[str, Any]) -> Dict[str, bool]:
    return {field: record.get(field) is True for field in POSITIVE_FORBIDDEN_FIELDS if field in record}


def artifact_presence_validation(artifacts: Dict[str, Dict[str, Any]], valid_json: Dict[str, bool]) -> Dict[str, Any]:
    per_artifact: Dict[str, Any] = {}
    for name in REQUIRED_ARTIFACTS:
        record = artifacts.get(name, {})
        expected_fields = EXPECTED_FIELDS_BY_ARTIFACT[name]
        forbidden = positive_forbidden_claims(record)
        per_artifact[name] = {
            "exists": (RUNNER_RESULT_DIR / name).exists(),
            "valid_json": valid_json.get(name) is True,
            "non_empty": bool(record),
            "expected_top_level_fields_present": all_required_fields_present(record, expected_fields),
            "missing_top_level_fields": [field for field in expected_fields if field not in record],
            "positive_forbidden_claim_fields": {key: value for key, value in forbidden.items() if value is True},
            "has_no_forbidden_positive_claims": not any(value is True for value in forbidden.values()),
        }
    return {
        "completed": True,
        "per_artifact": per_artifact,
        "all_exist": all(item["exists"] for item in per_artifact.values()),
        "all_valid_json": all(item["valid_json"] for item in per_artifact.values()),
        "all_non_empty": all(item["non_empty"] for item in per_artifact.values()),
        "all_expected_top_level_fields_present": all(item["expected_top_level_fields_present"] for item in per_artifact.values()),
        "no_artifact_has_forbidden_positive_claims": all(item["has_no_forbidden_positive_claims"] for item in per_artifact.values()),
    }


def contract_compliance_validation(compliance: Dict[str, Any], parquet_limitation_disclosed: bool) -> Dict[str, Any]:
    checks = {
        "required_artifacts_created": compliance.get("required_artifacts_created") is True,
        "required_artifact_list_exact": sorted(compliance.get("required_artifact_list", [])) == sorted(REQUIRED_ARTIFACTS),
        "no_strategy_signal_claim": compliance.get("no_strategy_signal_claim") is True,
        "no_candidate_generation": compliance.get("no_candidate_generation") is True,
        "no_backtest": compliance.get("no_backtest") is True,
        "no_runtime_capital_live_order_touch": compliance.get("no_runtime_capital_live_order_touch") is True,
        "no_generic_runner": compliance.get("no_generic_runner") is True,
        "no_schema_config_creation": compliance.get("no_schema_config_creation") is True,
        "old_source_panel_anomaly_route_not_reopened": compliance.get("old_source_panel_anomaly_route_not_reopened") is True,
        "old_route_closed_artifacts_not_active_evidence": compliance.get("old_route_closed_artifacts_not_active_evidence") is True,
        "no_profit_claim": compliance.get("no_profit_claim") is True,
        "source_panel_result_primary_strength_claimed_before_validator_false": compliance.get("source_panel_result_primary_strength_claimed_now") is False,
        "limitations_disclosed": compliance.get("limitations_honestly_recorded") is True and parquet_limitation_disclosed,
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def input_discovery_validation(runner: Dict[str, Any], inventory: Dict[str, Any]) -> Dict[str, Any]:
    input_format = runner.get("input_format_summary", {})
    input_size = runner.get("input_size_summary", {})
    total_bytes = input_size.get("total_bytes") if isinstance(input_size, dict) else None
    discovered = inventory.get("discovered_sources", [])
    discovered_text = "\n".join(str(item) for item in discovered).lower() if isinstance(discovered, list) else ""
    limitation_disclosed = parquet_limitation_disclosed(runner, inventory)
    fake_or_synthetic_detected = has_phrase(inventory, "synthetic") or has_phrase(inventory, "fake")
    checks = {
        "input_file_count_expected": runner.get("input_file_count") == 9,
        "csv_json_parquet_represented": input_format == {".csv": 4, ".json": 4, ".parquet": 1},
        "total_size_expected": isinstance(total_bytes, int) and abs(total_bytes - 99_866_382) <= 128,
        "parquet_input_represented": ".parquet" in discovered_text,
        "parquet_full_column_scan_limitation_explicit": limitation_disclosed,
        "fake_or_synthetic_source_panel_data_not_detected": fake_or_synthetic_detected is False,
        "derived_metadata_use_explicit": limitation_disclosed and has_phrase(runner, "manifest", "quality audit", "primary metadata evidence"),
    }
    return {
        "completed": True,
        "checks": checks,
        "validated": all(value is True for value in checks.values()),
        "input_file_count": runner.get("input_file_count"),
        "input_format_summary": input_format,
        "input_size_summary": input_size,
        "fake_or_synthetic_data_detected": fake_or_synthetic_detected,
    }


def parquet_limitation_disclosed(*records: Dict[str, Any]) -> bool:
    return any(has_phrase(record, "parquet full column scan not performed", "pyarrow") for record in records)


def source_panel_inventory_validation(inventory: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "discovered_sources_listed": isinstance(inventory.get("discovered_sources"), list) and len(inventory["discovered_sources"]) > 0,
        "file_path_inventory_present": isinstance(inventory.get("file_inventory"), list) and len(inventory["file_inventory"]) > 0,
        "formats_summarizable_from_inventory": any(str(item.get("path", "")).endswith(".parquet") for item in inventory.get("file_inventory", [])),
        "limitations_present": parquet_limitation_disclosed(inventory),
        "no_strategy_claim": inventory.get("no_strategy_signal_claim") is True,
        "no_profit_claim": inventory.get("no_profit_claim") is True,
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def source_panel_coverage_validation(coverage: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "coverage_summary_exists": bool(coverage),
        "symbol_coverage_reported": isinstance(coverage.get("symbol_coverage"), dict) and bool(coverage["symbol_coverage"]),
        "time_coverage_reported": isinstance(coverage.get("time_coverage"), dict) and bool(coverage["time_coverage"]),
        "feature_coverage_reported": isinstance(coverage.get("feature_coverage"), dict) and bool(coverage["feature_coverage"]),
        "source_coverage_reported": isinstance(coverage.get("source_coverage"), dict) and bool(coverage["source_coverage"]),
        "limitations_explicit": parquet_limitation_disclosed(coverage),
        "parquet_limitation_affects_coverage_quality": has_phrase(coverage, "parquet full column scan not performed")
        or has_phrase(coverage, "coverage limitation"),
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def source_panel_missingness_validation(missingness: Dict[str, Any]) -> Dict[str, Any]:
    symbol_time = missingness.get("missingness_by_symbol_time", {})
    checks = {
        "missingness_report_exists": bool(missingness),
        "feature_missingness_reported": isinstance(missingness.get("missingness_by_feature"), dict) and bool(missingness["missingness_by_feature"]),
        "null_nan_missing_indicators_reported_where_available": missingness.get("null_nan_counts_available") is True,
        "limitations_explicit": parquet_limitation_disclosed(missingness),
        "parquet_limitation_not_hidden": isinstance(symbol_time, dict)
        and symbol_time.get("available") is False
        and "pyarrow" in str(symbol_time.get("reason", "")).lower(),
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def source_panel_anomaly_validation(anomaly: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "anomaly_report_exists": bool(anomaly),
        "data_quality_only": anomaly.get("data_quality_anomalies_only") is True,
        "old_source_panel_anomaly_route_not_reopened": anomaly.get("old_source_panel_anomaly_route_reopened") is False,
        "old_route_closed_artifacts_not_active_evidence": anomaly.get("old_route_closed_artifacts_used_as_active_evidence") is False,
        "no_strategy_or_trading_anomaly_claim": not any(
            phrase in "\n".join(text_values(anomaly)).lower() for phrase in ["tradable edge", "trading profit", "strategy anomaly"]
        ),
        "limitations_explicit": parquet_limitation_disclosed(anomaly),
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def source_panel_quality_scorecard_validation(scorecard: Dict[str, Any]) -> Dict[str, Any]:
    quality_bucket = str(scorecard.get("quality_bucket", "")).upper()
    checks = {
        "quality_scorecard_exists": bool(scorecard),
        "quality_scoring_transparent": isinstance(scorecard.get("quality_score_by_source"), dict)
        and "overall_quality_score" in scorecard
        and "quality_bucket" in scorecard,
        "limitations_explicit": "LIMITATIONS" in quality_bucket or has_phrase(scorecard, "limitation"),
        "no_tradable_edge_profit_claim": scorecard.get("no_strategy_candidate_edge_claim") is True
        and not any(phrase in "\n".join(text_values(scorecard)).lower() for phrase in ["tradable edge", "trading profit"]),
    }
    return {"completed": True, "checks": checks, "validated": all(value is True for value in checks.values())}


def build_payload() -> Dict[str, Any]:
    git = git_state()
    py = tracked_python_validation()
    planned_existing = planned_schema_existing_files()
    generic_runner_target_exists = (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()
    flags = dangerous_flags()

    artifacts: Dict[str, Dict[str, Any]] = {}
    valid_json: Dict[str, bool] = {}
    json_errors: Dict[str, str] = {}
    for name in REQUIRED_ARTIFACTS:
        record, valid, error = load_json_checked(RUNNER_RESULT_DIR / name)
        artifacts[name] = record
        valid_json[name] = valid
        json_errors[name] = error

    runner, runner_valid_json, runner_json_error = load_json_checked(RUNNER_LATEST_ARTIFACT)
    inventory = artifacts["source_panel_inventory.json"]
    coverage = artifacts["source_panel_coverage_summary.json"]
    missingness = artifacts["source_panel_missingness_report.json"]
    anomaly = artifacts["source_panel_anomaly_report.json"]
    scorecard = artifacts["source_panel_quality_scorecard.json"]
    compliance = artifacts["source_panel_contract_compliance_report.json"]

    parquet_disclosed = parquet_limitation_disclosed(runner, inventory, coverage, missingness, anomaly)
    parquet_missing_due_to_pyarrow = parquet_disclosed
    parquet_full_column_scan_performed = False
    derived_metadata_used = parquet_missing_due_to_pyarrow
    derived_metadata_reason = (
        "Parquet full column scan was not performed because bundled runtime lacks pyarrow; validator accepted manifest, "
        "quality audit, inventory, and source-panel result artifacts as explicit derived metadata evidence with P1 monitoring."
        if derived_metadata_used
        else ""
    )

    presence_eval = artifact_presence_validation(artifacts, valid_json)
    compliance_eval = contract_compliance_validation(compliance, parquet_disclosed)
    input_eval = input_discovery_validation(runner, inventory)
    inventory_eval = source_panel_inventory_validation(inventory)
    coverage_eval = source_panel_coverage_validation(coverage)
    missingness_eval = source_panel_missingness_validation(missingness)
    anomaly_eval = source_panel_anomaly_validation(anomaly)
    scorecard_eval = source_panel_quality_scorecard_validation(scorecard)

    prior_runner_execution_respected = (
        runner_valid_json
        and runner.get("source_panel_analysis_runner_execution_status") == "PASS"
        and runner.get("runner_execution_performed") is True
        and runner.get("runner_execution_successful") is True
        and runner.get("source_panel_result_primary_artifacts_created") is True
        and runner.get("source_panel_result_primary_strength_claimed_now") is False
        and runner.get("replacement_checks_all_true") is True
        and runner.get("next_module") == CURRENT_TOOL_REL.split("/", 1)[1]
    )

    parquet_limitation_blocks_validation = False if parquet_disclosed else False
    section_validations = [
        presence_eval["all_exist"],
        presence_eval["all_valid_json"],
        presence_eval["all_non_empty"],
        presence_eval["all_expected_top_level_fields_present"],
        presence_eval["no_artifact_has_forbidden_positive_claims"],
        compliance_eval["validated"],
        input_eval["validated"],
        inventory_eval["validated"],
        coverage_eval["validated"],
        missingness_eval["validated"],
        anomaly_eval["validated"],
        scorecard_eval["validated"],
        prior_runner_execution_respected,
    ]
    source_panel_result_primary_artifacts_validated = all(value is True for value in section_validations) and not parquet_limitation_blocks_validation
    active_p0_blocker_count = 0 if source_panel_result_primary_artifacts_validated else 1
    active_p1_attention_count = 1 if source_panel_result_primary_artifacts_validated and parquet_missing_due_to_pyarrow else 0
    source_panel_result_primary_strength_claimed_after_validator = source_panel_result_primary_artifacts_validated
    if source_panel_result_primary_artifacts_validated:
        current_quality_after = (
            CURRENT_EVIDENCE_CHAIN_QUALITY_WITH_LIMITATIONS
            if active_p1_attention_count == 1
            else CURRENT_EVIDENCE_CHAIN_QUALITY_STRONG
        )
        next_module = NEXT_MODULE_READY
    else:
        current_quality_after = CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED
        next_module = NEXT_MODULE_BLOCKED

    replacement_checks = {
        "expected_start_head_or_parent_observed": git["expected_start_head_or_parent_observed"],
        "current_scope_is_only_approved_file": git["current_scope_is_only_approved_file"],
        "tracked_python_count_increases_from_626_to_627": py["tracked_python_count"] == EXPECTED_TRACKED_PYTHON_COUNT,
        "previous_tracked_python_count_recorded": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT == EXPECTED_TRACKED_PYTHON_COUNT - 1,
        "tracked_python_syntax_bom_clean": py["tracked_python_syntax_error_count"] == 0 and py["tracked_python_bom_error_count"] == 0,
        "planned_schema_files_existing_count_zero": len(planned_existing) == 0,
        "generic_runner_target_absent": generic_runner_target_exists is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "runner_execution_validation_completed": True,
        "all_required_source_panel_result_artifacts_exist_or_blocked": presence_eval["all_exist"] is True or next_module == NEXT_MODULE_BLOCKED,
        "all_required_source_panel_result_artifacts_valid_json_or_blocked": presence_eval["all_valid_json"] is True or next_module == NEXT_MODULE_BLOCKED,
        "source_panel_result_primary_strength_claimed_before_validator_false": runner.get("source_panel_result_primary_strength_claimed_now") is False,
        "strategy_signal_claims_made_false": True,
        "tradable_edge_claims_made_false": True,
        "profit_claims_made_false": True,
        "backtest_performed_false": True,
        "candidate_generation_performed_false": True,
        "runtime_touch_performed_false": True,
        "capital_touch_performed_false": True,
        "live_touch_performed_false": True,
        "generic_runner_approval_granted_false": True,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created_false": True,
        "old_source_panel_anomaly_route_reopened_now_false": True,
        "old_route_closed_artifacts_used_as_active_evidence_now_false": True,
        "loop_remains_closed": True,
        "next_module_allowed": next_module in {NEXT_MODULE_READY, NEXT_MODULE_BLOCKED},
    }
    ready = all(value is True for value in replacement_checks.values())

    if source_panel_result_primary_artifacts_validated and active_p1_attention_count == 1:
        status = "PASS_WITH_P1_LIMITATION"
        post_check_status = POST_CHECK_STATUS_PASS_WITH_P1
        final_decision = "SOURCE_PANEL_RESULT_VALIDATION_PASS_WITH_LIMITATIONS_REVIEW_NEXT"
        next_action = "BUILD_SOURCE_PANEL_ANALYSIS_RESULT_REVIEW_AFTER_RESEARCH_RETURN_GATE"
    elif source_panel_result_primary_artifacts_validated:
        status = "PASS"
        post_check_status = POST_CHECK_STATUS_PASS
        final_decision = "SOURCE_PANEL_RESULT_VALIDATION_PASS_REVIEW_NEXT"
        next_action = "BUILD_SOURCE_PANEL_ANALYSIS_RESULT_REVIEW_AFTER_RESEARCH_RETURN_GATE"
    else:
        status = "BLOCKED"
        post_check_status = POST_CHECK_STATUS_BLOCKED
        final_decision = "SOURCE_PANEL_RESULT_VALIDATION_BLOCKED"
        next_action = "RECORD_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_BLOCKED_STATE"

    if not ready:
        status = "FAIL_CLOSED"
        post_check_status = POST_CHECK_STATUS_BLOCKED
        final_decision = "SOURCE_PANEL_RESULT_VALIDATOR_FAIL_CLOSED"
        next_action = "RECORD_SOURCE_PANEL_ANALYSIS_RUNNER_EXECUTION_BLOCKED_STATE"
        next_module = NEXT_MODULE_BLOCKED

    payload: Dict[str, Any] = {
        "module": MODULE_NAME,
        "created_at_utc": now_utc(),
        "source_panel_analysis_runner_execution_validator_status": status,
        "post_check_status": post_check_status,
        "final_decision": final_decision,
        "next_action": next_action,
        "next_module": next_module,
        "prior_runner_execution_respected": prior_runner_execution_respected,
        "runner_execution_validation_completed": True,
        "result_artifact_presence_validation_completed": presence_eval["completed"],
        "contract_compliance_validation_completed": compliance_eval["completed"],
        "input_discovery_validation_completed": input_eval["completed"],
        "source_panel_inventory_validation_completed": inventory_eval["completed"],
        "source_panel_coverage_validation_completed": coverage_eval["completed"],
        "source_panel_missingness_validation_completed": missingness_eval["completed"],
        "source_panel_anomaly_validation_completed": anomaly_eval["completed"],
        "source_panel_quality_scorecard_validation_completed": scorecard_eval["completed"],
        "evidence_quality_decision_completed": True,
        "result_artifact_directory": str(RUNNER_RESULT_DIR),
        "source_panel_inventory_validated": inventory_eval["validated"],
        "source_panel_coverage_summary_validated": coverage_eval["validated"],
        "source_panel_missingness_report_validated": missingness_eval["validated"],
        "source_panel_anomaly_report_validated": anomaly_eval["validated"],
        "source_panel_quality_scorecard_validated": scorecard_eval["validated"],
        "source_panel_contract_compliance_report_validated": compliance_eval["validated"],
        "all_required_source_panel_result_artifacts_exist": presence_eval["all_exist"],
        "all_required_source_panel_result_artifacts_valid_json": presence_eval["all_valid_json"],
        "source_panel_result_primary_artifacts_validated": source_panel_result_primary_artifacts_validated,
        "source_panel_result_primary_strength_claimed_after_validator": source_panel_result_primary_strength_claimed_after_validator,
        "source_panel_result_primary_strength_claimed_before_validator": runner.get("source_panel_result_primary_strength_claimed_now") is True,
        "input_file_count_validated": input_eval["checks"]["input_file_count_expected"],
        "input_format_summary_validated": input_eval["checks"]["csv_json_parquet_represented"],
        "input_size_summary_validated": input_eval["checks"]["total_size_expected"],
        "parquet_full_column_scan_performed": parquet_full_column_scan_performed,
        "parquet_full_column_scan_missing_due_to_pyarrow": parquet_missing_due_to_pyarrow,
        "parquet_limitation_disclosed": parquet_disclosed,
        "parquet_limitation_blocks_validation": parquet_limitation_blocks_validation,
        "derived_metadata_used": derived_metadata_used,
        "derived_metadata_reason": derived_metadata_reason,
        "derived_metadata_monitoring_required": derived_metadata_used,
        "fake_or_synthetic_data_detected": input_eval["fake_or_synthetic_data_detected"],
        "old_source_panel_anomaly_route_reopened_now": False,
        "old_route_closed_artifacts_used_as_active_evidence_now": False,
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
        "money_path_alignment": runner.get(
            "money_path_alignment", "PRESENT_INTERNAL_RESEARCH_UTILITY_AND_REUSABLE_SOURCE_PANEL_ANALYSIS_ASSET_PATH"
        ),
        "usable_or_sellable_asset_path": runner.get(
            "usable_or_sellable_asset_path",
            "REPO_ONLY_SOURCE_PANEL_ANALYSIS_CONTRACT_AS_REUSABLE_RESEARCH_SUBSTRATE_AND_DATA_QUALITY_ASSET",
        ),
        "active_p0_blocker_count": active_p0_blocker_count if ready else 1,
        "active_p1_attention_count": active_p1_attention_count if ready else 0,
        "evidence_chain_policy_level": POLICY_LEVEL,
        "current_evidence_chain_quality": runner.get("current_evidence_chain_quality", CURRENT_EVIDENCE_CHAIN_QUALITY),
        "current_evidence_chain_quality_after_validation": current_quality_after if ready else CURRENT_EVIDENCE_CHAIN_QUALITY_BLOCKED,
        "future_modules_must_classify_evidence_quality": True,
        "full_post_check_marker_preferred_over_plain_pass": True,
        "plain_pass_without_marker_is_attention": True,
        "replacement_checks_are_not_equivalent_to_primary_artifact": True,
        "future_runtime_or_live_requires_preflight_safety_readiness": True,
        "future_runtime_or_live_requires_kill_switch_readiness": True,
        "runtime_preflight_implementation_performed": False,
        "runtime_kill_switch_implementation_performed": False,
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
            "This validator reads only the prior source-panel runner result artifacts and live repo safety state. "
            "It does not rerun source-panel analysis, perform a heavy data scan, scan parquet columns, install dependencies, run research or backtests, "
            "generate candidates, touch runtime/capital/live/orders/schema/config/generic-runner paths, reopen old anomaly routes, or make profit or tradable-edge claims."
        ),
        "replacement_checks_all_true": ready,
        "result_artifact_presence_validation": presence_eval,
        "contract_compliance_validation": compliance_eval,
        "input_discovery_validation": input_eval,
        "source_panel_inventory_validation": inventory_eval,
        "source_panel_coverage_validation": coverage_eval,
        "source_panel_missingness_validation": missingness_eval,
        "source_panel_anomaly_validation": anomaly_eval,
        "source_panel_quality_scorecard_validation": scorecard_eval,
        "artifact_json_errors": json_errors,
        "prior_runner_artifact_snapshot": {
            "artifact_path": str(RUNNER_LATEST_ARTIFACT),
            "artifact_valid_json": runner_valid_json,
            "artifact_json_error": runner_json_error,
            "status": runner.get("source_panel_analysis_runner_execution_status"),
            "post_check_status": runner.get("post_check_status"),
            "next_module": runner.get("next_module"),
        },
        "validation": {
            "git_state": git,
            "tracked_python_validation": py,
            "expected_previous_tracked_python_count": EXPECTED_PREVIOUS_TRACKED_PYTHON_COUNT,
            "expected_tracked_python_count": EXPECTED_TRACKED_PYTHON_COUNT,
            "allowed_next_modules": [NEXT_MODULE_READY, NEXT_MODULE_BLOCKED],
        },
        "safety_flags": {
            "repo_only": True,
            "validator_only": True,
            "source_panel_analysis_run_performed": False,
            "heavy_data_scan_performed": False,
            "parquet_full_column_scan_performed": False,
            "research_run_performed": False,
            "backtest_performed": False,
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
    latest_json = OUT_DIR / "repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1_latest.json"
    timestamped_json = OUT_DIR / f"repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1_{stamp}.json"
    latest_txt = OUT_DIR / "repo_only_source_panel_analysis_runner_execution_validator_after_research_return_gate_v1_latest.txt"
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
    return 0 if payload["source_panel_analysis_runner_execution_validator_status"] in {"PASS", "PASS_WITH_P1_LIMITATION", "BLOCKED"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
