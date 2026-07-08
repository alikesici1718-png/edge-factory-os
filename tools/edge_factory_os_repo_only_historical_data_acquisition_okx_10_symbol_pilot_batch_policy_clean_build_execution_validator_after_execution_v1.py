from __future__ import annotations

import ast
import csv
import json
import math
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_after_execution_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "4a3e58b"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_EXECUTED_VALIDATOR_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_VALIDATED_PIPELINE_SUMMARY_READY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_VALIDATION_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_after_build_validator_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_validation_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN_BUILD_VALIDATED_PIPELINE_SUMMARY_READY"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
EXECUTION_MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_after_batch_policy_v1"
EXECUTION_DIR = EDGE_LAB_ROOT / EXECUTION_MODULE_NAME

DATE_RANGE_START = "2023-07-01"
DATE_RANGE_END = "2026-05-18"
EXPECTED_OUTPUT_ROWS = 252_720
EXPECTED_COMPLETE_ROWS = 252_710
EXPECTED_INCOMPLETE_ROWS = 10
EXPECTED_AFFECTED_HOURS = 10
EXPECTED_SYMBOL_ROWS = 25_272
EXPECTED_RAW_ROWS = 15_166_462
EXPECTED_EXACT_DUPLICATE_ROWS_DROPPED = 3_252
EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED = 20
EXPECTED_MISSING_MINUTES = 4_800
EXPECTED_CLEAN_SOURCE_ROWS = 15_163_190
EXPECTED_FILE_COUNT_TOTAL = 10_530
EXPECTED_ACTIVE_P1 = 505

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

ARTIFACTS = {
    "execution_summary": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_summary.json",
    "execution_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_report.json",
    "manifest": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_1h_output_manifest.json",
    "exact_duplicate_audit": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_exact_duplicate_drop_audit.json",
    "material_conflict_audit": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_material_conflict_quarantine_audit.json",
    "missing_minute_audit": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_missing_minute_audit.json",
    "incomplete_hour_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_incomplete_hour_report.json",
    "schema_validation_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_schema_validation_report.json",
    "provenance_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_output_provenance_report.json",
    "numeric_sanity_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_numeric_sanity_report.json",
    "compliance_report": EXECUTION_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_compliance_report.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_output_validation_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_per_symbol_validation_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_incomplete_hour_validation_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_numeric_sanity_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_provenance_validation_report.json",
    "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_summary.json",
]


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


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
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_decimal(value: str) -> Decimal | None:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite():
        return None
    return parsed


def parse_bool(value: str) -> bool | None:
    normalized = str(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def read_required_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def output_csv_path_from_manifest(manifest: dict[str, Any]) -> Path:
    output_files = manifest.get("output_files")
    require(isinstance(output_files, list) and len(output_files) == 1, "manifest output_files must contain exactly one output")
    path = Path(str(output_files[0].get("path", "")))
    require(path.exists(), f"output CSV missing: {path}")
    return path


def validate_chain(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any], output_csv: Path) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    execution = artifacts["execution_summary"]
    manifest = artifacts["manifest"]
    compliance = artifacts["compliance_report"]
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": execution.get("historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_status") == PREVIOUS_STATUS,
        "current_next_module_matches": execution.get("next_module") == REQUESTED_MODULE,
        "execution_replacement_checks_true": execution.get("replacement_checks_all_true") is True,
        "output_csv_exists": output_csv.exists(),
        "output_manifest_exists": ARTIFACTS["manifest"].exists(),
        "manifest_row_count_expected": manifest.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS or manifest.get("output_files", [{}])[0].get("row_count") == EXPECTED_OUTPUT_ROWS,
        "execution_counts_expected": (
            execution.get("output_1h_row_count") == EXPECTED_OUTPUT_ROWS
            and execution.get("complete_1h_row_count") == EXPECTED_COMPLETE_ROWS
            and execution.get("incomplete_1h_row_count") == EXPECTED_INCOMPLETE_ROWS
            and execution.get("affected_hour_count") == EXPECTED_AFFECTED_HOURS
            and execution.get("total_exact_duplicate_rows_dropped") == EXPECTED_EXACT_DUPLICATE_ROWS_DROPPED
            and execution.get("total_material_conflict_rows_quarantined") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED
            and execution.get("total_missing_minute_count") == EXPECTED_MISSING_MINUTES
            and execution.get("clean_source_rows_after_policy") == EXPECTED_CLEAN_SOURCE_ROWS
        ),
        "execution_safety_flags": (
            execution.get("synthetic_fill_used") is False
            and execution.get("forward_fill_used") is False
            and execution.get("backfill_used") is False
            and execution.get("output_valid_for_research_backtest") is False
            and execution.get("output_valid_for_edge_claim") is False
            and execution.get("safe_for_full_universe_acquisition") is False
            and execution.get("broad_acquisition_ready") is False
        ),
        "compliance_no_forbidden_actions": (
            compliance.get("new_download_performed_now") is False
            and compliance.get("okx_api_call_performed") is False
            and compliance.get("okx_browse_performed") is False
            and compliance.get("research_backtest_edge_claim_made") is False
            and compliance.get("full_universe_ready_claim_made") is False
            and compliance.get("broad_acquisition_ready_claim_made") is False
        ),
    }
    return {"head": head, "checks": checks}


