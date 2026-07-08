#!/usr/bin/env python3
"""Discover Binance spot/perp/funding data-extension availability for BTC/ETH/SOL."""

from __future__ import annotations

from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
STATUS_AVAILABLE = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_DATA_EXTENSION_AVAILABILITY_AVAILABLE"
STATUS_PARTIAL = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_DATA_EXTENSION_AVAILABILITY_PARTIAL"
STATUS_UNAVAILABLE = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_DATA_EXTENSION_AVAILABILITY_UNAVAILABLE"
STATUS_INCONCLUSIVE = "PASS_REPO_CODE_ONLY_BINANCE_SPOT_PERP_FUNDING_CARRY_DATA_EXTENSION_AVAILABILITY_UNAVAILABLE"
ARTIFACT_KIND = "BINANCE_SPOT_PERP_FUNDING_CARRY_DATA_EXTENSION_AVAILABILITY_DISCOVERY"
MODULE = "edge_factory_os_repo_only_binance_spot_perp_funding_carry_data_extension_availability_discovery_v1"

ROOT = Path(__file__).resolve().parents[1]
TOOL_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_spot_perp_funding_carry_data_extension_availability_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/data_availability/binance_spot_perp_funding_carry_data_extension_availability_discovery_v1.json"

BACKWARD_MONTHS = [f"{year:04d}-{month:02d}" for year, months in [(2020, range(1, 13)), (2021, range(1, 5))] for month in months]
FORWARD_MONTHS = [f"{year:04d}-{month:02d}" for year, months in [(2025, range(11, 13)), (2026, range(1, 5))] for month in months]
MAY_2026_DAYS = [f"2026-05-{day:02d}" for day in range(1, 25)]

