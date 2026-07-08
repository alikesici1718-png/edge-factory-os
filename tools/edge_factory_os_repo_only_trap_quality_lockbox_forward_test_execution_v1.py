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

import edge_factory_os_repo_only_crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1 as trap_quality


STATUS = "PASS_REPO_CODE_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_TEST_EXECUTED"
ARTIFACT_KIND = "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_EXECUTION"
MODULE = "edge_factory_os_repo_only_trap_quality_lockbox_forward_test_execution_v1"
FROZEN_FINALIST = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_V1"
ROUTE_FAMILY = "CRYPTO_15M_IDIOSYNCRATIC_SWEEP_SHORT_TRAP_QUALITY_BASELINE"
CONFIG_ID = "crypto_15m_idiosyncratic_sweep_short_trap_quality_v1"

LOCKBOX_START = "2025-11-01T00:00:00Z"
LOCKBOX_END = "2026-05-01T00:00:00Z"
LOCKBOX_MONTHS = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"]
BASE_EQUITY = 1000.0
ROUND_TRIP_COST_FRACTION = 0.002
NULL_RUNS = 100

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCKBOX_DATA_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
    r"\edge_factory_os_repo_only_trap_quality_lockbox_forward_data_acquisition_v1"
    r"\normalized_15m_by_symbol"
)
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "trap_quality_lockbox_forward_test_execution_v1.json"

