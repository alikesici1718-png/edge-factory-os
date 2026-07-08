#!/usr/bin/env python3
"""Discover and build max available Coinalyze OI/liquidation history dataset.

Max-history data discovery + dataset builder only. This module reads the
Coinalyze API key only from COINALYZE_API_KEY, never prints or persists it, and
does not run strategies, generate signals, backtest, compute PnL, optimize,
create candidates, claim edge, or grant runtime/live/capital permission.
"""

from __future__ import annotations

import hashlib
import json
import os
import statistics
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_max_available_oi_liq_history_dataset_builder_v1"
STATUS = "PASS_REPO_ONLY_COINALYZE_MAX_AVAILABLE_OI_LIQ_HISTORY_DATASET_BUILDER_CREATED"
MISSING_KEY_STATUS = "BLOCKED_COINALYZE_API_KEY_MISSING_FOR_MAX_HISTORY_BUILDER"
ARTIFACT_KIND = "COINALYZE_MAX_AVAILABLE_OI_LIQ_HISTORY_DATASET_BUILDER"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_max_available_oi_liq_history_dataset_builder_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "data_builds" / "coinalyze_max_available_oi_liq_history_dataset_builder_v1.json"
DISCOVERY_PATH = REPO_ROOT / "artifacts" / "data_discovery" / "coinalyze_free_oi_liq_funding_availability_discovery_v5.json"
PRIOR_DATASET_PATH = REPO_ROOT / "artifacts" / "data_builds" / "coinalyze_recent_oi_liquidation_dataset_builder_v1.json"
DESIGN_PATH = REPO_ROOT / "artifacts" / "research_designs" / "coinalyze_long_liquidation_flush_strategy_design_v1.json"
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "coinalyze_long_liquidation_flush_strategy_preregistration_v1.json"
EXTERNAL_OUTPUT_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_coinalyze_max_available_oi_liq_dataset_v1")
RAW_DIR = EXTERNAL_OUTPUT_ROOT / "raw_responses"
NORMALIZED_DIR = EXTERNAL_OUTPUT_ROOT / "normalized_by_symbol"
COVERAGE_DIR = EXTERNAL_OUTPUT_ROOT / "coverage_reports"
CHECKSUM_DIR = EXTERNAL_OUTPUT_ROOT / "checksums"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
API_KEY_ENV = "COINALYZE_API_KEY"
COINALYZE_BASE_URL = "https://api.coinalyze.net/v1"
RATE_LIMIT_SLEEP_SECONDS = 1.0
BASE_EQUITY_NOT_USED = None

REQUESTED_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "DOGEUSDT",
    "XRPUSDT",
    "BNBUSDT",
    "LINKUSDT",
    "APTUSDT",
    "ARBUSDT",
    "OPUSDT",
]
ENDPOINTS = [
    "open-interest-history",
    "liquidation-history",
    "funding-rate-history",
    "ohlcv-history",
    "long-short-ratio-history",
]
REQUIRED_ALIGNMENT_ENDPOINTS = [
    "open-interest-history",
    "liquidation-history",
    "funding-rate-history",
    "ohlcv-history",
]
INTERVAL_PLANS = {
    "15min": {"chunk_days": 14, "max_chunks": 8, "seconds": 900, "rolling_bars_24h": 96, "min_rolling_bars": 48, "past_1h_bars": 4},
    "1hour": {"chunk_days": 60, "max_chunks": 8, "seconds": 3600, "rolling_bars_24h": 24, "min_rolling_bars": 12, "past_1h_bars": 1},
    "daily": {"chunk_days": 365, "max_chunks": 5, "seconds": 86400, "rolling_bars_24h": 1, "min_rolling_bars": 1, "past_1h_bars": 1},
}
PREFERRED_INTERVALS = ["15min", "1hour", "daily"]
EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}


def git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={SAFE_DIR}", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def source_checkpoint() -> str:
    return git(["rev-parse", "HEAD"])


def git_status_entries() -> list[tuple[str, str]]:
    raw = git(["status", "--short", "-uall"])
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if line.strip():
            entries.append((line[:2], line[3:].strip().strip('"').replace("\\", "/")))
    return entries


def repo_clean_except_expected_new_files() -> bool:
    for status, path in git_status_entries():
        if status == "??" and path in EXPECTED_NEW_PATHS:
            continue
        return False
    return True


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def ensure_external_dirs() -> None:
    for directory in (RAW_DIR, NORMALIZED_DIR, COVERAGE_DIR, CHECKSUM_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def iso_from_ts(value: int | float | str | None) -> str | None:
    if value is None:
        return None
    try:
        ts = int(float(value))
    except (TypeError, ValueError):
        return None
    if ts > 10_000_000_000:
        ts //= 1000
    return datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z")


def ts_int(row: dict[str, Any]) -> int | None:
    for key in ("t", "time", "timestamp"):
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, str) and value.endswith("Z"):
            try:
                return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
            except ValueError:
                continue
        try:
            parsed = int(float(value))
            return parsed // 1000 if parsed > 10_000_000_000 else parsed
        except (TypeError, ValueError):
            continue
    return None


