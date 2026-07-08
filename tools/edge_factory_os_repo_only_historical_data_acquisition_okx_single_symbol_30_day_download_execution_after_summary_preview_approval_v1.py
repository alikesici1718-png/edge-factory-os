from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_after_summary_preview_approval_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "81c2d9c"
TARGET_SYMBOL = "BTC-USDT-SWAP"
DATE_RANGE_START = "2026-04-19"
DATE_RANGE_END = "2026-05-18"
PLANNED_FILE_COUNT = 30
REUSE_FILE_COUNT = 7
NEW_DOWNLOAD_FILE_COUNT = 23
MAX_ZIP_SIZE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_ZIP_SIZE_BYTES = 30 * MAX_ZIP_SIZE_BYTES
MAX_ZIP_MEMBERS = 10
MAX_SAMPLE_ROWS = 5
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
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_PIPELINE_SUMMARY_"
    "30_DAY_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_DOWNLOAD_YET"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_NO_BUILD"
)
BEFORE_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_SMALL_RANGE_PIPELINE_SUMMARY_"
    "30_DAY_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_NEXT_NO_DOWNLOAD_YET"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_30_DAY_DOWNLOAD_EXECUTED_"
    "PENDING_VALIDATOR_NO_BUILD"
)
NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_validator_after_execution_v1.py"
)
BLOCKED_NEXT_MODULE = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_blocked_record_after_summary_preview_approval_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "30_day_download_execution_after_summary_preview_approval_v1"
)
QUARANTINE_DIR = OUTPUT_DIR / "downloaded_single_symbol_30_day_quarantine"

SUMMARY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "small_range_pipeline_summary_after_build_validator_v1"
)
SMALL_RANGE_DOWNLOAD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_"
    "download_execution_after_preview_approval_v1"
)
SMALL_RANGE_DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_small_range_"
    "download_execution_validator_after_execution_v1"
)

SUMMARY_ARTIFACT = SUMMARY_DIR / "historical_okx_single_symbol_small_range_pipeline_summary_after_build_validator_summary.json"
PREVIEW_ARTIFACT = SUMMARY_DIR / "historical_okx_single_symbol_30_day_download_preview.json"
APPROVAL_ARTIFACT = SUMMARY_DIR / "historical_okx_single_symbol_30_day_download_approval_record.json"
REUSE_PROVENANCE_ARTIFACT = SMALL_RANGE_DOWNLOAD_DIR / "historical_okx_single_symbol_small_range_download_provenance_report.json"
REUSE_HASH_VALIDATION_ARTIFACT = SMALL_RANGE_DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_small_range_hash_validation_report.json"

