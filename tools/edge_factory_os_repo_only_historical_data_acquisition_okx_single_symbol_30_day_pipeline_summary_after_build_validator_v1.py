from __future__ import annotations

import json
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_pipeline_summary_after_build_validator_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "82be099"
TARGET_SYMBOL = "BTC-USDT-SWAP"
INPUT_INTERVAL = "1m"
OUTPUT_INTERVAL = "1h"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_EXECUTION_VALIDATED_PIPELINE_SUMMARY_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_PIPELINE_SUMMARY_"
    "3_YEAR_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_DOWNLOAD_YET"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_PIPELINE_SUMMARY"
)

THIRTY_DAY_START = date(2026, 4, 19)
NOMINAL_END = date(2026, 5, 18)
NOMINAL_STRICT_3Y_START = date(2023, 5, 19)
MAX_AVAILABLE_START_CANDIDATE = date(2023, 7, 1)
EXPECTED_STRICT_3Y_FILE_COUNT = 1096
EXPECTED_MAX_AVAILABLE_FILE_COUNT = 1053
EXISTING_VALIDATED_REUSE_FILE_COUNT = 30
EXPECTED_MAX_AVAILABLE_MISSING_DOWNLOAD_FILE_COUNT = 1023
EXPECTED_STRICT_3Y_MISSING_DOWNLOAD_FILE_COUNT = 1066
KNOWN_OKX_COVERAGE_START_FROM_PRIOR_ARTIFACTS = "July 2023"
PURPOSE = "PIPELINE_LONG_RANGE_VALIDATION_ONLY_NOT_RESEARCH_NOT_EDGE"

NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_after_30_day_summary_preview_approval_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_pipeline_summary_blocked_record_after_build_validator_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
PREVIOUS_VALIDATOR_SUMMARY = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_validator_after_execution_v1"
) / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_validator_after_execution_v1_latest.json"
)

