#!/usr/bin/env python3
"""Repo-only strategy-search preview after OKX 88-symbol 1h holdout registry.

This module creates a preview/contract only. It does not execute strategy
search, generate candidates, optimize parameters, access sealed holdout, claim
edge, full-read the 1h panel, read original 1m sources, download, browse, call
APIs, build data, aggregate data, or touch runtime/live/capital.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_strategy_search_preview_after_holdout_registry_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_strategy_search_preview_after_holdout_registry_v1"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
SPLIT_POLICY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_split_policy.json"
ACCESS_RULES = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_access_rules.json"
REGISTRY_LIMITATIONS = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry_limitations.json"
REGISTRY_APPROVAL = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview_approval_record.json"

EXPECTED_HEAD = "fb04fef"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_STRATEGY_SEARCH_PREVIEW_READY"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_STRATEGY_SEARCH_PREVIEW_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_strategy_search_preview_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_STRATEGY_SEARCH_PREVIEW_READY_ROUTE_FAMILY_PREREGISTRATION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_STRATEGY_SEARCH_PREVIEW_BLOCKED_REVIEW_REQUIRED"

FUTURE_STRATEGY_SEARCH_CLASS = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_BASELINE_STRATEGY_SEARCH_V1"
THEORY_PRIOR_SUMMARY = (
    "At 1h bar frequency on crypto perpetual swaps, cross-sectional momentum is the more defensible first baseline "
    "than reversal because sub-hour reversal is more closely tied to microstructure/bid-ask/liquidity bounce, while "
    "1h bars are better aligned with trend/herding/continuation mechanisms. This is a prior only, not evidence of "
    "profitability on this panel."
)


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
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(TOOL_REL.as_posix())]
    return not unexpected, unexpected


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    for label, path in {
        "registry": REGISTRY,
        "split_policy": SPLIT_POLICY,
        "access_rules": ACCESS_RULES,
        "registry_limitations": REGISTRY_LIMITATIONS,
        "registry_approval": REGISTRY_APPROVAL,
    }.items():
        try:
            loaded[label] = read_json(path)
        except (OSError, json.JSONDecodeError, RuntimeError) as exc:
            errors[label] = f"{path}: {exc}"
    return loaded, errors


def build_outputs() -> dict[str, Any]:
    head = git(["rev-parse", "--short", "HEAD"])
    repo_clean, unexpected_status = clean_status_allowing_tool()
    loaded, load_errors = load_inputs()
    registry = loaded.get("registry", {})
    split = loaded.get("split_policy", {})
    access = loaded.get("access_rules", {})
    limitations = loaded.get("registry_limitations", {})
    approval = loaded.get("registry_approval", {})

    holdout_registry_confirmed = (
        registry.get("okx_88_symbol_1h_panel_holdout_registry_builder_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED"
        and registry.get("replacement_checks_all_true") is True
        and registry.get("holdout_registry_created") is True
        and registry.get("holdout_registry_valid_for_this_panel") is True
        and registry.get("holdout_registry_valid_for_strategy_search_governance") is True
        and registry.get("true_untouched_final_holdout_claimed") is False
        and registry.get("diagnostic_exposure_recorded") is True
        and registry.get("valid_for_final_edge_claim") is False
        and registry.get("final_edge_claim_requires_external_or_future_holdout") is True
        and registry.get("future_strategy_search_preview_allowed_next") is True
        and approval.get("approval_grants_future_strategy_search_preview_next") is True
    )
    holdout_policy_confirmed = (
        split.get("train_development_window_start") == "2023-07-01T00:00:00Z"
        and split.get("train_development_window_end_exclusive") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_start") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_end_exclusive") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_start") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_end_exclusive") == "2026-05-19T00:00:00Z"
        and split.get("split_boundaries_deterministic") is True
        and split.get("split_boundaries_return_optimized") is False
        and access.get("sealed_holdout_access_blocked_during_strategy_search") is True
        and access.get("holdout_access_requires_pre_registered_freeze") is True
        and access.get("holdout_access_logging_required") is True
    )
    panel_identity_confirmed = (
        registry.get("selected_symbol_count") == 88
        and registry.get("output_1h_row_count") == 2223936
        and registry.get("complete_1h_row_count") == 2223843
        and registry.get("incomplete_1h_row_count") == 93
    )
    final_holdout_nuance_preserved = (
        registry.get("true_untouched_final_holdout_claimed") is False
        and limitations.get("true_untouched_final_holdout_claimed") is False
        and registry.get("valid_for_final_edge_claim") is False
        and limitations.get("valid_for_final_edge_claim") is False
        and registry.get("diagnostic_exposure_recorded") is True
        and registry.get("final_edge_claim_requires_external_or_future_holdout") is True
    )

    route_family_requirement = {
        "future_preregistration_module_must_choose_exactly_one_route_family": True,
        "momentum_vs_reversal_both_tested_now": False,
        "one_route_family_only": True,
        "reversal_not_tested_in_first_route": True,
        "route_family_choice_locked_before_execution": True,
        "route_family_choice_performance_free": True,
        "route_family_count_max": 1,
        "route_family_preregistration_required": True,
        "route_family_selected_now": False,
        "selection_must_not_use_extreme_return_distribution_for_alpha_choice": True,
        "selection_must_not_use_okx_88_panel_returns": True,
        "selection_must_not_use_train_validation_or_holdout_performance": True,
        "strategy_search_execution_allowed_next": False,
        "strategy_search_execution_allowed_now": False,
    }
    theory_prior = {
        "preferred_first_route_family_theory_prior": "CROSS_SECTIONAL_MOMENTUM_BASELINE",
        "rejected_alternative_route_family": "CROSS_SECTIONAL_REVERSAL_BASELINE",
        "selection_basis": "PERFORMANCE_FREE_THEORETICAL_PRIOR",
        "selection_must_not_use_extreme_return_distribution_for_alpha_choice": True,
        "selection_must_not_use_okx_88_panel_returns": True,
        "selection_must_not_use_train_validation_or_holdout_performance": True,
        "theory_prior_not_based_on_okx_panel_performance": True,
        "theory_prior_not_edge_claim": True,
        "theory_prior_recorded": True,
        "theory_prior_source": "PERFORMANCE_FREE_MARKET_STRUCTURE_PRIOR",
        "theory_prior_summary": THEORY_PRIOR_SUMMARY,
    }
    holdout_policy = {
        "holdout_access_logging_required": True,
        "holdout_access_requires_pre_registered_freeze": True,
        "sealed_holdout_access_allowed_now": False,
        "sealed_holdout_access_blocked_during_strategy_search": True,
        "sealed_holdout_accessed": False,
        "sealed_holdout_window_end_exclusive": split.get("sealed_holdout_window_end_exclusive"),
        "sealed_holdout_window_start": split.get("sealed_holdout_window_start"),
        "strategy_search_fail_closed_on_early_holdout_access": True,
        "train_development_window_end_exclusive": split.get("train_development_window_end_exclusive"),
        "train_development_window_start": split.get("train_development_window_start"),
        "validation_window_end_exclusive": split.get("validation_window_end_exclusive"),
        "validation_window_start": split.get("validation_window_start"),
    }
    route_budget = {
        "every_tested_parameter_counted_in_ledger": True,
        "holding_period_options_max": 3,
        "no_objective_driven_route_switching_after_results": True,
        "no_repeated_search_loops_without_new_approval": True,
        "no_symbol_specific_parameter_optimization": True,
        "parameter_grid_count_max": 12,
        "route_budget_created": True,
        "route_config_hash_recorded_before_execution_required": True,
        "route_family_count_max": 1,
        "timeframe_fixed": "1h",
        "universe_scope_fixed_symbol_count": 88,
    }
    null_validation = {
        "cost_slippage_policy_required": True,
        "external_second_source_validation_future_work_recorded": True,
        "incomplete_hour_policy_required": True,
        "monthly_stability_reporting_required": True,
        "naive_benchmark_comparison_required": True,
        "no_lookahead_policy_required": True,
        "no_sealed_holdout_results": True,
        "null_baseline_required": True,
        "okx_only_limitation_disclosure_required": True,
        "shuffled_label_or_block_bootstrap_null_required": True,
        "survivorship_limitation_disclosure_required": True,
        "train_development_results_separated_from_validation_results": True,
        "turnover_concentration_reporting_required": True,
    }
    cost_slippage = {
        "cost_slippage_policy_required": True,
        "gross_only_edge_claim_forbidden": True,
        "maker_fee_assumption_required": True,
        "no_profitability_claim_without_cost_adjusted_analysis": True,
        "slippage_assumption_required": True,
        "taker_fee_assumption_required": True,
        "turnover_adjusted_net_performance_required": True,
    }
    release_blocks = {
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "strategy_search_allowed_now": False,
    }
    approvals = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_future_restricted_strategy_search_execution_next": False,
        "approval_grants_future_route_family_preregistration_next": True,
        "approval_grants_holdout_access_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "approval_grants_strategy_search_preview_now": True,
        "next_module": NEXT_PASS_MODULE,
    }

    replacement_checks = {
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "final_holdout_nuance_preserved": final_holdout_nuance_preserved,
        "holdout_policy_confirmed": holdout_policy_confirmed,
        "holdout_registry_confirmed": holdout_registry_confirmed,
        "no_candidate_generation_now": True,
        "no_edge_claim_now": True,
        "no_forbidden_download_api_browse_build_aggregation": True,
        "no_full_1h_panel_read": True,
        "no_original_1m_source_read": True,
        "no_strategy_search_execution_now": True,
        "panel_identity_confirmed": panel_identity_confirmed,
        "repo_clean_except_current_tool": repo_clean,
        "route_family_preregistration_required": route_family_requirement["route_family_preregistration_required"] is True,
        "route_family_selected_now_false": route_family_requirement["route_family_selected_now"] is False,
        "strategy_search_execution_allowed_next_false": route_family_requirement["strategy_search_execution_allowed_next"] is False,
        "theory_prior_performance_free": theory_prior["theory_prior_not_based_on_okx_panel_performance"] is True,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY
    approvals["next_module"] = next_module
    if not replacement_checks_all_true:
        approvals["approval_grants_future_route_family_preregistration_next"] = False
        approvals["approval_grants_strategy_search_preview_now"] = False

    preview = {
        **route_family_requirement,
        **theory_prior,
        **holdout_policy,
        **route_budget,
        **null_validation,
        **cost_slippage,
        **release_blocks,
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 0 if replacement_checks_all_true else 1,
        "aggregation_performed_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_future_restricted_strategy_search_execution_next": False,
        "approval_grants_future_route_family_preregistration_next": approvals[
            "approval_grants_future_route_family_preregistration_next"
        ],
        "approval_grants_holdout_access_now": False,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "candidate_generation_performed": False,
        "complete_1h_row_count": registry.get("complete_1h_row_count"),
        "current_evidence_chain_quality_after_preview": quality,
        "data_build_performed": False,
        "data_download_performed": False,
        "diagnostic_exposure_recorded": registry.get("diagnostic_exposure_recorded"),
        "edge_claim_performed": False,
        "final_edge_claim_requires_external_or_future_holdout": registry.get("final_edge_claim_requires_external_or_future_holdout"),
        "full_1h_panel_read_performed": False,
        "future_route_family_preregistration_allowed_next": replacement_checks_all_true,
        "future_strategy_search_class": FUTURE_STRATEGY_SEARCH_CLASS,
        "holdout_registry_confirmed": holdout_registry_confirmed,
        "holdout_registry_valid_for_strategy_search_governance": registry.get("holdout_registry_valid_for_strategy_search_governance"),
        "holdout_registry_valid_for_this_panel": registry.get("holdout_registry_valid_for_this_panel"),
        "incomplete_1h_row_count": registry.get("incomplete_1h_row_count"),
        "next_module": next_module,
        "okx_88_symbol_1h_panel_strategy_search_preview_status": status,
        "original_source_full_csv_read_performed": False,
        "output_1h_row_count": registry.get("output_1h_row_count"),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "runtime_live_capital_allowed_now": False,
        "sealed_holdout_accessed": False,
        "selected_symbol_count": registry.get("selected_symbol_count"),
        "strategy_search_executed": False,
        "strategy_search_preview_created": replacement_checks_all_true,
        "true_untouched_final_holdout_claimed": registry.get("true_untouched_final_holdout_claimed"),
        "valid_for_final_edge_claim": registry.get("valid_for_final_edge_claim"),
        "tracked_python_count_at_preview_run": tracked_python_count(),
    }
    if load_errors:
        preview["input_artifact_errors"] = load_errors

    contract = {
        "future_strategy_search_class": FUTURE_STRATEGY_SEARCH_CLASS,
        "no_execution_in_this_module": True,
        "route_family_preregistration_required_before_execution": True,
        "strategy_search_execution_allowed_next": False,
        "strategy_search_execution_allowed_now": False,
    }
    self_validator = {
        "created_at_utc": now_utc(),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "required_output_artifacts": [],
        "unexpected_git_status_entries": unexpected_status,
    }
    return {
        "approvals": approvals,
        "contract": contract,
        "cost_slippage": cost_slippage,
        "holdout_policy": holdout_policy,
        "null_validation": null_validation,
        "preview": preview,
        "release_blocks": release_blocks,
        "route_budget": route_budget,
        "route_family_requirement": route_family_requirement,
        "self_validator": self_validator,
        "theory_prior": theory_prior,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    preview_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview.json"
    contract_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview_contract.json"
    route_req_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration_requirement.json"
    theory_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_theory_prior_for_route_family_selection.json"
    holdout_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_holdout_access_policy.json"
    budget_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_route_budget.json"
    null_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_null_validation_requirements.json"
    cost_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_cost_slippage_requirements.json"
    blocks_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_release_blocks.json"
    approval_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration_approval_record.json"
    validator_path = OUTPUT_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview_self_validator.json"

    write_json(preview_path, outputs["preview"])
    write_json(contract_path, outputs["contract"])
    write_json(route_req_path, outputs["route_family_requirement"])
    write_json(theory_path, outputs["theory_prior"])
    write_json(holdout_path, outputs["holdout_policy"])
    write_json(budget_path, outputs["route_budget"])
    write_json(null_path, outputs["null_validation"])
    write_json(cost_path, outputs["cost_slippage"])
    write_json(blocks_path, outputs["release_blocks"])
    write_json(approval_path, outputs["approvals"])
    artifact_paths = [
        preview_path,
        contract_path,
        route_req_path,
        theory_path,
        holdout_path,
        budget_path,
        null_path,
        cost_path,
        blocks_path,
        approval_path,
        validator_path,
    ]
    outputs["self_validator"]["required_output_artifacts"] = [str(path) for path in artifact_paths]
    outputs["self_validator"]["required_output_artifacts_exist"] = {str(path): path.exists() for path in artifact_paths[:-1]}
    write_json(validator_path, outputs["self_validator"])


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["preview"], indent=2, sort_keys=True))
    return 0 if outputs["preview"]["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
