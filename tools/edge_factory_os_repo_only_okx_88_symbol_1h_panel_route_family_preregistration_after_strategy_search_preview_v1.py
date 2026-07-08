#!/usr/bin/env python3
"""Repo-only route-family preregistration after OKX 88-symbol 1h preview.

This module locks exactly one first route family for a future restricted
strategy-search execution. It does not execute strategy search, generate
candidates, optimize parameters, access sealed holdout, claim edge, full-read
the 1h panel, read original 1m sources, download, browse, call APIs, build data,
aggregate data, or touch runtime/live/capital.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
TOOL_REL = Path("tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1.py")
OUTPUT_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_after_strategy_search_preview_v1"

PREVIEW_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_strategy_search_preview_after_holdout_registry_v1"
PREVIEW = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview.json"
PREVIEW_CONTRACT = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_strategy_search_preview_contract.json"
PREREG_REQUIREMENT = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration_requirement.json"
THEORY_PRIOR = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_theory_prior_for_route_family_selection.json"
PREVIEW_APPROVAL = PREVIEW_DIR / "repo_only_okx_88_symbol_1h_panel_route_family_preregistration_approval_record.json"

REGISTRY_DIR = EDGE_ROOT / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
REGISTRY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
SPLIT_POLICY = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_split_policy.json"
ACCESS_RULES = REGISTRY_DIR / "repo_only_okx_88_symbol_1h_panel_holdout_access_rules.json"

EXPECTED_HEAD = "0f3e167"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTERED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTRATION_REVIEW_REQUIRED"
NEXT_PASS_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_after_route_preregistration_v1.py"
NEXT_BLOCKED_MODULE = "edge_factory_os_repo_only_okx_88_symbol_1h_panel_route_family_preregistration_blocked_record_v1.py"
PASS_QUALITY = "OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTERED_RESTRICTED_STRATEGY_SEARCH_EXECUTION_NEXT"
BLOCKED_QUALITY = "OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTRATION_BLOCKED_REVIEW_REQUIRED"

SELECTED_ROUTE_FAMILY = "CROSS_SECTIONAL_MOMENTUM_BASELINE"
REJECTED_ROUTE_FAMILY = "CROSS_SECTIONAL_REVERSAL_BASELINE"
SELECTION_BASIS = "PERFORMANCE_FREE_THEORETICAL_PRIOR"
LOOKBACK_BASIS = "PERFORMANCE_FREE_GEOMETRIC_DOUBLING"
ALLOWED_LOOKBACK_OPTIONS = ["6h", "12h", "24h", "48h"]
ALLOWED_HOLDING_PERIOD_OPTIONS = ["1h", "3h", "6h"]
FUTURE_STRATEGY_SEARCH_CLASS = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_BASELINE_STRATEGY_SEARCH_V1"
THEORY_SELECTION_RATIONALE = (
    "At 1h bar frequency on crypto perpetual swaps, cross-sectional momentum is the more defensible first baseline "
    "than reversal because sub-hour reversal is more closely tied to microstructure, bid-ask bounce, and temporary "
    "liquidity imbalance, while 1h bars are more aligned with trend, herding, and continuation mechanisms. This is "
    "a theoretical prior only, not evidence of profitability on this panel."
)
LOOKBACK_RATIONALE = (
    "The first route uses performance-free geometric doubling from 6h to 48h: 6h, 12h, 24h, 48h. "
    "The 72h horizon is intentionally excluded because it is a less regular 3-day horizon; weekly or longer "
    "multi-day horizons require a separate future route budget and separate approval."
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


def canonical_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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
        "preview": PREVIEW,
        "preview_contract": PREVIEW_CONTRACT,
        "prereg_requirement": PREREG_REQUIREMENT,
        "theory_prior": THEORY_PRIOR,
        "preview_approval": PREVIEW_APPROVAL,
        "registry": REGISTRY,
        "split_policy": SPLIT_POLICY,
        "access_rules": ACCESS_RULES,
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
    preview = loaded.get("preview", {})
    preview_contract = loaded.get("preview_contract", {})
    prereg_requirement = loaded.get("prereg_requirement", {})
    theory_prior_input = loaded.get("theory_prior", {})
    preview_approval = loaded.get("preview_approval", {})
    registry = loaded.get("registry", {})
    split = loaded.get("split_policy", {})
    access = loaded.get("access_rules", {})

    preview_confirmed = (
        preview.get("okx_88_symbol_1h_panel_strategy_search_preview_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_STRATEGY_SEARCH_PREVIEW_READY"
        and preview.get("strategy_search_preview_created") is True
        and preview.get("route_family_preregistration_required") is True
        and preview.get("route_family_selected_now") is False
        and preview.get("strategy_search_execution_allowed_next") is False
        and preview.get("future_route_family_preregistration_allowed_next") is True
        and preview.get("approval_grants_future_route_family_preregistration_next") is True
        and preview.get("momentum_vs_reversal_both_tested_now") is False
        and preview.get("reversal_not_tested_in_first_route") is True
        and preview.get("one_route_family_only") is True
        and preview.get("route_family_choice_locked_before_execution") is True
        and preview.get("route_family_choice_performance_free") is True
        and preview.get("preferred_first_route_family_theory_prior") == SELECTED_ROUTE_FAMILY
        and preview.get("rejected_alternative_route_family") == REJECTED_ROUTE_FAMILY
        and preview.get("theory_prior_not_edge_claim") is True
        and preview.get("theory_prior_not_based_on_okx_panel_performance") is True
        and preview.get("strategy_search_allowed_now") is False
        and preview.get("candidate_generation_allowed_now") is False
        and preview.get("edge_claim_allowed_now") is False
        and preview.get("sealed_holdout_accessed") is False
        and preview.get("replacement_checks_all_true") is True
        and prereg_requirement.get("route_family_preregistration_required") is True
        and prereg_requirement.get("route_family_selected_now") is False
        and prereg_requirement.get("strategy_search_execution_allowed_next") is False
        and theory_prior_input.get("preferred_first_route_family_theory_prior") == SELECTED_ROUTE_FAMILY
        and theory_prior_input.get("selection_basis") == SELECTION_BASIS
        and preview_approval.get("approval_grants_future_route_family_preregistration_next") is True
        and preview_approval.get("approval_grants_future_restricted_strategy_search_execution_next") is False
    )
    holdout_registry_confirmed = (
        registry.get("okx_88_symbol_1h_panel_holdout_registry_builder_status")
        == "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED"
        and registry.get("holdout_registry_valid_for_this_panel") is True
        and registry.get("holdout_registry_valid_for_strategy_search_governance") is True
        and registry.get("true_untouched_final_holdout_claimed") is False
        and registry.get("valid_for_final_edge_claim") is False
        and registry.get("replacement_checks_all_true") is True
    )
    holdout_policy_confirmed = (
        split.get("train_development_window_start") == "2023-07-01T00:00:00Z"
        and split.get("train_development_window_end_exclusive") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_start") == "2025-01-01T00:00:00Z"
        and split.get("validation_window_end_exclusive") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_start") == "2025-11-01T00:00:00Z"
        and split.get("sealed_holdout_window_end_exclusive") == "2026-05-19T00:00:00Z"
        and access.get("sealed_holdout_access_blocked_during_strategy_search") is True
    )

    route_config = {
        "allowed_holding_period_options": ALLOWED_HOLDING_PERIOD_OPTIONS,
        "allowed_lookback_options": ALLOWED_LOOKBACK_OPTIONS,
        "future_strategy_search_class": FUTURE_STRATEGY_SEARCH_CLASS,
        "parameter_grid_count_max": 12,
        "rejected_route_family_for_first_route": REJECTED_ROUTE_FAMILY,
        "route_family_count_max": 1,
        "route_family_selected": SELECTED_ROUTE_FAMILY,
        "timeframe": "1h",
        "universe_symbol_count": 88,
    }
    route_hash_payload = {
        "route_family_selected": SELECTED_ROUTE_FAMILY,
        "route_family_selection_basis": SELECTION_BASIS,
        "rejected_alternative": REJECTED_ROUTE_FAMILY,
    }
    config_hash = canonical_hash(route_config)
    route_hash = canonical_hash(route_hash_payload)

    no_forbidden_actions = {
        "data_download_performed": False,
        "data_build_performed": False,
        "aggregation_performed_now": False,
        "full_1h_panel_read_performed": False,
        "original_source_full_csv_read_performed": False,
        "strategy_search_executed": False,
        "candidate_generation_performed": False,
        "edge_claim_performed": False,
        "sealed_holdout_accessed": False,
        "okx_api_call_performed": False,
        "okx_browse_performed": False,
    }
    release_blocks = {
        "strategy_search_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "family_release_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
    }
    route_selection = {
        "allowed_holding_period_options": ",".join(ALLOWED_HOLDING_PERIOD_OPTIONS),
        "allowed_lookback_options": ",".join(ALLOWED_LOOKBACK_OPTIONS),
        "lookback_horizon_48h_included_as_geometric_doubling": True,
        "lookback_horizon_72h_excluded_from_first_route": True,
        "lookback_horizon_72h_future_route_budget_required": True,
        "lookback_horizon_selection_basis": LOOKBACK_BASIS,
        "lookback_horizon_selection_used_panel_performance": False,
        "momentum_vs_reversal_both_tested": False,
        "one_route_family_only": True,
        "reversal_not_tested_in_first_route": True,
        "route_family_choice_locked_before_execution": True,
        "route_family_rejected_for_first_route": REJECTED_ROUTE_FAMILY,
        "route_family_selected": SELECTED_ROUTE_FAMILY,
        "route_family_selection_basis": SELECTION_BASIS,
        "route_family_selection_used_extreme_return_distribution_for_alpha_choice": False,
        "route_family_selection_used_panel_performance": False,
        "route_family_selection_used_sealed_holdout": False,
        "route_family_selection_used_train_performance": False,
        "route_family_selection_used_validation_performance": False,
        "selected_route_family_config_bounds_created": True,
        "theory_prior_not_edge_claim": True,
        "theory_prior_recorded": True,
    }
    guardrails = {
        "cost_slippage_policy_required": True,
        "every_parameter_combination_counted": True,
        "future_execution_may_execute_only_selected_route_family": SELECTED_ROUTE_FAMILY,
        "incomplete_hour_policy_required": True,
        "monthly_stability_reporting_required": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_incomplete_hour_mishandling": True,
        "no_lookahead_policy_required": True,
        "no_reversal_test_in_first_route": True,
        "no_route_family_switch_after_results": True,
        "no_sealed_holdout_access": True,
        "null_baseline_required": True,
        "route_config_hash_recorded_before_execution_required": True,
        "sealed_holdout_access_allowed_now": False,
        "sealed_holdout_access_blocked_during_strategy_search": True,
        "turnover_concentration_reporting_required": True,
    }
    approvals = {
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_future_restricted_strategy_search_execution_next": True,
        "approval_grants_holdout_access_now": False,
        "approval_grants_route_family_preregistration_now": True,
        "approval_grants_runtime_live_capital_now": False,
        "approval_grants_strategy_search_execution_now": False,
        "next_module": NEXT_PASS_MODULE,
    }

    replacement_checks = {
        "allowed_lookbacks_are_6_12_24_48_only": ALLOWED_LOOKBACK_OPTIONS == ["6h", "12h", "24h", "48h"],
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "forty_eight_hour_included": "48h" in ALLOWED_LOOKBACK_OPTIONS,
        "holdout_policy_confirmed": holdout_policy_confirmed,
        "holdout_registry_confirmed": holdout_registry_confirmed,
        "no_candidate_generation_now": release_blocks["candidate_generation_allowed_now"] is False,
        "no_edge_claim_now": release_blocks["edge_claim_allowed_now"] is False,
        "no_full_1h_panel_read": no_forbidden_actions["full_1h_panel_read_performed"] is False,
        "no_original_1m_source_read": no_forbidden_actions["original_source_full_csv_read_performed"] is False,
        "no_sealed_holdout_access": no_forbidden_actions["sealed_holdout_accessed"] is False,
        "no_strategy_search_execution_now": no_forbidden_actions["strategy_search_executed"] is False,
        "preview_confirmed": preview_confirmed,
        "repo_clean_except_current_tool": repo_clean,
        "reversal_not_tested": route_selection["reversal_not_tested_in_first_route"] is True,
        "route_family_count_one": route_config["route_family_count_max"] == 1,
        "route_family_is_momentum_only": route_selection["route_family_selected"] == SELECTED_ROUTE_FAMILY,
        "route_family_selection_performance_free": (
            route_selection["route_family_selection_used_panel_performance"] is False
            and route_selection["route_family_selection_used_train_performance"] is False
            and route_selection["route_family_selection_used_validation_performance"] is False
            and route_selection["route_family_selection_used_sealed_holdout"] is False
            and route_selection["route_family_selection_used_extreme_return_distribution_for_alpha_choice"] is False
        ),
        "seventy_two_hour_excluded": "72h" not in ALLOWED_LOOKBACK_OPTIONS,
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS
    next_module = NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE
    quality = PASS_QUALITY if replacement_checks_all_true else BLOCKED_QUALITY

    summary = {
        "active_p0_blocker_count": 0 if replacement_checks_all_true else 1,
        "active_p1_attention_count": 0,
        "allowed_holding_period_options": route_selection["allowed_holding_period_options"],
        "allowed_lookback_options": route_selection["allowed_lookback_options"],
        "config_hash": config_hash,
        "config_hash_record_created": replacement_checks_all_true,
        "current_evidence_chain_quality_after_preregistration": quality,
        "future_restricted_strategy_search_execution_allowed_next": replacement_checks_all_true,
        "holdout_registry_confirmed": holdout_registry_confirmed,
        "holdout_registry_valid_for_this_panel": registry.get("holdout_registry_valid_for_this_panel") is True,
        "lookback_horizon_48h_included_as_geometric_doubling": True,
        "lookback_horizon_72h_excluded_from_first_route": True,
        "lookback_horizon_72h_future_route_budget_required": True,
        "lookback_horizon_selection_basis": LOOKBACK_BASIS,
        "lookback_horizon_selection_used_panel_performance": False,
        "next_module": next_module,
        "okx_88_symbol_1h_panel_route_family_preregistration_status": status,
        "parameter_grid_count_max": 12,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "route_family_count_max": 1,
        "route_family_preregistration_performed": replacement_checks_all_true,
        "route_hash": route_hash,
        "route_hash_record_created": replacement_checks_all_true,
        "strategy_search_preview_confirmed": preview_confirmed,
        "tracked_python_count_at_preregistration_run": tracked_python_count(),
        "unexpected_git_status_entries": unexpected_status,
        "validation_load_errors": load_errors,
    }
    summary.update(route_selection)
    summary.update(guardrails)
    summary.update(approvals if replacement_checks_all_true else {**approvals, "approval_grants_future_restricted_strategy_search_execution_next": False, "next_module": next_module})
    summary.update(release_blocks)
    summary.update(no_forbidden_actions)

    rationale = {
        "route_family_rejected_for_first_route": REJECTED_ROUTE_FAMILY,
        "route_family_selected": SELECTED_ROUTE_FAMILY,
        "route_family_selection_basis": SELECTION_BASIS,
        "route_family_selection_rationale": THEORY_SELECTION_RATIONALE,
        "theory_prior_not_edge_claim": True,
        "theory_prior_recorded": True,
        "theory_prior_source": "PERFORMANCE_FREE_MARKET_STRUCTURE_PRIOR",
    }
    lookback = {
        "allowed_lookback_options": ALLOWED_LOOKBACK_OPTIONS,
        "lookback_horizon_48h_included_as_geometric_doubling": True,
        "lookback_horizon_72h_excluded_from_first_route": True,
        "lookback_horizon_72h_future_route_budget_required": True,
        "lookback_horizon_selection_basis": LOOKBACK_BASIS,
        "lookback_horizon_selection_rationale": LOOKBACK_RATIONALE,
        "lookback_horizon_selection_used_panel_performance": False,
    }
    config_bounds = {
        "allowed_future_signal_shape": "cross-sectional momentum based on past returns",
        "allowed_holding_period_options": ALLOWED_HOLDING_PERIOD_OPTIONS,
        "allowed_lookback_options": ALLOWED_LOOKBACK_OPTIONS,
        "alternative_data_allowed": False,
        "ensemble_allowed": False,
        "future_execution_must_not_execute_reversal": True,
        "machine_learning_allowed": False,
        "no_symbol_specific_parameter_tuning": True,
        "parameter_grid_count_max": 12,
        "rank_symbols_cross_sectionally_within_each_timestamp": True,
        "route_family_selected": SELECTED_ROUTE_FAMILY,
    }
    hash_record = {
        "config_hash": config_hash,
        "config_hash_record_created": replacement_checks_all_true,
        "config_hash_source": route_config,
        "route_hash": route_hash,
        "route_hash_record_created": replacement_checks_all_true,
        "route_hash_source": route_hash_payload,
    }
    self_validator = {
        "created_at_utc": now_utc(),
        "expected_head": EXPECTED_HEAD,
        "latest_head_at_run": head,
        "output_dir": str(OUTPUT_DIR),
        "required_artifacts": list(output_payloads(summary, rationale, lookback, config_bounds, hash_record, guardrails, approvals).keys()),
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "status": status,
        "tool_path": str(REPO / TOOL_REL),
    }

    return {
        "summary": summary,
        "rationale": rationale,
        "lookback": lookback,
        "config_bounds": config_bounds,
        "hash_record": hash_record,
        "guardrails": guardrails,
        "approvals": approvals if replacement_checks_all_true else {**approvals, "approval_grants_future_restricted_strategy_search_execution_next": False, "next_module": next_module},
        "self_validator": self_validator,
    }


def output_payloads(
    summary: dict[str, Any],
    rationale: dict[str, Any],
    lookback: dict[str, Any],
    config_bounds: dict[str, Any],
    hash_record: dict[str, Any],
    guardrails: dict[str, Any],
    approvals: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "repo_only_okx_88_symbol_1h_panel_route_family_preregistration.json": summary,
        "repo_only_okx_88_symbol_1h_panel_route_family_selection_rationale.json": rationale,
        "repo_only_okx_88_symbol_1h_panel_lookback_horizon_selection_rationale.json": lookback,
        "repo_only_okx_88_symbol_1h_panel_cross_sectional_momentum_baseline_config_bounds.json": config_bounds,
        "repo_only_okx_88_symbol_1h_panel_route_family_hash_record.json": hash_record,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_guardrails.json": guardrails,
        "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_execution_approval_record.json": approvals,
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payloads = output_payloads(
        outputs["summary"],
        outputs["rationale"],
        outputs["lookback"],
        outputs["config_bounds"],
        outputs["hash_record"],
        outputs["guardrails"],
        outputs["approvals"],
    )
    payloads["repo_only_okx_88_symbol_1h_panel_route_family_preregistration_self_validator.json"] = outputs["self_validator"]
    for filename, payload in payloads.items():
        write_json(OUTPUT_DIR / filename, payload)


def main() -> int:
    outputs = build_outputs()
    write_outputs(outputs)
    print(json.dumps(outputs["summary"], indent=2, sort_keys=True))
    return 0 if outputs["summary"]["replacement_checks_all_true"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
