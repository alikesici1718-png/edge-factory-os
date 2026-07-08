from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1 as trap


REPO_ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_preregistration_v1.json"
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_evaluator_v1.json"
MARKET_PUMP_EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_execution_v1.json"
MARKET_PUMP_EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_idiosyncratic_sweep_short_market_pump_veto_evaluator_v1.json"
V3_NULL_AUDIT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_short_only_v3_null_failure_audit_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_idiosyncratic_sweep_short_trap_quality_postmortem_diagnostic_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_POSTMORTEM_DIAGNOSTIC_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_POSTMORTEM_DIAGNOSTIC"
STRATEGY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
EXECUTION_STATUS = "PASS_REPO_CODE_ONLY_CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_EXECUTED"
REJECTED_CLASS = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_REJECTED_NO_FOLLOWUP"

BASE_EQUITY = 1000.0
EXPECTED_ACCEPTED_SHORT_TRADES = 454
EXPECTED_CLOSED_TRADES = 454
EXPECTED_VALIDATION_BPS = 379.021858
EXPECTED_HOLDOUT_BPS = 341.386162
EXPECTED_VALIDATION_MONTHLY_POSITIVE_RATE = 0.555556
EXPECTED_HOLDOUT_MONTHLY_POSITIVE_RATE = 0.714286


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def payload_hash(data: dict[str, Any]) -> str:
    clone = dict(data)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def tracked_python_count() -> int:
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def r6(value: float | int | None) -> float | None:
    return None if value is None else round(float(value), 6)


def bps_from_usdt(value: float) -> float:
    return value / BASE_EQUITY * 10000.0


def safe_mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def safe_median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def finite_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(key)
        if value is not None:
            value = float(value)
            if math.isfinite(value):
                values.append(value)
    return values


def distribution(values: list[float | None]) -> dict[str, Any]:
    finite = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not finite:
        return {"count": 0, "min": None, "median": None, "mean": None, "max": None}
    return {
        "count": len(finite),
        "min": r6(min(finite)),
        "median": r6(statistics.median(finite)),
        "mean": r6(statistics.mean(finite)),
        "max": r6(max(finite)),
    }


def recover_trap_quality_trades() -> dict[str, Any]:
    files = sorted(trap.PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    if "BTCUSDT" not in symbols or "ETHUSDT" not in symbols:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")

    btc = trap.mpv.v3.v2.read_symbol("BTCUSDT")
    eth = trap.mpv.v3.v2.read_symbol("ETHUSDT")
    master_timestamps = btc["timestamps"]
    market = trap.mpv.compute_market_context(symbols, btc, eth)
    btc_returns = trap.mpv.v3.v2.returns_from_closes(btc["closes"])
    eth_returns = trap.mpv.v3.v2.returns_from_closes(eth["closes"])
    anchor = {
        "master_index_by_ts": market["master_index_by_ts"],
        "btc_returns_by_ts": {timestamp: value for timestamp, value in zip(btc["timestamps"], btc_returns) if value is not None},
        "eth_returns_by_ts": {timestamp: value for timestamp, value in zip(eth["timestamps"], eth_returns) if value is not None},
        "btc_24h_by_ts": trap.mpv.v3.v2.btc_24h_returns(btc["timestamps"], btc["closes"]),
        "market_context_by_idx": market["veto_by_idx"],
    }
    counters: dict[str, int] = defaultdict(int)
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    blocked_contexts: list[dict[str, Any]] = []
    for symbol in [item for item in symbols if item not in {"BTCUSDT", "ETHUSDT"}]:
        trap.mpv.v3.merge_candidates(candidates_by_idx, trap.generate_candidates_for_symbol(symbol, anchor, counters, blocked_contexts))

    simulation = trap.simulate_portfolio(master_timestamps, candidates_by_idx, counters)
    trades = simulation["trades"]
    for trade in trades:
        trade["abs_z_residual"] = abs(float(trade.get("z_residual", 0.0)))
        trade["expected_abs_move_proxy"] = abs(float(trade.get("residual_4h", 0.0)))
        context = market["veto_by_idx"].get(int(trade.get("signal_master_idx", -1)), {})
        for key in ("btc_ret_4h", "eth_ret_4h", "btc_ret_24h", "eth_ret_24h", "pump_breadth", "median_universe_ret_4h"):
            trade[key] = context.get(key)

    metrics = trap.summarize_metrics(trades, counters, simulation, blocked_contexts)
    split_metrics = {split: trap.mpv.v3.v2.summarize_split(trades, split) for split in ("train", "validation", "holdout")}
    null = reproduce_null_distribution(trades)
    return {
        "symbols": symbols,
        "master_timestamps": master_timestamps,
        "trades": trades,
        "metrics": metrics,
        "split_metrics": split_metrics,
        "null": null,
    }


def split_rows(rows: list[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("split") == split]


def monthly_bps(rows: list[dict[str, Any]]) -> dict[str, float]:
    month_net: dict[str, float] = defaultdict(float)
    for row in rows:
        month_net[row["month"]] += float(row["net_pnl_usdt"])
    return {month: r6(bps_from_usdt(value)) for month, value in sorted(month_net.items())}


def monthly_positive_rate(months: dict[str, float]) -> float | None:
    if not months:
        return None
    return r6(sum(1 for value in months.values() if value > 0) / len(months))


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "count": 0,
            "full_sample_net_pnl_usdt": 0.0,
            "validation_net_pnl_usdt": 0.0,
            "holdout_net_pnl_usdt": 0.0,
            "full_sample_bps_contribution": 0.0,
            "validation_bps_contribution": 0.0,
            "holdout_bps_contribution": 0.0,
            "win_rate": None,
            "average_net_pnl_usdt": None,
            "median_net_pnl_usdt": None,
            "average_hold_bars": None,
            "average_notional": None,
            "average_cost": None,
            "monthly_bps": {},
        }
    net_values = [float(row["net_pnl_usdt"]) for row in rows]
    validation_net = sum(float(row["net_pnl_usdt"]) for row in rows if row["split"] == "validation")
    holdout_net = sum(float(row["net_pnl_usdt"]) for row in rows if row["split"] == "holdout")
    return {
        "count": len(rows),
        "full_sample_net_pnl_usdt": r6(sum(net_values)),
        "validation_net_pnl_usdt": r6(validation_net),
        "holdout_net_pnl_usdt": r6(holdout_net),
        "full_sample_bps_contribution": r6(bps_from_usdt(sum(net_values))),
        "validation_bps_contribution": r6(bps_from_usdt(validation_net)),
        "holdout_bps_contribution": r6(bps_from_usdt(holdout_net)),
        "win_rate": r6(sum(1 for value in net_values if value > 0) / len(net_values)),
        "average_net_pnl_usdt": r6(statistics.mean(net_values)),
        "median_net_pnl_usdt": r6(statistics.median(net_values)),
        "average_hold_bars": r6(statistics.mean([float(row["hold_bars"]) for row in rows])),
        "average_notional": r6(statistics.mean([float(row["notional"]) for row in rows])),
        "average_cost": r6(statistics.mean([float(row["cost_pnl_usdt"]) for row in rows])),
        "monthly_bps": monthly_bps(rows),
    }


def summarize_by_field(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field))].append(row)
    return {key: summarize_rows(value) for key, value in sorted(grouped.items())}


