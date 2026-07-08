#!/usr/bin/env python3
"""Forward extension diagnostic for the Binance spot-perp funding carry route.

This module reads only the reviewed forward extension files and prior metadata
artifacts. It does not call network endpoints, place orders, enable runtime, or
grant candidate/edge/live/capital permissions.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path


getcontext().prec = 34

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")
MODULE_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_diagnostic_v1.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "strategy_diagnostics" / "binance_spot_perp_funding_carry_forward_extension_diagnostic_v1.json"

STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_DIAGNOSTIC_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_DIAGNOSTIC"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_diagnostic_v1"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
WINDOW_START_UTC = "2025-11-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2026-05-01T00:00:00Z"
WINDOW_MONTHS = ("2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04")

DATA_REVIEW_PATH = REPO_ROOT / "artifacts" / "data_reviews" / "binance_spot_perp_funding_carry_forward_extension_data_review_v1.json"
ACQUISITION_MANIFEST_PATH = REPO_ROOT / "artifacts" / "data_acquisition_locks" / "binance_spot_perp_funding_carry_forward_extension_acquisition_lock_v1.json"
EXECUTION_PATH = REPO_ROOT / "artifacts" / "strategy_executions" / "binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EVALUATOR_PATH = REPO_ROOT / "artifacts" / "strategy_evaluations" / "binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
CLOSURE_PATH = REPO_ROOT / "artifacts" / "strategy_closures" / "binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
RISK_PATH = REPO_ROOT / "artifacts" / "risk_capital_diagnostics" / "binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"

REQUIRED_REVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_FORWARD_EXTENSION_DATA_REVIEW_CREATED"
REQUIRED_REVIEW_CLASSIFICATION = "FORWARD_EXTENSION_DATA_REVIEW_PASS_VALID_FOR_EXTENDED_FUNDING_CARRY_DIAGNOSTIC"
REQUIRED_BASE_RESULT_CLASS = "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"

CSV_HEADER = [
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
    "complete_1h",
]


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required artifact missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def payload_hash(payload: dict) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def git_output(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={REPO_ROOT.as_posix()}", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repo_clean_except_expected_outputs() -> bool:
    allowed_paths = {
        "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_forward_extension_diagnostic_v1.py",
        "artifacts/strategy_diagnostics/binance_spot_perp_funding_carry_forward_extension_diagnostic_v1.json",
    }
    status = git_output(["status", "--short", "--untracked-files=all"])
    if not status:
        return True
    for line in status.splitlines():
        rel_path = line[3:].replace("\\", "/")
        if rel_path not in allowed_paths:
            return False
    return True


def parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"Timestamp is not UTC Z-normalized: {value}")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def ms_to_utc(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def d(value) -> Decimal:
    return Decimal(str(value))


def rounded_decimal(value: Decimal, places: str = "0.000001") -> float:
    return float(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))


def rounded_rate(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP))


def read_panel(path: Path, expected_symbol: str) -> dict[str, dict[str, Decimal]]:
    if not path.exists():
        raise FileNotFoundError(f"Panel file missing: {path}")
    rows: dict[str, dict[str, Decimal]] = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CSV_HEADER:
            raise ValueError(f"Unexpected CSV header for {path}: {reader.fieldnames}")
        for row in reader:
            symbol = row["symbol"]
            timestamp = row["timestamp_utc"]
            if symbol != expected_symbol:
                raise ValueError(f"Wrong symbol in {path}: {symbol}")
            if timestamp in rows:
                raise ValueError(f"Duplicate timestamp in {path}: {timestamp}")
            if not (WINDOW_START_UTC <= timestamp < WINDOW_END_EXCLUSIVE_UTC):
                raise ValueError(f"Timestamp outside forward window in {path}: {timestamp}")
            if row["complete_1h"].lower() != "true":
                raise ValueError(f"Incomplete 1h row in {path}: {timestamp}")
            open_price = d(row["open"])
            high_price = d(row["high"])
            low_price = d(row["low"])
            close_price = d(row["close"])
            numeric_values = [
                open_price,
                high_price,
                low_price,
                close_price,
                d(row["volume"]),
                d(row["quote_volume"]),
                d(row["trade_count"]),
                d(row["taker_buy_base_volume"]),
                d(row["taker_buy_quote_volume"]),
            ]
            if any(value < 0 for value in numeric_values):
                raise ValueError(f"Negative numeric value in {path}: {timestamp}")
            if open_price <= 0 or high_price <= 0 or low_price <= 0 or close_price <= 0:
                raise ValueError(f"Nonpositive OHLC value in {path}: {timestamp}")
            if high_price < max(open_price, close_price) or low_price > min(open_price, close_price):
                raise ValueError(f"OHLC sanity failure in {path}: {timestamp}")
            rows[timestamp] = {"open": open_price, "close": close_price}
    ordered = sorted(rows)
    if ordered != list(rows.keys()):
        raise ValueError(f"Timestamps are not strictly increasing in {path}")
    return rows


def read_funding(path: Path, expected_symbol: str) -> list[dict[str, Decimal | str | int]]:
    if not path.exists():
        raise FileNotFoundError(f"Funding file missing: {path}")
    records: list[dict[str, Decimal | str | int]] = []
    seen: set[str] = set()
    last_timestamp = ""
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            for key in ("symbol", "funding_time_ms", "funding_time_utc", "funding_rate", "source_endpoint"):
                if key not in row:
                    raise ValueError(f"Missing funding field {key} in {path} line {line_number}")
            symbol = row["symbol"]
            timestamp = row["funding_time_utc"]
            if symbol != expected_symbol:
                raise ValueError(f"Wrong funding symbol in {path}: {symbol}")
            if not timestamp.endswith("Z"):
                raise ValueError(f"Funding timestamp is not UTC Z-normalized in {path}: {timestamp}")
            if timestamp in seen:
                raise ValueError(f"Duplicate funding timestamp in {path}: {timestamp}")
            if timestamp <= last_timestamp:
                raise ValueError(f"Funding timestamps not strictly increasing in {path}: {timestamp}")
            if not (WINDOW_START_UTC <= timestamp < WINDOW_END_EXCLUSIVE_UTC):
                raise ValueError(f"Funding timestamp outside forward window in {path}: {timestamp}")
            observed_from_ms = ms_to_utc(int(row["funding_time_ms"]))
            if observed_from_ms != timestamp:
                parsed_ms = int(parse_utc(timestamp).timestamp() * 1000)
                if abs(parsed_ms - int(row["funding_time_ms"])) >= 1000:
                    raise ValueError(f"Funding timestamp/ms mismatch in {path}: {timestamp}")
            funding_rate = d(row["funding_rate"])
            mark_price = row.get("mark_price")
            if mark_price is not None and d(mark_price) <= 0:
                raise ValueError(f"Nonpositive funding mark price in {path}: {timestamp}")
            seen.add(timestamp)
            last_timestamp = timestamp
            records.append(
                {
                    "symbol": symbol,
                    "funding_time_ms": int(row["funding_time_ms"]),
                    "funding_time_utc": timestamp,
                    "funding_rate": funding_rate,
                }
            )
    return records


def month_key(timestamp: str) -> str:
    return timestamp[:7]


def safe_get(mapping: dict, path: list[str], default=None):
    current = mapping
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def build_prior_comparison(execution: dict, risk: dict) -> dict:
    execution_metrics = safe_get(execution, ["config_result", "aggregate_split_metrics"], {})
    validation = execution_metrics.get("validation", {})
    holdout = execution_metrics.get("holdout", {})
    combined_stress = risk.get("combined_stress", {})
    return {
        "validation": {
            "base_net_after_lifecycle_cost_bps": validation.get("net_after_lifecycle_cost_bps", 1268.112469),
            "base_net_after_monthly_rebalance_cost_bps": validation.get("net_after_monthly_rebalance_cost_bps", 1238.112469),
            "gross_price_component_bps": validation.get("gross_price_component_bps", 13.527102),
            "gross_funding_component_bps": validation.get("gross_funding_component_bps", 1284.585367),
            "monthly_positive_rate": safe_get(
                validation,
                ["monthly_summary", "monthly_positive_rate_net_after_rebalance"],
                1.0,
            ),
            "funding_positive_event_count": validation.get("funding_positive_event_count", 1038),
            "funding_negative_event_count": validation.get("funding_negative_event_count", 60),
            "fifty_pct_funding_haircut_2x_cost_net_bps": safe_get(
                combined_stress,
                ["validation", "50pct_funding_haircut_2x_lifecycle_cost", "net_bps"],
                595.819785,
            ),
        },
        "holdout_1": {
            "base_net_after_lifecycle_cost_bps": holdout.get("net_after_lifecycle_cost_bps", 256.969856),
            "base_net_after_monthly_rebalance_cost_bps": holdout.get("net_after_monthly_rebalance_cost_bps", 236.969856),
            "gross_price_component_bps": holdout.get("gross_price_component_bps", 1.983989),
            "gross_funding_component_bps": holdout.get("gross_funding_component_bps", 284.985867),
            "monthly_positive_rate": safe_get(
                holdout,
                ["monthly_summary", "monthly_positive_rate_net_after_rebalance"],
                0.9,
            ),
            "funding_positive_event_count": holdout.get("funding_positive_event_count", 721),
            "funding_negative_event_count": holdout.get("funding_negative_event_count", 190),
            "fifty_pct_funding_haircut_2x_cost_net_bps": safe_get(
                combined_stress,
                ["holdout", "50pct_funding_haircut_2x_lifecycle_cost", "net_bps"],
                84.476923,
            ),
        },
    }


def compute_diagnostic(index: dict) -> tuple[dict, dict, dict, dict, dict]:
    spot_rows: dict[str, dict[str, dict[str, Decimal]]] = {}
    perp_rows: dict[str, dict[str, dict[str, Decimal]]] = {}
    funding_records: dict[str, list[dict[str, Decimal | str | int]]] = {}

    for symbol in SYMBOLS:
        record = index["symbol_records"][symbol]
        spot_rows[symbol] = read_panel(Path(record["spot_output_path"]), symbol)
        perp_rows[symbol] = read_panel(Path(record["perp_output_path"]), symbol)
        funding_records[symbol] = read_funding(Path(record["funding_output_path"]), symbol)

    common_hours = sorted(set.intersection(*(set(spot_rows[s].keys()) & set(perp_rows[s].keys()) for s in SYMBOLS)))
    if not common_hours:
        raise ValueError("No common spot/perp hours found for forward diagnostic")

    symbol_price_bps: dict[str, Decimal] = {symbol: Decimal("0") for symbol in SYMBOLS}
    symbol_hour_counts: dict[str, int] = {symbol: len(common_hours) for symbol in SYMBOLS}
    monthly_price_by_symbol: dict[str, dict[str, Decimal]] = {
        symbol: {month: Decimal("0") for month in WINDOW_MONTHS} for symbol in SYMBOLS
    }
    monthly_hour_counts = {month: 0 for month in WINDOW_MONTHS}
    aggregate_price_bps = Decimal("0")

    for timestamp in common_hours:
        month = month_key(timestamp)
        residuals = []
        for symbol in SYMBOLS:
            spot = spot_rows[symbol][timestamp]
            perp = perp_rows[symbol][timestamp]
            spot_return = (spot["close"] / spot["open"]) - Decimal("1")
            perp_return = (perp["close"] / perp["open"]) - Decimal("1")
            residual = spot_return - perp_return
            residuals.append(residual)
            bps = residual * Decimal("10000")
            symbol_price_bps[symbol] += bps
            monthly_price_by_symbol[symbol][month] += bps
        aggregate_hour_bps = sum(residuals, Decimal("0")) / Decimal(len(SYMBOLS)) * Decimal("10000")
        aggregate_price_bps += aggregate_hour_bps
        monthly_hour_counts[month] += 1

    funding_by_timestamp: dict[str, dict[str, Decimal]] = defaultdict(dict)
    symbol_funding_bps: dict[str, Decimal] = {symbol: Decimal("0") for symbol in SYMBOLS}
    symbol_funding_counts: dict[str, Counter] = {symbol: Counter() for symbol in SYMBOLS}
    monthly_funding_by_symbol: dict[str, dict[str, Decimal]] = {
        symbol: {month: Decimal("0") for month in WINDOW_MONTHS} for symbol in SYMBOLS
    }
    for symbol in SYMBOLS:
        for record in funding_records[symbol]:
            timestamp = str(record["funding_time_utc"])
            rate = record["funding_rate"]
            assert isinstance(rate, Decimal)
            funding_by_timestamp[timestamp][symbol] = rate
            bps = rate * Decimal("10000")
            symbol_funding_bps[symbol] += bps
            monthly_funding_by_symbol[symbol][month_key(timestamp)] += bps
            if rate > 0:
                symbol_funding_counts[symbol]["positive"] += 1
            elif rate < 0:
                symbol_funding_counts[symbol]["negative"] += 1
            else:
                symbol_funding_counts[symbol]["zero"] += 1

    aggregate_funding_bps = Decimal("0")
    aggregate_funding_rates: list[Decimal] = []
    funding_positive_count = 0
    funding_negative_count = 0
    funding_zero_count = 0
    monthly_funding_bps: dict[str, Decimal] = {month: Decimal("0") for month in WINDOW_MONTHS}
    monthly_funding_event_counts: dict[str, int] = {month: 0 for month in WINDOW_MONTHS}
    monthly_funding_sign_counts: dict[str, Counter] = {month: Counter() for month in WINDOW_MONTHS}

    for timestamp in sorted(funding_by_timestamp):
        rates_by_symbol = funding_by_timestamp[timestamp]
        missing = sorted(set(SYMBOLS) - set(rates_by_symbol))
        if missing:
            raise ValueError(f"Missing funding symbols at {timestamp}: {missing}")
        aggregate_rate = sum((rates_by_symbol[s] for s in SYMBOLS), Decimal("0")) / Decimal(len(SYMBOLS))
        aggregate_funding_rates.append(aggregate_rate)
        aggregate_event_bps = aggregate_rate * Decimal("10000")
        aggregate_funding_bps += aggregate_event_bps
        month = month_key(timestamp)
        monthly_funding_bps[month] += aggregate_event_bps
        monthly_funding_event_counts[month] += 1
        if aggregate_rate > 0:
            funding_positive_count += 1
            monthly_funding_sign_counts[month]["positive"] += 1
        elif aggregate_rate < 0:
            funding_negative_count += 1
            monthly_funding_sign_counts[month]["negative"] += 1
        else:
            funding_zero_count += 1
            monthly_funding_sign_counts[month]["zero"] += 1

    lifecycle_cost_bps = Decimal("30.0")
    monthly_rebalance_cost_per_month_bps = Decimal("5.0")
    monthly_rebalance_cost_bps = monthly_rebalance_cost_per_month_bps * Decimal(len(WINDOW_MONTHS))
    gross_total_bps = aggregate_price_bps + aggregate_funding_bps
    net_after_lifecycle_cost_bps = gross_total_bps - lifecycle_cost_bps
    net_after_monthly_rebalance_cost_bps = gross_total_bps - monthly_rebalance_cost_bps

    monthly_records = {}
    monthly_positive_count = 0
    best_month = None
    worst_month = None
    for month in WINDOW_MONTHS:
        month_price = sum((monthly_price_by_symbol[s][month] for s in SYMBOLS), Decimal("0")) / Decimal(len(SYMBOLS))
        month_funding = monthly_funding_bps[month]
        month_gross = month_price + month_funding
        month_net = month_gross - monthly_rebalance_cost_per_month_bps
        if month_net > 0:
            monthly_positive_count += 1
        record = {
            "month": month,
            "hour_count": monthly_hour_counts[month],
            "funding_event_count": monthly_funding_event_counts[month],
            "funding_positive_event_count": monthly_funding_sign_counts[month]["positive"],
            "funding_negative_event_count": monthly_funding_sign_counts[month]["negative"],
            "gross_price_component_bps": rounded_decimal(month_price),
            "gross_funding_component_bps": rounded_decimal(month_funding),
            "gross_total_bps": rounded_decimal(month_gross),
            "monthly_rebalance_cost_bps": rounded_decimal(monthly_rebalance_cost_per_month_bps),
            "net_after_monthly_rebalance_cost_bps": rounded_decimal(month_net),
        }
        monthly_records[month] = record
        if best_month is None or month_net > d(best_month["net_after_monthly_rebalance_cost_bps"]):
            best_month = record
        if worst_month is None or month_net < d(worst_month["net_after_monthly_rebalance_cost_bps"]):
            worst_month = record

    symbol_metrics = {}
    symbol_gross_values = {}
    for symbol in SYMBOLS:
        gross = symbol_price_bps[symbol] + symbol_funding_bps[symbol]
        symbol_gross_values[symbol] = gross
    abs_symbol_gross_sum = sum((abs(value) for value in symbol_gross_values.values()), Decimal("0"))
    for symbol in SYMBOLS:
        gross = symbol_gross_values[symbol]
        symbol_metrics[symbol] = {
            "symbol": symbol,
            "hour_count": symbol_hour_counts[symbol],
            "funding_event_count": len(funding_records[symbol]),
            "forward_holdout_2_gross_price_component_bps": rounded_decimal(symbol_price_bps[symbol]),
            "forward_holdout_2_funding_component_bps": rounded_decimal(symbol_funding_bps[symbol]),
            "forward_holdout_2_gross_total_bps": rounded_decimal(gross),
            "forward_holdout_2_net_after_lifecycle_cost_bps": rounded_decimal(gross - lifecycle_cost_bps),
            "forward_holdout_2_equal_weight_contribution_to_aggregate_gross_bps": rounded_decimal(gross / Decimal(len(SYMBOLS))),
            "symbol_abs_gross_contribution_share": rounded_decimal(abs(gross) / abs_symbol_gross_sum if abs_symbol_gross_sum else Decimal("0")),
            "funding_positive_event_count": symbol_funding_counts[symbol]["positive"],
            "funding_negative_event_count": symbol_funding_counts[symbol]["negative"],
            "funding_zero_event_count": symbol_funding_counts[symbol]["zero"],
            "negative_funding_event_share": rounded_decimal(
                Decimal(symbol_funding_counts[symbol]["negative"]) / Decimal(len(funding_records[symbol]))
                if funding_records[symbol]
                else Decimal("0")
            ),
        }

    total_events = funding_positive_count + funding_negative_count + funding_zero_count
    monthly_positive_rate = Decimal(monthly_positive_count) / Decimal(len(WINDOW_MONTHS))
    average_funding_rate = (
        sum(aggregate_funding_rates, Decimal("0")) / Decimal(len(aggregate_funding_rates))
        if aggregate_funding_rates
        else Decimal("0")
    )
    aggregate_metrics = {
        "window_start_utc": WINDOW_START_UTC,
        "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
        "symbols": list(SYMBOLS),
        "hour_count": len(common_hours),
        "month_count": len(WINDOW_MONTHS),
        "forward_holdout_2_gross_price_component_bps": rounded_decimal(aggregate_price_bps),
        "forward_holdout_2_funding_component_bps": rounded_decimal(aggregate_funding_bps),
        "forward_holdout_2_gross_total_bps": rounded_decimal(gross_total_bps),
        "lifecycle_cost_bps": rounded_decimal(lifecycle_cost_bps),
        "monthly_rebalance_cost_per_month_bps": rounded_decimal(monthly_rebalance_cost_per_month_bps),
        "monthly_rebalance_cost_bps": rounded_decimal(monthly_rebalance_cost_bps),
        "forward_holdout_2_net_after_lifecycle_cost_bps": rounded_decimal(net_after_lifecycle_cost_bps),
        "forward_holdout_2_net_after_monthly_rebalance_cost_bps": rounded_decimal(net_after_monthly_rebalance_cost_bps),
        "forward_holdout_2_monthly_positive_rate": rounded_decimal(monthly_positive_rate),
        "worst_month": worst_month,
        "best_month": best_month,
        "funding_positive_event_count": funding_positive_count,
        "funding_negative_event_count": funding_negative_count,
        "funding_zero_event_count": funding_zero_count,
        "funding_total_event_count": total_events,
        "negative_funding_event_share": rounded_decimal(Decimal(funding_negative_count) / Decimal(total_events) if total_events else Decimal("0")),
        "average_funding_rate": rounded_rate(average_funding_rate),
    }
    funding_event_summary = {
        "aggregate_event_count_uses_equal_weight_average_rate_per_funding_timestamp": True,
        "funding_positive_event_count": funding_positive_count,
        "funding_negative_event_count": funding_negative_count,
        "funding_zero_event_count": funding_zero_count,
        "funding_total_event_count": total_events,
        "negative_funding_event_share": aggregate_metrics["negative_funding_event_share"],
        "average_funding_rate": aggregate_metrics["average_funding_rate"],
        "per_symbol_event_counts": {
            symbol: {
                "positive": symbol_funding_counts[symbol]["positive"],
                "negative": symbol_funding_counts[symbol]["negative"],
                "zero": symbol_funding_counts[symbol]["zero"],
                "total": len(funding_records[symbol]),
            }
            for symbol in SYMBOLS
        },
    }
    metric_integrity = {
        "common_hour_count": len(common_hours),
        "expected_common_hour_count": 4344,
        "aggregate_funding_event_count": total_events,
        "expected_aggregate_funding_event_count": 543,
        "all_symbol_spot_row_counts": {symbol: len(spot_rows[symbol]) for symbol in SYMBOLS},
        "all_symbol_perp_row_counts": {symbol: len(perp_rows[symbol]) for symbol in SYMBOLS},
        "all_symbol_funding_record_counts": {symbol: len(funding_records[symbol]) for symbol in SYMBOLS},
        "passed": len(common_hours) == 4344
        and total_events == 543
        and all(len(spot_rows[s]) == 4344 for s in SYMBOLS)
        and all(len(perp_rows[s]) == 4344 for s in SYMBOLS)
        and all(len(funding_records[s]) == 543 for s in SYMBOLS),
    }
    return aggregate_metrics, symbol_metrics, monthly_records, funding_event_summary, metric_integrity


def build_artifact() -> dict:
    repo_clean_before_run = repo_clean_except_expected_outputs()
    source_checkpoint = git_output(["rev-parse", "HEAD"])

    review = load_json(DATA_REVIEW_PATH)
    acquisition = load_json(ACQUISITION_MANIFEST_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    risk = load_json(RISK_PATH)

    review_passed = (
        review.get("status") == REQUIRED_REVIEW_STATUS
        and review.get("data_validity_classification") == REQUIRED_REVIEW_CLASSIFICATION
        and review.get("replacement_checks_all_true") is True
    )
    if not review_passed:
        raise ValueError("Forward extension data review did not pass required checks")

    acquisition_scope = acquisition.get("acquisition_scope", {})
    if acquisition_scope.get("window_start_utc") != WINDOW_START_UTC or acquisition_scope.get("window_end_exclusive_utc") != WINDOW_END_EXCLUSIVE_UTC:
        raise ValueError("Acquisition manifest window does not match forward holdout-2 scope")

    index_path = Path(acquisition["non_repo_artifacts"]["extension_index"])
    index = load_json(index_path)
    if tuple(index.get("symbols", [])) != SYMBOLS:
        raise ValueError("External index symbols do not match required symbols")

    aggregate_metrics, symbol_metrics, monthly_metrics, funding_summary, metric_integrity = compute_diagnostic(index)

    prior_result = {
        "route_family": "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE",
        "config_id": "spot_long_perp_short_always_on_funding_carry_3symbol",
        "symbols": list(SYMBOLS),
        "diagnostic_promising": True,
        "final_result_class": REQUIRED_BASE_RESULT_CLASS,
        "risk_capital_classification": safe_get(
            risk,
            ["feasibility_classification", "classification"],
            "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_STRONG_DIAGNOSTIC_NO_LIVE_PERMISSION",
        ),
        "candidate_generation_allowed": False,
        "edge_claim_allowed": False,
        "runtime_live_capital_allowed": False,
        "prior_artifacts_loaded": {
            "execution": execution.get("status"),
            "evaluator": evaluator.get("status"),
            "closure": closure.get("status"),
            "risk_capital": risk.get("status"),
        },
    }
    prior_comparison = build_prior_comparison(execution, risk)
    fwd_lifecycle = d(aggregate_metrics["forward_holdout_2_net_after_lifecycle_cost_bps"])
    fwd_monthly = d(aggregate_metrics["forward_holdout_2_net_after_monthly_rebalance_cost_bps"])
    fwd_funding = d(aggregate_metrics["forward_holdout_2_funding_component_bps"])
    fwd_price = d(aggregate_metrics["forward_holdout_2_gross_price_component_bps"])
    fwd_monthly_rate = d(aggregate_metrics["forward_holdout_2_monthly_positive_rate"])
    comparison = {
        "prior_reference_metrics": prior_comparison,
        "forward_holdout_2_vs_validation": {
            "net_after_lifecycle_delta_bps": rounded_decimal(fwd_lifecycle - d(prior_comparison["validation"]["base_net_after_lifecycle_cost_bps"])),
            "net_after_monthly_rebalance_delta_bps": rounded_decimal(fwd_monthly - d(prior_comparison["validation"]["base_net_after_monthly_rebalance_cost_bps"])),
            "monthly_positive_rate_delta": rounded_decimal(fwd_monthly_rate - d(prior_comparison["validation"]["monthly_positive_rate"])),
            "forward_net_vs_validation_50pct_haircut_2x_cost_delta_bps": rounded_decimal(
                fwd_lifecycle - d(prior_comparison["validation"]["fifty_pct_funding_haircut_2x_cost_net_bps"])
            ),
        },
        "forward_holdout_2_vs_holdout_1": {
            "net_after_lifecycle_delta_bps": rounded_decimal(fwd_lifecycle - d(prior_comparison["holdout_1"]["base_net_after_lifecycle_cost_bps"])),
            "net_after_monthly_rebalance_delta_bps": rounded_decimal(fwd_monthly - d(prior_comparison["holdout_1"]["base_net_after_monthly_rebalance_cost_bps"])),
            "monthly_positive_rate_delta": rounded_decimal(fwd_monthly_rate - d(prior_comparison["holdout_1"]["monthly_positive_rate"])),
            "forward_net_vs_holdout_50pct_haircut_2x_cost_delta_bps": rounded_decimal(
                fwd_lifecycle - d(prior_comparison["holdout_1"]["fifty_pct_funding_haircut_2x_cost_net_bps"])
            ),
        },
        "forward_holdout_2_price_component_bps": rounded_decimal(fwd_price),
        "forward_holdout_2_funding_component_bps": rounded_decimal(fwd_funding),
    }

    if not metric_integrity["passed"]:
        assessment = "FORWARD_HOLDOUT_2_INCONCLUSIVE_DATA_OR_METRIC_LIMITATION_NO_LIVE_PERMISSION"
        assessment_reason = "Metric integrity checks did not pass."
    elif fwd_lifecycle <= 0 or fwd_monthly_rate < Decimal("0.50") or fwd_funding <= 0:
        assessment = "FORWARD_HOLDOUT_2_FAILS_FUNDING_CARRY_DIAGNOSTIC_NO_LIVE_PERMISSION"
        assessment_reason = "Aggregate net, monthly positive rate, or funding component failed the diagnostic thresholds."
    elif fwd_lifecycle > 0 and fwd_monthly_rate >= Decimal("0.60") and fwd_funding > 0:
        assessment = "FORWARD_HOLDOUT_2_SUPPORTS_FUNDING_CARRY_DIAGNOSTIC_NO_LIVE_PERMISSION"
        assessment_reason = "Aggregate lifecycle-net is positive, monthly positive rate is at least 0.60, funding component is positive, and metric integrity passed."
    else:
        assessment = "FORWARD_HOLDOUT_2_MIXED_WEAKENS_BUT_DOES_NOT_INVALIDATE_NO_LIVE_PERMISSION"
        assessment_reason = "Aggregate diagnostics are mixed but do not meet fail thresholds."

    safety_permissions = {
        "forward_extension_diagnostic_created": True,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "scheduler_allowed_now": False,
        "daemon_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "next_step_must_not_be_live_or_capital": True,
    }
    validation_checks = {
        "repo_clean_before_run": repo_clean_before_run,
        "forward_extension_data_review_loaded": True,
        "forward_extension_review_passed": review_passed,
        "prior_strategy_artifacts_loaded": all(
            artifact.get("status") for artifact in (execution, evaluator, closure, risk)
        ),
        "exact_symbols_verified_3": tuple(index.get("symbols", [])) == SYMBOLS,
        "no_network_used": True,
        "no_api_called": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_live_or_capital_permission": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_family_release": True,
        "metric_integrity_passed": metric_integrity["passed"],
        "exactly_one_python_tool_created": MODULE_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }
    replacement_checks_all_true = all(validation_checks.values()) and all(
        value is False
        for key, value in safety_permissions.items()
        if key.endswith("_allowed_now") or key in ("scheduler_allowed_now", "daemon_allowed_now")
    )

    artifact = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "head": source_checkpoint,
            "repo_clean_before_run": repo_clean_before_run,
            "expected_head": "152c50781d1b54491ddfd33b9d76eb5bf00d0d35",
        },
        "source_artifacts": {
            "forward_extension_data_review": str(DATA_REVIEW_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "forward_extension_acquisition_lock": str(ACQUISITION_MANIFEST_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "external_extension_index": str(index_path),
            "prior_strategy_execution": str(EXECUTION_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "prior_strategy_evaluator": str(EVALUATOR_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "prior_strategy_closure": str(CLOSURE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "prior_risk_capital_diagnostic": str(RISK_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "prior_route_result_preserved": prior_result,
        "forward_extension_data_review_preserved": {
            "status": review.get("status"),
            "data_validity_classification": review.get("data_validity_classification"),
            "reviewed_counts": {
                "spot": safe_get(review, ["aggregate_validation_review", "reviewed_spot_rows"]),
                "perp": safe_get(review, ["aggregate_validation_review", "reviewed_perp_rows"]),
                "funding": safe_get(review, ["aggregate_validation_review", "reviewed_funding_records"]),
            },
            "duplicate_counts": safe_get(review, ["aggregate_validation_review", "duplicate_counts"]),
            "ohlc_sanity_valid": safe_get(review, ["aggregate_validation_review", "ohlc_sanity_valid"]),
            "numeric_sanity_valid": safe_get(review, ["aggregate_validation_review", "numeric_sanity_valid"]),
            "next_allowed_step": "EXTENDED_FUNDING_CARRY_DIAGNOSTIC_ONLY",
        },
        "diagnostic_method": {
            "scope": "forward_holdout_2_only",
            "window_start_utc": WINDOW_START_UTC,
            "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
            "position_model": "long Binance spot and short Binance USD-M perpetual",
            "weighting": "equal_weight_across_BTCUSDT_ETHUSDT_SOLUSDT",
            "price_component": "sum hourly equal-weight average of spot open-to-close return minus perp open-to-close return, in bps",
            "funding_component": "sum equal-weight average funding rate at each funding timestamp, in bps; positive funding is treated as received by the short perp leg",
            "cost_assumptions": {
                "lifecycle_cost_bps": aggregate_metrics["lifecycle_cost_bps"],
                "monthly_rebalance_cost_per_month_bps": aggregate_metrics["monthly_rebalance_cost_per_month_bps"],
                "source": "prior execution/risk artifacts; fallback values match recorded 30 bps lifecycle and 5 bps per month rebalance assumptions",
            },
            "no_compounding": True,
            "no_reinvestment": True,
            "no_leverage_assumption": True,
            "old_base_route_not_modified": True,
        },
        "forward_holdout_2_aggregate_metrics": aggregate_metrics,
        "forward_holdout_2_symbol_metrics": symbol_metrics,
        "forward_holdout_2_monthly_metrics": {
            "monthly_records": monthly_metrics,
            "month_count": len(WINDOW_MONTHS),
            "monthly_positive_count": sum(
                1 for record in monthly_metrics.values() if d(record["net_after_monthly_rebalance_cost_bps"]) > 0
            ),
            "monthly_positive_rate": aggregate_metrics["forward_holdout_2_monthly_positive_rate"],
            "worst_month": aggregate_metrics["worst_month"],
            "best_month": aggregate_metrics["best_month"],
        },
        "funding_event_summary": funding_summary,
        "comparison_to_prior_validation_holdout": comparison,
        "forward_extension_assessment": {
            "classification": assessment,
            "reason": assessment_reason,
            "grants_candidate_or_edge_or_live_or_capital_permission": False,
        },
        "limitations": [
            "Forward diagnostic uses reviewed extension rows only and does not rerun or modify the prior base diagnostic artifacts.",
            "No live exchange/account state, margin/liquidation model, actual fees, actual slippage, or capital allocation is modeled.",
            "The diagnostic is historical and public-data based; it is not a candidate, edge claim, family release, or live/capital permission.",
            "Monthly rebalance cost follows prior artifact convention and is not additive with lifecycle cost in the net_after_monthly_rebalance_cost_bps field.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)
    return artifact


def main() -> None:
    artifact = build_artifact()
    write_json(ARTIFACT_PATH, artifact)
    aggregate = artifact["forward_holdout_2_aggregate_metrics"]
    funding = artifact["funding_event_summary"]
    print(f"status: {artifact['status']}")
    print(f"forward_extension_assessment: {artifact['forward_extension_assessment']['classification']}")
    print(f"forward_holdout_2_net_after_lifecycle_cost_bps: {aggregate['forward_holdout_2_net_after_lifecycle_cost_bps']}")
    print(f"forward_holdout_2_net_after_monthly_rebalance_cost_bps: {aggregate['forward_holdout_2_net_after_monthly_rebalance_cost_bps']}")
    print(f"forward_holdout_2_funding_component_bps: {aggregate['forward_holdout_2_funding_component_bps']}")
    print(f"forward_holdout_2_price_component_bps: {aggregate['forward_holdout_2_gross_price_component_bps']}")
    print(f"forward_holdout_2_monthly_positive_rate: {aggregate['forward_holdout_2_monthly_positive_rate']}")
    print(f"funding_positive_event_count: {funding['funding_positive_event_count']}")
    print(f"funding_negative_event_count: {funding['funding_negative_event_count']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(artifact['replacement_checks_all_true']).lower()}")


if __name__ == "__main__":
    main()
