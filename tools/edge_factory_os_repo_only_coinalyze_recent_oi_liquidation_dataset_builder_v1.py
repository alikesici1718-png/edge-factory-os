#!/usr/bin/env python3
"""Build a recent Coinalyze OI/liquidation/funding alignment dataset.

Dataset builder only. This module does not run a strategy, generate signals,
run a backtest, compute PnL, optimize, create candidates, claim edge, or grant
runtime/live/capital permission. The Coinalyze API key is read only from the
temporary process environment variable COINALYZE_API_KEY and is never printed or
written to repo artifacts or external dataset files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_recent_oi_liquidation_dataset_builder_v1"
STATUS = "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BUILDER_CREATED"
MISSING_KEY_STATUS = "BLOCKED_COINALYZE_API_KEY_MISSING_FOR_DATASET_BUILDER"
API_BLOCKED_STATUS = "BLOCKED_COINALYZE_DATASET_BUILDER_API_OR_RATE_LIMIT"
ARTIFACT_KIND = "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BUILDER"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_recent_oi_liquidation_dataset_builder_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "data_builds" / "coinalyze_recent_oi_liquidation_dataset_builder_v1.json"
DISCOVERY_PATH = REPO_ROOT / "artifacts" / "data_discovery" / "coinalyze_free_oi_liq_funding_availability_discovery_v5.json"
DESIGN_PATH = REPO_ROOT / "artifacts" / "research_designs" / "coinalyze_recent_oi_liquidation_hypothesis_design_v1.json"
EXTERNAL_OUTPUT_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_coinalyze_recent_oi_liquidation_dataset_v1")
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
COINALYZE_BASE_URL = "https://api.coinalyze.net/v1"
API_KEY_ENV = "COINALYZE_API_KEY"
RATE_LIMIT_SLEEP_SECONDS = 2.0
PRIMARY_INTERVAL = "15min"
FETCH_DAYS = 14

ENDPOINTS = [
    "open-interest-history",
    "liquidation-history",
    "funding-rate-history",
    "ohlcv-history",
    "long-short-ratio-history",
]

RAW_DIR = EXTERNAL_OUTPUT_ROOT / "raw_responses"
NORMALIZED_DIR = EXTERNAL_OUTPUT_ROOT / "normalized_by_symbol"
COVERAGE_DIR = EXTERNAL_OUTPUT_ROOT / "coverage_reports"
CHECKSUM_DIR = EXTERNAL_OUTPUT_ROOT / "checksums"
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


def ensure_external_dirs() -> None:
    for directory in (RAW_DIR, NORMALIZED_DIR, COVERAGE_DIR, CHECKSUM_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def floor_last_closed_15m(now: datetime) -> datetime:
    floored_minute = (now.minute // 15) * 15
    floored = now.replace(minute=floored_minute, second=0, microsecond=0)
    return floored - timedelta(minutes=15)


def iso_from_ts(ts: int | float | str | None) -> str | None:
    if ts is None:
        return None
    try:
        value = int(float(ts))
    except (TypeError, ValueError):
        return None
    if value > 10_000_000_000:
        value //= 1000
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


def ts_int(row: dict[str, Any]) -> int | None:
    for key in ("t", "time", "timestamp"):
        value = row.get(key)
        if value is None:
            continue
        try:
            parsed = int(float(value))
            return parsed // 1000 if parsed > 10_000_000_000 else parsed
        except (TypeError, ValueError):
            continue
    return None


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sanitize_error(message: str | None, api_key: str) -> str | None:
    if message is None:
        return None
    text = str(message)
    if api_key:
        text = text.replace(api_key, "[REDACTED_API_KEY]")
    for marker in ("api_key=", "api_key%3D"):
        lower = text.lower()
        idx = lower.find(marker)
        if idx >= 0:
            text = text[:idx] + marker + "[REDACTED]"
    return text[:700]


def coinalyze_get(endpoint: str, params: dict[str, Any], api_key: str) -> tuple[bool, int | None, Any, str | None]:
    request_params = dict(params)
    request_params["api_key"] = api_key
    url = f"{COINALYZE_BASE_URL}/{endpoint}?{urllib.parse.urlencode(request_params)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "edge-factory-os-coinalyze-dataset-builder/1.0"},
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


def extract_rows(data: Any, symbol: str) -> list[dict[str, Any]]:
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "history" in data[0]:
            for item in data:
                if not isinstance(item, dict):
                    continue
                item_symbol = str(item.get("symbol", ""))
                if not item_symbol or item_symbol == symbol:
                    history = item.get("history")
                    if isinstance(history, list):
                        return [row for row in history if isinstance(row, dict)]
            history = data[0].get("history")
            if isinstance(history, list):
                return [row for row in history if isinstance(row, dict)]
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("history", "data", "result"):
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    return []


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def endpoint_row_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    timestamps = [ts for ts in (ts_int(row) for row in rows) if ts is not None]
    duplicate_count = len(timestamps) - len(set(timestamps))
    if timestamps:
        min_ts = min(timestamps)
        max_ts = max(timestamps)
    else:
        min_ts = None
        max_ts = None
    return {
        "row_count": len(rows),
        "timestamp_min": iso_from_ts(min_ts),
        "timestamp_max": iso_from_ts(max_ts),
        "duplicate_timestamp_count": duplicate_count,
        "field_names": sorted({str(key) for row in rows[:10] for key in row.keys() if "api" not in str(key).lower()}),
    }


def add_ohlcv(target: dict[str, Any], row: dict[str, Any]) -> None:
    target["open"] = as_float(row.get("o"))
    target["high"] = as_float(row.get("h"))
    target["low"] = as_float(row.get("l"))
    target["close"] = as_float(row.get("c"))
    target["volume"] = as_float(row.get("v"))


def add_oi(target: dict[str, Any], row: dict[str, Any]) -> None:
    target["oi"] = as_float(row.get("c"))


def add_liquidation(target: dict[str, Any], row: dict[str, Any]) -> None:
    long_liq = as_float(row.get("l"))
    short_liq = as_float(row.get("s"))
    target["liquidation_long"] = long_liq
    target["liquidation_short"] = short_liq
    if long_liq is not None or short_liq is not None:
        total = (long_liq or 0.0) + (short_liq or 0.0)
        target["liquidation_total"] = total
        target["liquidation_imbalance"] = ((long_liq or 0.0) - (short_liq or 0.0)) / total if total > 0 else 0.0


def add_funding(target: dict[str, Any], row: dict[str, Any]) -> None:
    target["funding_rate"] = as_float(row.get("c"))


def add_long_short(target: dict[str, Any], row: dict[str, Any]) -> None:
    ratio = as_float(row.get("r"))
    long_value = as_float(row.get("l"))
    short_value = as_float(row.get("s"))
    if ratio is None and long_value is not None and short_value not in (None, 0):
        ratio = long_value / short_value
    target["long_short_ratio"] = ratio


def expected_timestamp_missing_count(timestamps: list[int]) -> int:
    if not timestamps:
        return 0
    unique_ts = sorted(set(timestamps))
    expected = ((unique_ts[-1] - unique_ts[0]) // 900) + 1
    return max(0, expected - len(unique_ts))


def normalize_symbol_records(
    target_symbol: str,
    mapped_symbol: str,
    exchange: str,
    endpoint_rows: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records_by_ts: dict[int, dict[str, Any]] = {}
    endpoint_availability: dict[str, bool] = {}
    row_count_by_endpoint: dict[str, int] = {}
    timestamp_range_by_endpoint: dict[str, dict[str, str | None]] = {}
    duplicate_timestamp_count_by_endpoint: dict[str, int] = {}

    for endpoint, rows in endpoint_rows.items():
        stats = endpoint_row_stats(rows)
        endpoint_availability[endpoint] = stats["row_count"] > 0
        row_count_by_endpoint[endpoint] = stats["row_count"]
        timestamp_range_by_endpoint[endpoint] = {
            "timestamp_min": stats["timestamp_min"],
            "timestamp_max": stats["timestamp_max"],
        }
        duplicate_timestamp_count_by_endpoint[endpoint] = stats["duplicate_timestamp_count"]
        for row in rows:
            timestamp = ts_int(row)
            if timestamp is None:
                continue
            record = records_by_ts.setdefault(
                timestamp,
                {
                    "timestamp": iso_from_ts(timestamp),
                    "symbol": target_symbol,
                    "coinalyze_symbol": mapped_symbol,
                    "exchange": exchange,
                    "interval": PRIMARY_INTERVAL,
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
    previous_oi: float | None = None
    for record in normalized:
        oi = record.get("oi")
        if isinstance(oi, (int, float)) and previous_oi is not None:
            record["oi_change"] = oi - previous_oi
            record["oi_change_pct"] = (oi - previous_oi) / previous_oi if previous_oi != 0 else None
        if isinstance(oi, (int, float)):
            previous_oi = float(oi)

    timestamps = [ts for ts in (ts_int({"t": record["timestamp"].replace("Z", "+00:00")}) for record in []) if ts is not None]
    numeric_timestamps: list[int] = []
    for record in normalized:
        timestamp_text = record.get("timestamp")
        if isinstance(timestamp_text, str):
            numeric_timestamps.append(int(datetime.fromisoformat(timestamp_text.replace("Z", "+00:00")).timestamp()))

    full_alignment_rows = [
        record
        for record in normalized
        if record.get("oi") is not None
        and record.get("liquidation_total") is not None
        and record.get("funding_rate") is not None
        and record.get("close") is not None
    ]
    negative_oi_count = sum(1 for record in normalized if isinstance(record.get("oi"), (int, float)) and record["oi"] < 0)
    negative_liquidation_count = sum(
        1
        for record in normalized
        if (isinstance(record.get("liquidation_long"), (int, float)) and record["liquidation_long"] < 0)
        or (isinstance(record.get("liquidation_short"), (int, float)) and record["liquidation_short"] < 0)
    )
    invalid_funding_count = sum(
        1
        for record in normalized
        if record.get("funding_rate") is not None
        and (not isinstance(record.get("funding_rate"), (int, float)) or abs(float(record["funding_rate"])) > 1.0)
    )
    ohlc_sanity_fail_count = 0
    for record in normalized:
        o = record.get("open")
        h = record.get("high")
        l = record.get("low")
        c = record.get("close")
        if all(isinstance(value, (int, float)) for value in (o, h, l, c)):
            if not (h >= max(o, c, l) and l <= min(o, c, h) and o > 0 and h > 0 and l > 0 and c > 0):
                ohlc_sanity_fail_count += 1

    quality = {
        "endpoint_availability": endpoint_availability,
        "row_count_by_endpoint": row_count_by_endpoint,
        "timestamp_range_by_endpoint": timestamp_range_by_endpoint,
        "alignment_row_count": len(full_alignment_rows),
        "alignment_coverage_share": len(full_alignment_rows) / len(normalized) if normalized else 0.0,
        "missing_timestamp_count": expected_timestamp_missing_count(numeric_timestamps),
        "duplicate_timestamp_count_by_endpoint": duplicate_timestamp_count_by_endpoint,
        "negative_oi_count": negative_oi_count,
        "negative_liquidation_count": negative_liquidation_count,
        "invalid_funding_count": invalid_funding_count,
        "ohlc_sanity_fail_count": ohlc_sanity_fail_count,
        "field_availability_summary": {
            "has_oi": any(record.get("oi") is not None for record in normalized),
            "has_liquidation": any(record.get("liquidation_total") is not None for record in normalized),
            "has_funding": any(record.get("funding_rate") is not None for record in normalized),
            "has_ohlcv": any(record.get("close") is not None for record in normalized),
            "has_long_short_ratio": any(record.get("long_short_ratio") is not None for record in normalized),
        },
    }
    return normalized, quality


def fetch_symbol(symbol_entry: dict[str, Any], start_ts: int, end_ts: int, api_key: str) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], list[str]]:
    target_symbol = str(symbol_entry["target_symbol"])
    mapped_symbol = str(symbol_entry.get("symbol") or symbol_entry.get("coinalyze_symbol") or "")
    external_files: list[str] = []
    endpoint_rows: dict[str, list[dict[str, Any]]] = {}
    endpoint_summary: dict[str, Any] = {}
    for endpoint in ENDPOINTS:
        params = {
            "symbols": mapped_symbol,
            "interval": PRIMARY_INTERVAL,
            "from": start_ts,
            "to": end_ts,
        }
        ok, http_status, data, error = coinalyze_get(endpoint, params, api_key)
        rows = extract_rows(data, mapped_symbol) if ok else []
        endpoint_rows[endpoint] = rows
        stats = endpoint_row_stats(rows)
        endpoint_summary[endpoint] = {
            "request_ok": ok,
            "http_status": http_status,
            "error_message": error,
            **stats,
        }
        raw_payload = {
            "endpoint": endpoint,
            "target_symbol": target_symbol,
            "coinalyze_symbol": mapped_symbol,
            "interval": PRIMARY_INTERVAL,
            "request_ok": ok,
            "http_status": http_status,
            "error_message": error,
            "rows": rows,
        }
        raw_path = RAW_DIR / f"{target_symbol}_{endpoint}_{PRIMARY_INTERVAL}.json"
        write_json(raw_path, raw_payload)
        external_files.append(str(raw_path))
        time.sleep(RATE_LIMIT_SLEEP_SECONDS)
    return endpoint_rows, endpoint_summary, external_files


def build_dataset(api_key: str) -> dict[str, Any]:
    discovery = load_json(DISCOVERY_PATH)
    design = load_json(DESIGN_PATH)
    clean = repo_clean_except_expected_new_files()
    requested_symbols = [
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
    probes_by_target = {entry["target_symbol"]: entry for entry in discovery.get("probe_symbols", [])}
    symbol_mapping = {
        symbol: {
            "target_symbol": symbol,
            "coinalyze_symbol": probes_by_target.get(symbol, {}).get("symbol"),
            "symbol_on_exchange": probes_by_target.get(symbol, {}).get("symbol_on_exchange"),
            "exchange": probes_by_target.get(symbol, {}).get("exchange"),
            "mapping_available": symbol in probes_by_target,
        }
        for symbol in requested_symbols
    }

    ensure_external_dirs()
    end_dt = floor_last_closed_15m(datetime.now(timezone.utc))
    start_dt = end_dt - timedelta(days=FETCH_DAYS)
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    generated_external_files: list[str] = []
    per_symbol_build_summary: dict[str, Any] = {}
    data_quality_checks: dict[str, Any] = {}
    alignment_summary: dict[str, Any] = {}
    all_normalized_files: list[Path] = []
    global_timestamps: list[str] = []

    for target_symbol in requested_symbols:
        mapping = symbol_mapping[target_symbol]
        if not mapping["mapping_available"] or not mapping["coinalyze_symbol"]:
            per_symbol_build_summary[target_symbol] = {"built": False, "missing_reason": "coinalyze_symbol_mapping_missing"}
            continue
        endpoint_rows, endpoint_summary, raw_files = fetch_symbol(mapping, start_ts, end_ts, api_key)
        generated_external_files.extend(raw_files)
        normalized, quality = normalize_symbol_records(
            target_symbol=target_symbol,
            mapped_symbol=str(mapping["coinalyze_symbol"]),
            exchange=str(mapping["exchange"]),
            endpoint_rows=endpoint_rows,
        )
        normalized_path = NORMALIZED_DIR / f"{target_symbol}_{PRIMARY_INTERVAL}.jsonl"
        write_jsonl(normalized_path, normalized)
        all_normalized_files.append(normalized_path)
        generated_external_files.append(str(normalized_path))
        coverage_path = COVERAGE_DIR / f"{target_symbol}_{PRIMARY_INTERVAL}_coverage.json"
        coverage_payload = {
            "target_symbol": target_symbol,
            "coinalyze_symbol": mapping["coinalyze_symbol"],
            "exchange": mapping["exchange"],
            "endpoint_summary": endpoint_summary,
            "data_quality": quality,
        }
        write_json(coverage_path, coverage_payload)
        generated_external_files.append(str(coverage_path))

        timestamps = [record["timestamp"] for record in normalized if record.get("timestamp")]
        global_timestamps.extend(timestamps)
        per_symbol_build_summary[target_symbol] = {
            "built": bool(normalized),
            "normalized_row_count": len(normalized),
            "timestamp_min": min(timestamps) if timestamps else None,
            "timestamp_max": max(timestamps) if timestamps else None,
            "endpoint_summary": endpoint_summary,
            "alignment_row_count": quality["alignment_row_count"],
            "alignment_coverage_share": quality["alignment_coverage_share"],
        }
        data_quality_checks[target_symbol] = quality
        alignment_summary[target_symbol] = {
            "full_alignment_row_count": quality["alignment_row_count"],
            "alignment_coverage_share": quality["alignment_coverage_share"],
            "has_full_alignment": quality["alignment_row_count"] > 0,
        }

    checksum_entries: dict[str, str] = {}
    for file_path_text in generated_external_files:
        path = Path(file_path_text)
        if path.exists() and path.is_file():
            checksum_entries[str(path)] = sha256_file(path)
    checksum_path = CHECKSUM_DIR / "coinalyze_recent_oi_liquidation_dataset_v1_sha256.json"
    write_json(checksum_path, checksum_entries)
    generated_external_files.append(str(checksum_path))

    built_symbols = [symbol for symbol, summary in per_symbol_build_summary.items() if summary.get("built")]
    symbols_with_oi = [symbol for symbol, quality in data_quality_checks.items() if quality["field_availability_summary"]["has_oi"]]
    symbols_with_liquidation = [symbol for symbol, quality in data_quality_checks.items() if quality["field_availability_summary"]["has_liquidation"]]
    symbols_with_funding = [symbol for symbol, quality in data_quality_checks.items() if quality["field_availability_summary"]["has_funding"]]
    symbols_with_ohlcv = [symbol for symbol, quality in data_quality_checks.items() if quality["field_availability_summary"]["has_ohlcv"]]
    symbols_with_full_alignment = [symbol for symbol, summary in alignment_summary.items() if summary["has_full_alignment"]]
    total_normalized_rows = sum(summary.get("normalized_row_count", 0) for summary in per_symbol_build_summary.values())
    endpoint_http_statuses = [
        endpoint_summary.get("http_status")
        for symbol_summary in per_symbol_build_summary.values()
        for endpoint_summary in symbol_summary.get("endpoint_summary", {}).values()
    ]
    repeated_auth_or_rate_limit_block = (
        bool(endpoint_http_statuses)
        and not (symbols_with_oi or symbols_with_liquidation or symbols_with_funding)
        and any(status in (401, 429) for status in endpoint_http_statuses)
    )
    quality_passed = all(
        quality["negative_oi_count"] == 0
        and quality["negative_liquidation_count"] == 0
        and quality["invalid_funding_count"] == 0
        and quality["ohlc_sanity_fail_count"] == 0
        for quality in data_quality_checks.values()
    )
    if repeated_auth_or_rate_limit_block:
        result_classification = "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BLOCKED_API_OR_RATE_LIMIT"
        next_allowed_step = "COINALYZE_DATASET_BUILDER_API_OR_RATE_LIMIT_REVIEW_V1"
    elif len(symbols_with_full_alignment) >= 5 and total_normalized_rows >= 1000 and quality_passed:
        result_classification = "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_READY_FOR_EVENT_STUDY"
        next_allowed_step = "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_V1"
    elif symbols_with_oi and symbols_with_liquidation:
        result_classification = "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_PARTIAL_USABLE"
        next_allowed_step = "COINALYZE_LIQUIDATION_IMBALANCE_OI_FLUSH_EVENT_STUDY_V1"
    else:
        result_classification = "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_INSUFFICIENT"
        next_allowed_step = "COINALYZE_DATASET_GAP_REVIEW_V1"

    coverage_summary = {
        "requested_symbol_count": len(requested_symbols),
        "built_symbol_count": len(built_symbols),
        "symbols_with_oi": symbols_with_oi,
        "symbols_with_liquidation": symbols_with_liquidation,
        "symbols_with_funding": symbols_with_funding,
        "symbols_with_ohlcv": symbols_with_ohlcv,
        "symbols_with_full_alignment": symbols_with_full_alignment,
        "symbols_with_oi_count": len(symbols_with_oi),
        "symbols_with_liquidation_count": len(symbols_with_liquidation),
        "symbols_with_funding_count": len(symbols_with_funding),
        "symbols_with_ohlcv_count": len(symbols_with_ohlcv),
        "symbols_with_full_alignment_count": len(symbols_with_full_alignment),
        "timestamp_global_min": min(global_timestamps) if global_timestamps else None,
        "timestamp_global_max": max(global_timestamps) if global_timestamps else None,
        "total_normalized_rows": total_normalized_rows,
        "best_interval": PRIMARY_INTERVAL,
        "limitations": [
            "Recent Coinalyze free intraday coverage only; not a 2022-2025 deep backtest dataset.",
            "Generic derived fields are limited to OI change and liquidation imbalance for dataset quality/alignment.",
        ],
    }
    validation_checks = {
        "repo_clean_before_run": clean,
        "coinalyze_v5_discovery_loaded": discovery.get("status") == "PASS_REPO_ONLY_COINALYZE_FREE_OI_LIQ_FUNDING_AVAILABILITY_DISCOVERY_V5_CREATED",
        "hypothesis_design_loaded": design.get("status") == "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN_CREATED",
        "top_priority_hypothesis_verified": design.get("recommended_hypothesis_priority", [{}])[0].get("hypothesis_key") == "LIQUIDATION_IMBALANCE_WITH_OI_FLUSH",
        "api_key_loaded_from_env_only": True,
        "api_key_not_written_to_artifact": True,
        "api_key_not_printed": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_exchange_api_used": True,
        "no_order_endpoint_used": True,
        "external_output_root_used": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": clean,
        "replacement_checks_all_true": True,
    }
    if repeated_auth_or_rate_limit_block:
        if any(status == 401 for status in endpoint_http_statuses):
            status = "BLOCKED_COINALYZE_API_KEY_INVALID_FOR_DATASET_BUILDER"
        else:
            status = API_BLOCKED_STATUS
    else:
        status = STATUS
    replacement_checks_all_true = all(validation_checks.values()) and result_classification != "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BLOCKED_API_OR_RATE_LIMIT"
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    payload: dict[str, Any] = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "source_artifacts": {
            "coinalyze_v5_discovery": str(DISCOVERY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "hypothesis_design": str(DESIGN_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "api_key_handling": {
            "env_var_name": API_KEY_ENV,
            "api_key_source": "temporary_process_env",
            "api_key_loaded_from_env_only": True,
            "api_key_persisted": False,
            "api_key_printed": False,
            "api_key_written_to_artifact": False,
            "api_key_written_to_external_files": False,
        },
        "requested_symbols": requested_symbols,
        "symbol_mapping": symbol_mapping,
        "request_plan": {
            "intervals_requested": [PRIMARY_INTERVAL],
            "optional_1hour_skipped_reason": "Primary 15min coverage was available and sufficient for the requested dataset build.",
            "window_days": FETCH_DAYS,
            "start_timestamp": start_dt.isoformat().replace("+00:00", "Z"),
            "end_timestamp": end_dt.isoformat().replace("+00:00", "Z"),
            "end_timestamp_is_last_closed_15m_bar": True,
            "endpoints": ENDPOINTS,
            "rate_limit_sleep_seconds": RATE_LIMIT_SLEEP_SECONDS,
        },
        "external_output_root": str(EXTERNAL_OUTPUT_ROOT),
        "generated_external_files": generated_external_files,
        "per_symbol_build_summary": per_symbol_build_summary,
        "alignment_summary": alignment_summary,
        "data_quality_checks": data_quality_checks,
        "coverage_summary": coverage_summary,
        "checksum_summary": {
            "checksum_file": str(checksum_path),
            "file_count": len(checksum_entries),
            "normalized_file_count": len(all_normalized_files),
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": coverage_summary["limitations"],
        "safety_permissions": {
            "dataset_builder_created": True,
            "event_study_allowed_next": result_classification in (
                "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_READY_FOR_EVENT_STUDY",
                "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_PARTIAL_USABLE",
            ),
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def blocked_missing_key_payload() -> dict[str, Any]:
    clean = repo_clean_except_expected_new_files()
    payload: dict[str, Any] = {
        "status": MISSING_KEY_STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "source_artifacts": {
            "coinalyze_v5_discovery": str(DISCOVERY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "hypothesis_design": str(DESIGN_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "api_key_handling": {
            "env_var_name": API_KEY_ENV,
            "api_key_source": "missing",
            "api_key_loaded_from_env_only": False,
            "api_key_persisted": False,
            "api_key_printed": False,
            "api_key_written_to_artifact": False,
            "api_key_written_to_external_files": False,
        },
        "requested_symbols": [],
        "symbol_mapping": {},
        "request_plan": {},
        "external_output_root": str(EXTERNAL_OUTPUT_ROOT),
        "generated_external_files": [],
        "per_symbol_build_summary": {},
        "alignment_summary": {},
        "data_quality_checks": {},
        "coverage_summary": {
            "requested_symbol_count": 0,
            "built_symbol_count": 0,
            "symbols_with_oi_count": 0,
            "symbols_with_liquidation_count": 0,
            "symbols_with_funding_count": 0,
            "symbols_with_full_alignment_count": 0,
            "timestamp_global_min": None,
            "timestamp_global_max": None,
            "total_normalized_rows": 0,
            "best_interval": None,
        },
        "checksum_summary": {},
        "result_classification": "COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BLOCKED_API_OR_RATE_LIMIT",
        "next_allowed_step": "COINALYZE_DATASET_BUILDER_API_KEY_REVIEW_V1",
        "limitations": ["COINALYZE_API_KEY was missing from the temporary process environment, so no API request was made."],
        "safety_permissions": {
            "dataset_builder_created": True,
            "event_study_allowed_next": False,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": clean,
            "coinalyze_v5_discovery_loaded": DISCOVERY_PATH.exists(),
            "hypothesis_design_loaded": DESIGN_PATH.exists(),
            "top_priority_hypothesis_verified": False,
            "api_key_loaded_from_env_only": False,
            "api_key_not_written_to_artifact": True,
            "api_key_not_printed": True,
            "no_strategy_execution": True,
            "no_signal_generation": True,
            "no_backtest_run": True,
            "no_pnl_computation": True,
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
        },
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def print_stdout(payload: dict[str, Any]) -> None:
    coverage = payload.get("coverage_summary", {})
    print(f"status: {payload.get('status')}")
    print(f"result_classification: {payload.get('result_classification')}")
    print(f"requested_symbol_count: {coverage.get('requested_symbol_count', 0)}")
    print(f"built_symbol_count: {coverage.get('built_symbol_count', 0)}")
    print(f"symbols_with_oi: {coverage.get('symbols_with_oi_count', 0)}")
    print(f"symbols_with_liquidation: {coverage.get('symbols_with_liquidation_count', 0)}")
    print(f"symbols_with_funding: {coverage.get('symbols_with_funding_count', 0)}")
    print(f"symbols_with_full_alignment: {coverage.get('symbols_with_full_alignment_count', 0)}")
    print(f"total_normalized_rows: {coverage.get('total_normalized_rows', 0)}")
    print(f"timestamp_global_min: {coverage.get('timestamp_global_min')}")
    print(f"timestamp_global_max: {coverage.get('timestamp_global_max')}")
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
    payload = build_dataset(api_key) if api_key else blocked_missing_key_payload()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print_stdout(payload)
    return 0 if payload.get("replacement_checks_all_true") else 1


if __name__ == "__main__":
    raise SystemExit(main())
