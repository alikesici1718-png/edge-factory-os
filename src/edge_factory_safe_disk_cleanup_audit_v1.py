from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUTPUT_DIR = REPO_ROOT / "outputs"

AUDIT_SUMMARY_JSON = OUTPUT_DIR / "safe_disk_cleanup_audit_summary.json"
AUDIT_SUMMARY_MD = OUTPUT_DIR / "safe_disk_cleanup_audit_summary.md"
CANDIDATES_CSV = OUTPUT_DIR / "safe_disk_cleanup_delete_whitelist_candidates.csv"
REPORT_ONLY_CSV = OUTPUT_DIR / "safe_disk_cleanup_report_only_large_items.csv"
PROTECTED_MD = OUTPUT_DIR / "safe_disk_cleanup_protected_items.md"

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
REPORT_ONLY_DIR_NAMES = {"node_modules", ".next", "dist", "build"}
SAFE_FILE_NAMES = {".DS_Store", "Thumbs.db", ".coverage"}
SAFE_FILE_SUFFIXES = {".pyc", ".pyo", ".tmp", ".temp", ".part"}
RECENT_ALLOWED_SUFFIXES = {".pyc", ".tmp", ".part"}
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
LARGE_FILE_BYTES = 100 * 1024 * 1024
RECENT_SECONDS = 24 * 60 * 60
TOP_N = 20


@dataclass
class ItemRecord:
    path: str
    item_type: str
    reason: str
    size_bytes: int
    modified_time_utc: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_from_timestamp(timestamp: float | None) -> str:
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


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
    protected_tokens = {
        "edge_factory_external_data",
        "market_data",
        "raw_market_data",
        "binance_um_81_full_bookdepth_raw",
    }
    if any(part in protected_tokens for part in parts):
        return True
    if any(part.endswith("_raw") for part in parts):
        return True
    if any("bookdepth" in part or "aggtrades" in part for part in parts):
        return True
    if any(part.startswith("binance_um") and ("raw" in part or "data" in part) for part in parts):
        return True
    return False


def is_protected_path(path: Path) -> tuple[bool, str]:
    if not is_within(path, SCAN_ROOT):
        return True, "outside_scan_root"
    if has_git_part(path):
        return True, "inside_git_metadata"
    if looks_like_market_data_path(path):
        return True, "raw_or_external_market_data"
    if is_within(path, EXTERNAL_DATA_ROOT) or is_within(path, FULL_BOOKDEPTH_RAW):
        return True, "protected_external_data_root"
    return False, ""


def has_project_marker_nearby(path: Path) -> bool:
    current = path.parent
    scan_root = safe_resolve(SCAN_ROOT)
    while True:
        if any((current / marker).exists() for marker in PROJECT_MARKERS):
            return True
        if safe_resolve(current) == scan_root or current.parent == current:
            return False
        current = current.parent


def is_safe_cache_dir(path: Path) -> tuple[bool, str]:
    name = path.name
    if name in CACHE_DIR_NAMES:
        return True, f"whitelist_cache_folder:{name}"
    if name == ".cache" and has_project_marker_nearby(path) and not looks_like_market_data_path(path):
        return True, "whitelist_project_cache_folder:.cache"
    return False, ""


def is_file_whitelisted(path: Path) -> tuple[bool, str]:
    if path.name in SAFE_FILE_NAMES:
        return True, f"whitelist_file_name:{path.name}"
    suffix = path.suffix.lower()
    if suffix in SAFE_FILE_SUFFIXES:
        return True, f"whitelist_file_suffix:{suffix}"
    return False, ""


def is_recent(path: Path, now: datetime) -> bool:
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    except OSError:
        return False
    return (now - modified).total_seconds() < RECENT_SECONDS


def recent_file_is_allowed(path: Path) -> bool:
    return path.suffix.lower() in RECENT_ALLOWED_SUFFIXES


def path_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def directory_size(path: Path) -> int:
    total = 0
    for current_root, dirs, files in os.walk(path, topdown=True, followlinks=False):
        current_path = Path(current_root)
        dirs[:] = [name for name in dirs if not (current_path / name).is_symlink()]
        for file_name in files:
            child = current_path / file_name
            if child.is_symlink():
                continue
            total += file_size(child)
    return total


def directory_is_empty(path: Path) -> bool:
    try:
        with os.scandir(path) as entries:
            return next(entries, None) is None
    except OSError:
        return False


