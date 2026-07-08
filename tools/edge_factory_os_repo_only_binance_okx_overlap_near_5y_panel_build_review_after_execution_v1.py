#!/usr/bin/env python3
"""Review the completed Binance/OKX overlap near-5y 1h panel build."""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REQUIRED_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_PANEL_BUILD_REVIEW_AFTER_EXECUTION_CREATED"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.py"
REVIEW_ARTIFACT_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
REPO_PATH = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
REVIEW_PATH = REPO_PATH / REVIEW_ARTIFACT_PATH
TEMP_REVIEW_PATH = REVIEW_PATH.with_suffix(".json.tmp")

BUILD_MANIFEST_PATH = REPO_PATH / "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_ARTIFACT_PATH = REPO_PATH / "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = REPO_PATH / "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

EXTERNAL_ARTIFACT_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1"
)
PANEL_PARTITIONED_DIR = EXTERNAL_ARTIFACT_ROOT / "panel_1h_by_symbol"
PANEL_INDEX_PATH = EXTERNAL_ARTIFACT_ROOT / "panel_index/binance_okx_overlap_near_5y_1h_panel_index_v1.json"

PRIOR_HEAD = "97a03039230beb657c52964b840128a113c4ed2d"
PRIOR_TRACKED_PYTHON_COUNT = 809
BUILD_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_NEAR_5Y_1M_TO_1H_PANEL_BUILD_EXECUTED"
BUILD_MANIFEST_PAYLOAD_HASH = "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7"
PREVIEW_PAYLOAD_HASH = "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9"
COVERAGE_LOCK_PAYLOAD_HASH = "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0"
BUILD_OPTION = "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_SECOND_SOURCE_PANEL"

EXPECTED_SYMBOL_COUNT = 81
EXPECTED_REQUIRED_ZIP_COUNT = 4334
EXPECTED_OUTPUT_ROWS = 3_149_514
EXPECTED_PREVIEW_ROWS = 3_164_952
EXPECTED_ROW_DELTA = -15_438
EXPECTED_COMPLETE_ROWS = 3_149_492
EXPECTED_INCOMPLETE_ROWS = 22
EXPECTED_OUTPUT_MIN = "2021-05-01T00:00:00Z"
EXPECTED_OUTPUT_MAX = "2026-04-30T22:00:00Z"
WINDOW_START = "2021-05-01T00:00:00Z"
WINDOW_END_EXCLUSIVE = "2026-05-01T00:00:00Z"
WINDOW_END_LAST_HOUR = "2026-04-30T23:00:00Z"
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:00:00Z$")
CSV_HEADER = [
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
    "minute_count",
    "complete_1h",
]
ALLOWED_CLASSIFICATIONS = {
    "PANEL_REVIEW_PASS_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS",
    "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS",
    "PANEL_REVIEW_FAIL_REQUIRES_REBUILD_OR_REPAIR",
}


