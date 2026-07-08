from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_after_batch_policy_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
CURRENT_TOOL_REL = f"tools/{REQUESTED_MODULE}"
EXPECTED_HEAD = "36695d0"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_APPROVED_POLICY_CLEAN_BUILD_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_EXECUTED_VALIDATOR_READY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_EXECUTION_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_after_execution_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_blocked_record_after_batch_policy_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_EXECUTED_VALIDATOR_READY"

DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_FILE_COUNT_TOTAL = 10_530
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_RAW_ROWS = 15_166_462
EXPECTED_EXACT_DUPLICATE_ROWS_DROPPED = 3_252
EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED = 20
EXPECTED_CLEAN_SOURCE_ROWS = 15_163_190
EXPECTED_MISSING_MINUTES = 4_800
EXPECTED_MINUTE_MS = 60_000
EXPECTED_HOUR_MS = 3_600_000
EXPECTED_UNIQUE_OPEN_TIME_COUNT_PER_SYMBOL = 1_516_320
DORMANT_REPO_ATTENTION_COUNT = 716

PILOT_SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",
    "SOL-USDT-SWAP",
    "XRP-USDT-SWAP",
    "DOGE-USDT-SWAP",
    "ADA-USDT-SWAP",
    "AVAX-USDT-SWAP",
    "LINK-USDT-SWAP",
    "LTC-USDT-SWAP",
    "DOT-USDT-SWAP",
]

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
OUTPUT_SCHEMA = [
    "instrument_name",
    "hour_start_epoch_ms",
    "hour_start_iso_utc",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "source_row_count",
    "complete_hour",
    "confirm",
    "source_first_open_time",
    "source_last_open_time",
    "source_zip_sha256",
    "source_csv_file",
    "source_date",
    "build_scope",
    "policy_clean_build",
    "quarantine_applied",
    "missing_minute_applied",
    "incomplete_reason",
]
OHLCV_FIELDS = ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote"]
CANONICAL_FIELDS = EXPECTED_SCHEMA

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
OUTPUT_CSV = OUTPUT_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_combined_1h_output.csv"
POLICY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_after_batch_anomaly_classification_v1"
CLASSIFICATION_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_anomaly_classification_after_policy_clean_build_block_v1"
DOWNLOAD_EXECUTION_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_after_expansion_preview_approval_v1"
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_download_execution_validator_after_execution_v1"

ARTIFACTS = {
    "batch_policy_summary": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy_summary.json",
    "batch_policy": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy.json",
    "batch_policy_clean_build_approval": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_approval_record.json",
    "batch_classification_summary": CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_anomaly_classification_summary.json",
    "batch_per_symbol_table": CLASSIFICATION_DIR / "historical_okx_10_symbol_pilot_batch_per_symbol_anomaly_table.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
    "download_hash_validation_report": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_hash_validation_report.json",
    "download_zip_schema_validation_report": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_zip_schema_validation_report.json",
    "download_execution_summary": DOWNLOAD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_download_execution_summary.json",
    "download_provenance_report": DOWNLOAD_EXECUTION_DIR / "historical_okx_10_symbol_pilot_download_provenance_report.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_1h_output_manifest.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_combined_1h_output.csv",
    "historical_okx_10_symbol_pilot_batch_exact_duplicate_drop_audit.json",
    "historical_okx_10_symbol_pilot_batch_material_conflict_quarantine_audit.json",
    "historical_okx_10_symbol_pilot_batch_missing_minute_audit.json",
    "historical_okx_10_symbol_pilot_batch_incomplete_hour_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_schema_validation_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_output_provenance_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_numeric_sanity_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_compliance_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_summary.json",
]


class Blocked(RuntimeError):
    pass


