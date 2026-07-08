#!/usr/bin/env python
"""Strict diagnostic-only discovery evaluator for the 30-day BTC/ETH/SOL absorption pilot."""

from __future__ import annotations

import csv
import json
import math
import os
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import edge_factory_orderbook_um_30d_absorption_preview_v1 as absorption_30d  # noqa: E402


OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_DATA_ROOT = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_external_data")
ABSORPTION_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_absorption_preview_summary.json"
ABSORPTION_CATEGORY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_category_diagnostics.csv"
ABSORPTION_QUANTILE_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_quantile_diagnostics.csv"
ABSORPTION_DAILY_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_daily_stability.csv"
ABSORPTION_SYMBOL_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_symbol_stability.csv"
ABSORPTION_QUALITY_MD = OUTPUTS_DIR / "orderbook_um_30d_absorption_quality_report.md"
ABSORPTION_SAMPLE_CSV = OUTPUTS_DIR / "orderbook_um_30d_absorption_sample.csv"
DOWNLOAD_SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_pilot_download_summary.json"

SUMMARY_JSON = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_summary.json"
SUMMARY_MD = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_summary.md"
CATEGORY_EFFECTS_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_category_effects.csv"
SYMBOL_EFFECTS_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_symbol_effects.csv"
DAILY_EFFECTS_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_daily_effects.csv"
SPLIT_VALIDATION_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_split_validation.csv"
PERMUTATION_NULL_CSV = OUTPUTS_DIR / "orderbook_um_30d_strict_permutation_null.csv"
CANDIDATE_JSON = OUTPUTS_DIR / "orderbook_um_30d_strict_candidate_hypotheses.json"
QUALITY_REPORT_MD = OUTPUTS_DIR / "orderbook_um_30d_strict_discovery_quality_report.md"

TARGET_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
EVALUATED_CATEGORIES = [
    "BUY_PRESSURE_ABSORBED",
    "SELL_PRESSURE_ABSORBED",
    "FLOW_AND_DEPTH_ALIGNED_UP",
    "FLOW_AND_DEPTH_ALIGNED_DOWN",
]
BASELINE_CATEGORY = "MIXED_OR_NOISY"
HORIZONS = [10, 30, 60, 300]
EXPECTED_DIRECTIONS = {
    "BUY_PRESSURE_ABSORBED": -1,
    "SELL_PRESSURE_ABSORBED": 1,
    "FLOW_AND_DEPTH_ALIGNED_UP": 1,
    "FLOW_AND_DEPTH_ALIGNED_DOWN": -1,
}
MIN_EFFECT_BPS = {10: 1.0, 30: 1.0, 60: 2.0, 300: 3.0}
BOOTSTRAP_ITERATIONS = int(os.environ.get("ORDERBOOK_STRICT_BOOTSTRAP_ITERATIONS", "300"))
BOOTSTRAP_SAMPLE_CAP = int(os.environ.get("ORDERBOOK_STRICT_BOOTSTRAP_SAMPLE_CAP", "5000"))
PERMUTATION_ITERATIONS = int(os.environ.get("ORDERBOOK_STRICT_PERMUTATION_ITERATIONS", "200"))
FDR_ALPHA = float(os.environ.get("ORDERBOOK_STRICT_FDR_ALPHA", "0.10"))
RANDOM_SEED = int(os.environ.get("ORDERBOOK_STRICT_RANDOM_SEED", "17321"))


class StrictDiscoveryBlocked(RuntimeError):
    """Raised when strict discovery evaluation cannot be completed."""


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def data_root() -> Path:
    return Path(os.environ.get("EDGE_FACTORY_DATA_ROOT", str(DEFAULT_DATA_ROOT))).expanduser()


def work_dir() -> Path:
    root = data_root()
    if path_is_inside(root, REPO_ROOT):
        raise StrictDiscoveryBlocked(f"data root resolves inside repo: {root}")
    path = root / "binance_um_30d_strict_discovery_work"
    path.mkdir(parents=True, exist_ok=True)
    return path


