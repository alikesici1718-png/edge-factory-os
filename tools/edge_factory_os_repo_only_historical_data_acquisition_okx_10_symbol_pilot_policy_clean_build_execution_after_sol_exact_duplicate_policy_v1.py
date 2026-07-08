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
    "policy_clean_build_execution_after_sol_exact_duplicate_policy_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "8255111"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_EXACT_DUPLICATE_"
    "POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
)
DOWNLOAD_VALIDATOR_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_"
    "VALIDATED_BUILD_PREVIEW_READY_NO_BUILD_NO_AGGREGATION"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_EXECUTION_"
    "PERFORMED_PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "EXECUTION_ANOMALY"
)
AFTER_QUALITY_PASS = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_EXECUTED_"
    "PENDING_VALIDATOR_PIPELINE_VALIDATION_ONLY"
)
AFTER_QUALITY_BLOCKED = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_EXECUTION_"
    "BLOCKED_OR_ANOMALY_RECORDED"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_validator_after_execution_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_sol_policy_v1.py"
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
EXPECTED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY = 13_647_209
EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY = 13_646_879
ETH_RAW_ROWS_BEFORE_POLICY = 1_516_648
ETH_EXACT_DUPLICATE_ROWS_DROPPED = 327
ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED = 2
ETH_CLEAN_SOURCE_ROWS_AFTER_POLICY = 1_516_319
ETH_COMPLETE_1H_ROWS_AFTER_POLICY = 25_271
ETH_INCOMPLETE_1H_ROWS_AFTER_POLICY = 1
ETH_AFFECTED_HOUR_COUNT_AFTER_POLICY = 1
ETH_DUPLICATE_OPEN_TIME = 1_697_108_400_000
ETH_DUPLICATE_OPEN_TIME_UTC = "2023-10-12T11:00:00+00:00"
ETH_DUPLICATE_SOURCE_DATE = "2023-10-12"
ETH_DUPLICATE_SOURCE_FILE = "ETH-USDT-SWAP-candlesticks-2023-10-12.csv"
SOL_DUPLICATE_OPEN_TIME = 1_697_108_400_000
SOL_DUPLICATE_OPEN_TIME_UTC = "2023-10-12T11:00:00+00:00"
SOL_DUPLICATE_SOURCE_DATE = "2023-10-12"
SOL_DUPLICATE_SOURCE_FILE = "SOL-USDT-SWAP-candlesticks-2023-10-12.csv"
SOL_EXACT_DUPLICATE_ROWS_DROPPED = 1
SOL_MATERIAL_CONFLICT_ROWS_QUARANTINED = 0
SOL_CLEAN_SOURCE_ROWS_AFTER_POLICY = 1_516_320
SOL_COMPLETE_1H_ROWS_AFTER_POLICY = 25_272
SOL_INCOMPLETE_1H_ROWS_AFTER_POLICY = 0
NOMINAL_TOTAL_SOURCE_ROWS = 15_163_200
BTC_OUTPUT_ROWS = 25_272
BTC_COMPLETE_ROWS = 25_271
BTC_INCOMPLETE_ROWS = 1
BTC_AFFECTED_HOUR_UTC = "2026-04-14T07:00:00+00:00"
NOMINAL_OUTPUT_ROWS_PER_SYMBOL = 25_272
NOMINAL_NEW_SYMBOL_OUTPUT_ROWS = 227_448
NOMINAL_TOTAL_PILOT_OUTPUT_ROWS = 252_720
EXPECTED_TOTAL_COMPLETE_1H_ROWS_AFTER_POLICY = 252_718
EXPECTED_TOTAL_INCOMPLETE_1H_ROWS_AFTER_POLICY = 2
EXPECTED_MINUTE_MS = 60_000
EXPECTED_HOUR_MS = 3_600_000
OUTPUT_DIR = (
    Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    / MODULE_NAME
)
OUTPUT_DATA_DIR = OUTPUT_DIR / "pilot_1h_outputs"
ACTIVE_P1_ATTENTION_COUNT = 12
DORMANT_REPO_ATTENTION_COUNT = 716

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
ETH_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1"
)
SOL_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_exact_duplicate_policy_after_diagnostic_v1"
)
RESIDUAL_DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_policy_application_residual_duplicate_diagnostic_after_build_block_v1"
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

SOL_POLICY_SUMMARY = SOL_POLICY_DIR / "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy_summary.json"
SOL_EXACT_POLICY = SOL_POLICY_DIR / "historical_okx_10_symbol_pilot_sol_exact_duplicate_policy.json"
SOL_EXACT_DROP_POLICY = SOL_POLICY_DIR / "historical_okx_10_symbol_pilot_sol_exact_duplicate_drop_policy.json"
POLICY_CLEAN_BUILD_PREVIEW = SOL_POLICY_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_preview_after_sol_policy.json"
POLICY_CLEAN_BUILD_APPROVAL = SOL_POLICY_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_approval_record_after_sol_policy.json"
ETH_POLICY_SUMMARY = ETH_POLICY_DIR / "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_summary.json"
ETH_MATERIAL_POLICY = ETH_POLICY_DIR / "historical_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy.json"
ETH_POLICY_COUNTS = ETH_POLICY_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_group_policy_counts.json"
ETH_QUARANTINE_POLICY = ETH_POLICY_DIR / "historical_okx_10_symbol_pilot_eth_material_conflict_quarantine_policy.json"
ETH_RESIDUAL_RAW_GROUP_REPORT = RESIDUAL_DIAGNOSTIC_DIR / "historical_okx_10_symbol_pilot_eth_residual_duplicate_raw_group_report.json"
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
BUILD_SCOPE = "OKX_10_SYMBOL_PILOT_POLICY_CLEAN_1M_TO_1H_PIPELINE_VALIDATION_ONLY"
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
    "clean_new_symbol_source_rows_after_policy": 0,
    "eth_exact_duplicate_rows_dropped": 0,
    "eth_material_conflict_rows_quarantined": 0,
    "eth_clean_source_rows_after_policy": 0,
    "eth_complete_1h_row_count": 0,
    "eth_incomplete_1h_row_count": 0,
    "sol_exact_duplicate_rows_dropped": 0,
    "sol_clean_source_rows_after_policy": 0,
    "sol_complete_1h_row_count": 0,
    "sol_incomplete_1h_row_count": 0,
    "eth_drop_audit_rows": [],
    "eth_quarantine_audit_rows": [],
    "sol_drop_audit_rows": [],
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


def normalized_decimal_text(value: str) -> str:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return str(value).strip()
    normalized = parsed.normalize()
    if normalized == 0:
        return "0"
    rendered = format(normalized, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def normalized_confirm_text(value: str) -> str:
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y"}:
        return "1"
    if text in {"0", "false", "f", "no", "n"}:
        return "0"
    return str(value).strip()


def normalized_input_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "instrument_name": str(row.get("instrument_name", "")).strip(),
        "open": normalized_decimal_text(str(row.get("open", ""))),
        "high": normalized_decimal_text(str(row.get("high", ""))),
        "low": normalized_decimal_text(str(row.get("low", ""))),
        "close": normalized_decimal_text(str(row.get("close", ""))),
        "vol": normalized_decimal_text(str(row.get("vol", ""))),
        "vol_ccy": normalized_decimal_text(str(row.get("vol_ccy", ""))),
        "vol_quote": normalized_decimal_text(str(row.get("vol_quote", ""))),
        "open_time": str(int(str(row.get("open_time", "")).strip())),
        "confirm": normalized_confirm_text(str(row.get("confirm", ""))),
    }


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


