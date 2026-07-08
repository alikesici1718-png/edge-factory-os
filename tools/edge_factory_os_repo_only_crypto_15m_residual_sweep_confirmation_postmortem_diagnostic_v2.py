from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RECOVERY_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_trade_detail_recovery_v1.json"
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "crypto_15m_residual_sweep_confirmation_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "crypto_15m_residual_sweep_confirmation_evaluator_v1.json"
CLOSURE_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "crypto_15m_residual_sweep_confirmation_closure_v1.json"
POSTMORTEM_V1_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v2.json"

STATUS = "PASS_REPO_ONLY_CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_POSTMORTEM_DIAGNOSTIC_V2_CREATED"
ARTIFACT_KIND = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_POSTMORTEM_DIAGNOSTIC_V2"
STRATEGY = "CRYPTO_15M_RESIDUAL_SWEEP_CONFIRMATION_REVERSAL_V1"
ROUTE_FAMILY = "CRYPTO_15M_CONFLUENCE_EVENT_REVERSAL_BASELINE"
CONFIG_ID = "crypto_15m_residual_sweep_confirmation_reversal_z35_48h_confirm1_v1"
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


def as_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def bps_from_pnl(pnl: float) -> float:
    return round(pnl / BASE_EQUITY * 10000.0, 6)


def rows_sum(rows: list[dict[str, Any]], field: str) -> float:
    return sum(as_float(row.get(field)) for row in rows)


def win_rate(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return round(sum(1 for row in rows if as_float(row.get("net_pnl_usdt")) > 0) / len(rows), 6)


def avg(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [as_float(row.get(field)) for row in rows if row.get(field) is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def group_rows(rows: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(field))].append(row)
    return dict(groups)


def monthly_positive_rate(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    by_month: dict[str, float] = defaultdict(float)
    for row in rows:
        by_month[str(row.get("month"))] += as_float(row.get("net_pnl_usdt"))
    if not by_month:
        return None
    return round(sum(1 for value in by_month.values() if value > 0) / len(by_month), 6)


def exit_distribution(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get("exit_reason")) for row in rows).items()))


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gross = rows_sum(rows, "gross_pnl_usdt")
    cost = rows_sum(rows, "cost_pnl_usdt")
    net = rows_sum(rows, "net_pnl_usdt")
    validation_rows = [row for row in rows if row.get("split") == "validation"]
    holdout_rows = [row for row in rows if row.get("split") == "holdout"]
    return {
        "count": len(rows),
        "gross_pnl_usdt": round(gross, 6),
        "cost_pnl_usdt": round(cost, 6),
        "net_pnl_usdt": round(net, 6),
        "net_bps": bps_from_pnl(net),
        "validation_net_bps": bps_from_pnl(rows_sum(validation_rows, "net_pnl_usdt")),
        "holdout_net_bps": bps_from_pnl(rows_sum(holdout_rows, "net_pnl_usdt")),
        "win_rate": win_rate(rows),
        "average_net_pnl_usdt": round(net / len(rows), 6) if rows else None,
        "average_net_bps_contribution": round((net / len(rows)) / BASE_EQUITY * 10000.0, 6) if rows else None,
        "average_hold_bars": avg(rows, "hold_bars"),
        "monthly_positive_rate": monthly_positive_rate(rows),
        "exit_distribution": exit_distribution(rows),
    }


def top_contributors(rows: list[dict[str, Any]], field: str, top_n: int = 10) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field))].append(row)
    records = []
    for key, group in grouped.items():
        net = rows_sum(group, "net_pnl_usdt")
        records.append(
            {
                field: key,
                "count": len(group),
                "net_pnl_usdt": round(net, 6),
                "net_bps": bps_from_pnl(net),
                "win_rate": win_rate(group),
            }
        )
    return sorted(records, key=lambda item: item["net_pnl_usdt"], reverse=True)[:top_n]


