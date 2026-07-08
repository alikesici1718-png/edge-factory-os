from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_validator_after_execution_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "2a7c406"
EXPECTED_PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_EXECUTION_VALIDATED_PIPELINE_SUMMARY_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
    "BUILD_EXECUTION_VALIDATION"
)

TARGET_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = "2026-04-19"
DATE_RANGE_END = "2026-05-18"
EXPECTED_FILE_COUNT = 30
EXPECTED_TOTAL_SOURCE_ROWS = 43200
EXPECTED_OUTPUT_ROWS = 720
EXPECTED_SOURCE_ROWS_PER_HOUR = 60
EXPECTED_HOUR_MS = 3_600_000
BUILD_SCOPE = "SINGLE_SYMBOL_30_DAY_1M_TO_1H_PIPELINE_VALIDATION_ONLY"

NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_pipeline_summary_after_build_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_validation_blocked_record_after_execution_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
BUILD_EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_after_preview_approval_v1"
)

ARTIFACTS = {
    "latest": BUILD_EXECUTION_DIR
    / (
        "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
        "30_day_1m_to_1h_build_execution_after_preview_approval_v1_latest.json"
    ),
    "build_execution_summary": BUILD_EXECUTION_DIR
    / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_summary.json",
    "build_execution_report": BUILD_EXECUTION_DIR
    / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_report.json",
    "gap_duplicate_report": BUILD_EXECUTION_DIR
    / "historical_okx_single_symbol_30_day_1m_to_1h_gap_duplicate_report.json",
    "schema_validation_report": BUILD_EXECUTION_DIR
    / "historical_okx_single_symbol_30_day_1m_to_1h_schema_validation_report.json",
    "output_provenance_report": BUILD_EXECUTION_DIR
    / "historical_okx_single_symbol_30_day_1m_to_1h_output_provenance_report.json",
    "build_execution_compliance_report": BUILD_EXECUTION_DIR
    / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_compliance_report.json",
}

EXPECTED_OUTPUT_SCHEMA = [
    "instrument_name",
    "hour_start_epoch_ms",
    "hour_start_iso_utc",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "source_row_count",
    "complete_hour",
    "confirm",
    "source_first_open_time",
    "source_last_open_time",
    "source_zip_sha256",
    "source_csv_file",
    "source_date",
    "build_scope",
]

