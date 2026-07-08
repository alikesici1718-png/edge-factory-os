#!/usr/bin/env python
"""Strict anti-overfit alpha search protocol for Binance UM bookDepth plus aggTrades."""

from __future__ import annotations

import bisect
import csv
import hashlib
import json
import math
import os
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import edge_factory_orderbook_um_81_streaming_absorption_discovery_90d_v1 as base


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "edge_factory_anti_overfit_alpha_search"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
FIXED_GRID_JSON = OUTPUTS_DIR / f"{PREFIX}_fixed_grid.json"
FOLD_PLAN_CSV = OUTPUTS_DIR / f"{PREFIX}_fold_plan.csv"
TRIAL_LOG_CSV = OUTPUTS_DIR / f"{PREFIX}_trial_log.csv"
RANKED_CANDIDATES_CSV = OUTPUTS_DIR / f"{PREFIX}_ranked_candidates.csv"
REJECTED_CANDIDATES_CSV = OUTPUTS_DIR / f"{PREFIX}_rejected_candidates.csv"
PROMOTED_CANDIDATES_CSV = OUTPUTS_DIR / f"{PREFIX}_promoted_candidates.csv"
WALK_FORWARD_RESULTS_CSV = OUTPUTS_DIR / f"{PREFIX}_walk_forward_results.csv"
MULTIPLE_TESTING_JSON = OUTPUTS_DIR / f"{PREFIX}_multiple_testing_report.json"

RUN_ENV = "EDGE_FACTORY_RUN_ANTI_OVERFIT_ALPHA_SEARCH"
TASK_NAME = "EDGE_FACTORY_ANTI_OVERFIT_ALPHA_SEARCH_PROTOCOL_V1"

BOOKDEPTH_RAW_ROOT = Path(r"C:\edge_factory_external_data\binance_um_81_full_bookdepth_raw")
AGGTRADES_RAW_ROOT = Path(r"C:\edge_factory_external_data\binance_um_81_full_matching_aggtrades_raw")
COVERAGE_START = date(2023, 1, 1)
COVERAGE_END = date(2026, 6, 15)
EXPECTED_SYMBOL_COUNT = 81

CATEGORIES = [
    "BUY_PRESSURE_ABSORBED",
    "SELL_PRESSURE_ABSORBED",
    "FLOW_AND_DEPTH_ALIGNED_UP",
    "FLOW_AND_DEPTH_ALIGNED_DOWN",
]
HORIZONS_SECONDS = [30, 60, 120, 300, 600]
COOLDOWNS_SECONDS = [300, 600, 900, 1200]
DELAYS_SECONDS = [0, 1, 3, 5, 10]
COSTS_BPS = [0.0, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0]
CAPACITY_SUBSETS = [
    "ALL",
    "EXCLUDE_THIN",
    "HIGH_ONLY",
    "HIGH_MEDIUM",
    "TOP_10_BY_DISCOVERY_NOTIONAL",
    "TOP_20_BY_DISCOVERY_NOTIONAL",
    "TOP_40_BY_DISCOVERY_NOTIONAL",
    "MIN_AROUND_EVENT_NOTIONAL_5000",
    "MIN_AROUND_EVENT_NOTIONAL_10000",
    "MIN_AROUND_EVENT_NOTIONAL_25000",
    "MIN_AROUND_EVENT_NOTIONAL_50000",
    "MIN_AROUND_EVENT_NOTIONAL_100000",
]
MIN_NOTIONAL_BY_SUBSET = {
    "MIN_AROUND_EVENT_NOTIONAL_5000": 5_000.0,
    "MIN_AROUND_EVENT_NOTIONAL_10000": 10_000.0,
    "MIN_AROUND_EVENT_NOTIONAL_25000": 25_000.0,
    "MIN_AROUND_EVENT_NOTIONAL_50000": 50_000.0,
    "MIN_AROUND_EVENT_NOTIONAL_100000": 100_000.0,
}

DISCOVERY_DAYS = 180
VALIDATION_DAYS = 90
TEST_DAYS = 90
STEP_DAYS = 90
DISCOVERY_PROMOTION_LIMIT = 20
VALIDATION_PROMOTION_LIMIT = 5

MIN_KEPT_EVENTS_PER_FOLD = 5_000
MIN_BREAK_EVEN_BPS = 3.0
MIN_SYMBOL_STABILITY = 0.65
MIN_MONTH_STABILITY = 0.70
MIN_WEEK_STABILITY = 0.65
MAX_SINGLE_SYMBOL_SHARE = 0.25
MAX_SINGLE_WEEK_SHARE = 0.15
SMALL_CAP_ONLY_SUBSETS = {
    "MIN_AROUND_EVENT_NOTIONAL_5000",
    "MIN_AROUND_EVENT_NOTIONAL_10000",
}

CAPACITY_WINDOW_RADIUS_MS = 30_000
PROGRESS_INTERVAL_SECONDS = 30

CLASSIFICATIONS = [
    "ROBUST_CAPACITY_AWARE_EDGE_CANDIDATE",
    "SMALL_CAP_ALPHA_CANDIDATE",
    "FILTER_ONLY_CANDIDATE",
    "RECENT_OR_REGIME_SPECIFIC_ONLY",
    "UNSTABLE_OR_OVERFIT",
    "REJECTED_NO_ROBUST_EDGE",
]


@dataclass(frozen=True)
class CandidateSpec:
    category: str
    horizon_seconds: int
    cooldown_seconds: int
    capacity_subset: str

    def key(self) -> str:
        return "|".join(
            [
                self.category,
                f"h{self.horizon_seconds}",
                f"cd{self.cooldown_seconds}",
                self.capacity_subset,
            ]
        )


@dataclass
class MomentStats:
    count: int = 0
    sum_value: float = 0.0
    sum_square: float = 0.0

    def add(self, value: float | None) -> None:
        if value is None:
            return
        self.count += 1
        self.sum_value += value
        self.sum_square += value * value

    def mean(self) -> float | None:
        if not self.count:
            return None
        return self.sum_value / self.count

    def std(self) -> float | None:
        if self.count <= 1:
            return None
        mean_value = self.sum_value / self.count
        variance = max(0.0, (self.sum_square / self.count) - (mean_value * mean_value))
        return math.sqrt(variance)


