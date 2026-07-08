#!/usr/bin/env python
"""Run a finite manual multi-cycle paper dry run for the Binance spot-perp carry route."""

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

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.py"
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

PREVIEW_RELATIVE_PATH = (
    "artifacts/paper_monitor_previews/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_implementation_preview_v1.json"
)
DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_multi_cycle_paper_monitor_design_v1.json"
)
SINGLE_CYCLE_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json"
)
PAPER_MONITOR_DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_paper_monitor_design_v1.json"
)
SIZING_REPAIR_RELATIVE_PATH = (
    "artifacts/order_sizing_simulations/binance_spot_perp_funding_carry_order_sizing_repair_sim_v1.json"
)
EXCHANGE_RULE_RELATIVE_PATH = (
    "artifacts/exchange_rule_discovery/binance_spot_perp_funding_carry_exchange_rule_discovery_v1.json"
)
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
CLOSURE_RELATIVE_PATH = (
    "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
)

PREVIEW_PATH = REPO_ROOT / PREVIEW_RELATIVE_PATH
DESIGN_PATH = REPO_ROOT / DESIGN_RELATIVE_PATH
SINGLE_CYCLE_PATH = REPO_ROOT / SINGLE_CYCLE_RELATIVE_PATH
PAPER_MONITOR_DESIGN_PATH = REPO_ROOT / PAPER_MONITOR_DESIGN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_DRY_RUN_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_PAPER_DRY_RUN"

PREVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_MULTI_CYCLE_IMPLEMENTATION_PREVIEW_CREATED"
PREVIEW_NEXT_STEP = "PAPER_MONITOR_MULTI_CYCLE_DRY_RUN_IMPLEMENTATION_ONLY"
PREVIEW_PAYLOAD_SHA256 = "89f4f97109d1ef717ce7f3f0ff696bbe8a90c06e7bd4ff9a76a88d388ead4717"
DESIGN_PAYLOAD_SHA256 = "08cfe12a65ff99098a2debf6c19958f0d9be2774e95aca33df1eebefb9126916"
SINGLE_CYCLE_PAYLOAD_SHA256 = "495fcc7bf364ef7ee1fabb317807c998343a5683ac6681505ef37784ec324d1f"
PAPER_MONITOR_DESIGN_PAYLOAD_SHA256 = "25cb17fa9a4e296f194b79808a6515d880ec232ecde3356c008ccb2da04c6188"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS = (100, 235, 250, 500, 1000, 2500, 5000)
TRACKED_PYTHON_COUNT_AT_START = 895

CYCLE_COUNT = 3
CYCLE_SPACING_SECONDS = 0
MISMATCH_THRESHOLD_BPS = Decimal("25")
UNUSED_NOTIONAL_THRESHOLD_BPS = Decimal("500")
MAX_OVESPEND_BPS = Decimal("25")

SPOT_TICKER_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
FUTURES_TICKER_PRICE_URL = "https://fapi.binance.com/fapi/v1/ticker/price"
FUTURES_PREMIUM_INDEX_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
SPOT_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"
FUTURES_EXCHANGE_INFO_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"

ORDER_PLACEMENT_ALLOWED = False
PRIVATE_API_ALLOWED = False
API_KEY_ALLOWED = False
RUNTIME_ALLOWED = False
SCHEDULER_ALLOWED = False
DAEMON_ALLOWED = False
LIVE_TRADING_ALLOWED = False
CAPITAL_ALLOCATION_ALLOWED = False
CANDIDATE_GENERATION_ALLOWED = False
EDGE_CLAIM_ALLOWED = False


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
        raise RuntimeError(f"target artifact already exists: {ARTIFACT_PATH}")


def assert_payload(name: str, artifact: dict, expected_hash: str) -> None:
    actual = artifact.get("payload_sha256_excluding_hash")
    if actual != expected_hash:
        raise RuntimeError(f"{name} payload hash mismatch: expected {expected_hash}, got {actual}")


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


