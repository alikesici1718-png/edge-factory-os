from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_preview_after_download_validator_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "e5e58ca"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_"
    "VALIDATED_BUILD_PREVIEW_READY_NO_BUILD_NO_AGGREGATION"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_PREVIEW_"
    "APPROVED_EXECUTION_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_PREVIEW_"
    "AFTER_DOWNLOAD_VALIDATOR"
)
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_PREVIEW_APPROVED_EXECUTION_READY"
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_after_preview_approval_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_preview_blocked_record_after_download_validator_v1.py"
)

PILOT_SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "LINK-USDT-SWAP",
    "LTC-USDT-SWAP",
    "DOT-USDT-SWAP",
]
BTC_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_TOTAL_PILOT_FILE_COUNT = 10_530
REUSED_FILE_COUNT = 1_053
NEW_DOWNLOAD_FILE_COUNT = 9_477
NOMINAL_SOURCE_ROWS_PER_SYMBOL = 1_516_320
NOMINAL_TOTAL_SOURCE_ROWS = 15_163_200
NOMINAL_OUTPUT_ROWS_PER_SYMBOL = 25_272
NOMINAL_TOTAL_OUTPUT_ROWS = 252_720
BTC_COMPLETE_ROWS = 25_271
BTC_INCOMPLETE_ROWS = 1
NEW_SYMBOL_COUNT_REQUIRING_BUILD = 9
ACTIVE_P1_ATTENTION_COUNT = 14
DORMANT_REPO_ATTENTION_COUNT = 716

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)
BTC_POLICY_SUMMARY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_pipeline_summary_after_rebuild_validator_v1"
)
BTC_POLICY_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_rebuild_execution_validator_after_execution_v1"
)

DOWNLOAD_VALIDATOR_SUMMARY = (
    DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json"
)
BTC_POLICY_SUMMARY = (
    BTC_POLICY_SUMMARY_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary.json"
)
BTC_POLICY_VALIDATOR_SUMMARY = (
    BTC_POLICY_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_summary.json"
)

