from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_policy_application_residual_duplicate_diagnostic_after_build_block_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "6452700"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_ETH_POLICY_APPLICATION_RESIDUAL_DUPLICATE_DIAGNOSTIC_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_POLICY_APPLICATION_"
    "RESIDUAL_DUPLICATE_DIAGNOSTIC_CORRECTED_BUILD_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_POLICY_APPLICATION_"
    "RESIDUAL_DUPLICATE_DIAGNOSTIC_FAILED_REVIEW"
)
TARGET_SYMBOL = "ETH-USDT-SWAP"
APPROVED_DUPLICATE_OPEN_TIME = 1_697_108_400_000
APPROVED_DUPLICATE_OPEN_TIME_UTC = "2023-10-12T11:00:00+00:00"
APPROVED_DUPLICATE_SOURCE_DATE = "2023-10-12"
APPROVED_DUPLICATE_SOURCE_FILE = "ETH-USDT-SWAP-candlesticks-2023-10-12.csv"
DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_ETH_FILE_COUNT = 1_053
EXPECTED_MINUTE_MS = 60_000
EXPECTED_PREVIOUS_OBSERVED_ROWS_BEFORE_POLICY = 149_464
EXPECTED_PREVIOUS_CLEAN_ROWS_AFTER_POLICY = 149_462
EXPECTED_PREVIOUS_EXPECTED_DELTA = 1
EXPECTED_PREVIOUS_OBSERVED_DELTA = 2
ACTIVE_P1_ATTENTION_COUNT = 12
AFTER_QUALITY_SAFE = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_POLICY_APPLICATION_"
    "DIAGNOSED_CORRECTED_BUILD_READY"
)
NEXT_MODULE_SAFE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "corrected_policy_clean_build_execution_after_eth_residual_diagnostic_v1.py"
)
NEXT_MODULE_SECOND_EXACT = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_additional_exact_duplicate_policy_after_residual_diagnostic_v1.py"
)
NEXT_MODULE_MATERIAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1.py"
)
NEXT_MODULE_UNKNOWN = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_residual_duplicate_manual_review_required_v1.py"
)
FAILED_NEXT_MODULE = NEXT_MODULE_UNKNOWN

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
ANOMALY_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_eth_policy_v1"
)
ETH_POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_exact_duplicate_policy_after_diagnostic_v1"
)
ETH_DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_duplicate_diagnostic_after_build_anomaly_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "anomaly_summary": ANOMALY_RECORD_DIR / f"{ANOMALY_RECORD_DIR.name}_latest.json",
    "anomaly_blocked_record": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record.json",
    "anomaly_diagnostic_preview": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_preview.json",
    "anomaly_diagnostic_approval": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_approval_record.json",
    "anomaly_count_mismatch": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_policy_application_count_mismatch_report.json",
    "eth_policy_summary": ETH_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy_summary.json",
    "eth_exact_duplicate_policy": ETH_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_policy.json",
    "eth_exact_duplicate_drop_policy": ETH_POLICY_DIR
    / "historical_okx_10_symbol_pilot_eth_exact_duplicate_drop_policy.json",
    "eth_duplicate_diagnostic_summary": ETH_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_summary.json",
    "eth_duplicate_raw_rows_report": ETH_DIAGNOSTIC_DIR
    / "historical_okx_10_symbol_pilot_eth_duplicate_raw_rows_report.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
    "download_hash_validation_report": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_hash_validation_report.json",
}

EXPECTED_INPUT_SCHEMA = [
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

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "rebuild_execution_performed_now": False,
    "dedupe_execution_output_created_now": False,
    "modified_source_output_created_now": False,
    "output_1h_csv_created_now": False,
    "row_selection_performed_now": False,
    "rows_averaged_or_merged_now": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_candidate_touched": False,
    "edge_profit_claim_made": False,
    "full_universe_ready_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class DiagnosticBlocked(RuntimeError):
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
        raise DiagnosticBlocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise DiagnosticBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(data, dict), f"artifact {label} is not a JSON object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_zip_member(name: str) -> bool:
    pure = PurePosixPath(name)
    return not pure.is_absolute() and ".." not in pure.parts


def expected_csv(symbol: str, day: str) -> str:
    return f"{symbol}-candlesticks-{day}.csv"


def decimal_text(value: str) -> str:
    try:
        return format(Decimal(str(value).strip()).normalize(), "f")
    except InvalidOperation:
        return str(value).strip()


def normalized_input_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "instrument_name": str(row.get("instrument_name", "")).strip(),
        "open": decimal_text(str(row.get("open", ""))),
        "high": decimal_text(str(row.get("high", ""))),
        "low": decimal_text(str(row.get("low", ""))),
        "close": decimal_text(str(row.get("close", ""))),
        "vol": decimal_text(str(row.get("vol", ""))),
        "vol_ccy": decimal_text(str(row.get("vol_ccy", ""))),
        "vol_quote": decimal_text(str(row.get("vol_quote", ""))),
        "open_time": str(int(str(row.get("open_time", "")).strip())),
        "confirm": str(row.get("confirm", "")).strip(),
    }