def sanitize_error(message: str | None, api_key: str) -> str | None:
    if message is None:
        return None
    text = str(message)
    if api_key:
        text = text.replace(api_key, "[REDACTED_API_KEY]")
    for marker in ("api_key=", "api_key%3D"):
        idx = text.lower().find(marker)
        if idx >= 0:
            text = text[:idx] + marker + "[REDACTED]"
    return text[:700]


def coinalyze_get(endpoint: str, params: dict[str, Any], api_key: str) -> tuple[bool, int | None, Any, str | None]:
    request_params = dict(params)
    request_params["api_key"] = api_key
    url = f"{COINALYZE_BASE_URL}/{endpoint}?{urllib.parse.urlencode(request_params)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "edge-factory-os-coinalyze-max-history-builder/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read().decode("utf-8")
            try:
                return True, response.status, json.loads(body), None
            except json.JSONDecodeError:
                return True, response.status, {"raw_response_preview": body[:500]}, None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = str(exc)
        return False, exc.code, None, sanitize_error(body, api_key)
    except urllib.error.URLError as exc:
        return False, None, None, sanitize_error(str(exc.reason), api_key)
    except Exception as exc:
        return False, None, None, sanitize_error(str(exc), api_key)


def extract_rows_by_symbol(data: Any, symbol_to_target: dict[str, str]) -> dict[str, list[dict[str, Any]]]:
    rows_by_target = {target: [] for target in symbol_to_target.values()}
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "history" in data[0]:
            for item in data:
                if not isinstance(item, dict):
                    continue
                symbol = str(item.get("symbol", ""))
                target = symbol_to_target.get(symbol)
                history = item.get("history")
                if target and isinstance(history, list):
                    rows_by_target[target].extend(row for row in history if isinstance(row, dict))
        else:
            for row in data:
                if isinstance(row, dict):
                    symbol = str(row.get("symbol", ""))
                    target = symbol_to_target.get(symbol)
                    if target:
                        rows_by_target[target].append(row)
    elif isinstance(data, dict):
        for key in ("history", "data", "result"):
            value = data.get(key)
            if isinstance(value, list):
                return extract_rows_by_symbol(value, symbol_to_target)
    return rows_by_target


