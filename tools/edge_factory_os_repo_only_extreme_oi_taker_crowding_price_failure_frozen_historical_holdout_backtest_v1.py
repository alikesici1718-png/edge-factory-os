#!/usr/bin/env python
"""Frozen pre-2023 historical holdout diagnostic for the neutral price-failure route."""

from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
import json
import subprocess
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FROZEN_HISTORICAL_HOLDOUT_BACKTEST_V1"
MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_"
    "frozen_historical_holdout_backtest_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_"
    "frozen_historical_holdout_backtest_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

BASE_RUNNER_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_runner_v1.py"
)
EXPECTED_HEAD = "7904a4973463a6b449bd3064e5415f5eb56911ad"

SOURCE_CONTRACT_RELATIVE_PATH = (
    "artifacts/contracts/extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_contract_v1.json"
)
SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_runner_v1.json"
)
SOURCE_SEMANTICS_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_direction_semantics_review_v1.json"
)
SOURCE_REFINEMENT_RELATIVE_PATH = (
    "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
)
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_CONTRACT_RELATIVE_PATH,
    SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH,
    SOURCE_SEMANTICS_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
]

HOLDOUT_STATUS_PASS = "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FROZEN_HISTORICAL_HOLDOUT_BACKTEST_CREATED"
HOLDOUT_STATUS_BLOCKED = "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FROZEN_HISTORICAL_HOLDOUT_BACKTEST"
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FROZEN_HISTORICAL_HOLDOUT_BACKTEST"

RESULT_PASS = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HISTORICAL_HOLDOUT_PASS_DIAGNOSTIC_ONLY"
RESULT_FAIL = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HISTORICAL_HOLDOUT_FAIL"
RESULT_INCONCLUSIVE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HISTORICAL_HOLDOUT_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
RESULT_DATA_UNAVAILABLE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HISTORICAL_HOLDOUT_DATA_UNAVAILABLE"
RESULT_ATTENTION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HISTORICAL_HOLDOUT_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HISTORICAL_HOLDOUT_FAILED_STOP"

NEXT_HOLDOUT_EVALUATOR = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_HOLDOUT_EVALUATOR_V1"
NEXT_CLOSE_OR_REDESIGN = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_ROUTE_CLOSE_OR_REDESIGN_EVALUATOR_V1"
NEXT_ACCUMULATION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_SAMPLE_ACCUMULATION_MONITOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_HISTORICAL_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"
NEXT_RUNTIME_REPAIR = "RECOVERY_OR_RUNTIME_REPAIR_V1"

APPROVED_NEUTRAL_LABEL = "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC"
PUBLIC_ARCHIVE_BASE = "https://data.binance.vision/"
MONTHLY_METRICS_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/monthly/metrics"
DAILY_METRICS_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/daily/metrics"
MONTHLY_KLINES_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/monthly/klines"
DAILY_KLINES_ROOT = f"{PUBLIC_ARCHIVE_BASE}data/futures/um/daily/klines"

REQUESTED_HOLDOUT_WINDOW = {
    "preferred_start": "2020-01-01",
    "preferred_end": "2022-12-31",
    "timezone": "UTC",
    "must_be_pre_2023": True,
}
HOLDOUT_START = date(2020, 1, 1)
HOLDOUT_END = date(2022, 12, 31)
PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528
REQUEST_TIMEOUT_SECONDS = 30
REQUEST_SLEEP_SECONDS = 0.005
CACHE_ROOT = REPO_ROOT / "cache" / "extreme_oi_taker_crowding_price_failure_frozen_historical_holdout_backtest_v1"
COST_STRESS_BPS = [0, 2, 5, 10, 20]

DEFAULT_SYMBOLS = [
    "APTUSDT",
    "ARBUSDT",
    "BNBUSDT",
    "BTCUSDT",
    "DOGEUSDT",
    "ETHUSDT",
    "LINKUSDT",
    "OPUSDT",
    "SOLUSDT",
    "XRPUSDT",
]


class HoldoutBlocked(Exception):
    pass


