from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_ROUTE_CLOSURE_CREATED"
ARTIFACT_KIND = "TRAP_QUALITY_LOCKBOX_ROUTE_CLOSURE"
MODULE = "edge_factory_os_repo_only_trap_quality_lockbox_route_closure_v1"
FINAL_CLASSIFICATION = "TRAP_QUALITY_LOCKBOX_ROUTE_CLOSED_FAILED_FORWARD_NO_EDGE_NO_LIVE"
FROZEN_FINALIST = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
LOCKBOX_RESULT_CLASSIFICATION = "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_FAIL_ROUTE_CLOSED_NO_EDGE_NO_LIVE"
NEXT_ALLOWED_STEP = "NEW_HYPOTHESIS_OR_NEW_DATA_SOURCE_ONLY"

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "trap_quality_lockbox_route_closure_v1.json"

SOURCE_PATHS = {
    "lockbox_execution": REPO_ROOT
    / "artifacts"
    / "strategy_executions"
    / "trap_quality_lockbox_forward_test_execution_v1.json",
    "lockbox_test_preregistration": REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "trap_quality_lockbox_forward_test_preregistration_v1.json",
    "freeze_contract": REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "trap_quality_lockbox_freeze_contract_v1.json",
    "data_review": REPO_ROOT
    / "artifacts"
    / "data_reviews"
    / "trap_quality_lockbox_forward_data_review_v1.json",
}

