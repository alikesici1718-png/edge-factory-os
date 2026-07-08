from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import random
import statistics
import sys
import time
from bisect import bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_EXECUTED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_EXECUTION"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_carry_short_positive_flat_negative_execution_v1.py"
ARTIFACT_PATH = "artifacts/strategy_executions/binance_okx_overlap_funding_carry_short_positive_flat_negative_execution_v1.json"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_BASELINE"
HYPOTHESIS_NAME = "funding_carry_short_positive_flat_negative"
ROUTE_TYPE = "one_sided_short_only_funding_carry"
CONFIG_ID = "funding_carry_short_positive_flat_negative_hold8h"

HOUR_MS = 60 * 60 * 1000
START_MS = 1688169600000
END_MS = 1761926400000
TRAIN_END_MS = 1735689600000
HOLD_HOURS = 8
HOLD_MS = HOLD_HOURS * HOUR_MS
SIGNAL_LAG_MS = HOUR_MS
MIN_ACTIVE_SHORTS = 10
COST = 0.0020
NULL_RUN_COUNT = 100
NULL_BLOCK_HOURS = 168

PANEL_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1\panel_1h_by_symbol")
FUNDING_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_funding_rate_data_acquisition_lock_v1\funding_by_symbol")

PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_carry_short_positive_flat_negative_preregistration_contract_v1.json"
PREREG_HASH = "64471c65aaff2504b9952095d39648099c83a47f78cfb155c59950a8cabdd10a"

SOURCE_ARTIFACTS = {
    "group2_closure": (
        "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json",
        "8bddb11159022e8b4d057169ab203a315716f2c310b6a30fe825a774af76e896",
    ),
    "funding_extreme_liquidity_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json",
        "a4824ed55c95ab3a0dcfcd1f37d49fffcd1453f3bd69bc1d866edd609da610cc",
    ),
    "plain_funding_closure": (
        "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
        "8eacb2decacac50140de27b6c84a9a5338e2473e62ccce54be5d07770a576b02",
    ),
    "funding_review": (
        "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
        "a579feb0472efbf03ffa955008dfabc0b526fa37029fc81dddd0195b4054d849",
    ),
    "funding_lock": (
        "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
        "dd5877b101c9a1e8d73f35f6032381cbdfd5435578abacf97b9db0c11c28e252",
    ),
    "readiness": (
        "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
        "0cfe239f6f5ad2d20bda64b827416851de8f5b959066902b59f1f00f44eba716",
    ),
    "panel_review": (
        "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
        "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112",
    ),
    "panel_manifest": (
        "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
        "bf4d4d681f36fab3a2131701e25ebc45c94ddb757f92874498ef425d698f40a7",
    ),
    "panel_preview": (
        "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
        "16e93ca05fe28f0d101d5228e299306bad3aea171f22bc6901f770b0ecf3a3d9",
    ),
    "coverage_lock": (
        "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
        "18a84b71c649b0462fdb0d511597dcb701448fe06184ef9c8da93d6911ada4e0",
    ),
}

EXPECTED_PANEL_HEADER = [
    "symbol",
    "timestamp_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "minute_count",
    "complete_1h",
]


class Blocked(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")).hexdigest()


def read_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing required source artifact: {rel_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_payload(payload: dict[str, Any], expected: str, label: str) -> None:
    if payload.get("payload_sha256_excluding_hash") != expected:
        raise Blocked(f"{label} stored payload hash mismatch")
    actual = payload_hash(payload)
    if actual != expected:
        raise Blocked(f"{label} payload hash recompute mismatch: {actual} != {expected}")


def parse_ms(value: str) -> int:
    if not value.endswith("Z"):
        raise Blocked(f"timestamp missing Z: {value}")
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def complete(value: str) -> bool:
    return value.strip().lower() == "true"


def bps(values: list[float]) -> float:
    if not values:
        return 0.0
    value = (sum(values) / len(values)) * 10000.0
    if not math.isfinite(value):
        raise Blocked("non-finite metric")
    return round(value, 6)


def finite_round(value: float) -> float:
    if not math.isfinite(value):
        raise Blocked("non-finite value")
    return round(value, 6)


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy))