def aggregate_to_row(agg: HourAggregate, allow_incomplete: bool = False, incomplete_reason: str = "") -> dict[str, str]:
    complete = agg.row_count == 60
    require(
        complete or allow_incomplete,
        f"incomplete new-symbol hour {agg.symbol} {iso_utc_from_ms(agg.hour_start)} rows={agg.row_count}",
    )
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
        "complete_hour": "true" if complete else "false",
        "confirm": "true" if agg.confirm_all else "false",
        "source_first_open_time": str(agg.first_open_time),
        "source_last_open_time": str(agg.last_open_time),
        "source_zip_sha256": "|".join(sorted(agg.source_hashes)),
        "source_csv_file": "|".join(sorted(agg.source_csvs)),
        "source_date": "|".join(sorted(agg.source_dates)),
        "build_scope": BUILD_SCOPE,
        "policy_clean_build": "true",
        "quarantine_applied": "true" if incomplete_reason else "false",
        "incomplete_reason": "" if complete else incomplete_reason,
    }


def validate_preflight(
    sol_policy_summary: dict[str, Any],
    sol_exact_policy: dict[str, Any],
    sol_drop_policy: dict[str, Any],
    policy_summary: dict[str, Any],
    material_policy: dict[str, Any],
    policy_counts: dict[str, Any],
    quarantine_policy: dict[str, Any],
    raw_group_report: dict[str, Any],
    build_preview: dict[str, Any],
    build_approval: dict[str, Any],
    download_summary: dict[str, Any],
    btc_validator: dict[str, Any],
) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved policy-clean build execution module")
    require(
        sol_policy_summary.get("historical_data_acquisition_okx_10_symbol_pilot_sol_exact_duplicate_policy_status")
        == PREVIOUS_STATUS,
        "SOL exact duplicate policy status mismatch",
    )
    require(sol_policy_summary.get("next_module") == REQUESTED_MODULE, "SOL policy next_module mismatch")
    require(sol_policy_summary.get("target_symbol") == "SOL-USDT-SWAP", "SOL policy target symbol mismatch")
    require(
        sol_policy_summary.get("duplicate_resolution_policy")
        == "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROW_KEEP_ONE_CANONICAL_ROW",
        "SOL duplicate resolution policy mismatch",
    )
    require(sol_policy_summary.get("duplicate_open_time") == SOL_DUPLICATE_OPEN_TIME, "SOL duplicate open_time mismatch")
    require(sol_policy_summary.get("duplicate_open_time_utc") == SOL_DUPLICATE_OPEN_TIME_UTC, "SOL duplicate open_time UTC mismatch")
    require(sol_policy_summary.get("duplicate_source_date") == SOL_DUPLICATE_SOURCE_DATE, "SOL duplicate source date mismatch")
    require(sol_policy_summary.get("duplicate_source_file") == SOL_DUPLICATE_SOURCE_FILE, "SOL duplicate source file mismatch")
    require(sol_policy_summary.get("exact_duplicate_extra_rows_to_drop") == SOL_EXACT_DUPLICATE_ROWS_DROPPED, "SOL exact duplicate drop count mismatch")
    require(sol_policy_summary.get("material_conflict_present") is False, "SOL material conflict flag mismatch")
    require(sol_policy_summary.get("exact_duplicate_drop_allowed") is True, "SOL exact duplicate drop not allowed")
    require(sol_policy_summary.get("btc_policy_clean_reuse_required") is True, "SOL policy BTC reuse missing")
    require(sol_policy_summary.get("eth_material_policy_required") is True, "SOL policy ETH material policy missing")
    require(sol_policy_summary.get("sol_exact_dedupe_required") is True, "SOL exact dedupe requirement missing")
    require(sol_policy_summary.get("approval_grants_future_10_symbol_policy_clean_build_next") is True, "SOL future build approval missing")
    require(sol_policy_summary.get("active_p0_blocker_count") == 0, "SOL policy P0 mismatch")
    require(sol_policy_summary.get("replacement_checks_all_true") is True, "SOL policy replacement checks mismatch")
    for key in [
        "choose_conflicting_row_allowed",
        "average_conflicting_rows_allowed",
        "merge_conflicting_rows_allowed",
        "ohlcv_modification_allowed",
        "data_build_performed",
        "aggregation_performed_now",
        "output_csv_created",
        "output_valid_for_research_backtest",
        "output_valid_for_edge_claim",
        "safe_for_full_universe_acquisition",
        "broad_acquisition_ready",
    ]:
        require(sol_policy_summary.get(key) is False, f"SOL policy {key} must be false")
    require(sol_exact_policy.get("sol_exact_duplicate_policy_created") is True, "SOL exact policy artifact missing")
    require(sol_exact_policy.get("exact_duplicate_extra_rows_to_drop") == SOL_EXACT_DUPLICATE_ROWS_DROPPED, "SOL exact policy drop count mismatch")
    require(sol_drop_policy.get("sol_exact_duplicate_drop_policy_created") is True, "SOL drop policy artifact missing")
    require(sol_drop_policy.get("future_build_drop_exact_duplicate_extra_rows_count") == SOL_EXACT_DUPLICATE_ROWS_DROPPED, "SOL drop policy count mismatch")

    require(
        policy_summary.get("historical_data_acquisition_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_status")
        == "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_MATERIAL_DUPLICATE_CONFLICT_POLICY_APPROVED_POLICY_CLEAN_BUILD_READY",
        "ETH material duplicate conflict policy status mismatch",
    )
    require(
        policy_summary.get("next_module")
        == "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_after_eth_material_conflict_policy_v1.py",
        "ETH policy next_module mismatch",
    )
    require(policy_summary.get("target_symbol") == "ETH-USDT-SWAP", "policy target symbol mismatch")
    require(policy_summary.get("raw_eth_rows_scanned") == ETH_RAW_ROWS_BEFORE_POLICY, "policy raw ETH row count mismatch")
    require(policy_summary.get("raw_eth_duplicate_group_count") == 325, "policy duplicate group count mismatch")
    require(policy_summary.get("raw_eth_duplicate_extra_row_count") == 328, "policy duplicate extra row count mismatch")
    require(policy_summary.get("eth_exact_duplicate_group_count") == 324, "policy exact duplicate group count mismatch")
    require(policy_summary.get("eth_exact_duplicate_extra_rows_to_drop") == ETH_EXACT_DUPLICATE_ROWS_DROPPED, "policy exact duplicate drop count mismatch")
    require(policy_summary.get("eth_material_conflict_group_count") == 1, "policy material conflict group count mismatch")
    require(policy_summary.get("eth_material_conflict_rows_to_quarantine") == ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED, "policy material quarantine row count mismatch")
    require(policy_summary.get("eth_expected_clean_source_rows_after_policy") == ETH_CLEAN_SOURCE_ROWS_AFTER_POLICY, "policy ETH clean row count mismatch")
    require(policy_summary.get("eth_expected_complete_1h_rows_after_policy") == ETH_COMPLETE_1H_ROWS_AFTER_POLICY, "policy ETH complete row count mismatch")
    require(policy_summary.get("eth_expected_incomplete_1h_rows_after_policy") == ETH_INCOMPLETE_1H_ROWS_AFTER_POLICY, "policy ETH incomplete row count mismatch")
    require(policy_summary.get("eth_affected_hour_count_after_policy") == ETH_AFFECTED_HOUR_COUNT_AFTER_POLICY, "policy ETH affected hour count mismatch")
    require(policy_summary.get("policy_counts_complete") is True, "policy counts incomplete")
    require(policy_summary.get("additional_group_classification_required") is False, "additional group classification unexpectedly required")
    require(policy_summary.get("exact_duplicate_drop_allowed") is True, "policy exact duplicate drop approval missing")
    require(policy_summary.get("material_conflict_quarantine_required") is True, "material conflict quarantine requirement missing")
    require(policy_summary.get("approval_grants_future_10_symbol_eth_material_policy_clean_build_next") is True, "future ETH material policy-clean build approval missing")
    require(policy_summary.get("active_p0_blocker_count") == 0, "policy P0 count mismatch")
    require(policy_summary.get("replacement_checks_all_true") is True, "policy replacement checks not all true")
    for key in [
        "choose_conflicting_row_allowed",
        "average_conflicting_rows_allowed",
        "merge_conflicting_rows_allowed",
        "ohlcv_modification_allowed",
        "data_build_performed",
        "aggregation_performed_now",
        "output_csv_created",
        "output_valid_for_research_backtest",
        "output_valid_for_edge_claim",
        "safe_for_full_universe_acquisition",
        "broad_acquisition_ready",
    ]:
        require(policy_summary.get(key) is False, f"policy {key} must be false")

    require(material_policy.get("material_conflict_policy_created") is True, "material policy missing")
    require(material_policy.get("choose_conflicting_row_allowed") is False, "conflicting row choice unexpectedly allowed")
    require(material_policy.get("average_conflicting_rows_allowed") is False, "averaging unexpectedly allowed")
    require(material_policy.get("merge_conflicting_rows_allowed") is False, "merge unexpectedly allowed")
    require(material_policy.get("ohlcv_modification_allowed") is False, "OHLCV modification unexpectedly allowed")
    require(policy_counts.get("eth_duplicate_group_policy_counts_created") is True, "policy count artifact missing")
    require(policy_counts.get("eth_exact_duplicate_extra_rows_to_drop") == ETH_EXACT_DUPLICATE_ROWS_DROPPED, "policy count exact drop mismatch")
    require(policy_counts.get("eth_material_conflict_rows_to_quarantine") == ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED, "policy count quarantine mismatch")
    require(quarantine_policy.get("eth_material_conflict_quarantine_policy_created") is True, "quarantine policy missing")
    require(len(quarantine_policy.get("material_conflict_groups", [])) == 1, "material conflict group detail mismatch")
    require(raw_group_report.get("eth_residual_duplicate_raw_group_report_created") is True, "residual raw group report missing")
    require(len(raw_group_report.get("duplicate_groups", [])) == 325, "residual raw group report count mismatch")
    require(build_preview.get("policy_clean_build_preview_created") is True, "policy-clean build preview missing")
    require(build_preview.get("future_build_may_reuse_btc_policy_clean_output_after_revalidation") is True, "build preview BTC reuse requirement missing")
    require(build_preview.get("future_build_must_apply_eth_material_duplicate_policy") is True, "build preview ETH material policy requirement missing")
    require(build_preview.get("future_build_must_apply_sol_exact_duplicate_policy") is True, "build preview SOL exact policy requirement missing")
    require(build_preview.get("future_build_fail_closed_on_new_material_conflicts") is True, "build preview fail-closed rule missing")
    require(build_approval.get("approval_grants_future_10_symbol_policy_clean_build_next") is True, "build approval missing")
    for key in [
        "approval_grants_rebuild_now",
        "approval_grants_download_now",
        "approval_grants_api_now",
        "approval_grants_browse_now",
        "approval_grants_research_backtest_edge_now",
    ]:
        require(build_approval.get(key) is False, f"build approval {key} must be false")

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


