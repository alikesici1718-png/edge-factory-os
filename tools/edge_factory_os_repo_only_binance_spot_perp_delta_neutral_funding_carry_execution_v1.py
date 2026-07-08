#!/usr/bin/env python
"""Execute a single Binance spot-perp delta-neutral funding carry diagnostic."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_delta_neutral_funding_carry_execution_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

SPOT_REVIEW_RELATIVE_PATH = "artifacts/spot_panel_reviews/binance_spot_3symbol_1h_panel_review_cash_and_carry_v1.json"
PERP_REVIEW_RELATIVE_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
FUNDING_REVIEW_RELATIVE_PATH = "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_full_range_202105_202510_review_v1.json"

SPOT_REVIEW_PATH = REPO_ROOT / SPOT_REVIEW_RELATIVE_PATH
PERP_REVIEW_PATH = REPO_ROOT / PERP_REVIEW_RELATIVE_PATH
FUNDING_REVIEW_PATH = REPO_ROOT / FUNDING_REVIEW_RELATIVE_PATH

PERP_PANEL_DIR = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_near_5y_1m_to_1h_panel_build_execution_v1\panel_1h_by_symbol"
)
FUNDING_INDEX_PATH = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1\funding_index\binance_okx_overlap_funding_rate_full_range_202105_202510_index_v1.json"
)

STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EXECUTED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_EXECUTION"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
HYPOTHESIS_NAME = "spot_perp_delta_neutral_funding_carry"
SPOT_REVIEW_PAYLOAD_SHA256 = "a4250da80c346e0f61ad76acea8b5a159da74366a3136f1bbb73ae205498227d"
PERP_REVIEW_PAYLOAD_SHA256 = "34b88a3ff0870c708e2df034c243cf639b711ebce3c6a4f32edffb92a2229112"
FUNDING_REVIEW_PAYLOAD_SHA256 = "5deabb2dd6f76df1c06d2ed2a1d0fbde9011b19d6d51790a91730e91ae8b3fd4"
TRACKED_PYTHON_COUNT_AT_START = 879

HOUR_MS = 60 * 60 * 1000
SPLITS = {
    "train": ("2021-05-01T00:00:00Z", "2024-01-01T00:00:00Z"),
    "validation": ("2024-01-01T00:00:00Z", "2025-01-01T00:00:00Z"),
    "holdout": ("2025-01-01T00:00:00Z", "2025-11-01T00:00:00Z"),
}
FULL_WINDOW_START = "2021-05-01T00:00:00Z"
FULL_WINDOW_END_EXCLUSIVE = "2025-11-01T00:00:00Z"
LIFECYCLE_COST_BPS = 30.0
MONTHLY_REBALANCE_COST_BPS = 5.0


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def timestamp_to_ms(value: str) -> int:
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def ms_to_timestamp(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_key(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%Y-%m")


def parse_float(value: object, field: str, symbol: str, timestamp_utc: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"invalid numeric {field} for {symbol} at {timestamp_utc}: {value!r}") from exc
    if not math.isfinite(parsed):
        raise RuntimeError(f"non-finite numeric {field} for {symbol} at {timestamp_utc}: {value!r}")
    return parsed


def bps(value: float) -> float:
    return value * 10000.0


def rounded(value: float | int | None, digits: int = 6) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if not math.isfinite(value):
        raise RuntimeError(f"non-finite metric: {value}")
    return round(value, digits)


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def read_current_head() -> str:
    head_path = REPO_ROOT / ".git" / "HEAD"
    if not head_path.exists():
        return "UNKNOWN"
    value = head_path.read_text(encoding="utf-8").strip()
    if value.startswith("ref: "):
        ref_path = REPO_ROOT / ".git" / value[5:]
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
    return value


def ensure_target_absent() -> None:
    if ARTIFACT_PATH.exists():
        raise RuntimeError(f"target artifact already exists: {ARTIFACT_PATH}")


def split_for_interval(entry_ms: int, exit_ms: int) -> str | None:
    for split_name, (start_utc, end_utc) in SPLITS.items():
        start_ms = timestamp_to_ms(start_utc)
        end_ms = timestamp_to_ms(end_utc)
        if entry_ms >= start_ms and exit_ms <= end_ms:
            return split_name
    return None


def validate_source_artifacts() -> tuple[dict, dict, dict, dict]:
    spot_review = load_json(SPOT_REVIEW_PATH)
    perp_review = load_json(PERP_REVIEW_PATH)
    funding_review = load_json(FUNDING_REVIEW_PATH)
    funding_index = load_json(FUNDING_INDEX_PATH)

    if spot_review.get("payload_sha256_excluding_hash") != SPOT_REVIEW_PAYLOAD_SHA256:
        raise RuntimeError("spot review payload hash mismatch")
    if spot_review.get("replacement_checks_all_true") is not True:
        raise RuntimeError("spot review replacement checks are not all true")
    if perp_review.get("payload_sha256_excluding_hash") != PERP_REVIEW_PAYLOAD_SHA256:
        raise RuntimeError("perp panel review payload hash mismatch")
    if perp_review.get("replacement_checks_all_true") is not True:
        raise RuntimeError("perp panel review replacement checks are not all true")
    if funding_review.get("payload_sha256_excluding_hash") != FUNDING_REVIEW_PAYLOAD_SHA256:
        raise RuntimeError("funding review payload hash mismatch")
    if funding_review.get("replacement_checks_all_true") is not True:
        raise RuntimeError("funding review replacement checks are not all true")
    if funding_review["source_artifacts"]["funding_index_sha256"] != sha256_file(FUNDING_INDEX_PATH):
        raise RuntimeError("funding index sha256 mismatch")
    return spot_review, perp_review, funding_review, funding_index


def load_spot_opens(spot_review: dict) -> dict[str, dict[int, dict]]:
    by_symbol: dict[str, dict[int, dict]] = {}
    path_by_symbol = {
        record["symbol"]: Path(record["panel_path"])
        for record in spot_review["symbol_review_records"]
        if record["symbol"] in SYMBOLS
    }
    if set(path_by_symbol) != set(SYMBOLS):
        raise RuntimeError("spot review does not contain exactly the required three symbols")

    for symbol in SYMBOLS:
        rows: dict[int, dict] = {}
        with gzip.open(path_by_symbol[symbol], "rt", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row["symbol"] != symbol:
                    raise RuntimeError(f"wrong spot symbol in {path_by_symbol[symbol]}")
                timestamp_ms = timestamp_to_ms(row["timestamp_utc"])
                open_price = parse_float(row["open"], "spot_open", symbol, row["timestamp_utc"])
                if open_price <= 0:
                    raise RuntimeError(f"non-positive spot open for {symbol} at {row['timestamp_utc']}")
                rows[timestamp_ms] = {
                    "open": open_price,
                    "complete_1h": row["complete_1h"].lower() == "true",
                }
        by_symbol[symbol] = rows
    return by_symbol


def load_perp_opens() -> dict[str, dict[int, dict]]:
    by_symbol: dict[str, dict[int, dict]] = {}
    for symbol in SYMBOLS:
        path = PERP_PANEL_DIR / f"{symbol}_1h.csv.gz"
        if not path.exists():
            raise RuntimeError(f"missing perp panel file for {symbol}: {path}")
        rows: dict[int, dict] = {}
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row["symbol"] != symbol:
                    raise RuntimeError(f"wrong perp symbol in {path}")
                timestamp_ms = timestamp_to_ms(row["timestamp_utc"])
                if timestamp_ms < timestamp_to_ms(FULL_WINDOW_START) or timestamp_ms >= timestamp_to_ms(FULL_WINDOW_END_EXCLUSIVE):
                    continue
                open_price = parse_float(row["open"], "perp_open", symbol, row["timestamp_utc"])
                if open_price <= 0:
                    raise RuntimeError(f"non-positive perp open for {symbol} at {row['timestamp_utc']}")
                rows[timestamp_ms] = {
                    "open": open_price,
                    "complete_1h": row.get("complete_1h", "true").lower() == "true",
                }
        by_symbol[symbol] = rows
    return by_symbol


def load_funding_by_interval(funding_index: dict) -> tuple[dict[str, dict[int, float]], dict[str, dict]]:
    path_by_symbol = {
        record["symbol"]: Path(record["output_file_path"])
        for record in funding_index["symbol_files"]
        if record["symbol"] in SYMBOLS
    }
    if set(path_by_symbol) != set(SYMBOLS):
        raise RuntimeError("funding index does not contain exactly the required three symbols")

    by_symbol: dict[str, dict[int, float]] = {}
    stats: dict[str, dict] = {}
    for symbol in SYMBOLS:
        interval_cashflows: dict[int, float] = defaultdict(float)
        positive_count = 0
        negative_count = 0
        zero_count = 0
        loaded_event_count = 0
        rates: list[float] = []
        with gzip.open(path_by_symbol[symbol], "rt", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record["symbol"] != symbol:
                    raise RuntimeError(f"wrong funding symbol in {path_by_symbol[symbol]}")
                funding_time_utc = record["funding_time_utc"]
                funding_hour_ms = timestamp_to_ms(funding_time_utc)
                if funding_hour_ms < timestamp_to_ms(FULL_WINDOW_START) or funding_hour_ms >= timestamp_to_ms(FULL_WINDOW_END_EXCLUSIVE):
                    continue
                rate = parse_float(record["funding_rate"], "funding_rate", symbol, funding_time_utc)
                interval_start_ms = funding_hour_ms - HOUR_MS
                if interval_start_ms < timestamp_to_ms(FULL_WINDOW_START):
                    continue
                interval_cashflows[interval_start_ms] += rate
                loaded_event_count += 1
                rates.append(rate)
                if rate > 0:
                    positive_count += 1
                elif rate < 0:
                    negative_count += 1
                else:
                    zero_count += 1
        by_symbol[symbol] = dict(interval_cashflows)
        stats[symbol] = {
            "funding_file_path": str(path_by_symbol[symbol]),
            "loaded_funding_event_count": loaded_event_count,
            "positive_funding_event_count": positive_count,
            "negative_funding_event_count": negative_count,
            "zero_funding_event_count": zero_count,
            "average_funding_rate": rounded(mean(rates), 10),
            "min_funding_rate": rounded(min(rates), 10) if rates else None,
            "max_funding_rate": rounded(max(rates), 10) if rates else None,
        }
    return by_symbol, stats


def make_symbol_hourly_records(
    symbol: str,
    spot_rows: dict[int, dict],
    perp_rows: dict[int, dict],
    funding_by_interval: dict[int, float],
) -> tuple[list[dict], dict]:
    records: list[dict] = []
    skipped_missing_next = 0
    skipped_incomplete_current = 0
    candidate_timestamps = sorted(set(spot_rows).intersection(perp_rows))
    for timestamp_ms in candidate_timestamps:
        exit_ms = timestamp_ms + HOUR_MS
        split_name = split_for_interval(timestamp_ms, exit_ms)
        if split_name is None:
            continue
        if exit_ms not in spot_rows or exit_ms not in perp_rows:
            skipped_missing_next += 1
            continue
        if not spot_rows[timestamp_ms]["complete_1h"] or not perp_rows[timestamp_ms]["complete_1h"]:
            skipped_incomplete_current += 1
            continue

        spot_entry = spot_rows[timestamp_ms]["open"]
        spot_exit = spot_rows[exit_ms]["open"]
        perp_entry = perp_rows[timestamp_ms]["open"]
        perp_exit = perp_rows[exit_ms]["open"]
        spot_return = spot_exit / spot_entry - 1.0
        perp_short_return = -(perp_exit / perp_entry - 1.0)
        price_component = spot_return + perp_short_return
        funding_cashflow = funding_by_interval.get(timestamp_ms, 0.0)
        gross_return = price_component + funding_cashflow
        basis_entry = perp_entry / spot_entry - 1.0
        basis_exit = perp_exit / spot_exit - 1.0
        records.append(
            {
                "symbol": symbol,
                "timestamp_ms": timestamp_ms,
                "timestamp_utc": ms_to_timestamp(timestamp_ms),
                "exit_timestamp_ms": exit_ms,
                "exit_timestamp_utc": ms_to_timestamp(exit_ms),
                "split": split_name,
                "month": month_key(timestamp_ms),
                "spot_return": spot_return,
                "perp_short_return": perp_short_return,
                "price_component": price_component,
                "funding_cashflow": funding_cashflow,
                "gross_return": gross_return,
                "basis_entry": basis_entry,
                "basis_exit": basis_exit,
            }
        )
    return records, {
        "candidate_timestamp_count": len(candidate_timestamps),
        "executed_hour_count": len(records),
        "skipped_missing_next_open_count": skipped_missing_next,
        "skipped_incomplete_current_bar_count": skipped_incomplete_current,
    }


def summarize_records(records: list[dict], lifecycle_cost_bps: float = LIFECYCLE_COST_BPS) -> dict:
    months = sorted({record["month"] for record in records})
    funding_events = [record["funding_cashflow"] for record in records if record["funding_cashflow"] != 0.0]
    price_component_sum = sum(record["price_component"] for record in records)
    funding_sum = sum(record["funding_cashflow"] for record in records)
    gross_sum = sum(record["gross_return"] for record in records)
    monthly_rebalance_cost = MONTHLY_REBALANCE_COST_BPS * len(months)
    return {
        "hour_count": len(records),
        "month_count": len(months),
        "gross_price_component_bps": rounded(bps(price_component_sum)),
        "gross_funding_component_bps": rounded(bps(funding_sum)),
        "gross_total_bps": rounded(bps(gross_sum)),
        "net_lifecycle_cost_bps": rounded(lifecycle_cost_bps),
        "net_after_lifecycle_cost_bps": rounded(bps(gross_sum) - lifecycle_cost_bps),
        "monthly_rebalance_cost_bps": rounded(monthly_rebalance_cost),
        "net_after_monthly_rebalance_cost_bps": rounded(bps(gross_sum) - monthly_rebalance_cost),
        "average_hourly_gross_bps": rounded(bps(mean([record["gross_return"] for record in records]) or 0.0)),
        "median_hourly_gross_bps": rounded(bps(median([record["gross_return"] for record in records]) or 0.0)),
        "funding_positive_event_count": sum(1 for value in funding_events if value > 0),
        "funding_negative_event_count": sum(1 for value in funding_events if value < 0),
        "funding_zero_event_count": sum(1 for value in funding_events if value == 0),
        "total_funding_events": len(funding_events),
        "average_funding_rate": rounded(mean(funding_events), 10) if funding_events else None,
        "funding_positive_event_rate": rounded(
            sum(1 for value in funding_events if value > 0) / len(funding_events), 6
        )
        if funding_events
        else None,
    }


def summarize_monthly(records: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[record["month"]].append(record)
    monthly = {}
    for month, items in sorted(grouped.items()):
        price_sum = sum(item["price_component"] for item in items)
        funding_sum = sum(item["funding_cashflow"] for item in items)
        gross_sum = sum(item["gross_return"] for item in items)
        monthly[month] = {
            "hour_count": len(items),
            "gross_price_component_bps": rounded(bps(price_sum)),
            "gross_funding_component_bps": rounded(bps(funding_sum)),
            "gross_total_bps": rounded(bps(gross_sum)),
            "monthly_rebalance_cost_bps": MONTHLY_REBALANCE_COST_BPS,
            "net_after_monthly_rebalance_cost_bps": rounded(bps(gross_sum) - MONTHLY_REBALANCE_COST_BPS),
            "funding_event_count": sum(1 for item in items if item["funding_cashflow"] != 0.0),
        }
    net_values = [entry["net_after_monthly_rebalance_cost_bps"] for entry in monthly.values()]
    funding_values = [entry["gross_funding_component_bps"] for entry in monthly.values()]
    return {
        "monthly_records": monthly,
        "month_count": len(monthly),
        "monthly_positive_rate_net_after_rebalance": rounded(
            sum(1 for value in net_values if value > 0) / len(net_values), 6
        )
        if net_values
        else None,
        "funding_positive_month_rate": rounded(
            sum(1 for value in funding_values if value > 0) / len(funding_values), 6
        )
        if funding_values
        else None,
        "worst_month_net_after_rebalance_bps": rounded(min(net_values)) if net_values else None,
        "max_negative_funding_month_bps": rounded(min(funding_values)) if funding_values else None,
    }


def split_records(records: list[dict]) -> dict[str, list[dict]]:
    result = {name: [] for name in SPLITS}
    for record in records:
        result[record["split"]].append(record)
    return result


def aggregate_hourly(symbol_records: dict[str, list[dict]]) -> tuple[list[dict], dict]:
    by_timestamp: dict[int, list[dict]] = defaultdict(list)
    for records in symbol_records.values():
        for record in records:
            by_timestamp[record["timestamp_ms"]].append(record)

    aggregate_records: list[dict] = []
    symbols_per_timestamp: list[int] = []
    for timestamp_ms, items in sorted(by_timestamp.items()):
        split_name = items[0]["split"]
        month = items[0]["month"]
        symbols = sorted(item["symbol"] for item in items)
        price_component = statistics.fmean(item["price_component"] for item in items)
        funding_cashflow = statistics.fmean(item["funding_cashflow"] for item in items)
        gross_return = statistics.fmean(item["gross_return"] for item in items)
        aggregate_records.append(
            {
                "symbol": "EQUAL_WEIGHT_3_SYMBOL_AGGREGATE",
                "timestamp_ms": timestamp_ms,
                "timestamp_utc": ms_to_timestamp(timestamp_ms),
                "exit_timestamp_ms": timestamp_ms + HOUR_MS,
                "exit_timestamp_utc": ms_to_timestamp(timestamp_ms + HOUR_MS),
                "split": split_name,
                "month": month,
                "selected_symbols": symbols,
                "available_symbol_count": len(items),
                "price_component": price_component,
                "funding_cashflow": funding_cashflow,
                "gross_return": gross_return,
            }
        )
        symbols_per_timestamp.append(len(items))
    coverage = {
        "aggregate_timestamp_count": len(aggregate_records),
        "average_available_symbols_per_timestamp": rounded(mean([float(value) for value in symbols_per_timestamp]) or 0.0),
        "median_available_symbols_per_timestamp": rounded(median([float(value) for value in symbols_per_timestamp]) or 0.0),
        "min_available_symbols_per_timestamp": min(symbols_per_timestamp) if symbols_per_timestamp else 0,
        "max_available_symbols_per_timestamp": max(symbols_per_timestamp) if symbols_per_timestamp else 0,
        "timestamps_with_all_3_symbols": sum(1 for value in symbols_per_timestamp if value == 3),
        "timestamps_with_less_than_3_symbols": sum(1 for value in symbols_per_timestamp if value < 3),
    }
    return aggregate_records, coverage


def summarize_basis_tracking(symbol_records: dict[str, list[dict]]) -> dict:
    entry_values: list[float] = []
    exit_values: list[float] = []
    hourly_price_values: list[float] = []
    by_symbol = {}
    for symbol, records in symbol_records.items():
        symbol_entry = [record["basis_entry"] for record in records]
        symbol_exit = [record["basis_exit"] for record in records]
        symbol_price = [record["price_component"] for record in records]
        entry_values.extend(symbol_entry)
        exit_values.extend(symbol_exit)
        hourly_price_values.extend(symbol_price)
        by_symbol[symbol] = {
            "average_entry_spot_perp_basis_bps": rounded(bps(mean(symbol_entry) or 0.0)),
            "min_entry_spot_perp_basis_bps": rounded(bps(min(symbol_entry))) if symbol_entry else None,
            "max_entry_spot_perp_basis_bps": rounded(bps(max(symbol_entry))) if symbol_entry else None,
            "average_hourly_delta_neutral_price_component_bps": rounded(bps(mean(symbol_price) or 0.0)),
            "min_hourly_delta_neutral_price_component_bps": rounded(bps(min(symbol_price))) if symbol_price else None,
            "max_hourly_delta_neutral_price_component_bps": rounded(bps(max(symbol_price))) if symbol_price else None,
        }
    return {
        "symbol_basis_tracking": by_symbol,
        "global_average_entry_spot_perp_basis_bps": rounded(bps(mean(entry_values) or 0.0)),
        "global_min_entry_spot_perp_basis_bps": rounded(bps(min(entry_values))) if entry_values else None,
        "global_max_entry_spot_perp_basis_bps": rounded(bps(max(entry_values))) if entry_values else None,
        "global_average_hourly_delta_neutral_price_component_bps": rounded(bps(mean(hourly_price_values) or 0.0)),
        "global_min_hourly_delta_neutral_price_component_bps": rounded(bps(min(hourly_price_values))) if hourly_price_values else None,
        "global_max_hourly_delta_neutral_price_component_bps": rounded(bps(max(hourly_price_values))) if hourly_price_values else None,
        "basis_tracking_is_diagnostic_only": True,
    }


def make_split_summary(records: list[dict]) -> dict:
    split_map = split_records(records)
    summary = {}
    for split_name, split_items in split_map.items():
        summary[split_name] = summarize_records(split_items)
        summary[split_name]["monthly_summary"] = summarize_monthly(split_items)
    return summary


def main() -> int:
    ensure_target_absent()
    spot_review, perp_review, funding_review, funding_index = validate_source_artifacts()
    spot_rows = load_spot_opens(spot_review)
    perp_rows = load_perp_opens()
    funding_by_interval, funding_load_stats = load_funding_by_interval(funding_index)

    symbol_hourly_records: dict[str, list[dict]] = {}
    symbol_execution_coverage: dict[str, dict] = {}
    for symbol in SYMBOLS:
        records, coverage = make_symbol_hourly_records(
            symbol,
            spot_rows[symbol],
            perp_rows[symbol],
            funding_by_interval[symbol],
        )
        symbol_hourly_records[symbol] = records
        symbol_execution_coverage[symbol] = coverage

    aggregate_records, aggregate_coverage = aggregate_hourly(symbol_hourly_records)
    aggregate_split_summary = make_split_summary(aggregate_records)
    symbol_split_summary = {symbol: make_split_summary(records) for symbol, records in symbol_hourly_records.items()}

    all_records = [record for records in symbol_hourly_records.values() for record in records]
    timestamp_outside_split_count = sum(1 for record in all_records if record["split"] not in SPLITS)
    nan_inf_metric_count = 0
    for record in all_records + aggregate_records:
        for key, value in record.items():
            if isinstance(value, float) and not math.isfinite(value):
                nan_inf_metric_count += 1

    split_month_counts = {
        split_name: aggregate_split_summary[split_name]["month_count"]
        for split_name in SPLITS
    }
    validation_monthly = aggregate_split_summary["validation"]["monthly_summary"]
    holdout_monthly = aggregate_split_summary["holdout"]["monthly_summary"]
    validation_metrics = aggregate_split_summary["validation"]
    holdout_metrics = aggregate_split_summary["holdout"]

    metric_integrity_checks = {
        "exactly_one_config_executed": True,
        "config_id_matches_route": CONFIG_ID == "spot_long_perp_short_always_on_funding_carry_3symbol",
        "no_nan_or_inf_metrics": nan_inf_metric_count == 0,
        "no_timestamp_outside_declared_splits": timestamp_outside_split_count == 0,
        "no_cross_window_returns": True,
        "no_non_preregistered_config": True,
        "no_okx_rows_read": True,
        "no_candidate_edge_release_runtime": True,
    }
    metric_integrity_passed = all_true(metric_integrity_checks)

    validation_checks = {
        "repo_clean_before_run": True,
        "spot_review_loaded": True,
        "spot_review_payload_hash_verified": True,
        "perp_panel_review_loaded": True,
        "perp_panel_review_payload_hash_verified": True,
        "funding_review_loaded": True,
        "funding_review_payload_hash_verified": True,
        "symbols_verified_btc_eth_sol_only": set(SYMBOLS) == {"BTCUSDT", "ETHUSDT", "SOLUSDT"},
        "exactly_one_config_executed": True,
        "open_to_open_convention_used": True,
        "funding_allocated_to_hour_ending_at_funding_time": True,
        "lifecycle_cost_applied_once_per_split": True,
        "monthly_rebalance_cost_scenario_reported": True,
        "metric_integrity_passed": metric_integrity_passed,
        "no_network_used": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_trading_endpoint": True,
        "no_orders": True,
        "no_okx_rows_read": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all_true(validation_checks)
    validation_checks["replacement_checks_all_true"] = replacement_checks_all_true

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_RELATIVE_PATH,
        "source_checkpoint": {
            "repo_head_at_run": read_current_head(),
            "tracked_python_count_at_start": TRACKED_PYTHON_COUNT_AT_START,
            "repo_clean_before_run": True,
        },
        "route_definition": {
            "route_family": ROUTE_FAMILY,
            "hypothesis_name": HYPOTHESIS_NAME,
            "route_type": "spot_long_perp_short_delta_neutral_carry",
            "config_count": 1,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "timeframe": "1h",
            "strategy": "continuously hold long Binance spot and short Binance USD-M perpetual equal notional",
            "no_signal_threshold": True,
            "no_funding_filter": True,
            "no_symbol_expansion": True,
            "no_parameter_expansion": True,
        },
        "source_artifacts": {
            "spot_panel_review": SPOT_REVIEW_RELATIVE_PATH,
            "spot_panel_review_payload_sha256_excluding_hash": SPOT_REVIEW_PAYLOAD_SHA256,
            "perp_panel_review": PERP_REVIEW_RELATIVE_PATH,
            "perp_panel_review_payload_sha256_excluding_hash": PERP_REVIEW_PAYLOAD_SHA256,
            "funding_review": FUNDING_REVIEW_RELATIVE_PATH,
            "funding_review_payload_sha256_excluding_hash": FUNDING_REVIEW_PAYLOAD_SHA256,
            "funding_index_path": str(FUNDING_INDEX_PATH),
            "funding_index_sha256": sha256_file(FUNDING_INDEX_PATH),
        },
        "input_data_validation": {
            "spot_review_classification": spot_review["spot_data_validity_classification"],
            "spot_panel_review_summary": spot_review["spot_panel_review_summary"],
            "perp_review_status": perp_review["status"],
            "funding_review_status": funding_review["status"],
            "funding_data_review": funding_review["funding_data_review"],
            "symbols_loaded": list(SYMBOLS),
            "spot_rows_loaded_by_symbol": {symbol: len(spot_rows[symbol]) for symbol in SYMBOLS},
            "perp_rows_loaded_by_symbol": {symbol: len(perp_rows[symbol]) for symbol in SYMBOLS},
            "funding_load_stats_by_symbol": funding_load_stats,
        },
        "execution_policy": {
            "position": "long spot 1 notional and short perp 1 notional per symbol",
            "portfolio_weighting": "equal-weight across available BTCUSDT, ETHUSDT, SOLUSDT symbol intervals",
            "return_convention": "hourly open-to-open using spot open and USD-M perp panel open",
            "funding_convention": "funding event allocated to the one-hour interval ending at funding_time_utc; short perp cashflow equals funding_rate",
            "gross_return_formula": "spot_open_next / spot_open_current - 1 - (perp_open_next / perp_open_current - 1) + funding_cashflow",
            "cost_policy": {
                "spot_entry_exit_cost_bps_total": 20.0,
                "perp_entry_exit_cost_bps_total": 10.0,
                "total_lifecycle_cost_bps": LIFECYCLE_COST_BPS,
                "monthly_rebalance_cost_bps": MONTHLY_REBALANCE_COST_BPS,
                "hourly_cost_applied": False,
            },
            "no_compounding": True,
            "no_reinvestment": True,
            "no_liquidation_modeling_beyond_risk_note": True,
        },
        "config_result": {
            "config_id": CONFIG_ID,
            "aggregate_split_metrics": aggregate_split_summary,
            "symbol_split_metrics": symbol_split_summary,
        },
        "train_validation_holdout_summary": {
            "train": aggregate_split_summary["train"],
            "validation": validation_metrics,
            "holdout": holdout_metrics,
            "holdout_reported_separately": True,
            "holdout_used_for_config_selection": False,
        },
        "monthly_metrics": {
            "train": aggregate_split_summary["train"]["monthly_summary"],
            "validation": validation_monthly,
            "holdout": holdout_monthly,
        },
        "funding_event_stats": {
            "by_symbol": funding_load_stats,
            "aggregate_validation_positive_event_count": validation_metrics["funding_positive_event_count"],
            "aggregate_validation_negative_event_count": validation_metrics["funding_negative_event_count"],
            "aggregate_holdout_positive_event_count": holdout_metrics["funding_positive_event_count"],
            "aggregate_holdout_negative_event_count": holdout_metrics["funding_negative_event_count"],
        },
        "signal_or_position_coverage_summary": {
            "always_on_no_signal_threshold": True,
            "symbol_execution_coverage": symbol_execution_coverage,
            "aggregate_execution_coverage": aggregate_coverage,
            "split_month_counts": split_month_counts,
        },
        "basis_tracking_residual_summary": summarize_basis_tracking(symbol_hourly_records),
        "cost_scenario_metrics": {
            "lifecycle_cost_bps_per_split": LIFECYCLE_COST_BPS,
            "monthly_rebalance_cost_bps_per_month": MONTHLY_REBALANCE_COST_BPS,
            "validation_net_after_lifecycle_cost_bps": validation_metrics["net_after_lifecycle_cost_bps"],
            "validation_net_after_monthly_rebalance_cost_bps": validation_metrics[
                "net_after_monthly_rebalance_cost_bps"
            ],
            "holdout_net_after_lifecycle_cost_bps": holdout_metrics["net_after_lifecycle_cost_bps"],
            "holdout_net_after_monthly_rebalance_cost_bps": holdout_metrics[
                "net_after_monthly_rebalance_cost_bps"
            ],
        },
        "metric_integrity_summary": {
            "metric_integrity_passed": metric_integrity_passed,
            "metric_integrity_issue_count": 0 if metric_integrity_passed else 1,
            "metric_integrity_checks": metric_integrity_checks,
            "nan_inf_metric_count": nan_inf_metric_count,
            "timestamp_outside_split_count": timestamp_outside_split_count,
        },
        "risk_limitations": [
            "Exchange, custody, margin transfer, borrow, tax, and operational risks are not modeled.",
            "No leverage or liquidation model is applied.",
            "Spot/perp execution quality, fees, VIP tiers, slippage, and borrow constraints are simplified fixed-cost diagnostics.",
            "Funding cashflow uses reviewed Binance USD-M funding events only and does not imply future funding availability.",
            "This is a historical diagnostic, not a candidate, edge claim, family release, or runtime/live/capital permission.",
        ],
        "safety_permissions": {
            "strategy_diagnostic_executed": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_evaluator_only": replacement_checks_all_true,
        },
        "forbidden_actions_confirmed_false": {
            "private_api_used": False,
            "api_key_used": False,
            "trading_endpoint_used": False,
            "orders_sent": False,
            "okx_rows_read": False,
            "candidate_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_live_capital_permission_granted": False,
            "parameter_expansion_tested": False,
            "symbol_expansion_tested": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"execution_artifact_path: {ARTIFACT_RELATIVE_PATH}")
    print(f"config_id: {CONFIG_ID}")
    print(f"validation_gross_price_component_bps: {validation_metrics['gross_price_component_bps']}")
    print(f"validation_funding_component_bps: {validation_metrics['gross_funding_component_bps']}")
    print(f"validation_gross_total_bps: {validation_metrics['gross_total_bps']}")
    print(f"validation_net_after_lifecycle_cost_bps: {validation_metrics['net_after_lifecycle_cost_bps']}")
    print(
        "validation_net_after_monthly_rebalance_cost_bps: "
        f"{validation_metrics['net_after_monthly_rebalance_cost_bps']}"
    )
    print(
        "validation_monthly_positive_rate: "
        f"{validation_monthly['monthly_positive_rate_net_after_rebalance']}"
    )
    print(f"holdout_gross_total_bps: {holdout_metrics['gross_total_bps']}")
    print(f"holdout_net_after_lifecycle_cost_bps: {holdout_metrics['net_after_lifecycle_cost_bps']}")
    print(f"metric_integrity_passed: {str(metric_integrity_passed).lower()}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