def under_any_git_worktree(path: Path) -> bool:
    current = safe_resolve(path)
    scan_root = safe_resolve(SCAN_ROOT)
    while True:
        if (current / ".git").exists():
            return True
        if current == scan_root or current.parent == current:
            return False
        current = current.parent


def should_report_only_directory(path: Path) -> tuple[bool, str]:
    name = path.name
    lower_name = name.lower()
    if name in REPORT_ONLY_DIR_NAMES:
        return True, f"report_only_build_or_dependency_folder:{name}"
    if "external_data" in lower_name:
        return True, "report_only_old_external_data_folder"
    if "pilot" in lower_name and ("data" in lower_name or "bookdepth" in lower_name or "aggtrades" in lower_name):
        return True, "report_only_pilot_data_folder"
    if ("duplicate" in lower_name or "copy" in lower_name) and "data" in lower_name:
        return True, "report_only_duplicate_looking_data_folder"
    return False, ""


def should_report_only_file(path: Path, size_bytes: int) -> tuple[bool, str]:
    suffix = path.suffix.lower()
    if size_bytes >= LARGE_FILE_BYTES and suffix in {".zip", ".csv", ".parquet", ".json", ".jsonl"}:
        return True, f"report_only_large_data_file:{suffix}"
    if size_bytes >= LARGE_FILE_BYTES and suffix in {".log", ".txt"}:
        return True, "report_only_log_over_100mb"
    return False, ""


def add_folder_size(folder_sizes: dict[str, int], path: Path, size_bytes: int) -> None:
    current = safe_resolve(path)
    scan_root = safe_resolve(SCAN_ROOT)
    while True:
        folder_sizes[str(current)] += size_bytes
        if current == scan_root or current.parent == current:
            break
        current = current.parent


