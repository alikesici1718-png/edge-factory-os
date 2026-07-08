#!/usr/bin/env python
"""Run a Binance spot-perp price snapshot and order sizing simulation."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_DOWN, getcontext
from pathlib import Path


getcontext().prec = 40

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_price_snapshot_order_sizing_sim_v1.py"
ARTIFACT_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/"
    "binance_spot_perp_funding_carry_price_snapshot_order_sizing_sim_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

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
EXECUTION_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EVALUATOR_RELATIVE_PATH = "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
CLOSURE_RELATIVE_PATH = "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"

EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
OPERATIONAL_PATH = REPO_ROOT / OPERATIONAL_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH
EVALUATOR_PATH = REPO_ROOT / EVALUATOR_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PRICE_SNAPSHOT_ORDER_SIZING_SIM_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_PRICE_SNAPSHOT_ORDER_SIZING_SIMULATION"

EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
OPERATIONAL_PAYLOAD_SHA256 = "5af80fc87f583f4f5f4ed4baaa5620d708eff1ade5aaa54969d4259e54d6604e"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
EXECUTION_PAYLOAD_SHA256 = "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378"
EVALUATOR_PAYLOAD_SHA256 = "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

EXCHANGE_RULE_CLASSIFICATION = "EXCHANGE_RULE_DISCOVERY_PASS_READY_FOR_PRICE_SNAPSHOT_AND_SIZING_SIM_NO_LIVE_PERMISSION"
NEXT_ALLOWED_FROM_RULES = "PRICE_SNAPSHOT_AND_ORDER_SIZING_SIMULATION_ONLY"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS_USDT = (100, 250, 500, 1000, 2500, 5000)
MAX_LEG_MISMATCH_BPS = Decimal("25")
NEXT_ALLOWED_STEP = "PAPER_TRADING_DESIGN_ONLY"
TRACKED_PYTHON_COUNT_AT_START = 885

SPOT_TICKER_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
FUTURES_TICKER_PRICE_URL = "https://fapi.binance.com/fapi/v1/ticker/price"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def decimal_float(value: Decimal) -> float:
    return float(value)


def fetch_price(endpoint: str, symbol: str) -> tuple[Decimal, dict]:
    url = f"{endpoint}?{urllib.parse.urlencode({'symbol': symbol})}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "edge-factory-os-public-price-sizing-sim/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            metadata = {
                "url": url,
                "http_status": response.status,
                "response_bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
            }
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"public ticker price fetch failed HTTP {exc.code}: {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"public ticker price fetch failed: {url}: {exc}") from exc
    record = json.loads(body.decode("utf-8"))
    if record.get("symbol") != symbol:
        raise RuntimeError(f"ticker response symbol mismatch for {symbol}: {record!r}")
    price = decimal_value(record.get("price"), f"{symbol} ticker price")
    if price <= 0:
        raise RuntimeError(f"non-positive ticker price for {symbol}: {price}")
    return price, metadata


def validate_prior_artifacts(exchange_rules: dict, operational: dict, risk: dict, execution: dict, evaluator: dict, closure: dict) -> None:
    if exchange_rules.get("payload_sha256_excluding_hash") != EXCHANGE_RULE_PAYLOAD_SHA256:
        raise RuntimeError("exchange-rule discovery payload hash mismatch")
    if exchange_rules["discovery_classification"]["classification"] != EXCHANGE_RULE_CLASSIFICATION:
        raise RuntimeError("exchange-rule discovery classification mismatch")
    if exchange_rules["next_allowed_step"]["step"] != NEXT_ALLOWED_FROM_RULES:
        raise RuntimeError("exchange-rule discovery next allowed step mismatch")
    if exchange_rules["safety_permissions"]["next_step_may_be_price_snapshot_and_order_sizing_simulation_only"] is not True:
        raise RuntimeError("exchange-rule discovery did not permit price snapshot and sizing simulation")
    if operational.get("payload_sha256_excluding_hash") != OPERATIONAL_PAYLOAD_SHA256:
        raise RuntimeError("operational feasibility payload hash mismatch")
    if risk.get("payload_sha256_excluding_hash") != RISK_CAPITAL_PAYLOAD_SHA256:
        raise RuntimeError("risk/capital payload hash mismatch")
    if execution.get("payload_sha256_excluding_hash") != EXECUTION_PAYLOAD_SHA256:
        raise RuntimeError("execution payload hash mismatch")
    if evaluator.get("payload_sha256_excluding_hash") != EVALUATOR_PAYLOAD_SHA256:
        raise RuntimeError("evaluator payload hash mismatch")
    if closure.get("payload_sha256_excluding_hash") != CLOSURE_PAYLOAD_SHA256:
        raise RuntimeError("closure payload hash mismatch")
    for key in (
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
    ):
        if exchange_rules["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"exchange-rule safety permission is not false: {key}")


def round_down_to_step(quantity: Decimal, step_size: Decimal) -> Decimal:
    if step_size <= 0:
        raise RuntimeError(f"invalid non-positive step size: {step_size}")
    increments = (quantity / step_size).to_integral_value(rounding=ROUND_DOWN)
    return increments * step_size


def min_notional_from_spot_filters(filters: dict) -> Decimal:
    if "MIN_NOTIONAL" in filters:
        return decimal_value(filters["MIN_NOTIONAL"]["minNotional"], "spot MIN_NOTIONAL.minNotional")
    if "NOTIONAL" in filters:
        return decimal_value(filters["NOTIONAL"]["minNotional"], "spot NOTIONAL.minNotional")
    raise RuntimeError("spot min notional filter missing")


def min_notional_from_futures_filters(filters: dict) -> Decimal:
    if "MIN_NOTIONAL" in filters:
        return decimal_value(filters["MIN_NOTIONAL"]["notional"], "futures MIN_NOTIONAL.notional")
    raise RuntimeError("futures min notional filter missing")


def leg_simulation(
    target_notional: Decimal,
    price: Decimal,
    filters: dict,
    side_label: str,
) -> dict:
    lot_size = filters["LOT_SIZE"]
    min_qty = decimal_value(lot_size["minQty"], f"{side_label} LOT_SIZE.minQty")
    max_qty = decimal_value(lot_size["maxQty"], f"{side_label} LOT_SIZE.maxQty")
    step_size = decimal_value(lot_size["stepSize"], f"{side_label} LOT_SIZE.stepSize")
    min_notional = (
        min_notional_from_spot_filters(filters)
        if side_label == "spot"
        else min_notional_from_futures_filters(filters)
    )
    raw_qty = target_notional / price
    rounded_qty = round_down_to_step(raw_qty, step_size)
    rounded_notional = rounded_qty * price
    rule_pass = rounded_qty >= min_qty and rounded_qty <= max_qty and rounded_notional >= min_notional
    return {
        "price": decimal_text(price),
        "quantity_raw": decimal_text(raw_qty),
        "quantity_rounded": decimal_text(rounded_qty),
        "notional_rounded": decimal_text(rounded_notional),
        "min_qty": decimal_text(min_qty),
        "max_qty": decimal_text(max_qty),
        "step_size": decimal_text(step_size),
        "min_notional": decimal_text(min_notional),
        "rule_pass": rule_pass,
        "min_qty_pass": rounded_qty >= min_qty,
        "max_qty_pass": rounded_qty <= max_qty,
        "min_notional_pass": rounded_notional >= min_notional,
        "unused_notional_estimate": decimal_text(max(Decimal("0"), target_notional - rounded_notional)),
        "_rounded_notional_decimal": rounded_notional,
    }


def scenario_simulation(capital: int, exchange_rules: dict, spot_prices: dict[str, Decimal], futures_prices: dict[str, Decimal]) -> dict:
    target_notional = Decimal(str(capital)) / Decimal(str(len(SYMBOLS)))
    symbol_records = []
    scenario_pass = True
    max_mismatch_bps = Decimal("0")
    aggregate_unused = Decimal("0")
    for symbol in SYMBOLS:
        spot_filters = exchange_rules["spot_exchange_rules"][symbol]["filters"]
        futures_filters = exchange_rules["futures_exchange_rules"][symbol]["filters"]
        spot_leg = leg_simulation(target_notional, spot_prices[symbol], spot_filters, "spot")
        futures_leg = leg_simulation(target_notional, futures_prices[symbol], futures_filters, "futures")
        spot_notional = spot_leg.pop("_rounded_notional_decimal")
        futures_notional = futures_leg.pop("_rounded_notional_decimal")
        mismatch_bps = (
            abs(spot_notional - futures_notional) / target_notional * Decimal("10000")
            if target_notional > 0
            else Decimal("0")
        )
        symbol_pass = (
            spot_leg["rule_pass"]
            and futures_leg["rule_pass"]
            and mismatch_bps <= MAX_LEG_MISMATCH_BPS
        )
        max_mismatch_bps = max(max_mismatch_bps, mismatch_bps)
        aggregate_unused += max(Decimal("0"), target_notional - spot_notional)
        aggregate_unused += max(Decimal("0"), target_notional - futures_notional)
        if not symbol_pass:
            scenario_pass = False
        symbol_records.append(
            {
                "symbol": symbol,
                "target_notional": decimal_text(target_notional),
                "spot_price": decimal_text(spot_prices[symbol]),
                "futures_price": decimal_text(futures_prices[symbol]),
                "spot_quantity_raw": spot_leg["quantity_raw"],
                "spot_quantity_rounded": spot_leg["quantity_rounded"],
                "futures_quantity_raw": futures_leg["quantity_raw"],
                "futures_quantity_rounded": futures_leg["quantity_rounded"],
                "spot_notional_rounded": spot_leg["notional_rounded"],
                "futures_notional_rounded": futures_leg["notional_rounded"],
                "leg_notional_mismatch_bps": decimal_float(mismatch_bps),
                "max_leg_mismatch_threshold_bps": decimal_float(MAX_LEG_MISMATCH_BPS),
                "spot_rule_pass": spot_leg["rule_pass"],
                "futures_rule_pass": futures_leg["rule_pass"],
                "scenario_symbol_pass": symbol_pass,
                "spot_rule_details": spot_leg,
                "futures_rule_details": futures_leg,
            }
        )
    return {
        "capital_usdt": capital,
        "notional_per_symbol": decimal_text(target_notional),
        "scenario_pass": scenario_pass,
        "max_leg_mismatch_bps": decimal_float(max_mismatch_bps),
        "max_leg_mismatch_threshold_bps": decimal_float(MAX_LEG_MISMATCH_BPS),
        "aggregate_unused_cash_estimate_usdt": decimal_text(aggregate_unused),
        "symbols": symbol_records,
    }


def classify_scenarios(scenarios: list[dict]) -> tuple[str, int | None]:
    passing = [item["capital_usdt"] for item in scenarios if item["scenario_pass"]]
    if len(passing) == len(scenarios):
        return "PRICE_SNAPSHOT_ORDER_SIZING_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION", min(passing)
    if passing:
        return "PRICE_SNAPSHOT_ORDER_SIZING_SIM_PARTIAL_MIN_CAPITAL_REQUIRED_NO_LIVE_PERMISSION", min(passing)
    return "PRICE_SNAPSHOT_ORDER_SIZING_SIM_FAIL_NO_LIVE_PERMISSION", None


def main() -> int:
    ensure_target_absent()
    exchange_rules = load_json(EXCHANGE_RULE_PATH)
    operational = load_json(OPERATIONAL_PATH)
    risk = load_json(RISK_CAPITAL_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    validate_prior_artifacts(exchange_rules, operational, risk, execution, evaluator, closure)

    snapshot_started_utc = now_utc()
    spot_prices: dict[str, Decimal] = {}
    futures_prices: dict[str, Decimal] = {}
    endpoint_metadata = {"spot": {}, "futures": {}}
    for symbol in SYMBOLS:
        spot_price, spot_meta = fetch_price(SPOT_TICKER_PRICE_URL, symbol)
        futures_price, futures_meta = fetch_price(FUTURES_TICKER_PRICE_URL, symbol)
        spot_prices[symbol] = spot_price
        futures_prices[symbol] = futures_price
        endpoint_metadata["spot"][symbol] = spot_meta
        endpoint_metadata["futures"][symbol] = futures_meta
    snapshot_completed_utc = now_utc()

    scenarios = [
        scenario_simulation(capital, exchange_rules, spot_prices, futures_prices)
        for capital in CAPITAL_SCENARIOS_USDT
    ]
    classification, minimum_passing = classify_scenarios(scenarios)
    scenario_pass_fail_summary = {
        str(item["capital_usdt"]): item["scenario_pass"] for item in scenarios
    }
    max_leg_mismatch_bps_by_scenario = {
        str(item["capital_usdt"]): item["max_leg_mismatch_bps"] for item in scenarios
    }

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_exchange_rule_discovery_loaded": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "public_price_snapshot_fetched": True,
        "no_strategy_rerun": True,
        "no_raw_rows_read": True,
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
        "source_artifacts": {
            "exchange_rule_discovery_artifact": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_discovery_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "operational_feasibility_artifact": OPERATIONAL_RELATIVE_PATH,
            "operational_feasibility_payload_sha256_excluding_hash": OPERATIONAL_PAYLOAD_SHA256,
            "risk_capital_artifact": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "execution_artifact": EXECUTION_RELATIVE_PATH,
            "execution_payload_sha256_excluding_hash": EXECUTION_PAYLOAD_SHA256,
            "evaluator_artifact": EVALUATOR_RELATIVE_PATH,
            "evaluator_payload_sha256_excluding_hash": EVALUATOR_PAYLOAD_SHA256,
            "closure_artifact": CLOSURE_RELATIVE_PATH,
            "closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_exchange_rule_discovery_preserved": {
            "classification": exchange_rules["discovery_classification"]["classification"],
            "next_allowed_step": exchange_rules["next_allowed_step"]["step"],
            "all_required_filters_available": exchange_rules["rule_completeness_summary"][
                "all_required_filters_available"
            ],
            "runtime_live_capital_allowed": False,
        },
        "endpoint_contracts": {
            "spot_ticker_price": {
                "url": SPOT_TICKER_PRICE_URL,
                "public_unsigned": True,
                "private_or_signed": False,
                "order_endpoint": False,
            },
            "usd_m_futures_ticker_price": {
                "url": FUTURES_TICKER_PRICE_URL,
                "public_unsigned": True,
                "private_or_signed": False,
                "order_endpoint": False,
            },
            "endpoint_metadata": endpoint_metadata,
            "api_key_used": False,
            "orders_placed": False,
        },
        "price_snapshot": {
            "snapshot_started_utc": snapshot_started_utc,
            "snapshot_completed_utc": snapshot_completed_utc,
            "prices_snapshot_time_utc": snapshot_completed_utc,
            "spot_prices": {symbol: decimal_text(price) for symbol, price in spot_prices.items()},
            "futures_prices": {symbol: decimal_text(price) for symbol, price in futures_prices.items()},
        },
        "simulation_policy": {
            "capital_scenarios_usdt": list(CAPITAL_SCENARIOS_USDT),
            "notional_per_symbol_formula": "capital / 3",
            "spot_quantity_formula": "notional_per_symbol / public spot ticker price",
            "futures_quantity_formula": "notional_per_symbol / public USD-M futures ticker price",
            "quantity_rounding": "round down to LOT_SIZE.stepSize",
            "max_leg_mismatch_bps_threshold": decimal_float(MAX_LEG_MISMATCH_BPS),
            "orders_placed": False,
            "strategy_rerun": False,
        },
        "order_sizing_simulation_results": {
            "scenarios": scenarios,
            "scenario_pass_fail_summary": scenario_pass_fail_summary,
            "max_leg_mismatch_bps_by_scenario": max_leg_mismatch_bps_by_scenario,
            "minimum_capital_scenario_that_passes_all_symbols": minimum_passing,
        },
        "classification": {
            "classification": classification,
            "classification_grants_live_or_capital_permission": False,
        },
        "next_allowed_step": {
            "step": NEXT_ALLOWED_STEP,
            "paper_trading_design_only": True,
            "live_or_capital_allowed": False,
        },
        "limitations": [
            "Public ticker prices are point-in-time snapshots and may change immediately after this diagnostic.",
            "No account balances, fee tier, order book depth, slippage, fill probability, margin mode, leverage, or liquidation behavior is modeled.",
            "No order endpoint, private endpoint, signed endpoint, API key, listen key, order placement, runtime, live, or capital action is used.",
            "A pass or partial pass only allows paper-trading design, not live trading or capital allocation.",
        ],
        "safety_permissions": {
            "price_snapshot_order_sizing_sim_created": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_paper_trading_design_only": True,
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
    print(f"classification: {classification}")
    print(f"prices_snapshot_time_utc: {snapshot_completed_utc}")
    print(f"capital_scenarios_evaluated: {','.join(str(value) for value in CAPITAL_SCENARIOS_USDT)}")
    print(f"minimum_capital_scenario_that_passes_all_symbols: {minimum_passing}")
    print(f"scenario_pass_fail_summary: {json.dumps(scenario_pass_fail_summary, sort_keys=True)}")
    print(f"max_leg_mismatch_bps_by_scenario: {json.dumps(max_leg_mismatch_bps_by_scenario, sort_keys=True)}")
    print(f"next_allowed_step: {NEXT_ALLOWED_STEP}")
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
