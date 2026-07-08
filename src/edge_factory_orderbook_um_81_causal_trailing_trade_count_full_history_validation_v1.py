#!/usr/bin/env python
"""Full-history validation for causal trailing trade-count filtered SELL_PRESSURE_ABSORBED@300s."""

from __future__ import annotations

import csv
import json
import math
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import edge_factory_orderbook_um_81_causal_capacity_filter_repair_v1 as repair
import edge_factory_orderbook_um_81_sell_pressure_absorbed_execution_delay_capacity_diagnostic_v1 as prior


base = prior.base
price_linkage = prior.price_linkage

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"
PREFIX = "orderbook_um_81_causal_trailing_trade_count_full_history_validation"

SUMMARY_JSON = OUTPUTS_DIR / f"{PREFIX}_summary.json"
SUMMARY_MD = OUTPUTS_DIR / f"{PREFIX}_summary.md"
PERIOD_STABILITY_CSV = OUTPUTS_DIR / f"{PREFIX}_period_stability.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / f"{PREFIX}_symbol_stability.csv"
DELAY_COST_GRID_CSV = OUTPUTS_DIR / f"{PREFIX}_delay_cost_grid.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / f"{PREFIX}_null_comparison.csv"
CHUNK_PROGRESS_CSV = OUTPUTS_DIR / f"{PREFIX}_chunk_progress.csv"
COMPLETED_CHUNKS_MANIFEST_JSON = OUTPUTS_DIR / f"{PREFIX}_completed_chunks_manifest.json"
PARTIAL_AGGREGATE_SUMMARIES_JSON = OUTPUTS_DIR / f"{PREFIX}_partial_aggregate_summaries.json"
CHUNK_OUTPUT_DIR = OUTPUTS_DIR / f"{PREFIX}_chunks"

LOCKED_CATEGORY = prior.LOCKED_CATEGORY
LOCKED_HORIZON_SECONDS = prior.LOCKED_HORIZON_SECONDS
LOCKED_COOLDOWN_SECONDS = prior.LOCKED_COOLDOWN_SECONDS
OBSERVED_PRICE_DIRECTION = prior.OBSERVED_PRICE_DIRECTION
LOCKED_FILTER_NAME = repair.trailing_trade_count_filter_name(60, 100)
LOCKED_FILTER_LOOKBACK_SECONDS = 60
LOCKED_FILTER_MIN_TRADE_COUNT = 100

START_DATE = "2023-01-01"
END_DATE = "2026-06-15"
FULL_SCOPE_VALUE = f"{START_DATE}_TO_{END_DATE}"
LATEST_WINDOW_DAYS = 90
HOLDOUT_WINDOW_DAYS = 90
EXPECTED_SYMBOL_COUNT = 81
EXPECTED_SYMBOL_DAYS = 99_404
DELAY_SECONDS = [0, 1, 3, 5, 10]
COST_GRID_BPS = [0.0, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0]
WINDOW_SCOPE_VALUES = ["LATEST_90D", "HOLDOUT_90D", "OLDER_HISTORY"]
MIN_EVENT_COUNT = 100
MIN_PERIOD_EVENT_COUNT = 50
MIN_SYMBOL_EVENT_COUNT = 100
MIN_STABILITY_RATE = 0.5
RESERVOIR_LIMIT = 50_000
PROGRESS_INTERVAL_SECONDS = 30
CHUNK_PERIOD_ENV = "ORDERBOOK_FULL_HISTORY_CHUNK_PERIOD"
CHUNK_LIMIT_ENV = "ORDERBOOK_FULL_HISTORY_CHUNK_LIMIT"
CHUNK_WORKERS_ENV = "ORDERBOOK_FULL_HISTORY_CHUNK_WORKERS"
DEFAULT_CHUNK_PERIOD = "month"
MAX_CHUNK_WORKERS = 4


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def int_value(value: Any, default: int = 0) -> int:
    return base.int_value(value, default)


def rounded(value: float | None, places: int = 12) -> float | str:
    if value is None or math.isnan(value):
        return ""
    return round(value, places)


def rounded_bps(value: float | None) -> float | str:
    return rounded(value, 6)


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def sign_of(value: float | None, tolerance: float = 1e-12) -> int:
    if value is None or abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1


def candidate_label() -> str:
    return f"{LOCKED_CATEGORY}@{LOCKED_HORIZON_SECONDS}s"


def observed_direction_text() -> str:
    return "NEGATIVE_PRICE_EFFECT" if OBSERVED_PRICE_DIRECTION < 0 else "POSITIVE_PRICE_EFFECT"