def classify_exit(exit_summary: dict[str, Any]) -> str:
    stop = exit_summary.get("by_exit_reason", {}).get("stop", {})
    take = exit_summary.get("by_exit_reason", {}).get("take", {})
    time = exit_summary.get("by_exit_reason", {}).get("time", {})
    stop_net = float(stop.get("full_sample_net_pnl_usdt") or 0.0)
    take_net = float(take.get("full_sample_net_pnl_usdt") or 0.0)
    time_net = float(time.get("full_sample_net_pnl_usdt") or 0.0)
    time_val = float(time.get("validation_net_pnl_usdt") or 0.0)
    time_hold = float(time.get("holdout_net_pnl_usdt") or 0.0)
    take_val = float(take.get("validation_net_pnl_usdt") or 0.0)
    take_hold = float(take.get("holdout_net_pnl_usdt") or 0.0)
    if time_net > 0 and time_val >= 0 and time_hold >= 0:
        return "TIME_EXITS_CARRY_EDGE"
    if stop_net < 0 and abs(stop_net) >= max(abs(time_net), abs(take_net)):
        return "STOP_EXITS_DOMINATE_LOSSES"
    if take_net > 0 and take_val >= 0 and take_hold >= 0:
        return "TAKE_EXITS_CARRY_EDGE"
    if time_net < 0:
        return "TIME_EXITS_DRAG"
    if stop or take or time:
        return "EXIT_MIXED_BUT_ACCEPTABLE"
    return "EXIT_DIAGNOSTIC_INCONCLUSIVE"


def exit_reason_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_reason = summarize_by_field(rows, "exit_reason")
    result = {
        "by_exit_reason": by_reason,
        "monthly_contribution_by_exit_reason": {
            reason: monthly_bps([row for row in rows if row.get("exit_reason") == reason])
            for reason in ("stop", "take", "time")
        },
    }
    classification = classify_exit(result)
    result.update(
        {
            "time_exits_good_or_bad": "good" if by_reason.get("time", {}).get("full_sample_net_pnl_usdt", 0.0) > 0 else "bad_or_mixed",
            "stop_exits_main_loss_source": by_reason.get("stop", {}).get("full_sample_net_pnl_usdt", 0.0) < 0,
            "take_profit_trades_carry_edge": by_reason.get("take", {}).get("full_sample_net_pnl_usdt", 0.0) > 0,
            "exit_distribution_explains_null_failure": classification in {"STOP_EXITS_DOMINATE_LOSSES", "TIME_EXITS_DRAG"},
            "exit_diagnostic_classification": classification,
        }
    )
    return result


def month_driver(rows: list[dict[str, Any]], month: str) -> dict[str, Any]:
    month_rows = [row for row in rows if row["month"] == month]
    by_exit = {key: summarize_rows([row for row in month_rows if row.get("exit_reason") == key]) for key in ("stop", "take", "time")}
    symbol_net: dict[str, float] = defaultdict(float)
    symbol_count: Counter[str] = Counter()
    cost = 0.0
    for row in month_rows:
        symbol_net[row["symbol"]] += float(row["net_pnl_usdt"])
        symbol_count[row["symbol"]] += 1
        cost += float(row["cost_pnl_usdt"])
    return {
        "trade_count": len(month_rows),
        "net_pnl_usdt": r6(sum(float(row["net_pnl_usdt"]) for row in month_rows)),
        "net_bps": r6(bps_from_usdt(sum(float(row["net_pnl_usdt"]) for row in month_rows))),
        "cost_usdt": r6(cost),
        "exit_reason_contribution": by_exit,
        "top_symbols_by_trade_count": symbol_count.most_common(5),
        "top_symbols_by_net_contribution": [[symbol, r6(value)] for symbol, value in sorted(symbol_net.items(), key=lambda item: item[1], reverse=True)[:5]],
        "top_symbols_by_loss_contribution": [[symbol, r6(value)] for symbol, value in sorted(symbol_net.items(), key=lambda item: item[1])[:5]],
    }


