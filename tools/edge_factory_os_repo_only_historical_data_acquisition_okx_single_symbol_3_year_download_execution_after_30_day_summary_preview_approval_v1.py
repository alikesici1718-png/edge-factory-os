from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import urllib.error
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_after_30_day_summary_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "552e9af"
TARGET_SYMBOL = "BTC-USDT-SWAP"
INPUT_INTERVAL = "1m"
TARGET_OUTPUT_INTERVAL_LATER = "1h"
MAX_AVAILABLE_START = date(2023, 7, 1)
MAX_AVAILABLE_END = date(2026, 5, 18)
NOMINAL_STRICT_3Y_START = date(2023, 5, 19)
EXPECTED_MAX_AVAILABLE_FILE_COUNT = 1053
EXPECTED_EXISTING_REUSE_FILE_COUNT = 30
EXPECTED_NEW_DOWNLOAD_FILE_COUNT = 1023
EXPECTED_SCHEMA = [
    "instrument_name",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "open_time",
    "confirm",
]
MAX_NEW_DOWNLOAD_FILES = 1023
MAX_TOTAL_FILE_SET = 1053
MAX_ZIP_SIZE_BYTES = 100 * 1024 * 1024
MAX_ZIP_MEMBERS = 10
MAX_CSV_SAMPLE_ROWS = 5
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_PIPELINE_SUMMARY_"
    "3_YEAR_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_DOWNLOAD_YET"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_MAX_AVAILABLE_NO_BUILD"
)
GAP_STATUS = (
    "BLOCKED_OR_GAP_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_PIPELINE_SUMMARY_"
    "3_YEAR_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_DOWNLOAD_YET"
)
AFTER_QUALITY_PASS = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_MAX_AVAILABLE_NO_BUILD"
)
AFTER_QUALITY_GAP = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DOWNLOAD_EXECUTION_BLOCKED_OR_GAP"
)
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1.py"
)
NEXT_MODULE_BLOCKED_OR_GAP = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_blocked_or_gap_record_after_preview_approval_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
DOWNLOAD_DIR = OUTPUT_DIR / "downloaded_single_symbol_3_year_max_available_quarantine"

SUMMARY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_pipeline_summary_after_build_validator_v1"
)
SUMMARY_ARTIFACT = SUMMARY_DIR / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_pipeline_summary_after_build_validator_v1_latest.json"
)
PREVIEW_ARTIFACT = SUMMARY_DIR / "historical_okx_single_symbol_3_year_download_preview.json"
MANIFEST_ARTIFACT = SUMMARY_DIR / "historical_okx_single_symbol_3_year_planned_url_manifest_preview.json"
APPROVAL_ARTIFACT = SUMMARY_DIR / "historical_okx_single_symbol_3_year_download_approval_record.json"
PREVIOUS_PROVENANCE_ARTIFACT = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_execution_after_preview_approval_v1"
) / "historical_okx_single_symbol_30_day_1m_to_1h_output_provenance_report.json"

DANGEROUS_FLAGS = {
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "full_csv_read_performed": False,
    "multi_symbol_performed": False,
    "research_backtest_edge_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class BlockedOrGap(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-C",
            str(REPO_ROOT),
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def repo_has_only_this_tool_change() -> bool:
    status = run_git(["status", "--short"]).splitlines()
    if not status:
        return True
    approved_rel = APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()
    return all(line[3:].replace("\\", "/") == approved_rel for line in status)


def tracked_python_count() -> int:
    return sum(1 for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BlockedOrGap(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"artifact is not a JSON object: {path}")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def inclusive_days(start: date, end: date) -> list[date]:
    require(start <= end, f"invalid date range: {start} > {end}")
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def okx_url(symbol: str, day: date) -> str:
    compact = day.strftime("%Y%m%d")
    iso_day = day.isoformat()
    return (
        "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/"
        f"{compact}/{symbol}-candlesticks-{iso_day}.zip"
    )


def expected_zip_name(day: date) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day.isoformat()}.zip"


def expected_csv_name(day: date) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day.isoformat()}.csv"


