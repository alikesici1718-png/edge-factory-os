#!/usr/bin/env python
"""Outcome-blind OI contraction plus taker capitulation price-rejection discovery."""

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
MODULE = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "4787005c26cc922f0292bd506cbf8585f46122e5"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

DISCOVERY_STATUS_PASS = "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_CREATED"
DISCOVERY_STATUS_BLOCKED = "BLOCKED_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY"
ARTIFACT_KIND = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY"

RESULT_READY = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_READY"
RESULT_TOO_SPARSE = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_TOO_SPARSE"
RESULT_TOO_BROAD = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_TOO_BROAD"
RESULT_ATTENTION = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DISCOVERY_FAILED_STOP"

NEXT_VALIDATOR = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_V1"
NEXT_REFINEMENT = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_DEFINITION_REFINEMENT_V1"

THEORY_ID = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION"
KLINE_CACHE_ROOT = REPO_ROOT / "cache" / "binance_public_kline_forward_return_diagnostic_v1"
KLINE_INTERVAL_MS = 15 * 60 * 1000
ONE_HOUR_MS = 60 * 60 * 1000
START_YEAR_MONTH = (2023, 1)
END_YEAR_MONTH = (2025, 12)
ROLLING_LOOKBACK_BARS = 16
EPSILON = 1e-12

OI_CONTRACTION_QUANTILES = [0.01, 0.005, 0.0025]
TAKER_PRESSURE_QUANTILES = [0.99, 0.995, 0.9975]
REJECTION_SCORE_BUCKETS = [1, 2, 3]
COOLDOWN_HOURS = [6, 12, 24]

EVENT_FAMILIES = {
    "LONG_CAPITULATION_REBOUND_CANDIDATE": {
        "side": "long_capitulation",
        "taker_key": "taker_sell_pressure",
        "mechanic": "OI contracts sharply, taker sell pressure is extreme, and the current/prior price bar shows downside rejection.",
    },
    "SHORT_COVER_EXHAUSTION_DOWNSIDE_CANDIDATE": {
        "side": "short_cover_exhaustion",
        "taker_key": "taker_buy_pressure",
        "mechanic": "OI contracts sharply, taker buy pressure is extreme, and the current/prior price bar shows upside rejection.",
    },
}

FORBIDDEN_FAILED_ROUTES = [
    "broad OI/taker/crowding forward-return route",
    "funding crowding reversal",
    "funding carry",
    "funding extreme volume surge",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
    "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC as live/candidate route",
]


class DiscoveryBlocked(Exception):
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
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={REPO_ROOT}", *args],
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
        raise DiscoveryBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
        if line.startswith("!! ") and line[3:].startswith("cache/"):
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
            raise DiscoveryBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise DiscoveryBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise DiscoveryBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise DiscoveryBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise DiscoveryBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if theory_queue.get("theory_queue_status") != "PASS_REPO_ONLY_OUTCOME_BLIND_BINANCE_THEORY_QUEUE_BUILDER_CREATED":
        raise DiscoveryBlocked("outcome-blind theory queue status is not PASS")
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise DiscoveryBlocked("outcome-blind theory queue is not ready")
    if theory_queue.get("allowed_next_step") != MODULE:
        raise DiscoveryBlocked(f"theory queue allowed_next_step is not {MODULE}")
    selected = theory_queue.get("selected_next_research_batch")
    if not isinstance(selected, list) or not selected or selected[0].get("theory_id") != THEORY_ID:
        raise DiscoveryBlocked(f"top selected theory is not {THEORY_ID}")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiscoveryBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise DiscoveryBlocked("public kline diagnostic status is not PASS")
    return theory_queue, dataset, kline, payload_hashes


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


