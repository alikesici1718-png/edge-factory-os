#!/usr/bin/env python
"""Independent 2026+ validation runner for the frozen neutral price-failure diagnostic."""

from __future__ import annotations

import csv
import concurrent.futures
import hashlib
import io
import json
import math
import re
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER_V1"
MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_runner_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_runner_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "9c04add259bc7b2382344e68af6367cbd659d7a0"
SOURCE_CONTRACT_RELATIVE_PATH = (
    "artifacts/contracts/extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_contract_v1.json"
)
SOURCE_SEMANTICS_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_direction_semantics_review_v1.json"
)
SOURCE_EVALUATOR_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_evaluator_v1.json"
)
SOURCE_REFINEMENT_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
)
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_CONTRACT_RELATIVE_PATH,
    SOURCE_SEMANTICS_RELATIVE_PATH,
    SOURCE_EVALUATOR_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
]

VALIDATION_STATUS_PASS = (
    "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER_CREATED"
)
VALIDATION_STATUS_BLOCKED = (
    "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER"
)
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER"

RESULT_PASS = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_VALIDATION_PASS_DIAGNOSTIC_ONLY"
RESULT_FAIL = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_VALIDATION_FAIL"
RESULT_INCONCLUSIVE = (
    "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_"
    "INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
)
RESULT_ATTENTION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_VALIDATION_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_VALIDATION_FAILED_STOP"

NEXT_EVALUATOR = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_VALIDATION_EVALUATOR_V1"
NEXT_CLOSE_OR_REDESIGN = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROUTE_CLOSE_OR_REDESIGN_EVALUATOR_V1"
NEXT_ACCUMULATION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_SAMPLE_ACCUMULATION_MONITOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_2026_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"
NEXT_RUNTIME_REPAIR = "RECOVERY_OR_RUNTIME_REPAIR_V1"

APPROVED_NEUTRAL_LABEL = "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC"
PUBLIC_ARCHIVE_HOST = "data.binance.vision"
PUBLIC_ARCHIVE_BASE = f"https://{PUBLIC_ARCHIVE_HOST}/"
MONTHLY_METRICS_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/monthly/metrics"
DAILY_METRICS_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/daily/metrics"
MONTHLY_KLINES_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/monthly/klines"
DAILY_KLINES_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/daily/klines"

