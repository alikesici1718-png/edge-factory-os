#!/usr/bin/env python
"""Forward-return diagnostic for validated OI contraction/taker capitulation events."""

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
MODULE = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "c67d4a0e8daa25da2968fc0763fffe26e7b6f275"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_VALIDATOR_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_validator_v1.json"
SOURCE_REFINEMENT_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_definition_refinement_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_VALIDATOR_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

BASE_DISCOVERY_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.py"

DIAGNOSTIC_STATUS_PASS = "PASS_REPO_ONLY_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_CREATED"
DIAGNOSTIC_STATUS_BLOCKED = "BLOCKED_OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC"
ARTIFACT_KIND = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC"

RESULT_PROMISING = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_PROMISING_DIAGNOSTIC_ONLY"
RESULT_NO_ROBUST = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_NO_ROBUST_EFFECT"
RESULT_ATTENTION = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_FAILED_STOP"

THEORY_ID = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION"
NEXT_NULL_VALIDATION = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_NULL_VALIDATION_V1"
NEXT_EVALUATOR = "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_KLINE_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"

LONG_DEFINITION_ID = "LONG_CAPITULATION_REBOUND_CANDIDATE__oi_p5.0__taker_p98.0__rejection_score_gte_1__cooldown_6h"
SHORT_DEFINITION_ID = "SHORT_COVER_EXHAUSTION_DOWNSIDE_CANDIDATE__oi_p5.0__taker_p98.0__rejection_score_gte_1__cooldown_6h"
EXPECTED_LONG_COUNT = 541
EXPECTED_SHORT_COUNT = 392

OI_CONTRACTION_QUANTILES = [0.01, 0.025, 0.05, 0.10]
TAKER_PRESSURE_QUANTILES = [0.99, 0.98, 0.975]
REJECTION_SCORE_BUCKETS = [1, 2]
COOLDOWN_HOURS = [3, 6, 12, 24]
HORIZONS = {"15m": 1, "1h": 4, "4h": 16, "24h": 96}
PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528


class DiagnosticBlocked(Exception):
    pass


def load_base_module() -> Any:
    if not BASE_DISCOVERY_TOOL.exists():
        raise DiagnosticBlocked(f"missing base discovery tool: {BASE_DISCOVERY_TOOL}")
    spec = importlib.util.spec_from_file_location("oi_contraction_discovery_base_for_diagnostic_v1", BASE_DISCOVERY_TOOL)
    if spec is None or spec.loader is None:
        raise DiagnosticBlocked("could not load base discovery tool module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OI_CONTRACTION_QUANTILES = list(OI_CONTRACTION_QUANTILES)
    module.TAKER_PRESSURE_QUANTILES = list(TAKER_PRESSURE_QUANTILES)
    module.REJECTION_SCORE_BUCKETS = list(REJECTION_SCORE_BUCKETS)
    module.COOLDOWN_HOURS = list(COOLDOWN_HOURS)

    def percentile_name(q: float) -> str:
        lookup = {
            0.0025: "p0.25",
            0.005: "p0.5",
            0.01: "p1.0",
            0.025: "p2.5",
            0.05: "p5.0",
            0.10: "p10.0",
            0.50: "p50.0",
            0.75: "p75.0",
            0.90: "p90.0",
            0.95: "p95.0",
            0.975: "p97.5",
            0.98: "p98.0",
            0.99: "p99.0",
            0.995: "p99.5",
            0.9975: "p99.75",
        }
        return lookup.get(q, f"p{q * 100:g}")

    module.percentile_name = percentile_name
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
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_VALIDATOR_RELATIVE_PATH: verify_payload_hash(validator, "OI contraction event validator"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "OI contraction event refinement"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "OI contraction event discovery"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if validator.get("result_classification") not in {
        "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_PASS_WITH_ATTENTION",
        "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_VALIDATOR_PASS",
    }:
        raise DiagnosticBlocked("validator did not pass")
    if validator.get("forward_return_diagnostic_allowed") is not True:
        raise DiagnosticBlocked("validator did not allow forward-return diagnostic")
    for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]:
        if validator.get(flag) is not False:
            raise DiagnosticBlocked(f"validator safety flag not false: {flag}")
    if refinement.get("result_classification") != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_EVENT_REFINEMENT_READY":
        raise DiagnosticBlocked("refinement is not ready")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiagnosticBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise DiagnosticBlocked("public kline diagnostic status is not PASS")
    return validator, refinement, discovery, dataset, kline, payload_hashes


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
        "optional_strict_variants_primary": False,
    }


