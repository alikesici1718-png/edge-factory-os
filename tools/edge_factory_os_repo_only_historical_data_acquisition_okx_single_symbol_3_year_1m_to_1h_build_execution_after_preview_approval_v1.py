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
    "3_year_1m_to_1h_build_execution_after_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "cc3ae3c"
TARGET_SYMBOL = "BTC-USDT-SWAP"
MAX_AVAILABLE_START = date(2023, 7, 1)
MAX_AVAILABLE_END = date(2026, 5, 18)
EXPECTED_FILE_COUNT = 1053
EXPECTED_SOURCE_ROWS_PER_FILE = 1440
EXPECTED_TOTAL_SOURCE_ROWS = 1_516_320
MAX_TOTAL_SOURCE_ROWS = 1_600_000
EXPECTED_OUTPUT_ROWS = 25_272
EXPECTED_OUTPUT_HOURS_PER_FILE = 24
EXPECTED_MINUTE_MS = 60_000
EXPECTED_HOUR_MS = 3_600_000
BUILD_SCOPE = "SINGLE_SYMBOL_3_YEAR_MAX_AVAILABLE_1M_TO_1H_PIPELINE_VALIDATION_ONLY"

PREVIEW_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_"
    "BUILD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)
DOWNLOAD_VALIDATOR_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_VALIDATED_"
    "BUILD_PREVIEW_READY_MAX_AVAILABLE_NO_BUILD"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_"
    "BUILD_EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_BUILD_EXECUTION"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_BUILD_PREVIEW_"
    "APPROVED_EXECUTION_NEXT_NO_BUILD_YET"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_1M_TO_1H_BUILD_EXECUTED_"
    "PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_execution_validator_after_execution_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_execution_blocked_record_after_preview_approval_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
PREVIEW_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_1m_to_1h_build_preview_after_download_validator_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1"
)

PREVIEW_SUMMARY = PREVIEW_DIR / f"{PREVIEW_DIR.name}_latest.json"
PREVIEW_APPROVAL = PREVIEW_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_approval_record.json"
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
]
DANGEROUS_FLAGS = {
    "new_download_performed_now": False,
    "data_download_performed": False,
    "data_fetch_performed": False,
    "okx_download_performed": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "external_download_allowed_now": False,
    "external_api_allowed_now": False,
    "strategy_research_implementation_touched": False,
    "candidate_generation_touched": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
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


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


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
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise Blocked(f"numeric parse failed {field_name} {source_csv} row={row_number}") from exc
    require(parsed.is_finite(), f"non-finite numeric {field_name} {source_csv} row={row_number}")
    return parsed


def decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal(1)))
    return format(normalized, "f")


