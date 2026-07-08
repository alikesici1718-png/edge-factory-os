#!/usr/bin/env python
"""Download manifest-listed Binance USD-M 81-symbol daily bookDepth ZIPs with checksum gates."""

from __future__ import annotations

import csv
import concurrent.futures
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edge_factory_orderbook_um_81_full_bookdepth_manifest_validator_v1 import (
    EXPECTED_SYMBOL_COUNT,
    MANIFEST_CSV,
    OUTPUTS_DIR,
    REPORT_JSON as MANIFEST_VALIDATION_JSON,
    REPO_ROOT,
    assert_public_bookdepth_url,
    bool_text,
    data_root,
    derived_checksum_path,
    derived_zip_path,
    logs_dir,
    path_is_inside,
    raw_target_dir,
    read_manifest,
)


DOWNLOAD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_download_summary.json"
DOWNLOAD_SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_download_summary.md"
FILE_STATUS_CSV = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_file_status.csv"
SYMBOL_COVERAGE_CSV = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_symbol_coverage.csv"
BLOCKED_NOT_ACK_MD = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED.md"

REQUEST_TIMEOUT_SECONDS = 120
REQUEST_SLEEP_SECONDS = 0.08
MAX_RETRIES = 5
MAX_CHECKSUM_REDOWNLOADS = 2
USER_AGENT = "edge-factory-orderbook-um-81-full-bookdepth-downloader-v1"
ACK_ENV = "ORDERBOOK_81_FULL_BOOKDEPTH_DOWNLOAD"
WORKERS_ENV = "ORDERBOOK_DOWNLOAD_WORKERS"
CONNECT_TIMEOUT_ENV = "ORDERBOOK_DOWNLOAD_CONNECT_TIMEOUT"
READ_TIMEOUT_ENV = "ORDERBOOK_DOWNLOAD_READ_TIMEOUT"
MAX_RETRIES_ENV = "ORDERBOOK_DOWNLOAD_MAX_RETRIES"
DEFAULT_WORKERS = 8
MIN_WORKERS = 1
MAX_WORKERS = 32
DEFAULT_CONNECT_TIMEOUT_SECONDS = 20
DEFAULT_READ_TIMEOUT_SECONDS = 120
DEFAULT_MAX_RETRIES = 5
PROGRESS_PRINT_SECONDS = 30


class DownloadBlocked(RuntimeError):
    """Raised when the full download must stop closed."""


class ChecksumMismatchBlocked(DownloadBlocked):
    """Raised after repeated checksum mismatch."""


@dataclass(frozen=True)
class DownloadSettings:
    workers: int
    connect_timeout_seconds: int
    read_timeout_seconds: int
    max_retries: int
    warnings: tuple[str, ...]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_int(value: Any) -> int | None:
    if value in ("", None):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def parse_required_positive_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return default
    try:
        parsed = int(raw)
    except ValueError as exc:
        raise DownloadBlocked(f"{name} must be an integer; got {raw!r}") from exc
    if parsed <= 0:
        raise DownloadBlocked(f"{name} must be greater than zero; got {parsed}")
    return parsed


