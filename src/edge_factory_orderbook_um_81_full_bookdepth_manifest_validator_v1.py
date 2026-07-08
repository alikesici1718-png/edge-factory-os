#!/usr/bin/env python
"""Validate the 81-symbol Binance USD-M daily bookDepth manifest before full download."""

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
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
RAW_DIR_NAME = "binance_um_81_full_bookdepth_raw"
LOGS_DIR_NAME = "binance_um_81_full_bookdepth_logs"

MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.csv"
COVERAGE_JSON = OUTPUTS_DIR / "orderbook_um_bookdepth_coverage_summary.json"
MANIFEST_JSONL = OUTPUTS_DIR / "orderbook_um_bookdepth_availability_manifest.jsonl"
REPORT_JSON = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_manifest_validation.json"
REPORT_MD = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_manifest_validation.md"

EXPECTED_SYMBOL_COUNT = 81
PUBLIC_ARCHIVE_HOST = "data.binance.vision"
PUBLIC_BOOKDEPTH_PREFIX = "/data/futures/um/daily/bookDepth/"
SAFETY_FREE_DISK_MULTIPLIER = 1.25
REQUIRED_COLUMNS = [
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


class ManifestValidationBlocked(RuntimeError):
    """Raised when the manifest is not safe to use for the approved data download."""


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


def valid_date(value: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""))


def assert_public_bookdepth_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_ARCHIVE_HOST:
        raise ManifestValidationBlocked(f"blocked non-public Binance Data Vision URL: {url}")
    if not parsed.path.startswith(PUBLIC_BOOKDEPTH_PREFIX):
        raise ManifestValidationBlocked(f"blocked non-USD-M daily bookDepth URL: {url}")
    if "/aggTrades/" in parsed.path or "/klines/" in parsed.path:
        raise ManifestValidationBlocked(f"blocked non-bookDepth URL: {url}")
    if parsed.query:
        raise ManifestValidationBlocked(f"blocked URL with query parameters: {url}")


def derived_zip_path(row: dict[str, str], root: Path | None = None) -> Path:
    symbol = row.get("symbol", "")
    file_name = row.get("file_name", "")
    return raw_target_dir(root) / "bookDepth" / "daily" / symbol / file_name


def derived_checksum_path(row: dict[str, str], root: Path | None = None) -> Path:
    symbol = row.get("symbol", "")
    file_name = row.get("file_name", "")
    return logs_dir(root) / "checksums" / "bookDepth" / "daily" / symbol / f"{file_name}.CHECKSUM"


def read_manifest() -> tuple[list[dict[str, str]], list[str]]:
    if not MANIFEST_CSV.exists():
        raise ManifestValidationBlocked(f"manifest missing: {MANIFEST_CSV}")
    with MANIFEST_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing:
            raise ManifestValidationBlocked(f"manifest required columns missing: {missing}")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ManifestValidationBlocked("manifest has zero rows")
    return rows, fieldnames


def load_coverage_summary() -> dict[str, Any]:
    if not COVERAGE_JSON.exists():
        raise ManifestValidationBlocked(f"coverage summary missing: {COVERAGE_JSON}")
    payload = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ManifestValidationBlocked(f"coverage summary is not a JSON object: {COVERAGE_JSON}")
    return payload


