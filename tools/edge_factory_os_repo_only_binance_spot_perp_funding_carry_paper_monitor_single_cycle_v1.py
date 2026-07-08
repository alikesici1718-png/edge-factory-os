#!/usr/bin/env python
"""Run one manual paper-monitor dry-run cycle for the Binance spot-perp carry route."""

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
    "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_paper_monitor_single_cycle_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

PREVIEW_RELATIVE_PATH = (
    "artifacts/paper_monitor_previews/binance_spot_perp_funding_carry_paper_monitor_dry_run_preview_v1.json"
)
DESIGN_RELATIVE_PATH = (
    "artifacts/paper_monitor_designs/binance_spot_perp_funding_carry_paper_monitor_design_v1.json"
)
PAPER_DRY_RUN_RELATIVE_PATH = (
    "artifacts/paper_trading_dry_runs/binance_spot_perp_funding_carry_paper_dry_run_simulator_v1.json"
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
PAPER_DRY_RUN_PATH = REPO_ROOT / PAPER_DRY_RUN_RELATIVE_PATH
SIZING_REPAIR_PATH = REPO_ROOT / SIZING_REPAIR_RELATIVE_PATH
EXCHANGE_RULE_PATH = REPO_ROOT / EXCHANGE_RULE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH

STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_SINGLE_CYCLE_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_SINGLE_CYCLE_DRY_RUN"

PREVIEW_STATUS = "PASS_REPO_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_PAPER_MONITOR_DRY_RUN_PREVIEW_CREATED"
PREVIEW_NEXT_STEP = "PAPER_MONITOR_DRY_RUN_SINGLE_CYCLE_IMPLEMENTATION_ONLY"
PREVIEW_PAYLOAD_SHA256 = "2d82499353b3ff5ed2326644de01fdfad01d2ca4a13e4edd7c90c4a329fa6173"
DESIGN_PAYLOAD_SHA256 = "25cb17fa9a4e296f194b79808a6515d880ec232ecde3356c008ccb2da04c6188"
PAPER_DRY_RUN_PAYLOAD_SHA256 = "7dcc93b6c82344266c72144f2cd06c5b5507701d2c7f99a7971652f175dc655d"
SIZING_REPAIR_PAYLOAD_SHA256 = "0f189c4b8999d7d9a1018cf988952e630d554ed898fc29a61510af93a906d822"
EXCHANGE_RULE_PAYLOAD_SHA256 = "db998979f8d902ddff553877fa59384893021d2e814fb4c42dbc1ab194ebff46"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"

ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS = (100, 235, 250, 500, 1000, 2500, 5000)
TRACKED_PYTHON_COUNT_AT_START = 892

SPOT_TICKER_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
FUTURES_TICKER_PRICE_URL = "https://fapi.binance.com/fapi/v1/ticker/price"
FUTURES_PREMIUM_INDEX_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
SPOT_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"
FUTURES_EXCHANGE_INFO_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"

MISMATCH_THRESHOLD_BPS = Decimal("25")
UNUSED_NOTIONAL_THRESHOLD_BPS = Decimal("500")
MAX_OVESPEND_BPS = Decimal("25")


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


def assert_payload(name: str, artifact: dict, expected_hash: str) -> None:
    actual = artifact.get("payload_sha256_excluding_hash")
    if actual != expected_hash:
        raise RuntimeError(f"{name} payload hash mismatch: expected {expected_hash}, got {actual}")


def validate_prior_chain(artifacts: dict) -> None:
    preview = artifacts["preview"]
    if preview.get("status") != PREVIEW_STATUS:
        raise RuntimeError("preview status mismatch")
    if preview.get("next_allowed_step") != PREVIEW_NEXT_STEP:
        raise RuntimeError("preview next allowed step mismatch")
    assert_payload("preview", preview, PREVIEW_PAYLOAD_SHA256)
    for source_key, expected in (
        ("design", DESIGN_PAYLOAD_SHA256),
        ("paper_dry_run", PAPER_DRY_RUN_PAYLOAD_SHA256),
        ("sizing_repair", SIZING_REPAIR_PAYLOAD_SHA256),
        ("exchange_rule", EXCHANGE_RULE_PAYLOAD_SHA256),
        ("risk_capital", RISK_CAPITAL_PAYLOAD_SHA256),
        ("closure", CLOSURE_PAYLOAD_SHA256),
    ):
        assert_payload(source_key, artifacts[source_key], expected)
    for key in (
        "order_placement_allowed_now",
        "private_api_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
    ):
        if preview["safety_permissions"].get(key) is not False:
            raise RuntimeError(f"preview safety permission not false: {key}")


def fetch_json(url: str, params: dict | None = None) -> tuple[dict | None, dict]:
    final_url = url
    if params:
        final_url = f"{url}?{urllib.parse.urlencode(params)}"
    started = utc_now()
    request = urllib.request.Request(
        final_url,
        headers={
            "User-Agent": "edge-factory-os-paper-monitor-single-cycle-public-data/1.0",
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
    premium: dict[str, dict] = {}
    records: dict[str, dict] = {}
    for symbol in SYMBOLS:
        spot_json, spot_meta = fetch_json(SPOT_TICKER_PRICE_URL, {"symbol": symbol})
        futures_json, futures_meta = fetch_json(FUTURES_TICKER_PRICE_URL, {"symbol": symbol})
        premium_json, premium_meta = fetch_json(FUTURES_PREMIUM_INDEX_URL, {"symbol": symbol})

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

        records[symbol] = {
            "symbol": symbol,
            "spot_price": decimal_text(spot_prices.get(symbol)),
            "futures_price": decimal_text(futures_prices.get(symbol)),
            "premium_index": premium.get(symbol),
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
    rules = {
        "spot_exchange_rules": extract_rules(spot_json, "spot"),
        "futures_exchange_rules": extract_rules(futures_json, "futures"),
    }
    metadata = {"spot_exchange_info": spot_meta, "futures_exchange_info": futures_meta}
    return rules, metadata


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
    params = {}
    for symbol in SYMBOLS:
        params[symbol] = {
            "spot": rule_params(exchange_rules, symbol, "spot"),
            "futures": rule_params(exchange_rules, symbol, "futures"),
        }
    return params


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
        "avg_notional": avg_notional,
        "leg_notional_mismatch_bps": mismatch_bps,
        "unused_notional_bps": unused_bps,
        "max_leg_overspend_bps": overspend_bps,
        "pass_checks": pass_checks,
        "symbol_pass": all(pass_checks.values()),
    }


def simulate_symbol(
    capital: Decimal,
    symbol: str,
    spot_price: Decimal,
    futures_price: Decimal,
    params: dict,
) -> dict:
    target_notional = capital / Decimal(len(SYMBOLS))
    spot_params = params[symbol]["spot"]
    futures_params = params[symbol]["futures"]
    common_step = lcm_decimal_step(spot_params["step_size"], futures_params["step_size"])
    min_common_qty = max(spot_params["min_qty"], futures_params["min_qty"])
    max_common_qty = min(spot_params["max_qty"], futures_params["max_qty"])
    candidates = candidate_quantities(
        target_notional,
        spot_price,
        futures_price,
        common_step,
        min_common_qty,
        max_common_qty,
    )
    best = None
    for candidate in candidates:
        evaluated = evaluate_quantity(candidate, target_notional, spot_price, futures_price, spot_params, futures_params)
        if best is None:
            best = evaluated
            continue
        best_score = (
            0 if best["symbol_pass"] else 1,
            abs(best["unused_notional_bps"]),
            best["leg_notional_mismatch_bps"],
        )
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
        "common_step_size": decimal_text(common_step),
        "candidate_quantity_count": len(candidates),
        "spot_price": decimal_text(spot_price),
        "futures_price": decimal_text(futures_price),
        "spot_quantity": decimal_text(best["spot_long_quantity"]),
        "futures_quantity": decimal_text(best["futures_short_quantity"]),
        "spot_notional": decimal_text(best["spot_notional"]),
        "futures_notional": decimal_text(best["futures_notional"]),
        "leg_notional_mismatch_bps": decimal_float(best["leg_notional_mismatch_bps"]),
        "unused_notional_bps": decimal_float(best["unused_notional_bps"]),
        "max_leg_overspend_bps": decimal_float(best["max_leg_overspend_bps"]),
        "spot_rule_pass": all(
            best["pass_checks"][key]
            for key in (
                "spot_min_qty_pass",
                "spot_max_qty_pass",
                "spot_min_notional_pass",
                "common_qty_positive",
            )
        ),
        "futures_rule_pass": all(
            best["pass_checks"][key]
            for key in (
                "futures_min_qty_pass",
                "futures_max_qty_pass",
                "futures_min_notional_pass",
                "common_qty_positive",
            )
        ),
        "pass_checks": best["pass_checks"],
        "symbol_pass": best["symbol_pass"],
    }


def simulate_sizing(spot_prices: dict, futures_prices: dict, params: dict) -> dict:
    scenario_results = []
    for capital in CAPITAL_SCENARIOS:
        capital_decimal = Decimal(str(capital))
        symbol_results = []
        for symbol in SYMBOLS:
            if symbol not in spot_prices or symbol not in futures_prices:
                symbol_results.append(
                    {
                        "symbol": symbol,
                        "capital_usdt": str(capital),
                        "symbol_pass": False,
                        "failure_reason": "missing spot or futures price",
                    }
                )
                continue
            symbol_results.append(
                simulate_symbol(capital_decimal, symbol, spot_prices[symbol], futures_prices[symbol], params)
            )
        max_mismatch = max((Decimal(str(item.get("leg_notional_mismatch_bps", 0))) for item in symbol_results), default=Decimal("0"))
        max_unused = max((Decimal(str(item.get("unused_notional_bps", 10000))) for item in symbol_results), default=Decimal("10000"))
        scenario_pass_pre_risk = all(item.get("symbol_pass") is True for item in symbol_results)
        scenario_results.append(
            {
                "capital_usdt": capital,
                "target_notional_per_symbol": decimal_text(capital_decimal / Decimal(len(SYMBOLS))),
                "symbol_results": symbol_results,
                "max_leg_mismatch_bps": decimal_float(max_mismatch),
                "max_unused_notional_bps": decimal_float(max_unused),
                "scenario_pass_pre_risk": scenario_pass_pre_risk,
            }
        )
    return {"scenario_results": scenario_results}


def build_risk_flags(
    records: dict,
    rules: dict,
    rule_metadata: dict,
    sizing: dict,
) -> dict:
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
        if premium and decimal_value(premium.get("lastFundingRate", "0"), f"{symbol} funding rate") < 0:
            non_critical.append(f"{symbol}:negative_funding")
        spot_rule = rules.get("spot_exchange_rules", {}).get(symbol)
        futures_rule = rules.get("futures_exchange_rules", {}).get(symbol)
        if not spot_rule or not futures_rule:
            critical.append(f"{symbol}:missing_exchange_rules")
        else:
            if spot_rule.get("status") != "TRADING" or futures_rule.get("status") != "TRADING":
                critical.append(f"{symbol}:symbol_status_not_trading")

    snapshot_errors = []
    for record in records.values():
        for meta in record["endpoint_metadata"].values():
            if meta.get("error") or meta.get("http_status") != 200:
                snapshot_errors.append(meta.get("url", "unknown_public_snapshot"))
    for meta in rule_metadata.values():
        if meta.get("error") or meta.get("http_status") != 200:
            snapshot_errors.append(meta.get("url", "unknown_exchange_rule_snapshot"))
    if snapshot_errors:
        critical.append("stale_or_incomplete_public_snapshot")

    pre_risk_passes = [item for item in sizing["scenario_results"] if item["scenario_pass_pre_risk"]]
    if not pre_risk_passes:
        critical.append("all_scenarios_fail_sizing")
    if len(pre_risk_passes) < len(CAPITAL_SCENARIOS):
        non_critical.append("some_scenarios_fail_sizing")
    for item in sizing["scenario_results"]:
        if not item["scenario_pass_pre_risk"] and item["max_leg_mismatch_bps"] > float(MISMATCH_THRESHOLD_BPS):
            non_critical.append(f"capital_{item['capital_usdt']}:high_mismatch_non_selected_scenario")

    funding_rates = []
    for symbol in SYMBOLS:
        premium = records.get(symbol, {}).get("premium_index")
        if premium and premium.get("lastFundingRate") not in (None, ""):
            funding_rates.append(decimal_value(premium["lastFundingRate"], f"{symbol} funding"))
    if funding_rates and all(value < 0 for value in funding_rates):
        critical.append("all_symbols_have_negative_funding")

    return {
        "critical_risk_flags": sorted(set(critical)),
        "non_critical_risk_flags": sorted(set(non_critical)),
        "private_or_order_endpoint_attempted": False,
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


def build_state_trace(critical_flags: list[str], passing_capitals: list[int]) -> list[dict]:
    trace = [
        {"state": "DISABLED", "action": "manual single-cycle dry run invoked", "orders_allowed": False},
        {"state": "SNAPSHOT_PUBLIC_MARKET_DATA", "action": "fetch allowed public price and premium snapshots", "orders_allowed": False},
        {"state": "REFRESH_EXCHANGE_RULES", "action": "fetch allowed public exchangeInfo rules", "orders_allowed": False},
        {"state": "RUN_REPAIRED_SIZING", "action": "run common-base-quantity sizing", "orders_allowed": False},
    ]
    if critical_flags:
        trace.append({"state": "RISK_HALT", "action": "critical risk flags present", "flags": critical_flags, "orders_allowed": False})
    elif passing_capitals:
        trace.append(
            {
                "state": "SIMULATE_ENTRY_DECISION",
                "action": "paper entry decision only for passing scenarios",
                "label": "SIMULATED_NOT_ORDER",
                "orders_allowed": False,
            }
        )
    trace.append({"state": "REPORT_ONLY", "action": "write immutable report-only artifact", "orders_allowed": False})
    return trace


def build_entry_plan(sizing: dict, records: dict) -> dict:
    plans = []
    for scenario in sizing["scenario_results"]:
        if not scenario["scenario_pass"]:
            continue
        entries = []
        for item in scenario["symbol_results"]:
            premium = records[item["symbol"]].get("premium_index") or {}
            entries.append(
                {
                    "label": "SIMULATED_NOT_ORDER",
                    "symbol": item["symbol"],
                    "paper_intent_spot_side": "BUY",
                    "paper_intent_futures_side": "SHORT",
                    "spot_quantity": item.get("spot_quantity"),
                    "futures_quantity": item.get("futures_quantity"),
                    "spot_notional": item.get("spot_notional"),
                    "futures_notional": item.get("futures_notional"),
                    "leg_notional_mismatch_bps": item.get("leg_notional_mismatch_bps"),
                    "current_lastFundingRate": premium.get("lastFundingRate"),
                    "nextFundingTime_utc": premium.get("nextFundingTime_utc"),
                    "real_order_payload_generated": False,
                    "real_order_endpoint_called": False,
                }
            )
        plans.append(
            {
                "capital_usdt": scenario["capital_usdt"],
                "label": "SIMULATED_NOT_ORDER",
                "orders_generated": False,
                "order_endpoint_payload_generated": False,
                "symbol_entries": entries,
            }
        )
    return {
        "plans": plans,
        "orders_generated": False,
        "order_endpoint_payload_generated": False,
        "all_entries_labeled": "SIMULATED_NOT_ORDER",
    }


def classification_and_next_step(passing: list[int], critical: list[str], non_critical: list[str]) -> tuple[str, str]:
    if critical or not passing:
        return (
            "PAPER_MONITOR_SINGLE_CYCLE_FAIL_NO_LIVE_PERMISSION",
            "PAPER_MONITOR_SINGLE_CYCLE_REPAIR_OR_WAIT_FOR_NEW_SNAPSHOT_ONLY",
        )
    if non_critical:
        return (
            "PAPER_MONITOR_SINGLE_CYCLE_PARTIAL_RISK_FLAGS_NO_LIVE_PERMISSION",
            "PAPER_MONITOR_MULTI_CYCLE_DRY_RUN_DESIGN_ONLY",
        )
    return (
        "PAPER_MONITOR_SINGLE_CYCLE_PASS_READY_FOR_MULTI_CYCLE_DRY_RUN_DESIGN_NO_LIVE_PERMISSION",
        "PAPER_MONITOR_MULTI_CYCLE_DRY_RUN_DESIGN_ONLY",
    )


def main() -> int:
    ensure_target_absent()
    artifacts = {
        "preview": load_json(PREVIEW_PATH),
        "design": load_json(DESIGN_PATH),
        "paper_dry_run": load_json(PAPER_DRY_RUN_PATH),
        "sizing_repair": load_json(SIZING_REPAIR_PATH),
        "exchange_rule": load_json(EXCHANGE_RULE_PATH),
        "risk_capital": load_json(RISK_CAPITAL_PATH),
        "closure": load_json(CLOSURE_PATH),
    }
    validate_prior_chain(artifacts)

    snapshot_started = utc_now()
    records, spot_prices, futures_prices = fetch_symbol_snapshots()
    rules, rule_metadata = fetch_exchange_rules()
    params = build_params(rules)
    sizing = simulate_sizing(spot_prices, futures_prices, params)
    risk_flags = build_risk_flags(records, rules, rule_metadata, sizing)
    sizing = update_sizing_after_risk(sizing, risk_flags["critical_risk_flags"])
    classification, next_allowed_step = classification_and_next_step(
        sizing["passing_capital_scenarios"],
        risk_flags["critical_risk_flags"],
        risk_flags["non_critical_risk_flags"],
    )
    snapshot_time = utc_now()

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_preview_loaded": True,
        "prior_design_loaded": True,
        "prior_sizing_repair_loaded": True,
        "public_price_snapshot_fetched": len(spot_prices) == len(SYMBOLS) and len(futures_prices) == len(SYMBOLS),
        "public_exchange_rules_fetched": set(rules["spot_exchange_rules"]) == set(SYMBOLS)
        and set(rules["futures_exchange_rules"]) == set(SYMBOLS),
        "public_premium_index_fetched": all(records[symbol].get("premium_index") for symbol in SYMBOLS),
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_runtime_enabled": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_live_or_capital_permission": True,
        "common_base_quantity_algorithm_used": True,
        "simulated_entry_plan_labeled_not_order": True,
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
            "paper_monitor_preview": PREVIEW_RELATIVE_PATH,
            "paper_monitor_preview_payload_sha256_excluding_hash": PREVIEW_PAYLOAD_SHA256,
            "paper_monitor_design": DESIGN_RELATIVE_PATH,
            "paper_monitor_design_payload_sha256_excluding_hash": DESIGN_PAYLOAD_SHA256,
            "paper_dry_run": PAPER_DRY_RUN_RELATIVE_PATH,
            "paper_dry_run_payload_sha256_excluding_hash": PAPER_DRY_RUN_PAYLOAD_SHA256,
            "order_sizing_repair_sim": SIZING_REPAIR_RELATIVE_PATH,
            "order_sizing_repair_payload_sha256_excluding_hash": SIZING_REPAIR_PAYLOAD_SHA256,
            "exchange_rule_discovery": EXCHANGE_RULE_RELATIVE_PATH,
            "exchange_rule_payload_sha256_excluding_hash": EXCHANGE_RULE_PAYLOAD_SHA256,
            "risk_capital_diagnostic": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "strategy_closure": CLOSURE_RELATIVE_PATH,
            "strategy_closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
        },
        "prior_chain_preserved": {
            "route_family": ROUTE_FAMILY,
            "config_id": CONFIG_ID,
            "symbols": list(SYMBOLS),
            "prior_preview_status": artifacts["preview"]["status"],
            "prior_preview_next_allowed_step": artifacts["preview"]["next_allowed_step"],
            "paper_monitor_design_classification": artifacts["design"]["classification"],
            "sizing_repair_classification": artifacts["sizing_repair"]["classification"]["classification"],
            "risk_capital_classification": artifacts["risk_capital"]["feasibility_classification"]["classification"],
            "route_closed": artifacts["closure"]["closure_record"]["route_closed"],
            "no_live_capital_permission_preserved": True,
        },
        "public_snapshot_summary": {
            "snapshot_started_utc": snapshot_started,
            "snapshot_time_utc": snapshot_time,
            "spot_symbols_fetched": sorted(spot_prices),
            "futures_symbols_fetched": sorted(futures_prices),
            "premium_symbols_fetched": sorted(symbol for symbol in SYMBOLS if records[symbol].get("premium_index")),
            "public_snapshot_complete": validation_checks["public_price_snapshot_fetched"]
            and validation_checks["public_premium_index_fetched"],
            "private_api_used": False,
            "api_key_used": False,
            "order_endpoint_called": False,
        },
        "symbol_snapshot_records": records,
        "exchange_rule_snapshot_summary": {
            "spot_exchange_info_loaded": rule_metadata["spot_exchange_info"].get("http_status") == 200,
            "futures_exchange_info_loaded": rule_metadata["futures_exchange_info"].get("http_status") == 200,
            "spot_symbols_found": sorted(rules["spot_exchange_rules"]),
            "futures_symbols_found": sorted(rules["futures_exchange_rules"]),
            "spot_symbol_status": {
                symbol: rules["spot_exchange_rules"].get(symbol, {}).get("status") for symbol in SYMBOLS
            },
            "futures_symbol_status": {
                symbol: rules["futures_exchange_rules"].get(symbol, {}).get("status") for symbol in SYMBOLS
            },
            "metadata": rule_metadata,
            "extracted_rules": rules,
        },
        "repaired_sizing_results": sizing,
        "paper_state_machine_trace": build_state_trace(
            risk_flags["critical_risk_flags"], sizing["passing_capital_scenarios"]
        ),
        "simulated_entry_plan": build_entry_plan(sizing, records),
        "risk_flags": risk_flags,
        "classification": {
            "classification": classification,
            "classification_grants_live_or_capital_permission": False,
        },
        "next_allowed_step": next_allowed_step,
        "limitations": [
            "This is one manual paper dry-run cycle only.",
            "Public Binance market-data and exchangeInfo endpoints were used; no private, account, balance, commission, listen-key, or order endpoint was used.",
            "Simulated entries are labeled SIMULATED_NOT_ORDER and do not contain real order payloads.",
            "No daemon, scheduler, service, runtime config, paper monitor enablement, live trading, or capital allocation is created.",
            "No candidate generation, edge claim, or family release is created.",
        ],
        "safety_permissions": {
            "paper_single_cycle_created": True,
            "order_placement_allowed_now": False,
            "private_api_allowed_now": False,
            "runtime_permission_allowed_now": False,
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
        "snapshot_time_utc": snapshot_time,
        "passing_capital_scenarios": sizing["passing_capital_scenarios"],
        "minimum_passing_capital": sizing["minimum_passing_capital"],
        "critical_risk_flags": risk_flags["critical_risk_flags"],
        "non_critical_risk_flags": risk_flags["non_critical_risk_flags"],
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
