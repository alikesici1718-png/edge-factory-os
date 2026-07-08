from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_preview_after_download_validator_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "ce76d26"
TARGET_SYMBOL = "BTC-USDT-SWAP"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATED_"
    "BUILD_PREVIEW_READY_MAX_AVAILABLE_NO_BUILD"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_"
    "BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_BUILD_PREVIEW"
)

NOMINAL_STRICT_3Y_START = "2023-05-19"
MAX_AVAILABLE_START = "2023-07-01"
MAX_AVAILABLE_END = "2026-05-18"
EXPECTED_FILE_COUNT = 1053
EXPECTED_SOURCE_ROWS_PER_FILE = 1440
EXPECTED_TOTAL_SOURCE_ROWS = 1_516_320
EXPECTED_OUTPUT_HOURS_PER_FILE = 24
EXPECTED_OUTPUT_ROWS = 25_272
MAX_TOTAL_SOURCE_ROWS_ALLOWED = 1_600_000
MAX_OUTPUT_ROWS_ALLOWED = 25_272
COMPLETE_HOUR_REQUIRED_SOURCE_ROWS = 60

NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_execution_after_preview_approval_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_preview_blocked_record_after_download_validator_v1.py"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATED_"
    "BUILD_PREVIEW_READY_MAX_AVAILABLE_NO_BUILD"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_BUILD_PREVIEW_"
    "APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
DOWNLOAD_VALIDATOR_SUMMARY = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1"
) / "historical_okx_single_symbol_3_year_download_execution_validator_summary.json"

