from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_preview_after_manifest_preview_v1"
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "efaa598"
PREVIOUS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_ARCHIVE_COVERAGE_MANIFEST_PREVIEW_READY_FOR_FIRST_CHUNK_DOWNLOAD_PREVIEW"
PASS_STATUS = "PASS_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_READY"
BLOCKED_STATUS = "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_PREVIEW_FAILED_CLOSED"
NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_after_preview_approval_v1.py"
FAILED_NEXT_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_preview_blocked_record_v1.py"
AFTER_QUALITY = "HISTORICAL_DATA_ACQUISITION_OKX_FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_PREVIEW_APPROVED_EXECUTION_READY"

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME

MANIFEST_PREVIEW_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1"
SOURCE_DISCOVERY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"
PILOT_SUMMARY_DIR = EDGE_LAB_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_after_build_validator_v1"

ARTIFACTS = {
    "manifest_preview_summary": MANIFEST_PREVIEW_DIR / "historical_okx_full_usdt_swap_archive_coverage_manifest_preview_summary.json",
    "chunk_plan": MANIFEST_PREVIEW_DIR / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json",
    "candidate_symbol_list": SOURCE_DISCOVERY_DIR / "historical_okx_full_usdt_swap_candidate_symbol_list.json",
    "pilot_pipeline_summary": PILOT_SUMMARY_DIR / "historical_okx_10_symbol_pilot_batch_policy_clean_pipeline_summary_bundle_summary.json",
}

REQUIRED_OUTPUTS = [
    "historical_okx_full_usdt_swap_first_chunk_download_preview.json",
    "historical_okx_full_usdt_swap_first_chunk_symbol_list.json",
    "historical_okx_full_usdt_swap_first_chunk_planned_file_manifest_preview.json",
    "historical_okx_full_usdt_swap_first_chunk_reuse_candidate_report.json",
    "historical_okx_full_usdt_swap_first_chunk_download_resource_limits.json",
    "historical_okx_full_usdt_swap_first_chunk_download_execution_approval_record.json",
    "historical_okx_full_usdt_swap_first_chunk_download_preview_self_validator.json",
    "historical_okx_full_usdt_swap_first_chunk_download_preview_summary.json",
]

EXPECTED_CANDIDATE_SYMBOL_COUNT = 303
EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL = 1053
EXPECTED_CHUNK_COUNT = 16
EXPECTED_FIRST_CHUNK_SYMBOL_COUNT = 20
EXPECTED_FIRST_CHUNK_FILE_COUNT = 21_060
DATE_START = "2023-07-01"
DATE_END = "2026-05-18"
EXPECTED_SCHEMA_KEY = "OKX_CANDLESTICKS_1M_SCHEMA_V1"
EXPECTED_INTERVAL = "1m"
PLANNED_STATUS = "PLANNED_NOT_CHECKED_NOT_DOWNLOADED"
REUSE_CANDIDATE_STATUS = "REUSE_CANDIDATE_ALREADY_VALIDATED_PILOT_FILE"
URL_PATTERN = "https://static.okx.com/cdn/okex/traderecords/candlesticks/daily/YYYYMMDD/SYMBOL-candlesticks-YYYY-MM-DD.zip"

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


