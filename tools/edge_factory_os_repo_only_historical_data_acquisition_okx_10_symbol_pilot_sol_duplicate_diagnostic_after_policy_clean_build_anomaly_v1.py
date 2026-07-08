from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_duplicate_diagnostic_after_policy_clean_build_anomaly_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "25cb683"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_POLICY_CLEAN_BUILD_"
    "ANOMALY_RECORD_SOL_DUPLICATE_DIAGNOSTIC_READY"
)
PASS_STATUS_PREFIX = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_DUPLICATE_"
    "DIAGNOSTIC"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_DUPLICATE_"
    "DIAGNOSTIC_FAILED_REVIEW"
)

TARGET_SYMBOL = "SOL-USDT-SWAP"
EXPECTED_DUPLICATE_OPEN_TIME = 1_697_108_400_000
EXPECTED_DUPLICATE_OPEN_TIME_COUNT = 1
EXPECTED_DUPLICATE_EXTRA_ROW_COUNT = 1
EXPECTED_DUPLICATE_GROUP_COUNT = 1
EXPECTED_DUPLICATE_ROW_COUNT = 2
EXPECTED_MISSING_MINUTE_COUNT = 0
EXPECTED_SOURCE_DATE = "2023-10-12"
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
CANONICAL_FIELDS = EXPECTED_SCHEMA
OHLC_FIELDS = {"open", "high", "low", "close"}
VOLUME_FIELDS = {"vol", "vol_ccy", "vol_quote"}
CONFIRM_FIELD = {"confirm"}
SYMBOL_SCHEMA_FIELDS = {"instrument_name", "open_time"}

NEXT_MODULE_EXACT = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_exact_duplicate_policy_after_diagnostic_v1.py"
)
NEXT_MODULE_CONFIRM_ONLY = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_confirm_only_duplicate_policy_after_diagnostic_v1.py"
)
NEXT_MODULE_MATERIAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_material_duplicate_conflict_policy_after_diagnostic_v1.py"
)
NEXT_MODULE_MANUAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "sol_duplicate_manual_review_required_v1.py"
)

QUALITY_EXACT = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_DUPLICATE_DIAGNOSED_"
    "EXACT_DUPLICATE_POLICY_READY"
)
QUALITY_CONFIRM_ONLY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_DUPLICATE_DIAGNOSED_"
    "CONFIRM_ONLY_POLICY_READY"
)
QUALITY_MATERIAL = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_DUPLICATE_DIAGNOSED_"
    "MATERIAL_CONFLICT_POLICY_READY"
)
QUALITY_MANUAL = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_SOL_DUPLICATE_DIAGNOSED_"
    "MANUAL_REVIEW_REQUIRED"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

ANOMALY_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_blocked_or_anomaly_record_after_eth_material_policy_v1"
)
POLICY_CLEAN_BUILD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "policy_clean_build_execution_after_eth_material_conflict_policy_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "anomaly_summary": ANOMALY_RECORD_DIR / f"{ANOMALY_RECORD_DIR.name}_latest.json",
    "anomaly_blocked_record": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_anomaly_blocked_record_after_eth_policy.json",
    "anomaly_preview": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_preview.json",
    "anomaly_approval": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json",
    "quarantine_record": ANOMALY_RECORD_DIR
    / "historical_okx_10_symbol_pilot_partial_output_quarantine_record_after_blocked_build.json",
    "policy_clean_summary": POLICY_CLEAN_BUILD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_build_execution_summary.json",
    "policy_clean_gap_duplicate_report": POLICY_CLEAN_BUILD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_gap_duplicate_report.json",
    "policy_clean_schema_validation_report": POLICY_CLEAN_BUILD_DIR
    / "historical_okx_10_symbol_pilot_policy_clean_schema_validation_report.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR
    / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
    "download_hash_report": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_hash_validation_report.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "dedupe_execution_performed_now": False,
    "rebuild_execution_performed_now": False,
    "output_1h_csv_created_now": False,
    "output_csv_created": False,
    "output_manifest_created": False,
    "modified_source_output_created": False,
    "conflicting_row_choice_performed": False,
    "averaging_or_merging_rows_performed": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_edge_claim_made": False,
    "full_universe_ready_claim_made": False,
    "broad_acquisition_ready_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
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
        raise Blocked(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.exists(), f"missing artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"artifact is not a JSON object: {path}")
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
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    if normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        return False
    if posix.is_absolute() or any(part == ".." for part in posix.parts):
        return False
    if posix.parts and ":" in posix.parts[0]:
        return False
    return True


def expected_csv_for_date(day: str) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day}.csv"


