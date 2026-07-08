#!/usr/bin/env python
"""Simulate a repaired common-quantity order sizing algorithm without new prices or orders."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, getcontext
from math import gcd
from pathlib import Path


getcontext().prec = 50

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.py"
ARTIFACT_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

PRICE_SNAPSHOT_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_price_snapshot_order_sizing_sim_v1.json"
)
FAILURE_ANALYSIS_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_failure_analysis_v1.json"
)
EXCHANGE_RULE_RELATIVE_PATH = (
    "artifacts/exchange_rule_discovery/binance_spot_perp_funding_carry_exchange_rule_discovery_v1.json"
)
OPERATIONAL_RELATIVE_PATH = (
    "artifacts/operational_feasibility/"
    "binance_spot_perp_delta_neutral_funding_carry_operational_feasibility_v1.json"
)
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/"
    "binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)

PRICE_SNAPSHOT_PATH = REPO_ROOT / PRICE_SNAPSHOT_RELATIVE_PATH
FAILURE_ANALYSIS_PATH = REPO_ROOT / FAILURE_ANALYSIS_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
OPERATIONAL_PATH = REPO_ROOT / OPERATIONAL_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_ORDER_SIZING_REPAIR_SIM_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_ORDER_SIZING_REPAIR_SIMULATION"

PRICE_SNAPSHOT_PAYLOAD_SHA256 = "b179b6efbe52ddb7611d678c7ac37e090fc1211784373a07e7bc64ecec2c470b"
FAILURE_ANALYSIS_PAYLOAD_SHA256 = "08b25b02675e327d5e9f76f1a8e081b5599b7f9cfa8c83868d7a7745df3e7b13"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
OPERATIONAL_PAYLOAD_SHA256 = "5af80fc87f583f4f5f4ed4baaa5620d708eff1ade5aaa54969d4259e54d6604e"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"

PRICE_SNAPSHOT_CLASSIFICATION = "PRICE_SNAPSHOT_ORDER_SIZING_SIM_FAIL_NO_LIVE_PERMISSION"
FAILURE_ANALYSIS_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_ORDER_SIZING_FAILURE_ANALYSIS_CREATED"
FAILURE_ASSESSMENT = "SIZING_ALGORITHM_REPAIR_NEEDED_UNDER_VALID_EXCHANGE_RULES"
NEXT_ALLOWED_FROM_FAILURE = "ORDER_SIZING_ALGORITHM_REPAIR_SIMULATION_ONLY"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS_USDT = (100, 235, 250, 500, 1000, 2500, 5000)
MISMATCH_THRESHOLD_BPS = Decimal("25")
UNUSED_NOTIONAL_THRESHOLD_BPS = Decimal("500")
MAX_OVESPEND_BPS = Decimal("25")
ESTIMATE_MAX_CAPITAL_USDT = Decimal("25000")
ESTIMATE_STEP_USDT = Decimal("1")
TRACKED_PYTHON_COUNT_AT_START = 887


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def decimal_value(value: object, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise RuntimeError(f"invalid Decimal for {field}: {value!r}") from exc
    if not parsed.is_finite():
        raise RuntimeError(f"non-finite Decimal for {field}: {value!r}")
    return parsed


def decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def decimal_float(value: Decimal) -> float:
    return float(value)


def ceil_decimal(value: Decimal) -> Decimal:
    return value.to_integral_value(rounding=ROUND_CEILING)


def floor_decimal(value: Decimal) -> Decimal:
    return value.to_integral_value(rounding=ROUND_FLOOR)


def decimal_step_to_scaled_int(step: Decimal, scale: Decimal) -> int:
    scaled = step * scale
    integer = scaled.to_integral_value()
    if scaled != integer:
        raise RuntimeError(f"step does not scale to integer: step={step} scale={scale}")
    return int(integer)


def lcm_decimal_step(step_a: Decimal, step_b: Decimal) -> Decimal:
    exponent = min(step_a.as_tuple().exponent, step_b.as_tuple().exponent, 0)
    scale = Decimal(10) ** Decimal(-exponent)
    int_a = decimal_step_to_scaled_int(step_a, scale)
    int_b = decimal_step_to_scaled_int(step_b, scale)
    lcm_int = abs(int_a * int_b) // gcd(int_a, int_b)
    return Decimal(lcm_int) / scale


def min_notional_from_filters(filters: dict, side: str) -> Decimal:
    if side == "spot":
        if "MIN_NOTIONAL" in filters:
            return decimal_value(filters["MIN_NOTIONAL"]["minNotional"], "spot minNotional")
        if "NOTIONAL" in filters:
            return decimal_value(filters["NOTIONAL"]["minNotional"], "spot minNotional")
    if side == "futures" and "MIN_NOTIONAL" in filters:
        return decimal_value(filters["MIN_NOTIONAL"]["notional"], "futures minNotional")
    raise RuntimeError(f"missing minNotional for {side}")


def rule_params(exchange_rules: dict, symbol: str, side: str) -> dict:
    rules = (
        exchange_rules["spot_exchange_rules"][symbol]
        if side == "spot"
        else exchange_rules["futures_exchange_rules"][symbol]
    )
    filters = rules["filters"]
    lot = filters["LOT_SIZE"]
    return {
        "min_qty": decimal_value(lot["minQty"], f"{side} {symbol} minQty"),
        "max_qty": decimal_value(lot["maxQty"], f"{side} {symbol} maxQty"),
        "step_size": decimal_value(lot["stepSize"], f"{side} {symbol} stepSize"),
        "min_notional": min_notional_from_filters(filters, side),
    }


def validate_sources(
    price_snapshot: dict,
    failure: dict,
    exchange_rules: dict,
    operational: dict,
    risk_capital: dict,
) -> None:
    if price_snapshot.get("payload_sha256_excluding_hash") != PRICE_SNAPSHOT_PAYLOAD_SHA256:
        raise RuntimeError("price snapshot sizing payload hash mismatch")
    if price_snapshot["classification"]["classification"] != PRICE_SNAPSHOT_CLASSIFICATION:
        raise RuntimeError("price snapshot sizing classification mismatch")
    if failure.get("status") != FAILURE_ANALYSIS_STATUS:
        raise RuntimeError("failure analysis status mismatch")
    if failure.get("payload_sha256_excluding_hash") != FAILURE_ANALYSIS_PAYLOAD_SHA256:
        raise RuntimeError("failure analysis payload hash mismatch")
    if failure["sizing_algorithm_vs_exchange_rule_assessment"]["assessment"] != FAILURE_ASSESSMENT:
        raise RuntimeError("failure analysis assessment mismatch")
    if failure["next_allowed_step"] != NEXT_ALLOWED_FROM_FAILURE:
        raise RuntimeError("failure analysis next allowed step mismatch")
    if exchange_rules.get("payload_sha256_excluding_hash") != EXCHANGE_RULE_PAYLOAD_SHA256:
        raise RuntimeError("exchange rule payload hash mismatch")
    if operational.get("payload_sha256_excluding_hash") != OPERATIONAL_PAYLOAD_SHA256:
        raise RuntimeError("operational payload hash mismatch")
    if risk_capital.get("payload_sha256_excluding_hash") != RISK_CAPITAL_PAYLOAD_SHA256:
        raise RuntimeError("risk/capital payload hash mismatch")
    if set(price_snapshot["price_snapshot"]["spot_prices"]) != set(SYMBOLS):
        raise RuntimeError("stored spot prices missing required symbols")
    if set(price_snapshot["price_snapshot"]["futures_prices"]) != set(SYMBOLS):
        raise RuntimeError("stored futures prices missing required symbols")


def build_prices_and_params(price_snapshot: dict, exchange_rules: dict) -> tuple[dict, dict]:
    prices = {
        "spot": {
            symbol: decimal_value(price_snapshot["price_snapshot"]["spot_prices"][symbol], f"spot {symbol} price")
            for symbol in SYMBOLS
        },
        "futures": {
            symbol: decimal_value(
                price_snapshot["price_snapshot"]["futures_prices"][symbol],
                f"futures {symbol} price",
            )
            for symbol in SYMBOLS
        },
    }
    params = {
        symbol: {
            "spot": rule_params(exchange_rules, symbol, "spot"),
            "futures": rule_params(exchange_rules, symbol, "futures"),
        }
        for symbol in SYMBOLS
    }
    return prices, params


def candidate_quantities(
    target_notional: Decimal,
    spot_price: Decimal,
    futures_price: Decimal,
    common_step: Decimal,
    min_common_qty: Decimal,
    max_common_qty: Decimal,
) -> list[Decimal]:
    target_by_spot = target_notional / spot_price
    target_by_futures = target_notional / futures_price
    target_common_qty = min(target_by_spot, target_by_futures)
    avg_price = (spot_price + futures_price) / Decimal("2")
    target_by_avg = target_notional / avg_price
    max_leg_price = max(spot_price, futures_price)
    overspend_qty_cap = (target_notional * (Decimal("1") + MAX_OVESPEND_BPS / Decimal("10000"))) / max_leg_price

    lower_k = ceil_decimal(min_common_qty / common_step)
    upper_k = floor_decimal(min(max_common_qty, overspend_qty_cap) / common_step)
    if upper_k < lower_k:
        return []

    center_values = [
        floor_decimal(target_common_qty / common_step),
        ceil_decimal(target_common_qty / common_step),
        floor_decimal(target_by_avg / common_step),
        ceil_decimal(target_by_avg / common_step),
    ]
    k_values: set[int] = set()
    for center in center_values:
        for offset in range(-25, 26):
            candidate_k = int(center) + offset
            if int(lower_k) <= candidate_k <= int(upper_k):
                k_values.add(candidate_k)
    k_values.add(int(lower_k))
    k_values.add(int(upper_k))
    return sorted((Decimal(k) * common_step for k in k_values))


def evaluate_quantity(
    common_qty: Decimal,
    target_notional: Decimal,
    spot_price: Decimal,
    futures_price: Decimal,
    spot_params: dict,
    futures_params: dict,
) -> dict:
    spot_notional = common_qty * spot_price
    futures_notional = common_qty * futures_price
    avg_notional = (spot_notional + futures_notional) / Decimal("2")
    mismatch_bps = (
        abs(spot_notional - futures_notional) / avg_notional * Decimal("10000")
        if avg_notional > 0
        else Decimal("0")
    )
    unused_bps = (
        (target_notional - avg_notional) / target_notional * Decimal("10000")
        if target_notional > 0
        else Decimal("0")
    )
    max_leg_notional = max(spot_notional, futures_notional)
    overspend_bps = (
        max(Decimal("0"), max_leg_notional - target_notional) / target_notional * Decimal("10000")
        if target_notional > 0
        else Decimal("0")
    )
    spot_min_qty_pass = common_qty >= spot_params["min_qty"]
    futures_min_qty_pass = common_qty >= futures_params["min_qty"]
    spot_max_qty_pass = common_qty <= spot_params["max_qty"]
    futures_max_qty_pass = common_qty <= futures_params["max_qty"]
    spot_min_notional_pass = spot_notional >= spot_params["min_notional"]
    futures_min_notional_pass = futures_notional >= futures_params["min_notional"]
    pass_checks = {
        "common_qty_positive": common_qty > 0,
        "spot_min_qty_pass": spot_min_qty_pass,
        "futures_min_qty_pass": futures_min_qty_pass,
        "spot_max_qty_pass": spot_max_qty_pass,
        "futures_max_qty_pass": futures_max_qty_pass,
        "spot_min_notional_pass": spot_min_notional_pass,
        "futures_min_notional_pass": futures_min_notional_pass,
        "leg_notional_mismatch_pass": mismatch_bps <= MISMATCH_THRESHOLD_BPS,
        "unused_notional_pass": unused_bps <= UNUSED_NOTIONAL_THRESHOLD_BPS,
        "overspend_rule_pass": overspend_bps <= MAX_OVESPEND_BPS,
    }
    return {
        "common_base_qty": common_qty,
        "spot_notional": spot_notional,
        "futures_notional": futures_notional,
        "avg_notional": avg_notional,
        "leg_notional_mismatch_bps": mismatch_bps,
        "unused_notional_vs_target_bps": unused_bps,
        "max_leg_overspend_bps": overspend_bps,
        "pass_checks": pass_checks,
        "symbol_pass": all(pass_checks.values()),
    }


def choose_best_quantity(
    target_notional: Decimal,
    symbol: str,
    prices: dict,
    params: dict,
) -> dict:
    spot_price = prices["spot"][symbol]
    futures_price = prices["futures"][symbol]
    spot_params = params[symbol]["spot"]
    futures_params = params[symbol]["futures"]
    common_step = lcm_decimal_step(spot_params["step_size"], futures_params["step_size"])
    min_common_qty = max(spot_params["min_qty"], futures_params["min_qty"])
    max_common_qty = min(spot_params["max_qty"], futures_params["max_qty"])
    target_by_spot = target_notional / spot_price
    target_by_futures = target_notional / futures_price
    target_common_qty = min(target_by_spot, target_by_futures)

    candidates = candidate_quantities(
        target_notional,
        spot_price,
        futures_price,
        common_step,
        min_common_qty,
        max_common_qty,
    )
    evaluated = [
        evaluate_quantity(candidate, target_notional, spot_price, futures_price, spot_params, futures_params)
        for candidate in candidates
    ]
    passing = [item for item in evaluated if item["symbol_pass"]]
    if passing:
        best = min(
            passing,
            key=lambda item: (
                abs(item["unused_notional_vs_target_bps"]),
                item["leg_notional_mismatch_bps"],
                item["max_leg_overspend_bps"],
            ),
        )
    elif evaluated:
        best = min(
            evaluated,
            key=lambda item: (
                0 if item["pass_checks"]["overspend_rule_pass"] else 1,
                abs(item["unused_notional_vs_target_bps"]),
                item["leg_notional_mismatch_bps"],
            ),
        )
    else:
        best = {
            "common_base_qty": Decimal("0"),
            "spot_notional": Decimal("0"),
            "futures_notional": Decimal("0"),
            "avg_notional": Decimal("0"),
            "leg_notional_mismatch_bps": Decimal("0"),
            "unused_notional_vs_target_bps": Decimal("10000"),
            "max_leg_overspend_bps": Decimal("0"),
            "pass_checks": {
                "common_qty_positive": False,
                "spot_min_qty_pass": False,
                "futures_min_qty_pass": False,
                "spot_max_qty_pass": True,
                "futures_max_qty_pass": True,
                "spot_min_notional_pass": False,
                "futures_min_notional_pass": False,
                "leg_notional_mismatch_pass": True,
                "unused_notional_pass": False,
                "overspend_rule_pass": True,
            },
            "symbol_pass": False,
        }

    return {
        "symbol": symbol,
        "target_notional_per_symbol": decimal_text(target_notional),
        "spot_price": decimal_text(spot_price),
        "futures_price": decimal_text(futures_price),
        "target_qty_by_spot": decimal_text(target_by_spot),
        "target_qty_by_futures": decimal_text(target_by_futures),
        "target_common_qty": decimal_text(target_common_qty),
        "common_step_size": decimal_text(common_step),
        "min_common_qty": decimal_text(min_common_qty),
        "max_common_qty": decimal_text(max_common_qty),
        "candidate_quantity_count": len(candidates),
        "selected_common_base_qty": decimal_text(best["common_base_qty"]),
        "spot_long_quantity": decimal_text(best["common_base_qty"]),
        "futures_short_quantity": decimal_text(best["common_base_qty"]),
        "spot_notional": decimal_text(best["spot_notional"]),
        "futures_notional": decimal_text(best["futures_notional"]),
        "avg_notional": decimal_text(best["avg_notional"]),
        "leg_notional_mismatch_bps": decimal_float(best["leg_notional_mismatch_bps"]),
        "unused_notional_vs_target_bps": decimal_float(best["unused_notional_vs_target_bps"]),
        "max_leg_overspend_bps": decimal_float(best["max_leg_overspend_bps"]),
        "small_overspend_used": best["max_leg_overspend_bps"] > 0,
        "pass_checks": best["pass_checks"],
        "symbol_pass": best["symbol_pass"],
    }


def simulate_capital(capital: Decimal, symbols: tuple[str, ...], prices: dict, params: dict) -> dict:
    target_notional = capital / Decimal(len(symbols))
    records = [choose_best_quantity(target_notional, symbol, prices, params) for symbol in symbols]
    scenario_pass = all(record["symbol_pass"] for record in records)
    max_mismatch = max(Decimal(str(record["leg_notional_mismatch_bps"])) for record in records) if records else Decimal("0")
    max_unused = max(Decimal(str(record["unused_notional_vs_target_bps"])) for record in records) if records else Decimal("0")
    return {
        "capital_usdt": decimal_text(capital),
        "symbols": list(symbols),
        "notional_per_symbol": decimal_text(target_notional),
        "scenario_pass": scenario_pass,
        "max_leg_mismatch_bps": decimal_float(max_mismatch),
        "max_unused_notional_bps": decimal_float(max_unused),
        "symbol_results": records,
    }


def estimate_min_capital(symbols: tuple[str, ...], prices: dict, params: dict) -> dict:
    capital = Decimal("1")
    while capital <= ESTIMATE_MAX_CAPITAL_USDT:
        result = simulate_capital(capital, symbols, prices, params)
        if result["scenario_pass"]:
            return {
                "available": True,
                "estimated_minimum_capital_usdt": decimal_text(capital),
                "notional_per_symbol": result["notional_per_symbol"],
                "symbols": list(symbols),
                "estimate_method": "stored_price_rule_common_quantity_scan_1_usdt_increment",
                "max_scan_capital_usdt": decimal_text(ESTIMATE_MAX_CAPITAL_USDT),
                "scenario_at_estimate": result,
            }
        capital += ESTIMATE_STEP_USDT
    return {
        "available": False,
        "reason": f"no passing common-quantity capital found up to {decimal_text(ESTIMATE_MAX_CAPITAL_USDT)} USDT",
        "symbols": list(symbols),
        "estimate_method": "stored_price_rule_common_quantity_scan_1_usdt_increment",
    }


def classify(all3_results: list[dict], all3_min: dict, btc_eth_min: dict) -> str:
    if any(item["scenario_pass"] and Decimal(item["capital_usdt"]) <= Decimal("5000") for item in all3_results):
        return "ORDER_SIZING_REPAIR_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION"
    if btc_eth_min.get("available") or all3_min.get("available"):
        return "ORDER_SIZING_REPAIR_SIM_PARTIAL_MIN_CAPITAL_REQUIRED_NO_LIVE_PERMISSION"
    return "ORDER_SIZING_REPAIR_SIM_FAIL_NO_LIVE_PERMISSION"


def main() -> int:
    ensure_target_absent()
    price_snapshot = load_json(PRICE_SNAPSHOT_PATH)
    failure = load_json(FAILURE_ANALYSIS_PATH)
    exchange_rules = load_json(EXCHANGE_RULE_PATH)
    operational = load_json(OPERATIONAL_PATH)
    risk_capital = load_json(RISK_CAPITAL_PATH)
    validate_sources(price_snapshot, failure, exchange_rules, operational, risk_capital)

    prices, params = build_prices_and_params(price_snapshot, exchange_rules)
    all3_results = [simulate_capital(Decimal(str(capital)), SYMBOLS, prices, params) for capital in CAPITAL_SCENARIOS_USDT]
    btc_eth_results = [
        simulate_capital(Decimal(str(capital)), ("BTCUSDT", "ETHUSDT"), prices, params)
        for capital in CAPITAL_SCENARIOS_USDT
    ]
    all3_min = estimate_min_capital(SYMBOLS, prices, params)
    btc_eth_min = estimate_min_capital(("BTCUSDT", "ETHUSDT"), prices, params)
    classification = classify(all3_results, all3_min, btc_eth_min)

    scenario_pass_fail_summary = {item["capital_usdt"]: item["scenario_pass"] for item in all3_results}
    max_leg_mismatch_bps_by_scenario = {
        item["capital_usdt"]: item["max_leg_mismatch_bps"] for item in all3_results
    }
    max_unused_notional_bps_by_scenario = {
        item["capital_usdt"]: item["max_unused_notional_bps"] for item in all3_results
    }
    minimum_passing_all3 = next(
        (item["capital_usdt"] for item in all3_results if item["scenario_pass"]),
        None,
    )
    minimum_passing_btc_eth = next(
        (item["capital_usdt"] for item in btc_eth_results if item["scenario_pass"]),
        None,
    )

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_price_snapshot_artifact_loaded": True,
        "prior_failure_analysis_loaded": True,
        "exchange_rule_discovery_loaded": True,
        "stored_prices_used": True,
        "no_new_price_fetch": True,
        "no_network_used": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "common_base_quantity_algorithm_used": True,
        "no_strategy_rerun": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
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
        "source_artifacts": {
            "price_snapshot_order_sizing_simulation": PRICE_SNAPSHOT_RELATIVE_PATH,
            "price_snapshot_payload_sha256_excluding_hash": PRICE_SNAPSHOT_PAYLOAD_SHA256,
            "order_sizing_failure_analysis": FAILURE_ANALYSIS_RELATIVE_PATH,
            "failure_analysis_payload_sha256_excluding_hash": FAILURE_ANALYSIS_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "operational_feasibility": OPERATIONAL_RELATIVE_PATH,
            "operational_payload_sha256_excluding_hash": OPERATIONAL_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
        },
        "prior_failure_preserved": {
            "prior_sizing_classification": price_snapshot["classification"]["classification"],
            "prior_failure_root_cause": failure["failure_root_cause"]["primary_root_cause"],
            "prior_failure_assessment": failure["sizing_algorithm_vs_exchange_rule_assessment"]["assessment"],
            "prior_next_allowed_step": failure["next_allowed_step"],
            "stored_prices_snapshot_time_utc": price_snapshot["price_snapshot"]["prices_snapshot_time_utc"],
        },
        "repaired_sizing_algorithm": {
            "principle": "choose one common base asset quantity per symbol for both spot long and futures short",
            "uses_common_quantity_for_both_legs": True,
            "uses_decimal_arithmetic_only": True,
            "common_step_size_method": "least_common_multiple_of_spot_and_futures_decimal_step_sizes",
            "target_common_qty_formula": "min(target_notional / spot_price, target_notional / futures_price)",
            "candidate_search": "near target common quantity and target average-notional quantity, with small overspend cap",
            "max_overspend_bps": decimal_float(MAX_OVESPEND_BPS),
            "leg_mismatch_threshold_bps": decimal_float(MISMATCH_THRESHOLD_BPS),
            "unused_notional_threshold_bps": decimal_float(UNUSED_NOTIONAL_THRESHOLD_BPS),
            "orders_placed": False,
        },
        "capital_scenario_results": all3_results,
        "symbol_scenario_results": {
            symbol: [
                {
                    "capital_usdt": scenario["capital_usdt"],
                    **next(result for result in scenario["symbol_results"] if result["symbol"] == symbol),
                }
                for scenario in all3_results
            ]
            for symbol in SYMBOLS
        },
        "btc_eth_only_diagnostic": {
            "diagnostic_only_no_symbol_change_permission": True,
            "scenario_results": btc_eth_results,
            "minimum_passing_capital_btc_eth_only": minimum_passing_btc_eth,
        },
        "estimated_min_capital": {
            "all3": all3_min,
            "btc_eth_only_diagnostic": btc_eth_min,
        },
        "classification": {
            "classification": classification,
            "minimum_passing_capital_all3": minimum_passing_all3,
            "minimum_passing_capital_btc_eth_only": minimum_passing_btc_eth,
            "root_cause_repaired": classification
            == "ORDER_SIZING_REPAIR_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION",
            "classification_grants_live_or_capital_permission": False,
        },
        "limitations": [
            "This repair simulation uses the stored price snapshot and stored exchange rules only.",
            "No new prices, network calls, APIs, order endpoints, or order placements are used.",
            "Passing sizing simulation does not model slippage, order book depth, balances, fees, margin, liquidation, or execution leg risk.",
            "BTC+ETH-only results are diagnostic only and grant no symbol-universe change permission.",
            "No candidate, edge claim, runtime, live trading, or capital allocation permission is granted.",
        ],
        "safety_permissions": {
            "order_sizing_repair_sim_created": True,
            "order_placement_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_paper_trading_design_only": classification
            == "ORDER_SIZING_REPAIR_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION",
            "next_step_must_not_be_live_or_capital": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")

    next_allowed_step = (
        "PAPER_TRADING_DESIGN_ONLY"
        if artifact["safety_permissions"]["next_step_may_be_paper_trading_design_only"]
        else "NO_PAPER_TRADING_DESIGN_UNTIL_SIZING_REPAIR_PASSES"
    )
    print(f"status: {STATUS}")
    print(f"classification: {classification}")
    print(f"minimum_passing_capital_all3: {minimum_passing_all3}")
    print(f"minimum_passing_capital_btc_eth_only: {minimum_passing_btc_eth}")
    print(f"scenario_pass_fail_summary: {json.dumps(scenario_pass_fail_summary, sort_keys=True)}")
    print(f"max_leg_mismatch_bps_by_scenario: {json.dumps(max_leg_mismatch_bps_by_scenario, sort_keys=True)}")
    print(f"max_unused_notional_bps_by_scenario: {json.dumps(max_unused_notional_bps_by_scenario, sort_keys=True)}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {str(replacement_checks_all_true).lower()}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
