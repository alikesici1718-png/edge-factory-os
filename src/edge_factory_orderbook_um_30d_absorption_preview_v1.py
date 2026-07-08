#!/usr/bin/env python
"""Build BTC/ETH/SOL 30-day diagnostic-only absorption preview from pilot ZIPs."""

from __future__ import annotations

import csv
import io
import json
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

import edge_factory_orderbook_um_absorption_pilot_preview_v1 as absorption_pilot  # noqa: E402
import edge_factory_orderbook_um_pilot_feature_preview_v1 as bookdepth_preview  # noqa: E402


OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
MANIFEST_CSV = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest.csv"
MANIFEST_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_manifest_summary.json"
DOWNLOAD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_download_summary.json"
SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_absorption_preview_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_30d_absorption_preview_summary.md"
CATEGORY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_category_diagnostics.csv"
QUANTILE_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_quantile_diagnostics.csv"
DAILY_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_daily_stability.csv"
SYMBOL_STABILITY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_symbol_stability.csv"
QUALITY_MD = OUTPUTS_DIR / "orderbook_um_30d_absorption_quality_report.md"
SAMPLE_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_sample.csv"
SAMPLE_PARQUET = OUTPUTS_DIR / "orderbook_um_30d_absorption_sample.parquet"

TARGET_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
WINDOW_SECONDS = [1, 5, 10]
FORWARD_COLUMNS = ["forward_return_10s", "forward_return_30s", "forward_return_60s", "forward_return_300s"]
MAX_SAMPLE_ROWS = int(os.environ.get("ORDERBOOK_30D_ABSORPTION_SAMPLE_ROWS", "10000"))
CATEGORIES = [
    "BUY_PRESSURE_ABSORBED",
    "SELL_PRESSURE_ABSORBED",
    "FLOW_AND_DEPTH_ALIGNED_UP",
    "FLOW_AND_DEPTH_ALIGNED_DOWN",
    "MIXED_OR_NOISY",
    "INSUFFICIENT_DATA",
]


class PreviewBlocked(RuntimeError):
    """Raised when the 30-day absorption preview must stop closed."""


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
        raise PreviewBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PreviewBlocked(f"input is not a JSON object: {path}")
    return payload


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST_CSV.exists():
        raise PreviewBlocked(f"missing required manifest: {MANIFEST_CSV}")
    with MANIFEST_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 90:
        raise PreviewBlocked(f"30d manifest row count is not 90: {len(rows)}")
    symbols = {row.get("symbol", "") for row in rows}
    if symbols != set(TARGET_SYMBOLS):
        raise PreviewBlocked(f"30d manifest symbols are not exactly BTC/ETH/SOL: {sorted(symbols)}")
    incomplete = [f"{row.get('symbol')}|{row.get('file_date')}|{row.get('status')}" for row in rows if row.get("status") != "AVAILABLE"]
    if incomplete:
        raise PreviewBlocked(f"30d manifest is incomplete: {incomplete[:20]}")
    return sorted(rows, key=lambda row: (row["file_date"], row["symbol"]))