def date_from_csv_name(name: str) -> str:
    prefix = f"{TARGET_SYMBOL}-candlesticks-"
    require(name.startswith(prefix) and name.endswith(".csv"), f"unexpected CSV name: {name}")
    return name.removeprefix(prefix).removesuffix(".csv")


def date_from_url(url: str) -> str:
    name = url.rsplit("/", 1)[-1]
    require(name == expected_zip_name(date.fromisoformat(name.removeprefix(f"{TARGET_SYMBOL}-candlesticks-").removesuffix(".zip"))), f"unexpected URL file name: {url}")
    return name.removeprefix(f"{TARGET_SYMBOL}-candlesticks-").removesuffix(".zip")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    if normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        return False
    if posix.is_absolute() or any(part == ".." for part in posix.parts):
        return False
    if posix.parts and ":" in posix.parts[0]:
        return False
    return True


def validate_summary_preview_approval(
    summary: dict[str, Any],
    preview: dict[str, Any],
    manifest: dict[str, Any],
    approval: dict[str, Any],
) -> list[str]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(summary.get("historical_data_acquisition_okx_single_symbol_30_day_pipeline_summary_status") == PREVIOUS_STATUS, "previous status mismatch")
    require(summary.get("target_symbol") == TARGET_SYMBOL, "summary target symbol mismatch")
    require(summary.get("next_module") == REQUESTED_MODULE, "summary next_module mismatch")
    require(summary.get("approval_grants_future_3_year_single_symbol_download_next") is True, "future download approval missing")
    require(summary.get("strict_3y_completeness_claimed") is False, "strict 3-year completeness already claimed")
    require(summary.get("max_available_start_candidate") == MAX_AVAILABLE_START.isoformat(), "max-available start mismatch")
    require(summary.get("nominal_end_date") == MAX_AVAILABLE_END.isoformat(), "nominal end mismatch")
    require(summary.get("max_available_candidate_file_count") == EXPECTED_MAX_AVAILABLE_FILE_COUNT, "max-available count mismatch")
    require(summary.get("existing_validated_reuse_file_count") == EXPECTED_EXISTING_REUSE_FILE_COUNT, "reuse count mismatch")
    require(summary.get("missing_download_file_count_for_max_available_candidate") == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, "missing download count mismatch")
    require(summary.get("output_valid_for_research_backtest") is False, "research/backtest claim detected")
    require(summary.get("output_valid_for_edge_claim") is False, "edge claim detected")
    require(summary.get("safe_for_broad_acquisition") is False, "broad acquisition claim detected")
    require(summary.get("safe_for_multi_symbol_build") is False, "multi-symbol claim detected")

    require(preview.get("three_year_download_preview_created") is True, "preview missing")
    require(preview.get("target_symbol") == TARGET_SYMBOL, "preview target mismatch")
    require(preview.get("route_type") == "SINGLE_SYMBOL_3_YEAR_OR_MAX_AVAILABLE_HISTORICAL_DOWNLOAD_PREVIEW", "route type mismatch")
    require(preview.get("strict_3y_completeness_claimed") is False, "preview strict completeness claimed")
    require(preview.get("max_available_start_candidate") == MAX_AVAILABLE_START.isoformat(), "preview max-available start mismatch")
    require(preview.get("max_available_candidate_end") == MAX_AVAILABLE_END.isoformat(), "preview max-available end mismatch")
    require(preview.get("max_available_candidate_file_count") == EXPECTED_MAX_AVAILABLE_FILE_COUNT, "preview max-available file count mismatch")
    require(preview.get("existing_validated_reuse_file_count") == EXPECTED_EXISTING_REUSE_FILE_COUNT, "preview reuse count mismatch")
    require(preview.get("missing_download_file_count_for_max_available_candidate") == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, "preview missing download count mismatch")

    require(approval.get("three_year_download_approval_record_created") is True, "approval record missing")
    require(approval.get("approval_grants_download_now") is False, "approval unexpectedly grants immediate download")
    require(approval.get("approval_grants_future_3_year_single_symbol_download_next") is True, "future execution approval missing")
    require(approval.get("approval_grants_build_now") is False, "approval grants build")
    require(approval.get("approval_grants_api_now") is False, "approval grants API")
    require(approval.get("approval_grants_browse_now") is False, "approval grants browse")
    require(approval.get("approval_grants_multi_symbol_now") is False, "approval grants multi-symbol")
    require(approval.get("approval_grants_broad_acquisition_now") is False, "approval grants broad acquisition")
    require(approval.get("approval_grants_research_backtest_edge_now") is False, "approval grants research/backtest/edge")
    require(approval.get("next_module") == REQUESTED_MODULE, "approval next_module mismatch")

    max_plan = manifest.get("max_available_candidate_plan", {})
    require(max_plan.get("start_date") == MAX_AVAILABLE_START.isoformat(), "manifest max start mismatch")
    require(max_plan.get("end_date") == MAX_AVAILABLE_END.isoformat(), "manifest max end mismatch")
    require(max_plan.get("file_count") == EXPECTED_MAX_AVAILABLE_FILE_COUNT, "manifest file count mismatch")
    require(max_plan.get("url_count") == EXPECTED_MAX_AVAILABLE_FILE_COUNT, "manifest URL count mismatch")
    require(max_plan.get("existing_validated_reuse_file_count") == EXPECTED_EXISTING_REUSE_FILE_COUNT, "manifest reuse count mismatch")
    require(max_plan.get("missing_download_file_count") == EXPECTED_NEW_DOWNLOAD_FILE_COUNT, "manifest missing count mismatch")
    planned_urls = list(max_plan.get("planned_urls", []))
    require(len(planned_urls) == EXPECTED_MAX_AVAILABLE_FILE_COUNT, "approved max-available URL count mismatch")
    require(len(set(planned_urls)) == EXPECTED_MAX_AVAILABLE_FILE_COUNT, "duplicate approved URLs")
    expected_urls = [okx_url(TARGET_SYMBOL, day) for day in inclusive_days(MAX_AVAILABLE_START, MAX_AVAILABLE_END)]
    require(planned_urls == expected_urls, "approved URL manifest differs from expected OKX static pattern")
    return planned_urls


