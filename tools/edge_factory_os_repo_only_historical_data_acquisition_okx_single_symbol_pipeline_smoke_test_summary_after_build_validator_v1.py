from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
LAB_ROOT = REPO_ROOT.parent
MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_"
    "after_build_validator_v1"
)
CURRENT_TOOL_REL = (
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_"
    "after_build_validator_v1.py"
)
OUT_DIR = LAB_ROOT / MODULE_NAME

EXPECTED_HEAD = "59442a9"
EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT = 686
EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT = 687

REQUESTED_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_"
    "after_build_validator_v1.py"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_download_preview_"
    "after_smoke_test_summary_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_"
    "blocked_record_after_build_validator_v1.py"
)

VALIDATOR_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1"
)
VALIDATOR_LATEST_ARTIFACT = (
    VALIDATOR_DIR
    / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_after_execution_v1_latest.json"
)
VALIDATOR_BUNDLE_ARTIFACT = VALIDATOR_DIR / "historical_okx_single_symbol_1m_to_1h_build_execution_validator.json"
OUTPUT_VALIDATION_REPORT_ARTIFACT = VALIDATOR_DIR / "historical_okx_single_symbol_1m_to_1h_output_validation_report.json"
NUMERIC_SANITY_REPORT_ARTIFACT = VALIDATOR_DIR / "historical_okx_single_symbol_1m_to_1h_output_numeric_sanity_report.json"
PROVENANCE_VALIDATION_REPORT_ARTIFACT = (
    VALIDATOR_DIR / "historical_okx_single_symbol_1m_to_1h_output_provenance_validation_report.json"
)

BUILD_EXECUTION_DIR = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_after_preview_approval_v1"
)
BUILD_EXECUTION_REPORT_ARTIFACT = BUILD_EXECUTION_DIR / "historical_okx_single_symbol_1m_to_1h_build_execution_report.json"
BUILD_PREVIEW_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_preview_after_download_validator_v1_latest.json"
)
DOWNLOAD_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1"
    / "repo_only_historical_data_acquisition_okx_single_symbol_smoke_test_download_execution_validator_after_execution_v1_latest.json"
)
POLICY_VALIDATOR_ARTIFACT = (
    LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1"
    / "repo_only_historical_data_acquisition_okx_1m_to_1h_aggregation_policy_validator_after_creation_v1_latest.json"
)

VALIDATOR_STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SMOKE_TEST_"
    "SUMMARY_READY"
)
STATUS_PASS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_CLOSED_SMALL_RANGE_DOWNLOAD_"
    "PREVIEW_READY"
)
STATUS_BLOCKED_CONTEXT = "BLOCKED_CONTEXT_MISMATCH"
STATUS_BLOCKED_NEXT_MODULE = "BLOCKED_NEXT_MODULE_MISMATCH"

EVIDENCE_BEFORE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SMOKE_TEST_SUMMARY_READY"
)
EVIDENCE_AFTER = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_PIPELINE_SMOKE_TEST_CLOSED_SMALL_RANGE_DOWNLOAD_PREVIEW_READY"
)