@dataclass(frozen=True)
class MinuteRow:
    instrument_name: str
    open: str
    high: str
    low: str
    close: str
    vol: str
    vol_ccy: str
    vol_quote: str
    open_time: int
    confirm: str
    source_zip_sha256: str
    source_csv_file: str
    source_date: str

    def canonical(self) -> tuple[str, str, str, str, str, str, str, str, str, str]:
        return (
            self.instrument_name,
            self.open,
            self.high,
            self.low,
            self.close,
            self.vol,
            self.vol_ccy,
            self.vol_quote,
            str(self.open_time),
            self.confirm,
        )

    def material(self) -> tuple[str, str, str, str, str, str, str]:
        return (self.open, self.high, self.low, self.close, self.vol, self.vol_ccy, self.vol_quote)

    def sample(self) -> dict[str, Any]:
        return {
            "instrument_name": self.instrument_name,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "vol": self.vol,
            "vol_ccy": self.vol_ccy,
            "vol_quote": self.vol_quote,
            "open_time": self.open_time,
            "confirm": self.confirm,
            "source_csv_file": self.source_csv_file,
            "source_date": self.source_date,
            "source_zip_sha256": self.source_zip_sha256,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def iso_from_ms(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def decimal_value(value: str, field_name: str) -> Decimal:
    normalized = str(value).strip()
    if normalized.lower() == "none" and field_name in {"vol_ccy", "vol_quote"}:
        return Decimal("0")
    return Decimal(normalized)


def truthy_confirm(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


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
    require(path.exists(), f"missing required artifact {label}: {path}")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(loaded, dict), f"artifact is not object: {label}")
    return loaded


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_start_end_ms() -> tuple[int, int]:
    start = datetime.fromisoformat(DATE_RANGE_START).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(DATE_RANGE_END).replace(tzinfo=timezone.utc)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000) + 24 * 60 * 60 * 1000 - EXPECTED_MINUTE_MS


def safe_zip_member_name(symbol: str, date: str, archive: zipfile.ZipFile) -> str:
    expected = f"{symbol}-candlesticks-{date}.csv"
    names = archive.namelist()
    require(expected in names, f"missing expected CSV member {expected}")
    require(all(PurePosixPath(name).name == name for name in names), f"zip path traversal risk for {symbol} {date}")
    return expected


def classify_duplicate_group(rows: list[MinuteRow]) -> str:
    first = rows[0]
    if all(row.canonical() == first.canonical() for row in rows[1:]):
        return "EXACT_DUPLICATE"
    if any(row.material() != first.material() for row in rows[1:]):
        return "MATERIAL_DUPLICATE_CONFLICT"
    non_confirm_equal = all(row.canonical()[:9] == first.canonical()[:9] for row in rows[1:])
    confirm_diff = any(row.confirm != first.confirm for row in rows[1:])
    if non_confirm_equal and confirm_diff:
        return "CONFIRM_ONLY_CONFLICT"
    return "UNKNOWN_DUPLICATE"


def raw_missing_minutes(open_times: set[int]) -> tuple[int, int, list[int]]:
    start_ms, end_ms = expected_start_end_ms()
    in_range = sorted(value for value in open_times if start_ms <= value <= end_ms)
    missing = 0
    affected_hours: set[int] = set()
    samples: list[int] = []
    if not in_range:
        return EXPECTED_UNIQUE_OPEN_TIME_COUNT_PER_SYMBOL, 0, samples
    previous = in_range[0]
    if previous > start_ms:
        for value in range(start_ms, previous, EXPECTED_MINUTE_MS):
            missing += 1
            affected_hours.add((value // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS)
            if len(samples) < 25:
                samples.append(value)
    for value in in_range[1:]:
        for missing_value in range(previous + EXPECTED_MINUTE_MS, value, EXPECTED_MINUTE_MS):
            missing += 1
            affected_hours.add((missing_value // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS)
            if len(samples) < 25:
                samples.append(missing_value)
        previous = value
    if previous < end_ms:
        for value in range(previous + EXPECTED_MINUTE_MS, end_ms + EXPECTED_MINUTE_MS, EXPECTED_MINUTE_MS):
            missing += 1
            affected_hours.add((value // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS)
            if len(samples) < 25:
                samples.append(value)
    return missing, len(affected_hours), samples


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def validate_chain(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    status_lines = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    policy_summary = artifacts["batch_policy_summary"]
    policy = artifacts["batch_policy"]
    approval = artifacts["batch_policy_clean_build_approval"]
    classification = artifacts["batch_classification_summary"]
    validator = artifacts["download_validator_summary"]
    execution = artifacts["download_execution_summary"]
    hash_report = artifacts["download_hash_validation_report"]

    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": policy_summary.get("historical_data_acquisition_okx_10_symbol_pilot_batch_policy_status") == PREVIOUS_STATUS,
        "current_next_module_matches": policy_summary.get("next_module") == REQUESTED_MODULE,
        "batch_policy_created": policy_summary.get("batch_policy_created") is True and policy.get("batch_policy_created") is True,
        "approval_grants_future_build": approval.get("approval_grants_future_batch_policy_clean_build_next") is True,
        "classification_counts_match": (
            classification.get("total_raw_rows_scanned") == EXPECTED_RAW_ROWS
            and classification.get("total_exact_duplicate_extra_rows") == EXPECTED_EXACT_DUPLICATE_ROWS_DROPPED
            and classification.get("total_material_conflict_rows") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED
            and classification.get("total_missing_minute_count") == EXPECTED_MISSING_MINUTES
        ),
        "download_validator_passed": validator.get("download_execution_validated") is True and validator.get("replacement_checks_all_true") is True,
        "download_file_count_valid": validator.get("final_pilot_file_set_count") == EXPECTED_FILE_COUNT_TOTAL,
        "download_execution_file_count_valid": execution.get("final_pilot_file_set_count") == EXPECTED_FILE_COUNT_TOTAL,
        "hash_report_count_valid": len(hash_report.get("hashes", [])) == EXPECTED_FILE_COUNT_TOTAL,
        "no_prior_research_edge_claim": (
            policy_summary.get("output_valid_for_research_backtest") is False
            and policy_summary.get("output_valid_for_edge_claim") is False
            and policy_summary.get("safe_for_full_universe_acquisition") is False
            and policy_summary.get("broad_acquisition_ready") is False
        ),
        "policy_forbids_fill_and_conflict_selection": (
            policy_summary.get("synthetic_fill_allowed") is False
            and policy_summary.get("forward_fill_allowed") is False
            and policy_summary.get("backfill_allowed") is False
            and policy_summary.get("choose_conflicting_row_allowed") is False
            and policy_summary.get("average_conflicting_rows_allowed") is False
            and policy_summary.get("merge_conflicting_rows_allowed") is False
        ),
    }
    return {"head": head, "status_lines": status_lines, "checks": checks}


def group_hash_items(hash_report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in hash_report.get("hashes", []):
        symbol = item.get("symbol")
        require(symbol in PILOT_SYMBOLS, f"unapproved symbol in hash report: {symbol}")
        grouped[symbol].append(item)
    require(set(grouped) == set(PILOT_SYMBOLS), "hash report does not cover exact pilot symbol set")
    for symbol in PILOT_SYMBOLS:
        require(len(grouped[symbol]) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL, f"{symbol} file count mismatch")
    return grouped


def scan_symbol(symbol: str, hash_items: list[dict[str, Any]]) -> dict[str, Any]:
    raw_row_count = 0
    schema_mismatch_count = 0
    symbol_mismatch_count = 0
    sha_revalidated_count = 0
    zip_open_count = 0
    csv_read_count = 0
    all_open_times: set[int] = set()
    clean_by_open_time: dict[int, MinuteRow] = {}
    duplicate_groups: dict[int, list[MinuteRow]] = {}
    file_audits: list[dict[str, Any]] = []

    for item in sorted(hash_items, key=lambda value: str(value["date"])):
        zip_path = Path(item["local_zip_path"])
        require(zip_path.exists(), f"missing ZIP: {zip_path}")
        observed_sha = sha256_file(zip_path)
        expected_sha = item.get("recorded_sha256") or item.get("sha256")
        require(observed_sha == expected_sha, f"SHA256 mismatch for {zip_path}")
        sha_revalidated_count += 1
        raw_file_rows = 0
        with zipfile.ZipFile(zip_path) as archive:
            member = safe_zip_member_name(symbol, str(item["date"]), archive)
            zip_open_count += 1
            with archive.open(member, "r") as raw_handle:
                text_handle = io.TextIOWrapper(raw_handle, encoding="utf-8", newline="")
                reader = csv.DictReader(text_handle)
                if reader.fieldnames != EXPECTED_SCHEMA:
                    schema_mismatch_count += 1
                    continue
                csv_read_count += 1
                for row in reader:
                    raw_row_count += 1
                    raw_file_rows += 1
                    if row.get("instrument_name") != symbol:
                        symbol_mismatch_count += 1
                    try:
                        open_time = int(row.get("open_time", ""))
                    except ValueError as exc:
                        raise Blocked(f"invalid open_time for {symbol} {item['date']}") from exc
                    minute = MinuteRow(
                        instrument_name=row["instrument_name"],
                        open=row["open"],
                        high=row["high"],
                        low=row["low"],
                        close=row["close"],
                        vol=row["vol"],
                        vol_ccy=row["vol_ccy"],
                        vol_quote=row["vol_quote"],
                        open_time=open_time,
                        confirm=row["confirm"],
                        source_zip_sha256=observed_sha,
                        source_csv_file=member,
                        source_date=str(item["date"]),
                    )
                    all_open_times.add(open_time)
                    if open_time in clean_by_open_time:
                        duplicate_groups.setdefault(open_time, [clean_by_open_time[open_time]]).append(minute)
                    else:
                        clean_by_open_time[open_time] = minute
        file_audits.append(
            {
                "symbol": symbol,
                "source_date": str(item["date"]),
                "local_zip_path": str(zip_path),
                "source_csv_file": f"{symbol}-candlesticks-{item['date']}.csv",
                "sha256_revalidated": True,
                "source_row_count_before_policy": raw_file_rows,
            }
        )

    exact_duplicate_groups = 0
    exact_duplicate_rows_dropped = 0
    material_conflict_groups = 0
    material_conflict_rows_quarantined = 0
    confirm_only_conflict_groups = 0
    unknown_duplicate_groups = 0
    material_open_times: set[int] = set()
    exact_samples: list[dict[str, Any]] = []
    material_samples: list[dict[str, Any]] = []
    duplicate_group_samples: list[dict[str, Any]] = []

    for open_time, rows in sorted(duplicate_groups.items()):
        duplicate_type = classify_duplicate_group(rows)
        if duplicate_type == "EXACT_DUPLICATE":
            exact_duplicate_groups += 1
            exact_duplicate_rows_dropped += len(rows) - 1
            if len(exact_samples) < 25:
                exact_samples.append(
                    {
                        "symbol": symbol,
                        "open_time": open_time,
                        "dropped_extra_rows": len(rows) - 1,
                        "kept_row": rows[0].sample(),
                        "dropped_row_sample": [row.sample() for row in rows[1:4]],
                    }
                )
        elif duplicate_type == "MATERIAL_DUPLICATE_CONFLICT":
            material_conflict_groups += 1
            material_conflict_rows_quarantined += len(rows)
            material_open_times.add(open_time)
            clean_by_open_time.pop(open_time, None)
            if len(material_samples) < 25:
                material_samples.append(
                    {
                        "symbol": symbol,
                        "open_time": open_time,
                        "quarantined_rows": len(rows),
                        "raw_rows": [row.sample() for row in rows],
                    }
                )
        elif duplicate_type == "CONFIRM_ONLY_CONFLICT":
            confirm_only_conflict_groups += 1
        else:
            unknown_duplicate_groups += 1
        if len(duplicate_group_samples) < 100:
            duplicate_group_samples.append(
                {
                    "symbol": symbol,
                    "open_time": open_time,
                    "duplicate_type": duplicate_type,
                    "row_count": len(rows),
                    "extra_row_count": len(rows) - 1,
                }
            )

    require(schema_mismatch_count == 0, f"{symbol} schema mismatch count {schema_mismatch_count}")
    require(symbol_mismatch_count == 0, f"{symbol} symbol mismatch count {symbol_mismatch_count}")
    require(confirm_only_conflict_groups == 0, f"{symbol} confirm-only conflict groups {confirm_only_conflict_groups}")
    require(unknown_duplicate_groups == 0, f"{symbol} unknown duplicate groups {unknown_duplicate_groups}")

    missing_minute_count, missing_hour_count, missing_samples = raw_missing_minutes(all_open_times)
    output_rows, hour_stats = aggregate_symbol(symbol, clean_by_open_time, material_open_times)
    clean_source_rows = len(clean_by_open_time)
    return {
        "symbol": symbol,
        "raw_row_count": raw_row_count,
        "unique_open_time_count": len(all_open_times),
        "clean_source_rows_after_policy": clean_source_rows,
        "sha256_revalidated_count": sha_revalidated_count,
        "zip_open_count": zip_open_count,
        "csv_read_count": csv_read_count,
        "schema_mismatch_count": schema_mismatch_count,
        "symbol_mismatch_count": symbol_mismatch_count,
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_extra_row_count": raw_row_count - len(all_open_times),
        "exact_duplicate_group_count": exact_duplicate_groups,
        "exact_duplicate_rows_dropped": exact_duplicate_rows_dropped,
        "material_conflict_group_count": material_conflict_groups,
        "material_conflict_rows_quarantined": material_conflict_rows_quarantined,
        "confirm_only_conflict_group_count": confirm_only_conflict_groups,
        "unknown_duplicate_group_count": unknown_duplicate_groups,
        "missing_minute_count": missing_minute_count,
        "raw_missing_affected_hour_count": missing_hour_count,
        "output_1h_row_count": hour_stats["output_1h_row_count"],
        "complete_1h_row_count": hour_stats["complete_1h_row_count"],
        "incomplete_1h_row_count": hour_stats["incomplete_1h_row_count"],
        "affected_hour_count": hour_stats["affected_hour_count"],
        "any_incomplete_hour_marked_complete": hour_stats["any_incomplete_hour_marked_complete"],
        "numeric_sanity_issue_count": hour_stats["numeric_sanity_issue_count"],
        "incomplete_hour_samples": hour_stats["incomplete_hour_samples"],
        "missing_open_time_samples": missing_samples,
        "exact_duplicate_samples": exact_samples,
        "material_conflict_samples": material_samples,
        "duplicate_group_samples": duplicate_group_samples,
        "file_audits": file_audits,
        "output_rows": output_rows,
    }


def aggregate_symbol(
    symbol: str,
    clean_by_open_time: dict[int, MinuteRow],
    material_open_times: set[int],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    output_rows: list[dict[str, str]] = []
    incomplete_samples: list[dict[str, Any]] = []
    numeric_sanity_issue_count = 0
    any_incomplete_marked_complete = False
    current_hour: int | None = None
    bucket: list[MinuteRow] = []
    material_hours = {(value // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS for value in material_open_times}

    def flush(hour_start: int | None, rows: list[MinuteRow]) -> None:
        nonlocal numeric_sanity_issue_count, any_incomplete_marked_complete
        if hour_start is None or not rows:
            return
        rows.sort(key=lambda row: row.open_time)
        source_row_count = len(rows)
        high_row = max(rows, key=lambda row: decimal_value(row.high, "high"))
        low_row = min(rows, key=lambda row: decimal_value(row.low, "low"))
        open_row = rows[0]
        close_row = rows[-1]
        vol = sum(decimal_value(row.vol, "vol") for row in rows)
        vol_ccy = sum(decimal_value(row.vol_ccy, "vol_ccy") for row in rows)
        vol_quote = sum(decimal_value(row.vol_quote, "vol_quote") for row in rows)
        complete = source_row_count == 60
        quarantine_applied = hour_start in material_hours
        missing_minute_applied = source_row_count < 60
        reasons: list[str] = []
        if quarantine_applied:
            reasons.append("MATERIAL_DUPLICATE_CONFLICT_QUARANTINE")
        if missing_minute_applied:
            reasons.append("MISSING_MINUTE_OR_POLICY_REMOVED_MINUTE")
        if source_row_count < 60 and complete:
            any_incomplete_marked_complete = True
        high_decimal = decimal_value(high_row.high, "high")
        low_decimal = decimal_value(low_row.low, "low")
        open_decimal = decimal_value(open_row.open, "open")
        close_decimal = decimal_value(close_row.close, "close")
        if high_decimal < low_decimal or high_decimal < open_decimal or high_decimal < close_decimal or low_decimal > open_decimal or low_decimal > close_decimal:
            numeric_sanity_issue_count += 1
        if not complete and len(incomplete_samples) < 50:
            incomplete_samples.append(
                {
                    "symbol": symbol,
                    "hour_start_epoch_ms": hour_start,
                    "hour_start_iso_utc": iso_from_ms(hour_start),
                    "source_row_count": source_row_count,
                    "quarantine_applied": quarantine_applied,
                    "missing_minute_applied": missing_minute_applied,
                    "incomplete_reason": "|".join(reasons),
                }
            )
        output_rows.append(
            {
                "instrument_name": symbol,
                "hour_start_epoch_ms": str(hour_start),
                "hour_start_iso_utc": iso_from_ms(hour_start),
                "open": open_row.open,
                "high": high_row.high,
                "low": low_row.low,
                "close": close_row.close,
                "vol": decimal_text(vol),
                "vol_ccy": decimal_text(vol_ccy),
                "vol_quote": decimal_text(vol_quote),
                "source_row_count": str(source_row_count),
                "complete_hour": "true" if complete else "false",
                "confirm": "true" if all(truthy_confirm(row.confirm) for row in rows) else "false",
                "source_first_open_time": str(open_row.open_time),
                "source_last_open_time": str(close_row.open_time),
                "source_zip_sha256": ";".join(sorted({row.source_zip_sha256 for row in rows})),
                "source_csv_file": ";".join(sorted({row.source_csv_file for row in rows})),
                "source_date": ";".join(sorted({row.source_date for row in rows})),
                "build_scope": "OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN",
                "policy_clean_build": "true",
                "quarantine_applied": "true" if quarantine_applied else "false",
                "missing_minute_applied": "true" if missing_minute_applied else "false",
                "incomplete_reason": "|".join(reasons),
            }
        )

    for open_time in sorted(clean_by_open_time):
        row = clean_by_open_time[open_time]
        hour_start = (open_time // EXPECTED_HOUR_MS) * EXPECTED_HOUR_MS
        if current_hour is None:
            current_hour = hour_start
        if hour_start != current_hour:
            flush(current_hour, bucket)
            current_hour = hour_start
            bucket = []
        bucket.append(row)
    flush(current_hour, bucket)
    complete_count = sum(1 for row in output_rows if row["complete_hour"] == "true")
    incomplete_count = len(output_rows) - complete_count
    return output_rows, {
        "output_1h_row_count": len(output_rows),
        "complete_1h_row_count": complete_count,
        "incomplete_1h_row_count": incomplete_count,
        "affected_hour_count": incomplete_count,
        "any_incomplete_hour_marked_complete": any_incomplete_marked_complete,
        "numeric_sanity_issue_count": numeric_sanity_issue_count,
        "incomplete_hour_samples": incomplete_samples,
    }


def write_output_csv(symbol_results: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_SCHEMA)
        writer.writeheader()
        for result in symbol_results:
            for row in result["output_rows"]:
                writer.writerow(row)


def summarize(symbol_results: list[dict[str, Any]], chain: dict[str, Any], py_state: dict[str, Any]) -> dict[str, Any]:
    totals = {
        "pilot_symbol_count": len(PILOT_SYMBOLS),
        "symbols_processed_count": len(symbol_results),
        "file_count_total": sum(result["zip_open_count"] for result in symbol_results),
        "total_raw_rows_scanned": sum(result["raw_row_count"] for result in symbol_results),
        "total_exact_duplicate_rows_dropped": sum(result["exact_duplicate_rows_dropped"] for result in symbol_results),
        "total_material_conflict_rows_quarantined": sum(result["material_conflict_rows_quarantined"] for result in symbol_results),
        "total_missing_minute_count": sum(result["missing_minute_count"] for result in symbol_results),
        "clean_source_rows_after_policy": sum(result["clean_source_rows_after_policy"] for result in symbol_results),
        "output_1h_row_count": sum(result["output_1h_row_count"] for result in symbol_results),
        "complete_1h_row_count": sum(result["complete_1h_row_count"] for result in symbol_results),
        "incomplete_1h_row_count": sum(result["incomplete_1h_row_count"] for result in symbol_results),
        "affected_hour_count": sum(result["affected_hour_count"] for result in symbol_results),
        "any_incomplete_hour_marked_complete": any(result["any_incomplete_hour_marked_complete"] for result in symbol_results),
        "numeric_sanity_issue_count": sum(result["numeric_sanity_issue_count"] for result in symbol_results),
    }
    symbols_with_incomplete = [result["symbol"] for result in symbol_results if result["incomplete_1h_row_count"] > 0]
    symbols_with_missing = [result["symbol"] for result in symbol_results if result["missing_minute_count"] > 0]
    replacement_checks = {
        **chain["checks"],
        "exactly_10_symbols_processed": totals["symbols_processed_count"] == 10,
        "file_count_total_10530": totals["file_count_total"] == EXPECTED_FILE_COUNT_TOTAL,
        "raw_rows_expected": totals["total_raw_rows_scanned"] == EXPECTED_RAW_ROWS,
        "exact_duplicate_rows_dropped_expected": totals["total_exact_duplicate_rows_dropped"] == EXPECTED_EXACT_DUPLICATE_ROWS_DROPPED,
        "material_conflict_rows_quarantined_expected": totals["total_material_conflict_rows_quarantined"] == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "missing_minutes_expected": totals["total_missing_minute_count"] == EXPECTED_MISSING_MINUTES,
        "clean_source_rows_expected": totals["clean_source_rows_after_policy"] == EXPECTED_CLEAN_SOURCE_ROWS,
        "no_incomplete_hour_marked_complete": totals["any_incomplete_hour_marked_complete"] is False,
        "numeric_sanity_clean": totals["numeric_sanity_issue_count"] == 0,
        "output_csv_created": OUTPUT_CSV.exists(),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    return {
        "historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_status": status,
        "batch_policy_clean_build_execution_performed": replacement_checks_all_true,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        **totals,
        "expected_clean_source_rows_after_policy": EXPECTED_CLEAN_SOURCE_ROWS,
        "all_symbols_complete": len(symbols_with_incomplete) == 0,
        "symbols_with_incomplete_hours": symbols_with_incomplete,
        "symbols_with_missing_minutes": symbols_with_missing,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_csv_created": OUTPUT_CSV.exists(),
        "output_manifest_created": True,
        "output_is_batch_policy_clean_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "no_new_download": True,
        "new_download_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_build_performed": True,
        "aggregation_performed_now": True,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 505,
        "dormant_repo_attention_count": DORMANT_REPO_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_execution": AFTER_QUALITY if replacement_checks_all_true else "BATCH_POLICY_CLEAN_BUILD_EXECUTION_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_reports(symbol_results: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    per_symbol = [
        {key: value for key, value in result.items() if key not in {"output_rows", "file_audits"}}
        for result in symbol_results
    ]
    file_audits = [item for result in symbol_results for item in result["file_audits"]]
    output_sha = sha256_file(OUTPUT_CSV) if OUTPUT_CSV.exists() else None
    output_size = OUTPUT_CSV.stat().st_size if OUTPUT_CSV.exists() else 0
    return {
        "execution_report": {
            **summary,
            "per_symbol_execution": per_symbol,
        },
        "manifest": {
            **summary,
            "output_files": [
                {
                    "path": str(OUTPUT_CSV),
                    "sha256": output_sha,
                    "size_bytes": output_size,
                    "schema": OUTPUT_SCHEMA,
                    "row_count": summary["output_1h_row_count"],
                }
            ],
            "output_written_outside_tracked_repo_code_paths": not str(OUTPUT_CSV).startswith(str(REPO_ROOT)),
        },
        "exact_duplicate_audit": {
            **summary,
            "total_exact_duplicate_rows_dropped": summary["total_exact_duplicate_rows_dropped"],
            "per_symbol": [
                {
                    "symbol": result["symbol"],
                    "exact_duplicate_group_count": result["exact_duplicate_group_count"],
                    "exact_duplicate_rows_dropped": result["exact_duplicate_rows_dropped"],
                    "samples": result["exact_duplicate_samples"],
                }
                for result in symbol_results
            ],
        },
        "material_conflict_audit": {
            **summary,
            "total_material_conflict_rows_quarantined": summary["total_material_conflict_rows_quarantined"],
            "conflicting_row_selected_or_averaged_or_merged": False,
            "per_symbol": [
                {
                    "symbol": result["symbol"],
                    "material_conflict_group_count": result["material_conflict_group_count"],
                    "material_conflict_rows_quarantined": result["material_conflict_rows_quarantined"],
                    "samples": result["material_conflict_samples"],
                }
                for result in symbol_results
            ],
        },
        "missing_minute_audit": {
            **summary,
            "total_missing_minute_count": summary["total_missing_minute_count"],
            "missing_minutes_filled": False,
            "per_symbol": [
                {
                    "symbol": result["symbol"],
                    "missing_minute_count": result["missing_minute_count"],
                    "raw_missing_affected_hour_count": result["raw_missing_affected_hour_count"],
                    "missing_open_time_samples": result["missing_open_time_samples"],
                }
                for result in symbol_results
            ],
        },
        "incomplete_hour_report": {
            **summary,
            "per_symbol": [
                {
                    "symbol": result["symbol"],
                    "output_1h_row_count": result["output_1h_row_count"],
                    "complete_1h_row_count": result["complete_1h_row_count"],
                    "incomplete_1h_row_count": result["incomplete_1h_row_count"],
                    "affected_hour_count": result["affected_hour_count"],
                    "samples": result["incomplete_hour_samples"],
                }
                for result in symbol_results
            ],
        },
        "schema_validation_report": {
            **summary,
            "expected_input_schema": EXPECTED_SCHEMA,
            "expected_output_schema": OUTPUT_SCHEMA,
            "schema_mismatch_count": sum(result["schema_mismatch_count"] for result in symbol_results),
            "symbol_mismatch_count": sum(result["symbol_mismatch_count"] for result in symbol_results),
        },
        "provenance_report": {
            **summary,
            "file_count_total": summary["file_count_total"],
            "sha256_revalidated_before_csv_read": True,
            "file_audits": file_audits,
        },
        "numeric_sanity_report": {
            **summary,
            "numeric_sanity_issue_count": summary["numeric_sanity_issue_count"],
            "ohlc_sanity_checked": True,
            "volume_sums_computed_from_clean_rows": True,
            "vol_ccy_and_vol_quote_literal_none_treated_as_zero_for_sum": True,
        },
        "compliance_report": {
            **summary,
            "no_new_download": True,
            "new_download_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "url_fetch_performed_now": False,
            "synthetic_fill_used": False,
            "forward_fill_used": False,
            "backfill_used": False,
            "research_backtest_edge_claim_made": False,
            "full_universe_ready_claim_made": False,
            "broad_acquisition_ready_claim_made": False,
            "runtime_capital_live_touched": False,
            "schema_or_config_created": False,
            "generic_runner_approval_granted": False,
        },
        "summary": summary,
    }


def write_reports(reports: dict[str, Any]) -> None:
    mapping = {
        "execution_report": "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_report.json",
        "manifest": "historical_okx_10_symbol_pilot_batch_policy_clean_1h_output_manifest.json",
        "exact_duplicate_audit": "historical_okx_10_symbol_pilot_batch_exact_duplicate_drop_audit.json",
        "material_conflict_audit": "historical_okx_10_symbol_pilot_batch_material_conflict_quarantine_audit.json",
        "missing_minute_audit": "historical_okx_10_symbol_pilot_batch_missing_minute_audit.json",
        "incomplete_hour_report": "historical_okx_10_symbol_pilot_batch_incomplete_hour_report.json",
        "schema_validation_report": "historical_okx_10_symbol_pilot_batch_policy_clean_schema_validation_report.json",
        "provenance_report": "historical_okx_10_symbol_pilot_batch_policy_clean_output_provenance_report.json",
        "numeric_sanity_report": "historical_okx_10_symbol_pilot_batch_policy_clean_numeric_sanity_report.json",
        "compliance_report": "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_compliance_report.json",
        "summary": "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_summary.json",
    }
    for key, name in mapping.items():
        write_json(OUTPUT_DIR / name, reports[key])


def run_build() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    chain = validate_chain(artifacts, py_state)
    require(all(chain["checks"].values()), f"chain validation failed: {chain['checks']}")
    grouped = group_hash_items(artifacts["download_hash_validation_report"])
    symbol_results = [scan_symbol(symbol, grouped[symbol]) for symbol in PILOT_SYMBOLS]
    write_output_csv(symbol_results)
    summary = summarize(symbol_results, chain, py_state)
    reports = build_reports(symbol_results, summary)
    write_reports(reports)
    missing_outputs = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing_outputs, f"missing required outputs: {missing_outputs}")
    require(summary["replacement_checks_all_true"] is True, "replacement checks did not all pass")
    return summary


def main() -> int:
    try:
        summary = run_build()
    except Exception as exc:
        blocked = {
            "historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_status": BLOCKED_STATUS,
            "batch_policy_clean_build_execution_performed": False,
            "blocked_reason": repr(exc),
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "created_at_utc": utc_now(),
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "new_download_performed_now": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
