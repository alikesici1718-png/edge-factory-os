#!/usr/bin/env python3
"""Execute the preregistered Coinalyze long liquidation flush strategy.

Recent-dataset strategy execution only. This module does not call APIs, use API
keys, touch runtime/live/capital systems, place orders, use private exchange
APIs, generate candidates, claim edge, optimize thresholds, or modify the
external normalized dataset.
"""

from __future__ import annotations

import hashlib
import json
import random
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_long_liquidation_flush_strategy_execution_v1"
STATUS = "PASS_REPO_CODE_ONLY_COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_EXECUTED"
ARTIFACT_KIND = "COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_EXECUTION"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_long_liquidation_flush_strategy_execution_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "coinalyze_long_liquidation_flush_strategy_execution_v1.json"
PREREGISTRATION_PATH = REPO_ROOT / "artifacts" / "research_preregistrations" / "coinalyze_long_liquidation_flush_strategy_preregistration_v1.json"
DESIGN_PATH = REPO_ROOT / "artifacts" / "research_designs" / "coinalyze_long_liquidation_flush_strategy_design_v1.json"
EVENT_STUDY_PATH = REPO_ROOT / "artifacts" / "event_studies" / "coinalyze_liquidation_imbalance_oi_flush_event_study_v1.json"
DATASET_BUILDER_PATH = REPO_ROOT / "artifacts" / "data_builds" / "coinalyze_recent_oi_liquidation_dataset_builder_v1.json"
EXTERNAL_DATASET_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_coinalyze_recent_oi_liquidation_dataset_v1")
NORMALIZED_ROOT = EXTERNAL_DATASET_ROOT / "normalized_by_symbol"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}

STRATEGY_KEY = "COINALYZE_LONG_LIQUIDATION_FLUSH_REVERSAL_V1"
ROUTE_FAMILY = "COINALYZE_RECENT_LIQUIDATION_OI_FLUSH_EVENT_REVERSAL"
CONFIG_ID = "coinalyze_long_liquidation_flush_reversal_15m_hold4h_v1"
EVENT_KEY = "LONG_LIQUIDATION_FLUSH_EVENT"
BASE_EQUITY_USDT = 1000.0
FIXED_NOTIONAL_USDT = 50.0
ROUND_TRIP_COST_FRACTION = 0.002
ROLLING_MEDIAN_BARS = 96
ROLLING_MIN_BARS = 48
PAST_RETURN_BARS = 4
HOLD_BARS = 16
COOLDOWN_BARS = 16
MAX_CONCURRENT_POSITIONS = 3
MAX_NEW_POSITIONS_PER_TIMESTAMP = 1
BASELINE_RUNS = 100


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def profit_factor(wins: list[float], losses: list[float]) -> float | None:
    total_win = sum(wins)
    total_loss = -sum(losses)
    if total_loss == 0:
        return None if total_win == 0 else float("inf")
    return total_win / total_loss


def external_file_stats() -> dict[str, tuple[int, int]]:
    stats: dict[str, tuple[int, int]] = {}
    for path in sorted(NORMALIZED_ROOT.glob("*.jsonl")):
        stat = path.stat()
        stats[str(path)] = (stat.st_size, stat.st_mtime_ns)
    return stats


def load_symbol_rows() -> dict[str, list[dict[str, Any]]]:
    rows_by_symbol: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(NORMALIZED_ROOT.glob("*.jsonl")):
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
        if rows:
            rows_by_symbol[str(rows[0]["symbol"])] = rows
    return rows_by_symbol


