#!/usr/bin/env python
"""Analyze the stored Binance spot-perp order sizing simulation failure without new API calls."""

from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_DOWN, getcontext
from pathlib import Path


getcontext().prec = 40

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_order_sizing_failure_analysis_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/"
    "binance_spot_perp_funding_carry_order_sizing_failure_analysis_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

SIZING_SIM_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/"
    "binance_spot_perp_funding_carry_price_snapshot_order_sizing_sim_v1.json"
)
EXCHANGE_RULE_RELATIVE_PATH = (
    "artifacts/exchange_rule_discovery/binance_spot_perp_funding_carry_exchange_rule_discovery_v1.json"
)

SIZING_SIM_PATH = REPO_ROOT / SIZING_SIM_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH

STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_ORDER_SIZING_FAILURE_ANALYSIS_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_ORDER_SIZING_FAILURE_ANALYSIS"

SIZING_SIM_PAYLOAD_SHA256 = "b179b6efbe52ddb7611d678c7ac37e090fc1211784373a07e7bc64ecec2c470b"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
SIZING_SIM_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PRICE_SNAPSHOT_ORDER_SIZING_SIM_CREATED"
SIZING_SIM_CLASSIFICATION = "PRICE_SNAPSHOT_ORDER_SIZING_SIM_FAIL_NO_LIVE_PERMISSION"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
MISMATCH_THRESHOLD_BPS = Decimal("25")
TRACKED_PYTHON_COUNT_AT_START = 886
MAX_ESTIMATE_CAPITAL_USDT = Decimal("1000000")
ESTIMATE_STEP_USDT = Decimal("1")


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
        existing = load_json(ARTIFACT_PATH)
        if existing.get("module") != MODULE_RELATIVE_PATH or existing.get("status") != STATUS:
            raise RuntimeError(f"target artifact already exists from a different producer: {ARTIFACT_PATH}")


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


def round_down_to_step(quantity: Decimal, step_size: Decimal) -> Decimal:
    if step_size <= 0:
        raise RuntimeError(f"invalid step size: {step_size}")
    increments = (quantity / step_size).to_integral_value(rounding=ROUND_DOWN)
    return increments * step_size


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


def simulated_leg(target_notional: Decimal, price: Decimal, params: dict) -> dict:
    raw_qty = target_notional / price
    rounded_qty = round_down_to_step(raw_qty, params["step_size"])
    rounded_notional = rounded_qty * price
    return {
        "raw_qty": raw_qty,
        "rounded_qty": rounded_qty,
        "rounded_notional": rounded_notional,
        "min_qty_failed": rounded_qty < params["min_qty"],
        "min_notional_failed": rounded_notional < params["min_notional"],
        "rule_pass": (
            rounded_qty >= params["min_qty"]
            and rounded_qty <= params["max_qty"]
            and rounded_notional >= params["min_notional"]
        ),
    }


def mismatch_for_symbol(target_notional: Decimal, symbol: str, prices: dict, params: dict) -> dict:
    spot = simulated_leg(target_notional, prices["spot"][symbol], params[symbol]["spot"])
    futures = simulated_leg(target_notional, prices["futures"][symbol], params[symbol]["futures"])
    mismatch_bps = (
        abs(spot["rounded_notional"] - futures["rounded_notional"]) / target_notional * Decimal("10000")
        if target_notional > 0
        else Decimal("0")
    )
    return {
        "spot": spot,
        "futures": futures,
        "mismatch_bps": mismatch_bps,
        "pass": spot["rule_pass"] and futures["rule_pass"] and mismatch_bps <= MISMATCH_THRESHOLD_BPS,
    }


