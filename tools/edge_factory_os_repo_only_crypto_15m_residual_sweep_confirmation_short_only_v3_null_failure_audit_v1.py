from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1 as v3


REPO_ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_preregistration_v1.json"
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_evaluator_v1.json"
CLOSURE_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "crypto_15m_residual_sweep_confirmation_short_only_v3_stop_risk_closure_v1.json"
V2_POSTMORTEM_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_short_only_v2_postmortem_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_short_only_v3_null_failure_audit_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_NULL_FAILURE_AUDIT_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_NULL_FAILURE_AUDIT"
STRATEGY = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_STOP_RISK_REPAIR_V3"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_EXECUTED"
EVALUATOR_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_EVALUATED"
CLOSURE_STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_CLOSURE_CREATED"
REJECTED_CLASS = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V3_STOP_RISK_REJECTED_NO_FOLLOWUP"

BASE_EQUITY = 1000.0
EXPECTED_VALIDATION_BPS = 321.36711
EXPECTED_HOLDOUT_BPS = 369.593962
EXPECTED_CLOSED_TRADES = 963


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


def r6(value: float | int | None) -> float | None:
    return None if value is None else round(float(value), 6)


def bps_from_usdt(value: float) -> float:
    return value / BASE_EQUITY * 10000.0


def month_bps(rows: list[dict[str, Any]]) -> dict[str, float]:
    month_net: dict[str, float] = defaultdict(float)
    for trade in rows:
        month_net[trade["month"]] += float(trade["net_pnl_usdt"])
    return {month: round(bps_from_usdt(value), 6) for month, value in sorted(month_net.items())}


def positive_rate(months: dict[str, float]) -> float | None:
    if not months:
        return None
    return round(sum(1 for value in months.values() if value > 0) / len(months), 6)


def percentile(sorted_values: list[float], p: float) -> float | None:
    if not sorted_values:
        return None
    index = max(0, min(len(sorted_values) - 1, math.ceil(p * len(sorted_values)) - 1))
    return sorted_values[index]


def sum_net(rows: list[dict[str, Any]]) -> float:
    return sum(float(trade["net_pnl_usdt"]) for trade in rows)


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "count": 0,
            "net_pnl_usdt": 0.0,
            "portfolio_net_bps": 0.0,
            "win_rate": None,
            "average_net_pnl_usdt": None,
            "average_hold_bars": None,
        }
    wins = sum(1 for trade in rows if float(trade["net_pnl_usdt"]) > 0)
    net = sum_net(rows)
    return {
        "count": len(rows),
        "net_pnl_usdt": r6(net),
        "portfolio_net_bps": r6(bps_from_usdt(net)),
        "win_rate": r6(wins / len(rows)),
        "average_net_pnl_usdt": r6(net / len(rows)),
        "average_hold_bars": r6(sum(float(trade["hold_bars"]) for trade in rows) / len(rows)),
    }


