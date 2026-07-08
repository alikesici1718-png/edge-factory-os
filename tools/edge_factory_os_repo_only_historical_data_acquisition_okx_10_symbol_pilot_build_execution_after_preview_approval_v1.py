from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import subprocess
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_after_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "0a693c6"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_PREVIEW_APPROVED_EXECUTION_READY"
DOWNLOAD_VALIDATOR_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_"
    "VALIDATED_BUILD_PREVIEW_READY_NO_BUILD_NO_AGGREGATION"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_EXECUTION_"
    "PERFORMED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_EXECUTION_ANOMALY"
AFTER_QUALITY_PASS = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_EXECUTED_PENDING_"
    "VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
AFTER_QUALITY_BLOCKED = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_EXECUTION_BLOCKED_OR_ANOMALY_RECORDED"
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_validator_after_execution_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_blocked_or_anomaly_record_after_preview_approval_v1.py"
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
NEW_SYMBOLS = [symbol for symbol in PILOT_SYMBOLS if symbol != BTC_SYMBOL]
DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_TOTAL_PILOT_FILE_COUNT = 10_530
BTC_REUSED_FILE_COUNT = 1_053
NEW_SYMBOL_FILE_COUNT = 9_477
NOMINAL_SOURCE_ROWS_PER_SYMBOL = 1_516_320
NOMINAL_NEW_SYMBOL_SOURCE_ROWS = 13_646_880
NOMINAL_TOTAL_SOURCE_ROWS = 15_163_200
BTC_OUTPUT_ROWS = 25_272
BTC_COMPLETE_ROWS = 25_271
BTC_INCOMPLETE_ROWS = 1
BTC_AFFECTED_HOUR_UTC = "2026-04-14T07:00:00+00:00"
NOMINAL_OUTPUT_ROWS_PER_SYMBOL = 25_272
NOMINAL_NEW_SYMBOL_OUTPUT_ROWS = 227_448
NOMINAL_TOTAL_PILOT_OUTPUT_ROWS = 252_720
EXPECTED_MINUTE_MS = 60_000
EXPECTED_HOUR_MS = 3_600_000
OUTPUT_DIR = (
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    / MODULE_NAME
)
OUTPUT_DATA_DIR = OUTPUT_DIR / "pilot_1h_outputs"
ACTIVE_P1_ATTENTION_COUNT = 16
DORMANT_REPO_ATTENTION_COUNT = 716

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
PREVIEW_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_preview_after_download_validator_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)
BTC_POLICY_EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_rebuild_execution_after_material_conflict_policy_v1"
)
BTC_POLICY_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_rebuild_execution_validator_after_execution_v1"
)
BTC_POLICY_SUMMARY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_pipeline_summary_after_rebuild_validator_v1"
)

PREVIEW_SUMMARY = PREVIEW_DIR / f"{PREVIEW_DIR.name}_latest.json"
DOWNLOAD_VALIDATOR_SUMMARY = DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json"
DOWNLOAD_HASH_REPORT = DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_hash_validation_report.json"
BTC_POLICY_CLEAN_SUMMARY = BTC_POLICY_SUMMARY_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary.json"
BTC_POLICY_VALIDATOR_SUMMARY = (
    BTC_POLICY_VALIDATOR_DIR
    / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_summary.json"
)
BTC_POLICY_OUTPUT_VALIDATION = (
    BTC_POLICY_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_output_validation_report.json"
)

EXPECTED_INPUT_SCHEMA = [
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
    "policy_clean_build",
    "quarantine_applied",
    "incomplete_reason",
]
BUILD_SCOPE = "OKX_10_SYMBOL_PILOT_1M_TO_1H_PIPELINE_VALIDATION_ONLY"
DANGEROUS_FLAGS = {
    "new_download_performed_now": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed": False,
    "url_iteration_performed": False,
    "strategy_research_touched": False,
    "backtest_performed": False,
    "candidate_generation_touched": False,
    "edge_profit_claim_made": False,
    "safe_for_full_universe_acquisition": False,
    "broad_acquisition_ready": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
}
GLOBAL_STATE: dict[str, Any] = {
    "btc_policy_clean_reused": False,
    "btc_policy_clean_revalidated": False,
    "new_symbol_build_count": 0,
    "observed_new_symbol_source_rows": 0,
    "output_1h_row_count": 0,
    "complete_1h_row_count": 0,
    "incomplete_1h_row_count": 0,
    "anomaly_symbols": [],
    "duplicate_open_time_count_total": 0,
    "missing_minute_count_total": 0,
    "schema_mismatch_count": 0,
    "symbol_mismatch_count": 0,
    "output_csv_created": False,
    "output_manifest_created": False,
}


class BuildBlocked(RuntimeError):
    pass


