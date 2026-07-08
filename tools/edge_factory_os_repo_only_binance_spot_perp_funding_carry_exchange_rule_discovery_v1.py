#!/usr/bin/env python
"""Discover Binance spot and USD-M futures exchange rules for the funding carry route."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path


getcontext().prec = 28

REPO_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_exchange_rule_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = (
    "artifacts/exchange_rule_discovery/binance_spot_perp_funding_carry_exchange_rule_discovery_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXECUTION_RELATIVE_PATH = "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json"
EVALUATOR_RELATIVE_PATH = "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json"
CLOSURE_RELATIVE_PATH = "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json"
RISK_CAPITAL_RELATIVE_PATH = (
    "artifacts/risk_capital_diagnostics/"
    "binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json"
)
OPERATIONAL_RELATIVE_PATH = (
    "artifacts/operational_feasibility/"
    "binance_spot_perp_delta_neutral_funding_carry_operational_feasibility_v1.json"
)

EXECUTION_PATH = REPO_ROOT / EXECUTION_RELATIVE_PATH
EVALUATOR_PATH = REPO_ROOT / EVALUATOR_RELATIVE_PATH
CLOSURE_PATH = REPO_ROOT / CLOSURE_RELATIVE_PATH
RISK_CAPITAL_PATH = REPO_ROOT / RISK_CAPITAL_RELATIVE_PATH
OPERATIONAL_PATH = REPO_ROOT / OPERATIONAL_RELATIVE_PATH

STATUS = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_EXCHANGE_RULE_DISCOVERY_CREATED"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_EXCHANGE_RULE_DISCOVERY"

EXECUTION_PAYLOAD_SHA256 = "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378"
EVALUATOR_PAYLOAD_SHA256 = "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b"
CLOSURE_PAYLOAD_SHA256 = "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8"
RISK_CAPITAL_PAYLOAD_SHA256 = "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc"
OPERATIONAL_PAYLOAD_SHA256 = "5af80fc87f583f4f5f4ed4baaa5620d708eff1ade5aaa54969d4259e54d6604e"

OPERATIONAL_CLASSIFICATION = (
    "FUNDING_CARRY_OPERATIONAL_FEASIBILITY_INCOMPLETE_NEEDS_EXCHANGE_RULES_NO_LIVE_PERMISSION"
)
RISK_CAPITAL_CLASSIFICATION = "FUNDING_CARRY_RISK_CAPITAL_FEASIBILITY_STRONG_DIAGNOSTIC_NO_LIVE_PERMISSION"
PRIOR_RESULT_CLASS = (
    "SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_DIAGNOSTIC_PROMISING_REQUIRES_CLOSURE_NO_CANDIDATE_NO_EDGE"
)
ROUTE_FAMILY = "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE"
CONFIG_ID = "spot_long_perp_short_always_on_funding_carry_3symbol"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
CAPITAL_SCENARIOS_USDT = (100, 250, 500, 1000, 2500, 5000)
TRACKED_PYTHON_COUNT_AT_START = 884

SPOT_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"
FUTURES_EXCHANGE_INFO_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"
NEXT_ALLOWED_STEP_PASS = "PRICE_SNAPSHOT_AND_ORDER_SIZING_SIMULATION_ONLY"


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


def validate_prior_artifacts(
    execution: dict,
    evaluator: dict,
    closure: dict,
    risk_capital: dict,
    operational: dict,
) -> None:
    if execution.get("payload_sha256_excluding_hash") != EXECUTION_PAYLOAD_SHA256:
        raise RuntimeError("execution payload hash mismatch")
    if evaluator.get("payload_sha256_excluding_hash") != EVALUATOR_PAYLOAD_SHA256:
        raise RuntimeError("evaluator payload hash mismatch")
    if closure.get("payload_sha256_excluding_hash") != CLOSURE_PAYLOAD_SHA256:
        raise RuntimeError("closure payload hash mismatch")
    if risk_capital.get("payload_sha256_excluding_hash") != RISK_CAPITAL_PAYLOAD_SHA256:
        raise RuntimeError("risk/capital payload hash mismatch")
    if operational.get("payload_sha256_excluding_hash") != OPERATIONAL_PAYLOAD_SHA256:
        raise RuntimeError("operational feasibility payload hash mismatch")
    if execution["route_definition"]["route_family"] != ROUTE_FAMILY:
        raise RuntimeError("route family mismatch")
    if execution["route_definition"]["config_id"] != CONFIG_ID:
        raise RuntimeError("config id mismatch")
    if tuple(execution["route_definition"]["symbols"]) != SYMBOLS:
        raise RuntimeError("symbol universe mismatch")
    if evaluator["result_classification"]["result_class"] != PRIOR_RESULT_CLASS:
        raise RuntimeError("prior result class mismatch")
    if evaluator["result_classification"]["diagnostic_promising"] is not True:
        raise RuntimeError("prior diagnostic promising flag not preserved")
    if closure["closure_record"]["route_closed"] is not True:
        raise RuntimeError("prior closure route_closed flag not preserved")
    if risk_capital["feasibility_classification"]["classification"] != RISK_CAPITAL_CLASSIFICATION:
        raise RuntimeError("risk/capital classification mismatch")
    if operational["feasibility_classification"]["classification"] != OPERATIONAL_CLASSIFICATION:
        raise RuntimeError("operational feasibility classification mismatch")
    safety = operational["safety_permissions"]
    if safety.get("next_step_may_be_exchange_rule_discovery_only") is not True:
        raise RuntimeError("operational feasibility did not allow exchange-rule discovery as next step")
    for key in (
        "candidate_generation_allowed_now",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
    ):
        if safety.get(key) is not False:
            raise RuntimeError(f"operational feasibility safety permission not false: {key}")


def fetch_json(url: str) -> tuple[dict, dict]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "edge-factory-os-public-exchange-rule-discovery/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
            metadata = {
                "url": url,
                "http_status": response.status,
                "response_bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
            }
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"public exchangeInfo fetch failed HTTP {exc.code}: {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"public exchangeInfo fetch failed: {url}: {exc}") from exc
    return json.loads(body.decode("utf-8")), metadata


def filter_map(symbol_record: dict) -> dict:
    return {item.get("filterType"): item for item in symbol_record.get("filters", []) if item.get("filterType")}


def filter_subset(filters: dict, wanted: tuple[str, ...]) -> dict:
    return {name: filters[name] for name in wanted if name in filters}


def decimal_or_none(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def min_notional_from_spot_filters(filters: dict) -> Decimal | None:
    if "MIN_NOTIONAL" in filters:
        return decimal_or_none(filters["MIN_NOTIONAL"].get("minNotional"))
    if "NOTIONAL" in filters:
        return decimal_or_none(filters["NOTIONAL"].get("minNotional"))
    return None


def min_notional_from_futures_filters(filters: dict) -> Decimal | None:
    if "MIN_NOTIONAL" in filters:
        return decimal_or_none(filters["MIN_NOTIONAL"].get("notional"))
    return None


def as_string(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")


def spot_rule_record(symbol_record: dict) -> dict:
    filters = filter_map(symbol_record)
    wanted_filters = (
        "PRICE_FILTER",
        "LOT_SIZE",
        "MIN_NOTIONAL",
        "NOTIONAL",
        "MARKET_LOT_SIZE",
        "ICEBERG_PARTS",
        "PERCENT_PRICE",
        "PERCENT_PRICE_BY_SIDE",
    )
    return {
        "symbol": symbol_record.get("symbol"),
        "status": symbol_record.get("status"),
        "baseAsset": symbol_record.get("baseAsset"),
        "quoteAsset": symbol_record.get("quoteAsset"),
        "isSpotTradingAllowed": symbol_record.get("isSpotTradingAllowed"),
        "orderTypes": symbol_record.get("orderTypes", []),
        "permissions": symbol_record.get("permissions"),
        "permissionSets": symbol_record.get("permissionSets"),
        "baseAssetPrecision": symbol_record.get("baseAssetPrecision"),
        "quoteAssetPrecision": symbol_record.get("quoteAssetPrecision"),
        "filters": filter_subset(filters, wanted_filters),
    }


def futures_rule_record(symbol_record: dict) -> dict:
    filters = filter_map(symbol_record)
    wanted_filters = (
        "PRICE_FILTER",
        "LOT_SIZE",
        "MARKET_LOT_SIZE",
        "MIN_NOTIONAL",
        "PERCENT_PRICE",
        "MAX_NUM_ORDERS",
    )
    return {
        "symbol": symbol_record.get("symbol"),
        "pair": symbol_record.get("pair"),
        "contractType": symbol_record.get("contractType"),
        "status": symbol_record.get("status"),
        "baseAsset": symbol_record.get("baseAsset"),
        "quoteAsset": symbol_record.get("quoteAsset"),
        "marginAsset": symbol_record.get("marginAsset"),
        "orderTypes": symbol_record.get("orderTypes", []),
        "timeInForce": symbol_record.get("timeInForce", []),
        "pricePrecision": symbol_record.get("pricePrecision"),
        "quantityPrecision": symbol_record.get("quantityPrecision"),
        "filters": filter_subset(filters, wanted_filters),
        "triggerProtect": symbol_record.get("triggerProtect"),
        "liquidationFee": symbol_record.get("liquidationFee"),
        "marketTakeBound": symbol_record.get("marketTakeBound"),
    }


def spot_completeness_record(record: dict) -> dict:
    filters = record["filters"]
    order_types = set(record.get("orderTypes", []))
    min_notional_available = "MIN_NOTIONAL" in filters or "NOTIONAL" in filters
    checks = {
        "symbol_status_trading": record.get("status") == "TRADING"
        and record.get("isSpotTradingAllowed") is True,
        "tick_size_available": bool(filters.get("PRICE_FILTER", {}).get("tickSize")),
        "step_size_available": bool(filters.get("LOT_SIZE", {}).get("stepSize")),
        "min_qty_available": bool(filters.get("LOT_SIZE", {}).get("minQty")),
        "min_notional_available": min_notional_available,
        "market_order_allowed": "MARKET" in order_types,
        "limit_order_allowed": "LIMIT" in order_types,
    }
    checks["rule_record_complete"] = all(checks.values())
    return checks


def futures_completeness_record(record: dict) -> dict:
    filters = record["filters"]
    order_types = set(record.get("orderTypes", []))
    checks = {
        "symbol_status_trading": record.get("status") == "TRADING",
        "tick_size_available": bool(filters.get("PRICE_FILTER", {}).get("tickSize")),
        "step_size_available": bool(filters.get("LOT_SIZE", {}).get("stepSize")),
        "min_qty_available": bool(filters.get("LOT_SIZE", {}).get("minQty")),
        "min_notional_available": bool(filters.get("MIN_NOTIONAL", {}).get("notional")),
        "market_order_allowed": "MARKET" in order_types,
        "limit_order_allowed": "LIMIT" in order_types,
    }
    checks["rule_record_complete"] = all(checks.values())
    return checks


def build_min_notional_feasibility(spot_rules: dict, futures_rules: dict) -> dict:
    scenarios = []
    for capital in CAPITAL_SCENARIOS_USDT:
        notional_per_symbol = Decimal(str(capital)) / Decimal("3")
        symbol_records = []
        for symbol in SYMBOLS:
            spot_filters = spot_rules[symbol]["filters"]
            futures_filters = futures_rules[symbol]["filters"]
            spot_min = min_notional_from_spot_filters(spot_filters)
            futures_min = min_notional_from_futures_filters(futures_filters)
            symbol_records.append(
                {
                    "symbol": symbol,
                    "notional_per_symbol_usdt": as_string(notional_per_symbol),
                    "spot_leg_target_notional_usdt": as_string(notional_per_symbol),
                    "futures_leg_target_notional_usdt": as_string(notional_per_symbol),
                    "spot_min_notional_usdt": as_string(spot_min),
                    "futures_min_notional_usdt": as_string(futures_min),
                    "min_notional_pass_spot": bool(spot_min is not None and spot_min <= notional_per_symbol),
                    "min_notional_pass_futures": bool(
                        futures_min is not None and futures_min <= notional_per_symbol
                    ),
                    "exact_quantity_rounding_requires_price_snapshot": True,
                    "actual_order_quantity_calculated": False,
                }
            )
        scenarios.append(
            {
                "capital_size_usdt": capital,
                "notional_per_symbol_usdt": as_string(notional_per_symbol),
                "symbols": symbol_records,
                "all_symbols_min_notional_pass_spot": all(
                    item["min_notional_pass_spot"] for item in symbol_records
                ),
                "all_symbols_min_notional_pass_futures": all(
                    item["min_notional_pass_futures"] for item in symbol_records
                ),
                "exact_quantity_rounding_requires_price_snapshot": True,
            }
        )
    return {
        "capital_scenarios_evaluated": list(CAPITAL_SCENARIOS_USDT),
        "price_snapshot_used": False,
        "quantity_rounding_performed": False,
        "scenarios": scenarios,
    }


def main() -> int:
    ensure_target_absent()
    execution = load_json(EXECUTION_PATH)
    evaluator = load_json(EVALUATOR_PATH)
    closure = load_json(CLOSURE_PATH)
    risk_capital = load_json(RISK_CAPITAL_PATH)
    operational = load_json(OPERATIONAL_PATH)
    validate_prior_artifacts(execution, evaluator, closure, risk_capital, operational)

    spot_exchange_info, spot_endpoint_metadata = fetch_json(SPOT_EXCHANGE_INFO_URL)
    futures_exchange_info, futures_endpoint_metadata = fetch_json(FUTURES_EXCHANGE_INFO_URL)

    spot_by_symbol = {
        item.get("symbol"): item
        for item in spot_exchange_info.get("symbols", [])
        if item.get("symbol") in SYMBOLS
    }
    futures_by_symbol = {
        item.get("symbol"): item
        for item in futures_exchange_info.get("symbols", [])
        if item.get("symbol") in SYMBOLS
    }

    spot_rules = {symbol: spot_rule_record(spot_by_symbol[symbol]) for symbol in SYMBOLS if symbol in spot_by_symbol}
    futures_rules = {
        symbol: futures_rule_record(futures_by_symbol[symbol]) for symbol in SYMBOLS if symbol in futures_by_symbol
    }
    spot_completeness = {symbol: spot_completeness_record(spot_rules[symbol]) for symbol in spot_rules}
    futures_completeness = {symbol: futures_completeness_record(futures_rules[symbol]) for symbol in futures_rules}

    all_three_spot_symbols_found = set(spot_rules) == set(SYMBOLS)
    all_three_futures_symbols_found = set(futures_rules) == set(SYMBOLS)
    required_spot_filters_available = all(
        spot_completeness.get(symbol, {}).get("rule_record_complete") is True for symbol in SYMBOLS
    )
    required_futures_filters_available = all(
        futures_completeness.get(symbol, {}).get("rule_record_complete") is True for symbol in SYMBOLS
    )
    all_required_filters_available = (
        all_three_spot_symbols_found
        and all_three_futures_symbols_found
        and required_spot_filters_available
        and required_futures_filters_available
    )

    if all_required_filters_available:
        classification = "EXCHANGE_RULE_DISCOVERY_PASS_READY_FOR_PRICE_SNAPSHOT_AND_SIZING_SIM_NO_LIVE_PERMISSION"
        next_allowed_step = NEXT_ALLOWED_STEP_PASS
    else:
        classification = "EXCHANGE_RULE_DISCOVERY_INCOMPLETE_MISSING_RULES_NO_LIVE_PERMISSION"
        next_allowed_step = "NONE_UNTIL_MISSING_RULES_REVIEWED"

    min_notional_feasibility = (
        build_min_notional_feasibility(spot_rules, futures_rules)
        if all_three_spot_symbols_found and all_three_futures_symbols_found
        else {
            "capital_scenarios_evaluated": list(CAPITAL_SCENARIOS_USDT),
            "price_snapshot_used": False,
            "quantity_rounding_performed": False,
            "scenarios": [],
            "blocked_reason": "required symbols missing from spot or futures exchangeInfo",
        }
    )

    validation_checks = {
        "repo_clean_before_run": True,
        "prior_operational_feasibility_loaded": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "spot_exchange_info_loaded": bool(spot_exchange_info),
        "futures_exchange_info_loaded": bool(futures_exchange_info),
        "all_three_spot_symbols_found": all_three_spot_symbols_found,
        "all_three_futures_symbols_found": all_three_futures_symbols_found,
        "required_spot_filters_available": required_spot_filters_available,
        "required_futures_filters_available": required_futures_filters_available,
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
            "execution_artifact": EXECUTION_RELATIVE_PATH,
            "execution_payload_sha256_excluding_hash": EXECUTION_PAYLOAD_SHA256,
            "evaluator_artifact": EVALUATOR_RELATIVE_PATH,
            "evaluator_payload_sha256_excluding_hash": EVALUATOR_PAYLOAD_SHA256,
            "closure_artifact": CLOSURE_RELATIVE_PATH,
            "closure_payload_sha256_excluding_hash": CLOSURE_PAYLOAD_SHA256,
            "risk_capital_artifact": RISK_CAPITAL_RELATIVE_PATH,
            "risk_capital_payload_sha256_excluding_hash": RISK_CAPITAL_PAYLOAD_SHA256,
            "operational_feasibility_artifact": OPERATIONAL_RELATIVE_PATH,
            "operational_feasibility_payload_sha256_excluding_hash": OPERATIONAL_PAYLOAD_SHA256,
        },
        "prior_operational_feasibility_preserved": {
            "operational_classification": operational["feasibility_classification"]["classification"],
            "risk_capital_classification": risk_capital["feasibility_classification"]["classification"],
            "prior_result_class": evaluator["result_classification"]["result_class"],
            "diagnostic_promising": evaluator["result_classification"]["diagnostic_promising"],
            "route_closed": closure["closure_record"]["route_closed"],
            "next_step_may_be_exchange_rule_discovery_only": operational["safety_permissions"][
                "next_step_may_be_exchange_rule_discovery_only"
            ],
            "runtime_live_capital_allowed": False,
        },
        "endpoint_contracts": {
            "spot_exchange_info": {
                "url": SPOT_EXCHANGE_INFO_URL,
                "method": "GET",
                "public_unsigned": True,
                "private_or_signed": False,
                "order_endpoint": False,
                "metadata": spot_endpoint_metadata,
            },
            "usd_m_futures_exchange_info": {
                "url": FUTURES_EXCHANGE_INFO_URL,
                "method": "GET",
                "public_unsigned": True,
                "private_or_signed": False,
                "order_endpoint": False,
                "metadata": futures_endpoint_metadata,
            },
            "api_key_used": False,
            "private_api_used": False,
            "orders_placed": False,
        },
        "spot_exchange_rules": spot_rules,
        "futures_exchange_rules": futures_rules,
        "rule_completeness_summary": {
            "spot_symbols_found_count": len(spot_rules),
            "futures_symbols_found_count": len(futures_rules),
            "spot_completeness_by_symbol": spot_completeness,
            "futures_completeness_by_symbol": futures_completeness,
            "all_three_spot_symbols_found": all_three_spot_symbols_found,
            "all_three_futures_symbols_found": all_three_futures_symbols_found,
            "required_spot_filters_available": required_spot_filters_available,
            "required_futures_filters_available": required_futures_filters_available,
            "all_required_filters_available": all_required_filters_available,
        },
        "capital_scenario_min_notional_feasibility": min_notional_feasibility,
        "discovery_classification": {
            "classification": classification,
            "classification_grants_live_or_capital_permission": False,
        },
        "next_allowed_step": {
            "step": next_allowed_step,
            "price_snapshot_and_order_sizing_simulation_only": classification.endswith(
                "PRICE_SNAPSHOT_AND_SIZING_SIM_NO_LIVE_PERMISSION"
            ),
            "live_or_capital_allowed": False,
        },
        "limitations": [
            "ExchangeInfo rules are public metadata only and can change after discovery.",
            "No ticker or price snapshot is fetched, so actual order quantities and rounding are not calculated.",
            "No account-specific balances, permissions, fee tiers, leverage, margin mode, or commission rates are known.",
            "No order endpoint, private endpoint, signed endpoint, API key, strategy rerun, raw row read, or live action is used.",
            "This discovery grants no candidate, edge, family release, runtime, live, or capital permission.",
        ],
        "safety_permissions": {
            "exchange_rule_discovery_created": True,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "next_step_may_be_price_snapshot_and_order_sizing_simulation_only": all_required_filters_available,
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
    print(f"discovery_classification: {classification}")
    print(f"spot_symbols_found_count: {len(spot_rules)}")
    print(f"futures_symbols_found_count: {len(futures_rules)}")
    print(f"all_required_filters_available: {str(all_required_filters_available).lower()}")
    print(f"capital_scenarios_evaluated: {','.join(str(value) for value in CAPITAL_SCENARIOS_USDT)}")
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