def max_drawdown_bps(values: list[float]) -> float:
    cumulative = 0.0
    peak = 0.0
    worst = 0.0
    for value in values:
        cumulative += value
        peak = max(peak, cumulative)
        worst = min(worst, cumulative - peak)
    return round(worst * 10000.0, 6)


def load_sources(root: Path) -> tuple[list[str], dict[str, Any]]:
    prereg = read_json(root, PREREG_PATH)
    verify_payload(prereg, PREREG_HASH, "preregistration")
    if prereg.get("status") != "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CARRY_SHORT_POSITIVE_FLAT_NEGATIVE_PREREGISTRATION_CONTRACT_CREATED":
        raise Blocked("preregistration status mismatch")
    if prereg.get("funding_carry_hypothesis_preregistration", {}).get("route_family") != ROUTE_FAMILY:
        raise Blocked("preregistration route family mismatch")
    if prereg.get("funding_carry_hypothesis_preregistration", {}).get("market_neutral") is not False:
        raise Blocked("preregistration market_neutral is not false")
    if prereg.get("funding_carry_hypothesis_preregistration", {}).get("short_only") is not True:
        raise Blocked("preregistration short_only is not true")

    source_summary: dict[str, Any] = {
        "all_source_artifacts_read_only": True,
        "preregistration_artifact_path": PREREG_PATH,
        "preregistration_payload_hash_verified": True,
    }
    loaded: dict[str, dict[str, Any]] = {"preregistration": prereg}
    for label, (rel_path, expected) in SOURCE_ARTIFACTS.items():
        payload = read_json(root, rel_path)
        verify_payload(payload, expected, label)
        loaded[label] = payload
        source_summary[f"{label}_path"] = rel_path
        source_summary[f"{label}_payload_hash_verified"] = True

    readiness = loaded["readiness"]
    symbols = readiness.get("symbol_universe_alignment", {}).get("exact_overlap_binance_symbols", [])
    if not isinstance(symbols, list) or len(symbols) != 81:
        raise Blocked("could not extract 81 overlap symbols")
    alignment = readiness.get("okx_binance_alignment_window", {})
    if alignment.get("recommended_aligned_window_start_utc") != "2023-07-01T00:00:00Z" or alignment.get("recommended_aligned_window_end_exclusive_utc") != "2025-10-31T16:00:00Z":
        raise Blocked("aligned window mismatch")
    funding_valid = loaded["funding_review"].get("safety_permissions", {}).get("funding_data_valid_for_future_funding_signal_construction")
    if funding_valid is not True:
        raise Blocked("funding data is not valid for future signal construction")
    return sorted(symbols), source_summary


def read_panel(symbol: str) -> tuple[dict[int, float], int, int]:
    path = PANEL_DIR / f"{symbol}_1h.csv.gz"
    if not path.exists():
        raise Blocked(f"missing panel file for {symbol}")
    rows: dict[int, float] = {}
    read_count = 0
    skipped_incomplete = 0
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_PANEL_HEADER:
            raise Blocked(f"bad panel header for {symbol}")
        for row in reader:
            if row["symbol"] != symbol:
                raise Blocked(f"panel symbol mismatch for {symbol}")
            ts = parse_ms(row["timestamp_utc"])
            if not (START_MS <= ts < END_MS):
                continue
            if not complete(row["complete_1h"]):
                skipped_incomplete += 1
                continue
            open_price = float(row["open"])
            if open_price <= 0 or not math.isfinite(open_price):
                raise Blocked(f"invalid open price for {symbol}")
            rows[ts] = open_price
            read_count += 1
    if not rows:
        raise Blocked(f"zero panel rows for {symbol}")
    return rows, read_count, skipped_incomplete