def month_key_from_ms(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m")


def detect_header(row: list[str]) -> bool:
    return bool(row) and not str(row[0]).strip().isdigit()


def parse_checksum_text(text: str) -> str | None:
    match = re.search(r"\b[a-fA-F0-9]{64}\b", text)
    return match.group(0).lower() if match else None


def kline_cache_zip_path(symbol: str, year: int, month: int) -> Path:
    return KLINE_CACHE_ROOT / "raw_archives" / "klines" / symbol / "15m" / f"{symbol}-15m-{year:04d}-{month:02d}.zip"


def expected_missing_archive_keys(kline_diagnostic: dict[str, Any]) -> set[tuple[str, int, int]]:
    missing = kline_diagnostic.get("kline_data_quality", {}).get("missing_archives", [])
    if not isinstance(missing, list):
        raise DiscoveryBlocked("kline diagnostic missing_archives is not a list")
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
                raise DiscoveryBlocked(f"kline cache checksum mismatch: {path}")
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
        raise DiscoveryBlocked(f"required cached kline archives missing: {unexpected_missing[:5]}")
    available_count = sum(1 for record in archive_records if record["available"])
    expected_available = kline_diagnostic.get("public_data_source", {}).get("monthly_archive_count_available")
    if expected_available is not None and int(expected_available) != available_count:
        raise DiscoveryBlocked(f"cached archive count mismatch: {available_count} != {expected_available}")
    return {
        "archive_records": archive_records,
        "available_count": available_count,
        "missing_count": len(missing_keys),
        "checksum_available": checksum_available,
        "checksum_verified": checksum_verified,
        "missing_archive_keys": sorted([f"{symbol}-{year:04d}-{month:02d}" for symbol, year, month in missing_keys]),
    }


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
    bars: dict[int, tuple[float, float, float, float, float]] = {}
    duplicate_open_time_count = 0
    invalid_numeric_count = 0
    for record in archive_records:
        if record["symbol"] != symbol or not record["available"]:
            continue
        path = Path(record["local_path"])
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise DiscoveryBlocked(f"no CSV member found in cached kline archive: {path}")
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
                        volume = float(raw[5])
                    except ValueError:
                        invalid_numeric_count += 1
                        continue
                    if open_time in bars:
                        duplicate_open_time_count += 1
                        continue
                    bars[open_time] = (open_price, high, low, close, volume)
    if not bars:
        raise DiscoveryBlocked(f"no cached kline rows loaded for {symbol}")
    opens = np.array(sorted(bars), dtype=np.int64)
    open_prices = np.array([bars[int(open_time)][0] for open_time in opens], dtype=np.float64)
    highs = np.array([bars[int(open_time)][1] for open_time in opens], dtype=np.float64)
    lows = np.array([bars[int(open_time)][2] for open_time in opens], dtype=np.float64)
    closes = np.array([bars[int(open_time)][3] for open_time in opens], dtype=np.float64)
    volumes = np.array([bars[int(open_time)][4] for open_time in opens], dtype=np.float64)
    ranges = np.maximum(highs - lows, EPSILON)
    prior_high = rolling_previous_extreme(highs, "max", ROLLING_LOOKBACK_BARS)
    prior_low = rolling_previous_extreme(lows, "min", ROLLING_LOOKBACK_BARS)
    prior_close = np.full(closes.shape, np.nan, dtype=np.float64)
    prior_close[1:] = closes[:-1]
    abs_return_15m = np.where(np.isfinite(prior_close) & (prior_close != 0), np.abs((closes / prior_close) - 1.0), np.nan)
    return {
        "symbol": symbol,
        "opens": opens,
        "open": open_prices,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
        "range": ranges,
        "abs_return_15m": abs_return_15m,
        "prior_rolling_high": prior_high,
        "prior_rolling_low": prior_low,
        "open_to_index": {int(open_time): int(index) for index, open_time in enumerate(opens)},
        "quality": {
            "symbol": symbol,
            "row_count": int(len(opens)),
            "timestamp_min": ms_to_iso(int(opens[0])),
            "timestamp_max": ms_to_iso(int(opens[-1])),
            "duplicate_open_time_count": duplicate_open_time_count,
            "invalid_numeric_count": invalid_numeric_count,
        },
    }


def normalized_paths(dataset: dict[str, Any]) -> list[Path]:
    files = dataset.get("generated_external_files", {}).get("normalized_by_symbol_files")
    if not isinstance(files, list) or not files:
        raise DiscoveryBlocked("dataset builder artifact missing normalized_by_symbol_files")
    paths = [Path(str(path)) for path in files]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise DiscoveryBlocked(f"normalized proxy dataset files missing: {missing}")
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


def percentile_name(q: float) -> str:
    lookup = {
        0.0025: "p0.25",
        0.005: "p0.5",
        0.01: "p1.0",
        0.025: "p2.5",
        0.05: "p5.0",
        0.50: "p50.0",
        0.75: "p75.0",
        0.90: "p90.0",
        0.95: "p95.0",
        0.99: "p99.0",
        0.995: "p99.5",
        0.9975: "p99.75",
    }
    return lookup.get(q, f"p{q * 100:g}")


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
                    "taker_buy_pressure": to_float(row.get("taker_buy_sell_ratio")),
                    "taker_sell_pressure": to_float(row.get("taker_sell_pressure")),
                    "account_long_short_ratio": to_float(row.get("account_long_short_ratio")),
                    "position_long_short_ratio": to_float(row.get("position_long_short_ratio")),
                    "top_account_long_short_ratio": to_float(row.get("top_account_long_short_ratio")),
                    "top_position_long_short_ratio": to_float(row.get("top_position_long_short_ratio")),
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


def build_metric_thresholds(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, float | None]]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        month = row["month"]
        for key in [
            "oi_delta_log_1h",
            "taker_buy_pressure",
            "taker_sell_pressure",
            "top_account_long_short_ratio",
            "top_position_long_short_ratio",
        ]:
            value = row.get(key)
            if isinstance(value, float) and math.isfinite(value):
                buckets[month][key].append(value)
    thresholds: dict[str, dict[str, dict[str, float | None]]] = {}
    for month, per_field in buckets.items():
        thresholds[month] = {
            "oi_delta_log_1h": {
                percentile_name(q): quantile_or_none(per_field["oi_delta_log_1h"], q) for q in OI_CONTRACTION_QUANTILES
            },
            "taker_buy_pressure": {
                percentile_name(q): quantile_or_none(per_field["taker_buy_pressure"], q) for q in TAKER_PRESSURE_QUANTILES
            },
            "taker_sell_pressure": {
                percentile_name(q): quantile_or_none(per_field["taker_sell_pressure"], q) for q in TAKER_PRESSURE_QUANTILES
            },
            "long_short_annotations": {
                "top_account_p5.0": quantile_or_none(per_field["top_account_long_short_ratio"], 0.05),
                "top_account_p95.0": quantile_or_none(per_field["top_account_long_short_ratio"], 0.95),
                "top_position_p5.0": quantile_or_none(per_field["top_position_long_short_ratio"], 0.05),
                "top_position_p95.0": quantile_or_none(per_field["top_position_long_short_ratio"], 0.95),
            },
            "absolute_taker_ratio_thresholds_recorded": {"ratio_0.70": 0.70, "ratio_0.75": 0.75},
        }
    return thresholds