@dataclass
class CandidateAggregate:
    returns_by_delay: dict[int, MomentStats]
    null_by_delay: dict[int, MomentStats]
    symbol_counts: Counter[str]
    week_counts: Counter[str]
    month_counts: Counter[str]
    symbol_returns: dict[str, MomentStats]
    week_returns: dict[str, MomentStats]
    month_returns: dict[str, MomentStats]
    thin_events: int = 0

    @classmethod
    def fresh(cls) -> "CandidateAggregate":
        return cls(
            returns_by_delay=defaultdict(MomentStats),
            null_by_delay=defaultdict(MomentStats),
            symbol_counts=Counter(),
            week_counts=Counter(),
            month_counts=Counter(),
            symbol_returns=defaultdict(MomentStats),
            week_returns=defaultdict(MomentStats),
            month_returns=defaultdict(MomentStats),
        )


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rounded(value: float | None, places: int = 10) -> float | str:
    if value is None or math.isnan(value):
        return ""
    return round(value, places)


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def sign_of(value: float | None, tolerance: float = 1e-12) -> int:
    if value is None or abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1


def bool_env(name: str) -> bool:
    return os.environ.get(name, "").strip().upper() == "YES"


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def grid_payload() -> dict[str, Any]:
    base_candidate_count = (
        len(CATEGORIES)
        * len(HORIZONS_SECONDS)
        * len(COOLDOWNS_SECONDS)
        * len(CAPACITY_SUBSETS)
    )
    full_stress_grid_count = base_candidate_count * len(DELAYS_SECONDS) * len(COSTS_BPS)
    grid = {
        "task": TASK_NAME,
        "created_at_utc": utc_now_text(),
        "grid_frozen_before_search": True,
        "categories": CATEGORIES,
        "horizons_seconds": HORIZONS_SECONDS,
        "cooldowns_seconds": COOLDOWNS_SECONDS,
        "delays_seconds": DELAYS_SECONDS,
        "costs_bps": COSTS_BPS,
        "capacity_subsets": CAPACITY_SUBSETS,
        "base_candidate_count": base_candidate_count,
        "full_stress_grid_count": full_stress_grid_count,
        "ranking_unit": "category+horizon+cooldown+capacity_subset; delays and costs are fixed execution-stress axes",
        "baseline": {
            "candidate": "SELL_PRESSURE_ABSORBED@300s",
            "cooldown_seconds": 600,
            "full_history_break_even_bps": 3.724399,
            "note": "capacity-limited baseline, used for comparison only",
        },
        "hard_pass_gates": {
            "kept_events_per_fold_min": MIN_KEPT_EVENTS_PER_FOLD,
            "same_sign_discovery_validation_test": True,
            "break_even_bps_min": MIN_BREAK_EVEN_BPS,
            "survives_cost_bps_at_delay_seconds": [
                {"delay_seconds": 3, "cost_bps": 3.0},
                {"delay_seconds": 5, "cost_bps": 2.0},
            ],
            "symbol_stability_min": MIN_SYMBOL_STABILITY,
            "month_stability_min": MIN_MONTH_STABILITY,
            "week_stability_min": MIN_WEEK_STABILITY,
            "single_symbol_kept_event_share_max": MAX_SINGLE_SYMBOL_SHARE,
            "single_week_kept_event_share_max": MAX_SINGLE_WEEK_SHARE,
            "not_thin_only_unless_small_cap_only": True,
            "null_comparison_same_sign_and_nonzero": True,
        },
        "walk_forward": {
            "discovery_days": DISCOVERY_DAYS,
            "validation_days": VALIDATION_DAYS,
            "test_days": TEST_DAYS,
            "step_days": STEP_DAYS,
            "discovery_promotion_limit": DISCOVERY_PROMOTION_LIMIT,
            "validation_promotion_limit": VALIDATION_PROMOTION_LIMIT,
            "test_window_used_once_only": True,
            "direction_inferred_only_in_discovery": True,
        },
        "safety": {
            "downloads_run": False,
            "row_level_dataset_created": False,
            "trading_or_order_logic": False,
            "private_endpoint_logic": False,
            "recommendations_created": False,
        },
    }
    stable = json.dumps(
        {key: value for key, value in grid.items() if key not in {"created_at_utc"}},
        sort_keys=True,
        separators=(",", ":"),
    )
    grid["fixed_grid_sha256"] = hashlib.sha256(stable.encode("utf-8")).hexdigest()
    return grid


def iter_candidate_specs() -> Iterable[CandidateSpec]:
    for category in CATEGORIES:
        for horizon in HORIZONS_SECONDS:
            for cooldown in COOLDOWNS_SECONDS:
                for subset in CAPACITY_SUBSETS:
                    yield CandidateSpec(category, horizon, cooldown, subset)


def build_fold_plan() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = COVERAGE_START
    fold_id = 1
    while True:
        discovery_start = start
        discovery_end = discovery_start + timedelta(days=DISCOVERY_DAYS - 1)
        validation_start = discovery_end + timedelta(days=1)
        validation_end = validation_start + timedelta(days=VALIDATION_DAYS - 1)
        test_start = validation_end + timedelta(days=1)
        test_end = test_start + timedelta(days=TEST_DAYS - 1)
        if test_end > COVERAGE_END:
            break
        rows.append(
            {
                "fold_id": fold_id,
                "discovery_start": discovery_start.isoformat(),
                "discovery_end": discovery_end.isoformat(),
                "validation_start": validation_start.isoformat(),
                "validation_end": validation_end.isoformat(),
                "test_start": test_start.isoformat(),
                "test_end": test_end.isoformat(),
                "step_days": STEP_DAYS,
                "test_window_use": "ONCE_AFTER_LOCKED_DISCOVERY_AND_VALIDATION_PROMOTION",
            }
        )
        start += timedelta(days=STEP_DAYS)
        fold_id += 1
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_verified_pairs() -> list[dict[str, Any]]:
    if path_is_inside(BOOKDEPTH_RAW_ROOT, REPO_ROOT) or path_is_inside(AGGTRADES_RAW_ROOT, REPO_ROOT):
        raise RuntimeError("raw data roots must stay outside repository")
    book_rows = base.load_verified_paths(base.BOOKDEPTH_FILE_STATUS_CSV, BOOKDEPTH_RAW_ROOT)
    agg_rows = base.load_verified_paths(base.AGGTRADES_FILE_STATUS_CSV, AGGTRADES_RAW_ROOT)
    pairs: list[dict[str, Any]] = []
    for symbol, file_date in sorted(set(book_rows) & set(agg_rows)):
        if COVERAGE_START.isoformat() <= file_date <= COVERAGE_END.isoformat():
            pairs.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "year_month": file_date[:7],
                    "week": base.iso_week_text(file_date),
                    "bookdepth_zip_path": book_rows[(symbol, file_date)]["local_zip_path"],
                    "aggtrades_zip_path": agg_rows[(symbol, file_date)]["local_zip_path"],
                }
            )
    return pairs


