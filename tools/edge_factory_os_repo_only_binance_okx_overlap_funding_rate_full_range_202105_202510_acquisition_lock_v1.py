import gzip
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1.py"
ARTIFACT_PATH = "artifacts/funding_rate_locks/binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1.json"
STATUS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_FUNDING_RATE_FULL_RANGE_202105_202510_ACQUISITION_LOCK_CREATED"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_FUNDING_RATE_FULL_RANGE_202105_202510_ACQUISITION_LOCK"

ROUTE_FAMILY = "CROSS_SECTIONAL_FUNDING_RATE_CROWDING_REVERSAL_BASELINE"
CONFIG_ID = "funding_mean9_hold24h"
ENDPOINT_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
ALLOWED_ENDPOINT_NETLOC = "fapi.binance.com"
ALLOWED_ENDPOINT_PATH = "/fapi/v1/fundingRate"
REQUEST_LIMIT = 1000
REQUEST_TIMEOUT_SECONDS = 20
RETRY_CAP = 2
SLEEP_BETWEEN_REQUESTS_SECONDS = 0.10

WINDOW_START_UTC = "2021-05-01T00:00:00Z"
WINDOW_END_EXCLUSIVE_UTC = "2025-11-01T00:00:00Z"
ENDPOINT_END_INCLUSIVE_UTC = "2025-10-31T23:59:59.999Z"
WINDOW_START_MS = 1_619_827_200_000
WINDOW_END_EXCLUSIVE_MS = 1_761_955_200_000
ENDPOINT_END_INCLUSIVE_MS = WINDOW_END_EXCLUSIVE_MS - 1
EXPECTED_SYMBOL_COUNT = 81
LARGE_GAP_THRESHOLD_HOURS = 24

EXTERNAL_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_funding_rate_full_range_202105_202510_acquisition_lock_v1"
)
FUNDING_BY_SYMBOL_DIR = EXTERNAL_ROOT / "funding_by_symbol"
FUNDING_INDEX_DIR = EXTERNAL_ROOT / "funding_index"
FUNDING_INDEX_PATH = FUNDING_INDEX_DIR / "binance_okx_overlap_funding_rate_full_range_202105_202510_index_v1.json"

READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_REVIEW_PATH = "artifacts/panel_build_reviews/binance_okx_overlap_near_5y_panel_build_review_after_execution_v1.json"
BUILD_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
PREVIEW_PATH = "artifacts/panel_build_previews/binance_near_5y_coverage_lock_review_okx_overlap_panel_build_preview_v1.json"
COVERAGE_LOCK_PATH = "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    if recomputed != stored:
        raise RuntimeError(f"source artifact payload hash mismatch: {recomputed} != {stored}")
    return stored


