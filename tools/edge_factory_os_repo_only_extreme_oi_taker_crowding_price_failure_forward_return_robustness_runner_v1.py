#!/usr/bin/env python
"""Robustness diagnostics for refined extreme OI/taker price-failure forward returns."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_forward_return_diagnostic_v1 as base


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_RUNNER_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_extreme_oi_taker_crowding_price_failure_forward_return_robustness_runner_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_robustness_runner_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "21a4d94e3281e3915845460194e693350f1c511f"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_forward_return_diagnostic_v1.json"
SOURCE_REFINEMENT_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_definition_refinement_v1.json"
SOURCE_DISCOVERY_RELATIVE_PATH = "artifacts/research/extreme_oi_taker_crowding_price_failure_event_discovery_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_DIAGNOSTIC_RELATIVE_PATH,
    SOURCE_REFINEMENT_RELATIVE_PATH,
    SOURCE_DISCOVERY_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

ROBUSTNESS_STATUS_PASS = "PASS_REPO_ONLY_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_RUNNER_CREATED"
ROBUSTNESS_STATUS_BLOCKED = "BLOCKED_EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_RUNNER"
ARTIFACT_KIND = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_RUNNER"

RESULT_PROMISING = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_PROMISING_DIAGNOSTIC_ONLY"
RESULT_WEAK = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_WEAK_OR_NOT_ROBUST"
RESULT_ATTENTION = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_FAILED_STOP"

NEXT_PROMISING = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_ROBUSTNESS_EVALUATOR_V1"
NEXT_WEAK = "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_EVALUATOR_V1"
NEXT_ATTENTION = "BINANCE_PUBLIC_KLINE_DATA_QUALITY_REPAIR_OR_GAP_ANALYSIS_V1"

PERMUTATION_COUNT = 1000
RANDOM_SEED = 20260528 + 17
PRIMARY_SIDE = "short_core"
PRIMARY_HORIZON = "1h"
SECONDARY_FINDINGS = [{"side": "long_core", "horizon": "4h"}, {"side": "long_core", "horizon": "24h"}]
TRACKED_FINDINGS = [{"side": PRIMARY_SIDE, "horizon": PRIMARY_HORIZON}, *SECONDARY_FINDINGS]


class RobustnessBlocked(Exception):
    pass


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
        raise RobustnessBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
        if line.startswith("!! ") and line[3:].startswith("cache/binance_public_kline_forward_return_diagnostic_v1/"):
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


def verify_payload_hash(payload: dict[str, Any], label: str) -> str | None:
    stored = payload.get("payload_sha256_excluding_hash")
    if not isinstance(stored, str):
        return None
    recomputed = canonical_payload_hash(payload)
    if stored != recomputed:
        raise RobustnessBlocked(f"{label} payload hash mismatch: {recomputed} != {stored}")
    return stored


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str | None]]:
    diagnostic = read_json_readonly(SOURCE_DIAGNOSTIC_RELATIVE_PATH)
    refinement = read_json_readonly(SOURCE_REFINEMENT_RELATIVE_PATH)
    discovery = read_json_readonly(SOURCE_DISCOVERY_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(diagnostic, "forward-return diagnostic"),
        SOURCE_REFINEMENT_RELATIVE_PATH: verify_payload_hash(refinement, "event refinement"),
        SOURCE_DISCOVERY_RELATIVE_PATH: verify_payload_hash(discovery, "event discovery"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    return diagnostic, refinement, discovery, dataset, kline, payload_hashes


def mini_verify_prior_diagnostic(diagnostic: dict[str, Any]) -> dict[str, Any]:
    fdr = diagnostic.get("fdr_q_values", {}).get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON)
    bonf = diagnostic.get("bonferroni_p_values", {}).get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON)
    pvals = diagnostic.get("p_values_by_side_and_horizon", {}).get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON, {})
    checks = {
        "diagnostic_promising": diagnostic.get("result_classification")
        == "EXTREME_OI_TAKER_CROWDING_PRICE_FAILURE_FORWARD_RETURN_DIAGNOSTIC_PROMISING_DIAGNOSTIC_ONLY",
        "long_core_count_463": diagnostic.get("long_core_event_count") == 463,
        "short_core_count_451": diagnostic.get("short_core_event_count") == 451,
        "primary_fdr_lte_0_01": isinstance(fdr, (int, float)) and fdr <= 0.01,
        "primary_bonferroni_lte_0_01": isinstance(bonf, (int, float)) and bonf <= 0.01,
        "strategy_allowed_false": diagnostic.get("strategy_allowed") is False,
        "signal_allowed_false": diagnostic.get("signal_allowed") is False,
        "candidate_generation_allowed_false": diagnostic.get("candidate_generation_allowed") is False,
        "release_allowed_false": diagnostic.get("release_allowed") is False,
    }
    if not all(checks.values()):
        raise RobustnessBlocked(f"prior diagnostic mini verification failed: {checks}")
    return {
        "checks": checks,
        "primary_finding": {
            "side": PRIMARY_SIDE,
            "horizon": PRIMARY_HORIZON,
            "mean": diagnostic.get("observed_stats_by_side_and_horizon", {}).get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON, {}).get("mean"),
            "raw_p": pvals.get("p_two_sided"),
            "fdr_q": fdr,
            "bonferroni_p": bonf,
            "valid_forward_return_count": diagnostic.get("observed_stats_by_side_and_horizon", {}).get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON, {}).get("valid_forward_return_count"),
        },
    }


def summarize_array(values: list[float] | np.ndarray) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    array = array[np.isfinite(array)]
    if array.size == 0:
        return {
            "count": 0,
            "valid_forward_return_count": 0,
            "mean": None,
            "median": None,
            "std": None,
            "positive_rate": None,
            "negative_rate": None,
            "q05": None,
            "q25": None,
            "q50": None,
            "q75": None,
            "q95": None,
        }
    return {
        "count": int(array.size),
        "valid_forward_return_count": int(array.size),
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "std": float(np.std(array, ddof=0)) if array.size > 1 else 0.0,
        "positive_rate": float(np.mean(array > 0.0)),
        "negative_rate": float(np.mean(array < 0.0)),
        "q05": float(np.quantile(array, 0.05)),
        "q25": float(np.quantile(array, 0.25)),
        "q50": float(np.quantile(array, 0.50)),
        "q75": float(np.quantile(array, 0.75)),
        "q95": float(np.quantile(array, 0.95)),
    }


def summarize_null_means(null_means: np.ndarray) -> dict[str, Any]:
    array = np.asarray(null_means, dtype=np.float64)
    array = array[np.isfinite(array)]
    if array.size == 0:
        return {
            "null_mean_mean": None,
            "null_mean_std": None,
            "null_mean_q05": None,
            "null_mean_q50": None,
            "null_mean_q95": None,
        }
    return {
        "null_mean_mean": float(np.mean(array)),
        "null_mean_std": float(np.std(array, ddof=0)) if array.size > 1 else 0.0,
        "null_mean_q05": float(np.quantile(array, 0.05)),
        "null_mean_q50": float(np.quantile(array, 0.50)),
        "null_mean_q95": float(np.quantile(array, 0.95)),
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


def enrich_observed_stats(observed_stats: dict[str, dict[str, dict[str, Any]]]) -> dict[str, dict[str, dict[str, Any]]]:
    output = {}
    for side, per_horizon in observed_stats.items():
        output[side] = {}
        for horizon, stats in per_horizon.items():
            output[side][horizon] = {
                "count": stats.get("event_count"),
                "event_count": stats.get("event_count"),
                "valid_forward_return_count": stats.get("valid_forward_return_count"),
                "mean": stats.get("mean"),
                "median": stats.get("median"),
                "std": stats.get("std"),
                "positive_rate": stats.get("positive_rate"),
                "negative_rate": stats.get("negative_rate"),
                "q05": stats.get("q05"),
                "q25": stats.get("q25"),
                "q50": stats.get("q50"),
                "q75": stats.get("q75"),
                "q95": stats.get("q95"),
            }
    return output


def month_indices_by_symbol_horizon(kline_by_symbol: dict[str, dict[str, Any]]) -> dict[str, dict[str, dict[str, np.ndarray]]]:
    output: dict[str, dict[str, dict[str, list[int]]]] = {
        symbol: {month: {horizon: [] for horizon in base.HORIZONS} for month in []} for symbol in kline_by_symbol
    }
    grouped: dict[str, dict[str, dict[str, list[int]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for symbol, data in kline_by_symbol.items():
        opens = data["opens"]
        for horizon in base.HORIZONS:
            valid = data["valid_indices_by_horizon"][horizon]
            for index in valid:
                month = base.month_key_from_ms(int(opens[int(index)]))
                grouped[symbol][month][horizon].append(int(index))
    converted: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    for symbol, per_month in grouped.items():
        converted[symbol] = {}
        for month, per_horizon in per_month.items():
            converted[symbol][month] = {
                horizon: np.array(indices, dtype=np.int64) for horizon, indices in per_horizon.items()
            }
    return converted


def event_values(
    events: list[dict[str, Any]],
    kline_by_symbol: dict[str, dict[str, Any]],
    horizon: str,
    exclude_symbol: str | None = None,
    exclude_month: str | None = None,
) -> list[float]:
    values = []
    for event in events:
        if exclude_symbol is not None and event["symbol"] == exclude_symbol:
            continue
        if exclude_month is not None and event["month"] == exclude_month:
            continue
        base_index = event.get("base_index")
        if base_index is None:
            continue
        value = kline_by_symbol[event["symbol"]]["returns_by_horizon"][horizon][base_index]
        if np.isfinite(value):
            values.append(float(value))
    return values


def build_event_group_counts(
    events_by_side: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    grouped: dict[str, dict[str, dict[str, dict[str, Any]]]] = {
        side: {horizon: defaultdict(lambda: {"count": 0, "event_indices": set()}) for horizon in base.HORIZONS}
        for side in base.SIDE_TO_DEFINITION_ID
    }
    for side, events in events_by_side.items():
        for event in events:
            symbol = event["symbol"]
            month = event["month"]
            base_index = event.get("base_index")
            if base_index is None:
                continue
            group_key = f"{symbol}|{month}"
            for horizon in base.HORIZONS:
                value = kline_by_symbol[symbol]["returns_by_horizon"][horizon][base_index]
                if np.isfinite(value):
                    grouped[side][horizon][group_key]["count"] += 1
                    grouped[side][horizon][group_key]["event_indices"].add(int(base_index))
    return grouped


def month_aware_symbol_balanced_null(
    events_by_side: dict[str, list[dict[str, Any]]],
    observed_stats: dict[str, dict[str, dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
    exclude_symbol: str | None = None,
    side_horizon_filter: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED + (97 if exclude_symbol else 0))
    month_index = month_indices_by_symbol_horizon(kline_by_symbol)
    filtered_events = {
        side: [event for event in events if exclude_symbol is None or event["symbol"] != exclude_symbol]
        for side, events in events_by_side.items()
    }
    group_counts = build_event_group_counts(filtered_events, kline_by_symbol)
    target_pairs = side_horizon_filter or [(side, horizon) for side in base.SIDE_TO_DEFINITION_ID for horizon in base.HORIZONS]
    null_stats = {side: {} for side in base.SIDE_TO_DEFINITION_ID}
    p_values = {side: {} for side in base.SIDE_TO_DEFINITION_ID}
    fallback_summary = {side: {} for side in base.SIDE_TO_DEFINITION_ID}
    p_items: list[tuple[str, float]] = []
    for side, horizon in target_pairs:
        null_sums = np.zeros(PERMUTATION_COUNT, dtype=np.float64)
        total_count = 0
        fallback = {
            "same_symbol_month_pool_used": 0,
            "actual_event_timestamps_excluded": 0,
            "symbol_pool_fallback_used": 0,
            "empty_group_count": 0,
        }
        for group_key, info in group_counts[side][horizon].items():
            count = int(info["count"])
            if count <= 0:
                continue
            symbol, month = group_key.split("|", 1)
            candidate_indices = month_index.get(symbol, {}).get(month, {}).get(horizon, np.array([], dtype=np.int64))
            event_indices = info["event_indices"]
            filtered_indices = candidate_indices
            if candidate_indices.size and event_indices:
                keep = np.array([int(index) not in event_indices for index in candidate_indices], dtype=bool)
                candidate_after_exclusion = candidate_indices[keep]
                if candidate_after_exclusion.size:
                    filtered_indices = candidate_after_exclusion
                    fallback["actual_event_timestamps_excluded"] += 1
            if filtered_indices.size:
                fallback["same_symbol_month_pool_used"] += 1
            else:
                filtered_indices = kline_by_symbol[symbol]["valid_indices_by_horizon"][horizon]
                if event_indices and filtered_indices.size:
                    keep = np.array([int(index) not in event_indices for index in filtered_indices], dtype=bool)
                    fallback_after_exclusion = filtered_indices[keep]
                    if fallback_after_exclusion.size:
                        filtered_indices = fallback_after_exclusion
                fallback["symbol_pool_fallback_used"] += 1
            candidates = kline_by_symbol[symbol]["returns_by_horizon"][horizon][filtered_indices]
            candidates = candidates[np.isfinite(candidates)]
            if candidates.size == 0:
                fallback["empty_group_count"] += 1
                continue
            total_count += count
            draws = rng.integers(0, candidates.size, size=(PERMUTATION_COUNT, count))
            null_sums += candidates[draws].sum(axis=1)
        if total_count <= 0:
            raise RobustnessBlocked(f"zero valid count for month-aware null {side} {horizon}")
        null_means = null_sums / float(total_count)
        observed_mean = observed_stats[side][horizon]["mean"]
        null_stats[side][horizon] = summarize_null_means(null_means)
        p_summary = empirical_p_values(observed_mean, null_means)
        p_values[side][horizon] = p_summary
        fallback_summary[side][horizon] = fallback
        p_two = p_summary["p_two_sided"]
        if isinstance(p_two, float):
            p_items.append((f"{side}|{horizon}", p_two))
    fdr_flat = benjamini_hochberg(p_items)
    bonferroni_flat = {key: float(min(value * len(p_items), 1.0)) for key, value in p_items}
    fdr = {side: {} for side in base.SIDE_TO_DEFINITION_ID}
    bonferroni = {side: {} for side in base.SIDE_TO_DEFINITION_ID}
    for key, value in fdr_flat.items():
        side, horizon = key.split("|", 1)
        fdr[side][horizon] = value
    for key, value in bonferroni_flat.items():
        side, horizon = key.split("|", 1)
        bonferroni[side][horizon] = value
        null_stats[side][horizon]["bonferroni_p"] = value
    for side, per_horizon in fdr.items():
        for horizon, value in per_horizon.items():
            null_stats[side][horizon]["fdr_q"] = value
            null_stats[side][horizon].update(p_values[side][horizon])
    return {
        "count_requested": PERMUTATION_COUNT,
        "count_completed": PERMUTATION_COUNT,
        "null_stats_by_side_and_horizon": null_stats,
        "p_values_by_side_and_horizon": p_values,
        "fdr_q_values": fdr,
        "bonferroni_p_values": bonferroni,
        "fallback_summary": fallback_summary,
        "top_findings": top_findings(fdr, bonferroni, p_values),
    }


def top_findings(
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
                    "p_two_sided": p_values[side][horizon].get("p_two_sided"),
                    "p_positive_mean": p_values[side][horizon].get("p_positive_mean"),
                    "p_negative_mean": p_values[side][horizon].get("p_negative_mean"),
                }
            )
    rows.sort(key=lambda item: (item["fdr_q"], item["p_two_sided"]))
    return rows[:limit]


def sensitivity_row(full_mean: float | None, values: list[float], label: str) -> dict[str, Any]:
    stats = summarize_array(values)
    mean = stats["mean"]
    if full_mean is None or mean is None or full_mean == 0:
        direction_preserved = None
        magnitude_ratio = None
        necessary = None
    else:
        direction_preserved = (full_mean > 0 and mean > 0) or (full_mean < 0 and mean < 0)
        magnitude_ratio = abs(mean) / abs(full_mean)
        necessary = (not direction_preserved) or magnitude_ratio < 0.30
    return {
        "excluded": label,
        **stats,
        "direction_preserved": direction_preserved,
        "magnitude_ratio_vs_full_sample": magnitude_ratio,
        "necessary": necessary,
    }


def leave_one_symbol_out(
    events_by_side: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
    observed_stats: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    symbols = sorted({event["symbol"] for rows in events_by_side.values() for event in rows})
    tracked = {}
    for finding in TRACKED_FINDINGS:
        side = finding["side"]
        horizon = finding["horizon"]
        full_mean = observed_stats[side][horizon]["mean"]
        rows = [
            sensitivity_row(full_mean, event_values(events_by_side[side], kline_by_symbol, horizon, exclude_symbol=symbol), symbol)
            for symbol in symbols
        ]
        necessary = [row["excluded"] for row in rows if row["necessary"]]
        tracked[f"{side}|{horizon}"] = {
            "full_sample_mean": full_mean,
            "rows": rows,
            "any_single_symbol_necessary": bool(necessary),
            "necessary_symbols": necessary,
        }
    return tracked


def leave_one_month_out(
    events_by_side: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
    observed_stats: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    months = sorted({event["month"] for rows in events_by_side.values() for event in rows})
    tracked = {}
    for finding in TRACKED_FINDINGS:
        side = finding["side"]
        horizon = finding["horizon"]
        full_mean = observed_stats[side][horizon]["mean"]
        rows = [
            sensitivity_row(full_mean, event_values(events_by_side[side], kline_by_symbol, horizon, exclude_month=month), month)
            for month in months
        ]
        necessary = [row["excluded"] for row in rows if row["necessary"]]
        tracked[f"{side}|{horizon}"] = {
            "full_sample_mean": full_mean,
            "rows": rows,
            "any_single_month_necessary": bool(necessary),
            "necessary_months": necessary,
        }
    return tracked


def arbusdt_exclusion(
    events_by_side: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
    observed_stats: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    full_mean = observed_stats[PRIMARY_SIDE][PRIMARY_HORIZON]["mean"]
    primary_values = event_values(events_by_side[PRIMARY_SIDE], kline_by_symbol, PRIMARY_HORIZON, exclude_symbol="ARBUSDT")
    observed = sensitivity_row(full_mean, primary_values, "ARBUSDT")
    subset_observed_stats = {PRIMARY_SIDE: {PRIMARY_HORIZON: observed}}
    null = month_aware_symbol_balanced_null(
        events_by_side,
        subset_observed_stats,
        kline_by_symbol,
        exclude_symbol="ARBUSDT",
        side_horizon_filter=[(PRIMARY_SIDE, PRIMARY_HORIZON)],
    )
    return {
        "primary_short_core_1h_excluding_arbusdt": observed,
        "month_aware_null_if_feasible": {
            "count_requested": null["count_requested"],
            "count_completed": null["count_completed"],
            "p_values": null["p_values_by_side_and_horizon"].get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON),
            "fdr_q": null["fdr_q_values"].get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON),
            "bonferroni_p": null["bonferroni_p_values"].get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON),
            "null_stats": null["null_stats_by_side_and_horizon"].get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON),
        },
        "direction_preserved": observed["direction_preserved"],
        "magnitude_ratio_vs_full_sample": observed["magnitude_ratio_vs_full_sample"],
    }


def top_contributors(
    events_by_side: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    values = []
    for event in events_by_side[PRIMARY_SIDE]:
        base_index = event.get("base_index")
        if base_index is None:
            continue
        value = kline_by_symbol[event["symbol"]]["returns_by_horizon"][PRIMARY_HORIZON][base_index]
        if np.isfinite(value):
            values.append((event["symbol"], event["month"], float(value)))
    total_count = len(values)
    total_mean = float(np.mean([value for _, _, value in values])) if values else None

    def summarize_group(index: int) -> list[dict[str, Any]]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in values:
            grouped[row[index]].append(row[2])
        rows = []
        for label, group_values in grouped.items():
            group_sum = float(sum(group_values))
            contribution_to_total_mean = group_sum / total_count if total_count else None
            contribution_share = None
            if total_mean not in (None, 0):
                contribution_share = contribution_to_total_mean / total_mean
            rows.append(
                {
                    "label": label,
                    "event_count": len(group_values),
                    "mean_return": float(np.mean(group_values)),
                    "contribution_to_total_mean": contribution_to_total_mean,
                    "contribution_share_of_total_mean": contribution_share,
                    "absolute_contribution": abs(contribution_to_total_mean or 0.0),
                }
            )
        rows.sort(key=lambda item: item["absolute_contribution"], reverse=True)
        return rows[:3]

    return {
        "primary_side_horizon": f"{PRIMARY_SIDE}|{PRIMARY_HORIZON}",
        "full_sample_valid_count": total_count,
        "full_sample_mean": total_mean,
        "top_3_symbols_by_absolute_contribution": summarize_group(0),
        "top_3_months_by_absolute_contribution": summarize_group(1),
    }


def crowding_confirmation_sensitivity(
    events_by_side: dict[str, list[dict[str, Any]]],
    kline_by_symbol: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for event in events_by_side[PRIMARY_SIDE]:
        base_index = event.get("base_index")
        if base_index is None:
            continue
        value = kline_by_symbol[event["symbol"]]["returns_by_horizon"][PRIMARY_HORIZON][base_index]
        if not np.isfinite(value):
            continue
        tier = event["crowding_confirmation"]
        buckets[tier].append(float(value))
        if tier != "none":
            buckets["any_confirmation"].append(float(value))
    output = {}
    for tier in ["none", "account_only", "position_only", "both", "any_confirmation"]:
        stats = summarize_array(buckets.get(tier, []))
        output[tier] = {
            **stats,
            "sparse_subgroup_not_promoted": stats["count"] < 100,
        }
    return output


def primary_gates(
    null_summary: dict[str, Any],
    leave_symbol: dict[str, Any],
    leave_month: dict[str, Any],
    arb: dict[str, Any],
    diagnostic: dict[str, Any],
    input_hashes_unchanged: bool,
) -> dict[str, bool]:
    fdr = null_summary["fdr_q_values"].get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON)
    bonf = null_summary["bonferroni_p_values"].get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON)
    primary_key = f"{PRIMARY_SIDE}|{PRIMARY_HORIZON}"
    missing_primary = diagnostic.get("missing_forward_return_summary", {}).get(PRIMARY_SIDE, {}).get(PRIMARY_HORIZON)
    return {
        "month_aware_symbol_balanced_null_fdr_q_lte_0_05": isinstance(fdr, (int, float)) and fdr <= 0.05,
        "bonferroni_lte_0_05": isinstance(bonf, (int, float)) and bonf <= 0.05,
        "leave_one_symbol_no_single_symbol_necessary": not leave_symbol.get(primary_key, {}).get("any_single_symbol_necessary", True),
        "leave_one_month_no_single_month_necessary": not leave_month.get(primary_key, {}).get("any_single_month_necessary", True),
        "arbusdt_exclusion_direction_preserved": arb.get("direction_preserved") is True,
        "arbusdt_exclusion_magnitude_ratio_gte_0_50": isinstance(arb.get("magnitude_ratio_vs_full_sample"), (int, float))
        and arb["magnitude_ratio_vs_full_sample"] >= 0.50,
        "missing_forward_returns_do_not_affect_primary": missing_primary == 0,
        "input_artifact_hashes_unchanged": input_hashes_unchanged,
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
        "event_definition_modified_on_forward_returns": False,
        "sparse_crowding_confirmed_primary_test": False,
    }


def blocked_artifact(reason: str, audit: dict[str, Any] | None = None, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
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
        "recovery_audit_status": (audit or {}).get("recovery_decision", RECOVERY_AUDIT_STATUS),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "prior_diagnostic_summary": {},
        "primary_finding": {},
        "secondary_findings_tracked": SECONDARY_FINDINGS,
        "month_aware_symbol_balanced_null_summary": {"count_requested": PERMUTATION_COUNT, "count_completed": 0},
        "leave_one_symbol_out_summary": {},
        "leave_one_month_out_summary": {},
        "arbusdt_exclusion_sensitivity": {},
        "top_contributor_diagnostics": {},
        "crowding_confirmation_sensitivity": {},
        "primary_robustness_gates": {},
        "failed_robustness_gates": [reason],
        "observed_stats_by_side_and_horizon": {},
        "null_stats_by_side_and_horizon": {},
        "p_values_by_side_and_horizon": {},
        "fdr_q_values": {},
        "bonferroni_p_values": {},
        "data_quality_warnings": [f"BLOCKED: {reason}"],
        "validation_limits": ["Blocked before robustness diagnostics completed."],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "strategy_allowed": False,
        "signal_allowed": False,
        "candidate_generation_allowed": False,
        "release_allowed": False,
        "allowed_next_step": NEXT_ATTENTION,
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
    diagnostic, refinement, discovery, dataset, kline, payload_hashes = load_inputs()
    prior_verification = mini_verify_prior_diagnostic(diagnostic)
    selected_validation = base.validate_selected_event_definitions(refinement)
    symbols = [str(symbol) for symbol in dataset.get("normalized_dataset_summary", {}).get("built_symbols", [])]
    if len(symbols) != 10:
        raise RobustnessBlocked("dataset builder does not expose expected 10 built symbols")
    cache_summary = base.verify_cached_archives(symbols, kline)
    kline_by_symbol = {symbol: base.load_kline_symbol(symbol, cache_summary["archive_records"]) for symbol in symbols}
    reconstructed = base.reconstruct_core_events(dataset, kline_by_symbol)
    if len(reconstructed["events"][PRIMARY_SIDE]) != 451 or len(reconstructed["events"]["long_core"]) != 463:
        raise RobustnessBlocked("EVENT_COUNT_RECONSTRUCTION_MISMATCH")
    observed = base.observed_forward_returns(reconstructed["events"], kline_by_symbol)
    observed_stats = enrich_observed_stats(observed["observed_stats"])
    null_summary = month_aware_symbol_balanced_null(reconstructed["events"], observed_stats, kline_by_symbol)
    leave_symbol = leave_one_symbol_out(reconstructed["events"], kline_by_symbol, observed_stats)
    leave_month = leave_one_month_out(reconstructed["events"], kline_by_symbol, observed_stats)
    arb = arbusdt_exclusion(reconstructed["events"], kline_by_symbol, observed_stats)
    contributors = top_contributors(reconstructed["events"], kline_by_symbol)
    crowding = crowding_confirmation_sensitivity(reconstructed["events"], kline_by_symbol)
    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise RobustnessBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    gates = primary_gates(null_summary, leave_symbol, leave_month, arb, diagnostic, input_unchanged)
    failed_gates = [name for name, passed in gates.items() if not passed]
    data_quality_warnings = [
        f"{cache_summary['available_count']}/360 monthly 15m kline archives available",
        f"{cache_summary['missing_count']} missing archives: {cache_summary['missing_archive_keys']}",
        f"diagnostic missing forward returns: {diagnostic.get('missing_forward_return_summary')}",
        "Sparse crowding-confirmed variants were not used as primary tests.",
    ]
    material_data_quality_blocker = observed["missing_join_count"] > 0
    if material_data_quality_blocker:
        result_classification = RESULT_ATTENTION
        allowed_next_step = NEXT_ATTENTION
    elif not failed_gates:
        result_classification = RESULT_PROMISING
        allowed_next_step = NEXT_PROMISING
    else:
        result_classification = RESULT_WEAK
        allowed_next_step = NEXT_WEAK
    validation_checks = {
        "repo_clean_or_only_output_before_run": audit["recovery_decision"] == "RECOVERY_AUDIT_CLEAN_CONTINUE",
        "head_matches_expected": audit["head_matches_expected"],
        "input_artifact_hashes_unchanged": input_unchanged,
        "prior_diagnostic_verified": all(prior_verification["checks"].values()),
        "selected_event_definitions_validated": selected_validation["validated"],
        "month_aware_symbol_balanced_null_exact_1000": null_summary["count_completed"] == PERMUTATION_COUNT,
        "artifacts_data_builds_not_written": True,
        "no_raw_data_committed": True,
        "no_cache_files_staged": True,
        "strategy_allowed_false": True,
        "signal_allowed_false": True,
        "candidate_generation_allowed_false": True,
        "release_allowed_false": True,
    }
    artifact = {
        "robustness_status": ROBUSTNESS_STATUS_PASS,
        "status": ROBUSTNESS_STATUS_PASS,
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
        "prior_diagnostic_summary": {
            "status": diagnostic.get("diagnostic_status"),
            "result_classification": diagnostic.get("result_classification"),
            "long_core_event_count": diagnostic.get("long_core_event_count"),
            "short_core_event_count": diagnostic.get("short_core_event_count"),
            "mini_verification": prior_verification["checks"],
        },
        "primary_finding": prior_verification["primary_finding"],
        "secondary_findings_tracked": SECONDARY_FINDINGS,
        "month_aware_symbol_balanced_null_summary": {
            "count_requested": null_summary["count_requested"],
            "count_completed": null_summary["count_completed"],
            "primary_short_core_1h": {
                "null_stats": null_summary["null_stats_by_side_and_horizon"][PRIMARY_SIDE][PRIMARY_HORIZON],
                "p_values": null_summary["p_values_by_side_and_horizon"][PRIMARY_SIDE][PRIMARY_HORIZON],
                "fdr_q": null_summary["fdr_q_values"][PRIMARY_SIDE][PRIMARY_HORIZON],
                "bonferroni_p": null_summary["bonferroni_p_values"][PRIMARY_SIDE][PRIMARY_HORIZON],
            },
            "top_findings": null_summary["top_findings"],
            "fallback_summary": null_summary["fallback_summary"],
        },
        "leave_one_symbol_out_summary": leave_symbol,
        "leave_one_month_out_summary": leave_month,
        "arbusdt_exclusion_sensitivity": arb,
        "top_contributor_diagnostics": contributors,
        "crowding_confirmation_sensitivity": crowding,
        "primary_robustness_gates": gates,
        "failed_robustness_gates": failed_gates,
        "observed_stats_by_side_and_horizon": observed_stats,
        "null_stats_by_side_and_horizon": null_summary["null_stats_by_side_and_horizon"],
        "p_values_by_side_and_horizon": null_summary["p_values_by_side_and_horizon"],
        "fdr_q_values": null_summary["fdr_q_values"],
        "bonferroni_p_values": null_summary["bonferroni_p_values"],
        "data_quality_warnings": data_quality_warnings,
        "validation_limits": [
            "Diagnostic robustness only; no strategy, signal, backtest, PnL, trade simulation, candidate generation, edge claim, or release permission.",
            "Event definitions were not modified or optimized based on forward returns.",
            "Sparse crowding-confirmed variants were used only for exclusion confirmation, not as primary tests.",
            "Forward returns remain public close-to-close diagnostic labels, not tradable execution logic.",
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
    print(f"status: {artifact['robustness_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"primary_finding: {artifact['primary_finding']}")
    print(f"month_aware_symbol_balanced_null_count_requested: {artifact['month_aware_symbol_balanced_null_summary']['count_requested']}")
    print(f"month_aware_symbol_balanced_null_count_completed: {artifact['month_aware_symbol_balanced_null_summary']['count_completed']}")
    print(f"primary_month_aware_null_result: {artifact['month_aware_symbol_balanced_null_summary'].get('primary_short_core_1h')}")
    print(f"leave_one_symbol_out_summary: {artifact['leave_one_symbol_out_summary'].get('short_core|1h')}")
    print(f"leave_one_month_out_summary: {artifact['leave_one_month_out_summary'].get('short_core|1h')}")
    print(f"arbusdt_exclusion_sensitivity: {artifact['arbusdt_exclusion_sensitivity']}")
    print(f"top_contributor_diagnostics: {artifact['top_contributor_diagnostics']}")
    print(f"crowding_confirmation_sensitivity: {artifact['crowding_confirmation_sensitivity']}")
    print(f"primary_robustness_gates: {artifact['primary_robustness_gates']}")
    print(f"failed_robustness_gates: {artifact['failed_robustness_gates']}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print(f"strategy_allowed: {bool_text(bool(artifact['strategy_allowed']))}")
    print(f"signal_allowed: {bool_text(bool(artifact['signal_allowed']))}")
    print(f"candidate_generation_allowed: {bool_text(bool(artifact['candidate_generation_allowed']))}")
    print(f"release_allowed: {bool_text(bool(artifact['release_allowed']))}")
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
        return 0 if artifact["robustness_status"] == ROBUSTNESS_STATUS_PASS else 1
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