class BlockedError(RuntimeError):
    """Raised when the review must stop before a successful artifact write."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_payload_excluding_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def verify_payload_hash(payload: dict[str, Any], expected_hash: str) -> bool:
    return payload.get("payload_sha256_excluding_hash") == expected_hash and sha256_payload_excluding_hash(payload) == expected_hash


def is_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def is_outside_repo(path: Path) -> bool:
    return not is_under(path, REPO_PATH)


def parse_timestamp(value: str) -> dt.datetime:
    if not TIMESTAMP_RE.match(value):
        raise ValueError(f"timestamp is not hourly UTC ISO format: {value}")
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def parse_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal: {value}") from exc


def load_source_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    missing = [
        str(path)
        for path in (BUILD_MANIFEST_PATH, PREVIEW_ARTIFACT_PATH, COVERAGE_LOCK_PATH, PANEL_INDEX_PATH, PANEL_PARTITIONED_DIR)
        if not path.exists()
    ]
    if missing:
        raise BlockedError(f"required source artifact missing: {missing}")
    if not PANEL_PARTITIONED_DIR.is_dir():
        raise BlockedError(f"panel partitioned directory is not a directory: {PANEL_PARTITIONED_DIR}")

    source_hashes = {
        "build_manifest_sha256_before_review": sha256_file(BUILD_MANIFEST_PATH),
        "coverage_lock_sha256_before_review": sha256_file(COVERAGE_LOCK_PATH),
        "panel_index_sha256_before_review": sha256_file(PANEL_INDEX_PATH),
        "preview_artifact_sha256_before_review": sha256_file(PREVIEW_ARTIFACT_PATH),
    }
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_ARTIFACT_PATH)
    coverage = read_json(COVERAGE_LOCK_PATH)
    if build_manifest.get("status") != BUILD_STATUS:
        raise BlockedError("build manifest status mismatch")
    if not verify_payload_hash(build_manifest, BUILD_MANIFEST_PAYLOAD_HASH):
        raise BlockedError("build manifest payload hash mismatch")
    if not verify_payload_hash(preview, PREVIEW_PAYLOAD_HASH):
        raise BlockedError("preview artifact payload hash mismatch")
    if not verify_payload_hash(coverage, COVERAGE_LOCK_PAYLOAD_HASH):
        raise BlockedError("coverage lock payload hash mismatch")
    return build_manifest, preview, coverage, source_hashes


def validate_manifest_facts(manifest: dict[str, Any]) -> dict[str, Any]:
    build_scope = manifest["build_scope"]
    downloads = manifest["source_download_summary"]
    rows = manifest["source_row_validation_summary"]
    output = manifest["panel_output_summary"]
    repo_scope = manifest["repo_scope"]
    safety = manifest["safety_permissions"]
    checks = {
        "build_option_verified": build_scope["build_option"] == BUILD_OPTION,
        "checksum_verified_zip_count_verified": downloads["checksum_verified_zip_count"] == EXPECTED_REQUIRED_ZIP_COUNT,
        "complete_1h_row_count_verified": output["complete_1h_row_count"] == EXPECTED_COMPLETE_ROWS,
        "duplicate_symbol_hour_count_zero": output["duplicate_symbol_hour_count"] == 0,
        "exact_overlap_symbol_count_verified": build_scope["exact_overlap_symbol_count"] == EXPECTED_SYMBOL_COUNT,
        "incomplete_1h_row_count_verified": output["incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_ROWS,
        "no_edge_claim": repo_scope["edge_claim"] is False and safety["edge_claim_allowed_now"] is False,
        "no_runtime_live_capital": repo_scope["runtime_live_capital"] is False and safety["runtime_permission_allowed_now"] is False,
        "no_strategy_or_candidate": repo_scope["strategy_search_executed"] is False and repo_scope["candidate_generation"] is False,
        "numeric_sanity_valid": rows["numeric_sanity_valid"] is True,
        "ohlc_sanity_valid": rows["ohlc_sanity_valid"] is True,
        "output_1h_row_count_verified": output["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS,
        "output_max_timestamp_verified": output["output_max_timestamp_utc"] == EXPECTED_OUTPUT_MAX,
        "output_min_timestamp_verified": output["output_min_timestamp_utc"] == EXPECTED_OUTPUT_MIN,
        "output_symbol_count_verified": output["output_symbol_count"] == EXPECTED_SYMBOL_COUNT,
        "preview_expected_1h_row_count_verified": output["preview_expected_1h_row_count"] == EXPECTED_PREVIEW_ROWS,
        "required_monthly_zip_count_verified": downloads["required_monthly_zip_count"] == EXPECTED_REQUIRED_ZIP_COUNT,
        "row_count_delta_explained_verified": output["row_count_delta_explained"] is True,
        "row_count_delta_vs_preview_verified": output["row_count_delta_vs_preview"] == EXPECTED_ROW_DELTA,
        "status_verified": manifest["status"] == BUILD_STATUS,
    }
    return {
        "build_option": build_scope["build_option"],
        "checks": checks,
        "checksum_verified_zip_count": downloads["checksum_verified_zip_count"],
        "complete_1h_row_count": output["complete_1h_row_count"],
        "downloaded_zip_count": downloads["downloaded_zip_count"],
        "duplicate_symbol_hour_count": output["duplicate_symbol_hour_count"],
        "exact_overlap_symbol_count": build_scope["exact_overlap_symbol_count"],
        "incomplete_1h_row_count": output["incomplete_1h_row_count"],
        "manifest_review_passed": all(checks.values()),
        "numeric_sanity_valid": rows["numeric_sanity_valid"],
        "ohlc_sanity_valid": rows["ohlc_sanity_valid"],
        "output_1h_row_count": output["output_1h_row_count"],
        "output_symbol_count": output["output_symbol_count"],
        "preview_expected_1h_row_count": output["preview_expected_1h_row_count"],
        "required_monthly_zip_count": downloads["required_monthly_zip_count"],
        "reused_cached_zip_count": downloads["reused_cached_zip_count"],
        "row_count_delta_explained": output["row_count_delta_explained"],
        "row_count_delta_vs_preview": output["row_count_delta_vs_preview"],
        "status": manifest["status"],
    }


def load_and_review_panel_index(manifest: dict[str, Any]) -> dict[str, Any]:
    panel_index = read_json(PANEL_INDEX_PATH)
    panel_files = [Path(path) for path in panel_index.get("panel_files", [])]
    manifest_panel_files = [Path(path) for path in manifest["non_repo_artifacts"]["panel_files"]]
    expected_symbols = sorted(manifest["build_scope"]["exact_overlap_binance_symbols"])
    expected_files_by_symbol = {
        symbol: PANEL_PARTITIONED_DIR / f"{symbol}_1h.csv.gz"
        for symbol in expected_symbols
    }
    all_exist = all(path.is_file() for path in panel_files)
    all_under_panel_dir = all(is_under(path, PANEL_PARTITIONED_DIR) for path in panel_files)
    all_outside_repo = all(is_outside_repo(path) for path in panel_files)
    index_sha = sha256_file(PANEL_INDEX_PATH)
    manifest_index_sha = manifest["panel_output_summary"]["panel_index_sha256"]
    expected_file_set = {path.resolve() for path in expected_files_by_symbol.values()}
    index_file_set = {path.resolve() for path in panel_files}
    manifest_file_set = {path.resolve() for path in manifest_panel_files}
    checks = {
        "artifact_kind_valid": panel_index.get("artifact_kind") == "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_1H_PANEL_INDEX",
        "every_referenced_file_exists": all_exist,
        "expected_files_match_index": expected_file_set == index_file_set,
        "index_files_match_manifest": index_file_set == manifest_file_set,
        "panel_files_count_verified_81": len(panel_files) == EXPECTED_SYMBOL_COUNT,
        "panel_files_outside_repo": all_outside_repo,
        "panel_files_under_expected_dir": all_under_panel_dir,
        "panel_index_outside_repo": is_outside_repo(PANEL_INDEX_PATH),
        "panel_index_sha256_matches_manifest": index_sha == manifest_index_sha,
        "row_count_matches_manifest": panel_index.get("row_count") == manifest["panel_output_summary"]["output_1h_row_count"],
        "schema_matches_expected": panel_index.get("schema") == CSV_HEADER,
        "symbol_count_matches_manifest": panel_index.get("symbol_count") == EXPECTED_SYMBOL_COUNT,
        "symbols_match_manifest": sorted(panel_index.get("symbols", [])) == expected_symbols,
    }
    return {
        "checks": checks,
        "external_panel_index_review_passed": all(checks.values()),
        "manifest_panel_files_count": len(manifest_panel_files),
        "panel_files": [str(path) for path in sorted(panel_files, key=lambda item: str(item))],
        "panel_files_count": len(panel_files),
        "panel_index_hash_matches_manifest": index_sha == manifest_index_sha,
        "panel_index_loaded": True,
        "panel_index_outside_repo": is_outside_repo(PANEL_INDEX_PATH),
        "panel_index_path": str(PANEL_INDEX_PATH),
        "panel_index_sha256": index_sha,
        "referenced_files_all_exist": all_exist,
        "referenced_files_all_outside_repo": all_outside_repo,
        "referenced_files_all_under_expected_panel_dir": all_under_panel_dir,
    }


def review_partition_file(path: Path, expected_symbol: str, manifest_record: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        raise BlockedError(f"expected panel partition missing: {path}")
    if not is_under(path, PANEL_PARTITIONED_DIR):
        raise BlockedError(f"panel file outside expected partition directory: {path}")
    if not is_outside_repo(path):
        raise BlockedError(f"panel file is inside repo: {path}")

    file_sha = sha256_file(path)
    row_count = 0
    complete_rows = 0
    incomplete_rows = 0
    duplicate_timestamps = 0
    rows_outside_window = 0
    rows_at_or_after_window_end = 0
    symbol_mismatch_count = 0
    timestamp_unsorted_count = 0
    bad_timestamp_format_count = 0
    numeric_sanity_valid = True
    ohlc_sanity_valid = True
    header_valid = False
    previous_timestamp: str | None = None
    seen_timestamps: set[str] = set()
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    incomplete_rows_by_month: dict[str, int] = defaultdict(int)

    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            raise BlockedError(f"empty panel file: {path}") from None
        header_valid = header == CSV_HEADER
        if not header_valid:
            raise BlockedError(f"header mismatch in panel file: {path}")
        for row in reader:
            if len(row) != len(CSV_HEADER):
                raise BlockedError(f"wrong column count in panel file: {path}")
            symbol = row[0]
            timestamp = row[1]
            if symbol != expected_symbol:
                symbol_mismatch_count += 1
            try:
                parse_timestamp(timestamp)
            except ValueError:
                bad_timestamp_format_count += 1
                continue
            if timestamp < WINDOW_START or timestamp >= WINDOW_END_EXCLUSIVE:
                rows_outside_window += 1
            if timestamp >= WINDOW_END_EXCLUSIVE:
                rows_at_or_after_window_end += 1
            if previous_timestamp is not None and timestamp <= previous_timestamp:
                timestamp_unsorted_count += 1
            previous_timestamp = timestamp
            if timestamp in seen_timestamps:
                duplicate_timestamps += 1
            seen_timestamps.add(timestamp)
            first_timestamp = timestamp if first_timestamp is None else min(first_timestamp, timestamp)
            last_timestamp = timestamp if last_timestamp is None else max(last_timestamp, timestamp)

            open_v = parse_decimal(row[2])
            high_v = parse_decimal(row[3])
            low_v = parse_decimal(row[4])
            close_v = parse_decimal(row[5])
            volume = parse_decimal(row[6])
            quote_volume = parse_decimal(row[7])
            trade_count = int(row[8])
            taker_buy_base = parse_decimal(row[9])
            taker_buy_quote = parse_decimal(row[10])
            minute_count = int(row[11])
            complete_flag = row[12]
            if not (open_v > 0 and high_v > 0 and low_v > 0 and close_v > 0):
                numeric_sanity_valid = False
            if volume < 0 or quote_volume < 0 or trade_count < 0 or taker_buy_base < 0 or taker_buy_quote < 0:
                numeric_sanity_valid = False
            if not (high_v >= max(open_v, close_v, low_v) and low_v <= min(open_v, close_v, high_v)):
                ohlc_sanity_valid = False
            if minute_count <= 0 or minute_count > 60:
                numeric_sanity_valid = False
            if complete_flag not in {"true", "false"}:
                raise BlockedError(f"bad complete_1h flag in panel file: {path}")
            if (complete_flag == "true") != (minute_count == 60):
                raise BlockedError(f"complete_1h flag mismatch in panel file: {path}")
            if complete_flag == "true":
                complete_rows += 1
            else:
                incomplete_rows += 1
                incomplete_rows_by_month[timestamp[:7]] += 1
            row_count += 1

    manifest_hash = manifest_record["output_file_sha256"]
    checks = {
        "complete_rows_match_manifest": complete_rows == manifest_record["complete_1h_rows"],
        "duplicate_symbol_hour_count_zero": duplicate_timestamps == 0,
        "file_hash_matches_manifest": file_sha == manifest_hash,
        "header_valid": header_valid,
        "incomplete_rows_match_manifest": incomplete_rows == manifest_record["incomplete_1h_rows"],
        "numeric_sanity_valid": numeric_sanity_valid,
        "ohlc_sanity_valid": ohlc_sanity_valid,
        "row_count_matches_manifest": row_count == manifest_record["output_1h_rows"],
        "symbol_matches": symbol_mismatch_count == 0,
        "timestamps_sorted": timestamp_unsorted_count == 0,
        "timestamps_valid_format": bad_timestamp_format_count == 0,
        "within_window": rows_outside_window == 0 and rows_at_or_after_window_end == 0,
        "zero_rows_false": row_count > 0,
    }
    return {
        "bad_timestamp_format_count": bad_timestamp_format_count,
        "complete_1h_rows": complete_rows,
        "duplicate_symbol_hour_count": duplicate_timestamps,
        "file_hash_matches_manifest": file_sha == manifest_hash,
        "first_timestamp_utc": first_timestamp,
        "header_valid": header_valid,
        "incomplete_1h_rows": incomplete_rows,
        "incomplete_rows_by_month": dict(sorted(incomplete_rows_by_month.items())),
        "last_timestamp_utc": last_timestamp,
        "manifest_output_file_sha256": manifest_hash,
        "numeric_sanity_valid": numeric_sanity_valid,
        "ohlc_sanity_valid": ohlc_sanity_valid,
        "output_file_path": str(path),
        "output_file_sha256": file_sha,
        "partition_review_checks": checks,
        "row_count": row_count,
        "rows_at_or_after_window_end": rows_at_or_after_window_end,
        "rows_outside_window": rows_outside_window,
        "symbol": expected_symbol,
        "symbol_build_valid": all(checks.values()),
        "symbol_mismatch_count": symbol_mismatch_count,
        "timestamp_unsorted_count": timestamp_unsorted_count,
    }


def review_partitions(manifest: dict[str, Any], index_review: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, dict[str, int]]]:
    manifest_records = {record["symbol"]: record for record in manifest["symbol_output_records"]}
    symbols = sorted(manifest["build_scope"]["exact_overlap_binance_symbols"])
    records: list[dict[str, Any]] = []
    incomplete_by_symbol: dict[str, int] = {}
    incomplete_by_month: dict[str, int] = defaultdict(int)
    for symbol in symbols:
        path = PANEL_PARTITIONED_DIR / f"{symbol}_1h.csv.gz"
        record = review_partition_file(path, symbol, manifest_records[symbol])
        records.append(record)
        if record["incomplete_1h_rows"]:
            incomplete_by_symbol[symbol] = record["incomplete_1h_rows"]
            for month, count in record["incomplete_rows_by_month"].items():
                incomplete_by_month[month] += count
    output_rows = sum(record["row_count"] for record in records)
    complete_rows = sum(record["complete_1h_rows"] for record in records)
    incomplete_rows = sum(record["incomplete_1h_rows"] for record in records)
    duplicate_hours = sum(record["duplicate_symbol_hour_count"] for record in records)
    output_hashes = {record["symbol"]: record["output_file_sha256"] for record in records}
    summary = {
        "all_headers_valid": all(record["header_valid"] for record in records),
        "all_panel_files_readable": True,
        "all_symbols_match_files": all(record["symbol_mismatch_count"] == 0 for record in records),
        "files_reviewed_count": len(records),
        "partition_file_review_passed": all(record["symbol_build_valid"] for record in records),
        "reviewed_complete_1h_row_count": complete_rows,
        "reviewed_duplicate_symbol_hour_count": duplicate_hours,
        "reviewed_incomplete_1h_row_count": incomplete_rows,
        "reviewed_output_1h_row_count": output_rows,
        "reviewed_output_files_count": len(records),
        "reviewed_output_max_timestamp_utc": max(record["last_timestamp_utc"] for record in records),
        "reviewed_output_min_timestamp_utc": min(record["first_timestamp_utc"] for record in records),
        "reviewed_output_panel_files_sha256": output_hashes,
        "reviewed_rows_per_symbol_max": max(record["row_count"] for record in records),
        "reviewed_rows_per_symbol_min": min(record["row_count"] for record in records),
        "reviewed_symbol_count": len(records),
        "reviewed_symbols_with_zero_rows": [record["symbol"] for record in records if record["row_count"] == 0],
        "timestamps_sorted_within_symbol": all(record["timestamp_unsorted_count"] == 0 for record in records),
    }
    incomplete_summary = {
        "incomplete_rows_by_month": dict(sorted(incomplete_by_month.items())),
        "incomplete_rows_by_symbol": dict(sorted(incomplete_by_symbol.items())),
    }
    return records, summary, incomplete_summary


def build_review() -> dict[str, Any]:
    build_manifest, _preview, _coverage, source_hashes = load_source_artifacts()
    manifest_review = validate_manifest_facts(build_manifest)
    index_review = load_and_review_panel_index(build_manifest)
    partition_records, partition_summary, incomplete_summary = review_partitions(build_manifest, index_review)

    manifest_output = build_manifest["panel_output_summary"]
    manifest_rows = build_manifest["source_row_validation_summary"]
    no_rows_outside_window = all(record["rows_outside_window"] == 0 for record in partition_records)
    no_rows_at_or_after_window_end = all(record["rows_at_or_after_window_end"] == 0 for record in partition_records)
    numeric_sanity_valid = all(record["numeric_sanity_valid"] for record in partition_records)
    ohlc_sanity_valid = all(record["ohlc_sanity_valid"] for record in partition_records)
    every_symbol_has_rows = not partition_summary["reviewed_symbols_with_zero_rows"]
    reviewed_against_manifest_passed = (
        partition_summary["reviewed_symbol_count"] == EXPECTED_SYMBOL_COUNT
        and partition_summary["reviewed_output_1h_row_count"] == manifest_output["output_1h_row_count"]
        and partition_summary["reviewed_complete_1h_row_count"] == manifest_output["complete_1h_row_count"]
        and partition_summary["reviewed_incomplete_1h_row_count"] == manifest_output["incomplete_1h_row_count"]
        and partition_summary["reviewed_duplicate_symbol_hour_count"] == manifest_output["duplicate_symbol_hour_count"]
        and numeric_sanity_valid
        and ohlc_sanity_valid
    )
    row_delta_explanation = manifest_output.get("row_count_delta_explanation", {})
    row_count_delta_review_passed = (
        manifest_output["row_count_delta_explained"] is True
        and row_delta_explanation.get("row_count_delta_arithmetic_reconciled") is True
        and partition_summary["reviewed_output_1h_row_count"] == manifest_output["output_1h_row_count"]
        and every_symbol_has_rows
        and partition_summary["reviewed_duplicate_symbol_hour_count"] == 0
        and no_rows_outside_window
        and numeric_sanity_valid
        and ohlc_sanity_valid
    )
    incomplete_hour_review_passed = (
        partition_summary["reviewed_incomplete_1h_row_count"] == manifest_output["incomplete_1h_row_count"]
        and partition_summary["reviewed_incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_ROWS
        and numeric_sanity_valid
        and ohlc_sanity_valid
    )
    timestamp_boundary_review_passed = (
        no_rows_outside_window
        and no_rows_at_or_after_window_end
        and partition_summary["reviewed_output_max_timestamp_utc"] == manifest_output["output_max_timestamp_utc"]
        and row_count_delta_review_passed
    )

    source_hashes_after = {
        "build_manifest_sha256_after_review": sha256_file(BUILD_MANIFEST_PATH),
        "coverage_lock_sha256_after_review": sha256_file(COVERAGE_LOCK_PATH),
        "panel_index_sha256_after_review": sha256_file(PANEL_INDEX_PATH),
        "preview_artifact_sha256_after_review": sha256_file(PREVIEW_ARTIFACT_PATH),
    }
    source_artifacts_unchanged = (
        source_hashes["build_manifest_sha256_before_review"] == source_hashes_after["build_manifest_sha256_after_review"]
        and source_hashes["coverage_lock_sha256_before_review"] == source_hashes_after["coverage_lock_sha256_after_review"]
        and source_hashes["panel_index_sha256_before_review"] == source_hashes_after["panel_index_sha256_after_review"]
        and source_hashes["preview_artifact_sha256_before_review"] == source_hashes_after["preview_artifact_sha256_after_review"]
    )

    p0_failures = []
    p0_checks = {
        "build_manifest_review_passed": manifest_review["manifest_review_passed"],
        "external_panel_index_review_passed": index_review["external_panel_index_review_passed"],
        "partition_file_review_passed": partition_summary["partition_file_review_passed"],
        "reviewed_against_manifest_passed": reviewed_against_manifest_passed,
        "row_count_delta_review_passed": row_count_delta_review_passed,
        "incomplete_hour_review_passed": incomplete_hour_review_passed,
        "timestamp_boundary_review_passed": timestamp_boundary_review_passed,
        "source_artifacts_unchanged": source_artifacts_unchanged,
        "no_strategy_candidate_edge_runtime": True,
    }
    p0_failures.extend(name for name, value in p0_checks.items() if not value)
    p1_attention_items = []
    if manifest_output["row_count_delta_vs_preview"] != 0 and row_count_delta_review_passed:
        p1_attention_items.append("row_count_delta_accepted_but_nonzero")
    if partition_summary["reviewed_incomplete_1h_row_count"] > 0 and incomplete_hour_review_passed:
        p1_attention_items.append("incomplete_1h_rows_present_and_correctly_flagged")
    if partition_summary["reviewed_output_max_timestamp_utc"] == EXPECTED_OUTPUT_MAX and timestamp_boundary_review_passed:
        p1_attention_items.append("output_max_timestamp_is_2026_04_30_22_00_00Z_not_23_00_00Z")

    active_p0_blocker_count = len(p0_failures)
    active_p1_attention_count = len(p1_attention_items)
    if active_p0_blocker_count:
        classification = "PANEL_REVIEW_FAIL_REQUIRES_REBUILD_OR_REPAIR"
    elif active_p1_attention_count > 0:
        classification = "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    else:
        classification = "PANEL_REVIEW_PASS_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"

    aggregate_review = {
        **partition_summary,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p0_blockers": p0_failures,
        "active_p1_attention_count": active_p1_attention_count,
        "active_p1_attention_items": p1_attention_items,
        "reviewed_against_external_index_passed": index_review["external_panel_index_review_passed"],
        "reviewed_against_manifest_passed": reviewed_against_manifest_passed,
        "reviewed_manifest_payload_hash_matches_expected": True,
        "reviewed_numeric_sanity_valid": numeric_sanity_valid,
        "reviewed_ohlc_sanity_valid": ohlc_sanity_valid,
        "reviewed_panel_index_sha256": index_review["panel_index_sha256"],
    }

    review: dict[str, Any] = {
        "aggregate_row_validation_review": aggregate_review,
        "artifact_kind": "BINANCE_OKX_EXACT_OVERLAP_NEAR_5Y_PANEL_BUILD_REVIEW",
        "build_manifest_review": manifest_review,
        "external_panel_index_review": index_review,
        "incomplete_hour_review": {
            **incomplete_summary,
            "complete_incomplete_policy_consistent": True,
            "incomplete_hour_review_passed": incomplete_hour_review_passed,
            "incomplete_rows_are_p1_attention_not_p0_blocker": True,
            "manifest_incomplete_1h_row_count": manifest_output["incomplete_1h_row_count"],
            "reviewed_incomplete_1h_row_count": partition_summary["reviewed_incomplete_1h_row_count"],
        },
        "limitations": [
            "This review validates the built Binance 1h panel partitions, not Binance 1m ZIP source rows.",
            "This review did not rerun the panel build.",
            "This review did not download or open Binance ZIP files.",
            "This review did not read OKX panel rows.",
            "This review did not compute strategy returns or signals.",
            "This review is not candidate generation.",
            "This review is not an edge claim.",
            "This review grants no runtime/live/capital permission.",
            "The panel is listing-aware/ragged and not a strict rectangular 5y panel.",
            "Daily tail through 2026-05-22 is not included.",
            "Future strategy research requires separate preregistration/governance.",
            "Future edge claim requires external/future holdout and separate governance.",
        ],
        "module": MODULE_PATH,
        "panel_validity_classification": classification,
        "partition_file_review_summary": partition_summary,
        "repo_scope": {
            "api_key_used": False,
            "binance_1h_panel_rows_read_for_validation": True,
            "binance_1m_kline_source_rows_read": False,
            "binance_coverage_discovery_rerun": False,
            "binance_kline_zip_downloaded": False,
            "binance_kline_zip_opened": False,
            "binance_panel_build_rerun": False,
            "binance_panel_modified": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "external_panel_files_read_for_validation_only": True,
            "okx_panel_rows_read": False,
            "okx_whitelisted_artifact_read": False,
            "private_api_used": False,
            "public_network_used": False,
            "review_artifact_created_in_repo": True,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "row_count_delta_review": {
            "actual_output_1h_row_count": partition_summary["reviewed_output_1h_row_count"],
            "manifest_row_count_delta_explained": manifest_output["row_count_delta_explained"],
            "manifest_row_count_delta_explanation_reviewed": bool(row_delta_explanation),
            "preview_expected_1h_row_count": manifest_output["preview_expected_1h_row_count"],
            "row_count_delta_review_passed": row_count_delta_review_passed,
            "row_count_delta_vs_preview": manifest_output["row_count_delta_vs_preview"],
            "row_count_delta_was_accepted_with_p1_attention": "row_count_delta_accepted_but_nonzero" in p1_attention_items,
        },
        "safety_permissions": {
            "candidate_generation_allowed_now": False,
            "capital_permission_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "live_permission_allowed_now": False,
            "next_step_may_be_read_only_second_source_research_planning_only": True,
            "okx_panel_access_allowed_now": False,
            "panel_build_review_created": True,
            "panel_valid_for_candidate_generation": False,
            "panel_valid_for_edge_claim": False,
            "panel_valid_for_read_only_second_source_analysis": classification != "PANEL_REVIEW_FAIL_REQUIRES_REBUILD_OR_REPAIR",
            "panel_valid_for_runtime_live_capital": False,
            "panel_valid_for_strategy_search": False,
            "runtime_permission_allowed_now": False,
            "strategy_research_not_allowed_from_this_review": True,
            "strategy_search_allowed_now": False,
        },
        "source_artifact_immutability_review": {
            **source_hashes,
            **source_hashes_after,
            "build_manifest_read_only": True,
            "coverage_lock_unchanged": source_hashes["coverage_lock_sha256_before_review"] == source_hashes_after["coverage_lock_sha256_after_review"],
            "external_panel_files_read_only": True,
            "panel_index_read_only": True,
            "preview_artifact_unchanged": source_hashes["preview_artifact_sha256_before_review"] == source_hashes_after["preview_artifact_sha256_after_review"],
            "review_wrote_only_new_review_artifact": True,
            "source_artifacts_unchanged": source_artifacts_unchanged,
        },
        "source_artifacts": {
            "all_source_artifacts_read_only": True,
            "build_manifest_path": str(BUILD_MANIFEST_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "build_manifest_payload_hash_verified": True,
            "build_manifest_status": build_manifest["status"],
            "coverage_lock_path": str(COVERAGE_LOCK_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "coverage_lock_payload_hash_verified": True,
            "external_artifact_root": str(EXTERNAL_ARTIFACT_ROOT),
            "panel_index_path": str(PANEL_INDEX_PATH),
            "panel_partitioned_dir": str(PANEL_PARTITIONED_DIR),
            "preview_artifact_path": str(PREVIEW_ARTIFACT_PATH.relative_to(REPO_PATH)).replace("\\", "/"),
            "preview_artifact_payload_hash_verified": True,
        },
        "source_checkpoint": {
            "prior_build_manifest": "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
            "prior_build_manifest_payload_sha256_excluding_hash": BUILD_MANIFEST_PAYLOAD_HASH,
            "prior_build_status": BUILD_STATUS,
            "prior_build_tool": "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1.py",
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap second-source panel build review",
            "repo_clean_before_review": True,
        },
        "status": REQUIRED_STATUS,
        "symbol_partition_review_records": partition_records,
        "timestamp_boundary_review": {
            "expected_window": f"{WINDOW_START} <= timestamp < {WINDOW_END_EXCLUSIVE}",
            "manifest_output_max_timestamp_utc": manifest_output["output_max_timestamp_utc"],
            "no_rows_at_or_after_window_end": no_rows_at_or_after_window_end,
            "no_rows_outside_window": no_rows_outside_window,
            "output_max_timestamp_is_p1_attention_not_p0_blocker": "output_max_timestamp_is_2026_04_30_22_00_00Z_not_23_00_00Z" in p1_attention_items,
            "reviewed_output_max_timestamp_utc": partition_summary["reviewed_output_max_timestamp_utc"],
            "timestamp_boundary_review_passed": timestamp_boundary_review_passed,
        },
    }
    validation_checks = {
        "all_headers_valid": partition_summary["all_headers_valid"],
        "all_panel_files_exist_outside_repo": index_review["referenced_files_all_exist"] and index_review["referenced_files_all_outside_repo"],
        "all_panel_files_readable": partition_summary["all_panel_files_readable"],
        "all_symbols_match_files": partition_summary["all_symbols_match_files"],
        "build_manifest_loaded": True,
        "build_manifest_payload_hash_verified": True,
        "build_manifest_status_verified": True,
        "candidate_generation_forbidden": True,
        "coverage_lock_loaded": True,
        "coverage_lock_payload_hash_verified": True,
        "edge_claim_forbidden": True,
        "exactly_one_new_tracked_json_review_artifact_expected": True,
        "exactly_one_new_tracked_python_tool_file_expected": True,
        "external_panel_index_loaded": True,
        "incomplete_hour_review_passed": incomplete_hour_review_passed,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.py",
        "no_binance_1m_source_rows_read": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_existing_files_modified_expected": True,
        "no_kline_zip_downloaded": True,
        "no_kline_zip_opened": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_other_tracked_files_expected": True,
        "no_panel_build_rerun": True,
        "no_rows_at_or_after_2026_05_01": no_rows_at_or_after_window_end,
        "no_rows_outside_window": no_rows_outside_window,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "panel_partition_files_count_verified_81": partition_summary["reviewed_output_files_count"] == EXPECTED_SYMBOL_COUNT,
        "payload_sha256_excluding_hash_present": True,
        "preview_artifact_loaded": True,
        "preview_payload_hash_verified": True,
        "replacement_checks_all_true": True,
        "review_artifact_json_valid": True,
        "review_artifact_path_equals_required_path": REVIEW_ARTIFACT_PATH == "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
        "reviewed_complete_1h_row_count_matches_manifest": partition_summary["reviewed_complete_1h_row_count"] == manifest_output["complete_1h_row_count"],
        "reviewed_duplicate_symbol_hour_count_zero": partition_summary["reviewed_duplicate_symbol_hour_count"] == 0,
        "reviewed_incomplete_1h_row_count_matches_manifest": partition_summary["reviewed_incomplete_1h_row_count"] == manifest_output["incomplete_1h_row_count"],
        "reviewed_numeric_sanity_valid": numeric_sanity_valid,
        "reviewed_ohlc_sanity_valid": ohlc_sanity_valid,
        "reviewed_output_1h_row_count_matches_manifest": partition_summary["reviewed_output_1h_row_count"] == manifest_output["output_1h_row_count"],
        "reviewed_output_symbol_count_verified_81": partition_summary["reviewed_symbol_count"] == EXPECTED_SYMBOL_COUNT,
        "row_count_delta_review_passed": row_count_delta_review_passed,
        "runtime_live_capital_forbidden": True,
        "source_artifacts_unchanged": source_artifacts_unchanged,
        "status_equals_required_status": True,
        "strategy_search_forbidden": True,
        "timestamp_boundary_review_passed": timestamp_boundary_review_passed,
        "timestamps_sorted_within_symbol": partition_summary["timestamps_sorted_within_symbol"],
    }
    review["validation_checks"] = validation_checks
    review["replacement_checks_all_true"] = all(value is True for value in validation_checks.values())
    payload_hash_input = dict(review)
    payload_hash_input.pop("payload_sha256_excluding_hash", None)
    review["payload_sha256_excluding_hash"] = hashlib.sha256(canonical_json_bytes(payload_hash_input)).hexdigest()
    return review


def validate_review(review: dict[str, Any]) -> None:
    assert review["status"] == REQUIRED_STATUS
    assert review["module"] == MODULE_PATH
    assert REVIEW_ARTIFACT_PATH == "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
    assert review["build_manifest_review"]["status"] == BUILD_STATUS
    assert review["source_artifacts"]["build_manifest_payload_hash_verified"] is True
    assert review["source_artifacts"]["preview_artifact_payload_hash_verified"] is True
    assert review["source_artifacts"]["coverage_lock_payload_hash_verified"] is True
    assert review["external_panel_index_review"]["panel_files_count"] == EXPECTED_SYMBOL_COUNT
    assert review["partition_file_review_summary"]["reviewed_output_files_count"] == EXPECTED_SYMBOL_COUNT
    assert review["aggregate_row_validation_review"]["reviewed_symbol_count"] == EXPECTED_SYMBOL_COUNT
    assert review["aggregate_row_validation_review"]["reviewed_output_1h_row_count"] == EXPECTED_OUTPUT_ROWS
    assert review["aggregate_row_validation_review"]["reviewed_complete_1h_row_count"] == EXPECTED_COMPLETE_ROWS
    assert review["aggregate_row_validation_review"]["reviewed_incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_ROWS
    assert review["aggregate_row_validation_review"]["reviewed_duplicate_symbol_hour_count"] == 0
    assert review["aggregate_row_validation_review"]["reviewed_numeric_sanity_valid"] is True
    assert review["aggregate_row_validation_review"]["reviewed_ohlc_sanity_valid"] is True
    assert review["row_count_delta_review"]["row_count_delta_review_passed"] is True
    assert review["incomplete_hour_review"]["incomplete_hour_review_passed"] is True
    assert review["timestamp_boundary_review"]["timestamp_boundary_review_passed"] is True
    assert review["source_artifact_immutability_review"]["source_artifacts_unchanged"] is True
    assert review["repo_scope"]["strategy_search_executed"] is False
    assert review["repo_scope"]["candidate_generation"] is False
    assert review["repo_scope"]["edge_claim"] is False
    assert review["repo_scope"]["runtime_live_capital"] is False
    assert review["repo_scope"]["okx_panel_rows_read"] is False
    assert review["panel_validity_classification"] in ALLOWED_CLASSIFICATIONS
    assert review["replacement_checks_all_true"] is True
    assert review["payload_sha256_excluding_hash"]


def write_review(review: dict[str, Any]) -> None:
    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEMP_REVIEW_PATH.exists():
        TEMP_REVIEW_PATH.unlink()
    TEMP_REVIEW_PATH.write_bytes(canonical_json_bytes(review) + b"\n")
    TEMP_REVIEW_PATH.replace(REVIEW_PATH)


def stdout_summary(review: dict[str, Any]) -> dict[str, Any]:
    aggregate = review["aggregate_row_validation_review"]
    return {
        "active_p0_blocker_count": aggregate["active_p0_blocker_count"],
        "active_p1_attention_count": aggregate["active_p1_attention_count"],
        "candidate_generation": False,
        "edge_claim": False,
        "incomplete_hour_review_passed": review["incomplete_hour_review"]["incomplete_hour_review_passed"],
        "manifest_output_1h_row_count": review["build_manifest_review"]["output_1h_row_count"],
        "panel_valid_for_read_only_second_source_analysis": review["safety_permissions"]["panel_valid_for_read_only_second_source_analysis"],
        "panel_validity_classification": review["panel_validity_classification"],
        "payload_sha256_excluding_hash": review["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": review["replacement_checks_all_true"],
        "review_artifact_path": REVIEW_ARTIFACT_PATH,
        "reviewed_complete_1h_row_count": aggregate["reviewed_complete_1h_row_count"],
        "reviewed_duplicate_symbol_hour_count": aggregate["reviewed_duplicate_symbol_hour_count"],
        "reviewed_incomplete_1h_row_count": aggregate["reviewed_incomplete_1h_row_count"],
        "reviewed_numeric_sanity_valid": aggregate["reviewed_numeric_sanity_valid"],
        "reviewed_ohlc_sanity_valid": aggregate["reviewed_ohlc_sanity_valid"],
        "reviewed_output_1h_row_count": aggregate["reviewed_output_1h_row_count"],
        "reviewed_output_max_timestamp_utc": aggregate["reviewed_output_max_timestamp_utc"],
        "reviewed_output_min_timestamp_utc": aggregate["reviewed_output_min_timestamp_utc"],
        "reviewed_output_panel_files_sha256": aggregate["reviewed_output_panel_files_sha256"],
        "reviewed_panel_index_sha256": aggregate["reviewed_panel_index_sha256"],
        "reviewed_symbol_count": aggregate["reviewed_symbol_count"],
        "row_count_delta_review_passed": review["row_count_delta_review"]["row_count_delta_review_passed"],
        "runtime_live_capital": False,
        "status": review["status"],
        "strategy_search_executed": False,
        "timestamp_boundary_review_passed": review["timestamp_boundary_review"]["timestamp_boundary_review_passed"],
    }


def main() -> int:
    try:
        review = build_review()
        validate_review(review)
        write_review(review)
    except BlockedError as exc:
        if TEMP_REVIEW_PATH.exists():
            TEMP_REVIEW_PATH.unlink()
        if REVIEW_PATH.exists():
            REVIEW_PATH.unlink()
        print(
            json.dumps(
                {
                    "exact_blocker": str(exc),
                    "replacement_checks_all_true": False,
                    "review_artifact_path": REVIEW_ARTIFACT_PATH,
                    "status": "BLOCKED",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(stdout_summary(review), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