def raw_row_copy(row: dict[str, str]) -> dict[str, str]:
    return {field: str(row.get(field, "")) for field in EXPECTED_INPUT_SCHEMA}


def validate_false(data: dict[str, Any], keys: list[str], label: str) -> None:
    for key in keys:
        require(data.get(key) is False, f"{label}.{key} must be false")


def validate_prior_artifacts(artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved ETH residual diagnostic module")

    anomaly = artifacts["anomaly_summary"]
    blocked = artifacts["anomaly_blocked_record"]
    preview = artifacts["anomaly_diagnostic_preview"]
    approval = artifacts["anomaly_diagnostic_approval"]
    mismatch = artifacts["anomaly_count_mismatch"]
    policy_summary = artifacts["eth_policy_summary"]
    policy = artifacts["eth_exact_duplicate_policy"]
    drop_policy = artifacts["eth_exact_duplicate_drop_policy"]
    diagnostic = artifacts["eth_duplicate_diagnostic_summary"]
    raw_rows = artifacts["eth_duplicate_raw_rows_report"]
    download_summary = artifacts["download_validator_summary"]
    hash_report = artifacts["download_hash_validation_report"]

    require(
        anomaly.get("historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_anomaly_record_status")
        == PREVIOUS_STATUS,
        "previous anomaly record status mismatch",
    )
    require(anomaly.get("next_module") == REQUESTED_MODULE, "previous anomaly next_module mismatch")
    require(anomaly.get("anomaly_symbol") == TARGET_SYMBOL, "previous anomaly symbol mismatch")
    require(anomaly.get("eth_exact_duplicate_policy_present") is True, "previous ETH policy missing")
    require(anomaly.get("eth_exact_duplicate_rows_dropped") == 1, "previous ETH drop count mismatch")
    require(anomaly.get("residual_duplicate_open_time_count_total") == 1, "previous residual count mismatch")
    require(anomaly.get("observed_new_symbol_source_rows_before_policy") == 149_464, "previous observed count mismatch")
    require(anomaly.get("clean_new_symbol_source_rows_after_policy") == 149_462, "previous clean count mismatch")
    require(anomaly.get("expected_clean_source_row_delta_for_one_exact_drop") == 1, "previous expected delta mismatch")
    require(anomaly.get("observed_clean_source_row_delta") == 2, "previous observed delta mismatch")
    require(anomaly.get("count_mismatch_detected") is True, "previous count mismatch not detected")
    validate_false(
        anomaly,
        [
            "data_build_performed",
            "aggregation_performed_now",
            "output_csv_created",
            "output_valid_for_research_backtest",
            "output_valid_for_edge_claim",
            "safe_for_full_universe_acquisition",
            "broad_acquisition_ready",
        ],
        "anomaly_summary",
    )
    require(anomaly.get("active_p0_blocker_count") == 1, "previous P0 count mismatch")
    require(anomaly.get("replacement_checks_all_true") is True, "previous replacement checks mismatch")

    require(blocked.get("pilot_policy_clean_build_execution_blocked") is True, "blocked record state mismatch")
    require(blocked.get("block_reason") == anomaly.get("block_reason"), "blocked reason mismatch")
    require(preview.get("eth_policy_application_residual_duplicate_diagnostic_preview_created") is True, "preview missing")
    require(approval.get("approval_grants_future_eth_policy_application_residual_duplicate_diagnostic_next") is True, "future diagnostic approval missing")
    validate_false(
        approval,
        [
            "approval_grants_diagnostic_now",
            "approval_grants_rebuild_now",
            "approval_grants_dedupe_now",
            "approval_grants_download_now",
            "approval_grants_api_now",
            "approval_grants_browse_now",
            "approval_grants_research_backtest_edge_now",
        ],
        "diagnostic_approval",
    )
    require(mismatch.get("count_mismatch_detected") is True, "count mismatch report mismatch")
    require(mismatch.get("observed_clean_source_row_delta") == 2, "count mismatch delta mismatch")

    require(policy_summary.get("target_symbol") == TARGET_SYMBOL, "policy summary target mismatch")
    require(policy_summary.get("duplicate_open_time") == APPROVED_DUPLICATE_OPEN_TIME, "policy summary open_time mismatch")
    require(policy_summary.get("duplicate_open_time_utc") == APPROVED_DUPLICATE_OPEN_TIME_UTC, "policy summary open_time UTC mismatch")
    require(policy_summary.get("exact_duplicate_extra_rows_to_drop") == 1, "policy summary drop count mismatch")
    require(policy_summary.get("material_conflict_present") is False, "policy summary material conflict mismatch")
    require(policy_summary.get("replacement_checks_all_true") is True, "policy summary checks mismatch")
    require(policy.get("policy", {}).get("duplicate_open_time") == APPROVED_DUPLICATE_OPEN_TIME, "policy open_time mismatch")
    require(policy.get("policy", {}).get("exact_duplicate_extra_rows_to_drop") == 1, "policy drop count mismatch")
    require(policy.get("material_conflict_present") is False, "policy material conflict mismatch")
    require(drop_policy.get("duplicate_open_time") == APPROVED_DUPLICATE_OPEN_TIME, "drop policy open_time mismatch")
    require(drop_policy.get("duplicate_open_time_utc") == APPROVED_DUPLICATE_OPEN_TIME_UTC, "drop policy open_time UTC mismatch")
    require(drop_policy.get("source_group_size") == 2, "drop policy source group size mismatch")
    require(drop_policy.get("exact_duplicate_extra_rows_to_drop") == 1, "drop policy drop count mismatch")
    require(drop_policy.get("drop_only_if_all_canonical_fields_identical") is True, "drop policy exact-only mismatch")

    require(diagnostic.get("target_symbol") == TARGET_SYMBOL, "prior diagnostic target mismatch")
    require(diagnostic.get("duplicate_classification") == "EXACT_DUPLICATE", "prior diagnostic classification mismatch")
    require(diagnostic.get("conflict_open_time") == APPROVED_DUPLICATE_OPEN_TIME, "prior diagnostic open_time mismatch")
    require(diagnostic.get("duplicate_open_time_count_total") == 1, "prior diagnostic duplicate count mismatch")
    require(diagnostic.get("duplicate_row_count") == 2, "prior diagnostic group size mismatch")
    require(diagnostic.get("differing_field_count") == 0, "prior diagnostic diff count mismatch")
    require(raw_rows.get("raw_duplicate_rows_captured") is True, "prior raw rows missing")
    require(len(raw_rows.get("raw_duplicate_rows", [])) == 2, "prior raw row count mismatch")

    require(download_summary.get("all_hashes_match_recorded") is True, "download validator hash status mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "hash report mismatch")
    require(hash_report.get("all_downloaded_zip_paths_exist") is True, "downloaded ZIP path status mismatch")
    eth_records = [row for row in hash_report.get("hashes", []) if row.get("symbol") == TARGET_SYMBOL]
    require(len(eth_records) == EXPECTED_ETH_FILE_COUNT, f"ETH file count mismatch: {len(eth_records)}")
    eth_records = sorted(eth_records, key=lambda row: str(row.get("date")))
    require(eth_records[0].get("date") == DATE_RANGE_START, "ETH start date mismatch")
    require(eth_records[-1].get("date") == DATE_RANGE_END, "ETH end date mismatch")
    for record in eth_records:
        require(record.get("hash_match") is True, f"ETH hash_match false for {record.get('date')}")
        require(record.get("recorded_sha256") == record.get("recomputed_sha256"), f"ETH recorded/recomputed mismatch {record.get('date')}")
        path = Path(str(record.get("local_zip_path", "")))
        require(path.exists(), f"ETH ZIP missing: {path}")
    return eth_records


def read_eth_rows(records: list[dict[str, Any]], capture_open_times: set[int] | None = None) -> dict[str, Any]:
    open_time_counts: dict[int, int] = defaultdict(int)
    captured: dict[int, list[dict[str, Any]]] = defaultdict(list)
    raw_rows_scanned = 0
    sha_reconfirmed_count = 0
    for record in records:
        day = str(record.get("date"))
        path = Path(str(record.get("local_zip_path", "")))
        recorded_sha = str(record.get("recorded_sha256"))
        digest = sha256_file(path)
        sha_reconfirmed_count += 1
        require(digest == recorded_sha, f"ETH SHA256 mismatch after recompute: {path}")
        inner_csv = expected_csv(TARGET_SYMBOL, day)
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) <= 10, f"ETH ZIP has too many members: {path}")
            require(all(safe_zip_member(name) for name in names), f"ETH ZIP traversal risk: {path}")
            require(inner_csv in names, f"ETH expected CSV missing: {inner_csv}")
            with archive.open(inner_csv, "r") as raw:
                reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
                require(reader.fieldnames == EXPECTED_INPUT_SCHEMA, f"ETH schema mismatch: {inner_csv}")
                for row_number, row in enumerate(reader, start=2):
                    raw_rows_scanned += 1
                    require(row.get("instrument_name") == TARGET_SYMBOL, f"ETH symbol mismatch {inner_csv} row={row_number}")
                    try:
                        open_time = int(str(row.get("open_time", "")).strip())
                    except ValueError as exc:
                        raise DiagnosticBlocked(f"ETH open_time parse failed {inner_csv} row={row_number}") from exc
                    open_time_counts[open_time] += 1
                    if capture_open_times is not None and open_time in capture_open_times:
                        captured[open_time].append(
                            {
                                "source_date": day,
                                "source_file": inner_csv,
                                "source_zip": str(path),
                                "source_zip_sha256": digest,
                                "row_number": row_number,
                                "raw_row": raw_row_copy(row),
                                "normalized_row": normalized_input_row(row),
                            }
                        )
    duplicate_open_times = sorted(open_time for open_time, count in open_time_counts.items() if count > 1)
    duplicate_extra_rows = sum(open_time_counts[open_time] - 1 for open_time in duplicate_open_times)
    return {
        "raw_rows_scanned": raw_rows_scanned,
        "open_time_counts": dict(open_time_counts),
        "unique_open_time_count": len(open_time_counts),
        "duplicate_open_times": duplicate_open_times,
        "duplicate_group_count": len(duplicate_open_times),
        "duplicate_extra_row_count": duplicate_extra_rows,
        "captured_duplicate_rows": dict(captured),
        "sha_reconfirmed_count": sha_reconfirmed_count,
    }


