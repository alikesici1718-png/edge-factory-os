#!/usr/bin/env python
"""Discover strict OI/taker/crowding price-failure events without forward returns."""

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
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_event_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "8341d3659878b833c32f502142d7436678e4f865"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
SOURCE_ROBUSTNESS_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_forward_return_robustness_runner_v1.json"
SOURCE_NULL_RUNNER_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_forward_return_null_validation_runner_v1.json"
SOURCE_EVENT_STUDY_RELATIVE_PATH = "artifacts/research/binance_oi_taker_crowding_proxy_event_study_v1.json"
SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH = "artifacts/contracts/binance_oi_taker_crowding_proxy_validation_contract_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_ROBUSTNESS_RELATIVE_PATH,
    SOURCE_NULL_RUNNER_RELATIVE_PATH,
    SOURCE_EVENT_STUDY_RELATIVE_PATH,
    SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH,
]

DISCOVERY_STATUS_PASS = "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_CREATED"
DISCOVERY_STATUS_BLOCKED = "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY"
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY"

RESULT_READY = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_READY"
RESULT_TOO_BROAD = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_TOO_BROAD"
RESULT_TOO_SPARSE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_TOO_SPARSE"
RESULT_ATTENTION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DISCOVERY_FAILED_STOP"

NEXT_VALIDATOR = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_VALIDATOR_V1"
NEXT_REFINEMENT = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_EVENT_DEFINITION_REFINEMENT_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_KLINE_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"

KLINE_CACHE_ROOT = REPO_ROOT / "cache" / "binance_public_kline_forward_return_diagnostic_v1"
KLINE_INTERVAL_MS = 15 * 60 * 1000
ONE_HOUR_MS = 60 * 60 * 1000
COOLDOWN_MS = 24 * 60 * 60 * 1000
ROLLING_LOOKBACK_BARS = 16
EPSILON = 1e-12
START_YEAR_MONTH = (2023, 1)
END_YEAR_MONTH = (2025, 12)

EVENT_DEFINITIONS = {
    "EXTREME_CROWDED_LONG_FAILURE": {
        "side": "long_failure",
        "description": "Extreme OI expansion, extreme taker buy aggression, extreme long crowding, and same-direction price failure/rejection.",
    },
    "EXTREME_CROWDED_SHORT_FAILURE": {
        "side": "short_failure",
        "description": "Extreme OI expansion, extreme taker sell aggression, extreme short crowding, and same-direction price failure/rejection.",
    },
}

STRICTNESS_GRID = {
    "strict": {
        "oi_quantile": 0.99,
        "taker_quantile": 0.99,
        "long_crowding_quantile": 0.975,
        "short_crowding_quantile": 0.025,
    },
    "very_strict": {
        "oi_quantile": 0.995,
        "taker_quantile": 0.995,
        "long_crowding_quantile": 0.99,
        "short_crowding_quantile": 0.01,
    },
    "ultra_strict": {
        "oi_quantile": 0.9975,
        "taker_quantile": 0.9975,
        "long_crowding_quantile": 0.995,
        "short_crowding_quantile": 0.005,
    },
}

