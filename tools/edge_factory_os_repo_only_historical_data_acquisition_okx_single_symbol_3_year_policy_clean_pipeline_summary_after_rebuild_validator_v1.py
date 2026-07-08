from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODULE_NAME = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_pipeline_summary_after_rebuild_validator_v1"
)
REQUESTED_MODULE = f"{MODULE_NAME}.py"
EXPECTED_HEAD = "260583f"
TARGET_SYMBOL = "BTC-USDT-SWAP"
MAX_AVAILABLE_START = "2023-07-01"
MAX_AVAILABLE_END = "2026-05-18"
EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY = 1_516_319
EXPECTED_OUTPUT_ROWS = 25_272
EXPECTED_COMPLETE_ROWS = 25_271
EXPECTED_INCOMPLETE_ROWS = 1
EXPECTED_AFFECTED_HOUR = "2026-04-14T07:00:00+00:00"
EXPECTED_EXACT_DUPLICATES_DROPPED = 320
EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED = 2
EXPECTED_DORMANT_REPO_ATTENTION_COUNT = 716

PREVIOUS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_REBUILD_"
    "EXECUTION_VALIDATED_PIPELINE_SUMMARY_READY"
)
PASS_STATUS = (
    "PASS_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_"
    "PIPELINE_SUMMARY_CLOSED_MULTI_SYMBOL_EXPANSION_PREVIEW_READY"
)
BLOCKED_STATUS = (
    "BLOCKED_HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_"
    "PIPELINE_SUMMARY"
)
AFTER_QUALITY = (
    "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_"
    "PIPELINE_CLOSED_MULTI_SYMBOL_EXPANSION_PREVIEW_READY"
)
RECOMMENDED_NEXT_ROUTE = "OKX_USDT_SWAP_SYMBOL_UNIVERSE_AND_MULTI_SYMBOL_EXPANSION_PREVIEW"
NEXT_MODULE_PASS = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_symbol_universe_and_"
    "multi_symbol_expansion_preview_after_single_symbol_3_year_summary_v1.py"
)
NEXT_MODULE_BLOCKED = (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_3_year_"
    "policy_clean_pipeline_summary_blocked_record_v1.py"
)

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_LAB_ROOT = REPO_ROOT.parent
APPROVED_TOOL = REPO_ROOT / "tools" / REQUESTED_MODULE
OUTPUT_DIR = EDGE_LAB_ROOT / MODULE_NAME
VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_validator_after_execution_v1"
)
BUILD_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_policy_clean_rebuild_execution_after_material_conflict_policy_v1"
)
POLICY_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_material_duplicate_conflict_policy_after_conflict_review_v1"
)
DOWNLOAD_VALIDATOR_DIR = EDGE_LAB_ROOT / (
    "edge_factory_os_repo_only_historical_data_acquisition_okx_single_symbol_"
    "3_year_download_execution_validator_after_execution_v1"
)

VALIDATOR_SUMMARY = VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_summary.json"
VALIDATOR_REPORT = VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator.json"
OUTPUT_VALIDATION_REPORT = VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_output_validation_report.json"
NUMERIC_SANITY_REPORT = VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_numeric_sanity_report.json"
QUARANTINE_VALIDATION_REPORT = VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_quarantine_validation_report.json"
PROVENANCE_VALIDATION_REPORT = VALIDATOR_DIR / "historical_okx_single_symbol_3_year_policy_clean_provenance_validation_report.json"
BUILD_SUMMARY = BUILD_DIR / "historical_okx_single_symbol_3_year_policy_clean_build_execution_summary.json"
BUILD_COMPLIANCE = BUILD_DIR / "historical_okx_single_symbol_3_year_policy_clean_build_execution_compliance_report.json"
POLICY_SUMMARY = POLICY_DIR / "historical_okx_single_symbol_3_year_material_conflict_policy_summary.json"
REBUILD_APPROVAL = POLICY_DIR / "historical_okx_single_symbol_3_year_policy_clean_rebuild_approval_record.json"
DOWNLOAD_VALIDATOR_SUMMARY = DOWNLOAD_VALIDATOR_DIR / "historical_okx_single_symbol_3_year_download_execution_validator_summary.json"

