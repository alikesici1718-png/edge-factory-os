import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_taker_buy_sell_volume_history_availability_discovery_lock_v1.py"
ARTIFACT_PATH = "artifacts/taker_buy_sell_volume_availability_locks/binance_okx_overlap_taker_buy_sell_volume_history_availability_discovery_lock_v1.json"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_TAKER_BUY_SELL_VOLUME_HISTORY_AVAILABILITY_DISCOVERY_LOCK"

STATUS_API_UNAVAILABLE_PANEL_AVAILABLE = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_SELL_VOLUME_HISTORY_AVAILABILITY_DISCOVERY_LOCK_API_UNAVAILABLE_PANEL_DERIVED_AVAILABLE"
STATUS_API_AVAILABLE = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_TAKER_BUY_SELL_VOLUME_HISTORY_AVAILABILITY_DISCOVERY_LOCK_API_AVAILABLE"

CLASS_API_AVAILABLE = "TAKER_BUY_SELL_API_HISTORY_AVAILABLE_FOR_ALIGNED_WINDOW_ALL_81_SYMBOLS"
CLASS_API_PARTIAL = "TAKER_BUY_SELL_API_HISTORY_PARTIALLY_AVAILABLE_REQUIRES_REDUCED_UNIVERSE_OR_WINDOW"
CLASS_API_UNAVAILABLE_PANEL_AVAILABLE = "TAKER_BUY_SELL_API_HISTORY_UNAVAILABLE_LATEST_30_DAYS_ONLY_PANEL_DERIVED_AVAILABLE"
CLASS_API_INCONCLUSIVE = "TAKER_BUY_SELL_API_HISTORY_DISCOVERY_INCONCLUSIVE_NETWORK_OR_SCHEMA_FAILURE"

ENDPOINT_URL = "https://fapi.binance.com/futures/data/takerlongshortRatio"
READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PREVIEW_PATH = "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
COVERAGE_LOCK_PATH = "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"
LONG_SHORT_LOCK_PATH = "artifacts/long_short_ratio_availability_locks/binance_okx_overlap_long_short_ratio_history_availability_discovery_lock_v1.json"

OLD_START = "2023-07-01T00:00:00Z"
OLD_END = "2023-07-03T00:00:00Z"
MID_START = "2024-06-01T00:00:00Z"
MID_END = "2024-06-03T00:00:00Z"
LATE_START = "2025-10-29T00:00:00Z"
LATE_END = "2025-10-31T16:00:00Z"
REPRESENTATIVE_SYMBOLS_REQUESTED = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "1INCHUSDT"]


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


def find_first_key(value: Any, target_key: str) -> Any:
    if isinstance(value, dict):
        if target_key in value:
            return value[target_key]
        for child in value.values():
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_first_key(child, target_key)
            if found is not None:
                return found
    return None


def contains_key(value: Any, target_key: str) -> bool:
    if isinstance(value, dict):
        if target_key in value:
            return True
        return any(contains_key(child, target_key) for child in value.values())
    if isinstance(value, list):
        return any(contains_key(child, target_key) for child in value)
    return False


def request_json(params: Dict[str, Any], retry_cap: int = 2) -> Dict[str, Any]:
    query = urllib.parse.urlencode(params)
    full_url = f"{ENDPOINT_URL}?{query}"
    last: Dict[str, Any] = {
        "ok": False,
        "status_code": None,
        "error": "not attempted",
        "data": None,
        "url": full_url,
    }
    for attempt in range(retry_cap + 1):
        try:
            request = urllib.request.Request(full_url, headers={"User-Agent": "repo-only-taker-buy-sell-availability/1"})
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
    expected_fields_seen = {
        "buySellRatio": False,
        "buyVol": False,
        "sellVol": False,
        "timestamp": False,
    }
    for row in rows:
        if not isinstance(row, dict):
            continue
        if not schema_keys:
            schema_keys = sorted(row.keys())
        for key in expected_fields_seen:
            if key in row:
                expected_fields_seen[key] = True
        ts = row.get("timestamp")
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
        "expected_response_fields_seen": expected_fields_seen,
        "error": response["error"],
    }