def build_eth_policy_maps(raw_group_report: dict[str, Any]) -> dict[str, Any]:
    exact_groups: dict[int, dict[str, Any]] = {}
    material_groups: dict[int, dict[str, Any]] = {}
    for group in raw_group_report.get("duplicate_groups", []):
        open_time = int(group["open_time"])
        if bool(group.get("exact_duplicate_group")):
            exact_groups[open_time] = group
        else:
            material_groups[open_time] = group
    require(len(exact_groups) == 324, "ETH exact duplicate group map count mismatch")
    require(len(material_groups) == 1, "ETH material conflict group map count mismatch")
    require(sum(int(group["group_size"]) - 1 for group in exact_groups.values()) == ETH_EXACT_DUPLICATE_ROWS_DROPPED, "ETH exact duplicate extra row policy mismatch")
    require(sum(int(group["group_size"]) for group in material_groups.values()) == ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED, "ETH material conflict quarantine policy mismatch")
    return {
        "exact_groups": exact_groups,
        "material_groups": material_groups,
        "material_affected_hours": {
            (open_time // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS for open_time in material_groups
        },
    }


def raw_row_to_minute(
    symbol: str,
    raw_row: dict[str, str],
    open_time: int,
    digest: str,
    inner_csv: str,
    day: str,
    row_number: int,
) -> dict[str, Any]:
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
    return {
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


def process_new_symbol(
    symbol: str,
    records: list[dict[str, Any]],
    eth_policy_maps: dict[str, Any],
    sol_policy_maps: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    output_path = output_path_for_symbol(symbol)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source_rows_before_policy = 0
    clean_source_rows = 0
    output_rows = 0
    complete_rows = 0
    incomplete_rows = 0
    duplicate_count = 0
    missing_count = 0
    schema_mismatches = 0
    symbol_mismatches = 0
    eth_exact_duplicate_rows_dropped = 0
    eth_material_conflict_rows_quarantined = 0
    sol_exact_duplicate_rows_dropped = 0
    previous_group_open_time: int | None = None
    current_hour: HourAggregate | None = None
    current_group: list[dict[str, Any]] = []
    file_reports: list[dict[str, Any]] = []
    schema_reports: list[dict[str, Any]] = []
    drop_audit: list[dict[str, Any]] = []
    quarantine_audit: list[dict[str, Any]] = []
    exact_groups = eth_policy_maps["exact_groups"] if symbol == "ETH-USDT-SWAP" else {}
    material_groups = eth_policy_maps["material_groups"] if symbol == "ETH-USDT-SWAP" else {}
    material_affected_hours = eth_policy_maps["material_affected_hours"] if symbol == "ETH-USDT-SWAP" else set()
    sol_exact_groups = sol_policy_maps["exact_groups"] if symbol == "SOL-USDT-SWAP" else {}

    def write_hour(agg: HourAggregate) -> None:
        nonlocal output_rows, complete_rows, incomplete_rows
        allow_incomplete = symbol == "ETH-USDT-SWAP" and agg.hour_start in material_affected_hours
        reason = "ETH_MATERIAL_CONFLICT_GROUP_QUARANTINED" if allow_incomplete else ""
        out_row = aggregate_to_row(agg, allow_incomplete=allow_incomplete, incomplete_reason=reason)
        writer.writerow(out_row)
        output_rows += 1
        GLOBAL_STATE["output_1h_row_count"] = int(GLOBAL_STATE["output_1h_row_count"]) + 1
        if out_row["complete_hour"] == "true":
            complete_rows += 1
            GLOBAL_STATE["complete_1h_row_count"] = int(GLOBAL_STATE["complete_1h_row_count"]) + 1
        else:
            incomplete_rows += 1
            GLOBAL_STATE["incomplete_1h_row_count"] = int(GLOBAL_STATE["incomplete_1h_row_count"]) + 1

    def accept_clean_row(group_row: dict[str, Any]) -> None:
        nonlocal current_hour, clean_source_rows
        minute_row = raw_row_to_minute(
            symbol,
            group_row["raw_row"],
            group_row["open_time"],
            group_row["source_zip_sha256"],
            group_row["source_csv_file"],
            group_row["source_date"],
            group_row["row_number"],
        )
        hour_start = (minute_row["open_time"] // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS
        if current_hour is None:
            current_hour = new_hour(symbol, minute_row)
        elif hour_start == current_hour.hour_start:
            update_hour(current_hour, minute_row)
        else:
            write_hour(current_hour)
            current_hour = new_hour(symbol, minute_row)
        clean_source_rows += 1
        GLOBAL_STATE["clean_new_symbol_source_rows_after_policy"] = (
            int(GLOBAL_STATE["clean_new_symbol_source_rows_after_policy"]) + 1
        )

    def flush_group() -> None:
        nonlocal duplicate_count, eth_exact_duplicate_rows_dropped, eth_material_conflict_rows_quarantined
        nonlocal sol_exact_duplicate_rows_dropped
        if not current_group:
            return
        open_time = int(current_group[0]["open_time"])
        group_size = len(current_group)
        normalized_rows = [row["normalized_row"] for row in current_group]
        exact_group = all(row == normalized_rows[0] for row in normalized_rows)
        if group_size == 1:
            require(open_time not in material_groups, f"ETH material conflict group missing duplicate rows {open_time}")
            accept_clean_row(current_group[0])
            return
        if symbol == "SOL-USDT-SWAP" and open_time in sol_exact_groups:
            policy_group = sol_exact_groups[open_time]
            require(group_size == int(policy_group["group_size"]), f"SOL exact group size mismatch {open_time}")
            require(exact_group, f"SOL exact duplicate group has differing fields {open_time}")
            accept_clean_row(current_group[0])
            for dropped in current_group[1:]:
                sol_exact_duplicate_rows_dropped += 1
                GLOBAL_STATE["sol_exact_duplicate_rows_dropped"] = int(GLOBAL_STATE["sol_exact_duplicate_rows_dropped"]) + 1
                drop_audit.append(
                    {
                        "target_symbol": symbol,
                        "duplicate_open_time": open_time,
                        "duplicate_open_time_utc": iso_utc_from_ms(open_time),
                        "source_date": dropped["source_date"],
                        "source_file": dropped["source_csv_file"],
                        "source_zip_path": dropped["source_zip_path"],
                        "source_zip_sha256": dropped["source_zip_sha256"],
                        "dropped_row_number": dropped["row_number"],
                        "kept_canonical_row": current_group[0]["audit_row"],
                        "dropped_raw_row": dropped["audit_row"]["raw_row"],
                        "drop_reason": "APPROVED_SOL_EXACT_DUPLICATE_EXTRA_ROW",
                    }
                )
                GLOBAL_STATE["sol_drop_audit_rows"] = list(GLOBAL_STATE["sol_drop_audit_rows"]) + [drop_audit[-1]]
            return
        if symbol != "ETH-USDT-SWAP":
            duplicate_count += group_size - 1
            GLOBAL_STATE["duplicate_open_time_count_total"] = int(GLOBAL_STATE["duplicate_open_time_count_total"]) + group_size - 1
            GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
            raise BuildBlocked(f"{symbol} duplicate open_time {open_time}")
        if open_time in material_groups:
            policy_group = material_groups[open_time]
            require(group_size == int(policy_group["group_size"]), f"ETH material group size mismatch {open_time}")
            require(not exact_group, f"ETH material group unexpectedly exact {open_time}")
            eth_material_conflict_rows_quarantined += group_size
            GLOBAL_STATE["eth_material_conflict_rows_quarantined"] = int(GLOBAL_STATE["eth_material_conflict_rows_quarantined"]) + group_size
            quarantine_audit.append(
                {
                    "target_symbol": symbol,
                    "material_conflict_open_time": open_time,
                    "material_conflict_open_time_utc": iso_utc_from_ms(open_time),
                    "group_size": group_size,
                    "quarantined_row_count": group_size,
                    "differing_field_count": policy_group.get("differing_field_count"),
                    "differing_fields": policy_group.get("differing_fields", []),
                    "quarantined_rows": [row["audit_row"] for row in current_group],
                    "quarantine_reason": "APPROVED_ETH_MATERIAL_DUPLICATE_CONFLICT_QUARANTINE_ALL_ROWS",
                }
            )
            GLOBAL_STATE["eth_quarantine_audit_rows"] = list(GLOBAL_STATE["eth_quarantine_audit_rows"]) + [quarantine_audit[-1]]
            return
        if open_time in exact_groups:
            policy_group = exact_groups[open_time]
            require(group_size == int(policy_group["group_size"]), f"ETH exact group size mismatch {open_time}")
            require(exact_group, f"ETH exact duplicate group has differing fields {open_time}")
            accept_clean_row(current_group[0])
            for dropped in current_group[1:]:
                eth_exact_duplicate_rows_dropped += 1
                GLOBAL_STATE["eth_exact_duplicate_rows_dropped"] = int(GLOBAL_STATE["eth_exact_duplicate_rows_dropped"]) + 1
                drop_audit.append(
                    {
                        "target_symbol": symbol,
                        "duplicate_open_time": open_time,
                        "duplicate_open_time_utc": iso_utc_from_ms(open_time),
                        "source_date": dropped["source_date"],
                        "source_file": dropped["source_csv_file"],
                        "source_zip_path": dropped["source_zip_path"],
                        "source_zip_sha256": dropped["source_zip_sha256"],
                        "dropped_row_number": dropped["row_number"],
                        "kept_canonical_row": current_group[0]["audit_row"],
                        "dropped_raw_row": dropped["audit_row"]["raw_row"],
                        "drop_reason": "APPROVED_ETH_EXACT_DUPLICATE_EXTRA_ROW",
                    }
                )
                GLOBAL_STATE["eth_drop_audit_rows"] = list(GLOBAL_STATE["eth_drop_audit_rows"]) + [drop_audit[-1]]
            return
        GLOBAL_STATE["duplicate_open_time_count_total"] = int(GLOBAL_STATE["duplicate_open_time_count_total"]) + group_size - 1
        GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
        raise BuildBlocked(f"ETH unapproved duplicate open_time {open_time}")

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
            raw_file_row_count = 0
            clean_file_row_count = 0
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
                        raw_file_row_count += 1
                        source_rows_before_policy += 1
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
                        if previous_group_open_time is not None and open_time != previous_group_open_time:
                            delta = open_time - previous_group_open_time
                            if delta <= 0:
                                GLOBAL_STATE["duplicate_open_time_count_total"] = int(GLOBAL_STATE["duplicate_open_time_count_total"]) + 1
                                GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
                                raise BuildBlocked(f"{symbol} non-monotonic open_time {open_time}")
                            if delta != EXPECTED_MINUTE_MS:
                                missing_count += max(0, (delta // EXPECTED_MINUTE_MS) - 1)
                                GLOBAL_STATE["missing_minute_count_total"] = int(GLOBAL_STATE["missing_minute_count_total"]) + max(1, missing_count)
                                GLOBAL_STATE["anomaly_symbols"] = sorted(set(GLOBAL_STATE["anomaly_symbols"]) | {symbol})
                                raise BuildBlocked(f"{symbol} missing raw minute gap after {previous_group_open_time}: delta={delta}")
                            flush_group()
                            current_group = []
                        previous_group_open_time = open_time
                        first_file_open_time = open_time if first_file_open_time is None else first_file_open_time
                        last_file_open_time = open_time
                        current_group.append(
                            {
                                "raw_row": {field: raw_row.get(field) for field in EXPECTED_INPUT_SCHEMA},
                                "normalized_row": normalized_input_row(raw_row),
                                "audit_row": {
                                    "source_date": day,
                                    "source_file": inner_csv,
                                    "source_zip_path": str(path),
                                    "source_zip_sha256": digest,
                                    "row_number": row_number,
                                    "raw_row": {field: raw_row.get(field) for field in EXPECTED_INPUT_SCHEMA},
                                    "normalized_row": normalized_input_row(raw_row),
                                },
                            "open_time": open_time,
                            "source_zip_sha256": digest,
                                "source_zip_path": str(path),
                            "source_csv_file": inner_csv,
                            "source_date": day,
                                "row_number": row_number,
                            }
                        )
                        clean_file_row_count = clean_source_rows
            expected_raw_rows = (
                1441
                if (symbol == "SOL-USDT-SWAP" and day == SOL_DUPLICATE_SOURCE_DATE)
                else 1440
            )
            if symbol != "ETH-USDT-SWAP":
                require(raw_file_row_count == expected_raw_rows, f"{symbol} raw source row count mismatch {inner_csv}: {raw_file_row_count}")
            file_reports.append(
                {
                    "symbol": symbol,
                    "date": day,
                    "source_zip_path": str(path),
                    "source_zip_sha256": digest,
                    "source_csv_file": inner_csv,
                    "source_row_count_before_policy": raw_file_row_count,
                    "clean_source_row_count_after_policy_running_total": clean_file_row_count,
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
        flush_group()
        if current_hour is not None:
            write_hour(current_hour)

    output_hash = sha256_file(output_path)
    GLOBAL_STATE["new_symbol_build_count"] = int(GLOBAL_STATE["new_symbol_build_count"]) + 1
    GLOBAL_STATE["output_csv_created"] = True
    expected_before_policy = (
        ETH_RAW_ROWS_BEFORE_POLICY
        if symbol == "ETH-USDT-SWAP"
        else SOL_CLEAN_SOURCE_ROWS_AFTER_POLICY + SOL_EXACT_DUPLICATE_ROWS_DROPPED
        if symbol == "SOL-USDT-SWAP"
        else NOMINAL_SOURCE_ROWS_PER_SYMBOL
    )
    expected_clean_source_rows = (
        ETH_CLEAN_SOURCE_ROWS_AFTER_POLICY
        if symbol == "ETH-USDT-SWAP"
        else SOL_CLEAN_SOURCE_ROWS_AFTER_POLICY
        if symbol == "SOL-USDT-SWAP"
        else NOMINAL_SOURCE_ROWS_PER_SYMBOL
    )
    expected_complete_rows = (
        ETH_COMPLETE_1H_ROWS_AFTER_POLICY
        if symbol == "ETH-USDT-SWAP"
        else SOL_COMPLETE_1H_ROWS_AFTER_POLICY
        if symbol == "SOL-USDT-SWAP"
        else NOMINAL_OUTPUT_ROWS_PER_SYMBOL
    )
    expected_incomplete_rows = ETH_INCOMPLETE_1H_ROWS_AFTER_POLICY if symbol == "ETH-USDT-SWAP" else 0
    require(source_rows_before_policy == expected_before_policy, f"{symbol} source row count before policy mismatch: {source_rows_before_policy}")
    require(clean_source_rows == expected_clean_source_rows, f"{symbol} clean source row count mismatch: {clean_source_rows}")
    require(output_rows == NOMINAL_OUTPUT_ROWS_PER_SYMBOL, f"{symbol} output row count mismatch: {output_rows}")
    require(complete_rows == expected_complete_rows, f"{symbol} complete output row count mismatch: {complete_rows}")
    require(incomplete_rows == expected_incomplete_rows, f"{symbol} incomplete output row count mismatch: {incomplete_rows}")
    if symbol == "ETH-USDT-SWAP":
        require(eth_exact_duplicate_rows_dropped == ETH_EXACT_DUPLICATE_ROWS_DROPPED, "ETH exact duplicate drop count mismatch")
        require(eth_material_conflict_rows_quarantined == ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED, "ETH material conflict quarantine count mismatch")
        require(sol_exact_duplicate_rows_dropped == 0, "ETH unexpectedly applied SOL duplicate policy")
        GLOBAL_STATE["eth_clean_source_rows_after_policy"] = clean_source_rows
        GLOBAL_STATE["eth_complete_1h_row_count"] = complete_rows
        GLOBAL_STATE["eth_incomplete_1h_row_count"] = incomplete_rows
    elif symbol == "SOL-USDT-SWAP":
        require(sol_exact_duplicate_rows_dropped == SOL_EXACT_DUPLICATE_ROWS_DROPPED, "SOL exact duplicate drop count mismatch")
        require(eth_exact_duplicate_rows_dropped == 0, "SOL unexpectedly applied ETH exact duplicate policy")
        require(eth_material_conflict_rows_quarantined == 0, "SOL unexpected quarantine")
        GLOBAL_STATE["sol_clean_source_rows_after_policy"] = clean_source_rows
        GLOBAL_STATE["sol_complete_1h_row_count"] = complete_rows
        GLOBAL_STATE["sol_incomplete_1h_row_count"] = incomplete_rows
    else:
        require(eth_exact_duplicate_rows_dropped == 0, f"{symbol} unexpected exact duplicate drop")
        require(eth_material_conflict_rows_quarantined == 0, f"{symbol} unexpected quarantine")
        require(sol_exact_duplicate_rows_dropped == 0, f"{symbol} unexpected SOL duplicate drop")
    return (
        {
            "symbol": symbol,
            "source_row_count_before_policy": source_rows_before_policy,
            "clean_source_row_count_after_policy": clean_source_rows,
            "output_1h_row_count": output_rows,
            "complete_1h_row_count": complete_rows,
            "incomplete_1h_row_count": incomplete_rows,
            "duplicate_open_time_count": duplicate_count,
            "missing_minute_count": missing_count,
            "schema_mismatch_count": schema_mismatches,
            "symbol_mismatch_count": symbol_mismatches,
            "eth_exact_duplicate_rows_dropped": eth_exact_duplicate_rows_dropped,
            "eth_material_conflict_rows_quarantined": eth_material_conflict_rows_quarantined,
            "sol_exact_duplicate_rows_dropped": sol_exact_duplicate_rows_dropped,
            "sol_material_conflict_rows_quarantined": 0,
            "output_csv_path": str(output_path),
            "output_csv_sha256": output_hash,
            "output_csv_created": True,
        },
        file_reports,
        schema_reports,
        drop_audit,
        quarantine_audit,
    )


def write_reports(payloads: dict[str, Any]) -> None:
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_execution_report.json", payloads["execution_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_1h_output_manifest.json", payloads["output_manifest"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_audit.json", payloads["eth_drop_audit"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_eth_material_conflict_quarantine_audit.json", payloads["eth_quarantine_audit"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_sol_exact_duplicate_drop_audit.json", payloads["sol_drop_audit"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_gap_duplicate_report.json", payloads["gap_duplicate_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_schema_validation_report.json", payloads["schema_validation_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_output_provenance_report.json", payloads["output_provenance_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_execution_compliance_report.json", payloads["compliance_report"])
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_execution_summary.json", payloads["summary"])


def main() -> None:
    generated_at = utc_now()
    sol_policy_summary = load_json(SOL_POLICY_SUMMARY)
    sol_exact_policy = load_json(SOL_EXACT_POLICY)
    sol_drop_policy = load_json(SOL_EXACT_DROP_POLICY)
    policy_summary = load_json(ETH_POLICY_SUMMARY)
    material_policy = load_json(ETH_MATERIAL_POLICY)
    policy_counts = load_json(ETH_POLICY_COUNTS)
    quarantine_policy = load_json(ETH_QUARANTINE_POLICY)
    raw_group_report = load_json(ETH_RESIDUAL_RAW_GROUP_REPORT)
    build_preview = load_json(POLICY_CLEAN_BUILD_PREVIEW)
    build_approval = load_json(POLICY_CLEAN_BUILD_APPROVAL)
    download_summary = load_json(DOWNLOAD_VALIDATOR_SUMMARY)
    hash_report = load_json(DOWNLOAD_HASH_REPORT)
    btc_summary = load_json(BTC_POLICY_CLEAN_SUMMARY)
    btc_validator = load_json(BTC_POLICY_VALIDATOR_SUMMARY)
    btc_output_validation = load_json(BTC_POLICY_OUTPUT_VALIDATION)
    validate_preflight(
        sol_policy_summary,
        sol_exact_policy,
        sol_drop_policy,
        policy_summary,
        material_policy,
        policy_counts,
        quarantine_policy,
        raw_group_report,
        build_preview,
        build_approval,
        download_summary,
        btc_validator,
    )
    eth_policy_maps = build_eth_policy_maps(raw_group_report)
    sol_policy_maps = {
        "exact_groups": {
            SOL_DUPLICATE_OPEN_TIME: {
                "group_size": 2,
                "duplicate_extra_rows": SOL_EXACT_DUPLICATE_ROWS_DROPPED,
            }
        }
    }
    by_symbol = load_hash_records(hash_report)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    btc_reuse = revalidate_btc_policy_clean(by_symbol[BTC_SYMBOL], btc_summary, btc_output_validation)

    symbol_results: list[dict[str, Any]] = [btc_reuse]
    source_file_reports: list[dict[str, Any]] = []
    schema_reports: list[dict[str, Any]] = []
    eth_drop_audit_rows: list[dict[str, Any]] = []
    eth_quarantine_audit_rows: list[dict[str, Any]] = []
    sol_drop_audit_rows: list[dict[str, Any]] = []
    for symbol in NEW_SYMBOLS:
        result, files, schemas, drops, quarantines = process_new_symbol(symbol, by_symbol[symbol], eth_policy_maps, sol_policy_maps)
        symbol_results.append(result)
        source_file_reports.extend(files)
        schema_reports.extend(schemas)
        if symbol == "SOL-USDT-SWAP":
            sol_drop_audit_rows.extend(drops)
        else:
            eth_drop_audit_rows.extend(drops)
        eth_quarantine_audit_rows.extend(quarantines)

    observed_new_symbol_source_rows_before_policy = sum(int(row["source_row_count_before_policy"]) for row in symbol_results if row["symbol"] != BTC_SYMBOL)
    clean_new_symbol_source_rows_after_policy = sum(int(row["clean_source_row_count_after_policy"]) for row in symbol_results if row["symbol"] != BTC_SYMBOL)
    eth_exact_duplicate_rows_dropped = sum(int(row.get("eth_exact_duplicate_rows_dropped", 0)) for row in symbol_results if row["symbol"] != BTC_SYMBOL)
    eth_material_conflict_rows_quarantined = sum(int(row.get("eth_material_conflict_rows_quarantined", 0)) for row in symbol_results if row["symbol"] != BTC_SYMBOL)
    sol_exact_duplicate_rows_dropped = sum(int(row.get("sol_exact_duplicate_rows_dropped", 0)) for row in symbol_results if row["symbol"] != BTC_SYMBOL)
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
    require(observed_new_symbol_source_rows_before_policy == EXPECTED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY, "new symbol source row count before policy mismatch")
    require(clean_new_symbol_source_rows_after_policy == EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY, "clean new symbol source row count after policy mismatch")
    require(eth_exact_duplicate_rows_dropped == ETH_EXACT_DUPLICATE_ROWS_DROPPED, "ETH exact duplicate rows dropped mismatch")
    require(eth_material_conflict_rows_quarantined == ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED, "ETH material conflict rows quarantined mismatch")
    require(len(eth_drop_audit_rows) == ETH_EXACT_DUPLICATE_ROWS_DROPPED, "ETH drop audit row count mismatch")
    require(len(eth_quarantine_audit_rows) == ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED // 2, "ETH quarantine audit group count mismatch")
    require(sol_exact_duplicate_rows_dropped == SOL_EXACT_DUPLICATE_ROWS_DROPPED, "SOL exact duplicate rows dropped mismatch")
    require(len(sol_drop_audit_rows) == SOL_EXACT_DUPLICATE_ROWS_DROPPED, "SOL drop audit row count mismatch")
    require(output_1h_row_count == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS, "pilot output row count mismatch")
    require(complete_1h_row_count == EXPECTED_TOTAL_COMPLETE_1H_ROWS_AFTER_POLICY, "complete 1h row count mismatch")
    require(incomplete_1h_row_count == EXPECTED_TOTAL_INCOMPLETE_1H_ROWS_AFTER_POLICY, "incomplete 1h row count mismatch")

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
        "output_is_pilot_policy_clean_pipeline_validation_only": True,
    }
    GLOBAL_STATE["new_symbol_build_count"] = len(NEW_SYMBOLS)
    GLOBAL_STATE["observed_new_symbol_source_rows"] = observed_new_symbol_source_rows_before_policy
    GLOBAL_STATE["clean_new_symbol_source_rows_after_policy"] = clean_new_symbol_source_rows_after_policy
    GLOBAL_STATE["eth_exact_duplicate_rows_dropped"] = eth_exact_duplicate_rows_dropped
    GLOBAL_STATE["sol_exact_duplicate_rows_dropped"] = sol_exact_duplicate_rows_dropped
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
        "eth_exact_duplicate_rows_dropped": eth_exact_duplicate_rows_dropped,
        "eth_material_conflict_rows_quarantined": eth_material_conflict_rows_quarantined,
        "sol_exact_duplicate_rows_dropped": sol_exact_duplicate_rows_dropped,
        "sol_material_conflict_rows_quarantined": 0,
        "eth_affected_hour_count_after_policy": ETH_AFFECTED_HOUR_COUNT_AFTER_POLICY,
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
        "observed_new_symbol_source_rows_before_policy": observed_new_symbol_source_rows_before_policy,
        "clean_new_symbol_source_rows_after_policy": clean_new_symbol_source_rows_after_policy,
        "eth_exact_duplicate_rows_dropped": eth_exact_duplicate_rows_dropped,
        "eth_material_conflict_rows_quarantined": eth_material_conflict_rows_quarantined,
        "eth_clean_source_rows_after_policy": ETH_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "eth_complete_1h_row_count": ETH_COMPLETE_1H_ROWS_AFTER_POLICY,
        "eth_incomplete_1h_row_count": ETH_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "sol_exact_duplicate_rows_dropped": sol_exact_duplicate_rows_dropped,
        "sol_material_conflict_rows_quarantined": 0,
        "sol_clean_source_rows_after_policy": SOL_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "sol_complete_1h_row_count": SOL_COMPLETE_1H_ROWS_AFTER_POLICY,
        "sol_incomplete_1h_row_count": SOL_INCOMPLETE_1H_ROWS_AFTER_POLICY,
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
        "output_is_pilot_policy_clean_pipeline_validation_only": True,
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
        "eth_exact_duplicate_policy_valid": True,
        "download_validator_valid": True,
        "file_count_total_10530": EXPECTED_TOTAL_PILOT_FILE_COUNT == sum(len(by_symbol[s]) for s in PILOT_SYMBOLS),
        "btc_policy_clean_reused": btc_reuse["btc_policy_clean_reused"],
        "btc_policy_clean_revalidated": btc_reuse["btc_policy_clean_revalidated"],
        "new_symbol_build_count_9": len([row for row in symbol_results if row["symbol"] != BTC_SYMBOL]) == 9,
        "new_symbol_source_rows_before_policy_expected": observed_new_symbol_source_rows_before_policy == EXPECTED_NEW_SYMBOL_SOURCE_ROWS_BEFORE_POLICY,
        "clean_new_symbol_source_rows_after_policy_expected": clean_new_symbol_source_rows_after_policy == EXPECTED_CLEAN_NEW_SYMBOL_SOURCE_ROWS_AFTER_POLICY,
        "eth_exact_duplicate_rows_dropped_expected": eth_exact_duplicate_rows_dropped == ETH_EXACT_DUPLICATE_ROWS_DROPPED,
        "eth_material_conflict_rows_quarantined_expected": eth_material_conflict_rows_quarantined == ETH_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "sol_exact_duplicate_rows_dropped_expected": sol_exact_duplicate_rows_dropped == SOL_EXACT_DUPLICATE_ROWS_DROPPED,
        "sol_clean_source_rows_expected": any(
            row["symbol"] == "SOL-USDT-SWAP"
            and row["clean_source_row_count_after_policy"] == SOL_CLEAN_SOURCE_ROWS_AFTER_POLICY
            and row["complete_1h_row_count"] == SOL_COMPLETE_1H_ROWS_AFTER_POLICY
            and row["incomplete_1h_row_count"] == SOL_INCOMPLETE_1H_ROWS_AFTER_POLICY
            for row in symbol_results
        ),
        "output_rows_expected": output_1h_row_count == NOMINAL_TOTAL_PILOT_OUTPUT_ROWS,
        "complete_rows_expected": complete_1h_row_count == EXPECTED_TOTAL_COMPLETE_1H_ROWS_AFTER_POLICY,
        "incomplete_rows_expected": incomplete_1h_row_count == EXPECTED_TOTAL_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "no_new_symbol_anomaly": not new_symbol_anomaly_detected,
        "no_unapproved_duplicate_open_times": duplicate_open_time_count_total == 0,
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
        "historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_status": PASS_STATUS,
        "policy_clean_build_execution_performed": True,
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
        "observed_new_symbol_source_rows_before_policy": observed_new_symbol_source_rows_before_policy,
        "eth_exact_duplicate_rows_dropped": eth_exact_duplicate_rows_dropped,
        "eth_material_conflict_rows_quarantined": eth_material_conflict_rows_quarantined,
        "eth_clean_source_rows_after_policy": ETH_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "eth_complete_1h_row_count": ETH_COMPLETE_1H_ROWS_AFTER_POLICY,
        "eth_incomplete_1h_row_count": ETH_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "sol_exact_duplicate_rows_dropped": sol_exact_duplicate_rows_dropped,
        "sol_material_conflict_rows_quarantined": 0,
        "sol_clean_source_rows_after_policy": SOL_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "sol_complete_1h_row_count": SOL_COMPLETE_1H_ROWS_AFTER_POLICY,
        "sol_incomplete_1h_row_count": SOL_INCOMPLETE_1H_ROWS_AFTER_POLICY,
        "clean_new_symbol_source_rows_after_policy": clean_new_symbol_source_rows_after_policy,
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
        "output_is_pilot_policy_clean_pipeline_validation_only": True,
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
    eth_drop_audit = {
        "eth_exact_duplicate_drop_audit_created": True,
        "target_symbol": "ETH-USDT-SWAP",
        "duplicate_open_time": ETH_DUPLICATE_OPEN_TIME,
        "duplicate_open_time_utc": ETH_DUPLICATE_OPEN_TIME_UTC,
        "duplicate_source_date": ETH_DUPLICATE_SOURCE_DATE,
        "duplicate_source_file": ETH_DUPLICATE_SOURCE_FILE,
        "eth_exact_duplicate_rows_dropped": eth_exact_duplicate_rows_dropped,
        "dropped_rows": eth_drop_audit_rows,
        "drop_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROW_KEEP_ONE_CANONICAL_ROW",
        "ohlcv_modification_performed": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
    }
    eth_quarantine_audit = {
        "eth_material_conflict_quarantine_audit_created": True,
        "target_symbol": "ETH-USDT-SWAP",
        "eth_material_conflict_rows_quarantined": eth_material_conflict_rows_quarantined,
        "eth_material_conflict_group_count": len(eth_quarantine_audit_rows),
        "quarantined_groups": eth_quarantine_audit_rows,
        "quarantine_policy": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_DUPLICATE_GROUP",
        "choose_conflicting_row_allowed": False,
        "average_conflicting_rows_allowed": False,
        "merge_conflicting_rows_allowed": False,
        "ohlcv_modification_performed": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
    }
    sol_drop_audit = {
        "sol_exact_duplicate_drop_audit_created": True,
        "target_symbol": "SOL-USDT-SWAP",
        "duplicate_open_time": SOL_DUPLICATE_OPEN_TIME,
        "duplicate_open_time_utc": SOL_DUPLICATE_OPEN_TIME_UTC,
        "duplicate_source_date": SOL_DUPLICATE_SOURCE_DATE,
        "duplicate_source_file": SOL_DUPLICATE_SOURCE_FILE,
        "sol_exact_duplicate_rows_dropped": sol_exact_duplicate_rows_dropped,
        "dropped_rows": sol_drop_audit_rows,
        "drop_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROW_KEEP_ONE_CANONICAL_ROW",
        "ohlcv_modification_performed": False,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
    }
    payloads = {
        "execution_report": execution_report,
        "output_manifest": output_manifest,
        "eth_drop_audit": eth_drop_audit,
        "eth_quarantine_audit": eth_quarantine_audit,
        "sol_drop_audit": sol_drop_audit,
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
            "historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_execution_status": BLOCKED_STATUS,
            "policy_clean_build_execution_performed": False,
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
            "observed_new_symbol_source_rows_before_policy": int(GLOBAL_STATE["observed_new_symbol_source_rows"]),
            "eth_exact_duplicate_rows_dropped": int(GLOBAL_STATE["eth_exact_duplicate_rows_dropped"]),
            "eth_material_conflict_rows_quarantined": int(GLOBAL_STATE["eth_material_conflict_rows_quarantined"]),
            "eth_clean_source_rows_after_policy": int(GLOBAL_STATE["eth_clean_source_rows_after_policy"]),
            "eth_complete_1h_row_count": int(GLOBAL_STATE["eth_complete_1h_row_count"]),
            "eth_incomplete_1h_row_count": int(GLOBAL_STATE["eth_incomplete_1h_row_count"]),
            "sol_exact_duplicate_rows_dropped": int(GLOBAL_STATE["sol_exact_duplicate_rows_dropped"]),
            "sol_clean_source_rows_after_policy": int(GLOBAL_STATE["sol_clean_source_rows_after_policy"]),
            "sol_complete_1h_row_count": int(GLOBAL_STATE["sol_complete_1h_row_count"]),
            "sol_incomplete_1h_row_count": int(GLOBAL_STATE["sol_incomplete_1h_row_count"]),
            "clean_new_symbol_source_rows_after_policy": int(GLOBAL_STATE["clean_new_symbol_source_rows_after_policy"]),
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
            "output_is_pilot_policy_clean_pipeline_validation_only": True,
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
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_execution_report.json",
            {**summary, "blocked_reason": str(exc)},
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_1h_output_manifest.json",
            {
                "output_manifest_created": False,
                "blocked_before_complete_manifest": True,
                "anomaly_symbols": anomaly_symbols,
                "btc_policy_clean_reused": bool(GLOBAL_STATE["btc_policy_clean_reused"]),
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_gap_duplicate_report.json",
            {
                "gap_duplicate_report_created": True,
                "new_symbol_anomaly_detected": True,
                "anomaly_symbol_count": len(anomaly_symbols),
                "anomaly_symbols": anomaly_symbols,
                "duplicate_open_time_count_total": int(GLOBAL_STATE["duplicate_open_time_count_total"]),
                "eth_exact_duplicate_rows_dropped": int(GLOBAL_STATE["eth_exact_duplicate_rows_dropped"]),
                "eth_material_conflict_rows_quarantined": int(GLOBAL_STATE["eth_material_conflict_rows_quarantined"]),
                "sol_exact_duplicate_rows_dropped": int(GLOBAL_STATE["sol_exact_duplicate_rows_dropped"]),
                "missing_minute_count_total": int(GLOBAL_STATE["missing_minute_count_total"]),
                "blocked_reason": str(exc),
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_audit.json",
            {
                "eth_exact_duplicate_drop_audit_created": True,
                "target_symbol": "ETH-USDT-SWAP",
                "duplicate_open_time": ETH_DUPLICATE_OPEN_TIME,
                "duplicate_open_time_utc": ETH_DUPLICATE_OPEN_TIME_UTC,
                "duplicate_source_date": ETH_DUPLICATE_SOURCE_DATE,
                "duplicate_source_file": ETH_DUPLICATE_SOURCE_FILE,
                "eth_exact_duplicate_rows_dropped": int(GLOBAL_STATE["eth_exact_duplicate_rows_dropped"]),
                "dropped_rows": list(GLOBAL_STATE["eth_drop_audit_rows"]),
                "blocked_after_approved_drop": True,
                "blocked_reason": str(exc),
                "synthetic_fill_used": False,
                "forward_fill_used": False,
                "backfill_used": False,
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_eth_material_conflict_quarantine_audit.json",
            {
                "eth_material_conflict_quarantine_audit_created": True,
                "target_symbol": "ETH-USDT-SWAP",
                "eth_material_conflict_rows_quarantined": int(GLOBAL_STATE["eth_material_conflict_rows_quarantined"]),
                "quarantined_groups": list(GLOBAL_STATE["eth_quarantine_audit_rows"]),
                "blocked_after_approved_quarantine": True,
                "blocked_reason": str(exc),
                "choose_conflicting_row_allowed": False,
                "average_conflicting_rows_allowed": False,
                "merge_conflicting_rows_allowed": False,
                "ohlcv_modification_performed": False,
                "synthetic_fill_used": False,
                "forward_fill_used": False,
                "backfill_used": False,
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_sol_exact_duplicate_drop_audit.json",
            {
                "sol_exact_duplicate_drop_audit_created": True,
                "target_symbol": "SOL-USDT-SWAP",
                "duplicate_open_time": SOL_DUPLICATE_OPEN_TIME,
                "duplicate_open_time_utc": SOL_DUPLICATE_OPEN_TIME_UTC,
                "duplicate_source_date": SOL_DUPLICATE_SOURCE_DATE,
                "duplicate_source_file": SOL_DUPLICATE_SOURCE_FILE,
                "sol_exact_duplicate_rows_dropped": int(GLOBAL_STATE["sol_exact_duplicate_rows_dropped"]),
                "dropped_rows": list(GLOBAL_STATE["sol_drop_audit_rows"]),
                "blocked_after_approved_drop": True,
                "blocked_reason": str(exc),
                "ohlcv_modification_performed": False,
                "synthetic_fill_used": False,
                "forward_fill_used": False,
                "backfill_used": False,
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_schema_validation_report.json",
            {
                "schema_validation_report_created": True,
                "schema_mismatch_count": int(GLOBAL_STATE["schema_mismatch_count"]),
                "symbol_mismatch_count": int(GLOBAL_STATE["symbol_mismatch_count"]),
                "blocked_reason": str(exc),
            },
        )
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_output_provenance_report.json",
            {
                "output_provenance_report_created": True,
                "btc_policy_clean_reused": bool(GLOBAL_STATE["btc_policy_clean_reused"]),
                "btc_policy_clean_revalidated": bool(GLOBAL_STATE["btc_policy_clean_revalidated"]),
                "blocked_reason": str(exc),
            },
        )
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_execution_summary.json", summary)
        write_json(
            OUTPUT_DIR / "historical_okx_10_symbol_pilot_policy_clean_build_execution_compliance_report.json",
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