@dataclass
class HourAggregate:
    symbol: str
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
        raise BuildBlocked(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.exists(), f"missing JSON artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"JSON artifact is not an object: {path}")
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


def parse_decimal(value: str, field_name: str, source_csv: str, row_number: int, allow_none_zero: bool = False) -> Decimal:
    if allow_none_zero and str(value).strip().lower() in {"none", ""}:
        return Decimal("0")
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise BuildBlocked(f"numeric parse failed {field_name} {source_csv} row={row_number}") from exc
    require(parsed.is_finite(), f"non-finite numeric {field_name} {source_csv} row={row_number}")
    return parsed


def decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal(1)))
    return format(normalized, "f")


def parse_confirm(value: str) -> bool:
    text = str(value).strip().lower()
    return text in {"1", "true", "t", "yes", "y"}


def expected_csv(symbol: str, day: str) -> str:
    return f"{symbol}-candlesticks-{day}.csv"


def output_path_for_symbol(symbol: str) -> Path:
    return OUTPUT_DATA_DIR / f"historical_okx_10_symbol_pilot_{symbol}_1h_output.csv"


def new_hour(symbol: str, row: dict[str, Any]) -> HourAggregate:
    agg = HourAggregate(
        symbol=symbol,
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
    agg.source_hashes.add(row["source_zip_sha256"])
    agg.source_csvs.add(row["source_csv_file"])
    agg.source_dates.add(row["source_date"])
    return agg


def update_hour(agg: HourAggregate, row: dict[str, Any]) -> None:
    require((row["open_time"] // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS == agg.hour_start, "hour update mismatch")
    agg.high = max(agg.high, row["high"])
    agg.low = min(agg.low, row["low"])
    agg.close = row["close"]
    agg.vol += row["vol"]
    agg.vol_ccy += row["vol_ccy"]
    agg.vol_quote += row["vol_quote"]
    agg.last_open_time = row["open_time"]
    agg.confirm_all = agg.confirm_all and row["confirm"]
    agg.row_count += 1
    agg.source_hashes.add(row["source_zip_sha256"])
    agg.source_csvs.add(row["source_csv_file"])
    agg.source_dates.add(row["source_date"])


def aggregate_to_row(agg: HourAggregate) -> dict[str, str]:
    complete = agg.row_count == 60
    require(complete, f"incomplete new-symbol hour {agg.symbol} {iso_utc_from_ms(agg.hour_start)} rows={agg.row_count}")
    return {
        "instrument_name": agg.symbol,
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
        "policy_clean_build": "false",
        "quarantine_applied": "false",
        "incomplete_reason": "",
    }


def validate_preflight(preview: dict[str, Any], download_summary: dict[str, Any], btc_validator: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved build execution module")
    require(preview.get("historical_data_acquisition_okx_10_symbol_pilot_build_preview_status") == PREVIOUS_STATUS, "preview status mismatch")
    require(preview.get("next_module") == REQUESTED_MODULE, "preview next_module mismatch")
    require(preview.get("pilot_symbol_count") == len(PILOT_SYMBOLS), "preview pilot symbol count mismatch")
    require(preview.get("pilot_symbols") == PILOT_SYMBOLS, "preview symbols mismatch")
    require(preview.get("nominal_total_source_rows") == NOMINAL_TOTAL_SOURCE_ROWS, "preview source row count mismatch")
    require(preview.get("nominal_total_output_rows") == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS, "preview output row count mismatch")
    require(preview.get("btc_policy_clean_reuse_allowed_in_future_execution") is True, "BTC reuse approval missing")
    require(preview.get("btc_policy_clean_reuse_requires_revalidation") is True, "BTC reuse revalidation requirement missing")
    require(preview.get("new_symbol_count_requiring_build") == len(NEW_SYMBOLS), "new symbol count mismatch")
    require(preview.get("future_build_must_fail_closed_on_new_symbol_material_conflicts") is True, "new-symbol conflict rule missing")
    require(preview.get("approval_grants_future_10_symbol_build_next") is True, "future build approval missing")
    require(preview.get("safe_for_full_universe_acquisition") is False, "full-universe readiness claim detected")
    require(preview.get("safe_for_research_backtest") is False, "research/backtest readiness claim detected")
    require(preview.get("safe_for_edge_claim") is False, "edge readiness claim detected")
    require(preview.get("replacement_checks_all_true") is True, "preview replacement checks not all true")

    require(
        download_summary.get("historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_status")
        == DOWNLOAD_VALIDATOR_STATUS,
        "download validator status mismatch",
    )
    require(download_summary.get("final_pilot_file_set_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "download final file count mismatch")
    require(download_summary.get("pilot_symbol_count") == len(PILOT_SYMBOLS), "download pilot symbol count mismatch")
    require(download_summary.get("all_hashes_match_recorded") is True, "download hash validation mismatch")
    require(download_summary.get("all_zip_open_success") is True, "download ZIP validation mismatch")
    require(download_summary.get("all_expected_inner_csv_present") is True, "download inner CSV validation mismatch")
    require(download_summary.get("all_expected_schema_match") is True, "download schema validation mismatch")
    require(download_summary.get("all_observed_symbols_match_expected") is True, "download symbol validation mismatch")
    require(download_summary.get("safe_for_10_symbol_build_preview") is True, "download validator not safe for preview")

    require(btc_validator.get("policy_clean_rebuild_execution_validated") is True, "BTC policy-clean validator did not pass")
    require(btc_validator.get("output_csv_exists") is True, "BTC policy-clean output missing")
    require(btc_validator.get("output_csv_row_count") == BTC_OUTPUT_ROWS, "BTC output row count mismatch")
    require(btc_validator.get("complete_1h_row_count") == BTC_COMPLETE_ROWS, "BTC complete row count mismatch")
    require(btc_validator.get("incomplete_1h_row_count") == BTC_INCOMPLETE_ROWS, "BTC incomplete row count mismatch")
    require(btc_validator.get("affected_hour_utc") == BTC_AFFECTED_HOUR_UTC, "BTC affected hour mismatch")
    require(btc_validator.get("output_valid_for_research_backtest") is False, "BTC research/backtest claim detected")
    require(btc_validator.get("output_valid_for_edge_claim") is False, "BTC edge claim detected")
    require(btc_validator.get("broad_acquisition_ready") is False, "BTC broad acquisition claim detected")


def load_hash_records(hash_report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    records = hash_report.get("hashes")
    require(isinstance(records, list), "hash report hashes is not a list")
    require(len(records) == EXPECTED_TOTAL_PILOT_FILE_COUNT, "hash report record count mismatch")
    by_symbol: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in PILOT_SYMBOLS}
    for record in records:
        require(isinstance(record, dict), "hash record is not an object")
        symbol = str(record.get("symbol"))
        require(symbol in by_symbol, f"unapproved symbol in hash report: {symbol}")
        by_symbol[symbol].append(record)
    for symbol, items in by_symbol.items():
        require(len(items) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL, f"{symbol} file count mismatch")
        items.sort(key=lambda item: str(item.get("date")))
        require(items[0].get("date") == DATE_RANGE_START and items[-1].get("date") == DATE_RANGE_END, f"{symbol} date range mismatch")
    return by_symbol


def recorded_hash(record: dict[str, Any]) -> str:
    return str(record.get("recorded_sha256") or record.get("sha256") or "")


def revalidate_btc_policy_clean(
    btc_items: list[dict[str, Any]],
    btc_summary: dict[str, Any],
    btc_output_validation: dict[str, Any],
) -> dict[str, Any]:
    source_hashes_match = 0
    for record in btc_items:
        path = Path(str(record.get("local_zip_path", "")))
        require(path.exists(), f"BTC source ZIP missing during reuse revalidation: {path}")
        require(sha256_file(path) == recorded_hash(record), f"BTC source ZIP hash mismatch during reuse revalidation: {path}")
        source_hashes_match += 1
    require(btc_summary.get("target_symbol") == BTC_SYMBOL, "BTC policy summary target mismatch")
    require(btc_summary.get("output_1h_row_count") == BTC_OUTPUT_ROWS, "BTC policy summary output count mismatch")
    require(btc_summary.get("complete_1h_row_count") == BTC_COMPLETE_ROWS, "BTC policy summary complete count mismatch")
    require(btc_summary.get("incomplete_1h_row_count") == BTC_INCOMPLETE_ROWS, "BTC policy summary incomplete count mismatch")
    require(btc_summary.get("affected_hour_utc") == BTC_AFFECTED_HOUR_UTC, "BTC policy summary affected hour mismatch")
    require(btc_summary.get("output_valid_for_pipeline_validation") is True, "BTC output not marked pipeline validation only")
    require(btc_summary.get("output_valid_for_research_backtest") is False, "BTC policy summary research/backtest claim detected")
    require(btc_summary.get("output_valid_for_edge_claim") is False, "BTC policy summary edge claim detected")
    require(btc_summary.get("broad_acquisition_ready") is False, "BTC policy summary broad acquisition claim detected")
    source_output = Path(str(btc_output_validation.get("output_csv_path", "")))
    require(source_output.exists(), f"BTC policy-clean output missing: {source_output}")
    require(btc_output_validation.get("output_csv_row_count") == BTC_OUTPUT_ROWS, "BTC output validation row count mismatch")
    require(btc_output_validation.get("output_observed_symbol") == BTC_SYMBOL, "BTC output validation symbol mismatch")
    require(btc_output_validation.get("output_schema") == OUTPUT_SCHEMA, "BTC output schema mismatch")
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    copied_output = output_path_for_symbol(BTC_SYMBOL)
    source_output_hash = sha256_file(source_output)
    shutil.copyfile(source_output, copied_output)
    copied_output_hash = sha256_file(copied_output)
    require(source_output_hash == copied_output_hash, "BTC copied output hash mismatch")
    GLOBAL_STATE["btc_policy_clean_reused"] = True
    GLOBAL_STATE["btc_policy_clean_revalidated"] = True
    return {
        "symbol": BTC_SYMBOL,
        "btc_policy_clean_reused": True,
        "btc_policy_clean_revalidated": True,
        "source_zip_hashes_revalidated": source_hashes_match,
        "output_csv_path": str(copied_output),
        "source_policy_clean_output_csv_path": str(source_output),
        "source_policy_clean_output_sha256": source_output_hash,
        "copied_policy_clean_output_sha256": copied_output_hash,
        "output_1h_row_count": BTC_OUTPUT_ROWS,
        "complete_1h_row_count": BTC_COMPLETE_ROWS,
        "incomplete_1h_row_count": BTC_INCOMPLETE_ROWS,
        "affected_hour_utc": BTC_AFFECTED_HOUR_UTC,
        "pipeline_validation_only": True,
    }


def process_new_symbol(symbol: str, records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    output_path = output_path_for_symbol(symbol)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source_rows = 0
    output_rows = 0
    complete_rows = 0
    duplicate_count = 0
    missing_count = 0
    schema_mismatches = 0
    symbol_mismatches = 0
    previous_open_time: int | None = None
    current_hour: HourAggregate | None = None
    file_reports: list[dict[str, Any]] = []
    schema_reports: list[dict[str, Any]] = []

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_SCHEMA)
        writer.writeheader()
        for record in records:
            day = str(record.get("date"))
            require(DATE_RANGE_START <= day <= DATE_RANGE_END, f"{symbol} date out of range: {day}")
            path = Path(str(record.get("local_zip_path", "")))
            require(path.exists(), f"{symbol} ZIP missing: {path}")
            digest = sha256_file(path)
            require(digest == recorded_hash(record), f"{symbol} SHA256 mismatch: {path}")
            inner_csv = expected_csv(symbol, day)
            file_row_count = 0
            first_file_open_time: int | None = None
            last_file_open_time: int | None = None
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                require(len(names) <= 10, f"{symbol} too many ZIP members: {path}")
                require(all(safe_zip_member(name) for name in names), f"{symbol} ZIP traversal risk: {path}")
                require(inner_csv in names, f"{symbol} expected CSV missing: {inner_csv}")
                with archive.open(inner_csv, "r") as raw:
                    reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
                    if reader.fieldnames != EXPECTED_INPUT_SCHEMA:
                        schema_mismatches += 1
                        GLOBAL_STATE["schema_mismatch_count"] = int(GLOBAL_STATE["schema_mismatch_count"]) + 1
                        GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
                        raise BuildBlocked(f"{symbol} schema mismatch: {inner_csv}")
                    for row_number, raw_row in enumerate(reader, start=2):
                        GLOBAL_STATE["observed_new_symbol_source_rows"] = int(GLOBAL_STATE["observed_new_symbol_source_rows"]) + 1
                        if raw_row.get("instrument_name") != symbol:
                            symbol_mismatches += 1
                            GLOBAL_STATE["symbol_mismatch_count"] = int(GLOBAL_STATE["symbol_mismatch_count"]) + 1
                            GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
                            raise BuildBlocked(f"{symbol} symbol mismatch {inner_csv} row={row_number}")
                        try:
                            open_time = int(str(raw_row["open_time"]).strip())
                        except ValueError as exc:
                            raise BuildBlocked(f"{symbol} open_time parse failed {inner_csv} row={row_number}") from exc
                        if previous_open_time is not None:
                            delta = open_time - previous_open_time
                            if delta <= 0:
                                duplicate_count += 1
                                GLOBAL_STATE["duplicate_open_time_count_total"] = int(GLOBAL_STATE["duplicate_open_time_count_total"]) + 1
                                GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
                                raise BuildBlocked(f"{symbol} duplicate or non-monotonic open_time {open_time}")
                            if delta != EXPECTED_MINUTE_MS:
                                missing_count += max(0, (delta // EXPECTED_MINUTE_MS) - 1)
                                GLOBAL_STATE["missing_minute_count_total"] = (
                                    int(GLOBAL_STATE["missing_minute_count_total"])
                                    + max(1, max(0, (delta // EXPECTED_MINUTE_MS) - 1))
                                )
                                GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
                                raise BuildBlocked(f"{symbol} missing minute gap after {previous_open_time}: delta={delta}")
                        previous_open_time = open_time
                        first_file_open_time = open_time if first_file_open_time is None else first_file_open_time
                        last_file_open_time = open_time
                        open_ = parse_decimal(raw_row["open"], "open", inner_csv, row_number)
                        high = parse_decimal(raw_row["high"], "high", inner_csv, row_number)
                        low = parse_decimal(raw_row["low"], "low", inner_csv, row_number)
                        close = parse_decimal(raw_row["close"], "close", inner_csv, row_number)
                        vol = parse_decimal(raw_row["vol"], "vol", inner_csv, row_number)
                        vol_ccy = parse_decimal(raw_row["vol_ccy"], "vol_ccy", inner_csv, row_number, allow_none_zero=True)
                        vol_quote = parse_decimal(raw_row["vol_quote"], "vol_quote", inner_csv, row_number, allow_none_zero=True)
                        require(vol >= 0 and vol_ccy >= 0 and vol_quote >= 0, f"{symbol} negative volume {inner_csv} row={row_number}")
                        require(high >= max(open_, close, low), f"{symbol} invalid high {inner_csv} row={row_number}")
                        require(low <= min(open_, close, high), f"{symbol} invalid low {inner_csv} row={row_number}")
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
                            "source_csv_file": inner_csv,
                            "source_date": day,
                        }
                        hour_start = (open_time // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS
                        if current_hour is None:
                            current_hour = new_hour(symbol, minute_row)
                        elif hour_start == current_hour.hour_start:
                            update_hour(current_hour, minute_row)
                        else:
                            out_row = aggregate_to_row(current_hour)
                            writer.writerow(out_row)
                            output_rows += 1
                            complete_rows += 1
                            GLOBAL_STATE["output_1h_row_count"] = int(GLOBAL_STATE["output_1h_row_count"]) + 1
                            GLOBAL_STATE["complete_1h_row_count"] = int(GLOBAL_STATE["complete_1h_row_count"]) + 1
                            current_hour = new_hour(symbol, minute_row)
                        file_row_count += 1
                        source_rows += 1
            require(file_row_count == 1440, f"{symbol} source row count mismatch {inner_csv}: {file_row_count}")
            file_reports.append(
                {
                    "symbol": symbol,
                    "date": day,
                    "source_zip_path": str(path),
                    "source_zip_sha256": digest,
                    "source_csv_file": inner_csv,
                    "source_row_count": file_row_count,
                    "first_open_time": first_file_open_time,
                    "last_open_time": last_file_open_time,
                }
            )
            schema_reports.append(
                {
                    "symbol": symbol,
                    "date": day,
                    "source_csv_file": inner_csv,
                    "schema_match": True,
                    "symbol_match": True,
                }
            )
        if current_hour is not None:
            out_row = aggregate_to_row(current_hour)
            writer.writerow(out_row)
            output_rows += 1
            complete_rows += 1
            GLOBAL_STATE["output_1h_row_count"] = int(GLOBAL_STATE["output_1h_row_count"]) + 1
            GLOBAL_STATE["complete_1h_row_count"] = int(GLOBAL_STATE["complete_1h_row_count"]) + 1

    output_hash = sha256_file(output_path)
    GLOBAL_STATE["new_symbol_build_count"] = int(GLOBAL_STATE["new_symbol_build_count"]) + 1
    GLOBAL_STATE["output_csv_created"] = True
    require(source_rows == NOMINAL_SOURCE_ROWS_PER_SYMBOL, f"{symbol} source row count mismatch: {source_rows}")
    require(output_rows == NOMINAL_OUTPUT_ROWS_PER_SYMBOL, f"{symbol} output row count mismatch: {output_rows}")
    return (
        {
            "symbol": symbol,
            "source_row_count": source_rows,
            "output_1h_row_count": output_rows,
            "complete_1h_row_count": complete_rows,
            "incomplete_1h_row_count": 0,
            "duplicate_open_time_count": duplicate_count,
            "missing_minute_count": missing_count,
            "schema_mismatch_count": schema_mismatches,
            "symbol_mismatch_count": symbol_mismatches,
            "output_csv_path": str(output_path),
            "output_csv_sha256": output_hash,
            "output_csv_created": True,
        },
        file_reports,
        schema_reports,
    )


def write_reports(payloads: dict[str, Any]) -> None:
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_execution_report.json", payloads["execution_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_1m_to_1h_output_manifest.json", payloads["output_manifest"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_gap_duplicate_report.json", payloads["gap_duplicate_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_schema_validation_report.json", payloads["schema_validation_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_output_provenance_report.json", payloads["output_provenance_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_execution_compliance_report.json", payloads["compliance_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_execution_summary.json", payloads["summary"])


def main() -> None:
    generated_at = utc_now()
    preview = load_json(PREVIEW_SUMMARY)
    download_summary = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    hash_report = load_json(DOWNLOAD_HASH_REPORT)
    btc_summary = load_json(BTC_POLICY_CLEAN_SUMMARY)
    btc_validator = load_json(BTC_POLICY_VALIDATOR_SUMMARY)
    btc_output_validation = load_json(BTC_POLICY_OUTPUT_VALIDATION)
    validate_preflight(preview, download_summary, btc_validator)
    by_symbol = load_hash_records(hash_report)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    btc_reuse = revalidate_btc_policy_clean(by_symbol[BTC_SYMBOL], btc_summary, btc_output_validation)

    symbol_results: list[dict[str, Any]] = [btc_reuse]
    source_file_reports: list[dict[str, Any]] = []
    schema_reports: list[dict[str, Any]] = []
    for symbol in NEW_SYMBOLS:
        result, files, schemas = process_new_symbol(symbol, by_symbol[symbol])
        symbol_results.append(result)
        source_file_reports.extend(files)
        schema_reports.extend(schemas)

    observed_new_symbol_source_rows = sum(int(row["source_row_count"]) for row in symbol_results if row["symbol"] != BTC_SYMBOL)
    output_1h_row_count = sum(int(row["output_1h_row_count"]) for row in symbol_results)
    complete_1h_row_count = sum(int(row["complete_1h_row_count"]) for row in symbol_results)
    incomplete_1h_row_count = sum(int(row["incomplete_1h_row_count"]) for row in symbol_results)
    duplicate_open_time_count_total = sum(int(row.get("duplicate_open_time_count", 0)) for row in symbol_results)
    missing_minute_count_total = sum(int(row.get("missing_minute_count", 0)) for row in symbol_results)
    schema_mismatch_count = sum(int(row.get("schema_mismatch_count", 0)) for row in symbol_results)
    symbol_mismatch_count = sum(int(row.get("symbol_mismatch_count", 0)) for row in symbol_results)
    new_symbol_anomaly_detected = any(
        int(row.get("duplicate_open_time_count", 0))
        or int(row.get("missing_minute_count", 0))
        or int(row.get("schema_mismatch_count", 0))
        or int(row.get("symbol_mismatch_count", 0))
        or (row["symbol"] != BTC_SYMBOL and row["output_1h_row_count"] != NOMINAL_OUTPUT_ROWS_PER_SYMBOL)
        for row in symbol_results
    )
    anomaly_symbols = [
        row["symbol"]
        for row in symbol_results
        if row["symbol"] != BTC_SYMBOL
        and (
            int(row.get("duplicate_open_time_count", 0))
            or int(row.get("missing_minute_count", 0))
            or int(row.get("schema_mismatch_count", 0))
            or int(row.get("symbol_mismatch_count", 0))
            or row["output_1h_row_count"] != NOMINAL_OUTPUT_ROWS_PER_SYMBOL
        )
    ]
    require(not new_symbol_anomaly_detected, f"new symbol anomalies detected: {anomaly_symbols}")
    require(observed_new_symbol_source_rows == NOMINAL_NEW_SYMBOL_SOURCE_ROWS, "new symbol source row count mismatch")
    require(output_1h_row_count == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS, "pilot output row count mismatch")
    require(complete_1h_row_count == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS - 1, "complete 1h row count mismatch")
    require(incomplete_1h_row_count == 1, "incomplete 1h row count mismatch")

    output_manifest = {
        "output_manifest_created": True,
        "output_mode": "PER_SYMBOL_1H_CSVS_PLUS_COMBINED_MANIFEST",
        "output_schema": OUTPUT_SCHEMA,
        "symbol_outputs": symbol_results,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "output_1h_row_count": output_1h_row_count,
        "complete_1h_row_count": complete_1h_row_count,
        "incomplete_1h_row_count": incomplete_1h_row_count,
        "all_symbols_complete": False,
        "output_is_pilot_pipeline_validation_only": True,
    }
    GLOBAL_STATE["new_symbol_build_count"] = len(NEW_SYMBOLS)
    GLOBAL_STATE["observed_new_symbol_source_rows"] = observed_new_symbol_source_rows
    GLOBAL_STATE["output_1h_row_count"] = output_1h_row_count
    GLOBAL_STATE["complete_1h_row_count"] = complete_1h_row_count
    GLOBAL_STATE["incomplete_1h_row_count"] = incomplete_1h_row_count
    GLOBAL_STATE["output_csv_created"] = True
    GLOBAL_STATE["output_manifest_created"] = True
    gap_duplicate_report = {
        "gap_duplicate_report_created": True,
        "new_symbol_anomaly_detected": new_symbol_anomaly_detected,
        "anomaly_symbol_count": len(anomaly_symbols),
        "anomaly_symbols": anomaly_symbols,
        "duplicate_open_time_count_total": duplicate_open_time_count_total,
        "missing_minute_count_total": missing_minute_count_total,
        "btc_incomplete_1h_row_count": BTC_INCOMPLETE_ROWS,
        "btc_affected_hour_utc": BTC_AFFECTED_HOUR_UTC,
    }
    schema_validation_report = {
        "schema_validation_report_created": True,
        "expected_input_schema": EXPECTED_INPUT_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
        "schema_mismatch_count": schema_mismatch_count,
        "symbol_mismatch_count": symbol_mismatch_count,
        "schema_validations": schema_reports,
    }
    output_provenance_report = {
        "output_provenance_report_created": True,
        "btc_policy_clean_reuse": btc_reuse,
        "new_symbol_source_file_count": len(source_file_reports),
        "new_symbol_source_files": source_file_reports,
        "source_hashes_revalidated_before_csv_read": True,
        "approved_zip_file_set_only": True,
    }
    compliance_report = {
        "compliance_report_created": True,
        "no_new_download": True,
        "new_download_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "url_fetch_performed": False,
        "url_iteration_performed": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_is_pilot_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "runtime_touched": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "schema_or_config_created": False,
        "generic_runner_implementation_remains_blocked": True,
    }
    replacement_checks = {
        "expected_head": True,
        "repo_clean_or_only_approved_tool_change": True,
        "preview_approval_valid": True,
        "download_validator_valid": True,
        "file_count_total_10530": EXPECTED_TOTAL_PILOT_FILE_COUNT == sum(len(by_symbol[s]) for s in PILOT_SYMBOLS),
        "btc_policy_clean_reused": btc_reuse["btc_policy_clean_reused"],
        "btc_policy_clean_revalidated": btc_reuse["btc_policy_clean_revalidated"],
        "new_symbol_build_count_9": len([row for row in symbol_results if row["symbol"] != BTC_SYMBOL]) == 9,
        "new_symbol_source_rows_expected": observed_new_symbol_source_rows == NOMINAL_NEW_SYMBOL_SOURCE_ROWS,
        "output_rows_expected": output_1h_row_count == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS,
        "complete_rows_expected": complete_1h_row_count == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS - 1,
        "incomplete_rows_expected": incomplete_1h_row_count == 1,
        "no_new_symbol_anomaly": not new_symbol_anomaly_detected,
        "no_duplicate_open_times": duplicate_open_time_count_total == 0,
        "no_missing_minutes": missing_minute_count_total == 0,
        "no_schema_symbol_mismatch": schema_mismatch_count == 0 and symbol_mismatch_count == 0,
        "no_fill_used": True,
        "no_new_download_api_browse": True,
        "not_research_backtest_edge_full_universe_broad": True,
        "schema_config_absent": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": EXPECTED_HEAD,
        "historical_data_acquisition_okx_10_symbol_pilot_build_execution_status": PASS_STATUS,
        "build_execution_performed": True,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "btc_policy_clean_reused": True,
        "btc_policy_clean_revalidated": True,
        "new_symbol_build_count": len(NEW_SYMBOLS),
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "file_count_total": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "btc_reused_file_count": BTC_REUSED_FILE_COUNT,
        "new_symbol_file_count": NEW_SYMBOL_FILE_COUNT,
        "nominal_total_source_rows": NOMINAL_TOTAL_SOURCE_ROWS,
        "observed_new_symbol_source_rows": observed_new_symbol_source_rows,
        "nominal_total_pilot_output_rows": NOMINAL_TOTAL_PILOT_OUTPUT_ROWS,
        "output_1h_row_count": output_1h_row_count,
        "complete_1h_row_count": complete_1h_row_count,
        "incomplete_1h_row_count": incomplete_1h_row_count,
        "all_symbols_complete": False,
        "new_symbol_anomaly_detected": new_symbol_anomaly_detected,
        "anomaly_symbol_count": len(anomaly_symbols),
        "anomaly_symbols": anomaly_symbols,
        "duplicate_open_time_count_total": duplicate_open_time_count_total,
        "missing_minute_count_total": missing_minute_count_total,
        "schema_mismatch_count": schema_mismatch_count,
        "symbol_mismatch_count": symbol_mismatch_count,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": True,
        "output_manifest_created": True,
        "output_is_pilot_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "no_new_download": True,
        "new_download_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_build_performed": True,
        "aggregation_performed_now": True,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
        "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "current_evidence_chain_quality_after_execution": AFTER_QUALITY_PASS,
        "next_module": NEXT_MODULE_PASS,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count_at_execution_run": tracked_python_count(),
    }
    execution_report = {
        **summary,
        "symbol_results": symbol_results,
    }
    payloads = {
        "execution_report": execution_report,
        "output_manifest": output_manifest,
        "gap_duplicate_report": gap_duplicate_report,
        "schema_validation_report": schema_validation_report,
        "output_provenance_report": output_provenance_report,
        "compliance_report": compliance_report,
        "summary": summary,
    }
    write_reports(payloads)
    require(replacement_checks_all_true, "replacement checks did not all pass")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BuildBlocked as exc:
        anomaly_symbols = list(GLOBAL_STATE.get("anomaly_symbols", []))
        summary = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_build_execution_status": BLOCKED_STATUS,
            "build_execution_performed": False,
            "pilot_symbol_count": len(PILOT_SYMBOLS),
            "pilot_symbols": PILOT_SYMBOLS,
            "btc_policy_clean_reused": bool(GLOBAL_STATE["btc_policy_clean_reused"]),
            "btc_policy_clean_revalidated": bool(GLOBAL_STATE["btc_policy_clean_revalidated"]),
            "new_symbol_build_count": int(GLOBAL_STATE["new_symbol_build_count"]),
            "date_range_start": DATE_RANGE_START,
            "date_range_end": DATE_RANGE_END,
            "file_count_total": EXPECTED_TOTAL_PILOT_FILE_COUNT,
            "btc_reused_file_count": BTC_REUSED_FILE_COUNT if GLOBAL_STATE["btc_policy_clean_revalidated"] else 0,
            "new_symbol_file_count": NEW_SYMBOL_FILE_COUNT,
            "nominal_total_source_rows": NOMINAL_TOTAL_SOURCE_ROWS,
            "observed_new_symbol_source_rows": int(GLOBAL_STATE["observed_new_symbol_source_rows"]),
            "nominal_total_pilot_output_rows": NOMINAL_TOTAL_PILOT_OUTPUT_ROWS,
            "output_1h_row_count": int(GLOBAL_STATE["output_1h_row_count"]),
            "complete_1h_row_count": int(GLOBAL_STATE["complete_1h_row_count"]),
            "incomplete_1h_row_count": int(GLOBAL_STATE["incomplete_1h_row_count"]),
            "all_symbols_complete": False,
            "new_symbol_anomaly_detected": True,
            "anomaly_symbol_count": len(anomaly_symbols),
            "anomaly_symbols": anomaly_symbols,
            "duplicate_open_time_count_total": int(GLOBAL_STATE["duplicate_open_time_count_total"]),
            "missing_minute_count_total": int(GLOBAL_STATE["missing_minute_count_total"]),
            "schema_mismatch_count": int(GLOBAL_STATE["schema_mismatch_count"]),
            "symbol_mismatch_count": int(GLOBAL_STATE["symbol_mismatch_count"]),
            "synthetic_fill_used": False,
            "forward_fill_used": False,
            "backfill_used": False,
            "output_csv_created": bool(GLOBAL_STATE["output_csv_created"]),
            "output_manifest_created": bool(GLOBAL_STATE["output_manifest_created"]),
            "output_is_pilot_pipeline_validation_only": True,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "no_new_download": True,
            "new_download_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "current_evidence_chain_quality_after_execution": AFTER_QUALITY_BLOCKED,
            "next_module": NEXT_MODULE_BLOCKED,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_execution_report.json",
            {**summary, "blocked_reason": str(exc)},
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_1m_to_1h_output_manifest.json",
            {
                "output_manifest_created": False,
                "blocked_before_complete_manifest": True,
                "anomaly_symbols": anomaly_symbols,
                "btc_policy_clean_reused": bool(GLOBAL_STATE["btc_policy_clean_reused"]),
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_gap_duplicate_report.json",
            {
                "gap_duplicate_report_created": True,
                "new_symbol_anomaly_detected": True,
                "anomaly_symbol_count": len(anomaly_symbols),
                "anomaly_symbols": anomaly_symbols,
                "duplicate_open_time_count_total": int(GLOBAL_STATE["duplicate_open_time_count_total"]),
                "missing_minute_count_total": int(GLOBAL_STATE["missing_minute_count_total"]),
                "blocked_reason": str(exc),
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_schema_validation_report.json",
            {
                "schema_validation_report_created": True,
                "schema_mismatch_count": int(GLOBAL_STATE["schema_mismatch_count"]),
                "symbol_mismatch_count": int(GLOBAL_STATE["symbol_mismatch_count"]),
                "blocked_reason": str(exc),
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_output_provenance_report.json",
            {
                "output_provenance_report_created": True,
                "btc_policy_clean_reused": bool(GLOBAL_STATE["btc_policy_clean_reused"]),
                "btc_policy_clean_revalidated": bool(GLOBAL_STATE["btc_policy_clean_revalidated"]),
                "blocked_reason": str(exc),
            },
        )
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_execution_summary.json", summary)
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_build_execution_compliance_report.json",
            {
                "compliance_report_created": True,
                "no_new_download": True,
                "new_download_performed_now": False,
                "okx_api_call_performed": False,
                "okx_browse_performed": False,
                "output_valid_for_research_backtest": False,
                "output_valid_for_edge_claim": False,
                "safe_for_full_universe_acquisition": False,
                "broad_acquisition_ready": False,
                "schema_or_config_created": False,
                "generic_runner_implementation_remains_blocked": True,
            },
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        raise SystemExit(1)
