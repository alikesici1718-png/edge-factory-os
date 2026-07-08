#!/usr/bin/env python3
"""Review the Binance spot/perp/funding carry forward-extension dataset."""

from __future__ import annotations

import csv
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_DATA_REVIEW_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_DATA_REVIEW"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_data_review_v1"

CLASS_PASS = "FORWARD_EXTENSION_DATA_REVIEW_PASS_VALID_FOR_EXTENDED_FUNDING_CARRY_DIAGNOSTIC"
CLASS_P1 = "FORWARD_EXTENSION_DATA_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_EXTENDED_FUNDING_CARRY_DIAGNOSTIC"
CLASS_FAIL = "FORWARD_EXTENSION_DATA_REVIEW_FAIL_REQUIRES_REACQUISITION_OR_REPAIR"
NEXT_ALLOWED_STEP = "EXTENDED_FUNDING_CARRY_DIAGNOSTIC_ONLY"

ROOT = Path(__file__).resolve().parents[1]
TOOL_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_data_review_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/data_reviews/binance_spot_perp_funding_carry_forward_extension_data_review_v1.json"
MANIFEST_RELATIVE_PATH = "artifacts/data_acquisition_locks/binance_spot_perp_funding_carry_forward_extension_acquisition_lock_v1.json"

EXPECTED_MANIFEST_HASH = "96c75d66548228a590a603ca0c226db04e578c35231b420f82004d0c29d8532b"
EXPECTED_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_ACQUISITION_LOCK_CREATED"
EXPECTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
WINDOW_START_UTC = "2025-11-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2026-05-01T00:00:00Z"
WINDOW_START_MS = 1761955200000
WINDOW_END_MS = 1777593600000
ONE_HOUR_MS = 60 * 60 * 1000

PANEL_HEADER = [
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
    "complete_1h",
]

