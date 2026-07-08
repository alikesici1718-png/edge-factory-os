#!/usr/bin/env python
"""Audit Binance USD-M Data Vision bookDepth availability for the 81-symbol overlap universe."""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
PUBLIC_ARCHIVE_HOSTS = {"data.binance.vision", "s3-ap-northeast-1.amazonaws.com"}
S3_LIST_BASE = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
DATA_VISION_BASE = "https://data.binance.vision/data/futures/um"
EXPECTED_SYMBOL_COUNT = 81
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 4
REQUEST_SLEEP_SECONDS = 0.12
USER_AGENT = "edge-factory-orderbook-um-availability-audit-v1"

MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.csv"
MANIFEST_JSONL = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.jsonl"
COVERAGE_JSON = OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.json"
COVERAGE_MD = OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.md"
OPTIONAL_ALIGNMENT_CSV = OUTPUTS_DIR / "orderbook_um_optional_alignment_manifest.csv"
OPTIONAL_ALIGNMENT_JSONL = OUTPUTS_DIR / "orderbook_um_optional_alignment_manifest.jsonl"
BLOCKED_UNIVERSE_MD = OUTPUTS_DIR / "orderbook_um_missing_symbol_universe_BLOCKED.md"

UNIVERSE_CANDIDATE_PATHS = [
    "artifacts/panel_build_manifests/binance_okx_overlap_81_symbol_15m_panel_build_manifest_v1.json",
    "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
    "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
    "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
]

MANIFEST_COLUMNS = [
    "symbol",
    "data_type",
    "frequency",
    "file_date_or_month",
    "file_name",
    "url",
    "checksum_url",
    "size_bytes",
    "last_modified",
    "earliest_for_symbol",
    "latest_for_symbol",
    "local_target_path",
    "status",
    "error_message",
]


class AuditBlocked(RuntimeError):
    """Raised when the audit must stop closed."""


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def data_root() -> Path:
    root = Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()
    return root