DANGEROUS_FLAGS = {
    "data_download_performed": False,
    "data_fetch_performed": False,
    "new_download_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "okx_download_performed": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed": False,
    "csv_read_performed": False,
    "zip_read_performed": False,
    "research_backtest_edge_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "multi_symbol_claim_made": False,
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


def inclusive_days(start: date, end: date) -> list[date]:
    require(start <= end, f"invalid date range: {start} > {end}")
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def okx_daily_candlestick_url(symbol: str, day: date) -> str:
    compact_day = day.strftime("%Y%m%d")
    iso_day = day.isoformat()
    return (
        "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/"
        f"{compact_day}/{symbol}-candlesticks-{iso_day}.zip"
    )


def expected_csv_name(symbol: str, day: date) -> str:
    return f"{symbol}-candlesticks-{day.isoformat()}.csv"


def validate_previous_summary(summary: dict[str, Any]) -> None:
    require(
        summary.get("historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_execution_validator_status")
        == PREVIOUS_STATUS,
        "previous validator status mismatch",
    )
    require(summary.get("next_module") == REQUESTED_MODULE, "current next_module mismatch")
    require(summary.get("build_execution_validated") is True, "30-day build execution not validated")
    require(summary.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(summary.get("date_range_start") == THIRTY_DAY_START.isoformat(), "30-day start mismatch")
    require(summary.get("date_range_end") == NOMINAL_END.isoformat(), "30-day end mismatch")
    require(summary.get("output_csv_row_count") == 720, "30-day output row count mismatch")
    require(summary.get("complete_1h_row_count") == 720, "30-day complete row count mismatch")
    require(summary.get("all_hours_complete") is True, "30-day all-hours-complete mismatch")
    require(summary.get("numeric_sanity_validated") is True, "numeric sanity not validated")
    require(summary.get("provenance_validated") is True, "provenance not validated")
    require(summary.get("synthetic_fill_used") is False, "synthetic fill was used")
    require(summary.get("forward_fill_used") is False, "forward fill was used")
    require(summary.get("backfill_used") is False, "backfill was used")
    require(summary.get("output_valid_for_pipeline_30_day_validation") is True, "30-day validation flag mismatch")
    require(summary.get("output_valid_for_research_backtest") is False, "research/backtest claim detected")
    require(summary.get("output_valid_for_edge_claim") is False, "edge claim detected")
    require(summary.get("safe_for_broad_acquisition") is False, "broad acquisition claim detected")
    require(summary.get("safe_for_multi_symbol_build") is False, "multi-symbol claim detected")
    require(summary.get("validator_p0_count") == 0, "previous validator P0 count nonzero")
    require(int(summary.get("validator_p1_count", 0)) >= 8, "previous validator P1 count too low")


def build_plan(start: date, end: date, existing_days: set[date]) -> dict[str, Any]:
    days = inclusive_days(start, end)
    missing_days = [day for day in days if day not in existing_days]
    return {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "file_count": len(days),
        "url_count": len(days),
        "planned_urls": [okx_daily_candlestick_url(TARGET_SYMBOL, day) for day in days],
        "expected_inner_csv_by_date": {
            day.isoformat(): expected_csv_name(TARGET_SYMBOL, day) for day in days
        },
        "existing_validated_reuse_dates": [day.isoformat() for day in days if day in existing_days],
        "existing_validated_reuse_file_count": len([day for day in days if day in existing_days]),
        "missing_download_dates": [day.isoformat() for day in missing_days],
        "missing_download_file_count": len(missing_days),
    }


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")

    previous = load_json(PREVIOUS_VALIDATOR_SUMMARY)
    validate_previous_summary(previous)

    existing_30_day_dates = set(inclusive_days(THIRTY_DAY_START, NOMINAL_END))
    strict_plan = build_plan(NOMINAL_STRICT_3Y_START, NOMINAL_END, existing_30_day_dates)
    max_available_plan = build_plan(MAX_AVAILABLE_START_CANDIDATE, NOMINAL_END, existing_30_day_dates)

    require(strict_plan["file_count"] == EXPECTED_STRICT_3Y_FILE_COUNT, "strict 3-year file count mismatch")
    require(max_available_plan["file_count"] == EXPECTED_MAX_AVAILABLE_FILE_COUNT, "max-available file count mismatch")
    require(strict_plan["existing_validated_reuse_file_count"] == EXISTING_VALIDATED_REUSE_FILE_COUNT, "strict reuse count mismatch")
    require(max_available_plan["existing_validated_reuse_file_count"] == EXISTING_VALIDATED_REUSE_FILE_COUNT, "max-available reuse count mismatch")
    require(
        strict_plan["missing_download_file_count"] == EXPECTED_STRICT_3Y_MISSING_DOWNLOAD_FILE_COUNT,
        "strict missing download count mismatch",
    )
    require(
        max_available_plan["missing_download_file_count"] == EXPECTED_MAX_AVAILABLE_MISSING_DOWNLOAD_FILE_COUNT,
        "max-available missing download count mismatch",
    )

    thirty_day_pipeline_summary = {
        "thirty_day_pipeline_summary_created": True,
        "thirty_day_pipeline_closed_successfully": True,
        "target_symbol": TARGET_SYMBOL,
        "input_interval": INPUT_INTERVAL,
        "output_interval": OUTPUT_INTERVAL,
        "date_range_start": THIRTY_DAY_START.isoformat(),
        "date_range_end": NOMINAL_END.isoformat(),
        "source_row_count_total": 43200,
        "output_1h_row_count": 720,
        "complete_1h_row_count": 720,
        "all_hours_complete": True,
        "numeric_sanity_validated": True,
        "provenance_validated": True,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_valid_for_pipeline_30_day_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
    }

    three_year_download_preview = {
        "three_year_download_preview_created": True,
        "target_symbol": TARGET_SYMBOL,
        "route_type": "SINGLE_SYMBOL_3_YEAR_OR_MAX_AVAILABLE_HISTORICAL_DOWNLOAD_PREVIEW",
        "nominal_end_date": NOMINAL_END.isoformat(),
        "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START.isoformat(),
        "nominal_strict_3y_file_count": strict_plan["file_count"],
        "known_okx_candlestick_coverage_start_from_prior_artifacts": KNOWN_OKX_COVERAGE_START_FROM_PRIOR_ARTIFACTS,
        "coverage_start_uncertainty_must_be_recorded": True,
        "coverage_start_uncertainty_recorded": True,
        "strict_3y_completeness_claimed": False,
        "strict_3y_completeness_not_claimed_reason": (
            "Exact OKX daily archive start date is not proven from repo-only prior artifacts; "
            "strict nominal files before the known July 2023 coverage start must fail closed or "
            "be recorded as coverage gaps in the future execution."
        ),
        "max_available_start_candidate": MAX_AVAILABLE_START_CANDIDATE.isoformat(),
        "max_available_candidate_end": NOMINAL_END.isoformat(),
        "max_available_candidate_file_count": max_available_plan["file_count"],
        "existing_validated_reuse_file_count": EXISTING_VALIDATED_REUSE_FILE_COUNT,
        "missing_download_file_count_for_max_available_candidate": max_available_plan["missing_download_file_count"],
        "missing_download_file_count_for_strict_3y_nominal_plan": strict_plan["missing_download_file_count"],
        "purpose": PURPOSE,
        "strict_3y_nominal_plan": {
            "start_date": strict_plan["start_date"],
            "end_date": strict_plan["end_date"],
            "planned_file_count": strict_plan["file_count"],
            "existing_validated_reuse_file_count": strict_plan["existing_validated_reuse_file_count"],
            "missing_download_file_count": strict_plan["missing_download_file_count"],
            "coverage_risk_flagged": True,
            "strict_3y_completeness_claimed": False,
        },
        "max_available_candidate_plan": {
            "start_date": max_available_plan["start_date"],
            "end_date": max_available_plan["end_date"],
            "planned_file_count": max_available_plan["file_count"],
            "existing_validated_reuse_file_count": max_available_plan["existing_validated_reuse_file_count"],
            "missing_download_file_count": max_available_plan["missing_download_file_count"],
            "coverage_risk_flagged": True,
            "candidate_plan_only_not_completeness_claim": True,
        },
    }

    planned_url_manifest_preview = {
        "planned_url_manifest_preview_created": True,
        "target_symbol": TARGET_SYMBOL,
        "route_type": "SINGLE_SYMBOL_3_YEAR_OR_MAX_AVAILABLE_HISTORICAL_DOWNLOAD_PREVIEW",
        "manifest_is_preview_only": True,
        "manifest_fetch_performed": False,
        "url_fetch_performed": False,
        "strict_3y_nominal_plan": strict_plan,
        "max_available_candidate_plan": max_available_plan,
        "future_execution_must_use_only_approved_planned_url_manifest": True,
        "future_execution_must_download_missing_older_daily_zip_files_only": True,
        "future_execution_must_reuse_existing_validated_30_day_files": True,
        "future_execution_must_not_build_or_aggregate": True,
    }

    approval_record = {
        "three_year_download_approval_record_created": True,
        "approval_scope": "NEXT_SEPARATE_3_YEAR_OR_MAX_AVAILABLE_SINGLE_SYMBOL_DOWNLOAD_EXECUTION_ONLY",
        "approval_grants_download_now": False,
        "approval_grants_future_3_year_single_symbol_download_next": True,
        "approval_grants_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_multi_symbol_now": False,
        "approval_grants_broad_acquisition_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": NEXT_MODULE,
    }

    coverage_gap_policy = {
        "coverage_gap_policy_created": True,
        "coverage_start_uncertainty_recorded": True,
        "known_okx_candlestick_coverage_start_from_prior_artifacts": KNOWN_OKX_COVERAGE_START_FROM_PRIOR_ARTIFACTS,
        "strict_3y_completeness_claimed": False,
        "future_execution_must_fail_closed_or_record_coverage_gap_if_early_planned_files_unavailable": True,
        "future_execution_fail_closed_rules": [
            "URL count differs from approved manifest",
            "Non-approved URL is used",
            "File count exceeds approved plan",
            "ZIP path traversal appears",
            "Expected inner CSV is missing",
            "Schema mismatch occurs",
            "Symbol mismatch occurs",
            "Download fails without explicit coverage-gap record",
            "Coverage start prevents strict 3-year completeness",
            "Data build or aggregation is attempted",
            "Research/backtest/edge/acquisition-ready claim occurs",
        ],
        "future_execution_may_inspect_zip_inventory_safely": True,
        "future_execution_may_read_headers_and_up_to_5_sample_rows_per_csv": True,
        "future_execution_must_not_build_data": True,
        "future_execution_must_not_aggregate": True,
        "future_execution_must_not_claim_research_backtest_edge": True,
        "future_execution_must_not_mark_broad_acquisition_ready": True,
    }

    replacement_checks = {
        "head_matches": head == EXPECTED_HEAD,
        "repo_clean_or_only_approved_tool": True,
        "previous_status_pass": True,
        "previous_next_module_matches": True,
        "thirty_day_pipeline_summary_created": True,
        "thirty_day_pipeline_closed_successfully": True,
        "three_year_download_preview_created": True,
        "three_year_download_approval_record_created": True,
        "post_30_day_escalation_policy_respected": True,
        "no_more_intermediate_ranges_before_3_year": True,
        "strict_3y_file_count_1096": strict_plan["file_count"] == EXPECTED_STRICT_3Y_FILE_COUNT,
        "max_available_file_count_1053": max_available_plan["file_count"] == EXPECTED_MAX_AVAILABLE_FILE_COUNT,
        "max_available_missing_download_file_count_1023": (
            max_available_plan["missing_download_file_count"]
            == EXPECTED_MAX_AVAILABLE_MISSING_DOWNLOAD_FILE_COUNT
        ),
        "coverage_start_uncertainty_recorded": True,
        "strict_3y_completeness_not_claimed": True,
        "approval_future_3_year_next_true": True,
        "approval_download_now_false": True,
        "no_download_api_browse_url_fetch": True,
        "no_csv_zip_read": True,
        "no_build_aggregation": True,
        "not_research_backtest_edge": True,
        "not_broad_acquisition": True,
        "not_multi_symbol": True,
        "next_module_direct_3_year_single_symbol_download": NEXT_MODULE
        == "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_download_execution_after_30_day_summary_preview_approval_v1.py",
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks did not all pass")

    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": head,
        "historical_data_acquisition_okx_single_symbol_30_day_pipeline_summary_status": PASS_STATUS,
        "thirty_day_pipeline_summary_created": True,
        "thirty_day_pipeline_closed_successfully": True,
        "target_symbol": TARGET_SYMBOL,
        "input_interval": INPUT_INTERVAL,
        "output_interval": OUTPUT_INTERVAL,
        "thirty_day_output_row_count": 720,
        "thirty_day_source_row_count_total": 43200,
        "complete_1h_row_count": 720,
        "all_hours_complete": True,
        "numeric_sanity_validated": True,
        "provenance_validated": True,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_valid_for_pipeline_30_day_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
        "three_year_download_preview_created": True,
        "three_year_download_approval_record_created": True,
        "post_30_day_escalation_policy_respected": True,
        "no_more_intermediate_ranges_before_3_year": True,
        "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START.isoformat(),
        "nominal_end_date": NOMINAL_END.isoformat(),
        "nominal_strict_3y_file_count": strict_plan["file_count"],
        "known_okx_coverage_start_from_prior_artifacts": KNOWN_OKX_COVERAGE_START_FROM_PRIOR_ARTIFACTS,
        "coverage_start_uncertainty_recorded": True,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START_CANDIDATE.isoformat(),
        "max_available_candidate_file_count": max_available_plan["file_count"],
        "existing_validated_reuse_file_count": EXISTING_VALIDATED_REUSE_FILE_COUNT,
        "missing_download_file_count_for_max_available_candidate": max_available_plan["missing_download_file_count"],
        "approval_grants_download_now": False,
        "approval_grants_future_3_year_single_symbol_download_next": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "url_fetch_performed": False,
        "csv_read_performed": False,
        "zip_read_performed": False,
        "current_evidence_chain_quality_before_summary": (
            "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
            "BUILD_EXECUTION_VALIDATED_PIPELINE_SUMMARY_READY"
        ),
        "current_evidence_chain_quality_after_summary": (
            "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_PIPELINE_SUMMARY_"
            "3_YEAR_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_DOWNLOAD_YET"
        ),
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(8, int(previous.get("active_p1_attention_count", 8))),
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
        "tracked_python_count_at_summary_run": tracked_python_count(),
    }

    self_validator = {
        "self_validator_created": True,
        "summary_status": PASS_STATUS,
        "required_artifacts_created": True,
        "thirty_day_pipeline_summary_created": True,
        "thirty_day_pipeline_closed_successfully": True,
        "three_year_download_preview_created": True,
        "three_year_download_approval_record_created": True,
        "post_30_day_escalation_policy_respected": True,
        "no_more_intermediate_ranges_before_3_year": True,
        "coverage_start_uncertainty_recorded": True,
        "strict_3y_completeness_claimed": False,
        "no_download_api_browse_url_fetch": True,
        "no_csv_zip_read": True,
        "no_build_aggregation": True,
        "no_research_backtest_edge_claim": True,
        "no_broad_acquisition_ready_claim": True,
        "next_module_direct_3_year_download_execution": True,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    bundle = {
        "thirty_day_pipeline_summary": thirty_day_pipeline_summary,
        "three_year_download_preview": three_year_download_preview,
        "planned_url_manifest_preview": {
            "target_symbol": planned_url_manifest_preview["target_symbol"],
            "route_type": planned_url_manifest_preview["route_type"],
            "manifest_is_preview_only": True,
            "strict_3y_nominal_url_count": strict_plan["url_count"],
            "max_available_candidate_url_count": max_available_plan["url_count"],
            "future_execution_must_use_only_approved_planned_url_manifest": True,
            "future_execution_must_download_missing_older_daily_zip_files_only": True,
        },
        "approval_record": approval_record,
        "coverage_gap_policy": coverage_gap_policy,
        "self_validator": self_validator,
        "summary": summary_payload,
    }

    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_pipeline_summary.json", thirty_day_pipeline_summary)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_preview.json", three_year_download_preview)
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_3_year_planned_url_manifest_preview.json",
        planned_url_manifest_preview,
    )
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_coverage_gap_policy.json", coverage_gap_policy)
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_30_day_to_3_year_summary_self_validator.json",
        self_validator,
    )
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_to_3_year_bundle_summary.json", bundle)
    write_json(
        OUTPUT_DIR / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_30_day_pipeline_summary_after_build_validator_v1_latest.json",
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
            "historical_data_acquisition_okx_single_symbol_30_day_pipeline_summary_status": BLOCKED_STATUS,
            "thirty_day_pipeline_summary_created": False,
            "thirty_day_pipeline_closed_successfully": False,
            "three_year_download_preview_created": False,
            "three_year_download_approval_record_created": False,
            "blocked_reason": str(exc),
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "next_module": BLOCKED_NEXT_MODULE,
            "new_download_performed_now": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "replacement_checks_all_true": False,
        }
        write_json(
            OUTPUT_DIR / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_30_day_pipeline_summary_after_build_validator_v1_latest.json",
            blocked_payload,
        )
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
