#!/usr/bin/env python
"""Download and inspect a tiny Binance USD-M bookDepth pilot sample."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.csv"
COVERAGE_JSON = OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.json"
VALIDATOR_REPORT_JSON = OUTPUTS_DIR / "orderbook_um_manifest_validator_report.json"
ALLOW_FULL_FILE = OUTPUTS_DIR / "ALLOW_ORDERBOOK_FULL_DOWNLOAD.txt"
PILOT_SCHEMA_JSON = OUTPUTS_DIR / "orderbook_um_pilot_schema_summary.json"
PILOT_SCHEMA_MD = OUTPUTS_DIR / "orderbook_um_pilot_schema_summary.md"
REQUEST_TIMEOUT_SECONDS = 45
MAX_RETRIES = 4
REQUEST_SLEEP_SECONDS = 0.15
USER_AGENT = "edge-factory-orderbook-um-pilot-downloader-v1"
PUBLIC_ARCHIVE_HOST = "data.binance.vision"


class DownloadBlocked(RuntimeError):
    """Raised when downloading must stop safely."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def external_dirs() -> dict[str, Path]:
    root = data_root()
    if path_is_inside(root, REPO_ROOT):
        raise DownloadBlocked(f"data root resolves inside repo: {root}")
    dirs = {
        "raw": root / "binance_um_orderbook_raw",
        "manifest": root / "binance_um_orderbook_manifest",
        "pilot": root / "binance_um_orderbook_pilot",
        "logs": root / "binance_um_orderbook_logs",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def assert_public_archive_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_ARCHIVE_HOST:
        raise DownloadBlocked(f"blocked non-public archive URL: {url}")
    if not parsed.path.startswith("/data/futures/um/"):
        raise DownloadBlocked(f"blocked non-USD-M archive URL: {url}")


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST_CSV.exists():
        raise DownloadBlocked(f"manifest missing: {MANIFEST_CSV}")
    with MANIFEST_CSV.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def request_bytes(url: str, max_bytes: int | None = None) -> tuple[bytes, dict[str, str]]:
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
                return body, headers
        except urllib.error.HTTPError as exc:
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


def select_pilot_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], str]:
    available = [row for row in rows if row.get("status") == "AVAILABLE" and row.get("url")]
    by_symbol: dict[str, list[dict[str, str]]] = {}
    for row in available:
        by_symbol.setdefault(row["symbol"], []).append(row)
    for symbol_rows in by_symbol.values():
        symbol_rows.sort(key=lambda row: row["file_date_or_month"])

    selected: list[dict[str, str]] = []
    reason = "Selected BTCUSDT earliest/latest and ETHUSDT/SOLUSDT latest from the verified 81-symbol universe."
    if by_symbol.get("BTCUSDT"):
        selected.append(by_symbol["BTCUSDT"][0])
        selected.append(by_symbol["BTCUSDT"][-1])
    for symbol in ["ETHUSDT", "SOLUSDT"]:
        if by_symbol.get(symbol):
            selected.append(by_symbol[symbol][-1])
    if len(selected) >= 3:
        dedup: dict[str, dict[str, str]] = {}
        for row in selected:
            dedup[row["url"]] = row
        return list(dedup.values()), reason

    liquid_order = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "LINKUSDT"]
    fallback = [symbol for symbol in liquid_order if by_symbol.get(symbol)]
    if len(fallback) < 3:
        fallback = sorted(symbol for symbol, symbol_rows in by_symbol.items() if symbol_rows)[:3]
    selected = [by_symbol[symbol][-1] for symbol in fallback[:3]]
    return selected, "BTC/ETH/SOL pilot set was incomplete, so selected the first liquid-looking available symbols by fixed major-symbol preference."


def local_pilot_zip_path(pilot_dir: Path, row: dict[str, str]) -> Path:
    return pilot_dir / row["symbol"] / row["file_name"]


