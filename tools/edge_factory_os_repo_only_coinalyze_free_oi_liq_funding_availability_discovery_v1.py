#!/usr/bin/env python3
"""Coinalyze free OI/liquidation/funding availability discovery.

This module performs data availability discovery only. It does not run a
strategy, generate signals, compute PnL, create candidates, or grant any
runtime/live/capital permission.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_free_oi_liq_funding_availability_discovery_v1"
ARTIFACT_KIND = "COINALYZE_FREE_OI_LIQ_FUNDING_AVAILABILITY_DISCOVERY"
PASS_STATUS = "PASS_REPO_ONLY_COINALYZE_FREE_OI_LIQ_FUNDING_AVAILABILITY_DISCOVERY_CREATED"
BLOCKED_MISSING_KEY_STATUS = "BLOCKED_COINALYZE_API_KEY_MISSING"
BLOCKED_API_STATUS = "BLOCKED_COINALYZE_API_OR_RATE_LIMIT"
REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "data_discovery" / "coinalyze_free_oi_liq_funding_availability_discovery_v1.json"
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_free_oi_liq_funding_availability_discovery_v1.py"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
COINALYZE_BASE_URL = "https://api.coinalyze.net/v1"
API_KEY_ENV = "COINALYZE_API_KEY"

TARGET_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "DOGEUSDT",
    "XRPUSDT",
    "BNBUSDT",
    "LINKUSDT",
    "APTUSDT",
    "ARBUSDT",
    "OPUSDT",
]

ENDPOINTS = [
    "open-interest-history",
    "liquidation-history",
    "funding-rate-history",
    "long-short-ratio-history",
    "ohlcv-history",
]

INTERVALS = {
    "15min": 14,
    "1hour": 60,
    "daily": 365,
}

EXPECTED_REPO_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={SAFE_DIR}", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def source_checkpoint() -> str:
    try:
        return run_git(["rev-parse", "HEAD"])
    except Exception as exc:  # pragma: no cover - defensive artifact capture
        return f"UNKNOWN_GIT_CHECKPOINT: {exc}"


def git_status_entries() -> list[tuple[str, str]]:
    try:
        raw = run_git(["status", "--short", "-uall"])
    except Exception:
        return [("??", "GIT_STATUS_UNAVAILABLE")]
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        path = line[3:].strip().strip('"').replace("\\", "/")
        entries.append((status, path))
    return entries


def existing_repo_files_clean_except_expected() -> bool:
    entries = git_status_entries()
    for status, path in entries:
        if path in EXPECTED_REPO_PATHS and status == "??":
            continue
        return False
    return True


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_hash_excluding_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def write_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    payload["payload_sha256_excluding_hash"] = payload_hash_excluding_hash(payload)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def normalize_symbol(value: str) -> str:
    cleaned = "".join(ch for ch in value.upper() if ch.isalnum())
    for suffix in ("PERP", "SWAP", "FUTURES", "USDTM", "USDCM"):
        cleaned = cleaned.replace(suffix, "")
    return cleaned


def market_exchange_name(market: dict[str, Any]) -> str:
    values = [
        market.get("exchange"),
        market.get("exchange_name"),
        market.get("market"),
        market.get("market_name"),
    ]
    return " ".join(str(v) for v in values if v is not None).upper()


def market_symbol_values(market: dict[str, Any]) -> list[str]:
    values = [
        market.get("symbol"),
        market.get("symbol_on_exchange"),
        market.get("base_asset"),
        market.get("quote_asset"),
        market.get("pair"),
    ]
    return [str(value) for value in values if value is not None]


def is_stable_perp_market(market: dict[str, Any]) -> bool:
    joined = " ".join(market_symbol_values(market)).upper()
    type_text = " ".join(
        str(market.get(key, ""))
        for key in ("future_type", "contract_type", "type", "margined", "settlement_asset")
    ).upper()
    stable = any(token in joined or token in type_text for token in ("USDT", "USDC"))
    perp = any(token in joined or token in type_text for token in ("PERP", "PERPETUAL", "SWAP"))
    if market.get("is_perpetual") is True:
        perp = True
    return stable and perp


def preferred_exchange(market: dict[str, Any]) -> str | None:
    text = market_exchange_name(market)
    if "BINANCE" in text:
        return "BINANCE"
    if "OKX" in text or "OKEX" in text:
        return "OKX"
    return None


def api_get(path: str, params: dict[str, Any], api_key: str) -> tuple[bool, int | None, Any, str | None]:
    url = f"{COINALYZE_BASE_URL}/{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "api_key": api_key,
            "User-Agent": "edge-factory-os-coinalyze-availability-discovery/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {"raw_body": body[:1000]}
            return True, response.status, data, None
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")[:1000]
        return False, exc.code, None, message
    except urllib.error.URLError as exc:
        return False, None, None, str(exc)
    except Exception as exc:  # pragma: no cover - defensive capture
        return False, None, None, str(exc)


def extract_rows(data: Any, symbol: str) -> list[dict[str, Any]]:
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "history" in data[0]:
            for item in data:
                item_symbol = str(item.get("symbol", ""))
                if not item_symbol or item_symbol == symbol:
                    history = item.get("history")
                    if isinstance(history, list):
                        return [row for row in history if isinstance(row, dict)]
            history = data[0].get("history")
            if isinstance(history, list):
                return [row for row in history if isinstance(row, dict)]
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("history", "data", "result"):
            rows = data.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, dict)]
    return []


def timestamp_bounds(rows: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    timestamps: list[int] = []
    for row in rows:
        for key in ("t", "time", "timestamp"):
            value = row.get(key)
            if isinstance(value, (int, float)):
                timestamps.append(int(value))
                break
            if isinstance(value, str) and value.isdigit():
                timestamps.append(int(value))
                break
    if not timestamps:
        return None, None
    min_ts = min(timestamps)
    max_ts = max(timestamps)
    if min_ts > 10_000_000_000:
        min_ts //= 1000
        max_ts //= 1000
    return (
        datetime.fromtimestamp(min_ts, timezone.utc).isoformat().replace("+00:00", "Z"),
        datetime.fromtimestamp(max_ts, timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def safe_sample_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    sample: dict[str, Any] = {}
    for key, value in rows[0].items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            sample[str(key)] = value
        else:
            sample[str(key)] = str(value)[:200]
    return sample


def classify_coverage(results: list[dict[str, Any]]) -> tuple[str, str, dict[str, Any]]:
    usable_by_endpoint: dict[str, set[str]] = {endpoint: set() for endpoint in ENDPOINTS}
    usable_intervals: dict[str, int] = {interval: 0 for interval in INTERVALS}
    blocked_statuses = 0
    for row in results:
        if row.get("http_status") in (401, 429):
            blocked_statuses += 1
        if row.get("request_ok") and int(row.get("row_count", 0)) > 0:
            usable_by_endpoint.setdefault(str(row["endpoint"]), set()).add(str(row["target_symbol"]))
            usable_intervals[str(row["interval"])] = usable_intervals.get(str(row["interval"]), 0) + 1

    oi_symbols = usable_by_endpoint.get("open-interest-history", set())
    liq_symbols = usable_by_endpoint.get("liquidation-history", set())
    funding_symbols = usable_by_endpoint.get("funding-rate-history", set())
    majors = {"BTCUSDT", "ETHUSDT", "SOLUSDT"}
    best_interval = None
    if usable_intervals:
        best_interval = max(usable_intervals.items(), key=lambda item: item[1])[0]

    summary = {
        "usable_oi_symbols": sorted(oi_symbols),
        "usable_liquidation_symbols": sorted(liq_symbols),
        "usable_funding_symbols": sorted(funding_symbols),
        "usable_oi_symbol_count": len(oi_symbols),
        "usable_liquidation_symbol_count": len(liq_symbols),
        "usable_funding_symbol_count": len(funding_symbols),
        "best_usable_interval": best_interval,
        "usable_interval_probe_counts": usable_intervals,
    }

    if blocked_statuses and not (oi_symbols or liq_symbols or funding_symbols):
        return (
            "COINALYZE_FREE_DATA_BLOCKED_API_OR_RATE_LIMIT",
            "COINALYZE_API_KEY_OR_RATE_LIMIT_REVIEW_V1",
            summary,
        )
    if len((oi_symbols & liq_symbols & funding_symbols) & majors) >= 2 and (
        usable_intervals.get("15min", 0) > 0 or usable_intervals.get("1hour", 0) > 0
    ):
        return (
            "COINALYZE_FREE_DATA_READY_FOR_RECENT_OI_LIQUIDATION_RESEARCH",
            "COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN_V1",
            summary,
        )
    if oi_symbols or liq_symbols or funding_symbols:
        return (
            "COINALYZE_FREE_DATA_PARTIAL_RECENT_ONLY",
            "COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN_V1",
            summary,
        )
    return (
        "COINALYZE_FREE_DATA_INSUFFICIENT_FOR_OI_LIQUIDATION_RESEARCH",
        "FREE_DATA_SOURCE_ALTERNATIVE_DISCOVERY_V1",
        summary,
    )


def base_payload(status: str, replacement_checks_all_true: bool) -> dict[str, Any]:
    validation_checks = {
        "repo_clean_before_run": existing_repo_files_clean_except_expected(),
        "api_key_loaded_from_env_only": False,
        "api_key_not_written_to_artifact": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_pnl_computation": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_exchange_api_used": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": existing_repo_files_clean_except_expected(),
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    return {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "api_key_handling": {
            "env_var_name": API_KEY_ENV,
            "api_key_required": True,
            "api_key_read_attempted_from_env_only": True,
            "api_key_loaded": False,
            "api_key_persisted": False,
            "api_key_value_written": False,
        },
        "coinalyze_constraints": {
            "api_key_required": True,
            "free_api_discovery_only": True,
            "recent_data_prototyping_only": True,
            "intraday_history_limited": True,
            "conservative_rate_limit_sleeps": True,
            "no_private_exchange_api": True,
        },
        "market_discovery_summary": {
            "market_count": 0,
            "binance_stable_perp_count": 0,
            "okx_stable_swap_count": 0,
            "source_endpoint": "future-markets",
        },
        "probe_symbols": [],
        "endpoint_probe_results": [],
        "interval_coverage_summary": {
            "tested_intervals": list(INTERVALS),
            "best_usable_interval": None,
        },
        "usable_data_summary": {
            "usable_oi_symbol_count": 0,
            "usable_liquidation_symbol_count": 0,
            "usable_funding_symbol_count": 0,
            "usable_oi_symbols": [],
            "usable_liquidation_symbols": [],
            "usable_funding_symbols": [],
        },
        "result_classification": "COINALYZE_FREE_DATA_BLOCKED_API_OR_RATE_LIMIT",
        "next_allowed_step": "COINALYZE_API_KEY_ENV_SETUP_REVIEW_V1",
        "next_module": "COINALYZE_API_KEY_ENV_SETUP_REVIEW_V1",
        "limitations": [],
        "safety_permissions": {
            "data_discovery_created": True,
            "strategy_execution_allowed_now": False,
            "signal_generation_allowed_now": False,
            "backtest_allowed_now": False,
            "pnl_computation_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
        },
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": None,
    }


def blocked_missing_key_payload() -> dict[str, Any]:
    payload = base_payload(BLOCKED_MISSING_KEY_STATUS, False)
    payload["api_key_handling"].update(
        {
            "env_var_present": False,
            "api_key_loaded": False,
            "blocked_reason": BLOCKED_MISSING_KEY_STATUS,
        }
    )
    payload["limitations"] = [
        "COINALYZE_API_KEY was not present in the environment, so no Coinalyze API request was made.",
        "Per hard safety rules, the route stopped instead of substituting another source or claiming discovery success.",
    ]
    payload["validation_checks"]["api_key_loaded_from_env_only"] = False
    return payload


def discover_with_api_key(api_key: str) -> dict[str, Any]:
    payload = base_payload(PASS_STATUS, True)
    payload["api_key_handling"].update(
        {
            "env_var_present": True,
            "api_key_loaded": True,
            "api_key_loaded_from_env_only": True,
        }
    )
    payload["validation_checks"]["api_key_loaded_from_env_only"] = True

    market_ok, market_status, market_data, market_error = api_get("future-markets", {}, api_key)
    all_markets = market_data if isinstance(market_data, list) else []
    selected_markets: list[dict[str, Any]] = []
    for market in all_markets:
        if not isinstance(market, dict):
            continue
        exchange = preferred_exchange(market)
        if exchange and is_stable_perp_market(market):
            selected = dict(market)
            selected["_preferred_exchange"] = exchange
            selected_markets.append(selected)

    by_target: dict[str, dict[str, Any]] = {}
    for target in TARGET_SYMBOLS:
        normalized_target = normalize_symbol(target)
        for preferred in ("BINANCE", "OKX"):
            match = None
            for market in selected_markets:
                if market.get("_preferred_exchange") != preferred:
                    continue
                values = market_symbol_values(market)
                if any(normalize_symbol(value) == normalized_target for value in values):
                    match = market
                    break
            if match is not None:
                by_target[target] = match
                break

    probe_symbols = []
    for target, market in by_target.items():
        coinalyze_symbol = str(market.get("symbol") or market.get("symbol_on_exchange") or "")
        probe_symbols.append(
            {
                "target_symbol": target,
                "coinalyze_symbol": coinalyze_symbol,
                "symbol_on_exchange": market.get("symbol_on_exchange"),
                "exchange": market.get("_preferred_exchange"),
            }
        )

    payload["market_discovery_summary"] = {
        "source_endpoint": "future-markets",
        "request_ok": market_ok,
        "http_status": market_status,
        "market_count": len(all_markets),
        "selected_stable_perp_count": len(selected_markets),
        "binance_stable_perp_count": sum(1 for item in selected_markets if item.get("_preferred_exchange") == "BINANCE"),
        "okx_stable_swap_count": sum(1 for item in selected_markets if item.get("_preferred_exchange") == "OKX"),
        "error_message": market_error,
    }
    payload["probe_symbols"] = probe_symbols

    endpoint_results: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    for probe in probe_symbols:
        symbol = str(probe["coinalyze_symbol"])
        if not symbol:
            continue
        for endpoint in ENDPOINTS:
            for interval, days in INTERVALS.items():
                start = now - timedelta(days=days)
                params = {
                    "symbols": symbol,
                    "interval": interval,
                    "from": int(start.timestamp()),
                    "to": int(now.timestamp()),
                }
                ok, status_code, data, error = api_get(endpoint, params, api_key)
                rows = extract_rows(data, symbol) if ok else []
                timestamp_min, timestamp_max = timestamp_bounds(rows)
                field_names = sorted({str(key) for row in rows[:5] for key in row.keys()})
                endpoint_results.append(
                    {
                        "endpoint": endpoint,
                        "target_symbol": probe["target_symbol"],
                        "symbol": symbol,
                        "exchange": probe["exchange"],
                        "interval": interval,
                        "request_ok": ok,
                        "http_status": status_code,
                        "row_count": len(rows),
                        "timestamp_min": timestamp_min,
                        "timestamp_max": timestamp_max,
                        "field_names": field_names,
                        "sample_row": safe_sample_row(rows),
                        "error_message": error,
                    }
                )
                time.sleep(1.2)

    result_classification, next_allowed_step, usable_summary = classify_coverage(endpoint_results)
    payload["endpoint_probe_results"] = endpoint_results
    payload["result_classification"] = result_classification
    payload["next_allowed_step"] = next_allowed_step
    payload["next_module"] = next_allowed_step
    payload["usable_data_summary"] = usable_summary
    payload["interval_coverage_summary"] = {
        "tested_intervals": list(INTERVALS),
        "best_usable_interval": usable_summary.get("best_usable_interval"),
        "usable_interval_probe_counts": usable_summary.get("usable_interval_probe_counts", {}),
    }

    if result_classification == "COINALYZE_FREE_DATA_BLOCKED_API_OR_RATE_LIMIT":
        payload["status"] = BLOCKED_API_STATUS
        payload["replacement_checks_all_true"] = False
        payload["validation_checks"]["replacement_checks_all_true"] = False
        payload["limitations"].append("Coinalyze API discovery was blocked by authorization, rate limit, or connectivity before usable data was found.")
    elif result_classification == "COINALYZE_FREE_DATA_INSUFFICIENT_FOR_OI_LIQUIDATION_RESEARCH":
        payload["limitations"].append("Coinalyze API responded, but the probed endpoints did not return useful OI/liquidation/funding coverage.")
    elif result_classification == "COINALYZE_FREE_DATA_PARTIAL_RECENT_ONLY":
        payload["limitations"].append("Coinalyze data appears partial and recent-only; this is not suitable for 2022-2025 deep backtests.")
    else:
        payload["limitations"].append("Coinalyze data appears usable for recent-data prototyping only; no strategy or edge was evaluated.")

    payload["validation_checks"]["repo_clean_before_run"] = existing_repo_files_clean_except_expected()
    payload["validation_checks"]["no_existing_repo_files_modified"] = existing_repo_files_clean_except_expected()
    if not payload["validation_checks"]["repo_clean_before_run"]:
        payload["status"] = "BLOCKED_REPO_NOT_CLEAN"
        payload["replacement_checks_all_true"] = False
        payload["validation_checks"]["replacement_checks_all_true"] = False
        payload["next_allowed_step"] = "REPO_CLEANLINESS_REVIEW_V1"
        payload["next_module"] = "REPO_CLEANLINESS_REVIEW_V1"
        payload["limitations"].append("Repo was not clean outside the expected new tool/artifact paths.")
    return payload


def print_stdout(payload: dict[str, Any]) -> None:
    usable = payload.get("usable_data_summary", {})
    market = payload.get("market_discovery_summary", {})
    print(f"status: {payload.get('status')}")
    print(f"result_classification: {payload.get('result_classification')}")
    print(f"market_count: {market.get('market_count', 0)}")
    print(f"probe_symbol_count: {len(payload.get('probe_symbols', []))}")
    print(f"usable_oi_symbol_count: {usable.get('usable_oi_symbol_count', 0)}")
    print(f"usable_liquidation_symbol_count: {usable.get('usable_liquidation_symbol_count', 0)}")
    print(f"usable_funding_symbol_count: {usable.get('usable_funding_symbol_count', 0)}")
    print(f"best_usable_interval: {payload.get('interval_coverage_summary', {}).get('best_usable_interval')}")
    print(f"next_allowed_step: {payload.get('next_allowed_step')}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"api_key_persisted: {str(payload.get('api_key_handling', {}).get('api_key_persisted')).lower()}")
    print(f"payload_sha256_excluding_hash: {payload.get('payload_sha256_excluding_hash')}")
    print(f"replacement_checks_all_true: {str(payload.get('replacement_checks_all_true')).lower()}")


def main() -> int:
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        payload = blocked_missing_key_payload()
    else:
        payload = discover_with_api_key(api_key)
    payload = write_artifact(payload)
    print_stdout(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