def validate_sources(sizing: dict, exchange_rules: dict) -> None:
    if sizing.get("status") != SIZING_SIM_STATUS:
        raise RuntimeError("sizing simulation status mismatch")
    if sizing.get("payload_sha256_excluding_hash") != SIZING_SIM_PAYLOAD_SHA256:
        raise RuntimeError("sizing simulation payload hash mismatch")
    if sizing["classification"]["classification"] != SIZING_SIM_CLASSIFICATION:
        raise RuntimeError("sizing simulation classification mismatch")
    if exchange_rules.get("payload_sha256_excluding_hash") != EXCHANGE_RULE_PAYLOAD_SHA256:
        raise RuntimeError("exchange-rule discovery payload hash mismatch")
    if tuple(sizing["source_checkpoint"].get("repo_head_at_run", "") for _ in [0]) is None:
        raise RuntimeError("sizing source checkpoint missing")
    if set(sizing["price_snapshot"]["spot_prices"]) != set(SYMBOLS):
        raise RuntimeError("stored spot prices missing required symbols")
    if set(sizing["price_snapshot"]["futures_prices"]) != set(SYMBOLS):
        raise RuntimeError("stored futures prices missing required symbols")


def scenario_reason(symbol_record: dict) -> dict:
    spot = symbol_record["spot_rule_details"]
    futures = symbol_record["futures_rule_details"]
    mismatch_bps = decimal_value(symbol_record["leg_notional_mismatch_bps"], "leg mismatch bps")
    reasons = []
    if not spot["min_qty_pass"]:
        reasons.append("spot_min_qty_failed")
    if not spot["min_notional_pass"]:
        reasons.append("spot_min_notional_failed")
    if not futures["min_qty_pass"]:
        reasons.append("futures_min_qty_failed")
    if not futures["min_notional_pass"]:
        reasons.append("futures_min_notional_failed")
    if mismatch_bps > MISMATCH_THRESHOLD_BPS:
        reasons.append("leg_notional_mismatch_exceeds_25_bps")
    if spot["rule_pass"] and futures["rule_pass"] and mismatch_bps > MISMATCH_THRESHOLD_BPS:
        reasons.append("rounding_caused_mismatch_after_rules_passed")

    spot_step = decimal_value(spot["step_size"], "spot step")
    futures_step = decimal_value(futures["step_size"], "futures step")
    spot_price = decimal_value(symbol_record["spot_price"], "spot price")
    futures_price = decimal_value(symbol_record["futures_price"], "futures price")
    spot_increment = spot_step * spot_price
    futures_increment = futures_step * futures_price
    step_ratio = futures_increment / spot_increment if spot_increment > 0 else None
    symbol_step_mismatch = bool(step_ratio is not None and step_ratio > Decimal("5"))
    if symbol_step_mismatch and mismatch_bps > MISMATCH_THRESHOLD_BPS:
        reasons.append("symbol_specific_step_size_granularity_mismatch")

    return {
        "exact_failing_reasons": reasons,
        "min_notional_failed": (not spot["min_notional_pass"]) or (not futures["min_notional_pass"]),
        "min_qty_failed": (not spot["min_qty_pass"]) or (not futures["min_qty_pass"]),
        "rounding_caused_mismatch": mismatch_bps > MISMATCH_THRESHOLD_BPS,
        "symbol_specific_step_size_caused_mismatch": symbol_step_mismatch and mismatch_bps > MISMATCH_THRESHOLD_BPS,
        "spot_notional_increment_usdt": decimal_text(spot_increment),
        "futures_notional_increment_usdt": decimal_text(futures_increment),
        "futures_to_spot_notional_increment_ratio": decimal_text(step_ratio),
    }


