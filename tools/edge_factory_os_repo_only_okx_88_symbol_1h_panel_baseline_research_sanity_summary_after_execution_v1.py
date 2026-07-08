#!/usr/bin/env python3
"""Summarize OKX 88-symbol 1h baseline research sanity execution.

This repo-only summary reads existing baseline diagnostic artifacts only. It
does not read original 1m sources, build or aggregate data, execute research or
backtests, search strategies, generate candidates, claim edge, or touch
runtime/live/capital.
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
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_after_execution_v1.py"
)
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_after_execution_v1"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_v1"
BASELINE_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_after_preview_v1"

PREVIEW = PREVIEW_DIR / "repo_only_research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate.json"
BASELINE_REPORT = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_execution_report.json"
MONTHLY_COVERAGE = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_monthly_coverage_diagnostics.csv"
INCOMPLETE_HOURS = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_incomplete_hour_diagnostics.json"
RETURN_SANITY = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_return_distribution_sanity.json"
VOLUME_SANITY = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_volume_liquidity_sanity.json"
NULL_COST_HOLDOUT = BASELINE_DIR / "repo_only_okx_88_symbol_1h_panel_null_cost_holdout_readiness_report.json"

EXPECTED_HEAD = "df849fa"
EXPECTED_SELECTED_SYMBOL_COUNT = 88
EXPECTED_OUTPUT_SYMBOL_COUNT = 88
EXPECTED_OUTPUT_ROWS = 2223936
EXPECTED_ROWS_PER_SYMBOL = 25272
EXPECTED_COMPLETE_ROWS = 2223843
EXPECTED_INCOMPLETE_ROWS = 93
EXPECTED_FINITE_RETURN_COUNT = 2223848
EXPECTED_NAN_INF_RETURN_COUNT = 0
EXPECTED_EXTREME_RETURN_COUNT = 80

BASELINE_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_EXECUTED"
PREVIEW_PASS_STATUS = "PASS_REPO_ONLY_RESEARCH_BACKTEST_PREVIEW_AFTER_OKX_88_SYMBOL_1H_PANEL_READINESS_GATE_CREATED"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_SUMMARY_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_SUMMARY_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_extreme_return_diagnostic_review_after_baseline_summary_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_SUMMARY_READY_EXTREME_RETURN_REVIEW_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_BASELINE_RESEARCH_SANITY_SUMMARY_BLOCKED_REVIEW_REQUIRED"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return payload


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


def load_required_artifacts() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "preview": PREVIEW,
        "baseline_report": BASELINE_REPORT,
        "incomplete_hours": INCOMPLETE_HOURS,
        "return_sanity": RETURN_SANITY,
        "volume_sanity": VOLUME_SANITY,
        "null_cost_holdout": NULL_COST_HOLDOUT,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def nested_has_key(obj: Any, candidate_keys: set[str]) -> bool:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in candidate_keys:
                return True
            if nested_has_key(value, candidate_keys):
                return True
    elif isinstance(obj, list):
        return any(nested_has_key(item, candidate_keys) for item in obj)
    return False


def first_path_with_key(files: dict[Path, dict[str, Any]], candidate_keys: set[str]) -> str | None:
    for path, payload in files.items():
        if nested_has_key(payload, candidate_keys):
            return str(path)
    return None


def detail_inventory(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    json_files: dict[Path, dict[str, Any]] = {}
    label_to_path = {
        "baseline_report": BASELINE_REPORT,
        "incomplete_hours": INCOMPLETE_HOURS,
        "return_sanity": RETURN_SANITY,
        "volume_sanity": VOLUME_SANITY,
        "null_cost_holdout": NULL_COST_HOLDOUT,
    }
    for label, path in label_to_path.items():
        if label in loaded:
            json_files[path] = loaded[label]

    symbol_keys = {
        "extreme_return_by_symbol",
        "extreme_return_count_by_symbol",
        "extreme_return_counts_by_symbol",
        "extreme_return_symbol_counts",
        "extreme_return_symbol_distribution",
    }
    timestamp_keys = {
        "extreme_return_by_hour",
        "extreme_return_by_month",
        "extreme_return_by_timestamp",
        "extreme_return_count_by_hour",
        "extreme_return_count_by_month",
        "extreme_return_timestamp_counts",
        "extreme_return_timestamp_distribution",
    }
    top_row_keys = {
        "extreme_return_rows",
        "extreme_return_top_rows",
        "top_10_rows_by_absolute_return",
        "top_extreme_return_rows",
    }
    overlap_keys = {
        "extreme_return_incomplete_hour_overlap",
        "extreme_return_incomplete_hour_overlap_count",
        "incomplete_hour_extreme_return_overlap_count",
    }

    symbol_path = first_path_with_key(json_files, symbol_keys)
    timestamp_path = first_path_with_key(json_files, timestamp_keys)
    top_rows_path = first_path_with_key(json_files, top_row_keys)
    overlap_path = first_path_with_key(json_files, overlap_keys)

    symbol_distribution_available = symbol_path is not None
    timestamp_distribution_available = timestamp_path is not None
    top_rows_available = top_rows_path is not None
    incomplete_hour_overlap_available = overlap_path is not None
    sufficient = (
        symbol_distribution_available
        and timestamp_distribution_available
        and top_rows_available
        and incomplete_hour_overlap_available
    )

    detail_path = next((path for path in [top_rows_path, symbol_path, timestamp_path, overlap_path] if path), None)
    return_sanity = loaded.get("return_sanity", {})
    per_symbol_distribution = return_sanity.get("per_symbol_return_distribution", {})
    threshold = return_sanity.get("extreme_return_abs_threshold", 0.25)
    minmax_candidate_symbols: list[str] = []
    if isinstance(per_symbol_distribution, dict):
        for symbol, stats in per_symbol_distribution.items():
            if not isinstance(stats, dict):
                continue
            max_value = stats.get("max")
            min_value = stats.get("min")
            if isinstance(max_value, (int, float)) and max_value >= threshold:
                minmax_candidate_symbols.append(str(symbol))
            elif isinstance(min_value, (int, float)) and min_value <= -threshold:
                minmax_candidate_symbols.append(str(symbol))

    missing_reason = None
    if not sufficient:
        missing_reason = (
            "Existing baseline artifacts record extreme_return_diagnostic_count=80 and per-symbol return min/max "
            "statistics, but they do not provide complete row-level extreme-return records, counts by symbol, "
            "counts by month/timestamp/hour, top rows by absolute return, or incomplete-hour overlap."
        )

    return {
        "extreme_return_detail_artifact_detected": bool(detail_path),
        "extreme_return_detail_artifact_path": detail_path,
        "extreme_return_symbol_distribution_available": symbol_distribution_available,
        "extreme_return_timestamp_distribution_available": timestamp_distribution_available,
        "extreme_return_top_rows_available": top_rows_available,
        "extreme_return_incomplete_hour_overlap_available": incomplete_hour_overlap_available,
        "extreme_return_detail_sufficient_for_concentration_answer": sufficient,
        "extreme_return_detail_missing_reason": missing_reason,
        "extreme_return_unique_symbol_count": None,
        "extreme_return_top_symbol": None,
        "extreme_return_top_symbol_count": None,
        "extreme_return_top_3_symbol_count": None,
        "extreme_return_concentrated_in_top_3_symbols": None,
        "extreme_return_unique_month_count": None,
        "extreme_return_clustered_by_month": None,
        "extreme_return_incomplete_hour_overlap_count": None,
        "extreme_return_minmax_candidate_symbol_count_from_existing_return_sanity": len(sorted(set(minmax_candidate_symbols))),
        "extreme_return_minmax_candidate_symbols_from_existing_return_sanity": sorted(set(minmax_candidate_symbols)),
    }


def bool_is(payload: dict[str, Any], key: str, expected: bool) -> bool:
    return payload.get(key) is expected


def value_is(payload: dict[str, Any], key: str, expected: Any) -> bool:
    return payload.get(key) == expected


def build_summary() -> dict[str, dict[str, Any]]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_required_artifacts()
    preview = loaded.get("preview", {})
    baseline = loaded.get("baseline_report", {})
    return_sanity = loaded.get("return_sanity", {})
    null_cost_holdout = loaded.get("null_cost_holdout", {})
    inventory = detail_inventory(loaded)

    required_path_exists = {
        str(PREVIEW): PREVIEW.exists(),
        str(BASELINE_REPORT): BASELINE_REPORT.exists(),
        str(MONTHLY_COVERAGE): MONTHLY_COVERAGE.exists(),
        str(INCOMPLETE_HOURS): INCOMPLETE_HOURS.exists(),
        str(RETURN_SANITY): RETURN_SANITY.exists(),
        str(VOLUME_SANITY): VOLUME_SANITY.exists(),
        str(NULL_COST_HOLDOUT): NULL_COST_HOLDOUT.exists(),
    }

    baseline_execution_confirmed = (
        value_is(baseline, "okx_88_symbol_1h_panel_baseline_research_sanity_execution_status", BASELINE_PASS_STATUS)
        and bool_is(baseline, "baseline_research_sanity_execution_performed", True)
        and bool_is(baseline, "replacement_checks_all_true", True)
    )
    preview_confirmed = (
        value_is(preview, "research_backtest_preview_after_okx_88_symbol_1h_panel_readiness_gate_status", PREVIEW_PASS_STATUS)
        and bool_is(preview, "preview_created", True)
        and bool_is(preview, "replacement_checks_all_true", True)
    )
    no_forbidden_execution = (
        bool_is(baseline, "strategy_search_executed", False)
        and bool_is(baseline, "candidate_generation_performed", False)
        and bool_is(baseline, "edge_claim_performed", False)
        and bool_is(baseline, "data_download_performed", False)
        and bool_is(baseline, "data_build_performed", False)
        and bool_is(baseline, "aggregation_performed_now", False)
        and bool_is(baseline, "original_source_full_csv_read_performed", False)
        and bool_is(baseline, "okx_api_call_performed", False)
        and bool_is(baseline, "okx_browse_performed", False)
    )
    restrictions_preserved = (
        bool_is(baseline, "strategy_search_allowed_now", False)
        and bool_is(baseline, "candidate_generation_allowed_now", False)
        and bool_is(baseline, "family_release_allowed_now", False)
        and bool_is(baseline, "edge_claim_allowed_now", False)
        and bool_is(baseline, "runtime_live_capital_allowed_now", False)
        and bool_is(baseline, "future_execution_may_generate_candidates", False)
        and bool_is(baseline, "future_execution_may_claim_edge", False)
        and bool_is(baseline, "holdout_registry_valid_for_this_panel", False)
        and bool_is(baseline, "holdout_registry_creation_required_before_strategy_search", True)
        and bool_is(baseline, "strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel", True)
    )
    panel_identity_confirmed = (
        value_is(baseline, "selected_symbol_count", EXPECTED_SELECTED_SYMBOL_COUNT)
        and value_is(baseline, "output_symbol_count", EXPECTED_OUTPUT_SYMBOL_COUNT)
        and value_is(baseline, "output_1h_row_count", EXPECTED_OUTPUT_ROWS)
        and value_is(baseline, "expected_rows_per_symbol", EXPECTED_ROWS_PER_SYMBOL)
        and value_is(baseline, "complete_1h_row_count", EXPECTED_COMPLETE_ROWS)
        and value_is(baseline, "incomplete_1h_row_count", EXPECTED_INCOMPLETE_ROWS)
        and bool_is(baseline, "all_hours_complete", False)
        and bool_is(baseline, "per_symbol_output_row_count_valid", True)
    )
    diagnostics_confirmed = (
        bool_is(baseline, "monthly_coverage_diagnostics_created", True)
        and bool_is(baseline, "incomplete_hour_diagnostics_created", True)
        and bool_is(baseline, "return_distribution_sanity_created", True)
        and bool_is(baseline, "volume_liquidity_sanity_created", True)
        and all(required_path_exists.values())
    )
    return_sanity_confirmed = (
        value_is(baseline, "finite_return_count", EXPECTED_FINITE_RETURN_COUNT)
        and value_is(baseline, "nan_inf_return_count", EXPECTED_NAN_INF_RETURN_COUNT)
        and value_is(baseline, "extreme_return_diagnostic_count", EXPECTED_EXTREME_RETURN_COUNT)
        and value_is(return_sanity, "extreme_return_diagnostic_count", EXPECTED_EXTREME_RETURN_COUNT)
    )

    replacement_checks = {
        "baseline_execution_artifact_valid": baseline_execution_confirmed,
        "diagnostic_artifacts_confirmed": diagnostics_confirmed,
        "extreme_return_count_confirmed_as_p1_attention": return_sanity_confirmed,
        "extreme_return_detail_inventory_completed": True,
        "head_matches_expected": head == EXPECTED_HEAD,
        "holdout_and_research_restrictions_preserved": restrictions_preserved,
        "input_artifacts_readable": not load_errors,
        "no_forbidden_research_strategy_edge_runtime_actions": no_forbidden_execution,
        "panel_identity_confirmed": panel_identity_confirmed,
        "preview_artifact_valid": preview_confirmed,
        "repo_clean_except_current_tool": repo_clean,
        "route_targets_extreme_return_review_before_strategy_search": True,
        "summary_does_not_treat_extreme_returns_as_edge": True,
    }
    replacement_checks_all_true = all(replacement_checks.values())
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE

    next_review_must_extract = not inventory["extreme_return_detail_sufficient_for_concentration_answer"]
    summary = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else sum(1 for passed in replacement_checks.values() if not passed),
        "active_p1_attention_count": EXPECTED_EXTREME_RETURN_COUNT if return_sanity_confirmed else 0,
        "aggregation_performed_now": False,
        "all_hours_complete": baseline.get("all_hours_complete"),
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_extreme_return_diagnostic_review_next": replacement_checks_all_true,
        "approval_grants_holdout_registry_builder_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "baseline_execution_confirmed": baseline_execution_confirmed,
        "baseline_summary_created": replacement_checks_all_true,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "complete_1h_row_count": baseline.get("complete_1h_row_count"),
        "cost_slippage_policy_required": True,
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_summary": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "expected_rows_per_symbol": baseline.get("expected_rows_per_symbol"),
        "extreme_return_concentrated_in_top_3_symbols": inventory["extreme_return_concentrated_in_top_3_symbols"],
        "extreme_return_detail_artifact_detected": inventory["extreme_return_detail_artifact_detected"],
        "extreme_return_detail_artifact_path": inventory["extreme_return_detail_artifact_path"],
        "extreme_return_detail_missing_reason": inventory["extreme_return_detail_missing_reason"],
        "extreme_return_detail_sufficient_for_concentration_answer": inventory[
            "extreme_return_detail_sufficient_for_concentration_answer"
        ],
        "extreme_return_diagnostic_attention": True,
        "extreme_return_diagnostic_count": baseline.get("extreme_return_diagnostic_count"),
        "extreme_return_incomplete_hour_overlap_available": inventory["extreme_return_incomplete_hour_overlap_available"],
        "extreme_return_incomplete_hour_overlap_count": inventory["extreme_return_incomplete_hour_overlap_count"],
        "extreme_return_review_required_before_edge_claim": True,
        "extreme_return_review_required_before_strategy_search": True,
        "extreme_return_symbol_distribution_available": inventory["extreme_return_symbol_distribution_available"],
        "extreme_return_timestamp_distribution_available": inventory["extreme_return_timestamp_distribution_available"],
        "extreme_return_top_3_symbol_count": inventory["extreme_return_top_3_symbol_count"],
        "extreme_return_top_rows_available": inventory["extreme_return_top_rows_available"],
        "extreme_return_top_symbol": inventory["extreme_return_top_symbol"],
        "extreme_return_top_symbol_count": inventory["extreme_return_top_symbol_count"],
        "extreme_return_unique_month_count": inventory["extreme_return_unique_month_count"],
        "extreme_return_unique_symbol_count": inventory["extreme_return_unique_symbol_count"],
        "extreme_returns_treated_as_edge": False,
        "family_release_allowed_now": False,
        "finite_return_count": baseline.get("finite_return_count"),
        "future_execution_may_claim_edge": False,
        "future_execution_may_generate_candidates": False,
        "holdout_policy_required": True,
        "holdout_registry_creation_required_before_strategy_search": True,
        "holdout_registry_valid_for_this_panel": False,
        "incomplete_1h_row_count": baseline.get("incomplete_1h_row_count"),
        "incomplete_hour_diagnostics_confirmed": bool_is(baseline, "incomplete_hour_diagnostics_created", True)
        and INCOMPLETE_HOURS.exists(),
        "monthly_coverage_diagnostics_confirmed": bool_is(baseline, "monthly_coverage_diagnostics_created", True)
        and MONTHLY_COVERAGE.exists(),
        "nan_inf_return_count": baseline.get("nan_inf_return_count"),
        "next_module": next_module,
        "next_review_must_classify_extreme_return_causes": True,
        "next_review_must_extract_full_row_level_extremes": next_review_must_extract,
        "null_baseline_required": True,
        "okx_88_symbol_1h_panel_baseline_research_sanity_summary_status": status,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
        "original_source_full_csv_read_performed": False,
        "output_1h_row_count": baseline.get("output_1h_row_count"),
        "output_symbol_count": baseline.get("output_symbol_count"),
        "output_valid_for_edge_claim": False,
        "output_valid_for_research_backtest": True,
        "per_symbol_output_row_count_valid": baseline.get("per_symbol_output_row_count_valid"),
        "preview_confirmed": preview_confirmed,
        "read_only_research_panel_ready": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "required_input_artifact_errors": load_errors,
        "required_input_artifact_paths_exist": required_path_exists,
        "return_distribution_sanity_confirmed": bool_is(baseline, "return_distribution_sanity_created", True)
        and RETURN_SANITY.exists(),
        "runtime_live_capital_allowed_now": False,
        "selected_symbol_count": baseline.get("selected_symbol_count"),
        "strategy_search_allowed_now": False,
        "strategy_search_executed": False,
        "strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel": True,
        "tracked_python_count_at_summary_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "volume_liquidity_sanity_confirmed": bool_is(baseline, "volume_liquidity_sanity_created", True)
        and VOLUME_SANITY.exists(),
    }

    diagnostic_results = {
        "all_hours_complete": summary["all_hours_complete"],
        "complete_1h_row_count": summary["complete_1h_row_count"],
        "expected_rows_per_symbol": summary["expected_rows_per_symbol"],
        "finite_return_count": summary["finite_return_count"],
        "incomplete_1h_row_count": summary["incomplete_1h_row_count"],
        "monthly_coverage_diagnostics_confirmed": summary["monthly_coverage_diagnostics_confirmed"],
        "nan_inf_return_count": summary["nan_inf_return_count"],
        "output_1h_row_count": summary["output_1h_row_count"],
        "output_symbol_count": summary["output_symbol_count"],
        "per_symbol_output_row_count_valid": summary["per_symbol_output_row_count_valid"],
        "selected_symbol_count": summary["selected_symbol_count"],
        "volume_liquidity_sanity_confirmed": summary["volume_liquidity_sanity_confirmed"],
    }
    attention = {
        "classification": "P1_ATTENTION_DIAGNOSTIC_REVIEW_REQUIRED",
        "do_not_treat_as_edge": True,
        "extreme_return_diagnostic_count": summary["extreme_return_diagnostic_count"],
        "extreme_return_review_required_before_edge_claim": True,
        "extreme_return_review_required_before_strategy_search": True,
        "next_review_must_classify_extreme_return_causes": True,
        "next_review_must_extract_full_row_level_extremes": next_review_must_extract,
        "required_next_review_outputs": [
            "count by symbol",
            "count by month",
            "count by timestamp/hour",
            "top 10 rows by absolute return",
            "concentration in top 3 symbols",
            "listing/first-available-hour overlap",
            "incomplete-hour overlap",
            "material conflict/quarantine overlap if provenance allows",
            "volume spike overlap",
            "classification: DATA_ISSUE / LISTING_EVENT / REAL_MARKET_EVENT / UNRESOLVED",
        ],
    }
    restrictions = {
        key: summary[key]
        for key in [
            "approval_grants_candidate_generation_now",
            "approval_grants_edge_claim_now",
            "approval_grants_future_extreme_return_diagnostic_review_next",
            "approval_grants_holdout_registry_builder_now",
            "approval_grants_runtime_live_capital_now",
            "approval_grants_strategy_search_now",
            "candidate_generation_allowed_now",
            "edge_claim_allowed_now",
            "family_release_allowed_now",
            "holdout_registry_creation_required_before_strategy_search",
            "holdout_registry_valid_for_this_panel",
            "runtime_live_capital_allowed_now",
            "strategy_search_allowed_now",
            "strategy_search_must_remain_blocked_until_holdout_registry_valid_for_this_panel",
        ]
    }
    route_approval = {
        "approval_grants_baseline_summary_now": replacement_checks_all_true,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_future_extreme_return_diagnostic_review_next": replacement_checks_all_true,
        "approval_grants_holdout_registry_builder_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_now": False,
        "next_module": next_module,
        "route_directly_to_strategy_search": False,
    }
    self_validator = {
        "created_at_utc": summary["created_at_utc"],
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "required_output_artifacts": [],
        "unexpected_git_status_entries": unexpected_status,
    }
    return {
        "attention": attention,
        "diagnostic_results": diagnostic_results,
        "inventory": inventory,
        "restrictions": restrictions,
        "route_approval": route_approval,
        "self_validator": self_validator,
        "summary": summary,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    artifact_paths = [
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary.json",
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_diagnostic_results_summary.json",
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_attention_summary.json",
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_extreme_return_detail_inventory.json",
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_research_restrictions_after_baseline_summary.json",
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_next_diagnostic_route_approval_record.json",
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_baseline_research_sanity_summary_self_validator.json",
    ]
    write_json(artifact_paths[0], outputs["summary"])
    write_json(artifact_paths[1], outputs["diagnostic_results"])
    write_json(artifact_paths[2], outputs["attention"])
    write_json(artifact_paths[3], outputs["inventory"])
    write_json(artifact_paths[4], outputs["restrictions"])
    write_json(artifact_paths[5], outputs["route_approval"])
    outputs["self_validator"]["required_output_artifacts"] = [str(path) for path in artifact_paths]
    outputs["self_validator"]["required_output_artifacts_exist"] = {str(path): path.exists() for path in artifact_paths[:-1]}
    write_json(artifact_paths[6], outputs["self_validator"])


def main() -> int:
    outputs = build_summary()
    write_outputs(outputs)
    print(json.dumps(outputs["summary"], indent=2, sort_keys=True))
    return 0 if outputs["summary"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
