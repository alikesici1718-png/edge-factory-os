#!/usr/bin/env python
"""Download only matching Binance USD-M aggTrades pilot ZIPs for absorption diagnostics."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
BOOKDEPTH_FEATURE_SUMMARY = OUTPUTS_DIR / "orderbook_um_pilot_feature_preview_summary.json"
SCHEMA_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_aggtrades_pilot_schema_summary.json"
SCHEMA_SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_aggtrades_pilot_schema_summary.md"
PUBLIC_ARCHIVE_HOST = "data.binance.vision"
REQUEST_TIMEOUT_SECONDS = 60
MAX_RETRIES = 4
REQUEST_SLEEP_SECONDS = 0.15
USER_AGENT = "edge-factory-orderbook-um-aggtrades-pilot-downloader-v1"

DEFAULT_NO_HEADER_COLUMNS = [
    "aggregate_trade_id",
    "price",
    "quantity",
    "first_trade_id",
    "last_trade_id",
    "timestamp",
    "is_buyer_maker",
    "is_best_match",
]


class DownloadBlocked(RuntimeError):
    """Raised when the pilot download must stop closed."""


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
        "aggtrades_pilot": root / "binance_um_aggtrades_pilot",
        "absorption_work": root / "binance_um_absorption_pilot_work",
        "logs": root / "binance_um_absorption_pilot_logs",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise DownloadBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DownloadBlocked(f"input is not a JSON object: {path}")
    return payload


def pilot_pairs_from_bookdepth_summary() -> list[dict[str, str]]:
    summary = load_json(BOOKDEPTH_FEATURE_SUMMARY)
    rows = summary.get("rows_parsed_per_symbol_day")
    if not isinstance(rows, dict) or not rows:
        raise DownloadBlocked("bookDepth feature summary has no rows_parsed_per_symbol_day")
    pairs: list[dict[str, str]] = []
    for key in sorted(rows):
        if "|" not in key:
            continue
        symbol, day = key.split("|", 1)
        pairs.append({"symbol": symbol, "date": day})
    required = {
        ("BTCUSDT", "2023-01-01"),
        ("BTCUSDT", "2026-06-15"),
        ("ETHUSDT", "2026-06-15"),
        ("SOLUSDT", "2026-06-15"),
    }
    observed = {(item["symbol"], item["date"]) for item in pairs}
    missing = sorted(required - observed)
    if missing:
        raise DownloadBlocked(f"bookDepth pilot summary missing required pilot pairs: {missing}")
    return [item for item in pairs if (item["symbol"], item["date"]) in required]


def aggtrades_url(symbol: str, day: str) -> str:
    return f"https://data.binance.vision/data/futures/um/daily/aggTrades/{symbol}/{symbol}-aggTrades-{day}.zip"


def checksum_url(url: str) -> str:
    return url + ".CHECKSUM"


def assert_public_archive_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_ARCHIVE_HOST:
        raise DownloadBlocked(f"blocked non-public archive URL: {url}")
    if not parsed.path.startswith("/data/futures/um/daily/aggTrades/"):
        raise DownloadBlocked(f"blocked non-aggTrades USD-M archive URL: {url}")


def request_bytes(url: str, missing_ok: bool = False, max_bytes: int | None = None) -> tuple[bytes, dict[str, str], bool]:
    assert_public_archive_url(url)
    last_error = ""
    for attempt in range(MAX_RETRIES):
        if attempt:
            time.sleep(min(2.0 * attempt, 8.0))
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                limit = None if max_bytes is None else max_bytes + 1
                body = response.read(limit)
                if max_bytes is not None and len(body) > max_bytes:
                    raise DownloadBlocked(f"response exceeded byte cap for {url}")
                headers = {key.lower(): value for key, value in response.headers.items()}
                time.sleep(REQUEST_SLEEP_SECONDS)
                return body, headers, False
        except urllib.error.HTTPError as exc:
            if missing_ok and exc.code == 404:
                return b"", {}, True
            body = exc.read(1000).decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {body[:300]}"
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
    raise DownloadBlocked(f"download failed for {url}: {last_error or 'unknown error'}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_checksum(text: str) -> str | None:
    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def local_zip_path(root: Path, symbol: str, day: str) -> Path:
    return root / symbol / f"{symbol}-aggTrades-{day}.zip"


def looks_like_header(row: list[str]) -> bool:
    joined = ",".join(row).lower()
    return any(token in joined for token in ["price", "qty", "quantity", "timestamp", "buyer", "maker", "trade"])


def infer_schema(zip_path: Path, sample_limit: int = 8) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(members) != 1:
            raise DownloadBlocked(f"expected exactly one CSV member in {zip_path}, found {members}")
        with archive.open(members[0], "r") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            reader = csv.reader(text)
            rows: list[list[str]] = []
            for row in reader:
                if row:
                    rows.append(row)
                if len(rows) >= sample_limit:
                    break
    if not rows:
        raise DownloadBlocked(f"empty aggTrades CSV in {zip_path}")
    has_header = looks_like_header(rows[0])
    header = rows[0] if has_header else DEFAULT_NO_HEADER_COLUMNS[: len(rows[0])]
    sample_rows = rows[1:] if has_header else rows
    return {
        "zip_member": members[0],
        "has_header": has_header,
        "header": header,
        "column_count_observed": len(header),
        "sample_row_count": len(sample_rows),
        "sample_rows": sample_rows[:5],
        "sample_width_counts": dict(Counter(str(len(row)) for row in sample_rows)),
    }


def write_schema_md(payload: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM aggTrades pilot schema summary v1",
        "",
        f"status: {payload['status']}",
        f"created_at_utc: {payload['created_at_utc']}",
        f"pilot_aggtrades_download_count: {payload['pilot_aggtrades_download_count']}",
        f"checksum_verified_count: {payload['checksum_verified_count']}",
        "",
        "## Downloads",
    ]
    for item in payload["downloads"]:
        lines.append(
            f"- {item['symbol']} {item['file_date_or_month']}: bytes={item['bytes']}, checksum_verified={item['checksum_verified']}, columns={item['schema']['header']}"
        )
    lines.append("")
    SCHEMA_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def download_one(pair: dict[str, str], pilot_root: Path) -> dict[str, Any]:
    symbol = pair["symbol"]
    day = pair["date"]
    url = aggtrades_url(symbol, day)
    zip_path = local_zip_path(pilot_root, symbol, day)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path = zip_path.with_name(zip_path.name + ".CHECKSUM")
    checksum_available = False
    checksum_verified = None
    expected_sha = None
    checksum_body, _checksum_headers, checksum_missing = request_bytes(checksum_url(url), missing_ok=True, max_bytes=4096)
    if not checksum_missing:
        checksum_available = True
        checksum_text = checksum_body.decode("utf-8", errors="replace")
        expected_sha = parse_checksum(checksum_text)
        checksum_path.write_text(checksum_text, encoding="utf-8")
    if not zip_path.exists():
        body, headers, missing = request_bytes(url)
        if missing:
            raise DownloadBlocked(f"aggTrades pilot ZIP missing: {url}")
        tmp = zip_path.with_suffix(zip_path.suffix + ".tmp")
        tmp.write_bytes(body)
        tmp.replace(zip_path)
    else:
        headers = {}
    observed_sha = sha256_file(zip_path)
    if expected_sha:
        checksum_verified = observed_sha == expected_sha
        if not checksum_verified:
            raise DownloadBlocked(f"checksum mismatch for {url}: {observed_sha} != {expected_sha}")
    schema = infer_schema(zip_path)
    return {
        "symbol": symbol,
        "file_date_or_month": day,
        "url": url,
        "checksum_url": checksum_url(url),
        "checksum_available": checksum_available,
        "checksum_verified": checksum_verified,
        "local_zip_path": str(zip_path),
        "local_checksum_path": str(checksum_path) if checksum_available else "",
        "bytes": zip_path.stat().st_size,
        "sha256": observed_sha,
        "response_content_length": headers.get("content-length", ""),
        "schema": schema,
    }


def main() -> int:
    try:
        dirs = external_dirs()
        pairs = pilot_pairs_from_bookdepth_summary()
        downloads = [download_one(pair, dirs["aggtrades_pilot"]) for pair in pairs]
        checksum_verified_count = sum(1 for item in downloads if item["checksum_verified"] is True)
        payload = {
            "status": "PASS_ORDERBOOK_UM_AGGTRADES_PILOT_SCHEMA_SUMMARY_CREATED",
            "created_at_utc": utc_now_text(),
            "mode": "safe_matching_pilot_only",
            "data_root": str(data_root()),
            "aggtrades_pilot_dir": str(dirs["aggtrades_pilot"]),
            "absorption_work_dir": str(dirs["absorption_work"]),
            "logs_dir": str(dirs["logs"]),
            "pilot_pairs": pairs,
            "pilot_aggtrades_download_count": len(downloads),
            "checksum_verified_count": checksum_verified_count,
            "downloads": downloads,
            "full_historical_download_attempted": False,
            "replacement_checks_all_true": len(downloads) == 4 and all(item["checksum_verified"] is not False for item in downloads),
            "next_module": "ORDERBOOK_UM_ABSORPTION_PILOT_PREVIEW_V1",
        }
        SCHEMA_SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_schema_md(payload)
        print(f"status: {payload['status']}")
        print(f"pilot_aggtrades_download_count: {payload['pilot_aggtrades_download_count']}")
        print(f"checksum_verified_count: {payload['checksum_verified_count']}")
        print(f"schema_summary_json: {SCHEMA_SUMMARY_JSON}")
        print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")
        return 0 if payload["replacement_checks_all_true"] else 2
    except DownloadBlocked as exc:
        payload = {
            "status": "BLOCKED_ORDERBOOK_UM_AGGTRADES_PILOT_DOWNLOAD",
            "created_at_utc": utc_now_text(),
            "exact_blocker": str(exc),
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_AGGTRADES_PILOT_BLOCKER_REVIEW",
        }
        SCHEMA_SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_schema_md({**payload, "pilot_aggtrades_download_count": 0, "checksum_verified_count": 0, "downloads": []})
        print(f"BLOCKED: {exc}")
        print("replacement_checks_all_true=false")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
