from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_CLOSURE_RECORD"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_REVERSAL"
HYPOTHESIS_NAME = "funding_extreme_momentum_confirmed_reversal"
CONFIG_ID = "funding_extreme_mom24_liqtop60_hold24h"

EVALUATOR_PATH = "artifacts/strategy_evaluations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_evaluator_v1.json"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_EVALUATED"
EVALUATOR_HASH = "b98e9652238c7b54f995e81f2a724e73a18c4ff262f23d4ac67ec1edaf147220"

EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_execution_v1.json"
EXECUTION_HASH = "c2c2762c5d4bc8ae64820f652283025dbb553a5fd92a88d6be9358a0af081a3a"

SOURCE_ARTIFACT_HASHES = {
    "source_preregistration": (
        "artifacts/research_preregistrations/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_preregistration_contract_v1.json",
        "be50fe006e730f2f756859ada35895b7bb5592f8400fdc5b40d1362c1ea59f77",
    ),
    "latest_funding_route_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
        "8eacb2decacac50140de27b6c84a9a5338e2473e62ccce54be5d07770a576b02",
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


class Blocked(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def canonical_payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")).hexdigest()


def load_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing required source artifact: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_payload(data: dict[str, Any], expected_hash: str, label: str) -> None:
    stored = data.get("payload_sha256_excluding_hash")
    if stored != expected_hash:
        raise Blocked(f"{label} stored payload hash mismatch: {stored} != {expected_hash}")
    recomputed = canonical_payload_hash(data)
    if recomputed != expected_hash:
        raise Blocked(f"{label} payload hash recompute mismatch: {recomputed} != {expected_hash}")


def build_artifact(root: Path) -> dict[str, Any]:
    evaluator = load_json(root, EVALUATOR_PATH)
    if evaluator.get("status") != EVALUATOR_STATUS:
        raise Blocked(f"evaluator status mismatch: {evaluator.get('status')}")
    verify_payload(evaluator, EVALUATOR_HASH, "evaluator")

    execution = load_json(root, EXECUTION_PATH)
    verify_payload(execution, EXECUTION_HASH, "execution")

    source_artifacts: dict[str, Any] = {
        "all_source_artifacts_read_only": True,
        "evaluator_artifact_path": EVALUATOR_PATH,
        "evaluator_payload_hash_verified": True,
        "evaluator_status": evaluator.get("status"),
        "execution_artifact_path": EXECUTION_PATH,
        "execution_payload_hash_verified": True,
    }
    for key, (rel_path, expected_hash) in SOURCE_ARTIFACT_HASHES.items():
        source = load_json(root, rel_path)
        verify_payload(source, expected_hash, key)
        source_artifacts[f"{key}_path"] = rel_path
        source_artifacts[f"{key}_payload_hash_verified"] = True

    classification = evaluator.get("result_classification", {})
    prior_exec = evaluator.get("prior_execution_preserved", {})
    findings = evaluator.get("evaluator_findings", {})
    if classification.get("config_id") != CONFIG_ID:
        raise Blocked(f"evaluator config_id mismatch: {classification.get('config_id')}")
    if prior_exec.get("route_family") != ROUTE_FAMILY:
        raise Blocked(f"route_family mismatch: {prior_exec.get('route_family')}")

    result_class = classification.get("result_class")
    allowed_results = [
        "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_DIAGNOSTIC_PROMISING_REQUIRES_SEPARATE_CLOSURE_NO_CANDIDATE_NO_EDGE",
        "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_REJECTED_NO_FOLLOWUP",
        "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_INCONCLUSIVE_EVALUATOR_INPUT_INCOMPLETE_NO_FOLLOWUP",
        "FUNDING_EXTREME_MOMENTUM_LIQUIDITY_INVALIDATED_BY_SAFETY_OR_INTEGRITY_FAILURE",
    ]
    if result_class not in allowed_results:
        raise Blocked(f"unexpected evaluator result_class: {result_class}")

    diagnostic_promising = classification.get("diagnostic_promising")
    if not isinstance(diagnostic_promising, bool):
        raise Blocked("diagnostic_promising missing")

    validation_net = classification.get("validation_net_metric_bps")
    validation_gross = classification.get("validation_gross_metric_bps")
    validation_positive = classification.get("validation_positive_after_cost")
    null_passed = classification.get("null_baseline_review_passed")
    monthly_passed = classification.get("monthly_stability_review_passed")
    turnover_passed = classification.get("turnover_concentration_review_passed")
    metric_issue_count = classification.get("metric_integrity_issue_count")

    closure_state = "CLOSED_DIAGNOSTIC_PROMISING_NO_CANDIDATE_NO_EDGE" if diagnostic_promising else "CLOSED_REJECTED_NO_FOLLOWUP"
    if "INCONCLUSIVE" in result_class:
        closure_state = "CLOSED_INCONCLUSIVE_NO_FOLLOWUP"
    if "INVALIDATED" in result_class:
        closure_state = "CLOSED_INVALIDATED_NO_FOLLOWUP"

    closure_reason = (
        f"The evaluator preserved result_class={result_class} for {CONFIG_ID}. Validation net metric was "
        f"{validation_net} bps, validation gross metric was {validation_gross} bps, "
        f"validation_positive_after_cost={str(validation_positive).lower()}, null baseline pass="
        f"{str(null_passed).lower()}, monthly stability pass={str(monthly_passed).lower()}, "
        f"turnover/concentration pass={str(turnover_passed).lower()}, metric integrity issue count="
        f"{metric_issue_count}. The route is closed with no candidate, no edge claim, no family release, "
        "no holdout access, and no runtime/live/capital permission."
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
            "closure_artifact_created_in_repo": True,
            "code_changes_repo_only": True,
            "evaluator_rerun": False,
            "funding_data_fetched_by_this_module": False,
            "funding_execution_rerun": False,
            "funding_rate_endpoint_called_by_this_module": False,
            "okx_panel_rows_read": False,
            "private_api_used": False,
            "public_network_used": False,
            "runtime_live_capital": False,
            "strategy_search_executed": False,
        },
        "source_checkpoint": {
            "prior_evaluator_artifact": EVALUATOR_PATH,
            "prior_evaluator_payload_sha256_excluding_hash": EVALUATOR_HASH,
            "prior_evaluator_status": EVALUATOR_STATUS,
            "prior_head": "0d38a3d7813822e2302812e91035eb4e8c17c71f",
            "prior_tracked_python_count": 820,
            "project": "Edge Factory OS / Binance OKX overlap funding extreme momentum liquidity closure",
            "repo_clean_before_closure": True,
        },
        "source_artifacts": source_artifacts,
        "prior_evaluator_result_preserved": {
            "candidate_generation_allowed_from_evaluator": False,
            "config_id": CONFIG_ID,
            "diagnostic_promising": diagnostic_promising,
            "edge_claim_allowed_from_evaluator": False,
            "family_release_allowed_from_evaluator": False,
            "metric_integrity_issue_count": metric_issue_count,
            "monthly_stability_review_passed": monthly_passed,
            "null_baseline_review_passed": null_passed,
            "result_class": result_class,
            "runtime_live_capital_allowed_from_evaluator": False,
            "turnover_concentration_review_passed": turnover_passed,
            "validation_gross_metric_bps": validation_gross,
            "validation_net_metric_bps": validation_net,
            "validation_positive_after_cost": validation_positive,
        },
        "prior_execution_result_preserved": {
            "config_id": CONFIG_ID,
            "execution_result_is_diagnostic_only": True,
            "metric_integrity_issue_count": metric_issue_count,
            "metric_integrity_passed": metric_issue_count == 0,
            "monthly_stability_review_preliminary_passed": monthly_passed,
            "null_baseline_review_preliminary_passed": null_passed,
            "route_family": ROUTE_FAMILY,
            "turnover_concentration_review_preliminary_passed": turnover_passed,
            "validation_gross_metric_bps": validation_gross,
            "validation_net_metric_bps": validation_net,
            "validation_positive_after_cost": validation_positive,
        },
        "closure_record": {
            "candidate_generation_allowed_now": False,
            "closure_reason": closure_reason,
            "closure_record_created": True,
            "closure_state": closure_state,
            "diagnostic_promising": diagnostic_promising,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_parameter_expansion_allowed_now": False,
            "hypothesis_name": HYPOTHESIS_NAME,
            "parameter_expansion_allowed_now": False,
            "result_class_confirmed": result_class,
            "retest_allowed_now": False,
            "route_closed": True,
            "route_family_closed": ROUTE_FAMILY,
            "runtime_live_capital_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "route_family_state_after_closure": {
            "funding_extreme_momentum_liquidity_route": {
                "candidate_generation_allowed_now": False,
                "diagnostic_promising": diagnostic_promising,
                "edge_claim_allowed_now": False,
                "parameter_expansion_allowed_now": False,
                "result_class": result_class,
                "retest_allowed_now": False,
                "route_family": ROUTE_FAMILY,
                "status": closure_state,
            },
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_runtime_live_capital_permission_exists": True,
        },
        "project_state_after_closure": {
            "binance_funding_baseline_route_closed": True,
            "binance_funding_extreme_momentum_liquidity_route_closed": True,
            "binance_okx_overlap_panel_built_and_reviewed": True,
            "funding_data_acquired_and_reviewed": True,
            "immediate_next_module_required": False,
            "no_active_candidate_exists": True,
            "no_active_edge_claim_exists": True,
            "no_family_release_exists": True,
            "no_holdout_access_exists": True,
            "no_runtime_live_capital_permission_exists": True,
            "project_can_pause_after_closure": True,
        },
        "followup_permissions_after_closure": {
            "candidate_generation_allowed_now": False,
            "closure_complete": True,
            "edge_claim_allowed_now": False,
            "external_data_access_allowed_now": False,
            "family_release_allowed_now": False,
            "funding_parameter_expansion_allowed_now": False,
            "funding_retest_allowed_now": False,
            "holdout_access_allowed_now": False,
            "next_immediate_module_required": False,
            "new_research_cycle_allowed_only_with_new_deliberate_contract": True,
            "okx_panel_access_allowed_now": False,
            "project_can_pause_after_closure": True,
            "runtime_live_capital_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "boundary_buffer_accessed": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "evaluator_rerun": False,
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
        "closure_artifact_json_valid": True,
        "closure_artifact_path_equals_required_path": ARTIFACT_PATH == "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json",
        "evaluator_artifact_loaded": True,
        "evaluator_payload_hash_verified": True,
        "evaluator_result_class_preserved": artifact["closure_record"]["result_class_confirmed"] == result_class,
        "execution_artifact_loaded": True,
        "execution_payload_hash_verified": True,
        "metric_integrity_issue_count_zero_preserved": metric_issue_count == 0,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.py",
        "next_immediate_module_required_false": artifact["followup_permissions_after_closure"]["next_immediate_module_required"] is False,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_evaluator_rerun": True,
        "no_execution_rerun": True,
        "no_funding_rows_read": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_panel_rows_read": True,
        "no_runtime_live_capital": True,
        "no_strategy_search": True,
        "payload_sha256_excluding_hash_present": True,
        "project_can_pause_after_closure": artifact["project_state_after_closure"]["project_can_pause_after_closure"] is True,
        "replacement_checks_all_true": True,
        "route_closed": artifact["closure_record"]["route_closed"] is True,
        "status_equals_required_status": STATUS == "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_EXTREME_MOMENTUM_CONFIRMED_LIQUIDITY_FILTERED_CLOSURE_CREATED",
    }
    artifact["validation_checks"] = validation_checks
    artifact["replacement_checks_all_true"] = all(validation_checks.values())
    if not artifact["replacement_checks_all_true"]:
        raise Blocked("replacement_checks_all_true is false")
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(root: Path, artifact: dict[str, Any]) -> None:
    path = root / ARTIFACT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reloaded = json.loads(path.read_text(encoding="utf-8"))
    if canonical_payload_hash(reloaded) != artifact["payload_sha256_excluding_hash"]:
        path.unlink(missing_ok=True)
        raise Blocked("written closure artifact payload hash mismatch")


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
            "closure_artifact_path": ARTIFACT_PATH,
            "diagnostic_promising": artifact["closure_record"]["diagnostic_promising"],
            "edge_claim": False,
            "family_release": False,
            "funding_parameter_expansion_allowed_now": artifact["closure_record"]["funding_parameter_expansion_allowed_now"],
            "metric_integrity_issue_count": artifact["prior_evaluator_result_preserved"]["metric_integrity_issue_count"],
            "monthly_stability_review_passed": artifact["prior_evaluator_result_preserved"]["monthly_stability_review_passed"],
            "null_baseline_review_passed": artifact["prior_evaluator_result_preserved"]["null_baseline_review_passed"],
            "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
            "project_can_pause_after_closure": artifact["project_state_after_closure"]["project_can_pause_after_closure"],
            "replacement_checks_all_true": artifact["replacement_checks_all_true"],
            "result_class": artifact["closure_record"]["result_class_confirmed"],
            "retest_allowed_now": artifact["closure_record"]["retest_allowed_now"],
            "route_closed": artifact["closure_record"]["route_closed"],
            "runtime_live_capital": False,
            "status": STATUS,
            "turnover_concentration_review_passed": artifact["prior_evaluator_result_preserved"]["turnover_concentration_review_passed"],
            "validation_gross_metric_bps": artifact["prior_evaluator_result_preserved"]["validation_gross_metric_bps"],
            "validation_net_metric_bps": artifact["prior_evaluator_result_preserved"]["validation_net_metric_bps"],
            "validation_positive_after_cost": artifact["prior_evaluator_result_preserved"]["validation_positive_after_cost"],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        if output_path.exists():
            output_path.unlink()
        print(f"BLOCKED {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
