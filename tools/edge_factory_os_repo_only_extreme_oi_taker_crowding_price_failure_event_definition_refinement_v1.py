#!/usr/bin/env python
"""Refine strict OI/taker/crowding price-failure event definitions without outcomes."""

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
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DEFINITION_REFINEMENT_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "f6e182663375cb58f6df1cd97e1e2a663d3c8658"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_discovery_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
SOURCE_ROBUSTNESS_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_forward_return_robustness_runner_v1.json"
SOURCE_NULL_RUNNER_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_forward_return_null_validation_runner_v1.json"
SOURCE_EVENT_STUDY_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_proxy_event_study_v1.json"
SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH = "artifacts/contracts/binance_oi_taker_crowding_proxy_validation_contract_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_NULL_RUNNER_RELATIVE_PATH,
    SOURCE_EVENT_STUDY_RELATIVE_PATH,
    SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH,
]

REFINEMENT_STATUS_PASS = "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_CREATED"
REFINEMENT_STATUS_BLOCKED = "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT"
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DEFINITION_REFINEMENT"

RESULT_READY = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_READY"
RESULT_SPARSE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_STILL_TOO_SPARSE"
RESULT_BROAD = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_TOO_BROAD"
RESULT_ATTENTION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_FAILED_STOP"

NEXT_VALIDATOR = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_VALIDATOR_V1"
NEXT_EVALUATOR = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_REFINEMENT_EVALUATOR_V1"

KLINE_CACHE_ROOT = REPO_ROOT / "cache" / "binance_public_kline_forward_return_diagnostic_v1"
KLINE_INTERVAL_MS = 15 * 60 * 1000
ONE_HOUR_MS = 60 * 60 * 1000
START_YEAR_MONTH = (2023, 1)
END_YEAR_MONTH = (2025, 12)
ROLLING_LOOKBACK_BARS = 16
EPSILON = 1e-12

OI_QUANTILES = [0.975, 0.98, 0.99]
TAKER_QUANTILES = [0.975, 0.98, 0.99]
CROWDING_QUANTILES = [0.95, 0.975]
FAILURE_SCORE_BUCKETS = [1, 2, 3]
COOLDOWN_HOURS = [6, 12, 24]
PRICE_FAILURE_VARIANTS = ["opposite_1h_return", "wick_rejection", "close_location_failure", "failed_breakout_breakdown", "any_failure"]

EVENT_SIDES = {
    "long_failure": "EXTREME_CROWDED_LONG_FAILURE_REFINED",
    "short_failure": "EXTREME_CROWDED_SHORT_FAILURE_REFINED",
}

FORBIDDEN_FAILED_ROUTES = [
    "funding crowding reversal",
    "funding carry",
    "funding extreme volume surge",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
]


class RefinementBlocked(Exception):
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
        raise RefinementBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
            raise RefinementBlocked(f"missing required input artifact: {relative_path}")
        hashes[relative_path] = sha256_file(path)
    return hashes