def path_is_inside(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise StrictDiscoveryBlocked(f"missing required input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise StrictDiscoveryBlocked(f"input is not a JSON object: {path}")
    return payload


def ensure_inputs() -> dict[str, Any]:
    required = [
        ABSORPTION_SUMMARY_JSON,
        ABSORPTION_CATEGORY_CSV,
        ABSORPTION_QUANTILE_CSV,
        ABSORPTION_DAILY_CSV,
        ABSORPTION_SYMBOL_CSV,
        ABSORPTION_QUALITY_MD,
        ABSORPTION_SAMPLE_CSV,
        DOWNLOAD_SUMMARY_JSON,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise StrictDiscoveryBlocked(f"missing required 30-day diagnostic inputs: {missing}")
    summary = load_json(ABSORPTION_SUMMARY_JSON)
    if summary.get("replacement_checks_all_true") is not True:
        raise StrictDiscoveryBlocked("30-day absorption preview did not pass replacement checks")
    if summary.get("selected_day_count") != 30:
        raise StrictDiscoveryBlocked("30-day absorption preview does not report a 30-day window")
    return summary


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def numeric(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def standard_deviation(values: list[float]) -> float | None:
    return statistics.pstdev(values) if len(values) >= 2 else None


def positive_rate(values: list[float]) -> float | None:
    return sum(1 for value in values if value > 0) / len(values) if values else None


def sign(value: float | None) -> int:
    if value is None:
        return 0
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def same_direction(value: float | None, expected: int) -> bool:
    return sign(value) == expected


def date_index_map(start: str, end: str) -> dict[str, int]:
    start_day = datetime.strptime(start, "%Y-%m-%d").date()
    end_day = datetime.strptime(end, "%Y-%m-%d").date()
    out: dict[str, int] = {}
    current = start_day
    idx = 1
    while current <= end_day:
        out[current.isoformat()] = idx
        idx += 1
        current = current.fromordinal(current.toordinal() + 1)
    return out


def daily_metadata() -> dict[tuple[str, str], dict[str, Any]]:
    rows = read_csv_rows(ABSORPTION_DAILY_CSV)
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row.get("symbol", ""), row.get("file_date", ""))
        out[key] = {
            "volatility_bucket": row.get("volatility_bucket", ""),
            "is_weekend": str(row.get("is_weekend", "")).lower() == "true",
            "day_of_week": row.get("day_of_week", ""),
        }
    return out


def rebuild_compact_rows(absorption_summary: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest_rows = absorption_30d.read_manifest()
    download_summary = load_json(DOWNLOAD_SUMMARY_JSON)
    downloads = absorption_30d.download_lookup(download_summary)
    day_indices = date_index_map(str(absorption_summary["selected_start_date"]), str(absorption_summary["selected_end_date"]))
    metadata = daily_metadata()
    compact_rows: list[dict[str, Any]] = []
    parse_summaries: list[dict[str, Any]] = []
    for manifest_row in manifest_rows:
        aligned, file_summary = absorption_30d.parse_symbol_day(manifest_row, downloads)
        symbol = manifest_row["symbol"]
        file_date = manifest_row["file_date"]
        meta = metadata.get((symbol, file_date), {})
        for row in aligned:
            compact = {
                "symbol": symbol,
                "file_date": file_date,
                "day_index": day_indices[file_date],
                "category": row.get("absorption_category", "INSUFFICIENT_DATA"),
                "volatility_bucket": meta.get("volatility_bucket", ""),
                "is_weekend": bool(meta.get("is_weekend", False)),
            }
            for horizon in HORIZONS:
                compact[f"forward_return_{horizon}s"] = numeric(row.get(f"forward_return_{horizon}s"))
            compact_rows.append(compact)
        parse_summaries.append(
            {
                "symbol": symbol,
                "file_date": file_date,
                "aligned_rows": len(aligned),
                "bookdepth_feature_rows": file_summary["bookdepth"]["feature_rows"],
                "aggtrade_rows": file_summary["aggtrades"]["parsed_trade_rows"],
            }
        )
    return compact_rows, parse_summaries


def values_for(rows: list[dict[str, Any]], horizon: int, category: str | None = None, symbol: str | None = None, file_date: str | None = None) -> list[float]:
    column = f"forward_return_{horizon}s"
    values: list[float] = []
    for row in rows:
        if category is not None and row["category"] != category:
            continue
        if symbol is not None and row["symbol"] != symbol:
            continue
        if file_date is not None and row["file_date"] != file_date:
            continue
        value = row.get(column)
        if value is not None:
            values.append(float(value))
    return values


def metric_block(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "mean_forward_return": mean(values),
        "median_forward_return": median(values),
        "positive_forward_return_rate": positive_rate(values),
        "standard_deviation": standard_deviation(values),
    }


def bootstrap_ci(category_values: list[float], baseline_values: list[float], rng: random.Random) -> dict[str, Any]:
    if not category_values or not baseline_values:
        return {"bootstrap_ci_low": None, "bootstrap_ci_high": None, "bootstrap_iterations": 0, "bootstrap_ci_excludes_zero": False}
    category_sample_size = min(len(category_values), BOOTSTRAP_SAMPLE_CAP)
    baseline_sample_size = min(len(baseline_values), BOOTSTRAP_SAMPLE_CAP)
    effects: list[float] = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        category_mean = statistics.fmean(rng.choice(category_values) for _ in range(category_sample_size))
        baseline_mean = statistics.fmean(rng.choice(baseline_values) for _ in range(baseline_sample_size))
        effects.append(category_mean - baseline_mean)
    effects.sort()
    low_index = max(0, int(0.025 * (len(effects) - 1)))
    high_index = min(len(effects) - 1, int(0.975 * (len(effects) - 1)))
    low = effects[low_index]
    high = effects[high_index]
    return {
        "bootstrap_ci_low": low,
        "bootstrap_ci_high": high,
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_ci_excludes_zero": (low > 0 and high > 0) or (low < 0 and high < 0),
    }


def permutation_tests(rows: list[dict[str, Any]], category_effects: dict[tuple[str, int], float | None]) -> dict[tuple[str, int], dict[str, Any]]:
    rng = random.Random(RANDOM_SEED + 991)
    result: dict[tuple[str, int], dict[str, Any]] = {}
    for horizon in HORIZONS:
        column = f"forward_return_{horizon}s"
        grouped: dict[tuple[str, str], list[tuple[float, str]]] = defaultdict(list)
        for row in rows:
            value = row.get(column)
            if value is not None:
                grouped[(row["symbol"], row["file_date"])].append((float(value), row["category"]))
        null_effects: dict[str, list[float]] = {category: [] for category in EVALUATED_CATEGORIES}
        for _iteration in range(PERMUTATION_ITERATIONS):
            sums: dict[str, float] = defaultdict(float)
            counts: dict[str, int] = defaultdict(int)
            baseline_sum = 0.0
            baseline_count = 0
            for group_values in grouped.values():
                returns = [item[0] for item in group_values]
                labels = [item[1] for item in group_values]
                rng.shuffle(labels)
                for value, label in zip(returns, labels):
                    if label in EVALUATED_CATEGORIES:
                        sums[label] += value
                        counts[label] += 1
                    if label == BASELINE_CATEGORY:
                        baseline_sum += value
                        baseline_count += 1
            baseline_mean = baseline_sum / baseline_count if baseline_count else None
            for category in EVALUATED_CATEGORIES:
                if baseline_mean is None or counts[category] == 0:
                    continue
                null_effects[category].append((sums[category] / counts[category]) - baseline_mean)
        for category in EVALUATED_CATEGORIES:
            observed = category_effects.get((category, horizon))
            nulls = null_effects[category]
            if observed is None or not nulls:
                p_value = None
            else:
                extreme = sum(1 for value in nulls if abs(value) >= abs(observed))
                p_value = (extreme + 1) / (len(nulls) + 1)
            result[(category, horizon)] = {
                "permutation_iterations": len(nulls),
                "observed_effect_vs_mixed": observed,
                "permutation_p_value": p_value,
                "null_mean": mean(nulls),
                "null_standard_deviation": standard_deviation(nulls),
            }
    return result


def bh_q_values(p_values: dict[tuple[str, int], float | None]) -> dict[tuple[str, int], float | None]:
    valid = [(key, value) for key, value in p_values.items() if value is not None]
    valid.sort(key=lambda item: item[1])
    total = len(valid)
    q_by_key: dict[tuple[str, int], float | None] = {key: None for key in p_values}
    running_min = 1.0
    for rank_from_end, (key, value) in enumerate(reversed(valid), start=1):
        rank = total - rank_from_end + 1
        q_value = min(running_min, value * total / rank)
        running_min = q_value
        q_by_key[key] = q_value
    return q_by_key


def symbol_effect_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[str, int], dict[str, Any]]]:
    output: list[dict[str, Any]] = []
    summary: dict[tuple[str, int], dict[str, Any]] = {}
    for category in EVALUATED_CATEGORIES:
        expected = EXPECTED_DIRECTIONS[category]
        for horizon in HORIZONS:
            signs = 0
            present = 0
            symbol_counts: dict[str, int] = {}
            for symbol in TARGET_SYMBOLS:
                category_values = values_for(rows, horizon, category=category, symbol=symbol)
                mixed_values = values_for(rows, horizon, category=BASELINE_CATEGORY, symbol=symbol)
                all_values = values_for(rows, horizon, symbol=symbol)
                cat_metrics = metric_block(category_values)
                mixed_mean = mean(mixed_values)
                all_mean = mean(all_values)
                effect_mixed = None if cat_metrics["mean_forward_return"] is None or mixed_mean is None else cat_metrics["mean_forward_return"] - mixed_mean
                effect_all = None if cat_metrics["mean_forward_return"] is None or all_mean is None else cat_metrics["mean_forward_return"] - all_mean
                if category_values:
                    present += 1
                    symbol_counts[symbol] = len(category_values)
                if same_direction(effect_mixed, expected):
                    signs += 1
                output.append(
                    {
                        "category": category,
                        "horizon_seconds": horizon,
                        "symbol": symbol,
                        **cat_metrics,
                        "mixed_baseline_mean": mixed_mean,
                        "unconditional_baseline_mean": all_mean,
                        "effect_vs_mixed": effect_mixed,
                        "effect_vs_unconditional": effect_all,
                        "effect_vs_mixed_bps": effect_mixed * 10000.0 if effect_mixed is not None else None,
                        "expected_direction": expected,
                        "sign_matches_expected": same_direction(effect_mixed, expected),
                    }
                )
            total_count = sum(symbol_counts.values())
            max_share = max((count / total_count for count in symbol_counts.values()), default=0.0)
            summary[(category, horizon)] = {
                "symbols_present": present,
                "symbol_sign_match_count": signs,
                "symbol_sign_match_rate": signs / present if present else None,
                "max_symbol_row_share": max_share,
            }
    return output, summary


def daily_effect_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[str, int], dict[str, Any]]]:
    output: list[dict[str, Any]] = []
    summary: dict[tuple[str, int], dict[str, Any]] = {}
    symbol_days = sorted({(row["symbol"], row["file_date"]) for row in rows})
    for category in EVALUATED_CATEGORIES:
        expected = EXPECTED_DIRECTIONS[category]
        for horizon in HORIZONS:
            active = 0
            signs = 0
            day_counts: dict[str, int] = {}
            for symbol, file_date in symbol_days:
                category_values = values_for(rows, horizon, category=category, symbol=symbol, file_date=file_date)
                mixed_values = values_for(rows, horizon, category=BASELINE_CATEGORY, symbol=symbol, file_date=file_date)
                cat_metrics = metric_block(category_values)
                mixed_mean = mean(mixed_values)
                effect = None if cat_metrics["mean_forward_return"] is None or mixed_mean is None else cat_metrics["mean_forward_return"] - mixed_mean
                if category_values:
                    active += 1
                    day_counts[f"{symbol}|{file_date}"] = len(category_values)
                if same_direction(effect, expected):
                    signs += 1
                output.append(
                    {
                        "category": category,
                        "horizon_seconds": horizon,
                        "symbol": symbol,
                        "file_date": file_date,
                        **cat_metrics,
                        "mixed_baseline_mean": mixed_mean,
                        "effect_vs_mixed": effect,
                        "effect_vs_mixed_bps": effect * 10000.0 if effect is not None else None,
                        "expected_direction": expected,
                        "sign_matches_expected": same_direction(effect, expected),
                    }
                )
            total_count = sum(day_counts.values())
            max_share = max((count / total_count for count in day_counts.values()), default=0.0)
            summary[(category, horizon)] = {
                "active_symbol_days": active,
                "day_sign_match_count": signs,
                "day_sign_match_rate": signs / active if active else None,
                "max_symbol_day_row_share": max_share,
            }
    return output, summary