def quarter_text(file_date: str) -> str:
    year = file_date[:4]
    month = int_value(file_date[5:7], 1)
    quarter = ((month - 1) // 3) + 1
    return f"{year}-Q{quarter}"


def chunk_period() -> str:
    value = os.environ.get(CHUNK_PERIOD_ENV, DEFAULT_CHUNK_PERIOD).strip().lower()
    return value if value in {"month", "quarter"} else DEFAULT_CHUNK_PERIOD


def chunk_limit() -> int | None:
    raw = os.environ.get(CHUNK_LIMIT_ENV, "").strip()
    if not raw:
        return None
    value = int_value(raw, 0)
    return value if value > 0 else None


def requested_chunk_workers() -> int:
    raw = os.environ.get(CHUNK_WORKERS_ENV, "1").strip()
    return max(1, min(MAX_CHUNK_WORKERS, int_value(raw, 1)))


def effective_chunk_workers(requested_workers: int) -> int:
    # Exact cooldown carry-forward is chronological, so parallel chunk execution is disabled.
    return 1 if requested_workers >= 1 else 1


def chunk_id_for_date(file_date: str, period: str) -> str:
    return quarter_text(file_date) if period == "quarter" else file_date[:7]


def chunk_sort_key(chunk_id: str, period: str) -> tuple[int, int]:
    if period == "quarter" and "-Q" in chunk_id:
        year_text, quarter = chunk_id.split("-Q", 1)
        return int_value(year_text), (int_value(quarter, 1) - 1) * 3 + 1
    return int_value(chunk_id[:4]), int_value(chunk_id[5:7], 1)


def chunk_file_path(chunk_id: str) -> Path:
    safe_id = chunk_id.replace("/", "_")
    return CHUNK_OUTPUT_DIR / f"{PREFIX}_{safe_id}_chunk_summary.json"


def build_chunks(pairs: list[dict[str, Any]], period: str) -> list[dict[str, Any]]:
    by_chunk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        by_chunk[chunk_id_for_date(str(pair["file_date"]), period)].append(pair)
    chunks: list[dict[str, Any]] = []
    for chunk_id in sorted(by_chunk, key=lambda item: chunk_sort_key(item, period)):
        chunk_pairs = sorted(by_chunk[chunk_id], key=lambda row: (str(row["symbol"]), str(row["file_date"])))
        dates = sorted({str(pair["file_date"]) for pair in chunk_pairs})
        chunks.append(
            {
                "chunk_id": chunk_id,
                "period": period,
                "start_date": dates[0],
                "end_date": dates[-1],
                "pair_count": len(chunk_pairs),
                "pairs": chunk_pairs,
                "path": chunk_file_path(chunk_id),
            }
        )
    return chunks


def fresh_distribution(seed_text: str) -> base.DistributionStats:
    return base.DistributionStats(sample_limit=RESERVOIR_LIMIT, seed_text=seed_text)


def get_distribution(
    stats: dict[tuple[Any, ...], base.DistributionStats],
    key: tuple[Any, ...],
) -> base.DistributionStats:
    if key not in stats:
        stats[key] = fresh_distribution(":".join(str(part) for part in key))
    return stats[key]


def locked_causal_trailing_trade_count(event_ms: int, trade_times: list[int]) -> int:
    return repair.trailing_trade_count_before_event(event_ms, LOCKED_FILTER_LOOKBACK_SECONDS, trade_times)


def passes_locked_causal_filter(event_ms: int, trade_times: list[int]) -> bool:
    return locked_causal_trailing_trade_count(event_ms, trade_times) >= LOCKED_FILTER_MIN_TRADE_COUNT


def load_full_history_pairs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    book_rows = base.load_verified_paths(base.BOOKDEPTH_FILE_STATUS_CSV, base.DEFAULT_BOOKDEPTH_RAW_ROOT)
    agg_rows = base.load_verified_paths(base.AGGTRADES_FILE_STATUS_CSV, base.DEFAULT_AGGTRADES_RAW_ROOT)
    by_symbol: dict[str, list[str]] = defaultdict(list)
    for symbol, file_date in sorted(set(book_rows) & set(agg_rows)):
        if START_DATE <= file_date <= END_DATE:
            by_symbol[symbol].append(file_date)

    pairs: list[dict[str, Any]] = []
    symbol_details: dict[str, Any] = {}
    for symbol in sorted(by_symbol):
        ascending_dates = sorted(by_symbol[symbol])
        descending_dates = list(reversed(ascending_dates))
        latest_set = set(descending_dates[:LATEST_WINDOW_DAYS])
        holdout_set = set(descending_dates[LATEST_WINDOW_DAYS : LATEST_WINDOW_DAYS + HOLDOUT_WINDOW_DAYS])
        symbol_details[symbol] = {
            "days_available": len(ascending_dates),
            "oldest": ascending_dates[0] if ascending_dates else "",
            "newest": ascending_dates[-1] if ascending_dates else "",
        }
        for file_date in ascending_dates:
            if file_date in latest_set:
                validation_window = "LATEST_90D"
            elif file_date in holdout_set:
                validation_window = "HOLDOUT_90D"
            else:
                validation_window = "OLDER_HISTORY"
            key = (symbol, file_date)
            pairs.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "year": file_date[:4],
                    "year_month": file_date[:7],
                    "quarter": quarter_text(file_date),
                    "week": base.iso_week_text(file_date),
                    "validation_window": validation_window,
                    "bookdepth_zip_path": book_rows[key]["local_zip_path"],
                    "aggtrades_zip_path": agg_rows[key]["local_zip_path"],
                }
            )
    return pairs, {"symbol_details": symbol_details}


def add_scope_value(
    stats: dict[tuple[Any, ...], base.DistributionStats],
    scope_value: str,
    delay: int,
    value: float,
) -> None:
    get_distribution(stats, (scope_value, delay)).add_diagnostic(
        value,
        OBSERVED_PRICE_DIRECTION,
        "UNUSED",
        None,
        None,
        None,
    )


def add_candidate_value(
    value: float,
    pair: dict[str, Any],
    delay: int,
    candidate_scope_stats: dict[tuple[Any, ...], base.DistributionStats],
    candidate_period_stats: dict[tuple[str, str, int], base.MomentStats],
    candidate_symbol_stats: dict[tuple[str, int], base.MomentStats],
) -> None:
    window = str(pair["validation_window"])
    add_scope_value(candidate_scope_stats, FULL_SCOPE_VALUE, delay, value)
    add_scope_value(candidate_scope_stats, window, delay, value)
    symbol = str(pair["symbol"])
    candidate_symbol_stats[(symbol, delay)].add(value, OBSERVED_PRICE_DIRECTION)
    for period_type, period_value in [
        ("YEAR", str(pair["year"])),
        ("QUARTER", str(pair["quarter"])),
        ("MONTH", str(pair["year_month"])),
        ("WEEK", str(pair["week"])),
        ("WINDOW", window),
    ]:
        candidate_period_stats[(period_type, period_value, delay)].add(value, OBSERVED_PRICE_DIRECTION)


def add_null_value(
    value: float,
    pair: dict[str, Any],
    delay: int,
    null_scope_stats: dict[tuple[Any, ...], base.DistributionStats],
    null_period_stats: dict[tuple[str, str, int], base.MomentStats],
    null_symbol_stats: dict[tuple[str, int], base.MomentStats],
) -> None:
    window = str(pair["validation_window"])
    add_scope_value(null_scope_stats, FULL_SCOPE_VALUE, delay, value)
    add_scope_value(null_scope_stats, window, delay, value)
    symbol = str(pair["symbol"])
    null_symbol_stats[(symbol, delay)].add(value, OBSERVED_PRICE_DIRECTION)
    for period_type, period_value in [
        ("YEAR", str(pair["year"])),
        ("QUARTER", str(pair["quarter"])),
        ("MONTH", str(pair["year_month"])),
        ("WEEK", str(pair["week"])),
        ("WINDOW", window),
    ]:
        null_period_stats[(period_type, period_value, delay)].add(value, OBSERVED_PRICE_DIRECTION)