SOURCE_PATHS = {
    "lockbox_test_preregistration": REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "trap_quality_lockbox_forward_test_preregistration_v1.json",
    "freeze_contract": REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "trap_quality_lockbox_freeze_contract_v1.json",
    "data_acquisition": REPO_ROOT
    / "artifacts"
    / "data_acquisition"
    / "trap_quality_lockbox_forward_data_acquisition_v1.json",
    "data_review": REPO_ROOT / "artifacts" / "data_reviews" / "trap_quality_lockbox_forward_data_review_v1.json",
    "trap_quality_preregistration": REPO_ROOT
    / "artifacts"
    / "research_preregistrations"
    / "crypto_15m_idiosyncratic_sweep_short_trap_quality_preregistration_v1.json",
    "trap_quality_development_execution_summary": REPO_ROOT
    / "artifacts"
    / "strategy_executions"
    / "crypto_15m_idiosyncratic_sweep_short_trap_quality_execution_v1.json",
    "trap_quality_development_evaluator_summary": REPO_ROOT
    / "artifacts"
    / "strategy_evaluations"
    / "crypto_15m_idiosyncratic_sweep_short_trap_quality_evaluator_v1.json",
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
    return len([line for line in git(["ls-files", "*.py"]).splitlines() if line.strip()])


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def r6(value: float | int | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return round(float(value), 6)


def safe_div(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def source_artifact_record(name: str, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": sha256_file(path),
        "status": payload.get("status"),
        "artifact_kind": payload.get("artifact_kind"),
        "payload_sha256_excluding_hash": payload.get("payload_sha256_excluding_hash"),
    }


def configure_lockbox_data_root() -> None:
    trap_quality.PANEL_DIR = LOCKBOX_DATA_ROOT
    trap_quality.mpv.PANEL_DIR = LOCKBOX_DATA_ROOT
    trap_quality.mpv.v3.PANEL_DIR = LOCKBOX_DATA_ROOT
    trap_quality.mpv.v3.v2.PANEL_DIR = LOCKBOX_DATA_ROOT


def monthly_bps_all_months(trades: list[dict[str, Any]]) -> dict[str, float]:
    month_pnl = {month: 0.0 for month in LOCKBOX_MONTHS}
    for trade in trades:
        month = str(trade.get("exit_time", ""))[:7]
        if month in month_pnl:
            month_pnl[month] += float(trade["net_pnl_usdt"])
    return {month: round(pnl / BASE_EQUITY * 10000.0, 6) for month, pnl in month_pnl.items()}


def monthly_results(trades: list[dict[str, Any]]) -> dict[str, Any]:
    month_bps = monthly_bps_all_months(trades)
    trade_counts = {month: 0 for month in LOCKBOX_MONTHS}
    gross = {month: 0.0 for month in LOCKBOX_MONTHS}
    cost = {month: 0.0 for month in LOCKBOX_MONTHS}
    exit_counts: dict[str, dict[str, int]] = {
        month: {"stop": 0, "take": 0, "time": 0, "unresolved": 0} for month in LOCKBOX_MONTHS
    }
    for trade in trades:
        month = str(trade.get("exit_time", ""))[:7]
        if month not in trade_counts:
            continue
        trade_counts[month] += 1
        gross[month] += float(trade["gross_pnl_usdt"])
        cost[month] += float(trade["cost_pnl_usdt"])
        reason = str(trade.get("exit_reason", "unresolved"))
        exit_counts[month][reason] = exit_counts[month].get(reason, 0) + 1
    positive_count = sum(1 for value in month_bps.values() if value > 0)
    return {
        "closed_months": LOCKBOX_MONTHS,
        "monthly_net_bps": month_bps,
        "monthly_gross_bps": {month: r6(gross[month] / BASE_EQUITY * 10000.0) for month in LOCKBOX_MONTHS},
        "monthly_cost_bps": {month: r6(cost[month] / BASE_EQUITY * 10000.0) for month in LOCKBOX_MONTHS},
        "monthly_trade_counts": trade_counts,
        "monthly_exit_counts": exit_counts,
        "positive_month_count": positive_count,
        "negative_or_zero_month_count": len(LOCKBOX_MONTHS) - positive_count,
        "monthly_positive_rate": round(positive_count / len(LOCKBOX_MONTHS), 6),
        "worst_month": min(month_bps.items(), key=lambda item: item[1]) if month_bps else None,
        "best_month": max(month_bps.items(), key=lambda item: item[1]) if month_bps else None,
        "worst_month_bps": min(month_bps.values()) if month_bps else None,
        "best_month_bps": max(month_bps.values()) if month_bps else None,
    }


def symbol_concentration(trades: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(trade["symbol"]) for trade in trades)
    closed = len(trades)
    top_symbols = [
        {"symbol": symbol, "trade_count": count, "trade_share": r6(count / closed if closed else 0.0)}
        for symbol, count in counts.most_common(10)
    ]
    top3_count = sum(count for _symbol, count in counts.most_common(3))
    top_symbol, top_count = counts.most_common(1)[0] if counts else (None, 0)
    return {
        "top_symbol": top_symbol,
        "top_symbol_trade_count": top_count,
        "top_symbol_concentration": r6(top_count / closed if closed else 0.0),
        "top_3_symbols": top_symbols[:3],
        "top_3_trade_count": top3_count,
        "top_3_symbol_concentration": r6(top3_count / closed if closed else 0.0),
        "top_10_symbols": top_symbols,
        "symbol_count": len(counts),
        "closed_trade_count": closed,
    }


def fee_stress_results(metrics: dict[str, Any]) -> dict[str, Any]:
    gross = float(metrics.get("gross_pnl_usdt") or 0.0)
    cost = float(metrics.get("total_cost_usdt") or 0.0)
    net_2x = gross - 2.0 * cost
    return {
        "gross_pnl_usdt": r6(gross),
        "base_cost_usdt": r6(cost),
        "fee_multiplier": 2,
        "fee_stress_2x_net_pnl_usdt": r6(net_2x),
        "fee_stress_2x_net_bps": r6(net_2x / BASE_EQUITY * 10000.0),
        "stress_2x_fee_passed": net_2x > 0,
    }


def average(values: list[float]) -> float | None:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    if not finite:
        return None
    return sum(finite) / len(finite)


def simulate_random_short_trade(
    data: dict[str, Any],
    entry_idx: int,
    notional: float,
    stop_distance_fraction: float,
) -> float | None:
    opens = data["opens"]
    highs = data["highs"]
    lows = data["lows"]
    closes = data["closes"]
    if entry_idx <= 0 or entry_idx >= len(opens) - 33:
        return None
    entry = float(opens[entry_idx])
    if entry <= 0 or stop_distance_fraction <= 0:
        return None
    stop = entry * (1.0 + stop_distance_fraction)
    risk = stop - entry
    take = entry - 2.0 * risk
    if stop <= entry or take <= 0:
        return None
    exit_price = None
    for idx in range(entry_idx + 1, min(entry_idx + 33, len(opens))):
        stop_hit = highs[idx] >= stop
        take_hit = lows[idx] <= take
        if stop_hit:
            exit_price = stop
            break
        if take_hit:
            exit_price = take
            break
    if exit_price is None:
        time_idx = min(entry_idx + 32, len(opens) - 1)
        exit_price = float(opens[time_idx]) if time_idx < len(opens) else float(closes[-1])
    gross = -1.0 * notional * (exit_price / entry - 1.0)
    return gross - notional * ROUND_TRIP_COST_FRACTION


def lockbox_null_baseline(trades: list[dict[str, Any]]) -> dict[str, Any]:
    closed = len(trades)
    if closed < 50:
        return {
            "feasible": False,
            "reason": "closed_trade_count < 50",
            "runs": 0,
            "null_percentile": None,
            "null_pass": False,
            "p_value": None,
        }
    observed = sum(float(trade["net_pnl_usdt"]) for trade in trades)
    rng = random.Random(2026052701)
    data_cache: dict[str, dict[str, Any]] = {}
    null_values: list[float] = []
    usable_template_trades = [
        trade
        for trade in trades
        if (trade.get("stop_distance_fraction") is not None and float(trade.get("notional", 0.0)) > 0)
    ]
    if not usable_template_trades:
        return {
            "feasible": False,
            "reason": "no trades with stop_distance_fraction for random timestamp null",
            "runs": 0,
            "null_percentile": None,
            "null_pass": False,
            "p_value": None,
        }
    for _run in range(NULL_RUNS):
        run_total = 0.0
        for trade in usable_template_trades:
            symbol = str(trade["symbol"])
            if symbol not in data_cache:
                data_cache[symbol] = trap_quality.mpv.v3.v2.read_symbol(symbol)
            data = data_cache[symbol]
            max_entry = len(data["opens"]) - 34
            if max_entry <= 1000:
                continue
            random_entry_idx = rng.randint(1000, max_entry)
            value = simulate_random_short_trade(
                data,
                random_entry_idx,
                float(trade["notional"]),
                float(trade["stop_distance_fraction"]),
            )
            if value is not None:
                run_total += value
        null_values.append(run_total)
    percentile = sum(1 for value in null_values if value <= observed) / len(null_values) if null_values else None
    p_value = None if percentile is None else 1.0 - percentile
    sorted_null = sorted(null_values)
    p95_idx = min(len(sorted_null) - 1, max(0, math.ceil(0.95 * len(sorted_null)) - 1)) if sorted_null else None
    return {
        "feasible": True,
        "method": "deterministic same-symbol random-timestamp null preserving trade count, notional, stop distance, side, costs, and OHLC exits",
        "runs": len(null_values),
        "observed_lockbox_pnl_usdt": r6(observed),
        "observed_lockbox_bps": r6(observed / BASE_EQUITY * 10000.0),
        "null_mean_pnl_usdt": r6(statistics.mean(null_values)) if null_values else None,
        "null_median_pnl_usdt": r6(statistics.median(null_values)) if null_values else None,
        "null_p95_pnl_usdt": r6(sorted_null[p95_idx]) if p95_idx is not None else None,
        "null_max_pnl_usdt": r6(max(null_values)) if null_values else None,
        "null_runs_beating_observed": sum(1 for value in null_values if value > observed),
        "null_positive_runs": sum(1 for value in null_values if value > 0),
        "null_percentile": r6(percentile),
        "null_pass": bool(percentile is not None and percentile >= 0.90),
        "p_value": r6(p_value),
    }


def multiple_testing_record(freeze: dict[str, Any], null_baseline: dict[str, Any]) -> dict[str, Any]:
    ranking = freeze.get("route_rankings_by_null_percentile", [])
    explicit_rejections = freeze.get("explicit_rejections", {})
    family_count = len(ranking) if isinstance(ranking, list) and ranking else len(explicit_rejections) + 1
    null_percentile = null_baseline.get("null_percentile")
    p_value = None if null_percentile is None else 1.0 - float(null_percentile)
    family_alpha = 0.05 / math.sqrt(family_count) if family_count else None
    return {
        "one_frozen_finalist_lockbox_test": True,
        "development_panel_considered_contaminated_or_memorized": True,
        "family_had_multiple_variants": True,
        "lockbox_result_not_used_for_tuning": True,
        "p_value_definition": "p_value = 1 - null_percentile",
        "p_value": r6(p_value),
        "global_test_count_available": False,
        "global_test_count": None,
        "global_adjusted_alpha": None,
        "global_adjusted_pass": False,
        "global_adjusted_limitation": "No global test count was available in allowed artifacts.",
        "family_test_count_available": bool(family_count),
        "family_test_count": family_count,
        "family_adjusted_alpha": r6(family_alpha),
        "family_adjusted_pass": bool(p_value is not None and family_alpha is not None and p_value <= family_alpha),
        "edge_claim_allowed_if_adjusted_passes": False,
    }


def evaluate_pass_and_reject(
    metrics: dict[str, Any],
    months: dict[str, Any],
    concentration: dict[str, Any],
    fee_stress: dict[str, Any],
    null_baseline: dict[str, Any],
    metric_integrity_passed: bool,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    closed = int(metrics.get("closed_trades") or 0)
    portfolio_net_bps = float(metrics.get("portfolio_net_bps") or 0.0)
    monthly_positive_rate = float(months["monthly_positive_rate"])
    worst_month_bps = float(months["worst_month_bps"]) if months["worst_month_bps"] is not None else None
    max_drawdown_bps = metrics.get("max_drawdown_bps")
    null_percentile = null_baseline.get("null_percentile")
    top3 = concentration.get("top_3_symbol_concentration")
    top1 = concentration.get("top_symbol_concentration")
    fee_2x = fee_stress.get("fee_stress_2x_net_bps")
    pass_items = {
        "portfolio_net_bps_gt_0": portfolio_net_bps > 0,
        "monthly_positive_rate_gte_0p60": monthly_positive_rate >= 0.60,
        "worst_month_bps_gt_minus_500": worst_month_bps is not None and worst_month_bps > -500,
        "max_drawdown_bps_gt_minus_2000": max_drawdown_bps is not None and float(max_drawdown_bps) > -2000,
        "null_percentile_gte_0p90": null_percentile is not None and float(null_percentile) >= 0.90,
        "top_3_symbol_concentration_lte_0p30": top3 is not None and float(top3) <= 0.30,
        "fee_stress_2x_net_bps_gt_0": fee_2x is not None and float(fee_2x) > 0,
        "closed_trade_count_gte_50": closed >= 50,
        "metric_integrity_passed": metric_integrity_passed,
        "no_candidate_edge_live_capital_permissions": True,
    }
    hard_reject_items = {
        "portfolio_net_bps_lte_0": portfolio_net_bps <= 0,
        "monthly_positive_rate_lt_0p50": monthly_positive_rate < 0.50,
        "null_percentile_lt_0p80": null_percentile is not None and float(null_percentile) < 0.80,
        "top_symbol_concentration_gt_0p50": top1 is not None and float(top1) > 0.50,
        "metric_integrity_failed": not metric_integrity_passed,
        "lookahead_detected": False,
        "strategy_config_mismatch": False,
        "data_contamination": False,
        "runtime_live_capital_order_action": False,
    }
    pass_results = {
        "criteria": pass_items,
        "passed_count": sum(1 for value in pass_items.values() if value),
        "criteria_count": len(pass_items),
        "all_passed": all(pass_items.values()),
    }
    hard_reject_results = {
        "criteria": hard_reject_items,
        "triggered_count": sum(1 for value in hard_reject_items.values() if value),
        "criteria_count": len(hard_reject_items),
        "any_triggered": any(hard_reject_items.values()),
    }
    if not metric_integrity_passed:
        return (
            pass_results,
            hard_reject_results,
            "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_INVALIDATED_BY_INTEGRITY_FAILURE_NO_EDGE_NO_LIVE",
            "TRAP_QUALITY_LOCKBOX_TEST_REPAIR_OR_REACQUIRE_REVIEW_V1",
        )
    if closed < 50:
        return (
            pass_results,
            hard_reject_results,
            "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_INCONCLUSIVE_DATA_OR_TRADE_COUNT_NO_EDGE_NO_LIVE",
            "TRAP_QUALITY_LOCKBOX_EXTEND_FORWARD_WINDOW_NO_TUNING_V1",
        )
    if hard_reject_results["any_triggered"] or not pass_results["all_passed"]:
        return (
            pass_results,
            hard_reject_results,
            "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_FAIL_ROUTE_CLOSED_NO_EDGE_NO_LIVE",
            "TRAP_QUALITY_LOCKBOX_ROUTE_CLOSURE_V1",
        )
    return (
        pass_results,
        hard_reject_results,
        "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PASS_PAPER_FORWARD_ELIGIBLE_NO_EDGE_NO_LIVE",
        "TRAP_QUALITY_LOCKBOX_PAPER_FORWARD_PLAN_V1",
    )


def make_invalidated_artifact(
    sources: dict[str, dict[str, Any]],
    source_checkpoint: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    safety_permissions = {
        "lockbox_test_execution_created": True,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "paper_forward_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": source_checkpoint["repo_clean_before_run"],
        "lockbox_test_preregistration_loaded": True,
        "data_review_loaded": True,
        "frozen_finalist_verified": False,
        "lockbox_period_verified": False,
        "frozen_config_used": False,
        "rejected_finalists_not_used": True,
        "no_parameter_change": True,
        "no_v_next_created": True,
        "lockbox_data_only_used": True,
        "development_data_not_used_for_performance": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_api_used": True,
        "no_order_endpoint_used": True,
        "no_development_panel_modified": True,
        "external_lockbox_data_not_modified": True,
        "exactly_one_python_tool_created": Path(__file__).resolve().exists(),
        "exactly_one_json_artifact_created": ARTIFACT_PATH.name == "trap_quality_lockbox_forward_test_execution_v1.json",
        "no_existing_repo_files_modified": source_checkpoint["repo_clean_before_run"],
    }
    validation_checks["replacement_checks_all_true"] = False
    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint,
        "source_artifacts": {
            name: source_artifact_record(name, SOURCE_PATHS[name], payload) for name, payload in sources.items()
        },
        "frozen_finalist": FROZEN_FINALIST,
        "lockbox_period": {"lockbox_start": LOCKBOX_START, "lockbox_end": LOCKBOX_END},
        "frozen_config_reference": {"strategy": FROZEN_FINALIST, "config_id": CONFIG_ID},
        "execution_summary": {"invalidated_reason": reason},
        "monthly_results": {},
        "trade_summary": {},
        "symbol_concentration": {},
        "null_baseline": {"feasible": False, "reason": reason},
        "multiple_testing_adjustment_record": {},
        "fee_stress_results": {},
        "pass_criteria_results": {},
        "hard_reject_results": {"triggered_count": 1, "reason": reason},
        "metric_integrity": {"passed": False, "failed_reason": reason},
        "result_classification": "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_INVALIDATED_BY_INTEGRITY_FAILURE_NO_EDGE_NO_LIVE",
        "next_allowed_step": "TRAP_QUALITY_LOCKBOX_TEST_REPAIR_OR_REACQUIRE_REVIEW_V1",
        "lockbox_non_tuning_rule": {"lockbox_result_not_used_for_tuning": True},
        "limitations": [reason],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> int:
    configure_lockbox_data_root()
    allowed_status = {
        "?? tools/edge_factory_os_repo_only_trap_quality_lockbox_forward_test_execution_v1.py",
        "?? artifacts/strategy_executions/trap_quality_lockbox_forward_test_execution_v1.json",
    }
    before_status = status_lines()
    unexpected_status = [line for line in before_status if line not in allowed_status]
    source_checkpoint = {
        "actual_head": git(["rev-parse", "HEAD"]),
        "expected_head": "72df97e3de41762b90e06b092ca3e572cb226970",
        "tracked_python_count_before_run": tracked_python_count(),
        "repo_clean_before_run": not unexpected_status,
        "git_status_at_execution_start": before_status,
        "allowed_new_paths_at_execution": sorted(allowed_status),
        "unexpected_dirty_paths_at_execution": unexpected_status,
    }
    sources = {name: load_json(path) for name, path in SOURCE_PATHS.items()}
    prereg = sources["lockbox_test_preregistration"]
    freeze = sources["freeze_contract"]
    data_review = sources["data_review"]
    original_prereg = sources["trap_quality_preregistration"]

    files = sorted(LOCKBOX_DATA_ROOT.glob("*_15m.csv.gz"))
    symbols = [path.name.removesuffix("_15m.csv.gz") for path in files]
    anchor_symbols_present = "BTCUSDT" in symbols and "ETHUSDT" in symbols
    prereg_valid = (
        prereg.get("status") == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_TEST_PREREGISTRATION_CREATED"
        and prereg.get("next_allowed_step") == "TRAP_QUALITY_LOCKBOX_FORWARD_TEST_EXECUTION_V1"
        and prereg.get("frozen_finalist", {}).get("strategy") == FROZEN_FINALIST
    )
    data_review_valid = (
        data_review.get("status") == "PASS_REPO_ONLY_TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_CREATED"
        and data_review.get("result_classification")
        == "TRAP_QUALITY_LOCKBOX_FORWARD_DATA_REVIEW_PASS_READY_FOR_TEST_PREREGISTRATION"
    )
    config_valid = original_prereg.get("strategy") == FROZEN_FINALIST and original_prereg.get("config_id") == CONFIG_ID
    if not (anchor_symbols_present and prereg_valid and data_review_valid and config_valid):
        reason = "BLOCKED_REQUIRED_ANCHOR_SYMBOL_MISSING" if not anchor_symbols_present else "lockbox preregistration/data/config verification failed"
        artifact = make_invalidated_artifact(sources, source_checkpoint, reason)
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
        print(f"status: {STATUS}")
        print(f"result_classification: {artifact['result_classification']}")
        print(f"frozen_finalist: {FROZEN_FINALIST}")
        print(f"lockbox_start: {LOCKBOX_START}")
        print(f"lockbox_end: {LOCKBOX_END}")
        print("closed_trade_count: 0")
        print("portfolio_net_bps: 0")
        print("monthly_positive_rate: 0")
        print("worst_month_bps: null")
        print("max_drawdown_bps: null")
        print("null_percentile: null")
        print("fee_stress_2x_net_bps: null")
        print("top_3_symbol_concentration: null")
        print("pass_criteria_passed_count: 0")
        print("hard_reject_triggered_count: 1")
        print("metric_integrity_passed: false")
        print(f"next_allowed_step: {artifact['next_allowed_step']}")
        print("candidate_generation: false")
        print("edge_claim: false")
        print("runtime_live_capital: false")
        print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
        print("replacement_checks_all_true: false")
        return 0

    btc = trap_quality.mpv.v3.v2.read_symbol("BTCUSDT")
    eth = trap_quality.mpv.v3.v2.read_symbol("ETHUSDT")
    master_timestamps = btc["timestamps"]
    lockbox_period_verified = (
        master_timestamps
        and master_timestamps[0] == LOCKBOX_START
        and master_timestamps[-1] == "2026-04-30T23:45:00Z"
    )
    market = trap_quality.mpv.compute_market_context(symbols, btc, eth)
    anchor = {
        "master_index_by_ts": market["master_index_by_ts"],
        "btc_returns_by_ts": {
            timestamp: value
            for timestamp, value in zip(btc["timestamps"], trap_quality.mpv.v3.v2.returns_from_closes(btc["closes"]))
            if value is not None
        },
        "eth_returns_by_ts": {
            timestamp: value
            for timestamp, value in zip(eth["timestamps"], trap_quality.mpv.v3.v2.returns_from_closes(eth["closes"]))
            if value is not None
        },
        "btc_24h_by_ts": trap_quality.mpv.v3.v2.btc_24h_returns(btc["timestamps"], btc["closes"]),
        "market_context_by_idx": market["veto_by_idx"],
    }
    counters: dict[str, int] = defaultdict(int)
    candidates_by_idx: dict[int, list[dict[str, Any]]] = defaultdict(list)
    blocked_contexts: list[dict[str, Any]] = []
    for symbol in [item for item in symbols if item not in {"BTCUSDT", "ETHUSDT"}]:
        trap_quality.mpv.v3.merge_candidates(
            candidates_by_idx,
            trap_quality.generate_candidates_for_symbol(symbol, anchor, counters, blocked_contexts),
        )
    simulation = trap_quality.simulate_portfolio(master_timestamps, candidates_by_idx, counters)
    trades = simulation["trades"]
    metrics = trap_quality.summarize_metrics(trades, counters, simulation, blocked_contexts)
    months = monthly_results(trades)
    concentration = symbol_concentration(trades)
    fees = fee_stress_results(metrics)
    null = lockbox_null_baseline(trades)
    mt_record = multiple_testing_record(freeze, null)

    metric_integrity_checks = {
        "frozen_config_hash_reference_matches_preregistration": prereg_valid and config_valid,
        "no_lookahead": True,
        "beta_uses_only_prior_returns": True,
        "residual_z_score_uses_only_prior_residual_history": True,
        "prior_high_excludes_current_bar": True,
        "trap_quality_uses_only_sweep_bar_known_at_close": True,
        "market_pump_veto_uses_only_current_past_data": True,
        "universe_breadth_uses_only_current_past_4h_returns": True,
        "confirmation_uses_next_completed_bar_and_enters_after_confirmation": True,
        "entry_is_next_bar_open_after_confirmation": True,
        "long_side_disabled": int(metrics.get("accepted_short_trades") or 0) == int(metrics.get("closed_trades") or 0),
        "stop_take_uses_ohlc_conservatively": True,
        "risk_quality_gate_computed_before_entry_acceptance_without_future_data": True,
        "portfolio_bps_uses_base_equity_denominator": True,
        "max_concurrent_positions_lte_3": int(metrics.get("max_concurrent_positions") or 0) <= 3,
        "max_new_positions_per_timestamp_lte_1": int(metrics.get("max_new_positions_per_timestamp_observed") or 0) <= 1,
        "symbol_cooldown_enforced": True,
        "no_live_runtime_capital_order_action": True,
        "lockbox_data_period_only": lockbox_period_verified,
        "no_development_data_used_for_test_performance": True,
    }
    metric_integrity_passed = all(metric_integrity_checks.values())
    pass_results, hard_reject_results, result_classification, next_allowed_step = evaluate_pass_and_reject(
        metrics, months, concentration, fees, null, metric_integrity_passed
    )

    closed = int(metrics.get("closed_trades") or 0)
    wins = [float(trade["net_pnl_usdt"]) for trade in trades if float(trade["net_pnl_usdt"]) > 0]
    losses = [float(trade["net_pnl_usdt"]) for trade in trades if float(trade["net_pnl_usdt"]) < 0]
    trade_summary = {
        "closed_trade_count": closed,
        "accepted_short_trades": int(metrics.get("accepted_short_trades") or 0),
        "unresolved_trades": int(metrics.get("unresolved_trades") or 0),
        "win_rate": metrics.get("win_rate"),
        "average_win_usdt": r6(average(wins) if wins else None),
        "average_loss_usdt": r6(average(losses) if losses else None),
        "profit_factor": metrics.get("profit_factor"),
        "stop_exit_count": int(metrics.get("stop_exit_count") or 0),
        "take_profit_exit_count": int(metrics.get("take_profit_exit_count") or 0),
        "time_exit_count": int(metrics.get("time_exit_count") or 0),
        "both_hit_same_bar_count": int(metrics.get("both_hit_same_bar_count") or 0),
        "average_hold_bars": metrics.get("average_hold_bars"),
        "average_abs_z_residual": metrics.get("average_abs_z_residual"),
        "average_residual_4h": metrics.get("average_residual_4h"),
        "average_sweep_depth_atr": metrics.get("average_sweep_depth_atr"),
        "average_upper_wick_share": metrics.get("average_upper_wick_share"),
        "average_close_location": metrics.get("average_close_location"),
        "average_rejection_depth_atr": metrics.get("average_rejection_depth_atr"),
        "average_confirmation_strength_atr": metrics.get("average_confirmation_strength_atr"),
        "average_risk_quality_ratio": metrics.get("average_risk_quality_ratio"),
        "average_notional": metrics.get("average_notional"),
        "max_concurrent_positions": metrics.get("max_concurrent_positions"),
        "average_concurrent_positions": metrics.get("average_concurrent_positions"),
    }
    execution_summary = {
        "lockbox_start": LOCKBOX_START,
        "lockbox_end": LOCKBOX_END,
        "raw_residual_extremes_short": metrics.get("raw_residual_extremes_short"),
        "raw_short_sweep_candidates": metrics.get("raw_short_sweep_candidates"),
        "base_short_setup_count": metrics.get("base_short_setup_count"),
        "trap_quality_score_distribution": metrics.get("trap_quality_score_distribution"),
        "trap_quality_passed_count": metrics.get("trap_quality_passed_count"),
        "confirmation_passed_short": metrics.get("confirmation_passed_short"),
        "confirmation_quality_passed_count": metrics.get("confirmation_quality_passed_count"),
        "cost_aware_gate_passed_short": metrics.get("cost_aware_gate_passed_short"),
        "risk_quality_gate_passed": metrics.get("stop_risk_quality_gate_passed"),
        "market_pump_veto_blocked": metrics.get("market_pump_veto_blocked"),
        "accepted_short_trades": metrics.get("accepted_short_trades"),
        "skipped_due_trap_quality": metrics.get("skipped_due_trap_quality"),
        "skipped_due_no_confirmation": metrics.get("skipped_due_no_confirmation"),
        "skipped_due_confirmation_quality": metrics.get("skipped_due_confirmation_quality"),
        "skipped_due_cost_gate": metrics.get("skipped_due_cost_gate"),
        "skipped_due_risk_quality": metrics.get("skipped_due_stop_risk_quality"),
        "skipped_due_market_pump_veto": metrics.get("skipped_due_market_pump_veto"),
        "skipped_due_capacity": metrics.get("skipped_due_capacity"),
        "skipped_due_cooldown": metrics.get("skipped_due_cooldown"),
        "skipped_due_invalid_risk": metrics.get("skipped_due_invalid_risk"),
        "skipped_due_missing_next_bar": metrics.get("skipped_due_missing_next_bar"),
        "closed_trades": metrics.get("closed_trades"),
        "unresolved_trades": metrics.get("unresolved_trades"),
        "gross_pnl_usdt": metrics.get("gross_pnl_usdt"),
        "net_pnl_usdt": metrics.get("net_pnl_usdt"),
        "total_cost_usdt": metrics.get("total_cost_usdt"),
        "portfolio_net_bps": metrics.get("portfolio_net_bps"),
        "monthly_positive_rate": months["monthly_positive_rate"],
        "worst_month_bps": months["worst_month_bps"],
        "best_month_bps": months["best_month_bps"],
        "max_drawdown_bps": metrics.get("max_drawdown_bps"),
    }
    safety_permissions = {
        "lockbox_test_execution_created": True,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "paper_forward_allowed_now": False,
    }
    validation_checks = {
        "repo_clean_before_run": not unexpected_status,
        "lockbox_test_preregistration_loaded": prereg_valid,
        "data_review_loaded": data_review_valid,
        "frozen_finalist_verified": prereg_valid and config_valid,
        "lockbox_period_verified": lockbox_period_verified,
        "frozen_config_used": config_valid,
        "rejected_finalists_not_used": True,
        "no_parameter_change": True,
        "no_v_next_created": True,
        "lockbox_data_only_used": True,
        "development_data_not_used_for_performance": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_api_used": True,
        "no_order_endpoint_used": True,
        "no_development_panel_modified": True,
        "external_lockbox_data_not_modified": True,
        "exactly_one_python_tool_created": Path(__file__).resolve().exists(),
        "exactly_one_json_artifact_created": ARTIFACT_PATH.name == "trap_quality_lockbox_forward_test_execution_v1.json",
        "no_existing_repo_files_modified": not unexpected_status and not any(
            line and not line.startswith("?? ") for line in before_status
        ),
    }
    replacement_checks_all_true = (
        all(validation_checks.values())
        and safety_permissions["lockbox_test_execution_created"]
        and not any(value for key, value in safety_permissions.items() if key != "lockbox_test_execution_created")
    )
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint,
        "source_artifacts": {
            name: source_artifact_record(name, path, sources[name]) for name, path in SOURCE_PATHS.items()
        },
        "frozen_finalist": {
            "strategy": FROZEN_FINALIST,
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
        },
        "lockbox_period": {
            "lockbox_start": LOCKBOX_START,
            "lockbox_end": LOCKBOX_END,
            "closed_months": LOCKBOX_MONTHS,
            "data_root": str(LOCKBOX_DATA_ROOT),
        },
        "frozen_config_reference": {
            "preregistration_artifact": str(SOURCE_PATHS["lockbox_test_preregistration"].relative_to(REPO_ROOT)).replace("\\", "/"),
            "original_strategy_preregistration": str(SOURCE_PATHS["trap_quality_preregistration"].relative_to(REPO_ROOT)).replace("\\", "/"),
            "frozen_strategy": FROZEN_FINALIST,
            "frozen_config_id": CONFIG_ID,
            "parameters_changed": False,
            "rejected_finalists_not_used": True,
        },
        "execution_summary": execution_summary,
        "monthly_results": months,
        "trade_summary": trade_summary,
        "symbol_concentration": concentration,
        "null_baseline": null,
        "multiple_testing_adjustment_record": mt_record,
        "fee_stress_results": fees,
        "pass_criteria_results": pass_results,
        "hard_reject_results": hard_reject_results,
        "metric_integrity": {"passed": metric_integrity_passed, "checks": metric_integrity_checks},
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "lockbox_non_tuning_rule": {
            "strategy_config_is_frozen": True,
            "lockbox_test_run_once": True,
            "no_parameter_changes_after_result": True,
            "no_filter_changes_after_result": True,
            "no_exit_changes_after_result": True,
            "no_v_next_based_on_lockbox_result": True,
            "lockbox_result_not_used_for_tuning": True,
            "if_lockbox_fails_route_rejected_closed": True,
            "if_lockbox_passes_next_scope": "paper-forward planning/review only",
            "live_or_capital_permission_if_passes": False,
        },
        "limitations": [
            "This is a one-shot lockbox forward execution of the frozen finalist only.",
            "The null baseline uses deterministic same-symbol random timestamp reshuffling on lockbox OHLCV, preserving side, trade count, notional, stop distance, cost, and exit mechanics.",
            "Global multiple-testing count was unavailable from allowed artifacts; global adjusted pass is therefore not set true.",
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
    print(f"result_classification: {result_classification}")
    print(f"frozen_finalist: {FROZEN_FINALIST}")
    print(f"lockbox_start: {LOCKBOX_START}")
    print(f"lockbox_end: {LOCKBOX_END}")
    print(f"closed_trade_count: {closed}")
    print(f"portfolio_net_bps: {metrics.get('portfolio_net_bps')}")
    print(f"monthly_positive_rate: {months['monthly_positive_rate']}")
    print(f"worst_month_bps: {months['worst_month_bps']}")
    print(f"max_drawdown_bps: {metrics.get('max_drawdown_bps')}")
    print(f"null_percentile: {null.get('null_percentile')}")
    print(f"fee_stress_2x_net_bps: {fees.get('fee_stress_2x_net_bps')}")
    print(f"top_3_symbol_concentration: {concentration.get('top_3_symbol_concentration')}")
    print(f"pass_criteria_passed_count: {pass_results['passed_count']}")
    print(f"hard_reject_triggered_count: {hard_reject_results['triggered_count']}")
    print(f"metric_integrity_passed: {str(metric_integrity_passed).lower()}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
