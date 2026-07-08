#!/usr/bin/env python
"""Stream latest 90-day 81-symbol absorption discovery diagnostics."""

from __future__ import annotations

import bisect
import csv
import hashlib
import io
import json
import math
import os
import random
import statistics
import time
import zipfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = REPO_ROOT / "outputs"

BOOKDEPTH_FILE_STATUS_CSV = OUTPUTS_DIR / "orderbook_um_81_full_bookdepth_file_status.csv"
AGGTRADES_FILE_STATUS_CSV = OUTPUTS_DIR / "orderbook_um_81_full_matching_aggtrades_file_status.csv"

DEFAULT_BOOKDEPTH_RAW_ROOT = Path(r"C:\edge_factory_external_data\binance_um_81_full_bookdepth_raw")
DEFAULT_AGGTRADES_RAW_ROOT = Path(r"C:\edge_factory_external_data\binance_um_81_full_matching_aggtrades_raw")

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_summary.md"
CATEGORY_HORIZON_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_category_horizon.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_symbol_stability.csv"
NULL_COMPARISON_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_null_comparison.csv"
CANDIDATES_CSV = OUTPUTS_DIR / "orderbook_um_81_streaming_absorption_discovery_90d_candidates.csv"

FULL_HISTORY_ENV = "ORDERBOOK_81_STREAMING_ABSORPTION_DISCOVERY"
EXPECTED_SYMBOL_COUNT = 81
LATEST_DAYS_PER_SYMBOL = 90
PROGRESS_INTERVAL_SECONDS = 30
ROLLING_WINDOW_ROWS = 12
RESERVOIR_LIMIT = 50_000

