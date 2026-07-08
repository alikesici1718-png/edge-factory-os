#!/usr/bin/env python3
"""Repo-only restricted strategy-search retry preview after finalization.

This module binds the preregistered CROSS_SECTIONAL_MOMENTUM_BASELINE contract
to the finalized revised non-holdout view. It does not read panel rows for
returns, execute strategy search, generate candidates, claim edge, access
sealed holdout, build data, aggregate, or modify tracked files.
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
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_after_revised_non_holdout_view_finalization_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_after_revised_non_holdout_view_finalization_v1"
)

EXPECTED_HEAD = "a37d511d5f65b64f0932df1ad416597a54957d7e"
FINALIZE_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_after_forensic_validation_v1"
)
FINAL_MANIFEST = FINALIZE_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_manifest.json"
FINAL_SCHEMA = FINALIZE_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_schema_binding.json"
FINAL_PROVENANCE = FINALIZE_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_provenance.json"
FINAL_ELIGIBILITY = FINALIZE_DIR / "repo_only_okx_88_symbol_1h_panel_revised_non_holdout_final_eligibility_record.json"
VALIDATION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_after_preview_v1"
)
VALIDATION_REPORT = (
    VALIDATION_DIR
    / "repo_only_okx_88_symbol_1h_panel_revised_partial_output_forensic_validation_execution_report.json"
)
ROUTE_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1"
)
ROUTE_PREREG = ROUTE_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration.json"
ROUTE_BOUNDS = ROUTE_DIR / "repo_only_okx_88_symbol_1h_panel_cross_sectional_momentum_baseline_config_bounds.json"
STRATEGY_PREVIEW_DIR = (
    EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_strategy_search_preview_after_holdout_registry_v1"
)
STRATEGY_PREVIEW = STRATEGY_PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview.json"
HOLDOUT_REGISTRY_DIR = (
    EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
)
HOLDOUT_REGISTRY = HOLDOUT_REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
HOLDOUT_ACCESS_RULES = HOLDOUT_REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_access_rules.json"
BLOCKED_EXECUTION_DIR = (
    EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_blocked_record_v1"
)
BLOCKED_EXECUTION_APPROVAL = (
    BLOCKED_EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_approval_record.json"
)
HOLDOUT_SAFE_ACCESS_DIR = (
    EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan_after_blocked_strategy_execution_v1"
)
HOLDOUT_SAFE_ACCESS_PLAN = HOLDOUT_SAFE_ACCESS_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_safe_access_plan.json"

PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_PREVIEW_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_PREVIEW_REVIEW_REQUIRED"
NEXT_PASS_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_after_revised_non_holdout_view_preview_v1.py"
)
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_PREVIEW_READY_EXECUTION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_PREVIEW_BLOCKED_REVIEW_REQUIRED"

EXPECTED_FINALIZE_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FINALIZE_MANIFEST_COMPLETE"
EXPECTED_ROUTE_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTERED"
ROUTE_FAMILY = "CROSS_SECTIONAL_MOMENTUM_BASELINE"
REJECTED_ROUTE = "CROSS_SECTIONAL_REVERSAL_BASELINE"
LOOKBACKS = ["6h", "12h", "24h", "48h"]
HOLDING_PERIODS = ["1h", "3h", "6h"]
LOOKBACKS_TEXT = "6h,12h,24h,48h"
HOLDING_PERIODS_TEXT = "1h,3h,6h"

PANEL_START = "2023-07-01T00:00:00Z"
PANEL_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
PANEL_MAX_TIMESTAMP = "2025-10-31T15:00:00Z"
TRAIN_START = "2023-07-01T00:00:00Z"
TRAIN_END_EXCLUSIVE = "2025-01-01T00:00:00Z"
VALIDATION_START = "2025-01-01T00:00:00Z"
VALIDATION_END_EXCLUSIVE = "2025-10-31T16:00:00Z"
BOUNDARY_BUFFER_START = "2025-10-31T16:00:00Z"
BOUNDARY_BUFFER_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
SEALED_HOLDOUT_START = "2025-11-01T00:00:00Z"
SEALED_HOLDOUT_END_EXCLUSIVE = "2026-05-19T00:00:00Z"


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def clean_status_allowing_tool() -> tuple[bool, list[str]]:
    lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_suffix = TOOL_REL.as_posix()
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(allowed_suffix)]
    return not unexpected, unexpected


def load_input(label: str, path: Path, errors: dict[str, str]) -> dict[str, Any]:
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        errors[label] = f"{path}: {exc}"
        return {}


def file_metadata(path_text: Any) -> dict[str, Any]:
    if not isinstance(path_text, str) or not path_text:
        return {"exists": False, "metadata_error": "missing path text", "path": path_text}
    path = Path(path_text)
    try:
        stat = path.stat()
    except OSError as exc:
        return {"exists": False, "metadata_error": str(exc), "path": str(path)}
    modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0)
    return {
        "exists": path.is_file(),
        "modified_time": modified.isoformat().replace("+00:00", "Z"),
        "path": str(path),
        "size_bytes": stat.st_size,
    }


def final_manifest_confirmed(manifest: dict[str, Any]) -> bool:
    return (
        manifest.get("okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_status") == EXPECTED_FINALIZE_STATUS
        and manifest.get("finalize_manifest_performed") is True
        and manifest.get("forensic_validation_confirmed") is True
        and manifest.get("final_manifest_created") is True
        and manifest.get("final_schema_binding_created") is True
        and manifest.get("final_provenance_created") is True
        and manifest.get("final_eligibility_record_created") is True
        and manifest.get("output_valid_for_strategy_search_after_finalization") is True
        and manifest.get("output_valid_for_restricted_momentum_search_input") is True
        and manifest.get("output_valid_for_edge_claim") is False
        and manifest.get("output_valid_for_final_edge_claim") is False
        and manifest.get("output_valid_for_runtime_or_live") is False
        and manifest.get("strategy_search_allowed_now") is False
        and manifest.get("future_restricted_strategy_search_retry_preview_allowed_next") is True
        and manifest.get("output_1h_row_count") == 1_802_944
        and manifest.get("output_symbol_count") == 88
        and manifest.get("expected_rows_per_symbol") == 20_488
        and manifest.get("duplicate_symbol_hour_count") == 0
        and manifest.get("complete_1h_row_count") == 1_802_935
        and manifest.get("incomplete_1h_row_count") == 9
        and manifest.get("revised_non_holdout_view_start") == PANEL_START
        and manifest.get("revised_non_holdout_view_end_exclusive") == PANEL_END_EXCLUSIVE
        and manifest.get("output_max_timestamp") == PANEL_MAX_TIMESTAMP
        and manifest.get("boundary_buffer_rows_written_count") == 0
        and manifest.get("sealed_holdout_rows_written_count") == 0
        and manifest.get("replacement_checks_all_true") is True
        and manifest.get("next_module") == TOOL_REL.name
    )


def route_preregistration_confirmed(prereg: dict[str, Any], bounds: dict[str, Any]) -> bool:
    return (
        prereg.get("okx_88_symbol_1h_panel_route_family_preregistration_status") == EXPECTED_ROUTE_STATUS
        and prereg.get("route_family_selected") == ROUTE_FAMILY
        and prereg.get("route_family_rejected_for_first_route") == REJECTED_ROUTE
        and prereg.get("route_family_selection_basis") == "PERFORMANCE_FREE_THEORETICAL_PRIOR"
        and prereg.get("one_route_family_only") is True
        and prereg.get("reversal_not_tested_in_first_route") is True
        and prereg.get("route_family_choice_locked_before_execution") is True
        and prereg.get("allowed_lookback_options") == LOOKBACKS_TEXT
        and prereg.get("allowed_holding_period_options") == HOLDING_PERIODS_TEXT
        and prereg.get("parameter_grid_count_max") == 12
        and prereg.get("route_family_count_max") == 1
        and prereg.get("sealed_holdout_access_blocked_during_strategy_search") is True
        and prereg.get("replacement_checks_all_true") is True
        and bounds.get("route_family_selected") == ROUTE_FAMILY
        and bounds.get("allowed_lookback_options") == LOOKBACKS
        and bounds.get("allowed_holding_period_options") == HOLDING_PERIODS
        and bounds.get("parameter_grid_count_max") == 12
        and bounds.get("future_execution_must_not_execute_reversal") is True
        and bounds.get("no_symbol_specific_parameter_tuning") is True
    )


def build_outputs() -> dict[str, dict[str, Any]]:
    head = git(["rev-parse", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    load_errors: dict[str, str] = {}
    manifest = load_input("final_manifest", FINAL_MANIFEST, load_errors)
    schema = load_input("final_schema_binding", FINAL_SCHEMA, load_errors)
    provenance = load_input("final_provenance", FINAL_PROVENANCE, load_errors)
    eligibility = load_input("final_eligibility", FINAL_ELIGIBILITY, load_errors)
    validation = load_input("forensic_validation_execution", VALIDATION_REPORT, load_errors)
    prereg = load_input("route_family_preregistration", ROUTE_PREREG, load_errors)
    bounds = load_input("route_family_config_bounds", ROUTE_BOUNDS, load_errors)
    strategy_preview = load_input("strategy_search_preview", STRATEGY_PREVIEW, load_errors)
    holdout_registry = load_input("holdout_registry", HOLDOUT_REGISTRY, load_errors)
    holdout_access_rules = load_input("holdout_access_rules", HOLDOUT_ACCESS_RULES, load_errors)
    blocked_execution = load_input("blocked_strategy_execution_context", BLOCKED_EXECUTION_APPROVAL, load_errors)
    holdout_safe_access = load_input("holdout_safe_access_plan", HOLDOUT_SAFE_ACCESS_PLAN, load_errors)

    panel_metadata = file_metadata(manifest.get("output_file_path"))
    final_ok = final_manifest_confirmed(manifest)
    forensic_ok = manifest.get("forensic_validation_confirmed") is True and validation.get("partial_output_forensic_validation_passed") is True
    route_ok = route_preregistration_confirmed(prereg, bounds)
    all_context_loaded = all(
        bool(item)
        for item in [
            schema,
            provenance,
            eligibility,
            strategy_preview,
            holdout_registry,
            holdout_access_rules,
            blocked_execution,
            holdout_safe_access,
        ]
    )

    approval = {
        "approval_grants_retry_preview_now": True,
        "approval_grants_future_restricted_strategy_search_retry_execution_next": True,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_holdout_access_now": False,
        "approval_grants_build_rerun_now": False,
    }
    action_state = {
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "finalized_panel_rows_read_for_returns": False,
        "current_all_in_one_panel_read_performed": False,
        "original_source_full_csv_read_performed": False,
        "strategy_search_executed": False,
        "candidate_generation_performed": False,
        "edge_claim_performed": False,
    }
    execution_guards = {
        "future_execution_must_use_finalized_revised_non_holdout_view": True,
        "future_execution_must_not_use_current_all_in_one_panel": True,
        "future_execution_must_not_use_original_source_data": True,
        "future_execution_must_not_access_holdout": True,
        "future_execution_must_not_use_boundary_buffer": True,
        "future_execution_must_not_use_binance_or_second_source_data": True,
        "future_execution_must_execute_exactly_12_preregistered_momentum_configs": True,
        "future_execution_must_separate_train_development_and_validation_metrics": True,
        "future_execution_must_apply_no_lookahead_signal_entry_delay": True,
        "future_execution_must_handle_incomplete_hours_according_to_policy": True,
        "future_execution_must_apply_conservative_cost_slippage_diagnostics": True,
        "future_execution_must_run_null_baseline_diagnostics": True,
        "future_execution_must_compute_monthly_stability": True,
        "future_execution_must_compute_turnover_and_concentration": True,
        "future_execution_must_produce_release_blocked_diagnostic_report": True,
    }
    cost_policy = {
        "fee_bps_per_side": 5,
        "slippage_bps_per_side": 5,
        "total_cost_bps_per_side": 10,
        "round_trip_cost_bps": 20,
        "turnover_adjusted_net_metrics_required": True,
        "gross_only_interpretation_allowed": False,
    }
    null_stability_policy = {
        "null_baseline_required": True,
        "minimum_null_runs": 100,
        "monthly_stability_reporting_required": True,
        "turnover_concentration_reporting_required": True,
        "no_lookahead_policy_required": True,
        "incomplete_hour_policy_required": True,
    }

    replacement_checks = {
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "repo_clean_except_current_tool": repo_clean,
        "finalized_revised_non_holdout_view_confirmed": final_ok,
        "forensic_validation_confirmed": forensic_ok,
        "final_manifest_context_loaded": all_context_loaded,
        "panel_metadata_available_without_row_read": panel_metadata.get("exists") is True,
        "strategy_search_eligible_after_finalization": manifest.get("output_valid_for_strategy_search_after_finalization") is True,
        "restricted_momentum_input_eligible": manifest.get("output_valid_for_restricted_momentum_search_input") is True,
        "edge_runtime_not_enabled": manifest.get("output_valid_for_edge_claim") is False
        and manifest.get("output_valid_for_final_edge_claim") is False
        and manifest.get("output_valid_for_runtime_or_live") is False,
        "route_preregistration_confirmed": route_ok,
        "lookbacks_exact": prereg.get("allowed_lookback_options") == LOOKBACKS_TEXT,
        "holding_periods_exact": prereg.get("allowed_holding_period_options") == HOLDING_PERIODS_TEXT,
        "strategy_execution_blocked_now": approval["approval_grants_strategy_search_execution_now"] is False,
        "no_panel_return_read": action_state["finalized_panel_rows_read_for_returns"] is False,
        "no_forbidden_source_panel_holdout_reads": (
            action_state["current_all_in_one_panel_read_performed"] is False
            and action_state["original_source_full_csv_read_performed"] is False
            and approval["approval_grants_holdout_access_now"] is False
        ),
        "no_build_or_aggregation": action_state["data_build_performed"] is False
        and action_state["aggregation_performed_now"] is False,
        "no_strategy_candidate_edge": action_state["strategy_search_executed"] is False
        and action_state["candidate_generation_performed"] is False
        and action_state["edge_claim_performed"] is False,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    base = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 0,
        "boundary_buffer_end_exclusive": BOUNDARY_BUFFER_END_EXCLUSIVE,
        "boundary_buffer_rows_written_count": manifest.get("boundary_buffer_rows_written_count"),
        "boundary_buffer_start": BOUNDARY_BUFFER_START,
        "candidate_generation_allowed_now": False,
        "complete_1h_row_count": manifest.get("complete_1h_row_count"),
        "current_evidence_chain_quality_after_retry_preview": quality,
        "duplicate_symbol_hour_count": manifest.get("duplicate_symbol_hour_count"),
        "edge_claim_allowed_now": False,
        "expected_rows_per_symbol": manifest.get("expected_rows_per_symbol"),
        "family_release_allowed_now": False,
        "final_manifest_confirmed": final_ok,
        "finalized_panel_end_exclusive": PANEL_END_EXCLUSIVE,
        "finalized_panel_metadata_only": panel_metadata,
        "finalized_panel_start": PANEL_START,
        "finalized_revised_non_holdout_view_confirmed": final_ok,
        "forensic_validation_confirmed": forensic_ok,
        "future_restricted_strategy_search_retry_execution_allowed_next": replacement_checks_all_true,
        "holding_period_options_allowed": HOLDING_PERIODS_TEXT,
        "incomplete_1h_row_count": manifest.get("incomplete_1h_row_count"),
        "load_errors": load_errors,
        "lookback_options_allowed": LOOKBACKS_TEXT,
        "momentum_vs_reversal_comparison_allowed": False,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_status": status,
        "output_1h_row_count": manifest.get("output_1h_row_count"),
        "output_max_timestamp": manifest.get("output_max_timestamp"),
        "output_valid_for_edge_claim": manifest.get("output_valid_for_edge_claim"),
        "output_valid_for_final_edge_claim": manifest.get("output_valid_for_final_edge_claim"),
        "output_valid_for_restricted_momentum_search_input": manifest.get("output_valid_for_restricted_momentum_search_input"),
        "output_valid_for_runtime_or_live": manifest.get("output_valid_for_runtime_or_live"),
        "output_valid_for_strategy_search_after_finalization": manifest.get(
            "output_valid_for_strategy_search_after_finalization"
        ),
        "parameter_grid_count_max": 12,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "retry_preview_created": replacement_checks_all_true,
        "retry_strategy_search_allowed_now": False,
        "reversal_test_allowed": False,
        "route_family_count_max": 1,
        "route_family_selected": ROUTE_FAMILY,
        "route_preregistration_confirmed": route_ok,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_access_allowed_in_future_execution": False,
        "sealed_holdout_access_allowed_now": False,
        "sealed_holdout_rows_written_count": manifest.get("sealed_holdout_rows_written_count"),
        "sealed_holdout_window_end_exclusive": SEALED_HOLDOUT_END_EXCLUSIVE,
        "sealed_holdout_window_start": SEALED_HOLDOUT_START,
        "selected_symbol_count": manifest.get("selected_symbol_count"),
        "strategy_search_allowed_now": False,
        "strategy_search_execution_allowed_now": False,
        "train_development_window_end_exclusive": TRAIN_END_EXCLUSIVE,
        "train_development_window_start": TRAIN_START,
        "tracked_python_count_at_retry_preview_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_window_end_exclusive": VALIDATION_END_EXCLUSIVE,
        "validation_window_start": VALIDATION_START,
    }
    base.update(approval)
    base.update(action_state)
    base.update(execution_guards)

    contract = {
        **base,
        "allowed_route_family": ROUTE_FAMILY,
        "forbidden_route_families": [REJECTED_ROUTE],
        "forbidden_parameter_expansions": ["72h lookback", "extra holding periods", "symbol-specific parameter tuning"],
        "future_execution_requirements": execution_guards,
        "cost_slippage_policy": cost_policy,
        "null_stability_policy": null_stability_policy,
    }
    input_binding = {
        **base,
        "future_execution_input_path": manifest.get("output_file_path"),
        "future_execution_input_hash": manifest.get("output_hash"),
        "future_execution_input_manifest": str(FINAL_MANIFEST),
        "future_execution_input_schema_binding": str(FINAL_SCHEMA),
        "must_use_finalized_revised_non_holdout_panel_only": True,
    }
    window_policy = {
        **base,
        "panel_window": {"start": PANEL_START, "end_exclusive": PANEL_END_EXCLUSIVE},
        "train_development_window": {"start": TRAIN_START, "end_exclusive": TRAIN_END_EXCLUSIVE},
        "validation_window": {"start": VALIDATION_START, "end_exclusive": VALIDATION_END_EXCLUSIVE},
        "boundary_buffer_window": {"start": BOUNDARY_BUFFER_START, "end_exclusive": BOUNDARY_BUFFER_END_EXCLUSIVE},
        "sealed_holdout_window": {"start": SEALED_HOLDOUT_START, "end_exclusive": SEALED_HOLDOUT_END_EXCLUSIVE},
    }
    route_budget = {
        **base,
        "allowed_lookback_options_list": LOOKBACKS,
        "allowed_holding_period_options_list": HOLDING_PERIODS,
        "total_preregistered_configs_exact": 12,
        "one_route_family_only": True,
        "route_switching_allowed": False,
    }
    release_blocks = {
        **base,
        "candidate_generation_blocked": True,
        "edge_claim_blocked": True,
        "family_release_blocked": True,
        "holdout_access_blocked": True,
        "runtime_live_capital_blocked": True,
        "strategy_execution_blocked_now": True,
    }
    approval_record = {
        **base,
        "approval_scope": "future restricted strategy-search retry execution only",
    }
    self_validator = {
        **base,
        "artifact_count_expected": 8,
        "artifacts_created": [
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_contract.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_input_binding.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_window_policy.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_route_budget.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_release_blocks.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_approval_record.json",
            "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_self_validator.json",
        ],
        "self_validation_created_at_utc": now_utc(),
        "self_validation_result": replacement_checks_all_true,
    }
    return {
        "preview": base,
        "contract": contract,
        "input_binding": input_binding,
        "window_policy": window_policy,
        "route_budget": route_budget,
        "release_blocks": release_blocks,
        "approval": approval_record,
        "self_validator": self_validator,
    }


def write_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    files = {
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview.json": outputs["preview"],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_contract.json": outputs["contract"],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_input_binding.json": outputs[
            "input_binding"
        ],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_window_policy.json": outputs[
            "window_policy"
        ],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_route_budget.json": outputs[
            "route_budget"
        ],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_release_blocks.json": outputs[
            "release_blocks"
        ],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_approval_record.json": outputs[
            "approval"
        ],
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_preview_self_validator.json": outputs[
            "self_validator"
        ],
    }
    for filename, payload in files.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["preview"], indent=2, sort_keys=True))
    return 0 if outputs["preview"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
