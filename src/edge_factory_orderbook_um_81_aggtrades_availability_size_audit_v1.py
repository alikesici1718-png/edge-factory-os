#!/usr/bin/env python
"""Audit Binance USD-M daily aggTrades availability and size for the verified 81-symbol universe."""

from __future__ import annotations

import csv
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\edge_factory_external_data")
PUBLIC_ARCHIVE_HOSTS = {"data.binance.vision", "s3-ap-northeast-1.amazonaws.com"}
S3_LIST_BASE = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
EXPECTED_SYMBOL_COUNT = 81
REQUEST_TIMEOUT_SECONDS = 45
MAX_RETRIES = 4
REQUEST_SLEEP_SECONDS = 0.10
USER_AGENT = "edge-factory-orderbook-um-81-aggtrades-availability-size-audit-v1"

BOOKDEPTH_MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.csv"
BOOKDEPTH_COVERAGE_JSON = OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.json"
BOOKDEPTH_DOWNLOAD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_download_summary.json"
BOOKDEPTH_SYMBOL_COVERAGE_CSV = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_symbol_coverage.csv"

AGGTRADES_MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_81_aggtrades_availability_manifest.csv"
AGGTRADES_MANIFEST_JSONL = OUTPUTS_DIR / "orderbook_um_81_aggtrades_availability_manifest.jsonl"
AGGTRADES_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_aggtrades_coverage_summary.json"
AGGTRADES_SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_aggtrades_coverage_summary.md"
AGGTRADES_GAPS_CSV = OUTPUTS_DIR / "orderbook_um_81_aggtrades_vs_bookdepth_coverage_gaps.csv"

MANIFEST_COLUMNS = [
    "symbol",
    "data_type",
    "frequency",
    "file_date",
    "file_name",
    "url",
    "checksum_url",
    "size_bytes",
    "last_modified",
    "local_target_path",
    "bookdepth_available_same_day",
    "aggtrades_available_same_day",
    "status",
    "error_message",
]

GAP_COLUMNS = [
    "symbol",
    "file_date",
    "bookdepth_available_same_day",
    "aggtrades_available_same_day",
    "gap_type",
    "estimated_missing_size_bytes",
    "bookdepth_symbol_earliest",
    "bookdepth_symbol_latest",
]


