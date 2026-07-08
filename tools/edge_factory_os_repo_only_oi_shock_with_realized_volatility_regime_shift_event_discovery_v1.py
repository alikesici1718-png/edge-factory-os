#!/usr/bin/env python
"""Outcome-blind OI shock plus realized-volatility regime-shift discovery."""

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
MODULE = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/oi_shock_with_realized_volatility_regime_shift_event_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "fc47217b8d5ee51869147496fde76e382cc707a6"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
SOURCE_PREVIOUS_EVALUATOR_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_evaluator_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
    SOURCE_PREVIOUS_EVALUATOR_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

BASE_DISCOVERY_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.py"

DISCOVERY_STATUS_PASS = "PASS_REPO_ONLY_OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_CREATED"
DISCOVERY_STATUS_BLOCKED = "BLOCKED_OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY"
ARTIFACT_KIND = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY"

RESULT_READY = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_READY"
RESULT_TOO_SPARSE = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_TOO_SPARSE"
RESULT_TOO_BROAD = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_TOO_BROAD"
RESULT_ATTENTION = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_DISCOVERY_FAILED_STOP"

THEORY_ID = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT"
NEXT_VALIDATOR = "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_EVENT_VALIDATOR_V1"
NEXT_BACKLOG = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_V1"

OI_POSITIVE_QUANTILES = [0.95, 0.975, 0.99]
OI_NEGATIVE_QUANTILES = [0.05, 0.025, 0.01]
VOL_LOW_QUANTILES = [0.25, 0.10]
VOL_HIGH_QUANTILES = [0.75, 0.90, 0.95]
REGIME_SHIFT_WINDOWS = ["current1h_vs_prior4h", "current1h_vs_prior24h", "current15m_range_vs_prior4h_median"]
COOLDOWN_HOURS = [6, 12, 24]
EPSILON = 1e-12

EVENT_FAMILIES = {
    "OI_EXPANSION_VOLATILITY_EXPANSION_EVENT": {
        "oi_direction": "expansion",
        "mechanic": "Positive OI shock with prior lower/normal volatility shifting to current high volatility.",
    },
    "OI_CONTRACTION_VOLATILITY_EXPANSION_EVENT": {
        "oi_direction": "contraction",
        "mechanic": "Negative OI shock with prior lower/normal volatility shifting to current high volatility.",
    },
    "OI_EXPANSION_VOLATILITY_COMPRESSION_BREAK_EVENT": {
        "oi_direction": "expansion",
        "mechanic": "Positive OI shock after prior compressed volatility with current range/volatility breakout.",
    },
    "OI_CONTRACTION_POST_STRESS_VOLATILITY_NORMALIZATION_EVENT": {
        "oi_direction": "contraction",
        "mechanic": "Negative OI shock after prior high-volatility stress with current volatility normalization/compression.",
    },
}


class DiscoveryBlocked(Exception):
    pass


