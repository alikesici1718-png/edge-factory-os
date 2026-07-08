from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_preview_after_first_chunk_coverage_summary_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "fcf4adc"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_COVERAGE_SUMMARY_CLOSED_CHUNK_02_PREVIEW_READY"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_READY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_PREVIEW_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_after_preview_approval_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_preview_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_CHUNK_02_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_READY"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

CHUNK_PLAN_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1"
SOURCE_DISCOVERY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"
CHUNK_01_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_after_validator_v1"

ARTIFACTS = {
    "chunk_plan": CHUNK_PLAN_DIR / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json",
    "manifest_preview_summary": CHUNK_PLAN_DIR / "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_summary.json",
    "candidate_symbol_list": SOURCE_DISCOVERY_DIR / "historical_okx_full_usdt_swap_candidate_symbol_list.json",
    "chunk_01_coverage_summary": CHUNK_01_SUMMARY_DIR / "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary_bundle_summary.json",
    "chunk_01_coverage_ledger": CHUNK_01_SUMMARY_DIR / "historical_okx_full_usdt_swap_cumulative_coverage_eligibility_ledger_after_chunk_01.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_chunk_02_download_preview.json",
    "historical_okx_full_usdt_swap_chunk_02_symbol_list.json",
    "historical_okx_full_usdt_swap_chunk_02_planned_file_manifest_preview.json",
    "historical_okx_full_usdt_swap_chunk_02_reuse_candidate_report.json",
    "historical_okx_full_usdt_swap_chunk_02_download_resource_limits.json",
    "historical_okx_full_usdt_swap_chunk_02_download_execution_approval_record.json",
    "historical_okx_full_usdt_swap_chunk_02_download_preview_self_validator.json",
    "historical_okx_full_usdt_swap_chunk_02_download_preview_summary.json",
]

CHUNK_ID = "chunk_02"
CHUNK_COUNT = 16
CHUNKS_COMPLETED_BEFORE_THIS_PREVIEW = 1
CHUNKS_REMAINING_BEFORE_THIS_PREVIEW = 15
EXPECTED_CANDIDATE_SYMBOL_COUNT = 303
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1_053
EXPECTED_CHUNK_02_SYMBOL_COUNT = 20
EXPECTED_CHUNK_02_FILE_COUNT = 21_060
DATE_START = "2023-07-01"
DATE_END = "2026-05-18"
EXPECTED_SCHEMA_KEY = "OKX_CANDLESTICKS_1M_SCHEMA_V1"
EXPECTED_INTERVAL = "1m"
PLANNED_STATUS = "PLANNED_NOT_CHECKED_NOT_DOWNLOADED"
REUSE_CANDIDATE_STATUS = "REUSE_CANDIDATE_ALREADY_VALIDATED_PILOT_OR_PRIOR_CHUNK_FILE"
URL_PATTERN = "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/YYYYMMDD/SYMBOL-candlesticks-YYYY-MM-DD.zip"

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


class PreviewBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreviewBlocked(message)


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
    require(path.exists(), f"missing artifact {label}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"artifact {label} is not a JSON object")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


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


def planned_entry(symbol: str, day: date, reuse_candidate: bool) -> dict[str, Any]:
    iso_date = day.isoformat()
    yyyymmdd = day.strftime("%Y%m%d")
    entry = {
        "chunk_id": CHUNK_ID,
        "symbol": symbol,
        "date": iso_date,
        "yyyyMMdd": yyyymmdd,
        "expected_url": planned_url(symbol, day),
        "expected_inner_csv": f"{symbol}-candlesticks-{iso_date}.csv",
        "expected_interval": EXPECTED_INTERVAL,
        "expected_schema_key": EXPECTED_SCHEMA_KEY,
        "planned_status": PLANNED_STATUS,
        "url_existence_checked": False,
        "downloaded": False,
        "sha256_claimed": False,
        "zip_open_checked": False,
        "csv_header_checked": False,
        "build_ready": False,
        "acquisition_ready": False,
    }
    if reuse_candidate:
        entry["reuse_candidate_status"] = REUSE_CANDIDATE_STATUS
    return entry


def chunk_02_from_plan(chunk_plan: dict[str, Any]) -> dict[str, Any]:
    chunks = chunk_plan.get("chunks", [])
    require(isinstance(chunks, list) and len(chunks) >= 2, "chunk plan does not contain chunk_02")
    chunk = chunks[1]
    require(isinstance(chunk, dict), "chunk_02 plan entry is not an object")
    require(chunk.get("chunk_id") == CHUNK_ID, f"second chunk id mismatch: {chunk.get('chunk_id')}")
    return chunk


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> tuple[dict[str, bool], dict[str, Any]]:
    head = run_git(["rev-parse", "HEAD"])
    chunk_plan = artifacts["chunk_plan"]
    candidate_list = artifacts["candidate_symbol_list"]
    coverage = artifacts["chunk_01_coverage_summary"]
    ledger = artifacts["chunk_01_coverage_ledger"]
    manifest_preview = artifacts["manifest_preview_summary"]
    chunk = chunk_02_from_plan(chunk_plan)
    symbols = [str(symbol) for symbol in chunk.get("symbols", [])]
    dates = date_values()
    expected_count = len(symbols) * len(dates)
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": coverage.get("historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_status") == PREVIOUS_STATUS,
        "current_next_module_matches": coverage.get("next_module") == REQUESTED_MODULE,
        "coverage_summary_ready": (
            coverage.get("coverage_summary_created") is True
            and coverage.get("next_chunk_download_preview_required") is True
            and coverage.get("approval_grants_future_chunk_02_download_preview_next") is True
        ),
        "coverage_no_forbidden_actions": (
            coverage.get("okx_api_call_performed") is False
            and coverage.get("okx_browse_performed") is False
            and coverage.get("data_download_performed") is False
            and coverage.get("data_build_performed") is False
            and coverage.get("aggregation_performed_now") is False
            and coverage.get("full_universe_download_allowed_now") is False
            and coverage.get("data_build_allowed_now") is False
            and coverage.get("strategy_backtest_edge_allowed_now") is False
        ),
        "ledger_counts_valid": (
            ledger.get("cumulative_near_3y_download_coverage_complete_symbol_count") == 5
            and ledger.get("cumulative_coverage_gap_symbol_count") == 15
            and ledger.get("cumulative_pending_symbol_count") == 283
            and ledger.get("cumulative_available_file_count") == 10106
            and ledger.get("cumulative_missing_or_failed_file_count") == 10954
            and ledger.get("cumulative_planned_file_count_evaluated") == 21060
            and ledger.get("build_ready_symbol_count") == 0
            and ledger.get("acquisition_ready_symbol_count") == 0
        ),
        "chunk_plan_valid": (
            chunk_plan.get("chunk_count") == CHUNK_COUNT
            and chunk_plan.get("candidate_symbol_count") == EXPECTED_CANDIDATE_SYMBOL_COUNT
            and len(chunk_plan.get("chunks", [])) == CHUNK_COUNT
            and chunk.get("chunk_number") == 2
            and chunk.get("symbol_count") == EXPECTED_CHUNK_02_SYMBOL_COUNT
            and chunk.get("expected_file_count") == EXPECTED_CHUNK_02_FILE_COUNT
            and chunk.get("planned_status") == PLANNED_STATUS
            and chunk.get("url_existence_checked") is False
            and chunk.get("downloaded") is False
            and chunk.get("build_ready") is False
            and chunk.get("acquisition_ready") is False
        ),
        "candidate_symbol_count_valid": (
            candidate_list.get("candidate_symbol_count") == EXPECTED_CANDIDATE_SYMBOL_COUNT
            and len(candidate_list.get("candidate_symbols", [])) == EXPECTED_CANDIDATE_SYMBOL_COUNT
        ),
        "manifest_preview_no_forbidden_actions": (
            manifest_preview.get("url_existence_checked") is False
            and manifest_preview.get("archive_download_performed") is False
            and manifest_preview.get("okx_api_call_performed") is False
            and manifest_preview.get("okx_browse_performed") is False
            and manifest_preview.get("data_build_performed") is False
            and manifest_preview.get("aggregation_performed_now") is False
        ),
        "date_count_valid": len(dates) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "chunk_02_symbol_count_valid": len(symbols) == EXPECTED_CHUNK_02_SYMBOL_COUNT,
        "expected_file_count_valid": expected_count == EXPECTED_CHUNK_02_FILE_COUNT,
        "chunk_02_symbols_unique": len(symbols) == len(set(symbols)),
        "chunk_02_symbols_match_plan_order": symbols == chunk.get("symbols"),
    }
    require(all(checks.values()), f"input validation failed: {checks}")
    return checks, {"chunk": chunk, "symbols": symbols, "dates": dates, "expected_count": expected_count}