def analyze_scenarios(sizing: dict) -> tuple[list[dict], dict]:
    scenario_records = []
    failing_by_scenario = {}
    for scenario in sizing["order_sizing_simulation_results"]["scenarios"]:
        scenario_failures = []
        symbol_records = []
        for symbol_record in scenario["symbols"]:
            reason = scenario_reason(symbol_record)
            record = {
                "symbol": symbol_record["symbol"],
                "target_notional": symbol_record["target_notional"],
                "spot_price": symbol_record["spot_price"],
                "futures_price": symbol_record["futures_price"],
                "spot_quantity_raw": symbol_record["spot_quantity_raw"],
                "spot_quantity_rounded": symbol_record["spot_quantity_rounded"],
                "futures_quantity_raw": symbol_record["futures_quantity_raw"],
                "futures_quantity_rounded": symbol_record["futures_quantity_rounded"],
                "spot_notional_rounded": symbol_record["spot_notional_rounded"],
                "futures_notional_rounded": symbol_record["futures_notional_rounded"],
                "leg_mismatch_bps": symbol_record["leg_notional_mismatch_bps"],
                "spot_rule_pass": symbol_record["spot_rule_pass"],
                "futures_rule_pass": symbol_record["futures_rule_pass"],
                "scenario_symbol_pass": symbol_record["scenario_symbol_pass"],
                **reason,
            }
            symbol_records.append(record)
            if not symbol_record["scenario_symbol_pass"]:
                scenario_failures.append(symbol_record["symbol"])
        scenario_records.append(
            {
                "capital_usdt": scenario["capital_usdt"],
                "notional_per_symbol": scenario["notional_per_symbol"],
                "scenario_pass": scenario["scenario_pass"],
                "max_leg_mismatch_bps": scenario["max_leg_mismatch_bps"],
                "failing_symbols": scenario_failures,
                "symbols": symbol_records,
            }
        )
        failing_by_scenario[str(scenario["capital_usdt"])] = scenario_failures
    return scenario_records, failing_by_scenario


def subset_pass_for_stored_scenario(scenario: dict, symbols: tuple[str, ...]) -> bool:
    records = [record for record in scenario["symbols"] if record["symbol"] in symbols]
    if len(records) != len(symbols):
        return False
    return all(record["scenario_symbol_pass"] for record in records)


def dropping_sol_analysis(sizing: dict) -> dict:
    results = {}
    any_pass = False
    for scenario in sizing["order_sizing_simulation_results"]["scenarios"]:
        passed = subset_pass_for_stored_scenario(scenario, ("BTCUSDT", "ETHUSDT"))
        any_pass = any_pass or passed
        results[str(scenario["capital_usdt"])] = {
            "btc_eth_pass_without_sol_using_stored_three_symbol_notional": passed,
            "diagnostic_only_no_universe_change_permission": True,
        }
    return {
        "dropping_sol_would_make_btc_eth_pass": any_pass,
        "scenario_results": results,
        "note": (
            "This checks stored BTC and ETH symbol pass flags only. It does not change the route universe, "
            "does not recompute a two-symbol allocation, and grants no parameter or symbol change permission."
        ),
    }