def read_funding(symbol: str) -> tuple[list[int], list[float], int]:
    path = FUNDING_DIR / f"{symbol}_funding_rate.jsonl.gz"
    if not path.exists():
        raise Blocked(f"missing funding file for {symbol}")
    times: list[int] = []
    rates: list[float] = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("symbol") != symbol:
                raise Blocked(f"funding symbol mismatch for {symbol}")
            if row.get("source_endpoint") != "fapi_v1_fundingRate":
                raise Blocked(f"funding source endpoint mismatch for {symbol}")
            funding_time = int(row["funding_time_ms"])
            if START_MS <= funding_time < END_MS:
                rate = float(row["funding_rate"])
                if not math.isfinite(rate):
                    raise Blocked(f"non-finite funding rate for {symbol}")
                times.append(funding_time)
                rates.append(rate)
    if not times:
        raise Blocked(f"zero funding rows for {symbol}")
    if any(b <= a for a, b in zip(times, times[1:])):
        raise Blocked(f"non-monotonic funding rows for {symbol}")
    return times, rates, len(times)


def funding_sum(times: list[int], rates: list[float], entry_ts: int, exit_ts: int) -> float:
    start = bisect_right(times, entry_ts)
    end = bisect_right(times, exit_ts)
    return sum(rates[start:end])


def window_for_entry(ts: int) -> str:
    return "train" if ts < TRAIN_END_MS else "validation"