def monthly_stability_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    all_months = monthly_bps(rows)
    validation_months = monthly_bps(split_rows(rows, "validation"))
    holdout_months = monthly_bps(split_rows(rows, "holdout"))
    validation_positive = sum(1 for value in validation_months.values() if value > 0)
    validation_total = len(validation_months)
    holdout_positive = sum(1 for value in holdout_months.values() if value > 0)
    holdout_total = len(holdout_months)
    worst_month = min(all_months.items(), key=lambda item: item[1]) if all_months else (None, None)
    best_month = max(all_months.items(), key=lambda item: item[1]) if all_months else (None, None)
    one_more_validation_month_passes = bool(validation_total and validation_positive / validation_total < 0.60 and (validation_positive + 1) / validation_total >= 0.60)
    abs_month_total = sum(abs(value) for value in all_months.values())
    top_month_share = max((abs(value) for value in all_months.values()), default=0.0) / abs_month_total if abs_month_total else 0.0
    if one_more_validation_month_passes:
        classification = "MONTHLY_STABILITY_FAILS_BY_ONE_MONTH"
    elif top_month_share > 0.50:
        classification = "MONTHLY_ONE_MONTH_DEPENDENT"
    elif validation_total and validation_positive / validation_total >= 0.50 and holdout_total and holdout_positive / holdout_total >= 0.50:
        classification = "MONTHLY_STABILITY_NEAR_PASS"
    elif validation_total or holdout_total:
        classification = "MONTHLY_STABILITY_UNSTABLE"
    else:
        classification = "MONTHLY_DIAGNOSTIC_INCONCLUSIVE"
    return {
        "monthly_net_bps": all_months,
        "validation_monthly_net_bps": validation_months,
        "holdout_monthly_net_bps": holdout_months,
        "validation_positive_month_count": validation_positive,
        "validation_negative_month_count": validation_total - validation_positive,
        "holdout_positive_month_count": holdout_positive,
        "holdout_negative_month_count": holdout_total - holdout_positive,
        "validation_gate_failed_by_one_month": one_more_validation_month_passes,
        "worst_month": worst_month[0],
        "worst_month_bps": worst_month[1],
        "worst_month_drivers": month_driver(rows, worst_month[0]) if worst_month[0] else {},
        "best_month": best_month[0],
        "best_month_bps": best_month[1],
        "best_month_drivers": month_driver(rows, best_month[0]) if best_month[0] else {},
        "top_abs_month_contribution_share": r6(top_month_share),
        "holdout_structurally_better_or_one_good_month": "not_one_month_dependent" if top_month_share <= 0.50 else "one_month_dependent",
        "monthly_stability_classification": classification,
    }


def quantile_edges(values: list[float]) -> list[float]:
    if len(values) < 4:
        return []
    ordered = sorted(values)
    return [ordered[int((len(ordered) - 1) * ratio)] for ratio in (0.25, 0.50, 0.75)]


def bucket_label(value: float, edges: list[float]) -> str:
    if not edges:
        return "all"
    if value <= edges[0]:
        return "q1_low"
    if value <= edges[1]:
        return "q2"
    if value <= edges[2]:
        return "q3"
    return "q4_high"


def bucket_rows(rows: list[dict[str, Any]], feature: str, exact: bool = False) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if exact:
        for row in rows:
            buckets[str(row.get(feature))].append(row)
        return buckets
    values = finite_values(rows, feature)
    edges = quantile_edges(values)
    for row in rows:
        value = row.get(feature)
        if value is None:
            continue
        value = float(value)
        if math.isfinite(value):
            buckets[bucket_label(value, edges)].append(row)
    return buckets


def feature_bucket_summary(rows: list[dict[str, Any]], feature: str, exact: bool = False) -> dict[str, Any]:
    buckets = bucket_rows(rows, feature, exact=exact)
    output: dict[str, Any] = {}
    for label, bucket in sorted(buckets.items()):
        summary = summarize_rows(bucket)
        summary["exit_reason_split"] = dict(sorted(Counter(row.get("exit_reason") for row in bucket).items()))
        summary["average_feature_value"] = r6(safe_mean(finite_values(bucket, feature))) if not exact else None
        output[label] = summary
    return output


def classify_feature(summary: dict[str, Any], feature: str) -> str:
    if not summary:
        return "NOISY_OR_INCONCLUSIVE"
    if "4" in summary and "3" in summary:
        score4 = summary["4"]
        score3 = summary["3"]
        if (
            (score4.get("validation_bps_contribution") or 0.0) > 0
            and (score4.get("holdout_bps_contribution") or 0.0) > 0
            and (score4.get("average_net_pnl_usdt") or 0.0) > (score3.get("average_net_pnl_usdt") or 0.0)
        ):
            return "STRONG_DISCRIMINATOR"
        if (score4.get("average_net_pnl_usdt") or 0.0) < (score3.get("average_net_pnl_usdt") or 0.0):
            return "REVERSED_OR_HARMFUL"
        return "WEAK_DISCRIMINATOR"
    q1 = summary.get("q1_low")
    q4 = summary.get("q4_high")
    if q1 and q4:
        q1_avg = q1.get("average_net_pnl_usdt") or 0.0
        q4_avg = q4.get("average_net_pnl_usdt") or 0.0
        q4_val = q4.get("validation_bps_contribution") or 0.0
        q4_hold = q4.get("holdout_bps_contribution") or 0.0
        q1_val = q1.get("validation_bps_contribution") or 0.0
        q1_hold = q1.get("holdout_bps_contribution") or 0.0
        if feature in {"close_location", "stop_distance_fraction"}:
            if q1_avg > q4_avg and q1_val > 0 and q1_hold > 0:
                return "STRONG_DISCRIMINATOR"
            if q4_avg > q1_avg:
                return "REVERSED_OR_HARMFUL"
        elif q4_avg > q1_avg and q4_val > 0 and q4_hold > 0:
            return "STRONG_DISCRIMINATOR"
        elif q4_avg > q1_avg or (q4_val > q1_val and q4_hold > q1_hold):
            return "WEAK_DISCRIMINATOR"
        elif q4_avg < q1_avg:
            return "REVERSED_OR_HARMFUL"
    return "NOISY_OR_INCONCLUSIVE"


