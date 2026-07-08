#!/usr/bin/env python
"""Evaluate the single basis/premium z-score diagnostic execution."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MODULE_RELATIVE_PATH = (
    "tools/"
    "edge_factory_os_repo_only_binance_okx_overlap_basis_premium_zscore_mean_reversion_"
    "evaluator_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/strategy_evaluations/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_evaluator_v1.json"
)
EXECUTION_RELATIVE_PATH = (
    "artifacts/strategy_executions/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_execution_v1.json"
)

ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_EVALUATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_EVALUATION"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_EXECUTED"
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_BASELINE"
CONFIG_ID = "mark_index_basis_z30d_reversal_hold8h"

PROMISING_CLASS = (
    "BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_"
    "NO_CANDIDATE_NO_EDGE"
)
REJECTED_CLASS = "BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_INCONCLUSIVE_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALIDATED_CLASS = "BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_false(values: dict) -> bool:
    return all(value is False for value in values.values() if isinstance(value, bool))


def main() -> int:
    if ARTIFACT_PATH.exists():
        print(f"BLOCKED: artifact already exists: {ARTIFACT_PATH}")
        print("replacement_checks_all_true: false")
        return 1

    execution = load_json(EXECUTION_PATH)
    config_result = execution.get("config_result", {})
    signal_coverage = execution.get("signal_coverage_summary", {})
    monthly = execution.get("monthly_stability_summary", {})
    null_baseline = execution.get("null_baseline_summary", {})
    turnover = execution.get("turnover_concentration_summary", {})
    metric_integrity = execution.get("metric_integrity_summary", {})
    safety_permissions = execution.get("safety_permissions", {})
    forbidden = execution.get("forbidden_actions_confirmed_false", {})
    side_summary = execution.get("long_short_side_summary", {})
    premium_basis = execution.get("premium_basis_diagnostic_summary", {})

    validation_net_metric_bps = config_result.get("validation_net_metric_bps")
    validation_positive_after_cost = config_result.get("validation_positive_after_cost") is True
    null_passed = null_baseline.get("null_baseline_review_preliminary_passed") is True
    monthly_passed = monthly.get("monthly_stability_review_preliminary_passed") is True
    coverage_passed = signal_coverage.get("signal_coverage_review_preliminary_passed") is True
    turnover_passed = turnover.get("turnover_concentration_review_preliminary_passed") is True
    metric_integrity_passed = metric_integrity.get("metric_integrity_passed") is True
    safety_review_passed = (
        safety_permissions.get("candidate_generation_allowed_now") is False
        and safety_permissions.get("edge_claim_allowed_now") is False
        and safety_permissions.get("family_release_allowed_now") is False
        and safety_permissions.get("holdout_permission_allowed_now") is False
        and safety_permissions.get("runtime_permission_allowed_now") is False
        and safety_permissions.get("live_permission_allowed_now") is False
        and safety_permissions.get("capital_permission_allowed_now") is False
        and all_false(forbidden)
    )
    validation_net_positive = (
        isinstance(validation_net_metric_bps, (int, float)) and validation_net_metric_bps > 0
    )

    diagnostic_promising = (
        validation_net_positive
        and validation_positive_after_cost
        and null_passed
        and monthly_passed
        and coverage_passed
        and turnover_passed
        and metric_integrity_passed
        and safety_review_passed
    )

    required_metric_values = [
        validation_net_metric_bps,
        config_result.get("train", {}).get("net_mean_bps"),
        config_result.get("holdout", {}).get("net_mean_bps"),
        signal_coverage.get("validation_eligible_timestamp_count"),
        signal_coverage.get("average_eligible_symbols_per_timestamp"),
    ]
    input_complete = all(value is not None for value in required_metric_values)
    if not metric_integrity_passed or not safety_review_passed:
        result_class = INVALIDATED_CLASS
    elif not input_complete:
        result_class = INCONCLUSIVE_CLASS
    elif diagnostic_promising:
        result_class = PROMISING_CLASS
    else:
        result_class = REJECTED_CLASS

    evaluation_policy = {
        "diagnostic_promising_requires_all_conditions": [
            "validation_net_metric_bps > 0",
            "validation_positive_after_cost is true",
            "null_baseline_review_preliminary_passed is true",
            "monthly_stability_review_preliminary_passed is true",
            "signal_coverage_review_preliminary_passed is true",
            "turnover_concentration_review_preliminary_passed is true",
            "metric_integrity_passed is true",
            "safety_review_passed is true",
        ],
        "holdout_reported_separately": True,
        "holdout_positive_cannot_override_validation_failure": True,
        "holdout_used_for_config_selection": False,
        "candidate_generation_from_holdout_allowed": False,
        "edge_claim_from_holdout_allowed": False,
    }

    evaluator_findings = {
        "diagnostic_promising": diagnostic_promising,
        "validation_net_metric_bps_positive": validation_net_positive,
        "validation_positive_after_cost": validation_positive_after_cost,
        "null_baseline_review_preliminary_passed": null_passed,
        "monthly_stability_review_preliminary_passed": monthly_passed,
        "signal_coverage_review_preliminary_passed": coverage_passed,
        "turnover_concentration_review_preliminary_passed": turnover_passed,
        "metric_integrity_passed": metric_integrity_passed,
        "safety_review_passed": safety_review_passed,
        "result_reason": (
            "validation failed after-cost and null requirements"
            if result_class == REJECTED_CLASS
            else "see result classification"
        ),
    }

    followup_permissions = {
        "closure_record_required_next": True,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "holdout_access_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    forbidden_actions_confirmed_false = {
        "execution_rerun": False,
        "basis_premium_rows_read": False,
        "network_used": False,
        "candidate_generation": False,
        "edge_claim": False,
        "family_release": False,
        "holdout_permission": False,
        "runtime_live_capital_permission": False,
    }
    validation_checks = {
        "execution_artifact_loaded": True,
        "execution_status_verified": execution.get("status") == EXECUTION_STATUS,
        "route_family_verified": execution.get("route_family") == ROUTE_FAMILY,
        "config_id_verified": execution.get("config_id") == CONFIG_ID,
        "execution_replacement_checks_true": execution.get("replacement_checks_all_true") is True,
        "execution_exactly_one_config": config_result.get("config_count_executed") == 1,
        "no_execution_rerun": True,
        "no_external_rows_read": True,
        "no_network_used": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_holdout_permission": True,
        "no_runtime_live_capital": True,
        "metric_integrity_passed_preserved": metric_integrity_passed,
        "safety_review_passed": safety_review_passed,
        "closure_record_required_next": True,
        "replacement_checks_all_true": False,
    }
    validation_checks["replacement_checks_all_true"] = all(
        value is True
        for key, value in validation_checks.items()
        if key != "replacement_checks_all_true" and isinstance(value, bool)
    )

    if not validation_checks["replacement_checks_all_true"]:
        print("BLOCKED: evaluator validation checks failed")
        for key in sorted(validation_checks):
            if validation_checks[key] is not True:
                print(f"{key}: {validation_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "prior_execution_preserved": {
            "path": EXECUTION_RELATIVE_PATH,
            "status": execution.get("status"),
            "payload_sha256_excluding_hash": execution.get("payload_sha256_excluding_hash"),
            "config_id": execution.get("config_id"),
        },
        "evaluation_policy": evaluation_policy,
        "execution_results_evaluated": {
            "config_id": CONFIG_ID,
            "train_gross_bps": config_result.get("train", {}).get("gross_mean_bps"),
            "train_net_bps": config_result.get("train", {}).get("net_mean_bps"),
            "validation_gross_bps": config_result.get("validation", {}).get("gross_mean_bps"),
            "validation_net_bps": config_result.get("validation", {}).get("net_mean_bps"),
            "holdout_gross_bps": config_result.get("holdout", {}).get("gross_mean_bps"),
            "holdout_net_bps": config_result.get("holdout", {}).get("net_mean_bps"),
            "validation_positive_after_cost": validation_positive_after_cost,
            "holdout_used_for_config_selection": False,
        },
        "signal_coverage_findings": {
            "validation_eligible_timestamp_count": signal_coverage.get(
                "validation_eligible_timestamp_count"
            ),
            "average_eligible_symbols_per_timestamp": signal_coverage.get(
                "average_eligible_symbols_per_timestamp"
            ),
            "signal_coverage_review_preliminary_passed": coverage_passed,
        },
        "side_performance_findings": {
            "long_validation_gross_bps": side_summary.get("long_validation_gross_bps"),
            "long_validation_net_bps": side_summary.get("long_validation_net_bps"),
            "short_validation_gross_bps": side_summary.get("short_validation_gross_bps"),
            "short_validation_net_bps": side_summary.get("short_validation_net_bps"),
            "long_validation_selection_count": side_summary.get("long_validation_selection_count"),
            "short_validation_selection_count": side_summary.get("short_validation_selection_count"),
        },
        "premium_basis_findings": {
            "global_min_basis_close": premium_basis.get("global_min_basis_close"),
            "global_max_basis_close": premium_basis.get("global_max_basis_close"),
            "validation_average_long_basis_z": premium_basis.get("validation_average_long_basis_z"),
            "validation_average_short_basis_z": premium_basis.get("validation_average_short_basis_z"),
            "validation_average_long_premium_close": premium_basis.get(
                "validation_average_long_premium_close"
            ),
            "validation_average_short_premium_close": premium_basis.get(
                "validation_average_short_premium_close"
            ),
            "P1_attention_preserved_from_data_review": premium_basis.get(
                "P1_attention_preserved_from_data_review"
            ),
        },
        "evaluator_findings": evaluator_findings,
        "result_classification": result_class,
        "followup_permissions": followup_permissions,
        "forbidden_actions_confirmed_false": forbidden_actions_confirmed_false,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": None,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2)
        handle.write("\n")

    print(f"status: {STATUS}")
    print(f"artifact_path: {ARTIFACT_PATH}")
    print(f"result_classification: {result_class}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print(f"validation_net_metric_bps: {validation_net_metric_bps}")
    print(f"validation_positive_after_cost: {str(validation_positive_after_cost).lower()}")
    print(f"null_baseline_review_preliminary_passed: {str(null_passed).lower()}")
    print(f"monthly_stability_review_preliminary_passed: {str(monthly_passed).lower()}")
    print(f"signal_coverage_review_preliminary_passed: {str(coverage_passed).lower()}")
    print(f"turnover_concentration_review_preliminary_passed: {str(turnover_passed).lower()}")
    print(f"metric_integrity_passed: {str(metric_integrity_passed).lower()}")
    print("candidate_generation_allowed_now: false")
    print("edge_claim_allowed_now: false")
    print("family_release_allowed_now: false")
    print("holdout_permission_allowed_now: false")
    print("runtime_live_capital_allowed_now: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("replacement_checks_all_true: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