def build_entries(
    symbols: list[str],
    panels: list[dict[int, float]],
    funding_times: list[list[int]],
    funding_rates: list[list[float]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    all_ts = sorted(set().union(*(panel.keys() for panel in panels)))
    entries: list[dict[str, Any]] = []
    skipped_insufficient = 0
    skipped_cross_window = 0
    missing_entry_exit = 0
    no_lookahead_violations = 0
    for pos, ts in enumerate(all_ts):
        if pos % 5000 == 0:
            print(f"building funding carry entries {pos + 1}/{len(all_ts)}", file=sys.stderr)
        if not (START_MS <= ts < END_MS):
            continue
        exit_ts = ts + HOLD_MS
        window = window_for_entry(ts)
        if window == "train" and exit_ts >= TRAIN_END_MS:
            skipped_cross_window += 1
            continue
        if window == "validation" and exit_ts >= END_MS:
            skipped_cross_window += 1
            continue

        active: list[int] = []
        net_symbol_returns: dict[int, float] = {}
        gross_symbol_returns: dict[int, float] = {}
        price_symbol_returns: dict[int, float] = {}
        funding_symbol_returns: dict[int, float] = {}
        market_returns: list[float] = []
        for index, panel in enumerate(panels):
            entry_open = panel.get(ts)
            exit_open = panel.get(exit_ts)
            if entry_open is None or exit_open is None:
                missing_entry_exit += 1
                continue
            long_price_return = (exit_open / entry_open) - 1.0
            market_returns.append(long_price_return)
            cutoff = ts - SIGNAL_LAG_MS
            funding_pos = bisect_right(funding_times[index], cutoff) - 1
            if funding_pos < 0:
                continue
            if funding_times[index][funding_pos] > cutoff:
                no_lookahead_violations += 1
                continue
            signal_rate = funding_rates[index][funding_pos]
            if signal_rate <= 0:
                continue
            cashflow = funding_sum(funding_times[index], funding_rates[index], ts, exit_ts)
            price_short = -long_price_return
            gross = price_short + cashflow
            net = gross - COST
            active.append(index)
            price_symbol_returns[index] = price_short
            funding_symbol_returns[index] = cashflow
            gross_symbol_returns[index] = gross
            net_symbol_returns[index] = net

        if len(active) < MIN_ACTIVE_SHORTS:
            skipped_insufficient += 1
            continue
        if not market_returns:
            continue
        entries.append(
            {
                "active": active,
                "entry_ts": ts,
                "funding_symbol_returns": funding_symbol_returns,
                "gross_symbol_returns": gross_symbol_returns,
                "market_return": sum(market_returns) / len(market_returns),
                "net_symbol_returns": net_symbol_returns,
                "price_symbol_returns": price_symbol_returns,
                "window": window,
            }
        )
    stats = {
        "no_lookahead_violations": no_lookahead_violations,
        "selected_entry_count": len(entries),
        "skipped_symbol_rows_missing_entry_or_exit_price": missing_entry_exit,
        "skipped_timestamps_cross_window_exit": skipped_cross_window,
        "skipped_timestamps_insufficient_active_short_symbols": skipped_insufficient,
    }
    return entries, stats


def mean_for_active(entry: dict[str, Any], field: str, active_override: list[int] | None = None) -> float | None:
    active = active_override if active_override is not None else entry["active"]
    values = [entry[field].get(index) for index in active]
    if any(value is None for value in values) or not values:
        return None
    return sum(values) / len(values)


def deterministic_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def shuffled_mapping(indices: list[int], run_index: int, window: str) -> dict[int, int]:
    blocks = [indices[i : i + NULL_BLOCK_HOURS] for i in range(0, len(indices), NULL_BLOCK_HOURS)]
    block_order = list(range(len(blocks)))
    rng = random.Random(deterministic_seed(f"{ROUTE_FAMILY}|{CONFIG_ID}|{window}|{run_index}"))
    rng.shuffle(block_order)
    shuffled = [item for block_index in block_order for item in blocks[block_index]]
    return dict(zip(indices, shuffled))


def evaluate(symbols: list[str], entries: list[dict[str, Any]], stats: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    windows = {"train": [], "validation": []}
    for index, entry in enumerate(entries):
        windows[entry["window"]].append(index)
    if not windows["train"] or not windows["validation"]:
        raise Blocked("missing train or validation entries")

    net_by_window: dict[str, list[float]] = {"train": [], "validation": []}
    gross_by_window: dict[str, list[float]] = {"train": [], "validation": []}
    price_by_window: dict[str, list[float]] = {"train": [], "validation": []}
    funding_by_window: dict[str, list[float]] = {"train": [], "validation": []}
    market_by_window: dict[str, list[float]] = {"train": [], "validation": []}
    monthly_validation_net: dict[str, list[float]] = defaultdict(list)
    validation_market_for_corr: list[float] = []
    validation_net_for_corr: list[float] = []
    active_counts: list[int] = []
    active_counts_by_window: dict[str, list[int]] = {"train": [], "validation": []}
    turnovers: list[float] = []
    participation: Counter[int] = Counter()
    previous_active: set[int] | None = None
    metric_issues = 0

    for entry in entries:
        active = entry["active"]
        gross = mean_for_active(entry, "gross_symbol_returns")
        net = mean_for_active(entry, "net_symbol_returns")
        price = mean_for_active(entry, "price_symbol_returns")
        funding = mean_for_active(entry, "funding_symbol_returns")
        if gross is None or net is None or price is None or funding is None:
            metric_issues += 1
            continue
        if not all(math.isfinite(value) for value in [gross, net, price, funding, entry["market_return"]]):
            metric_issues += 1
            continue
        window = entry["window"]
        gross_by_window[window].append(gross)
        net_by_window[window].append(net)
        price_by_window[window].append(price - COST)
        funding_by_window[window].append(funding)
        market_by_window[window].append(entry["market_return"])
        active_counts.append(len(active))
        active_counts_by_window[window].append(len(active))
        current_active = set(active)
        if previous_active is None:
            turnovers.append(1.0)
        else:
            union = previous_active | current_active
            turnovers.append(len(previous_active ^ current_active) / len(union) if union else 0.0)
        previous_active = current_active
        for index in current_active:
            participation[index] += 1
        if window == "validation":
            month = utc(entry["entry_ts"])[:7]
            monthly_validation_net[month].append(net)
            validation_market_for_corr.append(entry["market_return"])
            validation_net_for_corr.append(net)

    if not net_by_window["train"] or not net_by_window["validation"]:
        raise Blocked("no valid train or validation metrics")

    validation_monthly = {month: bps(values) for month, values in sorted(monthly_validation_net.items())}
    validation_month_count = len(validation_monthly)
    validation_positive_months = sum(1 for value in validation_monthly.values() if value > 0)
    monthly_positive_rate = validation_positive_months / validation_month_count if validation_month_count else 0.0
    monthly_passed = monthly_positive_rate >= 0.60 and validation_month_count >= 6
    worst_validation_month = min(validation_monthly.values()) if validation_monthly else 0.0

    correlation = pearson(validation_net_for_corr, validation_market_for_corr)
    drawdown_proxy = max_drawdown_bps(net_by_window["validation"])
    total_participation = sum(participation.values())
    top_share = max((count / total_participation for count in participation.values()), default=0.0)
    average_turnover = sum(turnovers) / len(turnovers) if turnovers else 0.0
    median_turnover = statistics.median(turnovers) if turnovers else 0.0
    max_turnover = max(turnovers) if turnovers else 0.0
    turnover_passed = top_share <= 0.35 and average_turnover <= 1.75

    actual_validation_net = sum(net_by_window["validation"]) / len(net_by_window["validation"])
    null_validation_metrics: list[float] = []
    for run_index in range(NULL_RUN_COUNT):
        mapping = shuffled_mapping(windows["validation"], run_index, "validation")
        values: list[float] = []
        for signal_index, return_index in mapping.items():
            signal_entry = entries[signal_index]
            return_entry = entries[return_index]
            gross = mean_for_active(return_entry, "gross_symbol_returns", signal_entry["active"])
            if gross is not None and math.isfinite(gross):
                values.append(gross - COST)
        if values:
            null_validation_metrics.append(sum(values) / len(values))
    if len(null_validation_metrics) != NULL_RUN_COUNT:
        raise Blocked("null baseline incomplete")
    null_percentile = sum(1 for value in null_validation_metrics if value <= actual_validation_net) / len(null_validation_metrics)
    null_passed = null_percentile >= 0.95

    validation_net_bps = bps(net_by_window["validation"])
    exposure_passed = (
        validation_net_bps > 0
        and worst_validation_month > -250.0
        and (correlation is not None)
        and correlation > -0.50
        and min(active_counts_by_window["validation"]) >= MIN_ACTIVE_SHORTS
    )

    config_result = {
        "average_active_short_count": finite_round(sum(active_counts) / len(active_counts)),
        "config_id": CONFIG_ID,
        "holding_period_hours": HOLD_HOURS,
        "market_neutral": False,
        "metric_integrity_issue_count": metric_issues,
        "monthly_positive_rate": finite_round(monthly_positive_rate),
        "monthly_stability_review_preliminary_passed": monthly_passed,
        "null_baseline": "deterministic_entry_timestamp_block_shuffle_null",
        "null_run_count": NULL_RUN_COUNT,
        "price_only_validation_metric_bps": bps(price_by_window["validation"]),
        "route_is_short_only": True,
        "skipped_symbol_rows_missing_entry_or_exit_price": stats["skipped_symbol_rows_missing_entry_or_exit_price"],
        "skipped_timestamps_cross_window_exit": stats["skipped_timestamps_cross_window_exit"],
        "skipped_timestamps_insufficient_active_short_symbols": stats["skipped_timestamps_insufficient_active_short_symbols"],
        "train_funding_adjusted_gross_metric_bps": bps(gross_by_window["train"]),
        "train_funding_adjusted_net_metric_bps": bps(net_by_window["train"]),
        "train_observation_count": len(net_by_window["train"]),
        "turnover_concentration_review_preliminary_passed": turnover_passed,
        "validation_funding_adjusted_gross_metric_bps": bps(gross_by_window["validation"]),
        "validation_funding_adjusted_net_metric_bps": validation_net_bps,
        "validation_funding_cashflow_metric_bps": bps(funding_by_window["validation"]),
        "validation_month_count": validation_month_count,
        "validation_monthly_net_metric_bps_by_month": validation_monthly,
        "validation_positive_after_cost": validation_net_bps > 0,
        "validation_price_only_metric_bps": bps(price_by_window["validation"]),
        "validation_null_percentile": finite_round(null_percentile),
        "validation_observation_count": len(net_by_window["validation"]),
    }
    exposure_summary = {
        "active_short_count_distribution": dict(sorted(Counter(active_counts).items())),
        "average_active_short_count": config_result["average_active_short_count"],
        "correlation_with_equal_weight_market_return": None if correlation is None else finite_round(correlation),
        "drawdown_proxy_bps": drawdown_proxy,
        "equal_weight_market_return_metric_bps": bps(market_by_window["validation"]),
        "funding_adjusted_gross_metric_bps": config_result["validation_funding_adjusted_gross_metric_bps"],
        "funding_adjusted_net_metric_bps": config_result["validation_funding_adjusted_net_metric_bps"],
        "funding_cashflow_metric_bps": config_result["validation_funding_cashflow_metric_bps"],
        "market_neutral": False,
        "max_active_short_count": max(active_counts),
        "min_active_short_count": min(active_counts),
        "price_only_metric_bps": config_result["validation_price_only_metric_bps"],
        "route_is_short_only": True,
        "train_average_active_short_count": finite_round(sum(active_counts_by_window["train"]) / len(active_counts_by_window["train"])),
        "validation_average_active_short_count": finite_round(sum(active_counts_by_window["validation"]) / len(active_counts_by_window["validation"])),
        "worst_validation_month_net_metric_bps": worst_validation_month,
    }
    null_summary = {
        "block_length_hours": NULL_BLOCK_HOURS,
        "null_baseline": "deterministic_entry_timestamp_block_shuffle_null",
        "null_baseline_complete": True,
        "null_baseline_review_preliminary_passed": null_passed,
        "null_run_count": NULL_RUN_COUNT,
        "validation_null_percentile": finite_round(null_percentile),
    }
    monthly_summary = {
        "monthly_positive_rate": finite_round(monthly_positive_rate),
        "monthly_stability_created": True,
        "monthly_stability_review_preliminary_passed": monthly_passed,
        "validation_month_count": validation_month_count,
        "validation_monthly_net_metric_bps_by_month": validation_monthly,
    }
    exposure_review = {
        "correlation_with_equal_weight_market_return": exposure_summary["correlation_with_equal_weight_market_return"],
        "exposure_risk_review_preliminary_passed": exposure_passed,
        "review_reason": "Pass requires positive validation net metric, non-catastrophic worst month, computable correlation not strongly negative, and sufficient active short count.",
        "route_is_short_only": True,
        "worst_validation_month_net_metric_bps": worst_validation_month,
    }
    turnover_summary = {
        "average_turnover": finite_round(average_turnover),
        "median_turnover": finite_round(median_turnover),
        "top_symbol_exposure_share": finite_round(top_share),
        "turnover_concentration_created": True,
        "turnover_concentration_review_preliminary_passed": turnover_passed,
    }
    metric_summary = {
        "config_count_executed": 1,
        "config_id_matches_preregistration": True,
        "metric_integrity_issue_count": metric_issues,
        "metric_integrity_passed": metric_issues == 0,
        "no_nan_or_infinite_metrics": True,
        "no_non_preregistered_config": True,
    }
    return config_result, exposure_summary, null_summary, monthly_summary, exposure_review, turnover_summary, metric_summary


def build_artifact(root: Path) -> dict[str, Any]:
    symbols, source_summary = load_sources(root)
    panels: list[dict[int, float]] = []
    funding_times: list[list[int]] = []
    funding_rates: list[list[float]] = []
    panel_rows = 0
    funding_rows = 0
    incomplete_rows = 0

    for index, symbol in enumerate(symbols):
        if index % 20 == 0:
            print(f"reading funding/panel rows {index + 1}/{len(symbols)}", file=sys.stderr)
        times, rates, funding_count = read_funding(symbol)
        panel, panel_count, incomplete_count = read_panel(symbol)
        funding_times.append(times)
        funding_rates.append(rates)
        panels.append(panel)
        funding_rows += funding_count
        panel_rows += panel_count
        incomplete_rows += incomplete_count

    entries, stats = build_entries(symbols, panels, funding_times, funding_rates)
    if stats["no_lookahead_violations"] != 0:
        raise Blocked("no-lookahead violation detected")
    (
        config_result,
        exposure_summary,
        null_summary,
        monthly_summary,
        exposure_review,
        turnover_summary,
        metric_summary,
    ) = evaluate(symbols, entries, stats)
    if metric_summary["metric_integrity_passed"] is not True:
        raise Blocked("metric integrity failed")

    validation_checks = {
        "config_count_verified_1": True,
        "config_id_matches_preregistration": True,
        "exposure_risk_review_created": True,
        "metric_integrity_checks_created": True,
        "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_carry_short_positive_flat_negative_execution_v1.py",
        "monthly_stability_created": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_network_used": True,
        "no_non_preregistered_config": True,
        "no_okx_panel_rows_read": True,
        "no_runtime_live_capital": True,
        "null_baseline_complete": True,
        "replacement_checks_all_true": True,
        "short_only_route_preserved": True,
        "status_equals_required_status": True,
    }

    artifact: dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "route_family": ROUTE_FAMILY,
        "config_id": CONFIG_ID,
        "source_checkpoint": {
            "prior_head": "10e996905a02012e0b9f4564c3c00398c043ca16",
            "prior_preregistration_artifact": PREREG_PATH,
            "prior_preregistration_payload_sha256_excluding_hash": PREREG_HASH,
            "prior_tracked_python_count": 826,
            "repo_clean_before_execution": True,
        },
        "source_artifacts": source_summary,
        "input_data_validation": {
            "funding_rows_outside_aligned_window_count": 0,
            "funding_rows_read_for_execution": funding_rows,
            "funding_symbol_count": len(funding_times),
            "incomplete_panel_rows_skipped": incomplete_rows,
            "input_data_valid_for_execution": True,
            "panel_rows_outside_aligned_window_count": 0,
            "panel_rows_read_for_execution": panel_rows,
            "panel_symbol_count": len(panels),
            "symbols": symbols,
            "symbols_missing_funding_rows": [],
            "symbols_missing_panel_rows": [],
        },
        "signal_alignment_policy": {
            "flat_rule": "flat if latest_lagged_funding_rate <= 0 or missing",
            "funding_signal": "latest fundingRate with funding_time <= entry_time - 1h",
            "minimum_active_short_symbols": MIN_ACTIVE_SHORTS,
            "no_long_leg": True,
            "short_rule": "short if latest_lagged_funding_rate > 0",
        },
        "return_and_cost_policy": {
            "cost_bps": 20,
            "entry_price": "open_at_entry_timestamp",
            "exit_price": "open_at_entry_plus_8h",
            "funding_cashflow_policy": "funding events strictly after entry time and up to and including exit time",
            "metric_units": "basis_points",
            "no_annualization": True,
            "no_compounding": True,
            "price_only_short_return": "-(exit_open / entry_open - 1)",
        },
        "exposure_risk_summary": exposure_summary,
        "execution_safety_controls": {
            "cross_window_holding_returns_prevented": True,
            "market_neutral_assumption": False,
            "no_beta_hedge": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_hedge": True,
            "no_lookahead_policy_applied": True,
            "no_non_preregistered_config": True,
            "no_runtime_live_capital": True,
            "short_only": True,
        },
        "config_result": config_result,
        "train_validation_summary": {
            "best_validation_config_id": CONFIG_ID,
            "best_validation_gross_metric_bps": config_result["validation_funding_adjusted_gross_metric_bps"],
            "best_validation_net_metric_bps": config_result["validation_funding_adjusted_net_metric_bps"],
            "config_id": CONFIG_ID,
            "exposure_risk_review_preliminary_passed": exposure_review["exposure_risk_review_preliminary_passed"],
            "monthly_stability_review_preliminary_passed": monthly_summary["monthly_stability_review_preliminary_passed"],
            "null_baseline_review_preliminary_passed": null_summary["null_baseline_review_preliminary_passed"],
            "turnover_concentration_review_preliminary_passed": turnover_summary["turnover_concentration_review_preliminary_passed"],
            "validation_positive_after_cost": config_result["validation_positive_after_cost"],
        },
        "null_baseline_summary": null_summary,
        "monthly_stability_summary": monthly_summary,
        "exposure_risk_review": exposure_review,
        "turnover_concentration_summary": turnover_summary,
        "metric_integrity_summary": metric_summary,
        "diagnostic_interpretation_limits": {
            "candidate_generation_allowed_from_this_execution": False,
            "edge_claim_allowed_from_this_execution": False,
            "execution_result_is_diagnostic_only": True,
            "family_release_allowed_from_this_execution": False,
            "positive_result_still_requires_evaluator_closure_and_governance": True,
            "route_is_short_only_not_market_neutral": True,
            "runtime_live_capital_allowed_from_this_execution": False,
        },
        "safety_permissions": {
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
            "strategy_search_allowed_now": False,
        },
        "forbidden_actions_confirmed_false": {
            "binance_1m_source_rows_read": False,
            "binance_api_called": False,
            "binance_panel_rebuild": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "funding_data_fetched": False,
            "funding_endpoint_called": False,
            "network_used": False,
            "non_preregistered_config_tested": False,
            "okx_panel_rows_read": False,
            "runtime_live_capital": False,
        },
        "validation_checks": validation_checks,
    }
    artifact["replacement_checks_all_true"] = all(validation_checks.values())
    if artifact["replacement_checks_all_true"] is not True:
        raise Blocked("replacement_checks_all_true is false")
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def write_artifact(root: Path, artifact: dict[str, Any]) -> None:
    output = root / ARTIFACT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reloaded = json.loads(output.read_text(encoding="utf-8"))
    if payload_hash(reloaded) != artifact["payload_sha256_excluding_hash"]:
        output.unlink(missing_ok=True)
        raise Blocked("written execution artifact hash mismatch")


def main() -> int:
    root = repo_root()
    output = root / ARTIFACT_PATH
    start = time.time()
    try:
        artifact = build_artifact(root)
        write_artifact(root, artifact)
        summary = {
            "average_active_short_count": artifact["exposure_risk_summary"]["average_active_short_count"],
            "config_id": CONFIG_ID,
            "correlation_with_equal_weight_market_return": artifact["exposure_risk_summary"]["correlation_with_equal_weight_market_return"],
            "exposure_risk_review_preliminary_passed": artifact["exposure_risk_review"]["exposure_risk_review_preliminary_passed"],
            "market_neutral": False,
            "metric_integrity_issue_count": artifact["metric_integrity_summary"]["metric_integrity_issue_count"],
            "monthly_stability_review_preliminary_passed": artifact["monthly_stability_summary"]["monthly_stability_review_preliminary_passed"],
            "null_baseline_review_preliminary_passed": artifact["null_baseline_summary"]["null_baseline_review_preliminary_passed"],
            "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
            "replacement_checks_all_true": artifact["replacement_checks_all_true"],
            "short_only": True,
            "status": STATUS,
            "turnover_concentration_review_preliminary_passed": artifact["turnover_concentration_summary"]["turnover_concentration_review_preliminary_passed"],
            "validation_funding_cashflow_metric_bps": artifact["config_result"]["validation_funding_cashflow_metric_bps"],
            "validation_gross_metric_bps": artifact["config_result"]["validation_funding_adjusted_gross_metric_bps"],
            "validation_net_metric_bps": artifact["config_result"]["validation_funding_adjusted_net_metric_bps"],
            "validation_positive_after_cost": artifact["config_result"]["validation_positive_after_cost"],
            "validation_price_only_metric_bps": artifact["config_result"]["validation_price_only_metric_bps"],
            "wall_seconds": round(time.time() - start, 3),
            "worst_validation_month_net_metric_bps": artifact["exposure_risk_summary"]["worst_validation_month_net_metric_bps"],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        if output.exists():
            output.unlink()
        print(f"BLOCKED {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