def load_base_module() -> Any:
    if not BASE_DISCOVERY_TOOL.exists():
        raise DiscoveryBlocked(f"missing base discovery tool: {BASE_DISCOVERY_TOOL}")
    spec = importlib.util.spec_from_file_location("oi_contraction_discovery_base_for_vol_v1", BASE_DISCOVERY_TOOL)
    if spec is None or spec.loader is None:
        raise DiscoveryBlocked("could not load base discovery tool module spec")
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


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    previous_evaluator = read_json_readonly(SOURCE_PREVIOUS_EVALUATOR_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
        SOURCE_PREVIOUS_EVALUATOR_RELATIVE_PATH: verify_payload_hash(previous_evaluator, "previous route evaluator"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise DiscoveryBlocked("outcome-blind theory queue is not ready")
    if previous_evaluator.get("result_classification") != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_DIAGNOSTIC_EVALUATOR_ROUTE_CLOSED_NO_ROBUST_EFFECT":
        raise DiscoveryBlocked("previous route evaluator did not close the prior route")
    if previous_evaluator.get("route_closed") is not True or previous_evaluator.get("no_robust_effect") is not True:
        raise DiscoveryBlocked("previous route evaluator did not set route_closed/no_robust_effect")
    if previous_evaluator.get("allowed_next_step") != MODULE:
        raise DiscoveryBlocked(f"previous evaluator allowed_next_step is not {MODULE}")
    if previous_evaluator.get("next_theory_selected") != THEORY_ID:
        raise DiscoveryBlocked(f"previous evaluator next theory is not {THEORY_ID}")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiscoveryBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise DiscoveryBlocked("public kline diagnostic status is not PASS")
    return theory_queue, previous_evaluator, dataset, kline, payload_hashes


def percentile_name(q: float) -> str:
    lookup = {
        0.01: "p1.0",
        0.025: "p2.5",
        0.05: "p5.0",
        0.10: "p10.0",
        0.25: "p25.0",
        0.50: "p50.0",
        0.75: "p75.0",
        0.90: "p90.0",
        0.95: "p95.0",
        0.975: "p97.5",
        0.99: "p99.0",
    }
    return lookup.get(q, f"p{q * 100:g}")


def quantile_or_none(values: list[float], q: float) -> float | None:
    clean = np.array([value for value in values if math.isfinite(value)], dtype=np.float64)
    if clean.size == 0:
        return None
    return float(np.quantile(clean, q))


def rolling_mean_current(values: np.ndarray, window: int) -> np.ndarray:
    finite = np.isfinite(values)
    clean = np.where(finite, values, 0.0)
    csum = np.concatenate([[0.0], np.cumsum(clean)])
    ccount = np.concatenate([[0], np.cumsum(finite.astype(np.int64))])
    out = np.full(values.shape, np.nan, dtype=np.float64)
    for idx in range(values.size):
        start = max(0, idx - window + 1)
        total = csum[idx + 1] - csum[start]
        count = ccount[idx + 1] - ccount[start]
        if count > 0:
            out[idx] = total / count
    return out


def rolling_mean_previous(values: np.ndarray, window: int) -> np.ndarray:
    finite = np.isfinite(values)
    clean = np.where(finite, values, 0.0)
    csum = np.concatenate([[0.0], np.cumsum(clean)])
    ccount = np.concatenate([[0], np.cumsum(finite.astype(np.int64))])
    out = np.full(values.shape, np.nan, dtype=np.float64)
    for idx in range(values.size):
        start = max(0, idx - window)
        total = csum[idx] - csum[start]
        count = ccount[idx] - ccount[start]
        if count > 0:
            out[idx] = total / count
    return out


def rolling_median_previous(values: np.ndarray, window: int) -> np.ndarray:
    out = np.full(values.shape, np.nan, dtype=np.float64)
    for idx in range(values.size):
        start = max(0, idx - window)
        segment = values[start:idx]
        segment = segment[np.isfinite(segment)]
        if segment.size > 0:
            out[idx] = float(np.median(segment))
    return out


def kline_feature_pack(kline_data: dict[str, Any], base: Any) -> dict[str, Any]:
    abs_return = np.array(kline_data["abs_return_15m"], dtype=np.float64)
    ranges = np.array(kline_data["range"], dtype=np.float64)
    volumes = np.array(kline_data["volume"], dtype=np.float64)
    current_vol_1h = rolling_mean_current(abs_return, 4)
    prior_vol_4h = rolling_mean_previous(abs_return, 16)
    prior_vol_24h = rolling_mean_previous(abs_return, 96)
    prior_range_median_4h = rolling_median_previous(ranges, 16)
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for idx, open_time in enumerate(kline_data["opens"]):
        month = base.month_key_from_ms(int(open_time))
        if math.isfinite(float(current_vol_1h[idx])):
            buckets[month]["current_vol_1h"].append(float(current_vol_1h[idx]))
        if math.isfinite(float(ranges[idx])):
            buckets[month]["range"].append(float(ranges[idx]))
        if math.isfinite(float(volumes[idx])):
            buckets[month]["volume"].append(float(volumes[idx]))
    thresholds: dict[str, dict[str, dict[str, float | None]]] = {}
    for month, fields in buckets.items():
        thresholds[month] = {
            "current_vol_1h": {
                percentile_name(q): quantile_or_none(fields["current_vol_1h"], q)
                for q in [*VOL_LOW_QUANTILES, *VOL_HIGH_QUANTILES]
            },
            "range": {
                percentile_name(q): quantile_or_none(fields["range"], q)
                for q in [*VOL_LOW_QUANTILES, *VOL_HIGH_QUANTILES]
            },
            "volume": {"p95.0": quantile_or_none(fields["volume"], 0.95)},
        }
    return {
        "current_vol_1h": current_vol_1h,
        "prior_vol_4h": prior_vol_4h,
        "prior_vol_24h": prior_vol_24h,
        "prior_range_median_4h": prior_range_median_4h,
        "thresholds": thresholds,
    }


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
            "oi_positive": {
                percentile_name(q): quantile_or_none(per_field["oi_delta_log_1h"], q) for q in OI_POSITIVE_QUANTILES
            },
            "oi_negative": {
                percentile_name(q): quantile_or_none(per_field["oi_delta_log_1h"], q) for q in OI_NEGATIVE_QUANTILES
            },
            "taker_buy_pressure": {
                "p98.0": quantile_or_none(per_field["taker_buy_pressure"], 0.98),
                "p99.0": quantile_or_none(per_field["taker_buy_pressure"], 0.99),
            },
            "taker_sell_pressure": {
                "p98.0": quantile_or_none(per_field["taker_sell_pressure"], 0.98),
                "p99.0": quantile_or_none(per_field["taker_sell_pressure"], 0.99),
            },
            "long_short_annotations": {
                "top_account_p5.0": quantile_or_none(per_field["top_account_long_short_ratio"], 0.05),
                "top_account_p95.0": quantile_or_none(per_field["top_account_long_short_ratio"], 0.95),
                "top_position_p5.0": quantile_or_none(per_field["top_position_long_short_ratio"], 0.05),
                "top_position_p95.0": quantile_or_none(per_field["top_position_long_short_ratio"], 0.95),
            },
        }
    return thresholds


def build_definition_catalog() -> dict[str, dict[str, Any]]:
    catalog: dict[str, dict[str, Any]] = {}
    for family, family_meta in EVENT_FAMILIES.items():
        oi_quantiles = OI_POSITIVE_QUANTILES if family_meta["oi_direction"] == "expansion" else OI_NEGATIVE_QUANTILES
        for oi_q in oi_quantiles:
            for low_q in VOL_LOW_QUANTILES:
                for high_q in VOL_HIGH_QUANTILES:
                    for window in REGIME_SHIFT_WINDOWS:
                        for cooldown in COOLDOWN_HOURS:
                            meta = {
                                "family": family,
                                "oi_direction": family_meta["oi_direction"],
                                "oi_threshold": percentile_name(oi_q),
                                "vol_low_threshold": percentile_name(low_q),
                                "vol_high_threshold": percentile_name(high_q),
                                "regime_shift_window": window,
                                "cooldown_hours": cooldown,
                                "uses_forward_returns": False,
                                "uses_outcome_optimization": False,
                            }
                            catalog[definition_id(meta)] = meta
    return catalog


def definition_id(meta: dict[str, Any]) -> str:
    return "__".join(
        [
            meta["family"],
            f"oi_{meta['oi_threshold']}",
            f"vol_low_{meta['vol_low_threshold']}",
            f"vol_high_{meta['vol_high_threshold']}",
            f"window_{meta['regime_shift_window']}",
            f"cooldown_{meta['cooldown_hours']}h",
        ]
    )


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
        "rejected_due_to_missing_volatility_regime_count": 0,
        "volatility_regime_distribution": Counter(),
        "oi_shock_direction_distribution": Counter(),
        "optional_annotation_distribution": {
            "taker_pressure_annotation": Counter(),
            "long_short_ratio_annotation": Counter(),
            "volume_stress_annotation": Counter(),
        },
        "_raw_timestamps": set(),
        "_raw_symbol_timestamps": set(),
        "_symbols": Counter(),
        "_months": Counter(),
        "_last_event_ms": {},
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


def taker_pressure_annotation(row: dict[str, Any], thresholds: dict[str, Any]) -> str:
    buy = row.get("taker_buy_pressure")
    sell = row.get("taker_sell_pressure")
    buy_p98 = thresholds.get("taker_buy_pressure", {}).get("p98.0")
    sell_p98 = thresholds.get("taker_sell_pressure", {}).get("p98.0")
    buy_extreme = buy is not None and buy_p98 is not None and buy >= buy_p98
    sell_extreme = sell is not None and sell_p98 is not None and sell >= sell_p98
    if buy_extreme and sell_extreme:
        return "both_buy_and_sell_pressure_extreme"
    if buy_extreme:
        return "buy_pressure_extreme"
    if sell_extreme:
        return "sell_pressure_extreme"
    return "none"


def volume_stress_annotation(row_month: str, feature: dict[str, Any], price_thresholds: dict[str, Any]) -> str:
    threshold = price_thresholds.get(row_month, {}).get("volume", {}).get("p95.0")
    if threshold is None or feature.get("volume") is None:
        return "unknown"
    return "volume_stress_p95_or_higher" if feature["volume"] >= threshold else "not_volume_stress"


def feature_for_row(row: dict[str, Any], kline_data: dict[str, Any], feature_pack: dict[str, Any], base: Any) -> dict[str, Any] | None:
    base_open = base.floor_to_15m_open(row["ts_ms"])
    index = kline_data["open_to_index"].get(base_open)
    if index is None:
        return None
    return {
        "current_vol_1h": float(feature_pack["current_vol_1h"][index]),
        "prior_vol_4h": float(feature_pack["prior_vol_4h"][index]),
        "prior_vol_24h": float(feature_pack["prior_vol_24h"][index]),
        "current_range": float(kline_data["range"][index]),
        "prior_range_median_4h": float(feature_pack["prior_range_median_4h"][index]),
        "volume": float(kline_data["volume"][index]),
        "month_thresholds": feature_pack["thresholds"].get(row["month"], {}),
    }


def threshold_lookup(feature: dict[str, Any], bucket: str, name: str) -> float | None:
    value = feature.get("month_thresholds", {}).get(bucket, {}).get(name)
    if value is None:
        return None
    if not math.isfinite(float(value)):
        return None
    return float(value)


def regime_pass(meta: dict[str, Any], feature: dict[str, Any]) -> tuple[bool, str]:
    low_name = meta["vol_low_threshold"]
    high_name = meta["vol_high_threshold"]
    window = meta["regime_shift_window"]
    low_vol = threshold_lookup(feature, "current_vol_1h", low_name)
    high_vol = threshold_lookup(feature, "current_vol_1h", high_name)
    low_range = threshold_lookup(feature, "range", low_name)
    high_range = threshold_lookup(feature, "range", high_name)
    current_vol = feature["current_vol_1h"]
    prior4 = feature["prior_vol_4h"]
    prior24 = feature["prior_vol_24h"]
    current_range = feature["current_range"]
    prior_range_median = feature["prior_range_median_4h"]
    values = [current_vol, current_range]
    if window == "current1h_vs_prior4h":
        values.append(prior4)
    elif window == "current1h_vs_prior24h":
        values.append(prior24)
    else:
        values.append(prior_range_median)
    if any(not math.isfinite(float(value)) for value in values):
        return False, "missing_volatility_feature"
    family = meta["family"]
    if family in {"OI_EXPANSION_VOLATILITY_EXPANSION_EVENT", "OI_CONTRACTION_VOLATILITY_EXPANSION_EVENT"}:
        if window == "current1h_vs_prior4h":
            passed = low_vol is not None and high_vol is not None and prior4 <= low_vol and current_vol >= high_vol
            return passed, "prior4h_low_to_current1h_high"
        if window == "current1h_vs_prior24h":
            passed = low_vol is not None and high_vol is not None and prior24 <= low_vol and current_vol >= high_vol
            return passed, "prior24h_low_to_current1h_high"
        passed = (
            low_range is not None
            and high_range is not None
            and prior_range_median <= low_range
            and current_range >= high_range
            and current_range / max(prior_range_median, EPSILON) >= 1.5
        )
        return passed, "prior4h_compressed_range_to_current15m_range_break"
    if family == "OI_EXPANSION_VOLATILITY_COMPRESSION_BREAK_EVENT":
        if window == "current15m_range_vs_prior4h_median":
            passed = (
                low_range is not None
                and high_range is not None
                and prior_range_median <= low_range
                and current_range >= high_range
                and current_range / max(prior_range_median, EPSILON) >= 1.5
            )
            return passed, "compressed_range_breakout"
        prior_value = prior4 if window == "current1h_vs_prior4h" else prior24
        label = "prior4h_compressed_vol_to_current1h_break" if window == "current1h_vs_prior4h" else "prior24h_compressed_vol_to_current1h_break"
        passed = low_vol is not None and high_vol is not None and prior_value <= low_vol and current_vol >= high_vol
        return passed, label
    if family == "OI_CONTRACTION_POST_STRESS_VOLATILITY_NORMALIZATION_EVENT":
        if window == "current15m_range_vs_prior4h_median":
            passed = low_range is not None and high_range is not None and prior_range_median >= high_range and current_range <= low_range
            return passed, "prior4h_high_range_to_current15m_low_range"
        prior_value = prior4 if window == "current1h_vs_prior4h" else prior24
        label = "prior4h_high_vol_to_current1h_low" if window == "current1h_vs_prior4h" else "prior24h_high_vol_to_current1h_low"
        passed = low_vol is not None and high_vol is not None and prior_value >= high_vol and current_vol <= low_vol
        return passed, label
    return False, "unknown_family"


def update_summary(summary: dict[str, Any], row: dict[str, Any], meta: dict[str, Any], regime_label: str, annotations: dict[str, str]) -> None:
    summary["raw_event_count"] += 1
    summary["_raw_timestamps"].add(row["timestamp"])
    summary["_raw_symbol_timestamps"].add((row["symbol"], row["timestamp"]))
    summary["volatility_regime_distribution"][regime_label] += 1
    summary["oi_shock_direction_distribution"][meta["oi_direction"]] += 1
    summary["optional_annotation_distribution"]["taker_pressure_annotation"][annotations["taker_pressure_annotation"]] += 1
    summary["optional_annotation_distribution"]["long_short_ratio_annotation"][annotations["long_short_ratio_annotation"]] += 1
    summary["optional_annotation_distribution"]["volume_stress_annotation"][annotations["volume_stress_annotation"]] += 1
    previous = summary["_last_event_ms"].get(row["symbol"])
    cooldown_ms = int(meta["cooldown_hours"]) * 60 * 60 * 1000
    if previous is not None and row["ts_ms"] - previous < cooldown_ms:
        summary["rejected_due_to_cooldown_count"] += 1
        return
    summary["_last_event_ms"][row["symbol"]] = row["ts_ms"]
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
    summary["volatility_regime_distribution"] = dict(summary["volatility_regime_distribution"])
    summary["oi_shock_direction_distribution"] = dict(summary["oi_shock_direction_distribution"])
    summary["optional_annotation_distribution"] = {
        key: dict(value) for key, value in summary["optional_annotation_distribution"].items()
    }
    summary["target_event_count_band"] = classify_count_band(cooldown_count)
    summary["reason_counts"] = {
        "rejected_due_to_cooldown_count": summary["rejected_due_to_cooldown_count"],
        "rejected_due_to_missing_volatility_regime_count": summary["rejected_due_to_missing_volatility_regime_count"],
    }
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
        "reason_counts",
        "volatility_regime_distribution",
        "oi_shock_direction_distribution",
        "optional_annotation_distribution",
        "target_event_count_band",
    ]
    return {field: summary[field] for field in fields}