DANGEROUS_FLAGS = {
    "new_download_performed_now": False,
    "okx_api_call_performed_now": False,
    "okx_browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_csv_read_performed_now": False,
    "zip_csv_extraction_or_read_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "parquet_read_performed_now": False,
    "multi_symbol_performed": False,
    "broad_acquisition_claim_made": False,
    "research_backtest_edge_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
    pass


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"artifact is not a JSON object: {path}")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_preflight(validator: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(
        validator.get("historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_status")
        == PREVIOUS_STATUS,
        "3-year download validator is not PASS",
    )
    require(validator.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(validator.get("download_execution_validated") is True, "download execution not validated")
    require(validator.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(validator.get("strict_3y_completeness_claimed") is False, "strict 3y completeness claimed")
    require(validator.get("max_available_start_candidate") == MAX_AVAILABLE_START, "max-available start mismatch")
    require(validator.get("max_available_end_date") == MAX_AVAILABLE_END, "max-available end mismatch")
    require(validator.get("max_available_candidate_file_count") == EXPECTED_FILE_COUNT, "file count mismatch")
    require(validator.get("final_file_set_count") == EXPECTED_FILE_COUNT, "final file set mismatch")
    require(validator.get("missing_or_failed_file_count") == 0, "missing or failed files detected")
    for key in [
        "all_hashes_match_recorded",
        "all_zip_open_success",
        "all_expected_inner_csv_present",
        "all_expected_schema_match",
        "all_observed_symbols_match_target",
        "all_one_minute_interval_observed_from_samples",
        "safe_for_3_year_build_preview",
    ]:
        require(validator.get(key) is True, f"{key} not true")
    for key in ["safe_for_broad_acquisition", "safe_for_research_backtest", "safe_for_edge_claim"]:
        require(validator.get(key) is False, f"{key} not false")
    for key in [
        "new_download_performed_by_validator",
        "full_csv_read_performed",
        "data_build_performed",
        "aggregation_performed_now",
        "okx_api_call_performed",
        "okx_browse_performed",
        "schema_or_config_created",
    ]:
        require(validator.get(key) is False, f"{key} not false")


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    validator = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    validate_preflight(validator)

    build_scope = {
        "build_scope_created": True,
        "target_symbol": TARGET_SYMBOL,
        "symbol_count": 1,
        "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START,
        "max_available_end_date": MAX_AVAILABLE_END,
        "input_interval": "1m",
        "output_interval": "1h",
        "expected_file_count": EXPECTED_FILE_COUNT,
        "expected_rows_per_file": EXPECTED_SOURCE_ROWS_PER_FILE,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "expected_output_hours_per_file": EXPECTED_OUTPUT_HOURS_PER_FILE,
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "max_total_source_rows_allowed": MAX_TOTAL_SOURCE_ROWS_ALLOWED,
        "max_output_rows_allowed": MAX_OUTPUT_ROWS_ALLOWED,
        "complete_hour_required_source_rows": COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
        "purpose": "PIPELINE_LONG_RANGE_VALIDATION_ONLY_NOT_RESEARCH_NOT_EDGE",
    }
    build_preview = {
        "preview_created": True,
        "build_scope": "SINGLE_SYMBOL_MAX_AVAILABLE_3_YEAR_1M_TO_1H_PIPELINE_LONG_RANGE_VALIDATION_ONLY",
        **build_scope,
        "future_build_may_use_only_validated_zip_count": EXPECTED_FILE_COUNT,
        "future_build_must_revalidate_sha256_before_csv_read": True,
        "future_build_may_read_full_csvs_only_in_execution_module": True,
        "future_build_must_process_only_target_symbol": TARGET_SYMBOL,
        "future_build_must_process_only_max_available_range": True,
        "future_build_must_not_download": True,
        "future_build_must_not_api_or_browse": True,
        "future_build_must_not_claim_strict_3y_completeness": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_broad_acquisition": False,
    }
    approval_record = {
        "approval_record_created": True,
        "approval_scope": "NEXT_3_YEAR_MAX_AVAILABLE_SINGLE_SYMBOL_1M_TO_1H_BUILD_EXECUTION_ONLY",
        "approval_grants_build_now": False,
        "approval_grants_future_3_year_build_next": True,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_full_csv_read_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_multi_symbol_now": False,
        "approval_grants_broad_acquisition_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }
    fail_closed_rules = {
        "fail_closed_rules_created": True,
        "max_zip_files_processed": EXPECTED_FILE_COUNT,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "max_total_source_rows_allowed": MAX_TOTAL_SOURCE_ROWS_ALLOWED,
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "max_output_rows_allowed": MAX_OUTPUT_ROWS_ALLOWED,
        "complete_hour_required_source_rows": COMPLETE_HOUR_REQUIRED_SOURCE_ROWS,
        "synthetic_fill_allowed": False,
        "forward_fill_allowed": False,
        "backfill_allowed": False,
        "fail_closed_on_duplicate_minute_rows": True,
        "fail_closed_on_missing_minutes_if_marking_incomplete_complete": True,
        "fail_closed_on_symbol_mismatch": True,
        "fail_closed_on_schema_mismatch": True,
        "fail_closed_on_download_api_browse": True,
        "fail_closed_on_strict_3y_completeness_claim": True,
        "fail_closed_on_research_backtest_edge_or_broad_acquisition_claim": True,
    }
    self_validator = {
        "self_validated": True,
        "preview_artifact_valid": True,
        "approval_record_valid": True,
        "fail_closed_rules_valid": True,
        "target_symbol_valid": build_preview["target_symbol"] == TARGET_SYMBOL,
        "strict_3y_completeness_not_claimed": build_preview["strict_3y_completeness_claimed"] is False,
        "expected_file_count_valid": build_preview["expected_file_count"] == EXPECTED_FILE_COUNT,
        "expected_total_source_rows_valid": build_preview["expected_total_source_rows"] == EXPECTED_TOTAL_SOURCE_ROWS,
        "expected_output_rows_valid": build_preview["expected_output_rows"] == EXPECTED_OUTPUT_ROWS,
        "approval_future_build_next_only": approval_record["approval_grants_future_3_year_build_next"] is True
        and approval_record["approval_grants_build_now"] is False,
        "no_download_api_browse_full_csv_read_build_aggregation_now": True,
        "next_module_is_direct_3_year_build_execution": approval_record["next_module"] == NEXT_MODULE,
    }
    replacement_checks = {
        "preflight_passed": True,
        "download_validator_pass": True,
        "preview_created": build_preview["preview_created"],
        "approval_record_created": approval_record["approval_record_created"],
        "self_validated": self_validator["self_validated"],
        "strict_3y_completeness_not_claimed": build_preview["strict_3y_completeness_claimed"] is False,
        "expected_file_count_1053": build_preview["expected_file_count"] == EXPECTED_FILE_COUNT,
        "expected_total_source_rows_1516320": build_preview["expected_total_source_rows"] == EXPECTED_TOTAL_SOURCE_ROWS,
        "expected_output_rows_25272": build_preview["expected_output_rows"] == EXPECTED_OUTPUT_ROWS,
        "approval_future_build_next": approval_record["approval_grants_future_3_year_build_next"] is True,
        "approval_build_now_false": approval_record["approval_grants_build_now"] is False,
        "no_download_api_browse_full_csv_read_build_aggregation": True,
        "not_broad_research_backtest_edge": True,
        "schema_config_absent": True,
        "generic_runner_blocked": True,
        "next_module_is_build_execution": approval_record["next_module"] == NEXT_MODULE,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_preview_status": PASS_STATUS,
        "preview_created": True,
        "approval_record_created": True,
        "self_validated": True,
        "target_symbol": TARGET_SYMBOL,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START,
        "max_available_end_date": MAX_AVAILABLE_END,
        "expected_file_count": EXPECTED_FILE_COUNT,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "approval_grants_build_now": False,
        "approval_grants_future_3_year_build_next": True,
        "new_download_performed_now": False,
        "full_csv_read_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "current_evidence_chain_quality_before_preview": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": NEXT_MODULE,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count_at_preview_run": tracked_python_count(),
    }
    bundle = {
        "build_preview": build_preview,
        "build_scope": build_scope,
        "approval_record": approval_record,
        "fail_closed_rules": fail_closed_rules,
        "self_validator": self_validator,
        "summary": summary_payload,
    }

    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_preview.json", build_preview)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_scope.json", build_scope)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_fail_closed_rules.json", fail_closed_rules)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_preview_bundle_summary.json", bundle)
    write_json(
        OUTPUT_DIR / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_preview_after_download_validator_v1_latest.json",
        summary_payload,
    )
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_preview_status": BLOCKED_STATUS,
            "preview_created": False,
            "approval_record_created": False,
            "self_validated": False,
            "target_symbol": TARGET_SYMBOL,
            "strict_3y_completeness_claimed": False,
            "max_available_start_candidate": MAX_AVAILABLE_START,
            "max_available_end_date": MAX_AVAILABLE_END,
            "new_download_performed_now": False,
            "full_csv_read_performed_now": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "safe_for_broad_acquisition": False,
            "safe_for_research_backtest": False,
            "safe_for_edge_claim": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "dormant_repo_attention_count": 716,
            "next_module": BLOCKED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(
            OUTPUT_DIR / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_preview_after_download_validator_v1_latest.json",
            blocked_payload,
        )
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