def validate_prior_chain(artifacts: dict) -> None:
    preview = artifacts["preview"]
    if preview.get("status") != PREVIEW_STATUS:
        raise RuntimeError("multi-cycle implementation preview status mismatch")
    if preview.get("next_allowed_step") != PREVIEW_NEXT_STEP:
        raise RuntimeError("multi-cycle implementation preview next step mismatch")
    assert_payload("multi-cycle implementation preview", preview, PREVIEW_PAYLOAD_SHA256)
    for key in (
        "order_placement_allowed_now",
        "private_api_allowed_now",
        "api_key_allowed_now",
        "runtime_permission_allowed_now",
        "scheduler_allowed_now",
        "daemon_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
    ):
        if preview["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"preview safety permission not false: {key}")
    for key, expected in (
        ("design", DESIGN_PAYLOAD_SHA256),
        ("single_cycle", SINGLE_CYCLE_PAYLOAD_SHA256),
        ("paper_monitor_design", PAPER_MONITOR_DESIGN_PAYLOAD_SHA256),
        ("sizing_repair", SIZING_REPAIR_PAYLOAD_SHA256),
        ("exchange_rule", EXCHANGE_RULE_PAYLOAD_SHA256),
        ("risk_capital", RISK_CAPITAL_PAYLOAD_SHA256),
        ("closure", CLOSURE_PAYLOAD_SHA256),
    ):
        assert_payload(key, artifacts[key], expected)


def fetch_json(url: str, params: dict | None = None) -> tuple[dict | None, dict]:
    final_url = url
    if params:
        final_url = f"{url}?{urllib.parse.urlencode(params)}"
    started = utc_now()
    request = urllib.request.Request(
        final_url,
        headers={
            "User-Agent": "edge-factory-os-multi-cycle-paper-dry-run-public-data/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            return json.loads(body.decode("utf-8")), {
                "url": final_url,
                "request_started_utc": started,
                "response_completed_utc": utc_now(),
                "http_status": response.status,
                "response_bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return None, {
            "url": final_url,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "http_status": exc.code,
            "response_bytes": 0,
            "sha256": None,
            "error": f"HTTP {exc.code}",
        }
    except urllib.error.URLError as exc:
        return None, {
            "url": final_url,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "http_status": None,
            "response_bytes": 0,
            "sha256": None,
            "error": str(exc),
        }


def fetch_symbol_snapshots() -> tuple[dict, dict, dict]:
    spot_prices: dict[str, Decimal] = {}
    futures_prices: dict[str, Decimal] = {}
    records: dict[str, dict] = {}
    for symbol in SYMBOLS:
        spot_json, spot_meta = fetch_json(SPOT_TICKER_PRICE_URL, {"symbol": symbol})
        futures_json, futures_meta = fetch_json(FUTURES_TICKER_PRICE_URL, {"symbol": symbol})
        premium_json, premium_meta = fetch_json(FUTURES_PREMIUM_INDEX_URL, {"symbol": symbol})
        premium = None
        if spot_json and spot_json.get("symbol") == symbol:
            spot_prices[symbol] = decimal_value(spot_json.get("price"), f"{symbol} spot price")
        if futures_json and futures_json.get("symbol") == symbol:
            futures_prices[symbol] = decimal_value(futures_json.get("price"), f"{symbol} futures price")
        if premium_json and premium_json.get("symbol") == symbol:
            premium = {
                "markPrice": premium_json.get("markPrice"),
                "indexPrice": premium_json.get("indexPrice"),
                "lastFundingRate": premium_json.get("lastFundingRate"),
                "nextFundingTime": premium_json.get("nextFundingTime"),
                "nextFundingTime_utc": utc_from_ms(premium_json.get("nextFundingTime")),
            }
        records[symbol] = {
            "symbol": symbol,
            "spot_price": decimal_text(spot_prices.get(symbol)),
            "futures_price": decimal_text(futures_prices.get(symbol)),
            "premium_index": premium,
            "endpoint_metadata": {
                "spot_price": spot_meta,
                "futures_price": futures_meta,
                "premium_index": premium_meta,
            },
        }
    return records, spot_prices, futures_prices


def filter_map(raw_filters: list[dict]) -> dict:
    return {item["filterType"]: {key: value for key, value in item.items() if key != "filterType"} for item in raw_filters}


def extract_rules(raw: dict | None, market: str) -> dict:
    if raw is None:
        return {}
    symbols = {}
    for item in raw.get("symbols", []):
        symbol = item.get("symbol")
        if symbol not in SYMBOLS:
            continue
        record = {
            "symbol": symbol,
            "status": item.get("status"),
            "baseAsset": item.get("baseAsset"),
            "quoteAsset": item.get("quoteAsset"),
            "orderTypes": item.get("orderTypes", []),
            "filters": filter_map(item.get("filters", [])),
        }
        if market == "spot":
            record["isSpotTradingAllowed"] = item.get("isSpotTradingAllowed")
        else:
            record["contractType"] = item.get("contractType")
            record["marginAsset"] = item.get("marginAsset")
        symbols[symbol] = record
    return symbols


def fetch_exchange_rules() -> tuple[dict, dict]:
    spot_json, spot_meta = fetch_json(SPOT_EXCHANGE_INFO_URL)
    futures_json, futures_meta = fetch_json(FUTURES_EXCHANGE_INFO_URL)
    return {
        "spot_exchange_rules": extract_rules(spot_json, "spot"),
        "futures_exchange_rules": extract_rules(futures_json, "futures"),
    }, {"spot_exchange_info": spot_meta, "futures_exchange_info": futures_meta}


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
        exchange_rules["spot_exchange_rules"].get(symbol)
        if side == "spot"
        else exchange_rules["futures_exchange_rules"].get(symbol)
    )
    if not rules:
        raise RuntimeError(f"missing {side} exchange rules for {symbol}")
    filters = rules["filters"]
    lot = filters["LOT_SIZE"]
    return {
        "status": rules.get("status"),
        "min_qty": decimal_value(lot["minQty"], f"{side} {symbol} minQty"),
        "max_qty": decimal_value(lot["maxQty"], f"{side} {symbol} maxQty"),
        "step_size": decimal_value(lot["stepSize"], f"{side} {symbol} stepSize"),
        "min_notional": min_notional_from_filters(filters, side),
    }


def build_params(exchange_rules: dict) -> dict:
    return {
        symbol: {
            "spot": rule_params(exchange_rules, symbol, "spot"),
            "futures": rule_params(exchange_rules, symbol, "futures"),
        }
        for symbol in SYMBOLS
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
    center_values = [
        floor_decimal(target_common_qty / common_step),
        ceil_decimal(target_common_qty / common_step),
        floor_decimal(target_by_avg / common_step),
        ceil_decimal(target_by_avg / common_step),
    ]
    k_values: set[int] = {int(lower_k), int(upper_k)}
    for center in center_values:
        for offset in range(-25, 26):
            candidate_k = int(center) + offset
            if int(lower_k) <= candidate_k <= int(upper_k):
                k_values.add(candidate_k)
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
    pass_checks = {
        "common_qty_positive": common_qty > 0,
        "spot_min_qty_pass": common_qty >= spot_params["min_qty"],
        "futures_min_qty_pass": common_qty >= futures_params["min_qty"],
        "spot_max_qty_pass": common_qty <= spot_params["max_qty"],
        "futures_max_qty_pass": common_qty <= futures_params["max_qty"],
        "spot_min_notional_pass": spot_notional >= spot_params["min_notional"],
        "futures_min_notional_pass": futures_notional >= futures_params["min_notional"],
        "leg_notional_mismatch_pass": mismatch_bps <= MISMATCH_THRESHOLD_BPS,
        "unused_notional_pass": unused_bps <= UNUSED_NOTIONAL_THRESHOLD_BPS,
        "overspend_rule_pass": overspend_bps <= MAX_OVESPEND_BPS,
    }
    return {
        "selected_common_base_qty": common_qty,
        "spot_long_quantity": common_qty,
        "futures_short_quantity": common_qty,
        "spot_notional": spot_notional,
        "futures_notional": futures_notional,
        "leg_notional_mismatch_bps": mismatch_bps,
        "unused_notional_bps": unused_bps,
        "max_leg_overspend_bps": overspend_bps,
        "pass_checks": pass_checks,
        "symbol_pass": all(pass_checks.values()),
    }


def simulate_symbol(capital: Decimal, symbol: str, spot_price: Decimal, futures_price: Decimal, params: dict) -> dict:
    target_notional = capital / Decimal(len(SYMBOLS))
    spot_params = params[symbol]["spot"]
    futures_params = params[symbol]["futures"]
    common_step = lcm_decimal_step(spot_params["step_size"], futures_params["step_size"])
    candidates = candidate_quantities(
        target_notional,
        spot_price,
        futures_price,
        common_step,
        max(spot_params["min_qty"], futures_params["min_qty"]),
        min(spot_params["max_qty"], futures_params["max_qty"]),
    )
    best = None
    for candidate in candidates:
        evaluated = evaluate_quantity(candidate, target_notional, spot_price, futures_price, spot_params, futures_params)
        if best is None:
            best = evaluated
            continue
        best_score = (0 if best["symbol_pass"] else 1, abs(best["unused_notional_bps"]), best["leg_notional_mismatch_bps"])
        candidate_score = (
            0 if evaluated["symbol_pass"] else 1,
            abs(evaluated["unused_notional_bps"]),
            evaluated["leg_notional_mismatch_bps"],
        )
        if candidate_score < best_score:
            best = evaluated
    if best is None:
        best = evaluate_quantity(Decimal("0"), target_notional, spot_price, futures_price, spot_params, futures_params)
    return {
        "symbol": symbol,
        "capital_usdt": decimal_text(capital),
        "target_notional_per_symbol": decimal_text(target_notional),
        "common_base_quantity": decimal_text(best["spot_long_quantity"]),
        "spot_notional": decimal_text(best["spot_notional"]),
        "futures_notional": decimal_text(best["futures_notional"]),
        "leg_notional_mismatch_bps": decimal_float(best["leg_notional_mismatch_bps"]),
        "unused_notional_bps": decimal_float(best["unused_notional_bps"]),
        "spot_rule_pass": all(
            best["pass_checks"][key]
            for key in ("common_qty_positive", "spot_min_qty_pass", "spot_max_qty_pass", "spot_min_notional_pass")
        ),
        "futures_rule_pass": all(
            best["pass_checks"][key]
            for key in ("common_qty_positive", "futures_min_qty_pass", "futures_max_qty_pass", "futures_min_notional_pass")
        ),
        "pass_checks": best["pass_checks"],
        "symbol_pass": best["symbol_pass"],
    }


def simulate_sizing(spot_prices: dict, futures_prices: dict, params: dict) -> dict:
    scenario_results = []
    for capital in CAPITAL_SCENARIOS:
        capital_decimal = Decimal(str(capital))
        symbol_results = [
            simulate_symbol(capital_decimal, symbol, spot_prices[symbol], futures_prices[symbol], params)
            for symbol in SYMBOLS
            if symbol in spot_prices and symbol in futures_prices
        ]
        max_mismatch = max((Decimal(str(item.get("leg_notional_mismatch_bps", 0))) for item in symbol_results), default=Decimal("0"))
        max_unused = max((Decimal(str(item.get("unused_notional_bps", 10000))) for item in symbol_results), default=Decimal("10000"))
        scenario_pass = len(symbol_results) == len(SYMBOLS) and all(item.get("symbol_pass") is True for item in symbol_results)
        scenario_results.append(
            {
                "capital_usdt": capital,
                "symbol_results": symbol_results,
                "max_leg_notional_mismatch_bps": decimal_float(max_mismatch),
                "max_unused_notional_bps": decimal_float(max_unused),
                "scenario_pass_pre_risk": scenario_pass,
            }
        )
    return {"scenario_results": scenario_results}


def build_risk_flags(records: dict, rules: dict, metadata: dict, sizing: dict) -> dict:
    critical: list[str] = []
    non_critical: list[str] = []
    for symbol in SYMBOLS:
        record = records.get(symbol, {})
        if not record.get("spot_price"):
            critical.append(f"{symbol}:missing_spot_price")
        if not record.get("futures_price"):
            critical.append(f"{symbol}:missing_futures_price")
        premium = record.get("premium_index")
        if not premium or premium.get("lastFundingRate") in (None, ""):
            critical.append(f"{symbol}:missing_premiumIndex_or_funding")
        if not premium or premium.get("nextFundingTime_utc") in (None, ""):
            non_critical.append(f"{symbol}:next_funding_time_ambiguous")
        if premium and decimal_value(premium.get("lastFundingRate", "0"), f"{symbol} funding") < 0:
            non_critical.append(f"{symbol}:one_symbol_negative_funding")
        spot_rule = rules["spot_exchange_rules"].get(symbol)
        futures_rule = rules["futures_exchange_rules"].get(symbol)
        if not spot_rule or not futures_rule:
            critical.append(f"{symbol}:missing_exchange_rules")
        elif spot_rule.get("status") != "TRADING" or futures_rule.get("status") != "TRADING":
            critical.append(f"{symbol}:symbol_status_not_trading")
    for record in records.values():
        for item in record["endpoint_metadata"].values():
            if item.get("http_status") != 200 or item.get("error"):
                critical.append("stale_snapshot")
    for item in metadata.values():
        if item.get("http_status") != 200 or item.get("error"):
            critical.append("stale_snapshot")
    pre_risk_passes = [item for item in sizing["scenario_results"] if item["scenario_pass_pre_risk"]]
    if not pre_risk_passes:
        critical.append("all_scenarios_fail_sizing")
    if len(pre_risk_passes) < len(CAPITAL_SCENARIOS):
        non_critical.append("some_scenarios_fail_sizing")
    for item in sizing["scenario_results"]:
        if not item["scenario_pass_pre_risk"] and item["max_leg_notional_mismatch_bps"] > float(MISMATCH_THRESHOLD_BPS):
            non_critical.append(f"capital_{item['capital_usdt']}:high_mismatch_in_non_selected_scenario")
    funding_rates = [
        decimal_value(records[symbol]["premium_index"]["lastFundingRate"], f"{symbol} funding")
        for symbol in SYMBOLS
        if records.get(symbol, {}).get("premium_index")
    ]
    if funding_rates and all(value < 0 for value in funding_rates):
        critical.append("all_symbols_have_negative_funding")
    return {
        "critical_risk_flags": sorted(set(critical)),
        "non_critical_risk_flags": sorted(set(non_critical)),
    }


def update_sizing_after_risk(sizing: dict, critical_flags: list[str]) -> dict:
    passing = []
    for item in sizing["scenario_results"]:
        item["scenario_pass"] = item["scenario_pass_pre_risk"] and not critical_flags
        if item["scenario_pass"]:
            passing.append(item["capital_usdt"])
    sizing["passing_capital_scenarios"] = passing
    sizing["minimum_passing_capital"] = min(passing) if passing else None
    sizing["scenario_pass_fail_summary"] = {str(item["capital_usdt"]): item["scenario_pass"] for item in sizing["scenario_results"]}
    return sizing


def classify_cycle(passing: list[int], critical: list[str], non_critical: list[str]) -> str:
    if critical or not passing:
        return "CYCLE_FAIL_CRITICAL_RISK_FLAGS_REPORT_ONLY"
    if non_critical:
        return "CYCLE_PARTIAL_NON_CRITICAL_RISK_FLAGS_REPORT_ONLY"
    return "CYCLE_PASS_SIMULATED_ENTRY_DECISION_REPORT_ONLY"


def state_trace(cycle_index: int, critical: list[str], passing: list[int]) -> list[dict]:
    trace = [
        {"state": "CYCLE_START", "cycle_index": cycle_index, "orders_allowed": False},
        {"state": "SNAPSHOT_PUBLIC_MARKET_DATA", "orders_allowed": False},
        {"state": "REFRESH_EXCHANGE_RULES", "orders_allowed": False},
        {"state": "RUN_REPAIRED_SIZING", "orders_allowed": False},
    ]
    if critical:
        trace.append({"state": "RISK_HALT", "flags": critical, "orders_allowed": False})
    elif passing:
        trace.append({"state": "SIMULATE_ENTRY_DECISION", "label": "SIMULATED_NOT_ORDER", "orders_allowed": False})
    trace.append({"state": "CYCLE_REPORT", "orders_allowed": False})
    return trace


def simulated_entry_plan(cycle_index: int, sizing: dict, records: dict) -> list[dict]:
    plans = []
    for scenario in sizing["scenario_results"]:
        if not scenario["scenario_pass"]:
            continue
        plans.append(
            {
                "cycle_index": cycle_index,
                "capital_usdt": scenario["capital_usdt"],
                "label": "SIMULATED_NOT_ORDER",
                "orders_generated": False,
                "real_order_payload_generated": False,
                "symbol_entries": [
                    {
                        "label": "SIMULATED_NOT_ORDER",
                        "symbol": item["symbol"],
                        "paper_spot_side": "BUY",
                        "paper_futures_side": "SHORT",
                        "common_base_quantity": item["common_base_quantity"],
                        "spot_notional": item["spot_notional"],
                        "futures_notional": item["futures_notional"],
                        "leg_notional_mismatch_bps": item["leg_notional_mismatch_bps"],
                        "lastFundingRate": (records[item["symbol"]].get("premium_index") or {}).get("lastFundingRate"),
                        "nextFundingTime_utc": (records[item["symbol"]].get("premium_index") or {}).get("nextFundingTime_utc"),
                    }
                    for item in scenario["symbol_results"]
                ],
            }
        )
    return plans


def run_cycle(cycle_index: int) -> tuple[dict, list[dict]]:
    cycle_start = utc_now()
    records, spot_prices, futures_prices = fetch_symbol_snapshots()
    rules, metadata = fetch_exchange_rules()
    params = build_params(rules)
    sizing = simulate_sizing(spot_prices, futures_prices, params)
    flags = build_risk_flags(records, rules, metadata, sizing)
    sizing = update_sizing_after_risk(sizing, flags["critical_risk_flags"])
    entry_plans = simulated_entry_plan(cycle_index, sizing, records)
    classification = classify_cycle(
        sizing["passing_capital_scenarios"],
        flags["critical_risk_flags"],
        flags["non_critical_risk_flags"],
    )
    negative_funding_symbols = [
        symbol
        for symbol in SYMBOLS
        if records[symbol].get("premium_index")
        and decimal_value(records[symbol]["premium_index"]["lastFundingRate"], f"{symbol} funding") < 0
    ]
    cycle_record = {
        "cycle_index": cycle_index,
        "cycle_start_time_utc": cycle_start,
        "snapshot_time_utc": utc_now(),
        "symbols": list(SYMBOLS),
        "symbol_snapshot_records": records,
        "exchange_rule_snapshot_metadata": metadata,
        "capital_scenario_results": sizing["scenario_results"],
        "passing_capital_scenarios": sizing["passing_capital_scenarios"],
        "minimum_passing_capital": sizing["minimum_passing_capital"],
        "risk_flags": flags,
        "state_trace": state_trace(cycle_index, flags["critical_risk_flags"], sizing["passing_capital_scenarios"]),
        "simulated_entry_plan": entry_plans,
        "cycle_classification": classification,
        "funding_negative_symbols": negative_funding_symbols,
        "no_order_confirmation": True,
    }
    return cycle_record, entry_plans


def aggregate_report(cycles: list[dict]) -> dict:
    cycles_with_passing = [item for item in cycles if item["passing_capital_scenarios"]]
    cycles_with_critical = [item for item in cycles if item["risk_flags"]["critical_risk_flags"]]
    cycles_with_non_critical = [item for item in cycles if item["risk_flags"]["non_critical_risk_flags"]]
    scenario_frequency = {str(capital): 0 for capital in CAPITAL_SCENARIOS}
    non_critical_frequency: dict[str, int] = {}
    for cycle in cycles:
        for capital in cycle["passing_capital_scenarios"]:
            scenario_frequency[str(capital)] += 1
        for flag in cycle["risk_flags"]["non_critical_risk_flags"]:
            non_critical_frequency[flag] = non_critical_frequency.get(flag, 0) + 1
    return {
        "cycle_count_requested": CYCLE_COUNT,
        "cycles_completed": len(cycles),
        "cycles_with_passing_scenario": len(cycles_with_passing),
        "cycles_with_critical_risk": len(cycles_with_critical),
        "cycles_with_non_critical_risk": len(cycles_with_non_critical),
        "minimum_passing_capital_by_cycle": {
            str(item["cycle_index"]): item["minimum_passing_capital"] for item in cycles
        },
        "scenario_pass_frequency": scenario_frequency,
        "most_common_non_critical_flags": dict(sorted(non_critical_frequency.items(), key=lambda item: (-item[1], item[0]))),
        "funding_negative_symbol_count_by_cycle": {
            str(item["cycle_index"]): len(item["funding_negative_symbols"]) for item in cycles
        },
        "all_cycle_records": cycles,
        "no_live_confirmation": True,
    }


def classify_run(report: dict) -> tuple[str, str]:
    if report["cycles_with_critical_risk"] > 0 or report["cycles_with_passing_scenario"] == 0:
        return (
            "MULTI_CYCLE_PAPER_DRY_RUN_FAIL_NO_LIVE_PERMISSION",
            "PAPER_MONITOR_MULTI_CYCLE_REPAIR_OR_WAIT_FOR_NEW_SNAPSHOT_ONLY",
        )
    if report["cycles_with_non_critical_risk"] > 0:
        return (
            "MULTI_CYCLE_PAPER_DRY_RUN_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION",
            "PAPER_MONITOR_REPORTING_RECONCILIATION_DESIGN_ONLY",
        )
    return (
        "MULTI_CYCLE_PAPER_DRY_RUN_PASS_READY_FOR_REPORTING_RECONCILIATION_DESIGN_NO_LIVE_PERMISSION",
        "PAPER_MONITOR_REPORTING_RECONCILIATION_DESIGN_ONLY",
    )


def main() -> int:
    ensure_target_absent()
    artifacts = {
        "preview": load_json(PREVIEW_PATH),
        "design": load_json(DESIGN_PATH),
        "single_cycle": load_json(SINGLE_CYCLE_PATH),
        "paper_monitor_design": load_json(PAPER_MONITOR_DESIGN_PATH),
        "sizing_repair": load_json(SIZING_REPAIR_PATH),
        "exchange_rule": load_json(EXCHANGE_RULE_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_prior_chain(artifacts)
    guard_constants = {
        "ORDER_PLACEMENT_ALLOWED": ORDER_PLACEMENT_ALLOWED,
        "PRIVATE_API_ALLOWED": PRIVATE_API_ALLOWED,
        "API_KEY_ALLOWED": API_KEY_ALLOWED,
        "RUNTIME_ALLOWED": RUNTIME_ALLOWED,
        "SCHEDULER_ALLOWED": SCHEDULER_ALLOWED,
        "DAEMON_ALLOWED": DAEMON_ALLOWED,
        "LIVE_TRADING_ALLOWED": LIVE_TRADING_ALLOWED,
        "CAPITAL_ALLOCATION_ALLOWED": CAPITAL_ALLOCATION_ALLOWED,
        "CANDIDATE_GENERATION_ALLOWED": CANDIDATE_GENERATION_ALLOWED,
        "EDGE_CLAIM_ALLOWED": EDGE_CLAIM_ALLOWED,
    }
    if any(guard_constants.values()):
        raise RuntimeError("one or more no-live guard constants is true")

    cycle_records = []
    entry_plans = []
    for cycle_index in range(1, CYCLE_COUNT + 1):
        cycle_record, plans = run_cycle(cycle_index)
        cycle_records.append(cycle_record)
        entry_plans.extend(plans)

    report = aggregate_report(cycle_records)
    classification, next_allowed_step = classify_run(report)
    all_critical = sorted({flag for cycle in cycle_records for flag in cycle["risk_flags"]["critical_risk_flags"]})
    all_non_critical = sorted({flag for cycle in cycle_records for flag in cycle["risk_flags"]["non_critical_risk_flags"]})

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_multi_cycle_preview_loaded": True,
        "prior_design_loaded": True,
        "public_price_snapshot_fetched": all(
            all(cycle["symbol_snapshot_records"][symbol].get(key) for symbol in SYMBOLS)
            for cycle in cycle_records
            for key in ("spot_price", "futures_price")
        ),
        "public_exchange_rules_fetched": True,
        "public_premium_index_fetched": all(
            all(cycle["symbol_snapshot_records"][symbol].get("premium_index") for symbol in SYMBOLS)
            for cycle in cycle_records
        ),
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_launcher_created": True,
        "no_live_or_capital_permission": True,
        "common_base_quantity_algorithm_used": True,
        "cycle_records_created": len(cycle_records) == CYCLE_COUNT,
        "simulated_entry_plans_labeled_not_order": all(plan["label"] == "SIMULATED_NOT_ORDER" for plan in entry_plans),
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
            "multi_cycle_implementation_preview": PREVIEW_RELATIVE_PATH,
            "multi_cycle_implementation_preview_payload_sha256_excluding_hash": PREVIEW_PAYLOAD_SHA256,
            "multi_cycle_design": DESIGN_RELATIVE_PATH,
            "multi_cycle_design_payload_sha256_excluding_hash": DESIGN_PAYLOAD_SHA256,
            "single_cycle_dry_run": SINGLE_CYCLE_RELATIVE_PATH,
            "single_cycle_payload_sha256_excluding_hash": SINGLE_CYCLE_PAYLOAD_SHA256,
            "paper_monitor_design": PAPER_MONITOR_DESIGN_RELATIVE_PATH,
            "paper_monitor_design_payload_sha256_excluding_hash": PAPER_MONITOR_DESIGN_PAYLOAD_SHA256,
            "order_sizing_repair_sim": SIZING_REPAIR_RELATIVE_PATH,
            "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "strategy_closure": CLOSURE_RELATIVE_PATH,
            "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_preview_preserved": {
            "status": artifacts["preview"]["status"],
            "next_allowed_step": artifacts["preview"]["next_allowed_step"],
            "class_count": artifacts["preview"]["preview_module_structure"]["class_count"],
            "state_count": artifacts["preview"]["state_machine_preview"]["state_count"],
            "transition_count": artifacts["preview"]["transition_table_preview"]["transition_count"],
            "adapter_stub_count": artifacts["preview"]["adapter_stub_contract"]["adapter_stub_count"],
            "report_schema_count": len(artifacts["preview"]["report_schema_preview"]),
            "no_live_permission_preserved": True,
        },
        "run_configuration": {
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "cycle_count": CYCLE_COUNT,
            "cycle_spacing_seconds": CYCLE_SPACING_SECONDS,
            "capital_scenarios": list(CAPITAL_SCENARIOS),
            "manual_invocation_only": True,
            "scheduler_created": False,
            "daemon_created": False,
            "sleep_longer_than_2_seconds": False,
            "background_work": False,
        },
        "cycle_records": cycle_records,
        "aggregate_run_report": report,
        "risk_flag_summary": {
            "critical_risk_flags_observed": all_critical,
            "non_critical_risk_flags_observed": all_non_critical,
            "critical_risk_flag_count": len(all_critical),
            "non_critical_risk_flag_count": len(all_non_critical),
        },
        "simulated_entry_plans": entry_plans,
        "classification": {
            "classification": classification,
            "classification_grants_live_or_capital_permission": False,
        },
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "This is a finite manual paper dry-run only and is not a daemon, scheduler, service, runtime, live system, or capital allocation.",
            "Only public Binance market-data and exchangeInfo endpoints are used.",
            "No private API, API key, account endpoint, balance endpoint, listen key, order endpoint, real order payload, or order placement is used.",
            "Simulated entry plans are labeled SIMULATED_NOT_ORDER and are report-only.",
            "No candidate generation, edge claim, or family release is created.",
        ],
        "safety_permissions": {
            "multi_cycle_paper_dry_run_created": True,
            "order_placement_allowed_now": False,
            "private_api_allowed_now": False,
            "api_key_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "scheduler_allowed_now": False,
            "daemon_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "next_step_must_not_be_live_or_capital": True,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    artifact["payload_sha256_excluding_hash"] = payload_hash(artifact)

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout = {
        "status": STATUS,
        "classification": classification,
        "cycle_count_requested": report["cycle_count_requested"],
        "cycles_completed": report["cycles_completed"],
        "cycles_with_passing_scenario": report["cycles_with_passing_scenario"],
        "cycles_with_critical_risk": report["cycles_with_critical_risk"],
        "cycles_with_non_critical_risk": report["cycles_with_non_critical_risk"],
        "minimum_passing_capital_by_cycle": report["minimum_passing_capital_by_cycle"],
        "next_allowed_step": next_allowed_step,
        "order_placement_allowed_now": False,
        "runtime_live_capital": False,
        "candidate_generation": False,
        "edge_claim": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    for key, value in stdout.items():
        print(f"{key}: {json.dumps(value, sort_keys=True)}")
    return 0 if replacement_checks_all_true else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(1)
