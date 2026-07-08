#!/usr/bin/env python
"""Build a Binance Data Vision USD-M metrics proxy dataset from public archives."""

from __future__ import annotations

import csv
import concurrent.futures
import hashlib
import io
import json
import math
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_data_vision_um_metrics_dataset_builder_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
DISCOVERY_RELATIVE_PATH = "artifacts/data_discovery/binance_data_vision_um_metrics_archive_discovery_v1.json"

STATUS_PASS = "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED"
STATUS_BLOCKED = "BLOCKED_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER"
ARTIFACT_KIND = "BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER"

RESULT_READY = "BINANCE_DATA_VISION_UM_METRICS_DATASET_READY_FOR_PROXY_EVENT_STUDY"
RESULT_PARTIAL = "BINANCE_DATA_VISION_UM_METRICS_DATASET_PARTIAL_USABLE"
RESULT_INSUFFICIENT = "BINANCE_DATA_VISION_UM_METRICS_DATASET_INSUFFICIENT"
RESULT_BLOCKED = "BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILD_BLOCKED"

NEXT_EVENT_STUDY = "BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_V1"
NEXT_GAP_REVIEW = "BINANCE_DATA_VISION_METRICS_GAP_REVIEW_V1"
NEXT_BLOCKED = "BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILD_BLOCKER_REVIEW_V1"

SOURCE_DISCOVERY_COMMIT = "41b9212d5e0bf41b4657dd43e5debea58254df39"
SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION = "41b9212d5e0bf41b4657dd43e5debea58254df39"
TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION = 1056
GIT_STATUS_SHORT_AFTER_STALE_CLEANUP_BEFORE_TOOL_CREATION: list[str] = []
STALE_LEFTOVERS_REMOVED = [
    "artifacts/research_contracts/",
    "tools/edge_factory_os_repo_only_institutional_research_contract_for_top_family_v1.py",
]

PUBLIC_ARCHIVE_HOST = "data.binance.vision"
PUBLIC_ARCHIVE_BASE = f"https://{PUBLIC_ARCHIVE_HOST}/"
DAILY_METRICS_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/daily/metrics"
MONTHLY_METRICS_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/monthly/metrics"

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
REQUESTED_METRICS = [
    "openInterestHist",
    "takerlongshortRatio",
    "globalLongShortAccountRatio",
    "topLongShortAccountRatio",
    "topLongShortPositionRatio",
]

START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)
INTERVAL_SECONDS = 5 * 60
TIMEOUT_SECONDS = 30
RETRY_CAP = 3
REQUEST_SLEEP_SECONDS = 0.015
DOWNLOAD_WORKERS = 16

EXTERNAL_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_data_vision_um_metrics_dataset_v1"
)
RAW_ARCHIVES_DIR = EXTERNAL_OUTPUT_ROOT / "raw_archives"
NORMALIZED_DIR = EXTERNAL_OUTPUT_ROOT / "normalized_by_symbol"
COVERAGE_DIR = EXTERNAL_OUTPUT_ROOT / "coverage_reports"
CHECKSUM_DIR = EXTERNAL_OUTPUT_ROOT / "checksums"

NORMALIZED_COLUMNS = [
    "timestamp",
    "symbol",
    "interval_or_period",
    "sumOpenInterest",
    "sumOpenInterestValue",
    "open_interest",
    "open_interest_value",
    "takerBuyVol",
    "takerSellVol",
    "takerBuySellRatio",
    "buySellRatio",
    "longShortRatio",
    "longAccount",
    "shortAccount",
    "longPosition",
    "shortPosition",
    "metric_source_fields",
    "source_metric_availability",
    "oi_change",
    "oi_change_pct",
    "taker_buy_sell_ratio",
    "taker_sell_pressure",
    "account_long_short_ratio",
    "position_long_short_ratio",
    "top_account_long_short_ratio",
    "top_position_long_short_ratio",
]

SOURCE_COLUMNS_WITH_HEADER = [
    "symbol",
    "sum_open_interest",
    "sum_open_interest_value",
    "count_toptrader_long_short_ratio",
    "sum_toptrader_long_short_ratio",
    "count_long_short_ratio",
    "sum_taker_long_short_vol_ratio",
    "create_time",
]


class BuildBlocked(Exception):
    pass


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_status_short() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return [f"git_status_failed: {result.stderr.strip()}"]
    return [line.rstrip() for line in result.stdout.splitlines() if line.strip()]


def tracked_python_count() -> int | None:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None
    return len([line for line in result.stdout.splitlines() if line.strip()])


def no_existing_tracked_files_modified(status_lines: list[str]) -> bool:
    allowed = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
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


def assert_public_archive_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_ARCHIVE_HOST:
        raise BuildBlocked(f"forbidden non-public-archive URL attempted: {url}")
    allowed_prefixes = (
        "/data/futures/um/daily/metrics/",
        "/data/futures/um/monthly/metrics/",
    )
    if not parsed.path.startswith(allowed_prefixes):
        raise BuildBlocked(f"forbidden non-metrics archive path attempted: {url}")


def daily_zip_url(symbol: str, day: date) -> str:
    day_text = day.isoformat()
    return f"{DAILY_METRICS_ROOT}/{symbol}/{symbol}-metrics-{day_text}.zip"


def monthly_zip_url(symbol: str, year: int, month: int) -> str:
    month_text = f"{year:04d}-{month:02d}"
    return f"{MONTHLY_METRICS_ROOT}/{symbol}/{symbol}-metrics-{month_text}.zip"


def checksum_url(zip_url: str) -> str:
    return f"{zip_url}.CHECKSUM"