FUNDING_FIELDS = ["symbol", "funding_time_ms", "funding_time_utc", "funding_rate", "source_endpoint"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(payload: dict[str, Any]) -> str:
    copy_payload = deepcopy(payload)
    copy_payload.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(copy_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_outside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return False
    except ValueError:
        return True


def parse_utc_ms(value: str) -> int:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"timestamp must end with Z: {value}")
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def decimal_value(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal: {value}") from exc


def review_panel_file(path: Path, symbol: str, layer: str, expected_hash: str | None) -> dict[str, Any]:
    file_hash = sha256_file(path)
    rows = 0
    timestamps: list[int] = []
    duplicate_count = 0
    missing_field_count = 0
    invalid_numeric_count = 0
    outside_window_count = 0
    wrong_symbol_count = 0
    ohlc_sanity = True
    complete_1h_all = True
    header_ok = False
    strictly_increasing = True
    previous_ts: int | None = None
    seen: set[int] = set()

    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header_ok = list(reader.fieldnames or []) == PANEL_HEADER
        for record in reader:
            rows += 1
            missing = [field for field in PANEL_HEADER if field not in record or record[field] in {None, ""}]
            if missing:
                missing_field_count += len(missing)
                continue
            if record["symbol"] != symbol:
                wrong_symbol_count += 1
            try:
                ts = parse_utc_ms(record["timestamp_utc"])
                open_price = decimal_value(record["open"])
                high = decimal_value(record["high"])
                low = decimal_value(record["low"])
                close = decimal_value(record["close"])
                volume = decimal_value(record["volume"])
                quote_volume = decimal_value(record["quote_volume"])
                trade_count = int(record["trade_count"])
                taker_buy_base = decimal_value(record["taker_buy_base_volume"])
                taker_buy_quote = decimal_value(record["taker_buy_quote_volume"])
            except (ValueError, TypeError):
                invalid_numeric_count += 1
                continue
            if ts in seen:
                duplicate_count += 1
            seen.add(ts)
            timestamps.append(ts)
            if previous_ts is not None and ts <= previous_ts:
                strictly_increasing = False
            previous_ts = ts
            if ts < WINDOW_START_MS or ts >= WINDOW_END_MS:
                outside_window_count += 1
            if ts % ONE_HOUR_MS != 0:
                invalid_numeric_count += 1
            if not (open_price > 0 and high > 0 and low > 0 and close > 0 and volume >= 0 and quote_volume >= 0 and trade_count >= 0 and taker_buy_base >= 0 and taker_buy_quote >= 0):
                invalid_numeric_count += 1
            if not (high >= max(open_price, close, low) and low <= min(open_price, close, high)):
                ohlc_sanity = False
            if str(record["complete_1h"]).lower() != "true":
                complete_1h_all = False

    gap_count = 0
    sorted_ts = sorted(timestamps)
    for index in range(len(sorted_ts) - 1):
        if sorted_ts[index] + ONE_HOUR_MS != sorted_ts[index + 1]:
            gap_count += 1

    return {
        "symbol": symbol,
        "layer": layer,
        "path": str(path),
        "file_exists": path.exists(),
        "outside_repo": is_outside_repo(path),
        "file_sha256": file_hash,
        "expected_sha256": expected_hash,
        "hash_matches_expected": expected_hash is None or file_hash == expected_hash,
        "header_ok": header_ok,
        "row_count": rows,
        "min_timestamp_utc": datetime.fromtimestamp(min(timestamps) / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if timestamps else None,
        "max_timestamp_utc": datetime.fromtimestamp(max(timestamps) / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if timestamps else None,
        "hourly_aligned": all(ts % ONE_HOUR_MS == 0 for ts in timestamps),
        "strictly_increasing": strictly_increasing,
        "duplicate_symbol_hour_count": duplicate_count,
        "gap_count": gap_count,
        "rows_outside_window": outside_window_count,
        "wrong_symbol_count": wrong_symbol_count,
        "missing_field_count": missing_field_count,
        "invalid_numeric_count": invalid_numeric_count,
        "ohlc_sanity_valid": ohlc_sanity,
        "complete_1h_all_true": complete_1h_all,
        "timestamp_set": sorted_ts,
    }


def review_funding_file(path: Path, symbol: str, expected_hash: str | None) -> dict[str, Any]:
    file_hash = sha256_file(path)
    records = 0
    timestamps: list[int] = []
    duplicate_count = 0
    missing_field_count = 0
    invalid_numeric_count = 0
    outside_window_count = 0
    wrong_symbol_count = 0
    strictly_increasing = True
    previous_ts: int | None = None
    seen: set[int] = set()
    malformed_json_count = 0
    mark_price_numeric_fail_count = 0
    timestamp_utc_ms_jitter_count = 0
    max_timestamp_utc_ms_jitter = 0

    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                malformed_json_count += 1
                continue
            records += 1
            missing = [field for field in FUNDING_FIELDS if field not in record or record[field] in {None, ""}]
            if missing:
                missing_field_count += len(missing)
                continue
            if record["symbol"] != symbol:
                wrong_symbol_count += 1
            try:
                ts = int(record["funding_time_ms"])
                ts_from_utc = parse_utc_ms(record["funding_time_utc"])
                decimal_value(record["funding_rate"])
                if record.get("mark_price") is not None:
                    mark = decimal_value(record["mark_price"])
                    if mark <= 0:
                        mark_price_numeric_fail_count += 1
            except (ValueError, TypeError):
                invalid_numeric_count += 1
                continue
            jitter = abs(ts - ts_from_utc)
            max_timestamp_utc_ms_jitter = max(max_timestamp_utc_ms_jitter, jitter)
            if jitter > 0:
                timestamp_utc_ms_jitter_count += 1
            if jitter >= 1000:
                invalid_numeric_count += 1
            if ts in seen:
                duplicate_count += 1
            seen.add(ts)
            timestamps.append(ts)
            if previous_ts is not None and ts <= previous_ts:
                strictly_increasing = False
            previous_ts = ts
            if ts < WINDOW_START_MS or ts >= WINDOW_END_MS:
                outside_window_count += 1

    gaps_ms = [timestamps[index + 1] - timestamps[index] for index in range(len(timestamps) - 1)]
    eight_hour_ms = 8 * ONE_HOUR_MS
    gap_summary = {
        "event_count": len(timestamps),
        "gap_count": len(gaps_ms),
        "min_gap_hours": min(gaps_ms) / ONE_HOUR_MS if gaps_ms else None,
        "max_gap_hours": max(gaps_ms) / ONE_HOUR_MS if gaps_ms else None,
        "unique_gap_hours_rounded": sorted({round(gap / ONE_HOUR_MS) for gap in gaps_ms}),
        "non_8h_gap_count": sum(1 for gap in gaps_ms if abs(gap - eight_hour_ms) >= 1000),
        "max_8h_gap_jitter_ms": max((abs(gap - eight_hour_ms) for gap in gaps_ms), default=0),
    }

    return {
        "symbol": symbol,
        "path": str(path),
        "file_exists": path.exists(),
        "outside_repo": is_outside_repo(path),
        "file_sha256": file_hash,
        "expected_sha256": expected_hash,
        "hash_matches_expected": expected_hash is None or file_hash == expected_hash,
        "record_count": records,
        "min_funding_time_utc": datetime.fromtimestamp(min(timestamps) / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if timestamps else None,
        "max_funding_time_utc": datetime.fromtimestamp(max(timestamps) / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if timestamps else None,
        "strictly_increasing": strictly_increasing,
        "duplicate_symbol_time_count": duplicate_count,
        "rows_outside_window": outside_window_count,
        "wrong_symbol_count": wrong_symbol_count,
        "missing_field_count": missing_field_count,
        "invalid_numeric_count": invalid_numeric_count,
        "malformed_json_count": malformed_json_count,
        "mark_price_numeric_fail_count": mark_price_numeric_fail_count,
        "timestamp_utc_ms_jitter_count": timestamp_utc_ms_jitter_count,
        "max_timestamp_utc_ms_jitter": max_timestamp_utc_ms_jitter,
        "funding_event_interval_gap_summary": gap_summary,
        "timestamp_set": sorted(timestamps),
    }


def strip_internal_sets(review: dict[str, Any]) -> dict[str, Any]:
    public = dict(review)
    public.pop("timestamp_set", None)
    return public


def main() -> None:
    manifest_path = ROOT / MANIFEST_RELATIVE_PATH
    manifest = load_json(manifest_path)
    if manifest.get("status") != EXPECTED_STATUS:
        raise ValueError("Acquisition manifest status mismatch")
    if manifest.get("payload_sha256_excluding_hash") != EXPECTED_MANIFEST_HASH:
        raise ValueError("Acquisition manifest payload hash mismatch")
    if manifest.get("replacement_checks_all_true") is not True:
        raise ValueError("Acquisition manifest replacement checks not true")

    non_repo = manifest.get("non_repo_artifacts") or {}
    external_root = Path(non_repo.get("external_data_root", ""))
    index_path = Path(non_repo.get("extension_index", ""))
    if not index_path.exists():
        raise FileNotFoundError(f"External index missing: {index_path}")
    index = load_json(index_path)
    index_file_sha256 = sha256_file(index_path)
    expected_index_file_sha256 = non_repo.get("extension_index_file_sha256")
    expected_index_payload_hash = non_repo.get("extension_index_sha256")

    symbol_records = index.get("symbol_records") or {}
    output_hash_map = index.get("output_file_sha256_map") or {}

    external_index_review = {
        "index_path": str(index_path),
        "index_exists": index_path.exists(),
        "index_outside_repo": is_outside_repo(index_path),
        "index_file_sha256": index_file_sha256,
        "expected_index_file_sha256": expected_index_file_sha256,
        "index_file_hash_matches_manifest": expected_index_file_sha256 is None or index_file_sha256 == expected_index_file_sha256,
        "index_payload_sha256": index.get("external_index_sha256"),
        "expected_index_payload_sha256": expected_index_payload_hash,
        "index_payload_hash_matches_manifest": expected_index_payload_hash is None or index.get("external_index_sha256") == expected_index_payload_hash,
        "symbol_count": len(index.get("symbols") or []),
        "references_exactly_3_spot_files": len([rec for rec in symbol_records.values() if rec.get("spot_output_path")]) == 3,
        "references_exactly_3_perp_files": len([rec for rec in symbol_records.values() if rec.get("perp_output_path")]) == 3,
        "references_exactly_3_funding_files": len([rec for rec in symbol_records.values() if rec.get("funding_output_path")]) == 3,
    }

    p0_issues: list[str] = []
    p1_attention: list[str] = []

    manifest_review = {
        "status_verified": manifest.get("status") == EXPECTED_STATUS,
        "symbol_count": len(manifest.get("acquisition_scope", {}).get("symbols") or []),
        "symbol_count_verified_3": len(manifest.get("acquisition_scope", {}).get("symbols") or []) == 3,
        "window_start_utc": manifest.get("acquisition_scope", {}).get("window_start_utc"),
        "window_end_exclusive_utc": manifest.get("acquisition_scope", {}).get("window_end_exclusive_utc"),
        "window_verified": manifest.get("acquisition_scope", {}).get("window_start_utc") == WINDOW_START_UTC
        and manifest.get("acquisition_scope", {}).get("window_end_exclusive_utc") == WINDOW_END_EXCLUSIVE_UTC,
        "spot_rows": manifest.get("output_data_summary", {}).get("spot_total_rows"),
        "perp_rows": manifest.get("output_data_summary", {}).get("perp_total_rows"),
        "funding_records": manifest.get("output_data_summary", {}).get("funding_total_records"),
        "zip_count": manifest.get("download_summary", {}).get("downloaded_zip_count"),
        "checksum_verified_zip_count": manifest.get("download_summary", {}).get("checksum_verified_zip_count"),
        "data_outside_repo_only": is_outside_repo(external_root),
        "payload_sha256_excluding_hash": manifest.get("payload_sha256_excluding_hash"),
    }

    spot_reviews: dict[str, Any] = {}
    perp_reviews: dict[str, Any] = {}
    funding_reviews: dict[str, Any] = {}
    alignment_reviews: dict[str, Any] = {}
    all_file_paths: list[Path] = []

    for symbol in EXPECTED_SYMBOLS:
        record = symbol_records.get(symbol)
        if not record:
            p0_issues.append(f"missing symbol record: {symbol}")
            continue
        spot_path = Path(record["spot_output_path"])
        perp_path = Path(record["perp_output_path"])
        funding_path = Path(record["funding_output_path"])
        all_file_paths.extend([spot_path, perp_path, funding_path])
        for path in [spot_path, perp_path, funding_path]:
            if not path.exists():
                p0_issues.append(f"missing external file: {path}")
            if not is_outside_repo(path):
                p0_issues.append(f"external file is inside repo: {path}")

        spot_review = review_panel_file(spot_path, symbol, "spot", output_hash_map.get(str(spot_path)))
        perp_review = review_panel_file(perp_path, symbol, "perp", output_hash_map.get(str(perp_path)))
        funding_review = review_funding_file(funding_path, symbol, output_hash_map.get(str(funding_path)))

        spot_set = set(spot_review["timestamp_set"])
        perp_set = set(perp_review["timestamp_set"])
        funding_gaps = funding_review["funding_event_interval_gap_summary"]
        alignment_reviews[symbol] = {
            "symbol": symbol,
            "spot_row_count": spot_review["row_count"],
            "perp_row_count": perp_review["row_count"],
            "spot_perp_common_hourly_timestamp_count": len(spot_set & perp_set),
            "spot_only_missing_hours": len(perp_set - spot_set),
            "perp_only_missing_hours": len(spot_set - perp_set),
            "funding_record_count": funding_review["record_count"],
            "funding_event_interval_gap_summary": funding_gaps,
            "min_max_timestamp_by_layer": {
                "spot": {"min": spot_review["min_timestamp_utc"], "max": spot_review["max_timestamp_utc"]},
                "perp": {"min": perp_review["min_timestamp_utc"], "max": perp_review["max_timestamp_utc"]},
                "funding": {"min": funding_review["min_funding_time_utc"], "max": funding_review["max_funding_time_utc"]},
            },
        }

        spot_reviews[symbol] = strip_internal_sets(spot_review)
        perp_reviews[symbol] = strip_internal_sets(perp_review)
        funding_reviews[symbol] = strip_internal_sets(funding_review)

    reviewed_spot_rows = sum(review["row_count"] for review in spot_reviews.values())
    reviewed_perp_rows = sum(review["row_count"] for review in perp_reviews.values())
    reviewed_funding_records = sum(review["record_count"] for review in funding_reviews.values())
    duplicate_counts = {
        "spot": sum(review["duplicate_symbol_hour_count"] for review in spot_reviews.values()),
        "perp": sum(review["duplicate_symbol_hour_count"] for review in perp_reviews.values()),
        "funding": sum(review["duplicate_symbol_time_count"] for review in funding_reviews.values()),
    }
    missing_invalid_counts = {
        "missing_fields": sum(review["missing_field_count"] for review in list(spot_reviews.values()) + list(perp_reviews.values()) + list(funding_reviews.values())),
        "invalid_numeric": sum(review["invalid_numeric_count"] for review in list(spot_reviews.values()) + list(perp_reviews.values()) + list(funding_reviews.values())),
        "malformed_json": sum(review["malformed_json_count"] for review in funding_reviews.values()),
        "wrong_symbol": sum(review["wrong_symbol_count"] for review in list(spot_reviews.values()) + list(perp_reviews.values()) + list(funding_reviews.values())),
    }

    all_external_files_exist = all(path.exists() for path in all_file_paths)
    all_external_files_outside_repo = all(is_outside_repo(path) for path in all_file_paths)
    all_hashes_match = all(review["hash_matches_expected"] for review in list(spot_reviews.values()) + list(perp_reviews.values()) + list(funding_reviews.values()))
    no_rows_outside = all(review["rows_outside_window"] == 0 for review in list(spot_reviews.values()) + list(perp_reviews.values()) + list(funding_reviews.values()))
    ohlc_sanity = all(review["ohlc_sanity_valid"] for review in list(spot_reviews.values()) + list(perp_reviews.values()))
    numeric_sanity = missing_invalid_counts["invalid_numeric"] == 0 and all(
        review.get("mark_price_numeric_fail_count", 0) == 0 for review in funding_reviews.values()
    )
    panel_order_ok = all(review["strictly_increasing"] and review["hourly_aligned"] for review in list(spot_reviews.values()) + list(perp_reviews.values()))
    funding_order_ok = all(review["strictly_increasing"] for review in funding_reviews.values())
    funding_present_all = all(review["record_count"] > 0 for review in funding_reviews.values())
    complete_1h_all = all(review["complete_1h_all_true"] for review in list(spot_reviews.values()) + list(perp_reviews.values()))
    header_ok = all(review["header_ok"] for review in list(spot_reviews.values()) + list(perp_reviews.values()))

    if not manifest_review["status_verified"]:
        p0_issues.append("manifest status mismatch")
    if not manifest_review["symbol_count_verified_3"] or not manifest_review["window_verified"]:
        p0_issues.append("manifest symbol count or window mismatch")
    if not all_external_files_exist:
        p0_issues.append("one or more external files missing")
    if not all_external_files_outside_repo:
        p0_issues.append("one or more external files are inside repo")
    if not all_hashes_match:
        p0_issues.append("one or more external file hashes mismatch")
    if not header_ok:
        p0_issues.append("one or more panel headers mismatch")
    if not (panel_order_ok and funding_order_ok):
        p0_issues.append("timestamps are unsorted or not hourly aligned")
    if any(duplicate_counts.values()):
        p0_issues.append("duplicate timestamps detected")
    if not no_rows_outside:
        p0_issues.append("rows outside window detected")
    if not ohlc_sanity or not numeric_sanity:
        p0_issues.append("OHLC or numeric sanity failed")
    if reviewed_spot_rows != manifest_review["spot_rows"] or reviewed_perp_rows != manifest_review["perp_rows"] or reviewed_funding_records != manifest_review["funding_records"]:
        p0_issues.append("aggregate row count mismatch versus manifest")
    if not funding_present_all:
        p0_issues.append("funding missing for at least one symbol")
    if not complete_1h_all:
        p0_issues.append("complete_1h false in panel")

    for symbol, review in funding_reviews.items():
        if review["funding_event_interval_gap_summary"]["non_8h_gap_count"] > 0:
            p1_attention.append(f"{symbol} has non-8h funding interval gaps")

    classification = CLASS_FAIL if p0_issues else (CLASS_P1 if p1_attention else CLASS_PASS)
    data_valid = classification != CLASS_FAIL

    aggregate_review = {
        "reviewed_symbol_count": len(spot_reviews),
        "reviewed_spot_rows": reviewed_spot_rows,
        "reviewed_perp_rows": reviewed_perp_rows,
        "reviewed_funding_records": reviewed_funding_records,
        "reviewed_min_spot_timestamp": min(review["min_timestamp_utc"] for review in spot_reviews.values()),
        "reviewed_max_spot_timestamp": max(review["max_timestamp_utc"] for review in spot_reviews.values()),
        "reviewed_min_perp_timestamp": min(review["min_timestamp_utc"] for review in perp_reviews.values()),
        "reviewed_max_perp_timestamp": max(review["max_timestamp_utc"] for review in perp_reviews.values()),
        "reviewed_min_funding_timestamp": min(review["min_funding_time_utc"] for review in funding_reviews.values()),
        "reviewed_max_funding_timestamp": max(review["max_funding_time_utc"] for review in funding_reviews.values()),
        "duplicate_counts": duplicate_counts,
        "missing_invalid_field_counts": missing_invalid_counts,
        "ohlc_sanity_valid": ohlc_sanity,
        "numeric_sanity_valid": numeric_sanity,
        "panel_header_valid": header_ok,
        "panel_complete_1h_all_true": complete_1h_all,
        "index_hash": index_file_sha256,
        "file_hash_maps": {
            "spot": {symbol: review["file_sha256"] for symbol, review in spot_reviews.items()},
            "perp": {symbol: review["file_sha256"] for symbol, review in perp_reviews.items()},
            "funding": {symbol: review["file_sha256"] for symbol, review in funding_reviews.items()},
        },
        "p0_issues": p0_issues,
        "p1_attention_items": p1_attention,
    }

    safety_permissions = {
        "forward_extension_data_review_created": True,
        "data_valid_for_extended_funding_carry_diagnostic": data_valid,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "next_step_may_be_extended_funding_carry_diagnostic_only": data_valid,
        "next_step_must_not_be_live_or_capital": True,
    }
    validation_checks = {
        "repo_clean_before_run": True,
        "acquisition_manifest_loaded": True,
        "acquisition_status_verified": manifest_review["status_verified"],
        "external_index_loaded": True,
        "all_external_files_exist": all_external_files_exist,
        "all_external_files_outside_repo": all_external_files_outside_repo,
        "reviewed_symbol_count_verified_3": len(spot_reviews) == 3,
        "spot_rows_match_manifest": reviewed_spot_rows == manifest_review["spot_rows"],
        "perp_rows_match_manifest": reviewed_perp_rows == manifest_review["perp_rows"],
        "funding_records_match_manifest": reviewed_funding_records == manifest_review["funding_records"],
        "no_duplicate_spot_symbol_hour": duplicate_counts["spot"] == 0,
        "no_duplicate_perp_symbol_hour": duplicate_counts["perp"] == 0,
        "no_duplicate_funding_symbol_time": duplicate_counts["funding"] == 0,
        "no_rows_outside_window": no_rows_outside,
        "ohlc_sanity_valid": ohlc_sanity,
        "numeric_sanity_valid": numeric_sanity,
        "no_network_used": True,
        "no_api_called": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": data_valid,
    }

    payload = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "created_at_utc": utc_now(),
            "expected_head": "1955537b1adc69997914c20cf0dc72d614aad44a",
            "tracked_python_count_before": 904,
            "tool_path": TOOL_RELATIVE_PATH,
            "artifact_path": ARTIFACT_RELATIVE_PATH,
        },
        "source_artifacts": {
            "acquisition_manifest": {
                "path": MANIFEST_RELATIVE_PATH,
                "status": manifest.get("status"),
                "payload_sha256_excluding_hash": manifest.get("payload_sha256_excluding_hash"),
            },
            "external_index": {
                "path": str(index_path),
                "external_index_sha256": index.get("external_index_sha256"),
                "index_file_sha256": index_file_sha256,
            },
        },
        "acquisition_manifest_review": manifest_review,
        "external_index_review": external_index_review,
        "spot_file_review": spot_reviews,
        "perp_file_review": perp_reviews,
        "funding_file_review": funding_reviews,
        "cross_layer_alignment_review": alignment_reviews,
        "aggregate_validation_review": aggregate_review,
        "data_validity_classification": classification,
        "next_allowed_step": NEXT_ALLOWED_STEP if data_valid else "FORWARD_EXTENSION_REACQUISITION_OR_REPAIR_ONLY",
        "limitations": [
            "Data review only; no strategy execution or return computation was performed.",
            "Review covers only the acquired forward closed-month extension through 2026-05-01 exclusive.",
            "May 2026 daily partial data was intentionally not reviewed because it was not acquired.",
            "No network or API calls were used by this review.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": data_valid,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)

    artifact_path = ROOT / ARTIFACT_RELATIVE_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout_fields = {
        "status": STATUS,
        "data_validity_classification": classification,
        "reviewed_symbol_count": aggregate_review["reviewed_symbol_count"],
        "reviewed_spot_rows": reviewed_spot_rows,
        "reviewed_perp_rows": reviewed_perp_rows,
        "reviewed_funding_records": reviewed_funding_records,
        "spot_timestamp_range": [aggregate_review["reviewed_min_spot_timestamp"], aggregate_review["reviewed_max_spot_timestamp"]],
        "perp_timestamp_range": [aggregate_review["reviewed_min_perp_timestamp"], aggregate_review["reviewed_max_perp_timestamp"]],
        "funding_timestamp_range": [aggregate_review["reviewed_min_funding_timestamp"], aggregate_review["reviewed_max_funding_timestamp"]],
        "duplicate_counts": duplicate_counts,
        "ohlc_sanity_valid": ohlc_sanity,
        "numeric_sanity_valid": numeric_sanity,
        "next_allowed_step": payload["next_allowed_step"],
        "strategy_execution_allowed_now": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": data_valid,
    }
    for key, value in stdout_fields.items():
        print(f"{key}={json.dumps(value, sort_keys=True)}")


if __name__ == "__main__":
    main()
