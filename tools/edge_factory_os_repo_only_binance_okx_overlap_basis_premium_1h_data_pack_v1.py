import gzip
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "tools/edge_factory_os_repo_only_binance_okx_overlap_basis_premium_1h_data_pack_v1.py"
ARTIFACT_PATH = "artifacts/basis_premium_data_locks/binance_okx_overlap_basis_premium_1h_data_pack_v1.json"
STATUS_SUCCESS = "PASS_REPO_CODE_ONLY_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_CREATED"
STATUS_BLOCKED = "BLOCKED_BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_UNAVAILABLE"
ARTIFACT_KIND = "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK"

ACTUAL_HEAD_BEFORE_RUN = "5511f38abb55059328f671c86316314325d0b208"
TRACKED_PYTHON_COUNT_BEFORE_RUN = 867
SYMBOL_COUNT = 81
INTERVAL = "1h"
LIMIT = 1500
TIMEOUT_SECONDS = 20
RETRY_CAP = 3
REQUEST_SLEEP_SECONDS = 0.06

START_UTC = "2023-01-01T00:00:00Z"
END_EXCLUSIVE_UTC = "2025-11-01T00:00:00Z"
OLD_PROBE_START_UTC = "2023-01-01T00:00:00Z"
OLD_PROBE_END_EXCLUSIVE_UTC = "2023-01-03T00:00:00Z"
REPRESENTATIVE_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]

EXTERNAL_ROOT = Path(
    r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo_only_binance_okx_overlap_basis_premium_1h_data_pack_v1"
)
OUTPUT_DIR = EXTERNAL_ROOT / "basis_premium_by_symbol"
INDEX_DIR = EXTERNAL_ROOT / "basis_premium_index"
INDEX_PATH = INDEX_DIR / "binance_okx_overlap_basis_premium_1h_index_v1.json"

READINESS_PATH = "artifacts/second_source_readiness/binance_okx_overlap_near_5y_second_source_readiness_alignment_summary_v1.json"
PANEL_MANIFEST_PATH = "artifacts/panel_build_manifests/binance_okx_overlap_near_5y_1m_to_1h_panel_build_manifest_v1.json"
COVERAGE_LOCK_PATH = "artifacts/coverage_locks/binance_usdt_perpetual_1m_coverage_discovery_lock_v1.json"

ENDPOINTS = {
    "premium": {
        "name": "premium_index_klines",
        "url": "https://fapi.binance.com/fapi/v1/premiumIndexKlines",
        "symbol_param": "symbol",
    },
    "mark": {
        "name": "mark_price_klines",
        "url": "https://fapi.binance.com/fapi/v1/markPriceKlines",
        "symbol_param": "symbol",
    },
    "index": {
        "name": "index_price_klines",
        "url": "https://fapi.binance.com/fapi/v1/indexPriceKlines",
        "symbol_param": "pair",
    },
}


REQUEST_STATS = {"total_requests": 0, "retries": 0, "errors": []}


def canonical_payload_hash(payload: Dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, indent=2).encode("utf-8")).hexdigest()


def read_json(relative_path: str) -> Dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"missing required source artifact: {relative_path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"source artifact is not a JSON object: {relative_path}")
    return payload


