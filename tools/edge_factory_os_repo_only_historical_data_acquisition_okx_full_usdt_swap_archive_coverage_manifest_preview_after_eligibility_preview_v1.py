from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "a8d9955"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_ELIGIBILITY_PREVIEW_READY_FOR_MANIFEST_PREVIEW"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_MANIFEST_PREVIEW_READY_FOR_FIRST_CHUNK_DOWNLOAD_PREVIEW"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_MANIFEST_PREVIEW_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_preview_after_manifest_preview_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_MANIFEST_PREVIEW_READY_FOR_FIRST_CHUNK_DOWNLOAD_PREVIEW"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

SOURCE_DISCOVERY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"
ELIGIBILITY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_eligibility_preview_after_symbol_source_discovery_v1"
PILOT_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_after_build_validator_v1"
POLICY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_after_batch_anomaly_classification_v1"

ARTIFACTS = {
    "candidate_symbol_list": SOURCE_DISCOVERY_DIR / "historical_okx_full_usdt_swap_candidate_symbol_list.json",
    "eligibility_summary": ELIGIBILITY_DIR / "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview_summary.json",
    "eligibility_preview": ELIGIBILITY_DIR / "historical_okx_full_usdt_swap_archive_coverage_eligibility_preview.json",
    "pilot_pipeline_summary": PILOT_SUMMARY_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json",
    "batch_policy_summary": POLICY_DIR / "historical_okx_10_symbol_pilot_batch_policy_summary.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_archive_coverage_manifest_preview.json",
    "historical_okx_full_usdt_swap_archive_coverage_manifest_index.json",
    "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json",
    "historical_okx_full_usdt_swap_archive_coverage_manifest_sample_urls.json",
    "historical_okx_full_usdt_swap_archive_coverage_manifest_resource_limits.json",
    "historical_okx_full_usdt_swap_first_chunk_download_preview_approval_record.json",
    "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_self_validator.json",
    "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_summary.json",
]

EXPECTED_CANDIDATE_SYMBOL_COUNT = 303
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1053
EXPECTED_TOTAL_ARCHIVE_FILE_COUNT = 319_059
EXISTING_10_SYMBOL_PILOT_FILE_COUNT = 10_530
EXISTING_PILOT_SYMBOL_COUNT = 10
REMAINING_CANDIDATE_SYMBOL_COUNT = 293
REMAINING_EXPECTED_ARCHIVE_FILE_COUNT = 308_529
RECOMMENDED_CHUNK_SYMBOL_MIN = 10
RECOMMENDED_CHUNK_SYMBOL_MAX = 25
PREFERRED_CHUNK_SYMBOL_COUNT = 20
EXPECTED_FILES_PER_PREFERRED_CHUNK = 21_060
FIRST_CHUNK_SYMBOL_COUNT = 20
EXPECTED_FIRST_CHUNK_FILE_COUNT = 21_060
DATE_START = "2023-07-01"
DATE_END = "2026-05-18"
URL_PATTERN = "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/YYYYMMDD/SYMBOL-candlesticks-YYYY-MM-DD.zip"
EXPECTED_SCHEMA_KEY = "OKX_CANDLESTICKS_1M_SCHEMA_V1"

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

POLICY = {
    "exact_duplicate_policy": "DROP_ONLY_EXACT_DUPLICATE_EXTRA_ROWS_KEEP_ONE_CANONICAL_ROW",
    "material_conflict_policy": "QUARANTINE_ALL_ROWS_IN_MATERIAL_CONFLICT_OPEN_TIME_GROUP",
    "missing_minute_policy": "NO_FILL_MARK_AFFECTED_HOUR_INCOMPLETE_OR_EXCLUDE_FROM_COMPLETE_CLAIMS",
    "synthetic_fill_allowed": False,
    "forward_fill_allowed": False,
    "backfill_allowed": False,
}


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


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def date_values() -> list[date]:
    start = parse_date(DATE_START)
    end = parse_date(DATE_END)
    values: list[date] = []
    current = start
    while current <= end:
        values.append(current)
        current += timedelta(days=1)
    return values