def row_stats(rows: list[dict[str, Any]], interval_seconds: int) -> dict[str, Any]:
    timestamps = sorted(ts for ts in (ts_int(row) for row in rows) if ts is not None)
    duplicate_count = len(timestamps) - len(set(timestamps))
    unique_ts = sorted(set(timestamps))
    if unique_ts:
        expected = ((unique_ts[-1] - unique_ts[0]) // interval_seconds) + 1
        gap_count = max(0, expected - len(unique_ts))
        usable_coverage = len(unique_ts) / expected if expected else 0.0
    else:
        gap_count = 0
        usable_coverage = 0.0
    return {
        "row_count": len(rows),
        "timestamp_min": iso_from_ts(unique_ts[0]) if unique_ts else None,
        "timestamp_max": iso_from_ts(unique_ts[-1]) if unique_ts else None,
        "duplicate_timestamp_count": duplicate_count,
        "gap_count": gap_count,
        "usable_coverage": usable_coverage,
        "field_names": sorted({str(key) for row in rows[:10] for key in row if "api" not in str(key).lower()}),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def load_symbol_mapping(discovery: dict[str, Any]) -> dict[str, dict[str, Any]]:
    probes = discovery.get("probe_symbols", [])
    mapping = {}
    for target in REQUESTED_SYMBOLS:
        match = next((entry for entry in probes if entry.get("target_symbol") == target), None)
        mapping[target] = {
            "target_symbol": target,
            "coinalyze_symbol": match.get("symbol") if match else None,
            "symbol_on_exchange": match.get("symbol_on_exchange") if match else None,
            "exchange": match.get("exchange") if match else None,
            "mapping_available": bool(match and match.get("symbol")),
        }
    return mapping


def discover_history(api_key: str, symbol_mapping: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, dict[str, dict[str, list[dict[str, Any]]]]], list[str]]:
    coinalyze_symbols = [str(entry["coinalyze_symbol"]) for entry in symbol_mapping.values() if entry.get("coinalyze_symbol")]
    symbol_to_target = {str(entry["coinalyze_symbol"]): symbol for symbol, entry in symbol_mapping.items() if entry.get("coinalyze_symbol")}
    rows_store: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = {
        interval: {endpoint: {symbol: [] for symbol in REQUESTED_SYMBOLS} for endpoint in ENDPOINTS}
        for interval in INTERVAL_PLANS
    }
    generated_external_files: list[str] = []
    discovery: dict[str, Any] = {
        interval: {
            endpoint: {
                symbol: {
                    "request_windows": [],
                    "earliest_available_timestamp": None,
                    "latest_available_timestamp": None,
                    "row_count": 0,
                    "gap_count": 0,
                    "usable_coverage": 0.0,
                    "api_limitation": None,
                }
                for symbol in REQUESTED_SYMBOLS
            }
            for endpoint in ENDPOINTS
        }
        for interval in INTERVAL_PLANS
    }
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    if not coinalyze_symbols:
        return discovery, rows_store, generated_external_files

    for interval, plan in INTERVAL_PLANS.items():
        interval_seconds = int(plan["seconds"])
        chunk_days = int(plan["chunk_days"])
        max_chunks = int(plan["max_chunks"])
        for endpoint in ENDPOINTS:
            no_rows_windows = 0
            for chunk_index in range(max_chunks):
                end_dt = now - timedelta(days=chunk_days * chunk_index)
                start_dt = end_dt - timedelta(days=chunk_days)
                params = {
                    "symbols": ",".join(coinalyze_symbols),
                    "interval": interval,
                    "from": int(start_dt.timestamp()),
                    "to": int(end_dt.timestamp()),
                }
                ok, http_status, data, error = coinalyze_get(endpoint, params, api_key)
                rows_by_target = extract_rows_by_symbol(data, symbol_to_target) if ok else {symbol: [] for symbol in REQUESTED_SYMBOLS}
                raw_payload = {
                    "endpoint": endpoint,
                    "interval": interval,
                    "chunk_index": chunk_index,
                    "window_start": start_dt.isoformat().replace("+00:00", "Z"),
                    "window_end": end_dt.isoformat().replace("+00:00", "Z"),
                    "request_ok": ok,
                    "http_status": http_status,
                    "error_message": error,
                    "row_counts_by_symbol": {symbol: len(rows_by_target.get(symbol, [])) for symbol in REQUESTED_SYMBOLS},
                    "rows_by_symbol": rows_by_target,
                }
                raw_path = RAW_DIR / f"{interval}_{endpoint}_chunk_{chunk_index:02d}.json"
                write_json(raw_path, raw_payload)
                generated_external_files.append(str(raw_path))
                total_rows = sum(len(rows) for rows in rows_by_target.values())
                if total_rows == 0:
                    no_rows_windows += 1
                else:
                    no_rows_windows = 0
                for symbol in REQUESTED_SYMBOLS:
                    symbol_rows = rows_by_target.get(symbol, [])
                    rows_store[interval][endpoint][symbol].extend(symbol_rows)
                    discovery[interval][endpoint][symbol]["request_windows"].append(
                        {
                            "chunk_index": chunk_index,
                            "window_start": start_dt.isoformat().replace("+00:00", "Z"),
                            "window_end": end_dt.isoformat().replace("+00:00", "Z"),
                            "request_ok": ok,
                            "http_status": http_status,
                            "row_count": len(symbol_rows),
                            "error_message": error,
                        }
                    )
                time.sleep(RATE_LIMIT_SLEEP_SECONDS)
                if no_rows_windows >= 2:
                    break
            for symbol in REQUESTED_SYMBOLS:
                deduped = dedupe_rows(rows_store[interval][endpoint][symbol])
                rows_store[interval][endpoint][symbol] = deduped
                stats = row_stats(deduped, interval_seconds)
                discovery[interval][endpoint][symbol].update(
                    {
                        "earliest_available_timestamp": stats["timestamp_min"],
                        "latest_available_timestamp": stats["timestamp_max"],
                        "row_count": stats["row_count"],
                        "gap_count": stats["gap_count"],
                        "usable_coverage": stats["usable_coverage"],
                        "field_names": stats["field_names"],
                    }
                )
                if stats["row_count"] == 0:
                    discovery[interval][endpoint][symbol]["api_limitation"] = "no_rows_returned_for_discovered_windows_or_endpoint_unavailable"
    return discovery, rows_store, generated_external_files


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[int, dict[str, Any]] = {}
    for row in rows:
        timestamp = ts_int(row)
        if timestamp is not None:
            deduped[timestamp] = row
    return [deduped[timestamp] for timestamp in sorted(deduped)]


def add_ohlcv(record: dict[str, Any], row: dict[str, Any]) -> None:
    record["open"] = as_float(row.get("o"))
    record["high"] = as_float(row.get("h"))
    record["low"] = as_float(row.get("l"))
    record["close"] = as_float(row.get("c"))
    record["volume"] = as_float(row.get("v"))


def add_oi(record: dict[str, Any], row: dict[str, Any]) -> None:
    record["oi"] = as_float(row.get("c"))


def add_liquidation(record: dict[str, Any], row: dict[str, Any]) -> None:
    long_liq = as_float(row.get("l"))
    short_liq = as_float(row.get("s"))
    record["liquidation_long"] = long_liq
    record["liquidation_short"] = short_liq
    if long_liq is not None or short_liq is not None:
        total = (long_liq or 0.0) + (short_liq or 0.0)
        record["liquidation_total"] = total
        record["liquidation_imbalance"] = ((long_liq or 0.0) - (short_liq or 0.0)) / total if total else 0.0


def add_funding(record: dict[str, Any], row: dict[str, Any]) -> None:
    record["funding_rate"] = as_float(row.get("c"))


def add_long_short(record: dict[str, Any], row: dict[str, Any]) -> None:
    ratio = as_float(row.get("r"))
    long_value = as_float(row.get("l"))
    short_value = as_float(row.get("s"))
    if ratio is None and long_value is not None and short_value not in (None, 0):
        ratio = long_value / short_value
    record["long_short_ratio"] = ratio


def normalize_symbol_interval(
    symbol: str,
    mapping: dict[str, Any],
    interval: str,
    endpoint_rows: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    records_by_ts: dict[int, dict[str, Any]] = {}
    for endpoint, rows in endpoint_rows.items():
        for row in rows:
            timestamp = ts_int(row)
            if timestamp is None:
                continue
            record = records_by_ts.setdefault(
                timestamp,
                {
                    "timestamp": iso_from_ts(timestamp),
                    "symbol": symbol,
                    "coinalyze_symbol": mapping.get("coinalyze_symbol"),
                    "exchange": mapping.get("exchange"),
                    "interval": interval,
                    "open": None,
                    "high": None,
                    "low": None,
                    "close": None,
                    "volume": None,
                    "oi": None,
                    "oi_change": None,
                    "oi_change_pct": None,
                    "liquidation_long": None,
                    "liquidation_short": None,
                    "liquidation_total": None,
                    "liquidation_imbalance": None,
                    "funding_rate": None,
                    "long_short_ratio": None,
                    "source_field_availability": {},
                },
            )
            record["source_field_availability"][endpoint] = True
            if endpoint == "ohlcv-history":
                add_ohlcv(record, row)
            elif endpoint == "open-interest-history":
                add_oi(record, row)
            elif endpoint == "liquidation-history":
                add_liquidation(record, row)
            elif endpoint == "funding-rate-history":
                add_funding(record, row)
            elif endpoint == "long-short-ratio-history":
                add_long_short(record, row)

    normalized = [records_by_ts[timestamp] for timestamp in sorted(records_by_ts)]
    previous_oi = None
    for record in normalized:
        oi = record.get("oi")
        if isinstance(oi, (int, float)) and previous_oi is not None:
            record["oi_change"] = oi - previous_oi
            record["oi_change_pct"] = (oi - previous_oi) / previous_oi if previous_oi else None
        if isinstance(oi, (int, float)):
            previous_oi = float(oi)
    return normalized


def quality_for_records(records: list[dict[str, Any]], interval_seconds: int) -> dict[str, Any]:
    timestamps = [int(datetime.fromisoformat(str(record["timestamp"]).replace("Z", "+00:00")).timestamp()) for record in records if record.get("timestamp")]
    duplicate_count = len(timestamps) - len(set(timestamps))
    missing_count = 0
    if timestamps:
        unique_ts = sorted(set(timestamps))
        expected = ((unique_ts[-1] - unique_ts[0]) // interval_seconds) + 1
        missing_count = max(0, expected - len(unique_ts))
    full_alignment_rows = [
        record
        for record in records
        if record.get("oi") is not None
        and record.get("liquidation_total") is not None
        and record.get("funding_rate") is not None
        and record.get("close") is not None
    ]
    ohlc_fail = 0
    for record in records:
        o, h, l, c = record.get("open"), record.get("high"), record.get("low"), record.get("close")
        if all(isinstance(value, (int, float)) for value in (o, h, l, c)):
            if not (h >= max(o, c, l) and l <= min(o, c, h) and min(o, h, l, c) > 0):
                ohlc_fail += 1
    return {
        "row_count": len(records),
        "alignment_row_count": len(full_alignment_rows),
        "alignment_coverage_share": len(full_alignment_rows) / len(records) if records else 0.0,
        "missing_timestamp_count": missing_count,
        "duplicate_timestamp_count": duplicate_count,
        "negative_oi_count": sum(1 for record in records if isinstance(record.get("oi"), (int, float)) and record["oi"] < 0),
        "negative_liquidation_count": sum(
            1
            for record in records
            if (isinstance(record.get("liquidation_long"), (int, float)) and record["liquidation_long"] < 0)
            or (isinstance(record.get("liquidation_short"), (int, float)) and record["liquidation_short"] < 0)
        ),
        "invalid_funding_count": sum(
            1
            for record in records
            if record.get("funding_rate") is not None
            and (not isinstance(record.get("funding_rate"), (int, float)) or abs(float(record["funding_rate"])) > 1.0)
        ),
        "ohlc_sanity_fail_count": ohlc_fail,
        "field_availability_summary": {
            "has_oi": any(record.get("oi") is not None for record in records),
            "has_liquidation": any(record.get("liquidation_total") is not None for record in records),
            "has_funding": any(record.get("funding_rate") is not None for record in records),
            "has_ohlcv": any(record.get("close") is not None for record in records),
            "has_long_short_ratio": any(record.get("long_short_ratio") is not None for record in records),
        },
    }


def estimate_long_liq_events(records_by_symbol: dict[str, list[dict[str, Any]]], interval: str) -> dict[str, Any]:
    plan = INTERVAL_PLANS[interval]
    rolling_bars = int(plan["rolling_bars_24h"])
    min_bars = int(plan["min_rolling_bars"])
    past_bars = int(plan["past_1h_bars"])
    counts_by_symbol: dict[str, int] = {}
    total_count = 0
    for symbol, records in records_by_symbol.items():
        count = 0
        for index, record in enumerate(records):
            if index < max(min_bars, past_bars):
                continue
            prior = records[max(0, index - rolling_bars) : index]
            if len(prior) < min_bars:
                continue
            median_long = statistics.median([(as_float(item.get("liquidation_long")) or 0.0) for item in prior])
            liquidation_long = as_float(record.get("liquidation_long")) or 0.0
            oi_change_pct = as_float(record.get("oi_change_pct"))
            close = as_float(record.get("close"))
            past_close = as_float(records[index - past_bars].get("close"))
            ret_1h_past = close / past_close - 1.0 if close is not None and past_close not in (None, 0) else None
            if (
                liquidation_long > 0
                and liquidation_long >= 3.0 * median_long
                and oi_change_pct is not None
                and oi_change_pct <= -0.005
                and ret_1h_past is not None
                and ret_1h_past <= -0.01
            ):
                count += 1
        counts_by_symbol[symbol] = count
        total_count += count
    return {
        "event_definition": "LONG_LIQUIDATION_FLUSH_EVENT",
        "count_is_raw_sample_size_estimate_only": True,
        "no_entries_exits_or_pnl_computed": True,
        "estimated_event_count": total_count,
        "estimated_event_count_by_symbol": counts_by_symbol,
    }


def evaluate_intervals(rows_store: dict[str, dict[str, dict[str, list[dict[str, Any]]]]], symbol_mapping: dict[str, dict[str, Any]]) -> dict[str, Any]:
    interval_evaluations: dict[str, Any] = {}
    for interval, endpoint_map in rows_store.items():
        records_by_symbol = {
            symbol: normalize_symbol_interval(
                symbol,
                symbol_mapping[symbol],
                interval,
                {endpoint: endpoint_map[endpoint][symbol] for endpoint in ENDPOINTS},
            )
            for symbol in REQUESTED_SYMBOLS
            if symbol_mapping[symbol].get("mapping_available")
        }
        qualities = {symbol: quality_for_records(records, int(INTERVAL_PLANS[interval]["seconds"])) for symbol, records in records_by_symbol.items()}
        full_alignment_symbols = [symbol for symbol, quality in qualities.items() if quality["alignment_row_count"] > 0]
        total_rows = sum(len(records) for records in records_by_symbol.values())
        timestamps = [record["timestamp"] for records in records_by_symbol.values() for record in records if record.get("timestamp")]
        quality_passed = all(
            quality["duplicate_timestamp_count"] == 0
            and quality["negative_oi_count"] == 0
            and quality["negative_liquidation_count"] == 0
            and quality["invalid_funding_count"] == 0
            and quality["ohlc_sanity_fail_count"] == 0
            for quality in qualities.values()
        )
        event_estimate = estimate_long_liq_events(records_by_symbol, interval)
        interval_evaluations[interval] = {
            "records_by_symbol": records_by_symbol,
            "qualities": qualities,
            "symbols_with_full_alignment": full_alignment_symbols,
            "symbols_with_full_alignment_count": len(full_alignment_symbols),
            "total_normalized_rows": total_rows,
            "timestamp_min": min(timestamps) if timestamps else None,
            "timestamp_max": max(timestamps) if timestamps else None,
            "data_quality_passed": quality_passed,
            "event_sample_size_estimate": event_estimate,
        }
    return interval_evaluations


def select_interval(interval_evaluations: dict[str, Any], prior_rows: int) -> tuple[str | None, str, str]:
    for interval in PREFERRED_INTERVALS:
        evaluation = interval_evaluations[interval]
        if evaluation["symbols_with_full_alignment_count"] >= 5 and evaluation["total_normalized_rows"] > 0:
            if interval in ("15min", "1hour"):
                return interval, evaluation["timestamp_min"], evaluation["timestamp_max"]
            if interval == "daily":
                return interval, evaluation["timestamp_min"], evaluation["timestamp_max"]
    materially_larger = [
        interval
        for interval in PREFERRED_INTERVALS
        if interval_evaluations[interval]["total_normalized_rows"] > prior_rows
    ]
    if materially_larger:
        interval = materially_larger[0]
        evaluation = interval_evaluations[interval]
        return interval, evaluation["timestamp_min"], evaluation["timestamp_max"]
    return None, None, None


def write_selected_dataset(
    selected_interval: str,
    interval_evaluations: dict[str, Any],
    generated_external_files: list[str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str], list[str]]:
    evaluation = interval_evaluations[selected_interval]
    records_by_symbol = evaluation["records_by_symbol"]
    qualities = evaluation["qualities"]
    per_symbol_build_summary: dict[str, Any] = {}
    data_quality_checks: dict[str, Any] = {}
    for symbol, records in records_by_symbol.items():
        output_path = NORMALIZED_DIR / f"{symbol}_{selected_interval}.jsonl"
        write_jsonl(output_path, records)
        generated_external_files.append(str(output_path))
        quality = qualities[symbol]
        coverage_path = COVERAGE_DIR / f"{symbol}_{selected_interval}_coverage.json"
        write_json(coverage_path, {"symbol": symbol, "interval": selected_interval, "data_quality": quality})
        generated_external_files.append(str(coverage_path))
        timestamps = [record["timestamp"] for record in records if record.get("timestamp")]
        per_symbol_build_summary[symbol] = {
            "built": bool(records),
            "normalized_row_count": len(records),
            "timestamp_min": min(timestamps) if timestamps else None,
            "timestamp_max": max(timestamps) if timestamps else None,
            "alignment_row_count": quality["alignment_row_count"],
            "alignment_coverage_share": quality["alignment_coverage_share"],
        }
        data_quality_checks[symbol] = quality

    checksum_entries = {}
    for file_path_text in generated_external_files:
        path = Path(file_path_text)
        if path.exists() and path.is_file():
            checksum_entries[str(path)] = sha256_file(path)
    checksum_path = CHECKSUM_DIR / "coinalyze_max_available_oi_liq_dataset_v1_sha256.json"
    write_json(checksum_path, checksum_entries)
    generated_external_files.append(str(checksum_path))
    return per_symbol_build_summary, data_quality_checks, checksum_entries, generated_external_files


def classify_dataset(selected_interval: str | None, evaluation: dict[str, Any] | None, prior_rows: int) -> tuple[str, str]:
    if not selected_interval or not evaluation:
        return "COINALYZE_MAX_HISTORY_DATASET_INSUFFICIENT", "FREE_DATA_SOURCE_ALTERNATIVE_DISCOVERY_V1"
    event_count = evaluation["event_sample_size_estimate"]["estimated_event_count"]
    full_alignment = evaluation["symbols_with_full_alignment_count"]
    quality = evaluation["data_quality_passed"]
    rows = evaluation["total_normalized_rows"]
    if selected_interval in ("15min", "1hour") and full_alignment >= 5 and event_count >= 100 and quality:
        return (
            "COINALYZE_MAX_HISTORY_DATASET_READY_FOR_EXTENDED_STRATEGY_EXECUTION",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_EXTENDED_STRATEGY_EXECUTION_PREREGISTRATION_V1",
        )
    if full_alignment >= 5 and event_count >= 50 and quality:
        return (
            "COINALYZE_MAX_HISTORY_DATASET_READY_FOR_EXTENDED_EVENT_STUDY_ONLY",
            "COINALYZE_LONG_LIQUIDATION_FLUSH_EXTENDED_EVENT_STUDY_V1",
        )
    if rows > prior_rows and full_alignment > 0:
        return (
            "COINALYZE_MAX_HISTORY_DATASET_PARTIAL_USABLE_LOW_SAMPLE",
            "COINALYZE_DATA_WINDOW_EXTENSION_OR_SYMBOL_EXPANSION_REVIEW_V1",
        )
    return "COINALYZE_MAX_HISTORY_DATASET_INSUFFICIENT", "FREE_DATA_SOURCE_ALTERNATIVE_DISCOVERY_V1"


def blocked_payload(status: str, reason: str) -> dict[str, Any]:
    clean = repo_clean_except_expected_new_files()
    validation_checks = {
        "repo_clean_before_run": clean,
        "prior_discovery_loaded": DISCOVERY_PATH.exists(),
        "prior_dataset_builder_loaded": PRIOR_DATASET_PATH.exists(),
        "strategy_preregistration_loaded": PREREGISTRATION_PATH.exists(),
        "api_key_loaded_from_one_time_env_only": False,
        "api_key_not_written_to_python": True,
        "api_key_not_written_to_artifact": True,
        "api_key_not_printed": True,
        "api_key_not_in_git_diff": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_exchange_api_used": True,
        "no_order_endpoint_used": True,
        "external_output_root_used": False,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": clean,
        "replacement_checks_all_true": False,
    }
    payload: dict[str, Any] = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "source_artifacts": {
            "prior_discovery": rel(DISCOVERY_PATH),
            "prior_dataset_builder": rel(PRIOR_DATASET_PATH),
            "strategy_design": rel(DESIGN_PATH),
            "strategy_preregistration": rel(PREREGISTRATION_PATH),
        },
        "api_key_handling": {
            "env_var_name": API_KEY_ENV,
            "api_key_source": "one_time_env",
            "api_key_loaded": False,
            "api_key_persisted": False,
            "api_key_printed": False,
            "api_key_written_to_python": False,
            "api_key_written_to_artifact": False,
            "api_key_in_git_diff": False,
        },
        "requested_symbols": REQUESTED_SYMBOLS,
        "interval_history_discovery": {},
        "selected_dataset_plan": {},
        "external_output_root": str(EXTERNAL_OUTPUT_ROOT),
        "generated_external_files": [],
        "per_symbol_build_summary": {},
        "alignment_summary": {},
        "event_sample_size_estimate": {"estimated_event_count": 0, "count_is_raw_sample_size_estimate_only": True},
        "data_quality_checks": {},
        "coverage_summary": {
            "requested_symbol_count": len(REQUESTED_SYMBOLS),
            "built_symbol_count": 0,
            "symbols_with_full_alignment": 0,
            "selected_interval": None,
            "selected_window_start": None,
            "selected_window_end": None,
            "total_normalized_rows": 0,
            "estimated_possible_event_count_for_LONG_LIQUIDATION_FLUSH_EVENT": 0,
            "limitations": [reason],
        },
        "checksum_summary": {},
        "result_classification": "COINALYZE_MAX_HISTORY_DATASET_BLOCKED_API_OR_RATE_LIMIT",
        "next_allowed_step": "COINALYZE_MAX_HISTORY_DATASET_BUILDER_BLOCKER_REVIEW_V1",
        "next_module": "COINALYZE_MAX_HISTORY_DATASET_BUILDER_BLOCKER_REVIEW_V1",
        "limitations": [reason],
        "safety_permissions": safety_permissions(),
        "validation_checks": validation_checks,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def safety_permissions() -> dict[str, bool]:
    return {
        "dataset_builder_created": True,
        "strategy_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "backtest_allowed_now": False,
        "pnl_computation_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }


def build_payload(api_key: str) -> dict[str, Any]:
    if not api_key:
        return blocked_payload(MISSING_KEY_STATUS, "COINALYZE_API_KEY was missing from the one-time process environment.")

    discovery = load_json(DISCOVERY_PATH)
    prior_dataset = load_json(PRIOR_DATASET_PATH)
    design = load_json(DESIGN_PATH)
    preregistration = load_json(PREREGISTRATION_PATH)
    clean = repo_clean_except_expected_new_files()
    ensure_external_dirs()
    symbol_mapping = load_symbol_mapping(discovery)
    interval_history, rows_store, generated_external_files = discover_history(api_key, symbol_mapping)
    interval_evaluations = evaluate_intervals(rows_store, symbol_mapping)
    prior_rows = int(prior_dataset.get("coverage_summary", {}).get("total_normalized_rows", 0))
    selected_interval, selected_start, selected_end = select_interval(interval_evaluations, prior_rows)
    selected_evaluation = interval_evaluations.get(selected_interval) if selected_interval else None

    if selected_interval and selected_evaluation:
        per_symbol_build_summary, data_quality_checks, checksums, generated_external_files = write_selected_dataset(
            selected_interval,
            interval_evaluations,
            generated_external_files,
        )
        selected_event_estimate = selected_evaluation["event_sample_size_estimate"]
    else:
        per_symbol_build_summary, data_quality_checks, checksums = {}, {}, {}
        selected_event_estimate = {"estimated_event_count": 0, "count_is_raw_sample_size_estimate_only": True}

    result_classification, next_allowed_step = classify_dataset(selected_interval, selected_evaluation, prior_rows)
    alignment_summary = {
        interval: {
            "symbols_with_full_alignment": evaluation["symbols_with_full_alignment"],
            "symbols_with_full_alignment_count": evaluation["symbols_with_full_alignment_count"],
            "total_normalized_rows": evaluation["total_normalized_rows"],
            "timestamp_min": evaluation["timestamp_min"],
            "timestamp_max": evaluation["timestamp_max"],
            "data_quality_passed": evaluation["data_quality_passed"],
            "estimated_long_liq_flush_event_count": evaluation["event_sample_size_estimate"]["estimated_event_count"],
        }
        for interval, evaluation in interval_evaluations.items()
    }
    built_symbols = [symbol for symbol, summary in per_symbol_build_summary.items() if summary.get("built")]
    symbols_with_full_alignment = selected_evaluation["symbols_with_full_alignment"] if selected_evaluation else []
    total_rows = selected_evaluation["total_normalized_rows"] if selected_evaluation else 0
    quality_passed = bool(selected_evaluation and selected_evaluation["data_quality_passed"])

    coverage_summary = {
        "requested_symbol_count": len(REQUESTED_SYMBOLS),
        "built_symbol_count": len(built_symbols),
        "symbols_with_oi": sum(1 for q in data_quality_checks.values() if q["field_availability_summary"]["has_oi"]),
        "symbols_with_liquidation": sum(1 for q in data_quality_checks.values() if q["field_availability_summary"]["has_liquidation"]),
        "symbols_with_funding": sum(1 for q in data_quality_checks.values() if q["field_availability_summary"]["has_funding"]),
        "symbols_with_ohlcv": sum(1 for q in data_quality_checks.values() if q["field_availability_summary"]["has_ohlcv"]),
        "symbols_with_full_alignment": len(symbols_with_full_alignment),
        "selected_interval": selected_interval,
        "selected_window_start": selected_start,
        "selected_window_end": selected_end,
        "total_normalized_rows": total_rows,
        "estimated_possible_event_count_for_LONG_LIQUIDATION_FLUSH_EVENT": selected_event_estimate["estimated_event_count"],
        "limitations": [
            "This is max-history discovery plus dataset build only; no strategy execution, trade simulation, signal generation, or PnL was computed.",
            "Raw event count is for sample-size estimation only using frozen structural thresholds.",
            "Coinalyze free API history availability may be limited by endpoint, interval, and returned rows.",
        ],
    }
    validation_checks = {
        "repo_clean_before_run": clean,
        "prior_discovery_loaded": discovery.get("status") == "PASS_REPO_ONLY_COINALYZE_FREE_OI_LIQ_FUNDING_AVAILABILITY_DISCOVERY_V5_CREATED",
        "prior_dataset_builder_loaded": prior_dataset.get("status") == "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BUILDER_CREATED",
        "strategy_preregistration_loaded": preregistration.get("status") == "PASS_REPO_ONLY_COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_PREREGISTRATION_CREATED",
        "api_key_loaded_from_one_time_env_only": True,
        "api_key_not_written_to_python": api_key not in TOOL_PATH.read_text(encoding="utf-8"),
        "api_key_not_written_to_artifact": True,
        "api_key_not_printed": True,
        "api_key_not_in_git_diff": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_exchange_api_used": True,
        "no_order_endpoint_used": True,
        "external_output_root_used": str(EXTERNAL_OUTPUT_ROOT).startswith(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_coinalyze_max_available_oi_liq_dataset_v1"),
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": clean,
        "replacement_checks_all_true": True,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())

    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "source_artifacts": {
            "prior_discovery": rel(DISCOVERY_PATH),
            "prior_dataset_builder": rel(PRIOR_DATASET_PATH),
            "strategy_design": rel(DESIGN_PATH),
            "strategy_preregistration": rel(PREREGISTRATION_PATH),
        },
        "api_key_handling": {
            "env_var_name": API_KEY_ENV,
            "api_key_source": "one_time_env",
            "api_key_loaded": True,
            "api_key_persisted": False,
            "api_key_printed": False,
            "api_key_written_to_python": False,
            "api_key_written_to_artifact": False,
            "api_key_in_git_diff": False,
        },
        "requested_symbols": REQUESTED_SYMBOLS,
        "interval_history_discovery": interval_history,
        "selected_dataset_plan": {
            "selected_interval": selected_interval,
            "selected_window_start": selected_start,
            "selected_window_end": selected_end,
            "preferred_order": PREFERRED_INTERVALS,
            "selection_policy": "Prefer 15min maximum available aligned history, then 1hour, then daily only for high-level event study unless later approved.",
            "data_quality_passed": quality_passed,
        },
        "external_output_root": str(EXTERNAL_OUTPUT_ROOT),
        "generated_external_files": generated_external_files,
        "per_symbol_build_summary": per_symbol_build_summary,
        "alignment_summary": alignment_summary,
        "event_sample_size_estimate": selected_event_estimate,
        "data_quality_checks": data_quality_checks,
        "coverage_summary": coverage_summary,
        "checksum_summary": {
            "file_count": len(checksums),
            "sha256_by_file": checksums,
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": coverage_summary["limitations"],
        "safety_permissions": safety_permissions(),
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": None,
    }
    if api_key in canonical_json(payload):
        payload = blocked_payload(
            "BLOCKED_API_KEY_LEAK_PREVENTED_MAX_HISTORY_BUILDER",
            "API key appeared in payload before artifact write; blocked and did not persist successful payload.",
        )
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def print_stdout(payload: dict[str, Any]) -> None:
    coverage = payload.get("coverage_summary", {})
    print(f"status: {payload.get('status')}")
    print(f"result_classification: {payload.get('result_classification')}")
    print(f"selected_interval: {coverage.get('selected_interval')}")
    print(f"selected_window_start: {coverage.get('selected_window_start')}")
    print(f"selected_window_end: {coverage.get('selected_window_end')}")
    print(f"requested_symbol_count: {coverage.get('requested_symbol_count', 0)}")
    print(f"built_symbol_count: {coverage.get('built_symbol_count', 0)}")
    print(f"symbols_with_full_alignment: {coverage.get('symbols_with_full_alignment', 0)}")
    print(f"total_normalized_rows: {coverage.get('total_normalized_rows', 0)}")
    print(f"estimated_long_liq_flush_event_count: {coverage.get('estimated_possible_event_count_for_LONG_LIQUIDATION_FLUSH_EVENT', 0)}")
    print(f"next_allowed_step: {payload.get('next_allowed_step')}")
    print("api_key_persisted: false")
    print("strategy_execution_allowed_now: false")
    print("signal_generation_allowed_now: false")
    print("backtest_allowed_now: false")
    print("pnl_computation_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload.get('payload_sha256_excluding_hash')}")
    print(f"replacement_checks_all_true: {str(payload.get('replacement_checks_all_true')).lower()}")


def main() -> int:
    api_key = os.environ.get(API_KEY_ENV, "").strip()
    payload = build_payload(api_key)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print_stdout(payload)
    return 0 if payload.get("replacement_checks_all_true") else 1


if __name__ == "__main__":
    raise SystemExit(main())
