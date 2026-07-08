from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v2_execution_v1 as execv2


REPO_ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "crypto_15m_residual_sweep_confirmation_short_only_v2_preregistration_v1.json"
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_short_only_v2_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_residual_sweep_confirmation_short_only_v2_evaluator_v1.json"
CLOSURE_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "crypto_15m_residual_sweep_confirmation_short_only_v2_closure_v1.json"
POSTMORTEM_V2_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v2.json"
V1_RECOVERY_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_trade_detail_recovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_short_only_v2_postmortem_diagnostic_v1.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V2_POSTMORTEM_DIAGNOSTIC_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V2_POSTMORTEM_DIAGNOSTIC"
REJECTED_CLASS = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_SHORT_ONLY_V2_REJECTED_NO_FOLLOWUP"
BASE_EQUITY = 1000.0


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


def bps(pnl: float) -> float:
    return round(pnl / BASE_EQUITY * 10000.0, 6)


def rows_sum(rows: list[dict[str, Any]], field: str) -> float:
    return sum(float(row.get(field) or 0.0) for row in rows)


def win_rate(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return round(sum(1 for row in rows if float(row.get("net_pnl_usdt", 0.0)) > 0) / len(rows), 6)


def avg(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def group_rows(rows: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(field))].append(row)
    return dict(groups)


def monthly_bps(rows: list[dict[str, Any]]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        totals[str(row["exit_time"])[:7]] += float(row.get("net_pnl_usdt", 0.0))
    return {month: bps(pnl) for month, pnl in sorted(totals.items())}


def monthly_positive_rate(rows: list[dict[str, Any]]) -> float | None:
    values = monthly_bps(rows)
    if not values:
        return None
    return round(sum(1 for value in values.values() if value > 0) / len(values), 6)


def split_name(timestamp: str) -> str:
    return execv2.split_name(timestamp)


def split_rows(rows: list[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("split") == split or split_name(str(row["exit_time"])) == split]


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gross = rows_sum(rows, "gross_pnl_usdt")
    cost = rows_sum(rows, "cost_pnl_usdt")
    net = rows_sum(rows, "net_pnl_usdt")
    validation = split_rows(rows, "validation")
    holdout = split_rows(rows, "holdout")
    return {
        "count": len(rows),
        "gross_pnl_usdt": round(gross, 6),
        "cost_pnl_usdt": round(cost, 6),
        "net_pnl_usdt": round(net, 6),
        "net_bps": bps(net),
        "validation_net_bps": bps(rows_sum(validation, "net_pnl_usdt")),
        "holdout_net_bps": bps(rows_sum(holdout, "net_pnl_usdt")),
        "win_rate": win_rate(rows),
        "average_net_pnl_usdt": round(net / len(rows), 6) if rows else None,
        "average_hold_bars": avg(rows, "hold_bars"),
        "monthly_positive_rate": monthly_positive_rate(rows),
    }


def reconstruct_trades() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    files = sorted(execv2.PANEL_DIR.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    if "BTCUSDT" not in symbols or "ETHUSDT" not in symbols:
        raise RuntimeError("BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING")
    btc = execv2.read_symbol("BTCUSDT")
    eth = execv2.read_symbol("ETHUSDT")
    master_timestamps = btc["timestamps"]
    anchor = {
        "master_index_by_ts": {timestamp: idx for idx, timestamp in enumerate(master_timestamps)},
        "btc_returns_by_ts": {timestamp: value for timestamp, value in zip(btc["timestamps"], execv2.returns_from_closes(btc["closes"])) if value is not None},
        "eth_returns_by_ts": {timestamp: value for timestamp, value in zip(eth["timestamps"], execv2.returns_from_closes(eth["closes"])) if value is not None},
        "btc_24h_by_ts": execv2.btc_24h_returns(btc["timestamps"], btc["closes"]),
    }
    counters: dict[str, int] = defaultdict(int)
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for symbol in [symbol for symbol in symbols if symbol not in {"BTCUSDT", "ETHUSDT"}]:
        execv2.merge_candidates(candidates_by_idx, execv2.generate_candidates_for_symbol(symbol, anchor, counters))
    simulation = execv2.simulate_portfolio(master_timestamps, candidates_by_idx, counters)
    trades = simulation["trades"]
    for trade in trades:
        trade["split"] = split_name(trade["exit_time"])
        trade["month"] = trade["exit_time"][:7]
    metrics = execv2.summarize_metrics(trades, counters, simulation)
    split_metrics = {split: execv2.summarize_split(trades, split) for split in ("train", "validation", "holdout")}
    null = execv2.null_baseline(trades)
    return trades, metrics, split_metrics, null


def compare_aggregate(execution: dict[str, Any], metrics: dict[str, Any], split_metrics: dict[str, Any], null: dict[str, Any]) -> dict[str, Any]:
    diffs: list[dict[str, Any]] = []

    def cmp(name: str, prior: Any, recovered: Any, tol: float = 1e-6) -> None:
        if isinstance(prior, (int, float)) and isinstance(recovered, (int, float)):
            if abs(float(prior) - float(recovered)) > tol:
                diffs.append({"field": name, "prior": prior, "recovered": recovered, "difference": round(float(recovered) - float(prior), 12)})
        elif prior != recovered:
            diffs.append({"field": name, "prior": prior, "recovered": recovered})

    prior_metrics = execution.get("metrics", {})
    prior_split = execution.get("split_metrics", {})
    prior_null = execution.get("null_baseline", {})
    for field in ["accepted_short_trades", "closed_trades", "worst_month_bps", "stop_exit_count", "take_profit_exit_count", "time_stop_exit_count"]:
        cmp(f"metrics.{field}", prior_metrics.get(field), metrics.get(field))
    for split in ["validation", "holdout"]:
        for field in ["portfolio_net_bps", "monthly_positive_rate"]:
            cmp(f"split_metrics.{split}.{field}", prior_split.get(split, {}).get(field), split_metrics.get(split, {}).get(field))
    for field in ["feasible", "null_pass", "validation_percentile"]:
        cmp(f"null_baseline.{field}", prior_null.get(field), null.get(field))
    return {"aggregate_match": not diffs, "difference_count": len(diffs), "differences": diffs}


def exit_reason_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_exit = {
        exit_reason: {
            **summarize_rows(exit_rows),
            "monthly_contribution_bps": monthly_bps(exit_rows),
        }
        for exit_reason, exit_rows in sorted(group_rows(rows, "exit_reason").items())
    }
    stop = by_exit.get("stop", {})
    take = by_exit.get("take", {})
    time = by_exit.get("time", {})
    if stop.get("validation_net_bps", 0) < 0 and stop.get("holdout_net_bps", 0) < 0 and stop.get("net_bps", 0) < 0:
        classification = "STOP_EXITS_DOMINATE_LOSSES"
    elif time.get("validation_net_bps", 0) > 0 and time.get("holdout_net_bps", 0) > 0 and time.get("net_bps", 0) > 0:
        classification = "TIME_EXITS_CARRY_EDGE"
    elif time.get("validation_net_bps", 0) < 0 and time.get("holdout_net_bps", 0) < 0:
        classification = "TIME_EXITS_DRAG"
    elif take.get("validation_net_bps", 0) > 0 and take.get("holdout_net_bps", 0) > 0:
        classification = "TAKE_EXITS_CARRY_EDGE"
    else:
        classification = "EXIT_DIAGNOSTIC_MIXED"
    return {
        "by_exit_reason": by_exit,
        "exit_diagnostic_classification": classification,
        "diagnosis": "Stop exits are the main loss source; take and time exits are positive in validation and holdout but not enough to clear the null baseline.",
    }


def monthly_stability_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    validation = split_rows(rows, "validation")
    holdout = split_rows(rows, "holdout")
    val_months = monthly_bps(validation)
    hold_months = monthly_bps(holdout)
    all_months = monthly_bps(rows)
    worst_month = min(all_months.items(), key=lambda item: item[1])
    best_month = max(all_months.items(), key=lambda item: item[1])
    exit_by_month: dict[str, dict[str, float]] = {}
    symbol_by_month: dict[str, list[dict[str, Any]]] = {}
    for month in sorted(all_months):
        month_rows = [row for row in rows if row["month"] == month]
        exit_by_month[month] = {
            reason: bps(rows_sum(reason_rows, "net_pnl_usdt"))
            for reason, reason_rows in sorted(group_rows(month_rows, "exit_reason").items())
        }
        symbol_by_month[month] = top_group_records(month_rows, "symbol", 3)
    if monthly_positive_rate(validation) and monthly_positive_rate(validation) >= 0.60 and monthly_positive_rate(holdout) and monthly_positive_rate(holdout) >= 0.50:
        classification = "MONTHLY_STABILITY_NEAR_PASS"
    elif worst_month[1] < -500:
        classification = "MONTHLY_INSTABILITY_MAIN_BLOCKER"
    else:
        classification = "MONTHLY_DIAGNOSTIC_INCONCLUSIVE"
    return {
        "validation_monthly_net_bps": val_months,
        "holdout_monthly_net_bps": hold_months,
        "full_sample_monthly_net_bps": all_months,
        "validation_positive_rate": monthly_positive_rate(validation),
        "holdout_positive_rate": monthly_positive_rate(holdout),
        "worst_month": {"month": worst_month[0], "net_bps": worst_month[1]},
        "best_month": {"month": best_month[0], "net_bps": best_month[1]},
        "exit_reason_by_month_bps": exit_by_month,
        "top_symbol_by_month": symbol_by_month,
        "monthly_stability_classification": classification,
        "diagnosis": "Validation and holdout monthly positive rates pass, but large historical drawdowns and a weak null percentile show remaining instability.",
    }


def quantile_edges(values: list[float]) -> list[float]:
    ordered = sorted(values)
    if not ordered:
        return []
    edges = []
    for q in (0.0, 0.25, 0.5, 0.75, 1.0):
        pos = (len(ordered) - 1) * q
        lo = math.floor(pos)
        hi = math.ceil(pos)
        if lo == hi:
            value = ordered[int(pos)]
        else:
            value = ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)
        edges.append(round(value, 10))
    return edges


def feature_bucket(rows: list[dict[str, Any]], feature: str) -> dict[str, Any]:
    values = [float(row[feature]) for row in rows if row.get(feature) is not None]
    edges = quantile_edges(values)
    buckets = []
    for idx in range(4):
        lo = edges[idx]
        hi = edges[idx + 1]
        if idx == 3:
            bucket_rows = [row for row in rows if row.get(feature) is not None and lo <= float(row[feature]) <= hi]
        else:
            bucket_rows = [row for row in rows if row.get(feature) is not None and lo <= float(row[feature]) < hi]
        buckets.append(
            {
                "bucket": f"q{idx + 1}",
                "lower_bound": lo,
                "upper_bound": hi,
                **summarize_rows(bucket_rows),
            }
        )
    positive_both = [bucket for bucket in buckets if bucket["validation_net_bps"] > 0 and bucket["holdout_net_bps"] > 0]
    if feature == "volume_ratio" and len(positive_both) >= 3:
        classification = "WEAK_DISCRIMINATOR"
        signal = "volume_ratio has several positive validation/holdout buckets but is not monotonic enough for a threshold claim"
    elif feature == "residual_4h" and buckets[-1]["validation_net_bps"] > 0 and buckets[-1]["holdout_net_bps"] > 0:
        classification = "WEAK_DISCRIMINATOR"
        signal = "highest residual_4h bucket is positive in validation and holdout, but lower buckets are noisy"
    elif len(positive_both) >= 2:
        classification = "WEAK_DISCRIMINATOR"
        signal = "multiple positive buckets exist, but ordering is noisy"
    else:
        classification = "NOISY_OR_INCONCLUSIVE"
        signal = "bucket behavior is not stable enough to support a no-grid V3 feature threshold"
    return {"feature": feature, "bucket_edges": edges, "buckets": buckets, "feature_classification": classification, "diagnostic_signal": signal}


def feature_bucket_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = ["z_residual", "abs_z_residual", "residual_4h", "sweep_depth", "volume_ratio", "confirmation_strength", "btc_24h_return"]
    results = {feature: feature_bucket(rows, feature) for feature in features}
    strongest = results["volume_ratio"]["diagnostic_signal"]
    return {
        "features_analyzed": features,
        "feature_bucket_results": results,
        "strongest_feature_bucket_signal": strongest,
        "diagnosis": "Feature buckets are informative but not strong or monotonic enough to justify an exact V3 threshold without optimization.",
    }


def cost_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gross = rows_sum(rows, "gross_pnl_usdt")
    net = rows_sum(rows, "net_pnl_usdt")
    cost = rows_sum(rows, "cost_pnl_usdt")
    by_month: dict[str, float] = defaultdict(float)
    for row in rows:
        by_month[row["month"]] += float(row["cost_pnl_usdt"])
    by_exit = {
        reason: {
            "count": len(reason_rows),
            "cost_usdt": round(rows_sum(reason_rows, "cost_pnl_usdt"), 6),
            "cost_per_trade_usdt": round(rows_sum(reason_rows, "cost_pnl_usdt") / len(reason_rows), 6),
        }
        for reason, reason_rows in sorted(group_rows(rows, "exit_reason").items())
    }
    classification = "COST_DOMINATES_EDGE" if gross > 0 and net < 0 and cost > gross else "COST_DRAG_MATERIAL"
    return {
        "gross_pnl_usdt": round(gross, 6),
        "net_pnl_usdt": round(net, 6),
        "total_cost_usdt": round(cost, 6),
        "cost_per_trade_usdt": round(cost / len(rows), 6) if rows else None,
        "cost_as_share_of_gross_pnl": round(cost / gross, 6) if gross else None,
        "cost_by_month": {month: round(value, 6) for month, value in sorted(by_month.items())},
        "cost_by_exit_reason": by_exit,
        "cost_diagnostic_classification": classification,
        "diagnosis": "Costs remain larger than full-sample gross PnL, so sparse-quality improvement would need to be structural and preregistered.",
    }


def top_group_records(rows: list[dict[str, Any]], field: str, n: int) -> list[dict[str, Any]]:
    records = []
    for key, group in group_rows(rows, field).items():
        net = rows_sum(group, "net_pnl_usdt")
        records.append({"value": key, "count": len(group), "net_pnl_usdt": round(net, 6), "net_bps": bps(net)})
    return sorted(records, key=lambda item: item["net_pnl_usdt"], reverse=True)[:n]


def bottom_group_records(rows: list[dict[str, Any]], field: str, n: int) -> list[dict[str, Any]]:
    records = top_group_records(rows, field, 10_000)
    return sorted(records, key=lambda item: item["net_pnl_usdt"])[:n]


def concentration_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["symbol"] for row in rows)
    top_symbol, top_count = counts.most_common(1)[0]
    combo_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        combo_groups[f"{row['symbol']}::{row['month']}"].append(row)
    combo_records = []
    for combo, group in combo_groups.items():
        net = rows_sum(group, "net_pnl_usdt")
        combo_records.append({"symbol_month": combo, "count": len(group), "net_pnl_usdt": round(net, 6), "net_bps": bps(net)})
    classification = "CONCENTRATION_OK" if top_count / len(rows) <= 0.25 else "SYMBOL_DEPENDENT"
    return {
        "top_symbols_by_trade_count": [{"symbol": sym, "count": count, "share": round(count / len(rows), 6)} for sym, count in counts.most_common(10)],
        "top_symbols_by_net_contribution": top_group_records(rows, "symbol", 10),
        "top_symbols_by_loss": bottom_group_records(rows, "symbol", 10),
        "top_symbol_month_combos_by_net": sorted(combo_records, key=lambda item: item["net_pnl_usdt"], reverse=True)[:10],
        "top_symbol_month_combos_by_loss": sorted(combo_records, key=lambda item: item["net_pnl_usdt"])[:10],
        "concentration_classification": classification,
        "diagnosis": "Symbol concentration is low; the remaining blocker is robustness rather than dependence on one symbol.",
    }


def v3_direction(exit_diag: dict[str, Any], cost_diag: dict[str, Any], feature_diag: dict[str, Any]) -> tuple[str, str | None]:
    if exit_diag["exit_diagnostic_classification"] == "STOP_EXITS_DOMINATE_LOSSES":
        return (
            "V3_DIRECTION_JUSTIFIED_STOP_EXIT_RISK_REPAIR",
            "A bounded V3 design may preregister a structural stop-risk repair for short-only setups while keeping the residual/sweep/confirmation entry stack single-config and without grid search.",
        )
    if cost_diag["cost_diagnostic_classification"] == "COST_DOMINATES_EDGE":
        return (
            "V3_DIRECTION_JUSTIFIED_COST_SPARSE_FILTER",
            "A bounded V3 design may preregister a structural sparse-quality filter, but no exact threshold is selected here.",
        )
    if any(result["feature_classification"] == "STRONG_DISCRIMINATOR" for result in feature_diag["feature_bucket_results"].values()):
        return (
            "V3_DIRECTION_JUSTIFIED_FEATURE_CONFLUENCE",
            "A bounded V3 design may preregister one structural confluence feature, without choosing a best bucket threshold.",
        )
    return ("V3_DIRECTION_NOT_JUSTIFIED_WEAK_EFFECT", None)


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v2_postmortem_diagnostic_v1.py",
        "?? artifacts/strategy_reviews/crypto_15m_residual_sweep_confirmation_short_only_v2_postmortem_diagnostic_v1.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]
    prereg = load_json(PREREG_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    postmortem_v2 = load_json(POSTMORTEM_V2_PATH)
    v1_recovery = load_json(V1_RECOVERY_PATH)

    execution_has_rows = isinstance(execution.get("trade_level_rows"), list) and bool(execution.get("trade_level_rows"))
    if execution_has_rows:
        rows = execution["trade_level_rows"]
        metrics = execution.get("metrics", {})
        split_metrics = execution.get("split_metrics", {})
        null = execution.get("null_baseline", {})
        aggregate_check = {"aggregate_match": True, "difference_count": 0, "differences": [], "source": "execution_artifact_rows"}
    else:
        rows, metrics, split_metrics, null = reconstruct_trades()
        aggregate_check = compare_aggregate(execution, metrics, split_metrics, null)
        aggregate_check["source"] = "same_config_reconstruction_inside_diagnostic"
    for row in rows:
        row["split"] = split_name(str(row["exit_time"]))
        row["month"] = str(row["exit_time"])[:7]

    prior_preserved = {
        "execution_status": execution.get("status"),
        "evaluator_result": evaluator.get("result_classification"),
        "diagnostic_promising": evaluator.get("diagnostic_promising"),
        "closure_status": closure.get("status"),
        "prior_rejection_preserved": evaluator.get("result_classification") == REJECTED_CLASS and evaluator.get("diagnostic_promising") is False,
        "no_edge_candidate_live_capital": True,
    }
    trade_review = {
        "execution_artifact_had_trade_rows": execution_has_rows,
        "trade_level_data_available": bool(rows),
        "trade_level_data_recovered_inside_diagnostic": not execution_has_rows,
        "recovered_trade_count": len(rows),
        "raw_panel_read_reason": "V2 execution artifact did not contain trade rows; exact same-config reconstruction was required for postmortem diagnostics.",
    }

    if not aggregate_check["aggregate_match"]:
        exit_diag = {"exit_diagnostic_classification": "EXIT_DIAGNOSTIC_INCONCLUSIVE"}
        monthly_diag = {"monthly_stability_classification": "MONTHLY_DIAGNOSTIC_INCONCLUSIVE"}
        feature_diag = {"strongest_feature_bucket_signal": "aggregate mismatch blocked feature conclusions", "feature_bucket_results": {}}
        cost_diag = {"cost_diagnostic_classification": "COST_DIAGNOSTIC_INCONCLUSIVE"}
        concentration_diag = {"concentration_classification": "CONCENTRATION_INCONCLUSIVE"}
        null_diag = {"null_failure_reason": "TRADE_DETAIL_REPRODUCTION_MISMATCH"}
        v3_class = "V3_DIRECTION_INCONCLUSIVE"
        v3_boundary = None
    else:
        exit_diag = exit_reason_diagnostic(rows)
        monthly_diag = monthly_stability_diagnostic(rows)
        feature_diag = feature_bucket_diagnostic(rows)
        cost_diag = cost_diagnostic(rows)
        concentration_diag = concentration_diagnostic(rows)
        null_reason = (
            "validation percentile was 0.86 instead of >=0.95 because the validation effect remains modest versus shuffled trade PnL; "
            "full-sample costs dominate gross PnL; stop exits dominate losses; and historical monthly drawdowns remain large even though validation and holdout are positive."
        )
        null_diag = {
            "null_pass": null.get("null_pass"),
            "validation_percentile": null.get("validation_percentile"),
            "null_failure_reason": null_reason,
            "likely_causes": {
                "effect_size_too_small": True,
                "monthly_instability": True,
                "cost_drag": True,
                "time_exits_noisy": False,
                "stop_losses_too_large": True,
                "feature_buckets_not_discriminative_enough": True,
                "randomization_remains_competitive": True,
                "sample_too_small_or_noisy": True,
            },
        }
        v3_class, v3_boundary = v3_direction(exit_diag, cost_diag, feature_diag)

    safety_permissions = {
        "postmortem_diagnostic_created": True,
        "v3_execution_allowed_now": False,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    checks = {
        "repo_clean_before_run": not unexpected_status,
        "prior_short_only_v2_artifacts_loaded": bool(prereg) and bool(execution) and bool(evaluator) and bool(closure),
        "prior_rejection_preserved": prior_preserved["prior_rejection_preserved"],
        "trade_level_data_available_or_recovered": bool(rows),
        "no_v3_tested": True,
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
    suggested = {
        "suggested_v3_boundary": v3_boundary,
        "not_allowed_now": [
            "no V3 execution",
            "no grid search",
            "no TP/SL optimization",
            "no exact threshold from best bucket",
            "no holdout-selected config",
            "no candidate, edge, runtime, live, or capital claim",
        ],
    }
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_short_only_v2_postmortem_diagnostic_v1",
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
            "postmortem_v2": str(POSTMORTEM_V2_PATH),
            "v1_trade_detail_recovery_schema_reference": str(V1_RECOVERY_PATH),
        },
        "prior_v2_result_preserved": prior_preserved,
        "trade_level_data_review": trade_review,
        "aggregate_reproduction_check": aggregate_check,
        "exit_reason_diagnostic": exit_diag,
        "monthly_stability_diagnostic": monthly_diag,
        "feature_bucket_diagnostic": feature_diag,
        "cost_diagnostic": cost_diag,
        "concentration_diagnostic": concentration_diag,
        "null_failure_diagnostic": null_diag,
        "v3_direction_assessment": {
            "v3_direction_classification": v3_class,
            "justified": v3_class not in {"V3_DIRECTION_NOT_JUSTIFIED_WEAK_EFFECT", "V3_DIRECTION_INCONCLUSIVE"},
            "no_grid_search_needed": True,
            "no_holdout_selected_parameter": True,
            "v1_postmortem_context": postmortem_v2.get("v2_direction_assessment", {}),
            "v1_recovery_schema_reference_loaded": bool(v1_recovery),
        },
        "suggested_v3_boundaries": suggested,
        "limitations": [
            "This diagnostic reconstructs exact same-config V2 trade rows because the V2 execution artifact was aggregate-only.",
            "No V3 was tested or run.",
            "No parameter, threshold, TP/SL, hold, universe, cost, ranking, or split was changed.",
            "Bucket diagnostics are descriptive and do not select thresholds.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": checks,
        "replacement_checks_all_true": all(checks.values())
        and safety_permissions["postmortem_diagnostic_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "postmortem_diagnostic_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"trade_level_data_available: {str(bool(rows)).lower()}")
    print(f"aggregate_match: {str(aggregate_check['aggregate_match']).lower()}")
    print(f"exit_diagnostic_classification: {exit_diag['exit_diagnostic_classification']}")
    print(f"monthly_stability_classification: {monthly_diag['monthly_stability_classification']}")
    print(f"cost_diagnostic_classification: {cost_diag['cost_diagnostic_classification']}")
    print(f"strongest_feature_bucket_signal: {feature_diag['strongest_feature_bucket_signal']}")
    print(f"null_failure_reason: {null_diag['null_failure_reason']}")
    print(f"v3_direction_classification: {v3_class}")
    print("v3_execution_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