def score_definition(summary: dict[str, Any]) -> float:
    count = int(summary["cooldown_filtered_count"])
    band_score = {
        "ideal": 1000.0,
        "acceptable_but_possibly_broad": 650.0,
        "sparse_but_potentially_usable": 420.0,
        "too_sparse": -450.0,
        "too_broad": -750.0,
    }[summary["target_event_count_band"]]
    symbol_score = float(summary["symbol_coverage_count"]) * 25.0
    month_score = float(summary["month_coverage_count"]) * 5.0
    count_center_bonus = -abs(count - 700) * 0.06 if count else -125.0
    top_symbol = summary["top_symbol_concentration"]
    top_month = summary["top_month_concentration"]
    concentration_penalty = 0.0
    if top_symbol is not None and top_symbol > 0.25:
        concentration_penalty += 450.0 * (top_symbol - 0.25)
    if top_month is not None and top_month > 0.15:
        concentration_penalty += 300.0 * (top_month - 0.15)
    overlap_penalty = float(summary["overlap_rate"]) * 125.0
    simplicity_bonus = 20.0 if summary["meta"]["regime_shift_window"] != "current1h_vs_prior24h" else 8.0
    return band_score + symbol_score + month_score + count_center_bonus + simplicity_bonus - concentration_penalty - overlap_penalty