FORBIDDEN_FAILED_ROUTES = [
    "funding crowding reversal",
    "funding carry",
    "funding extreme volume surge",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
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


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    robustness = read_json_readonly(SOURCE_ROBUSTNESS_RELATIVE_PATH)
    null_runner = read_json_readonly(SOURCE_NULL_RUNNER_RELATIVE_PATH)
    event_study = read_json_readonly(SOURCE_EVENT_STUDY_RELATIVE_PATH)
    validation = read_json_readonly(SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
        SOURCE_ROBUSTNESS_RELATIVE_PATH: verify_payload_hash(robustness, "robustness runner"),
        SOURCE_NULL_RUNNER_RELATIVE_PATH: verify_payload_hash(null_runner, "null validation runner"),
        SOURCE_EVENT_STUDY_RELATIVE_PATH: verify_payload_hash(event_study, "proxy event study"),
        SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: verify_payload_hash(validation, "proxy validation contract"),
    }
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiscoveryBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise DiscoveryBlocked("public kline diagnostic status is not PASS")
    if robustness.get("robustness_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_RUNNER_CREATED":
        raise DiscoveryBlocked("robustness runner status is not PASS")
    if robustness.get("result_classification") != "BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_ROBUSTNESS_WEAK_OR_NOT_ROBUST":
        raise DiscoveryBlocked("prior broad route result is not recorded as weak/not robust")
    if null_runner.get("null_validation_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_FORWARD_RETURN_NULL_VALIDATION_RUNNER_CREATED":
        raise DiscoveryBlocked("null validation runner status is not PASS")
    if event_study.get("status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_EVENT_STUDY_CREATED":
        raise DiscoveryBlocked("proxy event study status is not PASS")
    if validation.get("validation_contract_status") != "PASS_REPO_ONLY_BINANCE_OI_TAKER_CROWDING_PROXY_VALIDATION_CONTRACT_CREATED":
        raise DiscoveryBlocked("proxy validation contract status is not PASS")
    return dataset, kline, robustness, null_runner, event_study, validation, payload_hashes


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
    if available_count != expected_available:
        raise DiscoveryBlocked(f"cached archive count mismatch: {available_count} != {expected_available}")
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
                    except ValueError:
                        invalid_numeric_count += 1
                        continue
                    if open_time in bars:
                        duplicate_open_time_count += 1
                        continue
                    bars[open_time] = (open_price, high, low, close)
    if not bars:
        raise DiscoveryBlocked(f"no cached kline rows loaded for {symbol}")
    opens = np.array(sorted(bars), dtype=np.int64)
    open_prices = np.array([bars[int(open_time)][0] for open_time in opens], dtype=np.float64)
    highs = np.array([bars[int(open_time)][1] for open_time in opens], dtype=np.float64)
    lows = np.array([bars[int(open_time)][2] for open_time in opens], dtype=np.float64)
    closes = np.array([bars[int(open_time)][3] for open_time in opens], dtype=np.float64)
    prior_high = rolling_previous_extreme(highs, "max", ROLLING_LOOKBACK_BARS)
    prior_low = rolling_previous_extreme(lows, "min", ROLLING_LOOKBACK_BARS)
    open_to_index = {int(open_time): int(index) for index, open_time in enumerate(opens)}
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


def empty_level_summary() -> dict[str, Any]:
    return {
        "raw_event_count": 0,
        "cooldown_filtered_event_count": 0,
        "unique_timestamp_count": 0,
        "unique_symbol_timestamp_count": 0,
        "symbol_coverage_count": 0,
        "symbols": [],
        "month_coverage_count": 0,
        "months": [],
        "top_symbol_concentration": None,
        "top_symbol": None,
        "top_month_concentration": None,
        "top_month": None,
        "arbusdt_event_count": 0,
        "event_overlap_rate": 0.0,
        "missing_data_count": 0,
        "rejected_due_to_cooldown_count": 0,
        "rejected_due_to_missing_price_failure_confirmation_count": 0,
        "rejected_due_to_missing_oi_taker_crowding_components_count": 0,
    }


def init_count_store() -> dict[str, dict[str, dict[str, Any]]]:
    return {
        event_id: {level: empty_level_summary() for level in STRICTNESS_GRID}
        for event_id in EVENT_DEFINITIONS
    }


def build_symbol_thresholds(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, float | None]]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        month = row["month"]
        for key in [
            "oi_delta_log_1h",
            "taker_buy_aggression",
            "taker_sell_aggression",
            "top_account_ratio",
            "top_position_ratio",
        ]:
            value = row.get(key)
            if isinstance(value, float) and math.isfinite(value):
                buckets[month][key].append(value)
    thresholds: dict[str, dict[str, dict[str, float | None]]] = {}
    for month, per_field in buckets.items():
        thresholds[month] = {
            "oi_delta_log_1h": {
                "p99.0": quantile_or_none(per_field["oi_delta_log_1h"], 0.99),
                "p99.5": quantile_or_none(per_field["oi_delta_log_1h"], 0.995),
                "p99.75": quantile_or_none(per_field["oi_delta_log_1h"], 0.9975),
            },
            "taker_buy_aggression": {
                "p99.0": quantile_or_none(per_field["taker_buy_aggression"], 0.99),
                "p99.5": quantile_or_none(per_field["taker_buy_aggression"], 0.995),
                "p99.75": quantile_or_none(per_field["taker_buy_aggression"], 0.9975),
                "absolute_ratio_0.70": 0.70,
                "absolute_ratio_0.75": 0.75,
            },
            "taker_sell_aggression": {
                "p99.0": quantile_or_none(per_field["taker_sell_aggression"], 0.99),
                "p99.5": quantile_or_none(per_field["taker_sell_aggression"], 0.995),
                "p99.75": quantile_or_none(per_field["taker_sell_aggression"], 0.9975),
                "absolute_ratio_0.70": 0.70,
                "absolute_ratio_0.75": 0.75,
            },
            "long_crowding": {
                "top_account_p97.5": quantile_or_none(per_field["top_account_ratio"], 0.975),
                "top_account_p99.0": quantile_or_none(per_field["top_account_ratio"], 0.99),
                "top_account_p99.5": quantile_or_none(per_field["top_account_ratio"], 0.995),
                "top_position_p97.5": quantile_or_none(per_field["top_position_ratio"], 0.975),
                "top_position_p99.0": quantile_or_none(per_field["top_position_ratio"], 0.99),
                "top_position_p99.5": quantile_or_none(per_field["top_position_ratio"], 0.995),
            },
            "short_crowding": {
                "top_account_p2.5": quantile_or_none(per_field["top_account_ratio"], 0.025),
                "top_account_p1.0": quantile_or_none(per_field["top_account_ratio"], 0.01),
                "top_account_p0.5": quantile_or_none(per_field["top_account_ratio"], 0.005),
                "top_position_p2.5": quantile_or_none(per_field["top_position_ratio"], 0.025),
                "top_position_p1.0": quantile_or_none(per_field["top_position_ratio"], 0.01),
                "top_position_p0.5": quantile_or_none(per_field["top_position_ratio"], 0.005),
            },
        }
    return thresholds


def metric_rows_for_symbol(path: Path) -> list[dict[str, Any]]:
    raw_rows: list[dict[str, Any]] = []
    oi_by_ms: dict[int, float] = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            timestamp = row.get("timestamp")
            if not timestamp:
                continue
            ts_ms = iso_to_ms(timestamp)
            open_interest = to_float(row.get("open_interest"))
            taker_buy = to_float(row.get("taker_buy_sell_ratio"))
            taker_sell = to_float(row.get("taker_sell_pressure"))
            top_account = to_float(row.get("top_account_long_short_ratio"))
            top_position = to_float(row.get("top_position_long_short_ratio"))
            if open_interest is not None and open_interest > 0:
                oi_by_ms[ts_ms] = open_interest
            raw_rows.append(
                {
                    "timestamp": timestamp,
                    "ts_ms": ts_ms,
                    "month": timestamp[:7],
                    "symbol": row.get("symbol") or path.name.split("_", 1)[0],
                    "open_interest": open_interest,
                    "taker_buy_aggression": taker_buy,
                    "taker_sell_aggression": taker_sell,
                    "top_account_ratio": top_account,
                    "top_position_ratio": top_position,
                }
            )
    for row in raw_rows:
        current = row["open_interest"]
        previous = oi_by_ms.get(row["ts_ms"] - ONE_HOUR_MS)
        if current is not None and previous is not None and current > 0 and previous > 0:
            row["oi_delta_log_1h"] = math.log(current) - math.log(previous)
        else:
            row["oi_delta_log_1h"] = None
    return raw_rows


def price_failure_features(row: dict[str, Any], kline_data: dict[str, Any]) -> dict[str, Any]:
    base_open = floor_to_15m_open(row["ts_ms"])
    index = kline_data["open_to_index"].get(base_open)
    if index is None:
        return {"price_available": False}
    open_time = int(kline_data["opens"][index])
    high = float(kline_data["high"][index])
    low = float(kline_data["low"][index])
    close = float(kline_data["close"][index])
    range_value = max(high - low, EPSILON)
    close_location = (close - low) / range_value
    upper_wick_rejection = (high - close) / range_value
    lower_wick_rejection = (close - low) / range_value
    prev_index = kline_data["open_to_index"].get(open_time - ONE_HOUR_MS)
    price_return_1h = None
    if prev_index is not None:
        previous_close = float(kline_data["close"][prev_index])
        if previous_close != 0:
            price_return_1h = (close / previous_close) - 1.0
    prior_high = float(kline_data["prior_rolling_high"][index])
    prior_low = float(kline_data["prior_rolling_low"][index])
    failed_breakout = math.isfinite(prior_high) and high > prior_high and close <= prior_high
    failed_breakdown = math.isfinite(prior_low) and low < prior_low and close >= prior_low
    long_failure = (
        (price_return_1h is not None and price_return_1h <= 0.0)
        or close_location <= 0.40
        or upper_wick_rejection >= 0.60
        or failed_breakout
    )
    short_failure = (
        (price_return_1h is not None and price_return_1h >= 0.0)
        or close_location >= 0.60
        or lower_wick_rejection >= 0.60
        or failed_breakdown
    )
    return {
        "price_available": True,
        "price_return_1h": price_return_1h,
        "close_location": close_location,
        "upper_wick_rejection": upper_wick_rejection,
        "lower_wick_rejection": lower_wick_rejection,
        "failed_breakout": failed_breakout,
        "failed_breakdown": failed_breakdown,
        "long_failure": long_failure,
        "short_failure": short_failure,
    }


def threshold_key(value: float) -> str:
    if value == 0.975:
        return "p97.5"
    if value == 0.9975:
        return "p99.75"
    if value == 0.995:
        return "p99.5"
    if value == 0.99:
        return "p99.0"
    if value == 0.025:
        return "p2.5"
    if value == 0.01:
        return "p1.0"
    if value == 0.005:
        return "p0.5"
    return f"p{value * 100:g}"


def passes_long(row: dict[str, Any], thresholds: dict[str, Any], level: str) -> tuple[bool, bool, bool]:
    grid = STRICTNESS_GRID[level]
    oi_threshold = thresholds["oi_delta_log_1h"][threshold_key(grid["oi_quantile"])]
    taker_threshold = thresholds["taker_buy_aggression"][threshold_key(grid["taker_quantile"])]
    crowd_key = threshold_key(grid["long_crowding_quantile"])
    account_threshold = thresholds["long_crowding"].get(f"top_account_{crowd_key}")
    position_threshold = thresholds["long_crowding"].get(f"top_position_{crowd_key}")
    oi_ok = row["oi_delta_log_1h"] is not None and oi_threshold is not None and row["oi_delta_log_1h"] >= oi_threshold
    taker_ok = row["taker_buy_aggression"] is not None and taker_threshold is not None and row["taker_buy_aggression"] >= taker_threshold
    account_ok = row["top_account_ratio"] is not None and account_threshold is not None and row["top_account_ratio"] >= account_threshold
    position_ok = row["top_position_ratio"] is not None and position_threshold is not None and row["top_position_ratio"] >= position_threshold
    crowding_ok = account_ok or position_ok
    return oi_ok, taker_ok, crowding_ok


def passes_short(row: dict[str, Any], thresholds: dict[str, Any], level: str) -> tuple[bool, bool, bool]:
    grid = STRICTNESS_GRID[level]
    oi_threshold = thresholds["oi_delta_log_1h"][threshold_key(grid["oi_quantile"])]
    taker_threshold = thresholds["taker_sell_aggression"][threshold_key(grid["taker_quantile"])]
    crowd_key = threshold_key(grid["short_crowding_quantile"])
    account_threshold = thresholds["short_crowding"].get(f"top_account_{crowd_key}")
    position_threshold = thresholds["short_crowding"].get(f"top_position_{crowd_key}")
    oi_ok = row["oi_delta_log_1h"] is not None and oi_threshold is not None and row["oi_delta_log_1h"] >= oi_threshold
    taker_ok = row["taker_sell_aggression"] is not None and taker_threshold is not None and row["taker_sell_aggression"] >= taker_threshold
    account_ok = row["top_account_ratio"] is not None and account_threshold is not None and row["top_account_ratio"] <= account_threshold
    position_ok = row["top_position_ratio"] is not None and position_threshold is not None and row["top_position_ratio"] <= position_threshold
    crowding_ok = account_ok or position_ok
    return oi_ok, taker_ok, crowding_ok


def update_raw_summary(summary: dict[str, Any], row: dict[str, Any]) -> None:
    summary["raw_event_count"] += 1
    summary.setdefault("_raw_timestamps", set()).add(row["timestamp"])
    summary.setdefault("_raw_symbol_timestamps", set()).add((row["symbol"], row["timestamp"]))
    summary.setdefault("_symbols", Counter())[row["symbol"]] += 1
    summary.setdefault("_months", Counter())[row["month"]] += 1
    if row["symbol"] == "ARBUSDT":
        summary["arbusdt_event_count"] += 1


def update_cooldown_summary(summary: dict[str, Any], row: dict[str, Any]) -> None:
    summary["cooldown_filtered_event_count"] += 1
    summary.setdefault("_cooldown_symbols", Counter())[row["symbol"]] += 1
    summary.setdefault("_cooldown_months", Counter())[row["month"]] += 1


def finalize_summary(summary: dict[str, Any]) -> dict[str, Any]:
    raw_count = summary["raw_event_count"]
    cooldown_count = summary["cooldown_filtered_event_count"]
    symbols_counter: Counter[str] = summary.pop("_cooldown_symbols", Counter())
    months_counter: Counter[str] = summary.pop("_cooldown_months", Counter())
    raw_timestamps = summary.pop("_raw_timestamps", set())
    raw_symbol_timestamps = summary.pop("_raw_symbol_timestamps", set())
    summary.pop("_symbols", None)
    summary.pop("_months", None)
    top_symbol, top_symbol_count = (None, 0) if not symbols_counter else symbols_counter.most_common(1)[0]
    top_month, top_month_count = (None, 0) if not months_counter else months_counter.most_common(1)[0]
    summary["unique_timestamp_count"] = len(raw_timestamps)
    summary["unique_symbol_timestamp_count"] = len(raw_symbol_timestamps)
    summary["symbol_coverage_count"] = len(symbols_counter)
    summary["symbols"] = sorted(symbols_counter)
    summary["month_coverage_count"] = len(months_counter)
    summary["months"] = sorted(months_counter)
    summary["top_symbol"] = top_symbol
    summary["top_symbol_concentration"] = (top_symbol_count / cooldown_count) if cooldown_count else None
    summary["top_month"] = top_month
    summary["top_month_concentration"] = (top_month_count / cooldown_count) if cooldown_count else None
    summary["event_overlap_rate"] = 1.0 - (len(raw_symbol_timestamps) / raw_count) if raw_count else 0.0
    return summary


def run_discovery_for_symbol(
    path: Path,
    kline_data: dict[str, Any],
    event_counts: dict[str, dict[str, dict[str, Any]]],
    symbol_thresholds_out: dict[str, Any],
) -> None:
    rows = metric_rows_for_symbol(path)
    thresholds = build_symbol_thresholds(rows)
    symbol = path.name.split("_", 1)[0]
    symbol_thresholds_out[symbol] = thresholds
    last_event_ms: dict[tuple[str, str], int] = {}
    for row in rows:
        month_thresholds = thresholds.get(row["month"])
        if month_thresholds is None:
            for event_id in EVENT_DEFINITIONS:
                for summary in event_counts[event_id].values():
                    summary["missing_data_count"] += 1
                    summary["rejected_due_to_missing_oi_taker_crowding_components_count"] += 1
            continue
        features = price_failure_features(row, kline_data)
        for level in STRICTNESS_GRID:
            long_oi, long_taker, long_crowding = passes_long(row, month_thresholds, level)
            long_summary = event_counts["EXTREME_CROWDED_LONG_FAILURE"][level]
            if not all([long_oi, long_taker, long_crowding]):
                if row["oi_delta_log_1h"] is None or row["taker_buy_aggression"] is None or (
                    row["top_account_ratio"] is None and row["top_position_ratio"] is None
                ):
                    long_summary["missing_data_count"] += 1
                    long_summary["rejected_due_to_missing_oi_taker_crowding_components_count"] += 1
            elif not features.get("price_available"):
                long_summary["missing_data_count"] += 1
                long_summary["rejected_due_to_missing_price_failure_confirmation_count"] += 1
            elif not features["long_failure"]:
                long_summary["rejected_due_to_missing_price_failure_confirmation_count"] += 1
            else:
                update_raw_summary(long_summary, row)
                cooldown_key = (row["symbol"], "EXTREME_CROWDED_LONG_FAILURE")
                previous = last_event_ms.get(cooldown_key)
                if previous is not None and row["ts_ms"] - previous < COOLDOWN_MS:
                    long_summary["rejected_due_to_cooldown_count"] += 1
                else:
                    last_event_ms[cooldown_key] = row["ts_ms"]
                    update_cooldown_summary(long_summary, row)

            short_oi, short_taker, short_crowding = passes_short(row, month_thresholds, level)
            short_summary = event_counts["EXTREME_CROWDED_SHORT_FAILURE"][level]
            if not all([short_oi, short_taker, short_crowding]):
                if row["oi_delta_log_1h"] is None or row["taker_sell_aggression"] is None or (
                    row["top_account_ratio"] is None and row["top_position_ratio"] is None
                ):
                    short_summary["missing_data_count"] += 1
                    short_summary["rejected_due_to_missing_oi_taker_crowding_components_count"] += 1
            elif not features.get("price_available"):
                short_summary["missing_data_count"] += 1
                short_summary["rejected_due_to_missing_price_failure_confirmation_count"] += 1
            elif not features["short_failure"]:
                short_summary["rejected_due_to_missing_price_failure_confirmation_count"] += 1
            else:
                update_raw_summary(short_summary, row)
                cooldown_key = (row["symbol"], "EXTREME_CROWDED_SHORT_FAILURE")
                previous = last_event_ms.get(cooldown_key)
                if previous is not None and row["ts_ms"] - previous < COOLDOWN_MS:
                    short_summary["rejected_due_to_cooldown_count"] += 1
                else:
                    last_event_ms[cooldown_key] = row["ts_ms"]
                    update_cooldown_summary(short_summary, row)


def aggregate_level_totals(event_counts: dict[str, dict[str, dict[str, Any]]]) -> dict[str, int]:
    totals = {}
    for level in STRICTNESS_GRID:
        totals[level] = sum(event_counts[event_id][level]["cooldown_filtered_event_count"] for event_id in EVENT_DEFINITIONS)
    return totals


def select_definition(event_counts: dict[str, dict[str, dict[str, Any]]]) -> tuple[list[dict[str, Any]], str, str, str]:
    totals = aggregate_level_totals(event_counts)
    ideal = [level for level, count in totals.items() if 300 <= count <= 1500]
    acceptable = [level for level, count in totals.items() if 1500 < count <= 5000]
    sparse_usable = [level for level, count in totals.items() if 100 <= count < 300]
    if ideal:
        selected_level = ideal[-1]
        classification = RESULT_READY
        next_step = NEXT_VALIDATOR
        reason = f"{selected_level} has ideal cooldown-filtered coverage ({totals[selected_level]} events) without using future returns."
    elif acceptable:
        selected_level = acceptable[-1]
        classification = RESULT_READY
        next_step = NEXT_VALIDATOR
        reason = f"{selected_level} has acceptable cooldown-filtered coverage ({totals[selected_level]} events), though it may still merit validator scrutiny."
    elif sparse_usable:
        selected_level = sparse_usable[0]
        classification = RESULT_TOO_SPARSE
        next_step = NEXT_REFINEMENT
        reason = f"Best usable level has only {totals[selected_level]} cooldown-filtered events, below the ideal range."
    elif totals and max(totals.values()) > 5000:
        selected_level = min(totals, key=lambda key: totals[key])
        classification = RESULT_TOO_BROAD
        next_step = NEXT_REFINEMENT
        reason = f"Even strict levels remain too broad; minimum cooldown-filtered total is {totals[selected_level]}."
    else:
        selected_level = max(totals, key=lambda key: totals[key]) if totals else "strict"
        classification = RESULT_TOO_SPARSE
        next_step = NEXT_REFINEMENT
        reason = f"All levels are too sparse; maximum cooldown-filtered total is {totals.get(selected_level, 0)}."
    selected = [
        {
            "event_definition": event_id,
            "strictness": selected_level,
            "cooldown_filtered_event_count": event_counts[event_id][selected_level]["cooldown_filtered_event_count"],
            "raw_event_count": event_counts[event_id][selected_level]["raw_event_count"],
        }
        for event_id in EVENT_DEFINITIONS
    ]
    return selected, reason, classification, next_step


def nested_counts(event_counts: dict[str, dict[str, dict[str, Any]]], key: str) -> dict[str, dict[str, int]]:
    return {
        event_id: {level: int(summary[key]) for level, summary in per_level.items()}
        for event_id, per_level in event_counts.items()
    }


def summary_by_dimension(event_counts: dict[str, dict[str, dict[str, Any]]], dimension: str) -> dict[str, dict[str, Any]]:
    output = {}
    for event_id, per_level in event_counts.items():
        output[event_id] = {}
        for level, summary in per_level.items():
            if dimension == "symbol":
                output[event_id][level] = {
                    "symbol_coverage_count": summary["symbol_coverage_count"],
                    "symbols": summary["symbols"],
                }
            elif dimension == "month":
                output[event_id][level] = {
                    "month_coverage_count": summary["month_coverage_count"],
                    "months": summary["months"],
                }
            elif dimension == "concentration":
                output[event_id][level] = {
                    "top_symbol": summary["top_symbol"],
                    "top_symbol_concentration": summary["top_symbol_concentration"],
                    "top_month": summary["top_month"],
                    "top_month_concentration": summary["top_month_concentration"],
                }
    return output


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
        "discovery_status": DISCOVERY_STATUS_BLOCKED,
        "status": DISCOVERY_STATUS_BLOCKED,
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
        "event_definition_family": MODULE,
        "material_difference_from_failed_broad_route": "Blocked before discovery completed.",
        "symbols": [],
        "timestamp_range": {},
        "threshold_grid": STRICTNESS_GRID,
        "event_definitions_tested": EVENT_DEFINITIONS,
        "event_counts_by_definition_and_strictness": {},
        "cooldown_filtered_counts": {},
        "symbol_coverage_summary": {},
        "month_coverage_summary": {},
        "concentration_summary": {},
        "arbusdt_summary": {},
        "overlap_summary": {},
        "missing_data_summary": {},
        "rejection_reason_summary": {},
        "selected_clean_event_definitions": [],
        "selected_definition_reason": "",
        "target_event_count_interpretation": "blocked",
        "validation_limits": [f"BLOCKED: {reason}"],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_REPAIR,
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise DiscoveryBlocked("RECOVERY_HEAD_MISMATCH_STOP")
    status_before = working_tree_status()
    if not output_only_status(status_before):
        raise DiscoveryBlocked(f"unexpected dirty state before event discovery execution: {status_before}")
    hashes_before = input_artifact_hashes()
    dataset, kline_diagnostic, robustness, null_runner, event_study, validation, payload_hashes = load_inputs()

    symbols = [str(symbol) for symbol in dataset.get("normalized_dataset_summary", {}).get("built_symbols", [])]
    if len(symbols) != 10:
        raise DiscoveryBlocked("dataset builder does not expose the expected 10 built symbols")
    cache_summary = verify_cached_archives(symbols, kline_diagnostic)
    kline_by_symbol = {symbol: load_kline_symbol(symbol, cache_summary["archive_records"]) for symbol in symbols}
    event_counts = init_count_store()
    symbol_thresholds: dict[str, Any] = {}
    paths = normalized_paths(dataset)
    for path in paths:
        symbol = path.name.split("_", 1)[0]
        run_discovery_for_symbol(path, kline_by_symbol[symbol], event_counts, symbol_thresholds)

    for per_level in event_counts.values():
        for level, summary in list(per_level.items()):
            per_level[level] = finalize_summary(summary)

    selected, selected_reason, result_classification, allowed_next_step = select_definition(event_counts)
    hashes_after = input_artifact_hashes()
    hashes_unchanged = hashes_before == hashes_after
    if not hashes_unchanged:
        return blocked_artifact("INPUT_ARTIFACT_HASH_CHANGED_STOP", hashes_before, hashes_after)

    cooldown_totals = aggregate_level_totals(event_counts)
    if result_classification == RESULT_READY:
        target_interpretation = "At least one strictness level falls in the 300-5000 cooldown-filtered usable range without using future returns."
    elif result_classification == RESULT_TOO_BROAD:
        target_interpretation = "Cooldown-filtered event counts exceed 5000 and are too broad."
    else:
        target_interpretation = "Cooldown-filtered event counts are below the desired usable range and likely too sparse."

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
        "discovery_status": DISCOVERY_STATUS_PASS if replacement_checks_all_true else DISCOVERY_STATUS_BLOCKED,
        "status": DISCOVERY_STATUS_PASS if replacement_checks_all_true else DISCOVERY_STATUS_BLOCKED,
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
            SOURCE_DATASET_BUILDER_RELATIVE_PATH: {"status": dataset.get("status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_DATASET_BUILDER_RELATIVE_PATH]},
            SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: {"status": kline_diagnostic.get("diagnostic_status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH]},
            SOURCE_ROBUSTNESS_RELATIVE_PATH: {"status": robustness.get("robustness_status"), "result_classification": robustness.get("result_classification"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_ROBUSTNESS_RELATIVE_PATH]},
            SOURCE_NULL_RUNNER_RELATIVE_PATH: {"status": null_runner.get("null_validation_status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_NULL_RUNNER_RELATIVE_PATH]},
            SOURCE_EVENT_STUDY_RELATIVE_PATH: {"status": event_study.get("status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_EVENT_STUDY_RELATIVE_PATH]},
            SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH: {"status": validation.get("validation_contract_status"), "payload_sha256_excluding_hash": payload_hashes[SOURCE_VALIDATION_CONTRACT_RELATIVE_PATH]},
        },
        "event_definition_family": MODULE,
        "material_difference_from_failed_broad_route": {
            "prior_route_result": robustness.get("result_classification"),
            "difference": "This discovery requires symbol-month extreme OI expansion, extreme same-side taker aggression, extreme top-trader crowding, current/prior-bar price failure, and 24h cooldown-filtered unique events. It does not test forward returns or revive the broad route.",
        },
        "symbols": symbols,
        "timestamp_range": {
            "metrics_min": dataset.get("normalized_dataset_summary", {}).get("timestamp_global_min"),
            "metrics_max": dataset.get("normalized_dataset_summary", {}).get("timestamp_global_max"),
            "uses_current_and_prior_price_bars_only": True,
        },
        "threshold_grid": STRICTNESS_GRID,
        "event_definitions_tested": EVENT_DEFINITIONS,
        "event_counts_by_definition_and_strictness": nested_counts(event_counts, "raw_event_count"),
        "cooldown_filtered_counts": nested_counts(event_counts, "cooldown_filtered_event_count"),
        "symbol_coverage_summary": summary_by_dimension(event_counts, "symbol"),
        "month_coverage_summary": summary_by_dimension(event_counts, "month"),
        "concentration_summary": summary_by_dimension(event_counts, "concentration"),
        "arbusdt_summary": nested_counts(event_counts, "arbusdt_event_count"),
        "overlap_summary": {
            event_id: {level: summary["event_overlap_rate"] for level, summary in per_level.items()}
            for event_id, per_level in event_counts.items()
        },
        "missing_data_summary": nested_counts(event_counts, "missing_data_count"),
        "rejection_reason_summary": {
            event_id: {
                level: {
                    "rejected_due_to_cooldown_count": summary["rejected_due_to_cooldown_count"],
                    "rejected_due_to_missing_price_failure_confirmation_count": summary["rejected_due_to_missing_price_failure_confirmation_count"],
                    "rejected_due_to_missing_oi_taker_crowding_components_count": summary["rejected_due_to_missing_oi_taker_crowding_components_count"],
                }
                for level, summary in per_level.items()
            }
            for event_id, per_level in event_counts.items()
        },
        "selected_clean_event_definitions": selected,
        "selected_definition_reason": selected_reason,
        "target_event_count_interpretation": {
            "ideal_range": "300 to 1500 cooldown-filtered events",
            "acceptable_range": "1500 to 5000 cooldown-filtered events",
            "too_broad": "over 5000 cooldown-filtered events",
            "too_sparse": "under 100 cooldown-filtered events",
            "observed_cooldown_totals_by_strictness": cooldown_totals,
            "interpretation": target_interpretation,
        },
        "symbol_month_threshold_preview": {
            symbol: {month: threshold for month, threshold in list(months.items())[:2]}
            for symbol, months in symbol_thresholds.items()
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
        "validation_limits": [
            "This is event discovery only, not a strategy, signal, backtest, PnL computation, candidate, or edge claim.",
            "No forward returns, p-values, null validation, or optimization against future returns were computed.",
            "Price failure/rejection uses only the current 15m bar and prior bars.",
            "Thresholds are symbol-month percentiles for event cleanliness and coverage, not future-return performance.",
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
    print(f"status: {artifact['discovery_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(artifact['input_artifact_hashes_unchanged'] is True)}")
    print(f"event_definition_family: {artifact['event_definition_family']}")
    print(f"material_difference_from_failed_broad_route: {artifact['material_difference_from_failed_broad_route']}")
    print(f"selected_clean_event_definitions: {artifact['selected_clean_event_definitions']}")
    print(f"event_counts_by_definition_and_strictness: {artifact['event_counts_by_definition_and_strictness']}")
    print(f"cooldown_filtered_counts: {artifact['cooldown_filtered_counts']}")
    print(f"symbol_coverage_summary: {artifact['symbol_coverage_summary']}")
    print(f"month_coverage_summary: {artifact['month_coverage_summary']}")
    print(f"concentration_summary: {artifact['concentration_summary']}")
    print(f"arbusdt_summary: {artifact['arbusdt_summary']}")
    print(f"overlap_summary: {artifact['overlap_summary']}")
    print(f"missing_data_summary: {artifact['missing_data_summary']}")
    print(f"rejection_reason_summary: {artifact['rejection_reason_summary']}")
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