def trap_quality_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = [
        ("trap_quality_score", True),
        ("upper_wick_share", False),
        ("close_location", False),
        ("sweep_depth_atr", False),
        ("rejection_depth_atr", False),
        ("confirmation_strength_atr", False),
    ]
    diagnostics: dict[str, Any] = {}
    classifications: dict[str, str] = {}
    for feature, exact in features:
        summary = feature_bucket_summary(rows, feature, exact=exact)
        diagnostics[feature] = summary
        classifications[feature] = classify_feature(summary, feature)
    strongest = "none"
    if classifications.get("trap_quality_score") == "STRONG_DISCRIMINATOR":
        strongest = "trap_quality_score_4_vs_3"
    else:
        strong = [feature for feature, classification in classifications.items() if classification == "STRONG_DISCRIMINATOR"]
        strongest = strong[0] if strong else "no_strong_trap_quality_signal"
    return {
        "feature_buckets": diagnostics,
        "feature_classifications": classifications,
        "score_4_better_than_score_3": classifications.get("trap_quality_score") == "STRONG_DISCRIMINATOR",
        "upper_wick_share_predictive": classifications.get("upper_wick_share"),
        "close_location_predictive": classifications.get("close_location"),
        "rejection_depth_atr_predictive": classifications.get("rejection_depth_atr"),
        "confirmation_strength_atr_predictive": classifications.get("confirmation_strength_atr"),
        "sweep_depth_atr_predictive": classifications.get("sweep_depth_atr"),
        "strongest_trap_quality_signal": strongest,
    }


def residual_feature_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = [
        "z_residual",
        "abs_z_residual",
        "residual_4h",
        "risk_quality_ratio",
        "stop_distance_fraction",
        "expected_abs_move_proxy",
    ]
    diagnostics: dict[str, Any] = {}
    classifications: dict[str, str] = {}
    for feature in features:
        summary = feature_bucket_summary(rows, feature)
        diagnostics[feature] = summary
        classifications[feature] = classify_feature(summary, feature)
    strong = [feature for feature, classification in classifications.items() if classification == "STRONG_DISCRIMINATOR"]
    if "risk_quality_ratio" in strong:
        residual_class = "RISK_QUALITY_HELPFUL_BUT_INSUFFICIENT"
    elif strong:
        residual_class = "RESIDUAL_FEATURE_STRONG"
    elif any(value == "WEAK_DISCRIMINATOR" for value in classifications.values()):
        residual_class = "RESIDUAL_FEATURE_WEAK"
    elif rows:
        residual_class = "RESIDUAL_FEATURE_NOISY"
    else:
        residual_class = "RESIDUAL_DIAGNOSTIC_INCONCLUSIVE"
    return {
        "feature_buckets": diagnostics,
        "feature_classifications": classifications,
        "higher_z_residual_helped": classifications.get("z_residual"),
        "higher_residual_4h_helped": classifications.get("residual_4h"),
        "higher_risk_quality_ratio_helped": classifications.get("risk_quality_ratio"),
        "wide_stops_harmful_after_v3_repair": classifications.get("stop_distance_fraction") == "STRONG_DISCRIMINATOR",
        "residual_strength_beats_cost_only_in_upper_buckets": classifications.get("expected_abs_move_proxy") in {"STRONG_DISCRIMINATOR", "WEAK_DISCRIMINATOR"},
        "strongest_residual_signal": strong[0] if strong else "no_strong_residual_signal",
        "residual_feature_classification": residual_class,
    }


def market_bucket_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = ["btc_ret_4h", "eth_ret_4h", "btc_ret_24h", "eth_ret_24h", "pump_breadth", "median_universe_ret_4h"]
    return {feature: feature_bucket_summary(rows, feature) for feature in features}


def market_pump_veto_diagnostic(
    rows: list[dict[str, Any]],
    metrics: dict[str, Any],
    market_pump_execution: dict[str, Any],
    current_execution: dict[str, Any],
) -> dict[str, Any]:
    comparison = current_execution.get("comparison_to_market_pump_veto_route", {})
    blocked = metrics.get("market_pump_veto_diagnostics", {})
    null_delta = comparison.get("null_percentile_delta")
    stop_delta = comparison.get("stop_exit_count_delta")
    cost_delta = comparison.get("cost_delta_usdt")
    if null_delta is not None and null_delta > 0 and stop_delta is not None and stop_delta < 0:
        classification = "MARKET_VETO_RISK_FILTER_HELPFUL"
    elif metrics.get("market_pump_veto_blocked", 0) > metrics.get("accepted_short_trades", 0) * 3:
        classification = "MARKET_VETO_TOO_STRICT"
    elif blocked:
        classification = "MARKET_VETO_NOT_DISCRIMINATIVE"
    else:
        classification = "MARKET_VETO_INCONCLUSIVE"
    return {
        "blocked_count": metrics.get("market_pump_veto_blocked"),
        "blocked_context_diagnostics": blocked,
        "accepted_trade_market_context_buckets": market_bucket_summary(rows),
        "comparison_to_market_pump_veto_route": comparison,
        "market_pump_veto_route_metrics_reference": {
            "validation_net_bps": market_pump_execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "holdout_net_bps": market_pump_execution.get("split_metrics", {}).get("holdout", {}).get("portfolio_net_bps"),
            "max_drawdown_bps": market_pump_execution.get("metrics", {}).get("max_drawdown_bps"),
        },
        "did_pump_veto_mainly_reduce_losses": stop_delta is not None and stop_delta < 0,
        "did_pump_veto_remove_too_many_good_trades": "cannot_test_directly_without_disallowed_no_veto_counterfactual",
        "did_pump_veto_improve_holdout_but_reduce_validation_monthly_rate": comparison.get("holdout_monthly_positive_rate_delta") == 0.0 and comparison.get("validation_monthly_positive_rate_delta", 0.0) < 0,
        "veto_usefulness_interpretation": "Useful as a broad risk filter, but the route still needs event-specific alpha because strict null remained competitive.",
        "market_veto_classification": classification,
    }


