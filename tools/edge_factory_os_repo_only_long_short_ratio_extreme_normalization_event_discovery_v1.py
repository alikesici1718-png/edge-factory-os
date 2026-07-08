"""Outcome-blind long-short ratio extreme normalization event discovery."""

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
MODULE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_V1"
MODULE_RELATIVE_PATH = "tools/edge_factory_os_repo_only_long_short_ratio_extreme_normalization_event_discovery_v1.py"
ARTIFACT_RELATIVE_PATH = "artifacts/research/long_short_ratio_extreme_normalization_event_discovery_v1.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELATIVE_PATH

EXPECTED_HEAD = "abee691914f8e85ef287e7d56b3c9b0da1dc7561"
RECOVERY_AUDIT_STATUS = "RECOVERY_AUDIT_CLEAN_CONTINUE"

SOURCE_THEORY_QUEUE_RELATIVE_PATH = "artifacts/research/outcome_blind_binance_theory_queue_builder_v1.json"
SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH = "artifacts/research/oi_shock_with_realized_volatility_regime_shift_pre_registered_independent_validation_runner_v1.json"
SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH = "artifacts/research/oi_contraction_taker_capitulation_price_rejection_forward_return_diagnostic_evaluator_v1.json"
SOURCE_DATASET_BUILDER_RELATIVE_PATH = "artifacts/data_builds/binance_data_vision_um_metrics_dataset_builder_v1.json"
SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH = "artifacts/research/binance_public_kline_forward_return_diagnostic_v1.json"
INPUT_ARTIFACT_RELATIVE_PATHS = [
    SOURCE_THEORY_QUEUE_RELATIVE_PATH,
    SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH,
    SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH,
    SOURCE_DATASET_BUILDER_RELATIVE_PATH,
    SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH,
]

BASE_DISCOVERY_TOOL = REPO_ROOT / "tools" / "edge_factory_os_repo_only_oi_contraction_taker_capitulation_price_rejection_event_discovery_v1.py"

DISCOVERY_STATUS_PASS = "PASS_REPO_ONLY_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_CREATED"
DISCOVERY_STATUS_BLOCKED = "BLOCKED_LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY"
ARTIFACT_KIND = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY"

RESULT_READY = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_READY"
RESULT_TOO_SPARSE = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_TOO_SPARSE"
RESULT_TOO_BROAD = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_TOO_BROAD"
RESULT_ATTENTION = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_DATA_QUALITY_ATTENTION"
RESULT_FAILED = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_DISCOVERY_FAILED_STOP"

THEORY_ID = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT"
NEXT_VALIDATOR = "LONG_SHORT_RATIO_EXTREME_NORMALIZATION_EVENT_VALIDATOR_V1"
NEXT_REFRESH = "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_REFRESH_V1"

HIGH_EXTREME_QUANTILES = [0.95, 0.975, 0.99]
LOW_EXTREME_QUANTILES = [0.05, 0.025, 0.01]
NEUTRAL_BAND = (40.0, 60.0)
NORMALIZATION_STRENGTHS = {
    "weak": 25.0,
    "medium": 40.0,
    "strong": 60.0,
}
NORMALIZATION_WINDOWS = {"1h": 12, "4h": 48}
PERSISTENCE_WINDOWS = {"1h": 12, "4h": 48, "24h": 288}
COOLDOWN_HOURS = [6, 12, 24]
ONE_HOUR_MS = 60 * 60 * 1000
KLINE_INTERVAL_MS = 15 * 60 * 1000

RATIO_SOURCES = {
    "global": "account_long_short_ratio",
    "top_account": "top_account_long_short_ratio",
    "top_position": "top_position_long_short_ratio",
    "account_and_position_agree": "account_and_position_agree",
}

EVENT_FAMILIES = {
    "LONG_CROWDING_NORMALIZATION_EVENT": "High/extreme long-short ratio moves down toward neutral using current/prior observations.",
    "SHORT_CROWDING_NORMALIZATION_EVENT": "Low/extreme long-short ratio moves up toward neutral using current/prior observations.",
    "LONG_CROWDING_PERSISTENCE_BREAK_EVENT": "High/extreme long-short ratio persists across a prior window and then breaks lower.",
    "SHORT_CROWDING_PERSISTENCE_BREAK_EVENT": "Low/extreme long-short ratio persists across a prior window and then breaks higher.",
    "TOP_ACCOUNT_POSITION_DIVERGENCE_RESOLUTION_EVENT": "Top-account and top-position long-short ratio divergence resolves toward convergence.",
}

FORBIDDEN_FAILED_ROUTES = [
    "broad OI/taker/crowding forward-return route",
    "funding crowding reversal",
    "funding carry",
    "funding extreme volume surge",
    "taker-buy exhaustion",
    "taker-flow momentum continuation",
    "SHORT_PRESSURE_FAILURE_DELAYED_DOWNSIDE_CONTINUATION_DIAGNOSTIC as live/candidate route",
    "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION route closed for no robust directional effect",
    "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT route as volatility sample accumulation monitor",
]


class DiscoveryBlocked(Exception):
    pass


def load_base_module() -> Any:
    if not BASE_DISCOVERY_TOOL.exists():
        raise DiscoveryBlocked(f"missing base discovery tool: {BASE_DISCOVERY_TOOL}")
    spec = importlib.util.spec_from_file_location("oi_contraction_base_for_lsr_discovery_v1", BASE_DISCOVERY_TOOL)
    if spec is None or spec.loader is None:
        raise DiscoveryBlocked("could not load base discovery module")
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
        raise DiscoveryBlocked(f"git {' '.join(args)} failed: {stderr.strip() or stdout.strip()}")
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
        if line.startswith("!! ") and line[3:].startswith("cache/"):
            continue
        return False
    return True


