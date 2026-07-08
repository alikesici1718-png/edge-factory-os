from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
EDGE_ROOT = REPO.parent
TOOL_REL = Path(
    "tools/edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_record_after_evaluator_v1.py"
)
OUTPUT_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_record_after_evaluator_v1"
)

EXPECTED_HEAD = "9b559c01c58aa9bb35a4e0fab46586c94c632b54"
PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_CLOSURE_RECORD_CREATED"
BLOCKED_STATUS = "BLOCKED_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_CLOSURE_RECORD_REVIEW_REQUIRED"
EVALUATOR_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_EVALUATED"
EXECUTION_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_RESTRICTED_STRATEGY_SEARCH_RETRY_EXECUTED"
FINALIZE_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_REVISED_PARTIAL_OUTPUT_FINALIZE_MANIFEST_COMPLETE"
ROUTE_PREREG_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_ROUTE_FAMILY_PREREGISTERED"
HOLDOUT_REGISTRY_PASS_STATUS = "PASS_REPO_ONLY_OKX_88_SYMBOL_1H_PANEL_HOLDOUT_REGISTRY_CREATED"

RESULT_CLASS = "MOMENTUM_BASELINE_REJECTED_NO_FOLLOWUP"
ROUTE_FAMILY = "CROSS_SECTIONAL_MOMENTUM_BASELINE"
CURRENT_QUALITY = "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_BASELINE_CLOSED_GOVERNANCE_SUMMARY_NEXT"
NEXT_PASS_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_research_governance_summary_after_momentum_closure_v1.py"
)
NEXT_BLOCKED_MODULE = (
    "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_record_blocked_review_v1.py"
)
CLOSURE_REASON = (
    "All validation net metrics are non-positive after costs, best validation net metric is "
    "-4.680782776161402 for momentum_lb48h_hold1h, null baseline review did not pass, "
    "monthly stability review did not pass, and diagnostic_promising is false. This is a clean "
    "negative research result, not a data failure, runtime failure, edge claim, or release."
)

EVALUATOR_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_after_execution_v1"
)
EVALUATOR_REPORT = EVALUATOR_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_report.json"
EVALUATOR_DECISION = EVALUATOR_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_decision.json"
EVALUATOR_APPROVAL = EVALUATOR_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_approval_record.json"
EVALUATOR_SELF_VALIDATOR = (
    EVALUATOR_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_self_validator.json"
)

EXECUTION_DIR = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_after_revised_non_holdout_view_preview_v1"
)
EXECUTION_REPORT = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_report.json"
EXECUTION_SUMMARY = EXECUTION_DIR / "repo_only_okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_summary.json"

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

HOLDOUT_REGISTRY = (
    EDGE_ROOT
    / "edge_factory_os_repo_only_okx_88_symbol_1h_panel_holdout_registry_builder_before_strategy_search_v1"
    / "repo_only_okx_88_symbol_1h_panel_holdout_registry.json"
)

REQUIRED_ARTIFACT_NAMES = [
    "repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_record.json",
    "repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_reason.json",
    "repo_only_okx_88_symbol_1h_panel_restricted_momentum_negative_result_summary.json",
    "repo_only_okx_88_symbol_1h_panel_restricted_momentum_route_block_record.json",
    "repo_only_okx_88_symbol_1h_panel_restricted_momentum_asset_preservation_record.json",
    "repo_only_okx_88_symbol_1h_panel_research_governance_summary_approval_record.json",
    "repo_only_okx_88_symbol_1h_panel_restricted_momentum_closure_record_self_validator.json",
]


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