def validate_output_csv(output_csv: Path) -> dict[str, Any]:
    row_count = 0
    symbol_counts: dict[str, int] = defaultdict(int)
    incomplete_counts: dict[str, int] = defaultdict(int)
    seen_symbol_hours: set[tuple[str, int]] = set()
    duplicate_symbol_hour_count = 0
    previous_hour_by_symbol: dict[str, int] = {}
    monotonic = True
    complete_count = 0
    incomplete_count = 0
    any_incomplete_hour_marked_complete = False
    any_complete_hour_source_row_count_lt_60 = False
    invalid_numeric_row_count = 0
    negative_volume_row_count = 0
    nan_inf_row_count = 0
    provenance_missing_count = 0
    invalid_schema = False
    invalid_symbol_count = 0
    incomplete_samples: list[dict[str, Any]] = []
    numeric_samples: list[dict[str, Any]] = []
    provenance_samples: list[dict[str, Any]] = []

    with output_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        invalid_schema = reader.fieldnames != OUTPUT_SCHEMA
        for row in reader:
            row_count += 1
            symbol = row.get("instrument_name", "")
            if symbol not in PILOT_SYMBOLS:
                invalid_symbol_count += 1
            try:
                hour_start = int(row.get("hour_start_epoch_ms", ""))
                source_row_count = int(row.get("source_row_count", ""))
            except ValueError:
                invalid_numeric_row_count += 1
                continue
            symbol_counts[symbol] += 1
            key = (symbol, hour_start)
            if key in seen_symbol_hours:
                duplicate_symbol_hour_count += 1
            seen_symbol_hours.add(key)
            if symbol in previous_hour_by_symbol and hour_start <= previous_hour_by_symbol[symbol]:
                monotonic = False
            previous_hour_by_symbol[symbol] = hour_start

            complete = parse_bool(row.get("complete_hour", ""))
            if complete is True:
                complete_count += 1
                if source_row_count < 60:
                    any_complete_hour_source_row_count_lt_60 = True
            elif complete is False:
                incomplete_count += 1
                incomplete_counts[symbol] += 1
                if len(incomplete_samples) < 50:
                    incomplete_samples.append(
                        {
                            "symbol": symbol,
                            "hour_start_epoch_ms": hour_start,
                            "source_row_count": source_row_count,
                            "complete_hour": row.get("complete_hour"),
                            "incomplete_reason": row.get("incomplete_reason"),
                        }
                    )
            else:
                invalid_numeric_row_count += 1
            if complete is True and source_row_count < 60:
                any_incomplete_hour_marked_complete = True

            decimals = {name: parse_decimal(row.get(name, "")) for name in ["open", "high", "low", "close", "vol", "vol_ccy", "vol_quote"]}
            if any(value is None for value in decimals.values()):
                invalid_numeric_row_count += 1
                nan_inf_row_count += 1
                if len(numeric_samples) < 25:
                    numeric_samples.append({"row_number": row_count, "symbol": symbol, "issue": "invalid_decimal"})
                continue
            open_value = decimals["open"]
            high_value = decimals["high"]
            low_value = decimals["low"]
            close_value = decimals["close"]
            assert open_value is not None and high_value is not None and low_value is not None and close_value is not None
            if high_value < open_value or high_value < close_value or high_value < low_value or low_value > open_value or low_value > close_value or low_value > high_value:
                invalid_numeric_row_count += 1
                if len(numeric_samples) < 25:
                    numeric_samples.append({"row_number": row_count, "symbol": symbol, "issue": "ohlc_bounds"})
            for name in ["vol", "vol_ccy", "vol_quote"]:
                value = decimals[name]
                assert value is not None
                if value < 0:
                    negative_volume_row_count += 1
                    if len(numeric_samples) < 25:
                        numeric_samples.append({"row_number": row_count, "symbol": symbol, "issue": f"negative_{name}"})

            required_present = [
                "source_zip_sha256",
                "source_csv_file",
                "source_date",
                "build_scope",
                "policy_clean_build",
            ]
            if any(not str(row.get(name, "")).strip() for name in required_present):
                provenance_missing_count += 1
                if len(provenance_samples) < 25:
                    provenance_samples.append({"row_number": row_count, "symbol": symbol, "issue": "missing_required_provenance"})
            if row.get("build_scope") != "OKX_10_SYMBOL_PILOT_BATCH_POLICY_CLEAN" or row.get("policy_clean_build") != "true":
                provenance_missing_count += 1
                if len(provenance_samples) < 25:
                    provenance_samples.append({"row_number": row_count, "symbol": symbol, "issue": "invalid_build_scope_or_policy"})

    per_symbol_output_row_count_valid = all(symbol_counts.get(symbol, 0) == EXPECTED_SYMBOL_ROWS for symbol in PILOT_SYMBOLS)
    every_symbol_has_one_incomplete_hour = all(incomplete_counts.get(symbol, 0) == 1 for symbol in PILOT_SYMBOLS)
    return {
        "output_1h_row_count": row_count,
        "output_symbol_count": len([symbol for symbol in PILOT_SYMBOLS if symbol_counts.get(symbol, 0) > 0]),
        "per_symbol_output_row_count_valid": per_symbol_output_row_count_valid,
        "output_unique_symbol_hour_count": len(seen_symbol_hours),
        "output_duplicate_symbol_hour_count": duplicate_symbol_hour_count,
        "output_hours_monotonic_by_symbol": monotonic,
        "complete_1h_row_count": complete_count,
        "incomplete_1h_row_count": incomplete_count,
        "affected_hour_count": incomplete_count,
        "all_symbols_complete": incomplete_count == 0,
        "every_symbol_has_one_incomplete_hour": every_symbol_has_one_incomplete_hour,
        "any_incomplete_hour_marked_complete": any_incomplete_hour_marked_complete,
        "any_complete_hour_source_row_count_lt_60": any_complete_hour_source_row_count_lt_60,
        "invalid_schema": invalid_schema,
        "invalid_symbol_count": invalid_symbol_count,
        "invalid_numeric_row_count": invalid_numeric_row_count,
        "negative_volume_row_count": negative_volume_row_count,
        "nan_inf_row_count": nan_inf_row_count,
        "provenance_missing_count": provenance_missing_count,
        "numeric_sanity_validated": invalid_numeric_row_count == 0 and negative_volume_row_count == 0 and nan_inf_row_count == 0,
        "provenance_validated": provenance_missing_count == 0,
        "symbol_counts": dict(symbol_counts),
        "incomplete_counts": dict(incomplete_counts),
        "incomplete_hour_samples": incomplete_samples,
        "numeric_issue_samples": numeric_samples,
        "provenance_issue_samples": provenance_samples,
    }