def load_settings() -> DownloadSettings:
    warnings: list[str] = []
    worker_raw = os.environ.get(WORKERS_ENV)
    if worker_raw in (None, ""):
        workers = DEFAULT_WORKERS
    else:
        try:
            workers = int(worker_raw)
        except ValueError as exc:
            raise DownloadBlocked(f"{WORKERS_ENV} must be an integer; got {worker_raw!r}") from exc
        if workers < MIN_WORKERS:
            warnings.append(f"{WORKERS_ENV}={workers} below {MIN_WORKERS}; clamped to {MIN_WORKERS}")
            workers = MIN_WORKERS
        elif workers > MAX_WORKERS:
            warnings.append(f"{WORKERS_ENV}={workers} above {MAX_WORKERS}; clamped to {MAX_WORKERS}")
            workers = MAX_WORKERS
    return DownloadSettings(
        workers=workers,
        connect_timeout_seconds=parse_required_positive_env(CONNECT_TIMEOUT_ENV, DEFAULT_CONNECT_TIMEOUT_SECONDS),
        read_timeout_seconds=parse_required_positive_env(READ_TIMEOUT_ENV, DEFAULT_READ_TIMEOUT_SECONDS),
        max_retries=parse_required_positive_env(MAX_RETRIES_ENV, DEFAULT_MAX_RETRIES),
        warnings=tuple(warnings),
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_checksum_text(text: str) -> str | None:
    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise DownloadBlocked(f"missing required JSON: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DownloadBlocked(f"JSON is not an object: {path}")
    return payload


def external_paths() -> dict[str, Path]:
    root = data_root()
    raw = raw_target_dir(root)
    logs = logs_dir(root)
    if path_is_inside(root, REPO_ROOT):
        raise DownloadBlocked(f"data root resolves inside repo: {root}")
    if path_is_inside(raw, REPO_ROOT):
        raise DownloadBlocked(f"raw target directory resolves inside repo: {raw}")
    if path_is_inside(logs, REPO_ROOT):
        raise DownloadBlocked(f"logs directory resolves inside repo: {logs}")
    for directory in [raw, logs, logs / "checksums", logs / "progress"]:
        directory.mkdir(parents=True, exist_ok=True)
    return {
        "data_root": root,
        "raw": raw,
        "logs": logs,
        "progress_json": logs / "progress" / "orderbook_um_81_full_bookdepth_progress.json",
        "external_status_csv": logs / "orderbook_um_81_full_bookdepth_file_status.csv",
        "external_status_jsonl": logs / "orderbook_um_81_full_bookdepth_file_status.jsonl",
    }


def external_data_root_warnings(root: Path) -> list[str]:
    if "onedrive" in str(root).lower():
        return [
            "EDGE_FACTORY_DATA_ROOT contains OneDrive; large parallel downloads may sync slowly. "
            r"Recommended external root: C:\edge_factory_external_data"
        ]
    return []


def set_response_read_timeout(response: Any, read_timeout_seconds: int) -> None:
    candidates = [
        ("fp", "raw", "_sock"),
        ("fp", "fp", "raw", "_sock"),
    ]
    for chain in candidates:
        socket_candidate = response
        try:
            for name in chain:
                socket_candidate = getattr(socket_candidate, name)
            socket_candidate.settimeout(read_timeout_seconds)
            return
        except AttributeError:
            continue


def transient_http_status(code: int) -> bool:
    return code in {408, 425, 429, 500, 502, 503, 504}


def backoff_sleep(attempt: int, status_code: int | None = None) -> None:
    base = 2.0 if status_code == 429 else 1.5
    time.sleep(min(base * (2**attempt), 30.0))


def request_bytes(url: str, settings: DownloadSettings, max_bytes: int = 8192) -> bytes:
    assert_public_bookdepth_url(url.removesuffix(".CHECKSUM"))
    last_error = ""
    for attempt in range(settings.max_retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=settings.connect_timeout_seconds) as response:
                set_response_read_timeout(response, settings.read_timeout_seconds)
                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise DownloadBlocked(f"checksum response exceeded byte cap: {url}")
                time.sleep(REQUEST_SLEEP_SECONDS)
                return body
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code == 404:
                return b""
            if not transient_http_status(exc.code):
                break
            if attempt + 1 < settings.max_retries:
                backoff_sleep(attempt, exc.code)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
            if attempt + 1 < settings.max_retries:
                backoff_sleep(attempt)
    raise DownloadBlocked(f"checksum download failed for {url}: {last_error or 'unknown error'}")


def get_checksum(checksum_url: str, checksum_path: Path, settings: DownloadSettings) -> tuple[str | None, bool]:
    if not checksum_url:
        return None, False
    assert_public_bookdepth_url(checksum_url.removesuffix(".CHECKSUM"))
    if checksum_path.exists():
        existing = checksum_path.read_text(encoding="utf-8", errors="replace")
        parsed = parse_checksum_text(existing)
        if parsed:
            return parsed, True
    body = request_bytes(checksum_url, settings)
    if not body:
        return None, False
    text = body.decode("utf-8", errors="replace")
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path.write_text(text, encoding="utf-8")
    return parse_checksum_text(text), True


def download_to_part(
    url: str,
    target: Path,
    expected_sha: str | None,
    settings: DownloadSettings,
    restart: bool = False,
) -> tuple[int, bool, str]:
    assert_public_bookdepth_url(url)
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    headers = {"User-Agent": USER_AGENT}
    mode = "ab"
    resume_offset = 0
    if part.exists() and not restart:
        resume_offset = part.stat().st_size
        if resume_offset > 0:
            headers["Range"] = f"bytes={resume_offset}-"
    else:
        mode = "wb"

    last_error = ""
    for attempt in range(settings.max_retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=settings.connect_timeout_seconds) as response:
                set_response_read_timeout(response, settings.read_timeout_seconds)
                status = getattr(response, "status", None)
                if resume_offset > 0 and status != 206:
                    mode = "wb"
                    resume_offset = 0
                bytes_written = 0
                with part.open(mode + "b" if mode in {"a", "w"} else mode) as handle:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
                        bytes_written += len(chunk)
                if expected_sha and sha256_file(part) != expected_sha:
                    try:
                        part.unlink()
                    except FileNotFoundError:
                        pass
                    return bytes_written, False, "CHECKSUM_MISMATCH_PART_DELETED"
                part.replace(target)
                time.sleep(REQUEST_SLEEP_SECONDS)
                return bytes_written, True, "DOWNLOADED"
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code == 404:
                return 0, False, "FAILED_PERMANENT_404"
            if not transient_http_status(exc.code):
                break
            if attempt + 1 < settings.max_retries:
                backoff_sleep(attempt, exc.code)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
            if attempt + 1 < settings.max_retries:
                backoff_sleep(attempt)
    raise DownloadBlocked(f"ZIP download failed for {url}: {last_error or 'unknown error'}")


def write_blocked_not_acknowledged() -> int:
    BLOCKED_NOT_ACK_MD.write_text(
        "\n".join(
            [
                "# BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED",
                "",
                f"created_at_utc: {utc_now_text()}",
                f"required_environment_variable: {ACK_ENV}=YES",
                "status: BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED",
                "replacement_checks_all_true=false",
                "next_module: ORDERBOOK_UM_81_FULL_BOOKDEPTH_APPROVAL_OR_BLOCKER_REVIEW",
                "",
                "The full 81-symbol bookDepth archive download was not started because the acknowledgement environment variable was not set to YES.",
                "No raw ZIP files were downloaded by this blocked route.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("status: BLOCKED_DOWNLOAD_NOT_ACKNOWLEDGED")
    print(f"blocked_report: {BLOCKED_NOT_ACK_MD}")
    print("replacement_checks_all_true: false")
    print("next_module: ORDERBOOK_UM_81_FULL_BOOKDEPTH_APPROVAL_OR_BLOCKER_REVIEW")
    return 2


def validate_prerequisites(rows: list[dict[str, str]], validation: dict[str, Any]) -> None:
    if validation.get("status") != "PASS_ORDERBOOK_UM_81_FULL_BOOKDEPTH_MANIFEST_VALIDATED":
        raise DownloadBlocked("manifest validation status is not PASS")
    if validation.get("replacement_checks_all_true") is not True:
        raise DownloadBlocked("manifest validation replacement checks are not all true")
    if validation.get("symbol_count") != EXPECTED_SYMBOL_COUNT:
        raise DownloadBlocked(f"manifest validation symbol count is not {EXPECTED_SYMBOL_COUNT}")
    if validation.get("expected_file_count") != len(rows):
        raise DownloadBlocked("manifest validation expected file count does not match manifest rows")


def write_progress(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def process_row(row: dict[str, str], dirs: dict[str, Path], settings: DownloadSettings) -> dict[str, Any]:
    url = row["url"]
    checksum_url = row.get("checksum_url", "")
    assert_public_bookdepth_url(url)
    if checksum_url:
        assert_public_bookdepth_url(checksum_url.removesuffix(".CHECKSUM"))
    zip_path = derived_zip_path(row, dirs["data_root"])
    checksum_path = derived_checksum_path(row, dirs["data_root"])
    if path_is_inside(zip_path, REPO_ROOT) or path_is_inside(checksum_path, REPO_ROOT):
        raise DownloadBlocked(f"derived local path resolves inside repo for {url}")
    expected_size = parse_int(row.get("size_bytes"))
    expected_sha, checksum_available = get_checksum(checksum_url, checksum_path, settings)
    downloaded_bytes = 0
    skipped_verified = False
    checksum_verified = False
    status = "NO_CHECKSUM_AVAILABLE"
    if expected_sha and zip_path.exists() and sha256_file(zip_path) == expected_sha:
        skipped_verified = True
        checksum_verified = True
        status = "SKIPPED_VERIFIED"
    elif not expected_sha and zip_path.exists() and (expected_size is None or zip_path.stat().st_size == expected_size):
        status = "EXISTING_NO_CHECKSUM_AVAILABLE"
    else:
        restart = False
        for attempt in range(MAX_CHECKSUM_REDOWNLOADS + 1):
            bytes_written, ok, download_status = download_to_part(
                url,
                zip_path,
                expected_sha,
                settings,
                restart=restart,
            )
            downloaded_bytes += bytes_written
            if ok:
                break
            if download_status == "FAILED_PERMANENT_404":
                status = "FAILED_PERMANENT_404"
                break
            restart = True
            if attempt >= MAX_CHECKSUM_REDOWNLOADS:
                raise ChecksumMismatchBlocked(f"repeated checksum mismatch for {url}")
        if status == "FAILED_PERMANENT_404":
            checksum_verified = False
        elif expected_sha:
            checksum_verified = sha256_file(zip_path) == expected_sha
            status = "DOWNLOADED_VERIFIED" if checksum_verified else "CHECKSUM_MISMATCH"
        else:
            status = "DOWNLOADED_NO_CHECKSUM_AVAILABLE"
    observed_size = zip_path.stat().st_size if zip_path.exists() else 0
    if expected_sha and not checksum_verified and status != "FAILED_PERMANENT_404":
        raise ChecksumMismatchBlocked(f"checksum mismatch after download for {url}")
    return {
        "symbol": row["symbol"],
        "file_date": row["file_date_or_month"],
        "file_name": row["file_name"],
        "url": url,
        "checksum_url": checksum_url,
        "local_zip_path": str(zip_path),
        "local_checksum_path": str(checksum_path) if checksum_available else "",
        "expected_size_bytes": expected_size if expected_size is not None else "",
        "observed_size_bytes": observed_size,
        "downloaded_bytes": downloaded_bytes,
        "checksum_available": checksum_available,
        "checksum_verified": checksum_verified,
        "skipped_verified": skipped_verified,
        "status": status,
        "error_message": "",
    }


def aggregate_symbol_coverage(rows: list[dict[str, str]], statuses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_symbol_expected: dict[str, list[dict[str, str]]] = {}
    by_symbol_status: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_symbol_expected.setdefault(row["symbol"], []).append(row)
    for item in statuses:
        by_symbol_status.setdefault(item["symbol"], []).append(item)
    coverage_rows: list[dict[str, Any]] = []
    for symbol in sorted(by_symbol_expected):
        expected_rows = by_symbol_expected[symbol]
        status_rows = by_symbol_status.get(symbol, [])
        dates = [row["file_date_or_month"] for row in expected_rows]
        coverage_rows.append(
            {
                "symbol": symbol,
                "expected_file_count": len(expected_rows),
                "completed_file_count": sum(1 for item in status_rows if status_is_complete(item)),
                "checksum_verified_count": sum(1 for item in status_rows if item.get("checksum_verified") is True),
                "checksum_missing_count": sum(1 for item in status_rows if item.get("checksum_available") is False),
                "failed_count": sum(1 for item in status_rows if status_is_failed(item)),
                "earliest_date": min(dates) if dates else "",
                "latest_date": max(dates) if dates else "",
            }
        )
    return coverage_rows


def status_is_failed(item: dict[str, Any]) -> bool:
    status = str(item.get("status", ""))
    return status.startswith("FAILED") or status == "CHECKSUM_MISMATCH"


def status_is_downloaded_this_run(item: dict[str, Any]) -> bool:
    return str(item.get("status", "")) in {"DOWNLOADED_VERIFIED", "DOWNLOADED_NO_CHECKSUM_AVAILABLE"}


def status_is_complete(item: dict[str, Any]) -> bool:
    return str(item.get("status", "")) in {
        "SKIPPED_VERIFIED",
        "DOWNLOADED_VERIFIED",
        "DOWNLOADED_NO_CHECKSUM_AVAILABLE",
        "EXISTING_NO_CHECKSUM_AVAILABLE",
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def compact_progress_payload(
    statuses: list[dict[str, Any]],
    expected_file_count: int,
    dirs: dict[str, Path],
    settings: DownloadSettings,
    started_at: float,
    last_progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = time.monotonic()
    downloaded_bytes = sum(int(item.get("downloaded_bytes") or 0) for item in statuses)
    verified_bytes = sum(int(item.get("observed_size_bytes") or 0) for item in statuses if item.get("checksum_verified") is True)
    recent_mbps = 0.0
    if last_progress:
        elapsed = max(now - float(last_progress["monotonic"]), 0.001)
        byte_delta = downloaded_bytes - int(last_progress["downloaded_bytes"])
        recent_mbps = (byte_delta / elapsed) / 1_000_000
    return {
        "status": "RUNNING_81_FULL_BOOKDEPTH_DOWNLOAD",
        "updated_at_utc": utc_now_text(),
        "completed_file_count": len(statuses),
        "expected_file_count": expected_file_count,
        "verified_skipped_file_count": sum(1 for item in statuses if item.get("skipped_verified")),
        "downloaded_this_run_file_count": sum(1 for item in statuses if status_is_downloaded_this_run(item)),
        "failed_count": sum(1 for item in statuses if status_is_failed(item)),
        "recent_mbps": round(recent_mbps, 3),
        "total_verified_gb": round(verified_bytes / 1_000_000_000, 6),
        "total_downloaded_this_run_gb": round(downloaded_bytes / 1_000_000_000, 6),
        "estimated_remaining_files": max(expected_file_count - len(statuses), 0),
        "worker_count": settings.workers,
        "raw_target_directory": str(dirs["raw"]),
        "elapsed_seconds": round(now - started_at, 3),
        "monotonic": now,
        "downloaded_bytes": downloaded_bytes,
    }


def print_progress(payload: dict[str, Any]) -> None:
    print(
        "progress: "
        f"{payload['completed_file_count']}/{payload['expected_file_count']} "
        f"verified_skipped={payload['verified_skipped_file_count']} "
        f"downloaded_this_run={payload['downloaded_this_run_file_count']} "
        f"failed={payload['failed_count']} "
        f"recent_mbps={payload['recent_mbps']} "
        f"total_verified_gb={payload['total_verified_gb']} "
        f"remaining_files={payload['estimated_remaining_files']} "
        f"workers={payload['worker_count']} "
        f"target={payload['raw_target_directory']}",
        flush=True,
    )


def final_status(summary: dict[str, Any]) -> str:
    if summary["failed_count"] > 0:
        return "FAIL_81_FULL_BOOKDEPTH_CHECKSUM_OR_DOWNLOAD"
    if summary["checksum_missing_count"] > 0:
        return "PARTIAL_81_FULL_BOOKDEPTH_DOWNLOAD_RETRY_REQUIRED"
    if summary["checksum_verified_count"] == summary["expected_file_count"]:
        return "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED"
    return "PARTIAL_81_FULL_BOOKDEPTH_DOWNLOAD_RETRY_REQUIRED"


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 full bookDepth download summary v1",
        "",
        f"status: {summary['status']}",
        f"symbol_count: {summary['symbol_count']}",
        f"expected_file_count: {summary['expected_file_count']}",
        f"worker_count: {summary.get('worker_count', '')}",
        f"connect_timeout_seconds: {summary.get('connect_timeout_seconds', '')}",
        f"read_timeout_seconds: {summary.get('read_timeout_seconds', '')}",
        f"max_retries: {summary.get('max_retries', '')}",
        f"downloaded_file_count: {summary['downloaded_file_count']}",
        f"skipped_verified_file_count: {summary['skipped_verified_file_count']}",
        f"checksum_verified_count: {summary['checksum_verified_count']}",
        f"checksum_missing_count: {summary['checksum_missing_count']}",
        f"failed_count: {summary['failed_count']}",
        f"total_downloaded_gb: {summary['total_downloaded_gb']}",
        f"total_verified_gb: {summary['total_verified_gb']}",
        f"external_data_root: {summary['external_data_root']}",
        f"raw_target_directory: {summary['raw_target_directory']}",
        f"earliest_global_date: {summary['earliest_global_date']}",
        f"latest_global_date: {summary['latest_global_date']}",
        f"replacement_checks_all_true: {bool_text(summary['replacement_checks_all_true'])}",
        f"next_module: {summary['next_module']}",
        "",
        "## Restart instructions",
        f"1. Keep raw ZIP files in place under {summary['raw_target_directory']}.",
        f"2. Re-run run_orderbook_um_81_full_bookdepth_downloader_v1.ps1 with {ACK_ENV}=YES.",
        "3. Existing ZIPs are skipped only when their checksum verifies.",
        "4. Recommended parallel worker count is 12 or 16 on a stable connection.",
        "",
        "## Scope",
        "- Public Binance Data Vision USD-M daily bookDepth ZIPs only.",
        "- No private endpoints, account endpoints, order execution, recommendations, or strategy logic.",
        "",
        "## Warnings",
    ]
    warnings = summary.get("warnings", [])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- none")
    lines.append("")
    DOWNLOAD_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_failure_summary(reason: str, partial_statuses: list[dict[str, Any]], dirs: dict[str, Path]) -> int:
    summary = {
        "status": "FAIL_81_FULL_BOOKDEPTH_CHECKSUM_OR_DOWNLOAD",
        "created_at_utc": utc_now_text(),
        "exact_blocker": reason,
        "symbol_count": 0,
        "expected_file_count": 0,
        "downloaded_file_count": sum(1 for item in partial_statuses if item.get("status") == "DOWNLOADED_VERIFIED"),
        "skipped_verified_file_count": sum(1 for item in partial_statuses if item.get("skipped_verified")),
        "checksum_verified_count": sum(1 for item in partial_statuses if item.get("checksum_verified") is True),
        "checksum_missing_count": sum(1 for item in partial_statuses if item.get("checksum_available") is False),
        "failed_count": 1,
        "total_downloaded_bytes": sum(int(item.get("downloaded_bytes") or 0) for item in partial_statuses),
        "total_downloaded_gb": round(sum(int(item.get("downloaded_bytes") or 0) for item in partial_statuses) / 1_000_000_000, 6),
        "total_verified_bytes": sum(int(item.get("observed_size_bytes") or 0) for item in partial_statuses if item.get("checksum_verified") is True),
        "total_verified_gb": round(sum(int(item.get("observed_size_bytes") or 0) for item in partial_statuses if item.get("checksum_verified") is True) / 1_000_000_000, 6),
        "external_data_root": str(dirs.get("data_root", data_root())),
        "raw_target_directory": str(dirs.get("raw", raw_target_dir())),
        "logs_directory": str(dirs.get("logs", logs_dir())),
        "failed_urls": [],
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_81_FULL_BOOKDEPTH_DOWNLOAD_BLOCKER_REVIEW",
    }
    DOWNLOAD_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_summary_md({**summary, "earliest_global_date": "", "latest_global_date": ""})
    print(f"status: {summary['status']}")
    print(f"exact_blocker: {reason}")
    print("replacement_checks_all_true: false")
    return 2


def main() -> int:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if os.environ.get(ACK_ENV) != "YES":
        return write_blocked_not_acknowledged()
    statuses: list[dict[str, Any]] = []
    dirs: dict[str, Path] = {}
    try:
        settings = load_settings()
        dirs = external_paths()
        warnings = list(settings.warnings) + external_data_root_warnings(dirs["data_root"])
        for warning in warnings:
            print(f"WARNING: {warning}", flush=True)
        rows, _fieldnames = read_manifest()
        rows = [row for row in rows if row.get("status") == "AVAILABLE"]
        validation = load_json(MANIFEST_VALIDATION_JSON)
        validate_prerequisites(rows, validation)
        expected_file_count = len(rows)
        started_at = time.monotonic()
        last_progress_marker: dict[str, Any] = {"monotonic": started_at, "downloaded_bytes": 0}
        progress = {
            "status": "RUNNING_81_FULL_BOOKDEPTH_DOWNLOAD",
            "started_at_utc": utc_now_text(),
            "expected_file_count": expected_file_count,
            "completed_file_count": 0,
            "failed_count": 0,
            "worker_count": settings.workers,
            "connect_timeout_seconds": settings.connect_timeout_seconds,
            "read_timeout_seconds": settings.read_timeout_seconds,
            "max_retries": settings.max_retries,
            "warnings": warnings,
            "raw_target_directory": str(dirs["raw"]),
        }
        write_progress(dirs["progress_json"], progress)

        def failed_item(row: dict[str, str], exc: BaseException, status: str = "FAILED_DOWNLOAD_OR_CHECKSUM") -> dict[str, Any]:
            return {
                "symbol": row.get("symbol", ""),
                "file_date": row.get("file_date_or_month", ""),
                "file_name": row.get("file_name", ""),
                "url": row.get("url", ""),
                "checksum_url": row.get("checksum_url", ""),
                "local_zip_path": str(derived_zip_path(row, dirs["data_root"])),
                "local_checksum_path": str(derived_checksum_path(row, dirs["data_root"])),
                "expected_size_bytes": row.get("size_bytes", ""),
                "observed_size_bytes": "",
                "downloaded_bytes": 0,
                "checksum_available": bool(row.get("checksum_url")),
                "checksum_verified": False,
                "skipped_verified": False,
                "status": status,
                "error_message": str(exc),
            }

        max_pending = max(settings.workers * 4, settings.workers)
        next_row_index = 0
        fatal_reason: str | None = None
        last_print_at = started_at

        with dirs["external_status_jsonl"].open("a", encoding="utf-8", newline="\n") as jsonl_handle:
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.workers) as executor:
                pending: dict[concurrent.futures.Future[dict[str, Any]], dict[str, str]] = {}

                def submit_until_full() -> None:
                    nonlocal next_row_index
                    while fatal_reason is None and next_row_index < expected_file_count and len(pending) < max_pending:
                        row = rows[next_row_index]
                        next_row_index += 1
                        future = executor.submit(process_row, row, dirs, settings)
                        pending[future] = row

                submit_until_full()
                while pending:
                    done, _not_done = concurrent.futures.wait(
                        pending,
                        timeout=1.0,
                        return_when=concurrent.futures.FIRST_COMPLETED,
                    )
                    if not done:
                        now = time.monotonic()
                        if now - last_print_at >= PROGRESS_PRINT_SECONDS:
                            payload = compact_progress_payload(
                                statuses,
                                expected_file_count,
                                dirs,
                                settings,
                                started_at,
                                last_progress_marker,
                            )
                            write_progress(dirs["progress_json"], payload)
                            print_progress(payload)
                            last_progress_marker = payload
                            last_print_at = now
                        continue
                    for future in done:
                        row = pending.pop(future)
                        try:
                            item = future.result()
                        except concurrent.futures.CancelledError as exc:
                            item = failed_item(row, exc, "FAILED_CANCELLED_AFTER_FATAL_CHECKSUM_MISMATCH")
                        except ChecksumMismatchBlocked as exc:
                            fatal_reason = str(exc)
                            item = failed_item(row, exc, "CHECKSUM_MISMATCH")
                        except Exception as exc:  # noqa: BLE001
                            item = failed_item(row, exc)
                        statuses.append(item)
                        jsonl_handle.write(json.dumps(item, sort_keys=True, ensure_ascii=True) + "\n")
                        jsonl_handle.flush()
                    if fatal_reason is not None:
                        for future in pending:
                            future.cancel()
                    submit_until_full()
                    now = time.monotonic()
                    if now - last_print_at >= PROGRESS_PRINT_SECONDS:
                        payload = compact_progress_payload(
                            statuses,
                            expected_file_count,
                            dirs,
                            settings,
                            started_at,
                            last_progress_marker,
                        )
                        write_progress(dirs["progress_json"], payload)
                        print_progress(payload)
                        last_progress_marker = payload
                        last_print_at = now
        if fatal_reason is not None:
            raise ChecksumMismatchBlocked(fatal_reason)
        file_fieldnames = [
            "symbol",
            "file_date",
            "file_name",
            "status",
            "checksum_available",
            "checksum_verified",
            "skipped_verified",
            "expected_size_bytes",
            "observed_size_bytes",
            "downloaded_bytes",
            "local_zip_path",
            "local_checksum_path",
            "url",
            "checksum_url",
            "error_message",
        ]
        write_csv(FILE_STATUS_CSV, statuses, file_fieldnames)
        write_csv(dirs["external_status_csv"], statuses, file_fieldnames)
        coverage_rows = aggregate_symbol_coverage(rows, statuses)
        write_csv(
            SYMBOL_COVERAGE_CSV,
            coverage_rows,
            [
                "symbol",
                "expected_file_count",
                "completed_file_count",
                "checksum_verified_count",
                "checksum_missing_count",
                "failed_count",
                "earliest_date",
                "latest_date",
            ],
        )
        failed = [item for item in statuses if status_is_failed(item)]
        verified_bytes = sum(int(item.get("observed_size_bytes") or 0) for item in statuses if item.get("checksum_verified") is True)
        downloaded_bytes = sum(int(item.get("downloaded_bytes") or 0) for item in statuses)
        summary = {
            "status": "",
            "created_at_utc": utc_now_text(),
            "task_name": "ORDERBOOK_UM_81_SYMBOL_FULL_BOOKDEPTH_DOWNLOAD_V1",
            "symbol_count": len({row["symbol"] for row in rows}),
            "expected_file_count": expected_file_count,
            "worker_count": settings.workers,
            "connect_timeout_seconds": settings.connect_timeout_seconds,
            "read_timeout_seconds": settings.read_timeout_seconds,
            "max_retries": settings.max_retries,
            "warnings": warnings,
            "downloaded_file_count": sum(1 for item in statuses if status_is_downloaded_this_run(item)),
            "skipped_verified_file_count": sum(1 for item in statuses if item.get("skipped_verified")),
            "checksum_verified_count": sum(1 for item in statuses if item.get("checksum_verified") is True),
            "checksum_missing_count": sum(1 for item in statuses if item.get("checksum_available") is False),
            "failed_count": len(failed),
            "total_downloaded_bytes": downloaded_bytes,
            "total_downloaded_gb": round(downloaded_bytes / 1_000_000_000, 6),
            "total_verified_bytes": verified_bytes,
            "total_verified_gb": round(verified_bytes / 1_000_000_000, 6),
            "external_data_root": str(dirs["data_root"]),
            "raw_target_directory": str(dirs["raw"]),
            "logs_directory": str(dirs["logs"]),
            "external_progress_log": str(dirs["progress_json"]),
            "external_file_status_log": str(dirs["external_status_csv"]),
            "earliest_global_date": validation.get("earliest_global_date"),
            "latest_global_date": validation.get("latest_global_date"),
            "earliest_latest_by_symbol": validation.get("earliest_latest_by_symbol", {}),
            "failed_urls": [item.get("url", "") for item in failed],
            "restart_resume_instructions": [
                f"Set {ACK_ENV}=YES before running the downloader runner.",
                f"Set {WORKERS_ENV}=12 or 16 for controlled parallel download on a stable connection.",
                "Re-run run_orderbook_um_81_full_bookdepth_downloader_v1.ps1 from the repo root.",
                "Existing ZIPs are skipped only after checksum verification.",
            ],
            "replacement_checks_all_true": False,
            "next_module": "ORDERBOOK_UM_81_FULL_BOOKDEPTH_DOWNLOAD_VALIDATOR_V1",
        }
        summary["status"] = final_status(summary)
        summary["replacement_checks_all_true"] = summary["status"] == "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED"
        if summary["status"] != "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED":
            summary["next_module"] = "ORDERBOOK_UM_81_FULL_BOOKDEPTH_DOWNLOAD_BLOCKER_REVIEW"
        DOWNLOAD_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_summary_md(summary)
        final_progress = compact_progress_payload(statuses, expected_file_count, dirs, settings, started_at, last_progress_marker)
        write_progress(dirs["progress_json"], {**final_progress, "status": summary["status"], "finished_at_utc": utc_now_text()})
        print(f"status: {summary['status']}")
        print(f"expected_file_count: {summary['expected_file_count']}")
        print(f"worker_count: {summary['worker_count']}")
        print(f"checksum_verified_count: {summary['checksum_verified_count']}")
        print(f"failed_count: {summary['failed_count']}")
        print(f"download_summary_json: {DOWNLOAD_SUMMARY_JSON}")
        print(f"replacement_checks_all_true: {bool_text(summary['replacement_checks_all_true'])}")
        return 0 if summary["replacement_checks_all_true"] else 2
    except ChecksumMismatchBlocked as exc:
        return write_failure_summary(str(exc), statuses, dirs)
    except DownloadBlocked as exc:
        return write_failure_summary(str(exc), statuses, dirs)


if __name__ == "__main__":
    raise SystemExit(main())
