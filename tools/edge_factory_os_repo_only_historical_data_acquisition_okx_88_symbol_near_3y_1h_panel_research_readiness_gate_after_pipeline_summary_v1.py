#!/usr/bin/env python3
"""Research-readiness gate for the validated OKX 88-symbol near-3y 1h panel.

This repo-only gate reads prior summary, validation, and manifest artifacts. It
does not read source ZIP/CSV data, rebuild, aggregate, run research, or backtest.
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
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_after_pipeline_summary_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_after_pipeline_summary_v1"
)

FINAL_SUMMARY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_full_usdt_swap_coverage_discovery_final_summary_after_generic_controller_v1"
)
BUILD_PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_preview_after_full_coverage_summary_v1"
)
BUILD_EXECUTION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1"
)
VALIDATOR_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_after_execution_v1"
)
PIPELINE_SUMMARY_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1"
)

FINAL_COVERAGE_SUMMARY = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_summary.json"
LOCKED_COMPLETE_SET = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_near_3y_complete_symbol_set_locked.json"
LOCKED_GAP_SET = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_gap_symbol_set_locked.json"
BUILD_PREVIEW = BUILD_PREVIEW_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_preview.json"
BUILD_EXECUTION_SUMMARY = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_summary.json"
BUILD_EXECUTION_MANIFEST = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
VALIDATOR_SUMMARY = VALIDATOR_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json"
PIPELINE_SUMMARY = PIPELINE_SUMMARY_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary.json"
PIPELINE_LIMITATIONS = PIPELINE_SUMMARY_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_limitations_summary.json"
PIPELINE_POLICY = PIPELINE_SUMMARY_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_policy_effects_summary.json"
PIPELINE_APPROVAL = PIPELINE_SUMMARY_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_approval_record.json"

EXPECTED_HEAD = "a3c4b85"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1H_PANEL_RESEARCH_READINESS_GATE_APPROVED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1H_PANEL_RESEARCH_READINESS_GATE_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_research_readiness_gate_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_NEAR_3Y_1H_PANEL_READ_ONLY_RESEARCH_READY_PREVIEW_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_NEAR_3Y_1H_PANEL_RESEARCH_READINESS_GATE_BLOCKED_REVIEW_REQUIRED"


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
    allowed = {
        f"?? {TOOL_REL.as_posix()}",
        f" M {TOOL_REL.as_posix()}",
        f"A  {TOOL_REL.as_posix()}",
    }
    unexpected = [line for line in lines if line.replace("\\", "/") not in allowed]
    return not unexpected, unexpected


def symbols_from_locked_sets(complete_payload: dict[str, Any], gap_payload: dict[str, Any]) -> dict[str, Any]:
    complete_symbols = set(complete_payload.get("build_preview_eligible_symbols", []))
    gap_symbols = set(gap_payload.get("coverage_gap_symbols", []))
    overlap = complete_symbols & gap_symbols
    return {
        "complete_symbol_count": len(complete_symbols),
        "gap_symbol_count": len(gap_symbols),
        "complete_gap_overlap_count": len(overlap),
        "complete_gap_total_unique_count": len(complete_symbols | gap_symbols),
        "complete_gap_sets_locked": (
            complete_payload.get("artifact_type") == "locked_near_3y_complete_symbol_set"
            and gap_payload.get("artifact_type") == "locked_coverage_gap_symbol_set"
        ),
    }


def build_gate() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    required_paths = [
        FINAL_COVERAGE_SUMMARY,
        LOCKED_COMPLETE_SET,
        LOCKED_GAP_SET,
        BUILD_PREVIEW,
        BUILD_EXECUTION_SUMMARY,
        BUILD_EXECUTION_MANIFEST,
        VALIDATOR_SUMMARY,
        PIPELINE_SUMMARY,
        PIPELINE_LIMITATIONS,
        PIPELINE_POLICY,
        PIPELINE_APPROVAL,
    ]
    artifacts_exist = {path.name: path.exists() for path in required_paths}

    final_coverage = read_json(FINAL_COVERAGE_SUMMARY)
    locked_complete = read_json(LOCKED_COMPLETE_SET)
    locked_gap = read_json(LOCKED_GAP_SET)
    preview = read_json(BUILD_PREVIEW)
    execution = read_json(BUILD_EXECUTION_SUMMARY)
    manifest = read_json(BUILD_EXECUTION_MANIFEST)
    validator = read_json(VALIDATOR_SUMMARY)
    pipeline = read_json(PIPELINE_SUMMARY)
    limitations = read_json(PIPELINE_LIMITATIONS)
    policy = read_json(PIPELINE_POLICY)
    pipeline_approval = read_json(PIPELINE_APPROVAL)

    symbol_sets = symbols_from_locked_sets(locked_complete, locked_gap)
    output_file = Path(manifest.get("output_file", execution.get("output_file", "")))
    output_file_exists = output_file.exists()
    output_manifest_exists = BUILD_EXECUTION_MANIFEST.exists()

    coverage_final_summary_confirmed = (
        final_coverage.get("okx_full_usdt_swap_coverage_discovery_final_summary_status")
        == "PASS_REPO_ONLY_OKX_FULL_USDT_SWAP_COVERAGE_DISCOVERY_FINAL_SUMMARY_CREATED"
        and final_coverage.get("replacement_checks_all_true") is True
    )
    build_preview_confirmed = (
        preview.get("okx_88_symbol_near_3y_1m_to_1h_build_preview_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PREVIEW_CREATED"
        and preview.get("replacement_checks_all_true") is True
    )
    build_execution_confirmed = (
        execution.get("okx_88_symbol_near_3y_1m_to_1h_build_execution_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTED_PENDING_VALIDATOR"
        and execution.get("replacement_checks_all_true") is True
    )
    build_validator_confirmed = (
        validator.get("okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_VALIDATED"
        and validator.get("replacement_checks_all_true") is True
        and validator.get("final_decision") == "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SUMMARY_READY"
    )
    pipeline_summary_confirmed = (
        pipeline.get("okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PIPELINE_SUMMARY_CREATED"
        and pipeline.get("replacement_checks_all_true") is True
        and pipeline_approval.get("approval_grants_future_research_readiness_gate_next") is True
    )

    fields: dict[str, Any] = {
        "backfill_used": validator.get("backfill_used"),
        "complete_1h_row_count": validator.get("complete_1h_row_count"),
        "coverage_gap_symbol_count": final_coverage.get("coverage_gap_symbol_count"),
        "delisted_historical_symbols_not_proven": final_coverage.get("delisted_historical_symbols_not_proven"),
        "excluded_gap_symbol_count": validator.get("excluded_gap_symbol_count"),
        "forward_fill_used": validator.get("forward_fill_used"),
        "gap_symbol_in_output_count": validator.get("gap_symbol_in_output_count"),
        "incomplete_1h_row_count": validator.get("incomplete_1h_row_count"),
        "max_available_end_date": final_coverage.get("max_available_end_date"),
        "max_available_start_candidate": final_coverage.get("max_available_start_candidate"),
        "near_3y_complete_symbol_count": final_coverage.get("near_3y_complete_symbol_count"),
        "no_complete_hour_source_row_count_lt_60": validator.get("no_complete_hour_source_row_count_lt_60"),
        "no_incomplete_hour_marked_complete": validator.get("no_incomplete_hour_marked_complete"),
        "numeric_sanity_validated": validator.get("numeric_sanity_validated"),
        "output_1h_row_count": validator.get("output_1h_row_count"),
        "output_duplicate_symbol_hour_count": validator.get("output_duplicate_symbol_hour_count"),
        "output_file_exists": output_file_exists,
        "output_hours_monotonic_by_symbol": validator.get("output_hours_monotonic_by_symbol"),
        "output_manifest_exists": output_manifest_exists,
        "output_schema_validated": validator.get("output_schema_validated"),
        "output_symbol_count": validator.get("output_symbol_count"),
        "output_unique_symbol_hour_count": validator.get("output_unique_symbol_hour_count"),
        "pending_symbol_count": final_coverage.get("cumulative_pending_symbol_count"),
        "per_symbol_output_row_count_valid": validator.get("per_symbol_output_row_count_valid"),
        "policy_row_count_reconciliation_pass": validator.get("policy_row_count_reconciliation_pass"),
        "provenance_validated": validator.get("provenance_validated"),
        "selected_symbol_count": validator.get("selected_symbol_count"),
        "strict_3y_completeness_claimed": final_coverage.get("strict_3y_completeness_claimed"),
        "survivorship_bias_limitations_recorded": final_coverage.get("survivorship_bias_limitations_recorded"),
        "synthetic_fill_used": validator.get("synthetic_fill_used"),
        "total_candidate_symbol_count": final_coverage.get("total_candidate_symbol_count"),
    }

    checks = {
        "artifacts_exist": all(artifacts_exist.values()),
        "build_execution_confirmed": build_execution_confirmed,
        "build_preview_confirmed": build_preview_confirmed,
        "build_validator_confirmed": build_validator_confirmed,
        "coverage_final_summary_confirmed": coverage_final_summary_confirmed,
        "coverage_source_counts": (
            fields["total_candidate_symbol_count"] == 303
            and fields["near_3y_complete_symbol_count"] == 88
            and fields["coverage_gap_symbol_count"] == 215
            and fields["pending_symbol_count"] == 0
            and fields["selected_symbol_count"] == 88
            and fields["excluded_gap_symbol_count"] == 215
            and symbol_sets["complete_symbol_count"] == 88
            and symbol_sets["gap_symbol_count"] == 215
            and symbol_sets["complete_gap_overlap_count"] == 0
            and symbol_sets["complete_gap_total_unique_count"] == 303
            and symbol_sets["complete_gap_sets_locked"] is True
        ),
        "head_matches_expected": head == EXPECTED_HEAD,
        "limitations_recorded": (
            fields["strict_3y_completeness_claimed"] is False
            and fields["max_available_start_candidate"] == "2023-07-01"
            and fields["max_available_end_date"] == "2026-05-18"
            and fields["survivorship_bias_limitations_recorded"] is True
            and fields["delisted_historical_symbols_not_proven"] is True
            and limitations.get("strict_3y_completeness_claimed") is False
        ),
        "no_forbidden_gate_actions": True,
        "no_strategy_or_edge_now": True,
        "output_counts": (
            fields["output_file_exists"] is True
            and fields["output_manifest_exists"] is True
            and fields["output_symbol_count"] == 88
            and fields["gap_symbol_in_output_count"] == 0
            and fields["output_1h_row_count"] == 2223936
            and fields["output_unique_symbol_hour_count"] == 2223936
            and fields["output_duplicate_symbol_hour_count"] == 0
            and fields["per_symbol_output_row_count_valid"] is True
            and fields["output_hours_monotonic_by_symbol"] is True
            and fields["complete_1h_row_count"] == 2223843
            and fields["incomplete_1h_row_count"] == 93
            and validator.get("complete_plus_incomplete_equals_total") is True
        ),
        "pipeline_summary_confirmed": pipeline_summary_confirmed,
        "policy_checks": (
            validator.get("exact_duplicate_rows_dropped") == 28497
            and validator.get("material_conflict_rows_quarantined") == 168
            and fields["policy_row_count_reconciliation_pass"] is True
            and fields["synthetic_fill_used"] is False
            and fields["forward_fill_used"] is False
            and fields["backfill_used"] is False
            and validator.get("all_hours_complete") is False
            and fields["no_incomplete_hour_marked_complete"] is True
            and fields["no_complete_hour_source_row_count_lt_60"] is True
            and policy.get("incomplete_1h_row_count") == 93
        ),
        "repo_clean": repo_clean,
        "schema_numeric_provenance": (
            fields["output_schema_validated"] is True
            and fields["numeric_sanity_validated"] is True
            and fields["provenance_validated"] is True
            and validator.get("invalid_numeric_row_count") == 0
            and validator.get("negative_volume_row_count") == 0
            and validator.get("nan_inf_row_count") == 0
        ),
    }

    replacement_checks_all_true = all(checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    summary = {
        **fields,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": validator.get("active_p1_attention_count", 0),
        "aggregation_performed_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_read_only_research_backtest_preview_next": replacement_checks_all_true,
        "approval_grants_research_backtest_execution_now": False,
        "approval_grants_research_readiness_gate_now": True,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "binance_5y_second_source_future_work_recorded": True,
        "build_execution_confirmed": build_execution_confirmed,
        "build_preview_confirmed": build_preview_confirmed,
        "build_validator_confirmed": build_validator_confirmed,
        "candidate_generation_allowed_now": False,
        "coverage_final_summary_confirmed": coverage_final_summary_confirmed,
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_readiness_gate": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "full_csv_read_performed": False,
        "next_module": next_module,
        "okx_88_symbol_near_3y_1h_panel_research_readiness_gate_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "okx_only_exchange_scope_recorded": True,
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": replacement_checks_all_true,
        "pipeline_summary_confirmed": pipeline_summary_confirmed,
        "read_only_research_approval_record_created": replacement_checks_all_true,
        "read_only_research_panel_ready": replacement_checks_all_true,
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "research_backtest_allowed_next": replacement_checks_all_true,
        "research_backtest_allowed_now": False,
        "research_readiness_gate_performed": True,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
    }

    checklist = {
        "artifact_type": "readiness_checklist",
        "checks": checks,
        "complete_gap_symbol_sets": symbol_sets,
        "ready": replacement_checks_all_true,
    }
    limitations_for_research = {
        "artifact_type": "limitations_for_research",
        "binance_5y_second_source_future_work_recorded": True,
        "coverage_gap_symbol_count": fields["coverage_gap_symbol_count"],
        "delisted_historical_symbols_not_proven": fields["delisted_historical_symbols_not_proven"],
        "excluded_gap_symbol_count": fields["excluded_gap_symbol_count"],
        "max_available_end_date": fields["max_available_end_date"],
        "max_available_start_candidate": fields["max_available_start_candidate"],
        "near_3y_not_exact_3y_recorded": True,
        "okx_only_exchange_scope_recorded": True,
        "strict_3y_completeness_claimed": False,
        "survivorship_bias_limitations_recorded": fields["survivorship_bias_limitations_recorded"],
    }
    research_use_policy = {
        "artifact_type": "research_use_policy",
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": replacement_checks_all_true,
        "read_only_research_panel_ready": replacement_checks_all_true,
        "research_backtest_allowed_next": replacement_checks_all_true,
        "research_backtest_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
    }
    approval = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_read_only_research_backtest_preview_next": replacement_checks_all_true,
        "approval_grants_research_backtest_execution_now": False,
        "approval_grants_research_readiness_gate_now": True,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "artifact_type": "read_only_research_approval_record",
        "next_module": next_module,
        "read_only_research_panel_ready": replacement_checks_all_true,
        "status": status,
    }
    self_validator = {
        "artifact_type": "research_readiness_gate_self_validator",
        "created_at_utc": now_utc(),
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
    }

    return {
        "approval": approval,
        "checklist": checklist,
        "limitations_for_research": limitations_for_research,
        "research_use_policy": research_use_policy,
        "self_validator": self_validator,
        "summary": summary,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_readiness_gate.json", outputs["summary"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_readiness_checklist.json", outputs["checklist"])
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_limitations_for_research.json",
        outputs["limitations_for_research"],
    )
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_use_policy.json", outputs["research_use_policy"])
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_read_only_research_approval_record.json",
        outputs["approval"],
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_self_validator.json",
        outputs["self_validator"],
    )


def main() -> int:
    outputs = build_gate()
    write_outputs(outputs)
    print(json.dumps(outputs["summary"], indent=2, sort_keys=True))
    return 0 if outputs["summary"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
