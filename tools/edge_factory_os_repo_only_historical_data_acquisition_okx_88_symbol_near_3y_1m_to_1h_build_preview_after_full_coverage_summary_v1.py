#!/usr/bin/env python3
"""Repo-only build preview for the 88 locked OKX near-3y symbols.

This module previews a future 1m-to-1h build. It does not open source ZIP/CSV
data, build outputs, aggregate rows, download, browse, or call APIs.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_preview_after_full_coverage_summary_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_preview_after_full_coverage_summary_v1"
)
FINAL_SUMMARY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
)

FINAL_SUMMARY = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_summary.json"
FINAL_LEDGER = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_ledger.json"
COMPLETE_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
GAP_LOCKED = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_gap_symbol_set_locked.json"
FINAL_APPROVAL = FINAL_SUMMARY_DIR / "repo_only_okx_88_symbol_near_3y_build_preview_approval_record.json"

EXPECTED_HEAD = "e34cc18"
EXPECTED_SELECTED_SYMBOL_COUNT = 88
EXPECTED_GAP_SYMBOL_COUNT = 215
EXPECTED_DAILY_FILE_COUNT = 1053
MINUTES_PER_DAY = 1440
HOURS_PER_DAY = 24
EXPECTED_SOURCE_ROWS_PER_SYMBOL = EXPECTED_DAILY_FILE_COUNT * MINUTES_PER_DAY
EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H = EXPECTED_DAILY_FILE_COUNT * HOURS_PER_DAY
EXPECTED_TOTAL_SOURCE_FILE_COUNT = EXPECTED_SELECTED_SYMBOL_COUNT * EXPECTED_DAILY_FILE_COUNT
EXPECTED_TOTAL_SOURCE_ROWS = EXPECTED_SELECTED_SYMBOL_COUNT * EXPECTED_SOURCE_ROWS_PER_SYMBOL
EXPECTED_TOTAL_OUTPUT_ROWS_1H = EXPECTED_SELECTED_SYMBOL_COUNT * EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H
MAX_AVAILABLE_START_CANDIDATE = "2023-07-01"
MAX_AVAILABLE_END_DATE = "2026-05-18"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PREVIEW_CREATED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PREVIEW_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_preview_blocked_record_v1.py"


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


def symbol_from_row(row: Any) -> str:
    if isinstance(row, str):
        return row
    if isinstance(row, dict) and isinstance(row.get("symbol"), str):
        return row["symbol"]
    raise ValueError(f"Cannot resolve symbol from row: {row!r}")


def load_source_symbol_file_counts(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    source_map: dict[str, dict[str, Any]] = {}
    for source in ledger.get("source_artifacts", []):
        per_symbol_path = Path(source["per_symbol_path"])
        per_symbol_doc = read_json(per_symbol_path)
        for row in per_symbol_doc.get("per_symbol_coverage", []):
            symbol = symbol_from_row(row)
            if symbol in source_map:
                raise ValueError(f"Duplicate per-symbol provenance row detected for {symbol}")
            source_map[symbol] = {
                "available_file_count": int(row.get("available_file_count", 0)),
                "build_ready": row.get("build_ready", False) is True,
                "coverage_complete": row.get("coverage_complete") is True,
                "full_near_3y_archive_coverage_validated": row.get("full_near_3y_archive_coverage_validated") is True,
                "missing_or_failed_file_count": int(row.get("missing_or_failed_file_count", 0)),
                "planned_file_count": int(row.get("planned_file_count", 0)),
                "provenance_artifact": str(per_symbol_path),
                "source_manifest_acquisition_ready": row.get("acquisition_ready", False) is True,
            }
    return source_map


def build_preview() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    final_summary = read_json(FINAL_SUMMARY)
    final_ledger = read_json(FINAL_LEDGER)
    complete_locked = read_json(COMPLETE_LOCKED)
    gap_locked = read_json(GAP_LOCKED)
    final_approval = read_json(FINAL_APPROVAL)

    selected_symbols = list(complete_locked.get("near_3y_complete_symbols") or complete_locked.get("build_preview_eligible_symbols") or [])
    gap_symbols = list(gap_locked.get("coverage_gap_symbols") or [])
    selected_set = set(selected_symbols)
    gap_set = set(gap_symbols)
    overlap = sorted(selected_set & gap_set)
    source_counts = load_source_symbol_file_counts(final_ledger)
    selected_symbol_file_rows = {
        symbol: source_counts.get(symbol, {})
        for symbol in selected_symbols
    }
    selected_symbols_all_have_1053_files = all(
        row.get("available_file_count") == EXPECTED_DAILY_FILE_COUNT
        and row.get("planned_file_count") == EXPECTED_DAILY_FILE_COUNT
        and row.get("missing_or_failed_file_count") == 0
        and row.get("coverage_complete") is True
        and row.get("full_near_3y_archive_coverage_validated") is True
        and row.get("build_ready") is False
        and row.get("source_manifest_acquisition_ready") is False
        for row in selected_symbol_file_rows.values()
    ) and len(selected_symbol_file_rows) == len(selected_symbols)

    output_schema = [
        {"name": "symbol", "type": "string", "description": "OKX instrument id"},
        {"name": "hour_open_time_utc", "type": "datetime_utc", "description": "Hour bucket open time"},
        {"name": "open", "type": "decimal", "rule": "first clean 1m open in hour"},
        {"name": "high", "type": "decimal", "rule": "max clean 1m high in hour"},
        {"name": "low", "type": "decimal", "rule": "min clean 1m low in hour"},
        {"name": "close", "type": "decimal", "rule": "last clean 1m close in hour"},
        {"name": "volume", "type": "decimal", "rule": "sum clean 1m volume in hour"},
        {"name": "volume_ccy", "type": "decimal", "rule": "sum clean 1m quote/currency volume if present"},
        {"name": "volume_ccy_quote", "type": "decimal", "rule": "sum clean 1m quote volume if present"},
        {"name": "source_row_count", "type": "int", "rule": "count of clean 1m rows in hour"},
        {"name": "complete_1h", "type": "bool", "rule": "true only when source_row_count=60 and no quarantined/missing minute"},
        {"name": "source_manifest_ref", "type": "string", "description": "Reference to validated source manifest row(s)"},
        {"name": "source_sha256_ref", "type": "string", "description": "Reference to source archive hash/provenance"},
        {"name": "pipeline_validation_only", "type": "bool", "value": True},
    ]

    duplicate_conflict_policy = {
        "backfill_allowed": False,
        "canonical_exact_duplicate_policy": "drop exact duplicate extra rows while keeping one canonical row",
        "conflicting_duplicate_policy": "quarantine material conflicting duplicate open-time groups",
        "duplicate_conflict_policy_carried_forward": True,
        "forward_fill_allowed": False,
        "material_conflict_resolution": "no choosing, averaging, or merging conflicting OHLCV rows",
        "policy_references": [
            "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_sol_duplicate_diagnostic_after_policy_clean_build_anomaly_v1.py",
            "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_eth_exact_duplicate_policy_after_diagnostic_v1.py",
            "edge_factory_os_repo_only_historical_data_acquisition_okx_10_symbol_pilot_eth_material_duplicate_conflict_policy_after_residual_diagnostic_v1.py",
            "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_material_duplicate_conflict_policy_after_conflict_review_v1.py",
        ],
        "synthetic_fill_allowed": False,
        "incomplete_hours_marked_incomplete": True,
    }

    aggregation_policy = {
        "aggregation_execution_now": False,
        "complete_hour_policy": "complete_1h=true only when source_row_count=60 and no quarantined or missing minute exists in that hour",
        "hour_bucket": "UTC hour_open_time",
        "incomplete_hours_marked_incomplete": True,
        "rules": {
            "close": "last clean 1m close in hour",
            "high": "max clean 1m high in hour",
            "low": "min clean 1m low in hour",
            "open": "first clean 1m open in hour",
            "source_row_count": "count clean 1m rows in hour",
            "volume_fields": "sum clean 1m volume fields in hour",
        },
        "selected_symbol_count": len(selected_symbols),
        "source_granularity": "1m",
        "target_granularity": "1h",
    }

    validation_plan = {
        "future_build_execution_must_full_read_csv": True,
        "full_csv_read_now": False,
        "steps": [
            "revalidate selected source ZIP paths exist",
            "revalidate SHA256 and provenance for every selected source archive",
            "verify every selected ZIP opens",
            "reject path traversal",
            "verify expected inner CSV exists",
            "verify source schema",
            "verify observed symbol matches selected symbol",
            "full-read CSV only during future build execution",
            "apply exact duplicate and material conflict policies",
            "validate 1h output schema and complete_1h semantics after future build",
        ],
        "validation_plan_created": True,
    }

    sizing_strategy = {
        "chunked_or_per_symbol_build_recommended": True,
        "expected_total_output_rows_1h": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "memory_safe_streaming_recommended": True,
        "per_symbol_build_then_manifest_concat_recommended": True,
        "single_execution_allowed_later": False,
        "strategy": "Use streaming per-symbol build shards with manifest-first validation; perform final concat only after per-symbol validators pass.",
    }

    input_manifest = {
        "artifact_type": "88_symbol_1m_to_1h_build_input_manifest_preview",
        "date_range_end": MAX_AVAILABLE_END_DATE,
        "date_range_start": MAX_AVAILABLE_START_CANDIDATE,
        "excluded_gap_symbol_count": len(gap_symbols),
        "excluded_gap_symbols": gap_symbols,
        "selected_symbol_count": len(selected_symbols),
        "selected_symbol_expected_daily_file_count": EXPECTED_DAILY_FILE_COUNT,
        "selected_symbol_file_rows": selected_symbol_file_rows,
        "selected_symbols": selected_symbols,
        "source_manifest_acquisition_ready": False,
    }

    expected_counts = {
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT,
        "expected_output_rows_per_symbol_1h": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "expected_source_rows_per_symbol": EXPECTED_SOURCE_ROWS_PER_SYMBOL,
        "expected_total_output_rows_1h": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "selected_symbol_count": len(selected_symbols),
    }

    final_coverage_summary_confirmed = (
        final_summary.get("okx_full_usdt_swap_coverage_discovery_final_summary_status")
        == "PASS_REPO_ONLY_OKX_FULL_USDT_SWAP_COVERAGE_DISCOVERY_FINAL_SUMMARY_CREATED"
        and final_summary.get("replacement_checks_all_true") is True
        and final_summary.get("near_3y_complete_symbol_count") == EXPECTED_SELECTED_SYMBOL_COUNT
        and final_summary.get("coverage_gap_symbol_count") == EXPECTED_GAP_SYMBOL_COUNT
        and final_summary.get("approval_grants_future_88_symbol_1m_to_1h_build_preview_next") is True
        and final_summary.get("approval_grants_build_now") is False
    )
    locked_complete_symbol_set_confirmed = (
        complete_locked.get("near_3y_complete_symbol_count") == EXPECTED_SELECTED_SYMBOL_COUNT
        and complete_locked.get("build_preview_eligible_symbol_count") == EXPECTED_SELECTED_SYMBOL_COUNT
        and complete_locked.get("files_marked_build_ready") is False
        and complete_locked.get("source_manifest_acquisition_ready") is False
    )
    locked_gap_symbol_set_confirmed = (
        gap_locked.get("coverage_gap_symbol_count") == EXPECTED_GAP_SYMBOL_COUNT
        and gap_locked.get("build_preview_excluded_symbol_count") == EXPECTED_GAP_SYMBOL_COUNT
        and gap_locked.get("gap_symbols_excluded_from_build_preview") is True
    )

    pass_checks = {
        "approval_grants_build_preview_next": final_approval.get("approval_grants_future_88_symbol_1m_to_1h_build_preview_next") is True,
        "complete_gap_no_overlap": len(overlap) == 0,
        "expected_counts_match_formulas": expected_counts
        == {
            "expected_daily_file_count_per_symbol": 1053,
            "expected_output_rows_per_symbol_1h": 25272,
            "expected_source_rows_per_symbol": 1516320,
            "expected_total_output_rows_1h": 2223936,
            "expected_total_source_file_count": 92664,
            "expected_total_source_rows": 133436160,
            "selected_symbol_count": 88,
        },
        "final_coverage_summary_confirmed": final_coverage_summary_confirmed,
        "head_matches_expected": head == EXPECTED_HEAD,
        "locked_complete_symbol_set_confirmed": locked_complete_symbol_set_confirmed,
        "locked_gap_symbol_set_confirmed": locked_gap_symbol_set_confirmed,
        "repo_clean": repo_clean,
        "selected_symbol_count": len(selected_symbols) == EXPECTED_SELECTED_SYMBOL_COUNT,
        "excluded_gap_symbol_count": len(gap_symbols) == EXPECTED_GAP_SYMBOL_COUNT,
        "selected_symbols_all_have_1053_files": selected_symbols_all_have_1053_files,
        "strict_3y_not_claimed": final_summary.get("strict_3y_completeness_claimed") is False,
        "no_ready_or_build_claims": all(
            item is False
            for item in [
                final_summary.get("output_valid_for_research_backtest"),
                final_summary.get("output_valid_for_edge_claim"),
                final_summary.get("source_manifest_acquisition_ready"),
                final_summary.get("broad_acquisition_ready"),
            ]
        ),
    }
    replacement_checks_all_true = all(pass_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE

    approval_record = {
        "approval_grants_aggregation_now": False,
        "approval_grants_build_execution_now": False,
        "approval_grants_build_preview_now": True,
        "approval_grants_data_build_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_full_csv_read_now": False,
        "approval_grants_future_88_symbol_1m_to_1h_build_execution_next": replacement_checks_all_true,
        "approval_grants_research_backtest_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "artifact_type": "88_symbol_1m_to_1h_build_execution_approval_record",
        "build_execution_allowed_now": False,
        "next_module": next_module,
        "selected_symbol_count": len(selected_symbols),
    }

    summary = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": final_summary.get("active_p1_attention_count", 0),
        "aggregation_performed_now": False,
        "approval_grants_aggregation_now": False,
        "approval_grants_build_execution_now": False,
        "approval_grants_data_build_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_full_csv_read_now": False,
        "approval_grants_future_88_symbol_1m_to_1h_build_execution_next": replacement_checks_all_true,
        "approval_grants_research_backtest_now": False,
        "backfill_allowed": False,
        "broad_acquisition_ready": False,
        "build_execution_approval_record_created": replacement_checks_all_true,
        "build_preview_created": replacement_checks_all_true,
        "build_sizing_strategy_created": True,
        "chunked_or_per_symbol_build_recommended": True,
        "current_evidence_chain_quality_after_preview": (
            "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PREVIEW_READY_FOR_EXECUTION"
            if replacement_checks_all_true
            else "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PREVIEW_BLOCKED_REVIEW_REQUIRED"
        ),
        "data_build_performed": False,
        "data_download_performed": False,
        "duplicate_conflict_policy_carried_forward": True,
        "excluded_gap_symbol_count": len(gap_symbols),
        "expected_daily_file_count_per_symbol": EXPECTED_DAILY_FILE_COUNT,
        "expected_output_rows_per_symbol_1h": EXPECTED_OUTPUT_ROWS_PER_SYMBOL_1H,
        "expected_source_rows_per_symbol": EXPECTED_SOURCE_ROWS_PER_SYMBOL,
        "expected_total_output_rows_1h": EXPECTED_TOTAL_OUTPUT_ROWS_1H,
        "expected_total_source_file_count": EXPECTED_TOTAL_SOURCE_FILE_COUNT,
        "expected_total_source_rows": EXPECTED_TOTAL_SOURCE_ROWS,
        "final_coverage_summary_confirmed": final_coverage_summary_confirmed,
        "forward_fill_allowed": False,
        "full_csv_read_performed": False,
        "incomplete_hours_marked_incomplete": True,
        "locked_complete_symbol_set_confirmed": locked_complete_symbol_set_confirmed,
        "locked_gap_symbol_set_confirmed": locked_gap_symbol_set_confirmed,
        "max_available_end_date": MAX_AVAILABLE_END_DATE,
        "max_available_start_candidate": MAX_AVAILABLE_START_CANDIDATE,
        "memory_safe_streaming_recommended": True,
        "next_module": next_module,
        "okx_88_symbol_near_3y_1m_to_1h_build_preview_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "output_schema_preview_created": True,
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": False,
        "replacement_checks": pass_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "selected_symbol_count": len(selected_symbols),
        "selected_symbols_all_have_1053_files": selected_symbols_all_have_1053_files,
        "source_manifest_acquisition_ready": False,
        "strict_3y_completeness_claimed": False,
        "synthetic_fill_allowed": False,
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_plan_created": True,
        "created_at_utc": now_utc(),
    }

    return {
        "aggregation_policy": aggregation_policy,
        "approval_record": approval_record,
        "duplicate_conflict_policy": duplicate_conflict_policy,
        "expected_counts": expected_counts,
        "input_manifest": input_manifest,
        "output_schema": {
            "artifact_type": "88_symbol_1h_output_schema_preview",
            "fields": output_schema,
            "output_schema_preview_created": True,
            "pipeline_validation_only": True,
        },
        "preview": {
            **summary,
            "aggregation_policy_preview": aggregation_policy,
            "duplicate_conflict_policy_preview": duplicate_conflict_policy,
            "expected_counts": expected_counts,
            "input_manifest_preview_artifact": "repo_only_okx_88_symbol_near_3y_build_input_manifest_preview.json",
            "selected_symbols": selected_symbols,
            "excluded_gap_symbols": gap_symbols,
            "source_artifacts": final_ledger.get("source_artifacts", []),
            "validation_plan": validation_plan,
            "build_sizing_strategy": sizing_strategy,
        },
        "self_validator": {
            "artifact_type": "88_symbol_1m_to_1h_build_preview_self_validator",
            "created_at_utc": now_utc(),
            "replacement_checks": pass_checks,
            "replacement_checks_all_true": replacement_checks_all_true,
            "status": status,
        },
        "sizing_strategy": sizing_strategy,
        "summary": summary,
        "validation_plan": validation_plan,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_preview.json", outputs["preview"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_build_input_manifest_preview.json", outputs["input_manifest"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_build_expected_counts.json", outputs["expected_counts"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_aggregation_policy_preview.json", outputs["aggregation_policy"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_duplicate_conflict_policy_preview.json", outputs["duplicate_conflict_policy"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_output_schema_preview.json", outputs["output_schema"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_build_validation_plan.json", outputs["validation_plan"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_build_sizing_and_execution_strategy.json", outputs["sizing_strategy"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_build_execution_approval_record.json", outputs["approval_record"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_build_preview_self_validator.json", outputs["self_validator"])


def main() -> int:
    outputs = build_preview()
    write_outputs(outputs)
    print(json.dumps(outputs["summary"], indent=2, sort_keys=True))
    return 0 if outputs["summary"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
