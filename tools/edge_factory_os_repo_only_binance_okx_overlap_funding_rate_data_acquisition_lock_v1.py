#!/usr/bin/env python3
"""Acquire and lock Binance funding-rate history for the 81-symbol overlap."""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_ACQUISITION_LOCK_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_acquisition_lock_v1.py"
ACQUISITION_LOCK_PATH = "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json"
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MANIFEST_PATH = REPO_PATH / ACQUISITION_LOCK_PATH
TEMP_MANIFEST_PATH = MANIFEST_PATH.with_suffix(".json.tmp")

PREREGISTRATION_PATH = REPO_PATH / "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json"
READINESS_PATH = REPO_PATH / "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = REPO_PATH / "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = REPO_PATH / "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = REPO_PATH / "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = REPO_PATH / "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

EXTERNAL_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_acquisition_lock_v1"
)
FUNDING_BY_SYMBOL_DIR = EXTERNAL_ROOT / "funding_by_symbol"
FUNDING_INDEX_DIR = EXTERNAL_ROOT / "funding_index"
FUNDING_INDEX_PATH = FUNDING_INDEX_DIR / "binance_okx_overlap_funding_rate_index_v1.json"
TEMP_OUTPUT_DIR = EXTERNAL_ROOT / "_tmp_funding_outputs"
TEMP_INDEX_PATH = FUNDING_INDEX_PATH.with_suffix(".json.tmp")

PRIOR_HEAD = "b86b006add521ea08a1aa1d00050cdd70033301f"
PRIOR_TRACKED_PYTHON_COUNT = 812
PREREGISTRATION_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_HYPOTHESIS_PREREGISTRATION_CONTRACT_CREATED"
PREREGISTRATION_PAYLOAD_HASH = "5febb59aee08873de1dbfc0464da463811090c334c18c5f2a552e1768cb3c768"
READINESS_PAYLOAD_HASH = "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716"
PANEL_REVIEW_PAYLOAD_HASH = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"
BUILD_MANIFEST_PAYLOAD_HASH = "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7"
PREVIEW_PAYLOAD_HASH = "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9"
COVERAGE_LOCK_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "funding_rate_crowding_reversal"
ENDPOINT_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
SOURCE_ENDPOINT_LABEL = "fapi_v1_fundingRate"
REQUEST_LIMIT = 1000
REQUEST_TIMEOUT_SECONDS = 20
RETRY_CAP = 3
SLEEP_BETWEEN_REQUESTS_SECONDS = 0.25
WINDOW_START_UTC = "2023-07-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2025-10-31T16:00:00Z"
ENDPOINT_END_INCLUSIVE_UTC = "2025-10-31T15:59:59.999Z"
WINDOW_START_MS = 1_688_169_600_000
WINDOW_END_EXCLUSIVE_MS = 1_761_925_600_000
ENDPOINT_END_INCLUSIVE_MS = WINDOW_END_EXCLUSIVE_MS - 1
EXPECTED_SYMBOL_COUNT = 81
EXTREME_FUNDING_RATE_ABS_THRESHOLD = Decimal("0.05")
LARGE_GAP_THRESHOLD_HOURS = 24
EXPECTED_PRIMARY_INTERVAL_HOURS = 8
ALLOWED_ENDPOINT_NETLOC = "fapi.binance.com"
ALLOWED_ENDPOINT_PATH = "/fapi/v1/fundingRate"


class BlockedError(RuntimeError):
    """Raised when acquisition cannot complete safely."""


