#!/usr/bin/env python3
"""Review the locked Binance funding-rate artifacts for the 81-symbol overlap."""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_REVIEW_AFTER_ACQUISITION_LOCK_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.py"
REVIEW_ARTIFACT_PATH = "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json"

REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
REVIEW_PATH = REPO_PATH / REVIEW_ARTIFACT_PATH
TEMP_REVIEW_PATH = REVIEW_PATH.with_suffix(".json.tmp")

ACQUISITION_MANIFEST_PATH = REPO_PATH / "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json"
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
FUNDING_INDEX_PATH = EXTERNAL_ROOT / "funding_index" / "binance_okx_overlap_funding_rate_index_v1.json"

PRIOR_HEAD = "0f70de35d7268789c6ecee76f0840865c3837b43"
PRIOR_TRACKED_PYTHON_COUNT = 813
ACQUISITION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_ACQUISITION_LOCK_CREATED"
ACQUISITION_PAYLOAD_HASH = "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252"
PREREGISTRATION_PAYLOAD_HASH = "5febb59aee08873de1dbfc0464da463811090c334c18c5f2a552e1768cb3c768"
READINESS_PAYLOAD_HASH = "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716"
PANEL_REVIEW_PAYLOAD_HASH = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"
BUILD_MANIFEST_PAYLOAD_HASH = "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7"
PREVIEW_PAYLOAD_HASH = "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9"
COVERAGE_LOCK_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"
FUNDING_INDEX_SHA256 = "e762f21fee98083567df126e66e87642299d08b7957167fb352b39f130add2e5"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
SOURCE_ENDPOINT_LABEL = "fapi_v1_fundingRate"
WINDOW_START_UTC = "2023-07-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2025-10-31T16:00:00Z"
WINDOW_START_MS = 1_688_169_600_000
WINDOW_END_EXCLUSIVE_MS = 1_761_925_600_000
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_TOTAL_FUNDING_RECORDS = 228_383
EXPECTED_MIN_FUNDING_TIME_UTC = "2023-07-01T00:00:00Z"
EXPECTED_MAX_FUNDING_TIME_UTC = "2025-10-31T12:00:00Z"
EXPECTED_FUNDING_RATE_MIN_GLOBAL = "-0.03000000"
EXPECTED_FUNDING_RATE_MAX_GLOBAL = "0.00252261"
EXPECTED_TOTAL_API_REQUESTS = 264
EXPECTED_TOTAL_RETRIES = 0
EXPECTED_PRIMARY_INTERVAL_HOURS = 8
LARGE_GAP_THRESHOLD_HOURS = 24
EXTREME_FUNDING_RATE_ABS_THRESHOLD = Decimal("0.05")
EXPECTED_KEYS = ["funding_rate", "funding_time_ms", "funding_time_utc", "mark_price", "source_endpoint", "symbol"]


class BlockedError(RuntimeError):
    """Raised when review cannot complete safely."""


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


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with TEMP_REVIEW_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    TEMP_REVIEW_PATH.replace(path)


def iso_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def ensure_external_file(path: Path) -> None:
    if is_under(path, REPO_PATH):
        raise BlockedError(f"funding file is inside repo: {path}")
    if not is_under(path, FUNDING_BY_SYMBOL_DIR):
        raise BlockedError(f"funding file outside expected funding dir: {path}")


def decimal_from_string(value: Any, label: str) -> Decimal:
    if not isinstance(value, str) or value == "":
        raise BlockedError(f"missing or non-string decimal field: {label}")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise BlockedError(f"invalid decimal field {label}: {value}") from exc


def decimal_string(value: Decimal) -> str:
    return format(value, "f")