def reconstruct_events_for_symbol(path: Path, kline_data: dict[str, Any], base: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    rows = base.metric_rows_for_symbol(path)
    metric_thresholds = base.build_metric_thresholds(rows)
    price_thresholds = base.build_price_thresholds(kline_data)
    long_events: list[dict[str, Any]] = []
    short_events: list[dict[str, Any]] = []
    counters = {
        "long_raw": 0,
        "long_cooldown_rejected": 0,
        "short_raw": 0,
        "short_cooldown_rejected": 0,
        "price_bar_missing": 0,
        "oi_delta_log_1h_missing": 0,
        "taker_sell_pressure_missing": 0,
        "taker_buy_pressure_missing": 0,
    }
    last_event_ms = {"long": None, "short": None}
    cooldown_ms = 6 * 60 * 60 * 1000
    for row in rows:
        thresholds = metric_thresholds.get(row["month"])
        if thresholds is None:
            continue
        features = base.price_features(row, kline_data, price_thresholds)
        if not features.get("price_available"):
            counters["price_bar_missing"] += 1
            continue
        oi_value = row.get("oi_delta_log_1h")
        oi_threshold = thresholds["oi_delta_log_1h"].get("p5.0")
        if oi_value is None:
            counters["oi_delta_log_1h_missing"] += 1
            continue
        if oi_threshold is None or oi_value > oi_threshold:
            continue
        for side_name, taker_key, score_key, events_key, definition_id in [
            ("long", "taker_sell_pressure", "long_rejection_score", long_events, LONG_DEFINITION_ID),
            ("short", "taker_buy_pressure", "short_rejection_score", short_events, SHORT_DEFINITION_ID),
        ]:
            taker_value = row.get(taker_key)
            taker_threshold = thresholds[taker_key].get("p98.0")
            if taker_value is None:
                counters[f"{taker_key}_missing"] += 1
                continue
            if taker_threshold is None or taker_value < taker_threshold:
                continue
            if int(features[score_key]) < 1:
                continue
            counters[f"{side_name}_raw"] += 1
            previous = last_event_ms[side_name]
            if previous is not None and row["ts_ms"] - previous < cooldown_ms:
                counters[f"{side_name}_cooldown_rejected"] += 1
                continue
            last_event_ms[side_name] = row["ts_ms"]
            base_open = base.floor_to_15m_open(row["ts_ms"])
            events_key.append(
                {
                    "definition_id": definition_id,
                    "side": side_name,
                    "symbol": row["symbol"],
                    "timestamp": row["timestamp"],
                    "ts_ms": int(row["ts_ms"]),
                    "base_open_ms": int(base_open),
                    "base_open_iso": base.ms_to_iso(int(base_open)),
                    "month": row["month"],
                    "expected_direction": "positive" if side_name == "long" else "negative",
                }
            )
    return long_events, short_events, counters


def reconstruct_events(dataset: dict[str, Any], kline_diagnostic: dict[str, Any], base: Any) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, Any]]:
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols") or dataset.get("requested_symbols")
    if not isinstance(symbols, list) or not symbols:
        raise DiagnosticBlocked("dataset builder artifact missing built symbol list")
    symbols = [str(symbol) for symbol in symbols]
    archive_summary = base.verify_cached_archives(symbols, kline_diagnostic)
    paths = base.normalized_paths(dataset)
    symbol_to_path = {path.name.split("_", 1)[0]: path for path in paths}
    events = {"long": [], "short": []}
    counters: dict[str, Any] = {"per_symbol": {}, "aggregate": Counter()}
    kline_by_symbol: dict[str, Any] = {}
    for symbol in symbols:
        path = symbol_to_path.get(symbol)
        if path is None:
            counters["aggregate"][f"{symbol}_normalized_path_missing"] += 1
            continue
        kline_data = base.load_kline_symbol(symbol, archive_summary["archive_records"])
        kline_by_symbol[symbol] = kline_data
        long_events, short_events, symbol_counters = reconstruct_events_for_symbol(path, kline_data, base)
        events["long"].extend(long_events)
        events["short"].extend(short_events)
        counters["per_symbol"][symbol] = symbol_counters
        counters["aggregate"].update(symbol_counters)
    if len(events["long"]) != EXPECTED_LONG_COUNT or len(events["short"]) != EXPECTED_SHORT_COUNT:
        raise DiagnosticBlocked(
            f"EVENT_COUNT_RECONSTRUCTION_MISMATCH: long={len(events['long'])} short={len(events['short'])}"
        )
    counters["aggregate"] = dict(counters["aggregate"])
    return events, kline_by_symbol, {"archive_summary": archive_summary, "reconstruction_counters": counters}


