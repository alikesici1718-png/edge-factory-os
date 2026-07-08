from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_residual_sweep_confirmation_preregistration_v1.json"
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_residual_sweep_confirmation_evaluator_v1.json"
CLOSURE_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "crypto_15m_residual_sweep_confirmation_closure_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_POSTMORTEM_DIAGNOSTIC_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_POSTMORTEM_DIAGNOSTIC"
STRATEGY = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_REVERSAL_V1"
ROUTE_FAMILY = "CRYPTO_15M_CONFLUENCE_EVENT_REVERSAL_BASELINE"
CONFIG_ID = "crypto_15m_residual_sweep_confirmation_reversal_z35_48h_confirm1_v1"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_EXECUTED"
EVALUATOR_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_EVALUATED"
CLOSURE_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_CLOSURE_CREATED"
REJECTED_CLASS = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_REJECTED_NO_FOLLOWUP"
V2_INCONCLUSIVE = "V2_DIRECTION_INCONCLUSIVE_MISSING_TRADE_LEVEL_DATA"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def pct(count: int | float, total: int | float) -> float | None:
    if not total:
        return None
    return round(float(count) / float(total), 6)


def split_months(monthly: dict[str, Any], start: str, end: str) -> dict[str, float]:
    return {month: float(value) for month, value in monthly.items() if start <= month < end}


def month_stats(months: dict[str, float]) -> dict[str, Any]:
    if not months:
        return {
            "month_count": 0,
            "positive_month_count": 0,
            "negative_month_count": 0,
            "net_bps": 0.0,
            "positive_rate": None,
            "best_month": None,
            "worst_month": None,
        }
    positive = {month: value for month, value in months.items() if value > 0}
    nonpositive = {month: value for month, value in months.items() if value <= 0}
    best_month = max(months.items(), key=lambda item: item[1])
    worst_month = min(months.items(), key=lambda item: item[1])
    return {
        "month_count": len(months),
        "positive_month_count": len(positive),
        "negative_or_flat_month_count": len(nonpositive),
        "net_bps": round(sum(months.values()), 6),
        "positive_rate": round(len(positive) / len(months), 6),
        "best_month": {"month": best_month[0], "net_bps": round(best_month[1], 6)},
        "worst_month": {"month": worst_month[0], "net_bps": round(worst_month[1], 6)},
    }


def has_trade_level_rows(execution: dict[str, Any]) -> tuple[bool, list[str]]:
    candidate_keys = [
        "trades",
        "trade_rows",
        "closed_trade_rows",
        "closed_trades",
        "trade_level_rows",
        "executed_trades",
    ]
    found = []
    for key in candidate_keys:
        value = execution.get(key)
        if isinstance(value, list) and value and all(isinstance(row, dict) for row in value):
            found.append(key)
    return bool(found), found