def download_lookup(summary: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    downloads = summary.get("downloads")
    if not isinstance(downloads, list) or not downloads:
        raise PreviewBlocked("download summary contains no downloads")
    lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in downloads:
        if not isinstance(item, dict):
            continue
        key = (str(item.get("symbol")), str(item.get("file_date")), str(item.get("asset_type")))
        lookup[key] = item
    return lookup


def assert_verified(download: dict[str, Any], asset_type: str, symbol: str, day: str) -> Path:
    if download.get("checksum_verified") is not True:
        raise PreviewBlocked(f"{asset_type} checksum not verified for {symbol} {day}")
    path = Path(str(download.get("local_zip_path", "")))
    if not path.exists():
        raise PreviewBlocked(f"{asset_type} ZIP missing for {symbol} {day}: {path}")
    if path_is_inside(path, REPO_ROOT):
        raise PreviewBlocked(f"{asset_type} ZIP resolves inside repo: {path}")
    return path


def parse_aggtrade_raw(raw_row: dict[str, str], mapping: dict[str, str]) -> dict[str, Any] | None:
    price = absorption_pilot.parse_float(raw_row.get(mapping["price"]))
    quantity = absorption_pilot.parse_float(raw_row.get(mapping["quantity"]))
    timestamp = absorption_pilot.parse_timestamp_seconds(raw_row.get(mapping["timestamp"]))
    buyer_maker = absorption_pilot.bool_from_text(raw_row.get(mapping["is_buyer_maker"]))
    if price is None or quantity is None or timestamp is None or buyer_maker is None or price <= 0 or quantity < 0:
        return None
    return {
        "timestamp_epoch_seconds": timestamp,
        "quantity": quantity,
        "notional": price * quantity,
        "aggressive_buy": not buyer_maker,
        "aggressive_sell": buyer_maker,
    }


def open_agg_reader(zip_path: Path) -> tuple[zipfile.ZipFile, Any, dict[str, str], list[str], bool]:
    archive, member, header, has_header = absorption_pilot.open_aggtrades_csv(zip_path)
    mapping = absorption_pilot.field_map(header)
    required = {"price", "quantity", "timestamp", "is_buyer_maker"}
    missing = sorted(required - set(mapping))
    if missing:
        archive.close()
        raise PreviewBlocked(f"aggTrades schema missing required fields in {zip_path.name}: {missing}; header={header}")
    raw = archive.open(member, "r")
    text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
    reader: Any = csv.DictReader(text) if has_header else csv.DictReader(text, fieldnames=header)
    return archive, reader, mapping, header, has_header


def aggtrade_scan_summary(zip_path: Path) -> dict[str, Any]:
    archive, reader, mapping, header, has_header = open_agg_reader(zip_path)
    quantities: list[float] = []
    malformed = 0
    timestamp_min: float | None = None
    timestamp_max: float | None = None
    try:
        for raw_row in reader:
            record = parse_aggtrade_raw(raw_row, mapping)
            if record is None:
                malformed += 1
                continue
            timestamp = float(record["timestamp_epoch_seconds"])
            timestamp_min = timestamp if timestamp_min is None else min(timestamp_min, timestamp)
            timestamp_max = timestamp if timestamp_max is None else max(timestamp_max, timestamp)
            quantities.append(float(record["quantity"]))
    finally:
        archive.close()
    threshold = absorption_pilot.quantile_threshold(quantities, 0.95)
    return {
        "zip_path": str(zip_path),
        "has_header": has_header,
        "header": header,
        "parsed_trade_rows": len(quantities),
        "malformed_trade_rows": malformed,
        "timestamp_min": datetime.fromtimestamp(timestamp_min, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if timestamp_min is not None
        else None,
        "timestamp_max": datetime.fromtimestamp(timestamp_max, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if timestamp_max is not None
        else None,
        "large_trade_quantity_threshold_95pct": threshold,
    }


def empty_trade_features(window_seconds: int) -> dict[str, Any]:
    return {
        f"trade_count_{window_seconds}s": 0,
        f"total_quantity_{window_seconds}s": 0.0,
        f"total_notional_{window_seconds}s": 0.0,
        f"aggressive_buy_quantity_{window_seconds}s": 0.0,
        f"aggressive_sell_quantity_{window_seconds}s": 0.0,
        f"aggressive_buy_notional_{window_seconds}s": 0.0,
        f"aggressive_sell_notional_{window_seconds}s": 0.0,
        f"trade_imbalance_qty_{window_seconds}s": None,
        f"trade_imbalance_notional_{window_seconds}s": None,
        f"avg_trade_size_{window_seconds}s": None,
        f"max_trade_size_{window_seconds}s": None,
        f"large_trade_count_{window_seconds}s": 0.0,
    }


def window_features_from_buffer(trades: deque[dict[str, Any]], timestamp: float, window_seconds: int, large_threshold: float | None) -> dict[str, Any]:
    start_time = timestamp - window_seconds + 1e-9
    relevant = [trade for trade in trades if trade["timestamp_epoch_seconds"] >= start_time]
    if not relevant:
        return empty_trade_features(window_seconds)
    total_qty = sum(float(trade["quantity"]) for trade in relevant)
    total_notional = sum(float(trade["notional"]) for trade in relevant)
    buy_qty = sum(float(trade["quantity"]) for trade in relevant if trade["aggressive_buy"])
    sell_qty = sum(float(trade["quantity"]) for trade in relevant if trade["aggressive_sell"])
    buy_notional = sum(float(trade["notional"]) for trade in relevant if trade["aggressive_buy"])
    sell_notional = sum(float(trade["notional"]) for trade in relevant if trade["aggressive_sell"])
    quantities = [float(trade["quantity"]) for trade in relevant]
    return {
        f"trade_count_{window_seconds}s": len(relevant),
        f"total_quantity_{window_seconds}s": total_qty,
        f"total_notional_{window_seconds}s": total_notional,
        f"aggressive_buy_quantity_{window_seconds}s": buy_qty,
        f"aggressive_sell_quantity_{window_seconds}s": sell_qty,
        f"aggressive_buy_notional_{window_seconds}s": buy_notional,
        f"aggressive_sell_notional_{window_seconds}s": sell_notional,
        f"trade_imbalance_qty_{window_seconds}s": absorption_pilot.safe_imbalance(buy_qty, sell_qty),
        f"trade_imbalance_notional_{window_seconds}s": absorption_pilot.safe_imbalance(buy_notional, sell_notional),
        f"avg_trade_size_{window_seconds}s": total_qty / len(relevant),
        f"max_trade_size_{window_seconds}s": max(quantities),
        f"large_trade_count_{window_seconds}s": sum(1 for quantity in quantities if large_threshold is not None and quantity >= large_threshold),
    }


def align_aggtrades_streaming(bookdepth_rows: list[dict[str, Any]], agg_zip: Path, large_threshold: float | None) -> list[dict[str, Any]]:
    archive, reader, mapping, _header, _has_header = open_agg_reader(agg_zip)
    aligned: list[dict[str, Any]] = []
    trades: deque[dict[str, Any]] = deque()
    pending: dict[str, Any] | None = None
    max_window = max(WINDOW_SECONDS)
    malformed_second_pass = 0
    try:
        iterator = iter(reader)
        for bd_row in sorted(bookdepth_rows, key=lambda item: item["timestamp_epoch_seconds"]):
            timestamp = float(bd_row["timestamp_epoch_seconds"])
            while True:
                if pending is None:
                    try:
                        raw_row = next(iterator)
                    except StopIteration:
                        break
                    pending = parse_aggtrade_raw(raw_row, mapping)
                    if pending is None:
                        malformed_second_pass += 1
                        continue
                if float(pending["timestamp_epoch_seconds"]) <= timestamp:
                    trades.append(pending)
                    pending = None
                    continue
                break
            cutoff = timestamp - max_window + 1e-9
            while trades and float(trades[0]["timestamp_epoch_seconds"]) < cutoff:
                trades.popleft()
            out = dict(bd_row)
            for window in WINDOW_SECONDS:
                out.update(window_features_from_buffer(trades, timestamp, window, large_threshold))
            aligned.append(out)
    finally:
        archive.close()
    for row in aligned:
        row["aggtrade_malformed_second_pass_rows"] = malformed_second_pass
    absorption_pilot.add_rolling_trade_features(aligned)
    absorption_pilot.add_absorption_categories(aligned)
    return aligned


def numeric(value: Any) -> float | None:
    return bookdepth_preview.numeric_value(value)


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def positive_rate(values: list[float]) -> float | None:
    return sum(1 for value in values if value > 0) / len(values) if values else None


def parse_symbol_day(row: dict[str, str], downloads: dict[tuple[str, str, str], dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    symbol = row["symbol"]
    day = row["file_date"]
    bd_download = downloads.get((symbol, day, "bookDepth"))
    agg_download = downloads.get((symbol, day, "aggTrades"))
    if not bd_download or not agg_download:
        raise PreviewBlocked(f"download summary missing pair for {symbol} {day}")
    bd_zip = assert_verified(bd_download, "bookDepth", symbol, day)
    agg_zip = assert_verified(agg_download, "aggTrades", symbol, day)
    bd_rows, bd_summary = bookdepth_preview.parse_pilot_zip({"symbol": symbol, "file_date_or_month": day}, bd_zip)
    if not bd_rows:
        raise PreviewBlocked(f"no bookDepth rows parsed for {symbol} {day}")
    bookdepth_preview.add_path_dependent_features(bd_rows)
    bookdepth_preview.add_forward_diagnostics(bd_rows)
    agg_summary = aggtrade_scan_summary(agg_zip)
    if not agg_summary["parsed_trade_rows"]:
        raise PreviewBlocked(f"no aggTrades rows parsed for {symbol} {day}")
    threshold = agg_summary["large_trade_quantity_threshold_95pct"]
    aligned = align_aggtrades_streaming(bd_rows, agg_zip, threshold)
    agg_summary.update(
        {
            "symbol": symbol,
            "file_date_or_month": day,
            "zip_bytes": agg_zip.stat().st_size,
        }
    )
    file_summary = {
        "symbol": symbol,
        "file_date": day,
        "bookdepth": bd_summary,
        "aggtrades": agg_summary,
        "aligned_rows": len(aligned),
        "category_counts": dict(Counter(item.get("absorption_category", "INSUFFICIENT_DATA") for item in aligned)),
        "missing_or_malformed_rows": bd_summary.get("missing_timestamp_or_malformed_row_count", 0) + agg_summary.get("malformed_trade_rows", 0),
    }
    return aligned, file_summary


def trade_feature_list(rows: list[dict[str, Any]]) -> list[str]:
    expected = [
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
        "mid_price_proxy_pct1",
        "spread_bps_proxy_pct1",
        "imbalance_1",
        "imbalance_5",
        "liquidity_pull_proxy_pct1",
        "rolling_imbalance_1_mean_20",
    ]
    return [feature for feature in expected if any(numeric(row.get(feature)) is not None for row in rows)]


def forward_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    for forward in FORWARD_COLUMNS:
        values = [numeric(row.get(forward)) for row in rows]
        values = [value for value in values if value is not None]
        stats[f"mean_{forward}"] = mean(values)
        stats[f"median_{forward}"] = median(values)
        stats[f"positive_rate_{forward}"] = positive_rate(values)
        stats[f"count_{forward}"] = len(values)
        stats[f"missing_rate_{forward}"] = (len(rows) - len(values)) / len(rows) if rows else None
    return stats


def category_diagnostics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return absorption_pilot.category_diagnostics(rows)


def quantile_diagnostics(rows: list[dict[str, Any]], features: list[str]) -> list[dict[str, Any]]:
    return bookdepth_preview.quantile_diagnostics(rows, features)


def daily_stability(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["symbol"], row["pilot_file_date"]), []).append(row)
    volatility_scores: dict[tuple[str, str], float | None] = {}
    for key, group_rows in grouped.items():
        values = [numeric(row.get("rolling_mid_return_vol_proxy_20")) for row in group_rows]
        values = [value for value in values if value is not None]
        volatility_scores[key] = mean(values)
    available_scores = [score for score in volatility_scores.values() if score is not None]
    median_vol = median(available_scores) if available_scores else None
    total_rows = len(rows)
    output: list[dict[str, Any]] = []
    for (symbol, day), group_rows in sorted(grouped.items()):
        day_obj = datetime.strptime(day, "%Y-%m-%d").date()
        item: dict[str, Any] = {
            "symbol": symbol,
            "file_date": day,
            "day_of_week": day_obj.strftime("%A"),
            "is_weekend": day_obj.weekday() >= 5,
            "aligned_rows": len(group_rows),
            "row_share": len(group_rows) / total_rows if total_rows else None,
            "volatility_score": volatility_scores[(symbol, day)],
            "volatility_bucket": "unavailable"
            if median_vol is None or volatility_scores[(symbol, day)] is None
            else ("high_volatility" if float(volatility_scores[(symbol, day)]) >= median_vol else "low_volatility"),
        }
        for category in CATEGORIES:
            item[f"category_count_{category}"] = sum(1 for row in group_rows if row.get("absorption_category") == category)
        item.update(forward_stats(group_rows))
        output.append(item)
    max_day_share = max((item["row_share"] or 0 for item in output), default=0)
    vol_bucket_counts = dict(Counter(str(item["volatility_bucket"]) for item in output))
    summary = {
        "symbol_day_count": len(output),
        "max_symbol_day_row_share": max_day_share,
        "volatility_bucket_counts": vol_bucket_counts,
    }
    return output, summary


def symbol_stability(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["symbol"], []).append(row)
    total_rows = len(rows)
    output: list[dict[str, Any]] = []
    for symbol, group_rows in sorted(grouped.items()):
        item: dict[str, Any] = {
            "symbol": symbol,
            "aligned_rows": len(group_rows),
            "row_share": len(group_rows) / total_rows if total_rows else None,
            "distinct_days": len({row["pilot_file_date"] for row in group_rows}),
        }
        category_counts = Counter(row.get("absorption_category", "INSUFFICIENT_DATA") for row in group_rows)
        for category in CATEGORIES:
            item[f"category_count_{category}"] = category_counts.get(category, 0)
        item["largest_category_share"] = max(category_counts.values()) / len(group_rows) if group_rows and category_counts else None
        item.update(forward_stats(group_rows))
        output.append(item)
    summary = {
        "symbol_count": len(output),
        "max_symbol_row_share": max((item["row_share"] or 0 for item in output), default=0),
        "max_largest_category_share_by_symbol": max((item["largest_category_share"] or 0 for item in output), default=0),
    }
    return output, summary


def stability_warnings(daily_summary: dict[str, Any], symbol_summary: dict[str, Any], category_counts: dict[str, int]) -> list[str]:
    warnings: list[str] = []
    if daily_summary.get("max_symbol_day_row_share", 0) > 0.08:
        warnings.append("one_symbol_day_exceeds_8pct_of_aligned_rows")
    if symbol_summary.get("max_symbol_row_share", 0) > 0.45:
        warnings.append("one_symbol_exceeds_45pct_of_aligned_rows")
    nonzero_categories = [category for category, count in category_counts.items() if count > 0]
    if len(nonzero_categories) < 4:
        warnings.append("fewer_than_four_absorption_categories_present")
    for category, count in category_counts.items():
        if count and count < 100:
            warnings.append(f"category_sample_small_{category}")
    return warnings


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    bookdepth_preview.write_csv_rows(path, rows, fieldnames)


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d absorption preview summary v1",
        "",
        f"status: {summary['status']}",
        f"selected_window: {summary['selected_start_date']} to {summary['selected_end_date']}",
        f"symbols_parsed: {', '.join(summary['symbols_parsed'])}",
        f"aligned_rows: {summary['aligned_row_count']}",
        f"recommended_next_step: {summary['recommended_next_step']}",
        "",
        "## Absorption categories",
    ]
    for category, count in summary["absorption_category_counts"].items():
        lines.append(f"- {category}: {count}")
    lines.extend(["", "## Stability warnings"])
    warnings = summary.get("stability_warnings") or []
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- none")
    lines.extend(["", f"replacement_checks_all_true={str(summary['replacement_checks_all_true']).lower()}", ""])
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_quality_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d absorption quality report v1",
        "",
        f"status: {summary['status']}",
        f"no_future_leakage: {summary['alignment_method']['no_future_leakage']}",
        f"checksum_verified_file_count: {summary['checksum_verification_summary']['verified_file_count']}",
        f"missing_or_malformed_row_count: {summary['missing_or_malformed_row_count']}",
        "",
        "## Binance aggTrades convention",
        "- isBuyerMaker=true means the buyer was maker, so the aggressive/taker side is sell.",
        "- isBuyerMaker=false means the buyer was taker, so the aggressive/taker side is buy.",
        "",
        "## Parsed rows per symbol/day",
    ]
    for key, value in sorted(summary["aligned_rows_per_symbol_day"].items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    QUALITY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_blocked(reason: str) -> int:
    payload = {
        "status": "BLOCKED_ORDERBOOK_UM_30D_ABSORPTION_PREVIEW",
        "created_at_utc": utc_now_text(),
        "exact_blocker": reason,
        "replacement_checks_all_true": False,
        "recommended_next_step": "D_STOP_DUE_TO_WEAK_OR_UNSTABLE_DIAGNOSTICS",
        "next_module": "ORDERBOOK_UM_30D_ABSORPTION_BLOCKER_REVIEW",
        "full_81_symbol_download_attempted": False,
    }
    SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    write_summary_md({**payload, "selected_start_date": "", "selected_end_date": "", "symbols_parsed": [], "aligned_row_count": 0, "absorption_category_counts": {}, "stability_warnings": []})
    print(f"BLOCKED: {reason}")
    print("replacement_checks_all_true=false")
    return 2


def main() -> int:
    try:
        if path_is_inside(data_root(), REPO_ROOT):
            raise PreviewBlocked(f"data root resolves inside repo: {data_root()}")
        manifest_summary = load_json(MANIFEST_SUMMARY_JSON)
        download_summary = load_json(DOWNLOAD_SUMMARY_JSON)
        if manifest_summary.get("manifest_complete") is not True:
            raise PreviewBlocked("30d manifest summary is not complete")
        if download_summary.get("replacement_checks_all_true") is not True:
            raise PreviewBlocked("30d download summary did not pass replacement checks")
        manifest_rows = read_manifest()
        downloads = download_lookup(download_summary)
        aligned_rows: list[dict[str, Any]] = []
        file_summaries: list[dict[str, Any]] = []
        for manifest_row in manifest_rows:
            rows, file_summary = parse_symbol_day(manifest_row, downloads)
            aligned_rows.extend(rows)
            file_summaries.append(file_summary)
        if not aligned_rows:
            raise PreviewBlocked("no aligned rows produced")
        features = trade_feature_list(aligned_rows)
        categories = category_diagnostics(aligned_rows)
        quantiles = quantile_diagnostics(aligned_rows, features)
        daily_rows, daily_summary = daily_stability(aligned_rows)
        symbol_rows, symbol_summary = symbol_stability(aligned_rows)
        category_counts = dict(Counter(row.get("absorption_category", "INSUFFICIENT_DATA") for row in aligned_rows))
        warnings = stability_warnings(daily_summary, symbol_summary, category_counts)
        sample_rows = aligned_rows[:MAX_SAMPLE_ROWS]
        id_columns = ["timestamp", "symbol", "pilot_file_date", "absorption_category"]
        numeric_columns = sorted({key for row in sample_rows for key, value in row.items() if numeric(value) is not None})
        sample_fields = id_columns + [column for column in numeric_columns if column not in id_columns]
        write_csv_rows(SAMPLE_CSV, sample_rows, sample_fields)
        parquet_written, parquet_error = bookdepth_preview.try_write_parquet(SAMPLE_PARQUET, sample_rows, sample_fields)
        diagnostic_fields = ["absorption_category", "count", "total_rows", "missing_rate", "stability_warning"]
        for forward in FORWARD_COLUMNS:
            diagnostic_fields.extend([f"mean_{forward}", f"median_{forward}", f"positive_rate_{forward}", f"count_{forward}"])
        write_csv_rows(CATEGORY_CSV, categories, diagnostic_fields)
        quantile_fields = ["feature", "quantile", "count", "total_rows", "missing_rate", "feature_min", "feature_max", "stability_warning"]
        for forward in FORWARD_COLUMNS:
            quantile_fields.extend([f"mean_{forward}", f"median_{forward}", f"positive_rate_{forward}", f"count_{forward}"])
        write_csv_rows(QUANTILE_CSV, quantiles, quantile_fields)
        daily_fields = [
            "symbol",
            "file_date",
            "day_of_week",
            "is_weekend",
            "aligned_rows",
            "row_share",
            "volatility_score",
            "volatility_bucket",
        ] + [f"category_count_{category}" for category in CATEGORIES]
        for forward in FORWARD_COLUMNS:
            daily_fields.extend([f"mean_{forward}", f"median_{forward}", f"positive_rate_{forward}", f"count_{forward}", f"missing_rate_{forward}"])
        write_csv_rows(DAILY_STABILITY_CSV, daily_rows, daily_fields)
        symbol_fields = ["symbol", "aligned_rows", "row_share", "distinct_days"] + [f"category_count_{category}" for category in CATEGORIES] + ["largest_category_share"]
        for forward in FORWARD_COLUMNS:
            symbol_fields.extend([f"mean_{forward}", f"median_{forward}", f"positive_rate_{forward}", f"count_{forward}", f"missing_rate_{forward}"])
        write_csv_rows(SYMBOL_STABILITY_CSV, symbol_rows, symbol_fields)
        aligned_per_day = {
            f"{item['symbol']}|{item['file_date']}": item["aligned_rows"] for item in file_summaries
        }
        forward_availability = {forward: sum(1 for row in aligned_rows if numeric(row.get(forward)) is not None) for forward in FORWARD_COLUMNS}
        recommended = "D_STOP_DUE_TO_WEAK_OR_UNSTABLE_DIAGNOSTICS" if any(warning.startswith("one_symbol") for warning in warnings) else "C_BUILD_FIRST_STRICT_DISCOVERY_EVALUATOR_ON_30_DAY_DATA"
        summary = {
            "status": "PASS_ORDERBOOK_UM_30D_ABSORPTION_PREVIEW_CREATED",
            "created_at_utc": utc_now_text(),
            "task_name": "ORDERBOOK_UM_BTC_ETH_SOL_30D_ABSORPTION_PILOT_V1",
            "data_root": str(data_root()),
            "selected_start_date": manifest_summary.get("selected_start_date"),
            "selected_end_date": manifest_summary.get("selected_end_date"),
            "selected_day_count": manifest_summary.get("selected_day_count"),
            "symbols_parsed": TARGET_SYMBOLS,
            "expected_file_count": 180,
            "downloaded_file_count": download_summary.get("downloaded_or_verified_file_count"),
            "checksum_verification_summary": {
                "verified_file_count": download_summary.get("checksum_verified_file_count"),
                "bookdepth_file_count": download_summary.get("bookdepth_file_count"),
                "aggtrades_file_count": download_summary.get("aggtrades_file_count"),
            },
            "parsed_row_counts_per_symbol_day": {
                key: {
                    "bookdepth_feature_rows": item["bookdepth"]["feature_rows"],
                    "aggtrade_rows": item["aggtrades"]["parsed_trade_rows"],
                }
                for key, item in ((f"{file_item['symbol']}|{file_item['file_date']}", file_item) for file_item in file_summaries)
            },
            "aligned_rows_per_symbol_day": aligned_per_day,
            "aligned_row_count": len(aligned_rows),
            "derived_feature_list": features,
            "absorption_categories": CATEGORIES,
            "absorption_category_counts": category_counts,
            "forward_diagnostic_availability": forward_availability,
            "daily_stability_summary": daily_summary,
            "symbol_stability_summary": symbol_summary,
            "stability_warnings": warnings,
            "missing_or_malformed_row_count": sum(int(item.get("missing_or_malformed_rows") or 0) for item in file_summaries),
            "duplicate_timestamp_notes": "aggTrades can share timestamps; aggregation preserves counts rather than requiring unique timestamps.",
            "alignment_method": {
                "method": "per symbol/day trailing aggTrades windows ending at each bookDepth percentage-depth timestamp",
                "no_future_leakage": True,
                "feature_rule": "At timestamp T, trade-flow features include only aggTrades with timestamps <= T.",
                "forward_diagnostics_rule": "Forward returns are retained only as diagnostics from bookDepth mid proxy columns.",
            },
            "file_summaries": file_summaries,
            "category_diagnostic_row_count": len(categories),
            "quantile_diagnostic_row_count": len(quantiles),
            "daily_stability_row_count": len(daily_rows),
            "symbol_stability_row_count": len(symbol_rows),
            "sample_row_count": len(sample_rows),
            "parquet_written": parquet_written,
            "parquet_error": parquet_error,
            "output_files": {
                "summary_json": str(SUMMARY_JSON),
                "summary_md": str(SUMMARY_MD),
                "category_diagnostics_csv": str(CATEGORY_CSV),
                "quantile_diagnostics_csv": str(QUANTILE_CSV),
                "daily_stability_csv": str(DAILY_STABILITY_CSV),
                "symbol_stability_csv": str(SYMBOL_STABILITY_CSV),
                "quality_report_md": str(QUALITY_MD),
                "sample_csv": str(SAMPLE_CSV),
                "sample_parquet": str(SAMPLE_PARQUET) if parquet_written else "",
            },
            "suitable_for_next_step": "DIAGNOSTIC_ONLY_EXPANDED_PILOT_NOT_FOR_TRADING_USE",
            "recommended_next_step": recommended,
            "full_81_symbol_download_attempted": False,
            "replacement_checks_all_true": True,
        }
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_summary_md(summary)
        write_quality_md(summary)
        print(f"status: {summary['status']}")
        print(f"selected_window: {summary['selected_start_date']} to {summary['selected_end_date']}")
        print(f"aligned_row_count: {summary['aligned_row_count']}")
        print(f"absorption_categories: {json.dumps(summary['absorption_category_counts'], sort_keys=True)}")
        print(f"summary_json: {SUMMARY_JSON}")
        print(f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}")
        print(f"recommended_next_step: {summary['recommended_next_step']}")
        return 0
    except PreviewBlocked as exc:
        return write_blocked(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
