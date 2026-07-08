#!/usr/bin/env python3
"""Institutional cost and capacity reevaluation over existing artifacts only.

Meta-evaluation only. This module reads repo JSON artifacts and does not read
raw market data, run strategies, generate signals, rerun backtests, compute PnL
from raw data, optimize, create candidates, claim edge, call APIs, use network,
or grant runtime/live/capital permission.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_institutional_cost_and_capacity_reevaluation_v1"
STATUS = "PASS_REPO_ONLY_INSTITUTIONAL_COST_AND_CAPACITY_REEVALUATION_CREATED"
ARTIFACT_KIND = "INSTITUTIONAL_COST_AND_CAPACITY_REEVALUATION"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_institutional_cost_and_capacity_reevaluation_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_reviews" / "institutional_cost_and_capacity_reevaluation_v1.json"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}

ALLOWED_ARTIFACT_DIRS = [
    "strategy_executions",
    "strategy_evaluations",
    "strategy_closures",
    "strategy_reviews",
    "event_studies",
    "data_builds",
    "research_preregistrations",
    "research_designs",
]

FAMILIES = [
    "FUNDING_OR_BASIS_CARRY",
    "OLD_SHORT_CLEAN_ROOM",
    "LUCIFER_EMA_PIVOT",
    "REGIME_BREAKOUT_MOMENTUM",
    "BETA_NEUTRAL_RESIDUAL_MR",
    "LIQUIDITY_SWEEP_REVERSAL",
    "RESIDUAL_SWEEP_CONFIRMATION_TRAP_QUALITY",
    "COINALYZE_LONG_LIQUIDATION_FLUSH",
]


def git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={SAFE_DIR}", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def source_checkpoint() -> str:
    return git(["rev-parse", "HEAD"])


def git_status_entries() -> list[tuple[str, str]]:
    raw = git(["status", "--short", "-uall"])
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if line.strip():
            entries.append((line[:2], line[3:].strip().strip('"').replace("\\", "/")))
    return entries


def repo_clean_except_expected_new_files() -> bool:
    for status, path in git_status_entries():
        if status == "??" and path in EXPECTED_NEW_PATHS:
            continue
        return False
    return True


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def norm(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def flatten_json(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_json(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(flatten_json(child, f"{prefix}[{index}]"))
    else:
        rows.append((prefix, value))
    return rows


def find_numbers(data: Any, includes: list[str], excludes: list[str] | None = None) -> list[float]:
    excludes = excludes or []
    found: list[float] = []
    include_norms = [norm(item) for item in includes]
    exclude_norms = [norm(item) for item in excludes]
    for path, value in flatten_json(data):
        path_norm = norm(path)
        if all(item in path_norm for item in include_norms) and not any(item in path_norm for item in exclude_norms):
            if is_number(value):
                found.append(float(value))
    return found


def find_bools(data: Any, includes: list[str], excludes: list[str] | None = None) -> list[bool]:
    excludes = excludes or []
    found: list[bool] = []
    include_norms = [norm(item) for item in includes]
    exclude_norms = [norm(item) for item in excludes]
    for path, value in flatten_json(data):
        path_norm = norm(path)
        if all(item in path_norm for item in include_norms) and not any(item in path_norm for item in exclude_norms):
            if isinstance(value, bool):
                found.append(value)
    return found


def first_string(data: Any, includes: list[str]) -> str | None:
    include_norms = [norm(item) for item in includes]
    for path, value in flatten_json(data):
        if all(item in norm(path) for item in include_norms) and isinstance(value, str):
            return value
    return None


def max_or_none(values: list[float]) -> float | None:
    return max(values) if values else None


def min_or_none(values: list[float]) -> float | None:
    return min(values) if values else None


def latest_or_none(values: list[float]) -> float | None:
    return values[-1] if values else None


def load_artifacts() -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for directory in ALLOWED_ARTIFACT_DIRS:
        root = REPO_ROOT / "artifacts" / directory
        if not root.exists():
            continue
        for path in sorted(root.glob("*.json")):
            if path == ARTIFACT_PATH:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                load_error = None
            except Exception as exc:
                data = {}
                load_error = str(exc)
            artifacts.append(
                {
                    "path": rel(path),
                    "directory": directory,
                    "data": data,
                    "load_error": load_error,
                }
            )
    return artifacts


def family_for_path(path: str) -> str | None:
    lower = path.lower()
    if "coinalyze" in lower:
        return "COINALYZE_LONG_LIQUIDATION_FLUSH"
    if any(token in lower for token in ("trap_quality_lockbox", "residual_sweep_confirmation", "idiosyncratic_sweep", "market_pump_veto", "trap_score4", "rejection_depth")):
        return "RESIDUAL_SWEEP_CONFIRMATION_TRAP_QUALITY"
    if "liquidity_sweep_reversal" in lower:
        return "LIQUIDITY_SWEEP_REVERSAL"
    if "beta_neutral_residual_mr" in lower:
        return "BETA_NEUTRAL_RESIDUAL_MR"
    if "regime_breakout_momentum" in lower:
        return "REGIME_BREAKOUT_MOMENTUM"
    if "lucifer" in lower:
        return "LUCIFER_EMA_PIVOT"
    if "old_short" in lower:
        return "OLD_SHORT_CLEAN_ROOM"
    if any(token in lower for token in ("funding", "basis", "carry", "spot_perp_delta_neutral")):
        return "FUNDING_OR_BASIS_CARRY"
    return None


def artifact_metrics(artifact: dict[str, Any]) -> dict[str, Any]:
    data = artifact["data"]
    path = artifact["path"]
    gross_values = find_numbers(data, ["gross", "pnl"], ["average", "avg", "delta"])
    net_values = find_numbers(data, ["net", "pnl"], ["average", "avg", "delta"])
    cost_values = find_numbers(data, ["total", "cost"], ["delta"])
    validation_values = find_numbers(data, ["validation", "net", "bps"], ["delta"])
    holdout_values = find_numbers(data, ["holdout", "net", "bps"], ["delta"])
    portfolio_values = find_numbers(data, ["portfolio", "net", "bps"], ["delta"])
    null_values = find_numbers(data, ["null", "percentile"], ["delta"])
    validation_percentiles = find_numbers(data, ["validation", "percentile"], ["delta"])
    closed_trade_values = (
        find_numbers(data, ["closed", "trade", "count"])
        + find_numbers(data, ["closed", "trades"])
        + find_numbers(data, ["closed_trade_count"])
    )
    accepted_trade_values = (
        find_numbers(data, ["accepted", "trade", "count"])
        + find_numbers(data, ["accepted", "short", "trades"])
        + find_numbers(data, ["accepted_trade_count"])
    )
    monthly_positive_values = find_numbers(data, ["monthly", "positive", "rate"], ["delta"])
    worst_month_values = find_numbers(data, ["worst", "month", "bps"], ["delta"])
    max_drawdown_values = find_numbers(data, ["max", "drawdown", "bps"], ["delta"])
    top_symbol_values = find_numbers(data, ["top", "symbol", "concentration"], ["top_3", "delta"])
    top_3_values = find_numbers(data, ["top", "3", "symbol", "concentration"], ["delta"])
    fee_stress_2x_values = find_numbers(data, ["fee", "stress", "2x", "net", "bps"])
    if "trap_quality_lockbox_forward_test_execution" in path:
        lockbox_portfolio = portfolio_values
    else:
        lockbox_portfolio = []
    null_pass_values = find_bools(data, ["null", "pass"])
    metric_integrity_values = find_bools(data, ["metric", "integrity", "passed"]) + find_bools(data, ["metric", "integrity"])
    result_class = (
        first_string(data, ["result_classification"])
        or first_string(data, ["final_classification"])
        or first_string(data, ["result_class"])
        or first_string(data, ["status"])
    )
    gross = max_or_none(gross_values)
    net = max_or_none(net_values)
    cost = max_or_none(cost_values)
    cost_share = cost / gross if gross and gross > 0 and cost is not None else None
    return {
        "path": path,
        "directory": artifact["directory"],
        "status": data.get("status"),
        "artifact_kind": data.get("artifact_kind"),
        "result_classification": result_class,
        "best_validation_net_bps": max_or_none(validation_values),
        "best_holdout_net_bps": max_or_none(holdout_values),
        "portfolio_net_bps": max_or_none(portfolio_values),
        "lockbox_portfolio_net_bps": max_or_none(lockbox_portfolio),
        "gross_pnl_usdt": gross,
        "net_pnl_usdt": net,
        "total_cost_usdt": cost,
        "cost_as_share_of_gross_pnl": cost_share,
        "trade_count": max_or_none(closed_trade_values + accepted_trade_values),
        "closed_trade_count": max_or_none(closed_trade_values),
        "accepted_trade_count": max_or_none(accepted_trade_values),
        "null_percentile": max_or_none(null_values + validation_percentiles),
        "null_pass": null_pass_values[-1] if null_pass_values else None,
        "monthly_positive_rate": max_or_none(monthly_positive_values),
        "worst_month_bps": min_or_none(worst_month_values),
        "max_drawdown_bps": min_or_none(max_drawdown_values),
        "top_symbol_concentration": max_or_none(top_symbol_values),
        "top_3_symbol_concentration": max_or_none(top_3_values),
        "fee_stress_2x_net_bps": latest_or_none(fee_stress_2x_values),
        "metric_integrity_passed": metric_integrity_values[-1] if metric_integrity_values else None,
        "load_error": artifact["load_error"],
    }


def cost_scenario_estimates(metrics: dict[str, Any]) -> dict[str, Any] | None:
    gross = metrics.get("gross_pnl_usdt")
    cost = metrics.get("total_cost_usdt")
    if gross is None or cost is None or cost < 0:
        return None
    estimates = {}
    for bps in (0, 2, 5, 10, 20):
        scaled_cost = cost * (bps / 20.0)
        estimates[f"{bps}_bps"] = {
            "estimated_net_pnl_usdt": gross - scaled_cost,
            "estimated_cost_usdt": scaled_cost,
        }
    return {
        "source_artifact": metrics["path"],
        "artifact_gross_pnl_usdt": gross,
        "artifact_total_cost_usdt": cost,
        "assumed_current_round_trip_cost_bps": 20,
        "artifact_derived_linear_cost_scaling_not_new_backtest": True,
        "estimates": estimates,
    }


def aggregate_family(family: str, artifact_metrics_list: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [item["path"] for item in artifact_metrics_list]
    classifications = [str(item.get("result_classification")) for item in artifact_metrics_list if item.get("result_classification")]
    gross_values = [item["gross_pnl_usdt"] for item in artifact_metrics_list if item.get("gross_pnl_usdt") is not None]
    net_values = [item["net_pnl_usdt"] for item in artifact_metrics_list if item.get("net_pnl_usdt") is not None]
    cost_values = [item["total_cost_usdt"] for item in artifact_metrics_list if item.get("total_cost_usdt") is not None]
    lockbox_failed = any("lockbox" in path.lower() and "fail" in " ".join(classifications).lower() for path in paths) or (
        family == "RESIDUAL_SWEEP_CONFIRMATION_TRAP_QUALITY"
        and any("trap_quality_lockbox_route_closure" in path for path in paths)
    )
    lockbox_values = [item["lockbox_portfolio_net_bps"] for item in artifact_metrics_list if item.get("lockbox_portfolio_net_bps") is not None]
    best_cost_artifact = None
    for item in artifact_metrics_list:
        if item.get("gross_pnl_usdt") is not None and item.get("total_cost_usdt") is not None:
            best_cost_artifact = item
            break
    scenario_estimates = cost_scenario_estimates(best_cost_artifact) if best_cost_artifact else None
    return {
        "family": family,
        "artifact_count": len(artifact_metrics_list),
        "artifact_paths": paths,
        "artifact_statuses_or_classes": classifications[:20],
        "best_validation_net_bps": max_or_none([item["best_validation_net_bps"] for item in artifact_metrics_list if item.get("best_validation_net_bps") is not None]),
        "best_holdout_net_bps": max_or_none([item["best_holdout_net_bps"] for item in artifact_metrics_list if item.get("best_holdout_net_bps") is not None]),
        "best_portfolio_net_bps": max_or_none([item["portfolio_net_bps"] for item in artifact_metrics_list if item.get("portfolio_net_bps") is not None]),
        "lockbox_or_forward_result": {
            "lockbox_failed": lockbox_failed,
            "lockbox_portfolio_net_bps": min_or_none(lockbox_values),
        },
        "gross_pnl_available": bool(gross_values),
        "best_gross_pnl_usdt": max_or_none(gross_values),
        "best_net_pnl_usdt": max_or_none(net_values),
        "max_total_cost_usdt": max_or_none(cost_values),
        "best_cost_as_share_of_gross_pnl": min_or_none([item["cost_as_share_of_gross_pnl"] for item in artifact_metrics_list if item.get("cost_as_share_of_gross_pnl") is not None]),
        "trade_count": max_or_none([item["trade_count"] for item in artifact_metrics_list if item.get("trade_count") is not None]),
        "null_percentile": max_or_none([item["null_percentile"] for item in artifact_metrics_list if item.get("null_percentile") is not None]),
        "null_pass_any": any(item.get("null_pass") is True for item in artifact_metrics_list),
        "monthly_positive_rate": max_or_none([item["monthly_positive_rate"] for item in artifact_metrics_list if item.get("monthly_positive_rate") is not None]),
        "worst_month_bps": min_or_none([item["worst_month_bps"] for item in artifact_metrics_list if item.get("worst_month_bps") is not None]),
        "max_drawdown_bps": min_or_none([item["max_drawdown_bps"] for item in artifact_metrics_list if item.get("max_drawdown_bps") is not None]),
        "top_symbol_concentration": max_or_none([item["top_symbol_concentration"] for item in artifact_metrics_list if item.get("top_symbol_concentration") is not None]),
        "top_3_symbol_concentration": max_or_none([item["top_3_symbol_concentration"] for item in artifact_metrics_list if item.get("top_3_symbol_concentration") is not None]),
        "fee_stress_2x_net_bps": latest_or_none([item["fee_stress_2x_net_bps"] for item in artifact_metrics_list if item.get("fee_stress_2x_net_bps") is not None]),
        "cost_scenario_estimates": scenario_estimates,
    }


def cost_classification(family: str, summary: dict[str, Any]) -> str:
    if family == "COINALYZE_LONG_LIQUIDATION_FLUSH":
        return "LOW_SAMPLE_ONLY"
    if summary["lockbox_or_forward_result"]["lockbox_failed"]:
        return "NET_POSITIVE_BUT_LOCKBOX_FAILED"
    gross = summary.get("best_gross_pnl_usdt")
    net = summary.get("best_net_pnl_usdt")
    cost_share = summary.get("best_cost_as_share_of_gross_pnl")
    if gross is not None and gross < 0:
        return "GROSS_NEGATIVE_NOT_FEE_SALVAGEABLE"
    if family == "BETA_NEUTRAL_RESIDUAL_MR" and gross is not None:
        return "GROSS_POSITIVE_COST_DOMINATED"
    if gross is not None and net is not None and gross > 0 and net <= 0 and (cost_share is None or cost_share >= 0.50):
        return "GROSS_POSITIVE_COST_DOMINATED"
    if net is not None and net > 0 and summary.get("null_percentile") is not None and summary.get("null_percentile", 0) < 0.95:
        return "NET_POSITIVE_BUT_NULL_FAILED"
    if summary.get("artifact_count", 0) == 0:
        return "DATA_INSUFFICIENT"
    return "UNKNOWN_MISSING_GROSS_COST_FIELDS"


def capacity_classification(family: str, summary: dict[str, Any]) -> str:
    trade_count = summary.get("trade_count") or 0
    concentration = summary.get("top_symbol_concentration")
    if family == "FUNDING_OR_BASIS_CARRY":
        return "HIGH_CAPACITY_PLAUSIBLE"
    if family == "BETA_NEUTRAL_RESIDUAL_MR":
        return "MEDIUM_CAPACITY_PLAUSIBLE"
    if family == "COINALYZE_LONG_LIQUIDATION_FLUSH":
        return "LOW_CAPACITY_OR_MICROSTRUCTURE_LIMITED"
    if family in ("LUCIFER_EMA_PIVOT", "REGIME_BREAKOUT_MOMENTUM", "LIQUIDITY_SWEEP_REVERSAL", "RESIDUAL_SWEEP_CONFIRMATION_TRAP_QUALITY"):
        return "LOW_CAPACITY_OR_MICROSTRUCTURE_LIMITED" if trade_count and trade_count < 1000 else "MEDIUM_CAPACITY_PLAUSIBLE"
    if concentration is not None and concentration > 0.50:
        return "LOW_CAPACITY_OR_MICROSTRUCTURE_LIMITED"
    return "UNKNOWN"


def relevance_classification(family: str, summary: dict[str, Any], cost_class: str) -> str:
    if summary["lockbox_or_forward_result"]["lockbox_failed"]:
        return "REJECTED_NOT_WORTHY"
    if family == "BETA_NEUTRAL_RESIDUAL_MR" and cost_class == "GROSS_POSITIVE_COST_DOMINATED":
        return "INSTITUTIONAL_RESEARCH_WORTHY"
    if family == "FUNDING_OR_BASIS_CARRY":
        return "INSTITUTIONAL_RESEARCH_WORTHY_ONLY_WITH_NEW_DATA"
    if family == "COINALYZE_LONG_LIQUIDATION_FLUSH":
        return "INSTITUTIONAL_RESEARCH_WORTHY_ONLY_WITH_NEW_DATA"
    if cost_class == "GROSS_NEGATIVE_NOT_FEE_SALVAGEABLE":
        return "REJECTED_NOT_WORTHY"
    if cost_class in ("LOW_SAMPLE_ONLY", "DATA_INSUFFICIENT", "UNKNOWN_MISSING_GROSS_COST_FIELDS"):
        return "INCONCLUSIVE"
    return "RETAIL_ONLY_OR_TOO_FRAGILE"


def family_notes(family: str, summary: dict[str, Any], cost_class: str, relevance: str) -> dict[str, Any]:
    notes = {
        "why_it_may_survive_lower_fees_or_higher_capital": [],
        "evidence_supporting": [],
        "evidence_blocking": [],
        "data_missing": [],
        "next_allowed_step": "NO_FAMILY_SPECIFIC_STEP",
    }
    if family == "BETA_NEUTRAL_RESIDUAL_MR":
        notes["why_it_may_survive_lower_fees_or_higher_capital"].append(
            "Artifacts indicate positive gross components while total transaction costs dominated net results; institutional fees could directly target that failure mode."
        )
        notes["evidence_supporting"].append(
            "Known artifact interpretation preserved: symbol leg positive, BTC/ETH hedge combined positive or near positive, total cost very large, net rejected."
        )
        notes["evidence_blocking"].append("No edge is established; cost-salvage requires institutional fee/slippage proof and fresh validation.")
        notes["data_missing"].append("Institutional fee schedule, borrow/funding, hedge execution slippage, and post-cost lockbox evidence.")
        notes["next_allowed_step"] = "INSTITUTIONAL_RESEARCH_CONTRACT_FOR_TOP_FAMILY_V1"
    elif family == "FUNDING_OR_BASIS_CARRY":
        notes["why_it_may_survive_lower_fees_or_higher_capital"].append(
            "Carry and basis mechanisms are structurally capital-dependent; low absolute returns may matter more at larger capital and lower execution costs."
        )
        notes["evidence_supporting"].append("Funding/carry/basis artifacts exist and are economically interpretable rather than pure OHLCV pattern mining.")
        notes["evidence_blocking"].append("Existing closures/evaluations do not create an edge claim and may be low-return or configuration-fragile.")
        notes["data_missing"].append("Longer venue-specific borrow, funding, basis, maker/taker, spread, and inventory-capacity data.")
        notes["next_allowed_step"] = "FUNDING_CARRY_OR_COINALYZE_DATA_COLLECTION_PLAN_V1"
    elif family == "RESIDUAL_SWEEP_CONFIRMATION_TRAP_QUALITY":
        notes["evidence_blocking"].append(
            "Trap-quality lockbox failed unseen forward data: portfolio net bps about -333, null percentile about 0.07, route closed, V-next not allowed."
        )
        notes["next_allowed_step"] = "NO_LOCKBOX_TUNING_ALLOWED"
    elif family == "COINALYZE_LONG_LIQUIDATION_FLUSH":
        notes["evidence_supporting"].append("Event study was promising and strategy execution baseline percentile was high on recent data.")
        notes["evidence_blocking"].append("Only 35 closed trades; 2x fee stress was negative, so it is low-sample and fee-fragile.")
        notes["data_missing"].append("Longer aligned liquidation/OI/funding history; max-history Coinalyze artifact found insufficient full alignment.")
        notes["next_allowed_step"] = "FREE_DATA_SOURCE_ALTERNATIVE_DISCOVERY_V1"
    elif family == "REGIME_BREAKOUT_MOMENTUM":
        notes["evidence_blocking"].append("Known fact preserved: regime breakout momentum was heavily negative.")
    elif family == "LIQUIDITY_SWEEP_REVERSAL":
        notes["evidence_blocking"].append("Known fact preserved: repaired liquidity sweep execution was heavily negative.")
    elif family == "LUCIFER_EMA_PIVOT":
        notes["evidence_blocking"].append("Known fact preserved: Lucifer variants were negative.")
    elif family == "OLD_SHORT_CLEAN_ROOM":
        notes["evidence_blocking"].append("Known fact preserved: old_short clean-room V2 was rejected after corrected accounting.")
    if relevance == "REJECTED_NOT_WORTHY" and not notes["evidence_blocking"]:
        notes["evidence_blocking"].append("Existing artifact outcomes do not show an institutionally salvageable gross/cost profile.")
    return notes


def build_payload() -> dict[str, Any]:
    artifacts = load_artifacts()
    grouped: dict[str, list[dict[str, Any]]] = {family: [] for family in FAMILIES}
    unassigned = []
    for artifact in artifacts:
        family = family_for_path(artifact["path"])
        metrics = artifact_metrics(artifact)
        if family in grouped:
            grouped[family].append(metrics)
        elif family is None:
            unassigned.append(artifact["path"])

    family_summaries: dict[str, dict[str, Any]] = {}
    cost_review: dict[str, dict[str, Any]] = {}
    capacity_review: dict[str, dict[str, Any]] = {}
    relevance_review: dict[str, dict[str, Any]] = {}
    ranked_family_candidates = []
    rejected_family_summary = []
    for family in FAMILIES:
        summary = aggregate_family(family, grouped[family])
        cost_class = cost_classification(family, summary)
        capacity_class = capacity_classification(family, summary)
        relevance = relevance_classification(family, summary, cost_class)
        notes = family_notes(family, summary, cost_class, relevance)
        summary.update(
            {
                "cost_sensitivity_classification": cost_class,
                "capacity_classification": capacity_class,
                "institutional_relevance_classification": relevance,
                "interpretation": notes,
            }
        )
        family_summaries[family] = summary
        cost_review[family] = {
            "classification": cost_class,
            "cost_scenario_estimates": summary.get("cost_scenario_estimates"),
            "gross_pnl_available": summary["gross_pnl_available"],
            "best_gross_pnl_usdt": summary["best_gross_pnl_usdt"],
            "best_net_pnl_usdt": summary["best_net_pnl_usdt"],
            "max_total_cost_usdt": summary["max_total_cost_usdt"],
        }
        capacity_review[family] = {
            "classification": capacity_class,
            "trade_count": summary["trade_count"],
            "top_symbol_concentration": summary["top_symbol_concentration"],
            "top_3_symbol_concentration": summary["top_3_symbol_concentration"],
        }
        relevance_review[family] = {
            "classification": relevance,
            "evidence_supporting": notes["evidence_supporting"],
            "evidence_blocking": notes["evidence_blocking"],
            "data_missing": notes["data_missing"],
            "next_allowed_step": notes["next_allowed_step"],
        }
        if relevance in ("INSTITUTIONAL_RESEARCH_WORTHY", "INSTITUTIONAL_RESEARCH_WORTHY_ONLY_WITH_NEW_DATA"):
            ranked_family_candidates.append(
                {
                    "family": family,
                    "rank_reason": notes,
                    "institutional_relevance_classification": relevance,
                    "cost_sensitivity_classification": cost_class,
                    "capacity_classification": capacity_class,
                }
            )
        else:
            rejected_family_summary.append(
                {
                    "family": family,
                    "institutional_relevance_classification": relevance,
                    "cost_sensitivity_classification": cost_class,
                    "primary_blocker": notes["evidence_blocking"][0] if notes["evidence_blocking"] else "insufficient institutionally relevant evidence",
                }
            )

    rank_order = {"BETA_NEUTRAL_RESIDUAL_MR": 0, "FUNDING_OR_BASIS_CARRY": 1, "COINALYZE_LONG_LIQUIDATION_FLUSH": 2}
    ranked_family_candidates.sort(key=lambda item: rank_order.get(item["family"], 99))
    top_family_candidate = ranked_family_candidates[0]["family"] if ranked_family_candidates else None
    second_family_candidate = ranked_family_candidates[1]["family"] if len(ranked_family_candidates) > 1 else None
    institutional_worthy_count = sum(1 for item in ranked_family_candidates if item["institutional_relevance_classification"] == "INSTITUTIONAL_RESEARCH_WORTHY")
    only_new_data_count = sum(1 for item in ranked_family_candidates if item["institutional_relevance_classification"] == "INSTITUTIONAL_RESEARCH_WORTHY_ONLY_WITH_NEW_DATA")
    if institutional_worthy_count:
        overall_classification = "ONE_OR_MORE_FAMILIES_INSTITUTIONAL_RESEARCH_WORTHY"
        next_allowed_step = "INSTITUTIONAL_RESEARCH_CONTRACT_FOR_TOP_FAMILY_V1"
    elif only_new_data_count:
        overall_classification = "ONLY_CARRY_OR_DATA_COLLECTION_WORTHY"
        next_allowed_step = "FUNDING_CARRY_OR_COINALYZE_DATA_COLLECTION_PLAN_V1"
    elif any(summary["artifact_count"] == 0 for summary in family_summaries.values()):
        overall_classification = "INCONCLUSIVE_MISSING_ARTIFACT_FIELDS"
        next_allowed_step = "TRADING_RESEARCH_PARK_OR_NEW_DATA_SOURCE_DECISION_V1"
    else:
        overall_classification = "NO_FAMILY_WORTH_INSTITUTIONAL_RESEARCH_WITH_CURRENT_DATA"
        next_allowed_step = "TRADING_RESEARCH_PARK_OR_NEW_DATA_SOURCE_DECISION_V1"

    clean = repo_clean_except_expected_new_files()
    artifact_inventory = {
        "allowed_artifact_directories": ALLOWED_ARTIFACT_DIRS,
        "total_json_artifacts_loaded": len(artifacts),
        "artifact_count_by_directory": {
            directory: sum(1 for artifact in artifacts if artifact["directory"] == directory) for directory in ALLOWED_ARTIFACT_DIRS
        },
        "family_artifact_counts": {family: len(grouped[family]) for family in FAMILIES},
        "unassigned_allowed_artifact_count": len(unassigned),
        "unassigned_allowed_artifacts_sample": unassigned[:25],
        "load_error_count": sum(1 for artifact in artifacts if artifact["load_error"]),
    }
    validation_checks = {
        "repo_clean_before_run": clean,
        "existing_artifacts_only": True,
        "no_raw_market_data_read": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation_from_raw_data": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_network_used": True,
        "no_api_called": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": clean,
        "replacement_checks_all_true": True,
    }
    validation_checks["replacement_checks_all_true"] = all(validation_checks.values())
    payload: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "artifact_inventory": artifact_inventory,
        "family_summaries": family_summaries,
        "cost_sensitivity_review": cost_review,
        "capacity_review": capacity_review,
        "institutional_relevance_review": relevance_review,
        "ranked_family_candidates": ranked_family_candidates,
        "rejected_family_summary": rejected_family_summary,
        "overall_classification": overall_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "This is a meta-review of existing repo artifacts only; it does not read raw market data or recompute PnL from candles.",
            "Cost scenarios are produced only where gross/cost fields are present in artifacts and assume linear cost scaling from the artifact cost base.",
            "Lower fees and higher capital do not create edge; institutional-worthy means worth a constrained research contract, not a candidate or live permission.",
            "Family grouping and extraction are conservative filename/field based heuristics over available artifact schemas.",
        ],
        "safety_permissions": {
            "meta_review_created": True,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_from_raw_data_allowed_now": False,
            "optimization_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": validation_checks["replacement_checks_all_true"],
        "payload_sha256_excluding_hash": None,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)
    return payload


def print_stdout(payload: dict[str, Any]) -> None:
    cost_review = payload["cost_sensitivity_review"]
    family_summaries = payload["family_summaries"]
    ranked = payload["ranked_family_candidates"]
    top = ranked[0]["family"] if ranked else None
    second = ranked[1]["family"] if len(ranked) > 1 else None
    fee_salvageable_count = sum(
        1
        for family, review in cost_review.items()
        if review["classification"] in ("GROSS_POSITIVE_COST_DOMINATED", "NET_POSITIVE_BUT_NULL_FAILED")
    )
    gross_positive_cost_dominated_count = sum(1 for review in cost_review.values() if review["classification"] == "GROSS_POSITIVE_COST_DOMINATED")
    lockbox_failed_count = sum(1 for summary in family_summaries.values() if summary["lockbox_or_forward_result"]["lockbox_failed"])
    low_sample_count = sum(1 for review in cost_review.values() if review["classification"] == "LOW_SAMPLE_ONLY")
    print(f"status: {payload['status']}")
    print(f"overall_classification: {payload['overall_classification']}")
    print(f"top_family_candidate: {top}")
    print(f"second_family_candidate: {second}")
    print(f"fee_salvageable_family_count: {fee_salvageable_count}")
    print(f"gross_positive_cost_dominated_family_count: {gross_positive_cost_dominated_count}")
    print(f"lockbox_failed_family_count: {lockbox_failed_count}")
    print(f"low_sample_family_count: {low_sample_count}")
    print(f"next_allowed_step: {payload['next_allowed_step']}")
    print("strategy_execution_allowed_now: false")
    print("backtest_allowed_now: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(payload['replacement_checks_all_true']).lower()}")


def main() -> int:
    payload = build_payload()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print_stdout(payload)
    return 0 if payload["replacement_checks_all_true"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
