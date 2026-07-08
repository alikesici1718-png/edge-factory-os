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
    "3_year_policy_clean_rebuild_execution_validator_after_execution_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "bcb4693"
TARGET_SYMBOL = "BTC-USDT-SWAP"
MAX_AVAILABLE_START = "2023-07-01"
MAX_AVAILABLE_END = "2026-05-18"
EXPECTED_OUTPUT_ROWS = 25_272
EXPECTED_COMPLETE_ROWS = 25_271
EXPECTED_INCOMPLETE_ROWS = 1
EXPECTED_EXACT_DUPLICATES_DROPPED = 320
EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED = 2
EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY = 1_516_319
EXPECTED_AFFECTED_HOUR = "2026-04-14T07:00:00+00:00"
EXPECTED_AFFECTED_HOUR_SOURCE_ROWS = 59
EXPECTED_HOUR_MS = 3_600_000
BUILD_SCOPE = "SINGLE_SYMBOL_3_YEAR_MAX_AVAILABLE_POLICY_CLEAN_1M_TO_1H_PIPELINE_VALIDATION_ONLY"
CONFLICT_RESOLUTION_POLICY = "QUARANTINE_MATERIAL_CONFLICTING_OPEN_TIME_GROUP"

EXPECTED_PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_"
    "EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_"
    "EXECUTION_VALIDATED_PIPELINE_SUMMARY_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_"
    "EXECUTION_VALIDATION"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_"
    "VALIDATED_PIPELINE_SUMMARY_READY"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_pipeline_summary_after_rebuild_validator_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_validation_blocked_record_after_execution_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_after_material_conflict_policy_v1"
)
POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_material_duplicate_conflict_policy_after_conflict_review_v1"
)

OUTPUT_CSV = EXECUTION_DIR / "historical_okx_single_symbol_3_year_policy_clean_1m_to_1h_output.csv"
EXECUTION_SUMMARY = EXECUTION_DIR / "historical_okx_single_symbol_3_year_policy_clean_build_execution_summary.json"
EXECUTION_REPORT = EXECUTION_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_report.json"
EXACT_DUPLICATE_AUDIT = EXECUTION_DIR / "historical_okx_single_symbol_3_year_exact_duplicate_drop_audit.json"
MATERIAL_CONFLICT_AUDIT = EXECUTION_DIR / "historical_okx_single_symbol_3_year_material_conflict_quarantine_audit.json"
GAP_REPORT = EXECUTION_DIR / "historical_okx_single_symbol_3_year_policy_clean_gap_incomplete_hour_report.json"
SCHEMA_REPORT = EXECUTION_DIR / "historical_okx_single_symbol_3_year_policy_clean_schema_validation_report.json"
PROVENANCE_REPORT = EXECUTION_DIR / "historical_okx_single_symbol_3_year_policy_clean_output_provenance_report.json"
COMPLIANCE_REPORT = EXECUTION_DIR / "historical_okx_single_symbol_3_year_policy_clean_build_execution_compliance_report.json"
LATEST_SUMMARY = EXECUTION_DIR / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_after_material_conflict_policy_v1_latest.json"
)

POLICY_SUMMARY = POLICY_DIR / "historical_okx_single_symbol_3_year_material_conflict_policy_summary.json"
MATERIAL_POLICY = POLICY_DIR / "historical_okx_single_symbol_3_year_material_duplicate_conflict_policy.json"
QUARANTINE_POLICY = POLICY_DIR / "historical_okx_single_symbol_3_year_conflict_quarantine_policy.json"
REBUILD_APPROVAL = POLICY_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_approval_record.json"

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
    "policy_clean_build",
    "quarantine_applied",
    "incomplete_reason",
]

JSON_ARTIFACTS = {
    "execution_summary": EXECUTION_SUMMARY,
    "execution_report": EXECUTION_REPORT,
    "exact_duplicate_audit": EXACT_DUPLICATE_AUDIT,
    "material_conflict_audit": MATERIAL_CONFLICT_AUDIT,
    "gap_report": GAP_REPORT,
    "schema_report": SCHEMA_REPORT,
    "provenance_report": PROVENANCE_REPORT,
    "compliance_report": COMPLIANCE_REPORT,
    "latest_summary": LATEST_SUMMARY,
    "policy_summary": POLICY_SUMMARY,
    "material_policy": MATERIAL_POLICY,
    "quarantine_policy": QUARANTINE_POLICY,
    "rebuild_approval": REBUILD_APPROVAL,
}

VALIDATOR_DANGEROUS_FLAGS = {
    "new_download_performed_by_validator": False,
    "data_build_performed_by_validator": False,
    "aggregation_performed_by_validator": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed_by_validator": False,
    "multi_symbol_performed_by_validator": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_performed_by_validator": False,
    "edge_claim_made_by_validator": False,
    "runtime_capital_live_touched_by_validator": False,
    "repo_schema_config_created_by_validator": False,
    "generic_runner_approval_granted_by_validator": False,
}