def ensure_external_data_dirs(root: Path) -> dict[str, str]:
    if path_is_inside(root, REPO_ROOT):
        raise AuditBlocked(f"data root resolves inside repo: {root}")
    subdirs = {
        "raw": root / "binance_um_orderbook_raw",
        "manifest": root / "binance_um_orderbook_manifest",
        "pilot": root / "binance_um_orderbook_pilot",
        "logs": root / "binance_um_orderbook_logs",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return {key: str(value) for key, value in subdirs.items()}


def symbol_list_from_value(value: Any) -> list[str] | None:
    if isinstance(value, dict):
        preferred_keys = (
            "symbols",
            "exact_overlap_binance_symbols",
            "recommended_second_source_symbol_set",
            "symbol_set",
        )
        for key in preferred_keys:
            child = value.get(key)
            found = symbol_list_from_value(child)
            if found:
                return found
        for child in value.values():
            found = symbol_list_from_value(child)
            if found:
                return found
    if isinstance(value, list):
        if len(value) == EXPECTED_SYMBOL_COUNT and all(
            isinstance(item, str) and re.fullmatch(r"[A-Z0-9]+USDT", item) for item in value
        ):
            return list(value)
        for child in value:
            found = symbol_list_from_value(child)
            if found:
                return found
    return None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_symbol_universe() -> tuple[list[str], str]:
    for relative in UNIVERSE_CANDIDATE_PATHS:
        path = REPO_ROOT / relative
        if not path.exists():
            continue
        payload = load_json(path)
        symbols = symbol_list_from_value(payload)
        if symbols and len(symbols) == EXPECTED_SYMBOL_COUNT:
            unique = sorted(set(symbols))
            if len(unique) != EXPECTED_SYMBOL_COUNT:
                raise AuditBlocked(f"symbol universe contains duplicates in {relative}")
            return unique, relative

    search_roots = [REPO_ROOT / "outputs", REPO_ROOT / "artifacts"]
    name_tokens = ("81", "overlap", "binance", "okx", "source", "panel", "universe")
    for root in search_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.json")):
            lowered = path.as_posix().lower()
            if not any(token in lowered for token in name_tokens):
                continue
            try:
                payload = load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            symbols = symbol_list_from_value(payload)
            if symbols and len(set(symbols)) == EXPECTED_SYMBOL_COUNT:
                return sorted(set(symbols)), path.relative_to(REPO_ROOT).as_posix()

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    BLOCKED_UNIVERSE_MD.write_text(
        "\n".join(
            [
                "# BLOCKED_MISSING_81_SYMBOL_UNIVERSE",
                "",
                f"created_at_utc: {utc_now_text()}",
                "",
                "The required 81-symbol Binance/OKX overlap universe could not be found in repo outputs/artifacts.",
                "replacement_checks_all_true=false",
                "next_module=ORDERBOOK_UM_SYMBOL_UNIVERSE_BLOCKER_REVIEW",
                "",
            ]
        ),
        encoding="utf-8",
    )
    raise AuditBlocked("BLOCKED_MISSING_81_SYMBOL_UNIVERSE")


def assert_public_archive_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in PUBLIC_ARCHIVE_HOSTS:
        raise AuditBlocked(f"blocked non-public Binance archive URL: {url}")
    if parsed.netloc == "data.binance.vision":
        query = urllib.parse.parse_qs(parsed.query)
        prefix = (query.get("prefix") or [""])[0]
        portal_listing = parsed.path == "/" and prefix.startswith("data/futures/um/")
        archive_file = parsed.path.startswith("/data/futures/um/")
        if not (portal_listing or archive_file):
            raise AuditBlocked(f"blocked non-USD-M archive URL: {url}")


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
    return rows, token


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
        url = s3_listing_url(prefix, token)
        status, body, headers = request_text(url)
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


def archive_prefix(data_type: str, frequency: str, symbol: str, interval: str | None = None) -> str:
    if data_type == "bookDepth":
        return f"data/futures/um/{frequency}/bookDepth/{symbol}/"
    if data_type == "aggTrades":
        return f"data/futures/um/{frequency}/aggTrades/{symbol}/"
    if data_type == "klines":
        if not interval:
            raise ValueError("klines prefix requires interval")
        return f"data/futures/um/{frequency}/klines/{symbol}/{interval}/"
    raise ValueError(f"unsupported data_type: {data_type}")


def archive_url_from_key(key: str) -> str:
    return f"https://data.binance.vision/{key}"


def target_path_for(data_root_path: Path, row: dict[str, Any]) -> str:
    data_type = row["data_type"]
    frequency = row["frequency"]
    symbol = row["symbol"]
    name = row["file_name"]
    if data_type == "bookDepth":
        return str(data_root_path / "binance_um_orderbook_raw" / data_type / frequency / symbol / name)
    return str(data_root_path / "binance_um_orderbook_manifest" / "optional_alignment" / data_type / frequency / symbol / name)


def extract_period(data_type: str, frequency: str, file_name: str) -> str | None:
    if data_type == "bookDepth":
        daily = re.search(r"-bookDepth-(\d{4}-\d{2}-\d{2})\.zip$", file_name)
        monthly = re.search(r"-bookDepth-(\d{4}-\d{2})\.zip$", file_name)
    elif data_type == "aggTrades":
        daily = re.search(r"-aggTrades-(\d{4}-\d{2}-\d{2})\.zip$", file_name)
        monthly = re.search(r"-aggTrades-(\d{4}-\d{2})\.zip$", file_name)
    else:
        daily = re.search(r"-\d+[mhdwM]?-(\d{4}-\d{2}-\d{2})\.zip$", file_name)
        monthly = re.search(r"-\d+[mhdwM]?-(\d{4}-\d{2})\.zip$", file_name)
    if frequency == "daily":
        return daily.group(1) if daily else None
    return monthly.group(1) if monthly else None


def checksum_key_set(listing_rows: list[dict[str, Any]]) -> set[str]:
    return {row["key"] for row in listing_rows if row["key"].endswith(".CHECKSUM")}


def build_rows_for_prefix(
    data_root_path: Path,
    symbol: str,
    data_type: str,
    frequency: str,
    interval: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    prefix = archive_prefix(data_type, frequency, symbol, interval=interval)
    listing_rows, error = list_archive_prefix(prefix)
    checksums = checksum_key_set(listing_rows)
    archive_rows = [
        row for row in listing_rows if row["key"].endswith(".zip") and not row["key"].endswith(".zip.CHECKSUM")
    ]
    parsed_rows: list[dict[str, Any]] = []
    for raw in sorted(archive_rows, key=lambda item: item["key"]):
        file_name = raw["key"].rsplit("/", 1)[-1]
        period = extract_period(data_type, frequency, file_name)
        if not period:
            continue
        checksum_key = raw["key"] + ".CHECKSUM"
        row = {
            "symbol": symbol,
            "data_type": data_type,
            "frequency": frequency if data_type != "klines" else f"{frequency}_1m",
            "file_date_or_month": period,
            "file_name": file_name,
            "url": archive_url_from_key(raw["key"]),
            "checksum_url": archive_url_from_key(checksum_key) if checksum_key in checksums else "",
            "size_bytes": raw.get("size_bytes"),
            "last_modified": raw.get("last_modified") or "",
            "earliest_for_symbol": "",
            "latest_for_symbol": "",
            "local_target_path": "",
            "status": "AVAILABLE",
            "error_message": "",
        }
        row["local_target_path"] = target_path_for(data_root_path, row)
        parsed_rows.append(row)
    return parsed_rows, error


def add_missing_symbol_row(data_root_path: Path, symbol: str, error_message: str) -> dict[str, Any]:
    row = {
        "symbol": symbol,
        "data_type": "bookDepth",
        "frequency": "daily",
        "file_date_or_month": "",
        "file_name": "",
        "url": "",
        "checksum_url": "",
        "size_bytes": "",
        "last_modified": "",
        "earliest_for_symbol": "",
        "latest_for_symbol": "",
        "local_target_path": str(data_root_path / "binance_um_orderbook_raw" / "bookDepth" / "daily" / symbol),
        "status": "MISSING_OR_EMPTY",
        "error_message": error_message,
    }
    return row


def write_rows_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
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


def summarize(rows: list[dict[str, Any]], symbols: list[str], universe_source: str, data_dirs: dict[str, str]) -> dict[str, Any]:
    available_rows = [row for row in rows if row["status"] == "AVAILABLE"]
    by_symbol: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in symbols}
    for row in available_rows:
        by_symbol.setdefault(row["symbol"], []).append(row)
    missing = [symbol for symbol in symbols if not by_symbol.get(symbol)]
    totals_by_symbol: list[dict[str, Any]] = []
    partial: list[str] = []
    for symbol in symbols:
        symbol_rows = by_symbol.get(symbol, [])
        estimated = sum(int(row["size_bytes"] or 0) for row in symbol_rows)
        dates = [row["file_date_or_month"] for row in symbol_rows if re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["file_date_or_month"])]
        if dates and min(dates) > "2023-01-01":
            partial.append(symbol)
        totals_by_symbol.append({"symbol": symbol, "file_count": len(symbol_rows), "estimated_size_bytes": estimated})
    total_size = sum(item["estimated_size_bytes"] for item in totals_by_symbol)
    all_dates = [
        row["file_date_or_month"]
        for row in available_rows
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["file_date_or_month"])
    ]
    size_known_count = sum(1 for row in available_rows if row.get("size_bytes") not in ("", None))
    full_download_safe = total_size > 0 and total_size < 250 * 1024 * 1024 * 1024 and len(missing) == 0
    return {
        "status": "PASS_ORDERBOOK_UM_AVAILABILITY_AUDIT_CREATED",
        "created_at_utc": utc_now_text(),
        "universe_source": universe_source,
        "symbol_count_requested": len(symbols),
        "symbol_count_found": len(symbols) - len(missing),
        "symbol_count_missing": len(missing),
        "total_file_count": len(available_rows),
        "total_estimated_size_bytes": total_size,
        "total_estimated_size_gb": round(total_size / 1_000_000_000, 6),
        "size_known_file_count": size_known_count,
        "earliest_global_date": min(all_dates) if all_dates else None,
        "latest_global_date": max(all_dates) if all_dates else None,
        "top_20_largest_symbols_by_estimated_size": sorted(
            totals_by_symbol, key=lambda item: item["estimated_size_bytes"], reverse=True
        )[:20],
        "missing_symbols": missing,
        "symbols_with_partial_coverage": sorted(set(partial)),
        "recommended_next_action": "Run the manifest validator, then run the safe pilot downloader only.",
        "full_historical_download_safe_or_too_large": "LOCKED_AND_REQUIRES_EXPLICIT_SIZE_REVIEW",
        "full_historical_download_safe": full_download_safe,
        "data_root": str(data_root()),
        "external_data_dirs": data_dirs,
        "manifest_csv": str(MANIFEST_CSV),
        "manifest_jsonl": str(MANIFEST_JSONL),
        "optional_alignment_manifest_csv": str(OPTIONAL_ALIGNMENT_CSV),
        "replacement_checks_all_true": True,
        "next_module": "ORDERBOOK_UM_MANIFEST_VALIDATOR_V1",
    }


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Binance USD-M bookDepth availability summary v1",
        "",
        f"status: {summary['status']}",
        f"created_at_utc: {summary['created_at_utc']}",
        f"universe_source: {summary['universe_source']}",
        f"symbol_count_requested: {summary['symbol_count_requested']}",
        f"symbol_count_found: {summary['symbol_count_found']}",
        f"symbol_count_missing: {summary['symbol_count_missing']}",
        f"total_file_count: {summary['total_file_count']}",
        f"total_estimated_size_gb: {summary['total_estimated_size_gb']}",
        f"earliest_global_date: {summary['earliest_global_date']}",
        f"latest_global_date: {summary['latest_global_date']}",
        f"full_historical_download_safe_or_too_large: {summary['full_historical_download_safe_or_too_large']}",
        "",
        "## Missing symbols",
    ]
    lines.extend(f"- {symbol}" for symbol in summary["missing_symbols"])
    if not summary["missing_symbols"]:
        lines.append("- none")
    lines.extend(["", "## Top 20 largest symbols by estimated size"])
    for item in summary["top_20_largest_symbols_by_estimated_size"]:
        gb = item["estimated_size_bytes"] / 1_000_000_000
        lines.append(f"- {item['symbol']}: {item['file_count']} files, {gb:.6f} GB")
    lines.extend(
        [
            "",
            "## Next safe step",
            summary["recommended_next_action"],
            "",
            "replacement_checks_all_true=true",
            f"next_module={summary['next_module']}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def add_symbol_extents(rows: list[dict[str, Any]]) -> None:
    by_symbol: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["status"] == "AVAILABLE":
            by_symbol.setdefault(row["symbol"], []).append(row)
    for symbol_rows in by_symbol.values():
        periods = [row["file_date_or_month"] for row in symbol_rows if row["file_date_or_month"]]
        earliest = min(periods) if periods else ""
        latest = max(periods) if periods else ""
        for row in symbol_rows:
            row["earliest_for_symbol"] = earliest
            row["latest_for_symbol"] = latest


def selected_pilot_bookdepth_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    available = [row for row in rows if row.get("status") == "AVAILABLE" and row.get("url")]
    by_symbol: dict[str, list[dict[str, Any]]] = {}
    for row in available:
        by_symbol.setdefault(row["symbol"], []).append(row)
    for symbol_rows in by_symbol.values():
        symbol_rows.sort(key=lambda row: row["file_date_or_month"])
    selected: list[dict[str, Any]] = []
    if by_symbol.get("BTCUSDT"):
        selected.append(by_symbol["BTCUSDT"][0])
        selected.append(by_symbol["BTCUSDT"][-1])
    for symbol in ["ETHUSDT", "SOLUSDT"]:
        if by_symbol.get(symbol):
            selected.append(by_symbol[symbol][-1])
    if len(selected) >= 3:
        dedup = {row["url"]: row for row in selected}
        return list(dedup.values())
    liquid_order = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "LINKUSDT"]
    fallback = [symbol for symbol in liquid_order if by_symbol.get(symbol)]
    if len(fallback) < 3:
        fallback = sorted(symbol for symbol, symbol_rows in by_symbol.items() if symbol_rows)[:3]
    return [by_symbol[symbol][-1] for symbol in fallback[:3]]


def build_optional_alignment_rows(data_root_path: Path, bookdepth_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = selected_pilot_bookdepth_rows(bookdepth_rows)
    desired: dict[str, set[str]] = {}
    for row in selected:
        desired.setdefault(row["symbol"], set()).add(row["file_date_or_month"])
    optional_rows: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for symbol, dates in sorted(desired.items()):
        for data_type, interval in [("aggTrades", None), ("klines", "1m")]:
            prefix_rows, _error = build_rows_for_prefix(data_root_path, symbol, data_type, "daily", interval=interval)
            for row in prefix_rows:
                if row["file_date_or_month"] not in dates or row["url"] in seen_urls:
                    continue
                seen_urls.add(row["url"])
                optional_rows.append(row)
    return optional_rows


def main() -> int:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        symbols, universe_source = find_symbol_universe()
        root = data_root()
        data_dirs = ensure_external_data_dirs(root)
        rows: list[dict[str, Any]] = []
        monthly_probe: dict[str, Any] = {}
        for index, symbol in enumerate(symbols, start=1):
            print(f"probe {index}/{len(symbols)} {symbol}", flush=True)
            daily_rows, daily_error = build_rows_for_prefix(root, symbol, "bookDepth", "daily")
            monthly_rows, monthly_error = build_rows_for_prefix(root, symbol, "bookDepth", "monthly")
            monthly_probe[symbol] = {
                "available": bool(monthly_rows),
                "file_count": len(monthly_rows),
                "error_message": monthly_error,
            }
            if daily_rows:
                rows.extend(daily_rows)
            else:
                rows.append(add_missing_symbol_row(root, symbol, daily_error or "no daily bookDepth zip files found"))

        add_symbol_extents(rows)
        optional_rows = build_optional_alignment_rows(root, rows)
        write_rows_csv(MANIFEST_CSV, rows, MANIFEST_COLUMNS)
        write_jsonl(MANIFEST_JSONL, rows)
        write_rows_csv(OPTIONAL_ALIGNMENT_CSV, optional_rows, MANIFEST_COLUMNS)
        write_jsonl(OPTIONAL_ALIGNMENT_JSONL, optional_rows)
        summary = summarize(rows, symbols, universe_source, data_dirs)
        summary["monthly_bookdepth_probe"] = monthly_probe
        json_dump(COVERAGE_JSON, summary)
        write_summary_md(COVERAGE_MD, summary)
        manifest_copy = Path(data_dirs["manifest"]) / MANIFEST_CSV.name
        write_rows_csv(manifest_copy, rows, MANIFEST_COLUMNS)
        print(f"status: {summary['status']}")
        print(f"81_symbol_universe_found: true")
        print(f"manifest_csv: {MANIFEST_CSV}")
        print(f"coverage_summary_json: {COVERAGE_JSON}")
        print(f"total_estimated_size_gb: {summary['total_estimated_size_gb']}")
        print(f"earliest_global_date: {summary['earliest_global_date']}")
        print(f"missing_symbols_count: {summary['symbol_count_missing']}")
        print("replacement_checks_all_true: true")
        return 0
    except AuditBlocked as exc:
        print(f"BLOCKED / APPROVAL_REQUIRED: {exc}")
        print("replacement_checks_all_true=false")
        print("next_module=ORDERBOOK_UM_APPROVAL_OR_BLOCKER_REVIEW")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