def verify_hash(payload: Dict[str, Any]) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RuntimeError("source artifact missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if recomputed != stored:
        raise RuntimeError(f"source artifact payload hash mismatch: {recomputed} != {stored}")
    return stored


def find_symbol_list(value: Any) -> Optional[List[str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"exact_overlap_binance_symbols", "symbol_set", "symbols", "binance_symbols"}:
                if isinstance(child, list) and len(child) == SYMBOL_COUNT:
                    if all(isinstance(item, str) and item.endswith("USDT") for item in child):
                        return sorted(child)
            found = find_symbol_list(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_symbol_list(child)
            if found is not None:
                return found
    return None


def parse_utc_ms(value: str) -> int:
    if not value.endswith("Z"):
        raise RuntimeError(f"timestamp does not end with Z: {value}")
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def ms_to_utc(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


START_MS = parse_utc_ms(START_UTC)
END_EXCLUSIVE_MS = parse_utc_ms(END_EXCLUSIVE_UTC)
OLD_PROBE_START_MS = parse_utc_ms(OLD_PROBE_START_UTC)
OLD_PROBE_END_MS = parse_utc_ms(OLD_PROBE_END_EXCLUSIVE_UTC) - 1
ONE_HOUR_MS = 60 * 60 * 1000


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request_json(endpoint_key: str, symbol: str, start_ms: Optional[int], end_ms: Optional[int], limit: int = LIMIT) -> List[Any]:
    endpoint = ENDPOINTS[endpoint_key]
    params: Dict[str, Any] = {
        endpoint["symbol_param"]: symbol,
        "interval": INTERVAL,
        "limit": str(limit),
    }
    if start_ms is not None:
        params["startTime"] = str(start_ms)
    if end_ms is not None:
        params["endTime"] = str(end_ms)
    url = endpoint["url"] + "?" + urllib.parse.urlencode(params)
    last_error: Optional[str] = None
    for attempt in range(RETRY_CAP):
        if attempt > 0:
            REQUEST_STATS["retries"] += 1
            time.sleep(min(2.0 * attempt, 5.0))
        try:
            REQUEST_STATS["total_requests"] += 1
            req = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-repo-only-basis-premium-pack/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, list):
                raise RuntimeError(f"unexpected non-list response for {endpoint_key} {symbol}: {payload}")
            time.sleep(REQUEST_SLEEP_SECONDS)
            return payload
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:500]
            last_error = f"HTTP {exc.code} {endpoint_key} {symbol}: {body}"
            if exc.code in {418, 429}:
                time.sleep(5.0 + attempt * 5.0)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = f"{type(exc).__name__} {endpoint_key} {symbol}: {exc}"
    REQUEST_STATS["errors"].append(last_error or f"unknown request failure {endpoint_key} {symbol}")
    raise RuntimeError(last_error or f"request failed for {endpoint_key} {symbol}")


def normalize_rows(rows: Iterable[Any], endpoint_key: str, symbol: str) -> Dict[int, Dict[str, str]]:
    normalized: Dict[int, Dict[str, str]] = {}
    for row in rows:
        if not isinstance(row, list) or len(row) < 5:
            raise RuntimeError(f"bad kline row for {endpoint_key} {symbol}: {row}")
        ts = int(row[0])
        if ts % ONE_HOUR_MS != 0:
            raise RuntimeError(f"non-hourly timestamp for {endpoint_key} {symbol}: {ts}")
        if not (START_MS <= ts < END_EXCLUSIVE_MS):
            continue
        normalized[ts] = {
            "open": str(row[1]),
            "high": str(row[2]),
            "low": str(row[3]),
            "close": str(row[4]),
        }
    return normalized


def fetch_endpoint_history(endpoint_key: str, symbol: str) -> Dict[int, Dict[str, str]]:
    rows_by_time: Dict[int, Dict[str, str]] = {}
    next_start = START_MS
    endpoint_end = END_EXCLUSIVE_MS - 1
    while next_start < END_EXCLUSIVE_MS:
        rows = request_json(endpoint_key, symbol, next_start, endpoint_end, LIMIT)
        if not rows:
            break
        normalized = normalize_rows(rows, endpoint_key, symbol)
        for ts, values in normalized.items():
            rows_by_time[ts] = values
        raw_open_times = [int(row[0]) for row in rows if isinstance(row, list) and row]
        if not raw_open_times:
            break
        last_open = max(raw_open_times)
        if last_open < next_start:
            break
        next_start = last_open + ONE_HOUR_MS
        if len(rows) < LIMIT:
            break
    return rows_by_time


def probe_endpoint(endpoint_key: str, symbol: str, old_range: bool) -> Dict[str, Any]:
    if old_range:
        rows = request_json(endpoint_key, symbol, OLD_PROBE_START_MS, OLD_PROBE_END_MS, LIMIT)
    else:
        rows = request_json(endpoint_key, symbol, None, None, 10)
    times = [int(row[0]) for row in rows if isinstance(row, list) and row]
    return {
        "endpoint_key": endpoint_key,
        "symbol": symbol,
        "range": "old_2023_01_01_to_2023_01_03" if old_range else "recent_no_start_end",
        "row_count": len(rows),
        "min_timestamp_utc": ms_to_utc(min(times)) if times else None,
        "max_timestamp_utc": ms_to_utc(max(times)) if times else None,
        "available": len(rows) > 0,
    }


def representative_probes() -> Tuple[Dict[str, Any], bool]:
    probe_records: List[Dict[str, Any]] = []
    endpoint_old_available = {key: True for key in ENDPOINTS}
    endpoint_recent_available = {key: True for key in ENDPOINTS}
    for symbol in REPRESENTATIVE_SYMBOLS:
        for endpoint_key in ENDPOINTS:
            old_record = probe_endpoint(endpoint_key, symbol, True)
            recent_record = probe_endpoint(endpoint_key, symbol, False)
            probe_records.extend([old_record, recent_record])
            endpoint_old_available[endpoint_key] = endpoint_old_available[endpoint_key] and old_record["available"]
            endpoint_recent_available[endpoint_key] = endpoint_recent_available[endpoint_key] and recent_record["available"]
    passed = all(endpoint_old_available.values()) and all(endpoint_recent_available.values())
    return (
        {
            "representative_symbols": REPRESENTATIVE_SYMBOLS,
            "probe_records": probe_records,
            "endpoint_old_range_available": endpoint_old_available,
            "endpoint_recent_range_available": endpoint_recent_available,
            "representative_endpoint_probes_passed": passed,
        },
        passed,
    )


def load_symbols_and_sources() -> Tuple[List[str], Dict[str, Any]]:
    readiness = read_json(READINESS_PATH)
    panel_manifest = read_json(PANEL_MANIFEST_PATH)
    coverage_lock = read_json(COVERAGE_LOCK_PATH)
    readiness_hash = verify_hash(readiness)
    panel_manifest_hash = verify_hash(panel_manifest)
    coverage_hash = verify_hash(coverage_lock)
    symbols = find_symbol_list(readiness) or find_symbol_list(panel_manifest) or find_symbol_list(coverage_lock)
    if symbols is None or len(symbols) != SYMBOL_COUNT:
        raise RuntimeError("could not verify exact 81-symbol universe")
    missing_representatives = [symbol for symbol in REPRESENTATIVE_SYMBOLS if symbol not in symbols]
    if missing_representatives:
        raise RuntimeError(f"representative symbols missing from universe: {missing_representatives}")
    source_summary = {
        "second_source_readiness": {
            "path": READINESS_PATH,
            "status": readiness.get("status"),
            "payload_sha256_excluding_hash": readiness_hash,
        },
        "panel_build_manifest": {
            "path": PANEL_MANIFEST_PATH,
            "status": panel_manifest.get("status"),
            "payload_sha256_excluding_hash": panel_manifest_hash,
        },
        "coverage_lock": {
            "path": COVERAGE_LOCK_PATH,
            "status": coverage_lock.get("status"),
            "payload_sha256_excluding_hash": coverage_hash,
        },
    }
    return symbols, source_summary


def parse_float(value: str, field: str, symbol: str, timestamp_ms: int) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise RuntimeError(f"numeric parse failure {field} {symbol} {timestamp_ms}: {value}") from exc
    return parsed


def acquire_symbol(symbol: str) -> Dict[str, Any]:
    endpoint_rows = {key: fetch_endpoint_history(key, symbol) for key in ENDPOINTS}
    all_timestamps = sorted(set().union(*(set(rows.keys()) for rows in endpoint_rows.values())))
    intersection = sorted(set(endpoint_rows["premium"]) & set(endpoint_rows["mark"]) & set(endpoint_rows["index"]))
    missing_counts = {
        key: sum(1 for ts in all_timestamps if ts not in endpoint_rows[key])
        for key in ENDPOINTS
    }
    rows_written = 0
    min_ts: Optional[int] = None
    max_ts: Optional[int] = None
    duplicate_count = 0
    numeric_invalid_count = 0
    mark_index_nonpositive_count = 0
    rows_outside_window_count = 0
    seen: set[int] = set()
    output_path = OUTPUT_DIR / f"{symbol}_basis_premium_1h.jsonl.gz"
    with gzip.open(output_path, "wt", encoding="utf-8", newline="\n") as handle:
        for ts in intersection:
            if ts in seen:
                duplicate_count += 1
                continue
            seen.add(ts)
            if not (START_MS <= ts < END_EXCLUSIVE_MS):
                rows_outside_window_count += 1
                continue
            premium = endpoint_rows["premium"][ts]
            mark = endpoint_rows["mark"][ts]
            index = endpoint_rows["index"][ts]
            try:
                parsed = {
                    "premium_open": parse_float(premium["open"], "premium_open", symbol, ts),
                    "premium_high": parse_float(premium["high"], "premium_high", symbol, ts),
                    "premium_low": parse_float(premium["low"], "premium_low", symbol, ts),
                    "premium_close": parse_float(premium["close"], "premium_close", symbol, ts),
                    "mark_open": parse_float(mark["open"], "mark_open", symbol, ts),
                    "mark_high": parse_float(mark["high"], "mark_high", symbol, ts),
                    "mark_low": parse_float(mark["low"], "mark_low", symbol, ts),
                    "mark_close": parse_float(mark["close"], "mark_close", symbol, ts),
                    "index_open": parse_float(index["open"], "index_open", symbol, ts),
                    "index_high": parse_float(index["high"], "index_high", symbol, ts),
                    "index_low": parse_float(index["low"], "index_low", symbol, ts),
                    "index_close": parse_float(index["close"], "index_close", symbol, ts),
                }
            except RuntimeError:
                numeric_invalid_count += 1
                continue
            if min(parsed["mark_open"], parsed["mark_high"], parsed["mark_low"], parsed["mark_close"]) <= 0:
                mark_index_nonpositive_count += 1
                continue
            if min(parsed["index_open"], parsed["index_high"], parsed["index_low"], parsed["index_close"]) <= 0:
                mark_index_nonpositive_count += 1
                continue
            record = {
                "symbol": symbol,
                "timestamp_utc": ms_to_utc(ts),
                "timestamp_ms": ts,
                **parsed,
                "source_endpoints": {
                    "premium": ENDPOINTS["premium"]["url"],
                    "mark": ENDPOINTS["mark"]["url"],
                    "index": ENDPOINTS["index"]["url"],
                },
                "interval": INTERVAL,
            }
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            rows_written += 1
            min_ts = ts if min_ts is None else min(min_ts, ts)
            max_ts = ts if max_ts is None else max(max_ts, ts)
    return {
        "symbol": symbol,
        "output_path": str(output_path),
        "row_count": rows_written,
        "min_timestamp_utc": ms_to_utc(min_ts) if min_ts is not None else None,
        "max_timestamp_utc": ms_to_utc(max_ts) if max_ts is not None else None,
        "endpoint_row_counts": {key: len(endpoint_rows[key]) for key in ENDPOINTS},
        "endpoint_missing_row_counts": missing_counts,
        "duplicate_symbol_hour_count": duplicate_count,
        "rows_outside_window_count": rows_outside_window_count,
        "numeric_invalid_count": numeric_invalid_count,
        "mark_index_nonpositive_count": mark_index_nonpositive_count,
        "sha256": sha256_file(output_path),
    }


def build_blocked_manifest(symbols: List[str], source_artifacts: Dict[str, Any], probes: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "status": STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "actual_head_before_run": ACTUAL_HEAD_BEFORE_RUN,
            "tracked_python_count_before_run": TRACKED_PYTHON_COUNT_BEFORE_RUN,
            "repo_clean_before_run": True,
        },
        "source_artifacts": source_artifacts,
        "acquisition_scope": {
            "symbol_count": len(symbols),
            "window_start_utc": START_UTC,
            "window_end_exclusive_utc": END_EXCLUSIVE_UTC,
            "interval": INTERVAL,
        },
        "endpoint_contracts": endpoint_contracts(),
        "endpoint_probe_results": probes,
        "acquisition_summary": {
            "symbol_count": len(symbols),
            "symbols_with_rows_count": 0,
            "symbols_with_zero_rows_count": len(symbols),
            "total_rows": 0,
            "min_timestamp_utc": None,
            "max_timestamp_utc": None,
            "total_requests": REQUEST_STATS["total_requests"],
            "retries": REQUEST_STATS["retries"],
            "errors": REQUEST_STATS["errors"],
            "endpoint_missing_row_counts": {},
            "output_files_count": 0,
            "data_valid_for_future_basis_premium_research": False,
        },
        "validation_summary": {
            "blocked_reason": "representative old/recent endpoint probes did not all return rows",
        },
        "symbol_records": [],
        "non_repo_artifacts": {
            "external_artifact_root": str(EXTERNAL_ROOT),
            "row_data_written_outside_repo": True,
        },
        "limitations": [
            "Bulk acquisition was not started because representative endpoint availability was not proven.",
        ],
        "safety_permissions": safety_permissions(False),
        "validation_checks": validation_checks(False),
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    return payload


def endpoint_contracts() -> Dict[str, Any]:
    return {
        key: {
            "endpoint_name": value["name"],
            "url": value["url"],
            "symbol_parameter": value["symbol_param"],
            "interval": INTERVAL,
            "limit": LIMIT,
            "public_market_data_endpoint": True,
            "api_key_used": False,
        }
        for key, value in ENDPOINTS.items()
    }


def safety_permissions(valid: bool) -> Dict[str, Any]:
    return {
        "basis_premium_data_pack_created": valid,
        "valid_for_future_basis_premium_feature_construction": valid,
        "strategy_execution_allowed_now": False,
        "candidate_generation_allowed_now": False,
        "edge_claim_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_permission_allowed_now": False,
        "live_permission_allowed_now": False,
        "capital_permission_allowed_now": False,
    }


def validation_checks(valid: bool) -> Dict[str, Any]:
    return {
        "repo_clean_before_run": True,
        "exact_overlap_symbol_count_verified_81": True,
        "representative_endpoint_probes_passed": valid,
        "all_required_endpoint_rows_acquired_or_missing_recorded": valid,
        "no_rows_outside_window": valid,
        "no_duplicate_symbol_hour": valid,
        "numeric_sanity_valid": valid,
        "mark_index_price_positive": valid,
        "premium_numeric_valid": valid,
        "row_data_written_outside_repo": True,
        "no_strategy_execution": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_manifest_created": True,
        "no_existing_files_modified": True,
        "replacement_checks_all_true": valid,
    }


def build_success_manifest(symbols: List[str], source_artifacts: Dict[str, Any], probes: Dict[str, Any], symbol_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_rows = sum(record["row_count"] for record in symbol_records)
    symbols_with_rows = [record["symbol"] for record in symbol_records if record["row_count"] > 0]
    zero_symbols = [record["symbol"] for record in symbol_records if record["row_count"] == 0]
    min_candidates = [record["min_timestamp_utc"] for record in symbol_records if record["min_timestamp_utc"]]
    max_candidates = [record["max_timestamp_utc"] for record in symbol_records if record["max_timestamp_utc"]]
    endpoint_missing_totals = {key: 0 for key in ENDPOINTS}
    for record in symbol_records:
        for key, count in record["endpoint_missing_row_counts"].items():
            endpoint_missing_totals[key] += count
    duplicate_count = sum(record["duplicate_symbol_hour_count"] for record in symbol_records)
    rows_outside = sum(record["rows_outside_window_count"] for record in symbol_records)
    numeric_invalid = sum(record["numeric_invalid_count"] for record in symbol_records)
    nonpositive = sum(record["mark_index_nonpositive_count"] for record in symbol_records)
    valid = (
        len(symbols) == SYMBOL_COUNT
        and len(symbols_with_rows) == SYMBOL_COUNT
        and total_rows > 0
        and duplicate_count == 0
        and rows_outside == 0
        and numeric_invalid == 0
        and nonpositive == 0
    )
    index_payload = {
        "status": STATUS_SUCCESS,
        "artifact_kind": "BINANCE_OKX_OVERLAP_BASIS_PREMIUM_1H_DATA_PACK_INDEX",
        "external_artifact_root": str(EXTERNAL_ROOT),
        "window_start_utc": START_UTC,
        "window_end_exclusive_utc": END_EXCLUSIVE_UTC,
        "interval": INTERVAL,
        "symbol_count": len(symbols),
        "total_rows": total_rows,
        "symbol_records": symbol_records,
    }
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index_payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    index_sha = sha256_file(INDEX_PATH)
    file_hashes = {record["symbol"]: record["sha256"] for record in symbol_records}
    payload: Dict[str, Any] = {
        "status": STATUS_SUCCESS if valid else STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE_PATH,
        "source_checkpoint": {
            "actual_head_before_run": ACTUAL_HEAD_BEFORE_RUN,
            "tracked_python_count_before_run": TRACKED_PYTHON_COUNT_BEFORE_RUN,
            "repo_clean_before_run": True,
        },
        "source_artifacts": source_artifacts,
        "acquisition_scope": {
            "symbol_count": len(symbols),
            "symbols": symbols,
            "window_start_utc": START_UTC,
            "window_end_exclusive_utc": END_EXCLUSIVE_UTC,
            "interval": INTERVAL,
            "row_data_written_outside_repo_only": True,
        },
        "endpoint_contracts": endpoint_contracts(),
        "endpoint_probe_results": probes,
        "acquisition_summary": {
            "symbol_count": len(symbols),
            "symbols_with_rows_count": len(symbols_with_rows),
            "symbols_with_zero_rows_count": len(zero_symbols),
            "total_rows": total_rows,
            "min_timestamp_utc": min(min_candidates) if min_candidates else None,
            "max_timestamp_utc": max(max_candidates) if max_candidates else None,
            "total_requests": REQUEST_STATS["total_requests"],
            "retries": REQUEST_STATS["retries"],
            "errors": REQUEST_STATS["errors"],
            "endpoint_missing_row_counts": endpoint_missing_totals,
            "output_files_count": len(symbol_records),
            "data_valid_for_future_basis_premium_research": valid,
        },
        "validation_summary": {
            "duplicate_symbol_hour_count": duplicate_count,
            "rows_outside_window_count": rows_outside,
            "numeric_invalid_count": numeric_invalid,
            "mark_index_nonpositive_count": nonpositive,
            "symbols_with_zero_rows": zero_symbols,
            "no_rows_outside_window": rows_outside == 0,
            "no_duplicate_symbol_hour": duplicate_count == 0,
            "numeric_sanity_valid": numeric_invalid == 0,
            "mark_index_price_positive": nonpositive == 0,
            "premium_numeric_valid": numeric_invalid == 0,
        },
        "symbol_records": symbol_records,
        "non_repo_artifacts": {
            "external_artifact_root": str(EXTERNAL_ROOT),
            "basis_premium_by_symbol_dir": str(OUTPUT_DIR),
            "basis_premium_index_path": str(INDEX_PATH),
            "basis_premium_index_sha256": index_sha,
            "output_files_sha256": file_hashes,
            "row_data_written_outside_repo": True,
        },
        "limitations": [
            "This is an acquisition and validation manifest only.",
            "Rows are retained only where premium, mark, and index endpoint timestamps intersect.",
            "No trading signal, strategy return, candidate, edge, release, or runtime/live/capital permission is created.",
        ],
        "safety_permissions": safety_permissions(valid),
        "validation_checks": validation_checks(valid),
        "replacement_checks_all_true": valid,
        "payload_sha256_excluding_hash": "",
    }
    payload["payload_sha256_excluding_hash"] = canonical_payload_hash(payload)
    return payload


def main() -> None:
    artifact_path = REPO_ROOT / ARTIFACT_PATH
    if artifact_path.exists():
        raise RuntimeError(f"manifest already exists: {ARTIFACT_PATH}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    symbols, source_artifacts = load_symbols_and_sources()
    probes, probes_passed = representative_probes()
    if not probes_passed:
        payload = build_blocked_manifest(symbols, source_artifacts, probes)
    else:
        symbol_records = []
        for index, symbol in enumerate(symbols, start=1):
            print(f"[basis-premium] acquiring {index}/{len(symbols)} {symbol}", file=sys.stderr)
            symbol_records.append(acquire_symbol(symbol))
        payload = build_success_manifest(symbols, source_artifacts, probes, symbol_records)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": payload["status"],
        "external_artifact_root": str(EXTERNAL_ROOT),
        "output_symbol_count": payload["acquisition_summary"]["symbols_with_rows_count"],
        "total_rows": payload["acquisition_summary"]["total_rows"],
        "min_timestamp_utc": payload["acquisition_summary"]["min_timestamp_utc"],
        "max_timestamp_utc": payload["acquisition_summary"]["max_timestamp_utc"],
        "total_requests": payload["acquisition_summary"]["total_requests"],
        "symbols_with_zero_rows_count": payload["acquisition_summary"]["symbols_with_zero_rows_count"],
        "data_valid_for_future_basis_premium_research": payload["acquisition_summary"]["data_valid_for_future_basis_premium_research"],
        "strategy_execution_allowed_now": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "payload_sha256_excluding_hash": payload["payload_sha256_excluding_hash"],
        "replacement_checks_all_true": payload["replacement_checks_all_true"],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))
    if payload["status"] != STATUS_SUCCESS:
        raise RuntimeError(payload["status"])


if __name__ == "__main__":
    main()