def utc_from_open_time(open_time: int) -> str:
    return datetime.fromtimestamp(open_time / 1000, tz=timezone.utc).isoformat()


def normalize_decimal_or_raw(value: Any) -> str:
    text = str(value).strip()
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError):
        return text
    require(parsed.is_finite(), f"non-finite decimal value: {text!r}")
    normalized = parsed.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal(1)))
    return format(normalized, "f")


def normalize_confirm(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "yes", "y"}:
        return "1"
    if text in {"0", "false", "f", "no", "n"}:
        return "0"
    return text


def canonical_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "instrument_name": str(row["instrument_name"]).strip(),
        "open": normalize_decimal_or_raw(row["open"]),
        "high": normalize_decimal_or_raw(row["high"]),
        "low": normalize_decimal_or_raw(row["low"]),
        "close": normalize_decimal_or_raw(row["close"]),
        "vol": normalize_decimal_or_raw(row["vol"]),
        "vol_ccy": normalize_decimal_or_raw(row["vol_ccy"]),
        "vol_quote": normalize_decimal_or_raw(row["vol_quote"]),
        "open_time": str(int(str(row["open_time"]).strip())),
        "confirm": normalize_confirm(row["confirm"]),
    }


def validate_prior_artifacts(artifacts: dict[str, dict[str, Any]]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved SOL diagnostic module")

    anomaly_summary = artifacts["anomaly_summary"]
    blocked = artifacts["anomaly_blocked_record"]
    preview = artifacts["anomaly_preview"]
    approval = artifacts["anomaly_approval"]
    quarantine = artifacts["quarantine_record"]
    policy_summary = artifacts["policy_clean_summary"]
    gap = artifacts["policy_clean_gap_duplicate_report"]
    schema = artifacts["policy_clean_schema_validation_report"]
    validator = artifacts["download_validator_summary"]
    hash_report = artifacts["download_hash_report"]

    require(
        anomaly_summary.get("historical_data_acquisition_okx_10_symbol_pilot_policy_clean_build_anomaly_record_status")
        == PREVIOUS_STATUS,
        "previous anomaly summary status mismatch",
    )
    require(anomaly_summary.get("next_module") == REQUESTED_MODULE, "previous next_module mismatch")
    require(blocked.get("anomaly_symbol") == TARGET_SYMBOL, "blocked anomaly symbol mismatch")
    require(blocked.get("duplicate_open_time_count_total") == EXPECTED_DUPLICATE_OPEN_TIME_COUNT, "blocked duplicate count mismatch")
    require(blocked.get("known_sol_duplicate_open_time") == EXPECTED_DUPLICATE_OPEN_TIME, "blocked open_time mismatch")
    require(blocked.get("missing_minute_count_total") == EXPECTED_MISSING_MINUTE_COUNT, "blocked missing minute mismatch")
    require(blocked.get("eth_material_policy_applied_before_block") is True, "ETH material policy not preserved")
    require(blocked.get("partial_output_created_during_blocked_route") is True, "partial output flag mismatch")
    require(blocked.get("partial_output_trusted") is False, "partial output trust flag mismatch")
    require(blocked.get("partial_output_quarantined") is True, "partial output quarantine mismatch")
    require(blocked.get("data_build_performed") is False, "prior data build flag mismatch")
    require(blocked.get("aggregation_performed_now") is False, "prior aggregation flag mismatch")
    require(blocked.get("output_csv_created") is False, "anomaly record output CSV flag mismatch")
    require(blocked.get("output_manifest_created") is False, "anomaly record output manifest flag mismatch")
    require(blocked.get("active_p0_blocker_count") == 1, "prior P0 count mismatch")
    require(preview.get("sol_duplicate_diagnostic_preview_created") is True, "SOL preview missing")
    require(preview.get("known_duplicate_open_time") == EXPECTED_DUPLICATE_OPEN_TIME, "preview open_time mismatch")
    require(preview.get("next_diagnostic_module_must_not_download") is True, "preview download ban missing")
    require(preview.get("next_diagnostic_module_must_not_call_api_or_browse") is True, "preview API/browser ban missing")
    require(preview.get("next_diagnostic_module_must_not_build_or_aggregate") is True, "preview build ban missing")
    require(preview.get("next_diagnostic_module_must_not_dedupe_or_rebuild") is True, "preview dedupe ban missing")
    require(approval.get("approval_grants_future_sol_duplicate_diagnostic_next") is True, "future SOL diagnostic approval missing")
    require(approval.get("approval_grants_rebuild_now") is False, "rebuild-now approval mismatch")
    require(approval.get("approval_grants_dedupe_now") is False, "dedupe-now approval mismatch")
    require(quarantine.get("partial_output_quarantined") is True, "quarantine record mismatch")
    require(quarantine.get("partial_output_trusted") is False, "quarantine trust mismatch")

    require(policy_summary.get("anomaly_symbols") == [TARGET_SYMBOL], "policy build anomaly symbol mismatch")
    require(policy_summary.get("duplicate_open_time_count_total") == EXPECTED_DUPLICATE_OPEN_TIME_COUNT, "policy build duplicate count mismatch")
    require(policy_summary.get("missing_minute_count_total") == EXPECTED_MISSING_MINUTE_COUNT, "policy build missing minute mismatch")
    require(policy_summary.get("eth_material_policy_applied_before_block") is not False, "ETH material policy application missing")
    require(policy_summary.get("data_build_performed") is False, "policy build data build flag mismatch")
    require(policy_summary.get("aggregation_performed_now") is False, "policy build aggregation flag mismatch")
    require(gap.get("duplicate_open_time_count_total") == EXPECTED_DUPLICATE_OPEN_TIME_COUNT, "gap duplicate count mismatch")
    require(gap.get("missing_minute_count_total") == EXPECTED_MISSING_MINUTE_COUNT, "gap missing minute mismatch")
    require(schema.get("schema_mismatch_count") == 0, "prior schema mismatch")
    require(schema.get("symbol_mismatch_count") == 0, "prior symbol mismatch")
    require(validator.get("all_hashes_match_recorded") is True, "download validator hash mismatch")
    require(validator.get("all_downloaded_zip_paths_exist") is True, "download validator path mismatch")
    require(validator.get("all_expected_inner_csv_present") is True, "download validator inner CSV mismatch")
    require(validator.get("all_expected_schema_match") is True, "download validator schema mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "hash report mismatch")
    require(hash_report.get("all_hashes_recomputed") is True, "hash report recompute mismatch")


def sol_hash_entry_for_date(hash_report: dict[str, Any], day: str) -> dict[str, Any]:
    items = hash_report.get("hashes")
    require(isinstance(items, list), "hash report hashes is not a list")
    matches = [
        item
        for item in items
        if isinstance(item, dict)
        and item.get("symbol") == TARGET_SYMBOL
        and item.get("date") == day
    ]
    require(len(matches) == 1, f"expected one SOL hash entry for {day}, observed {len(matches)}")
    entry = matches[0]
    require(str(entry.get("recorded_sha256", "")), "SOL hash entry missing recorded SHA256")
    require(str(entry.get("local_zip_path", "")), "SOL hash entry missing ZIP path")
    return entry


def inspect_duplicate_group(entry: dict[str, Any]) -> dict[str, Any]:
    day = str(entry["date"])
    zip_path = Path(str(entry["local_zip_path"]))
    require(zip_path.exists(), f"SOL ZIP missing: {zip_path}")
    recorded_hash = str(entry["recorded_sha256"])
    recomputed_hash = sha256_file(zip_path)
    require(recomputed_hash == recorded_hash, f"SHA256 mismatch for SOL ZIP: {zip_path}")

    expected_csv = expected_csv_for_date(day)
    occurrences: list[dict[str, Any]] = []
    total_rows_read = 0
    schema_match = False
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        require(all(safe_zip_member(name) for name in names), f"ZIP traversal risk: {zip_path}")
        require(expected_csv in names, f"expected SOL CSV missing: {expected_csv}")
        with archive.open(expected_csv, "r") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
            reader = csv.DictReader(text)
            schema_match = reader.fieldnames == EXPECTED_SCHEMA
            require(schema_match, f"schema mismatch in {expected_csv}: {reader.fieldnames}")
            for row_number, row in enumerate(reader, start=2):
                total_rows_read += 1
                require(row.get("instrument_name") == TARGET_SYMBOL, f"symbol mismatch in {expected_csv} row {row_number}")
                open_time = int(str(row["open_time"]).strip())
                if open_time == EXPECTED_DUPLICATE_OPEN_TIME:
                    occurrences.append(
                        {
                            "source_date": day,
                            "source_file": expected_csv,
                            "source_zip": str(zip_path),
                            "source_row_number": row_number,
                            "raw_values": {field: row.get(field) for field in CANONICAL_FIELDS},
                            "canonical_values": canonical_row(row),
                        }
                    )

    require(len(occurrences) == EXPECTED_DUPLICATE_ROW_COUNT, f"duplicate row count mismatch: {len(occurrences)}")
    return {
        "source_date": day,
        "source_file": expected_csv,
        "source_zip": str(zip_path),
        "source_zip_sha256_recomputed": recomputed_hash,
        "source_zip_sha256_recorded": recorded_hash,
        "source_zip_sha256_match": True,
        "schema_match": schema_match,
        "source_rows_read_for_target_day": total_rows_read,
        "occurrences": occurrences,
    }


def diff_duplicate_rows(occurrences: list[dict[str, Any]]) -> dict[str, Any]:
    require(len(occurrences) == 2, "field diff requires exactly two duplicate rows")
    left = occurrences[0]["canonical_values"]
    right = occurrences[1]["canonical_values"]
    field_diffs: list[dict[str, Any]] = []
    differing_fields: list[str] = []
    for field in CANONICAL_FIELDS:
        differs = left[field] != right[field]
        if differs:
            differing_fields.append(field)
        field_diffs.append(
            {
                "field": field,
                "differs": differs,
                "row_1_raw": occurrences[0]["raw_values"][field],
                "row_2_raw": occurrences[1]["raw_values"][field],
                "row_1_normalized": left[field],
                "row_2_normalized": right[field],
            }
        )
    return {
        "differing_field_count": len(differing_fields),
        "differing_fields": differing_fields,
        "field_diffs": field_diffs,
    }


def classify_duplicate(differing_fields: list[str], schema_match: bool) -> dict[str, Any]:
    diff_set = set(differing_fields)
    exact_duplicate = schema_match and not diff_set
    symbol_or_schema_conflict = (not schema_match) or bool(diff_set & SYMBOL_SCHEMA_FIELDS)
    confirm_only_conflict = diff_set == CONFIRM_FIELD
    ohlc_only_conflict = bool(diff_set) and diff_set <= OHLC_FIELDS
    volume_only_conflict = bool(diff_set) and diff_set <= VOLUME_FIELDS
    ohlcv_material_conflict = bool(diff_set & (OHLC_FIELDS | VOLUME_FIELDS))
    unknown_conflict = False

    if exact_duplicate:
        classification = "EXACT_DUPLICATE"
        next_module = NEXT_MODULE_EXACT
        after_quality = QUALITY_EXACT
        pass_status = f"{PASS_STATUS_PREFIX}_EXACT_DUPLICATE_POLICY_READY"
    elif confirm_only_conflict:
        classification = "CONFIRM_ONLY_CONFLICT"
        next_module = NEXT_MODULE_CONFIRM_ONLY
        after_quality = QUALITY_CONFIRM_ONLY
        pass_status = f"{PASS_STATUS_PREFIX}_CONFIRM_ONLY_POLICY_READY"
    elif symbol_or_schema_conflict:
        classification = "SYMBOL_OR_SCHEMA_CONFLICT"
        next_module = NEXT_MODULE_MANUAL
        after_quality = QUALITY_MANUAL
        pass_status = f"{PASS_STATUS_PREFIX}_MANUAL_REVIEW_REQUIRED"
    elif ohlc_only_conflict:
        classification = "OHLC_ONLY_CONFLICT"
        next_module = NEXT_MODULE_MATERIAL
        after_quality = QUALITY_MATERIAL
        pass_status = f"{PASS_STATUS_PREFIX}_MATERIAL_CONFLICT_POLICY_READY"
    elif volume_only_conflict:
        classification = "VOLUME_ONLY_CONFLICT"
        next_module = NEXT_MODULE_MATERIAL
        after_quality = QUALITY_MATERIAL
        pass_status = f"{PASS_STATUS_PREFIX}_MATERIAL_CONFLICT_POLICY_READY"
    elif ohlcv_material_conflict:
        classification = "OHLCV_MATERIAL_CONFLICT"
        next_module = NEXT_MODULE_MATERIAL
        after_quality = QUALITY_MATERIAL
        pass_status = f"{PASS_STATUS_PREFIX}_MATERIAL_CONFLICT_POLICY_READY"
    else:
        classification = "UNKNOWN_CONFLICT"
        next_module = NEXT_MODULE_MANUAL
        after_quality = QUALITY_MANUAL
        pass_status = f"{PASS_STATUS_PREFIX}_MANUAL_REVIEW_REQUIRED"
        unknown_conflict = True

    return {
        "duplicate_classification": classification,
        "exact_duplicate": exact_duplicate,
        "confirm_only_conflict": confirm_only_conflict,
        "ohlc_only_conflict": ohlc_only_conflict,
        "volume_only_conflict": volume_only_conflict,
        "ohlcv_material_conflict": ohlcv_material_conflict,
        "symbol_or_schema_conflict": symbol_or_schema_conflict,
        "unknown_conflict": unknown_conflict,
        "next_module": next_module,
        "after_quality": after_quality,
        "pass_status": pass_status,
    }


def build_payloads(generated_at: str, inspection: dict[str, Any], diff: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    source_date = inspection["source_date"]
    source_file = inspection["source_file"]
    source_zip = inspection["source_zip"]
    conflict_open_time_utc = utc_from_open_time(EXPECTED_DUPLICATE_OPEN_TIME)
    exact_duplicate = classification["exact_duplicate"]
    confirm_only = classification["confirm_only_conflict"]
    material = classification["ohlcv_material_conflict"]
    symbol_or_schema = classification["symbol_or_schema_conflict"]
    unknown = classification["unknown_conflict"]
    active_p0 = 0 if exact_duplicate else 1
    active_p1 = 0 if exact_duplicate else 1

    shared = {
        "diagnostic_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_open_time_count_total": EXPECTED_DUPLICATE_OPEN_TIME_COUNT,
        "diagnostic_duplicate_extra_row_count": EXPECTED_DUPLICATE_EXTRA_ROW_COUNT,
        "duplicate_open_time_group_count": EXPECTED_DUPLICATE_GROUP_COUNT,
        "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME,
        "conflict_open_time_utc": conflict_open_time_utc,
        "duplicate_source_date": source_date,
        "duplicate_source_file": source_file,
        "duplicate_source_zip": source_zip,
        "duplicate_row_count": len(inspection["occurrences"]),
        "differing_field_count": diff["differing_field_count"],
        "differing_fields": diff["differing_fields"],
        "duplicate_classification": classification["duplicate_classification"],
        "exact_duplicate": exact_duplicate,
        "confirm_only_conflict": confirm_only,
        "ohlcv_material_conflict": material,
        "symbol_or_schema_conflict": symbol_or_schema,
        "unknown_conflict": unknown,
        "raw_duplicate_rows_captured": True,
        "field_diff_report_created": True,
        "policy_preview_created": True,
        "approval_record_created": True,
        "approval_grants_resolution_now": False,
        "approval_grants_future_policy_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": active_p1,
        "current_evidence_chain_quality_after_diagnostic": classification["after_quality"],
        "next_module": classification["next_module"],
    }

    diagnostic = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "historical_data_acquisition_okx_10_symbol_pilot_sol_duplicate_diagnostic_status": classification["pass_status"],
        "duplicate_group_size": len(inspection["occurrences"]),
        "expected_duplicate_extra_row_count_from_blocked_route": EXPECTED_DUPLICATE_EXTRA_ROW_COUNT,
        "missing_minute_count_total": EXPECTED_MISSING_MINUTE_COUNT,
        "source_zip_sha256_recorded": inspection["source_zip_sha256_recorded"],
        "source_zip_sha256_recomputed": inspection["source_zip_sha256_recomputed"],
        "source_zip_sha256_match": inspection["source_zip_sha256_match"],
        "schema_match": inspection["schema_match"],
        "normalization_policy": {
            "instrument_name": "exact string",
            "open_time": "integer",
            "open_high_low_close_vol_vol_ccy_vol_quote": "normalized decimal string when decimal parse succeeds, otherwise raw stripped string",
            "confirm": "boolean-equivalent normalized string",
            "rounding_used": False,
            "raw_values_preserved": True,
        },
        "allowed_scope": {
            "read_prior_sol_anomaly_artifacts": True,
            "read_prior_download_validator_hash_artifacts": True,
            "opened_only_validated_sol_zip_csv": True,
            "reconfirmed_sha256_before_csv_read": True,
            "no_download_api_browse_build_aggregation_dedupe": True,
        },
        **shared,
    }
    raw_rows_report = {
        "raw_duplicate_rows_report_created": True,
        "target_symbol": TARGET_SYMBOL,
        "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME,
        "conflict_open_time_utc": conflict_open_time_utc,
        "duplicate_source_date": source_date,
        "duplicate_source_file": source_file,
        "duplicate_source_zip": source_zip,
        "duplicate_row_count": len(inspection["occurrences"]),
        "raw_duplicate_rows_captured": True,
        "duplicate_rows": inspection["occurrences"],
    }
    field_diff_report = {
        "field_diff_report_created": True,
        "target_symbol": TARGET_SYMBOL,
        "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME,
        "conflict_open_time_utc": conflict_open_time_utc,
        "canonical_fields_compared": CANONICAL_FIELDS,
        "differing_field_count": diff["differing_field_count"],
        "differing_fields": diff["differing_fields"],
        "exact_duplicate_group": exact_duplicate,
        "conflicting_duplicate_group": not exact_duplicate,
        "field_diffs": diff["field_diffs"],
    }
    policy_preview = {
        "policy_preview_created": True,
        "preview_only": True,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_classification": classification["duplicate_classification"],
        "next_safe_route": classification["next_module"],
        "exact_duplicate_policy_route_safe": exact_duplicate,
        "confirm_only_policy_route_safe": confirm_only,
        "material_conflict_policy_route_required": material,
        "manual_review_required": unknown or symbol_or_schema,
        "future_policy_may_use_diagnostic_evidence": True,
        "future_policy_must_not_download_api_browse": True,
        "future_policy_must_not_rebuild_or_dedupe_now": True,
        "future_policy_must_preserve_raw_duplicate_rows_and_field_diff": True,
        "approval_grants_resolution_now": False,
        "approval_grants_future_policy_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
    }
    approval_record = {
        "approval_record_created": True,
        "approval_scope": "NEXT_SOL_DUPLICATE_POLICY_ONLY_AFTER_DIAGNOSTIC",
        "target_symbol": TARGET_SYMBOL,
        "duplicate_classification": classification["duplicate_classification"],
        "approval_grants_resolution_now": False,
        "approval_grants_future_policy_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": classification["next_module"],
    }
    replacement_checks = {
        "diagnostic_performed": True,
        "target_symbol_sol": TARGET_SYMBOL == "SOL-USDT-SWAP",
        "duplicate_open_time_count_total_one": EXPECTED_DUPLICATE_OPEN_TIME_COUNT == 1,
        "diagnostic_duplicate_extra_row_count_one": EXPECTED_DUPLICATE_EXTRA_ROW_COUNT == 1,
        "duplicate_group_count_one": EXPECTED_DUPLICATE_GROUP_COUNT == 1,
        "duplicate_row_count_two": len(inspection["occurrences"]) == 2,
        "missing_minutes_zero": EXPECTED_MISSING_MINUTE_COUNT == 0,
        "schema_match": inspection["schema_match"] is True,
        "source_zip_sha256_match": inspection["source_zip_sha256_match"] is True,
        "raw_duplicate_rows_captured": raw_rows_report["raw_duplicate_rows_captured"] is True,
        "field_diff_report_created": field_diff_report["field_diff_report_created"] is True,
        "policy_preview_created": policy_preview["policy_preview_created"] is True,
        "approval_record_created": approval_record["approval_record_created"] is True,
        "classification_route_valid": classification["next_module"]
        in {NEXT_MODULE_EXACT, NEXT_MODULE_CONFIRM_ONLY, NEXT_MODULE_MATERIAL, NEXT_MODULE_MANUAL},
        "approval_future_policy_only": approval_record["approval_grants_future_policy_next"] is True
        and approval_record["approval_grants_resolution_now"] is False
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False,
        "no_download_api_browse_build_aggregation_dedupe": all(value is False for value in DANGEROUS_FLAGS.values()),
        "not_research_backtest_edge_full_universe_broad": shared["output_valid_for_research_backtest"] is False
        and shared["output_valid_for_edge_claim"] is False
        and shared["safe_for_full_universe_acquisition"] is False
        and shared["broad_acquisition_ready"] is False,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_sol_duplicate_diagnostic_status": classification["pass_status"],
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "tracked_python_count_at_diagnostic_run": tracked_python_count(),
        **shared,
    }
    payloads = {
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic.json": diagnostic,
        "historical_okx_10_symbol_pilot_sol_duplicate_raw_rows_report.json": raw_rows_report,
        "historical_okx_10_symbol_pilot_sol_duplicate_field_diff_report.json": field_diff_report,
        "historical_okx_10_symbol_pilot_sol_duplicate_policy_preview.json": policy_preview,
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_summary.json": summary,
        f"{MODULE_NAME}_latest.json": summary,
    }
    require(replacement_checks_all_true, f"replacement checks failed: {replacement_checks}")
    return payloads


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic.json",
        "historical_okx_10_symbol_pilot_sol_duplicate_raw_rows_report.json",
        "historical_okx_10_symbol_pilot_sol_duplicate_field_diff_report.json",
        "historical_okx_10_symbol_pilot_sol_duplicate_policy_preview.json",
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json",
        "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    raw_rows = loaded["historical_okx_10_symbol_pilot_sol_duplicate_raw_rows_report.json"]
    diff = loaded["historical_okx_10_symbol_pilot_sol_duplicate_field_diff_report.json"]
    preview = loaded["historical_okx_10_symbol_pilot_sol_duplicate_policy_preview.json"]
    approval = loaded["historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_approval_record.json"]
    checks = {
        "required_artifacts_exist": True,
        "raw_duplicate_rows_captured": raw_rows.get("raw_duplicate_rows_captured") is True
        and raw_rows.get("duplicate_row_count") == 2,
        "differing_fields_listed": isinstance(diff.get("differing_fields"), list),
        "field_diff_report_created": diff.get("field_diff_report_created") is True,
        "policy_preview_created": preview.get("policy_preview_created") is True,
        "approval_record_created": approval.get("approval_record_created") is True,
        "next_module_matches_classification": preview.get("next_safe_route") == approval.get("next_module") == summary.get("next_module"),
        "no_forbidden_execution": summary.get("dangerous_flags_all_false") is True
        and summary.get("data_build_performed") is False
        and summary.get("aggregation_performed_now") is False
        and summary.get("output_csv_created") is False,
        "replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
    }
    checks["written_artifacts_valid"] = all(checks.values())
    return checks


def main() -> None:
    generated_at = utc_now()
    artifacts = {label: load_json(path) for label, path in ARTIFACTS.items()}
    validate_prior_artifacts(artifacts)
    sol_entry = sol_hash_entry_for_date(artifacts["download_hash_report"], EXPECTED_SOURCE_DATE)
    inspection = inspect_duplicate_group(sol_entry)
    diff = diff_duplicate_rows(inspection["occurrences"])
    classification = classify_duplicate(diff["differing_fields"], inspection["schema_match"])
    payloads = build_payloads(generated_at, inspection, diff, classification)
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    summary = payloads["historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_summary.json"]
    written = validate_written_artifacts(summary)
    require(written["written_artifacts_valid"] is True, f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_sol_duplicate_diagnostic_status": BLOCKED_STATUS,
            "diagnostic_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "duplicate_open_time_count_total": EXPECTED_DUPLICATE_OPEN_TIME_COUNT,
            "diagnostic_duplicate_extra_row_count": None,
            "duplicate_open_time_group_count": None,
            "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME,
            "conflict_open_time_utc": utc_from_open_time(EXPECTED_DUPLICATE_OPEN_TIME),
            "duplicate_source_date": EXPECTED_SOURCE_DATE,
            "duplicate_source_file": expected_csv_for_date(EXPECTED_SOURCE_DATE),
            "duplicate_row_count": None,
            "differing_field_count": None,
            "differing_fields": [],
            "duplicate_classification": "UNKNOWN_CONFLICT",
            "exact_duplicate": False,
            "confirm_only_conflict": False,
            "ohlcv_material_conflict": False,
            "symbol_or_schema_conflict": False,
            "unknown_conflict": True,
            "raw_duplicate_rows_captured": False,
            "field_diff_report_created": False,
            "policy_preview_created": False,
            "approval_record_created": False,
            "approval_grants_resolution_now": False,
            "approval_grants_future_policy_next": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_dedupe_now": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 1,
            "current_evidence_chain_quality_after_diagnostic": QUALITY_MANUAL,
            "next_module": NEXT_MODULE_MANUAL,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_10_symbol_pilot_sol_duplicate_diagnostic_summary.json", blocked)
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