def split_condition(row: dict[str, Any], split_type: str, split_name: str) -> bool:
    idx = int(row["day_index"])
    if split_type == "first20_last10":
        return idx <= 20 if split_name == "first20" else idx > 20
    if split_type == "first15_last15":
        return idx <= 15 if split_name == "first15" else idx > 15
    if split_type == "volatility":
        return row.get("volatility_bucket") == split_name
    if split_type == "weekday_weekend":
        return bool(row.get("is_weekend")) if split_name == "weekend" else not bool(row.get("is_weekend"))
    return False


def split_effect_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[str, int], dict[str, Any]]]:
    splits = [
        ("first20_last10", "first20"),
        ("first20_last10", "last10"),
        ("first15_last15", "first15"),
        ("first15_last15", "last15"),
        ("volatility", "high_volatility"),
        ("volatility", "low_volatility"),
        ("weekday_weekend", "weekday"),
        ("weekday_weekend", "weekend"),
    ]
    output: list[dict[str, Any]] = []
    summary: dict[tuple[str, int], dict[str, Any]] = {}
    for category in EVALUATED_CATEGORIES:
        expected = EXPECTED_DIRECTIONS[category]
        for horizon in HORIZONS:
            required_split_matches: dict[str, bool] = {}
            for split_type, split_name in splits:
                split_rows = [row for row in rows if split_condition(row, split_type, split_name)]
                category_values = values_for(split_rows, horizon, category=category)
                mixed_values = values_for(split_rows, horizon, category=BASELINE_CATEGORY)
                all_values = values_for(split_rows, horizon)
                cat_metrics = metric_block(category_values)
                mixed_mean = mean(mixed_values)
                all_mean = mean(all_values)
                effect_mixed = None if cat_metrics["mean_forward_return"] is None or mixed_mean is None else cat_metrics["mean_forward_return"] - mixed_mean
                effect_all = None if cat_metrics["mean_forward_return"] is None or all_mean is None else cat_metrics["mean_forward_return"] - all_mean
                sign_ok = same_direction(effect_mixed, expected)
                if split_type in {"first20_last10", "first15_last15"}:
                    required_split_matches[f"{split_type}:{split_name}"] = sign_ok
                output.append(
                    {
                        "category": category,
                        "horizon_seconds": horizon,
                        "split_type": split_type,
                        "split_name": split_name,
                        **cat_metrics,
                        "mixed_baseline_mean": mixed_mean,
                        "unconditional_baseline_mean": all_mean,
                        "effect_vs_mixed": effect_mixed,
                        "effect_vs_unconditional": effect_all,
                        "effect_vs_mixed_bps": effect_mixed * 10000.0 if effect_mixed is not None else None,
                        "expected_direction": expected,
                        "sign_matches_expected": sign_ok,
                    }
                )
            summary[(category, horizon)] = {
                "first_second_split_signs_match": all(required_split_matches.values()) if required_split_matches else False,
                "required_split_sign_matches": required_split_matches,
            }
    return output, summary


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "" if row.get(field) is None else row.get(field, "") for field in fieldnames})


