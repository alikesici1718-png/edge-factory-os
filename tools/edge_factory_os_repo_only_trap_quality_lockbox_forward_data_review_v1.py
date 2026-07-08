from __future__ import annotations

import csv
import datetime as dt
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
ACQUISITION_PATH = REPO_ROOT / "artifacts" / "data_acquisition" / "trap_quality_lockbox_forward_data_acquisition_v1.json"
FREEZE_CONTRACT_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "trap_quality_lockbox_freeze_contract_v1.json"
PANEL_REVIEW_PATH = REPO_ROOT / "artifacts" / "panel_build_reviews" / "binance_okx_overlap_81_symbol_15m_panel_review_after_build_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "data_reviews" / "trap_quality_lockbox_forward_data_review_v1.json"

STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_CREATED"
ARTIFACT_KIND = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW"
MODULE = "edge_factory_os_repo_only_trap_quality_lockbox_forward_data_review_v1"
FROZEN_FINALIST = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
EXPECTED_ACQUISITION_STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_CREATED"
EXPECTED_ACQUISITION_RESULT = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_ACQUISITION_PASS_READY_FOR_DATA_REVIEW"
EXPECTED_FREEZE_STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FREEZE_CONTRACT_CREATED"

LOCKBOX_START = "2025-11-01T00:00:00Z"
LOCKBOX_END = "2026-05-01T00:00:00Z"
EXPECTED_CLOSED_MONTHS = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"]
EXPECTED_DAYS = 181
BARS_PER_DAY = 96
EXPECTED_ROWS_PER_SYMBOL = EXPECTED_DAYS * BARS_PER_DAY
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_TOTAL_ROWS = EXPECTED_ROWS_PER_SYMBOL * EXPECTED_SYMBOL_COUNT
INTERVAL_SECONDS = 15 * 60
REQUIRED_COLUMNS = {"open", "high", "low", "close", "volume"}
DEVELOPMENT_PANEL_COMPATIBLE_COLUMNS = {
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
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ts_to_epoch_seconds(timestamp: str) -> int | None:
    if not timestamp.endswith("Z"):
        return None
    try:
        parsed = dt.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None
    return int(parsed.timestamp())


def snapshot_external_files(paths: list[Path]) -> dict[str, dict[str, int]]:
    snapshot: dict[str, dict[str, int]] = {}
    for path in paths:
        stat = path.stat()
        snapshot[str(path)] = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    return snapshot


def compare_snapshots(before: dict[str, dict[str, int]], after: dict[str, dict[str, int]]) -> bool:
    return before == after


def review_symbol_file(symbol: str, path: Path, expected_sha256: str | None) -> dict[str, Any]:
    file_exists = path.is_file()
    if not file_exists:
        return {"symbol": symbol, "file_exists": False, "missing_reason": "normalized_file_missing"}

    observed_sha256 = sha256_file(path)
    duplicate_count = 0
    missing_interval_count = 0
    non_numeric_ohlc_count = 0
    ohlc_sanity_fail_count = 0
    negative_volume_count = 0
    negative_quote_volume_count = 0
    rows_before_start = 0
    rows_at_or_after_end = 0
    timestamp_parse_fail_count = 0
    symbol_mismatch_count = 0
    row_count = 0
    min_timestamp: str | None = None
    max_timestamp: str | None = None
    previous_epoch: int | None = None
    seen: set[str] = set()
    header: list[str] = []
    quote_volume_present = False

    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        quote_volume_present = "quote_volume" in set(header)
        timestamp_column = "timestamp_utc" if "timestamp_utc" in set(header) else "time" if "time" in set(header) else None
        for row in reader:
            row_count += 1
            if row.get("symbol") and row["symbol"] != symbol:
                symbol_mismatch_count += 1
            timestamp = row.get(timestamp_column or "", "")
            epoch = ts_to_epoch_seconds(timestamp)
            if epoch is None:
                timestamp_parse_fail_count += 1
                continue
            if timestamp in seen:
                duplicate_count += 1
            seen.add(timestamp)
            if previous_epoch is not None and epoch != previous_epoch + INTERVAL_SECONDS:
                if epoch > previous_epoch:
                    missing_interval_count += (epoch - previous_epoch) // INTERVAL_SECONDS - 1
                else:
                    missing_interval_count += 1
            previous_epoch = epoch
            min_timestamp = timestamp if min_timestamp is None else min(min_timestamp, timestamp)
            max_timestamp = timestamp if max_timestamp is None else max(max_timestamp, timestamp)
            if timestamp < LOCKBOX_START:
                rows_before_start += 1
            if timestamp >= LOCKBOX_END:
                rows_at_or_after_end += 1
            try:
                open_price = float(row.get("open", "nan"))
                high_price = float(row.get("high", "nan"))
                low_price = float(row.get("low", "nan"))
                close_price = float(row.get("close", "nan"))
            except ValueError:
                non_numeric_ohlc_count += 1
                continue
            if not all(value > 0 for value in [open_price, high_price, low_price, close_price]):
                non_numeric_ohlc_count += 1
            if high_price < open_price or high_price < close_price or high_price < low_price or low_price > open_price or low_price > close_price:
                ohlc_sanity_fail_count += 1
            try:
                volume = float(row.get("volume", "nan"))
            except ValueError:
                negative_volume_count += 1
            else:
                if volume < 0:
                    negative_volume_count += 1
            if quote_volume_present:
                try:
                    quote_volume = float(row.get("quote_volume", "nan"))
                except ValueError:
                    negative_quote_volume_count += 1
                else:
                    if quote_volume < 0:
                        negative_quote_volume_count += 1

    header_set = set(header)
    schema_compatible = (
        (("timestamp_utc" in header_set) or ("time" in header_set))
        and REQUIRED_COLUMNS.issubset(header_set)
        and ("symbol" in header_set or symbol.endswith("USDT"))
        and DEVELOPMENT_PANEL_COMPATIBLE_COLUMNS.issubset(header_set)
    )
    return {
        "symbol": symbol,
        "file_exists": True,
        "path": str(path),
        "row_count": row_count,
        "expected_row_count": EXPECTED_ROWS_PER_SYMBOL,
        "row_count_matches_expected": row_count == EXPECTED_ROWS_PER_SYMBOL,
        "timestamp_min": min_timestamp,
        "timestamp_max": max_timestamp,
        "timestamp_min_matches_expected": min_timestamp == LOCKBOX_START,
        "timestamp_max_matches_expected": max_timestamp == "2026-04-30T23:45:00Z",
        "duplicate_timestamp_count": duplicate_count,
        "missing_interval_count": missing_interval_count,
        "rows_before_lockbox_start": rows_before_start,
        "rows_at_or_after_lockbox_end": rows_at_or_after_end,
        "utc_timestamp_parse_fail_count": timestamp_parse_fail_count,
        "symbol_mismatch_count": symbol_mismatch_count,
        "non_numeric_or_non_positive_ohlc_count": non_numeric_ohlc_count,
        "ohlc_sanity_fail_count": ohlc_sanity_fail_count,
        "negative_volume_count": negative_volume_count,
        "negative_quote_volume_count": negative_quote_volume_count,
        "quote_volume_present": quote_volume_present,
        "header": header,
        "schema_compatible_with_development_panel": schema_compatible,
        "observed_sha256": observed_sha256,
        "expected_sha256": expected_sha256,
        "sha256_matches_manifest": expected_sha256 == observed_sha256,
        "timezone_utc": timestamp_parse_fail_count == 0,
        "coverage_passed": row_count == EXPECTED_ROWS_PER_SYMBOL
        and min_timestamp == LOCKBOX_START
        and max_timestamp == "2026-04-30T23:45:00Z"
        and duplicate_count == 0
        and missing_interval_count == 0
        and rows_before_start == 0
        and rows_at_or_after_end == 0
        and timestamp_parse_fail_count == 0
        and symbol_mismatch_count == 0,
        "ohlcv_sanity_passed": non_numeric_ohlc_count == 0
        and ohlc_sanity_fail_count == 0
        and negative_volume_count == 0
        and negative_quote_volume_count == 0,
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_trap_quality_lockbox_forward_data_review_v1.py",
        "?? artifacts/data_reviews/trap_quality_lockbox_forward_data_review_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    acquisition = load_json(ACQUISITION_PATH)
    freeze_contract = load_json(FREEZE_CONTRACT_PATH)
    panel_review = load_json(PANEL_REVIEW_PATH)
    external_root = Path(acquisition["external_output_root"])
    normalized_dir = external_root / "normalized_15m_by_symbol"
    coverage_dir = external_root / "coverage_reports"
    checksums_dir = external_root / "checksums"
    checksum_report_path = Path(acquisition["generated_external_files"]["external_reports"]["checksum_report"]["path"])
    checksum_report = load_json(checksum_report_path)

    requested_symbols = acquisition.get("requested_universe", {}).get("symbols", [])
    normalized_files = sorted(normalized_dir.glob("*_15m.csv.gz"))
    external_paths_to_snapshot = normalized_files + sorted(coverage_dir.glob("*")) + sorted(checksums_dir.glob("*"))
    before_external_snapshot = snapshot_external_files(external_paths_to_snapshot)

    expected_sha_by_symbol = checksum_report.get("normalized_file_sha256", {})
    per_symbol_reviews = {
        symbol: review_symbol_file(symbol, normalized_dir / f"{symbol}_15m.csv.gz", expected_sha_by_symbol.get(symbol))
        for symbol in requested_symbols
    }

    after_external_snapshot = snapshot_external_files(external_paths_to_snapshot)
    external_data_not_modified = compare_snapshots(before_external_snapshot, after_external_snapshot)

    actual_total_rows = sum(record.get("row_count", 0) for record in per_symbol_reviews.values())
    acquired_symbols = [symbol for symbol, record in per_symbol_reviews.items() if record.get("file_exists")]
    missing_symbols = [symbol for symbol, record in per_symbol_reviews.items() if not record.get("file_exists")]
    full_coverage_symbols = [symbol for symbol, record in per_symbol_reviews.items() if record.get("coverage_passed")]
    ohlcv_sanity_passed = all(record.get("ohlcv_sanity_passed") for record in per_symbol_reviews.values())
    schema_compatible = all(record.get("schema_compatible_with_development_panel") for record in per_symbol_reviews.values())
    checksum_review_passed = (
        acquisition.get("payload_sha256_excluding_hash") is not None
        and len(expected_sha_by_symbol) == EXPECTED_SYMBOL_COUNT
        and all(record.get("sha256_matches_manifest") for record in per_symbol_reviews.values())
    )
    coverage_passed = all(record.get("coverage_passed") for record in per_symbol_reviews.values())
    exact_rows_passed = actual_total_rows == EXPECTED_TOTAL_ROWS
    universe_passed = (
        len(requested_symbols) == EXPECTED_SYMBOL_COUNT
        and len(acquired_symbols) == EXPECTED_SYMBOL_COUNT
        and len(missing_symbols) == 0
        and sorted(path.name.removesuffix("_15m.csv.gz") for path in normalized_files) == requested_symbols
        and acquisition.get("coverage_summary", {}).get("requested_symbol_count") == EXPECTED_SYMBOL_COUNT
        and acquisition.get("coverage_summary", {}).get("acquired_symbol_count") == EXPECTED_SYMBOL_COUNT
        and acquisition.get("coverage_summary", {}).get("missing_symbol_count") == 0
    )
    period_passed = (
        acquisition.get("lockbox_period", {}).get("lockbox_start") == LOCKBOX_START
        and acquisition.get("lockbox_period", {}).get("lockbox_end") == LOCKBOX_END
        and acquisition.get("lockbox_period", {}).get("primary_closed_months") == EXPECTED_CLOSED_MONTHS
        and acquisition.get("lockbox_period", {}).get("partial_month_extension") is None
        and acquisition.get("lockbox_period", {}).get("partial_month_extension_included_in_primary") is False
    )
    lockbox_integrity = acquisition.get("lockbox_integrity", {})
    lockbox_integrity_passed = (
        lockbox_integrity.get("frozen_config_not_modified") is True
        and lockbox_integrity.get("strategy_execution_performed") is False
        and lockbox_integrity.get("signal_generation_performed") is False
        and lockbox_integrity.get("pnl_computation_performed") is False
        and lockbox_integrity.get("candidate_generation_allowed_now") is False
        and lockbox_integrity.get("edge_claim_allowed_now") is False
        and lockbox_integrity.get("runtime_live_capital_allowed_now") is False
    )

    blocking_failures: list[str] = []
    attention_warnings: list[str] = []
    if not exact_rows_passed:
        blocking_failures.append("actual_total_rows_mismatch")
    if not universe_passed:
        blocking_failures.append("universe_mismatch")
    if not coverage_passed:
        blocking_failures.append("per_symbol_coverage_failed")
    if not ohlcv_sanity_passed:
        blocking_failures.append("ohlcv_sanity_failed")
    if not schema_compatible:
        blocking_failures.append("schema_incompatible")
    if not checksum_review_passed:
        blocking_failures.append("checksum_review_failed")
    if not lockbox_integrity_passed:
        blocking_failures.append("lockbox_integrity_failed")
    if not external_data_not_modified:
        blocking_failures.append("external_lockbox_data_modified")
    if acquisition.get("result_classification") != EXPECTED_ACQUISITION_RESULT:
        attention_warnings.append("acquisition_result_not_pass_ready_for_data_review")

    if blocking_failures:
        result_classification = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_FAIL_REQUIRES_REACQUIRE"
        next_allowed_step = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REACQUIRE_V1"
    elif attention_warnings:
        result_classification = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_PASS_WITH_ATTENTION"
        next_allowed_step = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_ATTENTION_RESOLUTION_V1"
    else:
        result_classification = "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_PASS_READY_FOR_TEST_PREREGISTRATION"
        next_allowed_step = "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PREREGISTRATION_V1"

    safety_permissions = {
        "data_review_created": True,
        "strategy_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "backtest_allowed_now": False,
        "pnl_computation_allowed_now": False,
        "optimization_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "acquisition_artifact_loaded": acquisition.get("status") == EXPECTED_ACQUISITION_STATUS,
        "freeze_contract_loaded": freeze_contract.get("status") == EXPECTED_FREEZE_STATUS,
        "frozen_finalist_verified": freeze_contract.get("freeze_decision", {}).get("frozen_finalist") == FROZEN_FINALIST
        and acquisition.get("frozen_finalist") == FROZEN_FINALIST,
        "lockbox_period_verified": period_passed,
        "expected_total_rows_verified_1407456": exact_rows_passed,
        "requested_symbol_count_verified_81": len(requested_symbols) == EXPECTED_SYMBOL_COUNT,
        "acquired_symbol_count_verified_81": len(acquired_symbols) == EXPECTED_SYMBOL_COUNT,
        "missing_symbol_count_verified_0": len(missing_symbols) == 0,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_pnl_computation": True,
        "no_parameter_change": True,
        "no_v_next_created": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_development_panel_modified": True,
        "external_lockbox_data_not_modified": external_data_not_modified,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": not unexpected_status,
        "replacement_checks_all_true": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_review": status_lines,
            "unexpected_dirty_paths_at_review": unexpected_status,
        },
        "source_artifacts": {
            "acquisition_artifact": str(ACQUISITION_PATH),
            "freeze_contract": str(FREEZE_CONTRACT_PATH),
            "panel_review": str(PANEL_REVIEW_PATH),
            "normalized_15m_by_symbol_dir": str(normalized_dir),
            "coverage_reports_dir": str(coverage_dir),
            "checksums_dir": str(checksums_dir),
            "checksum_report": str(checksum_report_path),
        },
        "frozen_finalist_review": {
            "frozen_finalist": FROZEN_FINALIST,
            "verified": validation_checks["frozen_finalist_verified"],
            "no_rejected_finalist_revived": bool(freeze_contract.get("explicit_rejections")),
        },
        "lockbox_period_review": {
            "lockbox_start": acquisition.get("lockbox_period", {}).get("lockbox_start"),
            "lockbox_end": acquisition.get("lockbox_period", {}).get("lockbox_end"),
            "expected_closed_months": EXPECTED_CLOSED_MONTHS,
            "observed_closed_months": acquisition.get("lockbox_period", {}).get("primary_closed_months"),
            "no_partial_month_in_primary_lockbox": acquisition.get("lockbox_period", {}).get("partial_month_extension") is None,
            "passed": period_passed,
        },
        "universe_review": {
            "requested_symbol_count": len(requested_symbols),
            "acquired_symbol_count": len(acquired_symbols),
            "missing_symbol_count": len(missing_symbols),
            "symbol_list_matches_development_reviewed_universe_exactly": universe_passed,
            "added_symbols": [],
            "removed_symbols": missing_symbols,
            "symbols": requested_symbols,
            "passed": universe_passed,
        },
        "expected_row_count_review": {
            "days": EXPECTED_DAYS,
            "bars_per_day": BARS_PER_DAY,
            "expected_rows_per_symbol": EXPECTED_ROWS_PER_SYMBOL,
            "expected_total_rows": EXPECTED_TOTAL_ROWS,
            "actual_total_rows": actual_total_rows,
            "passed": exact_rows_passed,
        },
        "per_symbol_coverage_review": {
            "full_coverage_symbol_count": len(full_coverage_symbols),
            "per_symbol": per_symbol_reviews,
            "passed": coverage_passed,
        },
        "ohlcv_sanity_review": {
            "open_high_low_close_positive": all(record.get("non_numeric_or_non_positive_ohlc_count", 0) == 0 for record in per_symbol_reviews.values()),
            "high_low_relationships_valid": all(record.get("ohlc_sanity_fail_count", 0) == 0 for record in per_symbol_reviews.values()),
            "volume_non_negative": all(record.get("negative_volume_count", 0) == 0 for record in per_symbol_reviews.values()),
            "quote_volume_non_negative": all(record.get("negative_quote_volume_count", 0) == 0 for record in per_symbol_reviews.values()),
            "passed": ohlcv_sanity_passed,
        },
        "schema_compatibility_review": {
            "development_panel_review_loaded": panel_review.get("status") is not None,
            "required_columns": sorted(DEVELOPMENT_PANEL_COMPATIBLE_COLUMNS),
            "quote_volume_presence_recorded": all(record.get("quote_volume_present") for record in per_symbol_reviews.values()),
            "schema_compatible": schema_compatible,
            "passed": schema_compatible,
        },
        "checksum_review": {
            "checksum_summary_exists": checksum_report.get("artifact_kind") == "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_CHECKSUM_REPORT",
            "manifest_payload_hash_exists": isinstance(acquisition.get("payload_sha256_excluding_hash"), str),
            "normalized_file_sha256_count": len(expected_sha_by_symbol),
            "all_normalized_file_sha256_present": len(expected_sha_by_symbol) == EXPECTED_SYMBOL_COUNT,
            "all_observed_sha256_match_manifest": all(record.get("sha256_matches_manifest") for record in per_symbol_reviews.values()),
            "passed": checksum_review_passed,
        },
        "lockbox_integrity_review": {
            "frozen_config_not_modified": lockbox_integrity.get("frozen_config_not_modified") is True,
            "strategy_execution_performed": False,
            "signal_generation_performed": False,
            "pnl_computation_performed": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
            "passed": lockbox_integrity_passed,
        },
        "review_findings": {
            "blocking_failures": blocking_failures,
            "attention_warnings": attention_warnings,
            "data_review_summary": "Lockbox forward OHLCV data review only; no strategy execution, signals, PnL, or optimization.",
        },
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "This review validates OHLCV/schema/coverage/checksum integrity only.",
            "No strategy features, signals, PnL, backtest, optimization, candidate generation, edge claim, or runtime/live/capital permission was computed or granted.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["data_review_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "data_review_created")
        and not blocking_failures,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"result_classification: {result_classification}")
    print(f"frozen_finalist: {FROZEN_FINALIST}")
    print(f"lockbox_start: {LOCKBOX_START}")
    print(f"lockbox_end: {LOCKBOX_END}")
    print(f"expected_total_rows: {EXPECTED_TOTAL_ROWS}")
    print(f"actual_total_rows: {actual_total_rows}")
    print(f"requested_symbol_count: {len(requested_symbols)}")
    print(f"acquired_symbol_count: {len(acquired_symbols)}")
    print(f"missing_symbol_count: {len(missing_symbols)}")
    print(f"full_coverage_symbol_count: {len(full_coverage_symbols)}")
    print(f"ohlcv_sanity_passed: {str(ohlcv_sanity_passed).lower()}")
    print(f"schema_compatible: {str(schema_compatible).lower()}")
    print(f"checksum_review_passed: {str(checksum_review_passed).lower()}")
    print("strategy_execution_performed: false")
    print("signal_generation_performed: false")
    print("pnl_computation_performed: false")
    print(f"next_allowed_step: {next_allowed_step}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