def missing_minutes_after_policy(open_time_counts: dict[int, int]) -> int:
    ordered = sorted(open_time_counts)
    if not ordered:
        return 0
    missing = 0
    previous = ordered[0]
    for open_time in ordered[1:]:
        delta = open_time - previous
        if delta > EXPECTED_MINUTE_MS:
            missing += max(1, (delta // EXPECTED_MINUTE_MS) - 1)
        previous = open_time
    return missing


def classify_duplicate_groups(captured: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for open_time in sorted(captured):
        rows = captured[open_time]
        normalized_rows = [row["normalized_row"] for row in rows]
        exact = bool(rows) and all(row == normalized_rows[0] for row in normalized_rows)
        differing_fields = []
        if not exact and normalized_rows:
            fields = list(normalized_rows[0])
            differing_fields = [
                field
                for field in fields
                if len({row.get(field) for row in normalized_rows}) > 1
            ]
        groups.append(
            {
                "open_time": open_time,
                "open_time_utc": APPROVED_DUPLICATE_OPEN_TIME_UTC
                if open_time == APPROVED_DUPLICATE_OPEN_TIME
                else datetime.fromtimestamp(open_time / 1000, tz=timezone.utc).isoformat(),
                "group_size": len(rows),
                "duplicate_extra_rows": max(0, len(rows) - 1),
                "exact_duplicate_group": exact,
                "differing_field_count": len(differing_fields),
                "differing_fields": differing_fields,
                "matches_approved_policy_open_time": open_time == APPROVED_DUPLICATE_OPEN_TIME,
                "raw_rows": rows,
            }
        )
    return groups


def build_payloads(
    generated_at: str,
    artifacts: dict[str, dict[str, Any]],
    eth_records: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    first_pass = read_eth_rows(eth_records)
    duplicate_open_times = set(first_pass["duplicate_open_times"])
    second_pass = read_eth_rows(eth_records, duplicate_open_times)
    require(first_pass["open_time_counts"] == second_pass["open_time_counts"], "ETH duplicate scan not repeatable")
    groups = classify_duplicate_groups(second_pass["captured_duplicate_rows"])

    approved_group = next(
        (group for group in groups if group["open_time"] == APPROVED_DUPLICATE_OPEN_TIME),
        None,
    )
    approved_duplicate_found = approved_group is not None
    approved_duplicate_group_exact = bool(approved_group and approved_group["exact_duplicate_group"] is True)
    approved_duplicate_group_size = int(approved_group["group_size"]) if approved_group else 0
    raw_duplicate_group_count = int(first_pass["duplicate_group_count"])
    second_duplicate_group_discovered = any(
        group["open_time"] != APPROVED_DUPLICATE_OPEN_TIME for group in groups
    )
    material_conflict_discovered = any(group["exact_duplicate_group"] is False for group in groups)
    diagnostic_exact_duplicate_rows_to_drop = (
        1
        if approved_duplicate_found
        and approved_duplicate_group_exact
        and approved_duplicate_group_size == 2
        else 0
    )
    diagnostic_policy_drops_only_extra_row = diagnostic_exact_duplicate_rows_to_drop == 1
    diagnostic_policy_drops_both_rows = False
    diagnostic_clean_eth_row_count_after_policy = (
        int(first_pass["raw_rows_scanned"]) - diagnostic_exact_duplicate_rows_to_drop
    )
    residual_duplicate_group_count_after_corrected_policy = raw_duplicate_group_count
    if diagnostic_policy_drops_only_extra_row:
        residual_duplicate_group_count_after_corrected_policy -= 1
    residual_duplicate_group_count_after_corrected_policy = max(
        0, residual_duplicate_group_count_after_corrected_policy
    )
    residual_duplicate_after_corrected_policy = (
        residual_duplicate_group_count_after_corrected_policy > 0
    )
    missing_minute_count_after_corrected_policy = missing_minutes_after_policy(
        first_pass["open_time_counts"]
    )
    previous_partial = EXPECTED_PREVIOUS_OBSERVED_ROWS_BEFORE_POLICY < int(
        first_pass["raw_rows_scanned"]
    )
    previous_delta_mismatch = (
        EXPECTED_PREVIOUS_OBSERVED_DELTA != EXPECTED_PREVIOUS_EXPECTED_DELTA
    )
    safe_for_corrected_build = (
        raw_duplicate_group_count == 1
        and approved_duplicate_found
        and approved_duplicate_group_exact
        and approved_duplicate_group_size == 2
        and diagnostic_exact_duplicate_rows_to_drop == 1
        and diagnostic_policy_drops_only_extra_row
        and not diagnostic_policy_drops_both_rows
        and not residual_duplicate_after_corrected_policy
        and not second_duplicate_group_discovered
        and not material_conflict_discovered
        and missing_minute_count_after_corrected_policy == 0
    )
    previous_count_mismatch_explained = False
    if previous_count_mismatch_explained:
        previous_counts_classified_as_partial_or_bug = (
            "PARTIAL_EARLY_STOP_COUNTERS_WITH_POLICY_APPLICATION_OR_COUNTER_BUG"
        )
        diagnostic_classification = (
            "POLICY_APPLICATION_OR_COUNTER_BUG_RESOLVED_BY_CORRECT_EXACT_DEDUPE_IMPLEMENTATION"
        )
        policy_application_bug_detected = True
        counter_bug_detected = True
        next_module = NEXT_MODULE_SAFE
        current_quality = AFTER_QUALITY_SAFE
        status = PASS_STATUS
        active_p0_blocker_count = 0
    elif second_duplicate_group_discovered and not material_conflict_discovered:
        previous_counts_classified_as_partial_or_bug = "SECOND_DUPLICATE_GROUP_DISCOVERED"
        diagnostic_classification = "SECOND_DUPLICATE_GROUP_DISCOVERED"
        policy_application_bug_detected = False
        counter_bug_detected = False
        next_module = NEXT_MODULE_SECOND_EXACT
        current_quality = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_ADDITIONAL_EXACT_DUPLICATE_POLICY_READY"
        status = (
            "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_POLICY_APPLICATION_"
            "RESIDUAL_DUPLICATE_DIAGNOSTIC_ADDITIONAL_EXACT_DUPLICATE_POLICY_READY"
        )
        active_p0_blocker_count = 1
    elif material_conflict_discovered:
        previous_counts_classified_as_partial_or_bug = "MATERIAL_CONFLICT_DISCOVERED"
        diagnostic_classification = "MATERIAL_CONFLICT_DISCOVERED"
        policy_application_bug_detected = False
        counter_bug_detected = False
        next_module = NEXT_MODULE_MATERIAL
        current_quality = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_MATERIAL_DUPLICATE_CONFLICT_POLICY_READY"
        status = (
            "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_POLICY_APPLICATION_"
            "RESIDUAL_DUPLICATE_DIAGNOSTIC_MATERIAL_CONFLICT_POLICY_READY"
        )
        active_p0_blocker_count = 1
    else:
        previous_counts_classified_as_partial_or_bug = "UNKNOWN_UNINSPECTABLE"
        diagnostic_classification = "UNKNOWN"
        policy_application_bug_detected = False
        counter_bug_detected = False
        next_module = NEXT_MODULE_UNKNOWN
        current_quality = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_RESIDUAL_DUPLICATE_MANUAL_REVIEW_REQUIRED"
        status = (
            "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_POLICY_APPLICATION_"
            "RESIDUAL_DUPLICATE_DIAGNOSTIC_MANUAL_REVIEW_REQUIRED"
        )
        active_p0_blocker_count = 1

    previous_count_mismatch_explained = bool(
        previous_partial
        and previous_delta_mismatch
        and diagnostic_classification
        in {
            "POLICY_APPLICATION_OR_COUNTER_BUG_RESOLVED_BY_CORRECT_EXACT_DEDUPE_IMPLEMENTATION",
            "SECOND_DUPLICATE_GROUP_DISCOVERED",
            "MATERIAL_CONFLICT_DISCOVERED",
        }
    )

    corrected_policy_clean_build_preview_created = safe_for_corrected_build
    corrected_policy_clean_build_approval_record_created = safe_for_corrected_build
    approval_grants_future_corrected_policy_clean_build_next = safe_for_corrected_build
    approval_grants_corrected_build_now = False

    base = {
        "diagnostic_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "raw_eth_rows_scanned": int(first_pass["raw_rows_scanned"]),
        "raw_eth_unique_open_time_count": int(first_pass["unique_open_time_count"]),
        "raw_eth_duplicate_group_count": raw_duplicate_group_count,
        "raw_eth_duplicate_extra_row_count": int(first_pass["duplicate_extra_row_count"]),
        "approved_duplicate_open_time": APPROVED_DUPLICATE_OPEN_TIME,
        "approved_duplicate_open_time_utc": APPROVED_DUPLICATE_OPEN_TIME_UTC,
        "approved_duplicate_found": approved_duplicate_found,
        "approved_duplicate_group_exact": approved_duplicate_group_exact,
        "approved_duplicate_group_size": approved_duplicate_group_size,
        "diagnostic_exact_duplicate_rows_to_drop": diagnostic_exact_duplicate_rows_to_drop,
        "diagnostic_policy_drops_only_extra_row": diagnostic_policy_drops_only_extra_row,
        "diagnostic_policy_drops_both_rows": diagnostic_policy_drops_both_rows,
        "diagnostic_clean_eth_row_count_after_policy": diagnostic_clean_eth_row_count_after_policy,
        "residual_duplicate_after_corrected_policy": residual_duplicate_after_corrected_policy,
        "residual_duplicate_group_count_after_corrected_policy": residual_duplicate_group_count_after_corrected_policy,
        "second_duplicate_group_discovered": second_duplicate_group_discovered,
        "material_conflict_discovered": material_conflict_discovered,
        "missing_minute_count_after_corrected_policy": missing_minute_count_after_corrected_policy,
        "previous_count_mismatch_explained": previous_count_mismatch_explained,
        "previous_counts_classified_as_partial_or_bug": previous_counts_classified_as_partial_or_bug,
        "policy_application_bug_detected": policy_application_bug_detected,
        "counter_bug_detected": counter_bug_detected,
        "corrected_policy_clean_build_preview_created": corrected_policy_clean_build_preview_created,
        "corrected_policy_clean_build_approval_record_created": corrected_policy_clean_build_approval_record_created,
        "approval_grants_corrected_build_now": approval_grants_corrected_build_now,
        "approval_grants_future_corrected_policy_clean_build_next": approval_grants_future_corrected_policy_clean_build_next,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": active_p0_blocker_count,
        "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
        "current_evidence_chain_quality_after_diagnostic": current_quality,
        "next_module": next_module,
    }
    raw_group_report = {
        "eth_residual_duplicate_raw_group_report_created": True,
        "source_zip_sha256_reconfirmed_before_each_read": True,
        "sha256_reconfirmed_file_count_first_pass": int(first_pass["sha_reconfirmed_count"]),
        "sha256_reconfirmed_file_count_second_pass": int(second_pass["sha_reconfirmed_count"]),
        "duplicate_groups": groups,
        **base,
    }
    count_audit = {
        "eth_policy_application_count_audit_created": True,
        "previous_observed_new_symbol_source_rows_before_policy": EXPECTED_PREVIOUS_OBSERVED_ROWS_BEFORE_POLICY,
        "previous_clean_new_symbol_source_rows_after_policy": EXPECTED_PREVIOUS_CLEAN_ROWS_AFTER_POLICY,
        "previous_expected_clean_source_row_delta_for_one_exact_drop": EXPECTED_PREVIOUS_EXPECTED_DELTA,
        "previous_observed_clean_source_row_delta": EXPECTED_PREVIOUS_OBSERVED_DELTA,
        "previous_observed_rows_were_partial_early_stop_counter": previous_partial,
        "full_eth_raw_rows_scanned_now": int(first_pass["raw_rows_scanned"]),
        "full_eth_clean_rows_after_corrected_policy_now": diagnostic_clean_eth_row_count_after_policy,
        "diagnostic_classification": diagnostic_classification,
        **base,
    }
    corrected_preview = {
        "eth_corrected_exact_dedupe_logic_preview_created": True,
        "preview_only": True,
        "dedupe_execution_output_created_now": False,
        "modified_source_output_created_now": False,
        "corrected_logic": {
            "read_only_diagnostic_logic": True,
            "approved_duplicate_open_time": APPROVED_DUPLICATE_OPEN_TIME,
            "approved_duplicate_open_time_utc": APPROVED_DUPLICATE_OPEN_TIME_UTC,
            "keep_exactly_one_canonical_row": True,
            "drop_exactly_one_duplicate_extra_row": diagnostic_exact_duplicate_rows_to_drop == 1,
            "drop_both_rows": False,
            "alter_ohlcv": False,
            "write_deduped_source_output": False,
            "write_1h_output": False,
        },
        "corrected_policy_clean_build_approval_record": {
            "approval_grants_corrected_build_now": False,
            "approval_grants_future_corrected_policy_clean_build_next": approval_grants_future_corrected_policy_clean_build_next,
            "approval_grants_download_now": False,
            "approval_grants_api_now": False,
            "approval_grants_browse_now": False,
            "approval_grants_research_backtest_edge_now": False,
            "next_module": next_module,
        },
        **base,
    }
    route_decision = {
        "eth_residual_duplicate_next_route_decision_created": True,
        "diagnostic_classification": diagnostic_classification,
        "safe_outcome_confirmed": safe_for_corrected_build,
        "next_module_decision_reason": previous_counts_classified_as_partial_or_bug,
        **base,
    }
    common_replacement_checks = {
        "diagnostic_performed": base["diagnostic_performed"] is True,
        "target_symbol_eth": base["target_symbol"] == TARGET_SYMBOL,
        "raw_eth_rows_scanned_full_range": base["raw_eth_rows_scanned"] >= 1_516_320,
        "raw_unique_count_positive": base["raw_eth_unique_open_time_count"] > 0,
        "raw_duplicate_group_count_positive": base["raw_eth_duplicate_group_count"] >= 1,
        "raw_duplicate_extra_row_count_positive": base["raw_eth_duplicate_extra_row_count"] >= 1,
        "approved_duplicate_found": base["approved_duplicate_found"] is True,
        "approved_duplicate_group_exact": base["approved_duplicate_group_exact"] is True,
        "approved_duplicate_group_size_two": base["approved_duplicate_group_size"] == 2,
        "diagnostic_drops_one_extra_row_only": base["diagnostic_exact_duplicate_rows_to_drop"] == 1
        and base["diagnostic_policy_drops_only_extra_row"] is True
        and base["diagnostic_policy_drops_both_rows"] is False,
        "no_missing_minutes_after_corrected_policy": base["missing_minute_count_after_corrected_policy"] == 0,
        "previous_count_mismatch_explained": base["previous_count_mismatch_explained"] is True,
        "approval_grants_corrected_build_now_false": base["approval_grants_corrected_build_now"] is False,
        "no_build_aggregation_output": base["data_build_performed"] is False
        and base["aggregation_performed_now"] is False
        and base["output_csv_created"] is False,
        "not_research_backtest_edge_full_universe_broad": base[
            "output_valid_for_research_backtest"
        ]
        is False
        and base["output_valid_for_edge_claim"] is False
        and base["safe_for_full_universe_acquisition"] is False
        and base["broad_acquisition_ready"] is False,
        "p1_attention_at_least_12": base["active_p1_attention_count"] >= 12,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    if safe_for_corrected_build:
        route_replacement_checks = {
            "safe_route_raw_duplicate_group_count_one": base["raw_eth_duplicate_group_count"] == 1,
            "safe_route_raw_duplicate_extra_row_count_one": base["raw_eth_duplicate_extra_row_count"] == 1,
            "safe_route_no_residual_after_corrected_policy": base["residual_duplicate_after_corrected_policy"] is False
            and base["residual_duplicate_group_count_after_corrected_policy"] == 0,
            "safe_route_no_second_duplicate_or_material_conflict": base["second_duplicate_group_discovered"] is False
            and base["material_conflict_discovered"] is False,
            "safe_route_corrected_preview_and_approval_created": base["corrected_policy_clean_build_preview_created"] is True
            and base["corrected_policy_clean_build_approval_record_created"] is True,
            "safe_route_approval_future_corrected_build_next": base[
                "approval_grants_future_corrected_policy_clean_build_next"
            ]
            is True,
            "safe_route_p0_cleared": base["active_p0_blocker_count"] == 0,
            "safe_route_next_module_valid": base["next_module"] == NEXT_MODULE_SAFE,
        }
    elif material_conflict_discovered:
        route_replacement_checks = {
            "material_route_second_duplicate_discovered": base["second_duplicate_group_discovered"] is True,
            "material_route_material_conflict_discovered": base["material_conflict_discovered"] is True,
            "material_route_residual_duplicate_remains": base["residual_duplicate_after_corrected_policy"] is True
            and base["residual_duplicate_group_count_after_corrected_policy"] >= 1,
            "material_route_corrected_build_not_approved": base[
                "approval_grants_future_corrected_policy_clean_build_next"
            ]
            is False
            and base["corrected_policy_clean_build_preview_created"] is False
            and base["corrected_policy_clean_build_approval_record_created"] is False,
            "material_route_p0_remains_active": base["active_p0_blocker_count"] == 1,
            "material_route_next_module_valid": base["next_module"] == NEXT_MODULE_MATERIAL,
        }
    elif second_duplicate_group_discovered:
        route_replacement_checks = {
            "second_exact_route_second_duplicate_discovered": base["second_duplicate_group_discovered"] is True,
            "second_exact_route_no_material_conflict": base["material_conflict_discovered"] is False,
            "second_exact_route_corrected_build_not_approved": base[
                "approval_grants_future_corrected_policy_clean_build_next"
            ]
            is False,
            "second_exact_route_p0_remains_active": base["active_p0_blocker_count"] == 1,
            "second_exact_route_next_module_valid": base["next_module"] == NEXT_MODULE_SECOND_EXACT,
        }
    else:
        route_replacement_checks = {
            "unknown_route_corrected_build_not_approved": base[
                "approval_grants_future_corrected_policy_clean_build_next"
            ]
            is False,
            "unknown_route_p0_remains_active": base["active_p0_blocker_count"] == 1,
            "unknown_route_next_module_valid": base["next_module"] == NEXT_MODULE_UNKNOWN,
        }
    replacement_checks = {**common_replacement_checks, **route_replacement_checks}
    replacement_checks_all_true = all(replacement_checks.values())
    diagnostic_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_status": status,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_diagnostic_run": tracked_python_count(),
        **base,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic.json": diagnostic_payload,
        "historical_okx_10_symbol_pilot_eth_residual_duplicate_raw_group_report.json": raw_group_report,
        "historical_okx_10_symbol_pilot_eth_policy_application_count_audit.json": count_audit,
        "historical_okx_10_symbol_pilot_eth_corrected_exact_dedupe_logic_preview.json": corrected_preview,
        "historical_okx_10_symbol_pilot_eth_residual_duplicate_next_route_decision.json": route_decision,
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_summary.json": diagnostic_payload,
        f"{MODULE_NAME}_latest.json": diagnostic_payload,
    }
    return diagnostic_payload, payloads


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic.json",
        "historical_okx_10_symbol_pilot_eth_residual_duplicate_raw_group_report.json",
        "historical_okx_10_symbol_pilot_eth_policy_application_count_audit.json",
        "historical_okx_10_symbol_pilot_eth_corrected_exact_dedupe_logic_preview.json",
        "historical_okx_10_symbol_pilot_eth_residual_duplicate_next_route_decision.json",
        "historical_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    raw_group = loaded[
        "historical_okx_10_symbol_pilot_eth_residual_duplicate_raw_group_report.json"
    ]
    count_audit = loaded[
        "historical_okx_10_symbol_pilot_eth_policy_application_count_audit.json"
    ]
    route = loaded[
        "historical_okx_10_symbol_pilot_eth_residual_duplicate_next_route_decision.json"
    ]
    duplicate_groups = raw_group.get("duplicate_groups", [])
    checks = {
        "required_artifacts_exist": True,
        "summary_replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
        "raw_group_captured_approved_duplicate": raw_group.get("approved_duplicate_found") is True
        and any(
            group.get("open_time") == APPROVED_DUPLICATE_OPEN_TIME
            and group.get("exact_duplicate_group") is True
            for group in duplicate_groups
        ),
        "count_audit_explains_previous_mismatch": count_audit.get(
            "previous_count_mismatch_explained"
        )
        is True,
        "route_decision_matches_summary": route.get("next_module") == summary.get("next_module")
        and route.get("next_module")
        in {
            NEXT_MODULE_SAFE,
            NEXT_MODULE_SECOND_EXACT,
            NEXT_MODULE_MATERIAL,
            NEXT_MODULE_UNKNOWN,
        },
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    eth_records = validate_prior_artifacts(artifacts)
    summary, payloads = build_payloads(generated_at, artifacts, eth_records)
    require(summary["replacement_checks_all_true"] is True, "replacement checks failed")
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    written = validate_written_artifacts(summary)
    require(written["written_artifacts_valid"] is True, f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except DiagnosticBlocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked_payload = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_eth_policy_application_residual_duplicate_diagnostic_status": BLOCKED_STATUS,
            "diagnostic_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "raw_eth_rows_scanned": 0,
            "raw_eth_unique_open_time_count": 0,
            "raw_eth_duplicate_group_count": 0,
            "raw_eth_duplicate_extra_row_count": 0,
            "approved_duplicate_open_time": APPROVED_DUPLICATE_OPEN_TIME,
            "approved_duplicate_open_time_utc": APPROVED_DUPLICATE_OPEN_TIME_UTC,
            "approved_duplicate_found": False,
            "approved_duplicate_group_exact": False,
            "approved_duplicate_group_size": 0,
            "diagnostic_exact_duplicate_rows_to_drop": 0,
            "diagnostic_policy_drops_only_extra_row": False,
            "diagnostic_policy_drops_both_rows": False,
            "diagnostic_clean_eth_row_count_after_policy": 0,
            "residual_duplicate_after_corrected_policy": True,
            "residual_duplicate_group_count_after_corrected_policy": 1,
            "second_duplicate_group_discovered": False,
            "material_conflict_discovered": False,
            "missing_minute_count_after_corrected_policy": 0,
            "previous_count_mismatch_explained": False,
            "previous_counts_classified_as_partial_or_bug": "UNKNOWN",
            "policy_application_bug_detected": False,
            "counter_bug_detected": False,
            "corrected_policy_clean_build_preview_created": False,
            "corrected_policy_clean_build_approval_record_created": False,
            "approval_grants_corrected_build_now": False,
            "approval_grants_future_corrected_policy_clean_build_next": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": ACTIVE_P1_ATTENTION_COUNT,
            "current_evidence_chain_quality_after_diagnostic": PREVIOUS_STATUS,
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked_payload)
        print(json.dumps(blocked_payload, indent=2, sort_keys=True))
        raise SystemExit(1)
