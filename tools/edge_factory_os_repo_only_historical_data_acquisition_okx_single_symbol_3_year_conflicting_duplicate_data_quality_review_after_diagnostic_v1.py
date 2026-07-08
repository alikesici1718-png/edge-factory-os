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
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_conflicting_duplicate_data_quality_review_after_diagnostic_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "dfd6663"
TARGET_SYMBOL = "BTC-USDT-SWAP"
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATE_MINUTE_"
    "DIAGNOSTIC_CONFLICTING_DATA_QUALITY_REVIEW_REQUIRED"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_CONFLICTING_DUPLICATE_"
    "DATA_QUALITY_REVIEW_MATERIAL_CONFLICT_POLICY_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_CONFLICTING_DUPLICATE_"
    "DATA_QUALITY_REVIEW"
)
EXPECTED_CONFLICTING_GROUP_COUNT = 1
EXPECTED_CONFLICTING_EXTRA_ROW_COUNT = 1
EXPECTED_CONFLICT_OPEN_TIME = 1_776_150_360_000
EXPECTED_CONFLICT_SOURCE_DATE = "2026-04-14"
EXPECTED_CONFLICT_SOURCE_FILE = "BTC-USDT-SWAP-candlesticks-2026-04-14.csv"
EXPECTED_FILE_COUNT = 1053
EXPECTED_SOURCE_ROW_COUNT = 1_516_641
EXPECTED_TOTAL_SOURCE_ROWS = 1_516_320
EXPECTED_DUPLICATE_OPEN_TIME_COUNT = 321
EXPECTED_MISSING_MINUTE_COUNT = 0
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATES_CONFLICTING_"
    "DATA_QUALITY_REVIEW_REQUIRED"
)
AFTER_QUALITY_CONFIRM_ONLY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_CONFIRM_ONLY_DUPLICATE_"
    "RESOLUTION_POLICY_READY"
)
AFTER_QUALITY_MATERIAL = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_MATERIAL_DUPLICATE_CONFLICT_"
    "POLICY_REVIEW_READY"
)
AFTER_QUALITY_UNKNOWN = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_DUPLICATE_CONFLICT_MANUAL_"
    "REVIEW_REQUIRED"
)
NEXT_MODULE_CONFIRM_ONLY = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_confirm_only_duplicate_resolution_policy_after_conflict_review_v1.py"
)
NEXT_MODULE_MATERIAL = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_material_duplicate_conflict_policy_after_conflict_review_v1.py"
)
NEXT_MODULE_UNKNOWN = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_duplicate_conflict_manual_review_required_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
DIAGNOSTIC_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_duplicate_minute_resolution_diagnostic_after_blocked_build_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1"
)