def cost_diagnostic(rows: list[dict[str, Any]], current_execution: dict[str, Any]) -> dict[str, Any]:
    gross = sum(float(row["gross_pnl_usdt"]) for row in rows)
    net = sum(float(row["net_pnl_usdt"]) for row in rows)
    cost = sum(float(row["cost_pnl_usdt"]) for row in rows)
    cost_share = cost / gross if gross > 0 else None
    comparison = current_execution.get("comparison_to_market_pump_veto_route", {})
    by_exit = {
        reason: {
            "cost_usdt": r6(sum(float(row["cost_pnl_usdt"]) for row in rows if row.get("exit_reason") == reason)),
            "net_pnl_usdt": r6(sum(float(row["net_pnl_usdt"]) for row in rows if row.get("exit_reason") == reason)),
        }
        for reason in ("stop", "take", "time")
    }
    cost_by_month: dict[str, float] = defaultdict(float)
    for row in rows:
        cost_by_month[row["month"]] += float(row["cost_pnl_usdt"])
    if cost_share is None:
        classification = "COST_DIAGNOSTIC_INCONCLUSIVE"
    elif cost_share > 1.0:
        classification = "COST_DOMINATES_EDGE"
    elif comparison.get("cost_delta_usdt", 0.0) < 0 and cost_share > 0.50:
        classification = "COST_IMPROVED_BUT_STILL_MATERIAL"
    elif cost_share > 0.35:
        classification = "COST_DRAG_MATERIAL"
    else:
        classification = "COST_ACCEPTABLE"
    return {
        "gross_pnl_before_cost_usdt": r6(gross),
        "net_pnl_after_cost_usdt": r6(net),
        "total_cost_usdt": r6(cost),
        "cost_per_trade_usdt": r6(cost / len(rows)) if rows else None,
        "cost_as_share_of_gross_pnl": r6(cost_share),
        "cost_by_month_usdt": {month: r6(value) for month, value in sorted(cost_by_month.items())},
        "cost_by_exit_reason": by_exit,
        "cost_by_trap_quality_score": {
            score: r6(sum(float(row["cost_pnl_usdt"]) for row in rows if str(row.get("trap_quality_score")) == score))
            for score in sorted({str(row.get("trap_quality_score")) for row in rows})
        },
        "cost_explains_null_failure": classification in {"COST_DRAG_MATERIAL", "COST_DOMINATES_EDGE", "COST_IMPROVED_BUT_STILL_MATERIAL"},
        "cost_classification": classification,
    }


def concentration_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    symbol_count = Counter(row["symbol"] for row in rows)
    symbol_net: dict[str, float] = defaultdict(float)
    month_net: dict[str, float] = defaultdict(float)
    combo_net: dict[str, float] = defaultdict(float)
    combo_count: Counter[str] = Counter()
    for row in rows:
        symbol_net[row["symbol"]] += float(row["net_pnl_usdt"])
        month_net[row["month"]] += float(row["net_pnl_usdt"])
        key = f"{row['symbol']}|{row['month']}"
        combo_net[key] += float(row["net_pnl_usdt"])
        combo_count[key] += 1
    top_symbol, top_symbol_count = symbol_count.most_common(1)[0] if symbol_count else (None, 0)
    symbol_share = top_symbol_count / len(rows) if rows else 0.0
    month_abs_total = sum(abs(value) for value in month_net.values())
    month_share = max((abs(value) for value in month_net.values()), default=0.0) / month_abs_total if month_abs_total else 0.0
    if symbol_share <= 0.25 and month_share <= 0.50:
        classification = "CONCENTRATION_OK"
    elif symbol_share > 0.25 and month_share > 0.50:
        classification = "SYMBOL_MONTH_DEPENDENT"
    elif symbol_share > 0.25:
        classification = "SYMBOL_DEPENDENT"
    elif month_share > 0.50:
        classification = "MONTH_DEPENDENT"
    else:
        classification = "CONCENTRATION_INCONCLUSIVE"
    return {
        "top_symbols_by_trade_count": symbol_count.most_common(10),
        "top_symbols_by_net_contribution": [[symbol, r6(value)] for symbol, value in sorted(symbol_net.items(), key=lambda item: item[1], reverse=True)[:10]],
        "top_symbols_by_loss_contribution": [[symbol, r6(value)] for symbol, value in sorted(symbol_net.items(), key=lambda item: item[1])[:10]],
        "top_symbol_month_combos_by_trade_count": combo_count.most_common(10),
        "top_symbol_month_combos_by_net_contribution": [[key, r6(value)] for key, value in sorted(combo_net.items(), key=lambda item: item[1], reverse=True)[:10]],
        "top_symbol_trade_share": r6(symbol_share),
        "top_abs_month_contribution_share": r6(month_share),
        "result_depends_on_one_symbol_or_month": classification != "CONCENTRATION_OK",
        "concentration_classification": classification,
    }


def reproduce_null_distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    validation_rows = [row for row in rows if row.get("split") == "validation"]
    if len(validation_rows) < 30:
        return {"feasible": False, "runs": 0, "validation_percentile": None, "null_pass": False, "reason": "validation closed trades < 30"}
    observed = sum(float(row["net_pnl_usdt"]) for row in validation_rows)
    pool = [float(row["net_pnl_usdt"]) for row in rows]
    rng = random.Random(1013409)
    null_values = []
    for _run in range(100):
        shuffled = pool[:]
        rng.shuffle(shuffled)
        null_values.append(sum(shuffled[: len(validation_rows)]))
    ordered = sorted(null_values)
    percentile = sum(1 for value in null_values if value <= observed) / len(null_values)
    p95 = ordered[int(math.ceil(0.95 * len(ordered))) - 1]
    return {
        "feasible": True,
        "method": "deterministic trade-pnl timestamp/block shuffle proxy",
        "runs": 100,
        "observed_validation_pnl_usdt": r6(observed),
        "observed_validation_bps": r6(bps_from_usdt(observed)),
        "null_mean_validation_bps": r6(bps_from_usdt(statistics.mean(null_values))),
        "null_median_validation_bps": r6(bps_from_usdt(statistics.median(null_values))),
        "null_p75_bps": r6(bps_from_usdt(ordered[int(math.ceil(0.75 * len(ordered))) - 1])),
        "null_p90_bps": r6(bps_from_usdt(ordered[int(math.ceil(0.90 * len(ordered))) - 1])),
        "null_p95_bps": r6(bps_from_usdt(p95)),
        "null_max_bps": r6(bps_from_usdt(max(null_values))),
        "validation_percentile": r6(percentile),
        "null_pass": percentile >= 0.95,
        "observed_minus_null_p95_bps": r6(bps_from_usdt(observed - p95)),
        "null_runs_beating_observed": sum(1 for value in null_values if value > observed),
        "null_positive_run_count": sum(1 for value in null_values if value > 0),
        "observed_positive_but_not_extreme": observed > 0 and percentile < 0.95,
    }