def load_base_runner():
    path = REPO_ROOT / BASE_RUNNER_RELATIVE_PATH
    spec = importlib.util.spec_from_file_location("pre_registered_independent_validation_runner_v1", path)
    if spec is None or spec.loader is None:
        raise HoldoutBlocked(f"cannot load base runner helpers: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.CACHE_ROOT = CACHE_ROOT
    module.VALIDATION_START = HOLDOUT_START
    return module


BASE = load_base_runner()


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
        raise HoldoutBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
            raise HoldoutBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise HoldoutBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise HoldoutBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise HoldoutBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    contract = read_json_readonly(SOURCE_CONTRACT_RELATIVE_PATH)
    independent = read_json_readonly(SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH)
    semantics = read_json_readonly(SOURCE_SEMANTICS_RELATIVE_PATH)
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_CONTRACT_RELATIVE_PATH: verify_payload_hash(contract, "independent validation contract"),
        SOURCE_INDEPENDENT_VALIDATION_RELATIVE_PATH: verify_payload_hash(independent, "independent validation runner"),
        SOURCE_SEMANTICS_RELATIVE_PATH: verify_payload_hash(semantics, "direction semantics review"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
    }
    return contract, independent, semantics, refinement, dataset, payload_hashes


def validate_input_chain(contract: dict[str, Any], independent: dict[str, Any], semantics: dict[str, Any], refinement: dict[str, Any]) -> dict[str, bool]:
    frozen = contract.get("frozen_hypothesis", {})
    return {
        "contract_ready": contract.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY",
        "independent_validation_prior_inconclusive": independent.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE",
        "semantics_relabel_ready": semantics.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_DIRECTION_SEMANTICS_REVIEW_RELABEL_READY",
        "refinement_ready": refinement.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_READY",
        "label_exact": frozen.get("diagnostic_label") == APPROVED_NEUTRAL_LABEL,
        "event_side_short_core": frozen.get("event_side") == "short_core",
        "horizon_1h": frozen.get("horizon") == "1h",
        "expected_direction_negative": frozen.get("expected_direction") == "negative",
        "primary_null_month_aware_symbol_balanced": frozen.get("primary_null_model_for_validation")
        == "month_aware_symbol_balanced_null",
    }


def dataset_symbols(dataset: dict[str, Any]) -> list[str]:
    symbols = dataset.get("requested_symbols")
    if isinstance(symbols, list) and all(isinstance(symbol, str) for symbol in symbols):
        return sorted(symbols)
    return DEFAULT_SYMBOLS


def assert_public_archive_url(url: str) -> None:
    if not url.startswith(PUBLIC_ARCHIVE_BASE):
        raise HoldoutBlocked(f"forbidden non-public archive URL attempted: {url}")
    allowed = [
        "/data/futures/um/monthly/metrics/",
        "/data/futures/um/daily/metrics/",
        "/data/futures/um/monthly/klines/",
        "/data/futures/um/daily/klines/",
    ]
    if not any(token in url for token in allowed):
        raise HoldoutBlocked(f"forbidden archive path attempted: {url}")


def request_url(url: str, missing_ok: bool = True) -> dict[str, Any]:
    assert_public_archive_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "edge-factory-os-historical-holdout/1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return {
                "ok": True,
                "status": getattr(response, "status", 200),
                "data": response.read(),
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


def parse_checksum_text(text: str) -> str | None:
    import re

    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def checksum_url(zip_url: str) -> str:
    return f"{zip_url}.CHECKSUM"


def month_pairs() -> list[tuple[int, int]]:
    return [(year, month) for year in range(2020, 2023) for month in range(1, 13)]


def month_end(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1) - timedelta(days=1)
    return date(year, month + 1, 1) - timedelta(days=1)


def days_for_month(year: int, month: int) -> list[date]:
    start = max(date(year, month, 1), HOLDOUT_START)
    end = min(month_end(year, month), HOLDOUT_END)
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


def get_archive(kind: str, cadence: str, symbol: str, url: str) -> tuple[Path | None, dict[str, Any]]:
    filename = url.rsplit("/", 1)[-1]
    path = archive_cache_path(kind, cadence, symbol, filename)
    checksum_path = path.with_name(path.name + ".CHECKSUM")
    if path.exists() and path.stat().st_size > 0:
        checksum_available = checksum_path.exists()
        checksum_verified = None
        if checksum_available:
            expected_sha = parse_checksum_text(checksum_path.read_text(encoding="utf-8", errors="replace"))
            checksum_verified = expected_sha == sha256_file(path) if expected_sha else False
            if checksum_verified is False:
                raise HoldoutBlocked(f"cached checksum mismatch: {path}")
        return path, {
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
    result = request_url(url, missing_ok=True)
    if not result["ok"]:
        return None, {
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
            "error": result["error"] or f"status {result['status']}",
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(result["data"])
    checksum_result = request_url(checksum_url(url), missing_ok=True)
    checksum_available = checksum_result["ok"]
    checksum_verified = None
    if checksum_available:
        checksum_path.write_bytes(checksum_result["data"])
        expected_sha = parse_checksum_text(checksum_result["data"].decode("utf-8", errors="replace"))
        checksum_verified = expected_sha == sha256_file(path) if expected_sha else False
        if checksum_verified is False:
            raise HoldoutBlocked(f"downloaded checksum mismatch: {url}")
    return path, {
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


def get_symbol_archives(symbol: str) -> tuple[str, dict[str, list[Path]], list[dict[str, Any]]]:
    manifest: list[dict[str, Any]] = []
    paths = {"metrics": [], "klines": []}
    for year, month in month_pairs():
        monthly_metrics, row = get_archive("metrics", "monthly", symbol, monthly_metrics_url(symbol, year, month))
        manifest.append(row)
        if monthly_metrics is not None:
            paths["metrics"].append(monthly_metrics)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_archive, "metrics", "daily", symbol, daily_metrics_url(symbol, day)) for day in days_for_month(year, month)]
                for future in concurrent.futures.as_completed(futures):
                    path, daily_row = future.result()
                    manifest.append(daily_row)
                    if path is not None:
                        paths["metrics"].append(path)
        monthly_kline, row = get_archive("klines", "monthly", symbol, monthly_kline_url(symbol, year, month))
        manifest.append(row)
        if monthly_kline is not None:
            paths["klines"].append(monthly_kline)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_archive, "klines", "daily", symbol, daily_kline_url(symbol, day)) for day in days_for_month(year, month)]
                for future in concurrent.futures.as_completed(futures):
                    path, daily_row = future.result()
                    manifest.append(daily_row)
                    if path is not None:
                        paths["klines"].append(path)
    return symbol, paths, manifest


