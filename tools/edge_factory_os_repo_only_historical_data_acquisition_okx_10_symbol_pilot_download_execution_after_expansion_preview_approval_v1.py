from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import subprocess
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_after_expansion_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "de3b4f8"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SYMBOL_UNIVERSE_AND_MULTI_SYMBOL_"
    "EXPANSION_PREVIEW_APPROVED_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_NO_BUILD_NO_AGGREGATION"
)
GAP_STATUS = (
    "GAP_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_"
    "INCOMPLETE_VALIDATION_BLOCKED"
)
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION"
BEFORE_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_READY"
AFTER_QUALITY_PASS = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTED_PENDING_"
    "VALIDATOR_NO_BUILD_NO_AGGREGATION"
)
AFTER_QUALITY_GAP = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_DOWNLOAD_EXECUTION_GAP_RECORDED_"
    "VALIDATION_BLOCKED"
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
REUSED_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = date(2023, 7, 1)
DATE_RANGE_END = date(2026, 5, 18)
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_TOTAL_PILOT_FILE_COUNT = 10_530
EXPECTED_REUSED_FILE_COUNT = 1_053
EXPECTED_NEW_DOWNLOAD_FILE_COUNT = 9_477
EXPECTED_REUSE_SYMBOL_COUNT = 1
EXPECTED_NEW_SYMBOL_COUNT = 9
EXPECTED_DORMANT_REPO_ATTENTION_COUNT = 716
MAX_SYMBOLS = 10
MAX_NEW_SYMBOLS = 9
MAX_TOTAL_FILE_SET = 10_530
MAX_NEW_DOWNLOAD_FILES = 9_477
MAX_ZIP_SIZE_PER_FILE_MB = 100
MAX_ZIP_MEMBERS_PER_FILE = 10
MAX_CSV_SAMPLE_ROWS_PER_FILE = 5
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
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1.py"
)
NEXT_MODULE_GAP = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_blocked_or_gap_record_after_preview_approval_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
DOWNLOAD_DIR = OUTPUT_DIR / "downloaded_10_symbol_pilot_approved_quarantine"
PREVIEW_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_and_"
    "multi_symbol_expansion_preview_after_single_symbol_3_year_summary_v1"
)
PREVIEW_BUNDLE = PREVIEW_DIR / "historical_okx_symbol_universe_and_multi_symbol_expansion_preview_bundle_summary.json"
PREVIEW_MANIFEST = PREVIEW_DIR / "historical_okx_10_symbol_pilot_manifest_preview.json"
PREVIEW_RESOURCE_POLICY = PREVIEW_DIR / "historical_okx_10_symbol_pilot_resource_limits_policy.json"
PREVIEW_APPROVAL = PREVIEW_DIR / "historical_okx_10_symbol_pilot_download_approval_record.json"
BTC_HASH_REPORT = (
    EDGE_LAB_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_download_execution_validator_after_execution_v1"
    / "historical_okx_single_symbol_3_year_hash_validation_report.json"
)


class ExecutionBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class PlannedFile:
    symbol: str
    day: date
    url: str
    expected_zip_name: str
    expected_inner_csv: str
    local_zip_path: Path
    source_kind: str


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
        raise ExecutionBlocked(message)


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.exists(), f"missing JSON artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ExecutionBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    require(isinstance(data, dict), f"JSON artifact {label} is not an object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def inclusive_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def zip_url(symbol: str, day: date) -> str:
    compact_day = day.strftime("%Y%m%d")
    iso_day = day.isoformat()
    return (
        "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/"
        f"{compact_day}/{symbol}-candlesticks-{iso_day}.zip"
    )


def zip_name(symbol: str, day: date) -> str:
    return f"{symbol}-candlesticks-{day.isoformat()}.zip"


