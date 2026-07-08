#!/usr/bin/env python
"""Build and validate the 81-symbol bookDepth-matching aggTrades download manifest."""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\edge_factory_external_data")
RAW_DIR_NAME = "binance_um_81_full_matching_aggtrades_raw"
LOGS_DIR_NAME = "binance_um_81_full_matching_aggtrades_logs"

AGGTRADES_AVAILABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_aggtrades_availability_manifest.csv"
AGGTRADES_COVERAGE_JSON = OUTPUTS_DIR / "orderbook_um_81_aggtrades_coverage_summary.json"
AGGTRADES_GAPS_CSV = OUTPUTS_DIR / "orderbook_um_81_aggtrades_vs_bookdepth_coverage_gaps.csv"
BOOKDEPTH_SYMBOL_COVERAGE_CSV = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_symbol_coverage.csv"
BOOKDEPTH_DOWNLOAD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_download_summary.json"

REPORT_JSON = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_manifest_validation.json"
REPORT_MD = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_manifest_validation.md"
DOWNLOAD_MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_download_manifest.csv"
DOWNLOAD_MANIFEST_JSONL = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_download_manifest.jsonl"

EXPECTED_SYMBOL_COUNT = 81
PUBLIC_ARCHIVE_HOST = "data.binance.vision"
PUBLIC_AGGTRADES_PREFIX = "/data/futures/um/daily/aggTrades/"
SAFETY_FREE_DISK_MULTIPLIER = 1.25

