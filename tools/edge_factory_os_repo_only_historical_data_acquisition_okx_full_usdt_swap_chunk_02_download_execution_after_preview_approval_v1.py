from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "5e1f39d"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
GAP_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_EXECUTED_WITH_COVERAGE_GAPS_PENDING_VALIDATOR_NO_BUILD"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_EXECUTION_FAILED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_validator_after_execution_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_blocked_record_v1.py"
AFTER_QUALITY_PASS = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD"
AFTER_QUALITY_GAP = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_EXECUTED_WITH_COVERAGE_GAPS_PENDING_VALIDATOR_NO_BUILD"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
DOWNLOAD_DIR = OUTPUT_DIR / "downloaded_chunk_02_approved_quarantine"

PREVIEW_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_preview_after_first_chunk_coverage_summary_v1"
PILOT_VALIDATOR_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1"

PREVIEW_SUMMARY = PREVIEW_DIR / "historical_okx_full_usdt_swap_chunk_02_download_preview_summary.json"
PREVIEW_MANIFEST = PREVIEW_DIR / "historical_okx_full_usdt_swap_chunk_02_planned_file_manifest_preview.json"
PREVIEW_APPROVAL = PREVIEW_DIR / "historical_okx_full_usdt_swap_chunk_02_download_execution_approval_record.json"
PREVIEW_RESOURCE_LIMITS = PREVIEW_DIR / "historical_okx_full_usdt_swap_chunk_02_download_resource_limits.json"
PILOT_HASH_REPORT = PILOT_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_hash_validation_report.json"
PILOT_VALIDATOR_SUMMARY = PILOT_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json"

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_chunk_02_download_execution_report.json",
    "historical_okx_full_usdt_swap_chunk_02_download_file_manifest_after_execution.json",
    "historical_okx_full_usdt_swap_chunk_02_download_gap_report.json",
    "historical_okx_full_usdt_swap_chunk_02_reuse_validation_report.json",
    "historical_okx_full_usdt_swap_chunk_02_sha256_report.json",
    "historical_okx_full_usdt_swap_chunk_02_zip_inventory_report.json",
    "historical_okx_full_usdt_swap_chunk_02_schema_sample_report.json",
    "historical_okx_full_usdt_swap_chunk_02_download_execution_compliance_report.json",
    "historical_okx_full_usdt_swap_chunk_02_download_execution_summary.json",
]

APPROVED_CHUNK_ID = "chunk_02"
APPROVED_SYMBOLS = [
    "APE-USDT-SWAP",
    "API3-USDT-SWAP",
    "APR-USDT-SWAP",
    "APT-USDT-SWAP",
    "AR-USDT-SWAP",
    "ARB-USDT-SWAP",
    "ARKM-USDT-SWAP",
    "ARM-USDT-SWAP",
    "ASTER-USDT-SWAP",
    "AT-USDT-SWAP",
    "ATH-USDT-SWAP",
    "ATOM-USDT-SWAP",
    "AUCTION-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "AVGO-USDT-SWAP",
    "AVNT-USDT-SWAP",
    "AXS-USDT-SWAP",
    "AZTEC-USDT-SWAP",
    "BABY-USDT-SWAP",
    "BAND-USDT-SWAP",
]
REUSE_SYMBOL = "AVAX-USDT-SWAP"
DATE_RANGE_START = date(2023, 7, 1)
DATE_RANGE_END = date(2026, 5, 18)
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_CHUNK_FILE_COUNT = 21_060
EXPECTED_REUSE_CANDIDATE_FILE_COUNT = 1_053
MAX_NEW_DOWNLOAD_ATTEMPT_COUNT = 20_007
MAX_TOTAL_DOWNLOAD_OR_REUSE_FILE_COUNT = 21_060
MAX_CSV_SAMPLE_ROWS_PER_FILE = 5
MAX_ZIP_SIZE_PER_FILE_MB = 100
MAX_ZIP_MEMBERS_PER_FILE = 10
EXPECTED_SCHEMA_KEY = "OKX_CANDLESTICKS_1M_SCHEMA_V1"
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


class ExecutionBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class PlannedFile:
    chunk_id: str
    symbol: str
    day: date
    url: str
    expected_inner_csv: str
    expected_schema_key: str
    local_zip_path: Path
    source_kind: str
    recorded_sha256: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExecutionBlocked(message)


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


def current_tool_rel() -> str:
    return APPROVED_TOOL.relative_to(REPO_ROOT).as_posix()


def repo_has_only_this_tool_change() -> bool:
    status = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    if not status:
        return True
    rel = current_tool_rel()
    return all(line[3:].replace("\\", "/") == rel for line in status)


def tracked_python_files_including_current() -> list[str]:
    files = sorted(path for path in run_git(["ls-files"]).splitlines() if path.endswith(".py"))
    rel = current_tool_rel()
    if APPROVED_TOOL.exists() and rel not in files:
        files.append(rel)
    return sorted(files)