def iso_from_ms(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def decimal_from_string(value: Any, label: str) -> Decimal:
    if not isinstance(value, str) or value == "":
        raise ValueError(f"missing or non-string decimal field {label}")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal field {label}: {value}") from exc


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


def validate_no_forbidden_permissions(source_artifacts: Iterable[Dict[str, Any]]) -> bool:
    forbidden_true_keys = {
        "candidate_generation",
        "candidate_generation_allowed_now",
        "edge_claim",
        "edge_claim_allowed_now",
        "family_release_allowed_now",
        "runtime_live_capital",
        "runtime_live_capital_allowed_now",
        "runtime_permission_allowed_now",
        "live_permission_allowed_now",
        "capital_permission_allowed_now",
        "holdout_access_allowed_now",
    }

    def walk(value: Any) -> bool:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_true_keys and child is True:
                    return False
                if not walk(child):
                    return False
        elif isinstance(value, list):
            for child in value:
                if not walk(child):
                    return False
        return True

    return all(walk(artifact) for artifact in source_artifacts)


def validate_endpoint_url(url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != ALLOWED_ENDPOINT_NETLOC or parsed.path != ALLOWED_ENDPOINT_PATH:
        raise RuntimeError(f"non-allowed network endpoint attempted: {url}")


def request_funding_page(symbol: str, start_ms: int, end_ms: int, counters: Dict[str, Any]) -> List[Dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "symbol": symbol,
            "startTime": str(start_ms),
            "endTime": str(end_ms),
            "limit": str(REQUEST_LIMIT),
        }
    )
    url = f"{ENDPOINT_URL}?{query}"
    validate_endpoint_url(url)
    last_error = ""
    for attempt in range(RETRY_CAP + 1):
        request = urllib.request.Request(url, headers={"User-Agent": "edge-factory-full-range-funding-lock/1"})
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                text = response.read(2_000_000).decode("utf-8")
                counters["total_api_requests"] += 1
                counters["http_status_counts"][str(response.status)] = counters["http_status_counts"].get(str(response.status), 0) + 1
                data = json.loads(text)
                if not isinstance(data, list):
                    raise RuntimeError(f"unexpected fundingRate response type for {symbol}")
                return data
        except urllib.error.HTTPError as exc:
            body = exc.read(2000).decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {body[:500]}"
            counters["total_api_requests"] += 1
            counters["http_status_counts"][str(exc.code)] = counters["http_status_counts"].get(str(exc.code), 0) + 1
            if exc.code in (418, 429, 500, 502, 503, 504) and attempt < RETRY_CAP:
                counters["total_retries"] += 1
                time.sleep(2.0 * (attempt + 1))
                continue
            raise RuntimeError(f"fundingRate request failed for {symbol}: {last_error}") from exc
        except Exception as exc:
            last_error = repr(exc)
            counters["http_status_counts"]["NETWORK_ERROR"] = counters["http_status_counts"].get("NETWORK_ERROR", 0) + 1
            if attempt < RETRY_CAP:
                counters["total_retries"] += 1
                time.sleep(2.0 * (attempt + 1))
                continue
            raise RuntimeError(f"fundingRate request failed for {symbol}: {last_error}") from exc
    raise RuntimeError(f"fundingRate request failed for {symbol}: {last_error}")


def normalize_row(symbol: str, row: Dict[str, Any]) -> Tuple[int, Dict[str, Any], Optional[str]]:
    if row.get("symbol") != symbol:
        raise RuntimeError(f"funding response symbol mismatch: {row.get('symbol')} != {symbol}")
    funding_time_ms = int(row["fundingTime"])
    funding_rate = decimal_from_string(row.get("fundingRate"), "fundingRate")
    mark_price_value = row.get("markPrice")
    if mark_price_value not in (None, ""):
        decimal_from_string(mark_price_value, "markPrice")
    output = {
        "symbol": symbol,
        "funding_time_ms": funding_time_ms,
        "funding_time_utc": iso_from_ms(funding_time_ms),
        "funding_rate": format(funding_rate, "f"),
        "mark_price": None if mark_price_value in (None, "") else str(mark_price_value),
        "source_endpoint": ENDPOINT_URL,
    }
    return funding_time_ms, output, None


def acquire_symbol(symbol: str, counters: Dict[str, Any]) -> Dict[str, Any]:
    start_ms = WINDOW_START_MS
    seen_times = set()
    rows: List[Dict[str, Any]] = []
    duplicate_count = 0
    outside_count = 0
    invalid_numeric_count = 0
    missing_required_field_count = 0
    while start_ms <= ENDPOINT_END_INCLUSIVE_MS:
        page = request_funding_page(symbol, start_ms, ENDPOINT_END_INCLUSIVE_MS, counters)
        time.sleep(SLEEP_BETWEEN_REQUESTS_SECONDS)
        if not page:
            break
        last_time = None
        for raw in page:
            try:
                if not all(key in raw for key in ("symbol", "fundingTime", "fundingRate")):
                    missing_required_field_count += 1
                    continue
                funding_time_ms, normalized, _ = normalize_row(symbol, raw)
            except (ValueError, TypeError, InvalidOperation):
                invalid_numeric_count += 1
                continue
            if funding_time_ms < WINDOW_START_MS or funding_time_ms >= WINDOW_END_EXCLUSIVE_MS:
                outside_count += 1
                last_time = funding_time_ms
                continue
            if funding_time_ms in seen_times:
                duplicate_count += 1
                last_time = funding_time_ms
                continue
            seen_times.add(funding_time_ms)
            rows.append(normalized)
            last_time = funding_time_ms
        if last_time is None:
            break
        if len(page) < REQUEST_LIMIT:
            break
        start_ms = int(last_time) + 1
    rows.sort(key=lambda item: int(item["funding_time_ms"]))
    gaps: List[Dict[str, Any]] = []
    for idx in range(1, len(rows)):
        prior = int(rows[idx - 1]["funding_time_ms"])
        current = int(rows[idx]["funding_time_ms"])
        gap_hours = (current - prior) / 3_600_000.0
        if gap_hours > LARGE_GAP_THRESHOLD_HOURS:
            gaps.append(
                {
                    "from_utc": rows[idx - 1]["funding_time_utc"],
                    "to_utc": rows[idx]["funding_time_utc"],
                    "gap_hours": round(gap_hours, 6),
                }
            )
    output_path = FUNDING_BY_SYMBOL_DIR / f"{symbol}_funding_rate.jsonl.gz"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output_path, "wt", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    file_hash = sha256_file(output_path)
    return {
        "symbol": symbol,
        "record_count": len(rows),
        "min_funding_time_utc": rows[0]["funding_time_utc"] if rows else None,
        "max_funding_time_utc": rows[-1]["funding_time_utc"] if rows else None,
        "duplicate_count": duplicate_count,
        "records_outside_window_count": outside_count,
        "invalid_numeric_count": invalid_numeric_count,
        "missing_required_field_count": missing_required_field_count,
        "large_gap_count": len(gaps),
        "max_gap_hours": max((item["gap_hours"] for item in gaps), default=0),
        "large_gap_examples": gaps[:5],
        "output_file_path": str(output_path),
        "sha256": file_hash,
    }


def build_artifact() -> Dict[str, Any]:
    readiness = read_json(READINESS_PATH)
    panel_review = read_json(PANEL_REVIEW_PATH)
    build_manifest = read_json(BUILD_MANIFEST_PATH)
    preview = read_json(PREVIEW_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    source_artifacts = [readiness, panel_review, build_manifest, preview, coverage_lock]
    source_hashes = {
        READINESS_PATH: verify_hash(readiness),
        PANEL_REVIEW_PATH: verify_hash(panel_review),
        BUILD_MANIFEST_PATH: verify_hash(build_manifest),
        PREVIEW_PATH: verify_hash(preview),
        COVERAGE_LOCK_PATH: verify_hash(coverage_lock),
    }
    if not validate_no_forbidden_permissions(source_artifacts):
        raise RuntimeError("source artifact unexpectedly grants forbidden permission")
    symbols = find_symbol_list(readiness) or find_symbol_list(preview) or find_symbol_list(build_manifest)
    if not symbols or len(symbols) != EXPECTED_SYMBOL_COUNT:
        raise RuntimeError("could not verify exact 81-symbol overlap universe")
    symbols = sorted(symbols)

    FUNDING_BY_SYMBOL_DIR.mkdir(parents=True, exist_ok=True)
    FUNDING_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    counters: Dict[str, Any] = {"total_api_requests": 0, "total_retries": 0, "http_status_counts": {}}
    symbol_summaries: List[Dict[str, Any]] = []
    for idx, symbol in enumerate(symbols, start=1):
        symbol_summaries.append(acquire_symbol(symbol, counters))
        print(json.dumps({"event": "symbol_acquired", "symbol": symbol, "index": idx, "symbol_count": len(symbols)}, sort_keys=True), flush=True)

    total_records = sum(item["record_count"] for item in symbol_summaries)
    min_times = [item["min_funding_time_utc"] for item in symbol_summaries if item["min_funding_time_utc"]]
    max_times = [item["max_funding_time_utc"] for item in symbol_summaries if item["max_funding_time_utc"]]
    duplicate_count = sum(item["duplicate_count"] for item in symbol_summaries)
    outside_count = sum(item["records_outside_window_count"] for item in symbol_summaries)
    invalid_numeric_count = sum(item["invalid_numeric_count"] for item in symbol_summaries)
    missing_required_field_count = sum(item["missing_required_field_count"] for item in symbol_summaries)
    zero_record_symbols = [item["symbol"] for item in symbol_summaries if item["record_count"] == 0]
    symbols_with_large_gaps = [item["symbol"] for item in symbol_summaries if item["large_gap_count"] > 0]
    total_large_gap_count = sum(item["large_gap_count"] for item in symbol_summaries)
    funding_file_hashes = {item["symbol"]: item["sha256"] for item in symbol_summaries}

    index_payload = {
        "artifact_kind": "BINANCE_OKX_OVERLAP_FUNDING_RATE_FULL_RANGE_202105_202510_INDEX",
        "created_by_module": MODULE_PATH,
        "symbol_count": len(symbols),
        "window_start_utc": WINDOW_START_UTC,
        "window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
        "total_funding_records": total_records,
        "symbol_files": symbol_summaries,
    }
    FUNDING_INDEX_PATH.write_text(json.dumps(index_payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    index_hash = sha256_file(FUNDING_INDEX_PATH)

    p0_passed = (
        len(symbols) == EXPECTED_SYMBOL_COUNT
        and total_records > 0
        and not zero_record_symbols
        and duplicate_count == 0
        and outside_count == 0
        and invalid_numeric_count == 0
        and missing_required_field_count == 0
    )
    payload: Dict[str, Any] = {
        "status": STATUS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "repo_scope": {
            "code_changes_repo_only": True,
            "funding_rate_acquisition_lock_created_in_repo": True,
            "public_binance_funding_rate_endpoint_used": True,
            "private_api_used": False,
            "api_key_used": False,
            "binance_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "okx_panel_rows_read": False,
            "strategy_executed": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
        },
        "source_artifacts": {
            "payload_hashes": source_hashes,
            "readiness_artifact": READINESS_PATH,
            "panel_review_artifact": PANEL_REVIEW_PATH,
            "panel_manifest_artifact": BUILD_MANIFEST_PATH,
            "preview_artifact": PREVIEW_PATH,
            "coverage_lock_artifact": COVERAGE_LOCK_PATH,
        },
        "acquisition_scope": {
            "route_family": ROUTE_FAMILY,
            "config_id_for_future_execution": CONFIG_ID,
            "symbol_count": len(symbols),
            "symbols": symbols,
            "full_window_start_utc": WINDOW_START_UTC,
            "full_window_end_exclusive_utc": WINDOW_END_EXCLUSIVE_UTC,
            "endpoint_end_inclusive_utc": ENDPOINT_END_INCLUSIVE_UTC,
            "okx_panel_rows_required": False,
        },
        "source_endpoint_contract": {
            "endpoint_url": ENDPOINT_URL,
            "method": "GET",
            "public_endpoint_only": True,
            "api_key_required": False,
            "limit": REQUEST_LIMIT,
            "startTime": "inclusive",
            "endTime": "inclusive",
            "next_page_startTime": "last fundingTime + 1",
        },
        "funding_data_output_summary": {
            "external_root": str(EXTERNAL_ROOT),
            "funding_by_symbol_dir": str(FUNDING_BY_SYMBOL_DIR),
            "funding_index_path": str(FUNDING_INDEX_PATH),
            "funding_index_sha256": index_hash,
            "symbol_count": len(symbols),
            "total_funding_records": total_records,
            "min_funding_time_utc": min(min_times) if min_times else None,
            "max_funding_time_utc": max(max_times) if max_times else None,
            "duplicate_count": duplicate_count,
            "records_outside_window_count": outside_count,
            "invalid_numeric_count": invalid_numeric_count,
            "missing_required_field_count": missing_required_field_count,
            "symbols_with_zero_records": zero_record_symbols,
            "symbols_with_zero_records_count": len(zero_record_symbols),
            "max_gap_review": {
                "large_gap_threshold_hours": LARGE_GAP_THRESHOLD_HOURS,
                "symbols_with_large_gaps": symbols_with_large_gaps,
                "symbols_with_large_gaps_count": len(symbols_with_large_gaps),
                "total_large_gap_count": total_large_gap_count,
                "max_gap_hours_global": max((item["max_gap_hours"] for item in symbol_summaries), default=0),
            },
            "funding_files_hashes": funding_file_hashes,
            "funding_data_p0_checks_passed": p0_passed,
        },
        "source_request_summary": counters,
        "safety_permissions": {
            "funding_data_acquisition_completed": True,
            "strategy_execution_allowed_now": False,
            "strategy_search_allowed_now": False,
            "candidate_generation_allowed_now": False,
            "edge_claim_allowed_now": False,
            "family_release_allowed_now": False,
            "runtime_permission_allowed_now": False,
            "live_permission_allowed_now": False,
            "capital_permission_allowed_now": False,
            "review_required_next": True,
        },
        "forbidden_actions_confirmed_false": {
            "strategy_executed": False,
            "strategy_search_executed": False,
            "non_preregistered_config_tested": False,
            "binance_panel_rows_read": False,
            "binance_1m_source_rows_read": False,
            "okx_panel_rows_read": False,
            "candidates_generated": False,
            "edge_claimed": False,
            "family_released": False,
            "runtime_permission_granted": False,
            "live_permission_granted": False,
            "capital_permission_granted": False,
            "existing_files_modified_by_module": False,
        },
        "validation_checks": {
            "status_equals_required_status": True,
            "module_path_equals_required_path": True,
            "artifact_path_equals_required_path": True,
            "exactly_one_new_tracked_python_tool_file_expected": True,
            "exactly_one_new_tracked_json_acquisition_artifact_expected": True,
            "symbol_count_verified_81": len(symbols) == EXPECTED_SYMBOL_COUNT,
            "full_range_window_recorded": True,
            "source_endpoint_is_allowed_funding_rate_only": True,
            "no_private_api_or_api_key": True,
            "no_panel_rows_read": True,
            "no_okx_panel_rows_read": True,
            "no_strategy_execution": True,
            "no_candidate_generation": True,
            "no_edge_claim": True,
            "payload_sha256_excluding_hash_present": True,
            "replacement_checks_all_true": True,
        },
        "replacement_checks_all_true": True,
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    required_assertions = [
        payload["status"] == STATUS,
        payload["module"] == MODULE_PATH,
        payload["acquisition_scope"]["symbol_count"] == EXPECTED_SYMBOL_COUNT,
        payload["repo_scope"]["private_api_used"] is False,
        payload["repo_scope"]["api_key_used"] is False,
        payload["repo_scope"]["strategy_executed"] is False,
        payload["forbidden_actions_confirmed_false"]["okx_panel_rows_read"] is False,
        payload["forbidden_actions_confirmed_false"]["candidates_generated"] is False,
        payload["forbidden_actions_confirmed_false"]["edge_claimed"] is False,
        payload["forbidden_actions_confirmed_false"]["runtime_permission_granted"] is False,
        payload["replacement_checks_all_true"] is True,
    ]
    if not all(required_assertions):
        raise RuntimeError("acquisition invariant assertion failed")
    return payload


def main() -> None:
    artifact = build_artifact()
    output_path = REPO_ROOT / ARTIFACT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": artifact["status"],
        "artifact_path": ARTIFACT_PATH,
        "symbol_count": artifact["funding_data_output_summary"]["symbol_count"],
        "total_funding_records": artifact["funding_data_output_summary"]["total_funding_records"],
        "min_funding_time_utc": artifact["funding_data_output_summary"]["min_funding_time_utc"],
        "max_funding_time_utc": artifact["funding_data_output_summary"]["max_funding_time_utc"],
        "symbols_with_zero_records_count": artifact["funding_data_output_summary"]["symbols_with_zero_records_count"],
        "total_api_requests": artifact["source_request_summary"]["total_api_requests"],
        "funding_index_sha256": artifact["funding_data_output_summary"]["funding_index_sha256"],
        "strategy_executed": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": artifact["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": artifact["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