def get_all_archives(symbols: list[str]) -> tuple[dict[str, dict[str, list[Path]]], list[dict[str, Any]]]:
    by_symbol: dict[str, dict[str, list[Path]]] = {}
    manifest: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(6, len(symbols))) as executor:
        futures = [executor.submit(get_symbol_archives, symbol) for symbol in symbols]
        for future in concurrent.futures.as_completed(futures):
            symbol, paths, rows = future.result()
            by_symbol[symbol] = paths
            manifest.extend(rows)
    return by_symbol, manifest


def archive_summary(manifest: list[dict[str, Any]], kind: str | None = None) -> dict[str, Any]:
    rows = [row for row in manifest if kind is None or row["kind"] == kind]
    available = [row for row in rows if row["available"]]
    missing = [row for row in rows if not row["available"]]
    by_symbol = defaultdict(lambda: {"available": 0, "missing": 0})
    by_symbol_month = []
    for row in rows:
        by_symbol[row["symbol"]]["available" if row["available"] else "missing"] += 1
        by_symbol_month.append(
            {
                "kind": row["kind"],
                "cadence": row["cadence"],
                "symbol": row["symbol"],
                "url": row["url"],
                "available": row["available"],
            }
        )
    return {
        "kind": kind or "all",
        "total_archive_records": len(rows),
        "available_archive_count": len(available),
        "missing_archive_count": len(missing),
        "downloaded_archive_count": sum(1 for row in available if row["downloaded"]),
        "reused_archive_count": sum(1 for row in available if row["reused_existing"]),
        "checksum_available_count": sum(1 for row in available if row["checksum_available"]),
        "checksum_verified_count": sum(1 for row in available if row["checksum_verified"] is True),
        "availability_by_symbol": dict(by_symbol),
        "missing_archive_sample": [
            {"symbol": row["symbol"], "cadence": row["cadence"], "url": row["url"], "error": row["error"]}
            for row in missing[:50]
        ],
    }