P1_ATTENTION_ITEMS = [
    "pipeline_validation_only_output",
    "strict_3y_completeness_not_claimed",
    "affected_hour_remains_incomplete",
    "material_conflict_quarantine_retains_gap",
    "no_synthetic_forward_or_backfill",
    "not_valid_for_research_backtest",
    "not_valid_for_edge_claim",
    "broad_acquisition_not_ready",
    "source_manifest_not_acquisition_ready",
    "single_symbol_scope_only",
]


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


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def parse_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def parse_decimal(value: Any) -> tuple[Decimal | None, bool]:
    text = str(value).strip()
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError):
        lowered = text.lower()
        return None, lowered in {"nan", "+nan", "-nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}
    if not parsed.is_finite():
        return None, True
    return parsed, False


def validate_preconditions() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    clean_or_only_tool = repo_has_only_approved_tool_change()
    requested_tool_is_current = Path(__file__).resolve() == APPROVED_TOOL.resolve()
    require(head.startswith(EXPECTED_HEAD), f"HEAD mismatch: {head}")
    require(clean_or_only_tool, "repo has changes outside the approved validator tool")
    require(requested_tool_is_current, "running unexpected validator module")
    return {
        "head": head,
        "expected_head": EXPECTED_HEAD,
        "repo_clean_or_only_approved_tool_change": clean_or_only_tool,
        "requested_tool_is_current": requested_tool_is_current,
        "tracked_python_count": tracked_python_count(),
    }


def validate_existing_artifacts() -> tuple[dict[str, Any], dict[str, bool], dict[str, bool]]:
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {
        label: load_json(path, label, exists, valid)
        for label, path in JSON_ARTIFACTS.items()
    }

    execution_summary = artifacts["execution_summary"]
    latest_summary = artifacts["latest_summary"]
    policy_summary = artifacts["policy_summary"]
    material_policy = artifacts["material_policy"]
    quarantine_policy = artifacts["quarantine_policy"]
    rebuild_approval = artifacts["rebuild_approval"]
    schema_report = artifacts["schema_report"]
    compliance_report = artifacts["compliance_report"]

    require(execution_summary == latest_summary, "latest summary does not match execution summary")
    require(
        execution_summary.get(
            "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_status"
        )
        == EXPECTED_PREVIOUS_STATUS,
        "previous execution status mismatch",
    )
    require(execution_summary.get("next_module") == REQUESTED_MODULE, "current next_module mismatch")
    require(execution_summary.get("target_symbol") == TARGET_SYMBOL, "execution target symbol mismatch")
    require(execution_summary.get("observed_symbol") == TARGET_SYMBOL, "execution observed symbol mismatch")
    require(execution_summary.get("max_available_start_candidate") == MAX_AVAILABLE_START, "start candidate mismatch")
    require(execution_summary.get("max_available_end_date") == MAX_AVAILABLE_END, "end date mismatch")
    require(execution_summary.get("output_csv_created") is True, "execution did not create output CSV")
    require(execution_summary.get("output_schema_validated") is True, "execution schema validation missing")
    require(execution_summary.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS, "execution output row count mismatch")
    require(execution_summary.get("complete_1h_row_count") == EXPECTED_COMPLETE_ROWS, "execution complete row count mismatch")
    require(execution_summary.get("incomplete_1h_row_count") == EXPECTED_INCOMPLETE_ROWS, "execution incomplete row count mismatch")
    require(execution_summary.get("all_hours_complete") is False, "execution claims all hours complete")
    require(execution_summary.get("affected_hour_utc") == EXPECTED_AFFECTED_HOUR, "execution affected hour mismatch")
    require(execution_summary.get("affected_hour_marked_complete") is False, "execution affected hour marked complete")
    require(
        execution_summary.get("affected_hour_source_row_count") == EXPECTED_AFFECTED_HOUR_SOURCE_ROWS,
        "execution affected hour source row count mismatch",
    )
    require(
        execution_summary.get("exact_duplicate_rows_dropped") == EXPECTED_EXACT_DUPLICATES_DROPPED,
        "execution exact duplicate drop count mismatch",
    )
    require(
        execution_summary.get("material_conflict_rows_quarantined")
        == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "execution material conflict quarantine count mismatch",
    )
    require(
        execution_summary.get("clean_source_row_count_after_policy")
        == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "execution clean source row count mismatch",
    )
    require(execution_summary.get("synthetic_fill_used") is False, "execution synthetic fill claim detected")
    require(execution_summary.get("forward_fill_used") is False, "execution forward fill claim detected")
    require(execution_summary.get("backfill_used") is False, "execution backfill claim detected")
    require(execution_summary.get("strict_3y_completeness_claimed") is False, "strict 3y claim detected")
    require(execution_summary.get("output_valid_for_research_backtest") is False, "research/backtest claim detected")
    require(execution_summary.get("output_valid_for_edge_claim") is False, "edge claim detected")
    require(execution_summary.get("broad_acquisition_ready") is False, "broad acquisition claim detected")
    require(execution_summary.get("source_manifest_acquisition_ready") is False, "source manifest ready claim detected")

    dangerous_flags = execution_summary.get("dangerous_flags")
    require(isinstance(dangerous_flags, dict), "execution dangerous_flags missing")
    for flag in [
        "new_download_performed_now",
        "data_download_performed",
        "data_fetch_performed",
        "okx_download_performed",
        "okx_api_call_performed",
        "okx_browse_performed",
        "url_fetch_performed",
        "url_iteration_performed",
        "multi_symbol_performed",
        "synthetic_fill_used",
        "forward_fill_used",
        "backfill_used",
        "conflicting_row_choice_performed",
        "conflicting_row_average_performed",
        "conflicting_row_merge_performed",
        "backtest_performed",
        "candidate_generation_touched",
        "edge_profit_claim_made",
        "broad_acquisition_ready",
        "strict_3y_completeness_claimed",
        "runtime_touched",
        "capital_changed",
        "live_or_real_orders",
        "schema_or_config_created",
        "generic_runner_approval_granted",
    ]:
        require(dangerous_flags.get(flag) is False, f"execution dangerous flag not false: {flag}")

    require(policy_summary.get("next_module") == "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_after_material_conflict_policy_v1.py", "policy summary next module mismatch")
    require(policy_summary.get("conflict_resolution_policy") == CONFLICT_RESOLUTION_POLICY, "policy summary conflict policy mismatch")
    require(policy_summary.get("exact_duplicate_extra_row_count") == EXPECTED_EXACT_DUPLICATES_DROPPED, "policy exact duplicate count mismatch")
    require(policy_summary.get("material_conflicting_row_count") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED, "policy material conflict row count mismatch")
    require(policy_summary.get("material_conflict_quarantine_required") is True, "policy quarantine requirement missing")
    require(policy_summary.get("exact_duplicate_drop_allowed") is True, "policy duplicate drop allowance missing")
    require(policy_summary.get("choose_conflicting_row_allowed") is False, "policy allows conflicting row choice")
    require(policy_summary.get("average_conflicting_rows_allowed") is False, "policy allows conflicting row average")
    require(policy_summary.get("merge_conflicting_rows_allowed") is False, "policy allows conflicting row merge")
    require(material_policy.get("conflict_resolution_policy") == CONFLICT_RESOLUTION_POLICY, "material policy mismatch")
    require(material_policy.get("material_conflict_quarantine_required") is True, "material policy quarantine missing")
    require(quarantine_policy.get("quarantine_scope") == "BOTH_ROWS_FOR_MATERIAL_CONFLICTING_OPEN_TIME_GROUP", "quarantine scope mismatch")
    require(quarantine_policy.get("material_conflict_rows_to_quarantine") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED, "quarantine row count mismatch")
    require(quarantine_policy.get("replacement_minute_allowed") is False, "quarantine replacement flag mismatch")
    require(rebuild_approval.get("policy_clean_rebuild_approval_record_created") is True, "rebuild approval missing")
    require(
        rebuild_approval.get("approval_grants_future_policy_clean_rebuild_next") is True,
        "future policy-clean rebuild approval missing",
    )
    require(rebuild_approval.get("approval_grants_download_now") is False, "approval grants download now")
    require(rebuild_approval.get("approval_grants_api_now") is False, "approval grants API now")
    require(rebuild_approval.get("approval_grants_browse_now") is False, "approval grants browse now")
    require(
        rebuild_approval.get("approval_grants_research_backtest_edge_now") is False,
        "approval grants research/backtest/edge now",
    )

    require(schema_report.get("output_schema_validated") is True, "schema report not validated")
    require(schema_report.get("output_schema") == EXPECTED_OUTPUT_SCHEMA, "schema report output schema mismatch")
    require(compliance_report.get("no_new_download") is True, "compliance no_new_download mismatch")
    require(compliance_report.get("no_api") is True, "compliance no_api mismatch")
    require(compliance_report.get("no_browse") is True, "compliance no_browse mismatch")
    require(compliance_report.get("no_synthetic_fill") is True, "compliance no_synthetic_fill mismatch")
    require(compliance_report.get("no_forward_fill") is True, "compliance no_forward_fill mismatch")
    require(compliance_report.get("no_backfill") is True, "compliance no_backfill mismatch")
    require(compliance_report.get("output_is_policy_clean_pipeline_validation_only") is True, "compliance pipeline-only mismatch")
    require(compliance_report.get("output_valid_for_research_backtest") is False, "compliance research/backtest claim detected")
    require(compliance_report.get("output_valid_for_edge_claim") is False, "compliance edge claim detected")
    require(compliance_report.get("broad_acquisition_ready") is False, "compliance broad readiness claim detected")
    require(compliance_report.get("source_manifest_acquisition_ready") is False, "compliance source manifest readiness claim detected")

    return artifacts, exists, valid


def validate_csv() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(OUTPUT_CSV.exists(), f"output CSV missing: {OUTPUT_CSV}")
    rows: list[dict[str, str]] = []
    with OUTPUT_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        observed_schema = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    row_count = len(rows)
    symbols: set[str] = set()
    scopes: set[str] = set()
    hours: list[int] = []
    complete_count = 0
    incomplete_count = 0
    incomplete_rows: list[dict[str, str]] = []
    affected_row: dict[str, str] | None = None
    duplicate_hour_count = 0
    seen_hours: set[int] = set()
    invalid_numeric_row_count = 0
    invalid_price_relation_row_count = 0
    negative_volume_row_count = 0
    nan_inf_row_count = 0
    provenance_missing_row_count = 0
    source_time_invalid_row_count = 0
    complete_row_source_count_not_60 = 0
    policy_clean_false_row_count = 0
    unexpected_quarantine_row_count = 0

    for row in rows:
        row_has_invalid_numeric = False
        row_has_nan_inf = False
        row_has_negative_volume = False
        row_has_bad_price_relation = False
        symbols.add(row.get("instrument_name", ""))
        scopes.add(row.get("build_scope", ""))

        hour = parse_int(row.get("hour_start_epoch_ms"))
        if hour is None:
            row_has_invalid_numeric = True
        else:
            hours.append(hour)
            if hour in seen_hours:
                duplicate_hour_count += 1
            seen_hours.add(hour)
            expected_iso = datetime.fromtimestamp(hour / 1000, tz=timezone.utc).isoformat()
            if row.get("hour_start_iso_utc") != expected_iso:
                row_has_invalid_numeric = True

        numeric_values: dict[str, Decimal] = {}
        for field in ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote"]:
            parsed, is_nan_inf = parse_decimal(row.get(field))
            if parsed is None:
                row_has_invalid_numeric = True
                row_has_nan_inf = row_has_nan_inf or is_nan_inf
            else:
                numeric_values[field] = parsed

        if all(field in numeric_values for field in ["open", "high", "low", "close"]):
            high = numeric_values["high"]
            low = numeric_values["low"]
            open_ = numeric_values["open"]
            close = numeric_values["close"]
            if high < open_ or high < close or high < low or low > open_ or low > close or low > high:
                row_has_bad_price_relation = True

        for field in ["vol", "vol_ccy", "vol_quote"]:
            value = numeric_values.get(field)
            if value is not None and value < 0:
                row_has_negative_volume = True

        source_row_count = parse_int(row.get("source_row_count"))
        source_first = parse_int(row.get("source_first_open_time"))
        source_last = parse_int(row.get("source_last_open_time"))
        if source_row_count is None or source_first is None or source_last is None:
            row_has_invalid_numeric = True
            source_time_invalid_row_count += 1
        elif source_first > source_last:
            source_time_invalid_row_count += 1

        complete = parse_bool(row.get("complete_hour"))
        if complete:
            complete_count += 1
            if source_row_count != 60:
                complete_row_source_count_not_60 += 1
        else:
            incomplete_count += 1
            incomplete_rows.append(row)

        if row.get("hour_start_iso_utc") == EXPECTED_AFFECTED_HOUR:
            affected_row = row

        if not parse_bool(row.get("policy_clean_build")):
            policy_clean_false_row_count += 1

        quarantine_applied = parse_bool(row.get("quarantine_applied"))
        if quarantine_applied and row.get("hour_start_iso_utc") != EXPECTED_AFFECTED_HOUR:
            unexpected_quarantine_row_count += 1

        for field in ["source_zip_sha256", "source_csv_file", "source_date"]:
            if not str(row.get(field, "")).strip():
                provenance_missing_row_count += 1
                break

        invalid_numeric_row_count += int(row_has_invalid_numeric or row_has_bad_price_relation)
        invalid_price_relation_row_count += int(row_has_bad_price_relation)
        negative_volume_row_count += int(row_has_negative_volume)
        nan_inf_row_count += int(row_has_nan_inf)

    output_hours_monotonic = all(left < right for left, right in zip(hours, hours[1:]))
    require(observed_schema == EXPECTED_OUTPUT_SCHEMA, "output CSV schema mismatch")
    require(row_count == EXPECTED_OUTPUT_ROWS, f"output row count mismatch: {row_count}")
    require(symbols == {TARGET_SYMBOL}, f"unexpected symbols: {sorted(symbols)}")
    require(scopes == {BUILD_SCOPE}, f"unexpected build scopes: {sorted(scopes)}")
    require(len(seen_hours) == EXPECTED_OUTPUT_ROWS, "unique hour count mismatch")
    require(duplicate_hour_count == 0, "duplicate output hours detected")
    require(output_hours_monotonic, "output hours are not strictly monotonic")
    require(complete_count == EXPECTED_COMPLETE_ROWS, "complete hour count mismatch")
    require(incomplete_count == EXPECTED_INCOMPLETE_ROWS, "incomplete hour count mismatch")
    require(len(incomplete_rows) == 1, "expected exactly one incomplete hour")
    require(affected_row is not None, "affected hour missing from output")
    require(parse_bool(affected_row.get("complete_hour")) is False, "affected hour marked complete")
    require(parse_int(affected_row.get("source_row_count")) == EXPECTED_AFFECTED_HOUR_SOURCE_ROWS, "affected hour source row count mismatch")
    require(parse_bool(affected_row.get("quarantine_applied")) is True, "affected hour quarantine flag missing")
    reason = str(affected_row.get("incomplete_reason", "")).lower()
    require("material" in reason and "conflict" in reason and "quarantin" in reason, "affected hour incomplete reason mismatch")
    require(complete_row_source_count_not_60 == 0, "complete row with source_row_count != 60 detected")
    require(policy_clean_false_row_count == 0, "policy_clean_build false row detected")
    require(unexpected_quarantine_row_count == 0, "unexpected quarantine-applied hour detected")
    require(invalid_numeric_row_count == 0, "numeric sanity failure")
    require(negative_volume_row_count == 0, "negative volume row detected")
    require(nan_inf_row_count == 0, "NaN/inf row detected")
    require(provenance_missing_row_count == 0, "missing row provenance detected")
    require(source_time_invalid_row_count == 0, "invalid source time provenance detected")

    output_report = {
        "output_csv_exists": True,
        "output_csv_path": str(OUTPUT_CSV),
        "output_csv_row_count": row_count,
        "output_schema": observed_schema,
        "output_schema_validated": True,
        "output_symbol_count": len(symbols),
        "output_observed_symbol": TARGET_SYMBOL if symbols == {TARGET_SYMBOL} else sorted(symbols),
        "output_hour_count": row_count,
        "output_unique_hour_count": len(seen_hours),
        "output_duplicate_hour_count": duplicate_hour_count,
        "output_hours_monotonic": output_hours_monotonic,
        "complete_1h_row_count": complete_count,
        "incomplete_1h_row_count": incomplete_count,
        "all_hours_complete": incomplete_count == 0,
        "affected_hour_utc": EXPECTED_AFFECTED_HOUR,
        "affected_hour_marked_complete": parse_bool(affected_row.get("complete_hour")),
        "affected_hour_source_row_count": parse_int(affected_row.get("source_row_count")),
        "quarantine_applied_to_affected_hour": parse_bool(affected_row.get("quarantine_applied")),
        "affected_hour_incomplete_reason": affected_row.get("incomplete_reason"),
        "complete_row_source_count_not_60": complete_row_source_count_not_60,
        "policy_clean_false_row_count": policy_clean_false_row_count,
        "unexpected_quarantine_row_count": unexpected_quarantine_row_count,
        "build_scope": BUILD_SCOPE,
    }
    numeric_report = {
        "numeric_sanity_validated": True,
        "invalid_numeric_row_count": invalid_numeric_row_count,
        "invalid_price_relation_row_count": invalid_price_relation_row_count,
        "negative_volume_row_count": negative_volume_row_count,
        "nan_inf_row_count": nan_inf_row_count,
        "source_time_invalid_row_count": source_time_invalid_row_count,
        "ohlc_numeric_validated": True,
        "volume_fields_numeric_validated": True,
        "high_low_relationship_validated": True,
        "no_negative_volume": True,
        "no_nan_inf": True,
    }
    row_provenance_report = {
        "row_provenance_validated": True,
        "provenance_missing_row_count": provenance_missing_row_count,
        "source_zip_sha256_values_present": True,
        "source_csv_names_present": True,
        "source_dates_present": True,
    }
    return output_report, numeric_report, row_provenance_report


def validate_quarantine_artifacts(artifacts: dict[str, Any]) -> dict[str, Any]:
    duplicate_audit = artifacts["exact_duplicate_audit"]
    quarantine_audit = artifacts["material_conflict_audit"]
    gap_report = artifacts["gap_report"]

    dropped_rows = duplicate_audit.get("dropped_rows")
    quarantined_rows = quarantine_audit.get("quarantined_rows")
    require(isinstance(dropped_rows, list), "duplicate audit dropped_rows missing")
    require(isinstance(quarantined_rows, list), "quarantine audit quarantined_rows missing")
    require(duplicate_audit.get("exact_duplicate_drop_audit_created") is True, "duplicate audit not created")
    require(duplicate_audit.get("exact_duplicate_drop_allowed") is True, "duplicate drop not allowed by audit")
    require(duplicate_audit.get("exact_duplicate_rows_dropped") == EXPECTED_EXACT_DUPLICATES_DROPPED, "duplicate audit count mismatch")
    require(len(dropped_rows) == EXPECTED_EXACT_DUPLICATES_DROPPED, "duplicate audit row list count mismatch")
    require(all(row.get("dropped") is True for row in dropped_rows), "duplicate audit row not marked dropped")
    require(all(row.get("selected_for_output") is False for row in dropped_rows), "duplicate audit row selected for output")

    require(quarantine_audit.get("material_conflict_quarantine_audit_created") is True, "quarantine audit not created")
    require(quarantine_audit.get("conflict_resolution_policy") == CONFLICT_RESOLUTION_POLICY, "quarantine audit policy mismatch")
    require(quarantine_audit.get("choose_conflicting_row_allowed") is False, "quarantine audit allows choosing row")
    require(quarantine_audit.get("average_conflicting_rows_allowed") is False, "quarantine audit allows averaging")
    require(quarantine_audit.get("merge_conflicting_rows_allowed") is False, "quarantine audit allows merging")
    require(quarantine_audit.get("material_conflict_rows_quarantined") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED, "quarantine audit count mismatch")
    require(len(quarantined_rows) == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED, "quarantine audit row list count mismatch")
    require(all(row.get("quarantined") is True for row in quarantined_rows), "quarantine audit row not marked quarantined")
    require(all(row.get("selected_for_output") is False for row in quarantined_rows), "quarantine audit row selected for output")
    require(all(row.get("averaged") is False for row in quarantined_rows), "quarantine audit row averaged")
    require(all(row.get("merged") is False for row in quarantined_rows), "quarantine audit row merged")
    require(all(row.get("synthesized_replacement") is False for row in quarantined_rows), "quarantine audit synthesized replacement")
    require(all(row.get("affected_hour_utc") == EXPECTED_AFFECTED_HOUR for row in quarantined_rows), "quarantine audit affected hour mismatch")

    require(gap_report.get("gap_incomplete_hour_report_created") is True, "gap report not created")
    require(gap_report.get("complete_hour_count") == EXPECTED_COMPLETE_ROWS, "gap report complete count mismatch")
    require(gap_report.get("incomplete_hour_count") == EXPECTED_INCOMPLETE_ROWS, "gap report incomplete count mismatch")
    require(gap_report.get("all_hours_complete") is False, "gap report claims all hours complete")
    require(gap_report.get("affected_hour_utc") == EXPECTED_AFFECTED_HOUR, "gap report affected hour mismatch")
    require(gap_report.get("affected_hour_marked_complete") is False, "gap report affected hour marked complete")
    require(gap_report.get("affected_hour_source_row_count") == EXPECTED_AFFECTED_HOUR_SOURCE_ROWS, "gap report affected source count mismatch")
    require(gap_report.get("synthetic_fill_used") is False, "gap report synthetic fill detected")
    require(gap_report.get("forward_fill_used") is False, "gap report forward fill detected")
    require(gap_report.get("backfill_used") is False, "gap report backfill detected")

    return {
        "approved_material_conflict_policy_validated": True,
        "conflict_resolution_policy": CONFLICT_RESOLUTION_POLICY,
        "exact_duplicate_rows_dropped": EXPECTED_EXACT_DUPLICATES_DROPPED,
        "exact_duplicate_drop_audit_row_count": len(dropped_rows),
        "material_conflict_rows_quarantined": EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "material_conflict_quarantine_audit_row_count": len(quarantined_rows),
        "affected_hour_utc": EXPECTED_AFFECTED_HOUR,
        "affected_hour_marked_complete": False,
        "affected_hour_source_row_count": EXPECTED_AFFECTED_HOUR_SOURCE_ROWS,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "choosing_averaging_merging_conflict_disallowed": True,
        "quarantined_rows_selected_for_output_count": 0,
    }


def validate_provenance_artifacts(artifacts: dict[str, Any], row_provenance: dict[str, Any]) -> dict[str, Any]:
    provenance = artifacts["provenance_report"]
    execution_summary = artifacts["execution_summary"]
    execution_report = artifacts["execution_report"]
    clean_by_file = provenance.get("clean_source_row_count_after_policy_by_file")
    require(provenance.get("provenance_status") == "POLICY_CLEAN_SINGLE_SYMBOL_PIPELINE_VALIDATION_BUILD_OUTPUT", "provenance status mismatch")
    require(provenance.get("output_csv_path") == str(OUTPUT_CSV), "provenance output path mismatch")
    require(provenance.get("output_row_count") == EXPECTED_OUTPUT_ROWS, "provenance output row count mismatch")
    require(isinstance(clean_by_file, dict), "provenance clean source count by file missing")
    require(sum(clean_by_file.values()) == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY, "provenance clean source row total mismatch")
    require(execution_summary.get("output_csv_path") == str(OUTPUT_CSV), "summary output path mismatch")

    embedded_duplicate = execution_report.get("exact_duplicate_drop_audit")
    embedded_quarantine = execution_report.get("material_conflict_quarantine_audit")
    embedded_gap = execution_report.get("gap_incomplete_hour_report")
    require(isinstance(embedded_duplicate, dict), "execution report duplicate audit link missing")
    require(isinstance(embedded_quarantine, dict), "execution report quarantine audit link missing")
    require(isinstance(embedded_gap, dict), "execution report gap report link missing")
    require(embedded_duplicate.get("exact_duplicate_rows_dropped") == EXPECTED_EXACT_DUPLICATES_DROPPED, "embedded duplicate count mismatch")
    require(embedded_quarantine.get("material_conflict_rows_quarantined") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED, "embedded quarantine count mismatch")
    require(embedded_gap.get("affected_hour_utc") == EXPECTED_AFFECTED_HOUR, "embedded gap affected hour mismatch")

    return {
        "provenance_validated": True,
        "provenance_status": provenance.get("provenance_status"),
        "output_csv_path": str(OUTPUT_CSV),
        "output_row_count": EXPECTED_OUTPUT_ROWS,
        "clean_source_row_count_after_policy": EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "clean_source_file_count": len(clean_by_file),
        "source_zip_sha256_values_present": row_provenance["source_zip_sha256_values_present"],
        "source_csv_names_present": row_provenance["source_csv_names_present"],
        "source_dates_present": row_provenance["source_dates_present"],
        "policy_clean_audit_artifacts_referenced": True,
        "exact_duplicate_drop_audit_referenced": True,
        "material_conflict_quarantine_audit_referenced": True,
        "gap_incomplete_hour_report_referenced": True,
    }


def build_summary(
    preconditions: dict[str, Any],
    artifacts: dict[str, Any],
    json_exists: dict[str, bool],
    json_valid: dict[str, bool],
    output_report: dict[str, Any],
    numeric_report: dict[str, Any],
    quarantine_report: dict[str, Any],
    provenance_report: dict[str, Any],
) -> dict[str, Any]:
    execution_summary = artifacts["execution_summary"]
    replacement_checks = {
        "expected_head": preconditions["head"].startswith(EXPECTED_HEAD),
        "repo_clean_or_only_approved_tool_change": preconditions["repo_clean_or_only_approved_tool_change"],
        "current_next_module": execution_summary.get("next_module") == REQUESTED_MODULE,
        "execution_artifacts_exist": all(json_exists.values()),
        "execution_artifacts_valid_json": all(json_valid.values()),
        "output_csv_exists": output_report["output_csv_exists"],
        "output_rows_expected": output_report["output_csv_row_count"] == EXPECTED_OUTPUT_ROWS,
        "output_schema_validated": output_report["output_schema_validated"],
        "single_symbol_expected": output_report["output_symbol_count"] == 1
        and output_report["output_observed_symbol"] == TARGET_SYMBOL,
        "unique_hours_expected": output_report["output_unique_hour_count"] == EXPECTED_OUTPUT_ROWS,
        "no_duplicate_hours": output_report["output_duplicate_hour_count"] == 0,
        "hours_monotonic": output_report["output_hours_monotonic"],
        "complete_row_count_expected": output_report["complete_1h_row_count"] == EXPECTED_COMPLETE_ROWS,
        "incomplete_row_count_expected": output_report["incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_ROWS,
        "all_hours_not_complete": output_report["all_hours_complete"] is False,
        "affected_hour_incomplete": output_report["affected_hour_marked_complete"] is False,
        "affected_hour_source_rows_expected": output_report["affected_hour_source_row_count"]
        == EXPECTED_AFFECTED_HOUR_SOURCE_ROWS,
        "affected_hour_quarantined": output_report["quarantine_applied_to_affected_hour"] is True,
        "complete_rows_have_60_source_rows": output_report["complete_row_source_count_not_60"] == 0,
        "no_fill_used": quarantine_report["synthetic_fill_used"] is False
        and quarantine_report["forward_fill_used"] is False
        and quarantine_report["backfill_used"] is False,
        "exact_duplicate_drop_count_expected": quarantine_report["exact_duplicate_rows_dropped"]
        == EXPECTED_EXACT_DUPLICATES_DROPPED,
        "material_conflict_quarantine_count_expected": quarantine_report["material_conflict_rows_quarantined"]
        == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "clean_source_rows_expected": provenance_report["clean_source_row_count_after_policy"]
        == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "numeric_sanity_validated": numeric_report["numeric_sanity_validated"],
        "provenance_validated": provenance_report["provenance_validated"],
        "strict_3y_completeness_not_claimed": execution_summary.get("strict_3y_completeness_claimed") is False,
        "not_research_backtest_edge": execution_summary.get("output_valid_for_research_backtest") is False
        and execution_summary.get("output_valid_for_edge_claim") is False,
        "not_broad_or_source_manifest_ready": execution_summary.get("broad_acquisition_ready") is False
        and execution_summary.get("source_manifest_acquisition_ready") is False,
        "no_new_download_api_browse_build_aggregation_by_validator": all(
            value is False for value in VALIDATOR_DANGEROUS_FLAGS.values()
        ),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks did not all pass")

    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "head": preconditions["head"],
        "tracked_python_count_at_validator_run": preconditions["tracked_python_count"],
        "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_status": PASS_STATUS,
        "policy_clean_rebuild_execution_validated": True,
        "target_symbol": TARGET_SYMBOL,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START,
        "max_available_end_date": MAX_AVAILABLE_END,
        "output_csv_exists": output_report["output_csv_exists"],
        "output_csv_row_count": output_report["output_csv_row_count"],
        "output_schema_validated": output_report["output_schema_validated"],
        "output_symbol_count": output_report["output_symbol_count"],
        "output_observed_symbol": output_report["output_observed_symbol"],
        "output_hour_count": output_report["output_hour_count"],
        "output_unique_hour_count": output_report["output_unique_hour_count"],
        "output_duplicate_hour_count": output_report["output_duplicate_hour_count"],
        "output_hours_monotonic": output_report["output_hours_monotonic"],
        "complete_1h_row_count": output_report["complete_1h_row_count"],
        "incomplete_1h_row_count": output_report["incomplete_1h_row_count"],
        "all_hours_complete": output_report["all_hours_complete"],
        "affected_hour_utc": output_report["affected_hour_utc"],
        "affected_hour_marked_complete": output_report["affected_hour_marked_complete"],
        "affected_hour_source_row_count": output_report["affected_hour_source_row_count"],
        "quarantine_applied_to_affected_hour": output_report["quarantine_applied_to_affected_hour"],
        "exact_duplicate_rows_dropped": quarantine_report["exact_duplicate_rows_dropped"],
        "material_conflict_rows_quarantined": quarantine_report["material_conflict_rows_quarantined"],
        "clean_source_row_count_after_policy": provenance_report["clean_source_row_count_after_policy"],
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "numeric_sanity_validated": numeric_report["numeric_sanity_validated"],
        "invalid_numeric_row_count": numeric_report["invalid_numeric_row_count"],
        "negative_volume_row_count": numeric_report["negative_volume_row_count"],
        "nan_inf_row_count": numeric_report["nan_inf_row_count"],
        "provenance_validated": provenance_report["provenance_validated"],
        "output_is_policy_clean_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "no_new_download": True,
        "new_download_performed_by_validator": False,
        "data_build_performed_by_validator": False,
        "aggregation_performed_by_validator": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "validator_dangerous_flags": VALIDATOR_DANGEROUS_FLAGS,
        "validator_p0_count": 0,
        "validator_p1_count": len(P1_ATTENTION_ITEMS),
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": len(P1_ATTENTION_ITEMS),
        "p1_attention_items": P1_ATTENTION_ITEMS,
        "current_evidence_chain_quality_after_validator": AFTER_QUALITY,
        "next_module": NEXT_MODULE_PASS,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    return summary


def write_reports(
    summary: dict[str, Any],
    output_report: dict[str, Any],
    numeric_report: dict[str, Any],
    quarantine_report: dict[str, Any],
    provenance_report: dict[str, Any],
    artifacts: dict[str, Any],
) -> None:
    validator_report = {
        "module_name": MODULE_NAME,
        "generated_at_utc": summary["generated_at_utc"],
        "validator_status": summary[
            "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_status"
        ],
        "policy_clean_rebuild_execution_validated": summary["policy_clean_rebuild_execution_validated"],
        "artifact_inputs": {label: str(path) for label, path in JSON_ARTIFACTS.items()},
        "output_csv_path": str(OUTPUT_CSV),
        "previous_execution_status": artifacts["execution_summary"].get(
            "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_status"
        ),
        "next_module": summary["next_module"],
        "no_new_download_api_browse_build_aggregation_by_validator": True,
        "validator_dangerous_flags": VALIDATOR_DANGEROUS_FLAGS,
    }
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator.json",
        validator_report,
    )
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_output_validation_report.json",
        output_report,
    )
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_numeric_sanity_report.json",
        numeric_report,
    )
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_quarantine_validation_report.json",
        quarantine_report,
    )
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_provenance_validation_report.json",
        provenance_report,
    )
    write_json(
        OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_summary.json",
        summary,
    )


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_status": BLOCKED_STATUS,
        "policy_clean_rebuild_execution_validated": False,
        "target_symbol": TARGET_SYMBOL,
        "validator_p0_count": 1,
        "validator_p1_count": len(P1_ATTENTION_ITEMS),
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": len(P1_ATTENTION_ITEMS),
        "blocker": message,
        "current_evidence_chain_quality_after_validator": "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_VALIDATION_BLOCKED",
        "next_module": NEXT_MODULE_BLOCKED,
        "replacement_checks_all_true": False,
        **VALIDATOR_DANGEROUS_FLAGS,
    }


def main() -> None:
    try:
        preconditions = validate_preconditions()
        artifacts, json_exists, json_valid = validate_existing_artifacts()
        output_report, numeric_report, row_provenance = validate_csv()
        quarantine_report = validate_quarantine_artifacts(artifacts)
        provenance_report = validate_provenance_artifacts(artifacts, row_provenance)
        summary = build_summary(
            preconditions,
            artifacts,
            json_exists,
            json_valid,
            output_report,
            numeric_report,
            quarantine_report,
            provenance_report,
        )
        write_reports(summary, output_report, numeric_report, quarantine_report, provenance_report, artifacts)
        print(json.dumps(summary, indent=2, sort_keys=True))
    except ValidationBlocked as exc:
        blocked = blocked_payload(str(exc))
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
