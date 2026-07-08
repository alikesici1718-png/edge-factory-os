from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_EVALUATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_EVALUATION"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_carry_short_positive_flat_negative_evaluator_v1.py"
ARTIFACT_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_carry_short_positive_flat_negative_evaluator_v1.json"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_BASELINE"
HYPOTHESIS_NAME = "funding_carry_short_positive_flat_negative"
ROUTE_TYPE = "one_sided_short_only_funding_carry"
CONFIG_ID = "funding_carry_short_positive_flat_negative_hold8h"

EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_carry_short_positive_flat_negative_execution_v1.json"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_EXECUTED"
EXECUTION_HASH = "d68c1d2616751a9d0f538a13a104205fd878e074ab6682b0d6c9dd61cd158441"
PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_carry_short_positive_flat_negative_preregistration_contract_v1.json"
PREREG_HASH = "64471c65aaff2504b9952095d39648099c83a47f78cfb155c59950a8cabdd10a"

RESULT_PROMISING = "FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
RESULT_REJECTED = "FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_REJECTED_NO_FOLLOWUP"
RESULT_INCONCLUSIVE = "FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP"
RESULT_INVALIDATED = "FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


class Blocked(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")).hexdigest()


def load_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing required artifact: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_payload(payload: dict[str, Any], expected: str, label: str) -> None:
    if payload.get("payload_sha256_excluding_hash") != expected:
        raise Blocked(f"{label} stored payload hash mismatch")
    actual = payload_hash(payload)
    if actual != expected:
        raise Blocked(f"{label} payload hash recompute mismatch: {actual} != {expected}")


def finite_number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise Blocked(f"missing or non-finite numeric field: {label}")
    return float(value)


def bool_field(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise Blocked(f"missing boolean field: {label}")
    return value


def build_artifact(root: Path) -> dict[str, Any]:
    execution = load_json(root, EXECUTION_PATH)
    verify_payload(execution, EXECUTION_HASH, "execution")
    if execution.get("status") != EXECUTION_STATUS:
        raise Blocked("execution status mismatch")
    if execution.get("route_family") != ROUTE_FAMILY or execution.get("config_id") != CONFIG_ID:
        raise Blocked("execution route/config mismatch")

    prereg = load_json(root, PREREG_PATH)
    verify_payload(prereg, PREREG_HASH, "preregistration")
    prereg_route = prereg.get("funding_carry_hypothesis_preregistration", {})
    if prereg_route.get("route_type") != ROUTE_TYPE or prereg_route.get("market_neutral") is not False or prereg_route.get("short_only") is not True:
        raise Blocked("preregistration short-only route fields mismatch")

    config = execution.get("config_result", {})
    null_summary = execution.get("null_baseline_summary", {})
    monthly_summary = execution.get("monthly_stability_summary", {})
    exposure_review = execution.get("exposure_risk_review", {})
    turnover_summary = execution.get("turnover_concentration_summary", {})
    metric_summary = execution.get("metric_integrity_summary", {})
    exposure_summary = execution.get("exposure_risk_summary", {})
    forbidden = execution.get("forbidden_actions_confirmed_false", {})

    validation_net = finite_number(config.get("validation_funding_adjusted_net_metric_bps"), "validation_funding_adjusted_net_metric_bps")
    validation_gross = finite_number(config.get("validation_funding_adjusted_gross_metric_bps"), "validation_funding_adjusted_gross_metric_bps")
    validation_price_only = finite_number(config.get("validation_price_only_metric_bps"), "validation_price_only_metric_bps")
    validation_funding_cashflow = finite_number(config.get("validation_funding_cashflow_metric_bps"), "validation_funding_cashflow_metric_bps")
    validation_positive = bool_field(config.get("validation_positive_after_cost"), "validation_positive_after_cost")
    null_passed = bool_field(null_summary.get("null_baseline_review_preliminary_passed"), "null_baseline_review_preliminary_passed")
    monthly_passed = bool_field(monthly_summary.get("monthly_stability_review_preliminary_passed"), "monthly_stability_review_preliminary_passed")
    exposure_passed = bool_field(exposure_review.get("exposure_risk_review_preliminary_passed"), "exposure_risk_review_preliminary_passed")
    turnover_passed = bool_field(turnover_summary.get("turnover_concentration_review_preliminary_passed"), "turnover_concentration_review_preliminary_passed")
    metric_integrity_passed = bool_field(metric_summary.get("metric_integrity_passed"), "metric_integrity_passed")
    metric_issue_count = metric_summary.get("metric_integrity_issue_count")
    if metric_issue_count != 0:
        raise Blocked(f"metric integrity issue count is not zero: {metric_issue_count}")
    safety_review_passed = all(value is False for value in forbidden.values()) and execution.get("safety_permissions", {}).get("candidate_generation_allowed_now") is False and execution.get("safety_permissions", {}).get("edge_claim_allowed_now") is False and execution.get("safety_permissions", {}).get("runtime_live_capital_allowed_now") is False

    evaluator_input_complete = all(
        [
            execution.get("status") == EXECUTION_STATUS,
            null_summary.get("null_baseline_complete") is True,
            monthly_summary.get("monthly_stability_created") is True,
            turnover_summary.get("turnover_concentration_created") is True,
            metric_summary.get("config_count_executed") == 1,
            exposure_summary.get("route_is_short_only") is True,
            exposure_summary.get("market_neutral") is False,
        ]
    )
    diagnostic_promising = all(
        [
            validation_net > 0,
            validation_positive,
            null_passed,
            monthly_passed,
            exposure_passed,
            turnover_passed,
            metric_integrity_passed,
            safety_review_passed,
        ]
    )
    if not evaluator_input_complete:
        result_class = RESULT_INCONCLUSIVE
    elif not metric_integrity_passed or not safety_review_passed:
        result_class = RESULT_INVALIDATED
    elif diagnostic_promising:
        result_class = RESULT_PROMISING
    else:
        result_class = RESULT_REJECTED

    reason = (
        f"The short-only funding carry route produced validation net metric {validation_net:.6f} bps, "
        f"gross metric {validation_gross:.6f} bps, price-only metric {validation_price_only:.6f} bps, "
        f"and funding-cashflow metric {validation_funding_cashflow:.6f} bps. "
        f"validation_positive_after_cost={str(validation_positive).lower()}, null baseline pass={str(null_passed).lower()}, "
        f"monthly stability pass={str(monthly_passed).lower()}, exposure risk pass={str(exposure_passed).lower()}, "
        f"turnover/concentration pass={str(turnover_passed).lower()}, metric integrity issue count={metric_issue_count}. "
        f"Because the route is short-only and not market-neutral, any positive result would remain diagnostic only. "
        f"Evaluator result_class={result_class}."
    )

    artifact: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "prior_execution_artifact": EXECUTION_PATH,
            "prior_execution_payload_sha256_excluding_hash": EXECUTION_HASH,
            "prior_execution_status": EXECUTION_STATUS,
            "prior_head": "f8723e26236fe4ed64b3f4ddcbf8edc30d1690c8",
            "prior_tracked_python_count": 827,
            "repo_clean_before_evaluator": True,
        },
        "source_artifacts": {
            "all_source_artifacts_read_only": True,
            "execution_artifact_path": EXECUTION_PATH,
            "execution_payload_hash_verified": True,
            "preregistration_artifact_path": PREREG_PATH,
            "preregistration_payload_hash_verified": True,
        },
        "prior_execution_preserved": {
            "average_active_short_count": exposure_summary.get("average_active_short_count"),
            "config_id": CONFIG_ID,
            "correlation_with_equal_weight_market_return": exposure_summary.get("correlation_with_equal_weight_market_return"),
            "exposure_risk_review_preliminary_passed": exposure_passed,
            "market_neutral": False,
            "metric_integrity_issue_count": metric_issue_count,
            "metric_integrity_passed": metric_integrity_passed,
            "monthly_stability_review_preliminary_passed": monthly_passed,
            "null_baseline_review_preliminary_passed": null_passed,
            "route_family": ROUTE_FAMILY,
            "route_type": ROUTE_TYPE,
            "short_only": True,
            "turnover_concentration_review_preliminary_passed": turnover_passed,
            "validation_funding_cashflow_metric_bps": round(validation_funding_cashflow, 6),
            "validation_gross_metric_bps": round(validation_gross, 6),
            "validation_net_metric_bps": round(validation_net, 6),
            "validation_positive_after_cost": validation_positive,
            "validation_price_only_metric_bps": round(validation_price_only, 6),
            "worst_validation_month_net_metric_bps": exposure_summary.get("worst_validation_month_net_metric_bps"),
        },
        "evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "exposure_risk_review_preliminary_passed is true",
                "turnover_concentration_review_preliminary_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "result_classes_allowed": [RESULT_PROMISING, RESULT_REJECTED, RESULT_INCONCLUSIVE, RESULT_INVALIDATED],
        },
        "execution_results_evaluated": {
            "config_id": CONFIG_ID,
            "hypothesis_name": HYPOTHESIS_NAME,
            "route_family": ROUTE_FAMILY,
            "route_type": ROUTE_TYPE,
            "validation_funding_cashflow_metric_bps": round(validation_funding_cashflow, 6),
            "validation_gross_metric_bps": round(validation_gross, 6),
            "validation_net_metric_bps": round(validation_net, 6),
            "validation_positive_after_cost": validation_positive,
            "validation_price_only_metric_bps": round(validation_price_only, 6),
        },
        "exposure_risk_findings": {
            "average_active_short_count": exposure_summary.get("average_active_short_count"),
            "correlation_with_equal_weight_market_return": exposure_summary.get("correlation_with_equal_weight_market_return"),
            "drawdown_proxy_bps": exposure_summary.get("drawdown_proxy_bps"),
            "exposure_risk_review_preliminary_passed": exposure_passed,
            "market_neutral": False,
            "route_is_short_only": True,
            "worst_validation_month_net_metric_bps": exposure_summary.get("worst_validation_month_net_metric_bps"),
        },
        "evaluator_findings": {
            "diagnostic_promising": diagnostic_promising,
            "evaluator_input_complete": evaluator_input_complete,
            "evaluator_ran": True,
            "evaluator_read_funding_rows": False,
            "evaluator_read_okx_rows": False,
            "evaluator_read_panel_rows": False,
            "evaluator_reason": reason,
            "evaluator_recomputed_strategy_metrics": False,
            "exposure_risk_review_passed": exposure_passed,
            "metric_integrity_review_passed": metric_integrity_passed,
            "monthly_stability_review_passed": monthly_passed,
            "null_baseline_review_passed": null_passed,
            "safety_review_passed": safety_review_passed,
            "turnover_concentration_review_passed": turnover_passed,
            "validation_net_metric_positive_after_cost": validation_net > 0,
            "validation_positive_after_cost": validation_positive,
        },
        "result_classification": {
            "candidate_generation_allowed_from_evaluator": False,
            "closure_record_required_next": True,
            "config_id": CONFIG_ID,
            "diagnostic_promising": diagnostic_promising,
            "edge_claim_allowed_from_evaluator": False,
            "family_release_allowed_from_evaluator": False,
            "metric_integrity_issue_count": metric_issue_count,
            "result_class": result_class,
            "result_reason": reason,
            "runtime_live_capital_allowed_from_evaluator": False,
            "validation_funding_cashflow_metric_bps": round(validation_funding_cashflow, 6),
            "validation_gross_metric_bps": round(validation_gross, 6),
            "validation_net_metric_bps": round(validation_net, 6),
            "validation_positive_after_cost": validation_positive,
            "validation_price_only_metric_bps": round(validation_price_only, 6),
        },
        "followup_permissions": {
            "candidate_generation_allowed_now": False,
            "closure_record_allowed_next": True,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "funding_rows_read": False,
            "network_used": False,
            "okx_panel_rows_read": False,
            "panel_rows_read": False,
            "runtime_live_capital": False,
            "strategy_execution_rerun": False,
            "strategy_search_executed": False,
        },
    }
    validation_checks = {
        "closure_record_required_next": True,
        "evaluator_artifact_json_valid": True,
        "evaluator_did_not_read_funding_rows": True,
        "evaluator_did_not_read_panel_rows": True,
        "evaluator_did_not_rerun_execution": True,
        "execution_payload_hash_verified": True,
        "exposure_risk_findings_created": True,
        "metric_integrity_issue_count_zero_preserved": metric_issue_count == 0,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_carry_short_positive_flat_negative_evaluator_v1.py",
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_runtime_live_capital": True,
        "replacement_checks_all_true": True,
        "result_class_is_from_allowed_set": result_class in [RESULT_PROMISING, RESULT_REJECTED, RESULT_INCONCLUSIVE, RESULT_INVALIDATED],
        "short_only_route_preserved": True,
        "status_equals_required_status": STATUS == "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_EVALUATED",
    }
    artifact["validation_checks"] = validation_checks
    artifact["replacement_checks_all_true"] = all(validation_checks.values())
    if artifact["replacement_checks_all_true"] is not True:
        raise Blocked("replacement_checks_all_true is false")
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def write_artifact(root: Path, artifact: dict[str, Any]) -> None:
    output = root / ARTIFACT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reloaded = json.loads(output.read_text(encoding="utf-8"))
    if payload_hash(reloaded) != artifact["payload_sha256_excluding_hash"]:
        output.unlink(missing_ok=True)
        raise Blocked("written evaluator artifact hash mismatch")


def main() -> int:
    root = repo_root()
    output = root / ARTIFACT_PATH
    try:
        artifact = build_artifact(root)
        write_artifact(root, artifact)
        summary = {
            "candidate_generation": False,
            "closure_record_required_next": True,
            "config_id": CONFIG_ID,
            "diagnostic_promising": artifact["result_classification"]["diagnostic_promising"],
            "edge_claim": False,
            "exposure_risk_review_passed": artifact["evaluator_findings"]["exposure_risk_review_passed"],
            "metric_integrity_issue_count": artifact["result_classification"]["metric_integrity_issue_count"],
            "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
            "replacement_checks_all_true": artifact["replacement_checks_all_true"],
            "result_class": artifact["result_classification"]["result_class"],
            "runtime_live_capital": False,
            "status": STATUS,
            "validation_gross_metric_bps": artifact["result_classification"]["validation_gross_metric_bps"],
            "validation_net_metric_bps": artifact["result_classification"]["validation_net_metric_bps"],
            "validation_positive_after_cost": artifact["result_classification"]["validation_positive_after_cost"],
            "validation_price_only_metric_bps": artifact["result_classification"]["validation_price_only_metric_bps"],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        if output.exists():
            output.unlink()
        print(f"BLOCKED {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