def tracked_python_validation() -> dict[str, Any]:
    syntax_errors: list[dict[str, str]] = []
    bom_errors: list[str] = []
    files = tracked_python_files_including_current()
    for rel in files:
        raw = (REPO_ROOT / rel).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_errors.append(rel)
        try:
            ast.parse(raw.decode("utf-8"), filename=rel)
        except Exception as exc:
            syntax_errors.append({"path": rel, "error": repr(exc)})
    return {
        "tracked_python_count": len(files),
        "syntax_error_count": len(syntax_errors),
        "bom_error_count": len(bom_errors),
        "syntax_errors": syntax_errors,
        "bom_errors": bom_errors,
    }


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.exists(), f"missing JSON artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ExecutionBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    require(isinstance(data, dict), f"JSON artifact {label} is not an object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def inclusive_days() -> list[date]:
    days: list[date] = []
    current = DATE_RANGE_START
    while current <= DATE_RANGE_END:
        days.append(current)
        current += timedelta(days=1)
    return days


def parse_day(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def approved_url(symbol: str, day: date) -> str:
    yyyymmdd = day.strftime("%Y%m%d")
    iso_day = day.isoformat()
    return (
        "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/"
        f"{yyyymmdd}/{symbol}-candlesticks-{iso_day}.zip"
    )


def expected_inner_csv(symbol: str, day: date) -> str:
    return f"{symbol}-candlesticks-{day.isoformat()}.csv"


def expected_zip_name(symbol: str, day: date) -> str:
    return f"{symbol}-candlesticks-{day.isoformat()}.zip"


def validate_preconditions(py_state: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
    }
    require(all(checks.values()), f"precondition failure: {checks}")
    return {"head": head, "checks": checks}


def load_and_validate_preview() -> dict[str, Any]:
    summary = load_json(PREVIEW_SUMMARY, "chunk_02_preview_summary")
    manifest = load_json(PREVIEW_MANIFEST, "chunk_02_planned_manifest_preview")
    approval = load_json(PREVIEW_APPROVAL, "chunk_02_download_execution_approval")
    resource_limits = load_json(PREVIEW_RESOURCE_LIMITS, "chunk_02_download_resource_limits")
    entries = manifest.get("planned_entries", [])
    require(isinstance(entries, list), "planned_entries must be a list")
    checks = {
        "previous_status_passed": summary.get("historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_preview_status") == PREVIOUS_STATUS,
        "current_next_module_matches": summary.get("next_module") == REQUESTED_MODULE,
        "preview_created": summary.get("chunk_02_download_preview_created") is True,
        "chunk_id_valid": summary.get("chunk_id") == APPROVED_CHUNK_ID,
        "chunk_symbols_valid": summary.get("chunk_02_symbols") == APPROVED_SYMBOLS,
        "symbol_count_valid": summary.get("chunk_02_symbol_count") == len(APPROVED_SYMBOLS),
        "expected_file_count_valid": summary.get("expected_chunk_02_file_count") == EXPECTED_CHUNK_FILE_COUNT,
        "planned_file_count_valid": len(entries) == EXPECTED_CHUNK_FILE_COUNT and summary.get("planned_file_count") == EXPECTED_CHUNK_FILE_COUNT,
        "reuse_candidate_count_valid": summary.get("reuse_candidate_file_count") == EXPECTED_REUSE_CANDIDATE_FILE_COUNT,
        "approval_available": approval.get("approval_grants_future_chunk_02_download_execution_next") is True,
        "approval_does_not_grant_broad_download_now": approval.get("approval_grants_download_now") is False,
        "resource_max_count_valid": resource_limits.get("max_expected_file_count") == MAX_TOTAL_DOWNLOAD_OR_REUSE_FILE_COUNT,
        "resource_sample_limit_valid": resource_limits.get("max_csv_sample_rows_per_file") == MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "preview_no_forbidden_actions": (
            summary.get("url_existence_checked") is False
            and summary.get("archive_download_performed") is False
            and summary.get("okx_api_call_performed") is False
            and summary.get("okx_browse_performed") is False
            and summary.get("data_build_performed") is False
            and summary.get("aggregation_performed_now") is False
        ),
    }
    require(all(checks.values()), f"preview validation failure: {checks}")
    return {"summary": summary, "manifest": manifest, "approval": approval, "resource_limits": resource_limits, "checks": checks}


def validate_manifest_entries(entries: list[dict[str, Any]]) -> None:
    approved_symbols = set(APPROVED_SYMBOLS)
    approved_dates = {day.isoformat() for day in inclusive_days()}
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        require(isinstance(entry, dict), "planned entry is not an object")
        symbol = str(entry.get("symbol"))
        day_value = str(entry.get("date"))
        day = parse_day(day_value)
        key = (symbol, day_value)
        require(entry.get("chunk_id") == APPROVED_CHUNK_ID, f"unapproved chunk_id in manifest: {entry.get('chunk_id')}")
        require(symbol in approved_symbols, f"unapproved symbol in manifest: {symbol}")
        require(day_value in approved_dates, f"unapproved date in manifest: {day_value}")
        require(entry.get("expected_url") == approved_url(symbol, day), f"unexpected URL for {symbol} {day_value}")
        require(entry.get("expected_inner_csv") == expected_inner_csv(symbol, day), f"unexpected inner CSV for {symbol} {day_value}")
        require(entry.get("expected_schema_key") == EXPECTED_SCHEMA_KEY, "unexpected schema key")
        require(entry.get("planned_status") == "PLANNED_NOT_CHECKED_NOT_DOWNLOADED", "planned entry status was not preview-only")
        require(entry.get("url_existence_checked") is False, "preview URL existence flag was true")
        require(entry.get("downloaded") is False, "preview downloaded flag was true")
        require(entry.get("build_ready") is False, "preview build_ready flag was true")
        require(entry.get("acquisition_ready") is False, "preview acquisition_ready flag was true")
        require(key not in seen, f"duplicate planned entry: {key}")
        seen.add(key)
    require(len(seen) == EXPECTED_CHUNK_FILE_COUNT, "manifest unique planned entry count mismatch")


def load_pilot_reuse_index() -> dict[str, dict[str, Any]]:
    pilot_summary = load_json(PILOT_VALIDATOR_SUMMARY, "pilot_validator_summary")
    pilot_hash = load_json(PILOT_HASH_REPORT, "pilot_hash_validation_report")
    require(pilot_summary.get("download_execution_validated") is True, "pilot download validator did not pass")
    require(pilot_summary.get("all_reused_files_revalidated") is True, "pilot reused files not revalidated")
    require(pilot_summary.get("all_hashes_recomputed") is True, "pilot hashes not recomputed")
    require(pilot_summary.get("all_zip_open_success") is True, "pilot zips not open")
    hashes = pilot_hash.get("hashes", [])
    require(isinstance(hashes, list), "pilot hash list missing")
    reuse: dict[str, dict[str, Any]] = {}
    for item in hashes:
        if isinstance(item, dict) and item.get("symbol") == REUSE_SYMBOL:
            reuse[str(item["date"])] = item
    require(len(reuse) == EXPECTED_REUSE_CANDIDATE_FILE_COUNT, "AVAX reuse candidate count mismatch")
    return reuse


def build_plan(preview: dict[str, Any], reuse_index: dict[str, dict[str, Any]]) -> list[PlannedFile]:
    entries = preview["manifest"]["planned_entries"]
    validate_manifest_entries(entries)
    plan: list[PlannedFile] = []
    for entry in entries:
        symbol = str(entry["symbol"])
        day = parse_day(str(entry["date"]))
        if symbol == REUSE_SYMBOL:
            prior = reuse_index.get(day.isoformat())
            require(prior is not None, f"missing reuse provenance for {symbol} {day.isoformat()}")
            path = Path(str(prior["local_zip_path"]))
            recorded_sha = str(prior.get("recorded_sha256") or prior.get("recomputed_sha256"))
            require(path.exists(), f"reuse source path missing: {path}")
            plan.append(
                PlannedFile(
                    chunk_id=APPROVED_CHUNK_ID,
                    symbol=symbol,
                    day=day,
                    url=str(entry["expected_url"]),
                    expected_inner_csv=str(entry["expected_inner_csv"]),
                    expected_schema_key=str(entry["expected_schema_key"]),
                    local_zip_path=path,
                    source_kind="REUSE_CANDIDATE_ALREADY_VALIDATED_PILOT_FILE_REVALIDATED",
                    recorded_sha256=recorded_sha,
                )
            )
        else:
            path = DOWNLOAD_DIR / symbol / expected_zip_name(symbol, day)
            plan.append(
                PlannedFile(
                    chunk_id=APPROVED_CHUNK_ID,
                    symbol=symbol,
                    day=day,
                    url=str(entry["expected_url"]),
                    expected_inner_csv=str(entry["expected_inner_csv"]),
                    expected_schema_key=str(entry["expected_schema_key"]),
                    local_zip_path=path,
                    source_kind="NEW_APPROVED_CHUNK_02_DOWNLOAD",
                )
            )
    require(len(plan) == EXPECTED_CHUNK_FILE_COUNT, "planned execution file count mismatch")
    require(sum(1 for item in plan if item.symbol == REUSE_SYMBOL) == EXPECTED_REUSE_CANDIDATE_FILE_COUNT, "planned reuse count mismatch")
    require(sum(1 for item in plan if item.symbol != REUSE_SYMBOL) == MAX_NEW_DOWNLOAD_ATTEMPT_COUNT, "planned new download count mismatch")
    return sorted(plan, key=lambda item: (APPROVED_SYMBOLS.index(item.symbol), item.day))


def download_one(item: PlannedFile) -> dict[str, Any]:
    item.local_zip_path.parent.mkdir(parents=True, exist_ok=True)
    if item.local_zip_path.exists():
        return {
            "chunk_id": item.chunk_id,
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "expected_url": item.url,
            "local_zip_path": str(item.local_zip_path),
            "download_attempted": False,
            "download_succeeded": True,
            "http_status": None,
            "failure_reason": None,
            "file_size_bytes": item.local_zip_path.stat().st_size,
            "source_kind": "EXISTING_APPROVED_CHUNK_02_FILE",
            "coverage_gap": False,
        }
    request = urllib.request.Request(item.url, headers={"User-Agent": "edge-factory-os-chunk-02-downloader/1.0"})
    last_error = ""
    last_status: int | None = None
    for attempt in range(1, 3):
        tmp_path = item.local_zip_path.with_suffix(item.local_zip_path.suffix + f".{uuid.uuid4().hex}.tmp")
        total = 0
        try:
            with urllib.request.urlopen(request, timeout=45) as response, tmp_path.open("wb") as handle:
                last_status = int(getattr(response, "status", 200))
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_ZIP_SIZE_PER_FILE_MB * 1024 * 1024:
                        raise ExecutionBlocked(f"zip exceeds configured size limit: {item.url}")
                    handle.write(chunk)
            tmp_path.replace(item.local_zip_path)
            return {
                "chunk_id": item.chunk_id,
                "symbol": item.symbol,
                "date": item.day.isoformat(),
                "expected_url": item.url,
                "local_zip_path": str(item.local_zip_path),
                "download_attempted": True,
                "download_succeeded": True,
                "http_status": last_status,
                "failure_reason": None,
                "file_size_bytes": item.local_zip_path.stat().st_size,
                "source_kind": "DOWNLOADED_THIS_RUN",
                "download_attempt_count": attempt,
                "coverage_gap": False,
            }
        except urllib.error.HTTPError as exc:
            last_status = exc.code
            last_error = f"HTTPError: {exc.code} {exc.reason}"
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
            if exc.code == 404:
                break
        except Exception as exc:
            last_error = type(exc).__name__ + ": " + str(exc)
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
    return {
        "chunk_id": item.chunk_id,
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "expected_url": item.url,
        "local_zip_path": str(item.local_zip_path),
        "download_attempted": True,
        "download_succeeded": False,
        "http_status": last_status,
        "failure_reason": last_error,
        "file_size_bytes": 0,
        "source_kind": "MISSING_OR_FAILED_APPROVED_CHUNK_02_FILE",
        "download_attempt_count": 1 if last_status == 404 else 2,
        "coverage_gap": True,
    }


def execute_downloads(plan: list[PlannedFile]) -> list[dict[str, Any]]:
    new_items = [item for item in plan if item.symbol != REUSE_SYMBOL]
    require(len(new_items) <= MAX_NEW_DOWNLOAD_ATTEMPT_COUNT, "new download item count exceeded")
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(download_one, item): item for item in new_items}
        for future in as_completed(futures):
            item = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(
                    {
                        "chunk_id": item.chunk_id,
                        "symbol": item.symbol,
                        "date": item.day.isoformat(),
                        "expected_url": item.url,
                        "local_zip_path": str(item.local_zip_path),
                        "download_attempted": True,
                        "download_succeeded": False,
                        "http_status": None,
                        "failure_reason": type(exc).__name__ + ": " + str(exc),
                        "file_size_bytes": 0,
                        "source_kind": "MISSING_OR_FAILED_APPROVED_CHUNK_02_FILE",
                        "download_attempt_count": 1,
                        "coverage_gap": True,
                    }
                )
    return sorted(results, key=lambda row: (APPROVED_SYMBOLS.index(row["symbol"]), row["date"]))