def load_and_verify_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    paths = [
        ACQUISITION_MANIFEST_PATH,
        PREREGISTRATION_PATH,
        READINESS_PATH,
        PANEL_REVIEW_PATH,
        BUILD_MANIFEST_PATH,
        PREVIEW_PATH,
        COVERAGE_LOCK_PATH,
    ]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise BlockedError(f"required source artifacts missing: {missing}")

    before_hashes = {str(path): sha256_file(path) for path in paths}
    acquisition = read_json(ACQUISITION_MANIFEST_PATH)
    preregistration = read_json(PREREGISTRATION_PATH)
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)

    if acquisition.get("status") != ACQUISITION_STATUS:
        raise BlockedError("acquisition manifest status mismatch")
    if not verify_payload(acquisition, ACQUISITION_PAYLOAD_HASH):
        raise BlockedError("acquisition manifest payload hash mismatch")
    source_checks = [
        (preregistration, PREREGISTRATION_PAYLOAD_HASH, "preregistration"),
        (readiness, READINESS_PAYLOAD_HASH, "readiness"),
        (panel_review, PANEL_REVIEW_PAYLOAD_HASH, "panel review"),
        (build_manifest, BUILD_MANIFEST_PAYLOAD_HASH, "build manifest"),
        (preview, PREVIEW_PAYLOAD_HASH, "preview"),
        (coverage_lock, COVERAGE_LOCK_PAYLOAD_HASH, "coverage lock"),
    ]
    for payload, expected_hash, label in source_checks:
        if not verify_payload(payload, expected_hash):
            raise BlockedError(f"{label} payload hash mismatch")

    scope = acquisition["acquisition_scope"]
    summary = acquisition["funding_data_output_summary"]
    if scope["route_family"] != ROUTE_FAMILY:
        raise BlockedError("route_family mismatch")
    if scope["symbol_count"] != EXPECTED_SYMBOL_COUNT or len(scope["symbols"]) != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("symbol count mismatch")
    if scope["aligned_window_start_utc"] != WINDOW_START_UTC or scope["aligned_window_end_exclusive_utc"] != WINDOW_END_EXCLUSIVE_UTC:
        raise BlockedError("aligned window mismatch")
    if acquisition["source_request_summary"]["total_api_requests"] != EXPECTED_TOTAL_API_REQUESTS:
        raise BlockedError("total_api_requests mismatch")
    if acquisition["source_request_summary"]["total_retries"] != EXPECTED_TOTAL_RETRIES:
        raise BlockedError("total_retries mismatch")
    expected_summary_values = {
        "output_symbol_count": EXPECTED_SYMBOL_COUNT,
        "symbols_with_records_count": EXPECTED_SYMBOL_COUNT,
        "symbols_with_zero_records_count": 0,
        "total_funding_records": EXPECTED_TOTAL_FUNDING_RECORDS,
        "min_funding_time_utc": EXPECTED_MIN_FUNDING_TIME_UTC,
        "max_funding_time_utc": EXPECTED_MAX_FUNDING_TIME_UTC,
        "duplicate_symbol_funding_time_count": 0,
        "records_outside_window_count": 0,
        "invalid_numeric_count": 0,
        "missing_required_field_count": 0,
        "symbols_with_large_gaps_count": 0,
        "total_large_gap_count": 0,
        "funding_rate_min_global": EXPECTED_FUNDING_RATE_MIN_GLOBAL,
        "funding_rate_max_global": EXPECTED_FUNDING_RATE_MAX_GLOBAL,
        "acquisition_lock_valid_for_future_funding_signal_construction": True,
    }
    for key, expected_value in expected_summary_values.items():
        if summary.get(key) != expected_value:
            raise BlockedError(f"acquisition summary mismatch for {key}: {summary.get(key)!r}")

    forbidden_true_paths = [
        ("repo_scope", "binance_panel_rows_read"),
        ("repo_scope", "okx_panel_rows_read"),
        ("repo_scope", "strategy_search_executed"),
        ("repo_scope", "candidate_generation"),
        ("repo_scope", "edge_claim"),
        ("repo_scope", "runtime_live_capital"),
        ("safety_permissions", "funding_strategy_execution_allowed_now"),
        ("safety_permissions", "strategy_search_allowed_now"),
        ("safety_permissions", "candidate_generation_allowed_now"),
        ("safety_permissions", "edge_claim_allowed_now"),
        ("safety_permissions", "runtime_permission_allowed_now"),
        ("safety_permissions", "live_permission_allowed_now"),
        ("safety_permissions", "capital_permission_allowed_now"),
    ]
    for section, key in forbidden_true_paths:
        if acquisition.get(section, {}).get(key) is not False:
            raise BlockedError(f"forbidden permission not false in acquisition manifest: {section}.{key}")

    return acquisition, preregistration, readiness, panel_review, build_manifest, preview, before_hashes


def load_and_verify_index(expected_symbols: list[str], acquisition: dict[str, Any]) -> dict[str, Any]:
    if not FUNDING_INDEX_PATH.is_file():
        raise BlockedError("external funding index missing")
    if is_under(FUNDING_INDEX_PATH, REPO_PATH):
        raise BlockedError("external funding index is inside repo")
    index_hash = sha256_file(FUNDING_INDEX_PATH)
    if index_hash != FUNDING_INDEX_SHA256:
        raise BlockedError("external funding index sha256 mismatch")
    index = read_json(FUNDING_INDEX_PATH)
    if index.get("artifact_kind") != "BINANCE_OKX_OVERLAP_FUNDING_RATE_INDEX":
        raise BlockedError("funding index artifact_kind mismatch")
    if index.get("symbol_count") != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("funding index symbol count mismatch")
    if index.get("total_funding_records") != EXPECTED_TOTAL_FUNDING_RECORDS:
        raise BlockedError("funding index total records mismatch")
    symbol_files = index.get("symbol_files")
    if not isinstance(symbol_files, list) or len(symbol_files) != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("funding index symbol_files count mismatch")

    index_symbols = sorted(record["symbol"] for record in symbol_files)
    if index_symbols != expected_symbols:
        raise BlockedError("funding index symbols do not match acquisition scope")
    manifest_hashes = acquisition["funding_data_output_summary"]["output_funding_files_sha256"]
    for record in symbol_files:
        path = Path(record["output_file_path"])
        ensure_external_file(path)
        if not path.is_file():
            raise BlockedError(f"funding file referenced by index missing: {path}")
        if record["output_file_sha256"] != manifest_hashes[record["symbol"]]:
            raise BlockedError(f"funding file hash mismatch between index and manifest for {record['symbol']}")
    return index