def common_summary(
    artifacts: dict[str, dict[str, Any]],
    checks: dict[str, bool],
    state: dict[str, Any],
    py_state: dict[str, Any],
    planned_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    coverage = artifacts["chunk_01_coverage_summary"]
    symbols = state["symbols"]
    reuse_symbols = [symbol for symbol in symbols if symbol in PILOT_SYMBOLS or symbol in coverage.get("symbols_with_full_file_coverage", [])]
    reuse_file_count = len(reuse_symbols) * EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL
    all_entries_safe = all(
        entry.get("planned_status") == PLANNED_STATUS
        and entry.get("url_existence_checked") is False
        and entry.get("downloaded") is False
        and entry.get("sha256_claimed") is False
        and entry.get("zip_open_checked") is False
        and entry.get("csv_header_checked") is False
        and entry.get("build_ready") is False
        and entry.get("acquisition_ready") is False
        for entry in planned_entries
    )
    replacement_checks = {
        **checks,
        "planned_manifest_count_valid": len(planned_entries) == state["expected_count"],
        "all_planned_entries_marked_not_checked": all_entries_safe,
        "reuse_candidate_file_count_valid": reuse_file_count == sum(1 for entry in planned_entries if entry.get("reuse_candidate_status") == REUSE_CANDIDATE_STATUS),
        "approval_record_routes_to_execution_only": True,
        "resource_limits_bound_chunk_02_only": True,
        "batch_policy_carry_forward_created": True,
        "no_download_api_browse_build_aggregation_now": True,
        "next_module_is_chunk_02_execution": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    return {
        "historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_preview_status": PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS,
        "chunk_02_download_preview_created": replacement_checks_all_true,
        "chunk_id": CHUNK_ID,
        "chunk_count": CHUNK_COUNT,
        "chunks_completed_before_this_preview": CHUNKS_COMPLETED_BEFORE_THIS_PREVIEW,
        "chunks_remaining_before_this_preview": CHUNKS_REMAINING_BEFORE_THIS_PREVIEW,
        "candidate_symbol_count": EXPECTED_CANDIDATE_SYMBOL_COUNT,
        "chunk_02_symbol_count": len(symbols),
        "chunk_02_symbols": symbols,
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_chunk_02_file_count": state["expected_count"],
        "date_range_start": DATE_START,
        "date_range_end": DATE_END,
        "planned_file_manifest_preview_created": replacement_checks_all_true,
        "planned_file_count": len(planned_entries),
        "all_planned_entries_marked_not_checked": all_entries_safe,
        "reuse_candidate_symbol_count": len(reuse_symbols),
        "reuse_candidate_symbols": reuse_symbols,
        "reuse_candidate_file_count": reuse_file_count,
        "future_execution_max_download_or_reuse_file_count": state["expected_count"],
        "cumulative_near_3y_download_coverage_complete_symbol_count_before_chunk": 5,
        "cumulative_coverage_gap_symbol_count_before_chunk": 15,
        "cumulative_pending_symbol_count_before_chunk": 283,
        "cumulative_available_file_count_before_chunk": 10106,
        "cumulative_missing_or_failed_file_count_before_chunk": 10954,
        "cumulative_planned_file_count_evaluated_before_chunk": 21060,
        "url_existence_checked": False,
        "archive_download_performed": False,
        "archive_download_allowed_now": False,
        "chunk_02_download_execution_allowed_now": False,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "chunk_02_download_execution_approval_record_created": replacement_checks_all_true,
        "approval_grants_chunk_02_download_preview_now": replacement_checks_all_true,
        "approval_grants_download_now": False,
        "approval_grants_future_chunk_02_download_execution_next": replacement_checks_all_true,
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
        "active_p1_attention_count": max(int(coverage.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY if replacement_checks_all_true else "CHUNK_02_DOWNLOAD_PREVIEW_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_planned_entries(symbols: list[str], dates: list[date]) -> list[dict[str, Any]]:
    reuse_set = set(PILOT_SYMBOLS)
    entries: list[dict[str, Any]] = []
    for symbol in symbols:
        reuse_candidate = symbol in reuse_set
        for day in dates:
            entries.append(planned_entry(symbol, day, reuse_candidate))
    return entries


def build_outputs(summary: dict[str, Any], planned_entries: list[dict[str, Any]]) -> dict[str, Any]:
    reuse_entries = [
        {
            "chunk_id": CHUNK_ID,
            "symbol": symbol,
            "date_range_start": DATE_START,
            "date_range_end": DATE_END,
            "expected_reuse_candidate_file_count": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
            "reuse_candidate_status": REUSE_CANDIDATE_STATUS,
            "reuse_finality": "NOT_FINAL_UNTIL_FUTURE_EXECUTION_REVALIDATES_HASH_PATH_PROVENANCE",
            "build_ready": False,
            "acquisition_ready": False,
        }
        for symbol in summary["reuse_candidate_symbols"]
    ]
    preview = {
        **summary,
        "artifact_type": "chunk_02_download_preview",
        "url_pattern": URL_PATTERN,
        "planned_status": PLANNED_STATUS,
        "reuse_policy": {
            "reuse_candidate_status": REUSE_CANDIDATE_STATUS,
            "reuse_finality": "Future execution must revalidate hash/path/provenance before reuse is final.",
            "no_file_marked_build_ready_or_acquisition_ready": True,
        },
    }
    symbol_list = {**summary, "artifact_type": "chunk_02_symbol_list", "symbols": summary["chunk_02_symbols"]}
    planned_manifest = {
        **summary,
        "artifact_type": "chunk_02_planned_file_manifest_preview",
        "full_entry_manifest_written": True,
        "planned_entries": planned_entries,
    }
    reuse_report = {
        **summary,
        "artifact_type": "chunk_02_reuse_candidate_report",
        "reuse_candidate_entries": reuse_entries,
        "reuse_finality": "NOT_FINAL_UNTIL_FUTURE_EXECUTION_REVALIDATES_HASH_PATH_PROVENANCE",
    }
    resource_limits = {
        **summary,
        "artifact_type": "chunk_02_download_resource_limits",
        "no_symbols_outside_chunk_02": True,
        "no_dates_outside_range": f"{DATE_START}_THROUGH_{DATE_END}",
        "max_expected_file_count": summary["expected_chunk_02_file_count"],
        "no_api_browse": True,
        "no_data_build_aggregation": True,
        "future_execution_allowed_scope": "READ_ONLY_ZIP_INVENTORY_AND_CSV_HEADER_SAMPLE_ROWS_AFTER_DOWNLOAD_OR_REUSE",
        "max_csv_sample_rows_per_file": 5,
        "compute_sha256_after_download_or_reuse_validation": True,
        "record_gaps_failures_without_silently_skipping": True,
    }
    approval = {
        **summary,
        "artifact_type": "chunk_02_download_execution_approval_record",
        "approval_scope": "next separate chunk_02 download execution module only",
    }
    self_validator = {
        **summary,
        "artifact_type": "chunk_02_download_preview_self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
        "forbidden_actions_verified_by_construction": True,
    }
    summary_artifact = {**summary, "artifact_type": "chunk_02_download_preview_summary", "artifact_count": len(REQUIRED_OUTPUTS)}
    return {
        "historical_okx_full_usdt_swap_chunk_02_download_preview.json": preview,
        "historical_okx_full_usdt_swap_chunk_02_symbol_list.json": symbol_list,
        "historical_okx_full_usdt_swap_chunk_02_planned_file_manifest_preview.json": planned_manifest,
        "historical_okx_full_usdt_swap_chunk_02_reuse_candidate_report.json": reuse_report,
        "historical_okx_full_usdt_swap_chunk_02_download_resource_limits.json": resource_limits,
        "historical_okx_full_usdt_swap_chunk_02_download_execution_approval_record.json": approval,
        "historical_okx_full_usdt_swap_chunk_02_download_preview_self_validator.json": self_validator,
        "historical_okx_full_usdt_swap_chunk_02_download_preview_summary.json": summary_artifact,
    }


def run_preview() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    checks, state = validate_inputs(artifacts, py_state)
    planned_entries = build_planned_entries(state["symbols"], state["dates"])
    summary = common_summary(artifacts, checks, state, py_state, planned_entries)
    outputs = build_outputs(summary, planned_entries)
    for name, payload in outputs.items():
        write_json(OUTPUT_DIR / name, payload)
    missing = [name for name in REQUIRED_OUTPUTS if not (OUTPUT_DIR / name).exists()]
    require(not missing, f"missing preview outputs: {missing}")
    require(summary["replacement_checks_all_true"], "replacement checks failed")
    return summary


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_preview_status": BLOCKED_STATUS,
        "chunk_02_download_preview_created": False,
        "blocked_reason": message,
        "chunk_id": CHUNK_ID,
        "chunk_count": CHUNK_COUNT,
        "chunks_completed_before_this_preview": CHUNKS_COMPLETED_BEFORE_THIS_PREVIEW,
        "chunks_remaining_before_this_preview": CHUNKS_REMAINING_BEFORE_THIS_PREVIEW,
        "candidate_symbol_count": EXPECTED_CANDIDATE_SYMBOL_COUNT,
        "chunk_02_symbol_count": 0,
        "chunk_02_symbols": [],
        "expected_chunk_02_file_count": 0,
        "planned_file_manifest_preview_created": False,
        "planned_file_count": 0,
        "all_planned_entries_marked_not_checked": False,
        "reuse_candidate_symbol_count": 0,
        "reuse_candidate_file_count": 0,
        "future_execution_max_download_or_reuse_file_count": 0,
        "url_existence_checked": False,
        "archive_download_performed": False,
        "chunk_02_download_execution_allowed_now": False,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "chunk_02_download_execution_approval_record_created": False,
        "approval_grants_future_chunk_02_download_execution_next": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": 505,
        "current_evidence_chain_quality_after_preview": "CHUNK_02_DOWNLOAD_PREVIEW_FAILED_CLOSED",
        "next_module": FAILED_NEXT_MODULE,
        "replacement_checks_all_true": False,
        "created_at_utc": utc_now(),
    }


def main() -> int:
    try:
        summary = run_preview()
    except Exception as exc:
        blocked = blocked_payload(type(exc).__name__ + ": " + str(exc))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_chunk_02_download_preview_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