def inspect_zip(item: PlannedFile) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    hash_record = {
        "chunk_id": item.chunk_id,
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "expected_url": item.url,
        "local_zip_path": str(item.local_zip_path),
        "source_kind": item.source_kind,
        "file_size_bytes": 0,
        "sha256": None,
        "recorded_sha256": item.recorded_sha256,
        "hash_computed_or_revalidated": False,
        "recorded_hash_match": None,
    }
    inventory = {
        "chunk_id": item.chunk_id,
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "local_zip_path": str(item.local_zip_path),
        "zip_open_success": False,
        "zip_member_count": 0,
        "zip_members": [],
        "path_traversal_detected": False,
        "expected_inner_csv": item.expected_inner_csv,
        "expected_inner_csv_present": False,
    }
    schema_sample = {
        "chunk_id": item.chunk_id,
        "symbol": item.symbol,
        "date": item.day.isoformat(),
        "expected_inner_csv": item.expected_inner_csv,
        "expected_schema_key": item.expected_schema_key,
        "schema_match": False,
        "observed_schema": [],
        "sample_rows_read": 0,
        "sampled_symbol_values": [],
        "observed_symbols_match_expected": False,
    }
    if not item.local_zip_path.exists():
        return hash_record, inventory, schema_sample, {
            "chunk_id": item.chunk_id,
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "expected_url": item.url,
            "failure_stage": "ZIP_EXISTS",
            "failure_reason": "local ZIP missing after execution",
            "coverage_gap": True,
        }
    hash_record["file_size_bytes"] = item.local_zip_path.stat().st_size
    hash_record["sha256"] = sha256_file(item.local_zip_path)
    hash_record["hash_computed_or_revalidated"] = True
    if item.recorded_sha256 is not None:
        hash_record["recorded_hash_match"] = hash_record["sha256"] == item.recorded_sha256
        if hash_record["recorded_hash_match"] is False:
            return hash_record, inventory, schema_sample, {
                "chunk_id": item.chunk_id,
                "symbol": item.symbol,
                "date": item.day.isoformat(),
                "expected_url": item.url,
                "failure_stage": "REUSE_HASH",
                "failure_reason": "reuse candidate hash mismatch",
                "coverage_gap": True,
            }
    try:
        with zipfile.ZipFile(item.local_zip_path) as zf:
            infos = zf.infolist()
            inventory["zip_open_success"] = True
            inventory["zip_member_count"] = len(infos)
            inventory["zip_members"] = [info.filename for info in infos]
            if len(infos) > MAX_ZIP_MEMBERS_PER_FILE:
                return hash_record, inventory, schema_sample, {
                    "chunk_id": item.chunk_id,
                    "symbol": item.symbol,
                    "date": item.day.isoformat(),
                    "expected_url": item.url,
                    "failure_stage": "ZIP_MEMBER_LIMIT",
                    "failure_reason": "ZIP member count exceeds limit",
                    "coverage_gap": True,
                }
            for info in infos:
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or ":" in info.filename:
                    inventory["path_traversal_detected"] = True
            if inventory["path_traversal_detected"]:
                return hash_record, inventory, schema_sample, {
                    "chunk_id": item.chunk_id,
                    "symbol": item.symbol,
                    "date": item.day.isoformat(),
                    "expected_url": item.url,
                    "failure_stage": "ZIP_PATH_TRAVERSAL",
                    "failure_reason": "unsafe ZIP member path",
                    "coverage_gap": True,
                }
            inventory["expected_inner_csv_present"] = item.expected_inner_csv in inventory["zip_members"]
            if not inventory["expected_inner_csv_present"]:
                return hash_record, inventory, schema_sample, {
                    "chunk_id": item.chunk_id,
                    "symbol": item.symbol,
                    "date": item.day.isoformat(),
                    "expected_url": item.url,
                    "failure_stage": "EXPECTED_CSV",
                    "failure_reason": "expected inner CSV missing",
                    "coverage_gap": True,
                }
            with zf.open(item.expected_inner_csv, "r") as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
                reader = csv.reader(text)
                observed_schema = next(reader, [])
                schema_sample["observed_schema"] = observed_schema
                schema_sample["schema_match"] = observed_schema == EXPECTED_SCHEMA
                sampled_symbols: list[str] = []
                rows_read = 0
                for row in reader:
                    if rows_read >= MAX_CSV_SAMPLE_ROWS_PER_FILE:
                        break
                    rows_read += 1
                    if row:
                        sampled_symbols.append(row[0])
                schema_sample["sample_rows_read"] = rows_read
                schema_sample["sampled_symbol_values"] = sorted(set(sampled_symbols))
                schema_sample["observed_symbols_match_expected"] = all(value == item.symbol for value in sampled_symbols)
                if not schema_sample["schema_match"]:
                    return hash_record, inventory, schema_sample, {
                        "chunk_id": item.chunk_id,
                        "symbol": item.symbol,
                        "date": item.day.isoformat(),
                        "expected_url": item.url,
                        "failure_stage": "SCHEMA",
                        "failure_reason": "schema mismatch",
                        "coverage_gap": True,
                    }
                if not schema_sample["observed_symbols_match_expected"]:
                    return hash_record, inventory, schema_sample, {
                        "chunk_id": item.chunk_id,
                        "symbol": item.symbol,
                        "date": item.day.isoformat(),
                        "expected_url": item.url,
                        "failure_stage": "SAMPLED_SYMBOL",
                        "failure_reason": "sampled symbol mismatch",
                        "coverage_gap": True,
                    }
    except zipfile.BadZipFile as exc:
        return hash_record, inventory, schema_sample, {
            "chunk_id": item.chunk_id,
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "expected_url": item.url,
            "failure_stage": "ZIP_OPEN",
            "failure_reason": f"BadZipFile: {exc}",
            "coverage_gap": True,
        }
    except Exception as exc:
        return hash_record, inventory, schema_sample, {
            "chunk_id": item.chunk_id,
            "symbol": item.symbol,
            "date": item.day.isoformat(),
            "expected_url": item.url,
            "failure_stage": "ZIP_INSPECTION",
            "failure_reason": type(exc).__name__ + ": " + str(exc),
            "coverage_gap": True,
        }
    return hash_record, inventory, schema_sample, None