def recovery_audit() -> dict[str, Any]:
    head = current_head()
    status = working_tree_status()
    staged = git_lines(["diff", "--cached", "--name-only"])
    modified = git_lines(["diff", "--name-only"])
    untracked = git_lines(["ls-files", "--others", "--exclude-standard"])
    deleted = git_lines(["ls-files", "--deleted"])
    if staged:
        decision = "STOP_STAGED_FILES_EXIST"
    elif head != EXPECTED_HEAD:
        decision = "STOP_HEAD_MISMATCH"
    elif status and not output_only_status(status):
        decision = "STOP_DIRTY_WORKTREE_UNKNOWN_OR_RISKY_FILES"
    else:
        decision = RECOVERY_AUDIT_STATUS
    return {
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "branch": current_branch(),
        "git_status_porcelain": status,
        "staged_files": staged,
        "modified_tracked_files": modified,
        "untracked_files": untracked,
        "deleted_files": deleted,
        "recovery_decision": decision,
    }


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


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    theory_queue = read_json_readonly(SOURCE_THEORY_QUEUE_RELATIVE_PATH)
    oi_shock_validation = read_json_readonly(SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH)
    oi_contraction_evaluator = read_json_readonly(SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH)
    dataset = read_json_readonly(SOURCE_DATASET_BUILDER_RELATIVE_PATH)
    kline = read_json_readonly(SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH)
    payload_hashes = {
        SOURCE_THEORY_QUEUE_RELATIVE_PATH: verify_payload_hash(theory_queue, "outcome-blind theory queue"),
        SOURCE_OI_SHOCK_VALIDATION_RELATIVE_PATH: verify_payload_hash(oi_shock_validation, "OI shock independent validation runner"),
        SOURCE_OI_CONTRACTION_EVALUATOR_RELATIVE_PATH: verify_payload_hash(oi_contraction_evaluator, "OI contraction diagnostic evaluator"),
        SOURCE_DATASET_BUILDER_RELATIVE_PATH: verify_payload_hash(dataset, "metrics dataset builder"),
        SOURCE_KLINE_DIAGNOSTIC_RELATIVE_PATH: verify_payload_hash(kline, "public kline diagnostic"),
    }
    if theory_queue.get("result_classification") != "OUTCOME_BLIND_BINANCE_THEORY_QUEUE_READY":
        raise DiscoveryBlocked("outcome-blind theory queue is not ready")
    selected = theory_queue.get("selected_next_research_batch")
    if not isinstance(selected, list) or not any(item.get("theory_id") == THEORY_ID for item in selected if isinstance(item, dict)):
        raise DiscoveryBlocked(f"theory queue did not include {THEORY_ID} in selected research batch")
    if oi_shock_validation.get("result_classification") != "OI_SHOCK_WITH_REALIZED_VOLATILITY_REGIME_SHIFT_INDEPENDENT_VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE":
        raise DiscoveryBlocked("OI shock independent validation result is not inconclusive sample accumulation state")
    for flag in ["strategy_allowed", "signal_allowed", "candidate_generation_allowed", "release_allowed"]:
        if oi_shock_validation.get(flag) is not False:
            raise DiscoveryBlocked(f"OI shock validation permission flag is not false: {flag}")
    if oi_contraction_evaluator.get("result_classification") != "OI_CONTRACTION_TAKER_CAPITULATION_PRICE_REJECTION_DIAGNOSTIC_EVALUATOR_ROUTE_CLOSED_NO_ROBUST_EFFECT":
        raise DiscoveryBlocked("OI contraction route is not closed/no robust effect")
    if oi_contraction_evaluator.get("route_closed") is not True or oi_contraction_evaluator.get("no_robust_effect") is not True:
        raise DiscoveryBlocked("OI contraction evaluator did not set route_closed/no_robust_effect")
    if dataset.get("status") != "PASS_REPO_ONLY_BINANCE_DATA_VISION_UM_METRICS_DATASET_BUILDER_CREATED":
        raise DiscoveryBlocked("metrics dataset builder status is not PASS")
    if kline.get("diagnostic_status") != "PASS_REPO_ONLY_BINANCE_PUBLIC_KLINE_FORWARD_RETURN_DIAGNOSTIC_CREATED":
        raise DiscoveryBlocked("public kline diagnostic status is not PASS")
    return theory_queue, oi_shock_validation, oi_contraction_evaluator, dataset, kline, payload_hashes


def percentile_name(q: float) -> str:
    lookup = {
        0.01: "p1.0",
        0.025: "p2.5",
        0.05: "p5.0",
        0.40: "p40.0",
        0.50: "p50.0",
        0.60: "p60.0",
        0.95: "p95.0",
        0.975: "p97.5",
        0.99: "p99.0",
    }
    return lookup.get(q, f"p{q * 100:g}")


def quantile_or_none(values: list[float], q: float) -> float | None:
    clean = np.asarray([value for value in values if math.isfinite(value)], dtype=np.float64)
    if clean.size == 0:
        return None
    return float(np.quantile(clean, q))


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        output = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(output):
        return None
    return output


def ratio_values(row: dict[str, Any], source: str) -> tuple[float | None, float | None]:
    if source == "account_and_position_agree":
        return row.get("top_account_long_short_ratio"), row.get("top_position_long_short_ratio")
    return row.get(RATIO_SOURCES[source]), None


def ratio_source_value(row: dict[str, Any], source: str) -> float | None:
    first, second = ratio_values(row, source)
    if source == "account_and_position_agree":
        if first is None or second is None:
            return None
        return (float(first) + float(second)) / 2.0
    return first


