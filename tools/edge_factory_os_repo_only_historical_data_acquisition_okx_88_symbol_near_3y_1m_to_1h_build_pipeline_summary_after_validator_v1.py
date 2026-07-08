#!/usr/bin/env python3
"""Pipeline summary after the validated OKX 88-symbol 1m-to-1h build.

This is a closure/summary module only. It reads prior JSON/CSV manifest
artifacts, writes summary artifacts, and keeps research/backtest/edge blocked.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1"
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

FINAL_COVERAGE_SUMMARY = FINAL_SUMMARY_DIR / "repo_only_okx_full_usdt_swap_coverage_discovery_final_summary.json"
BUILD_PREVIEW = BUILD_PREVIEW_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_preview.json"
BUILD_EXECUTION_SUMMARY = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_summary.json"
BUILD_EXECUTION_MANIFEST = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_manifest.json"
PER_SYMBOL_COUNTS = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_per_symbol_counts.csv"
POLICY_EFFECTS = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_policy_effects_report.json"
SCHEMA_REPORT = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_output_schema_report.json"
PROVENANCE = BUILD_EXECUTION_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_provenance_manifest.json"
VALIDATOR_SUMMARY = VALIDATOR_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_summary.json"

EXPECTED_HEAD = "bc5a807"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PIPELINE_SUMMARY_CREATED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_PIPELINE_SUMMARY_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_after_pipeline_summary_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_NEAR_3Y_1H_PANEL_VALIDATED_PIPELINE_SUMMARY_READY_RESEARCH_READINESS_GATE_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_NEAR_3Y_1H_PANEL_PIPELINE_SUMMARY_BLOCKED_REVIEW_REQUIRED"


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


def per_symbol_counts_summary() -> dict[str, Any]:
    symbol_count = 0
    total_output_rows = 0
    min_output_rows = None
    max_output_rows = None
    with PER_SYMBOL_COUNTS.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            symbol_count += 1
            output_rows = int(row["output_1h_row_count"])
            total_output_rows += output_rows
            min_output_rows = output_rows if min_output_rows is None else min(min_output_rows, output_rows)
            max_output_rows = output_rows if max_output_rows is None else max(max_output_rows, output_rows)
    return {
        "per_symbol_counts_file_read": True,
        "per_symbol_counts_symbol_count": symbol_count,
        "per_symbol_counts_total_output_rows": total_output_rows,
        "per_symbol_output_row_count_min": min_output_rows,
        "per_symbol_output_row_count_max": max_output_rows,
    }


def build_summary() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    required_paths = [
        FINAL_COVERAGE_SUMMARY,
        BUILD_PREVIEW,
        BUILD_EXECUTION_SUMMARY,
        BUILD_EXECUTION_MANIFEST,
        PER_SYMBOL_COUNTS,
        POLICY_EFFECTS,
        SCHEMA_REPORT,
        PROVENANCE,
        VALIDATOR_SUMMARY,
    ]
    artifacts_exist = {path.name: path.exists() for path in required_paths}
    final_coverage = read_json(FINAL_COVERAGE_SUMMARY)
    preview = read_json(BUILD_PREVIEW)
    execution = read_json(BUILD_EXECUTION_SUMMARY)
    manifest = read_json(BUILD_EXECUTION_MANIFEST)
    policy = read_json(POLICY_EFFECTS)
    schema = read_json(SCHEMA_REPORT)
    provenance = read_json(PROVENANCE)
    validator = read_json(VALIDATOR_SUMMARY)
    per_symbol_summary = per_symbol_counts_summary()
    output_file = Path(manifest.get("output_file", execution.get("output_file", "")))

    validator_confirmed = (
        validator.get("okx_88_symbol_near_3y_1m_to_1h_build_execution_validator_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_EXECUTION_VALIDATED"
        and validator.get("build_execution_validated") is True
        and validator.get("replacement_checks_all_true") is True
        and validator.get("final_decision") == "OKX_88_SYMBOL_NEAR_3Y_1M_TO_1H_BUILD_VALIDATED_PIPELINE_SUMMARY_READY"
    )
    output_file_exists = output_file.exists()
    output_manifest_exists = BUILD_EXECUTION_MANIFEST.exists()

    summary_fields = {
        "all_hours_complete": validator.get("all_hours_complete"),
        "backfill_used": validator.get("backfill_used"),
        "broad_acquisition_ready": False,
        "clean_source_rows_after_policy": validator.get("clean_source_rows_after_policy"),
        "complete_1h_row_count": validator.get("complete_1h_row_count"),
        "coverage_gap_symbol_count": final_coverage.get("coverage_gap_symbol_count"),
        "delisted_historical_symbols_not_proven": final_coverage.get("delisted_historical_symbols_not_proven"),
        "excluded_gap_symbol_count": validator.get("excluded_gap_symbol_count"),
        "expected_total_output_rows_1h": validator.get("expected_total_output_rows_1h"),
        "expected_total_source_file_count": validator.get("expected_total_source_file_count"),
        "expected_total_source_rows": validator.get("expected_total_source_rows"),
        "exact_duplicate_rows_dropped": validator.get("exact_duplicate_rows_dropped"),
        "forward_fill_used": validator.get("forward_fill_used"),
        "gap_symbol_in_output_count": validator.get("gap_symbol_in_output_count"),
        "incomplete_1h_row_count": validator.get("incomplete_1h_row_count"),
        "invalid_numeric_row_count": validator.get("invalid_numeric_row_count"),
        "locked_complete_symbols_all_in_output": validator.get("locked_complete_symbols_all_in_output"),
        "material_conflict_rows_quarantined": validator.get("material_conflict_rows_quarantined"),
        "max_available_end_date": final_coverage.get("max_available_end_date"),
        "max_available_start_candidate": final_coverage.get("max_available_start_candidate"),
        "nan_inf_row_count": validator.get("nan_inf_row_count"),
        "near_3y_complete_symbol_count": final_coverage.get("near_3y_complete_symbol_count"),
        "negative_volume_row_count": validator.get("negative_volume_row_count"),
        "numeric_sanity_validated": validator.get("numeric_sanity_validated"),
        "output_1h_row_count": validator.get("output_1h_row_count"),
        "output_duplicate_symbol_hour_count": validator.get("output_duplicate_symbol_hour_count"),
        "output_file_exists": output_file_exists,
        "output_hours_monotonic_by_symbol": validator.get("output_hours_monotonic_by_symbol"),
        "output_is_pipeline_validation_only": validator.get("output_is_pipeline_validation_only"),
        "output_manifest_exists": output_manifest_exists,
        "output_schema_validated": validator.get("output_schema_validated"),
        "output_symbol_count": validator.get("output_symbol_count"),
        "output_unique_symbol_hour_count": validator.get("output_unique_symbol_hour_count"),
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": False,
        "pending_symbol_count": final_coverage.get("cumulative_pending_symbol_count"),
        "per_symbol_output_row_count_valid": validator.get("per_symbol_output_row_count_valid"),
        "policy_row_count_reconciliation_pass": validator.get("policy_row_count_reconciliation_pass"),
        "provenance_validated": validator.get("provenance_validated"),
        "raw_source_rows_read": validator.get("raw_source_rows_read"),
        "selected_symbol_count": validator.get("selected_symbol_count"),
        "source_file_count_processed": validator.get("source_file_count_processed"),
        "source_manifest_acquisition_ready": False,
        "strict_3y_completeness_claimed": final_coverage.get("strict_3y_completeness_claimed"),
        "survivorship_bias_limitations_recorded": final_coverage.get("survivorship_bias_limitations_recorded"),
        "synthetic_fill_used": validator.get("synthetic_fill_used"),
        "total_candidate_symbol_count": final_coverage.get("total_candidate_symbol_count"),
    }

    checks = {
        "artifacts_exist": all(artifacts_exist.values()),
        "coverage_counts": (
            summary_fields["total_candidate_symbol_count"] == 303
            and summary_fields["near_3y_complete_symbol_count"] == 88
            and summary_fields["coverage_gap_symbol_count"] == 215
            and summary_fields["pending_symbol_count"] == 0
        ),
        "execution_was_validated_not_rebuilt": (
            execution.get("data_build_performed") is True
            and execution.get("aggregation_performed_now") is True
            and validator.get("data_build_performed_by_validator") is False
            and validator.get("aggregation_performed_by_validator") is False
        ),
        "head_matches_expected": head == EXPECTED_HEAD,
        "manifest_consistent": (
            manifest.get("output_file_created") is True
            and manifest.get("output_manifest_created") is True
            and manifest.get("output_is_pipeline_validation_only") is True
            and output_file_exists
        ),
        "no_forbidden_summary_actions": True,
        "no_readiness_claims": (
            summary_fields["output_valid_for_research_backtest"] is False
            and summary_fields["output_valid_for_edge_claim"] is False
            and summary_fields["broad_acquisition_ready"] is False
            and summary_fields["source_manifest_acquisition_ready"] is False
        ),
        "per_symbol_counts_light_check": (
            per_symbol_summary["per_symbol_counts_symbol_count"] == 88
            and per_symbol_summary["per_symbol_counts_total_output_rows"] == 2223936
            and per_symbol_summary["per_symbol_output_row_count_min"] == 25272
            and per_symbol_summary["per_symbol_output_row_count_max"] == 25272
        ),
        "policy_values": (
            policy.get("exact_duplicate_rows_dropped") == 28497
            and policy.get("material_conflict_rows_quarantined") == 168
            and policy.get("synthetic_fill_used") is False
            and policy.get("forward_fill_used") is False
            and policy.get("backfill_used") is False
            and summary_fields["all_hours_complete"] is False
            and summary_fields["incomplete_1h_row_count"] == 93
        ),
        "preview_confirmed": preview.get("replacement_checks_all_true") is True,
        "provenance_schema": (
            provenance.get("provenance_entry_count") == 92664
            and schema.get("output_schema_created") is True
            and schema.get("pipeline_validation_only") is True
        ),
        "repo_clean": repo_clean,
        "validator_confirmed": validator_confirmed,
        "validator_counts": (
            summary_fields["selected_symbol_count"] == 88
            and summary_fields["excluded_gap_symbol_count"] == 215
            and summary_fields["expected_total_source_file_count"] == 92664
            and summary_fields["source_file_count_processed"] == 92664
            and summary_fields["expected_total_source_rows"] == 133436160
            and summary_fields["raw_source_rows_read"] == 133464732
            and summary_fields["exact_duplicate_rows_dropped"] == 28497
            and summary_fields["material_conflict_rows_quarantined"] == 168
            and summary_fields["clean_source_rows_after_policy"] == 133436067
            and summary_fields["policy_row_count_reconciliation_pass"] is True
            and summary_fields["expected_total_output_rows_1h"] == 2223936
            and summary_fields["output_1h_row_count"] == 2223936
            and summary_fields["output_symbol_count"] == 88
            and summary_fields["gap_symbol_in_output_count"] == 0
            and summary_fields["output_unique_symbol_hour_count"] == 2223936
            and summary_fields["output_duplicate_symbol_hour_count"] == 0
            and summary_fields["per_symbol_output_row_count_valid"] is True
            and summary_fields["output_hours_monotonic_by_symbol"] is True
            and summary_fields["complete_1h_row_count"] == 2223843
            and summary_fields["incomplete_1h_row_count"] == 93
            and summary_fields["output_schema_validated"] is True
            and summary_fields["numeric_sanity_validated"] is True
            and summary_fields["provenance_validated"] is True
        ),
    }
    replacement_checks_all_true = all(checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    summary = {
        **summary_fields,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": validator.get("active_p1_attention_count", 0),
        "aggregation_performed_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_research_readiness_gate_next": replacement_checks_all_true,
        "approval_grants_pipeline_summary_now": True,
        "approval_grants_research_backtest_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "current_evidence_chain_quality_after_pipeline_summary": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_allowed_now": False,
        "full_csv_read_performed": False,
        "next_module": next_module,
        "okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "pipeline_summary_created": replacement_checks_all_true,
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "research_backtest_allowed_now": False,
        "research_readiness_gate_approval_record_created": replacement_checks_all_true,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
        "tracked_python_count": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validator_confirmed": validator_confirmed,
        "created_at_utc": now_utc(),
    }

    validated_output = {
        "artifact_type": "validated_pipeline_output_summary",
        "output_file": str(output_file),
        "output_is_pipeline_validation_only": True,
        "output_manifest": str(BUILD_EXECUTION_MANIFEST),
        "output_schema_validated": summary["output_schema_validated"],
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": False,
        "selected_symbol_count": summary["selected_symbol_count"],
        "output_1h_row_count": summary["output_1h_row_count"],
        "complete_1h_row_count": summary["complete_1h_row_count"],
        "incomplete_1h_row_count": summary["incomplete_1h_row_count"],
        "research_readiness_gate_required_before_research_use": True,
    }
    policy_summary = {
        "exact_duplicate_rows_dropped": summary["exact_duplicate_rows_dropped"],
        "material_conflict_rows_quarantined": summary["material_conflict_rows_quarantined"],
        "clean_source_rows_after_policy": summary["clean_source_rows_after_policy"],
        "policy_row_count_reconciliation_pass": summary["policy_row_count_reconciliation_pass"],
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "all_hours_complete": False,
        "incomplete_1h_row_count": summary["incomplete_1h_row_count"],
    }
    limitations = {
        "coverage_gap_symbol_count": summary["coverage_gap_symbol_count"],
        "delisted_historical_symbols_not_proven": summary["delisted_historical_symbols_not_proven"],
        "max_available_end_date": summary["max_available_end_date"],
        "max_available_start_candidate": summary["max_available_start_candidate"],
        "near_3y_complete_symbol_count": summary["near_3y_complete_symbol_count"],
        "strict_3y_completeness_claimed": False,
        "survivorship_bias_limitations_recorded": summary["survivorship_bias_limitations_recorded"],
        "total_candidate_symbol_count": summary["total_candidate_symbol_count"],
    }
    approval = {
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_research_readiness_gate_next": replacement_checks_all_true,
        "approval_grants_pipeline_summary_now": True,
        "approval_grants_research_backtest_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "artifact_type": "research_readiness_gate_approval_record",
        "next_module": next_module,
        "pipeline_summary_status": status,
    }
    self_validator = {
        "artifact_type": "pipeline_summary_self_validator",
        "created_at_utc": now_utc(),
        "replacement_checks": checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
    }
    return {
        "approval": approval,
        "limitations": limitations,
        "policy_summary": policy_summary,
        "self_validator": self_validator,
        "summary": summary,
        "validated_output": validated_output,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary.json", outputs["summary"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_validated_pipeline_output_summary.json", outputs["validated_output"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_policy_effects_summary.json", outputs["policy_summary"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_limitations_summary.json", outputs["limitations"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1h_panel_research_readiness_gate_approval_record.json", outputs["approval"])
    write_json(OUTPUT_DIR / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_self_validator.json", outputs["self_validator"])


def main() -> int:
    outputs = build_summary()
    write_outputs(outputs)
    print(json.dumps(outputs["summary"], indent=2, sort_keys=True))
    return 0 if outputs["summary"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
