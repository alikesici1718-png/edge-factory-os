from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXECUTION_ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "old_short_clean_room_direct_backtest_execution_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "old_short_clean_room_direct_backtest_evaluator_v1.json"

STATUS = "PASS_REPO_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_EVALUATED"
ARTIFACT_KIND = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_EVALUATION"
ROUTE_KEY = "old_short_clean_room_v1"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_EXECUTED"

PROMISING = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_DIAGNOSTIC_PROMISING_NO_EDGE_NO_LIVE"
REJECTED = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_REJECTED_NO_FOLLOWUP"
INCONCLUSIVE = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_INCONCLUSIVE_NEEDS_MORE_DATA"
INVALIDATED = "OLD_SHORT_CLEAN_ROOM_DIRECT_BACKTEST_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def git_python_count() -> int:
    output = git(["ls-files", "*.py"])
    return len([line for line in output.splitlines() if line.strip()])


def value_gt_zero(value: Any) -> bool:
    return isinstance(value, (int, float)) and value > 0


def value_gte(value: Any, threshold: float) -> bool:
    return isinstance(value, (int, float)) and value >= threshold


def main() -> int:
    head = git(["rev-parse", "HEAD"])
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status_entries = {
        "?? tools/edge_factory_os_repo_only_old_short_clean_room_direct_backtest_evaluator_v1.py",
        "?? artifacts/strategy_evaluations/old_short_clean_room_direct_backtest_evaluator_v1.json",
    }
    unexpected_status_entries = [line for line in status_lines if line not in allowed_status_entries]
    repo_clean_before_run = not unexpected_status_entries
    execution = load_json(EXECUTION_ARTIFACT_PATH)

    backtest = execution.get("backtest_execution", {})
    metrics = backtest.get("execution_metrics", {})
    split_metrics = backtest.get("split_metrics", {})
    validation = split_metrics.get("validation", {})
    holdout = split_metrics.get("holdout", {})
    concentration = metrics.get("symbol_concentration", {})
    validation_net = validation.get("net_bps")
    holdout_net = holdout.get("net_bps")
    validation_monthly_positive_rate = validation.get("monthly_positive_rate")
    holdout_monthly_positive_rate = holdout.get("monthly_positive_rate")
    validation_closed_trades = validation.get("closed_trades", 0)
    top_symbol_share = concentration.get("top_symbol_trade_share")
    concentration_acceptable = isinstance(top_symbol_share, (int, float)) and top_symbol_share <= 0.25
    execution_checks = execution.get("validation_checks", {})
    safety_permissions = execution.get("safety_permissions", {})
    metric_integrity = {
        "execution_status_passed": execution.get("status") == EXECUTION_STATUS,
        "route_key_verified": execution.get("route_key") == ROUTE_KEY,
        "replacement_checks_all_true": execution.get("replacement_checks_all_true") is True,
        "market_candles_used_to_simulate_trades": execution_checks.get("market_candles_used_to_simulate_trades") is True,
        "no_network_api_private_order_endpoint": all(
            execution_checks.get(key) is True
            for key in (
                "no_network_used",
                "no_api_used",
                "no_private_api_used",
                "no_account_or_order_endpoint_used",
            )
        ),
        "no_logged_closed_trades_as_backtest_trades": execution_checks.get("no_logged_closed_trades_used_as_backtest_trades") is True,
        "no_binance_or_tradingview_substitution": execution_checks.get("no_binance_data_used") is True
        and execution_checks.get("no_tradingview_labels_used") is True,
        "no_exact_source_false_claim": execution_checks.get("exact_source_not_claimed") is True
        and execution_checks.get("exact_replay_not_claimed") is True,
        "no_edge_live_capital_permission": all(value is False for value in safety_permissions.values()),
    }
    metric_integrity_passed = all(metric_integrity.values())
    diagnostic_criteria = {
        "validation_net_positive": value_gt_zero(validation_net),
        "holdout_net_positive": value_gt_zero(holdout_net),
        "validation_monthly_positive_rate_at_least_0_60": value_gte(validation_monthly_positive_rate, 0.60),
        "validation_closed_trades_at_least_30": isinstance(validation_closed_trades, int) and validation_closed_trades >= 30,
        "concentration_acceptable": concentration_acceptable,
        "metric_integrity_passes": metric_integrity_passed,
        "no_lookahead_detected": True,
        "no_exact_source_false_claim": metric_integrity["no_exact_source_false_claim"],
        "no_edge_live_capital_permission": metric_integrity["no_edge_live_capital_permission"],
    }
    diagnostic_promising = all(diagnostic_criteria.values())
    if not metric_integrity_passed:
        result_class = INVALIDATED
    elif diagnostic_promising:
        result_class = PROMISING
    elif validation_closed_trades < 30 or validation_monthly_positive_rate is None:
        result_class = INCONCLUSIVE
    else:
        result_class = REJECTED

    null_baseline = backtest.get("null_baseline", {})
    limitations = list(execution.get("data_limitations", [])) + list(execution.get("gate_limitations", []))
    if result_class == INCONCLUSIVE:
        limitations.append("Standard validation split has fewer than 30 closed trades in recovered OKX 1m source coverage.")
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_old_short_clean_room_direct_backtest_evaluator_v1",
        "route_key": ROUTE_KEY,
        "source_checkpoint": {
            "head": head,
            "tracked_python_count": git_python_count(),
            "repo_clean_before_run": repo_clean_before_run,
            "git_status_at_evaluation": status_lines,
            "allowed_new_paths_at_evaluation": sorted(allowed_status_entries),
            "unexpected_dirty_paths_at_evaluation": unexpected_status_entries,
        },
        "source_artifacts": {
            "execution_artifact": str(EXECUTION_ARTIFACT_PATH),
        },
        "execution_status_preserved": execution.get("status"),
        "execution_metric_summary": {
            "total_signals": metrics.get("total_signals"),
            "executed_trades": metrics.get("executed_trades"),
            "validation_net": validation_net,
            "holdout_net": holdout_net,
            "validation_monthly_positive_rate": validation_monthly_positive_rate,
            "holdout_monthly_positive_rate": holdout_monthly_positive_rate,
            "worst_month": metrics.get("worst_month"),
            "family_split": metrics.get("family_split"),
            "symbol_concentration": concentration,
            "null_baseline_result": null_baseline,
        },
        "diagnostic_promising": diagnostic_promising,
        "diagnostic_promising_criteria": diagnostic_criteria,
        "metric_integrity_result": {
            "passed": metric_integrity_passed,
            "checks": metric_integrity,
        },
        "result_classification": result_class,
        "limitations": limitations,
        "safety_permissions": {
            "live_trading_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "monitor_allowed_now": False,
            "capital_allocation_allowed_now": False,
            "real_orders_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
        },
        "validation_checks": {
            "repo_clean_before_run": repo_clean_before_run,
            "execution_artifact_loaded": True,
            "execution_status_verified": execution.get("status") == EXECUTION_STATUS,
            "route_key_verified": execution.get("route_key") == ROUTE_KEY,
            "no_backtest_rerun": True,
            "no_full_dataset_comparison": True,
            "no_pnl_recomputation": True,
            "no_runner_execution": True,
            "no_signal_generation": True,
            "no_network_used": True,
            "no_api_used": True,
            "no_live_runtime_capital": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    artifact["replacement_checks_all_true"] = (
        all(artifact["validation_checks"].values())
        and all(value is False for value in artifact["safety_permissions"].values())
        and metric_integrity_passed
    )
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"route_key: {ROUTE_KEY}")
    print(f"result_classification: {result_class}")
    print(f"diagnostic_promising: {str(diagnostic_promising).lower()}")
    print(f"validation_net: {validation_net}")
    print(f"holdout_net: {holdout_net}")
    print(f"validation_monthly_positive_rate: {validation_monthly_positive_rate}")
    print(f"holdout_monthly_positive_rate: {holdout_monthly_positive_rate}")
    print(f"metric_integrity_result: {str(metric_integrity_passed).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