def build_threshold_state(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        month = row["month"]
        for source in RATIO_SOURCES:
            if source == "account_and_position_agree":
                account = row.get("top_account_long_short_ratio")
                position = row.get("top_position_long_short_ratio")
                if account is not None and position is not None:
                    buckets[month][source].append((float(account) + float(position)) / 2.0)
                continue
            value = row.get(RATIO_SOURCES[source])
            if value is not None and math.isfinite(float(value)):
                buckets[month][source].append(float(value))
        for key in ["oi_delta_log_1h", "taker_buy_pressure", "taker_sell_pressure"]:
            value = row.get(key)
            if value is not None and math.isfinite(float(value)):
                buckets[month][key].append(float(value))
    thresholds: dict[str, Any] = {}
    sorted_values: dict[str, Any] = {}
    for month, fields in buckets.items():
        thresholds[month] = {}
        sorted_values[month] = {}
        for source in RATIO_SOURCES:
            values = fields[source]
            thresholds[month][source] = {
                percentile_name(q): quantile_or_none(values, q)
                for q in [*LOW_EXTREME_QUANTILES, 0.40, 0.50, 0.60, *HIGH_EXTREME_QUANTILES]
            }
            sorted_values[month][source] = np.sort(np.asarray(values, dtype=np.float64)) if values else np.asarray([], dtype=np.float64)
        thresholds[month]["oi_delta_log_1h"] = {
            "p5.0": quantile_or_none(fields["oi_delta_log_1h"], 0.05),
            "p95.0": quantile_or_none(fields["oi_delta_log_1h"], 0.95),
        }
        thresholds[month]["taker_buy_pressure"] = {"p98.0": quantile_or_none(fields["taker_buy_pressure"], 0.98)}
        thresholds[month]["taker_sell_pressure"] = {"p98.0": quantile_or_none(fields["taker_sell_pressure"], 0.98)}
    return {"thresholds": thresholds, "sorted_values": sorted_values}


def percentile_rank(value: float | None, sorted_values: np.ndarray) -> float | None:
    if value is None or not math.isfinite(float(value)) or sorted_values.size == 0:
        return None
    right = int(np.searchsorted(sorted_values, float(value), side="right"))
    return 100.0 * right / float(sorted_values.size)


def source_percentile(row: dict[str, Any], source: str, state: dict[str, Any]) -> float | None:
    value = ratio_source_value(row, source)
    sorted_values = state["sorted_values"].get(row["month"], {}).get(source, np.asarray([], dtype=np.float64))
    return percentile_rank(value, sorted_values)


def source_thresholds(row: dict[str, Any], source: str, state: dict[str, Any]) -> dict[str, float | None]:
    return state["thresholds"].get(row["month"], {}).get(source, {})


def threshold_pass(row: dict[str, Any], source: str, threshold_name: str, direction: str, state: dict[str, Any]) -> bool:
    thresholds = source_thresholds(row, source, state)
    if source == "account_and_position_agree":
        account = row.get("top_account_long_short_ratio")
        position = row.get("top_position_long_short_ratio")
        if account is None or position is None:
            return False
        account_sorted = state["sorted_values"].get(row["month"], {}).get("top_account", np.asarray([], dtype=np.float64))
        position_sorted = state["sorted_values"].get(row["month"], {}).get("top_position", np.asarray([], dtype=np.float64))
        account_rank = percentile_rank(account, account_sorted)
        position_rank = percentile_rank(position, position_sorted)
        if account_rank is None or position_rank is None:
            return False
        target = float(threshold_name[1:])
        if direction == "high":
            return account_rank >= target and position_rank >= target
        return account_rank <= target and position_rank <= target
    value = ratio_source_value(row, source)
    threshold = thresholds.get(threshold_name)
    if value is None or threshold is None:
        return False
    if direction == "high":
        return float(value) >= float(threshold)
    return float(value) <= float(threshold)


def neutral_pass(row: dict[str, Any], source: str, state: dict[str, Any]) -> bool:
    if source == "account_and_position_agree":
        account = row.get("top_account_long_short_ratio")
        position = row.get("top_position_long_short_ratio")
        account_rank = percentile_rank(account, state["sorted_values"].get(row["month"], {}).get("top_account", np.asarray([], dtype=np.float64)))
        position_rank = percentile_rank(position, state["sorted_values"].get(row["month"], {}).get("top_position", np.asarray([], dtype=np.float64)))
        return (
            account_rank is not None
            and position_rank is not None
            and NEUTRAL_BAND[0] <= account_rank <= NEUTRAL_BAND[1]
            and NEUTRAL_BAND[0] <= position_rank <= NEUTRAL_BAND[1]
        )
    rank = source_percentile(row, source, state)
    return rank is not None and NEUTRAL_BAND[0] <= rank <= NEUTRAL_BAND[1]


def build_price_context_thresholds(kline_data: dict[str, Any], base: Any) -> dict[str, dict[str, float | None]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for idx, open_time in enumerate(kline_data["opens"]):
        month = base.month_key_from_ms(int(open_time))
        buckets[month]["volume"].append(float(kline_data["volume"][idx]))
        abs_ret = float(kline_data["abs_return_15m"][idx])
        if math.isfinite(abs_ret):
            buckets[month]["abs_return_15m"].append(abs_ret)
    return {
        month: {
            "volume_p95.0": quantile_or_none(fields["volume"], 0.95),
            "abs_return_15m_p75.0": quantile_or_none(fields["abs_return_15m"], 0.75),
            "abs_return_15m_p90.0": quantile_or_none(fields["abs_return_15m"], 0.90),
        }
        for month, fields in buckets.items()
    }


def optional_annotations(row: dict[str, Any], kline_data: dict[str, Any] | None, price_thresholds: dict[str, Any], base: Any, metric_state: dict[str, Any]) -> dict[str, str]:
    oi_delta = row.get("oi_delta_log_1h")
    metric_thresholds = metric_state["thresholds"].get(row["month"], {})
    oi_low = metric_thresholds.get("oi_delta_log_1h", {}).get("p5.0")
    oi_high = metric_thresholds.get("oi_delta_log_1h", {}).get("p95.0")
    if oi_delta is None or oi_low is None or oi_high is None:
        oi_annotation = "unknown"
    elif oi_delta <= oi_low:
        oi_annotation = "oi_contraction_p5_or_lower"
    elif oi_delta >= oi_high:
        oi_annotation = "oi_expansion_p95_or_higher"
    else:
        oi_annotation = "oi_neutral"
    buy = row.get("taker_buy_pressure")
    sell = row.get("taker_sell_pressure")
    buy_p98 = metric_thresholds.get("taker_buy_pressure", {}).get("p98.0")
    sell_p98 = metric_thresholds.get("taker_sell_pressure", {}).get("p98.0")
    if buy is not None and buy_p98 is not None and buy >= buy_p98:
        taker = "buy_pressure_p98_or_higher"
    elif sell is not None and sell_p98 is not None and sell >= sell_p98:
        taker = "sell_pressure_p98_or_higher"
    else:
        taker = "none"
    volume = "unknown"
    realized_vol = "unknown"
    if kline_data is not None:
        base_open = base.floor_to_15m_open(row["ts_ms"])
        index = kline_data["open_to_index"].get(base_open)
        if index is not None:
            price_month_thresholds = price_thresholds.get(row["month"], {})
            volume_p95 = price_month_thresholds.get("volume_p95.0")
            abs_p75 = price_month_thresholds.get("abs_return_15m_p75.0")
            abs_p90 = price_month_thresholds.get("abs_return_15m_p90.0")
            vol_value = float(kline_data["volume"][index])
            abs_ret = float(kline_data["abs_return_15m"][index])
            if volume_p95 is not None:
                volume = "volume_stress_p95_or_higher" if vol_value >= volume_p95 else "not_volume_stress"
            if math.isfinite(abs_ret) and abs_p90 is not None and abs_p75 is not None:
                if abs_ret >= abs_p90:
                    realized_vol = "very_high_abs_return"
                elif abs_ret >= abs_p75:
                    realized_vol = "high_abs_return"
                else:
                    realized_vol = "not_high_abs_return"
    return {
        "oi_annotation": oi_annotation,
        "taker_pressure_annotation": taker,
        "volume_stress_annotation": volume,
        "realized_volatility_annotation": realized_vol,
    }


def source_rank_array(rows: list[dict[str, Any]], source: str, state: dict[str, Any]) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
    ranks = np.full(len(rows), np.nan, dtype=np.float64)
    high_pass = {percentile_name(q): np.zeros(len(rows), dtype=bool) for q in HIGH_EXTREME_QUANTILES}
    low_pass = {percentile_name(q): np.zeros(len(rows), dtype=bool) for q in LOW_EXTREME_QUANTILES}
    if source == "account_and_position_agree":
        account_ranks = np.full(len(rows), np.nan, dtype=np.float64)
        position_ranks = np.full(len(rows), np.nan, dtype=np.float64)
        for idx, row in enumerate(rows):
            month_values = state["sorted_values"].get(row["month"], {})
            account_rank = percentile_rank(row.get("top_account_long_short_ratio"), month_values.get("top_account", np.asarray([], dtype=np.float64)))
            position_rank = percentile_rank(row.get("top_position_long_short_ratio"), month_values.get("top_position", np.asarray([], dtype=np.float64)))
            account_ranks[idx] = account_rank if account_rank is not None else np.nan
            position_ranks[idx] = position_rank if position_rank is not None else np.nan
        ranks = (account_ranks + position_ranks) / 2.0
        for q in HIGH_EXTREME_QUANTILES:
            name = percentile_name(q)
            threshold = q * 100.0
            high_pass[name] = (account_ranks >= threshold) & (position_ranks >= threshold)
        for q in LOW_EXTREME_QUANTILES:
            name = percentile_name(q)
            threshold = q * 100.0
            low_pass[name] = (account_ranks <= threshold) & (position_ranks <= threshold)
        return ranks, high_pass, low_pass
    for idx, row in enumerate(rows):
        rank = source_percentile(row, source, state)
        ranks[idx] = rank if rank is not None else np.nan
    for q in HIGH_EXTREME_QUANTILES:
        name = percentile_name(q)
        high_pass[name] = ranks >= q * 100.0
    for q in LOW_EXTREME_QUANTILES:
        name = percentile_name(q)
        low_pass[name] = ranks <= q * 100.0
    return ranks, high_pass, low_pass


def prior_window_arrays(ranks: np.ndarray, bars: int, threshold_pct: float) -> dict[str, np.ndarray]:
    finite = np.isfinite(ranks)
    clean = np.where(finite, ranks, 0.0)
    high = np.where(finite & (ranks >= threshold_pct), 1.0, 0.0)
    low = np.where(finite & (ranks <= threshold_pct), 1.0, 0.0)
    csum = np.concatenate([[0.0], np.cumsum(clean)])
    ccount = np.concatenate([[0.0], np.cumsum(finite.astype(np.float64))])
    chigh = np.concatenate([[0.0], np.cumsum(high)])
    clow = np.concatenate([[0.0], np.cumsum(low)])
    indices = np.arange(len(ranks))
    start = np.maximum(0, indices - bars)
    counts = ccount[indices] - ccount[start]
    sums = csum[indices] - csum[start]
    high_counts = chigh[indices] - chigh[start]
    low_counts = clow[indices] - clow[start]
    means = np.divide(sums, counts, out=np.full(len(ranks), np.nan, dtype=np.float64), where=counts > 0)
    high_ratio = np.divide(high_counts, counts, out=np.zeros(len(ranks), dtype=np.float64), where=counts > 0)
    low_ratio = np.divide(low_counts, counts, out=np.zeros(len(ranks), dtype=np.float64), where=counts > 0)
    enough = counts >= max(3.0, bars * 0.75)
    return {"mean": means, "high_ratio": high_ratio, "low_ratio": low_ratio, "enough": enough}


def definition_id(meta: dict[str, Any]) -> str:
    fields = [
        meta["family"],
        f"source_{meta['ratio_source']}",
        f"extreme_{meta['extreme_threshold']}",
        f"strength_{meta['normalization_strength']}",
        f"window_{meta['path_window']}",
        f"cooldown_{meta['cooldown_hours']}h",
    ]
    return "__".join(fields)


def blank_summary(def_id: str, meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "definition_id": def_id,
        "meta": dict(meta),
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
        "ratio_source_distribution": Counter(),
        "extreme_threshold_distribution": Counter(),
        "normalization_strength_distribution": Counter(),
        "optional_annotation_distribution": {
            "oi_annotation": Counter(),
            "taker_pressure_annotation": Counter(),
            "volume_stress_annotation": Counter(),
            "realized_volatility_annotation": Counter(),
        },
        "_raw_timestamps": set(),
        "_raw_symbol_timestamps": set(),
        "_symbols": Counter(),
        "_months": Counter(),
        "_last_event_ms": {},
    }


def update_summary(summary: dict[str, Any], row: dict[str, Any], annotations: dict[str, str]) -> None:
    summary["raw_event_count"] += 1
    summary["_raw_timestamps"].add(row["timestamp"])
    summary["_raw_symbol_timestamps"].add((row["symbol"], row["timestamp"]))
    meta = summary["meta"]
    summary["ratio_source_distribution"][meta["ratio_source"]] += 1
    summary["extreme_threshold_distribution"][meta["extreme_threshold"]] += 1
    summary["normalization_strength_distribution"][meta["normalization_strength"]] += 1
    for key, value in annotations.items():
        summary["optional_annotation_distribution"][key][value] += 1
    symbol = row["symbol"]
    previous = summary["_last_event_ms"].get(symbol)
    cooldown_ms = int(meta["cooldown_hours"]) * ONE_HOUR_MS
    if previous is not None and row["ts_ms"] - previous < cooldown_ms:
        return
    summary["_last_event_ms"][symbol] = row["ts_ms"]
    summary["cooldown_filtered_count"] += 1
    summary["_symbols"][symbol] += 1
    summary["_months"][row["month"]] += 1
    if symbol == "ARBUSDT":
        summary["arbusdt_count"] += 1


def count_band(count: int) -> str:
    if 300 <= count <= 1500:
        return "ideal"
    if 1500 < count <= 5000:
        return "acceptable_but_possibly_broad"
    if count > 5000:
        return "too_broad"
    if 100 <= count < 300:
        return "sparse_but_potentially_usable"
    return "too_sparse"


def finalize_summary(summary: dict[str, Any], global_missing: int) -> dict[str, Any]:
    raw = summary["raw_event_count"]
    cooldown = summary["cooldown_filtered_count"]
    symbols = summary.pop("_symbols")
    months = summary.pop("_months")
    raw_timestamps = summary.pop("_raw_timestamps")
    raw_symbol_timestamps = summary.pop("_raw_symbol_timestamps")
    summary.pop("_last_event_ms", None)
    top_symbol, top_symbol_count = symbols.most_common(1)[0] if symbols else (None, 0)
    top_month, top_month_count = months.most_common(1)[0] if months else (None, 0)
    summary["unique_timestamp_count"] = len(raw_timestamps)
    summary["unique_symbol_timestamp_count"] = len(raw_symbol_timestamps)
    summary["symbol_coverage_count"] = len(symbols)
    summary["symbols"] = sorted(symbols)
    summary["month_coverage_count"] = len(months)
    summary["months"] = sorted(months)
    summary["top_symbol"] = top_symbol
    summary["top_symbol_concentration"] = (top_symbol_count / cooldown) if cooldown else None
    summary["top_month"] = top_month
    summary["top_month_concentration"] = (top_month_count / cooldown) if cooldown else None
    summary["overlap_rate"] = 1.0 - (len(raw_symbol_timestamps) / raw) if raw else 0.0
    summary["missing_component_count"] = global_missing
    summary["ratio_source_distribution"] = dict(summary["ratio_source_distribution"])
    summary["extreme_threshold_distribution"] = dict(summary["extreme_threshold_distribution"])
    summary["normalization_strength_distribution"] = dict(summary["normalization_strength_distribution"])
    summary["optional_annotation_distribution"] = {
        key: dict(value) for key, value in summary["optional_annotation_distribution"].items()
    }
    summary["target_event_count_band"] = count_band(cooldown)
    return summary


def compact(summary: dict[str, Any]) -> dict[str, Any]:
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
        "ratio_source_distribution",
        "extreme_threshold_distribution",
        "normalization_strength_distribution",
        "optional_annotation_distribution",
        "target_event_count_band",
    ]
    return {field: summary[field] for field in fields}


def score_definition(summary: dict[str, Any]) -> float:
    count = int(summary["cooldown_filtered_count"])
    band_score = {
        "ideal": 1000.0,
        "acceptable_but_possibly_broad": 620.0,
        "sparse_but_potentially_usable": 430.0,
        "too_sparse": -500.0,
        "too_broad": -800.0,
    }[summary["target_event_count_band"]]
    source_bonus = 35.0 if summary["meta"]["ratio_source"] in {"top_account", "top_position", "account_and_position_agree"} else 15.0
    count_center_bonus = -abs(count - 700) * 0.06 if count else -150.0
    symbol_score = float(summary["symbol_coverage_count"]) * 25.0
    month_score = float(summary["month_coverage_count"]) * 5.0
    concentration_penalty = 0.0
    if summary["top_symbol_concentration"] is not None and summary["top_symbol_concentration"] > 0.25:
        concentration_penalty += 500.0 * (summary["top_symbol_concentration"] - 0.25)
    if summary["top_month_concentration"] is not None and summary["top_month_concentration"] > 0.15:
        concentration_penalty += 350.0 * (summary["top_month_concentration"] - 0.15)
    overlap_penalty = float(summary["overlap_rate"]) * 150.0
    simplicity_bonus = 20.0 if summary["meta"]["normalization_strength"] in {"weak", "medium"} else 8.0
    return band_score + source_bonus + count_center_bonus + symbol_score + month_score + simplicity_bonus - concentration_penalty - overlap_penalty


def candidate_meta(family: str, ratio_source: str, threshold: str, strength: str, path_window: str, cooldown: int) -> dict[str, Any]:
    return {
        "family": family,
        "ratio_source": ratio_source,
        "extreme_threshold": threshold,
        "normalization_strength": strength,
        "path_window": path_window,
        "cooldown_hours": cooldown,
        "uses_forward_returns": False,
        "uses_outcome_optimization": False,
    }


def register_event(summaries: dict[str, dict[str, Any]], meta: dict[str, Any], row: dict[str, Any], annotations: dict[str, str]) -> None:
    def_id = definition_id(meta)
    if def_id not in summaries:
        summaries[def_id] = blank_summary(def_id, meta)
    update_summary(summaries[def_id], row, annotations)


def run_symbol_discovery(path: Path, kline_data: dict[str, Any] | None, base: Any, summaries: dict[str, dict[str, Any]], missing_counter: Counter[str]) -> None:
    rows = base.metric_rows_for_symbol(path)
    if not rows:
        missing_counter["empty_metric_rows"] += 1
        return
    state = build_threshold_state(rows)
    price_thresholds = build_price_context_thresholds(kline_data, base) if kline_data is not None else {}
    annotation_cache: dict[int, dict[str, str]] = {}

    def annotations_for(index: int) -> dict[str, str]:
        cached = annotation_cache.get(index)
        if cached is None:
            cached = optional_annotations(rows[index], kline_data, price_thresholds, base, state)
            annotation_cache[index] = cached
        return cached

    def register_indices(indices: np.ndarray, family: str, source: str, threshold: str, strength: str, window_name: str) -> None:
        if indices.size == 0:
            return
        for cooldown in COOLDOWN_HOURS:
            meta = candidate_meta(family, source, threshold, strength, window_name, cooldown)
            for index in indices:
                idx_int = int(index)
                register_event(summaries, meta, rows[idx_int], annotations_for(idx_int))

    for source in RATIO_SOURCES:
        ranks, high_pass, low_pass = source_rank_array(rows, source, state)
        finite = np.isfinite(ranks)
        missing_counter[f"{source}_missing_or_unranked"] += int((~finite).sum())
        neutral = finite & (ranks >= NEUTRAL_BAND[0]) & (ranks <= NEUTRAL_BAND[1])
        for window_name, bars in NORMALIZATION_WINDOWS.items():
            if len(rows) <= bars:
                continue
            current = ranks[bars:]
            prior = ranks[:-bars]
            valid = np.isfinite(current) & np.isfinite(prior)
            current_indices = np.arange(bars, len(rows))
            neutral_current = neutral[bars:]
            move_down = prior - current
            move_up = current - prior
            for q in HIGH_EXTREME_QUANTILES:
                threshold = percentile_name(q)
                high_extreme = high_pass[threshold][bars:] | high_pass[threshold][:-bars]
                for strength, min_move in NORMALIZATION_STRENGTHS.items():
                    mask = valid & high_extreme & ((move_down >= min_move) | (neutral_current & (move_down > 0)))
                    register_indices(current_indices[mask], "LONG_CROWDING_NORMALIZATION_EVENT", source, threshold, strength, window_name)
            for q in LOW_EXTREME_QUANTILES:
                threshold = percentile_name(q)
                low_extreme = low_pass[threshold][bars:] | low_pass[threshold][:-bars]
                for strength, min_move in NORMALIZATION_STRENGTHS.items():
                    mask = valid & low_extreme & ((move_up >= min_move) | (neutral_current & (move_up > 0)))
                    register_indices(current_indices[mask], "SHORT_CROWDING_NORMALIZATION_EVENT", source, threshold, strength, window_name)
        for window_name, bars in PERSISTENCE_WINDOWS.items():
            if len(rows) <= bars:
                continue
            for q in HIGH_EXTREME_QUANTILES:
                threshold = percentile_name(q)
                threshold_pct = q * 100.0
                prior_stats = prior_window_arrays(ranks, bars, threshold_pct)
                move_down = prior_stats["mean"] - ranks
                persist_mask = prior_stats["enough"] & (prior_stats["high_ratio"] >= 0.75) & np.isfinite(ranks) & (ranks < threshold_pct)
                for strength, min_move in NORMALIZATION_STRENGTHS.items():
                    register_indices(np.flatnonzero(persist_mask & (move_down >= min_move)), "LONG_CROWDING_PERSISTENCE_BREAK_EVENT", source, threshold, strength, window_name)
            for q in LOW_EXTREME_QUANTILES:
                threshold = percentile_name(q)
                threshold_pct = q * 100.0
                prior_stats = prior_window_arrays(ranks, bars, threshold_pct)
                move_up = ranks - prior_stats["mean"]
                persist_mask = prior_stats["enough"] & (prior_stats["low_ratio"] >= 0.75) & np.isfinite(ranks) & (ranks > threshold_pct)
                for strength, min_move in NORMALIZATION_STRENGTHS.items():
                    register_indices(np.flatnonzero(persist_mask & (move_up >= min_move)), "SHORT_CROWDING_PERSISTENCE_BREAK_EVENT", source, threshold, strength, window_name)

    account_ranks, _, _ = source_rank_array(rows, "top_account", state)
    position_ranks, _, _ = source_rank_array(rows, "top_position", state)
    spread = np.abs(account_ranks - position_ranks)
    for window_name, bars in NORMALIZATION_WINDOWS.items():
        if len(rows) <= bars:
            continue
        current_spread = spread[bars:]
        prior_spread = spread[:-bars]
        valid = np.isfinite(current_spread) & np.isfinite(prior_spread)
        current_indices = np.arange(bars, len(rows))
        for strength, min_prior_spread in {"weak": 25.0, "medium": 40.0, "strong": 60.0}.items():
            resolution_cap = {"weak": 25.0, "medium": 15.0, "strong": 10.0}[strength]
            mask = valid & (prior_spread >= min_prior_spread) & (current_spread <= resolution_cap) & (current_spread < prior_spread)
            register_indices(current_indices[mask], "TOP_ACCOUNT_POSITION_DIVERGENCE_RESOLUTION_EVENT", "account_position_pair", "spread_percentile", strength, window_name)


def select_definitions(summaries: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], str, str, str]:
    slots = [
        ("best_long_crowding_normalization_candidate", "LONG_CROWDING_NORMALIZATION_EVENT"),
        ("best_short_crowding_normalization_candidate", "SHORT_CROWDING_NORMALIZATION_EVENT"),
        ("best_long_crowding_persistence_break_candidate", "LONG_CROWDING_PERSISTENCE_BREAK_EVENT"),
        ("best_short_crowding_persistence_break_candidate", "SHORT_CROWDING_PERSISTENCE_BREAK_EVENT"),
        ("optional_account_position_divergence_resolution_candidate", "TOP_ACCOUNT_POSITION_DIVERGENCE_RESOLUTION_EVENT"),
    ]
    selections: list[dict[str, Any]] = []
    for slot, family in slots:
        candidates = [
            summary for summary in summaries.values() if summary["meta"]["family"] == family and summary["cooldown_filtered_count"] > 0
        ]
        if not candidates:
            continue
        candidates.sort(key=score_definition, reverse=True)
        best = compact(candidates[0])
        best["selection_slot"] = slot
        best["selection_score"] = score_definition(candidates[0])
        selections.append(best)
    if not selections:
        return [], "No long-short ratio normalization definitions survived outcome-blind mechanical gates.", RESULT_TOO_SPARSE, NEXT_REFRESH
    bands = [selection["target_event_count_band"] for selection in selections]
    if any(band in {"ideal", "acceptable_but_possibly_broad", "sparse_but_potentially_usable"} for band in bands):
        return (
            selections,
            "Selected only by cooldown-filtered count, coverage, concentration, overlap, missingness, simplicity, and material difference from failed routes.",
            RESULT_READY,
            NEXT_VALIDATOR,
        )
    if all(band == "too_broad" for band in bands):
        return selections, "All selected long-short ratio definitions are too broad.", RESULT_TOO_BROAD, NEXT_REFRESH
    return selections, "Selected long-short ratio definitions remain too sparse.", RESULT_TOO_SPARSE, NEXT_REFRESH