def run_symbol_discovery(
    path: Path,
    kline_data: dict[str, Any],
    base: Any,
    catalog: dict[str, dict[str, Any]],
    summaries: dict[str, dict[str, Any]],
    missing_counter: Counter[str],
) -> None:
    rows = base.metric_rows_for_symbol(path)
    metric_thresholds = build_metric_thresholds(rows)
    feature_pack = kline_feature_pack(kline_data, base)
    for row in rows:
        metric_month = metric_thresholds.get(row["month"])
        if metric_month is None:
            missing_counter["metric_threshold_month_missing"] += 1
            continue
        feature = feature_for_row(row, kline_data, feature_pack, base)
        if feature is None:
            missing_counter["price_bar_missing"] += 1
            continue
        oi_delta = row.get("oi_delta_log_1h")
        if oi_delta is None:
            missing_counter["oi_delta_log_1h_missing"] += 1
            continue
        positive_pass = [
            percentile_name(q)
            for q in OI_POSITIVE_QUANTILES
            if metric_month["oi_positive"].get(percentile_name(q)) is not None and oi_delta >= metric_month["oi_positive"][percentile_name(q)]
        ]
        negative_pass = [
            percentile_name(q)
            for q in OI_NEGATIVE_QUANTILES
            if metric_month["oi_negative"].get(percentile_name(q)) is not None and oi_delta <= metric_month["oi_negative"][percentile_name(q)]
        ]
        if not positive_pass and not negative_pass:
            continue
        annotations = {
            "taker_pressure_annotation": taker_pressure_annotation(row, metric_month),
            "long_short_ratio_annotation": long_short_annotation(row, metric_month),
            "volume_stress_annotation": volume_stress_annotation(row["month"], feature, feature_pack["thresholds"]),
        }
        for def_id, meta in catalog.items():
            if meta["oi_direction"] == "expansion" and meta["oi_threshold"] not in positive_pass:
                continue
            if meta["oi_direction"] == "contraction" and meta["oi_threshold"] not in negative_pass:
                continue
            passed, regime_label = regime_pass(meta, feature)
            summary = summaries[def_id]
            if passed:
                update_summary(summary, row, meta, regime_label, annotations)
            elif regime_label == "missing_volatility_feature":
                summary["rejected_due_to_missing_volatility_regime_count"] += 1