def build_price_thresholds(kline_data: dict[str, Any]) -> dict[str, dict[str, float | None]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for idx, open_time in enumerate(kline_data["opens"]):
        month = month_key_from_ms(int(open_time))
        buckets[month]["volume"].append(float(kline_data["volume"][idx]))
        buckets[month]["range"].append(float(kline_data["range"][idx]))
        abs_ret = float(kline_data["abs_return_15m"][idx])
        if math.isfinite(abs_ret):
            buckets[month]["abs_return_15m"].append(abs_ret)
    thresholds: dict[str, dict[str, float | None]] = {}
    for month, per_field in buckets.items():
        thresholds[month] = {
            "volume_p95.0": quantile_or_none(per_field["volume"], 0.95),
            "range_p95.0": quantile_or_none(per_field["range"], 0.95),
            "abs_return_15m_p25.0": quantile_or_none(per_field["abs_return_15m"], 0.25),
            "abs_return_15m_p75.0": quantile_or_none(per_field["abs_return_15m"], 0.75),
            "abs_return_15m_p90.0": quantile_or_none(per_field["abs_return_15m"], 0.90),
        }
    return thresholds


def price_features(row: dict[str, Any], kline_data: dict[str, Any], price_thresholds: dict[str, dict[str, float | None]]) -> dict[str, Any]:
    base_open = floor_to_15m_open(row["ts_ms"])
    index = kline_data["open_to_index"].get(base_open)
    if index is None:
        return {"price_available": False}
    open_price = float(kline_data["open"][index])
    high = float(kline_data["high"][index])
    low = float(kline_data["low"][index])
    close = float(kline_data["close"][index])
    volume = float(kline_data["volume"][index])
    range_value = max(float(kline_data["range"][index]), EPSILON)
    close_location = (close - low) / range_value
    upper_wick_ratio = (high - close) / range_value
    lower_wick_ratio = (close - low) / range_value
    prev_index = kline_data["open_to_index"].get(int(kline_data["opens"][index]) - ONE_HOUR_MS)
    current_return_1h = None
    if prev_index is not None:
        previous_close = float(kline_data["close"][prev_index])
        if previous_close != 0:
            current_return_1h = (close / previous_close) - 1.0
    prior_high = float(kline_data["prior_rolling_high"][index])
    prior_low = float(kline_data["prior_rolling_low"][index])
    month_thresholds = price_thresholds.get(row["month"], {})
    range_p95 = month_thresholds.get("range_p95.0")
    volume_p95 = month_thresholds.get("volume_p95.0")
    abs_return = float(kline_data["abs_return_15m"][index])
    abs_p25 = month_thresholds.get("abs_return_15m_p25.0")
    abs_p75 = month_thresholds.get("abs_return_15m_p75.0")
    abs_p90 = month_thresholds.get("abs_return_15m_p90.0")

    large_range = range_p95 is not None and range_value >= range_p95
    failed_breakdown = math.isfinite(prior_low) and low < prior_low and close >= prior_low
    failed_breakout = math.isfinite(prior_high) and high > prior_high and close <= prior_high
    downside_recovery = large_range and close_location >= 0.60 and (
        (current_return_1h is not None and current_return_1h <= 0.0) or close < open_price
    )
    upside_rejection = large_range and close_location <= 0.40 and (
        (current_return_1h is not None and current_return_1h >= 0.0) or close > open_price
    )
    long_flags = {
        "lower_wick_rejection": lower_wick_ratio >= 0.60,
        "close_location_upper": close_location >= 0.60,
        "failed_breakdown": failed_breakdown,
        "large_downside_range_recovery": downside_recovery,
    }
    short_flags = {
        "upper_wick_rejection": upper_wick_ratio >= 0.60,
        "close_location_lower": close_location <= 0.40,
        "failed_breakout": failed_breakout,
        "large_upside_range_rejection": upside_rejection,
    }
    if volume_p95 is None:
        volume_stress = "unknown"
    else:
        volume_stress = "volume_stress_p95_or_higher" if volume >= volume_p95 else "not_volume_stress"
    if not math.isfinite(abs_return) or abs_p25 is None or abs_p75 is None or abs_p90 is None:
        realized_vol_regime = "unknown"
    elif abs_return >= abs_p90:
        realized_vol_regime = "very_high_abs_return"
    elif abs_return >= abs_p75:
        realized_vol_regime = "high_abs_return"
    elif abs_return <= abs_p25:
        realized_vol_regime = "low_abs_return"
    else:
        realized_vol_regime = "normal_abs_return"
    return {
        "price_available": True,
        "current_return_1h": current_return_1h,
        "close_location": close_location,
        "upper_wick_ratio": upper_wick_ratio,
        "lower_wick_ratio": lower_wick_ratio,
        "long_flags": long_flags,
        "short_flags": short_flags,
        "long_rejection_score": sum(long_flags.values()),
        "short_rejection_score": sum(short_flags.values()),
        "volume_stress_annotation": volume_stress,
        "realized_volatility_regime_annotation": realized_vol_regime,
    }


def long_short_annotation(row: dict[str, Any], thresholds: dict[str, Any]) -> str:
    annotation_thresholds = thresholds.get("long_short_annotations", {})
    account_value = row.get("top_account_long_short_ratio")
    position_value = row.get("top_position_long_short_ratio")
    account_low = annotation_thresholds.get("top_account_p5.0")
    account_high = annotation_thresholds.get("top_account_p95.0")
    position_low = annotation_thresholds.get("top_position_p5.0")
    position_high = annotation_thresholds.get("top_position_p95.0")
    states = []
    if account_value is not None and account_low is not None and account_value <= account_low:
        states.append("account_short_extreme")
    if account_value is not None and account_high is not None and account_value >= account_high:
        states.append("account_long_extreme")
    if position_value is not None and position_low is not None and position_value <= position_low:
        states.append("position_short_extreme")
    if position_value is not None and position_high is not None and position_value >= position_high:
        states.append("position_long_extreme")
    if not states:
        return "none"
    account_side = any(state.startswith("account_") for state in states)
    position_side = any(state.startswith("position_") for state in states)
    if account_side and position_side:
        return "both"
    if account_side:
        return "account_only"
    return "position_only"


def definition_id(meta: dict[str, Any]) -> str:
    return "__".join(
        [
            meta["family"],
            f"oi_{meta['oi_contraction_percentile']}",
            f"taker_{meta['taker_pressure_percentile']}",
            f"rejection_score_gte_{meta['rejection_score_min']}",
            f"cooldown_{meta['cooldown_hours']}h",
        ]
    )


def build_definition_catalog() -> dict[str, dict[str, Any]]:
    catalog = {}
    for family in EVENT_FAMILIES:
        for oi_quantile in OI_CONTRACTION_QUANTILES:
            for taker_quantile in TAKER_PRESSURE_QUANTILES:
                for score_min in REJECTION_SCORE_BUCKETS:
                    for cooldown in COOLDOWN_HOURS:
                        meta = {
                            "family": family,
                            "side": EVENT_FAMILIES[family]["side"],
                            "taker_key": EVENT_FAMILIES[family]["taker_key"],
                            "oi_contraction_percentile": percentile_name(oi_quantile),
                            "taker_pressure_percentile": percentile_name(taker_quantile),
                            "rejection_score_min": score_min,
                            "cooldown_hours": cooldown,
                            "uses_forward_returns": False,
                            "uses_outcome_optimization": False,
                        }
                        catalog[definition_id(meta)] = meta
    return catalog


def blank_summary(def_id: str, meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "definition_id": def_id,
        "meta": meta,
        "raw_event_count": 0,
        "cooldown_filtered_count": 0,
        "unique_timestamp_count": 0,
        "unique_symbol_timestamp_count": 0,
        "symbol_coverage_count": 0,
        "month_coverage_count": 0,
        "top_symbol": None,
        "top_symbol_concentration": None,
        "top_month": None,
        "top_month_concentration": None,
        "arbusdt_count": 0,
        "overlap_rate": 0.0,
        "missing_component_count": 0,
        "rejected_due_to_cooldown_count": 0,
        "rejected_due_to_missing_price_rejection_count": 0,
        "rejected_due_to_missing_oi_or_taker_component_count": 0,
        "rejection_variant_distribution": Counter(),
        "optional_annotation_distribution": {
            "long_short_ratio_annotation": Counter(),
            "volume_stress_annotation": Counter(),
            "realized_volatility_regime_annotation": Counter(),
            "absolute_taker_ratio_annotations": Counter(),
        },
        "_raw_timestamps": set(),
        "_raw_symbol_timestamps": set(),
        "_symbols": Counter(),
        "_months": Counter(),
        "_last_event_ms": {},
    }


def taker_absolute_annotation(row: dict[str, Any], taker_key: str) -> str:
    value = row.get(taker_key)
    if value is None:
        return "unknown"
    parts = []
    if value >= 0.70:
        parts.append("ratio_gte_0.70")
    if value >= 0.75:
        parts.append("ratio_gte_0.75")
    return "+".join(parts) if parts else "ratio_lt_0.70"


def update_summary(
    summary: dict[str, Any],
    row: dict[str, Any],
    features: dict[str, Any],
    meta: dict[str, Any],
    annotation: str,
) -> None:
    summary["raw_event_count"] += 1
    summary["_raw_timestamps"].add(row["timestamp"])
    summary["_raw_symbol_timestamps"].add((row["symbol"], row["timestamp"]))
    flags = features["long_flags"] if meta["side"] == "long_capitulation" else features["short_flags"]
    for variant, passed in flags.items():
        if passed:
            summary["rejection_variant_distribution"][variant] += 1
    summary["optional_annotation_distribution"]["long_short_ratio_annotation"][annotation] += 1
    summary["optional_annotation_distribution"]["volume_stress_annotation"][features["volume_stress_annotation"]] += 1
    summary["optional_annotation_distribution"]["realized_volatility_regime_annotation"][
        features["realized_volatility_regime_annotation"]
    ] += 1
    summary["optional_annotation_distribution"]["absolute_taker_ratio_annotations"][
        taker_absolute_annotation(row, meta["taker_key"])
    ] += 1
    cooldown_key = row["symbol"]
    cooldown_ms = int(meta["cooldown_hours"]) * 60 * 60 * 1000
    previous = summary["_last_event_ms"].get(cooldown_key)
    if previous is not None and row["ts_ms"] - previous < cooldown_ms:
        summary["rejected_due_to_cooldown_count"] += 1
        return
    summary["_last_event_ms"][cooldown_key] = row["ts_ms"]
    summary["cooldown_filtered_count"] += 1
    summary["_symbols"][row["symbol"]] += 1
    summary["_months"][row["month"]] += 1
    if row["symbol"] == "ARBUSDT":
        summary["arbusdt_count"] += 1


def classify_count_band(count: int) -> str:
    if 300 <= count <= 1500:
        return "ideal"
    if 1500 < count <= 5000:
        return "acceptable_but_possibly_broad"
    if 100 <= count < 300:
        return "sparse_but_potentially_usable"
    if count > 5000:
        return "too_broad"
    return "too_sparse"


def finalize_summary(summary: dict[str, Any], global_missing_components: int) -> dict[str, Any]:
    raw_count = summary["raw_event_count"]
    cooldown_count = summary["cooldown_filtered_count"]
    symbols = summary.pop("_symbols")
    months = summary.pop("_months")
    raw_timestamps = summary.pop("_raw_timestamps")
    raw_symbol_timestamps = summary.pop("_raw_symbol_timestamps")
    summary.pop("_last_event_ms", None)
    top_symbol, top_symbol_count = (None, 0) if not symbols else symbols.most_common(1)[0]
    top_month, top_month_count = (None, 0) if not months else months.most_common(1)[0]
    summary["unique_timestamp_count"] = len(raw_timestamps)
    summary["unique_symbol_timestamp_count"] = len(raw_symbol_timestamps)
    summary["symbol_coverage_count"] = len(symbols)
    summary["symbols"] = sorted(symbols)
    summary["month_coverage_count"] = len(months)
    summary["months"] = sorted(months)
    summary["top_symbol"] = top_symbol
    summary["top_symbol_concentration"] = (top_symbol_count / cooldown_count) if cooldown_count else None
    summary["top_month"] = top_month
    summary["top_month_concentration"] = (top_month_count / cooldown_count) if cooldown_count else None
    summary["overlap_rate"] = 1.0 - (len(raw_symbol_timestamps) / raw_count) if raw_count else 0.0
    summary["missing_component_count"] = global_missing_components
    summary["rejection_variant_distribution"] = dict(summary["rejection_variant_distribution"])
    summary["optional_annotation_distribution"] = {
        key: dict(value) for key, value in summary["optional_annotation_distribution"].items()
    }
    summary["target_event_count_band"] = classify_count_band(cooldown_count)
    return summary


def compact_summary(summary: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "definition_id",
        "meta",
        "raw_event_count",
        "cooldown_filtered_count",
        "unique_timestamp_count",
        "unique_symbol_timestamp_count",
        "symbol_coverage_count",
        "symbols",
        "month_coverage_count",
        "months",
        "top_symbol",
        "top_symbol_concentration",
        "top_month",
        "top_month_concentration",
        "arbusdt_count",
        "overlap_rate",
        "missing_component_count",
        "rejected_due_to_cooldown_count",
        "rejected_due_to_missing_price_rejection_count",
        "rejected_due_to_missing_oi_or_taker_component_count",
        "rejection_variant_distribution",
        "optional_annotation_distribution",
        "target_event_count_band",
    ]
    return {field: summary[field] for field in fields}


def score_definition(summary: dict[str, Any]) -> float:
    count = summary["cooldown_filtered_count"]
    band_score = {
        "ideal": 1000,
        "acceptable_but_possibly_broad": 700,
        "sparse_but_potentially_usable": 420,
        "too_sparse": -500,
        "too_broad": -700,
    }[summary["target_event_count_band"]]
    symbol_score = summary["symbol_coverage_count"] * 25
    month_score = summary["month_coverage_count"] * 4
    count_center_bonus = -abs(count - 700) * 0.08 if count else -100
    concentration_penalty = 0.0
    if summary["top_symbol_concentration"] is not None and summary["top_symbol_concentration"] > 0.45:
        concentration_penalty += 300 * (summary["top_symbol_concentration"] - 0.45)
    if summary["top_month_concentration"] is not None and summary["top_month_concentration"] > 0.25:
        concentration_penalty += 200 * (summary["top_month_concentration"] - 0.25)
    overlap_penalty = summary["overlap_rate"] * 100
    strictness_bonus = summary["meta"]["rejection_score_min"] * 10
    return band_score + symbol_score + month_score + count_center_bonus + strictness_bonus - concentration_penalty - overlap_penalty


def run_symbol_discovery(
    path: Path,
    kline_data: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    summaries: dict[str, dict[str, Any]],
    missing_component_counter: Counter[str],
) -> None:
    rows = metric_rows_for_symbol(path)
    metric_thresholds_by_month = build_metric_thresholds(rows)
    price_thresholds_by_month = build_price_thresholds(kline_data)
    for row in rows:
        thresholds = metric_thresholds_by_month.get(row["month"])
        if thresholds is None:
            missing_component_counter["threshold_month_missing"] += 1
            continue
        features = price_features(row, kline_data, price_thresholds_by_month)
        if not features.get("price_available"):
            missing_component_counter["price_bar_missing"] += 1
            continue
        if row["oi_delta_log_1h"] is None:
            missing_component_counter["oi_delta_log_1h_missing"] += 1
            continue
        oi_pass = [
            percentile_name(q)
            for q in OI_CONTRACTION_QUANTILES
            if thresholds["oi_delta_log_1h"].get(percentile_name(q)) is not None
            and row["oi_delta_log_1h"] <= thresholds["oi_delta_log_1h"][percentile_name(q)]
        ]
        if not oi_pass:
            continue
        annotation = long_short_annotation(row, thresholds)
        for family, config in EVENT_FAMILIES.items():
            taker_key = config["taker_key"]
            if row.get(taker_key) is None:
                missing_component_counter[f"{taker_key}_missing"] += 1
                continue
            taker_pass = [
                percentile_name(q)
                for q in TAKER_PRESSURE_QUANTILES
                if thresholds[taker_key].get(percentile_name(q)) is not None
                and row[taker_key] >= thresholds[taker_key][percentile_name(q)]
            ]
            if not taker_pass:
                continue
            score = features["long_rejection_score"] if config["side"] == "long_capitulation" else features["short_rejection_score"]
            for oi_name in oi_pass:
                for taker_name in taker_pass:
                    for score_min in REJECTION_SCORE_BUCKETS:
                        for cooldown in COOLDOWN_HOURS:
                            meta = {
                                "family": family,
                                "side": config["side"],
                                "taker_key": taker_key,
                                "oi_contraction_percentile": oi_name,
                                "taker_pressure_percentile": taker_name,
                                "rejection_score_min": score_min,
                                "cooldown_hours": cooldown,
                                "uses_forward_returns": False,
                                "uses_outcome_optimization": False,
                            }
                            summary = summaries[definition_id(meta)]
                            if score >= score_min:
                                update_summary(summary, row, features, meta, annotation)
                            else:
                                summary["rejected_due_to_missing_price_rejection_count"] += 1


def select_definitions(summaries: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], str, str, str]:
    selections = []
    for slot_name, family in [
        ("best_long_capitulation_candidate", "LONG_CAPITULATION_REBOUND_CANDIDATE"),
        ("best_short_cover_exhaustion_candidate", "SHORT_COVER_EXHAUSTION_DOWNSIDE_CANDIDATE"),
    ]:
        candidates = [
            summary
            for summary in summaries.values()
            if summary["meta"]["family"] == family and summary["cooldown_filtered_count"] > 0
        ]
        if not candidates:
            continue
        candidates.sort(key=score_definition, reverse=True)
        best = compact_summary(candidates[0])
        best["selection_slot"] = slot_name
        best["selection_score"] = score_definition(candidates[0])
        selections.append(best)
        stricter = [
            item
            for item in candidates[1:]
            if item["target_event_count_band"] in {"ideal", "sparse_but_potentially_usable"}
            and (item["meta"]["oi_contraction_percentile"] in {"p0.5", "p0.25"} or item["meta"]["rejection_score_min"] >= 2)
        ]
        if stricter:
            optional = compact_summary(sorted(stricter, key=score_definition, reverse=True)[0])
            optional["selection_slot"] = f"optional_stricter_{slot_name}"
            optional["selection_score"] = score_definition(stricter[0])
            selections.append(optional)
    if not selections:
        return [], "No nonzero OI contraction/taker capitulation definitions survived contemporaneous gates.", RESULT_TOO_SPARSE, NEXT_REFINEMENT
    bands = [item["target_event_count_band"] for item in selections]
    if any(band in {"ideal", "acceptable_but_possibly_broad", "sparse_but_potentially_usable"} for band in bands):
        return (
            selections[:4],
            "Selected only by outcome-blind event count band, coverage, concentration, overlap, missing components, and material difference from blocked routes.",
            RESULT_READY,
            NEXT_VALIDATOR,
        )
    if all(band == "too_broad" for band in bands):
        return selections[:4], "All selected OI contraction/taker capitulation definitions are too broad.", RESULT_TOO_BROAD, NEXT_REFINEMENT
    return selections[:4], "Selected definitions remain too sparse for a clean validator route.", RESULT_TOO_SPARSE, NEXT_REFINEMENT


