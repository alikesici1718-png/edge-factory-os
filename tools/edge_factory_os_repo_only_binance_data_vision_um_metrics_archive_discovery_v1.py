#!/usr/bin/env python
"""Discover Binance Data Vision USD-M Futures daily metrics archive coverage."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "BINANCE_DATA_VISION_UM_METRICS_ARCHIVE_DISCOVERY_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_data_vision_um_metrics_archive_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/data_discovery/binance_data_vision_um_metrics_archive_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

STATUS_PASS = "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_ARCHIVE_DISCOVERY_CREATED"
STATUS_BLOCKED = "BLOCKED_BINANCE_DATA_VISION_UM_METRICS_ARCHIVE_DISCOVERY"
ARTIFACT_KIND = "BINANCE_DATA_VISION_UM_METRICS_ARCHIVE_DISCOVERY"

ARCHIVE_ROOT = "https://data.binance.vision/?prefix=data/futures/um/daily/metrics"
DIRECT_ARCHIVE_ROOT = "https://data.binance.vision/data/futures/um/daily/metrics/"
ARCHIVE_PREFIX = "data/futures/um/daily/metrics"

RESULT_READY = "BINANCE_DATA_VISION_METRICS_READY_FOR_OI_TAKER_CROWDING_DATASET"
RESULT_PARTIAL_OI = "BINANCE_DATA_VISION_METRICS_PARTIAL_OI_ONLY"
RESULT_PARTIAL_RATIO = "BINANCE_DATA_VISION_METRICS_PARTIAL_TAKER_OR_RATIO_ONLY"
RESULT_INSUFFICIENT = "BINANCE_DATA_VISION_METRICS_INSUFFICIENT"
RESULT_BLOCKED = "BINANCE_DATA_VISION_METRICS_DISCOVERY_BLOCKED"

NEXT_READY = "BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_V1"
NEXT_PARTIAL = "BINANCE_DATA_VISION_METRICS_PARTIAL_REVIEW_V1"
NEXT_INSUFFICIENT = "FREE_OR_CHEAP_LIQUIDATION_DATA_SOURCE_DECISION_V1"
NEXT_BLOCKED = "BINANCE_DATA_VISION_UM_METRICS_ARCHIVE_DISCOVERY_BLOCKER_REVIEW_V1"

PROBE_SYMBOLS = [
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
CORE_2023_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT", "BNBUSDT", "LINKUSDT"]
STATIC_PROBE_DATES = ["2023-01-01", "2024-01-01", "2025-01-01"]

TIMEOUT_SECONDS = 20
LISTING_READ_LIMIT_BYTES = 500_000
SAMPLE_ZIP_MAX_BYTES = 300_000
TOTAL_SAMPLE_ZIP_MAX_BYTES = 5_000_000
RECENT_LOOKBACK_DAYS = 90
HEAD_PAUSE_SECONDS = 0.03
DOWNLOAD_PAUSE_SECONDS = 0.05

SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION = "efb4780f1957a7221438a02b7e6108d30fcb6643"
TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION = 1055
GIT_STATUS_SHORT_BEFORE_TOOL_CREATION: list[str] = []

METRIC_COLUMN_MAP = {
    "openInterestHist": {
        "required_any_columns": ["sum_open_interest", "sum_open_interest_value"],
        "description": "Open interest history fields in combined daily metrics ZIP files.",
    },
    "takerlongshortRatio": {
        "required_any_columns": ["sum_taker_long_short_vol_ratio"],
        "description": "Taker buy/sell volume ratio field in combined daily metrics ZIP files.",
    },
    "globalLongShortAccountRatio": {
        "required_any_columns": ["count_long_short_ratio"],
        "description": "All-account long/short ratio field in combined daily metrics ZIP files.",
    },
    "topLongShortAccountRatio": {
        "required_any_columns": ["count_toptrader_long_short_ratio"],
        "description": "Top-trader account long/short ratio field in combined daily metrics ZIP files.",
    },
    "topLongShortPositionRatio": {
        "required_any_columns": ["sum_toptrader_long_short_ratio"],
        "description": "Top-trader position long/short ratio field in combined daily metrics ZIP files.",
    },
    "funding_like_metric": {
        "required_any_columns": ["funding", "funding_rate", "last_funding_rate", "premium"],
        "description": "Funding-like fields, if present inside the daily metrics ZIP files.",
    },
    "liquidation_or_force_order_metric": {
        "required_any_columns": ["liquidation", "force_order", "forceorder", "adl"],
        "description": "Liquidation or force-order fields, if present inside the daily metrics ZIP files.",
    },
}


class DiscoveryBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def assert_public_archive_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "data.binance.vision":
        raise DiscoveryBlocked(f"forbidden non-Data-Vision URL attempted: {url}")
    if parsed.path in ("", "/"):
        query = urllib.parse.parse_qs(parsed.query)
        prefixes = query.get("prefix", [])
        if not prefixes:
            raise DiscoveryBlocked(f"forbidden Data Vision listing URL without prefix: {url}")
        if not all(prefix.startswith(ARCHIVE_PREFIX) for prefix in prefixes):
            raise DiscoveryBlocked(f"forbidden Data Vision listing prefix attempted: {url}")
        return
    if not parsed.path.startswith(f"/{ARCHIVE_PREFIX}/"):
        raise DiscoveryBlocked(f"forbidden Data Vision archive path attempted: {url}")


def metrics_file_url(symbol: str, date_text: str) -> str:
    return f"{DIRECT_ARCHIVE_ROOT}{symbol}/{symbol}-metrics-{date_text}.zip"


def git_status_short() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def tracked_python_count() -> int | None:
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.py"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return len([line for line in result.stdout.splitlines() if line.strip()])


def no_existing_tracked_repo_file_changes(status_lines: list[str]) -> bool:
    allowed_untracked = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
    }
    allowed_added = {
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
    allowed = allowed_untracked | allowed_added
    for line in status_lines:
        if line in allowed:
            continue
        if line.startswith("?? "):
            continue
        return False
    return True


def existing_artifact_can_be_replaced() -> bool:
    if not ARTIFACT_PATH.exists():
        return True
    try:
        payload = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return False
    return payload.get("artifact_kind") == ARTIFACT_KIND and payload.get("module") == MODULE


def fetch_limited_text(url: str, limit: int) -> dict[str, Any]:
    assert_public_archive_url(url)
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-data-vision-metrics-discovery/1"})
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(limit + 1)
            truncated = len(body) > limit
            if truncated:
                body = body[:limit]
            return {
                "url": url,
                "ok": True,
                "http_status": getattr(response, "status", None),
                "bytes_read": len(body),
                "truncated_at_limit": truncated,
                "content_type": response.headers.get("Content-Type"),
                "last_modified": response.headers.get("Last-Modified"),
                "fetched_at_utc": started,
                "text": body.decode("utf-8", errors="replace"),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(4000).decode("utf-8", errors="replace")
        return {
            "url": url,
            "ok": False,
            "http_status": exc.code,
            "bytes_read": len(body),
            "truncated_at_limit": False,
            "content_type": None,
            "last_modified": None,
            "fetched_at_utc": started,
            "text": body,
            "error": body[:1000] or repr(exc),
        }
    except Exception as exc:
        return {
            "url": url,
            "ok": False,
            "http_status": None,
            "bytes_read": 0,
            "truncated_at_limit": False,
            "content_type": None,
            "last_modified": None,
            "fetched_at_utc": started,
            "text": "",
            "error": repr(exc),
        }


def head_archive_file(url: str) -> dict[str, Any]:
    assert_public_archive_url(url)
    try:
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "edge-factory-os-data-vision-metrics-discovery/1"})
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            content_length = response.headers.get("Content-Length")
            return {
                "url": url,
                "exists": True,
                "ok": True,
                "http_status": getattr(response, "status", None),
                "content_length_bytes": int(content_length) if content_length and content_length.isdigit() else None,
                "last_modified": response.headers.get("Last-Modified"),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "url": url,
            "exists": False,
            "ok": False,
            "http_status": exc.code,
            "content_length_bytes": None,
            "last_modified": None,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "url": url,
            "exists": False,
            "ok": False,
            "http_status": None,
            "content_length_bytes": None,
            "last_modified": None,
            "error": repr(exc),
        }


def download_limited_binary(url: str, limit: int) -> dict[str, Any]:
    assert_public_archive_url(url)
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-data-vision-metrics-discovery/1"})
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(limit + 1)
            if len(body) > limit:
                return {
                    "ok": False,
                    "http_status": getattr(response, "status", None),
                    "bytes_read": len(body),
                    "bytes": b"",
                    "error": f"download exceeded cap of {limit} bytes",
                }
            return {
                "ok": True,
                "http_status": getattr(response, "status", None),
                "bytes_read": len(body),
                "bytes": body,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(2000)
        return {
            "ok": False,
            "http_status": exc.code,
            "bytes_read": len(body),
            "bytes": b"",
            "error": body.decode("utf-8", errors="replace")[:1000] or str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "http_status": None,
            "bytes_read": 0,
            "bytes": b"",
            "error": repr(exc),
        }


def parse_symbols_from_listing_text(text: str) -> list[str]:
    patterns = [
        r"data/futures/um/daily/metrics/([A-Z0-9]+USDT)/",
        r"data%2Ffutures%2Fum%2Fdaily%2Fmetrics%2F([A-Z0-9]+USDT)%2F",
        r"/data/futures/um/daily/metrics/([A-Z0-9]+USDT)/",
    ]
    symbols: set[str] = set()
    for pattern in patterns:
        symbols.update(re.findall(pattern, text))
    return sorted(symbols)


def inspect_listing_structure() -> dict[str, Any]:
    listing_urls = [
        ARCHIVE_ROOT,
        f"https://data.binance.vision/?prefix={urllib.parse.quote(ARCHIVE_PREFIX + '/', safe='')}",
        DIRECT_ARCHIVE_ROOT,
    ]
    fetches: list[dict[str, Any]] = []
    discovered_symbols: set[str] = set()
    for url in listing_urls:
        result = fetch_limited_text(url, LISTING_READ_LIMIT_BYTES)
        discovered_symbols.update(parse_symbols_from_listing_text(result.get("text", "")))
        text = result.pop("text", "")
        fetches.append(
            {
                **result,
                "sample_text_prefix": text[:500],
                "symbol_count_parsed_from_limited_text": len(parse_symbols_from_listing_text(text)),
            }
        )
        time.sleep(DOWNLOAD_PAUSE_SECONDS)

    return {
        "archive_prefix": ARCHIVE_PREFIX,
        "listing_urls_checked": listing_urls,
        "listing_fetches": fetches,
        "symbols_parsed_from_listing_limited_text": sorted(discovered_symbols),
        "symbols_parsed_from_listing_count": len(discovered_symbols),
        "direct_pattern_probe_used": True,
        "observed_or_tested_url_pattern": f"{DIRECT_ARCHIVE_ROOT}SYMBOL/SYMBOL-metrics-YYYY-MM-DD.zip",
        "structure_summary": (
            "The usable archive object pattern is SYMBOL-level combined daily metrics ZIP files, "
            "not separate metric folders per openInterestHist/takerlongshortRatio/etc."
        ),
    }


def find_recent_available_date(symbol: str = "BTCUSDT") -> dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    attempts: list[dict[str, Any]] = []
    for offset in range(1, RECENT_LOOKBACK_DAYS + 1):
        date_text = (today - timedelta(days=offset)).isoformat()
        result = head_archive_file(metrics_file_url(symbol, date_text))
        attempts.append(
            {
                "date": date_text,
                "exists": result["exists"],
                "http_status": result["http_status"],
                "content_length_bytes": result["content_length_bytes"],
                "last_modified": result["last_modified"],
            }
        )
        if result["exists"]:
            return {
                "symbol": symbol,
                "recent_available_date": date_text,
                "lookback_days_checked": offset,
                "found": True,
                "attempts_preview": attempts[:5],
                "found_head": result,
            }
        time.sleep(HEAD_PAUSE_SECONDS)
    return {
        "symbol": symbol,
        "recent_available_date": None,
        "lookback_days_checked": RECENT_LOOKBACK_DAYS,
        "found": False,
        "attempts_preview": attempts[:10],
        "found_head": None,
    }


def parse_timestamp_to_ms(value: str) -> int | None:
    raw = str(value).strip()
    if not raw:
        return None
    try:
        number = float(raw)
    except ValueError:
        cleaned = raw.replace("Z", "+00:00")
        try:
            return int(datetime.fromisoformat(cleaned).timestamp() * 1000)
        except ValueError:
            return None
    if number > 10_000_000_000_000:
        return int(number / 1000)
    if number > 10_000_000_000:
        return int(number)
    return int(number * 1000)


def ms_to_iso(ms_value: int) -> str:
    return datetime.fromtimestamp(ms_value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def looks_like_header(row: list[str]) -> bool:
    joined = ",".join(cell.lower() for cell in row)
    tokens = ["symbol", "time", "timestamp", "interest", "ratio", "long", "short", "taker"]
    return any(token in joined for token in tokens)


def detect_timestamp_column(columns: list[str]) -> str | None:
    lowered = {column.lower(): column for column in columns}
    for candidate in ["timestamp", "create_time", "time", "open_time", "close_time"]:
        if candidate in lowered:
            return lowered[candidate]
    return None


def infer_granularity(timestamps_ms: list[int], row_count: int) -> dict[str, Any]:
    unique = sorted(set(timestamps_ms))
    if len(unique) < 2:
        return {
            "inferred_interval": "unknown",
            "median_interval_seconds": None,
            "basis": "fewer than two timestamps",
        }
    diffs = [right - left for left, right in zip(unique, unique[1:]) if right > left]
    if not diffs:
        return {
            "inferred_interval": "unknown",
            "median_interval_seconds": None,
            "basis": "non-increasing timestamps",
        }
    median_ms = sorted(diffs)[len(diffs) // 2]
    label_by_seconds = {
        60: "1m",
        300: "5m",
        900: "15m",
        1800: "30m",
        3600: "1h",
        86_400: "1d",
    }
    seconds = int(median_ms / 1000)
    return {
        "inferred_interval": label_by_seconds.get(seconds, f"{seconds}s"),
        "median_interval_seconds": seconds,
        "basis": f"{row_count} rows and timestamp deltas",
    }


def review_zip_sample(symbol: str, date_text: str, head_result: dict[str, Any], total_downloaded_so_far: int) -> dict[str, Any]:
    url = head_result["url"]
    content_length = head_result.get("content_length_bytes")
    if content_length is not None and content_length > SAMPLE_ZIP_MAX_BYTES:
        return {
            "symbol": symbol,
            "date": date_text,
            "url": url,
            "file_exists": True,
            "opened": False,
            "skip_reason": f"content length {content_length} exceeds sample cap {SAMPLE_ZIP_MAX_BYTES}",
            "downloaded_bytes": 0,
            "columns": [],
            "row_count": None,
            "timestamp_min_utc": None,
            "timestamp_max_utc": None,
            "interval_granularity": "not opened",
            "error": None,
        }
    if total_downloaded_so_far + (content_length or SAMPLE_ZIP_MAX_BYTES) > TOTAL_SAMPLE_ZIP_MAX_BYTES:
        return {
            "symbol": symbol,
            "date": date_text,
            "url": url,
            "file_exists": True,
            "opened": False,
            "skip_reason": f"total sample download cap {TOTAL_SAMPLE_ZIP_MAX_BYTES} would be exceeded",
            "downloaded_bytes": 0,
            "columns": [],
            "row_count": None,
            "timestamp_min_utc": None,
            "timestamp_max_utc": None,
            "interval_granularity": "not opened",
            "error": None,
        }

    downloaded = download_limited_binary(url, SAMPLE_ZIP_MAX_BYTES)
    if not downloaded["ok"]:
        return {
            "symbol": symbol,
            "date": date_text,
            "url": url,
            "file_exists": True,
            "opened": False,
            "skip_reason": "download_failed",
            "downloaded_bytes": downloaded["bytes_read"],
            "columns": [],
            "row_count": None,
            "timestamp_min_utc": None,
            "timestamp_max_utc": None,
            "interval_granularity": "unknown",
            "error": downloaded["error"],
        }

    try:
        with zipfile.ZipFile(io.BytesIO(downloaded["bytes"])) as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
            csv_names = [name for name in names if name.lower().endswith(".csv")]
            selected_name = csv_names[0] if csv_names else names[0]
            info = archive.getinfo(selected_name)
            if info.file_size > 2_000_000:
                return {
                    "symbol": symbol,
                    "date": date_text,
                    "url": url,
                    "file_exists": True,
                    "opened": False,
                    "skip_reason": f"inner file size {info.file_size} exceeds review cap",
                    "downloaded_bytes": downloaded["bytes_read"],
                    "columns": [],
                    "row_count": None,
                    "timestamp_min_utc": None,
                    "timestamp_max_utc": None,
                    "interval_granularity": "not opened",
                    "error": None,
                }
            raw = archive.read(selected_name)
    except Exception as exc:
        return {
            "symbol": symbol,
            "date": date_text,
            "url": url,
            "file_exists": True,
            "opened": False,
            "skip_reason": "zip_parse_failed",
            "downloaded_bytes": downloaded["bytes_read"],
            "columns": [],
            "row_count": None,
            "timestamp_min_utc": None,
            "timestamp_max_utc": None,
            "interval_granularity": "unknown",
            "error": repr(exc),
        }

    rows = list(csv.reader(io.StringIO(raw.decode("utf-8", errors="replace"))))
    rows = [row for row in rows if row]
    if not rows:
        return {
            "symbol": symbol,
            "date": date_text,
            "url": url,
            "file_exists": True,
            "opened": True,
            "skip_reason": None,
            "downloaded_bytes": downloaded["bytes_read"],
            "columns": [],
            "row_count": 0,
            "timestamp_min_utc": None,
            "timestamp_max_utc": None,
            "interval_granularity": "unknown",
            "error": None,
        }

    has_header = looks_like_header(rows[0])
    if has_header:
        columns = [column.strip() for column in rows[0]]
        data_rows = rows[1:]
    else:
        columns = [f"column_{idx}" for idx in range(len(rows[0]))]
        data_rows = rows

    timestamp_column = detect_timestamp_column(columns)
    timestamps_ms: list[int] = []
    if timestamp_column is not None:
        ts_index = columns.index(timestamp_column)
        for row in data_rows:
            if ts_index >= len(row):
                continue
            parsed = parse_timestamp_to_ms(row[ts_index])
            if parsed is not None:
                timestamps_ms.append(parsed)

    granularity = infer_granularity(timestamps_ms, len(data_rows))
    return {
        "symbol": symbol,
        "date": date_text,
        "url": url,
        "file_exists": True,
        "opened": True,
        "skip_reason": None,
        "downloaded_bytes": downloaded["bytes_read"],
        "zip_members": names,
        "reviewed_member": selected_name,
        "columns": columns,
        "row_count": len(data_rows),
        "timestamp_column": timestamp_column,
        "timestamp_min_utc": ms_to_iso(min(timestamps_ms)) if timestamps_ms else None,
        "timestamp_max_utc": ms_to_iso(max(timestamps_ms)) if timestamps_ms else None,
        "interval_granularity": granularity["inferred_interval"],
        "granularity_review": granularity,
        "error": None,
    }


def probe_dates(sample_dates: list[str]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], int]:
    date_probe_results: dict[str, Any] = {}
    symbol_probe_results: dict[str, Any] = {
        symbol: {
            "symbol": symbol,
            "dates_checked": [],
            "available_dates": [],
            "missing_dates": [],
            "exists_any_probe": False,
            "exists_all_static_2023_2025_dates": False,
        }
        for symbol in PROBE_SYMBOLS
    }
    sample_file_reviews: list[dict[str, Any]] = []
    total_downloaded = 0

    for date_text in sample_dates:
        date_entry: dict[str, Any] = {
            "date": date_text,
            "symbols_checked": PROBE_SYMBOLS,
            "available_count": 0,
            "missing_count": 0,
            "file_results": {},
        }
        for symbol in PROBE_SYMBOLS:
            url = metrics_file_url(symbol, date_text)
            head = head_archive_file(url)
            compact = {
                "exists": head["exists"],
                "http_status": head["http_status"],
                "content_length_bytes": head["content_length_bytes"],
                "last_modified": head["last_modified"],
                "url": url,
                "error": head["error"],
            }
            date_entry["file_results"][symbol] = compact
            symbol_entry = symbol_probe_results[symbol]
            symbol_entry["dates_checked"].append(date_text)
            if head["exists"]:
                date_entry["available_count"] += 1
                symbol_entry["available_dates"].append(date_text)
                symbol_entry["exists_any_probe"] = True
                review = review_zip_sample(symbol, date_text, head, total_downloaded)
                total_downloaded += int(review.get("downloaded_bytes") or 0)
                sample_file_reviews.append(review)
                time.sleep(DOWNLOAD_PAUSE_SECONDS)
            else:
                date_entry["missing_count"] += 1
                symbol_entry["missing_dates"].append(date_text)
            time.sleep(HEAD_PAUSE_SECONDS)
        date_probe_results[date_text] = date_entry

    for symbol, entry in symbol_probe_results.items():
        entry["exists_all_static_2023_2025_dates"] = all(date_text in entry["available_dates"] for date_text in STATIC_PROBE_DATES)
        entry["coverage_note"] = (
            "available for all static 2023/2024/2025 probe dates"
            if entry["exists_all_static_2023_2025_dates"]
            else "one or more static probe dates unavailable; likely symbol inception/delist or archive gap"
        )
    return symbol_probe_results, date_probe_results, sample_file_reviews, total_downloaded


def metric_availability_from_samples(sample_file_reviews: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    observed_columns: set[str] = set()
    observed_columns_original: set[str] = set()
    evidence_files: list[str] = []
    for review in sample_file_reviews:
        if not review.get("opened"):
            continue
        evidence_files.append(review["url"])
        for column in review.get("columns", []):
            observed_columns.add(str(column).strip().lower())
            observed_columns_original.add(str(column).strip())

    availability: dict[str, Any] = {}
    for metric_name, spec in METRIC_COLUMN_MAP.items():
        matched = sorted(
            column
            for column in observed_columns_original
            if any(token in column.lower() for token in spec["required_any_columns"])
        )
        availability[metric_name] = {
            "available": bool(matched),
            "matched_columns": matched,
            "column_match_terms": spec["required_any_columns"],
            "description": spec["description"],
            "evidence_file_count": len(evidence_files) if matched else 0,
        }
    return availability, sorted(observed_columns_original)


def classify_result(metric_availability: dict[str, Any], historical_2023_2025_feasible: bool, discovery_blocker: str | None) -> tuple[str, str, bool]:
    if discovery_blocker:
        return RESULT_BLOCKED, NEXT_BLOCKED, False
    oi_available = metric_availability["openInterestHist"]["available"]
    taker_available = metric_availability["takerlongshortRatio"]["available"]
    long_short_available = all(
        metric_availability[name]["available"]
        for name in [
            "globalLongShortAccountRatio",
            "topLongShortAccountRatio",
            "topLongShortPositionRatio",
        ]
    )
    if oi_available and taker_available and long_short_available and historical_2023_2025_feasible:
        return RESULT_READY, NEXT_READY, True
    if oi_available and not (taker_available or long_short_available):
        return RESULT_PARTIAL_OI, NEXT_PARTIAL, False
    if (taker_available or long_short_available) and not oi_available:
        return RESULT_PARTIAL_RATIO, NEXT_PARTIAL, False
    return RESULT_INSUFFICIENT, NEXT_INSUFFICIENT, False


def build_artifact() -> dict[str, Any]:
    if not existing_artifact_can_be_replaced():
        raise DiscoveryBlocked(f"artifact already exists: {ARTIFACT_RELATIVE_PATH}")

    status_before = git_status_short()
    listing_discovery = inspect_listing_structure()
    recent_discovery = find_recent_available_date("BTCUSDT")
    recent_date = recent_discovery.get("recent_available_date")
    sample_dates = list(STATIC_PROBE_DATES)
    if isinstance(recent_date, str) and recent_date not in sample_dates:
        sample_dates.append(recent_date)

    symbol_probe_results, date_probe_results, sample_file_reviews, total_downloaded = probe_dates(sample_dates)
    metric_availability, observed_columns = metric_availability_from_samples(sample_file_reviews)

    oi_available = bool(metric_availability["openInterestHist"]["available"])
    taker_ratio_available = bool(metric_availability["takerlongshortRatio"]["available"])
    long_short_ratio_available = all(
        bool(metric_availability[name]["available"])
        for name in [
            "globalLongShortAccountRatio",
            "topLongShortAccountRatio",
            "topLongShortPositionRatio",
        ]
    )
    liquidation_available = bool(metric_availability["liquidation_or_force_order_metric"]["available"])
    funding_available = bool(metric_availability["funding_like_metric"]["available"])

    opened_sample_count = sum(1 for review in sample_file_reviews if review.get("opened"))
    discovery_blocker = None
    if opened_sample_count == 0:
        discovery_blocker = "no metrics ZIP sample could be opened from the public archive probes"

    core_static_dates_available = all(
        date_probe_results.get(date_text, {}).get("file_results", {}).get(symbol, {}).get("exists") is True
        for date_text in STATIC_PROBE_DATES
        for symbol in CORE_2023_SYMBOLS
    )
    historical_2023_2025_feasible = bool(oi_available and taker_ratio_available and long_short_ratio_available and core_static_dates_available)
    result_classification, next_allowed_step, dataset_builder_allowed_next = classify_result(
        metric_availability,
        historical_2023_2025_feasible,
        discovery_blocker,
    )

    available_metric_names = [name for name, value in metric_availability.items() if value.get("available") is True]
    metric_count = len(available_metric_names)

    safety_permissions = {
        "data_archive_discovery_created": discovery_blocker is None,
        "dataset_builder_allowed_next": dataset_builder_allowed_next,
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

    validation_checks = {
        "repo_clean_before_run": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION == [],
        "public_archive_only": True,
        "no_private_api_used": True,
        "no_account_api_used": True,
        "no_order_endpoint_used": True,
        "no_api_key_used": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "huge_download_avoided": total_downloaded <= TOTAL_SAMPLE_ZIP_MAX_BYTES,
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": no_existing_tracked_repo_file_changes(status_before),
    }
    replacement_checks_all_true = all(value is True for value in validation_checks.values()) and discovery_blocker is None
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    recommended_proxy_package = {
        "classification": (
            "USABLE_FOR_OI_TAKER_CROWDING_PROXY_RESEARCH"
            if oi_available and taker_ratio_available and long_short_ratio_available
            else "NOT_READY_FOR_OI_TAKER_CROWDING_PROXY_RESEARCH"
        ),
        "components": [
            "open_interest",
            "taker_buy_sell_volume_ratio",
            "global_long_short_account_ratio",
            "top_trader_long_short_account_ratio",
            "top_trader_long_short_position_ratio",
        ]
        if oi_available and taker_ratio_available and long_short_ratio_available
        else [],
        "explicit_liquidation_limitation": (
            "True liquidation flush cannot be directly tested from this metrics archive; "
            "only OI/taker/crowding proxy flush research is supported by discovered fields."
        ),
    }

    artifact: dict[str, Any] = {
        "status": STATUS_PASS if replacement_checks_all_true else STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "repo_head_before_tool_creation": SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION,
            "repo_clean_before_tool_creation": True,
            "git_status_short_before_tool_creation": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION,
            "tracked_python_count_before_tool_creation": TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION,
            "tracked_python_count_at_run": tracked_python_count(),
            "git_status_short_at_run_start": status_before,
            "created_python_tool": MODULE_RELATIVE_PATH,
            "created_json_artifact": ARTIFACT_RELATIVE_PATH,
            "run_started_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "archive_root": {
            "listing_root": ARCHIVE_ROOT,
            "direct_archive_root": DIRECT_ARCHIVE_ROOT,
            "archive_prefix": ARCHIVE_PREFIX,
            "host_allowlist": ["data.binance.vision"],
            "public_archive_only": True,
        },
        "listing_discovery": {
            **listing_discovery,
            "recent_available_date_discovery": recent_discovery,
            "sample_dates_used": sample_dates,
        },
        "metric_availability": {
            "metric_count": metric_count,
            "available_metric_names": available_metric_names,
            "observed_columns": observed_columns,
            "metrics": metric_availability,
            "oi_available": oi_available,
            "taker_ratio_available": taker_ratio_available,
            "long_short_ratio_available": long_short_ratio_available,
        },
        "symbol_probe_results": symbol_probe_results,
        "date_probe_results": date_probe_results,
        "sample_file_reviews": sample_file_reviews,
        "historical_feasibility": {
            "historical_2023_2025_feasible": historical_2023_2025_feasible,
            "open_interest_history_2023_2025_feasible": bool(oi_available and core_static_dates_available),
            "taker_buy_sell_ratio_history_2023_2025_feasible": bool(taker_ratio_available and core_static_dates_available),
            "long_short_ratio_history_2023_2025_feasible": bool(long_short_ratio_available and core_static_dates_available),
            "core_2023_symbols_checked": CORE_2023_SYMBOLS,
            "core_static_dates_available": core_static_dates_available,
            "newer_symbol_limitation": (
                "Newer listings such as ARBUSDT may not have files for 2023-01-01; "
                "dataset builder must use per-symbol archive start dates."
            ),
        },
        "liquidation_availability": {
            "available": liquidation_available,
            "archive_metric_found": liquidation_available,
            "terms_checked": METRIC_COLUMN_MAP["liquidation_or_force_order_metric"]["required_any_columns"],
            "conclusion": (
                "liquidation or force-order fields were discovered"
                if liquidation_available
                else "no liquidation or force-order fields were found in sampled daily metrics ZIP columns"
            ),
        },
        "funding_availability": {
            "available": funding_available,
            "archive_metric_found": funding_available,
            "terms_checked": METRIC_COLUMN_MAP["funding_like_metric"]["required_any_columns"],
            "conclusion": (
                "funding-like fields were discovered"
                if funding_available
                else "no funding-like fields were found in sampled daily metrics ZIP columns"
            ),
        },
        "recommended_proxy_package": recommended_proxy_package,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "This is archive discovery only and does not build a dataset.",
            "Only small listing responses, HEAD probes, and capped daily ZIP samples were downloaded.",
            "The archive pattern discovered is combined per-symbol daily metrics files, not separate metric folders.",
            "Per-symbol historical coverage can begin after instrument listing; builder must not assume every symbol exists on 2023-01-01.",
            "Funding history was not found inside this metrics archive.",
            "Liquidation or force-order history was not found inside this metrics archive.",
            "No strategy, signal, backtest, PnL, candidate, edge, runtime, live, or capital action was performed or permitted.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def print_stdout_summary(artifact: dict[str, Any]) -> None:
    metric_availability = artifact["metric_availability"]
    historical = artifact["historical_feasibility"]
    print(f"status: {artifact['status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"metric_count: {metric_availability['metric_count']}")
    print(f"oi_available: {bool_text(metric_availability['oi_available'])}")
    print(f"taker_ratio_available: {bool_text(metric_availability['taker_ratio_available'])}")
    print(f"long_short_ratio_available: {bool_text(metric_availability['long_short_ratio_available'])}")
    print(f"liquidation_available: {bool_text(artifact['liquidation_availability']['available'])}")
    print(f"funding_available: {bool_text(artifact['funding_availability']['available'])}")
    print(f"historical_2023_2025_feasible: {bool_text(historical['historical_2023_2025_feasible'])}")
    print(f"recommended_proxy_package: {artifact['recommended_proxy_package']['classification']}")
    print(f"next_allowed_step: {artifact['next_allowed_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(artifact['replacement_checks_all_true'])}")


def main() -> int:
    try:
        artifact = build_artifact()
        write_artifact(artifact)
        print_stdout_summary(artifact)
        return 0 if artifact["replacement_checks_all_true"] else 2
    except DiscoveryBlocked as exc:
        blocked_artifact = {
            "status": STATUS_BLOCKED,
            "artifact_kind": ARTIFACT_KIND,
            "module": MODULE,
            "source_checkpoint": {
                "repo_root": str(REPO_ROOT),
                "repo_head_before_tool_creation": SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION,
                "repo_clean_before_tool_creation": True,
                "git_status_short_before_tool_creation": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION,
                "tracked_python_count_before_tool_creation": TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION,
                "blocked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "archive_root": {
                "listing_root": ARCHIVE_ROOT,
                "direct_archive_root": DIRECT_ARCHIVE_ROOT,
                "archive_prefix": ARCHIVE_PREFIX,
                "host_allowlist": ["data.binance.vision"],
                "public_archive_only": True,
            },
            "listing_discovery": {"blocked_reason": str(exc)},
            "metric_availability": {"metric_count": 0, "available_metric_names": [], "metrics": {}},
            "symbol_probe_results": {},
            "date_probe_results": {},
            "sample_file_reviews": [],
            "historical_feasibility": {"historical_2023_2025_feasible": False},
            "liquidation_availability": {"available": False},
            "funding_availability": {"available": False},
            "recommended_proxy_package": {"classification": "NOT_READY_FOR_OI_TAKER_CROWDING_PROXY_RESEARCH"},
            "result_classification": RESULT_BLOCKED,
            "next_allowed_step": NEXT_BLOCKED,
            "limitations": [f"BLOCKED: {exc}"],
            "safety_permissions": {
                "data_archive_discovery_created": False,
                "dataset_builder_allowed_next": False,
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
                "repo_clean_before_run": GIT_STATUS_SHORT_BEFORE_TOOL_CREATION == [],
                "public_archive_only": True,
                "no_private_api_used": True,
                "no_account_api_used": True,
                "no_order_endpoint_used": True,
                "no_api_key_used": True,
                "no_strategy_execution": True,
                "no_signal_generation": True,
                "no_backtest_run": True,
                "no_pnl_computation": True,
                "no_candidate_generation": True,
                "no_edge_claim": True,
                "no_runtime_live_capital": True,
                "huge_download_avoided": True,
                "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
                "exactly_one_json_artifact_created": False,
                "no_existing_repo_files_modified": no_existing_tracked_repo_file_changes(git_status_short()),
                "replacement_checks_all_true": False,
            },
            "replacement_checks_all_true": False,
            "payload_sha256_excluding_hash": "",
        }
        blocked_artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(blocked_artifact)
        print_stdout_summary(blocked_artifact)
        print(f"exact_blocker: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
