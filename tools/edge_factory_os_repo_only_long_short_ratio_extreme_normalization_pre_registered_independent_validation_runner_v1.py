#!/usr/bin/env python3
"""Repo-only pre-registered independent validation runner for L/S ratio normalization.

This module evaluates only the frozen account/position divergence volatility
diagnostic on 2026+ public Binance Data Vision archives. It does not create a
strategy, signal, candidate, backtest, PnL, or runtime action.
"""

from __future__ import annotations

import hashlib
import importlib.util
import csv
import io
import json
import math
import random
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


MODULE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_RUNNER_V1"
EXPECTED_HEAD = "7e3c4c199127f04efd2fc69af270ebef96fc53af"
THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_RELATIVE_PATH = (
    "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_"
    "pre_registered_independent_validation_runner_v1.py"
)
ARTIFACT_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_"
    "pre_registered_independent_validation_runner_v1.json"
)
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

CONTRACT_RELATIVE_PATH = (
    "artifacts/contracts/long_short_ratio_extreme_normalization_"
    "pre_registered_independent_validation_contract_v1.json"
)
EVALUATOR_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_"
    "volatility_robustness_evaluator_v1.json"
)
ROBUSTNESS_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_"
    "volatility_robustness_runner_v1.json"
)
VALIDATOR_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_event_validator_v1.json"
)
DISCOVERY_RELATIVE_PATH = (
    "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json"
)
DATASET_RELATIVE_PATH = (
    "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
)
INPUT_RELATIVE_PATHS = [
    CONTRACT_RELATIVE_PATH,
    EVALUATOR_RELATIVE_PATH,
    ROBUSTNESS_RELATIVE_PATH,
    VALIDATOR_RELATIVE_PATH,
    DISCOVERY_RELATIVE_PATH,
    DATASET_RELATIVE_PATH,
]

ARCHIVE_HELPER_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_"
    "pre_registered_independent_validation_runner_v1.py"
)
GENERIC_2026_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_"
    "pre_registered_independent_validation_runner_v1.py"
)
DISCOVERY_TOOL = (
    REPO_ROOT
    / "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_event_discovery_v1.py"
)

PASS_CLASSIFICATION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_PASS_DIAGNOSTIC_ONLY"
)
FAIL_CLASSIFICATION = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_FAIL"
INCONCLUSIVE_CLASSIFICATION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE"
)
DATA_QUALITY_CLASSIFICATION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_DATA_QUALITY_ATTENTION"
)
FAILED_STOP_CLASSIFICATION = (
    "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_FAILED_STOP"
)

ALLOWED_NEXT_BY_CLASSIFICATION = {
    PASS_CLASSIFICATION: "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_VALIDATION_EVALUATOR_V1",
    FAIL_CLASSIFICATION: "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_ROUTE_CLOSE_OR_REDESIGN_EVALUATOR_V1",
    INCONCLUSIVE_CLASSIFICATION: (
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_INDEPENDENT_SAMPLE_ACCUMULATION_MONITOR_V1"
    ),
    DATA_QUALITY_CLASSIFICATION: "BINANCE_PUBLIC_2026_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1",
    FAILED_STOP_CLASSIFICATION: "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VALIDATION_RECOVERY_REVIEW_V1",
}

