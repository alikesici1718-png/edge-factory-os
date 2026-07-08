#!/usr/bin/env python
"""Close the basis/premium z-score mean-reversion diagnostic route."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MODULE_RELATIVE_PATH = (
    "tools/"
    "edge_factory_os_repo_only_binance_okx_overlap_basis_premium_zscore_mean_reversion_"
    "closure_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/strategy_closures/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_closure_v1.json"
)
EVALUATOR_RELATIVE_PATH = (
    "artifacts/strategy_evaluations/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_evaluator_v1.json"
)
EXECUTION_RELATIVE_PATH = (
    "artifacts/strategy_executions/"
    "binance_okx_overlap_basis_premium_zscore_mean_reversion_execution_v1.json"
)

ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH
EVALUATOR_PATH = REPO_ROOT / EVALUATOR_RELATIVE_PATH
EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_CLOSURE_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_CLOSURE_RECORD"
EVALUATOR_STATUS = "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_EVALUATED"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_EXECUTED"
ROUTE_FAMILY = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_BASELINE"
CONFIG_ID = "mark_index_basis_z30d_reversal_hold8h"


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

    evaluator = load_json(EVALUATOR_PATH)
    execution = load_json(EXECUTION_PATH)

    evaluator_result = evaluator.get("result_classification")
    diagnostic_promising = evaluator.get("evaluator_findings", {}).get("diagnostic_promising")
    execution_config = execution.get("config_result", {})
    evaluator_followup = evaluator.get("followup_permissions", {})
    evaluator_forbidden = evaluator.get("forbidden_actions_confirmed_false", {})
    execution_forbidden = execution.get("forbidden_actions_confirmed_false", {})

    closure_record = {
        "route_closed": True,
        "closure_reason": "single preregistered diagnostic cycle completed and evaluated",
        "result_classification": evaluator_result,
        "diagnostic_promising": diagnostic_promising,
        "config_id": CONFIG_ID,
        "holdout_used_for_config_selection": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "holdout_permission_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
    }
    route_family_state_after_closure = {
        "route_family": ROUTE_FAMILY,
        "route_closed": True,
        "retest_allowed_now": False,
        "parameter_expansion_allowed_now": False,
        "strategy_search_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
    }
    project_state_after_closure = {
        "next_immediate_module_required": False,
        "project_can_pause_after_closure": True,
        "no_followup_required_from_rejected_diagnostic": evaluator_result
        == "BASIS_PREMIUM_ZSCORE_MEAN_REVERSION_REJECTED_NO_FOLLOWUP",
    }
    followup_permissions_after_closure = {
        "retest_allowed_now": False,
        "parameter_expansion_allowed_now": False,
        "strategy_search_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "holdout_permission_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "next_immediate_module_required": False,
    }
    forbidden_actions_confirmed_false = {
        "evaluator_rerun": False,
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
        "evaluator_artifact_loaded": True,
        "execution_artifact_loaded": True,
        "evaluator_status_verified": evaluator.get("status") == EVALUATOR_STATUS,
        "execution_status_verified": execution.get("status") == EXECUTION_STATUS,
        "evaluator_replacement_checks_true": evaluator.get("replacement_checks_all_true") is True,
        "execution_replacement_checks_true": execution.get("replacement_checks_all_true") is True,
        "evaluator_result_preserved": closure_record["result_classification"] == evaluator_result,
        "diagnostic_promising_preserved": closure_record["diagnostic_promising"] == diagnostic_promising,
        "config_id_preserved": execution.get("config_id") == CONFIG_ID,
        "route_closed": True,
        "retest_allowed_now_false": route_family_state_after_closure["retest_allowed_now"] is False,
        "parameter_expansion_allowed_now_false": route_family_state_after_closure[
            "parameter_expansion_allowed_now"
        ]
        is False,
        "strategy_search_allowed_now_false": route_family_state_after_closure[
            "strategy_search_allowed_now"
        ]
        is False,
        "candidate_generation_allowed_now_false": followup_permissions_after_closure[
            "candidate_generation_allowed_now"
        ]
        is False,
        "edge_claim_allowed_now_false": followup_permissions_after_closure["edge_claim_allowed_now"]
        is False,
        "family_release_allowed_now_false": followup_permissions_after_closure[
            "family_release_allowed_now"
        ]
        is False,
        "runtime_live_capital_allowed_now_false": route_family_state_after_closure[
            "runtime_live_capital_allowed_now"
        ]
        is False,
        "next_immediate_module_required_false": project_state_after_closure[
            "next_immediate_module_required"
        ]
        is False,
        "project_can_pause_after_closure_true": project_state_after_closure[
            "project_can_pause_after_closure"
        ]
        is True,
        "no_evaluator_rerun": True,
        "no_execution_rerun": True,
        "no_external_rows_read": True,
        "no_network_used": True,
        "evaluator_forbidden_actions_false": all_false(evaluator_forbidden),
        "execution_forbidden_actions_false": all_false(execution_forbidden),
        "replacement_checks_all_true": False,
    }
    validation_checks["replacement_checks_all_true"] = all(
        value is True
        for key, value in validation_checks.items()
        if key != "replacement_checks_all_true" and isinstance(value, bool)
    )

    if not validation_checks["replacement_checks_all_true"]:
        print("BLOCKED: closure validation checks failed")
        for key in sorted(validation_checks):
            if validation_checks[key] is not True:
                print(f"{key}: {validation_checks[key]}")
        print("replacement_checks_all_true: false")
        return 1

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "prior_evaluator_result_preserved": {
            "path": EVALUATOR_RELATIVE_PATH,
            "status": evaluator.get("status"),
            "payload_sha256_excluding_hash": evaluator.get("payload_sha256_excluding_hash"),
            "result_classification": evaluator_result,
            "diagnostic_promising": diagnostic_promising,
            "evaluator_findings": evaluator.get("evaluator_findings"),
        },
        "prior_execution_result_preserved": {
            "path": EXECUTION_RELATIVE_PATH,
            "status": execution.get("status"),
            "payload_sha256_excluding_hash": execution.get("payload_sha256_excluding_hash"),
            "config_id": execution.get("config_id"),
            "train_gross_bps": execution_config.get("train", {}).get("gross_mean_bps"),
            "train_net_bps": execution_config.get("train", {}).get("net_mean_bps"),
            "validation_gross_bps": execution_config.get("validation", {}).get("gross_mean_bps"),
            "validation_net_bps": execution_config.get("validation", {}).get("net_mean_bps"),
            "holdout_gross_bps": execution_config.get("holdout", {}).get("gross_mean_bps"),
            "holdout_net_bps": execution_config.get("holdout", {}).get("net_mean_bps"),
            "holdout_used_for_config_selection": execution_config.get("holdout_used_for_config_selection"),
        },
        "closure_record": closure_record,
        "route_family_state_after_closure": route_family_state_after_closure,
        "project_state_after_closure": project_state_after_closure,
        "followup_permissions_after_closure": followup_permissions_after_closure,
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
    print(f"result_classification: {evaluator_result}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print(f"config_id: {CONFIG_ID}")
    print("route_closed: true")
    print("retest_allowed_now: false")
    print("parameter_expansion_allowed_now: false")
    print("strategy_search_allowed_now: false")
    print("candidate_generation_allowed_now: false")
    print("edge_claim_allowed_now: false")
    print("family_release_allowed_now: false")
    print("holdout_permission_allowed_now: false")
    print("runtime_live_capital_allowed_now: false")
    print("next_immediate_module_required: false")
    print("project_can_pause_after_closure: true")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("replacement_checks_all_true: true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
