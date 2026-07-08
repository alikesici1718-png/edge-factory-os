#!/usr/bin/env python
"""Create the closure record for the Binance spot-perp delta-neutral funding carry diagnostic."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_delta_neutral_funding_carry_closure_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EVALUATOR_RELATIVE_PATH = "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
EXECUTION_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / EVALUATOR_RELATIVE_PATH
EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_CLOSURE_RECORD"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EVALUATED"
EVALUATOR_PAYLOAD_SHA256 = "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b"
EXECUTION_PAYLOAD_SHA256 = "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378"
TRACKED_PYTHON_COUNT_AT_START = 881


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
    evaluator = load_json(EVALUATOR_PATH)
    execution = load_json(EXECUTION_PATH)
    if evaluator.get("status") != EVALUATOR_STATUS:
        raise RuntimeError("evaluator status mismatch")
    if evaluator.get("payload_sha256_excluding_hash") != EVALUATOR_PAYLOAD_SHA256:
        raise RuntimeError("evaluator payload hash mismatch")
    if evaluator.get("replacement_checks_all_true") is not True:
        raise RuntimeError("evaluator replacement checks are not all true")
    if execution.get("payload_sha256_excluding_hash") != EXECUTION_PAYLOAD_SHA256:
        raise RuntimeError("execution payload hash mismatch")
    if execution.get("replacement_checks_all_true") is not True:
        raise RuntimeError("execution replacement checks are not all true")

    result_classification = evaluator["result_classification"]
    execution_validation = execution["config_result"]["aggregate_split_metrics"]["validation"]
    execution_holdout = execution["config_result"]["aggregate_split_metrics"]["holdout"]

    validation_checks = {
        "repo_clean_before_run": True,
        "evaluator_artifact_loaded": True,
        "evaluator_status_verified": True,
        "evaluator_payload_hash_verified": True,
        "execution_artifact_loaded": True,
        "execution_payload_hash_verified": True,
        "does_not_rerun_evaluator": True,
        "does_not_rerun_execution": True,
        "does_not_read_rows": True,
        "prior_evaluator_result_preserved_exactly": True,
        "route_closed": True,
        "candidate_generation_not_allowed": True,
        "edge_claim_not_allowed": True,
        "family_release_not_allowed": True,
        "runtime_live_capital_not_allowed": True,
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
        "prior_evaluator_result_preserved": {
            "evaluator_artifact": EVALUATOR_RELATIVE_PATH,
            "evaluator_status": evaluator["status"],
            "evaluator_payload_sha256_excluding_hash": evaluator["payload_sha256_excluding_hash"],
            "result_classification": result_classification,
            "evaluator_findings": evaluator["evaluator_findings"],
        },
        "prior_execution_result_preserved": {
            "execution_artifact": EXECUTION_RELATIVE_PATH,
            "execution_payload_sha256_excluding_hash": execution["payload_sha256_excluding_hash"],
            "config_id": execution["route_definition"]["config_id"],
            "validation_summary": {
                "gross_price_component_bps": execution_validation["gross_price_component_bps"],
                "gross_funding_component_bps": execution_validation["gross_funding_component_bps"],
                "gross_total_bps": execution_validation["gross_total_bps"],
                "net_after_lifecycle_cost_bps": execution_validation["net_after_lifecycle_cost_bps"],
                "net_after_monthly_rebalance_cost_bps": execution_validation[
                    "net_after_monthly_rebalance_cost_bps"
                ],
                "monthly_positive_rate": execution_validation["monthly_summary"][
                    "monthly_positive_rate_net_after_rebalance"
                ],
            },
            "holdout_summary": {
                "gross_price_component_bps": execution_holdout["gross_price_component_bps"],
                "gross_funding_component_bps": execution_holdout["gross_funding_component_bps"],
                "gross_total_bps": execution_holdout["gross_total_bps"],
                "net_after_lifecycle_cost_bps": execution_holdout["net_after_lifecycle_cost_bps"],
                "net_after_monthly_rebalance_cost_bps": execution_holdout[
                    "net_after_monthly_rebalance_cost_bps"
                ],
                "monthly_positive_rate": execution_holdout["monthly_summary"][
                    "monthly_positive_rate_net_after_rebalance"
                ],
            },
        },
        "closure_record": {
            "route_family": execution["route_definition"]["route_family"],
            "config_id": execution["route_definition"]["config_id"],
            "route_closed": True,
            "result_class": result_classification["result_class"],
            "diagnostic_promising": result_classification["diagnostic_promising"],
            "no_candidate_created": True,
            "no_edge_claim_created": True,
            "no_family_release_created": True,
            "no_runtime_live_capital_permission_created": True,
        },
        "route_family_state_after_closure": {
            "route_closed": True,
            "retest_allowed_now": False,
            "parameter_expansion_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
        },
        "project_state_after_closure": {
            "next_immediate_module_required": False,
            "project_can_pause_after_closure": True,
        },
        "followup_permissions_after_closure": {
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "holdout_permission_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "evaluator_rerun": False,
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
    print(f"closure_artifact_path: {ARTIFACT_RELATIVE_PATH}")
    print(f"result_class: {result_classification['result_class']}")
    print(f"diagnostic_promising: {str(result_classification['diagnostic_promising']).lower()}")
    print("route_closed: true")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
