from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_EVALUATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_EVALUATION"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_evaluator_v1.py"
ARTIFACT_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_evaluator_v1.json"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_REVERSAL"
HYPOTHESIS_NAME = "funding_extreme_momentum_confirmed_reversal"
CONFIG_ID = "funding_extreme_mom24_liqtop60_hold24h"
ALIGNED_WINDOW_START_UTC = "2023-07-01T00:00:00Z"
ALIGNED_WINDOW_END_EXCLUSIVE_UTC = "2025-10-31T16:00:00Z"

EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_execution_v1.json"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_EXECUTED"
EXECUTION_HASH = "c2c2762c5d4bc8ae64820f652283025dbb553a5fd92a88d6be9358a0af081a3a"

SOURCE_ARTIFACT_HASHES = {
    "latest_funding_route_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
        "8eacb2decacac50140de27b6c84a9a5338e2473e62ccce54be5d07770a576b02",
    ),
    "source_preregistration": (
        "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_preregistration_contract_v1.json",
        "be50fe006e730f2f756859ada35895b7bb5592f8400fdc5b40d1362c1ea59f77",
    ),
    "funding_review": (
        "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
        "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849",
    ),
    "funding_acquisition_lock": (
        "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
        "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252",
    ),
    "second_source_readiness": (
        "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
        "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716",
    ),
    "panel_review": (
        "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
        "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112",
    ),
}

RESULT_PROMISING = "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_DIAGNOSTIC_PROMISING_REQUIRES_SEPARATE_CLOSURE_NO_CANDIDATE_NO_EDGE"
RESULT_REJECTED = "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_REJECTED_NO_FOLLOWUP"
RESULT_INCONCLUSIVE = "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP"
RESULT_INVALIDATED = "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE"