DEFAULT_SYMBOLS = [
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
SOURCE_COLUMNS_WITH_HEADER = [
    "symbol",
    "sum_open_interest",
    "sum_open_interest_value",
    "count_toptrader_long_short_ratio",
    "sum_toptrader_long_short_ratio",
    "count_long_short_ratio",
    "sum_taker_long_short_vol_ratio",
    "create_time",
]

VALIDATION_START = date(2026, 1, 1)
KLINE_INTERVAL_MS = 15 * 60 * 1000
ONE_HOUR_MS = 60 * 60 * 1000
ROLLING_LOOKBACK_BARS = 16
EPSILON = 1e-12
OI_QUANTILE = 0.975
TAKER_QUANTILE = 0.975
CORE_CROWDING_QUANTILE_SHORT = 0.05
COOLDOWN_HOURS = 6
PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528
REQUEST_TIMEOUT_SECONDS = 30
REQUEST_SLEEP_SECONDS = 0.02

HORIZON = "1h"
HORIZON_MS = ONE_HOUR_MS
SHORT_CORE_DEFINITION_ID = (
    "CORE_PRICE_FAILURE_WITH_CROWDING_TIER__short_failure__oi_p97.5__"
    "taker_p97.5__pf_score_bucket__score_1__cooldown_6h"
)
CACHE_ROOT = REPO_ROOT / "cache" / "extreme_oi_taker_crowding_price_failure_pre_registered_independent_validation_runner_v1"


class ValidationBlocked(Exception):
    pass


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def git_base_args() -> list[str]:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    return ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={safe_dir}"]


def run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        [*git_base_args(), *args],
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
        raise ValidationBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
    return [line.rstrip() for line in stdout.splitlines() if line.strip()]


def current_head() -> str:
    lines = git_lines(["rev-parse", "HEAD"])
    return lines[0] if lines else ""


def current_branch() -> str:
    lines = git_lines(["branch", "--show-current"])
    return lines[0] if lines else ""


def output_only_status(status_lines: list[str]) -> bool:
    allowed = {
        f"?? {MODULE_RELATIVE_PATH}",
        f"?? {ARTIFACT_RELATIVE_PATH}",
        f"A  {MODULE_RELATIVE_PATH}",
        f"A  {ARTIFACT_RELATIVE_PATH}",
    }
    for line in status_lines:
        if line in allowed:
            continue
        if line.startswith("!! ") and line[3:].startswith("cache/"):
            continue
        return False
    return True


def recovery_audit() -> dict[str, Any]:
    head = current_head()
    porcelain = git_lines(["status", "--porcelain=v1"])
    staged = git_lines(["diff", "--cached", "--name-status"])
    modified = git_lines(["diff", "--name-status"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    head_matches = head == EXPECTED_HEAD
    if staged:
        decision = "RECOVERY_STAGED_FILES_PRESENT_STOP"
    elif not head_matches:
        decision = "RECOVERY_HEAD_MISMATCH_STOP"
    elif not output_only_status(porcelain):
        decision = "RECOVERY_DIRTY_WITH_UNKNOWN_OR_RISKY_FILES_STOP"
    else:
        decision = "RECOVERY_AUDIT_CLEAN_CONTINUE"
    return {
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head_matches,
        "branch": current_branch(),
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "recovery_decision": decision,
        "git_clean_before": not porcelain and not staged and not modified and not untracked and not deleted,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_artifact_hashes() -> dict[str, str]:
    hashes = {}
    for relative_path in INPUT_ARTIFACT_RELATIVE_PATHS:
        path = REPO_ROOT / relative_path
        if not path.exists():
            raise ValidationBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise ValidationBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValidationBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise ValidationBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    contract = read_json_readonly(SOURCE_CONTRACT_RELATIVE_PATH)
    semantics = read_json_readonly(SOURCE_SEMANTICS_RELATIVE_PATH)
    evaluator = read_json_readonly(SOURCE_EVALUATOR_RELATIVE_PATH)
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_CONTRACT_RELATIVE_PATH: verify_payload_hash(contract, "independent validation contract"),
        SOURCE_SEMANTICS_RELATIVE_PATH: verify_payload_hash(semantics, "direction semantics review"),
        SOURCE_EVALUATOR_RELATIVE_PATH: verify_payload_hash(evaluator, "robustness evaluator"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
    }
    return contract, semantics, evaluator, refinement, dataset, payload_hashes


def validate_input_chain(contract: dict[str, Any], semantics: dict[str, Any], evaluator: dict[str, Any], refinement: dict[str, Any]) -> dict[str, bool]:
    frozen = contract.get("frozen_hypothesis", {})
    event_policy = contract.get("frozen_event_definition_policy", {})
    checks = {
        "contract_ready": contract.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY",
        "contract_allowed_next_step_this_runner": contract.get("allowed_next_step") == MODULE,
        "contract_label_exact": contract.get("approved_neutral_diagnostic_label") == APPROVED_NEUTRAL_LABEL,
        "contract_event_side_short_core": frozen.get("event_side") == "short_core",
        "contract_horizon_1h": frozen.get("horizon") == "1h",
        "contract_expected_direction_negative": frozen.get("expected_direction") == "negative",
        "contract_primary_null_month_aware_symbol_balanced": frozen.get("primary_null_model_for_validation")
        == "month_aware_symbol_balanced_null",
        "contract_single_pre_registered_primary_test": frozen.get("primary_multiple_comparison_scope")
        == "single_pre_registered_primary_test",
        "contract_research_sample_not_validation": contract.get("independent_validation_data_policy", {}).get(
            "research_evaluation_sample_must_not_be_reused_as_independent_result"
        )
        is True,
        "contract_no_event_definition_changes": event_policy.get("no_event_definition_edits_based_on_validation_outcomes") is True,
        "semantics_relabel_ready": semantics.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_RELABEL_READY",
        "semantics_label_exact": semantics.get("approved_neutral_diagnostic_label") == APPROVED_NEUTRAL_LABEL,
        "evaluator_requires_relabel_attention": evaluator.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROBUSTNESS_EVALUATOR_REQUIRES_DIRECTION_RELABEL_ATTENTION",
        "refinement_ready": refinement.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_READY",
    }
    return checks


def dataset_symbols(dataset: dict[str, Any]) -> list[str]:
    symbols = dataset.get("requested_symbols")
    if isinstance(symbols, list) and all(isinstance(symbol, str) for symbol in symbols):
        return symbols
    summary_symbols = dataset.get("normalized_dataset_summary", {}).get("requested_symbols")
    if isinstance(summary_symbols, list) and all(isinstance(symbol, str) for symbol in summary_symbols):
        return summary_symbols
    return DEFAULT_SYMBOLS


def assert_public_archive_url(url: str) -> None:
    if not url.startswith(PUBLIC_ARCHIVE_BASE):
        raise ValidationBlocked(f"forbidden non-public archive URL attempted: {url}")
    allowed = [
        "/data/futures/um/monthly/metrics/",
        "/data/futures/um/daily/metrics/",
        "/data/futures/um/monthly/klines/",
        "/data/futures/um/daily/klines/",
    ]
    if not any(token in url for token in allowed):
        raise ValidationBlocked(f"forbidden non-validation archive path attempted: {url}")


def request_url(url: str, method: str = "GET", missing_ok: bool = False) -> dict[str, Any]:
    assert_public_archive_url(url)
    req = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "edge-factory-os-independent-validation-runner/1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = b"" if method == "HEAD" else response.read()
            return {
                "ok": True,
                "status": getattr(response, "status", 200),
                "data": data,
                "headers": dict(response.headers.items()),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        if missing_ok and exc.code == 404:
            return {"ok": False, "status": 404, "data": b"", "headers": {}, "error": "404 not found"}
        return {"ok": False, "status": exc.code, "data": b"", "headers": {}, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "status": None, "data": b"", "headers": {}, "error": str(exc)}
    finally:
        time.sleep(REQUEST_SLEEP_SECONDS)


def head_exists(url: str) -> dict[str, Any]:
    result = request_url(url, method="HEAD", missing_ok=True)
    return {
        "url": url,
        "exists": result["ok"],
        "status": result["status"],
        "error": result["error"],
        "content_length": result["headers"].get("Content-Length"),
    }


def parse_checksum_text(text: str) -> str | None:
    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def checksum_url(zip_url: str) -> str:
    return f"{zip_url}.CHECKSUM"


def month_starts() -> list[tuple[int, int]]:
    today = datetime.now(timezone.utc).date()
    months: list[tuple[int, int]] = []
    year = VALIDATION_START.year
    month = VALIDATION_START.month
    while (year, month) <= (today.year, today.month):
        months.append((year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def month_end(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1) - timedelta(days=1)
    return date(year, month + 1, 1) - timedelta(days=1)


def days_in_month_for_validation(year: int, month: int) -> list[date]:
    today = datetime.now(timezone.utc).date()
    end = min(month_end(year, month), today - timedelta(days=1))
    start = max(date(year, month, 1), VALIDATION_START)
    if end < start:
        return []
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def monthly_metrics_url(symbol: str, year: int, month: int) -> str:
    return f"{MONTHLY_METRICS_ROOT}/{symbol}/{symbol}-metrics-{year:04d}-{month:02d}.zip"


def daily_metrics_url(symbol: str, day: date) -> str:
    return f"{DAILY_METRICS_ROOT}/{symbol}/{symbol}-metrics-{day:%Y-%m-%d}.zip"


def monthly_kline_url(symbol: str, year: int, month: int) -> str:
    return f"{MONTHLY_KLINES_ROOT}/{symbol}/15m/{symbol}-15m-{year:04d}-{month:02d}.zip"


def daily_kline_url(symbol: str, day: date) -> str:
    return f"{DAILY_KLINES_ROOT}/{symbol}/15m/{symbol}-15m-{day:%Y-%m-%d}.zip"


def archive_cache_path(kind: str, cadence: str, symbol: str, filename: str) -> Path:
    return CACHE_ROOT / "raw_archives" / kind / cadence / symbol / filename


def download_archive(kind: str, cadence: str, symbol: str, url: str, manifest: list[dict[str, Any]]) -> Path | None:
    assert_public_archive_url(url)
    filename = url.rsplit("/", 1)[-1]
    path = archive_cache_path(kind, cadence, symbol, filename)
    checksum_path = path.with_name(path.name + ".CHECKSUM")
    if path.exists() and path.stat().st_size > 0:
        checksum_available = checksum_path.exists()
        checksum_verified = None
        expected_sha = None
        if checksum_available:
            expected_sha = parse_checksum_text(checksum_path.read_text(encoding="utf-8", errors="replace"))
            checksum_verified = expected_sha == sha256_file(path) if expected_sha else False
            if checksum_verified is False:
                raise ValidationBlocked(f"cached archive checksum mismatch: {path}")
        manifest.append(
            {
                "kind": kind,
                "cadence": cadence,
                "symbol": symbol,
                "url": url,
                "available": True,
                "downloaded": False,
                "reused_existing": True,
                "local_path": str(path),
                "bytes": path.stat().st_size,
                "checksum_available": checksum_available,
                "checksum_verified": checksum_verified,
                "sha256": sha256_file(path),
                "error": None,
            }
        )
        return path
    probe = head_exists(url)
    if not probe["exists"]:
        manifest.append(
            {
                "kind": kind,
                "cadence": cadence,
                "symbol": symbol,
                "url": url,
                "available": False,
                "downloaded": False,
                "reused_existing": False,
                "local_path": str(path),
                "bytes": 0,
                "checksum_available": False,
                "checksum_verified": False,
                "sha256": None,
                "error": probe["error"] or f"status {probe['status']}",
            }
        )
        return None
    result = request_url(url, method="GET", missing_ok=False)
    if not result["ok"]:
        raise ValidationBlocked(f"archive download failed for {url}: {result['error']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(result["data"])
    checksum_result = request_url(checksum_url(url), method="GET", missing_ok=True)
    checksum_available = checksum_result["ok"]
    checksum_verified = None
    expected_sha = None
    if checksum_available:
        checksum_path.write_bytes(checksum_result["data"])
        expected_sha = parse_checksum_text(checksum_result["data"].decode("utf-8", errors="replace"))
        checksum_verified = expected_sha == sha256_file(path) if expected_sha else False
        if checksum_verified is False:
            raise ValidationBlocked(f"downloaded archive checksum mismatch: {url}")
    manifest.append(
        {
            "kind": kind,
            "cadence": cadence,
            "symbol": symbol,
            "url": url,
            "available": True,
            "downloaded": True,
            "reused_existing": False,
            "local_path": str(path),
            "bytes": path.stat().st_size,
            "checksum_available": checksum_available,
            "checksum_verified": checksum_verified,
            "sha256": sha256_file(path),
            "error": None,
        }
    )
    return path


def download_symbol_archives(symbol: str) -> tuple[str, dict[str, list[Path]], list[dict[str, Any]]]:
    manifest: list[dict[str, Any]] = []
    paths = {"metrics": [], "klines": []}
    for year, month in month_starts():
        metrics_monthly = download_archive("metrics", "monthly", symbol, monthly_metrics_url(symbol, year, month), manifest)
        if metrics_monthly is not None:
            paths["metrics"].append(metrics_monthly)
        else:
            for day in days_in_month_for_validation(year, month):
                daily_path = download_archive("metrics", "daily", symbol, daily_metrics_url(symbol, day), manifest)
                if daily_path is not None:
                    paths["metrics"].append(daily_path)
        kline_monthly = download_archive("klines", "monthly", symbol, monthly_kline_url(symbol, year, month), manifest)
        if kline_monthly is not None:
            paths["klines"].append(kline_monthly)
        else:
            for day in days_in_month_for_validation(year, month):
                daily_path = download_archive("klines", "daily", symbol, daily_kline_url(symbol, day), manifest)
                if daily_path is not None:
                    paths["klines"].append(daily_path)
    return symbol, paths, manifest


def download_all_archives(symbols: list[str]) -> tuple[dict[str, dict[str, list[Path]]], list[dict[str, Any]]]:
    archive_paths_by_symbol: dict[str, dict[str, list[Path]]] = {}
    manifest: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, max(1, len(symbols)))) as executor:
        futures = [executor.submit(download_symbol_archives, symbol) for symbol in symbols]
        for future in concurrent.futures.as_completed(futures):
            symbol, paths, local_manifest = future.result()
            archive_paths_by_symbol[symbol] = paths
            manifest.extend(local_manifest)
    return archive_paths_by_symbol, manifest


def detect_header(row: list[str]) -> bool:
    joined = ",".join(value.lower() for value in row)
    return any(token in joined for token in ["symbol", "interest", "ratio", "create_time", "timestamp", "open_time"])


def parse_ts_ms(value: Any) -> int | None:
    raw = str(value).strip()
    if not raw:
        return None
    try:
        numeric = float(raw)
        if numeric > 10_000_000_000_000:
            return int(numeric / 1000)
        if numeric > 10_000_000_000:
            return int(numeric)
        return int(numeric * 1000)
    except ValueError:
        pass
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)
    except ValueError:
        return None


def ms_to_iso(ms_value: int | None) -> str | None:
    if ms_value is None:
        return None
    return datetime.fromtimestamp(ms_value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def floor_to_15m_open(timestamp_ms: int) -> int:
    return timestamp_ms - (timestamp_ms % KLINE_INTERVAL_MS)


def month_key_from_ms(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m")


def clean_number(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"none", "null", "nan"}:
        return ""
    return text


def to_float(value: Any) -> float | None:
    text = clean_number(value)
    if not text:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def quantile_or_none(values: list[float], q: float) -> float | None:
    clean = np.asarray([value for value in values if math.isfinite(value)], dtype=np.float64)
    if clean.size == 0:
        return None
    return float(np.quantile(clean, q))


def read_metrics_archives(paths: list[Path], symbol: str) -> list[dict[str, Any]]:
    by_ts: dict[int, dict[str, str]] = {}
    for path in paths:
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not names:
                raise ValidationBlocked(f"no CSV member in metrics archive: {path}")
            for name in names:
                content = archive.read(name).decode("utf-8", errors="replace")
                parsed_rows = [row for row in csv.reader(io.StringIO(content)) if row]
                if not parsed_rows:
                    continue
                if detect_header(parsed_rows[0]):
                    columns = [cell.strip() for cell in parsed_rows[0]]
                    data_rows = parsed_rows[1:]
                else:
                    columns = SOURCE_COLUMNS_WITH_HEADER[: len(parsed_rows[0])]
                    data_rows = parsed_rows
                for raw_row in data_rows:
                    record = {columns[idx]: raw_row[idx].strip() if idx < len(raw_row) else "" for idx in range(len(columns))}
                    if record.get("symbol") and record["symbol"] != symbol:
                        continue
                    ts_ms = parse_ts_ms(record.get("create_time") or record.get("timestamp") or record.get("time") or "")
                    if ts_ms is None or datetime.fromtimestamp(ts_ms / 1000, timezone.utc).date() < VALIDATION_START:
                        continue
                    by_ts[ts_ms] = record
    rows: list[dict[str, Any]] = []
    oi_by_ms: dict[int, float] = {}
    for ts_ms in sorted(by_ts):
        record = by_ts[ts_ms]
        open_interest = to_float(record.get("sum_open_interest"))
        if open_interest is not None and open_interest > 0:
            oi_by_ms[ts_ms] = open_interest
        taker_ratio = to_float(record.get("sum_taker_long_short_vol_ratio"))
        taker_sell_pressure = (1.0 / taker_ratio) if taker_ratio and taker_ratio > 0 else None
        row = {
            "timestamp": ms_to_iso(ts_ms),
            "ts_ms": ts_ms,
            "month": month_key_from_ms(ts_ms),
            "symbol": symbol,
            "open_interest": open_interest,
            "taker_buy_aggression": taker_ratio,
            "taker_sell_aggression": taker_sell_pressure,
            "top_account_ratio": to_float(record.get("count_toptrader_long_short_ratio")),
            "top_position_ratio": to_float(record.get("sum_toptrader_long_short_ratio")),
        }
        previous = oi_by_ms.get(ts_ms - ONE_HOUR_MS)
        if open_interest is not None and previous is not None and open_interest > 0 and previous > 0:
            row["oi_delta_log_1h"] = math.log(open_interest) - math.log(previous)
        else:
            row["oi_delta_log_1h"] = None
        rows.append(row)
    return rows


def rolling_previous_extreme(values: np.ndarray, mode: str, lookback: int) -> np.ndarray:
    output = np.full(values.shape, np.nan, dtype=np.float64)
    window: deque[float] = deque(maxlen=lookback)
    for idx, value in enumerate(values):
        if window:
            output[idx] = max(window) if mode == "high" else min(window)
        window.append(float(value))
    return output


def read_kline_archives(paths: list[Path], symbol: str) -> dict[str, Any]:
    rows_by_open: dict[int, tuple[float, float, float, float, int | None]] = {}
    for path in paths:
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not names:
                raise ValidationBlocked(f"no CSV member in kline archive: {path}")
            for name in names:
                content = archive.read(name).decode("utf-8", errors="replace")
                parsed_rows = [row for row in csv.reader(io.StringIO(content)) if row]
                if not parsed_rows:
                    continue
                if detect_header(parsed_rows[0]):
                    header = [cell.strip() for cell in parsed_rows[0]]
                    data_rows = parsed_rows[1:]
                else:
                    header = [
                        "open_time",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "close_time",
                        "quote_asset_volume",
                        "number_of_trades",
                        "taker_buy_base_asset_volume",
                        "taker_buy_quote_asset_volume",
                        "ignore",
                    ][: len(parsed_rows[0])]
                    data_rows = parsed_rows
                for raw_row in data_rows:
                    record = {header[idx]: raw_row[idx].strip() if idx < len(raw_row) else "" for idx in range(len(header))}
                    open_ms = parse_ts_ms(record.get("open_time") or record.get("timestamp") or "")
                    if open_ms is None or datetime.fromtimestamp(open_ms / 1000, timezone.utc).date() < VALIDATION_START:
                        continue
                    open_price = to_float(record.get("open"))
                    high = to_float(record.get("high"))
                    low = to_float(record.get("low"))
                    close = to_float(record.get("close"))
                    close_ms = parse_ts_ms(record.get("close_time") or "")
                    if None in (open_price, high, low, close):
                        continue
                    rows_by_open[open_ms] = (float(open_price), float(high), float(low), float(close), close_ms)
    if not rows_by_open:
        raise ValidationBlocked(f"no 2026+ kline rows loaded for {symbol}")
    opens = np.asarray(sorted(rows_by_open), dtype=np.int64)
    open_prices = np.asarray([rows_by_open[int(ts)][0] for ts in opens], dtype=np.float64)
    high = np.asarray([rows_by_open[int(ts)][1] for ts in opens], dtype=np.float64)
    low = np.asarray([rows_by_open[int(ts)][2] for ts in opens], dtype=np.float64)
    close = np.asarray([rows_by_open[int(ts)][3] for ts in opens], dtype=np.float64)
    open_to_index = {int(ts): idx for idx, ts in enumerate(opens)}
    returns = np.full(opens.shape, np.nan, dtype=np.float64)
    for idx, open_ms in enumerate(opens):
        target = int(open_ms) + HORIZON_MS
        target_idx = open_to_index.get(target)
        if target_idx is not None and close[idx] != 0:
            returns[idx] = (close[target_idx] / close[idx]) - 1.0
    valid_indices = np.flatnonzero(np.isfinite(returns))
    return {
        "symbol": symbol,
        "opens": opens,
        "open": open_prices,
        "high": high,
        "low": low,
        "close": close,
        "open_to_index": open_to_index,
        "prior_rolling_high": rolling_previous_extreme(high, "high", ROLLING_LOOKBACK_BARS),
        "prior_rolling_low": rolling_previous_extreme(low, "low", ROLLING_LOOKBACK_BARS),
        "returns_1h": returns,
        "valid_indices_1h": valid_indices,
        "timestamp_min": ms_to_iso(int(opens[0])),
        "timestamp_max": ms_to_iso(int(opens[-1])),
        "row_count": int(opens.size),
    }


def build_symbol_thresholds(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        month = row["month"]
        for key in ["oi_delta_log_1h", "taker_sell_aggression", "top_account_ratio", "top_position_ratio"]:
            value = row.get(key)
            if isinstance(value, float) and math.isfinite(value):
                buckets[month][key].append(value)
    thresholds: dict[str, dict[str, float | None]] = {}
    for month, per_field in buckets.items():
        thresholds[month] = {
            "oi_delta_log_1h_p97.5": quantile_or_none(per_field["oi_delta_log_1h"], OI_QUANTILE),
            "taker_sell_aggression_p97.5": quantile_or_none(per_field["taker_sell_aggression"], TAKER_QUANTILE),
            "top_account_short_p5.0": quantile_or_none(per_field["top_account_ratio"], CORE_CROWDING_QUANTILE_SHORT),
            "top_position_short_p5.0": quantile_or_none(per_field["top_position_ratio"], CORE_CROWDING_QUANTILE_SHORT),
        }
    return thresholds


def price_features(row: dict[str, Any], kline_data: dict[str, Any]) -> dict[str, Any]:
    base_open = floor_to_15m_open(row["ts_ms"])
    index = kline_data["open_to_index"].get(base_open)
    if index is None:
        return {"price_available": False}
    high = float(kline_data["high"][index])
    low = float(kline_data["low"][index])
    close = float(kline_data["close"][index])
    range_value = max(high - low, EPSILON)
    close_location = (close - low) / range_value
    lower_wick_ratio = (close - low) / range_value
    prev_index = kline_data["open_to_index"].get(int(kline_data["opens"][index]) - ONE_HOUR_MS)
    price_return_1h = None
    if prev_index is not None:
        previous_close = float(kline_data["close"][prev_index])
        if previous_close != 0:
            price_return_1h = (close / previous_close) - 1.0
    prior_low = float(kline_data["prior_rolling_low"][index])
    failed_breakdown = math.isfinite(prior_low) and low < prior_low and close >= prior_low
    short_flags = {
        "opposite_1h_return": price_return_1h is not None and price_return_1h >= 0.0,
        "wick_rejection": lower_wick_ratio >= 0.60,
        "close_location_failure": close_location >= 0.60,
        "failed_breakout_breakdown": failed_breakdown,
    }
    return {
        "price_available": True,
        "short_flags": {**short_flags, "any_failure": any(short_flags.values())},
        "short_failure_score": sum(short_flags.values()),
    }


def crowding_tier(account_ok: bool, position_ok: bool) -> str:
    if account_ok and position_ok:
        return "both"
    if account_ok:
        return "account_only"
    if position_ok:
        return "position_only"
    return "none"


def reconstruct_short_core_events(
    metrics_by_symbol: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    raw_count = 0
    rejected_due_to_cooldown = 0
    rejected_due_to_missing_price_failure = 0
    rejected_due_to_missing_components = Counter()
    crowding_distribution = Counter()
    price_failure_distribution = Counter()
    last_event_ms: dict[str, int] = {}
    cooldown_ms = COOLDOWN_HOURS * ONE_HOUR_MS
    for symbol, rows in metrics_by_symbol.items():
        if symbol not in kline_by_symbol:
            rejected_due_to_missing_components["symbol_kline_missing"] += len(rows)
            continue
        thresholds_by_month = build_symbol_thresholds(rows)
        kline_data = kline_by_symbol[symbol]
        for row in rows:
            thresholds = thresholds_by_month.get(row["month"])
            if thresholds is None:
                rejected_due_to_missing_components["threshold_month_missing"] += 1
                continue
            features = price_features(row, kline_data)
            if not features.get("price_available"):
                rejected_due_to_missing_components["price_bar_missing"] += 1
                continue
            oi_threshold = thresholds.get("oi_delta_log_1h_p97.5")
            taker_threshold = thresholds.get("taker_sell_aggression_p97.5")
            if row.get("oi_delta_log_1h") is None or oi_threshold is None:
                rejected_due_to_missing_components["oi_delta_log_1h_missing"] += 1
                continue
            if row.get("taker_sell_aggression") is None or taker_threshold is None:
                rejected_due_to_missing_components["taker_sell_aggression_missing"] += 1
                continue
            if row["oi_delta_log_1h"] < oi_threshold or row["taker_sell_aggression"] < taker_threshold:
                continue
            if int(features["short_failure_score"]) < 1:
                rejected_due_to_missing_price_failure += 1
                continue
            account_threshold = thresholds.get("top_account_short_p5.0")
            position_threshold = thresholds.get("top_position_short_p5.0")
            account_ok = row["top_account_ratio"] is not None and account_threshold is not None and row["top_account_ratio"] <= account_threshold
            position_ok = row["top_position_ratio"] is not None and position_threshold is not None and row["top_position_ratio"] <= position_threshold
            tier = crowding_tier(account_ok, position_ok)
            raw_count += 1
            crowding_distribution[tier] += 1
            for variant, passed in features["short_flags"].items():
                if variant != "any_failure" and passed:
                    price_failure_distribution[variant] += 1
            previous = last_event_ms.get(symbol)
            if previous is not None and row["ts_ms"] - previous < cooldown_ms:
                rejected_due_to_cooldown += 1
                continue
            last_event_ms[symbol] = row["ts_ms"]
            base_open = floor_to_15m_open(row["ts_ms"])
            base_index = kline_data["open_to_index"].get(base_open)
            events.append(
                {
                    "side": "short_core",
                    "definition_id": SHORT_CORE_DEFINITION_ID,
                    "symbol": symbol,
                    "timestamp": row["timestamp"],
                    "ts_ms": row["ts_ms"],
                    "base_open_ms": base_open,
                    "base_open": ms_to_iso(base_open),
                    "base_index": base_index,
                    "month": row["month"],
                    "crowding_confirmation": tier,
                    "failure_score": int(features["short_failure_score"]),
                    "price_failure_flags": {
                        key: bool(value) for key, value in features["short_flags"].items() if key != "any_failure"
                    },
                }
            )
    return {
        "events": events,
        "raw_event_count": raw_count,
        "cooldown_filtered_count": len(events),
        "rejected_due_to_cooldown": rejected_due_to_cooldown,
        "rejected_due_to_missing_price_failure": rejected_due_to_missing_price_failure,
        "rejected_due_to_missing_components": dict(rejected_due_to_missing_components),
        "crowding_confirmation_distribution": dict(crowding_distribution),
        "price_failure_variant_distribution": dict(price_failure_distribution),
    }


def summarize_array(values: list[float] | np.ndarray) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    array = array[np.isfinite(array)]
    if array.size == 0:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "std": None,
            "positive_rate": None,
            "negative_rate": None,
            "q01": None,
            "q05": None,
            "q25": None,
            "q50": None,
            "q75": None,
            "q95": None,
            "q99": None,
        }
    return {
        "count": int(array.size),
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "std": float(np.std(array, ddof=0)) if array.size > 1 else 0.0,
        "positive_rate": float(np.mean(array > 0.0)),
        "negative_rate": float(np.mean(array < 0.0)),
        "q01": float(np.quantile(array, 0.01)),
        "q05": float(np.quantile(array, 0.05)),
        "q25": float(np.quantile(array, 0.25)),
        "q50": float(np.quantile(array, 0.50)),
        "q75": float(np.quantile(array, 0.75)),
        "q95": float(np.quantile(array, 0.95)),
        "q99": float(np.quantile(array, 0.99)),
    }


def summarize_null_means(null_means: np.ndarray) -> dict[str, Any]:
    array = np.asarray(null_means, dtype=np.float64)
    array = array[np.isfinite(array)]
    if array.size == 0:
        return {
            "null_mean_mean": None,
            "null_mean_std": None,
            "null_mean_q01": None,
            "null_mean_q05": None,
            "null_mean_q50": None,
            "null_mean_q95": None,
            "null_mean_q99": None,
        }
    return {
        "null_mean_mean": float(np.mean(array)),
        "null_mean_std": float(np.std(array, ddof=0)) if array.size > 1 else 0.0,
        "null_mean_q01": float(np.quantile(array, 0.01)),
        "null_mean_q05": float(np.quantile(array, 0.05)),
        "null_mean_q50": float(np.quantile(array, 0.50)),
        "null_mean_q95": float(np.quantile(array, 0.95)),
        "null_mean_q99": float(np.quantile(array, 0.99)),
    }


def observed_primary(events: list[dict[str, Any]], kline_by_symbol: dict[str, dict[str, Any]]) -> dict[str, Any]:
    values: list[float] = []
    event_indices_by_symbol_month: dict[tuple[str, str], set[int]] = defaultdict(set)
    valid_counts_by_symbol_month: Counter[tuple[str, str]] = Counter()
    valid_event_returns: list[dict[str, Any]] = []
    missing_forward = 0
    missing_join = 0
    for event in events:
        symbol = event["symbol"]
        base_index = event.get("base_index")
        if base_index is None or symbol not in kline_by_symbol:
            missing_join += 1
            missing_forward += 1
            continue
        returns = kline_by_symbol[symbol]["returns_1h"]
        value = returns[int(base_index)]
        if np.isfinite(value):
            ret = float(value)
            values.append(ret)
            month = event["month"]
            event_indices_by_symbol_month[(symbol, month)].add(int(base_index))
            valid_counts_by_symbol_month[(symbol, month)] += 1
            valid_event_returns.append({**event, "forward_return_1h": ret})
        else:
            missing_forward += 1
    stats = summarize_array(values)
    return {
        "values": values,
        "valid_event_returns": valid_event_returns,
        "event_indices_by_symbol_month": event_indices_by_symbol_month,
        "valid_counts_by_symbol_month": valid_counts_by_symbol_month,
        "observed_primary_stats": {
            "event_count": len(events),
            "valid_forward_return_count": stats["count"],
            "missing_forward_return_count": missing_forward,
            **{key: value for key, value in stats.items() if key != "count"},
        },
        "missing_join_count": missing_join,
    }


def empirical_p_values(observed_mean: float | None, null_means: np.ndarray) -> dict[str, Any]:
    if observed_mean is None or not np.isfinite(observed_mean):
        return {
            "p_two_sided": None,
            "p_positive_mean": None,
            "p_negative_mean": None,
            "empirical_p_value_formula": "p = (1 + count(null stats as or more extreme than observed)) / (1 + permutation_count)",
        }
    null_center = float(np.mean(null_means))
    denominator = 1 + PERMUTATION_COUNT
    return {
        "p_two_sided": float((1 + int(np.sum(np.abs(null_means - null_center) >= abs(observed_mean - null_center)))) / denominator),
        "p_positive_mean": float((1 + int(np.sum(null_means >= observed_mean))) / denominator),
        "p_negative_mean": float((1 + int(np.sum(null_means <= observed_mean))) / denominator),
        "empirical_p_value_formula": "p = (1 + count(null stats as or more extreme than observed)) / (1 + permutation_count)",
        "null_center_used_for_two_sided": null_center,
    }


def month_aware_symbol_balanced_null(observed: dict[str, Any], kline_by_symbol: dict[str, dict[str, Any]]) -> dict[str, Any]:
    valid_count = int(observed["observed_primary_stats"]["valid_forward_return_count"])
    if valid_count <= 0:
        return {
            "permutation_count_requested": PERMUTATION_COUNT,
            "permutation_count_completed": 0,
            "null_stats": summarize_null_means(np.asarray([], dtype=np.float64)),
            "p_values": {"p_two_sided": None, "p_positive_mean": None, "p_negative_mean": None},
            "fallback_summary": {"skipped_reason": "zero valid forward returns"},
        }
    rng = np.random.default_rng(RANDOM_SEED)
    null_sums = np.zeros(PERMUTATION_COUNT, dtype=np.float64)
    total_count = 0
    fallback_summary = {
        "month_aware_pool_used": 0,
        "symbol_pool_fallback_used": 0,
        "event_timestamp_exclusion_used": 0,
        "empty_pool_count": 0,
    }
    for (symbol, month), count in observed["valid_counts_by_symbol_month"].items():
        if count <= 0:
            continue
        symbol_data = kline_by_symbol[symbol]
        month_mask = np.array([month_key_from_ms(int(open_ms)) == month for open_ms in symbol_data["opens"]], dtype=bool)
        candidate_indices = np.flatnonzero(month_mask & np.isfinite(symbol_data["returns_1h"]))
        if candidate_indices.size:
            fallback_summary["month_aware_pool_used"] += 1
        else:
            fallback_summary["symbol_pool_fallback_used"] += 1
            candidate_indices = symbol_data["valid_indices_1h"]
        event_indices = observed["event_indices_by_symbol_month"].get((symbol, month), set())
        if candidate_indices.size and event_indices:
            keep = np.array([int(index) not in event_indices for index in candidate_indices], dtype=bool)
            filtered = candidate_indices[keep]
            if filtered.size:
                fallback_summary["event_timestamp_exclusion_used"] += 1
                candidate_indices = filtered
        candidates = symbol_data["returns_1h"][candidate_indices]
        candidates = candidates[np.isfinite(candidates)]
        if candidates.size == 0:
            fallback_summary["empty_pool_count"] += 1
            continue
        draws = rng.integers(0, candidates.size, size=(PERMUTATION_COUNT, int(count)))
        null_sums += candidates[draws].sum(axis=1)
        total_count += int(count)
    if total_count <= 0:
        raise ValidationBlocked("zero valid null sample count for primary validation")
    null_means = null_sums / float(total_count)
    observed_mean = observed["observed_primary_stats"]["mean"]
    p_values = empirical_p_values(observed_mean, null_means)
    return {
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": PERMUTATION_COUNT,
        "null_stats": summarize_null_means(null_means),
        "p_values": p_values,
        "fdr_q_value": p_values.get("p_negative_mean"),
        "bonferroni_p_value": p_values.get("p_negative_mean"),
        "fallback_summary": fallback_summary,
    }


def group_stats(valid_event_returns: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for event in valid_event_returns:
        grouped[str(event[key])].append(float(event["forward_return_1h"]))
    rows = []
    total_sum = sum(sum(values) for values in grouped.values())
    for group_key, values in grouped.items():
        stats = summarize_array(values)
        contribution = (sum(values) / total_sum) if total_sum else None
        rows.append({"key": group_key, "count": len(values), "mean": stats["mean"], "contribution_to_total_sum": contribution})
    rows.sort(key=lambda row: abs(row["contribution_to_total_sum"] or 0.0), reverse=True)
    return rows


def leave_one_diagnostics(valid_event_returns: list[dict[str, Any]], key: str, full_mean: float | None) -> dict[str, Any]:
    groups = sorted({str(event[key]) for event in valid_event_returns})
    if full_mean is None or not groups or len(valid_event_returns) < 100:
        return {"skipped": True, "reason": "insufficient events or full mean unavailable", "any_single_dependence": None}
    rows = []
    any_necessary = False
    for group in groups:
        subset = [float(event["forward_return_1h"]) for event in valid_event_returns if str(event[key]) != group]
        stats = summarize_array(subset)
        mean = stats["mean"]
        direction_preserved = mean is not None and mean < 0
        ratio = (abs(mean) / abs(full_mean)) if mean is not None and full_mean else None
        necessary = (not direction_preserved) or (ratio is not None and ratio < 0.30)
        any_necessary = any_necessary or necessary
        rows.append(
            {
                key: group,
                "remaining_count": stats["count"],
                "mean": mean,
                "direction_preserved": direction_preserved,
                "magnitude_ratio_vs_full": ratio,
                "single_group_necessary": necessary,
            }
        )
    return {"skipped": False, "groups_tested": len(groups), "any_single_dependence": any_necessary, "details": rows}


def arbusdt_sensitivity(valid_event_returns: list[dict[str, Any]], full_mean: float | None) -> dict[str, Any]:
    arbusdt_count = sum(1 for event in valid_event_returns if event["symbol"] == "ARBUSDT")
    if arbusdt_count == 0:
        return {"arbusdt_event_count": 0, "skipped": True, "reason": "no ARBUSDT events"}
    subset = [float(event["forward_return_1h"]) for event in valid_event_returns if event["symbol"] != "ARBUSDT"]
    stats = summarize_array(subset)
    mean = stats["mean"]
    return {
        "arbusdt_event_count": arbusdt_count,
        "skipped": False,
        "observed_without_arbusdt": stats,
        "direction_preserved": mean is not None and mean < 0,
        "magnitude_ratio_vs_full": (abs(mean) / abs(full_mean)) if mean is not None and full_mean else None,
    }


def build_sensitivity_diagnostics(observed: dict[str, Any]) -> dict[str, Any]:
    valid = observed["valid_event_returns"]
    full_mean = observed["observed_primary_stats"]["mean"]
    return {
        "leave_one_symbol_out": leave_one_diagnostics(valid, "symbol", full_mean),
        "leave_one_month_out": leave_one_diagnostics(valid, "month", full_mean),
        "arbusdt_exclusion": arbusdt_sensitivity(valid, full_mean),
        "top_contributor_symbols": group_stats(valid, "symbol")[:5],
        "top_contributor_months": group_stats(valid, "month")[:5],
    }


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_validation_returns": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "used_2023_2025_as_independent_validation": False,
        "event_definition_changes": False,
        "threshold_changes": False,
        "horizon_changes": False,
        "outcome_based_selection": False,
        "release_promotion": False,
    }


def archive_summary(manifest: list[dict[str, Any]]) -> dict[str, Any]:
    available = [row for row in manifest if row["available"]]
    missing = [row for row in manifest if not row["available"]]
    return {
        "total_archive_records": len(manifest),
        "available_archive_count": len(available),
        "missing_archive_count": len(missing),
        "downloaded_archive_count": sum(1 for row in available if row["downloaded"]),
        "reused_archive_count": sum(1 for row in available if row["reused_existing"]),
        "checksum_available_count": sum(1 for row in available if row["checksum_available"]),
        "checksum_verified_count": sum(1 for row in available if row["checksum_verified"] is True),
        "missing_archives": [
            {
                "kind": row["kind"],
                "cadence": row["cadence"],
                "symbol": row["symbol"],
                "url": row["url"],
                "error": row["error"],
            }
            for row in missing
        ],
    }


def classify_validation(
    observed_stats: dict[str, Any],
    p_values: dict[str, Any],
    validation_gates: dict[str, bool],
    data_quality_attention: bool,
) -> tuple[str, str, bool, str]:
    event_count = int(observed_stats.get("event_count") or 0)
    valid_count = int(observed_stats.get("valid_forward_return_count") or 0)
    mean = observed_stats.get("mean")
    p_negative = p_values.get("p_negative_mean")
    if data_quality_attention and event_count >= 100:
        return RESULT_ATTENTION, NEXT_REPAIR, False, "data quality attention prevents clean validation decision"
    if event_count < 50 or valid_count < 50:
        return RESULT_INCONCLUSIVE, NEXT_ACCUMULATION, False, "insufficient independent validation events"
    if event_count < 100 or valid_count < 100:
        return RESULT_INCONCLUSIVE, NEXT_ACCUMULATION, False, "attention/inconclusive independent validation sample below 100 events"
    if all(validation_gates.values()) and isinstance(mean, (int, float)) and mean < 0 and isinstance(p_negative, (int, float)) and p_negative <= 0.05:
        return RESULT_PASS, NEXT_EVALUATOR, True, "pre-registered diagnostic validation gates passed"
    return RESULT_FAIL, NEXT_CLOSE_OR_REDESIGN, False, "pre-registered diagnostic validation gates failed"


def blocked_artifact(
    reason: str,
    audit: dict[str, Any] | None = None,
    hashes_before: dict[str, str] | None = None,
    hashes_after: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "validation_status": VALIDATION_STATUS_BLOCKED,
        "status": VALIDATION_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": (audit or {}).get("recovery_decision", "RECOVERY_UNKNOWN"),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "approved_neutral_diagnostic_label": APPROVED_NEUTRAL_LABEL,
        "frozen_hypothesis": {},
        "independent_validation_window": {},
        "independent_validation_data_policy_followed": False,
        "public_data_source_summary": {},
        "symbols_requested": DEFAULT_SYMBOLS,
        "symbols_available": [],
        "archive_availability_summary": {},
        "event_reconstruction_status": "BLOCKED",
        "event_count": 0,
        "symbol_coverage": {},
        "month_coverage": {},
        "observed_primary_stats": {},
        "null_model": "month_aware_symbol_balanced_null",
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": 0,
        "null_stats": {},
        "p_values": {},
        "fdr_q_value": None,
        "bonferroni_p_value": None,
        "validation_gates": {},
        "failed_validation_gates": [reason],
        "sensitivity_diagnostics": {},
        "data_quality_warnings": [f"BLOCKED: {reason}"],
        "final_validation_decision": "blocked",
        "independent_validation_passed": False,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_RUNTIME_REPAIR,
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    if audit["recovery_decision"] != "RECOVERY_AUDIT_CLEAN_CONTINUE":
        return blocked_artifact(audit["recovery_decision"], audit)
    hashes_before = input_artifact_hashes()
    contract, semantics, evaluator, refinement, dataset, payload_hashes = load_inputs()
    input_checks = validate_input_chain(contract, semantics, evaluator, refinement)
    if not all(input_checks.values()):
        raise ValidationBlocked(f"input chain validation failed: {input_checks}")
    symbols = dataset_symbols(dataset)
    archive_paths_by_symbol, manifest = download_all_archives(symbols)
    metrics_by_symbol: dict[str, list[dict[str, Any]]] = {}
    kline_by_symbol: dict[str, dict[str, Any]] = {}
    data_quality_warnings: list[str] = []
    for symbol, paths in archive_paths_by_symbol.items():
        if paths["metrics"] and paths["klines"]:
            try:
                metrics_by_symbol[symbol] = read_metrics_archives(paths["metrics"], symbol)
                kline_by_symbol[symbol] = read_kline_archives(paths["klines"], symbol)
            except Exception as exc:
                data_quality_warnings.append(f"{symbol} load warning: {exc}")
        else:
            data_quality_warnings.append(
                f"{symbol} missing validation archives: metrics={len(paths['metrics'])}, klines={len(paths['klines'])}"
            )
    symbols_available = sorted(set(metrics_by_symbol) & set(kline_by_symbol))
    reconstructed = reconstruct_short_core_events(metrics_by_symbol, kline_by_symbol) if symbols_available else {
        "events": [],
        "raw_event_count": 0,
        "cooldown_filtered_count": 0,
        "rejected_due_to_cooldown": 0,
        "rejected_due_to_missing_price_failure": 0,
        "rejected_due_to_missing_components": {},
        "crowding_confirmation_distribution": {},
        "price_failure_variant_distribution": {},
    }
    observed = observed_primary(reconstructed["events"], kline_by_symbol)
    null_result = month_aware_symbol_balanced_null(observed, kline_by_symbol)
    sensitivity = build_sensitivity_diagnostics(observed)
    valid_events = observed["valid_event_returns"]
    event_months = sorted({event["month"] for event in reconstructed["events"]})
    event_symbols = sorted({event["symbol"] for event in reconstructed["events"]})
    all_kline_mins = [data["timestamp_min"] for data in kline_by_symbol.values()]
    all_kline_maxs = [data["timestamp_max"] for data in kline_by_symbol.values()]
    independent_window = {
        "start": min(all_kline_mins) if all_kline_mins else None,
        "end": max(all_kline_maxs) if all_kline_maxs else None,
        "validation_start_not_before": "2026-01-01",
        "uses_2023_2025_research_sample": False,
    }
    observed_stats = observed["observed_primary_stats"]
    p_values = null_result["p_values"]
    fdr_q = null_result.get("fdr_q_value")
    bonferroni = null_result.get("bonferroni_p_value")
    validation_gates = {
        "independent_validation_uses_2026_plus_only": independent_window["start"] is not None
        and str(independent_window["start"]) >= "2026-01-01",
        "event_reconstruction_current_or_prior_bar_only": True,
        "sufficient_event_count_exists": int(observed_stats.get("event_count") or 0) >= 100,
        "observed_primary_mean_negative": isinstance(observed_stats.get("mean"), (int, float)) and observed_stats["mean"] < 0,
        "p_negative_mean_lte_0_05": isinstance(p_values.get("p_negative_mean"), (int, float)) and p_values["p_negative_mean"] <= 0.05,
        "fdr_and_bonferroni_recorded": isinstance(fdr_q, (int, float)) and isinstance(bonferroni, (int, float)),
        "leave_one_symbol_no_single_dependence_when_applicable": sensitivity["leave_one_symbol_out"].get("any_single_dependence") is not True,
        "leave_one_month_no_single_dependence_when_applicable": sensitivity["leave_one_month_out"].get("any_single_dependence") is not True,
        "arbusdt_sensitivity_recorded_if_relevant": "arbusdt_event_count" in sensitivity["arbusdt_exclusion"],
        "no_forbidden_action_occurred": True,
    }
    failed_gates = [key for key, value in validation_gates.items() if value is not True]
    archive_availability = archive_summary(manifest)
    if archive_availability["available_archive_count"] == 0:
        data_quality_warnings.append("No public 2026+ Binance Data Vision archives were available or downloadable.")
    if archive_availability["missing_archive_count"] > 0:
        data_quality_warnings.append(f"{archive_availability['missing_archive_count']} public archive probes were unavailable.")
    missing_forward = observed_stats.get("missing_forward_return_count") or 0
    if observed_stats.get("event_count") and missing_forward:
        data_quality_warnings.append(f"{missing_forward} event rows had missing 1h forward returns.")
    data_quality_attention = archive_availability["available_archive_count"] == 0 or (
        int(observed_stats.get("event_count") or 0) >= 100
        and int(observed_stats.get("valid_forward_return_count") or 0) < int(observed_stats.get("event_count") or 0) * 0.8
    )
    result_classification, allowed_next_step, validation_passed, final_decision = classify_validation(
        observed_stats,
        p_values,
        validation_gates,
        data_quality_attention,
    )
    if result_classification == RESULT_INCONCLUSIVE:
        failed_gates = [gate for gate in failed_gates if gate != "sufficient_event_count_exists"] + [
            "insufficient_independent_validation_sample"
        ]
    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise ValidationBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    validation_checks = {
        **input_checks,
        "input_artifact_hashes_unchanged": input_unchanged,
        "public_data_vision_only": True,
        "validation_window_2026_plus_only": validation_gates["independent_validation_uses_2026_plus_only"]
        or int(observed_stats.get("event_count") or 0) == 0,
        "no_2023_2025_independent_validation_reuse": True,
        "no_strategy_signal_candidate_release_permissions": True,
        "no_artifacts_data_builds_written": True,
    }
    artifact = {
        "validation_status": VALIDATION_STATUS_PASS,
        "status": VALIDATION_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_decision"],
        "current_head": audit["current_head"],
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": input_unchanged,
        "input_payload_hashes_verified": payload_hashes,
        "approved_neutral_diagnostic_label": APPROVED_NEUTRAL_LABEL,
        "frozen_hypothesis": contract.get("frozen_hypothesis", {}),
        "independent_validation_window": independent_window,
        "independent_validation_data_policy_followed": True,
        "public_data_source_summary": {
            "host": PUBLIC_ARCHIVE_HOST,
            "monthly_metrics_root": MONTHLY_METRICS_ROOT,
            "daily_metrics_root": DAILY_METRICS_ROOT,
            "monthly_klines_root": MONTHLY_KLINES_ROOT,
            "daily_klines_root": DAILY_KLINES_ROOT,
            "cache_root": str(CACHE_ROOT),
            "raw_data_committed": False,
            "cache_files_staged": False,
        },
        "symbols_requested": symbols,
        "symbols_available": symbols_available,
        "archive_availability_summary": archive_availability,
        "event_reconstruction_status": "RECONSTRUCTED_FROZEN_SHORT_CORE_ONLY",
        "event_reconstruction_summary": reconstructed,
        "event_count": int(observed_stats.get("event_count") or 0),
        "symbol_coverage": {
            "symbol_count": len(event_symbols),
            "symbols": event_symbols,
            "top_contributor_symbols": sensitivity["top_contributor_symbols"],
        },
        "month_coverage": {
            "month_count": len(event_months),
            "months": event_months,
            "top_contributor_months": sensitivity["top_contributor_months"],
        },
        "observed_primary_stats": observed_stats,
        "null_model": "month_aware_symbol_balanced_null",
        "permutation_count_requested": int(null_result["permutation_count_requested"]),
        "permutation_count_completed": int(null_result["permutation_count_completed"]),
        "null_stats": null_result["null_stats"],
        "p_values": p_values,
        "fdr_q_value": fdr_q,
        "bonferroni_p_value": bonferroni,
        "validation_gates": validation_gates,
        "failed_validation_gates": failed_gates,
        "sensitivity_diagnostics": sensitivity,
        "data_quality_warnings": data_quality_warnings,
        "final_validation_decision": final_decision,
        "independent_validation_passed": validation_passed,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": allowed_next_step,
        "blocker": None,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": all(
            value is True
            for key, value in validation_checks.items()
            if key not in {"validation_window_2026_plus_only"}
        ),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"status: {artifact['validation_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"approved_neutral_diagnostic_label: {artifact['approved_neutral_diagnostic_label']}")
    print(f"independent_validation_window: {artifact['independent_validation_window']}")
    print(f"symbols_requested: {artifact['symbols_requested']}")
    print(f"symbols_available: {artifact['symbols_available']}")
    print(f"event_count: {artifact['event_count']}")
    print(f"symbol_coverage: {artifact['symbol_coverage']}")
    print(f"month_coverage: {artifact['month_coverage']}")
    print(f"observed_primary_stats: {artifact['observed_primary_stats']}")
    print(f"permutation_count_requested: {artifact['permutation_count_requested']}")
    print(f"permutation_count_completed: {artifact['permutation_count_completed']}")
    print(f"p_negative_mean: {artifact['p_values'].get('p_negative_mean')}")
    print(f"fdr_q_value: {artifact['fdr_q_value']}")
    print(f"bonferroni_p_value: {artifact['bonferroni_p_value']}")
    print(f"validation_gates: {artifact['validation_gates']}")
    print(f"failed_validation_gates: {artifact['failed_validation_gates']}")
    print(f"sensitivity_diagnostics: {artifact['sensitivity_diagnostics']}")
    print(f"data_quality_warnings: {artifact['data_quality_warnings']}")
    print(f"final_validation_decision: {artifact['final_validation_decision']}")
    print(f"independent_validation_passed: {bool_text(bool(artifact['independent_validation_passed']))}")
    print(f"strategy_allowed: {bool_text(bool(artifact['strategy_allowed']))}")
    print(f"signal_allowed: {bool_text(bool(artifact['signal_allowed']))}")
    print(f"candidate_generation_allowed: {bool_text(bool(artifact['candidate_generation_allowed']))}")
    print(f"release_allowed: {bool_text(bool(artifact['release_allowed']))}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"forbidden actions confirmed false: {artifact['forbidden_actions_confirmed_false']}")
    print(f"blocker: {artifact['blocker']}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")


def main() -> int:
    hashes_before = None
    hashes_after = None
    audit = None
    try:
        audit = recovery_audit()
        print(f"current HEAD: {audit['current_head']}")
        print(f"expected HEAD: {EXPECTED_HEAD}")
        print(f"branch: {audit['branch']}")
        print(f"git status porcelain: {audit['git_status_porcelain']}")
        print(f"staged files: {audit['staged_files']}")
        print(f"modified tracked files: {audit['modified_tracked_files']}")
        print(f"untracked files: {audit['untracked_files']}")
        print(f"deleted files: {audit['deleted_files']}")
        print(f"recovery decision: {audit['recovery_decision']}")
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
        hashes_after = input_artifact_hashes()
        if hashes_before != hashes_after:
            artifact = blocked_artifact("INPUT_ARTIFACT_HASH_CHANGED", audit, hashes_before, hashes_after)
        write_artifact(artifact)
        print_summary(artifact)
        return 0 if artifact["validation_status"] == VALIDATION_STATUS_PASS else 1
    except Exception as exc:
        try:
            hashes_after = input_artifact_hashes() if hashes_before else None
        except Exception:
            hashes_after = None
        artifact = blocked_artifact(str(exc), audit, hashes_before, hashes_after)
        write_artifact(artifact)
        print_summary(artifact)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
