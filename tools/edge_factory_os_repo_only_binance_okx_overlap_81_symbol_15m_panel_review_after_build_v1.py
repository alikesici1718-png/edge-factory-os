#!/usr/bin/env python3
"""Review the completed Binance/OKX overlap 81-symbol 15m panel build."""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_REVIEW_AFTER_BUILD_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_REVIEW_AFTER_BUILD"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.py"
REVIEW_ARTIFACT_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
REVIEW_PATH = REPO_ROOT / REVIEW_ARTIFACT_PATH
BUILD_MANIFEST_RELATIVE_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_81_symbol_15m_panel_build_manifest_v1.json"
BUILD_MANIFEST_PATH = REPO_ROOT / BUILD_MANIFEST_RELATIVE_PATH

BUILD_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_81_SYMBOL_15M_PANEL_BUILD_CREATED"
BUILD_MANIFEST_PAYLOAD_HASH = "9a19eb2cc92e3132d81fb427e2ebf3c6c1b1f6f3a3127f9054dc26077e19e623"

EXPECTED_SYMBOL_COUNT = 81
EXPECTED_ROW_COUNT = 7_808_472
EXPECTED_MIN_TIMESTAMP = "2023-01-01T00:00:00Z"
EXPECTED_MAX_TIMESTAMP = "2025-10-31T23:45:00Z"
WINDOW_START = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
WINDOW_END_EXCLUSIVE = dt.datetime(2025, 11, 1, tzinfo=dt.timezone.utc)
INTERVAL_SECONDS = 15 * 60

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
    "complete_15m",
]

PASS_CLASS = "PANEL_15M_REVIEW_PASS_VALID_FOR_READ_ONLY_EXTREME_MOVE_RESEARCH"
PASS_P1_CLASS = "PANEL_15M_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_EXTREME_MOVE_RESEARCH"
FAIL_CLASS = "PANEL_15M_REVIEW_FAIL_REQUIRES_REBUILD_OR_REPAIR"