DANGEROUS_FLAGS = {
    "new_download_performed_by_validator": False,
    "data_build_performed_by_validator": False,
    "aggregation_performed_by_validator": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "strategy_research_implementation_touched": False,
    "candidate_generation_touched": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class ValidationBlocked(RuntimeError):
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


def rel_repo_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def repo_has_only_approved_tool_change() -> bool:
    status_lines = run_git(["status", "--short"]).splitlines()
    if not status_lines:
        return True
    approved_rel = rel_repo_path(APPROVED_TOOL)
    return all(line[3:].replace("\\", "/") == approved_rel for line in status_lines)


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationBlocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> Any:
    exists[label] = path.exists()
    require(path.exists(), f"missing JSON artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise ValidationBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(data, dict), f"JSON artifact {label} is not an object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def parse_decimal(value: str) -> Decimal | None:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite():
        return None
    return parsed


def validate_output_csv(path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(path.exists(), f"output CSV missing: {path}")
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        observed_schema = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    row_count = len(rows)
    hours: list[int] = []
    symbols: set[str] = set()
    scopes: set[str] = set()
    source_dates: set[str] = set()
    source_csv_files: set[str] = set()
    source_zip_hashes: set[str] = set()
    source_row_count_60 = True
    complete_hour_true = True
    invalid_numeric_row_count = 0
    negative_volume_row_count = 0
    nan_inf_row_count = 0
    invalid_price_relation_row_count = 0
    provenance_missing_row_count = 0

    for row_index, row in enumerate(rows, start=1):
        symbols.add(row.get("instrument_name", ""))
        scopes.add(row.get("build_scope", ""))
        source_dates.add(row.get("source_date", ""))
        source_csv_files.add(row.get("source_csv_file", ""))
        source_zip_hashes.add(row.get("source_zip_sha256", ""))

        try:
            hours.append(int(row.get("hour_start_epoch_ms", "")))
        except ValueError:
            invalid_numeric_row_count += 1

        if row.get("source_row_count") != str(EXPECTED_SOURCE_ROWS_PER_HOUR):
            source_row_count_60 = False
        if parse_bool(row.get("complete_hour", "")) is not True:
            complete_hour_true = False

        if not row.get("source_zip_sha256") or not row.get("source_csv_file") or not row.get("source_date"):
            provenance_missing_row_count += 1

        numeric_values: dict[str, Decimal] = {}
        for column in ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote"]:
            parsed = parse_decimal(row.get(column, ""))
            if parsed is None:
                invalid_numeric_row_count += 1
                nan_inf_row_count += 1
                continue
            numeric_values[column] = parsed

        volume_negative = any(
            numeric_values.get(column, Decimal(0)) < 0 for column in ["vol", "vol_ccy", "vol_quote"]
        )
        if volume_negative:
            negative_volume_row_count += 1

        if all(column in numeric_values for column in ["open", "high", "low", "close"]):
            open_value = numeric_values["open"]
            high_value = numeric_values["high"]
            low_value = numeric_values["low"]
            close_value = numeric_values["close"]
            if high_value < max(open_value, close_value, low_value) or low_value > min(open_value, close_value, high_value):
                invalid_price_relation_row_count += 1
        else:
            invalid_price_relation_row_count += 1

        if row.get("build_scope") != BUILD_SCOPE:
            provenance_missing_row_count += 1

    unique_hours = set(hours)
    duplicate_hour_count = len(hours) - len(unique_hours)
    hours_sorted = hours == sorted(hours)
    if hours:
        expected_hours = list(range(min(hours), min(hours) + EXPECTED_OUTPUT_ROWS * EXPECTED_HOUR_MS, EXPECTED_HOUR_MS))
        missing_hours = sorted(set(expected_hours) - unique_hours)
    else:
        expected_hours = []
        missing_hours = []
    missing_hour_count = len(missing_hours)
    interval_valid = all((right - left) == EXPECTED_HOUR_MS for left, right in zip(hours, hours[1:]))
    observed_symbol = next(iter(symbols)) if len(symbols) == 1 else None

    output_validation = {
        "output_csv_exists": True,
        "output_csv_readable": True,
        "output_csv_row_count": row_count,
        "output_schema_validated": observed_schema == EXPECTED_OUTPUT_SCHEMA,
        "output_observed_schema": observed_schema,
        "output_expected_schema": EXPECTED_OUTPUT_SCHEMA,
        "output_symbol_count": len(symbols),
        "output_observed_symbol": observed_symbol,
        "output_hour_count": len(hours),
        "output_unique_hour_count": len(unique_hours),
        "output_duplicate_hour_count": duplicate_hour_count,
        "output_missing_hour_count": missing_hour_count,
        "output_hours_monotonic": hours_sorted and interval_valid,
        "output_all_source_row_count_60": source_row_count_60,
        "output_all_complete_hour_true": complete_hour_true,
        "output_observed_build_scope_count": len(scopes),
        "output_observed_build_scope": next(iter(scopes)) if len(scopes) == 1 else None,
        "source_date_count": len(source_dates - {""}),
        "source_csv_file_count": len(source_csv_files - {""}),
        "source_zip_sha256_count": len(source_zip_hashes - {""}),
        "first_hour_epoch_ms": min(hours) if hours else None,
        "last_hour_epoch_ms": max(hours) if hours else None,
        "missing_hour_epoch_ms_sample": missing_hours[:10],
    }
    numeric_validation = {
        "numeric_sanity_validated": (
            invalid_numeric_row_count == 0
            and negative_volume_row_count == 0
            and nan_inf_row_count == 0
            and invalid_price_relation_row_count == 0
        ),
        "invalid_numeric_row_count": invalid_numeric_row_count,
        "negative_volume_row_count": negative_volume_row_count,
        "nan_inf_row_count": nan_inf_row_count,
        "invalid_price_relation_row_count": invalid_price_relation_row_count,
    }
    provenance_validation = {
        "provenance_validated": provenance_missing_row_count == 0,
        "provenance_missing_row_count": provenance_missing_row_count,
        "all_source_zip_sha256_values_present": (
            len(source_zip_hashes - {""}) == EXPECTED_FILE_COUNT
            and all(len(value) == 64 for value in source_zip_hashes - {""})
        ),
        "all_source_csv_names_present": len(source_csv_files - {""}) == EXPECTED_FILE_COUNT,
        "all_source_date_values_present": len(source_dates - {""}) == EXPECTED_FILE_COUNT,
        "output_marked_pipeline_validation_only": scopes == {BUILD_SCOPE},
    }
    return output_validation, numeric_validation, provenance_validation


def validate_artifact_contract(artifacts: dict[str, Any]) -> None:
    summary = artifacts["build_execution_summary"]
    report = artifacts["build_execution_report"]
    gap_report = artifacts["gap_duplicate_report"]
    schema_report = artifacts["schema_validation_report"]
    provenance_report = artifacts["output_provenance_report"]
    compliance_report = artifacts["build_execution_compliance_report"]
    latest = artifacts["latest"]

    require(summary.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(latest.get("next_module") == REQUESTED_MODULE, "latest next_module mismatch")
    require(
        summary.get("historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_execution_status")
        == EXPECTED_PREVIOUS_STATUS,
        "previous build execution status mismatch",
    )
    require(summary.get("target_symbol") == TARGET_SYMBOL, "summary target symbol mismatch")
    require(summary.get("date_range_start") == DATE_RANGE_START, "summary date_range_start mismatch")
    require(summary.get("date_range_end") == DATE_RANGE_END, "summary date_range_end mismatch")
    require(summary.get("expected_file_count") == EXPECTED_FILE_COUNT, "summary expected file count mismatch")
    require(summary.get("file_count_processed") == EXPECTED_FILE_COUNT, "summary file count processed mismatch")
    require(summary.get("source_row_count_total") == EXPECTED_TOTAL_SOURCE_ROWS, "summary source rows mismatch")
    require(summary.get("expected_total_source_rows") == EXPECTED_TOTAL_SOURCE_ROWS, "summary expected source rows mismatch")
    require(summary.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS, "summary output rows mismatch")
    require(summary.get("expected_output_rows") == EXPECTED_OUTPUT_ROWS, "summary expected output rows mismatch")
    require(summary.get("complete_1h_row_count") == EXPECTED_OUTPUT_ROWS, "summary complete rows mismatch")
    require(summary.get("incomplete_1h_row_count") == 0, "summary incomplete rows mismatch")
    require(summary.get("all_hours_complete") is True, "summary complete hours mismatch")
    require(summary.get("synthetic_fill_used") is False, "summary synthetic fill mismatch")
    require(summary.get("forward_fill_used") is False, "summary forward fill mismatch")
    require(summary.get("backfill_used") is False, "summary backfill mismatch")
    require(summary.get("output_valid_for_research_backtest") is False, "summary research/backtest flag mismatch")
    require(summary.get("output_valid_for_edge_claim") is False, "summary edge flag mismatch")
    require(summary.get("broad_acquisition_ready") is False, "summary broad acquisition flag mismatch")
    require(summary.get("source_manifest_acquisition_ready") is False, "summary source manifest flag mismatch")
    require(summary.get("no_new_download") is True, "summary no new download flag mismatch")
    require(summary.get("new_download_performed_now") is False, "summary new download flag mismatch")
    require(summary.get("okx_api_call_performed") is False, "summary OKX API flag mismatch")
    require(summary.get("okx_browse_performed") is False, "summary OKX browse flag mismatch")
    require(summary.get("data_download_performed") is False, "summary data download flag mismatch")
    require(summary.get("data_fetch_performed") is False, "summary data fetch flag mismatch")
    require(summary.get("backtest_performed") is False, "summary backtest flag mismatch")
    require(summary.get("candidate_generation_performed") is False, "summary candidate flag mismatch")
    require(summary.get("schema_or_config_created") is False, "summary schema/config flag mismatch")
    require(summary.get("generic_runner_implementation_remains_blocked") is True, "summary generic runner flag mismatch")
    require(summary.get("output_is_pipeline_30_day_validation_only") is True, "summary pipeline validation flag mismatch")

    aggregation = report.get("aggregation_execution", {})
    require(aggregation.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS, "report output row count mismatch")
    require(aggregation.get("complete_1h_row_count") == EXPECTED_OUTPUT_ROWS, "report complete row count mismatch")
    require(aggregation.get("incomplete_1h_row_count") == 0, "report incomplete row count mismatch")
    require(aggregation.get("synthetic_fill_used") is False, "report synthetic fill mismatch")
    require(aggregation.get("forward_fill_used") is False, "report forward fill mismatch")
    require(aggregation.get("backfill_used") is False, "report backfill mismatch")
    require(gap_report.get("duplicate_minute_count_total") == 0, "gap duplicate report duplicate mismatch")
    require(gap_report.get("missing_minute_count_total") == 0, "gap duplicate report missing mismatch")
    require(gap_report.get("incomplete_hour_count") == 0, "gap duplicate report incomplete mismatch")
    require(schema_report.get("output_schema") == EXPECTED_OUTPUT_SCHEMA, "schema report output schema mismatch")
    require(schema_report.get("output_schema_validated") is True, "schema report not validated")
    require(schema_report.get("numeric_validation_passed") is True, "schema report numeric validation mismatch")
    require(provenance_report.get("output_row_count") == EXPECTED_OUTPUT_ROWS, "provenance output rows mismatch")
    require(
        provenance_report.get("provenance_status") == "THIRTY_DAY_SINGLE_SYMBOL_PIPELINE_VALIDATION_BUILD_OUTPUT",
        "provenance status mismatch",
    )
    require(len(provenance_report.get("source_zip_sha256_by_file", {})) == EXPECTED_FILE_COUNT, "source SHA256 count mismatch")
    require(len(provenance_report.get("expected_inner_csv_by_file", {})) == EXPECTED_FILE_COUNT, "source CSV count mismatch")
    require(compliance_report.get("no_new_download") is True, "compliance no new download mismatch")
    require(compliance_report.get("no_api") is True, "compliance API mismatch")
    require(compliance_report.get("no_browse") is True, "compliance browse mismatch")
    require(compliance_report.get("no_multi_symbol") is True, "compliance multi-symbol mismatch")
    require(compliance_report.get("no_strategy_backtest_candidate") is True, "compliance strategy/backtest mismatch")
    require(compliance_report.get("no_runtime_capital_live") is True, "compliance runtime/capital/live mismatch")
    require(compliance_report.get("no_repo_schema_config") is True, "compliance schema/config mismatch")
    require(compliance_report.get("no_generic_runner") is True, "compliance generic runner mismatch")
    require(compliance_report.get("broad_acquisition_ready") is False, "compliance broad acquisition mismatch")
    require(compliance_report.get("source_manifest_acquisition_ready") is False, "compliance source manifest mismatch")


def main() -> None:
    generated_at = utc_now()
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_approved_tool_change(), "repo dirty outside approved validator tool")

    exists: dict[str, bool] = {}
    valid_json: dict[str, bool] = {}
    artifacts = {
        label: load_json(path, label, exists, valid_json)
        for label, path in ARTIFACTS.items()
    }
    validate_artifact_contract(artifacts)

    summary = artifacts["build_execution_summary"]
    provenance_report = artifacts["output_provenance_report"]
    output_csv_path = Path(summary.get("output_csv_path") or provenance_report.get("output_csv_path", ""))
    output_validation, numeric_validation, row_provenance_validation = validate_output_csv(output_csv_path)

    require(output_validation["output_csv_row_count"] == EXPECTED_OUTPUT_ROWS, "output CSV row count mismatch")
    require(output_validation["output_schema_validated"] is True, "output CSV schema mismatch")
    require(output_validation["output_symbol_count"] == 1, "output symbol count mismatch")
    require(output_validation["output_observed_symbol"] == TARGET_SYMBOL, "output observed symbol mismatch")
    require(output_validation["output_hour_count"] == EXPECTED_OUTPUT_ROWS, "output hour count mismatch")
    require(output_validation["output_unique_hour_count"] == EXPECTED_OUTPUT_ROWS, "output unique hour count mismatch")
    require(output_validation["output_duplicate_hour_count"] == 0, "duplicate output hours found")
    require(output_validation["output_missing_hour_count"] == 0, "missing output hours found")
    require(output_validation["output_hours_monotonic"] is True, "output hours not monotonic or hourly")
    require(output_validation["output_all_source_row_count_60"] is True, "source_row_count value other than 60 found")
    require(output_validation["output_all_complete_hour_true"] is True, "complete_hour false found")
    require(numeric_validation["numeric_sanity_validated"] is True, "numeric sanity validation failed")
    require(row_provenance_validation["provenance_validated"] is True, "row provenance validation failed")
    require(row_provenance_validation["all_source_zip_sha256_values_present"] is True, "source ZIP SHA256 missing")
    require(row_provenance_validation["all_source_csv_names_present"] is True, "source CSV names missing")
    require(row_provenance_validation["all_source_date_values_present"] is True, "source dates missing")
    require(row_provenance_validation["output_marked_pipeline_validation_only"] is True, "pipeline validation marker missing")

    validator_p0_count = 0
    validator_p1_count = int(summary.get("active_p1_attention_count", 8))
    replacement_checks = {
        "execution_artifacts_exist": all(exists.values()),
        "execution_artifacts_valid_json": all(valid_json.values()),
        "output_csv_720_rows": output_validation["output_csv_row_count"] == EXPECTED_OUTPUT_ROWS,
        "output_schema_validated": output_validation["output_schema_validated"],
        "single_symbol_btc_usdt_swap": (
            output_validation["output_symbol_count"] == 1
            and output_validation["output_observed_symbol"] == TARGET_SYMBOL
        ),
        "hours_unique_monotonic_complete_no_gaps": (
            output_validation["output_unique_hour_count"] == EXPECTED_OUTPUT_ROWS
            and output_validation["output_duplicate_hour_count"] == 0
            and output_validation["output_missing_hour_count"] == 0
            and output_validation["output_hours_monotonic"]
        ),
        "all_source_row_count_60": output_validation["output_all_source_row_count_60"],
        "all_complete_hour_true": output_validation["output_all_complete_hour_true"],
        "numeric_sanity_validated": numeric_validation["numeric_sanity_validated"],
        "provenance_validated": row_provenance_validation["provenance_validated"],
        "no_new_download_api_browse": True,
        "no_validator_build_aggregation": True,
        "not_research_backtest_edge": True,
        "not_broad_acquisition_ready": True,
        "not_multi_symbol_build_ready": True,
        "schema_config_absent": True,
        "generic_runner_blocked": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks did not all pass")

    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": head,
        "historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_execution_validator_status": PASS_STATUS,
        "build_execution_validated": True,
        "final_decision": "30_DAY_1M_TO_1H_BUILD_EXECUTION_VALIDATED_PIPELINE_SUMMARY_READY",
        "next_action": "CREATE_30_DAY_SINGLE_SYMBOL_PIPELINE_SUMMARY_AFTER_BUILD_VALIDATOR",
        "next_module": NEXT_MODULE_PASS,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "execution_artifacts_exist": all(exists.values()),
        "execution_artifacts_valid_json": all(valid_json.values()),
        "artifact_exists_by_label": exists,
        "artifact_valid_json_by_label": valid_json,
        "output_csv_exists": output_validation["output_csv_exists"],
        "output_csv_row_count": output_validation["output_csv_row_count"],
        "output_schema_validated": output_validation["output_schema_validated"],
        "output_symbol_count": output_validation["output_symbol_count"],
        "output_observed_symbol": output_validation["output_observed_symbol"],
        "output_hour_count": output_validation["output_hour_count"],
        "output_unique_hour_count": output_validation["output_unique_hour_count"],
        "output_duplicate_hour_count": output_validation["output_duplicate_hour_count"],
        "output_missing_hour_count": output_validation["output_missing_hour_count"],
        "output_hours_monotonic": output_validation["output_hours_monotonic"],
        "output_all_source_row_count_60": output_validation["output_all_source_row_count_60"],
        "output_all_complete_hour_true": output_validation["output_all_complete_hour_true"],
        "complete_1h_row_count": summary.get("complete_1h_row_count"),
        "incomplete_1h_row_count": summary.get("incomplete_1h_row_count"),
        "all_hours_complete": summary.get("all_hours_complete"),
        "synthetic_fill_used": summary.get("synthetic_fill_used"),
        "forward_fill_used": summary.get("forward_fill_used"),
        "backfill_used": summary.get("backfill_used"),
        "numeric_sanity_validated": numeric_validation["numeric_sanity_validated"],
        "invalid_numeric_row_count": numeric_validation["invalid_numeric_row_count"],
        "negative_volume_row_count": numeric_validation["negative_volume_row_count"],
        "nan_inf_row_count": numeric_validation["nan_inf_row_count"],
        "invalid_price_relation_row_count": numeric_validation["invalid_price_relation_row_count"],
        "provenance_validated": row_provenance_validation["provenance_validated"],
        "all_source_zip_sha256_values_present": row_provenance_validation["all_source_zip_sha256_values_present"],
        "all_source_csv_names_present": row_provenance_validation["all_source_csv_names_present"],
        "all_source_date_values_present": row_provenance_validation["all_source_date_values_present"],
        "output_valid_for_pipeline_30_day_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_30_day_pipeline_summary": True,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
        "no_new_download": True,
        "new_download_performed_by_validator": False,
        "data_build_performed_by_validator": False,
        "aggregation_performed_by_validator": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "validator_p0_count": validator_p0_count,
        "validator_p1_count": validator_p1_count,
        "current_evidence_chain_quality_before_validator": (
            "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
            "BUILD_EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
        ),
        "current_evidence_chain_quality_after_validator": (
            "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_1M_TO_1H_"
            "BUILD_EXECUTION_VALIDATED_PIPELINE_SUMMARY_READY"
        ),
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": validator_p1_count,
        "dormant_repo_attention_count": summary.get("dormant_repo_attention_count", 716),
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "output_csv_path": str(output_csv_path),
        "required_artifact_paths": {label: str(path) for label, path in ARTIFACTS.items()},
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": (
            "validated the existing BTC-USDT-SWAP 30-day 1m-to-1h pipeline-validation output "
            "from existing JSON artifacts and the generated 720-row CSV only; confirmed exact "
            "schema, one symbol, 720 unique monotonic hourly buckets, all source_row_count "
            "values at 60, all hours complete, numeric sanity, provenance fields present, no "
            "new download/API/browse, no validator-side build or aggregation, and no broad "
            "acquisition, research, backtest, edge, runtime, capital, live, schema/config, or "
            "generic-runner action"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count_at_validator_run": tracked_python_count(),
    }
    risk_decision = {
        "build_execution_validated": True,
        "output_valid_for_pipeline_30_day_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_30_day_pipeline_summary": True,
        "safe_for_broad_acquisition": False,
        "safe_for_multi_symbol_build": False,
        "validator_p0_count": validator_p0_count,
        "validator_p1_count": validator_p1_count,
    }
    bundle = {
        "execution_artifact_validation": {
            "all_required_build_execution_artifacts_exist": all(exists.values()),
            "all_required_build_execution_artifacts_valid_json": all(valid_json.values()),
            "artifact_exists_by_label": exists,
            "artifact_valid_json_by_label": valid_json,
        },
        "output_csv_validation": output_validation,
        "numeric_sanity_validation": numeric_validation,
        "provenance_validation": row_provenance_validation,
        "risk_decision": risk_decision,
        "summary": summary_payload,
    }

    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_validator.json", bundle)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_output_validation_report.json", output_validation)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_output_numeric_sanity_report.json", numeric_validation)
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_output_provenance_validation_report.json",
        row_provenance_validation,
    )
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_validator_summary.json", summary_payload)
    write_json(
        OUTPUT_DIR
        / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_execution_validator_after_execution_v1_latest.json",
        summary_payload,
    )
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except ValidationBlocked as exc:
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_single_symbol_30_day_1m_to_1h_build_execution_validator_status": BLOCKED_STATUS,
            "build_execution_validated": False,
            "final_decision": "BLOCKED_CONTEXT_MISMATCH",
            "next_action": "WRITE_30_DAY_1M_TO_1H_BUILD_EXECUTION_VALIDATION_BLOCKED_RECORD",
            "next_module": NEXT_MODULE_BLOCKED,
            "blocked_reason": str(exc),
            "active_p0_blocker_count": 1,
            "validator_p0_count": 1,
            "validator_p1_count": 0,
            "no_new_download": True,
            "new_download_performed_by_validator": False,
            "data_build_performed_by_validator": False,
            "aggregation_performed_by_validator": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_broad_acquisition": False,
            "safe_for_multi_symbol_build": False,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "replacement_checks_all_true": False,
        }
        write_json(
            OUTPUT_DIR / "historical_okx_single_symbol_30_day_1m_to_1h_build_execution_validator_summary.json",
            blocked_payload,
        )
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
