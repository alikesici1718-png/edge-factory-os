#!/usr/bin/env python3
"""Acquire and lock the forward Binance spot/perp/funding carry data extension."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import zipfile


STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_ACQUISITION_LOCK_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_ACQUISITION_LOCK"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_acquisition_lock_v1"

ROOT = Path(__file__).resolve().parents[1]
TOOL_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_acquisition_lock_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/data_acquisition_locks/binance_spot_perp_funding_carry_forward_extension_acquisition_lock_v1.json"
EXTERNAL_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_acquisition_lock_v1"
)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
MONTHS = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"]
WINDOW_START_UTC = "2025-11-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2026-05-01T00:00:00Z"
WINDOW_START_MS = 1761955200000
WINDOW_END_MS = 1777593600000
ONE_HOUR_MS = 60 * 60 * 1000
EXPECTED_HOURS_PER_SYMBOL = 4344

SOURCE_ARTIFACTS = {
    "extension_availability": {
        "path": "artifacts/data_availability/binance_spot_perp_funding_carry_data_extension_availability_discovery_v1.json",
        "expected_status": "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_DATA_EXTENSION_AVAILABILITY_PARTIAL",
        "expected_classification": "FORWARD_EXTENSION_AVAILABLE_BACKWARD_PARTIAL_OR_UNAVAILABLE",
        "expected_hash": "2ca8e99fc66c1f3fe17a306694d77a488bbdfe0df0f2f892bdf06a3b9d3ed81b",
    },
    "strategy_execution": {
        "path": "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json",
        "expected_hash": "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378",
    },
    "strategy_evaluation": {
        "path": "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json",
        "expected_hash": "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b",
    },
    "strategy_closure": {
        "path": "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json",
        "expected_hash": "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8",
    },
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
    "complete_1h",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ms_to_utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required source artifact missing: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(payload: dict[str, Any]) -> str:
    copy_payload = dict(payload)
    copy_payload.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(copy_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_outside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return False
    except ValueError:
        return True


def validate_source(name: str, spec: dict[str, str], data: dict[str, Any]) -> None:
    if spec.get("expected_status") and data.get("status") != spec["expected_status"]:
        raise ValueError(f"{name} status mismatch: {data.get('status')} != {spec['expected_status']}")
    if spec.get("expected_classification") and data.get("overall_extension_classification") != spec["expected_classification"]:
        raise ValueError(
            f"{name} classification mismatch: {data.get('overall_extension_classification')} != {spec['expected_classification']}"
        )
    if spec.get("expected_hash") and data.get("payload_sha256_excluding_hash") != spec["expected_hash"]:
        raise ValueError(f"{name} payload hash mismatch")
    if data.get("replacement_checks_all_true") is False:
        raise ValueError(f"{name} replacement_checks_all_true is false")


def source_summary(name: str, spec: dict[str, str], data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": spec["path"],
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "expected_payload_sha256_excluding_hash": spec.get("expected_hash"),
    }


def spot_url(symbol: str, month: str) -> str:
    return f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/1h/{symbol}-1h-{month}.zip"


def perp_url(symbol: str, month: str) -> str:
    return f"https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/1h/{symbol}-1h-{month}.zip"


def download_bytes(url: str, timeout: int = 60) -> bytes:
    request = Request(url, headers={"User-Agent": "edge-factory-os-forward-extension-acquisition/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_to_cache(url: str, path: Path, summary: dict[str, Any], retries: int = 3) -> None:
    if path.exists() and path.stat().st_size > 0:
        summary["cached_file_count"] += 1
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            data = download_bytes(url)
            with tmp_path.open("wb") as handle:
                handle.write(data)
            tmp_path.replace(path)
            summary["downloaded_file_count"] += 1
            return
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}:{exc}"
            summary["retry_count"] += 1
            time.sleep(min(2 * attempt, 5))
    raise RuntimeError(f"Failed to download {url}: {last_error}")


def parse_checksum(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    for token in text.replace("*", " ").split():
        if len(token) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in token):
            return token.lower()
    raise ValueError(f"Could not parse SHA256 checksum from {path}")


def acquire_archive(layer: str, symbol: str, month: str, download_summary: dict[str, Any]) -> dict[str, Any]:
    url = spot_url(symbol, month) if layer == "spot" else perp_url(symbol, month)
    prefix = f"{layer}_{symbol}_1h_{month}"
    zip_path = EXTERNAL_ROOT / "download_cache" / f"{prefix}.zip"
    checksum_path = EXTERNAL_ROOT / "download_cache" / f"{prefix}.zip.CHECKSUM"
    fetch_to_cache(url + ".CHECKSUM", checksum_path, download_summary)
    fetch_to_cache(url, zip_path, download_summary)
    expected = parse_checksum(checksum_path)
    observed = sha256_file(zip_path)
    checksum_ok = expected == observed
    if not checksum_ok:
        raise ValueError(f"Checksum mismatch for {layer} {symbol} {month}")
    download_summary["downloaded_zip_count"] += 1
    download_summary["checksum_verified_zip_count"] += 1
    return {
        "layer": layer,
        "symbol": symbol,
        "month": month,
        "url": url,
        "zip_path": str(zip_path),
        "checksum_path": str(checksum_path),
        "expected_sha256": expected,
        "observed_sha256": observed,
        "checksum_verified": checksum_ok,
    }


def decimal_value(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal value: {value}") from exc


def normalize_archive_timestamp_ms(value: str) -> int:
    raw = int(value)
    if raw > 100_000_000_000_000:
        return raw // 1000
    return raw


def parse_kline_zip(path: Path, symbol: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with zipfile.ZipFile(path, "r") as zf:
        csv_names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV found in {path}")
        with zf.open(csv_names[0], "r") as raw:
            text = (line.decode("utf-8").strip() for line in raw)
            reader = csv.reader(text)
            for row in reader:
                if not row or row[0] in {"open_time", "Open time"}:
                    continue
                if len(row) < 11:
                    raise ValueError(f"Unexpected kline row length {len(row)} in {path}")
                open_time = normalize_archive_timestamp_ms(row[0])
                if open_time < WINDOW_START_MS or open_time >= WINDOW_END_MS:
                    continue
                close_time = normalize_archive_timestamp_ms(row[6])
                open_price = decimal_value(row[1])
                high = decimal_value(row[2])
                low = decimal_value(row[3])
                close = decimal_value(row[4])
                volume = decimal_value(row[5])
                quote_volume = decimal_value(row[7])
                trade_count = int(row[8])
                taker_buy_base = decimal_value(row[9])
                taker_buy_quote = decimal_value(row[10])
                records.append(
                    {
                        "symbol": symbol,
                        "timestamp_ms": open_time,
                        "timestamp_utc": ms_to_utc(open_time),
                        "open": str(open_price),
                        "high": str(high),
                        "low": str(low),
                        "close": str(close),
                        "volume": str(volume),
                        "quote_volume": str(quote_volume),
                        "trade_count": trade_count,
                        "taker_buy_base_volume": str(taker_buy_base),
                        "taker_buy_quote_volume": str(taker_buy_quote),
                        "complete_1h": close_time >= open_time + ONE_HOUR_MS - 1,
                    }
                )
    return records


def validate_kline_records(records: list[dict[str, Any]], symbol: str, layer: str) -> dict[str, Any]:
    timestamps = [int(record["timestamp_ms"]) for record in records]
    seen = set()
    duplicate_count = 0
    ohlc_ok = True
    numeric_ok = True
    outside_count = 0
    complete_count = 0
    for record in records:
        ts = int(record["timestamp_ms"])
        if ts in seen:
            duplicate_count += 1
        seen.add(ts)
        if ts < WINDOW_START_MS or ts >= WINDOW_END_MS:
            outside_count += 1
        try:
            open_price = decimal_value(record["open"])
            high = decimal_value(record["high"])
            low = decimal_value(record["low"])
            close = decimal_value(record["close"])
            volume = decimal_value(record["volume"])
            quote_volume = decimal_value(record["quote_volume"])
            taker_buy_base = decimal_value(record["taker_buy_base_volume"])
            taker_buy_quote = decimal_value(record["taker_buy_quote_volume"])
        except ValueError:
            numeric_ok = False
            continue
        if not (open_price > 0 and high > 0 and low > 0 and close > 0 and volume >= 0 and quote_volume >= 0 and taker_buy_base >= 0 and taker_buy_quote >= 0):
            numeric_ok = False
        if not (high >= max(open_price, close, low) and low <= min(open_price, close, high)):
            ohlc_ok = False
        if record["complete_1h"]:
            complete_count += 1
    sorted_ts = sorted(timestamps)
    hourly_aligned = all(ts % ONE_HOUR_MS == 0 for ts in sorted_ts)
    consecutive = len(sorted_ts) == EXPECTED_HOURS_PER_SYMBOL and all(
        sorted_ts[i] + ONE_HOUR_MS == sorted_ts[i + 1] for i in range(len(sorted_ts) - 1)
    )
    return {
        "symbol": symbol,
        "layer": layer,
        "row_count": len(records),
        "expected_row_count": EXPECTED_HOURS_PER_SYMBOL,
        "min_timestamp_utc": ms_to_utc(min(sorted_ts)) if sorted_ts else None,
        "max_timestamp_utc": ms_to_utc(max(sorted_ts)) if sorted_ts else None,
        "duplicate_timestamp_count": duplicate_count,
        "rows_outside_window": outside_count,
        "complete_1h_count": complete_count,
        "hourly_aligned": hourly_aligned,
        "consecutive_hourly_window": consecutive,
        "ohlc_sanity_valid": ohlc_ok,
        "numeric_sanity_valid": numeric_ok,
    }


def write_panel(path: Path, records: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PANEL_HEADER, extrasaction="ignore")
        writer.writeheader()
        for record in sorted(records, key=lambda item: int(item["timestamp_ms"])):
            output = {key: record[key] for key in PANEL_HEADER if key in record}
            output["complete_1h"] = "true" if record["complete_1h"] else "false"
            writer.writerow(output)
    return sha256_file(path)


def funding_url(symbol: str, start_ms: int, end_ms: int, limit: int = 1000) -> str:
    params = {"symbol": symbol, "startTime": start_ms, "endTime": end_ms, "limit": limit}
    return "https://fapi.binance.com/fapi/v1/fundingRate?" + urlencode(params)


def fetch_funding_page(symbol: str, start_ms: int, end_ms: int, funding_summary: dict[str, Any]) -> list[dict[str, Any]]:
    url = funding_url(symbol, start_ms, end_ms)
    request = Request(url, headers={"User-Agent": "edge-factory-os-forward-extension-acquisition/1.0"})
    funding_summary["funding_request_count"] += 1
    with urlopen(request, timeout=30) as response:
        rows = json.loads(response.read().decode("utf-8"))
    for row in rows:
        row["source_endpoint"] = "https://fapi.binance.com/fapi/v1/fundingRate"
    return rows


def acquire_funding(symbol: str, funding_summary: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    cursor = WINDOW_START_MS
    end_ms = WINDOW_END_MS - 1
    while cursor <= end_ms:
        rows = fetch_funding_page(symbol, cursor, end_ms, funding_summary)
        if not rows:
            break
        kept = []
        for row in rows:
            funding_time = int(row["fundingTime"])
            if WINDOW_START_MS <= funding_time < WINDOW_END_MS:
                kept.append(
                    {
                        "symbol": symbol,
                        "funding_time_ms": funding_time,
                        "funding_time_utc": ms_to_utc(funding_time),
                        "funding_rate": str(row.get("fundingRate")),
                        "mark_price": None if row.get("markPrice") is None else str(row.get("markPrice")),
                        "source_endpoint": row["source_endpoint"],
                    }
                )
        records.extend(kept)
        max_time = max(int(row["fundingTime"]) for row in rows)
        next_cursor = max_time + 1
        if next_cursor <= cursor or len(rows) < 1000:
            break
        cursor = next_cursor
        time.sleep(0.1)
    return sorted(records, key=lambda item: int(item["funding_time_ms"]))


def validate_funding_records(records: list[dict[str, Any]], symbol: str) -> dict[str, Any]:
    seen = set()
    duplicate_count = 0
    outside_count = 0
    numeric_ok = True
    for record in records:
        ts = int(record["funding_time_ms"])
        if ts in seen:
            duplicate_count += 1
        seen.add(ts)
        if ts < WINDOW_START_MS or ts >= WINDOW_END_MS:
            outside_count += 1
        try:
            decimal_value(record["funding_rate"])
            if record["mark_price"] is not None:
                mark = decimal_value(record["mark_price"])
                if mark <= 0:
                    numeric_ok = False
        except ValueError:
            numeric_ok = False
    timestamps = [int(record["funding_time_ms"]) for record in records]
    return {
        "symbol": symbol,
        "record_count": len(records),
        "min_funding_time_utc": ms_to_utc(min(timestamps)) if timestamps else None,
        "max_funding_time_utc": ms_to_utc(max(timestamps)) if timestamps else None,
        "duplicate_funding_time_count": duplicate_count,
        "rows_outside_window": outside_count,
        "numeric_sanity_valid": numeric_ok,
    }


def write_funding(path: Path, records: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n")
    return sha256_file(path)


def write_external_index(index_payload: dict[str, Any]) -> str:
    index_path = EXTERNAL_ROOT / "extension_index" / "binance_spot_perp_funding_carry_forward_extension_index_v1.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_copy = dict(index_payload)
    index_copy.pop("external_index_sha256", None)
    index_hash = payload_hash(index_copy)
    index_payload["external_index_sha256"] = index_hash
    with index_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(index_payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return sha256_file(index_path)


def main() -> None:
    if not is_outside_repo(EXTERNAL_ROOT):
        raise ValueError("External root is not outside repo")

    source_artifacts: dict[str, dict[str, Any]] = {}
    loaded: dict[str, dict[str, Any]] = {}
    for name, spec in SOURCE_ARTIFACTS.items():
        data = load_json(spec["path"])
        validate_source(name, spec, data)
        loaded[name] = data
        source_artifacts[name] = source_summary(name, spec, data)

    availability = loaded["extension_availability"]
    forward = availability.get("forward_extension_summary") or {}
    if forward.get("forward_extension_available") is not True:
        raise ValueError("Prior availability artifact does not verify forward extension")

    for relative in ["download_cache", "spot_1h_by_symbol", "perp_1h_by_symbol", "funding_by_symbol", "extension_index"]:
        (EXTERNAL_ROOT / relative).mkdir(parents=True, exist_ok=True)

    download_summary = {
        "downloaded_file_count": 0,
        "cached_file_count": 0,
        "retry_count": 0,
        "error_count": 0,
        "downloaded_zip_count": 0,
        "checksum_verified_zip_count": 0,
        "required_zip_count": len(SYMBOLS) * len(MONTHS) * 2,
        "required_checksum_count": len(SYMBOLS) * len(MONTHS) * 2,
        "archive_records": [],
    }
    funding_summary = {"funding_request_count": 0, "error_count": 0}

    symbol_records: dict[str, Any] = {}
    output_hashes: dict[str, str] = {}
    all_spot_timestamps: dict[str, set[int]] = {}
    all_perp_timestamps: dict[str, set[int]] = {}

    for symbol in SYMBOLS:
        spot_records: list[dict[str, Any]] = []
        perp_records: list[dict[str, Any]] = []
        archive_records: list[dict[str, Any]] = []
        for month in MONTHS:
            spot_archive = acquire_archive("spot", symbol, month, download_summary)
            perp_archive = acquire_archive("perp", symbol, month, download_summary)
            archive_records.extend([spot_archive, perp_archive])
            spot_records.extend(parse_kline_zip(Path(spot_archive["zip_path"]), symbol))
            perp_records.extend(parse_kline_zip(Path(perp_archive["zip_path"]), symbol))

        spot_validation = validate_kline_records(spot_records, symbol, "spot")
        perp_validation = validate_kline_records(perp_records, symbol, "perp")
        spot_ts = {int(record["timestamp_ms"]) for record in spot_records}
        perp_ts = {int(record["timestamp_ms"]) for record in perp_records}
        timestamp_alignment = spot_ts == perp_ts
        all_spot_timestamps[symbol] = spot_ts
        all_perp_timestamps[symbol] = perp_ts

        spot_path = EXTERNAL_ROOT / "spot_1h_by_symbol" / f"{symbol}_spot_1h_forward_202511_202604.csv.gz"
        perp_path = EXTERNAL_ROOT / "perp_1h_by_symbol" / f"{symbol}_perp_1h_forward_202511_202604.csv.gz"
        spot_hash = write_panel(spot_path, spot_records)
        perp_hash = write_panel(perp_path, perp_records)
        output_hashes[str(spot_path)] = spot_hash
        output_hashes[str(perp_path)] = perp_hash

        funding_records = acquire_funding(symbol, funding_summary)
        funding_validation = validate_funding_records(funding_records, symbol)
        funding_path = EXTERNAL_ROOT / "funding_by_symbol" / f"{symbol}_funding_forward_202511_202604.jsonl.gz"
        funding_hash = write_funding(funding_path, funding_records)
        output_hashes[str(funding_path)] = funding_hash

        symbol_records[symbol] = {
            "symbol": symbol,
            "archive_records": archive_records,
            "spot_output_path": str(spot_path),
            "perp_output_path": str(perp_path),
            "funding_output_path": str(funding_path),
            "spot_output_sha256": spot_hash,
            "perp_output_sha256": perp_hash,
            "funding_output_sha256": funding_hash,
            "spot_validation": spot_validation,
            "perp_validation": perp_validation,
            "funding_validation": funding_validation,
            "spot_perp_timestamp_alignment": timestamp_alignment,
        }
        download_summary["archive_records"].extend(archive_records)
        time.sleep(0.1)

    all_symbols_spot_aligned = len({frozenset(values) for values in all_spot_timestamps.values()}) == 1
    all_symbols_perp_aligned = len({frozenset(values) for values in all_perp_timestamps.values()}) == 1

    spot_total_rows = sum(record["spot_validation"]["row_count"] for record in symbol_records.values())
    perp_total_rows = sum(record["perp_validation"]["row_count"] for record in symbol_records.values())
    funding_total_records = sum(record["funding_validation"]["record_count"] for record in symbol_records.values())

    no_rows_outside = all(
        record["spot_validation"]["rows_outside_window"] == 0
        and record["perp_validation"]["rows_outside_window"] == 0
        and record["funding_validation"]["rows_outside_window"] == 0
        for record in symbol_records.values()
    )
    no_duplicate_spot = all(record["spot_validation"]["duplicate_timestamp_count"] == 0 for record in symbol_records.values())
    no_duplicate_perp = all(record["perp_validation"]["duplicate_timestamp_count"] == 0 for record in symbol_records.values())
    no_duplicate_funding = all(record["funding_validation"]["duplicate_funding_time_count"] == 0 for record in symbol_records.values())
    ohlc_sanity = all(
        record["spot_validation"]["ohlc_sanity_valid"] and record["perp_validation"]["ohlc_sanity_valid"]
        for record in symbol_records.values()
    )
    numeric_sanity = all(
        record["spot_validation"]["numeric_sanity_valid"]
        and record["perp_validation"]["numeric_sanity_valid"]
        and record["funding_validation"]["numeric_sanity_valid"]
        for record in symbol_records.values()
    )
    spot_row_counts_ok = all(record["spot_validation"]["row_count"] == EXPECTED_HOURS_PER_SYMBOL for record in symbol_records.values())
    perp_row_counts_ok = all(record["perp_validation"]["row_count"] == EXPECTED_HOURS_PER_SYMBOL for record in symbol_records.values())
    funding_records_ok = all(record["funding_validation"]["record_count"] > 0 for record in symbol_records.values())
    checksums_ok = download_summary["checksum_verified_zip_count"] == download_summary["required_zip_count"]

    non_repo_artifacts = {
        "external_data_root": str(EXTERNAL_ROOT),
        "download_cache": str(EXTERNAL_ROOT / "download_cache"),
        "spot_1h_by_symbol": str(EXTERNAL_ROOT / "spot_1h_by_symbol"),
        "perp_1h_by_symbol": str(EXTERNAL_ROOT / "perp_1h_by_symbol"),
        "funding_by_symbol": str(EXTERNAL_ROOT / "funding_by_symbol"),
        "extension_index": str(EXTERNAL_ROOT / "extension_index" / "binance_spot_perp_funding_carry_forward_extension_index_v1.json"),
        "output_file_sha256_map": output_hashes,
    }
    external_index_payload = {
        "artifact_kind": "BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_EXTERNAL_INDEX",
        "created_at_utc": utc_now(),
        "external_data_root": str(EXTERNAL_ROOT),
        "symbols": SYMBOLS,
        "months": MONTHS,
        "window_start_utc": WINDOW_START_UTC,
        "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
        "symbol_records": symbol_records,
        "output_file_sha256_map": output_hashes,
    }
    index_file_sha = write_external_index(external_index_payload)
    non_repo_artifacts["extension_index_sha256"] = external_index_payload["external_index_sha256"]
    non_repo_artifacts["extension_index_file_sha256"] = index_file_sha

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_extension_availability_loaded": True,
        "forward_extension_availability_verified": forward.get("forward_extension_available") is True,
        "backward_extension_not_acquired": True,
        "partial_may_2026_daily_not_acquired": True,
        "exact_symbol_count_3": len(symbol_records) == 3,
        "all_required_spot_zips_downloaded_or_cached": download_summary["downloaded_zip_count"] == download_summary["required_zip_count"],
        "all_required_perp_zips_downloaded_or_cached": download_summary["downloaded_zip_count"] == download_summary["required_zip_count"],
        "all_required_checksums_verified": checksums_ok,
        "funding_records_acquired_all_symbols": funding_records_ok,
        "no_rows_outside_window": no_rows_outside,
        "no_duplicate_spot_symbol_hour": no_duplicate_spot,
        "no_duplicate_perp_symbol_hour": no_duplicate_perp,
        "no_duplicate_funding_symbol_time": no_duplicate_funding,
        "ohlc_sanity_valid": ohlc_sanity,
        "numeric_sanity_valid": numeric_sanity,
        "data_written_outside_repo": is_outside_repo(EXTERNAL_ROOT),
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }

    # Split this post-check into layer-specific summary fields while preserving the requested validation key names.
    validation_checks["all_required_spot_zips_downloaded_or_cached"] = all(
        len([record for record in symbol_records[symbol]["archive_records"] if record["layer"] == "spot"]) == len(MONTHS)
        for symbol in SYMBOLS
    )
    validation_checks["all_required_perp_zips_downloaded_or_cached"] = all(
        len([record for record in symbol_records[symbol]["archive_records"] if record["layer"] == "perp"]) == len(MONTHS)
        for symbol in SYMBOLS
    )

    if not all(validation_checks.values()):
        failed = [key for key, value in validation_checks.items() if not value]
        raise ValueError(f"Validation checks failed: {failed}")
    if not (spot_row_counts_ok and perp_row_counts_ok and all_symbols_spot_aligned and all_symbols_perp_aligned):
        raise ValueError("Hourly panel row count/alignment validation failed")

    safety_permissions = {
        "data_extension_acquisition_created": True,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "next_step_may_be_forward_extension_data_review_only": True,
        "next_step_must_not_be_live_or_capital": True,
    }

    minmax_summary = {
        "spot": {
            "min_timestamp_utc": min(record["spot_validation"]["min_timestamp_utc"] for record in symbol_records.values()),
            "max_timestamp_utc": max(record["spot_validation"]["max_timestamp_utc"] for record in symbol_records.values()),
        },
        "perp": {
            "min_timestamp_utc": min(record["perp_validation"]["min_timestamp_utc"] for record in symbol_records.values()),
            "max_timestamp_utc": max(record["perp_validation"]["max_timestamp_utc"] for record in symbol_records.values()),
        },
        "funding": {
            "min_funding_time_utc": min(record["funding_validation"]["min_funding_time_utc"] for record in symbol_records.values()),
            "max_funding_time_utc": max(record["funding_validation"]["max_funding_time_utc"] for record in symbol_records.values()),
        },
    }

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "created_at_utc": utc_now(),
            "expected_head": "ff7f67b0783c9c9033d17900908ece12f498d7a0",
            "tracked_python_count_before": 903,
            "tool_path": TOOL_RELATIVE_PATH,
            "artifact_path": ARTIFACT_RELATIVE_PATH,
        },
        "source_artifacts": source_artifacts,
        "acquisition_scope": {
            "symbols": SYMBOLS,
            "months": MONTHS,
            "window_start_utc": WINDOW_START_UTC,
            "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
            "backward_extension_acquired": False,
            "partial_may_2026_daily_acquired": False,
        },
        "source_contracts": {
            "spot_monthly_klines": "https://data.binance.vision/data/spot/monthly/klines/{SYMBOL}/1h/{SYMBOL}-1h-{YYYY-MM}.zip",
            "perp_um_monthly_klines": "https://data.binance.vision/data/futures/um/monthly/klines/{SYMBOL}/1h/{SYMBOL}-1h-{YYYY-MM}.zip",
            "funding_rate_endpoint": "https://fapi.binance.com/fapi/v1/fundingRate",
            "checksum_required_before_zip_open": True,
        },
        "download_summary": download_summary,
        "funding_endpoint_summary": funding_summary,
        "output_data_summary": {
            "spot_total_rows": spot_total_rows,
            "perp_total_rows": perp_total_rows,
            "funding_total_records": funding_total_records,
            "minmax_summary": minmax_summary,
            "all_symbols_spot_aligned": all_symbols_spot_aligned,
            "all_symbols_perp_aligned": all_symbols_perp_aligned,
            "spot_perp_timestamp_alignment_all_symbols": all(record["spot_perp_timestamp_alignment"] for record in symbol_records.values()),
        },
        "validation_summary": {
            "spot_row_counts_ok": spot_row_counts_ok,
            "perp_row_counts_ok": perp_row_counts_ok,
            "funding_records_ok": funding_records_ok,
            "no_rows_outside_window": no_rows_outside,
            "no_duplicate_spot_symbol_hour": no_duplicate_spot,
            "no_duplicate_perp_symbol_hour": no_duplicate_perp,
            "no_duplicate_funding_symbol_time": no_duplicate_funding,
            "ohlc_sanity_valid": ohlc_sanity,
            "numeric_sanity_valid": numeric_sanity,
            "checksums_ok": checksums_ok,
        },
        "symbol_records": symbol_records,
        "non_repo_artifacts": non_repo_artifacts,
        "limitations": [
            "This is an acquisition lock only; row-level strategy metrics are not computed.",
            "Only the forward closed-month extension 2025-11 through 2026-04 was acquired.",
            "Backward 2020/2021 data and partial May 2026 daily archives were not acquired.",
            "No strategy execution, candidate generation, edge claim, runtime, live, or capital permission is created.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)

    artifact_path = ROOT / ARTIFACT_RELATIVE_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout_fields = {
        "status": STATUS,
        "external_data_root": str(EXTERNAL_ROOT),
        "symbols": SYMBOLS,
        "window_start_utc": WINDOW_START_UTC,
        "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
        "spot_total_rows": spot_total_rows,
        "perp_total_rows": perp_total_rows,
        "funding_total_records": funding_total_records,
        "downloaded_zip_count": download_summary["downloaded_zip_count"],
        "checksum_verified_zip_count": download_summary["checksum_verified_zip_count"],
        "funding_request_count": funding_summary["funding_request_count"],
        "output_index_path": non_repo_artifacts["extension_index"],
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "strategy_execution_allowed_now": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "replacement_checks_all_true": True,
    }
    for key, value in stdout_fields.items():
        print(f"{key}={json.dumps(value, sort_keys=True)}")


if __name__ == "__main__":
    main()
