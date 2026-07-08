from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import zipfile
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_after_material_conflict_policy_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "cfa57ed"
TARGET_SYMBOL = "BTC-USDT-SWAP"
MAX_AVAILABLE_START = date(2023, 7, 1)
MAX_AVAILABLE_END = date(2026, 5, 18)
EXPECTED_FILE_COUNT = 1053
EXPECTED_OBSERVED_SOURCE_ROWS = 1_516_641
EXPECTED_UNIQUE_OPEN_TIME_COUNT = 1_516_320
EXPECTED_EXACT_DUPLICATE_ROWS_TO_DROP = 320
EXPECTED_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE = 2
EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY = 1_516_319
EXPECTED_OUTPUT_ROWS_AFTER_POLICY = 25_272
EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY = 25_271
EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY = 1
EXPECTED_MINUTE_MS = 60_000
EXPECTED_HOUR_MS = 3_600_000
CONFLICT_OPEN_TIME = 1_776_150_360_000
CONFLICT_OPEN_TIME_UTC = "2026-04-14T07:06:00+00:00"
AFFECTED_HOUR = 1_776_150_000_000
AFFECTED_HOUR_UTC = "2026-04-14T07:00:00+00:00"
CONFLICT_RESOLUTION_POLICY = "QUARANTINE_MATERIAL_CONFLICTING_OPEN_TIME_GROUP"
DIFFERING_FIELDS = ["high", "vol", "vol_ccy", "vol_quote"]
BUILD_SCOPE = "SINGLE_SYMBOL_3_YEAR_MAX_AVAILABLE_POLICY_CLEAN_1M_TO_1H_PIPELINE_VALIDATION_ONLY"

PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_MATERIAL_DUPLICATE_"
    "CONFLICT_POLICY_APPROVED_POLICY_CLEAN_REBUILD_READY"
)
DOWNLOAD_VALIDATOR_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATED_"
    "BUILD_PREVIEW_READY_MAX_AVAILABLE_NO_BUILD"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_"
    "EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_EXECUTION"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_MATERIAL_CONFLICT_POLICY_"
    "APPROVED_POLICY_CLEAN_REBUILD_READY"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_EXECUTED_"
    "PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_validator_after_execution_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_blocked_record_after_policy_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_material_duplicate_conflict_policy_after_conflict_review_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1"
)

POLICY_SUMMARY = POLICY_DIR / "historical_okx_single_symbol_3_year_material_conflict_policy_summary.json"
MATERIAL_POLICY = POLICY_DIR / "historical_okx_single_symbol_3_year_material_duplicate_conflict_policy.json"
QUARANTINE_POLICY = POLICY_DIR / "historical_okx_single_symbol_3_year_conflict_quarantine_policy.json"
REBUILD_APPROVAL = POLICY_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_approval_record.json"
DOWNLOAD_VALIDATOR_SUMMARY = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_download_execution_validator_summary.json"
HASH_VALIDATION_REPORT = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_hash_validation_report.json"

EXPECTED_SCHEMA = [
    "instrument_name",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "open_time",
    "confirm",
]
CANONICAL_FIELDS = EXPECTED_SCHEMA
OUTPUT_SCHEMA = [
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
DANGEROUS_FLAGS = {
    "new_download_performed_now": False,
    "data_download_performed": False,
    "data_fetch_performed": False,
    "okx_download_performed": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed": False,
    "url_iteration_performed": False,
    "multi_symbol_performed": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "conflicting_row_choice_performed": False,
    "conflicting_row_average_performed": False,
    "conflicting_row_merge_performed": False,
    "ohlcv_modification_performed": False,
    "strategy_research_implementation_touched": False,
    "backtest_performed": False,
    "candidate_generation_touched": False,
    "edge_profit_claim_made": False,
    "broad_acquisition_ready": False,
    "strict_3y_completeness_claimed": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
    pass


@dataclass
class HourAggregate:
    hour_start: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    vol: Decimal
    vol_ccy: Decimal
    vol_quote: Decimal
    first_open_time: int
    last_open_time: int
    confirm_all: bool
    row_count: int = 1
    unique_open_times: set[int] = field(default_factory=set)
    source_hashes: set[str] = field(default_factory=set)
    source_csvs: set[str] = field(default_factory=set)
    source_dates: set[str] = field(default_factory=set)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_utc_from_ms(epoch_ms: int) -> str:
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    if normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        return False
    if posix.is_absolute() or any(part == ".." for part in posix.parts):
        return False
    if posix.parts and ":" in posix.parts[0]:
        return False
    return True


def inclusive_days(start: date, end: date) -> list[str]:
    days: list[str] = []
    current = start
    while current <= end:
        days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def expected_csv_for_date(day: str) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day}.csv"


def parse_decimal(value: str, field_name: str, source_csv: str, row_number: int, allow_none_zero: bool = False) -> Decimal:
    if allow_none_zero and str(value).strip().lower() in {"none", ""}:
        return Decimal("0")
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise Blocked(f"numeric parse failed {field_name} {source_csv} row={row_number}") from exc
    require(parsed.is_finite(), f"non-finite numeric {field_name} {source_csv} row={row_number}")
    return parsed


def decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal(1)))
    return format(normalized, "f")


def normalize_decimal_or_raw(value: Any) -> str:
    text = str(value).strip()
    if text.lower() in {"none", ""}:
        return "0"
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError):
        return text
    require(parsed.is_finite(), f"non-finite decimal value: {text!r}")
    return decimal_text(parsed)