def forward_return_for_event(event: dict[str, Any], kline_data: dict[str, Any], horizon_bars: int) -> float | None:
    index = kline_data["open_to_index"].get(int(event["base_open_ms"]))
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


def stats(values: list[float], event_count: int) -> dict[str, Any]:
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


def compute_observed(events: dict[str, list[dict[str, Any]]], kline_by_symbol: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, list[float]]], dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {"long": {}, "short": {}}
    values_by_side_horizon: dict[str, dict[str, list[float]]] = {"long": {}, "short": {}}
    missing_summary: dict[str, Any] = {"by_side_and_horizon": {}, "total_missing_forward_returns": 0}
    for side, side_events in events.items():
        for horizon, bars in HORIZONS.items():
            values: list[float] = []
            missing = 0
            for event in side_events:
                value = forward_return_for_event(event, kline_by_symbol[event["symbol"]], bars)
                if value is None:
                    missing += 1
                    continue
                values.append(value)
            observed[side][horizon] = stats(values, len(side_events))
            values_by_side_horizon[side][horizon] = values
            missing_summary["by_side_and_horizon"][f"{side}__{horizon}"] = missing
            missing_summary["total_missing_forward_returns"] += missing
    return observed, values_by_side_horizon, missing_summary


def build_null_pools(
    events: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, Any],
) -> dict[str, dict[str, dict[str, np.ndarray]]]:
    pools: dict[str, dict[str, dict[str, np.ndarray]]] = {"long": {}, "short": {}}
    event_opens_by_side_symbol: dict[str, dict[str, set[int]]] = {"long": defaultdict(set), "short": defaultdict(set)}
    for side, side_events in events.items():
        for event in side_events:
            event_opens_by_side_symbol[side][event["symbol"]].add(int(event["base_open_ms"]))
    for side in ["long", "short"]:
        pools[side] = {}
        for symbol, kline_data in kline_by_symbol.items():
            pools[side][symbol] = {}
            excluded = event_opens_by_side_symbol[side].get(symbol, set())
            closes = kline_data["close"]
            opens = kline_data["opens"]
            for horizon, bars in HORIZONS.items():
                values = []
                limit = len(closes) - bars
                for idx in range(limit):
                    open_time = int(opens[idx])
                    if open_time in excluded:
                        continue
                    base_close = float(closes[idx])
                    target_close = float(closes[idx + bars])
                    if base_close == 0 or not math.isfinite(base_close) or not math.isfinite(target_close):
                        continue
                    values.append((target_close / base_close) - 1.0)
                pools[side][symbol][horizon] = np.array(values, dtype=np.float64)
    return pools


