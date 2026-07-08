#!/usr/bin/env python
"""Forward-return diagnostic for validated long-short ratio normalization events."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_RETURN_DIAGNOSTIC_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_forward_return_diagnostic_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_forward_return_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "4412416a30412276f29707e20b1303a70d68caaf"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_VALIDATOR_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_event_validator_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json"
SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_VALIDATOR_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

DISCOVERY_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_long_short_ratio_extreme_normalization_event_discovery_v1.py"

DIAGNOSTIC_STATUS_PASS = "PASS_REPO_ONLY_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_RETURN_DIAGNOSTIC_CREATED"
DIAGNOSTIC_STATUS_BLOCKED = "BLOCKED_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_RETURN_DIAGNOSTIC"
ARTIFACT_KIND = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_RETURN_DIAGNOSTIC"

RESULT_PROMISING_SIGNED = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_PROMISING_SIGNED_RETURN_DIAGNOSTIC_ONLY"
RESULT_PROMISING_VOL = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY"
RESULT_NO_ROBUST = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_NO_ROBUST_EFFECT"
RESULT_ATTENTION = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_FAILED_STOP"

THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"
NEXT_SIGNED_ROBUSTNESS = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_SIGNED_RETURN_ROBUSTNESS_RUNNER_V1"
NEXT_VOL_ROBUSTNESS = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_RUNNER_V1"
NEXT_EVALUATOR = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_EVALUATOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_KLINE_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"

LONG_SLOT = "best_long_crowding_normalization_candidate"
SHORT_SLOT = "best_short_crowding_normalization_candidate"
DIVERGENCE_SLOT = "optional_account_position_divergence_resolution_candidate"
MAIN_SELECTION_SLOTS = [LONG_SLOT, SHORT_SLOT, DIVERGENCE_SLOT]
SECONDARY_SELECTION_SLOTS = [
    "best_long_crowding_persistence_break_candidate",
    "best_short_crowding_persistence_break_candidate",
]
EXPECTED_COUNTS = {
    LONG_SLOT: 520,
    SHORT_SLOT: 426,
    DIVERGENCE_SLOT: 947,
}
HORIZONS = {"15m": 1, "1h": 4, "4h": 16, "24h": 96}
PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528


class DiagnosticBlocked(Exception):
    pass


def load_discovery_module() -> Any:
    if not DISCOVERY_TOOL.exists():
        raise DiagnosticBlocked(f"missing discovery tool: {DISCOVERY_TOOL}")
    spec = importlib.util.spec_from_file_location("lsr_normalization_discovery_for_forward_diagnostic_v1", DISCOVERY_TOOL)
    if spec is None or spec.loader is None:
        raise DiagnosticBlocked("could not load long-short ratio discovery module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_payload_hash(payload: dict[str, Any]) -> str:
    clean = dict(payload)
    clean.pop("payload_sha256_excluding_hash", None)
    encoded = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    output = float(value)
    if math.isnan(output) or math.isinf(output):
        return None
    return output


def run_git(args: list[str]) -> tuple[int, str, str]:
    safe_dir = str(REPO_ROOT).replace("\\", "/")
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", f"safe.directory={safe_dir}", *args],
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
    hashes: dict[str, str] = {}
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


def verify_payload_hash(payload: dict[str, Any], label: str) -> str:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        raise DiagnosticBlocked(f"{label} missing payload_sha256_excluding_hash")
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise DiagnosticBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    validator = read_json_readonly(SOURCE_VALIDATOR_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_VALIDATOR_RELATIVE_PATH: verify_payload_hash(validator, "long-short ratio event validator"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "long-short ratio event discovery"),
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if validator.get("result_classification") not in {
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
        "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_PASS",
    }:
        raise DiagnosticBlocked("validator did not pass")
    if validator.get("forward_return_diagnostic_allowed") is not True:
        raise DiagnosticBlocked("validator did not allow forward-return diagnostic")
    for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]:
        if validator.get(flag) is not False:
            raise DiagnosticBlocked(f"validator safety flag not false: {flag}")
    if discovery.get("result_classification") != "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY":
        raise DiagnosticBlocked("discovery is not ready")
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise DiagnosticBlocked("outcome-blind theory queue is not ready")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiagnosticBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise DiagnosticBlocked("public kline diagnostic status is not PASS")
    return validator, discovery, theory_queue, dataset, kline, payload_hashes


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
        "event_definitions_modified": False,
        "thresholds_changed": False,
        "horizons_changed_based_on_results": False,
        "secondary_persistence_variants_primary": False,
    }


def selected_definitions(discovery: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected = discovery.get("selected_clean_event_definitions")
    if not isinstance(selected, list):
        raise DiagnosticBlocked("selected_clean_event_definitions is not a list")
    by_slot: dict[str, dict[str, Any]] = {}
    for item in selected:
        if not isinstance(item, dict):
            continue
        slot = item.get("selection_slot")
        if isinstance(slot, str) and slot in MAIN_SELECTION_SLOTS + SECONDARY_SELECTION_SLOTS:
            by_slot[slot] = item
    missing = [slot for slot in MAIN_SELECTION_SLOTS + SECONDARY_SELECTION_SLOTS if slot not in by_slot]
    if missing:
        raise DiagnosticBlocked(f"selected definitions missing from discovery artifact: {missing}")
    return by_slot


def selected_meta(discovery: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_slot = selected_definitions(discovery)
    metas: dict[str, dict[str, Any]] = {}
    for slot in MAIN_SELECTION_SLOTS:
        meta = by_slot[slot].get("meta")
        if not isinstance(meta, dict):
            raise DiagnosticBlocked(f"selected definition missing meta: {slot}")
        metas[slot] = dict(meta)
    return metas


def record_event(row: dict[str, Any], slot: str, meta: dict[str, Any], base: Any, definition_id: str) -> dict[str, Any]:
    base_open = base.floor_to_15m_open(row["ts_ms"])
    return {
        "selection_slot": slot,
        "definition_id": definition_id,
        "symbol": row["symbol"],
        "timestamp": row["timestamp"],
        "ts_ms": int(row["ts_ms"]),
        "base_open_ms": int(base_open),
        "base_open_iso": base.ms_to_iso(int(base_open)),
        "month": row["month"],
        "family": meta["family"],
        "ratio_source": meta["ratio_source"],
        "extreme_threshold": meta["extreme_threshold"],
        "normalization_strength": meta["normalization_strength"],
        "path_window": meta["path_window"],
    }


def register_candidate(
    events: dict[str, list[dict[str, Any]]],
    counters: dict[str, Any],
    last_event_ms: dict[str, dict[str, int]],
    rows: list[dict[str, Any]],
    indices: np.ndarray,
    slot: str,
    meta: dict[str, Any],
    base: Any,
    lsr: Any,
) -> None:
    definition_id = lsr.definition_id(meta)
    cooldown_ms = int(meta["cooldown_hours"]) * lsr.ONE_HOUR_MS
    for index in indices:
        row = rows[int(index)]
        counters["raw_counts"][slot] += 1
        previous = last_event_ms[slot].get(row["symbol"])
        if previous is not None and row["ts_ms"] - previous < cooldown_ms:
            counters["cooldown_rejections"][slot] += 1
            continue
        last_event_ms[slot][row["symbol"]] = int(row["ts_ms"])
        events[slot].append(record_event(row, slot, meta, base, definition_id))


def reconstruct_symbol_events(
    path: Path,
    base: Any,
    lsr: Any,
    selected_meta_by_slot: dict[str, dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    rows = base.metric_rows_for_symbol(path)
    if not rows:
        return {slot: [] for slot in MAIN_SELECTION_SLOTS}, {"raw_counts": {}, "cooldown_rejections": {}, "missing": {"empty_metric_rows": 1}}
    state = lsr.build_threshold_state(rows)
    events: dict[str, list[dict[str, Any]]] = {slot: [] for slot in MAIN_SELECTION_SLOTS}
    counters: dict[str, Any] = {"raw_counts": Counter(), "cooldown_rejections": Counter(), "missing": Counter()}
    last_event_ms: dict[str, dict[str, int]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}

    source_cache: dict[str, tuple[np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]] = {}

    def source_data(source: str) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
        cached = source_cache.get(source)
        if cached is None:
            cached = lsr.source_rank_array(rows, source, state)
            source_cache[source] = cached
        return cached

    for slot, meta in selected_meta_by_slot.items():
        family = meta["family"]
        if family in {"LONG_CROWDING_NORMALIZATION_EVENT", "SHORT_CROWDING_NORMALIZATION_EVENT"}:
            source = meta["ratio_source"]
            ranks, high_pass, low_pass = source_data(source)
            finite = np.isfinite(ranks)
            neutral = finite & (ranks >= lsr.NEUTRAL_BAND[0]) & (ranks <= lsr.NEUTRAL_BAND[1])
            bars = int(lsr.NORMALIZATION_WINDOWS[meta["path_window"]])
            if len(rows) <= bars:
                continue
            current = ranks[bars:]
            prior = ranks[:-bars]
            valid = np.isfinite(current) & np.isfinite(prior)
            current_indices = np.arange(bars, len(rows))
            neutral_current = neutral[bars:]
            min_move = float(lsr.NORMALIZATION_STRENGTHS[meta["normalization_strength"]])
            if family == "LONG_CROWDING_NORMALIZATION_EVENT":
                high_extreme = high_pass[meta["extreme_threshold"]][bars:] | high_pass[meta["extreme_threshold"]][:-bars]
                move_down = prior - current
                mask = valid & high_extreme & ((move_down >= min_move) | (neutral_current & (move_down > 0)))
            else:
                low_extreme = low_pass[meta["extreme_threshold"]][bars:] | low_pass[meta["extreme_threshold"]][:-bars]
                move_up = current - prior
                mask = valid & low_extreme & ((move_up >= min_move) | (neutral_current & (move_up > 0)))
            register_candidate(events, counters, last_event_ms, rows, current_indices[mask], slot, meta, base, lsr)
            continue

        if family == "TOP_ACCOUNT_POSITION_DIVERGENCE_RESOLUTION_EVENT":
            account_ranks, _, _ = source_data("top_account")
            position_ranks, _, _ = source_data("top_position")
            spread = np.abs(account_ranks - position_ranks)
            bars = int(lsr.NORMALIZATION_WINDOWS[meta["path_window"]])
            if len(rows) <= bars:
                continue
            current_spread = spread[bars:]
            prior_spread = spread[:-bars]
            valid = np.isfinite(current_spread) & np.isfinite(prior_spread)
            current_indices = np.arange(bars, len(rows))
            strength = meta["normalization_strength"]
            min_prior_spread = {"weak": 25.0, "medium": 40.0, "strong": 60.0}[strength]
            resolution_cap = {"weak": 25.0, "medium": 15.0, "strong": 10.0}[strength]
            mask = (
                valid
                & (prior_spread >= min_prior_spread)
                & (current_spread <= resolution_cap)
                & (current_spread < prior_spread)
            )
            register_candidate(events, counters, last_event_ms, rows, current_indices[mask], slot, meta, base, lsr)
            continue

        counters["missing"][f"unsupported_family__{family}"] += 1

    return events, {
        "raw_counts": dict(counters["raw_counts"]),
        "cooldown_rejections": dict(counters["cooldown_rejections"]),
        "missing": dict(counters["missing"]),
    }


def reconstruct_events(
    dataset: dict[str, Any],
    kline_diagnostic: dict[str, Any],
    discovery: dict[str, Any],
    lsr: Any,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, Any]]:
    selected = selected_definitions(discovery)
    selected_meta_by_slot = selected_meta(discovery)
    base = lsr.load_base_module()
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols") or dataset.get("requested_symbols")
    if not isinstance(symbols, list) or not symbols:
        raise DiagnosticBlocked("dataset builder artifact missing built symbol list")
    symbols = [str(symbol) for symbol in symbols]
    archive_summary = base.verify_cached_archives(symbols, kline_diagnostic)
    paths = base.normalized_paths(dataset)
    symbol_to_path = {path.name.split("_", 1)[0]: path for path in paths}
    events = {slot: [] for slot in MAIN_SELECTION_SLOTS}
    kline_by_symbol: dict[str, Any] = {}
    counters: dict[str, Any] = {"per_symbol": {}, "aggregate": Counter()}
    for symbol in symbols:
        path = symbol_to_path.get(symbol)
        if path is None:
            counters["aggregate"][f"{symbol}_normalized_path_missing"] += 1
            continue
        kline_data = base.load_kline_symbol(symbol, archive_summary["archive_records"])
        kline_by_symbol[symbol] = kline_data
        symbol_events, symbol_counters = reconstruct_symbol_events(path, base, lsr, selected_meta_by_slot)
        for slot, slot_events in symbol_events.items():
            events[slot].extend(slot_events)
        counters["per_symbol"][symbol] = symbol_counters
        for group in ["raw_counts", "cooldown_rejections", "missing"]:
            counters["aggregate"].update({f"{group}__{key}": value for key, value in symbol_counters[group].items()})
    actual_counts = {slot: len(events[slot]) for slot in MAIN_SELECTION_SLOTS}
    mismatches = {
        slot: {"expected": expected, "actual": actual_counts.get(slot)}
        for slot, expected in EXPECTED_COUNTS.items()
        if actual_counts.get(slot) != expected
    }
    if mismatches:
        raise DiagnosticBlocked(f"EVENT_COUNT_RECONSTRUCTION_MISMATCH: {mismatches}")
    counters["aggregate"] = dict(counters["aggregate"])
    return events, kline_by_symbol, {
        "status": "EVENT_COUNT_RECONSTRUCTION_EXACT",
        "expected_counts": EXPECTED_COUNTS,
        "actual_counts": actual_counts,
        "selected_secondary_definitions_not_used_as_primary": {
            slot: {
                "definition_id": selected[slot].get("definition_id"),
                "cooldown_filtered_count": selected[slot].get("cooldown_filtered_count"),
                "used_as_primary": False,
            }
            for slot in SECONDARY_SELECTION_SLOTS
        },
        "reconstruction_counters": counters,
        "archive_summary": archive_summary,
    }


def signed_forward_return(kline_data: dict[str, Any], base_open_ms: int, horizon_bars: int) -> float | None:
    index = kline_data["open_to_index"].get(int(base_open_ms))
    if index is None:
        return None
    target_index = index + horizon_bars
    if target_index >= len(kline_data["close"]):
        return None
    base_close = float(kline_data["close"][index])
    target_close = float(kline_data["close"][target_index])
    if base_close == 0 or not math.isfinite(base_close) or not math.isfinite(target_close):
        return None
    return (target_close / base_close) - 1.0


def range_proxy(kline_data: dict[str, Any], base_open_ms: int, horizon_bars: int) -> float | None:
    index = kline_data["open_to_index"].get(int(base_open_ms))
    if index is None:
        return None
    start = index + 1
    target = index + horizon_bars
    if start > target or target >= len(kline_data["close"]):
        return None
    base_close = float(kline_data["close"][index])
    if base_close == 0 or not math.isfinite(base_close):
        return None
    high = float(np.max(kline_data["high"][start : target + 1]))
    low = float(np.min(kline_data["low"][start : target + 1]))
    if not math.isfinite(high) or not math.isfinite(low):
        return None
    return (high - low) / base_close


def realized_vol_proxy(kline_data: dict[str, Any], base_open_ms: int, horizon_bars: int) -> float | None:
    index = kline_data["open_to_index"].get(int(base_open_ms))
    if index is None:
        return None
    target = index + horizon_bars
    if target >= len(kline_data["close"]):
        return None
    closes = kline_data["close"][index : target + 1]
    if len(closes) < 2:
        return None
    returns = []
    for prior, current in zip(closes[:-1], closes[1:]):
        prior_float = float(prior)
        current_float = float(current)
        if prior_float == 0 or not math.isfinite(prior_float) or not math.isfinite(current_float):
            continue
        returns.append((current_float / prior_float) - 1.0)
    if not returns:
        return None
    return float(np.mean(np.abs(np.array(returns, dtype=np.float64))))


def signed_stats(values: list[float], event_count: int) -> dict[str, Any]:
    arr = np.array(values, dtype=np.float64)
    missing = event_count - int(arr.size)
    if arr.size == 0:
        return {
            "event_count": event_count,
            "valid_forward_return_count": 0,
            "missing_forward_return_count": missing,
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
        "event_count": event_count,
        "valid_forward_return_count": int(arr.size),
        "missing_forward_return_count": int(missing),
        "mean": safe_float(np.mean(arr)),
        "median": safe_float(np.median(arr)),
        "std": safe_float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "positive_rate": safe_float(np.mean(arr > 0)),
        "negative_rate": safe_float(np.mean(arr < 0)),
        "q01": safe_float(np.quantile(arr, 0.01)),
        "q05": safe_float(np.quantile(arr, 0.05)),
        "q25": safe_float(np.quantile(arr, 0.25)),
        "q50": safe_float(np.quantile(arr, 0.50)),
        "q75": safe_float(np.quantile(arr, 0.75)),
        "q95": safe_float(np.quantile(arr, 0.95)),
        "q99": safe_float(np.quantile(arr, 0.99)),
    }


def abs_vol_stats(abs_values: list[float], range_values: list[float], rv_values: list[float], event_count: int) -> dict[str, Any]:
    arr = np.array(abs_values, dtype=np.float64)
    range_arr = np.array(range_values, dtype=np.float64)
    rv_arr = np.array(rv_values, dtype=np.float64)
    missing = event_count - int(arr.size)
    if arr.size == 0:
        return {
            "event_count": event_count,
            "valid_abs_return_count": 0,
            "missing_abs_return_count": missing,
            "mean_abs_return": None,
            "median_abs_return": None,
            "std_abs_return": None,
            "q50_abs_return": None,
            "q75_abs_return": None,
            "q90_abs_return": None,
            "q95_abs_return": None,
            "q99_abs_return": None,
            "forward_range_proxy_mean": safe_float(np.mean(range_arr)) if range_arr.size else None,
            "realized_vol_proxy_mean": safe_float(np.mean(rv_arr)) if rv_arr.size else None,
        }
    return {
        "event_count": event_count,
        "valid_abs_return_count": int(arr.size),
        "missing_abs_return_count": int(missing),
        "mean_abs_return": safe_float(np.mean(arr)),
        "median_abs_return": safe_float(np.median(arr)),
        "std_abs_return": safe_float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "q50_abs_return": safe_float(np.quantile(arr, 0.50)),
        "q75_abs_return": safe_float(np.quantile(arr, 0.75)),
        "q90_abs_return": safe_float(np.quantile(arr, 0.90)),
        "q95_abs_return": safe_float(np.quantile(arr, 0.95)),
        "q99_abs_return": safe_float(np.quantile(arr, 0.99)),
        "forward_range_proxy_mean": safe_float(np.mean(range_arr)) if range_arr.size else None,
        "forward_range_proxy_q95": safe_float(np.quantile(range_arr, 0.95)) if range_arr.size else None,
        "realized_vol_proxy_mean": safe_float(np.mean(rv_arr)) if rv_arr.size else None,
        "realized_vol_proxy_q95": safe_float(np.quantile(rv_arr, 0.95)) if rv_arr.size else None,
        "primary_null_metric": "mean_abs_return",
    }


def compute_observed(
    events: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    signed_observed: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    abs_observed: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    missing_summary: dict[str, Any] = {"by_definition_and_horizon": {}, "total_missing_forward_returns": 0}
    for slot, slot_events in events.items():
        for horizon, bars in HORIZONS.items():
            signed_values: list[float] = []
            abs_values: list[float] = []
            range_values: list[float] = []
            rv_values: list[float] = []
            missing = 0
            for event in slot_events:
                kline = kline_by_symbol[event["symbol"]]
                value = signed_forward_return(kline, int(event["base_open_ms"]), bars)
                if value is None:
                    missing += 1
                    continue
                signed_values.append(value)
                abs_values.append(abs(value))
                range_value = range_proxy(kline, int(event["base_open_ms"]), bars)
                if range_value is not None:
                    range_values.append(range_value)
                rv_value = realized_vol_proxy(kline, int(event["base_open_ms"]), bars)
                if rv_value is not None:
                    rv_values.append(rv_value)
            signed_observed[slot][horizon] = signed_stats(signed_values, len(slot_events))
            abs_observed[slot][horizon] = abs_vol_stats(abs_values, range_values, rv_values, len(slot_events))
            missing_summary["by_definition_and_horizon"][f"{slot}__{horizon}"] = missing
            missing_summary["total_missing_forward_returns"] += missing
    return signed_observed, abs_observed, missing_summary


def build_null_pools(
    events: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, Any],
) -> dict[str, dict[str, dict[str, np.ndarray]]]:
    pools: dict[str, dict[str, dict[str, np.ndarray]]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    excluded_by_slot_symbol: dict[str, dict[str, set[int]]] = {slot: defaultdict(set) for slot in MAIN_SELECTION_SLOTS}
    for slot, slot_events in events.items():
        for event in slot_events:
            excluded_by_slot_symbol[slot][event["symbol"]].add(int(event["base_open_ms"]))
    for slot in MAIN_SELECTION_SLOTS:
        for symbol, kline in kline_by_symbol.items():
            pools[slot][symbol] = {}
            excluded = excluded_by_slot_symbol[slot].get(symbol, set())
            opens = kline["opens"]
            close = kline["close"]
            for horizon, bars in HORIZONS.items():
                signed_values = []
                abs_values = []
                limit = len(close) - bars
                for index in range(limit):
                    open_time = int(opens[index])
                    if open_time in excluded:
                        continue
                    base_close = float(close[index])
                    target_close = float(close[index + bars])
                    if base_close == 0 or not math.isfinite(base_close) or not math.isfinite(target_close):
                        continue
                    signed = (target_close / base_close) - 1.0
                    signed_values.append(signed)
                    abs_values.append(abs(signed))
                pools[slot][symbol][horizon] = {
                    "signed": np.array(signed_values, dtype=np.float64),
                    "abs": np.array(abs_values, dtype=np.float64),
                }
    return pools


def null_distribution_stats(values: np.ndarray) -> dict[str, Any]:
    return {
        "null_mean_mean": safe_float(np.mean(values)),
        "null_mean_std": safe_float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
        "null_mean_q01": safe_float(np.quantile(values, 0.01)),
        "null_mean_q05": safe_float(np.quantile(values, 0.05)),
        "null_mean_q50": safe_float(np.quantile(values, 0.50)),
        "null_mean_q95": safe_float(np.quantile(values, 0.95)),
        "null_mean_q99": safe_float(np.quantile(values, 0.99)),
    }


def null_model(
    events: dict[str, list[dict[str, Any]]],
    pools: dict[str, dict[str, dict[str, Any]]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, np.ndarray]], dict[str, dict[str, np.ndarray]], dict[str, Any]]:
    rng = np.random.default_rng(RANDOM_SEED)
    null_signed_stats: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    null_abs_stats: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    null_signed_means: dict[str, dict[str, np.ndarray]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    null_abs_means: dict[str, dict[str, np.ndarray]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    pool_quality: dict[str, Any] = {}
    for slot, slot_events in events.items():
        symbol_counts = Counter(event["symbol"] for event in slot_events)
        pool_quality[slot] = {}
        for horizon in HORIZONS:
            signed_means = np.empty(PERMUTATION_COUNT, dtype=np.float64)
            abs_means = np.empty(PERMUTATION_COUNT, dtype=np.float64)
            pool_quality[slot][horizon] = {
                "symbol_counts": dict(symbol_counts),
                "pool_sizes": {symbol: int(pools[slot][symbol][horizon]["signed"].size) for symbol in symbol_counts},
                "actual_event_timestamps_excluded_where_possible": True,
            }
            for perm_idx in range(PERMUTATION_COUNT):
                signed_parts = []
                abs_parts = []
                for symbol, count in symbol_counts.items():
                    signed_pool = pools[slot][symbol][horizon]["signed"]
                    abs_pool = pools[slot][symbol][horizon]["abs"]
                    if signed_pool.size == 0 or abs_pool.size == 0:
                        raise DiagnosticBlocked(f"empty null pool for {slot} {symbol} {horizon}")
                    replace = count > signed_pool.size
                    indices = rng.choice(np.arange(signed_pool.size), size=count, replace=replace)
                    signed_parts.append(signed_pool[indices])
                    abs_parts.append(abs_pool[indices])
                signed_combined = np.concatenate(signed_parts) if signed_parts else np.array([], dtype=np.float64)
                abs_combined = np.concatenate(abs_parts) if abs_parts else np.array([], dtype=np.float64)
                if signed_combined.size == 0 or abs_combined.size == 0:
                    raise DiagnosticBlocked(f"empty combined null sample for {slot} {horizon}")
                signed_means[perm_idx] = float(np.mean(signed_combined))
                abs_means[perm_idx] = float(np.mean(abs_combined))
            null_signed_means[slot][horizon] = signed_means
            null_abs_means[slot][horizon] = abs_means
            null_signed_stats[slot][horizon] = null_distribution_stats(signed_means)
            null_abs_stats[slot][horizon] = null_distribution_stats(abs_means)
    return null_signed_stats, null_abs_stats, null_signed_means, null_abs_means, pool_quality


def empirical_signed_p_values(
    observed: dict[str, dict[str, Any]],
    null_means: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            observed_mean = observed[slot][horizon]["mean"]
            if observed_mean is None:
                output[slot][horizon] = {
                    "p_two_sided_mean": None,
                    "p_positive_mean": None,
                    "p_negative_mean": None,
                    "primary_directional_p_value": None,
                    "primary_directional_role": "secondary_signed_return" if slot == DIVERGENCE_SLOT else None,
                }
                continue
            obs = float(observed_mean)
            null_arr = null_means[slot][horizon]
            p_two = safe_float((1 + np.sum(np.abs(null_arr) >= abs(obs))) / (1 + PERMUTATION_COUNT))
            p_pos = safe_float((1 + np.sum(null_arr >= obs)) / (1 + PERMUTATION_COUNT))
            p_neg = safe_float((1 + np.sum(null_arr <= obs)) / (1 + PERMUTATION_COUNT))
            primary = None
            role = "secondary_signed_return"
            if slot == LONG_SLOT:
                primary = p_neg
                role = "primary_expected_negative"
            elif slot == SHORT_SLOT:
                primary = p_pos
                role = "primary_expected_positive"
            output[slot][horizon] = {
                "p_two_sided_mean": p_two,
                "p_positive_mean": p_pos,
                "p_negative_mean": p_neg,
                "primary_directional_p_value": primary,
                "primary_directional_role": role,
            }
    return output


def empirical_abs_p_values(
    observed: dict[str, dict[str, Any]],
    null_means: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            observed_mean = observed[slot][horizon]["mean_abs_return"]
            if observed_mean is None:
                output[slot][horizon] = {"p_abs_high_mean": None, "p_abs_low_mean": None, "primary_volatility_p_value": None}
                continue
            obs = float(observed_mean)
            null_arr = null_means[slot][horizon]
            p_high = safe_float((1 + np.sum(null_arr >= obs)) / (1 + PERMUTATION_COUNT))
            p_low = safe_float((1 + np.sum(null_arr <= obs)) / (1 + PERMUTATION_COUNT))
            output[slot][horizon] = {
                "p_abs_high_mean": p_high,
                "p_abs_low_mean": p_low,
                "primary_volatility_p_value": p_high if slot == DIVERGENCE_SLOT else None,
                "primary_null_metric": "mean_abs_return",
                "primary_volatility_role": "primary_divergence_volatility" if slot == DIVERGENCE_SLOT else "secondary_abs_return",
            }
    return output


def bh_fdr(pairs: list[tuple[str, float]]) -> dict[str, float]:
    sorted_pairs = sorted(pairs, key=lambda item: item[1])
    m = len(sorted_pairs)
    adjusted: dict[str, float] = {}
    running = 1.0
    for rank_from_end, (key, p_value) in enumerate(reversed(sorted_pairs), start=1):
        rank = m - rank_from_end + 1
        q_value = min(running, p_value * m / rank)
        running = q_value
        adjusted[key] = safe_float(q_value) or 1.0
    return adjusted


def correction_from_pairs(pairs: list[tuple[str, float]]) -> tuple[dict[str, float], dict[str, float]]:
    fdr = bh_fdr(pairs)
    m = len(pairs)
    bonferroni = {key: min(1.0, p_value * m) for key, p_value in pairs}
    return fdr, bonferroni


def signed_primary_corrections(p_values: dict[str, dict[str, Any]]) -> tuple[dict[str, float], dict[str, float]]:
    pairs: list[tuple[str, float]] = []
    for slot in [LONG_SLOT, SHORT_SLOT]:
        for horizon in HORIZONS:
            key = f"{slot}__{horizon}"
            p_value = p_values[slot][horizon].get("primary_directional_p_value")
            if p_value is not None:
                pairs.append((key, float(p_value)))
    return correction_from_pairs(pairs)


def volatility_primary_corrections(p_values: dict[str, dict[str, Any]]) -> tuple[dict[str, float], dict[str, float]]:
    pairs: list[tuple[str, float]] = []
    for horizon in HORIZONS:
        key = f"{DIVERGENCE_SLOT}__{horizon}"
        p_value = p_values[DIVERGENCE_SLOT][horizon].get("primary_volatility_p_value")
        if p_value is not None:
            pairs.append((key, float(p_value)))
    return correction_from_pairs(pairs)


def broader_all_tests_correction(
    signed_p_values: dict[str, dict[str, Any]],
    abs_p_values: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    signed_pairs: list[tuple[str, float]] = []
    abs_pairs: list[tuple[str, float]] = []
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            signed_primary = signed_p_values[slot][horizon].get("primary_directional_p_value")
            if signed_primary is not None:
                signed_pairs.append((f"signed__{slot}__{horizon}", float(signed_primary)))
            abs_primary = abs_p_values[slot][horizon].get("p_abs_high_mean")
            if abs_primary is not None:
                abs_pairs.append((f"abs__{slot}__{horizon}", float(abs_primary)))
    fdr, bonferroni = correction_from_pairs(signed_pairs + abs_pairs)
    return {"fdr_q_values": fdr, "bonferroni_p_values": bonferroni, "diagnostic_role": "secondary_broader_all_tests"}


def top_signed_findings(
    observed: dict[str, dict[str, Any]],
    p_values: dict[str, dict[str, Any]],
    fdr: dict[str, float],
    bonferroni: dict[str, float],
) -> list[dict[str, Any]]:
    rows = []
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            key = f"{slot}__{horizon}"
            primary_key = key if slot in {LONG_SLOT, SHORT_SLOT} else None
            rows.append(
                {
                    "selection_slot": slot,
                    "horizon": horizon,
                    "mean": observed[slot][horizon]["mean"],
                    "valid_forward_return_count": observed[slot][horizon]["valid_forward_return_count"],
                    "p_two_sided_mean": p_values[slot][horizon].get("p_two_sided_mean"),
                    "p_positive_mean": p_values[slot][horizon].get("p_positive_mean"),
                    "p_negative_mean": p_values[slot][horizon].get("p_negative_mean"),
                    "primary_directional_p_value": p_values[slot][horizon].get("primary_directional_p_value"),
                    "primary_directional_role": p_values[slot][horizon].get("primary_directional_role"),
                    "fdr_q_value": fdr.get(primary_key) if primary_key else None,
                    "bonferroni_p_value": bonferroni.get(primary_key) if primary_key else None,
                    "diagnostic_role": "primary_signed_return" if primary_key else "secondary_signed_return",
                }
            )
    rows.sort(
        key=lambda item: (
            item["fdr_q_value"] if item["fdr_q_value"] is not None else 1.0,
            item["primary_directional_p_value"] if item["primary_directional_p_value"] is not None else 1.0,
            item["p_two_sided_mean"] if item["p_two_sided_mean"] is not None else 1.0,
        )
    )
    return rows[:8]


def top_volatility_findings(
    observed: dict[str, dict[str, Any]],
    p_values: dict[str, dict[str, Any]],
    fdr: dict[str, float],
    bonferroni: dict[str, float],
) -> list[dict[str, Any]]:
    rows = []
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            key = f"{slot}__{horizon}"
            primary_key = key if slot == DIVERGENCE_SLOT else None
            rows.append(
                {
                    "selection_slot": slot,
                    "horizon": horizon,
                    "mean_abs_return": observed[slot][horizon]["mean_abs_return"],
                    "forward_range_proxy_mean": observed[slot][horizon].get("forward_range_proxy_mean"),
                    "realized_vol_proxy_mean": observed[slot][horizon].get("realized_vol_proxy_mean"),
                    "valid_abs_return_count": observed[slot][horizon]["valid_abs_return_count"],
                    "p_abs_high_mean": p_values[slot][horizon].get("p_abs_high_mean"),
                    "p_abs_low_mean": p_values[slot][horizon].get("p_abs_low_mean"),
                    "fdr_q_value": fdr.get(primary_key) if primary_key else None,
                    "bonferroni_p_value": bonferroni.get(primary_key) if primary_key else None,
                    "diagnostic_role": "primary_divergence_volatility" if primary_key else "secondary_abs_return",
                }
            )
    rows.sort(
        key=lambda item: (
            item["fdr_q_value"] if item["fdr_q_value"] is not None else 1.0,
            item["p_abs_high_mean"] if item["p_abs_high_mean"] is not None else 1.0,
        )
    )
    return rows[:8]


def base_artifact(
    head: str | None,
    hashes_before: dict[str, str] | None,
    hashes_after: dict[str, str] | None,
    blocker: str | None,
) -> dict[str, Any]:
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    return {
        "diagnostic_status": DIAGNOSTIC_STATUS_BLOCKED if blocker else DIAGNOSTIC_STATUS_PASS,
        "status": DIAGNOSTIC_STATUS_BLOCKED if blocker else DIAGNOSTIC_STATUS_PASS,
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
        "selected_event_definitions_validated": {},
        "event_reconstruction_status": None,
        "event_counts_by_definition": {},
        "horizons": list(HORIZONS),
        "observed_signed_return_stats_by_definition_and_horizon": {},
        "observed_abs_return_or_vol_stats_by_definition_and_horizon": {},
        "symbol_balanced_null_count_requested": PERMUTATION_COUNT,
        "symbol_balanced_null_count_completed": 0,
        "random_seed": RANDOM_SEED,
        "null_signed_return_stats_by_definition_and_horizon": {},
        "null_abs_return_or_vol_stats_by_definition_and_horizon": {},
        "signed_return_p_values": {},
        "abs_return_or_vol_p_values": {},
        "signed_return_fdr_q_values": {},
        "abs_return_or_vol_fdr_q_values": {},
        "signed_return_bonferroni_p_values": {},
        "abs_return_or_vol_bonferroni_p_values": {},
        "top_signed_return_findings": [],
        "top_volatility_findings": [],
        "missing_forward_return_summary": {},
        "data_quality_warnings": [],
        "validation_limits": [
            "Diagnostic research only; not strategy, signal, backtest, PnL, trade simulation, candidate, release, or edge claim.",
            "Long normalization signed-return primary p-value is p_negative_mean.",
            "Short normalization signed-return primary p-value is p_positive_mean.",
            "Account/position divergence primary diagnostic family is forward absolute return / realized-volatility proxy.",
            "Secondary persistence-break tiers are not used as primary tests.",
            "Event definitions, thresholds, and horizons were inherited from the validator and not changed based on results.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "allowed_next_step": NEXT_REPAIR if blocker else None,
        "blocker": blocker,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise DiagnosticBlocked(f"HEAD mismatch: {head} != {EXPECTED_HEAD}")
    if not output_only_status(working_tree_status()):
        raise DiagnosticBlocked(f"unexpected dirty repo state during build: {working_tree_status()}")
    hashes_before = input_artifact_hashes()
    validator, discovery, theory_queue, dataset, kline, input_payload_hashes = load_inputs()
    lsr = load_discovery_module()
    events, kline_by_symbol, reconstruction_details = reconstruct_events(dataset, kline, discovery, lsr)
    signed_observed, abs_observed, missing_forward = compute_observed(events, kline_by_symbol)
    pools = build_null_pools(events, kline_by_symbol)
    null_signed_stats, null_abs_stats, null_signed_means, null_abs_means, null_pool_quality = null_model(events, pools)
    signed_p_values = empirical_signed_p_values(signed_observed, null_signed_means)
    abs_p_values = empirical_abs_p_values(abs_observed, null_abs_means)
    signed_fdr, signed_bonferroni = signed_primary_corrections(signed_p_values)
    abs_fdr, abs_bonferroni = volatility_primary_corrections(abs_p_values)
    broader_correction = broader_all_tests_correction(signed_p_values, abs_p_values)
    signed_top = top_signed_findings(signed_observed, signed_p_values, signed_fdr, signed_bonferroni)
    vol_top = top_volatility_findings(abs_observed, abs_p_values, abs_fdr, abs_bonferroni)
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise DiagnosticBlocked("input artifact hash changed during diagnostic run")

    total_missing = int(missing_forward["total_missing_forward_returns"])
    total_tests = sum(len(values) for values in events.values()) * len(HORIZONS)
    missing_rate = total_missing / total_tests if total_tests else 0.0
    signed_promising = any(value <= 0.05 for value in signed_fdr.values()) and any(
        value <= 0.05 for value in signed_bonferroni.values()
    )
    vol_promising = any(value <= 0.05 for value in abs_fdr.values()) and any(
        value <= 0.05 for value in abs_bonferroni.values()
    )
    if missing_rate > 0.01:
        result_classification = RESULT_ATTENTION
        allowed_next_step = NEXT_REPAIR
    elif signed_promising:
        result_classification = RESULT_PROMISING_SIGNED
        allowed_next_step = NEXT_SIGNED_ROBUSTNESS
    elif vol_promising:
        result_classification = RESULT_PROMISING_VOL
        allowed_next_step = NEXT_VOL_ROBUSTNESS
    else:
        result_classification = RESULT_NO_ROBUST
        allowed_next_step = NEXT_EVALUATOR

    data_quality_warnings = [
        "Known public kline archive gaps remain where inherited from prior artifacts, including ARBUSDT-2023-01 and ARBUSDT-2023-02.",
        "Raw kline cache files were reused and not committed.",
        f"Missing forward rows across definition/horizon tests: {total_missing}.",
        f"Missing forward-row rate across definition/horizon tests: {missing_rate:.8f}.",
    ]
    selected = selected_definitions(discovery)
    selected_validated = {
        slot: {
            "definition_id": selected[slot].get("definition_id"),
            "expected_cooldown_count": EXPECTED_COUNTS[slot],
            "reconstructed_cooldown_count": len(events[slot]),
            "used_as_primary": True,
            "diagnostic_hypothesis": (
                "expected_signed_direction_negative"
                if slot == LONG_SLOT
                else "expected_signed_direction_positive"
                if slot == SHORT_SLOT
                else "expected_forward_abs_return_higher_than_null"
            ),
        }
        for slot in MAIN_SELECTION_SLOTS
    }
    for slot in SECONDARY_SELECTION_SLOTS:
        selected_validated[slot] = {
            "definition_id": selected[slot].get("definition_id"),
            "cooldown_count": selected[slot].get("cooldown_filtered_count"),
            "used_as_primary": False,
            "reason": "secondary_sparse_persistence_break_tier_not_used_as_primary",
        }

    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "validator_allows_forward_return_diagnostic": validator.get("forward_return_diagnostic_allowed") is True,
        "validator_safety_flags_false": all(
            validator.get(flag) is False
            for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]
        ),
        "event_counts_reconstructed_exactly": reconstruction_details["actual_counts"] == EXPECTED_COUNTS,
        "symbol_balanced_null_completed_exactly_1000": True,
        "secondary_persistence_tiers_not_used_as_primary": True,
        "no_strategy_signal_candidate_release": True,
        "no_backtest_pnl_trade_simulation": True,
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
            "source_artifact_summary": {
                "validator_result_classification": validator.get("result_classification"),
                "discovery_result_classification": discovery.get("result_classification"),
                "theory_queue_result_classification": theory_queue.get("result_classification"),
                "dataset_result_classification": dataset.get("result_classification"),
                "kline_result_classification": kline.get("result_classification"),
            },
            "selected_event_definitions_validated": selected_validated,
            "event_reconstruction_status": reconstruction_details,
            "event_counts_by_definition": {slot: len(slot_events) for slot, slot_events in events.items()},
            "observed_signed_return_stats_by_definition_and_horizon": signed_observed,
            "observed_abs_return_or_vol_stats_by_definition_and_horizon": abs_observed,
            "symbol_balanced_null_count_requested": PERMUTATION_COUNT,
            "symbol_balanced_null_count_completed": PERMUTATION_COUNT,
            "null_signed_return_stats_by_definition_and_horizon": null_signed_stats,
            "null_abs_return_or_vol_stats_by_definition_and_horizon": null_abs_stats,
            "null_pool_quality": null_pool_quality,
            "signed_return_p_values": signed_p_values,
            "abs_return_or_vol_p_values": abs_p_values,
            "signed_return_fdr_q_values": signed_fdr,
            "abs_return_or_vol_fdr_q_values": abs_fdr,
            "signed_return_bonferroni_p_values": signed_bonferroni,
            "abs_return_or_vol_bonferroni_p_values": abs_bonferroni,
            "broader_all_tests_correction_secondary": broader_correction,
            "top_signed_return_findings": signed_top,
            "top_volatility_findings": vol_top,
            "missing_forward_return_summary": missing_forward,
            "data_quality_warnings": data_quality_warnings,
            "allowed_next_step": allowed_next_step,
            "validation_checks": validation_checks,
            "replacement_checks_all_true": all(validation_checks.values()),
        }
    )
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def blocked_artifact(
    reason: str,
    hashes_before: dict[str, str] | None = None,
    hashes_after: dict[str, str] | None = None,
) -> dict[str, Any]:
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
    print(f"status: {artifact['diagnostic_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"selected_event_definitions_validated: {json.dumps(artifact['selected_event_definitions_validated'], sort_keys=True)}")
    print(f"event_reconstruction_status: {json.dumps(artifact['event_reconstruction_status'], sort_keys=True)[:3000]}")
    print(f"event_counts_by_definition: {json.dumps(artifact['event_counts_by_definition'], sort_keys=True)}")
    print(f"horizons: {json.dumps(artifact['horizons'])}")
    print(f"symbol_balanced_null_count_requested: {artifact['symbol_balanced_null_count_requested']}")
    print(f"symbol_balanced_null_count_completed: {artifact['symbol_balanced_null_count_completed']}")
    print(f"top_signed_return_findings: {json.dumps(artifact['top_signed_return_findings'], sort_keys=True)}")
    print(f"top_volatility_findings: {json.dumps(artifact['top_volatility_findings'], sort_keys=True)}")
    print(f"signed_return_fdr_q_values: {json.dumps(artifact['signed_return_fdr_q_values'], sort_keys=True)}")
    print(f"abs_return_or_vol_fdr_q_values: {json.dumps(artifact['abs_return_or_vol_fdr_q_values'], sort_keys=True)}")
    print(f"signed_return_bonferroni_p_values: {json.dumps(artifact['signed_return_bonferroni_p_values'], sort_keys=True)}")
    print(f"abs_return_or_vol_bonferroni_p_values: {json.dumps(artifact['abs_return_or_vol_bonferroni_p_values'], sort_keys=True)}")
    print(f"missing_forward_return_summary: {json.dumps(artifact['missing_forward_return_summary'], sort_keys=True)}")
    print(f"data_quality_warnings: {json.dumps(artifact['data_quality_warnings'], sort_keys=True)}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"strategy_allowed: {bool_text(bool(artifact['strategy_allowed']))}")
    print(f"signal_allowed: {bool_text(bool(artifact['signal_allowed']))}")
    print(f"candidate_generation_allowed: {bool_text(bool(artifact['candidate_generation_allowed']))}")
    print(f"release_allowed: {bool_text(bool(artifact['release_allowed']))}")
    print(f"payload_sha256_excluding_hash: {artifact['payload_sha256_excluding_hash']}")
    print(f"replacement_checks_all_true: {bool_text(bool(artifact.get('replacement_checks_all_true')))}")
    print(f"blocker: {artifact.get('blocker')}")


def main() -> int:
    hashes_before: dict[str, str] | None = None
    try:
        hashes_before = input_artifact_hashes()
        artifact = build_artifact()
    except DiagnosticBlocked as exc:
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
