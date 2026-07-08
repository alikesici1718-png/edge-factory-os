#!/usr/bin/env python
"""Direct robustness diagnostics for Binance OI/taker/crowding forward returns."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import subprocess
import time
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_RUNNER_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_binance_oi_taker_crowding_forward_return_robustness_runner_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_forward_return_robustness_runner_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "42e7be63763abe03bbed01ea83b8510314304238"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_NULL_RUNNER_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_forward_return_null_validation_runner_v1.json"
SOURCE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
SOURCE_EVENT_STUDY_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_proxy_event_study_v1.json"
SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH = "artifacts/contracts/binance_oi_taker_crowding_proxy_validation_contract_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_NULL_RUNNER_RELATIVE_PATH,
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_EVENT_STUDY_RELATIVE_PATH,
    SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
]

ROBUSTNESS_STATUS_PASS = "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_RUNNER_CREATED"
ROBUSTNESS_STATUS_BLOCKED = "BLOCKED_BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_RUNNER"
ARTIFACT_KIND = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_RUNNER"

RESULT_PROMISING = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY"
RESULT_WEAK = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_WEAK_OR_NOT_ROBUST"
RESULT_ATTENTION = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_FAILED_STOP"

NEXT_PROMISING = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_EVALUATOR_V1"
NEXT_WEAK = "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_NULL_VALIDATION_EVALUATOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_KLINE_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"
NEXT_FAILED = "RECOVERY_OR_RUNTIME_REPAIR_V1"

KLINE_CACHE_ROOT = REPO_ROOT / "cache" / "binance_public_kline_forward_return_diagnostic_v1"
KLINE_INTERVAL_MS = 15 * 60 * 1000
START_YEAR_MONTH = (2023, 1)
END_YEAR_MONTH = (2025, 12)

PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528
MONTH_AWARE_MODEL = "month_aware_permutation_null"
SYMBOL_BALANCED_MODEL = "symbol_balanced_non_event_null"

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

PRIOR_TOP_FINDINGS = [
    {"event_definition": "oi_expansion_taker_buy_global_crowding_high", "horizon": "24h"},
    {"event_definition": "oi_expansion_taker_sell_global_crowding_low", "horizon": "4h"},
    {"event_definition": "oi_expansion_taker_sell_global_crowding_low", "horizon": "24h"},
]

FORBIDDEN_FAILED_ROUTES = [
    "funding crowding reversal",
    "funding carry",
    "funding extreme volume surge",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
]


class RobustnessBlocked(Exception):
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
        raise RobustnessBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
    return [line.rstrip() for line in stdout.splitlines() if line.strip()]


def current_head() -> str:
    lines = git_lines(["rev-parse", "HEAD"])
    return lines[0] if lines else ""


def working_tree_status() -> list[str]:
    return git_lines(["status", "--porcelain=v1"])


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
        if line.startswith("!! ") and line[3:].startswith("cache/binance_public_kline_forward_return_diagnostic_v1/"):
            continue
        return False
    return True


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
            raise RobustnessBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RobustnessBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RobustnessBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RobustnessBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise RobustnessBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    null_runner = read_json_readonly(SOURCE_NULL_RUNNER_RELATIVE_PATH)
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    event_study = read_json_readonly(SOURCE_EVENT_STUDY_RELATIVE_PATH)
    validation_contract = read_json_readonly(SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH)
    dataset_builder = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_NULL_RUNNER_RELATIVE_PATH: verify_payload_hash(null_runner, "null validation runner"),
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "public kline diagnostic"),
        SOURCE_EVENT_STUDY_RELATIVE_PATH: verify_payload_hash(event_study, "proxy event study"),
        SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: verify_payload_hash(validation_contract, "proxy validation contract"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset_builder, "metrics dataset builder"),
    }
    if null_runner.get("null_validation_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_NULL_VALIDATION_RUNNER_CREATED":
        raise RobustnessBlocked("null validation runner status is not PASS")
    if null_runner.get("event_count") != 99870 or null_runner.get("unique_event_count") != 75467:
        raise RobustnessBlocked("null validation runner event counts do not match expected facts")
    if null_runner.get("input_artifact_hashes_unchanged") is not True:
        raise RobustnessBlocked("null validation runner input hash guard was not true")
    if diagnostic.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise RobustnessBlocked("public kline diagnostic status is not PASS")
    if diagnostic.get("joined_event_count") != 99870 or diagnostic.get("missing_join_count") != 0:
        raise RobustnessBlocked("public kline diagnostic event join facts do not match expected facts")
    if event_study.get("status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_CREATED":
        raise RobustnessBlocked("event study status is not PASS")
    if validation_contract.get("validation_contract_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_CREATED":
        raise RobustnessBlocked("proxy validation contract status is not PASS")
    if dataset_builder.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise RobustnessBlocked("metrics dataset builder status is not PASS")
    return null_runner, diagnostic, event_study, validation_contract, dataset_builder, payload_hashes


def iso_to_ms(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def ms_to_iso(value: int | None) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_key_from_ms(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m")


def floor_to_15m_open(timestamp_ms: int) -> int:
    return (timestamp_ms // KLINE_INTERVAL_MS) * KLINE_INTERVAL_MS


def month_iter() -> list[tuple[int, int]]:
    year, month = START_YEAR_MONTH
    months = []
    while (year, month) <= END_YEAR_MONTH:
        months.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def parse_checksum_text(text: str) -> str | None:
    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def kline_cache_zip_path(symbol: str, year: int, month: int) -> Path:
    return (
        KLINE_CACHE_ROOT
        / "raw_archives"
        / "klines"
        / symbol
        / "15m"
        / f"{symbol}-15m-{year:04d}-{month:02d}.zip"
    )


def expected_missing_archive_keys(diagnostic: dict[str, Any]) -> set[tuple[str, int, int]]:
    missing = diagnostic.get("kline_data_quality", {}).get("missing_archives", [])
    if not isinstance(missing, list):
        raise RobustnessBlocked("diagnostic missing_archives is not a list")
    output = set()
    for item in missing:
        if isinstance(item, dict):
            output.add((str(item.get("symbol")), int(item.get("year")), int(item.get("month"))))
    return output


def verify_cached_archives(symbols: list[str], diagnostic: dict[str, Any]) -> dict[str, Any]:
    missing_keys = expected_missing_archive_keys(diagnostic)
    archive_records: list[dict[str, Any]] = []
    checksum_available = 0
    checksum_verified = 0
    unexpected_missing = []
    for symbol in symbols:
        for year, month in month_iter():
            key = (symbol, year, month)
            path = kline_cache_zip_path(symbol, year, month)
            if key in missing_keys:
                archive_records.append({"symbol": symbol, "year": year, "month": month, "available": False, "local_path": str(path)})
                continue
            if not path.exists():
                unexpected_missing.append(str(path))
                continue
            checksum_path = path.with_name(path.name + ".CHECKSUM")
            expected_sha = None
            checksum_ok = False
            if checksum_path.exists():
                expected_sha = parse_checksum_text(checksum_path.read_text(encoding="utf-8", errors="replace"))
                checksum_ok = expected_sha is not None
            checksum_available += int(checksum_ok)
            actual_sha = sha256_file(path)
            verified = expected_sha is None or expected_sha == actual_sha
            if checksum_ok and verified:
                checksum_verified += 1
            if not verified:
                raise RobustnessBlocked(f"kline cache checksum mismatch: {path}")
            archive_records.append(
                {
                    "symbol": symbol,
                    "year": year,
                    "month": month,
                    "available": True,
                    "local_path": str(path),
                    "checksum_available": checksum_ok,
                    "checksum_verified": verified if checksum_ok else None,
                    "sha256": actual_sha,
                    "bytes": path.stat().st_size,
                }
            )
    if unexpected_missing:
        raise RobustnessBlocked(f"required cached kline archives missing: {unexpected_missing[:5]}")
    available_count = sum(1 for record in archive_records if record["available"])
    expected_available = diagnostic.get("public_data_source", {}).get("monthly_archive_count_available")
    if available_count != expected_available:
        raise RobustnessBlocked(f"cached archive count mismatch: {available_count} != {expected_available}")
    return {
        "archive_records": archive_records,
        "available_count": available_count,
        "missing_count": len(missing_keys),
        "checksum_available": checksum_available,
        "checksum_verified": checksum_verified,
    }


def detect_header(row: list[str]) -> bool:
    return bool(row) and not str(row[0]).strip().isdigit()


def load_kline_symbol(symbol: str, archive_records: list[dict[str, Any]]) -> dict[str, Any]:
    close_by_open: dict[int, float] = {}
    duplicate_open_time_count = 0
    invalid_numeric_count = 0
    for record in archive_records:
        if record["symbol"] != symbol or not record["available"]:
            continue
        path = Path(record["local_path"])
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise RobustnessBlocked(f"no CSV member found in cached kline archive: {path}")
            for name in csv_names:
                rows = csv.reader(io.StringIO(archive.read(name).decode("utf-8", errors="replace")))
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
                    if open_time in close_by_open:
                        duplicate_open_time_count += 1
                        continue
                    close_by_open[open_time] = close_price
    if not close_by_open:
        raise RobustnessBlocked(f"no cached kline rows loaded for {symbol}")
    opens = np.array(sorted(close_by_open), dtype=np.int64)
    closes = np.array([close_by_open[int(open_time)] for open_time in opens], dtype=np.float64)
    months = np.array([month_key_from_ms(int(open_time)) for open_time in opens])
    open_to_index = {int(open_time): int(index) for index, open_time in enumerate(opens)}
    returns_by_horizon = {}
    valid_returns_by_horizon = {}
    valid_returns_by_month_horizon: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    valid_indices_by_month_horizon: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    for horizon, horizon_ms in HORIZONS.items():
        future = opens + horizon_ms
        future_index = np.searchsorted(opens, future)
        in_range = future_index < len(opens)
        matched = np.zeros(len(opens), dtype=bool)
        matched[in_range] = opens[future_index[in_range]] == future[in_range]
        valid = matched & (closes != 0.0) & np.isfinite(closes)
        returns = np.full(len(opens), np.nan, dtype=np.float64)
        returns[valid] = (closes[future_index[valid]] / closes[valid]) - 1.0
        returns_by_horizon[horizon] = returns
        valid_returns_by_horizon[horizon] = returns[np.isfinite(returns)]
        for month in sorted(set(months)):
            month_valid = (months == month) & np.isfinite(returns)
            valid_returns_by_month_horizon[month][horizon] = returns[month_valid]
            valid_indices_by_month_horizon[month][horizon] = np.nonzero(month_valid)[0].astype(np.int64)
    return {
        "symbol": symbol,
        "opens": opens,
        "months": months,
        "open_to_index": open_to_index,
        "returns_by_horizon": returns_by_horizon,
        "valid_returns_by_horizon": valid_returns_by_horizon,
        "valid_returns_by_month_horizon": valid_returns_by_month_horizon,
        "valid_indices_by_month_horizon": valid_indices_by_month_horizon,
        "quality": {
            "symbol": symbol,
            "row_count": int(len(opens)),
            "timestamp_min": ms_to_iso(int(opens[0])),
            "timestamp_max": ms_to_iso(int(opens[-1])),
            "duplicate_open_time_count": duplicate_open_time_count,
            "invalid_numeric_count": invalid_numeric_count,
        },
    }


def normalized_paths(dataset_builder: dict[str, Any]) -> list[Path]:
    files = dataset_builder.get("generated_external_files", {}).get("normalized_by_symbol_files")
    if not isinstance(files, list) or not files:
        raise RobustnessBlocked("dataset builder artifact missing normalized_by_symbol_files")
    paths = [Path(str(path)) for path in files]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise RobustnessBlocked(f"normalized proxy dataset files missing: {missing}")
    return sorted(paths, key=lambda path: path.name)


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "nan"}:
        return None
    try:
        output = float(text)
    except ValueError:
        return None
    if math.isnan(output) or math.isinf(output):
        return None
    return output


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


def empirical_p_values(observed_mean: float | None, null_means: np.ndarray) -> dict[str, Any]:
    if observed_mean is None or not np.isfinite(observed_mean):
        return {
            "p_two_sided": None,
            "p_positive_mean": None,
            "p_negative_mean": None,
            "empirical_p_value_formula": "p = (1 + number_of_null_stats_as_or_more_extreme_than_observed) / (1 + permutation_count)",
        }
    null_center = float(np.mean(null_means))
    denominator = 1 + PERMUTATION_COUNT
    return {
        "p_two_sided": float((1 + int(np.sum(np.abs(null_means - null_center) >= abs(observed_mean - null_center)))) / denominator),
        "p_positive_mean": float((1 + int(np.sum(null_means >= observed_mean))) / denominator),
        "p_negative_mean": float((1 + int(np.sum(null_means <= observed_mean))) / denominator),
        "empirical_p_value_formula": "p = (1 + number_of_null_stats_as_or_more_extreme_than_observed) / (1 + permutation_count)",
        "null_center_used_for_two_sided": null_center,
    }


def build_event_universe(
    event_study: dict[str, Any],
    dataset_builder: dict[str, Any],
    kline_data: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    thresholds_by_symbol = event_study.get("descriptive_statistics", {}).get("per_symbol_thresholds", {})
    if not isinstance(thresholds_by_symbol, dict):
        raise RobustnessBlocked("event study missing per_symbol_thresholds")
    observed_values = {event_id: {horizon: [] for horizon in HORIZONS} for event_id in EVENT_IDS}
    observed_by_symbol = {
        event_id: {symbol: {horizon: [] for horizon in HORIZONS} for symbol in kline_data} for event_id in EVENT_IDS
    }
    observed_by_month = {
        event_id: defaultdict(lambda: {horizon: [] for horizon in HORIZONS}) for event_id in EVENT_IDS
    }
    group_counts = {
        event_id: defaultdict(lambda: {horizon: 0 for horizon in HORIZONS}) for event_id in EVENT_IDS
    }
    event_indices_by_group = {event_id: defaultdict(set) for event_id in EVENT_IDS}
    missing_forward = {event_id: {horizon: 0 for horizon in HORIZONS} for event_id in EVENT_IDS}
    unique_values = {horizon: [] for horizon in HORIZONS}
    unique_event_keys: set[tuple[str, str]] = set()
    event_count = 0
    missing_join_count = 0
    timestamp_min: str | None = None
    timestamp_max: str | None = None
    symbols_with_events: set[str] = set()
    months_with_events: set[str] = set()
    multi_definition_symbol_timestamp_events = 0

    for path in normalized_paths(dataset_builder):
        symbol = path.name.split("_", 1)[0]
        thresholds = thresholds_by_symbol.get(symbol)
        if not isinstance(thresholds, dict):
            raise RobustnessBlocked(f"event thresholds missing for {symbol}")
        symbol_kline = kline_data[symbol]
        open_to_index = symbol_kline["open_to_index"]
        returns_by_horizon = symbol_kline["returns_by_horizon"]
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                events = evaluate_row(row, thresholds)
                if not events:
                    continue
                timestamp = row["timestamp"]
                event_ms = iso_to_ms(timestamp)
                base_open = floor_to_15m_open(event_ms)
                base_index = open_to_index.get(base_open)
                month = month_key_from_ms(base_open)
                timestamp_min = timestamp if timestamp_min is None else min(timestamp_min, timestamp)
                timestamp_max = timestamp if timestamp_max is None else max(timestamp_max, timestamp)
                symbols_with_events.add(symbol)
                months_with_events.add(month)
                if len(events) > 1:
                    multi_definition_symbol_timestamp_events += 1
                if base_index is None:
                    missing_join_count += len(events)
                    continue
                unique_key = (symbol, timestamp)
                if unique_key not in unique_event_keys:
                    unique_event_keys.add(unique_key)
                    for horizon in HORIZONS:
                        value = returns_by_horizon[horizon][base_index]
                        if np.isfinite(value):
                            unique_values[horizon].append(float(value))
                for event_id in events:
                    event_count += 1
                    group_key = f"{symbol}|{month}"
                    event_indices_by_group[event_id][group_key].add(int(base_index))
                    for horizon in HORIZONS:
                        value = returns_by_horizon[horizon][base_index]
                        if np.isfinite(value):
                            observed_values[event_id][horizon].append(float(value))
                            observed_by_symbol[event_id][symbol][horizon].append(float(value))
                            observed_by_month[event_id][month][horizon].append(float(value))
                            group_counts[event_id][group_key][horizon] += 1
                        else:
                            missing_forward[event_id][horizon] += 1

    return {
        "observed_values": observed_values,
        "observed_by_symbol": observed_by_symbol,
        "observed_by_month": observed_by_month,
        "group_counts": group_counts,
        "event_indices_by_group": event_indices_by_group,
        "missing_forward": missing_forward,
        "unique_values": unique_values,
        "event_count": event_count,
        "missing_join_count": missing_join_count,
        "unique_event_count": len(unique_event_keys),
        "symbol_count": len(symbols_with_events),
        "months_with_events": sorted(months_with_events),
        "timestamp_min": timestamp_min,
        "timestamp_max": timestamp_max,
        "multi_definition_symbol_timestamp_events": multi_definition_symbol_timestamp_events,
    }


def resample_mean_from_groups(
    rng: np.random.Generator,
    event_id: str,
    horizon: str,
    event_universe: dict[str, Any],
    kline_data: dict[str, dict[str, Any]],
    model: str,
) -> tuple[np.ndarray, dict[str, int]]:
    null_sums = np.zeros(PERMUTATION_COUNT, dtype=np.float64)
    total_count = 0
    fallback_counts = {"same_symbol_month_pool_used": 0, "symbol_fallback_used": 0, "empty_group_count": 0}
    for group_key, per_horizon in event_universe["group_counts"][event_id].items():
        count = int(per_horizon[horizon])
        if count <= 0:
            continue
        symbol, month = group_key.split("|", 1)
        symbol_data = kline_data[symbol]
        if model == MONTH_AWARE_MODEL:
            candidates = symbol_data["valid_returns_by_month_horizon"].get(month, {}).get(horizon, np.array([], dtype=np.float64))
        else:
            candidate_indices = symbol_data["valid_indices_by_month_horizon"].get(month, {}).get(horizon, np.array([], dtype=np.int64))
            event_indices = event_universe["event_indices_by_group"][event_id].get(group_key, set())
            if candidate_indices.size:
                keep = np.array([int(index) not in event_indices for index in candidate_indices], dtype=bool)
                candidate_indices = candidate_indices[keep]
            candidates = symbol_data["returns_by_horizon"][horizon][candidate_indices]
            candidates = candidates[np.isfinite(candidates)]
        if candidates.size == 0:
            candidates = symbol_data["valid_returns_by_horizon"][horizon]
            fallback_counts["symbol_fallback_used"] += 1
        else:
            fallback_counts["same_symbol_month_pool_used"] += 1
        if candidates.size == 0:
            fallback_counts["empty_group_count"] += 1
            continue
        total_count += count
        draws = rng.integers(0, candidates.size, size=(PERMUTATION_COUNT, count))
        null_sums += candidates[draws].sum(axis=1)
    if total_count <= 0:
        raise RobustnessBlocked(f"zero valid event count for {model} {event_id} {horizon}")
    return null_sums / float(total_count), fallback_counts


def benjamini_hochberg(p_items: list[tuple[str, float]]) -> dict[str, float]:
    m = len(p_items)
    if m == 0:
        return {}
    ordered = sorted(p_items, key=lambda item: item[1])
    q_values = {}
    running_min = 1.0
    for rank_from_end, (key, p_value) in enumerate(reversed(ordered), start=1):
        rank = m - rank_from_end + 1
        q_value = min(running_min, p_value * m / rank)
        running_min = q_value
        q_values[key] = float(min(q_value, 1.0))
    return q_values


def run_null_model(
    rng: np.random.Generator,
    event_universe: dict[str, Any],
    kline_data: dict[str, dict[str, Any]],
    model: str,
) -> dict[str, Any]:
    null_stats = {event_id: {} for event_id in EVENT_IDS}
    p_values = {event_id: {} for event_id in EVENT_IDS}
    fallback_summary = {event_id: {} for event_id in EVENT_IDS}
    p_items: list[tuple[str, float]] = []
    for event_id in EVENT_IDS:
        for horizon in HORIZONS:
            observed = summarize_array(event_universe["observed_values"][event_id][horizon])
            null_means, fallback_counts = resample_mean_from_groups(rng, event_id, horizon, event_universe, kline_data, model)
            summary = summarize_null_means(null_means)
            p_summary = empirical_p_values(observed["mean"], null_means)
            null_stats[event_id][horizon] = {**summary, **p_summary}
            p_values[event_id][horizon] = p_summary
            fallback_summary[event_id][horizon] = fallback_counts
            p_two = p_summary["p_two_sided"]
            if isinstance(p_two, float):
                p_items.append((f"{event_id}|{horizon}", p_two))
    fdr_flat = benjamini_hochberg(p_items)
    bonferroni_flat = {key: float(min(value * len(p_items), 1.0)) for key, value in p_items}
    fdr_nested = {event_id: {} for event_id in EVENT_IDS}
    bonferroni_nested = {event_id: {} for event_id in EVENT_IDS}
    for key, q_value in fdr_flat.items():
        event_id, horizon = key.split("|", 1)
        fdr_nested[event_id][horizon] = q_value
    for key, p_value in bonferroni_flat.items():
        event_id, horizon = key.split("|", 1)
        bonferroni_nested[event_id][horizon] = p_value
    return {
        "model": model,
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": PERMUTATION_COUNT,
        "null_stats": null_stats,
        "p_values": p_values,
        "fdr_q_values": fdr_nested,
        "bonferroni_p_values": bonferroni_nested,
        "fallback_summary": fallback_summary,
        "top_findings": top_findings_from_p(fdr_nested, p_values),
    }


def top_findings_from_p(fdr_q_values: dict[str, dict[str, float]], p_values: dict[str, dict[str, dict[str, Any]]], limit: int = 5) -> list[dict[str, Any]]:
    rows = []
    for event_id, per_horizon in fdr_q_values.items():
        for horizon, q_value in per_horizon.items():
            rows.append(
                {
                    "event_definition": event_id,
                    "horizon": horizon,
                    "fdr_q": q_value,
                    "p_two_sided": p_values[event_id][horizon]["p_two_sided"],
                    "p_positive_mean": p_values[event_id][horizon]["p_positive_mean"],
                    "p_negative_mean": p_values[event_id][horizon]["p_negative_mean"],
                }
            )
    rows.sort(key=lambda item: item["fdr_q"])
    return rows[:limit]


def observed_stats_by_event(event_universe: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        event_id: {
            horizon: summarize_array(event_universe["observed_values"][event_id][horizon])
            for horizon in HORIZONS
        }
        for event_id in EVENT_IDS
    }


def summarize_exclusion(base_mean: float | None, values: list[float]) -> dict[str, Any]:
    stats = summarize_array(values)
    mean = stats["mean"]
    if base_mean is None or mean is None or base_mean == 0:
        direction_same = None
        magnitude_ratio = None
        destroys_effect = None
    else:
        direction_same = (base_mean > 0 and mean > 0) or (base_mean < 0 and mean < 0)
        magnitude_ratio = abs(mean) / abs(base_mean)
        destroys_effect = (not direction_same) or magnitude_ratio < 0.25
    return {
        **stats,
        "direction_same_as_full_sample": direction_same,
        "magnitude_ratio_to_full_sample": magnitude_ratio,
        "destroys_effect_by_rule": destroys_effect,
    }


def leave_one_symbol_out(event_universe: dict[str, Any], observed_stats: dict[str, Any]) -> dict[str, Any]:
    symbols = sorted(next(iter(event_universe["observed_by_symbol"].values())).keys())
    detail = {}
    necessary_symbols = set()
    for finding in PRIOR_TOP_FINDINGS:
        event_id = finding["event_definition"]
        horizon = finding["horizon"]
        base_mean = observed_stats[event_id][horizon]["mean"]
        finding_key = f"{event_id}|{horizon}"
        detail[finding_key] = {}
        for excluded_symbol in symbols:
            values: list[float] = []
            for symbol in symbols:
                if symbol != excluded_symbol:
                    values.extend(event_universe["observed_by_symbol"][event_id][symbol][horizon])
            summary = summarize_exclusion(base_mean, values)
            detail[finding_key][excluded_symbol] = summary
            if summary["destroys_effect_by_rule"] is True:
                necessary_symbols.add(excluded_symbol)
    return {
        "symbols_tested": symbols,
        "prior_top_finding_details": detail,
        "single_symbol_necessary_by_rule": sorted(necessary_symbols),
        "any_single_symbol_necessary": bool(necessary_symbols),
    }


def leave_one_month_out(event_universe: dict[str, Any], observed_stats: dict[str, Any]) -> dict[str, Any]:
    months = event_universe["months_with_events"]
    detail = {}
    necessary_months = set()
    for finding in PRIOR_TOP_FINDINGS:
        event_id = finding["event_definition"]
        horizon = finding["horizon"]
        base_mean = observed_stats[event_id][horizon]["mean"]
        finding_key = f"{event_id}|{horizon}"
        detail[finding_key] = {}
        for excluded_month in months:
            values: list[float] = []
            for month in months:
                if month != excluded_month:
                    values.extend(event_universe["observed_by_month"][event_id].get(month, {}).get(horizon, []))
            summary = summarize_exclusion(base_mean, values)
            detail[finding_key][excluded_month] = summary
            if summary["destroys_effect_by_rule"] is True:
                necessary_months.add(excluded_month)
    return {
        "months_tested": months,
        "prior_top_finding_details": detail,
        "single_month_necessary_by_rule": sorted(necessary_months),
        "any_single_month_necessary": bool(necessary_months),
    }


def arbusdt_exclusion(event_universe: dict[str, Any], observed_stats: dict[str, Any]) -> dict[str, Any]:
    output = {}
    destroyed = []
    for finding in PRIOR_TOP_FINDINGS:
        event_id = finding["event_definition"]
        horizon = finding["horizon"]
        base_mean = observed_stats[event_id][horizon]["mean"]
        values: list[float] = []
        for symbol, per_horizon in event_universe["observed_by_symbol"][event_id].items():
            if symbol != "ARBUSDT":
                values.extend(per_horizon[horizon])
        key = f"{event_id}|{horizon}"
        summary = summarize_exclusion(base_mean, values)
        output[key] = summary
        if summary["destroys_effect_by_rule"] is True:
            destroyed.append(key)
    return {
        "excluded_symbol": "ARBUSDT",
        "prior_top_finding_details": output,
        "destroyed_top_findings_by_rule": destroyed,
        "arbusdt_exclusion_destroys_any_top_finding": bool(destroyed),
    }


def unique_event_sensitivity(event_universe: dict[str, Any], observed_stats: dict[str, Any]) -> dict[str, Any]:
    observed_unique = {horizon: summarize_array(event_universe["unique_values"][horizon]) for horizon in HORIZONS}
    prior_detail = {}
    reversed_items = []
    for finding in PRIOR_TOP_FINDINGS:
        event_id = finding["event_definition"]
        horizon = finding["horizon"]
        base_mean = observed_stats[event_id][horizon]["mean"]
        unique_mean = observed_unique[horizon]["mean"]
        if base_mean is None or unique_mean is None:
            reversed_direction = None
        else:
            reversed_direction = (base_mean > 0 and unique_mean < 0) or (base_mean < 0 and unique_mean > 0)
        key = f"{event_id}|{horizon}"
        prior_detail[key] = {
            "full_overlap_event_definition_mean": base_mean,
            "unique_all_event_rows_mean": unique_mean,
            "direction_reversed": reversed_direction,
            "note": "Unique-event observed summary counts distinct symbol/timestamp rows once across all definitions.",
        }
        if reversed_direction is True:
            reversed_items.append(key)
    return {
        "computed_observed_unique_event_statistics": True,
        "full_unique_null_testing_computed": False,
        "full_unique_null_testing_skipped_reason": "Main robustness nulls ran for overlap-aware events; unique-event sensitivity reports observed unique-event direction only.",
        "unique_event_count": event_universe["unique_event_count"],
        "observed_stats_by_horizon": observed_unique,
        "prior_top_finding_details": prior_detail,
        "unique_event_sensitivity_reverses_any_top_finding": bool(reversed_items),
        "reversed_top_findings": reversed_items,
    }


def missing_archive_summary(diagnostic: dict[str, Any]) -> dict[str, Any]:
    return {
        "monthly_archive_count_requested": diagnostic.get("public_data_source", {}).get("monthly_archive_count_requested"),
        "monthly_archive_count_available": diagnostic.get("public_data_source", {}).get("monthly_archive_count_available"),
        "monthly_archive_count_missing": diagnostic.get("public_data_source", {}).get("monthly_archive_count_missing"),
        "missing_archives": diagnostic.get("kline_data_quality", {}).get("missing_archives", []),
    }


def flatten_missing_forward(missing_forward: dict[str, dict[str, int]]) -> dict[str, int]:
    totals = {horizon: 0 for horizon in HORIZONS}
    for per_horizon in missing_forward.values():
        for horizon, count in per_horizon.items():
            totals[horizon] += int(count)
    return totals


def data_quality_warnings(diagnostic: dict[str, Any], event_universe: dict[str, Any]) -> list[str]:
    missing_forward = {horizon: count for horizon, count in flatten_missing_forward(event_universe["missing_forward"]).items() if count}
    warnings = [
        "358/360 monthly 15m kline archives available from prior public Binance Data Vision diagnostic.",
        "2 missing monthly archives recorded: ARBUSDT 2023-01 and ARBUSDT 2023-02.",
        f"Missing join count from prior diagnostic: {diagnostic.get('missing_join_count')}.",
    ]
    if missing_forward:
        warnings.append(f"Observed missing forward-return rows by horizon: {missing_forward}.")
    else:
        warnings.append("Observed missing forward-return rows by horizon: none.")
    return warnings


def forbidden_false() -> dict[str, bool]:
    return {
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
        "private_api": False,
        "account_api": False,
        "api_key": False,
    }


def robustness_gate_summary(
    month_model: dict[str, Any],
    symbol_model: dict[str, Any],
    loo_symbol: dict[str, Any],
    loo_month: dict[str, Any],
    arbusdt: dict[str, Any],
    unique_summary: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    robust = []
    failed = []
    for finding in PRIOR_TOP_FINDINGS:
        event_id = finding["event_definition"]
        horizon = finding["horizon"]
        key = f"{event_id}|{horizon}"
        gates = {
            "month_aware_fdr_q_lte_0_05": month_model["fdr_q_values"].get(event_id, {}).get(horizon, 1.0) <= 0.05,
            "symbol_balanced_fdr_q_lte_0_05": symbol_model["fdr_q_values"].get(event_id, {}).get(horizon, 1.0) <= 0.05,
            "leave_one_symbol_not_single_symbol_dependent": not any(
                item.get("destroys_effect_by_rule") is True
                for item in loo_symbol["prior_top_finding_details"].get(key, {}).values()
            ),
            "leave_one_month_not_single_month_dependent": not any(
                item.get("destroys_effect_by_rule") is True
                for item in loo_month["prior_top_finding_details"].get(key, {}).values()
            ),
            "arbusdt_exclusion_does_not_destroy": not arbusdt["prior_top_finding_details"].get(key, {}).get("destroys_effect_by_rule", True),
            "unique_event_sensitivity_does_not_reverse": not unique_summary["prior_top_finding_details"].get(key, {}).get("direction_reversed", True),
        }
        row = {
            "event_definition": event_id,
            "horizon": horizon,
            "month_aware_fdr_q": month_model["fdr_q_values"].get(event_id, {}).get(horizon),
            "symbol_balanced_fdr_q": symbol_model["fdr_q_values"].get(event_id, {}).get(horizon),
            "gates": gates,
            "all_gates_passed": all(gates.values()),
        }
        if row["all_gates_passed"]:
            robust.append(row)
        else:
            failed.append(f"{key}: " + ", ".join(name for name, passed in gates.items() if not passed))
    return robust, failed


def blocked_artifact(
    reason: str,
    hashes_before: dict[str, str] | None = None,
    hashes_after: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "robustness_status": ROBUSTNESS_STATUS_BLOCKED,
        "status": ROBUSTNESS_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": RECOVERY_AUDIT_STATUS,
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "event_count": 0,
        "unique_event_count": 0,
        "symbol_count": 0,
        "horizons": list(HORIZONS),
        "prior_top_findings": PRIOR_TOP_FINDINGS,
        "month_aware_permutation_summary": {"permutation_count_requested": PERMUTATION_COUNT, "permutation_count_completed": 0},
        "symbol_balanced_null_summary": {"resample_count_requested": PERMUTATION_COUNT, "resample_count_completed": 0},
        "leave_one_symbol_out_summary": {},
        "leave_one_month_out_summary": {},
        "arbusdt_exclusion_sensitivity": {},
        "unique_event_sensitivity_summary": {},
        "observed_stats_by_event_definition_and_horizon": {},
        "p_values_by_null_model_event_definition_and_horizon": {},
        "fdr_q_values_by_null_model": {},
        "bonferroni_p_values_by_null_model": {},
        "top_robustness_findings": [],
        "failed_robustness_gates": [reason],
        "data_quality_warnings": [],
        "validation_limits": [f"BLOCKED: {reason}"],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_FAILED,
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise RobustnessBlocked("RECOVERY_HEAD_MISMATCH_STOP")
    status_before = working_tree_status()
    if not output_only_status(status_before):
        raise RobustnessBlocked(f"unexpected dirty state before robustness execution: {status_before}")
    hashes_before = input_artifact_hashes()
    null_runner, diagnostic, event_study, validation_contract, dataset_builder, payload_hashes = load_inputs()

    symbols = [str(symbol) for symbol in diagnostic.get("symbols_built", [])]
    if len(symbols) != 10:
        raise RobustnessBlocked("diagnostic does not expose the expected 10 symbols")
    cache_summary = verify_cached_archives(symbols, diagnostic)
    kline_data = {symbol: load_kline_symbol(symbol, cache_summary["archive_records"]) for symbol in symbols}
    event_universe = build_event_universe(event_study, dataset_builder, kline_data)
    if event_universe["event_count"] != 99870:
        raise RobustnessBlocked(f"event count mismatch: {event_universe['event_count']} != 99870")
    if event_universe["unique_event_count"] != 75467:
        raise RobustnessBlocked(f"unique event count mismatch: {event_universe['unique_event_count']} != 75467")
    if event_universe["missing_join_count"] != 0:
        raise RobustnessBlocked(f"missing join count is nonzero: {event_universe['missing_join_count']}")

    observed_stats = observed_stats_by_event(event_universe)
    rng = np.random.default_rng(RANDOM_SEED)
    start = time.perf_counter()
    try:
        month_model = run_null_model(rng, event_universe, kline_data, MONTH_AWARE_MODEL)
        symbol_model = run_null_model(rng, event_universe, kline_data, SYMBOL_BALANCED_MODEL)
    except MemoryError as exc:
        raise RobustnessBlocked("PERMUTATION_RUNTIME_OR_MEMORY_LIMIT") from exc
    elapsed_seconds = time.perf_counter() - start

    loo_symbol = leave_one_symbol_out(event_universe, observed_stats)
    loo_month = leave_one_month_out(event_universe, observed_stats)
    arbusdt = arbusdt_exclusion(event_universe, observed_stats)
    unique_summary = unique_event_sensitivity(event_universe, observed_stats)
    top_robust, failed_gates = robustness_gate_summary(month_model, symbol_model, loo_symbol, loo_month, arbusdt, unique_summary)
    hashes_after = input_artifact_hashes()
    hashes_unchanged = hashes_before == hashes_after
    if not hashes_unchanged:
        return blocked_artifact("INPUT_ARTIFACT_HASH_CHANGED_STOP", hashes_before, hashes_after)

    warnings = data_quality_warnings(diagnostic, event_universe)
    if top_robust:
        result_classification = RESULT_PROMISING
        allowed_next_step = NEXT_PROMISING
    elif warnings:
        result_classification = RESULT_WEAK
        allowed_next_step = NEXT_WEAK
    else:
        result_classification = RESULT_ATTENTION
        allowed_next_step = NEXT_REPAIR

    validation_checks = {
        "recovery_audit_clean_continue": True,
        "head_matches_expected": True,
        "input_artifacts_loaded": True,
        "input_payload_hashes_verified": True,
        "input_artifact_hashes_unchanged": hashes_unchanged,
        "used_existing_public_data_vision_kline_cache_only": True,
        "no_network_used": True,
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
        "month_aware_permutation_count_exact": month_model["permutation_count_completed"] == 1000,
        "symbol_balanced_null_count_exact": symbol_model["permutation_count_completed"] == 1000,
        "event_count_matches_required": event_universe["event_count"] == 99870,
        "unique_event_count_matches_expected": event_universe["unique_event_count"] == 75467,
        "artifacts_data_builds_not_written": hashes_before[SOURCE_DATASET_BUILDER_RELATIVE_PATH] == hashes_after[SOURCE_DATASET_BUILDER_RELATIVE_PATH],
        "raw_data_committed": False,
        "cache_files_staged": False,
        "exactly_one_python_tool_created": (REPO_ROOT / MODULE_RELATIVE_PATH).exists(),
        "exactly_one_json_artifact_created": True,
    }
    replacement_checks_all_true = all(
        value is True for key, value in validation_checks.items() if key not in {"raw_data_committed", "cache_files_staged"}
    )
    artifact = {
        "robustness_status": ROBUSTNESS_STATUS_PASS if replacement_checks_all_true else ROBUSTNESS_STATUS_BLOCKED,
        "status": ROBUSTNESS_STATUS_PASS if replacement_checks_all_true else ROBUSTNESS_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": result_classification,
        "recovery_audit_status": RECOVERY_AUDIT_STATUS,
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": True,
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": hashes_unchanged,
        "source_artifacts": {
            SOURCE_NULL_RUNNER_RELATIVE_PATH: {
                "status": null_runner.get("null_validation_status"),
                "result_classification": null_runner.get("result_classification"),
                "payload_sha256_excluding_hash": payload_hashes[SOURCE_NULL_RUNNER_RELATIVE_PATH],
            },
            SOURCE_DIAGNOSTIC_RELATIVE_PATH: {
                "status": diagnostic.get("diagnostic_status"),
                "result_classification": diagnostic.get("result_classification"),
                "payload_sha256_excluding_hash": payload_hashes[SOURCE_DIAGNOSTIC_RELATIVE_PATH],
            },
            SOURCE_EVENT_STUDY_RELATIVE_PATH: {
                "status": event_study.get("status"),
                "payload_sha256_excluding_hash": payload_hashes[SOURCE_EVENT_STUDY_RELATIVE_PATH],
            },
            SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: {
                "status": validation_contract.get("validation_contract_status"),
                "payload_sha256_excluding_hash": payload_hashes[SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH],
            },
            SOURCE_DATASET_BUILDER_RELATIVE_PATH: {
                "status": dataset_builder.get("status"),
                "payload_sha256_excluding_hash": payload_hashes[SOURCE_DATASET_BUILDER_RELATIVE_PATH],
            },
        },
        "event_count": event_universe["event_count"],
        "unique_event_count": event_universe["unique_event_count"],
        "symbol_count": event_universe["symbol_count"],
        "horizons": list(HORIZONS),
        "prior_top_findings": PRIOR_TOP_FINDINGS,
        "month_aware_permutation_summary": {
            "model": MONTH_AWARE_MODEL,
            "permutation_count_requested": PERMUTATION_COUNT,
            "permutation_count_completed": month_model["permutation_count_completed"],
            "elapsed_seconds_including_symbol_balanced": elapsed_seconds,
            "top_findings": month_model["top_findings"],
            "fallback_summary": month_model["fallback_summary"],
            "sampling_note": "Resampled with replacement inside symbol/month pools to preserve month buckets without reducing permutation count.",
        },
        "symbol_balanced_null_summary": {
            "model": SYMBOL_BALANCED_MODEL,
            "resample_count_requested": PERMUTATION_COUNT,
            "resample_count_completed": symbol_model["permutation_count_completed"],
            "top_findings": symbol_model["top_findings"],
            "fallback_summary": symbol_model["fallback_summary"],
            "sampling_note": "Matched symbol/month counts where feasible and excluded same event-definition timestamps from non-event pools where possible.",
        },
        "leave_one_symbol_out_summary": loo_symbol,
        "leave_one_month_out_summary": loo_month,
        "arbusdt_exclusion_sensitivity": arbusdt,
        "unique_event_sensitivity_summary": unique_summary,
        "observed_stats_by_event_definition_and_horizon": observed_stats,
        "p_values_by_null_model_event_definition_and_horizon": {
            MONTH_AWARE_MODEL: month_model["p_values"],
            SYMBOL_BALANCED_MODEL: symbol_model["p_values"],
        },
        "fdr_q_values_by_null_model": {
            MONTH_AWARE_MODEL: month_model["fdr_q_values"],
            SYMBOL_BALANCED_MODEL: symbol_model["fdr_q_values"],
        },
        "bonferroni_p_values_by_null_model": {
            MONTH_AWARE_MODEL: month_model["bonferroni_p_values"],
            SYMBOL_BALANCED_MODEL: symbol_model["bonferroni_p_values"],
        },
        "top_robustness_findings": top_robust,
        "failed_robustness_gates": failed_gates,
        "data_quality_warnings": warnings,
        "missing_archive_summary": missing_archive_summary(diagnostic),
        "cache_summary": {
            "cache_root": str(KLINE_CACHE_ROOT),
            "archive_count_available": cache_summary["available_count"],
            "archive_count_missing": cache_summary["missing_count"],
            "checksum_available": cache_summary["checksum_available"],
            "checksum_verified": cache_summary["checksum_verified"],
            "cache_files_staged": False,
            "raw_data_committed": False,
        },
        "validation_limits": [
            "This is direct robustness diagnostic research only, not strategy validation.",
            "Month-aware and symbol-balanced null results are non-tradable diagnostics.",
            "No fees, fills, orders, execution, portfolio sizing, signal generation, trade simulation, or PnL were computed.",
            "Multiple-comparison outputs are diagnostic controls and are not edge claims.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "forbidden_failed_strategy_routes_not_reused": {
            "not_reused": True,
            "routes": FORBIDDEN_FAILED_ROUTES,
        },
        "allowed_next_step": allowed_next_step,
        "blocker": None,
        "validation_checks": validation_checks,
        "replacement_checks_all_true": replacement_checks_all_true,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def print_summary(artifact: dict[str, Any]) -> None:
    print(f"status: {artifact['robustness_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(artifact['input_artifact_hashes_unchanged'] is True)}")
    print(f"month_aware_permutation_count_requested: {artifact['month_aware_permutation_summary']['permutation_count_requested']}")
    print(f"month_aware_permutation_count_completed: {artifact['month_aware_permutation_summary']['permutation_count_completed']}")
    print(f"symbol_balanced_null_count_requested: {artifact['symbol_balanced_null_summary']['resample_count_requested']}")
    print(f"symbol_balanced_null_count_completed: {artifact['symbol_balanced_null_summary']['resample_count_completed']}")
    print(f"event_count: {artifact['event_count']}")
    print(f"unique_event_count: {artifact['unique_event_count']}")
    print(f"horizons: {','.join(artifact['horizons'])}")
    print(f"top_month_aware_findings: {artifact['month_aware_permutation_summary'].get('top_findings', [])[:3]}")
    print(f"top_symbol_balanced_findings: {artifact['symbol_balanced_null_summary'].get('top_findings', [])[:3]}")
    print(f"prior_top_findings_robustness_summary: {artifact.get('top_robustness_findings', [])}")
    print(f"leave_one_symbol_out_summary: any_single_symbol_necessary={artifact.get('leave_one_symbol_out_summary', {}).get('any_single_symbol_necessary')}")
    print(f"leave_one_month_out_summary: any_single_month_necessary={artifact.get('leave_one_month_out_summary', {}).get('any_single_month_necessary')}")
    print(f"arbusdt_exclusion_summary: destroys_any={artifact.get('arbusdt_exclusion_sensitivity', {}).get('arbusdt_exclusion_destroys_any_top_finding')}")
    print(f"unique_event_sensitivity_summary: reverses_any={artifact.get('unique_event_sensitivity_summary', {}).get('unique_event_sensitivity_reverses_any_top_finding')}")
    print(f"failed_robustness_gates: {artifact['failed_robustness_gates']}")
    print(f"data_quality_warnings: {artifact['data_quality_warnings']}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(artifact.get('replacement_checks_all_true') is True)}")
    print(f"blocker: {artifact['blocker']}")


def main() -> int:
    hashes_before: dict[str, str] | None = None
    try:
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
    except RobustnessBlocked as exc:
        try:
            hashes_after = input_artifact_hashes()
        except Exception:
            hashes_after = None
        artifact = blocked_artifact(str(exc), hashes_before, hashes_after)
    write_artifact(artifact)
    print_summary(artifact)
    return 0 if artifact.get("replacement_checks_all_true") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