def summarize(
    artifacts: dict[str, dict[str, Any]],
    chain: dict[str, Any],
    output_validation: dict[str, Any],
    py_state: dict[str, Any],
) -> dict[str, Any]:
    execution = artifacts["execution_summary"]
    exact = artifacts["exact_duplicate_audit"]
    material = artifacts["material_conflict_audit"]
    missing = artifacts["missing_minute_audit"]
    compliance = artifacts["compliance_report"]
    replacement_checks = {
        **chain["checks"],
        "output_schema_valid": output_validation["invalid_schema"] is False,
        "output_row_count_expected": output_validation["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS,
        "output_symbol_count_expected": output_validation["output_symbol_count"] == 10,
        "all_pilot_symbols_present": set(output_validation["symbol_counts"]) == set(PILOT_SYMBOLS),
        "per_symbol_rows_expected": output_validation["per_symbol_output_row_count_valid"] is True,
        "unique_symbol_hour_count_expected": output_validation["output_unique_symbol_hour_count"] == EXPECTED_OUTPUT_ROWS,
        "duplicate_symbol_hour_zero": output_validation["output_duplicate_symbol_hour_count"] == 0,
        "hours_monotonic": output_validation["output_hours_monotonic_by_symbol"] is True,
        "complete_hour_count_expected": output_validation["complete_1h_row_count"] == EXPECTED_COMPLETE_ROWS,
        "incomplete_hour_count_expected": output_validation["incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_ROWS,
        "affected_hour_count_expected": output_validation["affected_hour_count"] == EXPECTED_AFFECTED_HOURS,
        "all_symbols_complete_false": output_validation["all_symbols_complete"] is False,
        "every_symbol_has_one_incomplete_hour": output_validation["every_symbol_has_one_incomplete_hour"] is True,
        "no_incomplete_hour_marked_complete": output_validation["any_incomplete_hour_marked_complete"] is False,
        "no_complete_hour_source_count_lt_60": output_validation["any_complete_hour_source_row_count_lt_60"] is False,
        "exact_duplicate_drop_count_expected": exact.get("total_exact_duplicate_rows_dropped") == EXPECTED_EXACT_DUPLICATE_ROWS_DROPPED,
        "material_quarantine_count_expected": material.get("total_material_conflict_rows_quarantined") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "missing_minute_count_expected": missing.get("total_missing_minute_count") == EXPECTED_MISSING_MINUTES,
        "clean_source_rows_expected": execution.get("clean_source_rows_after_policy") == EXPECTED_CLEAN_SOURCE_ROWS,
        "no_fill_used": execution.get("synthetic_fill_used") is False and execution.get("forward_fill_used") is False and execution.get("backfill_used") is False,
        "numeric_sanity_validated": output_validation["numeric_sanity_validated"] is True,
        "provenance_validated": output_validation["provenance_validated"] is True,
        "pipeline_validation_only": execution.get("output_is_batch_policy_clean_pipeline_validation_only") is True,
        "no_research_edge_universe_claim": (
            execution.get("output_valid_for_research_backtest") is False
            and execution.get("output_valid_for_edge_claim") is False
            and execution.get("safe_for_full_universe_acquisition") is False
            and execution.get("broad_acquisition_ready") is False
        ),
        "validator_no_forbidden_actions": (
            compliance.get("new_download_performed_now") is False
            and compliance.get("okx_api_call_performed") is False
            and compliance.get("okx_browse_performed") is False
        ),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    return {
        "historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_status": status,
        "batch_policy_clean_build_execution_validated": replacement_checks_all_true,
        "pilot_symbol_count": 10,
        "output_csv_exists": True,
        "output_manifest_exists": True,
        "output_1h_row_count": output_validation["output_1h_row_count"],
        "output_symbol_count": output_validation["output_symbol_count"],
        "per_symbol_output_row_count_valid": output_validation["per_symbol_output_row_count_valid"],
        "output_unique_symbol_hour_count": output_validation["output_unique_symbol_hour_count"],
        "output_duplicate_symbol_hour_count": output_validation["output_duplicate_symbol_hour_count"],
        "output_hours_monotonic_by_symbol": output_validation["output_hours_monotonic_by_symbol"],
        "complete_1h_row_count": output_validation["complete_1h_row_count"],
        "incomplete_1h_row_count": output_validation["incomplete_1h_row_count"],
        "affected_hour_count": output_validation["affected_hour_count"],
        "all_symbols_complete": output_validation["all_symbols_complete"],
        "every_symbol_has_one_incomplete_hour": output_validation["every_symbol_has_one_incomplete_hour"],
        "any_incomplete_hour_marked_complete": output_validation["any_incomplete_hour_marked_complete"],
        "any_complete_hour_source_row_count_lt_60": output_validation["any_complete_hour_source_row_count_lt_60"],
        "total_exact_duplicate_rows_dropped": exact.get("total_exact_duplicate_rows_dropped"),
        "total_material_conflict_rows_quarantined": material.get("total_material_conflict_rows_quarantined"),
        "total_missing_minute_count": missing.get("total_missing_minute_count"),
        "clean_source_rows_after_policy": execution.get("clean_source_rows_after_policy"),
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "numeric_sanity_validated": output_validation["numeric_sanity_validated"],
        "invalid_numeric_row_count": output_validation["invalid_numeric_row_count"],
        "negative_volume_row_count": output_validation["negative_volume_row_count"],
        "nan_inf_row_count": output_validation["nan_inf_row_count"],
        "provenance_validated": output_validation["provenance_validated"],
        "output_is_batch_policy_clean_pipeline_validation_only": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "no_new_download": True,
        "new_download_performed_by_validator": False,
        "data_build_performed_by_validator": False,
        "aggregation_performed_by_validator": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "validator_p0_count": 0 if replacement_checks_all_true else 1,
        "validator_p1_count": EXPECTED_ACTIVE_P1,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": EXPECTED_ACTIVE_P1,
        "current_evidence_chain_quality_after_validator": AFTER_QUALITY if replacement_checks_all_true else "BATCH_POLICY_CLEAN_BUILD_VALIDATION_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def write_reports(summary: dict[str, Any], output_validation: dict[str, Any]) -> None:
    validator = {
        **summary,
        "artifact_type": "validator",
        "validator_performed_no_new_download_api_browse_build_aggregation": True,
    }
    output_report = {
        **summary,
        "artifact_type": "output_validation_report",
        "schema": OUTPUT_SCHEMA,
        "symbol_counts": output_validation["symbol_counts"],
    }
    per_symbol_report = {
        **summary,
        "artifact_type": "per_symbol_validation_report",
        "per_symbol": [
            {
                "symbol": symbol,
                "output_row_count": output_validation["symbol_counts"].get(symbol, 0),
                "incomplete_hour_count": output_validation["incomplete_counts"].get(symbol, 0),
                "row_count_valid": output_validation["symbol_counts"].get(symbol, 0) == EXPECTED_SYMBOL_ROWS,
                "has_one_incomplete_hour": output_validation["incomplete_counts"].get(symbol, 0) == 1,
            }
            for symbol in PILOT_SYMBOLS
        ],
    }
    incomplete_report = {
        **summary,
        "artifact_type": "incomplete_hour_validation_report",
        "samples": output_validation["incomplete_hour_samples"],
    }
    numeric_report = {
        **summary,
        "artifact_type": "numeric_sanity_report",
        "numeric_issue_samples": output_validation["numeric_issue_samples"],
    }
    provenance_report = {
        **summary,
        "artifact_type": "provenance_validation_report",
        "provenance_missing_count": output_validation["provenance_missing_count"],
        "provenance_issue_samples": output_validation["provenance_issue_samples"],
    }
    files = {
        "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator.json": validator,
        "historical_okx_10_symbol_pilot_batch_policy_clean_output_validation_report.json": output_report,
        "historical_okx_10_symbol_pilot_batch_policy_clean_per_symbol_validation_report.json": per_symbol_report,
        "historical_okx_10_symbol_pilot_batch_policy_clean_incomplete_hour_validation_report.json": incomplete_report,
        "historical_okx_10_symbol_pilot_batch_policy_clean_numeric_sanity_report.json": numeric_report,
        "historical_okx_10_symbol_pilot_batch_policy_clean_provenance_validation_report.json": provenance_report,
        "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_summary.json": summary,
    }
    for name, payload in files.items():
        write_json(OUTPUT_DIR / name, payload)


def run_validator() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_required_artifacts()
    manifest = artifacts["manifest"]
    output_csv = output_csv_path_from_manifest(manifest)
    chain = validate_chain(artifacts, py_state, output_csv)
    require(all(chain["checks"].values()), f"chain validation failed: {chain['checks']}")
    output_validation = validate_output_csv(output_csv)
    summary = summarize(artifacts, chain, output_validation, py_state)
    write_reports(summary, output_validation)
    missing_outputs = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing_outputs, f"missing validator outputs: {missing_outputs}")
    require(summary["replacement_checks_all_true"] is True, "replacement checks did not all pass")
    return summary


def main() -> int:
    try:
        summary = run_validator()
    except Exception as exc:
        blocked = {
            "historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_status": BLOCKED_STATUS,
            "batch_policy_clean_build_execution_validated": False,
            "blocked_reason": repr(exc),
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "new_download_performed_by_validator": False,
            "data_build_performed_by_validator": False,
            "aggregation_performed_by_validator": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "created_at_utc": utc_now(),
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_build_execution_validator_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