BUCKETS = [1, 2, 3, 4, 5]
HORIZON_SECONDS = [10, 30, 60, 300]
CATEGORIES = [
    "BUY_PRESSURE_ABSORBED",
    "SELL_PRESSURE_ABSORBED",
    "FLOW_AND_DEPTH_ALIGNED_UP",
    "FLOW_AND_DEPTH_ALIGNED_DOWN",
    "MIXED_OR_NOISY",
    "INSUFFICIENT_DATA",
]
DIRECTION_BY_CATEGORY = {
    "BUY_PRESSURE_ABSORBED": -1,
    "SELL_PRESSURE_ABSORBED": 1,
    "FLOW_AND_DEPTH_ALIGNED_UP": 1,
    "FLOW_AND_DEPTH_ALIGNED_DOWN": -1,
    "MIXED_OR_NOISY": 0,
    "INSUFFICIENT_DATA": 0,
}


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bool_value(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_div(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def csv_writer(path: Path, fieldnames: list[str]) -> tuple[Any, csv.DictWriter]:
    handle = path.open("w", encoding="utf-8", newline="")
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    return handle, writer


def parse_book_timestamp(value: str) -> tuple[int, str]:
    parsed = datetime.fromisoformat(value.replace(" ", "T")).replace(tzinfo=timezone.utc)
    timestamp_ms = int(parsed.timestamp() * 1000)
    return timestamp_ms, parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def single_csv_reader(zip_path: Path) -> Iterable[list[str]]:
    with zipfile.ZipFile(zip_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"expected exactly one CSV in {zip_path}, found {len(csv_names)}")
        with archive.open(csv_names[0], "r") as raw_handle:
            text_handle = io.TextIOWrapper(raw_handle, encoding="utf-8", newline="")
            yield from csv.reader(text_handle)


def load_verified_paths(status_csv: Path, expected_root: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with status_csv.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not bool_value(row.get("checksum_verified")):
                continue
            zip_path = Path(row.get("local_zip_path", ""))
            if not zip_path.exists():
                continue
            if not path_is_inside(zip_path, expected_root):
                continue
            symbol = str(row.get("symbol", "")).strip()
            file_date = str(row.get("file_date", "")).strip()
            if symbol and file_date:
                rows[(symbol, file_date)] = row
    return rows


def build_input_pairs() -> list[dict[str, Any]]:
    book_rows = load_verified_paths(BOOKDEPTH_FILE_STATUS_CSV, DEFAULT_BOOKDEPTH_RAW_ROOT)
    agg_rows = load_verified_paths(AGGTRADES_FILE_STATUS_CSV, DEFAULT_AGGTRADES_RAW_ROOT)
    by_symbol: dict[str, list[str]] = defaultdict(list)
    for symbol, file_date in sorted(set(book_rows) & set(agg_rows)):
        by_symbol[symbol].append(file_date)

    full_history_requested = os.environ.get(FULL_HISTORY_ENV, "").strip().upper() == "YES"
    pairs: list[dict[str, Any]] = []
    for symbol in sorted(by_symbol):
        selected_dates = sorted(by_symbol[symbol], reverse=True)
        if not full_history_requested:
            selected_dates = selected_dates[:LATEST_DAYS_PER_SYMBOL]
        for file_date in sorted(selected_dates):
            key = (symbol, file_date)
            pairs.append(
                {
                    "symbol": symbol,
                    "file_date": file_date,
                    "year_month": file_date[:7],
                    "week": iso_week_text(file_date),
                    "bookdepth_zip_path": book_rows[key]["local_zip_path"],
                    "aggtrades_zip_path": agg_rows[key]["local_zip_path"],
                    "bookdepth_size_bytes": int_value(book_rows[key].get("observed_size_bytes")),
                    "aggtrades_size_bytes": int_value(agg_rows[key].get("observed_size_bytes")),
                }
            )
    return pairs


def iso_week_text(file_date: str) -> str:
    try:
        parsed = datetime.strptime(file_date, "%Y-%m-%d")
    except ValueError:
        return ""
    year, week, _ = parsed.isocalendar()
    return f"{year}-W{week:02d}"


def empty_feature_row(symbol: str, file_date: str, year_month: str, timestamp: str) -> dict[str, Any]:
    row = {
        "timestamp": timestamp,
        "symbol": symbol,
        "file_date": file_date,
        "year_month": year_month,
        "trade_count": 0,
        "total_qty": 0.0,
        "total_notional": 0.0,
        "aggressive_buy_qty": 0.0,
        "aggressive_sell_qty": 0.0,
        "aggressive_buy_notional": 0.0,
        "aggressive_sell_notional": 0.0,
        "flow_imbalance": None,
        "rolling_flow_pressure": None,
        "depth_imbalance_proxy": None,
        "rolling_depth_imbalance_proxy": None,
        "flow_depth_divergence_proxy": None,
        "spread_proxy": None,
        "microprice_proxy": None,
        "absorption_category": "INSUFFICIENT_DATA",
    }
    for bucket in BUCKETS:
        row[f"bid_depth_pct_{bucket}"] = 0.0
        row[f"ask_depth_pct_{bucket}"] = 0.0
        row[f"bid_notional_pct_{bucket}"] = 0.0
        row[f"ask_notional_pct_{bucket}"] = 0.0
    return row


def read_bookdepth_features(pair: dict[str, Any]) -> tuple[list[int], list[dict[str, Any]]]:
    by_timestamp: dict[int, dict[str, Any]] = {}
    timestamp_cache: dict[str, tuple[int, str]] = {}
    symbol = str(pair["symbol"])
    file_date = str(pair["file_date"])
    year_month = str(pair["year_month"])

    reader = iter(single_csv_reader(Path(str(pair["bookdepth_zip_path"]))))
    header = next(reader, None)
    if not header:
        return [], []
    positions = {name: index for index, name in enumerate(header)}
    required = {"timestamp", "percentage", "depth", "notional"}
    if not required.issubset(positions):
        raise ValueError(f"bookDepth CSV missing columns: {required - set(positions)}")

    for columns in reader:
        timestamp_text_raw = columns[positions["timestamp"]]
        parsed_timestamp = timestamp_cache.get(timestamp_text_raw)
        if parsed_timestamp is None:
            parsed_timestamp = parse_book_timestamp(timestamp_text_raw)
            timestamp_cache[timestamp_text_raw] = parsed_timestamp
        timestamp_ms, timestamp_text = parsed_timestamp
        feature_row = by_timestamp.setdefault(
            timestamp_ms,
            empty_feature_row(symbol, file_date, year_month, timestamp_text),
        )
        percentage = float_value(columns[positions["percentage"]])
        bucket = int(abs(percentage))
        if bucket not in BUCKETS:
            continue
        side = "bid" if percentage < 0 else "ask" if percentage > 0 else ""
        if not side:
            continue
        feature_row[f"{side}_depth_pct_{bucket}"] += float_value(columns[positions["depth"]])
        feature_row[f"{side}_notional_pct_{bucket}"] += float_value(columns[positions["notional"]])

    timestamps = sorted(by_timestamp)
    rows = [by_timestamp[timestamp_ms] for timestamp_ms in timestamps]
    for row in rows:
        bid_notional_total = sum(float(row[f"bid_notional_pct_{bucket}"]) for bucket in BUCKETS)
        ask_notional_total = sum(float(row[f"ask_notional_pct_{bucket}"]) for bucket in BUCKETS)
        row["depth_imbalance_proxy"] = safe_div(bid_notional_total - ask_notional_total, bid_notional_total + ask_notional_total)
    return timestamps, rows


def add_trade_flow(pair: dict[str, Any], timestamps: list[int], rows: list[dict[str, Any]]) -> None:
    if not timestamps:
        return
    reader = iter(single_csv_reader(Path(str(pair["aggtrades_zip_path"]))))
    header = next(reader, None)
    if not header:
        return
    positions = {name: index for index, name in enumerate(header)}
    required = {"price", "quantity", "transact_time", "is_buyer_maker"}
    if not required.issubset(positions):
        raise ValueError(f"aggTrades CSV missing columns: {required - set(positions)}")

    for columns in reader:
        transact_ms = int_value(columns[positions["transact_time"]], -1)
        row_index = bisect.bisect_right(timestamps, transact_ms) - 1
        if row_index < 0:
            continue
        row = rows[row_index]
        price = float_value(columns[positions["price"]])
        quantity = float_value(columns[positions["quantity"]])
        notional = price * quantity
        row["trade_count"] += 1
        row["total_qty"] += quantity
        row["total_notional"] += notional
        if bool_value(columns[positions["is_buyer_maker"]]):
            row["aggressive_sell_qty"] += quantity
            row["aggressive_sell_notional"] += notional
        else:
            row["aggressive_buy_qty"] += quantity
            row["aggressive_buy_notional"] += notional


def add_rolling_features(rows: list[dict[str, Any]]) -> None:
    buy_window: deque[float] = deque()
    sell_window: deque[float] = deque()
    depth_window: deque[float | None] = deque()
    buy_sum = 0.0
    sell_sum = 0.0
    depth_sum = 0.0
    depth_count = 0
    for row in rows:
        buy_notional = float(row["aggressive_buy_notional"])
        sell_notional = float(row["aggressive_sell_notional"])
        depth = row.get("depth_imbalance_proxy")
        row["flow_imbalance"] = safe_div(buy_notional - sell_notional, buy_notional + sell_notional)

        buy_window.append(buy_notional)
        sell_window.append(sell_notional)
        depth_window.append(depth if depth is None else float(depth))
        buy_sum += buy_notional
        sell_sum += sell_notional
        if depth is not None:
            depth_sum += float(depth)
            depth_count += 1

        if len(buy_window) > ROLLING_WINDOW_ROWS:
            buy_sum -= buy_window.popleft()
            sell_sum -= sell_window.popleft()
            removed_depth = depth_window.popleft()
            if removed_depth is not None:
                depth_sum -= float(removed_depth)
                depth_count -= 1

        row["rolling_flow_pressure"] = safe_div(buy_sum - sell_sum, buy_sum + sell_sum)
        row["rolling_depth_imbalance_proxy"] = safe_div(depth_sum, depth_count)
        if row["rolling_flow_pressure"] is None or row["rolling_depth_imbalance_proxy"] is None:
            row["flow_depth_divergence_proxy"] = None
        else:
            row["flow_depth_divergence_proxy"] = (
                float(row["rolling_flow_pressure"]) - float(row["rolling_depth_imbalance_proxy"])
            )
        row["absorption_category"] = absorption_category(row)


def absorption_category(row: dict[str, Any]) -> str:
    flow = row.get("rolling_flow_pressure")
    depth = row.get("rolling_depth_imbalance_proxy")
    if flow is None or depth is None:
        return "INSUFFICIENT_DATA"
    flow_value = float(flow)
    depth_value = float(depth)
    threshold = 0.15
    if abs(flow_value) < 0.05 and abs(depth_value) < 0.05:
        return "MIXED_OR_NOISY"
    if flow_value >= threshold and depth_value <= -threshold:
        return "BUY_PRESSURE_ABSORBED"
    if flow_value <= -threshold and depth_value >= threshold:
        return "SELL_PRESSURE_ABSORBED"
    if flow_value >= threshold and depth_value >= threshold:
        return "FLOW_AND_DEPTH_ALIGNED_UP"
    if flow_value <= -threshold and depth_value <= -threshold:
        return "FLOW_AND_DEPTH_ALIGNED_DOWN"
    return "MIXED_OR_NOISY"


def build_feature_rows(pair: dict[str, Any]) -> tuple[list[int], list[dict[str, Any]]]:
    timestamps, rows = read_bookdepth_features(pair)
    add_trade_flow(pair, timestamps, rows)
    add_rolling_features(rows)
    return timestamps, rows


def row_proxy_value(row: dict[str, Any]) -> float | None:
    value = row.get("rolling_depth_imbalance_proxy")
    if value is None:
        value = row.get("depth_imbalance_proxy")
    return None if value is None else float(value)


def day_volatility_proxy(rows: list[dict[str, Any]]) -> float | None:
    previous: float | None = None
    deltas: list[float] = []
    for row in rows:
        value = row_proxy_value(row)
        if value is None:
            continue
        if previous is not None:
            deltas.append(value - previous)
        previous = value
    if len(deltas) < 2:
        return None
    return float(statistics.pstdev(deltas))


def sign_of(value: float | None, tolerance: float = 1e-12) -> int:
    if value is None or abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1


@dataclass
class MomentStats:
    row_count: int = 0
    valid_forward_count: int = 0
    sum_value: float = 0.0
    sum_square: float = 0.0
    min_value: float | None = None
    max_value: float | None = None
    directional_total: int = 0
    directional_match: int = 0

    def add(self, value: float | None, expected_direction: int) -> None:
        self.row_count += 1
        if value is None:
            return
        self.valid_forward_count += 1
        self.sum_value += value
        self.sum_square += value * value
        self.min_value = value if self.min_value is None else min(self.min_value, value)
        self.max_value = value if self.max_value is None else max(self.max_value, value)
        observed_direction = sign_of(value)
        if expected_direction and observed_direction:
            self.directional_total += 1
            if observed_direction == expected_direction:
                self.directional_match += 1

    def mean(self) -> float | None:
        if not self.valid_forward_count:
            return None
        return self.sum_value / self.valid_forward_count

    def std(self) -> float | None:
        if self.valid_forward_count <= 1:
            return None
        mean = self.sum_value / self.valid_forward_count
        variance = max(0.0, (self.sum_square / self.valid_forward_count) - (mean * mean))
        return math.sqrt(variance)

    def directional_rate(self) -> float | None:
        if not self.directional_total:
            return None
        return self.directional_match / self.directional_total


@dataclass
class DistributionStats(MomentStats):
    sample_limit: int = RESERVOIR_LIMIT
    seed_text: str = ""
    reservoir: list[float] = field(default_factory=list)
    randomizer: random.Random = field(init=False)
    high_vol_count: int = 0
    high_vol_sum: float = 0.0
    low_vol_count: int = 0
    low_vol_sum: float = 0.0
    flow_sum: float = 0.0
    flow_count: int = 0
    depth_sum: float = 0.0
    depth_count: int = 0
    divergence_sum: float = 0.0
    divergence_count: int = 0

    def __post_init__(self) -> None:
        digest = hashlib.sha256(self.seed_text.encode("utf-8")).hexdigest()
        self.randomizer = random.Random(int(digest[:16], 16))

    def add_diagnostic(
        self,
        value: float | None,
        expected_direction: int,
        volatility_group: str,
        flow: float | None,
        depth: float | None,
        divergence: float | None,
    ) -> None:
        super().add(value, expected_direction)
        if flow is not None:
            self.flow_sum += flow
            self.flow_count += 1
        if depth is not None:
            self.depth_sum += depth
            self.depth_count += 1
        if divergence is not None:
            self.divergence_sum += divergence
            self.divergence_count += 1
        if value is None:
            return
        sample_number = self.valid_forward_count
        if len(self.reservoir) < self.sample_limit:
            self.reservoir.append(value)
        else:
            replacement_index = self.randomizer.randrange(sample_number)
            if replacement_index < self.sample_limit:
                self.reservoir[replacement_index] = value
        if volatility_group == "HIGH":
            self.high_vol_count += 1
            self.high_vol_sum += value
        elif volatility_group == "LOW":
            self.low_vol_count += 1
            self.low_vol_sum += value

    def quantile(self, probability: float) -> float | None:
        if not self.reservoir:
            return None
        values = sorted(self.reservoir)
        if len(values) == 1:
            return values[0]
        position = probability * (len(values) - 1)
        lower = math.floor(position)
        upper = math.ceil(position)
        if lower == upper:
            return values[lower]
        fraction = position - lower
        return values[lower] * (1 - fraction) + values[upper] * fraction

    def sampled_median(self) -> float | None:
        return self.quantile(0.5)

    def mean_flow(self) -> float | None:
        return safe_div(self.flow_sum, self.flow_count)

    def mean_depth(self) -> float | None:
        return safe_div(self.depth_sum, self.depth_count)

    def mean_divergence(self) -> float | None:
        return safe_div(self.divergence_sum, self.divergence_count)

    def high_vol_mean(self) -> float | None:
        return safe_div(self.high_vol_sum, self.high_vol_count)

    def low_vol_mean(self) -> float | None:
        return safe_div(self.low_vol_sum, self.low_vol_count)


def rounded(value: float | None, places: int = 10) -> float | str:
    if value is None or math.isnan(value):
        return ""
    return round(value, places)


def distribution_row(category: str, horizon: int, stats: DistributionStats) -> dict[str, Any]:
    return {
        "category": category,
        "horizon_seconds": horizon,
        "row_count": stats.row_count,
        "valid_forward_count": stats.valid_forward_count,
        "mean_forward_proxy_return": rounded(stats.mean()),
        "median_forward_proxy_return": rounded(stats.sampled_median()),
        "std_forward_proxy_return": rounded(stats.std()),
        "q05_forward_proxy_return": rounded(stats.quantile(0.05)),
        "q25_forward_proxy_return": rounded(stats.quantile(0.25)),
        "q50_forward_proxy_return": rounded(stats.quantile(0.50)),
        "q75_forward_proxy_return": rounded(stats.quantile(0.75)),
        "q95_forward_proxy_return": rounded(stats.quantile(0.95)),
        "directional_diagnostic_rate": rounded(stats.directional_rate(), 6),
        "directional_diagnostic_count": stats.directional_match,
        "directional_diagnostic_total": stats.directional_total,
        "mean_flow_imbalance": rounded(stats.mean_flow()),
        "mean_depth_imbalance_proxy": rounded(stats.mean_depth()),
        "mean_flow_depth_divergence_proxy": rounded(stats.mean_divergence()),
        "high_vol_count": stats.high_vol_count,
        "high_vol_mean_forward_proxy_return": rounded(stats.high_vol_mean()),
        "low_vol_count": stats.low_vol_count,
        "low_vol_mean_forward_proxy_return": rounded(stats.low_vol_mean()),
        "quantile_method": f"deterministic_reservoir_limit_{RESERVOIR_LIMIT}",
    }


def moment_row(
    symbol: str,
    period_type: str,
    period_value: str,
    category: str,
    horizon: int,
    stats: MomentStats,
) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "period_type": period_type,
        "period_value": period_value,
        "category": category,
        "horizon_seconds": horizon,
        "row_count": stats.row_count,
        "valid_forward_count": stats.valid_forward_count,
        "mean_forward_proxy_return": rounded(stats.mean()),
        "std_forward_proxy_return": rounded(stats.std()),
        "min_forward_proxy_return": rounded(stats.min_value),
        "max_forward_proxy_return": rounded(stats.max_value),
        "directional_diagnostic_rate": rounded(stats.directional_rate(), 6),
        "directional_diagnostic_count": stats.directional_match,
        "directional_diagnostic_total": stats.directional_total,
    }


def category_horizon_fieldnames() -> list[str]:
    return [
        "category",
        "horizon_seconds",
        "row_count",
        "valid_forward_count",
        "mean_forward_proxy_return",
        "median_forward_proxy_return",
        "std_forward_proxy_return",
        "q05_forward_proxy_return",
        "q25_forward_proxy_return",
        "q50_forward_proxy_return",
        "q75_forward_proxy_return",
        "q95_forward_proxy_return",
        "directional_diagnostic_rate",
        "directional_diagnostic_count",
        "directional_diagnostic_total",
        "mean_flow_imbalance",
        "mean_depth_imbalance_proxy",
        "mean_flow_depth_divergence_proxy",
        "high_vol_count",
        "high_vol_mean_forward_proxy_return",
        "low_vol_count",
        "low_vol_mean_forward_proxy_return",
        "quantile_method",
    ]


def symbol_stability_fieldnames() -> list[str]:
    return [
        "symbol",
        "period_type",
        "period_value",
        "category",
        "horizon_seconds",
        "row_count",
        "valid_forward_count",
        "mean_forward_proxy_return",
        "std_forward_proxy_return",
        "min_forward_proxy_return",
        "max_forward_proxy_return",
        "directional_diagnostic_rate",
        "directional_diagnostic_count",
        "directional_diagnostic_total",
    ]


def null_fieldnames() -> list[str]:
    return [
        "category",
        "horizon_seconds",
        "valid_forward_count",
        "category_mean_forward_proxy_return",
        "null_valid_forward_count",
        "null_mean_forward_proxy_return",
        "null_std_forward_proxy_return",
        "effect_vs_null",
        "effect_size_vs_null",
    ]


def candidate_fieldnames() -> list[str]:
    return [
        "candidate_rank",
        "category",
        "horizon_seconds",
        "valid_forward_count",
        "mean_forward_proxy_return",
        "null_mean_forward_proxy_return",
        "effect_vs_null",
        "effect_size_vs_null",
        "symbol_support_count",
        "symbol_consistent_count",
        "symbol_stability_rate",
        "month_support_count",
        "month_consistent_count",
        "month_stability_rate",
        "week_support_count",
        "week_consistent_count",
        "week_stability_rate",
        "directional_diagnostic_rate",
        "candidate_score",
        "research_note",
    ]


def compute_day_volatility_threshold(pairs: list[dict[str, Any]]) -> tuple[dict[tuple[str, str], float | None], float | None, dict[str, Any]]:
    vol_by_pair: dict[tuple[str, str], float | None] = {}
    values: list[float] = []
    started = time.monotonic()
    next_progress = started + PROGRESS_INTERVAL_SECONDS
    failed = 0
    for index, pair in enumerate(pairs, start=1):
        key = (str(pair["symbol"]), str(pair["file_date"]))
        try:
            _, rows = read_bookdepth_features(pair)
            value = day_volatility_proxy(rows)
            vol_by_pair[key] = value
            if value is not None:
                values.append(value)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            vol_by_pair[key] = None
            pair["volatility_error"] = f"{type(exc).__name__}: {exc}"
        if time.monotonic() >= next_progress:
            print(
                "progress phase=volatility "
                f"symbol_days={index}/{len(pairs)} failed={failed} "
                f"elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS
    threshold = statistics.median(values) if values else None
    metadata = {
        "volatility_threshold": threshold,
        "volatility_available_symbol_days": len(values),
        "volatility_failed_symbol_days": failed,
        "volatility_split_method": "median_day_depth_imbalance_delta_std",
    }
    return vol_by_pair, threshold, metadata


def aggregate_pair(
    pair: dict[str, Any],
    vol_by_pair: dict[tuple[str, str], float | None],
    volatility_threshold: float | None,
    category_horizon: dict[tuple[str, int], DistributionStats],
    horizon_null: dict[int, MomentStats],
    stability: dict[tuple[str, str, str, str, int], MomentStats],
) -> dict[str, Any]:
    timestamps, rows = build_feature_rows(pair)
    key = (str(pair["symbol"]), str(pair["file_date"]))
    day_vol = vol_by_pair.get(key)
    if day_vol is None or volatility_threshold is None:
        volatility_group = "UNAVAILABLE"
    else:
        volatility_group = "HIGH" if day_vol >= volatility_threshold else "LOW"

    category_counts: Counter[str] = Counter()
    observation_count = 0
    valid_forward_count = 0
    symbol = str(pair["symbol"])
    month = str(pair["year_month"])
    week = str(pair.get("week", ""))

    for row_index, row in enumerate(rows):
        category = str(row.get("absorption_category") or "INSUFFICIENT_DATA")
        if category not in CATEGORIES:
            category = "INSUFFICIENT_DATA"
        category_counts[category] += 1
        current_proxy = row_proxy_value(row)
        expected_direction = DIRECTION_BY_CATEGORY.get(category, 0)
        flow = row.get("flow_imbalance")
        depth = row.get("rolling_depth_imbalance_proxy")
        divergence = row.get("flow_depth_divergence_proxy")
        flow_value = None if flow is None else float(flow)
        depth_value = None if depth is None else float(depth)
        divergence_value = None if divergence is None else float(divergence)

        for horizon in HORIZON_SECONDS:
            future_index = bisect.bisect_left(timestamps, timestamps[row_index] + horizon * 1000, lo=row_index + 1)
            forward_value: float | None = None
            if current_proxy is not None and future_index < len(rows):
                future_proxy = row_proxy_value(rows[future_index])
                if future_proxy is not None:
                    forward_value = future_proxy - current_proxy
                    valid_forward_count += 1
            observation_count += 1

            dist_key = (category, horizon)
            if dist_key not in category_horizon:
                category_horizon[dist_key] = DistributionStats(seed_text=f"{category}:{horizon}")
            category_horizon[dist_key].add_diagnostic(
                forward_value,
                expected_direction,
                volatility_group,
                flow_value,
                depth_value,
                divergence_value,
            )
            horizon_null[horizon].add(forward_value, expected_direction)
            stability[(symbol, "ALL", "ALL", category, horizon)].add(forward_value, expected_direction)
            stability[(symbol, "MONTH", month, category, horizon)].add(forward_value, expected_direction)
            stability[(symbol, "WEEK", week, category, horizon)].add(forward_value, expected_direction)

    return {
        "symbol": symbol,
        "file_date": pair["file_date"],
        "row_count": len(rows),
        "observation_count": observation_count,
        "valid_forward_count": valid_forward_count,
        "category_counts": dict(category_counts),
        "day_volatility_proxy": day_vol,
        "volatility_group": volatility_group,
    }


def stability_rates(
    category: str,
    horizon: int,
    effect_vs_null: float | None,
    stability: dict[tuple[str, str, str, str, int], MomentStats],
) -> dict[str, Any]:
    if effect_vs_null is None or effect_vs_null == 0:
        direction = 0
    else:
        direction = 1 if effect_vs_null > 0 else -1
    result: dict[str, Any] = {}
    for period_type in ["ALL", "MONTH", "WEEK"]:
        support = 0
        consistent = 0
        min_count = 100 if period_type == "ALL" else 50
        for (symbol, candidate_period_type, _period_value, candidate_category, candidate_horizon), stats in stability.items():
            if candidate_period_type != period_type or candidate_category != category or candidate_horizon != horizon:
                continue
            mean_value = stats.mean()
            if mean_value is None or stats.valid_forward_count < min_count:
                continue
            support += 1
            if direction and sign_of(mean_value) == direction:
                consistent += 1
        prefix = "symbol" if period_type == "ALL" else period_type.lower()
        result[f"{prefix}_support_count"] = support
        result[f"{prefix}_consistent_count"] = consistent
        result[f"{prefix}_stability_rate"] = safe_div(consistent, support)
    return result


def write_category_horizon(category_horizon: dict[tuple[str, int], DistributionStats]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for category in CATEGORIES:
        for horizon in HORIZON_SECONDS:
            stats = category_horizon.get((category, horizon), DistributionStats(seed_text=f"{category}:{horizon}"))
            rows.append(distribution_row(category, horizon, stats))
    with CATEGORY_HORIZON_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=category_horizon_fieldnames())
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_symbol_stability(stability: dict[tuple[str, str, str, str, int], MomentStats]) -> dict[str, Any]:
    row_count = 0
    nonzero_rows = 0
    with SYMBOL_STABILITY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=symbol_stability_fieldnames())
        writer.writeheader()
        for key in sorted(stability):
            symbol, period_type, period_value, category, horizon = key
            stats = stability[key]
            if stats.row_count == 0:
                continue
            writer.writerow(moment_row(symbol, period_type, period_value, category, horizon, stats))
            row_count += 1
            if stats.valid_forward_count > 0:
                nonzero_rows += 1
    return {"stability_rows": row_count, "nonzero_stability_rows": nonzero_rows}


def write_null_and_candidates(
    category_horizon: dict[tuple[str, int], DistributionStats],
    horizon_null: dict[int, MomentStats],
    stability: dict[tuple[str, str, str, str, int], MomentStats],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    null_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    for category in CATEGORIES:
        for horizon in HORIZON_SECONDS:
            stats = category_horizon.get((category, horizon))
            null_stats = horizon_null[horizon]
            mean_value = stats.mean() if stats else None
            null_mean = null_stats.mean()
            null_std = null_stats.std()
            effect = mean_value - null_mean if mean_value is not None and null_mean is not None else None
            effect_size = safe_div(effect or 0.0, null_std) if effect is not None and null_std not in (None, 0) else None
            null_rows.append(
                {
                    "category": category,
                    "horizon_seconds": horizon,
                    "valid_forward_count": stats.valid_forward_count if stats else 0,
                    "category_mean_forward_proxy_return": rounded(mean_value),
                    "null_valid_forward_count": null_stats.valid_forward_count,
                    "null_mean_forward_proxy_return": rounded(null_mean),
                    "null_std_forward_proxy_return": rounded(null_std),
                    "effect_vs_null": rounded(effect),
                    "effect_size_vs_null": rounded(effect_size, 8),
                }
            )
            if not stats or effect is None or effect_size is None or stats.valid_forward_count < 500:
                continue
            stability_result = stability_rates(category, horizon, effect, stability)
            symbol_stability = stability_result.get("symbol_stability_rate")
            month_stability = stability_result.get("month_stability_rate")
            week_stability = stability_result.get("week_stability_rate")
            stability_score = statistics.mean(
                value for value in [symbol_stability, month_stability, week_stability] if value is not None
            ) if any(value is not None for value in [symbol_stability, month_stability, week_stability]) else 0.0
            count_weight = math.log10(stats.valid_forward_count + 10)
            candidate_score = abs(effect_size) * count_weight * stability_score
            candidate_rows.append(
                {
                    "candidate_rank": 0,
                    "category": category,
                    "horizon_seconds": horizon,
                    "valid_forward_count": stats.valid_forward_count,
                    "mean_forward_proxy_return": rounded(mean_value),
                    "null_mean_forward_proxy_return": rounded(null_mean),
                    "effect_vs_null": rounded(effect),
                    "effect_size_vs_null": rounded(effect_size, 8),
                    "symbol_support_count": stability_result.get("symbol_support_count", 0),
                    "symbol_consistent_count": stability_result.get("symbol_consistent_count", 0),
                    "symbol_stability_rate": rounded(symbol_stability, 6),
                    "month_support_count": stability_result.get("month_support_count", 0),
                    "month_consistent_count": stability_result.get("month_consistent_count", 0),
                    "month_stability_rate": rounded(month_stability, 6),
                    "week_support_count": stability_result.get("week_support_count", 0),
                    "week_consistent_count": stability_result.get("week_consistent_count", 0),
                    "week_stability_rate": rounded(week_stability, 6),
                    "directional_diagnostic_rate": rounded(stats.directional_rate(), 6),
                    "candidate_score": rounded(candidate_score, 8),
                    "research_note": "ranked_research_diagnostic_not_a_trading_rule",
                }
            )

    candidate_rows.sort(key=lambda row: float(row.get("candidate_score") or 0), reverse=True)
    for rank, row in enumerate(candidate_rows, start=1):
        row["candidate_rank"] = rank

    with NULL_COMPARISON_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=null_fieldnames())
        writer.writeheader()
        writer.writerows(null_rows)
    with CANDIDATES_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=candidate_fieldnames())
        writer.writeheader()
        writer.writerows(candidate_rows)
    return null_rows, candidate_rows


def write_summary_md(summary: dict[str, Any]) -> None:
    top_candidates = summary.get("top_candidates", [])
    lines = [
        "# Orderbook UM 81 streaming absorption discovery 90d v1",
        "",
        f"status: {summary['status']}",
        f"mode: {summary['mode']}",
        f"runtime_seconds: {summary['runtime_seconds']}",
        f"selected_symbol_count: {summary['selected_symbol_count']}",
        f"selected_symbol_days: {summary['selected_symbol_days']}",
        f"processed_symbol_days: {summary['processed_symbol_days']}",
        f"failed_symbol_days: {summary['failed_symbol_days']}",
        f"total_feature_rows_seen: {summary['total_feature_rows_seen']}",
        f"total_horizon_observations: {summary['total_horizon_observations']}",
        f"valid_forward_observations: {summary['valid_forward_observations']}",
        f"categories_found: {', '.join(summary['categories_found'])}",
        f"volatility_split_method: {summary.get('volatility_split_method', '')}",
        f"volatility_threshold: {summary.get('volatility_threshold', '')}",
        f"row_level_dataset_created: {str(summary['row_level_dataset_created']).lower()}",
        f"parquet_dataset_created: {str(summary['parquet_dataset_created']).lower()}",
        "",
        "## Top Candidates",
    ]
    if top_candidates:
        lines.append("| rank | category | horizon_seconds | effect_size_vs_null | stability | count |")
        lines.append("| ---: | --- | ---: | ---: | ---: | ---: |")
        for row in top_candidates[:10]:
            lines.append(
                "| "
                f"{row.get('candidate_rank')} | {row.get('category')} | {row.get('horizon_seconds')} | "
                f"{row.get('effect_size_vs_null')} | {row.get('symbol_stability_rate')} | "
                f"{row.get('valid_forward_count')} |"
            )
    else:
        lines.append("No candidate rows passed the minimum compact diagnostic gate.")
    lines.extend(
        [
            "",
            "## Outputs",
            f"- {CATEGORY_HORIZON_CSV.name}",
            f"- {SYMBOL_STABILITY_CSV.name}",
            f"- {NULL_COMPARISON_CSV.name}",
            f"- {CANDIDATES_CSV.name}",
            "",
            "The forward proxy return is the forward change in rolling depth-imbalance proxy, not a price or trade return.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def output_sizes() -> dict[str, int]:
    paths = [SUMMARY_JSON, SUMMARY_MD, CATEGORY_HORIZON_CSV, SYMBOL_STABILITY_CSV, NULL_COMPARISON_CSV, CANDIDATES_CSV]
    return {path.name: path.stat().st_size for path in paths if path.exists()}


def run_discovery() -> dict[str, Any]:
    started = time.monotonic()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if path_is_inside(DEFAULT_BOOKDEPTH_RAW_ROOT, REPO_ROOT) or path_is_inside(DEFAULT_AGGTRADES_RAW_ROOT, REPO_ROOT):
        raise RuntimeError("raw ZIP roots must stay outside repo")

    pairs = build_input_pairs()
    selected_symbols = sorted({str(pair["symbol"]) for pair in pairs})
    mode = "FULL_AVAILABLE_HISTORY" if os.environ.get(FULL_HISTORY_ENV, "").strip().upper() == "YES" else "LATEST_90D_ACTUAL_DISCOVERY"

    vol_by_pair, volatility_threshold, volatility_metadata = compute_day_volatility_threshold(pairs)
    category_horizon: dict[tuple[str, int], DistributionStats] = {}
    horizon_null: dict[int, MomentStats] = defaultdict(MomentStats)
    stability: dict[tuple[str, str, str, str, int], MomentStats] = defaultdict(MomentStats)

    processed_symbol_days = 0
    failed_symbol_days = 0
    total_feature_rows_seen = 0
    total_horizon_observations = 0
    valid_forward_observations = 0
    category_counts_total: Counter[str] = Counter()
    failure_examples: list[dict[str, str]] = []
    next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    for pair in pairs:
        try:
            result = aggregate_pair(pair, vol_by_pair, volatility_threshold, category_horizon, horizon_null, stability)
            processed_symbol_days += 1
            total_feature_rows_seen += int(result["row_count"])
            total_horizon_observations += int(result["observation_count"])
            valid_forward_observations += int(result["valid_forward_count"])
            category_counts_total.update(result["category_counts"])
        except Exception as exc:  # noqa: BLE001
            failed_symbol_days += 1
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
                "progress phase=discovery "
                f"processed_symbol_days={processed_symbol_days}/{len(pairs)} "
                f"failed_symbol_days={failed_symbol_days} "
                f"feature_rows={total_feature_rows_seen} "
                f"valid_forward_observations={valid_forward_observations} "
                f"elapsed_seconds={round(time.monotonic() - started, 1)}",
                flush=True,
            )
            next_progress = time.monotonic() + PROGRESS_INTERVAL_SECONDS

    category_rows = write_category_horizon(category_horizon)
    stability_metadata = write_symbol_stability(stability)
    null_rows, candidate_rows = write_null_and_candidates(category_horizon, horizon_null, stability)

    categories_found = [category for category in CATEGORIES if category_counts_total.get(category, 0) > 0]
    status = (
        "PASS_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_90D_COMPLETED"
        if processed_symbol_days > 0 and failed_symbol_days == 0 and len(selected_symbols) == EXPECTED_SYMBOL_COUNT
        else "PARTIAL_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_90D_COMPLETED"
    )
    runtime_seconds = round(time.monotonic() - started, 3)
    summary: dict[str, Any] = {
        "status": status,
        "created_at_utc": utc_now_text(),
        "task": "ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_90D_V1",
        "mode": mode,
        "full_history_env": FULL_HISTORY_ENV,
        "full_history_requested": os.environ.get(FULL_HISTORY_ENV, "").strip().upper() == "YES",
        "raw_bookdepth_root": str(DEFAULT_BOOKDEPTH_RAW_ROOT),
        "raw_aggtrades_root": str(DEFAULT_AGGTRADES_RAW_ROOT),
        "raw_roots_outside_repo": True,
        "selected_symbol_count": len(selected_symbols),
        "selected_symbols": selected_symbols,
        "selected_days_per_symbol": LATEST_DAYS_PER_SYMBOL if mode != "FULL_AVAILABLE_HISTORY" else "all_available",
        "selected_symbol_days": len(pairs),
        "processed_symbol_days": processed_symbol_days,
        "failed_symbol_days": failed_symbol_days,
        "failure_examples": failure_examples,
        "runtime_seconds": runtime_seconds,
        "horizon_seconds": HORIZON_SECONDS,
        "categories_expected": CATEGORIES,
        "categories_found": categories_found,
        "category_counts_total": dict(category_counts_total),
        "total_feature_rows_seen": total_feature_rows_seen,
        "total_horizon_observations": total_horizon_observations,
        "valid_forward_observations": valid_forward_observations,
        "forward_proxy_return_definition": "future rolling depth-imbalance proxy minus current rolling depth-imbalance proxy",
        "directional_diagnostic_rate_definition": "share of nonzero category-direction observations matching nonzero forward proxy direction",
        "row_level_dataset_created": False,
        "parquet_dataset_created": False,
        "downloads_run": False,
        "outputs": {
            "summary_json": str(SUMMARY_JSON),
            "summary_md": str(SUMMARY_MD),
            "category_horizon_csv": str(CATEGORY_HORIZON_CSV),
            "symbol_stability_csv": str(SYMBOL_STABILITY_CSV),
            "null_comparison_csv": str(NULL_COMPARISON_CSV),
            "candidates_csv": str(CANDIDATES_CSV),
        },
        "category_horizon_row_count": len(category_rows),
        "null_comparison_row_count": len(null_rows),
        "candidate_row_count": len(candidate_rows),
        "top_candidates": candidate_rows[:10],
        "stability_summary": stability_metadata,
        **volatility_metadata,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["output_sizes_bytes"] = output_sizes()
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_md(summary)
    return summary


def main() -> int:
    try:
        summary = run_discovery()
    except Exception as exc:  # noqa: BLE001
        error_summary = {
            "status": "FAILED_ORDERBOOK_UM_81_STREAMING_ABSORPTION_DISCOVERY_90D",
            "created_at_utc": utc_now_text(),
            "error": f"{type(exc).__name__}: {exc}",
            "row_level_dataset_created": False,
            "parquet_dataset_created": False,
            "downloads_run": False,
        }
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SUMMARY_JSON.write_text(json.dumps(error_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        SUMMARY_MD.write_text(
            "# Orderbook UM 81 streaming absorption discovery 90d v1\n\n"
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