def process_full_history(
    pairs: list[dict[str, Any]],
    initial_candidate_last_kept_ms: dict[str, int] | None = None,
    initial_null_last_kept_ms: dict[tuple[str, int], int] | None = None,
    progress_label: str = "full_history",
) -> dict[str, Any]:
    started = time.monotonic()
    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows = 0
    original_candidate_row_count = 0
    original_valid_event_count = 0
    kept_non_overlap_event_count = 0
    event_count_after_causal_filter = 0
    null_original_event_count = 0
    category_counts: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    last_candidate_kept_ms: dict[str, int] = dict(initial_candidate_last_kept_ms or {})
    last_null_kept_ms: dict[tuple[str, int], int] = dict(initial_null_last_kept_ms or {})
    candidate_scope_stats: dict[tuple[Any, ...], base.DistributionStats] = {}
    candidate_period_stats: dict[tuple[str, str, int], base.MomentStats] = defaultdict(base.MomentStats)
    candidate_symbol_stats: dict[tuple[str, int], base.MomentStats] = defaultdict(base.MomentStats)
    null_scope_stats: dict[tuple[Any, ...], base.DistributionStats] = {}
    null_period_stats: dict[tuple[str, str, int], base.MomentStats] = defaultdict(base.MomentStats)
    null_symbol_stats: dict[tuple[str, int], base.MomentStats] = defaultdict(base.MomentStats)
    filter_trade_count_examples: Counter[str] = Counter()
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    for pair in pairs:
        try:
            timestamps, rows, trade_times, trade_prices, _trade_notionals, _prefix_notionals = prior.read_features_trade_details(pair)
            processed_symbol_days += 1
            total_feature_rows += len(rows)
            symbol = str(pair["symbol"])
            for index, row in enumerate(rows):
                event_ms = timestamps[index]
                category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
                if category not in base.CATEGORIES:
                    category = "INSUFFICIENT_DATA"
                category_counts[category] += 1
                passes_filter = passes_locked_causal_filter(event_ms, trade_times)

                if passes_filter:
                    for delay in DELAY_SECONDS:
                        null_key = (symbol, delay)
                        if not prior.may_keep_event(last_null_kept_ms.get(null_key), event_ms):
                            continue
                        price_return = prior.delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                        if price_return is None:
                            continue
                        null_original_event_count += 1
                        last_null_kept_ms[null_key] = event_ms
                        add_null_value(
                            price_return,
                            pair,
                            delay,
                            null_scope_stats,
                            null_period_stats,
                            null_symbol_stats,
                        )

                if category != LOCKED_CATEGORY:
                    continue
                original_candidate_row_count += 1
                base_return = prior.delayed_forward_price_return(event_ms, 0, trade_times, trade_prices)
                if base_return is None:
                    continue
                original_valid_event_count += 1
                if not prior.may_keep_event(last_candidate_kept_ms.get(symbol), event_ms):
                    continue
                last_candidate_kept_ms[symbol] = event_ms
                kept_non_overlap_event_count += 1
                if not passes_filter:
                    continue
                event_count_after_causal_filter += 1
                count_bucket = min(500, (locked_causal_trailing_trade_count(event_ms, trade_times) // 50) * 50)
                filter_trade_count_examples[str(count_bucket)] += 1
                for delay in DELAY_SECONDS:
                    price_return = prior.delayed_forward_price_return(event_ms, delay, trade_times, trade_prices)
                    if price_return is None:
                        continue
                    add_candidate_value(
                        price_return,
                        pair,
                        delay,
                        candidate_scope_stats,
                        candidate_period_stats,
                        candidate_symbol_stats,
                    )
        except Exception as exc:  # noqa: BLE001
            failed_symbol_days += 1
            if len(failure_examples) < 30:
                failure_examples.append(
                    {
                        "symbol": str(pair.get("symbol", "")),
                        "file_date": str(pair.get("file_date", "")),
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )

        if time.monotonic() >= next_progress:
            print(
                "progress phase=causal_trailing_trade_count_full_history "
                f"chunk={progress_label} "
                f"processed_symbol_days={processed_symbol_days}/{len(pairs)} "
                f"failed_symbol_days={failed_symbol_days} feature_rows={total_feature_rows} "
                f"filtered_events={event_count_after_causal_filter} "
                f"elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    return {
        "processed_symbol_days": processed_symbol_days,
        "failed_symbol_days": failed_symbol_days,
        "total_feature_rows": total_feature_rows,
        "original_candidate_row_count": original_candidate_row_count,
        "original_valid_event_count": original_valid_event_count,
        "kept_non_overlap_event_count": kept_non_overlap_event_count,
        "event_count_after_causal_filter": event_count_after_causal_filter,
        "null_original_event_count": null_original_event_count,
        "category_counts": dict(category_counts),
        "filter_trade_count_bucket_counts": dict(filter_trade_count_examples),
        "failure_examples": failure_examples,
        "candidate_scope_stats": candidate_scope_stats,
        "candidate_period_stats": candidate_period_stats,
        "candidate_symbol_stats": candidate_symbol_stats,
        "null_scope_stats": null_scope_stats,
        "null_period_stats": null_period_stats,
        "null_symbol_stats": null_symbol_stats,
        "ending_candidate_last_kept_ms": last_candidate_kept_ms,
        "ending_null_last_kept_ms": last_null_kept_ms,
    }


def empty_distribution(seed_text: str) -> base.DistributionStats:
    return fresh_distribution(f"empty:{seed_text}")


def stat_payload(stat: base.MomentStats) -> dict[str, Any]:
    payload = {
        "row_count": stat.row_count,
        "valid_forward_count": stat.valid_forward_count,
        "sum_value": stat.sum_value,
        "sum_square": stat.sum_square,
        "min_value": stat.min_value,
        "max_value": stat.max_value,
        "directional_total": stat.directional_total,
        "directional_match": stat.directional_match,
    }
    if isinstance(stat, base.DistributionStats):
        payload["reservoir"] = stat.reservoir
    return payload


def stats_payload(stats: dict[tuple[Any, ...], base.MomentStats]) -> dict[str, dict[str, Any]]:
    return {json.dumps(list(key), separators=(",", ":")): stat_payload(stat) for key, stat in sorted(stats.items())}


def merge_payload_into_stat(accumulator: base.MomentStats, payload: dict[str, Any]) -> None:
    accumulator.row_count += int_value(payload.get("row_count"))
    accumulator.valid_forward_count += int_value(payload.get("valid_forward_count"))
    accumulator.sum_value += float(payload.get("sum_value") or 0.0)
    accumulator.sum_square += float(payload.get("sum_square") or 0.0)
    min_value = payload.get("min_value")
    max_value = payload.get("max_value")
    if min_value is not None:
        accumulator.min_value = (
            float(min_value) if accumulator.min_value is None else min(accumulator.min_value, float(min_value))
        )
    if max_value is not None:
        accumulator.max_value = (
            float(max_value) if accumulator.max_value is None else max(accumulator.max_value, float(max_value))
        )
    accumulator.directional_total += int_value(payload.get("directional_total"))
    accumulator.directional_match += int_value(payload.get("directional_match"))
    if isinstance(accumulator, base.DistributionStats):
        for value in payload.get("reservoir", []) or []:
            if len(accumulator.reservoir) >= accumulator.sample_limit:
                break
            accumulator.reservoir.append(float(value))


def merge_stats_payload(
    accumulators: dict[tuple[Any, ...], base.MomentStats],
    payloads: dict[str, dict[str, Any]],
    distribution: bool,
) -> None:
    for key_text, payload in payloads.items():
        key = tuple(json.loads(key_text))
        if key not in accumulators:
            accumulators[key] = fresh_distribution(key_text) if distribution else base.MomentStats()
        merge_payload_into_stat(accumulators[key], payload)


def serialize_null_state(state: dict[tuple[str, int], int]) -> dict[str, int]:
    return {f"{symbol}|{delay}": value for (symbol, delay), value in sorted(state.items())}


def deserialize_null_state(state: dict[str, Any]) -> dict[tuple[str, int], int]:
    result: dict[tuple[str, int], int] = {}
    for key, value in state.items():
        symbol, delay_text = str(key).rsplit("|", 1)
        result[(symbol, int_value(delay_text))] = int_value(value)
    return result


def metric_row(
    scope_type: str,
    scope_value: str,
    delay: int,
    candidate_stats: base.MomentStats,
    null_stats: base.MomentStats,
    original_event_count: int | None = None,
    original_row_count: int | None = None,
) -> dict[str, Any]:
    candidate_mean = candidate_stats.mean()
    null_mean = null_stats.mean()
    effect = candidate_mean - null_mean if candidate_mean is not None and null_mean is not None else None
    gross_edge = effect * OBSERVED_PRICE_DIRECTION if effect is not None else None
    break_even = max(0.0, gross_edge * 10_000) if gross_edge is not None else None
    median_value = candidate_stats.sampled_median() if isinstance(candidate_stats, base.DistributionStats) else None
    return {
        "scope_type": scope_type,
        "scope_value": scope_value,
        "candidate": candidate_label(),
        "locked_filter": LOCKED_FILTER_NAME,
        "filter_definition": "[event_ms - 60s, event_ms) aggTrades count >= 100",
        "category": LOCKED_CATEGORY,
        "horizon_seconds": LOCKED_HORIZON_SECONDS,
        "cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "delay_seconds": delay,
        "observed_direction": observed_direction_text(),
        "original_candidate_row_count": "" if original_row_count is None else original_row_count,
        "original_valid_event_count": "" if original_event_count is None else original_event_count,
        "kept_event_count": candidate_stats.valid_forward_count,
        "retention_rate": rounded(safe_div(candidate_stats.valid_forward_count, original_event_count), 6)
        if original_event_count is not None
        else "",
        "gross_mean_forward_price_return": rounded(candidate_mean),
        "gross_median_forward_price_return": rounded(median_value),
        "gross_std_forward_price_return": rounded(candidate_stats.std()),
        "null_event_count": null_stats.valid_forward_count,
        "null_mean_forward_price_return": rounded(null_mean),
        "null_std_forward_price_return": rounded(null_stats.std()),
        "gross_effect_vs_null_signed": rounded(effect),
        "gross_edge_observed_direction": rounded(gross_edge),
        "break_even_cost_bps": rounded_bps(break_even),
        "directional_diagnostic_rate": rounded(candidate_stats.directional_rate(), 6),
        "consistent_with_observed_direction": str(sign_of(effect) == OBSERVED_PRICE_DIRECTION).lower(),
    }


def build_scope_rows(processed: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidate_scope_stats = processed["candidate_scope_stats"]
    null_scope_stats = processed["null_scope_stats"]
    for delay in DELAY_SECONDS:
        rows.append(
            metric_row(
                "FULL_HISTORY",
                FULL_SCOPE_VALUE,
                delay,
                candidate_scope_stats.get((FULL_SCOPE_VALUE, delay), empty_distribution(f"candidate:{FULL_SCOPE_VALUE}:{delay}")),
                null_scope_stats.get((FULL_SCOPE_VALUE, delay), empty_distribution(f"null:{FULL_SCOPE_VALUE}:{delay}")),
                processed["event_count_after_causal_filter"],
                processed["original_candidate_row_count"],
            )
        )
        for window in WINDOW_SCOPE_VALUES:
            rows.append(
                metric_row(
                    "WINDOW",
                    window,
                    delay,
                    candidate_scope_stats.get((window, delay), empty_distribution(f"candidate:{window}:{delay}")),
                    null_scope_stats.get((window, delay), empty_distribution(f"null:{window}:{delay}")),
                )
            )
    return rows


def build_period_rows(processed: dict[str, Any], full_effect_sign: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidate_period_stats: dict[tuple[str, str, int], base.MomentStats] = processed["candidate_period_stats"]
    null_period_stats: dict[tuple[str, str, int], base.MomentStats] = processed["null_period_stats"]
    for period_key in sorted(candidate_period_stats):
        period_type, period_value, delay = period_key
        row = metric_row(period_type, period_value, delay, candidate_period_stats[period_key], null_period_stats[period_key])
        effect = price_linkage.float_or_none(row["gross_effect_vs_null_signed"])
        gross_edge = price_linkage.float_or_none(row["gross_edge_observed_direction"])
        row["consistent_with_full_history_effect"] = str(sign_of(effect) == full_effect_sign).lower()
        row["regime_edge_bps"] = rounded_bps(gross_edge * 10_000 if gross_edge is not None else None)
        rows.append(row)
    return rows


def build_symbol_rows(processed: dict[str, Any], full_effect_sign: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidate_symbol_stats: dict[tuple[str, int], base.MomentStats] = processed["candidate_symbol_stats"]
    null_symbol_stats: dict[tuple[str, int], base.MomentStats] = processed["null_symbol_stats"]
    for symbol, delay in sorted(candidate_symbol_stats):
        row = metric_row("SYMBOL", symbol, delay, candidate_symbol_stats[(symbol, delay)], null_symbol_stats[(symbol, delay)])
        effect = price_linkage.float_or_none(row["gross_effect_vs_null_signed"])
        gross_edge = price_linkage.float_or_none(row["gross_edge_observed_direction"])
        row["symbol"] = symbol
        row["consistent_with_full_history_effect"] = str(sign_of(effect) == full_effect_sign).lower()
        row["symbol_edge_bps"] = rounded_bps(gross_edge * 10_000 if gross_edge is not None else None)
        rows.append(row)
    return rows


def stability_summary(rows: list[dict[str, Any]], period_type: str, delay: int, min_count: int) -> dict[str, Any]:
    support = 0
    consistent = 0
    for row in rows:
        if str(row.get("scope_type")) != period_type:
            continue
        if int_value(row.get("delay_seconds"), -1) != delay:
            continue
        if int_value(row.get("kept_event_count")) < min_count:
            continue
        support += 1
        if str(row.get("consistent_with_full_history_effect", "")).lower() == "true":
            consistent += 1
    return {
        "period_type": period_type,
        "delay_seconds": delay,
        "support_count": support,
        "consistent_count": consistent,
        "stability_rate": rounded(safe_div(consistent, support), 6),
    }


def worst_period(rows: list[dict[str, Any]], period_type: str, delay: int) -> dict[str, Any]:
    candidates = [
        row for row in rows
        if str(row.get("scope_type")) == period_type
        and int_value(row.get("delay_seconds"), -1) == delay
        and int_value(row.get("kept_event_count")) >= MIN_PERIOD_EVENT_COUNT
        and price_linkage.float_or_none(row.get("gross_edge_observed_direction")) is not None
    ]
    if not candidates:
        return {}
    return min(candidates, key=lambda row: price_linkage.float_or_none(row.get("gross_edge_observed_direction")) or 0.0)


def build_cost_rows(scope_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scope_row in scope_rows:
        gross_edge = price_linkage.float_or_none(scope_row.get("gross_edge_observed_direction"))
        for cost_bps in COST_GRID_BPS:
            cost_return = cost_bps / 10_000
            net_effect = gross_edge - cost_return if gross_edge is not None else None
            rows.append(
                {
                    "scope_type": scope_row["scope_type"],
                    "scope_value": scope_row["scope_value"],
                    "candidate": candidate_label(),
                    "locked_filter": LOCKED_FILTER_NAME,
                    "horizon_seconds": LOCKED_HORIZON_SECONDS,
                    "cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
                    "delay_seconds": scope_row["delay_seconds"],
                    "cost_bps": cost_bps,
                    "kept_event_count": scope_row["kept_event_count"],
                    "gross_mean_forward_price_return": scope_row["gross_mean_forward_price_return"],
                    "gross_median_forward_price_return": scope_row["gross_median_forward_price_return"],
                    "gross_effect_vs_null_signed": scope_row["gross_effect_vs_null_signed"],
                    "gross_edge_observed_direction": scope_row["gross_edge_observed_direction"],
                    "net_effect_after_cost": rounded(net_effect),
                    "net_effect_after_cost_bps": rounded_bps(net_effect * 10_000 if net_effect is not None else None),
                    "break_even_cost_bps": scope_row["break_even_cost_bps"],
                    "classification": "SURVIVES_COST" if net_effect is not None and net_effect > 0 else "FILTER_ONLY",
                }
            )
    return rows


def max_cost_survived(cost_rows: list[dict[str, Any]], required_scope_values: set[str], delay: int) -> float | None:
    survived: list[float] = []
    for cost in COST_GRID_BPS:
        rows_for_cost = [
            row for row in cost_rows
            if float(row.get("cost_bps", -1)) == cost
            and int_value(row.get("delay_seconds"), -1) == delay
            and str(row.get("scope_value")) in required_scope_values
        ]
        if len(rows_for_cost) != len(required_scope_values):
            continue
        if all(str(row.get("classification")) == "SURVIVES_COST" for row in rows_for_cost):
            survived.append(cost)
    return max(survived) if survived else None


def build_delay_survival(scope_rows: list[dict[str, Any]], cost_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_scope_delay = {(str(row["scope_value"]), int_value(row["delay_seconds"])): row for row in scope_rows}
    result: dict[str, Any] = {}
    required_scopes = {FULL_SCOPE_VALUE, "LATEST_90D", "HOLDOUT_90D", "OLDER_HISTORY"}
    for delay in DELAY_SECONDS:
        full = by_scope_delay.get((FULL_SCOPE_VALUE, delay), {})
        latest = by_scope_delay.get(("LATEST_90D", delay), {})
        holdout = by_scope_delay.get(("HOLDOUT_90D", delay), {})
        older = by_scope_delay.get(("OLDER_HISTORY", delay), {})
        max_cost = max_cost_survived(cost_rows, required_scopes, delay)
        result[str(delay)] = {
            "delay_seconds": delay,
            "full_history_break_even_cost_bps": full.get("break_even_cost_bps", ""),
            "latest_break_even_cost_bps": latest.get("break_even_cost_bps", ""),
            "holdout_break_even_cost_bps": holdout.get("break_even_cost_bps", ""),
            "older_history_break_even_cost_bps": older.get("break_even_cost_bps", ""),
            "full_history_event_count": full.get("kept_event_count", 0),
            "latest_event_count": latest.get("kept_event_count", 0),
            "holdout_event_count": holdout.get("kept_event_count", 0),
            "older_history_event_count": older.get("kept_event_count", 0),
            "max_cost_bps_survived_all_scopes": "" if max_cost is None else max_cost,
        }
    return result


def classify(scope_rows: list[dict[str, Any]], stability: dict[str, Any], delay_survival: dict[str, Any]) -> str:
    by_scope = {(str(row["scope_value"]), int_value(row["delay_seconds"])): row for row in scope_rows}
    full = by_scope[(FULL_SCOPE_VALUE, 0)]
    latest = by_scope[("LATEST_90D", 0)]
    holdout = by_scope[("HOLDOUT_90D", 0)]
    older = by_scope[("OLDER_HISTORY", 0)]
    full_edge = price_linkage.float_or_none(full.get("gross_edge_observed_direction"))
    latest_edge = price_linkage.float_or_none(latest.get("gross_edge_observed_direction"))
    holdout_edge = price_linkage.float_or_none(holdout.get("gross_edge_observed_direction"))
    older_edge = price_linkage.float_or_none(older.get("gross_edge_observed_direction"))
    if full_edge is None or full_edge <= 0 or int_value(full.get("kept_event_count")) < MIN_EVENT_COUNT:
        return "REJECTED"
    stable = all(
        (price_linkage.float_or_none(stability[key]["stability_rate"]) or 0.0) >= MIN_STABILITY_RATE
        for key in ["symbol", "monthly", "quarterly", "yearly", "weekly"]
    )
    all_windows_positive = all(value is not None and value > 0 for value in [latest_edge, holdout_edge, older_edge])
    max_delay0_cost = price_linkage.float_or_none(delay_survival["0"].get("max_cost_bps_survived_all_scopes"))
    if all_windows_positive and stable and max_delay0_cost is not None and max_delay0_cost >= 1.0:
        return "FULL_HISTORY_SURVIVED"
    if latest_edge is not None and latest_edge > 0 and holdout_edge is not None and holdout_edge > 0:
        if older_edge is None or older_edge <= 0:
            return "RECENT_ONLY"
        return "FILTER_ONLY"
    if full_edge > 0:
        return "UNSTABLE"
    return "REJECTED"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def metric_fieldnames(extra: list[str] | None = None) -> list[str]:
    names = [
        "scope_type",
        "scope_value",
        "candidate",
        "locked_filter",
        "filter_definition",
        "category",
        "horizon_seconds",
        "cooldown_seconds",
        "delay_seconds",
        "observed_direction",
        "original_candidate_row_count",
        "original_valid_event_count",
        "kept_event_count",
        "retention_rate",
        "gross_mean_forward_price_return",
        "gross_median_forward_price_return",
        "gross_std_forward_price_return",
        "null_event_count",
        "null_mean_forward_price_return",
        "null_std_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "break_even_cost_bps",
        "directional_diagnostic_rate",
        "consistent_with_observed_direction",
        "consistent_with_full_history_effect",
        "regime_edge_bps",
    ]
    if extra:
        names.extend(extra)
    return names


def cost_fieldnames() -> list[str]:
    return [
        "scope_type",
        "scope_value",
        "candidate",
        "locked_filter",
        "horizon_seconds",
        "cooldown_seconds",
        "delay_seconds",
        "cost_bps",
        "kept_event_count",
        "gross_mean_forward_price_return",
        "gross_median_forward_price_return",
        "gross_effect_vs_null_signed",
        "gross_edge_observed_direction",
        "net_effect_after_cost",
        "net_effect_after_cost_bps",
        "break_even_cost_bps",
        "classification",
    ]


def output_sizes() -> dict[str, int]:
    paths = [
        SUMMARY_JSON,
        SUMMARY_MD,
        PERIOD_STABILITY_CSV,
        SYMBOL_STABILITY_CSV,
        DELAY_COST_GRID_CSV,
        NULL_COMPARISON_CSV,
        CHUNK_PROGRESS_CSV,
        COMPLETED_CHUNKS_MANIFEST_JSON,
        PARTIAL_AGGREGATE_SUMMARIES_JSON,
    ]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Causal trailing trade-count full-history validation v1",
        "",
        f"status: {summary['status']}",
        f"classification: {summary['classification']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"symbol_days_processed: {summary['symbol_days_processed']}",
        f"event_count_after_causal_filter: {summary['event_count_after_causal_filter']}",
        f"delay0_break_even_cost_bps: {summary['full_history_metrics_delay0'].get('break_even_cost_bps', '')}",
        f"delay0_max_cost_bps_survived_all_scopes: {summary['delay_survival']['0'].get('max_cost_bps_survived_all_scopes', '')}",
        "",
        "## Locked Filter",
        f"locked_filter: {summary['locked_causal_filter']}",
        "filter_definition: aggTrades count in [event_ms - 60s, event_ms) >= 100",
        "",
        "This is locked-candidate research validation only. No downloads, row-level dataset, parquet dataset, strategy, backtest, signal, PnL curve, orders, private endpoints, or recommendations are created.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def load_completed_chunk_payloads(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    gap_seen = False
    for chunk in chunks:
        path = Path(chunk["path"])
        if path.exists():
            payload = load_json_object(path)
            is_complete = (
                payload.get("status") == "COMPLETE_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_CHUNK"
                and payload.get("chunk_id") == chunk["chunk_id"]
                and payload.get("start_date") == chunk["start_date"]
                and payload.get("end_date") == chunk["end_date"]
            )
            if is_complete:
                if gap_seen:
                    raise RuntimeError(f"completed chunk after incomplete gap is not resumable safely: {chunk['chunk_id']}")
                payloads.append(payload)
                continue
        gap_seen = True
    return payloads


def write_chunk_payload(
    chunk: dict[str, Any],
    processed: dict[str, Any],
    starting_candidate_state: dict[str, int],
    starting_null_state: dict[tuple[str, int], int],
    runtime_seconds: float,
) -> dict[str, Any]:
    payload = {
        "status": "COMPLETE_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_CHUNK",
        "created_at_utc": utc_now_text(),
        "chunk_id": chunk["chunk_id"],
        "chunk_period": chunk["period"],
        "start_date": chunk["start_date"],
        "end_date": chunk["end_date"],
        "pair_count": chunk["pair_count"],
        "runtime_seconds": round(runtime_seconds, 3),
        "candidate": candidate_label(),
        "locked_category": LOCKED_CATEGORY,
        "locked_horizon_seconds": LOCKED_HORIZON_SECONDS,
        "locked_cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "locked_causal_filter": LOCKED_FILTER_NAME,
        "filter_definition": "aggTrades count in [event_ms - 60s, event_ms) >= 100",
        "candidate_selection_uses_future_window": False,
        "candidate_selection_uses_post_event_notional": False,
        "candidate_selection_uses_post_event_trade_count": False,
        "candidate_selection_uses_around_event_helper": False,
        "processed_symbol_days": processed["processed_symbol_days"],
        "failed_symbol_days": processed["failed_symbol_days"],
        "feature_rows_seen": processed["total_feature_rows"],
        "original_candidate_row_count": processed["original_candidate_row_count"],
        "original_valid_event_count": processed["original_valid_event_count"],
        "kept_non_overlap_event_count_before_filter": processed["kept_non_overlap_event_count"],
        "event_count_after_causal_filter": processed["event_count_after_causal_filter"],
        "null_original_event_count": processed["null_original_event_count"],
        "category_counts": processed["category_counts"],
        "filter_trade_count_bucket_counts": processed["filter_trade_count_bucket_counts"],
        "failure_examples": processed["failure_examples"],
        "starting_candidate_last_kept_ms": starting_candidate_state,
        "starting_null_last_kept_ms": serialize_null_state(starting_null_state),
        "ending_candidate_last_kept_ms": processed["ending_candidate_last_kept_ms"],
        "ending_null_last_kept_ms": serialize_null_state(processed["ending_null_last_kept_ms"]),
        "candidate_scope_stats": stats_payload(processed["candidate_scope_stats"]),
        "candidate_period_stats": stats_payload(processed["candidate_period_stats"]),
        "candidate_symbol_stats": stats_payload(processed["candidate_symbol_stats"]),
        "null_scope_stats": stats_payload(processed["null_scope_stats"]),
        "null_period_stats": stats_payload(processed["null_period_stats"]),
        "null_symbol_stats": stats_payload(processed["null_symbol_stats"]),
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "raw_data_modified": False,
    }
    CHUNK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    Path(chunk["path"]).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def merge_chunk_payloads(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "processed_symbol_days": 0,
        "failed_symbol_days": 0,
        "total_feature_rows": 0,
        "original_candidate_row_count": 0,
        "original_valid_event_count": 0,
        "kept_non_overlap_event_count": 0,
        "event_count_after_causal_filter": 0,
        "null_original_event_count": 0,
        "category_counts": {},
        "filter_trade_count_bucket_counts": {},
        "failure_examples": [],
        "candidate_scope_stats": {},
        "candidate_period_stats": defaultdict(base.MomentStats),
        "candidate_symbol_stats": defaultdict(base.MomentStats),
        "null_scope_stats": {},
        "null_period_stats": defaultdict(base.MomentStats),
        "null_symbol_stats": defaultdict(base.MomentStats),
    }
    category_counts: Counter[str] = Counter()
    trade_count_buckets: Counter[str] = Counter()
    for payload in payloads:
        merged["processed_symbol_days"] += int_value(payload.get("processed_symbol_days"))
        merged["failed_symbol_days"] += int_value(payload.get("failed_symbol_days"))
        merged["total_feature_rows"] += int_value(payload.get("feature_rows_seen"))
        merged["original_candidate_row_count"] += int_value(payload.get("original_candidate_row_count"))
        merged["original_valid_event_count"] += int_value(payload.get("original_valid_event_count"))
        merged["kept_non_overlap_event_count"] += int_value(payload.get("kept_non_overlap_event_count_before_filter"))
        merged["event_count_after_causal_filter"] += int_value(payload.get("event_count_after_causal_filter"))
        merged["null_original_event_count"] += int_value(payload.get("null_original_event_count"))
        category_counts.update(payload.get("category_counts", {}) or {})
        trade_count_buckets.update(payload.get("filter_trade_count_bucket_counts", {}) or {})
        for failure in payload.get("failure_examples", []) or []:
            if len(merged["failure_examples"]) < 30:
                merged["failure_examples"].append(failure)
        merge_stats_payload(merged["candidate_scope_stats"], payload.get("candidate_scope_stats", {}) or {}, True)
        merge_stats_payload(merged["candidate_period_stats"], payload.get("candidate_period_stats", {}) or {}, False)
        merge_stats_payload(merged["candidate_symbol_stats"], payload.get("candidate_symbol_stats", {}) or {}, False)
        merge_stats_payload(merged["null_scope_stats"], payload.get("null_scope_stats", {}) or {}, True)
        merge_stats_payload(merged["null_period_stats"], payload.get("null_period_stats", {}) or {}, False)
        merge_stats_payload(merged["null_symbol_stats"], payload.get("null_symbol_stats", {}) or {}, False)
    merged["category_counts"] = dict(category_counts)
    merged["filter_trade_count_bucket_counts"] = dict(trade_count_buckets)
    return merged


def write_chunk_progress(chunks: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    completed = {str(payload["chunk_id"]): payload for payload in payloads}
    rows: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks, start=1):
        payload = completed.get(str(chunk["chunk_id"]), {})
        rows.append(
            {
                "chunk_index": index,
                "chunk_id": chunk["chunk_id"],
                "chunk_period": chunk["period"],
                "start_date": chunk["start_date"],
                "end_date": chunk["end_date"],
                "status": "COMPLETED" if payload else "PENDING",
                "pair_count": chunk["pair_count"],
                "processed_symbol_days": payload.get("processed_symbol_days", ""),
                "failed_symbol_days": payload.get("failed_symbol_days", ""),
                "feature_rows_seen": payload.get("feature_rows_seen", ""),
                "event_count_after_causal_filter": payload.get("event_count_after_causal_filter", ""),
                "runtime_seconds": payload.get("runtime_seconds", ""),
                "chunk_summary_path": str(chunk["path"]),
            }
        )
    write_csv(
        CHUNK_PROGRESS_CSV,
        [
            "chunk_index",
            "chunk_id",
            "chunk_period",
            "start_date",
            "end_date",
            "status",
            "pair_count",
            "processed_symbol_days",
            "failed_symbol_days",
            "feature_rows_seen",
            "event_count_after_causal_filter",
            "runtime_seconds",
            "chunk_summary_path",
        ],
        rows,
    )
    return rows


def write_completed_manifest(
    chunks: list[dict[str, Any]],
    payloads: list[dict[str, Any]],
    requested_workers: int,
    effective_workers: int,
) -> dict[str, Any]:
    manifest = {
        "status": "CHUNK_MANIFEST_UPDATED",
        "created_at_utc": utc_now_text(),
        "chunk_period": chunk_period(),
        "chunk_count_total": len(chunks),
        "completed_chunk_count": len(payloads),
        "pending_chunk_count": max(0, len(chunks) - len(payloads)),
        "completed_chunks_are_contiguous_from_start": True,
        "resume_safe": True,
        "requested_chunk_workers": requested_workers,
        "effective_chunk_workers": effective_workers,
        "chunk_parallelism_status": "SEQUENTIAL_FOR_EXACT_COOLDOWN_CARRY_FORWARD",
        "completed_chunks": [
            {
                "chunk_id": payload["chunk_id"],
                "start_date": payload["start_date"],
                "end_date": payload["end_date"],
                "processed_symbol_days": payload["processed_symbol_days"],
                "failed_symbol_days": payload["failed_symbol_days"],
                "event_count_after_causal_filter": payload["event_count_after_causal_filter"],
                "runtime_seconds": payload["runtime_seconds"],
                "chunk_summary_path": str(chunk_file_path(str(payload["chunk_id"]))),
            }
            for payload in payloads
        ],
    }
    COMPLETED_CHUNKS_MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def build_and_write_merged_outputs(
    chunks: list[dict[str, Any]],
    payloads: list[dict[str, Any]],
    pair_metadata: dict[str, Any],
    started: float,
    requested_workers: int,
    effective_workers: int,
) -> dict[str, Any]:
    if not payloads:
        raise RuntimeError("no completed chunks available to merge")
    processed = merge_chunk_payloads(payloads)
    scope_rows = build_scope_rows(processed)
    full_delay0 = next(row for row in scope_rows if row["scope_type"] == "FULL_HISTORY" and int_value(row["delay_seconds"]) == 0)
    full_effect_sign = sign_of(price_linkage.float_or_none(full_delay0.get("gross_effect_vs_null_signed")))
    period_rows = build_period_rows(processed, full_effect_sign)
    symbol_rows = build_symbol_rows(processed, full_effect_sign)
    stability = {
        "symbol": stability_summary(symbol_rows, "SYMBOL", 0, MIN_SYMBOL_EVENT_COUNT),
        "monthly": stability_summary(period_rows, "MONTH", 0, MIN_PERIOD_EVENT_COUNT),
        "quarterly": stability_summary(period_rows, "QUARTER", 0, MIN_PERIOD_EVENT_COUNT),
        "yearly": stability_summary(period_rows, "YEAR", 0, MIN_PERIOD_EVENT_COUNT),
        "weekly": stability_summary(period_rows, "WEEK", 0, MIN_PERIOD_EVENT_COUNT),
    }
    cost_rows = build_cost_rows(scope_rows)
    delay_survival = build_delay_survival(scope_rows, cost_rows)
    all_chunks_complete = len(payloads) == len(chunks)
    classification = classify(scope_rows, stability, delay_survival) if all_chunks_complete else "PARTIAL_CHUNKED_SMOKE"
    worst_quarter = worst_period(period_rows, "QUARTER", 0)
    worst_month = worst_period(period_rows, "MONTH", 0)
    chunk_rows = write_chunk_progress(chunks, payloads)
    manifest = write_completed_manifest(chunks, payloads, requested_workers, effective_workers)

    write_csv(PERIOD_STABILITY_CSV, metric_fieldnames(), period_rows)
    write_csv(SYMBOL_STABILITY_CSV, metric_fieldnames(["symbol", "symbol_edge_bps"]), symbol_rows)
    write_csv(DELAY_COST_GRID_CSV, cost_fieldnames(), cost_rows)
    write_csv(NULL_COMPARISON_CSV, metric_fieldnames(), scope_rows)

    completed_runtime = sum(float(payload.get("runtime_seconds") or 0.0) for payload in payloads)
    estimated_full_runtime = safe_div(completed_runtime, processed["processed_symbol_days"])
    estimated_full_runtime_seconds = estimated_full_runtime * EXPECTED_SYMBOL_DAYS if estimated_full_runtime is not None else None
    status = (
        "PASS_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATED"
        if all_chunks_complete
        and processed["processed_symbol_days"] == EXPECTED_SYMBOL_DAYS
        and processed["failed_symbol_days"] == 0
        and len(pair_metadata["symbol_details"]) == EXPECTED_SYMBOL_COUNT
        else "SMOKE_OR_PARTIAL_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATION_CHUNKED"
    )
    summary: dict[str, Any] = {
        "status": status,
        "classification": classification,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATION_V1",
        "candidate": candidate_label(),
        "locked_category": LOCKED_CATEGORY,
        "locked_horizon_seconds": LOCKED_HORIZON_SECONDS,
        "locked_cooldown_seconds": LOCKED_COOLDOWN_SECONDS,
        "locked_causal_filter": LOCKED_FILTER_NAME,
        "filter_definition": "aggTrades count in [event_ms - 60s, event_ms) >= 100",
        "filter_lookback_seconds": LOCKED_FILTER_LOOKBACK_SECONDS,
        "filter_min_trade_count": LOCKED_FILTER_MIN_TRADE_COUNT,
        "candidate_selection_uses_future_window": False,
        "candidate_selection_uses_post_event_notional": False,
        "candidate_selection_uses_post_event_trade_count": False,
        "candidate_selection_uses_around_event_helper": False,
        "observed_direction": observed_direction_text(),
        "coverage_start": START_DATE,
        "coverage_end": END_DATE,
        "delay_seconds": DELAY_SECONDS,
        "cost_grid_bps": COST_GRID_BPS,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "completed_chunks_runtime_seconds": round(completed_runtime, 3),
        "estimated_full_runtime_seconds": rounded(estimated_full_runtime_seconds, 3),
        "chunked_resume_enabled": True,
        "chunk_period": chunk_period(),
        "chunk_count_total": len(chunks),
        "completed_chunk_count": len(payloads),
        "pending_chunk_count": max(0, len(chunks) - len(payloads)),
        "run_completion_status": "FULL_HISTORY_COMPLETE" if all_chunks_complete else "PARTIAL_CHUNKED_SMOKE_OR_RESUME",
        "requested_chunk_workers": requested_workers,
        "effective_chunk_workers": effective_workers,
        "chunk_workers_max": MAX_CHUNK_WORKERS,
        "chunk_parallelism_status": "SEQUENTIAL_FOR_EXACT_COOLDOWN_CARRY_FORWARD",
        "symbol_days_expected": EXPECTED_SYMBOL_DAYS,
        "symbol_days_processed": processed["processed_symbol_days"],
        "failed_symbol_days": processed["failed_symbol_days"],
        "feature_rows_seen": processed["total_feature_rows"],
        "original_candidate_row_count": processed["original_candidate_row_count"],
        "original_valid_event_count": processed["original_valid_event_count"],
        "kept_non_overlap_event_count_before_filter": processed["kept_non_overlap_event_count"],
        "event_count_after_causal_filter": processed["event_count_after_causal_filter"],
        "causal_filter_retention_rate_vs_original_valid_events": rounded(
            safe_div(processed["event_count_after_causal_filter"], processed["original_valid_event_count"]),
            6,
        ),
        "causal_filter_retention_rate_vs_non_overlap_events": rounded(
            safe_div(processed["event_count_after_causal_filter"], processed["kept_non_overlap_event_count"]),
            6,
        ),
        "null_original_event_count": processed["null_original_event_count"],
        "full_history_metrics_delay0": full_delay0,
        "scope_metrics": scope_rows,
        "delay_survival": delay_survival,
        "latest_90d_vs_holdout_90d_vs_older_history_consistency": {
            row["scope_value"]: {
                "delay_seconds": row["delay_seconds"],
                "kept_event_count": row["kept_event_count"],
                "gross_effect_vs_null_signed": row["gross_effect_vs_null_signed"],
                "gross_edge_observed_direction": row["gross_edge_observed_direction"],
                "break_even_cost_bps": row["break_even_cost_bps"],
                "consistent_with_observed_direction": row["consistent_with_observed_direction"],
            }
            for row in scope_rows
            if row["scope_type"] == "WINDOW" and int_value(row["delay_seconds"]) == 0
        },
        "stability": stability,
        "regime_drift": {
            "yearly": stability["yearly"],
            "quarterly": stability["quarterly"],
            "monthly": stability["monthly"],
        },
        "worst_quarter": worst_quarter,
        "worst_month": worst_month,
        "category_counts": processed["category_counts"],
        "filter_trade_count_bucket_counts": processed["filter_trade_count_bucket_counts"],
        "failure_examples": processed["failure_examples"],
        "chunk_progress_rows": chunk_rows,
        "completed_chunks_manifest": manifest,
        "pair_metadata": {
            "symbol_count": len(pair_metadata["symbol_details"]),
            "oldest_date": min((item["oldest"] for item in pair_metadata["symbol_details"].values()), default=""),
            "newest_date": max((item["newest"] for item in pair_metadata["symbol_details"].values()), default=""),
        },
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "raw_data_modified": False,
        "new_filters_added": False,
        "thresholds_optimized": False,
        "strategy_created": False,
        "backtest_created": False,
        "pnl_created": False,
        "signals_created": False,
        "orders_created": False,
        "private_endpoints_used": False,
        "recommendations_created": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "period_stability_csv": str(PERIOD_STABILITY_CSV),
            "symbol_stability_csv": str(SYMBOL_STABILITY_CSV),
            "delay_cost_grid_csv": str(DELAY_COST_GRID_CSV),
            "null_comparison_csv": str(NULL_COMPARISON_CSV),
            "chunk_progress_csv": str(CHUNK_PROGRESS_CSV),
            "completed_chunks_manifest_json": str(COMPLETED_CHUNKS_MANIFEST_JSON),
            "partial_aggregate_summaries_json": str(PARTIAL_AGGREGATE_SUMMARIES_JSON),
            "chunk_output_dir": str(CHUNK_OUTPUT_DIR),
        },
        "resume_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            ".\\run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.ps1"
        ),
        "exact_full_run_command": (
            "$env:ORDERBOOK_FULL_HISTORY_CHUNK_PERIOD='month'; "
            "Remove-Item Env:ORDERBOOK_FULL_HISTORY_CHUNK_LIMIT -ErrorAction SilentlyContinue; "
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            ".\\run_edge_factory_orderbook_um_81_causal_trailing_trade_count_full_history_validation_v1.ps1"
        ),
    }
    PARTIAL_AGGREGATE_SUMMARIES_JSON.write_text(
        json.dumps(
            {
                "created_at_utc": utc_now_text(),
                "status": summary["status"],
                "completed_chunk_count": len(payloads),
                "pending_chunk_count": summary["pending_chunk_count"],
                "symbol_days_processed": processed["processed_symbol_days"],
                "event_count_after_causal_filter": processed["event_count_after_causal_filter"],
                "full_history_metrics_delay0": full_delay0,
                "scope_metrics": scope_rows,
                "completed_chunks": manifest["completed_chunks"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    summary["output_sizes_bytes"] = output_sizes()
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def run_validation() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    CHUNK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if base.path_is_inside(base.DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or base.path_is_inside(
        base.DEFAULT_AGGTRADES_RAW_ROOT,
        REPO_ROOT,
    ):
        raise RuntimeError("raw ZIP roots must stay outside repo")
    pairs, pair_metadata = load_full_history_pairs()
    period = chunk_period()
    chunks = build_chunks(pairs, period)
    requested_workers = requested_chunk_workers()
    effective_workers = effective_chunk_workers(requested_workers)
    payloads = load_completed_chunk_payloads(chunks)
    starting_index = len(payloads)
    limit = chunk_limit()
    chunks_to_run = chunks[starting_index:]
    if limit is not None:
        chunks_to_run = chunks_to_run[:limit]
    candidate_state = dict(payloads[-1].get("ending_candidate_last_kept_ms", {})) if payloads else {}
    null_state = deserialize_null_state(payloads[-1].get("ending_null_last_kept_ms", {})) if payloads else {}
    if payloads:
        write_chunk_progress(chunks, payloads)
        write_completed_manifest(chunks, payloads, requested_workers, effective_workers)
    if not chunks_to_run and not payloads:
        raise RuntimeError("no chunks selected and no completed chunks available")
    for chunk in chunks_to_run:
        chunk_started = time.monotonic()
        processed = process_full_history(
            list(chunk["pairs"]),
            candidate_state,
            null_state,
            progress_label=str(chunk["chunk_id"]),
        )
        payload = write_chunk_payload(
            chunk,
            processed,
            candidate_state,
            null_state,
            time.monotonic() - chunk_started,
        )
        payloads.append(payload)
        candidate_state = dict(payload.get("ending_candidate_last_kept_ms", {}))
        null_state = deserialize_null_state(payload.get("ending_null_last_kept_ms", {}))
        build_and_write_merged_outputs(chunks, payloads, pair_metadata, started, requested_workers, effective_workers)
    return build_and_write_merged_outputs(chunks, payloads, pair_metadata, started, requested_workers, effective_workers)


def main() -> int:
    try:
        summary = run_validation()
    except Exception as exc:  # noqa: BLE001
        error_summary = {
            "status": "FAILED_ORDERBOOK_UM_81_CAUSAL_TRAILING_TRADE_COUNT_FULL_HISTORY_VALIDATION",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "row_level_dataset_created": False,
            "parquet_dataset_created": False,
            "downloads_run": False,
            "raw_data_modified": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Causal trailing trade-count full-history validation v1\n\n"
            f"status: {error_summary['status']}\n"
            f"error: {error_summary['error']}\n",
            encoding="utf-8",
        )
        print(json.dumps(error_summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if str(summary.get("status", "")).startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