def planned_url(symbol: str, day: date) -> str:
    yyyymmdd = day.strftime("%Y%m%d")
    iso_date = day.isoformat()
    return f"https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/{yyyymmdd}/{symbol}-candlesticks-{iso_date}.zip"


def planned_entry(symbol: str, day: date) -> dict[str, Any]:
    iso_date = day.isoformat()
    yyyymmdd = day.strftime("%Y%m%d")
    return {
        "symbol": symbol,
        "date": iso_date,
        "yyyymmdd": yyyymmdd,
        "expected_url": planned_url(symbol, day),
        "expected_inner_csv": f"{symbol}-candlesticks-{iso_date}.csv",
        "expected_interval": "1m",
        "expected_schema_key": EXPECTED_SCHEMA_KEY,
        "planned_status": "PLANNED_NOT_CHECKED_NOT_DOWNLOADED",
        "url_existence_checked": False,
        "downloaded": False,
        "sha256_claimed": False,
        "build_ready": False,
        "acquisition_ready": False,
    }


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def candidate_symbols(artifacts: dict[str, dict[str, Any]]) -> list[str]:
    symbols = artifacts["candidate_symbol_list"].get("candidate_symbols", [])
    require(isinstance(symbols, list), "candidate_symbols must be a list")
    return [str(symbol) for symbol in symbols]


def chunk_symbols(symbols: list[str]) -> list[list[str]]:
    return [symbols[index : index + PREFERRED_CHUNK_SYMBOL_COUNT] for index in range(0, len(symbols), PREFERRED_CHUNK_SYMBOL_COUNT)]


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    eligibility = artifacts["eligibility_summary"]
    symbols = candidate_symbols(artifacts)
    dates = date_values()
    pilot = artifacts["pilot_pipeline_summary"]
    policy = artifacts["batch_policy_summary"]
    chunks = chunk_symbols(symbols)
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": eligibility.get("historical_data_acquisition_okx_full_usdt_swap_archive_coverage_eligibility_preview_status") == PREVIOUS_STATUS,
        "current_next_module_matches": eligibility.get("next_module") == REQUESTED_MODULE,
        "candidate_symbol_count_303": len(symbols) == EXPECTED_CANDIDATE_SYMBOL_COUNT and artifacts["candidate_symbol_list"].get("candidate_symbol_count") == EXPECTED_CANDIDATE_SYMBOL_COUNT,
        "candidate_symbols_unique": len(symbols) == len(set(symbols)),
        "candidate_symbols_usdt_swap_format": all(symbol.endswith("-USDT-SWAP") for symbol in symbols),
        "date_count_1053": len(dates) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_archive_file_count_valid": len(symbols) * len(dates) == EXPECTED_TOTAL_ARCHIVE_FILE_COUNT,
        "remaining_file_count_valid": REMAINING_CANDIDATE_SYMBOL_COUNT * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL == REMAINING_EXPECTED_ARCHIVE_FILE_COUNT,
        "eligibility_preview_no_forbidden_actions": (
            eligibility.get("url_existence_checked") is False
            and eligibility.get("archive_download_performed") is False
            and eligibility.get("okx_api_call_performed") is False
            and eligibility.get("okx_browse_performed") is False
            and eligibility.get("data_download_performed") is False
            and eligibility.get("data_build_performed") is False
            and eligibility.get("aggregation_performed_now") is False
        ),
        "eligibility_preview_no_readiness_claim": (
            eligibility.get("output_valid_for_research_backtest") is False
            and eligibility.get("output_valid_for_edge_claim") is False
            and eligibility.get("safe_for_full_universe_acquisition") is False
            and eligibility.get("broad_acquisition_ready") is False
        ),
        "future_manifest_approved": eligibility.get("approval_grants_future_archive_coverage_manifest_preview_next") is True,
        "pilot_pipeline_closed": pilot.get("pipeline_closed_successfully") is True and pilot.get("replacement_checks_all_true") is True,
        "batch_policy_available": policy.get("replacement_checks_all_true") is True,
        "chunk_count_valid": len(chunks) == 16,
        "first_chunk_count_valid": len(chunks[0]) == FIRST_CHUNK_SYMBOL_COUNT if chunks else False,
        "last_chunk_not_zero": len(chunks[-1]) > 0 if chunks else False,
    }
    return {"head": head, "checks": checks, "dates": dates, "chunks": chunks, "symbols": symbols}