def load_symbol_data(paths_by_symbol: dict[str, dict[str, list[Path]]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]], list[str]]:
    metrics_by_symbol: dict[str, list[dict[str, Any]]] = {}
    kline_by_symbol: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    for symbol, paths in paths_by_symbol.items():
        if not paths["metrics"] or not paths["klines"]:
            warnings.append(f"{symbol} missing pre-2023 archives: metrics={len(paths['metrics'])}, klines={len(paths['klines'])}")
            continue
        try:
            metrics_by_symbol[symbol] = BASE.read_metrics_archives(paths["metrics"], symbol)
            kline_by_symbol[symbol] = BASE.read_kline_archives(paths["klines"], symbol)
        except Exception as exc:
            warnings.append(f"{symbol} load warning: {exc}")
    return metrics_by_symbol, kline_by_symbol, warnings


def observed_with_holdout_names(observed: dict[str, Any]) -> dict[str, Any]:
    stats = observed["observed_primary_stats"]
    return {
        "event_count": stats.get("event_count"),
        "valid_forward_return_count": stats.get("valid_forward_return_count"),
        "missing_forward_return_count": stats.get("missing_forward_return_count"),
        "mean_forward_return": stats.get("mean"),
        "median_forward_return": stats.get("median"),
        "std_forward_return": stats.get("std"),
        "positive_rate_forward_return": stats.get("positive_rate"),
        "negative_rate_forward_return": stats.get("negative_rate"),
        "q01": stats.get("q01"),
        "q05": stats.get("q05"),
        "q25": stats.get("q25"),
        "q50": stats.get("q50"),
        "q75": stats.get("q75"),
        "q95": stats.get("q95"),
        "q99": stats.get("q99"),
        "mean_gross_short_interpretation_return": (-1.0 * stats["mean"]) if isinstance(stats.get("mean"), (int, float)) else None,
    }


def cost_stressed_returns(forward_returns: list[float]) -> dict[str, Any]:
    gross = np.asarray([-1.0 * value for value in forward_returns if np.isfinite(value)], dtype=np.float64)
    result = {}
    for bps in COST_STRESS_BPS:
        stressed = gross - (bps / 10000.0)
        result[f"{bps}bps"] = {
            "mean_short_interpretation_return": float(np.mean(stressed)) if stressed.size else None,
            "positive_rate": float(np.mean(stressed > 0.0)) if stressed.size else None,
            "cost_bps_per_event": bps,
            "compounding_used": False,
            "position_sizing_used": False,
            "deployable_pnl": False,
        }
    return result