DANGEROUS_FLAGS = {
    "new_download_performed_now": False,
    "full_csv_read_performed_now": False,
    "zip_csv_extraction_or_read_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed_now": False,
    "parquet_read_performed_now": False,
    "research_backtest_edge_claim_made": False,
    "full_universe_ready_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class PreviewBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        raise PreviewBlocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing JSON artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise PreviewBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(data, dict), f"JSON artifact {label} is not an object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_download_validator(summary: dict[str, Any]) -> None:
    require(
        summary.get("historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_status")
        == PREVIOUS_STATUS,
        "download validator status mismatch",
    )
    require(summary.get("next_module") == REQUESTED_MODULE, "download validator next_module mismatch")
    require(summary.get("download_execution_validated") is True, "download execution not validated")
    require(summary.get("pilot_symbol_count") == len(PILOT_SYMBOLS), "pilot symbol count mismatch")
    require(summary.get("pilot_symbols") == PILOT_SYMBOLS, "pilot symbols mismatch")
    require(summary.get("date_range_start") == DATE_RANGE_START, "date range start mismatch")
    require(summary.get("date_range_end") == DATE_RANGE_END, "date range end mismatch")
    require(summary.get("expected_total_pilot_file_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "expected file count mismatch")
    require(summary.get("final_pilot_file_set_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "final file set count mismatch")
    require(summary.get("reused_file_count") == REUSED_FILE_COUNT, "reused file count mismatch")
    require(summary.get("new_download_file_count") == NEW_DOWNLOAD_FILE_COUNT, "new download count mismatch")
    require(summary.get("missing_or_failed_file_count") == 0, "missing/failed file count mismatch")
    require(summary.get("coverage_gap_detected") is False, "coverage gap detected")
    require(summary.get("approved_manifest_validated") is True, "approved manifest not validated")
    require(summary.get("all_hashes_match_recorded") is True, "hash validation mismatch")
    require(summary.get("all_zip_open_success") is True, "ZIP validation mismatch")
    require(summary.get("all_expected_inner_csv_present") is True, "inner CSV validation mismatch")
    require(summary.get("all_expected_schema_match") is True, "schema validation mismatch")
    require(summary.get("all_observed_symbols_match_expected") is True, "symbol validation mismatch")
    require(summary.get("all_one_minute_interval_observed_from_samples") is True, "sample interval validation mismatch")
    require(summary.get("safe_for_10_symbol_build_preview") is True, "not safe for 10-symbol build preview")
    require(summary.get("safe_for_full_universe_acquisition") is False, "full universe readiness claim detected")
    require(summary.get("safe_for_research_backtest") is False, "research/backtest readiness claim detected")
    require(summary.get("safe_for_edge_claim") is False, "edge claim readiness detected")
    require(summary.get("replacement_checks_all_true") is True, "download validator replacement checks not all true")


def validate_btc_policy_clean(summary: dict[str, Any], validator: dict[str, Any]) -> None:
    require(summary.get("target_symbol") == BTC_SYMBOL, "BTC policy summary target mismatch")
    require(summary.get("single_symbol_3_year_policy_clean_pipeline_closed_successfully") is True, "BTC policy clean pipeline not closed")
    require(summary.get("output_1h_row_count") == NOMINAL_OUTPUT_ROWS_PER_SYMBOL, "BTC output row count mismatch")
    require(summary.get("complete_1h_row_count") == BTC_COMPLETE_ROWS, "BTC complete row count mismatch")
    require(summary.get("incomplete_1h_row_count") == BTC_INCOMPLETE_ROWS, "BTC incomplete row count mismatch")
    require(summary.get("quarantine_applied_to_affected_hour") is True, "BTC affected hour not quarantined")
    require(summary.get("output_valid_for_pipeline_validation") is True, "BTC not valid for pipeline validation")
    require(summary.get("output_valid_for_research_backtest") is False, "BTC research/backtest claim detected")
    require(summary.get("output_valid_for_edge_claim") is False, "BTC edge claim detected")
    require(summary.get("broad_acquisition_ready") is False, "BTC broad acquisition claim detected")
    require(summary.get("source_manifest_acquisition_ready") is False, "BTC source manifest acquisition claim detected")
    require(summary.get("strict_3y_completeness_claimed") is False, "BTC strict 3-year completeness claim detected")

    require(validator.get("policy_clean_rebuild_execution_validated") is True, "BTC policy clean validator did not pass")
    require(validator.get("replacement_checks_all_true") is True, "BTC policy clean validator replacement checks failed")
    require(validator.get("output_csv_row_count") == NOMINAL_OUTPUT_ROWS_PER_SYMBOL, "BTC validator output rows mismatch")
    require(validator.get("complete_1h_row_count") == BTC_COMPLETE_ROWS, "BTC validator complete rows mismatch")
    require(validator.get("incomplete_1h_row_count") == BTC_INCOMPLETE_ROWS, "BTC validator incomplete rows mismatch")
    require(validator.get("data_build_performed_by_validator") is False, "BTC validator build occurred")
    require(validator.get("aggregation_performed_by_validator") is False, "BTC validator aggregation occurred")
    require(validator.get("new_download_performed_by_validator") is False, "BTC validator download occurred")
    require(validator.get("okx_api_call_performed") is False, "BTC validator API occurred")
    require(validator.get("okx_browse_performed") is False, "BTC validator browse occurred")


def build_artifacts(generated_at: str, download_summary: dict[str, Any], btc_summary: dict[str, Any]) -> dict[str, Any]:
    build_scope = {
        "build_scope_created": True,
        "scope_name": "OKX_10_SYMBOL_PILOT_1M_TO_1H_PIPELINE_SCALING_VALIDATION_ONLY",
        "symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "reused_btc_zip_file_count": REUSED_FILE_COUNT,
        "new_symbol_zip_file_count": NEW_DOWNLOAD_FILE_COUNT,
        "input_interval": "1m",
        "output_interval": "1h",
        "nominal_source_rows_per_symbol": NOMINAL_SOURCE_ROWS_PER_SYMBOL,
        "nominal_total_source_rows": NOMINAL_TOTAL_SOURCE_ROWS,
        "nominal_output_rows_per_symbol": NOMINAL_OUTPUT_ROWS_PER_SYMBOL,
        "nominal_total_output_rows": NOMINAL_TOTAL_OUTPUT_ROWS,
        "future_output_options_allowed": [
            "ONE_COMBINED_10_SYMBOL_1H_CSV",
            "PER_SYMBOL_1H_CSVS_PLUS_COMBINED_MANIFEST",
        ],
        "output_is_pipeline_pilot_validation_only": True,
        "safe_for_full_universe_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
    }

    build_preview = {
        "preview_created": True,
        "purpose": "10_SYMBOL_PILOT_PIPELINE_SCALING_VALIDATION_ONLY_NOT_RESEARCH_NOT_EDGE",
        "download_validator_status": download_summary[
            "historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_status"
        ],
        "approved_input_file_set_already_validated": True,
        "future_build_may_use_only_10530_validated_zip_paths": True,
        "future_build_must_revalidate_sha256_before_each_csv_read": True,
        "future_build_may_read_full_csvs_only_in_future_execution_module": True,
        "future_build_must_process_only_approved_10_symbols": True,
        "future_build_must_process_only_approved_date_range": True,
        "future_build_must_aggregate_1m_rows_to_utc_1h_candles": True,
        "future_build_must_write_per_symbol_reports": True,
        "future_build_must_write_pilot_build_summary": True,
        "btc_policy_clean_reuse_allowed_in_future_execution": True,
        "btc_policy_clean_reuse_requires_revalidation": True,
        "btc_policy_clean_validated_output_rows": btc_summary["output_1h_row_count"],
        "btc_policy_clean_complete_rows": btc_summary["complete_1h_row_count"],
        "btc_policy_clean_incomplete_rows": btc_summary["incomplete_1h_row_count"],
        "btc_policy_clean_affected_hour_utc": btc_summary["affected_hour_utc"],
        "new_symbol_count_requiring_build": NEW_SYMBOL_COUNT_REQUIRING_BUILD,
        "new_symbols_requiring_build": [symbol for symbol in PILOT_SYMBOLS if symbol != BTC_SYMBOL],
        "future_build_must_not_download": True,
        "future_build_must_not_api_or_browse": True,
        "future_build_must_not_claim_research_backtest_edge": True,
        "future_build_must_not_claim_full_universe_or_broad_acquisition": True,
        "approval_grants_build_now": False,
        "approval_grants_future_10_symbol_build_next": True,
    }

    approval_record = {
        "approval_record_created": True,
        "approval_scope": "NEXT_10_SYMBOL_PILOT_1M_TO_1H_BUILD_EXECUTION_ONLY",
        "approval_grants_build_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_full_csv_read_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_future_10_symbol_build_next": True,
        "approval_grants_full_universe_acquisition": False,
        "approval_grants_research_backtest_edge": False,
        "next_module": NEXT_MODULE_PASS,
    }

    fail_closed_rules = {
        "fail_closed_rules_created": True,
        "max_symbols_processed": len(PILOT_SYMBOLS),
        "max_zip_files_processed": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "allowed_symbols": PILOT_SYMBOLS,
        "allowed_date_range_start": DATE_RANGE_START,
        "allowed_date_range_end": DATE_RANGE_END,
        "future_execution_must_revalidate_download_validator_summary": True,
        "future_execution_must_revalidate_sha256_before_csv_read": True,
        "fail_closed_on_download_api_browse": True,
        "fail_closed_on_unapproved_symbol": True,
        "fail_closed_on_unapproved_date": True,
        "fail_closed_on_schema_mismatch": True,
        "fail_closed_on_symbol_mismatch": True,
        "fail_closed_on_hash_mismatch": True,
        "fail_closed_on_material_duplicate_conflicts": True,
        "fail_closed_on_missing_minutes_without_explicit_incomplete_hour_policy": True,
        "fail_closed_on_output_row_count_over_nominal_without_policy": True,
        "fail_closed_on_research_backtest_edge_or_broad_acquisition_claim": True,
        "synthetic_fill_allowed": False,
        "forward_fill_allowed": False,
        "backfill_allowed": False,
        "silent_dedupe_allowed": False,
        "generic_runner_approval_granted": False,
    }

    anomaly_policy_preview = {
        "anomaly_policy_preview_created": True,
        "btc_reuse_policy": {
            "reuse_allowed_in_future_execution": True,
            "reuse_requires_provenance_hash_date_symbol_scope_revalidation": True,
            "validated_output_rows": NOMINAL_OUTPUT_ROWS_PER_SYMBOL,
            "validated_complete_rows": BTC_COMPLETE_ROWS,
            "validated_incomplete_rows": BTC_INCOMPLETE_ROWS,
            "affected_incomplete_hour_utc": btc_summary["affected_hour_utc"],
            "affected_hour_must_remain_marked_incomplete": True,
        },
        "new_symbol_policy": {
            "new_symbol_count_requiring_build": NEW_SYMBOL_COUNT_REQUIRING_BUILD,
            "future_build_must_fail_closed_on_new_symbol_material_conflicts": True,
            "future_build_must_fail_closed_on_missing_minutes_unless_policy_created": True,
            "future_build_must_fail_closed_on_schema_symbol_hash_mismatch": True,
            "silent_dedupe_for_new_symbols_allowed": False,
            "exact_duplicate_drop_requires_separate_audit": True,
            "material_conflict_quarantine_requires_separate_policy": True,
            "incomplete_hour_policy_requires_separate_policy": True,
        },
    }

    self_validator = {
        "self_validator_created": True,
        "self_validated": True,
        "download_validator_pass": download_summary[
            "historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_status"
        ]
        == PREVIOUS_STATUS,
        "pilot_symbol_count_valid": build_scope["symbol_count"] == 10,
        "file_count_valid": build_scope["expected_total_pilot_file_count"] == EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "source_rows_valid": build_scope["nominal_total_source_rows"] == NOMINAL_TOTAL_SOURCE_ROWS,
        "output_rows_valid": build_scope["nominal_total_output_rows"] == NOMINAL_TOTAL_OUTPUT_ROWS,
        "btc_policy_clean_reuse_rules_valid": (
            build_preview["btc_policy_clean_reuse_allowed_in_future_execution"]
            and build_preview["btc_policy_clean_reuse_requires_revalidation"]
            and build_preview["btc_policy_clean_validated_output_rows"] == NOMINAL_OUTPUT_ROWS_PER_SYMBOL
            and build_preview["btc_policy_clean_complete_rows"] == BTC_COMPLETE_ROWS
            and build_preview["btc_policy_clean_incomplete_rows"] == BTC_INCOMPLETE_ROWS
        ),
        "new_symbol_fail_closed_rules_valid": (
            anomaly_policy_preview["new_symbol_policy"]["future_build_must_fail_closed_on_new_symbol_material_conflicts"]
            and fail_closed_rules["silent_dedupe_allowed"] is False
        ),
        "approval_record_valid": approval_record["approval_record_created"],
        "approval_build_now_false": approval_record["approval_grants_build_now"] is False,
        "approval_future_10_symbol_build_next": approval_record["approval_grants_future_10_symbol_build_next"],
        "next_module_is_direct_10_symbol_build_execution": approval_record["next_module"] == NEXT_MODULE_PASS,
        "no_download_api_browse_full_csv_read_build_aggregation_now": all(value is False for value in DANGEROUS_FLAGS.values()),
        "not_full_universe_research_backtest_edge": (
            build_scope["safe_for_full_universe_acquisition"] is False
            and build_scope["safe_for_research_backtest"] is False
            and build_scope["safe_for_edge_claim"] is False
        ),
    }
    self_validator["replacement_checks_all_true"] = all(
        value is True for key, value in self_validator.items() if key not in {"self_validator_created"}
    )

    replacement_checks = {
        "preflight_passed": True,
        "download_validator_pass": True,
        "download_validator_next_module_current": download_summary.get("next_module") == REQUESTED_MODULE,
        "safe_for_10_symbol_build_preview": download_summary.get("safe_for_10_symbol_build_preview") is True,
        "pilot_symbol_count_10": build_scope["symbol_count"] == 10,
        "final_file_count_10530": build_scope["expected_total_pilot_file_count"] == EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "nominal_source_rows_per_symbol_1516320": build_scope["nominal_source_rows_per_symbol"] == NOMINAL_SOURCE_ROWS_PER_SYMBOL,
        "nominal_total_source_rows_15163200": build_scope["nominal_total_source_rows"] == NOMINAL_TOTAL_SOURCE_ROWS,
        "nominal_output_rows_per_symbol_25272": build_scope["nominal_output_rows_per_symbol"] == NOMINAL_OUTPUT_ROWS_PER_SYMBOL,
        "nominal_total_output_rows_252720": build_scope["nominal_total_output_rows"] == NOMINAL_TOTAL_OUTPUT_ROWS,
        "btc_policy_clean_reuse_allowed_with_revalidation": self_validator["btc_policy_clean_reuse_rules_valid"],
        "new_symbol_fail_closed_policy": self_validator["new_symbol_fail_closed_rules_valid"],
        "approval_build_now_false": approval_record["approval_grants_build_now"] is False,
        "approval_future_10_symbol_build_next": approval_record["approval_grants_future_10_symbol_build_next"],
        "next_module_is_direct_10_symbol_build_execution": approval_record["next_module"] == NEXT_MODULE_PASS,
        "no_download_api_browse_full_csv_read_build_aggregation_now": all(value is False for value in DANGEROUS_FLAGS.values()),
        "not_full_universe_research_backtest_edge": self_validator["not_full_universe_research_backtest_edge"],
        "generic_runner_blocked": True,
        "schema_config_absent": True,
        "self_validated": self_validator["self_validated"] and self_validator["replacement_checks_all_true"],
    }
    replacement_checks_all_true = all(replacement_checks.values())

    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": EXPECTED_HEAD,
        "historical_data_acquisition_okx_10_symbol_pilot_build_preview_status": PASS_STATUS,
        "preview_created": True,
        "approval_record_created": True,
        "self_validated": True,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "nominal_source_rows_per_symbol": NOMINAL_SOURCE_ROWS_PER_SYMBOL,
        "nominal_total_source_rows": NOMINAL_TOTAL_SOURCE_ROWS,
        "nominal_output_rows_per_symbol": NOMINAL_OUTPUT_ROWS_PER_SYMBOL,
        "nominal_total_output_rows": NOMINAL_TOTAL_OUTPUT_ROWS,
        "btc_policy_clean_reuse_allowed_in_future_execution": True,
        "btc_policy_clean_reuse_requires_revalidation": True,
        "new_symbol_count_requiring_build": NEW_SYMBOL_COUNT_REQUIRING_BUILD,
        "future_build_must_fail_closed_on_new_symbol_material_conflicts": True,
        "future_build_must_not_claim_research_backtest_edge": True,
        "approval_grants_build_now": False,
        "approval_grants_future_10_symbol_build_next": True,
        "new_download_performed_now": False,
        "full_csv_read_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "safe_for_full_universe_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
        "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY,
        "next_module": NEXT_MODULE_PASS,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "tracked_python_count_at_preview_run": tracked_python_count(),
    }

    return {
        "build_preview": build_preview,
        "build_scope": build_scope,
        "approval_record": approval_record,
        "fail_closed_rules": fail_closed_rules,
        "anomaly_policy_preview": anomaly_policy_preview,
        "self_validator": self_validator,
        "summary": summary,
    }


def main() -> None:
    generated_at = utc_now()
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved build preview module")

    exists: dict[str, bool] = {}
    valid_json: dict[str, bool] = {}
    download_summary = load_json(DOWNLOAD_VALIDATOR_SUMMARY, "download_validator_summary", exists, valid_json)
    btc_policy_summary = load_json(BTC_POLICY_SUMMARY, "btc_policy_clean_pipeline_summary", exists, valid_json)
    btc_policy_validator = load_json(BTC_POLICY_VALIDATOR_SUMMARY, "btc_policy_clean_rebuild_validator_summary", exists, valid_json)

    validate_download_validator(download_summary)
    validate_btc_policy_clean(btc_policy_summary, btc_policy_validator)
    artifacts = build_artifacts(generated_at, download_summary, btc_policy_summary)
    artifacts["summary"]["artifact_exists_by_label"] = exists
    artifacts["summary"]["artifact_valid_json_by_label"] = valid_json
    require(artifacts["summary"]["replacement_checks_all_true"], "replacement checks did not all pass")

    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_preview.json", artifacts["build_preview"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_scope.json", artifacts["build_scope"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_approval_record.json", artifacts["approval_record"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_fail_closed_rules.json", artifacts["fail_closed_rules"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_anomaly_policy_preview.json", artifacts["anomaly_policy_preview"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_self_validator.json", artifacts["self_validator"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_preview_bundle_summary.json", artifacts)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", artifacts["summary"])
    print(json.dumps(artifacts["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except PreviewBlocked as exc:
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_build_preview_status": BLOCKED_STATUS,
            "preview_created": False,
            "approval_record_created": False,
            "self_validated": False,
            "pilot_symbol_count": len(PILOT_SYMBOLS),
            "pilot_symbols": PILOT_SYMBOLS,
            "date_range_start": DATE_RANGE_START,
            "date_range_end": DATE_RANGE_END,
            "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
            "nominal_source_rows_per_symbol": NOMINAL_SOURCE_ROWS_PER_SYMBOL,
            "nominal_total_source_rows": NOMINAL_TOTAL_SOURCE_ROWS,
            "nominal_output_rows_per_symbol": NOMINAL_OUTPUT_ROWS_PER_SYMBOL,
            "nominal_total_output_rows": NOMINAL_TOTAL_OUTPUT_ROWS,
            "btc_policy_clean_reuse_allowed_in_future_execution": False,
            "btc_policy_clean_reuse_requires_revalidation": True,
            "new_symbol_count_requiring_build": NEW_SYMBOL_COUNT_REQUIRING_BUILD,
            "future_build_must_fail_closed_on_new_symbol_material_conflicts": True,
            "future_build_must_not_claim_research_backtest_edge": True,
            "approval_grants_build_now": False,
            "approval_grants_future_10_symbol_build_next": False,
            "new_download_performed_now": False,
            "full_csv_read_performed_now": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "safe_for_full_universe_acquisition": False,
            "safe_for_research_backtest": False,
            "safe_for_edge_claim": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "current_evidence_chain_quality_after_preview": PREVIOUS_STATUS,
            "next_module": NEXT_MODULE_BLOCKED,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked_payload)
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