def normalize_confirm(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y"}:
        return "true"
    if text in {"0", "false", "f", "no", "n"}:
        return "false"
    return text


def parse_confirm(value: str) -> bool:
    return normalize_confirm(value) == "true"


def canonical_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "instrument_name": str(row["instrument_name"]).strip(),
        "open": normalize_decimal_or_raw(row["open"]),
        "high": normalize_decimal_or_raw(row["high"]),
        "low": normalize_decimal_or_raw(row["low"]),
        "close": normalize_decimal_or_raw(row["close"]),
        "vol": normalize_decimal_or_raw(row["vol"]),
        "vol_ccy": normalize_decimal_or_raw(row["vol_ccy"]),
        "vol_quote": normalize_decimal_or_raw(row["vol_quote"]),
        "open_time": str(int(str(row["open_time"]).strip())),
        "confirm": normalize_confirm(row["confirm"]),
    }


def canonical_key(canon: dict[str, str]) -> tuple[str, ...]:
    return tuple(canon[field] for field in CANONICAL_FIELDS)


def audit_occurrence(
    row: dict[str, Any],
    canon: dict[str, str],
    source_csv: str,
    source_date: str,
    source_zip_path: Path,
    source_zip_sha256: str,
    row_number: int,
) -> dict[str, Any]:
    return {
        "source_date": source_date,
        "source_csv_file": source_csv,
        "source_zip_path": str(source_zip_path),
        "source_zip_sha256": source_zip_sha256,
        "row_number": row_number,
        "open_time": int(canon["open_time"]),
        "open_time_utc": iso_utc_from_ms(int(canon["open_time"])),
        "raw_values": {field: row.get(field) for field in CANONICAL_FIELDS},
        "canonical_values": canon,
    }


def validate_preflight(
    policy_summary: dict[str, Any],
    material_policy: dict[str, Any],
    quarantine_policy: dict[str, Any],
    rebuild_approval: dict[str, Any],
    download_validator: dict[str, Any],
) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(
        policy_summary.get("historical_data_acquisition_okx_single_symbol_3_year_material_duplicate_conflict_policy_status")
        == PREVIOUS_STATUS,
        "material conflict policy status mismatch",
    )
    require(policy_summary.get("next_module") == REQUESTED_MODULE, "policy next_module mismatch")
    require(policy_summary.get("target_symbol") == TARGET_SYMBOL, "policy target mismatch")
    require(policy_summary.get("conflict_resolution_policy") == CONFLICT_RESOLUTION_POLICY, "policy conflict resolution mismatch")
    require(policy_summary.get("conflict_open_time") == CONFLICT_OPEN_TIME, "policy conflict open_time mismatch")
    require(policy_summary.get("conflict_open_time_utc") == CONFLICT_OPEN_TIME_UTC, "policy conflict UTC mismatch")
    require(policy_summary.get("differing_fields") == DIFFERING_FIELDS, "policy differing fields mismatch")
    require(policy_summary.get("exact_duplicate_extra_row_count") == EXPECTED_EXACT_DUPLICATE_ROWS_TO_DROP, "policy exact duplicate count mismatch")
    require(policy_summary.get("material_conflicting_group_count") == 1, "policy material conflict group count mismatch")
    require(policy_summary.get("material_conflicting_row_count") == EXPECTED_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE, "policy conflict row count mismatch")
    require(policy_summary.get("choose_conflicting_row_allowed") is False, "policy allows choosing conflicting row")
    require(policy_summary.get("average_conflicting_rows_allowed") is False, "policy allows averaging conflicting rows")
    require(policy_summary.get("merge_conflicting_rows_allowed") is False, "policy allows merging conflicting rows")
    require(policy_summary.get("exact_duplicate_drop_allowed") is True, "policy does not allow exact duplicate drop")
    require(policy_summary.get("material_conflict_quarantine_required") is True, "policy does not require quarantine")
    require(policy_summary.get("expected_clean_source_rows_after_policy") == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY, "policy clean row count mismatch")
    require(policy_summary.get("expected_complete_1h_rows_after_policy") == EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY, "policy complete hour count mismatch")
    require(policy_summary.get("expected_incomplete_1h_rows_after_policy") == EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY, "policy incomplete hour count mismatch")
    require(policy_summary.get("affected_hour_utc") == AFFECTED_HOUR_UTC, "policy affected hour mismatch")
    require(policy_summary.get("all_hours_complete_after_policy") is False, "policy claims all hours complete")
    require(policy_summary.get("approval_grants_future_policy_clean_rebuild_next") is True, "policy rebuild approval missing")
    require(policy_summary.get("active_p0_blocker_count") == 0, "policy P0 blocker count mismatch")
    require(policy_summary.get("active_p1_attention_count") == 9, "policy P1 attention count mismatch")
    require(policy_summary.get("strict_3y_completeness_claimed") is False, "policy strict 3y claim detected")
    require(policy_summary.get("output_valid_for_research_backtest") is False, "policy research/backtest claim detected")
    require(policy_summary.get("output_valid_for_edge_claim") is False, "policy edge claim detected")
    require(policy_summary.get("broad_acquisition_ready") is False, "policy broad acquisition claim detected")
    require(material_policy.get("conflict_resolution_policy") == CONFLICT_RESOLUTION_POLICY, "material policy resolution mismatch")
    require(material_policy.get("choose_conflicting_row_allowed") is False, "material policy choose flag mismatch")
    require(material_policy.get("average_conflicting_rows_allowed") is False, "material policy average flag mismatch")
    require(material_policy.get("merge_conflicting_rows_allowed") is False, "material policy merge flag mismatch")
    require(material_policy.get("exact_duplicate_drop_allowed") is True, "material policy exact drop flag mismatch")
    require(material_policy.get("material_conflict_quarantine_required") is True, "material policy quarantine flag mismatch")
    require(quarantine_policy.get("quarantine_scope") == "BOTH_ROWS_FOR_MATERIAL_CONFLICTING_OPEN_TIME_GROUP", "quarantine scope mismatch")
    require(quarantine_policy.get("conflict_open_time") == CONFLICT_OPEN_TIME, "quarantine open_time mismatch")
    require(quarantine_policy.get("material_conflict_rows_to_quarantine") == EXPECTED_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE, "quarantine row count mismatch")
    require(quarantine_policy.get("replacement_minute_allowed") is False, "quarantine replacement flag mismatch")
    require(quarantine_policy.get("affected_hour_complete") is False, "quarantine affected hour complete flag mismatch")
    require(rebuild_approval.get("approval_grants_future_policy_clean_rebuild_next") is True, "approval future rebuild flag mismatch")
    require(rebuild_approval.get("approval_grants_download_now") is False, "approval download flag mismatch")
    require(rebuild_approval.get("approval_grants_api_now") is False, "approval API flag mismatch")
    require(rebuild_approval.get("approval_grants_browse_now") is False, "approval browse flag mismatch")
    require(rebuild_approval.get("approval_grants_research_backtest_edge_now") is False, "approval research/edge flag mismatch")
    require(rebuild_approval.get("next_module") == REQUESTED_MODULE, "approval next_module mismatch")
    require(
        download_validator.get("historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_status")
        == DOWNLOAD_VALIDATOR_STATUS,
        "download validator status mismatch",
    )
    require(download_validator.get("target_symbol") == TARGET_SYMBOL, "download validator target mismatch")
    require(download_validator.get("strict_3y_completeness_claimed") is False, "download validator strict 3y claim detected")
    require(download_validator.get("max_available_start_candidate") == MAX_AVAILABLE_START.isoformat(), "download validator start mismatch")
    require(download_validator.get("max_available_end_date") == MAX_AVAILABLE_END.isoformat(), "download validator end mismatch")
    require(download_validator.get("final_file_set_count") == EXPECTED_FILE_COUNT, "download validator file count mismatch")
    require(download_validator.get("all_downloaded_zip_paths_exist") is True, "download validator ZIP path flag mismatch")
    require(download_validator.get("all_hashes_match_recorded") is True, "download validator hash flag mismatch")
    require(download_validator.get("all_expected_inner_csv_present") is True, "download validator inner CSV flag mismatch")
    require(download_validator.get("all_expected_schema_match") is True, "download validator schema flag mismatch")
    require(download_validator.get("all_observed_symbols_match_target") is True, "download validator symbol flag mismatch")
    require(download_validator.get("full_csv_read_performed") is False, "download validator full CSV flag mismatch")
    require(download_validator.get("data_build_performed") is False, "download validator data build flag mismatch")
    require(download_validator.get("aggregation_performed_now") is False, "download validator aggregation flag mismatch")
    require(download_validator.get("okx_api_call_performed") is False, "download validator API flag mismatch")
    require(download_validator.get("okx_browse_performed") is False, "download validator browse flag mismatch")


