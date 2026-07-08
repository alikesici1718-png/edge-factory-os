#!/usr/bin/env python3
"""Repo-only validator for the OKX 88-symbol 1m-to-1h build output.

This validator reads the produced 1h output and build manifests only. It does
not read original 1m ZIP/CSV sources, build data, aggregate, download, browse,
or mark research/backtest/edge readiness.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1.py"
)
BUILD_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
)
FINAL_SUMMARY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1"
)

BUILD_REPORT = BUILD_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_report.json"
BUILD_MANIFEST = BUILD_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
PER_SYMBOL_COUNTS = BUILD_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_per_symbol_counts.csv"
POLICY_EFFECTS = BUILD_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_policy_effects_report.json"
SCHEMA_REPORT = BUILD_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json"
PROVENANCE = BUILD_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_provenance_manifest.json"
BUILD_SUMMARY = BUILD_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_summary.json"
COMPLETE_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
GAP_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_gap_symbol_set_locked.json"

EXPECTED_HEAD = "f1e9328"
EXPECTED_SELECTED_SYMBOL_COUNT = 88
EXPECTED_GAP_SYMBOL_COUNT = 215
EXPECTED_TOTAL_SOURCE_FILE_COUNT = 92664
EXPECTED_TOTAL_SOURCE_ROWS = 133436160
EXPECTED_RAW_SOURCE_ROWS_READ = 133464732
EXPECTED_EXACT_DUPLICATES = 28497
EXPECTED_MATERIAL_CONFLICTS = 168
EXPECTED_CLEAN_SOURCE_ROWS = 133436067
EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = 25272
EXPECTED_TOTAL_OUTPUT_ROWS_1H = 2223936
EXPECTED_COMPLETE_1H_ROWS = 2223843
EXPECTED_INCOMPLETE_1H_ROWS = 93
REQUIRED_OUTPUT_FIELDS = [
    "symbol",
    "hour_open_time_utc",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "source_row_count",
    "complete_1h",
    "source_manifest_ref",
    "source_sha256_ref",
    "pipeline_validation_only",
]
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_VALIDATED"
FAIL_STATUS = "FAIL_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_VALIDATION_REVIEW_REQUIRED"
PASS_DECISION = "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SUMMARY_READY"
FAIL_DECISION = "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_VALIDATION_FAILED_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1.py"
NEXT_FAIL_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_validation_failed_record_v1.py"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed = {f"?? {TOOL_REL.as_posix()}", f" M {TOOL_REL.as_posix()}", f"A  {TOOL_REL.as_posix()}"}
    unexpected = [line for line in lines if line.replace("\\", "/") not in allowed]
    return not unexpected, unexpected


def parse_decimal(raw: str) -> Decimal | None:
    try:
        value = Decimal(raw)
    except (InvalidOperation, TypeError):
        return None
    return value if value.is_finite() else None


def parse_hour(raw: str) -> datetime | None:
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def read_per_symbol_counts() -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    totals = defaultdict(int)
    with PER_SYMBOL_COUNTS.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            symbol = row["symbol"]
            parsed = {
                key: int(row[key])
                for key in [
                    "source_file_count_processed",
                    "raw_source_rows_read",
                    "exact_duplicate_rows_dropped",
                    "material_conflict_rows_quarantined",
                    "clean_source_rows_after_policy",
                    "output_1h_row_count",
                    "complete_1h_row_count",
                    "incomplete_1h_row_count",
                ]
            }
            rows[symbol] = parsed
            for key, value in parsed.items():
                totals[key] += value
    return rows, dict(totals)


def validate_output_csv(output_path: Path, locked_symbols: set[str], gap_symbols: set[str]) -> dict[str, Any]:
    symbol_counts = Counter()
    complete_counts = Counter()
    incomplete_counts = Counter()
    seen_symbols: set[str] = set()
    gap_symbols_in_output: set[str] = set()
    last_hour_by_symbol: dict[str, datetime] = {}
    first_hour_by_symbol: dict[str, str] = {}
    final_hour_by_symbol: dict[str, str] = {}
    output_rows = 0
    complete_rows = 0
    incomplete_rows = 0
    duplicate_symbol_hour_count = 0
    non_monotonic_count = 0
    invalid_numeric_row_count = 0
    negative_volume_row_count = 0
    nan_inf_row_count = 0
    no_incomplete_hour_marked_complete = True
    no_complete_hour_source_row_count_lt_60 = True
    schema_validated = False
    pipeline_validation_only_false_count = 0

    with output_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        schema_validated = reader.fieldnames == REQUIRED_OUTPUT_FIELDS
        for row in reader:
            output_rows += 1
            symbol = row.get("symbol", "")
            seen_symbols.add(symbol)
            if symbol in gap_symbols:
                gap_symbols_in_output.add(symbol)
            hour = parse_hour(row.get("hour_open_time_utc", ""))
            if hour is None:
                invalid_numeric_row_count += 1
                continue
            if symbol not in first_hour_by_symbol:
                first_hour_by_symbol[symbol] = row["hour_open_time_utc"]
            final_hour_by_symbol[symbol] = row["hour_open_time_utc"]
            prior_hour = last_hour_by_symbol.get(symbol)
            if prior_hour is not None:
                if hour == prior_hour:
                    duplicate_symbol_hour_count += 1
                if hour <= prior_hour:
                    non_monotonic_count += 1
            last_hour_by_symbol[symbol] = hour
            symbol_counts[symbol] += 1

            values = {field: parse_decimal(row.get(field, "")) for field in ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote"]}
            if any(value is None for value in values.values()):
                invalid_numeric_row_count += 1
                nan_inf_row_count += 1
                continue
            open_value = values["open"]
            high_value = values["high"]
            low_value = values["low"]
            close_value = values["close"]
            volumes = [values["vol"], values["vol_ccy"], values["vol_quote"]]
            if high_value < low_value or high_value < open_value or high_value < close_value or low_value > open_value or low_value > close_value:
                invalid_numeric_row_count += 1
            if any(volume < 0 for volume in volumes):
                negative_volume_row_count += 1
            try:
                source_row_count = int(row.get("source_row_count", ""))
            except ValueError:
                invalid_numeric_row_count += 1
                continue
            complete_flag = row.get("complete_1h") == "true"
            if complete_flag:
                complete_rows += 1
                complete_counts[symbol] += 1
                if source_row_count < 60:
                    no_complete_hour_source_row_count_lt_60 = False
                    no_incomplete_hour_marked_complete = False
            else:
                incomplete_rows += 1
                incomplete_counts[symbol] += 1
            if row.get("pipeline_validation_only") != "true":
                pipeline_validation_only_false_count += 1

    per_symbol_output_row_count_valid = (
        len(symbol_counts) == len(locked_symbols)
        and set(symbol_counts) == locked_symbols
        and all(count == EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H for count in symbol_counts.values())
    )
    hour_range_start_values = sorted(set(first_hour_by_symbol.values()))
    hour_range_end_values = sorted(set(final_hour_by_symbol.values()))
    return {
        "complete_1h_row_count": complete_rows,
        "duplicate_symbol_hour_count": duplicate_symbol_hour_count,
        "first_hour_values": hour_range_start_values,
        "gap_symbol_in_output_count": len(gap_symbols_in_output),
        "gap_symbols_in_output": sorted(gap_symbols_in_output),
        "incomplete_1h_row_count": incomplete_rows,
        "invalid_numeric_row_count": invalid_numeric_row_count,
        "last_hour_values": hour_range_end_values,
        "locked_complete_symbols_all_in_output": locked_symbols.issubset(seen_symbols),
        "nan_inf_row_count": nan_inf_row_count,
        "negative_volume_row_count": negative_volume_row_count,
        "no_complete_hour_source_row_count_lt_60": no_complete_hour_source_row_count_lt_60,
        "no_incomplete_hour_marked_complete": no_incomplete_hour_marked_complete,
        "output_duplicate_symbol_hour_count": duplicate_symbol_hour_count,
        "output_hours_monotonic_by_symbol": non_monotonic_count == 0,
        "output_1h_row_count": output_rows,
        "output_schema_validated": schema_validated,
        "output_symbol_count": len(seen_symbols),
        "output_unique_symbol_hour_count": output_rows - duplicate_symbol_hour_count,
        "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        "pipeline_validation_only_false_count": pipeline_validation_only_false_count,
        "symbols_in_output": sorted(seen_symbols),
    }


def build_validation() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    required_paths = [BUILD_REPORT, BUILD_MANIFEST, PER_SYMBOL_COUNTS, POLICY_EFFECTS, SCHEMA_REPORT, PROVENANCE, BUILD_SUMMARY]
    artifacts_confirmed = all(path.exists() for path in required_paths)
    report = read_json(BUILD_REPORT)
    manifest = read_json(BUILD_MANIFEST)
    policy = read_json(POLICY_EFFECTS)
    schema_report = read_json(SCHEMA_REPORT)
    provenance = read_json(PROVENANCE)
    complete_locked = read_json(COMPLETE_LOCKED)
    gap_locked = read_json(GAP_LOCKED)
    locked_symbols = set(complete_locked.get("near_3y_complete_symbols", []))
    gap_symbols = set(gap_locked.get("coverage_gap_symbols", []))
    output_path = Path(report.get("output_file", ""))
    output_file_exists = output_path.exists()
    output_manifest_exists = BUILD_MANIFEST.exists()
    per_symbol_rows, per_symbol_totals = read_per_symbol_counts()
    output_validation = validate_output_csv(output_path, locked_symbols, gap_symbols)

    selected_symbol_count = int(report.get("selected_symbol_count", -1))
    excluded_gap_symbol_count = int(report.get("excluded_gap_symbol_count", -1))
    source_file_count_processed = int(report.get("source_file_count_processed", -1))
    raw_source_rows_read = int(report.get("raw_source_rows_read", -1))
    exact_duplicate_rows_dropped = int(report.get("exact_duplicate_rows_dropped", -1))
    material_conflict_rows_quarantined = int(report.get("material_conflict_rows_quarantined", -1))
    clean_source_rows_after_policy = int(report.get("clean_source_rows_after_policy", -1))
    complete_1h_row_count = output_validation["complete_1h_row_count"]
    incomplete_1h_row_count = output_validation["incomplete_1h_row_count"]
    output_1h_row_count = output_validation["output_1h_row_count"]
    policy_row_count_reconciliation_pass = (
        raw_source_rows_read - exact_duplicate_rows_dropped - material_conflict_rows_quarantined == clean_source_rows_after_policy
        and EXPECTED_TOTAL_SOURCE_ROWS - clean_source_rows_after_policy == EXPECTED_INCOMPLETE_1H_ROWS
        and incomplete_1h_row_count == EXPECTED_INCOMPLETE_1H_ROWS
    )
    complete_plus_incomplete_equals_total = complete_1h_row_count + incomplete_1h_row_count == output_1h_row_count
    numeric_sanity_validated = (
        output_validation["invalid_numeric_row_count"] == 0
        and output_validation["negative_volume_row_count"] == 0
        and output_validation["nan_inf_row_count"] == 0
    )
    provenance_symbols = Counter(entry.get("symbol") for entry in provenance.get("provenance_entries", []))
    provenance_validated = (
        provenance.get("provenance_entry_count") == EXPECTED_TOTAL_SOURCE_FILE_COUNT
        and set(provenance_symbols) == locked_symbols
        and all(count == 1053 for count in provenance_symbols.values())
    )
    output_is_pipeline_validation_only = (
        report.get("output_is_pipeline_validation_only") is True
        and manifest.get("output_file") == str(output_path)
        and output_validation["pipeline_validation_only_false_count"] == 0
    )
    schema_validated = (
        output_validation["output_schema_validated"] is True
        and schema_report.get("output_schema") == REQUIRED_OUTPUT_FIELDS
        and schema_report.get("pipeline_validation_only") is True
    )
    per_symbol_output_row_count_valid = (
        report.get("per_symbol_output_row_count_valid") is True
        and output_validation["per_symbol_output_row_count_valid"] is True
        and set(per_symbol_rows) == locked_symbols
        and all(row["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H for row in per_symbol_rows.values())
    )

    checks = {
        "artifacts_confirmed": artifacts_confirmed,
        "clean_source_rows_after_policy": clean_source_rows_after_policy == EXPECTED_CLEAN_SOURCE_ROWS,
        "complete_1h_row_count": complete_1h_row_count == EXPECTED_COMPLETE_1H_ROWS,
        "complete_plus_incomplete_equals_total": complete_plus_incomplete_equals_total,
        "expected_head": head == EXPECTED_HEAD,
        "gap_symbol_in_output_count": output_validation["gap_symbol_in_output_count"] == 0,
        "incomplete_1h_row_count": incomplete_1h_row_count == EXPECTED_INCOMPLETE_1H_ROWS,
        "locked_complete_symbols_all_in_output": output_validation["locked_complete_symbols_all_in_output"],
        "no_fill_used": report.get("synthetic_fill_used") is False and report.get("forward_fill_used") is False and report.get("backfill_used") is False,
        "no_readiness_claims": report.get("output_valid_for_research_backtest") is False and report.get("output_valid_for_edge_claim") is False and report.get("broad_acquisition_ready") is False and report.get("source_manifest_acquisition_ready") is False,
        "numeric_sanity_validated": numeric_sanity_validated,
        "output_file_exists": output_file_exists,
        "output_is_pipeline_validation_only": output_is_pipeline_validation_only,
        "output_manifest_exists": output_manifest_exists,
        "output_row_count": output_1h_row_count == EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "output_unique_symbol_hour_count": output_validation["output_unique_symbol_hour_count"] == EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        "policy_effects_match": policy.get("exact_duplicate_rows_dropped") == EXPECTED_EXACT_DUPLICATES and policy.get("material_conflict_rows_quarantined") == EXPECTED_MATERIAL_CONFLICTS,
        "policy_row_count_reconciliation_pass": policy_row_count_reconciliation_pass,
        "provenance_validated": provenance_validated,
        "repo_clean": repo_clean,
        "schema_validated": schema_validated,
        "selected_and_gap_counts": selected_symbol_count == EXPECTED_SELECTED_SYMBOL_COUNT and excluded_gap_symbol_count == EXPECTED_GAP_SYMBOL_COUNT,
        "source_count_values": source_file_count_processed == EXPECTED_TOTAL_SOURCE_FILE_COUNT and raw_source_rows_read == EXPECTED_RAW_SOURCE_ROWS_READ,
        "time_monotonic": output_validation["output_hours_monotonic_by_symbol"],
    }
    replacement_checks_all_true = all(checks.values())
    final_decision = PASS_DECISION if replacement_checks_all_true else FAIL_DECISION
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_FAIL_MODULE
    summary = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": report.get("active_p1_attention_count", 0),
        "aggregation_performed_by_validator": False,
        "all_hours_complete": False,
        "backfill_used": False,
        "broad_acquisition_ready": False,
        "build_execution_artifacts_confirmed": artifacts_confirmed,
        "build_execution_validated": replacement_checks_all_true,
        "clean_source_rows_after_policy": clean_source_rows_after_policy,
        "complete_1h_row_count": complete_1h_row_count,
        "complete_plus_incomplete_equals_total": complete_plus_incomplete_equals_total,
        "current_evidence_chain_quality_after_validator": final_decision if replacement_checks_all_true else "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_VALIDATION_FAILED_REVIEW_REQUIRED",
        "data_build_performed_by_validator": False,
        "data_download_performed_by_validator": False,
        "exact_duplicate_rows_dropped": exact_duplicate_rows_dropped,
        "excluded_gap_symbol_count": excluded_gap_symbol_count,
        "expected_total_output_rows_1h": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "final_decision": final_decision,
        "forward_fill_used": False,
        "gap_symbol_in_output_count": output_validation["gap_symbol_in_output_count"],
        "incomplete_1h_row_count": incomplete_1h_row_count,
        "invalid_numeric_row_count": output_validation["invalid_numeric_row_count"],
        "locked_complete_symbols_all_in_output": output_validation["locked_complete_symbols_all_in_output"],
        "material_conflict_rows_quarantined": material_conflict_rows_quarantined,
        "nan_inf_row_count": output_validation["nan_inf_row_count"],
        "negative_volume_row_count": output_validation["negative_volume_row_count"],
        "next_module": next_module,
        "no_complete_hour_source_row_count_lt_60": output_validation["no_complete_hour_source_row_count_lt_60"],
        "no_incomplete_hour_marked_complete": output_validation["no_incomplete_hour_marked_complete"],
        "numeric_sanity_validated": numeric_sanity_validated,
        "okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_status": PASS_STATUS if replacement_checks_all_true else FAIL_STATUS,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "original_source_full_csv_read_by_validator": False,
        "output_1h_row_count": output_1h_row_count,
        "output_duplicate_symbol_hour_count": output_validation["output_duplicate_symbol_hour_count"],
        "output_file_exists": output_file_exists,
        "output_hours_monotonic_by_symbol": output_validation["output_hours_monotonic_by_symbol"],
        "output_is_pipeline_validation_only": output_is_pipeline_validation_only,
        "output_manifest_exists": output_manifest_exists,
        "output_schema_validated": schema_validated,
        "output_symbol_count": output_validation["output_symbol_count"],
        "output_unique_symbol_hour_count": output_validation["output_unique_symbol_hour_count"],
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": False,
        "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        "policy_row_count_reconciliation_pass": policy_row_count_reconciliation_pass,
        "provenance_validated": provenance_validated,
        "raw_source_rows_read": raw_source_rows_read,
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "selected_symbol_count": selected_symbol_count,
        "source_file_count_processed": source_file_count_processed,
        "source_manifest_acquisition_ready": False,
        "synthetic_fill_used": False,
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validator_p0_count": 0 if replacement_checks_all_true else 1,
        "validator_p1_count": report.get("active_p1_attention_count", 0),
        "created_at_utc": now_utc(),
    }
    return {
        "count_validation": {
            **{key: summary[key] for key in [
                "selected_symbol_count",
                "excluded_gap_symbol_count",
                "expected_total_source_file_count",
                "source_file_count_processed",
                "expected_total_source_rows",
                "raw_source_rows_read",
                "exact_duplicate_rows_dropped",
                "material_conflict_rows_quarantined",
                "clean_source_rows_after_policy",
                "expected_total_output_rows_1h",
                "output_1h_row_count",
                "complete_1h_row_count",
                "incomplete_1h_row_count",
                "complete_plus_incomplete_equals_total",
            ]},
            "per_symbol_totals": per_symbol_totals,
        },
        "key_time_validation": {
            **{key: output_validation[key] for key in [
                "first_hour_values",
                "last_hour_values",
                "output_duplicate_symbol_hour_count",
                "output_hours_monotonic_by_symbol",
                "output_symbol_count",
                "output_unique_symbol_hour_count",
            ]},
            "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        },
        "numeric_validation": {
            "invalid_numeric_row_count": output_validation["invalid_numeric_row_count"],
            "nan_inf_row_count": output_validation["nan_inf_row_count"],
            "negative_volume_row_count": output_validation["negative_volume_row_count"],
            "numeric_sanity_validated": numeric_sanity_validated,
        },
        "policy_validation": {
            "all_hours_complete": False,
            "backfill_used": False,
            "forward_fill_used": False,
            "no_complete_hour_source_row_count_lt_60": output_validation["no_complete_hour_source_row_count_lt_60"],
            "no_incomplete_hour_marked_complete": output_validation["no_incomplete_hour_marked_complete"],
            "policy_row_count_reconciliation_pass": policy_row_count_reconciliation_pass,
            "synthetic_fill_used": False,
        },
        "provenance_validation": {
            "provenance_entry_count": provenance.get("provenance_entry_count"),
            "provenance_symbol_count": len(provenance_symbols),
            "provenance_validated": provenance_validated,
        },
        "schema_validation": {
            "actual_schema": REQUIRED_OUTPUT_FIELDS if schema_validated else None,
            "output_is_pipeline_validation_only": output_is_pipeline_validation_only,
            "output_schema_validated": schema_validated,
            "required_schema": REQUIRED_OUTPUT_FIELDS,
        },
        "summary": summary,
    }


def write_outputs(results: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_report.json", results["summary"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_count_validation.json", results["count_validation"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_validation.json", results["schema_validation"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_key_time_validation.json", results["key_time_validation"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_numeric_sanity_validation.json", results["numeric_validation"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_policy_consistency_validation.json", results["policy_validation"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_provenance_validation.json", results["provenance_validation"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json", results["summary"])


def main() -> int:
    results = build_validation()
    write_outputs(results)
    print(json.dumps(results["summary"], indent=2, sort_keys=True))
    return 0 if results["summary"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
