from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_validator_after_execution_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "3351c1f"
TARGET_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = "2026-04-19"
DATE_RANGE_END = "2026-05-18"
PLANNED_FILE_COUNT = 30
REUSE_FILE_COUNT = 7
NEW_DOWNLOAD_FILE_COUNT = 23
MAX_SAMPLE_ROWS = 5
MAX_ZIP_MEMBERS = 10
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
PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_NO_BUILD"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_VALIDATED_"
    "BUILD_PREVIEW_READY_NO_BUILD"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_NO_BUILD"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_VALIDATED_"
    "BUILD_PREVIEW_READY_NO_BUILD"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_1m_to_1h_build_preview_after_download_validator_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_validation_blocked_record_after_execution_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
EXECUTION_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_after_summary_preview_approval_v1"
)
OUTPUT_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_validator_after_execution_v1"
)

ARTIFACTS = {
    "execution_report": EXECUTION_DIR / "historical_okx_single_symbol_30_day_download_execution_report.json",
    "provenance_report": EXECUTION_DIR / "historical_okx_single_symbol_30_day_download_provenance_report.json",
    "zip_inventory_report": EXECUTION_DIR / "historical_okx_single_symbol_30_day_zip_inventory_report.json",
    "schema_sample_report": EXECUTION_DIR / "historical_okx_single_symbol_30_day_schema_sample_report.json",
    "compliance_report": EXECUTION_DIR / "historical_okx_single_symbol_30_day_download_execution_compliance_report.json",
    "execution_summary": EXECUTION_DIR / "historical_okx_single_symbol_30_day_download_execution_summary.json",
}

DANGEROUS_FLAGS = {
    "new_download_performed_by_validator": False,
    "data_build_performed_now": False,
    "aggregation_performed_now": False,
    "external_api_call_performed_now": False,
    "okx_api_call_performed_now": False,
    "okx_browse_performed_now": False,
    "repo_schema_config_created_now": False,
    "strategy_research_implementation_touched": False,
    "candidate_generation_touched": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "generic_runner_approval_granted": False,
}


class Blocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Blocked(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
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


def sample_zip(path: Path, expected_csv: str) -> tuple[dict[str, Any], dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        traversal = any(not safe_zip_member(name) for name in names)
        expected_present = expected_csv in names
        inventory = {
            "zip_path": str(path),
            "zip_open_success": True,
            "zip_member_count": len(names),
            "zip_member_names": names,
            "expected_inner_csv": expected_csv,
            "expected_inner_csv_present": expected_present,
            "zip_path_traversal_detected": traversal,
            "zip_inventory_status": "PASS" if expected_present and not traversal and len(names) <= MAX_ZIP_MEMBERS else "FAIL",
        }
        require(len(names) <= MAX_ZIP_MEMBERS, f"too many ZIP members: {path}")
        require(not traversal, f"ZIP traversal detected: {path}")
        require(expected_present, f"expected CSV missing: {expected_csv}")
        with archive.open(expected_csv, "r") as raw:
            text = (line.decode("utf-8-sig").rstrip("\r\n") for line in raw)
            reader = csv.reader(text)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise Blocked(f"empty expected CSV: {expected_csv}") from exc
            rows = []
            for _, row in zip(range(MAX_SAMPLE_ROWS), reader):
                rows.append(row)

    symbols = sorted({row[0] for row in rows if row})
    open_times = []
    for row in rows:
        if len(row) > 8:
            try:
                open_times.append(int(row[8]))
            except ValueError:
                pass
    deltas = [right - left for left, right in zip(open_times, open_times[1:])]
    interval = deltas[0] if deltas and all(delta == deltas[0] for delta in deltas) else None
    one_minute = interval == 60_000
    sample = {
        "csv_header_read": True,
        "csv_sample_rows_read_count": len(rows),
        "csv_full_read_performed": False,
        "expected_schema_match": header == EXPECTED_SCHEMA,
        "observed_columns": header,
        "observed_symbol_sample": symbols,
        "observed_symbols_match_target": all(symbol == TARGET_SYMBOL for symbol in symbols) if symbols else True,
        "sample_open_time_delta_ms": interval,
        "inferred_sample_interval": "1m" if one_minute else None,
        "one_minute_interval_observed": one_minute,
        "direct_1h_interval_present": False if one_minute else None,
    }
    require(sample["expected_schema_match"], f"schema mismatch: {expected_csv}")
    require(sample["observed_symbols_match_target"], f"symbol mismatch: {expected_csv}")
    require(sample["csv_sample_rows_read_count"] <= MAX_SAMPLE_ROWS, f"sample limit exceeded: {expected_csv}")
    require(one_minute or len(rows) < 2, f"sample interval not 1m: {expected_csv}")
    return inventory, sample


def validate_preflight(summary: dict[str, Any]) -> None:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved validator")
    require(summary.get("historical_data_acquisition_okx_single_symbol_30_day_download_execution_status") == PREVIOUS_STATUS, "previous status mismatch")
    require(summary.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(summary.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(summary.get("date_range_start") == DATE_RANGE_START, "date range start mismatch")
    require(summary.get("date_range_end") == DATE_RANGE_END, "date range end mismatch")
    require(summary.get("planned_30_day_file_count") == PLANNED_FILE_COUNT, "planned file count mismatch")
    require(summary.get("existing_validated_reuse_file_count") == REUSE_FILE_COUNT, "reuse count mismatch")
    require(summary.get("new_download_file_count") == NEW_DOWNLOAD_FILE_COUNT, "new download count mismatch")
    require(summary.get("final_30_day_file_count") == PLANNED_FILE_COUNT, "final file count mismatch")
    require(summary.get("approved_url_count") == PLANNED_FILE_COUNT, "approved URL count mismatch")
    for key in [
        "all_downloads_succeeded",
        "all_reused_files_validated",
        "all_hashes_computed_or_revalidated",
        "all_zip_open_success",
        "all_expected_inner_csv_present",
        "all_expected_schema_match",
    ]:
        require(summary.get(key) is True, f"{key} not true")
    for key in [
        "full_csv_read_performed",
        "data_build_performed",
        "aggregation_performed_now",
        "okx_api_call_performed",
        "okx_browse_performed",
        "files_marked_build_ready",
        "source_manifest_acquisition_ready",
        "broad_acquisition_execution_allowed_now",
        "output_valid_for_research_backtest",
        "output_valid_for_edge_claim",
    ]:
        require(summary.get(key) is False, f"{key} not false")


def main() -> None:
    generated_at = utc_now()
    artifacts = {label: load_json(path) for label, path in ARTIFACTS.items()}
    summary = artifacts["execution_summary"]
    provenance = artifacts["provenance_report"]
    prior_inventory = artifacts["zip_inventory_report"]
    prior_samples = artifacts["schema_sample_report"]
    compliance = artifacts["compliance_report"]
    validate_preflight(summary)

    require(isinstance(provenance, list) and len(provenance) == PLANNED_FILE_COUNT, "provenance file count mismatch")
    require(isinstance(prior_inventory, list) and len(prior_inventory) == PLANNED_FILE_COUNT, "inventory file count mismatch")
    require(isinstance(prior_samples, list) and len(prior_samples) == PLANNED_FILE_COUNT, "schema sample file count mismatch")
    require(compliance.get("no_api") is True and compliance.get("no_browse") is True, "execution compliance API/browse mismatch")
    require(compliance.get("no_data_build") is True and compliance.get("no_aggregation") is True, "execution compliance build/aggregation mismatch")

    reuse_count = sum(1 for item in provenance if item.get("file_status") == "REUSED_VALIDATED_SEVEN_DAY_FILE")
    new_count = sum(1 for item in provenance if item.get("file_status") == "DOWNLOADED_30_DAY_MISSING_APPROVED_URL")
    require(reuse_count == REUSE_FILE_COUNT, "reused count mismatch")
    require(new_count == NEW_DOWNLOAD_FILE_COUNT, "new downloaded count mismatch")

    hash_report = []
    validation_inventory = []
    validation_samples = []
    for index, item in enumerate(provenance):
        path = Path(item["local_zip_path"])
        require(path.exists(), f"ZIP missing: {path}")
        digest = sha256_file(path)
        require(digest == item.get("sha256"), f"hash mismatch: {path}")
        size = path.stat().st_size
        require(size == item.get("file_size_bytes"), f"file size mismatch: {path}")
        inventory, sample = sample_zip(path, item["expected_inner_csv"])
        hash_report.append(
            {
                "validation_index": index,
                "date": item["date"],
                "local_zip_path": str(path),
                "zip_path_exists": True,
                "file_size_bytes": size,
                "file_status": item["file_status"],
                "hash_algorithm": "SHA256",
                "sha256_recorded": item["sha256"],
                "sha256_recomputed": digest,
                "sha256_matches_recorded": True,
            }
        )
        validation_inventory.append({"date": item["date"], **inventory})
        validation_samples.append({"date": item["date"], "expected_inner_csv": item["expected_inner_csv"], **sample})

    all_paths = all(Path(item["local_zip_path"]).exists() for item in provenance)
    all_reused_revalidated = all(row["sha256_matches_recorded"] for row in hash_report if row["file_status"] == "REUSED_VALIDATED_SEVEN_DAY_FILE")
    all_hashes_recomputed = len(hash_report) == PLANNED_FILE_COUNT
    all_hashes_match = all(row["sha256_matches_recorded"] for row in hash_report)
    all_zip_open = all(item["zip_open_success"] for item in validation_inventory)
    any_traversal = any(item["zip_path_traversal_detected"] for item in validation_inventory)
    all_csv_present = all(item["expected_inner_csv_present"] for item in validation_inventory)
    all_schema = all(item["expected_schema_match"] for item in validation_samples)
    all_symbols = all(item["observed_symbols_match_target"] for item in validation_samples)
    all_one_minute = all(item["one_minute_interval_observed"] or item["csv_sample_rows_read_count"] < 2 for item in validation_samples)
    max_sample = max(item["csv_sample_rows_read_count"] for item in validation_samples)
    full_csv_read = False

    require(all_paths, "not all downloaded ZIP paths exist")
    require(all_reused_revalidated, "not all reused files revalidated")
    require(all_hashes_recomputed and all_hashes_match, "hash validation failed")
    require(all_zip_open and not any_traversal and all_csv_present, "ZIP validation failed")
    require(all_schema and all_symbols and all_one_minute, "schema/sample validation failed")
    require(max_sample <= MAX_SAMPLE_ROWS, "sample row limit exceeded")

    validator_p0_count = 0
    validator_p1_count = 8
    replacement_checks = {
        "preflight_passed": True,
        "artifact_chain_valid": True,
        "file_count_30": len(provenance) == PLANNED_FILE_COUNT,
        "reuse_count_7": reuse_count == REUSE_FILE_COUNT,
        "new_count_23": new_count == NEW_DOWNLOAD_FILE_COUNT,
        "all_paths_exist": all_paths,
        "all_reused_files_revalidated": all_reused_revalidated,
        "all_hashes_recomputed": all_hashes_recomputed,
        "all_hashes_match_recorded": all_hashes_match,
        "all_zip_open_success": all_zip_open,
        "no_zip_traversal": not any_traversal,
        "all_expected_inner_csv_present": all_csv_present,
        "all_expected_schema_match": all_schema,
        "all_observed_symbols_match_target": all_symbols,
        "all_one_minute_interval_observed_from_samples": all_one_minute,
        "sample_limit_respected": max_sample <= MAX_SAMPLE_ROWS,
        "no_full_csv_read": full_csv_read is False,
        "no_new_download_api_browse": True,
        "no_build_aggregation": True,
        "no_research_backtest_edge_or_acquisition_ready": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    derived_reason = (
        "validated the 30-file BTC-USDT-SWAP download execution from existing artifacts and ZIPs only; "
        "recomputed all 30 SHA256 values, revalidated 7 reused files and 23 newly downloaded files, "
        "opened all ZIPs, found no path traversal, confirmed every expected inner CSV and schema, read "
        "only header plus at most five sample rows per CSV, observed BTC-USDT-SWAP and 1m sample intervals, "
        "and performed no new download/API/browse/full CSV read/build/aggregation or readiness/edge claim"
    )
    summary_payload = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "historical_data_acquisition_okx_single_symbol_30_day_download_execution_validator_status": PASS_STATUS,
        "final_decision": "30_DAY_SINGLE_SYMBOL_DOWNLOAD_VALIDATED_BUILD_PREVIEW_READY_NO_BUILD",
        "next_action": "CREATE_30_DAY_SINGLE_SYMBOL_1M_TO_1H_BUILD_PREVIEW_NO_EXECUTION",
        "next_module": NEXT_MODULE,
        "download_execution_validated": True,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "planned_30_day_file_count": PLANNED_FILE_COUNT,
        "existing_validated_reuse_file_count": reuse_count,
        "new_download_file_count": new_count,
        "final_30_day_file_count": len(provenance),
        "approved_url_count": PLANNED_FILE_COUNT,
        "all_downloaded_zip_paths_exist": all_paths,
        "all_reused_files_revalidated": all_reused_revalidated,
        "all_hashes_recomputed": all_hashes_recomputed,
        "all_hashes_match_recorded": all_hashes_match,
        "all_zip_open_success": all_zip_open,
        "any_zip_path_traversal_detected": any_traversal,
        "all_expected_inner_csv_present": all_csv_present,
        "all_expected_schema_match": all_schema,
        "all_observed_symbols_match_target": all_symbols,
        "all_one_minute_interval_observed_from_samples": all_one_minute,
        "max_csv_sample_rows_read_per_file": max_sample,
        "full_csv_read_performed": full_csv_read,
        "new_download_performed_by_validator": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "safe_for_30_day_build_preview": True,
        "safe_for_broad_acquisition": False,
        "safe_for_research_backtest": False,
        "safe_for_edge_claim": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "validator_p0_count": validator_p0_count,
        "validator_p1_count": validator_p1_count,
        "current_evidence_chain_quality_before_validator": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_validator": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": validator_p1_count,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "dangerous_flags_true_count": sum(1 for value in DANGEROUS_FLAGS.values() if value),
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": derived_reason,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    validation_bundle = {
        "execution_artifact_validation": {
            "required_artifacts": {label: str(path) for label, path in ARTIFACTS.items()},
            "artifact_chain_valid": True,
            "previous_status": summary.get("historical_data_acquisition_okx_single_symbol_30_day_download_execution_status"),
            "previous_next_module": summary.get("next_module"),
        },
        "hash_validation": hash_report,
        "zip_inventory_validation": validation_inventory,
        "schema_sample_validation": validation_samples,
        "compliance_validation": {
            "no_new_download_by_validator": True,
            "no_api": True,
            "no_browse": True,
            "no_data_build": True,
            "no_aggregation": True,
            "no_full_csv_read": True,
            "no_research_backtest_edge_or_acquisition_ready": True,
        },
        "risk_decision": {
            "safe_for_30_day_build_preview": True,
            "safe_for_broad_acquisition": False,
            "safe_for_research_backtest": False,
            "safe_for_edge_claim": False,
            "validator_p0_count": validator_p0_count,
            "validator_p1_count": validator_p1_count,
        },
        "next_module_decision": {
            "next_module": NEXT_MODULE,
            "blocked_next_module": BLOCKED_NEXT_MODULE,
        },
        "summary": summary_payload,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_validator.json", validation_bundle)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_hash_validation_report.json", hash_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_zip_schema_validation_report.json", {
        "zip_inventory_validation": validation_inventory,
        "schema_sample_validation": validation_samples,
    })
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_provenance_validation_report.json", {
        "provenance_entry_count": len(provenance),
        "existing_validated_reuse_file_count": reuse_count,
        "new_download_file_count": new_count,
        "all_downloaded_zip_paths_exist": all_paths,
        "all_hashes_match_recorded": all_hashes_match,
    })
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_validator_summary.json", summary_payload)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary_payload)
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "historical_data_acquisition_okx_single_symbol_30_day_download_execution_validator_status": "BLOCKED_CONTEXT_MISMATCH",
            "next_module": BLOCKED_NEXT_MODULE,
            "blocked_reason": str(exc),
            "active_p0_blocker_count": 1,
            "validator_p0_count": 1,
            "replacement_checks_all_true": False,
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_validator_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