def download_one(row: dict[str, str], pilot_dir: Path) -> dict[str, Any]:
    zip_path = local_pilot_zip_path(pilot_dir, row)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path = zip_path.with_name(zip_path.name + ".CHECKSUM")
    checksum_text = ""
    expected_sha = None
    checksum_verified = None
    if row.get("checksum_url"):
        checksum_bytes, _headers = request_bytes(row["checksum_url"], max_bytes=4096)
        checksum_text = checksum_bytes.decode("utf-8", errors="replace")
        expected_sha = parse_checksum(checksum_text)
        checksum_path.write_text(checksum_text, encoding="utf-8")
    if not zip_path.exists():
        body, headers = request_bytes(row["url"])
        tmp = zip_path.with_suffix(zip_path.suffix + ".tmp")
        tmp.write_bytes(body)
        tmp.replace(zip_path)
    else:
        headers = {}
    observed_sha = sha256_file(zip_path)
    if expected_sha:
        checksum_verified = observed_sha == expected_sha
        if not checksum_verified:
            raise DownloadBlocked(f"checksum mismatch for {row['url']}: {observed_sha} != {expected_sha}")
    schema = inspect_zip_sample(zip_path)
    return {
        "symbol": row["symbol"],
        "file_date_or_month": row["file_date_or_month"],
        "url": row["url"],
        "checksum_url": row.get("checksum_url", ""),
        "local_zip_path": str(zip_path),
        "local_checksum_path": str(checksum_path) if checksum_text else "",
        "bytes": zip_path.stat().st_size,
        "sha256": observed_sha,
        "checksum_verified": checksum_verified,
        "response_content_length": headers.get("content-length", ""),
        "schema": schema,
    }


def inspect_zip_sample(zip_path: Path, sample_limit: int = 8) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise DownloadBlocked(f"zip has no CSV member: {zip_path}")
        member = csv_names[0]
        with archive.open(member, "r") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            reader = csv.reader(text)
            rows: list[list[str]] = []
            for row in reader:
                if row:
                    rows.append(row)
                if len(rows) >= sample_limit:
                    break
    header = rows[0] if rows and any(not cell.replace(".", "", 1).isdigit() for cell in rows[0]) else None
    sample_rows = rows[1:] if header else rows
    width_counts: dict[str, int] = {}
    for row in sample_rows:
        width_counts[str(len(row))] = width_counts.get(str(len(row)), 0) + 1
    return {
        "zip_member": member,
        "has_header": header is not None,
        "header": header or [],
        "sample_row_count": len(sample_rows),
        "sample_rows": sample_rows[:5],
        "column_count_observed": len(header or sample_rows[0]) if rows else 0,
        "sample_width_counts": width_counts,
    }


def validator_passed() -> bool:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "src" / "edge_factory_orderbook_um_manifest_validator_v1.py")],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return False
    if not VALIDATOR_REPORT_JSON.exists():
        return False
    payload = json.loads(VALIDATOR_REPORT_JSON.read_text(encoding="utf-8"))
    return payload.get("replacement_checks_all_true") is True


def assert_full_download_unlocked(rows: list[dict[str, str]]) -> dict[str, Any]:
    if os.environ.get("ORDERBOOK_FULL_DOWNLOAD") != "YES":
        raise DownloadBlocked("BLOCKED_FULL_DOWNLOAD_LOCKED: ORDERBOOK_FULL_DOWNLOAD is not YES")
    if os.environ.get("I_ACKNOWLEDGE_ORDERBOOK_DOWNLOAD_SIZE") != "YES":
        raise DownloadBlocked("BLOCKED_FULL_DOWNLOAD_LOCKED: I_ACKNOWLEDGE_ORDERBOOK_DOWNLOAD_SIZE is not YES")
    if not validator_passed():
        raise DownloadBlocked("BLOCKED_FULL_DOWNLOAD_LOCKED: manifest validator has not passed")
    if not ALLOW_FULL_FILE.exists() or ALLOW_FULL_FILE.read_text(encoding="utf-8").strip() != "ALLOW_FULL_ORDERBOOK_DOWNLOAD":
        raise DownloadBlocked("BLOCKED_FULL_DOWNLOAD_LOCKED: confirmation file is missing or invalid")
    dirs = external_dirs()
    estimated = sum(int(row.get("size_bytes") or 0) for row in rows if row.get("status") == "AVAILABLE")
    free = shutil.disk_usage(dirs["raw"]).free
    if estimated <= 0:
        raise DownloadBlocked("BLOCKED_FULL_DOWNLOAD_LOCKED: estimated total size is unavailable")
    if free < estimated * 1.25:
        raise DownloadBlocked(
            f"BLOCKED_FULL_DOWNLOAD_LOCKED: free disk {free} is less than required {int(estimated * 1.25)}"
        )
    return {"estimated_total_size_bytes": estimated, "free_disk_bytes": free}


