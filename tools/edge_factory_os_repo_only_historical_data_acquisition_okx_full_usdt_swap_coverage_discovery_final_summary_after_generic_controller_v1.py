#!/usr/bin/env python3
"""Final coverage discovery summary after the generic OKX chunk controller.

Repo-only reconciler. It reads JSON coverage artifacts and writes summary
artifacts only; it does not download, fetch, build, aggregate, or open data.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1.py"
)
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"

GENERIC_DIR = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_generic_chunk_coverage_cycle_execution_v1"
CHUNK_01_VALIDATOR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_execution_validator_after_execution_v1"
    / "historical_okx_full_usdt_swap_first_chunk_per_symbol_coverage_validation_report.json"
)
CHUNK_01_SUMMARY = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_first_chunk_download_coverage_summary_after_validator_v1"
    / "historical_okx_full_usdt_swap_first_chunk_download_coverage_summary.json"
)
CHUNK_02_VALIDATOR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_execution_validator_after_execution_v1"
    / "historical_okx_full_usdt_swap_chunk_02_per_symbol_coverage_validation_report.json"
)
CHUNK_02_SUMMARY = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_chunk_02_download_coverage_summary_after_validator_v1"
    / "historical_okx_full_usdt_swap_chunk_02_download_coverage_summary.json"
)
CHUNK_03_PER_SYMBOL = GENERIC_DIR / "historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_per_symbol_coverage_summary.json"

CANDIDATE_LIST = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_symbol_source_discovery_after_universe_preview_approval_v1"
    / "historical_okx_full_usdt_swap_candidate_symbol_list.json"
)
CHUNK_PLAN = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_archive_coverage_manifest_preview_after_eligibility_preview_v1"
    / "historical_okx_full_usdt_swap_archive_coverage_chunk_plan.json"
)

EXPECTED_HEAD = "544355e"
EXPECTED_DAILY_FILE_COUNT = 1053
EXPECTED_TOTAL_SYMBOLS = 303
EXPECTED_COMPLETE_SYMBOLS = 88
EXPECTED_GAP_SYMBOLS = 215
EXPECTED_CHUNKS = 16
MAX_AVAILABLE_START_CANDIDATE = "2023-07-01"
MAX_AVAILABLE_END_DATE = "2026-05-18"
PASS_STATUS = "PASS_REPO_ONLY_OKX_FULL_USDT_SWAP_COVERAGE_DISCOVERY_FINAL_SUMMARY_CREATED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_FULL_USDT_SWAP_COVERAGE_DISCOVERY_FINAL_SUMMARY_PRECHECK_OR_RECONCILIATION_FAILED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_preview_after_full_coverage_summary_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_blocked_record_v1.py"


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


def symbol_from_entry(entry: Any) -> str:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict) and isinstance(entry.get("symbol"), str):
        return entry["symbol"]
    raise ValueError(f"Cannot resolve symbol from entry: {entry!r}")


def false_or_absent(record: dict[str, Any], *keys: str) -> bool:
    return all(record.get(key, False) is False for key in keys)


def load_chunk_artifacts(chunk_num: int) -> tuple[Path, dict[str, Any], Path | None, dict[str, Any] | None]:
    if chunk_num == 1:
        per_path = CHUNK_01_VALIDATOR
        summary_path = CHUNK_01_SUMMARY
    elif chunk_num == 2:
        per_path = CHUNK_02_VALIDATOR
        summary_path = CHUNK_02_SUMMARY
    elif chunk_num == 3:
        per_path = CHUNK_03_PER_SYMBOL
        summary_path = None
    else:
        chunk_id = f"chunk_{chunk_num:02d}"
        per_path = GENERIC_DIR / f"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{chunk_id}_per_symbol_coverage_summary.json"
        summary_path = GENERIC_DIR / f"historical_okx_full_usdt_swap_generic_chunk_coverage_cycle_{chunk_id}_summary.json"

    per_doc = read_json(per_path)
    summary_doc = read_json(summary_path) if summary_path else None
    return per_path, per_doc, summary_path, summary_doc


def normalized_bool(record: dict[str, Any], primary: str, fallback: str | None = None) -> bool:
    if primary in record:
        return record.get(primary) is True
    if fallback:
        return record.get(fallback) is True
    return False


def build_chunk_record(chunk_num: int) -> dict[str, Any]:
    per_path, per_doc, summary_path, summary_doc = load_chunk_artifacts(chunk_num)
    chunk_id = f"chunk_{chunk_num:02d}"
    rows = per_doc.get("per_symbol_coverage") or []
    if per_doc.get("chunk_id") != chunk_id:
        raise ValueError(f"{per_path} has chunk_id={per_doc.get('chunk_id')}, expected {chunk_id}")
    if not rows:
        raise ValueError(f"{per_path} has no per_symbol_coverage rows")

    complete_rows = [
        row
        for row in rows
        if row.get("coverage_complete") is True
        and row.get("full_near_3y_archive_coverage_validated") is True
        and int(row.get("available_file_count", -1)) == EXPECTED_DAILY_FILE_COUNT
        and int(row.get("missing_or_failed_file_count", -1)) == 0
        and row.get("build_ready", False) is False
        and row.get("acquisition_ready", False) is False
    ]
    gap_rows = [row for row in rows if row not in complete_rows]

    symbols = [symbol_from_entry(row) for row in rows]
    complete_symbols = [symbol_from_entry(row) for row in complete_rows]
    gap_symbols = [symbol_from_entry(row) for row in gap_rows]
    planned = sum(int(row.get("planned_file_count", 0)) for row in rows)
    available = sum(int(row.get("available_file_count", 0)) for row in rows)
    missing = sum(int(row.get("missing_or_failed_file_count", 0)) for row in rows)
    symbol_count = len(rows)
    expected_file_count = symbol_count * EXPECTED_DAILY_FILE_COUNT

    source = summary_doc or per_doc
    return {
        "active_p0_blocker_count": int(per_doc.get("active_p0_blocker_count", source.get("active_p0_blocker_count", 999))),
        "active_p1_attention_count": int(per_doc.get("active_p1_attention_count", source.get("active_p1_attention_count", 0))),
        "all_available_expected_inner_csv_present": per_doc.get("all_available_expected_inner_csv_present") is True,
        "all_available_expected_schema_match": per_doc.get("all_available_expected_schema_match") is True,
        "all_available_observed_symbols_match_expected": per_doc.get("all_available_observed_symbols_match_expected") is True,
        "all_available_zips_open_success": per_doc.get("all_available_zips_open_success") is True,
        "all_hashes_computed_or_revalidated": per_doc.get("all_hashes_computed_or_revalidated") is True,
        "any_zip_path_traversal_detected": per_doc.get("any_zip_path_traversal_detected") is True,
        "chunk_id": chunk_id,
        "chunk_num": chunk_num,
        "chunk_symbol_count": symbol_count,
        "complete_symbols": complete_symbols,
        "count_reconciliation_pass": per_doc.get("count_reconciliation_pass") is True,
        "data_build_performed": normalized_bool(per_doc, "data_build_performed", "data_build_performed_by_validator"),
        "files_marked_build_ready": per_doc.get("files_marked_build_ready", False) is True,
        "final_available_file_count": available,
        "full_csv_read_performed": per_doc.get("full_csv_read_performed", False) is True,
        "gap_symbols": gap_symbols,
        "missing_or_failed_file_count": missing,
        "output_valid_for_edge_claim": per_doc.get("output_valid_for_edge_claim", False) is True,
        "output_valid_for_research_backtest": per_doc.get("output_valid_for_research_backtest", False) is True,
        "per_symbol_path": str(per_path),
        "planned_file_count": planned,
        "replacement_checks_all_true": per_doc.get("replacement_checks_all_true") is True,
        "source_manifest_acquisition_ready": per_doc.get("source_manifest_acquisition_ready", False) is True,
        "summary_path": str(summary_path) if summary_path else None,
        "symbols": symbols,
        "symbols_with_coverage_gaps_count": len(gap_symbols),
        "symbols_with_full_file_coverage_count": len(complete_symbols),
        "expected_chunk_file_count": expected_file_count,
        "aggregation_performed_now": normalized_bool(per_doc, "aggregation_performed_now", "aggregation_performed_by_validator"),
        "rows": rows,
    }


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    candidate_doc = read_json(CANDIDATE_LIST)
    candidate_symbols = candidate_doc.get("candidate_symbols") or []
    chunk_plan_doc = read_json(CHUNK_PLAN)

    chunks = [build_chunk_record(i) for i in range(1, EXPECTED_CHUNKS + 1)]
    complete_symbols: list[str] = []
    gap_symbols: list[str] = []
    all_symbols: list[str] = []
    for chunk in chunks:
        complete_symbols.extend(chunk["complete_symbols"])
        gap_symbols.extend(chunk["gap_symbols"])
        all_symbols.extend(chunk["symbols"])

    complete_counter = Counter(complete_symbols)
    gap_counter = Counter(gap_symbols)
    all_counter = Counter(all_symbols)
    complete_set = set(complete_symbols)
    gap_set = set(gap_symbols)
    candidate_set = set(candidate_symbols)
    duplicate_symbol_count = sum(count - 1 for count in all_counter.values() if count > 1)
    symbol_missing_from_final_sets = sorted(candidate_set - complete_set - gap_set)
    symbols_in_both = sorted(complete_set & gap_set)
    final_complete = sorted(complete_set)
    final_gap = sorted(gap_set)
    total_planned = sum(chunk["planned_file_count"] for chunk in chunks)
    total_available = sum(chunk["final_available_file_count"] for chunk in chunks)
    total_missing = sum(chunk["missing_or_failed_file_count"] for chunk in chunks)
    max_p1 = max((chunk["active_p1_attention_count"] for chunk in chunks), default=0)

    all_complete_symbols_have_1053_files = all(
        int(row.get("available_file_count", 0)) == EXPECTED_DAILY_FILE_COUNT
        and int(row.get("missing_or_failed_file_count", -1)) == 0
        and row.get("coverage_complete") is True
        and row.get("full_near_3y_archive_coverage_validated") is True
        for chunk in chunks
        for row in chunk["rows"]
        if symbol_from_entry(row) in complete_set
    )
    all_gap_symbols_have_missing_files = all(
        int(row.get("missing_or_failed_file_count", 0)) > 0
        for chunk in chunks
        for row in chunk["rows"]
        if symbol_from_entry(row) in gap_set
    )

    chunk_count_completed = sum(1 for chunk in chunks if chunk["chunk_symbol_count"] > 0)
    total_candidate_symbol_count = int(candidate_doc.get("candidate_symbol_count", len(candidate_symbols)))
    complete_plus_gap_equals_total = len(final_complete) + len(final_gap) == total_candidate_symbol_count
    all_chunk_count_reconciliations_passed = all(
        chunk["count_reconciliation_pass"]
        and chunk["planned_file_count"] == chunk["expected_chunk_file_count"]
        and chunk["final_available_file_count"] + chunk["missing_or_failed_file_count"] == chunk["planned_file_count"]
        for chunk in chunks
    )
    all_chunks_replacement_checks_true = all(chunk["replacement_checks_all_true"] for chunk in chunks)
    all_chunks_active_p0_zero = all(chunk["active_p0_blocker_count"] == 0 for chunk in chunks)
    source_safety_ok = all(
        chunk["full_csv_read_performed"] is False
        and chunk["data_build_performed"] is False
        and chunk["aggregation_performed_now"] is False
        and chunk["files_marked_build_ready"] is False
        and chunk["source_manifest_acquisition_ready"] is False
        and chunk["output_valid_for_research_backtest"] is False
        and chunk["output_valid_for_edge_claim"] is False
        and chunk["all_hashes_computed_or_revalidated"] is True
        and chunk["all_available_zips_open_success"] is True
        and chunk["any_zip_path_traversal_detected"] is False
        and chunk["all_available_expected_inner_csv_present"] is True
        and chunk["all_available_expected_schema_match"] is True
        and chunk["all_available_observed_symbols_match_expected"] is True
        for chunk in chunks
    )

    pass_checks = {
        "head_matches_expected": head == EXPECTED_HEAD,
        "repo_clean": repo_clean,
        "chunk_count_completed": chunk_count_completed == EXPECTED_CHUNKS,
        "total_candidate_symbol_count": total_candidate_symbol_count == EXPECTED_TOTAL_SYMBOLS,
        "candidate_symbol_list_unique": len(candidate_symbols) == len(candidate_set) == EXPECTED_TOTAL_SYMBOLS,
        "symbols_evaluated_for_download_coverage": len(all_symbols) == EXPECTED_TOTAL_SYMBOLS,
        "cumulative_pending_symbol_count": total_candidate_symbol_count - len(set(all_symbols)) == 0,
        "near_3y_complete_symbol_count": len(final_complete) == EXPECTED_COMPLETE_SYMBOLS,
        "coverage_gap_symbol_count": len(final_gap) == EXPECTED_GAP_SYMBOLS,
        "complete_plus_gap_equals_total": complete_plus_gap_equals_total,
        "duplicate_symbol_count_zero": duplicate_symbol_count == 0,
        "symbol_missing_from_final_sets_count_zero": len(symbol_missing_from_final_sets) == 0,
        "symbol_in_both_complete_and_gap_count_zero": len(symbols_in_both) == 0,
        "all_complete_symbols_have_1053_files": all_complete_symbols_have_1053_files,
        "all_gap_symbols_have_missing_files": all_gap_symbols_have_missing_files,
        "all_chunk_count_reconciliations_passed": all_chunk_count_reconciliations_passed,
        "all_chunks_replacement_checks_true": all_chunks_replacement_checks_true,
        "all_chunks_active_p0_zero": all_chunks_active_p0_zero,
        "source_safety_ok": source_safety_ok,
    }
    replacement_checks_all_true = all(pass_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE

    chunk_table = [
        {
            "active_p0_blocker_count": chunk["active_p0_blocker_count"],
            "chunk_id": chunk["chunk_id"],
            "chunk_symbol_count": chunk["chunk_symbol_count"],
            "count_reconciliation_pass": chunk["count_reconciliation_pass"],
            "expected_chunk_file_count": chunk["expected_chunk_file_count"],
            "final_available_file_count": chunk["final_available_file_count"],
            "missing_or_failed_file_count": chunk["missing_or_failed_file_count"],
            "planned_file_count": chunk["planned_file_count"],
            "replacement_checks_all_true": chunk["replacement_checks_all_true"],
            "symbols_with_coverage_gaps_count": chunk["symbols_with_coverage_gaps_count"],
            "symbols_with_full_file_coverage_count": chunk["symbols_with_full_file_coverage_count"],
        }
        for chunk in chunks
    ]

    summary = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": max_p1,
        "aggregation_performed_now": False,
        "all_chunk_count_reconciliations_passed": all_chunk_count_reconciliations_passed,
        "all_chunks_active_p0_zero": all_chunks_active_p0_zero,
        "all_chunks_replacement_checks_true": all_chunks_replacement_checks_true,
        "all_complete_symbols_have_1053_files": all_complete_symbols_have_1053_files,
        "all_gap_symbols_have_missing_files": all_gap_symbols_have_missing_files,
        "approval_grants_aggregation_now": False,
        "approval_grants_build_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_final_coverage_summary_now": True,
        "approval_grants_future_88_symbol_1m_to_1h_build_preview_next": replacement_checks_all_true,
        "approval_grants_research_backtest_now": False,
        "broad_acquisition_ready": False,
        "build_preview_approval_record_created": replacement_checks_all_true,
        "chunk_count_completed": chunk_count_completed,
        "complete_plus_gap_equals_total": complete_plus_gap_equals_total,
        "coverage_gap_symbol_count": len(final_gap),
        "current_evidence_chain_quality_after_summary": (
            "OKX_FULL_USDT_SWAP_COVERAGE_DISCOVERY_FINAL_SUMMARY_COMPLETE_88_SYMBOL_BUILD_PREVIEW_READY"
            if replacement_checks_all_true
            else "OKX_FULL_USDT_SWAP_COVERAGE_DISCOVERY_FINAL_SUMMARY_BLOCKED_REVIEW_REQUIRED"
        ),
        "data_build_performed": False,
        "data_download_performed": False,
        "delisted_historical_symbols_not_proven": True,
        "duplicate_symbol_count": duplicate_symbol_count,
        "files_marked_build_ready": False,
        "final_summary_created": replacement_checks_all_true,
        "full_csv_read_performed": False,
        "locked_complete_symbol_set_created": replacement_checks_all_true,
        "locked_gap_symbol_set_created": replacement_checks_all_true,
        "max_available_end_date": MAX_AVAILABLE_END_DATE,
        "max_available_start_candidate": MAX_AVAILABLE_START_CANDIDATE,
        "near_3y_complete_symbol_count": len(final_complete),
        "next_module": next_module,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_full_usdt_swap_coverage_discovery_final_summary_status": status,
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": False,
        "replacement_checks": pass_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "safe_for_full_universe_acquisition": False,
        "source_manifest_acquisition_ready": False,
        "strict_3y_completeness_claimed": False,
        "survivorship_bias_limitations_recorded": True,
        "symbol_in_both_complete_and_gap_count": len(symbols_in_both),
        "symbol_missing_from_final_sets_count": len(symbol_missing_from_final_sets),
        "symbols_evaluated_for_download_coverage": len(set(all_symbols)),
        "total_available_file_count": total_available,
        "total_candidate_symbol_count": total_candidate_symbol_count,
        "total_missing_or_failed_file_count": total_missing,
        "total_planned_file_count": total_planned,
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "created_at_utc": now_utc(),
        "cumulative_pending_symbol_count": total_candidate_symbol_count - len(set(all_symbols)),
    }

    final_ledger = {
        **summary,
        "chunk_reconciliation_table": chunk_table,
        "coverage_gap_symbols": final_gap,
        "coverage_percentage_by_symbol_count": round(len(final_complete) / total_candidate_symbol_count * 100.0, 6),
        "near_3y_complete_symbols": final_complete,
        "source_artifacts": [
            {"chunk_id": chunk["chunk_id"], "per_symbol_path": chunk["per_symbol_path"], "summary_path": chunk["summary_path"]}
            for chunk in chunks
        ],
    }

    complete_manifest = {
        "artifact_type": "locked_near_3y_complete_symbol_set",
        "build_preview_eligible_symbol_count": len(final_complete),
        "build_preview_eligible_symbols": final_complete,
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT,
        "files_marked_build_ready": False,
        "locked_for_future_build_preview_only": replacement_checks_all_true,
        "near_3y_complete_symbol_count": len(final_complete),
        "near_3y_complete_symbols": final_complete,
        "output_valid_for_research_backtest": False,
        "requires_future_build_preview_before_any_build": True,
        "source_manifest_acquisition_ready": False,
    }

    gap_manifest = {
        "artifact_type": "locked_coverage_gap_symbol_set",
        "build_preview_excluded_symbol_count": len(final_gap),
        "coverage_gap_symbol_count": len(final_gap),
        "coverage_gap_symbols": final_gap,
        "gap_symbols_excluded_from_build_preview": True,
        "strict_3y_completeness_claimed": False,
    }

    reconciliation = {
        "complete_plus_gap_equals_total": complete_plus_gap_equals_total,
        "coverage_gap_symbol_count": len(final_gap),
        "duplicate_symbol_count": duplicate_symbol_count,
        "near_3y_complete_symbol_count": len(final_complete),
        "symbol_in_both_complete_and_gap_count": len(symbols_in_both),
        "symbol_missing_from_final_sets": symbol_missing_from_final_sets,
        "symbol_missing_from_final_sets_count": len(symbol_missing_from_final_sets),
        "symbols_in_both_complete_and_gap": symbols_in_both,
        "total_available_file_count": total_available,
        "total_candidate_symbol_count": total_candidate_symbol_count,
        "total_missing_or_failed_file_count": total_missing,
        "total_planned_file_count": total_planned,
    }

    limitations = {
        "delisted_historical_symbols_not_proven": True,
        "max_available_end_date": MAX_AVAILABLE_END_DATE,
        "max_available_start_candidate": MAX_AVAILABLE_START_CANDIDATE,
        "strict_3y_completeness_claimed": False,
        "survivorship_bias_limitations_recorded": True,
    }

    approval = {
        "approval_grants_aggregation_now": False,
        "approval_grants_build_execution_now": False,
        "approval_grants_build_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_final_coverage_summary_now": True,
        "approval_grants_full_universe_acquisition_now": False,
        "approval_grants_future_88_symbol_1m_to_1h_build_preview_next": replacement_checks_all_true,
        "approval_grants_research_backtest_now": False,
        "artifact_type": "future_88_symbol_1m_to_1h_build_preview_approval_record",
        "build_execution_allowed_now": False,
        "eligible_symbol_count": len(final_complete),
        "eligible_symbols": final_complete,
        "gap_symbols_excluded_from_build_preview": True,
        "next_module": next_module,
    }

    self_validator = {
        "artifact_type": "final_summary_self_validator",
        "created_at_utc": now_utc(),
        "replacement_checks": pass_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
    }

    return {
        "approval": approval,
        "chunk_plan_artifact": str(CHUNK_PLAN),
        "chunk_plan_chunk_count": len(chunk_plan_doc.get("chunks", [])) if isinstance(chunk_plan_doc.get("chunks"), list) else None,
        "chunk_table": chunk_table,
        "complete_manifest": complete_manifest,
        "final_ledger": final_ledger,
        "gap_manifest": gap_manifest,
        "limitations": limitations,
        "reconciliation": reconciliation,
        "self_validator": self_validator,
        "summary": summary,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_summary.json", outputs["summary"])
    write_json(OUTPUT_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_ledger.json", outputs["final_ledger"])
    write_json(OUTPUT_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json", outputs["complete_manifest"])
    write_json(OUTPUT_DIR / "repo_only_okx_full_usdt_swap_coverage_gap_symbol_set_locked.json", outputs["gap_manifest"])
    write_json(OUTPUT_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_count_reconciliation.json", outputs["reconciliation"])
    write_json(OUTPUT_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_limitations_report.json", outputs["limitations"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_build_preview_approval_record.json", outputs["approval"])
    write_json(OUTPUT_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_summary_self_validator.json", outputs["self_validator"])

    csv_path = OUTPUT_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_chunk_reconciliation_table.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "chunk_id",
            "chunk_symbol_count",
            "expected_chunk_file_count",
            "planned_file_count",
            "final_available_file_count",
            "missing_or_failed_file_count",
            "symbols_with_full_file_coverage_count",
            "symbols_with_coverage_gaps_count",
            "count_reconciliation_pass",
            "replacement_checks_all_true",
            "active_p0_blocker_count",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in outputs["chunk_table"]:
            writer.writerow({field: row[field] for field in fieldnames})


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    summary = outputs["summary"]
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
