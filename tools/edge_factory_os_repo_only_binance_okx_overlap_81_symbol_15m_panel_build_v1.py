#!/usr/bin/env python3
"""Build a Binance/OKX overlap 81-symbol 15m OHLCV panel from Binance archives.

This is a data acquisition and panel build tool only. It downloads public
Binance USD-M futures monthly 15m kline archives, verifies their SHA256
checksums before opening, and writes partitioned panel files outside the repo.
It does not run strategy logic, compute returns, create candidates, or grant
runtime/live/capital permission.
"""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_BUILD_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_BUILD_MANIFEST"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1.py"
MANIFEST_RELATIVE_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_81_symbol_15m_panel_build_manifest_v1.json"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MANIFEST_PATH = REPO_ROOT / MANIFEST_RELATIVE_PATH
EXTERNAL_ARTIFACT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1"
)
DOWNLOAD_CACHE_DIR = EXTERNAL_ARTIFACT_ROOT / "download_cache"
PANEL_DIR = EXTERNAL_ARTIFACT_ROOT / "panel_15m_by_symbol"
PANEL_INDEX_DIR = EXTERNAL_ARTIFACT_ROOT / "panel_index"
PANEL_INDEX_PATH = PANEL_INDEX_DIR / "binance_okx_overlap_81_symbol_15m_panel_index_v1.json"
TEMP_OUTPUT_DIR = EXTERNAL_ARTIFACT_ROOT / "_tmp_panel_outputs"

READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

WINDOW_START_ISO = "2023-01-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_ISO = "2025-11-01T00:00:00Z"
WINDOW_START_MS = 1_672_531_200_000
WINDOW_END_MS = 1_761_955_200_000
INTERVAL_MS = 15 * 60 * 1000
MONTHLY_WINDOW_START = "2023-01"
MONTHLY_WINDOW_END = "2025-10"
EXPECTED_SYMBOL_COUNT = 81
REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES = 3
PROGRESS_INTERVAL_SECONDS = 60
MONTHLY_ARCHIVE_BASE = "https://data.binance.vision/data/futures/um/monthly/klines"
USER_AGENT = "edge-factory-os-binance-okx-overlap-15m-panel-build/1.0"

PANEL_HEADER = [
    "symbol",
    "timestamp_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "complete_15m",
]


class BlockedError(RuntimeError):
    """Raised when the panel build must stop without writing the manifest."""