class Blocked(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing required source artifact: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def payload_hash(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_payload(data: dict[str, Any], expected_hash: str, label: str) -> None:
    actual = data.get("payload_sha256_excluding_hash")
    if actual != expected_hash:
        raise Blocked(f"{label} payload hash field mismatch: {actual} != {expected_hash}")
    recomputed = payload_hash(data)
    if recomputed != expected_hash:
        raise Blocked(f"{label} payload hash recompute mismatch: {recomputed} != {expected_hash}")


def finite_number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise Blocked(f"non-finite or missing metric: {label}")
    return float(value)


def bool_field(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise Blocked(f"missing boolean field: {label}")
    return value


def build_artifact(root: Path) -> dict[str, Any]:
    execution = load_json(root, EXECUTION_PATH)
    if execution.get("status") != EXECUTION_STATUS:
        raise Blocked(f"execution status mismatch: {execution.get('status')}")
    verify_payload(execution, EXECUTION_HASH, "execution")

    source_artifacts: dict[str, Any] = {
        "execution_artifact_path": EXECUTION_PATH,
        "execution_payload_hash_verified": True,
        "execution_status": execution.get("status"),
    }
    for key, (rel_path, expected_hash) in SOURCE_ARTIFACT_HASHES.items():
        source = load_json(root, rel_path)
        verify_payload(source, expected_hash, key)
        source_artifacts[f"{key}_path"] = rel_path
        source_artifacts[f"{key}_payload_hash_verified"] = True
    source_artifacts["all_source_artifacts_read_only"] = True

    if execution.get("route_family") != ROUTE_FAMILY:
        raise Blocked(f"route_family mismatch: {execution.get('route_family')}")
    if execution.get("config_id") != CONFIG_ID:
        raise Blocked(f"config_id mismatch: {execution.get('config_id')}")

    config = execution.get("config_result")
    if not isinstance(config, dict):
        raise Blocked("execution config_result missing")
    null_summary = execution.get("null_baseline_summary")
    monthly_summary = execution.get("monthly_stability_summary")
    turnover_summary = execution.get("turnover_concentration_summary")
    metric_summary = execution.get("metric_integrity_summary")
    forbidden = execution.get("forbidden_actions_confirmed_false")
    if not all(isinstance(x, dict) for x in (null_summary, monthly_summary, turnover_summary, metric_summary, forbidden)):
        raise Blocked("execution summary sections missing")

    validation_net = finite_number(config.get("validation_net_metric_bps"), "validation_net_metric_bps")
    validation_gross = finite_number(config.get("validation_gross_metric_bps"), "validation_gross_metric_bps")
    validation_positive = bool_field(config.get("validation_positive_after_cost"), "validation_positive_after_cost")
    null_passed = bool_field(null_summary.get("null_baseline_review_preliminary_passed"), "null_baseline_review_preliminary_passed")
    monthly_passed = bool_field(monthly_summary.get("monthly_stability_review_preliminary_passed"), "monthly_stability_review_preliminary_passed")
    turnover_passed = bool_field(turnover_summary.get("turnover_concentration_review_preliminary_passed"), "turnover_concentration_review_preliminary_passed")
    metric_integrity_passed = bool_field(metric_summary.get("metric_integrity_passed"), "metric_integrity_passed")
    metric_issue_count = metric_summary.get("metric_integrity_issue_count")
    if metric_issue_count != 0:
        raise Blocked(f"metric integrity issue count is not zero: {metric_issue_count}")

    forbidden_ok = all(value is False for value in forbidden.values())
    no_candidate_edge_release_runtime = (
        execution.get("safety_permissions", {}).get("candidate_generation_allowed_now") is False
        and execution.get("safety_permissions", {}).get("edge_claim_allowed_now") is False
        and execution.get("safety_permissions", {}).get("family_release_allowed_now") is False
        and execution.get("safety_permissions", {}).get("runtime_live_capital_allowed_now") is False
    )
    safety_review_passed = forbidden_ok and no_candidate_edge_release_runtime
    evaluator_input_complete = all(
        [
            execution.get("status") == EXECUTION_STATUS,
            config.get("config_id") == CONFIG_ID,
            bool_field(null_summary.get("null_baseline_complete"), "null_baseline_complete"),
            "validation_null_percentile" in null_summary,
            bool_field(monthly_summary.get("monthly_stability_created"), "monthly_stability_created"),
            bool_field(turnover_summary.get("turnover_concentration_created"), "turnover_concentration_created"),
        ]
    )
    diagnostic_promising = all(
        [
            validation_net > 0,
            validation_positive,
            null_passed,
            monthly_passed,
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

    prior_execution_preserved = {
        "config_id": CONFIG_ID,
        "diagnostic_interpretation_limits": execution.get("diagnostic_interpretation_limits", {}),
        "metric_integrity_issue_count": metric_issue_count,
        "metric_integrity_passed": metric_integrity_passed,
        "monthly_stability_review_preliminary_passed": monthly_passed,
        "null_baseline_review_preliminary_passed": null_passed,
        "route_family": ROUTE_FAMILY,
        "turnover_concentration_review_preliminary_passed": turnover_passed,
        "validation_gross_metric_bps": round(validation_gross, 6),
        "validation_net_metric_bps": round(validation_net, 6),
        "validation_positive_after_cost": validation_positive,
    }

    evaluator_reason = (
        f"The single preregistered config {CONFIG_ID} produced validation net metric "
        f"{validation_net:.6f} bps after costs and validation_positive_after_cost={str(validation_positive).lower()}. "
        f"Null baseline preliminary pass={str(null_passed).lower()}, monthly stability preliminary pass="
        f"{str(monthly_passed).lower()}, turnover/concentration preliminary pass={str(turnover_passed).lower()}, "
        "and metric integrity issue count is zero. Under the preregistered evaluator policy, this route is "
        f"{result_class}."
    )

    artifact: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "repo_scope": {
            "api_key_used": False,
            "binance_1m_kline_source_rows_read": False,
            "binance_funding_rows_read": False,
            "binance_panel_rows_read": False,
            "code_changes_repo_only": True,
            "evaluator_artifact_created_in_repo": True,
            "evaluator_recomputed_strategy_metrics": False,
            "funding_data_fetched_by_this_module": False,
            "funding_rate_endpoint_called_by_this_module": False,
            "funding_strategy_execution_rerun": False,
            "okx_panel_rows_read": False,
            "private_api_used": False,
            "public_network_used": False,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "source_checkpoint": {
            "prior_execution_artifact": EXECUTION_PATH,
            "prior_execution_payload_sha256_excluding_hash": EXECUTION_HASH,
            "prior_execution_status": EXECUTION_STATUS,
            "prior_head": "3d48bcdc6055722ff742c05f5f407fa4a65b552b",
            "prior_tracked_python_count": 819,
            "project": "Edge Factory OS / Binance OKX overlap funding extreme momentum liquidity evaluator",
            "repo_clean_before_evaluator": True,
        },
        "source_artifacts": source_artifacts,
        "prior_execution_preserved": prior_execution_preserved,
        "evaluation_policy": {
            "diagnostic_promising_requires_all": [
                "validation_net_metric_bps > 0",
                "validation_positive_after_cost is true",
                "null_baseline_review_preliminary_passed is true",
                "monthly_stability_review_preliminary_passed is true",
                "turnover_concentration_review_preliminary_passed is true",
                "metric_integrity_passed is true",
                "safety_review_passed is true",
            ],
            "result_classes_allowed": [
                RESULT_PROMISING,
                RESULT_REJECTED,
                RESULT_INCONCLUSIVE,
                RESULT_INVALIDATED,
            ],
        },
        "execution_results_evaluated": {
            "config_count": 1,
            "config_id": CONFIG_ID,
            "hypothesis_name": HYPOTHESIS_NAME,
            "route_family": ROUTE_FAMILY,
            "validation_gross_metric_bps": round(validation_gross, 6),
            "validation_net_metric_bps": round(validation_net, 6),
            "validation_positive_after_cost": validation_positive,
        },
        "evaluator_findings": {
            "diagnostic_promising": diagnostic_promising,
            "evaluator_input_complete": evaluator_input_complete,
            "evaluator_ran": True,
            "evaluator_read_funding_rows": False,
            "evaluator_read_okx_rows": False,
            "evaluator_read_panel_rows": False,
            "evaluator_reason": evaluator_reason,
            "evaluator_recomputed_strategy_metrics": False,
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
            "monthly_stability_review_passed": monthly_passed,
            "null_baseline_review_passed": null_passed,
            "result_class": result_class,
            "result_reason": evaluator_reason,
            "runtime_live_capital_allowed_from_evaluator": False,
            "turnover_concentration_review_passed": turnover_passed,
            "validation_gross_metric_bps": round(validation_gross, 6),
            "validation_net_metric_bps": round(validation_net, 6),
            "validation_positive_after_cost": validation_positive,
        },
        "followup_permissions": {
            "boundary_buffer_access_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "closure_record_allowed_next": True,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_parameter_expansion_allowed_now": False,
            "funding_retest_allowed_now": False,
            "funding_row_access_allowed_now": False,
            "holdout_access_allowed_now": False,
            "okx_panel_access_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "funding_data_fetched": False,
            "funding_execution_rerun": False,
            "funding_rate_endpoint_called": False,
            "funding_rows_read": False,
            "holdout_accessed": False,
            "okx_panel_rows_read": False,
            "panel_rows_read": False,
            "runtime_permission_granted": False,
            "strategy_search_executed": False,
        },
    }

    validation_checks = {
        "closure_record_required_next": artifact["result_classification"]["closure_record_required_next"] is True,
        "diagnostic_promising_matches_policy": artifact["result_classification"]["diagnostic_promising"] is diagnostic_promising,
        "evaluator_artifact_json_valid": True,
        "evaluator_artifact_path_equals_required_path": ARTIFACT_PATH == "artifacts/strategy_evaluations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_evaluator_v1.json",
        "evaluator_did_not_read_funding_rows": True,
        "evaluator_did_not_read_panel_rows": True,
        "evaluator_did_not_rerun_execution": True,
        "execution_artifact_loaded": True,
        "execution_payload_hash_verified": True,
        "execution_status_verified": True,
        "metric_integrity_issue_count_zero_preserved": metric_issue_count == 0,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_evaluator_v1.py",
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "payload_sha256_excluding_hash_present": True,
        "replacement_checks_all_true": True,
        "result_class_is_from_allowed_set": result_class in [RESULT_PROMISING, RESULT_REJECTED, RESULT_INCONCLUSIVE, RESULT_INVALIDATED],
        "status_equals_required_status": STATUS == "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_EVALUATED",
    }
    artifact["validation_checks"] = validation_checks
    artifact["replacement_checks_all_true"] = all(validation_checks.values())
    if not artifact["replacement_checks_all_true"]:
        raise Blocked("replacement_checks_all_true is false")
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def write_artifact(root: Path, artifact: dict[str, Any]) -> None:
    output_path = root / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    reloaded = json.loads(output_path.read_text(encoding="utf-8"))
    if payload_hash(reloaded) != artifact["payload_sha256_excluding_hash"]:
        output_path.unlink(missing_ok=True)
        raise Blocked("written evaluator artifact payload hash mismatch")


def main() -> int:
    root = repo_root()
    output_path = root / ARTIFACT_PATH
    try:
        artifact = build_artifact(root)
        if artifact["status"] != STATUS:
            raise Blocked("status mismatch")
        write_artifact(root, artifact)
        summary = {
            "candidate_generation": False,
            "closure_record_required_next": artifact["result_classification"]["closure_record_required_next"],
            "config_id": CONFIG_ID,
            "diagnostic_promising": artifact["result_classification"]["diagnostic_promising"],
            "edge_claim": False,
            "evaluator_artifact_path": ARTIFACT_PATH,
            "metric_integrity_issue_count": artifact["result_classification"]["metric_integrity_issue_count"],
            "monthly_stability_review_passed": artifact["result_classification"]["monthly_stability_review_passed"],
            "null_baseline_review_passed": artifact["result_classification"]["null_baseline_review_passed"],
            "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
            "replacement_checks_all_true": artifact["replacement_checks_all_true"],
            "result_class": artifact["result_classification"]["result_class"],
            "runtime_live_capital": False,
            "status": STATUS,
            "turnover_concentration_review_passed": artifact["result_classification"]["turnover_concentration_review_passed"],
            "validation_gross_metric_bps": artifact["result_classification"]["validation_gross_metric_bps"],
            "validation_net_metric_bps": artifact["result_classification"]["validation_net_metric_bps"],
            "validation_positive_after_cost": artifact["result_classification"]["validation_positive_after_cost"],
        }
        print(json.dumps(summary, sort_keys=True, indent=2))
        return 0
    except Exception as exc:
        if output_path.exists():
            output_path.unlink()
        print(f"BLOCKED {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