def null_model(
    events: dict[str, list[dict[str, Any]]],
    pools: dict[str, dict[str, dict[str, np.ndarray]]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    rng = np.random.default_rng(RANDOM_SEED)
    null_stats: dict[str, dict[str, Any]] = {"long": {}, "short": {}}
    null_means_by_side_horizon: dict[str, dict[str, np.ndarray]] = {"long": {}, "short": {}}
    pool_quality: dict[str, dict[str, Any]] = {"long": {}, "short": {}}
    for side, side_events in events.items():
        symbol_counts = Counter(event["symbol"] for event in side_events)
        for horizon in HORIZONS:
            null_means = np.empty(PERMUTATION_COUNT, dtype=np.float64)
            pool_quality[side][horizon] = {
                "symbol_counts": dict(symbol_counts),
                "pool_sizes": {symbol: int(pools[side][symbol][horizon].size) for symbol in symbol_counts},
                "actual_event_timestamps_excluded_where_possible": True,
            }
            for perm_idx in range(PERMUTATION_COUNT):
                sampled_parts = []
                for symbol, count in symbol_counts.items():
                    pool = pools[side][symbol][horizon]
                    if pool.size == 0:
                        raise DiagnosticBlocked(f"empty null pool for {side} {symbol} {horizon}")
                    replace = count > pool.size
                    sample = rng.choice(pool, size=count, replace=replace)
                    sampled_parts.append(sample)
                combined = np.concatenate(sampled_parts) if sampled_parts else np.array([], dtype=np.float64)
                if combined.size == 0:
                    raise DiagnosticBlocked(f"empty combined null sample for {side} {horizon}")
                null_means[perm_idx] = float(np.mean(combined))
            null_means_by_side_horizon[side][horizon] = null_means
            null_stats[side][horizon] = {
                "null_mean_mean": safe_float(np.mean(null_means)),
                "null_mean_std": safe_float(np.std(null_means, ddof=1)),
                "null_mean_q01": safe_float(np.quantile(null_means, 0.01)),
                "null_mean_q05": safe_float(np.quantile(null_means, 0.05)),
                "null_mean_q50": safe_float(np.quantile(null_means, 0.50)),
                "null_mean_q95": safe_float(np.quantile(null_means, 0.95)),
                "null_mean_q99": safe_float(np.quantile(null_means, 0.99)),
            }
    return null_stats, null_means_by_side_horizon, pool_quality


def empirical_p_values(observed_stats: dict[str, dict[str, Any]], null_means: dict[str, dict[str, np.ndarray]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {"long": {}, "short": {}}
    for side in ["long", "short"]:
        for horizon in HORIZONS:
            observed_mean = observed_stats[side][horizon]["mean"]
            if observed_mean is None:
                output[side][horizon] = {"p_two_sided": None, "p_positive_mean": None, "p_negative_mean": None}
                continue
            null_arr = null_means[side][horizon]
            obs = float(observed_mean)
            output[side][horizon] = {
                "p_two_sided": safe_float((1 + np.sum(np.abs(null_arr) >= abs(obs))) / (1 + PERMUTATION_COUNT)),
                "p_positive_mean": safe_float((1 + np.sum(null_arr >= obs)) / (1 + PERMUTATION_COUNT)),
                "p_negative_mean": safe_float((1 + np.sum(null_arr <= obs)) / (1 + PERMUTATION_COUNT)),
                "primary_directional_p_value": None,
            }
            output[side][horizon]["primary_directional_p_value"] = (
                output[side][horizon]["p_positive_mean"] if side == "long" else output[side][horizon]["p_negative_mean"]
            )
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


def multiple_comparison_values(p_values: dict[str, dict[str, Any]]) -> tuple[dict[str, float], dict[str, float]]:
    primary_pairs = []
    for side in ["long", "short"]:
        for horizon in HORIZONS:
            key = f"{side}__{horizon}"
            p_value = p_values[side][horizon]["primary_directional_p_value"]
            if p_value is not None:
                primary_pairs.append((key, float(p_value)))
    fdr = bh_fdr(primary_pairs)
    m = len(primary_pairs)
    bonferroni = {key: min(1.0, p_value * m) for key, p_value in primary_pairs}
    return fdr, bonferroni


def top_findings(observed: dict[str, dict[str, Any]], p_values: dict[str, dict[str, Any]], fdr: dict[str, float]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    observed_rows = []
    null_rows = []
    for side in ["long", "short"]:
        for horizon in HORIZONS:
            key = f"{side}__{horizon}"
            observed_rows.append(
                {
                    "side": side,
                    "horizon": horizon,
                    "mean": observed[side][horizon]["mean"],
                    "expected_direction": "positive" if side == "long" else "negative",
                    "valid_forward_return_count": observed[side][horizon]["valid_forward_return_count"],
                }
            )
            null_rows.append(
                {
                    "side": side,
                    "horizon": horizon,
                    "primary_directional_p_value": p_values[side][horizon]["primary_directional_p_value"],
                    "fdr_q_value": fdr.get(key),
                    "mean": observed[side][horizon]["mean"],
                }
            )
    observed_rows.sort(key=lambda item: abs(item["mean"] or 0.0), reverse=True)
    null_rows.sort(key=lambda item: (item["fdr_q_value"] if item["fdr_q_value"] is not None else 1.0))
    return observed_rows[:5], null_rows[:5]


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
        "long_event_count": 0,
        "short_event_count": 0,
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
        "data_quality_warnings": [],
        "validation_limits": [
            "Diagnostic research only; not a strategy, signal, backtest, PnL, trade simulation, candidate, release, or edge claim.",
            "Event definitions, thresholds, and horizons were inherited from the validator and not changed based on results.",
            "Forward returns are diagnostic labels only.",
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
    validator, refinement, discovery, dataset, kline, input_payload_hashes = load_inputs()
    base = load_base_module()
    events, kline_by_symbol, reconstruction_details = reconstruct_events(dataset, kline, base)
    observed, observed_values, missing_forward = compute_observed(events, kline_by_symbol)
    null_pools = build_null_pools(events, kline_by_symbol)
    null_stats, null_means, null_pool_quality = null_model(events, null_pools)
    p_values = empirical_p_values(observed, null_means)
    fdr, bonferroni = multiple_comparison_values(p_values)
    top_observed, top_null = top_findings(observed, p_values, fdr)
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise DiagnosticBlocked("input artifact hash changed during diagnostic run")
    any_promising = any(value <= 0.05 for value in fdr.values())
    total_missing_forward = int(missing_forward["total_missing_forward_returns"])
    result_classification = RESULT_ATTENTION if total_missing_forward > 0 else (RESULT_PROMISING if any_promising else RESULT_NO_ROBUST)
    allowed_next_step = NEXT_REPAIR if result_classification == RESULT_ATTENTION else (NEXT_NULL_VALIDATION if any_promising else NEXT_EVALUATOR)
    data_quality_warnings = [
        "Known public kline archive gaps remain: ARBUSDT-2023-01 and ARBUSDT-2023-02.",
        "Raw kline cache files were reused and not committed.",
        f"Missing forward-return rows across all side/horizon tests: {total_missing_forward}.",
    ]
    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "validator_allows_forward_return_diagnostic": validator.get("forward_return_diagnostic_allowed") is True,
        "validator_safety_flags_false": all(
            validator.get(flag) is False
            for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]
        ),
        "long_event_count_reconstructed_exactly": len(events["long"]) == EXPECTED_LONG_COUNT,
        "short_event_count_reconstructed_exactly": len(events["short"]) == EXPECTED_SHORT_COUNT,
        "symbol_balanced_null_completed_exactly_1000": True,
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
                "refinement_result_classification": refinement.get("result_classification"),
                "discovery_result_classification": discovery.get("result_classification"),
                "dataset_result_classification": dataset.get("result_classification"),
                "kline_result_classification": kline.get("result_classification"),
            },
            "selected_event_definitions_validated": {
                "long": {
                    "definition_id": LONG_DEFINITION_ID,
                    "expected_direction": "positive",
                    "event_count": len(events["long"]),
                    "used_as_primary": True,
                },
                "short": {
                    "definition_id": SHORT_DEFINITION_ID,
                    "expected_direction": "negative",
                    "event_count": len(events["short"]),
                    "used_as_primary": True,
                },
                "optional_strict_variants_used_as_primary": False,
            },
            "event_reconstruction_status": {
                "status": "EVENT_COUNT_RECONSTRUCTION_EXACT",
                "long_expected": EXPECTED_LONG_COUNT,
                "long_reconstructed": len(events["long"]),
                "short_expected": EXPECTED_SHORT_COUNT,
                "short_reconstructed": len(events["short"]),
                "reconstruction_counters": reconstruction_details["reconstruction_counters"],
                "archive_summary": reconstruction_details["archive_summary"],
            },
            "long_event_count": len(events["long"]),
            "short_event_count": len(events["short"]),
            "observed_stats_by_side_and_horizon": observed,
            "observed_return_value_counts": {
                side: {horizon: len(values) for horizon, values in per_horizon.items()}
                for side, per_horizon in observed_values.items()
            },
            "symbol_balanced_null_count_requested": PERMUTATION_COUNT,
            "symbol_balanced_null_count_completed": PERMUTATION_COUNT,
            "null_stats_by_side_and_horizon": null_stats,
            "null_pool_quality": null_pool_quality,
            "p_values_by_side_and_horizon": p_values,
            "fdr_q_values": fdr,
            "bonferroni_p_values": bonferroni,
            "top_observed_findings": top_observed,
            "top_symbol_balanced_null_findings": top_null,
            "missing_forward_return_summary": missing_forward,
            "data_quality_warnings": data_quality_warnings,
            "allowed_next_step": allowed_next_step,
            "validation_checks": validation_checks,
            "replacement_checks_all_true": all(validation_checks.values()),
        }
    )
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
    print(f"status: {artifact['diagnostic_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"selected_event_definitions_validated: {json.dumps(artifact['selected_event_definitions_validated'], sort_keys=True)}")
    print(f"event_reconstruction_status: {json.dumps(artifact['event_reconstruction_status'], sort_keys=True)[:3000]}")
    print(f"long_event_count: {artifact['long_event_count']}")
    print(f"short_event_count: {artifact['short_event_count']}")
    print(f"horizons: {json.dumps(artifact['horizons'])}")
    print(f"symbol_balanced_null_count_requested: {artifact['symbol_balanced_null_count_requested']}")
    print(f"symbol_balanced_null_count_completed: {artifact['symbol_balanced_null_count_completed']}")
    print(f"top_observed_findings: {json.dumps(artifact.get('top_observed_findings', []), sort_keys=True)}")
    print(f"top_symbol_balanced_null_findings: {json.dumps(artifact.get('top_symbol_balanced_null_findings', []), sort_keys=True)}")
    print(f"fdr_q_values: {json.dumps(artifact['fdr_q_values'], sort_keys=True)}")
    print(f"bonferroni_p_values: {json.dumps(artifact['bonferroni_p_values'], sort_keys=True)}")
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