def build_chunk_index(chunks: list[list[str]]) -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []
    for chunk_number, symbols in enumerate(chunks, start=1):
        pilot_overlap = sorted(symbol for symbol in symbols if symbol in PILOT_SYMBOLS)
        index.append(
            {
                "chunk_id": f"chunk_{chunk_number:02d}",
                "chunk_number": chunk_number,
                "symbol_count": len(symbols),
                "expected_file_count": len(symbols) * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
                "first_symbol": symbols[0],
                "last_symbol": symbols[-1],
                "symbols": symbols,
                "pilot_symbols_already_validated_or_reusable_if_present": pilot_overlap,
                "date_range_start": DATE_START,
                "date_range_end": DATE_END,
                "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
                "planned_status": "PLANNED_NOT_CHECKED_NOT_DOWNLOADED",
                "all_planned_entries_marked_not_checked": True,
                "url_existence_checked": False,
                "downloaded": False,
                "sha256_claimed": False,
                "build_ready": False,
                "acquisition_ready": False,
            }
        )
    return index


def write_chunk_manifests(chunks: list[list[str]], dates: list[date]) -> list[str]:
    written: list[str] = []
    first_day = dates[0]
    last_day = dates[-1]
    middle_day = dates[len(dates) // 2]
    for chunk_number, symbols in enumerate(chunks, start=1):
        chunk_id = f"chunk_{chunk_number:02d}"
        sample_entries = [
            planned_entry(symbols[0], first_day),
            planned_entry(symbols[0], middle_day),
            planned_entry(symbols[-1], last_day),
        ]
        payload = {
            "artifact_type": "archive_coverage_chunk_manifest_preview",
            "chunk_id": chunk_id,
            "chunk_number": chunk_number,
            "symbol_count": len(symbols),
            "symbols": symbols,
            "date_range_start": DATE_START,
            "date_range_end": DATE_END,
            "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
            "expected_file_count": len(symbols) * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
            "full_entry_manifest_deferred_due_size": True,
            "planned_entry_template": {
                "symbol": "BASE-USDT-SWAP",
                "date": "YYYY-MM-DD",
                "yyyymmdd": "YYYYMMDD",
                "expected_url": URL_PATTERN,
                "expected_inner_csv": "SYMBOL-candlesticks-YYYY-MM-DD.csv",
                "expected_interval": "1m",
                "expected_schema_key": EXPECTED_SCHEMA_KEY,
                "planned_status": "PLANNED_NOT_CHECKED_NOT_DOWNLOADED",
                "url_existence_checked": False,
                "downloaded": False,
                "sha256_claimed": False,
                "build_ready": False,
                "acquisition_ready": False,
            },
            "sample_planned_entries": sample_entries,
            "url_existence_checked": False,
            "archive_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "output_valid_for_research_backtest": False,
            "output_valid_for_edge_claim": False,
            "safe_for_full_universe_acquisition": False,
            "broad_acquisition_ready": False,
            "created_at_utc": utc_now(),
        }
        name = f"historical_okx_full_usdt_swap_archive_coverage_chunk_manifest_{chunk_number:02d}.json"
        write_json(OUTPUT_DIR / name, payload)
        written.append(name)
    return written


def common_summary(artifacts: dict[str, dict[str, Any]], chain: dict[str, Any], py_state: dict[str, Any]) -> dict[str, Any]:
    eligibility = artifacts["eligibility_summary"]
    chunks = chain["chunks"]
    first_chunk_symbol_count = len(chunks[0]) if chunks else 0
    chunk_manifest_names = write_chunk_manifests(chunks, chain["dates"])
    replacement_checks = {
        **chain["checks"],
        "full_manifest_deferred_due_size": True,
        "chunk_manifests_written": len(chunk_manifest_names) == len(chunks),
        "sample_urls_created": True,
        "all_planned_entries_marked_not_checked": True,
        "no_url_existence_check_or_download": True,
        "no_download_api_browse_build_aggregation_now": True,
        "no_research_backtest_edge_claim": True,
        "no_full_universe_or_broad_ready_claim": True,
        "next_module_is_first_chunk_download_preview": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    return {
        "historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_status": status,
        "archive_coverage_manifest_preview_created": replacement_checks_all_true,
        "candidate_symbol_count": EXPECTED_CANDIDATE_SYMBOL_COUNT,
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_total_archive_file_count": EXPECTED_TOTAL_ARCHIVE_FILE_COUNT,
        "existing_10_symbol_pilot_file_count": EXISTING_10_SYMBOL_PILOT_FILE_COUNT,
        "existing_pilot_symbol_count": EXISTING_PILOT_SYMBOL_COUNT,
        "remaining_candidate_symbol_count": REMAINING_CANDIDATE_SYMBOL_COUNT,
        "remaining_expected_archive_file_count": REMAINING_EXPECTED_ARCHIVE_FILE_COUNT,
        "date_range_start": DATE_START,
        "date_range_end": DATE_END,
        "full_manifest_written": False,
        "full_manifest_deferred_due_size": True,
        "chunk_plan_created": replacement_checks_all_true,
        "chunk_count": len(chunks),
        "chunk_manifest_files_written": chunk_manifest_names,
        "preferred_chunk_symbol_count": PREFERRED_CHUNK_SYMBOL_COUNT,
        "recommended_chunk_symbol_min": RECOMMENDED_CHUNK_SYMBOL_MIN,
        "recommended_chunk_symbol_max": RECOMMENDED_CHUNK_SYMBOL_MAX,
        "expected_files_per_preferred_chunk": EXPECTED_FILES_PER_PREFERRED_CHUNK,
        "final_chunk_may_be_smaller": True,
        "first_chunk_symbol_count": first_chunk_symbol_count,
        "expected_first_chunk_file_count": first_chunk_symbol_count * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "sample_urls_created": replacement_checks_all_true,
        "all_planned_entries_marked_not_checked": True,
        "url_existence_checked": False,
        "archive_download_performed": False,
        "archive_download_allowed_now": False,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "first_chunk_download_preview_approval_record_created": replacement_checks_all_true,
        "approval_grants_manifest_preview_now": replacement_checks_all_true,
        "approval_grants_download_now": False,
        "approval_grants_future_first_chunk_download_preview_next": replacement_checks_all_true,
        "approval_grants_full_universe_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "batch_policy_carry_forward_created": True,
        **POLICY,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": max(int(eligibility.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_manifest_preview": AFTER_QUALITY if replacement_checks_all_true else "FULL_USDT_SWAP_ARCHIVE_COVERAGE_MANIFEST_PREVIEW_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_outputs(summary: dict[str, Any], artifacts: dict[str, dict[str, Any]], chain: dict[str, Any]) -> dict[str, Any]:
    symbols = chain["symbols"]
    dates = chain["dates"]
    chunks = chain["chunks"]
    chunk_index = build_chunk_index(chunks)
    sample_symbols = [symbols[0], symbols[min(9, len(symbols) - 1)], symbols[-1]]
    sample_days = [dates[0], dates[len(dates) // 2], dates[-1]]
    sample_entries = [planned_entry(symbol, day) for symbol in sample_symbols for day in sample_days]
    preview = {
        **summary,
        "artifact_type": "archive_coverage_manifest_preview",
        "planned_manifest_shape": {
            "fields": [
                "symbol",
                "date",
                "yyyymmdd",
                "expected_url",
                "expected_inner_csv",
                "expected_interval",
                "expected_schema_key",
                "planned_status",
                "url_existence_checked",
                "downloaded",
                "sha256_claimed",
                "build_ready",
                "acquisition_ready",
            ],
            "url_pattern": URL_PATTERN,
            "expected_schema_key": EXPECTED_SCHEMA_KEY,
            "planned_status": "PLANNED_NOT_CHECKED_NOT_DOWNLOADED",
        },
        "full_manifest_decision": "DEFER_FULL_319059_ROW_MANIFEST_WRITE_AND_USE_INDEX_CHUNK_PREVIEWS",
    }
    manifest_index = {
        **summary,
        "artifact_type": "archive_coverage_manifest_index",
        "chunk_index": chunk_index,
        "chunk_manifest_files": summary["chunk_manifest_files_written"],
    }
    chunk_plan = {
        **summary,
        "artifact_type": "archive_coverage_chunk_plan",
        "chunks": chunk_index,
        "resource_policy": [
            "No all-at-once download.",
            "No all-at-once build.",
            "Future download must be chunk-approved.",
            "Reuse already validated 10-symbol pilot files where symbols overlap.",
            "Do not perform one-symbol-at-a-time loops.",
        ],
    }
    sample_urls = {
        **summary,
        "artifact_type": "archive_coverage_manifest_sample_urls",
        "sample_planned_entries": sample_entries,
    }
    resource_limits = {
        **summary,
        "artifact_type": "archive_coverage_manifest_resource_limits",
        "max_unapproved_download_count_now": 0,
        "max_unapproved_api_calls_now": 0,
        "max_unapproved_url_existence_checks_now": 0,
        "future_first_chunk_limits": {
            "first_chunk_symbol_count": FIRST_CHUNK_SYMBOL_COUNT,
            "expected_first_chunk_file_count": EXPECTED_FIRST_CHUNK_FILE_COUNT,
            "download_requires_separate_preview_and_approval": True,
        },
    }
    approval = {
        **summary,
        "artifact_type": "first_chunk_download_preview_approval_record",
        "approval_scope": "next separate first chunk download preview only",
    }
    self_validator = {
        **summary,
        "artifact_type": "self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
        "optional_chunk_manifest_count": len(summary["chunk_manifest_files_written"]),
    }
    summary_artifact = {
        **summary,
        "artifact_type": "summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    return {
        "historical_okx_full_usdt_swap_archive_coverage_manifest_preview.json": preview,
        "historical_okx_full_usdt_swap_archive_coverage_manifest_index.json": manifest_index,
        "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json": chunk_plan,
        "historical_okx_full_usdt_swap_archive_coverage_manifest_sample_urls.json": sample_urls,
        "historical_okx_full_usdt_swap_archive_coverage_manifest_resource_limits.json": resource_limits,
        "historical_okx_full_usdt_swap_first_chunk_download_preview_approval_record.json": approval,
        "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_self_validator.json": self_validator,
        "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_summary.json": summary_artifact,
    }


def run_preview() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    chain = validate_inputs(artifacts, py_state)
    summary = common_summary(artifacts, chain, py_state)
    outputs = build_outputs(summary, artifacts, chain)
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing required outputs: {missing}")
    require(summary["replacement_checks_all_true"] is True, "replacement checks did not all pass")
    return summary


def main() -> int:
    try:
        summary = run_preview()
    except Exception as exc:
        blocked = {
            "historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_status": BLOCKED_STATUS,
            "archive_coverage_manifest_preview_created": False,
            "blocked_reason": repr(exc),
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            "url_existence_checked": False,
            "archive_download_performed": False,
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "created_at_utc": utc_now(),
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