def output_counts(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        definition_id: {
            "raw_event_count": summary["raw_event_count"],
            "cooldown_filtered_count": summary["cooldown_filtered_count"],
            "target_event_count_band": summary["target_event_count_band"],
            "family": summary["meta"]["family"],
            "symbol_coverage_count": summary["symbol_coverage_count"],
            "month_coverage_count": summary["month_coverage_count"],
        }
        for definition_id, summary in summaries.items()
    }


def output_by_field(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {definition_id: summary[field] for definition_id, summary in summaries.items()}


def nested_distribution(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {definition_id: summary[field] for definition_id, summary in summaries.items() if summary["cooldown_filtered_count"] > 0}


def selected_by_slot(selected: list[dict[str, Any]]) -> dict[str, Any]:
    return {item["selection_slot"]: item for item in selected}


def forbidden_false() -> dict[str, bool]:
    return {
        "strategy": False,
        "signal": False,
        "backtest": False,
        "pnl": False,
        "trade_simulation": False,
        "optimization_against_returns": False,
        "candidate_generation": False,
        "edge_claim": False,
        "runtime_live_capital": False,
        "order_private_account_api_key": False,
        "private_api": False,
        "account_api": False,
        "api_key": False,
        "forward_returns_computed": False,
        "p_values_computed": False,
        "null_validation_run": False,
        "failed_routes_reused_under_new_names": False,
    }


def base_artifact(head: str | None, hashes_before: dict[str, str] | None, hashes_after: dict[str, str] | None, blocker: str | None) -> dict[str, Any]:
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    return {
        "discovery_status": DISCOVERY_STATUS_BLOCKED if blocker else DISCOVERY_STATUS_PASS,
        "status": DISCOVERY_STATUS_BLOCKED if blocker else DISCOVERY_STATUS_PASS,
        "artifact_kind": ARTIFACT_KIND,
        "module": MODULE,
        "result_classification": RESULT_FAILED if blocker else None,
        "recovery_audit_status": RECOVERY_AUDIT_STATUS,
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "theory_id": THEORY_ID,
        "mechanical_rationale": "OI contraction can indicate position unwind/deleveraging; extreme taker pressure plus current/prior-bar price rejection can identify capitulation or exhaustion without inspecting future outcomes.",
        "material_difference_from_failed_routes": "Uses OI contraction rather than the failed OI-expansion pressure-failure route, requires current/prior-bar price rejection, treats long-short ratios only as annotations, and never uses funding/liquidation unavailable data.",
        "threshold_grid": {
            "oi_contraction_thresholds": [percentile_name(q) for q in OI_CONTRACTION_QUANTILES],
            "taker_pressure_thresholds": [percentile_name(q) for q in TAKER_PRESSURE_QUANTILES],
            "rejection_strength_score": [f"score>={value}" for value in REJECTION_SCORE_BUCKETS],
            "threshold_basis": "symbol-month distributions only; no future-return, p-value, PnL, hit-rate, Sharpe, or backtest optimization",
        },
        "cooldown_grid": [f"{value}h" for value in COOLDOWN_HOURS],
        "event_families_tested": EVENT_FAMILIES,
        "event_counts_by_definition": {},
        "cooldown_filtered_counts": {},
        "selected_clean_event_definitions": [],
        "selected_definition_reason": None,
        "symbol_coverage_summary": {},
        "month_coverage_summary": {},
        "concentration_summary": {},
        "arbusdt_summary": {},
        "overlap_summary": {},
        "missing_data_summary": {},
        "rejection_reason_summary": {},
        "rejection_variant_distribution": {},
        "optional_annotation_distribution": {},
        "target_event_count_interpretation": {
            "ideal": "300 to 1500 cooldown-filtered events",
            "acceptable_but_possibly_broad": "1500 to 5000 cooldown-filtered events",
            "too_broad": "over 5000 cooldown-filtered events",
            "sparse_but_potentially_usable": "100 to 300 cooldown-filtered events",
            "too_sparse": "under 100 cooldown-filtered events",
            "outcome_blind_selection": True,
        },
        "validation_limits": [
            "Event discovery only; no forward returns were computed.",
            "No p-values, null validation, backtest, PnL, signal, candidate, or edge claim was produced.",
            "Selection used only event cleanliness, coverage, concentration, overlap, missing components, and material difference from failed routes.",
            "Long-short ratio, volume stress, and realized volatility are annotations only, not mandatory gates.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_REFINEMENT if blocker else None,
        "blocker": blocker,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise DiscoveryBlocked(f"HEAD mismatch: {head} != {EXPECTED_HEAD}")
    status_lines = working_tree_status()
    if not output_only_status(status_lines):
        raise DiscoveryBlocked(f"unexpected dirty repo state during build: {status_lines}")
    theory_queue, dataset, kline_diagnostic, input_payload_hashes = load_inputs()
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols") or dataset.get("requested_symbols")
    if not isinstance(symbols, list) or not symbols:
        raise DiscoveryBlocked("dataset builder artifact missing built symbol list")
    symbols = [str(symbol) for symbol in symbols]
    archive_summary = verify_cached_archives(symbols, kline_diagnostic)
    catalog = build_definition_catalog()
    summaries = {def_id: blank_summary(def_id, meta) for def_id, meta in catalog.items()}
    missing_counter: Counter[str] = Counter()
    kline_quality: dict[str, Any] = {}
    paths = normalized_paths(dataset)
    symbol_to_path = {path.name.split("_", 1)[0]: path for path in paths}
    for symbol in symbols:
        path = symbol_to_path.get(symbol)
        if path is None:
            missing_counter[f"{symbol}_normalized_path_missing"] += 1
            continue
        kline_data = load_kline_symbol(symbol, archive_summary["archive_records"])
        kline_quality[symbol] = kline_data["quality"]
        run_symbol_discovery(path, kline_data, catalog, summaries, missing_counter)
    global_missing_components = int(sum(missing_counter.values()))
    finalized = {def_id: finalize_summary(summary, global_missing_components) for def_id, summary in summaries.items()}
    selected, selection_reason, result_classification, next_step = select_definitions(finalized)
    hashes_before = input_artifact_hashes()
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise DiscoveryBlocked("input artifact hash changed during build")
    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "theory_queue_ready": theory_queue.get("result_classification") == "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY",
        "top_theory_matches_requested": (theory_queue.get("selected_next_research_batch") or [{}])[0].get("theory_id") == THEORY_ID,
        "public_binance_derived_data_only": True,
        "no_new_downloads_performed": True,
        "no_forward_returns_computed": True,
        "no_p_values_computed": True,
        "no_null_validation_run": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_strategy_signal_candidate_release": True,
        "no_runtime_live_capital_order_private_account_api_key": True,
        "artifacts_data_builds_not_written": True,
        "exactly_one_python_tool_created": True,
        "exactly_one_json_artifact_created": True,
    }
    artifact = base_artifact(head, hashes_before, hashes_after, None)
    artifact.update(
        {
            "result_classification": result_classification,
            "input_payload_hashes_verified": input_payload_hashes,
            "available_data_source_summary": {
                "symbols": symbols,
                "normalized_metric_files": [str(path) for path in paths],
                "kline_cache_root": str(KLINE_CACHE_ROOT),
                "archive_availability_summary": archive_summary,
                "kline_quality": kline_quality,
            },
            "event_counts_by_definition": output_counts(finalized),
            "cooldown_filtered_counts": output_by_field(finalized, "cooldown_filtered_count"),
            "selected_clean_event_definitions": selected,
            "selected_definition_reason": selection_reason,
            "symbol_coverage_summary": output_by_field(finalized, "symbol_coverage_count"),
            "month_coverage_summary": output_by_field(finalized, "month_coverage_count"),
            "concentration_summary": {
                def_id: {
                    "top_symbol": summary["top_symbol"],
                    "top_symbol_concentration": summary["top_symbol_concentration"],
                    "top_month": summary["top_month"],
                    "top_month_concentration": summary["top_month_concentration"],
                }
                for def_id, summary in finalized.items()
            },
            "arbusdt_summary": output_by_field(finalized, "arbusdt_count"),
            "overlap_summary": output_by_field(finalized, "overlap_rate"),
            "missing_data_summary": {
                "global_missing_component_count": global_missing_components,
                "missing_component_counter": dict(missing_counter),
                "archive_missing_count": archive_summary["missing_count"],
                "missing_archive_keys": archive_summary["missing_archive_keys"],
            },
            "rejection_reason_summary": {
                def_id: {
                    "rejected_due_to_cooldown_count": summary["rejected_due_to_cooldown_count"],
                    "rejected_due_to_missing_price_rejection_count": summary["rejected_due_to_missing_price_rejection_count"],
                    "rejected_due_to_missing_oi_or_taker_component_count": summary[
                        "rejected_due_to_missing_oi_or_taker_component_count"
                    ],
                }
                for def_id, summary in finalized.items()
            },
            "rejection_variant_distribution": nested_distribution(finalized, "rejection_variant_distribution"),
            "optional_annotation_distribution": nested_distribution(finalized, "optional_annotation_distribution"),
            "allowed_next_step": next_step,
            "validation_checks": validation_checks,
            "replacement_checks_all_true": all(validation_checks.values()),
        }
    )
    artifact["selected_clean_event_definitions_by_slot"] = selected_by_slot(selected)
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def blocked_artifact(reason: str, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    artifact = base_artifact(head, hashes_before, hashes_after, reason)
    artifact["validation_checks"] = {
        "blocked_without_substitution": True,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after if hashes_before and hashes_after else False,
        "replacement_checks_all_true": False,
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def print_summary(artifact: dict[str, Any]) -> None:
    selected = artifact.get("selected_clean_event_definitions", [])
    selected_counts = {
        item.get("selection_slot"): {
            "definition_id": item.get("definition_id"),
            "cooldown_filtered_count": item.get("cooldown_filtered_count"),
            "target_event_count_band": item.get("target_event_count_band"),
        }
        for item in selected
    }
    print(f"status: {artifact['discovery_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"material_difference_from_failed_routes: {artifact['material_difference_from_failed_routes']}")
    print(f"selected_clean_event_definitions: {json.dumps(selected_counts, sort_keys=True)}")
    print(f"event_counts_by_definition: {len(artifact.get('event_counts_by_definition', {}))} definitions evaluated")
    print(f"cooldown_filtered_counts: {json.dumps(selected_counts, sort_keys=True)}")
    print(f"symbol_coverage_summary: {json.dumps({k: v['symbol_coverage_count'] if isinstance(v, dict) and 'symbol_coverage_count' in v else v for k, v in selected_counts.items()}, sort_keys=True)}")
    print(f"month_coverage_summary: {json.dumps({k: v for k, v in artifact.get('month_coverage_summary', {}).items() if artifact.get('cooldown_filtered_counts', {}).get(k, 0) > 0}, sort_keys=True)[:1000]}")
    print(f"concentration_summary: {json.dumps({item.get('selection_slot'): {'top_symbol': item.get('top_symbol'), 'top_symbol_concentration': item.get('top_symbol_concentration'), 'top_month': item.get('top_month'), 'top_month_concentration': item.get('top_month_concentration')} for item in selected}, sort_keys=True)}")
    print(f"arbusdt_summary: {json.dumps({item.get('selection_slot'): item.get('arbusdt_count') for item in selected}, sort_keys=True)}")
    print(f"overlap_summary: {json.dumps({item.get('selection_slot'): item.get('overlap_rate') for item in selected}, sort_keys=True)}")
    print(f"missing_data_summary: {json.dumps(artifact.get('missing_data_summary', {}), sort_keys=True)}")
    print(f"rejection_reason_summary: {json.dumps({item.get('selection_slot'): {'cooldown_rejects': item.get('rejected_due_to_cooldown_count'), 'price_rejection_rejects': item.get('rejected_due_to_missing_price_rejection_count')} for item in selected}, sort_keys=True)}")
    print(f"rejection_variant_distribution: {json.dumps({item.get('selection_slot'): item.get('rejection_variant_distribution') for item in selected}, sort_keys=True)}")
    print(f"optional_annotation_distribution: {json.dumps({item.get('selection_slot'): item.get('optional_annotation_distribution') for item in selected}, sort_keys=True)[:2000]}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"candidate_generation: false")
    print(f"edge_claim: false")
    print(f"runtime_live_capital: false")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(bool(artifact.get('replacement_checks_all_true')))}")
    print(f"blocker: {artifact.get('blocker')}")


def main() -> int:
    hashes_before: dict[str, str] | None = None
    try:
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
    except DiscoveryBlocked as exc:
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