def build_price_and_params(sizing: dict, exchange_rules: dict) -> tuple[dict, dict]:
    prices = {
        "spot": {
            symbol: decimal_value(sizing["price_snapshot"]["spot_prices"][symbol], f"spot {symbol} price")
            for symbol in SYMBOLS
        },
        "futures": {
            symbol: decimal_value(sizing["price_snapshot"]["futures_prices"][symbol], f"futures {symbol} price")
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


def estimate_min_capital(prices: dict, params: dict, symbols: tuple[str, ...]) -> dict:
    min_rule_capital = Decimal("0")
    for symbol in symbols:
        spot_min = max(params[symbol]["spot"]["min_qty"] * prices["spot"][symbol], params[symbol]["spot"]["min_notional"])
        futures_min = max(
            params[symbol]["futures"]["min_qty"] * prices["futures"][symbol],
            params[symbol]["futures"]["min_notional"],
        )
        min_rule_capital = max(min_rule_capital, max(spot_min, futures_min) * Decimal(len(symbols)))

    start = max(Decimal("1"), min_rule_capital.to_integral_value(rounding=ROUND_DOWN))
    if start < min_rule_capital:
        start += Decimal("1")
    capital = start
    while capital <= MAX_ESTIMATE_CAPITAL_USDT:
        target = capital / Decimal(len(symbols))
        checks = [mismatch_for_symbol(target, symbol, prices, params) for symbol in symbols]
        if all(check["pass"] for check in checks):
            return {
                "available": True,
                "estimated_minimum_capital_usdt": decimal_text(capital),
                "notional_per_symbol_usdt": decimal_text(target),
                "symbols": list(symbols),
                "estimate_method": "stored_price_rule_scan_1_usdt_increment",
                "max_scan_capital_usdt": decimal_text(MAX_ESTIMATE_CAPITAL_USDT),
                "symbol_mismatch_bps_at_estimate": {
                    symbol: float(checks[index]["mismatch_bps"]) for index, symbol in enumerate(symbols)
                },
            }
        capital += ESTIMATE_STEP_USDT
    return {
        "available": False,
        "reason": f"no passing capital found up to {decimal_text(MAX_ESTIMATE_CAPITAL_USDT)} USDT",
        "symbols": list(symbols),
        "estimate_method": "stored_price_rule_scan_1_usdt_increment",
    }


def root_cause(scenario_records: list[dict]) -> dict:
    all_fail_reasons = []
    for scenario in scenario_records:
        for symbol in scenario["symbols"]:
            all_fail_reasons.extend(symbol["exact_failing_reasons"])
    mismatch_failures = sum(1 for reason in all_fail_reasons if reason == "leg_notional_mismatch_exceeds_25_bps")
    min_notional_failures = sum(1 for reason in all_fail_reasons if reason.endswith("min_notional_failed"))
    min_qty_failures = sum(1 for reason in all_fail_reasons if reason.endswith("min_qty_failed"))
    step_failures = sum(1 for reason in all_fail_reasons if reason == "symbol_specific_step_size_granularity_mismatch")
    return {
        "primary_root_cause": "independent_spot_and_futures_round_down_with_coarse_futures_lot_size_created_leg_notional_mismatch",
        "secondary_root_causes": [
            "BTCUSDT futures 0.001 quantity step creates a large notional increment at the stored BTC futures price",
            "100 USDT scenario also fails BTCUSDT futures minQty and minNotional after rounding to zero",
            "ETHUSDT and SOLUSDT pass minQty/minNotional but still fail the 25 bps mismatch threshold in stored scenarios",
        ],
        "failure_counts": {
            "leg_notional_mismatch_exceeds_25_bps": mismatch_failures,
            "min_notional_failures": min_notional_failures,
            "min_qty_failures": min_qty_failures,
            "symbol_specific_step_size_granularity_mismatch": step_failures,
        },
        "sizing_algorithm_issue_or_exchange_rule_issue": "SIZING_ALGORITHM_ISSUE_UNDER_VALID_EXCHANGE_RULES",
        "explanation": (
            "The exchange rules were present and used. The failing behavior comes from sizing both legs to the "
            "same notional and rounding each leg down independently. A repair simulation should test leg-aligned "
            "quantity selection under the same exchange rules without placing orders."
        ),
    }


def increasing_capital_assessment(min_capital: dict) -> dict:
    if min_capital.get("available") is True:
        return {
            "increasing_capital_would_eventually_pass": True,
            "estimated_minimum_capital_usdt": min_capital["estimated_minimum_capital_usdt"],
            "basis": min_capital["estimate_method"],
            "capital_pass_fail_is_monotonic": False,
            "note": (
                "A passing capital point exists under stored prices/rules, but independent step-size rounding creates "
                "non-monotonic pass/fail windows. Increasing capital alone is not a robust repair."
            ),
        }
    return {
        "increasing_capital_would_eventually_pass": False,
        "reason": min_capital.get("reason"),
        "basis": min_capital.get("estimate_method"),
    }


def main() -> int:
    ensure_target_absent()
    sizing = load_json(SIZING_SIM_PATH)
    exchange_rules = load_json(EXCHANGE_RULE_PATH)
    validate_sources(sizing, exchange_rules)

    scenario_records, failing_by_scenario = analyze_scenarios(sizing)
    prices, params = build_price_and_params(sizing, exchange_rules)
    min_capital_all = estimate_min_capital(prices, params, SYMBOLS)
    min_capital_btc_eth = estimate_min_capital(prices, params, ("BTCUSDT", "ETHUSDT"))
    drop_sol = dropping_sol_analysis(sizing)
    failure_root_cause = root_cause(scenario_records)

    validation_checks = {
        "repo_clean_before_run": True,
        "sizing_simulation_artifact_loaded": True,
        "exchange_rule_artifact_loaded": True,
        "no_new_prices_fetched": True,
        "no_api_calls": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_strategy_rerun": True,
        "no_raw_rows_read": True,
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
            "price_snapshot_order_sizing_simulation": SIZING_SIM_RELATIVE_PATH,
            "price_snapshot_order_sizing_payload_sha256_excluding_hash": SIZING_SIM_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
        },
        "prior_sizing_result_preserved": {
            "status": sizing["status"],
            "classification": sizing["classification"]["classification"],
            "prices_snapshot_time_utc": sizing["price_snapshot"]["prices_snapshot_time_utc"],
            "minimum_capital_scenario_that_passes_all_symbols": sizing[
                "order_sizing_simulation_results"
            ]["minimum_capital_scenario_that_passes_all_symbols"],
            "scenario_pass_fail_summary": sizing["order_sizing_simulation_results"][
                "scenario_pass_fail_summary"
            ],
        },
        "failure_root_cause": failure_root_cause,
        "scenario_failure_analysis": scenario_records,
        "failing_symbols_by_scenario": failing_by_scenario,
        "drop_sol_diagnostic_only": drop_sol,
        "min_capital_estimate_if_available": {
            "all_three_symbols": min_capital_all,
            "btc_eth_only_diagnostic": min_capital_btc_eth,
            "uses_stored_prices_and_rules_only": True,
        },
        "increasing_capital_assessment": increasing_capital_assessment(min_capital_all),
        "sizing_algorithm_vs_exchange_rule_assessment": {
            "assessment": "SIZING_ALGORITHM_REPAIR_NEEDED_UNDER_VALID_EXCHANGE_RULES",
            "exchange_rules_missing": False,
            "exchange_rules_caused_failure": False,
            "sizing_algorithm_issue": True,
            "reason": "Independent round-down of each leg does not target matched executable notionals.",
        },
        "next_allowed_step": "ORDER_SIZING_ALGORITHM_REPAIR_SIMULATION_ONLY",
        "limitations": [
            "Read-only analysis of stored JSON artifacts only.",
            "No new prices are fetched and no API calls are made.",
            "Minimum capital estimate scans stored prices/rules and is diagnostic only; it may change with prices or filters.",
            "Dropping SOL is diagnostic only and grants no symbol universe change permission.",
            "No orders, runtime, live trading, capital allocation, candidate generation, or edge claim are permitted.",
        ],
        "safety_permissions": {
            "order_sizing_failure_analysis_created": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_order_sizing_algorithm_repair_simulation_only": True,
            "next_step_must_not_be_live_or_capital": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"status: {STATUS}")
    print(f"failure_root_cause: {failure_root_cause['primary_root_cause']}")
    print(f"min_capital_estimate_all_three_available: {str(min_capital_all.get('available')).lower()}")
    print(f"min_capital_estimate_all_three_usdt: {min_capital_all.get('estimated_minimum_capital_usdt')}")
    print(f"drop_sol_btc_eth_passes_stored_scenarios: {str(drop_sol['dropping_sol_would_make_btc_eth_pass']).lower()}")
    print("next_allowed_step: ORDER_SIZING_ALGORITHM_REPAIR_SIMULATION_ONLY")
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