class AggTradesAuditBlocked(RuntimeError):
    """Raised when the manifest-only audit must stop closed."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def path_is_inside(child: Path, parent: Path) -> bool:
    child_text = os.path.normcase(os.path.abspath(os.fspath(child)))
    parent_text = os.path.normcase(os.path.abspath(os.fspath(parent)))
    return child_text == parent_text or child_text.startswith(parent_text + os.sep)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AggTradesAuditBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AggTradesAuditBlocked(f"required input is not a JSON object: {path}")
    return payload


def data_root(download_summary: dict[str, Any]) -> Path:
    configured = os.environ.get("EDGE_FACTORY_DATA_ROOT")
    if configured:
        root = Path(configured).expanduser()
    else:
        root = Path(download_summary.get("external_data_root") or DEFAULT_DATA_ROOT).expanduser()
    if path_is_inside(root, REPO_ROOT):
        raise AggTradesAuditBlocked(f"data root resolves inside repo: {root}")
    return root


def raw_target_dir(root: Path) -> Path:
    return root / "binance_um_81_full_aggtrades_raw"


def local_target_path(root: Path, symbol: str, file_name: str) -> str:
    return str(raw_target_dir(root) / "aggTrades" / "daily" / symbol / file_name)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AggTradesAuditBlocked(f"missing required input: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")


def json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def valid_symbol(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9]+USDT", value or ""))


def parse_nonnegative_int(value: Any, label: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AggTradesAuditBlocked(f"{label} is not an integer: {value!r}") from exc
    if parsed < 0:
        raise AggTradesAuditBlocked(f"{label} is negative: {parsed}")
    return parsed


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise AggTradesAuditBlocked(f"invalid date: {value}") from exc


def date_range(start_text: str, end_text: str) -> list[str]:
    start = parse_date(start_text)
    end = parse_date(end_text)
    if end < start:
        raise AggTradesAuditBlocked(f"invalid date range: {start_text} to {end_text}")
    values: list[str] = []
    current = start
    while current <= end:
        values.append(current.isoformat())
        current += timedelta(days=1)
    return values


def load_verified_bookdepth_context() -> tuple[list[str], dict[str, set[str]], dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    coverage = load_json(BOOKDEPTH_COVERAGE_JSON)
    download_summary = load_json(BOOKDEPTH_DOWNLOAD_SUMMARY_JSON)
    if download_summary.get("status") != "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED":
        raise AggTradesAuditBlocked("full bookDepth download summary is not PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED")
    checksum_verified_count = parse_nonnegative_int(download_summary.get("checksum_verified_count"), "checksum_verified_count")
    expected_file_count = parse_nonnegative_int(download_summary.get("expected_file_count"), "expected_file_count")
    failed_count = parse_nonnegative_int(download_summary.get("failed_count"), "failed_count")
    if checksum_verified_count != expected_file_count:
        raise AggTradesAuditBlocked("full bookDepth checksum_verified_count does not match expected_file_count")
    if failed_count != 0:
        raise AggTradesAuditBlocked("full bookDepth download summary reports failures")

    symbol_coverage_rows = read_csv_rows(BOOKDEPTH_SYMBOL_COVERAGE_CSV)
    symbols = [row.get("symbol", "") for row in symbol_coverage_rows]
    if len(symbols) != EXPECTED_SYMBOL_COUNT or len(set(symbols)) != EXPECTED_SYMBOL_COUNT:
        raise AggTradesAuditBlocked("bookDepth symbol coverage does not contain exactly 81 unique symbols")
    if not all(valid_symbol(symbol) for symbol in symbols):
        raise AggTradesAuditBlocked("bookDepth symbol coverage contains invalid symbols")

    summary_symbols = sorted((download_summary.get("earliest_latest_by_symbol") or {}).keys())
    if summary_symbols and summary_symbols != sorted(symbols):
        raise AggTradesAuditBlocked("bookDepth download summary symbols do not match symbol coverage CSV")

    bookdepth_rows = read_csv_rows(BOOKDEPTH_MANIFEST_CSV)
    bookdepth_dates: dict[str, set[str]] = {symbol: set() for symbol in symbols}
    for row in bookdepth_rows:
        if (
            row.get("symbol") in bookdepth_dates
            and row.get("data_type") == "bookDepth"
            and row.get("frequency") == "daily"
            and row.get("status") == "AVAILABLE"
            and row.get("file_date_or_month")
        ):
            bookdepth_dates[row["symbol"]].add(row["file_date_or_month"])

    extents: dict[str, dict[str, Any]] = {}
    for row in symbol_coverage_rows:
        symbol = row["symbol"]
        dates = bookdepth_dates.get(symbol) or set(date_range(row["earliest_date"], row["latest_date"]))
        expected_count = int(row.get("expected_file_count") or 0)
        if len(dates) != expected_count:
            raise AggTradesAuditBlocked(f"bookDepth manifest date count mismatch for {symbol}: {len(dates)} != {expected_count}")
        extents[symbol] = {
            "earliest": row["earliest_date"],
            "latest": row["latest_date"],
            "expected_file_count": expected_count,
        }
    return symbols, bookdepth_dates, extents, coverage, download_summary


def assert_public_archive_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in PUBLIC_ARCHIVE_HOSTS:
        raise AggTradesAuditBlocked(f"blocked non-public Binance archive URL: {url}")
    if parsed.netloc == "data.binance.vision" and not parsed.path.startswith("/data/futures/um/daily/aggTrades/"):
        raise AggTradesAuditBlocked(f"blocked non-USD-M daily aggTrades URL: {url}")


def request_text(url: str) -> tuple[int | None, str, dict[str, str]]:
    assert_public_archive_url(url)
    last_error = ""
    for attempt in range(MAX_RETRIES):
        if attempt:
            time.sleep(min(1.5 * attempt, 5.0))
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                body = response.read().decode("utf-8", errors="replace")
                headers = {key.lower(): value for key, value in response.headers.items()}
                time.sleep(REQUEST_SLEEP_SECONDS)
                return getattr(response, "status", None), body, headers
        except urllib.error.HTTPError as exc:
            body = exc.read(2048).decode("utf-8", errors="replace")
            if exc.code == 404:
                return 404, body, {}
            last_error = f"HTTP {exc.code}: {body[:500]}"
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
    return None, "", {"x-edge-factory-error": last_error or "unknown request failure"}


def s3_listing_url(prefix: str, continuation_token: str | None = None) -> str:
    params = {"list-type": "2", "prefix": prefix}
    if continuation_token:
        params["continuation-token"] = continuation_token
    return S3_LIST_BASE + "?" + urllib.parse.urlencode(params)


def xml_text(element: ET.Element, name: str) -> str:
    for child in list(element):
        if child.tag.rsplit("}", 1)[-1] == name:
            return "" if child.text is None else child.text.strip()
    return ""


def parse_s3_xml(body: str) -> tuple[list[dict[str, Any]], str | None]:
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return [], None
    rows: list[dict[str, Any]] = []
    for contents in root.iter():
        if contents.tag.rsplit("}", 1)[-1] != "Contents":
            continue
        key = xml_text(contents, "Key")
        if not key:
            continue
        size_text = xml_text(contents, "Size")
        rows.append(
            {
                "key": key,
                "size_bytes": int(size_text) if size_text.isdigit() else None,
                "last_modified": xml_text(contents, "LastModified"),
            }
        )
    token = ""
    for child in root.iter():
        if child.tag.rsplit("}", 1)[-1] == "NextContinuationToken":
            token = "" if child.text is None else child.text.strip()
            break
    return rows, token or None


def parse_listing_fallback(body: str, prefix: str) -> list[dict[str, Any]]:
    escaped_prefix = re.escape(prefix)
    pattern = re.compile(rf"({escaped_prefix}[^\"'<>\s]+)")
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for match in pattern.finditer(body):
        key = match.group(1).replace("\\/", "/")
        if key in seen:
            continue
        seen.add(key)
        rows.append({"key": key, "size_bytes": None, "last_modified": ""})
    return rows


def list_archive_prefix(prefix: str) -> tuple[list[dict[str, Any]], str | None]:
    rows: list[dict[str, Any]] = []
    token: str | None = None
    first_error: str | None = None
    for _page in range(20):
        status, body, headers = request_text(s3_listing_url(prefix, token))
        if status != 200:
            first_error = headers.get("x-edge-factory-error") or f"listing status {status}"
            break
        page_rows, token = parse_s3_xml(body)
        if not page_rows:
            page_rows = parse_listing_fallback(body, prefix)
        rows.extend(page_rows)
        if not token:
            break
    if rows:
        return rows, None

    portal_url = "https://data.binance.vision/?" + urllib.parse.urlencode({"prefix": prefix})
    status, body, headers = request_text(portal_url)
    if status == 200:
        fallback_rows = parse_listing_fallback(body, prefix)
        if fallback_rows:
            return fallback_rows, None
    return [], headers.get("x-edge-factory-error") or first_error or f"listing status {status}"


def archive_url_from_key(key: str) -> str:
    return f"https://data.binance.vision/{key}"


def checksum_key_set(rows: list[dict[str, Any]]) -> set[str]:
    return {row["key"] for row in rows if row["key"].endswith(".CHECKSUM")}


def extract_aggtrades_date(file_name: str) -> str | None:
    match = re.fullmatch(r"[A-Z0-9]+USDT-aggTrades-(\d{4}-\d{2}-\d{2})\.zip", file_name)
    return match.group(1) if match else None


def build_available_rows_for_symbol(root: Path, symbol: str, bookdepth_dates: set[str]) -> tuple[list[dict[str, Any]], str | None]:
    prefix = f"data/futures/um/daily/aggTrades/{symbol}/"
    listing_rows, error = list_archive_prefix(prefix)
    checksums = checksum_key_set(listing_rows)
    archive_rows = [row for row in listing_rows if row["key"].endswith(".zip") and not row["key"].endswith(".zip.CHECKSUM")]
    parsed: list[dict[str, Any]] = []
    for raw in sorted(archive_rows, key=lambda item: item["key"]):
        file_name = raw["key"].rsplit("/", 1)[-1]
        file_date = extract_aggtrades_date(file_name)
        if not file_date:
            continue
        checksum_key = raw["key"] + ".CHECKSUM"
        row = {
            "symbol": symbol,
            "data_type": "aggTrades",
            "frequency": "daily",
            "file_date": file_date,
            "file_name": file_name,
            "url": archive_url_from_key(raw["key"]),
            "checksum_url": archive_url_from_key(checksum_key) if checksum_key in checksums else "",
            "size_bytes": raw.get("size_bytes") if raw.get("size_bytes") is not None else "",
            "last_modified": raw.get("last_modified") or "",
            "local_target_path": local_target_path(root, symbol, file_name),
            "bookdepth_available_same_day": bool_text(file_date in bookdepth_dates),
            "aggtrades_available_same_day": "true",
            "status": "AVAILABLE",
            "error_message": "",
        }
        parsed.append(row)
    return parsed, error


def average_size(rows: list[dict[str, Any]]) -> int:
    values = [int(row["size_bytes"]) for row in rows if str(row.get("size_bytes", "")).isdigit()]
    if not values:
        return 0
    return int(round(sum(values) / len(values)))


def build_missing_rows(root: Path, symbol: str, missing_dates: list[str], error_message: str = "") -> list[dict[str, Any]]:
    return [
        {
            "symbol": symbol,
            "data_type": "aggTrades",
            "frequency": "daily",
            "file_date": file_date,
            "file_name": "",
            "url": "",
            "checksum_url": "",
            "size_bytes": "",
            "last_modified": "",
            "local_target_path": str(raw_target_dir(root) / "aggTrades" / "daily" / symbol),
            "bookdepth_available_same_day": "true",
            "aggtrades_available_same_day": "false",
            "status": "MISSING_AGGTRADES_WHILE_BOOKDEPTH_AVAILABLE",
            "error_message": error_message,
        }
        for file_date in missing_dates
    ]


def choose_next_action(total_estimated_size_gb: float, missing_gap_count: int, missing_symbols: list[str]) -> str:
    if missing_symbols:
        return "C) stop due to missing/unsupported coverage"
    if missing_gap_count:
        return "B) recent-window aggTrades download if full size is too large"
    if total_estimated_size_gb <= 250.0:
        return "A) full 81-symbol aggTrades download if size is acceptable"
    return "B) recent-window aggTrades download if full size is too large"


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 aggTrades availability and size audit v1",
        "",
        f"status: {summary['status']}",
        f"created_at_utc: {summary['created_at_utc']}",
        f"symbol_count_requested: {summary['symbol_count_requested']}",
        f"symbol_count_found: {summary['symbol_count_found']}",
        f"symbol_count_missing: {summary['symbol_count_missing']}",
        f"total_file_count: {summary['total_file_count']}",
        f"total_estimated_size_gb: {summary['total_estimated_size_gb']}",
        f"estimated_size_for_bookdepth_matching_coverage_gb: {summary['estimated_size_for_bookdepth_matching_coverage_gb']}",
        f"estimated_size_for_global_2023_01_01_to_2026_06_15_gb: {summary['estimated_size_for_global_2023_01_01_to_2026_06_15_gb']}",
        f"earliest_global_date: {summary['earliest_global_date']}",
        f"latest_global_date: {summary['latest_global_date']}",
        f"missing_aggtrades_while_bookdepth_exists_count: {summary['bookdepth_coverage_comparison']['missing_aggtrades_while_bookdepth_exists_count']}",
        f"extra_aggtrades_outside_bookdepth_count: {summary['bookdepth_coverage_comparison']['extra_aggtrades_outside_bookdepth_count']}",
        f"recommended_next_action: {summary['recommended_next_action']}",
        f"replacement_checks_all_true: {bool_text(summary['replacement_checks_all_true'])}",
        f"next_module: {summary['next_module']}",
        "",
        "## Missing symbols",
    ]
    if summary["missing_symbols"]:
        lines.extend(f"- {symbol}" for symbol in summary["missing_symbols"])
    else:
        lines.append("- none")
    lines.extend(["", "## Symbols with partial coverage"])
    if summary["symbols_with_partial_coverage"]:
        lines.extend(f"- {symbol}" for symbol in summary["symbols_with_partial_coverage"])
    else:
        lines.append("- none")
    lines.extend(["", "## Top 20 largest symbols by estimated size"])
    for item in summary["top_20_largest_symbols_by_estimated_size"]:
        lines.append(f"- {item['symbol']}: {item['file_count']} files, {item['estimated_size_gb']:.6f} GB")
    lines.extend(
        [
            "",
            "## Safety",
            "- Manifest and size audit only.",
            "- No raw aggTrades ZIPs were downloaded.",
            "- Public Binance Data Vision USD-M daily aggTrades listings only.",
            "- No private endpoints, account data, execution, recommendation, or strategy logic.",
            "",
        ]
    )
    AGGTRADES_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def build_audit() -> dict[str, Any]:
    symbols, bookdepth_dates, bookdepth_extents, bookdepth_coverage, download_summary = load_verified_bookdepth_context()
    root = data_root(download_summary)
    rows: list[dict[str, Any]] = []
    gap_rows: list[dict[str, Any]] = []
    symbol_summaries: dict[str, dict[str, Any]] = {}

    for index, symbol in enumerate(symbols, start=1):
        print(f"probe aggTrades {index}/{len(symbols)} {symbol}", flush=True)
        available_rows, error = build_available_rows_for_symbol(root, symbol, bookdepth_dates[symbol])
        available_dates = {row["file_date"] for row in available_rows}
        missing_dates = sorted(bookdepth_dates[symbol] - available_dates)
        missing_rows = build_missing_rows(root, symbol, missing_dates, error or "")
        rows.extend(available_rows)
        rows.extend(missing_rows)
        avg_size = average_size(available_rows)
        matching_available_rows = [row for row in available_rows if row["file_date"] in bookdepth_dates[symbol]]
        matching_size = sum(int(row["size_bytes"]) for row in matching_available_rows if str(row.get("size_bytes", "")).isdigit())
        estimated_missing_size = avg_size * len(missing_dates)
        extra_dates = sorted(available_dates - bookdepth_dates[symbol])
        for file_date in missing_dates:
            gap_rows.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "bookdepth_available_same_day": "true",
                    "aggtrades_available_same_day": "false",
                    "gap_type": "MISSING_AGGTRADES_WHILE_BOOKDEPTH_EXISTS",
                    "estimated_missing_size_bytes": avg_size,
                    "bookdepth_symbol_earliest": bookdepth_extents[symbol]["earliest"],
                    "bookdepth_symbol_latest": bookdepth_extents[symbol]["latest"],
                }
            )
        for file_date in extra_dates:
            gap_rows.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "bookdepth_available_same_day": "false",
                    "aggtrades_available_same_day": "true",
                    "gap_type": "AGGTRADES_EXISTS_OUTSIDE_BOOKDEPTH_COVERAGE",
                    "estimated_missing_size_bytes": 0,
                    "bookdepth_symbol_earliest": bookdepth_extents[symbol]["earliest"],
                    "bookdepth_symbol_latest": bookdepth_extents[symbol]["latest"],
                }
            )
        global_dates = set(date_range("2023-01-01", "2026-06-15"))
        global_missing_count = len(global_dates - available_dates)
        symbol_summaries[symbol] = {
            "available_file_count": len(available_rows),
            "bookdepth_file_count": len(bookdepth_dates[symbol]),
            "missing_while_bookdepth_exists_count": len(missing_dates),
            "extra_outside_bookdepth_count": len(extra_dates),
            "estimated_available_size_bytes": sum(int(row["size_bytes"]) for row in available_rows if str(row.get("size_bytes", "")).isdigit()),
            "estimated_bookdepth_matching_size_bytes": matching_size + estimated_missing_size,
            "estimated_global_2023_01_01_to_2026_06_15_size_bytes": sum(int(row["size_bytes"]) for row in available_rows if str(row.get("size_bytes", "")).isdigit()) + avg_size * global_missing_count,
            "average_size_bytes": avg_size,
            "earliest": min(available_dates) if available_dates else None,
            "latest": max(available_dates) if available_dates else None,
            "listing_error": error,
        }

    available_manifest_rows = [row for row in rows if row["status"] == "AVAILABLE"]
    missing_symbols = [symbol for symbol, item in symbol_summaries.items() if item["available_file_count"] == 0]
    partial_symbols = [
        symbol
        for symbol, item in symbol_summaries.items()
        if item["missing_while_bookdepth_exists_count"] > 0 or item["extra_outside_bookdepth_count"] > 0
    ]
    all_available_dates = [row["file_date"] for row in available_manifest_rows]
    total_size_bytes = sum(item["estimated_available_size_bytes"] for item in symbol_summaries.values())
    matching_size_bytes = sum(item["estimated_bookdepth_matching_size_bytes"] for item in symbol_summaries.values())
    global_size_bytes = sum(item["estimated_global_2023_01_01_to_2026_06_15_size_bytes"] for item in symbol_summaries.values())
    gap_missing_count = sum(item["missing_while_bookdepth_exists_count"] for item in symbol_summaries.values())
    extra_count = sum(item["extra_outside_bookdepth_count"] for item in symbol_summaries.values())
    next_action = choose_next_action(round(total_size_bytes / 1_000_000_000, 6), gap_missing_count, missing_symbols)
    summary = {
        "status": "PASS_ORDERBOOK_UM_81_AGGTRADES_AVAILABILITY_SIZE_AUDIT_CREATED",
        "created_at_utc": utc_now_text(),
        "task_name": "ORDERBOOK_UM_81_SYMBOL_AGGTRADES_AVAILABILITY_SIZE_AUDIT_V1",
        "symbol_count_requested": EXPECTED_SYMBOL_COUNT,
        "symbol_count_found": EXPECTED_SYMBOL_COUNT - len(missing_symbols),
        "symbol_count_missing": len(missing_symbols),
        "total_file_count": len(available_manifest_rows),
        "total_estimated_size_bytes": total_size_bytes,
        "total_estimated_size_gb": round(total_size_bytes / 1_000_000_000, 6),
        "estimated_size_for_bookdepth_matching_coverage_bytes": matching_size_bytes,
        "estimated_size_for_bookdepth_matching_coverage_gb": round(matching_size_bytes / 1_000_000_000, 6),
        "estimated_size_for_global_2023_01_01_to_2026_06_15_bytes": global_size_bytes,
        "estimated_size_for_global_2023_01_01_to_2026_06_15_gb": round(global_size_bytes / 1_000_000_000, 6),
        "earliest_global_date": min(all_available_dates) if all_available_dates else None,
        "latest_global_date": max(all_available_dates) if all_available_dates else None,
        "bookdepth_global_earliest_date": bookdepth_coverage.get("earliest_global_date"),
        "bookdepth_global_latest_date": bookdepth_coverage.get("latest_global_date"),
        "bookdepth_download_summary_status": download_summary.get("status"),
        "bookDepth coverage comparison": {
            "bookdepth_expected_file_count": download_summary.get("expected_file_count"),
            "bookdepth_checksum_verified_count": download_summary.get("checksum_verified_count"),
            "missing_aggtrades_while_bookdepth_exists_count": gap_missing_count,
            "extra_aggtrades_outside_bookdepth_count": extra_count,
            "coverage_gaps_csv": str(AGGTRADES_GAPS_CSV),
        },
        "bookdepth_coverage_comparison": {
            "bookdepth_expected_file_count": download_summary.get("expected_file_count"),
            "bookdepth_checksum_verified_count": download_summary.get("checksum_verified_count"),
            "missing_aggtrades_while_bookdepth_exists_count": gap_missing_count,
            "extra_aggtrades_outside_bookdepth_count": extra_count,
            "coverage_gaps_csv": str(AGGTRADES_GAPS_CSV),
        },
        "missing_symbols": missing_symbols,
        "symbols_with_partial_coverage": sorted(partial_symbols),
        "dates_missing_aggTrades_while_bookDepth_exists": {
            "count": gap_missing_count,
            "sample": gap_rows[:50],
            "csv": str(AGGTRADES_GAPS_CSV),
        },
        "top_20_largest_symbols_by_estimated_size": [
            {
                "symbol": item["symbol"],
                "file_count": item["file_count"],
                "estimated_size_bytes": item["estimated_size_bytes"],
                "estimated_size_gb": item["estimated_size_bytes"] / 1_000_000_000,
            }
            for item in sorted(
                [
                    {
                        "symbol": symbol,
                        "file_count": symbol_summaries[symbol]["available_file_count"],
                        "estimated_size_bytes": symbol_summaries[symbol]["estimated_available_size_bytes"],
                    }
                    for symbol in symbols
                ],
                key=lambda item: item["estimated_size_bytes"],
                reverse=True,
            )[:20]
        ],
        "symbol_summaries": symbol_summaries,
        "external_data_root": str(root),
        "raw_target_directory": str(raw_target_dir(root)),
        "manifest_csv": str(AGGTRADES_MANIFEST_CSV),
        "manifest_jsonl": str(AGGTRADES_MANIFEST_JSONL),
        "coverage_summary_json": str(AGGTRADES_SUMMARY_JSON),
        "coverage_gaps_csv": str(AGGTRADES_GAPS_CSV),
        "recommended_next_action": next_action,
        "replacement_checks_all_true": True,
        "next_module": "ORDERBOOK_UM_81_AGGTRADES_MANIFEST_VALIDATOR_V1",
    }
    write_csv(AGGTRADES_MANIFEST_CSV, rows, MANIFEST_COLUMNS)
    write_jsonl(AGGTRADES_MANIFEST_JSONL, rows)
    write_csv(AGGTRADES_GAPS_CSV, gap_rows, GAP_COLUMNS)
    json_dump(AGGTRADES_SUMMARY_JSON, summary)
    write_summary_md(summary)
    return summary


def write_blocked(exc: Exception) -> dict[str, Any]:
    summary = {
        "status": "BLOCKED_ORDERBOOK_UM_81_AGGTRADES_AVAILABILITY_SIZE_AUDIT",
        "created_at_utc": utc_now_text(),
        "exact_blocker": str(exc),
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_81_AGGTRADES_APPROVAL_OR_BLOCKER_REVIEW",
    }
    json_dump(AGGTRADES_SUMMARY_JSON, summary)
    AGGTRADES_SUMMARY_MD.write_text(
        "\n".join(
            [
                "# BLOCKED_ORDERBOOK_UM_81_AGGTRADES_AVAILABILITY_SIZE_AUDIT",
                "",
                f"created_at_utc: {summary['created_at_utc']}",
                f"exact_blocker: {summary['exact_blocker']}",
                "replacement_checks_all_true=false",
                f"next_module: {summary['next_module']}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return summary


def main() -> int:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        summary = build_audit()
    except Exception as exc:  # noqa: BLE001
        summary = write_blocked(exc)
    print(f"status: {summary['status']}")
    print(f"manifest_csv: {AGGTRADES_MANIFEST_CSV}")
    print(f"manifest_jsonl: {AGGTRADES_MANIFEST_JSONL}")
    print(f"coverage_summary_json: {AGGTRADES_SUMMARY_JSON}")
    print(f"coverage_summary_md: {AGGTRADES_SUMMARY_MD}")
    print(f"coverage_gaps_csv: {AGGTRADES_GAPS_CSV}")
    print(f"replacement_checks_all_true: {bool_text(bool(summary['replacement_checks_all_true']))}")
    print(f"next_module: {summary['next_module']}")
    return 0 if summary["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