def load_json(label: str, path: Path, errors: dict[str, str]) -> dict[str, Any]:
    try:
        return read_json(path)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        errors[label] = f"{path}: {exc}"
        return {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def tracked_python_count_with_current_tool() -> int:
    tracked = [line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()]
    current = TOOL_REL.as_posix()
    if current not in {line.replace("\\", "/") for line in tracked} and (REPO / TOOL_REL).exists():
        tracked.append(current)
    return len(tracked)


def repo_status_allowing_current_tool() -> tuple[bool, list[str], list[str]]:
    lines = [line for line in git(["status", "--short", "--untracked-files=all"]).splitlines() if line.strip()]
    allowed_suffix = TOOL_REL.as_posix()
    unexpected = [line for line in lines if not line.replace("\\", "/").endswith(allowed_suffix)]
    return not unexpected, lines, unexpected


def bool_is_false(payload: dict[str, Any], key: str) -> bool:
    return payload.get(key) is False


def bool_is_true(payload: dict[str, Any], key: str) -> bool:
    return payload.get(key) is True


def build_report() -> dict[str, Any]:
    load_errors: dict[str, str] = {}
    evaluator = load_json("evaluator_report", EVALUATOR_REPORT, load_errors)
    evaluator_decision = load_json("evaluator_decision", EVALUATOR_DECISION, load_errors)
    evaluator_approval = load_json("evaluator_approval", EVALUATOR_APPROVAL, load_errors)
    evaluator_self_validator = load_json("evaluator_self_validator", EVALUATOR_SELF_VALIDATOR, load_errors)
    execution_report = load_json("execution_report", EXECUTION_REPORT, load_errors)
    execution_summary = load_json("execution_summary", EXECUTION_SUMMARY, load_errors)
    final_manifest = load_json("final_manifest", FINAL_MANIFEST, load_errors)
    final_eligibility = load_json("final_eligibility", FINAL_ELIGIBILITY, load_errors)
    route_prereg = load_json("route_preregistration", ROUTE_PREREG, load_errors)
    route_bounds = load_json("route_bounds", ROUTE_BOUNDS, load_errors)
    holdout_registry = load_json("holdout_registry", HOLDOUT_REGISTRY, load_errors)

    repo_root = git(["rev-parse", "--show-toplevel"])
    head = git(["rev-parse", "HEAD"])
    repo_clean_except_tool, status_lines, unexpected_status = repo_status_allowing_current_tool()

    evaluator_confirmed = (
        evaluator.get("okx_88_symbol_1h_panel_restricted_strategy_search_retry_evaluator_status")
        == EVALUATOR_PASS_STATUS
        and bool_is_true(evaluator, "evaluator_performed")
        and bool_is_true(evaluator, "retry_execution_confirmed")
        and bool_is_true(evaluator, "replacement_checks_all_true")
        and evaluator_decision.get("result_class") == RESULT_CLASS
        and evaluator_approval.get("approval_grants_future_closure_record_next") is True
        and evaluator_self_validator.get("self_validation_result") is True
    )
    result_class_confirmed = evaluator.get("result_class") == RESULT_CLASS
    diagnostic_promising = evaluator.get("diagnostic_promising")
    best_validation_net_metric = evaluator.get("best_validation_net_metric")

    execution_confirmed = (
        execution_report.get("okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_status")
        == EXECUTION_PASS_STATUS
        and execution_summary.get("okx_88_symbol_1h_panel_restricted_strategy_search_retry_execution_status")
        == EXECUTION_PASS_STATUS
        and bool_is_true(execution_report, "restricted_strategy_search_retry_execution_performed")
        and bool_is_true(execution_report, "replacement_checks_all_true")
        and execution_report.get("route_family_selected") == ROUTE_FAMILY
        and execution_report.get("tested_config_count") == 12
        and bool_is_false(execution_report, "sealed_holdout_accessed")
        and bool_is_false(execution_report, "boundary_buffer_accessed")
        and bool_is_false(execution_report, "current_all_in_one_panel_read_performed")
        and bool_is_false(execution_report, "original_source_full_csv_read_performed")
        and bool_is_false(execution_report, "reversal_tested")
        and bool_is_false(execution_report, "momentum_vs_reversal_compared")
        and bool_is_false(execution_report, "candidate_generation_performed")
        and bool_is_false(execution_report, "edge_claim_performed")
        and bool_is_false(execution_report, "family_release_performed")
    )
    finalized_panel_confirmed = (
        final_manifest.get("okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_status")
        == FINALIZE_PASS_STATUS
        and final_eligibility.get("okx_88_symbol_1h_panel_revised_partial_output_finalize_manifest_status")
        == FINALIZE_PASS_STATUS
        and final_manifest.get("output_symbol_count") == 88
        and final_manifest.get("output_1h_row_count") == 1802944
        and bool_is_true(final_manifest, "output_valid_for_restricted_momentum_search_input")
        and bool_is_true(final_manifest, "output_valid_for_strategy_search_after_finalization")
        and bool_is_false(final_manifest, "output_valid_for_edge_claim")
        and bool_is_false(final_manifest, "output_valid_for_runtime_or_live")
        and bool_is_true(final_manifest, "physically_excludes_sealed_holdout")
        and bool_is_true(final_manifest, "physically_excludes_boundary_buffer")
        and bool_is_false(final_manifest, "current_all_in_one_panel_read_performed")
        and bool_is_false(final_manifest, "original_source_full_csv_read_performed")
        and bool_is_true(final_manifest, "replacement_checks_all_true")
    )
    route_prereg_confirmed = (
        route_prereg.get("okx_88_symbol_1h_panel_route_family_preregistration_status") == ROUTE_PREREG_PASS_STATUS
        and route_prereg.get("route_family_selected") == ROUTE_FAMILY
        and route_prereg.get("parameter_grid_count_max") == 12
        and route_prereg.get("allowed_lookback_options") == "6h,12h,24h,48h"
        and route_prereg.get("allowed_holding_period_options") == "1h,3h,6h"
        and bool_is_true(route_prereg, "no_reversal_test_in_first_route")
        and bool_is_true(route_prereg, "lookback_horizon_72h_excluded_from_first_route")
        and bool_is_false(route_prereg, "strategy_search_executed")
        and bool_is_true(route_prereg, "replacement_checks_all_true")
        and route_bounds.get("route_family_selected") == ROUTE_FAMILY
    )
    holdout_registry_confirmed = (
        holdout_registry.get("okx_88_symbol_1h_panel_holdout_registry_builder_status") == HOLDOUT_REGISTRY_PASS_STATUS
        and holdout_registry.get("selected_symbol_count") == 88
        and bool_is_true(holdout_registry, "holdout_registry_valid_for_strategy_search_governance")
        and bool_is_true(holdout_registry, "holdout_registry_valid_for_this_panel")
        and bool_is_true(holdout_registry, "sealed_holdout_access_blocked_during_strategy_search")
        and bool_is_false(holdout_registry, "full_1h_panel_read_performed")
        and bool_is_false(holdout_registry, "original_source_full_csv_read_performed")
        and bool_is_true(holdout_registry, "replacement_checks_all_true")
    )

    closure_permissions = {
        "momentum_route_closed": True,
        "momentum_route_retest_allowed_now": False,
        "momentum_parameter_expansion_allowed_now": False,
        "reversal_followup_allowed_from_this_closure": False,
        "strategy_search_expansion_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "holdout_access_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "new_strategy_search_executed": False,
        "reversal_tested": False,
        "candidate_generation_performed": False,
        "edge_claim_performed": False,
        "family_release_performed": False,
        "holdout_accessed": False,
        "finalized_panel_rows_read": False,
        "current_all_in_one_panel_read_performed": False,
        "original_source_full_csv_read_performed": False,
    }
    approval_record = {
        "approval_grants_closure_record_now": True,
        "approval_grants_future_research_governance_summary_next": True,
        "approval_grants_momentum_retest_now": False,
        "approval_grants_strategy_search_expansion_now": False,
        "approval_grants_reversal_search_now": False,
        "approval_grants_candidate_generation_now": False,
        "approval_grants_edge_claim_now": False,
        "approval_grants_family_release_now": False,
        "approval_grants_holdout_access_now": False,
        "approval_grants_runtime_live_capital_now": False,
    }
    asset_preservation = {
        "panel_reusable_for_future_read_only_research": True,
        "panel_valid_for_edge_claim": False,
        "panel_valid_for_runtime_live_capital": False,
        "panel_requires_new_preregistered_route_for_future_search": True,
    }

    replacement_checks = {
        "repo_root_matches_expected": repo_root == REPO.as_posix(),
        "current_head_matches_expected": head == EXPECTED_HEAD,
        "repo_clean_except_current_tool": repo_clean_except_tool,
        "evaluator_artifacts_loaded": not load_errors,
        "evaluator_confirmed": evaluator_confirmed,
        "result_class_confirmed": result_class_confirmed,
        "diagnostic_promising_false": diagnostic_promising is False,
        "best_validation_net_metric_negative": isinstance(best_validation_net_metric, (int, float))
        and best_validation_net_metric < 0,
        "validation_positive_after_cost_false": evaluator.get("validation_positive_after_cost") is False,
        "null_baseline_review_passed_false": evaluator.get("null_baseline_review_passed") is False,
        "monthly_stability_review_passed_false": evaluator.get("monthly_stability_review_passed") is False,
        "turnover_concentration_review_passed_true": evaluator.get("turnover_concentration_review_passed") is True,
        "metric_integrity_issue_count_zero": evaluator.get("metric_integrity_issue_count") == 0,
        "execution_artifacts_confirmed": execution_confirmed,
        "finalized_panel_metadata_confirmed_without_row_read": finalized_panel_confirmed,
        "route_preregistration_confirmed": route_prereg_confirmed,
        "holdout_registry_confirmed": holdout_registry_confirmed,
        "closure_permissions_all_fail_closed": all(value is False for key, value in closure_permissions.items() if key != "momentum_route_closed")
        and closure_permissions["momentum_route_closed"] is True,
        "approval_permissions_all_fail_closed_except_governance_summary": (
            approval_record["approval_grants_future_research_governance_summary_next"] is True
            and all(
                value is False
                for key, value in approval_record.items()
                if key
                not in {
                    "approval_grants_closure_record_now",
                    "approval_grants_future_research_governance_summary_next",
                }
            )
        ),
        "asset_preservation_truth_boundary": (
            asset_preservation["panel_reusable_for_future_read_only_research"] is True
            and asset_preservation["panel_valid_for_edge_claim"] is False
            and asset_preservation["panel_valid_for_runtime_live_capital"] is False
            and asset_preservation["panel_requires_new_preregistered_route_for_future_search"] is True
        ),
    }
    replacement_checks_all_true = all(replacement_checks.values()) and not load_errors
    status = PASS_STATUS if replacement_checks_all_true else BLOCKED_STATUS

    active_p0 = 0 if replacement_checks_all_true else 1
    report = {
        "active_p0_blocker_count": active_p0,
        "active_p1_attention_count": 0,
        "artifact_output_dir": str(OUTPUT_DIR),
        "best_validation_config_id": evaluator.get("best_validation_config_id"),
        "best_validation_holding_period": evaluator.get("best_validation_holding_period"),
        "best_validation_lookback": evaluator.get("best_validation_lookback"),
        "best_validation_net_metric": best_validation_net_metric,
        "closure_reason": CLOSURE_REASON,
        "closure_record_created": replacement_checks_all_true,
        "created_at_utc": now_utc(),
        "current_evidence_chain_quality_after_closure": CURRENT_QUALITY
        if replacement_checks_all_true
        else "OKX_88_SYMBOL_1H_PANEL_RESTRICTED_MOMENTUM_BASELINE_CLOSURE_BLOCKED_REVIEW_REQUIRED",
        "diagnostic_promising": diagnostic_promising,
        "evaluator_confirmed": evaluator_confirmed,
        "load_errors": load_errors,
        "metric_integrity_issue_count": evaluator.get("metric_integrity_issue_count"),
        "monthly_stability_review_passed": evaluator.get("monthly_stability_review_passed"),
        "next_module": NEXT_PASS_MODULE if replacement_checks_all_true else NEXT_BLOCKED_MODULE,
        "null_baseline_review_passed": evaluator.get("null_baseline_review_passed"),
        "okx_88_symbol_1h_panel_restricted_momentum_closure_record_status": status,
        "replacement_checks": replacement_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "result_class": evaluator.get("result_class"),
        "result_class_confirmed": result_class_confirmed,
        "route_family_selected": evaluator.get("route_family_selected"),
        "tested_config_count": evaluator.get("tested_config_count"),
        "tracked_python_count_at_closure_run_including_current_tool": tracked_python_count_with_current_tool(),
        "turnover_concentration_review_passed": evaluator.get("turnover_concentration_review_passed"),
        "unexpected_git_status_entries": unexpected_status,
        "validation_positive_after_cost": evaluator.get("validation_positive_after_cost"),
        **closure_permissions,
        **asset_preservation,
        **approval_record,
    }
    report["evidence_chain"] = {
        "evaluator_report": str(EVALUATOR_REPORT),
        "evaluator_decision": str(EVALUATOR_DECISION),
        "evaluator_approval": str(EVALUATOR_APPROVAL),
        "evaluator_self_validator": str(EVALUATOR_SELF_VALIDATOR),
        "execution_report": str(EXECUTION_REPORT),
        "execution_summary": str(EXECUTION_SUMMARY),
        "final_manifest": str(FINAL_MANIFEST),
        "final_eligibility": str(FINAL_ELIGIBILITY),
        "route_preregistration": str(ROUTE_PREREG),
        "route_bounds": str(ROUTE_BOUNDS),
        "holdout_registry": str(HOLDOUT_REGISTRY),
    }
    report["closure_interpretation"] = {
        "clean_negative_research_result": True,
        "data_failure": False,
        "runtime_failure": False,
        "edge_claim": False,
        "route_was_preregistered": route_prereg_confirmed,
        "route_was_executed_on_finalized_revised_non_holdout_panel": execution_confirmed
        and finalized_panel_confirmed,
        "symbol_count": final_manifest.get("output_symbol_count"),
        "non_holdout_1h_row_count": final_manifest.get("output_1h_row_count"),
        "sealed_holdout_rows_used": 0,
        "boundary_buffer_rows_used": 0,
        "preregistered_momentum_config_count": evaluator.get("tested_config_count"),
        "reversal_comparison_performed": False,
        "costs_applied": execution_report.get("round_trip_cost_bps") == 20,
        "null_monthly_turnover_diagnostics_produced": (
            evaluator.get("null_diagnostics_loaded") is True
            and evaluator.get("monthly_stability_loaded") is True
            and evaluator.get("turnover_concentration_loaded") is True
        ),
    }
    return report


def artifact_payloads(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    common = {
        key: report[key]
        for key in [
            "okx_88_symbol_1h_panel_restricted_momentum_closure_record_status",
            "closure_record_created",
            "evaluator_confirmed",
            "result_class_confirmed",
            "result_class",
            "diagnostic_promising",
            "route_family_selected",
            "tested_config_count",
            "best_validation_config_id",
            "best_validation_lookback",
            "best_validation_holding_period",
            "best_validation_net_metric",
            "validation_positive_after_cost",
            "null_baseline_review_passed",
            "monthly_stability_review_passed",
            "turnover_concentration_review_passed",
            "metric_integrity_issue_count",
            "closure_reason",
            "momentum_route_closed",
            "momentum_route_retest_allowed_now",
            "momentum_parameter_expansion_allowed_now",
            "reversal_followup_allowed_from_this_closure",
            "strategy_search_expansion_allowed_now",
            "candidate_generation_allowed_now",
            "edge_claim_allowed_now",
            "family_release_allowed_now",
            "holdout_access_allowed_now",
            "runtime_live_capital_allowed_now",
            "panel_reusable_for_future_read_only_research",
            "panel_valid_for_edge_claim",
            "panel_valid_for_runtime_live_capital",
            "panel_requires_new_preregistered_route_for_future_search",
            "new_strategy_search_executed",
            "reversal_tested",
            "candidate_generation_performed",
            "edge_claim_performed",
            "family_release_performed",
            "holdout_accessed",
            "finalized_panel_rows_read",
            "current_all_in_one_panel_read_performed",
            "original_source_full_csv_read_performed",
            "approval_grants_future_research_governance_summary_next",
            "approval_grants_momentum_retest_now",
            "approval_grants_strategy_search_expansion_now",
            "approval_grants_reversal_search_now",
            "approval_grants_candidate_generation_now",
            "approval_grants_edge_claim_now",
            "approval_grants_family_release_now",
            "approval_grants_holdout_access_now",
            "approval_grants_runtime_live_capital_now",
            "active_p0_blocker_count",
            "active_p1_attention_count",
            "current_evidence_chain_quality_after_closure",
            "next_module",
            "replacement_checks_all_true",
        ]
    }
    return {
        REQUIRED_ARTIFACT_NAMES[0]: {
            **report,
            "record_type": "REPO_ONLY_MOMENTUM_BASELINE_CLOSURE_RECORD",
        },
        REQUIRED_ARTIFACT_NAMES[1]: {
            **common,
            "record_type": "REPO_ONLY_MOMENTUM_BASELINE_CLOSURE_REASON",
            "closure_reason_detail": report["closure_interpretation"],
        },
        REQUIRED_ARTIFACT_NAMES[2]: {
            **common,
            "record_type": "REPO_ONLY_MOMENTUM_BASELINE_NEGATIVE_RESULT_SUMMARY",
            "negative_result_basis": {
                "all_validation_net_metrics_non_positive_after_costs": True,
                "best_validation_config_id": report["best_validation_config_id"],
                "best_validation_net_metric": report["best_validation_net_metric"],
                "null_baseline_review_passed": report["null_baseline_review_passed"],
                "monthly_stability_review_passed": report["monthly_stability_review_passed"],
                "diagnostic_promising": report["diagnostic_promising"],
            },
        },
        REQUIRED_ARTIFACT_NAMES[3]: {
            **common,
            "record_type": "REPO_ONLY_MOMENTUM_ROUTE_BLOCK_RECORD",
            "blocked_route_family": ROUTE_FAMILY,
            "route_block_policy": {
                "do_not_route_to_reversal_because_momentum_failed": True,
                "reversal_requires_separate_preregistered_route_family_contract": True,
                "do_not_expand_momentum_grid": True,
                "do_not_rerun_with_72h": True,
                "do_not_generate_candidate_from_least_bad_config": True,
            },
        },
        REQUIRED_ARTIFACT_NAMES[4]: {
            **common,
            "record_type": "REPO_ONLY_MOMENTUM_ASSET_PRESERVATION_RECORD",
            "asset_preservation_policy": {
                "finalized_revised_non_holdout_panel_remains_validated_research_input": True,
                "not_edge_artifact": True,
                "not_runtime_live_capital_artifact": True,
                "future_search_requires_new_preregistered_route": True,
            },
        },
        REQUIRED_ARTIFACT_NAMES[5]: {
            **common,
            "record_type": "REPO_ONLY_RESEARCH_GOVERNANCE_SUMMARY_APPROVAL_RECORD",
            "approval_scope": "future governance summary only",
            "approved_next_module": NEXT_PASS_MODULE if report["replacement_checks_all_true"] else NEXT_BLOCKED_MODULE,
            "approval_grants_closure_record_now": report["approval_grants_closure_record_now"],
        },
        REQUIRED_ARTIFACT_NAMES[6]: {
            **common,
            "record_type": "REPO_ONLY_MOMENTUM_CLOSURE_RECORD_SELF_VALIDATOR",
            "artifact_count_expected": len(REQUIRED_ARTIFACT_NAMES),
            "required_artifact_names": REQUIRED_ARTIFACT_NAMES,
            "replacement_checks": report["replacement_checks"],
            "load_errors": report["load_errors"],
            "self_validation_result": report["replacement_checks_all_true"],
            "self_validation_created_at_utc": now_utc(),
        },
    }


def write_outputs(report: dict[str, Any]) -> None:
    for name, payload in artifact_payloads(report).items():
        write_json(OUTPUT_DIR / name, payload)


def refresh_self_validator(report: dict[str, Any]) -> None:
    existence = {name: (OUTPUT_DIR / name).exists() for name in REQUIRED_ARTIFACT_NAMES}
    report["required_artifacts_exist"] = existence
    report["required_artifacts_all_exist"] = all(existence.values())
    if not report["required_artifacts_all_exist"]:
        report["replacement_checks_all_true"] = False
        report["closure_record_created"] = False
        report["active_p0_blocker_count"] = 1
        report["okx_88_symbol_1h_panel_restricted_momentum_closure_record_status"] = BLOCKED_STATUS
        report["next_module"] = NEXT_BLOCKED_MODULE
    payloads = artifact_payloads(report)
    payloads[REQUIRED_ARTIFACT_NAMES[6]]["required_artifacts_exist"] = existence
    payloads[REQUIRED_ARTIFACT_NAMES[6]]["required_artifacts_all_exist"] = report["required_artifacts_all_exist"]
    write_json(OUTPUT_DIR / REQUIRED_ARTIFACT_NAMES[0], payloads[REQUIRED_ARTIFACT_NAMES[0]])
    write_json(OUTPUT_DIR / REQUIRED_ARTIFACT_NAMES[6], payloads[REQUIRED_ARTIFACT_NAMES[6]])


def main() -> int:
    report = build_report()
    write_outputs(report)
    refresh_self_validator(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["replacement_checks_all_true"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
