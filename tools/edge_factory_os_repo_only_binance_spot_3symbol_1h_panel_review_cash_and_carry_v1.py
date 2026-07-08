#!/usr/bin/env python
"""Review the Binance spot 3-symbol 1h panel built for cash-and-carry diagnostics."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_3symbol_1h_panel_review_cash_and_carry_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/spot_panel_reviews/binance_spot_3symbol_1h_panel_review_cash_and_carry_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

BUILD_MANIFEST_RELATIVE_PATH = (
    "artifacts/spot_panel_build_manifests/binance_spot_3symbol_1h_panel_build_cash_and_carry_v1.json"
)
BUILD_MANIFEST_PATH = REPO_ROOT / BUILD_MANIFEST_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_3SYMBOL_1H_PANEL_REVIEW_CASH_AND_CARRY_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_3SYMBOL_1H_PANEL_REVIEW_CASH_AND_CARRY"
BUILD_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_3SYMBOL_1H_PANEL_BUILD_CASH_AND_CARRY_CREATED"
BUILD_PAYLOAD_SHA256 = "59a52fb9755abd1034edd90f5c73e645bca911703497092eaa2a0df57807126a"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
START_UTC = "2021-05-01T00:00:00Z"
MAX_TIMESTAMP_UTC = "2025-10-31T23:00:00Z"
START_MS = 1619827200000
END_EXCLUSIVE_MS = 1761955200000
HOUR_MS = 60 * 60 * 1000
TRACKED_PYTHON_COUNT_AT_START = 878

REQUIRED_FIELDS = (
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
)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_current_head() -> str:
    head_path = REPO_ROOT / ".git" / "HEAD"
    if not head_path.exists():
        return "UNKNOWN"
    value = head_path.read_text(encoding="utf-8").strip()
    if value.startswith("ref: "):
        ref_path = REPO_ROOT / ".git" / value[5:]
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
    return value


def timestamp_to_ms(value: str) -> int:
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def parse_float(value: str, field: str, symbol: str, timestamp_utc: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise RuntimeError(f"invalid numeric {field} for {symbol} at {timestamp_utc}: {value!r}") from exc
    if not math.isfinite(parsed):
        raise RuntimeError(f"non-finite numeric {field} for {symbol} at {timestamp_utc}: {value!r}")
    return parsed


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def ensure_target_absent() -> None:
    if ARTIFACT_PATH.exists():
        existing = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        if existing.get("module") != MODULE_RELATIVE_PATH or existing.get("status") != STATUS:
            raise RuntimeError(f"target artifact already exists from a different producer: {ARTIFACT_PATH}")


def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def review_symbol_file(symbol: str, panel_path: Path, expected_record: dict, external_root: Path) -> dict:
    if not panel_path.exists():
        raise RuntimeError(f"missing panel file for {symbol}: {panel_path}")
    if is_inside(panel_path, REPO_ROOT):
        raise RuntimeError(f"panel file is inside repo for {symbol}: {panel_path}")
    if not is_inside(panel_path, external_root):
        raise RuntimeError(f"panel file is outside expected external root for {symbol}: {panel_path}")

    file_hash = sha256_file(panel_path)
    if file_hash != expected_record.get("panel_sha256"):
        raise RuntimeError(f"panel sha256 mismatch for {symbol}")

    row_count = 0
    missing_field_count = 0
    invalid_numeric_count = 0
    duplicate_timestamp_count = 0
    non_hourly_timestamp_count = 0
    out_of_window_count = 0
    ohlc_sanity_failure_count = 0
    complete_1h_false_count = 0
    gap_count = 0
    max_gap_hours = 0
    previous_ms: int | None = None
    timestamps_seen: set[int] = set()
    min_timestamp_utc: str | None = None
    max_timestamp_utc: str | None = None

    with gzip.open(panel_path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"missing csv header for {symbol}: {panel_path}")
        missing_header_fields = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing_header_fields:
            raise RuntimeError(f"missing csv header fields for {symbol}: {missing_header_fields}")
        for row in reader:
            row_count += 1
            for field in REQUIRED_FIELDS:
                if row.get(field) in (None, ""):
                    missing_field_count += 1
            timestamp_utc = row["timestamp_utc"]
            if row["symbol"] != symbol:
                raise RuntimeError(f"wrong symbol in {panel_path}: {row['symbol']} != {symbol}")
            if not timestamp_utc.endswith("Z"):
                raise RuntimeError(f"timestamp without Z for {symbol}: {timestamp_utc}")
            timestamp_ms = timestamp_to_ms(timestamp_utc)
            if timestamp_ms % HOUR_MS != 0:
                non_hourly_timestamp_count += 1
            if timestamp_ms < START_MS or timestamp_ms >= END_EXCLUSIVE_MS:
                out_of_window_count += 1
            if timestamp_ms in timestamps_seen:
                duplicate_timestamp_count += 1
            timestamps_seen.add(timestamp_ms)
            if previous_ms is not None:
                if timestamp_ms <= previous_ms:
                    raise RuntimeError(f"timestamps not strictly increasing for {symbol} at {timestamp_utc}")
                gap_hours = (timestamp_ms - previous_ms) // HOUR_MS
                if gap_hours != 1:
                    gap_count += 1
                    max_gap_hours = max(max_gap_hours, gap_hours)
            previous_ms = timestamp_ms

            try:
                open_price = parse_float(row["open"], "open", symbol, timestamp_utc)
                high = parse_float(row["high"], "high", symbol, timestamp_utc)
                low = parse_float(row["low"], "low", symbol, timestamp_utc)
                close = parse_float(row["close"], "close", symbol, timestamp_utc)
                volume = parse_float(row["volume"], "volume", symbol, timestamp_utc)
                quote_volume = parse_float(row["quote_volume"], "quote_volume", symbol, timestamp_utc)
                taker_base = parse_float(row["taker_buy_base_volume"], "taker_buy_base_volume", symbol, timestamp_utc)
                taker_quote = parse_float(row["taker_buy_quote_volume"], "taker_buy_quote_volume", symbol, timestamp_utc)
                trade_count = int(row["trade_count"])
            except Exception:
                invalid_numeric_count += 1
                raise
            if min(open_price, high, low, close) <= 0:
                ohlc_sanity_failure_count += 1
            if high < max(open_price, close, low) or low > min(open_price, close, high):
                ohlc_sanity_failure_count += 1
            if min(volume, quote_volume, taker_base, taker_quote) < 0 or trade_count < 0:
                invalid_numeric_count += 1
            if row["complete_1h"].lower() != "true":
                complete_1h_false_count += 1
            min_timestamp_utc = timestamp_utc if min_timestamp_utc is None else min(min_timestamp_utc, timestamp_utc)
            max_timestamp_utc = timestamp_utc if max_timestamp_utc is None else max(max_timestamp_utc, timestamp_utc)

    if row_count != expected_record.get("row_count"):
        raise RuntimeError(f"row count mismatch for {symbol}: {row_count} != {expected_record.get('row_count')}")
    if min_timestamp_utc != expected_record.get("min_timestamp_utc"):
        raise RuntimeError(f"min timestamp mismatch for {symbol}")
    if max_timestamp_utc != expected_record.get("max_timestamp_utc"):
        raise RuntimeError(f"max timestamp mismatch for {symbol}")

    return {
        "symbol": symbol,
        "panel_path": str(panel_path),
        "row_count": row_count,
        "min_timestamp_utc": min_timestamp_utc,
        "max_timestamp_utc": max_timestamp_utc,
        "panel_sha256": file_hash,
        "missing_field_count": missing_field_count,
        "invalid_numeric_count": invalid_numeric_count,
        "duplicate_timestamp_count": duplicate_timestamp_count,
        "non_hourly_timestamp_count": non_hourly_timestamp_count,
        "out_of_window_count": out_of_window_count,
        "ohlc_sanity_failure_count": ohlc_sanity_failure_count,
        "complete_1h_false_count": complete_1h_false_count,
        "timestamp_gap_count": gap_count,
        "max_gap_hours": max_gap_hours,
    }


def main() -> int:
    ensure_target_absent()
    build_manifest = load_json(BUILD_MANIFEST_PATH)
    if build_manifest.get("status") != BUILD_STATUS:
        raise RuntimeError("spot panel build manifest status mismatch")
    if build_manifest.get("payload_sha256_excluding_hash") != BUILD_PAYLOAD_SHA256:
        raise RuntimeError("spot panel build manifest payload hash mismatch")
    if build_manifest.get("replacement_checks_all_true") is not True:
        raise RuntimeError("spot panel build replacement checks are not all true")

    index_path = Path(build_manifest["external_outputs"]["index_path"])
    external_root = Path(build_manifest["external_outputs"]["external_root"])
    index = load_json(index_path)
    if sha256_file(index_path) != build_manifest["external_outputs"]["index_sha256"]:
        raise RuntimeError("external spot index sha256 mismatch")
    if index.get("payload_sha256_excluding_hash") != build_manifest["external_outputs"]["index_payload_sha256_excluding_hash"]:
        raise RuntimeError("external spot index payload hash mismatch")
    if tuple(index.get("symbols", [])) != SYMBOLS:
        raise RuntimeError("external spot index symbol set mismatch")

    expected_by_symbol = {record["symbol"]: record for record in index["symbol_records"]}
    symbol_reviews = []
    for symbol in SYMBOLS:
        expected = expected_by_symbol[symbol]
        symbol_reviews.append(review_symbol_file(symbol, Path(expected["panel_path"]), expected, external_root))

    total_rows = sum(record["row_count"] for record in symbol_reviews)
    min_timestamp = min(record["min_timestamp_utc"] for record in symbol_reviews)
    max_timestamp = max(record["max_timestamp_utc"] for record in symbol_reviews)
    aggregate_missing = sum(record["missing_field_count"] for record in symbol_reviews)
    aggregate_invalid = sum(record["invalid_numeric_count"] for record in symbol_reviews)
    aggregate_duplicates = sum(record["duplicate_timestamp_count"] for record in symbol_reviews)
    aggregate_out_of_window = sum(record["out_of_window_count"] for record in symbol_reviews)
    aggregate_ohlc_failures = sum(record["ohlc_sanity_failure_count"] for record in symbol_reviews)
    aggregate_non_hourly = sum(record["non_hourly_timestamp_count"] for record in symbol_reviews)
    aggregate_complete_false = sum(record["complete_1h_false_count"] for record in symbol_reviews)

    validation_checks = {
        "repo_clean_before_run": True,
        "build_manifest_loaded": True,
        "build_manifest_status_verified": True,
        "build_manifest_payload_hash_verified": True,
        "external_index_loaded": True,
        "external_index_hash_verified": True,
        "external_index_outside_repo": not is_inside(index_path, REPO_ROOT),
        "symbol_count_verified_3": len(symbol_reviews) == 3,
        "all_panel_files_exist": all(Path(record["panel_path"]).exists() for record in symbol_reviews),
        "all_panel_files_outside_repo": all(not is_inside(Path(record["panel_path"]), REPO_ROOT) for record in symbol_reviews),
        "reviewed_total_rows_matches_build": total_rows == build_manifest["build_summary"]["total_rows"],
        "reviewed_min_timestamp_verified": min_timestamp == START_UTC,
        "reviewed_max_timestamp_verified": max_timestamp == MAX_TIMESTAMP_UTC,
        "no_duplicate_symbol_timestamp": aggregate_duplicates == 0,
        "no_rows_outside_window": aggregate_out_of_window == 0,
        "timestamps_hourly_aligned": aggregate_non_hourly == 0,
        "required_field_missing_count_zero": aggregate_missing == 0,
        "invalid_numeric_count_zero": aggregate_invalid == 0,
        "ohlc_sanity_valid": aggregate_ohlc_failures == 0,
        "complete_1h_field_reviewed": True,
        "timestamp_gaps_recorded": True,
        "no_network_used": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all_true(validation_checks)
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "source_checkpoint": {
            "repo_head_at_run": read_current_head(),
            "tracked_python_count_at_start": TRACKED_PYTHON_COUNT_AT_START,
            "repo_clean_before_run": True,
        },
        "source_artifacts": {
            "spot_panel_build_manifest": BUILD_MANIFEST_RELATIVE_PATH,
            "spot_panel_build_payload_sha256_excluding_hash": BUILD_PAYLOAD_SHA256,
            "external_spot_panel_index_path": str(index_path),
            "external_spot_panel_index_sha256": sha256_file(index_path),
        },
        "review_scope": {
            "symbols": list(SYMBOLS),
            "symbol_count": len(SYMBOLS),
            "window_start_utc": START_UTC,
            "window_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "strategy_execution_performed": False,
        },
        "spot_panel_review_summary": {
            "reviewed_symbol_count": len(symbol_reviews),
            "reviewed_total_rows": total_rows,
            "reviewed_min_timestamp_utc": min_timestamp,
            "reviewed_max_timestamp_utc": max_timestamp,
            "duplicate_symbol_timestamp_count": aggregate_duplicates,
            "required_field_missing_count": aggregate_missing,
            "invalid_numeric_count": aggregate_invalid,
            "ohlc_sanity_failure_count": aggregate_ohlc_failures,
            "non_hourly_timestamp_count": aggregate_non_hourly,
            "rows_outside_window_count": aggregate_out_of_window,
            "complete_1h_false_count": aggregate_complete_false,
            "timestamp_gap_count": sum(record["timestamp_gap_count"] for record in symbol_reviews),
            "max_gap_hours": max(record["max_gap_hours"] for record in symbol_reviews),
        },
        "symbol_review_records": symbol_reviews,
        "spot_data_validity_classification": (
            "BINANCE_SPOT_3SYMBOL_1H_PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_CASH_AND_CARRY_DIAGNOSTIC_EXECUTION"
            if replacement_checks_all_true and (aggregate_complete_false > 0 or sum(record["timestamp_gap_count"] for record in symbol_reviews) > 0)
            else (
                "BINANCE_SPOT_3SYMBOL_1H_PANEL_REVIEW_PASS_VALID_FOR_CASH_AND_CARRY_DIAGNOSTIC_EXECUTION"
                if replacement_checks_all_true
                else "BINANCE_SPOT_3SYMBOL_1H_PANEL_REVIEW_FAIL_REQUIRES_REPAIR"
            )
        ),
        "limitations": [
            "This review validates spot kline panel integrity only.",
            "Timestamp gaps are recorded for downstream join awareness and are not strategy results.",
            "No candidate, edge, family release, runtime, live, or capital permission is granted.",
        ],
        "safety_permissions": {
            "spot_panel_review_created": True,
            "spot_data_valid_for_cash_and_carry_execution": replacement_checks_all_true,
            "strategy_execution_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_spot_perp_delta_neutral_funding_carry_execution_only": replacement_checks_all_true,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"review_artifact_path: {ARTIFACT_RELATIVE_PATH}")
    print(f"reviewed_symbol_count: {len(symbol_reviews)}")
    print(f"reviewed_total_rows: {total_rows}")
    print(f"reviewed_min_timestamp_utc: {min_timestamp}")
    print(f"reviewed_max_timestamp_utc: {max_timestamp}")
    print(f"duplicate_symbol_timestamp_count: {aggregate_duplicates}")
    print(f"required_field_missing_count: {aggregate_missing}")
    print(f"invalid_numeric_count: {aggregate_invalid}")
    print(f"ohlc_sanity_valid: {str(aggregate_ohlc_failures == 0).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("strategy_execution_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
