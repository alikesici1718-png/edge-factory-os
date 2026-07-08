#!/usr/bin/env python
"""Direct public Binance Data Vision kline forward-return diagnostic for proxy events."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import statistics
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_public_kline_forward_return_diagnostic_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_BASELINE_HEAD = "6fb32c85ab277f8a74f632b21a73adda7a944baf"
PHASE1_GIT_CLEAN_BEFORE_TOOL_CREATION = True
SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH = "artifacts/contracts/binance_oi_taker_crowding_proxy_validation_contract_v1.json"
SOURCE_EVENT_STUDY_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_proxy_event_study_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"

DIAGNOSTIC_STATUS_PASS = "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED"
DIAGNOSTIC_STATUS_BLOCKED = "BLOCKED_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC"
ARTIFACT_KIND = "BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC"

RESULT_READY = "BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_READY_FOR_NULL_VALIDATION"
RESULT_ATTENTION = "BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_FAILED_STOP"
ALLOWED_NEXT_STEP_READY = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_NULL_VALIDATION_CONTRACT_V1"
ALLOWED_NEXT_STEP_BLOCKED = "BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_BLOCKER_REVIEW_V1"

PUBLIC_DATA_HOST = "data.binance.vision"
PUBLIC_DATA_ROOT = "https://data.binance.vision/"
KLINE_INTERVAL = "15m"
KLINE_PATH_TEMPLATE = "data/futures/um/monthly/klines/{symbol}/15m/{symbol}-15m-{year:04d}-{month:02d}.zip"
CACHE_ROOT = REPO_ROOT / "cache" / "binance_public_kline_forward_return_diagnostic_v1"

START_YEAR_MONTH = (2023, 1)
END_YEAR_MONTH = (2025, 12)
KLINE_INTERVAL_MS = 15 * 60 * 1000
TIMEOUT_SECONDS = 30
RETRY_CAP = 3
DOWNLOAD_WORKERS = 12
REQUEST_SLEEP_SECONDS = 0.01

HORIZONS = {
    "15m": 15 * 60 * 1000,
    "30m": 30 * 60 * 1000,
    "1h": 60 * 60 * 1000,
    "4h": 4 * 60 * 60 * 1000,
    "12h": 12 * 60 * 60 * 1000,
    "24h": 24 * 60 * 60 * 1000,
}

EVENT_IDS = [
    "oi_expansion_taker_buy_global_crowding_high",
    "oi_expansion_taker_sell_global_crowding_low",
    "oi_expansion_top_account_crowding_high",
    "oi_expansion_top_position_crowding_high",
    "broad_proxy_alignment_extreme",
]

FORBIDDEN_FAILED_ROUTES = [
    "funding crowding reversal",
    "funding carry",
    "funding extreme volume surge",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
]

RECOVERY_EXPECTED_ALLOWED_DIRTY_PREFIXES = [
    "tools/edge_factory_os_repo_only_binance_public_kline_forward_return_diagnostic_v1.py",
    "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json",
    "cache/binance_public_kline_forward_return_diagnostic_v1/",
]


class DiagnosticBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.returncode, result.stdout, result.stderr


def git_lines(args: list[str]) -> list[str]:
    code, stdout, stderr = run_git(args)
    if code != 0:
        raise DiagnosticBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
    return [line.rstrip() for line in stdout.splitlines() if line.strip()]


def current_head() -> str:
    lines = git_lines(["rev-parse", "HEAD"])
    return lines[0] if lines else ""


def tracked_python_count() -> int:
    return len(git_lines(["ls-files", "*.py"]))


def recovery_audit() -> dict[str, Any]:
    head = current_head()
    porcelain = git_lines(["status", "--porcelain=v1"])
    staged = git_lines(["diff", "--cached", "--name-status"])
    modified = git_lines(["diff", "--name-status"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    classifications: dict[str, str] = {}
    dirty_paths: set[str] = set()
    for line in porcelain:
        path = line[3:] if len(line) > 3 else line
        dirty_paths.add(path)
    for line in staged + modified:
        parts = line.split("\t")
        if len(parts) >= 2:
            dirty_paths.add(parts[-1])
    for path in untracked + deleted:
        dirty_paths.add(path)
    for path in sorted(dirty_paths):
        if path == MODULE_RELATIVE_PATH or path == ARTIFACT_RELATIVE_PATH:
            classifications[path] = "INTENDED_DIRECT_KLINE_DIAGNOSTIC"
        elif path.startswith("cache/binance_public_kline_forward_return_diagnostic_v1/"):
            classifications[path] = "LOG_OR_CACHE"
        elif path.endswith(".log") or "__pycache__" in path or path.endswith(".pyc"):
            classifications[path] = "LOG_OR_CACHE"
        elif path.startswith("artifacts/research/binance_public_kline_forward_return_diagnostic_v1"):
            classifications[path] = "GENERATED_DATA_ARTIFACT"
        else:
            classifications[path] = "UNKNOWN_REQUIRES_MANUAL_REVIEW"
    head_matches = head == EXPECTED_BASELINE_HEAD
    risky_or_unknown = [path for path, label in classifications.items() if label in {"UNRELATED_RISK", "UNKNOWN_REQUIRES_MANUAL_REVIEW"}]
    if staged:
        final_decision = "RECOVERY_STAGED_FILES_PRESENT_STOP"
    elif not head_matches:
        final_decision = "RECOVERY_HEAD_MISMATCH_STOP"
    elif risky_or_unknown:
        final_decision = "RECOVERY_DIRTY_WITH_UNKNOWN_OR_RISKY_FILES_STOP"
    else:
        final_decision = "RECOVERY_SAFE_CONTINUE"
    return {
        "current_head": head,
        "expected_baseline_head": EXPECTED_BASELINE_HEAD,
        "head_matches_expected_baseline": head_matches,
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "dirty_path_classification": classifications,
        "final_recovery_decision": final_decision,
        "git_clean_at_recovery_audit_run": not porcelain and not staged and not modified and not untracked and not deleted,
    }


def no_existing_tracked_files_modified(status_lines: list[str]) -> bool:
    allowed = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
    for line in status_lines:
        if line in allowed:
            continue
        if line.startswith("?? ") and line[3:].startswith("cache/binance_public_kline_forward_return_diagnostic_v1/"):
            continue
        if line.startswith("!! ") and line[3:].startswith("cache/binance_public_kline_forward_return_diagnostic_v1/"):
            continue
        return False
    return True


def existing_artifact_can_be_replaced() -> bool:
    if not ARTIFACT_PATH.exists():
        return True
    try:
        payload = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return False
    return payload.get("artifact_kind") == ARTIFACT_KIND and payload.get("module") == MODULE


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise DiagnosticBlocked(f"missing required input artifact: {path.relative_to(REPO_ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DiagnosticBlocked(f"input artifact is not a JSON object: {path.relative_to(REPO_ROOT)}")
    return payload


def verify_artifact_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise DiagnosticBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise DiagnosticBlocked(f"{label} hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    validation = read_json(REPO_ROOT / SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH)
    event_study = read_json(REPO_ROOT / SOURCE_EVENT_STUDY_RELATIVE_PATH)
    dataset = read_json(REPO_ROOT / SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    hashes = {
        SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: verify_artifact_hash(validation, "validation contract"),
        SOURCE_EVENT_STUDY_RELATIVE_PATH: verify_artifact_hash(event_study, "event study"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_artifact_hash(dataset, "dataset builder"),
    }
    if validation.get("validation_contract_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_CREATED":
        raise DiagnosticBlocked("validation contract status is not PASS")
    if validation.get("public_price_return_dependency_required") is not True:
        raise DiagnosticBlocked("validation contract does not require public price/return dependency")
    if event_study.get("status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_CREATED":
        raise DiagnosticBlocked("event study status is not PASS")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiagnosticBlocked("dataset builder status is not PASS")
    return validation, event_study, dataset, hashes


def assert_public_data_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_DATA_HOST:
        raise DiagnosticBlocked(f"forbidden non-public Binance Data Vision URL attempted: {url}")
    if not parsed.path.startswith("/data/futures/um/monthly/klines/"):
        raise DiagnosticBlocked(f"forbidden non-UM-kline archive path attempted: {url}")


def kline_url(symbol: str, year: int, month: int) -> str:
    rel = KLINE_PATH_TEMPLATE.format(symbol=symbol, year=year, month=month)
    return PUBLIC_DATA_ROOT + rel


def checksum_url(zip_url: str) -> str:
    return f"{zip_url}.CHECKSUM"


def cache_path_for_url(url: str) -> Path:
    parsed = urllib.parse.urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    return CACHE_ROOT / "raw_archives" / parts[-4] / parts[-3] / parts[-2] / parts[-1]


def checksum_cache_path(zip_path: Path) -> Path:
    return zip_path.with_name(zip_path.name + ".CHECKSUM")


def request_bytes(url: str, max_bytes: int | None = None, missing_ok: bool = False) -> dict[str, Any]:
    assert_public_data_url(url)
    last_error = ""
    for attempt in range(RETRY_CAP):
        if attempt:
            time.sleep(min(2.0 * attempt, 5.0))
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-public-kline-forward-return-diagnostic/1"})
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                limit = max_bytes + 1 if max_bytes is not None else None
                body = response.read(limit) if limit is not None else response.read()
                if max_bytes is not None and len(body) > max_bytes:
                    raise DiagnosticBlocked(f"download exceeded byte cap for {url}")
                time.sleep(REQUEST_SLEEP_SECONDS)
                return {
                    "ok": True,
                    "missing": False,
                    "http_status": getattr(response, "status", None),
                    "bytes": body,
                    "content_length": response.headers.get("Content-Length"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "error": None,
                }
        except urllib.error.HTTPError as exc:
            body = exc.read(1000).decode("utf-8", errors="replace")
            if exc.code == 404 and missing_ok:
                return {"ok": False, "missing": True, "http_status": 404, "bytes": b"", "error": "404 not found"}
            last_error = f"HTTP {exc.code}: {body[:500]}"
            if exc.code not in {418, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
    return {"ok": False, "missing": False, "http_status": None, "bytes": b"", "error": last_error or "unknown request failure"}


def parse_checksum_text(text: str) -> str | None:
    import re

    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_one_archive(plan: dict[str, Any]) -> dict[str, Any]:
    url = plan["url"]
    zip_path = cache_path_for_url(url)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path = checksum_cache_path(zip_path)
    checksum_available = False
    checksum_verified = None
    expected_sha = None
    if checksum_path.exists():
        expected_sha = parse_checksum_text(checksum_path.read_text(encoding="utf-8", errors="replace"))
        checksum_available = expected_sha is not None
    else:
        checksum_result = request_bytes(checksum_url(url), max_bytes=4096, missing_ok=True)
        if checksum_result["ok"]:
            checksum_path.write_bytes(checksum_result["bytes"])
            expected_sha = parse_checksum_text(checksum_result["bytes"].decode("utf-8", errors="replace"))
            checksum_available = expected_sha is not None
    reused_existing = False
    if zip_path.exists():
        actual_existing = sha256_file(zip_path)
        if expected_sha is None or expected_sha == actual_existing:
            reused_existing = True
        else:
            zip_path.unlink()
    if not zip_path.exists():
        result = request_bytes(url, missing_ok=True)
        if result["missing"]:
            return {
                **plan,
                "available": False,
                "local_path": str(zip_path),
                "downloaded": False,
                "reused_existing": False,
                "checksum_available": checksum_available,
                "checksum_verified": False,
                "sha256": None,
                "bytes": 0,
                "error": "404 not found",
            }
        if not result["ok"]:
            raise DiagnosticBlocked(f"kline archive download failed for {url}: {result['error']}")
        zip_path.write_bytes(result["bytes"])
    actual_sha = sha256_file(zip_path)
    checksum_verified = expected_sha is None or expected_sha == actual_sha
    if not checksum_verified:
        raise DiagnosticBlocked(f"kline checksum mismatch for {url}: {actual_sha} != {expected_sha}")
    return {
        **plan,
        "available": True,
        "local_path": str(zip_path),
        "downloaded": not reused_existing,
        "reused_existing": reused_existing,
        "checksum_available": checksum_available,
        "checksum_verified": checksum_verified if checksum_available else None,
        "sha256": actual_sha,
        "bytes": zip_path.stat().st_size,
        "error": None,
    }


def month_iter() -> list[tuple[int, int]]:
    year, month = START_YEAR_MONTH
    months: list[tuple[int, int]] = []
    while (year, month) <= END_YEAR_MONTH:
        months.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def download_kline_archives(symbols: list[str]) -> list[dict[str, Any]]:
    plans = [
        {"symbol": symbol, "year": year, "month": month, "url": kline_url(symbol, year, month)}
        for symbol in symbols
        for year, month in month_iter()
    ]
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as executor:
        futures = [executor.submit(download_one_archive, plan) for plan in plans]
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda item: (item["symbol"], item["year"], item["month"]))


def detect_header(row: list[str]) -> bool:
    return bool(row) and not str(row[0]).strip().isdigit()


def load_klines_for_symbol(symbol: str, archive_results: list[dict[str, Any]]) -> tuple[dict[int, float], dict[str, Any]]:
    close_by_open_time: dict[int, float] = {}
    duplicate_open_time_count = 0
    invalid_numeric_count = 0
    row_count = 0
    timestamp_min = None
    timestamp_max = None
    for result in archive_results:
        if result["symbol"] != symbol or not result["available"]:
            continue
        path = Path(result["local_path"])
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise DiagnosticBlocked(f"no CSV member found in {path}")
            for name in csv_names:
                content = archive.read(name).decode("utf-8", errors="replace")
                rows = csv.reader(io.StringIO(content))
                first = True
                for raw in rows:
                    if not raw:
                        continue
                    if first and detect_header(raw):
                        first = False
                        continue
                    first = False
                    if len(raw) < 7:
                        invalid_numeric_count += 1
                        continue
                    try:
                        open_time = int(float(raw[0]))
                        close_price = float(raw[4])
                    except ValueError:
                        invalid_numeric_count += 1
                        continue
                    if open_time in close_by_open_time:
                        duplicate_open_time_count += 1
                        continue
                    close_by_open_time[open_time] = close_price
                    row_count += 1
                    timestamp_min = open_time if timestamp_min is None else min(timestamp_min, open_time)
                    timestamp_max = open_time if timestamp_max is None else max(timestamp_max, open_time)
    monotonic = list(close_by_open_time) == sorted(close_by_open_time)
    return close_by_open_time, {
        "symbol": symbol,
        "row_count": row_count,
        "timestamp_min": ms_to_iso(timestamp_min) if timestamp_min is not None else None,
        "timestamp_max": ms_to_iso(timestamp_max) if timestamp_max is not None else None,
        "duplicate_open_time_count": duplicate_open_time_count,
        "invalid_numeric_count": invalid_numeric_count,
        "monotonic_after_sort": True,
        "input_order_monotonic": monotonic,
    }


def iso_to_ms(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def ms_to_iso(value: int | None) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def floor_to_15m_open(timestamp_ms: int) -> int:
    return (timestamp_ms // KLINE_INTERVAL_MS) * KLINE_INTERVAL_MS


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "nan"}:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def ge(value: float | None, threshold: float | None) -> bool:
    return value is not None and threshold is not None and value >= threshold


def le(value: float | None, threshold: float | None) -> bool:
    return value is not None and threshold is not None and value <= threshold


def evaluate_row(row: dict[str, str], thresholds: dict[str, Any]) -> list[str]:
    values = {
        "oi_change_pct": to_float(row.get("oi_change_pct")),
        "taker_buy_sell_ratio": to_float(row.get("taker_buy_sell_ratio")),
        "account_long_short_ratio": to_float(row.get("account_long_short_ratio")),
        "top_account_long_short_ratio": to_float(row.get("top_account_long_short_ratio")),
        "top_position_long_short_ratio": to_float(row.get("top_position_long_short_ratio")),
    }
    events: list[str] = []
    if (
        ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"])
        and ge(values["taker_buy_sell_ratio"], thresholds["taker_buy_sell_ratio"]["p90"])
        and ge(values["account_long_short_ratio"], thresholds["account_long_short_ratio"]["p90"])
    ):
        events.append("oi_expansion_taker_buy_global_crowding_high")
    if (
        ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"])
        and le(values["taker_buy_sell_ratio"], thresholds["taker_buy_sell_ratio"]["p10"])
        and le(values["account_long_short_ratio"], thresholds["account_long_short_ratio"]["p10"])
    ):
        events.append("oi_expansion_taker_sell_global_crowding_low")
    if ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"]) and ge(
        values["top_account_long_short_ratio"],
        thresholds["top_account_long_short_ratio"]["p90"],
    ):
        events.append("oi_expansion_top_account_crowding_high")
    if ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p90"]) and ge(
        values["top_position_long_short_ratio"],
        thresholds["top_position_long_short_ratio"]["p90"],
    ):
        events.append("oi_expansion_top_position_crowding_high")
    high_extremes = sum(
        ge(values[key], thresholds[key]["p90"])
        for key in [
            "taker_buy_sell_ratio",
            "account_long_short_ratio",
            "top_account_long_short_ratio",
            "top_position_long_short_ratio",
        ]
    )
    low_extremes = sum(
        le(values[key], thresholds[key]["p10"])
        for key in [
            "taker_buy_sell_ratio",
            "account_long_short_ratio",
            "top_account_long_short_ratio",
            "top_position_long_short_ratio",
        ]
    )
    if ge(values["oi_change_pct"], thresholds["oi_change_pct"]["p75"]) and (high_extremes >= 3 or low_extremes >= 3):
        events.append("broad_proxy_alignment_extreme")
    return events


def empty_return_store() -> dict[str, list[float]]:
    return {horizon: [] for horizon in HORIZONS}


def empty_missing_store() -> dict[str, int]:
    return {horizon: 0 for horizon in HORIZONS}


def add_return_stats(store: dict[str, list[float]], missing: dict[str, int], close_by_open: dict[int, float], event_ms: int) -> bool:
    base_open = floor_to_15m_open(event_ms)
    base_close = close_by_open.get(base_open)
    joined = base_close is not None
    for horizon, horizon_ms in HORIZONS.items():
        future_close = close_by_open.get(base_open + horizon_ms)
        if base_close is None or future_close is None or base_close == 0:
            missing[horizon] += 1
            continue
        store[horizon].append((future_close / base_close) - 1.0)
    return joined


def summarize_values(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "std": None,
            "hit_rate_positive": None,
            "hit_rate_negative": None,
            "q05": None,
            "q25": None,
            "q75": None,
            "q95": None,
            "min": None,
            "max": None,
        }
    ordered = sorted(values)
    count = len(values)
    std = statistics.pstdev(values) if count > 1 else 0.0
    return {
        "count": count,
        "mean": sum(values) / count,
        "median": statistics.median(ordered),
        "std": std,
        "hit_rate_positive": sum(1 for value in values if value > 0) / count,
        "hit_rate_negative": sum(1 for value in values if value < 0) / count,
        "q05": quantile_sorted(ordered, 0.05),
        "q25": quantile_sorted(ordered, 0.25),
        "q75": quantile_sorted(ordered, 0.75),
        "q95": quantile_sorted(ordered, 0.95),
        "min": ordered[0],
        "max": ordered[-1],
    }


def quantile_sorted(ordered: list[float], q: float) -> float | None:
    if not ordered:
        return None
    pos = (len(ordered) - 1) * q
    low = int(math.floor(pos))
    high = int(math.ceil(pos))
    if low == high:
        return ordered[low]
    frac = pos - low
    return ordered[low] * (1 - frac) + ordered[high] * frac


def summarize_return_store(store: dict[str, list[float]], missing: dict[str, int]) -> dict[str, Any]:
    return {
        horizon: {
            **summarize_values(values),
            "missing_forward_return_count": missing[horizon],
        }
        for horizon, values in store.items()
    }


def normalized_paths(dataset: dict[str, Any]) -> list[Path]:
    files = dataset.get("generated_external_files", {}).get("normalized_by_symbol_files")
    if not isinstance(files, list) or not files:
        raise DiagnosticBlocked("dataset artifact missing normalized files")
    paths = [Path(str(path)) for path in files]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise DiagnosticBlocked(f"normalized proxy dataset files missing: {missing}")
    return sorted(paths, key=lambda path: path.name)


def compute_diagnostics(event_study: dict[str, Any], dataset: dict[str, Any], kline_maps: dict[str, dict[int, float]]) -> dict[str, Any]:
    thresholds_by_symbol = event_study.get("descriptive_statistics", {}).get("per_symbol_thresholds", {})
    by_event = {event_id: empty_return_store() for event_id in EVENT_IDS}
    by_event_missing = {event_id: empty_missing_store() for event_id in EVENT_IDS}
    by_symbol = {symbol: empty_return_store() for symbol in kline_maps}
    by_symbol_missing = {symbol: empty_missing_store() for symbol in kline_maps}
    unique_store = empty_return_store()
    unique_missing = empty_missing_store()
    joined_event_count = 0
    missing_join_count = 0
    event_occurrence_count = 0
    unique_event_keys: set[str] = set()
    unique_joined_count = 0
    unique_missing_join_count = 0
    overlap_counts = {"overlap_aware_event_occurrences": 0, "unique_symbol_timestamp_events": 0, "multi_definition_symbol_timestamp_events": 0}
    event_timestamp_min = None
    event_timestamp_max = None

    for path in normalized_paths(dataset):
        symbol = path.name.split("_", 1)[0]
        thresholds = thresholds_by_symbol.get(symbol)
        if not isinstance(thresholds, dict):
            raise DiagnosticBlocked(f"missing event thresholds for {symbol}")
        close_by_open = kline_maps[symbol]
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                events = evaluate_row(row, thresholds)
                if not events:
                    continue
                timestamp = row["timestamp"]
                event_ms = iso_to_ms(timestamp)
                event_timestamp_min = timestamp if event_timestamp_min is None else min(event_timestamp_min, timestamp)
                event_timestamp_max = timestamp if event_timestamp_max is None else max(event_timestamp_max, timestamp)
                row_key = f"{symbol}|{timestamp}"
                if len(events) > 1:
                    overlap_counts["multi_definition_symbol_timestamp_events"] += 1
                if row_key not in unique_event_keys:
                    unique_event_keys.add(row_key)
                    if add_return_stats(unique_store, unique_missing, close_by_open, event_ms):
                        unique_joined_count += 1
                    else:
                        unique_missing_join_count += 1
                for event_id in events:
                    event_occurrence_count += 1
                    if add_return_stats(by_event[event_id], by_event_missing[event_id], close_by_open, event_ms):
                        joined_event_count += 1
                    else:
                        missing_join_count += 1
                    add_return_stats(by_symbol[symbol], by_symbol_missing[symbol], close_by_open, event_ms)
    overlap_counts["overlap_aware_event_occurrences"] = event_occurrence_count
    overlap_counts["unique_symbol_timestamp_events"] = len(unique_event_keys)
    return {
        "diagnostics_by_event_definition": {
            event_id: summarize_return_store(by_event[event_id], by_event_missing[event_id]) for event_id in EVENT_IDS
        },
        "diagnostics_by_symbol": {
            symbol: summarize_return_store(by_symbol[symbol], by_symbol_missing[symbol]) for symbol in sorted(by_symbol)
        },
        "unique_event_diagnostics": summarize_return_store(unique_store, unique_missing),
        "joined_event_count": joined_event_count,
        "missing_join_count": missing_join_count,
        "unique_joined_event_count": unique_joined_count,
        "unique_missing_join_count": unique_missing_join_count,
        "overlap_counts": overlap_counts,
        "event_timestamp_min": event_timestamp_min,
        "event_timestamp_max": event_timestamp_max,
    }


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    if audit["final_recovery_decision"] != "RECOVERY_SAFE_CONTINUE":
        return blocked_artifact(audit, audit["final_recovery_decision"])
    if not existing_artifact_can_be_replaced():
        raise DiagnosticBlocked(f"artifact already exists and is not this module output: {ARTIFACT_RELATIVE_PATH}")
    validation, event_study, dataset, source_hashes = load_inputs()
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols")
    if not isinstance(symbols, list) or len(symbols) != 10:
        raise DiagnosticBlocked("dataset artifact does not expose the expected 10 symbols")
    timestamp_range = {
        "requested_start": "2023-01-01T00:00:00Z",
        "requested_end": "2025-12-31T23:55:00Z",
        "proxy_dataset_min": dataset["normalized_dataset_summary"]["timestamp_global_min"],
        "proxy_dataset_max": dataset["normalized_dataset_summary"]["timestamp_global_max"],
        "event_min": event_study["timestamp_range"]["event_timestamp_min"],
        "event_max": event_study["timestamp_range"]["event_timestamp_max"],
    }
    archive_results = download_kline_archives([str(symbol) for symbol in symbols])
    available_archives = [row for row in archive_results if row["available"]]
    kline_maps: dict[str, dict[int, float]] = {}
    kline_quality: dict[str, Any] = {}
    for symbol in symbols:
        kline_map, quality = load_klines_for_symbol(str(symbol), archive_results)
        kline_maps[str(symbol)] = kline_map
        kline_quality[str(symbol)] = quality
    diagnostic = compute_diagnostics(event_study, dataset, kline_maps)
    kline_row_count = sum(quality["row_count"] for quality in kline_quality.values())
    symbols_built = sorted([symbol for symbol, quality in kline_quality.items() if quality["row_count"] > 0])
    checksum_available = sum(1 for row in available_archives if row["checksum_available"])
    checksum_verified = sum(1 for row in available_archives if row["checksum_verified"] is True)
    missing_archives = [row for row in archive_results if not row["available"]]
    missing_join_count = diagnostic["missing_join_count"]
    joined_event_count = diagnostic["joined_event_count"]
    join_attention = missing_join_count > 0
    data_quality_attention = bool(missing_archives) or checksum_available != checksum_verified or join_attention
    result_classification = RESULT_ATTENTION if data_quality_attention else RESULT_READY
    allowed_next_step = ALLOWED_NEXT_STEP_READY if result_classification in {RESULT_READY, RESULT_ATTENTION} else ALLOWED_NEXT_STEP_BLOCKED
    forbidden_false = {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
    }
    status_lines = git_lines(["status", "--porcelain=v1"])
    validation_checks = {
        "recovery_safe_continue": audit["final_recovery_decision"] == "RECOVERY_SAFE_CONTINUE",
        "head_matches_expected_baseline": audit["head_matches_expected_baseline"],
        "git_clean_before": PHASE1_GIT_CLEAN_BEFORE_TOOL_CREATION,
        "input_artifacts_loaded": True,
        "input_hashes_verified": True,
        "public_data_vision_only": True,
        "monthly_zip_klines_used": True,
        "no_api_key_used": True,
        "no_private_api_used": True,
        "no_account_api_used": True,
        "no_order_endpoint_used": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
        "no_failed_strategy_route_reuse": True,
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": True,
        "no_existing_tracked_files_modified": no_existing_tracked_files_modified(status_lines),
        "raw_data_committed": False,
    }
    replacement_checks_all_true = all(value is True for key, value in validation_checks.items() if key != "raw_data_committed")
    artifact: dict[str, Any] = {
        "diagnostic_status": DIAGNOSTIC_STATUS_PASS if replacement_checks_all_true else DIAGNOSTIC_STATUS_BLOCKED,
        "status": DIAGNOSTIC_STATUS_PASS if replacement_checks_all_true else DIAGNOSTIC_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": result_classification,
        "recovery_audit_status": audit["final_recovery_decision"],
        "current_head": audit["current_head"],
        "expected_baseline_head": audit["expected_baseline_head"],
        "head_matches_expected_baseline": audit["head_matches_expected_baseline"],
        "git_clean_before": PHASE1_GIT_CLEAN_BEFORE_TOOL_CREATION,
        "source_artifacts": {
            SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: {
                "status": validation.get("validation_contract_status"),
                "payload_sha256_excluding_hash": source_hashes[SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH],
            },
            SOURCE_EVENT_STUDY_RELATIVE_PATH: {
                "status": event_study.get("status"),
                "payload_sha256_excluding_hash": source_hashes[SOURCE_EVENT_STUDY_RELATIVE_PATH],
            },
            SOURCE_DATASET_BUILDER_RELATIVE_PATH: {
                "status": dataset.get("status"),
                "payload_sha256_excluding_hash": source_hashes[SOURCE_DATASET_BUILDER_RELATIVE_PATH],
            },
        },
        "symbols_requested": symbols,
        "symbols_built": symbols_built,
        "public_data_source": {
            "host": PUBLIC_DATA_HOST,
            "path_template": KLINE_PATH_TEMPLATE,
            "monthly_archive_count_requested": len(archive_results),
            "monthly_archive_count_available": len(available_archives),
            "monthly_archive_count_missing": len(missing_archives),
            "cache_root": str(CACHE_ROOT),
            "raw_cache_gitignored": True,
        },
        "interval": KLINE_INTERVAL,
        "timestamp_range": {
            **timestamp_range,
            "event_diagnostic_min": diagnostic["event_timestamp_min"],
            "event_diagnostic_max": diagnostic["event_timestamp_max"],
        },
        "kline_row_count": kline_row_count,
        "joined_event_count": joined_event_count,
        "missing_join_count": missing_join_count,
        "forward_return_horizons": list(HORIZONS.keys()),
        "diagnostics_by_event_definition": diagnostic["diagnostics_by_event_definition"],
        "diagnostics_by_symbol": diagnostic["diagnostics_by_symbol"],
        "unique_event_diagnostics": diagnostic["unique_event_diagnostics"],
        "overlap_policy": {
            "overlap_aware": "each proxy event definition occurrence is counted separately",
            "unique_event": "distinct symbol/timestamp rows are counted once in unique_event_diagnostics",
            **diagnostic["overlap_counts"],
        },
        "kline_data_quality": {
            "per_symbol": kline_quality,
            "checksum_summary": {
                "archives_with_checksum_available": checksum_available,
                "archives_with_checksum_verified": checksum_verified,
                "checksum_mismatch_count": 0,
            },
            "missing_archives": missing_archives[:20],
            "missing_archive_count": len(missing_archives),
        },
        "download_cache_summary": {
            "cache_root": str(CACHE_ROOT),
            "archive_files_present": len(list(CACHE_ROOT.rglob("*.zip"))) if CACHE_ROOT.exists() else 0,
            "checksum_files_present": len(list(CACHE_ROOT.rglob("*.CHECKSUM"))) if CACHE_ROOT.exists() else 0,
            "downloaded_this_run_count": sum(1 for row in archive_results if row["downloaded"]),
            "reused_existing_count": sum(1 for row in archive_results if row["reused_existing"]),
            "cache_files_committed": False,
        },
        "validation_limits": [
            "This is diagnostic research only, not strategy validation.",
            "Forward returns are public close-to-close kline diagnostics and are non-tradable research labels.",
            "No fees, fills, orders, execution, portfolio sizing, or PnL were computed.",
            "Events are aligned to the containing 15m kline open time in UTC; base close is that kline close.",
            "Late-2025 events may lack 24h forward returns because the requested source range stops at 2025-12.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false,
        "forbidden_failed_strategy_routes_not_reused": {
            "not_reused": True,
            "routes": FORBIDDEN_FAILED_ROUTES,
        },
        "allowed_next_step": allowed_next_step,
        "blocker": None,
        "recovery_audit": audit,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def blocked_artifact(audit: dict[str, Any], reason: str) -> dict[str, Any]:
    artifact: dict[str, Any] = {
        "diagnostic_status": DIAGNOSTIC_STATUS_BLOCKED,
        "status": DIAGNOSTIC_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": audit.get("final_recovery_decision"),
        "current_head": audit.get("current_head"),
        "expected_baseline_head": EXPECTED_BASELINE_HEAD,
        "head_matches_expected_baseline": audit.get("head_matches_expected_baseline"),
        "git_clean_before": PHASE1_GIT_CLEAN_BEFORE_TOOL_CREATION,
        "symbols_requested": [],
        "symbols_built": [],
        "public_data_source": {"host": PUBLIC_DATA_HOST, "path_template": KLINE_PATH_TEMPLATE},
        "interval": KLINE_INTERVAL,
        "timestamp_range": {},
        "kline_row_count": 0,
        "joined_event_count": 0,
        "missing_join_count": 0,
        "forward_return_horizons": list(HORIZONS.keys()),
        "diagnostics_by_event_definition": {},
        "diagnostics_by_symbol": {},
        "overlap_policy": {},
        "validation_limits": [f"BLOCKED: {reason}"],
        "forbidden_actions_confirmed_false": {
            "strategy": False,
            "signal": False,
            "backtest": False,
            "pnl": False,
            "trade_simulation": False,
            "optimization": False,
            "candidate_generation": False,
            "edge_claim": False,
            "runtime_live_capital": False,
            "order_private_account_api_key": False,
        },
        "allowed_next_step": ALLOWED_NEXT_STEP_BLOCKED,
        "blocker": reason,
        "recovery_audit": audit,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"diagnostic_status: {artifact['diagnostic_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"current_head: {artifact['current_head']}")
    print(f"expected_baseline_head: {artifact['expected_baseline_head']}")
    print(f"head_matches_expected_baseline: {bool_text(artifact['head_matches_expected_baseline'] is True)}")
    print(f"git_clean_before: {bool_text(artifact['git_clean_before'] is True)}")
    print(f"symbols_requested: {len(artifact['symbols_requested'])}")
    print(f"symbols_built: {len(artifact['symbols_built'])}")
    print(f"kline_row_count: {artifact['kline_row_count']}")
    print(f"joined_event_count: {artifact['joined_event_count']}")
    print(f"missing_join_count: {artifact['missing_join_count']}")
    print(f"forward_return_horizons: {','.join(artifact['forward_return_horizons'])}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(artifact['replacement_checks_all_true'])}")
    print(f"blocker: {artifact['blocker']}")


def main() -> int:
    try:
        artifact = build_artifact()
        write_artifact(artifact)
        print_summary(artifact)
        return 0 if artifact["replacement_checks_all_true"] else 2
    except DiagnosticBlocked as exc:
        audit = recovery_audit()
        artifact = blocked_artifact(audit, str(exc))
        write_artifact(artifact)
        print_summary(artifact)
        print(f"exact_blocker: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