def csv_name(symbol: str, day: date) -> str:
    return f"{symbol}-candlesticks-{day.isoformat()}.csv"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_preconditions() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    require(head.startswith(EXPECTED_HEAD), f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(Path(__file__).resolve() == APPROVED_TOOL.resolve(), "running unexpected module path")
    return {
        "head": head,
        "tracked_python_count": tracked_python_count(),
        "repo_clean_or_only_this_tool": True,
    }


def validate_preview_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    bundle = load_json(PREVIEW_BUNDLE, "preview_bundle")
    manifest = load_json(PREVIEW_MANIFEST, "pilot_manifest_preview")
    resource_policy = load_json(PREVIEW_RESOURCE_POLICY, "pilot_resource_limits_policy")
    approval = load_json(PREVIEW_APPROVAL, "pilot_download_approval_record")
    btc_hash_report = load_json(BTC_HASH_REPORT, "btc_hash_report")

    require(
        bundle.get("historical_data_acquisition_okx_symbol_universe_and_multi_symbol_expansion_preview_status")
        == PREVIOUS_STATUS,
        "previous preview status mismatch",
    )
    require(bundle.get("next_module") == REQUESTED_MODULE, "current next_module mismatch")
    require(bundle.get("pilot_symbol_count") == len(PILOT_SYMBOLS), "pilot symbol count mismatch")
    require(bundle.get("pilot_symbols") == PILOT_SYMBOLS, "pilot symbols mismatch")
    require(bundle.get("expected_reuse_symbol_count") == EXPECTED_REUSE_SYMBOL_COUNT, "reuse symbol count mismatch")
    require(bundle.get("expected_new_symbol_count") == EXPECTED_NEW_SYMBOL_COUNT, "new symbol count mismatch")
    require(bundle.get("expected_total_pilot_file_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "total file count mismatch")
    require(bundle.get("expected_new_download_file_count") == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, "new download count mismatch")
    require(bundle.get("full_universe_acquisition_allowed_now") is False, "full universe allowed by preview")
    require(bundle.get("strategy_backtest_edge_allowed_now") is False, "strategy/backtest/edge allowed by preview")
    require(bundle.get("replacement_checks_all_true") is True, "preview replacement checks not true")

    require(manifest.get("pilot_symbols") == PILOT_SYMBOLS, "manifest pilot symbols mismatch")
    require(manifest.get("expected_total_pilot_file_set_count") == EXPECTED_TOTAL_PILOT_FILE_COUNT, "manifest total file set mismatch")
    require(resource_policy.get("max_symbols") == MAX_SYMBOLS, "resource max_symbols mismatch")
    require(resource_policy.get("max_new_symbols") == MAX_NEW_SYMBOLS, "resource max_new_symbols mismatch")
    require(resource_policy.get("max_total_file_set") == MAX_TOTAL_FILE_SET, "resource max_total_file_set mismatch")
    require(resource_policy.get("max_new_download_files") == MAX_NEW_DOWNLOAD_FILES, "resource max_new_download_files mismatch")
    require(resource_policy.get("max_zip_size_per_file_mb") == MAX_ZIP_SIZE_PER_FILE_MB, "resource max zip size mismatch")
    require(resource_policy.get("max_csv_sample_rows_per_file") == MAX_CSV_SAMPLE_ROWS_PER_FILE, "resource sample rows mismatch")
    require(resource_policy.get("no_full_csv_read_during_download_execution") is True, "resource allows full CSV read")
    require(resource_policy.get("no_build_aggregation_during_download_execution") is True, "resource allows build/aggregation")
    require(approval.get("pilot_download_approval_record_created") is True, "approval record missing")
    require(approval.get("approval_grants_future_10_symbol_pilot_download_next") is True, "future download approval missing")
    require(approval.get("approval_grants_download_now") is False, "approval grants download in preview")
    require(approval.get("approved_pilot_symbols") == PILOT_SYMBOLS, "approved pilot symbols mismatch")
    require(approval.get("next_module") == REQUESTED_MODULE, "approval next_module mismatch")
    require(btc_hash_report.get("all_reused_files_revalidated") is True, "BTC hash report was not validated")
    require(isinstance(btc_hash_report.get("hashes"), list), "BTC hash list missing")
    return bundle, manifest, resource_policy, approval, btc_hash_report


def build_plan(btc_hash_report: dict[str, Any]) -> list[PlannedFile]:
    days = inclusive_days(DATE_RANGE_START, DATE_RANGE_END)
    require(len(days) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL, "date range daily file count mismatch")
    btc_by_date = {
        item["date"]: item
        for item in btc_hash_report["hashes"]
        if isinstance(item, dict) and item.get("date") and item.get("local_zip_path")
    }
    planned: list[PlannedFile] = []
    for symbol in PILOT_SYMBOLS:
        for day in days:
            source_kind = "REUSED_VALIDATED_BTC_FILE_SET" if symbol == REUSED_SYMBOL else "NEW_APPROVED_PILOT_DOWNLOAD"
            if symbol == REUSED_SYMBOL:
                prior = btc_by_date.get(day.isoformat())
                require(prior is not None, f"missing BTC hash entry for {day.isoformat()}")
                local_zip_path = Path(str(prior["local_zip_path"]))
            else:
                local_zip_path = DOWNLOAD_DIR / symbol / zip_name(symbol, day)
            planned.append(
                PlannedFile(
                    symbol=symbol,
                    day=day,
                    url=zip_url(symbol, day),
                    expected_zip_name=zip_name(symbol, day),
                    expected_inner_csv=csv_name(symbol, day),
                    local_zip_path=local_zip_path,
                    source_kind=source_kind,
                )
            )
    require(len(planned) == EXPECTED_TOTAL_PILOT_FILE_COUNT, "planned file set count mismatch")
    require(sum(1 for item in planned if item.symbol == REUSED_SYMBOL) == EXPECTED_REUSED_FILE_COUNT, "planned reused file count mismatch")
    require(sum(1 for item in planned if item.symbol != REUSED_SYMBOL) == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, "planned new download file count mismatch")
    require({item.symbol for item in planned} == set(PILOT_SYMBOLS), "non-approved symbol in plan")
    return planned


def download_one(item: PlannedFile) -> dict[str, Any]:
    item.local_zip_path.parent.mkdir(parents=True, exist_ok=True)
    if item.local_zip_path.exists():
        return {
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "url": item.url,
            "local_zip_path": str(item.local_zip_path),
            "download_attempted": False,
            "download_succeeded": True,
            "failure_reason": None,
            "file_size_bytes": item.local_zip_path.stat().st_size,
            "downloaded_or_existing": "EXISTING_NEW_SYMBOL_FILE",
        }
    tmp_path = item.local_zip_path.with_suffix(item.local_zip_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    request = urllib.request.Request(item.url, headers={"User-Agent": "edge-factory-os-pilot-downloader/1.0"})
    last_error = ""
    for attempt in range(1, 4):
        total = 0
        try:
            with urllib.request.urlopen(request, timeout=90) as response, tmp_path.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_ZIP_SIZE_PER_FILE_MB * 1024 * 1024:
                        raise ExecutionBlocked(f"zip exceeds size limit: {item.url}")
                    handle.write(chunk)
            tmp_path.replace(item.local_zip_path)
            return {
                "symbol": item.symbol,
                "date": item.day.isoformat(),
                "url": item.url,
                "local_zip_path": str(item.local_zip_path),
                "download_attempted": True,
                "download_succeeded": True,
                "failure_reason": None,
                "file_size_bytes": item.local_zip_path.stat().st_size,
                "downloaded_or_existing": "DOWNLOADED_THIS_RUN",
                "download_attempt_count": attempt,
            }
        except Exception as exc:
            last_error = type(exc).__name__ + ": " + str(exc)
            if tmp_path.exists():
                tmp_path.unlink()
    return {
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "url": item.url,
        "local_zip_path": str(item.local_zip_path),
        "download_attempted": True,
        "download_succeeded": False,
        "failure_reason": last_error,
        "file_size_bytes": 0,
        "downloaded_or_existing": "FAILED",
        "download_attempt_count": 3,
    }


def execute_downloads(planned: list[PlannedFile]) -> list[dict[str, Any]]:
    new_items = [item for item in planned if item.symbol != REUSED_SYMBOL]
    require(len(new_items) <= MAX_NEW_DOWNLOAD_FILES, "new download file limit exceeded")
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(download_one, item) for item in new_items]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: (row["symbol"], row["date"]))
    return results


def inspect_zip(item: PlannedFile) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    failure: dict[str, Any] | None = None
    inventory = {
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "local_zip_path": str(item.local_zip_path),
        "zip_open_success": False,
        "zip_member_count": 0,
        "zip_members": [],
        "path_traversal_detected": False,
        "expected_inner_csv": item.expected_inner_csv,
        "expected_inner_csv_present": False,
    }
    schema_sample = {
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "expected_inner_csv": item.expected_inner_csv,
        "schema_match": False,
        "observed_schema": [],
        "sample_rows_read": 0,
        "sampled_symbol_values": [],
        "observed_symbols_match_expected": False,
    }
    hash_record = {
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "url": item.url,
        "local_zip_path": str(item.local_zip_path),
        "source_kind": item.source_kind,
        "file_size_bytes": 0,
        "sha256": None,
        "hash_computed_or_revalidated": False,
    }

    if not item.local_zip_path.exists():
        failure = {
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "url": item.url,
            "failure_stage": "ZIP_EXISTS",
            "failure_reason": "local ZIP missing",
        }
        return hash_record, inventory, schema_sample, failure

    hash_record["file_size_bytes"] = item.local_zip_path.stat().st_size
    hash_record["sha256"] = sha256_file(item.local_zip_path)
    hash_record["hash_computed_or_revalidated"] = True
    if hash_record["file_size_bytes"] > MAX_ZIP_SIZE_PER_FILE_MB * 1024 * 1024:
        failure = {
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "url": item.url,
            "failure_stage": "ZIP_SIZE",
            "failure_reason": "ZIP exceeds configured size limit",
        }
        return hash_record, inventory, schema_sample, failure

    try:
        with zipfile.ZipFile(item.local_zip_path) as zf:
            infos = zf.infolist()
            inventory["zip_open_success"] = True
            inventory["zip_member_count"] = len(infos)
            inventory["zip_members"] = [info.filename for info in infos]
            if len(infos) > MAX_ZIP_MEMBERS_PER_FILE:
                failure = {
                    "symbol": item.symbol,
                    "date": item.day.isoformat(),
                    "url": item.url,
                    "failure_stage": "ZIP_MEMBER_LIMIT",
                    "failure_reason": "ZIP member count exceeds limit",
                }
                return hash_record, inventory, schema_sample, failure
            for info in infos:
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or ":" in info.filename:
                    inventory["path_traversal_detected"] = True
            if inventory["path_traversal_detected"]:
                failure = {
                    "symbol": item.symbol,
                    "date": item.day.isoformat(),
                    "url": item.url,
                    "failure_stage": "ZIP_PATH_TRAVERSAL",
                    "failure_reason": "unsafe ZIP member path",
                }
                return hash_record, inventory, schema_sample, failure
            inventory["expected_inner_csv_present"] = item.expected_inner_csv in inventory["zip_members"]
            if not inventory["expected_inner_csv_present"]:
                failure = {
                    "symbol": item.symbol,
                    "date": item.day.isoformat(),
                    "url": item.url,
                    "failure_stage": "EXPECTED_CSV",
                    "failure_reason": "expected inner CSV missing",
                }
                return hash_record, inventory, schema_sample, failure
            with zf.open(item.expected_inner_csv, "r") as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
                reader = csv.reader(text)
                observed_schema = next(reader, [])
                schema_sample["observed_schema"] = observed_schema
                schema_sample["schema_match"] = observed_schema == EXPECTED_SCHEMA
                sampled_symbols: list[str] = []
                sample_rows_read = 0
                for row in reader:
                    if sample_rows_read >= MAX_CSV_SAMPLE_ROWS_PER_FILE:
                        break
                    sample_rows_read += 1
                    if row:
                        sampled_symbols.append(row[0])
                schema_sample["sample_rows_read"] = sample_rows_read
                schema_sample["sampled_symbol_values"] = sorted(set(sampled_symbols))
                schema_sample["observed_symbols_match_expected"] = all(value == item.symbol for value in sampled_symbols)
                if not schema_sample["schema_match"]:
                    failure = {
                        "symbol": item.symbol,
                        "date": item.day.isoformat(),
                        "url": item.url,
                        "failure_stage": "SCHEMA",
                        "failure_reason": "schema mismatch",
                    }
                    return hash_record, inventory, schema_sample, failure
                if not schema_sample["observed_symbols_match_expected"]:
                    failure = {
                        "symbol": item.symbol,
                        "date": item.day.isoformat(),
                        "url": item.url,
                        "failure_stage": "SAMPLED_SYMBOL",
                        "failure_reason": "sampled symbol mismatch",
                    }
                    return hash_record, inventory, schema_sample, failure
                if sample_rows_read > MAX_CSV_SAMPLE_ROWS_PER_FILE:
                    failure = {
                        "symbol": item.symbol,
                        "date": item.day.isoformat(),
                        "url": item.url,
                        "failure_stage": "CSV_SAMPLE_LIMIT",
                        "failure_reason": "sample row limit exceeded",
                    }
                    return hash_record, inventory, schema_sample, failure
    except zipfile.BadZipFile as exc:
        failure = {
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "url": item.url,
            "failure_stage": "ZIP_OPEN",
            "failure_reason": f"BadZipFile: {exc}",
        }
    except Exception as exc:
        failure = {
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "url": item.url,
            "failure_stage": "ZIP_INSPECTION",
            "failure_reason": type(exc).__name__ + ": " + str(exc),
        }
    return hash_record, inventory, schema_sample, failure


def inspect_all(planned: list[PlannedFile]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    hash_records: list[dict[str, Any]] = []
    inventory_records: list[dict[str, Any]] = []
    schema_records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for item in planned:
        hash_record, inventory, schema_sample, failure = inspect_zip(item)
        hash_records.append(hash_record)
        inventory_records.append(inventory)
        schema_records.append(schema_sample)
        if failure is not None:
            failures.append(failure)
    return hash_records, inventory_records, schema_records, failures


def summarize_symbol_counts(records: list[dict[str, Any]], value_key: str) -> dict[str, int]:
    counts: dict[str, int] = {symbol: 0 for symbol in PILOT_SYMBOLS}
    for record in records:
        if record.get(value_key):
            counts[record["symbol"]] += 1
    return counts


def write_reports(
    preconditions: dict[str, Any],
    planned: list[PlannedFile],
    download_results: list[dict[str, Any]],
    hash_records: list[dict[str, Any]],
    inventory_records: list[dict[str, Any]],
    schema_records: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    download_failures = [row for row in download_results if not row["download_succeeded"]]
    all_failures = download_failures + failures
    missing_or_failed_file_count = len({(row["symbol"], row["date"]) for row in all_failures})
    coverage_gap_detected = missing_or_failed_file_count > 0
    reused_file_count = sum(1 for record in hash_records if record["symbol"] == REUSED_SYMBOL and record["hash_computed_or_revalidated"])
    new_file_count = sum(1 for record in hash_records if record["symbol"] != REUSED_SYMBOL and record["hash_computed_or_revalidated"])
    final_file_set_count = reused_file_count + new_file_count
    all_hashes = len(hash_records) == EXPECTED_TOTAL_PILOT_FILE_COUNT and all(record["hash_computed_or_revalidated"] for record in hash_records)
    all_zip_open = len(inventory_records) == EXPECTED_TOTAL_PILOT_FILE_COUNT and all(record["zip_open_success"] for record in inventory_records)
    all_inner_csv = all(record["expected_inner_csv_present"] for record in inventory_records)
    all_schema = all(record["schema_match"] for record in schema_records)
    all_symbols = all(record["observed_symbols_match_expected"] for record in schema_records)
    max_sample_rows = max((record["sample_rows_read"] for record in schema_records), default=0)
    all_downloads_succeeded = not download_failures and new_file_count == EXPECTED_NEW_DOWNLOAD_FILE_COUNT
    all_reused_validated = reused_file_count == EXPECTED_REUSED_FILE_COUNT
    success = (
        not coverage_gap_detected
        and all_downloads_succeeded
        and all_reused_validated
        and all_hashes
        and all_zip_open
        and all_inner_csv
        and all_schema
        and all_symbols
        and final_file_set_count == EXPECTED_TOTAL_PILOT_FILE_COUNT
        and max_sample_rows <= MAX_CSV_SAMPLE_ROWS_PER_FILE
    )

    replacement_checks = {
        "expected_head": preconditions["head"].startswith(EXPECTED_HEAD),
        "repo_clean_or_only_this_tool": preconditions["repo_clean_or_only_this_tool"],
        "approved_manifest_used": True,
        "pilot_symbol_count_expected": len(PILOT_SYMBOLS) == MAX_SYMBOLS,
        "date_count_expected": len(inclusive_days(DATE_RANGE_START, DATE_RANGE_END)) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "new_download_limit_respected": new_file_count <= MAX_NEW_DOWNLOAD_FILES,
        "total_file_limit_respected": final_file_set_count <= MAX_TOTAL_FILE_SET,
        "all_downloads_succeeded": all_downloads_succeeded,
        "all_reused_files_validated": all_reused_validated,
        "all_hashes_computed_or_revalidated": all_hashes,
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_inner_csv,
        "all_expected_schema_match": all_schema,
        "all_observed_symbols_match_expected": all_symbols,
        "sample_row_limit_respected": max_sample_rows <= MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "no_full_csv_read": True,
        "no_build_aggregation": True,
        "no_api_browse": True,
        "no_research_backtest_edge_broad_claim": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())

    status = PASS_STATUS if success else GAP_STATUS
    next_module = NEXT_MODULE_PASS if success else NEXT_MODULE_GAP
    after_quality = AFTER_QUALITY_PASS if success else AFTER_QUALITY_GAP

    execution_report = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "download_execution_performed": True,
        "approved_manifest_used": True,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "date_range_start": DATE_RANGE_START.isoformat(),
        "date_range_end": DATE_RANGE_END.isoformat(),
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "expected_reused_file_count": EXPECTED_REUSED_FILE_COUNT,
        "expected_new_download_file_count": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "reused_symbol_count": EXPECTED_REUSE_SYMBOL_COUNT,
        "new_symbol_count": EXPECTED_NEW_SYMBOL_COUNT,
        "reused_file_count": reused_file_count,
        "new_download_file_count": new_file_count,
        "final_pilot_file_set_count": final_file_set_count,
        "download_result_count": len(download_results),
        "download_failure_count": len(download_failures),
        "missing_or_failed_file_count": missing_or_failed_file_count,
        "coverage_gap_detected": coverage_gap_detected,
    }
    provenance_report = {
        "provenance_report_created": True,
        "download_directory": str(DOWNLOAD_DIR),
        "reused_btc_hash_report": str(BTC_HASH_REPORT),
        "per_symbol_hash_count": summarize_symbol_counts(hash_records, "hash_computed_or_revalidated"),
        "per_symbol_zip_open_count": summarize_symbol_counts(inventory_records, "zip_open_success"),
        "per_symbol_schema_match_count": summarize_symbol_counts(schema_records, "schema_match"),
        "download_results": download_results,
    }
    hash_manifest = {
        "hash_manifest_created": True,
        "all_hashes_computed_or_revalidated": all_hashes,
        "hash_record_count": len(hash_records),
        "hashes": hash_records,
    }
    zip_inventory_report = {
        "zip_inventory_report_created": True,
        "max_zip_members_per_file": MAX_ZIP_MEMBERS_PER_FILE,
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_inner_csv,
        "path_traversal_detected": any(record["path_traversal_detected"] for record in inventory_records),
        "zip_inventory": inventory_records,
    }
    schema_sample_report = {
        "schema_sample_report_created": True,
        "expected_schema": EXPECTED_SCHEMA,
        "max_csv_sample_rows_read_per_file": max_sample_rows,
        "configured_max_csv_sample_rows_per_file": MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "full_csv_read_performed": False,
        "all_expected_schema_match": all_schema,
        "all_observed_symbols_match_expected": all_symbols,
        "schema_samples": schema_records,
    }
    coverage_gap_report = {
        "coverage_gap_report_created": True,
        "missing_or_failed_file_count": missing_or_failed_file_count,
        "coverage_gap_detected": coverage_gap_detected,
        "failures": all_failures,
    }
    compliance_report = {
        "compliance_report_created": True,
        "approved_manifest_used": True,
        "data_download_performed": True,
        "full_csv_read_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "parquet_read_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "runtime_touched": False,
        "capital_changed": False,
        "live_or_real_orders": False,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
    }
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "head": preconditions["head"],
        "tracked_python_count_at_execution_run": preconditions["tracked_python_count"],
        "historical_data_acquisition_okx_10_symbol_pilot_download_execution_status": status,
        "download_execution_performed": True,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "date_range_start": DATE_RANGE_START.isoformat(),
        "date_range_end": DATE_RANGE_END.isoformat(),
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "expected_reused_file_count": EXPECTED_REUSED_FILE_COUNT,
        "expected_new_download_file_count": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "reused_symbol_count": EXPECTED_REUSE_SYMBOL_COUNT,
        "new_symbol_count": EXPECTED_NEW_SYMBOL_COUNT,
        "reused_file_count": reused_file_count,
        "new_download_file_count": new_file_count,
        "final_pilot_file_set_count": final_file_set_count,
        "missing_or_failed_file_count": missing_or_failed_file_count,
        "coverage_gap_detected": coverage_gap_detected,
        "approved_manifest_used": True,
        "all_downloads_succeeded": all_downloads_succeeded,
        "all_reused_files_validated": all_reused_validated,
        "all_hashes_computed_or_revalidated": all_hashes,
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_inner_csv,
        "all_expected_schema_match": all_schema,
        "all_observed_symbols_match_expected": all_symbols,
        "max_csv_sample_rows_read_per_file": max_sample_rows,
        "full_csv_read_performed": False,
        "data_download_performed": True,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": after_quality,
        "active_p0_blocker_count": 0 if success else 1,
        "active_p1_attention_count": 12,
        "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": next_module,
        "derived_live_repo_post_check": "PENDING_POST_COMMIT_GUARD",
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_execution_report.json", execution_report)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_provenance_report.json", provenance_report)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_hash_manifest.json", hash_manifest)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_zip_inventory_report.json", zip_inventory_report)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_schema_sample_report.json", schema_sample_report)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_coverage_gap_report.json", coverage_gap_report)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_execution_compliance_report.json", compliance_report)
    write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_execution_summary.json", summary)
    return summary


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_10_symbol_pilot_download_execution_status": BLOCKED_STATUS,
        "download_execution_performed": False,
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "pilot_symbols": PILOT_SYMBOLS,
        "date_range_start": DATE_RANGE_START.isoformat(),
        "date_range_end": DATE_RANGE_END.isoformat(),
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_pilot_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "expected_reused_file_count": EXPECTED_REUSED_FILE_COUNT,
        "expected_new_download_file_count": EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "reused_symbol_count": 0,
        "new_symbol_count": EXPECTED_NEW_SYMBOL_COUNT,
        "reused_file_count": 0,
        "new_download_file_count": 0,
        "final_pilot_file_set_count": 0,
        "missing_or_failed_file_count": EXPECTED_TOTAL_PILOT_FILE_COUNT,
        "coverage_gap_detected": True,
        "blocker": message,
        "approved_manifest_used": False,
        "all_downloads_succeeded": False,
        "all_reused_files_validated": False,
        "all_hashes_computed_or_revalidated": False,
        "all_zip_open_success": False,
        "all_expected_inner_csv_present": False,
        "all_expected_schema_match": False,
        "all_observed_symbols_match_expected": False,
        "max_csv_sample_rows_read_per_file": 0,
        "full_csv_read_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": AFTER_QUALITY_GAP,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 12,
        "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": NEXT_MODULE_GAP,
        "derived_live_repo_post_check": "PENDING_POST_COMMIT_GUARD",
        "replacement_checks_all_true": False,
    }


def main() -> None:
    try:
        preconditions = validate_preconditions()
        _bundle, _manifest, _resource_policy, _approval, btc_hash_report = validate_preview_artifacts()
        planned = build_plan(btc_hash_report)
        download_results = execute_downloads(planned)
        hash_records, inventory_records, schema_records, failures = inspect_all(planned)
        summary = write_reports(
            preconditions,
            planned,
            download_results,
            hash_records,
            inventory_records,
            schema_records,
            failures,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
    except ExecutionBlocked as exc:
        blocked = blocked_payload(str(exc))
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_download_execution_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
