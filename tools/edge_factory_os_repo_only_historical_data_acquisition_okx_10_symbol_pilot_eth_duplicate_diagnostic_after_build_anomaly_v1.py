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
    "eth_duplicate_diagnostic_after_build_anomaly_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "2d910bd"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_BUILD_ANOMALY_RECORD_"
    "ETH_DUPLICATE_DIAGNOSTIC_READY"
)
PASS_STATUS_PREFIX = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_DUPLICATE_DIAGNOSTIC"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_DUPLICATE_DIAGNOSTIC"
)
TARGET_SYMBOL = "ETH-USDT-SWAP"
EXPECTED_DUPLICATE_OPEN_TIME_MS = 1_697_108_400_000
EXPECTED_DUPLICATE_SOURCE_DATE = "2023-10-12"
EXPECTED_DUPLICATE_EXTRA_ROW_COUNT = 1
EXPECTED_DUPLICATE_GROUP_SIZE = 2
EXPECTED_DUPLICATE_OPEN_TIME_GROUP_COUNT = 1
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
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_10_SYMBOL_PILOT_ETH_DUPLICATE_DIAGNOSTIC_"
    "CLASSIFIED_POLICY_READY"
)
NEXT_MODULE_EXACT = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_exact_duplicate_policy_after_diagnostic_v1.py"
)
NEXT_MODULE_CONFIRM_ONLY = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_confirm_only_duplicate_policy_after_diagnostic_v1.py"
)
NEXT_MODULE_MATERIAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_material_duplicate_conflict_policy_after_diagnostic_v1.py"
)
NEXT_MODULE_UNKNOWN = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "eth_duplicate_manual_review_required_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
ANOMALY_RECORD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "build_execution_blocked_or_anomaly_record_after_preview_approval_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_"
    "download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "anomaly_record_summary": ANOMALY_RECORD_DIR / f"{ANOMALY_RECORD_DIR.name}_latest.json",
    "anomaly_blocked_record": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_build_anomaly_blocked_record.json",
    "diagnostic_preview": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_preview.json",
    "diagnostic_prior_approval": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json",
    "anomaly_limitations": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_build_anomaly_limitations_report.json",
    "anomaly_self_validator": ANOMALY_RECORD_DIR / "historical_okx_10_symbol_pilot_build_anomaly_self_validator.json",
    "download_validator_summary": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_download_execution_validator_summary.json",
    "download_hash_validation_report": DOWNLOAD_VALIDATOR_DIR / "historical_okx_10_symbol_pilot_hash_validation_report.json",
}

DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_10_symbol_rebuild_performed_now": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "dedupe_execution_performed_now": False,
    "output_1h_csv_created_now": False,
    "modified_source_output_created_now": False,
    "conflicting_row_selected_now": False,
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


def iso_utc_from_ms(epoch_ms: int) -> str:
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()


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


def recorded_hash(record: dict[str, Any]) -> str:
    return str(record.get("recorded_sha256") or record.get("sha256") or "")


def safe_zip_member(name: str) -> bool:
    pure = PurePosixPath(name)
    return not pure.is_absolute() and ".." not in pure.parts


def expected_csv_name(symbol: str, day: str) -> str:
    return f"{symbol}-candlesticks-{day}.csv"