JSON_INPUTS = {
    "validator_summary": VALIDATOR_SUMMARY,
    "validator_report": VALIDATOR_REPORT,
    "output_validation_report": OUTPUT_VALIDATION_REPORT,
    "numeric_sanity_report": NUMERIC_SANITY_REPORT,
    "quarantine_validation_report": QUARANTINE_VALIDATION_REPORT,
    "provenance_validation_report": PROVENANCE_VALIDATION_REPORT,
    "build_summary": BUILD_SUMMARY,
    "build_compliance": BUILD_COMPLIANCE,
    "policy_summary": POLICY_SUMMARY,
    "rebuild_approval": REBUILD_APPROVAL,
    "download_validator_summary": DOWNLOAD_VALIDATOR_SUMMARY,
}

DANGEROUS_FLAGS = {
    "data_download_performed": False,
    "data_build_performed": False,
    "aggregation_performed_now": False,
    "okx_api_call_performed": False,
    "okx_browse_performed": False,
    "url_fetch_performed": False,
    "csv_read_performed": False,
    "zip_read_performed": False,
    "parquet_read_performed": False,
    "strategy_research_performed": False,
    "backtest_performed": False,
    "candidate_generation_performed": False,
    "edge_profit_claim_made": False,
    "runtime_touched": False,
    "capital_changed": False,
    "live_or_real_orders": False,
    "schema_or_config_created": False,
    "generic_runner_approval_granted": False,
}

P1_ATTENTION_ITEMS = [
    "strict_3y_completeness_from_2023_05_19_not_claimed",
    "max_available_coverage_starts_2023_07_01",
    "one_hour_incomplete_by_material_conflict_quarantine",
    "no_synthetic_forward_or_backfill",
    "policy_clean_pipeline_validation_only",
    "not_research_backtest_ready",
    "not_edge_claim_ready",
    "broad_acquisition_not_ready",
    "source_manifest_not_acquisition_ready",
    "multi_symbol_universe_unresolved",
    "symbol_universe_preview_required_next",
    "full_285_symbol_execution_blocked_until_preview",
]


class SummaryBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        raise SummaryBlocked(message)