def symbol_extents(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for symbol in sorted({row["symbol"] for row in rows}):
        symbol_rows = [row for row in rows if row["symbol"] == symbol]
        dates = [row["file_date_or_month"] for row in symbol_rows if valid_date(row.get("file_date_or_month", ""))]
        sizes = [parse_int(row.get("size_bytes")) or 0 for row in symbol_rows]
        result[symbol] = {
            "file_count": len(symbol_rows),
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None,
            "estimated_size_bytes": sum(sizes),
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
        relative_key = Path("bookDepth", "daily", row.get("symbol", ""), row.get("file_name", "")).as_posix().lower()
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
        "estimated_remaining_download_gb": round(estimated_remaining / 1_000_000_000, 6),
        "required_free_gb": round(required_free / 1_000_000_000, 6),
        "free_gb": round(usage.free / 1_000_000_000, 6),
    }


def build_report() -> dict[str, Any]:
    rows, _fieldnames = read_manifest()
    coverage = load_coverage_summary()
    root = data_root()
    target_root = raw_target_dir(root)
    checksum_root = logs_dir(root)
    available_rows = [row for row in rows if row.get("status") == "AVAILABLE"]
    symbols = sorted({row.get("symbol", "") for row in available_rows})
    urls = [row.get("url", "") for row in available_rows if row.get("url")]
    checksum_urls = [row.get("checksum_url", "") for row in available_rows if row.get("checksum_url")]
    duplicate_urls = sorted(url for url, count in Counter(urls).items() if count > 1)
    duplicate_checksum_urls = sorted(url for url, count in Counter(checksum_urls).items() if count > 1)
    invalid_urls: list[str] = []
    invalid_checksum_urls: list[str] = []
    invalid_rows: list[dict[str, str]] = []
    manifest_local_paths_inside_repo: list[str] = []
    derived_paths_inside_repo: list[str] = []
    checksum_paths_inside_repo: list[str] = []

    for row in available_rows:
        try:
            assert_public_bookdepth_url(row.get("url", ""))
        except ManifestValidationBlocked as exc:
            invalid_urls.append(str(exc))
        checksum_url = row.get("checksum_url", "")
        if checksum_url:
            try:
                assert_public_bookdepth_url(checksum_url.removesuffix(".CHECKSUM"))
                if not checksum_url.endswith(".CHECKSUM"):
                    raise ManifestValidationBlocked(f"checksum URL does not end with .CHECKSUM: {checksum_url}")
            except ManifestValidationBlocked as exc:
                invalid_checksum_urls.append(str(exc))
        if row.get("data_type") != "bookDepth" or row.get("frequency") != "daily":
            invalid_rows.append(row)
        if not valid_date(row.get("file_date_or_month", "")):
            invalid_rows.append(row)
        if not row.get("file_name", "").endswith(".zip"):
            invalid_rows.append(row)
        local_target = row.get("local_target_path", "")
        if local_target and path_is_inside(Path(local_target), REPO_ROOT):
            manifest_local_paths_inside_repo.append(local_target)
        derived_target = derived_zip_path(row, root)
        derived_checksum = derived_checksum_path(row, root)
        if path_is_inside(derived_target, REPO_ROOT):
            derived_paths_inside_repo.append(str(derived_target))
        if path_is_inside(derived_checksum, REPO_ROOT):
            checksum_paths_inside_repo.append(str(derived_checksum))

    extents = symbol_extents(available_rows)
    symbol_extent_failures = {
        symbol: value
        for symbol, value in extents.items()
        if not value.get("earliest") or not value.get("latest")
    }
    recomputed_size = sum(parse_int(row.get("size_bytes")) or 0 for row in available_rows)
    coverage_size = parse_int(coverage.get("total_estimated_size_bytes"))
    expected_count = len(available_rows)
    coverage_count = parse_int(coverage.get("total_file_count"))
    disk = disk_report(available_rows, root)
    data_root_inside_repo = path_is_inside(root, REPO_ROOT)
    raw_inside_repo = path_is_inside(target_root, REPO_ROOT)
    logs_inside_repo = path_is_inside(checksum_root, REPO_ROOT)
    checks = {
        "manifest_exists": MANIFEST_CSV.exists(),
        "coverage_summary_exists": COVERAGE_JSON.exists(),
        "manifest_jsonl_available_or_optional": MANIFEST_JSONL.exists(),
        "unique_symbol_count_is_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
        "coverage_missing_symbol_count_is_0": coverage.get("symbol_count_missing") == 0,
        "all_available_rows_are_bookdepth_daily": not invalid_rows,
        "all_urls_public_binance_data_vision_bookdepth": not invalid_urls,
        "manifest_local_target_paths_outside_repo": not manifest_local_paths_inside_repo,
        "derived_zip_paths_outside_repo": not derived_paths_inside_repo,
        "derived_checksum_paths_outside_repo": not checksum_paths_inside_repo,
        "data_root_outside_repo": not data_root_inside_repo,
        "raw_target_dir_outside_repo": not raw_inside_repo,
        "logs_dir_outside_repo": not logs_inside_repo,
        "estimated_total_size_present_or_recomputed": (coverage_size is not None or recomputed_size > 0),
        "expected_file_count_matches_coverage": coverage_count == expected_count,
        "earliest_latest_dates_per_symbol_present": not symbol_extent_failures,
        "no_duplicate_urls": not duplicate_urls,
        "no_duplicate_checksum_urls": not duplicate_checksum_urls,
        "checksum_url_coverage_complete": len(checksum_urls) == expected_count and not invalid_checksum_urls,
        "free_disk_space_ge_remaining_times_1_25": disk["free_disk_check_passed"],
        "no_raw_output_path_inside_repo": not any([data_root_inside_repo, raw_inside_repo, logs_inside_repo]),
    }
    replacement_checks_all_true = all(checks.values())
    return {
        "status": (
            "PASS_ORDERBOOK_UM_81_FULL_BOOKDEPTH_MANIFEST_VALIDATED"
            if replacement_checks_all_true
            else "BLOCKED_ORDERBOOK_UM_81_FULL_BOOKDEPTH_MANIFEST_VALIDATION"
        ),
        "created_at_utc": utc_now_text(),
        "task_name": "ORDERBOOK_UM_81_SYMBOL_FULL_BOOKDEPTH_DOWNLOAD_V1",
        "manifest_csv": str(MANIFEST_CSV),
        "manifest_jsonl": str(MANIFEST_JSONL) if MANIFEST_JSONL.exists() else "",
        "coverage_summary_json": str(COVERAGE_JSON),
        "external_data_root": str(root),
        "raw_target_directory": str(target_root),
        "logs_directory": str(checksum_root),
        "symbol_count": len(symbols),
        "symbols": symbols,
        "expected_file_count": expected_count,
        "coverage_total_file_count": coverage_count,
        "estimated_total_size_bytes": coverage_size if coverage_size is not None else recomputed_size,
        "estimated_total_size_gb": round((coverage_size if coverage_size is not None else recomputed_size) / 1_000_000_000, 6),
        "earliest_global_date": min((item["earliest"] for item in extents.values() if item["earliest"]), default=None),
        "latest_global_date": max((item["latest"] for item in extents.values() if item["latest"]), default=None),
        "earliest_latest_by_symbol": extents,
        "checksum_url_count": len(checksum_urls),
        "duplicate_urls": duplicate_urls[:100],
        "duplicate_checksum_urls": duplicate_checksum_urls[:100],
        "invalid_url_examples": invalid_urls[:50],
        "invalid_checksum_url_examples": invalid_checksum_urls[:50],
        "manifest_local_paths_inside_repo": manifest_local_paths_inside_repo[:50],
        "derived_paths_inside_repo": derived_paths_inside_repo[:50],
        "disk": disk,
        "validation_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "next_module": (
            "ORDERBOOK_UM_81_FULL_BOOKDEPTH_DOWNLOADER_V1"
            if replacement_checks_all_true
            else "ORDERBOOK_UM_81_FULL_BOOKDEPTH_APPROVAL_OR_BLOCKER_REVIEW"
        ),
    }