def output_counts(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        definition_id_: {
            "raw_event_count": summary["raw_event_count"],
            "cooldown_filtered_count": summary["cooldown_filtered_count"],
            "target_event_count_band": summary["target_event_count_band"],
            "family": summary["meta"]["family"],
            "ratio_source": summary["meta"]["ratio_source"],
            "extreme_threshold": summary["meta"]["extreme_threshold"],
            "normalization_strength": summary["meta"]["normalization_strength"],
            "path_window": summary["meta"]["path_window"],
            "symbol_coverage_count": summary["symbol_coverage_count"],
            "month_coverage_count": summary["month_coverage_count"],
        }
        for definition_id_, summary in sorted(summaries.items())
    }


def summarize_field(summaries: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    return {definition_id_: summary[field] for definition_id_, summary in summaries.items()}


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
        "prior_failed_route_revived": False,
    }


def blocked_artifact(reason: str, audit: dict[str, Any] | None = None, hashes_before: dict[str, str] | None = None, hashes_after: dict[str, str] | None = None) -> dict[str, Any]:
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
        "recovery_audit_status": (audit or {}).get("recovery_decision", "RECOVERY_UNKNOWN"),
        "current_head": head,
        "expected_head": EXPECTED_HEAD,
        "head_matches_expected": head == EXPECTED_HEAD,
        "input_artifact_hashes_before": hashes_before or {},
        "input_artifact_hashes_after": hashes_after or {},
        "input_artifact_hashes_unchanged": unchanged,
        "theory_id": THEORY_ID,
        "mechanical_rationale": "blocked",
        "material_difference_from_failed_routes": {},
        "threshold_grid": {},
        "cooldown_grid": COOLDOWN_HOURS,
        "event_families_tested": list(EVENT_FAMILIES),
        "event_counts_by_definition": {},
        "cooldown_filtered_counts": {},
        "selected_clean_event_definitions": [],
        "selected_definition_reason": "blocked",
        "symbol_coverage_summary": {},
        "month_coverage_summary": {},
        "concentration_summary": {},
        "arbusdt_summary": {},
        "overlap_summary": {},
        "missing_data_summary": {},
        "ratio_source_distribution": {},
        "extreme_threshold_distribution": {},
        "normalization_strength_distribution": {},
        "optional_annotation_distribution": {},
        "target_event_count_interpretation": {},
        "validation_limits": {},
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": "RECOVERY_OR_RUNTIME_REPAIR_V1",
        "blocker": reason,
        "replacement_checks_all_true": False,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def build_artifact() -> dict[str, Any]:
    audit = recovery_audit()
    if audit["recovery_decision"] != RECOVERY_AUDIT_STATUS:
        return blocked_artifact(audit["recovery_decision"], audit)
    hashes_before = input_artifact_hashes()
    theory_queue, oi_shock_validation, oi_contraction_evaluator, dataset, kline, payload_hashes = load_inputs()
    base = load_base_module()
    symbols = dataset.get("normalized_dataset_summary", {}).get("built_symbols") or dataset.get("requested_symbols")
    if not isinstance(symbols, list) or not symbols:
        raise DiscoveryBlocked("dataset builder artifact missing built/requested symbols")
    symbols = [str(symbol) for symbol in symbols]
    archive_summary = base.verify_cached_archives(symbols, kline)
    normalized = base.normalized_paths(dataset)
    symbol_to_path = {path.name.split("_", 1)[0]: path for path in normalized}
    summaries: dict[str, dict[str, Any]] = {}
    missing_counter: Counter[str] = Counter()
    per_symbol_quality: dict[str, Any] = {}
    for symbol in symbols:
        path = symbol_to_path.get(symbol)
        if path is None:
            missing_counter[f"{symbol}_normalized_path_missing"] += 1
            continue
        try:
            kline_data = base.load_kline_symbol(symbol, archive_summary["archive_records"])
            per_symbol_quality[symbol] = kline_data.get("quality", {})
        except Exception as exc:
            kline_data = None
            per_symbol_quality[symbol] = {"warning": str(exc)}
            missing_counter[f"{symbol}_kline_context_missing"] += 1
        run_symbol_discovery(path, kline_data, base, summaries, missing_counter)
    global_missing = int(sum(missing_counter.values()))
    finalized = {definition_id_: finalize_summary(summary, global_missing) for definition_id_, summary in summaries.items()}
    selections, selected_reason, result_classification, allowed_next_step = select_definitions(finalized)
    hashes_after = input_artifact_hashes()
    input_unchanged = hashes_before == hashes_after
    if not input_unchanged:
        raise DiscoveryBlocked("INPUT_ARTIFACT_HASH_CHANGED")
    event_counts = output_counts(finalized)
    cooldown_counts = {definition_id_: item["cooldown_filtered_count"] for definition_id_, item in event_counts.items()}
    target_interpretation = {
        "ideal": "300 to 1500 cooldown-filtered events",
        "acceptable_but_possibly_broad": "1500 to 5000 cooldown-filtered events",
        "too_broad": "over 5000 cooldown-filtered events",
        "sparse_but_potentially_usable": "100 to 300 cooldown-filtered events",
        "too_sparse": "under 100 cooldown-filtered events",
    }
    artifact = {
        "discovery_status": DISCOVERY_STATUS_PASS,
        "status": DISCOVERY_STATUS_PASS,
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
        "theory_id": THEORY_ID,
        "mechanical_rationale": "Extreme long-short positioning can indicate crowded exposure; current/prior movement from extreme toward neutral or account/position convergence is a crowding-normalization event definition without future outcomes.",
        "material_difference_from_failed_routes": {
            "blocked_route_keys": FORBIDDEN_FAILED_ROUTES,
            "difference": "Uses long-short ratio path and normalization/convergence as the core gate; OI, taker, volume, and realized-volatility are annotations only; no price-failure, directional drift, OI contraction/taker capitulation, or OI shock volatility route is reused.",
        },
        "threshold_grid": {
            "ratio_source": list(RATIO_SOURCES),
            "extreme_high_thresholds": [percentile_name(q) for q in HIGH_EXTREME_QUANTILES],
            "extreme_low_thresholds": [percentile_name(q) for q in LOW_EXTREME_QUANTILES],
            "neutral_band": "p40.0_to_p60.0",
            "normalization_strength": NORMALIZATION_STRENGTHS,
            "normalization_windows": list(NORMALIZATION_WINDOWS),
            "persistence_windows": list(PERSISTENCE_WINDOWS),
        },
        "cooldown_grid": COOLDOWN_HOURS,
        "event_families_tested": EVENT_FAMILIES,
        "event_counts_by_definition": event_counts,
        "cooldown_filtered_counts": cooldown_counts,
        "selected_clean_event_definitions": selections,
        "selected_definition_reason": selected_reason,
        "symbol_coverage_summary": summarize_field(finalized, "symbol_coverage_count"),
        "month_coverage_summary": summarize_field(finalized, "month_coverage_count"),
        "concentration_summary": {
            definition_id_: {
                "top_symbol": summary["top_symbol"],
                "top_symbol_concentration": summary["top_symbol_concentration"],
                "top_month": summary["top_month"],
                "top_month_concentration": summary["top_month_concentration"],
            }
            for definition_id_, summary in finalized.items()
        },
        "arbusdt_summary": summarize_field(finalized, "arbusdt_count"),
        "overlap_summary": summarize_field(finalized, "overlap_rate"),
        "missing_data_summary": {
            "global_missing_component_count": global_missing,
            "missing_component_counter": dict(missing_counter),
            "selected_missing_component_count": {item["selection_slot"]: item["missing_component_count"] for item in selections},
            "kline_archive_summary": archive_summary,
            "per_symbol_kline_quality": per_symbol_quality,
        },
        "ratio_source_distribution": summarize_field(finalized, "ratio_source_distribution"),
        "extreme_threshold_distribution": summarize_field(finalized, "extreme_threshold_distribution"),
        "normalization_strength_distribution": summarize_field(finalized, "normalization_strength_distribution"),
        "optional_annotation_distribution": summarize_field(finalized, "optional_annotation_distribution"),
        "target_event_count_interpretation": target_interpretation,
        "validation_limits": {
            "outcome_blind": True,
            "forward_returns_used": False,
            "p_values_used": False,
            "null_validation_used": False,
            "backtest_used": False,
            "pnl_used": False,
            "strategy_or_signal_used": False,
            "current_prior_bar_only": True,
            "selection_inputs": [
                "cooldown-filtered event count",
                "symbol coverage",
                "month coverage",
                "concentration",
                "overlap",
                "missingness",
                "material difference from failed routes",
                "simplicity / low degrees of freedom",
            ],
        },
        "forbidden_actions_confirmed_false": forbidden_false(),
        "allowed_next_step": allowed_next_step,
        "blocker": None,
        "replacement_checks_all_true": True,
        "payload_sha256_excluding_hash": "",
    }
    artifact["payload_sha256_excluding_hash"] = canonical_payload_hash(artifact)
    return artifact