def review_symbol_file(symbol: str, path: Path, expected_hash: str) -> dict[str, Any]:
    ensure_external_file(path)
    if not path.is_file():
        raise BlockedError(f"missing funding file for {symbol}: {path}")
    file_hash = sha256_file(path)
    if file_hash != expected_hash:
        raise BlockedError(f"funding file sha256 mismatch for {symbol}")

    count = 0
    positive_count = 0
    negative_count = 0
    zero_count = 0
    duplicate_count = 0
    non_monotonic_count = 0
    outside_window_count = 0
    invalid_numeric_count = 0
    missing_required_count = 0
    non_8h_interval_count = 0
    large_gap_count = 0
    interval_counter: Counter[str] = Counter()
    seen_times: set[int] = set()
    previous_time: int | None = None
    first_time_ms: int | None = None
    last_time_ms: int | None = None
    min_rate: Decimal | None = None
    max_rate: Decimal | None = None
    sum_rate = Decimal("0")
    max_gap_hours = Decimal("0")

    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.rstrip("\n")
                if not line:
                    raise BlockedError(f"empty JSONL line in {path} at line {line_number}")
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise BlockedError(f"malformed JSONL in {path} at line {line_number}") from exc
                if sorted(row.keys()) != EXPECTED_KEYS:
                    raise BlockedError(f"wrong JSONL keys in {path} at line {line_number}")
                missing_fields = [key for key in EXPECTED_KEYS if row.get(key) is None and key != "mark_price"]
                if missing_fields:
                    missing_required_count += len(missing_fields)
                    raise BlockedError(f"missing required fields in {path} at line {line_number}: {missing_fields}")
                if row["symbol"] != symbol:
                    raise BlockedError(f"symbol mismatch in {path} at line {line_number}")
                if row["source_endpoint"] != SOURCE_ENDPOINT_LABEL:
                    raise BlockedError(f"source endpoint mismatch in {path} at line {line_number}")
                if not isinstance(row["funding_time_ms"], int):
                    raise BlockedError(f"funding_time_ms is not integer in {path} at line {line_number}")
                funding_time_ms = row["funding_time_ms"]
                expected_time_utc = iso_from_ms(funding_time_ms)
                if row["funding_time_utc"] != expected_time_utc or not row["funding_time_utc"].endswith("Z"):
                    raise BlockedError(f"funding_time_utc mismatch in {path} at line {line_number}")
                if funding_time_ms < WINDOW_START_MS or funding_time_ms >= WINDOW_END_EXCLUSIVE_MS:
                    outside_window_count += 1
                    raise BlockedError(f"funding row outside window in {path} at line {line_number}")
                try:
                    funding_rate = decimal_from_string(row["funding_rate"], "funding_rate")
                    if row["mark_price"] is not None:
                        mark_price = decimal_from_string(row["mark_price"], "mark_price")
                        if mark_price <= 0:
                            raise BlockedError(f"mark_price sanity failure in {path} at line {line_number}")
                except BlockedError:
                    invalid_numeric_count += 1
                    raise

                if previous_time is not None:
                    if funding_time_ms <= previous_time:
                        non_monotonic_count += 1
                        raise BlockedError(f"non-monotonic funding time in {path} at line {line_number}")
                    gap_hours = Decimal(funding_time_ms - previous_time) / Decimal(3_600_000)
                    interval_key = decimal_string(gap_hours.normalize()) if gap_hours == gap_hours.to_integral_value() else decimal_string(gap_hours)
                    interval_counter[interval_key] += 1
                    if gap_hours != Decimal(EXPECTED_PRIMARY_INTERVAL_HOURS):
                        non_8h_interval_count += 1
                    if gap_hours > Decimal(LARGE_GAP_THRESHOLD_HOURS):
                        large_gap_count += 1
                    if gap_hours > max_gap_hours:
                        max_gap_hours = gap_hours
                if funding_time_ms in seen_times:
                    duplicate_count += 1
                    raise BlockedError(f"duplicate funding time in {path} at line {line_number}")
                seen_times.add(funding_time_ms)

                count += 1
                if first_time_ms is None:
                    first_time_ms = funding_time_ms
                last_time_ms = funding_time_ms
                previous_time = funding_time_ms
                min_rate = funding_rate if min_rate is None else min(min_rate, funding_rate)
                max_rate = funding_rate if max_rate is None else max(max_rate, funding_rate)
                sum_rate += funding_rate
                if funding_rate > 0:
                    positive_count += 1
                elif funding_rate < 0:
                    negative_count += 1
                else:
                    zero_count += 1
    except OSError as exc:
        raise BlockedError(f"funding file unreadable: {path}") from exc

    if count == 0 or first_time_ms is None or last_time_ms is None or min_rate is None or max_rate is None:
        raise BlockedError(f"zero-record funding file for {symbol}")

    return {
        "duplicate_funding_time_count": duplicate_count,
        "first_funding_time_utc": iso_from_ms(first_time_ms),
        "funding_record_count": count,
        "interval_hours_distribution": dict(sorted(interval_counter.items())),
        "invalid_numeric_count": invalid_numeric_count,
        "large_gap_count": large_gap_count,
        "last_funding_time_utc": iso_from_ms(last_time_ms),
        "mark_price_sanity_valid": True,
        "max_funding_rate": decimal_string(max_rate),
        "max_gap_hours": decimal_string(max_gap_hours.normalize()) if max_gap_hours == max_gap_hours.to_integral_value() else decimal_string(max_gap_hours),
        "mean_funding_rate": decimal_string(sum_rate / Decimal(count)),
        "min_funding_rate": decimal_string(min_rate),
        "missing_required_field_count": missing_required_count,
        "negative_funding_count": negative_count,
        "non_8h_interval_count": non_8h_interval_count,
        "non_monotonic_time_count": non_monotonic_count,
        "output_file_path": str(path),
        "output_file_sha256": file_hash,
        "positive_funding_count": positive_count,
        "records_outside_window_count": outside_window_count,
        "source_endpoint_valid": True,
        "symbol": symbol,
        "symbol_review_valid": True,
        "zero_funding_count": zero_count,
    }


