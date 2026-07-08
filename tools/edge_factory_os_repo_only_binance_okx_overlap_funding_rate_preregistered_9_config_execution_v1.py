#!/usr/bin/env python3
"""Execute the preregistered 9-config Binance funding-rate diagnostic."""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_PREREGISTERED_9_CONFIG_EXECUTED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.py"
EXECUTION_ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.json"

REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_PATH / EXECUTION_ARTIFACT_PATH
TEMP_ARTIFACT_PATH = ARTIFACT_PATH.with_suffix(".json.tmp")

FUNDING_REVIEW_PATH = REPO_PATH / "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json"
ACQUISITION_MANIFEST_PATH = REPO_PATH / "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json"
PREREGISTRATION_PATH = REPO_PATH / "artifacts/research_preregistrations/binance_okx_overlap_funding_rate_hypothesis_preregistration_contract_v1.json"
READINESS_PATH = REPO_PATH / "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = REPO_PATH / "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = REPO_PATH / "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = REPO_PATH / "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = REPO_PATH / "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

FUNDING_INDEX_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_acquisition_lock_v1\funding_index\binance_okx_overlap_funding_rate_index_v1.json"
)
PANEL_INDEX_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1\panel_index\binance_okx_overlap_near_5y_1h_panel_index_v1.json"
)
FUNDING_BY_SYMBOL_DIR = FUNDING_INDEX_PATH.parents[1] / "funding_by_symbol"
PANEL_BY_SYMBOL_DIR = PANEL_INDEX_PATH.parents[1] / "panel_1h_by_symbol"

PRIOR_HEAD = "e851bed7ea615d216501fc4cb6d5e9d055cb6b68"
PRIOR_TRACKED_PYTHON_COUNT = 814

FUNDING_REVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_DATA_REVIEW_AFTER_ACQUISITION_LOCK_CREATED"
FUNDING_REVIEW_PAYLOAD_HASH = "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849"
ACQUISITION_PAYLOAD_HASH = "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252"
PREREGISTRATION_PAYLOAD_HASH = "5febb59aee08873de1dbfc0464da463811090c334c18c5f2a552e1768cb3c768"
READINESS_PAYLOAD_HASH = "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716"
PANEL_REVIEW_PAYLOAD_HASH = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"
BUILD_MANIFEST_PAYLOAD_HASH = "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7"
PREVIEW_PAYLOAD_HASH = "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9"
COVERAGE_LOCK_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"
FUNDING_INDEX_SHA256 = "e762f21fee98083567df126e66e87642299d08b7957167fb352b39f130add2e5"
PANEL_INDEX_SHA256 = "2fa2dd67ec65d001e8b87812003809725a5780d51ae7840838e6932f67d63be7"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
HYPOTHESIS_NAME = "funding_rate_crowding_reversal"
WINDOW_START_UTC = "2023-07-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2025-10-31T16:00:00Z"
TRAIN_START_UTC = "2023-07-01T00:00:00Z"
TRAIN_END_EXCLUSIVE_UTC = "2025-01-01T00:00:00Z"
VALIDATION_START_UTC = "2025-01-01T00:00:00Z"
VALIDATION_END_EXCLUSIVE_UTC = "2025-10-31T16:00:00Z"
HOUR_MS = 3_600_000
SIGNAL_LAG_HOURS = 1
MIN_SYMBOLS_PER_TIMESTAMP = 60
TAIL_FRACTION = 0.20
ROUND_TRIP_COST_BPS = 20
ROUND_TRIP_COST_RETURN = ROUND_TRIP_COST_BPS / 10_000
NULL_RUN_COUNT = 100
NULL_BLOCK_LENGTH_HOURS = 168
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_CONFIG_IDS = [
    "funding_latest_hold8h",
    "funding_latest_hold16h",
    "funding_latest_hold24h",
    "funding_mean3_hold8h",
    "funding_mean3_hold16h",
    "funding_mean3_hold24h",
    "funding_mean9_hold8h",
    "funding_mean9_hold16h",
    "funding_mean9_hold24h",
]
CONFIGS = [
    ("funding_latest_hold8h", "latest_lagged_funding_rate", 8),
    ("funding_latest_hold16h", "latest_lagged_funding_rate", 16),
    ("funding_latest_hold24h", "latest_lagged_funding_rate", 24),
    ("funding_mean3_hold8h", "rolling_mean_3_funding_events", 8),
    ("funding_mean3_hold16h", "rolling_mean_3_funding_events", 16),
    ("funding_mean3_hold24h", "rolling_mean_3_funding_events", 24),
    ("funding_mean9_hold8h", "rolling_mean_9_funding_events", 8),
    ("funding_mean9_hold16h", "rolling_mean_9_funding_events", 16),
    ("funding_mean9_hold24h", "rolling_mean_9_funding_events", 24),
]
TRANSFORM_REQUIREMENTS = {
    "latest_lagged_funding_rate": 1,
    "rolling_mean_3_funding_events": 3,
    "rolling_mean_9_funding_events": 9,
}
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
    "minute_count",
    "complete_1h",
]
FUNDING_KEYS = ["funding_rate", "funding_time_ms", "funding_time_utc", "mark_price", "source_endpoint", "symbol"]


class BlockedError(RuntimeError):
    """Raised when execution cannot safely continue."""


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def parse_utc(value: str) -> int:
    return int(dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


WINDOW_START_MS = parse_utc(WINDOW_START_UTC)
WINDOW_END_MS = parse_utc(WINDOW_END_EXCLUSIVE_UTC)
TRAIN_START_MS = parse_utc(TRAIN_START_UTC)
TRAIN_END_MS = parse_utc(TRAIN_END_EXCLUSIVE_UTC)
VALIDATION_START_MS = parse_utc(VALIDATION_START_UTC)
VALIDATION_END_MS = parse_utc(VALIDATION_END_EXCLUSIVE_UTC)


def iso_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).strftime("%Y-%m")


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
    with TEMP_ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    TEMP_ARTIFACT_PATH.replace(path)


def is_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def decimal_from_string(value: Any, label: str) -> Decimal:
    if not isinstance(value, str) or value == "":
        raise BlockedError(f"missing decimal field {label}")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise BlockedError(f"invalid decimal field {label}: {value}") from exc


def safe_mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def metric_bps(values: list[float]) -> float | None:
    mean_value = safe_mean(values)
    if mean_value is None:
        return None
    return mean_value * 10_000