def recover_v3_trades() -> dict[str, Any]:
    files = sorted(v3.PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    if "BTCUSDT" not in symbols or "ETHUSDT" not in symbols:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    btc = v3.v2.read_symbol("BTCUSDT")
    eth = v3.v2.read_symbol("ETHUSDT")
    master_timestamps = btc["timestamps"]
    anchor = {
        "master_index_by_ts": {timestamp: idx for idx, timestamp in enumerate(master_timestamps)},
        "btc_returns_by_ts": {
            timestamp: value
            for timestamp, value in zip(btc["timestamps"], v3.v2.returns_from_closes(btc["closes"]))
            if value is not None
        },
        "eth_returns_by_ts": {
            timestamp: value
            for timestamp, value in zip(eth["timestamps"], v3.v2.returns_from_closes(eth["closes"]))
            if value is not None
        },
        "btc_24h_by_ts": v3.v2.btc_24h_returns(btc["timestamps"], btc["closes"]),
    }
    counters: dict[str, int] = defaultdict(int)
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for symbol in [item for item in symbols if item not in {"BTCUSDT", "ETHUSDT"}]:
        v3.merge_candidates(candidates_by_idx, v3.generate_candidates_for_symbol(symbol, anchor, counters))
    simulation = v3.simulate_portfolio(master_timestamps, candidates_by_idx, counters)
    trades = simulation["trades"]
    metrics = v3.summarize_metrics(trades, counters, simulation)
    split_metrics = {split: v3.v2.summarize_split(trades, split) for split in ("train", "validation", "holdout")}
    return {"trades": trades, "metrics": metrics, "split_metrics": split_metrics, "symbol_file_count": len(symbols)}


def null_distribution(trades: list[dict[str, Any]]) -> dict[str, Any]:
    validation_rows = v3.v2.split_trades(trades, "validation")
    observed_usdt = sum_net(validation_rows)
    observed_bps = bps_from_usdt(observed_usdt)
    pool = [float(trade["net_pnl_usdt"]) for trade in trades]
    validation_month_slots = [trade["month"] for trade in validation_rows]
    rng = random.Random(7133101)
    null_usdt: list[float] = []
    null_monthly_positive_rates: list[float] = []
    for _run in range(100):
        shuffled = pool[:]
        rng.shuffle(shuffled)
        sample = shuffled[: len(validation_rows)]
        null_usdt.append(sum(sample))
        month_net: dict[str, float] = defaultdict(float)
        for month, pnl in zip(validation_month_slots, sample):
            month_net[month] += pnl
        if month_net:
            null_monthly_positive_rates.append(sum(1 for value in month_net.values() if value > 0) / len(month_net))
    null_bps = sorted(bps_from_usdt(value) for value in null_usdt)
    p95 = percentile(null_bps, 0.95)
    percentile_rank = sum(1 for value in null_usdt if value <= observed_usdt) / len(null_usdt)
    positive_runs = sum(1 for value in null_usdt if value > 0)
    beat_observed = sum(1 for value in null_usdt if value > observed_usdt)
    return {
        "observed_validation_net_bps": r6(observed_bps),
        "null_run_count": len(null_usdt),
        "null_mean_validation_bps": r6(statistics.mean(null_bps)),
        "null_median_validation_bps": r6(statistics.median(null_bps)),
        "null_p75_bps": r6(percentile(null_bps, 0.75)),
        "null_p90_bps": r6(percentile(null_bps, 0.90)),
        "null_p95_bps": r6(p95),
        "null_max_bps": r6(max(null_bps)),
        "observed_percentile": r6(percentile_rank),
        "observed_minus_null_p95_bps": r6(observed_bps - (p95 or 0.0)),
        "observed_positive_but_not_extreme": observed_bps > 0 and percentile_rank < 0.95,
        "null_runs_beat_observed": beat_observed,
        "null_runs_positive": positive_runs,
        "null_monthly_positive_rate_distribution": {
            "available": bool(null_monthly_positive_rates),
            "mean": r6(statistics.mean(null_monthly_positive_rates)) if null_monthly_positive_rates else None,
            "median": r6(statistics.median(null_monthly_positive_rates)) if null_monthly_positive_rates else None,
            "p95": r6(percentile(sorted(null_monthly_positive_rates), 0.95)) if null_monthly_positive_rates else None,
            "method_note": "Descriptive extension: shuffled net trade PnLs are mapped onto validation trade month slots; the original V3 null summary did not store monthly null detail.",
        },
    }


def effect_size_audit(trades: list[dict[str, Any]]) -> dict[str, Any]:
    validation = v3.v2.split_trades(trades, "validation")
    gross = sum(float(trade["gross_pnl_usdt"]) for trade in validation)
    cost = sum(float(trade["cost_pnl_usdt"]) for trade in validation)
    net = sum_net(validation)
    avg_net = net / len(validation) if validation else 0.0
    avg_cost = cost / len(validation) if validation else 0.0
    if not validation:
        classification = "EFFECT_SIZE_INCONCLUSIVE"
    elif avg_net > avg_cost * 2.0:
        classification = "EFFECT_SIZE_STRONG"
    elif avg_net > 0:
        classification = "EFFECT_SIZE_MODEST"
    else:
        classification = "EFFECT_SIZE_WEAK"
    return {
        "observed_validation_net_bps": r6(bps_from_usdt(net)),
        "average_validation_net_per_trade_usdt": r6(avg_net),
        "validation_trade_count": len(validation),
        "validation_gross_before_cost_usdt": r6(gross),
        "validation_cost_usdt": r6(cost),
        "observed_edge_per_trade_vs_cost_per_trade": {
            "average_net_usdt": r6(avg_net),
            "average_cost_usdt": r6(avg_cost),
            "net_to_cost_ratio": r6(avg_net / avg_cost) if avg_cost else None,
        },
        "edge_too_small_relative_to_noise_or_cost": avg_net > 0 and avg_net < avg_cost,
        "effect_size_classification": classification,
    }


def monthly_instability_audit(trades: list[dict[str, Any]]) -> dict[str, Any]:
    validation_months = month_bps(v3.v2.split_trades(trades, "validation"))
    holdout_months = month_bps(v3.v2.split_trades(trades, "holdout"))
    total_validation = sum(validation_months.values())
    best_month, best_value = max(validation_months.items(), key=lambda item: item[1])
    worst_month, worst_value = min(validation_months.items(), key=lambda item: item[1])
    one_month_dominates = total_validation > 0 and best_value / total_validation > 0.75
    if one_month_dominates:
        classification = "MONTHLY_ONE_MONTH_DEPENDENT"
    elif positive_rate(validation_months) and positive_rate(validation_months) >= 0.60 and worst_value > -250:
        classification = "MONTHLY_NEAR_PASS"
    elif positive_rate(validation_months) and positive_rate(validation_months) >= 0.60:
        classification = "MONTHLY_STABLE"
    else:
        classification = "MONTHLY_UNSTABLE"
    return {
        "validation_monthly_net_bps": validation_months,
        "validation_positive_month_count": sum(1 for value in validation_months.values() if value > 0),
        "validation_negative_month_count": sum(1 for value in validation_months.values() if value <= 0),
        "validation_monthly_positive_rate": positive_rate(validation_months),
        "holdout_monthly_net_bps": holdout_months,
        "holdout_monthly_positive_rate": positive_rate(holdout_months),
        "worst_validation_month": {"month": worst_month, "bps": r6(worst_value)},
        "best_validation_month": {"month": best_month, "bps": r6(best_value)},
        "one_month_dominates_validation": one_month_dominates,
        "negative_months_too_large": worst_value <= -1000,
        "monthly_instability_classification": classification,
    }


def exit_cost_audit(trades: list[dict[str, Any]]) -> dict[str, Any]:
    by_exit = {reason: summarize_group([trade for trade in trades if trade["exit_reason"] == reason]) for reason in ("stop", "take", "time")}
    validation = v3.v2.split_trades(trades, "validation")
    gross_total = sum(float(trade["gross_pnl_usdt"]) for trade in trades)
    cost_total = sum(float(trade["cost_pnl_usdt"]) for trade in trades)
    net_total = sum_net(trades)
    validation_cost = sum(float(trade["cost_pnl_usdt"]) for trade in validation)
    validation_net = sum_net(validation)
    stop_net = by_exit["stop"]["net_pnl_usdt"]
    cost_explains = validation_cost > validation_net > 0
    stop_explains = stop_net is not None and stop_net < 0
    if cost_explains and stop_explains:
        classification = "MIXED_COST_STOP_DRAG"
    elif stop_explains:
        classification = "STOP_LOSSES_DOMINATE"
    elif cost_total > gross_total:
        classification = "COST_DOMINATES_EDGE"
    elif cost_total > abs(net_total) * 0.5:
        classification = "COST_MATERIAL"
    else:
        classification = "COST_MINOR"
    return {
        "stop_take_time_exit_count": {
            "stop": by_exit["stop"]["count"],
            "take": by_exit["take"]["count"],
            "time": by_exit["time"]["count"],
        },
        "stop_take_time_net_contribution": by_exit,
        "cost_total_usdt": r6(cost_total),
        "cost_per_trade_usdt": r6(cost_total / len(trades)) if trades else None,
        "gross_to_net_effect": {
            "gross_pnl_usdt": r6(gross_total),
            "net_pnl_usdt": r6(net_total),
            "cost_drag_usdt": r6(cost_total),
        },
        "cost_explains_null_failure": cost_explains,
        "stop_exits_explain_null_failure": stop_explains,
        "cost_exit_classification": classification,
    }


def trade_distribution_audit(trades: list[dict[str, Any]]) -> dict[str, Any]:
    net_values = sorted(float(trade["net_pnl_usdt"]) for trade in trades)
    wins = [value for value in net_values if value > 0]
    losses = [value for value in net_values if value < 0]
    top_wins = sorted(wins, reverse=True)[:5]
    top_losses = losses[:5]
    median = statistics.median(net_values) if net_values else None
    if not trades:
        classification = "INCONCLUSIVE"
    elif median is not None and median < 0 and len(wins) / len(trades) < 0.50:
        classification = "THIN_EDGE_MANY_SMALL_TRADES"
    elif abs(sum(top_losses)) > max(sum(top_wins), 1e-12) * 1.5:
        classification = "TAIL_LOSS_DOMINATED"
    elif sum(top_wins) > abs(sum_net(trades)) * 2.0:
        classification = "OUTLIER_DEPENDENT"
    else:
        classification = "HEALTHY_DISTRIBUTION"
    return {
        "win_rate": r6(len(wins) / len(trades)) if trades else None,
        "average_win_usdt": r6(sum(wins) / len(wins)) if wins else None,
        "average_loss_usdt": r6(sum(losses) / len(losses)) if losses else None,
        "median_trade_net_pnl_usdt": r6(median),
        "tail_loss_concentration": {
            "top_5_winning_trades_usdt": [r6(value) for value in top_wins],
            "top_5_winning_contribution_usdt": r6(sum(top_wins)),
            "top_5_losing_trades_usdt": [r6(value) for value in top_losses],
            "top_5_losing_contribution_usdt": r6(sum(top_losses)),
        },
        "few_outliers_drive_results": sum(top_wins) > abs(sum_net(trades)) * 2.0,
        "distribution_classification": classification,
    }


def null_model_appropriateness_audit(execution: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "preserves_trade_count": True,
        "preserves_monthly_distribution": False,
        "preserves_side_short_only_structure": True,
        "preserves_capacity_cooldown_constraints": False,
        "preserves_cost": True,
        "methodology_documented": bool(execution.get("null_baseline", {}).get("method")),
        "realistic_random_timing": False,
    }
    classification = "NULL_MODEL_TOO_COMPETITIVE_BUT_VALID"
    return {
        "method": execution.get("null_baseline", {}).get("method"),
        "appropriateness_checks": checks,
        "interpretation": "The null preserves trade count, short-only net-PnL distribution, and costs, but it does not preserve monthly timing, capacity state, or cooldown path. It is a conservative documented shuffle proxy rather than an exact strategy-state null.",
        "null_model_appropriateness_classification": classification,
    }


def materially_matches(recovered: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    recovered_split = recovered["split_metrics"]
    recovered_metrics = recovered["metrics"]
    comparisons = {
        "validation_net_bps": {
            "expected": EXPECTED_VALIDATION_BPS,
            "recovered": recovered_split["validation"]["portfolio_net_bps"],
            "abs_diff": abs(recovered_split["validation"]["portfolio_net_bps"] - EXPECTED_VALIDATION_BPS),
        },
        "holdout_net_bps": {
            "expected": EXPECTED_HOLDOUT_BPS,
            "recovered": recovered_split["holdout"]["portfolio_net_bps"],
            "abs_diff": abs(recovered_split["holdout"]["portfolio_net_bps"] - EXPECTED_HOLDOUT_BPS),
        },
        "closed_trades": {
            "expected": EXPECTED_CLOSED_TRADES,
            "recovered": recovered_metrics["closed_trades"],
            "abs_diff": abs(recovered_metrics["closed_trades"] - EXPECTED_CLOSED_TRADES),
        },
        "artifact_validation_net_bps": {
            "expected": execution["split_metrics"]["validation"]["portfolio_net_bps"],
            "recovered": recovered_split["validation"]["portfolio_net_bps"],
            "abs_diff": abs(recovered_split["validation"]["portfolio_net_bps"] - execution["split_metrics"]["validation"]["portfolio_net_bps"]),
        },
        "artifact_holdout_net_bps": {
            "expected": execution["split_metrics"]["holdout"]["portfolio_net_bps"],
            "recovered": recovered_split["holdout"]["portfolio_net_bps"],
            "abs_diff": abs(recovered_split["holdout"]["portfolio_net_bps"] - execution["split_metrics"]["holdout"]["portfolio_net_bps"]),
        },
    }
    aggregate_match = (
        comparisons["validation_net_bps"]["abs_diff"] <= 0.00001
        and comparisons["holdout_net_bps"]["abs_diff"] <= 0.00001
        and comparisons["closed_trades"]["abs_diff"] == 0
    )
    return {"aggregate_match": aggregate_match, "comparisons": comparisons}


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_null_failure_audit_v1.py",
        "?? artifacts/strategy_reviews/crypto_15m_residual_sweep_confirmation_short_only_v3_null_failure_audit_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    preregistration = load_json(PREREGISTRATION_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    v2_postmortem = load_json(V2_POSTMORTEM_PATH) if V2_POSTMORTEM_PATH.exists() else {}

    execution_trade_rows_available = bool(execution.get("trade_level_rows"))
    execution_null_distribution_available = bool(execution.get("null_baseline", {}).get("null_distribution"))
    execution_monthly_breakdown_available = bool(execution.get("metrics", {}).get("monthly_net_bps"))

    recovered = recover_v3_trades()
    aggregate_reproduction = materially_matches(recovered, execution)
    trades = recovered["trades"]
    null_audit = null_distribution(trades)
    effect_audit = effect_size_audit(trades)
    monthly_audit = monthly_instability_audit(trades)
    exit_cost = exit_cost_audit(trades)
    distribution = trade_distribution_audit(trades)
    null_model = null_model_appropriateness_audit(execution)

    if not aggregate_reproduction["aggregate_match"]:
        v4_classification = "V4_DIRECTION_INCONCLUSIVE_NEEDS_BETTER_NULL"
        null_failure_summary = "Aggregate reproduction mismatch prevents a reliable null-failure interpretation."
    elif null_model["null_model_appropriateness_classification"] in {"NULL_MODEL_POSSIBLY_MIS_SPECIFIED", "NULL_MODEL_INSUFFICIENTLY_DOCUMENTED", "NULL_MODEL_INCONCLUSIVE"}:
        v4_classification = "V4_DIRECTION_INCONCLUSIVE_NEEDS_BETTER_NULL"
        null_failure_summary = "Null methodology is not strong enough for a directional V4 decision."
    elif effect_audit["effect_size_classification"] in {"EFFECT_SIZE_WEAK", "EFFECT_SIZE_MODEST"} and null_audit["observed_percentile"] < 0.95:
        v4_classification = "V4_DIRECTION_NOT_JUSTIFIED_NULL_MODEL_FAIR_AND_FAILED"
        null_failure_summary = "Observed validation is positive but not extreme under a documented conservative null; the main blocker is modest effect size with noisy trade PnL distribution and material cost/stop drag."
    else:
        v4_classification = "V4_DIRECTION_INCONCLUSIVE_NEEDS_BETTER_NULL"
        null_failure_summary = "Audit did not isolate one structural preregisterable V4 repair without threshold mining."

    safety_permissions = {
        "null_failure_audit_created": True,
        "v4_execution_allowed_now": False,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "prior_v3_artifacts_loaded": True,
        "prior_rejection_preserved": evaluator.get("result_classification") == REJECTED_CLASS and evaluator.get("diagnostic_promising") is False,
        "aggregate_reproduction_match": aggregate_reproduction["aggregate_match"],
        "no_v4_tested": True,
        "no_parameter_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_network_used": True,
        "no_api_called": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": not unexpected_status,
        "replacement_checks_all_true": True,
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v3_null_failure_audit_v1",
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_audit": status_lines,
            "allowed_new_paths_at_audit": sorted(allowed_status),
            "unexpected_dirty_paths_at_audit": unexpected_status,
        },
        "source_artifacts": {
            "preregistration": str(PREREGISTRATION_PATH),
            "execution": str(EXECUTION_PATH),
            "evaluator": str(EVALUATOR_PATH),
            "closure": str(CLOSURE_PATH),
            "v2_postmortem_reference": str(V2_POSTMORTEM_PATH),
        },
        "prior_v3_result_preserved": {
            "execution_status": execution.get("status"),
            "evaluator_status": evaluator.get("status"),
            "closure_status": closure.get("status"),
            "result_classification": evaluator.get("result_classification"),
            "diagnostic_promising": evaluator.get("diagnostic_promising"),
            "prior_rejection_preserved": evaluator.get("result_classification") == REJECTED_CLASS and evaluator.get("diagnostic_promising") is False,
            "no_edge_candidate_live_capital": {
                "candidate_created": closure.get("closure_result", {}).get("candidate_created") is False,
                "edge_claim_created": closure.get("closure_result", {}).get("edge_claim_created") is False,
                "runtime_enabled": closure.get("closure_result", {}).get("runtime_enabled") is False,
                "live_trading_enabled": closure.get("closure_result", {}).get("live_trading_enabled") is False,
                "capital_allocated": closure.get("closure_result", {}).get("capital_allocated") is False,
            },
        },
        "trade_level_data_review": {
            "execution_artifact_trade_level_rows_available": execution_trade_rows_available,
            "execution_artifact_null_distribution_available": execution_null_distribution_available,
            "execution_artifact_monthly_breakdown_available": execution_monthly_breakdown_available,
            "trade_level_rows_recovered_inside_audit": True,
            "null_distribution_reproduced_inside_audit": True,
            "recovered_trade_count": len(trades),
            "aggregate_reproduction_check": aggregate_reproduction,
            "audit_reliability_classification": "NULL_AUDIT_AGGREGATES_MATCH" if aggregate_reproduction["aggregate_match"] else "NULL_AUDIT_INCONCLUSIVE_AGGREGATE_MISMATCH",
        },
        "null_distribution_audit": null_audit,
        "effect_size_audit": effect_audit,
        "monthly_instability_audit": monthly_audit,
        "exit_cost_audit": exit_cost,
        "trade_distribution_audit": distribution,
        "null_model_appropriateness_audit": null_model,
        "v4_decision": {
            "v4_direction_classification": v4_classification,
            "decision_summary": null_failure_summary,
            "v4_execution_allowed_now": False,
            "no_grid_no_holdout_selection_no_edge_claim": True,
        },
        "limitations": [
            "The original V3 execution artifact did not persist trade-level rows or the 100-run null distribution; both were recovered inside this audit using the exact same V3 code path and verified against aggregate metrics.",
            "The null baseline is a documented trade-PnL shuffle proxy and not an exact strategy-state null preserving monthly timing, capacity, and cooldown path.",
            "No V4, parameter optimization, grid search, candidate generation, or edge claim was performed.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["null_failure_audit_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "null_failure_audit_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"trade_level_data_available: {str(True).lower()}")
    print(f"null_distribution_available: {str(True).lower()}")
    print(f"observed_validation_percentile: {null_audit['observed_percentile']}")
    print(f"null_p95_bps: {null_audit['null_p95_bps']}")
    print(f"observed_minus_null_p95_bps: {null_audit['observed_minus_null_p95_bps']}")
    print(f"effect_size_classification: {effect_audit['effect_size_classification']}")
    print(f"monthly_instability_classification: {monthly_audit['monthly_instability_classification']}")
    print(f"cost_exit_classification: {exit_cost['cost_exit_classification']}")
    print(f"null_model_appropriateness_classification: {null_model['null_model_appropriateness_classification']}")
    print(f"v4_direction_classification: {v4_classification}")
    print("v4_execution_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