def write_csv(path: Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def record_to_dict(record: ItemRecord) -> dict[str, object]:
    return {
        "path": record.path,
        "item_type": record.item_type,
        "reason": record.reason,
        "size_bytes": record.size_bytes,
        "size_gb": format_gb(record.size_bytes),
        "modified_time_utc": record.modified_time_utc,
    }


def top_records(mapping: dict[str, int], item_type: str) -> list[dict[str, object]]:
    return [
        {"path": path, "item_type": item_type, "size_bytes": size, "size_gb": format_gb(size)}
        for path, size in sorted(mapping.items(), key=lambda item: item[1], reverse=True)[:TOP_N]
    ]


def main() -> int:
    now = utc_now()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not SCAN_ROOT.exists():
        summary = {
            "status": "BLOCKED_SCAN_ROOT_MISSING",
            "replacement_checks_all_true": False,
            "next_module": "safe_disk_cleanup_blocker_review_v1",
            "scan_root": str(SCAN_ROOT),
            "error": "Scan root does not exist.",
        }
        AUDIT_SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        AUDIT_SUMMARY_MD.write_text("# Safe Disk Cleanup Audit\n\nStatus: BLOCKED_SCAN_ROOT_MISSING\n", encoding="utf-8")
        return 2

    candidates: list[ItemRecord] = []
    report_only: list[ItemRecord] = []
    protected_samples: list[tuple[str, str]] = []
    protected_count = 0
    folder_sizes: dict[str, int] = defaultdict(int)
    file_sizes: dict[str, int] = {}
    total_scanned_size = 0

    for current_root, dirs, files in os.walk(SCAN_ROOT, topdown=True, followlinks=False):
        current_path = Path(current_root)
        kept_dirs: list[str] = []

        for dir_name in dirs:
            dir_path = current_path / dir_name
            if dir_path.is_symlink():
                protected_count += 1
                if len(protected_samples) < 100:
                    protected_samples.append((str(dir_path), "symlink_directory_skipped"))
                continue

            protected, protected_reason = is_protected_path(dir_path)
            if protected:
                protected_count += 1
                if len(protected_samples) < 100:
                    protected_samples.append((str(dir_path), protected_reason))
                kept_dirs.append(dir_name)
                continue

            cache_ok, cache_reason = is_safe_cache_dir(dir_path)
            if cache_ok:
                size_bytes = directory_size(dir_path)
                total_scanned_size += size_bytes
                add_folder_size(folder_sizes, dir_path, size_bytes)
                candidates.append(
                    ItemRecord(
                        path=str(safe_resolve(dir_path)),
                        item_type="directory",
                        reason=cache_reason,
                        size_bytes=size_bytes,
                        modified_time_utc=iso_from_timestamp(path_mtime(dir_path)),
                    )
                )
                continue

            report_dir, report_reason = should_report_only_directory(dir_path)
            if report_dir:
                size_bytes = directory_size(dir_path)
                total_scanned_size += size_bytes
                add_folder_size(folder_sizes, dir_path, size_bytes)
                report_only.append(
                    ItemRecord(
                        path=str(safe_resolve(dir_path)),
                        item_type="directory",
                        reason=report_reason,
                        size_bytes=size_bytes,
                        modified_time_utc=iso_from_timestamp(path_mtime(dir_path)),
                    )
                )
                continue

            if directory_is_empty(dir_path):
                if under_any_git_worktree(dir_path):
                    protected_count += 1
                    if len(protected_samples) < 100:
                        protected_samples.append((str(dir_path), "empty_directory_inside_git_worktree_report_only"))
                elif is_recent(dir_path, now):
                    report_only.append(
                        ItemRecord(
                            path=str(safe_resolve(dir_path)),
                            item_type="directory",
                            reason="report_only_recent_empty_directory",
                            size_bytes=0,
                            modified_time_utc=iso_from_timestamp(path_mtime(dir_path)),
                        )
                    )
                else:
                    candidates.append(
                        ItemRecord(
                            path=str(safe_resolve(dir_path)),
                            item_type="directory",
                            reason="whitelist_empty_directory",
                            size_bytes=0,
                            modified_time_utc=iso_from_timestamp(path_mtime(dir_path)),
                        )
                    )
                continue

            kept_dirs.append(dir_name)

        dirs[:] = kept_dirs

        for file_name in files:
            file_path = current_path / file_name
            if file_path.is_symlink():
                protected_count += 1
                if len(protected_samples) < 100:
                    protected_samples.append((str(file_path), "symlink_file_skipped"))
                continue

            size_bytes = file_size(file_path)
            total_scanned_size += size_bytes
            file_sizes[str(safe_resolve(file_path))] = size_bytes
            add_folder_size(folder_sizes, file_path.parent, size_bytes)

            protected, protected_reason = is_protected_path(file_path)
            if protected:
                protected_count += 1
                if len(protected_samples) < 100:
                    protected_samples.append((str(file_path), protected_reason))
                continue

            whitelisted, reason = is_file_whitelisted(file_path)
            if whitelisted:
                suffix = file_path.suffix.lower()
                if suffix in NEVER_DELETE_SUFFIXES and suffix not in {".tmp", ".part"}:
                    protected_count += 1
                    if len(protected_samples) < 100:
                        protected_samples.append((str(file_path), "protected_data_or_report_extension"))
                    continue
                if is_recent(file_path, now) and not recent_file_is_allowed(file_path):
                    report_only.append(
                        ItemRecord(
                            path=str(safe_resolve(file_path)),
                            item_type="file",
                            reason="report_only_recent_whitelist_file_not_in_recent_exception",
                            size_bytes=size_bytes,
                            modified_time_utc=iso_from_timestamp(path_mtime(file_path)),
                        )
                    )
                    continue
                candidates.append(
                    ItemRecord(
                        path=str(safe_resolve(file_path)),
                        item_type="file",
                        reason=reason,
                        size_bytes=size_bytes,
                        modified_time_utc=iso_from_timestamp(path_mtime(file_path)),
                    )
                )
                continue

            report_file, report_reason = should_report_only_file(file_path, size_bytes)
            if report_file:
                report_only.append(
                    ItemRecord(
                        path=str(safe_resolve(file_path)),
                        item_type="file",
                        reason=report_reason,
                        size_bytes=size_bytes,
                        modified_time_utc=iso_from_timestamp(path_mtime(file_path)),
                    )
                )

    candidate_size = sum(item.size_bytes for item in candidates)
    report_only_size = sum(item.size_bytes for item in report_only)
    candidate_file_count = sum(1 for item in candidates if item.item_type == "file")
    candidate_folder_count = sum(1 for item in candidates if item.item_type == "directory")
    warning_most_reclaimable = report_only_size > candidate_size

    candidate_rows = [record_to_dict(item) for item in sorted(candidates, key=lambda item: item.size_bytes, reverse=True)]
    report_rows = [record_to_dict(item) for item in sorted(report_only, key=lambda item: item.size_bytes, reverse=True)]
    candidate_fields = ["path", "item_type", "reason", "size_bytes", "size_gb", "modified_time_utc"]
    report_fields = ["path", "item_type", "reason", "size_bytes", "size_gb", "modified_time_utc"]
    write_csv(CANDIDATES_CSV, candidate_rows, candidate_fields)
    write_csv(REPORT_ONLY_CSV, report_rows, report_fields)

    top_folders = top_records(folder_sizes, "directory")
    top_files = top_records(file_sizes, "file")

    summary = {
        "status": "PASS_SAFE_DISK_CLEANUP_AUDIT_DRY_RUN",
        "replacement_checks_all_true": True,
        "next_module": "safe_disk_cleanup_delete_dry_run_or_explicit_env_ack_v1",
        "generated_at_utc": now.isoformat(),
        "scan_root": str(SCAN_ROOT),
        "repo_root": str(REPO_ROOT),
        "total_scanned_size_bytes": total_scanned_size,
        "total_scanned_size_gb": format_gb(total_scanned_size),
        "strict_safe_delete_candidate_size_bytes": candidate_size,
        "strict_safe_delete_candidate_size_gb": format_gb(candidate_size),
        "candidate_file_count": candidate_file_count,
        "candidate_folder_count": candidate_folder_count,
        "report_only_large_items_size_bytes": report_only_size,
        "report_only_large_items_size_gb": format_gb(report_only_size),
        "report_only_large_items_count": len(report_only),
        "protected_paths_count": protected_count,
        "warning_most_reclaimable_space_is_not_whitelist": warning_most_reclaimable,
        "top_20_largest_folders": top_folders,
        "top_20_largest_files": top_files,
        "protected_external_paths": [str(EXTERNAL_DATA_ROOT), str(FULL_BOOKDEPTH_RAW)],
        "outputs": {
            "audit_summary_json": str(AUDIT_SUMMARY_JSON),
            "audit_summary_md": str(AUDIT_SUMMARY_MD),
            "delete_whitelist_candidates_csv": str(CANDIDATES_CSV),
            "report_only_large_items_csv": str(REPORT_ONLY_CSV),
            "protected_items_md": str(PROTECTED_MD),
        },
    }

    AUDIT_SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    protected_lines = [
        "# Safe Disk Cleanup Protected Items",
        "",
        f"Protected path count observed: {protected_count}",
        "",
        "External protected paths:",
        f"- {EXTERNAL_DATA_ROOT}",
        f"- {FULL_BOOKDEPTH_RAW}",
        "",
        "Sample protected or skipped paths:",
    ]
    for path, reason in protected_samples:
        protected_lines.append(f"- `{path}` - {reason}")
    PROTECTED_MD.write_text("\n".join(protected_lines) + "\n", encoding="utf-8")

    md_lines = [
        "# Safe Disk Cleanup Audit",
        "",
        f"Status: `{summary['status']}`",
        "",
        f"- Scan root: `{SCAN_ROOT}`",
        f"- Total scanned size: {summary['total_scanned_size_gb']} GB",
        f"- Strict safe-delete candidate size: {summary['strict_safe_delete_candidate_size_gb']} GB",
        f"- Candidate file count: {candidate_file_count}",
        f"- Candidate folder count: {candidate_folder_count}",
        f"- Report-only large item size: {summary['report_only_large_items_size_gb']} GB",
        f"- Report-only large item count: {len(report_only)}",
        f"- Protected paths count: {protected_count}",
        f"- Warning most reclaimable space is not whitelist: {warning_most_reclaimable}",
        "",
        "Deletion remains dry-run unless `EDGE_FACTORY_CLEANUP_DELETE_SAFE=YES` is set.",
        "",
        "Top 20 largest folders:",
    ]
    for item in top_folders:
        md_lines.append(f"- {item['size_gb']} GB - `{item['path']}`")
    md_lines.append("")
    md_lines.append("Top 20 largest files:")
    for item in top_files:
        md_lines.append(f"- {item['size_gb']} GB - `{item['path']}`")
    if warning_most_reclaimable:
        md_lines.extend(
            [
                "",
                "Warning: most reclaimable space is in report-only items. Manual approval is required before deleting those paths.",
            ]
        )
    AUDIT_SUMMARY_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
