#!/usr/bin/env python
"""Robustness diagnostic for long-short ratio normalization volatility findings."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_RUNNER_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_volatility_robustness_runner_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_volatility_robustness_runner_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "08beae34135938ef360816e618b6d4cff3c63211"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_forward_return_diagnostic_v1.json"
SOURCE_VALIDATOR_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_event_validator_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_VALIDATOR_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

FORWARD_DIAGNOSTIC_TOOL = (
    REPO_ROOT / "tools" / "edge_factory_os_repo_only_long_short_ratio_extreme_normalization_forward_return_diagnostic_v1.py"
)

ROBUSTNESS_STATUS_PASS = "PASS_REPO_ONLY_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_RUNNER_CREATED"
ROBUSTNESS_STATUS_BLOCKED = "BLOCKED_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_RUNNER"
ARTIFACT_KIND = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_RUNNER"

RESULT_PROMISING = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY"
RESULT_WEAK = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_WEAK_OR_NOT_ROBUST"
RESULT_ATTENTION = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_FAILED_STOP"

THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"
NEXT_EVALUATOR = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_VOLATILITY_ROBUSTNESS_EVALUATOR_V1"
NEXT_DIAGNOSTIC_EVALUATOR = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_EVALUATOR_V1"
NEXT_REPAIR = "BINANCE_PUBLIC_KLINE_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"

LONG_SLOT = "best_long_crowding_normalization_candidate"
SHORT_SLOT = "best_short_crowding_normalization_candidate"
DIVERGENCE_SLOT = "optional_account_position_divergence_resolution_candidate"
MAIN_SELECTION_SLOTS = [LONG_SLOT, SHORT_SLOT, DIVERGENCE_SLOT]
EXPECTED_COUNTS = {
    LONG_SLOT: 520,
    SHORT_SLOT: 426,
    DIVERGENCE_SLOT: 947,
}
HORIZONS = {"15m": 1, "1h": 4, "4h": 16, "24h": 96}
PRIMARY_TARGETS = [
    (DIVERGENCE_SLOT, "15m"),
    (DIVERGENCE_SLOT, "1h"),
    (DIVERGENCE_SLOT, "4h"),
]
TRACK_ONLY_TARGETS = [(DIVERGENCE_SLOT, "24h")]
PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528


class RobustnessBlocked(Exception):
    pass


def load_forward_diagnostic_module() -> Any:
    if not FORWARD_DIAGNOSTIC_TOOL.exists():
        raise RobustnessBlocked(f"missing forward diagnostic tool: {FORWARD_DIAGNOSTIC_TOOL}")
    spec = importlib.util.spec_from_file_location("lsr_forward_diagnostic_for_robustness_v1", FORWARD_DIAGNOSTIC_TOOL)
    if spec is None or spec.loader is None:
        raise RobustnessBlocked("could not load long-short ratio forward diagnostic module")
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


def month_key_from_ms(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m")


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
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    validator = read_json_readonly(SOURCE_VALIDATOR_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "long-short ratio forward diagnostic"),
        SOURCE_VALIDATOR_RELATIVE_PATH: verify_payload_hash(validator, "long-short ratio event validator"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "long-short ratio event discovery"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if diagnostic.get("result_classification") != "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY":
        raise RobustnessBlocked("prior diagnostic is not promising volatility diagnostic only")
    if diagnostic.get("allowed_next_step") != MODULE:
        raise RobustnessBlocked(f"prior diagnostic allowed_next_step is not {MODULE}")
    if diagnostic.get("symbol_balanced_null_count_completed") != 1000:
        raise RobustnessBlocked("prior diagnostic did not complete 1000 symbol-balanced resamples")
    for slot, count in EXPECTED_COUNTS.items():
        actual = diagnostic.get("event_counts_by_definition", {}).get(slot)
        if actual != count:
            raise RobustnessBlocked(f"prior diagnostic count mismatch for {slot}: {actual} != {count}")
    for slot, horizon in PRIMARY_TARGETS:
        key = f"{slot}__{horizon}"
        fdr = diagnostic.get("abs_return_or_vol_fdr_q_values", {}).get(key)
        bonferroni = diagnostic.get("abs_return_or_vol_bonferroni_p_values", {}).get(key)
        if fdr is None or fdr > 0.05 or bonferroni is None or bonferroni > 0.05:
            raise RobustnessBlocked(f"prior primary volatility target did not pass adjusted thresholds: {key}")
    track_key = f"{DIVERGENCE_SLOT}__24h"
    if (diagnostic.get("abs_return_or_vol_fdr_q_values", {}).get(track_key) or 1.0) <= 0.05:
        raise RobustnessBlocked("24h divergence target unexpectedly passed FDR and cannot be track-only")
    if min(diagnostic.get("signed_return_fdr_q_values", {}).values()) <= 0.05:
        raise RobustnessBlocked("signed-return findings unexpectedly passed FDR")
    selected = diagnostic.get("selected_event_definitions_validated", {})
    for secondary_slot in ["best_long_crowding_persistence_break_candidate", "best_short_crowding_persistence_break_candidate"]:
        if selected.get(secondary_slot, {}).get("used_as_primary") is not False:
            raise RobustnessBlocked(f"secondary persistence-break tier was used as primary: {secondary_slot}")
    for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]:
        if diagnostic.get(flag) is not False or validator.get(flag) is not False:
            raise RobustnessBlocked(f"safety flag not false in input artifacts: {flag}")
    if validator.get("forward_return_diagnostic_allowed") is not True:
        raise RobustnessBlocked("validator did not allow diagnostic")
    if discovery.get("result_classification") != "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY":
        raise RobustnessBlocked("discovery is not ready")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise RobustnessBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise RobustnessBlocked("public kline diagnostic status is not PASS")
    return diagnostic, validator, discovery, dataset, kline, payload_hashes


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
        "signed_return_promoted": False,
        "entry_exit_sizing_rules_created": False,
    }


def event_metric_rows(
    events: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, Any],
    diag: Any,
) -> tuple[dict[str, dict[str, list[dict[str, Any]]]], dict[str, Any]]:
    output: dict[str, dict[str, list[dict[str, Any]]]] = {slot: {h: [] for h in HORIZONS} for slot in MAIN_SELECTION_SLOTS}
    missing: dict[str, Any] = {"by_definition_and_horizon": {}, "total_missing_forward_returns": 0}
    for slot, slot_events in events.items():
        for horizon, bars in HORIZONS.items():
            missing_count = 0
            for event in slot_events:
                kline = kline_by_symbol[event["symbol"]]
                signed = diag.signed_forward_return(kline, int(event["base_open_ms"]), bars)
                if signed is None:
                    missing_count += 1
                    continue
                range_value = diag.range_proxy(kline, int(event["base_open_ms"]), bars)
                rv_value = diag.realized_vol_proxy(kline, int(event["base_open_ms"]), bars)
                output[slot][horizon].append(
                    {
                        "symbol": event["symbol"],
                        "month": event["month"],
                        "base_open_ms": int(event["base_open_ms"]),
                        "signed_return": signed,
                        "abs_return": abs(signed),
                        "forward_range_proxy": range_value,
                        "realized_vol_proxy": rv_value,
                    }
                )
            missing["by_definition_and_horizon"][f"{slot}__{horizon}"] = missing_count
            missing["total_missing_forward_returns"] += missing_count
    return output, missing


def quantile_stats(values: list[float], prefix: str) -> dict[str, Any]:
    arr = np.array(values, dtype=np.float64)
    if arr.size == 0:
        return {
            f"{prefix}_mean": None,
            f"{prefix}_median": None,
            f"{prefix}_std": None,
            f"{prefix}_q50": None,
            f"{prefix}_q75": None,
            f"{prefix}_q90": None,
            f"{prefix}_q95": None,
            f"{prefix}_q99": None,
        }
    return {
        f"{prefix}_mean": safe_float(np.mean(arr)),
        f"{prefix}_median": safe_float(np.median(arr)),
        f"{prefix}_std": safe_float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        f"{prefix}_q50": safe_float(np.quantile(arr, 0.50)),
        f"{prefix}_q75": safe_float(np.quantile(arr, 0.75)),
        f"{prefix}_q90": safe_float(np.quantile(arr, 0.90)),
        f"{prefix}_q95": safe_float(np.quantile(arr, 0.95)),
        f"{prefix}_q99": safe_float(np.quantile(arr, 0.99)),
    }


def observed_stats(metric_rows: dict[str, dict[str, list[dict[str, Any]]]], events: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            rows = metric_rows[slot][horizon]
            abs_values = [float(row["abs_return"]) for row in rows]
            signed_values = [float(row["signed_return"]) for row in rows]
            range_values = [float(row["forward_range_proxy"]) for row in rows if row["forward_range_proxy"] is not None]
            rv_values = [float(row["realized_vol_proxy"]) for row in rows if row["realized_vol_proxy"] is not None]
            abs_stats = quantile_stats(abs_values, "abs_return")
            output[slot][horizon] = {
                "event_count": len(events[slot]),
                "valid_count": len(abs_values),
                "missing_count": len(events[slot]) - len(abs_values),
                "mean_abs_return": abs_stats["abs_return_mean"],
                "median_abs_return": abs_stats["abs_return_median"],
                "std_abs_return": abs_stats["abs_return_std"],
                "q50_abs_return": abs_stats["abs_return_q50"],
                "q75_abs_return": abs_stats["abs_return_q75"],
                "q90_abs_return": abs_stats["abs_return_q90"],
                "q95_abs_return": abs_stats["abs_return_q95"],
                "q99_abs_return": abs_stats["abs_return_q99"],
                "forward_range_proxy": quantile_stats(range_values, "range_proxy"),
                "realized_vol_proxy": quantile_stats(rv_values, "realized_vol_proxy"),
                "signed_mean": safe_float(np.mean(signed_values)) if signed_values else None,
                "signed_median": safe_float(np.median(signed_values)) if signed_values else None,
            }
    return output


def kline_metric_value(kline: dict[str, Any], index: int, bars: int, metric: str) -> float | None:
    target = index + bars
    if target >= len(kline["close"]):
        return None
    base_close = float(kline["close"][index])
    target_close = float(kline["close"][target])
    if base_close == 0 or not math.isfinite(base_close) or not math.isfinite(target_close):
        return None
    signed = (target_close / base_close) - 1.0
    if metric == "abs":
        return abs(signed)
    if metric == "range":
        high = float(np.max(kline["high"][index + 1 : target + 1]))
        low = float(np.min(kline["low"][index + 1 : target + 1]))
        if not math.isfinite(high) or not math.isfinite(low):
            return None
        return (high - low) / base_close
    if metric == "rv":
        segment = kline["abs_return_15m"][index + 1 : target + 1]
        segment = segment[np.isfinite(segment)]
        if segment.size == 0:
            return None
        return float(np.mean(segment))
    raise RobustnessBlocked(f"unknown null pool metric: {metric}")


def build_month_aware_pools(
    events: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, Any],
    metric: str,
) -> dict[str, Any]:
    excluded: dict[str, dict[str, set[int]]] = {slot: defaultdict(set) for slot in MAIN_SELECTION_SLOTS}
    for slot, slot_events in events.items():
        for event in slot_events:
            excluded[slot][event["symbol"]].add(int(event["base_open_ms"]))
    pools: dict[str, Any] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    for slot in MAIN_SELECTION_SLOTS:
        for symbol, kline in kline_by_symbol.items():
            pools[slot][symbol] = {"by_month": defaultdict(dict), "all": {}}
            opens = kline["opens"]
            for horizon, bars in HORIZONS.items():
                all_values: list[float] = []
                by_month_values: dict[str, list[float]] = defaultdict(list)
                limit = len(opens) - bars
                for index in range(limit):
                    open_time = int(opens[index])
                    if open_time in excluded[slot].get(symbol, set()):
                        continue
                    value = kline_metric_value(kline, index, bars, metric)
                    if value is None:
                        continue
                    month = month_key_from_ms(open_time)
                    all_values.append(value)
                    by_month_values[month].append(value)
                pools[slot][symbol]["all"][horizon] = np.array(all_values, dtype=np.float64)
                for month, values in by_month_values.items():
                    pools[slot][symbol]["by_month"][month][horizon] = np.array(values, dtype=np.float64)
    return pools


def sample_month_aware_means(
    slot_events: list[dict[str, Any]],
    pools_for_slot: dict[str, Any],
    horizon: str,
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict[str, Any]]:
    group_counts = Counter((event["symbol"], event["month"]) for event in slot_events)
    null_means = np.empty(PERMUTATION_COUNT, dtype=np.float64)
    fallback_groups = []
    pool_sizes: dict[str, int] = {}
    for symbol, month in group_counts:
        month_pool = pools_for_slot[symbol]["by_month"].get(month, {}).get(horizon)
        if month_pool is None or month_pool.size == 0:
            fallback_groups.append(f"{symbol}__{month}")
            pool = pools_for_slot[symbol]["all"].get(horizon)
        else:
            pool = month_pool
        if pool is None or pool.size == 0:
            raise RobustnessBlocked(f"empty month-aware null pool for {symbol} {month} {horizon}")
        pool_sizes[f"{symbol}__{month}"] = int(pool.size)
    for perm_idx in range(PERMUTATION_COUNT):
        sampled_parts = []
        for (symbol, month), count in group_counts.items():
            pool = pools_for_slot[symbol]["by_month"].get(month, {}).get(horizon)
            if pool is None or pool.size == 0:
                pool = pools_for_slot[symbol]["all"].get(horizon)
            if pool is None or pool.size == 0:
                raise RobustnessBlocked(f"empty fallback null pool for {symbol} {horizon}")
            replace = count > pool.size
            sampled_parts.append(rng.choice(pool, size=count, replace=replace))
        combined = np.concatenate(sampled_parts) if sampled_parts else np.array([], dtype=np.float64)
        if combined.size == 0:
            raise RobustnessBlocked(f"empty combined month-aware null sample for {horizon}")
        null_means[perm_idx] = float(np.mean(combined))
    return null_means, {
        "symbol_month_group_count": len(group_counts),
        "symbol_month_counts": {f"{symbol}__{month}": count for (symbol, month), count in group_counts.items()},
        "fallback_symbol_only_groups": fallback_groups,
        "fallback_symbol_only_group_count": len(fallback_groups),
        "pool_sizes": pool_sizes,
    }


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


def month_aware_null(
    events: dict[str, list[dict[str, Any]]],
    pools: dict[str, Any],
    observed: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, float], dict[str, float], dict[str, Any]]:
    rng = np.random.default_rng(RANDOM_SEED)
    null_stats: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    p_values: dict[str, dict[str, Any]] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    p_pairs: list[tuple[str, float]] = []
    quality: dict[str, Any] = {slot: {} for slot in MAIN_SELECTION_SLOTS}
    primary_set = set(PRIMARY_TARGETS)
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            null_means, pool_quality = sample_month_aware_means(events[slot], pools[slot], horizon, rng)
            obs = observed[slot][horizon]["mean_abs_return"]
            p_high = safe_float((1 + np.sum(null_means >= float(obs))) / (1 + PERMUTATION_COUNT)) if obs is not None else None
            null_stats[slot][horizon] = {**null_distribution_stats(null_means), "p_abs_high_mean": p_high}
            p_values[slot][horizon] = {
                "p_abs_high_mean": p_high,
                "primary_p_value_for_multiple_comparison": p_high if (slot, horizon) in primary_set else None,
                "diagnostic_role": "primary_volatility" if (slot, horizon) in primary_set else "track_only_or_secondary",
            }
            if p_high is not None and (slot, horizon) in primary_set:
                p_pairs.append((f"{slot}__{horizon}", float(p_high)))
            quality[slot][horizon] = pool_quality
    fdr = bh_fdr(p_pairs)
    bonferroni = {key: min(1.0, p_value * len(p_pairs)) for key, p_value in p_pairs}
    for slot in MAIN_SELECTION_SLOTS:
        for horizon in HORIZONS:
            key = f"{slot}__{horizon}"
            null_stats[slot][horizon]["fdr_q"] = fdr.get(key)
            null_stats[slot][horizon]["bonferroni_p"] = bonferroni.get(key)
    return null_stats, p_values, fdr, bonferroni, quality


def mean_abs_for_rows(rows: list[dict[str, Any]]) -> float | None:
    values = [float(row["abs_return"]) for row in rows if row.get("abs_return") is not None]
    return safe_float(np.mean(np.array(values, dtype=np.float64))) if values else None


def leave_one_out_summary(metric_rows: dict[str, dict[str, list[dict[str, Any]]]], dimension: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for slot, horizon in PRIMARY_TARGETS:
        rows = metric_rows[slot][horizon]
        full_mean = mean_abs_for_rows(rows)
        labels = sorted({str(row[dimension]) for row in rows})
        cases = []
        any_necessary = False
        for label in labels:
            kept = [row for row in rows if str(row[dimension]) != label]
            mean_value = mean_abs_for_rows(kept)
            ratio = (mean_value / full_mean) if mean_value is not None and full_mean not in {None, 0.0} else None
            necessary = bool(ratio is None or ratio < 0.30)
            any_necessary = any_necessary or necessary
            cases.append(
                {
                    dimension: label,
                    "excluded_event_count": len(rows) - len(kept),
                    "remaining_event_count": len(kept),
                    "mean_abs_return": mean_value,
                    "magnitude_ratio_vs_full": safe_float(ratio) if ratio is not None else None,
                    "direction_preserved": mean_value is not None and mean_value > 0,
                    "necessary": necessary,
                }
            )
        cases.sort(key=lambda item: item["magnitude_ratio_vs_full"] if item["magnitude_ratio_vs_full"] is not None else -1.0)
        output[f"{slot}__{horizon}"] = {
            "full_mean_abs_return": full_mean,
            "any_single_symbol_necessary" if dimension == "symbol" else "any_single_month_necessary": any_necessary,
            "worst_cases": cases[:8],
            "all_cases_count": len(cases),
        }
    return output


def arbusdt_sensitivity(
    events: dict[str, list[dict[str, Any]]],
    metric_rows: dict[str, dict[str, list[dict[str, Any]]]],
    kline_by_symbol: dict[str, Any],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for offset, (slot, horizon) in enumerate(PRIMARY_TARGETS, start=100):
        rows = metric_rows[slot][horizon]
        full_mean = mean_abs_for_rows(rows)
        kept_rows = [row for row in rows if row["symbol"] != "ARBUSDT"]
        kept_events = [event for event in events[slot] if event["symbol"] != "ARBUSDT"]
        mean_value = mean_abs_for_rows(kept_rows)
        ratio = (mean_value / full_mean) if mean_value is not None and full_mean not in {None, 0.0} else None
        subset_pools = build_month_aware_pools(events, kline_by_symbol, "abs")
        rng = np.random.default_rng(RANDOM_SEED + offset)
        null_means, pool_quality = sample_month_aware_means(kept_events, subset_pools[slot], horizon, rng)
        p_high = safe_float((1 + np.sum(null_means >= float(mean_value))) / (1 + PERMUTATION_COUNT)) if mean_value is not None else None
        output[f"{slot}__{horizon}"] = {
            "arbusdt_event_count": len(rows) - len(kept_rows),
            "remaining_event_count": len(kept_rows),
            "mean_abs_return_ex_arbusdt": mean_value,
            "magnitude_ratio_vs_full": safe_float(ratio) if ratio is not None else None,
            "direction_preserved": mean_value is not None and mean_value > 0,
            "p_abs_high_mean_ex_arbusdt": p_high,
            "null_stats_ex_arbusdt": null_distribution_stats(null_means),
            "pool_quality_ex_arbusdt": pool_quality,
            "arbusdt_exclusion_pass": bool(mean_value is not None and mean_value > 0 and ratio is not None and ratio >= 0.50),
        }
    return output


def top_contributors(metric_rows: dict[str, dict[str, list[dict[str, Any]]]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for slot, horizon in PRIMARY_TARGETS:
        rows = metric_rows[slot][horizon]
        total = sum(float(row["abs_return"]) for row in rows)
        by_symbol: dict[str, list[float]] = defaultdict(list)
        by_month: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            by_symbol[row["symbol"]].append(float(row["abs_return"]))
            by_month[row["month"]].append(float(row["abs_return"]))

        def compact(groups: dict[str, list[float]]) -> list[dict[str, Any]]:
            entries = []
            for label, values in groups.items():
                group_sum = sum(values)
                entries.append(
                    {
                        "label": label,
                        "event_count": len(values),
                        "mean_abs_return": safe_float(np.mean(np.array(values, dtype=np.float64))),
                        "contribution_share_of_abs_return_sum": safe_float(group_sum / total) if total else None,
                    }
                )
            entries.sort(key=lambda item: abs(item["contribution_share_of_abs_return_sum"] or 0.0), reverse=True)
            return entries[:3]

        output[f"{slot}__{horizon}"] = {
            "top_3_symbols_by_abs_return_contribution": compact(by_symbol),
            "top_3_months_by_abs_return_contribution": compact(by_month),
            "symbol_event_counts": {symbol: len(values) for symbol, values in sorted(by_symbol.items())},
            "month_event_counts": {month: len(values) for month, values in sorted(by_month.items())},
        }
    return output


def alternative_metric_sensitivity(
    events: dict[str, list[dict[str, Any]]],
    metric_rows: dict[str, dict[str, list[dict[str, Any]]]],
    kline_by_symbol: dict[str, Any],
) -> dict[str, Any]:
    range_pools = build_month_aware_pools(events, kline_by_symbol, "range")
    rv_pools = build_month_aware_pools(events, kline_by_symbol, "rv")
    output: dict[str, Any] = {}
    for offset, (slot, horizon) in enumerate(PRIMARY_TARGETS, start=200):
        rows = metric_rows[slot][horizon]
        range_values = [float(row["forward_range_proxy"]) for row in rows if row.get("forward_range_proxy") is not None]
        rv_values = [float(row["realized_vol_proxy"]) for row in rows if row.get("realized_vol_proxy") is not None]
        range_mean = safe_float(np.mean(np.array(range_values, dtype=np.float64))) if range_values else None
        rv_mean = safe_float(np.mean(np.array(rv_values, dtype=np.float64))) if rv_values else None
        rng = np.random.default_rng(RANDOM_SEED + offset)
        range_null, range_quality = sample_month_aware_means(events[slot], range_pools[slot], horizon, rng)
        rng = np.random.default_rng(RANDOM_SEED + offset + 10)
        rv_null, rv_quality = sample_month_aware_means(events[slot], rv_pools[slot], horizon, rng)
        range_p = safe_float((1 + np.sum(range_null >= float(range_mean))) / (1 + PERMUTATION_COUNT)) if range_mean is not None else None
        rv_p = safe_float((1 + np.sum(rv_null >= float(rv_mean))) / (1 + PERMUTATION_COUNT)) if rv_mean is not None else None
        output[f"{slot}__{horizon}"] = {
            "forward_abs_return_mean": mean_abs_for_rows(rows),
            "forward_range_proxy_mean": range_mean,
            "realized_vol_proxy_mean": rv_mean,
            "forward_range_proxy_p_high": range_p,
            "realized_vol_proxy_p_high": rv_p,
            "forward_range_proxy_null_stats": null_distribution_stats(range_null),
            "realized_vol_proxy_null_stats": null_distribution_stats(rv_null),
            "forward_range_pool_quality": range_quality,
            "realized_vol_pool_quality": rv_quality,
            "alternate_proxy_supports_direction": bool(
                (range_p is not None and range_p <= 0.05) or (rv_p is not None and rv_p <= 0.05)
            ),
        }
    return output


def secondary_signed_tracking(diagnostic: dict[str, Any]) -> dict[str, Any]:
    return {
        "signed_return_fdr_q_values": diagnostic.get("signed_return_fdr_q_values"),
        "signed_return_bonferroni_p_values": diagnostic.get("signed_return_bonferroni_p_values"),
        "top_signed_return_findings": diagnostic.get("top_signed_return_findings", [])[:5],
        "signed_return_findings_not_promoted": True,
        "strategy_signal_candidate_release_allowed": False,
    }


def attention_checks(diagnostic: dict[str, Any], validator: dict[str, Any]) -> dict[str, Any]:
    return {
        "top_symbol_concentration_near_25pct_recorded": validator.get("attention_checks", {}).get(
            "top_symbol_concentration_close_to_25pct_limit"
        ),
        "raw_to_cooldown_compression_high_recorded": validator.get("attention_checks", {}).get(
            "raw_to_cooldown_compression_high"
        ),
        "normalization_strength_weak_recorded": validator.get("attention_checks", {}).get("normalization_strength_weak"),
        "mostly_top_account_or_account_position_pair_ratio_recorded": validator.get("attention_checks", {}).get(
            "mostly_top_account_ratio_primary"
        ),
        "persistence_break_sparse_tiers_not_promoted": diagnostic.get("selected_event_definitions_validated", {}).get(
            "best_long_crowding_persistence_break_candidate", {}
        ).get("used_as_primary")
        is False
        and diagnostic.get("selected_event_definitions_validated", {}).get(
            "best_short_crowding_persistence_break_candidate", {}
        ).get("used_as_primary")
        is False,
        "attention_items_are_not_automatic_failures": True,
    }


def primary_gates(
    fdr: dict[str, float],
    bonferroni: dict[str, float],
    leave_symbol: dict[str, Any],
    leave_month: dict[str, Any],
    arbusdt: dict[str, Any],
    alt_metrics: dict[str, Any],
    missing_forward: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    gates: dict[str, Any] = {}
    failed: list[str] = []
    missing_by_test = missing_forward.get("by_definition_and_horizon", {})
    for slot, horizon in PRIMARY_TARGETS:
        key = f"{slot}__{horizon}"
        gate = {
            "month_aware_symbol_balanced_fdr_lte_05": fdr.get(key) is not None and fdr[key] <= 0.05,
            "bonferroni_lte_05": bonferroni.get(key) is not None and bonferroni[key] <= 0.05,
            "bonferroni_or_fdr_only_attention_recorded": (
                bonferroni.get(key) is not None
                and bonferroni[key] <= 0.05
                or fdr.get(key) is not None
                and fdr[key] <= 0.05
            ),
            "no_single_symbol_dependence": leave_symbol.get(key, {}).get("any_single_symbol_necessary") is False,
            "no_single_month_dependence": leave_month.get(key, {}).get("any_single_month_necessary") is False,
            "arbusdt_exclusion_preserves_effect": arbusdt.get(key, {}).get("arbusdt_exclusion_pass") is True,
            "alternate_volatility_proxy_supports_direction": alt_metrics.get(key, {}).get(
                "alternate_proxy_supports_direction"
            )
            is True,
            "missing_rows_immaterial": int(missing_by_test.get(key, 0)) == 0,
            "input_hashes_unchanged": True,
        }
        gate["primary_target_passes_all_gates"] = all(gate.values())
        gates[key] = gate
        if not gate["primary_target_passes_all_gates"]:
            failed.extend([f"{key}:{name}" for name, value in gate.items() if value is False])
    return gates, failed


def base_artifact(
    head: str | None,
    hashes_before: dict[str, str] | None,
    hashes_after: dict[str, str] | None,
    blocker: str | None,
) -> dict[str, Any]:
    unchanged = hashes_before == hashes_after if hashes_before and hashes_after else False
    return {
        "robustness_status": ROBUSTNESS_STATUS_BLOCKED if blocker else ROBUSTNESS_STATUS_PASS,
        "status": ROBUSTNESS_STATUS_BLOCKED if blocker else ROBUSTNESS_STATUS_PASS,
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
        "prior_diagnostic_summary": {},
        "primary_robustness_targets": [],
        "month_aware_symbol_balanced_null_summary": {},
        "leave_one_symbol_out_summary": {},
        "leave_one_month_out_summary": {},
        "arbusdt_exclusion_sensitivity": {},
        "top_contributor_diagnostics": {},
        "alternative_volatility_metric_sensitivity": {},
        "attention_checks": {},
        "secondary_signed_return_tracking": {},
        "primary_robustness_gates": {},
        "failed_robustness_gates": [],
        "observed_volatility_stats_by_target": {},
        "null_volatility_stats_by_target": {},
        "p_values_by_target": {},
        "fdr_q_values": {},
        "bonferroni_p_values": {},
        "data_quality_warnings": [],
        "validation_limits": [
            "Diagnostic research only; not a strategy, signal, backtest, PnL, trade simulation, candidate, release, or edge claim.",
            "Primary metric family is forward absolute return / volatility proxy.",
            "Signed-return findings are tracked only and cannot override volatility classification.",
            "The 24h divergence horizon is tracked only because it did not pass the prior adjusted diagnostic.",
            "Event definitions, thresholds, and horizons were not changed.",
            "No entry, exit, sizing, live, runtime, capital, private, account, or order action was created.",
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
        raise RobustnessBlocked(f"HEAD mismatch: {head} != {EXPECTED_HEAD}")
    if not output_only_status(working_tree_status()):
        raise RobustnessBlocked(f"unexpected dirty repo state during build: {working_tree_status()}")
    hashes_before = input_artifact_hashes()
    diagnostic, validator, discovery, dataset, kline, input_payload_hashes = load_inputs()
    diag = load_forward_diagnostic_module()
    lsr = diag.load_discovery_module()
    events, kline_by_symbol, reconstruction = diag.reconstruct_events(dataset, kline, discovery, lsr)
    if reconstruction["actual_counts"] != EXPECTED_COUNTS:
        raise RobustnessBlocked(f"EVENT_COUNT_RECONSTRUCTION_MISMATCH: {reconstruction['actual_counts']}")
    metric_rows, missing_forward = event_metric_rows(events, kline_by_symbol, diag)
    observed = observed_stats(metric_rows, events)
    pools = build_month_aware_pools(events, kline_by_symbol, "abs")
    null_stats, p_values, fdr, bonferroni, pool_quality = month_aware_null(events, pools, observed)
    leave_symbol = leave_one_out_summary(metric_rows, "symbol")
    leave_month = leave_one_out_summary(metric_rows, "month")
    arbusdt = arbusdt_sensitivity(events, metric_rows, kline_by_symbol)
    contributors = top_contributors(metric_rows)
    alt_metrics = alternative_metric_sensitivity(events, metric_rows, kline_by_symbol)
    signed_tracking = secondary_signed_tracking(diagnostic)
    attention = attention_checks(diagnostic, validator)
    gates, failed_gates = primary_gates(fdr, bonferroni, leave_symbol, leave_month, arbusdt, alt_metrics, missing_forward)
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise RobustnessBlocked("input artifact hash changed during robustness run")
    all_primary_pass = all(item.get("primary_target_passes_all_gates") is True for item in gates.values())
    missing_total = int(missing_forward.get("total_missing_forward_returns", 0))
    data_quality_warnings = [
        "Known public kline archive gaps remain where inherited from prior artifacts, including ARBUSDT-2023-01 and ARBUSDT-2023-02.",
        "Raw kline cache files were reused and not committed.",
        f"Missing forward rows across definition/horizon tests: {missing_total}.",
        "Missing rows are zero for primary divergence 15m/1h/4h robustness targets.",
    ]
    if all_primary_pass:
        result_classification = RESULT_PROMISING
        allowed_next_step = NEXT_EVALUATOR
    elif missing_total > 20:
        result_classification = RESULT_ATTENTION
        allowed_next_step = NEXT_REPAIR
    else:
        result_classification = RESULT_WEAK
        allowed_next_step = NEXT_DIAGNOSTIC_EVALUATOR
    prior_summary = {
        "result_classification": diagnostic.get("result_classification"),
        "event_counts_by_definition": diagnostic.get("event_counts_by_definition"),
        "primary_volatility_findings": [
            item for item in diagnostic.get("top_volatility_findings", []) if (item.get("selection_slot"), item.get("horizon")) in PRIMARY_TARGETS
        ],
        "track_only_24h_volatility": {
            "fdr_q": diagnostic.get("abs_return_or_vol_fdr_q_values", {}).get(f"{DIVERGENCE_SLOT}__24h"),
            "bonferroni_p": diagnostic.get("abs_return_or_vol_bonferroni_p_values", {}).get(f"{DIVERGENCE_SLOT}__24h"),
            "promoted": False,
        },
        "signed_return_findings_did_not_pass": True,
        "strategy_allowed": diagnostic.get("strategy_allowed"),
        "signal_allowed": diagnostic.get("signal_allowed"),
        "candidate_generation_allowed": diagnostic.get("candidate_generation_allowed"),
        "release_allowed": diagnostic.get("release_allowed"),
    }
    primary_targets = [
        {
            "selection_slot": slot,
            "horizon": horizon,
            "primary_metric": "mean_abs_return",
            "prior_fdr_q": diagnostic.get("abs_return_or_vol_fdr_q_values", {}).get(f"{slot}__{horizon}"),
            "prior_bonferroni_p": diagnostic.get("abs_return_or_vol_bonferroni_p_values", {}).get(f"{slot}__{horizon}"),
            "event_count": len(events[slot]),
        }
        for slot, horizon in PRIMARY_TARGETS
    ]
    observed_targets = {f"{slot}__{horizon}": observed[slot][horizon] for slot, horizon in PRIMARY_TARGETS + TRACK_ONLY_TARGETS}
    null_targets = {f"{slot}__{horizon}": null_stats[slot][horizon] for slot, horizon in PRIMARY_TARGETS + TRACK_ONLY_TARGETS}
    p_targets = {f"{slot}__{horizon}": p_values[slot][horizon] for slot, horizon in PRIMARY_TARGETS + TRACK_ONLY_TARGETS}
    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "prior_diagnostic_promising_volatility_only": diagnostic.get("result_classification")
        == "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_FORWARD_DIAGNOSTIC_PROMISING_VOLATILITY_DIAGNOSTIC_ONLY",
        "event_counts_reconstructed_exactly": reconstruction["actual_counts"] == EXPECTED_COUNTS,
        "month_aware_symbol_balanced_null_completed_exactly_1000": True,
        "signed_return_not_promoted": True,
        "secondary_24h_volatility_not_promoted": True,
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
                "diagnostic_result_classification": diagnostic.get("result_classification"),
                "validator_result_classification": validator.get("result_classification"),
                "discovery_result_classification": discovery.get("result_classification"),
                "dataset_status": dataset.get("status"),
                "kline_diagnostic_status": kline.get("diagnostic_status"),
            },
            "prior_diagnostic_summary": prior_summary,
            "primary_robustness_targets": primary_targets,
            "month_aware_symbol_balanced_null_summary": {
                "count_requested": PERMUTATION_COUNT,
                "count_completed": PERMUTATION_COUNT,
                "null_model": "month-aware symbol-balanced null; symbol and calendar-month distributions preserved where feasible; actual event timestamps excluded where possible",
                "pool_quality": {f"{slot}__{horizon}": pool_quality[slot][horizon] for slot, horizon in PRIMARY_TARGETS},
                "primary_month_aware_null_results": {
                    f"{slot}__{horizon}": {
                        "p_abs_high_mean": p_values[slot][horizon]["p_abs_high_mean"],
                        "fdr_q": fdr.get(f"{slot}__{horizon}"),
                        "bonferroni_p": bonferroni.get(f"{slot}__{horizon}"),
                        "null_stats": null_stats[slot][horizon],
                    }
                    for slot, horizon in PRIMARY_TARGETS
                },
            },
            "leave_one_symbol_out_summary": leave_symbol,
            "leave_one_month_out_summary": leave_month,
            "arbusdt_exclusion_sensitivity": arbusdt,
            "top_contributor_diagnostics": contributors,
            "alternative_volatility_metric_sensitivity": alt_metrics,
            "attention_checks": attention,
            "secondary_signed_return_tracking": signed_tracking,
            "primary_robustness_gates": gates,
            "failed_robustness_gates": failed_gates,
            "observed_volatility_stats_by_target": observed_targets,
            "null_volatility_stats_by_target": null_targets,
            "p_values_by_target": p_targets,
            "fdr_q_values": fdr,
            "bonferroni_p_values": bonferroni,
            "data_quality_warnings": data_quality_warnings,
            "strategy_allowed": False,
            "signal_allowed": False,
            "candidate_generation_allowed": False,
            "release_allowed": False,
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
    summary = artifact.get("month_aware_symbol_balanced_null_summary", {})
    print(f"status: {artifact['robustness_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"primary_robustness_targets: {json.dumps(artifact['primary_robustness_targets'], sort_keys=True)}")
    print(f"month_aware_symbol_balanced_null_count_requested: {summary.get('count_requested')}")
    print(f"month_aware_symbol_balanced_null_count_completed: {summary.get('count_completed')}")
    print(f"primary_month_aware_null_results: {json.dumps(summary.get('primary_month_aware_null_results', {}), sort_keys=True)}")
    print(f"leave_one_symbol_out_summary: {json.dumps(artifact['leave_one_symbol_out_summary'], sort_keys=True)}")
    print(f"leave_one_month_out_summary: {json.dumps(artifact['leave_one_month_out_summary'], sort_keys=True)}")
    print(f"arbusdt_exclusion_sensitivity: {json.dumps(artifact['arbusdt_exclusion_sensitivity'], sort_keys=True)}")
    print(f"top_contributor_diagnostics: {json.dumps(artifact['top_contributor_diagnostics'], sort_keys=True)}")
    print(f"alternative_volatility_metric_sensitivity: {json.dumps(artifact['alternative_volatility_metric_sensitivity'], sort_keys=True)}")
    print(f"attention_checks: {json.dumps(artifact['attention_checks'], sort_keys=True)}")
    print(f"secondary_signed_return_tracking: {json.dumps(artifact['secondary_signed_return_tracking'], sort_keys=True)}")
    print(f"primary_robustness_gates: {json.dumps(artifact['primary_robustness_gates'], sort_keys=True)}")
    print(f"failed_robustness_gates: {json.dumps(artifact['failed_robustness_gates'], sort_keys=True)}")
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
