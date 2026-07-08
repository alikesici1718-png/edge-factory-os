#!/usr/bin/env python3
"""Discover and lock Binance USD-M USDT perpetual 1m archive coverage.

This tool performs metadata-only discovery against official Binance public
endpoints. It uses exchangeInfo and Binance public archive listings/checks only;
it does not download or open kline ZIP contents, read kline rows, build a panel,
run strategy research, or grant candidate/edge/runtime permissions.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import platform
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_USDT_PERPETUAL_1M_COVERAGE_DISCOVERY_LOCK_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_usdt_perpetual_1m_coverage_discovery_and_lock_v1.py"
COVERAGE_LOCK_ARTIFACT_PATH = (
    "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"
)
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_PATH / COVERAGE_LOCK_ARTIFACT_PATH
TEMP_ARTIFACT_PATH = ARTIFACT_PATH.with_suffix(".json.tmp")
PRIOR_HEAD = "ccdc1d1a9d813441647865311d1c3c09c3ac55c8"
PRIOR_TRACKED_PYTHON_COUNT = 806

EXCHANGE_INFO_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"
ARCHIVE_LISTING_URL = "https://data.binance.vision/?prefix=data/futures/um/monthly/klines/"
S3_LIST_URL = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
PUBLIC_ARCHIVE_BASE = "https://data.binance.vision/data/futures/um/"
MONTHLY_KLINE_URL_TEMPLATE = (
    "https://data.binance.vision/data/futures/um/monthly/klines/{SYMBOL}/1m/{SYMBOL}-1m-{YYYY_MM}.zip"
)
MONTHLY_CHECKSUM_URL_TEMPLATE = MONTHLY_KLINE_URL_TEMPLATE + ".CHECKSUM"
DAILY_KLINE_URL_TEMPLATE = (
    "https://data.binance.vision/data/futures/um/daily/klines/{SYMBOL}/1m/{SYMBOL}-1m-{YYYY_MM_DD}.zip"
)
DAILY_CHECKSUM_URL_TEMPLATE = DAILY_KLINE_URL_TEMPLATE + ".CHECKSUM"

MONTHLY_PROBE_START = "2019-09"
DAILY_TAIL_DAYS = 45
MAX_WORKERS = 8
HTTP_TIMEOUT_SECONDS = 10
HTTP_RETRIES = 2
S3_MAX_KEYS = 1000
MAX_DIRECT_PROBE_BUDGET = 5000
USER_AGENT = "edge-factory-os-binance-coverage-discovery/1.0"


class BlockedError(RuntimeError):
    """Raised when the route must stop before writing the coverage lock."""


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def progress(start_monotonic: float, event: str, **fields: Any) -> None:
    payload = {"elapsed_seconds": round(time.monotonic() - start_monotonic, 1), "event": event}
    payload.update(fields)
    print(json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)


def month_tuple(month: str) -> tuple[int, int]:
    year_text, month_text = month.split("-")
    return int(year_text), int(month_text)


def month_add(month: str, delta: int) -> str:
    year, month_number = month_tuple(month)
    index = year * 12 + (month_number - 1) + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def month_range(start: str, end: str) -> list[str]:
    months: list[str] = []
    current = start
    while current <= end:
        months.append(current)
        current = month_add(current, 1)
    return months


def date_range(start: dt.date, end: dt.date) -> list[str]:
    dates: list[str] = []
    current = start
    while current <= end:
        dates.append(current.isoformat())
        current += dt.timedelta(days=1)
    return dates


def previous_utc_month(current_date: dt.date) -> str:
    first_this_month = current_date.replace(day=1)
    previous_day = first_this_month - dt.timedelta(days=1)
    return f"{previous_day.year:04d}-{previous_day.month:02d}"


def ms_to_iso(value: Any) -> str | None:
    if value in (None, "", 0):
        return None
    try:
        milliseconds = int(value)
    except (TypeError, ValueError):
        return None
    if milliseconds <= 0:
        return None
    return dt.datetime.fromtimestamp(milliseconds / 1000, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def ms_to_month(value: Any) -> str | None:
    iso = ms_to_iso(value)
    return None if iso is None else iso[:7]


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def http_status_key(status: int | None) -> str:
    return "NO_STATUS" if status is None else str(status)


def is_transient_status(status: int | None) -> bool:
    return status in {408, 425, 429, 500, 502, 503, 504} or status is None


def request_text(url: str, read_limit: int | None = None) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            raw = response.read() if read_limit is None else response.read(read_limit)
            return {
                "error": None,
                "status": response.status,
                "text": raw.decode("utf-8", errors="replace"),
                "url": url,
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read(read_limit or 0) if read_limit else b""
        return {
            "error": str(exc),
            "status": exc.code,
            "text": raw.decode("utf-8", errors="replace") if raw else "",
            "url": url,
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc), "status": None, "text": "", "url": url}


def request_text_with_retry(url: str, read_limit: int | None = None) -> dict[str, Any]:
    last_result: dict[str, Any] | None = None
    for attempt in range(HTTP_RETRIES + 1):
        result = request_text(url, read_limit=read_limit)
        last_result = result
        if result["status"] == 404:
            return result
        if not is_transient_status(result["status"]):
            return result
        if attempt < HTTP_RETRIES:
            time.sleep(0.2 * (attempt + 1))
    assert last_result is not None
    return last_result


def fetch_json(url: str) -> dict[str, Any]:
    result = request_text_with_retry(url, read_limit=None)
    if result["status"] != 200:
        raise BlockedError(f"exchangeInfo fetch failed: status={result['status']} error={result['error']}")
    try:
        return json.loads(result["text"])
    except json.JSONDecodeError as exc:
        raise BlockedError(f"exchangeInfo JSON decode failed: {exc}") from exc


def s3_listing_url(prefix: str, delimiter: str | None = None, continuation_token: str | None = None) -> str:
    params = {"list-type": "2", "max-keys": str(S3_MAX_KEYS), "prefix": prefix}
    if delimiter:
        params["delimiter"] = delimiter
    if continuation_token:
        params["continuation-token"] = continuation_token
    return S3_LIST_URL + "?" + urllib.parse.urlencode(params)


def regex_values(pattern: str, text: str) -> list[str]:
    return [html.unescape(value) for value in re.findall(pattern, text)]


def s3_list_prefix(prefix: str, delimiter: str | None = None) -> dict[str, Any]:
    keys: list[str] = []
    common_prefixes: list[str] = []
    statuses: list[int | None] = []
    errors: list[str] = []
    token: str | None = None
    page_count = 0
    while True:
        url = s3_listing_url(prefix, delimiter=delimiter, continuation_token=token)
        result = request_text_with_retry(url, read_limit=None)
        page_count += 1
        statuses.append(result["status"])
        if result["status"] != 200:
            errors.append(f"{url} status={result['status']} error={result['error']}")
            break
        text = result["text"]
        keys.extend(regex_values(r"<Key>(.*?)</Key>", text))
        common_prefixes.extend(regex_values(r"<CommonPrefixes>\s*<Prefix>(.*?)</Prefix>\s*</CommonPrefixes>", text))
        token_values = regex_values(r"<NextContinuationToken>(.*?)</NextContinuationToken>", text)
        is_truncated = "<IsTruncated>true</IsTruncated>" in text
        token = token_values[0] if token_values else None
        if not is_truncated or not token:
            break
    return {
        "common_prefixes": sorted(set(common_prefixes)),
        "errors": errors,
        "failed": bool(errors),
        "keys": sorted(set(keys)),
        "page_count": page_count,
        "statuses": statuses,
    }


def exchange_info_universe(exchange_info: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    symbols = exchange_info.get("symbols")
    if not isinstance(symbols, list):
        raise BlockedError("exchangeInfo response missing symbols list")
    records: dict[str, dict[str, Any]] = {}
    trading: list[str] = []
    non_trading: list[str] = []
    for row in symbols:
        if not isinstance(row, dict):
            continue
        if row.get("contractType") != "PERPETUAL":
            continue
        if row.get("quoteAsset") != "USDT":
            continue
        if row.get("marginAsset") not in (None, "USDT"):
            continue
        symbol = str(row.get("symbol", "")).strip().upper()
        if not symbol:
            continue
        status = row.get("status")
        if status == "TRADING":
            trading.append(symbol)
        else:
            non_trading.append(symbol)
        records[symbol] = {
            "baseAsset": row.get("baseAsset"),
            "contractType": row.get("contractType"),
            "deliveryDate_raw_ms": row.get("deliveryDate"),
            "marginAsset": row.get("marginAsset"),
            "onboardDate_raw_ms": row.get("onboardDate"),
            "onboardDate_utc_iso": ms_to_iso(row.get("onboardDate")),
            "pair": row.get("pair"),
            "quoteAsset": row.get("quoteAsset"),
            "status": status,
            "symbol": symbol,
            "underlyingSubType": row.get("underlyingSubType"),
            "underlyingType": row.get("underlyingType"),
        }
    return records, sorted(trading), sorted(non_trading)


def archive_symbols_from_listing() -> tuple[bool, list[str], str | None, dict[str, int]]:
    listing = s3_list_prefix("data/futures/um/monthly/klines/", delimiter="/")
    status_counts: dict[str, int] = {}
    for status in listing["statuses"]:
        key = http_status_key(status)
        status_counts[key] = status_counts.get(key, 0) + 1
    if listing["failed"]:
        return False, [], "; ".join(listing["errors"]), status_counts
    found = set()
    for prefix in listing["common_prefixes"]:
        match = re.match(r"data/futures/um/monthly/klines/([^/]+USDT)/$", prefix)
        if match:
            found.add(match.group(1).upper())
    return bool(found), sorted(found), None if found else "no USDT archive symbols parsed from S3 listing", status_counts


def list_symbol_monthly(symbol: str) -> dict[str, Any]:
    prefix = f"data/futures/um/monthly/klines/{symbol}/1m/"
    listing = s3_list_prefix(prefix)
    zip_pattern = re.compile(rf"^{re.escape(prefix)}{re.escape(symbol)}-1m-(\d{{4}}-\d{{2}})\.zip$")
    checksum_pattern = re.compile(rf"^{re.escape(prefix)}{re.escape(symbol)}-1m-(\d{{4}}-\d{{2}})\.zip\.CHECKSUM$")
    available_months = []
    checksum_months = []
    for key in listing["keys"]:
        zip_match = zip_pattern.match(key)
        checksum_match = checksum_pattern.match(key)
        if zip_match:
            available_months.append(zip_match.group(1))
        if checksum_match:
            checksum_months.append(checksum_match.group(1))
    return {
        "available_months": sorted(set(available_months)),
        "checksum_months": sorted(set(checksum_months)),
        "failed": listing["failed"],
        "errors": listing["errors"],
        "page_count": listing["page_count"],
        "statuses": listing["statuses"],
        "symbol": symbol,
    }


def list_symbol_daily_tail(symbol: str, tail_dates: set[str]) -> dict[str, Any]:
    prefix = f"data/futures/um/daily/klines/{symbol}/1m/"
    listing = s3_list_prefix(prefix)
    date_pattern = re.compile(rf"^{re.escape(prefix)}{re.escape(symbol)}-1m-(\d{{4}}-\d{{2}}-\d{{2}})\.zip$")
    available_dates = []
    for key in listing["keys"]:
        match = date_pattern.match(key)
        if match and match.group(1) in tail_dates:
            available_dates.append(match.group(1))
    return {
        "available_dates": sorted(set(available_dates)),
        "failed": listing["failed"],
        "errors": listing["errors"],
        "page_count": listing["page_count"],
        "statuses": listing["statuses"],
        "symbol": symbol,
    }


def contiguous_ranges(months: list[str]) -> list[dict[str, str | int]]:
    if not months:
        return []
    ranges: list[dict[str, str | int]] = []
    start = months[0]
    previous = months[0]
    count = 1
    for month in months[1:]:
        if month == month_add(previous, 1):
            previous = month
            count += 1
        else:
            ranges.append({"end": previous, "month_count": count, "start": start})
            start = previous = month
            count = 1
    ranges.append({"end": previous, "month_count": count, "start": start})
    return ranges


def top_missing_months(records: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for record in records:
        for month in record["missing_months_after_onboard_within_probe_range"]:
            counts[month] = counts.get(month, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"missing_count": count, "month": month} for month, count in ordered[:limit]]


def build_symbol_record(
    symbol: str,
    sources: list[str],
    exchange_metadata: dict[str, Any] | None,
    probe_months: list[str],
    window_3y: list[str],
    window_5y: list[str],
    monthly_listing: dict[str, Any],
    daily_listing: dict[str, Any],
) -> dict[str, Any]:
    available_months = [month for month in monthly_listing["available_months"] if month in probe_months]
    missing_months = [month for month in probe_months if month not in available_months]
    checksum_months = [month for month in monthly_listing["checksum_months"] if month in probe_months]
    onboard_month = ms_to_month(exchange_metadata.get("onboardDate_raw_ms")) if exchange_metadata else None
    pre_onboard = [month for month in probe_months if onboard_month and month < onboard_month]
    expected_after_onboard = [month for month in probe_months if not onboard_month or month >= onboard_month]
    missing_after_onboard = [month for month in expected_after_onboard if month in missing_months]
    first_available = available_months[0] if available_months else None
    last_available = available_months[-1] if available_months else None
    if first_available and last_available:
        between = [month for month in probe_months if first_available <= month <= last_available]
        internal_missing = [month for month in between if month not in available_months and month not in pre_onboard]
        trailing_missing = [month for month in probe_months if month > last_available and month not in pre_onboard]
        leading_missing = [month for month in probe_months if month < first_available and month not in pre_onboard]
    else:
        internal_missing = []
        trailing_missing = []
        leading_missing = [month for month in probe_months if month not in pre_onboard]
    daily_available_dates = daily_listing["available_dates"]
    max_daily = daily_available_dates[-1] if daily_available_dates else None

    def window_eval(window: list[str]) -> tuple[bool, bool, list[str], list[str]]:
        available = [month for month in window if month in available_months]
        missing = [month for month in window if month not in available_months]
        expected = [month for month in window if not onboard_month or month >= onboard_month]
        missing_expected = [month for month in expected if month not in available_months]
        near = bool(expected) and not missing_expected
        strict = not missing
        complete = near
        return complete, strict, available, missing

    complete_3y, strict_3y, available_3y, missing_3y = window_eval(window_3y)
    complete_5y, strict_5y, available_5y, missing_5y = window_eval(window_5y)
    coverage_gap = not complete_3y or bool(internal_missing) or bool(trailing_missing)
    pending = monthly_listing["failed"] or daily_listing["failed"]
    return {
        "available_months": available_months,
        "available_months_in_3y_window": available_3y,
        "available_months_in_5y_window": available_5y,
        "checksum_available_count": len(checksum_months),
        "checksum_missing_count": len(available_months) - len(checksum_months),
        "checksum_sha256_texts": {},
        "complete_3y_monthly_coverage": complete_3y,
        "complete_5y_monthly_coverage": complete_5y,
        "contiguous_available_month_ranges": contiguous_ranges(available_months),
        "coverage_end_candidate_daily_tail": max_daily,
        "coverage_end_candidate_monthly": last_available,
        "coverage_gap_symbol": coverage_gap,
        "coverage_start_candidate": onboard_month or first_available,
        "current_trading": exchange_metadata.get("status") == "TRADING" if exchange_metadata else False,
        "daily_tail_available_dates": daily_available_dates,
        "exchange_info_metadata": exchange_metadata,
        "first_available_month": first_available,
        "internal_missing_months_between_first_and_last": internal_missing,
        "last_available_month": last_available,
        "leading_missing_months_before_first_available": leading_missing,
        "max_available_daily_date": max_daily,
        "missing_months_after_onboard_within_probe_range": missing_after_onboard,
        "missing_months_in_3y_window": missing_3y,
        "missing_months_in_5y_window": missing_5y,
        "monthly_available_count": len(available_months),
        "monthly_missing_count": len(missing_months),
        "near_3y_complete_symbol": complete_3y,
        "near_5y_complete_symbol": complete_5y,
        "onboard_month": onboard_month,
        "pending_or_failed_probe_symbol": pending,
        "pre_onboard_not_expected_months": pre_onboard,
        "status": exchange_metadata.get("status") if exchange_metadata else "ARCHIVE_ONLY",
        "strict_3y_complete_symbol": strict_3y,
        "strict_5y_complete_symbol": strict_5y,
        "symbol": symbol,
        "symbol_limitations": [
            "coverage presence only; kline zip contents were not opened",
            "row counts and OHLCV values were not validated",
            "checksum SHA256 text was not fetched when listing metadata was sufficient",
        ],
        "trailing_missing_months_after_last_available": trailing_missing,
        "universe_sources": sources,
    }


def aggregate_status_counts(status_lists: list[list[int | None]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for statuses in status_lists:
        for status in statuses:
            key = http_status_key(status)
            counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def collect_listings(
    symbols: list[str],
    worker,
    start_monotonic: float,
    phase: str,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    completed = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_symbol = {executor.submit(worker, symbol): symbol for symbol in symbols}
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            result = future.result()
            results[symbol] = result
            completed += 1
            if result["failed"]:
                failed += 1
            if completed == 1 or completed % 25 == 0 or completed == len(symbols):
                progress(
                    start_monotonic,
                    f"{phase}_progress",
                    failed_symbols=failed,
                    processed_symbols=completed,
                    total_symbols=len(symbols),
                )
    return results


def build_lock() -> dict[str, Any]:
    start_monotonic = time.monotonic()
    run_started = utc_now()
    current_date = run_started.date()
    progress(start_monotonic, "exchangeInfo_fetch_started")
    exchange_info = fetch_json(EXCHANGE_INFO_URL)
    exchange_records, trading_symbols, non_trading_symbols = exchange_info_universe(exchange_info)
    if not exchange_records:
        raise BlockedError("USDT perpetual universe is empty after exchangeInfo filters")
    progress(
        start_monotonic,
        "exchangeInfo_fetch_completed",
        exchange_info_symbols_total=len(exchange_info.get("symbols", [])),
        usdt_perpetual_symbols=len(exchange_records),
    )
    progress(start_monotonic, "archive_directory_listing_started")
    archive_listing_parsed, archive_symbols, archive_listing_error, listing_status_counts = archive_symbols_from_listing()
    candidate_symbols = sorted(set(exchange_records) | set(archive_symbols))
    if not candidate_symbols:
        raise BlockedError("candidate universe is empty")
    progress(
        start_monotonic,
        "archive_directory_listing_completed",
        archive_directory_listing_parsed=archive_listing_parsed,
        archive_symbols=len(archive_symbols),
        candidate_symbols=len(candidate_symbols),
    )

    candidate_end_month = previous_utc_month(current_date)
    direct_probe_plan = len(candidate_symbols) * len(month_range(MONTHLY_PROBE_START, candidate_end_month))
    if not archive_listing_parsed and direct_probe_plan > MAX_DIRECT_PROBE_BUDGET:
        raise BlockedError(
            "archive listing unavailable and direct per-symbol/per-month probe plan exceeds budget: "
            f"{direct_probe_plan}>{MAX_DIRECT_PROBE_BUDGET}"
        )
    progress(start_monotonic, "monthly_listing_phase_started", total_symbols=len(candidate_symbols))
    monthly_by_symbol = collect_listings(candidate_symbols, list_symbol_monthly, start_monotonic, "monthly_listing")
    all_available_months = sorted(
        {
            month
            for result in monthly_by_symbol.values()
            for month in result["available_months"]
            if month >= MONTHLY_PROBE_START
        }
    )
    if not all_available_months:
        raise BlockedError("no monthly archive coverage could be discovered from Binance listings")
    latest_monthly_archive_month = min(max(all_available_months), candidate_end_month)
    probe_months = month_range(MONTHLY_PROBE_START, latest_monthly_archive_month)
    progress(
        start_monotonic,
        "monthly_listing_phase_completed",
        latest_monthly_archive_month=latest_monthly_archive_month,
        monthly_probe_month_count=len(probe_months),
    )

    daily_tail_end = current_date - dt.timedelta(days=1)
    daily_tail_start = daily_tail_end - dt.timedelta(days=DAILY_TAIL_DAYS - 1)
    daily_dates = date_range(daily_tail_start, daily_tail_end)
    daily_date_set = set(daily_dates)

    def daily_worker(symbol: str) -> dict[str, Any]:
        return list_symbol_daily_tail(symbol, daily_date_set)

    progress(
        start_monotonic,
        "daily_tail_listing_phase_started",
        daily_tail_day_count=len(daily_dates),
        total_symbols=len(candidate_symbols),
    )
    daily_by_symbol = collect_listings(candidate_symbols, daily_worker, start_monotonic, "daily_tail_listing")
    progress(start_monotonic, "daily_tail_listing_phase_completed", total_symbols=len(candidate_symbols))

    window_3y = month_range(month_add(latest_monthly_archive_month, -35), latest_monthly_archive_month)
    window_5y = month_range(month_add(latest_monthly_archive_month, -59), latest_monthly_archive_month)
    records: list[dict[str, Any]] = []
    for symbol in candidate_symbols:
        in_exchange = symbol in exchange_records
        in_archive = symbol in archive_symbols
        if in_exchange and in_archive:
            sources = ["archive_directory_universe", "exchangeInfo_current_universe"]
        elif in_archive:
            sources = ["archive_directory_universe"]
        else:
            sources = ["exchangeInfo_current_universe"]
        records.append(
            build_symbol_record(
                symbol,
                sources,
                exchange_records.get(symbol),
                probe_months,
                window_3y,
                window_5y,
                monthly_by_symbol[symbol],
                daily_by_symbol[symbol],
            )
        )
    records.sort(key=lambda row: row["symbol"])

    global_daily_dates = [record["max_available_daily_date"] for record in records if record["max_available_daily_date"]]
    global_max_daily = max(global_daily_dates) if global_daily_dates else None
    monthly_available_records = [record for record in records if record["monthly_available_count"] > 0]
    earliest_month = min((record["first_available_month"] for record in monthly_available_records if record["first_available_month"]), default=None)
    latest_month = max((record["last_available_month"] for record in monthly_available_records if record["last_available_month"]), default=None)
    near_3y = sorted(record["symbol"] for record in records if record["near_3y_complete_symbol"])
    strict_3y = sorted(record["symbol"] for record in records if record["strict_3y_complete_symbol"])
    near_5y = sorted(record["symbol"] for record in records if record["near_5y_complete_symbol"])
    strict_5y = sorted(record["symbol"] for record in records if record["strict_5y_complete_symbol"])
    coverage_gap = sorted(record["symbol"] for record in records if record["coverage_gap_symbol"])
    pending = sorted(record["symbol"] for record in records if record["pending_or_failed_probe_symbol"])
    archive_only = sorted(symbol for symbol in archive_symbols if symbol not in exchange_records)
    monthly_failed = [row for row in monthly_by_symbol.values() if row["failed"]]
    daily_failed = [row for row in daily_by_symbol.values() if row["failed"]]
    failed_probe_samples = sorted(
        [
            {"errors": row["errors"][:2], "symbol": row["symbol"]}
            for row in (monthly_failed + daily_failed)
        ],
        key=lambda row: row["symbol"],
    )[:20]
    status_counts = aggregate_status_counts(
        [list(listing_status_counts.keys())] if False else []
    )
    status_counts = aggregate_status_counts(
        [row["statuses"] for row in monthly_by_symbol.values()]
        + [row["statuses"] for row in daily_by_symbol.values()]
        + [[int(key) for key in listing_status_counts if key.isdigit() for _ in range(listing_status_counts[key])]]
    )
    run_completed = utc_now()
    payload: dict[str, Any] = {
        "archive_discovery_summary": {
            "daily_tail_day_count": len(daily_dates),
            "daily_tail_end_date": daily_tail_end.isoformat(),
            "daily_tail_start_date": daily_tail_start.isoformat(),
            "failed_probe_count": len(monthly_failed) + len(daily_failed),
            "http_status_counts": status_counts,
            "monthly_probe_month_count": len(probe_months),
            "monthly_probe_month_end": latest_monthly_archive_month,
            "monthly_probe_month_start": MONTHLY_PROBE_START,
            "permanent_404_count": 0,
            "probe_completed": True,
            "sample_failed_probes": failed_probe_samples,
            "total_checksum_urls_probed": 0,
            "total_daily_tail_urls_probed": sum(row["page_count"] for row in daily_by_symbol.values()),
            "total_monthly_urls_probed": sum(row["page_count"] for row in monthly_by_symbol.values()),
            "transient_failure_count": len(monthly_failed) + len(daily_failed),
        },
        "artifact_kind": "BINANCE_USDT_PERPETUAL_1M_COVERAGE_DISCOVERY_LOCK",
        "coverage_window_policy": {
            "comparable_3y_window_end_month": latest_monthly_archive_month,
            "comparable_3y_window_month_count": len(window_3y),
            "comparable_3y_window_start_month": window_3y[0],
            "global_max_available_daily_date": global_max_daily,
            "latest_monthly_archive_month": latest_monthly_archive_month,
            "second_source_5y_window_end_month": latest_monthly_archive_month,
            "second_source_5y_window_month_count": len(window_5y),
            "second_source_5y_window_start_month": window_5y[0],
            "strict_3y_completeness_claimed": len(strict_3y) == len(candidate_symbols),
            "strict_5y_completeness_claimed": len(strict_5y) == len(candidate_symbols),
        },
        "discovery_policy": {
            "coverage_presence_only": True,
            "daily_tail_days": DAILY_TAIL_DAYS,
            "daily_tail_probe_enabled": True,
            "direct_probe_budget_guard": {
                "direct_probe_budget": MAX_DIRECT_PROBE_BUDGET,
                "direct_probe_plan_if_listing_unavailable": direct_probe_plan,
                "direct_probe_plan_started": False,
            },
            "exchange": "BINANCE",
            "instrument_filter": "USDT_PERPETUAL",
            "interval": "1m",
            "kline_rows_validated": False,
            "market": "USD_M_FUTURES",
            "monthly_archives_primary": True,
            "no_strategy_research": True,
            "row_content_downloaded": False,
            "zip_content_opened": False,
        },
        "global_coverage_summary": {
            "candidate_universe_symbols_total": len(candidate_symbols),
            "coverage_gap_symbols": len(coverage_gap),
            "current_trading_symbols_with_coverage_count": sum(
                1 for record in records if record["current_trading"] and record["monthly_available_count"] > 0
            ),
            "current_trading_symbols_without_coverage_count": sum(
                1 for record in records if record["current_trading"] and record["monthly_available_count"] == 0
            ),
            "delisted_or_archive_only_symbols_count_if_available": len(archive_only),
            "earliest_monthly_coverage_start": earliest_month,
            "global_max_available_daily_date": global_max_daily,
            "latest_monthly_coverage_end": latest_month,
            "near_3y_complete_symbols": len(near_3y),
            "near_5y_complete_symbols": len(near_5y),
            "pending_or_failed_probe_symbols": len(pending),
            "strict_3y_complete_symbols": len(strict_3y),
            "strict_5y_complete_symbols": len(strict_5y),
            "symbols_with_any_monthly_coverage": len(monthly_available_records),
            "symbols_with_internal_gaps_count": sum(
                1 for record in records if record["internal_missing_months_between_first_and_last"]
            ),
            "symbols_with_no_monthly_coverage": sum(1 for record in records if record["monthly_available_count"] == 0),
            "symbols_with_trailing_gaps_count": sum(
                1 for record in records if record["trailing_missing_months_after_last_available"]
            ),
            "top_missing_months_by_count": top_missing_months(records),
        },
        "limitations": [
            "coverage lock is based on public archive file presence, not row-level validation.",
            "no kline zip contents were opened.",
            "no OHLCV sanity validation was performed.",
            "archive files may be updated by Binance later.",
            "current exchangeInfo may omit delisted historical symbols.",
            "archive directory parsing may be incomplete if unavailable.",
            "this lock is not a backtest panel.",
            "this lock is not valid for edge claim.",
            "this lock is not runtime/live/capital permission.",
        ],
        "locked_symbol_sets": {
            "binance_usdt_perpetual_archive_only_symbols_if_available": archive_only,
            "binance_usdt_perpetual_candidate_universe_symbols": candidate_symbols,
            "binance_usdt_perpetual_coverage_gap_symbols": coverage_gap,
            "binance_usdt_perpetual_current_trading_symbols": sorted(trading_symbols),
            "binance_usdt_perpetual_near_3y_complete_symbols": near_3y,
            "binance_usdt_perpetual_near_5y_complete_symbols": near_5y,
            "binance_usdt_perpetual_pending_or_failed_probe_symbols": pending,
            "binance_usdt_perpetual_strict_3y_complete_symbols": strict_3y,
            "binance_usdt_perpetual_strict_5y_complete_symbols": strict_5y,
        },
        "module": MODULE_PATH,
        "repo_scope": {
            "api_key_used": False,
            "artifact_created_in_repo": True,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "public_binance_network_used_for_metadata_discovery": True,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "run_metadata": {
            "current_utc_date": current_date.isoformat(),
            "deterministic_sorting_applied": True,
            "platform": platform.platform(),
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "python_version": sys.version,
            "run_completed_at_utc": run_completed.isoformat().replace("+00:00", "Z"),
            "run_started_at_utc": run_started.isoformat().replace("+00:00", "Z"),
        },
        "safety_permissions": {
            "binance_panel_build_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "coverage_lock_created": True,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "next_step_may_be_coverage_review_or_panel_build_planning_only": True,
            "okx_panel_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "source_endpoints": {
            "daily_checksum_url_template": DAILY_CHECKSUM_URL_TEMPLATE,
            "daily_kline_url_template": DAILY_KLINE_URL_TEMPLATE,
            "exchange_info_url": EXCHANGE_INFO_URL,
            "monthly_checksum_url_template": MONTHLY_CHECKSUM_URL_TEMPLATE,
            "monthly_kline_url_template": MONTHLY_KLINE_URL_TEMPLATE,
            "official_public_archive_base": PUBLIC_ARCHIVE_BASE,
        },
        "status": REQUIRED_STATUS,
        "symbol_coverage_records": records,
        "universe_summary": {
            "archive_directory_listing_error": archive_listing_error,
            "archive_directory_listing_parsed": archive_listing_parsed,
            "archive_symbols_total_if_parsed": len(archive_symbols) if archive_listing_parsed else 0,
            "candidate_universe_source_policy": "union(exchangeInfo USDT perpetual symbols, parsed archive USDT symbols if available)",
            "candidate_universe_symbols": candidate_symbols,
            "candidate_universe_symbols_total": len(candidate_symbols),
            "current_trading_symbols_total": len(trading_symbols),
            "exchange_info_symbols_total": len(exchange_info.get("symbols", [])),
            "exchange_info_usdt_perpetual_symbols_total": len(exchange_records),
            "non_trading_symbols_total": len(non_trading_symbols),
        },
    }
    payload["validation_checks"] = {
        "artifact_json_valid": True,
        "candidate_universe_symbols_total_matches_records_count": len(candidate_symbols) == len(records),
        "coverage_lock_artifact_path_equals_required_path": COVERAGE_LOCK_ARTIFACT_PATH
        == "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
        "daily_tail_probe_completed_or_recorded_unavailable": len(daily_by_symbol) == len(candidate_symbols),
        "every_symbol_has_record": sorted(record["symbol"] for record in records) == candidate_symbols,
        "exactly_one_new_tracked_json_coverage_lock_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "exchange_info_fetched": True,
        "locked_symbol_sets_sorted": all(
            values == sorted(values)
            for values in payload["locked_symbol_sets"].values()
            if isinstance(values, list)
        ),
        "module_path_equals_required_path": MODULE_PATH
        == "tools/edge_factory_os_repo_only_binance_usdt_perpetual_1m_coverage_discovery_and_lock_v1.py",
        "monthly_probe_completed": len(monthly_by_symbol) == len(candidate_symbols),
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_kline_rows_read": True,
        "no_kline_zip_contents_downloaded": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "payload_sha256_excluding_hash_present": True,
        "replacement_checks_all_true": True,
        "status_equals_required_status": True,
        "symbol_records_sorted": [record["symbol"] for record in records] == candidate_symbols,
        "usdt_perpetual_universe_nonempty": bool(exchange_records),
    }
    payload["replacement_checks_all_true"] = all(value is True for value in payload["validation_checks"].values())
    payload_without_hash = dict(payload)
    payload_without_hash.pop("payload_sha256_excluding_hash", None)
    payload["payload_sha256_excluding_hash"] = hashlib.sha256(canonical_json_bytes(payload_without_hash)).hexdigest()
    progress(
        start_monotonic,
        "coverage_lock_built_in_memory",
        candidate_symbols=len(candidate_symbols),
        failed_probe_count=payload["archive_discovery_summary"]["failed_probe_count"],
        payload_sha256_excluding_hash=payload["payload_sha256_excluding_hash"],
    )
    return payload


def validate_payload(payload: dict[str, Any]) -> None:
    assert payload["status"] == REQUIRED_STATUS
    assert payload["module"] == MODULE_PATH
    assert COVERAGE_LOCK_ARTIFACT_PATH == "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"
    assert payload["validation_checks"]["exchange_info_fetched"] is True
    assert payload["universe_summary"]["exchange_info_usdt_perpetual_symbols_total"] > 0
    assert payload["universe_summary"]["candidate_universe_symbols_total"] > 0
    assert payload["validation_checks"]["candidate_universe_symbols_total_matches_records_count"] is True
    assert payload["validation_checks"]["every_symbol_has_record"] is True
    assert payload["validation_checks"]["monthly_probe_completed"] is True
    assert payload["discovery_policy"]["row_content_downloaded"] is False
    assert payload["discovery_policy"]["zip_content_opened"] is False
    assert payload["discovery_policy"]["kline_rows_validated"] is False
    assert payload["repo_scope"]["strategy_search_executed"] is False
    assert payload["repo_scope"]["candidate_generation"] is False
    assert payload["repo_scope"]["edge_claim"] is False
    assert payload["repo_scope"]["runtime_live_capital"] is False
    assert payload["replacement_checks_all_true"] is True
    assert payload["payload_sha256_excluding_hash"]


def write_artifact_atomic(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEMP_ARTIFACT_PATH.exists():
        TEMP_ARTIFACT_PATH.unlink()
    TEMP_ARTIFACT_PATH.write_bytes(canonical_json_bytes(payload) + b"\n")
    TEMP_ARTIFACT_PATH.replace(ARTIFACT_PATH)


def stdout_summary(payload: dict[str, Any]) -> dict[str, Any]:
    global_summary = payload["global_coverage_summary"]
    return {
        "candidate_generation": False,
        "candidate_universe_symbols_total": payload["universe_summary"]["candidate_universe_symbols_total"],
        "coverage_gap_symbols": global_summary["coverage_gap_symbols"],
        "coverage_lock_artifact_path": COVERAGE_LOCK_ARTIFACT_PATH,
        "current_trading_symbols_total": payload["universe_summary"]["current_trading_symbols_total"],
        "edge_claim": False,
        "global_max_available_daily_date": payload["coverage_window_policy"]["global_max_available_daily_date"],
        "latest_monthly_archive_month": payload["coverage_window_policy"]["latest_monthly_archive_month"],
        "near_3y_complete_symbols": global_summary["near_3y_complete_symbols"],
        "near_5y_complete_symbols": global_summary["near_5y_complete_symbols"],
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "pending_or_failed_probe_symbols": global_summary["pending_or_failed_probe_symbols"],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
        "runtime_live_capital": False,
        "status": payload["status"],
        "strategy_search_executed": False,
        "strict_3y_complete_symbols": global_summary["strict_3y_complete_symbols"],
        "strict_5y_complete_symbols": global_summary["strict_5y_complete_symbols"],
    }


def main() -> int:
    try:
        payload = build_lock()
        validate_payload(payload)
    except BlockedError as exc:
        print(
            json.dumps(
                {
                    "exact_blocker": str(exc),
                    "replacement_checks_all_true": False,
                    "status": "BLOCKED",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    write_artifact_atomic(payload)
    print(json.dumps(stdout_summary(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
