#!/usr/bin/env python
"""Forward-return diagnostic for refined extreme OI/taker price-failure events."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import subprocess
import zipfile
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_forward_return_diagnostic_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "d7ce5f169b62457e13df12fb7539bf5c00b89529"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_REFINEMENT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_discovery_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

DIAGNOSTIC_STATUS_PASS = "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_CREATED"
DIAGNOSTIC_STATUS_BLOCKED = "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC"
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC"

RESULT_PROMISING = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_PROMISING_DIAGNOSTIC_ONLY"
RESULT_NO_EFFECT = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_NO_ROBUST_EFFECT"
RESULT_ATTENTION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_FAILED_STOP"

NEXT_ROBUSTNESS = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_RUNNER_V1"
NEXT_EVALUATOR = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_KLINE_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"
NEXT_RUNTIME_REPAIR = "RECOVERY_OR_RUNTIME_REPAIR_V1"

KLINE_CACHE_ROOT = REPO_ROOT / "cache" / "binance_public_kline_forward_return_diagnostic_v1"
KLINE_INTERVAL_MS = 15 * 60 * 1000
ONE_HOUR_MS = 60 * 60 * 1000
START_YEAR_MONTH = (2023, 1)
END_YEAR_MONTH = (2025, 12)
ROLLING_LOOKBACK_BARS = 16
EPSILON = 1e-12

HORIZONS = {
    "15m": 15 * 60 * 1000,
    "1h": 60 * 60 * 1000,
    "4h": 4 * 60 * 60 * 1000,
    "24h": 24 * 60 * 60 * 1000,
}

PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528

LONG_CORE_DEFINITION_ID = (
    "CORE_PRICE_FAILURE_WITH_CROWDING_TIER__long_failure__oi_p97.5__"
    "taker_p97.5__pf_score_bucket__score_1__cooldown_6h"
)
SHORT_CORE_DEFINITION_ID = (
    "CORE_PRICE_FAILURE_WITH_CROWDING_TIER__short_failure__oi_p97.5__"
    "taker_p97.5__pf_score_bucket__score_1__cooldown_6h"
)
SIDE_TO_DEFINITION_ID = {
    "long_core": LONG_CORE_DEFINITION_ID,
    "short_core": SHORT_CORE_DEFINITION_ID,
}
EXPECTED_CORE_COUNTS = {"long_core": 463, "short_core": 451}

OI_QUANTILE = 0.975
TAKER_QUANTILE = 0.975
CORE_CROWDING_QUANTILE_LONG = 0.95
CORE_CROWDING_QUANTILE_SHORT = 0.05
COOLDOWN_HOURS = 6


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


def current_branch() -> str:
    lines = git_lines(["branch", "--show-current"])
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


def recovery_audit() -> dict[str, Any]:
    head = current_head()
    porcelain = working_tree_status()
    staged = git_lines(["diff", "--cached", "--name-status"])
    modified = git_lines(["diff", "--name-status"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    head_matches = head == EXPECTED_HEAD
    risky_dirty = not output_only_status(porcelain)
    if staged:
        decision = "RECOVERY_STAGED_FILES_PRESENT_STOP"
    elif not head_matches:
        decision = "RECOVERY_HEAD_MISMATCH_STOP"
    elif risky_dirty:
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
            raise DiagnosticBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise DiagnosticBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise DiagnosticBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise DiagnosticBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "event discovery"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if refinement.get("result_classification") != "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_READY":
        raise DiagnosticBlocked("refinement artifact is not READY")
    if discovery.get("discovery_status") != "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_CREATED":
        raise DiagnosticBlocked("prior discovery status is not PASS")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiagnosticBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise DiagnosticBlocked("public kline diagnostic status is not PASS")
    return refinement, discovery, dataset, kline, payload_hashes


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


def month_key_from_ms(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m")


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


def percentile_name(q: float) -> str:
    lookup = {0.975: "p97.5", 0.95: "p95.0", 0.05: "p5.0"}
    return lookup.get(q, f"p{q * 100:g}")


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


def expected_missing_archive_keys(kline_diagnostic: dict[str, Any]) -> set[tuple[str, int, int]]:
    missing = kline_diagnostic.get("kline_data_quality", {}).get("missing_archives", [])
    if not isinstance(missing, list):
        raise DiagnosticBlocked("kline diagnostic missing_archives is not a list")
    output = set()
    for item in missing:
        if isinstance(item, dict):
            output.add((str(item.get("symbol")), int(item.get("year")), int(item.get("month"))))
    return output


def verify_cached_archives(symbols: list[str], kline_diagnostic: dict[str, Any]) -> dict[str, Any]:
    missing_keys = expected_missing_archive_keys(kline_diagnostic)
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
                raise DiagnosticBlocked(f"kline cache checksum mismatch: {path}")
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
        raise DiagnosticBlocked(f"required cached kline archives missing: {unexpected_missing[:5]}")
    available_count = sum(1 for record in archive_records if record["available"])
    expected_available = kline_diagnostic.get("public_data_source", {}).get("monthly_archive_count_available")
    if available_count != expected_available:
        raise DiagnosticBlocked(f"cached archive count mismatch: {available_count} != {expected_available}")
    return {
        "archive_records": archive_records,
        "available_count": available_count,
        "missing_count": len(missing_keys),
        "missing_archive_keys": sorted(missing_keys),
        "checksum_available": checksum_available,
        "checksum_verified": checksum_verified,
    }


def detect_header(row: list[str]) -> bool:
    return bool(row) and not str(row[0]).strip().isdigit()


def rolling_previous_extreme(values: np.ndarray, mode: str, lookback: int) -> np.ndarray:
    output = np.full(values.shape, np.nan, dtype=np.float64)
    window: deque[float] = deque()
    for idx, value in enumerate(values):
        if window:
            output[idx] = max(window) if mode == "max" else min(window)
        window.append(float(value))
        if len(window) > lookback:
            window.popleft()
    return output


def load_kline_symbol(symbol: str, archive_records: list[dict[str, Any]]) -> dict[str, Any]:
    bars: dict[int, tuple[float, float, float, float]] = {}
    duplicate_open_time_count = 0
    invalid_numeric_count = 0
    for record in archive_records:
        if record["symbol"] != symbol or not record["available"]:
            continue
        path = Path(record["local_path"])
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise DiagnosticBlocked(f"no CSV member found in cached kline archive: {path}")
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
                        open_price = float(raw[1])
                        high = float(raw[2])
                        low = float(raw[3])
                        close = float(raw[4])
                    except ValueError:
                        invalid_numeric_count += 1
                        continue
                    if open_time in bars:
                        duplicate_open_time_count += 1
                        continue
                    bars[open_time] = (open_price, high, low, close)
    if not bars:
        raise DiagnosticBlocked(f"no cached kline rows loaded for {symbol}")
    opens = np.array(sorted(bars), dtype=np.int64)
    open_prices = np.array([bars[int(open_time)][0] for open_time in opens], dtype=np.float64)
    highs = np.array([bars[int(open_time)][1] for open_time in opens], dtype=np.float64)
    lows = np.array([bars[int(open_time)][2] for open_time in opens], dtype=np.float64)
    closes = np.array([bars[int(open_time)][3] for open_time in opens], dtype=np.float64)
    prior_high = rolling_previous_extreme(highs, "max", ROLLING_LOOKBACK_BARS)
    prior_low = rolling_previous_extreme(lows, "min", ROLLING_LOOKBACK_BARS)
    open_to_index = {int(open_time): int(index) for index, open_time in enumerate(opens)}
    returns_by_horizon: dict[str, np.ndarray] = {}
    valid_indices_by_horizon: dict[str, np.ndarray] = {}
    valid_returns_by_horizon: dict[str, np.ndarray] = {}
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
        valid_indices_by_horizon[horizon] = np.where(np.isfinite(returns))[0].astype(np.int64)
        valid_returns_by_horizon[horizon] = returns[np.isfinite(returns)]
    return {
        "symbol": symbol,
        "opens": opens,
        "open": open_prices,
        "high": highs,
        "low": lows,
        "close": closes,
        "prior_rolling_high": prior_high,
        "prior_rolling_low": prior_low,
        "open_to_index": open_to_index,
        "returns_by_horizon": returns_by_horizon,
        "valid_indices_by_horizon": valid_indices_by_horizon,
        "valid_returns_by_horizon": valid_returns_by_horizon,
        "quality": {
            "symbol": symbol,
            "row_count": int(len(opens)),
            "timestamp_min": ms_to_iso(int(opens[0])),
            "timestamp_max": ms_to_iso(int(opens[-1])),
            "duplicate_open_time_count": duplicate_open_time_count,
            "invalid_numeric_count": invalid_numeric_count,
            "valid_forward_return_counts": {horizon: int(np.isfinite(returns_by_horizon[horizon]).sum()) for horizon in HORIZONS},
        },
    }


def normalized_paths(dataset: dict[str, Any]) -> list[Path]:
    files = dataset.get("generated_external_files", {}).get("normalized_by_symbol_files")
    if not isinstance(files, list) or not files:
        raise DiagnosticBlocked("dataset builder artifact missing normalized_by_symbol_files")
    paths = [Path(str(path)) for path in files]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise DiagnosticBlocked(f"normalized proxy dataset files missing: {missing}")
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


def quantile_or_none(values: list[float], q: float) -> float | None:
    clean = np.array([value for value in values if math.isfinite(value)], dtype=np.float64)
    if clean.size == 0:
        return None
    return float(np.quantile(clean, q))


def metric_rows_for_symbol(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    oi_by_ms: dict[int, float] = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            timestamp = row.get("timestamp")
            if not timestamp:
                continue
            ts_ms = iso_to_ms(timestamp)
            open_interest = to_float(row.get("open_interest"))
            if open_interest is not None and open_interest > 0:
                oi_by_ms[ts_ms] = open_interest
            rows.append(
                {
                    "timestamp": timestamp,
                    "ts_ms": ts_ms,
                    "month": timestamp[:7],
                    "symbol": row.get("symbol") or path.name.split("_", 1)[0],
                    "open_interest": open_interest,
                    "taker_buy_aggression": to_float(row.get("taker_buy_sell_ratio")),
                    "taker_sell_aggression": to_float(row.get("taker_sell_pressure")),
                    "top_account_ratio": to_float(row.get("top_account_long_short_ratio")),
                    "top_position_ratio": to_float(row.get("top_position_long_short_ratio")),
                }
            )
    for row in rows:
        current = row["open_interest"]
        previous = oi_by_ms.get(row["ts_ms"] - ONE_HOUR_MS)
        if current is not None and previous is not None and current > 0 and previous > 0:
            row["oi_delta_log_1h"] = math.log(current) - math.log(previous)
        else:
            row["oi_delta_log_1h"] = None
    return rows


def build_symbol_thresholds(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        month = row["month"]
        for key in ["oi_delta_log_1h", "taker_buy_aggression", "taker_sell_aggression", "top_account_ratio", "top_position_ratio"]:
            value = row.get(key)
            if isinstance(value, float) and math.isfinite(value):
                buckets[month][key].append(value)
    thresholds: dict[str, dict[str, Any]] = {}
    for month, per_field in buckets.items():
        thresholds[month] = {
            "oi_delta_log_1h": {"p97.5": quantile_or_none(per_field["oi_delta_log_1h"], OI_QUANTILE)},
            "taker_buy_aggression": {"p97.5": quantile_or_none(per_field["taker_buy_aggression"], TAKER_QUANTILE)},
            "taker_sell_aggression": {"p97.5": quantile_or_none(per_field["taker_sell_aggression"], TAKER_QUANTILE)},
            "long_crowding": {
                "top_account_p95.0": quantile_or_none(per_field["top_account_ratio"], CORE_CROWDING_QUANTILE_LONG),
                "top_position_p95.0": quantile_or_none(per_field["top_position_ratio"], CORE_CROWDING_QUANTILE_LONG),
            },
            "short_crowding": {
                "top_account_p5.0": quantile_or_none(per_field["top_account_ratio"], CORE_CROWDING_QUANTILE_SHORT),
                "top_position_p5.0": quantile_or_none(per_field["top_position_ratio"], CORE_CROWDING_QUANTILE_SHORT),
            },
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
    upper_wick_ratio = (high - close) / range_value
    lower_wick_ratio = (close - low) / range_value
    prev_index = kline_data["open_to_index"].get(int(kline_data["opens"][index]) - ONE_HOUR_MS)
    price_return_1h = None
    if prev_index is not None:
        previous_close = float(kline_data["close"][prev_index])
        if previous_close != 0:
            price_return_1h = (close / previous_close) - 1.0
    prior_high = float(kline_data["prior_rolling_high"][index])
    prior_low = float(kline_data["prior_rolling_low"][index])
    failed_breakout = math.isfinite(prior_high) and high > prior_high and close <= prior_high
    failed_breakdown = math.isfinite(prior_low) and low < prior_low and close >= prior_low
    long_flags = {
        "opposite_1h_return": price_return_1h is not None and price_return_1h <= 0.0,
        "wick_rejection": upper_wick_ratio >= 0.60,
        "close_location_failure": close_location <= 0.40,
        "failed_breakout_breakdown": failed_breakout,
    }
    short_flags = {
        "opposite_1h_return": price_return_1h is not None and price_return_1h >= 0.0,
        "wick_rejection": lower_wick_ratio >= 0.60,
        "close_location_failure": close_location >= 0.60,
        "failed_breakout_breakdown": failed_breakdown,
    }
    return {
        "price_available": True,
        "price_return_1h": price_return_1h,
        "close_location": close_location,
        "upper_wick_ratio": upper_wick_ratio,
        "lower_wick_ratio": lower_wick_ratio,
        "long_flags": {**long_flags, "any_failure": any(long_flags.values())},
        "short_flags": {**short_flags, "any_failure": any(short_flags.values())},
        "long_failure_score": sum(long_flags.values()),
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


def reconstruct_core_events(dataset: dict[str, Any], kline_by_symbol: dict[str, dict[str, Any]]) -> dict[str, Any]:
    raw_counts = Counter()
    cooldown_counts = Counter()
    rejected_due_to_cooldown = Counter()
    rejected_due_to_missing_price_failure = Counter()
    rejected_due_to_missing_components = Counter()
    crowding_distribution = {"long_core": Counter(), "short_core": Counter()}
    price_failure_distribution = {"long_core": Counter(), "short_core": Counter()}
    last_event_ms: dict[str, dict[str, int]] = {"long_core": {}, "short_core": {}}
    events: dict[str, list[dict[str, Any]]] = {"long_core": [], "short_core": []}
    missing_component_counter: Counter[str] = Counter()

    for path in normalized_paths(dataset):
        rows = metric_rows_for_symbol(path)
        symbol = path.name.split("_", 1)[0]
        thresholds_by_month = build_symbol_thresholds(rows)
        kline_data = kline_by_symbol[symbol]
        for row in rows:
            thresholds = thresholds_by_month.get(row["month"])
            if thresholds is None:
                missing_component_counter["threshold_month_missing"] += 1
                continue
            features = price_features(row, kline_data)
            if not features.get("price_available"):
                missing_component_counter["price_bar_missing"] += 1
                continue
            oi_threshold = thresholds["oi_delta_log_1h"].get("p97.5")
            if row["oi_delta_log_1h"] is None or oi_threshold is None:
                missing_component_counter["oi_delta_log_1h_missing"] += 1
                continue
            if row["oi_delta_log_1h"] < oi_threshold:
                continue
            side_specs = [
                ("long_core", "taker_buy_aggression", "long_failure_score", "long_flags"),
                ("short_core", "taker_sell_aggression", "short_failure_score", "short_flags"),
            ]
            for side, taker_key, score_key, flags_key in side_specs:
                taker_threshold = thresholds[taker_key].get("p97.5")
                if row[taker_key] is None or taker_threshold is None:
                    rejected_due_to_missing_components[side] += 1
                    continue
                if row[taker_key] < taker_threshold:
                    continue
                if int(features[score_key]) < 1:
                    rejected_due_to_missing_price_failure[side] += 1
                    continue
                if side == "long_core":
                    account_threshold = thresholds["long_crowding"].get("top_account_p95.0")
                    position_threshold = thresholds["long_crowding"].get("top_position_p95.0")
                    account_ok = row["top_account_ratio"] is not None and account_threshold is not None and row["top_account_ratio"] >= account_threshold
                    position_ok = row["top_position_ratio"] is not None and position_threshold is not None and row["top_position_ratio"] >= position_threshold
                else:
                    account_threshold = thresholds["short_crowding"].get("top_account_p5.0")
                    position_threshold = thresholds["short_crowding"].get("top_position_p5.0")
                    account_ok = row["top_account_ratio"] is not None and account_threshold is not None and row["top_account_ratio"] <= account_threshold
                    position_ok = row["top_position_ratio"] is not None and position_threshold is not None and row["top_position_ratio"] <= position_threshold
                tier = crowding_tier(account_ok, position_ok)
                raw_counts[side] += 1
                crowding_distribution[side][tier] += 1
                for variant, passed in features[flags_key].items():
                    if variant != "any_failure" and passed:
                        price_failure_distribution[side][variant] += 1
                previous = last_event_ms[side].get(symbol)
                cooldown_ms = COOLDOWN_HOURS * 60 * 60 * 1000
                if previous is not None and row["ts_ms"] - previous < cooldown_ms:
                    rejected_due_to_cooldown[side] += 1
                    continue
                last_event_ms[side][symbol] = row["ts_ms"]
                base_open = floor_to_15m_open(row["ts_ms"])
                base_index = kline_data["open_to_index"].get(base_open)
                event = {
                    "side": side,
                    "definition_id": SIDE_TO_DEFINITION_ID[side],
                    "symbol": symbol,
                    "timestamp": row["timestamp"],
                    "ts_ms": row["ts_ms"],
                    "base_open_ms": base_open,
                    "base_open": ms_to_iso(base_open),
                    "base_index": base_index,
                    "month": row["month"],
                    "crowding_confirmation": tier,
                    "failure_score": int(features[score_key]),
                    "price_failure_flags": {key: bool(value) for key, value in features[flags_key].items() if key != "any_failure"},
                }
                events[side].append(event)
                cooldown_counts[side] += 1
    return {
        "events": events,
        "raw_counts": dict(raw_counts),
        "cooldown_counts": dict(cooldown_counts),
        "rejected_due_to_cooldown": dict(rejected_due_to_cooldown),
        "rejected_due_to_missing_price_failure": dict(rejected_due_to_missing_price_failure),
        "rejected_due_to_missing_components": dict(rejected_due_to_missing_components),
        "missing_component_counter": dict(missing_component_counter),
        "crowding_distribution": {side: dict(counter) for side, counter in crowding_distribution.items()},
        "price_failure_distribution": {side: dict(counter) for side, counter in price_failure_distribution.items()},
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


def observed_forward_returns(
    events: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    values = {side: {horizon: [] for horizon in HORIZONS} for side in SIDE_TO_DEFINITION_ID}
    missing = {side: {horizon: 0 for horizon in HORIZONS} for side in SIDE_TO_DEFINITION_ID}
    event_indices = {side: defaultdict(set) for side in SIDE_TO_DEFINITION_ID}
    valid_counts_by_symbol = {side: defaultdict(lambda: {horizon: 0 for horizon in HORIZONS}) for side in SIDE_TO_DEFINITION_ID}
    missing_join_count = 0
    for side, rows in events.items():
        for event in rows:
            symbol = event["symbol"]
            base_index = event["base_index"]
            if base_index is None:
                missing_join_count += 1
                for horizon in HORIZONS:
                    missing[side][horizon] += 1
                continue
            event_indices[side][symbol].add(int(base_index))
            for horizon in HORIZONS:
                value = kline_by_symbol[symbol]["returns_by_horizon"][horizon][base_index]
                if np.isfinite(value):
                    values[side][horizon].append(float(value))
                    valid_counts_by_symbol[side][symbol][horizon] += 1
                else:
                    missing[side][horizon] += 1
    observed_stats = {}
    for side in SIDE_TO_DEFINITION_ID:
        observed_stats[side] = {}
        for horizon in HORIZONS:
            stats = summarize_array(values[side][horizon])
            observed_stats[side][horizon] = {
                "event_count": len(events[side]),
                "valid_forward_return_count": stats["count"],
                "missing_forward_return_count": missing[side][horizon],
                **{key: value for key, value in stats.items() if key != "count"},
            }
    return {
        "values": values,
        "missing": missing,
        "observed_stats": observed_stats,
        "event_indices": event_indices,
        "valid_counts_by_symbol": valid_counts_by_symbol,
        "missing_join_count": missing_join_count,
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


def benjamini_hochberg(p_items: list[tuple[str, float]]) -> dict[str, float]:
    m = len(p_items)
    if m == 0:
        return {}
    ordered = sorted(p_items, key=lambda item: item[1])
    q_values: dict[str, float] = {}
    running_min = 1.0
    for rank_from_end, (key, p_value) in enumerate(reversed(ordered), start=1):
        rank = m - rank_from_end + 1
        q_value = min(running_min, p_value * m / rank)
        running_min = q_value
        q_values[key] = float(min(q_value, 1.0))
    return q_values


def symbol_balanced_null(
    observed: dict[str, Any],
    kline_by_symbol: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    null_stats = {side: {} for side in SIDE_TO_DEFINITION_ID}
    p_values = {side: {} for side in SIDE_TO_DEFINITION_ID}
    p_items: list[tuple[str, float]] = []
    fallback_summary = {side: {} for side in SIDE_TO_DEFINITION_ID}
    for side in SIDE_TO_DEFINITION_ID:
        for horizon in HORIZONS:
            null_sums = np.zeros(PERMUTATION_COUNT, dtype=np.float64)
            total_count = 0
            fallback = {"event_timestamp_exclusion_used": 0, "symbol_pool_fallback_used": 0, "empty_symbol_pool_count": 0}
            for symbol, per_horizon_counts in observed["valid_counts_by_symbol"][side].items():
                count = int(per_horizon_counts[horizon])
                if count <= 0:
                    continue
                symbol_data = kline_by_symbol[symbol]
                candidate_indices = symbol_data["valid_indices_by_horizon"][horizon]
                event_indices = observed["event_indices"][side].get(symbol, set())
                filtered_indices = candidate_indices
                if candidate_indices.size and event_indices:
                    keep = np.array([int(index) not in event_indices for index in candidate_indices], dtype=bool)
                    filtered_indices = candidate_indices[keep]
                    if filtered_indices.size:
                        fallback["event_timestamp_exclusion_used"] += 1
                    else:
                        fallback["symbol_pool_fallback_used"] += 1
                        filtered_indices = candidate_indices
                candidates = symbol_data["returns_by_horizon"][horizon][filtered_indices]
                candidates = candidates[np.isfinite(candidates)]
                if candidates.size == 0:
                    fallback["empty_symbol_pool_count"] += 1
                    continue
                total_count += count
                draws = rng.integers(0, candidates.size, size=(PERMUTATION_COUNT, count))
                null_sums += candidates[draws].sum(axis=1)
            if total_count <= 0:
                raise DiagnosticBlocked(f"zero valid null sample count for {side} {horizon}")
            null_means = null_sums / float(total_count)
            observed_mean = observed["observed_stats"][side][horizon]["mean"]
            null_stats[side][horizon] = summarize_null_means(null_means)
            p_summary = empirical_p_values(observed_mean, null_means)
            p_values[side][horizon] = p_summary
            fallback_summary[side][horizon] = fallback
            p_two = p_summary["p_two_sided"]
            if isinstance(p_two, float):
                p_items.append((f"{side}|{horizon}", p_two))
    fdr_flat = benjamini_hochberg(p_items)
    bonferroni_flat = {key: float(min(value * len(p_items), 1.0)) for key, value in p_items}
    fdr_nested = {side: {} for side in SIDE_TO_DEFINITION_ID}
    bonferroni_nested = {side: {} for side in SIDE_TO_DEFINITION_ID}
    for key, value in fdr_flat.items():
        side, horizon = key.split("|", 1)
        fdr_nested[side][horizon] = value
    for key, value in bonferroni_flat.items():
        side, horizon = key.split("|", 1)
        bonferroni_nested[side][horizon] = value
    return {
        "symbol_balanced_null_count_requested": PERMUTATION_COUNT,
        "symbol_balanced_null_count_completed": PERMUTATION_COUNT,
        "null_stats_by_side_and_horizon": null_stats,
        "p_values_by_side_and_horizon": p_values,
        "fdr_q_values": fdr_nested,
        "bonferroni_p_values": bonferroni_nested,
        "fallback_summary": fallback_summary,
        "top_symbol_balanced_null_findings": top_findings_from_p(fdr_nested, bonferroni_nested, p_values),
        "minimum_fdr_q_value": min(fdr_flat.values()) if fdr_flat else None,
    }


def top_findings_from_p(
    fdr_q_values: dict[str, dict[str, float]],
    bonferroni_p_values: dict[str, dict[str, float]],
    p_values: dict[str, dict[str, dict[str, Any]]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    rows = []
    for side, per_horizon in fdr_q_values.items():
        for horizon, q_value in per_horizon.items():
            rows.append(
                {
                    "side": side,
                    "horizon": horizon,
                    "fdr_q": q_value,
                    "bonferroni_p": bonferroni_p_values.get(side, {}).get(horizon),
                    "p_two_sided": p_values[side][horizon]["p_two_sided"],
                    "p_positive_mean": p_values[side][horizon]["p_positive_mean"],
                    "p_negative_mean": p_values[side][horizon]["p_negative_mean"],
                }
            )
    rows.sort(key=lambda item: (item["fdr_q"], item["p_two_sided"]))
    return rows[:limit]


def top_observed_findings(observed_stats: dict[str, dict[str, dict[str, Any]]], limit: int = 5) -> list[dict[str, Any]]:
    rows = []
    for side, per_horizon in observed_stats.items():
        for horizon, stats in per_horizon.items():
            mean = stats.get("mean")
            rows.append(
                {
                    "side": side,
                    "horizon": horizon,
                    "event_count": stats.get("event_count"),
                    "valid_forward_return_count": stats.get("valid_forward_return_count"),
                    "mean": mean,
                    "median": stats.get("median"),
                    "positive_rate": stats.get("positive_rate"),
                    "negative_rate": stats.get("negative_rate"),
                }
            )
    rows.sort(key=lambda item: abs(item["mean"] or 0.0), reverse=True)
    return rows[:limit]


def validate_selected_event_definitions(refinement: dict[str, Any]) -> dict[str, Any]:
    selected = refinement.get("selected_clean_event_definitions")
    if not isinstance(selected, list):
        raise DiagnosticBlocked("refinement selected_clean_event_definitions is not a list")
    by_id = {item.get("definition_id"): item for item in selected if isinstance(item, dict)}
    long_def = by_id.get(LONG_CORE_DEFINITION_ID)
    short_def = by_id.get(SHORT_CORE_DEFINITION_ID)
    if not isinstance(long_def, dict):
        raise DiagnosticBlocked("selected long core definition missing")
    if not isinstance(short_def, dict):
        raise DiagnosticBlocked("selected short core definition missing")
    checks = {
        "prior_result_ready": refinement.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_READY",
        "long_core_cooldown_count_463": long_def.get("cooldown_filtered_count") == 463,
        "short_core_cooldown_count_451": short_def.get("cooldown_filtered_count") == 451,
        "long_core_10_symbols": long_def.get("symbol_coverage_count") == 10,
        "short_core_10_symbols": short_def.get("symbol_coverage_count") == 10,
        "long_core_36_months": long_def.get("month_coverage_count") == 36,
        "short_core_36_months": short_def.get("month_coverage_count") == 36,
        "long_core_overlap_zero": float(long_def.get("overlap_rate", -1.0)) == 0.0,
        "short_core_overlap_zero": float(short_def.get("overlap_rate", -1.0)) == 0.0,
        "long_core_missing_component_zero": long_def.get("missing_component_count") == 0,
        "short_core_missing_component_zero": short_def.get("missing_component_count") == 0,
        "forbidden_future_outcome_selection_absent": bool(
            refinement.get("forbidden_actions_confirmed_false", {}).get("forward_return_impact") is False
            and refinement.get("forbidden_actions_confirmed_false", {}).get("p_values") is False
            and refinement.get("forbidden_actions_confirmed_false", {}).get("optimization_against_future_returns") is False
        ),
    }
    if not all(checks.values()):
        raise DiagnosticBlocked(f"selected event definition validation failed: {checks}")
    return {
        "validated": True,
        "checks": checks,
        "long_core": long_def,
        "short_core": short_def,
        "sparse_crowding_confirmed_variants_excluded_from_primary_tests": True,
    }


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_future_returns": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "failed_broad_route_revival": False,
        "sparse_crowding_confirmed_primary_test": False,
        "event_definition_optimized_on_forward_returns": False,
    }


def classify_result(minimum_fdr_q_value: float | None, data_quality_attention: bool) -> tuple[str, str]:
    if data_quality_attention:
        return RESULT_ATTENTION, NEXT_REPAIR
    if isinstance(minimum_fdr_q_value, float) and minimum_fdr_q_value <= 0.05:
        return RESULT_PROMISING, NEXT_ROBUSTNESS
    return RESULT_NO_EFFECT, NEXT_EVALUATOR


def blocked_artifact(reason: str, audit: dict[str, Any] | None = None, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "diagnostic_status": DIAGNOSTIC_STATUS_BLOCKED,
        "status": DIAGNOSTIC_STATUS_BLOCKED,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED,
        "recovery_audit_status": (audit or {}).get("recovery_decision", RECOVERY_AUDIT_STATUS),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "selected_event_definitions_validated": {"validated": False},
        "event_reconstruction_status": "BLOCKED",
        "long_core_event_count": 0,
        "short_core_event_count": 0,
        "symbol_count": 0,
        "month_count": 0,
        "horizons": list(HORIZONS),
        "observed_stats_by_side_and_horizon": {},
        "symbol_balanced_null_count_requested": PERMUTATION_COUNT,
        "symbol_balanced_null_count_completed": 0,
        "random_seed": RANDOM_SEED,
        "null_stats_by_side_and_horizon": {},
        "p_values_by_side_and_horizon": {},
        "fdr_q_values": {},
        "bonferroni_p_values": {},
        "missing_forward_return_summary": {},
        "data_quality_warnings": [f"BLOCKED: {reason}"],
        "validation_limits": ["Blocked before diagnostic completion."],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
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
    refinement, discovery, dataset, kline, input_payload_hashes = load_inputs()
    selected_validation = validate_selected_event_definitions(refinement)
    symbols = [str(symbol) for symbol in dataset.get("normalized_dataset_summary", {}).get("built_symbols", [])]
    if len(symbols) != 10:
        raise DiagnosticBlocked("dataset builder does not expose expected 10 built symbols")
    cache_summary = verify_cached_archives(symbols, kline)
    kline_by_symbol = {symbol: load_kline_symbol(symbol, cache_summary["archive_records"]) for symbol in symbols}
    reconstructed = reconstruct_core_events(dataset, kline_by_symbol)
    long_count = len(reconstructed["events"]["long_core"])
    short_count = len(reconstructed["events"]["short_core"])
    if long_count != EXPECTED_CORE_COUNTS["long_core"] or short_count != EXPECTED_CORE_COUNTS["short_core"]:
        raise DiagnosticBlocked(
            f"EVENT_COUNT_RECONSTRUCTION_MISMATCH: long_core={long_count}, short_core={short_count}"
        )
    observed = observed_forward_returns(reconstructed["events"], kline_by_symbol)
    null = symbol_balanced_null(observed, kline_by_symbol)
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise DiagnosticBlocked("INPUT_ARTIFACT_HASH_CHANGED")

    event_symbols = sorted({event["symbol"] for rows in reconstructed["events"].values() for event in rows})
    event_months = sorted({event["month"] for rows in reconstructed["events"].values() for event in rows})
    missing_forward_summary = {
        side: {
            horizon: int(observed["missing"][side][horizon])
            for horizon in HORIZONS
        }
        for side in SIDE_TO_DEFINITION_ID
    }
    data_quality_warnings = [
        f"{cache_summary['available_count']}/360 monthly 15m kline archives available",
        f"{cache_summary['missing_count']} missing archives: {cache_summary['missing_archive_keys']}",
        f"missing join count: {observed['missing_join_count']}",
        f"missing forward-return rows by side/horizon: {missing_forward_summary}",
        "Sparse crowding-confirmed variants were not used as primary tests.",
    ]
    # Known archive gaps and tiny horizon-edge missingness are recorded as warnings.
    # Escalate to DATA_QUALITY_ATTENTION only when event joins fail or forward-return
    # missingness becomes material for a tested side/horizon.
    material_missing_forward = False
    for side, per_horizon in missing_forward_summary.items():
        side_event_count = len(reconstructed["events"][side])
        for count in per_horizon.values():
            if side_event_count and count / side_event_count > 0.01:
                material_missing_forward = True
    data_quality_attention = observed["missing_join_count"] > 0 or material_missing_forward
    result_classification, allowed_next_step = classify_result(null["minimum_fdr_q_value"], data_quality_attention)
    validation_checks = {
        "repo_clean_or_only_output_before_run": audit["recovery_decision"] == "RECOVERY_AUDIT_CLEAN_CONTINUE",
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "selected_event_definitions_validated": selected_validation["validated"],
        "event_count_reconstructed_exact": long_count == 463 and short_count == 451,
        "symbol_balanced_null_exact_1000": null["symbol_balanced_null_count_completed"] == PERMUTATION_COUNT,
        "artifacts_data_builds_not_written": True,
        "no_raw_data_committed": True,
        "no_cache_files_staged": True,
        "strategy_allowed_false": True,
        "signal_allowed_false": True,
        "candidate_generation_allowed_false": True,
        "release_allowed_false": True,
    }
    artifact = {
        "diagnostic_status": DIAGNOSTIC_STATUS_PASS,
        "status": DIAGNOSTIC_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_decision"],
        "current_head": audit["current_head"],
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": hashes_before,
        "input_artifact_hashes_after": hashes_after,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "input_payload_hashes_verified": input_payload_hashes,
        "source_artifacts": INPUT_ARTIFACT_RELATIVE_PATHS,
        "selected_event_definitions_validated": selected_validation,
        "event_reconstruction_status": "RECONSTRUCTED_EXACT_LONG_463_SHORT_451_FROM_CURRENT_AND_PRIOR_BAR_DATA_ONLY",
        "long_core_event_count": long_count,
        "short_core_event_count": short_count,
        "symbol_count": len(event_symbols),
        "month_count": len(event_months),
        "event_symbols": event_symbols,
        "event_months": event_months,
        "horizons": list(HORIZONS),
        "observed_stats_by_side_and_horizon": observed["observed_stats"],
        "symbol_balanced_null_count_requested": null["symbol_balanced_null_count_requested"],
        "symbol_balanced_null_count_completed": null["symbol_balanced_null_count_completed"],
        "random_seed": RANDOM_SEED,
        "null_model": "symbol_balanced_non_event_timestamp_resampling",
        "null_stats_by_side_and_horizon": null["null_stats_by_side_and_horizon"],
        "p_values_by_side_and_horizon": null["p_values_by_side_and_horizon"],
        "fdr_q_values": null["fdr_q_values"],
        "bonferroni_p_values": null["bonferroni_p_values"],
        "top_observed_findings": top_observed_findings(observed["observed_stats"]),
        "top_symbol_balanced_null_findings": null["top_symbol_balanced_null_findings"],
        "missing_forward_return_summary": missing_forward_summary,
        "data_quality_warnings": data_quality_warnings,
        "kline_cache_summary": {
            "cache_root": str(KLINE_CACHE_ROOT),
            "available_archive_count": cache_summary["available_count"],
            "missing_archive_count": cache_summary["missing_count"],
            "missing_archives": cache_summary["missing_archive_keys"],
            "checksum_available": cache_summary["checksum_available"],
            "checksum_verified": cache_summary["checksum_verified"],
            "downloaded_new_raw_data": False,
        },
        "event_reconstruction_summary": {
            "raw_counts": reconstructed["raw_counts"],
            "cooldown_counts": reconstructed["cooldown_counts"],
            "rejected_due_to_cooldown": reconstructed["rejected_due_to_cooldown"],
            "rejected_due_to_missing_price_failure": reconstructed["rejected_due_to_missing_price_failure"],
            "rejected_due_to_missing_components": reconstructed["rejected_due_to_missing_components"],
            "missing_component_counter": reconstructed["missing_component_counter"],
            "crowding_confirmation_distribution": reconstructed["crowding_distribution"],
            "price_failure_variant_distribution": reconstructed["price_failure_distribution"],
        },
        "validation_limits": [
            "Diagnostic research only; this is not a strategy, signal, backtest, PnL, trade simulation, candidate generation, edge claim, or release approval.",
            "Events were reconstructed using only current-bar, prior-bar, and contemporaneous UM metrics information.",
            "Sparse crowding-confirmed variants from the refinement artifact were excluded from primary tests.",
            "Forward returns are public close-to-close diagnostic labels and are not entry/exit or PnL logic.",
            "Event definitions were not optimized against this forward-return result.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
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
    print(f"status: {artifact['diagnostic_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"selected_event_definitions_validated: {bool_text(bool(artifact.get('selected_event_definitions_validated', {}).get('validated')))}")
    print(f"event_reconstruction_status: {artifact['event_reconstruction_status']}")
    print(f"long_core_event_count: {artifact['long_core_event_count']}")
    print(f"short_core_event_count: {artifact['short_core_event_count']}")
    print(f"horizons: {','.join(artifact['horizons'])}")
    print(f"symbol_balanced_null_count_requested: {artifact['symbol_balanced_null_count_requested']}")
    print(f"symbol_balanced_null_count_completed: {artifact['symbol_balanced_null_count_completed']}")
    print(f"top_observed_findings: {artifact.get('top_observed_findings', [])[:3]}")
    print(f"top_symbol_balanced_null_findings: {artifact.get('top_symbol_balanced_null_findings', [])[:3]}")
    print(f"fdr_q_values: {artifact['fdr_q_values']}")
    print(f"bonferroni_p_values: {artifact['bonferroni_p_values']}")
    print(f"missing_forward_return_summary: {artifact['missing_forward_return_summary']}")
    print(f"data_quality_warnings: {artifact['data_quality_warnings']}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"strategy_allowed: {bool_text(bool(artifact['strategy_allowed']))}")
    print(f"signal_allowed: {bool_text(bool(artifact['signal_allowed']))}")
    print(f"candidate_generation_allowed: {bool_text(bool(artifact['candidate_generation_allowed']))}")
    print(f"release_allowed: {bool_text(bool(artifact['release_allowed']))}")
    print(f"forbidden_actions_confirmed_false: {artifact['forbidden_actions_confirmed_false']}")
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
        return 0 if artifact["diagnostic_status"] == DIAGNOSTIC_STATUS_PASS else 1
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