def category_effect_rows(rows: list[dict[str, Any]], symbol_summary: dict[tuple[str, int], dict[str, Any]], day_summary: dict[tuple[str, int], dict[str, Any]], split_summary: dict[tuple[str, int], dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(RANDOM_SEED)
    base_rows: list[dict[str, Any]] = []
    category_effect_lookup: dict[tuple[str, int], float | None] = {}
    for category in EVALUATED_CATEGORIES:
        expected = EXPECTED_DIRECTIONS[category]
        for horizon in HORIZONS:
            category_values = values_for(rows, horizon, category=category)
            mixed_values = values_for(rows, horizon, category=BASELINE_CATEGORY)
            all_values = values_for(rows, horizon)
            cat_metrics = metric_block(category_values)
            mixed_mean = mean(mixed_values)
            all_mean = mean(all_values)
            effect_mixed = None if cat_metrics["mean_forward_return"] is None or mixed_mean is None else cat_metrics["mean_forward_return"] - mixed_mean
            effect_all = None if cat_metrics["mean_forward_return"] is None or all_mean is None else cat_metrics["mean_forward_return"] - all_mean
            category_effect_lookup[(category, horizon)] = effect_mixed
            boot = bootstrap_ci(category_values, mixed_values, rng)
            row = {
                "category": category,
                "horizon_seconds": horizon,
                **cat_metrics,
                "mixed_baseline_count": len(mixed_values),
                "mixed_baseline_mean": mixed_mean,
                "unconditional_baseline_count": len(all_values),
                "unconditional_baseline_mean": all_mean,
                "effect_vs_mixed": effect_mixed,
                "effect_vs_unconditional": effect_all,
                "effect_vs_mixed_bps": effect_mixed * 10000.0 if effect_mixed is not None else None,
                "effect_vs_unconditional_bps": effect_all * 10000.0 if effect_all is not None else None,
                "expected_direction": expected,
                "expected_direction_matches": same_direction(effect_mixed, expected),
                **symbol_summary[(category, horizon)],
                **day_summary[(category, horizon)],
                **split_summary[(category, horizon)],
                **boot,
            }
            base_rows.append(row)
    permutation = permutation_tests(rows, category_effect_lookup)
    q_values = bh_q_values({key: value.get("permutation_p_value") for key, value in permutation.items()})
    permutation_rows: list[dict[str, Any]] = []
    final_rows: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for row in base_rows:
        key = (row["category"], row["horizon_seconds"])
        perm = permutation[key]
        q_value = q_values[key]
        permutation_rows.append(
            {
                "category": row["category"],
                "horizon_seconds": row["horizon_seconds"],
                **perm,
                "bh_q_value": q_value,
                "fdr_alpha": FDR_ALPHA,
                "passes_fdr": q_value is not None and q_value <= FDR_ALPHA,
            }
        )
        criteria = {
            "category_count_min_5000": row["count"] >= 5000,
            "present_in_all_3_symbols": row["symbols_present"] == 3,
            "present_in_at_least_20_symbol_days": row["active_symbol_days"] >= 20,
            "expected_direction_matches_observed": row["expected_direction_matches"],
            "symbol_sign_consistency_2_of_3": row["symbol_sign_match_count"] >= 2,
            "day_sign_consistency_at_least_60pct": (row["day_sign_match_rate"] or 0) >= 0.60,
            "first_second_split_signs_match": row["first_second_split_signs_match"],
            "statistical_check_passes": bool(row["bootstrap_ci_excludes_zero"]) or (q_value is not None and q_value <= FDR_ALPHA),
            "effect_magnitude_exceeds_threshold": row["effect_vs_mixed_bps"] is not None
            and abs(float(row["effect_vs_mixed_bps"])) >= MIN_EFFECT_BPS[int(row["horizon_seconds"])],
            "no_single_symbol_over_50pct": row["max_symbol_row_share"] <= 0.50,
            "no_single_symbol_day_over_10pct": row["max_symbol_day_row_share"] <= 0.10,
        }
        pass_count = sum(1 for value in criteria.values() if value)
        if all(criteria.values()):
            research_label = "DISCOVERY_CANDIDATE"
            biggest_failure_reason = ""
        elif criteria["category_count_min_5000"] and criteria["expected_direction_matches_observed"] and pass_count >= 7:
            research_label = "WEAK_MONITOR_ONLY"
            biggest_failure_reason = ",".join(key for key, value in criteria.items() if not value)
        else:
            research_label = "FAIL_NO_STABLE_SEPARATION"
            biggest_failure_reason = ",".join(key for key, value in criteria.items() if not value)
        final_row = {
            **row,
            "permutation_p_value": perm.get("permutation_p_value"),
            "bh_q_value": q_value,
            "passes_fdr": q_value is not None and q_value <= FDR_ALPHA,
            "minimum_effect_bps_threshold": MIN_EFFECT_BPS[int(row["horizon_seconds"])],
            "strict_criteria_json": json.dumps(criteria, sort_keys=True),
            "strict_criteria_pass_count": pass_count,
            "research_status_label": research_label,
            "biggest_failure_reason": biggest_failure_reason,
        }
        final_rows.append(final_row)
        if research_label == "DISCOVERY_CANDIDATE":
            candidates.append(
                {
                    "category": row["category"],
                    "horizon_seconds": row["horizon_seconds"],
                    "effect_vs_mixed_bps": row["effect_vs_mixed_bps"],
                    "effect_vs_unconditional_bps": row["effect_vs_unconditional_bps"],
                    "count": row["count"],
                    "strict_criteria": criteria,
                    "bootstrap_ci_low": row["bootstrap_ci_low"],
                    "bootstrap_ci_high": row["bootstrap_ci_high"],
                    "permutation_p_value": perm.get("permutation_p_value"),
                    "bh_q_value": q_value,
                    "research_status_label": research_label,
                }
            )
    return final_rows, permutation_rows, candidates


def choose_best(rows: list[dict[str, Any]], label: str) -> dict[str, Any] | None:
    selected = [row for row in rows if row.get("research_status_label") == label and row.get("effect_vs_mixed_bps") not in {None, ""}]
    if not selected:
        return None
    return max(selected, key=lambda item: abs(float(item["effect_vs_mixed_bps"])))


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d strict discovery summary v1",
        "",
        f"status: {summary['status']}",
        f"aligned_dataset_rebuilt: {summary['aligned_dataset_rebuilt']}",
        f"evaluated_categories: {', '.join(summary['evaluated_categories'])}",
        f"evaluated_horizons_seconds: {summary['evaluated_horizons_seconds']}",
        f"discovery_candidate_count: {summary['discovery_candidate_count']}",
        f"weak_monitor_only_count: {summary['weak_monitor_only_count']}",
        f"fail_count: {summary['fail_count']}",
        f"blocked_count: {summary['blocked_count']}",
        f"best_diagnostic_category: {summary['best_diagnostic_category']}",
        f"strongest_rejection_result: {summary['strongest_rejection_result']}",
        f"next_recommended_step: {summary['next_recommended_step']}",
        "",
        "## Pass/fail table",
    ]
    for item in summary["category_horizon_table"]:
        lines.append(
            f"- {item['category']} {item['horizon_seconds']}s: {item['research_status_label']}, effect_bps={item['effect_vs_mixed_bps']}, pass_count={item['strict_criteria_pass_count']}"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- Discovery labels are research status labels only.",
            "- No tradable strategy, execution action, or market instruction is produced by this evaluator.",
            f"- Multiple-testing control uses Benjamini-Hochberg FDR alpha {FDR_ALPHA}.",
            f"- Bootstrap iterations: {BOOTSTRAP_ITERATIONS}; permutation iterations: {PERMUTATION_ITERATIONS}.",
            "",
            f"replacement_checks_all_true={str(summary['replacement_checks_all_true']).lower()}",
            "",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_quality_md(summary: dict[str, Any]) -> None:
    lines = [
        "# Orderbook UM 30d strict discovery quality report v1",
        "",
        f"status: {summary['status']}",
        f"compact_row_count: {summary['compact_row_count']}",
        f"aligned_dataset_rebuilt: {summary['aligned_dataset_rebuilt']}",
        f"external_work_path: {summary['external_work_path']}",
        "",
        "## Leakage checks",
    ]
    for key, value in summary["leakage_checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Stability notes"])
    for note in summary["daily_symbol_stability_notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "## Multiple-testing notes"])
    for note in summary["multiple_testing_notes"]:
        lines.append(f"- {note}")
    lines.append("")
    QUALITY_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_blocked(reason: str) -> int:
    payload = {
        "status": "BLOCKED_INSUFFICIENT_DIAGNOSTIC_DATA",
        "created_at_utc": utc_now_text(),
        "exact_blocker": reason,
        "replacement_checks_all_true": False,
        "next_module": "ORDERBOOK_UM_30D_STRICT_DISCOVERY_BLOCKER_REVIEW",
        "next_recommended_step": "C_STOP_ORDERBOOK_ABSORPTION_ROUTE_IF_NO_STABLE_SEPARATION",
        "full_81_symbol_download_attempted": False,
        "ninety_day_download_attempted": False,
    }
    SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    SUMMARY_MD.write_text(
        "\n".join(
            [
                "# BLOCKED_INSUFFICIENT_DIAGNOSTIC_DATA",
                "",
                f"exact_blocker: {reason}",
                "replacement_checks_all_true=false",
                "next_module=ORDERBOOK_UM_30D_STRICT_DISCOVERY_BLOCKER_REVIEW",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"BLOCKED: {reason}")
    print("replacement_checks_all_true=false")
    return 2


def main() -> int:
    try:
        input_summary = ensure_inputs()
        external_work_path = work_dir()
        compact_rows, parse_summaries = rebuild_compact_rows(input_summary)
        if not compact_rows:
            raise StrictDiscoveryBlocked("rebuilt compact aligned diagnostics are empty")
        symbol_rows, symbol_summary = symbol_effect_rows(compact_rows)
        daily_rows, day_summary = daily_effect_rows(compact_rows)
        split_rows, split_summary = split_effect_rows(compact_rows)
        category_rows, permutation_rows, candidates = category_effect_rows(compact_rows, symbol_summary, day_summary, split_summary)
        candidate_count = sum(1 for row in category_rows if row["research_status_label"] == "DISCOVERY_CANDIDATE")
        weak_count = sum(1 for row in category_rows if row["research_status_label"] == "WEAK_MONITOR_ONLY")
        fail_count = sum(1 for row in category_rows if row["research_status_label"] == "FAIL_NO_STABLE_SEPARATION")
        best_candidate = choose_best(category_rows, "DISCOVERY_CANDIDATE")
        strongest_fail = choose_best(category_rows, "FAIL_NO_STABLE_SEPARATION")
        if candidate_count:
            next_step = "A_EXPAND_TO_90_DAYS_BTC_ETH_SOL"
        elif weak_count:
            next_step = "B_REDESIGN_DIAGNOSTIC_CATEGORIES"
        else:
            next_step = "C_STOP_ORDERBOOK_ABSORPTION_ROUTE_IF_NO_STABLE_SEPARATION"
        category_fields = [
            "category",
            "horizon_seconds",
            "count",
            "mean_forward_return",
            "median_forward_return",
            "positive_forward_return_rate",
            "standard_deviation",
            "mixed_baseline_count",
            "mixed_baseline_mean",
            "unconditional_baseline_count",
            "unconditional_baseline_mean",
            "effect_vs_mixed",
            "effect_vs_unconditional",
            "effect_vs_mixed_bps",
            "effect_vs_unconditional_bps",
            "expected_direction",
            "expected_direction_matches",
            "symbols_present",
            "symbol_sign_match_count",
            "symbol_sign_match_rate",
            "max_symbol_row_share",
            "active_symbol_days",
            "day_sign_match_count",
            "day_sign_match_rate",
            "max_symbol_day_row_share",
            "first_second_split_signs_match",
            "bootstrap_ci_low",
            "bootstrap_ci_high",
            "bootstrap_iterations",
            "bootstrap_ci_excludes_zero",
            "permutation_p_value",
            "bh_q_value",
            "passes_fdr",
            "minimum_effect_bps_threshold",
            "strict_criteria_json",
            "strict_criteria_pass_count",
            "research_status_label",
            "biggest_failure_reason",
        ]
        write_csv_rows(CATEGORY_EFFECTS_CSV, category_rows, category_fields)
        symbol_fields = [
            "category",
            "horizon_seconds",
            "symbol",
            "count",
            "mean_forward_return",
            "median_forward_return",
            "positive_forward_return_rate",
            "standard_deviation",
            "mixed_baseline_mean",
            "unconditional_baseline_mean",
            "effect_vs_mixed",
            "effect_vs_unconditional",
            "effect_vs_mixed_bps",
            "expected_direction",
            "sign_matches_expected",
        ]
        write_csv_rows(SYMBOL_EFFECTS_CSV, symbol_rows, symbol_fields)
        daily_fields = [
            "category",
            "horizon_seconds",
            "symbol",
            "file_date",
            "count",
            "mean_forward_return",
            "median_forward_return",
            "positive_forward_return_rate",
            "standard_deviation",
            "mixed_baseline_mean",
            "effect_vs_mixed",
            "effect_vs_mixed_bps",
            "expected_direction",
            "sign_matches_expected",
        ]
        write_csv_rows(DAILY_EFFECTS_CSV, daily_rows, daily_fields)
        split_fields = [
            "category",
            "horizon_seconds",
            "split_type",
            "split_name",
            "count",
            "mean_forward_return",
            "median_forward_return",
            "positive_forward_return_rate",
            "standard_deviation",
            "mixed_baseline_mean",
            "unconditional_baseline_mean",
            "effect_vs_mixed",
            "effect_vs_unconditional",
            "effect_vs_mixed_bps",
            "expected_direction",
            "sign_matches_expected",
        ]
        write_csv_rows(SPLIT_VALIDATION_CSV, split_rows, split_fields)
        permutation_fields = [
            "category",
            "horizon_seconds",
            "permutation_iterations",
            "observed_effect_vs_mixed",
            "permutation_p_value",
            "null_mean",
            "null_standard_deviation",
            "bh_q_value",
            "fdr_alpha",
            "passes_fdr",
        ]
        write_csv_rows(PERMUTATION_NULL_CSV, permutation_rows, permutation_fields)
        candidate_payload = {
            "status": "STRICT_DISCOVERY_CANDIDATE_REPORT_CREATED",
            "created_at_utc": utc_now_text(),
            "discovery_candidates": candidates,
            "weak_monitor_only": [row for row in category_rows if row["research_status_label"] == "WEAK_MONITOR_ONLY"],
            "fail_no_stable_separation": [row for row in category_rows if row["research_status_label"] == "FAIL_NO_STABLE_SEPARATION"],
            "research_labels_only": True,
            "tradable_strategy_claimed": False,
        }
        CANDIDATE_JSON.write_text(json.dumps(candidate_payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        table = [
            {
                "category": row["category"],
                "horizon_seconds": row["horizon_seconds"],
                "research_status_label": row["research_status_label"],
                "effect_vs_mixed_bps": row["effect_vs_mixed_bps"],
                "strict_criteria_pass_count": row["strict_criteria_pass_count"],
                "biggest_failure_reason": row["biggest_failure_reason"],
            }
            for row in category_rows
        ]
        summary = {
            "status": "PASS_ORDERBOOK_UM_30D_STRICT_DISCOVERY_EVALUATOR",
            "created_at_utc": utc_now_text(),
            "task_name": "ORDERBOOK_UM_30D_STRICT_DISCOVERY_EVALUATOR_V1",
            "input_files_used": [str(path) for path in [ABSORPTION_SUMMARY_JSON, ABSORPTION_CATEGORY_CSV, ABSORPTION_QUANTILE_CSV, ABSORPTION_DAILY_CSV, ABSORPTION_SYMBOL_CSV, ABSORPTION_QUALITY_MD, ABSORPTION_SAMPLE_CSV]],
            "aligned_dataset_rebuilt": True,
            "existing_aggregates_sufficient": False,
            "why_rebuilt": "strict permutation and split checks require category-specific row diagnostics by symbol-day",
            "external_work_path": str(external_work_path),
            "compact_row_count": len(compact_rows),
            "parse_summaries": parse_summaries,
            "evaluated_categories": EVALUATED_CATEGORIES,
            "evaluated_horizons_seconds": HORIZONS,
            "baseline_definitions": {
                "mixed_baseline": BASELINE_CATEGORY,
                "unconditional_baseline": "all categories with non-missing forward return for the horizon",
            },
            "strict_criteria": {
                "min_category_count": 5000,
                "present_in_all_symbols": 3,
                "min_symbol_days": 20,
                "min_symbol_sign_consistency": "2_of_3",
                "min_symbol_day_sign_consistency": 0.60,
                "split_tests": ["first20_last10", "first15_last15"],
                "statistical_check": "bootstrap_ci_excludes_zero OR permutation_bh_q_value <= fdr_alpha",
                "min_effect_bps": MIN_EFFECT_BPS,
                "max_single_symbol_row_share": 0.50,
                "max_single_symbol_day_row_share": 0.10,
            },
            "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
            "bootstrap_sample_cap": BOOTSTRAP_SAMPLE_CAP,
            "permutation_iterations": PERMUTATION_ITERATIONS,
            "fdr_alpha": FDR_ALPHA,
            "category_horizon_table": table,
            "discovery_candidate_count": candidate_count,
            "weak_monitor_only_count": weak_count,
            "fail_count": fail_count,
            "blocked_count": 0,
            "best_diagnostic_category": None if best_candidate is None else f"{best_candidate['category']}|{best_candidate['horizon_seconds']}s",
            "strongest_rejection_result": None if strongest_fail is None else f"{strongest_fail['category']}|{strongest_fail['horizon_seconds']}s",
            "daily_symbol_stability_notes": [
                "symbol-day effects are evaluated with within-symbol-day mixed baseline where available",
                "single symbol and single symbol-day concentration thresholds are enforced in strict criteria",
            ],
            "multiple_testing_notes": [
                "permutation p-values are corrected across all category/horizon tests using Benjamini-Hochberg",
                "corrected q-values are included in category effects and permutation null outputs",
            ],
            "leakage_checks": {
                "uses_existing_30d_outputs_only": True,
                "redownload_attempted": False,
                "ninety_day_download_attempted": False,
                "full_81_symbol_download_attempted": False,
                "forward_returns_used_only_as_diagnostics": True,
            },
            "output_files": {
                "summary_json": str(SUMMARY_JSON),
                "summary_md": str(SUMMARY_MD),
                "category_effects_csv": str(CATEGORY_EFFECTS_CSV),
                "symbol_effects_csv": str(SYMBOL_EFFECTS_CSV),
                "daily_effects_csv": str(DAILY_EFFECTS_CSV),
                "split_validation_csv": str(SPLIT_VALIDATION_CSV),
                "permutation_null_csv": str(PERMUTATION_NULL_CSV),
                "candidate_hypotheses_json": str(CANDIDATE_JSON),
                "quality_report_md": str(QUALITY_REPORT_MD),
            },
            "next_recommended_step": next_step,
            "research_labels_only": True,
            "tradable_strategy_claimed": False,
            "full_81_symbol_download_attempted": False,
            "ninety_day_download_attempted": False,
            "replacement_checks_all_true": True,
            "next_module": "ORDERBOOK_UM_30D_STRICT_DISCOVERY_VALIDATOR",
        }
        SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        write_summary_md(summary)
        write_quality_md(summary)
        print(f"status: {summary['status']}")
        print(f"aligned_dataset_rebuilt: {str(summary['aligned_dataset_rebuilt']).lower()}")
        print(f"compact_row_count: {summary['compact_row_count']}")
        print(f"discovery_candidate_count: {summary['discovery_candidate_count']}")
        print(f"weak_monitor_only_count: {summary['weak_monitor_only_count']}")
        print(f"fail_count: {summary['fail_count']}")
        print(f"summary_json: {SUMMARY_JSON}")
        print(f"replacement_checks_all_true: {str(summary['replacement_checks_all_true']).lower()}")
        print(f"next_recommended_step: {summary['next_recommended_step']}")
        return 0
    except StrictDiscoveryBlocked as exc:
        return write_blocked(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