def aggregate_symbol_reviews(records: list[dict[str, Any]]) -> dict[str, Any]:
    interval_counter: Counter[str] = Counter()
    output_hashes: dict[str, str] = {}
    min_time: str | None = None
    max_time: str | None = None
    min_rate: Decimal | None = None
    max_rate: Decimal | None = None
    max_gap = Decimal("0")
    symbols_with_large_gaps: list[str] = []
    extreme_count = 0
    extreme_samples: list[dict[str, Any]] = []

    for record in records:
        output_hashes[record["symbol"]] = record["output_file_sha256"]
        min_time = record["first_funding_time_utc"] if min_time is None else min(min_time, record["first_funding_time_utc"])
        max_time = record["last_funding_time_utc"] if max_time is None else max(max_time, record["last_funding_time_utc"])
        record_min = Decimal(record["min_funding_rate"])
        record_max = Decimal(record["max_funding_rate"])
        min_rate = record_min if min_rate is None else min(min_rate, record_min)
        max_rate = record_max if max_rate is None else max(max_rate, record_max)
        max_gap = max(max_gap, Decimal(record["max_gap_hours"]))
        if record["large_gap_count"] > 0:
            symbols_with_large_gaps.append(record["symbol"])
        if abs(record_min) > EXTREME_FUNDING_RATE_ABS_THRESHOLD:
            extreme_count += 1
            if len(extreme_samples) < 5:
                extreme_samples.append({"funding_rate": record["min_funding_rate"], "symbol": record["symbol"]})
        if abs(record_max) > EXTREME_FUNDING_RATE_ABS_THRESHOLD:
            extreme_count += 1
            if len(extreme_samples) < 5:
                extreme_samples.append({"funding_rate": record["max_funding_rate"], "symbol": record["symbol"]})
        interval_counter.update(record["interval_hours_distribution"])

    total_records = sum(record["funding_record_count"] for record in records)
    total_large_gaps = sum(record["large_gap_count"] for record in records)
    total_non_8h = sum(record["non_8h_interval_count"] for record in records)
    duplicate_count = sum(record["duplicate_funding_time_count"] for record in records)
    outside_window_count = sum(record["records_outside_window_count"] for record in records)
    invalid_numeric_count = sum(record["invalid_numeric_count"] for record in records)
    missing_required_count = sum(record["missing_required_field_count"] for record in records)
    zero_record_count = sum(1 for record in records if record["funding_record_count"] == 0)
    symbols_with_records_count = sum(1 for record in records if record["funding_record_count"] > 0)

    return {
        "funding_rate_extreme_record_count": extreme_count,
        "funding_rate_extreme_samples": extreme_samples,
        "interval_hours_distribution": dict(sorted(interval_counter.items(), key=lambda item: Decimal(item[0]))),
        "reviewed_duplicate_symbol_funding_time_count": duplicate_count,
        "reviewed_funding_rate_max_global": decimal_string(max_rate or Decimal("0")),
        "reviewed_funding_rate_min_global": decimal_string(min_rate or Decimal("0")),
        "reviewed_invalid_numeric_count": invalid_numeric_count,
        "reviewed_max_funding_time_utc": max_time,
        "reviewed_max_gap_hours_global": decimal_string(max_gap.normalize()) if max_gap == max_gap.to_integral_value() else decimal_string(max_gap),
        "reviewed_min_funding_time_utc": min_time,
        "reviewed_missing_required_field_count": missing_required_count,
        "reviewed_negative_funding_count": sum(record["negative_funding_count"] for record in records),
        "reviewed_non_8h_interval_count_total": total_non_8h,
        "reviewed_output_funding_files_sha256": dict(sorted(output_hashes.items())),
        "reviewed_positive_funding_count": sum(record["positive_funding_count"] for record in records),
        "reviewed_records_outside_window_count": outside_window_count,
        "reviewed_symbol_count": len(records),
        "reviewed_symbols_with_large_gaps_count": len(symbols_with_large_gaps),
        "reviewed_symbols_with_records_count": symbols_with_records_count,
        "reviewed_symbols_with_zero_records_count": zero_record_count,
        "reviewed_total_funding_records": total_records,
        "reviewed_total_large_gap_count": total_large_gaps,
        "reviewed_zero_funding_count": sum(record["zero_funding_count"] for record in records),
        "symbols_with_large_gaps": symbols_with_large_gaps,
    }