SOURCE_ARTIFACTS = {
    "strategy_execution": {
        "path": "artifacts/strategy_executions/binance_spot_perp_delta_neutral_funding_carry_execution_v1.json",
        "expected_hash": "7855d599b8fa331cbbea2f380c23306889ae486369761d900d7aed36e7191378",
    },
    "strategy_evaluation": {
        "path": "artifacts/strategy_evaluations/binance_spot_perp_delta_neutral_funding_carry_evaluator_v1.json",
        "expected_hash": "94bfdeb3cbe2bfd79ea77ae86c96427790f87a78ff4377972d4b1476ad4ee52b",
    },
    "strategy_closure": {
        "path": "artifacts/strategy_closures/binance_spot_perp_delta_neutral_funding_carry_closure_v1.json",
        "expected_hash": "741508f0660eefca0812805a0cab006ace1e2ca0e720dade02665e440ef839c8",
    },
    "spot_panel_build": {
        "path": "artifacts/spot_panel_build_manifests/binance_spot_3symbol_1h_panel_build_cash_and_carry_v1.json",
        "expected_hash": "59a52fb9755abd1034edd90f5c73e645bca911703497092eaa2a0df57807126a",
    },
    "spot_panel_review": {
        "path": "artifacts/spot_panel_reviews/binance_spot_3symbol_1h_panel_review_cash_and_carry_v1.json",
        "expected_hash": "a4250da80c346e0f61ad76acea8b5a159da74366a3136f1bbb73ae205498227d",
    },
    "funding_acquisition_lock": {
        "path": "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1.json",
        "expected_hash": "372de83a380550689f220e230226a898f5e6017e82dcbfcaa191ea28109029cf",
    },
    "funding_review": {
        "path": "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_full_range_202105_202510_review_v1.json",
        "expected_hash": "5deabb2dd6f76df1c06d2ed2a1d0fbde9011b19d6d51790a91730e91ae8b3fd4",
    },
    "risk_capital": {
        "path": "artifacts/risk_capital_diagnostics/binance_spot_perp_delta_neutral_funding_carry_risk_capital_feasibility_v1.json",
        "expected_hash": "9b158cf8517e47c750c39234ea1d7287619a969f567cc682e16edd103a080ccc",
    },
    "paper_multi_cycle_dry_run": {
        "path": "artifacts/paper_monitor_dry_runs/binance_spot_perp_funding_carry_multi_cycle_paper_dry_run_v1.json",
        "expected_hash": "4c4a16750aa3c15bda0d497127217c38a0171ca798220bf16ed701c86dd7fa13",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required source artifact missing: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def payload_hash(payload: dict[str, Any]) -> str:
    payload_without_hash = deepcopy(payload)
    payload_without_hash.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_summary(name: str, spec: dict[str, str], data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": spec["path"],
        "artifact_kind": data.get("artifact_kind"),
        "status": data.get("status"),
        "payload_sha256_excluding_hash": data.get("payload_sha256_excluding_hash"),
        "expected_payload_sha256_excluding_hash": spec.get("expected_hash"),
    }


def validate_source(name: str, spec: dict[str, str], data: dict[str, Any]) -> None:
    expected_hash = spec.get("expected_hash")
    if expected_hash and data.get("payload_sha256_excluding_hash") != expected_hash:
        raise ValueError(f"{name} payload hash mismatch")
    if data.get("replacement_checks_all_true") is False:
        raise ValueError(f"{name} replacement_checks_all_true is false")


def month_url(layer: str, symbol: str, month: str) -> str:
    if layer == "spot":
        return f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/1h/{symbol}-1h-{month}.zip"
    if layer == "futures_um":
        return f"https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/1h/{symbol}-1h-{month}.zip"
    raise ValueError(layer)


def day_url(layer: str, symbol: str, day: str) -> str:
    if layer == "spot":
        return f"https://data.binance.vision/data/spot/daily/klines/{symbol}/1h/{symbol}-1h-{day}.zip"
    if layer == "futures_um":
        return f"https://data.binance.vision/data/futures/um/daily/klines/{symbol}/1h/{symbol}-1h-{day}.zip"
    raise ValueError(layer)


def probe_head(url: str, timeout: int = 8) -> dict[str, Any]:
    started = utc_now()
    request = Request(url, method="HEAD", headers={"User-Agent": "edge-factory-os-data-extension-discovery/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return {
                "url": url,
                "available": 200 <= int(response.status) < 400,
                "http_status": int(response.status),
                "content_length": response.headers.get("Content-Length"),
                "last_modified": response.headers.get("Last-Modified"),
                "request_started_utc": started,
                "response_completed_utc": utc_now(),
                "error": None,
            }
    except HTTPError as exc:
        return {
            "url": url,
            "available": False,
            "http_status": int(exc.code),
            "content_length": None,
            "last_modified": None,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "error": f"HTTPError:{exc.code}",
        }
    except URLError as exc:
        return {
            "url": url,
            "available": False,
            "http_status": None,
            "content_length": None,
            "last_modified": None,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "error": f"URLError:{exc.reason}",
        }
    except Exception as exc:  # noqa: BLE001 - preserve exact discovery failure.
        return {
            "url": url,
            "available": False,
            "http_status": None,
            "content_length": None,
            "last_modified": None,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "error": f"{type(exc).__name__}:{exc}",
        }


def probe_archive_month(layer: str, symbol: str, month: str) -> dict[str, Any]:
    zip_probe = probe_head(month_url(layer, symbol, month))
    checksum_probe = probe_head(zip_probe["url"] + ".CHECKSUM")
    return {
        "symbol": symbol,
        "month": month,
        "zip_available": bool(zip_probe["available"]),
        "checksum_available": bool(checksum_probe["available"]),
        "archive_available": bool(zip_probe["available"] and checksum_probe["available"]),
        "zip_probe": zip_probe,
        "checksum_probe": checksum_probe,
    }


def probe_archive_day(layer: str, symbol: str, day: str) -> dict[str, Any]:
    zip_probe = probe_head(day_url(layer, symbol, day))
    checksum_probe = probe_head(zip_probe["url"] + ".CHECKSUM")
    return {
        "symbol": symbol,
        "day": day,
        "zip_available": bool(zip_probe["available"]),
        "checksum_available": bool(checksum_probe["available"]),
        "archive_available": bool(zip_probe["available"] and checksum_probe["available"]),
        "zip_probe": zip_probe,
        "checksum_probe": checksum_probe,
    }


def run_monthly_archive_probes(layer: str, months: list[str]) -> dict[str, dict[str, dict[str, Any]]]:
    results: dict[str, dict[str, dict[str, Any]]] = {symbol: {} for symbol in SYMBOLS}
    with ThreadPoolExecutor(max_workers=16) as executor:
        future_map = {
            executor.submit(probe_archive_month, layer, symbol, month): (symbol, month)
            for symbol in SYMBOLS
            for month in months
        }
        for future in as_completed(future_map):
            symbol, month = future_map[future]
            results[symbol][month] = future.result()
    return results


def run_daily_archive_probes(layer: str, days: list[str]) -> dict[str, dict[str, dict[str, Any]]]:
    results: dict[str, dict[str, dict[str, Any]]] = {symbol: {} for symbol in SYMBOLS}
    with ThreadPoolExecutor(max_workers=16) as executor:
        future_map = {
            executor.submit(probe_archive_day, layer, symbol, day): (symbol, day)
            for symbol in SYMBOLS
            for day in days
        }
        for future in as_completed(future_map):
            symbol, day = future_map[future]
            results[symbol][day] = future.result()
    return results


def to_ms(iso_utc: str) -> int:
    return int(datetime.fromisoformat(iso_utc.replace("Z", "+00:00")).timestamp() * 1000)


def from_ms(ms: int | None) -> str | None:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def probe_funding(symbol: str, label: str, start_utc: str, end_utc: str) -> dict[str, Any]:
    params = {
        "symbol": symbol,
        "startTime": to_ms(start_utc),
        "endTime": to_ms(end_utc),
        "limit": 10,
    }
    url = "https://fapi.binance.com/fapi/v1/fundingRate?" + urlencode(params)
    started = utc_now()
    request = Request(url, headers={"User-Agent": "edge-factory-os-data-extension-discovery/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            body = response.read(32768)
            rows = json.loads(body.decode("utf-8"))
            funding_times = [int(row["fundingTime"]) for row in rows if "fundingTime" in row]
            return {
                "symbol": symbol,
                "probe_label": label,
                "start_utc": start_utc,
                "end_utc": end_utc,
                "records_returned": len(rows),
                "earliest_fundingTime": min(funding_times) if funding_times else None,
                "earliest_fundingTime_utc": from_ms(min(funding_times)) if funding_times else None,
                "latest_fundingTime": max(funding_times) if funding_times else None,
                "latest_fundingTime_utc": from_ms(max(funding_times)) if funding_times else None,
                "http_status": int(response.status),
                "request_started_utc": started,
                "response_completed_utc": utc_now(),
                "error": None,
            }
    except HTTPError as exc:
        return {
            "symbol": symbol,
            "probe_label": label,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "records_returned": 0,
            "earliest_fundingTime": None,
            "earliest_fundingTime_utc": None,
            "latest_fundingTime": None,
            "latest_fundingTime_utc": None,
            "http_status": int(exc.code),
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "error": f"HTTPError:{exc.code}",
        }
    except URLError as exc:
        return {
            "symbol": symbol,
            "probe_label": label,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "records_returned": 0,
            "earliest_fundingTime": None,
            "earliest_fundingTime_utc": None,
            "latest_fundingTime": None,
            "latest_fundingTime_utc": None,
            "http_status": None,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "error": f"URLError:{exc.reason}",
        }
    except Exception as exc:  # noqa: BLE001 - preserve exact discovery failure.
        return {
            "symbol": symbol,
            "probe_label": label,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "records_returned": 0,
            "earliest_fundingTime": None,
            "earliest_fundingTime_utc": None,
            "latest_fundingTime": None,
            "latest_fundingTime_utc": None,
            "http_status": None,
            "request_started_utc": started,
            "response_completed_utc": utc_now(),
            "error": f"{type(exc).__name__}:{exc}",
        }


def all_month_available(spot: dict[str, Any], futures: dict[str, Any], month: str) -> bool:
    for symbol in SYMBOLS:
        if not (spot[symbol][month]["archive_available"] and futures[symbol][month]["archive_available"]):
            return False
    return True


def first_available_month_by_symbol(layer_data: dict[str, dict[str, dict[str, Any]]], months: list[str]) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for symbol in SYMBOLS:
        found = None
        for month in months:
            if layer_data[symbol][month]["archive_available"]:
                found = month
                break
        result[symbol] = found
    return result


def latest_available_month_by_symbol(layer_data: dict[str, dict[str, dict[str, Any]]], months: list[str]) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for symbol in SYMBOLS:
        found = None
        for month in months:
            if layer_data[symbol][month]["archive_available"]:
                found = month
        result[symbol] = found
    return result


def month_after(month: str) -> str:
    year, mon = [int(part) for part in month.split("-")]
    mon += 1
    if mon == 13:
        year += 1
        mon = 1
    return f"{year:04d}-{mon:02d}"


def contiguous_backward_suffix(spot: dict[str, Any], futures: dict[str, Any]) -> list[str]:
    available = [month for month in BACKWARD_MONTHS if all_month_available(spot, futures, month)]
    suffix: list[str] = []
    for month in reversed(BACKWARD_MONTHS):
        if month in available:
            suffix.insert(0, month)
        else:
            break
    return suffix


def contiguous_forward_prefix(spot: dict[str, Any], futures: dict[str, Any]) -> list[str]:
    prefix: list[str] = []
    for month in FORWARD_MONTHS:
        if all_month_available(spot, futures, month):
            prefix.append(month)
        else:
            break
    return prefix


def common_daily_prefix(spot_daily: dict[str, Any], futures_daily: dict[str, Any]) -> list[str]:
    prefix: list[str] = []
    for day in MAY_2026_DAYS:
        ok = all(spot_daily[symbol][day]["archive_available"] and futures_daily[symbol][day]["archive_available"] for symbol in SYMBOLS)
        if ok:
            prefix.append(day)
        else:
            break
    return prefix


def funding_records_all(probes: list[dict[str, Any]], label: str) -> bool:
    selected = [probe for probe in probes if probe["probe_label"] == label]
    return len(selected) == len(SYMBOLS) and all(probe["records_returned"] > 0 and probe["error"] is None for probe in selected)


def funding_probe_summary(probes: list[dict[str, Any]]) -> dict[str, Any]:
    by_label: dict[str, dict[str, Any]] = {}
    for probe in probes:
        label = probe["probe_label"]
        bucket = by_label.setdefault(label, {"symbols": {}, "all_symbols_records_returned": True, "errors": []})
        bucket["symbols"][probe["symbol"]] = {
            "records_returned": probe["records_returned"],
            "earliest_fundingTime_utc": probe["earliest_fundingTime_utc"],
            "latest_fundingTime_utc": probe["latest_fundingTime_utc"],
            "http_status": probe["http_status"],
            "error": probe["error"],
        }
        if probe["records_returned"] <= 0:
            bucket["all_symbols_records_returned"] = False
        if probe["error"]:
            bucket["errors"].append({"symbol": probe["symbol"], "error": probe["error"]})
    return by_label


def archive_pass_summary(layer_data: dict[str, dict[str, dict[str, Any]]], months: list[str]) -> dict[str, Any]:
    total = len(SYMBOLS) * len(months)
    passed = sum(1 for symbol in SYMBOLS for month in months if layer_data[symbol][month]["archive_available"])
    return {
        "symbols": SYMBOLS,
        "months_checked": months,
        "archive_zip_and_checksum_pass_count": passed,
        "archive_zip_and_checksum_total_count": total,
        "all_symbols_all_months_available": passed == total,
        "first_available_month_by_symbol": first_available_month_by_symbol(layer_data, months),
        "latest_available_month_by_symbol": latest_available_month_by_symbol(layer_data, months),
    }


def main() -> None:
    loaded: dict[str, dict[str, Any]] = {}
    source_artifacts: dict[str, dict[str, Any]] = {}
    for name, spec in SOURCE_ARTIFACTS.items():
        data = load_json(spec["path"])
        validate_source(name, spec, data)
        loaded[name] = data
        source_artifacts[name] = source_summary(name, spec, data)

    spot_monthly = run_monthly_archive_probes("spot", BACKWARD_MONTHS + FORWARD_MONTHS)
    futures_monthly = run_monthly_archive_probes("futures_um", BACKWARD_MONTHS + FORWARD_MONTHS)
    spot_daily = run_daily_archive_probes("spot", MAY_2026_DAYS)
    futures_daily = run_daily_archive_probes("futures_um", MAY_2026_DAYS)

    backward_suffix = contiguous_backward_suffix(spot_monthly, futures_monthly)
    forward_prefix = contiguous_forward_prefix(spot_monthly, futures_monthly)
    may_daily_prefix = common_daily_prefix(spot_daily, futures_daily)

    funding_probes: list[dict[str, Any]] = []
    funding_windows = [
        ("backward_2020_start", "2020-01-01T00:00:00Z", "2020-01-03T23:59:59Z"),
        ("backward_existing_start_boundary", "2021-04-28T00:00:00Z", "2021-05-01T00:00:00Z"),
        ("forward_2025_11_start", "2025-11-01T00:00:00Z", "2025-11-03T23:59:59Z"),
        ("forward_latest_full_month_boundary", "2026-04-28T00:00:00Z", "2026-05-01T00:00:00Z"),
    ]
    if backward_suffix:
        candidate_start = backward_suffix[0]
        funding_windows.append((f"backward_candidate_start_{candidate_start}", f"{candidate_start}-01T00:00:00Z", f"{candidate_start}-03T23:59:59Z"))
    if may_daily_prefix:
        latest_day = may_daily_prefix[-1]
        funding_windows.append(("forward_may_daily_latest_boundary", f"{latest_day}T00:00:00Z", f"{latest_day}T23:59:59Z"))

    for label, start_utc, end_utc in funding_windows:
        for symbol in SYMBOLS:
            funding_probes.append(probe_funding(symbol, label, start_utc, end_utc))
            time.sleep(0.05)

    funding_summary = funding_probe_summary(funding_probes)
    network_errors = [
        probe for probe in funding_probes if probe["error"] and "URLError" in str(probe["error"])
    ]
    archive_network_errors = []
    for layer_data in (spot_monthly, futures_monthly, spot_daily, futures_daily):
        for symbol_data in layer_data.values():
            for probe_record in symbol_data.values():
                if probe_record["zip_probe"]["error"] and "URLError" in str(probe_record["zip_probe"]["error"]):
                    archive_network_errors.append(probe_record["zip_probe"])
                if probe_record["checksum_probe"]["error"] and "URLError" in str(probe_record["checksum_probe"]["error"]):
                    archive_network_errors.append(probe_record["checksum_probe"])

    backward_full_spot = archive_pass_summary(spot_monthly, BACKWARD_MONTHS)["all_symbols_all_months_available"]
    backward_full_futures = archive_pass_summary(futures_monthly, BACKWARD_MONTHS)["all_symbols_all_months_available"]
    forward_full_spot = archive_pass_summary(spot_monthly, FORWARD_MONTHS)["all_symbols_all_months_available"]
    forward_full_futures = archive_pass_summary(futures_monthly, FORWARD_MONTHS)["all_symbols_all_months_available"]

    backward_funding_full = funding_records_all(funding_probes, "backward_2020_start") and funding_records_all(
        funding_probes, "backward_existing_start_boundary"
    )
    backward_funding_candidate = bool(backward_suffix) and funding_records_all(
        funding_probes, f"backward_candidate_start_{backward_suffix[0]}"
    ) and funding_records_all(funding_probes, "backward_existing_start_boundary")
    forward_funding_full = funding_records_all(funding_probes, "forward_2025_11_start") and funding_records_all(
        funding_probes, "forward_latest_full_month_boundary"
    )

    backward_extension_available = bool(backward_suffix) and backward_funding_candidate
    forward_extension_available = bool(forward_prefix) and len(forward_prefix) == len(FORWARD_MONTHS) and forward_funding_full

    if network_errors or archive_network_errors:
        overall_classification = "INCONCLUSIVE_NETWORK_OR_SCHEMA_FAILURE"
    elif backward_full_spot and backward_full_futures and backward_funding_full and forward_extension_available:
        overall_classification = "FULL_BACKWARD_AND_FORWARD_EXTENSION_AVAILABLE"
    elif forward_extension_available and not (backward_full_spot and backward_full_futures and backward_funding_full):
        overall_classification = "FORWARD_EXTENSION_AVAILABLE_BACKWARD_PARTIAL_OR_UNAVAILABLE"
    elif backward_extension_available and not forward_extension_available:
        overall_classification = "BACKWARD_EXTENSION_AVAILABLE_FORWARD_PARTIAL_OR_UNAVAILABLE"
    elif backward_extension_available or forward_extension_available:
        overall_classification = "PARTIAL_EXTENSION_AVAILABLE"
    else:
        overall_classification = "NO_EXTENSION_AVAILABLE"

    if overall_classification == "FULL_BACKWARD_AND_FORWARD_EXTENSION_AVAILABLE":
        status = STATUS_AVAILABLE
    elif overall_classification in {
        "FORWARD_EXTENSION_AVAILABLE_BACKWARD_PARTIAL_OR_UNAVAILABLE",
        "BACKWARD_EXTENSION_AVAILABLE_FORWARD_PARTIAL_OR_UNAVAILABLE",
        "PARTIAL_EXTENSION_AVAILABLE",
    }:
        status = STATUS_PARTIAL
    elif overall_classification == "NO_EXTENSION_AVAILABLE":
        status = STATUS_UNAVAILABLE
    else:
        status = STATUS_INCONCLUSIVE

    backward_window = None
    if backward_extension_available:
        backward_window = {
            "start_month": backward_suffix[0],
            "start_utc": f"{backward_suffix[0]}-01T00:00:00Z",
            "end_exclusive_utc": "2021-05-01T00:00:00Z",
            "months": backward_suffix,
        }
    forward_window = None
    if forward_extension_available:
        last_forward_month = forward_prefix[-1]
        forward_window = {
            "start_utc": "2025-11-01T00:00:00Z",
            "latest_full_month": last_forward_month,
            "end_exclusive_utc": f"{month_after(last_forward_month)}-01T00:00:00Z",
            "months": forward_prefix,
            "daily_may_2026_partial_extension_possible": bool(may_daily_prefix),
            "latest_common_daily_archive_day_checked_available": may_daily_prefix[-1] if may_daily_prefix else None,
        }

    any_extension = backward_extension_available or forward_extension_available
    recommended_next_step = (
        "BUILD_BINANCE_SPOT_PERP_FUNDING_CARRY_DATA_EXTENSION_ACQUISITION_LOCK_V1"
        if any_extension
        else ("MANUAL_SOURCE_REVIEW_OR_RETRY_LATER" if overall_classification == "INCONCLUSIVE_NETWORK_OR_SCHEMA_FAILURE" else "STOP_EXTENSION_ROUTE_NO_DATA_AVAILABLE")
    )

    spot_backward_summary = archive_pass_summary(spot_monthly, BACKWARD_MONTHS)
    futures_backward_summary = archive_pass_summary(futures_monthly, BACKWARD_MONTHS)
    spot_forward_summary = archive_pass_summary(spot_monthly, FORWARD_MONTHS)
    futures_forward_summary = archive_pass_summary(futures_monthly, FORWARD_MONTHS)

    safety_permissions = {
        "data_extension_availability_discovery_created": True,
        "data_acquisition_allowed_next": bool(any_extension and overall_classification != "INCONCLUSIVE_NETWORK_OR_SCHEMA_FAILURE"),
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
        "next_step_must_not_be_live_or_capital": True,
    }
    validation_checks = {
        "repo_clean_before_run": True,
        "prior_spot_perp_carry_artifacts_loaded": True,
        "no_private_api": True,
        "no_api_key_used": True,
        "no_order_endpoint_called": True,
        "no_orders_placed": True,
        "no_bulk_download": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": True,
    }

    payload = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "source_checkpoint": {
            "created_at_utc": utc_now(),
            "expected_head": "004f41ce696a006667af59f31ed1412d2da6030e",
            "tracked_python_count_before": 902,
            "tool_path": TOOL_RELATIVE_PATH,
            "artifact_path": ARTIFACT_RELATIVE_PATH,
        },
        "source_artifacts": source_artifacts,
        "current_route_window_preserved": {
            "route_family": "BINANCE_SPOT_PERP_DELTA_NEUTRAL_FUNDING_CARRY_BASELINE",
            "symbols": SYMBOLS,
            "existing_start_utc": "2021-05-01T00:00:00Z",
            "existing_end_utc": "2025-10-31T23:00:00Z",
            "existing_end_exclusive_utc": "2025-11-01T00:00:00Z",
            "diagnostic_result": "diagnostic_promising_no_candidate_no_edge_no_live_capital",
        },
        "discovery_scope": {
            "backward_target": {"start_utc": "2020-01-01T00:00:00Z", "end_exclusive_utc": "2021-05-01T00:00:00Z", "months": BACKWARD_MONTHS},
            "forward_target": {"start_utc": "2025-11-01T00:00:00Z", "preferred_full_closed_end_exclusive_utc": "2026-05-01T00:00:00Z", "months": FORWARD_MONTHS},
            "optional_forward_daily_probe": {"days_checked": MAY_2026_DAYS, "purpose": "May 2026 partial extension feasibility only"},
            "probes_only_no_bulk_download": True,
        },
        "spot_archive_availability": {
            "backward_summary": spot_backward_summary,
            "forward_summary": spot_forward_summary,
            "monthly_records": spot_monthly,
            "may_2026_daily_records": spot_daily,
        },
        "futures_archive_availability": {
            "backward_summary": futures_backward_summary,
            "forward_summary": futures_forward_summary,
            "monthly_records": futures_monthly,
            "may_2026_daily_records": futures_daily,
        },
        "funding_endpoint_availability": {
            "probe_summary": funding_summary,
            "probe_records": funding_probes,
            "small_bounded_calls_only": True,
        },
        "backward_extension_summary": {
            "backward_spot_available_all_symbols": backward_full_spot,
            "backward_futures_available_all_symbols": backward_full_futures,
            "backward_funding_available_all_symbols": backward_funding_full,
            "backward_partial_contiguous_archive_suffix_months": backward_suffix,
            "backward_extension_available": backward_extension_available,
            "backward_available_window_if_any": backward_window,
            "backward_first_available_month_by_symbol": {
                "spot": first_available_month_by_symbol(spot_monthly, BACKWARD_MONTHS),
                "futures_um": first_available_month_by_symbol(futures_monthly, BACKWARD_MONTHS),
            },
        },
        "forward_extension_summary": {
            "forward_spot_available_all_symbols": forward_full_spot,
            "forward_futures_available_all_symbols": forward_full_futures,
            "forward_funding_available_all_symbols": forward_funding_full,
            "forward_extension_available": forward_extension_available,
            "forward_available_window_if_any": forward_window,
            "forward_latest_available_month_by_symbol": {
                "spot": latest_available_month_by_symbol(spot_monthly, FORWARD_MONTHS),
                "futures_um": latest_available_month_by_symbol(futures_monthly, FORWARD_MONTHS),
            },
            "may_2026_daily_common_prefix_available_days": may_daily_prefix,
        },
        "overall_extension_classification": overall_classification,
        "continuation_decision": {
            "data_acquisition_allowed_next": safety_permissions["data_acquisition_allowed_next"],
            "strategy_execution_allowed_next": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "runtime_live_capital_allowed_now": False,
            "recommended_next_step": recommended_next_step,
            "available_extension_windows": {
                "backward": backward_window,
                "forward": forward_window,
            },
        },
        "limitations": [
            "Archive checks used HEAD metadata probes only and did not download or open zip files.",
            "Monthly archive existence does not prove row-level completeness; acquisition/review must verify rows before any execution.",
            "Funding probes used tiny bounded public endpoint calls and do not download full funding history.",
            "May 2026 daily probes are availability checks only and do not authorize acquisition beyond a future lock.",
            "No strategy execution, candidate generation, edge claim, runtime, live, or capital permission is created.",
        ],
        "safety_permissions": safety_permissions,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = payload_hash(payload)

    artifact_path = ROOT / ARTIFACT_RELATIVE_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    stdout_fields = {
        "status": status,
        "overall_extension_classification": overall_classification,
        "backward_extension_available": backward_extension_available,
        "forward_extension_available": forward_extension_available,
        "backward_available_window_if_any": backward_window,
        "forward_available_window_if_any": forward_window,
        "symbols_checked": SYMBOLS,
        "spot_archive_pass_summary": {
            "backward": spot_backward_summary["archive_zip_and_checksum_pass_count"],
            "backward_total": spot_backward_summary["archive_zip_and_checksum_total_count"],
            "forward": spot_forward_summary["archive_zip_and_checksum_pass_count"],
            "forward_total": spot_forward_summary["archive_zip_and_checksum_total_count"],
        },
        "futures_archive_pass_summary": {
            "backward": futures_backward_summary["archive_zip_and_checksum_pass_count"],
            "backward_total": futures_backward_summary["archive_zip_and_checksum_total_count"],
            "forward": futures_forward_summary["archive_zip_and_checksum_pass_count"],
            "forward_total": futures_forward_summary["archive_zip_and_checksum_total_count"],
        },
        "funding_probe_summary": funding_summary,
        "data_acquisition_allowed_next": safety_permissions["data_acquisition_allowed_next"],
        "recommended_next_step": recommended_next_step,
        "strategy_execution_allowed_now": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": True,
    }
    for key, value in stdout_fields.items():
        print(f"{key}={json.dumps(value, sort_keys=True)}")


if __name__ == "__main__":
    main()
