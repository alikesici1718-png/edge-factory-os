#!/usr/bin/env python3
"""Evaluate restricted momentum retry diagnostic results.

This repo-only evaluator reads strategy-search retry diagnostic artifacts,
classifies result quality, and selects the next governance route. It does not
read panel rows, run new strategy search, test reversal, generate candidates,
claim edge, release a family, access holdout, or enable runtime/live/capital.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_after_execution_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_after_execution_v1"
)

EXPECTED_HEAD = "5520a480ddd5db28f8f6beeb30306405ab165c63"
EXECUTION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_after_revised_non_holdout_view_preview_v1"
)
EXECUTION_REPORT = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_report.json"
CONFIG_METRICS = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_config_metrics.csv"
TRAIN_VALIDATION_METRICS = (
    EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_train_validation_metrics.csv"
)
MONTHLY_STABILITY = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_monthly_stability.csv"
NULL_DIAGNOSTICS = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_null_diagnostics.json"
COST_SENSITIVITY = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_cost_sensitivity.json"
TURNOVER_CONCENTRATION = (
    EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_turnover_concentration.json"
)
DATA_WINDOW_ACCESS_LOG = (
    EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_data_window_access_log.json"
)
PROGRESS_LEDGER = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_progress_ledger.json"
RELEASE_BLOCKS = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_release_blocks.json"
EXECUTION_SUMMARY = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_summary.json"

PREVIEW_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_after_revised_non_holdout_view_finalization_v1"
)
RETRY_PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview.json"
FINALIZE_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_after_forensic_validation_v1"
)
FINAL_MANIFEST = FINALIZE_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_manifest.json"
FINAL_ELIGIBILITY = FINALIZE_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_eligibility_record.json"
ROUTE_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1"
)
ROUTE_PREREG = ROUTE_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration.json"
ROUTE_BOUNDS = ROUTE_DIR / "repo_only_okx_88_symbol_1h_panel_cross_sectional_momentum_baseline_config_bounds.json"

PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_EVALUATED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_EVALUATOR_REVIEW_REQUIRED"
ROUTE_FAMILY = "CROSS_SECTIONAL_MOMENTUM_BASELINE"
PROMISING_CLASS = "MOMENTUM_BASELINE_DIAGNOSTIC_PROMISING_ROBUSTNESS_PREVIEW_NEXT"
INCONCLUSIVE_CLASS = "MOMENTUM_BASELINE_INCONCLUSIVE_GOVERNANCE_SUMMARY_NEXT"
REJECTED_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
BLOCKED_CLASS = "MOMENTUM_BASELINE_BLOCKED_ARTIFACT_OR_METRIC_INTEGRITY_ISSUE"
NEXT_PROMISING_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_momentum_robustness_preview_after_evaluator_v1.py"
NEXT_INCONCLUSIVE_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_momentum_result_governance_summary_after_evaluator_v1.py"
NEXT_REJECTED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_record_after_evaluator_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_STRATEGY_SEARCH_RETRY_EVALUATED_GOVERNANCE_ROUTE_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_STRATEGY_SEARCH_RETRY_EVALUATOR_BLOCKED_REVIEW_REQUIRED"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO.as_posix()}", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return payload


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_suffix = TOOL_REL.as_posix()
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(allowed_suffix)]
    return not unexpected, unexpected


def load_json_input(label: str, path: Path, errors: dict[str, str]) -> dict[str, Any]:
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        errors[label] = f"{path}: {exc}"
        return {}


def load_csv_input(label: str, path: Path, errors: dict[str, str]) -> list[dict[str, str]]:
    try:
        return read_csv(path)
    except OSError as exc:
        errors[label] = f"{path}: {exc}"
        return []


def to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def execution_confirmed(report: dict[str, Any]) -> bool:
    return (
        report.get("okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_EXECUTED"
        and report.get("restricted_strategy_search_retry_execution_performed") is True
        and report.get("retry_preview_confirmed") is True
        and report.get("finalized_revised_non_holdout_view_confirmed") is True
        and report.get("route_preregistration_confirmed") is True
        and report.get("route_family_selected") == ROUTE_FAMILY
        and report.get("route_family_count") == 1
        and report.get("reversal_tested") is False
        and report.get("momentum_vs_reversal_compared") is False
        and report.get("lookback_options_used") == "6h,12h,24h,48h"
        and report.get("holding_period_options_used") == "1h,3h,6h"
        and report.get("tested_config_count") == 12
        and report.get("current_all_in_one_panel_read_performed") is False
        and report.get("sealed_holdout_accessed") is False
        and report.get("boundary_buffer_accessed") is False
        and report.get("candidate_generation_performed") is False
        and report.get("edge_claim_performed") is False
        and report.get("family_release_performed") is False
        and report.get("replacement_checks_all_true") is True
        and report.get("next_module") == TOOL_REL.name
    )


def rank_map(rows: list[dict[str, Any]], metric: str) -> dict[str, int]:
    ordered = sorted(rows, key=lambda row: to_float(row.get(metric)), reverse=True)
    return {str(row["config_id"]): index + 1 for index, row in enumerate(ordered)}


def monthly_review(monthly_rows: list[dict[str, str]], best_config_id: str) -> dict[str, Any]:
    validation_rows = [row for row in monthly_rows if row.get("config_id") == best_config_id and row.get("window") == "validation"]
    net_values = [to_float(row.get("monthly_net_return")) for row in validation_rows]
    valid_values = [value for value in net_values if math.isfinite(value)]
    month_count = len(valid_values)
    positive = sum(1 for value in valid_values if value > 0)
    negative = sum(1 for value in valid_values if value < 0)
    best = max(valid_values) if valid_values else 0.0
    worst = min(valid_values) if valid_values else 0.0
    total = sum(valid_values)
    concentrated = bool(valid_values) and best > abs(total) * 0.75
    catastrophic_worst = bool(valid_values) and worst < -abs(total) * 0.75
    passed = month_count >= 6 and positive > negative and not concentrated and not catastrophic_worst and total > 0
    return {
        "best_validation_month_net": best,
        "month_count": month_count,
        "monthly_stability_review_passed": passed,
        "negative_validation_month_count": negative,
        "positive_validation_month_count": positive,
        "stability_concentrated_in_one_month": concentrated,
        "validation_monthly_net_total": total,
        "worst_validation_month_net": worst,
    }


def null_review(null_payload: dict[str, Any], best_config_id: str) -> dict[str, Any]:
    records = null_payload.get("null_records", [])
    validation_records = [
        row for row in records if row.get("config_id") == best_config_id and row.get("window") == "validation"
    ]
    train_records = [row for row in records if row.get("config_id") == best_config_id and row.get("window") == "train_development"]
    validation_p = validation_records[0].get("empirical_two_sided_p") if validation_records else None
    train_p = train_records[0].get("empirical_two_sided_p") if train_records else None
    validation_observed = validation_records[0].get("observed_mean") if validation_records else None
    train_observed = train_records[0].get("observed_mean") if train_records else None
    passed = (
        validation_p is not None
        and train_p is not None
        and to_float(validation_observed) > 0
        and to_float(train_observed) > 0
        and to_float(validation_p) <= 0.10
    )
    return {
        "null_baseline_review_passed": passed,
        "train_null_p_style": train_p,
        "train_observed_mean": train_observed,
        "validation_null_p_style": validation_p,
        "validation_observed_mean": validation_observed,
    }


def turnover_review(turnover_payload: dict[str, Any], best_config_id: str) -> dict[str, Any]:
    records = turnover_payload.get("turnover_concentration_records", [])
    validation_records = [
        row for row in records if row.get("config_id") == best_config_id and row.get("window") == "validation"
    ]
    if not validation_records:
        return {
            "average_turnover": None,
            "concentration_risk_flag": True,
            "top_symbol_exposure_share": None,
            "turnover_concentration_review_passed": False,
            "turnover_risk_flag": True,
        }
    row = validation_records[0]
    avg_turnover = to_float(row.get("average_turnover"))
    max_turnover = to_float(row.get("max_turnover"))
    top_share = to_float(row.get("top_symbol_exposure_share"))
    turnover_risk = avg_turnover > 1.5 or max_turnover > 2.0
    concentration_risk = top_share > 0.20
    return {
        "average_turnover": avg_turnover,
        "concentration_risk_flag": concentration_risk,
        "max_turnover": max_turnover,
        "top_symbol_exposure_share": top_share,
        "turnover_concentration_review_passed": not turnover_risk and not concentration_risk,
        "turnover_risk_flag": turnover_risk,
    }


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    load_errors: dict[str, str] = {}
    execution = load_json_input("execution_report", EXECUTION_REPORT, load_errors)
    null_payload = load_json_input("null_diagnostics", NULL_DIAGNOSTICS, load_errors)
    cost = load_json_input("cost_sensitivity", COST_SENSITIVITY, load_errors)
    turnover = load_json_input("turnover_concentration", TURNOVER_CONCENTRATION, load_errors)
    access_log = load_json_input("data_window_access_log", DATA_WINDOW_ACCESS_LOG, load_errors)
    progress = load_json_input("progress_ledger", PROGRESS_LEDGER, load_errors)
    release_blocks = load_json_input("release_blocks", RELEASE_BLOCKS, load_errors)
    summary = load_json_input("execution_summary", EXECUTION_SUMMARY, load_errors)
    retry_preview = load_json_input("retry_preview", RETRY_PREVIEW, load_errors)
    final_manifest = load_json_input("final_manifest", FINAL_MANIFEST, load_errors)
    final_eligibility = load_json_input("final_eligibility", FINAL_ELIGIBILITY, load_errors)
    route = load_json_input("route_preregistration", ROUTE_PREREG, load_errors)
    bounds = load_json_input("route_bounds", ROUTE_BOUNDS, load_errors)

    config_rows_raw = load_csv_input("config_metrics", CONFIG_METRICS, load_errors)
    tv_rows_raw = load_csv_input("train_validation_metrics", TRAIN_VALIDATION_METRICS, load_errors)
    monthly_rows_raw = load_csv_input("monthly_stability", MONTHLY_STABILITY, load_errors)

    config_metrics_loaded = len(config_rows_raw) == 12
    train_validation_metrics_loaded = len(tv_rows_raw) == 24
    monthly_stability_loaded = len(monthly_rows_raw) > 0
    null_diagnostics_loaded = bool(null_payload.get("null_records"))
    turnover_concentration_loaded = bool(turnover.get("turnover_concentration_records"))
    progress_records = progress.get("progress_records", [])
    progress_complete = len(progress_records) == 12 and all(row.get("status") == "COMPLETE" for row in progress_records)
    release_blocks_confirmed = (
        release_blocks.get("candidate_generation_blocked") is True
        and release_blocks.get("edge_claim_blocked") is True
        and release_blocks.get("family_release_blocked") is True
    )
    retry_execution_confirmed = execution_confirmed(execution)
    finalized_confirmed = final_manifest.get("output_valid_for_strategy_search_after_finalization") is True and final_eligibility.get("output_valid_for_restricted_momentum_search_input") is True
    route_confirmed = route.get("route_family_selected") == ROUTE_FAMILY and bounds.get("route_family_selected") == ROUTE_FAMILY

    config_rows: list[dict[str, Any]] = []
    for row in config_rows_raw:
        config_rows.append(
            {
                **row,
                "train_net_return_sum": to_float(row.get("train_net_return_sum")),
                "validation_net_return_sum": to_float(row.get("validation_net_return_sum")),
                "train_turnover_average": to_float(row.get("train_turnover_average")),
                "validation_turnover_average": to_float(row.get("validation_turnover_average")),
            }
        )
    best_validation = max(config_rows, key=lambda row: row["validation_net_return_sum"]) if config_rows else {}
    best_train = max(config_rows, key=lambda row: row["train_net_return_sum"]) if config_rows else {}
    best_validation_config_id = best_validation.get("config_id")
    validation_rank = rank_map(config_rows, "validation_net_return_sum") if config_rows else {}
    train_rank = rank_map(config_rows, "train_net_return_sum") if config_rows else {}
    rank_diffs = [
        abs(validation_rank[config_id] - train_rank[config_id])
        for config_id in validation_rank
        if config_id in train_rank
    ]
    train_validation_rank_consistency = 1.0 - (sum(rank_diffs) / (len(rank_diffs) * 11)) if rank_diffs else 0.0
    best_validation_train_net = best_validation.get("train_net_return_sum", 0.0)
    best_validation_net = best_validation.get("validation_net_return_sum", 0.0)
    validation_positive_after_cost = best_validation_net > 0
    train_validation_degradation_flag = best_validation_train_net > 0 and best_validation_net < best_validation_train_net * 0.25
    if best_validation_train_net <= 0 and best_validation_net <= 0:
        train_validation_degradation_flag = False

    null_result = null_review(null_payload, str(best_validation_config_id))
    monthly_result = monthly_review(monthly_rows_raw, str(best_validation_config_id))
    turnover_result = turnover_review(turnover, str(best_validation_config_id))

    metric_issues = []
    if not retry_execution_confirmed:
        metric_issues.append("execution_report_invalid")
    if not config_metrics_loaded:
        metric_issues.append("config_metrics_missing_or_incomplete")
    if not train_validation_metrics_loaded:
        metric_issues.append("train_validation_metrics_missing_or_incomplete")
    if not monthly_stability_loaded:
        metric_issues.append("monthly_stability_missing")
    if not null_diagnostics_loaded:
        metric_issues.append("null_diagnostics_missing")
    if not turnover_concentration_loaded:
        metric_issues.append("turnover_concentration_missing")
    if not progress_complete:
        metric_issues.append("progress_ledger_incomplete")
    if not release_blocks_confirmed:
        metric_issues.append("release_blocks_invalid")

    monthly_passed = monthly_result["monthly_stability_review_passed"]
    null_passed = null_result["null_baseline_review_passed"]
    turnover_passed = turnover_result["turnover_concentration_review_passed"]
    diagnostic_promising = (
        validation_positive_after_cost
        and null_passed
        and monthly_passed
        and turnover_passed
        and not train_validation_degradation_flag
        and not metric_issues
    )
    mixed_results = any(row["validation_net_return_sum"] > 0 for row in config_rows)
    if metric_issues:
        result_class = BLOCKED_CLASS
        result_class_reason = "Required execution artifacts or metrics are missing, incomplete, or invalid."
        next_module = NEXT_BLOCKED_MODULE
    elif diagnostic_promising:
        result_class = PROMISING_CLASS
        result_class_reason = "Validation net, null, monthly stability, and turnover/concentration gates justify read-only robustness preview."
        next_module = NEXT_PROMISING_MODULE
    elif mixed_results:
        result_class = INCONCLUSIVE_CLASS
        result_class_reason = "Mixed diagnostic results exist, but robustness gates are not all satisfied."
        next_module = NEXT_INCONCLUSIVE_MODULE
    else:
        result_class = REJECTED_CLASS
        result_class_reason = "All validation net metrics are non-positive after costs, so the momentum baseline is rejected for follow-up."
        next_module = NEXT_REJECTED_MODULE

    replacement_checks = {
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "repo_clean_except_current_tool": repo_clean,
        "retry_execution_confirmed": retry_execution_confirmed,
        "finalized_revised_non_holdout_view_confirmed": finalized_confirmed,
        "route_family_confirmed": route_confirmed,
        "tested_config_count_12": execution.get("tested_config_count") == 12 and config_metrics_loaded,
        "config_metrics_loaded": config_metrics_loaded,
        "train_validation_metrics_loaded": train_validation_metrics_loaded,
        "null_diagnostics_loaded": null_diagnostics_loaded,
        "monthly_stability_loaded": monthly_stability_loaded,
        "turnover_concentration_loaded": turnover_concentration_loaded,
        "progress_ledger_complete": progress_complete,
        "release_blocks_confirmed": release_blocks_confirmed,
        "no_forbidden_execution": (
            execution.get("sealed_holdout_accessed") is False
            and execution.get("boundary_buffer_accessed") is False
            and execution.get("current_all_in_one_panel_read_performed") is False
            and execution.get("reversal_tested") is False
            and execution.get("momentum_vs_reversal_compared") is False
        ),
        "evaluator_no_new_search_candidate_edge_release": True,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    if not replacement_checks_all_true:
        result_class = BLOCKED_CLASS
        result_class_reason = "Evaluator fail-closed because prerequisite replacement checks did not all pass."
        next_module = NEXT_BLOCKED_MODULE

    approval = {
        "approval_grants_evaluator_now": True,
        "approval_grants_future_robustness_preview_next": result_class == PROMISING_CLASS,
        "approval_grants_future_governance_summary_next": result_class == INCONCLUSIVE_CLASS,
        "approval_grants_future_closure_record_next": result_class == REJECTED_CLASS,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_strategy_search_expansion_now": False,
        "approval_grants_holdout_access_now": False,
        "approval_grants_runtime_live_capital_now": False,
    }
    report = {
        "active_p0_blocker_count": 1 if result_class == BLOCKED_CLASS else 0,
        "active_p1_attention_count": 0,
        "best_train_config_id": best_train.get("config_id"),
        "best_validation_config_id": best_validation_config_id,
        "best_validation_holding_period": best_validation.get("holding_period"),
        "best_validation_lookback": best_validation.get("lookback"),
        "best_validation_net_metric": best_validation_net,
        "boundary_buffer_accessed": execution.get("boundary_buffer_accessed", False),
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "config_metrics_loaded": config_metrics_loaded,
        "concentration_risk_flag": turnover_result["concentration_risk_flag"],
        "created_at_utc": now_utc(),
        "current_all_in_one_panel_read_performed": False,
        "current_evidence_chain_quality_after_evaluator": (
            PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY
        ),
        "diagnostic_promising": diagnostic_promising,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "evaluator_performed": replacement_checks_all_true,
        "family_release_allowed_now": False,
        "family_release_performed": False,
        "finalized_panel_rows_read_for_returns": False,
        "finalized_revised_non_holdout_view_confirmed": finalized_confirmed,
        "holdout_access_allowed_now": False,
        "metric_integrity_issues": metric_issues,
        "metric_integrity_issue_count": len(metric_issues),
        "momentum_vs_reversal_compared": False,
        "monthly_stability_loaded": monthly_stability_loaded,
        "monthly_stability_review": monthly_result,
        "monthly_stability_review_passed": monthly_passed,
        "new_strategy_search_executed": False,
        "next_module": next_module,
        "null_baseline_review": null_result,
        "null_baseline_review_passed": null_passed,
        "null_diagnostics_loaded": null_diagnostics_loaded,
        "okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_status": status,
        "progress_ledger_complete_confirmed": progress_complete,
        "release_blocks_confirmed": release_blocks_confirmed,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "result_class": result_class,
        "result_class_reason": result_class_reason,
        "retry_execution_confirmed": retry_execution_confirmed,
        "reversal_tested": False,
        "route_family_selected": ROUTE_FAMILY,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_accessed": execution.get("sealed_holdout_accessed", False),
        "strategy_search_expansion_allowed_now": False,
        "tested_config_count": execution.get("tested_config_count"),
        "tracked_python_count_at_evaluator_run": tracked_python_count(),
        "train_validation_degradation_flag": train_validation_degradation_flag,
        "train_validation_metrics_loaded": train_validation_metrics_loaded,
        "train_validation_rank_consistency": train_validation_rank_consistency,
        "turnover_concentration_loaded": turnover_concentration_loaded,
        "turnover_concentration_review": turnover_result,
        "turnover_concentration_review_passed": turnover_passed,
        "turnover_risk_flag": turnover_result["turnover_risk_flag"],
        "unexpected_git_status_entries": unexpected_status,
        "validation_positive_after_cost": validation_positive_after_cost,
    }
    report.update(approval)
    return create_outputs(report, config_rows, tv_rows_raw, monthly_rows_raw, null_payload, turnover)


def create_outputs(
    report: dict[str, Any],
    config_rows: list[dict[str, Any]],
    tv_rows: list[dict[str, str]],
    monthly_rows: list[dict[str, str]],
    null_payload: dict[str, Any],
    turnover_payload: dict[str, Any],
) -> dict[str, Any]:
    ranking_rows = []
    for index, row in enumerate(sorted(config_rows, key=lambda item: item["validation_net_return_sum"], reverse=True), start=1):
        ranking_rows.append(
            {
                "rank_validation_net": index,
                "config_id": row["config_id"],
                "lookback": row["lookback"],
                "holding_period": row["holding_period"],
                "train_net_return_sum": row["train_net_return_sum"],
                "validation_net_return_sum": row["validation_net_return_sum"],
                "diagnostic_only_not_candidate": True,
            }
        )
    train_validation = {
        **report,
        "train_validation_metric_rows": tv_rows,
        "train_validation_rank_consistency_method": "1 - mean_abs_rank_delta / 11",
    }
    null_review_payload = {
        **report,
        "null_record_count": len(null_payload.get("null_records", [])),
        "null_records_for_review": null_payload.get("null_records", []),
    }
    monthly_review_payload = {
        **report,
        "monthly_row_count": len(monthly_rows),
        "monthly_rows_reviewed": monthly_rows,
    }
    turnover_review_payload = {
        **report,
        "turnover_concentration_records": turnover_payload.get("turnover_concentration_records", []),
    }
    decision = {
        **report,
        "classification_options": [PROMISING_CLASS, INCONCLUSIVE_CLASS, REJECTED_CLASS, BLOCKED_CLASS],
    }
    approval = {
        **report,
        "approval_scope": "selected future read-only governance route only",
    }
    self_validator = {
        **report,
        "artifact_count_expected": 9,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_report.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_config_ranking.csv",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_train_validation_comparison.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_null_review.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_monthly_stability_review.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_turnover_concentration_review.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_decision.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
        "self_validation_result": report.get("replacement_checks_all_true") is True,
    }
    return {
        "approval": approval,
        "decision": decision,
        "monthly": monthly_review_payload,
        "null": null_review_payload,
        "ranking_rows": ranking_rows,
        "report": report,
        "self_validator": self_validator,
        "train_validation": train_validation,
        "turnover": turnover_review_payload,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_report.json",
        outputs["report"],
    )
    write_csv(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_config_ranking.csv",
        outputs["ranking_rows"],
        [
            "rank_validation_net",
            "config_id",
            "lookback",
            "holding_period",
            "train_net_return_sum",
            "validation_net_return_sum",
            "diagnostic_only_not_candidate",
        ],
    )
    write_json(
        OUTPUT_DIR
        / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_train_validation_comparison.json",
        outputs["train_validation"],
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_null_review.json",
        outputs["null"],
    )
    write_json(
        OUTPUT_DIR
        / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_monthly_stability_review.json",
        outputs["monthly"],
    )
    write_json(
        OUTPUT_DIR
        / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_turnover_concentration_review.json",
        outputs["turnover"],
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_decision.json",
        outputs["decision"],
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_approval_record.json",
        outputs["approval"],
    )
    write_json(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_self_validator.json",
        outputs["self_validator"],
    )


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["report"], indent=2, sort_keys=True))
    return 0 if outputs["report"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