TARGET_SYMBOL = "BTC-USDT-SWAP"
SOURCE_TYPE = "OKX_SINGLE_APPROVED_SAMPLE_ZIP"
INPUT_INTERVAL = "1m"
OUTPUT_INTERVAL = "1h"
SOURCE_ROW_COUNT = 1440
OUTPUT_1H_ROW_COUNT = 24
SUGGESTED_RANGE_DAYS = 7
MAX_ALLOWED_FILES_FOR_FIRST_RANGE_TEST = 7
RECOMMENDED_NEXT_ROUTE = "SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_PREVIEW"
ROUTE_TYPE = "SINGLE_SYMBOL_SMALL_RANGE_PIPELINE_EXPANSION_PREVIEW"
ROUTE_PURPOSE = "PIPELINE_RANGE_VALIDATION_ONLY_NOT_RESEARCH_NOT_EDGE"
PIPELINE_STAGE_VALIDATED = "SINGLE_FILE_DOWNLOAD_TO_1H_OUTPUT_PIPELINE_SMOKE_TEST"

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
DANGEROUS_FLAG_NAMES = [
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
    "schema_file_creation_performed_now",
    "schema_file_edit_performed_now",
    "schema_apply_performed_now",
    "external_download_performed_now",
    "external_api_call_performed_now",
    "data_build_performed_now",
    "aggregation_performed_now",
    "okx_browse_performed_now",
    "okx_download_performed_now",
    "okx_api_call_performed_now",
    "okx_sample_zip_downloaded_now",
    "okx_page_reopened_now",
    "source_manifest_created_now",
    "repo_schema_config_created_now",
    "generic_runner_approval_granted",
    "old_source_panel_anomaly_route_reopened_now",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: List[str]) -> str:
    allowed = (
        ["rev-parse", "--short", "HEAD"],
        ["status", "--short"],
        ["ls-files"],
    )
    if args not in allowed:
        raise RuntimeError(f"unsafe git metadata command refused: {args}")
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", "-C", str(REPO_ROOT)] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def read_json_checked(path: Path) -> Tuple[Dict[str, Any], bool, bool, bool]:
    exists = path.exists()
    if not exists:
        return {}, False, False, False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}, True, False, False
    return data, True, True, isinstance(data, dict) and bool(data)


def load_json(path: Path, label: str) -> Dict[str, Any]:
    data, exists, valid, non_empty = read_json_checked(path)
    if not (exists and valid and non_empty):
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
    return data


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_equal(actual: Any, expected: Any, field: str, status: str = STATUS_BLOCKED_CONTEXT) -> None:
    if actual != expected:
        raise RuntimeError(f"{status}: {field}={actual!r} expected {expected!r}")


def require_true(actual: Any, field: str) -> None:
    if actual is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be true, got {actual!r}")


def require_false(actual: Any, field: str) -> None:
    if actual is not False:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {field} must be false, got {actual!r}")


def normalize_status_lines(status: str) -> List[str]:
    return [line.strip() for line in status.splitlines() if line.strip()]


def validate_repo_status_allows_current_tool_only(status: str) -> None:
    allowed = {f"?? {CURRENT_TOOL_REL}", f"A  {CURRENT_TOOL_REL}", f"AM {CURRENT_TOOL_REL}"}
    unexpected = [line for line in normalize_status_lines(status) if line not in allowed]
    if unexpected:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: repo dirty outside approved tool: {unexpected}")


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def planned_schema_files_existing_count() -> int:
    return sum(1 for rel_path in PLANNED_SCHEMA_REL_PATHS if (REPO_ROOT / rel_path).exists())


def generic_runner_target_exists() -> bool:
    return (REPO_ROOT / GENERIC_RUNNER_TARGET_FILE).exists()


def dangerous_flags() -> Dict[str, bool]:
    return {name: False for name in DANGEROUS_FLAG_NAMES}


def validate_no_true_dangerous_flags(data: Dict[str, Any], artifact_name: str) -> None:
    true_flags = [name for name, value in data.get("dangerous_flags", {}).items() if value is True]
    if true_flags:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {artifact_name} dangerous flags true: {true_flags}")