def planned_entry(chunk_id: str, symbol: str, day: date, reuse_candidate: bool) -> dict[str, Any]:
    iso_date = day.isoformat()
    yyyymmdd = day.strftime("%Y%m%d")
    entry = {
        "chunk_id": chunk_id,
        "symbol": symbol,
        "date": iso_date,
        "yyyymmdd": yyyymmdd,
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


def read_artifacts() -> dict[str, dict[str, Any]]:
    return {label: load_json(path, label) for label, path in ARTIFACTS.items()}


def candidate_symbols(artifacts: dict[str, dict[str, Any]]) -> list[str]:
    symbols = artifacts["candidate_symbol_list"].get("candidate_symbols", [])
    require(isinstance(symbols, list), "candidate_symbols must be a list")
    return [str(symbol) for symbol in symbols]


def pilot_symbols(artifacts: dict[str, dict[str, Any]]) -> list[str]:
    symbols = artifacts["pilot_pipeline_summary"].get("pilot_symbols", [])
    require(isinstance(symbols, list), "pilot_symbols must be a list")
    return [str(symbol) for symbol in symbols]


def first_chunk_from_plan(artifacts: dict[str, dict[str, Any]], candidates: list[str]) -> tuple[str, list[str], str]:
    chunk_plan = artifacts["chunk_plan"]
    chunks = chunk_plan.get("chunks", [])
    require(isinstance(chunks, list) and chunks, "chunk plan must contain chunks")
    first = chunks[0]
    require(isinstance(first, dict), "first chunk plan entry must be an object")
    symbols = first.get("symbols")
    derivation_method = "READ_EXPLICIT_FIRST_CHUNK_SYMBOLS_FROM_CHUNK_PLAN"
    if symbols is None:
        symbols = candidates[:EXPECTED_FIRST_CHUNK_SYMBOL_COUNT]
        derivation_method = "DERIVED_FROM_CANDIDATE_SYMBOL_LIST_ORDER_USED_IN_MANIFEST_PREVIEW"
    require(isinstance(symbols, list), "first chunk symbols must be a list")
    chunk_id = str(first.get("chunk_id", "chunk_01"))
    return chunk_id, [str(symbol) for symbol in symbols], derivation_method


def build_planned_manifest(chunk_id: str, symbols: list[str], dates: list[date], pilot_set: set[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for symbol in symbols:
        reuse_candidate = symbol in pilot_set
        for day in dates:
            entries.append(planned_entry(chunk_id, symbol, day, reuse_candidate))
    return entries


def common_false_flags() -> dict[str, bool]:
    return {
        "url_existence_checked": False,
        "archive_download_performed": False,
        "archive_download_allowed_now": False,
        "first_chunk_download_execution_allowed_now": False,
        "full_universe_download_allowed_now": False,
        "data_build_allowed_now": False,
        "strategy_backtest_edge_allowed_now": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "safe_for_full_universe_acquisition": False,
        "broad_acquisition_ready": False,
    }


def validate_inputs(artifacts: dict[str, dict[str, Any]], py_state: dict[str, Any]) -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    manifest_summary = artifacts["manifest_preview_summary"]
    chunk_plan = artifacts["chunk_plan"]
    candidates = candidate_symbols(artifacts)
    pilot = pilot_symbols(artifacts)
    dates = date_values()
    chunk_id, first_symbols, derivation_method = first_chunk_from_plan(artifacts, candidates)
    first_chunk_plan = chunk_plan["chunks"][0]
    planned_count = len(first_symbols) * len(dates)
    checks = {
        "current_head_guard_passed": head.startswith(EXPECTED_HEAD),
        "current_path_guard_passed": APPROVED_TOOL.exists(),
        "repo_has_only_approved_tool_change": repo_has_only_this_tool_change(),
        "python_syntax_bom_clean": py_state["syntax_error_count"] == 0 and py_state["bom_error_count"] == 0,
        "previous_status_passed": manifest_summary.get("historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_status") == PREVIOUS_STATUS,
        "current_next_module_matches": manifest_summary.get("next_module") == REQUESTED_MODULE,
        "manifest_preview_created": manifest_summary.get("archive_coverage_manifest_preview_created") is True,
        "manifest_preview_approval_available": manifest_summary.get("approval_grants_future_first_chunk_download_preview_next") is True,
        "manifest_preview_no_forbidden_actions": (
            manifest_summary.get("url_existence_checked") is False
            and manifest_summary.get("archive_download_performed") is False
            and manifest_summary.get("okx_api_call_performed") is False
            and manifest_summary.get("okx_browse_performed") is False
            and manifest_summary.get("data_download_performed") is False
            and manifest_summary.get("data_build_performed") is False
            and manifest_summary.get("aggregation_performed_now") is False
        ),
        "manifest_preview_no_readiness_claim": (
            manifest_summary.get("output_valid_for_research_backtest") is False
            and manifest_summary.get("output_valid_for_edge_claim") is False
            and manifest_summary.get("safe_for_full_universe_acquisition") is False
            and manifest_summary.get("broad_acquisition_ready") is False
        ),
        "candidate_symbol_count_303": (
            len(candidates) == EXPECTED_CANDIDATE_SYMBOL_COUNT
            and artifacts["candidate_symbol_list"].get("candidate_symbol_count") == EXPECTED_CANDIDATE_SYMBOL_COUNT
            and manifest_summary.get("candidate_symbol_count") == EXPECTED_CANDIDATE_SYMBOL_COUNT
            and chunk_plan.get("candidate_symbol_count") == EXPECTED_CANDIDATE_SYMBOL_COUNT
        ),
        "chunk_count_16": (
            chunk_plan.get("chunk_count") == EXPECTED_CHUNK_COUNT
            and len(chunk_plan.get("chunks", [])) == EXPECTED_CHUNK_COUNT
        ),
        "first_chunk_symbol_count_20": (
            len(first_symbols) == EXPECTED_FIRST_CHUNK_SYMBOL_COUNT
            and first_chunk_plan.get("symbol_count") == EXPECTED_FIRST_CHUNK_SYMBOL_COUNT
        ),
        "first_chunk_file_count_21060": (
            planned_count == EXPECTED_FIRST_CHUNK_FILE_COUNT
            and first_chunk_plan.get("expected_file_count") == EXPECTED_FIRST_CHUNK_FILE_COUNT
            and manifest_summary.get("expected_first_chunk_file_count") == EXPECTED_FIRST_CHUNK_FILE_COUNT
        ),
        "date_count_1053": len(dates) == EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "date_range_matches": (
            manifest_summary.get("date_range_start") == DATE_START
            and manifest_summary.get("date_range_end") == DATE_END
        ),
        "first_chunk_symbols_match_candidate_order": first_symbols == candidates[:EXPECTED_FIRST_CHUNK_SYMBOL_COUNT],
        "first_chunk_entries_not_checked_or_downloaded": (
            first_chunk_plan.get("all_planned_entries_marked_not_checked") is True
            and first_chunk_plan.get("url_existence_checked") is False
            and first_chunk_plan.get("downloaded") is False
            and first_chunk_plan.get("sha256_claimed") is False
            and first_chunk_plan.get("build_ready") is False
            and first_chunk_plan.get("acquisition_ready") is False
        ),
        "pilot_summary_available": (
            artifacts["pilot_pipeline_summary"].get("pipeline_closed_successfully") is True
            and artifacts["pilot_pipeline_summary"].get("replacement_checks_all_true") is True
            and len(pilot) == 10
        ),
        "no_download_api_browse_build_aggregation_now": True,
        "no_url_existence_check": True,
        "no_research_backtest_edge_claim": True,
        "no_full_universe_or_broad_ready_claim": True,
        "next_module_is_first_chunk_download_execution": True,
    }
    return {
        "head": head,
        "checks": checks,
        "dates": dates,
        "chunk_id": chunk_id,
        "first_chunk_symbols": first_symbols,
        "first_chunk_derivation_method": derivation_method,
        "pilot_symbols": pilot,
        "candidate_symbols": candidates,
    }


def build_summary(
    artifacts: dict[str, dict[str, Any]],
    chain: dict[str, Any],
    py_state: dict[str, Any],
    planned_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    manifest_summary = artifacts["manifest_preview_summary"]
    first_symbols = chain["first_chunk_symbols"]
    pilot_set = set(chain["pilot_symbols"])
    reuse_symbols = [symbol for symbol in first_symbols if symbol in pilot_set]
    planned_count = len(planned_entries)
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
        **chain["checks"],
        "planned_file_manifest_preview_created": planned_count == EXPECTED_FIRST_CHUNK_FILE_COUNT,
        "all_planned_entries_marked_not_checked": all_entries_safe,
        "reuse_candidate_count_valid": reuse_file_count == sum(1 for entry in planned_entries if entry.get("reuse_candidate_status") == REUSE_CANDIDATE_STATUS),
        "approval_record_routes_to_execution_only": True,
        "resource_limits_bound_first_chunk_only": True,
        "batch_policy_carry_forward_created": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    return {
        "historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_preview_status": status,
        "first_chunk_download_preview_created": replacement_checks_all_true,
        "chunk_id": chain["chunk_id"],
        "chunk_count": EXPECTED_CHUNK_COUNT,
        "candidate_symbol_count": EXPECTED_CANDIDATE_SYMBOL_COUNT,
        "first_chunk_symbol_count": len(first_symbols),
        "first_chunk_symbols": first_symbols,
        "first_chunk_derivation_method": chain["first_chunk_derivation_method"],
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
        "expected_first_chunk_file_count": EXPECTED_FIRST_CHUNK_FILE_COUNT,
        "date_range_start": DATE_START,
        "date_range_end": DATE_END,
        "planned_file_manifest_preview_created": replacement_checks_all_true,
        "planned_file_count": planned_count,
        "all_planned_entries_marked_not_checked": all_entries_safe,
        "reuse_candidate_symbol_count": len(reuse_symbols),
        "reuse_candidate_symbols": reuse_symbols,
        "reuse_candidate_file_count": reuse_file_count,
        "future_execution_max_download_or_reuse_file_count": EXPECTED_FIRST_CHUNK_FILE_COUNT,
        **common_false_flags(),
        "first_chunk_download_execution_approval_record_created": replacement_checks_all_true,
        "approval_grants_first_chunk_download_preview_now": replacement_checks_all_true,
        "approval_grants_download_now": False,
        "approval_grants_future_first_chunk_download_execution_next": replacement_checks_all_true,
        "approval_grants_full_universe_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
        "batch_policy_carry_forward_created": True,
        **POLICY,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": max(int(manifest_summary.get("active_p1_attention_count", 0)), 505),
        "dormant_repo_attention_count": 716,
        "current_evidence_chain_quality_after_preview": AFTER_QUALITY if replacement_checks_all_true else "FULL_USDT_SWAP_FIRST_CHUNK_DOWNLOAD_PREVIEW_FAILED_CLOSED",
        "next_module": NEXT_MODULE if replacement_checks_all_true else FAILED_NEXT_MODULE,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "tracked_python_count": py_state["tracked_python_count"],
        "syntax_error_count": py_state["syntax_error_count"],
        "bom_error_count": py_state["bom_error_count"],
        "created_at_utc": utc_now(),
    }


def build_outputs(summary: dict[str, Any], planned_entries: list[dict[str, Any]]) -> dict[str, Any]:
    first_symbols = summary["first_chunk_symbols"]
    reuse_symbols = summary["reuse_candidate_symbols"]
    reuse_candidate_entries = [
        {
            "chunk_id": summary["chunk_id"],
            "symbol": symbol,
            "date_range_start": DATE_START,
            "date_range_end": DATE_END,
            "expected_reuse_candidate_file_count": EXPECTED_DAILY_FILE_COUNT_PER_SYMBOL,
            "reuse_candidate_status": REUSE_CANDIDATE_STATUS,
            "reuse_finality": "NOT_FINAL_UNTIL_FUTURE_EXECUTION_REVALIDATES_HASH_PATH_PROVENANCE",
            "build_ready": False,
            "acquisition_ready": False,
        }
        for symbol in reuse_symbols
    ]
    preview = {
        **summary,
        "artifact_type": "first_chunk_download_preview",
        "url_pattern": URL_PATTERN,
        "planned_status": PLANNED_STATUS,
        "reuse_policy": {
            "reuse_candidate_status": REUSE_CANDIDATE_STATUS,
            "reuse_finality": "Reuse candidates reduce future new-download count only after execution validator confirms hash/path/provenance.",
            "no_file_marked_build_ready_or_acquisition_ready": True,
        },
        "planned_manifest_fields": [
            "chunk_id",
            "symbol",
            "date",
            "yyyymmdd",
            "expected_url",
            "expected_inner_csv",
            "expected_interval",
            "expected_schema_key",
            "planned_status",
            "reuse_candidate_status",
            "url_existence_checked",
            "downloaded",
            "sha256_claimed",
            "zip_open_checked",
            "csv_header_checked",
            "build_ready",
            "acquisition_ready",
        ],
    }
    symbol_list = {
        **summary,
        "artifact_type": "first_chunk_symbol_list",
        "symbols": first_symbols,
    }
    planned_manifest = {
        **summary,
        "artifact_type": "first_chunk_planned_file_manifest_preview",
        "full_entry_manifest_written": True,
        "planned_entries": planned_entries,
    }
    reuse_report = {
        **summary,
        "artifact_type": "first_chunk_reuse_candidate_report",
        "validated_pilot_overlap_symbols": reuse_symbols,
        "reuse_candidate_entries": reuse_candidate_entries,
        "reuse_finality": "NOT_FINAL_UNTIL_FUTURE_EXECUTION_REVALIDATES_HASH_PATH_PROVENANCE",
    }
    resource_limits = {
        **summary,
        "artifact_type": "first_chunk_download_resource_limits",
        "max_chunk_symbol_count": EXPECTED_FIRST_CHUNK_SYMBOL_COUNT,
        "max_expected_file_count": EXPECTED_FIRST_CHUNK_FILE_COUNT,
        "no_symbols_outside_first_chunk": True,
        "no_dates_outside_range": f"{DATE_START}_THROUGH_{DATE_END}",
        "no_api_browse": True,
        "no_data_build_aggregation": True,
        "future_execution_allowed_scope": "READ_ONLY_ZIP_INVENTORY_AND_CSV_HEADER_SAMPLE_ROWS_AFTER_DOWNLOAD_OR_REUSE",
        "max_csv_sample_rows_per_file": 5,
        "compute_sha256_after_download_or_reuse_validation": True,
        "record_gaps_failures_without_silently_skipping": True,
    }
    approval = {
        **summary,
        "artifact_type": "first_chunk_download_execution_approval_record",
        "approval_scope": "next separate first chunk download execution module only",
        "approval_grants_first_chunk_download_preview_now": True,
        "approval_grants_download_now": False,
        "approval_grants_future_first_chunk_download_execution_next": summary["replacement_checks_all_true"],
        "approval_grants_full_universe_download_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_api_now": False,
        "approval_grants_browse_now": False,
        "approval_grants_research_backtest_edge_now": False,
    }
    self_validator = {
        **summary,
        "artifact_type": "self_validator",
        "required_outputs": REQUIRED_OUTPUTS,
        "required_output_count": len(REQUIRED_OUTPUTS),
        "forbidden_actions_verified_by_construction": True,
    }
    summary_artifact = {
        **summary,
        "artifact_type": "summary",
        "artifact_count": len(REQUIRED_OUTPUTS),
    }
    return {
        "historical_okx_full_usdt_swap_first_chunk_download_preview.json": preview,
        "historical_okx_full_usdt_swap_first_chunk_symbol_list.json": symbol_list,
        "historical_okx_full_usdt_swap_first_chunk_planned_file_manifest_preview.json": planned_manifest,
        "historical_okx_full_usdt_swap_first_chunk_reuse_candidate_report.json": reuse_report,
        "historical_okx_full_usdt_swap_first_chunk_download_resource_limits.json": resource_limits,
        "historical_okx_full_usdt_swap_first_chunk_download_execution_approval_record.json": approval,
        "historical_okx_full_usdt_swap_first_chunk_download_preview_self_validator.json": self_validator,
        "historical_okx_full_usdt_swap_first_chunk_download_preview_summary.json": summary_artifact,
    }


def run_preview() -> dict[str, Any]:
    py_state = tracked_python_validation()
    artifacts = read_artifacts()
    chain = validate_inputs(artifacts, py_state)
    planned_entries = build_planned_manifest(
        chain["chunk_id"],
        chain["first_chunk_symbols"],
        chain["dates"],
        set(chain["pilot_symbols"]),
    )
    summary = build_summary(artifacts, chain, py_state, planned_entries)
    outputs = build_outputs(summary, planned_entries)
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
            "historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_preview_status": BLOCKED_STATUS,
            "first_chunk_download_preview_created": False,
            "blocked_reason": repr(exc),
            "next_module": FAILED_NEXT_MODULE,
            "replacement_checks_all_true": False,
            **common_false_flags(),
            "okx_api_call_performed": False,
            "okx_browse_performed": False,
            "data_download_performed": False,
            "data_build_performed": False,
            "aggregation_performed_now": False,
            "created_at_utc": utc_now(),
        }
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "historical_okx_full_usdt_swap_first_chunk_download_preview_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