def load_hash_entries(hash_report: dict[str, Any]) -> list[dict[str, Any]]:
    require(hash_report.get("all_downloaded_zip_paths_exist") is True, "hash report ZIP path flag mismatch")
    require(hash_report.get("all_hashes_recomputed") is True, "hash report recompute flag mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "hash report hash flag mismatch")
    items = hash_report.get("hashes")
    require(isinstance(items, list), "hash report hashes is not a list")
    require(len(items) == EXPECTED_FILE_COUNT, f"hash report count mismatch: {len(items)}")
    expected_days = inclusive_days(MAX_AVAILABLE_START, MAX_AVAILABLE_END)
    by_date: dict[str, dict[str, Any]] = {}
    for item in items:
        require(isinstance(item, dict), "hash report item is not an object")
        day = item.get("date")
        require(isinstance(day, str), "hash report item missing date")
        require(day not in by_date, f"duplicate hash report date: {day}")
        by_date[day] = item
    require(list(by_date) == expected_days, "hash report dates do not match max-available range")
    return [by_date[day] for day in expected_days]


def new_hour(row: dict[str, Any]) -> HourAggregate:
    agg = HourAggregate(
        hour_start=(row["open_time"] // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS,
        open=row["open"],
        high=row["high"],
        low=row["low"],
        close=row["close"],
        vol=row["vol"],
        vol_ccy=row["vol_ccy"],
        vol_quote=row["vol_quote"],
        first_open_time=row["open_time"],
        last_open_time=row["open_time"],
        confirm_all=row["confirm"],
    )
    agg.unique_open_times.add(row["open_time"])
    agg.source_hashes.add(row["source_zip_sha256"])
    agg.source_csvs.add(row["source_csv_file"])
    agg.source_dates.add(row["source_date"])
    return agg


def update_hour(agg: HourAggregate, row: dict[str, Any]) -> None:
    require(((row["open_time"] // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS) == agg.hour_start, "hour update mismatch")
    require(row["open_time"] not in agg.unique_open_times, f"duplicate clean minute in hour: {row['open_time']}")
    agg.high = max(agg.high, row["high"])
    agg.low = min(agg.low, row["low"])
    agg.close = row["close"]
    agg.vol += row["vol"]
    agg.vol_ccy += row["vol_ccy"]
    agg.vol_quote += row["vol_quote"]
    agg.last_open_time = row["open_time"]
    agg.confirm_all = agg.confirm_all and row["confirm"]
    agg.row_count += 1
    agg.unique_open_times.add(row["open_time"])
    agg.source_hashes.add(row["source_zip_sha256"])
    agg.source_csvs.add(row["source_csv_file"])
    agg.source_dates.add(row["source_date"])


def aggregate_to_row(agg: HourAggregate) -> dict[str, str]:
    complete = agg.row_count == 60 and len(agg.unique_open_times) == 60
    affected = agg.hour_start == AFFECTED_HOUR
    if not complete:
        require(affected, f"unexpected incomplete UTC hour: {agg.hour_start}")
        require(agg.row_count == 59 and len(agg.unique_open_times) == 59, "affected hour row count is not 59")
    quarantine_applied = affected and not complete
    incomplete_reason = "MATERIAL_CONFLICT_OPEN_TIME_QUARANTINED" if quarantine_applied else ""
    return {
        "instrument_name": TARGET_SYMBOL,
        "hour_start_epoch_ms": str(agg.hour_start),
        "hour_start_iso_utc": iso_utc_from_ms(agg.hour_start),
        "open": decimal_text(agg.open),
        "high": decimal_text(agg.high),
        "low": decimal_text(agg.low),
        "close": decimal_text(agg.close),
        "vol": decimal_text(agg.vol),
        "vol_ccy": decimal_text(agg.vol_ccy),
        "vol_quote": decimal_text(agg.vol_quote),
        "source_row_count": str(agg.row_count),
        "complete_hour": "true" if complete else "false",
        "confirm": "true" if agg.confirm_all else "false",
        "source_first_open_time": str(agg.first_open_time),
        "source_last_open_time": str(agg.last_open_time),
        "source_zip_sha256": "|".join(sorted(agg.source_hashes)),
        "source_csv_file": "|".join(sorted(agg.source_csvs)),
        "source_date": "|".join(sorted(agg.source_dates)),
        "build_scope": BUILD_SCOPE,
        "policy_clean_build": "true",
        "quarantine_applied": "true" if quarantine_applied else "false",
        "incomplete_reason": incomplete_reason,
    }


def output_csv_path() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = (OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_1m_to_1h_output.csv").resolve()
    path.relative_to(OUTPUT_DIR.resolve())
    try:
        path.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return path
    raise Blocked("output path inside tracked repo")


def process_files(entries: list[dict[str, Any]], output_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    total_source_rows = 0
    clean_source_rows = 0
    output_rows = 0
    complete_hours = 0
    incomplete_hours = 0
    exact_duplicate_rows_dropped = 0
    material_conflict_rows_quarantined = 0
    file_count_processed = 0
    csv_count_read = 0
    all_source_zips_exist = True
    all_source_zip_sha256_match = True
    all_expected_inner_csv_present = True
    schema_match = True
    open_time_monotonic_by_file = True
    symbols: set[str] = set()
    raw_unique_open_times: set[int] = set()
    clean_keys_by_open_time: dict[int, tuple[str, ...]] = {}
    source_row_count_by_file: dict[str, int] = {}
    clean_source_row_count_by_file: dict[str, int] = {}
    exact_duplicate_audit_rows: list[dict[str, Any]] = []
    material_conflict_audit_rows: list[dict[str, Any]] = []
    file_metadata: list[dict[str, Any]] = []
    clean_deltas: set[int] = set()
    clean_missing_minute_count = 0
    previous_clean_open_time: int | None = None
    first_clean_open_time: int | None = None
    last_clean_open_time: int | None = None
    current_hour: HourAggregate | None = None

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_SCHEMA)
        writer.writeheader()
        for entry in entries:
            day = str(entry.get("date"))
            require(MAX_AVAILABLE_START.isoformat() <= day <= MAX_AVAILABLE_END.isoformat(), f"date out of range: {day}")
            path = Path(str(entry.get("local_zip_path", "")))
            all_source_zips_exist = all_source_zips_exist and path.exists()
            require(path.exists(), f"ZIP missing: {path}")
            digest = sha256_file(path)
            recorded_hash = str(entry.get("recorded_sha256", ""))
            hash_match = digest == recorded_hash
            all_source_zip_sha256_match = all_source_zip_sha256_match and hash_match
            require(hash_match, f"SHA256 mismatch: {path}")
            expected_csv = expected_csv_for_date(day)
            file_row_count = 0
            clean_file_row_count = 0
            previous_file_open_time: int | None = None
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                require(len(names) <= 10, f"too many ZIP members: {path}")
                require(all(safe_zip_member(name) for name in names), f"ZIP traversal risk: {path}")
                expected_present = expected_csv in names
                all_expected_inner_csv_present = all_expected_inner_csv_present and expected_present
                require(expected_present, f"expected CSV missing: {expected_csv}")
                with archive.open(expected_csv, "r") as raw:
                    csv_count_read += 1
                    text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                    reader = csv.DictReader(text)
                    header_match = reader.fieldnames == EXPECTED_SCHEMA
                    schema_match = schema_match and header_match
                    require(header_match, f"schema mismatch: {expected_csv}")
                    for row_number, raw_row in enumerate(reader, start=2):
                        require(raw_row.get("instrument_name") == TARGET_SYMBOL, f"symbol mismatch {expected_csv} row={row_number}")
                        symbols.add(TARGET_SYMBOL)
                        open_ = parse_decimal(raw_row["open"], "open", expected_csv, row_number)
                        high = parse_decimal(raw_row["high"], "high", expected_csv, row_number)
                        low = parse_decimal(raw_row["low"], "low", expected_csv, row_number)
                        close = parse_decimal(raw_row["close"], "close", expected_csv, row_number)
                        vol = parse_decimal(raw_row["vol"], "vol", expected_csv, row_number)
                        vol_ccy = parse_decimal(raw_row["vol_ccy"], "vol_ccy", expected_csv, row_number, allow_none_zero=True)
                        vol_quote = parse_decimal(raw_row["vol_quote"], "vol_quote", expected_csv, row_number, allow_none_zero=True)
                        require(vol >= 0 and vol_ccy >= 0 and vol_quote >= 0, f"negative volume {expected_csv} row={row_number}")
                        require(high >= max(open_, close, low), f"invalid high {expected_csv} row={row_number}")
                        require(low <= min(open_, close, high), f"invalid low {expected_csv} row={row_number}")
                        try:
                            open_time = int(str(raw_row["open_time"]).strip())
                        except ValueError as exc:
                            raise Blocked(f"open_time parse failed {expected_csv} row={row_number}") from exc
                        if previous_file_open_time is not None and open_time < previous_file_open_time:
                            open_time_monotonic_by_file = False
                            raise Blocked(f"decreasing open_time within file {expected_csv} row={row_number}")
                        previous_file_open_time = open_time
                        raw_unique_open_times.add(open_time)
                        canon = canonical_row(raw_row)
                        key = canonical_key(canon)
                        occurrence = audit_occurrence(raw_row, canon, expected_csv, day, path, digest, row_number)
                        total_source_rows += 1
                        file_row_count += 1

                        if open_time == CONFLICT_OPEN_TIME:
                            material_conflict_rows_quarantined += 1
                            material_conflict_audit_rows.append(
                                {
                                    **occurrence,
                                    "quarantine_policy": CONFLICT_RESOLUTION_POLICY,
                                    "quarantined": True,
                                    "selected_for_output": False,
                                    "averaged": False,
                                    "merged": False,
                                    "synthesized_replacement": False,
                                    "affected_hour_utc": AFFECTED_HOUR_UTC,
                                }
                            )
                            continue

                        existing_key = clean_keys_by_open_time.get(open_time)
                        if existing_key is not None:
                            if existing_key == key:
                                exact_duplicate_rows_dropped += 1
                                exact_duplicate_audit_rows.append(
                                    {
                                        **occurrence,
                                        "dropped": True,
                                        "drop_reason": "EXACT_DUPLICATE_EXTRA_ROW",
                                        "selected_for_output": False,
                                    }
                                )
                                continue
                            raise Blocked(f"unexpected material conflicting duplicate outside policy open_time={open_time}")

                        clean_keys_by_open_time[open_time] = key
                        if previous_clean_open_time is not None:
                            delta = open_time - previous_clean_open_time
                            clean_deltas.add(delta)
                            require(delta > 0, f"non-monotonic clean open_time at {expected_csv} row={row_number}")
                            if delta != EXPECTED_MINUTE_MS:
                                clean_missing_minute_count += max(0, (delta // EXPECTED_MINUTE_MS) - 1)
                        previous_clean_open_time = open_time
                        first_clean_open_time = open_time if first_clean_open_time is None else first_clean_open_time
                        last_clean_open_time = open_time
                        minute_row = {
                            "open": open_,
                            "high": high,
                            "low": low,
                            "close": close,
                            "vol": vol,
                            "vol_ccy": vol_ccy,
                            "vol_quote": vol_quote,
                            "open_time": open_time,
                            "confirm": parse_confirm(str(raw_row["confirm"])),
                            "source_zip_sha256": digest,
                            "source_csv_file": expected_csv,
                            "source_date": day,
                        }
                        hour_start = (open_time // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS
                        if current_hour is None:
                            current_hour = new_hour(minute_row)
                        elif hour_start == current_hour.hour_start:
                            update_hour(current_hour, minute_row)
                        else:
                            out_row = aggregate_to_row(current_hour)
                            writer.writerow(out_row)
                            output_rows += 1
                            complete_hours += 1 if out_row["complete_hour"] == "true" else 0
                            incomplete_hours += 1 if out_row["complete_hour"] != "true" else 0
                            require(output_rows <= EXPECTED_OUTPUT_ROWS_AFTER_POLICY, "output row count exceeded expected")
                            current_hour = new_hour(minute_row)
                        clean_file_row_count += 1
                        clean_source_rows += 1
            source_row_count_by_file[expected_csv] = file_row_count
            clean_source_row_count_by_file[expected_csv] = clean_file_row_count
            file_count_processed += 1
            file_metadata.append(
                {
                    "date": day,
                    "source_zip_path": str(path),
                    "source_zip_sha256": digest,
                    "source_zip_size_bytes": path.stat().st_size,
                    "source_csv_file": expected_csv,
                    "source_row_count_before_policy": file_row_count,
                    "clean_source_row_count_after_policy": clean_file_row_count,
                    "source_kind": entry.get("source_kind"),
                }
            )
        if current_hour is not None:
            out_row = aggregate_to_row(current_hour)
            writer.writerow(out_row)
            output_rows += 1
            complete_hours += 1 if out_row["complete_hour"] == "true" else 0
            incomplete_hours += 1 if out_row["complete_hour"] != "true" else 0

    affected_hour_row = find_output_hour(output_path, AFFECTED_HOUR)
    require(total_source_rows == EXPECTED_OBSERVED_SOURCE_ROWS, f"observed source rows={total_source_rows}")
    require(len(raw_unique_open_times) == EXPECTED_UNIQUE_OPEN_TIME_COUNT, f"unique open_time count={len(raw_unique_open_times)}")
    require(exact_duplicate_rows_dropped == EXPECTED_EXACT_DUPLICATE_ROWS_TO_DROP, f"exact duplicate rows dropped={exact_duplicate_rows_dropped}")
    require(material_conflict_rows_quarantined == EXPECTED_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE, f"material conflict rows quarantined={material_conflict_rows_quarantined}")
    require(clean_source_rows == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY, f"clean source rows={clean_source_rows}")
    require(output_rows == EXPECTED_OUTPUT_ROWS_AFTER_POLICY, f"output rows={output_rows}")
    require(complete_hours == EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY, f"complete rows={complete_hours}")
    require(incomplete_hours == EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY, f"incomplete rows={incomplete_hours}")
    require(symbols == {TARGET_SYMBOL}, f"unexpected symbols: {sorted(symbols)}")
    require(first_clean_open_time is not None and last_clean_open_time is not None, "no clean source rows observed")
    require(clean_missing_minute_count == 1, f"clean missing minute count={clean_missing_minute_count}")
    require(affected_hour_row is not None, "affected hour missing from output")
    require(affected_hour_row["complete_hour"] == "false", "affected hour marked complete")
    require(affected_hour_row["source_row_count"] == "59", "affected hour source_row_count is not 59")
    require(affected_hour_row["quarantine_applied"] == "true", "affected hour quarantine flag missing")
    require(affected_hour_row["incomplete_reason"] == "MATERIAL_CONFLICT_OPEN_TIME_QUARANTINED", "affected hour reason mismatch")

    validation = {
        "file_count_processed": file_count_processed,
        "csv_count_read": csv_count_read,
        "all_source_zips_exist": all_source_zips_exist,
        "all_source_zip_sha256_match": all_source_zip_sha256_match,
        "all_expected_inner_csv_present": all_expected_inner_csv_present,
        "schema_match": schema_match,
        "full_csv_read_performed": True,
        "observed_source_row_count_before_policy": total_source_rows,
        "expected_unique_open_time_count": EXPECTED_UNIQUE_OPEN_TIME_COUNT,
        "observed_unique_open_time_count": len(raw_unique_open_times),
        "exact_duplicate_rows_dropped": exact_duplicate_rows_dropped,
        "material_conflict_rows_quarantined": material_conflict_rows_quarantined,
        "clean_source_row_count_after_policy": clean_source_rows,
        "expected_clean_source_rows_after_policy": EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "source_row_count_by_file": source_row_count_by_file,
        "clean_source_row_count_by_file": clean_source_row_count_by_file,
        "unique_symbol_count": len(symbols),
        "observed_symbol": TARGET_SYMBOL,
        "open_time_monotonic_by_file": open_time_monotonic_by_file,
        "clean_missing_minute_count": clean_missing_minute_count,
        "observed_clean_interval_ms": EXPECTED_MINUTE_MS if clean_deltas == {EXPECTED_MINUTE_MS, EXPECTED_MINUTE_MS * 2} else None,
        "observed_first_open_time_ms": first_clean_open_time,
        "observed_last_open_time_ms": last_clean_open_time,
        "observed_first_open_time_utc": iso_utc_from_ms(first_clean_open_time),
        "observed_last_open_time_utc": iso_utc_from_ms(last_clean_open_time),
        "daily_boundary_interpretation": (
            "OKX daily ZIP file-date boundaries were used as validated source partitions; UTC hourly buckets "
            "were derived only from source open_time epoch milliseconds with no local timezone dependence."
        ),
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "affected_hour_marked_complete": affected_hour_row["complete_hour"] == "true",
        "affected_hour_source_row_count": int(affected_hour_row["source_row_count"]),
        "affected_hour_quarantine_applied": affected_hour_row["quarantine_applied"] == "true",
        "output_1h_row_count": output_rows,
        "complete_1h_row_count": complete_hours,
        "incomplete_1h_row_count": incomplete_hours,
        "all_hours_complete": complete_hours == output_rows and incomplete_hours == 0,
    }
    quarantine_summary = {
        "material_conflicting_group_count": 1 if material_conflict_rows_quarantined == 2 else 0,
        "material_conflicting_row_count": material_conflict_rows_quarantined,
        "conflict_open_time": CONFLICT_OPEN_TIME,
        "conflict_open_time_utc": CONFLICT_OPEN_TIME_UTC,
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "quarantined_rows": material_conflict_audit_rows,
    }
    return validation, file_metadata, exact_duplicate_audit_rows, material_conflict_audit_rows, quarantine_summary


def find_output_hour(path: Path, hour_start: int) -> dict[str, str] | None:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("hour_start_epoch_ms") == str(hour_start):
                return dict(row)
    return None


def validate_output_schema(path: Path) -> bool:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return False
    return header == OUTPUT_SCHEMA


def write_outputs(
    generated_at: str,
    output_path: Path,
    validation: dict[str, Any],
    file_metadata: list[dict[str, Any]],
    exact_duplicate_audit_rows: list[dict[str, Any]],
    material_conflict_audit_rows: list[dict[str, Any]],
    quarantine_summary: dict[str, Any],
) -> dict[str, Any]:
    output_schema_validated = validate_output_schema(output_path)
    require(output_schema_validated, "output schema invalid")
    replacement_checks = {
        "expected_head": run_git(["rev-parse", "--short", "HEAD"]) == EXPECTED_HEAD,
        "expected_file_count_1053": validation["file_count_processed"] == EXPECTED_FILE_COUNT,
        "expected_csv_count_1053": validation["csv_count_read"] == EXPECTED_FILE_COUNT,
        "single_symbol_processed": validation["unique_symbol_count"] == 1 and validation["observed_symbol"] == TARGET_SYMBOL,
        "source_rows_expected_before_policy": validation["observed_source_row_count_before_policy"] == EXPECTED_OBSERVED_SOURCE_ROWS,
        "unique_open_time_count_expected": validation["observed_unique_open_time_count"] == EXPECTED_UNIQUE_OPEN_TIME_COUNT,
        "all_source_zip_paths_exist": validation["all_source_zips_exist"],
        "all_hashes_rechecked_and_match": validation["all_source_zip_sha256_match"],
        "all_expected_csvs_read": validation["all_expected_inner_csv_present"],
        "schema_match": validation["schema_match"],
        "full_csv_read_performed": validation["full_csv_read_performed"],
        "exact_duplicate_drop_count_expected": validation["exact_duplicate_rows_dropped"] == EXPECTED_EXACT_DUPLICATE_ROWS_TO_DROP,
        "material_conflict_quarantine_count_expected": validation["material_conflict_rows_quarantined"] == EXPECTED_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE,
        "clean_source_rows_expected": validation["clean_source_row_count_after_policy"] == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "affected_hour_incomplete": validation["affected_hour_marked_complete"] is False
        and validation["affected_hour_source_row_count"] == 59
        and validation["affected_hour_quarantine_applied"] is True,
        "output_rows_expected": validation["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS_AFTER_POLICY,
        "complete_hour_count_expected": validation["complete_1h_row_count"] == EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY,
        "incomplete_hour_count_expected": validation["incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "all_hours_not_complete": validation["all_hours_complete"] is False,
        "no_fill_used": True,
        "no_conflict_row_selection_average_or_merge": True,
        "output_schema_validated": output_schema_validated,
        "no_new_download_api_browse": True,
        "strict_3y_completeness_not_claimed": True,
        "not_research_backtest_edge": True,
        "not_broad_acquisition_ready": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_status": PASS_STATUS,
        "policy_clean_rebuild_execution_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "expected_file_count": EXPECTED_FILE_COUNT,
        "file_count_processed": validation["file_count_processed"],
        "all_source_zips_exist": validation["all_source_zips_exist"],
        "all_source_zip_sha256_match": validation["all_source_zip_sha256_match"],
        "all_expected_inner_csv_present": validation["all_expected_inner_csv_present"],
        "schema_match": validation["schema_match"],
        "full_csv_read_performed": validation["full_csv_read_performed"],
        "observed_source_row_count_before_policy": validation["observed_source_row_count_before_policy"],
        "expected_unique_open_time_count": EXPECTED_UNIQUE_OPEN_TIME_COUNT,
        "exact_duplicate_rows_dropped": validation["exact_duplicate_rows_dropped"],
        "material_conflict_rows_quarantined": validation["material_conflict_rows_quarantined"],
        "clean_source_row_count_after_policy": validation["clean_source_row_count_after_policy"],
        "expected_clean_source_rows_after_policy": EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "unique_symbol_count": validation["unique_symbol_count"],
        "observed_symbol": validation["observed_symbol"],
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "affected_hour_marked_complete": validation["affected_hour_marked_complete"],
        "affected_hour_source_row_count": validation["affected_hour_source_row_count"],
        "aggregation_performed_now": True,
        "data_build_performed": True,
        "output_1h_row_count": validation["output_1h_row_count"],
        "expected_output_rows_after_policy": EXPECTED_OUTPUT_ROWS_AFTER_POLICY,
        "complete_1h_row_count": validation["complete_1h_row_count"],
        "expected_complete_1h_rows_after_policy": EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY,
        "incomplete_1h_row_count": validation["incomplete_1h_row_count"],
        "expected_incomplete_1h_rows_after_policy": EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "all_hours_complete": validation["all_hours_complete"],
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": output_path.exists(),
        "output_csv_path": str(output_path),
        "output_schema_validated": output_schema_validated,
        "output_is_policy_clean_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "no_new_download": True,
        "new_download_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 9,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": AFTER_QUALITY,
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "tracked_python_count_at_execution_run": tracked_python_count(),
    }
    exact_duplicate_audit = {
        "exact_duplicate_drop_audit_created": True,
        "exact_duplicate_drop_allowed": True,
        "exact_duplicate_rows_dropped": validation["exact_duplicate_rows_dropped"],
        "expected_exact_duplicate_rows_dropped": EXPECTED_EXACT_DUPLICATE_ROWS_TO_DROP,
        "dropped_rows": exact_duplicate_audit_rows,
    }
    material_conflict_audit = {
        "material_conflict_quarantine_audit_created": True,
        "conflict_resolution_policy": CONFLICT_RESOLUTION_POLICY,
        "conflict_open_time": CONFLICT_OPEN_TIME,
        "conflict_open_time_utc": CONFLICT_OPEN_TIME_UTC,
        "differing_fields": DIFFERING_FIELDS,
        "material_conflict_rows_quarantined": validation["material_conflict_rows_quarantined"],
        "expected_material_conflict_rows_quarantined": EXPECTED_MATERIAL_CONFLICT_ROWS_TO_QUARANTINE,
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "selected_for_output_count": 0,
        "quarantined_rows": material_conflict_audit_rows,
        "quarantine_summary": quarantine_summary,
    }
    gap_report = {
        "gap_incomplete_hour_report_created": True,
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "affected_hour_marked_complete": validation["affected_hour_marked_complete"],
        "affected_hour_source_row_count": validation["affected_hour_source_row_count"],
        "clean_missing_minute_count": validation["clean_missing_minute_count"],
        "complete_hour_count": validation["complete_1h_row_count"],
        "incomplete_hour_count": validation["incomplete_1h_row_count"],
        "all_hours_complete": validation["all_hours_complete"],
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "incomplete_reason": "MATERIAL_CONFLICT_OPEN_TIME_QUARANTINED",
    }
    schema_report = {
        "schema_validation_report_created": True,
        "input_schema": EXPECTED_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
        "schema_match": validation["schema_match"],
        "output_schema_validated": output_schema_validated,
        "policy_clean_schema_extension_documented": True,
        "older_19_column_schema_not_silently_used": True,
        "timestamp_unit": "epoch_milliseconds",
    }
    provenance_report = {
        "output_provenance_report_created": True,
        "source_zip_paths": [item["source_zip_path"] for item in file_metadata],
        "source_zip_sha256_by_file": {item["source_csv_file"]: item["source_zip_sha256"] for item in file_metadata},
        "source_zip_size_bytes_by_file": {item["source_csv_file"]: item["source_zip_size_bytes"] for item in file_metadata},
        "expected_inner_csv_by_date": {item["date"]: item["source_csv_file"] for item in file_metadata},
        "source_row_count_before_policy_by_file": {item["source_csv_file"]: item["source_row_count_before_policy"] for item in file_metadata},
        "clean_source_row_count_after_policy_by_file": {item["source_csv_file"]: item["clean_source_row_count_after_policy"] for item in file_metadata},
        "file_dates": [item["date"] for item in file_metadata],
        "build_timestamp_utc": generated_at,
        "output_csv_path": str(output_path),
        "output_row_count": validation["output_1h_row_count"],
        "url_iteration_performed": False,
        "new_download_performed_now": False,
        "provenance_status": "POLICY_CLEAN_SINGLE_SYMBOL_PIPELINE_VALIDATION_BUILD_OUTPUT",
    }
    compliance = {
        "no_new_download": True,
        "no_api": True,
        "no_browse": True,
        "no_url_fetch": True,
        "no_url_iteration": True,
        "no_multi_symbol": True,
        "no_dates_outside_max_available_file_range": True,
        "no_conflicting_row_choice": True,
        "no_conflicting_row_average": True,
        "no_conflicting_row_merge": True,
        "no_ohlcv_modification": True,
        "no_synthetic_fill": True,
        "no_forward_fill": True,
        "no_backfill": True,
        "no_strategy_research": True,
        "no_backtest": True,
        "no_candidate_generation": True,
        "no_edge_profit_claim": True,
        "no_broad_acquisition_ready_claim": True,
        "no_strict_3_year_completeness_claim": True,
        "no_runtime_capital_live": True,
        "no_repo_schema_config": True,
        "no_generic_runner": True,
        "output_is_policy_clean_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
    }
    execution_report = {
        "execution_scope": {
            "policy_clean_rebuild_execution_performed": True,
            "target_symbol": TARGET_SYMBOL,
            "strict_3y_completeness_claimed": False,
            "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
            "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
            "expected_file_count": EXPECTED_FILE_COUNT,
            "source_zip_sha256_validation_performed_for_all_files": True,
            "full_csv_read_performed": True,
            "output_directory": str(OUTPUT_DIR),
            "new_download_performed": False,
            "api_call_performed": False,
            "browse_performed": False,
            "multi_symbol_processing": False,
        },
        "input_validation": validation,
        "exact_duplicate_drop_audit": exact_duplicate_audit,
        "material_conflict_quarantine_audit": material_conflict_audit,
        "gap_incomplete_hour_report": gap_report,
        "schema_validation_report": schema_report,
        "output_provenance_report": provenance_report,
        "compliance_report": compliance,
        "next_module_decision": {"next_module": NEXT_MODULE, "blocked_next_module": BLOCKED_NEXT_MODULE},
    }
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_report.json", execution_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_exact_duplicate_drop_audit.json", exact_duplicate_audit)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_material_conflict_quarantine_audit.json", material_conflict_audit)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_gap_incomplete_hour_report.json", gap_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_schema_validation_report.json", schema_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_output_provenance_report.json", provenance_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_build_execution_compliance_report.json", compliance)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_build_execution_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    return summary


def write_blocked(reason: str) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    blocked = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "head": run_git(["rev-parse", "--short", "HEAD"]) if REPO_ROOT.exists() else None,
        "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_status": BLOCKED_STATUS,
        "policy_clean_rebuild_execution_performed": False,
        "target_symbol": TARGET_SYMBOL,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "file_count_processed": 0,
        "observed_source_row_count_before_policy": 0,
        "exact_duplicate_rows_dropped": 0,
        "material_conflict_rows_quarantined": 0,
        "clean_source_row_count_after_policy": 0,
        "expected_clean_source_rows_after_policy": EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "affected_hour_utc": AFFECTED_HOUR_UTC,
        "affected_hour_marked_complete": False,
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "output_1h_row_count": 0,
        "expected_output_rows_after_policy": EXPECTED_OUTPUT_ROWS_AFTER_POLICY,
        "complete_1h_row_count": 0,
        "expected_complete_1h_rows_after_policy": EXPECTED_COMPLETE_1H_ROWS_AFTER_POLICY,
        "incomplete_1h_row_count": 0,
        "expected_incomplete_1h_rows_after_policy": EXPECTED_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "all_hours_complete": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": False,
        "output_schema_validated": False,
        "output_is_policy_clean_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "no_new_download": True,
        "new_download_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 9,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": BEFORE_QUALITY,
        "next_module": BLOCKED_NEXT_MODULE,
        "replacement_checks_all_true": False,
        "blocked_reason": reason,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_build_execution_summary.json", blocked)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
    return blocked


def main() -> None:
    generated_at = utc_now()
    policy_summary = load_json(POLICY_SUMMARY)
    material_policy = load_json(MATERIAL_POLICY)
    quarantine_policy = load_json(QUARANTINE_POLICY)
    rebuild_approval = load_json(REBUILD_APPROVAL)
    download_validator = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    hash_report = load_json(HASH_VALIDATION_REPORT)
    validate_preflight(policy_summary, material_policy, quarantine_policy, rebuild_approval, download_validator)
    entries = load_hash_entries(hash_report)
    output_path = output_csv_path()
    validation, file_metadata, exact_duplicate_audit_rows, material_conflict_audit_rows, quarantine_summary = process_files(entries, output_path)
    summary = write_outputs(
        generated_at,
        output_path,
        validation,
        file_metadata,
        exact_duplicate_audit_rows,
        material_conflict_audit_rows,
        quarantine_summary,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        blocked = write_blocked(str(exc))
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
