"""
Reads the safe-to-delete whitelist candidates CSV produced by edge_factory_safe_disk_cleanup_audit_v1.py and physically deletes the approved files and directories, protecting data files (.csv, .json, .parquet, etc.) from deletion regardless of the whitelist.
Outputs a JSON/Markdown delete summary and per-item deleted/skipped CSVs to the repo outputs directory.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUTPUT_DIR = REPO_ROOT / "outputs"

CANDIDATES_CSV = OUTPUT_DIR / "safe_disk_cleanup_delete_whitelist_candidates.csv"
DELETE_SUMMARY_JSON = OUTPUT_DIR / "safe_disk_cleanup_delete_summary.json"
DELETE_SUMMARY_MD = OUTPUT_DIR / "safe_disk_cleanup_delete_summary.md"
DELETED_ITEMS_CSV = OUTPUT_DIR / "safe_disk_cleanup_deleted_items.csv"
SKIPPED_ITEMS_CSV = OUTPUT_DIR / "safe_disk_cleanup_skipped_items.csv"

EXTERNAL_DATA_ROOT = Path(r"C:\edge_factory_external_data")
FULL_BOOKDEPTH_RAW = EXTERNAL_DATA_ROOT / "binance_um_81_full_bookdepth_raw"

CACHE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "htmlcov",
}
SAFE_FILE_NAMES = {".DS_Store", "Thumbs.db", ".coverage"}
SAFE_FILE_SUFFIXES = {".pyc", ".pyo", ".tmp", ".temp", ".part"}
NEVER_DELETE_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".parquet",
    ".zip",
    ".7z",
    ".rar",
    ".db",
    ".sqlite",
    ".duckdb",
    ".pkl",
    ".feather",
    ".arrow",
}
PROJECT_MARKERS = {".git", "pyproject.toml", "package.json", "requirements.txt", "poetry.lock", "uv.lock"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_gb(size_bytes: int) -> float:
    return round(size_bytes / (1024**3), 6)


def safe_resolve(path: Path) -> Path:
    return path.resolve(strict=False)


def is_within(path: Path, root: Path) -> bool:
    try:
        safe_resolve(path).relative_to(safe_resolve(root))
        return True
    except ValueError:
        return False


def lower_parts(path: Path) -> list[str]:
    return [part.lower() for part in safe_resolve(path).parts]


def has_git_part(path: Path) -> bool:
    return ".git" in lower_parts(path)


def looks_like_market_data_path(path: Path) -> bool:
    parts = lower_parts(path)
    if any(part in {"edge_factory_external_data", "market_data", "raw_market_data", "binance_um_81_full_bookdepth_raw"} for part in parts):
        return True
    if any(part.endswith("_raw") for part in parts):
        return True
    if any("bookdepth" in part or "aggtrades" in part for part in parts):
        return True
    if any(part.startswith("binance_um") and ("raw" in part or "data" in part) for part in parts):
        return True
    return False


def has_project_marker_nearby(path: Path) -> bool:
    current = path.parent
    scan_root = safe_resolve(SCAN_ROOT)
    while True:
        if any((current / marker).exists() for marker in PROJECT_MARKERS):
            return True
        if safe_resolve(current) == scan_root or current.parent == current:
            return False
        current = current.parent


def directory_is_empty(path: Path) -> bool:
    try:
        with os.scandir(path) as entries:
            return next(entries, None) is None
    except OSError:
        return False


def is_safe_cache_dir(path: Path) -> bool:
    if path.name in CACHE_DIR_NAMES:
        return True
    return path.name == ".cache" and has_project_marker_nearby(path) and not looks_like_market_data_path(path)


def is_safe_directory_candidate(path: Path, reason: str) -> bool:
    if is_safe_cache_dir(path):
        return True
    if reason == "whitelist_empty_directory" and directory_is_empty(path):
        return True
    return False


def is_safe_file_candidate(path: Path) -> bool:
    suffix = path.suffix.lower()
    if suffix in NEVER_DELETE_SUFFIXES and suffix not in {".tmp", ".part"}:
        return False
    if path.name in SAFE_FILE_NAMES:
        return True
    return suffix in SAFE_FILE_SUFFIXES


def recheck_candidate(path: Path, item_type: str, reason: str) -> tuple[bool, str]:
    if not is_within(path, SCAN_ROOT):
        return False, "outside_scan_root"
    if has_git_part(path):
        return False, "inside_git_metadata"
    if is_within(path, EXTERNAL_DATA_ROOT) or is_within(path, FULL_BOOKDEPTH_RAW) or looks_like_market_data_path(path):
        return False, "protected_raw_or_external_market_data"
    if path.is_symlink():
        return False, "symlink_skipped"
    if not path.exists():
        return False, "path_missing"
    if item_type == "file":
        if not path.is_file():
            return False, "candidate_not_file"
        if not is_safe_file_candidate(path):
            return False, "file_not_strict_whitelist"
        return True, "rechecked_file_whitelist"
    if item_type == "directory":
        if not path.is_dir():
            return False, "candidate_not_directory"
        if not is_safe_directory_candidate(path, reason):
            return False, "directory_not_strict_whitelist"
        return True, "rechecked_directory_whitelist"
    return False, "unknown_item_type"


def path_size(path: Path) -> int:
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    if path.is_dir():
        for current_root, dirs, files in os.walk(path, topdown=True, followlinks=False):
            current_path = Path(current_root)
            dirs[:] = [name for name in dirs if not (current_path / name).is_symlink()]
            for file_name in files:
                child = current_path / file_name
                if child.is_symlink():
                    continue
                try:
                    total += child.stat().st_size
                except OSError:
                    continue
    return total


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    now = utc_now()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    delete_enabled = os.environ.get("EDGE_FACTORY_CLEANUP_DELETE_SAFE") == "YES"

    if not CANDIDATES_CSV.exists():
        summary = {
            "status": "BLOCKED_CANDIDATE_CSV_MISSING",
            "replacement_checks_all_true": False,
            "next_module": "safe_disk_cleanup_audit_v1",
            "candidate_csv": str(CANDIDATES_CSV),
            "delete_enabled": delete_enabled,
        }
        DELETE_SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        DELETE_SUMMARY_MD.write_text("# Safe Disk Cleanup Delete\n\nStatus: BLOCKED_CANDIDATE_CSV_MISSING\n", encoding="utf-8")
        return 2

    deleted_rows: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []
    attempted_count = 0
    deleted_count = 0
    skipped_count = 0
    deleted_bytes = 0
    dry_run_bytes = 0
    error_count = 0

    with CANDIDATES_CSV.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            attempted_count += 1
            raw_path = row.get("path", "")
            item_type = row.get("item_type", "")
            reason = row.get("reason", "")
            path = Path(raw_path)
            ok, recheck_reason = recheck_candidate(path, item_type, reason)
            size_before = path_size(path) if path.exists() else 0
            base_row = {
                "path": str(path),
                "item_type": item_type,
                "reason": reason,
                "recheck_reason": recheck_reason,
                "size_bytes": size_before,
                "size_gb": format_gb(size_before),
                "timestamp_utc": now.isoformat(),
            }

            if not ok:
                skipped_count += 1
                skipped_rows.append({**base_row, "status": "SKIPPED_RECHECK_FAILED"})
                continue

            if not delete_enabled:
                skipped_count += 1
                dry_run_bytes += size_before
                skipped_rows.append({**base_row, "status": "DRY_RUN_NO_DELETE"})
                continue

            try:
                if item_type == "file":
                    path.unlink()
                elif item_type == "directory":
                    if directory_is_empty(path):
                        path.rmdir()
                    elif is_safe_cache_dir(path):
                        shutil.rmtree(path)
                    else:
                        skipped_count += 1
                        skipped_rows.append({**base_row, "status": "SKIPPED_DIRECTORY_NOT_CACHE_OR_EMPTY"})
                        continue
                else:
                    skipped_count += 1
                    skipped_rows.append({**base_row, "status": "SKIPPED_UNKNOWN_ITEM_TYPE"})
                    continue
                deleted_count += 1
                deleted_bytes += size_before
                deleted_rows.append({**base_row, "status": "DELETED"})
            except Exception as exc:  # noqa: BLE001 - cleanup must log and continue safely.
                error_count += 1
                skipped_count += 1
                skipped_rows.append({**base_row, "status": "ERROR_DELETE_FAILED", "error_message": str(exc)})

    if not delete_enabled:
        status = "DRY_RUN_NO_DELETION_PERFORMED"
    elif error_count:
        status = "FAIL_SAFE_DISK_CLEANUP_DELETE_ERRORS"
    else:
        status = "PASS_SAFE_DISK_CLEANUP_DELETE_SAFE_COMPLETED"

    summary = {
        "status": status,
        "replacement_checks_all_true": error_count == 0,
        "next_module": "safe_disk_cleanup_manual_review_v1",
        "generated_at_utc": now.isoformat(),
        "scan_root": str(SCAN_ROOT),
        "repo_root": str(REPO_ROOT),
        "candidate_csv": str(CANDIDATES_CSV),
        "delete_enabled": delete_enabled,
        "attempted_candidate_count": attempted_count,
        "deleted_count": deleted_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "deleted_size_bytes": deleted_bytes,
        "deleted_size_gb": format_gb(deleted_bytes),
        "dry_run_candidate_size_bytes": dry_run_bytes,
        "dry_run_candidate_size_gb": format_gb(dry_run_bytes),
        "outputs": {
            "delete_summary_json": str(DELETE_SUMMARY_JSON),
            "delete_summary_md": str(DELETE_SUMMARY_MD),
            "deleted_items_csv": str(DELETED_ITEMS_CSV),
            "skipped_items_csv": str(SKIPPED_ITEMS_CSV),
        },
    }

    fields = [
        "path",
        "item_type",
        "reason",
        "recheck_reason",
        "size_bytes",
        "size_gb",
        "timestamp_utc",
        "status",
        "error_message",
    ]
    write_csv(DELETED_ITEMS_CSV, deleted_rows, fields)
    write_csv(SKIPPED_ITEMS_CSV, skipped_rows, fields)
    DELETE_SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_lines = [
        "# Safe Disk Cleanup Delete",
        "",
        f"Status: `{status}`",
        "",
        f"- Delete enabled: {delete_enabled}",
        f"- Attempted candidates: {attempted_count}",
        f"- Deleted count: {deleted_count}",
        f"- Skipped count: {skipped_count}",
        f"- Error count: {error_count}",
        f"- Deleted size: {summary['deleted_size_gb']} GB",
        f"- Dry-run candidate size: {summary['dry_run_candidate_size_gb']} GB",
        "",
        "Actual deletion requires `EDGE_FACTORY_CLEANUP_DELETE_SAFE=YES`.",
        "Report-only large items are never deleted by this module.",
    ]
    DELETE_SUMMARY_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
