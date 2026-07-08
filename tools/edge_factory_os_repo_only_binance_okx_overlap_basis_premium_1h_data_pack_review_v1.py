#!/usr/bin/env python
"""Review the Binance/OKX overlap basis/premium 1h data pack.

This module performs data validation only. It does not execute strategy logic,
compute returns, generate candidates, claim edge, or grant runtime/live/capital
permission.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EXPECTED_HEAD = "47f3547340973749d518a93207698fd2462f25ae"
EXPECTED_TRACKED_PYTHON_COUNT = 868

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_okx_overlap_basis_premium_1h_data_pack_review_v1.py"
)
REVIEW_ARTIFACT_RELATIVE_PATH = (
    "artifacts/basis_premium_data_reviews/"
    "binance_okx_overlap_basis_premium_1h_data_pack_review_v1.json"
)
MANIFEST_RELATIVE_PATH = (
    "artifacts/basis_premium_data_locks/"
    "binance_okx_overlap_basis_premium_1h_data_pack_v1.json"
)

MODULE_PATH = REPO_ROOT / MODULE_RELATIVE_PATH
REVIEW_ARTIFACT_PATH = REPO_ROOT / REVIEW_ARTIFACT_RELATIVE_PATH
MANIFEST_PATH = REPO_ROOT / MANIFEST_RELATIVE_PATH

EXTERNAL_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_basis_premium_1h_data_pack_v1"
)
EXTERNAL_ROW_DIR = EXTERNAL_ROOT / "basis_premium_by_symbol"
EXTERNAL_INDEX_PATH = (
    EXTERNAL_ROOT
    / "basis_premium_index"
    / "binance_okx_overlap_basis_premium_1h_index_v1.json"
)

EXPECTED_SOURCE_STATUS = (
    "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_CREATED"
)
REVIEW_STATUS = (
    "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_REVIEW_CREATED"
)
EXPECTED_MANIFEST_PAYLOAD_SHA256 = (
    "9fb2943502e37c2d288e09d7daadf97ff9f9e63d90ebcb2d02c1f29029508b9b"
)
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_TOTAL_ROWS = 1_952_156
EXPECTED_MIN_TIMESTAMP_UTC = "2023-01-01T00:00:00Z"
EXPECTED_MAX_TIMESTAMP_UTC = "2025-10-31T23:00:00Z"
EXPECTED_START_MS = 1_672_531_200_000
EXPECTED_MAX_MS = 1_761_951_600_000
HOUR_MS = 3_600_000

PASS_CLASSIFICATION = (
    "BASIS_PREMIUM_REVIEW_PASS_VALID_FOR_FUTURE_BASIS_PREMIUM_FEATURE_CONSTRUCTION"
)
PASS_WITH_P1_CLASSIFICATION = (
    "BASIS_PREMIUM_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_FUTURE_BASIS_PREMIUM_FEATURE_CONSTRUCTION"
)
FAIL_CLASSIFICATION = "BASIS_PREMIUM_REVIEW_FAIL_REQUIRES_REACQUISITION_OR_REPAIR"

REQUIRED_FIELDS = (
    "symbol",
    "timestamp_utc",
    "timestamp_ms",
    "premium_open",
    "premium_high",
    "premium_low",
    "premium_close",
    "mark_open",
    "mark_high",
    "mark_low",
    "mark_close",
    "index_open",
    "index_high",
    "index_low",
    "index_close",
    "source_endpoints",
    "interval",
)

NUMERIC_FIELDS = (
    "premium_open",
    "premium_high",
    "premium_low",
    "premium_close",
    "mark_open",
    "mark_high",
    "mark_low",
    "mark_close",
    "index_open",
    "index_high",
    "index_low",
    "index_close",
)

MARK_FIELDS = ("mark_open", "mark_high", "mark_low", "mark_close")
INDEX_FIELDS = ("index_open", "index_high", "index_low", "index_close")
INTERVAL_EQUIVALENTS = {"1h", "1H", "60m", "60min", "3600s", "3600000ms", "hour", "1hour"}


def to_repo_slash(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def normalized_path(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(str(path)))


def path_is_inside(path: str | Path, root: str | Path) -> bool:
    try:
        return os.path.commonpath([normalized_path(path), normalized_path(root)]) == normalized_path(root)
    except ValueError:
        return False


def run_git(args: list[str]) -> list[str]:
    safe_dir = to_repo_slash(REPO_ROOT)
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={safe_dir}", "-C", str(REPO_ROOT), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout = completed.stdout.strip("\n")
    if not stdout:
        return []
    return stdout.splitlines()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_timestamp_ms(timestamp_utc: object, timestamp_ms: object) -> tuple[int | None, str | None]:
    if not isinstance(timestamp_utc, str) or not timestamp_utc.endswith("Z"):
        return None, "timestamp_utc_missing_z"
    try:
        parsed = datetime.strptime(timestamp_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None, "timestamp_utc_malformed"
    if parsed.minute != 0 or parsed.second != 0 or parsed.microsecond != 0:
        return None, "timestamp_not_hourly_aligned"

    expected_ms = int(parsed.timestamp() * 1000)
    try:
        actual_ms = parse_integer(timestamp_ms)
    except ValueError:
        return None, "timestamp_ms_malformed"
    if actual_ms != expected_ms:
        return None, "timestamp_ms_mismatch"
    if actual_ms % HOUR_MS != 0:
        return None, "timestamp_ms_not_hourly_aligned"
    return actual_ms, None


def parse_integer(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("bool_not_integer")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isfinite(value) and value.is_integer():
            return int(value)
        raise ValueError("float_not_integer")
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("+"):
            stripped = stripped[1:]
        if stripped.startswith("-"):
            digits = stripped[1:]
        else:
            digits = stripped
        if digits.isdigit():
            return int(stripped)
    raise ValueError("not_integer")


def parse_number(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("bool_not_numeric")
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError("not_numeric")
    if not math.isfinite(parsed):
        raise ValueError("not_finite")
    return parsed


def update_min(current: float | None, value: float) -> float:
    if current is None:
        return value
    return value if value < current else current


def update_max(current: float | None, value: float) -> float:
    if current is None:
        return value
    return value if value > current else current


def iso_from_ms(timestamp_ms: int | None) -> str | None:
    if timestamp_ms is None:
        return None
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def status_paths(status_lines: list[str]) -> set[str]:
    paths: set[str] = set()
    for line in status_lines:
        if not line:
            continue
        paths.add(line[3:].strip().replace("\\", "/"))
    return paths


def status_has_only_expected_new_files(status_lines: list[str], expected_paths: set[str]) -> bool:
    if len(status_lines) != len(expected_paths):
        return False
    for line in status_lines:
        if not line.startswith("?? "):
            return False
        if line[3:].strip().replace("\\", "/") not in expected_paths:
            return False
    return True


def manifest_payload_review(manifest: dict) -> tuple[dict, list[str], list[str]]:
    issues: list[str] = []
    p1_reasons: list[str] = []
    summary = manifest.get("acquisition_summary", {})
    safety = manifest.get("safety_permissions", {})
    endpoint_missing = summary.get("endpoint_missing_row_counts", {})

    checks = {
        "status_verified": manifest.get("status") == EXPECTED_SOURCE_STATUS,
        "payload_hash_verified": manifest.get("payload_sha256_excluding_hash")
        == EXPECTED_MANIFEST_PAYLOAD_SHA256,
        "symbols_with_rows_verified": summary.get("symbols_with_rows_count") == EXPECTED_SYMBOL_COUNT,
        "symbols_with_zero_rows_verified": summary.get("symbols_with_zero_rows_count") == 0,
        "total_rows_verified": summary.get("total_rows") == EXPECTED_TOTAL_ROWS,
        "min_timestamp_verified": summary.get("min_timestamp_utc") == EXPECTED_MIN_TIMESTAMP_UTC,
        "max_timestamp_verified": summary.get("max_timestamp_utc") == EXPECTED_MAX_TIMESTAMP_UTC,
        "data_valid_for_future_basis_premium_research_verified": summary.get(
            "data_valid_for_future_basis_premium_research"
        )
        is True,
        "strategy_execution_flag_false": safety.get("strategy_execution_allowed_now") is False,
        "candidate_generation_flag_false": safety.get("candidate_generation_allowed_now") is False,
        "edge_claim_flag_false": safety.get("edge_claim_allowed_now") is False,
        "runtime_permission_flag_false": safety.get("runtime_permission_allowed_now") is False,
        "live_permission_flag_false": safety.get("live_permission_allowed_now") is False,
        "capital_permission_flag_false": safety.get("capital_permission_allowed_now") is False,
    }
    for key, passed in checks.items():
        if not passed:
            issues.append(f"manifest_{key}_failed")

    if any(int(endpoint_missing.get(endpoint, 0) or 0) > 0 for endpoint in ("premium", "mark", "index")):
        p1_reasons.append("manifest_records_missing_endpoint_rows")

    review = {
        "manifest_path": MANIFEST_RELATIVE_PATH,
        "loaded": True,
        "status_expected": EXPECTED_SOURCE_STATUS,
        "status_actual": manifest.get("status"),
        "payload_sha256_expected": EXPECTED_MANIFEST_PAYLOAD_SHA256,
        "payload_sha256_actual": manifest.get("payload_sha256_excluding_hash"),
        "symbols_with_rows_actual": summary.get("symbols_with_rows_count"),
        "symbols_with_zero_rows_actual": summary.get("symbols_with_zero_rows_count"),
        "total_rows_actual": summary.get("total_rows"),
        "min_timestamp_utc_actual": summary.get("min_timestamp_utc"),
        "max_timestamp_utc_actual": summary.get("max_timestamp_utc"),
        "data_valid_for_future_basis_premium_research_actual": summary.get(
            "data_valid_for_future_basis_premium_research"
        ),
        "endpoint_missing_row_counts": endpoint_missing,
        "safety_permissions_source": safety,
        "checks": checks,
    }
    return review, issues, p1_reasons


def review_symbol_file(
    symbol: str,
    file_path: Path,
    index_record: dict,
    manifest_row_hashes: dict,
) -> tuple[dict, list[str], dict]:
    file_hash = sha256_file(file_path)
    expected_filename = f"{symbol}_basis_premium_1h.jsonl.gz"

    counters = {
        "required_field_missing_count": 0,
        "invalid_numeric_count": 0,
        "mark_index_nonpositive_count": 0,
        "timestamp_malformed_count": 0,
        "timestamp_ms_mismatch_count": 0,
        "timestamp_not_hourly_aligned_count": 0,
        "rows_outside_window_count": 0,
        "duplicate_symbol_timestamp_count": 0,
        "unsorted_timestamp_count": 0,
        "wrong_symbol_count": 0,
        "invalid_interval_count": 0,
        "malformed_jsonl_count": 0,
        "extreme_abs_premium_close_gt_0_10_count": 0,
        "extreme_abs_mark_index_basis_close_gt_0_10_count": 0,
    }

    issues: list[str] = []
    seen_timestamps: set[int] = set()
    row_count = 0
    min_ms: int | None = None
    max_ms: int | None = None
    previous_ms: int | None = None
    min_premium_close: float | None = None
    max_premium_close: float | None = None
    min_basis_close: float | None = None
    max_basis_close: float | None = None

    try:
        with gzip.open(file_path, "rt", encoding="utf-8", newline="") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    counters["malformed_jsonl_count"] += 1
                    issues.append(f"{symbol}:blank_jsonl_line:{line_number}")
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    counters["malformed_jsonl_count"] += 1
                    issues.append(f"{symbol}:malformed_jsonl_line:{line_number}")
                    continue

                row_count += 1
                missing_fields = [field for field in REQUIRED_FIELDS if field not in row]
                counters["required_field_missing_count"] += len(missing_fields)
                if missing_fields:
                    issues.append(f"{symbol}:missing_required_fields_line:{line_number}")
                    continue

                if row.get("symbol") != symbol:
                    counters["wrong_symbol_count"] += 1
                    issues.append(f"{symbol}:wrong_symbol_line:{line_number}")

                interval = row.get("interval")
                if not isinstance(interval, str) or interval not in INTERVAL_EQUIVALENTS:
                    counters["invalid_interval_count"] += 1
                    issues.append(f"{symbol}:invalid_interval_line:{line_number}")

                timestamp_ms, timestamp_error = parse_timestamp_ms(
                    row.get("timestamp_utc"), row.get("timestamp_ms")
                )
                if timestamp_error:
                    if timestamp_error == "timestamp_ms_mismatch":
                        counters["timestamp_ms_mismatch_count"] += 1
                    elif "hourly_aligned" in timestamp_error:
                        counters["timestamp_not_hourly_aligned_count"] += 1
                    else:
                        counters["timestamp_malformed_count"] += 1
                    issues.append(f"{symbol}:{timestamp_error}_line:{line_number}")
                    continue

                if timestamp_ms in seen_timestamps:
                    counters["duplicate_symbol_timestamp_count"] += 1
                    issues.append(f"{symbol}:duplicate_timestamp_line:{line_number}")
                seen_timestamps.add(timestamp_ms)

                if previous_ms is not None and timestamp_ms <= previous_ms:
                    counters["unsorted_timestamp_count"] += 1
                    issues.append(f"{symbol}:timestamp_not_strictly_increasing_line:{line_number}")
                previous_ms = timestamp_ms

                if timestamp_ms < EXPECTED_START_MS or timestamp_ms > EXPECTED_MAX_MS:
                    counters["rows_outside_window_count"] += 1
                    issues.append(f"{symbol}:row_outside_window_line:{line_number}")

                min_ms = timestamp_ms if min_ms is None or timestamp_ms < min_ms else min_ms
                max_ms = timestamp_ms if max_ms is None or timestamp_ms > max_ms else max_ms

                parsed_numbers: dict[str, float] = {}
                for field in NUMERIC_FIELDS:
                    try:
                        parsed_numbers[field] = parse_number(row.get(field))
                    except ValueError:
                        counters["invalid_numeric_count"] += 1
                        issues.append(f"{symbol}:invalid_numeric_{field}_line:{line_number}")

                if len(parsed_numbers) != len(NUMERIC_FIELDS):
                    continue

                for field in MARK_FIELDS + INDEX_FIELDS:
                    if parsed_numbers[field] <= 0:
                        counters["mark_index_nonpositive_count"] += 1
                        issues.append(f"{symbol}:nonpositive_{field}_line:{line_number}")

                premium_close = parsed_numbers["premium_close"]
                index_close = parsed_numbers["index_close"]
                mark_close = parsed_numbers["mark_close"]
                basis_close = mark_close / index_close - 1.0

                min_premium_close = update_min(min_premium_close, premium_close)
                max_premium_close = update_max(max_premium_close, premium_close)
                min_basis_close = update_min(min_basis_close, basis_close)
                max_basis_close = update_max(max_basis_close, basis_close)

                if abs(premium_close) > 0.10:
                    counters["extreme_abs_premium_close_gt_0_10_count"] += 1
                if abs(basis_close) > 0.10:
                    counters["extreme_abs_mark_index_basis_close_gt_0_10_count"] += 1
    except OSError as exc:
        issues.append(f"{symbol}:unreadable_file:{exc}")
        counters["malformed_jsonl_count"] += 1

    index_hash = index_record.get("sha256")
    manifest_hash = manifest_row_hashes.get(symbol)
    file_hash_matches_index = index_hash == file_hash
    file_hash_matches_manifest = manifest_hash == file_hash
    if not file_hash_matches_index:
        issues.append(f"{symbol}:file_sha256_mismatch_index")
    if not file_hash_matches_manifest:
        issues.append(f"{symbol}:file_sha256_mismatch_manifest")

    index_row_count = index_record.get("row_count")
    row_count_matches_index = index_row_count == row_count
    if not row_count_matches_index:
        issues.append(f"{symbol}:row_count_mismatch_index")

    record = {
        "symbol": symbol,
        "file_path": str(file_path),
        "file_name_matches_symbol": file_path.name == expected_filename,
        "row_count": row_count,
        "index_row_count": index_row_count,
        "row_count_matches_index": row_count_matches_index,
        "min_timestamp_utc": iso_from_ms(min_ms),
        "max_timestamp_utc": iso_from_ms(max_ms),
        "sha256": file_hash,
        "index_sha256": index_hash,
        "manifest_sha256": manifest_hash,
        "file_hash_matches_index": file_hash_matches_index,
        "file_hash_matches_manifest": file_hash_matches_manifest,
        "required_field_missing_count": counters["required_field_missing_count"],
        "invalid_numeric_count": counters["invalid_numeric_count"],
        "mark_index_nonpositive_count": counters["mark_index_nonpositive_count"],
        "timestamp_malformed_count": counters["timestamp_malformed_count"],
        "timestamp_ms_mismatch_count": counters["timestamp_ms_mismatch_count"],
        "timestamp_not_hourly_aligned_count": counters["timestamp_not_hourly_aligned_count"],
        "rows_outside_window_count": counters["rows_outside_window_count"],
        "duplicate_symbol_timestamp_count": counters["duplicate_symbol_timestamp_count"],
        "unsorted_timestamp_count": counters["unsorted_timestamp_count"],
        "wrong_symbol_count": counters["wrong_symbol_count"],
        "invalid_interval_count": counters["invalid_interval_count"],
        "malformed_jsonl_count": counters["malformed_jsonl_count"],
        "min_premium_close": min_premium_close,
        "max_premium_close": max_premium_close,
        "min_mark_index_basis_close": min_basis_close,
        "max_mark_index_basis_close": max_basis_close,
        "extreme_abs_premium_close_gt_0_10_count": counters[
            "extreme_abs_premium_close_gt_0_10_count"
        ],
        "extreme_abs_mark_index_basis_close_gt_0_10_count": counters[
            "extreme_abs_mark_index_basis_close_gt_0_10_count"
        ],
    }
    return record, issues, counters


def build_payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    p0_issues: list[str] = []
    p1_reasons: list[str] = []

    expected_pre_run_paths = {MODULE_RELATIVE_PATH}
    expected_post_run_paths = {MODULE_RELATIVE_PATH, REVIEW_ARTIFACT_RELATIVE_PATH}

    status_before = run_git(["status", "--short"])
    head = run_git(["rev-parse", "HEAD"])[0]
    tracked_python_count = len(run_git(["ls-files", "*.py"]))
    repo_clean_before_run = status_has_only_expected_new_files(status_before, expected_pre_run_paths)

    if head != EXPECTED_HEAD:
        p0_issues.append("source_checkpoint_head_mismatch")
    if tracked_python_count != EXPECTED_TRACKED_PYTHON_COUNT:
        p0_issues.append("tracked_python_count_mismatch_before_review_tool_tracking")
    if not repo_clean_before_run:
        p0_issues.append("unexpected_repo_status_before_review_run")
    if not MODULE_PATH.exists():
        p0_issues.append("review_tool_missing")
    if REVIEW_ARTIFACT_PATH.exists():
        print("BLOCKED: review artifact already exists; refusing to modify existing file")
        print("replacement_checks_all_true: false")
        return 1

    manifest_loaded = False
    external_index_loaded = False
    try:
        manifest = load_json(MANIFEST_PATH)
        manifest_loaded = True
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: unable to load tracked manifest: {exc}")
        print("replacement_checks_all_true: false")
        return 1

    manifest_review, manifest_issues, manifest_p1_reasons = manifest_payload_review(manifest)
    p0_issues.extend(manifest_issues)
    p1_reasons.extend(manifest_p1_reasons)

    try:
        index = load_json(EXTERNAL_INDEX_PATH)
        external_index_loaded = True
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: unable to load external index: {exc}")
        print("replacement_checks_all_true: false")
        return 1

    reviewed_index_sha256 = sha256_file(EXTERNAL_INDEX_PATH)
    manifest_index_sha256 = manifest.get("non_repo_artifacts", {}).get("basis_premium_index_sha256")
    manifest_row_hashes = manifest.get("non_repo_artifacts", {}).get("output_files_sha256", {})
    symbol_records = index.get("symbol_records", [])

    external_index_outside_repo = not path_is_inside(EXTERNAL_INDEX_PATH, REPO_ROOT)
    index_hash_verified = (
        reviewed_index_sha256 == manifest_index_sha256 if manifest_index_sha256 else True
    )
    if not external_index_outside_repo:
        p0_issues.append("external_index_inside_repo")
    if not index_hash_verified:
        p0_issues.append("external_index_sha256_mismatch_manifest")
    if index.get("symbol_count") != EXPECTED_SYMBOL_COUNT or len(symbol_records) != EXPECTED_SYMBOL_COUNT:
        p0_issues.append("external_index_symbol_file_count_mismatch")

    referenced_file_checks = []
    all_row_files_exist = True
    all_row_files_inside_expected_dir = True
    all_row_files_outside_repo = True
    unique_symbols: set[str] = set()
    duplicate_index_symbol_count = 0

    for record in symbol_records:
        symbol = record.get("symbol")
        output_path = record.get("output_path")
        file_path = Path(output_path) if isinstance(output_path, str) else Path("")
        file_exists = file_path.exists()
        inside_row_dir = path_is_inside(file_path, EXTERNAL_ROW_DIR)
        outside_repo = not path_is_inside(file_path, REPO_ROOT)
        all_row_files_exist = all_row_files_exist and file_exists
        all_row_files_inside_expected_dir = all_row_files_inside_expected_dir and inside_row_dir
        all_row_files_outside_repo = all_row_files_outside_repo and outside_repo
        if symbol in unique_symbols:
            duplicate_index_symbol_count += 1
        if isinstance(symbol, str):
            unique_symbols.add(symbol)
        referenced_file_checks.append(
            {
                "symbol": symbol,
                "output_path": output_path,
                "exists": file_exists,
                "inside_expected_external_row_directory": inside_row_dir,
                "outside_repo": outside_repo,
            }
        )

    if not all_row_files_exist:
        p0_issues.append("one_or_more_row_files_missing")
    if not all_row_files_inside_expected_dir:
        p0_issues.append("one_or_more_row_files_outside_expected_external_row_directory")
    if not all_row_files_outside_repo:
        p0_issues.append("one_or_more_row_files_inside_repo")
    if duplicate_index_symbol_count:
        p0_issues.append("duplicate_symbol_in_external_index")

    symbol_review_records = []
    row_files_sha256: dict[str, str] = {}
    reviewed_total_rows = 0
    reviewed_min_ms: int | None = None
    reviewed_max_ms: int | None = None
    rows_per_symbol: list[int] = []
    symbols_with_zero_rows = []
    aggregate_counts = {
        "duplicate_symbol_timestamp_count": 0,
        "required_field_missing_count": 0,
        "invalid_numeric_count": 0,
        "mark_index_nonpositive_count": 0,
        "rows_outside_window_count": 0,
        "malformed_jsonl_count": 0,
        "timestamp_malformed_count": 0,
        "timestamp_ms_mismatch_count": 0,
        "timestamp_not_hourly_aligned_count": 0,
        "unsorted_timestamp_count": 0,
        "wrong_symbol_count": 0,
        "invalid_interval_count": 0,
        "extreme_abs_premium_close_gt_0_10_count": 0,
        "extreme_abs_mark_index_basis_close_gt_0_10_count": 0,
    }
    global_min_premium_close: float | None = None
    global_max_premium_close: float | None = None
    global_min_basis_close: float | None = None
    global_max_basis_close: float | None = None

    if all_row_files_exist and all_row_files_inside_expected_dir and all_row_files_outside_repo:
        for record in symbol_records:
            symbol = record["symbol"]
            file_path = Path(record["output_path"])
            review_record, symbol_issues, counters = review_symbol_file(
                symbol, file_path, record, manifest_row_hashes
            )
            symbol_review_records.append(review_record)
            row_files_sha256[symbol] = review_record["sha256"]
            p0_issues.extend(symbol_issues)

            row_count = review_record["row_count"]
            reviewed_total_rows += row_count
            rows_per_symbol.append(row_count)
            if row_count == 0:
                symbols_with_zero_rows.append(symbol)

            min_ts = review_record["min_timestamp_utc"]
            max_ts = review_record["max_timestamp_utc"]
            if min_ts:
                min_ms, _ = parse_timestamp_ms(min_ts, int(datetime.strptime(min_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000))
                if min_ms is not None:
                    reviewed_min_ms = min_ms if reviewed_min_ms is None or min_ms < reviewed_min_ms else reviewed_min_ms
            if max_ts:
                max_ms, _ = parse_timestamp_ms(max_ts, int(datetime.strptime(max_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000))
                if max_ms is not None:
                    reviewed_max_ms = max_ms if reviewed_max_ms is None or max_ms > reviewed_max_ms else reviewed_max_ms

            for key in aggregate_counts:
                aggregate_counts[key] += counters[key]

            if review_record["min_premium_close"] is not None:
                global_min_premium_close = update_min(
                    global_min_premium_close, review_record["min_premium_close"]
                )
            if review_record["max_premium_close"] is not None:
                global_max_premium_close = update_max(
                    global_max_premium_close, review_record["max_premium_close"]
                )
            if review_record["min_mark_index_basis_close"] is not None:
                global_min_basis_close = update_min(
                    global_min_basis_close, review_record["min_mark_index_basis_close"]
                )
            if review_record["max_mark_index_basis_close"] is not None:
                global_max_basis_close = update_max(
                    global_max_basis_close, review_record["max_mark_index_basis_close"]
                )

    reviewed_symbol_count = len(symbol_review_records)
    rows_per_symbol_min = min(rows_per_symbol) if rows_per_symbol else 0
    rows_per_symbol_max = max(rows_per_symbol) if rows_per_symbol else 0

    mark_index_price_sanity_valid = aggregate_counts["mark_index_nonpositive_count"] == 0
    premium_numeric_sanity_valid = aggregate_counts["invalid_numeric_count"] == 0
    row_counts_uneven = rows_per_symbol_min != rows_per_symbol_max
    if row_counts_uneven:
        p1_reasons.append("symbols_have_uneven_row_counts")
    if (
        aggregate_counts["extreme_abs_premium_close_gt_0_10_count"] > 0
        or aggregate_counts["extreme_abs_mark_index_basis_close_gt_0_10_count"] > 0
    ):
        p1_reasons.append("extreme_premium_or_basis_values_observed")

    if reviewed_symbol_count != EXPECTED_SYMBOL_COUNT:
        p0_issues.append("reviewed_symbol_count_mismatch")
    if reviewed_total_rows != EXPECTED_TOTAL_ROWS:
        p0_issues.append("reviewed_total_rows_mismatch_manifest")
    if iso_from_ms(reviewed_min_ms) != EXPECTED_MIN_TIMESTAMP_UTC:
        p0_issues.append("reviewed_min_timestamp_mismatch_expected")
    if iso_from_ms(reviewed_max_ms) != EXPECTED_MAX_TIMESTAMP_UTC:
        p0_issues.append("reviewed_max_timestamp_mismatch_expected")
    if symbols_with_zero_rows:
        p0_issues.append("one_or_more_symbols_with_zero_rows")
    if aggregate_counts["required_field_missing_count"] != 0:
        p0_issues.append("required_field_missing_count_nonzero")
    if aggregate_counts["invalid_numeric_count"] != 0:
        p0_issues.append("invalid_numeric_count_nonzero")
    if aggregate_counts["mark_index_nonpositive_count"] != 0:
        p0_issues.append("mark_or_index_nonpositive")
    if aggregate_counts["duplicate_symbol_timestamp_count"] != 0:
        p0_issues.append("duplicate_symbol_timestamp_nonzero")
    if aggregate_counts["rows_outside_window_count"] != 0:
        p0_issues.append("rows_outside_window_nonzero")
    if aggregate_counts["malformed_jsonl_count"] != 0:
        p0_issues.append("malformed_jsonl_nonzero")
    if aggregate_counts["timestamp_malformed_count"] != 0:
        p0_issues.append("timestamp_malformed_nonzero")
    if aggregate_counts["timestamp_ms_mismatch_count"] != 0:
        p0_issues.append("timestamp_ms_mismatch_nonzero")
    if aggregate_counts["timestamp_not_hourly_aligned_count"] != 0:
        p0_issues.append("timestamp_not_hourly_aligned_nonzero")
    if aggregate_counts["unsorted_timestamp_count"] != 0:
        p0_issues.append("unsorted_timestamp_nonzero")
    if aggregate_counts["wrong_symbol_count"] != 0:
        p0_issues.append("wrong_symbol_nonzero")
    if aggregate_counts["invalid_interval_count"] != 0:
        p0_issues.append("invalid_interval_nonzero")

    classification = FAIL_CLASSIFICATION
    if not p0_issues:
        classification = PASS_WITH_P1_CLASSIFICATION if p1_reasons else PASS_CLASSIFICATION

    safety_permissions = {
        "basis_premium_data_review_created": True,
        "basis_premium_data_valid_for_future_feature_construction": classification != FAIL_CLASSIFICATION,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "next_step_may_be_basis_premium_strategy_preregistration_only": True,
    }

    external_index_review = {
        "external_index_path": str(EXTERNAL_INDEX_PATH),
        "external_index_loaded": external_index_loaded,
        "external_index_outside_repo": external_index_outside_repo,
        "external_index_symbol_count_actual": index.get("symbol_count"),
        "referenced_symbol_file_count": len(symbol_records),
        "referenced_symbol_file_count_verified_81": len(symbol_records) == EXPECTED_SYMBOL_COUNT,
        "all_row_files_exist": all_row_files_exist,
        "all_row_files_inside_expected_external_row_directory": all_row_files_inside_expected_dir,
        "all_row_files_outside_repo": all_row_files_outside_repo,
        "duplicate_index_symbol_count": duplicate_index_symbol_count,
        "manifest_index_sha256": manifest_index_sha256,
        "reviewed_index_sha256": reviewed_index_sha256,
        "index_hash_verified": index_hash_verified,
        "referenced_file_checks": referenced_file_checks,
    }

    row_file_review_summary = {
        "row_files_reviewed": reviewed_symbol_count,
        "row_files_sha256": row_files_sha256,
        "malformed_jsonl_count": aggregate_counts["malformed_jsonl_count"],
        "wrong_symbol_count": aggregate_counts["wrong_symbol_count"],
        "timestamp_malformed_count": aggregate_counts["timestamp_malformed_count"],
        "timestamp_ms_mismatch_count": aggregate_counts["timestamp_ms_mismatch_count"],
        "timestamp_not_hourly_aligned_count": aggregate_counts["timestamp_not_hourly_aligned_count"],
        "unsorted_timestamp_count": aggregate_counts["unsorted_timestamp_count"],
        "duplicate_symbol_timestamp_count": aggregate_counts["duplicate_symbol_timestamp_count"],
        "rows_outside_window_count": aggregate_counts["rows_outside_window_count"],
        "invalid_interval_count": aggregate_counts["invalid_interval_count"],
        "required_field_missing_count": aggregate_counts["required_field_missing_count"],
        "invalid_numeric_count": aggregate_counts["invalid_numeric_count"],
        "mark_index_nonpositive_count": aggregate_counts["mark_index_nonpositive_count"],
    }

    aggregate_validation_review = {
        "reviewed_symbol_count": reviewed_symbol_count,
        "reviewed_total_rows": reviewed_total_rows,
        "reviewed_min_timestamp_utc": iso_from_ms(reviewed_min_ms),
        "reviewed_max_timestamp_utc": iso_from_ms(reviewed_max_ms),
        "duplicate_symbol_timestamp_count": aggregate_counts["duplicate_symbol_timestamp_count"],
        "rows_per_symbol_min": rows_per_symbol_min,
        "rows_per_symbol_max": rows_per_symbol_max,
        "symbols_with_zero_rows": len(symbols_with_zero_rows),
        "symbols_with_zero_rows_list": symbols_with_zero_rows,
        "required_field_missing_count": aggregate_counts["required_field_missing_count"],
        "invalid_numeric_count": aggregate_counts["invalid_numeric_count"],
        "mark_index_price_sanity_valid": mark_index_price_sanity_valid,
        "premium_numeric_sanity_valid": premium_numeric_sanity_valid,
        "row_files_sha256": row_files_sha256,
        "reviewed_index_sha256": reviewed_index_sha256,
    }

    premium_basis_sanity_review = {
        "review_only_not_strategy_signal": True,
        "global_min_premium_close": global_min_premium_close,
        "global_max_premium_close": global_max_premium_close,
        "global_min_mark_index_basis_close": global_min_basis_close,
        "global_max_mark_index_basis_close": global_max_basis_close,
        "extreme_abs_premium_close_gt_0_10_count": aggregate_counts[
            "extreme_abs_premium_close_gt_0_10_count"
        ],
        "extreme_abs_mark_index_basis_close_gt_0_10_count": aggregate_counts[
            "extreme_abs_mark_index_basis_close_gt_0_10_count"
        ],
        "p1_attention_reasons": sorted(set(p1_reasons)),
    }

    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "manifest_loaded": manifest_loaded,
        "manifest_status_verified": manifest_review["checks"]["status_verified"],
        "manifest_payload_hash_verified": manifest_review["checks"]["payload_hash_verified"],
        "external_index_loaded": external_index_loaded,
        "external_index_outside_repo": external_index_outside_repo,
        "row_files_count_verified_81": len(symbol_records) == EXPECTED_SYMBOL_COUNT,
        "all_row_files_exist": all_row_files_exist,
        "all_row_files_outside_repo": all_row_files_outside_repo,
        "reviewed_symbol_count_verified_81": reviewed_symbol_count == EXPECTED_SYMBOL_COUNT,
        "reviewed_total_rows_matches_manifest": reviewed_total_rows == EXPECTED_TOTAL_ROWS,
        "no_duplicate_symbol_timestamp": aggregate_counts["duplicate_symbol_timestamp_count"] == 0,
        "no_rows_outside_window": aggregate_counts["rows_outside_window_count"] == 0,
        "required_field_missing_count_zero": aggregate_counts["required_field_missing_count"] == 0,
        "invalid_numeric_count_zero": aggregate_counts["invalid_numeric_count"] == 0,
        "mark_index_price_sanity_valid": mark_index_price_sanity_valid,
        "premium_numeric_sanity_valid": premium_numeric_sanity_valid,
        "no_network_used": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": False,
        "exactly_one_json_review_artifact_created": False,
        "no_existing_files_modified": False,
        "replacement_checks_all_true": False,
    }

    status = REVIEW_STATUS if classification != FAIL_CLASSIFICATION else "FAIL_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_REVIEW_REQUIRES_REPAIR"

    artifact = {
        "status": status,
        "artifact_kind": "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_REVIEW",
        "module": MODULE_RELATIVE_PATH,
        "repo_scope": "repo_only_data_review_external_basis_premium_rows_no_network_no_strategy_no_candidates_no_edge_no_runtime_live_capital",
        "source_checkpoint": {
            "head": head,
            "expected_head": EXPECTED_HEAD,
            "head_verified": head == EXPECTED_HEAD,
            "repo_status_before_run": status_before,
            "repo_clean_before_run": repo_clean_before_run,
            "tracked_python_count_before_review_tool_tracking": tracked_python_count,
            "tracked_python_count_expected_before_review_tool_tracking": EXPECTED_TRACKED_PYTHON_COUNT,
        },
        "source_artifacts": {
            "data_pack_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_basis_premium_1h_data_pack_v1.py",
            "data_pack_manifest": MANIFEST_RELATIVE_PATH,
            "external_artifact_root": str(EXTERNAL_ROOT),
            "external_row_directory": str(EXTERNAL_ROW_DIR),
            "external_index": str(EXTERNAL_INDEX_PATH),
        },
        "manifest_review": manifest_review,
        "external_index_review": external_index_review,
        "row_file_review_summary": row_file_review_summary,
        "symbol_review_records": symbol_review_records,
        "aggregate_validation_review": aggregate_validation_review,
        "premium_basis_sanity_review": premium_basis_sanity_review,
        "basis_premium_data_validity_classification": classification,
        "limitations": [
            "This artifact is data review only.",
            "No strategy execution, backtest, return computation, candidate generation, or edge claim is performed.",
            "No runtime, live, or capital permission is granted.",
            "External basis/premium JSONL.GZ row files are read only for validation.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": None,
    }

    REVIEW_ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact["payload_sha256_excluding_hash"] = build_payload_hash(artifact)
    with REVIEW_ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2)
        handle.write("\n")

    status_after = run_git(["status", "--short", "--untracked-files=all"])
    validation_checks["exactly_one_python_tool_created"] = status_has_only_expected_new_files(
        [line for line in status_after if line[3:].strip().replace("\\", "/").endswith(".py")],
        {MODULE_RELATIVE_PATH},
    )
    validation_checks["exactly_one_json_review_artifact_created"] = status_has_only_expected_new_files(
        [line for line in status_after if line[3:].strip().replace("\\", "/").endswith(".json")],
        {REVIEW_ARTIFACT_RELATIVE_PATH},
    )
    validation_checks["no_existing_files_modified"] = status_has_only_expected_new_files(
        status_after, expected_post_run_paths
    )
    validation_checks["replacement_checks_all_true"] = (
        all(
            value is True
            for key, value in validation_checks.items()
            if key != "replacement_checks_all_true" and isinstance(value, bool)
        )
        and not p0_issues
    )
    artifact["validation_checks"] = validation_checks
    artifact["replacement_checks_all_true"] = validation_checks["replacement_checks_all_true"]
    artifact["payload_sha256_excluding_hash"] = None
    artifact["payload_sha256_excluding_hash"] = build_payload_hash(artifact)
    with REVIEW_ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2)
        handle.write("\n")

    stdout_items = {
        "status": status,
        "review_artifact_path": str(REVIEW_ARTIFACT_PATH),
        "basis_premium_data_validity_classification": classification,
        "reviewed_symbol_count": reviewed_symbol_count,
        "reviewed_total_rows": reviewed_total_rows,
        "reviewed_min_timestamp_utc": iso_from_ms(reviewed_min_ms),
        "reviewed_max_timestamp_utc": iso_from_ms(reviewed_max_ms),
        "duplicate_symbol_timestamp_count": aggregate_counts["duplicate_symbol_timestamp_count"],
        "required_field_missing_count": aggregate_counts["required_field_missing_count"],
        "invalid_numeric_count": aggregate_counts["invalid_numeric_count"],
        "mark_index_price_sanity_valid": str(mark_index_price_sanity_valid).lower(),
        "premium_numeric_sanity_valid": str(premium_numeric_sanity_valid).lower(),
        "global_min_premium_close": global_min_premium_close,
        "global_max_premium_close": global_max_premium_close,
        "global_min_mark_index_basis_close": global_min_basis_close,
        "global_max_mark_index_basis_close": global_max_basis_close,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "strategy_execution_allowed_now": "false",
        "candidate_generation": "false",
        "edge_claim": "false",
        "runtime_live_capital": "false",
        "replacement_checks_all_true": str(validation_checks["replacement_checks_all_true"]).lower(),
    }
    for key, value in stdout_items.items():
        print(f"{key}: {value}")

    if p0_issues:
        print("p0_issues:")
        for issue in sorted(set(p0_issues)):
            print(f"- {issue}")

    return 0 if validation_checks["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    sys.exit(main())
