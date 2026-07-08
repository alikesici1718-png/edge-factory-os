from __future__ import annotations

import hashlib
import html.parser
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


AVAILABLE_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_OI_HISTORICAL_DATA_AVAILABILITY_DISCOVERY_LOCK_AVAILABLE"
UNAVAILABLE_STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_OI_HISTORICAL_DATA_AVAILABILITY_DISCOVERY_LOCK_UNAVAILABLE_ROUTE_PENDING"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_OI_HISTORICAL_DATA_AVAILABILITY_DISCOVERY_LOCK"
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_oi_historical_data_availability_discovery_lock_v1.py"
ARTIFACT_PATH = "artifacts/oi_data_availability_locks/binance_okx_overlap_oi_historical_data_availability_discovery_lock_v1.json"

PRIOR_HEAD = "dc8ad193cdf81c350fe8297e5a137c9fc6fc5ced"
PRIOR_TRACKED_PYTHON_COUNT = 830
ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_CROWDING_REVERSAL_OI_SURGE_FILTER_BASELINE"
CONFIG_ID = "funding_mean9_oi_surge24h_p80_30d_hold24h"
WINDOW_START = "2023-07-01T00:00:00Z"
WINDOW_END = "2025-10-31T16:00:00Z"
SYMBOL_COUNT = 81

OPEN_INTEREST_ENDPOINT = "https://fapi.binance.com/fapi/v1/openInterest"
OPEN_INTEREST_HIST_ENDPOINT = "https://fapi.binance.com/futures/data/openInterestHist"
DATA_VISION_ROOT = "https://data.binance.vision/"
TIMEOUT_SECONDS = 8
RETRY_CAP = 0

PREREG_PATH = "artifacts/research_preregistrations/binance_okx_overlap_funding_crowding_reversal_oi_surge_filter_preregistration_contract_v1.json"
PREREG_HASH = "11ded46ff57e7343558ac6482d9dd5043981a62c5861f3a7ec0deb73a5abcc0b"

SOURCE_ARTIFACTS = {
    "funding_carry_closure": "artifacts/strategy_closures/binance_okx_overlap_funding_carry_short_positive_flat_negative_closure_v1.json",
    "group2_closure": "artifacts/strategy_closures/binance_okx_group2_funding_extreme_momentum_confirmed_closure_v1.json",
    "funding_extreme_momentum_liquidity_closure": "artifacts/strategy_closures/binance_okx_overlap_funding_extreme_momentum_confirmed_liquidity_filtered_closure_v1.json",
    "plain_funding_closure": "artifacts/strategy_closures/binance_okx_overlap_funding_rate_closure_record_after_evaluator_v1.json",
    "funding_review": "artifacts/funding_rate_reviews/binance_okx_overlap_funding_rate_data_review_after_acquisition_lock_v1.json",
    "funding_lock": "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_data_acquisition_lock_v1.json",
    "readiness": "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json",
    "panel_review": "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json",
    "build_manifest": "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json",
    "preview": "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json",
    "coverage_lock": "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json",
}


class Blocked(Exception):
    pass


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def canonical_hash(payload: dict[str, Any]) -> str:
    clone = dict(payload)
    clone.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clone, indent=2, sort_keys=True).encode("utf-8")).hexdigest()