def write_report_md(report: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 81 full bookDepth manifest validation v1",
        "",
        f"status: {report['status']}",
        f"created_at_utc: {report['created_at_utc']}",
        f"symbol_count: {report['symbol_count']}",
        f"expected_file_count: {report['expected_file_count']}",
        f"estimated_total_size_gb: {report['estimated_total_size_gb']}",
        f"estimated_remaining_download_gb: {report['disk']['estimated_remaining_download_gb']}",
        f"required_free_gb: {report['disk']['required_free_gb']}",
        f"free_gb: {report['disk']['free_gb']}",
        f"earliest_global_date: {report['earliest_global_date']}",
        f"latest_global_date: {report['latest_global_date']}",
        f"external_data_root: {report['external_data_root']}",
        f"raw_target_directory: {report['raw_target_directory']}",
        f"logs_directory: {report['logs_directory']}",
        f"replacement_checks_all_true: {bool_text(report['replacement_checks_all_true'])}",
        f"next_module: {report['next_module']}",
        "",
        "## Checks",
    ]
    for key, value in report["validation_checks"].items():
        lines.append(f"- {key}: {bool_text(bool(value))}")
    lines.extend(["", "## Notes"])
    lines.append("- This validation is limited to public Binance Data Vision USD-M daily bookDepth archive files.")
    lines.append("- Raw ZIP targets resolve outside the git repository.")
    lines.append("- No strategy, recommendation, account, private endpoint, or execution logic is part of this module.")
    lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_blocked(exc: Exception) -> dict[str, Any]:
    return {
        "status": "BLOCKED_ORDERBOOK_UM_81_FULL_BOOKDEPTH_MANIFEST_VALIDATION",
        "created_at_utc": utc_now_text(),
        "exact_blocker": str(exc),
        "validation_checks": {"replacement_checks_all_true": False},
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_81_FULL_BOOKDEPTH_APPROVAL_OR_BLOCKER_REVIEW",
    }


def main() -> int:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        report = build_report()
    except Exception as exc:  # noqa: BLE001
        report = write_blocked(exc)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    if "disk" in report:
        write_report_md(report)
    else:
        REPORT_MD.write_text(
            "\n".join(
                [
                    "# Orderbook UM 81 full bookDepth manifest validation v1",
                    "",
                    f"status: {report['status']}",
                    f"exact_blocker: {report.get('exact_blocker', '')}",
                    "replacement_checks_all_true: false",
                    f"next_module: {report['next_module']}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    print(f"status: {report['status']}")
    print(f"manifest_validation_json: {REPORT_JSON}")
    print(f"manifest_validation_md: {REPORT_MD}")
    print(f"replacement_checks_all_true: {bool_text(bool(report['replacement_checks_all_true']))}")
    print(f"next_module: {report['next_module']}")
    return 0 if report["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
