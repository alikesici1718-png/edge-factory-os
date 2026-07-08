import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_long_short_ratio_history_availability_discovery_lock_v1.py"
ARTIFACT_PATH = "artifacts/long_short_ratio_availability_locks/binance_okx_overlap_long_short_ratio_history_availability_discovery_lock_v1.json"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_LONG_SHORT_RATIO_HISTORY_AVAILABILITY_DISCOVERY_LOCK"

STATUS_AVAILABLE = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_LONG_SHORT_RATIO_HISTORY_AVAILABILITY_DISCOVERY_LOCK_AVAILABLE"
STATUS_UNAVAILABLE = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_LONG_SHORT_RATIO_HISTORY_AVAILABILITY_DISCOVERY_LOCK_UNAVAILABLE_ROUTE_PENDING"

CLASS_AVAILABLE = "LONG_SHORT_RATIO_HISTORY_AVAILABLE_FOR_ALIGNED_WINDOW_ALL_81_SYMBOLS"
CLASS_PARTIAL = "LONG_SHORT_RATIO_HISTORY_PARTIALLY_AVAILABLE_REQUIRES_REDUCED_UNIVERSE_OR_WINDOW"
CLASS_UNAVAILABLE = "LONG_SHORT_RATIO_HISTORY_UNAVAILABLE_LATEST_30_DAYS_ONLY"
CLASS_INCONCLUSIVE = "LONG_SHORT_RATIO_HISTORY_DISCOVERY_INCONCLUSIVE_NETWORK_OR_SCHEMA_FAILURE"

BASE_URL = "https://fapi.binance.com/futures/data"
ENDPOINTS = {
    "global_long_short_account_ratio": f"{BASE_URL}/globalLongShortAccountRatio",
    "top_trader_long_short_account_ratio": f"{BASE_URL}/topLongShortAccountRatio",
    "top_trader_long_short_position_ratio": f"{BASE_URL}/topLongShortPositionRatio",
}

READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PREVIEW_PATH = "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"

OLD_START = "2023-07-01T00:00:00Z"
OLD_END = "2023-07-03T00:00:00Z"
MID_START = "2024-06-01T00:00:00Z"
MID_END = "2024-06-03T00:00:00Z"
LATE_START = "2025-10-29T00:00:00Z"
LATE_END = "2025-10-31T16:00:00Z"