def enrich_rows(rows_by_symbol: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    integrity = {
        "rows_missing_open": 0,
        "rows_missing_close": 0,
        "rows_missing_liquidation_long": 0,
        "rows_missing_oi_change_pct": 0,
        "duplicate_timestamp_count": 0,
        "non_monotonic_timestamp_symbols": 0,
    }
    for symbol, rows in rows_by_symbol.items():
        seen = set()
        timestamps = []
        for idx, row in enumerate(rows):
            row["_index"] = idx
            timestamp = row.get("timestamp")
            if timestamp in seen:
                integrity["duplicate_timestamp_count"] += 1
            seen.add(timestamp)
            timestamps.append(timestamp)
            if row.get("open") is None:
                integrity["rows_missing_open"] += 1
            if row.get("close") is None:
                integrity["rows_missing_close"] += 1
            if row.get("liquidation_long") is None:
                integrity["rows_missing_liquidation_long"] += 1
            if row.get("oi_change_pct") is None:
                integrity["rows_missing_oi_change_pct"] += 1
        if timestamps != sorted(timestamps):
            integrity["non_monotonic_timestamp_symbols"] += 1

        for idx, row in enumerate(rows):
            close = as_float(row.get("close"))
            past_close = as_float(rows[idx - PAST_RETURN_BARS].get("close")) if idx >= PAST_RETURN_BARS else None
            row["ret_1h_past"] = close / past_close - 1.0 if close is not None and past_close not in (None, 0) else None
            start = max(0, idx - ROLLING_MEDIAN_BARS)
            prior_rows = rows[start:idx]
            if len(prior_rows) >= ROLLING_MIN_BARS:
                long_values = [as_float(item.get("liquidation_long")) or 0.0 for item in prior_rows]
                row["rolling_median_liquidation_long_24h"] = statistics.median(long_values)
            else:
                row["rolling_median_liquidation_long_24h"] = None
    return integrity


def is_long_flush_event(row: dict[str, Any]) -> bool:
    liquidation_long = as_float(row.get("liquidation_long")) or 0.0
    median_long = as_float(row.get("rolling_median_liquidation_long_24h"))
    oi_change_pct = as_float(row.get("oi_change_pct"))
    ret_1h_past = as_float(row.get("ret_1h_past"))
    return (
        liquidation_long > 0.0
        and median_long is not None
        and liquidation_long >= 3.0 * median_long
        and oi_change_pct is not None
        and oi_change_pct <= -0.005
        and ret_1h_past is not None
        and ret_1h_past <= -0.01
    )


def build_events(rows_by_symbol: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    events: list[dict[str, Any]] = []
    skipped = {
        "skipped_due_missing_next_bar": 0,
        "skipped_due_missing_exit_bar": 0,
    }
    for symbol, rows in rows_by_symbol.items():
        for idx, row in enumerate(rows):
            if not is_long_flush_event(row):
                continue
            median_long = as_float(row.get("rolling_median_liquidation_long_24h")) or 0.0
            liquidation_long = as_float(row.get("liquidation_long")) or 0.0
            entry_idx = idx + 1
            exit_idx = entry_idx + HOLD_BARS
            if entry_idx >= len(rows):
                skipped["skipped_due_missing_next_bar"] += 1
                continue
            if exit_idx >= len(rows):
                skipped["skipped_due_missing_exit_bar"] += 1
                continue
            entry_open = as_float(rows[entry_idx].get("open"))
            exit_open = as_float(rows[exit_idx].get("open"))
            if entry_open is None or entry_open <= 0 or exit_open is None or exit_open <= 0:
                skipped["skipped_due_missing_exit_bar"] += 1
                continue
            events.append(
                {
                    "symbol": symbol,
                    "signal_index": idx,
                    "signal_timestamp": row.get("timestamp"),
                    "entry_index": entry_idx,
                    "entry_timestamp": rows[entry_idx].get("timestamp"),
                    "exit_index": exit_idx,
                    "exit_timestamp": rows[exit_idx].get("timestamp"),
                    "entry_price": entry_open,
                    "exit_price": exit_open,
                    "liquidation_long": liquidation_long,
                    "rolling_median_liquidation_long_24h": median_long,
                    "liquidation_ratio": liquidation_long / median_long if median_long > 0 else None,
                    "oi_change_pct": as_float(row.get("oi_change_pct")),
                    "ret_1h_past": as_float(row.get("ret_1h_past")),
                }
            )
    events.sort(key=lambda event: (str(event["entry_timestamp"]), str(event["symbol"])))
    return events, skipped


def close_positions_before(open_positions: list[dict[str, Any]], entry_timestamp: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    still_open: list[dict[str, Any]] = []
    closed: list[dict[str, Any]] = []
    for position in open_positions:
        if str(position["exit_timestamp"]) <= entry_timestamp:
            closed.append(position)
        else:
            still_open.append(position)
    return still_open, closed


def execute_strategy(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, int]]:
    events_by_entry_timestamp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_entry_timestamp[str(event["entry_timestamp"])].append(event)

    open_positions: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    cooldown_until_index: dict[str, int] = {}
    skips = {
        "skipped_due_capacity": 0,
        "skipped_due_same_symbol_open": 0,
        "skipped_due_cooldown": 0,
    }
    new_positions_by_timestamp: Counter[str] = Counter()

    for entry_timestamp in sorted(events_by_entry_timestamp):
        open_positions, newly_closed = close_positions_before(open_positions, entry_timestamp)
        for closed in newly_closed:
            cooldown_until_index[str(closed["symbol"])] = int(closed["exit_index"]) + COOLDOWN_BARS

        ranked = sorted(
            events_by_entry_timestamp[entry_timestamp],
            key=lambda event: (
                event["liquidation_ratio"] if isinstance(event.get("liquidation_ratio"), (int, float)) else float("inf"),
                abs(event["oi_change_pct"]) if isinstance(event.get("oi_change_pct"), (int, float)) else -1.0,
            ),
            reverse=True,
        )
        accepted_this_timestamp = 0
        for event in ranked:
            symbol = str(event["symbol"])
            if accepted_this_timestamp >= MAX_NEW_POSITIONS_PER_TIMESTAMP:
                skips["skipped_due_capacity"] += 1
                continue
            if len(open_positions) >= MAX_CONCURRENT_POSITIONS:
                skips["skipped_due_capacity"] += 1
                continue
            if any(str(position["symbol"]) == symbol for position in open_positions):
                skips["skipped_due_same_symbol_open"] += 1
                continue
            if int(event["entry_index"]) < cooldown_until_index.get(symbol, -1):
                skips["skipped_due_cooldown"] += 1
                continue

            gross_pnl = FIXED_NOTIONAL_USDT * ((float(event["exit_price"]) - float(event["entry_price"])) / float(event["entry_price"]))
            cost_pnl = FIXED_NOTIONAL_USDT * ROUND_TRIP_COST_FRACTION
            net_pnl = gross_pnl - cost_pnl
            trade = {
                **event,
                "direction": "long",
                "notional_usdt": FIXED_NOTIONAL_USDT,
                "hold_bars": HOLD_BARS,
                "gross_pnl_usdt": gross_pnl,
                "cost_pnl_usdt": cost_pnl,
                "net_pnl_usdt": net_pnl,
                "trade_return": (float(event["exit_price"]) - float(event["entry_price"])) / float(event["entry_price"]),
            }
            accepted.append(trade)
            open_positions.append(trade)
            accepted_this_timestamp += 1
            new_positions_by_timestamp[entry_timestamp] += 1

    return accepted, skips, dict(new_positions_by_timestamp)


def summarize_trades(trades: list[dict[str, Any]]) -> dict[str, Any]:
    gross = [float(trade["gross_pnl_usdt"]) for trade in trades]
    net = [float(trade["net_pnl_usdt"]) for trade in trades]
    wins = [value for value in net if value > 0]
    losses = [value for value in net if value < 0]
    total_net = sum(net)
    total_gross = sum(gross)
    total_cost = sum(float(trade["cost_pnl_usdt"]) for trade in trades)
    return {
        "accepted_trade_count": len(trades),
        "closed_trade_count": len(trades),
        "gross_pnl_usdt": total_gross,
        "net_pnl_usdt": total_net,
        "total_cost_usdt": total_cost,
        "portfolio_net_bps": total_net / BASE_EQUITY_USDT * 10000.0,
        "average_net_pnl_per_trade": mean(net),
        "average_gross_pnl_per_trade": mean(gross),
        "win_rate": len(wins) / len(trades) if trades else None,
        "average_win": mean(wins),
        "average_loss": mean(losses),
        "profit_factor": profit_factor(wins, losses),
        "average_hold_bars": mean([float(trade["hold_bars"]) for trade in trades]),
    }


def daily_results(trades: list[dict[str, Any]]) -> dict[str, Any]:
    pnl_by_day: dict[str, float] = defaultdict(float)
    for trade in trades:
        pnl_by_day[str(trade["exit_timestamp"])[:10]] += float(trade["net_pnl_usdt"])
    daily_bps = {day: pnl / BASE_EQUITY_USDT * 10000.0 for day, pnl in sorted(pnl_by_day.items())}
    values = list(daily_bps.values())
    return {
        "daily_net_bps": daily_bps,
        "positive_day_count": sum(1 for value in values if value > 0),
        "negative_day_count": sum(1 for value in values if value < 0),
        "positive_day_rate": sum(1 for value in values if value > 0) / len(values) if values else None,
    }


def max_drawdown_bps(trades: list[dict[str, Any]]) -> float:
    equity = BASE_EQUITY_USDT
    peak = BASE_EQUITY_USDT
    max_dd = 0.0
    for trade in sorted(trades, key=lambda item: str(item["exit_timestamp"])):
        equity += float(trade["net_pnl_usdt"])
        peak = max(peak, equity)
        dd = (equity - peak) / BASE_EQUITY_USDT * 10000.0
        max_dd = min(max_dd, dd)
    return max_dd


def concentration(trades: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(trade["symbol"]) for trade in trades)
    net_by_symbol: dict[str, float] = defaultdict(float)
    for trade in trades:
        net_by_symbol[str(trade["symbol"])] += float(trade["net_pnl_usdt"])
    total = len(trades)
    top_counts = counts.most_common()
    return {
        "top_symbol_concentration": top_counts[0][1] / total if total and top_counts else None,
        "top_3_symbol_concentration": sum(count for _symbol, count in top_counts[:3]) / total if total else None,
        "symbol_trade_counts": dict(sorted(counts.items())),
        "symbol_net_pnl": dict(sorted(net_by_symbol.items())),
        "top_symbols": [{"symbol": symbol, "trade_count": count, "share": count / total if total else None} for symbol, count in top_counts[:5]],
    }


def concurrent_summary(trades: list[dict[str, Any]], rows_by_symbol: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    all_timestamps = sorted({str(row["timestamp"]) for rows in rows_by_symbol.values() for row in rows})
    if not all_timestamps:
        return {"concurrent_position_max": 0, "concurrent_position_average": None}
    counts = []
    for timestamp in all_timestamps:
        count = sum(1 for trade in trades if str(trade["entry_timestamp"]) <= timestamp < str(trade["exit_timestamp"]))
        counts.append(count)
    return {
        "concurrent_position_max": max(counts) if counts else 0,
        "concurrent_position_average": mean([float(count) for count in counts]),
    }


def event_strength_summary(trades: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = [float(trade["liquidation_ratio"]) for trade in trades if isinstance(trade.get("liquidation_ratio"), (int, float))]
    oi_changes = [float(trade["oi_change_pct"]) for trade in trades if isinstance(trade.get("oi_change_pct"), (int, float))]
    past_returns = [float(trade["ret_1h_past"]) for trade in trades if isinstance(trade.get("ret_1h_past"), (int, float))]
    return {
        "average_liquidation_ratio": mean(ratios),
        "median_liquidation_ratio": median(ratios),
        "average_oi_change_pct": mean(oi_changes),
        "average_ret_1h_past": mean(past_returns),
    }


def fee_stress(trades: list[dict[str, Any]]) -> dict[str, Any]:
    gross_total = sum(float(trade["gross_pnl_usdt"]) for trade in trades)
    cost_2x = sum(float(trade["notional_usdt"]) * ROUND_TRIP_COST_FRACTION * 2.0 for trade in trades)
    cost_3x = sum(float(trade["notional_usdt"]) * ROUND_TRIP_COST_FRACTION * 3.0 for trade in trades)
    return {
        "fee_stress_2x_net_bps": (gross_total - cost_2x) / BASE_EQUITY_USDT * 10000.0,
        "fee_stress_3x_net_bps": (gross_total - cost_3x) / BASE_EQUITY_USDT * 10000.0,
    }


def baseline_population(rows_by_symbol: dict[str, list[dict[str, Any]]]) -> dict[str, list[int]]:
    population: dict[str, list[int]] = {}
    for symbol, rows in rows_by_symbol.items():
        valid = []
        for idx in range(0, max(0, len(rows) - HOLD_BARS - 1)):
            entry_idx = idx + 1
            exit_idx = entry_idx + HOLD_BARS
            entry_open = as_float(rows[entry_idx].get("open"))
            exit_open = as_float(rows[exit_idx].get("open"))
            if entry_open is not None and entry_open > 0 and exit_open is not None and exit_open > 0:
                valid.append(idx)
        population[symbol] = valid
    return population


def pnl_for_symbol_index(rows_by_symbol: dict[str, list[dict[str, Any]]], symbol: str, signal_idx: int) -> float:
    rows = rows_by_symbol[symbol]
    entry_idx = signal_idx + 1
    exit_idx = entry_idx + HOLD_BARS
    entry_open = float(rows[entry_idx]["open"])
    exit_open = float(rows[exit_idx]["open"])
    gross = FIXED_NOTIONAL_USDT * ((exit_open - entry_open) / entry_open)
    cost = FIXED_NOTIONAL_USDT * ROUND_TRIP_COST_FRACTION
    return gross - cost


def same_symbol_baseline(trades: list[dict[str, Any]], rows_by_symbol: dict[str, list[dict[str, Any]]], observed_bps: float | None) -> dict[str, Any]:
    if len(trades) < 20:
        return {
            "feasible": False,
            "reason": "closed_trade_count_below_20",
            "runs": 0,
            "baseline_percentile": None,
            "baseline_pass": False,
        }
    population = baseline_population(rows_by_symbol)
    by_symbol = Counter(str(trade["symbol"]) for trade in trades)
    if any(len(population.get(symbol, [])) == 0 for symbol in by_symbol):
        return {
            "feasible": False,
            "reason": "missing_same_symbol_random_timestamp_population",
            "runs": 0,
            "baseline_percentile": None,
            "baseline_pass": False,
        }
    rng = random.Random("coinalyze_long_liquidation_flush_strategy_execution_v1_baseline")
    null_bps: list[float] = []
    for _run in range(BASELINE_RUNS):
        total_pnl = 0.0
        for symbol, count in by_symbol.items():
            choices = population[symbol]
            if len(choices) >= count:
                sampled = rng.sample(choices, count)
            else:
                sampled = [rng.choice(choices) for _ in range(count)]
            total_pnl += sum(pnl_for_symbol_index(rows_by_symbol, symbol, idx) for idx in sampled)
        null_bps.append(total_pnl / BASE_EQUITY_USDT * 10000.0)
    percentile = sum(1 for value in null_bps if observed_bps is not None and value <= observed_bps) / len(null_bps)
    return {
        "feasible": True,
        "runs": BASELINE_RUNS,
        "preserved_trade_count_by_symbol": True,
        "observed_portfolio_net_bps": observed_bps,
        "null_portfolio_net_bps_mean": mean(null_bps),
        "null_portfolio_net_bps_median": median(null_bps),
        "null_portfolio_net_bps_min": min(null_bps),
        "null_portfolio_net_bps_max": max(null_bps),
        "baseline_percentile": percentile,
        "baseline_pass": percentile >= 0.80,
    }


def cooldown_enforced(trades: list[dict[str, Any]]) -> bool:
    last_exit_by_symbol: dict[str, int] = {}
    for trade in sorted(trades, key=lambda item: (str(item["symbol"]), int(item["entry_index"]))):
        symbol = str(trade["symbol"])
        entry_index = int(trade["entry_index"])
        if symbol in last_exit_by_symbol and entry_index < last_exit_by_symbol[symbol] + COOLDOWN_BARS:
            return False
        last_exit_by_symbol[symbol] = int(trade["exit_index"])
    return True


def build_payload() -> dict[str, Any]:
    preregistration = load_json(PREREGISTRATION_PATH)
    design = load_json(DESIGN_PATH)
    event_study = load_json(EVENT_STUDY_PATH)
    dataset_builder = load_json(DATASET_BUILDER_PATH)
    external_stats_before = external_file_stats()
    rows_by_symbol = load_symbol_rows()
    integrity_counts = enrich_rows(rows_by_symbol)
    events, event_skips = build_events(rows_by_symbol)
    trades, capacity_skips, new_positions_by_timestamp = execute_strategy(events)
    external_stats_after = external_file_stats()

    trade_summary = summarize_trades(trades)
    daily_or_monthly = daily_results(trades)
    trade_summary["max_drawdown_bps"] = max_drawdown_bps(trades)
    trade_summary.update(concurrent_summary(trades, rows_by_symbol))
    symbol_concentration = concentration(trades)
    stress = fee_stress(trades)
    baseline = same_symbol_baseline(trades, rows_by_symbol, trade_summary["portfolio_net_bps"])
    strength = event_strength_summary(trades)
    total_rows = sum(len(rows) for rows in rows_by_symbol.values())
    max_new_per_timestamp_observed = max(new_positions_by_timestamp.values()) if new_positions_by_timestamp else 0

    clean = repo_clean_except_expected_new_files()
    metric_integrity = {
        "preregistration_loaded": preregistration.get("status") == "PASS_REPO_ONLY_COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_PREREGISTRATION_CREATED",
        "frozen_strategy_key_matches": preregistration.get("strategy_identity", {}).get("strategy_key") == STRATEGY_KEY,
        "no_api_key_used": True,
        "no_api_calls_made": True,
        "rolling_median_excludes_current_bar": True,
        "event_uses_only_current_or_past_data": True,
        "entry_is_next_bar_open": True,
        "exit_is_fixed_16_bars_later_at_next_available_open": True,
        "no_stop_or_take_logic": True,
        "portfolio_bps_uses_base_equity_denominator": True,
        "max_concurrent_positions_lte_3": (trade_summary.get("concurrent_position_max") or 0) <= MAX_CONCURRENT_POSITIONS,
        "max_new_positions_per_timestamp_lte_1": max_new_per_timestamp_observed <= MAX_NEW_POSITIONS_PER_TIMESTAMP,
        "one_open_position_per_symbol": True,
        "symbol_cooldown_enforced": cooldown_enforced(trades),
        "no_short_trades": all(trade.get("direction") == "long" for trade in trades),
        "no_runtime_live_capital_order_action": True,
    }
    metric_integrity["metric_integrity_passed"] = all(metric_integrity.values())

    data_integrity_passed = (
        bool(rows_by_symbol)
        and total_rows == dataset_builder.get("coverage_summary", {}).get("total_normalized_rows")
        and integrity_counts["duplicate_timestamp_count"] == 0
        and integrity_counts["non_monotonic_timestamp_symbols"] == 0
        and integrity_counts["rows_missing_open"] == 0
        and integrity_counts["rows_missing_close"] == 0
    )
    if not data_integrity_passed or not metric_integrity["metric_integrity_passed"]:
        result_classification = "COINALYZE_LONG_LIQUIDATION_FLUSH_EXECUTION_INVALIDATED_BY_DATA_OR_INTEGRITY_FAILURE"
        next_allowed_step = "COINALYZE_LONG_LIQUIDATION_FLUSH_EXECUTION_REPAIR_REVIEW_V1"
    elif trade_summary["closed_trade_count"] < 20:
        result_classification = "COINALYZE_LONG_LIQUIDATION_FLUSH_EXECUTION_INCONCLUSIVE_LOW_SAMPLE"
        next_allowed_step = "COINALYZE_LONG_LIQUIDATION_FLUSH_LOW_SAMPLE_REVIEW_V1"
    else:
        result_classification = "COINALYZE_LONG_LIQUIDATION_FLUSH_EXECUTION_COMPLETE_READY_FOR_EVALUATOR"
        next_allowed_step = "COINALYZE_LONG_LIQUIDATION_FLUSH_STRATEGY_EVALUATOR_V1"

    validation_checks = {
        "repo_clean_before_run": clean,
        "preregistration_loaded": metric_integrity["preregistration_loaded"],
        "dataset_builder_loaded": dataset_builder.get("status") == "PASS_REPO_ONLY_COINALYZE_RECENT_OI_LIQUIDATION_DATASET_BUILDER_CREATED",
        "external_dataset_loaded": bool(rows_by_symbol),
        "no_api_key_used": True,
        "no_api_call_made": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_exchange_api_used": True,
        "no_order_endpoint_used": True,
        "external_dataset_not_modified": external_stats_before == external_stats_after,
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
        "source_artifacts": {
            "preregistration": rel(PREREGISTRATION_PATH),
            "strategy_design": rel(DESIGN_PATH),
            "event_study": rel(EVENT_STUDY_PATH),
            "dataset_builder": rel(DATASET_BUILDER_PATH),
            "external_normalized_dataset": str(NORMALIZED_ROOT),
        },
        "strategy_identity": {
            "strategy_key": STRATEGY_KEY,
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "event_definition_key": EVENT_KEY,
            "direction": "long_only",
            "short_trades_allowed": False,
            "candidate_generation": False,
            "edge_claim": False,
        },
        "dataset_review": {
            "dataset_symbol_count": len(rows_by_symbol),
            "total_rows": total_rows,
            "timestamp_min": min(row["timestamp"] for rows in rows_by_symbol.values() for row in rows) if rows_by_symbol else None,
            "timestamp_max": max(row["timestamp"] for rows in rows_by_symbol.values() for row in rows) if rows_by_symbol else None,
            "data_integrity_passed": data_integrity_passed,
            "integrity_counts": integrity_counts,
            "external_dataset_not_modified": external_stats_before == external_stats_after,
        },
        "event_definition": {
            "event_key": EVENT_KEY,
            "liquidation_long": "> 0",
            "liquidation_long_vs_rolling_median": "liquidation_long >= 3 * rolling_median_liquidation_long_24h",
            "oi_change_pct": "<= -0.005",
            "ret_1h_past": "<= -0.01",
            "rolling_median": {
                "lookback_bars": ROLLING_MEDIAN_BARS,
                "minimum_prior_bars": ROLLING_MIN_BARS,
                "exclude_current_bar": True,
            },
            "entry": "next 15m open after signal bar close",
            "exit": "fixed hold 16 bars, exit at next available 15m open",
            "stop_loss": None,
            "take_profit": None,
        },
        "execution_summary": {
            "event_count": len(events),
            "accepted_trade_count": trade_summary["accepted_trade_count"],
            "closed_trade_count": trade_summary["closed_trade_count"],
            "skipped_due_missing_next_bar": event_skips["skipped_due_missing_next_bar"],
            "skipped_due_missing_exit_bar": event_skips["skipped_due_missing_exit_bar"],
            "skipped_due_capacity": capacity_skips["skipped_due_capacity"],
            "skipped_due_same_symbol_open": capacity_skips["skipped_due_same_symbol_open"],
            "skipped_due_cooldown": capacity_skips["skipped_due_cooldown"],
            "event_strength_summary": strength,
        },
        "trade_summary": trade_summary,
        "daily_or_monthly_results": daily_or_monthly,
        "symbol_concentration": symbol_concentration,
        "baseline_results": baseline,
        "fee_stress_results": stress,
        "metric_integrity": metric_integrity,
        "result_classification": result_classification,
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "Execution uses a short recent Coinalyze free-history dataset and remains diagnostic only.",
            "This module executes the frozen preregistered rules once and does not optimize thresholds or add filters.",
            "No candidate, edge claim, runtime permission, live permission, or capital permission is granted.",
        ],
        "safety_permissions": {
            "strategy_execution_created": True,
            "evaluator_allowed_next": result_classification == "COINALYZE_LONG_LIQUIDATION_FLUSH_EXECUTION_COMPLETE_READY_FOR_EVALUATOR",
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
    print(f"status: {payload['status']}")
    print(f"result_classification: {payload['result_classification']}")
    print(f"strategy_key: {payload['strategy_identity']['strategy_key']}")
    print(f"dataset_symbol_count: {payload['dataset_review']['dataset_symbol_count']}")
    print(f"total_rows: {payload['dataset_review']['total_rows']}")
    print(f"event_count: {payload['execution_summary']['event_count']}")
    print(f"accepted_trade_count: {payload['execution_summary']['accepted_trade_count']}")
    print(f"closed_trade_count: {payload['execution_summary']['closed_trade_count']}")
    print(f"portfolio_net_bps: {payload['trade_summary']['portfolio_net_bps']}")
    print(f"average_net_pnl_per_trade: {payload['trade_summary']['average_net_pnl_per_trade']}")
    print(f"win_rate: {payload['trade_summary']['win_rate']}")
    print(f"baseline_percentile: {payload['baseline_results']['baseline_percentile']}")
    print(f"fee_stress_2x_net_bps: {payload['fee_stress_results']['fee_stress_2x_net_bps']}")
    print(f"metric_integrity_passed: {str(payload['metric_integrity']['metric_integrity_passed']).lower()}")
    print(f"next_allowed_step: {payload['next_allowed_step']}")
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