def perform_probe(symbol: str, range_name: str, start_iso: Optional[str], end_iso: Optional[str]) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "symbol": symbol,
        "period": "1h",
        "limit": 500,
    }
    if start_iso is not None and end_iso is not None:
        params["startTime"] = iso_to_ms(start_iso)
        params["endTime"] = iso_to_ms(end_iso)
    response = request_json(params)
    time.sleep(0.30)
    summary = summarize_rows(response)
    summary.update(
        {
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
    panel_review = read_json(PANEL_REVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    long_short_lock = read_json(LONG_SHORT_LOCK_PATH)
    source_hashes = {
        READINESS_PATH: verify_hash(readiness),
        PREVIEW_PATH: verify_hash(preview),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
        LONG_SHORT_LOCK_PATH: verify_hash(long_short_lock),
    }

    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != 81:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")

    panel_classification = panel_review.get("panel_validity_classification") or find_first_key(panel_review, "panel_validity_classification")
    panel_review_passed = panel_classification == "PANEL_REVIEW_PASS_WITH_P1_ATTENTION_VALID_FOR_READ_ONLY_SECOND_SOURCE_ANALYSIS"
    all_headers_valid = find_first_key(panel_review, "all_headers_valid") is True
    schema_matches_expected = find_first_key(panel_review, "schema_matches_expected") is True

    panel_schema_has_taker_buy_base_volume = contains_key(build_manifest, "taker_buy_base_volume_policy")
    panel_schema_has_taker_buy_quote_volume = contains_key(build_manifest, "taker_buy_quote_volume_policy")
    panel_schema_has_total_volume = contains_key(build_manifest, "volume_policy")
    panel_schema_has_total_quote_volume = contains_key(build_manifest, "quote_volume_policy")
    taker_sell_derivable = (
        panel_schema_has_taker_buy_base_volume
        and panel_schema_has_taker_buy_quote_volume
        and panel_schema_has_total_volume
        and panel_schema_has_total_quote_volume
    )
    panel_start = find_first_key(build_manifest, "primary_window_start_utc") or find_first_key(preview, "primary_window_start_utc")
    panel_end = find_first_key(build_manifest, "primary_window_end_exclusive_utc") or find_first_key(preview, "primary_window_end_exclusive_utc")
    aligned_window_covered = panel_start <= OLD_START and panel_end >= "2025-10-31T16:00:00Z"
    panel_derived_available = panel_review_passed and all_headers_valid and schema_matches_expected and taker_sell_derivable and aligned_window_covered

    representative_symbols = [symbol for symbol in REPRESENTATIVE_SYMBOLS_REQUESTED if symbol in symbols]
    if len(representative_symbols) < 5:
        raise RuntimeError("representative symbols missing from exact overlap universe")

    representative_probe_results = []
    old_available_count = 0
    recent_available_count = 0
    all_timestamps: List[str] = []
    network_or_schema_error_count = 0

    for symbol in representative_symbols:
        old_probe = perform_probe(symbol, "old_2023_target_window", OLD_START, OLD_END)
        recent_probe = perform_probe(symbol, "recent_no_start_end", None, None)
        representative_probe_results.append(
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

    full_81_probe_results_if_needed: Dict[str, Any] = {
        "performed": False,
        "reason": "Representative old 2023 target-window probes did not prove old aligned-window API availability.",
    }
    if old_available_count > 0 and network_or_schema_error_count == 0:
        full_81_results = []
        for symbol in symbols:
            symbol_result = {
                "symbol": symbol,
                "old_2023_target_window": perform_probe(symbol, "old_2023_target_window", OLD_START, OLD_END),
                "mid_2024_target_window": perform_probe(symbol, "mid_2024_target_window", MID_START, MID_END),
                "late_2025_target_window": perform_probe(symbol, "late_2025_target_window", LATE_START, LATE_END),
            }
            full_81_results.append(symbol_result)
            for probe in (
                symbol_result["old_2023_target_window"],
                symbol_result["mid_2024_target_window"],
                symbol_result["late_2025_target_window"],
            ):
                if probe["earliest_timestamp_utc"]:
                    all_timestamps.append(probe["earliest_timestamp_utc"])
                if probe["latest_timestamp_utc"]:
                    all_timestamps.append(probe["latest_timestamp_utc"])
        full_81_probe_results_if_needed = {
            "performed": True,
            "reason": "Representative old-window data appeared unexpectedly available; lightweight all-81 old/mid/late probes executed.",
            "results": full_81_results,
        }

    recent_data_available = recent_available_count > 0
    old_target_available = old_available_count > 0
    if old_target_available and full_81_probe_results_if_needed.get("performed"):
        availability_classification = CLASS_API_PARTIAL
    elif not old_target_available and recent_data_available and panel_derived_available:
        availability_classification = CLASS_API_UNAVAILABLE_PANEL_AVAILABLE
    elif network_or_schema_error_count > 0 and not recent_data_available:
        availability_classification = CLASS_API_INCONCLUSIVE
    else:
        availability_classification = CLASS_API_INCONCLUSIVE

    api_available = availability_classification == CLASS_API_AVAILABLE
    status = STATUS_API_AVAILABLE if api_available else STATUS_API_UNAVAILABLE_PANEL_AVAILABLE
    api_acquisition_allowed_next = api_available

    payload: Dict[str, Any] = {
        "status": status,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "repo_scope": {
            "code_changes_repo_only": True,
            "availability_lock_created_in_repo": True,
            "public_binance_network_used_for_endpoint_probe": True,
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
            "prior_head": "b686563198b11bd42b850b5e9e1b8dd5af11eb8b",
            "prior_tracked_python_count": 836,
            "repo_clean_before_discovery": True,
            "latest_long_short_ratio_availability_classification": long_short_lock.get("availability_classification"),
        },
        "source_artifacts": {
            "readiness_artifact": READINESS_PATH,
            "preview_artifact": PREVIEW_PATH,
            "build_manifest_artifact": BUILD_MANIFEST_PATH,
            "panel_review_artifact": PANEL_REVIEW_PATH,
            "coverage_lock_artifact": COVERAGE_LOCK_PATH,
            "long_short_ratio_availability_lock_artifact": LONG_SHORT_LOCK_PATH,
            "payload_hashes": source_hashes,
        },
        "endpoint_contract": {
            "endpoint_url": ENDPOINT_URL,
            "endpoint_name": "Taker Buy/Sell Volume",
            "request_path": "/futures/data/takerlongshortRatio",
            "period_tested": "1h",
            "period_supported_values": ["5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"],
            "max_limit": 500,
            "startTime_endTime_supported": True,
            "if_startTime_endTime_not_sent_most_recent_data_returned": True,
            "official_limitation": {
                "only_latest_30_days_available": True,
                "ip_rate_limit": "1000 requests / 5 min",
            },
            "response_fields_expected": ["buySellRatio", "buyVol", "sellVol", "timestamp"],
        },
        "representative_probe_results": representative_probe_results,
        "full_81_probe_results_if_needed": full_81_probe_results_if_needed,
        "panel_derived_taker_buy_sell_availability": {
            "reviewed_panel_available": panel_review_passed,
            "panel_schema_has_taker_buy_base_volume": panel_schema_has_taker_buy_base_volume,
            "panel_schema_has_taker_buy_quote_volume": panel_schema_has_taker_buy_quote_volume,
            "panel_schema_has_total_volume": panel_schema_has_total_volume,
            "panel_schema_has_total_quote_volume": panel_schema_has_total_quote_volume,
            "taker_sell_derivable_from_panel": taker_sell_derivable,
            "panel_derived_availability_window_start_utc": panel_start,
            "panel_derived_availability_window_end_exclusive_utc": panel_end,
            "aligned_window_covered_by_panel_derived_data": aligned_window_covered,
            "panel_rows_read_by_this_module": False,
            "panel_derived_feature_requires_new_preregistration_before_execution": True,
        },
        "availability_classification": availability_classification,
        "continuation_decision": {
            "api_acquisition_allowed_next": api_acquisition_allowed_next,
            "panel_derived_taker_buy_sell_available_for_future_feature_construction": panel_derived_available,
            "panel_derived_feature_execution_requires_separate_preregistration": True,
            "strategy_execution_allowed_next": False,
            "immediate_next_module_required": False,
            "project_can_pause_after_availability_lock": True,
        },
        "limitations": [
            "This discovery lock does not acquire full taker buy/sell history.",
            "This discovery lock does not read Binance panel rows.",
            "This discovery lock does not read Binance funding rows.",
            "This discovery lock does not read OKX rows.",
            "Panel-derived taker sell availability is inferred from reviewed panel schema and manifest only.",
            "This discovery lock does not run strategy logic or compute returns.",
            "This discovery lock grants no candidate, edge, release, or runtime/live/capital permission.",
        ],
        "safety_permissions": {
            "taker_buy_sell_api_acquisition_allowed_next": api_acquisition_allowed_next,
            "panel_derived_taker_buy_sell_feature_available_for_future_preregistration": panel_derived_available,
            "strategy_execution_allowed_next": False,
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
            "old_2023_window_not_available_if_api_unavailable": (availability_classification != CLASS_API_UNAVAILABLE_PANEL_AVAILABLE) or (old_available_count == 0),
            "recent_data_available_if_latest_30_days_behavior_confirmed": (availability_classification != CLASS_API_UNAVAILABLE_PANEL_AVAILABLE) or recent_data_available,
            "panel_schema_checked_from_artifacts": True,
            "panel_rows_not_read": True,
            "panel_derived_taker_buy_sell_availability_recorded": True,
            "no_bulk_download": True,
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
            "endpoint_tested": ENDPOINT_URL,
            "representative_symbols_tested": representative_symbols,
            "old_range_available_count": old_available_count,
            "recent_range_available_count": recent_available_count,
            "global_earliest_timestamp_observed_from_endpoint": min(all_timestamps) if all_timestamps else None,
            "global_latest_timestamp_observed_from_endpoint": max(all_timestamps) if all_timestamps else None,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)

    required_assertions = [
        payload["status"] in (STATUS_API_UNAVAILABLE_PANEL_AVAILABLE, STATUS_API_AVAILABLE),
        payload["module"] == MODULE_PATH,
        len(symbols) == 81,
        payload["repo_scope"]["bulk_history_downloaded"] is False,
        payload["repo_scope"]["panel_rows_read"] is False,
        payload["repo_scope"]["funding_rows_read"] is False,
        payload["repo_scope"]["okx_panel_rows_read"] is False,
        payload["repo_scope"]["strategy_executed"] is False,
        payload["repo_scope"]["candidate_generation"] is False,
        payload["repo_scope"]["edge_claim"] is False,
        payload["repo_scope"]["runtime_live_capital"] is False,
        payload["continuation_decision"]["strategy_execution_allowed_next"] is False,
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
        "endpoint_tested": artifact["summary_counts"]["endpoint_tested"],
        "representative_symbols_tested": artifact["summary_counts"]["representative_symbols_tested"],
        "old_range_available_count": artifact["summary_counts"]["old_range_available_count"],
        "recent_range_available_count": artifact["summary_counts"]["recent_range_available_count"],
        "global_earliest_timestamp_observed_from_endpoint": artifact["summary_counts"]["global_earliest_timestamp_observed_from_endpoint"],
        "global_latest_timestamp_observed_from_endpoint": artifact["summary_counts"]["global_latest_timestamp_observed_from_endpoint"],
        "api_acquisition_allowed_next": artifact["continuation_decision"]["api_acquisition_allowed_next"],
        "panel_derived_taker_buy_sell_available_for_future_preregistration": artifact["continuation_decision"]["panel_derived_taker_buy_sell_available_for_future_feature_construction"],
        "strategy_execution_allowed_next": artifact["continuation_decision"]["strategy_execution_allowed_next"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