def load_required_artifacts() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    paths = {
        "validator_latest": VALIDATOR_LATEST_ARTIFACT,
        "validator_bundle": VALIDATOR_BUNDLE_ARTIFACT,
        "output_validation_report": OUTPUT_VALIDATION_REPORT_ARTIFACT,
        "numeric_sanity_report": NUMERIC_SANITY_REPORT_ARTIFACT,
        "provenance_validation_report": PROVENANCE_VALIDATION_REPORT_ARTIFACT,
        "build_execution_report": BUILD_EXECUTION_REPORT_ARTIFACT,
        "build_preview": BUILD_PREVIEW_ARTIFACT,
        "download_validator": DOWNLOAD_VALIDATOR_ARTIFACT,
        "policy_validator": POLICY_VALIDATOR_ARTIFACT,
    }
    artifacts: Dict[str, Dict[str, Any]] = {}
    status: Dict[str, Any] = {
        "required_artifact_paths": {label: str(path) for label, path in paths.items()},
        "artifact_exists_by_label": {},
        "artifact_valid_json_by_label": {},
    }
    for label, path in paths.items():
        data, exists, valid, non_empty = read_json_checked(path)
        status["artifact_exists_by_label"][label] = exists
        status["artifact_valid_json_by_label"][label] = valid and non_empty
        if not (exists and valid and non_empty):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: {label} missing/invalid/empty: {path}")
        artifacts[label] = data
    status["summary_input_artifacts_exist"] = all(status["artifact_exists_by_label"].values())
    status["summary_input_artifacts_valid_json"] = all(status["artifact_valid_json_by_label"].values())
    return artifacts, status