def load_json(path: Path, label: str, exists: dict[str, bool], valid: dict[str, bool]) -> dict[str, Any]:
    exists[label] = path.exists()
    require(path.exists(), f"missing JSON artifact {label}: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        valid[label] = False
        raise SummaryBlocked(f"invalid JSON artifact {label}: {exc}") from exc
    valid[label] = True
    require(isinstance(data, dict), f"JSON artifact {label} is not an object")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_preconditions() -> dict[str, Any]:
    head = run_git(["rev-parse", "HEAD"])
    require(head.startswith(EXPECTED_HEAD), f"HEAD mismatch: expected {EXPECTED_HEAD}, observed {head}")
    require(repo_has_only_this_tool_change(), "repo dirty outside approved module")
    require(Path(__file__).resolve() == APPROVED_TOOL.resolve(), "running unexpected module path")
    return {
        "head": head,
        "expected_head": EXPECTED_HEAD,
        "repo_clean_or_only_this_tool": True,
        "tracked_python_count": tracked_python_count(),
    }


def validate_evidence() -> tuple[dict[str, dict[str, Any]], dict[str, bool], dict[str, bool]]:
    exists: dict[str, bool] = {}
    valid: dict[str, bool] = {}
    loaded = {label: load_json(path, label, exists, valid) for label, path in JSON_INPUTS.items()}

    summary = loaded["validator_summary"]
    validator_report = loaded["validator_report"]
    output_report = loaded["output_validation_report"]
    numeric_report = loaded["numeric_sanity_report"]
    quarantine_report = loaded["quarantine_validation_report"]
    provenance_report = loaded["provenance_validation_report"]
    build_summary = loaded["build_summary"]
    build_compliance = loaded["build_compliance"]
    policy_summary = loaded["policy_summary"]
    rebuild_approval = loaded["rebuild_approval"]

    require(
        summary.get(
            "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_status"
        )
        == PREVIOUS_STATUS,
        "previous validator status mismatch",
    )
    require(summary.get("next_module") == REQUESTED_MODULE, "current next_module mismatch")
    require(summary.get("policy_clean_rebuild_execution_validated") is True, "validator did not validate rebuild")
    require(summary.get("target_symbol") == TARGET_SYMBOL, "target symbol mismatch")
    require(summary.get("max_available_start_candidate") == MAX_AVAILABLE_START, "max available start mismatch")
    require(summary.get("max_available_end_date") == MAX_AVAILABLE_END, "max available end mismatch")
    require(summary.get("strict_3y_completeness_claimed") is False, "strict 3y completeness claim detected")
    require(summary.get("clean_source_row_count_after_policy") == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY, "clean source rows mismatch")
    require(summary.get("output_csv_row_count") == EXPECTED_OUTPUT_ROWS, "output CSV row count mismatch")
    require(summary.get("output_symbol_count") == 1, "output symbol count mismatch")
    require(summary.get("output_observed_symbol") == TARGET_SYMBOL, "observed symbol mismatch")
    require(summary.get("output_unique_hour_count") == EXPECTED_OUTPUT_ROWS, "unique hour count mismatch")
    require(summary.get("output_duplicate_hour_count") == 0, "duplicate hour count nonzero")
    require(summary.get("output_hours_monotonic") is True, "hours not monotonic")
    require(summary.get("complete_1h_row_count") == EXPECTED_COMPLETE_ROWS, "complete hour count mismatch")
    require(summary.get("incomplete_1h_row_count") == EXPECTED_INCOMPLETE_ROWS, "incomplete hour count mismatch")
    require(summary.get("all_hours_complete") is False, "all hours complete claim detected")
    require(summary.get("affected_hour_utc") == EXPECTED_AFFECTED_HOUR, "affected hour mismatch")
    require(summary.get("affected_hour_marked_complete") is False, "affected hour marked complete")
    require(summary.get("quarantine_applied_to_affected_hour") is True, "affected hour quarantine flag missing")
    require(summary.get("exact_duplicate_rows_dropped") == EXPECTED_EXACT_DUPLICATES_DROPPED, "exact duplicate count mismatch")
    require(
        summary.get("material_conflict_rows_quarantined") == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "material conflict quarantine count mismatch",
    )
    require(summary.get("synthetic_fill_used") is False, "synthetic fill used")
    require(summary.get("forward_fill_used") is False, "forward fill used")
    require(summary.get("backfill_used") is False, "backfill used")
    require(summary.get("numeric_sanity_validated") is True, "numeric sanity not validated")
    require(summary.get("provenance_validated") is True, "provenance not validated")
    require(summary.get("output_is_policy_clean_pipeline_validation_only") is True, "pipeline-only output flag missing")
    require(summary.get("output_valid_for_research_backtest") is False, "research/backtest readiness claim detected")
    require(summary.get("output_valid_for_edge_claim") is False, "edge claim detected")
    require(summary.get("broad_acquisition_ready") is False, "broad acquisition ready claim detected")
    require(summary.get("source_manifest_acquisition_ready") is False, "source manifest acquisition ready claim detected")
    require(summary.get("validator_p0_count") == 0, "validator P0 count nonzero")
    require(int(summary.get("validator_p1_count", 0)) >= 10, "validator P1 count too low")
    require(summary.get("replacement_checks_all_true") is True, "validator replacement checks did not pass")

    require(validator_report.get("no_new_download_api_browse_build_aggregation_by_validator") is True, "validator safety flag mismatch")
    require(output_report.get("output_csv_row_count") == EXPECTED_OUTPUT_ROWS, "output validation report row count mismatch")
    require(numeric_report.get("numeric_sanity_validated") is True, "numeric report not validated")
    require(quarantine_report.get("approved_material_conflict_policy_validated") is True, "quarantine policy not validated")
    require(quarantine_report.get("synthetic_fill_used") is False, "quarantine report synthetic fill used")
    require(quarantine_report.get("forward_fill_used") is False, "quarantine report forward fill used")
    require(quarantine_report.get("backfill_used") is False, "quarantine report backfill used")
    require(provenance_report.get("provenance_validated") is True, "provenance report not validated")
    require(provenance_report.get("clean_source_row_count_after_policy") == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY, "provenance clean row count mismatch")

    require(build_summary.get("data_build_performed") is True, "historical build summary missing prior build flag")
    require(build_summary.get("aggregation_performed_now") is True, "historical build summary missing prior aggregation flag")
    require(build_summary.get("output_valid_for_research_backtest") is False, "build summary research/backtest claim detected")
    require(build_summary.get("output_valid_for_edge_claim") is False, "build summary edge claim detected")
    require(build_summary.get("broad_acquisition_ready") is False, "build summary broad readiness claim detected")
    require(build_summary.get("source_manifest_acquisition_ready") is False, "build summary source manifest readiness claim detected")
    require(build_compliance.get("no_new_download") is True, "build compliance download mismatch")
    require(build_compliance.get("output_is_policy_clean_pipeline_validation_only") is True, "build compliance pipeline-only mismatch")
    require(policy_summary.get("strict_3y_completeness_claimed") is False, "policy summary strict 3y claim detected")
    require(rebuild_approval.get("approval_grants_research_backtest_edge_now") is False, "approval grants research/backtest/edge")

    return loaded, exists, valid


def build_outputs(
    preconditions: dict[str, Any],
    loaded: dict[str, dict[str, Any]],
    exists: dict[str, bool],
    valid: dict[str, bool],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    validator_summary = loaded["validator_summary"]

    pipeline_summary = {
        "single_symbol_3_year_policy_clean_pipeline_summary_created": True,
        "single_symbol_3_year_policy_clean_pipeline_closed_successfully": True,
        "target_symbol": TARGET_SYMBOL,
        "coverage_mode": "MAX_AVAILABLE_POLICY_CLEAN_SINGLE_SYMBOL_1M_TO_1H",
        "max_available_start_candidate": MAX_AVAILABLE_START,
        "max_available_end_date": MAX_AVAILABLE_END,
        "strict_3y_start_not_covered": "2023-05-19",
        "strict_3y_completeness_claimed": False,
        "clean_source_row_count_after_policy": EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "output_1h_row_count": EXPECTED_OUTPUT_ROWS,
        "complete_1h_row_count": EXPECTED_COMPLETE_ROWS,
        "incomplete_1h_row_count": EXPECTED_INCOMPLETE_ROWS,
        "all_hours_complete": False,
        "affected_hour_utc": EXPECTED_AFFECTED_HOUR,
        "affected_hour_marked_complete": False,
        "quarantine_applied_to_affected_hour": True,
        "exact_duplicate_rows_dropped": EXPECTED_EXACT_DUPLICATES_DROPPED,
        "material_conflict_rows_quarantined": EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_valid_for_pipeline_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "multi_symbol_universe_resolved": False,
        "multi_symbol_acquisition_ready": False,
        "research_backtest_edge_remains_blocked": True,
    }

    closure_record = {
        "pipeline_closure_record_created": True,
        "single_symbol_pipeline_validated_for": TARGET_SYMBOL,
        "single_symbol_long_range_data_acquisition_build_pipeline_validated": True,
        "pipeline_closed_successfully": True,
        "closed_at_utc": utc_now(),
        "validator_summary_source": str(VALIDATOR_SUMMARY),
        "output_valid_for_pipeline_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "next_step_must_remain_repo_only_preview": True,
    }

    limitations_report = {
        "limitations_report_created": True,
        "strict_3y_completeness_claimed": False,
        "strict_3y_missing_start_note": "No completeness claim is made for 2023-05-19 through 2023-06-30.",
        "max_available_coverage": f"{MAX_AVAILABLE_START} through {MAX_AVAILABLE_END}",
        "all_hours_complete": False,
        "known_incomplete_hour": EXPECTED_AFFECTED_HOUR,
        "incomplete_hour_reason": "MATERIAL_DUPLICATE_CONFLICT_QUARANTINE",
        "synthetic_fill_used": False,
        "forward_fill_used": False,
        "backfill_used": False,
        "output_valid_for_pipeline_validation": True,
        "output_valid_for_research_backtest": False,
        "output_valid_for_edge_claim": False,
        "broad_acquisition_ready": False,
        "source_manifest_acquisition_ready": False,
        "multi_symbol_universe_resolved": False,
        "full_285_symbol_acquisition_execution_allowed": False,
        "strategy_backtest_route_allowed": False,
    }

    next_route_decision = {
        "next_expansion_route_decision_created": True,
        "recommended_next_route": RECOMMENDED_NEXT_ROUTE,
        "next_module": NEXT_MODULE_PASS,
        "do_not_route_to_strategy_backtest_yet": True,
        "do_not_route_directly_to_full_285_symbol_acquisition_execution": True,
        "next_safe_route_is_symbol_universe_multi_symbol_expansion_preview": True,
        "reason": [
            "Single-symbol data pipeline is validated.",
            "The next real blocker is symbol universe / survivorship-safe multi-symbol scope.",
            "A repo-only preview must decide symbol universe resolution, small pilot set, resource limits, and continued research/backtest/edge block.",
        ],
        "preview_decisions_required": [
            "resolve_okx_usdt_swap_symbol_universe",
            "choose_small_fixed_multi_symbol_pilot_set",
            "define_reuse_download_build_resource_limits",
            "keep_research_backtest_edge_blocked",
        ],
    }

    replacement_checks = {
        "expected_head": preconditions["head"].startswith(EXPECTED_HEAD),
        "repo_clean_or_only_this_tool": preconditions["repo_clean_or_only_this_tool"],
        "json_inputs_exist": all(exists.values()),
        "json_inputs_valid": all(valid.values()),
        "previous_status_pass": validator_summary.get(
            "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_rebuild_execution_validator_status"
        )
        == PREVIOUS_STATUS,
        "current_next_module_matches": validator_summary.get("next_module") == REQUESTED_MODULE,
        "target_symbol_expected": pipeline_summary["target_symbol"] == TARGET_SYMBOL,
        "max_available_coverage_expected": pipeline_summary["max_available_start_candidate"] == MAX_AVAILABLE_START
        and pipeline_summary["max_available_end_date"] == MAX_AVAILABLE_END,
        "strict_3y_not_claimed": pipeline_summary["strict_3y_completeness_claimed"] is False,
        "clean_source_rows_expected": pipeline_summary["clean_source_row_count_after_policy"]
        == EXPECTED_CLEAN_SOURCE_ROWS_AFTER_POLICY,
        "output_rows_expected": pipeline_summary["output_1h_row_count"] == EXPECTED_OUTPUT_ROWS,
        "complete_rows_expected": pipeline_summary["complete_1h_row_count"] == EXPECTED_COMPLETE_ROWS,
        "incomplete_rows_expected": pipeline_summary["incomplete_1h_row_count"] == EXPECTED_INCOMPLETE_ROWS,
        "affected_hour_quarantined": pipeline_summary["quarantine_applied_to_affected_hour"] is True,
        "duplicate_and_conflict_counts_expected": pipeline_summary["exact_duplicate_rows_dropped"]
        == EXPECTED_EXACT_DUPLICATES_DROPPED
        and pipeline_summary["material_conflict_rows_quarantined"]
        == EXPECTED_MATERIAL_CONFLICT_ROWS_QUARANTINED,
        "no_fill_used": pipeline_summary["synthetic_fill_used"] is False
        and pipeline_summary["forward_fill_used"] is False
        and pipeline_summary["backfill_used"] is False,
        "pipeline_validation_only": pipeline_summary["output_valid_for_pipeline_validation"] is True,
        "research_backtest_edge_blocked": pipeline_summary["output_valid_for_research_backtest"] is False
        and pipeline_summary["output_valid_for_edge_claim"] is False,
        "broad_acquisition_blocked": pipeline_summary["broad_acquisition_ready"] is False
        and pipeline_summary["source_manifest_acquisition_ready"] is False,
        "next_route_decision_created": next_route_decision["next_expansion_route_decision_created"] is True,
        "recommended_route_expected": next_route_decision["recommended_next_route"] == RECOMMENDED_NEXT_ROUTE,
        "next_module_expected": next_route_decision["next_module"] == NEXT_MODULE_PASS,
        "dangerous_flags_all_false": all(value is False for value in DANGEROUS_FLAGS.values()),
    }
    replacement_checks_all_true = all(replacement_checks.values())
    require(replacement_checks_all_true, "replacement checks did not all pass")

    self_validator = {
        "self_validator_created": True,
        "single_symbol_3_year_policy_clean_pipeline_summary_created": True,
        "single_symbol_3_year_policy_clean_pipeline_closed_successfully": True,
        "next_expansion_route_decision_created": True,
        "no_download_api_browse": True,
        "no_csv_zip_parquet_read": True,
        "no_data_build": True,
        "no_aggregation": True,
        "no_research_backtest_edge_claim": True,
        "no_broad_acquisition_ready_claim": True,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    bundle_summary = {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "head": preconditions["head"],
        "tracked_python_count_at_summary_run": preconditions["tracked_python_count"],
        "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_pipeline_summary_status": PASS_STATUS,
        **pipeline_summary,
        "next_expansion_route_decision_created": True,
        "recommended_next_route": RECOMMENDED_NEXT_ROUTE,
        **DANGEROUS_FLAGS,
        "active_p0_blocker_count": 0,
        "active_p1_attention_count": len(P1_ATTENTION_ITEMS),
        "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "p1_attention_items": P1_ATTENTION_ITEMS,
        "current_evidence_chain_quality_after_summary": AFTER_QUALITY,
        "next_module": NEXT_MODULE_PASS,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }

    return pipeline_summary, closure_record, limitations_report, next_route_decision, self_validator, bundle_summary


def write_outputs(
    pipeline_summary: dict[str, Any],
    closure_record: dict[str, Any],
    limitations_report: dict[str, Any],
    next_route_decision: dict[str, Any],
    self_validator: dict[str, Any],
    bundle_summary: dict[str, Any],
) -> None:
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary.json", pipeline_summary)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_closure_record.json", closure_record)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_limitations_report.json", limitations_report)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_next_expansion_route_decision.json", next_route_decision)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary_self_validator.json", self_validator)
    write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary_bundle_summary.json", bundle_summary)


def blocked_payload(message: str) -> dict[str, Any]:
    return {
        "module_name": MODULE_NAME,
        "generated_at_utc": utc_now(),
        "historical_data_acquisition_okx_single_symbol_3_year_policy_clean_pipeline_summary_status": BLOCKED_STATUS,
        "single_symbol_3_year_policy_clean_pipeline_summary_created": False,
        "single_symbol_3_year_policy_clean_pipeline_closed_successfully": False,
        "target_symbol": TARGET_SYMBOL,
        "blocker": message,
        "active_p0_blocker_count": 1,
        "active_p1_attention_count": len(P1_ATTENTION_ITEMS),
        "dormant_repo_attention_count": EXPECTED_DORMANT_REPO_ATTENTION_COUNT,
        "generic_runner_implementation_remains_blocked": True,
        "ordinary_selector_backlog_loop_reentry_allowed": False,
        "loop_remains_closed": True,
        "current_evidence_chain_quality_after_summary": "HISTORICAL_DATA_ACQUISITION_OKX_SINGLE_SYMBOL_3_YEAR_POLICY_CLEAN_PIPELINE_SUMMARY_BLOCKED",
        "next_module": NEXT_MODULE_BLOCKED,
        "replacement_checks_all_true": False,
        **DANGEROUS_FLAGS,
    }


def main() -> None:
    try:
        preconditions = validate_preconditions()
        loaded, exists, valid = validate_evidence()
        outputs = build_outputs(preconditions, loaded, exists, valid)
        write_outputs(*outputs)
        print(json.dumps(outputs[-1], indent=2, sort_keys=True))
    except SummaryBlocked as exc:
        blocked = blocked_payload(str(exc))
        write_json(OUTPUT_DIR / "historical_okx_single_symbol_3_year_policy_clean_pipeline_summary_bundle_summary.json", blocked)
        print(json.dumps(blocked, indent=2, sort_keys=True))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