def pairs_for_window(
    pairs: list[dict[str, Any]],
    start_text: str,
    end_text: str,
) -> list[dict[str, Any]]:
    return [pair for pair in pairs if start_text <= str(pair["file_date"]) <= end_text]


def read_features_trade_details(
    pair: dict[str, Any],
) -> tuple[list[int], list[dict[str, Any]], list[int], list[float], list[float]]:
    timestamps, rows = base.read_bookdepth_features(pair)
    if not timestamps:
        return timestamps, rows, [], [], [0.0]

    trade_times: list[int] = []
    trade_prices: list[float] = []
    trade_notionals: list[float] = []
    out_of_order = False
    previous_trade_ms = -1
    reader = iter(base.single_csv_reader(Path(str(pair["aggtrades_zip_path"]))))
    header = next(reader, None)
    if not header:
        base.add_rolling_features(rows)
        return timestamps, rows, [], [], [0.0]
    positions = {name: index for index, name in enumerate(header)}
    required = {"price", "quantity", "transact_time", "is_buyer_maker"}
    if not required.issubset(positions):
        raise ValueError(f"aggTrades CSV missing columns: {required - set(positions)}")

    for columns in reader:
        transact_ms = base.int_value(columns[positions["transact_time"]], -1)
        price = base.float_value(columns[positions["price"]])
        quantity = base.float_value(columns[positions["quantity"]])
        notional = price * quantity
        if transact_ms < previous_trade_ms:
            out_of_order = True
        previous_trade_ms = transact_ms
        trade_times.append(transact_ms)
        trade_prices.append(price)
        trade_notionals.append(notional)

        row_index = bisect.bisect_right(timestamps, transact_ms) - 1
        if row_index < 0:
            continue
        row = rows[row_index]
        row["trade_count"] += 1
        row["total_qty"] += quantity
        row["total_notional"] += notional
        if base.bool_value(columns[positions["is_buyer_maker"]]):
            row["aggressive_sell_qty"] += quantity
            row["aggressive_sell_notional"] += notional
        else:
            row["aggressive_buy_qty"] += quantity
            row["aggressive_buy_notional"] += notional

    if out_of_order:
        combined = sorted(zip(trade_times, trade_prices, trade_notionals), key=lambda item: item[0])
        trade_times = [item[0] for item in combined]
        trade_prices = [item[1] for item in combined]
        trade_notionals = [item[2] for item in combined]

    prefix_notionals = [0.0]
    running = 0.0
    for notional in trade_notionals:
        running += notional
        prefix_notionals.append(running)
    base.add_rolling_features(rows)
    return timestamps, rows, trade_times, trade_prices, prefix_notionals


def delayed_forward_price_return(
    event_ms: int,
    horizon_seconds: int,
    delay_seconds: int,
    trade_times: list[int],
    trade_prices: list[float],
) -> float | None:
    if not trade_times:
        return None
    reference_ms = event_ms + delay_seconds * 1000
    future_ms = event_ms + horizon_seconds * 1000
    if reference_ms >= future_ms:
        return None
    reference_index = bisect.bisect_right(trade_times, reference_ms) - 1
    future_index = bisect.bisect_left(trade_times, future_ms)
    if reference_index < 0 or future_index >= len(trade_prices):
        return None
    reference_price = trade_prices[reference_index]
    future_price = trade_prices[future_index]
    if reference_price <= 0:
        return None
    return (future_price / reference_price) - 1.0


def notional_around_event(event_ms: int, trade_times: list[int], prefix_notionals: list[float]) -> float | None:
    if not trade_times:
        return None
    left = bisect.bisect_left(trade_times, event_ms - CAPACITY_WINDOW_RADIUS_MS)
    right = bisect.bisect_right(trade_times, event_ms + CAPACITY_WINDOW_RADIUS_MS)
    if right <= left:
        return 0.0
    return prefix_notionals[right] - prefix_notionals[left]


def percentile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def liquidity_tier(p50_notional: float | None) -> str:
    if p50_notional is None:
        return "UNKNOWN"
    if p50_notional >= 1_000_000:
        return "HIGH"
    if p50_notional >= 250_000:
        return "MEDIUM"
    if p50_notional >= 50_000:
        return "LOW"
    return "THIN"


