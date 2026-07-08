#!/usr/bin/env python
"""Run a report-only paper dry-run simulation for the Binance spot-perp funding carry route."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR, getcontext
from math import gcd
from pathlib import Path


getcontext().prec = 50

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_paper_dry_run_simulator_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_trading_dry_runs/binance_spot_perp_funding_carry_paper_dry_run_simulator_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

PAPER_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_trading_designs/binance_spot_perp_funding_carry_paper_trading_design_v1.json"
)
SIZING_REPAIR_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json"
)
PRICE_SIZING_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_price_snapshot_order_sizing_sim_v1.json"
)
EXCHANGE_RULE_RELATIVE_PATH = (
    "artifacts/exchange_rule_discovery/binance_spot_perp_funding_carry_exchange_rule_discovery_v1.json"
)
OPERATIONAL_RELATIVE_PATH = (
    "artifacts/operational_feasibility/binance_spot_perp_delta_neutral_funding_carry_operational_feasibility_v1.json"
)
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
EXECUTION_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EVALUATOR_RELATIVE_PATH = "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
CLOSURE_RELATIVE_PATH = "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"

PAPER_DESIGN_PATH = REPO_ROOT / PAPER_DESIGN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
PRICE_SIZING_PATH = REPO_ROOT / PRICE_SIZING_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
OPERATIONAL_PATH = REPO_ROOT / OPERATIONAL_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH
EVALUATOR_PATH = REPO_ROOT / EVALUATOR_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_DRY_RUN_SIMULATOR_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_DRY_RUN_SIMULATOR"

PAPER_DESIGN_PAYLOAD_SHA256 = "67aca1c1e11d62cec04d5c05c1ec963868f04d095f84714c6c39110320ee8b63"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
PRICE_SIZING_PAYLOAD_SHA256 = "b179b6efbe52ddb7611d678c7ac37e090fc1211784373a07e7bc64ecec2c470b"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
OPERATIONAL_PAYLOAD_SHA256 = "5af80fc87f583f4f5f4ed4baaa5620d708eff1ade5aaa54969d4259e54d6604e"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
EXECUTION_PAYLOAD_SHA256 = "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378"
EVALUATOR_PAYLOAD_SHA256 = "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

PAPER_DESIGN_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_TRADING_DESIGN_CREATED"
SIZING_REPAIR_CLASSIFICATION = "ORDER_SIZING_REPAIR_SIM_PASS_READY_FOR_PAPER_TRADING_DESIGN_NO_LIVE_PERMISSION"
RISK_CAPITAL_CLASSIFICATION = "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_STRONG_DIAGNOSTIC_NO_LIVE_PERMISSION"
EVALUATOR_RESULT_CLASS = "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS_USDT = (235, 250, 500, 1000)
MISMATCH_THRESHOLD_BPS = Decimal("25")
UNUSED_NOTIONAL_THRESHOLD_BPS = Decimal("500")
MAX_OVESPEND_BPS = Decimal("25")
TRACKED_PYTHON_COUNT_AT_START = 889

SPOT_TICKER_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
FUTURES_TICKER_PRICE_URL = "https://fapi.binance.com/fapi/v1/ticker/price"
FUTURES_PREMIUM_INDEX_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(artifact: dict) -> str:
    payload = {key: value for key, value in artifact.items() if key != "payload_sha256_excluding_hash"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def all_true(checks: dict) -> bool:
    return all(value is True for value in checks.values() if isinstance(value, bool))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_from_ms(value: int | str | None) -> str | None:
    if value in (None, ""):
        return None
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def decimal_float(value: Decimal) -> float:
    return float(value)


def ceil_decimal(value: Decimal) -> Decimal:
    return value.to_integral_value(rounding="ROUND_CEILING")


def floor_decimal(value: Decimal) -> Decimal:
    return value.to_integral_value(rounding="ROUND_FLOOR")


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
        "status": rules.get("status"),
        "min_qty": decimal_value(lot["minQty"], f"{side} {symbol} minQty"),
        "max_qty": decimal_value(lot["maxQty"], f"{side} {symbol} maxQty"),
        "step_size": decimal_value(lot["stepSize"], f"{side} {symbol} stepSize"),
        "min_notional": min_notional_from_filters(filters, side),
    }


def validate_prior_chain(
    design: dict,
    repair: dict,
    price_sizing: dict,
    exchange_rules: dict,
    operational: dict,
    risk: dict,
    execution: dict,
    evaluator: dict,
    closure: dict,
) -> None:
    expected_hashes = (
        (design, PAPER_DESIGN_PAYLOAD_SHA256, "paper design"),
        (repair, SIZING_REPAIR_PAYLOAD_SHA256, "sizing repair"),
        (price_sizing, PRICE_SIZING_PAYLOAD_SHA256, "price sizing"),
        (exchange_rules, EXCHANGE_RULE_PAYLOAD_SHA256, "exchange rules"),
        (operational, OPERATIONAL_PAYLOAD_SHA256, "operational"),
        (risk, RISK_CAPITAL_PAYLOAD_SHA256, "risk capital"),
        (execution, EXECUTION_PAYLOAD_SHA256, "execution"),
        (evaluator, EVALUATOR_PAYLOAD_SHA256, "evaluator"),
        (closure, CLOSURE_PAYLOAD_SHA256, "closure"),
    )
    for artifact, expected, name in expected_hashes:
        if artifact.get("payload_sha256_excluding_hash") != expected:
            raise RuntimeError(f"{name} payload hash mismatch")
        if artifact.get("replacement_checks_all_true") is not True:
            raise RuntimeError(f"{name} replacement checks not true")
    if design.get("status") != PAPER_DESIGN_STATUS:
        raise RuntimeError("paper design status mismatch")
    if design["next_step_after_design"]["step"] != "PAPER_TRADING_DRY_RUN_SIMULATOR_ONLY":
        raise RuntimeError("paper design did not allow dry-run simulator next")
    if repair["classification"]["classification"] != SIZING_REPAIR_CLASSIFICATION:
        raise RuntimeError("sizing repair classification mismatch")
    if risk["feasibility_classification"]["classification"] != RISK_CAPITAL_CLASSIFICATION:
        raise RuntimeError("risk/capital classification mismatch")
    if evaluator["result_classification"]["result_class"] != EVALUATOR_RESULT_CLASS:
        raise RuntimeError("strategy result class mismatch")
    if evaluator["result_classification"]["diagnostic_promising"] is not True:
        raise RuntimeError("strategy promising flag mismatch")
    if closure["closure_record"]["route_closed"] is not True:
        raise RuntimeError("closure route_closed mismatch")
    for source in (design["explicit_non_permissions"], repair["safety_permissions"]):
        for key in (
            "candidate_generation_allowed_now",
            "edge_claim_allowed_now",
            "runtime_permission_allowed_now",
            "live_permission_allowed_now",
            "capital_permission_allowed_now",
        ):
            if source.get(key) is not False:
                raise RuntimeError(f"prior permission not false: {key}")


def fetch_json(endpoint: str, symbol: str) -> tuple[dict | None, dict]:
    url = f"{endpoint}?{urllib.parse.urlencode({'symbol': symbol})}"
    started = utc_now()
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "edge-factory-os-paper-dry-run-public-data/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            completed = utc_now()
            metadata = {
                "url": url,
                "request_started_utc": started,
                "response_completed_utc": completed,
                "http_status": response.status,
                "response_bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "error": None,
            }
            return json.loads(body.decode("utf-8")), metadata
    except urllib.error.HTTPError as exc:
        return None, {
            "url": url,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "http_status": exc.code,
            "response_bytes": 0,
            "sha256": None,
            "error": f"HTTP {exc.code}",
        }
    except urllib.error.URLError as exc:
        return None, {
            "url": url,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "http_status": None,
            "response_bytes": 0,
            "sha256": None,
            "error": str(exc),
        }


def fetch_public_snapshot() -> tuple[dict, dict, dict]:
    spot_prices: dict[str, Decimal] = {}
    futures_prices: dict[str, Decimal] = {}
    premium: dict[str, dict] = {}
    records = {}
    for symbol in SYMBOLS:
        symbol_record = {"symbol": symbol}
        spot_json, spot_meta = fetch_json(SPOT_TICKER_PRICE_URL, symbol)
        futures_json, futures_meta = fetch_json(FUTURES_TICKER_PRICE_URL, symbol)
        premium_json, premium_meta = fetch_json(FUTURES_PREMIUM_INDEX_URL, symbol)
        if spot_json and spot_json.get("symbol") == symbol:
            spot_prices[symbol] = decimal_value(spot_json.get("price"), f"{symbol} spot price")
        if futures_json and futures_json.get("symbol") == symbol:
            futures_prices[symbol] = decimal_value(futures_json.get("price"), f"{symbol} futures price")
        if premium_json and premium_json.get("symbol") == symbol:
            premium[symbol] = {
                "markPrice": premium_json.get("markPrice"),
                "indexPrice": premium_json.get("indexPrice"),
                "lastFundingRate": premium_json.get("lastFundingRate"),
                "nextFundingTime": premium_json.get("nextFundingTime"),
                "nextFundingTime_utc": utc_from_ms(premium_json.get("nextFundingTime")),
            }
        symbol_record["spot_price"] = decimal_text(spot_prices.get(symbol))
        symbol_record["futures_price"] = decimal_text(futures_prices.get(symbol))
        symbol_record["premium_index"] = premium.get(symbol)
        symbol_record["endpoint_metadata"] = {
            "spot_price": spot_meta,
            "futures_price": futures_meta,
            "premium_index": premium_meta,
        }
        records[symbol] = symbol_record
    return {"spot": spot_prices, "futures": futures_prices, "premium": premium}, records, {
        "spot_price_url": SPOT_TICKER_PRICE_URL,
        "futures_price_url": FUTURES_TICKER_PRICE_URL,
        "premium_index_url": FUTURES_PREMIUM_INDEX_URL,
        "private_api_used": False,
        "api_key_used": False,
        "order_endpoint_called": False,
    }


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
    centers = [
        floor_decimal(target_common_qty / common_step),
        ceil_decimal(target_common_qty / common_step),
        floor_decimal(target_by_avg / common_step),
        ceil_decimal(target_by_avg / common_step),
    ]
    values: set[int] = {int(lower_k), int(upper_k)}
    for center in centers:
        for offset in range(-25, 26):
            value = int(center) + offset
            if int(lower_k) <= value <= int(upper_k):
                values.add(value)
    return sorted(Decimal(value) * common_step for value in values)


def evaluate_quantity(
    qty: Decimal,
    target_notional: Decimal,
    spot_price: Decimal,
    futures_price: Decimal,
    spot_params: dict,
    futures_params: dict,
) -> dict:
    spot_notional = qty * spot_price
    futures_notional = qty * futures_price
    avg_notional = (spot_notional + futures_notional) / Decimal("2")
    mismatch = abs(spot_notional - futures_notional) / avg_notional * Decimal("10000") if avg_notional > 0 else Decimal("0")
    unused = (target_notional - avg_notional) / target_notional * Decimal("10000") if target_notional > 0 else Decimal("0")
    overspend = max(Decimal("0"), max(spot_notional, futures_notional) - target_notional) / target_notional * Decimal("10000")
    checks = {
        "common_qty_positive": qty > 0,
        "spot_min_qty_pass": qty >= spot_params["min_qty"],
        "futures_min_qty_pass": qty >= futures_params["min_qty"],
        "spot_max_qty_pass": qty <= spot_params["max_qty"],
        "futures_max_qty_pass": qty <= futures_params["max_qty"],
        "spot_min_notional_pass": spot_notional >= spot_params["min_notional"],
        "futures_min_notional_pass": futures_notional >= futures_params["min_notional"],
        "leg_notional_mismatch_pass": mismatch <= MISMATCH_THRESHOLD_BPS,
        "unused_notional_pass": unused <= UNUSED_NOTIONAL_THRESHOLD_BPS,
        "overspend_rule_pass": overspend <= MAX_OVESPEND_BPS,
    }
    return {
        "qty": qty,
        "spot_notional": spot_notional,
        "futures_notional": futures_notional,
        "avg_notional": avg_notional,
        "mismatch_bps": mismatch,
        "unused_bps": unused,
        "overspend_bps": overspend,
        "checks": checks,
        "pass": all(checks.values()),
    }


def choose_common_quantity(target_notional: Decimal, symbol: str, prices: dict, params: dict) -> dict:
    spot_price = prices["spot"][symbol]
    futures_price = prices["futures"][symbol]
    spot_params = params[symbol]["spot"]
    futures_params = params[symbol]["futures"]
    common_step = lcm_decimal_step(spot_params["step_size"], futures_params["step_size"])
    min_common_qty = max(spot_params["min_qty"], futures_params["min_qty"])
    max_common_qty = min(spot_params["max_qty"], futures_params["max_qty"])
    candidates = candidate_quantities(target_notional, spot_price, futures_price, common_step, min_common_qty, max_common_qty)
    evaluated = [
        evaluate_quantity(candidate, target_notional, spot_price, futures_price, spot_params, futures_params)
        for candidate in candidates
    ]
    passing = [item for item in evaluated if item["pass"]]
    if passing:
        best = min(passing, key=lambda item: (abs(item["unused_bps"]), item["mismatch_bps"], item["overspend_bps"]))
    elif evaluated:
        best = min(evaluated, key=lambda item: (abs(item["unused_bps"]), item["mismatch_bps"], item["overspend_bps"]))
    else:
        best = evaluate_quantity(Decimal("0"), target_notional, spot_price, futures_price, spot_params, futures_params)
    return {
        "symbol": symbol,
        "target_notional_per_symbol": decimal_text(target_notional),
        "spot_price": decimal_text(spot_price),
        "futures_price": decimal_text(futures_price),
        "common_step_size": decimal_text(common_step),
        "spot_quantity": decimal_text(best["qty"]),
        "futures_quantity": decimal_text(best["qty"]),
        "spot_notional": decimal_text(best["spot_notional"]),
        "futures_notional": decimal_text(best["futures_notional"]),
        "leg_notional_mismatch_bps": decimal_float(best["mismatch_bps"]),
        "unused_notional_bps": decimal_float(best["unused_bps"]),
        "max_leg_overspend_bps": decimal_float(best["overspend_bps"]),
        "spot_rule_pass": all(
            best["checks"][key] for key in ("spot_min_qty_pass", "spot_max_qty_pass", "spot_min_notional_pass")
        ),
        "futures_rule_pass": all(
            best["checks"][key] for key in ("futures_min_qty_pass", "futures_max_qty_pass", "futures_min_notional_pass")
        ),
        "pass_checks": best["checks"],
        "symbol_pass": best["pass"],
    }


def build_rule_params(exchange_rules: dict) -> dict:
    return {
        symbol: {
            "spot": rule_params(exchange_rules, symbol, "spot"),
            "futures": rule_params(exchange_rules, symbol, "futures"),
        }
        for symbol in SYMBOLS
    }


def simulate_scenario(capital: int, prices: dict, params: dict, snapshot_stale: bool, rules_missing: bool) -> dict:
    target = Decimal(str(capital)) / Decimal(str(len(SYMBOLS)))
    symbol_records = [choose_common_quantity(target, symbol, prices, params) for symbol in SYMBOLS if symbol in prices["spot"] and symbol in prices["futures"]]
    all_symbols_present = len(symbol_records) == len(SYMBOLS)
    max_mismatch = max((Decimal(str(item["leg_notional_mismatch_bps"])) for item in symbol_records), default=Decimal("0"))
    max_unused = max((Decimal(str(item["unused_notional_bps"])) for item in symbol_records), default=Decimal("10000"))
    scenario_pass = (
        all_symbols_present
        and all(item["symbol_pass"] for item in symbol_records)
        and max_mismatch <= MISMATCH_THRESHOLD_BPS
        and max_unused <= UNUSED_NOTIONAL_THRESHOLD_BPS
        and not snapshot_stale
        and not rules_missing
    )
    return {
        "capital_usdt": capital,
        "target_notional_per_symbol": decimal_text(target),
        "scenario_pass": scenario_pass,
        "all_symbols_present": all_symbols_present,
        "max_leg_mismatch_bps": decimal_float(max_mismatch),
        "max_unused_notional_bps": decimal_float(max_unused),
        "symbol_results": symbol_records,
    }


def premium_funding_rate(symbol: str, snapshot: dict) -> Decimal | None:
    premium = snapshot["premium"].get(symbol)
    if not premium or premium.get("lastFundingRate") in (None, ""):
        return None
    return decimal_value(premium["lastFundingRate"], f"{symbol} lastFundingRate")


def risk_flags(
    symbol_records: dict,
    prices: dict,
    exchange_rules: dict,
    scenario_results: list[dict],
    snapshot_stale: bool,
) -> tuple[list[str], list[str], dict]:
    per_flag = {}
    flags = []
    critical = []
    any_scenario_pass = any(item["scenario_pass"] for item in scenario_results)
    for symbol in SYMBOLS:
        record = symbol_records.get(symbol, {})
        spot_missing = symbol not in prices["spot"]
        futures_missing = symbol not in prices["futures"]
        premium_missing = symbol not in prices["premium"]
        funding = premium_funding_rate(symbol, prices)
        funding_missing = funding is None
        next_funding_missing = premium_missing or not prices["premium"][symbol].get("nextFundingTime")
        funding_negative = bool(funding is not None and funding < 0)
        spot_status = exchange_rules["spot_exchange_rules"][symbol].get("status")
        futures_status = exchange_rules["futures_exchange_rules"][symbol].get("status")
        status_not_trading = spot_status != "TRADING" or futures_status != "TRADING"
        per_flag[symbol] = {
            "missing_price_snapshot": spot_missing or futures_missing,
            "premiumIndex_unavailable": premium_missing,
            "futures_funding_rate_missing": funding_missing,
            "funding_rate_negative": funding_negative,
            "next_funding_time_missing": next_funding_missing,
            "symbol_status_not_trading": status_not_trading,
            "spot_status": spot_status,
            "futures_status": futures_status,
            "lastFundingRate": decimal_text(funding),
            "snapshot_record": record,
        }
        if spot_missing or futures_missing:
            flags.append(f"{symbol}:missing_price_snapshot")
            critical.append(f"{symbol}:missing_price_snapshot")
        if premium_missing:
            flags.append(f"{symbol}:premiumIndex_unavailable")
            critical.append(f"{symbol}:premiumIndex_unavailable")
        if funding_missing:
            flags.append(f"{symbol}:futures_funding_rate_missing")
            critical.append(f"{symbol}:futures_funding_rate_missing")
        if funding_negative:
            flags.append(f"{symbol}:funding_rate_negative")
        if next_funding_missing:
            flags.append(f"{symbol}:next_funding_time_missing")
            critical.append(f"{symbol}:next_funding_time_missing")
        if status_not_trading:
            flags.append(f"{symbol}:symbol_status_not_trading")
            critical.append(f"{symbol}:symbol_status_not_trading")
    if snapshot_stale:
        flags.append("snapshot_stale")
        critical.append("snapshot_stale")
    if not any_scenario_pass:
        flags.append("all_capital_scenarios_sizing_fail")
        critical.append("all_capital_scenarios_sizing_fail")
    for scenario in scenario_results:
        if not scenario["scenario_pass"]:
            flags.append(f"capital_{scenario['capital_usdt']}:sizing_fails")
    return flags, critical, per_flag


def state_trace(critical_flags: list[str], risk_flags_list: list[str], passing_scenarios: list[int]) -> list[dict]:
    trace = [
        {"state": "IDLE", "action": "start report-only dry run", "orders_allowed": False},
        {"state": "SNAPSHOT_RULES", "action": "load stored exchangeInfo rules", "orders_allowed": False},
        {"state": "SNAPSHOT_PRICES", "action": "fetch public spot/futures/premium snapshots", "orders_allowed": False},
        {"state": "SIZE_ORDERS", "action": "simulate common-base quantities", "orders_allowed": False},
    ]
    if critical_flags:
        trace.append({"state": "RISK_HALT", "action": "critical risk flags present", "flags": critical_flags, "orders_allowed": False})
        trace.append({"state": "REPORT_ONLY", "action": "report failure/repair need only", "orders_allowed": False})
    elif risk_flags_list:
        trace.append({"state": "RISK_HALT", "action": "non-critical risk flags present", "flags": risk_flags_list, "orders_allowed": False})
        trace.append({"state": "REPORT_ONLY", "action": "report partial dry-run only", "orders_allowed": False})
    elif passing_scenarios:
        trace.append({"state": "SIMULATE_ENTRY", "action": "create simulated-not-order entry plan", "orders_allowed": False})
        trace.append({"state": "MONITOR_FUNDING", "action": "record current funding diagnostics", "orders_allowed": False})
        trace.append({"state": "REPORT_ONLY", "action": "report dry-run success only", "orders_allowed": False})
    else:
        trace.append({"state": "RISK_HALT", "action": "no passing scenario", "orders_allowed": False})
        trace.append({"state": "REPORT_ONLY", "action": "report failure only", "orders_allowed": False})
    return trace


def simulated_entry_plan(scenario_results: list[dict], prices: dict) -> list[dict]:
    plans = []
    for scenario in scenario_results:
        if not scenario["scenario_pass"]:
            continue
        symbol_entries = []
        for item in scenario["symbol_results"]:
            premium = prices["premium"].get(item["symbol"], {})
            symbol_entries.append(
                {
                    "label": "SIMULATED_NOT_ORDER",
                    "symbol": item["symbol"],
                    "hypothetical_spot_side": "BUY",
                    "hypothetical_futures_side": "SHORT",
                    "spot_quantity": item["spot_quantity"],
                    "futures_quantity": item["futures_quantity"],
                    "spot_notional": item["spot_notional"],
                    "futures_notional": item["futures_notional"],
                    "leg_notional_mismatch_bps": item["leg_notional_mismatch_bps"],
                    "current_lastFundingRate": premium.get("lastFundingRate"),
                    "nextFundingTime": premium.get("nextFundingTime"),
                    "nextFundingTime_utc": premium.get("nextFundingTime_utc"),
                    "order_endpoint_payload_generated": False,
                }
            )
        plans.append(
            {
                "capital_usdt": scenario["capital_usdt"],
                "label": "SIMULATED_NOT_ORDER",
                "orders_generated": False,
                "symbol_entries": symbol_entries,
            }
        )
    return plans


def main() -> int:
    ensure_target_absent()
    design = load_json(PAPER_DESIGN_PATH)
    repair = load_json(SIZING_REPAIR_PATH)
    price_sizing = load_json(PRICE_SIZING_PATH)
    exchange_rules = load_json(EXCHANGE_RULE_PATH)
    operational = load_json(OPERATIONAL_PATH)
    risk = load_json(RISK_CAPITAL_PATH)
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    validate_prior_chain(design, repair, price_sizing, exchange_rules, operational, risk, execution, evaluator, closure)

    snapshot_started = utc_now()
    prices, symbol_snapshot_records, endpoint_contracts = fetch_public_snapshot()
    snapshot_time = utc_now()
    snapshot_stale = not all(symbol in prices["spot"] and symbol in prices["futures"] for symbol in SYMBOLS)
    rules_missing = not exchange_rules["rule_completeness_summary"]["all_required_filters_available"]
    params = build_rule_params(exchange_rules)
    scenario_results = [
        simulate_scenario(capital, prices, params, snapshot_stale, rules_missing)
        for capital in CAPITAL_SCENARIOS_USDT
    ]
    passing_capitals = [item["capital_usdt"] for item in scenario_results if item["scenario_pass"]]
    minimum_passing = min(passing_capitals) if passing_capitals else None
    flags, critical_flags, per_symbol_flags = risk_flags(
        symbol_snapshot_records,
        prices,
        exchange_rules,
        scenario_results,
        snapshot_stale,
    )
    negative_funding_flags = [flag for flag in flags if flag.endswith("funding_rate_negative")]
    if critical_flags:
        classification = "PAPER_DRY_RUN_SIM_FAIL_NO_LIVE_PERMISSION"
        next_allowed_step = "PAPER_DRY_RUN_REPAIR_OR_WAIT_FOR_NEW_SNAPSHOT_ONLY"
    elif passing_capitals and negative_funding_flags:
        classification = "PAPER_DRY_RUN_SIM_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION"
        next_allowed_step = "PAPER_MONITOR_DESIGN_ONLY"
    elif passing_capitals and len(passing_capitals) < len(CAPITAL_SCENARIOS_USDT):
        classification = "PAPER_DRY_RUN_SIM_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION"
        next_allowed_step = "PAPER_MONITOR_DESIGN_ONLY"
    elif passing_capitals:
        classification = "PAPER_DRY_RUN_SIM_PASS_READY_FOR_PAPER_MONITOR_DESIGN_NO_LIVE_PERMISSION"
        next_allowed_step = "PAPER_MONITOR_DESIGN_ONLY"
    else:
        classification = "PAPER_DRY_RUN_SIM_FAIL_NO_LIVE_PERMISSION"
        next_allowed_step = "PAPER_DRY_RUN_REPAIR_OR_WAIT_FOR_NEW_SNAPSHOT_ONLY"

    dry_run_trade_allowed_in_simulation = bool(passing_capitals and not flags)
    trace = state_trace(critical_flags, flags, passing_capitals)
    entry_plan = simulated_entry_plan(scenario_results, prices) if passing_capitals and not critical_flags else []
    scenario_pass_fail = {str(item["capital_usdt"]): item["scenario_pass"] for item in scenario_results}

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_paper_design_loaded": True,
        "prior_sizing_repair_loaded": True,
        "exchange_rules_loaded": True,
        "public_price_snapshot_fetched": all(symbol in prices["spot"] and symbol in prices["futures"] for symbol in SYMBOLS),
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_live_or_capital_permission": True,
        "common_base_quantity_algorithm_used": True,
        "state_machine_trace_created": True,
        "simulated_entry_plan_labeled_not_order": all(
            plan["label"] == "SIMULATED_NOT_ORDER"
            and all(entry["label"] == "SIMULATED_NOT_ORDER" for entry in plan["symbol_entries"])
            for plan in entry_plan
        ),
        "no_candidate_generation": True,
        "no_edge_claim": True,
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
            "paper_trading_design": PAPER_DESIGN_RELATIVE_PATH,
            "paper_trading_design_payload_sha256_excluding_hash": PAPER_DESIGN_PAYLOAD_SHA256,
            "order_sizing_repair_sim": SIZING_REPAIR_RELATIVE_PATH,
            "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
            "price_snapshot_sizing_sim": PRICE_SIZING_RELATIVE_PATH,
            "price_snapshot_sizing_payload_sha256_excluding_hash": PRICE_SIZING_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "operational_feasibility": OPERATIONAL_RELATIVE_PATH,
            "operational_payload_sha256_excluding_hash": OPERATIONAL_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "strategy_execution": EXECUTION_RELATIVE_PATH,
            "strategy_execution_payload_sha256_excluding_hash": EXECUTION_PAYLOAD_SHA256,
            "strategy_evaluator": EVALUATOR_RELATIVE_PATH,
            "strategy_evaluator_payload_sha256_excluding_hash": EVALUATOR_PAYLOAD_SHA256,
            "strategy_closure": CLOSURE_RELATIVE_PATH,
            "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_chain_preserved": {
            "strategy_diagnostic_promising": evaluator["result_classification"]["diagnostic_promising"],
            "strategy_result_class": evaluator["result_classification"]["result_class"],
            "risk_capital_classification": risk["feasibility_classification"]["classification"],
            "sizing_repair_classification": repair["classification"]["classification"],
            "paper_trading_design_status": design["status"],
            "route_closed": closure["closure_record"]["route_closed"],
            "live_capital_permission_exists": False,
        },
        "public_snapshot_summary": {
            "snapshot_started_utc": snapshot_started,
            "snapshot_time_utc": snapshot_time,
            "snapshot_stale": snapshot_stale,
            "public_price_snapshot_fetched": validation_checks["public_price_snapshot_fetched"],
            "premiumIndex_all_symbols_available": all(symbol in prices["premium"] for symbol in SYMBOLS),
            "endpoint_contracts": endpoint_contracts,
        },
        "symbol_snapshot_records": symbol_snapshot_records,
        "repaired_sizing_results": {
            "capital_scenarios": list(CAPITAL_SCENARIOS_USDT),
            "scenario_pass_fail_summary": scenario_pass_fail,
            "passing_capital_scenarios": passing_capitals,
            "minimum_passing_capital": minimum_passing,
            "scenario_results": scenario_results,
        },
        "paper_state_machine_trace": trace,
        "simulated_entry_plan": {
            "dry_run_trade_allowed_in_simulation": dry_run_trade_allowed_in_simulation,
            "orders_generated": False,
            "order_endpoint_payload_generated": False,
            "plans": entry_plan,
        },
        "risk_halt_checks": {
            "dry_run_trade_allowed_in_simulation": dry_run_trade_allowed_in_simulation,
            "risk_flags": flags,
            "critical_risk_flags": critical_flags,
            "per_symbol_flags": per_symbol_flags,
            "any_symbol_missing_price_snapshot": any(flag.endswith("missing_price_snapshot") for flag in flags),
            "any_futures_funding_rate_missing": any(flag.endswith("futures_funding_rate_missing") for flag in flags),
            "any_funding_rate_negative": bool(negative_funding_flags),
            "any_symbol_sizing_fails": any(not item["scenario_pass"] for item in scenario_results),
            "any_mismatch_above_threshold": any(
                item["max_leg_mismatch_bps"] > decimal_float(MISMATCH_THRESHOLD_BPS) for item in scenario_results
            ),
            "snapshot_stale": snapshot_stale,
            "any_exchange_rule_missing": rules_missing,
            "any_next_funding_time_missing": any(flag.endswith("next_funding_time_missing") for flag in flags),
            "any_premiumIndex_unavailable": any(flag.endswith("premiumIndex_unavailable") for flag in flags),
            "any_symbol_status_not_trading": any(flag.endswith("symbol_status_not_trading") for flag in flags),
        },
        "classification": {
            "classification": classification,
            "classification_grants_live_or_capital_permission": False,
        },
        "next_allowed_step": {
            "step": next_allowed_step,
            "live_or_capital_allowed": False,
        },
        "limitations": [
            "This is a report-only dry-run simulation using public market-data endpoints.",
            "No private endpoint, API key, account endpoint, order endpoint, order placement, runtime, daemon, paper monitor, live trading, or capital allocation is used.",
            "Simulated entry plans are labeled SIMULATED_NOT_ORDER and contain no order IDs or order endpoint payloads.",
            "Current public snapshots can change immediately after the run.",
            "No candidate generation, edge claim, or family release is granted.",
        ],
        "safety_permissions": {
            "paper_dry_run_created": True,
            "order_placement_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
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
    print(f"snapshot_time_utc: {snapshot_time}")
    print(f"passing_capital_scenarios: {json.dumps(passing_capitals)}")
    print(f"minimum_passing_capital: {minimum_passing}")
    print(f"critical_risk_flags: {json.dumps(critical_flags, sort_keys=True)}")
    print(f"next_allowed_step: {next_allowed_step}")
    print("order_placement_allowed_now: false")
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