def parse_confirm(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def validate_preflight(preview: dict[str, Any], approval: dict[str, Any], validator: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(
        preview.get("historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_preview_status")
        == PREVIEW_STATUS,
        "preview status mismatch",
    )
    require(preview.get("next_module") == REQUESTED_MODULE, "preview next_module mismatch")
    require(preview.get("approval_grants_future_3_year_build_next") is True, "future build approval missing")
    require(preview.get("approval_grants_build_now") is False, "preview build-now grant unexpectedly true")
    require(preview.get("target_symbol") == TARGET_SYMBOL, "preview target mismatch")
    require(preview.get("strict_3y_completeness_claimed") is False, "preview strict 3y claim detected")
    require(preview.get("max_available_start_candidate") == MAX_AVAILABLE_START.isoformat(), "preview start mismatch")
    require(preview.get("max_available_end_date") == MAX_AVAILABLE_END.isoformat(), "preview end mismatch")
    require(preview.get("expected_file_count") == EXPECTED_FILE_COUNT, "preview file count mismatch")
    require(preview.get("expected_total_source_rows") == EXPECTED_TOTAL_SOURCE_ROWS, "preview source row mismatch")
    require(preview.get("expected_output_rows") == EXPECTED_OUTPUT_ROWS, "preview output row mismatch")
    require(preview.get("safe_for_broad_acquisition") is False, "preview broad acquisition flag mismatch")
    require(preview.get("safe_for_research_backtest") is False, "preview research/backtest flag mismatch")
    require(preview.get("safe_for_edge_claim") is False, "preview edge flag mismatch")
    require(approval.get("approval_grants_future_3_year_build_next") is True, "approval future build grant missing")
    require(approval.get("approval_grants_build_now") is False, "approval build-now grant unexpectedly true")
    require(approval.get("approval_grants_download_now") is False, "approval download grant unexpectedly true")
    require(approval.get("approval_grants_api_now") is False, "approval API grant unexpectedly true")
    require(approval.get("approval_grants_browse_now") is False, "approval browse grant unexpectedly true")
    require(approval.get("approval_grants_multi_symbol_now") is False, "approval multi-symbol grant unexpectedly true")
    require(approval.get("approval_grants_broad_acquisition_now") is False, "approval broad grant unexpectedly true")
    require(approval.get("approval_grants_research_backtest_edge_now") is False, "approval research/edge grant unexpectedly true")
    require(approval.get("next_module") == REQUESTED_MODULE, "approval next_module mismatch")
    require(
        validator.get("historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_status")
        == DOWNLOAD_VALIDATOR_STATUS,
        "download validator status mismatch",
    )
    require(validator.get("next_module") == "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_preview_after_download_validator_v1.py", "download validator chain mismatch")
    require(validator.get("download_execution_validated") is True, "download validator did not validate execution")
    require(validator.get("target_symbol") == TARGET_SYMBOL, "download validator target mismatch")
    require(validator.get("strict_3y_completeness_claimed") is False, "download validator strict 3y claim detected")
    require(validator.get("max_available_start_candidate") == MAX_AVAILABLE_START.isoformat(), "download validator start mismatch")
    require(validator.get("max_available_end_date") == MAX_AVAILABLE_END.isoformat(), "download validator end mismatch")
    require(validator.get("final_file_set_count") == EXPECTED_FILE_COUNT, "download validator file count mismatch")
    require(validator.get("all_downloaded_zip_paths_exist") is True, "download validator ZIP path flag mismatch")
    require(validator.get("all_hashes_match_recorded") is True, "download validator hash flag mismatch")
    require(validator.get("all_expected_inner_csv_present") is True, "download validator inner CSV flag mismatch")
    require(validator.get("all_expected_schema_match") is True, "download validator schema flag mismatch")
    require(validator.get("all_observed_symbols_match_target") is True, "download validator symbol flag mismatch")
    require(validator.get("safe_for_3_year_build_preview") is True, "download validator build-preview safety missing")
    require(validator.get("safe_for_broad_acquisition") is False, "download validator broad flag mismatch")
    require(validator.get("safe_for_research_backtest") is False, "download validator research flag mismatch")
    require(validator.get("safe_for_edge_claim") is False, "download validator edge flag mismatch")
    require(validator.get("full_csv_read_performed") is False, "download validator full CSV read flag mismatch")
    require(validator.get("data_build_performed") is False, "download validator build flag mismatch")
    require(validator.get("aggregation_performed_now") is False, "download validator aggregation flag mismatch")
    require(validator.get("okx_api_call_performed") is False, "download validator API flag mismatch")
    require(validator.get("okx_browse_performed") is False, "download validator browse flag mismatch")


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
    require(complete, f"incomplete UTC hour: {agg.hour_start}")
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
        "complete_hour": "true",
        "confirm": "true" if agg.confirm_all else "false",
        "source_first_open_time": str(agg.first_open_time),
        "source_last_open_time": str(agg.last_open_time),
        "source_zip_sha256": "|".join(sorted(agg.source_hashes)),
        "source_csv_file": "|".join(sorted(agg.source_csvs)),
        "source_date": "|".join(sorted(agg.source_dates)),
        "build_scope": BUILD_SCOPE,
    }


def output_csv_path() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = (OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_output.csv").resolve()
    path.relative_to(OUTPUT_DIR.resolve())
    try:
        path.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return path
    raise Blocked("output path inside tracked repo")


def scan_source_files(entries: list[dict[str, Any]]) -> dict[str, Any]:
    source_row_count_by_file: dict[str, int] = {}
    symbols: set[str] = set()
    all_open_times: list[int] = []
    file_count_processed = 0
    all_source_zips_exist = True
    all_source_zip_sha256_match = True
    all_expected_inner_csv_present = True
    schema_match = True
    open_time_monotonic_by_file = True
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
        previous_file_open_time: int | None = None
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) <= 10, f"too many ZIP members: {path}")
            require(all(safe_zip_member(name) for name in names), f"ZIP traversal risk: {path}")
            expected_present = expected_csv in names
            all_expected_inner_csv_present = all_expected_inner_csv_present and expected_present
            require(expected_present, f"expected CSV missing: {expected_csv}")
            with archive.open(expected_csv, "r") as raw:
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
                        open_time = int(str(raw_row["open_time"]))
                    except ValueError as exc:
                        raise Blocked(f"open_time parse failed {expected_csv} row={row_number}") from exc
                    if previous_file_open_time is not None and open_time <= previous_file_open_time:
                        open_time_monotonic_by_file = False
                    previous_file_open_time = open_time
                    all_open_times.append(open_time)
                    file_row_count += 1
        source_row_count_by_file[expected_csv] = file_row_count
        file_count_processed += 1

    sorted_times = sorted(all_open_times)
    unique_times = sorted(set(all_open_times))
    duplicate_open_time_count = len(all_open_times) - len(unique_times)
    raw_deltas = [right - left for left, right in zip(sorted_times, sorted_times[1:])]
    unique_deltas = [right - left for left, right in zip(unique_times, unique_times[1:])]
    missing_minute_count = sum(max(0, (delta // EXPECTED_MINUTE_MS) - 1) for delta in unique_deltas if delta != EXPECTED_MINUTE_MS)
    source_row_count_total = len(all_open_times)
    source_row_count_by_file_valid = (
        len(source_row_count_by_file) == EXPECTED_FILE_COUNT
        and all(count == EXPECTED_SOURCE_ROWS_PER_FILE for count in source_row_count_by_file.values())
    )
    observed_interval_ms = EXPECTED_MINUTE_MS if raw_deltas and all(delta == EXPECTED_MINUTE_MS for delta in raw_deltas) else None
    one_minute_interval_validated = (
        duplicate_open_time_count == 0
        and bool(unique_deltas)
        and all(delta == EXPECTED_MINUTE_MS for delta in unique_deltas)
    )
    return {
        "file_count_processed": file_count_processed,
        "all_source_zips_exist": all_source_zips_exist,
        "all_source_zip_sha256_match": all_source_zip_sha256_match,
        "all_expected_inner_csv_present": all_expected_inner_csv_present,
        "schema_match": schema_match,
        "full_csv_read_performed": True,
        "source_row_count_total": source_row_count_total,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "source_row_count_by_file": source_row_count_by_file,
        "source_row_count_by_file_valid": source_row_count_by_file_valid,
        "unique_symbol_count": len(symbols),
        "observed_symbol": TARGET_SYMBOL if symbols == {TARGET_SYMBOL} else "|".join(sorted(symbols)),
        "open_time_monotonic_by_file": open_time_monotonic_by_file,
        "duplicate_open_time_count_total": duplicate_open_time_count,
        "missing_minute_count_total": missing_minute_count,
        "observed_interval_ms": observed_interval_ms,
        "one_minute_interval_validated": one_minute_interval_validated,
        "observed_first_open_time_utc": iso_utc_from_ms(unique_times[0]) if unique_times else None,
        "observed_last_open_time_utc": iso_utc_from_ms(unique_times[-1]) if unique_times else None,
        "daily_boundary_interpretation": (
            "OKX daily ZIP file-date boundaries were used as validated source partitions; UTC hourly buckets "
            "would be derived only from source open_time epoch milliseconds with no local timezone dependence."
        ),
    }


def write_blocked_outputs(generated_at: str, scan: dict[str, Any], reason: str) -> dict[str, Any]:
    output_path = output_csv_path()
    if output_path.exists():
        output_path.unlink()
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_execution_status": BLOCKED_STATUS,
        "build_execution_performed": False,
        "target_symbol": TARGET_SYMBOL,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "expected_file_count": EXPECTED_FILE_COUNT,
        "file_count_processed": scan.get("file_count_processed", 0),
        "all_source_zips_exist": scan.get("all_source_zips_exist", False),
        "all_source_zip_sha256_match": scan.get("all_source_zip_sha256_match", False),
        "all_expected_inner_csv_present": scan.get("all_expected_inner_csv_present", False),
        "schema_match": scan.get("schema_match", False),
        "full_csv_read_performed": scan.get("full_csv_read_performed", False),
        "source_row_count_total": scan.get("source_row_count_total", 0),
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "source_row_count_by_file_valid": scan.get("source_row_count_by_file_valid", False),
        "unique_symbol_count": scan.get("unique_symbol_count", 0),
        "observed_symbol": scan.get("observed_symbol"),
        "open_time_monotonic_by_file": scan.get("open_time_monotonic_by_file", False),
        "duplicate_open_time_count_total": scan.get("duplicate_open_time_count_total", 0),
        "missing_minute_count_total": scan.get("missing_minute_count_total", 0),
        "observed_interval_ms": scan.get("observed_interval_ms"),
        "one_minute_interval_validated": scan.get("one_minute_interval_validated", False),
        "observed_first_open_time_utc": scan.get("observed_first_open_time_utc"),
        "observed_last_open_time_utc": scan.get("observed_last_open_time_utc"),
        "daily_boundary_interpretation": scan.get("daily_boundary_interpretation"),
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "output_1h_row_count": 0,
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "complete_1h_row_count": 0,
        "incomplete_1h_row_count": 0,
        "all_hours_complete": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": False,
        "output_schema_validated": False,
        "output_is_pipeline_3_year_max_available_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "no_new_download": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": BEFORE_QUALITY,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 0,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": BLOCKED_NEXT_MODULE,
        "derived_live_repo_post_check": BLOCKED_STATUS,
        "replacement_checks_all_true": False,
        "blocked_reason": reason,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "tracked_python_count_at_execution_run": tracked_python_count(),
    }
    gap_report = {
        "duplicate_open_time_count_total": summary["duplicate_open_time_count_total"],
        "missing_minute_count_total": summary["missing_minute_count_total"],
        "incomplete_hour_count": None,
        "complete_hour_count": 0,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "gap_duplicate_status": "BLOCKED_DUPLICATE_OR_SOURCE_ROW_COUNT_MISMATCH",
        "blocked_reason": reason,
    }
    schema_report = {
        "input_schema": EXPECTED_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
        "schema_match": summary["schema_match"],
        "output_schema_validated": False,
        "numeric_validation_passed": True,
        "timestamp_unit": "epoch_milliseconds",
    }
    provenance_report = {
        "build_timestamp_utc": generated_at,
        "output_csv_path": str(output_path),
        "output_row_count": 0,
        "validator_inputs_prepared": True,
        "url_iteration_performed": False,
        "provenance_status": "BLOCKED_NO_COMPLETED_OUTPUT_WRITTEN",
        "blocked_reason": reason,
    }
    compliance = {
        "no_new_download": True,
        "no_api": True,
        "no_browse": True,
        "no_url_fetch": True,
        "no_url_iteration": True,
        "no_multi_symbol": True,
        "no_strategy_research": True,
        "no_backtest": True,
        "no_candidate_generation": True,
        "no_edge_profit_claim": True,
        "no_broad_acquisition_ready_claim": True,
        "no_strict_3_year_completeness_claim": True,
        "no_runtime_capital_live": True,
        "no_repo_schema_config": True,
        "no_generic_runner": True,
        "output_is_pipeline_3_year_max_available_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
    }
    execution_report = {
        "execution_scope": {
            "build_execution_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "strict_3y_completeness_claimed": False,
            "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
            "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
            "expected_file_count": EXPECTED_FILE_COUNT,
            "source_zip_sha256_validation_performed_for_all_files": summary["file_count_processed"] == EXPECTED_FILE_COUNT,
            "full_csv_read_performed": summary["full_csv_read_performed"],
            "output_directory": str(OUTPUT_DIR),
            "new_download_performed": False,
            "api_call_performed": False,
            "browse_performed": False,
            "multi_symbol_processing": False,
            "blocked_reason": reason,
        },
        "input_validation": scan,
        "gap_duplicate_report": gap_report,
        "schema_validation_report": schema_report,
        "output_provenance_report": provenance_report,
        "compliance_report": compliance,
        "next_module_decision": {"next_module": None, "blocked_next_module": BLOCKED_NEXT_MODULE},
    }
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_report.json", execution_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_gap_duplicate_report.json", gap_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_schema_validation_report.json", schema_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_output_provenance_report.json", provenance_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_compliance_report.json", compliance)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    return summary


def process_files(entries: list[dict[str, Any]], output_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source_row_count_by_file: dict[str, int] = {}
    file_metadata: list[dict[str, Any]] = []
    symbols: set[str] = set()
    total_source_rows = 0
    output_rows = 0
    complete_hours = 0
    incomplete_hours = 0
    duplicate_open_time_count = 0
    missing_minute_count = 0
    observed_deltas: set[int] = set()
    previous_global_open_time: int | None = None
    first_open_time: int | None = None
    last_open_time: int | None = None
    open_time_monotonic_by_file = True
    all_source_zips_exist = True
    all_source_zip_sha256_match = True
    all_expected_inner_csv_present = True
    schema_match = True
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
            previous_file_open_time: int | None = None
            seen_file_open_times: set[int] = set()
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                require(len(names) <= 10, f"too many ZIP members: {path}")
                require(all(safe_zip_member(name) for name in names), f"ZIP traversal risk: {path}")
                expected_present = expected_csv in names
                all_expected_inner_csv_present = all_expected_inner_csv_present and expected_present
                require(expected_present, f"expected CSV missing: {expected_csv}")
                with archive.open(expected_csv, "r") as raw:
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
                            open_time = int(str(raw_row["open_time"]))
                        except ValueError as exc:
                            raise Blocked(f"open_time parse failed {expected_csv} row={row_number}") from exc
                        if previous_file_open_time is not None:
                            if open_time <= previous_file_open_time:
                                open_time_monotonic_by_file = False
                            require(open_time > previous_file_open_time, f"non-monotonic open_time {expected_csv}")
                            require(open_time - previous_file_open_time == EXPECTED_MINUTE_MS, f"missing minute within file {expected_csv}")
                        previous_file_open_time = open_time
                        require(open_time not in seen_file_open_times, f"duplicate open_time within file {expected_csv}")
                        seen_file_open_times.add(open_time)
                        if previous_global_open_time is not None:
                            delta = open_time - previous_global_open_time
                            observed_deltas.add(delta)
                            if delta == 0:
                                duplicate_open_time_count += 1
                            require(delta > 0, f"non-monotonic global open_time at {expected_csv} row={row_number}")
                            if delta != EXPECTED_MINUTE_MS:
                                missing_minute_count += max(0, (delta // EXPECTED_MINUTE_MS) - 1)
                            require(delta == EXPECTED_MINUTE_MS, f"missing minute across files at {expected_csv} row={row_number}")
                        previous_global_open_time = open_time
                        first_open_time = open_time if first_open_time is None else first_open_time
                        last_open_time = open_time
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
                            require(output_rows <= EXPECTED_OUTPUT_ROWS, "output row count exceeded expected")
                            current_hour = new_hour(minute_row)
                        file_row_count += 1
                        total_source_rows += 1
                        require(total_source_rows <= MAX_TOTAL_SOURCE_ROWS, "total source row count exceeds guardrail")
            require(file_row_count == EXPECTED_SOURCE_ROWS_PER_FILE, f"source rows for {expected_csv}={file_row_count}")
            source_row_count_by_file[expected_csv] = file_row_count
            file_metadata.append(
                {
                    "date": day,
                    "source_zip_path": str(path),
                    "source_zip_sha256": digest,
                    "source_zip_size_bytes": path.stat().st_size,
                    "source_csv_file": expected_csv,
                    "source_row_count": file_row_count,
                    "source_kind": entry.get("source_kind"),
                }
            )
        if current_hour is not None:
            out_row = aggregate_to_row(current_hour)
            writer.writerow(out_row)
            output_rows += 1
            complete_hours += 1 if out_row["complete_hour"] == "true" else 0
            incomplete_hours += 1 if out_row["complete_hour"] != "true" else 0

    require(total_source_rows == EXPECTED_TOTAL_SOURCE_ROWS, f"total source rows={total_source_rows}")
    require(output_rows == EXPECTED_OUTPUT_ROWS, f"output rows={output_rows}")
    require(complete_hours == EXPECTED_OUTPUT_ROWS and incomplete_hours == 0, "incomplete hours detected")
    require(duplicate_open_time_count == 0, "duplicate open_time exists")
    require(missing_minute_count == 0, "missing minutes detected")
    require(symbols == {TARGET_SYMBOL}, f"unexpected symbols: {sorted(symbols)}")
    require(first_open_time is not None and last_open_time is not None, "no source rows observed")
    source_row_count_by_file_valid = (
        len(source_row_count_by_file) == EXPECTED_FILE_COUNT
        and all(count == EXPECTED_SOURCE_ROWS_PER_FILE for count in source_row_count_by_file.values())
    )
    input_validation = {
        "source_row_count_total": total_source_rows,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "source_row_count_by_file": source_row_count_by_file,
        "source_row_count_by_file_valid": source_row_count_by_file_valid,
        "unique_symbol_count": len(symbols),
        "observed_symbol": TARGET_SYMBOL,
        "open_time_monotonic_by_file": open_time_monotonic_by_file,
        "duplicate_open_time_count_total": duplicate_open_time_count,
        "missing_minute_count_total": missing_minute_count,
        "observed_interval_ms": EXPECTED_MINUTE_MS if observed_deltas == {EXPECTED_MINUTE_MS} else None,
        "one_minute_interval_validated": observed_deltas == {EXPECTED_MINUTE_MS},
        "observed_first_open_time_ms": first_open_time,
        "observed_last_open_time_ms": last_open_time,
        "observed_first_open_time_utc": iso_utc_from_ms(first_open_time),
        "observed_last_open_time_utc": iso_utc_from_ms(last_open_time),
        "daily_boundary_interpretation": (
            "OKX daily ZIP file-date boundaries were used as validated source partitions; UTC hourly buckets "
            "were derived only from source open_time epoch milliseconds with no local timezone dependence."
        ),
        "all_source_zips_exist": all_source_zips_exist,
        "all_source_zip_sha256_match": all_source_zip_sha256_match,
        "all_expected_inner_csv_present": all_expected_inner_csv_present,
        "schema_match": schema_match,
        "full_csv_read_performed": True,
        "file_count_processed": len(file_metadata),
        "output_1h_row_count": output_rows,
        "complete_1h_row_count": complete_hours,
        "incomplete_1h_row_count": incomplete_hours,
    }
    return input_validation, file_metadata


def validate_output_schema(path: Path) -> bool:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return False
    return header == OUTPUT_SCHEMA


def build_summary(
    generated_at: str,
    output_path: Path,
    input_validation: dict[str, Any],
    file_metadata: list[dict[str, Any]],
    replacement_checks: dict[str, bool],
) -> dict[str, Any]:
    replacement_checks_all_true = all(replacement_checks.values())
    output_schema_validated = validate_output_schema(output_path)
    require(output_schema_validated, "output schema invalid")
    require(replacement_checks_all_true, "replacement checks failed")
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_execution_status": PASS_STATUS,
        "final_decision": "3_YEAR_MAX_AVAILABLE_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY",
        "build_execution_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "expected_file_count": EXPECTED_FILE_COUNT,
        "file_count_processed": input_validation["file_count_processed"],
        "all_source_zips_exist": input_validation["all_source_zips_exist"],
        "all_source_zip_sha256_match": input_validation["all_source_zip_sha256_match"],
        "all_expected_inner_csv_present": input_validation["all_expected_inner_csv_present"],
        "schema_match": input_validation["schema_match"],
        "full_csv_read_performed": input_validation["full_csv_read_performed"],
        "source_row_count_total": input_validation["source_row_count_total"],
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "source_row_count_by_file_valid": input_validation["source_row_count_by_file_valid"],
        "unique_symbol_count": input_validation["unique_symbol_count"],
        "observed_symbol": input_validation["observed_symbol"],
        "open_time_monotonic_by_file": input_validation["open_time_monotonic_by_file"],
        "duplicate_open_time_count_total": input_validation["duplicate_open_time_count_total"],
        "missing_minute_count_total": input_validation["missing_minute_count_total"],
        "observed_interval_ms": input_validation["observed_interval_ms"],
        "one_minute_interval_validated": input_validation["one_minute_interval_validated"],
        "observed_first_open_time_utc": input_validation["observed_first_open_time_utc"],
        "observed_last_open_time_utc": input_validation["observed_last_open_time_utc"],
        "daily_boundary_interpretation": input_validation["daily_boundary_interpretation"],
        "aggregation_performed_now": True,
        "data_build_performed": True,
        "output_1h_row_count": input_validation["output_1h_row_count"],
        "expected_output_rows": EXPECTED_OUTPUT_ROWS,
        "complete_1h_row_count": input_validation["complete_1h_row_count"],
        "incomplete_1h_row_count": input_validation["incomplete_1h_row_count"],
        "all_hours_complete": input_validation["complete_1h_row_count"] == EXPECTED_OUTPUT_ROWS
        and input_validation["incomplete_1h_row_count"] == 0,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": output_path.exists(),
        "output_csv_path": str(output_path),
        "output_schema_validated": output_schema_validated,
        "output_is_pipeline_3_year_max_available_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "no_new_download": True,
        "data_download_performed": False,
        "data_fetch_performed": False,
        "new_download_performed_now": False,
        "external_download_allowed_now": False,
        "external_api_allowed_now": False,
        "okx_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": NEXT_MODULE,
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": (
            "built exactly one BTC-USDT-SWAP max-available 1h pipeline-validation output from 1053 "
            "already validated local OKX daily ZIPs; rechecked every SHA256 before reading exactly the "
            "expected inner CSV, read full CSV contents, validated 1516320 monotonic unique 1m rows, "
            "produced 25272 complete UTC 1h rows, used no fill, and made no strict 3-year completeness, "
            "broad acquisition, research, backtest, edge, runtime, capital, live, schema/config, API, "
            "browse, or new-download claim"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "source_file_count": len(file_metadata),
        "tracked_python_count_at_execution_run": tracked_python_count(),
    }


def main() -> None:
    generated_at = utc_now()
    preview = load_json(PREVIEW_SUMMARY)
    approval = load_json(PREVIEW_APPROVAL)
    validator = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    hash_report = load_json(HASH_VALIDATION_REPORT)
    validate_preflight(preview, approval, validator)
    entries = load_hash_entries(hash_report)
    scan = scan_source_files(entries)
    scan_blockers = []
    if scan["file_count_processed"] != EXPECTED_FILE_COUNT:
        scan_blockers.append(f"file_count_processed={scan['file_count_processed']}")
    if scan["source_row_count_total"] != EXPECTED_TOTAL_SOURCE_ROWS:
        scan_blockers.append(f"source_row_count_total={scan['source_row_count_total']}")
    if scan["duplicate_open_time_count_total"] != 0:
        scan_blockers.append(f"duplicate_open_time_count_total={scan['duplicate_open_time_count_total']}")
    if scan["missing_minute_count_total"] != 0:
        scan_blockers.append(f"missing_minute_count_total={scan['missing_minute_count_total']}")
    if scan["source_row_count_by_file_valid"] is not True:
        scan_blockers.append("source_row_count_by_file_valid=false")
    if scan["one_minute_interval_validated"] is not True:
        scan_blockers.append("one_minute_interval_validated=false")
    if scan_blockers:
        summary = write_blocked_outputs(generated_at, scan, "; ".join(scan_blockers))
        print(json.dumps(summary, indent=2, sort_keys=True))
        raise SystemExit(1)
    output_path = output_csv_path()
    input_validation, file_metadata = process_files(entries, output_path)
    output_schema_validated = validate_output_schema(output_path)
    replacement_checks = {
        "preflight_passed": True,
        "expected_file_count_1053": input_validation["file_count_processed"] == EXPECTED_FILE_COUNT,
        "single_symbol_processed": input_validation["unique_symbol_count"] == 1
        and input_validation["observed_symbol"] == TARGET_SYMBOL,
        "source_rows_expected": input_validation["source_row_count_total"] == EXPECTED_TOTAL_SOURCE_ROWS,
        "source_row_count_by_file_valid": input_validation["source_row_count_by_file_valid"],
        "all_source_zip_paths_exist": input_validation["all_source_zips_exist"],
        "all_hashes_rechecked_and_match": input_validation["all_source_zip_sha256_match"],
        "all_expected_csvs_read": input_validation["all_expected_inner_csv_present"],
        "schema_match": input_validation["schema_match"],
        "one_minute_interval_validated": input_validation["one_minute_interval_validated"],
        "no_duplicate_open_time": input_validation["duplicate_open_time_count_total"] == 0,
        "no_missing_minutes": input_validation["missing_minute_count_total"] == 0,
        "output_rows_expected": input_validation["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS,
        "all_hours_complete": input_validation["complete_1h_row_count"] == EXPECTED_OUTPUT_ROWS
        and input_validation["incomplete_1h_row_count"] == 0,
        "no_fill_used": True,
        "output_schema_validated": output_schema_validated,
        "no_new_download_api_browse": True,
        "strict_3y_completeness_not_claimed": True,
        "not_research_backtest_edge": True,
        "not_broad_acquisition_ready": True,
        "schema_config_absent": True,
        "generic_runner_blocked": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    summary = build_summary(generated_at, output_path, input_validation, file_metadata, replacement_checks)
    gap_report = {
        "duplicate_open_time_count_total": summary["duplicate_open_time_count_total"],
        "missing_minute_count_total": summary["missing_minute_count_total"],
        "incomplete_hour_count": summary["incomplete_1h_row_count"],
        "complete_hour_count": summary["complete_1h_row_count"],
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "gap_duplicate_status": "PASS_NO_GAPS_DUPLICATES_OR_INCOMPLETE_HOURS",
    }
    schema_report = {
        "input_schema": EXPECTED_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
        "schema_match": summary["schema_match"],
        "output_schema_validated": summary["output_schema_validated"],
        "numeric_validation_passed": True,
        "timestamp_unit": "epoch_milliseconds",
    }
    provenance_report = {
        "source_zip_paths": [item["source_zip_path"] for item in file_metadata],
        "source_zip_sha256_by_file": {item["source_csv_file"]: item["source_zip_sha256"] for item in file_metadata},
        "source_zip_size_bytes_by_file": {item["source_csv_file"]: item["source_zip_size_bytes"] for item in file_metadata},
        "expected_inner_csv_by_date": {item["date"]: item["source_csv_file"] for item in file_metadata},
        "file_dates": [item["date"] for item in file_metadata],
        "build_timestamp_utc": generated_at,
        "output_csv_path": str(output_path),
        "output_row_count": summary["output_1h_row_count"],
        "validator_inputs_prepared": True,
        "url_iteration_performed": False,
        "provenance_status": "THREE_YEAR_MAX_AVAILABLE_SINGLE_SYMBOL_PIPELINE_VALIDATION_BUILD_OUTPUT",
    }
    compliance = {
        "no_new_download": True,
        "no_api": True,
        "no_browse": True,
        "no_url_fetch": True,
        "no_url_iteration": True,
        "no_multi_symbol": True,
        "no_dates_outside_max_available_file_range": True,
        "no_strategy_research": True,
        "no_backtest": True,
        "no_candidate_generation": True,
        "no_edge_profit_claim": True,
        "no_broad_acquisition_ready_claim": True,
        "no_strict_3_year_completeness_claim": True,
        "no_runtime_capital_live": True,
        "no_repo_schema_config": True,
        "no_generic_runner": True,
        "output_is_pipeline_3_year_max_available_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
    }
    execution_report = {
        "execution_scope": {
            "build_execution_performed": True,
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
        "input_validation": {
            key: summary[key]
            for key in [
                "file_count_processed",
                "all_source_zips_exist",
                "all_source_zip_sha256_match",
                "all_expected_inner_csv_present",
                "schema_match",
                "source_row_count_total",
                "expected_total_source_rows",
                "source_row_count_by_file_valid",
                "unique_symbol_count",
                "observed_symbol",
                "open_time_monotonic_by_file",
                "duplicate_open_time_count_total",
                "missing_minute_count_total",
                "observed_interval_ms",
                "one_minute_interval_validated",
                "observed_first_open_time_utc",
                "observed_last_open_time_utc",
                "daily_boundary_interpretation",
            ]
        },
        "aggregation_execution": {
            key: summary[key]
            for key in [
                "aggregation_performed_now",
                "data_build_performed",
                "output_1h_row_count",
                "expected_output_rows",
                "complete_1h_row_count",
                "incomplete_1h_row_count",
                "all_hours_complete",
                "synthetic_fill_used",
                "forward_fill_used",
                "backfill_used",
                "output_csv_created",
                "output_csv_path",
                "output_schema_validated",
            ]
        },
        "gap_duplicate_report": gap_report,
        "schema_validation_report": schema_report,
        "output_provenance_report": provenance_report,
        "compliance_report": compliance,
        "next_module_decision": {"next_module": NEXT_MODULE, "blocked_next_module": BLOCKED_NEXT_MODULE},
    }
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_report.json", execution_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_gap_duplicate_report.json", gap_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_schema_validation_report.json", schema_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_output_provenance_report.json", provenance_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_compliance_report.json", compliance)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_single_symbol_3_year_1m_to_1h_build_execution_status": BLOCKED_STATUS,
            "build_execution_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "strict_3y_completeness_claimed": False,
            "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
            "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
            "expected_file_count": EXPECTED_FILE_COUNT,
            "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
            "expected_output_rows": EXPECTED_OUTPUT_ROWS,
            "aggregation_performed_now": False,
            "data_build_performed": False,
            "synthetic_fill_used": False,
            "forward_fill_used": False,
            "backfill_used": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "broad_acquisition_ready": False,
            "source_manifest_acquisition_ready": False,
            "no_new_download": True,
            "data_download_performed": False,
            "data_fetch_performed": False,
            "new_download_performed_now": False,
            "external_download_allowed_now": False,
            "external_api_allowed_now": False,
            "okx_download_performed": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "dormant_repo_attention_count": 716,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "next_module": BLOCKED_NEXT_MODULE,
            "derived_live_repo_post_check": BLOCKED_STATUS,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_1m_to_1h_build_execution_summary.json", blocked)
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
