#!/usr/bin/env python
"""Build pilot-only aggTrades plus bookDepth absorption diagnostics."""

from __future__ import annotations

import bisect
import csv
import io
import json
import math
import os
import statistics
import sys
import zipfile
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import edge_factory_orderbook_um_pilot_feature_preview_v1 as bookdepth_preview  # noqa: E402


OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
BOOKDEPTH_FEATURE_SUMMARY = OUTPUTS_DIR / "orderbook_um_pilot_feature_preview_summary.json"
BOOKDEPTH_FEATURE_SAMPLE = OUTPUTS_DIR / "orderbook_um_pilot_feature_sample.csv"
AGGTRADES_SCHEMA_SUMMARY = OUTPUTS_DIR / "orderbook_um_aggtrades_pilot_schema_summary.json"
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_absorption_pilot_preview_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_absorption_pilot_preview_summary.md"
QUANTILE_CSV = OUTPUTS_DIR / "orderbook_um_absorption_pilot_quantile_diagnostics.csv"
CATEGORY_CSV = OUTPUTS_DIR / "orderbook_um_absorption_pilot_category_diagnostics.csv"
QUALITY_MD = OUTPUTS_DIR / "orderbook_um_absorption_pilot_quality_report.md"
SAMPLE_CSV = OUTPUTS_DIR / "orderbook_um_absorption_pilot_sample.csv"
SAMPLE_PARQUET = OUTPUTS_DIR / "orderbook_um_absorption_pilot_sample.parquet"

MAX_AGGTRADES_PER_FILE = int(os.environ.get("ORDERBOOK_ABSORPTION_MAX_AGGTRADES_PER_FILE", "5000000"))
MAX_SAMPLE_ROWS = int(os.environ.get("ORDERBOOK_ABSORPTION_SAMPLE_ROWS", "5000"))
WINDOW_SECONDS = [1, 5, 10]
FORWARD_COLUMNS = ["forward_return_10s", "forward_return_30s", "forward_return_60s", "forward_return_300s"]