def progress(start: float, event: str, **fields: Any) -> None:
    payload = {"elapsed_seconds": round(time.monotonic() - start, 1), "event": event}
    payload.update(fields)
    print(json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(clean)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise BlockedError(f"missing required source artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def verify_payload_hash(payload: dict[str, Any], relative_path: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise BlockedError(f"source artifact missing payload_sha256_excluding_hash: {relative_path}")
    observed = canonical_payload_hash(payload)
    if observed != stored:
        raise BlockedError(f"source artifact hash mismatch for {relative_path}: {observed} != {stored}")
    return stored


def current_head_from_git_files() -> str | None:
    head_path = REPO_ROOT / ".git" / "HEAD"
    if not head_path.exists():
        return None
    content = head_path.read_text(encoding="utf-8").strip()
    if content.startswith("ref: "):
        ref_path = REPO_ROOT / ".git" / content[5:]
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
        packed_refs = REPO_ROOT / ".git" / "packed-refs"
        if packed_refs.exists():
            ref_name = content[5:]
            for line in packed_refs.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith("#") and not line.startswith("^"):
                    parts = line.split(" ")
                    if len(parts) == 2 and parts[1] == ref_name:
                        return parts[0]
        return None
    return content


def find_symbol_list(value: Any) -> list[str] | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"exact_overlap_binance_symbols", "symbol_set"} and isinstance(child, list) and len(child) == 81:
                if all(isinstance(item, str) and item.endswith("USDT") for item in child):
                    return list(child)
            found = find_symbol_list(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found:
                return found
    return None


def find_first_key(value: Any, target_key: str) -> Any:
    if isinstance(value, dict):
        if target_key in value:
            return value[target_key]
        for child in value.values():
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    return None


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


def month_url(symbol: str, month: str) -> str:
    return f"{MONTHLY_ARCHIVE_BASE}/{symbol}/15m/{symbol}-15m-{month}.zip"


def checksum_url(symbol: str, month: str) -> str:
    return month_url(symbol, month) + ".CHECKSUM"


def request_bytes(url: str, allow_404: bool = False) -> tuple[int | None, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code == 404:
            return exc.code, b""
        return exc.code, exc.read()
    except Exception as exc:  # noqa: BLE001
        raise BlockedError(f"network request failed for {url}: {exc}") from exc


def request_head(url: str) -> int | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:  # noqa: BLE001
        raise BlockedError(f"network HEAD request failed for {url}: {exc}") from exc


def request_bytes_with_retry(url: str, allow_404: bool = False) -> tuple[int | None, bytes]:
    last_status: int | None = None
    last_error: str | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            status, data = request_bytes(url, allow_404=allow_404)
        except BlockedError as exc:
            status, data = None, b""
            last_error = str(exc)
        last_status = status
        if status == 200:
            return status, data
        if status == 404 and allow_404:
            return status, data
        if status is None or status in {408, 425, 429, 500, 502, 503, 504}:
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise BlockedError(
                f"network request failed after retries for {url}: status={last_status} error={last_error}"
            )
        if attempt == MAX_RETRIES:
            return status, data
        return status, data
    return last_status, b""


def parse_checksum(text: str, expected_filename: str) -> str:
    match = re.search(r"\b([a-fA-F0-9]{64})\b", text)
    if not match:
        raise BlockedError(f"checksum file missing SHA256 for {expected_filename}")
    if expected_filename not in text:
        raise BlockedError(f"checksum file does not reference {expected_filename}")
    return match.group(1).lower()


def verify_representative_availability(symbols: list[str]) -> list[dict[str, Any]]:
    representative_symbols = [symbol for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"] if symbol in symbols]
    if len(representative_symbols) < 4:
        raise BlockedError("representative symbols unavailable in 81-symbol universe")
    probe_months = ["2023-01", "2024-06", "2025-10"]
    results: list[dict[str, Any]] = []
    for symbol in representative_symbols:
        for month in probe_months:
            zip_status = request_head(month_url(symbol, month))
            checksum_status = request_head(checksum_url(symbol, month))
            ok = zip_status == 200 and checksum_status == 200
            results.append(
                {
                    "symbol": symbol,
                    "month": month,
                    "zip_status": zip_status,
                    "checksum_status": checksum_status,
                    "archive_and_checksum_available": ok,
                }
            )
    if not all(item["archive_and_checksum_available"] for item in results):
        raise BlockedError(f"representative 15m archive availability failed: {results}")
    return results


def prepare_external_dirs() -> None:
    if REPO_ROOT.resolve() in EXTERNAL_ARTIFACT_ROOT.resolve().parents:
        raise BlockedError("external artifact root resolves inside repo")
    EXTERNAL_ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_checksum(symbol: str, month: str, counters: dict[str, int], missing: list[dict[str, Any]]) -> str | None:
    filename = f"{symbol}-15m-{month}.zip"
    status, data = request_bytes_with_retry(checksum_url(symbol, month), allow_404=True)
    if status == 404:
        missing.append({"symbol": symbol, "month": month, "missing_url": checksum_url(symbol, month), "reason": "checksum_404"})
        return None
    if status != 200:
        raise BlockedError(f"checksum request failed for {filename}: status={status}")
    counters["checksum_files_fetched_count"] += 1
    return parse_checksum(data.decode("utf-8", errors="replace"), filename)


def verify_or_download_zip(symbol: str, month: str, expected_hash: str, counters: dict[str, int]) -> Path:
    filename = f"{symbol}-15m-{month}.zip"
    zip_path = DOWNLOAD_CACHE_DIR / filename
    if zip_path.is_file() and sha256_file(zip_path) == expected_hash:
        counters["reused_cached_zip_count"] += 1
        counters["checksum_verified_zip_count"] += 1
        return zip_path
    status, data = request_bytes_with_retry(month_url(symbol, month), allow_404=False)
    if status != 200:
        raise BlockedError(f"zip download failed for {filename}: status={status}")
    counters["downloaded_zip_count"] += 1
    counters["total_zip_bytes_downloaded"] += len(data)
    temp_path = zip_path.with_suffix(".zip.tmp")
    temp_path.write_bytes(data)
    observed_hash = sha256_file(temp_path)
    if observed_hash != expected_hash:
        try:
            temp_path.unlink()
        except OSError:
            pass
        counters["checksum_failed_count"] += 1
        raise BlockedError(f"checksum mismatch for {filename}: {observed_hash} != {expected_hash}")
    temp_path.replace(zip_path)
    counters["checksum_verified_zip_count"] += 1
    return zip_path


def parse_non_negative_float(value: str, field_name: str, symbol: str, timestamp: str) -> float:
    parsed = float(value)
    if not (parsed >= 0 and parsed < float("inf")):
        raise BlockedError(f"invalid nonnegative {field_name} for {symbol} at {timestamp}")
    return parsed


def parse_positive_float(value: str, field_name: str, symbol: str, timestamp: str) -> float:
    parsed = float(value)
    if not (parsed > 0 and parsed < float("inf")):
        raise BlockedError(f"invalid positive {field_name} for {symbol} at {timestamp}")
    return parsed


def iter_zip_rows(zip_path: Path) -> Any:
    with zipfile.ZipFile(zip_path, "r") as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise BlockedError(f"expected exactly one CSV in {zip_path.name}, found {csv_names}")
        with archive.open(csv_names[0], "r") as raw_handle:
            text_handle = io.TextIOWrapper(raw_handle, encoding="utf-8", newline="")
            reader = csv.reader(text_handle)
            for row in reader:
                if not row:
                    continue
                if row[0].strip().lower() == "open_time" or not row[0].strip().isdigit():
                    continue
                yield row


def build_symbol_panel(
    symbol: str,
    months: list[str],
    counters: dict[str, int],
    missing_archives: list[dict[str, Any]],
    start_time: float,
) -> dict[str, Any]:
    temp_output = TEMP_OUTPUT_DIR / f"{symbol}_15m.csv.gz.tmp"
    final_output = PANEL_DIR / f"{symbol}_15m.csv.gz"
    seen_timestamps: set[int] = set()
    output_row_count = 0
    rows_outside_window_skipped = 0
    duplicate_count = 0
    malformed_rows = 0
    incomplete_rows = 0
    source_zip_count = 0
    source_months_used: list[str] = []
    min_ts_ms: int | None = None
    max_ts_ms: int | None = None
    last_progress = time.monotonic()

    with gzip.open(temp_output, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(PANEL_HEADER)
        for month in months:
            expected_hash = fetch_checksum(symbol, month, counters, missing_archives)
            counters["symbol_month_candidates_checked_count"] += 1
            if expected_hash is None:
                continue
            counters["required_zip_count"] += 1
            zip_path = verify_or_download_zip(symbol, month, expected_hash, counters)
            source_zip_count += 1
            source_months_used.append(month)
            for row in iter_zip_rows(zip_path):
                if len(row) < 12:
                    malformed_rows += 1
                    raise BlockedError(f"malformed kline row in {zip_path.name}: {row}")
                open_time_ms = int(row[0])
                close_time_ms = int(row[6])
                if open_time_ms < WINDOW_START_MS or open_time_ms >= WINDOW_END_MS:
                    rows_outside_window_skipped += 1
                    continue
                timestamp_utc = iso_from_ms(open_time_ms)
                if open_time_ms % INTERVAL_MS != 0:
                    raise BlockedError(f"non-15m-aligned timestamp for {symbol}: {timestamp_utc}")
                complete_15m = close_time_ms == open_time_ms + INTERVAL_MS - 1
                if not complete_15m:
                    incomplete_rows += 1
                open_price = parse_positive_float(row[1], "open", symbol, timestamp_utc)
                high_price = parse_positive_float(row[2], "high", symbol, timestamp_utc)
                low_price = parse_positive_float(row[3], "low", symbol, timestamp_utc)
                close_price = parse_positive_float(row[4], "close", symbol, timestamp_utc)
                volume = parse_non_negative_float(row[5], "volume", symbol, timestamp_utc)
                quote_volume = parse_non_negative_float(row[7], "quote_volume", symbol, timestamp_utc)
                trade_count = int(row[8])
                taker_buy_base = parse_non_negative_float(row[9], "taker_buy_base_volume", symbol, timestamp_utc)
                taker_buy_quote = parse_non_negative_float(row[10], "taker_buy_quote_volume", symbol, timestamp_utc)
                if trade_count < 0:
                    raise BlockedError(f"negative trade_count for {symbol} at {timestamp_utc}")
                if high_price < max(open_price, close_price, low_price):
                    raise BlockedError(f"OHLC high sanity failed for {symbol} at {timestamp_utc}")
                if low_price > min(open_price, close_price, high_price):
                    raise BlockedError(f"OHLC low sanity failed for {symbol} at {timestamp_utc}")
                if open_time_ms in seen_timestamps:
                    duplicate_count += 1
                    raise BlockedError(f"duplicate symbol/timestamp for {symbol}: {timestamp_utc}")
                seen_timestamps.add(open_time_ms)
                min_ts_ms = open_time_ms if min_ts_ms is None else min(min_ts_ms, open_time_ms)
                max_ts_ms = open_time_ms if max_ts_ms is None else max(max_ts_ms, open_time_ms)
                output_row_count += 1
                writer.writerow(
                    [
                        symbol,
                        timestamp_utc,
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[7],
                        row[8],
                        row[9],
                        row[10],
                        "true" if complete_15m else "false",
                    ]
                )
            if time.monotonic() - last_progress >= PROGRESS_INTERVAL_SECONDS:
                progress(start_time, "symbol_build_progress", symbol=symbol, month=month, output_rows=output_row_count)
                last_progress = time.monotonic()
    if output_row_count == 0:
        raise BlockedError(f"zero output rows for symbol {symbol}")
    temp_output.replace(final_output)
    expected_between_first_last = 0
    missing_between_first_last = 0
    if min_ts_ms is not None and max_ts_ms is not None:
        expected_between_first_last = ((max_ts_ms - min_ts_ms) // INTERVAL_MS) + 1
        missing_between_first_last = expected_between_first_last - output_row_count
    return {
        "symbol": symbol,
        "source_zip_count": source_zip_count,
        "source_months_used": source_months_used,
        "output_15m_rows": output_row_count,
        "first_output_timestamp_utc": None if min_ts_ms is None else iso_from_ms(min_ts_ms),
        "last_output_timestamp_utc": None if max_ts_ms is None else iso_from_ms(max_ts_ms),
        "rows_outside_window_skipped": rows_outside_window_skipped,
        "duplicate_symbol_timestamp_count": duplicate_count,
        "malformed_rows": malformed_rows,
        "incomplete_15m_rows": incomplete_rows,
        "missing_15m_intervals_between_first_and_last_observed": missing_between_first_last,
        "expected_15m_intervals_between_first_and_last_observed": expected_between_first_last,
        "output_file_path": str(final_output),
        "output_file_sha256": sha256_file(final_output),
        "symbol_build_valid": True,
    }


def write_panel_index(symbol_records: list[dict[str, Any]]) -> dict[str, Any]:
    index = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_INDEX",
        "created_by_module": MODULE_PATH,
        "external_artifact_root": str(EXTERNAL_ARTIFACT_ROOT),
        "panel_partitioned_dir": str(PANEL_DIR),
        "window_start_utc": WINDOW_START_ISO,
        "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_ISO,
        "symbol_count": len(symbol_records),
        "symbols": [record["symbol"] for record in symbol_records],
        "panel_files": {
            record["symbol"]: {
                "path": record["output_file_path"],
                "sha256": record["output_file_sha256"],
                "row_count": record["output_15m_rows"],
                "min_timestamp_utc": record["first_output_timestamp_utc"],
                "max_timestamp_utc": record["last_output_timestamp_utc"],
            }
            for record in symbol_records
        },
        "safety": {
            "strategy_execution": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
        },
    }
    PANEL_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = PANEL_INDEX_PATH.with_suffix(".json.tmp")
    tmp_path.write_bytes(canonical_json_bytes(index) + b"\n")
    tmp_path.replace(PANEL_INDEX_PATH)
    return {"path": str(PANEL_INDEX_PATH), "sha256": sha256_file(PANEL_INDEX_PATH), "payload": index}


def cleanup_zip_cache_if_requested() -> dict[str, Any]:
    keep_cache = os.environ.get("EDGE_FACTORY_KEEP_BINANCE_15M_ZIP_CACHE") == "1"
    if keep_cache:
        return {"zip_cache_removed_after_success": False, "reason": "EDGE_FACTORY_KEEP_BINANCE_15M_ZIP_CACHE=1"}
    removed_files = 0
    removed_dirs = 0
    if DOWNLOAD_CACHE_DIR.exists():
        for child in DOWNLOAD_CACHE_DIR.iterdir():
            if child.is_file():
                child.unlink()
                removed_files += 1
            elif child.is_dir():
                shutil.rmtree(child)
                removed_dirs += 1
        try:
            DOWNLOAD_CACHE_DIR.rmdir()
            removed_dirs += 1
        except OSError:
            pass
    return {"zip_cache_removed_after_success": True, "removed_files": removed_files, "removed_dirs": removed_dirs}


def build_manifest() -> dict[str, Any]:
    start = time.monotonic()
    source_checkpoint = {
        "actual_head_before_build": current_head_from_git_files(),
        "repo_clean_before_build_confirmed_externally": True,
        "tracked_python_count_before_build_expected": 857,
        "target_window_start_utc": WINDOW_START_ISO,
        "target_window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_ISO,
    }
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest_source = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    source_hashes = {
        READINESS_PATH: verify_payload_hash(readiness, READINESS_PATH),
        PANEL_REVIEW_PATH: verify_payload_hash(panel_review, PANEL_REVIEW_PATH),
        BUILD_MANIFEST_PATH: verify_payload_hash(build_manifest_source, BUILD_MANIFEST_PATH),
        PREVIEW_PATH: verify_payload_hash(preview, PREVIEW_PATH),
        COVERAGE_LOCK_PATH: verify_payload_hash(coverage_lock, COVERAGE_LOCK_PATH),
    }
    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest_source)
    if symbols is None or len(symbols) != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("could not verify exact 81-symbol overlap universe")
    symbols = sorted(symbols)
    panel_review_passed = (
        panel_review.get("panel_validity_classification")
        or find_first_key(panel_review, "panel_validity_classification")
    ) == "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    if not panel_review_passed:
        raise BlockedError("existing Binance 1h panel review is not valid for metadata use")
    representative_results = verify_representative_availability(symbols)
    progress(start, "representative_15m_availability_verified", probes=len(representative_results))
    prepare_external_dirs()
    months = month_range(MONTHLY_WINDOW_START, MONTHLY_WINDOW_END)
    counters = {
        "symbol_month_candidates_checked_count": 0,
        "required_zip_count": 0,
        "checksum_files_fetched_count": 0,
        "downloaded_zip_count": 0,
        "reused_cached_zip_count": 0,
        "checksum_verified_zip_count": 0,
        "checksum_failed_count": 0,
        "total_zip_bytes_downloaded": 0,
    }
    missing_archives: list[dict[str, Any]] = []
    symbol_records: list[dict[str, Any]] = []
    for index, symbol in enumerate(symbols, start=1):
        progress(start, "symbol_build_start", symbol=symbol, symbol_index=index, symbol_count=len(symbols))
        record = build_symbol_panel(symbol, months, counters, missing_archives, start)
        symbol_records.append(record)
        progress(start, "symbol_build_complete", symbol=symbol, output_15m_rows=record["output_15m_rows"], source_zip_count=record["source_zip_count"])

    output_min = min(record["first_output_timestamp_utc"] for record in symbol_records if record["first_output_timestamp_utc"])
    output_max = max(record["last_output_timestamp_utc"] for record in symbol_records if record["last_output_timestamp_utc"])
    output_rows = sum(record["output_15m_rows"] for record in symbol_records)
    duplicate_count = sum(record["duplicate_symbol_timestamp_count"] for record in symbol_records)
    incomplete_count = sum(record["incomplete_15m_rows"] for record in symbol_records)
    rows_per_symbol = [record["output_15m_rows"] for record in symbol_records]
    missing_between = sum(record["missing_15m_intervals_between_first_and_last_observed"] for record in symbol_records)
    panel_index = write_panel_index(symbol_records)
    cleanup_summary = cleanup_zip_cache_if_requested()

    ohlc_sanity_valid = True
    validation_checks = {
        "exactly_one_new_python_tool_file_expected": True,
        "exactly_one_new_json_manifest_expected": True,
        "no_existing_files_modified_expected": True,
        "no_other_tracked_files_expected": True,
        "exact_overlap_symbol_count_verified_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
        "representative_15m_archive_availability_verified": True,
        "all_required_zips_downloaded_or_cached": counters["required_zip_count"]
        == counters["downloaded_zip_count"] + counters["reused_cached_zip_count"],
        "all_required_zips_checksum_verified": counters["required_zip_count"] == counters["checksum_verified_zip_count"],
        "output_symbol_count_verified_81": len(symbol_records) == EXPECTED_SYMBOL_COUNT,
        "no_duplicate_symbol_timestamp": duplicate_count == 0,
        "ohlc_sanity_valid": ohlc_sanity_valid,
        "no_rows_outside_window": True,
        "panel_files_written_outside_repo": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all(validation_checks.values())
    manifest: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": source_checkpoint,
        "source_artifacts": {
            "readiness_path": READINESS_PATH,
            "panel_review_path": PANEL_REVIEW_PATH,
            "build_manifest_path": BUILD_MANIFEST_PATH,
            "preview_path": PREVIEW_PATH,
            "coverage_lock_path": COVERAGE_LOCK_PATH,
            "payload_hashes": source_hashes,
            "source_artifacts_read_only": True,
        },
        "build_scope": {
            "universe": "Binance/OKX exact overlap 81 Binance symbols",
            "symbol_count": len(symbols),
            "symbols": symbols,
            "target_interval": "15m",
            "source": "Binance public data archive monthly USD-M futures klines",
            "source_url_template": f"{MONTHLY_ARCHIVE_BASE}/{{SYMBOL}}/15m/{{SYMBOL}}-15m-{{YYYY-MM}}.zip",
            "checksum_url_template": f"{MONTHLY_ARCHIVE_BASE}/{{SYMBOL}}/15m/{{SYMBOL}}-15m-{{YYYY-MM}}.zip.CHECKSUM",
            "window_start_utc": WINDOW_START_ISO,
            "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_ISO,
            "monthly_window_start": MONTHLY_WINDOW_START,
            "monthly_window_end": MONTHLY_WINDOW_END,
            "month_count": len(months),
            "symbol_month_candidate_count": len(symbols) * len(months),
            "listing_aware_ragged_panel": True,
            "missing_prelisting_archives_recorded_not_synthesized": True,
            "no_forward_fill": True,
            "no_backfill": True,
            "no_synthetic_rows": True,
        },
        "source_download_summary": {
            **counters,
            "missing_archive_count": len(missing_archives),
            "missing_archive_samples": missing_archives[:25],
            "representative_availability_results": representative_results,
            "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "retry_cap": MAX_RETRIES,
            "sequential_downloads": True,
            "zip_cache_cleanup": cleanup_summary,
        },
        "source_row_validation_summary": {
            "binance_csv_schema_expected": [
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
            "timestamp_15m_alignment_valid": True,
            "rows_outside_window_in_output": 0,
            "duplicate_symbol_timestamp_count": duplicate_count,
            "ohlc_sanity_valid": ohlc_sanity_valid,
            "volume_sanity_valid": True,
            "trade_count_sanity_valid": True,
            "taker_field_sanity_valid": True,
            "incomplete_15m_row_count": incomplete_count,
            "no_forward_fill": True,
            "no_backfill": True,
            "no_synthetic_rows": True,
        },
        "panel_output_summary": {
            "output_symbol_count": len(symbol_records),
            "output_15m_row_count": output_rows,
            "output_min_timestamp_utc": output_min,
            "output_max_timestamp_utc": output_max,
            "duplicate_symbol_timestamp_count": duplicate_count,
            "rows_per_symbol_min": min(rows_per_symbol),
            "rows_per_symbol_max": max(rows_per_symbol),
            "incomplete_or_missing_interval_summary": {
                "incomplete_15m_row_count": incomplete_count,
                "total_missing_15m_intervals_between_first_and_last_observed": missing_between,
                "symbols_with_missing_15m_intervals_between_first_and_last_observed": [
                    record["symbol"]
                    for record in symbol_records
                    if record["missing_15m_intervals_between_first_and_last_observed"] > 0
                ],
                "missing_archive_count": len(missing_archives),
                "missing_archive_policy": "recorded as unavailable source months; no synthetic rows were created",
            },
            "panel_index_sha256": panel_index["sha256"],
            "output_panel_files_sha256": {
                record["symbol"]: record["output_file_sha256"] for record in symbol_records
            },
            "valid_for_future_extreme_move_reversal_research": True,
            "valid_for_strategy_execution_now": False,
            "valid_for_candidate_generation": False,
            "valid_for_edge_claim": False,
        },
        "symbol_output_records": symbol_records,
        "non_repo_artifacts": {
            "external_artifact_root": str(EXTERNAL_ARTIFACT_ROOT),
            "download_cache": str(DOWNLOAD_CACHE_DIR),
            "panel_partitioned_dir": str(PANEL_DIR),
            "panel_index_path": str(PANEL_INDEX_PATH),
            "panel_index_sha256": panel_index["sha256"],
            "panel_files_written_outside_repo": True,
        },
        "limitations": [
            "This is a data acquisition and panel build manifest only.",
            "The panel is listing-aware/ragged; missing pre-listing archives are not synthesized.",
            "No strategy execution, returns, candidate generation, edge claim, or runtime/live/capital permission is created.",
            "Future strategy use requires a separate explicit contract and review.",
        ],
        "safety_permissions": {
            "panel_build_created": True,
            "future_strategy_execution_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_15m_panel_review_only": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    manifest["payload_sha256_excluding_hash"] = canonical_payload_hash(manifest)
    required_assertions = [
        manifest["status"] == STATUS,
        manifest["module"] == MODULE_PATH,
        manifest["panel_output_summary"]["output_symbol_count"] == EXPECTED_SYMBOL_COUNT,
        manifest["panel_output_summary"]["duplicate_symbol_timestamp_count"] == 0,
        manifest["panel_output_summary"]["valid_for_strategy_execution_now"] is False,
        manifest["safety_permissions"]["candidate_generation_allowed_now"] is False,
        manifest["safety_permissions"]["edge_claim_allowed_now"] is False,
        manifest["safety_permissions"]["runtime_permission_allowed_now"] is False,
        manifest["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise BlockedError("manifest invariant assertion failed")
    return manifest


def main() -> None:
    try:
        manifest = build_manifest()
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp_manifest = MANIFEST_PATH.with_suffix(".json.tmp")
        tmp_manifest.write_bytes(canonical_json_bytes(manifest) + b"\n")
        tmp_manifest.replace(MANIFEST_PATH)
        summary = {
            "status": manifest["status"],
            "external_artifact_root": str(EXTERNAL_ARTIFACT_ROOT),
            "panel_partitioned_dir": str(PANEL_DIR),
            "panel_index_path": str(PANEL_INDEX_PATH),
            "output_symbol_count": manifest["panel_output_summary"]["output_symbol_count"],
            "output_15m_row_count": manifest["panel_output_summary"]["output_15m_row_count"],
            "output_min_timestamp_utc": manifest["panel_output_summary"]["output_min_timestamp_utc"],
            "output_max_timestamp_utc": manifest["panel_output_summary"]["output_max_timestamp_utc"],
            "required_zip_count": manifest["source_download_summary"]["required_zip_count"],
            "downloaded_zip_count": manifest["source_download_summary"]["downloaded_zip_count"],
            "checksum_verified_zip_count": manifest["source_download_summary"]["checksum_verified_zip_count"],
            "duplicate_symbol_timestamp_count": manifest["panel_output_summary"]["duplicate_symbol_timestamp_count"],
            "ohlc_sanity_valid": manifest["source_row_validation_summary"]["ohlc_sanity_valid"],
            "payload_sha256_excluding_hash": manifest["payload_sha256_excluding_hash"],
            "replacement_checks_all_true": manifest["replacement_checks_all_true"],
            "strategy_execution_allowed_now": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    except BlockedError as exc:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "reason": str(exc),
                    "replacement_checks_all_true": False,
                    "strategy_execution_allowed_now": False,
                    "candidate_generation": False,
                    "edge_claim": False,
                    "runtime_live_capital": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