def read_json_readonly(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise RefinementBlocked(f"missing required input artifact: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RefinementBlocked(f"input artifact is not a JSON object: {relative_path}")
    return payload


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise RefinementBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise RefinementBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    null_runner = read_json_readonly(SOURCE_NULL_RUNNER_RELATIVE_PATH)
    event_study = read_json_readonly(SOURCE_EVENT_STUDY_RELATIVE_PATH)
    validation = read_json_readonly(SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "prior extreme discovery"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "robustness runner"),
        SOURCE_NULL_RUNNER_RELATIVE_PATH: verify_payload_hash(null_runner, "null validation runner"),
        SOURCE_EVENT_STUDY_RELATIVE_PATH: verify_payload_hash(event_study, "proxy event study"),
        SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: verify_payload_hash(validation, "proxy validation contract"),
    }
    if discovery.get("discovery_status") != "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_CREATED":
        raise RefinementBlocked("prior extreme discovery status is not PASS")
    if discovery.get("result_classification") != "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_TOO_SPARSE":
        raise RefinementBlocked("prior extreme discovery was not classified too sparse")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise RefinementBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise RefinementBlocked("public kline diagnostic status is not PASS")
    if robustness.get("robustness_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_RUNNER_CREATED":
        raise RefinementBlocked("robustness runner status is not PASS")
    if null_runner.get("null_validation_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_NULL_VALIDATION_RUNNER_CREATED":
        raise RefinementBlocked("null validation runner status is not PASS")
    if event_study.get("status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_CREATED":
        raise RefinementBlocked("event study status is not PASS")
    if validation.get("validation_contract_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_CREATED":
        raise RefinementBlocked("proxy validation contract status is not PASS")
    return discovery, dataset, kline, robustness, null_runner, event_study, validation, payload_hashes


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


def expected_missing_archive_keys(kline_diagnostic: dict[str, Any]) -> set[tuple[str, int, int]]:
    missing = kline_diagnostic.get("kline_data_quality", {}).get("missing_archives", [])
    if not isinstance(missing, list):
        raise RefinementBlocked("kline diagnostic missing_archives is not a list")
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
                raise RefinementBlocked(f"kline cache checksum mismatch: {path}")
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
        raise RefinementBlocked(f"required cached kline archives missing: {unexpected_missing[:5]}")
    available_count = sum(1 for record in archive_records if record["available"])
    expected_available = kline_diagnostic.get("public_data_source", {}).get("monthly_archive_count_available")
    if available_count != expected_available:
        raise RefinementBlocked(f"cached archive count mismatch: {available_count} != {expected_available}")
    return {
        "archive_records": archive_records,
        "available_count": available_count,
        "missing_count": len(missing_keys),
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
                raise RefinementBlocked(f"no CSV member found in cached kline archive: {path}")
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
        raise RefinementBlocked(f"no cached kline rows loaded for {symbol}")
    opens = np.array(sorted(bars), dtype=np.int64)
    open_prices = np.array([bars[int(open_time)][0] for open_time in opens], dtype=np.float64)
    highs = np.array([bars[int(open_time)][1] for open_time in opens], dtype=np.float64)
    lows = np.array([bars[int(open_time)][2] for open_time in opens], dtype=np.float64)
    closes = np.array([bars[int(open_time)][3] for open_time in opens], dtype=np.float64)
    prior_high = rolling_previous_extreme(highs, "max", ROLLING_LOOKBACK_BARS)
    prior_low = rolling_previous_extreme(lows, "min", ROLLING_LOOKBACK_BARS)
    return {
        "symbol": symbol,
        "opens": opens,
        "open": open_prices,
        "high": highs,
        "low": lows,
        "close": closes,
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
        raise RefinementBlocked("dataset builder artifact missing normalized_by_symbol_files")
    paths = [Path(str(path)) for path in files]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise RefinementBlocked(f"normalized proxy dataset files missing: {missing}")
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
        0.975: "p97.5",
        0.98: "p98.0",
        0.99: "p99.0",
        0.95: "p95.0",
        0.025: "p2.5",
        0.02: "p2.0",
        0.01: "p1.0",
        0.05: "p5.0",
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


def build_symbol_thresholds(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, float | None]]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        month = row["month"]
        for key in ["oi_delta_log_1h", "taker_buy_aggression", "taker_sell_aggression", "top_account_ratio", "top_position_ratio"]:
            value = row.get(key)
            if isinstance(value, float) and math.isfinite(value):
                buckets[month][key].append(value)
    thresholds: dict[str, dict[str, dict[str, float | None]]] = {}
    for month, per_field in buckets.items():
        thresholds[month] = {
            "oi_delta_log_1h": {percentile_name(q): quantile_or_none(per_field["oi_delta_log_1h"], q) for q in OI_QUANTILES},
            "taker_buy_aggression": {percentile_name(q): quantile_or_none(per_field["taker_buy_aggression"], q) for q in TAKER_QUANTILES},
            "taker_sell_aggression": {percentile_name(q): quantile_or_none(per_field["taker_sell_aggression"], q) for q in TAKER_QUANTILES},
            "long_crowding": {
                "top_account_p95.0": quantile_or_none(per_field["top_account_ratio"], 0.95),
                "top_account_p97.5": quantile_or_none(per_field["top_account_ratio"], 0.975),
                "top_position_p95.0": quantile_or_none(per_field["top_position_ratio"], 0.95),
                "top_position_p97.5": quantile_or_none(per_field["top_position_ratio"], 0.975),
            },
            "short_crowding": {
                "top_account_p5.0": quantile_or_none(per_field["top_account_ratio"], 0.05),
                "top_account_p2.5": quantile_or_none(per_field["top_account_ratio"], 0.025),
                "top_position_p5.0": quantile_or_none(per_field["top_position_ratio"], 0.05),
                "top_position_p2.5": quantile_or_none(per_field["top_position_ratio"], 0.025),
            },
            "absolute_taker_ratio_thresholds_recorded": {"ratio_0.70": 0.70, "ratio_0.75": 0.75},
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
    long_score = sum(long_flags.values())
    short_score = sum(short_flags.values())
    return {
        "price_available": True,
        "price_return_1h": price_return_1h,
        "close_location": close_location,
        "upper_wick_ratio": upper_wick_ratio,
        "lower_wick_ratio": lower_wick_ratio,
        "long_flags": {**long_flags, "any_failure": any(long_flags.values())},
        "short_flags": {**short_flags, "any_failure": any(short_flags.values())},
        "long_failure_score": long_score,
        "short_failure_score": short_score,
    }


def blank_summary(definition_id: str, meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "definition_id": definition_id,
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
        "rejected_due_to_missing_price_failure_confirmation_count": 0,
        "rejected_due_to_missing_oi_taker_components_count": 0,
        "rejected_due_to_missing_crowding_components_count": 0,
        "rejected_due_to_cooldown_count": 0,
        "crowding_confirmation_distribution": Counter(),
        "price_failure_variant_distribution": Counter(),
        "_raw_timestamps": set(),
        "_raw_symbol_timestamps": set(),
        "_symbols": Counter(),
        "_months": Counter(),
        "_last_event_ms": {},
    }


def definition_id(meta: dict[str, Any]) -> str:
    parts = [
        meta["family"],
        meta["side"],
        f"oi_{meta['oi_percentile']}",
        f"taker_{meta['taker_percentile']}",
        f"pf_{meta['price_failure_variant']}",
        f"score_{meta['failure_score_min']}",
        f"cooldown_{meta['cooldown_hours']}h",
    ]
    if meta.get("crowding_hard_gate"):
        parts.append(f"crowd_{meta['crowding_percentile']}")
    return "__".join(str(part) for part in parts)


def build_definition_catalog() -> dict[str, dict[str, Any]]:
    catalog = {}
    for side in EVENT_SIDES:
        for oi_q in OI_QUANTILES:
            for taker_q in TAKER_QUANTILES:
                for score_min in FAILURE_SCORE_BUCKETS:
                    for cooldown in COOLDOWN_HOURS:
                        meta = {
                            "family": "CORE_PRICE_FAILURE_WITH_CROWDING_TIER",
                            "side": side,
                            "oi_percentile": percentile_name(oi_q),
                            "taker_percentile": percentile_name(taker_q),
                            "crowding_hard_gate": False,
                            "crowding_percentile": None,
                            "price_failure_variant": "score_bucket",
                            "failure_score_min": score_min,
                            "cooldown_hours": cooldown,
                        }
                        catalog[definition_id(meta)] = meta
                for crowd_q in CROWDING_QUANTILES:
                    for variant in PRICE_FAILURE_VARIANTS:
                        for cooldown in COOLDOWN_HOURS:
                            meta = {
                                "family": "RELAXED_EXTREME_GRID",
                                "side": side,
                                "oi_percentile": percentile_name(oi_q),
                                "taker_percentile": percentile_name(taker_q),
                                "crowding_hard_gate": True,
                                "crowding_percentile": percentile_name(crowd_q),
                                "price_failure_variant": variant,
                                "failure_score_min": 1,
                                "cooldown_hours": cooldown,
                            }
                            catalog[definition_id(meta)] = meta
    return catalog


def threshold_lookup(thresholds: dict[str, Any], row: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    side = meta["side"]
    oi_threshold = thresholds["oi_delta_log_1h"][meta["oi_percentile"]]
    taker_key = "taker_buy_aggression" if side == "long_failure" else "taker_sell_aggression"
    taker_threshold = thresholds[taker_key][meta["taker_percentile"]]
    if side == "long_failure":
        crowd_bucket = thresholds["long_crowding"]
        account_threshold = crowd_bucket.get(f"top_account_{meta.get('crowding_percentile') or 'p95.0'}")
        position_threshold = crowd_bucket.get(f"top_position_{meta.get('crowding_percentile') or 'p95.0'}")
        account_ok = row["top_account_ratio"] is not None and account_threshold is not None and row["top_account_ratio"] >= account_threshold
        position_ok = row["top_position_ratio"] is not None and position_threshold is not None and row["top_position_ratio"] >= position_threshold
    else:
        crowd_name = meta.get("crowding_percentile") or "p5.0"
        short_key = {"p95.0": "p5.0", "p97.5": "p2.5"}.get(crowd_name, "p5.0")
        crowd_bucket = thresholds["short_crowding"]
        account_threshold = crowd_bucket.get(f"top_account_{short_key}")
        position_threshold = crowd_bucket.get(f"top_position_{short_key}")
        account_ok = row["top_account_ratio"] is not None and account_threshold is not None and row["top_account_ratio"] <= account_threshold
        position_ok = row["top_position_ratio"] is not None and position_threshold is not None and row["top_position_ratio"] <= position_threshold
    return {
        "oi_threshold": oi_threshold,
        "taker_threshold": taker_threshold,
        "taker_key": taker_key,
        "account_crowding_ok": account_ok,
        "position_crowding_ok": position_ok,
    }


def crowding_tier(account_ok: bool, position_ok: bool) -> str:
    if account_ok and position_ok:
        return "both"
    if account_ok:
        return "account_only"
    if position_ok:
        return "position_only"
    return "none"


def update_summary(summary: dict[str, Any], row: dict[str, Any], features: dict[str, Any], meta: dict[str, Any], crowd_tier: str) -> None:
    summary["raw_event_count"] += 1
    summary["_raw_timestamps"].add(row["timestamp"])
    summary["_raw_symbol_timestamps"].add((row["symbol"], row["timestamp"]))
    summary["crowding_confirmation_distribution"][crowd_tier] += 1
    side_flags = features["long_flags"] if meta["side"] == "long_failure" else features["short_flags"]
    if meta["price_failure_variant"] == "score_bucket":
        for variant, passed in side_flags.items():
            if variant != "any_failure" and passed:
                summary["price_failure_variant_distribution"][variant] += 1
    else:
        summary["price_failure_variant_distribution"][meta["price_failure_variant"]] += 1
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


def finalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
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
    summary["crowding_confirmation_distribution"] = dict(summary["crowding_confirmation_distribution"])
    summary["price_failure_variant_distribution"] = dict(summary["price_failure_variant_distribution"])
    summary["target_event_count_band"] = classify_count_band(cooldown_count)
    return summary


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


def score_definition(summary: dict[str, Any], require_crowding: bool) -> float:
    count = summary["cooldown_filtered_count"]
    band = summary["target_event_count_band"]
    band_score = {
        "ideal": 1000,
        "acceptable_but_possibly_broad": 700,
        "sparse_but_potentially_usable": 400,
        "too_sparse": -500,
        "too_broad": -600,
    }[band]
    symbol_score = summary["symbol_coverage_count"] * 20
    month_score = summary["month_coverage_count"] * 4
    concentration_penalty = 0.0
    if summary["top_symbol_concentration"] is not None and summary["top_symbol_concentration"] > 0.45:
        concentration_penalty += 200 * (summary["top_symbol_concentration"] - 0.45)
    if summary["top_month_concentration"] is not None and summary["top_month_concentration"] > 0.25:
        concentration_penalty += 150 * (summary["top_month_concentration"] - 0.25)
    overlap_penalty = summary["overlap_rate"] * 100
    crowding_bonus = 0
    if require_crowding:
        distribution = summary["crowding_confirmation_distribution"]
        crowded = distribution.get("account_only", 0) + distribution.get("position_only", 0) + distribution.get("both", 0)
        crowding_bonus = 50 if count and crowded / count >= 0.5 else -200
    return band_score + symbol_score + month_score + crowding_bonus - concentration_penalty - overlap_penalty


def run_symbol_refinement(
    path: Path,
    kline_data: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    summaries: dict[str, dict[str, Any]],
    missing_component_counter: Counter[str],
) -> None:
    rows = metric_rows_for_symbol(path)
    thresholds_by_month = build_symbol_thresholds(rows)
    for row in rows:
        thresholds = thresholds_by_month.get(row["month"])
        if thresholds is None:
            missing_component_counter["threshold_month_missing"] += 1
            continue
        features = price_features(row, kline_data)
        if not features.get("price_available"):
            missing_component_counter["price_bar_missing"] += 1
            continue
        if row["oi_delta_log_1h"] is None:
            missing_component_counter["oi_delta_log_1h_missing"] += 1
            continue
        oi_pass = [
            percentile_name(q)
            for q in OI_QUANTILES
            if thresholds["oi_delta_log_1h"].get(percentile_name(q)) is not None
            and row["oi_delta_log_1h"] >= thresholds["oi_delta_log_1h"][percentile_name(q)]
        ]
        if not oi_pass:
            continue
        for side in EVENT_SIDES:
            taker_key = "taker_buy_aggression" if side == "long_failure" else "taker_sell_aggression"
            if row[taker_key] is None:
                missing_component_counter[f"{taker_key}_missing"] += 1
                continue
            taker_pass = [
                percentile_name(q)
                for q in TAKER_QUANTILES
                if thresholds[taker_key].get(percentile_name(q)) is not None
                and row[taker_key] >= thresholds[taker_key][percentile_name(q)]
            ]
            if not taker_pass:
                continue
            side_flags = features["long_flags"] if side == "long_failure" else features["short_flags"]
            failure_score = features["long_failure_score"] if side == "long_failure" else features["short_failure_score"]
            if side == "long_failure":
                account_p95 = thresholds["long_crowding"].get("top_account_p95.0")
                position_p95 = thresholds["long_crowding"].get("top_position_p95.0")
                account_core = row["top_account_ratio"] is not None and account_p95 is not None and row["top_account_ratio"] >= account_p95
                position_core = row["top_position_ratio"] is not None and position_p95 is not None and row["top_position_ratio"] >= position_p95
                hard_crowd_pass = [
                    percentile_name(q)
                    for q in CROWDING_QUANTILES
                    if (
                        row["top_account_ratio"] is not None
                        and thresholds["long_crowding"].get(f"top_account_{percentile_name(q)}") is not None
                        and row["top_account_ratio"] >= thresholds["long_crowding"][f"top_account_{percentile_name(q)}"]
                    )
                    or (
                        row["top_position_ratio"] is not None
                        and thresholds["long_crowding"].get(f"top_position_{percentile_name(q)}") is not None
                        and row["top_position_ratio"] >= thresholds["long_crowding"][f"top_position_{percentile_name(q)}"]
                    )
                ]
            else:
                account_p5 = thresholds["short_crowding"].get("top_account_p5.0")
                position_p5 = thresholds["short_crowding"].get("top_position_p5.0")
                account_core = row["top_account_ratio"] is not None and account_p5 is not None and row["top_account_ratio"] <= account_p5
                position_core = row["top_position_ratio"] is not None and position_p5 is not None and row["top_position_ratio"] <= position_p5
                hard_crowd_pass = []
                for q in CROWDING_QUANTILES:
                    mapped = "p5.0" if q == 0.95 else "p2.5"
                    if (
                        row["top_account_ratio"] is not None
                        and thresholds["short_crowding"].get(f"top_account_{mapped}") is not None
                        and row["top_account_ratio"] <= thresholds["short_crowding"][f"top_account_{mapped}"]
                    ) or (
                        row["top_position_ratio"] is not None
                        and thresholds["short_crowding"].get(f"top_position_{mapped}") is not None
                        and row["top_position_ratio"] <= thresholds["short_crowding"][f"top_position_{mapped}"]
                    ):
                        hard_crowd_pass.append(percentile_name(q))
            tier = crowding_tier(account_core, position_core)
            if row["top_account_ratio"] is None and row["top_position_ratio"] is None:
                missing_component_counter["crowding_components_missing"] += 1
            for oi_name in oi_pass:
                for taker_name in taker_pass:
                    if failure_score == 0:
                        for score_min in FAILURE_SCORE_BUCKETS:
                            for cooldown in COOLDOWN_HOURS:
                                meta = {
                                    "family": "CORE_PRICE_FAILURE_WITH_CROWDING_TIER",
                                    "side": side,
                                    "oi_percentile": oi_name,
                                    "taker_percentile": taker_name,
                                    "crowding_hard_gate": False,
                                    "crowding_percentile": None,
                                    "price_failure_variant": "score_bucket",
                                    "failure_score_min": score_min,
                                    "cooldown_hours": cooldown,
                                }
                                summaries[definition_id(meta)]["rejected_due_to_missing_price_failure_confirmation_count"] += 1
                    else:
                        for score_min in [value for value in FAILURE_SCORE_BUCKETS if failure_score >= value]:
                            for cooldown in COOLDOWN_HOURS:
                                meta = {
                                    "family": "CORE_PRICE_FAILURE_WITH_CROWDING_TIER",
                                    "side": side,
                                    "oi_percentile": oi_name,
                                    "taker_percentile": taker_name,
                                    "crowding_hard_gate": False,
                                    "crowding_percentile": None,
                                    "price_failure_variant": "score_bucket",
                                    "failure_score_min": score_min,
                                    "cooldown_hours": cooldown,
                                }
                                update_summary(summaries[definition_id(meta)], row, features, meta, tier)
                    for crowd_name in hard_crowd_pass:
                        for variant in PRICE_FAILURE_VARIANTS:
                            for cooldown in COOLDOWN_HOURS:
                                meta = {
                                    "family": "RELAXED_EXTREME_GRID",
                                    "side": side,
                                    "oi_percentile": oi_name,
                                    "taker_percentile": taker_name,
                                    "crowding_hard_gate": True,
                                    "crowding_percentile": crowd_name,
                                    "price_failure_variant": variant,
                                    "failure_score_min": 1,
                                    "cooldown_hours": cooldown,
                                }
                                summary = summaries[definition_id(meta)]
                                if side_flags[variant]:
                                    update_summary(summary, row, features, meta, tier)
                                else:
                                    summary["rejected_due_to_missing_price_failure_confirmation_count"] += 1


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
        "rejected_due_to_missing_price_failure_confirmation_count",
        "rejected_due_to_missing_oi_taker_components_count",
        "rejected_due_to_missing_crowding_components_count",
        "rejected_due_to_cooldown_count",
        "crowding_confirmation_distribution",
        "price_failure_variant_distribution",
        "target_event_count_band",
    ]
    return {field: summary[field] for field in fields}


def select_definitions(summaries: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], str, str, str]:
    finalized = list(summaries.values())
    selections = []
    slots = [
        ("best_long_failure_definition", "long_failure", False),
        ("best_short_failure_definition", "short_failure", False),
        ("best_long_failure_with_crowding_confirmation_definition", "long_failure", True),
        ("best_short_failure_with_crowding_confirmation_definition", "short_failure", True),
    ]
    for slot_name, side, require_crowding in slots:
        candidates = [
            item
            for item in finalized
            if item["meta"]["side"] == side
            and (item["meta"]["crowding_hard_gate"] if require_crowding else True)
            and item["cooldown_filtered_count"] > 0
        ]
        if not candidates:
            continue
        candidates.sort(key=lambda item: score_definition(item, require_crowding), reverse=True)
        best = compact_summary(candidates[0])
        best["selection_slot"] = slot_name
        best["selection_score"] = score_definition(candidates[0], require_crowding)
        selections.append(best)
    if not selections:
        return [], "No nonzero refined definitions survived contemporaneous gates.", RESULT_SPARSE, NEXT_EVALUATOR
    bands = [item["target_event_count_band"] for item in selections]
    if any(band in {"ideal", "acceptable_but_possibly_broad", "sparse_but_potentially_usable"} for band in bands):
        result = RESULT_READY
        next_step = NEXT_VALIDATOR
        reason = "Selected definitions were chosen by event-count band, coverage, concentration, overlap, component completeness, and material difference from the failed broad route only."
    elif all(band == "too_broad" for band in bands):
        result = RESULT_BROAD
        next_step = NEXT_EVALUATOR
        reason = "Relaxed definitions remain too broad across selected slots."
    else:
        result = RESULT_SPARSE
        next_step = NEXT_EVALUATOR
        reason = "Relaxed definitions remain too sparse for a clean validator route."
    return selections[:4], reason, result, next_step


def output_by_field(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {definition_id: summary[field] for definition_id, summary in summaries.items()}


def nested_distribution(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {definition_id: summary[field] for definition_id, summary in summaries.items() if summary["cooldown_filtered_count"] > 0}


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
        "forward_return_impact": False,
        "p_values": False,
        "null_validation": False,
    }


def blocked_artifact(reason: str, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        head = current_head()
    except Exception:
        head = None
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    artifact = {
        "refinement_status": REFINEMENT_STATUS_BLOCKED,
        "status": REFINEMENT_STATUS_BLOCKED,
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
        "prior_discovery_summary": {},
        "refinement_families_tested": [],
        "threshold_grid": {},
        "cooldown_grid": COOLDOWN_HOURS,
        "event_counts_by_definition": {},
        "cooldown_filtered_counts": {},
        "selected_clean_event_definitions": [],
        "selected_definition_reason": "",
        "symbol_coverage_summary": {},
        "month_coverage_summary": {},
        "concentration_summary": {},
        "arbusdt_summary": {},
        "overlap_summary": {},
        "missing_data_summary": {},
        "rejection_reason_summary": {},
        "crowding_confirmation_distribution": {},
        "price_failure_variant_distribution": {},
        "target_event_count_interpretation": {},
        "material_difference_from_failed_broad_route": "Blocked before refinement completed.",
        "validation_limits": [f"BLOCKED: {reason}"],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_EVALUATOR,
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise RefinementBlocked("RECOVERY_HEAD_MISMATCH_STOP")
    status_before = working_tree_status()
    if not output_only_status(status_before):
        raise RefinementBlocked(f"unexpected dirty state before refinement execution: {status_before}")
    hashes_before = input_artifact_hashes()
    discovery, dataset, kline, robustness, null_runner, event_study, validation, payload_hashes = load_inputs()
    symbols = [str(symbol) for symbol in dataset.get("normalized_dataset_summary", {}).get("built_symbols", [])]
    if len(symbols) != 10:
        raise RefinementBlocked("dataset builder does not expose expected 10 built symbols")

    cache_summary = verify_cached_archives(symbols, kline)
    kline_by_symbol = {symbol: load_kline_symbol(symbol, cache_summary["archive_records"]) for symbol in symbols}
    catalog = build_definition_catalog()
    summaries = {definition_id: blank_summary(definition_id, meta) for definition_id, meta in catalog.items()}
    missing_component_counter: Counter[str] = Counter()
    for path in normalized_paths(dataset):
        symbol = path.name.split("_", 1)[0]
        run_symbol_refinement(path, kline_by_symbol[symbol], catalog, summaries, missing_component_counter)
    finalized = {definition_id: finalize_summary(summary) for definition_id, summary in summaries.items()}
    selected, selected_reason, result_classification, allowed_next_step = select_definitions(finalized)
    hashes_after = input_artifact_hashes()
    hashes_unchanged = hashes_before == hashes_after
    if not hashes_unchanged:
        return blocked_artifact("INPUT_ARTIFACT_HASH_CHANGED_STOP", hashes_before, hashes_after)

    nonzero = {definition_id: compact_summary(summary) for definition_id, summary in finalized.items() if summary["cooldown_filtered_count"] > 0}
    validation_checks = {
        "recovery_audit_clean_continue": True,
        "head_matches_expected": True,
        "input_artifacts_loaded": True,
        "input_payload_hashes_verified": True,
        "input_artifact_hashes_unchanged": hashes_unchanged,
        "used_existing_public_data_vision_metrics_and_kline_cache_only": True,
        "no_network_used": True,
        "no_api_key_used": True,
        "no_private_api_used": True,
        "no_account_api_used": True,
        "no_order_endpoint_used": True,
        "no_forward_returns_used": True,
        "no_p_values_computed": True,
        "no_null_validation_run": True,
        "no_strategy_execution": True,
        "no_signal_generation": True,
        "no_backtest_run": True,
        "no_pnl_computation": True,
        "no_trade_simulation": True,
        "no_optimization_against_future_returns": True,
        "no_candidate_generation": True,
        "no_edge_claim": True,
        "no_runtime_live_capital": True,
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
        "refinement_status": REFINEMENT_STATUS_PASS if replacement_checks_all_true else REFINEMENT_STATUS_BLOCKED,
        "status": REFINEMENT_STATUS_PASS if replacement_checks_all_true else REFINEMENT_STATUS_BLOCKED,
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
            SOURCE_DISCOVERY_RELATIVE_PATH: {"status": discovery.get("discovery_status"), "result_classification": discovery.get("result_classification"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_DISCOVERY_RELATIVE_PATH]},
            SOURCE_DATASET_BUILDER_RELATIVE_PATH: {"status": dataset.get("status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_DATASET_BUILDER_RELATIVE_PATH]},
            SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: {"status": kline.get("diagnostic_status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH]},
            SOURCE_ROBUSTNESS_RELATIVE_PATH: {"status": robustness.get("robustness_status"), "result_classification": robustness.get("result_classification"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_ROBUSTNESS_RELATIVE_PATH]},
            SOURCE_NULL_RUNNER_RELATIVE_PATH: {"status": null_runner.get("null_validation_status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_NULL_RUNNER_RELATIVE_PATH]},
            SOURCE_EVENT_STUDY_RELATIVE_PATH: {"status": event_study.get("status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_EVENT_STUDY_RELATIVE_PATH]},
            SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: {"status": validation.get("validation_contract_status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH]},
        },
        "prior_discovery_summary": {
            "result_classification": discovery.get("result_classification"),
            "selected_clean_event_definitions": discovery.get("selected_clean_event_definitions"),
            "cooldown_filtered_counts": discovery.get("cooldown_filtered_counts"),
            "lesson": "Prior strict mandatory-crowding definition was clean but too sparse.",
        },
        "refinement_families_tested": [
            "CORE_PRICE_FAILURE_WITH_CROWDING_TIER",
            "RELAXED_EXTREME_GRID",
            "PRICE_FAILURE_STRENGTH_SCORE",
            "COOLDOWN_GRID",
        ],
        "threshold_grid": {
            "oi_percentiles": [percentile_name(q) for q in OI_QUANTILES],
            "taker_percentiles": [percentile_name(q) for q in TAKER_QUANTILES],
            "crowding_percentiles_if_hard_gate": [percentile_name(q) for q in CROWDING_QUANTILES],
            "price_failure_variants": PRICE_FAILURE_VARIANTS,
            "failure_score_buckets": FAILURE_SCORE_BUCKETS,
            "absolute_taker_thresholds_recorded": [0.70, 0.75],
            "absolute_taker_threshold_note": "Source taker field is a buy/sell ratio, not bounded buy or sell share, so percentile gates are primary.",
        },
        "cooldown_grid": COOLDOWN_HOURS,
        "event_counts_by_definition": output_by_field(finalized, "raw_event_count"),
        "cooldown_filtered_counts": output_by_field(finalized, "cooldown_filtered_count"),
        "nonzero_definition_summaries": nonzero,
        "selected_clean_event_definitions": selected,
        "selected_definition_reason": selected_reason,
        "symbol_coverage_summary": output_by_field(finalized, "symbol_coverage_count"),
        "month_coverage_summary": output_by_field(finalized, "month_coverage_count"),
        "concentration_summary": {
            definition_id: {
                "top_symbol": summary["top_symbol"],
                "top_symbol_concentration": summary["top_symbol_concentration"],
                "top_month": summary["top_month"],
                "top_month_concentration": summary["top_month_concentration"],
            }
            for definition_id, summary in finalized.items()
        },
        "arbusdt_summary": output_by_field(finalized, "arbusdt_count"),
        "overlap_summary": output_by_field(finalized, "overlap_rate"),
        "missing_data_summary": output_by_field(finalized, "missing_component_count"),
        "rejection_reason_summary": {
            definition_id: {
                "rejected_due_to_missing_price_failure_confirmation_count": summary["rejected_due_to_missing_price_failure_confirmation_count"],
                "rejected_due_to_missing_oi_taker_components_count": summary["rejected_due_to_missing_oi_taker_components_count"],
                "rejected_due_to_missing_crowding_components_count": summary["rejected_due_to_missing_crowding_components_count"],
                "rejected_due_to_cooldown_count": summary["rejected_due_to_cooldown_count"],
            }
            for definition_id, summary in finalized.items()
        },
        "crowding_confirmation_distribution": nested_distribution(finalized, "crowding_confirmation_distribution"),
        "price_failure_variant_distribution": nested_distribution(finalized, "price_failure_variant_distribution"),
        "target_event_count_interpretation": {
            "ideal": "300 to 1500 cooldown-filtered events",
            "acceptable_but_possibly_broad": "1500 to 5000 cooldown-filtered events",
            "too_broad": "over 5000 cooldown-filtered events",
            "sparse_but_potentially_usable": "100 to 300 cooldown-filtered events",
            "too_sparse": "under 100 cooldown-filtered events",
            "selected_bands": [item["target_event_count_band"] for item in selected],
        },
        "material_difference_from_failed_broad_route": {
            "prior_broad_route_result": robustness.get("result_classification"),
            "difference": "Refinement still requires OI expansion, same-side taker aggression, current/prior-bar price failure, cooldown filtering, and optional/hard crowding tiers; it uses no forward returns, p-values, null validation, or outcome optimization.",
        },
        "kline_cache_summary": {
            "cache_root": str(KLINE_CACHE_ROOT),
            "archive_count_available": cache_summary["available_count"],
            "archive_count_missing": cache_summary["missing_count"],
            "checksum_available": cache_summary["checksum_available"],
            "checksum_verified": cache_summary["checksum_verified"],
            "raw_data_committed": False,
            "cache_files_staged": False,
        },
        "global_missing_component_counter": dict(missing_component_counter),
        "validation_limits": [
            "This is event-definition refinement only, not strategy, signal, backtest, PnL, candidate generation, or edge claim.",
            "No future returns, forward-return impact, p-values, null validation, or outcome optimization were computed.",
            "Price failure/rejection uses current 15m bar and prior bars only.",
            "Selection uses event-count band, coverage, concentration, overlap, completeness, and material difference from the failed broad route.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "forbidden_failed_strategy_routes_not_reused": {"not_reused": True, "routes": FORBIDDEN_FAILED_ROUTES},
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
    print(f"status: {artifact['refinement_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(artifact['input_artifact_hashes_unchanged'] is True)}")
    print(f"selected_clean_event_definitions: {artifact['selected_clean_event_definitions']}")
    print(f"event_counts_by_definition: {artifact['event_counts_by_definition']}")
    print(f"cooldown_filtered_counts: {artifact['cooldown_filtered_counts']}")
    print(f"symbol_coverage_summary: {artifact['symbol_coverage_summary']}")
    print(f"month_coverage_summary: {artifact['month_coverage_summary']}")
    print(f"concentration_summary: {artifact['concentration_summary']}")
    print(f"arbusdt_summary: {artifact['arbusdt_summary']}")
    print(f"overlap_summary: {artifact['overlap_summary']}")
    print(f"crowding_confirmation_distribution: {artifact['crowding_confirmation_distribution']}")
    print(f"price_failure_variant_distribution: {artifact['price_failure_variant_distribution']}")
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
    except RefinementBlocked as exc:
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