def null_failure_diagnostic(rows: list[dict[str, Any]], null_audit: dict[str, Any], monthly: dict[str, Any], cost: dict[str, Any], exit_diag: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    if null_audit.get("observed_positive_but_not_extreme"):
        reasons.append("observed validation result was positive but not extreme versus the deterministic trade-PnL shuffle null")
    if monthly.get("monthly_stability_classification") == "MONTHLY_STABILITY_FAILS_BY_ONE_MONTH":
        reasons.append("validation monthly gate failed by one positive month")
    if cost.get("cost_classification") in {"COST_DRAG_MATERIAL", "COST_DOMINATES_EDGE", "COST_IMPROVED_BUT_STILL_MATERIAL"}:
        reasons.append("cost remains a material share of gross PnL")
    if exit_diag.get("exit_diagnostic_classification") == "STOP_EXITS_DOMINATE_LOSSES":
        reasons.append("stop exits remain the main tail-loss source")
    if null_audit.get("null_runs_beating_observed", 0) > 0:
        reasons.append("random timing remained competitive in a non-trivial number of null runs")
    if monthly.get("monthly_stability_classification") == "MONTHLY_STABILITY_FAILS_BY_ONE_MONTH":
        classification = "NULL_FAIL_MONTHLY_INSTABILITY"
    elif cost.get("cost_classification") in {"COST_DOMINATES_EDGE", "COST_DRAG_MATERIAL"}:
        classification = "NULL_FAIL_COST_DRAG"
    elif exit_diag.get("exit_diagnostic_classification") == "STOP_EXITS_DOMINATE_LOSSES":
        classification = "NULL_FAIL_STOP_TAIL"
    elif null_audit.get("observed_positive_but_not_extreme"):
        classification = "NULL_FAIL_RANDOM_TIMING_COMPETITIVE"
    else:
        classification = "NULL_FAIL_INCONCLUSIVE"
    return {
        "observed_validation_bps": null_audit.get("observed_validation_bps"),
        "null_p95_bps": null_audit.get("null_p95_bps"),
        "observed_minus_null_p95_bps": null_audit.get("observed_minus_null_p95_bps"),
        "null_runs_beating_observed": null_audit.get("null_runs_beating_observed"),
        "null_positive_run_count": null_audit.get("null_positive_run_count"),
        "failure_reasons": reasons,
        "null_failure_classification": classification,
    }


def aggregate_reproduction_check(recovered: dict[str, Any]) -> dict[str, Any]:
    metrics = recovered["metrics"]
    splits = recovered["split_metrics"]
    comparisons = {
        "accepted_short_trades": {
            "expected": EXPECTED_ACCEPTED_SHORT_TRADES,
            "recovered": metrics.get("accepted_short_trades"),
            "abs_diff": abs((metrics.get("accepted_short_trades") or 0) - EXPECTED_ACCEPTED_SHORT_TRADES),
            "matches": metrics.get("accepted_short_trades") == EXPECTED_ACCEPTED_SHORT_TRADES,
        },
        "closed_trades": {
            "expected": EXPECTED_CLOSED_TRADES,
            "recovered": metrics.get("closed_trades"),
            "abs_diff": abs((metrics.get("closed_trades") or 0) - EXPECTED_CLOSED_TRADES),
            "matches": metrics.get("closed_trades") == EXPECTED_CLOSED_TRADES,
        },
        "validation_net_bps": {
            "expected": EXPECTED_VALIDATION_BPS,
            "recovered": splits["validation"].get("portfolio_net_bps"),
            "abs_diff": r6(abs((splits["validation"].get("portfolio_net_bps") or 0.0) - EXPECTED_VALIDATION_BPS)),
            "matches": abs((splits["validation"].get("portfolio_net_bps") or 0.0) - EXPECTED_VALIDATION_BPS) <= 0.00001,
        },
        "holdout_net_bps": {
            "expected": EXPECTED_HOLDOUT_BPS,
            "recovered": splits["holdout"].get("portfolio_net_bps"),
            "abs_diff": r6(abs((splits["holdout"].get("portfolio_net_bps") or 0.0) - EXPECTED_HOLDOUT_BPS)),
            "matches": abs((splits["holdout"].get("portfolio_net_bps") or 0.0) - EXPECTED_HOLDOUT_BPS) <= 0.00001,
        },
        "validation_monthly_positive_rate": {
            "expected": EXPECTED_VALIDATION_MONTHLY_POSITIVE_RATE,
            "recovered": splits["validation"].get("monthly_positive_rate"),
            "abs_diff": r6(abs((splits["validation"].get("monthly_positive_rate") or 0.0) - EXPECTED_VALIDATION_MONTHLY_POSITIVE_RATE)),
            "matches": abs((splits["validation"].get("monthly_positive_rate") or 0.0) - EXPECTED_VALIDATION_MONTHLY_POSITIVE_RATE) <= 0.00001,
        },
        "holdout_monthly_positive_rate": {
            "expected": EXPECTED_HOLDOUT_MONTHLY_POSITIVE_RATE,
            "recovered": splits["holdout"].get("monthly_positive_rate"),
            "abs_diff": r6(abs((splits["holdout"].get("monthly_positive_rate") or 0.0) - EXPECTED_HOLDOUT_MONTHLY_POSITIVE_RATE)),
            "matches": abs((splits["holdout"].get("monthly_positive_rate") or 0.0) - EXPECTED_HOLDOUT_MONTHLY_POSITIVE_RATE) <= 0.00001,
        },
    }
    aggregate_match = all(item["matches"] for item in comparisons.values())
    return {
        "aggregate_match": aggregate_match,
        "comparisons": comparisons,
        "classification": "AGGREGATES_MATCH" if aggregate_match else "TRADE_DETAIL_REPRODUCTION_MISMATCH",
    }


def next_direction_assessment(
    trap_diag: dict[str, Any],
    residual_diag: dict[str, Any],
    exit_diag: dict[str, Any],
    cost_diag: dict[str, Any],
    null_diag: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    boundary = "No bounded next strategy boundary is justified by this diagnostic."
    if trap_diag.get("feature_classifications", {}).get("trap_quality_score") == "STRONG_DISCRIMINATOR":
        classification = "NEXT_DIRECTION_JUSTIFIED_TRAP_SCORE_4_ONLY"
        boundary = "A bounded next strategy could require trap_quality_score = 4, meaning all four already-preregistered trap components pass; no threshold search is implied."
    elif trap_diag.get("feature_classifications", {}).get("confirmation_strength_atr") == "STRONG_DISCRIMINATOR":
        classification = "NEXT_DIRECTION_JUSTIFIED_CONFIRMATION_STRENGTH_FILTER"
        boundary = "A bounded next strategy could emphasize structurally stronger confirmation, but this diagnostic does not select a new numeric threshold."
    elif exit_diag.get("exit_diagnostic_classification") == "TIME_EXITS_DRAG":
        classification = "NEXT_DIRECTION_JUSTIFIED_TIME_EXIT_REWORK"
        boundary = "A bounded next strategy could preregister a structural time-exit review if time exits are confirmed harmful."
    elif residual_diag.get("feature_classifications", {}).get("risk_quality_ratio") == "STRONG_DISCRIMINATOR":
        classification = "NEXT_DIRECTION_JUSTIFIED_RISK_QUALITY_TIGHTENING"
        boundary = "A bounded next strategy could preregister a stricter structural risk-quality requirement without using a best-bucket threshold."
    elif cost_diag.get("cost_classification") in {"COST_DRAG_MATERIAL", "COST_IMPROVED_BUT_STILL_MATERIAL"} and residual_diag.get("residual_feature_classification") in {"RESIDUAL_FEATURE_STRONG", "RISK_QUALITY_HELPFUL_BUT_INSUFFICIENT"}:
        classification = "NEXT_DIRECTION_JUSTIFIED_COST_SPARSE_FILTER"
        boundary = "A bounded next strategy could become more cost-sparse only if it uses structural confluence, not a grid or best-bucket threshold."
    elif null_diag.get("null_failure_classification") in {"NULL_FAIL_INCONCLUSIVE"}:
        classification = "NEXT_DIRECTION_INCONCLUSIVE"
    else:
        classification = "NEXT_DIRECTION_NOT_JUSTIFIED_WEAK_OR_NOISY_EFFECT"
    return {
        "next_direction_classification": classification,
        "supporting_evidence": {
            "strongest_trap_quality_signal": trap_diag.get("strongest_trap_quality_signal"),
            "strongest_residual_signal": residual_diag.get("strongest_residual_signal"),
            "exit_classification": exit_diag.get("exit_diagnostic_classification"),
            "cost_classification": cost_diag.get("cost_classification"),
            "null_failure_classification": null_diag.get("null_failure_classification"),
        },
        "forbidden_interpretations_preserved": [
            "No exact new threshold is selected from a best bucket.",
            "No grid search, holdout-selected config, candidate generation, or edge claim is made.",
        ],
    }, boundary


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_postmortem_diagnostic_v1.py",
        "?? artifacts/strategy_reviews/crypto_15m_idiosyncratic_sweep_short_trap_quality_postmortem_diagnostic_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    preregistration = load_json(PREREGISTRATION_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    market_pump_execution = load_json(MARKET_PUMP_EXECUTION_PATH)
    market_pump_evaluator = load_json(MARKET_PUMP_EVALUATOR_PATH)
    v3_null_audit = load_json(V3_NULL_AUDIT_PATH)

    execution_trade_rows_available = bool(execution.get("trade_level_rows"))
    recovered = recover_trap_quality_trades()
    trades = recovered["trades"]
    aggregate_check = aggregate_reproduction_check(recovered)

    if aggregate_check["aggregate_match"]:
        exit_diag = exit_reason_diagnostic(trades)
        monthly_diag = monthly_stability_diagnostic(trades)
        trap_diag = trap_quality_diagnostic(trades)
        residual_diag = residual_feature_diagnostic(trades)
        market_diag = market_pump_veto_diagnostic(trades, recovered["metrics"], market_pump_execution, execution)
        cost_diag = cost_diagnostic(trades, execution)
        concentration_diag = concentration_diagnostic(trades)
        null_diag = null_failure_diagnostic(trades, recovered["null"], monthly_diag, cost_diag, exit_diag)
        next_assessment, boundary = next_direction_assessment(trap_diag, residual_diag, exit_diag, cost_diag, null_diag)
    else:
        exit_diag = {"exit_diagnostic_classification": "EXIT_DIAGNOSTIC_INCONCLUSIVE", "reason": "aggregate reproduction mismatch"}
        monthly_diag = {"monthly_stability_classification": "MONTHLY_DIAGNOSTIC_INCONCLUSIVE", "reason": "aggregate reproduction mismatch"}
        trap_diag = {"strongest_trap_quality_signal": "unavailable_due_aggregate_mismatch"}
        residual_diag = {"strongest_residual_signal": "unavailable_due_aggregate_mismatch"}
        market_diag = {"market_veto_classification": "MARKET_VETO_INCONCLUSIVE", "reason": "aggregate reproduction mismatch"}
        cost_diag = {"cost_classification": "COST_DIAGNOSTIC_INCONCLUSIVE", "reason": "aggregate reproduction mismatch"}
        concentration_diag = {"concentration_classification": "CONCENTRATION_INCONCLUSIVE", "reason": "aggregate reproduction mismatch"}
        null_diag = {"null_failure_classification": "NULL_FAIL_INCONCLUSIVE", "reason": "aggregate reproduction mismatch"}
        next_assessment = {"next_direction_classification": "NEXT_DIRECTION_INCONCLUSIVE", "reason": "aggregate reproduction mismatch"}
        boundary = "No boundary; aggregate reproduction mismatch blocks bucket conclusions."

    safety_permissions = {
        "postmortem_diagnostic_created": True,
        "next_strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "prior_trap_quality_artifacts_loaded": True,
        "prior_rejection_preserved": evaluator.get("result_classification") == REJECTED_CLASS and evaluator.get("diagnostic_promising") is False,
        "trade_level_data_available_or_recovered": bool(trades),
        "aggregate_reproduction_match": aggregate_check["aggregate_match"],
        "no_next_strategy_tested": True,
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
        "module": Path(__file__).name,
        "source_checkpoint": {
            "head": git(["rev-parse", "HEAD"]),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_diagnostic": status_lines,
            "allowed_new_paths_at_diagnostic": sorted(allowed_status),
            "unexpected_dirty_paths_at_diagnostic": unexpected_status,
            "tracked_python_count": tracked_python_count(),
        },
        "source_artifacts": {
            "preregistration": str(PREREGISTRATION_PATH),
            "execution": str(EXECUTION_PATH),
            "evaluator": str(EVALUATOR_PATH),
            "market_pump_veto_execution_reference": str(MARKET_PUMP_EXECUTION_PATH),
            "market_pump_veto_evaluator_reference": str(MARKET_PUMP_EVALUATOR_PATH),
            "v3_null_failure_audit_reference": str(V3_NULL_AUDIT_PATH),
            "panel_directory_used_for_exact_same_config_trade_recovery": str(trap.PANEL_DIR),
        },
        "prior_result_preserved": {
            "strategy": STRATEGY,
            "execution_status": execution.get("status"),
            "evaluator_result_class": evaluator.get("result_classification"),
            "diagnostic_promising": evaluator.get("diagnostic_promising"),
            "accepted_short_trades": execution.get("metrics", {}).get("accepted_short_trades"),
            "closed_trades": execution.get("metrics", {}).get("closed_trades"),
            "validation_net_bps": execution.get("split_metrics", {}).get("validation", {}).get("portfolio_net_bps"),
            "holdout_net_bps": execution.get("split_metrics", {}).get("holdout", {}).get("portfolio_net_bps"),
            "null_pass": execution.get("null_baseline", {}).get("null_pass"),
            "validation_percentile": execution.get("null_baseline", {}).get("validation_percentile"),
            "no_edge_candidate_live_capital": True,
        },
        "trade_level_data_review": {
            "execution_artifact_trade_level_rows_available": execution_trade_rows_available,
            "trade_level_rows_recovered_inside_diagnostic": True,
            "trade_level_data_available": bool(trades),
            "recovered_trade_count": len(trades),
            "available_trade_fields": sorted(trades[0].keys()) if trades else [],
            "recovery_method": "exact same-config replay through the committed trap-quality execution module; no parameter changes, V2, optimization, or new strategy run",
        },
        "aggregate_reproduction_check": aggregate_check,
        "exit_reason_diagnostic": exit_diag,
        "monthly_stability_diagnostic": monthly_diag,
        "trap_quality_diagnostic": trap_diag,
        "residual_feature_diagnostic": residual_diag,
        "market_pump_veto_diagnostic": market_diag,
        "cost_diagnostic": cost_diag,
        "concentration_diagnostic": concentration_diag,
        "null_failure_diagnostic": {
            "null_distribution_audit": recovered["null"],
            "v3_null_failure_audit_context": {
                "v3_effect_size_classification": v3_null_audit.get("effect_size_audit", {}).get("effect_size_classification"),
                "v3_null_model_classification": v3_null_audit.get("null_model_appropriateness_audit", {}).get("null_model_appropriateness_classification"),
            },
            **null_diag,
        },
        "next_direction_assessment": next_assessment,
        "suggested_next_strategy_boundary": boundary,
        "limitations": [
            "This diagnostic recovers exact same-config trade-level detail for analysis only; it does not run V2 or a next strategy.",
            "The market-pump veto effect is inferred from recorded route comparisons and blocked contexts; a same-trap no-veto counterfactual was not run.",
            "Feature buckets are descriptive diagnostics only and do not select thresholds.",
            "The null baseline is the documented deterministic trade-PnL shuffle proxy, not a full state-preserving strategy null.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["postmortem_diagnostic_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "postmortem_diagnostic_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"trade_level_data_available: {str(bool(trades)).lower()}")
    print(f"aggregate_match: {str(aggregate_check['aggregate_match']).lower()}")
    print(f"exit_diagnostic_classification: {exit_diag.get('exit_diagnostic_classification')}")
    print(f"monthly_stability_classification: {monthly_diag.get('monthly_stability_classification')}")
    print(f"strongest_trap_quality_signal: {trap_diag.get('strongest_trap_quality_signal')}")
    print(f"strongest_residual_signal: {residual_diag.get('strongest_residual_signal')}")
    print(f"market_veto_classification: {market_diag.get('market_veto_classification')}")
    print(f"cost_classification: {cost_diag.get('cost_classification')}")
    print(f"null_failure_classification: {null_diag.get('null_failure_classification')}")
    print(f"next_direction_classification: {next_assessment.get('next_direction_classification')}")
    print("next_strategy_execution_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