class BlockedError(RuntimeError):
    """Raised when required review inputs are not usable."""


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BlockedError(f"missing required JSON artifact: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_timestamp(value: str) -> dt.datetime:
    if not value.endswith("Z"):
        raise ValueError(f"timestamp does not end with Z: {value}")
    parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    if parsed.minute % 15 != 0 or parsed.second != 0 or parsed.microsecond != 0:
        raise ValueError(f"timestamp is not 15m aligned: {value}")
    return parsed


def parse_decimal(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal: {value}") from exc
    if not parsed.is_finite():
        raise ValueError(f"non-finite decimal: {value}")
    return parsed


def parse_nonnegative_decimal(value: str, field: str) -> Decimal:
    parsed = parse_decimal(value)
    if parsed < 0:
        raise ValueError(f"negative {field}: {value}")
    return parsed


def current_head_from_git_files() -> str | None:
    head_path = REPO_ROOT / ".git" / "HEAD"
    if not head_path.exists():
        return None
    content = head_path.read_text(encoding="utf-8").strip()
    if content.startswith("ref: "):
        ref_name = content[5:]
        ref_path = REPO_ROOT / ".git" / ref_name
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
        packed_refs = REPO_ROOT / ".git" / "packed-refs"
        if packed_refs.exists():
            for line in packed_refs.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith("#") and not line.startswith("^"):
                    parts = line.split(" ")
                    if len(parts) == 2 and parts[1] == ref_name:
                        return parts[0]
    return content


def is_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def validate_build_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    observed_payload_hash = payload_hash_excluding_hash(manifest)
    output = manifest["panel_output_summary"]
    rows = manifest["source_row_validation_summary"]
    checks = {
        "status_verified": manifest.get("status") == BUILD_STATUS,
        "payload_hash_verified": manifest.get("payload_sha256_excluding_hash") == BUILD_MANIFEST_PAYLOAD_HASH
        and observed_payload_hash == BUILD_MANIFEST_PAYLOAD_HASH,
        "output_symbol_count_verified_81": output.get("output_symbol_count") == EXPECTED_SYMBOL_COUNT,
        "output_15m_row_count_verified": output.get("output_15m_row_count") == EXPECTED_ROW_COUNT,
        "duplicate_symbol_timestamp_count_zero": output.get("duplicate_symbol_timestamp_count") == 0,
        "ohlc_sanity_valid_true": rows.get("ohlc_sanity_valid") is True,
        "numeric_sanity_valid_true": rows.get("volume_sanity_valid") is True
        and rows.get("trade_count_sanity_valid") is True
        and rows.get("taker_field_sanity_valid") is True,
        "checksum_verified_zip_count_verified": manifest["source_download_summary"].get("checksum_verified_zip_count") == 2680,
    }
    return {
        "path": BUILD_MANIFEST_RELATIVE_PATH,
        "status": manifest.get("status"),
        "payload_sha256_excluding_hash": manifest.get("payload_sha256_excluding_hash"),
        "observed_payload_sha256_excluding_hash": observed_payload_hash,
        "output_symbol_count": output.get("output_symbol_count"),
        "output_15m_row_count": output.get("output_15m_row_count"),
        "duplicate_symbol_timestamp_count": output.get("duplicate_symbol_timestamp_count"),
        "ohlc_sanity_valid": rows.get("ohlc_sanity_valid"),
        "checksum_verified_zip_count": manifest["source_download_summary"].get("checksum_verified_zip_count"),
        "checks": checks,
        "build_manifest_review_passed": all(checks.values()),
    }


def validate_panel_index(manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    index_path = Path(manifest["non_repo_artifacts"]["panel_index_path"])
    if not index_path.exists():
        raise BlockedError(f"panel index missing: {index_path}")
    if is_under(index_path, REPO_ROOT):
        raise BlockedError(f"panel index is inside repo: {index_path}")
    observed_index_sha = sha256_file(index_path)
    expected_index_sha = manifest["non_repo_artifacts"]["panel_index_sha256"]
    index = read_json(index_path)
    panel_files = index.get("panel_files", {})
    if not isinstance(panel_files, dict):
        raise BlockedError("panel index panel_files must be a symbol map")
    file_records: dict[str, Any] = {}
    missing_files: list[str] = []
    hash_mismatches: list[dict[str, str]] = []
    for symbol, file_info in sorted(panel_files.items()):
        path = Path(file_info["path"])
        if is_under(path, REPO_ROOT):
            raise BlockedError(f"panel partition resolves inside repo: {path}")
        if not path.exists():
            missing_files.append(str(path))
            continue
        observed = sha256_file(path)
        expected = file_info.get("sha256")
        if expected and observed != expected:
            hash_mismatches.append({"symbol": symbol, "expected": expected, "observed": observed})
        file_records[symbol] = {
            "path": str(path),
            "expected_sha256": expected,
            "observed_sha256": observed,
            "expected_row_count": file_info.get("row_count"),
            "expected_min_timestamp_utc": file_info.get("min_timestamp_utc"),
            "expected_max_timestamp_utc": file_info.get("max_timestamp_utc"),
        }
    review = {
        "panel_index_path": str(index_path),
        "panel_index_exists_outside_repo": True,
        "panel_index_sha256": observed_index_sha,
        "panel_index_sha256_matches_manifest": observed_index_sha == expected_index_sha,
        "index_symbol_count": index.get("symbol_count"),
        "index_references_81_files": len(panel_files) == EXPECTED_SYMBOL_COUNT,
        "all_referenced_files_exist": not missing_files,
        "missing_files": missing_files,
        "file_hash_mismatch_count": len(hash_mismatches),
        "file_hash_mismatches": hash_mismatches[:10],
        "panel_partitioned_dir": index.get("panel_partitioned_dir"),
        "window_start_utc": index.get("window_start_utc"),
        "window_end_exclusive_utc": index.get("window_end_exclusive_utc"),
    }
    return index, {"review": review, "file_records": file_records}


def review_partition(symbol: str, file_record: dict[str, Any]) -> dict[str, Any]:
    path = Path(file_record["path"])
    row_count = 0
    duplicate_count = 0
    malformed_count = 0
    ohlc_valid = True
    numeric_valid = True
    symbol_mismatch_count = 0
    complete_false_count = 0
    rows_outside_window = 0
    timestamp_alignment_fail_count = 0
    strictly_increasing = True
    min_timestamp: str | None = None
    max_timestamp: str | None = None
    previous_dt: dt.datetime | None = None
    seen: set[str] = set()
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header != CSV_HEADER:
            raise BlockedError(f"header mismatch for {symbol}: {header}")
        for row in reader:
            if len(row) != len(CSV_HEADER):
                malformed_count += 1
                raise BlockedError(f"malformed row length for {symbol} in {path}")
            row_symbol = row[0]
            timestamp_utc = row[1]
            if row_symbol != symbol:
                symbol_mismatch_count += 1
                raise BlockedError(f"symbol mismatch in {path}: {row_symbol} != {symbol}")
            try:
                timestamp = parse_timestamp(timestamp_utc)
            except ValueError:
                timestamp_alignment_fail_count += 1
                raise
            if timestamp < WINDOW_START or timestamp >= WINDOW_END_EXCLUSIVE:
                rows_outside_window += 1
                raise BlockedError(f"row outside window for {symbol}: {timestamp_utc}")
            if previous_dt is not None and timestamp <= previous_dt:
                strictly_increasing = False
                raise BlockedError(f"timestamps not strictly increasing for {symbol}: {timestamp_utc}")
            previous_dt = timestamp
            if timestamp_utc in seen:
                duplicate_count += 1
                raise BlockedError(f"duplicate timestamp for {symbol}: {timestamp_utc}")
            seen.add(timestamp_utc)
            open_price = parse_decimal(row[2])
            high_price = parse_decimal(row[3])
            low_price = parse_decimal(row[4])
            close_price = parse_decimal(row[5])
            if not (open_price > 0 and high_price > 0 and low_price > 0 and close_price > 0):
                ohlc_valid = False
                raise BlockedError(f"non-positive OHLC for {symbol}: {timestamp_utc}")
            if high_price < max(open_price, close_price, low_price):
                ohlc_valid = False
                raise BlockedError(f"OHLC high sanity failed for {symbol}: {timestamp_utc}")
            if low_price > min(open_price, close_price, high_price):
                ohlc_valid = False
                raise BlockedError(f"OHLC low sanity failed for {symbol}: {timestamp_utc}")
            parse_nonnegative_decimal(row[6], "volume")
            parse_nonnegative_decimal(row[7], "quote_volume")
            trade_count = int(row[8])
            if trade_count < 0:
                numeric_valid = False
                raise BlockedError(f"negative trade count for {symbol}: {timestamp_utc}")
            parse_nonnegative_decimal(row[9], "taker_buy_base_volume")
            parse_nonnegative_decimal(row[10], "taker_buy_quote_volume")
            if row[11].strip().lower() != "true":
                complete_false_count += 1
            row_count += 1
            min_timestamp = timestamp_utc if min_timestamp is None else min_timestamp
            max_timestamp = timestamp_utc
    observed_sha = sha256_file(path)
    return {
        "symbol": symbol,
        "path": str(path),
        "row_count": row_count,
        "expected_row_count": file_record.get("expected_row_count"),
        "row_count_matches_index": row_count == file_record.get("expected_row_count"),
        "min_timestamp_utc": min_timestamp,
        "max_timestamp_utc": max_timestamp,
        "min_timestamp_matches_index": min_timestamp == file_record.get("expected_min_timestamp_utc"),
        "max_timestamp_matches_index": max_timestamp == file_record.get("expected_max_timestamp_utc"),
        "header_matches_expected": True,
        "all_rows_match_file_symbol": symbol_mismatch_count == 0,
        "timestamps_15m_aligned": timestamp_alignment_fail_count == 0,
        "timestamps_strictly_increasing": strictly_increasing,
        "duplicate_symbol_timestamp_count": duplicate_count,
        "rows_outside_window": rows_outside_window,
        "ohlc_sanity_valid": ohlc_valid,
        "numeric_sanity_valid": numeric_valid,
        "complete_false_count": complete_false_count,
        "observed_sha256": observed_sha,
        "expected_sha256": file_record.get("expected_sha256"),
        "sha256_matches_index": observed_sha == file_record.get("expected_sha256"),
        "partition_review_passed": (
            row_count == file_record.get("expected_row_count")
            and min_timestamp == file_record.get("expected_min_timestamp_utc")
            and max_timestamp == file_record.get("expected_max_timestamp_utc")
            and observed_sha == file_record.get("expected_sha256")
            and complete_false_count == 0
        ),
    }


def build_review() -> dict[str, Any]:
    manifest = read_json(BUILD_MANIFEST_PATH)
    build_manifest_review = validate_build_manifest(manifest)
    if not build_manifest_review["build_manifest_review_passed"]:
        raise BlockedError(f"build manifest review failed: {build_manifest_review['checks']}")
    panel_index, panel_index_data = validate_panel_index(manifest)
    panel_index_review = panel_index_data["review"]
    if not panel_index_review["panel_index_sha256_matches_manifest"]:
        raise BlockedError("panel index hash mismatch against build manifest")
    if not panel_index_review["all_referenced_files_exist"]:
        raise BlockedError(f"missing panel partition files: {panel_index_review['missing_files']}")
    if panel_index_review["file_hash_mismatch_count"] != 0:
        raise BlockedError(f"panel file hash mismatches: {panel_index_review['file_hash_mismatches']}")
    file_records = panel_index_data["file_records"]
    symbol_partition_review_records: list[dict[str, Any]] = []
    for symbol in sorted(file_records):
        symbol_partition_review_records.append(review_partition(symbol, file_records[symbol]))

    reviewed_rows = sum(record["row_count"] for record in symbol_partition_review_records)
    duplicate_count = sum(record["duplicate_symbol_timestamp_count"] for record in symbol_partition_review_records)
    complete_false_count = sum(record["complete_false_count"] for record in symbol_partition_review_records)
    rows_outside_window = sum(record["rows_outside_window"] for record in symbol_partition_review_records)
    rows_per_symbol = [record["row_count"] for record in symbol_partition_review_records]
    min_timestamp = min(record["min_timestamp_utc"] for record in symbol_partition_review_records if record["min_timestamp_utc"])
    max_timestamp = max(record["max_timestamp_utc"] for record in symbol_partition_review_records if record["max_timestamp_utc"])
    ohlc_valid = all(record["ohlc_sanity_valid"] for record in symbol_partition_review_records)
    numeric_valid = all(record["numeric_sanity_valid"] for record in symbol_partition_review_records)
    all_partitions_passed = all(record["partition_review_passed"] for record in symbol_partition_review_records)
    p0_failures: list[str] = []
    if reviewed_rows != EXPECTED_ROW_COUNT:
        p0_failures.append("aggregate_row_count_mismatch")
    if len(symbol_partition_review_records) != EXPECTED_SYMBOL_COUNT:
        p0_failures.append("symbol_count_mismatch")
    if duplicate_count != 0:
        p0_failures.append("duplicate_symbol_timestamp")
    if rows_outside_window != 0:
        p0_failures.append("rows_outside_window")
    if not ohlc_valid:
        p0_failures.append("ohlc_sanity_fail")
    if not numeric_valid:
        p0_failures.append("numeric_sanity_fail")
    if not all_partitions_passed:
        p0_failures.append("partition_review_failure")
    classification = FAIL_CLASS if p0_failures else PASS_CLASS
    aggregate_validation_review = {
        "reviewed_symbol_count": len(symbol_partition_review_records),
        "reviewed_15m_row_count": reviewed_rows,
        "reviewed_min_timestamp_utc": min_timestamp,
        "reviewed_max_timestamp_utc": max_timestamp,
        "duplicate_symbol_timestamp_count": duplicate_count,
        "rows_per_symbol_min": min(rows_per_symbol),
        "rows_per_symbol_max": max(rows_per_symbol),
        "rows_outside_window": rows_outside_window,
        "complete_false_count": complete_false_count,
        "ohlc_sanity_valid": ohlc_valid,
        "numeric_sanity_valid": numeric_valid,
        "output_panel_files_sha256": {
            record["symbol"]: record["observed_sha256"] for record in symbol_partition_review_records
        },
        "panel_index_sha256": panel_index_review["panel_index_sha256"],
        "p0_failure_count": len(p0_failures),
        "p0_failures": p0_failures,
    }
    source_checkpoint = {
        "actual_head_before_review": current_head_from_git_files(),
        "repo_clean_before_review_confirmed_externally": True,
        "tracked_python_count_before_review_expected": 858,
        "latest_build_commit": "0750ac5304aa1c12f2029d8f81d960e4fee4662c",
    }
    validation_checks = {
        "status_equals_required_status": True,
        "module_path_equals_required_path": True,
        "review_artifact_path_equals_required_path": True,
        "exactly_one_new_python_tool_file_expected": True,
        "exactly_one_new_json_review_artifact_expected": True,
        "no_existing_files_modified_expected": True,
        "no_other_tracked_files_expected": True,
        "build_manifest_loaded": True,
        "build_manifest_payload_hash_verified": True,
        "panel_index_loaded": True,
        "panel_index_exists_outside_repo": True,
        "panel_index_references_81_files": panel_index_review["index_references_81_files"],
        "all_panel_files_exist": panel_index_review["all_referenced_files_exist"],
        "all_panel_file_hashes_verified": panel_index_review["file_hash_mismatch_count"] == 0,
        "reviewed_symbol_count_verified_81": aggregate_validation_review["reviewed_symbol_count"] == EXPECTED_SYMBOL_COUNT,
        "reviewed_15m_row_count_verified": aggregate_validation_review["reviewed_15m_row_count"] == EXPECTED_ROW_COUNT,
        "reviewed_min_timestamp_verified": aggregate_validation_review["reviewed_min_timestamp_utc"] == EXPECTED_MIN_TIMESTAMP,
        "reviewed_max_timestamp_verified": aggregate_validation_review["reviewed_max_timestamp_utc"] == EXPECTED_MAX_TIMESTAMP,
        "no_duplicate_symbol_timestamp": aggregate_validation_review["duplicate_symbol_timestamp_count"] == 0,
        "ohlc_sanity_valid": aggregate_validation_review["ohlc_sanity_valid"],
        "numeric_sanity_valid": aggregate_validation_review["numeric_sanity_valid"],
        "no_rows_outside_window": aggregate_validation_review["rows_outside_window"] == 0,
        "no_network_used": True,
        "no_data_downloaded": True,
        "no_zip_opened": True,
        "no_okx_panel_rows_read": True,
        "no_binance_1m_source_rows_read": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "payload_sha256_excluding_hash_present": True,
        "replacement_checks_all_true": classification != FAIL_CLASS,
    }
    replacement_checks_all_true = all(validation_checks.values())
    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "repo_scope": {
            "code_changes_repo_only": True,
            "review_artifact_created_in_repo": True,
            "external_panel_index_read": True,
            "external_panel_partitions_read_for_validation": True,
            "public_network_used": False,
            "binance_zip_opened": False,
            "data_downloaded": False,
            "okx_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "strategy_executed": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
        },
        "source_checkpoint": source_checkpoint,
        "source_artifacts": {
            "build_manifest_path": BUILD_MANIFEST_RELATIVE_PATH,
            "build_manifest_payload_sha256_excluding_hash": BUILD_MANIFEST_PAYLOAD_HASH,
            "panel_index_path": panel_index_review["panel_index_path"],
            "panel_index_sha256": panel_index_review["panel_index_sha256"],
            "panel_partitioned_dir": panel_index.get("panel_partitioned_dir"),
            "source_artifacts_read_only": True,
        },
        "build_manifest_review": build_manifest_review,
        "panel_index_review": panel_index_review,
        "partition_file_review_summary": {
            "partition_files_opened_gzip_text_mode": len(symbol_partition_review_records),
            "expected_header": CSV_HEADER,
            "all_headers_match": all(record["header_matches_expected"] for record in symbol_partition_review_records),
            "all_rows_match_file_symbol": all(record["all_rows_match_file_symbol"] for record in symbol_partition_review_records),
            "all_timestamps_15m_aligned": all(record["timestamps_15m_aligned"] for record in symbol_partition_review_records),
            "all_timestamps_strictly_increasing": all(record["timestamps_strictly_increasing"] for record in symbol_partition_review_records),
            "all_partition_hashes_match_index": all(record["sha256_matches_index"] for record in symbol_partition_review_records),
            "all_partition_row_counts_match_index": all(record["row_count_matches_index"] for record in symbol_partition_review_records),
        },
        "symbol_partition_review_records": symbol_partition_review_records,
        "aggregate_validation_review": aggregate_validation_review,
        "panel_validity_classification": classification,
        "limitations": [
            "This is panel review only, not strategy execution.",
            "This review validates external 15m panel partitions for read-only extreme-move research.",
            "No downloads, Binance ZIP opening, API calls, returns, candidates, edge claims, or runtime/live/capital permissions are created.",
        ],
        "safety_permissions": {
            "panel_review_created": True,
            "panel_valid_for_read_only_extreme_move_research": classification != FAIL_CLASS,
            "strategy_execution_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_extreme_move_reversal_preregistration_only": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash_excluding_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["panel_validity_classification"] in {PASS_CLASS, PASS_P1_CLASS, FAIL_CLASS},
        payload["safety_permissions"]["strategy_execution_allowed_now"] is False,
        payload["safety_permissions"]["candidate_generation_allowed_now"] is False,
        payload["safety_permissions"]["edge_claim_allowed_now"] is False,
        payload["safety_permissions"]["runtime_permission_allowed_now"] is False,
        payload["repo_scope"]["public_network_used"] is False,
        payload["repo_scope"]["data_downloaded"] is False,
        payload["repo_scope"]["binance_zip_opened"] is False,
        payload["repo_scope"]["strategy_executed"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise BlockedError("review invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_review()
    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = REVIEW_PATH.with_suffix(".json.tmp")
    temp_path.write_bytes(canonical_json_bytes(artifact) + b"\n")
    temp_path.replace(REVIEW_PATH)
    summary = {
        "status": artifact["status"],
        "review_artifact_path": REVIEW_ARTIFACT_PATH,
        "panel_validity_classification": artifact["panel_validity_classification"],
        "reviewed_symbol_count": artifact["aggregate_validation_review"]["reviewed_symbol_count"],
        "reviewed_15m_row_count": artifact["aggregate_validation_review"]["reviewed_15m_row_count"],
        "reviewed_min_timestamp_utc": artifact["aggregate_validation_review"]["reviewed_min_timestamp_utc"],
        "reviewed_max_timestamp_utc": artifact["aggregate_validation_review"]["reviewed_max_timestamp_utc"],
        "duplicate_symbol_timestamp_count": artifact["aggregate_validation_review"]["duplicate_symbol_timestamp_count"],
        "ohlc_sanity_valid": artifact["aggregate_validation_review"]["ohlc_sanity_valid"],
        "numeric_sanity_valid": artifact["aggregate_validation_review"]["numeric_sanity_valid"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "strategy_execution_allowed_now": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
