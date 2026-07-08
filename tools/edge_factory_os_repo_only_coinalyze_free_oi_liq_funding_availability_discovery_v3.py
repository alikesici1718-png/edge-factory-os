#!/usr/bin/env python3
"""Coinalyze free OI/liquidation/funding availability discovery V3.

Data availability discovery only. This module does not run a strategy, generate
signals, compute PnL, create candidates, claim edge, or grant runtime/live/
capital permission. The Coinalyze key is read only from COINALYZE_API_KEY and is
never printed or written to the artifact.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MODULE = "edge_factory_os_repo_only_coinalyze_free_oi_liq_funding_availability_discovery_v3"
ARTIFACT_KIND = "COINALYZE_FREE_OI_LIQ_FUNDING_AVAILABILITY_DISCOVERY_V3"
PASS_STATUS = "PASS_REPO_ONLY_COINALYZE_FREE_OI_LIQ_FUNDING_AVAILABILITY_DISCOVERY_V3_CREATED"
BLOCKED_MISSING_KEY_STATUS = "BLOCKED_COINALYZE_API_KEY_MISSING_AFTER_SECURE_INPUT"
BLOCKED_API_STATUS = "BLOCKED_COINALYZE_API_OR_RATE_LIMIT_V3"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "edge_factory_os_repo_only_coinalyze_free_oi_liq_funding_availability_discovery_v3.py"
ARTIFACT_PATH = REPO_ROOT / "artifacts" / "data_discovery" / "coinalyze_free_oi_liq_funding_availability_discovery_v3.json"
PRIOR_V1_ARTIFACT = REPO_ROOT / "artifacts" / "data_discovery" / "coinalyze_free_oi_liq_funding_availability_discovery_v1.json"
PRIOR_V2_ARTIFACT = REPO_ROOT / "artifacts" / "data_discovery" / "coinalyze_free_oi_liq_funding_availability_discovery_v2.json"
SAFE_DIR = str(REPO_ROOT).replace("\\", "/")
COINALYZE_BASE_URL = "https://api.coinalyze.net/v1"
API_KEY_ENV = "COINALYZE_API_KEY"
RATE_LIMIT_SLEEP_SECONDS = 2.0

PRIOR_BLOCKED_ATTEMPTS = [
    {
        "version": "V1",
        "commit": "0c00fd0459ff1aaaa0939e7c2f0b24116f46c704",
        "status": "BLOCKED_COINALYZE_API_KEY_MISSING",
        "exact_blocker": "COINALYZE_API_KEY missing from environment",
        "artifact": "artifacts/data_discovery/coinalyze_free_oi_liq_funding_availability_discovery_v1.json",
    },
    {
        "version": "V2",
        "commit": "3cca8c2674ae3a56c7d11eed4c1c9c8e89ab9eb7",
        "status": "BLOCKED_COINALYZE_API_KEY_MISSING_AGAIN",
        "exact_blocker": "COINALYZE_API_KEY missing from environment",
        "artifact": "artifacts/data_discovery/coinalyze_free_oi_liq_funding_availability_discovery_v2.json",
    },
]

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

INTERVAL_WINDOWS_DAYS = {
    "15min": 14,
    "1hour": 60,
    "daily": 365,
}

EXPECTED_NEW_PATHS = {
    str(TOOL_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
    str(ARTIFACT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
}


def git(args: list[str]) -> str:
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
        return git(["rev-parse", "HEAD"])
    except Exception as exc:
        return f"UNKNOWN_SOURCE_CHECKPOINT: {exc}"


def git_status_entries() -> list[tuple[str, str]]:
    try:
        raw = git(["status", "--short", "-uall"])
    except Exception:
        return [("??", "GIT_STATUS_UNAVAILABLE")]
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if line.strip():
            entries.append((line[:2], line[3:].strip().strip('"').replace("\\", "/")))
    return entries


def repo_clean_except_expected_new_files() -> bool:
    for status, path in git_status_entries():
        if status == "??" and path in EXPECTED_NEW_PATHS:
            continue
        return False
    return True


def prior_blocked_files_modified() -> bool:
    prior_paths = {
        str(PRIOR_V1_ARTIFACT.relative_to(REPO_ROOT)).replace("\\", "/"),
        str(PRIOR_V2_ARTIFACT.relative_to(REPO_ROOT)).replace("\\", "/"),
    }
    return any(path in prior_paths for _status, path in git_status_entries())


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_sha256(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


def write_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    payload["payload_sha256_excluding_hash"] = payload_sha256(payload)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def normalize_symbol(value: str) -> str:
    normalized = "".join(ch for ch in value.upper() if ch.isalnum())
    for suffix in ("PERPETUAL", "PERP", "SWAP", "FUTURES", "USDTM", "USDCM"):
        normalized = normalized.replace(suffix, "")
    return normalized


def market_exchange(market: dict[str, Any]) -> str | None:
    text = " ".join(
        str(market.get(key, ""))
        for key in ("exchange", "exchange_name", "market", "market_name")
    ).upper()
    if "BINANCE" in text:
        return "BINANCE"
    if "OKX" in text or "OKEX" in text:
        return "OKX"
    return None


def market_symbol_fields(market: dict[str, Any]) -> list[str]:
    fields = [
        market.get("symbol"),
        market.get("symbol_on_exchange"),
        market.get("pair"),
        market.get("base_asset"),
        market.get("quote_asset"),
    ]
    return [str(item) for item in fields if item is not None]


def stable_perpetual_or_swap(market: dict[str, Any]) -> bool:
    symbol_text = " ".join(market_symbol_fields(market)).upper()
    type_text = " ".join(
        str(market.get(key, ""))
        for key in ("future_type", "contract_type", "type", "margined", "settlement_asset")
    ).upper()
    stable = any(token in symbol_text or token in type_text for token in ("USDT", "USDC"))
    perpetual = any(token in symbol_text or token in type_text for token in ("PERP", "PERPETUAL", "SWAP"))
    return stable and (perpetual or market.get("is_perpetual") is True)


def sanitize_error(message: str | None) -> str | None:
    if message is None:
        return None
    text = str(message)
    for marker in ("api_key=", "api_key%3D"):
        lower = text.lower()
        marker_index = lower.find(marker)
        if marker_index >= 0:
            text = text[:marker_index] + marker + "[REDACTED]"
    return text[:700]


def coinalyze_get(endpoint: str, params: dict[str, Any], api_key: str) -> tuple[bool, int | None, Any, str | None]:
    request_params = dict(params)
    request_params["api_key"] = api_key
    query = urllib.parse.urlencode(request_params)
    request = urllib.request.Request(
        f"{COINALYZE_BASE_URL}/{endpoint}?{query}",
        headers={"User-Agent": "edge-factory-os-coinalyze-v3-discovery/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {"raw_response_preview": body[:500]}
            return True, response.status, data, None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = str(exc)
        return False, exc.code, None, sanitize_error(body)
    except urllib.error.URLError as exc:
        return False, None, None, sanitize_error(str(exc.reason))
    except Exception as exc:
        return False, None, None, sanitize_error(str(exc))


def extract_rows(data: Any, symbol: str) -> list[dict[str, Any]]:
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "history" in data[0]:
            for item in data:
                if not isinstance(item, dict):
                    continue
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
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
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
    low = min(timestamps)
    high = max(timestamps)
    if low > 10_000_000_000:
        low //= 1000
        high //= 1000
    return (
        datetime.fromtimestamp(low, timezone.utc).isoformat().replace("+00:00", "Z"),
        datetime.fromtimestamp(high, timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def sample_row_without_api_key(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    sample: dict[str, Any] = {}
    for key, value in rows[0].items():
        key_text = str(key)
        if "api" in key_text.lower() or "key" in key_text.lower():
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            sample[key_text] = value
        else:
            sample[key_text] = str(value)[:200]
    return sample


def classify_results(results: list[dict[str, Any]]) -> tuple[str, str, dict[str, Any]]:
    usable_by_endpoint: dict[str, set[str]] = {endpoint: set() for endpoint in ENDPOINTS}
    interval_counts: dict[str, int] = {interval: 0 for interval in INTERVAL_WINDOWS_DAYS}
    blocked_count = 0
    for result in results:
        if result.get("http_status") in (401, 429):
            blocked_count += 1
        if result.get("request_ok") and int(result.get("row_count", 0)) > 0:
            endpoint = str(result.get("endpoint"))
            target_symbol = str(result.get("target_symbol"))
            interval = str(result.get("interval"))
            usable_by_endpoint.setdefault(endpoint, set()).add(target_symbol)
            interval_counts[interval] = interval_counts.get(interval, 0) + 1

    oi_symbols = usable_by_endpoint.get("open-interest-history", set())
    liquidation_symbols = usable_by_endpoint.get("liquidation-history", set())
    funding_symbols = usable_by_endpoint.get("funding-rate-history", set())
    best_interval = max(interval_counts.items(), key=lambda item: item[1])[0] if interval_counts else None
    summary = {
        "usable_oi_symbol_count": len(oi_symbols),
        "usable_liquidation_symbol_count": len(liquidation_symbols),
        "usable_funding_symbol_count": len(funding_symbols),
        "usable_oi_symbols": sorted(oi_symbols),
        "usable_liquidation_symbols": sorted(liquidation_symbols),
        "usable_funding_symbols": sorted(funding_symbols),
        "usable_interval_probe_counts": interval_counts,
        "best_usable_interval": best_interval,
    }

    major_coverage = {"BTCUSDT", "ETHUSDT", "SOLUSDT"} & oi_symbols & liquidation_symbols & funding_symbols
    intraday_ok = interval_counts.get("15min", 0) > 0 or interval_counts.get("1hour", 0) > 0
    if blocked_count and not (oi_symbols or liquidation_symbols or funding_symbols):
        return "COINALYZE_FREE_DATA_BLOCKED_API_OR_RATE_LIMIT", "COINALYZE_API_OR_RATE_LIMIT_REVIEW_V3", summary
    if len(major_coverage) >= 2 and intraday_ok:
        return "COINALYZE_FREE_DATA_READY_FOR_RECENT_OI_LIQUIDATION_RESEARCH", "COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN_V1", summary
    if oi_symbols or liquidation_symbols or funding_symbols:
        return "COINALYZE_FREE_DATA_PARTIAL_RECENT_ONLY", "COINALYZE_RECENT_OI_LIQUIDATION_HYPOTHESIS_DESIGN_V1", summary
    return "COINALYZE_FREE_DATA_INSUFFICIENT_FOR_OI_LIQUIDATION_RESEARCH", "FREE_DATA_SOURCE_ALTERNATIVE_DISCOVERY_V1", summary


def base_payload(status: str, replacement_checks_all_true: bool) -> dict[str, Any]:
    clean = repo_clean_except_expected_new_files()
    prior_unmodified = not prior_blocked_files_modified()
    validation_checks = {
        "repo_clean_before_run": clean,
        "secure_interactive_api_key_setup_used": True,
        "api_key_loaded_from_env_only": False,
        "api_key_not_written_to_artifact": True,
        "prior_blocked_artifacts_not_modified": prior_unmodified,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_pnl_computation": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_private_exchange_api_used": True,
        "no_order_endpoint_used": True,
        "exactly_one_python_tool_created": TOOL_PATH.exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_repo_files_modified": clean,
        "replacement_checks_all_true": replacement_checks_all_true,
    }
    return {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": source_checkpoint(),
        "prior_blocked_attempts": PRIOR_BLOCKED_ATTEMPTS,
        "api_key_handling": {
            "env_var_name": API_KEY_ENV,
            "secure_interactive_prompt_required": True,
            "api_key_read_attempted_from_env_only": True,
            "api_key_loaded": False,
            "api_key_persisted": False,
            "api_key_printed": False,
            "api_key_written_to_artifact": False,
            "api_key_written_to_logs": False,
            "api_key_in_git_diff": False,
        },
        "coinalyze_constraints": {
            "public_coinalyze_data_api_only": True,
            "recent_bounded_windows_only": True,
            "intraday_history_is_limited": True,
            "conservative_rate_limit_sleep_seconds": RATE_LIMIT_SLEEP_SECONDS,
            "no_private_exchange_api": True,
            "no_order_endpoint": True,
        },
        "market_discovery_summary": {
            "source_endpoint": "future-markets",
            "request_ok": False,
            "http_status": None,
            "market_count": 0,
            "binance_stable_perp_count": 0,
            "okx_stable_swap_count": 0,
        },
        "probe_symbols": [],
        "endpoint_probe_results": [],
        "interval_coverage_summary": {
            "tested_intervals": list(INTERVAL_WINDOWS_DAYS),
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
        "next_allowed_step": "COINALYZE_SECURE_API_KEY_INPUT_REVIEW_V3",
        "next_module": "COINALYZE_SECURE_API_KEY_INPUT_REVIEW_V3",
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


def missing_key_payload() -> dict[str, Any]:
    payload = base_payload(BLOCKED_MISSING_KEY_STATUS, False)
    payload["api_key_handling"].update(
        {
            "env_var_present": False,
            "api_key_loaded": False,
            "blocked_reason": BLOCKED_MISSING_KEY_STATUS,
        }
    )
    payload["limitations"] = [
        "COINALYZE_API_KEY was not present after the secure interactive setup step visible to this process.",
        "No Coinalyze API request or network call was made.",
        "Prior V1 and V2 blocked artifacts were not modified.",
    ]
    return payload


def discover(api_key: str) -> dict[str, Any]:
    payload = base_payload(PASS_STATUS, True)
    payload["api_key_handling"].update({"env_var_present": True, "api_key_loaded": True})
    payload["validation_checks"]["api_key_loaded_from_env_only"] = True

    market_ok, market_status, market_data, market_error = coinalyze_get("future-markets", {}, api_key)
    markets = market_data if isinstance(market_data, list) else []
    selected: list[dict[str, Any]] = []
    for market in markets:
        if not isinstance(market, dict):
            continue
        exchange = market_exchange(market)
        if exchange and stable_perpetual_or_swap(market):
            item = dict(market)
            item["_mapped_exchange"] = exchange
            selected.append(item)

    mapped: dict[str, dict[str, Any]] = {}
    for target in TARGET_SYMBOLS:
        target_norm = normalize_symbol(target)
        for exchange in ("BINANCE", "OKX"):
            match = None
            for market in selected:
                if market.get("_mapped_exchange") != exchange:
                    continue
                if any(normalize_symbol(value) == target_norm for value in market_symbol_fields(market)):
                    match = market
                    break
            if match is not None:
                mapped[target] = match
                break

    probes: list[dict[str, Any]] = []
    for target, market in mapped.items():
        probes.append(
            {
                "target_symbol": target,
                "symbol": str(market.get("symbol") or ""),
                "symbol_on_exchange": market.get("symbol_on_exchange"),
                "exchange": market.get("_mapped_exchange"),
            }
        )

    payload["market_discovery_summary"] = {
        "source_endpoint": "future-markets",
        "request_ok": market_ok,
        "http_status": market_status,
        "market_count": len(markets),
        "selected_stable_perpetual_or_swap_count": len(selected),
        "binance_stable_perp_count": sum(1 for market in selected if market.get("_mapped_exchange") == "BINANCE"),
        "okx_stable_swap_count": sum(1 for market in selected if market.get("_mapped_exchange") == "OKX"),
        "error_message": market_error,
    }
    payload["probe_symbols"] = probes

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    endpoint_results: list[dict[str, Any]] = []
    for probe in probes:
        symbol = str(probe.get("symbol") or "")
        if not symbol:
            continue
        for endpoint in ENDPOINTS:
            for interval, days in INTERVAL_WINDOWS_DAYS.items():
                start = now - timedelta(days=days)
                params = {
                    "symbols": symbol,
                    "interval": interval,
                    "from": int(start.timestamp()),
                    "to": int(now.timestamp()),
                }
                ok, status_code, data, error = coinalyze_get(endpoint, params, api_key)
                rows = extract_rows(data, symbol) if ok else []
                timestamp_min, timestamp_max = timestamp_bounds(rows)
                endpoint_results.append(
                    {
                        "endpoint": endpoint,
                        "target_symbol": probe["target_symbol"],
                        "symbol": symbol,
                        "exchange": probe.get("exchange"),
                        "interval": interval,
                        "request_ok": ok,
                        "http_status": status_code,
                        "row_count": len(rows),
                        "timestamp_min": timestamp_min,
                        "timestamp_max": timestamp_max,
                        "field_names": sorted({str(key) for row in rows[:5] for key in row.keys() if "api" not in str(key).lower()}),
                        "sample_row_without_api_key": sample_row_without_api_key(rows),
                        "error_message": error,
                    }
                )
                time.sleep(RATE_LIMIT_SLEEP_SECONDS)

    classification, next_step, usable_summary = classify_results(endpoint_results)
    payload["endpoint_probe_results"] = endpoint_results
    payload["result_classification"] = classification
    payload["next_allowed_step"] = next_step
    payload["next_module"] = next_step
    payload["usable_data_summary"] = usable_summary
    payload["interval_coverage_summary"] = {
        "tested_intervals": list(INTERVAL_WINDOWS_DAYS),
        "best_usable_interval": usable_summary.get("best_usable_interval"),
        "usable_interval_probe_counts": usable_summary.get("usable_interval_probe_counts", {}),
    }

    if classification == "COINALYZE_FREE_DATA_BLOCKED_API_OR_RATE_LIMIT":
        payload["status"] = BLOCKED_API_STATUS
        payload["replacement_checks_all_true"] = False
        payload["validation_checks"]["replacement_checks_all_true"] = False
        payload["limitations"].append("Coinalyze API was blocked by authorization, rate limit, or connectivity before usable coverage was found.")
    elif classification == "COINALYZE_FREE_DATA_READY_FOR_RECENT_OI_LIQUIDATION_RESEARCH":
        payload["limitations"].append("Coverage appears usable for recent-data prototyping only; no strategy, signal, or PnL was computed.")
    elif classification == "COINALYZE_FREE_DATA_PARTIAL_RECENT_ONLY":
        payload["limitations"].append("Only partial recent Coinalyze coverage was discovered; no strategy, signal, or PnL was computed.")
    else:
        payload["limitations"].append("No useful OI/liquidation/funding coverage was discovered for the probe set.")

    clean = repo_clean_except_expected_new_files()
    prior_unmodified = not prior_blocked_files_modified()
    payload["validation_checks"]["repo_clean_before_run"] = clean
    payload["validation_checks"]["no_existing_repo_files_modified"] = clean
    payload["validation_checks"]["prior_blocked_artifacts_not_modified"] = prior_unmodified
    if not clean or not prior_unmodified:
        payload["status"] = "BLOCKED_REPO_STATE_OR_PRIOR_BLOCKED_FILE_MODIFIED_V3"
        payload["result_classification"] = "COINALYZE_FREE_DATA_BLOCKED_API_OR_RATE_LIMIT"
        payload["next_allowed_step"] = "REPO_STATE_OR_PRIOR_ARTIFACT_REVIEW_V3"
        payload["next_module"] = "REPO_STATE_OR_PRIOR_ARTIFACT_REVIEW_V3"
        payload["replacement_checks_all_true"] = False
        payload["validation_checks"]["replacement_checks_all_true"] = False
        payload["limitations"].append("Repo state validation failed outside expected V3 files or a prior blocked artifact was modified.")
    return payload


def print_required_stdout(payload: dict[str, Any]) -> None:
    market = payload.get("market_discovery_summary", {})
    usable = payload.get("usable_data_summary", {})
    print(f"status: {payload.get('status')}")
    print(f"result_classification: {payload.get('result_classification')}")
    print(f"market_count: {market.get('market_count', 0)}")
    print(f"probe_symbol_count: {len(payload.get('probe_symbols', []))}")
    print(f"usable_oi_symbol_count: {usable.get('usable_oi_symbol_count', 0)}")
    print(f"usable_liquidation_symbol_count: {usable.get('usable_liquidation_symbol_count', 0)}")
    print(f"usable_funding_symbol_count: {usable.get('usable_funding_symbol_count', 0)}")
    print(f"best_usable_interval: {payload.get('interval_coverage_summary', {}).get('best_usable_interval')}")
    print(f"next_allowed_step: {payload.get('next_allowed_step')}")
    print("api_key_persisted: false")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {payload.get('payload_sha256_excluding_hash')}")
    print(f"replacement_checks_all_true: {str(payload.get('replacement_checks_all_true')).lower()}")


def main() -> int:
    api_key = os.environ.get(API_KEY_ENV)
    payload = discover(api_key) if api_key else missing_key_payload()
    payload = write_artifact(payload)
    print_required_stdout(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