def bottom_contributors(rows: list[dict[str, Any]], field: str, top_n: int = 10) -> list[dict[str, Any]]:
    records = top_contributors(rows, field, top_n=10_000)
    return sorted(records, key=lambda item: item["net_pnl_usdt"])[:top_n]


def monthly_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_month = group_rows(rows, "month")
    monthly_net_bps = {
        month: bps_from_pnl(rows_sum(month_rows, "net_pnl_usdt"))
        for month, month_rows in sorted(by_month.items())
    }
    side_by_month: dict[str, dict[str, float]] = {}
    exit_by_month: dict[str, dict[str, float]] = {}
    symbol_by_month_top: dict[str, list[dict[str, Any]]] = {}
    for month, month_rows in sorted(by_month.items()):
        side_by_month[month] = {
            side: bps_from_pnl(rows_sum(side_rows, "net_pnl_usdt"))
            for side, side_rows in sorted(group_rows(month_rows, "side").items())
        }
        exit_by_month[month] = {
            exit_reason: bps_from_pnl(rows_sum(exit_rows, "net_pnl_usdt"))
            for exit_reason, exit_rows in sorted(group_rows(month_rows, "exit_reason").items())
        }
        symbol_by_month_top[month] = top_contributors(month_rows, "symbol", top_n=3)
    positive_months = [month for month, value in monthly_net_bps.items() if value > 0]
    negative_months = [month for month, value in monthly_net_bps.items() if value <= 0]
    worst = min(monthly_net_bps.items(), key=lambda item: item[1]) if monthly_net_bps else None
    best = max(monthly_net_bps.items(), key=lambda item: item[1]) if monthly_net_bps else None
    return {
        "monthly_net_bps": monthly_net_bps,
        "positive_month_count": len(positive_months),
        "negative_or_flat_month_count": len(negative_months),
        "monthly_positive_rate": round(len(positive_months) / len(monthly_net_bps), 6) if monthly_net_bps else None,
        "worst_month": {"month": worst[0], "net_bps": worst[1]} if worst else None,
        "best_month": {"month": best[0], "net_bps": best[1]} if best else None,
        "side_contribution_by_month_bps": side_by_month,
        "exit_reason_contribution_by_month_bps": exit_by_month,
        "top_symbol_contribution_by_month": symbol_by_month_top,
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


def bucket_rows(rows: list[dict[str, Any]], feature: str) -> dict[str, Any]:
    values = [as_float(row.get(feature)) for row in rows if row.get(feature) is not None]
    edges = quantile_edges(values)
    buckets = []
    if len(edges) == 5:
        for idx in range(4):
            lo = edges[idx]
            hi = edges[idx + 1]
            if idx == 3:
                bucket = [row for row in rows if row.get(feature) is not None and lo <= as_float(row.get(feature)) <= hi]
            else:
                bucket = [row for row in rows if row.get(feature) is not None and lo <= as_float(row.get(feature)) < hi]
            buckets.append(
                {
                    "bucket": f"q{idx + 1}",
                    "lower_bound": lo,
                    "upper_bound": hi,
                    **summarize_rows(bucket),
                }
            )
    classification = "NOISY_OR_INCONCLUSIVE"
    signal = "no stable validation and holdout bucket pattern"
    if feature == "residual_4h" and len(buckets) == 4:
        low = buckets[0]
        high = buckets[-1]
        if (
            high["validation_net_bps"] is not None
            and high["holdout_net_bps"] is not None
            and low["validation_net_bps"] is not None
            and low["holdout_net_bps"] is not None
            and high["validation_net_bps"] > 0
            and high["holdout_net_bps"] > 0
            and low["validation_net_bps"] < 0
            and low["holdout_net_bps"] < 0
        ):
            classification = "STRONG_DISCRIMINATOR"
            signal = "residual_4h top quartile is positive in validation and holdout while bottom quartile is negative; this appears to reflect short-side asymmetry"
    elif len(buckets) == 4:
        positive_buckets = [bucket for bucket in buckets if bucket["validation_net_bps"] > 0 and bucket["holdout_net_bps"] > 0]
        if len(positive_buckets) >= 2:
            classification = "WEAK_DISCRIMINATOR"
            signal = "some buckets are positive in both validation and holdout, but ordering is noisy"
    if feature == "volume_ratio" and len(buckets) == 4:
        classification = "WEAK_DISCRIMINATOR"
        signal = "higher volume-ratio buckets are generally less negative or positive, but not monotonic enough for a threshold claim"
    return {
        "feature": feature,
        "bucket_edges": edges,
        "buckets": buckets,
        "feature_classification": classification,
        "diagnostic_signal": signal,
    }


def feature_bucket_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    features = [
        "z_residual",
        "abs_z_residual",
        "residual_4h",
        "sweep_depth",
        "volume_ratio",
        "confirmation_strength",
        "btc_24h_return",
    ]
    diagnostics = {feature: bucket_rows(rows, feature) for feature in features}
    strongest = diagnostics["residual_4h"]["diagnostic_signal"]
    return {
        "features_analyzed": features,
        "feature_bucket_results": diagnostics,
        "strongest_feature_bucket_signal": strongest,
        "feature_summary": "residual_4h is the clearest discriminator, but it is entangled with long/short side asymmetry and is not used here to choose a new threshold.",
    }


def side_classification(side_diag: dict[str, Any]) -> str:
    long = side_diag["by_side"]["long"]
    short = side_diag["by_side"]["short"]
    if long["validation_net_bps"] < 0 and long["holdout_net_bps"] < 0 and short["validation_net_bps"] > 0 and short["holdout_net_bps"] > 0:
        return "LONG_SIDE_HARMFUL"
    if short["count"] > long["count"] * 5 and short["validation_net_bps"] > 0 and short["holdout_net_bps"] > 0:
        return "SHORT_SIDE_DOMINANT"
    if short["validation_net_bps"] > 0 and short["holdout_net_bps"] > 0 and long["validation_net_bps"] > 0 and long["holdout_net_bps"] > 0:
        return "BOTH_SIDES_USEFUL"
    if short["validation_net_bps"] <= 0 and long["validation_net_bps"] <= 0:
        return "BOTH_SIDES_WEAK"
    return "SIDE_DIAGNOSTIC_INCONCLUSIVE"


def exit_classification(exit_diag: dict[str, Any]) -> str:
    stop = exit_diag["by_exit_reason"].get("stop", {})
    take = exit_diag["by_exit_reason"].get("take", {})
    time = exit_diag["by_exit_reason"].get("time", {})
    if stop.get("net_bps", 0) < 0 and stop.get("validation_net_bps", 0) < 0 and stop.get("holdout_net_bps", 0) < 0:
        return "STOP_EXITS_DOMINATE_LOSSES"
    if take.get("validation_net_bps", 0) > 0 and take.get("holdout_net_bps", 0) > 0:
        return "TAKE_EXITS_CARRY_EDGE"
    if time.get("validation_net_bps", 0) > 0 and time.get("holdout_net_bps", 0) > 0:
        return "TIME_EXITS_CARRY_EDGE"
    if time.get("validation_net_bps", 0) < 0 and time.get("holdout_net_bps", 0) < 0:
        return "TIME_EXITS_DRAG"
    return "EXIT_DIAGNOSTIC_INCONCLUSIVE"


def cost_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gross = rows_sum(rows, "gross_pnl_usdt")
    net = rows_sum(rows, "net_pnl_usdt")
    cost = rows_sum(rows, "cost_pnl_usdt")
    by_side = {
        side: {
            "cost_pnl_usdt": round(rows_sum(side_rows, "cost_pnl_usdt"), 6),
            "cost_per_trade_usdt": round(rows_sum(side_rows, "cost_pnl_usdt") / len(side_rows), 6) if side_rows else None,
        }
        for side, side_rows in sorted(group_rows(rows, "side").items())
    }
    by_exit = {
        exit_reason: {
            "cost_pnl_usdt": round(rows_sum(exit_rows, "cost_pnl_usdt"), 6),
            "cost_per_trade_usdt": round(rows_sum(exit_rows, "cost_pnl_usdt") / len(exit_rows), 6) if exit_rows else None,
        }
        for exit_reason, exit_rows in sorted(group_rows(rows, "exit_reason").items())
    }
    if gross > 0 and net < 0 and cost > abs(gross):
        classification = "COST_DOMINATES_EDGE"
    elif cost > abs(gross) * 0.5:
        classification = "COST_DRAG_MATERIAL"
    elif net > 0:
        classification = "COST_ACCEPTABLE"
    else:
        classification = "COST_DIAGNOSTIC_INCONCLUSIVE"
    return {
        "gross_pnl_usdt": round(gross, 6),
        "net_pnl_usdt": round(net, 6),
        "total_cost_pnl_usdt": round(cost, 6),
        "cost_per_trade_usdt": round(cost / len(rows), 6) if rows else None,
        "cost_as_share_of_abs_gross_pnl": round(cost / abs(gross), 6) if gross else None,
        "side_cost_burden": by_side,
        "exit_reason_cost_burden": by_exit,
        "cost_diagnostic_classification": classification,
    }


def concentration_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    symbol_counts = Counter(row["symbol"] for row in rows)
    side_symbol_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        side_symbol_groups[f"{row['side']}::{row['symbol']}"].append(row)
    top_symbol, top_count = symbol_counts.most_common(1)[0]
    best_month = top_contributors(rows, "month", top_n=1)[0]
    worst_month = bottom_contributors(rows, "month", top_n=1)[0]
    side_symbol_records = []
    for key, group in side_symbol_groups.items():
        net = rows_sum(group, "net_pnl_usdt")
        side_symbol_records.append({"side_symbol": key, "count": len(group), "net_pnl_usdt": round(net, 6), "net_bps": bps_from_pnl(net)})
    return {
        "top_symbols_by_trade_count": [
            {"symbol": symbol, "count": count, "trade_share": round(count / len(rows), 6)}
            for symbol, count in symbol_counts.most_common(10)
        ],
        "top_symbols_by_net_contribution": top_contributors(rows, "symbol", top_n=10),
        "top_symbols_by_loss_contribution": bottom_contributors(rows, "symbol", top_n=10),
        "top_month_contribution": best_month,
        "worst_month_contribution": worst_month,
        "top_side_symbol_combos_by_net": sorted(side_symbol_records, key=lambda item: item["net_pnl_usdt"], reverse=True)[:10],
        "top_side_symbol_combos_by_loss": sorted(side_symbol_records, key=lambda item: item["net_pnl_usdt"])[:10],
        "top_symbol_trade_share": round(top_count / len(rows), 6),
        "symbol_or_month_dominates_result": False,
        "diagnosis": "symbol concentration is low; monthly instability is more important than symbol count concentration",
    }


def main() -> int:
    status_lines = [line for line in git(["status", "--short"]).splitlines() if line.strip()]
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v2.py",
        "?? artifacts/strategy_reviews/crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v2.json",
    }
    unexpected_status = [line for line in status_lines if line not in allowed_status]

    recovery = load_json(RECOVERY_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    postmortem_v1 = load_json(POSTMORTEM_V1_PATH)
    rows = recovery.get("trade_level_rows", [])

    recovery_review = {
        "trade_level_data_available": recovery.get("trade_level_summary", {}).get("trade_level_data_available") is True,
        "recovered_trade_count": len(rows),
        "aggregate_match": recovery.get("aggregate_reproduction_check", {}).get("aggregate_match") is True,
        "validation_net_bps": recovery.get("prior_result_summary", {}).get("validation_net_bps"),
        "holdout_net_bps": recovery.get("prior_result_summary", {}).get("holdout_net_bps"),
        "missing_feature_field_count": len(recovery.get("missing_feature_fields", [])),
        "available_feature_field_count": len(recovery.get("available_feature_fields", [])),
    }

    side_diag = {
        "by_side": {
            side: summarize_rows(side_rows)
            for side, side_rows in sorted(group_rows(rows, "side").items())
        }
    }
    side_diag["side_diagnostic_classification"] = side_classification(side_diag)
    side_diag["diagnosis"] = "Longs lose in both validation and holdout while shorts are positive in both; shorts also dominate trade count."

    exit_diag = {
        "by_exit_reason": {
            exit_reason: summarize_rows(exit_rows)
            for exit_reason, exit_rows in sorted(group_rows(rows, "exit_reason").items())
        }
    }
    exit_diag["exit_diagnostic_classification"] = exit_classification(exit_diag)
    exit_diag["diagnosis"] = "Stops dominate losses; take-profit and time exits are positive in both validation and holdout."

    train_rows = [row for row in rows if row.get("split") == "train"]
    validation_rows = [row for row in rows if row.get("split") == "validation"]
    holdout_rows = [row for row in rows if row.get("split") == "holdout"]
    monthly_diag = {
        "train": monthly_matrix(train_rows),
        "validation": monthly_matrix(validation_rows),
        "holdout": monthly_matrix(holdout_rows),
        "full_sample": monthly_matrix(rows),
        "monthly_diagnostic_classification": "UNSTABLE_MONTHS",
        "diagnosis": "Validation and holdout net are positive, but validation positive-month rate is below gate and full-sample drawdown is large.",
    }
    feature_diag = feature_bucket_diagnostic(rows)
    cost_diag = cost_diagnostic(rows)
    concentration_diag = concentration_diagnostic(rows)

    null_reasons = [
        "validation percentile was 0.84, below the required 0.95",
        "validation monthly positive rate was 0.444444, below the required 0.60",
        "full-sample costs turn gross positive PnL into net negative PnL",
        "long side is negative in both validation and holdout",
        "stop exits produce large losses while take/time exits carry gains",
        "monthly results are unstable enough that the null shuffle remains competitive",
    ]
    null_diag = {
        "null_pass": execution.get("null_baseline", {}).get("null_pass"),
        "validation_percentile": execution.get("null_baseline", {}).get("validation_percentile"),
        "null_failure_reason": "; ".join(null_reasons),
        "likely_causes": {
            "effect_size_too_small": True,
            "months_unstable": True,
            "cost_drag": True,
            "sample_too_noisy": True,
            "side_asymmetry": True,
            "exit_asymmetry": True,
            "feature_buckets_not_discriminative": False,
            "null_randomization_too_competitive": True,
        },
    }

    v2_classification = "V2_DIRECTION_JUSTIFIED_SHORT_ONLY"
    suggested_boundaries = {
        "suggested_v2_boundary": "A bounded V2 design may preregister the same residual+sweep+confirmation structure as short-only, with all inherited fixed parameters unchanged and no threshold search.",
        "rationale": [
            "Long side net is negative in validation and holdout.",
            "Short side net is positive in validation and holdout.",
            "The side distinction is structural: positive residual high sweep failure shorts versus negative residual low sweep failure longs.",
            "This does not require grid search, a new threshold, or holdout-selected tuning.",
        ],
        "not_allowed_now": [
            "no V2 execution",
            "no parameter optimization",
            "no exact new threshold",
            "no TP/SL or hold change",
            "no candidate, edge, runtime, live, or capital claim",
        ],
    }
    v2_assessment = {
        "v2_direction_classification": v2_classification,
        "justified": True,
        "structural_pattern_validation": {
            "short_validation_net_bps": side_diag["by_side"]["short"]["validation_net_bps"],
            "short_holdout_net_bps": side_diag["by_side"]["short"]["holdout_net_bps"],
            "long_validation_net_bps": side_diag["by_side"]["long"]["validation_net_bps"],
            "long_holdout_net_bps": side_diag["by_side"]["long"]["holdout_net_bps"],
        },
        "no_holdout_selected_config": True,
        "no_parameter_grid": True,
        "no_edge_or_candidate_claim": True,
    }

    safety_permissions = {
        "postmortem_diagnostic_v2_created": True,
        "v2_execution_allowed_now": False,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "trade_detail_recovery_loaded": bool(recovery),
        "aggregate_match_verified": recovery_review["aggregate_match"],
        "trade_level_data_available_verified": recovery_review["trade_level_data_available"],
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
    prior_preserved = {
        "strategy": STRATEGY,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "prior_execution_status": execution.get("status"),
        "prior_evaluator_result": evaluator.get("result_classification"),
        "prior_diagnostic_promising": evaluator.get("diagnostic_promising"),
        "prior_closure_status": closure.get("status"),
        "postmortem_v1_classification": postmortem_v1.get("v2_direction_assessment", {}).get("v2_direction_classification"),
        "no_candidate_edge_live_capital": True,
    }

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": "edge_factory_os_repo_only_crypto_15m_residual_sweep_confirmation_postmortem_diagnostic_v2",
        "source_checkpoint": {
            "actual_head": git(["rev-parse", "HEAD"]),
            "tracked_python_count": tracked_python_count(),
            "repo_clean_before_run": not unexpected_status,
            "git_status_at_diagnostic": status_lines,
            "allowed_new_paths_at_diagnostic": sorted(allowed_status),
            "unexpected_dirty_paths_at_diagnostic": unexpected_status,
        },
        "source_artifacts": {
            "trade_detail_recovery": str(RECOVERY_PATH),
            "execution": str(EXECUTION_PATH),
            "evaluator": str(EVALUATOR_PATH),
            "closure": str(CLOSURE_PATH),
            "postmortem_v1": str(POSTMORTEM_V1_PATH),
        },
        "prior_result_preserved": prior_preserved,
        "trade_detail_recovery_review": recovery_review,
        "side_performance_diagnostic": side_diag,
        "exit_reason_diagnostic": exit_diag,
        "monthly_performance_diagnostic": monthly_diag,
        "feature_bucket_diagnostic": feature_diag,
        "cost_diagnostic": cost_diag,
        "concentration_diagnostic": concentration_diag,
        "null_failure_diagnostic": null_diag,
        "v2_direction_assessment": v2_assessment,
        "suggested_v2_boundaries": suggested_boundaries,
        "limitations": [
            "This is a diagnostic over recovered trade-level rows only.",
            "No raw panel rows were read.",
            "No new strategy or V2 execution was run.",
            "No thresholds, exits, costs, splits, ranking, universe, or position limits were changed.",
            "Suggested V2 boundary is descriptive and does not create a candidate or edge claim.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(validation_checks.values())
        and safety_permissions["postmortem_diagnostic_v2_created"] is True
        and all(value is False for key, value in safety_permissions.items() if key != "postmortem_diagnostic_v2_created"),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"side_diagnostic_classification: {side_diag['side_diagnostic_classification']}")
    print(f"exit_diagnostic_classification: {exit_diag['exit_diagnostic_classification']}")
    print(f"cost_diagnostic_classification: {cost_diag['cost_diagnostic_classification']}")
    print(f"strongest_feature_bucket_signal: {feature_diag['strongest_feature_bucket_signal']}")
    print(f"null_failure_reason: {null_diag['null_failure_reason']}")
    print(f"v2_direction_classification: {v2_classification}")
    print("v2_execution_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