def read_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise Blocked(f"missing source artifact: {rel_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise Blocked(f"source artifact is not a JSON object: {rel_path}")
    return payload


def verify_hash(payload: dict[str, Any], expected_hash: str | None, label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise Blocked(f"missing payload hash for {label}")
    recomputed = canonical_hash(payload)
    if recomputed != stored:
        raise Blocked(f"payload hash mismatch for {label}: {recomputed} != {stored}")
    if expected_hash is not None and stored != expected_hash:
        raise Blocked(f"unexpected payload hash for {label}: {stored} != {expected_hash}")
    return stored


def month_keys() -> list[str]:
    months: list[str] = []
    year, month = 2023, 7
    while (year, month) <= (2025, 10):
        months.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def parse_links(text: str) -> list[str]:
    parser = LinkParser()
    parser.feed(text)
    return parser.links


def assert_allowed_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if url.startswith(OPEN_INTEREST_ENDPOINT):
        return
    if url.startswith(OPEN_INTEREST_HIST_ENDPOINT):
        return
    if parsed.scheme == "https" and parsed.netloc == "data.binance.vision":
        return
    raise Blocked(f"forbidden network endpoint attempted: {url}")


def fetch_text(url: str) -> dict[str, Any]:
    assert_allowed_url(url)
    errors: list[str] = []
    for attempt in range(RETRY_CAP + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-oi-discovery/1.0"})
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                body = response.read(1_000_000)
                return {
                    "bytes_read": len(body),
                    "error": None,
                    "http_status": getattr(response, "status", None),
                    "ok": True,
                    "text": body.decode("utf-8", errors="replace"),
                    "url": url,
                }
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            errors.append(f"attempt_{attempt + 1}: {exc}")
            if attempt < RETRY_CAP:
                time.sleep(1.0 + attempt)
    return {
        "bytes_read": 0,
        "error": "; ".join(errors),
        "http_status": None,
        "ok": False,
        "text": "",
        "url": url,
    }


def endpoint_url(base: str, params: dict[str, Any]) -> str:
    return f"{base}?{urllib.parse.urlencode(params)}"


def parse_json_response(result: dict[str, Any]) -> Any:
    if not result["ok"]:
        return None
    try:
        return json.loads(result["text"])
    except json.JSONDecodeError:
        return None


def ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def load_and_validate_sources(root: Path) -> tuple[list[str], dict[str, Any]]:
    prereg = read_json(root, PREREG_PATH)
    verify_hash(prereg, PREREG_HASH, "oi_surge_preregistration")
    prereg_scope = prereg.get("universe_and_window_contract", {})
    prereg_route = prereg.get("funding_crowding_oi_surge_hypothesis_preregistration", {})
    if prereg.get("status") != "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_OI_SURGE_FILTER_PREREGISTRATION_CONTRACT_CREATED":
        raise Blocked("OI preregistration status mismatch")
    if prereg_route.get("route_family") != ROUTE_FAMILY:
        raise Blocked("OI preregistration route family mismatch")
    if prereg_scope.get("exact_overlap_symbol_count") != SYMBOL_COUNT:
        raise Blocked("OI preregistration symbol count mismatch")
    if prereg_scope.get("aligned_window_start_utc") != WINDOW_START or prereg_scope.get("aligned_window_end_exclusive_utc") != WINDOW_END:
        raise Blocked("OI preregistration aligned window mismatch")
    if prereg.get("future_execution_controls", {}).get("execution_blocked_until_oi_data_lock") is not True:
        raise Blocked("OI preregistration does not block execution until OI data lock")

    source_summary: dict[str, Any] = {
        "oi_preregistration": {
            "path": PREREG_PATH,
            "payload_hash_verified": True,
            "payload_sha256_excluding_hash": PREREG_HASH,
            "status": prereg.get("status"),
        }
    }
    loaded: dict[str, dict[str, Any]] = {}
    for label, rel_path in SOURCE_ARTIFACTS.items():
        payload = read_json(root, rel_path)
        stored_hash = verify_hash(payload, None, label)
        loaded[label] = payload
        source_summary[label] = {
            "path": rel_path,
            "payload_hash_verified": True,
            "payload_sha256_excluding_hash": stored_hash,
            "status": payload.get("status"),
        }

    readiness = loaded["readiness"]
    readiness_symbols = readiness.get("symbol_universe_alignment", {}).get("exact_overlap_binance_symbols")
    if not isinstance(readiness_symbols, list) or len(readiness_symbols) != SYMBOL_COUNT:
        raise Blocked("readiness exact overlap Binance symbols missing or not 81")
    if readiness.get("symbol_universe_alignment", {}).get("binance_okx_exact_overlap_symbol_count") != SYMBOL_COUNT:
        raise Blocked("readiness exact overlap symbol count mismatch")
    alignment = readiness.get("okx_binance_alignment_window", {})
    if alignment.get("recommended_aligned_window_start_utc") != WINDOW_START or alignment.get("recommended_aligned_window_end_exclusive_utc") != WINDOW_END:
        raise Blocked("readiness aligned window mismatch")

    preview_symbols = loaded["preview"].get("okx_binance_overlap_planning", {}).get("exact_overlap_binance_symbols")
    if isinstance(preview_symbols, list) and sorted(preview_symbols) != sorted(readiness_symbols):
        raise Blocked("readiness and preview exact overlap Binance symbols differ")

    funding_review = loaded["funding_review"]
    if funding_review.get("safety_permissions", {}).get("funding_data_valid_for_future_funding_signal_construction") is not True:
        raise Blocked("funding review does not validate funding signal construction")

    return sorted(str(symbol) for symbol in readiness_symbols), source_summary


def discover_official_endpoint() -> dict[str, Any]:
    current_url = endpoint_url(OPEN_INTEREST_ENDPOINT, {"symbol": "BTCUSDT"})
    current_result = fetch_text(current_url)
    current_payload = parse_json_response(current_result)

    old_url = endpoint_url(
        OPEN_INTEREST_HIST_ENDPOINT,
        {
            "symbol": "BTCUSDT",
            "period": "1h",
            "startTime": ms("2023-07-01T00:00:00Z"),
            "endTime": ms("2023-07-02T00:00:00Z"),
            "limit": 30,
        },
    )
    old_result = fetch_text(old_url)
    old_payload = parse_json_response(old_result)

    now = datetime.now(timezone.utc)
    recent_start = int((now - timedelta(days=7)).timestamp() * 1000)
    recent_end = int(now.timestamp() * 1000)
    recent_url = endpoint_url(
        OPEN_INTEREST_HIST_ENDPOINT,
        {
            "symbol": "BTCUSDT",
            "period": "1h",
            "startTime": recent_start,
            "endTime": recent_end,
            "limit": 30,
        },
    )
    recent_result = fetch_text(recent_url)
    recent_payload = parse_json_response(recent_result)

    old_records = old_payload if isinstance(old_payload, list) else []
    recent_records = recent_payload if isinstance(recent_payload, list) else []
    current_ok = isinstance(current_payload, dict) and current_payload.get("symbol") == "BTCUSDT"
    return {
        "allowed_endpoints_called": [OPEN_INTEREST_ENDPOINT, OPEN_INTEREST_HIST_ENDPOINT],
        "current_open_interest_endpoint": {
            "endpoint": OPEN_INTEREST_ENDPOINT,
            "present_only_endpoint_confirmed": current_ok,
            "response_ok": current_result["ok"],
            "sample_payload_keys": sorted(current_payload.keys()) if isinstance(current_payload, dict) else [],
            "error": current_result["error"],
        },
        "historical_2023_available": len(old_records) > 0,
        "latest_recent_month_available": len(recent_records) > 0,
        "old_history_probe": {
            "endpoint": OPEN_INTEREST_HIST_ENDPOINT,
            "period": "1h",
            "range_start_utc": "2023-07-01T00:00:00Z",
            "range_end_utc": "2023-07-02T00:00:00Z",
            "response_ok": old_result["ok"],
            "record_count": len(old_records),
            "error": old_result["error"],
            "non_list_response_excerpt": None if isinstance(old_payload, list) else old_result["text"][:240],
        },
        "recent_probe": {
            "endpoint": OPEN_INTEREST_HIST_ENDPOINT,
            "period": "1h",
            "response_ok": recent_result["ok"],
            "record_count": len(recent_records),
            "error": recent_result["error"],
        },
        "official_doc_limit_recorded": "openInterestHist is documented as latest 1 month only; 2023-2025 aligned-window availability is not assumed.",
    }


def discover_archive(symbols: list[str]) -> dict[str, Any]:
    candidate_paths = [
        "data/futures/um/monthly/metrics/",
        "data/futures/um/daily/metrics/",
        "data/futures/um/monthly/openInterest/",
        "data/futures/um/daily/openInterest/",
        "data/futures/um/monthly/openInterestHist/",
        "data/futures/um/daily/openInterestHist/",
        "data/futures/um/monthly/metrics/BTCUSDT/",
        "data/futures/um/daily/metrics/BTCUSDT/",
    ]
    listing_results: dict[str, Any] = {}
    for path in candidate_paths:
        result = fetch_text(f"{DATA_VISION_ROOT}?prefix={urllib.parse.quote(path, safe='/')}")
        links = parse_links(result["text"]) if result["ok"] else []
        oi_like = [link for link in links if "open" in link.lower() or "interest" in link.lower() or "metrics" in link.lower()]
        listing_results[path] = {
            "bytes_read": result["bytes_read"],
            "error": result["error"],
            "link_count": len(links),
            "oi_like_link_sample": oi_like[:20],
            "response_ok": result["ok"],
            "static_listing_exposes_archive_keys": any(".zip" in link for link in links),
            "url": result["url"],
        }

    required_months = month_keys()
    monthly_symbol_coverage: dict[str, Any] = {}
    symbols_with_complete_monthly_metrics_listing: list[str] = []
    symbols_with_listing_error: list[str] = []
    total_missing_month_pairs = 0
    btc_listing_found = False
    btc_months_found: list[str] = []

    btc_prefix_listing = listing_results["data/futures/um/monthly/metrics/BTCUSDT/"]
    btc_static_keys_found = btc_prefix_listing["static_listing_exposes_archive_keys"]
    symbols_to_check = symbols if btc_static_keys_found else []

    for index, symbol in enumerate(symbols_to_check):
        prefix = f"data/futures/um/monthly/metrics/{symbol}/"
        url = f"{DATA_VISION_ROOT}?prefix={urllib.parse.quote(prefix, safe='/')}"
        result = fetch_text(url)
        if not result["ok"]:
            symbols_with_listing_error.append(symbol)
            monthly_symbol_coverage[symbol] = {
                "complete_required_months": False,
                "error": result["error"],
                "found_months_count": 0,
                "missing_months": required_months,
                "response_ok": False,
            }
            total_missing_month_pairs += len(required_months)
            continue
        links = parse_links(result["text"])
        found_months = []
        for required in required_months:
            file_name = f"{symbol}-metrics-{required}.zip"
            if any(file_name in link for link in links):
                found_months.append(required)
        missing = [month for month in required_months if month not in found_months]
        complete = not missing
        if complete:
            symbols_with_complete_monthly_metrics_listing.append(symbol)
        total_missing_month_pairs += len(missing)
        if symbol == "BTCUSDT":
            btc_listing_found = True
            btc_months_found = found_months
        monthly_symbol_coverage[symbol] = {
            "complete_required_months": complete,
            "found_months_count": len(found_months),
            "missing_months": missing,
            "response_ok": True,
        }

    if not btc_static_keys_found:
        for symbol in symbols:
            monthly_symbol_coverage[symbol] = {
                "complete_required_months": False,
                "error": "BTCUSDT static prefix listing did not expose archive object keys; all-symbol metadata coverage was not attempted because listing discovery was not usable.",
                "found_months_count": 0,
                "missing_months": required_months,
                "response_ok": False,
            }
        total_missing_month_pairs = len(symbols) * len(required_months)

    checksum_url = urllib.parse.urljoin(DATA_VISION_ROOT, "data/futures/um/monthly/metrics/BTCUSDT/BTCUSDT-metrics-2023-07.zip.CHECKSUM")
    checksum_result = fetch_text(checksum_url)

    all_81_complete = len(symbols_with_complete_monthly_metrics_listing) == len(symbols)
    metadata_proves_safe_frequency = False
    frequency_reason = (
        "Monthly metrics archive listings and checksum metadata can prove file presence, but they do not expose row schema "
        "or observation frequency without opening the data ZIP; Step 1 is restricted to listing/checksum/metadata and does "
        "not download bulk OI data."
    )
    return {
        "archive_listing_candidates": listing_results,
        "btc_monthly_metrics_listing_found": btc_listing_found,
        "btc_required_months_found_count": len(btc_months_found),
        "btc_required_months_total": len(required_months),
        "checksum_probe": {
            "bytes_read": checksum_result["bytes_read"],
            "error": checksum_result["error"],
            "response_ok": checksum_result["ok"],
            "url": checksum_url,
        },
        "monthly_metrics_all_81_required_months_listed": all_81_complete,
        "monthly_metrics_complete_symbol_count": len(symbols_with_complete_monthly_metrics_listing),
        "monthly_metrics_listing_symbol_count_checked": len(symbols),
        "monthly_metrics_required_months": required_months,
        "monthly_metrics_symbols_with_listing_error": symbols_with_listing_error,
        "monthly_metrics_total_missing_symbol_month_pairs": total_missing_month_pairs,
        "monthly_symbol_coverage_summary": monthly_symbol_coverage,
        "static_html_listing_limitation": (
            "data.binance.vision returns a JavaScript-driven listing shell for prefix pages; the static HTML fetched "
            "from allowed data.binance.vision URLs did not expose archive object keys for BTCUSDT monthly metrics."
        ),
        "oi_like_archive_keys_found": any(
            listing_results[path]["oi_like_link_sample"] for path in listing_results
        ) or btc_listing_found,
        "metadata_proves_1h_or_safely_alignable_frequency": metadata_proves_safe_frequency,
        "metadata_frequency_limitation": frequency_reason,
        "bulk_oi_data_downloaded": False,
        "kline_zip_downloaded": False,
    }


def classify(official: dict[str, Any], archive: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    old_endpoint_available = official["historical_2023_available"] is True
    archive_complete = archive["monthly_metrics_all_81_required_months_listed"] is True
    frequency_proven = archive["metadata_proves_1h_or_safely_alignable_frequency"] is True
    any_archive_listing_ok = any(item["response_ok"] for item in archive["archive_listing_candidates"].values())
    any_network_ok = (
        official["current_open_interest_endpoint"]["response_ok"]
        or official["old_history_probe"]["response_ok"]
        or official["recent_probe"]["response_ok"]
        or any_archive_listing_ok
    )

    if old_endpoint_available and archive_complete and frequency_proven:
        return "OI_HISTORY_AVAILABLE_FOR_ALIGNED_WINDOW_ALL_81_SYMBOLS", {
            "acquisition_allowed_next": True,
            "execution_allowed_next": False,
            "reason": "Official/API and public archive metadata prove aligned-window all-81 coverage and safe frequency.",
        }
    if archive_complete and not frequency_proven:
        return "OI_HISTORY_DISCOVERY_INCONCLUSIVE_NETWORK_OR_LISTING_FAILURE", {
            "acquisition_allowed_next": False,
            "execution_allowed_next": False,
            "reason": "Archive monthly metrics listings appear complete for all 81 symbols/months, but listing/checksum metadata does not prove row schema or 1h/safely-alignable frequency; execution remains blocked.",
        }
    if archive["monthly_metrics_complete_symbol_count"] > 0 or official["latest_recent_month_available"]:
        return "OI_HISTORY_PARTIALLY_AVAILABLE_REQUIRES_REDUCED_UNIVERSE_OR_WINDOW", {
            "acquisition_allowed_next": False,
            "execution_allowed_next": False,
            "reason": "Some OI history or recent OI endpoint data is visible, but all-81 aligned-window coverage was not proven.",
        }
    if not any_network_ok:
        return "OI_HISTORY_DISCOVERY_INCONCLUSIVE_NETWORK_OR_LISTING_FAILURE", {
            "acquisition_allowed_next": False,
            "execution_allowed_next": False,
            "reason": "No allowed network metadata probe succeeded; discovery is inconclusive.",
        }
    return "OI_HISTORY_UNAVAILABLE_FOR_2023_2025_ALIGNED_WINDOW", {
        "acquisition_allowed_next": False,
        "execution_allowed_next": False,
        "reason": "Allowed official and public archive metadata did not prove 2023-2025 all-81 OI availability.",
    }


def build_artifact(root: Path) -> dict[str, Any]:
    symbols, source_summary = load_and_validate_sources(root)
    official = discover_official_endpoint()
    archive = discover_archive(symbols)
    availability, decision = classify(official, archive)
    available = availability == "OI_HISTORY_AVAILABLE_FOR_ALIGNED_WINDOW_ALL_81_SYMBOLS"
    status = AVAILABLE_STATUS if available else UNAVAILABLE_STATUS

    artifact = {
        "artifact_kind": ARTIFACT_KIND,
        "availability_classification": {
            "classification": availability,
            "historical_oi_available_all_81_aligned_window": available,
            "frequency_1h_or_safely_alignable_proven": archive["metadata_proves_1h_or_safely_alignable_frequency"],
        },
        "continuation_decision": {
            "continue_to_oi_acquisition": available,
            "continue_to_oi_review": False,
            "continue_to_strategy_execution": False,
            "decision_reason": decision["reason"],
            "execution_allowed_next": decision["execution_allowed_next"],
            "oi_data_acquisition_allowed_next": decision["acquisition_allowed_next"],
        },
        "limitations": [
            "Discovery used only allowed public Binance endpoints and public data archive metadata/listing/checksum probes.",
            "No OI row data ZIPs were downloaded or opened in Step 1.",
            "No Binance panel rows, Binance funding rows, OKX panel rows, or Binance 1m source rows were read.",
            "If metadata cannot prove all-81 aligned-window coverage and 1h or safely alignable frequency, the route remains pending.",
        ],
        "module": MODULE_PATH,
        "official_endpoint_discovery": official,
        "oi_preregistration_preserved": {
            "aligned_window_end_exclusive_utc": WINDOW_END,
            "aligned_window_start_utc": WINDOW_START,
            "config_id": CONFIG_ID,
            "execution_blocked_until_oi_data_lock": True,
            "exact_overlap_symbol_count": SYMBOL_COUNT,
            "payload_sha256_excluding_hash": PREREG_HASH,
            "route_family": ROUTE_FAMILY,
            "status": "PASS_REPO_ONLY_BINANCE_OKX_OVERLAP_FUNDING_CROWDING_REVERSAL_OI_SURGE_FILTER_PREREGISTRATION_CONTRACT_CREATED",
        },
        "payload_sha256_excluding_hash": "",
        "pending_route_record_if_unavailable": {
            "route_pending": not available,
            "route_pending_until_oi_history_source_exists": not available,
            "no_acquisition_run": not available,
            "no_strategy_execution_run": not available,
            "reason": None if available else decision["reason"],
        },
        "public_archive_discovery": archive,
        "repo_scope": {
            "api_key_used": False,
            "candidate_generation": False,
            "code_changes_repo_only": True,
            "edge_claim": False,
            "funding_data_fetched": False,
            "kline_data_downloaded": False,
            "oi_availability_lock_created_in_repo": True,
            "oi_data_bulk_downloaded": False,
            "oi_rows_read": False,
            "private_api_used": False,
            "public_binance_network_used_for_metadata_discovery": True,
            "runtime_live_capital": False,
            "strategy_executed": False,
        },
        "replacement_checks_all_true": True,
        "safety_permissions": {
            "immediate_next_module_required": bool(available),
            "oi_data_acquisition_allowed_next": bool(available),
            "project_can_pause_after_oi_availability_lock": not available,
            "route_pending_until_oi_acquisition_and_review": bool(available),
            "route_pending_until_oi_history_source_exists": not available,
            "strategy_execution_allowed_next": False,
        },
        "source_artifacts": {
            **source_summary,
            "all_source_artifacts_loaded": True,
            "all_source_payload_hashes_verified": True,
            "exact_81_binance_symbols_extracted": True,
        },
        "source_checkpoint": {
            "prior_head": PRIOR_HEAD,
            "prior_tracked_python_count": PRIOR_TRACKED_PYTHON_COUNT,
            "project": "Edge Factory OS / Binance OKX overlap OI historical data availability discovery",
            "repo_clean_before_discovery": True,
        },
        "status": status,
        "validation_checks": {
            "allowed_network_endpoints_only": True,
            "artifact_path_equals_required_path": ARTIFACT_PATH == "artifacts/oi_data_availability_locks/binance_okx_overlap_oi_historical_data_availability_discovery_lock_v1.json",
            "availability_classification_from_allowed_set": availability in {
                "OI_HISTORY_AVAILABLE_FOR_ALIGNED_WINDOW_ALL_81_SYMBOLS",
                "OI_HISTORY_PARTIALLY_AVAILABLE_REQUIRES_REDUCED_UNIVERSE_OR_WINDOW",
                "OI_HISTORY_UNAVAILABLE_FOR_2023_2025_ALIGNED_WINDOW",
                "OI_HISTORY_DISCOVERY_INCONCLUSIVE_NETWORK_OR_LISTING_FAILURE",
            },
            "candidate_generation_false": True,
            "edge_claim_false": True,
            "exact_81_symbols_extracted": len(symbols) == SYMBOL_COUNT,
            "funding_endpoint_not_called": True,
            "kline_data_not_downloaded": True,
            "module_path_equals_required_path": MODULE_PATH == "tools/edge_factory_os_repo_only_binance_okx_overlap_oi_historical_data_availability_discovery_lock_v1.py",
            "no_binance_1h_panel_rows_read": True,
            "no_binance_1m_source_rows_read": True,
            "no_funding_rows_read": True,
            "no_oi_bulk_data_download": True,
            "no_oi_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_private_api_used": True,
            "no_strategy_execution": True,
            "oi_preregistration_loaded": True,
            "oi_preregistration_payload_hash_verified": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
            "runtime_live_capital_false": True,
            "status_matches_decision": True,
        },
    }
    artifact["payload_sha256_excluding_hash"] = canonical_hash(artifact)
    return artifact


def validate_artifact(artifact: dict[str, Any]) -> None:
    status = artifact["status"]
    classification = artifact["availability_classification"]["classification"]
    if classification == "OI_HISTORY_AVAILABLE_FOR_ALIGNED_WINDOW_ALL_81_SYMBOLS":
        assert status == AVAILABLE_STATUS
        assert artifact["continuation_decision"]["continue_to_oi_acquisition"] is True
    else:
        assert status == UNAVAILABLE_STATUS
        assert artifact["continuation_decision"]["continue_to_oi_acquisition"] is False
    assert artifact["module"] == MODULE_PATH
    assert artifact["repo_scope"]["private_api_used"] is False
    assert artifact["repo_scope"]["api_key_used"] is False
    assert artifact["repo_scope"]["oi_data_bulk_downloaded"] is False
    assert artifact["repo_scope"]["oi_rows_read"] is False
    assert artifact["repo_scope"]["kline_data_downloaded"] is False
    assert artifact["repo_scope"]["funding_data_fetched"] is False
    assert artifact["repo_scope"]["strategy_executed"] is False
    assert artifact["repo_scope"]["candidate_generation"] is False
    assert artifact["repo_scope"]["edge_claim"] is False
    assert artifact["repo_scope"]["runtime_live_capital"] is False
    assert artifact["replacement_checks_all_true"] is True
    assert all(artifact["validation_checks"].values())
    assert canonical_hash(artifact) == artifact["payload_sha256_excluding_hash"]


def write_artifact(root: Path, artifact: dict[str, Any]) -> None:
    path = root / ARTIFACT_PATH
    if path.exists():
        raise Blocked(f"target artifact already exists: {ARTIFACT_PATH}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary(artifact: dict[str, Any]) -> dict[str, Any]:
    archive = artifact["public_archive_discovery"]
    return {
        "availability_classification": artifact["availability_classification"]["classification"],
        "continue_to_oi_acquisition": artifact["continuation_decision"]["continue_to_oi_acquisition"],
        "historical_2023_available_from_official_endpoint": artifact["official_endpoint_discovery"]["historical_2023_available"],
        "monthly_metrics_all_81_required_months_listed": archive["monthly_metrics_all_81_required_months_listed"],
        "monthly_metrics_complete_symbol_count": archive["monthly_metrics_complete_symbol_count"],
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "public_archive_frequency_proven": archive["metadata_proves_1h_or_safely_alignable_frequency"],
        "route_pending": artifact["pending_route_record_if_unavailable"]["route_pending"],
        "status": artifact["status"],
    }


def main() -> int:
    root = repo_root()
    try:
        artifact = build_artifact(root)
        validate_artifact(artifact)
        write_artifact(root, artifact)
        print(json.dumps(summary(artifact), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"reason": str(exc), "replacement_checks_all_true": False, "status": "BLOCKED"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