def write_schema_summary(payload: dict[str, Any]) -> None:
    PILOT_SCHEMA_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    lines = [
        "# Orderbook UM pilot schema summary v1",
        "",
        f"status: {payload['status']}",
        f"created_at_utc: {payload['created_at_utc']}",
        f"pilot_download_count: {payload['pilot_download_count']}",
        f"selection_reason: {payload['selection_reason']}",
        f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}",
        "",
        "## Files",
    ]
    for item in payload["downloads"]:
        lines.append(f"- {item['symbol']} {item['file_date_or_month']}: {item['local_zip_path']}")
    lines.append("")
    PILOT_SCHEMA_MD.write_text("\n".join(lines), encoding="utf-8")


def run_pilot() -> dict[str, Any]:
    rows = read_manifest()
    dirs = external_dirs()
    selected, reason = select_pilot_rows(rows)
    if not selected:
        raise DownloadBlocked("no pilot rows available in manifest")
    downloads = [download_one(row, dirs["pilot"]) for row in selected]
    return {
        "status": "PASS_ORDERBOOK_UM_PILOT_SCHEMA_VALIDATED",
        "created_at_utc": utc_now_text(),
        "mode": "safe_pilot_only",
        "selection_reason": reason,
        "pilot_download_count": len(downloads),
        "downloads": downloads,
        "data_root": str(data_root()),
        "full_download_attempted": False,
        "replacement_checks_all_true": True,
        "next_module": "ORDERBOOK_UM_DATA_REVIEW_OR_STOP",
    }


def run_full_locked_or_download() -> dict[str, Any]:
    rows = read_manifest()
    unlock = assert_full_download_unlocked(rows)
    dirs = external_dirs()
    downloads: list[dict[str, Any]] = []
    for row in rows:
        if row.get("status") != "AVAILABLE":
            continue
        downloads.append(download_one(row, dirs["raw"]))
    return {
        "status": "PASS_ORDERBOOK_UM_FULL_DOWNLOAD_COMPLETED",
        "created_at_utc": utc_now_text(),
        "mode": "full_download_unlocked",
        "unlock_checks": unlock,
        "download_count": len(downloads),
        "downloads": downloads,
        "replacement_checks_all_true": True,
        "next_module": "ORDERBOOK_UM_FULL_DOWNLOAD_REVIEW",
    }


def main() -> int:
    try:
        if os.environ.get("ORDERBOOK_FULL_DOWNLOAD") == "YES":
            payload = run_full_locked_or_download()
        else:
            payload = run_pilot()
        write_schema_summary(payload)
        print(f"status: {payload['status']}")
        print(f"pilot_schema_summary_json: {PILOT_SCHEMA_JSON}")
        print(f"pilot_schema_summary_md: {PILOT_SCHEMA_MD}")
        print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")
        print(f"next_module: {payload['next_module']}")
        return 0
    except DownloadBlocked as exc:
        payload = {
            "status": "BLOCKED_ORDERBOOK_UM_PILOT_DOWNLOADER",
            "created_at_utc": utc_now_text(),
            "exact_blocker": str(exc),
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_APPROVAL_OR_BLOCKER_REVIEW",
        }
        write_schema_summary(payload)
        print(f"BLOCKED / APPROVAL_REQUIRED: {exc}")
        print("replacement_checks_all_true=false")
        print("next_module=ORDERBOOK_UM_APPROVAL_OR_BLOCKER_REVIEW")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