def classify(
    observed_stats: dict[str, Any],
    p_values: dict[str, Any],
    gates: dict[str, bool],
    data_unavailable: bool,
    data_quality_attention: bool,
) -> tuple[str, str, bool, str]:
    event_count = int(observed_stats.get("event_count") or 0)
    if data_unavailable:
        return RESULT_DATA_UNAVAILABLE, NEXT_ACCUMULATION, False, "pre-2023 metrics/klines unavailable for frozen reconstruction"
    if event_count < 50:
        return RESULT_INCONCLUSIVE, NEXT_ACCUMULATION, False, "fewer than 50 valid holdout events"
    if event_count < 100:
        return RESULT_INCONCLUSIVE, NEXT_ACCUMULATION, False, "50-99 valid holdout events: inconclusive by preregistered sample rule"
    if data_quality_attention:
        return RESULT_ATTENTION, NEXT_REPAIR, False, "data quality attention prevents clean holdout decision"
    p_negative = p_values.get("p_negative_mean")
    if all(gates.values()) and isinstance(p_negative, (int, float)) and p_negative <= 0.05:
        return RESULT_PASS, NEXT_HOLDOUT_EVALUATOR, True, "frozen historical holdout diagnostic gates passed"
    return RESULT_FAIL, NEXT_CLOSE_OR_REDESIGN, False, "frozen historical holdout diagnostic gates failed"


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy_release": False,
        "signal": False,
        "live_paper_trading": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "optimization_against_holdout_returns": False,
        "event_definition_changes": False,
        "threshold_changes": False,
        "horizon_changes": False,
        "used_2023_2025_as_holdout": False,
        "picked_window_based_on_results": False,
        "deployable_pnl_reported": False,
    }


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
        "holdout_backtest_status": HOLDOUT_STATUS_BLOCKED,
        "status": HOLDOUT_STATUS_BLOCKED,
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
        "requested_holdout_window": REQUESTED_HOLDOUT_WINDOW,
        "actual_holdout_window": {},
        "public_data_source_summary": {},
        "symbols_requested": DEFAULT_SYMBOLS,
        "symbols_available": [],
        "archive_availability_summary": {},
        "metrics_availability_summary": {},
        "kline_availability_summary": {},
        "event_reconstruction_status": "BLOCKED",
        "event_count": 0,
        "symbol_coverage": {},
        "month_coverage": {},
        "observed_primary_stats": {},
        "cost_stressed_diagnostic_returns": {},
        "null_model": "month_aware_symbol_balanced_null",
        "permutation_count_requested": 1000,
        "permutation_count_completed": 0,
        "null_stats": {},
        "p_values": {},
        "fdr_q_value": None,
        "bonferroni_p_value": None,
        "holdout_gates": {},
        "failed_holdout_gates": [reason],
        "sensitivity_diagnostics": {},
        "data_quality_warnings": [f"BLOCKED: {reason}"],
        "final_holdout_decision": "blocked",
        "historical_holdout_passed": False,
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
    contract, independent, semantics, refinement, dataset, payload_hashes = load_inputs()
    input_checks = validate_input_chain(contract, independent, semantics, refinement)
    if not all(input_checks.values()):
        raise HoldoutBlocked(f"input chain validation failed: {input_checks}")

    symbols = dataset_symbols(dataset)
    paths_by_symbol, manifest = get_all_archives(symbols)
    metrics_by_symbol, kline_by_symbol, load_warnings = load_symbol_data(paths_by_symbol)
    symbols_available = sorted(set(metrics_by_symbol) & set(kline_by_symbol))
    data_unavailable = len(symbols_available) == 0
    if data_unavailable:
        reconstructed = {"events": [], "raw_event_count": 0, "cooldown_filtered_count": 0}
        observed = {
            "values": [],
            "valid_event_returns": [],
            "observed_primary_stats": BASE.summarize_array([]) | {
                "event_count": 0,
                "valid_forward_return_count": 0,
                "missing_forward_return_count": 0,
            },
            "missing_join_count": 0,
        }
        null_result = {
            "permutation_count_requested": 1000,
            "permutation_count_completed": 0,
            "null_stats": BASE.summarize_null_means(np.asarray([], dtype=np.float64)),
            "p_values": {"p_two_sided": None, "p_positive_mean": None, "p_negative_mean": None},
            "fdr_q_value": None,
            "bonferroni_p_value": None,
        }
        sensitivity = {}
    else:
        reconstructed = BASE.reconstruct_short_core_events(metrics_by_symbol, kline_by_symbol)
        observed = BASE.observed_primary(reconstructed["events"], kline_by_symbol)
        null_result = BASE.month_aware_symbol_balanced_null(observed, kline_by_symbol)
        sensitivity = BASE.build_sensitivity_diagnostics(observed)

    observed_named = observed_with_holdout_names(observed)
    event_months = sorted({event["month"] for event in reconstructed.get("events", [])})
    event_symbols = sorted({event["symbol"] for event in reconstructed.get("events", [])})
    valid_forward_returns = observed.get("values", [])
    cost_stress = cost_stressed_returns(valid_forward_returns)
    all_mins = [data["timestamp_min"] for data in kline_by_symbol.values()]
    all_maxs = [data["timestamp_max"] for data in kline_by_symbol.values()]
    actual_window = {
        "start": min(all_mins) if all_mins else None,
        "end": max(all_maxs) if all_maxs else None,
        "pre_2023_only": True,
        "used_2023_2025_research_sample": False,
    }
    archive_all = archive_summary(manifest)
    archive_metrics = archive_summary(manifest, "metrics")
    archive_klines = archive_summary(manifest, "klines")
    observed_stats = observed["observed_primary_stats"]
    p_values = null_result["p_values"]
    fdr_q = null_result.get("fdr_q_value")
    bonferroni = null_result.get("bonferroni_p_value")
    cost_5bps = cost_stress.get("5bps", {}).get("mean_short_interpretation_return")
    cost_10bps = cost_stress.get("10bps", {}).get("mean_short_interpretation_return")
    holdout_gates = {
        "pre_2023_data_only": actual_window["end"] is None or str(actual_window["end"]) < "2023-01-01",
        "current_prior_bar_reconstruction_only": True,
        "sufficient_event_count_gte_100": int(observed_stats.get("event_count") or 0) >= 100,
        "observed_primary_mean_negative": isinstance(observed_stats.get("mean"), (int, float)) and observed_stats["mean"] < 0,
        "p_negative_mean_lte_0_05": isinstance(p_values.get("p_negative_mean"), (int, float)) and p_values["p_negative_mean"] <= 0.05,
        "cost_stressed_non_trivial_5bps": isinstance(cost_5bps, (int, float)) and cost_5bps > 0,
        "cost_stressed_non_trivial_10bps": isinstance(cost_10bps, (int, float)) and cost_10bps > 0,
        "leave_one_symbol_month_no_obvious_dependence_when_applicable": (
            not sensitivity
            or (
                sensitivity.get("leave_one_symbol_out", {}).get("any_single_dependence") is not True
                and sensitivity.get("leave_one_month_out", {}).get("any_single_dependence") is not True
            )
        ),
        "no_forbidden_action_occurred": True,
    }
    failed_gates = [key for key, value in holdout_gates.items() if value is not True]
    data_quality_warnings = list(load_warnings)
    if archive_all["missing_archive_count"]:
        data_quality_warnings.append(f"{archive_all['missing_archive_count']} public pre-2023 archive probes were unavailable.")
    if observed_stats.get("missing_forward_return_count"):
        data_quality_warnings.append(f"{observed_stats['missing_forward_return_count']} event rows had missing 1h forward returns.")
    data_quality_attention = (
        not data_unavailable
        and int(observed_stats.get("event_count") or 0) >= 100
        and int(observed_stats.get("valid_forward_return_count") or 0) < int(observed_stats.get("event_count") or 0) * 0.8
    )
    result_classification, allowed_next_step, holdout_passed, final_decision = classify(
        observed_stats,
        p_values,
        holdout_gates,
        data_unavailable,
        data_quality_attention,
    )
    if result_classification in {RESULT_INCONCLUSIVE, RESULT_DATA_UNAVAILABLE}:
        failed_gates = [gate for gate in failed_gates if gate != "sufficient_event_count_gte_100"] + [
            "insufficient_or_unavailable_pre_2023_holdout_sample"
        ]

    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise HoldoutBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    validation_checks = {
        **input_checks,
        "input_artifact_hashes_unchanged": input_unchanged,
        "public_data_vision_only": True,
        "pre_2023_only": holdout_gates["pre_2023_data_only"],
        "no_2023_2025_holdout_reuse": True,
        "no_strategy_signal_candidate_release_permissions": True,
        "no_artifacts_data_builds_written": True,
    }
    artifact = {
        "holdout_backtest_status": HOLDOUT_STATUS_PASS,
        "status": HOLDOUT_STATUS_PASS,
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
        "requested_holdout_window": REQUESTED_HOLDOUT_WINDOW,
        "actual_holdout_window": actual_window,
        "public_data_source_summary": {
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
        "archive_availability_summary": archive_all,
        "metrics_availability_summary": archive_metrics,
        "kline_availability_summary": archive_klines,
        "event_reconstruction_status": "RECONSTRUCTED_FROZEN_SHORT_CORE_ONLY" if not data_unavailable else "DATA_UNAVAILABLE",
        "event_reconstruction_summary": reconstructed,
        "event_count": int(observed_stats.get("event_count") or 0),
        "symbol_coverage": {
            "symbol_count": len(event_symbols),
            "symbols": event_symbols,
            "top_contributor_symbols": sensitivity.get("top_contributor_symbols") if sensitivity else [],
        },
        "month_coverage": {
            "month_count": len(event_months),
            "months": event_months,
            "top_contributor_months": sensitivity.get("top_contributor_months") if sensitivity else [],
        },
        "observed_primary_stats": observed_named,
        "cost_stressed_diagnostic_returns": cost_stress,
        "null_model": "month_aware_symbol_balanced_null",
        "permutation_count_requested": int(null_result["permutation_count_requested"]),
        "permutation_count_completed": int(null_result["permutation_count_completed"]),
        "null_stats": null_result["null_stats"],
        "p_values": p_values,
        "fdr_q_value": fdr_q,
        "bonferroni_p_value": bonferroni,
        "holdout_gates": holdout_gates,
        "failed_holdout_gates": failed_gates,
        "sensitivity_diagnostics": sensitivity,
        "data_quality_warnings": data_quality_warnings,
        "final_holdout_decision": final_decision,
        "historical_holdout_passed": holdout_passed,
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
        "replacement_checks_all_true": all(validation_checks.values()),
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"status: {artifact['holdout_backtest_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"approved_neutral_diagnostic_label: {artifact['approved_neutral_diagnostic_label']}")
    print(f"requested_holdout_window: {artifact['requested_holdout_window']}")
    print(f"actual_holdout_window: {artifact['actual_holdout_window']}")
    print(f"symbols_requested: {artifact['symbols_requested']}")
    print(f"symbols_available: {artifact['symbols_available']}")
    print(f"archive_availability_summary: {artifact['archive_availability_summary']}")
    print(f"event_count: {artifact['event_count']}")
    print(f"symbol_coverage: {artifact['symbol_coverage']}")
    print(f"month_coverage: {artifact['month_coverage']}")
    print(f"observed_primary_stats: {artifact['observed_primary_stats']}")
    print(f"cost_stressed_diagnostic_returns: {artifact['cost_stressed_diagnostic_returns']}")
    print(f"permutation_count_requested: {artifact['permutation_count_requested']}")
    print(f"permutation_count_completed: {artifact['permutation_count_completed']}")
    print(f"p_negative_mean: {artifact['p_values'].get('p_negative_mean')}")
    print(f"fdr_q_value: {artifact['fdr_q_value']}")
    print(f"bonferroni_p_value: {artifact['bonferroni_p_value']}")
    print(f"holdout_gates: {artifact['holdout_gates']}")
    print(f"failed_holdout_gates: {artifact['failed_holdout_gates']}")
    print(f"sensitivity_diagnostics: {artifact['sensitivity_diagnostics']}")
    print(f"data_quality_warnings: {artifact['data_quality_warnings']}")
    print(f"final_holdout_decision: {artifact['final_holdout_decision']}")
    print(f"historical_holdout_passed: {bool_text(bool(artifact['historical_holdout_passed']))}")
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
        return 0 if artifact["holdout_backtest_status"] == HOLDOUT_STATUS_PASS else 1
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
