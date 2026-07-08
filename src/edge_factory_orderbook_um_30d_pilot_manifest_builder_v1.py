#!/usr/bin/env python
"""Build the BTC/ETH/SOL 30-day Binance USD-M bookDepth plus aggTrades pilot manifest."""

from __future__ import annotations

import csv
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
BOOKDEPTH_AVAILABILITY_MANIFEST = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.csv"
COVERAGE_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.json"
MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest.csv"
MANIFEST_JSONL = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest.jsonl"
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest_summary.md"

PUBLIC_ARCHIVE_HOST = "data.binance.vision"
TARGET_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
DAY_COUNT = 30
REQUEST_TIMEOUT_SECONDS = 40
REQUEST_SLEEP_SECONDS = 0.08
MAX_RETRIES = 3
USER_AGENT = "edge-factory-orderbook-um-30d-pilot-manifest-builder-v1"


class ManifestBlocked(RuntimeError):
    """Raised when the 30-day pilot manifest cannot be safely built."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def external_dirs() -> dict[str, Path]:
    root = data_root()
    if path_is_inside(root, REPO_ROOT):
        raise ManifestBlocked(f"data root resolves inside repo: {root}")
    dirs = {
        "bookdepth": root / "binance_um_30d_bookdepth_pilot",
        "aggtrades": root / "binance_um_30d_aggtrades_pilot",
        "work": root / "binance_um_30d_absorption_work",
        "logs": root / "binance_um_30d_absorption_logs",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    return dirs


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ManifestBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ManifestBlocked(f"input is not a JSON object: {path}")
    return payload


def assert_public_archive_url(url: str, expected_type: str | None = None) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_ARCHIVE_HOST:
        raise ManifestBlocked(f"blocked non-public archive URL: {url}")
    if not parsed.path.startswith("/data/futures/um/daily/"):
        raise ManifestBlocked(f"blocked non-USD-M daily archive URL: {url}")
    if expected_type and f"/{expected_type}/" not in parsed.path:
        raise ManifestBlocked(f"blocked unexpected archive type for {expected_type}: {url}")


def head_url(url: str, expected_type: str | None = None) -> dict[str, Any]:
    assert_public_archive_url(url, expected_type)
    last_error = ""
    for attempt in range(MAX_RETRIES):
        if attempt:
            time.sleep(min(2.0 * attempt, 6.0))
        try:
            request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                headers = {key.lower(): value for key, value in response.headers.items()}
                time.sleep(REQUEST_SLEEP_SECONDS)
                return {
                    "available": True,
                    "status_code": int(getattr(response, "status", 200)),
                    "size_bytes": int(headers["content-length"]) if headers.get("content-length", "").isdigit() else None,
                    "last_modified": headers.get("last-modified", ""),
                    "error_message": "",
                }
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return {
                    "available": False,
                    "status_code": 404,
                    "size_bytes": None,
                    "last_modified": "",
                    "error_message": "HTTP 404",
                }
            last_error = f"HTTP {exc.code}"
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
    return {
        "available": False,
        "status_code": None,
        "size_bytes": None,
        "last_modified": "",
        "error_message": last_error or "unknown HEAD error",
    }


def parse_day(raw: str) -> date | None:
    try:
        return datetime.strptime(str(raw), "%Y-%m-%d").date()
    except ValueError:
        return None


def read_bookdepth_rows() -> dict[tuple[str, str], dict[str, str]]:
    if not BOOKDEPTH_AVAILABILITY_MANIFEST.exists():
        raise ManifestBlocked(f"missing required manifest: {BOOKDEPTH_AVAILABILITY_MANIFEST}")
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with BOOKDEPTH_AVAILABILITY_MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"symbol", "file_date_or_month", "url", "checksum_url", "status", "size_bytes", "last_modified"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ManifestBlocked(f"bookDepth manifest missing columns: {sorted(missing)}")
        for row in reader:
            symbol = str(row.get("symbol", ""))
            day = str(row.get("file_date_or_month", ""))
            if symbol in TARGET_SYMBOLS and row.get("status") == "AVAILABLE" and parse_day(day):
                rows[(symbol, day)] = row
    return rows


def latest_common_complete_day(bookdepth_rows: dict[tuple[str, str], dict[str, str]]) -> date:
    per_symbol: dict[str, set[date]] = {symbol: set() for symbol in TARGET_SYMBOLS}
    for symbol, day_text in bookdepth_rows:
        day = parse_day(day_text)
        if day:
            per_symbol[symbol].add(day)
    if any(not days for days in per_symbol.values()):
        raise ManifestBlocked("one or more target symbols have no bookDepth availability rows")
    common = set.intersection(*(per_symbol[symbol] for symbol in TARGET_SYMBOLS))
    latest_allowed = datetime.now(timezone.utc).date() - timedelta(days=1)
    common = {day for day in common if day <= latest_allowed}
    if not common:
        raise ManifestBlocked("latest common complete date could not be resolved")
    return max(common)


def selected_window(end_day: date, bookdepth_rows: dict[tuple[str, str], dict[str, str]]) -> list[date]:
    days = [end_day - timedelta(days=offset) for offset in reversed(range(DAY_COUNT))]
    missing = []
    for symbol in TARGET_SYMBOLS:
        for day in days:
            if (symbol, day.isoformat()) not in bookdepth_rows:
                missing.append(f"{symbol}|{day.isoformat()}")
    if missing:
        raise ManifestBlocked(f"30-calendar-day common bookDepth window is incomplete: {missing[:20]}")
    return days


def aggtrades_url(symbol: str, day: str) -> str:
    return f"https://data.binance.vision/data/futures/um/daily/aggTrades/{symbol}/{symbol}-aggTrades-{day}.zip"


def checksum_url(url: str) -> str:
    return url + ".CHECKSUM"


def bookdepth_local_zip(dirs: dict[str, Path], symbol: str, day: str) -> Path:
    return dirs["bookdepth"] / symbol / f"{symbol}-bookDepth-{day}.zip"


def aggtrades_local_zip(dirs: dict[str, Path], symbol: str, day: str) -> Path:
    return dirs["aggtrades"] / symbol / f"{symbol}-aggTrades-{day}.zip"


def build_rows(days: list[date], bookdepth_rows: dict[tuple[str, str], dict[str, str]], dirs: dict[str, Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for symbol in TARGET_SYMBOLS:
        for day in days:
            day_text = day.isoformat()
            bookdepth = bookdepth_rows.get((symbol, day_text))
            if not bookdepth:
                rows.append(
                    {
                        "symbol": symbol,
                        "file_date": day_text,
                        "bookdepth_status": "MISSING",
                        "aggtrades_status": "NOT_PROBED",
                        "status": "MISSING_BOOKDEPTH",
                        "error_message": "bookDepth file missing from availability manifest",
                    }
                )
                continue
            bd_url = str(bookdepth["url"])
            bd_checksum = str(bookdepth.get("checksum_url", ""))
            agg_url = aggtrades_url(symbol, day_text)
            agg_head = head_url(agg_url, "aggTrades")
            agg_checksum_head = head_url(checksum_url(agg_url), "aggTrades")
            bd_size = int(bookdepth["size_bytes"]) if str(bookdepth.get("size_bytes", "")).isdigit() else None
            agg_size = agg_head["size_bytes"]
            agg_available = bool(agg_head["available"])
            checksum_available = bool(agg_checksum_head["available"])
            row = {
                "symbol": symbol,
                "file_date": day_text,
                "bookdepth_url": bd_url,
                "bookdepth_checksum_url": bd_checksum,
                "bookdepth_size_bytes": bd_size,
                "bookdepth_last_modified": bookdepth.get("last_modified", ""),
                "bookdepth_local_zip_path": str(bookdepth_local_zip(dirs, symbol, day_text)),
                "bookdepth_local_checksum_path": str(bookdepth_local_zip(dirs, symbol, day_text).with_name(f"{symbol}-bookDepth-{day_text}.zip.CHECKSUM")),
                "bookdepth_status": "AVAILABLE",
                "aggtrades_url": agg_url,
                "aggtrades_checksum_url": checksum_url(agg_url) if checksum_available else "",
                "aggtrades_size_bytes": agg_size,
                "aggtrades_last_modified": agg_head["last_modified"],
                "aggtrades_local_zip_path": str(aggtrades_local_zip(dirs, symbol, day_text)),
                "aggtrades_local_checksum_path": str(aggtrades_local_zip(dirs, symbol, day_text).with_name(f"{symbol}-aggTrades-{day_text}.zip.CHECKSUM")),
                "aggtrades_status": "AVAILABLE" if agg_available else "MISSING",
                "status": "AVAILABLE" if agg_available else "MISSING_AGGTRADES",
                "error_message": "" if agg_available else agg_head["error_message"],
            }
            rows.append(row)
    return rows


FIELDNAMES = [
    "symbol",
    "file_date",
    "bookdepth_url",
    "bookdepth_checksum_url",
    "bookdepth_size_bytes",
    "bookdepth_last_modified",
    "bookdepth_local_zip_path",
    "bookdepth_local_checksum_path",
    "bookdepth_status",
    "aggtrades_url",
    "aggtrades_checksum_url",
    "aggtrades_size_bytes",
    "aggtrades_last_modified",
    "aggtrades_local_zip_path",
    "aggtrades_local_checksum_path",
    "aggtrades_status",
    "status",
    "error_message",
]


def write_manifest(rows: list[dict[str, Any]]) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "" if row.get(field) is None else row.get(field, "") for field in FIELDNAMES})
    with MANIFEST_JSONL.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d pilot manifest summary v1",
        "",
        f"status: {summary['status']}",
        f"selected_start_date: {summary.get('selected_start_date', '')}",
        f"selected_end_date: {summary.get('selected_end_date', '')}",
        f"selected_day_count: {summary.get('selected_day_count', '')}",
        f"manifest_complete: {summary.get('manifest_complete')}",
        f"estimated_download_size_gb: {summary.get('estimated_download_size_gb')}",
        f"recommended_next_action: {summary.get('recommended_next_action')}",
        "",
        "## Missing bookDepth files",
    ]
    missing_bd = summary.get("missing_bookdepth_files") or []
    lines.extend(f"- {item}" for item in missing_bd) if missing_bd else lines.append("- none")
    lines.extend(["", "## Missing aggTrades files"])
    missing_agg = summary.get("missing_aggtrades_files") or []
    lines.extend(f"- {item}" for item in missing_agg) if missing_agg else lines.append("- none")
    lines.extend(["", f"replacement_checks_all_true={str(summary.get('replacement_checks_all_true')).lower()}", ""])
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def build_summary(rows: list[dict[str, Any]], days: list[date], dirs: dict[str, Path], status: str) -> dict[str, Any]:
    missing_bookdepth = [f"{row['symbol']}|{row['file_date']}" for row in rows if row.get("bookdepth_status") != "AVAILABLE"]
    missing_aggtrades = [f"{row['symbol']}|{row['file_date']}" for row in rows if row.get("aggtrades_status") != "AVAILABLE"]
    bookdepth_size = sum(int(row.get("bookdepth_size_bytes") or 0) for row in rows)
    agg_size = sum(int(row.get("aggtrades_size_bytes") or 0) for row in rows)
    complete = not missing_bookdepth and not missing_aggtrades and len(rows) == len(TARGET_SYMBOLS) * DAY_COUNT
    return {
        "status": status if complete else "BLOCKED_ORDERBOOK_UM_30D_PILOT_MANIFEST_INCOMPLETE",
        "created_at_utc": utc_now_text(),
        "task_name": "ORDERBOOK_UM_BTC_ETH_SOL_30D_ABSORPTION_PILOT_V1",
        "data_root": str(data_root()),
        "external_data_dirs": {key: str(value) for key, value in dirs.items()},
        "selected_start_date": days[0].isoformat() if days else "",
        "selected_end_date": days[-1].isoformat() if days else "",
        "selected_day_count": len(days),
        "selected_symbols": TARGET_SYMBOLS,
        "expected_bookdepth_file_count": len(TARGET_SYMBOLS) * len(days),
        "expected_aggtrades_file_count": len(TARGET_SYMBOLS) * len(days),
        "manifest_row_count": len(rows),
        "missing_bookdepth_files": missing_bookdepth,
        "missing_aggtrades_files": missing_aggtrades,
        "estimated_bookdepth_size_bytes": bookdepth_size,
        "estimated_aggtrades_size_bytes": agg_size,
        "estimated_download_size_bytes": bookdepth_size + agg_size,
        "estimated_download_size_gb": round((bookdepth_size + agg_size) / (1024**3), 6),
        "manifest_complete": complete,
        "manifest_csv": str(MANIFEST_CSV),
        "manifest_jsonl": str(MANIFEST_JSONL),
        "recommended_next_action": "RUN_30D_PILOT_DOWNLOADER" if complete else "REVIEW_PARTIAL_COVERAGE_BEFORE_DOWNLOADING",
        "full_81_symbol_download_attempted": False,
        "replacement_checks_all_true": complete,
        "next_module": "ORDERBOOK_UM_30D_PILOT_DOWNLOADER" if complete else "ORDERBOOK_UM_30D_MANIFEST_BLOCKER_REVIEW",
    }


def write_blocked(reason: str) -> int:
    payload = {
        "status": "BLOCKED_ORDERBOOK_UM_30D_PILOT_MANIFEST",
        "created_at_utc": utc_now_text(),
        "exact_blocker": reason,
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_30D_MANIFEST_BLOCKER_REVIEW",
        "recommended_next_action": "STOP_REVIEW_BLOCKER",
    }
    SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_summary_md(payload)
    print(f"BLOCKED: {reason}")
    print("replacement_checks_all_true=false")
    return 2


def main() -> int:
    try:
        dirs = external_dirs()
        coverage = load_json(COVERAGE_SUMMARY_JSON)
        if coverage.get("symbol_count_missing") not in {0, "0"}:
            raise ManifestBlocked("coverage summary indicates missing symbols")
        bookdepth_rows = read_bookdepth_rows()
        end_day = latest_common_complete_day(bookdepth_rows)
        days = selected_window(end_day, bookdepth_rows)
        rows = build_rows(days, bookdepth_rows, dirs)
        write_manifest(rows)
        summary = build_summary(rows, days, dirs, "PASS_ORDERBOOK_UM_30D_PILOT_MANIFEST_CREATED")
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_summary_md(summary)
        print(f"status: {summary['status']}")
        print(f"selected_start_date: {summary['selected_start_date']}")
        print(f"selected_end_date: {summary['selected_end_date']}")
        print(f"manifest_complete: {str(summary['manifest_complete']).lower()}")
        print(f"estimated_download_size_gb: {summary['estimated_download_size_gb']}")
        print(f"manifest_csv: {MANIFEST_CSV}")
        print(f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}")
        return 0 if summary["replacement_checks_all_true"] else 2
    except ManifestBlocked as exc:
        return write_blocked(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
