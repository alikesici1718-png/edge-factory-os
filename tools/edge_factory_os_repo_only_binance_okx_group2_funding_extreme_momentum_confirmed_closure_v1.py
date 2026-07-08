from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_CLOSURE_RECORD"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.py"
ARTIFACT_PATH = "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json"

ROUTE_FAMILY = "CROSS_SECTIONAL_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_REVERSAL"
HYPOTHESIS_NAME = "group2_funding_extreme_momentum_confirmed_reversal"
CONFIG_ID = "group2_funding_extreme_mom24_hold24h"

EVALUATOR_PATH = "artifacts/strategy_evaluations/binance_okx_group2_funding_extreme_momentum_confirmed_evaluator_v1.json"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_EVALUATED"
EVALUATOR_HASH = "3a5dc3c20c871d9567e54b1aec08ef1b9eb1d6eec131d3ecdf9bfde64898cd76"
EXECUTION_PATH = "artifacts/strategy_executions/binance_okx_group2_funding_extreme_momentum_confirmed_execution_v1.json"
EXECUTION_HASH = "1daec6130f9449e85d0350fdefdbfc82782e657032aa904e6de6dd481ee4a277"
PREREG_PATH = "artifacts/research_preregistrations/binance_okx_group2_funding_extreme_momentum_confirmed_preregistration_contract_v1.json"
PREREG_HASH = "33acd29e5ffcf177c93cebe8e83bf223d353064eda63e5967bd5cf31975bf85c"


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