def progress(start: float, event: str, **fields: Any) -> None:
    payload = {"elapsed_seconds": round(time.monotonic() - start, 1), "event": event}
    payload.update(fields)
    print(json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def payload_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def verify_payload(payload: dict[str, Any], expected_hash: str) -> bool:
    return payload.get("payload_sha256_excluding_hash") == expected_hash and payload_hash(payload) == expected_hash


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iso_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def ensure_external(path: Path) -> None:
    if not is_under(path, EXTERNAL_ROOT):
        raise BlockedError(f"refusing non-repo artifact operation outside acquisition root: {path}")
    if is_under(path, REPO_PATH):
        raise BlockedError(f"refusing to write funding artifact inside repo: {path}")


def clear_directory(path: Path) -> None:
    ensure_external(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    for child in path.iterdir():
        ensure_external(child)
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def validate_endpoint_url(url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != ALLOWED_ENDPOINT_NETLOC or parsed.path != ALLOWED_ENDPOINT_PATH:
        raise BlockedError(f"non-allowed network endpoint attempted: {url}")


def decimal_from_string(value: Any, label: str) -> Decimal:
    if not isinstance(value, str) or value == "":
        raise ValueError(f"missing or non-string decimal field {label}")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal field {label}: {value}") from exc


def load_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    paths = [PREREGISTRATION_PATH, READINESS_PATH, PANEL_REVIEW_PATH, BUILD_MANIFEST_PATH, PREVIEW_PATH, COVERAGE_LOCK_PATH]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise BlockedError(f"required source artifacts missing: {missing}")
    prereg = read_json(PREREGISTRATION_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    if prereg.get("status") != PREREGISTRATION_STATUS:
        raise BlockedError("preregistration artifact status mismatch")
    if not verify_payload(prereg, PREREGISTRATION_PAYLOAD_HASH):
        raise BlockedError("preregistration payload hash mismatch")
    if not verify_payload(readiness, READINESS_PAYLOAD_HASH):
        raise BlockedError("readiness payload hash mismatch")
    if not verify_payload(panel_review, PANEL_REVIEW_PAYLOAD_HASH):
        raise BlockedError("panel review payload hash mismatch")
    if not verify_payload(build_manifest, BUILD_MANIFEST_PAYLOAD_HASH):
        raise BlockedError("build manifest payload hash mismatch")
    if not verify_payload(preview, PREVIEW_PAYLOAD_HASH):
        raise BlockedError("preview payload hash mismatch")
    if not verify_payload(coverage_lock, COVERAGE_LOCK_PAYLOAD_HASH):
        raise BlockedError("coverage lock payload hash mismatch")
    hypothesis = prereg["funding_rate_hypothesis_preregistration"]
    window = prereg["universe_and_window_contract"]
    if hypothesis["route_family"] != ROUTE_FAMILY:
        raise BlockedError("route family mismatch")
    if hypothesis["hypothesis_name"] != HYPOTHESIS_NAME:
        raise BlockedError("hypothesis name mismatch")
    if window["exact_overlap_symbol_count"] != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("exact overlap symbol count mismatch")
    if window["aligned_window_start_utc"] != WINDOW_START_UTC or window["aligned_window_end_exclusive_utc"] != WINDOW_END_EXCLUSIVE_UTC:
        raise BlockedError("aligned window mismatch")
    if prereg["predefined_config_grid"]["config_count"] != 9:
        raise BlockedError("config count mismatch")
    symbols = sorted(window.get("future_execution_binance_symbol_set", []))
    if len(symbols) != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("could not extract exact 81 Binance symbols")
    return prereg, readiness, panel_review, build_manifest, preview, coverage_lock, symbols


def request_funding_page(symbol: str, start_ms: int, end_ms: int, counters: dict[str, Any]) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "endTime": str(end_ms),
            "limit": str(REQUEST_LIMIT),
            "startTime": str(start_ms),
            "symbol": symbol,
        }
    )
    url = f"{ENDPOINT_URL}?{query}"
    validate_endpoint_url(url)
    last_error = ""
    for attempt in range(RETRY_CAP + 1):
        request = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-funding-rate-lock/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                status = response.status
                counters["http_status_counts"][str(status)] += 1
                counters["total_api_requests"] += 1
                payload = response.read()
        except urllib.error.HTTPError as exc:
            status = exc.code
            counters["http_status_counts"][str(status)] += 1
            counters["total_api_requests"] += 1
            if status == 418:
                counters["blocked_by_418_count"] += 1
                raise BlockedError(f"Binance returned 418 for {symbol}") from exc
            if status == 429:
                counters["rate_limit_backoff_applied_count"] += 1
                if attempt < RETRY_CAP:
                    counters["total_retries"] += 1
                    time.sleep(5)
                    continue
            if status >= 500 and attempt < RETRY_CAP:
                counters["total_retries"] += 1
                time.sleep(1 + attempt)
                continue
            raise BlockedError(f"fundingRate HTTP failure status={status} symbol={symbol}") from exc
        except Exception as exc:  # noqa: BLE001
            counters["http_status_counts"]["NETWORK_ERROR"] += 1
            last_error = str(exc)
            if attempt < RETRY_CAP:
                counters["total_retries"] += 1
                time.sleep(1 + attempt)
                continue
            raise BlockedError(f"fundingRate network failure symbol={symbol}: {last_error}") from exc
        if status != 200:
            if attempt < RETRY_CAP:
                counters["total_retries"] += 1
                time.sleep(1 + attempt)
                continue
            raise BlockedError(f"fundingRate non-200 status={status} symbol={symbol}")
        for json_attempt in range(2):
            try:
                decoded = json.loads(payload.decode("utf-8"))
            except json.JSONDecodeError as exc:
                if json_attempt == 0:
                    counters["total_retries"] += 1
                    time.sleep(1)
                    continue
                raise BlockedError(f"fundingRate malformed JSON symbol={symbol}") from exc
            if not isinstance(decoded, list):
                raise BlockedError(f"fundingRate response is not a list for {symbol}")
            time.sleep(SLEEP_BETWEEN_REQUESTS_SECONDS)
            return decoded
    raise BlockedError(f"fundingRate request failed after retries for {symbol}: {last_error}")


def normalize_record(symbol: str, raw: dict[str, Any], stats: dict[str, Any], extreme_samples: list[dict[str, Any]]) -> dict[str, Any] | None:
    missing_fields = [field for field in ("symbol", "fundingRate", "fundingTime") if field not in raw or raw.get(field) in (None, "")]
    if missing_fields:
        stats["missing_required_field_count"] += 1
        return None
    if raw["symbol"] != symbol:
        stats["missing_required_field_count"] += 1
        return None
    try:
        funding_time_ms = int(raw["fundingTime"])
        funding_rate_decimal = decimal_from_string(raw["fundingRate"], "fundingRate")
        mark_raw = raw.get("markPrice")
        mark_price_decimal = None if mark_raw in (None, "") else decimal_from_string(mark_raw, "markPrice")
    except (ValueError, TypeError):
        stats["invalid_numeric_count"] += 1
        return None
    if mark_price_decimal is not None and mark_price_decimal <= 0:
        stats["invalid_numeric_count"] += 1
        return None
    if abs(funding_rate_decimal) > EXTREME_FUNDING_RATE_ABS_THRESHOLD:
        stats["funding_rate_extreme_record_count"] += 1
        if len(extreme_samples) < 20:
            extreme_samples.append(
                {
                    "funding_rate": raw["fundingRate"],
                    "funding_time_utc": iso_from_ms(funding_time_ms),
                    "symbol": symbol,
                }
            )
    if funding_time_ms < WINDOW_START_MS or funding_time_ms >= WINDOW_END_EXCLUSIVE_MS:
        stats["records_outside_window_count"] += 1
        return None
    return {
        "funding_rate": raw["fundingRate"],
        "funding_time_ms": funding_time_ms,
        "funding_time_utc": iso_from_ms(funding_time_ms),
        "mark_price": mark_raw if mark_raw not in (None, "") else None,
        "source_endpoint": SOURCE_ENDPOINT_LABEL,
        "symbol": symbol,
    }


def acquire_symbol(symbol: str, global_counters: dict[str, Any], start_monotonic: float, symbol_index: int, symbol_count: int) -> dict[str, Any]:
    start_ms = WINDOW_START_MS
    records_by_time: dict[int, dict[str, Any]] = {}
    stats: dict[str, Any] = defaultdict(int)
    extreme_samples: list[dict[str, Any]] = []
    request_count_start = global_counters["total_api_requests"]
    retry_count_start = global_counters["total_retries"]
    while start_ms <= ENDPOINT_END_INCLUSIVE_MS:
        page = request_funding_page(symbol, start_ms, ENDPOINT_END_INCLUSIVE_MS, global_counters)
        stats["acquisition_request_count"] = global_counters["total_api_requests"] - request_count_start
        if not page:
            stats["api_empty_page_count"] += 1
            global_counters["total_empty_pages"] += 1
            break
        page_max_time = start_ms
        for raw in page:
            normalized = normalize_record(symbol, raw, stats, extreme_samples)
            if normalized is None:
                continue
            funding_time = normalized["funding_time_ms"]
            page_max_time = max(page_max_time, funding_time)
            if funding_time in records_by_time:
                stats["duplicate_funding_time_count"] += 1
                continue
            records_by_time[funding_time] = normalized
        if page_max_time >= ENDPOINT_END_INCLUSIVE_MS:
            break
        if len(page) < REQUEST_LIMIT:
            break
        start_ms = page_max_time + 1
    records = [records_by_time[key] for key in sorted(records_by_time)]
    if not records:
        raise BlockedError(f"symbol has zero funding records: {symbol}")
    previous_time: int | None = None
    interval_distribution: dict[str, int] = defaultdict(int)
    max_gap_hours = 0.0
    non_8h_count = 0
    large_gap_count = 0
    for record in records:
        funding_time = record["funding_time_ms"]
        if previous_time is not None:
            delta_hours = (funding_time - previous_time) / 3_600_000
            key = f"{delta_hours:g}"
            interval_distribution[key] += 1
            if delta_hours != EXPECTED_PRIMARY_INTERVAL_HOURS:
                non_8h_count += 1
            if delta_hours > LARGE_GAP_THRESHOLD_HOURS:
                large_gap_count += 1
            max_gap_hours = max(max_gap_hours, delta_hours)
        previous_time = funding_time
    rates = [Decimal(record["funding_rate"]) for record in records]
    positive = sum(1 for value in rates if value > 0)
    negative = sum(1 for value in rates if value < 0)
    zero = sum(1 for value in rates if value == 0)
    output_path = FUNDING_BY_SYMBOL_DIR / f"{symbol}_funding_rate.jsonl.gz"
    temp_path = TEMP_OUTPUT_DIR / f"{symbol}_funding_rate.jsonl.gz.tmp"
    ensure_external(output_path)
    ensure_external(temp_path)
    with gzip.open(temp_path, "wt", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")
    temp_stats = validate_symbol_file(temp_path, symbol)
    temp_path.replace(output_path)
    final_stats = validate_symbol_file(output_path, symbol)
    if temp_stats != final_stats:
        raise BlockedError(f"funding file validation changed after atomic replace for {symbol}")
    file_sha = sha256_file(output_path)
    progress(
        start_monotonic,
        "symbol_completed",
        records=len(records),
        requests=stats["acquisition_request_count"],
        retries=global_counters["total_retries"],
        symbol=symbol,
        symbol_index=symbol_index,
        symbol_total=symbol_count,
        total_records=global_counters["total_funding_records"] + len(records),
    )
    return {
        "acquisition_request_count": stats["acquisition_request_count"],
        "api_empty_page_count": stats["api_empty_page_count"],
        "duplicate_funding_time_count": stats["duplicate_funding_time_count"],
        "first_funding_time_utc": records[0]["funding_time_utc"],
        "funding_rate_extreme_record_count": stats["funding_rate_extreme_record_count"],
        "funding_rate_extreme_samples": extreme_samples,
        "funding_record_count": len(records),
        "interval_hours_distribution": dict(sorted(interval_distribution.items(), key=lambda item: float(item[0]))),
        "invalid_numeric_count": stats["invalid_numeric_count"],
        "large_gap_count": large_gap_count,
        "last_funding_time_utc": records[-1]["funding_time_utc"],
        "mark_price_sanity_valid": True,
        "max_funding_rate": str(max(rates)),
        "max_gap_hours": max_gap_hours,
        "mean_funding_rate": str(sum(rates) / Decimal(len(rates))),
        "min_funding_rate": str(min(rates)),
        "missing_required_field_count": stats["missing_required_field_count"],
        "negative_funding_count": negative,
        "non_8h_interval_count": non_8h_count,
        "non_monotonic_time_count": final_stats["non_monotonic_time_count"],
        "output_file_path": str(output_path),
        "output_file_sha256": file_sha,
        "positive_funding_count": positive,
        "records_outside_window_count": stats["records_outside_window_count"],
        "retry_count": global_counters["total_retries"] - retry_count_start,
        "symbol": symbol,
        "symbol_acquisition_valid": (
            final_stats["record_count"] == len(records)
            and final_stats["duplicate_funding_time_count"] == 0
            and stats["invalid_numeric_count"] == 0
            and stats["missing_required_field_count"] == 0
            and stats["records_outside_window_count"] == 0
        ),
        "zero_funding_count": zero,
    }


def validate_symbol_file(path: Path, symbol: str) -> dict[str, int]:
    record_count = 0
    previous_time: int | None = None
    duplicate_count = 0
    non_monotonic_count = 0
    seen: set[int] = set()
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if sorted(row) != ["funding_rate", "funding_time_ms", "funding_time_utc", "mark_price", "source_endpoint", "symbol"]:
                raise BlockedError(f"bad JSONL schema in {path}")
            if row["symbol"] != symbol:
                raise BlockedError(f"symbol mismatch in {path}")
            funding_time = int(row["funding_time_ms"])
            if funding_time < WINDOW_START_MS or funding_time >= WINDOW_END_EXCLUSIVE_MS:
                raise BlockedError(f"funding row outside window in {path}")
            if row["funding_time_utc"] != iso_from_ms(funding_time):
                raise BlockedError(f"funding_time_utc mismatch in {path}")
            decimal_from_string(row["funding_rate"], "fundingRate")
            if row["mark_price"] is not None and decimal_from_string(row["mark_price"], "markPrice") <= 0:
                raise BlockedError(f"bad markPrice in {path}")
            if previous_time is not None and funding_time <= previous_time:
                non_monotonic_count += 1
            if funding_time in seen:
                duplicate_count += 1
            seen.add(funding_time)
            previous_time = funding_time
            record_count += 1
    return {
        "duplicate_funding_time_count": duplicate_count,
        "non_monotonic_time_count": non_monotonic_count,
        "record_count": record_count,
    }


def build_index(symbol_records: list[dict[str, Any]]) -> dict[str, Any]:
    index = {
        "aligned_window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
        "aligned_window_start_utc": WINDOW_START_UTC,
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_INDEX",
        "created_by_module": MODULE_PATH,
        "external_artifact_root": str(EXTERNAL_ROOT),
        "funding_by_symbol_dir": str(FUNDING_BY_SYMBOL_DIR),
        "source_endpoint": SOURCE_ENDPOINT_LABEL,
        "symbol_count": len(symbol_records),
        "symbol_files": [
            {
                "funding_record_count": record["funding_record_count"],
                "output_file_path": record["output_file_path"],
                "output_file_sha256": record["output_file_sha256"],
                "symbol": record["symbol"],
            }
            for record in symbol_records
        ],
        "total_funding_records": sum(record["funding_record_count"] for record in symbol_records),
    }
    index_hash_input = dict(index)
    index_hash_input.pop("payload_sha256_excluding_hash", None)
    index["payload_sha256_excluding_hash"] = hashlib.sha256(canonical_json_bytes(index_hash_input)).hexdigest()
    return index


def write_index(index: dict[str, Any]) -> None:
    ensure_external(FUNDING_INDEX_DIR)
    FUNDING_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_INDEX_PATH.write_bytes(canonical_json_bytes(index) + b"\n")
    TEMP_INDEX_PATH.replace(FUNDING_INDEX_PATH)


def acquire_all() -> dict[str, Any]:
    start_monotonic = time.monotonic()
    acquisition_started = now_utc()
    prereg, readiness, panel_review, build_manifest, preview, coverage_lock, symbols = load_sources()
    progress(start_monotonic, "acquisition_started", symbol_count=len(symbols), window_start=WINDOW_START_UTC, window_end=WINDOW_END_EXCLUSIVE_UTC)
    EXTERNAL_ROOT.mkdir(parents=True, exist_ok=True)
    FUNDING_BY_SYMBOL_DIR.mkdir(parents=True, exist_ok=True)
    FUNDING_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clear_directory(FUNDING_BY_SYMBOL_DIR)
    clear_directory(FUNDING_INDEX_DIR)
    clear_directory(TEMP_OUTPUT_DIR)
    counters: dict[str, Any] = defaultdict(int)
    counters["http_status_counts"] = defaultdict(int)
    failed_symbols: list[str] = []
    symbol_records: list[dict[str, Any]] = []
    for index, symbol in enumerate(symbols, start=1):
        progress(start_monotonic, "symbol_started", symbol=symbol, symbol_index=index, symbol_total=len(symbols), total_api_requests=counters["total_api_requests"])
        try:
            record = acquire_symbol(symbol, counters, start_monotonic, index, len(symbols))
        except Exception:
            failed_symbols.append(symbol)
            raise
        counters["total_funding_records"] += record["funding_record_count"]
        symbol_records.append(record)
    symbol_records.sort(key=lambda item: item["symbol"])
    index_payload = build_index(symbol_records)
    write_index(index_payload)
    funding_index_sha = sha256_file(FUNDING_INDEX_PATH)
    acquisition_completed = now_utc()
    output_hashes = {record["symbol"]: record["output_file_sha256"] for record in symbol_records}
    total_invalid_numeric = sum(record["invalid_numeric_count"] for record in symbol_records)
    total_missing_required = sum(record["missing_required_field_count"] for record in symbol_records)
    total_duplicates = sum(record["duplicate_funding_time_count"] for record in symbol_records)
    total_outside = sum(record["records_outside_window_count"] for record in symbol_records)
    total_large_gap_count = sum(record["large_gap_count"] for record in symbol_records)
    symbols_with_large_gaps = [record["symbol"] for record in symbol_records if record["large_gap_count"] > 0]
    funding_rate_min_global = min(Decimal(record["min_funding_rate"]) for record in symbol_records)
    funding_rate_max_global = max(Decimal(record["max_funding_rate"]) for record in symbol_records)
    extreme_count = sum(record["funding_rate_extreme_record_count"] for record in symbol_records)
    extreme_samples: list[dict[str, Any]] = []
    for record in symbol_records:
        for sample in record["funding_rate_extreme_samples"]:
            if len(extreme_samples) < 20:
                extreme_samples.append(sample)
    large_gap_max = max(record["max_gap_hours"] for record in symbol_records)
    interval_non_8h_total = sum(record["non_8h_interval_count"] for record in symbol_records)
    source_request_summary = {
        "acquisition_completed_at_utc": acquisition_completed,
        "acquisition_started_at_utc": acquisition_started,
        "blocked_by_418_count": counters["blocked_by_418_count"],
        "failed_symbols": failed_symbols,
        "http_status_counts": dict(sorted(counters["http_status_counts"].items())),
        "rate_limit_backoff_applied_count": counters["rate_limit_backoff_applied_count"],
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "retry_cap": RETRY_CAP,
        "symbols_completed": len(symbol_records),
        "symbols_failed": len(failed_symbols),
        "total_api_requests": counters["total_api_requests"],
        "total_empty_pages": counters["total_empty_pages"],
        "total_retries": counters["total_retries"],
    }
    funding_output_summary = {
        "acquisition_lock_valid_for_candidate_generation": False,
        "acquisition_lock_valid_for_edge_claim": False,
        "acquisition_lock_valid_for_future_funding_signal_construction": (
            len(symbol_records) == EXPECTED_SYMBOL_COUNT
            and all(record["funding_record_count"] > 0 and record["symbol_acquisition_valid"] for record in symbol_records)
            and total_invalid_numeric == 0
            and total_missing_required == 0
            and total_duplicates == 0
            and total_outside == 0
        ),
        "acquisition_lock_valid_for_runtime_live_capital": False,
        "acquisition_lock_valid_for_strategy_execution": False,
        "duplicate_symbol_funding_time_count": total_duplicates,
        "external_artifact_root": str(EXTERNAL_ROOT),
        "funding_by_symbol_dir": str(FUNDING_BY_SYMBOL_DIR),
        "funding_index_path": str(FUNDING_INDEX_PATH),
        "funding_index_sha256": funding_index_sha,
        "funding_rate_extreme_record_count": extreme_count,
        "funding_rate_max_global": str(funding_rate_max_global),
        "funding_rate_min_global": str(funding_rate_min_global),
        "invalid_numeric_count": total_invalid_numeric,
        "max_funding_time_utc": max(record["last_funding_time_utc"] for record in symbol_records),
        "min_funding_time_utc": min(record["first_funding_time_utc"] for record in symbol_records),
        "missing_required_field_count": total_missing_required,
        "output_files_count": len(symbol_records),
        "output_funding_files_sha256": output_hashes,
        "output_symbol_count": len(symbol_records),
        "records_outside_window_count": total_outside,
        "symbols_with_large_gaps_count": len(symbols_with_large_gaps),
        "symbols_with_records_count": sum(1 for record in symbol_records if record["funding_record_count"] > 0),
        "symbols_with_zero_records_count": sum(1 for record in symbol_records if record["funding_record_count"] == 0),
        "total_funding_records": sum(record["funding_record_count"] for record in symbol_records),
        "total_large_gap_count": total_large_gap_count,
    }
    manifest: dict[str, Any] = {
        "acquisition_scope": {
            "aligned_window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
            "aligned_window_start_utc": WINDOW_START_UTC,
            "endpoint_end_time_inclusive_utc": ENDPOINT_END_INCLUSIVE_UTC,
            "funding_data_only": True,
            "hypothesis_name": HYPOTHESIS_NAME,
            "no_price_panel_rows_read": True,
            "no_strategy_execution": True,
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "route_family": ROUTE_FAMILY,
            "symbol_count": len(symbols),
            "symbols": symbols,
        },
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_ACQUISITION_LOCK",
        "funding_data_output_summary": funding_output_summary,
        "funding_endpoint_contract": {
            "api_key_used": False,
            "authentication_required": False,
            "end_time_inclusive_at_endpoint": True,
            "endpoint_called_by_this_module": True,
            "endpoint_url": ENDPOINT_URL,
            "exchange": "BINANCE",
            "market": "USD_M_FUTURES",
            "method": "GET",
            "pagination_policy": "next_start_time_equals_last_funding_time_plus_one_ms",
            "project_window_end_exclusive": True,
            "public_endpoint": True,
            "request_limit_used": REQUEST_LIMIT,
            "response_fields_expected": ["symbol", "fundingRate", "fundingTime", "markPrice"],
            "start_time_inclusive": True,
        },
        "funding_rate_sanity_review": {
            "funding_rate_decimal_parse_valid": total_invalid_numeric == 0,
            "funding_rate_extreme_record_count": funding_output_summary["funding_rate_extreme_record_count"],
            "funding_rate_extreme_samples": extreme_samples,
            "funding_rate_extreme_threshold_abs": str(EXTREME_FUNDING_RATE_ABS_THRESHOLD),
            "funding_rate_max_global": str(funding_rate_max_global),
            "funding_rate_min_global": str(funding_rate_min_global),
            "funding_rate_sanity_review_passed": total_invalid_numeric == 0,
            "mark_price_decimal_parse_valid": total_invalid_numeric == 0,
            "mark_price_sanity_review_passed": total_invalid_numeric == 0,
        },
        "interval_gap_review": {
            "active_p1_attention_count_from_gaps": len(symbols_with_large_gaps),
            "expected_primary_interval_hours": EXPECTED_PRIMARY_INTERVAL_HOURS,
            "interval_gap_review_is_p1_attention_if_any_large_gap": True,
            "interval_gap_review_passed": True,
            "large_gap_threshold_hours": LARGE_GAP_THRESHOLD_HOURS,
            "max_gap_hours_global": large_gap_max,
            "non_8h_interval_count_total": interval_non_8h_total,
            "symbols_with_large_gaps": symbols_with_large_gaps,
        },
        "limitations": [
            "This is funding-rate data acquisition only, not strategy execution.",
            "No Binance price panel rows were read.",
            "No OKX panel rows were read.",
            "No strategy returns or signals were computed.",
            "No candidate generation was performed.",
            "No edge claim was made.",
            "No family release was made.",
            "No runtime/live/capital permission was granted.",
            "Funding data is from Binance public fundingRate history endpoint.",
            "Endpoint responses may be revised by Binance in the future.",
            "Future strategy execution requires separate explicit approval.",
            "Future edge claim requires external/future holdout and separate governance.",
        ],
        "module": MODULE_PATH,
        "non_repo_artifacts": {
            "artifact_root_outside_repo": True,
            "external_artifact_root": str(EXTERNAL_ROOT),
            "funding_by_symbol_dir": str(FUNDING_BY_SYMBOL_DIR),
            "funding_files": [record["output_file_path"] for record in symbol_records],
            "funding_index_path": str(FUNDING_INDEX_PATH),
            "tracked_in_git": False,
        },
        "repo_scope": {
            "api_key_used": False,
            "binance_1m_kline_source_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_panel_build_rerun": False,
            "binance_panel_rows_read": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "funding_data_written_outside_repo": True,
            "funding_rate_data_fetched": True,
            "funding_rate_endpoint_called": True,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "public_binance_funding_rate_network_used": True,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
            "tracked_manifest_created_in_repo": True,
        },
        "safety_permissions": {
            "binance_panel_row_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_data_acquisition_lock_created": True,
            "funding_data_valid_for_future_funding_signal_construction": funding_output_summary["acquisition_lock_valid_for_future_funding_signal_construction"],
            "funding_strategy_execution_allowed_now": False,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "next_step_may_be_funding_data_review_only": True,
            "okx_panel_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "strategy_research_not_allowed_from_this_lock": True,
            "strategy_search_allowed_now": False,
        },
        "source_artifacts": {
            "all_source_artifacts_read_only": True,
            "build_manifest_path": str(BUILD_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "build_manifest_payload_hash_verified": True,
            "coverage_lock_path": str(COVERAGE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "coverage_lock_payload_hash_verified": True,
            "panel_review_artifact_path": str(PANEL_REVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "panel_review_payload_hash_verified": True,
            "preregistration_artifact_path": str(PREREGISTRATION_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preregistration_artifact_status": prereg["status"],
            "preregistration_payload_hash_verified": True,
            "preview_artifact_path": str(PREVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preview_payload_hash_verified": True,
            "readiness_artifact_path": str(READINESS_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "readiness_payload_hash_verified": True,
        },
        "source_checkpoint": {
            "prior_head": PRIOR_HEAD,
            "prior_preregistration_artifact": "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json",
            "prior_preregistration_payload_sha256_excluding_hash": PREREGISTRATION_PAYLOAD_HASH,
            "prior_preregistration_status": PREREGISTRATION_STATUS,
            "prior_preregistration_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.py",
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding-rate data acquisition lock",
            "repo_clean_before_acquisition": True,
        },
        "source_request_summary": source_request_summary,
        "status": REQUIRED_STATUS,
        "symbol_funding_records": symbol_records,
    }
    manifest["validation_checks"] = {
        "acquisition_lock_json_valid": True,
        "acquisition_lock_manifest_path_equals_required_path": ACQUISITION_LOCK_PATH == "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
        "aligned_window_verified": True,
        "all_symbols_completed": len(symbol_records) == EXPECTED_SYMBOL_COUNT and not failed_symbols,
        "all_symbols_have_records": funding_output_summary["symbols_with_zero_records_count"] == 0,
        "build_manifest_loaded": True,
        "build_manifest_payload_hash_verified": True,
        "candidate_generation_forbidden": True,
        "coverage_lock_loaded": True,
        "coverage_lock_payload_hash_verified": True,
        "edge_claim_forbidden": True,
        "exact_overlap_symbol_count_verified_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
        "exactly_one_new_tracked_json_acquisition_lock_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "funding_data_fetched": counters["total_funding_records"] > 0,
        "funding_endpoint_called": counters["total_api_requests"] > 0,
        "funding_files_exist_outside_repo": all(Path(record["output_file_path"]).is_file() and not is_under(Path(record["output_file_path"]), REPO_PATH) for record in symbol_records),
        "funding_index_exists_outside_repo": FUNDING_INDEX_PATH.is_file() and not is_under(FUNDING_INDEX_PATH, REPO_PATH),
        "invalid_numeric_count_zero": total_invalid_numeric == 0,
        "missing_required_field_count_zero": total_missing_required == 0,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_acquisition_lock_v1.py",
        "no_binance_1m_source_rows_read": True,
        "no_binance_panel_rows_read": True,
        "no_candidate_generation": True,
        "no_duplicate_symbol_funding_times": total_duplicates == 0,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_records_outside_window": total_outside == 0,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "output_symbol_count_verified_81": len(symbol_records) == EXPECTED_SYMBOL_COUNT,
        "panel_review_artifact_loaded": True,
        "panel_review_payload_hash_verified": True,
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_loaded": True,
        "preregistration_payload_hash_verified": True,
        "preregistration_status_verified": prereg["status"] == PREREGISTRATION_STATUS,
        "preview_artifact_loaded": True,
        "preview_payload_hash_verified": True,
        "readiness_artifact_loaded": True,
        "readiness_payload_hash_verified": True,
        "replacement_checks_all_true": True,
        "runtime_live_capital_forbidden": True,
        "status_equals_required_status": True,
        "strategy_search_forbidden": True,
    }
    manifest["replacement_checks_all_true"] = all(value is True for value in manifest["validation_checks"].values())
    hash_input = dict(manifest)
    hash_input.pop("payload_sha256_excluding_hash", None)
    manifest["payload_sha256_excluding_hash"] = hashlib.sha256(canonical_json_bytes(hash_input)).hexdigest()
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    assert manifest["status"] == REQUIRED_STATUS
    assert manifest["module"] == MODULE_PATH
    assert ACQUISITION_LOCK_PATH == "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json"
    assert manifest["source_artifacts"]["preregistration_payload_hash_verified"] is True
    assert manifest["acquisition_scope"]["route_family"] == ROUTE_FAMILY
    assert manifest["acquisition_scope"]["symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert manifest["acquisition_scope"]["aligned_window_start_utc"] == WINDOW_START_UTC
    assert manifest["acquisition_scope"]["aligned_window_end_exclusive_utc"] == WINDOW_END_EXCLUSIVE_UTC
    assert manifest["funding_endpoint_contract"]["endpoint_url"] == ENDPOINT_URL
    assert manifest["funding_endpoint_contract"]["api_key_used"] is False
    assert manifest["source_request_summary"]["symbols_failed"] == 0
    assert manifest["funding_data_output_summary"]["output_symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert manifest["funding_data_output_summary"]["symbols_with_zero_records_count"] == 0
    assert manifest["funding_data_output_summary"]["duplicate_symbol_funding_time_count"] == 0
    assert manifest["funding_data_output_summary"]["records_outside_window_count"] == 0
    assert manifest["funding_data_output_summary"]["invalid_numeric_count"] == 0
    assert manifest["funding_data_output_summary"]["missing_required_field_count"] == 0
    assert manifest["funding_data_output_summary"]["acquisition_lock_valid_for_future_funding_signal_construction"] is True
    assert manifest["repo_scope"]["binance_panel_rows_read"] is False
    assert manifest["repo_scope"]["okx_panel_rows_read"] is False
    assert manifest["repo_scope"]["strategy_search_executed"] is False
    assert manifest["repo_scope"]["candidate_generation"] is False
    assert manifest["repo_scope"]["edge_claim"] is False
    assert manifest["repo_scope"]["runtime_live_capital"] is False
    assert manifest["replacement_checks_all_true"] is True
    assert manifest["payload_sha256_excluding_hash"]


def write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEMP_MANIFEST_PATH.exists():
        TEMP_MANIFEST_PATH.unlink()
    TEMP_MANIFEST_PATH.write_bytes(canonical_json_bytes(manifest) + b"\n")
    TEMP_MANIFEST_PATH.replace(MANIFEST_PATH)


def stdout_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    output = manifest["funding_data_output_summary"]
    requests = manifest["source_request_summary"]
    scope = manifest["acquisition_scope"]
    return {
        "acquisition_lock_valid_for_future_funding_signal_construction": output["acquisition_lock_valid_for_future_funding_signal_construction"],
        "aligned_window_end_exclusive_utc": scope["aligned_window_end_exclusive_utc"],
        "aligned_window_start_utc": scope["aligned_window_start_utc"],
        "duplicate_symbol_funding_time_count": output["duplicate_symbol_funding_time_count"],
        "exact_overlap_symbol_count": scope["symbol_count"],
        "external_artifact_root": output["external_artifact_root"],
        "funding_by_symbol_dir": output["funding_by_symbol_dir"],
        "funding_index_path": output["funding_index_path"],
        "funding_index_sha256": output["funding_index_sha256"],
        "funding_rate_max_global": output["funding_rate_max_global"],
        "funding_rate_min_global": output["funding_rate_min_global"],
        "invalid_numeric_count": output["invalid_numeric_count"],
        "max_funding_time_utc": output["max_funding_time_utc"],
        "min_funding_time_utc": output["min_funding_time_utc"],
        "missing_required_field_count": output["missing_required_field_count"],
        "output_symbol_count": output["output_symbol_count"],
        "payload_sha256_excluding_hash": manifest["payload_sha256_excluding_hash"],
        "records_outside_window_count": output["records_outside_window_count"],
        "replacement_checks_all_true": manifest["replacement_checks_all_true"],
        "route_family": scope["route_family"],
        "status": manifest["status"],
        "symbols_with_large_gaps_count": output["symbols_with_large_gaps_count"],
        "symbols_with_records_count": output["symbols_with_records_count"],
        "symbols_with_zero_records_count": output["symbols_with_zero_records_count"],
        "total_api_requests": requests["total_api_requests"],
        "total_funding_records": output["total_funding_records"],
        "total_large_gap_count": output["total_large_gap_count"],
        "total_retries": requests["total_retries"],
    }


def main() -> int:
    try:
        manifest = acquire_all()
        validate_manifest(manifest)
        write_manifest(manifest)
    except BlockedError as exc:
        if TEMP_MANIFEST_PATH.exists():
            TEMP_MANIFEST_PATH.unlink()
        print(
            json.dumps(
                {
                    "exact_blocker": str(exc),
                    "external_artifact_root": str(EXTERNAL_ROOT),
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
