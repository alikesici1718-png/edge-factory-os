#!/usr/bin/env python3
"""Restricted OKX 88-symbol 1h momentum execution guard.

This tool is allowed to run only the preregistered momentum diagnostic when
sealed holdout rows can be excluded at read time. The current validated panel is
stored as symbol-contiguous CSV blocks and no row-offset index artifact is
available, so the tool fails closed instead of scanning through sealed holdout
rows to reach later symbols.
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
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_after_route_preregistration_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_after_route_preregistration_v1"

PREREG_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1"
PREREG = PREREG_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration.json"
CONFIG_BOUNDS = PREREG_DIR / "repo_only_okx_88_symbol_1h_panel_cross_sectional_momentum_baseline_config_bounds.json"
PREREG_APPROVAL = PREREG_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_approval_record.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
SPLIT_POLICY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_split_policy.json"
ACCESS_RULES = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_access_rules.json"

PIPELINE_SUMMARY = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_pipeline_summary_after_validator_v1" / "repo_only_okx_88_symbol_near_3y_1h_panel_validated_pipeline_output_summary.json"
BUILD_SUMMARY = EDGE_ROOT / "edge_factory_os_repo_only_historical_data_acquisition_okx_88_symbol_near_3y_1m_to_1h_build_execution_after_preview_approval_v1" / "repo_only_okx_88_symbol_near_3y_1m_to_1h_build_execution_summary.json"

EXPECTED_HEAD = "833e8eb"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_EXECUTED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_EXECUTION_SEALED_HOLDOUT_READ_GUARD"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_evaluator_after_execution_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_STRATEGY_SEARCH_EXECUTED_EVALUATOR_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_EXECUTION_BLOCKED_SEALED_HOLDOUT_READ_GUARD"

ROUTE_FAMILY = "CROSS_SECTIONAL_MOMENTUM_BASELINE"
LOOKBACKS = ["6h", "12h", "24h", "48h"]
HOLDING_PERIODS = ["1h", "3h", "6h"]
BLOCKER_CODE = "PANEL_SORTED_BY_SYMBOL_WITHOUT_ROW_OFFSET_INDEX_REQUIRES_SEALED_HOLDOUT_SCAN_TO_REACH_LATER_SYMBOL_PRE_HOLDOUT_ROWS"


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


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


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
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "preregistration": PREREG,
        "config_bounds": CONFIG_BOUNDS,
        "prereg_approval": PREREG_APPROVAL,
        "registry": REGISTRY,
        "split_policy": SPLIT_POLICY,
        "access_rules": ACCESS_RULES,
        "pipeline_summary": PIPELINE_SUMMARY,
        "build_summary": BUILD_SUMMARY,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def inspect_panel_layout(panel_path: Path) -> tuple[bool, str, list[str]]:
    """Read only the header and first two data rows, which are pre-holdout."""
    try:
        with panel_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            first = next(reader, None)
            second = next(reader, None)
    except OSError as exc:
        return False, f"panel header/sample unavailable: {exc}", []
    if first is None or second is None:
        return False, "panel sample unavailable", []
    sample_times = [first.get("hour_open_time_utc", ""), second.get("hour_open_time_utc", "")]
    sample_symbols = [first.get("symbol", ""), second.get("symbol", "")]
    if any(ts >= "2025-11-01T00:00:00Z" for ts in sample_times):
        return False, "panel sample unexpectedly touches sealed holdout boundary", sample_symbols
    if sample_symbols[0] == sample_symbols[1]:
        return True, "first two rows share a symbol; panel is symbol-contiguous at file start", sample_symbols
    return False, "panel start is not symbol-contiguous in first sample", sample_symbols


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    prereg = loaded.get("preregistration", {})
    config = loaded.get("config_bounds", {})
    approval = loaded.get("prereg_approval", {})
    registry = loaded.get("registry", {})
    split = loaded.get("split_policy", {})
    access = loaded.get("access_rules", {})
    pipeline = loaded.get("pipeline_summary", {})
    build = loaded.get("build_summary", {})

    prereg_confirmed = (
        prereg.get("okx_88_symbol_1h_panel_route_family_preregistration_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTERED"
        and prereg.get("route_family_preregistration_performed") is True
        and prereg.get("route_family_selected") == ROUTE_FAMILY
        and prereg.get("allowed_lookback_options") == ",".join(LOOKBACKS)
        and prereg.get("allowed_holding_period_options") == ",".join(HOLDING_PERIODS)
        and prereg.get("route_family_count_max") == 1
        and prereg.get("parameter_grid_count_max") == 12
        and prereg.get("reversal_not_tested_in_first_route") is True
        and prereg.get("momentum_vs_reversal_both_tested") is False
        and prereg.get("replacement_checks_all_true") is True
        and config.get("route_family_selected") == ROUTE_FAMILY
        and config.get("allowed_lookback_options") == LOOKBACKS
        and config.get("allowed_holding_period_options") == HOLDING_PERIODS
        and approval.get("approval_grants_future_restricted_strategy_search_execution_next") is True
    )
    holdout_registry_confirmed = (
        registry.get("okx_88_symbol_1h_panel_holdout_registry_builder_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED"
        and registry.get("holdout_registry_valid_for_this_panel") is True
        and registry.get("sealed_holdout_window_start") == "2025-11-01T00:00:00Z"
        and registry.get("replacement_checks_all_true") is True
        and access.get("sealed_holdout_access_blocked_during_strategy_search") is True
    )
    window_policy_confirmed = (
        split.get("train_development_window_start") == "2023-07-01T00:00:00Z"
        and split.get("train_development_window_end_exclusive") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_start") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_end_exclusive") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_start") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_end_exclusive") == "2026-05-19T00:00:00Z"
    )
    panel_path = Path(str(registry.get("output_file_path") or pipeline.get("output_file") or ""))
    panel_exists = panel_path.is_file()
    symbol_contiguous, panel_layout_reason, panel_sample_symbols = inspect_panel_layout(panel_path) if panel_exists else (False, "validated 1h panel output missing", [])
    expected_rows_per_symbol = int(build.get("expected_output_rows_per_symbol_1h") or 0)
    row_offset_index_available = False
    safe_pre_holdout_read_available = False
    exact_blocker = None
    if not prereg_confirmed:
        exact_blocker = "ROUTE_PREREGISTRATION_MISSING_OR_INVALID"
    elif not holdout_registry_confirmed:
        exact_blocker = "HOLDOUT_REGISTRY_MISSING_OR_INVALID"
    elif not window_policy_confirmed:
        exact_blocker = "HOLDOUT_WINDOW_POLICY_MISSING_OR_INVALID"
    elif not panel_exists:
        exact_blocker = "VALIDATED_1H_PANEL_OUTPUT_MISSING"
    elif symbol_contiguous and expected_rows_per_symbol > 0 and not row_offset_index_available:
        exact_blocker = BLOCKER_CODE
    elif not safe_pre_holdout_read_available:
        exact_blocker = "SAFE_PRE_HOLDOUT_READ_PATH_NOT_AVAILABLE"

    blocked = exact_blocker is not None
    status = BLOCKED_STATUS if blocked else PASS_STATUS
    next_module = NEXT_BLOCKED_MODULE if blocked else NEXT_PASS_MODULE
    quality = BLOCKED_QUALITY if blocked else PASS_QUALITY

    configs = [{"lookback": lookback, "holding_period": holding} for lookback in LOOKBACKS for holding in HOLDING_PERIODS]
    no_forbidden_actions = {
        "aggregation_performed_now": False,
        "data_build_performed": False,
        "data_download_performed": False,
        "edge_claim_performed": False,
        "family_release_performed": False,
        "original_source_full_csv_read_performed": False,
        "sealed_holdout_accessed": False,
        "strategy_search_executed": False,
    }
    release_blocks = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
    }
    replacement_checks = {
        "allowed_holding_periods_exact": HOLDING_PERIODS == ["1h", "3h", "6h"],
        "allowed_lookbacks_exact_no_72h": LOOKBACKS == ["6h", "12h", "24h", "48h"] and "72h" not in LOOKBACKS,
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "execution_blocked_before_sealed_holdout_read": blocked and no_forbidden_actions["sealed_holdout_accessed"] is False,
        "holdout_registry_confirmed": holdout_registry_confirmed,
        "no_candidate_generation": release_blocks["candidate_generation_allowed_now"] is False and no_forbidden_actions.get("candidate_generation_performed", False) is False,
        "no_edge_claim": release_blocks["edge_claim_allowed_now"] is False and no_forbidden_actions["edge_claim_performed"] is False,
        "no_original_1m_source_read": no_forbidden_actions["original_source_full_csv_read_performed"] is False,
        "no_reversal_tested": True,
        "no_sealed_holdout_access": no_forbidden_actions["sealed_holdout_accessed"] is False,
        "parameter_grid_count_exact": len(configs) == 12,
        "preregistration_confirmed": prereg_confirmed,
        "repo_clean_except_current_tool": repo_clean,
        "window_policy_confirmed": window_policy_confirmed,
    }
    replacement_checks_all_true = False if blocked else all(replacement_checks.values()) and not load_errors

    report = {
        "active_p0_blocker_count": 1 if blocked else 0,
        "active_p1_attention_count": 0,
        "blocked_reason": exact_blocker,
        "bucket_count_rule": "bucket_count=floor(eligible_symbol_count*0.20), minimum 5, skip timestamp if below 5",
        "bucket_fraction": 0.20,
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "config_metrics_created": False,
        "cost_slippage_policy_required": True,
        "current_evidence_chain_quality_after_execution": quality,
        "eligible_symbol_count": 88 if panel_exists else 0,
        "fee_bps_per_side": 5,
        "gross_metrics_created": False,
        "holding_period_options_used": ",".join(HOLDING_PERIODS),
        "holdout_registry_confirmed": holdout_registry_confirmed,
        "incomplete_hour_policy_applied": False,
        "lookback_options_used": ",".join(LOOKBACKS),
        "monthly_stability_created": False,
        "momentum_vs_reversal_compared": False,
        "net_cost_adjusted_metrics_created": False,
        "next_module": next_module,
        "no_lookahead_policy_applied": False,
        "null_baseline_complete": False,
        "null_baseline_created": False,
        "null_model_type": None,
        "null_run_count": 0,
        "okx_88_symbol_1h_panel_restricted_strategy_search_execution_status": status,
        "output_valid_for_edge_claim": False,
        "parameter_grid_count_max": 12,
        "panel_layout_reason": panel_layout_reason,
        "panel_sample_symbols": panel_sample_symbols,
        "portfolio_definition_locked": True,
        "release_blocks_created": True,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "restricted_strategy_search_execution_performed": False if blocked else True,
        "reversal_tested": False,
        "route_family_count": 1,
        "route_family_selected": ROUTE_FAMILY,
        "route_preregistration_confirmed": prereg_confirmed,
        "round_trip_cost_bps": 20,
        "sealed_holdout_accessed": False,
        "sealed_holdout_rows_read_count": 0,
        "sealed_holdout_window_used": False,
        "signal_entry_delay_applied": False,
        "skipped_incomplete_rows_count": 0,
        "slippage_bps_per_side": 5,
        "tested_config_count": 0 if blocked else len(configs),
        "train_development_row_count": 0,
        "train_development_window_used": False,
        "tracked_python_count_at_execution_run": tracked_python_count(),
        "turnover_concentration_created": False,
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
        "validation_row_count": 0,
        "validation_window_used": False,
    }
    report.update(no_forbidden_actions)
    report.update(release_blocks)

    access_log = {
        "blocked_before_panel_strategy_read": blocked,
        "exact_blocker": exact_blocker,
        "full_1h_panel_read_performed": False,
        "original_source_full_csv_read_performed": False,
        "panel_header_and_two_pre_holdout_sample_rows_read": panel_exists,
        "panel_path": str(panel_path) if panel_path else None,
        "row_offset_index_available": row_offset_index_available,
        "safe_pre_holdout_read_available": safe_pre_holdout_read_available,
        "sealed_holdout_accessed": False,
        "sealed_holdout_rows_read_count": 0,
        "symbol_contiguous_layout_detected": symbol_contiguous,
    }
    null_diagnostics = {
        "blocked_reason": exact_blocker,
        "null_baseline_complete": False,
        "null_baseline_created": False,
        "null_model_type": None,
        "null_run_count": 0,
        "sealed_holdout_accessed": False,
    }
    cost_sensitivity = {
        "blocked_reason": exact_blocker,
        "fee_bps_per_side": 5,
        "gross_only_interpretation_allowed": False,
        "net_cost_adjusted_metrics_created": False,
        "round_trip_cost_bps": 20,
        "slippage_bps_per_side": 5,
    }
    turnover_concentration = {
        "blocked_reason": exact_blocker,
        "symbol_exposure_concentration_created": False,
        "turnover_concentration_created": False,
    }
    release_blocks_payload = {
        "candidate_generation_allowed_now": False,
        "candidate_generation_performed": False,
        "edge_claim_allowed_now": False,
        "edge_claim_performed": False,
        "family_release_allowed_now": False,
        "family_release_performed": False,
        "output_valid_for_edge_claim": False,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
    }
    execution_summary = {
        "blocked_reason": exact_blocker,
        "current_evidence_chain_quality_after_execution": quality,
        "next_module": next_module,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
    }
    self_validator = {
        "created_at_utc": now_utc(),
        "expected_head": EXPECTED_HEAD,
        "latest_head_at_run": head,
        "output_dir": str(OUTPUT_DIR),
        "required_artifacts": list(output_payloads(report, null_diagnostics, cost_sensitivity, turnover_concentration, access_log, release_blocks_payload, execution_summary, self_validator_placeholder={}).keys()),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
        "tool_path": str(REPO / TOOL_REL),
    }

    return {
        "report": report,
        "null_diagnostics": null_diagnostics,
        "cost_sensitivity": cost_sensitivity,
        "turnover_concentration": turnover_concentration,
        "access_log": access_log,
        "release_blocks": release_blocks_payload,
        "execution_summary": execution_summary,
        "self_validator": self_validator,
    }


def output_payloads(
    report: dict[str, Any],
    null_diagnostics: dict[str, Any],
    cost_sensitivity: dict[str, Any],
    turnover_concentration: dict[str, Any],
    access_log: dict[str, Any],
    release_blocks: dict[str, Any],
    execution_summary: dict[str, Any],
    self_validator_placeholder: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_report.json": report,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_null_diagnostics.json": null_diagnostics,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_cost_sensitivity.json": cost_sensitivity,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_turnover_concentration.json": turnover_concentration,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_data_window_access_log.json": access_log,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_release_blocks.json": release_blocks,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_summary.json": execution_summary,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_self_validator.json": self_validator_placeholder,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payloads = output_payloads(
        outputs["report"],
        outputs["null_diagnostics"],
        outputs["cost_sensitivity"],
        outputs["turnover_concentration"],
        outputs["access_log"],
        outputs["release_blocks"],
        outputs["execution_summary"],
        outputs["self_validator"],
    )
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)
    write_csv(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_config_metrics.csv",
        [],
        [
            "route_family",
            "lookback",
            "holding_period",
            "window",
            "gross_return",
            "net_return",
            "turnover",
            "blocked_reason",
        ],
    )
    write_csv(
        OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_monthly_stability.csv",
        [],
        [
            "route_family",
            "lookback",
            "holding_period",
            "window",
            "month",
            "gross_return",
            "net_return",
            "blocked_reason",
        ],
    )


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["report"], indent=2, sort_keys=True))
    return 0 if outputs["report"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