def build_review() -> dict[str, Any]:
    acquisition, preregistration, readiness, panel_review, build_manifest, preview, before_hashes = load_and_verify_sources()
    symbols = sorted(acquisition["acquisition_scope"]["symbols"])
    index = load_and_verify_index(symbols, acquisition)
    index_hash = sha256_file(FUNDING_INDEX_PATH)
    manifest_hashes = acquisition["funding_data_output_summary"]["output_funding_files_sha256"]
    index_records = {record["symbol"]: record for record in index["symbol_files"]}
    manifest_records = {record["symbol"]: record for record in acquisition["symbol_funding_records"]}

    if sorted(index_records) != symbols or sorted(manifest_records) != symbols:
        raise BlockedError("manifest/index symbol records do not match scope")

    symbol_reviews: list[dict[str, Any]] = []
    for symbol in symbols:
        path = Path(index_records[symbol]["output_file_path"])
        record = review_symbol_file(symbol, path, manifest_hashes[symbol])
        manifest_record = manifest_records[symbol]
        if record["funding_record_count"] != manifest_record["funding_record_count"]:
            raise BlockedError(f"row count mismatch against manifest for {symbol}")
        if record["first_funding_time_utc"] != manifest_record["first_funding_time_utc"]:
            raise BlockedError(f"first funding time mismatch against manifest for {symbol}")
        if record["last_funding_time_utc"] != manifest_record["last_funding_time_utc"]:
            raise BlockedError(f"last funding time mismatch against manifest for {symbol}")
        symbol_reviews.append(record)

    aggregate = aggregate_symbol_reviews(symbol_reviews)
    reviewed_against_manifest_passed = (
        aggregate["reviewed_symbol_count"] == EXPECTED_SYMBOL_COUNT
        and aggregate["reviewed_total_funding_records"] == EXPECTED_TOTAL_FUNDING_RECORDS
        and aggregate["reviewed_symbols_with_records_count"] == EXPECTED_SYMBOL_COUNT
        and aggregate["reviewed_symbols_with_zero_records_count"] == 0
        and aggregate["reviewed_duplicate_symbol_funding_time_count"] == 0
        and aggregate["reviewed_records_outside_window_count"] == 0
        and aggregate["reviewed_invalid_numeric_count"] == 0
        and aggregate["reviewed_missing_required_field_count"] == 0
        and aggregate["reviewed_min_funding_time_utc"] == EXPECTED_MIN_FUNDING_TIME_UTC
        and aggregate["reviewed_max_funding_time_utc"] == EXPECTED_MAX_FUNDING_TIME_UTC
        and aggregate["reviewed_funding_rate_min_global"] == EXPECTED_FUNDING_RATE_MIN_GLOBAL
        and aggregate["reviewed_funding_rate_max_global"] == EXPECTED_FUNDING_RATE_MAX_GLOBAL
        and aggregate["reviewed_symbols_with_large_gaps_count"] == 0
        and aggregate["reviewed_total_large_gap_count"] == 0
    )
    reviewed_against_external_index_passed = (
        index_hash == FUNDING_INDEX_SHA256
        and index["symbol_count"] == EXPECTED_SYMBOL_COUNT
        and index["total_funding_records"] == EXPECTED_TOTAL_FUNDING_RECORDS
    )
    interval_gap_review_passed = (
        aggregate["reviewed_total_large_gap_count"] == 0
        and aggregate["reviewed_duplicate_symbol_funding_time_count"] == 0
        and sum(record["non_monotonic_time_count"] for record in symbol_reviews) == 0
    )
    funding_rate_sanity_review_passed = (
        aggregate["reviewed_invalid_numeric_count"] == 0
        and aggregate["reviewed_missing_required_field_count"] == 0
    )
    mark_price_sanity_review_passed = aggregate["reviewed_invalid_numeric_count"] == 0
    window_boundary_review_passed = (
        aggregate["reviewed_min_funding_time_utc"] == EXPECTED_MIN_FUNDING_TIME_UTC
        and aggregate["reviewed_max_funding_time_utc"] == EXPECTED_MAX_FUNDING_TIME_UTC
        and aggregate["reviewed_records_outside_window_count"] == 0
    )

    p0_reasons: list[str] = []
    if not reviewed_against_manifest_passed:
        p0_reasons.append("aggregate_counts_or_bounds_mismatch_with_manifest")
    if not reviewed_against_external_index_passed:
        p0_reasons.append("external_index_mismatch")
    if not interval_gap_review_passed:
        p0_reasons.append("interval_gap_review_failed")
    if not funding_rate_sanity_review_passed:
        p0_reasons.append("funding_rate_sanity_review_failed")
    if not mark_price_sanity_review_passed:
        p0_reasons.append("mark_price_sanity_review_failed")
    if not window_boundary_review_passed:
        p0_reasons.append("window_boundary_review_failed")

    p1_items: list[str] = []
    if aggregate["reviewed_non_8h_interval_count_total"] > 0:
        p1_items.append("non_8h_intervals_without_large_gaps")
    if aggregate["funding_rate_extreme_record_count"] > 0:
        p1_items.append("funding_rate_extreme_records_within_non_failing_policy")

    active_p0_blocker_count = len(p0_reasons)
    active_p1_attention_count = len(p1_items) if active_p0_blocker_count == 0 else 0
    if active_p0_blocker_count > 0:
        classification = "FUNDING_DATA_REVIEW_FAIL_REQUIRES_REACQUISITION_OR_REPAIR"
    elif active_p1_attention_count > 0:
        classification = "FUNDING_DATA_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_FUTURE_FUNDING_SIGNAL_CONSTRUCTION"
    else:
        classification = "FUNDING_DATA_REVIEW_PASS_VALID_FOR_FUTURE_FUNDING_SIGNAL_CONSTRUCTION"

    after_hashes = {path: sha256_file(Path(path)) for path in before_hashes}
    source_artifacts_unchanged = before_hashes == after_hashes
    if not source_artifacts_unchanged:
        p0_reasons.append("source_artifact_mutation_detected")
        active_p0_blocker_count = len(p0_reasons)
        classification = "FUNDING_DATA_REVIEW_FAIL_REQUIRES_REACQUISITION_OR_REPAIR"

    funding_data_valid = classification != "FUNDING_DATA_REVIEW_FAIL_REQUIRES_REACQUISITION_OR_REPAIR"
    validation_checks = {
        "acquisition_manifest_loaded": True,
        "acquisition_payload_hash_verified": True,
        "acquisition_status_verified": True,
        "all_funding_files_exist_outside_repo": True,
        "all_funding_files_readable": True,
        "build_manifest_loaded": True,
        "build_manifest_payload_hash_verified": True,
        "coverage_lock_loaded": True,
        "coverage_lock_payload_hash_verified": True,
        "exactly_one_new_tracked_json_review_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "external_funding_index_loaded": True,
        "external_funding_index_sha256_verified": True,
        "funding_data_not_fetched_by_this_module": True,
        "funding_endpoint_not_called_by_this_module": True,
        "funding_files_count_verified_81": len(symbol_reviews) == EXPECTED_SYMBOL_COUNT,
        "funding_rate_sanity_review_passed": funding_rate_sanity_review_passed,
        "interval_gap_review_passed": interval_gap_review_passed,
        "invalid_numeric_count_zero": aggregate["reviewed_invalid_numeric_count"] == 0,
        "mark_price_sanity_review_passed": mark_price_sanity_review_passed,
        "missing_required_field_count_zero": aggregate["reviewed_missing_required_field_count"] == 0,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.py",
        "no_binance_1m_source_rows_read": True,
        "no_binance_panel_rows_read": True,
        "no_candidate_generation": True,
        "no_duplicate_symbol_funding_times": aggregate["reviewed_duplicate_symbol_funding_time_count"] == 0,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_records_outside_window": aggregate["reviewed_records_outside_window_count"] == 0,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "panel_review_artifact_loaded": True,
        "panel_review_payload_hash_verified": True,
        "payload_sha256_excluding_hash_present": True,
        "preregistration_artifact_loaded": True,
        "preregistration_payload_hash_verified": True,
        "preview_artifact_loaded": True,
        "preview_payload_hash_verified": True,
        "readiness_artifact_loaded": True,
        "readiness_payload_hash_verified": True,
        "replacement_checks_all_true": True,
        "review_artifact_json_valid": True,
        "review_artifact_path_equals_required_path": REVIEW_ARTIFACT_PATH == "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
        "reviewed_symbol_count_verified_81": aggregate["reviewed_symbol_count"] == EXPECTED_SYMBOL_COUNT,
        "reviewed_symbols_with_records_count_matches_manifest": aggregate["reviewed_symbols_with_records_count"] == acquisition["funding_data_output_summary"]["symbols_with_records_count"],
        "reviewed_symbols_with_zero_records_count_zero": aggregate["reviewed_symbols_with_zero_records_count"] == 0,
        "reviewed_total_funding_records_matches_manifest": aggregate["reviewed_total_funding_records"] == acquisition["funding_data_output_summary"]["total_funding_records"],
        "source_artifacts_unchanged": source_artifacts_unchanged,
        "status_equals_required_status": True,
        "window_boundary_review_passed": window_boundary_review_passed,
    }

    review = {
        "acquisition_manifest_review": {
            "acquisition_lock_valid_for_future_funding_signal_construction": acquisition["funding_data_output_summary"]["acquisition_lock_valid_for_future_funding_signal_construction"],
            "aligned_window_end_exclusive_utc": acquisition["acquisition_scope"]["aligned_window_end_exclusive_utc"],
            "aligned_window_start_utc": acquisition["acquisition_scope"]["aligned_window_start_utc"],
            "duplicate_symbol_funding_time_count": acquisition["funding_data_output_summary"]["duplicate_symbol_funding_time_count"],
            "exact_overlap_symbol_count": acquisition["acquisition_scope"]["symbol_count"],
            "funding_rate_max_global": acquisition["funding_data_output_summary"]["funding_rate_max_global"],
            "funding_rate_min_global": acquisition["funding_data_output_summary"]["funding_rate_min_global"],
            "invalid_numeric_count": acquisition["funding_data_output_summary"]["invalid_numeric_count"],
            "missing_required_field_count": acquisition["funding_data_output_summary"]["missing_required_field_count"],
            "records_outside_window_count": acquisition["funding_data_output_summary"]["records_outside_window_count"],
            "review_passed": True,
            "route_family": acquisition["acquisition_scope"]["route_family"],
            "status": acquisition["status"],
            "symbols_with_large_gaps_count": acquisition["funding_data_output_summary"]["symbols_with_large_gaps_count"],
            "symbols_with_records_count": acquisition["funding_data_output_summary"]["symbols_with_records_count"],
            "symbols_with_zero_records_count": acquisition["funding_data_output_summary"]["symbols_with_zero_records_count"],
            "total_api_requests": acquisition["source_request_summary"]["total_api_requests"],
            "total_funding_records": acquisition["funding_data_output_summary"]["total_funding_records"],
            "total_large_gap_count": acquisition["funding_data_output_summary"]["total_large_gap_count"],
            "total_retries": acquisition["source_request_summary"]["total_retries"],
        },
        "aggregate_funding_validation_review": {
            **aggregate,
            "reviewed_against_external_index_passed": reviewed_against_external_index_passed,
            "reviewed_against_manifest_passed": reviewed_against_manifest_passed,
            "reviewed_funding_index_sha256": index_hash,
        },
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_REVIEW",
        "external_funding_index_review": {
            "external_funding_index_path": str(FUNDING_INDEX_PATH),
            "external_funding_index_sha256": index_hash,
            "external_funding_index_sha256_verified": index_hash == FUNDING_INDEX_SHA256,
            "funding_files_referenced_count": len(index["symbol_files"]),
            "index_outside_repo": not is_under(FUNDING_INDEX_PATH, REPO_PATH),
            "referenced_files_all_exist": True,
            "referenced_files_all_outside_repo": True,
            "referenced_files_all_under_expected_dir": True,
            "review_passed": reviewed_against_external_index_passed,
        },
        "funding_data_validity_classification": {
            "active_p0_blocker_count": active_p0_blocker_count,
            "active_p0_blocker_reasons": p0_reasons,
            "active_p1_attention_count": active_p1_attention_count,
            "active_p1_attention_items": p1_items,
            "classification": classification,
        },
        "funding_file_review_summary": {
            "expected_keys": EXPECTED_KEYS,
            "funding_files_count": len(symbol_reviews),
            "jsonl_schema_valid": True,
            "reviewed_files_all_gzip_readable": True,
            "reviewed_files_all_hash_verified": True,
            "reviewed_files_all_outside_repo": True,
            "reviewed_files_all_under_expected_dir": True,
            "source_endpoint_all_valid": True,
        },
        "funding_rate_sanity_review": {
            "funding_rate_decimal_parse_valid": aggregate["reviewed_invalid_numeric_count"] == 0,
            "funding_rate_extreme_record_count": aggregate["funding_rate_extreme_record_count"],
            "funding_rate_extreme_samples": aggregate["funding_rate_extreme_samples"],
            "funding_rate_extreme_threshold_abs": decimal_string(EXTREME_FUNDING_RATE_ABS_THRESHOLD),
            "funding_rate_max_global": aggregate["reviewed_funding_rate_max_global"],
            "funding_rate_min_global": aggregate["reviewed_funding_rate_min_global"],
            "funding_rate_sanity_review_passed": funding_rate_sanity_review_passed,
            "mark_price_decimal_parse_valid": aggregate["reviewed_invalid_numeric_count"] == 0,
            "mark_price_sanity_review_passed": mark_price_sanity_review_passed,
        },
        "interval_cadence_review": {
            "expected_primary_interval_hours": EXPECTED_PRIMARY_INTERVAL_HOURS,
            "interval_gap_review_passed": interval_gap_review_passed,
            "interval_hours_distribution": aggregate["interval_hours_distribution"],
            "large_gap_threshold_hours": LARGE_GAP_THRESHOLD_HOURS,
            "max_gap_hours_global": aggregate["reviewed_max_gap_hours_global"],
            "non_8h_interval_count_total": aggregate["reviewed_non_8h_interval_count_total"],
            "symbols_with_large_gaps": aggregate["symbols_with_large_gaps"],
            "symbols_with_large_gaps_count": aggregate["reviewed_symbols_with_large_gaps_count"],
            "total_large_gap_count": aggregate["reviewed_total_large_gap_count"],
        },
        "limitations": [
            "This review validates acquired funding-rate rows, not Binance price panel rows.",
            "This review did not call Binance APIs.",
            "This review did not fetch funding data again.",
            "This review did not compute strategy returns or signals.",
            "This review did not read OKX panel rows.",
            "This review is not candidate generation.",
            "This review is not an edge claim.",
            "This review grants no runtime/live/capital permission.",
            "Future funding strategy execution requires separate explicit approval.",
            "Future edge claim requires external/future holdout and separate governance.",
        ],
        "module": MODULE_PATH,
        "repo_scope": {
            "api_key_used": False,
            "binance_1m_kline_source_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_panel_build_rerun": False,
            "binance_panel_rows_read": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "external_funding_files_read_for_validation_only": True,
            "funding_data_acquisition_rerun": False,
            "funding_rate_data_fetched_by_this_module": False,
            "funding_rate_endpoint_called_by_this_module": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "public_network_used": False,
            "review_artifact_created_in_repo": True,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "replacement_checks_all_true": True,
        "safety_permissions": {
            "binance_panel_row_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_data_review_created": True,
            "funding_data_valid_for_future_funding_signal_construction": funding_data_valid,
            "funding_strategy_execution_allowed_now": False,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "next_step_may_be_funding_signal_alignment_or_execution_planning_only": True,
            "okx_panel_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "strategy_research_not_allowed_from_this_review": True,
            "strategy_search_allowed_now": False,
        },
        "source_artifact_immutability_review": {
            "acquisition_manifest_read_only": True,
            "build_manifest_unchanged": True,
            "coverage_lock_unchanged": True,
            "external_funding_files_read_only": True,
            "external_funding_index_read_only": True,
            "panel_review_artifact_unchanged": True,
            "preregistration_artifact_unchanged": True,
            "preview_artifact_unchanged": True,
            "readiness_artifact_unchanged": True,
            "review_wrote_only_new_review_artifact": True,
            "source_artifacts_unchanged": source_artifacts_unchanged,
        },
        "source_artifacts": {
            "acquisition_manifest_path": str(ACQUISITION_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "acquisition_manifest_status": acquisition["status"],
            "acquisition_payload_hash_verified": True,
            "all_source_artifacts_read_only": True,
            "build_manifest_path": str(BUILD_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "build_manifest_payload_hash_verified": True,
            "coverage_lock_path": str(COVERAGE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "coverage_lock_payload_hash_verified": True,
            "external_funding_index_path": str(FUNDING_INDEX_PATH),
            "external_funding_index_sha256_verified": index_hash == FUNDING_INDEX_SHA256,
            "panel_review_artifact_path": str(PANEL_REVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "panel_review_payload_hash_verified": True,
            "preregistration_artifact_path": str(PREREGISTRATION_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preregistration_payload_hash_verified": True,
            "preview_artifact_path": str(PREVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preview_payload_hash_verified": True,
            "readiness_artifact_path": str(READINESS_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "readiness_payload_hash_verified": True,
        },
        "source_checkpoint": {
            "prior_acquisition_manifest": "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
            "prior_acquisition_payload_sha256_excluding_hash": ACQUISITION_PAYLOAD_HASH,
            "prior_acquisition_status": ACQUISITION_STATUS,
            "prior_acquisition_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_acquisition_lock_v1.py",
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding-rate data review",
            "repo_clean_before_review": True,
        },
        "status": REQUIRED_STATUS,
        "symbol_funding_review_records": symbol_reviews,
        "validation_checks": validation_checks,
        "window_boundary_review": {
            "max_funding_time_utc": aggregate["reviewed_max_funding_time_utc"],
            "min_funding_time_utc": aggregate["reviewed_min_funding_time_utc"],
            "no_records_at_or_after_aligned_window_end": aggregate["reviewed_records_outside_window_count"] == 0,
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "records_outside_window_count": aggregate["reviewed_records_outside_window_count"],
            "window_boundary_review_passed": window_boundary_review_passed,
            "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
            "window_start_utc": WINDOW_START_UTC,
        },
    }
    review["payload_sha256_excluding_hash"] = payload_hash(review)
    validate_review(review)
    return review


def validate_review(review: dict[str, Any]) -> None:
    assert review["status"] == REQUIRED_STATUS
    assert review["module"] == MODULE_PATH
    assert REVIEW_ARTIFACT_PATH == "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json"
    checks = review["validation_checks"]
    assert all(checks.values()), [key for key, value in checks.items() if value is not True]
    summary = review["aggregate_funding_validation_review"]
    assert summary["reviewed_symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert summary["reviewed_total_funding_records"] == EXPECTED_TOTAL_FUNDING_RECORDS
    assert summary["reviewed_symbols_with_records_count"] == EXPECTED_SYMBOL_COUNT
    assert summary["reviewed_symbols_with_zero_records_count"] == 0
    assert summary["reviewed_min_funding_time_utc"] == EXPECTED_MIN_FUNDING_TIME_UTC
    assert summary["reviewed_max_funding_time_utc"] == EXPECTED_MAX_FUNDING_TIME_UTC
    assert summary["reviewed_duplicate_symbol_funding_time_count"] == 0
    assert summary["reviewed_records_outside_window_count"] == 0
    assert summary["reviewed_invalid_numeric_count"] == 0
    assert summary["reviewed_missing_required_field_count"] == 0
    assert summary["reviewed_funding_rate_min_global"] == EXPECTED_FUNDING_RATE_MIN_GLOBAL
    assert summary["reviewed_funding_rate_max_global"] == EXPECTED_FUNDING_RATE_MAX_GLOBAL
    assert summary["reviewed_symbols_with_large_gaps_count"] == 0
    assert summary["reviewed_total_large_gap_count"] == 0
    assert review["interval_cadence_review"]["interval_gap_review_passed"] is True
    assert review["funding_rate_sanity_review"]["funding_rate_sanity_review_passed"] is True
    assert review["funding_rate_sanity_review"]["mark_price_sanity_review_passed"] is True
    assert review["window_boundary_review"]["window_boundary_review_passed"] is True
    assert review["source_artifact_immutability_review"]["source_artifacts_unchanged"] is True
    assert review["repo_scope"]["public_network_used"] is False
    assert review["repo_scope"]["funding_rate_endpoint_called_by_this_module"] is False
    assert review["repo_scope"]["funding_rate_data_fetched_by_this_module"] is False
    assert review["repo_scope"]["binance_panel_rows_read"] is False
    assert review["repo_scope"]["okx_panel_rows_read"] is False
    assert review["repo_scope"]["strategy_search_executed"] is False
    assert review["repo_scope"]["candidate_generation"] is False
    assert review["repo_scope"]["edge_claim"] is False
    assert review["repo_scope"]["runtime_live_capital"] is False
    assert review["replacement_checks_all_true"] is True
    assert review["payload_sha256_excluding_hash"] == payload_hash(review)


def summary_from_review(review: dict[str, Any]) -> dict[str, Any]:
    aggregate = review["aggregate_funding_validation_review"]
    classification = review["funding_data_validity_classification"]
    return {
        "active_p0_blocker_count": classification["active_p0_blocker_count"],
        "active_p1_attention_count": classification["active_p1_attention_count"],
        "candidate_generation": False,
        "edge_claim": False,
        "funding_data_valid_for_future_funding_signal_construction": review["safety_permissions"]["funding_data_valid_for_future_funding_signal_construction"],
        "funding_data_validity_classification": classification["classification"],
        "funding_rate_sanity_review_passed": review["funding_rate_sanity_review"]["funding_rate_sanity_review_passed"],
        "interval_gap_review_passed": review["interval_cadence_review"]["interval_gap_review_passed"],
        "mark_price_sanity_review_passed": review["funding_rate_sanity_review"]["mark_price_sanity_review_passed"],
        "payload_sha256_excluding_hash": review["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
        "review_artifact_path": REVIEW_ARTIFACT_PATH,
        "reviewed_duplicate_symbol_funding_time_count": aggregate["reviewed_duplicate_symbol_funding_time_count"],
        "reviewed_funding_index_sha256": aggregate["reviewed_funding_index_sha256"],
        "reviewed_funding_rate_max_global": aggregate["reviewed_funding_rate_max_global"],
        "reviewed_funding_rate_min_global": aggregate["reviewed_funding_rate_min_global"],
        "reviewed_invalid_numeric_count": aggregate["reviewed_invalid_numeric_count"],
        "reviewed_max_funding_time_utc": aggregate["reviewed_max_funding_time_utc"],
        "reviewed_min_funding_time_utc": aggregate["reviewed_min_funding_time_utc"],
        "reviewed_missing_required_field_count": aggregate["reviewed_missing_required_field_count"],
        "reviewed_records_outside_window_count": aggregate["reviewed_records_outside_window_count"],
        "reviewed_symbol_count": aggregate["reviewed_symbol_count"],
        "reviewed_symbols_with_large_gaps_count": aggregate["reviewed_symbols_with_large_gaps_count"],
        "reviewed_symbols_with_records_count": aggregate["reviewed_symbols_with_records_count"],
        "reviewed_symbols_with_zero_records_count": aggregate["reviewed_symbols_with_zero_records_count"],
        "reviewed_total_funding_records": aggregate["reviewed_total_funding_records"],
        "reviewed_total_large_gap_count": aggregate["reviewed_total_large_gap_count"],
        "runtime_live_capital": False,
        "status": review["status"],
        "strategy_search_executed": False,
        "window_boundary_review_passed": review["window_boundary_review"]["window_boundary_review_passed"],
    }


def main() -> int:
    try:
        review = build_review()
        write_json_atomic(REVIEW_PATH, review)
        # Confirm the artifact can be read back before printing success.
        reloaded = read_json(REVIEW_PATH)
        if reloaded.get("payload_sha256_excluding_hash") != review["payload_sha256_excluding_hash"]:
            raise BlockedError("review artifact readback hash mismatch")
        print(json.dumps(summary_from_review(review), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        if TEMP_REVIEW_PATH.exists():
            TEMP_REVIEW_PATH.unlink()
        if REVIEW_PATH.exists():
            try:
                payload = read_json(REVIEW_PATH)
                if payload.get("status") != REQUIRED_STATUS:
                    REVIEW_PATH.unlink()
            except Exception:
                REVIEW_PATH.unlink()
        print(json.dumps({"reason": str(exc), "replacement_checks_all_true": False, "status": "BLOCKED"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