def validate_preflight(artifacts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require_equal(head, EXPECTED_HEAD, "HEAD")
    validate_repo_status_allows_current_tool_only(run_git(["status", "--short"]))

    validator = artifacts["validator_latest"]
    bundle = artifacts["validator_bundle"]
    output = artifacts["output_validation_report"]
    numeric = artifacts["numeric_sanity_report"]
    provenance = artifacts["provenance_validation_report"]
    execution_report = artifacts["build_execution_report"]
    preview = artifacts["build_preview"]
    download_validator = artifacts["download_validator"]
    policy_validator = artifacts["policy_validator"]

    require_equal(
        validator.get("historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_validator_status"),
        VALIDATOR_STATUS_PASS,
        "validator.status",
    )
    require_equal(validator.get("next_module"), REQUESTED_MODULE, "validator.next_module", STATUS_BLOCKED_NEXT_MODULE)
    require_equal(
        bundle.get("next_module_decision", {}).get("next_module"),
        REQUESTED_MODULE,
        "validator_bundle.next_module",
        STATUS_BLOCKED_NEXT_MODULE,
    )

    require_true(validator.get("build_execution_validated"), "validator.build_execution_validated")
    require_true(output.get("output_csv_exists"), "output.output_csv_exists")
    require_equal(output.get("output_csv_row_count"), OUTPUT_1H_ROW_COUNT, "output.output_csv_row_count")
    require_true(output.get("output_schema_validated"), "output.output_schema_validated")
    require_equal(output.get("output_observed_symbol"), TARGET_SYMBOL, "output.output_observed_symbol")
    require_equal(output.get("output_unique_hour_count"), OUTPUT_1H_ROW_COUNT, "output.output_unique_hour_count")
    require_equal(output.get("output_missing_hour_count"), 0, "output.output_missing_hour_count")
    require_equal(output.get("output_duplicate_hour_count"), 0, "output.output_duplicate_hour_count")
    require_true(output.get("output_all_source_row_count_60"), "output.output_all_source_row_count_60")
    require_true(output.get("output_all_complete_hour_true"), "output.output_all_complete_hour_true")
    require_true(validator.get("all_hours_complete"), "validator.all_hours_complete")
    require_false(validator.get("synthetic_fill_used"), "validator.synthetic_fill_used")
    require_false(validator.get("forward_fill_used"), "validator.forward_fill_used")
    require_false(validator.get("backfill_used"), "validator.backfill_used")
    require_true(numeric.get("numeric_sanity_validated"), "numeric.numeric_sanity_validated")
    require_equal(numeric.get("invalid_numeric_row_count"), 0, "numeric.invalid_numeric_row_count")
    require_equal(numeric.get("negative_volume_row_count"), 0, "numeric.negative_volume_row_count")
    require_equal(numeric.get("nan_inf_row_count"), 0, "numeric.nan_inf_row_count")
    require_true(provenance.get("provenance_validated"), "provenance.provenance_validated")
    require_true(validator.get("output_valid_for_pipeline_smoke_test"), "validator.pipeline_smoke_test")
    require_false(validator.get("output_valid_for_research_backtest"), "validator.research_backtest")
    require_false(validator.get("output_valid_for_edge_claim"), "validator.edge_claim")
    require_false(validator.get("safe_for_broad_acquisition"), "validator.broad_acquisition")
    require_false(validator.get("safe_for_multi_symbol_build"), "validator.multi_symbol")
    require_equal(validator.get("validator_p0_count"), 0, "validator.p0_count")
    require_equal(validator.get("active_p0_blocker_count"), 0, "validator.active_p0")
    require_true(int(validator.get("active_p1_attention_count", 0)) >= 8, "validator.active_p1")
    require_equal(validator.get("dormant_repo_attention_count"), 716, "validator.dormant_attention")
    require_false(validator.get("new_download_performed_by_validator"), "validator.new_download")
    require_false(validator.get("data_build_performed_by_validator"), "validator.data_build")
    require_false(validator.get("aggregation_performed_by_validator"), "validator.aggregation")
    require_false(validator.get("okx_api_call_performed"), "validator.api")
    require_false(validator.get("okx_browse_performed"), "validator.browse")
    require_true(validator.get("generic_runner_implementation_remains_blocked"), "validator.generic_runner_blocked")
    require_false(validator.get("schema_or_config_created"), "validator.schema_or_config_created")
    validate_no_true_dangerous_flags(validator, "validator")

    execution_scope = execution_report.get("execution_scope", {})
    aggregation_execution = execution_report.get("aggregation_execution", {})
    require_true(execution_scope.get("build_execution_performed"), "execution_report.build_execution_performed")
    require_equal(execution_scope.get("target_symbol"), TARGET_SYMBOL, "execution_report.target_symbol")
    require_false(execution_scope.get("new_download_performed"), "execution_report.new_download")
    require_false(execution_scope.get("api_call_performed"), "execution_report.api")
    require_false(execution_scope.get("browse_performed"), "execution_report.browse")
    require_equal(aggregation_execution.get("output_1h_row_count"), OUTPUT_1H_ROW_COUNT, "execution_report.output_rows")
    require_true(aggregation_execution.get("all_hours_complete"), "execution_report.all_hours_complete")

    require_equal(
        preview.get("next_module"),
        "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_1m_to_1h_build_execution_after_preview_approval_v1.py",
        "preview.next_module",
    )
    require_true(download_validator.get("safe_for_single_file_pipeline_build_preview"), "download_validator.safe_preview")
    require_true(policy_validator.get("okx_1m_to_1h_aggregation_policy_validated"), "policy_validator.validated")
    require_false(policy_validator.get("policy_execution_allowed_now"), "policy_validator.execution_allowed")

    return {
        "head": head,
        "whole_system_preflight_completed": True,
        "live_next_module_matches_requested_module": True,
        "artifact_chain_consistent": True,
        "stale_or_contradictory_artifact_detected": False,
    }


def build_sections(validator: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    smoke_test_success_summary = {
        "smoke_test_summary_created": True,
        "smoke_test_closed_successfully": True,
        "target_symbol": TARGET_SYMBOL,
        "source_type": SOURCE_TYPE,
        "input_interval": INPUT_INTERVAL,
        "output_interval": OUTPUT_INTERVAL,
        "source_row_count": SOURCE_ROW_COUNT,
        "output_1h_row_count": OUTPUT_1H_ROW_COUNT,
        "complete_1h_row_count": OUTPUT_1H_ROW_COUNT,
        "all_hours_complete": True,
        "output_schema_validated": True,
        "numeric_sanity_validated": True,
        "provenance_validated": True,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "pipeline_stage_validated": PIPELINE_STAGE_VALIDATED,
    }
    limitations_report = {
        "output_valid_for_pipeline_smoke_test": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
        "symbol_universe_still_unresolved": True,
        "coverage_still_unresolved": True,
        "provenance_still_single_file_only": True,
        "source_manifest_still_placeholder": True,
        "three_year_horizon_not_built": True,
        "four_year_gap_still_recorded": True,
        "active_p1_attention_count": max(8, int(validator.get("active_p1_attention_count", 8))),
    }
    next_expansion_route_decision = {
        "next_expansion_route_decision_created": True,
        "recommended_next_route": RECOMMENDED_NEXT_ROUTE,
        "reason": [
            "single file pipeline passed",
            "next safest step is not broad acquisition",
            "next safest step is a small date range for the same symbol to test URL generation, range manifest, and download validation",
            "no download should happen in this summary",
            "future preview must define exact date count, file count, URL pattern, output directory, resource limits, and fail-closed rules",
            "future execution must remain separate and approved",
        ],
        "recommended_target_symbol": TARGET_SYMBOL,
        "target_symbol": TARGET_SYMBOL,
        "route_type": ROUTE_TYPE,
        "suggested_range_days": SUGGESTED_RANGE_DAYS,
        "max_allowed_files_for_first_range_test": MAX_ALLOWED_FILES_FOR_FIRST_RANGE_TEST,
        "output_target_interval": OUTPUT_INTERVAL,
        "input_interval": INPUT_INTERVAL,
        "purpose": ROUTE_PURPOSE,
        "no_broad_acquisition": True,
        "no_strategy_backtest_edge_claim": True,
        "next_route_is_preview_only": True,
        "next_route_requires_separate_execution_approval": True,
    }
    fail_closed_policy = {
        "future_small_range_preview_execution_must_fail_closed_if": [
            "scope exceeds one symbol",
            "scope exceeds approved day/file count",
            "URL pattern ambiguous",
            "any non-approved URL is used in execution",
            "download path outside output directory",
            "source ZIP hash missing after download",
            "schema mismatch",
            "missing days/files not handled",
            "aggregation creates incomplete hours as complete",
            "synthetic fill is used",
            "output is marked research/backtest/edge-ready",
            "runtime/capital/live path touched",
        ],
        "broad_acquisition_must_remain_blocked": True,
        "download_execution_must_be_separate": True,
    }
    return {
        "smoke_test_success_summary": smoke_test_success_summary,
        "limitations_report": limitations_report,
        "next_expansion_route_decision": next_expansion_route_decision,
        "fail_closed_policy": fail_closed_policy,
    }


def build_payload(
    artifacts: Dict[str, Dict[str, Any]],
    artifact_status: Dict[str, Any],
    preflight: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    validator = artifacts["validator_latest"]
    sections = build_sections(validator)
    flags = dangerous_flags()
    active_p1 = max(8, int(validator.get("active_p1_attention_count", 8)))
    smoke = sections["smoke_test_success_summary"]
    limitations = sections["limitations_report"]
    route = sections["next_expansion_route_decision"]
    replacement_checks = {
        "preflight_passed": preflight["whole_system_preflight_completed"] is True,
        "artifact_chain_consistent": preflight["artifact_chain_consistent"] is True,
        "input_artifacts_valid": artifact_status["summary_input_artifacts_exist"] is True
        and artifact_status["summary_input_artifacts_valid_json"] is True,
        "smoke_test_closed": smoke["smoke_test_closed_successfully"] is True,
        "limitations_preserved": limitations["output_valid_for_research_backtest"] is False
        and limitations["output_valid_for_edge_claim"] is False
        and limitations["safe_for_broad_acquisition"] is False
        and limitations["safe_for_multi_symbol_build"] is False,
        "next_route_preview_only": route["recommended_next_route"] == RECOMMENDED_NEXT_ROUTE
        and route["next_route_is_preview_only"] is True
        and route["next_route_requires_separate_execution_approval"] is True,
        "no_download_api_browse_build_aggregation": True,
        "not_research_backtest_edge": True,
        "schema_config_absent": planned_schema_files_existing_count() == 0,
        "generic_runner_absent": generic_runner_target_exists() is False,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
    }
    payload: Dict[str, Any] = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_status": STATUS_PASS,
        "final_decision": EVIDENCE_AFTER,
        "next_action": "PREVIEW_SINGLE_SYMBOL_SMALL_RANGE_DOWNLOAD_NO_EXECUTION",
        "next_module": NEXT_MODULE_PASS,
        **preflight,
        **artifact_status,
        **smoke,
        **limitations,
        **route,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
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
        "schema_or_config_created": False,
        "current_evidence_chain_quality_before_summary": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_summary": EVIDENCE_AFTER,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": active_p1,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": all(value is False for value in flags.values()),
        "dangerous_flags_true_count": sum(1 for value in flags.values() if value),
        "derived_live_repo_post_check": STATUS_PASS,
        "derived_live_repo_post_check_reason": (
            "closed the validated BTC-USDT-SWAP single-file OKX 1m-to-1h pipeline smoke test using JSON artifacts only; "
            "preserved the limitation that the output is smoke-test-only, not research/backtest/edge-ready, kept broad "
            "and multi-symbol acquisition blocked, and selected a separate single-symbol seven-day small-range download "
            "preview as the next safe route without performing any download, API call, browse, CSV/ZIP/parquet read, "
            "data build, aggregation, strategy, backtest, candidate, runtime, capital, live, schema/config, or generic-runner action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": all(replacement_checks.values()),
        "tracked_python_count_current_pre_commit": tracked_python_count(),
        "tracked_python_count_expectation": {
            "pre_commit": EXPECTED_TRACKED_PYTHON_COUNT_PRE_COMMIT,
            "after_commit": EXPECTED_TRACKED_PYTHON_COUNT_POST_COMMIT,
        },
    }
    if payload["replacement_checks_all_true"] is not True:
        raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: replacement checks failed")

    self_validator = {
        "generated_at_utc": utc_now(),
        "all_summary_artifacts_exist": True,
        "all_summary_artifacts_valid_json": True,
        "smoke_test_closed_successfully": True,
        "limitations_preserved": True,
        "next_route_is_preview_only": True,
        "no_new_download_api_browse_build_aggregation_occurred": True,
        "no_readiness_overclaim_occurred": True,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": active_p1,
        "dormant_repo_attention_count": 716,
        "replacement_checks_all_true": True,
    }
    sections["self_validator"] = self_validator
    return payload, sections


def write_artifacts(payload: Dict[str, Any], sections: Dict[str, Dict[str, Any]]) -> None:
    outputs = {
        "historical_okx_single_symbol_pipeline_smoke_test_summary.json": sections["smoke_test_success_summary"],
        "historical_okx_single_symbol_pipeline_smoke_test_closure_record.json": {
            "generated_at_utc": utc_now(),
            "smoke_test_closed_successfully": True,
            "pipeline_stage_validated": PIPELINE_STAGE_VALIDATED,
            "current_evidence_chain_quality_after_summary": EVIDENCE_AFTER,
            "summary": payload,
        },
        "historical_okx_single_symbol_pipeline_smoke_test_limitations_report.json": sections["limitations_report"],
        "historical_okx_next_expansion_route_decision_after_smoke_test.json": sections[
            "next_expansion_route_decision"
        ],
        "historical_okx_single_symbol_pipeline_smoke_test_summary_self_validator.json": sections["self_validator"],
        "historical_okx_single_symbol_pipeline_smoke_test_summary_bundle_summary.json": {
            "generated_at_utc": utc_now(),
            "smoke_test_success_summary": sections["smoke_test_success_summary"],
            "limitations_report": sections["limitations_report"],
            "next_expansion_route_decision": sections["next_expansion_route_decision"],
            "fail_closed_policy": sections["fail_closed_policy"],
            "self_validator": sections["self_validator"],
            "summary": payload,
        },
        "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1_latest.json": payload,
    }
    for name, artifact in outputs.items():
        write_json(OUT_DIR / name, artifact)

    required = [
        "historical_okx_single_symbol_pipeline_smoke_test_summary.json",
        "historical_okx_single_symbol_pipeline_smoke_test_closure_record.json",
        "historical_okx_single_symbol_pipeline_smoke_test_limitations_report.json",
        "historical_okx_next_expansion_route_decision_after_smoke_test.json",
        "historical_okx_single_symbol_pipeline_smoke_test_summary_self_validator.json",
        "historical_okx_single_symbol_pipeline_smoke_test_summary_bundle_summary.json",
    ]
    for name in required:
        data, exists, valid, non_empty = read_json_checked(OUT_DIR / name)
        if not (exists and valid and non_empty and isinstance(data, dict)):
            raise RuntimeError(f"{STATUS_BLOCKED_CONTEXT}: generated artifact failed self-validation: {name}")


def blocked_payload(exc: Exception) -> Dict[str, Any]:
    flags = dangerous_flags()
    message = str(exc)
    blocked_status = STATUS_BLOCKED_NEXT_MODULE if STATUS_BLOCKED_NEXT_MODULE in message else STATUS_BLOCKED_CONTEXT
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_status": blocked_status,
        "final_decision": blocked_status,
        "next_action": "STOP_FAIL_CLOSED_NO_SMOKE_TEST_SUMMARY_ROUTE_DECISION",
        "next_module": NEXT_MODULE_BLOCKED,
        "error": message,
        "whole_system_preflight_completed": False,
        "live_next_module_matches_requested_module": False,
        "artifact_chain_consistent": False,
        "stale_or_contradictory_artifact_detected": True,
        "smoke_test_summary_created": False,
        "smoke_test_closed_successfully": False,
        "target_symbol": TARGET_SYMBOL,
        "input_interval": INPUT_INTERVAL,
        "output_interval": OUTPUT_INTERVAL,
        "source_row_count": 0,
        "output_1h_row_count": 0,
        "complete_1h_row_count": 0,
        "all_hours_complete": False,
        "output_schema_validated": False,
        "numeric_sanity_validated": False,
        "provenance_validated": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_valid_for_pipeline_smoke_test": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
        "symbol_universe_still_unresolved": True,
        "coverage_still_unresolved": True,
        "provenance_still_single_file_only": True,
        "source_manifest_still_placeholder": True,
        "three_year_horizon_not_built": True,
        "four_year_gap_still_recorded": True,
        "next_expansion_route_decision_created": False,
        "recommended_next_route": "",
        "recommended_target_symbol": TARGET_SYMBOL,
        "suggested_range_days": 0,
        "max_allowed_files_for_first_range_test": 0,
        "next_route_is_preview_only": False,
        "next_route_requires_separate_execution_approval": False,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_sample_zip_downloaded_now": False,
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
        "schema_or_config_created": False,
        "current_evidence_chain_quality_before_summary": EVIDENCE_BEFORE,
        "current_evidence_chain_quality_after_summary": blocked_status,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "planned_schema_files_existing_count": planned_schema_files_existing_count(),
        "generic_runner_target_exists": generic_runner_target_exists(),
        "dangerous_flags": flags,
        "dangerous_flags_all_false": True,
        "dangerous_flags_true_count": 0,
        "derived_live_repo_post_check": blocked_status,
        "derived_live_repo_post_check_reason": message,
        "replacement_checks_all_true": False,
    }


def main() -> int:
    try:
        artifacts, artifact_status = load_required_artifacts()
        preflight = validate_preflight(artifacts)
        payload, sections = build_payload(artifacts, artifact_status, preflight)
        write_artifacts(payload, sections)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = blocked_payload(exc)
        write_json(
            OUT_DIR
            / "repo_only_historical_data_acquisition_okx_single_symbol_pipeline_smoke_test_summary_after_build_validator_v1_latest.json",
            payload,
        )
        write_json(OUT_DIR / "historical_okx_single_symbol_pipeline_smoke_test_summary_bundle_summary.json", payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