def build_capacity_plan(discovery_pairs: list[dict[str, Any]]) -> dict[str, Any]:
    by_symbol: dict[str, list[float]] = defaultdict(list)
    started = time.monotonic()
    next_progress = started + PROGRESS_INTERVAL_SECONDS
    failed = 0
    for index, pair in enumerate(discovery_pairs, start=1):
        try:
            timestamps, rows, trade_times, _trade_prices, prefix_notionals = read_features_trade_details(pair)
            symbol = str(pair["symbol"])
            for row_index, row in enumerate(rows):
                category = str(row.get("absorption_category") or "")
                if category not in CATEGORIES:
                    continue
                value = notional_around_event(timestamps[row_index], trade_times, prefix_notionals)
                if value is not None:
                    by_symbol[symbol].append(value)
        except Exception:
            failed += 1
        if time.monotonic() >= next_progress:
            print(
                "progress phase=capacity_plan "
                f"symbol_days={index}/{len(discovery_pairs)} failed={failed} "
                f"elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    symbol_profiles: dict[str, dict[str, Any]] = {}
    for symbol, values in by_symbol.items():
        p50 = percentile(values, 0.50)
        symbol_profiles[symbol] = {
            "sample_count": len(values),
            "p50_notional": p50,
            "liquidity_tier": liquidity_tier(p50),
        }
    ranked_symbols = sorted(
        symbol_profiles,
        key=lambda symbol: float(symbol_profiles[symbol].get("p50_notional") or 0.0),
        reverse=True,
    )
    return {
        "source": "discovery_only_locked_before_validation_and_test",
        "failed_symbol_days": failed,
        "symbol_profiles": symbol_profiles,
        "top10": ranked_symbols[:10],
        "top20": ranked_symbols[:20],
        "top40": ranked_symbols[:40],
    }


def event_in_subset(
    subset: str,
    symbol: str,
    around_notional: float | None,
    capacity_plan: dict[str, Any],
) -> tuple[bool, bool]:
    profiles = capacity_plan.get("symbol_profiles", {})
    tier = str(profiles.get(symbol, {}).get("liquidity_tier", "UNKNOWN"))
    is_thin = tier == "THIN"
    if subset == "ALL":
        return True, is_thin
    if subset == "EXCLUDE_THIN":
        return tier not in {"THIN", "UNKNOWN"}, is_thin
    if subset == "HIGH_ONLY":
        return tier == "HIGH", is_thin
    if subset == "HIGH_MEDIUM":
        return tier in {"HIGH", "MEDIUM"}, is_thin
    if subset == "TOP_10_BY_DISCOVERY_NOTIONAL":
        return symbol in set(capacity_plan.get("top10", [])), is_thin
    if subset == "TOP_20_BY_DISCOVERY_NOTIONAL":
        return symbol in set(capacity_plan.get("top20", [])), is_thin
    if subset == "TOP_40_BY_DISCOVERY_NOTIONAL":
        return symbol in set(capacity_plan.get("top40", [])), is_thin
    threshold = MIN_NOTIONAL_BY_SUBSET.get(subset)
    if threshold is not None:
        return around_notional is not None and around_notional >= threshold, is_thin
    return False, is_thin


def aggregate_window(
    phase: str,
    pairs: list[dict[str, Any]],
    specs: list[CandidateSpec],
    capacity_plan: dict[str, Any],
) -> tuple[dict[str, CandidateAggregate], dict[str, Any]]:
    spec_by_category: dict[str, list[CandidateSpec]] = defaultdict(list)
    for spec in specs:
        spec_by_category[spec.category].append(spec)
    all_horizons = sorted({spec.horizon_seconds for spec in specs})
    all_cooldowns = sorted({spec.cooldown_seconds for spec in specs})
    aggregates: dict[str, CandidateAggregate] = {spec.key(): CandidateAggregate.fresh() for spec in specs}
    null_stats: dict[tuple[int, int], MomentStats] = defaultdict(MomentStats)
    last_kept: dict[tuple[str, int, str, str], int] = {}
    last_null_kept: dict[tuple[str, int, int], int] = {}
    processed = 0
    failed = 0
    feature_rows = 0
    category_counts: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    started = time.monotonic()
    next_progress = started + PROGRESS_INTERVAL_SECONDS

    for pair in pairs:
        try:
            timestamps, rows, trade_times, trade_prices, prefix_notionals = read_features_trade_details(pair)
            processed += 1
            feature_rows += len(rows)
            symbol = str(pair["symbol"])
            week = str(pair.get("week", ""))
            month = str(pair.get("year_month", ""))
            for row_index, row in enumerate(rows):
                event_ms = timestamps[row_index]
                category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
                if category not in base.CATEGORIES:
                    category = "INSUFFICIENT_DATA"
                category_counts[category] += 1

                for horizon in all_horizons:
                    for delay in DELAYS_SECONDS:
                        null_key = (symbol, horizon, delay)
                        if event_ms - last_null_kept.get(null_key, -10**18) < min(all_cooldowns) * 1000:
                            continue
                        value = delayed_forward_price_return(event_ms, horizon, delay, trade_times, trade_prices)
                        if value is None:
                            continue
                        last_null_kept[null_key] = event_ms
                        null_stats[(horizon, delay)].add(value)

                if category not in spec_by_category:
                    continue
                around_notional = notional_around_event(event_ms, trade_times, prefix_notionals)
                for spec in spec_by_category[category]:
                    cooldown_key = (spec.key(), spec.cooldown_seconds, symbol, phase)
                    if event_ms - last_kept.get(cooldown_key, -10**18) < spec.cooldown_seconds * 1000:
                        continue
                    keep, is_thin = event_in_subset(spec.capacity_subset, symbol, around_notional, capacity_plan)
                    if not keep:
                        continue
                    values = {
                        delay: delayed_forward_price_return(
                            event_ms,
                            spec.horizon_seconds,
                            delay,
                            trade_times,
                            trade_prices,
                        )
                        for delay in DELAYS_SECONDS
                    }
                    if values[0] is None:
                        continue
                    last_kept[cooldown_key] = event_ms
                    aggregate = aggregates[spec.key()]
                    aggregate.symbol_counts[symbol] += 1
                    aggregate.week_counts[week] += 1
                    aggregate.month_counts[month] += 1
                    if is_thin:
                        aggregate.thin_events += 1
                    for delay, value in values.items():
                        aggregate.returns_by_delay[delay].add(value)
                        null_mean = null_stats[(spec.horizon_seconds, delay)].mean()
                        if null_mean is not None and value is not None:
                            aggregate.null_by_delay[delay].add(value - null_mean)
                    aggregate.symbol_returns[symbol].add(values[0])
                    aggregate.week_returns[week].add(values[0])
                    aggregate.month_returns[month].add(values[0])
        except Exception as exc:  # noqa: BLE001
            failed += 1
            if len(failure_examples) < 20:
                failure_examples.append(
                    {
                        "symbol": str(pair.get("symbol", "")),
                        "file_date": str(pair.get("file_date", "")),
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        if time.monotonic() >= next_progress:
            print(
                f"progress phase={phase} processed_symbol_days={processed}/{len(pairs)} "
                f"failed_symbol_days={failed} feature_rows={feature_rows} "
                f"elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    for spec in specs:
        aggregate = aggregates[spec.key()]
        for delay in DELAYS_SECONDS:
            aggregate.null_by_delay[delay] = null_stats[(spec.horizon_seconds, delay)]
    metadata = {
        "phase": phase,
        "processed_symbol_days": processed,
        "failed_symbol_days": failed,
        "feature_rows": feature_rows,
        "category_counts": dict(category_counts),
        "failure_examples": failure_examples,
    }
    return aggregates, metadata


def stability_rate(groups: dict[str, MomentStats], locked_direction: int, min_count: int) -> tuple[int, int, float | None]:
    support = 0
    consistent = 0
    for stats in groups.values():
        mean_value = stats.mean()
        if mean_value is None or stats.count < min_count:
            continue
        support += 1
        if locked_direction and sign_of(mean_value) == locked_direction:
            consistent += 1
    return support, consistent, safe_div(consistent, support)


def metrics_for_aggregate(
    spec: CandidateSpec,
    phase: str,
    aggregate: CandidateAggregate,
    locked_direction: int | None = None,
) -> dict[str, Any]:
    base_stats = aggregate.returns_by_delay[0]
    candidate_mean = base_stats.mean()
    null_mean = aggregate.null_by_delay[0].mean()
    effect = candidate_mean - null_mean if candidate_mean is not None and null_mean is not None else None
    direction = locked_direction or sign_of(effect)
    edge = effect * direction if effect is not None and direction else None
    break_even_bps = edge * 10_000 if edge is not None else None
    kept_events = base_stats.count
    symbol_support, symbol_consistent, symbol_rate = stability_rate(aggregate.symbol_returns, direction, 100)
    week_support, week_consistent, week_rate = stability_rate(aggregate.week_returns, direction, 50)
    month_support, month_consistent, month_rate = stability_rate(aggregate.month_returns, direction, 50)
    max_symbol_share = safe_div(max(aggregate.symbol_counts.values(), default=0), kept_events)
    max_week_share = safe_div(max(aggregate.week_counts.values(), default=0), kept_events)
    delay3_edge = None
    if aggregate.returns_by_delay[3].mean() is not None and aggregate.null_by_delay[3].mean() is not None and direction:
        delay3_edge = (aggregate.returns_by_delay[3].mean() - aggregate.null_by_delay[3].mean()) * direction
    delay5_edge = None
    if aggregate.returns_by_delay[5].mean() is not None and aggregate.null_by_delay[5].mean() is not None and direction:
        delay5_edge = (aggregate.returns_by_delay[5].mean() - aggregate.null_by_delay[5].mean()) * direction
    null_effect = aggregate.null_by_delay[0].mean()
    null_ok = null_effect is not None and sign_of(null_effect) == direction and sign_of(null_effect) != 0
    thin_share = safe_div(aggregate.thin_events, kept_events)
    return {
        "candidate_key": spec.key(),
        "category": spec.category,
        "horizon_seconds": spec.horizon_seconds,
        "cooldown_seconds": spec.cooldown_seconds,
        "capacity_subset": spec.capacity_subset,
        "phase": phase,
        "kept_events": kept_events,
        "locked_direction": direction,
        "candidate_mean_return": candidate_mean,
        "null_mean_return": null_mean,
        "effect_vs_null": effect,
        "edge_in_locked_direction": edge,
        "break_even_bps": break_even_bps,
        "delay3_edge_bps": delay3_edge * 10_000 if delay3_edge is not None else None,
        "delay5_edge_bps": delay5_edge * 10_000 if delay5_edge is not None else None,
        "survives_3bps_cost_at_3s_delay": bool(delay3_edge is not None and delay3_edge * 10_000 >= 3.0),
        "survives_2bps_cost_at_5s_delay": bool(delay5_edge is not None and delay5_edge * 10_000 >= 2.0),
        "symbol_support_count": symbol_support,
        "symbol_consistent_count": symbol_consistent,
        "symbol_stability_rate": symbol_rate,
        "month_support_count": month_support,
        "month_consistent_count": month_consistent,
        "month_stability_rate": month_rate,
        "week_support_count": week_support,
        "week_consistent_count": week_consistent,
        "week_stability_rate": week_rate,
        "single_symbol_kept_event_share": max_symbol_share,
        "single_week_kept_event_share": max_week_share,
        "thin_event_share": thin_share,
        "null_comparison_same_sign_nonzero": null_ok,
    }


def metric_pass_reasons(metrics: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if int(metrics.get("kept_events") or 0) < MIN_KEPT_EVENTS_PER_FOLD:
        reasons.append("kept_events_below_5000")
    if sign_of(metrics.get("edge_in_locked_direction")) <= 0:
        reasons.append("non_positive_locked_direction_edge")
    if (metrics.get("break_even_bps") or 0.0) < MIN_BREAK_EVEN_BPS:
        reasons.append("break_even_below_3bps")
    if not metrics.get("survives_3bps_cost_at_3s_delay"):
        reasons.append("fails_3bps_cost_at_3s_delay")
    if not metrics.get("survives_2bps_cost_at_5s_delay"):
        reasons.append("fails_2bps_cost_at_5s_delay")
    if (metrics.get("symbol_stability_rate") or 0.0) < MIN_SYMBOL_STABILITY:
        reasons.append("symbol_stability_below_0_65")
    if (metrics.get("month_stability_rate") or 0.0) < MIN_MONTH_STABILITY:
        reasons.append("month_stability_below_0_70")
    if (metrics.get("week_stability_rate") or 0.0) < MIN_WEEK_STABILITY:
        reasons.append("week_stability_below_0_65")
    if (metrics.get("single_symbol_kept_event_share") or 1.0) > MAX_SINGLE_SYMBOL_SHARE:
        reasons.append("single_symbol_share_above_25pct")
    if (metrics.get("single_week_kept_event_share") or 1.0) > MAX_SINGLE_WEEK_SHARE:
        reasons.append("single_week_share_above_15pct")
    if not metrics.get("null_comparison_same_sign_nonzero"):
        reasons.append("null_comparison_not_same_sign_nonzero")
    subset = str(metrics.get("capacity_subset", ""))
    thin_share = metrics.get("thin_event_share")
    if thin_share is not None and thin_share >= 0.95 and subset not in SMALL_CAP_ONLY_SUBSETS:
        reasons.append("thin_only_without_small_cap_only_classification")
    return reasons


def score_metrics(metrics: dict[str, Any]) -> float:
    kept = max(1, int(metrics.get("kept_events") or 0))
    break_even = float(metrics.get("break_even_bps") or 0.0)
    stability_values = [
        float(metrics.get("symbol_stability_rate") or 0.0),
        float(metrics.get("month_stability_rate") or 0.0),
        float(metrics.get("week_stability_rate") or 0.0),
    ]
    concentration_penalty = max(
        float(metrics.get("single_symbol_kept_event_share") or 0.0),
        float(metrics.get("single_week_kept_event_share") or 0.0),
    )
    return break_even * math.log10(kept + 10) * min(stability_values) * max(0.0, 1.0 - concentration_penalty)


def compact_metric_row(metrics: dict[str, Any], fold_id: int, promotion_stage: str, rank: int, reasons: list[str]) -> dict[str, Any]:
    row = {
        "fold_id": fold_id,
        "promotion_stage": promotion_stage,
        "rank": rank,
        "candidate_key": metrics.get("candidate_key", ""),
        "category": metrics.get("category", ""),
        "horizon_seconds": metrics.get("horizon_seconds", ""),
        "cooldown_seconds": metrics.get("cooldown_seconds", ""),
        "capacity_subset": metrics.get("capacity_subset", ""),
        "phase": metrics.get("phase", ""),
        "locked_direction": metrics.get("locked_direction", ""),
        "kept_events": metrics.get("kept_events", 0),
        "effect_vs_null": rounded(metrics.get("effect_vs_null"), 12),
        "break_even_bps": rounded(metrics.get("break_even_bps"), 6),
        "delay3_edge_bps": rounded(metrics.get("delay3_edge_bps"), 6),
        "delay5_edge_bps": rounded(metrics.get("delay5_edge_bps"), 6),
        "symbol_stability_rate": rounded(metrics.get("symbol_stability_rate"), 6),
        "month_stability_rate": rounded(metrics.get("month_stability_rate"), 6),
        "week_stability_rate": rounded(metrics.get("week_stability_rate"), 6),
        "single_symbol_share": rounded(metrics.get("single_symbol_kept_event_share"), 6),
        "single_week_share": rounded(metrics.get("single_week_kept_event_share"), 6),
        "thin_event_share": rounded(metrics.get("thin_event_share"), 6),
        "score": rounded(score_metrics(metrics), 8),
        "pass_gate": str(not reasons).lower(),
        "reject_reasons": ";".join(reasons),
    }
    return row


def classify_final(test_rows: list[dict[str, Any]]) -> str:
    if not test_rows:
        return "REJECTED_NO_ROBUST_EDGE"
    passed = [row for row in test_rows if str(row.get("pass_gate", "")).lower() == "true"]
    if not passed:
        return "REJECTED_NO_ROBUST_EDGE"
    if any(str(row.get("capacity_subset", "")) in SMALL_CAP_ONLY_SUBSETS for row in passed):
        return "SMALL_CAP_ALPHA_CANDIDATE"
    if any(str(row.get("capacity_subset", "")) in {"HIGH_ONLY", "HIGH_MEDIUM", "EXCLUDE_THIN", "ALL"} for row in passed):
        return "ROBUST_CAPACITY_AWARE_EDGE_CANDIDATE"
    return "FILTER_ONLY_CANDIDATE"


def write_empty_outputs(fold_rows: list[dict[str, Any]], grid: dict[str, Any]) -> None:
    write_csv(FOLD_PLAN_CSV, list(fold_rows[0].keys()), fold_rows)
    write_csv(
        TRIAL_LOG_CSV,
        [
            "fold_id",
            "promotion_stage",
            "rank",
            "candidate_key",
            "category",
            "horizon_seconds",
            "cooldown_seconds",
            "capacity_subset",
            "phase",
            "locked_direction",
            "kept_events",
            "effect_vs_null",
            "break_even_bps",
            "delay3_edge_bps",
            "delay5_edge_bps",
            "symbol_stability_rate",
            "month_stability_rate",
            "week_stability_rate",
            "single_symbol_share",
            "single_week_share",
            "thin_event_share",
            "score",
            "pass_gate",
            "reject_reasons",
        ],
        [],
    )
    for path in [RANKED_CANDIDATES_CSV, REJECTED_CANDIDATES_CSV, PROMOTED_CANDIDATES_CSV, WALK_FORWARD_RESULTS_CSV]:
        write_csv(path, [
            "fold_id",
            "promotion_stage",
            "rank",
            "candidate_key",
            "category",
            "horizon_seconds",
            "cooldown_seconds",
            "capacity_subset",
            "phase",
            "locked_direction",
            "kept_events",
            "effect_vs_null",
            "break_even_bps",
            "delay3_edge_bps",
            "delay5_edge_bps",
            "symbol_stability_rate",
            "month_stability_rate",
            "week_stability_rate",
            "single_symbol_share",
            "single_week_share",
            "thin_event_share",
            "score",
            "pass_gate",
            "reject_reasons",
        ], [])
    multiple = multiple_testing_report(grid, full_search_run=False, fold_count=len(fold_rows), candidates_tested=0)
    MULTIPLE_TESTING_JSON.write_text(json.dumps(multiple, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def multiple_testing_report(
    grid: dict[str, Any],
    full_search_run: bool,
    fold_count: int,
    candidates_tested: int,
) -> dict[str, Any]:
    return {
        "task": TASK_NAME,
        "created_at_utc": utc_now_text(),
        "full_search_run": full_search_run,
        "fixed_grid_sha256": grid["fixed_grid_sha256"],
        "base_candidate_count": grid["base_candidate_count"],
        "full_stress_grid_count": grid["full_stress_grid_count"],
        "fold_count": fold_count,
        "candidate_fold_tests_logged": candidates_tested,
        "familywise_control_method": "hard_holdout_gates_plus_walk_forward_test_used_once",
        "promotion_limits": {
            "discovery_to_validation_max": DISCOVERY_PROMOTION_LIMIT,
            "validation_to_test_max": VALIDATION_PROMOTION_LIMIT,
        },
        "adaptivity_controls": [
            "grid_declared_before search",
            "discovery ranks only frozen candidates",
            "max 20 promoted to validation",
            "max 5 promoted to test",
            "test rows are evaluated only after validation promotion",
            "direction is inferred in discovery and locked",
            "no post-failure filter or threshold edits",
        ],
    }


def run_smoke() -> dict[str, Any]:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    grid = grid_payload()
    fold_rows = build_fold_plan()
    FIXED_GRID_JSON.write_text(json.dumps(grid, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_empty_outputs(fold_rows, grid)
    summary = {
        "status": "PASS_ANTI_OVERFIT_ALPHA_SEARCH_PROTOCOL_SMOKE_ONLY",
        "final_classification": "REJECTED_NO_ROBUST_EDGE",
        "classification_reason": "smoke mode only; full search did not run because env gate was not set",
        "created_at_utc": utc_now_text(),
        "task": TASK_NAME,
        "mode": "SMOKE_ONLY",
        "full_search_env_var": RUN_ENV,
        "full_search_env_value": os.environ.get(RUN_ENV, ""),
        "full_search_run": False,
        "env_gate_respected": not bool_env(RUN_ENV),
        "fixed_grid_sha256": grid["fixed_grid_sha256"],
        "fixed_grid_base_candidate_count": grid["base_candidate_count"],
        "fixed_grid_full_stress_grid_count": grid["full_stress_grid_count"],
        "fold_count": len(fold_rows),
        "coverage_start": COVERAGE_START.isoformat(),
        "coverage_end": COVERAGE_END.isoformat(),
        "raw_bookdepth_root": str(BOOKDEPTH_RAW_ROOT),
        "raw_aggtrades_root": str(AGGTRADES_RAW_ROOT),
        "raw_roots_outside_repo": not path_is_inside(BOOKDEPTH_RAW_ROOT, REPO_ROOT)
        and not path_is_inside(AGGTRADES_RAW_ROOT, REPO_ROOT),
        "downloads_run": False,
        "row_level_dataset_created": False,
        "full_parquet_dataset_created": False,
        "trading_or_order_logic": False,
        "private_endpoint_logic": False,
        "pnl_curve_created": False,
        "recommendations_created": False,
        "direction_locked": True,
        "promotion_limits_enforced": True,
        "test_used_in_discovery": False,
        "rejected_candidates_logged": True,
        "outputs": output_paths(),
    }
    write_summary(summary)
    return summary


def run_full_search() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    grid = grid_payload()
    fold_rows = build_fold_plan()
    specs = list(iter_candidate_specs())
    FIXED_GRID_JSON.write_text(json.dumps(grid, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(FOLD_PLAN_CSV, list(fold_rows[0].keys()), fold_rows)
    pairs = load_verified_pairs()

    trial_rows: list[dict[str, Any]] = []
    ranked_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    promoted_rows: list[dict[str, Any]] = []
    walk_rows: list[dict[str, Any]] = []
    phase_metadata: list[dict[str, Any]] = []

    spec_by_key = {spec.key(): spec for spec in specs}
    for fold in fold_rows:
        fold_id = int(fold["fold_id"])
        discovery_pairs = pairs_for_window(pairs, str(fold["discovery_start"]), str(fold["discovery_end"]))
        validation_pairs = pairs_for_window(pairs, str(fold["validation_start"]), str(fold["validation_end"]))
        test_pairs = pairs_for_window(pairs, str(fold["test_start"]), str(fold["test_end"]))

        capacity_plan = build_capacity_plan(discovery_pairs)
        discovery_aggregates, discovery_meta = aggregate_window("discovery", discovery_pairs, specs, capacity_plan)
        phase_metadata.append({"fold_id": fold_id, **discovery_meta})
        discovery_metrics = [
            metrics_for_aggregate(spec, "discovery", discovery_aggregates[spec.key()])
            for spec in specs
        ]
        discovery_metrics = [item for item in discovery_metrics if sign_of(item.get("effect_vs_null")) != 0]
        discovery_metrics.sort(key=score_metrics, reverse=True)
        for rank, metrics in enumerate(discovery_metrics, start=1):
            reasons = metric_pass_reasons(metrics)
            row = compact_metric_row(metrics, fold_id, "DISCOVERY_RANK", rank, reasons)
            trial_rows.append(row)
            ranked_rows.append(row)
            if reasons:
                rejected_rows.append({**row, "promotion_stage": "DISCOVERY_REJECT"})
        discovery_promoted = discovery_metrics[:DISCOVERY_PROMOTION_LIMIT]
        for rank, metrics in enumerate(discovery_promoted, start=1):
            reasons = metric_pass_reasons(metrics)
            row = compact_metric_row(metrics, fold_id, "PROMOTED_TO_VALIDATION", rank, reasons)
            promoted_rows.append(row)

        validation_specs = [spec_by_key[str(item["candidate_key"])] for item in discovery_promoted]
        locked_direction = {str(item["candidate_key"]): int(item["locked_direction"]) for item in discovery_promoted}
        validation_aggregates, validation_meta = aggregate_window("validation", validation_pairs, validation_specs, capacity_plan)
        phase_metadata.append({"fold_id": fold_id, **validation_meta})
        validation_metrics = []
        for spec in validation_specs:
            metrics = metrics_for_aggregate(
                spec,
                "validation",
                validation_aggregates[spec.key()],
                locked_direction=locked_direction[spec.key()],
            )
            validation_metrics.append(metrics)
        validation_metrics.sort(key=score_metrics, reverse=True)
        validation_passed = []
        for rank, metrics in enumerate(validation_metrics, start=1):
            reasons = metric_pass_reasons(metrics)
            row = compact_metric_row(metrics, fold_id, "VALIDATION_LOCKED_DIRECTION", rank, reasons)
            walk_rows.append(row)
            if reasons:
                rejected_rows.append({**row, "promotion_stage": "VALIDATION_REJECT"})
            else:
                validation_passed.append(metrics)
        test_promoted = validation_passed[:VALIDATION_PROMOTION_LIMIT]
        for rank, metrics in enumerate(test_promoted, start=1):
            row = compact_metric_row(metrics, fold_id, "PROMOTED_TO_TEST", rank, [])
            promoted_rows.append(row)

        test_specs = [spec_by_key[str(item["candidate_key"])] for item in test_promoted]
        test_aggregates, test_meta = aggregate_window("test", test_pairs, test_specs, capacity_plan)
        phase_metadata.append({"fold_id": fold_id, **test_meta})
        for rank, spec in enumerate(test_specs, start=1):
            metrics = metrics_for_aggregate(
                spec,
                "test",
                test_aggregates[spec.key()],
                locked_direction=locked_direction[spec.key()],
            )
            reasons = metric_pass_reasons(metrics)
            row = compact_metric_row(metrics, fold_id, "TEST_USED_ONCE", rank, reasons)
            walk_rows.append(row)
            if reasons:
                rejected_rows.append({**row, "promotion_stage": "TEST_REJECT"})

    write_csv(TRIAL_LOG_CSV, list(trial_rows[0].keys()) if trial_rows else [], trial_rows)
    write_csv(RANKED_CANDIDATES_CSV, list(trial_rows[0].keys()) if trial_rows else [], ranked_rows)
    write_csv(REJECTED_CANDIDATES_CSV, list(trial_rows[0].keys()) if trial_rows else [], rejected_rows)
    write_csv(PROMOTED_CANDIDATES_CSV, list(trial_rows[0].keys()) if trial_rows else [], promoted_rows)
    write_csv(WALK_FORWARD_RESULTS_CSV, list(trial_rows[0].keys()) if trial_rows else [], walk_rows)
    MULTIPLE_TESTING_JSON.write_text(
        json.dumps(
            multiple_testing_report(grid, full_search_run=True, fold_count=len(fold_rows), candidates_tested=len(trial_rows)),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    final_classification = classify_final(walk_rows)
    summary = {
        "status": "PASS_ANTI_OVERFIT_ALPHA_SEARCH_PROTOCOL_FULL_SEARCH_COMPLETED",
        "final_classification": final_classification,
        "created_at_utc": utc_now_text(),
        "task": TASK_NAME,
        "mode": "FULL_SEARCH",
        "full_search_env_var": RUN_ENV,
        "full_search_env_value": os.environ.get(RUN_ENV, ""),
        "full_search_run": True,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "fixed_grid_sha256": grid["fixed_grid_sha256"],
        "fixed_grid_base_candidate_count": grid["base_candidate_count"],
        "fixed_grid_full_stress_grid_count": grid["full_stress_grid_count"],
        "fold_count": len(fold_rows),
        "verified_pair_count": len(pairs),
        "selected_symbol_count": len({pair["symbol"] for pair in pairs}),
        "phase_metadata": phase_metadata,
        "trial_log_rows": len(trial_rows),
        "ranked_candidate_rows": len(ranked_rows),
        "rejected_candidate_rows": len(rejected_rows),
        "promoted_candidate_rows": len(promoted_rows),
        "walk_forward_rows": len(walk_rows),
        "raw_roots_outside_repo": not path_is_inside(BOOKDEPTH_RAW_ROOT, REPO_ROOT)
        and not path_is_inside(AGGTRADES_RAW_ROOT, REPO_ROOT),
        "downloads_run": False,
        "row_level_dataset_created": False,
        "full_parquet_dataset_created": False,
        "trading_or_order_logic": False,
        "private_endpoint_logic": False,
        "pnl_curve_created": False,
        "recommendations_created": False,
        "direction_locked": True,
        "promotion_limits_enforced": True,
        "test_used_in_discovery": False,
        "rejected_candidates_logged": bool(rejected_rows),
        "outputs": output_paths(),
    }
    write_summary(summary)
    return summary


def output_paths() -> dict[str, str]:
    return {
        "summary_json": str(SUMMARY_JSON),
        "summary_md": str(SUMMARY_MD),
        "fixed_grid_json": str(FIXED_GRID_JSON),
        "fold_plan_csv": str(FOLD_PLAN_CSV),
        "trial_log_csv": str(TRIAL_LOG_CSV),
        "ranked_candidates_csv": str(RANKED_CANDIDATES_CSV),
        "rejected_candidates_csv": str(REJECTED_CANDIDATES_CSV),
        "promoted_candidates_csv": str(PROMOTED_CANDIDATES_CSV),
        "walk_forward_results_csv": str(WALK_FORWARD_RESULTS_CSV),
        "multiple_testing_report_json": str(MULTIPLE_TESTING_JSON),
    }


def output_sizes() -> dict[str, int]:
    paths = [
        SUMMARY_JSON,
        SUMMARY_MD,
        FIXED_GRID_JSON,
        FOLD_PLAN_CSV,
        TRIAL_LOG_CSV,
        RANKED_CANDIDATES_CSV,
        REJECTED_CANDIDATES_CSV,
        PROMOTED_CANDIDATES_CSV,
        WALK_FORWARD_RESULTS_CSV,
        MULTIPLE_TESTING_JSON,
    ]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Anti-overfit alpha search protocol v1",
        "",
        f"status: {summary['status']}",
        f"mode: {summary['mode']}",
        f"final_classification: {summary['final_classification']}",
        f"full_search_run: {str(summary['full_search_run']).lower()}",
        f"fixed_grid_full_stress_grid_count: {summary['fixed_grid_full_stress_grid_count']}",
        f"fold_count: {summary['fold_count']}",
        f"env_gate_respected: {str(summary.get('env_gate_respected', True)).lower()}",
        "",
        "## Anti-overfit safeguards",
        "- fixed grid is written before any full search",
        "- discovery ranks only frozen candidates",
        "- validation promotion is capped at 20 per fold",
        "- test promotion is capped at 5 per fold",
        "- direction is inferred only in discovery and locked afterward",
        "- test windows are evaluated only after locked validation promotion",
        "- rejected candidates are logged",
        "- diagnostics only: no downloads, no row-level dataset, no private endpoints, no orders",
        "",
        "## Outputs",
    ]
    for name, path in summary["outputs"].items():
        lines.append(f"- {name}: {Path(path).name}")
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary(summary: dict[str, Any]) -> None:
    summary["output_sizes_bytes"] = output_sizes()
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    summary["output_sizes_bytes"] = output_sizes()
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    try:
        if bool_env(RUN_ENV):
            summary = run_full_search()
        else:
            summary = run_smoke()
    except Exception as exc:  # noqa: BLE001
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        summary = {
            "status": "FAILED_ANTI_OVERFIT_ALPHA_SEARCH_PROTOCOL",
            "final_classification": "REJECTED_NO_ROBUST_EDGE",
            "created_at_utc": utc_now_text(),
            "task": TASK_NAME,
            "error": f"{type(exc).__name__}: {exc}",
            "full_search_run": bool_env(RUN_ENV),
            "downloads_run": False,
            "row_level_dataset_created": False,
            "trading_or_order_logic": False,
            "private_endpoint_logic": False,
            "outputs": output_paths(),
        }
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Anti-overfit alpha search protocol v1\n\n"
            f"status: {summary['status']}\n"
            f"final_classification: {summary['final_classification']}\n"
            f"error: {summary['error']}\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(summary.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
