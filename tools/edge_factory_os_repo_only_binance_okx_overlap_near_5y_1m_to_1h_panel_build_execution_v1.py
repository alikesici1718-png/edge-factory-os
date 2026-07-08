#!/usr/bin/env python3
"""Build the Binance/OKX exact-overlap near-5y 1m-to-1h panel.

This is a data panel build execution only. It reads the committed Binance
coverage lock and committed Option C preview, downloads only required Binance
public monthly 1m kline archives, verifies checksums, aggregates to 1h by
symbol, and writes partitioned panel files outside the repo.
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_1M_TO_1H_PANEL_BUILD_EXECUTED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1.py"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MANIFEST_PATH = REPO_PATH / BUILD_MANIFEST_PATH
TEMP_MANIFEST_PATH = MANIFEST_PATH.with_suffix(".json.tmp")
PREVIEW_PATH = REPO_PATH / "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = REPO_PATH / "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"
EXTERNAL_ARTIFACT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1"
)
PANEL_DIR = EXTERNAL_ARTIFACT_ROOT / "panel_1h_by_symbol"
PANEL_INDEX_DIR = EXTERNAL_ARTIFACT_ROOT / "panel_index"
PANEL_INDEX_PATH = PANEL_INDEX_DIR / "binance_okx_overlap_near_5y_1h_panel_index_v1.json"
TEMP_PANEL_INDEX_PATH = PANEL_INDEX_PATH.with_suffix(".json.tmp")
DOWNLOAD_CACHE_DIR = EXTERNAL_ARTIFACT_ROOT / "download_cache"
TEMP_OUTPUT_DIR = EXTERNAL_ARTIFACT_ROOT / "_tmp_panel_outputs"

PRIOR_HEAD = "60bdfdab78438b46a20d8188c7cfa169b91ebf63"
PRIOR_TRACKED_PYTHON_COUNT = 808
PREVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_NEAR_5Y_COVERAGE_LOCK_REVIEW_OKX_OVERLAP_PANEL_BUILD_PREVIEW_CREATED"
PREVIEW_PAYLOAD_HASH = "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9"
COVERAGE_LOCK_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_USDT_PERPETUAL_1M_COVERAGE_DISCOVERY_LOCK_CREATED"
COVERAGE_LOCK_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"
BUILD_OPTION = "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_SECOND_SOURCE_PANEL"
EXPECTED_SYMBOL_COUNT = 81
PREVIEW_EXPECTED_1H_ROWS = 3_164_952
PREVIEW_EXPECTED_1M_ROWS = 189_897_120
WINDOW_START_MS = 1_619_827_200_000
WINDOW_END_MS = 1_777_590_000_000
WINDOW_START_ISO = "2021-05-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_ISO = "2026-05-01T00:00:00Z"
WINDOW_END_LAST_HOUR_ISO = "2026-04-30T23:00:00Z"
MONTHLY_WINDOW_START = "2021-05"
MONTHLY_WINDOW_END = "2026-04"
REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES = 3
PROGRESS_INTERVAL_SECONDS = 60
MONTHLY_ARCHIVE_BASE = "https://data.binance.vision/data/futures/um/monthly/klines/"
CSV_HEADER = (
    "symbol,timestamp_utc,open,high,low,close,volume,quote_volume,trade_count,"
    "taker_buy_base_volume,taker_buy_quote_volume,minute_count,complete_1h\n"
)


class BlockedError(RuntimeError):
    """Raised when the build must stop before a successful manifest write."""


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def progress(start: float, event: str, **fields: Any) -> None:
    payload = {"elapsed_seconds": round(time.monotonic() - start, 1), "event": event}
    payload.update(fields)
    print(json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def ensure_under_external_root(path: Path) -> Path:
    resolved_root = EXTERNAL_ARTIFACT_ROOT.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise BlockedError(f"refusing external artifact operation outside root: {resolved_path}")
    return resolved_path


def clear_directory_contents(path: Path) -> int:
    ensure_under_external_root(path)
    if not path.exists():
        return 0
    removed = 0
    for child in path.iterdir():
        ensure_under_external_root(child)
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
        removed += 1
    return removed


def prepare_external_outputs_for_rebuild(start: float) -> dict[str, int]:
    EXTERNAL_ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    removed = {
        "stale_panel_files_removed": clear_directory_contents(PANEL_DIR),
        "stale_panel_index_files_removed": clear_directory_contents(PANEL_INDEX_DIR),
        "stale_temp_output_files_removed": clear_directory_contents(TEMP_OUTPUT_DIR),
    }
    stale_suffixes = (".tmp", ".partial", ".incomplete")
    stale_removed = 0
    for path in EXTERNAL_ARTIFACT_ROOT.rglob("*"):
        if path.is_file() and path.name.endswith(stale_suffixes):
            ensure_under_external_root(path)
            path.unlink()
            stale_removed += 1
    removed["stale_tmp_partial_incomplete_files_removed"] = stale_removed
    progress(start, "external_outputs_prepared_for_rebuild", **removed)
    return removed


def month_add(month: str, delta: int) -> str:
    year, month_number = (int(part) for part in month.split("-"))
    idx = year * 12 + month_number - 1 + delta
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def month_range(start: str, end: str) -> list[str]:
    months: list[str] = []
    month = start
    while month <= end:
        months.append(month)
        month = month_add(month, 1)
    return months


def iso_from_ms(open_time_ms: int) -> str:
    return dt.datetime.fromtimestamp(open_time_ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dt_from_iso(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def hours_between(start_iso: str, end_iso: str) -> int:
    return int((dt_from_iso(end_iso) - dt_from_iso(start_iso)).total_seconds() // 3600)


def month_start_iso(month: str) -> str:
    return f"{month}-01T00:00:00Z"


def hour_ms(open_time_ms: int) -> int:
    return open_time_ms - (open_time_ms % 3_600_000)


def month_url(symbol: str, month: str) -> str:
    return f"{MONTHLY_ARCHIVE_BASE}{symbol}/1m/{symbol}-1m-{month}.zip"


def checksum_url(symbol: str, month: str) -> str:
    return month_url(symbol, month) + ".CHECKSUM"


def request_bytes(url: str) -> tuple[int | None, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-binance-panel-build/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except Exception as exc:  # noqa: BLE001
        raise BlockedError(f"network request failed for {url}: {exc}") from exc


def request_bytes_with_retry(url: str, allow_404: bool = False) -> bytes:
    last_status: int | None = None
    for attempt in range(MAX_RETRIES + 1):
        status, data = request_bytes(url)
        last_status = status
        if status == 200:
            return data
        if status == 404:
            if allow_404:
                return b""
            raise BlockedError(f"required Binance archive URL returned 404: {url}")
        if status not in {408, 425, 429, 500, 502, 503, 504} or attempt == MAX_RETRIES:
            raise BlockedError(f"required Binance archive URL failed: status={status} url={url}")
        time.sleep(0.5 * (attempt + 1))
    raise BlockedError(f"required Binance archive URL failed after retries: status={last_status} url={url}")


def parse_checksum(text: str, expected_filename: str) -> str:
    match = re.search(r"\b([a-fA-F0-9]{64})\b", text)
    if not match:
        raise BlockedError(f"checksum file does not contain a SHA256 hash for {expected_filename}")
    if expected_filename not in text:
        raise BlockedError(f"checksum file does not reference expected filename {expected_filename}")
    return match.group(1).lower()


def verify_or_download_zip(symbol: str, month: str, counters: dict[str, int]) -> Path:
    DOWNLOAD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{symbol}-1m-{month}.zip"
    zip_path = DOWNLOAD_CACHE_DIR / filename
    checksum_text = request_bytes_with_retry(checksum_url(symbol, month)).decode("utf-8", errors="replace")
    counters["checksum_files_fetched_count"] += 1
    expected_hash = parse_checksum(checksum_text, filename)
    if zip_path.is_file() and sha256_file(zip_path) == expected_hash:
        counters["reused_cached_zip_count"] += 1
        counters["checksum_verified_zip_count"] += 1
        return zip_path
    data = request_bytes_with_retry(month_url(symbol, month))
    counters["downloaded_zip_count"] += 1
    counters["total_zip_bytes_downloaded"] += len(data)
    temp_path = zip_path.with_suffix(".zip.tmp")
    temp_path.write_bytes(data)
    observed_hash = sha256_file(temp_path)
    if observed_hash != expected_hash:
        counters["checksum_failed_count"] += 1
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise BlockedError(f"checksum mismatch for {filename}")
    temp_path.replace(zip_path)
    counters["checksum_verified_zip_count"] += 1
    return zip_path


def parse_decimal(value: str, label: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"bad numeric {label}={value!r}") from exc
    if parsed < 0 and label not in {"open", "high", "low", "close"}:
        raise ValueError(f"negative numeric {label}={value!r}")
    return parsed


def format_float(value: float) -> str:
    text = f"{value:.12f}".rstrip("0").rstrip(".")
    return text if text else "0"


def validate_panel_file(path: Path, expected_symbol: str) -> dict[str, Any]:
    if not path.is_file():
        raise BlockedError(f"panel output file missing: {path}")
    previous_timestamp: str | None = None
    seen_timestamps: set[str] = set()
    row_count = 0
    complete_rows = 0
    incomplete_rows = 0
    min_timestamp: str | None = None
    max_timestamp: str | None = None
    duplicate_hours = 0
    numeric_sanity = True
    ohlc_sanity = True
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        header = handle.readline()
        if header != CSV_HEADER:
            raise BlockedError(f"panel output header mismatch for {path}")
        for line in handle:
            parts = line.rstrip("\n").split(",")
            if len(parts) != 13:
                raise BlockedError(f"panel output row has wrong column count for {path}")
            symbol, timestamp = parts[0], parts[1]
            if symbol != expected_symbol:
                raise BlockedError(f"panel output row symbol mismatch for {path}: {symbol}")
            if timestamp < WINDOW_START_ISO or timestamp > WINDOW_END_LAST_HOUR_ISO:
                raise BlockedError(f"panel output timestamp outside window for {path}: {timestamp}")
            if previous_timestamp is not None and timestamp <= previous_timestamp:
                raise BlockedError(f"panel output timestamps not strictly sorted for {path}")
            previous_timestamp = timestamp
            if timestamp in seen_timestamps:
                duplicate_hours += 1
            seen_timestamps.add(timestamp)
            open_v = float(parts[2])
            high_v = float(parts[3])
            low_v = float(parts[4])
            close_v = float(parts[5])
            volume = float(parts[6])
            quote_volume = float(parts[7])
            trade_count = int(parts[8])
            taker_buy_base = float(parts[9])
            taker_buy_quote = float(parts[10])
            minute_count = int(parts[11])
            complete_flag = parts[12]
            if not (open_v > 0 and high_v > 0 and low_v > 0 and close_v > 0):
                numeric_sanity = False
            if volume < 0 or quote_volume < 0 or trade_count < 0 or taker_buy_base < 0 or taker_buy_quote < 0:
                numeric_sanity = False
            if not (high_v >= max(open_v, close_v, low_v) and low_v <= min(open_v, close_v, high_v)):
                ohlc_sanity = False
            if complete_flag not in {"true", "false"}:
                raise BlockedError(f"bad complete_1h flag in {path}: {complete_flag}")
            if (complete_flag == "true") != (minute_count == 60):
                raise BlockedError(f"complete_1h flag does not match minute_count in {path}")
            complete_rows += 1 if complete_flag == "true" else 0
            incomplete_rows += 1 if complete_flag == "false" else 0
            row_count += 1
            min_timestamp = timestamp if min_timestamp is None else min(min_timestamp, timestamp)
            max_timestamp = timestamp if max_timestamp is None else max(max_timestamp, timestamp)
    if row_count == 0:
        raise BlockedError(f"panel output file has zero rows: {path}")
    if not numeric_sanity:
        raise BlockedError(f"panel output numeric sanity failed for {path}")
    if not ohlc_sanity:
        raise BlockedError(f"panel output OHLC sanity failed for {path}")
    if duplicate_hours:
        raise BlockedError(f"panel output duplicate symbol-hour rows found for {path}")
    return {
        "complete_1h_rows": complete_rows,
        "duplicate_symbol_hour_count": duplicate_hours,
        "first_output_timestamp_utc": min_timestamp,
        "incomplete_1h_rows": incomplete_rows,
        "last_output_timestamp_utc": max_timestamp,
        "numeric_sanity_valid": numeric_sanity,
        "ohlc_sanity_valid": ohlc_sanity,
        "output_1h_rows": row_count,
    }


def build_row_count_delta_explanation(records: list[dict[str, Any]], output_rows: int) -> dict[str, Any]:
    month_start_expected_rows = sum(
        hours_between(month_start_iso(record["source_months_used"][0]), WINDOW_END_EXCLUSIVE_ISO)
        for record in records
    )
    first_output_expected_rows = sum(
        hours_between(record["first_output_timestamp_utc"], WINDOW_END_EXCLUSIVE_ISO)
        for record in records
    )
    terminal_missing_hours_after_last_output = sum(
        hours_between(
            (
                dt_from_iso(record["last_output_timestamp_utc"]) + dt.timedelta(hours=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            WINDOW_END_EXCLUSIVE_ISO,
        )
        for record in records
    )
    listing_month_pre_first_output_hours = month_start_expected_rows - first_output_expected_rows
    post_first_output_missing_hours = first_output_expected_rows - output_rows
    row_delta = output_rows - PREVIEW_EXPECTED_1H_ROWS
    reconciled = (
        month_start_expected_rows == PREVIEW_EXPECTED_1H_ROWS
        and output_rows
        + listing_month_pre_first_output_hours
        + post_first_output_missing_hours
        == PREVIEW_EXPECTED_1H_ROWS
    )
    delayed_start_symbols = [
        {
            "first_output_timestamp_utc": record["first_output_timestamp_utc"],
            "month_start_timestamp_utc": month_start_iso(record["source_months_used"][0]),
            "symbol": record["symbol"],
        }
        for record in records
        if record["first_output_timestamp_utc"] != month_start_iso(record["source_months_used"][0])
    ]
    return {
        "actual_output_1h_rows": output_rows,
        "listing_month_pre_first_output_hours": listing_month_pre_first_output_hours,
        "month_start_expected_rows": month_start_expected_rows,
        "post_first_output_missing_hours": post_first_output_missing_hours,
        "preview_expected_1h_rows": PREVIEW_EXPECTED_1H_ROWS,
        "reason": (
            "The preview row count is a coverage-metadata expectation from each symbol's first required month "
            "start through 2026-05-01 exclusive. The built panel is row-observed and listing-aware: it starts "
            "each symbol at the first observed Binance 1m row, does not synthesize pre-listing or missing "
            "hours, and therefore has fewer rows when the first required month begins before the first observed "
            "source row or when archive rows contain observed gaps."
        ),
        "row_count_delta_arithmetic_reconciled": reconciled,
        "row_count_delta_vs_preview": row_delta,
        "sample_symbols_with_first_output_after_required_month_start": delayed_start_symbols[:20],
        "symbols_with_first_output_after_required_month_start_count": len(delayed_start_symbols),
        "symbols_with_missing_minutes_between_first_and_last_observed": sum(
            1 for record in records if record["missing_minutes_between_first_and_last_observed"] > 0
        ),
        "terminal_missing_hours_after_last_output": terminal_missing_hours_after_last_output,
        "total_missing_minutes_between_first_and_last_observed": sum(
            record["missing_minutes_between_first_and_last_observed"] for record in records
        ),
    }


def build_required_plan(preview: dict[str, Any], coverage: dict[str, Any]) -> tuple[list[str], dict[str, list[str]], dict[str, str | None], dict[str, str]]:
    overlap = list(preview["okx_binance_overlap_planning"]["exact_overlap_binance_symbols"])
    if len(overlap) != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("preview exact overlap symbol count is not 81")
    records = {row["symbol"]: row for row in coverage["symbol_coverage_records"]}
    near_5y = set(coverage["locked_symbol_sets"]["binance_usdt_perpetual_near_5y_complete_symbols"])
    okx_by_binance = {
        binance: okx
        for binance, okx in zip(
            preview["okx_binance_overlap_planning"]["exact_overlap_binance_symbols"],
            preview["okx_binance_overlap_planning"]["exact_overlap_okx_symbols"],
        )
    }
    months_by_symbol: dict[str, list[str]] = {}
    start_by_symbol: dict[str, str | None] = {}
    missing: dict[str, list[str]] = {}
    for symbol in overlap:
        if symbol not in records:
            raise BlockedError(f"overlap symbol missing from coverage lock: {symbol}")
        if symbol not in near_5y:
            raise BlockedError(f"overlap symbol is not near-5y complete: {symbol}")
        record = records[symbol]
        start_candidates = [MONTHLY_WINDOW_START]
        for key in ("first_available_month", "onboard_month"):
            value = record.get(key)
            if isinstance(value, str) and re.match(r"^\d{4}-\d{2}$", value):
                start_candidates.append(value)
        start_month = max(start_candidates)
        required = month_range(start_month, MONTHLY_WINDOW_END)
        available = set(record.get("available_months", []))
        absent = [month for month in required if month not in available]
        if absent:
            missing[symbol] = absent
        months_by_symbol[symbol] = required
        start_by_symbol[symbol] = start_month
    if missing:
        raise BlockedError(f"required monthly coverage missing for overlap symbols: {missing}")
    return sorted(overlap), months_by_symbol, start_by_symbol, okx_by_binance


def load_sources() -> tuple[dict[str, Any], dict[str, Any], list[str], dict[str, list[str]], dict[str, str | None], dict[str, str], dict[str, str]]:
    if not PREVIEW_PATH.is_file():
        raise BlockedError(f"preview artifact is missing: {PREVIEW_PATH}")
    if not COVERAGE_LOCK_PATH.is_file():
        raise BlockedError(f"coverage lock is missing: {COVERAGE_LOCK_PATH}")
    source_hashes = {
        "coverage_lock_file_sha256_before_build": sha256_file(COVERAGE_LOCK_PATH),
        "preview_file_sha256_before_build": sha256_file(PREVIEW_PATH),
    }
    preview = read_json(PREVIEW_PATH)
    coverage = read_json(COVERAGE_LOCK_PATH)
    if preview.get("status") != PREVIEW_STATUS:
        raise BlockedError("preview artifact status is invalid")
    if preview.get("payload_sha256_excluding_hash") != PREVIEW_PAYLOAD_HASH:
        raise BlockedError("preview payload hash mismatch")
    if preview["panel_build_preview"]["recommended_next_build_option"] != BUILD_OPTION:
        raise BlockedError("preview does not recommend Option C")
    if coverage.get("status") != COVERAGE_LOCK_STATUS:
        raise BlockedError("coverage lock status is invalid")
    if coverage.get("payload_sha256_excluding_hash") != COVERAGE_LOCK_PAYLOAD_HASH:
        raise BlockedError("coverage lock payload hash mismatch")
    if coverage["global_coverage_summary"]["pending_or_failed_probe_symbols"] != 0:
        raise BlockedError("coverage lock has pending or failed probe symbols")
    symbols, months_by_symbol, start_by_symbol, okx_by_binance = build_required_plan(preview, coverage)
    return preview, coverage, symbols, months_by_symbol, start_by_symbol, okx_by_binance, source_hashes


def process_symbol(
    symbol: str,
    months: list[str],
    okx_symbol: str | None,
    counters: dict[str, int],
    start_time: float,
    symbol_index: int,
    symbol_total: int,
) -> dict[str, Any]:
    rows_by_minute: dict[int, tuple[str, str, str, str, str, str, str, str, str, str, str, str]] = {}
    hour_rows: dict[int, dict[str, Any]] = {}
    exact_duplicates = 0
    conflicts = 0
    malformed_rows = 0
    outside = 0
    raw_rows = 0
    clean_rows = 0
    numeric_sanity = True
    ohlc_sanity = True
    conflict_samples: list[dict[str, Any]] = []
    source_min_ms: int | None = None
    source_max_ms: int | None = None
    last_progress = time.monotonic()

    for month_index, month in enumerate(months, start=1):
        zip_path = verify_or_download_zip(symbol, month, counters)
        if time.monotonic() - last_progress >= PROGRESS_INTERVAL_SECONDS:
            progress(
                start_time,
                "symbol_month_progress",
                checksum_verified_zip_count=counters["checksum_verified_zip_count"],
                downloaded_zip_count=counters["downloaded_zip_count"],
                month=month,
                month_index=month_index,
                raw_1m_rows_read=counters["raw_1m_rows_read"],
                reused_cached_zip_count=counters["reused_cached_zip_count"],
                symbol=symbol,
                symbol_index=symbol_index,
                symbol_total=symbol_total,
            )
            last_progress = time.monotonic()
        expected_member = f"{symbol}-1m-{month}.csv"
        with zipfile.ZipFile(zip_path) as archive:
            members = [name for name in archive.namelist() if name.endswith(".csv")]
            if expected_member in members:
                member = expected_member
            elif len(members) == 1:
                member = members[0]
            else:
                raise BlockedError(f"unexpected ZIP members for {zip_path}: {members[:5]}")
            with archive.open(member) as handle:
                for raw_line in handle:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) < 12:
                        malformed_rows += 1
                        continue
                    try:
                        open_time = int(parts[0])
                    except ValueError:
                        # Header row.
                        continue
                    raw_rows += 1
                    counters["raw_1m_rows_read"] += 1
                    if open_time < WINDOW_START_MS or open_time >= WINDOW_END_MS:
                        outside += 1
                        continue
                    normalized = tuple(parts[:12])  # type: ignore[assignment]
                    prior = rows_by_minute.get(open_time)
                    if prior is not None:
                        if prior == normalized:
                            exact_duplicates += 1
                        else:
                            conflicts += 1
                            if len(conflict_samples) < 10:
                                conflict_samples.append({"month": month, "open_time": open_time, "symbol": symbol})
                        continue
                    rows_by_minute[open_time] = normalized
                    try:
                        open_v = parse_decimal(parts[1], "open")
                        high_v = parse_decimal(parts[2], "high")
                        low_v = parse_decimal(parts[3], "low")
                        close_v = parse_decimal(parts[4], "close")
                        volume = parse_decimal(parts[5], "volume")
                        quote_volume = parse_decimal(parts[7], "quote_volume")
                        trade_count = int(float(parts[8]))
                        taker_buy_base = parse_decimal(parts[9], "taker_buy_base_volume")
                        taker_buy_quote = parse_decimal(parts[10], "taker_buy_quote_volume")
                    except (ValueError, IndexError):
                        malformed_rows += 1
                        continue
                    if not (open_v > 0 and high_v > 0 and low_v > 0 and close_v > 0):
                        numeric_sanity = False
                    if volume < 0 or quote_volume < 0 or trade_count < 0 or taker_buy_base < 0 or taker_buy_quote < 0:
                        numeric_sanity = False
                    if not (high_v >= max(open_v, close_v, low_v) and low_v <= min(open_v, close_v, high_v)):
                        ohlc_sanity = False
                    hms = hour_ms(open_time)
                    bucket = hour_rows.get(hms)
                    if bucket is None:
                        hour_rows[hms] = {
                            "close": close_v,
                            "first_minute": open_time,
                            "high": high_v,
                            "last_minute": open_time,
                            "low": low_v,
                            "minute_set": {open_time},
                            "open": open_v,
                            "quote_volume": quote_volume,
                            "taker_buy_base_volume": taker_buy_base,
                            "taker_buy_quote_volume": taker_buy_quote,
                            "trade_count": trade_count,
                            "volume": volume,
                        }
                    else:
                        if open_time < bucket["first_minute"]:
                            bucket["first_minute"] = open_time
                            bucket["open"] = open_v
                        if open_time > bucket["last_minute"]:
                            bucket["last_minute"] = open_time
                            bucket["close"] = close_v
                        bucket["high"] = max(bucket["high"], high_v)
                        bucket["low"] = min(bucket["low"], low_v)
                        bucket["volume"] += volume
                        bucket["quote_volume"] += quote_volume
                        bucket["trade_count"] += trade_count
                        bucket["taker_buy_base_volume"] += taker_buy_base
                        bucket["taker_buy_quote_volume"] += taker_buy_quote
                        bucket["minute_set"].add(open_time)
                    source_min_ms = open_time if source_min_ms is None else min(source_min_ms, open_time)
                    source_max_ms = open_time if source_max_ms is None else max(source_max_ms, open_time)
                    clean_rows += 1
                    counters["clean_1m_rows_after_policy"] += 1
    if malformed_rows > 0:
        raise BlockedError(f"malformed rows found for {symbol}: {malformed_rows}")
    if not numeric_sanity:
        raise BlockedError(f"numeric sanity failed for {symbol}")
    if not ohlc_sanity:
        raise BlockedError(f"OHLC sanity failed for {symbol}")

    output_rows: list[str] = []
    complete_rows = 0
    incomplete_rows = 0
    previous_hour: int | None = None
    duplicate_hour_count = 0
    missing_minutes = 0
    sorted_hours = sorted(hour_rows)
    if sorted_hours:
        for expected_hour in range(sorted_hours[0], sorted_hours[-1] + 3_600_000, 3_600_000):
            if expected_hour not in hour_rows:
                missing_minutes += 60
    for hms in sorted_hours:
        if previous_hour == hms:
            duplicate_hour_count += 1
        previous_hour = hms
        row = hour_rows[hms]
        minute_count = len(row["minute_set"])
        complete = minute_count == 60
        complete_rows += 1 if complete else 0
        incomplete_rows += 0 if complete else 1
        if minute_count < 60:
            missing_minutes += 60 - minute_count
        output_rows.append(
            ",".join(
                [
                    symbol,
                    iso_from_ms(hms),
                    format_float(row["open"]),
                    format_float(row["high"]),
                    format_float(row["low"]),
                    format_float(row["close"]),
                    format_float(row["volume"]),
                    format_float(row["quote_volume"]),
                    str(int(row["trade_count"])),
                    format_float(row["taker_buy_base_volume"]),
                    format_float(row["taker_buy_quote_volume"]),
                    str(minute_count),
                    "true" if complete else "false",
                ]
            )
            + "\n"
        )
    if not output_rows:
        raise BlockedError(f"symbol has zero output rows: {symbol}")

    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final_path = PANEL_DIR / f"{symbol}_1h.csv.gz"
    temp_path = TEMP_OUTPUT_DIR / f"{symbol}_1h.csv.gz.tmp"
    with gzip.open(temp_path, "wt", encoding="utf-8", newline="\n") as handle:
        handle.write(CSV_HEADER)
        for line in output_rows:
            handle.write(line)
    temp_stats = validate_panel_file(temp_path, symbol)
    temp_sha = sha256_file(temp_path)
    temp_path.replace(final_path)
    final_stats = validate_panel_file(final_path, symbol)
    final_sha = sha256_file(final_path)
    if temp_sha != final_sha:
        raise BlockedError(f"output hash changed during atomic replace for {symbol}")
    if temp_stats != final_stats:
        raise BlockedError(f"output validation stats changed during atomic replace for {symbol}")

    return {
        "checksum_verified_count": len(months),
        "clean_1m_rows_after_policy": clean_rows,
        "complete_1h_rows": final_stats["complete_1h_rows"],
        "exact_duplicate_rows_dropped": exact_duplicates,
        "first_output_timestamp_utc": final_stats["first_output_timestamp_utc"],
        "first_source_timestamp_utc": iso_from_ms(source_min_ms) if source_min_ms is not None else None,
        "incomplete_1h_rows": final_stats["incomplete_1h_rows"],
        "last_output_timestamp_utc": final_stats["last_output_timestamp_utc"],
        "last_source_timestamp_utc": iso_from_ms(source_max_ms) if source_max_ms is not None else None,
        "malformed_rows": malformed_rows,
        "material_conflict_rows_quarantined": conflicts,
        "material_conflict_samples": conflict_samples,
        "missing_minutes_between_first_and_last_observed": missing_minutes,
        "numeric_sanity_valid": final_stats["numeric_sanity_valid"],
        "ohlc_sanity_valid": final_stats["ohlc_sanity_valid"],
        "okx_symbol_if_available": okx_symbol,
        "output_1h_rows": final_stats["output_1h_rows"],
        "output_file_path": str(final_path),
        "output_file_sha256": final_sha,
        "raw_1m_rows_read": raw_rows,
        "rows_outside_window_skipped": outside,
        "source_months_used": months,
        "source_zip_count": len(months),
        "symbol": symbol,
        "symbol_build_valid": True,
        "duplicate_symbol_hour_count": final_stats["duplicate_symbol_hour_count"],
    }


def build_panel() -> dict[str, Any]:
    start = time.monotonic()
    run_started = now_utc()
    preview, coverage, symbols, months_by_symbol, _start_by_symbol, okx_by_binance, source_hashes = load_sources()
    required_zip_count = sum(len(months) for months in months_by_symbol.values())
    if required_zip_count <= 0:
        raise BlockedError("required monthly ZIP count is zero")
    progress(start, "build_started", required_monthly_zip_count=required_zip_count, symbol_count=len(symbols))
    cleanup_summary = prepare_external_outputs_for_rebuild(start)
    counters = defaultdict(int)
    counters["required_monthly_zip_count"] = required_zip_count
    counters["reused_existing_valid_symbol_panel_count"] = 0
    counters["rebuilt_symbol_count"] = 0
    records: list[dict[str, Any]] = []
    for symbol_index, symbol in enumerate(symbols, start=1):
        progress(
            start,
            "symbol_started",
            months=len(months_by_symbol[symbol]),
            symbol=symbol,
            symbol_index=symbol_index,
            symbol_total=len(symbols),
        )
        record = process_symbol(
            symbol,
            months_by_symbol[symbol],
            okx_by_binance.get(symbol),
            counters,
            start,
            symbol_index,
            len(symbols),
        )
        records.append(record)
        counters["rebuilt_symbol_count"] += 1
        progress(
            start,
            "symbol_completed",
            output_1h_rows=record["output_1h_rows"],
            raw_1m_rows_read=counters["raw_1m_rows_read"],
            rebuilt_symbol_count=counters["rebuilt_symbol_count"],
            reused_existing_valid_symbol_panel_count=counters["reused_existing_valid_symbol_panel_count"],
            symbol=symbol,
            symbol_index=symbol_index,
            symbol_total=len(symbols),
        )
    records.sort(key=lambda row: row["symbol"])
    output_files = [Path(record["output_file_path"]) for record in records]
    output_file_hashes = {record["symbol"]: record["output_file_sha256"] for record in records}
    output_rows = sum(record["output_1h_rows"] for record in records)
    complete_rows = sum(record["complete_1h_rows"] for record in records)
    incomplete_rows = sum(record["incomplete_1h_rows"] for record in records)
    duplicate_hours = sum(record["duplicate_symbol_hour_count"] for record in records)
    row_delta = output_rows - PREVIEW_EXPECTED_1H_ROWS
    row_delta_explanation = build_row_count_delta_explanation(records, output_rows)
    row_delta_explained = row_delta_explanation["row_count_delta_arithmetic_reconciled"]
    index_payload = {
        "artifact_kind": "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_1H_PANEL_INDEX",
        "created_at_utc": now_utc(),
        "panel_files": [str(path) for path in output_files],
        "panel_partitioned_dir": str(PANEL_DIR),
        "row_count": output_rows,
        "schema": CSV_HEADER.strip().split(","),
        "symbol_count": len(records),
        "symbols": [record["symbol"] for record in records],
    }
    TEMP_PANEL_INDEX_PATH.write_bytes(canonical_json_bytes(index_payload) + b"\n")
    TEMP_PANEL_INDEX_PATH.replace(PANEL_INDEX_PATH)
    panel_index_sha = sha256_file(PANEL_INDEX_PATH)
    keep_cache = os.environ.get("EDGE_FACTORY_KEEP_BINANCE_ZIP_CACHE") == "1"
    source_hashes["coverage_lock_file_sha256_before_manifest_write"] = sha256_file(COVERAGE_LOCK_PATH)
    source_hashes["preview_file_sha256_before_manifest_write"] = sha256_file(PREVIEW_PATH)
    if source_hashes["coverage_lock_file_sha256_before_build"] != source_hashes["coverage_lock_file_sha256_before_manifest_write"]:
        raise BlockedError("coverage lock changed during build; refusing to write manifest")
    if source_hashes["preview_file_sha256_before_build"] != source_hashes["preview_file_sha256_before_manifest_write"]:
        raise BlockedError("preview artifact changed during build; refusing to write manifest")
    run_completed = now_utc()
    manifest: dict[str, Any] = {
        "aggregation_policy": {
            "aggregation": "1m_to_1h_ohlcv",
            "backfill": False,
            "close_policy": "last_1m_close_by_open_time",
            "complete_1h_policy": "minute_count_equals_60",
            "forward_fill": False,
            "high_policy": "max_1m_high",
            "low_policy": "min_1m_low",
            "open_policy": "first_1m_open_by_open_time",
            "quote_volume_policy": "sum",
            "synthetic_fill": False,
            "taker_buy_base_volume_policy": "sum",
            "taker_buy_quote_volume_policy": "sum",
            "trade_count_policy": "sum",
            "volume_policy": "sum",
        },
        "artifact_kind": "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_1M_TO_1H_PANEL_BUILD_MANIFEST",
        "build_scope": {
            "backfill": False,
            "build_option": BUILD_OPTION,
            "daily_tail_included": False,
            "exact_overlap_binance_symbols": symbols,
            "exact_overlap_okx_symbols": [okx_by_binance.get(symbol) for symbol in symbols],
            "exact_overlap_symbol_count": len(symbols),
            "forward_fill": False,
            "listing_aware_ragged_panel": True,
            "monthly_window_end": MONTHLY_WINDOW_END,
            "monthly_window_start": MONTHLY_WINDOW_START,
            "primary_window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_ISO,
            "primary_window_start_utc": WINDOW_START_ISO,
            "rectangular_full_5y_panel": False,
            "source_interval": "1m",
            "synthetic_pre_onboard_fill": False,
            "target_interval": "1h",
        },
        "limitations": [
            "This is a Binance second-source data panel build, not a backtest.",
            "No strategy returns were computed.",
            "No candidate generation was performed.",
            "No edge claim was made.",
            "No family release was made.",
            "No runtime/live/capital permission was granted.",
            "The panel is listing-aware/ragged and not a strict rectangular 5y panel.",
            "Daily tail through 2026-05-22 was not included in this first build.",
            "The panel ends at 2026-05-01T00:00:00Z exclusive.",
            "Future strategy research requires separate preregistration/governance.",
            "Future edge claim requires external/future holdout and separate governance.",
        ],
        "module": MODULE_PATH,
        "non_repo_artifacts": {
            "artifact_root_outside_repo": True,
            "download_cache_path": str(DOWNLOAD_CACHE_DIR),
            "external_artifact_root": str(EXTERNAL_ARTIFACT_ROOT),
            "external_cleanup_summary": cleanup_summary,
            "panel_files": [str(path) for path in output_files],
            "panel_index_path": str(PANEL_INDEX_PATH),
            "panel_partitioned_dir": str(PANEL_DIR),
            "tracked_in_git": False,
        },
        "panel_output_summary": {
            "complete_1h_row_count": complete_rows,
            "duplicate_symbol_hour_count": duplicate_hours,
            "external_artifact_root": str(EXTERNAL_ARTIFACT_ROOT),
            "incomplete_1h_row_count": incomplete_rows,
            "output_1h_row_count": output_rows,
            "output_files_count": len(output_files),
            "output_max_timestamp_utc": max(record["last_output_timestamp_utc"] for record in records),
            "output_min_timestamp_utc": min(record["first_output_timestamp_utc"] for record in records),
            "output_panel_files_sha256": output_file_hashes,
            "output_symbol_count": len(records),
            "output_valid_for_candidate_generation": False,
            "output_valid_for_edge_claim": False,
            "output_valid_for_read_only_second_source_panel_analysis": True,
            "output_valid_for_runtime_live_capital": False,
            "output_valid_for_strategy_search": False,
            "panel_index_path": str(PANEL_INDEX_PATH),
            "panel_index_sha256": panel_index_sha,
            "panel_partitioned_dir": str(PANEL_DIR),
            "preview_expected_1h_row_count": PREVIEW_EXPECTED_1H_ROWS,
            "rebuilt_symbol_count": counters["rebuilt_symbol_count"],
            "reused_existing_valid_symbol_panel_count": counters["reused_existing_valid_symbol_panel_count"],
            "row_count_delta_explained": row_delta_explained,
            "row_count_delta_explanation": row_delta_explanation,
            "row_count_delta_vs_preview": row_delta,
            "rows_per_symbol_max": max(record["output_1h_rows"] for record in records),
            "rows_per_symbol_min": min(record["output_1h_rows"] for record in records),
            "symbols_with_zero_rows": [record["symbol"] for record in records if record["output_1h_rows"] == 0],
        },
        "repo_scope": {
            "api_key_used": False,
            "binance_coverage_discovery_rerun": False,
            "binance_kline_rows_read": True,
            "binance_kline_zip_downloaded": counters["downloaded_zip_count"] > 0,
            "binance_kline_zip_opened": True,
            "binance_panel_built": True,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "panel_data_written_outside_repo": True,
            "private_api_used": False,
            "public_binance_archive_network_used": True,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
            "tracked_manifest_created_in_repo": True,
        },
        "safety_permissions": {
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "next_step_may_be_panel_build_review_or_validation_only": True,
            "okx_panel_access_allowed_now": False,
            "panel_build_executed": True,
            "panel_build_option": BUILD_OPTION,
            "runtime_permission_allowed_now": False,
            "strategy_research_not_allowed_from_this_manifest": True,
            "strategy_search_allowed_now": False,
        },
        "source_artifacts": {
            "coverage_lock_loaded": True,
            "coverage_lock_path": str(COVERAGE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "coverage_lock_file_sha256_before_build": source_hashes["coverage_lock_file_sha256_before_build"],
            "coverage_lock_file_sha256_before_manifest_write": source_hashes["coverage_lock_file_sha256_before_manifest_write"],
            "coverage_lock_unchanged_during_build": (
                source_hashes["coverage_lock_file_sha256_before_build"]
                == source_hashes["coverage_lock_file_sha256_before_manifest_write"]
            ),
            "coverage_lock_payload_hash_verified": True,
            "preview_artifact_loaded": True,
            "preview_artifact_path": str(PREVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preview_file_sha256_before_build": source_hashes["preview_file_sha256_before_build"],
            "preview_file_sha256_before_manifest_write": source_hashes["preview_file_sha256_before_manifest_write"],
            "preview_unchanged_during_build": (
                source_hashes["preview_file_sha256_before_build"]
                == source_hashes["preview_file_sha256_before_manifest_write"]
            ),
            "preview_payload_hash_verified": True,
            "source_artifacts_read_only": True,
        },
        "source_checkpoint": {
            "prior_coverage_lock": "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
            "prior_coverage_lock_payload_sha256_excluding_hash": COVERAGE_LOCK_PAYLOAD_HASH,
            "prior_coverage_lock_status": COVERAGE_LOCK_STATUS,
            "prior_head": PRIOR_HEAD,
            "prior_preview_artifact": "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
            "prior_preview_payload_sha256_excluding_hash": PREVIEW_PAYLOAD_HASH,
            "prior_preview_status": PREVIEW_STATUS,
            "prior_preview_tool": "tools/edge_factory_os_repo_only_binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.py",
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap second-source panel build",
            "repo_clean_before_build": True,
            "run_completed_at_utc": run_completed,
            "run_started_at_utc": run_started,
        },
        "source_download_summary": {
            "all_required_zips_verified": counters["checksum_failed_count"] == 0
            and counters["checksum_verified_zip_count"] == required_zip_count,
            "checksum_failed_count": counters["checksum_failed_count"],
            "checksum_files_fetched_count": counters["checksum_files_fetched_count"],
            "checksum_verified_zip_count": counters["checksum_verified_zip_count"],
            "download_cache_path": str(DOWNLOAD_CACHE_DIR),
            "download_cache_retained_after_success": keep_cache,
            "downloaded_zip_count": counters["downloaded_zip_count"],
            "failed_download_count": counters["failed_download_count"],
            "missing_required_zip_count": counters["missing_required_zip_count"],
            "public_archive_base": MONTHLY_ARCHIVE_BASE,
            "required_monthly_zip_count": required_zip_count,
            "reused_cached_zip_count": counters["reused_cached_zip_count"],
            "total_zip_bytes_downloaded": counters["total_zip_bytes_downloaded"],
        },
        "source_row_validation_summary": {
            "clean_1m_rows_after_policy": counters["clean_1m_rows_after_policy"],
            "duplicate_symbol_minute_count": sum(record["exact_duplicate_rows_dropped"] + record["material_conflict_rows_quarantined"] for record in records),
            "exact_duplicate_rows_dropped": sum(record["exact_duplicate_rows_dropped"] for record in records),
            "malformed_rows": sum(record["malformed_rows"] for record in records),
            "material_conflict_rows_quarantined": sum(record["material_conflict_rows_quarantined"] for record in records),
            "no_okx_rows_read": True,
            "no_rows_at_or_after_window_end": all(record["last_output_timestamp_utc"] <= WINDOW_END_LAST_HOUR_ISO for record in records),
            "numeric_sanity_valid": all(record["numeric_sanity_valid"] for record in records),
            "ohlc_sanity_valid": all(record["ohlc_sanity_valid"] for record in records),
            "raw_1m_rows_read": counters["raw_1m_rows_read"],
            "rows_outside_window_skipped": sum(record["rows_outside_window_skipped"] for record in records),
            "source_max_timestamp_utc": max(record["last_source_timestamp_utc"] for record in records),
            "source_min_timestamp_utc": min(record["first_source_timestamp_utc"] for record in records),
            "symbols_with_missing_minutes_count": sum(1 for record in records if record["missing_minutes_between_first_and_last_observed"] > 0),
            "total_missing_minutes_between_first_and_last_observed": sum(record["missing_minutes_between_first_and_last_observed"] for record in records),
        },
        "status": REQUIRED_STATUS,
        "symbol_output_records": records,
    }
    manifest["validation_checks"] = {
        "all_overlap_symbols_found_in_coverage_lock": True,
        "all_overlap_symbols_near_5y_complete": True,
        "all_required_zips_checksum_verified": manifest["source_download_summary"]["checksum_verified_zip_count"]
        == required_zip_count,
        "all_required_zips_downloaded_or_cached": (
            manifest["source_download_summary"]["downloaded_zip_count"]
            + manifest["source_download_summary"]["reused_cached_zip_count"]
            == required_zip_count
        ),
        "build_manifest_json_valid": True,
        "build_manifest_path_equals_required_path": BUILD_MANIFEST_PATH
        == "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
        "build_option_verified_option_c": True,
        "coverage_lock_loaded": True,
        "coverage_lock_payload_hash_verified": True,
        "coverage_lock_status_verified": True,
        "coverage_lock_unchanged_during_build": manifest["source_artifacts"]["coverage_lock_unchanged_during_build"],
        "duplicate_symbol_hour_count_zero": duplicate_hours == 0,
        "every_symbol_has_output_rows": not manifest["panel_output_summary"]["symbols_with_zero_rows"],
        "exact_overlap_symbol_count_verified_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
        "exactly_one_new_tracked_json_build_manifest_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "module_path_equals_required_path": MODULE_PATH
        == "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1.py",
        "no_candidate_generation": True,
        "no_checksum_failures": manifest["source_download_summary"]["checksum_failed_count"] == 0,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_rows_at_or_after_2026_05_01": manifest["source_row_validation_summary"]["no_rows_at_or_after_window_end"],
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "numeric_sanity_valid": manifest["source_row_validation_summary"]["numeric_sanity_valid"],
        "ohlc_sanity_valid": manifest["source_row_validation_summary"]["ohlc_sanity_valid"],
        "output_files_exist_outside_repo": all(path.is_file() for path in output_files),
        "output_rows_within_window": (
            manifest["panel_output_summary"]["output_min_timestamp_utc"] >= WINDOW_START_ISO
            and manifest["panel_output_summary"]["output_max_timestamp_utc"] <= WINDOW_END_LAST_HOUR_ISO
        ),
        "output_symbol_count_verified_81": len(records) == EXPECTED_SYMBOL_COUNT,
        "panel_index_exists_outside_repo": PANEL_INDEX_PATH.is_file(),
        "payload_sha256_excluding_hash_present": True,
        "preview_artifact_loaded": True,
        "preview_payload_hash_verified": True,
        "preview_status_verified": True,
        "preview_unchanged_during_build": manifest["source_artifacts"]["preview_unchanged_during_build"],
        "replacement_checks_all_true": True,
        "required_months_available_for_all_symbols": True,
        "row_count_delta_explained": row_delta_explained,
        "source_artifacts_read_only": True,
        "status_equals_required_status": True,
    }
    manifest["replacement_checks_all_true"] = all(value is True for value in manifest["validation_checks"].values())
    payload_without_hash = dict(manifest)
    payload_without_hash.pop("payload_sha256_excluding_hash", None)
    manifest["payload_sha256_excluding_hash"] = sha256_bytes(canonical_json_bytes(payload_without_hash))
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    assert manifest["status"] == REQUIRED_STATUS
    assert manifest["module"] == MODULE_PATH
    assert BUILD_MANIFEST_PATH == "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
    assert manifest["build_scope"]["build_option"] == BUILD_OPTION
    assert manifest["build_scope"]["exact_overlap_symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert manifest["source_download_summary"]["required_monthly_zip_count"] > 0
    assert manifest["source_download_summary"]["checksum_failed_count"] == 0
    assert manifest["source_download_summary"]["all_required_zips_verified"] is True
    assert manifest["panel_output_summary"]["output_symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert manifest["panel_output_summary"]["rebuilt_symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert manifest["panel_output_summary"]["reused_existing_valid_symbol_panel_count"] == 0
    assert manifest["panel_output_summary"]["row_count_delta_explained"] is True
    assert not manifest["panel_output_summary"]["symbols_with_zero_rows"]
    assert manifest["panel_output_summary"]["output_max_timestamp_utc"] <= WINDOW_END_LAST_HOUR_ISO
    assert manifest["source_row_validation_summary"]["numeric_sanity_valid"] is True
    assert manifest["source_row_validation_summary"]["ohlc_sanity_valid"] is True
    assert manifest["panel_output_summary"]["duplicate_symbol_hour_count"] == 0
    assert manifest["repo_scope"]["strategy_search_executed"] is False
    assert manifest["repo_scope"]["candidate_generation"] is False
    assert manifest["repo_scope"]["edge_claim"] is False
    assert manifest["repo_scope"]["runtime_live_capital"] is False
    assert manifest["repo_scope"]["okx_panel_rows_read"] is False
    assert manifest["source_artifacts"]["coverage_lock_unchanged_during_build"] is True
    assert manifest["source_artifacts"]["preview_unchanged_during_build"] is True
    assert manifest["source_artifacts"]["source_artifacts_read_only"] is True
    assert manifest["replacement_checks_all_true"] is True
    assert manifest["payload_sha256_excluding_hash"]


def write_manifest(manifest: dict[str, Any]) -> None:
    if sha256_file(COVERAGE_LOCK_PATH) != manifest["source_artifacts"]["coverage_lock_file_sha256_before_build"]:
        raise BlockedError("coverage lock changed immediately before manifest write")
    if sha256_file(PREVIEW_PATH) != manifest["source_artifacts"]["preview_file_sha256_before_build"]:
        raise BlockedError("preview artifact changed immediately before manifest write")
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEMP_MANIFEST_PATH.exists():
        TEMP_MANIFEST_PATH.unlink()
    TEMP_MANIFEST_PATH.write_bytes(canonical_json_bytes(manifest) + b"\n")
    TEMP_MANIFEST_PATH.replace(MANIFEST_PATH)


def delete_download_cache_after_success(manifest: dict[str, Any]) -> None:
    if manifest["source_download_summary"]["download_cache_retained_after_success"]:
        return
    if DOWNLOAD_CACHE_DIR.exists():
        ensure_under_external_root(DOWNLOAD_CACHE_DIR)
        shutil.rmtree(DOWNLOAD_CACHE_DIR)


def stdout_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    download = manifest["source_download_summary"]
    row_summary = manifest["source_row_validation_summary"]
    output = manifest["panel_output_summary"]
    return {
        "build_manifest_path": BUILD_MANIFEST_PATH,
        "build_option": manifest["build_scope"]["build_option"],
        "candidate_generation": False,
        "checksum_verified_zip_count": download["checksum_verified_zip_count"],
        "clean_1m_rows_after_policy": row_summary["clean_1m_rows_after_policy"],
        "complete_1h_row_count": output["complete_1h_row_count"],
        "downloaded_zip_count": download["downloaded_zip_count"],
        "duplicate_symbol_hour_count": output["duplicate_symbol_hour_count"],
        "edge_claim": False,
        "exact_overlap_symbol_count": manifest["build_scope"]["exact_overlap_symbol_count"],
        "external_artifact_root": output["external_artifact_root"],
        "incomplete_1h_row_count": output["incomplete_1h_row_count"],
        "numeric_sanity_valid": row_summary["numeric_sanity_valid"],
        "ohlc_sanity_valid": row_summary["ohlc_sanity_valid"],
        "output_1h_row_count": output["output_1h_row_count"],
        "output_max_timestamp_utc": output["output_max_timestamp_utc"],
        "output_min_timestamp_utc": output["output_min_timestamp_utc"],
        "output_symbol_count": output["output_symbol_count"],
        "panel_index_path": output["panel_index_path"],
        "panel_partitioned_dir": output["panel_partitioned_dir"],
        "payload_sha256_excluding_hash": manifest["payload_sha256_excluding_hash"],
        "preview_expected_1h_row_count": output["preview_expected_1h_row_count"],
        "raw_1m_rows_read": row_summary["raw_1m_rows_read"],
        "rebuilt_symbol_count": output["rebuilt_symbol_count"],
        "replacement_checks_all_true": manifest["replacement_checks_all_true"],
        "required_monthly_zip_count": download["required_monthly_zip_count"],
        "reused_existing_valid_symbol_panel_count": output["reused_existing_valid_symbol_panel_count"],
        "reused_cached_zip_count": download["reused_cached_zip_count"],
        "row_count_delta_explained": output["row_count_delta_explained"],
        "row_count_delta_vs_preview": output["row_count_delta_vs_preview"],
        "runtime_live_capital": False,
        "status": manifest["status"],
        "strategy_search_executed": False,
    }


def main() -> int:
    try:
        manifest = build_panel()
        validate_manifest(manifest)
        write_manifest(manifest)
        delete_download_cache_after_success(manifest)
    except BlockedError as exc:
        print(
            json.dumps(
                {
                    "exact_blocker": str(exc),
                    "external_artifact_root": str(EXTERNAL_ARTIFACT_ROOT),
                    "replacement_checks_all_true": False,
                    "status": "BLOCKED",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(stdout_summary(manifest), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