REQUIRED_AVAILABILITY_COLUMNS = [
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

DOWNLOAD_MANIFEST_COLUMNS = REQUIRED_AVAILABILITY_COLUMNS + [
    "bookdepth_verified_earliest_date",
    "bookdepth_verified_latest_date",
]


class ManifestValidationBlocked(RuntimeError):
    """Raised when the matching aggTrades manifest is not safe to use."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def raw_target_dir(root: Path | None = None) -> Path:
    return (root or data_root()) / RAW_DIR_NAME


def logs_dir(root: Path | None = None) -> Path:
    return (root or data_root()) / LOGS_DIR_NAME


def path_is_inside(child: Path, parent: Path) -> bool:
    child_text = os.path.normcase(os.path.abspath(os.fspath(child)))
    parent_text = os.path.normcase(os.path.abspath(os.fspath(parent)))
    return child_text == parent_text or child_text.startswith(parent_text + os.sep)


def nearest_existing_path(path: Path) -> Path:
    probe = path.resolve()
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    return probe


def parse_int(value: Any) -> int | None:
    if value in ("", None):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def valid_date(value: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""))


def assert_public_aggtrades_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_ARCHIVE_HOST:
        raise ManifestValidationBlocked(f"blocked non-public Binance Data Vision URL: {url}")
    if not parsed.path.startswith(PUBLIC_AGGTRADES_PREFIX):
        raise ManifestValidationBlocked(f"blocked non-USD-M daily aggTrades URL: {url}")
    if "/bookDepth/" in parsed.path or "/klines/" in parsed.path:
        raise ManifestValidationBlocked(f"blocked non-aggTrades URL: {url}")
    if parsed.query:
        raise ManifestValidationBlocked(f"blocked URL with query parameters: {url}")


def derived_zip_path(row: dict[str, str], root: Path | None = None) -> Path:
    symbol = row.get("symbol", "")
    file_name = row.get("file_name", "")
    return raw_target_dir(root) / "aggTrades" / "daily" / symbol / file_name


def derived_checksum_path(row: dict[str, str], root: Path | None = None) -> Path:
    symbol = row.get("symbol", "")
    file_name = row.get("file_name", "")
    return logs_dir(root) / "checksums" / "aggTrades" / "daily" / symbol / f"{file_name}.CHECKSUM"


def read_csv_rows(path: Path, required_columns: list[str] | None = None) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise ManifestValidationBlocked(f"missing required CSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        missing = [column for column in (required_columns or []) if column not in fieldnames]
        if missing:
            raise ManifestValidationBlocked(f"CSV required columns missing in {path}: {missing}")
        rows = [dict(row) for row in reader]
    if required_columns and not rows:
        raise ManifestValidationBlocked(f"CSV has zero rows: {path}")
    return rows, fieldnames


def read_manifest() -> tuple[list[dict[str, str]], list[str]]:
    return read_csv_rows(DOWNLOAD_MANIFEST_CSV, DOWNLOAD_MANIFEST_COLUMNS)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ManifestValidationBlocked(f"missing required JSON: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ManifestValidationBlocked(f"JSON is not an object: {path}")
    return payload


def load_verified_bookdepth_coverage() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    summary = load_json(BOOKDEPTH_DOWNLOAD_SUMMARY_JSON)
    if summary.get("status") != "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED":
        raise ManifestValidationBlocked("bookDepth download summary is not PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED")
    if summary.get("replacement_checks_all_true") is not True:
        raise ManifestValidationBlocked("bookDepth download summary replacement checks are not all true")
    rows, _fieldnames = read_csv_rows(
        BOOKDEPTH_SYMBOL_COVERAGE_CSV,
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
    coverage: dict[str, dict[str, Any]] = {}
    invalid_rows: list[dict[str, str]] = []
    for row in rows:
        expected = parse_int(row.get("expected_file_count"))
        completed = parse_int(row.get("completed_file_count"))
        verified = parse_int(row.get("checksum_verified_count"))
        checksum_missing = parse_int(row.get("checksum_missing_count"))
        failed = parse_int(row.get("failed_count"))
        earliest = row.get("earliest_date", "")
        latest = row.get("latest_date", "")
        is_verified = (
            expected is not None
            and expected > 0
            and completed == expected
            and verified == expected
            and checksum_missing == 0
            and failed == 0
            and valid_date(earliest)
            and valid_date(latest)
            and earliest <= latest
        )
        if not is_verified:
            invalid_rows.append(row)
            continue
        coverage[row["symbol"]] = {
            "earliest_date": earliest,
            "latest_date": latest,
            "expected_file_count": expected,
        }
    if invalid_rows:
        raise ManifestValidationBlocked(f"bookDepth symbol coverage has unverified rows: {invalid_rows[:5]}")
    if len(coverage) != EXPECTED_SYMBOL_COUNT:
        raise ManifestValidationBlocked(f"verified bookDepth symbol count is not {EXPECTED_SYMBOL_COUNT}: {len(coverage)}")
    expected_count = sum(int(item["expected_file_count"]) for item in coverage.values())
    if parse_int(summary.get("expected_file_count")) != expected_count:
        raise ManifestValidationBlocked("bookDepth summary expected file count does not match symbol coverage")
    return coverage, summary


def load_gap_report() -> dict[str, Any]:
    rows, _fieldnames = read_csv_rows(
        AGGTRADES_GAPS_CSV,
        [
            "symbol",
            "file_date",
            "bookdepth_available_same_day",
            "aggtrades_available_same_day",
            "gap_type",
            "estimated_missing_size_bytes",
            "bookdepth_symbol_earliest",
            "bookdepth_symbol_latest",
        ],
    )
    gap_counts = Counter(row.get("gap_type", "") for row in rows)
    missing_while_bookdepth_exists = [
        row for row in rows if row.get("gap_type") == "MISSING_AGGTRADES_WHILE_BOOKDEPTH_EXISTS"
    ]
    return {
        "gap_row_count": len(rows),
        "gap_type_counts": dict(sorted(gap_counts.items())),
        "missing_aggtrades_while_bookdepth_exists_count": len(missing_while_bookdepth_exists),
        "missing_aggtrades_while_bookdepth_exists_examples": missing_while_bookdepth_exists[:20],
    }


def row_matches_verified_coverage(row: dict[str, str], coverage: dict[str, dict[str, Any]]) -> bool:
    symbol = row.get("symbol", "")
    if symbol not in coverage:
        return False
    file_date = row.get("file_date", "")
    if row.get("data_type") != "aggTrades" or row.get("frequency") != "daily":
        return False
    if row.get("status") != "AVAILABLE":
        return False
    if not parse_bool(row.get("bookdepth_available_same_day", "")):
        return False
    if not parse_bool(row.get("aggtrades_available_same_day", "")):
        return False
    if not valid_date(file_date):
        return False
    return coverage[symbol]["earliest_date"] <= file_date <= coverage[symbol]["latest_date"]


def normalized_manifest_row(row: dict[str, str], coverage: dict[str, dict[str, Any]], root: Path) -> dict[str, str]:
    result = {column: row.get(column, "") for column in REQUIRED_AVAILABILITY_COLUMNS}
    result["local_target_path"] = str(derived_zip_path(result, root))
    result["bookdepth_verified_earliest_date"] = str(coverage[result["symbol"]]["earliest_date"])
    result["bookdepth_verified_latest_date"] = str(coverage[result["symbol"]]["latest_date"])
    return result


def write_download_manifest(rows: list[dict[str, str]]) -> None:
    DOWNLOAD_MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    with DOWNLOAD_MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DOWNLOAD_MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in DOWNLOAD_MANIFEST_COLUMNS})
    with DOWNLOAD_MANIFEST_JSONL.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")


def symbol_extents(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for symbol in sorted({row["symbol"] for row in rows}):
        symbol_rows = [row for row in rows if row["symbol"] == symbol]
        dates = [row["file_date"] for row in symbol_rows if valid_date(row.get("file_date", ""))]
        sizes = [parse_int(row.get("size_bytes")) or 0 for row in symbol_rows]
        result[symbol] = {
            "file_count": len(symbol_rows),
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None,
            "estimated_size_bytes": sum(sizes),
            "estimated_size_gb": round(sum(sizes) / 1_000_000_000, 6),
        }
    return result


def disk_report(rows: list[dict[str, str]], root: Path) -> dict[str, Any]:
    total_estimated = 0
    already_present_size_matched = 0
    missing_size_rows = 0
    target_root = raw_target_dir(root)
    existing_sizes: dict[str, int] = {}
    if target_root.exists():
        for path in target_root.rglob("*.zip"):
            try:
                key = path.relative_to(target_root).as_posix().lower()
                existing_sizes[key] = path.stat().st_size
            except OSError:
                continue
    for row in rows:
        expected = parse_int(row.get("size_bytes"))
        if expected is None:
            missing_size_rows += 1
            continue
        total_estimated += expected
        relative_key = Path("aggTrades", "daily", row.get("symbol", ""), row.get("file_name", "")).as_posix().lower()
        if existing_sizes.get(relative_key) == expected:
            already_present_size_matched += expected
    estimated_remaining = max(total_estimated - already_present_size_matched, 0)
    disk_base = nearest_existing_path(target_root)
    usage = shutil.disk_usage(disk_base)
    required_free = int(estimated_remaining * SAFETY_FREE_DISK_MULTIPLIER)
    return {
        "disk_checked_path": str(disk_base),
        "free_bytes": usage.free,
        "estimated_total_size_bytes": total_estimated,
        "already_present_size_matched_bytes": already_present_size_matched,
        "estimated_remaining_download_bytes": estimated_remaining,
        "required_free_bytes": required_free,
        "free_disk_multiplier": SAFETY_FREE_DISK_MULTIPLIER,
        "missing_size_rows": missing_size_rows,
        "free_disk_check_passed": usage.free >= required_free,
        "estimated_total_size_gb": round(total_estimated / 1_000_000_000, 6),
        "estimated_remaining_download_gb": round(estimated_remaining / 1_000_000_000, 6),
        "required_free_gb": round(required_free / 1_000_000_000, 6),
        "free_gb": round(usage.free / 1_000_000_000, 6),
    }


def validate_manifest_rows(rows: list[dict[str, str]], root: Path) -> dict[str, Any]:
    urls = [row.get("url", "") for row in rows if row.get("url")]
    checksum_urls = [row.get("checksum_url", "") for row in rows if row.get("checksum_url")]
    duplicate_urls = sorted(url for url, count in Counter(urls).items() if count > 1)
    duplicate_checksum_urls = sorted(url for url, count in Counter(checksum_urls).items() if count > 1)
    invalid_urls: list[str] = []
    invalid_checksum_urls: list[str] = []
    invalid_rows: list[dict[str, str]] = []
    local_paths_inside_repo: list[str] = []
    derived_paths_inside_repo: list[str] = []
    checksum_paths_inside_repo: list[str] = []

    for row in rows:
        try:
            assert_public_aggtrades_url(row.get("url", ""))
        except ManifestValidationBlocked as exc:
            invalid_urls.append(str(exc))
        checksum_url = row.get("checksum_url", "")
        if checksum_url:
            try:
                if not checksum_url.endswith(".CHECKSUM"):
                    raise ManifestValidationBlocked(f"checksum URL does not end with .CHECKSUM: {checksum_url}")
                assert_public_aggtrades_url(checksum_url.removesuffix(".CHECKSUM"))
            except ManifestValidationBlocked as exc:
                invalid_checksum_urls.append(str(exc))
        if row.get("data_type") != "aggTrades" or row.get("frequency") != "daily":
            invalid_rows.append(row)
        if not valid_date(row.get("file_date", "")):
            invalid_rows.append(row)
        if not row.get("file_name", "").endswith(".zip"):
            invalid_rows.append(row)
        local_target = row.get("local_target_path", "")
        if local_target and path_is_inside(Path(local_target), REPO_ROOT):
            local_paths_inside_repo.append(local_target)
        derived_target = derived_zip_path(row, root)
        derived_checksum = derived_checksum_path(row, root)
        if path_is_inside(derived_target, REPO_ROOT):
            derived_paths_inside_repo.append(str(derived_target))
        if path_is_inside(derived_checksum, REPO_ROOT):
            checksum_paths_inside_repo.append(str(derived_checksum))

    return {
        "duplicate_urls": duplicate_urls,
        "duplicate_checksum_urls": duplicate_checksum_urls,
        "invalid_url_examples": invalid_urls[:50],
        "invalid_checksum_url_examples": invalid_checksum_urls[:50],
        "invalid_row_examples": invalid_rows[:50],
        "local_paths_inside_repo": local_paths_inside_repo[:50],
        "derived_paths_inside_repo": derived_paths_inside_repo[:50],
        "checksum_paths_inside_repo": checksum_paths_inside_repo[:50],
        "all_urls_valid": not invalid_urls,
        "all_checksum_urls_valid": not invalid_checksum_urls,
        "all_rows_are_aggtrades_daily": not invalid_rows,
        "no_duplicate_urls": not duplicate_urls,
        "no_duplicate_checksum_urls": not duplicate_checksum_urls,
        "checksum_url_coverage_complete": len(checksum_urls) == len(rows),
        "paths_outside_repo": not local_paths_inside_repo and not derived_paths_inside_repo and not checksum_paths_inside_repo,
    }


def build_report() -> dict[str, Any]:
    availability_rows, _availability_fields = read_csv_rows(AGGTRADES_AVAILABILITY_CSV, REQUIRED_AVAILABILITY_COLUMNS)
    aggtrades_summary = load_json(AGGTRADES_COVERAGE_JSON)
    gap_report = load_gap_report()
    coverage, bookdepth_summary = load_verified_bookdepth_coverage()
    root = data_root()
    target_root = raw_target_dir(root)
    checksum_root = logs_dir(root)

    matching_rows = [
        normalized_manifest_row(row, coverage, root)
        for row in availability_rows
        if row_matches_verified_coverage(row, coverage)
    ]
    matching_rows.sort(key=lambda item: (item["symbol"], item["file_date"], item["file_name"]))
    write_download_manifest(matching_rows)

    extents = symbol_extents(matching_rows)
    symbol_count = len(extents)
    expected_file_count = len(matching_rows)
    expected_bookdepth_file_count = sum(int(item["expected_file_count"]) for item in coverage.values())
    estimated_size_bytes = sum(parse_int(row.get("size_bytes")) or 0 for row in matching_rows)
    per_symbol_summary = aggtrades_summary.get("per_symbol", {})
    summary_matching_size = None
    if isinstance(per_symbol_summary, dict):
        values = [
            parse_int(value.get("estimated_bookdepth_matching_size_bytes"))
            for value in per_symbol_summary.values()
            if isinstance(value, dict)
        ]
        if values and all(value is not None for value in values):
            summary_matching_size = sum(int(value) for value in values if value is not None)
    validation = validate_manifest_rows(matching_rows, root)
    disk = disk_report(matching_rows, root)
    data_root_inside_repo = path_is_inside(root, REPO_ROOT)
    raw_inside_repo = path_is_inside(target_root, REPO_ROOT)
    logs_inside_repo = path_is_inside(checksum_root, REPO_ROOT)
    symbol_count_mismatches = {
        symbol: {
            "manifest_file_count": extents.get(symbol, {}).get("file_count", 0),
            "bookdepth_expected_file_count": item["expected_file_count"],
        }
        for symbol, item in coverage.items()
        if extents.get(symbol, {}).get("file_count", 0) != item["expected_file_count"]
    }

    checks = {
        "aggtrades_availability_manifest_exists": AGGTRADES_AVAILABILITY_CSV.exists(),
        "aggtrades_coverage_summary_exists": AGGTRADES_COVERAGE_JSON.exists(),
        "aggtrades_vs_bookdepth_gaps_exists": AGGTRADES_GAPS_CSV.exists(),
        "bookdepth_symbol_coverage_exists": BOOKDEPTH_SYMBOL_COVERAGE_CSV.exists(),
        "bookdepth_download_summary_exists": BOOKDEPTH_DOWNLOAD_SUMMARY_JSON.exists(),
        "bookdepth_download_verified_pass": bookdepth_summary.get("status") == "PASS_81_FULL_BOOKDEPTH_DOWNLOAD_VERIFIED",
        "unique_symbol_count_is_81": symbol_count == EXPECTED_SYMBOL_COUNT,
        "expected_file_count_matches_verified_bookdepth": expected_file_count == expected_bookdepth_file_count,
        "symbol_file_counts_match_verified_bookdepth": not symbol_count_mismatches,
        "no_missing_aggtrades_while_bookdepth_exists": gap_report["missing_aggtrades_while_bookdepth_exists_count"] == 0,
        "all_manifest_rows_match_bookdepth_same_day_flag": all(
            parse_bool(row.get("bookdepth_available_same_day", "")) for row in matching_rows
        ),
        "all_manifest_rows_match_aggtrades_same_day_flag": all(
            parse_bool(row.get("aggtrades_available_same_day", "")) for row in matching_rows
        ),
        "all_manifest_rows_inside_symbol_bookdepth_coverage": all(
            coverage[row["symbol"]]["earliest_date"] <= row["file_date"] <= coverage[row["symbol"]]["latest_date"]
            for row in matching_rows
        ),
        "download_manifest_csv_written": DOWNLOAD_MANIFEST_CSV.exists(),
        "download_manifest_jsonl_written": DOWNLOAD_MANIFEST_JSONL.exists(),
        "all_rows_are_aggtrades_daily": validation["all_rows_are_aggtrades_daily"],
        "all_urls_public_binance_data_vision_aggtrades": validation["all_urls_valid"],
        "checksum_url_coverage_complete": validation["checksum_url_coverage_complete"] and validation["all_checksum_urls_valid"],
        "no_duplicate_urls": validation["no_duplicate_urls"],
        "no_duplicate_checksum_urls": validation["no_duplicate_checksum_urls"],
        "manifest_local_target_paths_outside_repo": validation["paths_outside_repo"],
        "data_root_outside_repo": not data_root_inside_repo,
        "raw_target_dir_outside_repo": not raw_inside_repo,
        "logs_dir_outside_repo": not logs_inside_repo,
        "estimated_matching_size_bytes_recomputed": estimated_size_bytes > 0,
        "estimated_matching_size_matches_summary_if_available": (
            summary_matching_size is None or summary_matching_size == estimated_size_bytes
        ),
        "free_disk_space_ge_remaining_times_1_25": disk["free_disk_check_passed"],
        "no_raw_output_path_inside_repo": not any([data_root_inside_repo, raw_inside_repo, logs_inside_repo]),
    }
    replacement_checks_all_true = all(checks.values())
    if replacement_checks_all_true:
        status = "PASS_ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_MANIFEST_VALIDATED"
        next_module = "ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_DOWNLOADER_V1"
    elif not disk["free_disk_check_passed"]:
        status = "BLOCKED_INSUFFICIENT_DISK_FOR_FULL_MATCHING_AGGTRADES"
        next_module = "ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_DISK_REVIEW"
    else:
        status = "BLOCKED_ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_MANIFEST_VALIDATION"
        next_module = "ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_APPROVAL_OR_BLOCKER_REVIEW"

    return {
        "status": status,
        "created_at_utc": utc_now_text(),
        "task_name": "ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_DOWNLOAD_V1",
        "source_aggtrades_availability_manifest_csv": str(AGGTRADES_AVAILABILITY_CSV),
        "source_aggtrades_coverage_summary_json": str(AGGTRADES_COVERAGE_JSON),
        "source_aggtrades_vs_bookdepth_gaps_csv": str(AGGTRADES_GAPS_CSV),
        "source_bookdepth_symbol_coverage_csv": str(BOOKDEPTH_SYMBOL_COVERAGE_CSV),
        "source_bookdepth_download_summary_json": str(BOOKDEPTH_DOWNLOAD_SUMMARY_JSON),
        "download_manifest_csv": str(DOWNLOAD_MANIFEST_CSV),
        "download_manifest_jsonl": str(DOWNLOAD_MANIFEST_JSONL),
        "external_data_root": str(root),
        "raw_target_directory": str(target_root),
        "logs_directory": str(checksum_root),
        "source_availability_file_count": len(availability_rows),
        "source_availability_estimated_size_bytes": sum(parse_int(row.get("size_bytes")) or 0 for row in availability_rows),
        "source_availability_estimated_size_gb": round(
            sum(parse_int(row.get("size_bytes")) or 0 for row in availability_rows) / 1_000_000_000,
            6,
        ),
        "symbol_count": symbol_count,
        "symbols": sorted(extents),
        "expected_file_count": expected_file_count,
        "expected_bookdepth_file_count": expected_bookdepth_file_count,
        "estimated_matching_size_bytes": estimated_size_bytes,
        "estimated_matching_size_gb": round(estimated_size_bytes / 1_000_000_000, 6),
        "summary_estimated_bookdepth_matching_size_bytes": summary_matching_size,
        "summary_estimated_bookdepth_matching_size_gb": (
            round(summary_matching_size / 1_000_000_000, 6) if summary_matching_size is not None else None
        ),
        "earliest_global_date": min((item["earliest"] for item in extents.values() if item["earliest"]), default=None),
        "latest_global_date": max((item["latest"] for item in extents.values() if item["latest"]), default=None),
        "earliest_latest_by_symbol": extents,
        "symbol_file_count_mismatches": symbol_count_mismatches,
        "gap_report": gap_report,
        "duplicate_urls": validation["duplicate_urls"][:100],
        "duplicate_checksum_urls": validation["duplicate_checksum_urls"][:100],
        "invalid_url_examples": validation["invalid_url_examples"],
        "invalid_checksum_url_examples": validation["invalid_checksum_url_examples"],
        "invalid_row_examples": validation["invalid_row_examples"],
        "local_paths_inside_repo": validation["local_paths_inside_repo"],
        "derived_paths_inside_repo": validation["derived_paths_inside_repo"],
        "disk": disk,
        "validation_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "next_module": next_module,
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 full matching aggTrades manifest validation v1",
        "",
        f"status: {report['status']}",
        f"created_at_utc: {report['created_at_utc']}",
        f"symbol_count: {report.get('symbol_count', '')}",
        f"expected_file_count: {report.get('expected_file_count', '')}",
        f"expected_bookdepth_file_count: {report.get('expected_bookdepth_file_count', '')}",
        f"estimated_matching_size_gb: {report.get('estimated_matching_size_gb', '')}",
        f"source_availability_estimated_size_gb: {report.get('source_availability_estimated_size_gb', '')}",
        f"estimated_remaining_download_gb: {report.get('disk', {}).get('estimated_remaining_download_gb', '')}",
        f"required_free_gb: {report.get('disk', {}).get('required_free_gb', '')}",
        f"free_gb: {report.get('disk', {}).get('free_gb', '')}",
        f"earliest_global_date: {report.get('earliest_global_date', '')}",
        f"latest_global_date: {report.get('latest_global_date', '')}",
        f"download_manifest_csv: {report.get('download_manifest_csv', '')}",
        f"download_manifest_jsonl: {report.get('download_manifest_jsonl', '')}",
        f"external_data_root: {report.get('external_data_root', '')}",
        f"raw_target_directory: {report.get('raw_target_directory', '')}",
        f"logs_directory: {report.get('logs_directory', '')}",
        f"replacement_checks_all_true: {bool_text(bool(report['replacement_checks_all_true']))}",
        f"next_module: {report['next_module']}",
        "",
        "## Checks",
    ]
    for key, value in report["validation_checks"].items():
        lines.append(f"- {key}: {bool_text(bool(value))}")
    lines.extend(["", "## Notes"])
    lines.append("- The download manifest includes only aggTrades rows with verified same-day bookDepth coverage.")
    lines.append("- Older aggTrades history outside verified bookDepth coverage is deliberately excluded.")
    lines.append("- This validation is limited to public Binance Data Vision USD-M daily aggTrades archive files.")
    lines.append("- Raw ZIP targets resolve outside the git repository.")
    lines.append("- No account, private endpoint, execution, recommendation, or trading logic is part of this module.")
    lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_blocked(exc: Exception) -> dict[str, Any]:
    return {
        "status": "BLOCKED_ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_MANIFEST_VALIDATION",
        "created_at_utc": utc_now_text(),
        "exact_blocker": str(exc),
        "validation_checks": {"replacement_checks_all_true": False},
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_81_FULL_MATCHING_AGGTRADES_APPROVAL_OR_BLOCKER_REVIEW",
    }


def main() -> int:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = write_blocked(exc)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_report_md(report)
    print(f"status: {report['status']}")
    print(f"manifest_validation_json: {REPORT_JSON}")
    print(f"manifest_validation_md: {REPORT_MD}")
    print(f"download_manifest_csv: {DOWNLOAD_MANIFEST_CSV}")
    print(f"download_manifest_jsonl: {DOWNLOAD_MANIFEST_JSONL}")
    print(f"replacement_checks_all_true: {bool_text(bool(report['replacement_checks_all_true']))}")
    print(f"next_module: {report['next_module']}")
    return 0 if report["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