SYMBOLS_REQUESTED = [
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
PRIMARY_SELECTION_SLOT = "optional_account_position_divergence_resolution_candidate"
PRIMARY_HORIZONS = {"15m": 1, "1h": 4, "4h": 16}
PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528
VALIDATION_START = date(2026, 1, 1)
KLINE_INTERVAL_MS = 15 * 60 * 1000
CACHE_ROOT = (
    REPO_ROOT
    / "cache"
    / "long_short_ratio_extreme_normalization_pre_registered_independent_validation_runner_v1"
)

FORBIDDEN_ACTIONS_CONFIRMED_FALSE = {
    "strategy": False,
    "signal": False,
    "backtest": False,
    "pnl": False,
    "trade_simulation": False,
    "optimization_against_validation_outcomes": False,
    "candidate_generation": False,
    "edge_claim": False,
    "runtime_live_capital_order_private_api_account_api_api_key": False,
    "use_2023_2025_as_independent_validation": False,
    "changed_event_definitions": False,
    "changed_thresholds": False,
    "changed_horizons": False,
    "promoted_signed_returns": False,
}


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def git_lines(args: list[str]) -> list[str]:
    out = run_git(args)
    return [line for line in out.splitlines() if line.strip()]


def recovery_audit() -> dict[str, Any]:
    current_head = run_git(["rev-parse", "HEAD"])
    branch = run_git(["branch", "--show-current"])
    porcelain = git_lines(["status", "--porcelain"])
    staged = git_lines(["diff", "--name-only", "--cached"])
    modified = git_lines(["diff", "--name-only"])
    deleted = [
        line[3:]
        for line in porcelain
        if line.startswith(" D ") or line.startswith("D  ") or line.startswith("D ")
    ]
    untracked = [line[3:] for line in porcelain if line.startswith("?? ")]
    head_matches = current_head == EXPECTED_HEAD
    allowed_in_progress = {
        MODULE_RELATIVE_PATH.replace("/", "\\"),
        MODULE_RELATIVE_PATH,
        ARTIFACT_RELATIVE_PATH.replace("/", "\\"),
        ARTIFACT_RELATIVE_PATH,
    }
    dirty_paths = set(modified + deleted + untracked)
    clean = (
        not staged
        and head_matches
        and all(path in allowed_in_progress for path in dirty_paths)
        and all(
            line.startswith("?? ") and line[3:] in allowed_in_progress
            for line in porcelain
        )
    )
    recovery_decision = "RECOVERY_AUDIT_CLEAN_CONTINUE" if head_matches and clean else "RECOVERY_AUDIT_STOP"
    return {
        "current_head": current_head,
        "expected_head": EXPECTED_HEAD,
        "branch": branch,
        "git_status_porcelain": porcelain,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "head_matches_expected": head_matches,
        "repo_clean": clean,
        "recovery_decision": recovery_decision,
        "recovery_audit_status": "PASS" if recovery_decision.endswith("CONTINUE") else "STOP",
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel in INPUT_RELATIVE_PATHS:
        path = REPO_ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f"missing required input artifact: {rel}")
        hashes[rel] = sha256_file(path)
    return hashes


def load_json(rel_path: str) -> dict[str, Any]:
    with (REPO_ROOT / rel_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_float(value: Any) -> float:
    try:
        if value is None:
            return math.nan
        converted = float(value)
        return converted if math.isfinite(converted) else math.nan
    except (TypeError, ValueError):
        return math.nan


def finite_mean(values: list[float]) -> float | None:
    clean = [float(v) for v in values if math.isfinite(float(v))]
    if not clean:
        return None
    return float(np.mean(clean))


def quantile(values: list[float], q: float) -> float | None:
    clean = [float(v) for v in values if math.isfinite(float(v))]
    if not clean:
        return None
    return float(np.quantile(np.array(clean, dtype=float), q))


def value_stats(values: list[float]) -> dict[str, Any]:
    clean = [float(v) for v in values if math.isfinite(float(v))]
    if not clean:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "std": None,
            "q50": None,
            "q75": None,
            "q90": None,
            "q95": None,
            "q99": None,
        }
    arr = np.array(clean, dtype=float)
    return {
        "count": int(arr.size),
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "q50": float(np.quantile(arr, 0.50)),
        "q75": float(np.quantile(arr, 0.75)),
        "q90": float(np.quantile(arr, 0.90)),
        "q95": float(np.quantile(arr, 0.95)),
        "q99": float(np.quantile(arr, 0.99)),
    }


def distribution_stats(values: list[float]) -> dict[str, Any]:
    clean = [float(v) for v in values if math.isfinite(float(v))]
    if not clean:
        return {
            "null_mean_mean": None,
            "null_mean_std": None,
            "null_mean_q01": None,
            "null_mean_q05": None,
            "null_mean_q50": None,
            "null_mean_q95": None,
            "null_mean_q99": None,
        }
    arr = np.array(clean, dtype=float)
    return {
        "null_mean_mean": float(arr.mean()),
        "null_mean_std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "null_mean_q01": float(np.quantile(arr, 0.01)),
        "null_mean_q05": float(np.quantile(arr, 0.05)),
        "null_mean_q50": float(np.quantile(arr, 0.50)),
        "null_mean_q95": float(np.quantile(arr, 0.95)),
        "null_mean_q99": float(np.quantile(arr, 0.99)),
    }


def bh_fdr(p_values: dict[str, float | None]) -> dict[str, float | None]:
    valid = sorted((key, float(value)) for key, value in p_values.items() if value is not None)
    if not valid:
        return {key: None for key in p_values}
    m = len(valid)
    adjusted: dict[str, float] = {}
    running = 1.0
    for rank, (key, p_value) in reversed(list(enumerate(valid, start=1))):
        running = min(running, p_value * m / rank)
        adjusted[key] = min(1.0, running)
    return {key: adjusted.get(key) for key in p_values}


def bonferroni(p_values: dict[str, float | None]) -> dict[str, float | None]:
    valid_count = sum(1 for value in p_values.values() if value is not None)
    if valid_count == 0:
        return {key: None for key in p_values}
    return {
        key: (min(1.0, float(value) * valid_count) if value is not None else None)
        for key, value in p_values.items()
    }


def assert_chain_inputs(
    contract: dict[str, Any],
    evaluator: dict[str, Any],
    robustness: dict[str, Any],
    validator: dict[str, Any],
    discovery: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if contract.get("result_classification") != (
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_PRE_REGISTERED_INDEPENDENT_VALIDATION_CONTRACT_READY"
    ):
        blockers.append("CONTRACT_NOT_READY")
    if contract.get("allowed_next_step") != MODULE:
        blockers.append("CONTRACT_ALLOWED_NEXT_STEP_MISMATCH")
    if evaluator.get("result_classification") != (
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_PROMISING_DIAGNOSTIC_ONLY"
    ):
        blockers.append("ROBUSTNESS_EVALUATOR_NOT_PROMISING")
    if evaluator.get("diagnostic_route_promising") is not True:
        blockers.append("DIAGNOSTIC_ROUTE_NOT_MARKED_PROMISING")
    if evaluator.get("independent_validation_required") is not True:
        blockers.append("INDEPENDENT_VALIDATION_NOT_REQUIRED_BY_EVALUATOR")
    if robustness.get("result_classification") != (
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY"
    ):
        blockers.append("ROBUSTNESS_RUNNER_NOT_PROMISING")
    if validator.get("result_classification") not in {
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS",
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
    }:
        blockers.append("EVENT_VALIDATOR_NOT_PASSING")
    if validator.get("forward_return_diagnostic_allowed") is not True:
        blockers.append("FORWARD_RETURN_DIAGNOSTIC_NOT_ALLOWED_BY_VALIDATOR")
    if discovery.get("result_classification") != "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY":
        blockers.append("EVENT_DISCOVERY_NOT_READY")
    for name, artifact in {
        "contract": contract,
        "evaluator": evaluator,
        "robustness": robustness,
        "validator": validator,
    }.items():
        for flag in ("strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"):
            if artifact.get(flag) is not False:
                blockers.append(f"{name.upper()}_{flag.upper()}_NOT_FALSE")
    return blockers


def selected_primary_meta(discovery: dict[str, Any]) -> dict[str, Any]:
    definitions = discovery.get("selected_clean_event_definitions", {})
    if isinstance(definitions, dict):
        meta = definitions.get(PRIMARY_SELECTION_SLOT)
        if isinstance(meta, dict):
            return meta
    for item in definitions if isinstance(definitions, list) else []:
        if item.get("selection_slot") == PRIMARY_SELECTION_SLOT:
            meta = item.get("meta")
            if isinstance(meta, dict):
                return meta
            return item
    raise RuntimeError("PRIMARY_EVENT_DEFINITION_NOT_FOUND")


def configure_archive_helper():
    helper = load_module(ARCHIVE_HELPER_TOOL, "binance_data_vision_archive_helper")
    helper.CACHE_ROOT = CACHE_ROOT
    helper.VALIDATION_START = VALIDATION_START
    if hasattr(helper, "REQUEST_SLEEP_SECONDS"):
        helper.REQUEST_SLEEP_SECONDS = 0.02
    return helper


def normalize_metric_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        clean = dict(row)
        aliases = {
            "global_long_short_ratio": ("global_long_short_ratio", "global_ratio"),
            "top_account_long_short_ratio": ("top_account_long_short_ratio", "top_account_ratio"),
            "top_position_long_short_ratio": ("top_position_long_short_ratio", "top_position_ratio"),
            "open_interest": ("open_interest", "sum_open_interest"),
            "taker_buy_pressure": ("taker_buy_pressure", "taker_buy_aggression"),
            "taker_sell_pressure": ("taker_sell_pressure", "taker_sell_aggression"),
        }
        for target, source_keys in aliases.items():
            for source_key in source_keys:
                if source_key in row and row.get(source_key) is not None:
                    clean[target] = row.get(source_key)
                    break
        normalized.append(clean)
    return normalized


def read_2026_kline_archives(paths: list[Path], symbol: str, archive_helper) -> dict[str, Any]:
    rows_by_open: dict[int, tuple[float, float, float, float, float]] = {}
    for archive_path in paths:
        with zipfile.ZipFile(archive_path) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not names:
                raise RuntimeError(f"no CSV member in kline archive: {archive_path}")
            for name in names:
                content = archive.read(name).decode("utf-8", errors="replace")
                parsed_rows = [row for row in csv.reader(io.StringIO(content)) if row]
                if not parsed_rows:
                    continue
                if archive_helper.detect_header(parsed_rows[0]):
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
                    record = {
                        header[index]: raw_row[index].strip() if index < len(raw_row) else ""
                        for index in range(len(header))
                    }
                    open_ms = archive_helper.parse_ts_ms(record.get("open_time") or record.get("timestamp") or "")
                    if open_ms is None:
                        continue
                    timestamp = datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc)
                    if timestamp.date() < VALIDATION_START:
                        continue
                    open_price = archive_helper.to_float(record.get("open"))
                    high = archive_helper.to_float(record.get("high"))
                    low = archive_helper.to_float(record.get("low"))
                    close = archive_helper.to_float(record.get("close"))
                    volume = archive_helper.to_float(record.get("volume")) or 0.0
                    if None in (open_price, high, low, close):
                        continue
                    rows_by_open[int(open_ms)] = (
                        float(open_price),
                        float(high),
                        float(low),
                        float(close),
                        float(volume),
                    )
    rows = []
    for open_time in sorted(rows_by_open):
        open_price, high, low, close, volume = rows_by_open[open_time]
        timestamp = datetime.fromtimestamp(open_time / 1000, tz=timezone.utc)
        rows.append(
            {
                "symbol": symbol,
                "open_time": open_time,
                "open_time_iso": timestamp.isoformat().replace("+00:00", "Z"),
                "month": timestamp.strftime("%Y-%m"),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
    closes = np.array([safe_float(row.get("close")) for row in rows], dtype=float)
    highs = np.array([safe_float(row.get("high")) for row in rows], dtype=float)
    lows = np.array([safe_float(row.get("low")) for row in rows], dtype=float)
    opens = np.array([int(row["open_time"]) for row in rows], dtype=np.int64)
    return {
        "rows": rows,
        "open_to_index": {int(open_time): index for index, open_time in enumerate(opens.tolist())},
        "opens": opens,
        "closes": closes,
        "highs": highs,
        "lows": lows,
        "months": [row["month"] for row in rows],
    }


def open_ms_to_month(open_ms: int) -> str:
    return datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc).strftime("%Y-%m")


def reconstruct_primary_events(
    symbols: list[str],
    archive_paths: dict[str, dict[str, Any]],
    archive_helper,
    lsr_module,
    meta: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    per_symbol_raw: dict[str, int] = {}
    per_symbol_kept: dict[str, int] = {}
    base = lsr_module.load_base_module()
    definition_id = lsr_module.definition_id(meta)
    min_prior_spread_by_strength = {"weak": 25.0, "medium": 40.0, "strong": 60.0}
    resolution_cap_by_strength = {"weak": 25.0, "medium": 15.0, "strong": 10.0}
    path_window = meta.get("path_window", "1h")
    path_bars = int(lsr_module.NORMALIZATION_WINDOWS[path_window])
    cooldown_ms = int(meta.get("cooldown_hours", 24)) * int(lsr_module.ONE_HOUR_MS)
    strength = meta.get("normalization_strength", "medium")
    min_prior_spread = min_prior_spread_by_strength[strength]
    resolution_cap = resolution_cap_by_strength[strength]

    for symbol in symbols:
        paths = archive_paths.get(symbol, {})
        if not paths.get("metrics"):
            warnings.append(f"{symbol}:NO_2026_METRICS_ARCHIVE")
            per_symbol_raw[symbol] = 0
            per_symbol_kept[symbol] = 0
            continue
        rows = normalize_metric_rows(archive_helper.read_metrics_archives(paths["metrics"], symbol))
        rows = [
            row
            for row in rows
            if row.get("ts_ms") is not None
            and datetime.fromtimestamp(int(row["ts_ms"]) / 1000, tz=timezone.utc).date() >= VALIDATION_START
        ]
        rows.sort(key=lambda row: int(row["ts_ms"]))
        if len(rows) <= path_bars:
            warnings.append(f"{symbol}:INSUFFICIENT_METRIC_ROWS")
            per_symbol_raw[symbol] = 0
            per_symbol_kept[symbol] = 0
            continue
        state = lsr_module.build_threshold_state(rows)
        account_ranks, _, _ = lsr_module.source_rank_array(rows, "top_account", state)
        position_ranks, _, _ = lsr_module.source_rank_array(rows, "top_position", state)
        spread = np.abs(account_ranks - position_ranks)
        current_spread = spread[path_bars:]
        prior_spread = spread[:-path_bars]
        valid = np.isfinite(current_spread) & np.isfinite(prior_spread)
        current_indices = np.arange(path_bars, len(rows))
        mask = (
            valid
            & (prior_spread >= min_prior_spread)
            & (current_spread <= resolution_cap)
            & (current_spread < prior_spread)
        )
        candidate_indices = current_indices[mask]
        raw_count = int(len(candidate_indices))
        kept = 0
        last_event_ts = -10**30
        for index in candidate_indices.tolist():
            row = rows[int(index)]
            ts_ms = int(row["ts_ms"])
            if ts_ms - last_event_ts < cooldown_ms:
                continue
            base_open_ms = int(base.floor_to_15m_open(ts_ms))
            events.append(
                {
                    "symbol": symbol,
                    "timestamp": base.ms_to_iso(ts_ms),
                    "ts_ms": ts_ms,
                    "base_open_ms": base_open_ms,
                    "base_open_iso": base.ms_to_iso(base_open_ms),
                    "month": datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m"),
                    "selection_slot": PRIMARY_SELECTION_SLOT,
                    "definition_id": definition_id,
                    "family": meta.get("family"),
                    "ratio_source": meta.get("ratio_source"),
                    "normalization_strength": strength,
                    "path_window": path_window,
                    "cooldown_hours": meta.get("cooldown_hours"),
                    "prior_spread_percentile_points": float(prior_spread[int(index) - path_bars]),
                    "current_spread_percentile_points": float(current_spread[int(index) - path_bars]),
                }
            )
            last_event_ts = ts_ms
            kept += 1
        per_symbol_raw[symbol] = raw_count
        per_symbol_kept[symbol] = kept
    events.sort(key=lambda event: (event["base_open_ms"], event["symbol"]))
    reconstruction = {
        "status": "RECONSTRUCTED",
        "selection_slot": PRIMARY_SELECTION_SLOT,
        "definition_id": definition_id,
        "raw_candidate_count": int(sum(per_symbol_raw.values())),
        "cooldown_filtered_event_count": int(len(events)),
        "raw_count_by_symbol": per_symbol_raw,
        "cooldown_count_by_symbol": per_symbol_kept,
        "rules": {
            "ratio_source": meta.get("ratio_source"),
            "normalization_strength": strength,
            "path_window": path_window,
            "cooldown_hours": meta.get("cooldown_hours"),
            "min_prior_spread_percentile_points": min_prior_spread,
            "resolution_cap_percentile_points": resolution_cap,
            "current_prior_only": True,
        },
    }
    return events, reconstruction, warnings


def metric_arrays(kline_data: dict[str, Any], horizon_bars: int) -> dict[str, np.ndarray]:
    closes = kline_data["closes"]
    highs = kline_data["highs"]
    lows = kline_data["lows"]
    n = len(closes)
    signed = np.full(n, np.nan, dtype=float)
    abs_ret = np.full(n, np.nan, dtype=float)
    range_proxy = np.full(n, np.nan, dtype=float)
    realized_vol = np.full(n, np.nan, dtype=float)
    for index in range(n):
        target = index + horizon_bars
        if target >= n:
            continue
        base_close = closes[index]
        target_close = closes[target]
        if not (math.isfinite(base_close) and math.isfinite(target_close) and base_close > 0):
            continue
        forward_return = target_close / base_close - 1.0
        signed[index] = forward_return
        abs_ret[index] = abs(forward_return)
        future_high = np.nanmax(highs[index + 1 : target + 1])
        future_low = np.nanmin(lows[index + 1 : target + 1])
        if math.isfinite(future_high) and math.isfinite(future_low):
            range_proxy[index] = (future_high - future_low) / base_close
        returns: list[float] = []
        for step in range(index + 1, target + 1):
            prev_close = closes[step - 1]
            this_close = closes[step]
            if math.isfinite(prev_close) and math.isfinite(this_close) and prev_close > 0:
                returns.append(this_close / prev_close - 1.0)
        if returns:
            if len(returns) == 1:
                realized_vol[index] = abs(float(returns[0]))
            else:
                realized_vol[index] = float(np.std(np.array(returns, dtype=float), ddof=1))
    return {
        "signed_return": signed,
        "abs_return": abs_ret,
        "range_proxy": range_proxy,
        "realized_vol_proxy": realized_vol,
    }


def observed_for_horizon(
    events: list[dict[str, Any]],
    kline_by_symbol: dict[str, dict[str, Any]],
    horizon_label: str,
    horizon_bars: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    values_abs: list[float] = []
    values_range: list[float] = []
    values_rv: list[float] = []
    valid_events: list[dict[str, Any]] = []
    missing_count = 0
    array_cache: dict[str, dict[str, np.ndarray]] = {}
    for event in events:
        symbol = event["symbol"]
        kline = kline_by_symbol.get(symbol)
        if not kline:
            missing_count += 1
            continue
        index = kline["open_to_index"].get(int(event["base_open_ms"]))
        if index is None:
            missing_count += 1
            continue
        arrays = array_cache.setdefault(symbol, metric_arrays(kline, horizon_bars))
        abs_value = arrays["abs_return"][index]
        if not math.isfinite(float(abs_value)):
            missing_count += 1
            continue
        range_value = arrays["range_proxy"][index]
        rv_value = arrays["realized_vol_proxy"][index]
        values_abs.append(float(abs_value))
        if math.isfinite(float(range_value)):
            values_range.append(float(range_value))
        if math.isfinite(float(rv_value)):
            values_rv.append(float(rv_value))
        valid_events.append(
            {
                "symbol": symbol,
                "month": event["month"],
                "base_open_ms": int(event["base_open_ms"]),
                "index": int(index),
                "abs_return": float(abs_value),
                "range_proxy": float(range_value) if math.isfinite(float(range_value)) else None,
                "realized_vol_proxy": float(rv_value) if math.isfinite(float(rv_value)) else None,
            }
        )
    abs_stats = value_stats(values_abs)
    range_stats = value_stats(values_range)
    rv_stats = value_stats(values_rv)
    observed = {
        "event_count": int(len(events)),
        "valid_count": int(len(values_abs)),
        "missing_count": int(missing_count),
        "mean_abs_return": abs_stats["mean"],
        "median_abs_return": abs_stats["median"],
        "std_abs_return": abs_stats["std"],
        "q50_abs_return": abs_stats["q50"],
        "q75_abs_return": abs_stats["q75"],
        "q90_abs_return": abs_stats["q90"],
        "q95_abs_return": abs_stats["q95"],
        "q99_abs_return": abs_stats["q99"],
        "forward_range_proxy": {
            "count": range_stats["count"],
            "mean": range_stats["mean"],
            "median": range_stats["median"],
            "q75": range_stats["q75"],
            "q90": range_stats["q90"],
            "q95": range_stats["q95"],
            "q99": range_stats["q99"],
        },
        "realized_vol_proxy": {
            "count": rv_stats["count"],
            "mean": rv_stats["mean"],
            "median": rv_stats["median"],
            "q75": rv_stats["q75"],
            "q90": rv_stats["q90"],
            "q95": rv_stats["q95"],
            "q99": rv_stats["q99"],
        },
    }
    return observed, valid_events


def build_null_pools(
    valid_events: list[dict[str, Any]],
    kline_by_symbol: dict[str, dict[str, Any]],
    horizon_bars: int,
) -> dict[tuple[str, str], dict[str, list[float]]]:
    event_indices = defaultdict(set)
    event_counts = Counter()
    for event in valid_events:
        key = (event["symbol"], event["month"])
        event_indices[key].add(int(event["index"]))
        event_counts[key] += 1
    pools: dict[tuple[str, str], dict[str, list[float]]] = {}
    array_cache: dict[str, dict[str, np.ndarray]] = {}
    for key in event_counts:
        symbol, month = key
        kline = kline_by_symbol.get(symbol)
        if not kline:
            pools[key] = {"abs_return": [], "range_proxy": [], "realized_vol_proxy": []}
            continue
        arrays = array_cache.setdefault(symbol, metric_arrays(kline, horizon_bars))
        month_indices = [
            index
            for index, row_month in enumerate(kline["months"])
            if row_month == month and math.isfinite(float(arrays["abs_return"][index]))
        ]
        excluded = event_indices[key]
        filtered = [index for index in month_indices if index not in excluded]
        candidate_indices = filtered if filtered else month_indices
        if not candidate_indices:
            symbol_indices = [
                index
                for index in range(len(kline["closes"]))
                if math.isfinite(float(arrays["abs_return"][index])) and index not in excluded
            ]
            candidate_indices = symbol_indices
        pools[key] = {
            "abs_return": [float(arrays["abs_return"][index]) for index in candidate_indices],
            "range_proxy": [
                float(arrays["range_proxy"][index])
                for index in candidate_indices
                if math.isfinite(float(arrays["range_proxy"][index]))
            ],
            "realized_vol_proxy": [
                float(arrays["realized_vol_proxy"][index])
                for index in candidate_indices
                if math.isfinite(float(arrays["realized_vol_proxy"][index]))
            ],
        }
    return pools


def run_month_aware_null(
    valid_events: list[dict[str, Any]],
    kline_by_symbol: dict[str, dict[str, Any]],
    horizon_bars: int,
    seed: int,
) -> dict[str, Any]:
    if not valid_events:
        return {
            "permutation_count_requested": PERMUTATION_COUNT,
            "permutation_count_completed": 0,
            "null_stats": distribution_stats([]),
            "p_abs_high_mean": None,
            "null_range_proxy_stats": distribution_stats([]),
            "range_proxy_p_high": None,
            "null_realized_vol_proxy_stats": distribution_stats([]),
            "realized_vol_proxy_p_high": None,
            "pool_status": "NO_VALID_EVENTS",
        }
    pools = build_null_pools(valid_events, kline_by_symbol, horizon_bars)
    group_counts = Counter((event["symbol"], event["month"]) for event in valid_events)
    observed_abs_mean = finite_mean([event["abs_return"] for event in valid_events])
    observed_range_mean = finite_mean(
        [event["range_proxy"] for event in valid_events if event.get("range_proxy") is not None]
    )
    observed_rv_mean = finite_mean(
        [event["realized_vol_proxy"] for event in valid_events if event.get("realized_vol_proxy") is not None]
    )
    rng = random.Random(seed)
    null_abs_means: list[float] = []
    null_range_means: list[float] = []
    null_rv_means: list[float] = []
    for _ in range(PERMUTATION_COUNT):
        sampled_abs: list[float] = []
        sampled_range: list[float] = []
        sampled_rv: list[float] = []
        for key, count in group_counts.items():
            pool = pools.get(key, {})
            abs_pool = pool.get("abs_return", [])
            range_pool = pool.get("range_proxy", [])
            rv_pool = pool.get("realized_vol_proxy", [])
            if not abs_pool:
                continue
            sampled_abs.extend(rng.choice(abs_pool) for _ in range(count))
            if range_pool:
                sampled_range.extend(rng.choice(range_pool) for _ in range(count))
            if rv_pool:
                sampled_rv.extend(rng.choice(rv_pool) for _ in range(count))
        if sampled_abs:
            null_abs_means.append(float(np.mean(np.array(sampled_abs, dtype=float))))
        if sampled_range:
            null_range_means.append(float(np.mean(np.array(sampled_range, dtype=float))))
        if sampled_rv:
            null_rv_means.append(float(np.mean(np.array(sampled_rv, dtype=float))))
    if len(null_abs_means) != PERMUTATION_COUNT:
        raise RuntimeError("VALIDATION_NULL_RUNTIME_OR_MEMORY_LIMIT")
    p_abs = None
    if observed_abs_mean is not None:
        p_abs = (1 + sum(1 for value in null_abs_means if value >= observed_abs_mean)) / (
            1 + PERMUTATION_COUNT
        )
    p_range = None
    if observed_range_mean is not None and null_range_means:
        p_range = (1 + sum(1 for value in null_range_means if value >= observed_range_mean)) / (
            1 + len(null_range_means)
        )
    p_rv = None
    if observed_rv_mean is not None and null_rv_means:
        p_rv = (1 + sum(1 for value in null_rv_means if value >= observed_rv_mean)) / (
            1 + len(null_rv_means)
        )
    return {
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": len(null_abs_means),
        "null_stats": distribution_stats(null_abs_means),
        "p_abs_high_mean": p_abs,
        "null_range_proxy_stats": distribution_stats(null_range_means),
        "range_proxy_p_high": p_range,
        "null_realized_vol_proxy_stats": distribution_stats(null_rv_means),
        "realized_vol_proxy_p_high": p_rv,
        "pool_status": "MONTH_AWARE_SYMBOL_BALANCED",
    }


def coverage_summary(events: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    symbol_counts = Counter(event["symbol"] for event in events)
    month_counts = Counter(event["month"] for event in events)
    total = len(events)
    symbol_summary = {
        "unique_symbol_count": len(symbol_counts),
        "event_count_by_symbol": dict(sorted(symbol_counts.items())),
        "top_symbol": symbol_counts.most_common(1)[0][0] if symbol_counts else None,
        "top_symbol_count": symbol_counts.most_common(1)[0][1] if symbol_counts else 0,
        "top_symbol_concentration": (
            symbol_counts.most_common(1)[0][1] / total if symbol_counts and total else None
        ),
    }
    month_summary = {
        "unique_month_count": len(month_counts),
        "event_count_by_month": dict(sorted(month_counts.items())),
        "top_month": month_counts.most_common(1)[0][0] if month_counts else None,
        "top_month_count": month_counts.most_common(1)[0][1] if month_counts else 0,
        "top_month_concentration": (
            month_counts.most_common(1)[0][1] / total if month_counts and total else None
        ),
    }
    return symbol_summary, month_summary


def validation_window_from_data(
    archive_paths: dict[str, dict[str, Any]], kline_by_symbol: dict[str, dict[str, Any]], events: list[dict[str, Any]]
) -> dict[str, Any]:
    opens: list[int] = []
    for kline in kline_by_symbol.values():
        opens.extend(int(value) for value in kline.get("opens", np.array([], dtype=np.int64)).tolist())
    event_times = [int(event["base_open_ms"]) for event in events]
    all_times = opens or event_times
    if not all_times:
        return {
            "start": None,
            "end": None,
            "event_start": None,
            "event_end": None,
            "validation_starts_no_earlier_than_2026_01_01": True,
        }
    start = min(all_times)
    end = max(all_times)
    event_start = min(event_times) if event_times else None
    event_end = max(event_times) if event_times else None
    return {
        "start": datetime.fromtimestamp(start / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "end": datetime.fromtimestamp(end / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "event_start": (
            datetime.fromtimestamp(event_start / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
            if event_start
            else None
        ),
        "event_end": (
            datetime.fromtimestamp(event_end / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
            if event_end
            else None
        ),
        "validation_starts_no_earlier_than_2026_01_01": True,
    }


def archive_summary(archive_paths: dict[str, dict[str, Any]], archive_helper) -> dict[str, Any]:
    symbol_summary: dict[str, Any] = {}
    missing_archives: list[str] = []
    for symbol in SYMBOLS_REQUESTED:
        paths = archive_paths.get(symbol, {})
        metric_count = len(paths.get("metrics", []))
        kline_count = len(paths.get("klines", []))
        symbol_summary[symbol] = {
            "metrics_archive_count": metric_count,
            "kline_15m_archive_count": kline_count,
            "has_metrics": metric_count > 0,
            "has_klines_15m": kline_count > 0,
        }
        if metric_count == 0:
            missing_archives.append(f"{symbol}:metrics")
        if kline_count == 0:
            missing_archives.append(f"{symbol}:klines_15m")
    return {
        "source": "https://data.binance.vision public futures archives",
        "cache_root": str(CACHE_ROOT),
        "validation_year_start": "2026-01-01",
        "symbol_archive_summary": symbol_summary,
        "missing_archive_items": missing_archives,
        "symbols_with_metrics_and_klines": [
            symbol
            for symbol, summary in symbol_summary.items()
            if summary["has_metrics"] and summary["has_klines_15m"]
        ],
        "raw_cache_committed": False,
    }


def sensitivity_for_horizon(
    horizon_label: str,
    full_observed: dict[str, Any],
    valid_events: list[dict[str, Any]],
    kline_by_symbol: dict[str, dict[str, Any]],
    horizon_bars: int,
    seed: int,
) -> dict[str, Any]:
    full_mean = full_observed.get("mean_abs_return")
    symbol_counts = Counter(event["symbol"] for event in valid_events)
    month_counts = Counter(event["month"] for event in valid_events)

    def leave_one(field: str, values: list[str]) -> dict[str, Any]:
        rows: dict[str, Any] = {}
        necessary: list[str] = []
        for value in values:
            subset = [event for event in valid_events if event[field] != value]
            mean_abs = finite_mean([event["abs_return"] for event in subset])
            ratio = mean_abs / full_mean if full_mean not in (None, 0) and mean_abs is not None else None
            destroyed = bool(ratio is not None and ratio < 0.30)
            if destroyed:
                necessary.append(value)
            rows[value] = {
                "excluded": value,
                "remaining_event_count": len(subset),
                "mean_abs_return": mean_abs,
                "magnitude_ratio_vs_full": ratio,
                "necessary_by_70pct_reduction_rule": destroyed,
            }
        worst_ratio = min(
            [row["magnitude_ratio_vs_full"] for row in rows.values() if row["magnitude_ratio_vs_full"] is not None],
            default=None,
        )
        return {
            "items": rows,
            "necessary_items": necessary,
            "passed": len(necessary) == 0,
            "worst_magnitude_ratio": worst_ratio,
        }

    leave_symbol = leave_one("symbol", sorted(symbol_counts)) if len(symbol_counts) > 1 else {
        "items": {},
        "necessary_items": [],
        "passed": None,
        "reason": "INSUFFICIENT_SYMBOL_COUNT",
    }
    leave_month = leave_one("month", sorted(month_counts)) if len(month_counts) > 1 else {
        "items": {},
        "necessary_items": [],
        "passed": None,
        "reason": "INSUFFICIENT_MONTH_COUNT",
    }

    arbusdt_events = [event for event in valid_events if event["symbol"] == "ARBUSDT"]
    arbusdt_excluded = [event for event in valid_events if event["symbol"] != "ARBUSDT"]
    arbusdt_mean = finite_mean([event["abs_return"] for event in arbusdt_excluded])
    arbusdt_ratio = arbusdt_mean / full_mean if full_mean not in (None, 0) and arbusdt_mean is not None else None
    arbusdt_null = None
    if arbusdt_events and arbusdt_excluded:
        arbusdt_null = run_month_aware_null(arbusdt_excluded, kline_by_symbol, horizon_bars, seed + 177)
    symbol_contribution: dict[str, Any] = {}
    for symbol, count in symbol_counts.items():
        symbol_values = [event["abs_return"] for event in valid_events if event["symbol"] == symbol]
        symbol_contribution[symbol] = {
            "event_count": count,
            "mean_abs_return": finite_mean(symbol_values),
            "sum_abs_return": float(sum(symbol_values)),
        }
    month_contribution: dict[str, Any] = {}
    for month, count in month_counts.items():
        month_values = [event["abs_return"] for event in valid_events if event["month"] == month]
        month_contribution[month] = {
            "event_count": count,
            "mean_abs_return": finite_mean(month_values),
            "sum_abs_return": float(sum(month_values)),
        }
    top_symbols = sorted(
        symbol_contribution.items(),
        key=lambda item: item[1]["sum_abs_return"],
        reverse=True,
    )[:3]
    top_months = sorted(
        month_contribution.items(),
        key=lambda item: item[1]["sum_abs_return"],
        reverse=True,
    )[:3]
    return {
        "horizon": horizon_label,
        "leave_one_symbol_out": leave_symbol,
        "leave_one_month_out": leave_month,
        "arbusdt_exclusion": {
            "arbusdt_event_count": len(arbusdt_events),
            "remaining_event_count": len(arbusdt_excluded),
            "mean_abs_return_ex_arbusdt": arbusdt_mean,
            "magnitude_ratio_vs_full": arbusdt_ratio,
            "passed": (arbusdt_ratio is None or arbusdt_ratio >= 0.30),
            "month_aware_null_if_feasible": (
                {
                    "permutation_count_completed": arbusdt_null["permutation_count_completed"],
                    "p_abs_high_mean": arbusdt_null["p_abs_high_mean"],
                }
                if arbusdt_null
                else None
            ),
        },
        "top_contributor_symbols": dict(top_symbols),
        "top_contributor_months": dict(top_months),
    }


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    print("current HEAD:", audit["current_head"])
    print("expected HEAD:", audit["expected_head"])
    print("branch:", audit["branch"])
    print("git status porcelain:", audit["git_status_porcelain"])
    print("staged files:", audit["staged_files"])
    print("modified tracked files:", audit["modified_tracked_files"])
    print("untracked files:", audit["untracked_files"])
    print("deleted files:", audit["deleted_files"])
    print("recovery decision:", audit["recovery_decision"])
    if audit["recovery_decision"] != "RECOVERY_AUDIT_CLEAN_CONTINUE":
        raise RuntimeError(f"RECOVERY_AUDIT_STOP:{audit['recovery_decision']}")

    before_hashes = input_hashes()
    contract = load_json(CONTRACT_RELATIVE_PATH)
    evaluator = load_json(EVALUATOR_RELATIVE_PATH)
    robustness = load_json(ROBUSTNESS_RELATIVE_PATH)
    validator = load_json(VALIDATOR_RELATIVE_PATH)
    discovery = load_json(DISCOVERY_RELATIVE_PATH)
    dataset = load_json(DATASET_RELATIVE_PATH)
    chain_blockers = assert_chain_inputs(contract, evaluator, robustness, validator, discovery)
    if chain_blockers:
        raise RuntimeError("INPUT_CHAIN_BLOCKER:" + ",".join(chain_blockers))

    primary_meta = selected_primary_meta(discovery)
    archive_helper = configure_archive_helper()
    lsr_module = load_module(DISCOVERY_TOOL, "long_short_ratio_extreme_normalization_discovery")

    archive_paths, manifest = archive_helper.download_all_archives(SYMBOLS_REQUESTED)
    public_summary = archive_summary(archive_paths, archive_helper)
    symbols_available = public_summary["symbols_with_metrics_and_klines"]
    kline_by_symbol = {
        symbol: read_2026_kline_archives(
            archive_paths.get(symbol, {}).get("klines", []), symbol, archive_helper
        )
        for symbol in symbols_available
    }
    kline_by_symbol = {symbol: data for symbol, data in kline_by_symbol.items() if data.get("rows")}
    symbols_available = [symbol for symbol in symbols_available if symbol in kline_by_symbol]

    events, reconstruction, reconstruction_warnings = reconstruct_primary_events(
        symbols_available, archive_paths, archive_helper, lsr_module, primary_meta
    )
    symbol_coverage, month_coverage = coverage_summary(events)
    validation_window = validation_window_from_data(archive_paths, kline_by_symbol, events)

    observed_by_horizon: dict[str, Any] = {}
    valid_events_by_horizon: dict[str, list[dict[str, Any]]] = {}
    null_stats_by_horizon: dict[str, Any] = {}
    p_values: dict[str, float | None] = {}
    sensitivity_by_horizon: dict[str, Any] = {}
    for index, (horizon_label, horizon_bars) in enumerate(PRIMARY_HORIZONS.items()):
        observed, valid_events = observed_for_horizon(events, kline_by_symbol, horizon_label, horizon_bars)
        observed_by_horizon[horizon_label] = observed
        valid_events_by_horizon[horizon_label] = valid_events
        null_result = run_month_aware_null(
            valid_events,
            kline_by_symbol,
            horizon_bars,
            RANDOM_SEED + index * 1009,
        )
        null_stats_by_horizon[horizon_label] = {
            **null_result["null_stats"],
            "permutation_count_requested": null_result["permutation_count_requested"],
            "permutation_count_completed": null_result["permutation_count_completed"],
            "p_abs_high_mean": null_result["p_abs_high_mean"],
            "null_range_proxy_stats": null_result["null_range_proxy_stats"],
            "range_proxy_p_high": null_result["range_proxy_p_high"],
            "null_realized_vol_proxy_stats": null_result["null_realized_vol_proxy_stats"],
            "realized_vol_proxy_p_high": null_result["realized_vol_proxy_p_high"],
            "pool_status": null_result["pool_status"],
        }
        p_values[horizon_label] = null_result["p_abs_high_mean"]
        sensitivity_by_horizon[horizon_label] = sensitivity_for_horizon(
            horizon_label,
            observed,
            valid_events,
            kline_by_symbol,
            horizon_bars,
            RANDOM_SEED + index * 2003,
        )

    fdr_values = bh_fdr(p_values)
    bonferroni_values = bonferroni(p_values)
    permutation_completed = min(
        [
            int(null_stats_by_horizon[h]["permutation_count_completed"])
            for h in PRIMARY_HORIZONS
            if null_stats_by_horizon[h]["permutation_count_completed"] is not None
        ],
        default=0,
    )

    event_count = len(events)
    min_valid = min((observed_by_horizon[h]["valid_count"] for h in PRIMARY_HORIZONS), default=0)
    data_quality_warnings = list(reconstruction_warnings)
    if public_summary["missing_archive_items"]:
        data_quality_warnings.append("MISSING_2026_PUBLIC_ARCHIVES:" + ",".join(public_summary["missing_archive_items"]))
    missing_total = sum(int(observed_by_horizon[h]["missing_count"]) for h in PRIMARY_HORIZONS)
    if missing_total:
        data_quality_warnings.append(f"MISSING_FORWARD_VOLATILITY_ROWS_TOTAL:{missing_total}")
    if validation_window["start"] and validation_window["start"] < "2026-01-01T00:00:00Z":
        data_quality_warnings.append("VALIDATION_WINDOW_STARTS_BEFORE_2026")

    observed_higher_than_null = {
        horizon: (
            observed_by_horizon[horizon]["mean_abs_return"] is not None
            and null_stats_by_horizon[horizon]["null_mean_mean"] is not None
            and observed_by_horizon[horizon]["mean_abs_return"] > null_stats_by_horizon[horizon]["null_mean_mean"]
        )
        for horizon in PRIMARY_HORIZONS
    }
    primary_p_pass = {
        horizon: (p_values[horizon] is not None and p_values[horizon] <= 0.05)
        for horizon in PRIMARY_HORIZONS
    }
    fdr_pass = {
        horizon: (fdr_values[horizon] is not None and fdr_values[horizon] <= 0.05)
        for horizon in PRIMARY_HORIZONS
    }
    bonferroni_pass = {
        horizon: (bonferroni_values[horizon] is not None and bonferroni_values[horizon] <= 0.05)
        for horizon in PRIMARY_HORIZONS
    }
    leave_one_symbol_pass = all(
        sensitivity_by_horizon[h]["leave_one_symbol_out"].get("passed") in {True, None}
        for h in PRIMARY_HORIZONS
    )
    leave_one_month_pass = all(
        sensitivity_by_horizon[h]["leave_one_month_out"].get("passed") in {True, None}
        for h in PRIMARY_HORIZONS
    )
    arbusdt_pass = all(
        sensitivity_by_horizon[h]["arbusdt_exclusion"].get("passed") in {True, None}
        for h in PRIMARY_HORIZONS
    )
    alternate_proxy_support = {
        horizon: (
            observed_by_horizon[horizon]["forward_range_proxy"]["mean"] is not None
            or observed_by_horizon[horizon]["realized_vol_proxy"]["mean"] is not None
        )
        for horizon in PRIMARY_HORIZONS
    }

    validation_gates = {
        "independent_validation_uses_2026_plus_only": validation_window[
            "validation_starts_no_earlier_than_2026_01_01"
        ],
        "event_reconstruction_uses_current_prior_observations_only": True,
        "sufficient_event_count": event_count >= 100,
        "observed_primary_volatility_metric_higher_than_null": any(observed_higher_than_null.values()),
        "p_abs_high_mean_lte_0_05_for_at_least_one_primary_horizon": any(primary_p_pass.values()),
        "all_primary_horizons_reported": set(observed_by_horizon) == set(PRIMARY_HORIZONS),
        "fdr_and_bonferroni_recorded_across_three_tests": all(
            horizon in fdr_values and horizon in bonferroni_values for horizon in PRIMARY_HORIZONS
        ),
        "leave_one_symbol_no_single_symbol_dependence": leave_one_symbol_pass,
        "leave_one_month_no_single_month_dependence": leave_one_month_pass,
        "arbusdt_missing_archive_sensitivity_recorded": True,
        "alternate_volatility_proxy_sensitivity_recorded_when_feasible": all(
            alternate_proxy_support.values()
        ),
        "no_forbidden_action_occurred": True,
        "input_hashes_unchanged": None,
    }

    failed_gates = [name for name, passed in validation_gates.items() if passed is False]
    if event_count < 50:
        result_classification = INCONCLUSIVE_CLASSIFICATION
        final_decision = (
            "INCONCLUSIVE_INSUFFICIENT_SAMPLE: primary event count below 50 validation events."
        )
    elif event_count < 100:
        result_classification = INCONCLUSIVE_CLASSIFICATION
        final_decision = (
            "INCONCLUSIVE_INSUFFICIENT_SAMPLE: primary event count is 50-99 and contract does not "
            "allow automatic pass."
        )
    elif not symbols_available or not kline_by_symbol:
        result_classification = DATA_QUALITY_CLASSIFICATION
        final_decision = "DATA_QUALITY_ATTENTION: no usable 2026 public archive coverage."
    elif (
        validation_gates["observed_primary_volatility_metric_higher_than_null"]
        and validation_gates["p_abs_high_mean_lte_0_05_for_at_least_one_primary_horizon"]
        and leave_one_symbol_pass
        and leave_one_month_pass
        and arbusdt_pass
        and all(alternate_proxy_support.values())
        and permutation_completed == PERMUTATION_COUNT
    ):
        result_classification = PASS_CLASSIFICATION
        final_decision = (
            "PASS_DIAGNOSTIC_ONLY: at least one frozen primary volatility horizon passed the "
            "pre-registered validation gates. No strategy/signal/candidate/release is allowed."
        )
    else:
        result_classification = FAIL_CLASSIFICATION
        final_decision = (
            "FAIL: sufficient validation sample exists, but the frozen volatility diagnostic did "
            "not pass the pre-registered primary validation gates."
        )

    after_hashes = input_hashes()
    hashes_unchanged = before_hashes == after_hashes
    validation_gates["input_hashes_unchanged"] = hashes_unchanged
    if not hashes_unchanged:
        raise RuntimeError("INPUT_ARTIFACT_HASH_CHANGED")
    failed_gates = [name for name, passed in validation_gates.items() if passed is False]

    artifact = {
        "validation_status": (
            "PASS"
            if result_classification == PASS_CLASSIFICATION
            else ("INCONCLUSIVE" if result_classification == INCONCLUSIVE_CLASSIFICATION else "FAIL")
        ),
        "result_classification": result_classification,
        "recovery_audit_status": audit["recovery_audit_status"],
        "current_head": audit["current_head"],
        "expected_head": audit["expected_head"],
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_before": before_hashes,
        "input_artifact_hashes_after": after_hashes,
        "input_artifact_hashes_unchanged": hashes_unchanged,
        "theory_id": THEORY_ID,
        "frozen_hypothesis": {
            "primary_event": "account/position divergence resolution",
            "research_event_count": 947,
            "primary_horizons": list(PRIMARY_HORIZONS),
            "primary_metric": "mean_forward_abs_return_or_realized_volatility_proxy",
            "expected_direction": "higher_than_month_aware_symbol_balanced_null",
            "primary_p_value": "p_abs_high_mean",
            "signed_returns": "secondary_only_not_pass_fail",
            "event_definition_policy": {
                "threshold_changes_allowed": False,
                "ratio_source_changes_allowed": False,
                "normalization_strength_changes_allowed": False,
                "cooldown_changes_allowed": False,
                "persistence_break_tier_promotion_allowed": False,
                "validation_outcome_optimization_allowed": False,
            },
        },
        "independent_validation_window": validation_window,
        "independent_validation_data_policy_followed": {
            "uses_2026_plus_public_binance_data_vision_only": True,
            "uses_2023_2025_as_independent_validation": False,
            "private_api_used": False,
            "account_api_used": False,
            "order_endpoint_used": False,
            "api_key_used": False,
            "raw_cache_committed": False,
        },
        "public_data_source_summary": {
            "source": "Binance Data Vision public futures archives",
            "preferred_archive_type": "monthly/daily public archive files",
            "cache_root": str(CACHE_ROOT),
            "raw_cache_committed": False,
        },
        "symbols_requested": SYMBOLS_REQUESTED,
        "symbols_available": symbols_available,
        "archive_availability_summary": public_summary,
        "event_reconstruction_status": reconstruction,
        "event_count": event_count,
        "symbol_coverage": symbol_coverage,
        "month_coverage": month_coverage,
        "observed_primary_volatility_stats_by_horizon": observed_by_horizon,
        "null_model": {
            "name": "month-aware symbol-balanced null",
            "preserve_symbol_distribution": True,
            "preserve_calendar_month_distribution_where_feasible": True,
            "exclude_actual_event_timestamps_where_possible": True,
            "permutation_count_requested": PERMUTATION_COUNT,
            "random_seed": RANDOM_SEED,
        },
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": permutation_completed,
        "null_stats_by_horizon": null_stats_by_horizon,
        "p_abs_high_mean_by_horizon": p_values,
        "fdr_q_values": fdr_values,
        "bonferroni_p_values": bonferroni_values,
        "validation_gates": validation_gates,
        "failed_validation_gates": failed_gates,
        "sensitivity_diagnostics": {
            "leave_one_symbol_out": {
                horizon: sensitivity_by_horizon[horizon]["leave_one_symbol_out"]
                for horizon in PRIMARY_HORIZONS
            },
            "leave_one_month_out": {
                horizon: sensitivity_by_horizon[horizon]["leave_one_month_out"]
                for horizon in PRIMARY_HORIZONS
            },
            "arbusdt_exclusion": {
                horizon: sensitivity_by_horizon[horizon]["arbusdt_exclusion"]
                for horizon in PRIMARY_HORIZONS
            },
            "top_contributor_symbols": {
                horizon: sensitivity_by_horizon[horizon]["top_contributor_symbols"]
                for horizon in PRIMARY_HORIZONS
            },
            "top_contributor_months": {
                horizon: sensitivity_by_horizon[horizon]["top_contributor_months"]
                for horizon in PRIMARY_HORIZONS
            },
            "alternate_volatility_proxy_sensitivity": {
                horizon: {
                    "forward_range_proxy_observed_mean": observed_by_horizon[horizon][
                        "forward_range_proxy"
                    ]["mean"],
                    "forward_range_proxy_p_high": null_stats_by_horizon[horizon][
                        "range_proxy_p_high"
                    ],
                    "realized_vol_proxy_observed_mean": observed_by_horizon[horizon][
                        "realized_vol_proxy"
                    ]["mean"],
                    "realized_vol_proxy_p_high": null_stats_by_horizon[horizon][
                        "realized_vol_proxy_p_high"
                    ],
                }
                for horizon in PRIMARY_HORIZONS
            },
            "missing_archive_summary": public_summary["missing_archive_items"],
            "data_quality_summary": data_quality_warnings,
        },
        "data_quality_warnings": data_quality_warnings,
        "final_validation_decision": final_decision,
        "independent_validation_passed": result_classification == PASS_CLASSIFICATION,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": ALLOWED_NEXT_BY_CLASSIFICATION[result_classification],
        "blocker": None,
    }
    return artifact


def blocked_artifact(reason: str) -> dict[str, Any]:
    audit = recovery_audit()
    try:
        before_hashes = input_hashes()
        after_hashes = input_hashes()
        unchanged = before_hashes == after_hashes
    except Exception:
        before_hashes = {}
        after_hashes = {}
        unchanged = False
    return {
        "validation_status": "FAILED_STOP",
        "result_classification": FAILED_STOP_CLASSIFICATION,
        "recovery_audit_status": audit.get("recovery_audit_status"),
        "current_head": audit.get("current_head"),
        "expected_head": audit.get("expected_head"),
        "head_matches_expected": audit.get("head_matches_expected"),
        "input_artifact_hashes_before": before_hashes,
        "input_artifact_hashes_after": after_hashes,
        "input_artifact_hashes_unchanged": unchanged,
        "theory_id": THEORY_ID,
        "frozen_hypothesis": None,
        "independent_validation_window": None,
        "independent_validation_data_policy_followed": None,
        "public_data_source_summary": None,
        "symbols_requested": SYMBOLS_REQUESTED,
        "symbols_available": [],
        "archive_availability_summary": None,
        "event_reconstruction_status": "FAILED_STOP",
        "event_count": 0,
        "symbol_coverage": None,
        "month_coverage": None,
        "observed_primary_volatility_stats_by_horizon": None,
        "null_model": None,
        "permutation_count_requested": PERMUTATION_COUNT,
        "permutation_count_completed": 0,
        "null_stats_by_horizon": None,
        "p_abs_high_mean_by_horizon": None,
        "fdr_q_values": None,
        "bonferroni_p_values": None,
        "validation_gates": None,
        "failed_validation_gates": ["FAILED_STOP"],
        "sensitivity_diagnostics": None,
        "data_quality_warnings": [],
        "final_validation_decision": "BLOCKED / FAILED_STOP: " + reason,
        "independent_validation_passed": False,
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "live_allowed": False,
        "forbidden_actions_confirmed_false": FORBIDDEN_ACTIONS_CONFIRMED_FALSE,
        "allowed_next_step": ALLOWED_NEXT_BY_CLASSIFICATION[FAILED_STOP_CLASSIFICATION],
        "blocker": reason,
    }


def write_artifact(artifact: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
        handle.write("\n")


def report_lines(artifact: dict[str, Any]) -> list[str]:
    return [
        f"status: {artifact.get('validation_status')}",
        f"result_classification: {artifact.get('result_classification')}",
        f"recovery_audit_status: {artifact.get('recovery_audit_status')}",
        f"input_artifact_hashes_unchanged: {artifact.get('input_artifact_hashes_unchanged')}",
        f"theory_id: {artifact.get('theory_id')}",
        f"independent_validation_window: {json.dumps(artifact.get('independent_validation_window'), sort_keys=True)}",
        f"symbols_requested: {json.dumps(artifact.get('symbols_requested'), sort_keys=True)}",
        f"symbols_available: {json.dumps(artifact.get('symbols_available'), sort_keys=True)}",
        f"event_count: {artifact.get('event_count')}",
        f"symbol_coverage: {json.dumps(artifact.get('symbol_coverage'), sort_keys=True)}",
        f"month_coverage: {json.dumps(artifact.get('month_coverage'), sort_keys=True)}",
        "observed_primary_volatility_stats_by_horizon: "
        + json.dumps(artifact.get("observed_primary_volatility_stats_by_horizon"), sort_keys=True),
        f"permutation_count_requested: {artifact.get('permutation_count_requested')}",
        f"permutation_count_completed: {artifact.get('permutation_count_completed')}",
        f"p_abs_high_mean_by_horizon: {json.dumps(artifact.get('p_abs_high_mean_by_horizon'), sort_keys=True)}",
        f"fdr_q_values: {json.dumps(artifact.get('fdr_q_values'), sort_keys=True)}",
        f"bonferroni_p_values: {json.dumps(artifact.get('bonferroni_p_values'), sort_keys=True)}",
        f"validation_gates: {json.dumps(artifact.get('validation_gates'), sort_keys=True)}",
        f"failed_validation_gates: {json.dumps(artifact.get('failed_validation_gates'), sort_keys=True)}",
        f"sensitivity_diagnostics: {json.dumps(artifact.get('sensitivity_diagnostics'), sort_keys=True)}",
        f"data_quality_warnings: {json.dumps(artifact.get('data_quality_warnings'), sort_keys=True)}",
        f"final_validation_decision: {artifact.get('final_validation_decision')}",
        f"independent_validation_passed: {artifact.get('independent_validation_passed')}",
        f"strategy_allowed: {artifact.get('strategy_allowed')}",
        f"signal_allowed: {artifact.get('signal_allowed')}",
        f"candidate_generation_allowed: {artifact.get('candidate_generation_allowed')}",
        f"release_allowed: {artifact.get('release_allowed')}",
        f"allowed_next_step: {artifact.get('allowed_next_step')}",
        "commit hash: PENDING_COMMIT",
        "final git status: PENDING_COMMIT",
        "repo clean: PENDING_COMMIT",
        "tracked Python count: PENDING_COMMIT",
        "raw data committed: false",
        "cache files staged: false",
        "forbidden actions confirmed false: "
        + json.dumps(artifact.get("forbidden_actions_confirmed_false"), sort_keys=True),
        f"blocker: {artifact.get('blocker')}",
    ]


def main() -> int:
    try:
        artifact = build_artifact()
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 0
    except Exception as exc:  # noqa: BLE001 - explicit failed-stop artifact is required.
        artifact = blocked_artifact(str(exc))
        write_artifact(artifact)
        for line in report_lines(artifact):
            print(line)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