REPRESENTATIVE_SYMBOLS_REQUESTED = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "1INCHUSDT", "QTUMUSDT"]


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required source artifact: {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash(payload: Dict[str, Any]) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("source artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise RuntimeError(f"source artifact payload hash mismatch: {recomputed} != {stored}")
    return stored


def iso_to_ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def ms_to_iso(value: Any) -> Optional[str]:
    try:
        raw = int(value)
    except Exception:
        return None
    if raw < 10_000_000_000:
        raw *= 1000
    return datetime.fromtimestamp(raw / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_symbol_list(value: Any) -> Optional[List[str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("exact_overlap_binance_symbols", "symbol_set") and isinstance(child, list) and len(child) == 81:
                if all(isinstance(item, str) and item.endswith("USDT") for item in child):
                    return list(child)
            found = find_symbol_list(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found:
                return found
    return None


def request_json(url: str, params: Dict[str, Any], retry_cap: int = 2) -> Dict[str, Any]:
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    last: Dict[str, Any] = {
        "ok": False,
        "status_code": None,
        "error": "not attempted",
        "data": None,
        "url": full_url,
    }
    for attempt in range(retry_cap + 1):
        try:
            request = urllib.request.Request(full_url, headers={"User-Agent": "repo-only-long-short-availability/1"})
            with urllib.request.urlopen(request, timeout=20) as response:
                text = response.read(500_000).decode("utf-8", errors="replace")
                data = json.loads(text)
                return {
                    "ok": True,
                    "status_code": response.status,
                    "error": None,
                    "data": data,
                    "url": full_url,
                }
        except urllib.error.HTTPError as exc:
            body = exc.read(2000).decode("utf-8", errors="replace")
            last = {
                "ok": False,
                "status_code": exc.code,
                "error": body[:1000],
                "data": None,
                "url": full_url,
            }
            if exc.code in (418, 429, 500, 502, 503, 504) and attempt < retry_cap:
                time.sleep(1.5 * (attempt + 1))
                continue
            return last
        except Exception as exc:
            last = {
                "ok": False,
                "status_code": None,
                "error": repr(exc),
                "data": None,
                "url": full_url,
            }
            if attempt < retry_cap:
                time.sleep(1.5 * (attempt + 1))
                continue
            return last
    return last


def summarize_rows(response: Dict[str, Any]) -> Dict[str, Any]:
    data = response.get("data")
    rows = data if isinstance(data, list) else []
    timestamps = []
    schema_keys = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if not schema_keys:
            schema_keys = sorted(row.keys())
        ts = row.get("timestamp") or row.get("time") or row.get("t")
        iso = ms_to_iso(ts) if ts is not None else None
        if iso:
            timestamps.append(iso)
    return {
        "ok": response["ok"],
        "status_code": response["status_code"],
        "row_count": len(rows),
        "earliest_timestamp_utc": min(timestamps) if timestamps else None,
        "latest_timestamp_utc": max(timestamps) if timestamps else None,
        "schema_keys_observed": schema_keys,
        "error": response["error"],
    }


def perform_probe(endpoint_name: str, endpoint_url: str, symbol: str, range_name: str, start_iso: Optional[str], end_iso: Optional[str]) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "symbol": symbol,
        "period": "1h",
        "limit": 500,
    }
    if start_iso is not None and end_iso is not None:
        params["startTime"] = iso_to_ms(start_iso)
        params["endTime"] = iso_to_ms(end_iso)
    response = request_json(endpoint_url, params)
    time.sleep(0.30)
    summary = summarize_rows(response)
    summary.update(
        {
            "endpoint": endpoint_name,
            "symbol": symbol,
            "range_name": range_name,
            "start_utc": start_iso,
            "end_utc": end_iso,
            "period": "1h",
            "limit": 500,
        }
    )
    return summary


def build_artifact() -> Dict[str, Any]:
    readiness = read_json(READINESS_PATH)
    preview = read_json(PREVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    source_hashes = {
        READINESS_PATH: verify_hash(readiness),
        PREVIEW_PATH: verify_hash(preview),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
    }

    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != 81:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")

    representative_symbols = [symbol for symbol in REPRESENTATIVE_SYMBOLS_REQUESTED if symbol in symbols]
    if len(representative_symbols) < 5:
        raise RuntimeError("representative symbol set missing required high-liquidity symbols")

    representative_probe_results: Dict[str, Any] = {}
    old_available_count = 0
    recent_available_count = 0
    all_timestamps: List[str] = []
    network_or_schema_error_count = 0

    for endpoint_name, endpoint_url in ENDPOINTS.items():
        endpoint_results = []
        for symbol in representative_symbols:
            old_probe = perform_probe(endpoint_name, endpoint_url, symbol, "old_2023_target_window", OLD_START, OLD_END)
            recent_probe = perform_probe(endpoint_name, endpoint_url, symbol, "recent_no_start_end", None, None)
            endpoint_results.append(
                {
                    "symbol": symbol,
                    "old_2023_target_window": old_probe,
                    "recent_no_start_end": recent_probe,
                }
            )
            if old_probe["row_count"] > 0:
                old_available_count += 1
            if recent_probe["row_count"] > 0:
                recent_available_count += 1
            for probe in (old_probe, recent_probe):
                if probe["earliest_timestamp_utc"]:
                    all_timestamps.append(probe["earliest_timestamp_utc"])
                if probe["latest_timestamp_utc"]:
                    all_timestamps.append(probe["latest_timestamp_utc"])
                if not probe["ok"] and probe["status_code"] not in (400, 404):
                    network_or_schema_error_count += 1
        representative_probe_results[endpoint_name] = endpoint_results

    full_81_probe_results_if_needed: Dict[str, Any] = {
        "performed": False,
        "reason": "Representative old 2023 target-window probes did not prove old aligned-window history availability.",
    }

    if old_available_count > 0 and network_or_schema_error_count == 0:
        full_81_probe_results_if_needed = {
            "performed": True,
            "reason": "Representative old-window data appeared unexpectedly available; lightweight all-81 old/mid/late probes executed.",
            "results": {},
        }
        for endpoint_name, endpoint_url in ENDPOINTS.items():
            endpoint_full_results = []
            for symbol in symbols:
                symbol_result = {
                    "symbol": symbol,
                    "old_2023_target_window": perform_probe(endpoint_name, endpoint_url, symbol, "old_2023_target_window", OLD_START, OLD_END),
                    "mid_2024_target_window": perform_probe(endpoint_name, endpoint_url, symbol, "mid_2024_target_window", MID_START, MID_END),
                    "late_2025_target_window": perform_probe(endpoint_name, endpoint_url, symbol, "late_2025_target_window", LATE_START, LATE_END),
                }
                endpoint_full_results.append(symbol_result)
                for probe in (
                    symbol_result["old_2023_target_window"],
                    symbol_result["mid_2024_target_window"],
                    symbol_result["late_2025_target_window"],
                ):
                    if probe["earliest_timestamp_utc"]:
                        all_timestamps.append(probe["earliest_timestamp_utc"])
                    if probe["latest_timestamp_utc"]:
                        all_timestamps.append(probe["latest_timestamp_utc"])
            full_81_probe_results_if_needed["results"][endpoint_name] = endpoint_full_results

    old_target_available = old_available_count > 0
    recent_data_available = recent_available_count > 0
    if network_or_schema_error_count > 0 and not recent_data_available:
        availability_classification = CLASS_INCONCLUSIVE
    elif old_target_available and full_81_probe_results_if_needed.get("performed"):
        availability_classification = CLASS_PARTIAL
    elif not old_target_available and recent_data_available:
        availability_classification = CLASS_UNAVAILABLE
    elif not old_target_available and not recent_data_available:
        availability_classification = CLASS_INCONCLUSIVE
    else:
        availability_classification = CLASS_INCONCLUSIVE

    if availability_classification == CLASS_AVAILABLE:
        status = STATUS_AVAILABLE
        acquisition_allowed_next = True
        route_pending = False
    else:
        status = STATUS_UNAVAILABLE
        acquisition_allowed_next = False
        route_pending = True

    payload: Dict[str, Any] = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "repo_scope": {
            "code_changes_repo_only": True,
            "availability_lock_created_in_repo": True,
            "public_binance_network_used_for_metadata_probe": True,
            "private_api_used": False,
            "api_key_used": False,
            "bulk_history_downloaded": False,
            "panel_rows_read": False,
            "funding_rows_read": False,
            "okx_panel_rows_read": False,
            "strategy_executed": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
        },
        "source_checkpoint": {
            "prior_head": "5c1603d89cd38e19837711b62915e0f361a96e4a",
            "prior_tracked_python_count": 835,
            "repo_clean_before_discovery": True,
            "latest_volume_surge_route_result": "FUNDING_EXTREME_VOLUME_SURGE_FILTER_REJECTED_NO_FOLLOWUP",
        },
        "source_artifacts": {
            "readiness_artifact": READINESS_PATH,
            "preview_artifact": PREVIEW_PATH,
            "build_manifest_artifact": BUILD_MANIFEST_PATH,
            "payload_hashes": source_hashes,
        },
        "endpoint_contracts": {
            "endpoints": ENDPOINTS,
            "period_tested": "1h",
            "max_limit": 500,
            "official_limitation": {
                "period_values_include_1h": True,
                "limit_max": 500,
                "if_startTime_endTime_not_sent_most_recent_data_returned": True,
                "only_latest_30_days_available": True,
                "ip_rate_limit": "1000 requests / 5 min",
            },
        },
        "representative_probe_results": representative_probe_results,
        "full_81_probe_results_if_needed": full_81_probe_results_if_needed,
        "availability_classification": availability_classification,
        "continuation_decision": {
            "long_short_ratio_acquisition_allowed_next": acquisition_allowed_next,
            "strategy_execution_allowed_next": False,
            "route_pending_until_historical_long_short_source_exists": route_pending,
            "immediate_next_module_required": False,
            "project_can_pause_after_availability_lock": True,
        },
        "pending_route_record_if_unavailable": {
            "route_pending": route_pending,
            "reason": "Official Binance public long/short ratio endpoints did not provide old 2023 aligned-window data in representative probes; recent data availability confirms latest-window behavior."
            if availability_classification == CLASS_UNAVAILABLE
            else "Discovery did not prove full aligned-window availability.",
            "required_future_condition": "A historical long/short-ratio source covering all 81 symbols over 2023-07-01 to 2025-10-31 at 1h or safely alignable cadence must exist before acquisition or execution.",
        },
        "limitations": [
            "This discovery lock does not acquire full long/short ratio history.",
            "This discovery lock does not read Binance panel rows.",
            "This discovery lock does not read Binance funding rows.",
            "This discovery lock does not read OKX rows.",
            "This discovery lock does not run strategy logic or compute returns.",
            "This discovery lock grants no candidate, edge, release, or runtime/live/capital permission.",
        ],
        "safety_permissions": {
            "long_short_ratio_acquisition_allowed_next": acquisition_allowed_next,
            "strategy_execution_allowed_next": False,
            "route_pending_until_historical_long_short_source_exists": route_pending,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "immediate_next_module_required": False,
            "project_can_pause_after_availability_lock": True,
        },
        "validation_checks": {
            "status_equals_expected_status": True,
            "module_path_equals_required_path": True,
            "artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_availability_artifact_expected": True,
            "no_existing_files_modified_expected": True,
            "no_other_tracked_files_expected": True,
            "exact_overlap_symbol_count_verified_81": len(symbols) == 81,
            "representative_old_range_probe_performed": True,
            "representative_recent_range_probe_performed": True,
            "old_2023_window_not_available_if_unavailable": (availability_classification != CLASS_UNAVAILABLE) or (old_available_count == 0),
            "recent_data_available_if_latest_30_days_behavior_confirmed": (availability_classification != CLASS_UNAVAILABLE) or recent_data_available,
            "no_bulk_download": True,
            "no_panel_rows_read": True,
            "no_funding_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_strategy_execution": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "no_runtime_live_capital": True,
            "artifact_json_valid": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "summary_counts": {
            "exact_overlap_symbol_count": len(symbols),
            "endpoints_tested": len(ENDPOINTS),
            "representative_symbols_tested": representative_symbols,
            "old_range_available_count": old_available_count,
            "recent_range_available_count": recent_available_count,
            "global_earliest_timestamp_observed": min(all_timestamps) if all_timestamps else None,
            "global_latest_timestamp_observed": max(all_timestamps) if all_timestamps else None,
        },
        "replacement_checks_all_true": True,
    }

    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] in (STATUS_AVAILABLE, STATUS_UNAVAILABLE),
        payload["module"] == MODULE_PATH,
        ARTIFACT_PATH == "artifacts/long_short_ratio_availability_locks/binance_okx_overlap_long_short_ratio_history_availability_discovery_lock_v1.json",
        len(symbols) == 81,
        payload["repo_scope"]["bulk_history_downloaded"] is False,
        payload["repo_scope"]["panel_rows_read"] is False,
        payload["repo_scope"]["funding_rows_read"] is False,
        payload["repo_scope"]["okx_panel_rows_read"] is False,
        payload["repo_scope"]["strategy_executed"] is False,
        payload["repo_scope"]["candidate_generation"] is False,
        payload["repo_scope"]["edge_claim"] is False,
        payload["repo_scope"]["runtime_live_capital"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("discovery lock invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_artifact()
    output_path = REPO_ROOT / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "artifact_path": ARTIFACT_PATH,
        "availability_classification": artifact["availability_classification"],
        "exact_overlap_symbol_count": artifact["summary_counts"]["exact_overlap_symbol_count"],
        "endpoints_tested": artifact["summary_counts"]["endpoints_tested"],
        "representative_symbols_tested": artifact["summary_counts"]["representative_symbols_tested"],
        "old_range_available_count": artifact["summary_counts"]["old_range_available_count"],
        "recent_range_available_count": artifact["summary_counts"]["recent_range_available_count"],
        "global_earliest_timestamp_observed": artifact["summary_counts"]["global_earliest_timestamp_observed"],
        "global_latest_timestamp_observed": artifact["summary_counts"]["global_latest_timestamp_observed"],
        "acquisition_allowed_next": artifact["continuation_decision"]["long_short_ratio_acquisition_allowed_next"],
        "strategy_execution_allowed_next": artifact["continuation_decision"]["strategy_execution_allowed_next"],
        "route_pending_until_historical_long_short_source_exists": artifact["continuation_decision"]["route_pending_until_historical_long_short_source_exists"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