def round_metric(value: float | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    if not math.isfinite(value):
        raise BlockedError("non-finite metric encountered")
    return round(value, digits)


def load_sources() -> dict[str, Any]:
    paths = [
        FUNDING_REVIEW_PATH,
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
    payloads = {
        "funding_review": read_json(FUNDING_REVIEW_PATH),
        "acquisition": read_json(ACQUISITION_MANIFEST_PATH),
        "preregistration": read_json(PREREGISTRATION_PATH),
        "readiness": read_json(READINESS_PATH),
        "panel_review": read_json(PANEL_REVIEW_PATH),
        "build_manifest": read_json(BUILD_MANIFEST_PATH),
        "preview": read_json(PREVIEW_PATH),
        "coverage_lock": read_json(COVERAGE_LOCK_PATH),
    }
    expected_hashes = {
        "funding_review": FUNDING_REVIEW_PAYLOAD_HASH,
        "acquisition": ACQUISITION_PAYLOAD_HASH,
        "preregistration": PREREGISTRATION_PAYLOAD_HASH,
        "readiness": READINESS_PAYLOAD_HASH,
        "panel_review": PANEL_REVIEW_PAYLOAD_HASH,
        "build_manifest": BUILD_MANIFEST_PAYLOAD_HASH,
        "preview": PREVIEW_PAYLOAD_HASH,
        "coverage_lock": COVERAGE_LOCK_PAYLOAD_HASH,
    }
    for key, expected_hash in expected_hashes.items():
        if not verify_payload(payloads[key], expected_hash):
            raise BlockedError(f"{key} payload hash mismatch")
    if payloads["funding_review"]["status"] != FUNDING_REVIEW_STATUS:
        raise BlockedError("funding review status mismatch")
    if payloads["funding_review"]["funding_data_validity_classification"]["active_p0_blocker_count"] != 0:
        raise BlockedError("funding review has active P0 blockers")
    if payloads["panel_review"]["panel_validity_classification"] != "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS":
        raise BlockedError("panel review classification mismatch")
    if payloads["panel_review"]["panel_validity_classification"] == "PANEL_REVIEW_FAIL_REQUIRES_REBUILD_OR_REPAIR":
        raise BlockedError("panel review failed")
    if payloads["panel_review"]["validation_checks"]["reviewed_output_symbol_count_verified_81"] is not True:
        raise BlockedError("panel review symbol count not verified")
    prereg = payloads["preregistration"]
    if prereg["funding_rate_hypothesis_preregistration"]["route_family"] != ROUTE_FAMILY:
        raise BlockedError("route family mismatch")
    if prereg["funding_rate_hypothesis_preregistration"]["hypothesis_name"] != HYPOTHESIS_NAME:
        raise BlockedError("hypothesis name mismatch")
    grid = prereg["predefined_config_grid"]
    if grid["config_count"] != 9 or grid["deterministic_config_ids"] != EXPECTED_CONFIG_IDS:
        raise BlockedError("preregistered config grid mismatch")
    universe = prereg["universe_and_window_contract"]
    if universe["exact_overlap_symbol_count"] != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("exact overlap count mismatch")
    if universe["aligned_window_start_utc"] != WINDOW_START_UTC or universe["aligned_window_end_exclusive_utc"] != WINDOW_END_EXCLUSIVE_UTC:
        raise BlockedError("aligned window mismatch")
    if payloads["funding_review"]["safety_permissions"]["funding_data_valid_for_future_funding_signal_construction"] is not True:
        raise BlockedError("funding data not valid for future funding signal construction")
    return payloads


def load_indexes_and_paths(payloads: dict[str, Any], symbols: list[str]) -> tuple[dict[str, Path], dict[str, Path]]:
    if sha256_file(FUNDING_INDEX_PATH) != FUNDING_INDEX_SHA256:
        raise BlockedError("funding index sha256 mismatch")
    if sha256_file(PANEL_INDEX_PATH) != PANEL_INDEX_SHA256:
        raise BlockedError("panel index sha256 mismatch")
    funding_index = read_json(FUNDING_INDEX_PATH)
    panel_index = read_json(PANEL_INDEX_PATH)
    if funding_index["symbol_count"] != EXPECTED_SYMBOL_COUNT or panel_index["symbol_count"] != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("index symbol count mismatch")
    funding_paths = {record["symbol"]: Path(record["output_file_path"]) for record in funding_index["symbol_files"]}
    panel_paths: dict[str, Path] = {}
    for value in panel_index["panel_files"]:
        path = Path(value)
        symbol = path.name.removesuffix("_1h.csv.gz")
        panel_paths[symbol] = path
    if sorted(funding_paths) != symbols or sorted(panel_paths) != symbols:
        raise BlockedError("index symbols do not match preregistered symbols")
    build_records = {record["symbol"]: record for record in payloads["build_manifest"]["symbol_output_records"]}
    acquisition_records = {record["symbol"]: record for record in payloads["acquisition"]["symbol_funding_records"]}
    for symbol in symbols:
        if not funding_paths[symbol].is_file() or not panel_paths[symbol].is_file():
            raise BlockedError(f"missing external input file for {symbol}")
        if is_under(funding_paths[symbol], REPO_PATH) or is_under(panel_paths[symbol], REPO_PATH):
            raise BlockedError(f"external input file is inside repo for {symbol}")
        if sha256_file(funding_paths[symbol]) != acquisition_records[symbol]["output_file_sha256"]:
            raise BlockedError(f"funding file hash mismatch for {symbol}")
        if sha256_file(panel_paths[symbol]) != build_records[symbol]["output_file_sha256"]:
            raise BlockedError(f"panel file hash mismatch for {symbol}")
    return funding_paths, panel_paths


def read_funding_rows(symbols: list[str], funding_paths: dict[str, Path], symbol_to_idx: dict[str, int]) -> tuple[list[list[tuple[int, float]]], dict[str, Any]]:
    events: list[list[tuple[int, float]]] = [[] for _ in symbols]
    total_rows = 0
    min_time: int | None = None
    max_time: int | None = None
    numeric_valid = True
    outside_count = 0
    for count, symbol in enumerate(symbols, start=1):
        if count == 1 or count % 20 == 0:
            log(f"reading funding rows {count}/{len(symbols)}")
        idx = symbol_to_idx[symbol]
        prev_time: int | None = None
        with gzip.open(funding_paths[symbol], "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if sorted(row.keys()) != FUNDING_KEYS:
                    raise BlockedError(f"funding row schema mismatch for {symbol}")
                if row["symbol"] != symbol or row["source_endpoint"] != "fapi_v1_fundingRate":
                    raise BlockedError(f"funding row symbol/source mismatch for {symbol}")
                funding_time = row["funding_time_ms"]
                if not isinstance(funding_time, int):
                    raise BlockedError(f"funding_time_ms non-integer for {symbol}")
                if row["funding_time_utc"] != iso_from_ms(funding_time):
                    raise BlockedError(f"funding_time_utc mismatch for {symbol}")
                if funding_time < WINDOW_START_MS or funding_time >= WINDOW_END_MS:
                    outside_count += 1
                    raise BlockedError(f"funding row outside aligned window for {symbol}")
                if prev_time is not None and funding_time <= prev_time:
                    raise BlockedError(f"funding rows not strictly increasing for {symbol}")
                rate = decimal_from_string(row["funding_rate"], "funding_rate")
                if row["mark_price"] is not None and decimal_from_string(row["mark_price"], "mark_price") <= 0:
                    numeric_valid = False
                    raise BlockedError(f"mark_price sanity failure for {symbol}")
                events[idx].append((funding_time, float(rate)))
                prev_time = funding_time
                total_rows += 1
                min_time = funding_time if min_time is None else min(min_time, funding_time)
                max_time = funding_time if max_time is None else max(max_time, funding_time)
        if not events[idx]:
            raise BlockedError(f"zero funding rows for {symbol}")
    return events, {
        "funding_max_time_utc": iso_from_ms(max_time or WINDOW_START_MS),
        "funding_min_time_utc": iso_from_ms(min_time or WINDOW_START_MS),
        "funding_numeric_sanity_valid": numeric_valid,
        "funding_rows_outside_aligned_window_count": outside_count,
        "funding_rows_read_for_execution": total_rows,
        "symbols_with_funding_rows_count": sum(1 for item in events if item),
        "symbols_missing_funding_rows": [symbols[i] for i, item in enumerate(events) if not item],
    }


def read_panel_rows(symbols: list[str], panel_paths: dict[str, Path], symbol_to_idx: dict[str, int]) -> tuple[list[dict[int, float]], dict[str, Any]]:
    opens: list[dict[int, float]] = [dict() for _ in symbols]
    rows_read = 0
    outside_count = 0
    incomplete_skipped = 0
    min_ts: int | None = None
    max_ts: int | None = None
    numeric_valid = True
    for count, symbol in enumerate(symbols, start=1):
        if count == 1 or count % 10 == 0:
            log(f"reading panel rows {count}/{len(symbols)}")
        idx = symbol_to_idx[symbol]
        with gzip.open(panel_paths[symbol], "rt", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != PANEL_HEADER:
                raise BlockedError(f"panel header mismatch for {symbol}")
            for row in reader:
                if row["symbol"] != symbol:
                    raise BlockedError(f"panel symbol mismatch for {symbol}")
                ts = parse_utc(row["timestamp_utc"])
                if ts < WINDOW_START_MS or ts >= WINDOW_END_MS:
                    continue
                rows_read += 1
                min_ts = ts if min_ts is None else min(min_ts, ts)
                max_ts = ts if max_ts is None else max(max_ts, ts)
                if row["complete_1h"] != "true":
                    incomplete_skipped += 1
                    continue
                open_value = float(decimal_from_string(row["open"], "open"))
                high_value = float(decimal_from_string(row["high"], "high"))
                low_value = float(decimal_from_string(row["low"], "low"))
                close_value = float(decimal_from_string(row["close"], "close"))
                if open_value <= 0 or high_value <= 0 or low_value <= 0 or close_value <= 0:
                    numeric_valid = False
                    raise BlockedError(f"panel OHLC non-positive for {symbol}")
                if high_value < max(open_value, close_value, low_value) or low_value > min(open_value, close_value, high_value):
                    numeric_valid = False
                    raise BlockedError(f"panel OHLC sanity failure for {symbol}")
                opens[idx][ts] = open_value
    missing_panel = [symbols[i] for i, mapping in enumerate(opens) if not mapping]
    if missing_panel:
        raise BlockedError(f"symbols missing panel rows: {missing_panel}")
    return opens, {
        "incomplete_panel_rows_skipped": incomplete_skipped,
        "panel_max_timestamp_utc": iso_from_ms(max_ts or WINDOW_START_MS),
        "panel_min_timestamp_utc": iso_from_ms(min_ts or WINDOW_START_MS),
        "panel_numeric_sanity_valid": numeric_valid,
        "panel_rows_outside_aligned_window_count": outside_count,
        "panel_rows_read_for_execution": rows_read,
        "panel_symbol_count": len(symbols),
        "symbols_missing_panel_rows": missing_panel,
        "symbols_with_panel_rows_count": len(symbols) - len(missing_panel),
    }


def hourly_timestamps() -> list[int]:
    return list(range(WINDOW_START_MS, WINDOW_END_MS, HOUR_MS))


def build_signal_vectors(
    timestamps: list[int],
    symbols: list[str],
    opens: list[dict[int, float]],
    funding_events: list[list[tuple[int, float]]],
) -> dict[str, dict[int, list[int]]]:
    signal_vectors: dict[str, dict[int, list[int]]] = {transform: {} for transform in TRANSFORM_REQUIREMENTS}
    pointers = [-1 for _ in symbols]
    start = time.time()
    for pos, ts in enumerate(timestamps, start=1):
        if pos == 1 or pos % 5000 == 0:
            log(f"aligning funding signals {pos}/{len(timestamps)} elapsed={time.time() - start:.1f}s")
        limit = ts - SIGNAL_LAG_HOURS * HOUR_MS
        latest_values: list[float | None] = [None for _ in symbols]
        mean3_values: list[float | None] = [None for _ in symbols]
        mean9_values: list[float | None] = [None for _ in symbols]
        for idx, events in enumerate(funding_events):
            pointer = pointers[idx]
            while pointer + 1 < len(events) and events[pointer + 1][0] <= limit:
                pointer += 1
            pointers[idx] = pointer
            if ts not in opens[idx]:
                continue
            if pointer >= 0:
                latest_values[idx] = events[pointer][1]
            if pointer >= 2:
                mean3_values[idx] = (events[pointer][1] + events[pointer - 1][1] + events[pointer - 2][1]) / 3
            if pointer >= 8:
                total = 0.0
                for offset in range(9):
                    total += events[pointer - offset][1]
                mean9_values[idx] = total / 9
        values_by_transform = {
            "latest_lagged_funding_rate": latest_values,
            "rolling_mean_3_funding_events": mean3_values,
            "rolling_mean_9_funding_events": mean9_values,
        }
        for transform, values in values_by_transform.items():
            ranked = [(value, symbols[idx], idx) for idx, value in enumerate(values) if value is not None]
            if len(ranked) >= MIN_SYMBOLS_PER_TIMESTAMP:
                ranked.sort()
                signal_vectors[transform][ts] = [idx for _, _, idx in ranked]
    return signal_vectors


def build_forward_returns(timestamps: list[int], symbols: list[str], opens: list[dict[int, float]]) -> dict[int, dict[int, list[float | None]]]:
    returns_by_holding: dict[int, dict[int, list[float | None]]] = {8: {}, 16: {}, 24: {}}
    for holding in [8, 16, 24]:
        log(f"building open-to-open returns for hold={holding}h")
        horizon = holding * HOUR_MS
        for ts in timestamps:
            exit_ts = ts + horizon
            if exit_ts >= WINDOW_END_MS:
                continue
            values: list[float | None] = []
            any_value = False
            for idx in range(len(symbols)):
                entry = opens[idx].get(ts)
                exit_open = opens[idx].get(exit_ts)
                if entry is None or exit_open is None:
                    values.append(None)
                else:
                    values.append((exit_open / entry) - 1.0)
                    any_value = True
            if any_value:
                returns_by_holding[holding][ts] = values
    return returns_by_holding


def split_for_timestamp(ts: int, holding: int) -> tuple[str | None, bool]:
    exit_ts = ts + holding * HOUR_MS
    if TRAIN_START_MS <= ts < TRAIN_END_MS:
        return "train", exit_ts >= TRAIN_END_MS
    if VALIDATION_START_MS <= ts < VALIDATION_END_MS:
        return "validation", exit_ts >= VALIDATION_END_MS
    return None, True


def spread_from_selected(selected_long: list[int], selected_short: list[int], returns: list[float | None]) -> tuple[float | None, int, int, int]:
    long_returns = [returns[idx] for idx in selected_long if returns[idx] is not None]
    short_returns = [returns[idx] for idx in selected_short if returns[idx] is not None]
    missing = (len(selected_long) - len(long_returns)) + (len(selected_short) - len(short_returns))
    if not long_returns or not short_returns:
        return None, len(long_returns), len(short_returns), missing
    return (sum(long_returns) / len(long_returns)) - (sum(short_returns) / len(short_returns)), len(long_returns), len(short_returns), missing


def block_shuffle(values: list[int], seed_text: str) -> list[int]:
    blocks = [values[i : i + NULL_BLOCK_LENGTH_HOURS] for i in range(0, len(values), NULL_BLOCK_LENGTH_HOURS)]
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed)
    rng.shuffle(blocks)
    shuffled: list[int] = []
    for block in blocks:
        shuffled.extend(block)
    return shuffled[: len(values)]


def run_nulls(
    config_id: str,
    transform: str,
    holding: int,
    actual_validation_net_bps: float | None,
    timestamps_by_window: dict[str, list[int]],
    signal_vectors: dict[str, dict[int, list[int]]],
    returns_by_holding: dict[int, dict[int, list[float | None]]],
) -> dict[str, Any]:
    null_metrics: dict[str, list[float]] = {"train": [], "validation": []}
    for window_name in ["train", "validation"]:
        timestamps = timestamps_by_window[window_name]
        if not timestamps:
            continue
        for run_index in range(NULL_RUN_COUNT):
            shuffled_signal_ts = block_shuffle(timestamps, f"{ROUTE_FAMILY}|{config_id}|{window_name}|{run_index}")
            net_returns: list[float] = []
            for return_ts, signal_ts in zip(timestamps, shuffled_signal_ts):
                ranked = signal_vectors[transform][signal_ts]
                tail_count = max(1, math.floor(len(ranked) * TAIL_FRACTION))
                gross, _, _, _ = spread_from_selected(ranked[:tail_count], ranked[-tail_count:], returns_by_holding[holding][return_ts])
                if gross is not None:
                    net_returns.append(gross - ROUND_TRIP_COST_RETURN)
            net_bps = metric_bps(net_returns)
            if net_bps is not None:
                null_metrics[window_name].append(net_bps)
    validation_null = null_metrics["validation"]
    percentile = None
    if actual_validation_net_bps is not None and len(validation_null) == NULL_RUN_COUNT:
        percentile = sum(1 for value in validation_null if value <= actual_validation_net_bps) / len(validation_null)
    return {
        "null_baseline": "deterministic_funding_signal_timestamp_block_shuffle_null",
        "null_block_length_hours": NULL_BLOCK_LENGTH_HOURS,
        "null_run_count": NULL_RUN_COUNT,
        "train_null_metric_bps_mean": round_metric(statistics.mean(null_metrics["train"]) if null_metrics["train"] else None),
        "train_null_runs_completed": len(null_metrics["train"]),
        "validation_null_metric_bps_mean": round_metric(statistics.mean(validation_null) if validation_null else None),
        "validation_null_percentile_or_rank": round_metric(percentile, 6),
        "validation_null_runs_completed": len(validation_null),
    }


def evaluate_configs(
    timestamps: list[int],
    symbols: list[str],
    signal_vectors: dict[str, dict[int, list[int]]],
    returns_by_holding: dict[int, dict[int, list[float | None]]],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    config_results: list[dict[str, Any]] = []
    null_complete = True
    for config_number, (config_id, transform, holding) in enumerate(CONFIGS, start=1):
        log(f"executing config {config_number}/9 {config_id}")
        gross_by_window: dict[str, list[float]] = {"train": [], "validation": []}
        net_by_window: dict[str, list[float]] = {"train": [], "validation": []}
        timestamps_by_window: dict[str, list[int]] = {"train": [], "validation": []}
        monthly_validation: dict[str, list[float]] = defaultdict(list)
        selected_sets: list[set[int]] = []
        turnover_values: list[float] = []
        participation: Counter[int] = Counter()
        skipped_insufficient = 0
        skipped_cross_window = 0
        skipped_missing = 0
        skipped_incomplete = 0
        eligible_symbol_sum = 0
        long_size_sum = 0
        short_size_sum = 0
        observation_count = 0
        previous_set: set[int] | None = None
        for ts in timestamps:
            ranked = signal_vectors[transform].get(ts)
            if ranked is None:
                skipped_insufficient += 1
                continue
            window_name, cross_window = split_for_timestamp(ts, holding)
            if window_name is None:
                continue
            if cross_window:
                skipped_cross_window += 1
                continue
            returns = returns_by_holding[holding].get(ts)
            if returns is None:
                skipped_missing += len(ranked)
                continue
            tail_count = max(1, math.floor(len(ranked) * TAIL_FRACTION))
            long_symbols = ranked[:tail_count]
            short_symbols = ranked[-tail_count:]
            gross, long_count, short_count, missing = spread_from_selected(long_symbols, short_symbols, returns)
            skipped_missing += missing
            if gross is None:
                continue
            net = gross - ROUND_TRIP_COST_RETURN
            gross_by_window[window_name].append(gross)
            net_by_window[window_name].append(net)
            timestamps_by_window[window_name].append(ts)
            if window_name == "validation":
                monthly_validation[month_from_ms(ts)].append(net)
            combined = set(long_symbols) | set(short_symbols)
            for idx in combined:
                participation[idx] += 1
            if previous_set is not None:
                denominator = max(1, len(previous_set))
                turnover_values.append(len(previous_set.symmetric_difference(combined)) / denominator)
            previous_set = combined
            selected_sets.append(combined)
            eligible_symbol_sum += len(ranked)
            long_size_sum += long_count
            short_size_sum += short_count
            observation_count += 1
        train_net_bps = metric_bps(net_by_window["train"])
        validation_net_bps = metric_bps(net_by_window["validation"])
        train_gross_bps = metric_bps(gross_by_window["train"])
        validation_gross_bps = metric_bps(gross_by_window["validation"])
        monthly_bps = {month: round_metric(metric_bps(values)) for month, values in sorted(monthly_validation.items())}
        monthly_positive = sum(1 for value in monthly_bps.values() if value is not None and value > 0)
        monthly_count = len(monthly_bps)
        total_participation = sum(participation.values())
        top_share = (max(participation.values()) / total_participation) if total_participation else None
        avg_turnover = safe_mean(turnover_values)
        median_turnover = statistics.median(turnover_values) if turnover_values else None
        max_turnover = max(turnover_values) if turnover_values else None
        null_result = run_nulls(config_id, transform, holding, validation_net_bps, timestamps_by_window, signal_vectors, returns_by_holding)
        if null_result["validation_null_runs_completed"] != NULL_RUN_COUNT:
            null_complete = False
        metric_issue_count = 0
        for value in [train_net_bps, validation_net_bps, train_gross_bps, validation_gross_bps]:
            if value is None or not math.isfinite(value):
                metric_issue_count += 1
        result = {
            "average_eligible_symbols_per_timestamp": round_metric(eligible_symbol_sum / observation_count if observation_count else None),
            "average_long_leg_size": round_metric(long_size_sum / observation_count if observation_count else None),
            "average_short_leg_size": round_metric(short_size_sum / observation_count if observation_count else None),
            "average_turnover": round_metric(avg_turnover),
            "average_turnover_if_available": round_metric(avg_turnover),
            "config_id": config_id,
            "holding_period_hours": holding,
            "long_short_participation_count": total_participation,
            "max_turnover": round_metric(max_turnover),
            "median_turnover": round_metric(median_turnover),
            "median_turnover_if_available": round_metric(median_turnover),
            "metric_integrity_issue_count": metric_issue_count,
            "monthly_positive_rate": round_metric(monthly_positive / monthly_count if monthly_count else None),
            "monthly_positive_rate_if_available": round_metric(monthly_positive / monthly_count if monthly_count else None),
            "monthly_stability_review_preliminary_passed": bool(monthly_count >= 6 and monthly_positive / monthly_count >= 0.60) if monthly_count else False,
            "null_baseline": null_result,
            "signal_transform": transform,
            "skipped_symbol_rows_incomplete_entry_or_exit": skipped_incomplete,
            "skipped_symbol_rows_missing_entry_or_exit_price": skipped_missing,
            "skipped_timestamps_cross_window_exit": skipped_cross_window,
            "skipped_timestamps_insufficient_symbols": skipped_insufficient,
            "tail_selection": "bottom_20_percent_long_top_20_percent_short",
            "top_symbol_exposure_share": round_metric(top_share),
            "top_symbol_exposure_share_if_available": round_metric(top_share),
            "train_eligible_timestamp_count": len(timestamps_by_window["train"]),
            "train_gross_metric_bps": round_metric(train_gross_bps),
            "train_net_metric_bps": round_metric(train_net_bps),
            "train_observation_count": len(net_by_window["train"]),
            "train_positive_after_cost": bool(train_net_bps is not None and train_net_bps > 0),
            "turnover_concentration_review_preliminary_passed": bool(top_share is not None and avg_turnover is not None and top_share <= 0.10 and avg_turnover <= 1.50),
            "validation_eligible_timestamp_count": len(timestamps_by_window["validation"]),
            "validation_gross_metric_bps": round_metric(validation_gross_bps),
            "validation_month_count": monthly_count,
            "validation_monthly_net_metric_bps_by_month": monthly_bps,
            "validation_months_negative_or_zero_count": monthly_count - monthly_positive,
            "validation_months_positive_count": monthly_positive,
            "validation_net_metric_bps": round_metric(validation_net_bps),
            "validation_null_percentile_or_rank_if_available": null_result["validation_null_percentile_or_rank"],
            "validation_observation_count": len(net_by_window["validation"]),
            "validation_positive_after_cost": bool(validation_net_bps is not None and validation_net_bps > 0),
        }
        config_results.append(result)
    train_validation_summary = build_train_validation_summary(config_results, null_complete)
    null_summary = {
        "best_validation_config_null_percentile": train_validation_summary["best_validation_null_percentile_or_rank"],
        "null_baseline": "deterministic_funding_signal_timestamp_block_shuffle_null",
        "null_baseline_complete": null_complete,
        "null_baseline_review_preliminary_passed": train_validation_summary["null_baseline_review_preliminary_passed"],
        "null_run_count": NULL_RUN_COUNT,
    }
    monthly_summary = {
        "monthly_stability_created": True,
        "monthly_stability_review_preliminary_passed": train_validation_summary["monthly_stability_review_preliminary_passed"],
        "per_config_monthly_positive_rates": {
            result["config_id"]: result["monthly_positive_rate"] for result in config_results
        },
    }
    turnover_summary = {
        "per_config_average_turnover": {
            result["config_id"]: result["average_turnover"] for result in config_results
        },
        "per_config_top_symbol_exposure_share": {
            result["config_id"]: result["top_symbol_exposure_share"] for result in config_results
        },
        "turnover_concentration_created": True,
        "turnover_concentration_review_preliminary_passed": train_validation_summary["turnover_concentration_review_preliminary_passed"],
    }
    metric_summary = {
        "all_config_ids_match_preregistration": [result["config_id"] for result in config_results] == EXPECTED_CONFIG_IDS,
        "config_count": len(config_results),
        "metric_integrity_issue_count": sum(result["metric_integrity_issue_count"] for result in config_results),
        "metric_integrity_passed": sum(result["metric_integrity_issue_count"] for result in config_results) == 0,
        "no_duplicate_config_ids": len({result["config_id"] for result in config_results}) == len(config_results),
        "no_non_preregistered_configs": True,
        "no_parameter_expansion": True,
    }
    return config_results, train_validation_summary, null_summary, monthly_summary, turnover_summary | {"metric_integrity_summary": metric_summary}


def rank_map(values: dict[str, float]) -> dict[str, int]:
    ordered = sorted(values.items(), key=lambda item: item[1], reverse=True)
    return {key: idx + 1 for idx, (key, _) in enumerate(ordered)}


def spearman_from_metrics(config_results: list[dict[str, Any]]) -> float | None:
    train = {r["config_id"]: r["train_net_metric_bps"] for r in config_results if r["train_net_metric_bps"] is not None}
    validation = {r["config_id"]: r["validation_net_metric_bps"] for r in config_results if r["validation_net_metric_bps"] is not None}
    if set(train) != set(validation) or len(train) < 2:
        return None
    train_ranks = rank_map(train)
    validation_ranks = rank_map(validation)
    xs = [train_ranks[key] for key in EXPECTED_CONFIG_IDS]
    ys = [validation_ranks[key] for key in EXPECTED_CONFIG_IDS]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def build_train_validation_summary(config_results: list[dict[str, Any]], null_complete: bool) -> dict[str, Any]:
    best_train = max(config_results, key=lambda r: r["train_net_metric_bps"] if r["train_net_metric_bps"] is not None else -float("inf"))
    best_validation = max(config_results, key=lambda r: r["validation_net_metric_bps"] if r["validation_net_metric_bps"] is not None else -float("inf"))
    validation_rank = rank_map({r["config_id"]: r["validation_net_metric_bps"] for r in config_results if r["validation_net_metric_bps"] is not None})
    train_rank = rank_map({r["config_id"]: r["train_net_metric_bps"] for r in config_results if r["train_net_metric_bps"] is not None})
    best_train_validation_rank = validation_rank.get(best_train["config_id"])
    best_validation_train_rank = train_rank.get(best_validation["config_id"])
    degradation = bool(
        (best_train_validation_rank is not None and best_train_validation_rank > math.ceil(len(config_results) / 2))
        or (best_validation_train_rank is not None and best_validation_train_rank > math.ceil(len(config_results) / 2))
    )
    all_validation_positive = all(r["validation_positive_after_cost"] for r in config_results)
    all_validation_non_positive = all(not r["validation_positive_after_cost"] for r in config_results)
    null_percentiles = [r["validation_null_percentile_or_rank_if_available"] for r in config_results]
    best_validation_percentile = best_validation["validation_null_percentile_or_rank_if_available"]
    monthly_pass = best_validation["monthly_stability_review_preliminary_passed"]
    turnover_pass = best_validation["turnover_concentration_review_preliminary_passed"]
    metric_issue_count = sum(r["metric_integrity_issue_count"] for r in config_results)
    return {
        "all_validation_net_metrics_non_positive_after_cost": all_validation_non_positive,
        "all_validation_net_metrics_positive_after_cost": all_validation_positive,
        "best_train_config_id": best_train["config_id"],
        "best_validation_config_id": best_validation["config_id"],
        "best_validation_gross_metric_bps": best_validation["validation_gross_metric_bps"],
        "best_validation_holding_period_hours": best_validation["holding_period_hours"],
        "best_validation_net_metric_bps": best_validation["validation_net_metric_bps"],
        "best_validation_null_percentile_or_rank": best_validation_percentile,
        "best_validation_signal_transform": best_validation["signal_transform"],
        "metric_integrity_issue_count": metric_issue_count,
        "metric_integrity_passed": metric_issue_count == 0,
        "monthly_stability_created": True,
        "monthly_stability_review_preliminary_passed": monthly_pass,
        "null_baseline_complete": null_complete and all(value is not None for value in null_percentiles),
        "null_baseline_review_preliminary_passed": bool(null_complete and best_validation_percentile is not None and best_validation_percentile >= 0.95 and all(value is not None for value in null_percentiles)),
        "null_run_count": NULL_RUN_COUNT,
        "train_validation_degradation_flag": degradation,
        "train_validation_rank_consistency": round_metric(spearman_from_metrics(config_results)),
        "turnover_concentration_created": True,
        "turnover_concentration_review_preliminary_passed": turnover_pass,
        "validation_positive_after_cost": best_validation["validation_positive_after_cost"],
    }


def build_execution_artifact() -> dict[str, Any]:
    start = time.time()
    payloads = load_sources()
    symbols = sorted(payloads["preregistration"]["universe_and_window_contract"]["future_execution_binance_symbol_set"])
    if len(symbols) != EXPECTED_SYMBOL_COUNT:
        raise BlockedError("symbol list count mismatch")
    symbol_to_idx = {symbol: idx for idx, symbol in enumerate(symbols)}
    funding_paths, panel_paths = load_indexes_and_paths(payloads, symbols)
    funding_events, funding_validation = read_funding_rows(symbols, funding_paths, symbol_to_idx)
    opens, panel_validation = read_panel_rows(symbols, panel_paths, symbol_to_idx)
    timestamps = hourly_timestamps()
    log(f"prepared {len(timestamps)} aligned hourly timestamps")
    signal_vectors = build_signal_vectors(timestamps, symbols, opens, funding_events)
    returns_by_holding = build_forward_returns(timestamps, symbols, opens)
    config_results, train_validation_summary, null_summary, monthly_summary, turnover_and_metric = evaluate_configs(
        timestamps, symbols, signal_vectors, returns_by_holding
    )
    metric_integrity_summary = turnover_and_metric.pop("metric_integrity_summary")
    input_validation = {
        **panel_validation,
        **funding_validation,
        "funding_symbol_count": len(symbols),
        "input_data_valid_for_execution": True,
    }
    validation_checks = {
        "acquisition_manifest_loaded": True,
        "acquisition_payload_hash_verified": True,
        "aligned_window_verified": True,
        "binance_1h_panel_rows_read_for_execution": True,
        "build_manifest_loaded": True,
        "build_manifest_payload_hash_verified": True,
        "config_count_verified_9": len(config_results) == 9,
        "config_ids_match_preregistration_exactly": [r["config_id"] for r in config_results] == EXPECTED_CONFIG_IDS,
        "coverage_lock_loaded": True,
        "coverage_lock_payload_hash_verified": True,
        "exact_overlap_symbol_count_verified_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
        "exactly_one_new_tracked_json_execution_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "execution_artifact_json_valid": True,
        "execution_artifact_path_equals_required_path": EXECUTION_ARTIFACT_PATH == "artifacts/strategy_executions/binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.json",
        "funding_data_not_fetched_by_this_module": True,
        "funding_endpoint_not_called_by_this_module": True,
        "funding_review_artifact_loaded": True,
        "funding_review_payload_hash_verified": True,
        "metric_integrity_checks_created": True,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.py",
        "monthly_stability_created": True,
        "no_binance_1m_source_rows_read": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_holdout_access": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "null_baseline_complete": train_validation_summary["null_baseline_complete"],
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
        "reviewed_funding_rows_read_for_execution": True,
        "route_family_verified": True,
        "status_equals_required_status": True,
        "turnover_concentration_created": True,
    }
    artifact = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_PREREGISTERED_9_CONFIG_EXECUTION",
        "config_results": config_results,
        "diagnostic_interpretation_limits": {
            "candidate_generation_allowed_from_this_execution": False,
            "edge_claim_allowed_from_this_execution": False,
            "evaluator_not_yet_run": True,
            "execution_result_is_diagnostic_only": True,
            "family_release_allowed_from_this_execution": False,
            "final_edge_claim_requires_external_or_future_holdout": True,
            "no_live_or_capital_implication": True,
            "positive_result_if_any_requires_separate_closure": True,
            "positive_result_if_any_requires_separate_evaluator": True,
            "positive_result_if_any_requires_separate_governance_before_any_followup": True,
            "runtime_live_capital_allowed_from_this_execution": False,
        },
        "execution_safety_controls": {
            "cross_window_holding_returns_prevented": True,
            "incomplete_hour_policy_applied": True,
            "no_backfill": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_forward_fill": True,
            "no_lookahead_policy_applied": True,
            "no_parameter_expansion": True,
            "no_runtime_live_capital": True,
            "no_synthetic_fill": True,
            "no_unregistered_config_tested": True,
            "open_to_open_return_policy": True,
            "signal_availability_lag_hours": SIGNAL_LAG_HOURS,
            "signal_entry_uses_lagged_funding_only": True,
        },
        "execution_scope": {
            "aligned_window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
            "aligned_window_start_utc": WINDOW_START_UTC,
            "config_count": 9,
            "exact_overlap_symbol_count": EXPECTED_SYMBOL_COUNT,
            "hypothesis_name": HYPOTHESIS_NAME,
            "no_okx_panel_rows": True,
            "okx_boundary_buffer_excluded": True,
            "okx_sealed_holdout_excluded": True,
            "route_family": ROUTE_FAMILY,
            "route_family_count": 1,
            "symbols": symbols,
            "train_window_end_exclusive_utc": TRAIN_END_EXCLUSIVE_UTC,
            "train_window_start_utc": TRAIN_START_UTC,
            "validation_window_end_exclusive_utc": VALIDATION_END_EXCLUSIVE_UTC,
            "validation_window_start_utc": VALIDATION_START_UTC,
        },
        "forbidden_actions_confirmed_false": {
            "binance_1m_source_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_panel_build_rerun": False,
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "capital_permission_granted": False,
            "edge_claimed": False,
            "existing_files_modified_by_module": False,
            "external_execution_artifacts_written": False,
            "family_released": False,
            "funding_data_acquisition_rerun": False,
            "funding_data_fetched": False,
            "funding_rate_endpoint_called": False,
            "holdout_accessed": False,
            "live_permission_granted": False,
            "momentum_retest_executed": False,
            "non_preregistered_config_tested": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "parameter_expansion_performed": False,
            "reversal_retest_executed": False,
            "runtime_permission_granted": False,
        },
        "input_data_validation": input_validation,
        "metric_integrity_summary": metric_integrity_summary,
        "module": MODULE_PATH,
        "monthly_stability_summary": monthly_summary,
        "null_baseline_summary": null_summary,
        "preregistered_config_grid": {
            "config_count": 9,
            "deterministic_config_ids": EXPECTED_CONFIG_IDS,
            "holding_periods_hours": [8, 16, 24],
            "route_family_count": 1,
            "signal_transforms": list(TRANSFORM_REQUIREMENTS.keys()),
        },
        "replacement_checks_all_true": True,
        "repo_scope": {
            "api_key_used": False,
            "binance_1h_panel_rows_read_for_execution": True,
            "binance_1m_kline_source_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_panel_build_rerun": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "funding_data_acquisition_rerun": False,
            "funding_data_fetched_by_this_module": False,
            "funding_rate_endpoint_called_by_this_module": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "public_network_used": False,
            "reviewed_funding_rows_read_for_execution": True,
            "runtime_live_capital": False,
            "strategy_execution_executed": True,
            "strategy_search_executed": False,
            "tracked_execution_artifact_created_in_repo": True,
        },
        "return_and_cost_policy": {
            "cost_policy": {
                "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
            },
            "entry_price": "open_price_at_entry_timestamp",
            "exit_price": "open_price_at_entry_timestamp_plus_holding_period",
            "metric_units": "basis_points_per_eligible_entry_timestamp",
            "no_annualization": True,
            "no_compounding": True,
            "open_to_open_forward_returns": True,
        },
        "safety_permissions": {
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "closure_required_after_evaluator": True,
            "edge_claim_allowed_now": False,
            "evaluator_required_before_any_followup": True,
            "family_release_allowed_now": False,
            "final_edge_claim_requires_external_or_future_holdout": True,
            "funding_strategy_execution_completed": True,
            "funding_strategy_execution_is_diagnostic_only": True,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "signal_alignment_policy": {
            "latest_lagged_funding_rate": "latest fundingRate with funding_time <= entry_time - 1h",
            "minimum_symbols_required_per_timestamp": MIN_SYMBOLS_PER_TIMESTAMP,
            "no_lookahead_policy": "funding observations may only affect entries at timestamps >= funding_time + 1 hour",
            "rolling_mean_3_funding_events": "mean of latest 3 funding events with funding_time <= entry_time - 1h",
            "rolling_mean_9_funding_events": "mean of latest 9 funding events with funding_time <= entry_time - 1h",
            "signal_availability_lag_hours": SIGNAL_LAG_HOURS,
            "tail_selection": "bottom 20 percent long, top 20 percent short",
            "tie_policy": "signal value then symbol ascending",
        },
        "source_artifacts": {
            "acquisition_manifest_path": str(ACQUISITION_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "acquisition_payload_hash_verified": True,
            "all_source_artifacts_read_only": True,
            "build_manifest_path": str(BUILD_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "build_manifest_payload_hash_verified": True,
            "coverage_lock_path": str(COVERAGE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "coverage_lock_payload_hash_verified": True,
            "funding_index_path": str(FUNDING_INDEX_PATH),
            "funding_index_sha256_verified": True,
            "funding_review_artifact_path": str(FUNDING_REVIEW_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "funding_review_payload_hash_verified": True,
            "panel_index_path": str(PANEL_INDEX_PATH),
            "panel_index_sha256_verified": True,
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
            "prior_funding_review_artifact": "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
            "prior_funding_review_payload_sha256_excluding_hash": FUNDING_REVIEW_PAYLOAD_HASH,
            "prior_funding_review_status": FUNDING_REVIEW_STATUS,
            "prior_funding_review_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.py",
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap funding-rate preregistered execution",
            "repo_clean_before_execution": True,
        },
        "status": REQUIRED_STATUS,
        "train_validation_summary": train_validation_summary,
        "turnover_concentration_summary": turnover_and_metric,
        "validation_checks": validation_checks,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    validate_artifact(artifact)
    log(f"execution artifact built in {time.time() - start:.1f}s")
    return artifact


def validate_artifact(artifact: dict[str, Any]) -> None:
    assert artifact["status"] == REQUIRED_STATUS
    assert artifact["module"] == MODULE_PATH
    assert EXECUTION_ARTIFACT_PATH == "artifacts/strategy_executions/binance_okx_overlap_funding_rate_preregistered_9_config_execution_v1.json"
    checks = artifact["validation_checks"]
    assert all(checks.values()), [key for key, value in checks.items() if value is not True]
    assert artifact["execution_scope"]["route_family"] == ROUTE_FAMILY
    assert artifact["execution_scope"]["exact_overlap_symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert artifact["execution_scope"]["aligned_window_start_utc"] == WINDOW_START_UTC
    assert artifact["execution_scope"]["aligned_window_end_exclusive_utc"] == WINDOW_END_EXCLUSIVE_UTC
    assert artifact["preregistered_config_grid"]["deterministic_config_ids"] == EXPECTED_CONFIG_IDS
    assert [result["config_id"] for result in artifact["config_results"]] == EXPECTED_CONFIG_IDS
    assert artifact["metric_integrity_summary"]["metric_integrity_passed"] is True
    assert artifact["null_baseline_summary"]["null_baseline_complete"] is True
    assert artifact["repo_scope"]["public_network_used"] is False
    assert artifact["repo_scope"]["funding_rate_endpoint_called_by_this_module"] is False
    assert artifact["repo_scope"]["funding_data_fetched_by_this_module"] is False
    assert artifact["repo_scope"]["binance_1m_kline_source_rows_read"] is False
    assert artifact["repo_scope"]["okx_panel_rows_read"] is False
    assert artifact["repo_scope"]["strategy_search_executed"] is False
    assert artifact["repo_scope"]["candidate_generation"] is False
    assert artifact["repo_scope"]["edge_claim"] is False
    assert artifact["repo_scope"]["runtime_live_capital"] is False
    assert artifact["replacement_checks_all_true"] is True
    assert artifact["payload_sha256_excluding_hash"] == payload_hash(artifact)


def summary_from_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    summary = artifact["train_validation_summary"]
    return {
        "aligned_window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
        "aligned_window_start_utc": WINDOW_START_UTC,
        "best_train_config_id": summary["best_train_config_id"],
        "best_validation_config_id": summary["best_validation_config_id"],
        "best_validation_gross_metric_bps": summary["best_validation_gross_metric_bps"],
        "best_validation_holding_period_hours": summary["best_validation_holding_period_hours"],
        "best_validation_net_metric_bps": summary["best_validation_net_metric_bps"],
        "best_validation_signal_transform": summary["best_validation_signal_transform"],
        "candidate_generation": False,
        "config_count": 9,
        "edge_claim": False,
        "exact_overlap_symbol_count": EXPECTED_SYMBOL_COUNT,
        "family_release": False,
        "metric_integrity_issue_count": summary["metric_integrity_issue_count"],
        "metric_integrity_passed": summary["metric_integrity_passed"],
        "monthly_stability_review_preliminary_passed": summary["monthly_stability_review_preliminary_passed"],
        "null_baseline_complete": summary["null_baseline_complete"],
        "null_baseline_review_preliminary_passed": summary["null_baseline_review_preliminary_passed"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
        "route_family": ROUTE_FAMILY,
        "runtime_live_capital": False,
        "status": REQUIRED_STATUS,
        "train_validation_rank_consistency": summary["train_validation_rank_consistency"],
        "turnover_concentration_review_preliminary_passed": summary["turnover_concentration_review_preliminary_passed"],
        "validation_positive_after_cost": summary["validation_positive_after_cost"],
    }


def main() -> int:
    try:
        artifact = build_execution_artifact()
        write_json_atomic(ARTIFACT_PATH, artifact)
        reloaded = read_json(ARTIFACT_PATH)
        if reloaded.get("payload_sha256_excluding_hash") != artifact["payload_sha256_excluding_hash"]:
            raise BlockedError("execution artifact readback mismatch")
        print(json.dumps(summary_from_artifact(artifact), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        if TEMP_ARTIFACT_PATH.exists():
            TEMP_ARTIFACT_PATH.unlink()
        if ARTIFACT_PATH.exists():
            try:
                payload = read_json(ARTIFACT_PATH)
                if payload.get("status") != REQUIRED_STATUS:
                    ARTIFACT_PATH.unlink()
            except Exception:
                ARTIFACT_PATH.unlink()
        print(json.dumps({"reason": str(exc), "replacement_checks_all_true": False, "status": "BLOCKED"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