def select_definitions(summaries: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], str, str, str]:
    selections: list[dict[str, Any]] = []
    for slot_name, family in [
        ("best_oi_expansion_volatility_expansion_definition", "OI_EXPANSION_VOLATILITY_EXPANSION_EVENT"),
        ("best_oi_contraction_volatility_expansion_definition", "OI_CONTRACTION_VOLATILITY_EXPANSION_EVENT"),
        ("best_oi_expansion_volatility_compression_break_definition", "OI_EXPANSION_VOLATILITY_COMPRESSION_BREAK_EVENT"),
        ("best_oi_contraction_post_stress_volatility_normalization_definition", "OI_CONTRACTION_POST_STRESS_VOLATILITY_NORMALIZATION_EVENT"),
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
        strict_candidates = [
            item
            for item in candidates[1:]
            if item["target_event_count_band"] in {"ideal", "sparse_but_potentially_usable"}
            and item["meta"]["oi_threshold"] in {"p97.5", "p99.0", "p2.5", "p1.0"}
            and item["meta"]["vol_high_threshold"] in {"p90.0", "p95.0"}
        ]
        if strict_candidates:
            strict_candidates.sort(key=score_definition, reverse=True)
            optional = compact_summary(strict_candidates[0])
            optional["selection_slot"] = f"optional_stricter_{slot_name}"
            optional["selection_score"] = score_definition(strict_candidates[0])
            selections.append(optional)
    if not selections:
        return [], "No nonzero OI shock / realized-volatility regime-shift definitions survived current/prior-bar gates.", RESULT_TOO_SPARSE, NEXT_BACKLOG
    bands = [item["target_event_count_band"] for item in selections]
    if any(band in {"ideal", "acceptable_but_possibly_broad", "sparse_but_potentially_usable"} for band in bands):
        return (
            selections[:8],
            "Selected only by outcome-blind event count band, symbol/month coverage, concentration, overlap, missingness, material difference, and simplicity.",
            RESULT_READY,
            NEXT_VALIDATOR,
        )
    if all(band == "too_broad" for band in bands):
        return selections[:8], "All selected volatility-regime definitions are too broad.", RESULT_TOO_BROAD, NEXT_BACKLOG
    return selections[:8], "Selected volatility-regime definitions remain too sparse.", RESULT_TOO_SPARSE, NEXT_BACKLOG


def output_counts(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        def_id: {
            "family": summary["meta"]["family"],
            "raw_event_count": summary["raw_event_count"],
            "cooldown_filtered_count": summary["cooldown_filtered_count"],
            "target_event_count_band": summary["target_event_count_band"],
            "symbol_coverage_count": summary["symbol_coverage_count"],
            "month_coverage_count": summary["month_coverage_count"],
            "reason_counts": summary["reason_counts"],
        }
        for def_id, summary in summaries.items()
    }


def output_by_field(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {def_id: summary[field] for def_id, summary in summaries.items()}


def nested_distribution(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {def_id: summary[field] for def_id, summary in summaries.items() if summary["cooldown_filtered_count"] > 0}


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


def base_artifact(
    head: str | None,
    hashes_before: dict[str, str] | None,
    hashes_after: dict[str, str] | None,
    blocker: str | None,
) -> dict[str, Any]:
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
        "mechanical_rationale": "A large open-interest shock combined with a current/prior realized-volatility regime transition can mark market microstructure stress or position repricing without inspecting future returns.",
        "material_difference_from_failed_routes": "This is a market-state OI shock plus realized-volatility regime route, not the closed OI-contraction/taker-capitulation return route and not the failed broad OI/taker/crowding route; taker and long-short fields are annotations only.",
        "threshold_grid": {
            "oi_expansion_thresholds": [percentile_name(q) for q in OI_POSITIVE_QUANTILES],
            "oi_contraction_thresholds": [percentile_name(q) for q in OI_NEGATIVE_QUANTILES],
            "volatility_low_thresholds": [percentile_name(q) for q in VOL_LOW_QUANTILES],
            "volatility_high_thresholds": [percentile_name(q) for q in VOL_HIGH_QUANTILES],
            "regime_shift_windows": REGIME_SHIFT_WINDOWS,
            "threshold_basis": "symbol-month distributions only; no forward-return, p-value, PnL, hit-rate, Sharpe, or backtest optimization",
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
        "volatility_regime_distribution": {},
        "oi_shock_direction_distribution": {},
        "optional_annotation_distribution": {},
        "target_event_count_interpretation": {
            "ideal": "300 to 1500 cooldown-filtered events",
            "acceptable_but_possibly_broad": "1500 to 5000 cooldown-filtered events",
            "too_broad": "over 5000 cooldown-filtered events",
            "sparse_but_potentially_usable": "100 to 300 cooldown-filtered events",
            "too_sparse": "under 100 cooldown-filtered events",
        },
        "validation_limits": [
            "Event discovery only; no forward returns were computed.",
            "No p-values, null validation, backtest, PnL, signal, candidate, or edge claim was produced.",
            "Volatility features use current/prior 15m bars only.",
            "Taker pressure and long-short ratios are optional annotations, not event gates.",
        ],
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": NEXT_BACKLOG if blocker else None,
        "blocker": blocker,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }


def build_artifact() -> dict[str, Any]:
    head = current_head()
    if head != EXPECTED_HEAD:
        raise DiscoveryBlocked(f"HEAD mismatch: {head} != {EXPECTED_HEAD}")
    if not output_only_status(working_tree_status()):
        raise DiscoveryBlocked(f"unexpected dirty repo state during build: {working_tree_status()}")
    theory_queue, previous_evaluator, dataset, kline, input_payload_hashes = load_inputs()
    base = load_base_module()
    hashes_before = input_artifact_hashes()
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols") or dataset.get("requested_symbols")
    if not isinstance(symbols, list) or not symbols:
        raise DiscoveryBlocked("dataset builder artifact missing built symbol list")
    symbols = [str(symbol) for symbol in symbols]
    archive_summary = base.verify_cached_archives(symbols, kline)
    paths = base.normalized_paths(dataset)
    symbol_to_path = {path.name.split("_", 1)[0]: path for path in paths}
    catalog = build_definition_catalog()
    summaries = {def_id: blank_summary(def_id, meta) for def_id, meta in catalog.items()}
    missing_counter: Counter[str] = Counter()
    kline_quality: dict[str, Any] = {}
    for symbol in symbols:
        path = symbol_to_path.get(symbol)
        if path is None:
            missing_counter[f"{symbol}_normalized_path_missing"] += 1
            continue
        kline_data = base.load_kline_symbol(symbol, archive_summary["archive_records"])
        kline_quality[symbol] = kline_data["quality"]
        run_symbol_discovery(path, kline_data, base, catalog, summaries, missing_counter)
    global_missing_components = int(sum(missing_counter.values()))
    finalized = {def_id: finalize_summary(summary, global_missing_components) for def_id, summary in summaries.items()}
    selected, selection_reason, result_classification, next_step = select_definitions(finalized)
    hashes_after = input_artifact_hashes()
    if hashes_before != hashes_after:
        raise DiscoveryBlocked("input artifact hash changed during build")
    validation_checks = {
        "repo_clean_or_only_outputs_during_run": output_only_status(working_tree_status()),
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_unchanged": hashes_before == hashes_after,
        "previous_route_closed": previous_evaluator.get("route_closed") is True,
        "next_theory_matches": previous_evaluator.get("next_theory_selected") == THEORY_ID,
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
            "source_artifact_summary": {
                "theory_queue_result_classification": theory_queue.get("result_classification"),
                "previous_evaluator_result_classification": previous_evaluator.get("result_classification"),
                "dataset_result_classification": dataset.get("result_classification"),
                "kline_result_classification": kline.get("result_classification"),
            },
            "available_data_source_summary": {
                "symbols": symbols,
                "normalized_metric_files": [str(path) for path in paths],
                "kline_cache_root": str(base.KLINE_CACHE_ROOT),
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
            "volatility_regime_distribution": nested_distribution(finalized, "volatility_regime_distribution"),
            "oi_shock_direction_distribution": nested_distribution(finalized, "oi_shock_direction_distribution"),
            "optional_annotation_distribution": nested_distribution(finalized, "optional_annotation_distribution"),
            "allowed_next_step": next_step,
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


def selected_counts(selected: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        item.get("selection_slot"): {
            "definition_id": item.get("definition_id"),
            "raw_event_count": item.get("raw_event_count"),
            "cooldown_filtered_count": item.get("cooldown_filtered_count"),
            "target_event_count_band": item.get("target_event_count_band"),
        }
        for item in selected
    }


def print_summary(artifact: dict[str, Any]) -> None:
    selected = artifact.get("selected_clean_event_definitions", [])
    counts = selected_counts(selected)
    print(f"status: {artifact['discovery_status']}")
    print(f"result_classification: {artifact['result_classification']}")
    print(f"recovery_audit_status: {artifact['recovery_audit_status']}")
    print(f"input_artifact_hashes_unchanged: {bool_text(bool(artifact['input_artifact_hashes_unchanged']))}")
    print(f"theory_id: {artifact['theory_id']}")
    print(f"material_difference_from_failed_routes: {artifact['material_difference_from_failed_routes']}")
    print(f"selected_clean_event_definitions: {json.dumps(counts, sort_keys=True)}")
    print(f"event_counts_by_definition: {len(artifact.get('event_counts_by_definition', {}))} definitions evaluated")
    print(f"cooldown_filtered_counts: {json.dumps(counts, sort_keys=True)}")
    print(f"symbol_coverage_summary: {json.dumps({item.get('selection_slot'): item.get('symbol_coverage_count') for item in selected}, sort_keys=True)}")
    print(f"month_coverage_summary: {json.dumps({item.get('selection_slot'): item.get('month_coverage_count') for item in selected}, sort_keys=True)}")
    print(f"concentration_summary: {json.dumps({item.get('selection_slot'): {'top_symbol': item.get('top_symbol'), 'top_symbol_concentration': item.get('top_symbol_concentration'), 'top_month': item.get('top_month'), 'top_month_concentration': item.get('top_month_concentration')} for item in selected}, sort_keys=True)}")
    print(f"arbusdt_summary: {json.dumps({item.get('selection_slot'): item.get('arbusdt_count') for item in selected}, sort_keys=True)}")
    print(f"overlap_summary: {json.dumps({item.get('selection_slot'): item.get('overlap_rate') for item in selected}, sort_keys=True)}")
    print(f"missing_data_summary: {json.dumps(artifact.get('missing_data_summary', {}), sort_keys=True)}")
    print(f"volatility_regime_distribution: {json.dumps({item.get('selection_slot'): item.get('volatility_regime_distribution') for item in selected}, sort_keys=True)}")
    print(f"oi_shock_direction_distribution: {json.dumps({item.get('selection_slot'): item.get('oi_shock_direction_distribution') for item in selected}, sort_keys=True)}")
    print(f"optional_annotation_distribution: {json.dumps({item.get('selection_slot'): item.get('optional_annotation_distribution') for item in selected}, sort_keys=True)[:2000]}")
    print(f"allowed_next_step: {artifact['allowed_next_step']}")
    print("candidate_generation: false")
    print("edge_claim: false")
    print("runtime_live_capital: false")
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