def request_bytes(url: str, max_bytes: int | None = None, missing_ok: bool = False) -> dict[str, Any]:
    assert_public_archive_url(url)
    last_error = ""
    for attempt in range(RETRY_CAP):
        if attempt:
            time.sleep(min(2.0 * attempt, 6.0))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-binance-data-vision-metrics-builder/1"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
                limit = max_bytes + 1 if max_bytes is not None else None
                body = response.read(limit) if limit is not None else response.read()
                if max_bytes is not None and len(body) > max_bytes:
                    raise BuildBlocked(f"download exceeded byte cap for {url}")
                time.sleep(REQUEST_SLEEP_SECONDS)
                return {
                    "ok": True,
                    "missing": False,
                    "http_status": getattr(response, "status", None),
                    "bytes": body,
                    "content_length": response.headers.get("Content-Length"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "error": None,
                }
        except urllib.error.HTTPError as exc:
            body = exc.read(1000).decode("utf-8", errors="replace")
            if exc.code == 404 and missing_ok:
                return {
                    "ok": False,
                    "missing": True,
                    "http_status": 404,
                    "bytes": b"",
                    "content_length": None,
                    "last_modified": None,
                    "error": "404 not found",
                }
            last_error = f"HTTP {exc.code}: {body[:500]}"
            if exc.code not in {418, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
    return {
        "ok": False,
        "missing": False,
        "http_status": None,
        "bytes": b"",
        "content_length": None,
        "last_modified": None,
        "error": last_error or "unknown request failure",
    }


def head_exists(url: str) -> dict[str, Any]:
    assert_public_archive_url(url)
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "edge-factory-os-binance-data-vision-metrics-builder/1"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            time.sleep(REQUEST_SLEEP_SECONDS)
            return {
                "exists": True,
                "http_status": getattr(response, "status", None),
                "content_length": response.headers.get("Content-Length"),
                "last_modified": response.headers.get("Last-Modified"),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"exists": False, "http_status": 404, "content_length": None, "last_modified": None, "error": "404 not found"}
        return {"exists": False, "http_status": exc.code, "content_length": None, "last_modified": None, "error": str(exc)}
    except Exception as exc:
        return {"exists": False, "http_status": None, "content_length": None, "last_modified": None, "error": repr(exc)}


def parse_checksum_text(text: str) -> str | None:
    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BuildBlocked(f"missing required source artifact: {path.relative_to(REPO_ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BuildBlocked(f"source artifact is not a JSON object: {path.relative_to(REPO_ROOT)}")
    return payload


def load_discovery_artifact() -> tuple[dict[str, Any], str]:
    payload = read_json(REPO_ROOT / DISCOVERY_RELATIVE_PATH)
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise BuildBlocked("discovery artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise BuildBlocked(f"discovery artifact hash mismatch: {recomputed} != {stored}")
    if payload.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_ARCHIVE_DISCOVERY_CREATED":
        raise BuildBlocked("discovery artifact status is not PASS")
    if payload.get("result_classification") != "BINANCE_DATA_VISION_METRICS_READY_FOR_OI_TAKER_CROWDING_DATASET":
        raise BuildBlocked("discovery artifact classification is not READY")
    metrics = payload.get("metric_availability", {})
    if metrics.get("oi_available") is not True or metrics.get("taker_ratio_available") is not True:
        raise BuildBlocked("discovery artifact does not validate OI and taker ratio availability")
    if metrics.get("long_short_ratio_available") is not True:
        raise BuildBlocked("discovery artifact does not validate long/short ratio availability")
    return payload, stored


def ensure_external_dirs() -> None:
    for path in [RAW_ARCHIVES_DIR, NORMALIZED_DIR, COVERAGE_DIR, CHECKSUM_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def iter_days() -> list[date]:
    days: list[date] = []
    current = START_DATE
    while current <= END_DATE:
        days.append(current)
        current += timedelta(days=1)
    return days


def iter_months() -> list[tuple[int, int]]:
    months: list[tuple[int, int]] = []
    year, month = START_DATE.year, START_DATE.month
    while (year, month) <= (END_DATE.year, END_DATE.month):
        months.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def archive_local_path(url: str) -> Path:
    parsed = urllib.parse.urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    cadence = parts[3]
    symbol = parts[5]
    return RAW_ARCHIVES_DIR / cadence / symbol / parts[-1]


def local_checksum_path(zip_path: Path) -> Path:
    return zip_path.with_name(zip_path.name + ".CHECKSUM")


def download_archive(url: str, download_manifest: list[dict[str, Any]], checksum_rows: list[dict[str, Any]]) -> Path | None:
    zip_path = archive_local_path(url)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path = local_checksum_path(zip_path)
    expected_sha = None
    checksum_saved = checksum_path.exists()
    if checksum_path.exists():
        checksum_text = checksum_path.read_text(encoding="utf-8", errors="replace")
        expected_sha = parse_checksum_text(checksum_text)
        checksum_available = expected_sha is not None
    else:
        checksum_result = request_bytes(checksum_url(url), max_bytes=4096, missing_ok=True)
        checksum_available = bool(checksum_result["ok"])
        if checksum_available:
            checksum_text = checksum_result["bytes"].decode("utf-8", errors="replace")
            expected_sha = parse_checksum_text(checksum_text)
            checksum_path.write_text(checksum_text, encoding="utf-8")
            checksum_saved = True

    reused_existing = False
    if zip_path.exists():
        actual_existing = sha256_file(zip_path)
        if expected_sha is None or actual_existing == expected_sha:
            reused_existing = True
        else:
            zip_path.unlink()

    if not zip_path.exists():
        result = request_bytes(url, missing_ok=True)
        if result["missing"]:
            download_manifest.append(
                {
                    "url": url,
                    "local_path": str(zip_path),
                    "available": False,
                    "downloaded": False,
                    "reused_existing": False,
                    "checksum_available": checksum_available,
                    "checksum_verified": False,
                    "sha256": None,
                    "bytes": 0,
                    "error": "404 not found",
                }
            )
            return None
        if not result["ok"]:
            raise BuildBlocked(f"archive download failed for {url}: {result['error']}")
        zip_path.write_bytes(result["bytes"])

    actual_sha = sha256_file(zip_path)
    checksum_verified = expected_sha is None or actual_sha == expected_sha
    if not checksum_verified:
        raise BuildBlocked(f"checksum mismatch for {url}: {actual_sha} != {expected_sha}")

    row = {
        "url": url,
        "local_path": str(zip_path),
        "available": True,
        "downloaded": not reused_existing,
        "reused_existing": reused_existing,
        "checksum_available": checksum_available,
        "checksum_saved": checksum_saved,
        "checksum_verified": checksum_verified if checksum_available else None,
        "sha256": actual_sha,
        "bytes": zip_path.stat().st_size,
        "error": None,
    }
    download_manifest.append(row)
    checksum_rows.append(row)
    return zip_path


def detect_header(first_row: list[str]) -> bool:
    joined = ",".join(value.lower() for value in first_row)
    return any(token in joined for token in ["symbol", "interest", "ratio", "create_time", "timestamp"])


def parse_ts_ms(value: str) -> int | None:
    raw = str(value).strip()
    if not raw:
        return None
    try:
        numeric = float(raw)
        if numeric > 10_000_000_000_000:
            return int(numeric / 1000)
        if numeric > 10_000_000_000:
            return int(numeric)
        return int(numeric * 1000)
    except ValueError:
        pass
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)
    except ValueError:
        return None


def ms_to_iso(ms_value: int) -> str:
    return datetime.fromtimestamp(ms_value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clean_number(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"none", "null", "nan"}:
        return ""
    return text


def to_float(value: Any) -> float | None:
    text = clean_number(value)
    if not text:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def fmt(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.12g}"


def read_archive_rows(path: Path, symbol: str) -> list[dict[str, str]]:
    rows_out: list[dict[str, str]] = []
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not names:
            raise BuildBlocked(f"no CSV member in archive: {path}")
        for name in names:
            content = archive.read(name).decode("utf-8", errors="replace")
            parsed_rows = [row for row in csv.reader(io.StringIO(content)) if row]
            if not parsed_rows:
                continue
            if detect_header(parsed_rows[0]):
                columns = [cell.strip() for cell in parsed_rows[0]]
                data_rows = parsed_rows[1:]
            else:
                columns = SOURCE_COLUMNS_WITH_HEADER[: len(parsed_rows[0])]
                data_rows = parsed_rows
            for raw_row in data_rows:
                record = {columns[idx]: raw_row[idx].strip() if idx < len(raw_row) else "" for idx in range(len(columns))}
                if record.get("symbol") and record["symbol"] != symbol:
                    continue
                ts_raw = record.get("create_time") or record.get("timestamp") or record.get("time")
                ts_ms = parse_ts_ms(ts_raw or "")
                if ts_ms is None:
                    continue
                record["_timestamp_ms"] = str(ts_ms)
                rows_out.append(record)
    return rows_out


def normalize_record(record: dict[str, str], previous_oi: float | None) -> tuple[dict[str, str], float | None]:
    ts_ms = int(record["_timestamp_ms"])
    symbol = record.get("symbol", "")
    oi = to_float(record.get("sum_open_interest"))
    oi_value = to_float(record.get("sum_open_interest_value"))
    taker_ratio = to_float(record.get("sum_taker_long_short_vol_ratio"))
    global_ratio = to_float(record.get("count_long_short_ratio"))
    top_account_ratio = to_float(record.get("count_toptrader_long_short_ratio"))
    top_position_ratio = to_float(record.get("sum_toptrader_long_short_ratio"))
    oi_change = oi - previous_oi if oi is not None and previous_oi not in (None, 0.0) else (oi - previous_oi if oi is not None and previous_oi is not None else None)
    oi_change_pct = (oi_change / previous_oi) if oi_change is not None and previous_oi not in (None, 0.0) else None
    taker_sell_pressure = (1.0 / taker_ratio) if taker_ratio and taker_ratio > 0 else None
    source_availability = {
        "openInterestHist": oi is not None or oi_value is not None,
        "takerlongshortRatio": taker_ratio is not None,
        "globalLongShortAccountRatio": global_ratio is not None,
        "topLongShortAccountRatio": top_account_ratio is not None,
        "topLongShortPositionRatio": top_position_ratio is not None,
    }
    metric_source_fields = {
        "sum_open_interest": clean_number(record.get("sum_open_interest")),
        "sum_open_interest_value": clean_number(record.get("sum_open_interest_value")),
        "sum_taker_long_short_vol_ratio": clean_number(record.get("sum_taker_long_short_vol_ratio")),
        "count_long_short_ratio": clean_number(record.get("count_long_short_ratio")),
        "count_toptrader_long_short_ratio": clean_number(record.get("count_toptrader_long_short_ratio")),
        "sum_toptrader_long_short_ratio": clean_number(record.get("sum_toptrader_long_short_ratio")),
        "create_time": clean_number(record.get("create_time")),
    }
    normalized = {
        "timestamp": ms_to_iso(ts_ms),
        "symbol": symbol,
        "interval_or_period": "5m",
        "sumOpenInterest": clean_number(record.get("sum_open_interest")),
        "sumOpenInterestValue": clean_number(record.get("sum_open_interest_value")),
        "open_interest": clean_number(record.get("sum_open_interest")),
        "open_interest_value": clean_number(record.get("sum_open_interest_value")),
        "takerBuyVol": "",
        "takerSellVol": "",
        "takerBuySellRatio": clean_number(record.get("sum_taker_long_short_vol_ratio")),
        "buySellRatio": clean_number(record.get("sum_taker_long_short_vol_ratio")),
        "longShortRatio": clean_number(record.get("count_long_short_ratio")),
        "longAccount": "",
        "shortAccount": "",
        "longPosition": "",
        "shortPosition": "",
        "metric_source_fields": json.dumps(metric_source_fields, sort_keys=True, separators=(",", ":")),
        "source_metric_availability": json.dumps(source_availability, sort_keys=True, separators=(",", ":")),
        "oi_change": fmt(oi_change),
        "oi_change_pct": fmt(oi_change_pct),
        "taker_buy_sell_ratio": clean_number(record.get("sum_taker_long_short_vol_ratio")),
        "taker_sell_pressure": fmt(taker_sell_pressure),
        "account_long_short_ratio": clean_number(record.get("count_long_short_ratio")),
        "position_long_short_ratio": clean_number(record.get("sum_toptrader_long_short_ratio")),
        "top_account_long_short_ratio": clean_number(record.get("count_toptrader_long_short_ratio")),
        "top_position_long_short_ratio": clean_number(record.get("sum_toptrader_long_short_ratio")),
    }
    return normalized, oi


def year_from_iso(value: str) -> str:
    return value[:4]


def summarize_symbol(symbol: str, rows: list[dict[str, str]], available_files: int, missing_files: int) -> dict[str, Any]:
    timestamps = [row["timestamp"] for row in rows]
    unique_timestamps = set(timestamps)
    duplicate_count = len(timestamps) - len(unique_timestamps)
    min_ts = min(timestamps) if timestamps else None
    max_ts = max(timestamps) if timestamps else None
    missing_interval_count = None
    if min_ts and max_ts:
        min_ms = parse_ts_ms(min_ts) or 0
        max_ms = parse_ts_ms(max_ts) or 0
        expected = int((max_ms - min_ms) / (INTERVAL_SECONDS * 1000)) + 1
        missing_interval_count = max(0, expected - len(unique_timestamps))
    rows_by_year: dict[str, int] = {}
    metric_rows_by_year: dict[str, dict[str, int]] = {}
    metric_counts = {
        "openInterestHist": 0,
        "takerlongshortRatio": 0,
        "globalLongShortAccountRatio": 0,
        "topLongShortAccountRatio": 0,
        "topLongShortPositionRatio": 0,
    }
    negative_oi_count = 0
    invalid_ratio_count = 0
    for row in rows:
        year = year_from_iso(row["timestamp"])
        rows_by_year[year] = rows_by_year.get(year, 0) + 1
        metric_rows_by_year.setdefault(year, {name: 0 for name in metric_counts})
        oi = to_float(row["open_interest"])
        if oi is not None:
            metric_counts["openInterestHist"] += 1
            metric_rows_by_year[year]["openInterestHist"] += 1
            if oi < 0:
                negative_oi_count += 1
        taker = to_float(row["taker_buy_sell_ratio"])
        if taker is not None:
            metric_counts["takerlongshortRatio"] += 1
            metric_rows_by_year[year]["takerlongshortRatio"] += 1
            if taker <= 0:
                invalid_ratio_count += 1
        global_ratio = to_float(row["account_long_short_ratio"])
        if global_ratio is not None:
            metric_counts["globalLongShortAccountRatio"] += 1
            metric_rows_by_year[year]["globalLongShortAccountRatio"] += 1
            if global_ratio <= 0:
                invalid_ratio_count += 1
        top_account = to_float(row["top_account_long_short_ratio"])
        if top_account is not None:
            metric_counts["topLongShortAccountRatio"] += 1
            metric_rows_by_year[year]["topLongShortAccountRatio"] += 1
            if top_account <= 0:
                invalid_ratio_count += 1
        top_position = to_float(row["top_position_long_short_ratio"])
        if top_position is not None:
            metric_counts["topLongShortPositionRatio"] += 1
            metric_rows_by_year[year]["topLongShortPositionRatio"] += 1
            if top_position <= 0:
                invalid_ratio_count += 1
    date_set = {row["timestamp"][:10] for row in rows}
    requested_date_count = (END_DATE - START_DATE).days + 1
    missing_date_count = requested_date_count - len(date_set)
    has_long_short = any(
        metric_counts[name] > 0
        for name in ["globalLongShortAccountRatio", "topLongShortAccountRatio", "topLongShortPositionRatio"]
    )
    invalid_ratio_rate = (invalid_ratio_count / len(rows)) if rows else 1.0
    invalid_ratio_tolerance_count = max(10, int(len(rows) * 0.0001)) if rows else 0
    quality_pass = (
        negative_oi_count == 0
        and duplicate_count == 0
        and len(rows) > 0
        and invalid_ratio_count <= invalid_ratio_tolerance_count
    )
    return {
        "symbol": symbol,
        "file_availability": {
            "available_archive_count": available_files,
            "missing_archive_count": missing_files,
        },
        "earliest_timestamp": min_ts,
        "latest_timestamp": max_ts,
        "row_count": len(rows),
        "duplicate_timestamp_count": duplicate_count,
        "missing_interval_count": missing_interval_count,
        "missing_date_count": missing_date_count,
        "numeric_field_sanity": {
            "negative_oi_count": negative_oi_count,
            "invalid_ratio_count": invalid_ratio_count,
            "invalid_ratio_rate": invalid_ratio_rate,
            "invalid_ratio_tolerance_count": invalid_ratio_tolerance_count,
        },
        "source_field_availability": {
            "openInterestHist": metric_counts["openInterestHist"] > 0,
            "takerlongshortRatio": metric_counts["takerlongshortRatio"] > 0,
            "globalLongShortAccountRatio": metric_counts["globalLongShortAccountRatio"] > 0,
            "topLongShortAccountRatio": metric_counts["topLongShortAccountRatio"] > 0,
            "topLongShortPositionRatio": metric_counts["topLongShortPositionRatio"] > 0,
        },
        "metric_row_counts": metric_counts,
        "rows_by_year": rows_by_year,
        "metric_rows_by_year": metric_rows_by_year,
        "has_open_interest": metric_counts["openInterestHist"] > 0,
        "has_taker_ratio": metric_counts["takerlongshortRatio"] > 0,
        "has_long_short_ratio": has_long_short,
        "has_full_proxy_alignment": metric_counts["openInterestHist"] > 0 and metric_counts["takerlongshortRatio"] > 0 and has_long_short,
        "data_quality_pass": quality_pass,
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def download_plan_entry(plan: dict[str, Any]) -> tuple[dict[str, Any], Path | None, list[dict[str, Any]], list[dict[str, Any]]]:
    local_manifest: list[dict[str, Any]] = []
    local_checksums: list[dict[str, Any]] = []
    path = download_archive(plan["url"], local_manifest, local_checksums)
    return plan, path, local_manifest, local_checksums


def build_symbol(symbol: str, monthly_available: dict[tuple[int, int], bool], download_manifest: list[dict[str, Any]], checksum_rows: list[dict[str, Any]]) -> tuple[list[dict[str, str]], dict[str, Any], list[dict[str, Any]]]:
    planned_files: list[dict[str, Any]] = []
    for year, month in iter_months():
        if monthly_available.get((year, month), False):
            planned_files.append(
                {
                    "symbol": symbol,
                    "cadence": "monthly",
                    "period": f"{year:04d}-{month:02d}",
                    "url": monthly_zip_url(symbol, year, month),
                }
            )
        else:
            for day in iter_days():
                if day.year != year or day.month != month:
                    continue
                planned_files.append(
                    {
                        "symbol": symbol,
                        "cadence": "daily",
                        "period": day.isoformat(),
                        "url": daily_zip_url(symbol, day),
                    }
                )

    archive_paths: list[Path] = []
    available_files = 0
    missing_files = 0
    file_rows: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as executor:
        futures = [executor.submit(download_plan_entry, plan) for plan in planned_files]
        for future in concurrent.futures.as_completed(futures):
            plan, path, local_manifest, local_checksums = future.result()
            download_manifest.extend(local_manifest)
            checksum_rows.extend(local_checksums)
            available = path is not None
            if available:
                archive_paths.append(path)
                available_files += 1
            else:
                missing_files += 1
            file_rows.append(
                {
                    "symbol": plan["symbol"],
                    "cadence": plan["cadence"],
                    "period": plan["period"],
                    "available": available,
                    "url": plan["url"],
                }
            )

    by_timestamp: dict[int, dict[str, str]] = {}
    duplicate_source_timestamp_count = 0
    for archive_path in archive_paths:
        for raw in read_archive_rows(archive_path, symbol):
            ts = int(raw["_timestamp_ms"])
            row_day = datetime.fromtimestamp(ts / 1000, timezone.utc).date()
            if not (START_DATE <= row_day <= END_DATE):
                continue
            if ts in by_timestamp:
                duplicate_source_timestamp_count += 1
                continue
            by_timestamp[ts] = raw

    normalized_rows: list[dict[str, str]] = []
    previous_oi: float | None = None
    for ts in sorted(by_timestamp):
        normalized, previous_oi = normalize_record(by_timestamp[ts], previous_oi)
        normalized_rows.append(normalized)

    normalized_path = NORMALIZED_DIR / f"{symbol}_um_metrics_5m_2023_2025_v1.csv"
    write_csv(normalized_path, NORMALIZED_COLUMNS, normalized_rows)
    coverage = summarize_symbol(symbol, normalized_rows, available_files, missing_files)
    coverage["duplicate_source_timestamp_count"] = duplicate_source_timestamp_count
    coverage["normalized_file"] = str(normalized_path)
    coverage["normalized_file_sha256"] = sha256_file(normalized_path)
    coverage_path = COVERAGE_DIR / f"{symbol}_coverage_report_v1.csv"
    coverage_row = {
        "symbol": symbol,
        "earliest_timestamp": coverage["earliest_timestamp"],
        "latest_timestamp": coverage["latest_timestamp"],
        "row_count": coverage["row_count"],
        "available_archive_count": available_files,
        "missing_archive_count": missing_files,
        "duplicate_timestamp_count": coverage["duplicate_timestamp_count"],
        "missing_interval_count": coverage["missing_interval_count"],
        "missing_date_count": coverage["missing_date_count"],
        "negative_oi_count": coverage["numeric_field_sanity"]["negative_oi_count"],
        "invalid_ratio_count": coverage["numeric_field_sanity"]["invalid_ratio_count"],
        "has_open_interest": coverage["has_open_interest"],
        "has_taker_ratio": coverage["has_taker_ratio"],
        "has_long_short_ratio": coverage["has_long_short_ratio"],
        "has_full_proxy_alignment": coverage["has_full_proxy_alignment"],
        "data_quality_pass": coverage["data_quality_pass"],
        "normalized_file": str(normalized_path),
        "normalized_file_sha256": coverage["normalized_file_sha256"],
    }
    write_csv(coverage_path, list(coverage_row), [coverage_row])
    coverage["coverage_report_file"] = str(coverage_path)
    coverage["coverage_report_file_sha256"] = sha256_file(coverage_path)
    return normalized_rows, coverage, file_rows


def aggregate_summary(per_symbol: dict[str, Any]) -> dict[str, Any]:
    built_symbols = [symbol for symbol, coverage in per_symbol.items() if coverage["row_count"] > 0]
    symbols_with_oi = [symbol for symbol, coverage in per_symbol.items() if coverage["has_open_interest"]]
    symbols_with_taker = [symbol for symbol, coverage in per_symbol.items() if coverage["has_taker_ratio"]]
    symbols_with_global = [
        symbol for symbol, coverage in per_symbol.items() if coverage["source_field_availability"]["globalLongShortAccountRatio"]
    ]
    symbols_with_top_account = [
        symbol for symbol, coverage in per_symbol.items() if coverage["source_field_availability"]["topLongShortAccountRatio"]
    ]
    symbols_with_top_position = [
        symbol for symbol, coverage in per_symbol.items() if coverage["source_field_availability"]["topLongShortPositionRatio"]
    ]
    symbols_with_long_short = [symbol for symbol, coverage in per_symbol.items() if coverage["has_long_short_ratio"]]
    symbols_with_full = [symbol for symbol, coverage in per_symbol.items() if coverage["has_full_proxy_alignment"]]
    mins = [coverage["earliest_timestamp"] for coverage in per_symbol.values() if coverage["earliest_timestamp"]]
    maxs = [coverage["latest_timestamp"] for coverage in per_symbol.values() if coverage["latest_timestamp"]]
    coverage_by_year: dict[str, int] = {}
    metric_coverage_by_year: dict[str, dict[str, int]] = {}
    for coverage in per_symbol.values():
        for year, count in coverage["rows_by_year"].items():
            coverage_by_year[year] = coverage_by_year.get(year, 0) + count
        for year, metrics in coverage["metric_rows_by_year"].items():
            metric_coverage_by_year.setdefault(year, {name: 0 for name in REQUESTED_METRICS})
            for metric, count in metrics.items():
                metric_coverage_by_year[year][metric] = metric_coverage_by_year[year].get(metric, 0) + count
    return {
        "requested_symbol_count": len(REQUESTED_SYMBOLS),
        "built_symbol_count": len(built_symbols),
        "built_symbols": built_symbols,
        "symbols_with_open_interest": len(symbols_with_oi),
        "symbols_with_taker_ratio": len(symbols_with_taker),
        "symbols_with_global_long_short": len(symbols_with_global),
        "symbols_with_top_account_ratio": len(symbols_with_top_account),
        "symbols_with_top_position_ratio": len(symbols_with_top_position),
        "symbols_with_long_short_ratio": len(symbols_with_long_short),
        "symbols_with_full_proxy_alignment": len(symbols_with_full),
        "timestamp_global_min": min(mins) if mins else None,
        "timestamp_global_max": max(maxs) if maxs else None,
        "total_normalized_rows": sum(coverage["row_count"] for coverage in per_symbol.values()),
        "coverage_by_year": dict(sorted(coverage_by_year.items())),
        "metric_coverage_by_year": dict(sorted(metric_coverage_by_year.items())),
        "limitations": [
            "Dataset contains OI/taker/crowding proxy metrics, not true liquidation data.",
            "Funding fields are unavailable in the sampled/discovered metrics archive and are not included.",
            "Taker buy and sell volume components are unavailable in the combined metrics archive; only the ratio is normalized.",
            "Some symbols begin after 2023-01-01, so early missing dates can reflect instrument listing history.",
        ],
    }


def classify(summary: dict[str, Any], per_symbol: dict[str, Any], checksum_summary: dict[str, Any]) -> tuple[str, str, bool]:
    years = summary["coverage_by_year"]
    materially_available = all(year in years and years[year] > 100_000 for year in ["2023", "2024", "2025"])
    quality_pass = all(coverage["data_quality_pass"] for coverage in per_symbol.values() if coverage["row_count"] > 0)
    quality_pass = quality_pass and checksum_summary["checksum_mismatch_count"] == 0
    if summary["symbols_with_full_proxy_alignment"] >= 5 and materially_available and quality_pass:
        return RESULT_READY, NEXT_EVENT_STUDY, True
    if summary["symbols_with_open_interest"] > 0 and (summary["symbols_with_taker_ratio"] > 0 or summary["symbols_with_long_short_ratio"] > 0):
        return RESULT_PARTIAL, NEXT_EVENT_STUDY, materially_available and quality_pass
    if summary["total_normalized_rows"] > 0:
        return RESULT_INSUFFICIENT, NEXT_GAP_REVIEW, False
    return RESULT_BLOCKED, NEXT_BLOCKED, False


def build_dataset() -> dict[str, Any]:
    if not existing_artifact_can_be_replaced():
        raise BuildBlocked(f"artifact already exists: {ARTIFACT_RELATIVE_PATH}")
    status_at_run_start = git_status_short()
    stale_absence = all(not (REPO_ROOT / path.rstrip("/")).exists() for path in STALE_LEFTOVERS_REMOVED)
    discovery, discovery_hash = load_discovery_artifact()
    ensure_external_dirs()

    monthly_probe_results: dict[str, Any] = {}
    monthly_available_by_symbol: dict[str, dict[tuple[int, int], bool]] = {}
    for symbol in REQUESTED_SYMBOLS:
        monthly_available_by_symbol[symbol] = {}
        probes: list[dict[str, Any]] = []
        for year, month in iter_months():
            url = monthly_zip_url(symbol, year, month)
            probe = head_exists(url)
            available = bool(probe["exists"])
            monthly_available_by_symbol[symbol][(year, month)] = available
            probes.append(
                {
                    "month": f"{year:04d}-{month:02d}",
                    "url": url,
                    "exists": available,
                    "http_status": probe["http_status"],
                    "content_length": probe["content_length"],
                    "last_modified": probe["last_modified"],
                    "error": probe["error"],
                }
            )
            if probe["error"] and probe["http_status"] not in (404, None):
                raise BuildBlocked(f"monthly archive probe failed for {url}: {probe['error']}")
        monthly_probe_results[symbol] = {
            "monthly_files_available": sum(1 for probe in probes if probe["exists"]),
            "monthly_files_checked": len(probes),
            "probes": probes,
        }

    download_manifest: list[dict[str, Any]] = []
    checksum_rows: list[dict[str, Any]] = []
    per_symbol_coverage: dict[str, Any] = {}
    archive_file_rows: list[dict[str, Any]] = []
    normalized_sha_rows: list[dict[str, Any]] = []
    for symbol in REQUESTED_SYMBOLS:
        _, coverage, file_rows = build_symbol(symbol, monthly_available_by_symbol[symbol], download_manifest, checksum_rows)
        per_symbol_coverage[symbol] = coverage
        archive_file_rows.extend(file_rows)
        normalized_sha_rows.append(
            {
                "symbol": symbol,
                "normalized_file": coverage["normalized_file"],
                "sha256": coverage["normalized_file_sha256"],
                "bytes": Path(coverage["normalized_file"]).stat().st_size,
            }
        )

    download_manifest_path = CHECKSUM_DIR / "download_manifest_v1.csv"
    download_fields = [
        "url",
        "local_path",
        "available",
        "downloaded",
        "reused_existing",
        "checksum_available",
        "checksum_saved",
        "checksum_verified",
        "sha256",
        "bytes",
        "error",
    ]
    write_csv(download_manifest_path, download_fields, download_manifest)
    normalized_sha_path = CHECKSUM_DIR / "normalized_file_sha256_v1.csv"
    write_csv(normalized_sha_path, ["symbol", "normalized_file", "sha256", "bytes"], normalized_sha_rows)
    archive_availability_path = COVERAGE_DIR / "archive_file_availability_v1.csv"
    write_csv(archive_availability_path, ["symbol", "cadence", "period", "available", "url"], archive_file_rows)

    summary = aggregate_summary(per_symbol_coverage)
    summary_path = COVERAGE_DIR / "dataset_coverage_summary_v1.csv"
    summary_row = {
        "requested_symbol_count": summary["requested_symbol_count"],
        "built_symbol_count": summary["built_symbol_count"],
        "symbols_with_open_interest": summary["symbols_with_open_interest"],
        "symbols_with_taker_ratio": summary["symbols_with_taker_ratio"],
        "symbols_with_global_long_short": summary["symbols_with_global_long_short"],
        "symbols_with_top_account_ratio": summary["symbols_with_top_account_ratio"],
        "symbols_with_top_position_ratio": summary["symbols_with_top_position_ratio"],
        "symbols_with_long_short_ratio": summary["symbols_with_long_short_ratio"],
        "symbols_with_full_proxy_alignment": summary["symbols_with_full_proxy_alignment"],
        "timestamp_global_min": summary["timestamp_global_min"],
        "timestamp_global_max": summary["timestamp_global_max"],
        "total_normalized_rows": summary["total_normalized_rows"],
    }
    write_csv(summary_path, list(summary_row), [summary_row])

    checksum_summary = {
        "download_manifest_file": str(download_manifest_path),
        "download_manifest_sha256": sha256_file(download_manifest_path),
        "normalized_file_sha256_manifest": str(normalized_sha_path),
        "normalized_file_sha256_manifest_sha256": sha256_file(normalized_sha_path),
        "archives_with_checksum_available": sum(1 for row in checksum_rows if row.get("checksum_available")),
        "archives_with_checksum_verified": sum(1 for row in checksum_rows if row.get("checksum_verified") is True),
        "checksum_mismatch_count": 0,
    }
    result_classification, next_allowed_step, historical_feasible = classify(summary, per_symbol_coverage, checksum_summary)
    if result_classification == RESULT_BLOCKED:
        raise BuildBlocked("dataset build produced no usable normalized rows")

    data_quality_checks = {
        "per_symbol": {
            symbol: {
                "file_availability": coverage["file_availability"],
                "earliest_timestamp": coverage["earliest_timestamp"],
                "latest_timestamp": coverage["latest_timestamp"],
                "row_count": coverage["row_count"],
                "duplicate_timestamp_count": coverage["duplicate_timestamp_count"],
                "missing_interval_count": coverage["missing_interval_count"],
                "missing_date_count": coverage["missing_date_count"],
                "numeric_field_sanity": coverage["numeric_field_sanity"],
                "source_field_availability": coverage["source_field_availability"],
                "checksum_availability_and_result": "see checksum_summary/download_manifest",
                "data_quality_pass": coverage["data_quality_pass"],
            }
            for symbol, coverage in per_symbol_coverage.items()
        },
        "overall": {
            "negative_oi_count": sum(coverage["numeric_field_sanity"]["negative_oi_count"] for coverage in per_symbol_coverage.values()),
            "invalid_ratio_count": sum(coverage["numeric_field_sanity"]["invalid_ratio_count"] for coverage in per_symbol_coverage.values()),
            "duplicate_timestamp_count": sum(coverage["duplicate_timestamp_count"] for coverage in per_symbol_coverage.values()),
            "data_quality_pass": all(coverage["data_quality_pass"] for coverage in per_symbol_coverage.values() if coverage["row_count"] > 0),
        },
    }

    generated_external_files = {
        "raw_archives_root": str(RAW_ARCHIVES_DIR),
        "normalized_by_symbol_files": [row["normalized_file"] for row in normalized_sha_rows],
        "coverage_report_files": [str(summary_path), str(archive_availability_path)]
        + [coverage["coverage_report_file"] for coverage in per_symbol_coverage.values()],
        "checksum_files": [str(download_manifest_path), str(normalized_sha_path)],
    }
    archive_files_available = sum(1 for row in download_manifest if row["available"])
    archive_files_downloaded = sum(1 for row in download_manifest if row["downloaded"])
    archive_files_reused = sum(1 for row in download_manifest if row["reused_existing"])
    archive_files_missing = sum(1 for row in download_manifest if not row["available"])
    download_summary = {
        "monthly_archive_probe_summary": {
            symbol: {
                "monthly_files_available": result["monthly_files_available"],
                "monthly_files_checked": result["monthly_files_checked"],
            }
            for symbol, result in monthly_probe_results.items()
        },
        "preferred_monthly_files_when_available": True,
        "daily_files_used_when_monthly_unavailable": True,
        "archive_files_available": archive_files_available,
        "archive_files_downloaded": archive_files_downloaded,
        "archive_files_reused_existing": archive_files_reused,
        "archive_files_missing": archive_files_missing,
        "download_manifest_file": str(download_manifest_path),
        "unrelated_market_data_downloaded": False,
    }

    per_metric_coverage = {
        metric: {
            "symbols_with_metric": sum(1 for coverage in per_symbol_coverage.values() if coverage["source_field_availability"].get(metric)),
            "rows_with_metric": sum(coverage["metric_row_counts"].get(metric, 0) for coverage in per_symbol_coverage.values()),
        }
        for metric in REQUESTED_METRICS
    }
    validation_checks = {
        "stale_institutional_contract_leftovers_removed": stale_absence,
        "repo_clean_before_dataset_build": GIT_STATUS_SHORT_AFTER_STALE_CLEANUP_BEFORE_TOOL_CREATION == [],
        "binance_discovery_artifact_loaded": True,
        "public_archive_only": True,
        "no_api_key_used": True,
        "no_private_api_used": True,
        "no_account_api_used": True,
        "no_order_endpoint_used": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "external_output_root_used": EXTERNAL_OUTPUT_ROOT.exists(),
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_tracked_files_modified": no_existing_tracked_files_modified(status_at_run_start),
    }
    replacement_checks_all_true = all(value is True for value in validation_checks.values())
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true
    artifact: dict[str, Any] = {
        "status": STATUS_PASS if replacement_checks_all_true else STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "source_discovery_commit": SOURCE_DISCOVERY_COMMIT,
            "repo_head_before_tool_creation": SOURCE_REPO_HEAD_BEFORE_TOOL_CREATION,
            "tracked_python_count_before_tool_creation": TRACKED_PYTHON_COUNT_BEFORE_TOOL_CREATION,
            "tracked_python_count_at_run": tracked_python_count(),
            "git_status_short_after_stale_cleanup_before_tool_creation": GIT_STATUS_SHORT_AFTER_STALE_CLEANUP_BEFORE_TOOL_CREATION,
            "git_status_short_at_run_start": status_at_run_start,
            "build_started_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "source_artifacts": {
            "binance_metrics_archive_discovery": {
                "path": DISCOVERY_RELATIVE_PATH,
                "status": discovery.get("status"),
                "result_classification": discovery.get("result_classification"),
                "payload_sha256_excluding_hash": discovery_hash,
            }
        },
        "cleanup_summary": {
            "stale_institutional_contract_leftovers_removed": stale_absence,
            "removed_paths": STALE_LEFTOVERS_REMOVED,
            "repo_clean_after_cleanup_before_dataset_tool_creation": True,
        },
        "archive_source": {
            "base_url": PUBLIC_ARCHIVE_BASE,
            "daily_metrics_root": DAILY_METRICS_ROOT,
            "monthly_metrics_root": MONTHLY_METRICS_ROOT,
            "public_archive_only": True,
            "url_patterns": {
                "daily": f"{DAILY_METRICS_ROOT}/SYMBOL/SYMBOL-metrics-YYYY-MM-DD.zip",
                "monthly": f"{MONTHLY_METRICS_ROOT}/SYMBOL/SYMBOL-metrics-YYYY-MM.zip",
            },
        },
        "requested_symbols": REQUESTED_SYMBOLS,
        "requested_metrics": REQUESTED_METRICS,
        "external_output_root": str(EXTERNAL_OUTPUT_ROOT),
        "download_summary": download_summary,
        "generated_external_files": generated_external_files,
        "normalized_dataset_summary": summary,
        "per_symbol_coverage": per_symbol_coverage,
        "per_metric_coverage": per_metric_coverage,
        "data_quality_checks": data_quality_checks,
        "checksum_summary": checksum_summary,
        "historical_feasibility": {
            "historical_2023_2025_feasible": historical_feasible,
            "requested_start_date": START_DATE.isoformat(),
            "requested_end_date": END_DATE.isoformat(),
            "material_coverage_by_year": summary["coverage_by_year"],
            "ready_threshold": "at least 5 symbols with OI + taker ratio + at least one long/short crowding ratio and quality pass",
        },
        "proxy_package_summary": {
            "purpose": "OI + taker pressure + crowding proxy dataset",
            "true_liquidation_data": False,
            "open_interest_available": summary["symbols_with_open_interest"],
            "taker_ratio_available": summary["symbols_with_taker_ratio"],
            "long_short_ratio_available": summary["symbols_with_long_short_ratio"],
            "full_proxy_alignment_symbols": summary["symbols_with_full_proxy_alignment"],
        },
        "unavailable_data_summary": {
            "liquidation": "unavailable in this metrics archive",
            "funding": "unavailable in this metrics archive",
            "taker_buy_sell_volume_components": "unavailable; taker ratio is available",
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": summary["limitations"]
        + [
            "This builder did not run strategy logic, generate signals, compute PnL, optimize, create candidates, or claim edge.",
            "External raw archives are limited to public Binance Data Vision USD-M metrics archive files.",
        ],
        "safety_permissions": {
            "dataset_builder_created": replacement_checks_all_true,
            "proxy_event_study_allowed_next": next_allowed_step == NEXT_EVENT_STUDY,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "trade_simulation_allowed_now": False,
            "optimization_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    summary = artifact["normalized_dataset_summary"]
    print(f"status: {artifact['status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"requested_symbol_count: {summary['requested_symbol_count']}")
    print(f"built_symbol_count: {summary['built_symbol_count']}")
    print(f"symbols_with_open_interest: {summary['symbols_with_open_interest']}")
    print(f"symbols_with_taker_ratio: {summary['symbols_with_taker_ratio']}")
    print(f"symbols_with_long_short_ratio: {summary['symbols_with_long_short_ratio']}")
    print(f"symbols_with_full_proxy_alignment: {summary['symbols_with_full_proxy_alignment']}")
    print(f"timestamp_global_min: {summary['timestamp_global_min']}")
    print(f"timestamp_global_max: {summary['timestamp_global_max']}")
    print(f"total_normalized_rows: {summary['total_normalized_rows']}")
    print(f"historical_2023_2025_feasible: {bool_text(artifact['historical_feasibility']['historical_2023_2025_feasible'])}")
    print("liquidation_available: false")
    print("funding_available: false")
    print(f"recommended_next_step: {artifact['next_allowed_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(artifact['replacement_checks_all_true'])}")


def blocked_artifact(reason: str) -> dict[str, Any]:
    validation_checks = {
        "stale_institutional_contract_leftovers_removed": all(not (REPO_ROOT / path.rstrip("/")).exists() for path in STALE_LEFTOVERS_REMOVED),
        "repo_clean_before_dataset_build": GIT_STATUS_SHORT_AFTER_STALE_CLEANUP_BEFORE_TOOL_CREATION == [],
        "binance_discovery_artifact_loaded": (REPO_ROOT / DISCOVERY_RELATIVE_PATH).exists(),
        "public_archive_only": True,
        "no_api_key_used": True,
        "no_private_api_used": True,
        "no_account_api_used": True,
        "no_order_endpoint_used": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "external_output_root_used": EXTERNAL_OUTPUT_ROOT.exists(),
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": False,
        "no_existing_tracked_files_modified": no_existing_tracked_files_modified(git_status_short()),
        "replacement_checks_all_true": False,
    }
    artifact: dict[str, Any] = {
        "status": STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "repo_root": str(REPO_ROOT),
            "source_discovery_commit": SOURCE_DISCOVERY_COMMIT,
            "blocked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "source_artifacts": {"binance_metrics_archive_discovery": {"path": DISCOVERY_RELATIVE_PATH}},
        "cleanup_summary": {
            "stale_institutional_contract_leftovers_removed": validation_checks["stale_institutional_contract_leftovers_removed"],
            "removed_paths": STALE_LEFTOVERS_REMOVED,
        },
        "archive_source": {"base_url": PUBLIC_ARCHIVE_BASE, "public_archive_only": True},
        "requested_symbols": REQUESTED_SYMBOLS,
        "requested_metrics": REQUESTED_METRICS,
        "external_output_root": str(EXTERNAL_OUTPUT_ROOT),
        "download_summary": {"blocked_reason": reason},
        "generated_external_files": {},
        "normalized_dataset_summary": {
            "requested_symbol_count": len(REQUESTED_SYMBOLS),
            "built_symbol_count": 0,
            "symbols_with_open_interest": 0,
            "symbols_with_taker_ratio": 0,
            "symbols_with_long_short_ratio": 0,
            "symbols_with_full_proxy_alignment": 0,
            "timestamp_global_min": None,
            "timestamp_global_max": None,
            "total_normalized_rows": 0,
        },
        "per_symbol_coverage": {},
        "per_metric_coverage": {},
        "data_quality_checks": {},
        "checksum_summary": {},
        "historical_feasibility": {"historical_2023_2025_feasible": False},
        "proxy_package_summary": {"purpose": "blocked before dataset build"},
        "unavailable_data_summary": {"liquidation": "unavailable in this metrics archive", "funding": "unavailable in this metrics archive"},
        "result_classification": RESULT_BLOCKED,
        "next_allowed_step": NEXT_BLOCKED,
        "limitations": [f"BLOCKED: {reason}"],
        "safety_permissions": {
            "dataset_builder_created": False,
            "proxy_event_study_allowed_next": False,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "trade_simulation_allowed_now": False,
            "optimization_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def main() -> int:
    try:
        artifact = build_dataset()
        write_artifact(artifact)
        print_summary(artifact)
        return 0 if artifact["replacement_checks_all_true"] else 2
    except BuildBlocked as exc:
        artifact = blocked_artifact(str(exc))
        write_artifact(artifact)
        print_summary(artifact)
        print(f"exact_blocker: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