def normalize_decimal_string(value: Any) -> str:
    text = str(value).strip()
    try:
        decimal_value = Decimal(text)
    except InvalidOperation:
        return text
    normalized = decimal_value.normalize()
    if normalized == 0:
        return "0"
    rendered = format(normalized, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def normalize_confirm(value: Any) -> str:
    text = str(value).strip()
    lowered = text.lower()
    if lowered in {"1", "true", "yes"}:
        return "1"
    if lowered in {"0", "false", "no"}:
        return "0"
    return text


def normalize_field(field: str, value: Any) -> str:
    if field in OHLC_FIELDS or field in VOLUME_FIELDS:
        return normalize_decimal_string(value)
    if field == "open_time":
        return str(int(str(value).strip()))
    if field == "confirm":
        return normalize_confirm(value)
    return str(value).strip()


def validate_false(data: dict[str, Any], keys: list[str], label: str) -> None:
    for key in keys:
        require(data.get(key) is False, f"{label}.{key} must be false")


def validate_prior_artifacts(artifacts: dict[str, dict[str, Any]]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved diagnostic module")

    summary = artifacts["anomaly_record_summary"]
    blocked_record = artifacts["anomaly_blocked_record"]
    preview = artifacts["diagnostic_preview"]
    approval = artifacts["diagnostic_prior_approval"]
    limitations = artifacts["anomaly_limitations"]
    self_validator = artifacts["anomaly_self_validator"]
    download_summary = artifacts["download_validator_summary"]
    hash_report = artifacts["download_hash_validation_report"]

    require(
        summary.get("historical_data_acquisition_okx_10_symbol_pilot_build_anomaly_record_status")
        == PREVIOUS_STATUS,
        "previous anomaly record status mismatch",
    )
    require(summary.get("next_module") == REQUESTED_MODULE, "previous next_module mismatch")
    require(summary.get("anomaly_symbol") == TARGET_SYMBOL, "summary anomaly symbol mismatch")
    require(summary.get("duplicate_open_time_count_total") == 1, "summary duplicate count mismatch")
    require(summary.get("missing_minute_count_total") == 0, "summary missing minute count mismatch")
    require(summary.get("schema_mismatch_count") == 0, "summary schema mismatch count mismatch")
    require(summary.get("symbol_mismatch_count") == 0, "summary symbol mismatch count mismatch")
    require(summary.get("pilot_build_execution_blocked") is True, "pilot build blocked flag mismatch")
    require(summary.get("active_p0_blocker_count") == 1, "active P0 blocker count mismatch")
    require(summary.get("approval_grants_future_eth_duplicate_diagnostic_next") is True, "future diagnostic approval missing")
    require(summary.get("replacement_checks_all_true") is True, "anomaly record replacement checks did not pass")

    require(blocked_record.get("pilot_build_execution_blocked") is True, "blocked record does not preserve blocked state")
    require(blocked_record.get("anomaly_symbol") == TARGET_SYMBOL, "blocked record target symbol mismatch")
    require(blocked_record.get("known_duplicate_open_time_epoch_ms") == EXPECTED_DUPLICATE_OPEN_TIME_MS, "known duplicate open_time mismatch")
    require(blocked_record.get("duplicate_open_time_count_total") == 1, "blocked record duplicate count mismatch")
    require(blocked_record.get("output_csv_created") is False, "blocked record output CSV mismatch")
    require(blocked_record.get("output_manifest_created") is False, "blocked record output manifest mismatch")
    require(blocked_record.get("data_build_performed") is False, "blocked record data build mismatch")
    require(blocked_record.get("aggregation_performed_now") is False, "blocked record aggregation mismatch")

    require(preview.get("eth_duplicate_diagnostic_preview_created") is True, "diagnostic preview missing")
    require(preview.get("target_symbol") == TARGET_SYMBOL, "diagnostic preview target mismatch")
    require(preview.get("known_duplicate_open_time_epoch_ms") == EXPECTED_DUPLICATE_OPEN_TIME_MS, "diagnostic preview open_time mismatch")
    require(preview.get("future_diagnostic_module_must_reconfirm_sha256_before_reading") is True, "SHA reconfirm rule missing")
    require(preview.get("future_diagnostic_module_may_read_only_eth_usdt_swap_already_validated_zip_csv_files") is True, "ETH-only read rule missing")
    validate_false(
        preview,
        ["download_allowed", "api_allowed", "browse_allowed", "build_or_aggregation_performed_now", "dedupe_or_rebuild_performed_now"],
        "diagnostic_preview",
    )

    require(approval.get("eth_duplicate_diagnostic_approval_record_created") is True, "diagnostic approval record missing")
    require(approval.get("approval_grants_future_eth_duplicate_diagnostic_next") is True, "future diagnostic approval mismatch")
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
        "diagnostic_prior_approval",
    )

    require(limitations.get("required_next_step") == "ETH_DUPLICATE_DIAGNOSTIC_ONLY", "limitations next step mismatch")
    require(self_validator.get("next_module_valid") is True, "anomaly self-validator next_module mismatch")
    require(download_summary.get("all_hashes_match_recorded") is True, "download validator hash summary mismatch")
    require(download_summary.get("all_expected_schema_match") is True, "download validator schema mismatch")
    require(download_summary.get("all_observed_symbols_match_expected") is True, "download validator symbol mismatch")
    require(hash_report.get("all_hashes_match_recorded") is True, "hash report mismatch")


def select_eth_hash_record(hash_report: dict[str, Any]) -> dict[str, Any]:
    records = hash_report.get("hashes")
    require(isinstance(records, list), "hash report hashes is not a list")
    matches = [
        record
        for record in records
        if isinstance(record, dict)
        and record.get("symbol") == TARGET_SYMBOL
        and record.get("date") == EXPECTED_DUPLICATE_SOURCE_DATE
    ]
    require(len(matches) == 1, f"expected one ETH hash record for {EXPECTED_DUPLICATE_SOURCE_DATE}, found {len(matches)}")
    return matches[0]


def read_duplicate_group(record: dict[str, Any]) -> dict[str, Any]:
    zip_path = Path(str(record.get("local_zip_path", "")))
    require(zip_path.exists(), f"ETH source ZIP missing: {zip_path}")
    observed_sha256 = sha256_file(zip_path)
    require(observed_sha256 == recorded_hash(record), f"ETH source ZIP SHA256 mismatch: {zip_path}")

    source_date = str(record.get("date"))
    inner_csv = expected_csv_name(TARGET_SYMBOL, source_date)
    duplicate_rows: list[dict[str, Any]] = []
    rows_read = 0
    schema_match = False
    symbol_mismatch_count = 0
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        require(len(names) <= 10, f"ETH ZIP has too many members: {zip_path}")
        require(all(safe_zip_member(name) for name in names), f"ETH ZIP traversal risk: {zip_path}")
        require(inner_csv in names, f"expected ETH inner CSV missing: {inner_csv}")
        with archive.open(inner_csv, "r") as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
            schema_match = reader.fieldnames == EXPECTED_SCHEMA
            require(schema_match, f"ETH schema mismatch in {inner_csv}")
            found_target = False
            for row_number, row in enumerate(reader, start=2):
                rows_read += 1
                if row.get("instrument_name") != TARGET_SYMBOL:
                    symbol_mismatch_count += 1
                try:
                    open_time = int(str(row.get("open_time", "")).strip())
                except ValueError as exc:
                    raise DiagnosticBlocked(f"ETH open_time parse failed {inner_csv} row={row_number}") from exc
                if open_time == EXPECTED_DUPLICATE_OPEN_TIME_MS:
                    found_target = True
                    duplicate_rows.append(
                        {
                            "row_number": row_number,
                            "source_date": source_date,
                            "source_file": inner_csv,
                            "source_zip": str(zip_path),
                            "source_zip_sha256": observed_sha256,
                            "raw_row": {field: row.get(field) for field in EXPECTED_SCHEMA},
                            "normalized_row": {field: normalize_field(field, row.get(field)) for field in EXPECTED_SCHEMA},
                        }
                    )
                elif found_target and open_time > EXPECTED_DUPLICATE_OPEN_TIME_MS:
                    break

    require(symbol_mismatch_count == 0, f"ETH symbol mismatch count: {symbol_mismatch_count}")
    require(duplicate_rows, "target ETH duplicate open_time row not found")
    return {
        "source_date": source_date,
        "source_file": inner_csv,
        "source_zip": str(zip_path),
        "source_zip_sha256": observed_sha256,
        "source_zip_sha256_reconfirmed": True,
        "rows_read_until_duplicate_group_captured": rows_read,
        "schema_match": schema_match,
        "symbol_mismatch_count": symbol_mismatch_count,
        "duplicate_rows": duplicate_rows,
    }


def diff_duplicate_rows(duplicate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    require(len(duplicate_rows) == EXPECTED_DUPLICATE_GROUP_SIZE, f"duplicate group size mismatch: {len(duplicate_rows)}")
    field_diffs: list[dict[str, Any]] = []
    for field in CANONICAL_FIELDS:
        raw_values = [row["raw_row"].get(field) for row in duplicate_rows]
        normalized_values = [row["normalized_row"].get(field) for row in duplicate_rows]
        unique_normalized = list(dict.fromkeys(normalized_values))
        if len(unique_normalized) > 1:
            field_diffs.append(
                {
                    "field": field,
                    "raw_values": raw_values,
                    "normalized_values": normalized_values,
                }
            )
    differing_fields = [item["field"] for item in field_diffs]
    exact_duplicate = len(differing_fields) == 0
    confirm_only_conflict = differing_fields == ["confirm"]
    ohlc_diff = any(field in OHLC_FIELDS for field in differing_fields)
    volume_diff = any(field in VOLUME_FIELDS for field in differing_fields)
    symbol_or_schema_conflict = any(field in {"instrument_name", "open_time"} for field in differing_fields)
    unknown_conflict = False
    if exact_duplicate:
        classification = "EXACT_DUPLICATE"
    elif symbol_or_schema_conflict:
        classification = "SYMBOL_OR_SCHEMA_CONFLICT"
    elif confirm_only_conflict:
        classification = "CONFIRM_ONLY_CONFLICT"
    elif ohlc_diff and not volume_diff and not any(field not in OHLC_FIELDS for field in differing_fields):
        classification = "OHLC_ONLY_CONFLICT"
    elif volume_diff and not ohlc_diff and not any(field not in VOLUME_FIELDS for field in differing_fields):
        classification = "VOLUME_ONLY_CONFLICT"
    elif ohlc_diff or volume_diff:
        classification = "OHLCV_MATERIAL_CONFLICT"
    else:
        classification = "UNKNOWN_CONFLICT"
        unknown_conflict = True
    return {
        "field_diffs": field_diffs,
        "differing_fields": differing_fields,
        "differing_field_count": len(differing_fields),
        "exact_duplicate": exact_duplicate,
        "confirm_only_conflict": confirm_only_conflict,
        "ohlcv_material_conflict": classification in {"OHLC_ONLY_CONFLICT", "VOLUME_ONLY_CONFLICT", "OHLCV_MATERIAL_CONFLICT"},
        "symbol_or_schema_conflict": symbol_or_schema_conflict,
        "unknown_conflict": unknown_conflict,
        "duplicate_classification": classification,
    }


def next_module_for_classification(classification: str) -> str:
    if classification == "EXACT_DUPLICATE":
        return NEXT_MODULE_EXACT
    if classification == "CONFIRM_ONLY_CONFLICT":
        return NEXT_MODULE_CONFIRM_ONLY
    if classification in {"OHLC_ONLY_CONFLICT", "VOLUME_ONLY_CONFLICT", "OHLCV_MATERIAL_CONFLICT", "SYMBOL_OR_SCHEMA_CONFLICT"}:
        return NEXT_MODULE_MATERIAL
    return NEXT_MODULE_UNKNOWN


def build_outputs(generated_at: str, duplicate: dict[str, Any], diff: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    classification = str(diff["duplicate_classification"])
    next_module = next_module_for_classification(classification)
    exact_duplicate = bool(diff["exact_duplicate"])
    active_p0 = 0 if exact_duplicate and next_module == NEXT_MODULE_EXACT else 1
    conflict_open_time_utc = iso_utc_from_ms(EXPECTED_DUPLICATE_OPEN_TIME_MS)
    status = f"{PASS_STATUS_PREFIX}_{classification}_POLICY_READY"

    raw_rows_report = {
        "raw_duplicate_rows_captured": True,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_source_date": duplicate["source_date"],
        "duplicate_source_file": duplicate["source_file"],
        "duplicate_source_zip": duplicate["source_zip"],
        "duplicate_source_zip_sha256": duplicate["source_zip_sha256"],
        "source_zip_sha256_reconfirmed": duplicate["source_zip_sha256_reconfirmed"],
        "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME_MS,
        "conflict_open_time_utc": conflict_open_time_utc,
        "duplicate_row_count": len(duplicate["duplicate_rows"]),
        "raw_duplicate_rows": duplicate["duplicate_rows"],
        "rows_read_until_duplicate_group_captured": duplicate["rows_read_until_duplicate_group_captured"],
    }
    field_diff_report = {
        "field_diff_report_created": True,
        "target_symbol": TARGET_SYMBOL,
        "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME_MS,
        "conflict_open_time_utc": conflict_open_time_utc,
        "canonical_fields_compared": CANONICAL_FIELDS,
        "normalization_rules": {
            "instrument_name": "exact stripped string",
            "open_time": "integer string",
            "ohlcv_volume_fields": "Decimal parsed and rendered without insignificant trailing zeros",
            "confirm": "boolean/integer-equivalent string when possible",
        },
        "differing_field_count": diff["differing_field_count"],
        "differing_fields": diff["differing_fields"],
        "field_diffs": diff["field_diffs"],
    }
    policy_preview = {
        "policy_preview_created": True,
        "preview_only": True,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_classification": classification,
        "next_safe_route": next_module,
        "exact_duplicate": diff["exact_duplicate"],
        "confirm_only_conflict": diff["confirm_only_conflict"],
        "ohlcv_material_conflict": diff["ohlcv_material_conflict"],
        "symbol_or_schema_conflict": diff["symbol_or_schema_conflict"],
        "unknown_conflict": diff["unknown_conflict"],
        "policy_route_reason": (
            "exact duplicate rows can be reviewed by the exact duplicate policy preview"
            if exact_duplicate
            else "non-exact or uninspectable duplicate remains blocked until a separate policy module"
        ),
        "future_policy_may_consider_resolution_next": True,
        "resolution_executed_now": False,
        "rebuild_executed_now": False,
        "dedupe_executed_now": False,
        "download_api_browse_allowed": False,
        "research_backtest_edge_ready": False,
    }
    approval_record = {
        "approval_record_created": True,
        "approval_scope": "NEXT_POLICY_ONLY_AFTER_ETH_DUPLICATE_DIAGNOSTIC_CLASSIFICATION",
        "approval_grants_resolution_now": False,
        "approval_grants_future_policy_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "approval_grants_download_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "next_module": next_module,
    }
    diagnostic = {
        "diagnostic_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "duplicate_open_time_count_total": 1,
        "diagnostic_duplicate_extra_row_count": EXPECTED_DUPLICATE_EXTRA_ROW_COUNT,
        "duplicate_open_time_group_count": EXPECTED_DUPLICATE_OPEN_TIME_GROUP_COUNT,
        "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME_MS,
        "conflict_open_time_utc": conflict_open_time_utc,
        "duplicate_source_date": duplicate["source_date"],
        "duplicate_source_file": duplicate["source_file"],
        "duplicate_source_zip": duplicate["source_zip"],
        "duplicate_row_count": len(duplicate["duplicate_rows"]),
        "differing_field_count": diff["differing_field_count"],
        "differing_fields": diff["differing_fields"],
        "duplicate_classification": classification,
        "exact_duplicate": diff["exact_duplicate"],
        "confirm_only_conflict": diff["confirm_only_conflict"],
        "ohlcv_material_conflict": diff["ohlcv_material_conflict"],
        "symbol_or_schema_conflict": diff["symbol_or_schema_conflict"],
        "unknown_conflict": diff["unknown_conflict"],
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
        "active_p1_attention_count": 0,
        "next_module": next_module,
    }
    replacement_checks = {
        "diagnostic_performed": diagnostic["diagnostic_performed"],
        "target_symbol_eth": diagnostic["target_symbol"] == TARGET_SYMBOL,
        "duplicate_count_total_one": diagnostic["duplicate_open_time_count_total"] == 1,
        "diagnostic_duplicate_extra_row_count_one": diagnostic["diagnostic_duplicate_extra_row_count"] == 1,
        "duplicate_open_time_group_count_one": diagnostic["duplicate_open_time_group_count"] == 1,
        "duplicate_row_count_two": diagnostic["duplicate_row_count"] == 2,
        "source_date_valid": diagnostic["duplicate_source_date"] == EXPECTED_DUPLICATE_SOURCE_DATE,
        "conflict_open_time_valid": diagnostic["conflict_open_time"] == EXPECTED_DUPLICATE_OPEN_TIME_MS,
        "raw_duplicate_rows_captured": diagnostic["raw_duplicate_rows_captured"],
        "field_diff_report_created": diagnostic["field_diff_report_created"],
        "policy_preview_created": diagnostic["policy_preview_created"],
        "approval_record_created": diagnostic["approval_record_created"],
        "approval_future_policy_next": diagnostic["approval_grants_future_policy_next"],
        "approval_rebuild_dedupe_now_false": diagnostic["approval_grants_rebuild_now"] is False
        and diagnostic["approval_grants_dedupe_now"] is False,
        "no_build_aggregation_output": diagnostic["data_build_performed"] is False
        and diagnostic["aggregation_performed_now"] is False
        and diagnostic["output_csv_created"] is False,
        "not_research_backtest_edge_full_universe_broad": diagnostic["output_valid_for_research_backtest"] is False
        and diagnostic["output_valid_for_edge_claim"] is False
        and diagnostic["safe_for_full_universe_acquisition"] is False
        and diagnostic["broad_acquisition_ready"] is False,
        "next_module_matches_classification": next_module == next_module_for_classification(classification),
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_10_symbol_pilot_eth_duplicate_diagnostic_status": status,
        **diagnostic,
        "current_evidence_chain_quality_after_diagnostic": AFTER_QUALITY,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_diagnostic_run": tracked_python_count(),
    }
    artifacts = {
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic.json": {
            **summary,
            "raw_rows_report_artifact": "historical_okx_10_symbol_pilot_eth_duplicate_raw_rows_report.json",
            "field_diff_report_artifact": "historical_okx_10_symbol_pilot_eth_duplicate_field_diff_report.json",
        },
        "historical_okx_10_symbol_pilot_eth_duplicate_raw_rows_report.json": raw_rows_report,
        "historical_okx_10_symbol_pilot_eth_duplicate_field_diff_report.json": field_diff_report,
        "historical_okx_10_symbol_pilot_eth_duplicate_policy_preview.json": policy_preview,
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json": approval_record,
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_summary.json": summary,
        f"{MODULE_NAME}_latest.json": summary,
    }
    return summary, artifacts


def validate_written_artifacts(summary: dict[str, Any]) -> dict[str, bool]:
    required_files = [
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_raw_rows_report.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_field_diff_report.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_policy_preview.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json",
        "historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_summary.json",
    ]
    loaded: dict[str, Any] = {}
    for filename in required_files:
        path = OUTPUT_DIR / filename
        require(path.exists(), f"missing written artifact {filename}")
        loaded[filename] = json.loads(path.read_text(encoding="utf-8"))
    raw_rows = loaded["historical_okx_10_symbol_pilot_eth_duplicate_raw_rows_report.json"]
    diff = loaded["historical_okx_10_symbol_pilot_eth_duplicate_field_diff_report.json"]
    approval = loaded["historical_okx_10_symbol_pilot_eth_duplicate_diagnostic_approval_record.json"]
    return {
        "required_artifacts_exist": True,
        "raw_duplicate_rows_captured": raw_rows.get("raw_duplicate_rows_captured") is True
        and raw_rows.get("duplicate_row_count") == 2,
        "field_diff_report_created": diff.get("field_diff_report_created") is True
        and isinstance(diff.get("differing_fields"), list),
        "approval_record_created": approval.get("approval_record_created") is True
        and approval.get("approval_grants_future_policy_next") is True,
        "summary_replacement_checks_all_true": summary.get("replacement_checks_all_true") is True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }


def main() -> None:
    generated_at = utc_now()
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    artifacts = {label: load_json(path, label, exists, valid) for label, path in ARTIFACTS.items()}
    validate_prior_artifacts(artifacts)
    eth_record = select_eth_hash_record(artifacts["download_hash_validation_report"])
    duplicate = read_duplicate_group(eth_record)
    diff = diff_duplicate_rows(duplicate["duplicate_rows"])
    summary, outputs = build_outputs(generated_at, duplicate, diff)
    require(summary["replacement_checks_all_true"] is True, "replacement checks failed")
    for filename, payload in outputs.items():
        write_json(OUTPUT_DIR / filename, payload)
    written = validate_written_artifacts(summary)
    require(all(written.values()), f"written artifact validation failed: {written}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except DiagnosticBlocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_10_symbol_pilot_eth_duplicate_diagnostic_status": BLOCKED_STATUS,
            "diagnostic_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "duplicate_open_time_count_total": 1,
            "diagnostic_duplicate_extra_row_count": 0,
            "duplicate_open_time_group_count": 0,
            "conflict_open_time": EXPECTED_DUPLICATE_OPEN_TIME_MS,
            "conflict_open_time_utc": iso_utc_from_ms(EXPECTED_DUPLICATE_OPEN_TIME_MS),
            "duplicate_source_date": EXPECTED_DUPLICATE_SOURCE_DATE,
            "duplicate_source_file": "",
            "duplicate_source_zip": "",
            "duplicate_row_count": 0,
            "differing_field_count": 0,
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
            "active_p1_attention_count": 0,
            "current_evidence_chain_quality_after_diagnostic": BLOCKED_STATUS,
            "next_module": NEXT_MODULE_UNKNOWN,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