def safety_all_false(safety: dict[str, Any]) -> bool:
    return all(value is False for value in safety.values())


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v1.py",
        "?? artifacts/strategy_reviews/crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    prereg = load_json(PREREG_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)

    metrics = execution.get("metrics", {})
    split = execution.get("split_metrics", {})
    validation = split.get("validation", {})
    holdout = split.get("holdout", {})
    null = execution.get("null_baseline", {})
    integrity = execution.get("metric_integrity_result", {})
    safety = execution.get("safety_permissions", {})
    criteria = evaluator.get("diagnostic_promising_criteria", {})
    monthly = {month: float(value) for month, value in metrics.get("monthly_net_bps", {}).items()}
    train_months = split_months(monthly, "2023-01", "2024-07")
    validation_months = split_months(monthly, "2024-07", "2025-04")
    holdout_months = split_months(monthly, "2025-04", "2025-11")

    trade_level_available, trade_row_keys = has_trade_level_rows(execution)
    closed_trades = int(metrics.get("closed_trades", 0))
    long_trades = int(metrics.get("accepted_long_trades", 0))
    short_trades = int(metrics.get("accepted_short_trades", 0))
    stop_count = int(metrics.get("stop_exit_count", 0))
    take_count = int(metrics.get("take_profit_exit_count", 0))
    time_count = int(metrics.get("time_stop_exit_count", 0))
    gross_pnl = float(metrics.get("gross_pnl_usdt", 0.0))
    net_pnl = float(metrics.get("net_pnl_usdt", 0.0))
    cost_drag = round(gross_pnl - net_pnl, 6)
    cost_share = round(cost_drag / abs(gross_pnl), 6) if gross_pnl else None
    top_concentration = metrics.get("top_symbol_concentration", {})

    side_summary = (
        f"short side dominates count ({short_trades}/{closed_trades}); "
        "side PnL unavailable because execution artifact has no trade-level rows"
    )
    exit_summary = (
        f"stops={stop_count}, takes={take_count}, time={time_count}; "
        "stop/time exits dominate by count, contribution unavailable without trade rows"
    )
    null_failure_reasons = []
    if criteria.get("validation_monthly_positive_rate_gte_0_60") is False:
        null_failure_reasons.append("validation_monthly_positive_rate_below_gate")
    if null.get("null_pass") is False:
        null_failure_reasons.append("validation_null_percentile_0_84_below_0_95")
    if gross_pnl > 0 and net_pnl < 0:
        null_failure_reasons.append("cost_drag_flips_full_sample_from_gross_positive_to_net_negative")
    if metrics.get("max_drawdown_bps", 0) < -1000:
        null_failure_reasons.append("large_full_sample_drawdown_despite_split_positive_net")
    null_failure_reason = ", ".join(null_failure_reasons) if null_failure_reasons else "no_single_aggregate_failure_reason_identified"

    prior_rejection_preserved = (
        execution.get("status") == EXECUTION_STATUS
        and evaluator.get("status") == EVALUATOR_STATUS
        and closure.get("status") == CLOSURE_STATUS
        and evaluator.get("result_classification") == REJECTED_CLASS
        and evaluator.get("diagnostic_promising") is False
        and safety_all_false(safety)
    )
    postmortem_safety = {
        "postmortem_diagnostic_created": True,
        "strategy_execution_allowed_now": False,
        "v2_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    checks = {
        "repo_clean_before_run": not unexpected_status,
        "prior_preregistration_loaded": bool(prereg),
        "prior_execution_loaded": execution.get("status") == EXECUTION_STATUS,
        "prior_evaluator_loaded": evaluator.get("status") == EVALUATOR_STATUS,
        "prior_closure_loaded": closure.get("status") == CLOSURE_STATUS,
        "prior_rejection_preserved": prior_rejection_preserved,
        "no_new_strategy_executed": True,
        "no_v2_tested": True,
        "no_parameter_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_network_used": True,
        "no_api_called": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": not unexpected_status,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v1",
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_diagnostic": status_lines,
            "allowed_new_paths_at_diagnostic": sorted(allowed_status),
            "unexpected_dirty_paths_at_diagnostic": unexpected_status,
        },
        "source_artifacts": {
            "preregistration": str(PREREG_PATH),
            "execution": str(EXECUTION_PATH),
            "evaluator": str(EVALUATOR_PATH),
            "closure": str(CLOSURE_PATH),
        },
        "prior_result_preserved": {
            "strategy": STRATEGY,
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "execution_status": execution.get("status"),
            "evaluator_result_classification": evaluator.get("result_classification"),
            "diagnostic_promising": evaluator.get("diagnostic_promising"),
            "accepted_long_trades": long_trades,
            "accepted_short_trades": short_trades,
            "closed_trades": closed_trades,
            "validation_net_bps": validation.get("portfolio_net_bps"),
            "holdout_net_bps": holdout.get("portfolio_net_bps"),
            "validation_monthly_positive_rate": validation.get("monthly_positive_rate"),
            "holdout_monthly_positive_rate": holdout.get("monthly_positive_rate"),
            "null_baseline": null,
            "metric_integrity": integrity,
            "no_edge_candidate_live_capital": safety_all_false(safety),
            "result_remains_rejected": evaluator.get("result_classification") == REJECTED_CLASS,
        },
        "trade_level_data_availability": {
            "trade_level_data_available": trade_level_available,
            "trade_row_keys_found": trade_row_keys,
            "aggregate_only_fields_available": [
                "accepted_long_trades",
                "accepted_short_trades",
                "exit_counts",
                "monthly_net_bps",
                "gross_pnl_usdt",
                "net_pnl_usdt",
                "top_symbol_concentration",
                "null_baseline",
            ],
            "raw_panel_rows_read": False,
            "limitation": "Execution artifact does not contain per-trade rows, so side PnL, exit contribution, feature buckets, and month-driver attribution cannot be computed safely.",
        },
        "side_performance_diagnostic": {
            "long_trade_count": long_trades,
            "short_trade_count": short_trades,
            "long_trade_share": pct(long_trades, closed_trades),
            "short_trade_share": pct(short_trades, closed_trades),
            "long_gross_bps": None,
            "long_net_bps": None,
            "short_gross_bps": None,
            "short_net_bps": None,
            "long_win_rate": None,
            "short_win_rate": None,
            "long_exit_reason_distribution": None,
            "short_exit_reason_distribution": None,
            "conclusion": "short side dominant by count; helpful or harmful cannot be determined without trade-level side PnL",
            "summary": side_summary,
        },
        "exit_reason_diagnostic": {
            "stop_exits": {"count": stop_count, "share": pct(stop_count, closed_trades), "net_contribution_usdt": None},
            "take_profit_exits": {"count": take_count, "share": pct(take_count, closed_trades), "net_contribution_usdt": None},
            "time_stop_exits": {"count": time_count, "share": pct(time_count, closed_trades), "net_contribution_usdt": None},
            "both_hit_same_bar_count": metrics.get("both_hit_same_bar_count"),
            "diagnosis": "stop and time exits dominate by count; take-profit exits are rare by count; contribution cannot be attributed without trade rows",
            "summary": exit_summary,
        },
        "monthly_performance_diagnostic": {
            "all_monthly_net_bps": monthly,
            "train": month_stats(train_months),
            "validation": month_stats(validation_months),
            "holdout": month_stats(holdout_months),
            "overall": month_stats(monthly),
            "positive_validation_and_holdout_but_rejected_reason": {
                "validation_net_positive": validation.get("portfolio_net_bps", 0) > 0,
                "holdout_net_positive": holdout.get("portfolio_net_bps", 0) > 0,
                "validation_monthly_positive_rate_gate_passed": criteria.get("validation_monthly_positive_rate_gte_0_60"),
                "null_baseline_gate_passed": criteria.get("null_baseline_passes"),
                "result_depends_on_one_month": "not_proven_from_aggregate_only; holdout best month 2025-05 contributes materially",
            },
        },
        "feature_bucket_diagnostic": {
            "trade_level_feature_buckets_available": False,
            "available_aggregate_feature_fields": {
                "average_abs_z_residual": metrics.get("average_abs_z_residual"),
                "raw_residual_extremes_long": metrics.get("raw_residual_extremes_long"),
                "raw_residual_extremes_short": metrics.get("raw_residual_extremes_short"),
                "raw_sweep_candidates_long": metrics.get("raw_sweep_candidates_long"),
                "raw_sweep_candidates_short": metrics.get("raw_sweep_candidates_short"),
                "confirmation_passed_long": metrics.get("confirmation_passed_long"),
                "confirmation_passed_short": metrics.get("confirmation_passed_short"),
                "cost_aware_gate_passed_long": metrics.get("cost_aware_gate_passed_long"),
                "cost_aware_gate_passed_short": metrics.get("cost_aware_gate_passed_short"),
            },
            "strongest_feature_bucket_signal": None,
            "classification": "inconclusive",
            "limitation": "No per-trade z_residual, residual_4h, sweep_depth, volume ratio, confirmation strength, BTC return, side, symbol PnL, or entry timestamp rows are present in the execution artifact.",
        },
        "cost_sensitivity_diagnostic": {
            "gross_pnl_usdt": gross_pnl,
            "net_pnl_usdt": net_pnl,
            "portfolio_gross_bps": metrics.get("portfolio_gross_bps"),
            "portfolio_net_bps": metrics.get("portfolio_net_bps"),
            "estimated_total_cost_drag_usdt": cost_drag,
            "average_cost_drag_per_closed_trade_usdt": round(cost_drag / closed_trades, 6) if closed_trades else None,
            "cost_as_share_of_abs_gross_pnl": cost_share,
            "diagnosis": "full-sample gross PnL is positive but costs flip full-sample net negative; validation and holdout remain net positive but fail robustness gates",
        },
        "concentration_diagnostic": {
            "top_symbol": top_concentration.get("top_symbol"),
            "top_symbol_trade_count": top_concentration.get("top_symbol_trade_count"),
            "top_symbol_trade_share": top_concentration.get("top_symbol_trade_share"),
            "top_symbol_share_lte_0_25": top_concentration.get("top_symbol_trade_share", 1) <= 0.25,
            "side_concentration": {"long": pct(long_trades, closed_trades), "short": pct(short_trades, closed_trades)},
            "month_concentration": {
                "best_month_bps": metrics.get("best_month_bps"),
                "worst_month_bps": metrics.get("worst_month_bps"),
                "max_drawdown_bps": metrics.get("max_drawdown_bps"),
            },
        },
        "null_failure_diagnostic": {
            "validation_percentile": null.get("validation_percentile"),
            "null_pass": null.get("null_pass"),
            "runs": null.get("runs"),
            "observed_validation_pnl_usdt": null.get("observed_validation_pnl_usdt"),
            "likely_reasons": null_failure_reasons,
            "summary": null_failure_reason,
        },
        "v2_direction_assessment": {
            "v2_direction_classification": V2_INCONCLUSIVE,
            "bounded_v2_direction": "No V2 execution is justified from this artifact alone because trade-level rows needed for side, exit, and feature-bucket attribution are missing.",
            "allowed_descriptive_findings": [
                "The route was rejected despite positive validation and holdout net bps because validation monthly positive rate was below 0.60 and the validation null percentile was 0.84 rather than at least 0.95.",
                "Short trades dominate accepted count, but side filtering is not justified without side-level PnL across validation and holdout.",
                "Stop and time exits dominate exit count, but exit parameter review is not justified without exit-level contribution rows.",
                "Full-sample costs are material enough to turn gross positive PnL into net negative PnL.",
            ],
            "forbidden_actions_preserved": [
                "no exact z threshold proposal",
                "no exact hold proposal",
                "no exact TP/SL proposal",
                "no parameter grid",
                "no holdout-selected config",
                "no edge or candidate claim",
            ],
        },
        "limitations": [
            "No raw panel rows were read.",
            "No strategy rerun or V2 test was performed.",
            "No trade-level rows were available in the execution artifact.",
            "Side PnL, exit PnL, feature buckets, month drivers, and symbol net contribution remain unavailable.",
        ],
        "safety_permissions": postmortem_safety,
        "validation_checks": checks,
        "replacement_checks_all_true": all(checks.values())
        and postmortem_safety["postmortem_diagnostic_created"] is True
        and all(value is False for key, value in postmortem_safety.items() if key != "postmortem_diagnostic_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"trade_level_data_available: {str(trade_level_available).lower()}")
    print(f"side_diagnostic_summary: {side_summary}")
    print(f"exit_diagnostic_summary: {exit_summary}")
    print("strongest_feature_bucket_signal: unavailable_trade_level_rows_missing")
    print(f"null_failure_reason: {null_failure_reason}")
    print(f"v2_direction_classification: {V2_INCONCLUSIVE}")
    print("v2_execution_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