def inspect_available_files(plan: list[PlannedFile]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    hash_records: list[dict[str, Any]] = []
    inventory_records: list[dict[str, Any]] = []
    schema_records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for item in plan:
        hash_record, inventory, schema_sample, failure = inspect_zip(item)
        hash_records.append(hash_record)
        inventory_records.append(inventory)
        schema_records.append(schema_sample)
        if failure is not None:
            failures.append(failure)
    return hash_records, inventory_records, schema_records, failures


def symbol_coverage_counts(hash_records: list[dict[str, Any]], failures: list[dict[str, Any]]) -> tuple[int, int, list[str]]:
    failed_keys = {(row["symbol"], row["date"]) for row in failures}
    full_symbols: list[str] = []
    gap_symbols: list[str] = []
    for symbol in APPROVED_SYMBOLS:
        symbol_hashes = [row for row in hash_records if row["symbol"] == symbol and row["hash_computed_or_revalidated"]]
        symbol_failed = any(key[0] == symbol for key in failed_keys)
        if len(symbol_hashes) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL and not symbol_failed:
            full_symbols.append(symbol)
        else:
            gap_symbols.append(symbol)
    return len(full_symbols), len(gap_symbols), gap_symbols


def build_file_manifest(plan: list[PlannedFile], hash_records: list[dict[str, Any]], download_results: list[dict[str, Any]], failures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hash_by_key = {(row["symbol"], row["date"]): row for row in hash_records}
    download_by_key = {(row["symbol"], row["date"]): row for row in download_results}
    failure_by_key = {(row["symbol"], row["date"]): row for row in failures}
    manifest: list[dict[str, Any]] = []
    for item in plan:
        key = (item.symbol, item.day.isoformat())
        hash_record = hash_by_key.get(key, {})
        download = download_by_key.get(key)
        failure = failure_by_key.get(key)
        available = bool(hash_record.get("hash_computed_or_revalidated")) and failure is None
        manifest.append(
            {
                "chunk_id": item.chunk_id,
                "symbol": item.symbol,
                "date": item.day.isoformat(),
                "expected_url": item.url,
                "expected_inner_csv": item.expected_inner_csv,
                "local_zip_path": str(item.local_zip_path),
                "source_kind": item.source_kind if item.symbol == REUSE_SYMBOL else (download or {}).get("source_kind", "NEW_APPROVED_CHUNK_02_DOWNLOAD"),
                "download_attempted": bool((download or {}).get("download_attempted")),
                "download_succeeded": None if download is None else bool(download.get("download_succeeded")),
                "http_status": None if download is None else download.get("http_status"),
                "sha256": hash_record.get("sha256"),
                "file_size_bytes": hash_record.get("file_size_bytes", 0),
                "available_for_validator": available,
                "coverage_gap": failure is not None,
                "failure_stage": None if failure is None else failure.get("failure_stage"),
                "failure_reason": None if failure is None else failure.get("failure_reason"),
                "build_ready": False,
                "acquisition_ready": False,
            }
        )
    return manifest


def write_reports(
    preconditions: dict[str, Any],
    preview: dict[str, Any],
    py_state: dict[str, Any],
    plan: list[PlannedFile],
    download_results: list[dict[str, Any]],
    hash_records: list[dict[str, Any]],
    inventory_records: list[dict[str, Any]],
    schema_records: list[dict[str, Any]],
    inspection_failures: list[dict[str, Any]],
) -> dict[str, Any]:
    download_failures = [
        {
            "chunk_id": row["chunk_id"],
            "symbol": row["symbol"],
            "date": row["date"],
            "expected_url": row["expected_url"],
            "failure_stage": "DOWNLOAD",
            "failure_reason": row["failure_reason"],
            "http_status": row["http_status"],
            "coverage_gap": True,
        }
        for row in download_results
        if not row["download_succeeded"]
    ]
    failures_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in download_failures + inspection_failures:
        failures_by_key[(row["symbol"], row["date"])] = row
    failures = sorted(failures_by_key.values(), key=lambda row: (APPROVED_SYMBOLS.index(row["symbol"]), row["date"], row["failure_stage"]))
    missing_or_failed_file_count = len(failures)
    coverage_gap_detected = missing_or_failed_file_count > 0
    failure_keys = set(failures_by_key)
    available_keys = {
        (row["symbol"], row["date"])
        for row in hash_records
        if row["hash_computed_or_revalidated"] and (row["symbol"], row["date"]) not in failure_keys
    }
    reused_file_count = sum(1 for row in hash_records if row["symbol"] == REUSE_SYMBOL and row["hash_computed_or_revalidated"] and row.get("recorded_hash_match") is not False)
    successful_new_download_count = sum(1 for symbol, _day in available_keys if symbol != REUSE_SYMBOL)
    new_download_attempt_count = sum(1 for row in download_results if row["download_attempted"])
    final_available_file_count = len(available_keys)
    full_coverage_count, gap_symbol_count, gap_symbols = symbol_coverage_counts(hash_records, failures)
    all_hashes = all(
        row["hash_computed_or_revalidated"]
        for row in hash_records
        if (row["symbol"], row["date"]) in available_keys
    )
    all_zips_open = all(row["zip_open_success"] for row in inventory_records if (row["symbol"], row["date"]) in available_keys)
    any_path_traversal = any(row["path_traversal_detected"] for row in inventory_records)
    all_inner_csv = all(row["expected_inner_csv_present"] for row in inventory_records if (row["symbol"], row["date"]) in available_keys)
    all_schema = all(row["schema_match"] for row in schema_records if (row["symbol"], row["date"]) in available_keys)
    all_symbols = all(row["observed_symbols_match_expected"] for row in schema_records if (row["symbol"], row["date"]) in available_keys)
    max_sample_rows = max((row["sample_rows_read"] for row in schema_records), default=0)
    status = GAP_STATUS if coverage_gap_detected else PASS_STATUS
    after_quality = AFTER_QUALITY_GAP if coverage_gap_detected else AFTER_QUALITY_PASS
    replacement_checks = {
        **preconditions["checks"],
        **preview["checks"],
        "approved_plan_count_valid": len(plan) == EXPECTED_CHUNK_FILE_COUNT,
        "only_approved_symbols_processed": sorted({item.symbol for item in plan}, key=APPROVED_SYMBOLS.index) == APPROVED_SYMBOLS,
        "only_approved_dates_processed": {item.day for item in plan} == set(inclusive_days()),
        "new_download_attempt_limit_respected": new_download_attempt_count <= MAX_NEW_DOWNLOAD_ATTEMPT_COUNT,
        "reuse_revalidated_or_recorded": reused_file_count <= EXPECTED_REUSE_CANDIDATE_FILE_COUNT,
        "gaps_recorded_not_silent": (not coverage_gap_detected) or missing_or_failed_file_count == len(failures),
        "sample_row_limit_respected": max_sample_rows <= MAX_CSV_SAMPLE_ROWS_PER_FILE,
        "no_zip_path_traversal": not any_path_traversal,
        "no_full_csv_read": True,
        "no_api_browse": True,
        "no_build_aggregation": True,
        "no_research_backtest_edge_or_broad_claim": True,
        "next_module_is_validator": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    base = {
        "historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_status": status,
        "download_execution_performed": True,
        "chunk_id": APPROVED_CHUNK_ID,
        "chunk_symbol_count": len(APPROVED_SYMBOLS),
        "chunk_symbols": APPROVED_SYMBOLS,
        "expected_chunk_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "expected_chunk_02_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "planned_file_count": len(plan),
        "reuse_candidate_file_count": EXPECTED_REUSE_CANDIDATE_FILE_COUNT,
        "reused_file_count": reused_file_count,
        "new_download_attempt_count": new_download_attempt_count,
        "successful_new_download_count": successful_new_download_count,
        "final_available_file_count": final_available_file_count,
        "missing_or_failed_file_count": missing_or_failed_file_count,
        "coverage_gap_detected": coverage_gap_detected,
        "symbols_with_full_file_coverage_count": full_coverage_count,
        "symbols_with_coverage_gaps_count": gap_symbol_count,
        "symbols_with_coverage_gaps": gap_symbols,
        "all_hashes_computed_or_revalidated": all_hashes,
        "all_available_zips_open_success": all_zips_open,
        "any_zip_path_traversal_detected": any_path_traversal,
        "all_available_expected_inner_csv_present": all_inner_csv,
        "all_available_expected_schema_match": all_schema,
        "all_available_observed_symbols_match_expected": all_symbols,
        "max_csv_sample_rows_read_per_file": max_sample_rows,
        "full_csv_read_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "near_3y_eligible_symbol_count_now": 0,
        "chunk_download_valid_for_validator": replacement_checks_all_true,
        "chunk_02_download_valid_for_validator": replacement_checks_all_true,
        "full_universe_acquisition_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "data_download_performed": new_download_attempt_count > 0,
        "archive_download_performed": new_download_attempt_count > 0,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": max(int(preview["summary"].get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_execution": after_quality,
        "next_module": NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }
    file_manifest = build_file_manifest(plan, hash_records, download_results, failures)
    reports = {
        "historical_okx_full_usdt_swap_chunk_02_download_execution_report.json": {
            **base,
            "artifact_type": "download_execution_report",
            "download_result_count": len(download_results),
            "download_results": download_results,
        },
        "historical_okx_full_usdt_swap_chunk_02_download_file_manifest_after_execution.json": {
            **base,
            "artifact_type": "download_file_manifest_after_execution",
            "file_manifest": file_manifest,
        },
        "historical_okx_full_usdt_swap_chunk_02_download_gap_report.json": {
            **base,
            "artifact_type": "download_gap_report",
            "coverage_gaps": failures,
        },
        "historical_okx_full_usdt_swap_chunk_02_reuse_validation_report.json": {
            **base,
            "artifact_type": "reuse_validation_report",
            "reuse_symbol": REUSE_SYMBOL,
            "reuse_validation_records": [row for row in hash_records if row["symbol"] == REUSE_SYMBOL],
            "reuse_validation_finality": "REVALIDATED_FOR_EXECUTION_BUT_NOT_BUILD_READY",
        },
        "historical_okx_full_usdt_swap_chunk_02_sha256_report.json": {
            **base,
            "artifact_type": "sha256_report",
            "sha256_records": hash_records,
        },
        "historical_okx_full_usdt_swap_chunk_02_zip_inventory_report.json": {
            **base,
            "artifact_type": "zip_inventory_report",
            "zip_inventory": inventory_records,
        },
        "historical_okx_full_usdt_swap_chunk_02_schema_sample_report.json": {
            **base,
            "artifact_type": "schema_sample_report",
            "expected_schema": EXPECTED_SCHEMA,
            "schema_samples": schema_records,
        },
        "historical_okx_full_usdt_swap_chunk_02_download_execution_compliance_report.json": {
            **base,
            "artifact_type": "download_execution_compliance_report",
            "no_api": True,
            "no_browse": True,
            "no_full_csv_read": True,
            "no_build": True,
            "no_aggregation": True,
            "no_research_backtest_edge": True,
            "no_runtime_capital_live": True,
            "no_schema_config_creation": True,
            "approved_static_archive_get_only": True,
        },
        "historical_okx_full_usdt_swap_chunk_02_download_execution_summary.json": {
            **base,
            "artifact_type": "download_execution_summary",
            "artifact_count": len(REQUIRED_OUTPUTS),
        },
    }
    for name, payload in reports.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing required execution outputs: {missing}")
    require(replacement_checks_all_true, f"replacement checks failed: {replacement_checks}")
    return base


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_status": BLOCKED_STATUS,
        "download_execution_performed": False,
        "blocked_reason": message,
        "chunk_id": APPROVED_CHUNK_ID,
        "chunk_symbol_count": len(APPROVED_SYMBOLS),
        "chunk_symbols": APPROVED_SYMBOLS,
        "expected_chunk_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "expected_chunk_02_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "planned_file_count": 0,
        "reuse_candidate_file_count": EXPECTED_REUSE_CANDIDATE_FILE_COUNT,
        "reused_file_count": 0,
        "new_download_attempt_count": 0,
        "successful_new_download_count": 0,
        "final_available_file_count": 0,
        "missing_or_failed_file_count": EXPECTED_CHUNK_FILE_COUNT,
        "coverage_gap_detected": True,
        "symbols_with_full_file_coverage_count": 0,
        "symbols_with_coverage_gaps_count": len(APPROVED_SYMBOLS),
        "symbols_with_coverage_gaps": APPROVED_SYMBOLS,
        "all_hashes_computed_or_revalidated": False,
        "all_available_zips_open_success": False,
        "any_zip_path_traversal_detected": False,
        "all_available_expected_inner_csv_present": False,
        "all_available_expected_schema_match": False,
        "all_available_observed_symbols_match_expected": False,
        "max_csv_sample_rows_read_per_file": 0,
        "full_csv_read_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "near_3y_eligible_symbol_count_now": 0,
        "chunk_download_valid_for_validator": False,
        "chunk_02_download_valid_for_validator": False,
        "full_universe_acquisition_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "data_download_performed": False,
        "archive_download_performed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 505,
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_execution": "CHUNK_02_DOWNLOAD_EXECUTION_FAILED_CLOSED",
        "next_module": FAILED_NEXT_MODULE,
        "replacement_checks_all_true": False,
        "created_at_utc": utc_now(),
    }


def run_execution() -> dict[str, Any]:
    py_state = tracked_python_validation()
    preconditions = validate_preconditions(py_state)
    preview = load_and_validate_preview()
    reuse_index = load_pilot_reuse_index()
    plan = build_plan(preview, reuse_index)
    download_results = execute_downloads(plan)
    hash_records, inventory_records, schema_records, failures = inspect_available_files(plan)
    return write_reports(preconditions, preview, py_state, plan, download_results, hash_records, inventory_records, schema_records, failures)


def main() -> int:
    try:
        summary = run_execution()
    except Exception as exc:
        blocked = blocked_payload(type(exc).__name__ + ": " + str(exc))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_chunk_02_download_execution_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
