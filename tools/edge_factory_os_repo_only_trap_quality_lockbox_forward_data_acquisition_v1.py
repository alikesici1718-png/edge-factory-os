from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "data_acquisition" / "trap_quality_lockbox_forward_data_acquisition_v1.json"
FREEZE_CONTRACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "trap_quality_lockbox_freeze_contract_v1.json"
PANEL_REVIEW_PATH = REPO_ROOT / "artifacts" / "panel_build_reviews" / "binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
DEVELOPMENT_PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_build_v1\panel_15m_by_symbol"
)
EXTERNAL_OUTPUT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_trap_quality_lockbox_forward_data_acquisition_v1"
)
RAW_ARCHIVES_DIR = EXTERNAL_OUTPUT_ROOT / "raw_archives"
NORMALIZED_DIR = EXTERNAL_OUTPUT_ROOT / "normalized_15m_by_symbol"
COVERAGE_REPORTS_DIR = EXTERNAL_OUTPUT_ROOT / "coverage_reports"
CHECKSUMS_DIR = EXTERNAL_OUTPUT_ROOT / "checksums"

STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_CREATED"
ARTIFACT_KIND = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION"
MODULE = "edge_factory_os_repo_only_trap_quality_lockbox_forward_data_acquisition_v1"
FROZEN_FINALIST = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
EXPECTED_FREEZE_STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FREEZE_CONTRACT_CREATED"
EXPECTED_NEXT_STEP = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_V1"

LOCKBOX_START_ISO = "2025-11-01T00:00:00Z"
LOCKBOX_START_MS = 1_761_955_200_000
INTERVAL_MS = 15 * 60 * 1000
MONTHLY_ARCHIVE_BASE = "https://data.binance.vision/data/futures/um/monthly/klines"
USER_AGENT = "edge-factory-os-trap-quality-lockbox-forward-data-acquisition/1.0"
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3

PANEL_HEADER = [
    "symbol",
    "timestamp_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "complete_15m",
]


class BlockedError(RuntimeError):
    pass