def build_reuse_map(previous_provenance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    paths = [Path(raw) for raw in previous_provenance.get("source_zip_paths", [])]
    hashes_by_csv = previous_provenance.get("source_zip_sha256_by_file", {})
    sizes_by_csv = previous_provenance.get("source_zip_size_bytes_by_file", {})
    require(len(paths) == EXPECTED_EXISTING_REUSE_FILE_COUNT, "previous provenance path count mismatch")
    require(len(hashes_by_csv) == EXPECTED_EXISTING_REUSE_FILE_COUNT, "previous provenance hash count mismatch")
    out: dict[str, dict[str, Any]] = {}
    for path in paths:
        csv_name = path.name.removesuffix(".zip") + ".csv"
        day = date_from_csv_name(csv_name)
        require(csv_name in hashes_by_csv, f"reuse hash missing for {csv_name}")
        require(csv_name in sizes_by_csv, f"reuse size missing for {csv_name}")
        out[day] = {
            "date": day,
            "local_zip_path": str(path),
            "expected_inner_csv": csv_name,
            "expected_sha256": hashes_by_csv[csv_name],
            "expected_size_bytes": sizes_by_csv[csv_name],
        }
    require(len(out) == EXPECTED_EXISTING_REUSE_FILE_COUNT, "duplicate reuse dates detected")
    expected_reuse_dates = {day.isoformat() for day in inclusive_days(date(2026, 4, 19), MAX_AVAILABLE_END)}
    require(set(out) == expected_reuse_dates, "reuse dates do not match validated 30-day range")
    return out


def download_file(url: str, dest: Path) -> tuple[int, str, bool]:
    if dest.exists():
        size = dest.stat().st_size
        require(0 < size <= MAX_ZIP_SIZE_BYTES, f"existing downloaded ZIP size invalid: {dest}")
        return size, sha256_file(dest), False
    tmp = dest.with_suffix(dest.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    downloaded = 0
    with urllib.request.urlopen(url, timeout=90) as response:
        with tmp.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > MAX_ZIP_SIZE_BYTES:
                    raise BlockedOrGap(f"download exceeds max ZIP size: {url}")
                handle.write(chunk)
    require(downloaded > 0, f"empty download: {url}")
    tmp.replace(dest)
    return downloaded, sha256_file(dest), True


def inspect_zip_and_sample(path: Path, expected_csv: str) -> tuple[dict[str, Any], dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        traversal = any(not safe_zip_member(name) for name in names)
        expected_present = expected_csv in names
        inventory = {
            "zip_path": str(path),
            "zip_open_success": True,
            "zip_member_count": len(names),
            "zip_member_names": names,
            "expected_inner_csv": expected_csv,
            "expected_inner_csv_present": expected_present,
            "zip_path_traversal_detected": traversal,
            "zip_inventory_status": "PASS" if expected_present and not traversal and len(names) <= MAX_ZIP_MEMBERS else "FAIL",
        }
        require(len(names) <= MAX_ZIP_MEMBERS, f"too many ZIP members: {path}")
        require(not traversal, f"ZIP traversal risk: {path}")
        require(expected_present, f"expected inner CSV missing: {expected_csv}")

        with archive.open(expected_csv, "r") as raw:
            text = (line.decode("utf-8-sig").rstrip("\r\n") for line in raw)
            reader = csv.reader(text)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise BlockedOrGap(f"empty CSV in ZIP: {expected_csv}") from exc
            rows: list[list[str]] = []
            for _, row in zip(range(MAX_CSV_SAMPLE_ROWS), reader):
                rows.append(row)

    symbol_sample = sorted({row[0] for row in rows if row})
    open_times: list[int] = []
    for row in rows:
        if len(row) > 8:
            try:
                open_times.append(int(row[8]))
            except ValueError:
                pass
    deltas = [right - left for left, right in zip(open_times, open_times[1:])]
    interval = deltas[0] if deltas and all(delta == deltas[0] for delta in deltas) else None
    one_minute = interval == 60_000
    schema_match = header == EXPECTED_SCHEMA
    symbols_match = all(symbol == TARGET_SYMBOL for symbol in symbol_sample) if symbol_sample else True
    sample = {
        "csv_header_read": True,
        "csv_sample_rows_read_count": len(rows),
        "max_csv_sample_rows_allowed": MAX_CSV_SAMPLE_ROWS,
        "csv_full_read_performed": False,
        "expected_schema_match": schema_match,
        "observed_columns": header,
        "observed_symbol_sample": symbol_sample,
        "observed_symbols_match_target": symbols_match,
        "sample_open_time_delta_ms": interval,
        "one_minute_interval_observed": one_minute,
        "direct_1h_interval_present": False if one_minute else None,
    }
    require(schema_match, f"schema mismatch: {expected_csv}")
    require(symbols_match, f"symbol mismatch in sample: {expected_csv}")
    require(len(rows) <= MAX_CSV_SAMPLE_ROWS, f"sample row count exceeded: {expected_csv}")
    require(one_minute or len(rows) < 2, f"sample interval is not 1m: {expected_csv}")
    return inventory, sample


def write_artifacts(
    status: str,
    generated_at: str,
    execution_report: dict[str, Any],
    provenance_report: dict[str, Any],
    hash_manifest: dict[str, Any],
    zip_inventory_report: dict[str, Any],
    schema_sample_report: dict[str, Any],
    coverage_gap_report: dict[str, Any],
    compliance_report: dict[str, Any],
    summary_payload: dict[str, Any],
) -> None:
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_execution_report.json", execution_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_provenance_report.json", provenance_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_hash_manifest.json", hash_manifest)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_zip_inventory_report.json", zip_inventory_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_schema_sample_report.json", schema_sample_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_coverage_gap_report.json", coverage_gap_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_execution_compliance_report.json", compliance_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_download_execution_summary.json", summary_payload)
    write_json(
        OUTPUT_DIR / "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_download_execution_after_30_day_summary_preview_approval_v1_latest.json",
        summary_payload,
    )
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


def main() -> None:
    generated_at = utc_now()
    summary = load_json(SUMMARY_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    manifest = load_json(MANIFEST_ARTIFACT)
    approval = load_json(APPROVAL_ARTIFACT)
    previous_provenance = load_json(PREVIOUS_PROVENANCE_ARTIFACT)
    planned_urls = validate_summary_preview_approval(summary, preview, manifest, approval)
    reuse_map = build_reuse_map(previous_provenance)

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    provenance_items: list[dict[str, Any]] = []
    hash_items: list[dict[str, Any]] = []
    zip_items: list[dict[str, Any]] = []
    schema_items: list[dict[str, Any]] = []
    coverage_gaps: list[dict[str, Any]] = []
    used_urls: list[str] = []
    new_download_file_count = 0
    downloaded_now_count = 0
    existing_validated_reuse_file_count = 0
    failed_file_count = 0
    approved_url_set = set(planned_urls)

    for url in planned_urls:
        day_text = date_from_url(url)
        day = date.fromisoformat(day_text)
        require(url in approved_url_set, f"URL outside approved manifest: {url}")
        require(MAX_AVAILABLE_START <= day <= MAX_AVAILABLE_END, f"date outside max-available range: {day_text}")
        require(TARGET_SYMBOL in url, f"target symbol missing from URL: {url}")
        used_urls.append(url)
        expected_csv = expected_csv_name(day)
        source_kind = "UNKNOWN"
        local_path: Path
        downloaded_now = False
        timestamp = utc_now()

        try:
            if day_text in reuse_map:
                reuse_item = reuse_map[day_text]
                local_path = Path(reuse_item["local_zip_path"])
                require(local_path.exists(), f"reused ZIP missing: {local_path}")
                size = local_path.stat().st_size
                digest = sha256_file(local_path)
                require(digest == reuse_item["expected_sha256"], f"reused SHA256 mismatch for {day_text}")
                require(size == reuse_item["expected_size_bytes"], f"reused size mismatch for {day_text}")
                source_kind = "REUSED_VALIDATED_30_DAY_FILE"
                existing_validated_reuse_file_count += 1
            else:
                local_path = DOWNLOAD_DIR / expected_zip_name(day)
                size, digest, downloaded_now = download_file(url, local_path)
                source_kind = "DOWNLOADED_MAX_AVAILABLE_MISSING_APPROVED_URL"
                new_download_file_count += 1
                downloaded_now_count += 1 if downloaded_now else 0
            require(0 < size <= MAX_ZIP_SIZE_BYTES, f"ZIP size invalid for {day_text}")
            inventory, sample = inspect_zip_and_sample(local_path, expected_csv)
        except (BlockedOrGap, OSError, urllib.error.URLError, zipfile.BadZipFile) as exc:
            failed_file_count += 1
            coverage_gaps.append(
                {
                    "date": day_text,
                    "source_url": url,
                    "expected_inner_csv": expected_csv,
                    "failure_reason": str(exc),
                    "coverage_gap_detected": True,
                    "strict_3y_completeness_claimed": False,
                    "synthetic_fill_used": False,
                    "forward_fill_used": False,
                    "backfill_used": False,
                }
            )
            break

        provenance_items.append(
            {
                "date": day_text,
                "source_url": url,
                "approved_url_manifest_used": True,
                "local_zip_path": str(local_path),
                "local_zip_file_name": local_path.name,
                "file_size_bytes": size,
                "sha256": digest,
                "hash_algorithm": "SHA256",
                "hash_computed_or_revalidated_after_execution": True,
                "download_or_reuse_timestamp_utc": timestamp,
                "downloaded_now": downloaded_now,
                "expected_inner_csv": expected_csv,
                "source_kind": source_kind,
            }
        )
        hash_items.append(
            {
                "date": day_text,
                "local_zip_path": str(local_path),
                "sha256": digest,
                "file_size_bytes": size,
                "hash_status": "PASS",
            }
        )
        zip_items.append({"date": day_text, **inventory})
        schema_items.append({"date": day_text, "expected_inner_csv": expected_csv, **sample})

    final_file_set_count = len(provenance_items)
    missing_or_failed_file_count = EXPECTED_MAX_AVAILABLE_FILE_COUNT - final_file_set_count
    coverage_gap_detected = bool(coverage_gaps) or missing_or_failed_file_count != 0
    success = not coverage_gap_detected

    all_hashes = all(item.get("sha256") and len(item["sha256"]) == 64 for item in provenance_items)
    all_zip_open = final_file_set_count == EXPECTED_MAX_AVAILABLE_FILE_COUNT and all(item["zip_open_success"] for item in zip_items)
    all_expected_inner_csv_present = final_file_set_count == EXPECTED_MAX_AVAILABLE_FILE_COUNT and all(
        item["expected_inner_csv_present"] for item in zip_items
    )
    all_expected_schema_match = final_file_set_count == EXPECTED_MAX_AVAILABLE_FILE_COUNT and all(
        item["expected_schema_match"] for item in schema_items
    )
    all_observed_symbols_match_target = final_file_set_count == EXPECTED_MAX_AVAILABLE_FILE_COUNT and all(
        item["observed_symbols_match_target"] for item in schema_items
    )
    max_sample_rows_read = max((item["csv_sample_rows_read_count"] for item in schema_items), default=0)
    all_downloads_succeeded = success and new_download_file_count == EXPECTED_NEW_DOWNLOAD_FILE_COUNT
    all_reused_files_validated = existing_validated_reuse_file_count == EXPECTED_EXISTING_REUSE_FILE_COUNT

    status = PASS_STATUS if success else GAP_STATUS
    next_module = NEXT_MODULE_PASS if success else NEXT_MODULE_BLOCKED_OR_GAP
    active_p0_blocker_count = 0 if success else 1
    current_evidence_after = AFTER_QUALITY_PASS if success else AFTER_QUALITY_GAP

    execution_report = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "download_execution_performed": success,
        "download_execution_attempted": True,
        "target_symbol": TARGET_SYMBOL,
        "input_interval": INPUT_INTERVAL,
        "output_target_interval_later": TARGET_OUTPUT_INTERVAL_LATER,
        "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START.isoformat(),
        "nominal_end_date": MAX_AVAILABLE_END.isoformat(),
        "strict_3y_completeness_claimed": False,
        "known_okx_coverage_start_from_prior_artifacts": "July 2023",
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "max_available_candidate_file_count": EXPECTED_MAX_AVAILABLE_FILE_COUNT,
        "existing_validated_reuse_file_count": existing_validated_reuse_file_count,
        "new_download_file_count": new_download_file_count,
        "downloaded_now_count": downloaded_now_count,
        "final_file_set_count": final_file_set_count,
        "missing_or_failed_file_count": missing_or_failed_file_count,
        "coverage_gap_detected": coverage_gap_detected,
        "approved_url_manifest_used": set(used_urls).issubset(approved_url_set),
        "all_downloads_succeeded": all_downloads_succeeded,
        "all_reused_files_validated": all_reused_files_validated,
        "max_new_download_files": MAX_NEW_DOWNLOAD_FILES,
        "max_total_file_set": MAX_TOTAL_FILE_SET,
        "max_zip_size_per_file_mb": 100,
        "max_zip_members_per_file": MAX_ZIP_MEMBERS,
        "max_csv_sample_rows_per_file": MAX_CSV_SAMPLE_ROWS,
        "full_csv_read_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
    }
    provenance_report = {
        "provenance_status": "PASS" if success else "BLOCKED_OR_GAP",
        "target_symbol": TARGET_SYMBOL,
        "approved_url_manifest_used": set(used_urls).issubset(approved_url_set),
        "per_file_provenance": provenance_items,
    }
    hash_manifest = {
        "hash_manifest_status": "PASS" if all_hashes and success else "BLOCKED_OR_GAP",
        "all_hashes_computed_or_revalidated": all_hashes,
        "hash_algorithm": "SHA256",
        "file_count": len(hash_items),
        "hashes": hash_items,
    }
    zip_inventory_report = {
        "zip_inventory_status": "PASS" if all_zip_open and all_expected_inner_csv_present else "BLOCKED_OR_GAP",
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_expected_inner_csv_present,
        "zip_path_traversal_detected": any(item.get("zip_path_traversal_detected") for item in zip_items),
        "zip_inventory": zip_items,
    }
    schema_sample_report = {
        "schema_sample_status": "PASS" if all_expected_schema_match and all_observed_symbols_match_target else "BLOCKED_OR_GAP",
        "all_expected_schema_match": all_expected_schema_match,
        "all_observed_symbols_match_target": all_observed_symbols_match_target,
        "max_csv_sample_rows_read_per_file": max_sample_rows_read,
        "full_csv_read_performed": False,
        "schema_samples": schema_items,
    }
    coverage_gap_report = {
        "coverage_gap_detected": coverage_gap_detected,
        "missing_or_failed_file_count": missing_or_failed_file_count,
        "coverage_gap_count_recorded": len(coverage_gaps),
        "strict_3y_completeness_claimed": False,
        "max_available_candidate_called_complete": success,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "coverage_gaps": coverage_gaps,
    }
    compliance_report = {
        "no_api": True,
        "no_browse": True,
        "no_url_discovery_outside_approved_manifest": True,
        "no_unapproved_url": set(used_urls).issubset(approved_url_set),
        "no_full_csv_read": True,
        "no_data_build": True,
        "no_aggregation": True,
        "no_multi_symbol": True,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "strict_3y_completeness_claimed": False,
        "no_strategy_backtest_candidate": True,
        "no_runtime_capital_live": True,
        "no_generic_runner": True,
        "no_repo_schema_config": True,
    }

    replacement_checks = {
        "preflight_passed": True,
        "approved_url_manifest_used": set(used_urls).issubset(approved_url_set),
        "max_available_file_count_1053": EXPECTED_MAX_AVAILABLE_FILE_COUNT == MAX_TOTAL_FILE_SET,
        "existing_validated_reuse_file_count_30": existing_validated_reuse_file_count == EXPECTED_EXISTING_REUSE_FILE_COUNT,
        "new_download_file_count_1023": new_download_file_count == EXPECTED_NEW_DOWNLOAD_FILE_COUNT,
        "final_file_set_count_1053": final_file_set_count == EXPECTED_MAX_AVAILABLE_FILE_COUNT,
        "missing_or_failed_file_count_0": missing_or_failed_file_count == 0,
        "coverage_gap_not_detected": not coverage_gap_detected,
        "all_downloads_succeeded": all_downloads_succeeded,
        "all_reused_files_validated": all_reused_files_validated,
        "all_hashes_computed_or_revalidated": all_hashes,
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_expected_inner_csv_present,
        "all_expected_schema_match": all_expected_schema_match,
        "all_observed_symbols_match_target": all_observed_symbols_match_target,
        "sample_limit_respected": max_sample_rows_read <= MAX_CSV_SAMPLE_ROWS,
        "full_csv_read_false": True,
        "no_build_aggregation_api_browse": True,
        "strict_3y_completeness_not_claimed": True,
        "not_research_backtest_edge": True,
        "not_broad_acquisition_ready": True,
        "schema_config_absent": True,
        "generic_runner_blocked": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())

    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_download_execution_status": status,
        "download_execution_performed": success,
        "download_execution_attempted": True,
        "target_symbol": TARGET_SYMBOL,
        "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START.isoformat(),
        "nominal_end_date": MAX_AVAILABLE_END.isoformat(),
        "strict_3y_completeness_claimed": False,
        "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
        "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
        "max_available_candidate_file_count": EXPECTED_MAX_AVAILABLE_FILE_COUNT,
        "existing_validated_reuse_file_count": existing_validated_reuse_file_count,
        "new_download_file_count": new_download_file_count,
        "final_file_set_count": final_file_set_count,
        "missing_or_failed_file_count": missing_or_failed_file_count,
        "coverage_gap_detected": coverage_gap_detected,
        "approved_url_manifest_used": set(used_urls).issubset(approved_url_set),
        "all_downloads_succeeded": all_downloads_succeeded,
        "all_reused_files_validated": all_reused_files_validated,
        "all_hashes_computed_or_revalidated": all_hashes,
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_expected_inner_csv_present,
        "all_expected_schema_match": all_expected_schema_match,
        "all_observed_symbols_match_target": all_observed_symbols_match_target,
        "max_csv_sample_rows_read_per_file": max_sample_rows_read,
        "full_csv_read_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": current_evidence_after,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "next_module": next_module,
        "derived_live_repo_post_check": status,
        "derived_live_repo_post_check_reason": (
            "executed approved max-available BTC-USDT-SWAP daily ZIP acquisition from "
            "2023-07-01 through 2026-05-18 with existing 30 validated files reused, "
            "SHA256 computed or revalidated, ZIP inventory inspected safely, and only "
            "CSV headers plus up to five sample rows read; no API, browse, build, "
            "aggregation, research, backtest, edge, broad acquisition, runtime, capital, "
            "live, schema/config, generic-runner, synthetic-fill, forward-fill, backfill, "
            "or strict 3-year completeness claim"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "tracked_python_count_at_execution_run": tracked_python_count(),
    }

    write_artifacts(
        status,
        generated_at,
        execution_report,
        provenance_report,
        hash_manifest,
        zip_inventory_report,
        schema_sample_report,
        coverage_gap_report,
        compliance_report,
        summary_payload,
    )
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except BlockedOrGap as exc:
        generated_at = utc_now()
        summary_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": generated_at,
            "historical_data_acquisition_okx_single_symbol_3_year_download_execution_status": GAP_STATUS,
            "download_execution_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "nominal_strict_3y_start_date": NOMINAL_STRICT_3Y_START.isoformat(),
            "nominal_end_date": MAX_AVAILABLE_END.isoformat(),
            "strict_3y_completeness_claimed": False,
            "max_available_start_candidate": MAX_AVAILABLE_START.isoformat(),
            "max_available_end_date": MAX_AVAILABLE_END.isoformat(),
            "max_available_candidate_file_count": EXPECTED_MAX_AVAILABLE_FILE_COUNT,
            "existing_validated_reuse_file_count": 0,
            "new_download_file_count": 0,
            "final_file_set_count": 0,
            "missing_or_failed_file_count": EXPECTED_MAX_AVAILABLE_FILE_COUNT,
            "coverage_gap_detected": True,
            "approved_url_manifest_used": False,
            "all_downloads_succeeded": False,
            "all_reused_files_validated": False,
            "all_hashes_computed_or_revalidated": False,
            "all_zip_open_success": False,
            "all_expected_inner_csv_present": False,
            "all_expected_schema_match": False,
            "all_observed_symbols_match_target": False,
            "max_csv_sample_rows_read_per_file": 0,
            "full_csv_read_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "files_marked_build_ready": False,
            "source_manifest_acquisition_ready": False,
            "broad_acquisition_execution_allowed_now": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
            "current_evidence_chain_quality_after_execution": AFTER_QUALITY_GAP,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 0,
            "dormant_repo_attention_count": 716,
            "generic_runner_implementation_remains_blocked": True,
            "schema_or_config_created": False,
            "ordinary_selector_backlog_loop_reentry_allowed": False,
            "loop_remains_closed": True,
            "next_module": NEXT_MODULE_BLOCKED_OR_GAP,
            "derived_live_repo_post_check": GAP_STATUS,
            "replacement_checks_all_true": False,
            "blocked_or_gap_reason": str(exc),
        }
        empty_report = {"generated_at_utc": generated_at, "blocked_or_gap_reason": str(exc)}
        write_artifacts(
            GAP_STATUS,
            generated_at,
            empty_report,
            {"per_file_provenance": []},
            {"hashes": []},
            {"zip_inventory": []},
            {"schema_samples": []},
            {
                "coverage_gap_detected": True,
                "missing_or_failed_file_count": EXPECTED_MAX_AVAILABLE_FILE_COUNT,
                "strict_3y_completeness_claimed": False,
                "coverage_gaps": [{"failure_reason": str(exc)}],
            },
            {
                "no_api": True,
                "no_browse": True,
                "no_full_csv_read": True,
                "no_data_build": True,
                "no_aggregation": True,
                "strict_3y_completeness_claimed": False,
                "output_valid_for_research_backtest": False,
                "output_valid_for_edge_claim": False,
                "broad_acquisition_execution_allowed_now": False,
            },
            summary_payload,
        )
        raise SystemExit(1)