DIAGNOSTIC_SUMMARY = DIAGNOSTIC_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_diagnostic_summary.json"
CONFLICT_REPORT = DIAGNOSTIC_DIR / "historical_okx_single_symbol_3_year_duplicate_minute_conflict_report.json"
HASH_VALIDATION_REPORT = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_hash_validation_report.json"

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
DIFF_FIELDS = [
    "instrument_name",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "vol_ccy",
    "vol_quote",
    "confirm",
]
DANGEROUS_FLAGS = {
    "download_performed_now": False,
    "api_call_performed_now": False,
    "browse_performed_now": False,
    "url_fetch_performed_now": False,
    "full_1053_file_rebuild_performed": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "dedupe_execution_performed": False,
    "output_csv_created": False,
    "modified_source_output_created": False,
    "conflicting_row_chosen_as_final": False,
    "synthetic_fill_used": False,
    "forward_fill_used": False,
    "backfill_used": False,
    "research_backtest_candidate_performed": False,
    "edge_profit_claim_made": False,
    "broad_acquisition_ready": False,
    "strict_3y_completeness_claimed": False,
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
        raise Blocked(message)


def load_json(path: Path) -> Any:
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
        return "true"
    if text in {"0", "false", "f", "no", "n"}:
        return "false"
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


def validate_preflight(summary: dict[str, Any], conflict_report: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(
        summary.get("historical_data_acquisition_okx_single_symbol_3_year_duplicate_minute_diagnostic_status")
        == PREVIOUS_STATUS,
        "previous diagnostic status mismatch",
    )
    require(summary.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(summary.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(summary.get("source_row_count_total") == EXPECTED_SOURCE_ROW_COUNT, "source row count mismatch")
    require(summary.get("expected_total_source_rows") == EXPECTED_TOTAL_SOURCE_ROWS, "expected row count mismatch")
    require(summary.get("duplicate_open_time_count_total") == EXPECTED_DUPLICATE_OPEN_TIME_COUNT, "duplicate count mismatch")
    require(summary.get("conflicting_duplicate_group_count") == EXPECTED_CONFLICTING_GROUP_COUNT, "conflict group count mismatch")
    require(summary.get("conflicting_duplicate_extra_row_count") == EXPECTED_CONFLICTING_EXTRA_ROW_COUNT, "conflict extra count mismatch")
    require(summary.get("any_conflicting_duplicates") is True, "conflicting duplicate flag mismatch")
    require(summary.get("exact_dedupe_rebuild_preview_created") is False, "exact dedupe preview unexpectedly created")
    require(summary.get("approval_grants_future_exact_dedupe_rebuild_next") is False, "exact dedupe approval unexpectedly granted")
    require(summary.get("active_p0_blocker_count") == 1, "P0 blocker count mismatch")
    require(summary.get("active_p1_attention_count") == 9, "P1 attention count mismatch")
    require(conflict_report.get("any_conflicting_duplicates") is True, "conflict report flag mismatch")
    require(conflict_report.get("conflicting_duplicate_group_count") == EXPECTED_CONFLICTING_GROUP_COUNT, "conflict report count mismatch")
    groups = conflict_report.get("conflicting_groups")
    require(isinstance(groups, list) and len(groups) == EXPECTED_CONFLICTING_GROUP_COUNT, "conflicting_groups mismatch")
    group = groups[0]
    require(group.get("open_time") == EXPECTED_CONFLICT_OPEN_TIME, "conflict open_time mismatch")
    require(group.get("group_size") == 2, "conflict group size mismatch")
    require(group.get("source_csv_files") == [EXPECTED_CONFLICT_SOURCE_FILE], "conflict source file mismatch")
    require(group.get("within_file_duplicate_group") is True, "within-file conflict flag mismatch")
    require(group.get("cross_file_duplicate_group") is False, "cross-file conflict flag mismatch")
    return group


def source_identity_from_hash_report(hash_report: dict[str, Any]) -> dict[str, Any]:
    items = hash_report.get("hashes")
    require(isinstance(items, list), "hash report hashes is not a list")
    matches = [item for item in items if isinstance(item, dict) and item.get("date") == EXPECTED_CONFLICT_SOURCE_DATE]
    require(len(matches) == 1, "source hash record not uniquely identified")
    item = matches[0]
    path = Path(str(item.get("local_zip_path", "")))
    require(path.exists(), f"source ZIP missing: {path}")
    digest = sha256_file(path)
    require(digest == item.get("recorded_sha256"), "source ZIP SHA256 mismatch")
    return {
        "date": EXPECTED_CONFLICT_SOURCE_DATE,
        "source_zip_path": str(path),
        "source_zip_sha256": digest,
        "source_kind": item.get("source_kind"),
    }


def read_conflict_rows(source: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    path = Path(source["source_zip_path"])
    captured: list[dict[str, Any]] = []
    schema_match = False
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) <= 10, f"too many ZIP members: {path}")
        require(all(safe_zip_member(name) for name in names), f"ZIP traversal risk: {path}")
        require(EXPECTED_CONFLICT_SOURCE_FILE in names, f"expected CSV missing: {EXPECTED_CONFLICT_SOURCE_FILE}")
        with archive.open(EXPECTED_CONFLICT_SOURCE_FILE, "r") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
            reader = csv.DictReader(text)
            schema_match = reader.fieldnames == EXPECTED_SCHEMA
            require(schema_match, "conflict source schema mismatch")
            for row_number, row in enumerate(reader, start=2):
                open_time = int(str(row["open_time"]).strip())
                if open_time == EXPECTED_CONFLICT_OPEN_TIME:
                    captured.append(
                        {
                            "source_date": EXPECTED_CONFLICT_SOURCE_DATE,
                            "source_file": EXPECTED_CONFLICT_SOURCE_FILE,
                            "source_zip": str(path),
                            "row_number": row_number,
                            "raw_values": {field: row.get(field) for field in EXPECTED_SCHEMA},
                            "canonical_values": canonical_row(row),
                        }
                    )
    require(len(captured) == 2, f"conflicting row count mismatch: {len(captured)}")
    return captured, schema_match


def diff_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    left = rows[0]["canonical_values"]
    right = rows[1]["canonical_values"]
    differing = [field for field in DIFF_FIELDS if left.get(field) != right.get(field)]
    ohlc_fields = {"open", "high", "low", "close"}
    volume_fields = {"vol", "vol_ccy", "vol_quote"}
    symbol_or_schema = "instrument_name" in differing
    confirm_only = differing == ["confirm"]
    ohlc_diff = bool(ohlc_fields.intersection(differing))
    volume_diff = bool(volume_fields.intersection(differing))
    if symbol_or_schema:
        classification = "SYMBOL_OR_SCHEMA_CONFLICT"
    elif confirm_only:
        classification = "CONFIRM_ONLY_CONFLICT"
    elif ohlc_diff and not volume_diff:
        classification = "OHLC_ONLY_CONFLICT"
    elif volume_diff and not ohlc_diff:
        classification = "VOLUME_ONLY_CONFLICT"
    elif ohlc_diff and volume_diff:
        classification = "OHLCV_MATERIAL_CONFLICT"
    elif differing:
        classification = "UNKNOWN_CONFLICT"
    else:
        classification = "UNKNOWN_CONFLICT"
    return {
        "differing_field_count": len(differing),
        "differing_fields": differing,
        "field_diffs": [
            {
                "field": field,
                "left_raw": rows[0]["raw_values"].get(field),
                "right_raw": rows[1]["raw_values"].get(field),
                "left_canonical": left.get(field),
                "right_canonical": right.get(field),
            }
            for field in differing
        ],
        "conflict_classification": classification,
        "confirm_only_conflict": classification == "CONFIRM_ONLY_CONFLICT",
        "ohlcv_material_conflict": classification in {"OHLC_ONLY_CONFLICT", "VOLUME_ONLY_CONFLICT", "OHLCV_MATERIAL_CONFLICT"},
        "symbol_or_schema_conflict": classification == "SYMBOL_OR_SCHEMA_CONFLICT",
        "unknown_conflict": classification == "UNKNOWN_CONFLICT",
    }


def main() -> None:
    generated_at = utc_now()
    diagnostic_summary = load_json(DIAGNOSTIC_SUMMARY)
    conflict_report = load_json(CONFLICT_REPORT)
    hash_report = load_json(HASH_VALIDATION_REPORT)
    conflict_group = validate_preflight(diagnostic_summary, conflict_report)
    source = source_identity_from_hash_report(hash_report)
    rows, schema_match = read_conflict_rows(source)
    diff = diff_rows(rows)

    if diff["confirm_only_conflict"]:
        next_module = NEXT_MODULE_CONFIRM_ONLY
        after_quality = AFTER_QUALITY_CONFIRM_ONLY
    elif diff["ohlcv_material_conflict"] or diff["symbol_or_schema_conflict"]:
        next_module = NEXT_MODULE_MATERIAL
        after_quality = AFTER_QUALITY_MATERIAL
    else:
        next_module = NEXT_MODULE_UNKNOWN
        after_quality = AFTER_QUALITY_UNKNOWN

    policy_preview = {
        "conflict_resolution_policy_preview_created": True,
        "preview_only": True,
        "conflict_classification": diff["conflict_classification"],
        "conflict_clearly_classifiable": diff["unknown_conflict"] is False,
        "resolution_now_allowed": False,
        "rebuild_now_allowed": False,
        "dedupe_now_allowed": False,
        "next_policy_module": next_module,
        "policy_requirements": [
            "Do not choose a conflicting row without a separate approved policy.",
            "Do not mark exact-dedupe rebuild safe while the conflicting duplicate remains unresolved.",
            "Do not synthesize, forward fill, backfill, alter OHLCV, or create a 1h output in this review.",
        ],
    }
    approval_record = {
        "approval_record_created": True,
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
    raw_rows_report = {
        "raw_conflict_rows_captured": True,
        "conflict_open_time": EXPECTED_CONFLICT_OPEN_TIME,
        "conflict_open_time_utc": iso_utc_from_ms(EXPECTED_CONFLICT_OPEN_TIME),
        "conflict_source_date": EXPECTED_CONFLICT_SOURCE_DATE,
        "conflict_source_file": EXPECTED_CONFLICT_SOURCE_FILE,
        "conflict_source_zip": source["source_zip_path"],
        "conflict_source_zip_sha256": source["source_zip_sha256"],
        "conflict_row_count": len(rows),
        "rows": rows,
        "prior_conflict_group": conflict_group,
    }
    field_diff_report = {
        "field_diff_report_created": True,
        "conflict_open_time": EXPECTED_CONFLICT_OPEN_TIME,
        **diff,
    }
    review = {
        "conflict_review_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "conflicting_duplicate_group_count": EXPECTED_CONFLICTING_GROUP_COUNT,
        "conflicting_duplicate_extra_row_count": EXPECTED_CONFLICTING_EXTRA_ROW_COUNT,
        "reviewed_conflicting_group_count": 1,
        "schema_match": schema_match,
        "source_identity_confirmed_from_hash_report": True,
        "source_zip_revalidated": True,
        "classification_rules_applied": True,
        **raw_rows_report,
        **field_diff_report,
        "policy_preview": policy_preview,
        "approval_record": approval_record,
    }
    replacement_checks = {
        "preflight_passed": True,
        "conflict_review_performed": True,
        "single_conflict_reviewed": review["reviewed_conflicting_group_count"] == 1,
        "raw_rows_captured": raw_rows_report["raw_conflict_rows_captured"] is True and raw_rows_report["conflict_row_count"] == 2,
        "field_diff_report_created": field_diff_report["field_diff_report_created"] is True,
        "differing_fields_listed": diff["differing_field_count"] == len(diff["differing_fields"]) and diff["differing_field_count"] > 0,
        "classification_valid": diff["conflict_classification"]
        in {
            "CONFIRM_ONLY_CONFLICT",
            "OHLC_ONLY_CONFLICT",
            "VOLUME_ONLY_CONFLICT",
            "OHLCV_MATERIAL_CONFLICT",
            "SYMBOL_OR_SCHEMA_CONFLICT",
            "UNKNOWN_CONFLICT",
        },
        "policy_preview_created": policy_preview["conflict_resolution_policy_preview_created"] is True,
        "approval_record_created": approval_record["approval_record_created"] is True,
        "future_policy_approved_only": approval_record["approval_grants_future_policy_next"] is True
        and approval_record["approval_grants_resolution_now"] is False
        and approval_record["approval_grants_rebuild_now"] is False
        and approval_record["approval_grants_dedupe_now"] is False,
        "no_download_api_browse_build_aggregation_dedupe": all(value is False for value in DANGEROUS_FLAGS.values()),
        "p0_preserved": True,
        "next_module_matches_classification": (
            (diff["confirm_only_conflict"] and next_module == NEXT_MODULE_CONFIRM_ONLY)
            or (diff["ohlcv_material_conflict"] and next_module == NEXT_MODULE_MATERIAL)
            or (diff["symbol_or_schema_conflict"] and next_module == NEXT_MODULE_MATERIAL)
            or (diff["unknown_conflict"] and next_module == NEXT_MODULE_UNKNOWN)
        ),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")
    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "historical_data_acquisition_okx_single_symbol_3_year_conflicting_duplicate_data_quality_review_status": PASS_STATUS,
        "conflict_review_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "conflicting_duplicate_group_count": EXPECTED_CONFLICTING_GROUP_COUNT,
        "conflicting_duplicate_extra_row_count": EXPECTED_CONFLICTING_EXTRA_ROW_COUNT,
        "reviewed_conflicting_group_count": 1,
        "conflict_open_time": EXPECTED_CONFLICT_OPEN_TIME,
        "conflict_open_time_utc": iso_utc_from_ms(EXPECTED_CONFLICT_OPEN_TIME),
        "conflict_source_date": EXPECTED_CONFLICT_SOURCE_DATE,
        "conflict_source_file": EXPECTED_CONFLICT_SOURCE_FILE,
        "conflict_source_zip": source["source_zip_path"],
        "conflict_row_count": len(rows),
        "differing_field_count": diff["differing_field_count"],
        "differing_fields": diff["differing_fields"],
        "conflict_classification": diff["conflict_classification"],
        "confirm_only_conflict": diff["confirm_only_conflict"],
        "ohlcv_material_conflict": diff["ohlcv_material_conflict"],
        "symbol_or_schema_conflict": diff["symbol_or_schema_conflict"],
        "unknown_conflict": diff["unknown_conflict"],
        "raw_conflict_rows_captured": True,
        "field_diff_report_created": True,
        "conflict_resolution_policy_preview_created": True,
        "approval_record_created": True,
        "approval_grants_resolution_now": False,
        "approval_grants_future_policy_next": True,
        "approval_grants_rebuild_now": False,
        "approval_grants_dedupe_now": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_csv_created": False,
        "strict_3y_completeness_claimed": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 9,
        "current_evidence_chain_quality_after_review": after_quality,
        "next_module": next_module,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": True,
        "tracked_python_count_at_review_run": tracked_python_count(),
    }
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_data_quality_review.json", review)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_raw_rows_report.json", raw_rows_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_field_diff_report.json", field_diff_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflict_resolution_policy_preview.json", policy_preview)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_review_approval_record.json", approval_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_review_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "module_name": MODULE_NAME,
            "generated_at_utc": utc_now(),
            "historical_data_acquisition_okx_single_symbol_3_year_conflicting_duplicate_data_quality_review_status": BLOCKED_STATUS,
            "conflict_review_performed": False,
            "target_symbol": TARGET_SYMBOL,
            "conflict_classification": "UNKNOWN_CONFLICT",
            "unknown_conflict": True,
            "raw_conflict_rows_captured": False,
            "field_diff_report_created": False,
            "conflict_resolution_policy_preview_created": False,
            "approval_record_created": False,
            "approval_grants_future_policy_next": False,
            "approval_grants_rebuild_now": False,
            "approval_grants_dedupe_now": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_csv_created": False,
            "active_p0_blocker_count": 1,
            "active_p1_attention_count": 9,
            "current_evidence_chain_quality_after_review": AFTER_QUALITY_UNKNOWN,
            "next_module": NEXT_MODULE_UNKNOWN,
            "replacement_checks_all_true": False,
            "blocked_reason": str(exc),
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_conflicting_duplicate_review_summary.json", blocked)
        write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