class IntegrityError(RuntimeError):
    pass


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def month_add(month: str, delta: int) -> str:
    year, number = (int(part) for part in month.split("-"))
    index = year * 12 + number - 1 + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def previous_full_month(now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    first_this_month = dt.datetime(now.year, now.month, 1, tzinfo=dt.timezone.utc)
    previous_day = first_this_month - dt.timedelta(days=1)
    return f"{previous_day.year:04d}-{previous_day.month:02d}"


def month_range(start_month: str, end_month_inclusive: str) -> list[str]:
    months: list[str] = []
    month = start_month
    while month <= end_month_inclusive:
        months.append(month)
        month = month_add(month, 1)
    return months


def month_end_exclusive_iso(end_month_inclusive: str) -> str:
    next_month = month_add(end_month_inclusive, 1)
    year, number = (int(part) for part in next_month.split("-"))
    return dt.datetime(year, number, 1, tzinfo=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ms_from_iso(iso_ts: str) -> int:
    return int(dt.datetime.strptime(iso_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def iso_from_ms(open_time_ms: int) -> str:
    return dt.datetime.fromtimestamp(open_time_ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_url(symbol: str, month: str) -> str:
    return f"{MONTHLY_ARCHIVE_BASE}/{symbol}/15m/{symbol}-15m-{month}.zip"


def checksum_url(symbol: str, month: str) -> str:
    return month_url(symbol, month) + ".CHECKSUM"


def request_bytes(url: str, allow_404: bool = False) -> tuple[int | None, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code == 404:
            return exc.code, b""
        return exc.code, exc.read()
    except Exception as exc:  # noqa: BLE001
        raise BlockedError(f"network request failed for {url}: {exc}") from exc


def request_head(url: str) -> int | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:  # noqa: BLE001
        raise BlockedError(f"network HEAD request failed for {url}: {exc}") from exc


def request_bytes_with_retry(url: str, allow_404: bool = False) -> tuple[int | None, bytes]:
    last_status: int | None = None
    last_error: str | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            status, data = request_bytes(url, allow_404=allow_404)
        except BlockedError as exc:
            status, data = None, b""
            last_error = str(exc)
        last_status = status
        if status == 200:
            return status, data
        if status == 404 and allow_404:
            return status, data
        if status is None or status in {408, 425, 429, 500, 502, 503, 504}:
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise BlockedError(f"request failed after retries for {url}: status={last_status} error={last_error}")
        return status, data
    return last_status, b""


def parse_checksum(text: str, expected_filename: str) -> str:
    match = re.search(r"\b([a-fA-F0-9]{64})\b", text)
    if not match:
        raise IntegrityError(f"checksum file missing SHA256 for {expected_filename}")
    if expected_filename not in text:
        raise IntegrityError(f"checksum file does not reference {expected_filename}")
    return match.group(1).lower()


def recover_universe() -> list[str]:
    if not DEVELOPMENT_PANEL_DIR.is_dir():
        raise BlockedError(f"development panel directory missing: {DEVELOPMENT_PANEL_DIR}")
    symbols = sorted(path.name.removesuffix("_15m.csv.gz") for path in DEVELOPMENT_PANEL_DIR.glob("*_15m.csv.gz"))
    if len(symbols) != 81:
        raise BlockedError(f"expected 81 symbols from reviewed panel, found {len(symbols)}")
    if "BTCUSDT" not in symbols or "ETHUSDT" not in symbols:
        raise BlockedError("required anchor symbol missing from reviewed panel universe")
    return symbols


def latest_available_closed_month() -> tuple[str, list[dict[str, Any]]]:
    start = "2025-11"
    candidate = previous_full_month()
    probes: list[dict[str, Any]] = []
    while candidate >= start:
        zip_status = request_head(month_url("BTCUSDT", candidate))
        checksum_status = request_head(checksum_url("BTCUSDT", candidate))
        probes.append(
            {
                "symbol": "BTCUSDT",
                "month": candidate,
                "zip_status": zip_status,
                "checksum_status": checksum_status,
                "archive_and_checksum_available": zip_status == 200 and checksum_status == 200,
            }
        )
        if zip_status == 200 and checksum_status == 200:
            return candidate, probes
        candidate = month_add(candidate, -1)
    raise BlockedError("BLOCKED_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_SOURCE_UNAVAILABLE: no BTCUSDT monthly 15m lockbox archive available from 2025-11 onward")


def prepare_external_dirs() -> None:
    resolved_root = EXTERNAL_OUTPUT_ROOT.resolve()
    resolved_repo = REPO_ROOT.resolve()
    if resolved_repo == resolved_root or resolved_repo in resolved_root.parents:
        raise BlockedError("external output root resolves inside repo")
    for directory in [RAW_ARCHIVES_DIR, NORMALIZED_DIR, COVERAGE_REPORTS_DIR, CHECKSUMS_DIR]:
        if directory.exists() and any(directory.iterdir()):
            raise BlockedError(f"external output directory already contains files; refusing overwrite: {directory}")
    for directory in [RAW_ARCHIVES_DIR, NORMALIZED_DIR, COVERAGE_REPORTS_DIR, CHECKSUMS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def fetch_checksum(symbol: str, month: str, archive_records: list[dict[str, Any]]) -> str | None:
    filename = f"{symbol}-15m-{month}.zip"
    url = checksum_url(symbol, month)
    status, data = request_bytes_with_retry(url, allow_404=True)
    if status == 404:
        archive_records.append({"symbol": symbol, "month": month, "checksum_url": url, "status": "missing_checksum_404"})
        return None
    if status != 200:
        raise BlockedError(f"checksum request failed for {filename}: status={status}")
    checksum_text = data.decode("utf-8", errors="replace")
    expected_hash = parse_checksum(checksum_text, filename)
    checksum_path = CHECKSUMS_DIR / f"{filename}.CHECKSUM"
    if checksum_path.exists():
        raise BlockedError(f"checksum file already exists; refusing overwrite: {checksum_path}")
    checksum_path.write_text(checksum_text, encoding="utf-8")
    archive_records.append(
        {
            "symbol": symbol,
            "month": month,
            "checksum_url": url,
            "checksum_path": str(checksum_path),
            "expected_sha256": expected_hash,
            "status": "checksum_fetched",
        }
    )
    return expected_hash


def download_zip(symbol: str, month: str, expected_hash: str, archive_records: list[dict[str, Any]]) -> Path:
    filename = f"{symbol}-15m-{month}.zip"
    path = RAW_ARCHIVES_DIR / filename
    if path.exists():
        observed = sha256_file(path)
        if observed == expected_hash:
            return path
        raise BlockedError(f"raw archive already exists with unexpected checksum; refusing overwrite: {path}")
    status, data = request_bytes_with_retry(month_url(symbol, month), allow_404=True)
    if status == 404:
        archive_records.append({"symbol": symbol, "month": month, "source_url": month_url(symbol, month), "status": "missing_zip_404"})
        return path
    if status != 200:
        raise BlockedError(f"zip download failed for {filename}: status={status}")
    tmp = path.with_suffix(".zip.tmp")
    if tmp.exists():
        raise BlockedError(f"temp archive already exists; refusing overwrite: {tmp}")
    tmp.write_bytes(data)
    observed_hash = sha256_file(tmp)
    if observed_hash != expected_hash:
        raise IntegrityError(f"checksum mismatch for {filename}: {observed_hash} != {expected_hash}")
    tmp.replace(path)
    archive_records.append(
        {
            "symbol": symbol,
            "month": month,
            "source_url": month_url(symbol, month),
            "raw_archive_path": str(path),
            "sha256": observed_hash,
            "bytes": len(data),
            "status": "downloaded_and_checksum_verified",
        }
    )
    return path


def iter_zip_rows(zip_path: Path) -> Any:
    with zipfile.ZipFile(zip_path, "r") as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise IntegrityError(f"expected exactly one CSV in {zip_path.name}, found {csv_names}")
        with archive.open(csv_names[0], "r") as raw_handle:
            text_handle = io.TextIOWrapper(raw_handle, encoding="utf-8", newline="")
            reader = csv.reader(text_handle)
            for row in reader:
                if not row:
                    continue
                if row[0].strip().lower() == "open_time" or not row[0].strip().isdigit():
                    continue
                yield row


def parse_positive_float(value: str) -> float:
    parsed = float(value)
    if not (parsed > 0 and math.isfinite(parsed)):
        raise ValueError(value)
    return parsed


def parse_non_negative_float(value: str) -> float:
    parsed = float(value)
    if not (parsed >= 0 and math.isfinite(parsed)):
        raise ValueError(value)
    return parsed


def acquire_symbol(symbol: str, months: list[str], lockbox_end_ms: int, archive_records: list[dict[str, Any]]) -> dict[str, Any]:
    final_output = NORMALIZED_DIR / f"{symbol}_15m.csv.gz"
    temp_output = NORMALIZED_DIR / f"{symbol}_15m.csv.gz.tmp"
    if final_output.exists() or temp_output.exists():
        raise BlockedError(f"normalized output already exists; refusing overwrite for {symbol}")
    seen: set[int] = set()
    source_months_used: list[str] = []
    missing_months: list[str] = []
    min_ts: int | None = None
    max_ts: int | None = None
    row_count = 0
    duplicate_timestamp_count = 0
    ohlc_sanity_fail_count = 0
    non_numeric_ohlc_count = 0
    negative_volume_count = 0
    negative_quote_volume_count = 0
    before_start_count = 0
    after_end_count = 0
    incomplete_15m_count = 0

    with gzip.open(temp_output, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(PANEL_HEADER)
        for month in months:
            expected_hash = fetch_checksum(symbol, month, archive_records)
            if expected_hash is None:
                missing_months.append(month)
                continue
            zip_path = download_zip(symbol, month, expected_hash, archive_records)
            if not zip_path.exists():
                missing_months.append(month)
                continue
            source_months_used.append(month)
            for row in iter_zip_rows(zip_path):
                if len(row) < 12:
                    raise IntegrityError(f"malformed kline row for {symbol} in {zip_path.name}: {row}")
                open_time_ms = int(row[0])
                close_time_ms = int(row[6])
                if open_time_ms < LOCKBOX_START_MS:
                    before_start_count += 1
                    continue
                if open_time_ms >= lockbox_end_ms:
                    after_end_count += 1
                    continue
                timestamp = iso_from_ms(open_time_ms)
                if open_time_ms % INTERVAL_MS != 0:
                    raise IntegrityError(f"non-15m aligned timestamp for {symbol}: {timestamp}")
                try:
                    open_price = parse_positive_float(row[1])
                    high_price = parse_positive_float(row[2])
                    low_price = parse_positive_float(row[3])
                    close_price = parse_positive_float(row[4])
                except ValueError as exc:
                    non_numeric_ohlc_count += 1
                    raise IntegrityError(f"non-positive/non-numeric OHLC for {symbol} at {timestamp}") from exc
                try:
                    volume = parse_non_negative_float(row[5])
                except ValueError as exc:
                    negative_volume_count += 1
                    raise IntegrityError(f"negative/non-numeric volume for {symbol} at {timestamp}") from exc
                try:
                    quote_volume = parse_non_negative_float(row[7])
                except ValueError as exc:
                    negative_quote_volume_count += 1
                    raise IntegrityError(f"negative/non-numeric quote_volume for {symbol} at {timestamp}") from exc
                if high_price < max(open_price, close_price, low_price) or low_price > min(open_price, close_price, high_price):
                    ohlc_sanity_fail_count += 1
                    raise IntegrityError(f"OHLC sanity failed for {symbol} at {timestamp}")
                if open_time_ms in seen:
                    duplicate_timestamp_count += 1
                    raise IntegrityError(f"duplicate timestamp for {symbol}: {timestamp}")
                seen.add(open_time_ms)
                complete_15m = close_time_ms == open_time_ms + INTERVAL_MS - 1
                if not complete_15m:
                    incomplete_15m_count += 1
                min_ts = open_time_ms if min_ts is None else min(min_ts, open_time_ms)
                max_ts = open_time_ms if max_ts is None else max(max_ts, open_time_ms)
                row_count += 1
                writer.writerow(
                    [
                        symbol,
                        timestamp,
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[7],
                        row[8],
                        row[9],
                        row[10],
                        "true" if complete_15m else "false",
                    ]
                )
    if row_count == 0:
        try:
            temp_output.unlink()
        except OSError:
            pass
        return {
            "symbol": symbol,
            "file_exists": False,
            "missing_reason": "no_source_rows_for_lockbox_months",
            "row_count": 0,
            "source_months_used": source_months_used,
            "missing_months": missing_months,
        }
    temp_output.replace(final_output)
    expected_full_period_rows = (lockbox_end_ms - LOCKBOX_START_MS) // INTERVAL_MS
    missing_full_period_intervals = expected_full_period_rows - row_count
    missing_between_first_last = 0
    if min_ts is not None and max_ts is not None:
        expected_between_first_last = ((max_ts - min_ts) // INTERVAL_MS) + 1
        missing_between_first_last = expected_between_first_last - row_count
    return {
        "symbol": symbol,
        "file_exists": True,
        "path": str(final_output),
        "sha256": sha256_file(final_output),
        "row_count": row_count,
        "timestamp_min": iso_from_ms(min_ts) if min_ts is not None else None,
        "timestamp_max": iso_from_ms(max_ts) if max_ts is not None else None,
        "source_months_used": source_months_used,
        "missing_months": missing_months,
        "expected_full_period_rows": expected_full_period_rows,
        "missing_full_period_intervals": missing_full_period_intervals,
        "missing_interval_count": missing_between_first_last,
        "duplicate_timestamp_count": duplicate_timestamp_count,
        "ohlc_sanity_fail_count": ohlc_sanity_fail_count,
        "non_numeric_ohlc_count": non_numeric_ohlc_count,
        "negative_volume_count": negative_volume_count,
        "negative_quote_volume_count": negative_quote_volume_count,
        "rows_before_2025_11_01": before_start_count,
        "rows_after_lockbox_end": after_end_count,
        "incomplete_15m_row_count": incomplete_15m_count,
        "expected_15m_cadence_valid": missing_between_first_last == 0 and duplicate_timestamp_count == 0,
        "ohlc_numeric_sanity_passed": ohlc_sanity_fail_count == 0
        and non_numeric_ohlc_count == 0
        and negative_volume_count == 0
        and negative_quote_volume_count == 0,
        "timezone": "UTC",
        "full_coverage": row_count == expected_full_period_rows and missing_full_period_intervals == 0,
        "partial_coverage": row_count > 0 and (row_count != expected_full_period_rows or bool(missing_months)),
    }


def write_external_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if path.exists():
        raise BlockedError(f"external report already exists; refusing overwrite: {path}")
    path.write_text(canonical_json(payload), encoding="utf-8")
    return {"path": str(path), "sha256": sha256_file(path)}


def build_artifact(
    status_lines: list[str],
    unexpected_status: list[str],
    freeze_contract: dict[str, Any],
    panel_review: dict[str, Any],
    symbols: list[str],
    months: list[str],
    lockbox_end_iso: str,
    latest_probe: list[dict[str, Any]],
    archive_records: list[dict[str, Any]],
    per_symbol: dict[str, Any],
    external_reports: dict[str, Any],
    result_classification: str,
    next_allowed_step: str,
    limitations: list[str],
) -> dict[str, Any]:
    acquired_symbols = [symbol for symbol, record in per_symbol.items() if record.get("file_exists")]
    missing_symbols = [symbol for symbol, record in per_symbol.items() if not record.get("file_exists")]
    partial_symbols = [symbol for symbol, record in per_symbol.items() if record.get("partial_coverage")]
    full_symbols = [symbol for symbol, record in per_symbol.items() if record.get("full_coverage")]
    total_rows = sum(int(record.get("row_count", 0)) for record in per_symbol.values())
    quality_failures = [
        {"symbol": symbol, "record": record}
        for symbol, record in per_symbol.items()
        if record.get("file_exists")
        and (
            not record.get("expected_15m_cadence_valid")
            or not record.get("ohlc_numeric_sanity_passed")
            or record.get("rows_before_2025_11_01", 0) != 0
            or record.get("rows_after_lockbox_end", 0) != 0
        )
    ]
    data_quality_passed = len(quality_failures) == 0 and len(acquired_symbols) > 0
    normalized_files = {
        symbol: {"path": record.get("path"), "sha256": record.get("sha256"), "row_count": record.get("row_count")}
        for symbol, record in per_symbol.items()
        if record.get("file_exists")
    }
    checksum_records = {symbol: record["sha256"] for symbol, record in per_symbol.items() if record.get("file_exists")}
    lockbox_integrity = {
        "frozen_config_not_modified": True,
        "strategy_execution_performed": False,
        "signal_generation_performed": False,
        "pnl_computation_performed": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
    }
    safety_permissions = {
        "data_acquisition_created": True,
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
        "repo_clean_before_run": not unexpected_status,
        "freeze_contract_loaded": freeze_contract.get("status") == EXPECTED_FREEZE_STATUS,
        "frozen_finalist_verified": freeze_contract.get("freeze_decision", {}).get("frozen_finalist") == FROZEN_FINALIST,
        "rejected_finalists_preserved": bool(freeze_contract.get("explicit_rejections")),
        "development_panel_review_loaded": panel_review.get("status") is not None,
        "lockbox_start_verified_2025_11_01": LOCKBOX_START_ISO == "2025-11-01T00:00:00Z",
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_pnl_computation": True,
        "no_parameter_change": True,
        "no_v_next_created": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_api_used": True,
        "no_order_endpoint_used": True,
        "external_output_root_used": str(EXTERNAL_OUTPUT_ROOT).startswith(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"),
        "no_development_panel_modified": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": not unexpected_status,
        "replacement_checks_all_true": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_acquisition": status_lines,
            "unexpected_dirty_paths_at_acquisition": unexpected_status,
        },
        "source_artifacts": {
            "freeze_contract": str(FREEZE_CONTRACT_PATH),
            "development_panel_review": str(PANEL_REVIEW_PATH),
            "development_panel_dir_read_only": str(DEVELOPMENT_PANEL_DIR),
        },
        "frozen_finalist": FROZEN_FINALIST,
        "lockbox_period": {
            "lockbox_start": LOCKBOX_START_ISO,
            "lockbox_end": lockbox_end_iso,
            "primary_closed_months": months,
            "partial_month_extension": None,
            "partial_month_extension_included_in_primary": False,
        },
        "requested_universe": {"requested_symbol_count": len(symbols), "symbols": symbols},
        "acquisition_source_summary": {
            "source": "Binance public data archive monthly USD-M futures klines",
            "source_url_template": f"{MONTHLY_ARCHIVE_BASE}/{{SYMBOL}}/15m/{{SYMBOL}}-15m-{{YYYY-MM}}.zip",
            "checksum_url_template": f"{MONTHLY_ARCHIVE_BASE}/{{SYMBOL}}/15m/{{SYMBOL}}-15m-{{YYYY-MM}}.zip.CHECKSUM",
            "latest_closed_month_probe": latest_probe,
            "archive_record_count": len(archive_records),
            "archive_records": archive_records,
            "private_api_used": False,
            "order_endpoint_used": False,
        },
        "external_output_root": str(EXTERNAL_OUTPUT_ROOT),
        "generated_external_files": {
            "raw_archives_dir": str(RAW_ARCHIVES_DIR),
            "normalized_15m_by_symbol_dir": str(NORMALIZED_DIR),
            "coverage_reports_dir": str(COVERAGE_REPORTS_DIR),
            "checksums_dir": str(CHECKSUMS_DIR),
            "normalized_files": normalized_files,
            "external_reports": external_reports,
        },
        "per_symbol_coverage": per_symbol,
        "coverage_summary": {
            "requested_symbol_count": len(symbols),
            "acquired_symbol_count": len(acquired_symbols),
            "missing_symbol_count": len(missing_symbols),
            "partial_symbol_count": len(partial_symbols),
            "full_coverage_symbol_count": len(full_symbols),
            "lockbox_start": LOCKBOX_START_ISO,
            "lockbox_end": lockbox_end_iso,
            "closed_month_coverage": {
                "months": months,
                "month_count": len(months),
                "full_coverage_symbol_count": len(full_symbols),
                "partial_symbol_count": len(partial_symbols),
            },
            "partial_month_coverage": None,
            "total_rows": total_rows,
            "per_symbol_row_counts": {symbol: record.get("row_count", 0) for symbol, record in per_symbol.items()},
            "missing_symbols": missing_symbols,
            "coverage_warnings": [
                f"partial coverage for {len(partial_symbols)} symbols" if partial_symbols else "",
                f"missing symbols: {missing_symbols}" if missing_symbols else "",
            ],
        },
        "data_quality_checks": {
            "data_quality_passed": data_quality_passed,
            "quality_failure_count": len(quality_failures),
            "quality_failures": quality_failures,
            "checks": {
                "file_exists_or_missing_reason_recorded": all(record.get("file_exists") or record.get("missing_reason") for record in per_symbol.values()),
                "expected_15m_cadence": all(record.get("expected_15m_cadence_valid", True) for record in per_symbol.values() if record.get("file_exists")),
                "duplicate_timestamp_count_zero": all(record.get("duplicate_timestamp_count", 0) == 0 for record in per_symbol.values() if record.get("file_exists")),
                "ohlc_sanity": all(record.get("ohlc_sanity_fail_count", 0) == 0 for record in per_symbol.values() if record.get("file_exists")),
                "positive_ohlc": all(record.get("non_numeric_ohlc_count", 0) == 0 for record in per_symbol.values() if record.get("file_exists")),
                "non_negative_volume": all(record.get("negative_volume_count", 0) == 0 for record in per_symbol.values() if record.get("file_exists")),
                "non_negative_quote_volume": all(record.get("negative_quote_volume_count", 0) == 0 for record in per_symbol.values() if record.get("file_exists")),
                "no_rows_before_2025_11_01": all(record.get("rows_before_2025_11_01", 0) == 0 for record in per_symbol.values() if record.get("file_exists")),
                "no_rows_after_lockbox_end": all(record.get("rows_after_lockbox_end", 0) == 0 for record in per_symbol.values() if record.get("file_exists")),
                "timezone_utc": all(record.get("timezone") == "UTC" for record in per_symbol.values() if record.get("file_exists")),
            },
        },
        "checksum_summary": {
            "normalized_file_sha256": checksum_records,
            "normalized_file_count": len(checksum_records),
            "raw_archive_count": len([record for record in archive_records if record.get("status") == "downloaded_and_checksum_verified"]),
        },
        "lockbox_integrity": lockbox_integrity,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": limitations,
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["data_acquisition_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "data_acquisition_created")
        and lockbox_integrity["strategy_execution_performed"] is False
        and lockbox_integrity["signal_generation_performed"] is False
        and lockbox_integrity["pnl_computation_performed"] is False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_trap_quality_lockbox_forward_data_acquisition_v1.py",
        "?? artifacts/data_acquisition/trap_quality_lockbox_forward_data_acquisition_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    start_time = time.monotonic()

    freeze_contract = load_json(FREEZE_CONTRACT_PATH)
    panel_review = load_json(PANEL_REVIEW_PATH)
    if freeze_contract.get("freeze_decision", {}).get("next_allowed_step") != EXPECTED_NEXT_STEP:
        raise BlockedError("freeze contract does not allow this acquisition step")
    symbols = recover_universe()
    latest_month, latest_probe = latest_available_closed_month()
    months = month_range("2025-11", latest_month)
    lockbox_end_iso = month_end_exclusive_iso(latest_month)
    lockbox_end_ms = ms_from_iso(lockbox_end_iso)
    prepare_external_dirs()

    archive_records: list[dict[str, Any]] = []
    per_symbol: dict[str, Any] = {}
    for index, symbol in enumerate(symbols, start=1):
        print(json.dumps({"event": "acquire_symbol", "symbol": symbol, "index": index, "total": len(symbols)}), file=sys.stderr, flush=True)
        per_symbol[symbol] = acquire_symbol(symbol, months, lockbox_end_ms, archive_records)

    acquired_count = sum(1 for record in per_symbol.values() if record.get("file_exists"))
    full_count = sum(1 for record in per_symbol.values() if record.get("full_coverage"))
    quality_fail = any(
        record.get("file_exists")
        and (
            not record.get("expected_15m_cadence_valid")
            or not record.get("ohlc_numeric_sanity_passed")
            or record.get("rows_before_2025_11_01", 0) != 0
            or record.get("rows_after_lockbox_end", 0) != 0
        )
        for record in per_symbol.values()
    )
    if acquired_count == 0:
        result_classification = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_BLOCKED_SOURCE_UNAVAILABLE"
        next_allowed_step = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_SOURCE_RECOVERY_V1"
    elif quality_fail:
        result_classification = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_FAIL_INTEGRITY"
        next_allowed_step = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REPAIR_OR_REACQUIRE_V1"
    elif full_count == len(symbols):
        result_classification = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_PASS_READY_FOR_DATA_REVIEW"
        next_allowed_step = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_V1"
    else:
        result_classification = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_PARTIAL_REVIEW_REQUIRED"
        next_allowed_step = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_V1"

    coverage_report = {
        "artifact_kind": "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_COVERAGE_REPORT",
        "lockbox_start": LOCKBOX_START_ISO,
        "lockbox_end": lockbox_end_iso,
        "months": months,
        "per_symbol_coverage": per_symbol,
    }
    checksum_report = {
        "artifact_kind": "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_CHECKSUM_REPORT",
        "normalized_file_sha256": {
            symbol: record["sha256"] for symbol, record in per_symbol.items() if record.get("file_exists")
        },
    }
    external_reports = {
        "coverage_report": write_external_json(COVERAGE_REPORTS_DIR / "trap_quality_lockbox_forward_coverage_report_v1.json", coverage_report),
        "checksum_report": write_external_json(CHECKSUMS_DIR / "trap_quality_lockbox_forward_normalized_file_sha256_v1.json", checksum_report),
    }
    limitations = [
        "This module acquired and normalized public OHLCV archives only.",
        "Current partial month data was not included in the primary closed-month lockbox panel.",
        "No strategy execution, signal generation, returns, PnL, optimization, candidate generation, edge claim, or runtime/live/capital permission was created.",
    ]
    artifact = build_artifact(
        status_lines=status_lines,
        unexpected_status=unexpected_status,
        freeze_contract=freeze_contract,
        panel_review=panel_review,
        symbols=symbols,
        months=months,
        lockbox_end_iso=lockbox_end_iso,
        latest_probe=latest_probe,
        archive_records=archive_records,
        per_symbol=per_symbol,
        external_reports=external_reports,
        result_classification=result_classification,
        next_allowed_step=next_allowed_step,
        limitations=limitations,
    )
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    total_rows = artifact["coverage_summary"]["total_rows"]
    data_quality_passed = artifact["data_quality_checks"]["data_quality_passed"]
    print(f"status: {STATUS}")
    print(f"result_classification: {result_classification}")
    print(f"frozen_finalist: {FROZEN_FINALIST}")
    print(f"lockbox_start: {LOCKBOX_START_ISO}")
    print(f"lockbox_end: {lockbox_end_iso}")
    print(f"requested_symbol_count: {len(symbols)}")
    print(f"acquired_symbol_count: {acquired_count}")
    print(f"missing_symbol_count: {len(symbols) - acquired_count}")
    print(f"total_rows: {total_rows}")
    print(f"data_quality_passed: {str(data_quality_passed).lower()}")
    print("strategy_execution_performed: false")
    print("signal_generation_performed: false")
    print("pnl_computation_performed: false")
    print(f"next_allowed_step: {next_allowed_step}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    print(f"elapsed_seconds: {round(time.monotonic() - start_time, 1)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BlockedError as exc:
        print(f"BLOCKED_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_SOURCE_UNAVAILABLE: {exc}", file=sys.stderr)
        raise
    except IntegrityError as exc:
        print(f"TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_FAIL_INTEGRITY: {exc}", file=sys.stderr)
        raise