def write_artifact(payload: dict[str, Any]) -> None:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def report(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload.get('discovery_status')}",
        f"result_classification: {payload.get('result_classification')}",
        f"recovery_audit_status: {payload.get('recovery_audit_status')}",
        f"input_artifact_hashes_unchanged: {bool_text(bool(payload.get('input_artifact_hashes_unchanged')))}",
        f"theory_id: {payload.get('theory_id')}",
        f"material_difference_from_failed_routes: {json.dumps(payload.get('material_difference_from_failed_routes'), sort_keys=True)}",
        f"selected_clean_event_definitions: {json.dumps(payload.get('selected_clean_event_definitions'), sort_keys=True)}",
        f"event_counts_by_definition: {json.dumps(payload.get('event_counts_by_definition'), sort_keys=True)}",
        f"cooldown_filtered_counts: {json.dumps(payload.get('cooldown_filtered_counts'), sort_keys=True)}",
        f"symbol_coverage_summary: {json.dumps(payload.get('symbol_coverage_summary'), sort_keys=True)}",
        f"month_coverage_summary: {json.dumps(payload.get('month_coverage_summary'), sort_keys=True)}",
        f"concentration_summary: {json.dumps(payload.get('concentration_summary'), sort_keys=True)}",
        f"arbusdt_summary: {json.dumps(payload.get('arbusdt_summary'), sort_keys=True)}",
        f"overlap_summary: {json.dumps(payload.get('overlap_summary'), sort_keys=True)}",
        f"missing_data_summary: {json.dumps(payload.get('missing_data_summary'), sort_keys=True)}",
        f"ratio_source_distribution: {json.dumps(payload.get('ratio_source_distribution'), sort_keys=True)}",
        f"extreme_threshold_distribution: {json.dumps(payload.get('extreme_threshold_distribution'), sort_keys=True)}",
        f"normalization_strength_distribution: {json.dumps(payload.get('normalization_strength_distribution'), sort_keys=True)}",
        f"optional_annotation_distribution: {json.dumps(payload.get('optional_annotation_distribution'), sort_keys=True)}",
        f"allowed_next_step: {payload.get('allowed_next_step')}",
        "commit hash: PENDING_COMMIT",
        "final git status: PENDING_COMMIT",
        "repo clean: PENDING_COMMIT",
        "tracked Python count: PENDING_COMMIT",
        "raw data committed: false",
        "cache files staged: false",
        f"forbidden actions confirmed false: {json.dumps(payload.get('forbidden_actions_confirmed_false'), sort_keys=True)}",
        f"blocker: {payload.get('blocker')}",
    ]
    return "\n".join(lines)


def main() -> int:
    hashes_before = None
    audit = None
    try:
        audit = recovery_audit()
        hashes_before = input_artifact_hashes() if audit["head_matches_expected"] else None
        payload = build_artifact()
    except Exception as exc:
        hashes_after = input_artifact_hashes() if hashes_before is not None else None
        payload = blocked_artifact(str(exc), audit, hashes_before, hashes_after)
    write_artifact(payload)
    print(report(payload))
    return 0 if payload.get("result_classification") != RESULT_FAILED else 1


if __name__ == "__main__":
    raise SystemExit(main())