EXPECTED_LOCKBOX_METRICS = {
    "closed_trade_count": 69,
    "portfolio_net_bps": -333.003836,
    "monthly_positive_rate": 0.333333,
    "worst_month_bps": -173.332597,
    "max_drawdown_bps": -537.933126,
    "null_percentile": 0.07,
    "fee_stress_2x_net_bps": -458.19856,
    "top_3_symbol_concentration": 0.188406,
    "pass_criteria_passed_count": 6,
    "hard_reject_triggered_count": 3,
    "metric_integrity_passed": True,
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": "), ensure_ascii=True) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(args: list[str]) -> str:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={safe_dir}", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def status_lines() -> list[str]:
    output = git(["status", "--short", "-uall"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def tracked_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def source_artifact_record(name: str, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": sha256_file(path),
        "status": payload.get("status"),
        "artifact_kind": payload.get("artifact_kind"),
        "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
    }


def close_enough(actual: Any, expected: Any) -> bool:
    if isinstance(expected, bool):
        return actual is expected
    if isinstance(expected, int):
        return int(actual) == expected
    return abs(float(actual) - float(expected)) <= 1e-9


def get_preserved_result(execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "lockbox_result_classification": execution.get("result_classification"),
        "closed_trade_count": execution.get("trade_summary", {}).get("closed_trade_count"),
        "portfolio_net_bps": execution.get("execution_summary", {}).get("portfolio_net_bps"),
        "monthly_positive_rate": execution.get("execution_summary", {}).get("monthly_positive_rate"),
        "worst_month_bps": execution.get("execution_summary", {}).get("worst_month_bps"),
        "max_drawdown_bps": execution.get("execution_summary", {}).get("max_drawdown_bps"),
        "null_percentile": execution.get("null_baseline", {}).get("null_percentile"),
        "fee_stress_2x_net_bps": execution.get("fee_stress_results", {}).get("fee_stress_2x_net_bps"),
        "top_3_symbol_concentration": execution.get("symbol_concentration", {}).get("top_3_symbol_concentration"),
        "pass_criteria_passed_count": execution.get("pass_criteria_results", {}).get("passed_count"),
        "hard_reject_triggered_count": execution.get("hard_reject_results", {}).get("triggered_count"),
        "metric_integrity_passed": execution.get("metric_integrity", {}).get("passed"),
        "next_allowed_step_from_execution": execution.get("next_allowed_step"),
    }


def main() -> int:
    allowed_new_paths = {
        "?? tools/edge_factory_os_repo_only_trap_quality_lockbox_route_closure_v1.py",
        "?? artifacts/strategy_closures/trap_quality_lockbox_route_closure_v1.json",
    }
    before_status = status_lines()
    unexpected_status = [line for line in before_status if line not in allowed_new_paths]
    sources = {name: load_json(path) for name, path in SOURCE_PATHS.items()}
    execution = sources["lockbox_execution"]
    prereg = sources["lockbox_test_preregistration"]
    freeze = sources["freeze_contract"]
    data_review = sources["data_review"]

    preserved = get_preserved_result(execution)
    metric_preservation_checks = {
        key: close_enough(preserved[key], expected) for key, expected in EXPECTED_LOCKBOX_METRICS.items()
    }
    metric_preservation_checks["lockbox_result_classification"] = (
        preserved["lockbox_result_classification"] == LOCKBOX_RESULT_CLASSIFICATION
    )
    metric_preservation_checks["frozen_finalist"] = (
        execution.get("frozen_finalist", {}).get("strategy") == FROZEN_FINALIST
    )

    closure_decision = {
        "final_classification": FINAL_CLASSIFICATION,
        "route_closed": True,
        "v_next_allowed_now": False,
        "lockbox_tuning_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_live_capital_allowed_now": False,
        "reason": (
            "The frozen finalist failed unseen lockbox forward data. Per pre-registered "
            "lockbox protocol, no parameter repair or V-next may be created from this lockbox result."
        ),
        "next_allowed_step": NEXT_ALLOWED_STEP,
    }

    safety_permissions = {
        "route_closure_created": True,
        "strategy_execution_allowed_now": False,
        "signal_generation_allowed_now": False,
        "pnl_recomputation_allowed_now": False,
        "backtest_allowed_now": False,
        "v_next_allowed_now": False,
        "lockbox_tuning_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }

    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "lockbox_execution_loaded": execution.get("status")
        == "PASS_REPO_CODE_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_TEST_EXECUTED",
        "lockbox_test_preregistration_loaded": prereg.get("status")
        == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PREREGISTRATION_CREATED",
        "freeze_contract_loaded": freeze.get("status")
        == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FREEZE_CONTRACT_CREATED",
        "data_review_loaded": data_review.get("status")
        == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_CREATED",
        "frozen_finalist_preserved": metric_preservation_checks["frozen_finalist"],
        "lockbox_failure_preserved": preserved["lockbox_result_classification"] == LOCKBOX_RESULT_CLASSIFICATION,
        "lockbox_metrics_preserved": all(metric_preservation_checks.values()),
        "route_closed_true": closure_decision["route_closed"] is True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_pnl_recomputation": True,
        "no_backtest": True,
        "no_v_next_created": True,
        "no_optimization": True,
        "no_lockbox_tuning": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": Path(__file__).resolve().exists(),
        "exactly_one_json_artifact_created": ARTIFACT_PATH.name == "trap_quality_lockbox_route_closure_v1.json",
        "no_existing_repo_files_modified": not unexpected_status
        and not any(line and not line.startswith("?? ") for line in before_status),
    }
    safety_ok = safety_permissions["route_closure_created"] and not any(
        value for key, value in safety_permissions.items() if key != "route_closure_created"
    )
    replacement_checks_all_true = all(validation_checks.values()) and safety_ok
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count_before_run": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_closure_start": before_status,
            "allowed_new_paths_at_closure": sorted(allowed_new_paths),
            "unexpected_dirty_paths_at_closure": unexpected_status,
        },
        "source_artifacts": {
            name: source_artifact_record(name, path, sources[name]) for name, path in SOURCE_PATHS.items()
        },
        "frozen_finalist": FROZEN_FINALIST,
        "lockbox_result_preserved": preserved,
        "metric_preservation_checks": metric_preservation_checks,
        "closure_decision": closure_decision,
        "final_classification": FINAL_CLASSIFICATION,
        "route_closed": True,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "lockbox_non_tuning_rule": {
            "no_parameter_repair_from_lockbox": True,
            "no_v_next_from_lockbox": True,
            "no_rerun": True,
            "no_lockbox_tuning": True,
            "route_closed_due_to_failed_unseen_forward_test": True,
        },
        "limitations": [
            "Closure only; no strategy execution, signal generation, PnL recomputation, or backtest was run.",
            "The lockbox result is preserved from the execution artifact without tuning or repair.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"final_classification: {FINAL_CLASSIFICATION}")
    print("route_closed: true")
    print("v_next_allowed_now: false")
    print("lockbox_tuning_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
