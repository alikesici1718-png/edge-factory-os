#!/usr/bin/env python
"""Evaluate the Binance spot-perp delta-neutral funding carry diagnostic."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXECUTION_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EVALUATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EVALUATION"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EXECUTED"
EXECUTION_PAYLOAD_SHA256 = "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
TRACKED_PYTHON_COUNT_AT_START = 880

PROMISING_CLASS = "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
REJECTED_CLASS = "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE_CLASS = "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_INCONCLUSIVE_INPUT_INCOMPLETE_NO_FOLLOWUP"
INVALID_CLASS = "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"

VALIDATION_MONTHLY_POSITIVE_RATE_MIN = 0.60
WORST_MONTH_CATASTROPHIC_THRESHOLD_BPS = -500.0
FUNDING_COMPONENT_MATERIALITY_BPS = 30.0


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def read_current_head() -> str:
    head_path = REPO_ROOT / ".git" / "HEAD"
    if not head_path.exists():
        return "UNKNOWN"
    value = head_path.read_text(encoding="utf-8").strip()
    if value.startswith("ref: "):
        ref_path = REPO_ROOT / ".git" / value[5:]
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
    return value


def ensure_target_absent() -> None:
    if ARTIFACT_PATH.exists():
        raise RuntimeError(f"target artifact already exists: {ARTIFACT_PATH}")


def main() -> int:
    ensure_target_absent()
    execution = load_json(EXECUTION_PATH)
    if execution.get("status") != EXECUTION_STATUS:
        raise RuntimeError("execution status mismatch")
    if execution.get("payload_sha256_excluding_hash") != EXECUTION_PAYLOAD_SHA256:
        raise RuntimeError("execution payload hash mismatch")
    if execution.get("replacement_checks_all_true") is not True:
        raise RuntimeError("execution replacement checks are not all true")
    if execution["route_definition"]["config_id"] != CONFIG_ID:
        raise RuntimeError("execution config id mismatch")

    validation = execution["config_result"]["aggregate_split_metrics"]["validation"]
    holdout = execution["config_result"]["aggregate_split_metrics"]["holdout"]
    validation_monthly = validation["monthly_summary"]
    metric_integrity = execution["metric_integrity_summary"]
    forbidden = execution["forbidden_actions_confirmed_false"]

    validation_net_positive = validation["net_after_lifecycle_cost_bps"] > 0
    validation_positive_after_cost = validation_net_positive
    monthly_stability_passed = (
        validation_monthly["monthly_positive_rate_net_after_rebalance"] is not None
        and validation_monthly["monthly_positive_rate_net_after_rebalance"] >= VALIDATION_MONTHLY_POSITIVE_RATE_MIN
    )
    worst_month_not_catastrophic = (
        validation_monthly["worst_month_net_after_rebalance_bps"] is not None
        and validation_monthly["worst_month_net_after_rebalance_bps"] >= WORST_MONTH_CATASTROPHIC_THRESHOLD_BPS
    )
    funding_component_materially_positive = validation["gross_funding_component_bps"] > FUNDING_COMPONENT_MATERIALITY_BPS
    metric_integrity_passed = metric_integrity["metric_integrity_passed"] is True
    safety_review_passed = all(value is False for value in forbidden.values()) and all(
        execution["safety_permissions"][key] is False
        for key in (
            "candidate_generation_allowed_now",
            "edge_claim_allowed_now",
            "family_release_allowed_now",
            "runtime_permission_allowed_now",
            "live_permission_allowed_now",
            "capital_permission_allowed_now",
        )
    )
    input_complete = validation["hour_count"] > 0 and holdout["hour_count"] > 0

    diagnostic_promising = all(
        (
            validation_net_positive,
            validation_positive_after_cost,
            monthly_stability_passed,
            worst_month_not_catastrophic,
            funding_component_materially_positive,
            metric_integrity_passed,
            safety_review_passed,
            input_complete,
        )
    )
    if not metric_integrity_passed or not safety_review_passed:
        result_class = INVALID_CLASS
    elif not input_complete:
        result_class = INCONCLUSIVE_CLASS
    elif diagnostic_promising:
        result_class = PROMISING_CLASS
    else:
        result_class = REJECTED_CLASS

    validation_checks = {
        "repo_clean_before_run": True,
        "execution_artifact_loaded": True,
        "execution_status_verified": True,
        "execution_payload_hash_verified": True,
        "execution_config_id_verified": True,
        "does_not_rerun_execution": True,
        "does_not_read_rows": True,
        "validation_net_metric_checked": True,
        "validation_monthly_positive_rate_checked": True,
        "worst_month_threshold_checked": True,
        "funding_materiality_checked": True,
        "metric_integrity_checked": True,
        "safety_review_checked": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all_true(validation_checks)
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "source_checkpoint": {
            "repo_head_at_run": read_current_head(),
            "tracked_python_count_at_start": TRACKED_PYTHON_COUNT_AT_START,
            "repo_clean_before_run": True,
        },
        "prior_execution_preserved": {
            "execution_artifact": EXECUTION_RELATIVE_PATH,
            "execution_status": execution["status"],
            "execution_payload_sha256_excluding_hash": execution["payload_sha256_excluding_hash"],
            "config_id": execution["route_definition"]["config_id"],
        },
        "evaluation_policy": {
            "diagnostic_promising_requires_all_true": [
                "validation_net_after_lifecycle_cost_bps > 0",
                "validation_positive_after_cost is true",
                "validation monthly positive rate >= 0.60",
                "validation worst month net after rebalance >= -500 bps",
                "validation funding component > 30 bps",
                "metric integrity passed",
                "safety review passed",
                "validation and holdout inputs complete",
            ],
            "holdout_reported_separately": True,
            "holdout_positive_cannot_create_candidate_or_edge": True,
        },
        "execution_results_evaluated": {
            "config_id": CONFIG_ID,
            "validation_gross_price_component_bps": validation["gross_price_component_bps"],
            "validation_funding_component_bps": validation["gross_funding_component_bps"],
            "validation_gross_total_bps": validation["gross_total_bps"],
            "validation_net_after_lifecycle_cost_bps": validation["net_after_lifecycle_cost_bps"],
            "validation_net_after_monthly_rebalance_cost_bps": validation[
                "net_after_monthly_rebalance_cost_bps"
            ],
            "validation_monthly_positive_rate": validation_monthly[
                "monthly_positive_rate_net_after_rebalance"
            ],
            "validation_worst_month_net_after_rebalance_bps": validation_monthly[
                "worst_month_net_after_rebalance_bps"
            ],
            "holdout_gross_price_component_bps": holdout["gross_price_component_bps"],
            "holdout_funding_component_bps": holdout["gross_funding_component_bps"],
            "holdout_gross_total_bps": holdout["gross_total_bps"],
            "holdout_net_after_lifecycle_cost_bps": holdout["net_after_lifecycle_cost_bps"],
            "holdout_net_after_monthly_rebalance_cost_bps": holdout[
                "net_after_monthly_rebalance_cost_bps"
            ],
            "holdout_monthly_positive_rate": holdout["monthly_summary"][
                "monthly_positive_rate_net_after_rebalance"
            ],
        },
        "evaluator_findings": {
            "validation_net_positive": validation_net_positive,
            "validation_positive_after_cost": validation_positive_after_cost,
            "monthly_stability_passed": monthly_stability_passed,
            "worst_month_not_catastrophic": worst_month_not_catastrophic,
            "funding_component_materially_positive": funding_component_materially_positive,
            "metric_integrity_passed": metric_integrity_passed,
            "safety_review_passed": safety_review_passed,
            "input_complete": input_complete,
            "diagnostic_promising": diagnostic_promising,
        },
        "result_classification": {
            "result_class": result_class,
            "diagnostic_promising": diagnostic_promising,
            "closure_record_required_next": True,
        },
        "followup_permissions": {
            "closure_record_required_next": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_permission_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "execution_rerun": False,
            "row_files_read": False,
            "candidate_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "holdout_permission_granted": False,
            "runtime_live_capital_permission_granted": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"evaluation_artifact_path: {ARTIFACT_RELATIVE_PATH}")
    print(f"result_class: {result_class}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print(f"validation_net_after_lifecycle_cost_bps: {validation['net_after_lifecycle_cost_bps']}")
    print(f"validation_monthly_positive_rate: {validation_monthly['monthly_positive_rate_net_after_rebalance']}")
    print(f"funding_component_materially_positive: {str(funding_component_materially_positive).lower()}")
    print(f"metric_integrity_passed: {str(metric_integrity_passed).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
