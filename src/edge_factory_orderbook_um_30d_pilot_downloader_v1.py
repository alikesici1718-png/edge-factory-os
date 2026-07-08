#!/usr/bin/env python
"""Download only manifest-listed BTC/ETH/SOL 30-day bookDepth and aggTrades pilot ZIPs."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest.csv"
MANIFEST_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest_summary.json"
DOWNLOAD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_download_summary.json"
DOWNLOAD_SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_30d_pilot_download_summary.md"
PUBLIC_ARCHIVE_HOST = "data.binance.vision"
REQUEST_TIMEOUT_SECONDS = 90
REQUEST_SLEEP_SECONDS = 0.06
MAX_RETRIES = 4
USER_AGENT = "edge-factory-orderbook-um-30d-pilot-downloader-v1"
TARGET_SYMBOLS = {"BTCUSDT", "ETHUSDT", "SOLUSDT"}


class DownloadBlocked(RuntimeError):
    """Raised when the 30-day pilot download must stop closed."""


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
        raise DownloadBlocked(f"data root resolves inside repo: {root}")
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
        raise DownloadBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DownloadBlocked(f"input is not a JSON object: {path}")
    return payload


def assert_public_archive_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_ARCHIVE_HOST:
        raise DownloadBlocked(f"blocked non-public archive URL: {url}")
    if not parsed.path.startswith("/data/futures/um/daily/"):
        raise DownloadBlocked(f"blocked non-USD-M daily archive URL: {url}")
    if "/bookDepth/" not in parsed.path and "/aggTrades/" not in parsed.path:
        raise DownloadBlocked(f"blocked unsupported archive type: {url}")


def request_text(url: str, max_bytes: int = 4096) -> str:
    assert_public_archive_url(url)
    last_error = ""
    for attempt in range(MAX_RETRIES):
        if attempt:
            time.sleep(min(2.0 * attempt, 8.0))
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise DownloadBlocked(f"checksum response exceeded byte cap for {url}")
                time.sleep(REQUEST_SLEEP_SECONDS)
                return body.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code == 404:
                return ""
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
    raise DownloadBlocked(f"checksum download failed for {url}: {last_error or 'unknown error'}")


def download_stream(url: str, target: Path) -> int:
    assert_public_archive_url(url)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    last_error = ""
    for attempt in range(MAX_RETRIES):
        if attempt:
            time.sleep(min(2.0 * attempt, 8.0))
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response, tmp.open("wb") as handle:
                shutil.copyfileobj(response, handle, length=1024 * 1024)
            tmp.replace(target)
            time.sleep(REQUEST_SLEEP_SECONDS)
            return target.stat().st_size
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
    raise DownloadBlocked(f"ZIP download failed for {url}: {last_error or 'unknown error'}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_checksum(text: str) -> str | None:
    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST_CSV.exists():
        raise DownloadBlocked(f"missing required manifest: {MANIFEST_CSV}")
    rows: list[dict[str, str]] = []
    with MANIFEST_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "symbol",
            "file_date",
            "bookdepth_url",
            "bookdepth_checksum_url",
            "bookdepth_local_zip_path",
            "bookdepth_local_checksum_path",
            "aggtrades_url",
            "aggtrades_checksum_url",
            "aggtrades_local_zip_path",
            "aggtrades_local_checksum_path",
            "status",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise DownloadBlocked(f"30d manifest missing columns: {sorted(missing)}")
        for row in reader:
            rows.append(row)
    symbols = {row["symbol"] for row in rows}
    if symbols != TARGET_SYMBOLS:
        raise DownloadBlocked(f"manifest symbols are not exactly BTCUSDT/ETHUSDT/SOLUSDT: {sorted(symbols)}")
    if len(rows) != 90:
        raise DownloadBlocked(f"manifest row count is not 90: {len(rows)}")
    incomplete = [f"{row['symbol']}|{row['file_date']}|{row['status']}" for row in rows if row.get("status") != "AVAILABLE"]
    if incomplete:
        raise DownloadBlocked(f"manifest is incomplete; refusing download: {incomplete[:20]}")
    return rows


def verify_path_external(path: Path) -> None:
    if path_is_inside(path, REPO_ROOT):
        raise DownloadBlocked(f"download target resolves inside repo: {path}")


def download_asset(symbol: str, day: str, asset_type: str, url: str, checksum_url: str, zip_path: Path, checksum_path: Path) -> dict[str, Any]:
    verify_path_external(zip_path)
    verify_path_external(checksum_path)
    expected_sha = None
    checksum_available = bool(checksum_url)
    checksum_text = ""
    if checksum_available:
        checksum_text = request_text(checksum_url)
        expected_sha = parse_checksum(checksum_text)
        if not expected_sha:
            raise DownloadBlocked(f"checksum file did not contain sha256 for {asset_type} {symbol} {day}")
        checksum_path.parent.mkdir(parents=True, exist_ok=True)
        checksum_path.write_text(checksum_text, encoding="utf-8")
    skipped_existing = False
    if zip_path.exists() and expected_sha and sha256_file(zip_path) == expected_sha:
        skipped_existing = True
    else:
        download_stream(url, zip_path)
    observed_sha = sha256_file(zip_path)
    checksum_verified = None
    if expected_sha:
        checksum_verified = observed_sha == expected_sha
        if not checksum_verified:
            raise DownloadBlocked(f"checksum mismatch for {asset_type} {symbol} {day}: {observed_sha} != {expected_sha}")
    return {
        "symbol": symbol,
        "file_date": day,
        "asset_type": asset_type,
        "url": url,
        "checksum_url": checksum_url,
        "local_zip_path": str(zip_path),
        "local_checksum_path": str(checksum_path) if checksum_available else "",
        "bytes": zip_path.stat().st_size,
        "checksum_available": checksum_available,
        "checksum_verified": checksum_verified,
        "skipped_existing": skipped_existing,
        "status": "VERIFIED" if checksum_verified is True else "DOWNLOADED_NO_CHECKSUM",
    }


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d pilot download summary v1",
        "",
        f"status: {summary['status']}",
        f"downloaded_or_verified_file_count: {summary['downloaded_or_verified_file_count']}",
        f"checksum_verified_file_count: {summary['checksum_verified_file_count']}",
        f"bookdepth_file_count: {summary['bookdepth_file_count']}",
        f"aggtrades_file_count: {summary['aggtrades_file_count']}",
        f"downloaded_bytes_gb: {summary['downloaded_bytes_gb']}",
        f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}",
        "",
        "## Notes",
        "- Raw ZIP files are stored outside the git repo under the configured external data root.",
        "- Existing files are skipped only after checksum verification.",
        "",
    ]
    DOWNLOAD_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_blocked(reason: str) -> int:
    payload = {
        "status": "BLOCKED_ORDERBOOK_UM_30D_PILOT_DOWNLOAD",
        "created_at_utc": utc_now_text(),
        "exact_blocker": reason,
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_30D_DOWNLOAD_BLOCKER_REVIEW",
        "full_81_symbol_download_attempted": False,
    }
    DOWNLOAD_SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_summary_md({**payload, "downloaded_or_verified_file_count": 0, "checksum_verified_file_count": 0, "bookdepth_file_count": 0, "aggtrades_file_count": 0, "downloaded_bytes_gb": 0})
    print(f"BLOCKED: {reason}")
    print("replacement_checks_all_true=false")
    return 2


def main() -> int:
    try:
        dirs = external_dirs()
        manifest_summary = load_json(MANIFEST_SUMMARY_JSON)
        if manifest_summary.get("manifest_complete") is not True:
            raise DownloadBlocked("manifest summary is not complete")
        rows = read_manifest()
        downloads: list[dict[str, Any]] = []
        for row in rows:
            symbol = row["symbol"]
            day = row["file_date"]
            downloads.append(
                download_asset(
                    symbol,
                    day,
                    "bookDepth",
                    row["bookdepth_url"],
                    row["bookdepth_checksum_url"],
                    Path(row["bookdepth_local_zip_path"]),
                    Path(row["bookdepth_local_checksum_path"]),
                )
            )
            downloads.append(
                download_asset(
                    symbol,
                    day,
                    "aggTrades",
                    row["aggtrades_url"],
                    row["aggtrades_checksum_url"],
                    Path(row["aggtrades_local_zip_path"]),
                    Path(row["aggtrades_local_checksum_path"]),
                )
            )
        verified_count = sum(1 for item in downloads if item.get("checksum_verified") is True)
        bookdepth_count = sum(1 for item in downloads if item["asset_type"] == "bookDepth")
        aggtrades_count = sum(1 for item in downloads if item["asset_type"] == "aggTrades")
        summary = {
            "status": "PASS_ORDERBOOK_UM_30D_PILOT_DOWNLOAD_COMPLETE",
            "created_at_utc": utc_now_text(),
            "task_name": "ORDERBOOK_UM_BTC_ETH_SOL_30D_ABSORPTION_PILOT_V1",
            "data_root": str(data_root()),
            "external_data_dirs": {key: str(value) for key, value in dirs.items()},
            "manifest_csv": str(MANIFEST_CSV),
            "selected_start_date": manifest_summary.get("selected_start_date"),
            "selected_end_date": manifest_summary.get("selected_end_date"),
            "selected_symbols": sorted(TARGET_SYMBOLS),
            "downloaded_or_verified_file_count": len(downloads),
            "checksum_verified_file_count": verified_count,
            "bookdepth_file_count": bookdepth_count,
            "aggtrades_file_count": aggtrades_count,
            "downloaded_bytes": sum(int(item.get("bytes") or 0) for item in downloads),
            "downloaded_bytes_gb": round(sum(int(item.get("bytes") or 0) for item in downloads) / (1024**3), 6),
            "downloads": downloads,
            "download_log_path": str(dirs["logs"] / "orderbook_um_30d_pilot_download_log.jsonl"),
            "full_81_symbol_download_attempted": False,
            "replacement_checks_all_true": verified_count == len(downloads),
            "next_module": "ORDERBOOK_UM_30D_ABSORPTION_PREVIEW" if verified_count == len(downloads) else "ORDERBOOK_UM_30D_DOWNLOAD_BLOCKER_REVIEW",
        }
        log_path = Path(summary["download_log_path"])
        with log_path.open("w", encoding="utf-8") as handle:
            for item in downloads:
                handle.write(json.dumps(item, sort_keys=True, ensure_ascii=True) + "\n")
        DOWNLOAD_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_summary_md(summary)
        print(f"status: {summary['status']}")
        print(f"downloaded_or_verified_file_count: {summary['downloaded_or_verified_file_count']}")
        print(f"checksum_verified_file_count: {summary['checksum_verified_file_count']}")
        print(f"download_summary_json: {DOWNLOAD_SUMMARY_JSON}")
        print(f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}")
        return 0 if summary["replacement_checks_all_true"] else 2
    except DownloadBlocked as exc:
        return write_blocked(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