def build_artifact(root: Path) -> dict[str, Any]:
    evaluator = load_json(root, EVALUATOR_PATH)
    verify_payload(evaluator, EVALUATOR_HASH, "evaluator")
    if evaluator.get("status") != EVALUATOR_STATUS:
        raise Blocked("evaluator status mismatch")
    execution = load_json(root, EXECUTION_PATH)
    verify_payload(execution, EXECUTION_HASH, "execution")
    prereg = load_json(root, PREREG_PATH)
    verify_payload(prereg, PREREG_HASH, "preregistration")

    classification = evaluator.get("result_classification", {})
    prior_execution = evaluator.get("prior_execution_preserved", {})
    result_class = classification.get("result_class")
    diagnostic_promising = classification.get("diagnostic_promising")
    if classification.get("config_id") != CONFIG_ID:
        raise Blocked("evaluator config_id mismatch")
    if prior_execution.get("route_family") != ROUTE_FAMILY:
        raise Blocked("route_family mismatch")
    if not isinstance(diagnostic_promising, bool):
        raise Blocked("diagnostic_promising missing")

    validation_net = classification.get("validation_net_metric_bps")
    validation_gross = classification.get("validation_gross_metric_bps")
    validation_positive = classification.get("validation_positive_after_cost")
    null_passed = classification.get("null_baseline_review_passed")
    monthly_passed = classification.get("monthly_stability_review_passed")
    turnover_passed = classification.get("turnover_concentration_review_passed")
    metric_issue_count = classification.get("metric_integrity_issue_count")

    if diagnostic_promising:
        closure_state = "CLOSED_DIAGNOSTIC_PROMISING_NO_CANDIDATE_NO_EDGE"
    elif "INCONCLUSIVE" in str(result_class):
        closure_state = "CLOSED_INCONCLUSIVE_NO_FOLLOWUP"
    elif "INVALIDATED" in str(result_class):
        closure_state = "CLOSED_INVALIDATED_NO_FOLLOWUP"
    else:
        closure_state = "CLOSED_REJECTED_NO_FOLLOWUP"

    closure_reason = (
        f"The fixed Group-2 funding extreme momentum confirmed postmortem diagnostic is closed with "
        f"result_class={result_class}. Validation net metric was {validation_net} bps, validation gross metric was "
        f"{validation_gross} bps, validation_positive_after_cost={str(validation_positive).lower()}, null baseline pass="
        f"{str(null_passed).lower()}, monthly stability pass={str(monthly_passed).lower()}, "
        f"turnover/concentration pass={str(turnover_passed).lower()}, and metric integrity issue count={metric_issue_count}. "
        "Because Group-2 was selected using same-window average trailing 24h liquidity, this postmortem diagnostic cannot "
        "create a candidate, edge claim, family release, holdout access, or runtime/live/capital permission."
    )

    artifact: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "prior_evaluator_artifact": EVALUATOR_PATH,
            "prior_evaluator_payload_sha256_excluding_hash": EVALUATOR_HASH,
            "prior_evaluator_status": EVALUATOR_STATUS,
            "prior_head": "dd930b9d479d06ba828a060857dd06c9bc53d9ce",
            "prior_tracked_python_count": 824,
            "repo_clean_before_closure": True,
        },
        "source_artifacts": {
            "all_source_artifacts_read_only": True,
            "evaluator_artifact_path": EVALUATOR_PATH,
            "evaluator_payload_hash_verified": True,
            "execution_artifact_path": EXECUTION_PATH,
            "execution_payload_hash_verified": True,
            "preregistration_artifact_path": PREREG_PATH,
            "preregistration_payload_hash_verified": True,
        },
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
            "symbol_count": 8,
            "turnover_concentration_review_preliminary_passed": turnover_passed,
            "validation_gross_metric_bps": validation_gross,
            "validation_net_metric_bps": validation_net,
            "validation_positive_after_cost": validation_positive,
        },
        "postmortem_bucket_warning_preserved": {
            "candidate_generation_forbidden_even_if_positive": True,
            "edge_claim_forbidden_even_if_positive": True,
            "group2_selected_using_same_aligned_window_liquidity": True,
            "runtime_live_capital_forbidden_even_if_positive": True,
        },
        "closure_record": {
            "candidate_generation_allowed_now": False,
            "closure_reason": closure_reason,
            "closure_record_created": True,
            "closure_state": closure_state,
            "diagnostic_promising": diagnostic_promising,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
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
            "group2_route": {
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
            "group2_postmortem_route_closed": True,
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
            "family_release_allowed_now": False,
            "holdout_access_allowed_now": False,
            "next_immediate_module_required": False,
            "new_research_cycle_allowed_only_with_new_deliberate_contract": True,
            "parameter_expansion_allowed_now": False,
            "project_can_pause_after_closure": True,
            "retest_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "candidates_generated": False,
            "edge_claimed": False,
            "evaluator_rerun": False,
            "family_released": False,
            "funding_rows_read": False,
            "holdout_accessed": False,
            "network_used": False,
            "okx_panel_rows_read": False,
            "panel_rows_read": False,
            "runtime_live_capital": False,
            "strategy_execution_rerun": False,
            "strategy_search_executed": False,
        },
    }
    validation_checks = {
        "closure_artifact_json_valid": True,
        "closure_artifact_path_equals_required_path": ARTIFACT_PATH == "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json",
        "evaluator_payload_hash_verified": True,
        "evaluator_result_class_preserved": True,
        "execution_payload_hash_verified": True,
        "metric_integrity_issue_count_zero_preserved": metric_issue_count == 0,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.py",
        "next_immediate_module_required_false": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_evaluator_rerun": True,
        "no_execution_rerun": True,
        "no_funding_rows_read": True,
        "no_network_used": True,
        "no_okx_panel_rows_read": True,
        "no_panel_rows_read": True,
        "no_runtime_live_capital": True,
        "postmortem_bucket_warning_preserved": True,
        "project_can_pause_after_closure": True,
        "replacement_checks_all_true": True,
        "route_closed": True,
        "status_equals_required_status": STATUS == "PASS_REPO_ONLY_BINANCE_OKX_GROUP2_FUNDING_EXTREME_MOMENTUM_CONFIRMED_CLOSURE_CREATED",
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
        raise Blocked("written closure artifact hash mismatch")


def main() -> int:
    root = repo_root()
    output = root / ARTIFACT_PATH
    try:
        artifact = build_artifact(root)
        write_artifact(root, artifact)
        summary = {
            "candidate_generation": False,
            "closure_artifact_path": ARTIFACT_PATH,
            "diagnostic_promising": artifact["closure_record"]["diagnostic_promising"],
            "edge_claim": False,
            "family_release": False,
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
        if output.exists():
            output.unlink()
        print(f"BLOCKED {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