DANGEROUS_FLAGS = {
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


def date_from_url(url: str) -> str:
    filename = url.rsplit("/", 1)[-1]
    require(filename.startswith(f"{TARGET_SYMBOL}-candlesticks-"), f"unexpected URL file name: {url}")
    require(filename.endswith(".zip"), f"unexpected URL suffix: {url}")
    return filename.removeprefix(f"{TARGET_SYMBOL}-candlesticks-").removesuffix(".zip")


def expected_csv_for_date(day: str) -> str:
    return f"{TARGET_SYMBOL}-candlesticks-{day}.csv"


def ensure_safe_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    posix = PurePosixPath(normalized)
    if normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        return False
    if posix.is_absolute() or any(part == ".." for part in posix.parts):
        return False
    if ":" in posix.parts[0]:
        return False
    return True


def download_file(url: str, dest: Path) -> tuple[int, str]:
    tmp = dest.with_suffix(dest.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    downloaded = 0
    with urllib.request.urlopen(url, timeout=60) as response:
        with tmp.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > MAX_ZIP_SIZE_BYTES:
                    raise Blocked(f"download exceeds max ZIP size: {url}")
                handle.write(chunk)
    require(downloaded > 0, f"empty download: {url}")
    tmp.replace(dest)
    return downloaded, sha256_file(dest)


def inspect_zip_and_sample(path: Path, expected_csv: str) -> tuple[dict[str, Any], dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        traversal = any(not ensure_safe_member(name) for name in names)
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
        require(not traversal, f"ZIP traversal risk: {path}")
        require(expected_present, f"expected inner CSV missing: {expected_csv}")

        with archive.open(expected_csv, "r") as raw:
            text = (line.decode("utf-8-sig").rstrip("\r\n") for line in raw)
            reader = csv.reader(text)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise Blocked(f"empty CSV in ZIP: {expected_csv}") from exc
            rows: list[list[str]] = []
            for _, row in zip(range(MAX_SAMPLE_ROWS), reader):
                rows.append(row)

    symbol_sample = sorted({row[0] for row in rows if row})
    deltas: list[int] = []
    open_times: list[int] = []
    for row in rows:
        if len(row) > 8:
            try:
                open_times.append(int(row[8]))
            except ValueError:
                pass
    for left, right in zip(open_times, open_times[1:]):
        deltas.append(right - left)
    interval = deltas[0] if deltas and all(delta == deltas[0] for delta in deltas) else None
    one_minute = interval == 60_000
    schema_match = header == EXPECTED_SCHEMA
    symbols_match = all(symbol == TARGET_SYMBOL for symbol in symbol_sample) if symbol_sample else True
    sample = {
        "csv_header_read": True,
        "csv_sample_rows_read_count": len(rows),
        "csv_full_read_performed": False,
        "expected_schema_match": schema_match,
        "observed_columns": header,
        "observed_symbol_sample": symbol_sample,
        "observed_symbols_match_target": symbols_match,
        "sample_open_time_delta_ms": interval,
        "inferred_sample_interval": "1m" if one_minute else None,
        "one_minute_interval_observed": one_minute,
        "direct_1h_interval_present": False if one_minute else None,
    }
    require(schema_match, f"schema mismatch: {expected_csv}")
    require(symbols_match, f"symbol mismatch in sample: {expected_csv}")
    require(len(rows) <= MAX_SAMPLE_ROWS, f"sample row count exceeded: {expected_csv}")
    require(one_minute or len(rows) < 2, f"sample interval is not 1m: {expected_csv}")
    return inventory, sample


def make_reuse_map(reuse_provenance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in reuse_provenance.get("per_file_download_provenance", []):
        out[item["date"]] = item
    return out


def validate_preflight(summary: dict[str, Any], preview: dict[str, Any], approval: dict[str, Any]) -> list[str]:
    head = run_git(["rev-parse", "--short", "HEAD"])
    require(head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(summary.get("historical_data_acquisition_okx_single_symbol_small_range_pipeline_summary_status") == PREVIOUS_STATUS, "previous status mismatch")
    require(summary.get("next_module") == REQUESTED_MODULE, "next_module mismatch")
    require(preview.get("planned_30_day_file_count") == PLANNED_FILE_COUNT, "planned file count mismatch")
    require(len(preview.get("planned_urls", [])) == PLANNED_FILE_COUNT, "approved URL count mismatch")
    require(preview.get("existing_validated_reuse_file_count") == REUSE_FILE_COUNT, "reuse count mismatch")
    require(preview.get("missing_download_file_count") == NEW_DOWNLOAD_FILE_COUNT, "missing download count mismatch")
    require(preview.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(preview.get("date_range_start") == DATE_RANGE_START, "date range start mismatch")
    require(preview.get("date_range_end") == DATE_RANGE_END, "date range end mismatch")
    require(approval.get("approval_grants_30_day_download_execution_next") is True, "download execution approval missing")
    require(approval.get("next_module") == REQUESTED_MODULE, "approval next_module mismatch")
    planned_urls = list(preview["planned_urls"])
    require(len(set(planned_urls)) == PLANNED_FILE_COUNT, "duplicate approved URLs")
    require(all(TARGET_SYMBOL in url for url in planned_urls), "multi-symbol URL detected")
    require(date_from_url(planned_urls[0]) == DATE_RANGE_START, "first URL date mismatch")
    require(date_from_url(planned_urls[-1]) == DATE_RANGE_END, "last URL date mismatch")
    return planned_urls


def main() -> None:
    generated_at = utc_now()
    summary_artifact = load_json(SUMMARY_ARTIFACT)
    preview = load_json(PREVIEW_ARTIFACT)
    approval = load_json(APPROVAL_ARTIFACT)
    reuse_provenance = load_json(REUSE_PROVENANCE_ARTIFACT)
    reuse_hash_validation = load_json(REUSE_HASH_VALIDATION_ARTIFACT)
    planned_urls = validate_preflight(summary_artifact, preview, approval)
    reuse_map = make_reuse_map(reuse_provenance)
    require(reuse_hash_validation.get("all_hashes_validated") is True, "reuse hashes not validated")

    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    provenance: list[dict[str, Any]] = []
    zip_inventory: list[dict[str, Any]] = []
    schema_samples: list[dict[str, Any]] = []
    used_urls: list[str] = []
    new_download_count = 0
    reuse_count = 0
    total_size = 0

    approved_url_set = set(planned_urls)
    for url in planned_urls:
        require(url in approved_url_set, f"URL outside approved manifest: {url}")
        used_urls.append(url)
        day = date_from_url(url)
        expected_csv = expected_csv_for_date(day)
        filename = url.rsplit("/", 1)[-1]
        now = utc_now()

        if day in preview.get("existing_validated_reuse_dates", []):
            require(day in reuse_map, f"reuse provenance missing for {day}")
            reuse_item = reuse_map[day]
            local_path = Path(reuse_item["downloaded_zip_path"])
            require(local_path.exists(), f"reused ZIP missing: {local_path}")
            digest = sha256_file(local_path)
            require(digest == reuse_item["downloaded_zip_sha256"], f"reused SHA256 mismatch for {day}")
            size = local_path.stat().st_size
            require(size == reuse_item["downloaded_zip_size_bytes"], f"reused size mismatch for {day}")
            status = "REUSED_VALIDATED_SEVEN_DAY_FILE"
            timestamp = reuse_item.get("download_timestamp_utc")
            reuse_count += 1
        elif day in preview.get("missing_download_dates", []):
            local_path = QUARANTINE_DIR / filename
            size, digest = download_file(url, local_path)
            status = "DOWNLOADED_30_DAY_MISSING_APPROVED_URL"
            timestamp = now
            new_download_count += 1
        else:
            raise Blocked(f"date is neither reuse nor missing approved: {day}")

        require(size <= MAX_ZIP_SIZE_BYTES, f"ZIP exceeds size limit for {day}")
        total_size += size
        require(total_size <= MAX_TOTAL_ZIP_SIZE_BYTES, "total ZIP size exceeds limit")
        inventory, sample = inspect_zip_and_sample(local_path, expected_csv)
        zip_inventory.append({"date": day, **inventory})
        schema_samples.append({"date": day, "expected_inner_csv": expected_csv, **sample})
        provenance.append(
            {
                "date": day,
                "source_url": url,
                "local_zip_path": str(local_path),
                "local_zip_file_name": local_path.name,
                "file_size_bytes": size,
                "sha256": digest,
                "hash_algorithm": "SHA256",
                "hash_computed_or_revalidated_after_execution": True,
                "download_or_reuse_timestamp_utc": timestamp,
                "expected_inner_csv": expected_csv,
                "file_status": status,
            }
        )

    require(new_download_count == NEW_DOWNLOAD_FILE_COUNT, "new download count mismatch")
    require(reuse_count == REUSE_FILE_COUNT, "reuse count mismatch")
    require(len(provenance) == PLANNED_FILE_COUNT, "final file set count mismatch")
    require(set(used_urls) == approved_url_set, "used URLs do not match approved manifest")

    all_hashes = all(item.get("sha256") and len(item["sha256"]) == 64 for item in provenance)
    all_zip_open = all(item["zip_open_success"] for item in zip_inventory)
    all_csv_present = all(item["expected_inner_csv_present"] for item in zip_inventory)
    any_traversal = any(item["zip_path_traversal_detected"] for item in zip_inventory)
    all_schema = all(item["expected_schema_match"] for item in schema_samples)
    all_one_minute = all(item["one_minute_interval_observed"] or item["csv_sample_rows_read_count"] < 2 for item in schema_samples)
    max_sample_rows = max(item["csv_sample_rows_read_count"] for item in schema_samples)
    observed_symbols = sorted({symbol for sample in schema_samples for symbol in sample.get("observed_symbol_sample", [])})
    require(not any_traversal, "ZIP traversal detected")
    require(observed_symbols in ([TARGET_SYMBOL], []), f"unexpected symbols: {observed_symbols}")

    compliance_report = {
        "no_api": True,
        "no_browse": True,
        "no_unapproved_url": True,
        "no_full_csv_read": True,
        "no_data_build": True,
        "no_aggregation": True,
        "no_multi_symbol": True,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "no_strategy_backtest_candidate": True,
        "no_runtime_capital_live": True,
        "no_generic_runner": True,
        "no_repo_schema_config": True,
    }
    replacement_checks = {
        "preflight_passed": True,
        "approved_url_list_used": set(used_urls) == approved_url_set,
        "approved_url_count_30": len(used_urls) == 30,
        "new_download_count_23": new_download_count == 23,
        "reuse_count_7": reuse_count == 7,
        "final_file_count_30": len(provenance) == 30,
        "all_downloads_succeeded": new_download_count == 23,
        "all_reused_files_validated": reuse_count == 7,
        "all_hashes_computed_or_revalidated": all_hashes,
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_csv_present,
        "all_expected_schema_match": all_schema,
        "sample_limit_respected": max_sample_rows <= MAX_SAMPLE_ROWS,
        "full_csv_read_false": True,
        "no_build_aggregation_api_browse": True,
        "no_readiness_or_edge_claim": True,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks failed")

    summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": generated_at,
        "historical_data_acquisition_okx_single_symbol_30_day_download_execution_status": PASS_STATUS,
        "final_decision": "30_DAY_SINGLE_SYMBOL_DOWNLOAD_EXECUTED_PENDING_VALIDATOR_NO_BUILD",
        "next_action": "VALIDATE_30_DAY_SINGLE_SYMBOL_DOWNLOAD_EXECUTION_NO_BUILD",
        "next_module": NEXT_MODULE,
        "download_execution_performed": True,
        "target_symbol": TARGET_SYMBOL,
        "date_range_start": DATE_RANGE_START,
        "date_range_end": DATE_RANGE_END,
        "planned_30_day_file_count": PLANNED_FILE_COUNT,
        "existing_validated_reuse_file_count": reuse_count,
        "new_download_file_count": new_download_count,
        "final_30_day_file_count": len(provenance),
        "approved_url_list_used": True,
        "approved_url_count": len(used_urls),
        "all_downloads_succeeded": True,
        "all_reused_files_validated": True,
        "all_hashes_computed_or_revalidated": all_hashes,
        "hash_algorithm": "SHA256",
        "all_zip_open_success": all_zip_open,
        "all_expected_inner_csv_present": all_csv_present,
        "any_zip_path_traversal_detected": any_traversal,
        "all_expected_schema_match": all_schema,
        "all_one_minute_interval_observed_from_samples": all_one_minute,
        "max_csv_sample_rows_read_per_file": max_sample_rows,
        "full_csv_read_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "files_marked_build_ready": False,
        "source_manifest_acquisition_ready": False,
        "broad_acquisition_execution_allowed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "data_download_performed": True,
        "data_fetch_performed": True,
        "external_download_allowed_now": True,
        "external_api_allowed_now": False,
        "okx_download_performed": True,
        "current_evidence_chain_quality_before_execution": BEFORE_QUALITY,
        "current_evidence_chain_quality_after_execution": AFTER_QUALITY,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": 8,
        "dormant_repo_attention_count": 716,
        "generic_runner_implementation_remains_blocked": True,
        "schema_or_config_created": False,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "dangerous_flags": DANGEROUS_FLAGS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
        "dangerous_flags_true_count": sum(1 for value in DANGEROUS_FLAGS.values() if value),
        "derived_live_repo_post_check": PASS_STATUS,
        "derived_live_repo_post_check_reason": (
            "downloaded exactly the 23 missing approved BTC-USDT-SWAP OKX daily ZIPs for "
            "2026-04-19 through 2026-05-11, reused the 7 already validated ZIPs for 2026-05-12 "
            "through 2026-05-18, produced a 30-file provenance set, computed or revalidated every "
            "SHA256, opened all ZIPs, confirmed expected inner CSVs and schema with header plus at "
            "most five sample rows only, and performed no API/browse/full CSV read/build/aggregation "
            "or research/backtest/edge/acquisition-ready claim"
        ),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    report = {
        "execution_scope": {
            "download_execution_performed": True,
            "target_symbol": TARGET_SYMBOL,
            "date_range_start": DATE_RANGE_START,
            "date_range_end": DATE_RANGE_END,
            "planned_30_day_file_count": PLANNED_FILE_COUNT,
            "existing_validated_reuse_file_count": reuse_count,
            "new_download_file_count": new_download_count,
            "final_30_day_file_count": len(provenance),
            "approved_url_list_used": True,
            "approved_url_count": len(used_urls),
            "output_directory": str(OUTPUT_DIR),
            "no_api": True,
            "no_browse": True,
            "no_data_build": True,
            "no_aggregation": True,
        },
        "per_file_provenance": provenance,
        "zip_inventory": zip_inventory,
        "schema_sample": schema_samples,
        "execution_compliance": compliance_report,
        "next_module_decision": {"next_module": NEXT_MODULE, "blocked_next_module": BLOCKED_NEXT_MODULE},
        "summary": summary,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_report.json", report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_provenance_report.json", provenance)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_zip_inventory_report.json", zip_inventory)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_schema_sample_report.json", schema_samples)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_compliance_report.json", compliance_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_summary.json", summary)
    write_json(OUTPUT_DIR / f"{MODULE_NAME}_latest.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Blocked as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "historical_data_acquisition_okx_single_symbol_30_day_download_execution_status": "BLOCKED_CONTEXT_MISMATCH",
            "next_module": BLOCKED_NEXT_MODULE,
            "blocked_reason": str(exc),
            "active_p0_blocker_count": 1,
            "replacement_checks_all_true": False,
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
    except Exception as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        blocked = {
            "historical_data_acquisition_okx_single_symbol_30_day_download_execution_status": "BLOCKED_CONTEXT_MISMATCH",
            "next_module": BLOCKED_NEXT_MODULE,
            "blocked_reason": repr(exc),
            "active_p0_blocker_count": 1,
            "replacement_checks_all_true": False,
        }
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_30_day_download_execution_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1)