class AbsorptionBlocked(RuntimeError):
    """Raised when the absorption preview must stop closed."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AbsorptionBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AbsorptionBlocked(f"input is not a JSON object: {path}")
    return payload


def bool_from_text(raw: Any) -> bool | None:
    text = str(raw).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def parse_float(raw: Any) -> float | None:
    try:
        value = float(str(raw).strip())
    except (TypeError, ValueError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def parse_timestamp_seconds(raw: Any) -> float | None:
    text = str(raw).strip()
    if not text:
        return None
    numeric = parse_float(text)
    if numeric is not None:
        if numeric > 10_000_000_000_000:
            return numeric / 1_000_000.0
        if numeric > 10_000_000_000:
            return numeric / 1000.0
        return numeric
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except ValueError:
        return None


def normalize_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


FIELD_ALIASES = {
    "aggregate_trade_id": ["aggregate_trade_id", "agg_trade_id", "aggtradeid", "a"],
    "price": ["price", "p"],
    "quantity": ["quantity", "qty", "q"],
    "first_trade_id": ["first_trade_id", "firsttradeid", "f"],
    "last_trade_id": ["last_trade_id", "lasttradeid", "l"],
    "timestamp": ["timestamp", "transact_time", "time", "t"],
    "is_buyer_maker": ["is_buyer_maker", "isbuyermaker", "buyer_is_maker", "m"],
    "is_best_match": ["is_best_match", "isbestmatch", "best_match", "M"],
}


def field_map(header: list[str]) -> dict[str, str]:
    normalized = {normalize_name(column): column for column in header}
    mapping: dict[str, str] = {}
    for canonical, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if normalize_name(alias) in normalized:
                mapping[canonical] = normalized[normalize_name(alias)]
                break
    return mapping


def looks_like_header(row: list[str]) -> bool:
    joined = ",".join(row).lower()
    return any(token in joined for token in ["price", "qty", "quantity", "timestamp", "buyer", "maker", "trade"])


def open_aggtrades_csv(zip_path: Path) -> tuple[zipfile.ZipFile, str, list[str], bool]:
    archive = zipfile.ZipFile(zip_path, "r")
    members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
    if len(members) != 1:
        archive.close()
        raise AbsorptionBlocked(f"expected exactly one aggTrades CSV member in {zip_path}, found {members}")
    with archive.open(members[0], "r") as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
        reader = csv.reader(text)
        first = next(reader, None)
    if not first:
        archive.close()
        raise AbsorptionBlocked(f"empty aggTrades CSV: {zip_path}")
    has_header = looks_like_header(first)
    if has_header:
        header = first
    else:
        header = [
            "aggregate_trade_id",
            "price",
            "quantity",
            "first_trade_id",
            "last_trade_id",
            "timestamp",
            "is_buyer_maker",
            "is_best_match",
        ][: len(first)]
    return archive, members[0], header, has_header


def iter_aggtrade_rows(zip_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    archive, member, header, has_header = open_aggtrades_csv(zip_path)
    mapping = field_map(header)
    required = {"price", "quantity", "timestamp", "is_buyer_maker"}
    missing = sorted(required - set(mapping))
    if missing:
        archive.close()
        raise AbsorptionBlocked(f"aggTrades schema missing required fields in {zip_path.name}: {missing}; header={header}")
    records: list[dict[str, Any]] = []
    malformed = 0
    with archive.open(member, "r") as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
        if has_header:
            reader: Any = csv.DictReader(text)
        else:
            reader = csv.DictReader(text, fieldnames=header)
        for raw_row in reader:
            if not raw_row:
                continue
            if len(records) + malformed >= MAX_AGGTRADES_PER_FILE:
                archive.close()
                raise AbsorptionBlocked(f"aggTrades row cap exceeded for {zip_path.name}")
            price = parse_float(raw_row.get(mapping["price"]))
            quantity = parse_float(raw_row.get(mapping["quantity"]))
            timestamp = parse_timestamp_seconds(raw_row.get(mapping["timestamp"]))
            buyer_maker = bool_from_text(raw_row.get(mapping["is_buyer_maker"]))
            if price is None or quantity is None or timestamp is None or buyer_maker is None or price <= 0 or quantity < 0:
                malformed += 1
                continue
            notional = price * quantity
            aggressive_buy = not buyer_maker
            records.append(
                {
                    "timestamp_epoch_seconds": timestamp,
                    "price": price,
                    "quantity": quantity,
                    "notional": notional,
                    "aggressive_buy": aggressive_buy,
                    "aggressive_sell": buyer_maker,
                }
            )
    archive.close()
    records.sort(key=lambda item: item["timestamp_epoch_seconds"])
    summary = {
        "zip_path": str(zip_path),
        "csv_member": member,
        "has_header": has_header,
        "header": header,
        "parsed_trade_rows": len(records),
        "malformed_trade_rows": malformed,
        "timestamp_min": datetime.fromtimestamp(records[0]["timestamp_epoch_seconds"], timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if records
        else None,
        "timestamp_max": datetime.fromtimestamp(records[-1]["timestamp_epoch_seconds"], timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if records
        else None,
    }
    return records, summary


def quantile_threshold(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return ordered[idx]


def prefix(values: list[float]) -> list[float]:
    out = [0.0]
    total = 0.0
    for value in values:
        total += value
        out.append(total)
    return out


def range_sum(prefix_values: list[float], start: int, end: int) -> float:
    return prefix_values[end] - prefix_values[start]


def build_trade_index(records: list[dict[str, Any]], large_threshold: float | None) -> dict[str, Any]:
    times = [row["timestamp_epoch_seconds"] for row in records]
    qty = [row["quantity"] for row in records]
    notional = [row["notional"] for row in records]
    buy_qty = [row["quantity"] if row["aggressive_buy"] else 0.0 for row in records]
    sell_qty = [row["quantity"] if row["aggressive_sell"] else 0.0 for row in records]
    buy_notional = [row["notional"] if row["aggressive_buy"] else 0.0 for row in records]
    sell_notional = [row["notional"] if row["aggressive_sell"] else 0.0 for row in records]
    large = [1.0 if large_threshold is not None and row["quantity"] >= large_threshold else 0.0 for row in records]
    return {
        "times": times,
        "qty": qty,
        "notional": notional,
        "prefix_qty": prefix(qty),
        "prefix_notional": prefix(notional),
        "prefix_buy_qty": prefix(buy_qty),
        "prefix_sell_qty": prefix(sell_qty),
        "prefix_buy_notional": prefix(buy_notional),
        "prefix_sell_notional": prefix(sell_notional),
        "prefix_large": prefix(large),
    }


def safe_imbalance(left_value: float, right_value: float) -> float | None:
    total = left_value + right_value
    if total <= 0:
        return None
    return (left_value - right_value) / total


def trade_window_features(index: dict[str, Any], timestamp: float, window_seconds: int) -> dict[str, Any]:
    times = index["times"]
    start = bisect.bisect_left(times, timestamp - window_seconds + 1e-9)
    end = bisect.bisect_right(times, timestamp)
    count = end - start
    total_qty = range_sum(index["prefix_qty"], start, end)
    total_notional = range_sum(index["prefix_notional"], start, end)
    buy_qty = range_sum(index["prefix_buy_qty"], start, end)
    sell_qty = range_sum(index["prefix_sell_qty"], start, end)
    buy_notional = range_sum(index["prefix_buy_notional"], start, end)
    sell_notional = range_sum(index["prefix_sell_notional"], start, end)
    window_qty = index["qty"][start:end]
    return {
        f"trade_count_{window_seconds}s": count,
        f"total_quantity_{window_seconds}s": total_qty,
        f"total_notional_{window_seconds}s": total_notional,
        f"aggressive_buy_quantity_{window_seconds}s": buy_qty,
        f"aggressive_sell_quantity_{window_seconds}s": sell_qty,
        f"aggressive_buy_notional_{window_seconds}s": buy_notional,
        f"aggressive_sell_notional_{window_seconds}s": sell_notional,
        f"trade_imbalance_qty_{window_seconds}s": safe_imbalance(buy_qty, sell_qty),
        f"trade_imbalance_notional_{window_seconds}s": safe_imbalance(buy_notional, sell_notional),
        f"avg_trade_size_{window_seconds}s": (total_qty / count) if count else None,
        f"max_trade_size_{window_seconds}s": max(window_qty) if window_qty else None,
        f"large_trade_count_{window_seconds}s": range_sum(index["prefix_large"], start, end),
    }


def add_rolling_trade_features(rows: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["symbol"], row["pilot_file_date"]), []).append(row)
    for group_rows in grouped.values():
        group_rows.sort(key=lambda item: item["timestamp_epoch_seconds"])
        imbalance_window: deque[float] = deque(maxlen=20)
        pressure_window: deque[float] = deque(maxlen=20)
        for row in group_rows:
            imbalance = row.get("trade_imbalance_qty_10s")
            pressure = None
            buy = row.get("aggressive_buy_notional_10s")
            sell = row.get("aggressive_sell_notional_10s")
            if buy is not None and sell is not None:
                pressure = buy - sell
            if isinstance(imbalance, (int, float)):
                imbalance_window.append(float(imbalance))
            if isinstance(pressure, (int, float)):
                pressure_window.append(float(pressure))
            row["rolling_trade_imbalance_qty_10s_mean_20"] = statistics.fmean(imbalance_window) if imbalance_window else None
            row["rolling_notional_pressure_10s_mean_20"] = statistics.fmean(pressure_window) if pressure_window else None


def category_for_row(row: dict[str, Any], high_notional_threshold: float | None) -> str:
    trade_imb = row.get("trade_imbalance_notional_10s")
    forward_60 = row.get("forward_return_60s")
    depth_imb = row.get("imbalance_1")
    depth_change = row.get("total_depth_pct1_change")
    total_notional = row.get("total_notional_10s")
    if trade_imb is None or forward_60 is None or depth_imb is None:
        return "INSUFFICIENT_DATA"
    high_notional = high_notional_threshold is not None and total_notional is not None and total_notional >= high_notional_threshold
    if trade_imb >= 0.25 and forward_60 <= 0:
        return "BUY_PRESSURE_ABSORBED"
    if trade_imb <= -0.25 and forward_60 >= 0:
        return "SELL_PRESSURE_ABSORBED"
    if trade_imb >= 0.15 and depth_imb >= 0.05:
        return "FLOW_AND_DEPTH_ALIGNED_UP"
    if trade_imb <= -0.15 and depth_imb <= -0.05:
        return "FLOW_AND_DEPTH_ALIGNED_DOWN"
    if high_notional and depth_change is not None and abs(trade_imb) >= 0.15 and depth_change < 0:
        return "MIXED_OR_NOISY"
    return "MIXED_OR_NOISY"


def add_absorption_categories(rows: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["symbol"], row["pilot_file_date"]), []).append(row)
    for group_rows in grouped.values():
        notionals = [row.get("total_notional_10s") for row in group_rows if isinstance(row.get("total_notional_10s"), (int, float))]
        threshold = quantile_threshold([float(value) for value in notionals], 0.75)
        for row in group_rows:
            row["absorption_category"] = category_for_row(row, threshold)
            row["absorption_high_notional_threshold_10s"] = threshold
            row["trade_depth_imbalance_divergence_10s"] = (
                None
                if row.get("trade_imbalance_notional_10s") is None or row.get("imbalance_1") is None
                else row["trade_imbalance_notional_10s"] - row["imbalance_1"]
            )
            row["fragility_flow_proxy_10s"] = (
                None
                if row.get("spread_bps_proxy_pct1") is None
                or row.get("liquidity_pull_proxy_pct1") is None
                or row.get("total_notional_10s") is None
                else row["spread_bps_proxy_pct1"] * row["liquidity_pull_proxy_pct1"] * row["total_notional_10s"]
            )


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def positive_rate(values: list[float]) -> float | None:
    return sum(1 for value in values if value > 0) / len(values) if values else None


def numeric(value: Any) -> float | None:
    return bookdepth_preview.numeric_value(value)


def category_diagnostics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_rows = len(rows)
    diagnostics: list[dict[str, Any]] = []
    categories = sorted({row.get("absorption_category", "INSUFFICIENT_DATA") for row in rows})
    for category in categories:
        category_rows = [row for row in rows if row.get("absorption_category") == category]
        item: dict[str, Any] = {
            "absorption_category": category,
            "count": len(category_rows),
            "total_rows": total_rows,
            "missing_rate": (total_rows - len(category_rows)) / total_rows if total_rows else None,
            "stability_warning": "sample_too_small" if len(category_rows) < 30 else "",
        }
        for forward in FORWARD_COLUMNS:
            values = [numeric(row.get(forward)) for row in category_rows]
            values = [value for value in values if value is not None]
            item[f"mean_{forward}"] = mean(values)
            item[f"median_{forward}"] = median(values)
            item[f"positive_rate_{forward}"] = positive_rate(values)
            item[f"count_{forward}"] = len(values)
        diagnostics.append(item)
    return diagnostics


def load_bookdepth_feature_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not BOOKDEPTH_FEATURE_SAMPLE.exists():
        raise AbsorptionBlocked(f"missing required feature sample: {BOOKDEPTH_FEATURE_SAMPLE}")
    schema_summary = bookdepth_preview.load_json(bookdepth_preview.PILOT_SCHEMA_SUMMARY)
    downloads = schema_summary.get("downloads")
    if not isinstance(downloads, list) or not downloads:
        raise AbsorptionBlocked("bookDepth pilot schema summary contains no downloads")
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for download in downloads:
        zip_path = bookdepth_preview.resolve_zip_path(download, bookdepth_preview.pilot_dir())
        parsed, summary = bookdepth_preview.parse_pilot_zip(download, zip_path)
        rows.extend(parsed)
        summaries.append(summary)
    bookdepth_preview.add_path_dependent_features(rows)
    bookdepth_preview.add_forward_diagnostics(rows)
    return rows, summaries


def load_aggtrade_indexes(schema_summary: dict[str, Any]) -> tuple[dict[tuple[str, str], dict[str, Any]], list[dict[str, Any]]]:
    indexes: dict[tuple[str, str], dict[str, Any]] = {}
    summaries: list[dict[str, Any]] = []
    downloads = schema_summary.get("downloads")
    if not isinstance(downloads, list) or not downloads:
        raise AbsorptionBlocked("aggTrades schema summary contains no downloads")
    for item in downloads:
        zip_path = Path(str(item.get("local_zip_path", "")))
        if not zip_path.exists():
            raise AbsorptionBlocked(f"aggTrades pilot ZIP missing: {zip_path}")
        if path_is_inside(zip_path, REPO_ROOT):
            raise AbsorptionBlocked(f"aggTrades pilot ZIP resolves inside repo: {zip_path}")
        records, parse_summary = iter_aggtrade_rows(zip_path)
        if not records:
            raise AbsorptionBlocked(f"no aggTrades records parsed from {zip_path}")
        threshold = quantile_threshold([record["quantity"] for record in records], 0.95)
        parse_summary["large_trade_quantity_threshold_95pct"] = threshold
        parse_summary["symbol"] = item.get("symbol")
        parse_summary["file_date_or_month"] = item.get("file_date_or_month")
        summaries.append(parse_summary)
        indexes[(str(item.get("symbol")), str(item.get("file_date_or_month")))] = build_trade_index(records, threshold)
    return indexes, summaries


def align_rows(bookdepth_rows: list[dict[str, Any]], agg_indexes: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    aligned: list[dict[str, Any]] = []
    for row in bookdepth_rows:
        key = (row["symbol"], row["pilot_file_date"])
        index = agg_indexes.get(key)
        if index is None:
            continue
        out = dict(row)
        for window in WINDOW_SECONDS:
            out.update(trade_window_features(index, row["timestamp_epoch_seconds"], window))
        aligned.append(out)
    add_rolling_trade_features(aligned)
    add_absorption_categories(aligned)
    return aligned


def quantile_diagnostics(rows: list[dict[str, Any]], feature_columns: list[str]) -> list[dict[str, Any]]:
    return bookdepth_preview.quantile_diagnostics(rows, feature_columns)


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM absorption pilot preview v1",
        "",
        f"status: {summary['status']}",
        f"created_at_utc: {summary['created_at_utc']}",
        f"aggtrades_pilot_zips_parsed: {summary['aggtrades_pilot_zips_parsed']}",
        f"aligned_bookdepth_rows: {summary['aligned_bookdepth_rows']}",
        f"recommended_next_step: {summary['recommended_next_step']}",
        "",
        "## Trade-flow features",
    ]
    lines.extend(f"- {feature}" for feature in summary["derived_trade_flow_features"])
    lines.extend(["", "## Absorption categories"])
    for category, count in summary["absorption_category_counts"].items():
        lines.append(f"- {category}: {count}")
    lines.extend(["", "replacement_checks_all_true=true", ""])
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_quality_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM absorption pilot quality report v1",
        "",
        f"status: {summary['status']}",
        f"missing_or_malformed_aggtrade_rows: {summary['missing_or_malformed_aggtrade_rows']}",
        f"forward_diagnostic_availability: {json.dumps(summary['forward_diagnostic_availability'], sort_keys=True)}",
        f"no_future_leakage: {summary['alignment_method']['no_future_leakage']}",
        "",
        "## Parsed rows",
    ]
    for item in summary["aggtrade_parse_summaries"]:
        lines.append(
            f"- {item['symbol']} {item['file_date_or_month']}: rows={item['parsed_trade_rows']}, malformed={item['malformed_trade_rows']}, range={item['timestamp_min']} to {item['timestamp_max']}"
        )
    lines.append("")
    QUALITY_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        if path_is_inside(data_root(), REPO_ROOT):
            raise AbsorptionBlocked(f"data root resolves inside repo: {data_root()}")
        bookdepth_summary = load_json(BOOKDEPTH_FEATURE_SUMMARY)
        schema_summary = load_json(AGGTRADES_SCHEMA_SUMMARY)
        if schema_summary.get("replacement_checks_all_true") is not True:
            raise AbsorptionBlocked("aggTrades schema summary did not pass replacement checks")
        bookdepth_rows, bookdepth_parse_summaries = load_bookdepth_feature_rows()
        agg_indexes, agg_summaries = load_aggtrade_indexes(schema_summary)
        aligned = align_rows(bookdepth_rows, agg_indexes)
        if not aligned:
            raise AbsorptionBlocked("no aligned bookDepth plus aggTrades rows produced")
        trade_features = [
            f"{base}_{window}s"
            for window in WINDOW_SECONDS
            for base in [
                "trade_count",
                "total_quantity",
                "total_notional",
                "aggressive_buy_quantity",
                "aggressive_sell_quantity",
                "aggressive_buy_notional",
                "aggressive_sell_notional",
                "trade_imbalance_qty",
                "trade_imbalance_notional",
                "avg_trade_size",
                "max_trade_size",
                "large_trade_count",
            ]
        ] + [
            "rolling_trade_imbalance_qty_10s_mean_20",
            "rolling_notional_pressure_10s_mean_20",
            "trade_depth_imbalance_divergence_10s",
            "fragility_flow_proxy_10s",
        ]
        bookdepth_features = [
            "mid_price_proxy_pct1",
            "spread_bps_proxy_pct1",
            "imbalance_1",
            "imbalance_5",
            "liquidity_pull_proxy_pct1",
            "rolling_imbalance_1_mean_20",
        ]
        numeric_features = [
            feature
            for feature in trade_features + bookdepth_features
            if any(numeric(row.get(feature)) is not None for row in aligned)
        ]
        quantiles = quantile_diagnostics(aligned, numeric_features)
        categories = category_diagnostics(aligned)
        sample_rows = aligned[:MAX_SAMPLE_ROWS]
        id_columns = ["timestamp", "symbol", "pilot_file_date", "absorption_category"]
        numeric_columns = sorted({key for row in sample_rows for key, value in row.items() if numeric(value) is not None})
        sample_fields = id_columns + [column for column in numeric_columns if column not in id_columns]
        bookdepth_preview.write_csv_rows(SAMPLE_CSV, sample_rows, sample_fields)
        parquet_written, parquet_error = bookdepth_preview.try_write_parquet(SAMPLE_PARQUET, sample_rows, sample_fields)
        diagnostic_fields = [
            "feature",
            "quantile",
            "count",
            "total_rows",
            "missing_rate",
            "feature_min",
            "feature_max",
            "stability_warning",
        ]
        for forward in FORWARD_COLUMNS:
            diagnostic_fields.extend([f"mean_{forward}", f"median_{forward}", f"positive_rate_{forward}", f"count_{forward}"])
        bookdepth_preview.write_csv_rows(QUANTILE_CSV, quantiles, diagnostic_fields)
        category_fields = [
            "absorption_category",
            "count",
            "total_rows",
            "missing_rate",
            "stability_warning",
        ]
        for forward in FORWARD_COLUMNS:
            category_fields.extend([f"mean_{forward}", f"median_{forward}", f"positive_rate_{forward}", f"count_{forward}"])
        bookdepth_preview.write_csv_rows(CATEGORY_CSV, categories, category_fields)
        category_counts = dict(Counter(row["absorption_category"] for row in aligned))
        forward_availability = {
            forward: sum(1 for row in aligned if numeric(row.get(forward)) is not None) for forward in FORWARD_COLUMNS
        }
        summary = {
            "status": "PASS_ORDERBOOK_UM_ABSORPTION_PILOT_PREVIEW_CREATED",
            "created_at_utc": utc_now_text(),
            "task_name": "ORDERBOOK_UM_AGGTRADES_PILOT_ABSORPTION_PREVIEW_V1",
            "data_root": str(data_root()),
            "aggtrades_pilot_zips_found": schema_summary.get("pilot_aggtrades_download_count"),
            "aggtrades_pilot_zips_downloaded": schema_summary.get("pilot_aggtrades_download_count"),
            "aggtrades_pilot_zips_parsed": len(agg_summaries),
            "checksum_verification_results": {
                f"{item['symbol']}|{item['file_date_or_month']}": item.get("checksum_verified")
                for item in schema_summary.get("downloads", [])
            },
            "detected_aggtrades_schema": {
                f"{item['symbol']}|{item['file_date_or_month']}": item.get("schema", {}).get("header")
                for item in schema_summary.get("downloads", [])
            },
            "parsed_symbols_dates": sorted(f"{item['symbol']}|{item['file_date_or_month']}" for item in agg_summaries),
            "rows_parsed_per_symbol_day": {
                f"{item['symbol']}|{item['file_date_or_month']}": item["parsed_trade_rows"] for item in agg_summaries
            },
            "aggregation_bucket_sizes_used_seconds": WINDOW_SECONDS,
            "derived_trade_flow_features": numeric_features,
            "alignment_method": {
                "method": "trailing aggTrades windows ending at each bookDepth timestamp",
                "no_future_leakage": True,
                "feature_rule": "For timestamp T, trade-flow features include only aggTrades with timestamps <= T.",
                "forward_diagnostics_rule": "Forward returns are retained only as diagnostics from bookDepth mid proxy columns.",
            },
            "aligned_bookdepth_rows": len(aligned),
            "absorption_categories": [
                "BUY_PRESSURE_ABSORBED",
                "SELL_PRESSURE_ABSORBED",
                "FLOW_AND_DEPTH_ALIGNED_UP",
                "FLOW_AND_DEPTH_ALIGNED_DOWN",
                "MIXED_OR_NOISY",
                "INSUFFICIENT_DATA",
            ],
            "absorption_category_counts": category_counts,
            "forward_diagnostic_availability": forward_availability,
            "missing_or_malformed_aggtrade_rows": sum(item["malformed_trade_rows"] for item in agg_summaries),
            "duplicate_timestamp_notes": "aggTrades can share timestamps; aggregation preserves counts rather than requiring unique timestamps.",
            "bookdepth_parse_summaries": bookdepth_parse_summaries,
            "aggtrade_parse_summaries": agg_summaries,
            "quantile_diagnostic_row_count": len(quantiles),
            "category_diagnostic_row_count": len(categories),
            "sample_row_count": len(sample_rows),
            "parquet_written": parquet_written,
            "parquet_error": parquet_error,
            "output_files": {
                "summary_json": str(SUMMARY_JSON),
                "summary_md": str(SUMMARY_MD),
                "quantile_diagnostics_csv": str(QUANTILE_CSV),
                "category_diagnostics_csv": str(CATEGORY_CSV),
                "quality_report_md": str(QUALITY_MD),
                "sample_csv": str(SAMPLE_CSV),
                "sample_parquet": str(SAMPLE_PARQUET) if parquet_written else "",
            },
            "suitable_for_next_step": "PILOT_ABSORPTION_DIAGNOSTICS_ONLY_NOT_FOR_TRADING_USE",
            "recommended_next_step": "B_EXPAND_PILOT_TO_30_DAYS_FOR_BTC_ETH_SOL_ONLY",
            "full_historical_download_attempted": False,
            "replacement_checks_all_true": True,
        }
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_summary_md(summary)
        write_quality_md(summary)
        print(f"status: {summary['status']}")
        print(f"aggtrades_pilot_zips_parsed: {summary['aggtrades_pilot_zips_parsed']}")
        print(f"aligned_bookdepth_rows: {summary['aligned_bookdepth_rows']}")
        print(f"absorption_categories: {json.dumps(summary['absorption_category_counts'], sort_keys=True)}")
        print(f"summary_json: {SUMMARY_JSON}")
        print(f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}")
        print(f"recommended_next_step: {summary['recommended_next_step']}")
        return 0
    except AbsorptionBlocked as exc:
        payload = {
            "status": "BLOCKED_ORDERBOOK_UM_ABSORPTION_PILOT_PREVIEW",
            "created_at_utc": utc_now_text(),
            "exact_blocker": str(exc),
            "replacement_checks_all_true": False,
            "recommended_next_step": "D_STOP_DUE_TO_UNSUPPORTED_SCHEMA_OR_INSUFFICIENT_ALIGNMENT",
        }
        SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        print(f"BLOCKED: {exc}")
        print("replacement_checks_all_true=false")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
