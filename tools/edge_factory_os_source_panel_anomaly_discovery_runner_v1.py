#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Source Panel Anomaly Discovery Runner v1

Purpose:
- Consume Source Panel Anomaly Discovery Contract v1.
- Consume policy/guard/validator/framework/true-panel states.
- Read full source panel parquet.
- Run outcome-agnostic anomaly discovery axes.
- Run negative controls and true-null replay.
- Keep plugin expansion blocked.
- Keep candidate/family/runtime/capital/live/real-order actions blocked.

This runner does NOT:
- use future returns as discovery features
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
- delete/move/archive files
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import math
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "source_panel_anomaly_discovery_contract_v1.json"
)

PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "source_panel_anomaly_discovery_with_true_nulls_plugin_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

TRUE_PANEL_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "true_source_panel_empirical_null_baseline_state_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

POLICY_VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_validation_state_v1.json"
)

POLICY_RUNTIME_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_policy_runtime_state_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_source_panel_anomaly_discovery_runner"

OUT_JSON = OUT_DIR / "source_panel_anomaly_discovery_runner_latest.json"
OUT_TXT = OUT_DIR / "source_panel_anomaly_discovery_runner_latest.txt"
OUT_SCHEMA_CSV = OUT_DIR / "source_panel_anomaly_schema_report_latest.csv"
OUT_COVERAGE_CSV = OUT_DIR / "source_panel_anomaly_month_symbol_coverage_latest.csv"
OUT_AXIS_INVENTORY_CSV = OUT_DIR / "source_panel_anomaly_axis_inventory_latest.csv"
OUT_NEGATIVE_CONTROL_CSV = OUT_DIR / "source_panel_anomaly_negative_control_inventory_latest.csv"
OUT_SCORE_CSV = OUT_DIR / "source_panel_outcome_agnostic_anomaly_scores_latest.csv"
OUT_MONTH_SCORE_CSV = OUT_DIR / "source_panel_anomaly_month_scores_latest.csv"
OUT_TRUE_NULL_CSV = OUT_DIR / "source_panel_anomaly_true_null_replay_summary_latest.csv"
OUT_TRUE_NULL_RUN_CSV = OUT_DIR / "source_panel_anomaly_true_null_runs_latest.csv"
OUT_POLICY_GATE_CSV = OUT_DIR / "source_panel_anomaly_policy_gate_pass_fail_latest.csv"
OUT_MATERIAL_DIFF_CSV = OUT_DIR / "source_panel_anomaly_material_difference_report_latest.csv"
OUT_CONSUMPTION_CSV = OUT_DIR / "source_panel_anomaly_consumption_report_latest.csv"

RUNNER_NAME = "edge_factory_os_source_panel_anomaly_discovery_runner_v1"
EXPECTED_RESEARCH_KEY = "SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS_V1"
EXPECTED_PLUGIN_KEY = "SOURCE_PANEL_ANOMALY_DISCOVERY_WITH_TRUE_NULLS_PLUGIN_V1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

ANOMALY_MONTH_SCORE_THRESHOLD = 1.65
ANOMALY_TOTAL_SCORE_THRESHOLD = 22.0

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
    "file_delete_performed": False,
    "file_move_performed": False,
    "archive_performed": False,
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def explicitly_blocked(value: Any) -> bool:
    """
    Safety interpretation:
    - Only explicit True means allowed.
    - Missing / None / False means blocked.
    """
    return value is not True


def safe_month_from_time(series: pd.Series) -> pd.Series:
    t = pd.to_datetime(series, utc=True, errors="coerce")
    t_naive = t.dt.tz_convert(None)
    return t_naive.dt.to_period("M").astype(str)


def choose_canonical_months(df: pd.DataFrame, required_count: int = 12) -> List[str]:
    month_counts = (
        df.groupby("month", sort=True)
        .size()
        .reset_index(name="row_count")
        .sort_values("month")
    )
    months = month_counts["month"].astype(str).tolist()

    if len(months) <= required_count:
        return months

    month_counts = month_counts.copy()
    month_counts["is_edge"] = False
    month_counts.loc[month_counts.index.min(), "is_edge"] = True
    month_counts.loc[month_counts.index.max(), "is_edge"] = True

    thinnest_edge = (
        month_counts[month_counts["is_edge"]]
        .sort_values("row_count")
        .head(1)["month"]
        .astype(str)
        .tolist()
    )
    filtered = [m for m in months if m not in set(thinnest_edge)]
    if len(filtered) >= required_count:
        return filtered[:required_count]

    return months[-required_count:]


def schema_report(df: pd.DataFrame, source_panel_path: Path, selected_features: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for col in df.columns:
        rows.append({
            "column": col,
            "present": True,
            "dtype": str(df[col].dtype),
            "selected_as_discovery_feature": col in selected_features,
            "source_panel_path": str(source_panel_path),
        })
    return rows


def coverage_report(df: pd.DataFrame, canonical_months: List[str]) -> List[Dict[str, Any]]:
    canonical_set = set(canonical_months)
    stats = (
        df.groupby("month")
        .agg(row_count=("symbol", "size"), symbol_count=("symbol", "nunique"))
        .reset_index()
        .sort_values("month")
    )
    rows = []
    for _, row in stats.iterrows():
        rows.append({
            "month": str(row["month"]),
            "is_canonical_policy_month": str(row["month"]) in canonical_set,
            "row_count": int(row["row_count"]),
            "symbol_count": int(row["symbol_count"]),
        })
    return rows


def is_forbidden_feature_name(col: str) -> bool:
    name = col.lower()
    forbidden_tokens = [
        "ret",
        "return",
        "pnl",
        "profit",
        "target",
        "future",
        "fwd",
        "label",
        "outcome",
        "signal",
        "win",
        "loss",
    ]
    return any(tok in name for tok in forbidden_tokens)


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df

    if {"high", "low", "close"}.issubset(out.columns):
        close = pd.to_numeric(out["close"], errors="coerce").replace(0, np.nan)
        high = pd.to_numeric(out["high"], errors="coerce")
        low = pd.to_numeric(out["low"], errors="coerce")
        out["derived_candle_range_bps"] = ((high - low) / close).replace([np.inf, -np.inf], np.nan) * 10000.0

    if {"open", "close"}.issubset(out.columns):
        open_ = pd.to_numeric(out["open"], errors="coerce").replace(0, np.nan)
        close = pd.to_numeric(out["close"], errors="coerce")
        out["derived_candle_body_bps"] = ((close - open_).abs() / open_).replace([np.inf, -np.inf], np.nan) * 10000.0

    if "close" in out.columns:
        close = pd.to_numeric(out["close"], errors="coerce").replace(0, np.nan)
        out["derived_log_close"] = np.log(close).replace([np.inf, -np.inf], np.nan)

    t = pd.to_datetime(out["time"], utc=True, errors="coerce")
    out["derived_hour_utc"] = t.dt.hour.astype("float64")
    out["derived_dayofweek_utc"] = t.dt.dayofweek.astype("float64")

    return out


def select_discovery_features(df: pd.DataFrame, max_features: int = 14) -> List[str]:
    preferred = [
        "entry_vol_quote",
        "entry_range_bps",
        "volume",
        "quote_volume",
        "turnover",
        "vol_quote",
        "range_bps",
        "atr_bps",
        "realized_vol_bps",
        "spread_bps",
        "derived_candle_range_bps",
        "derived_candle_body_bps",
        "derived_log_close",
        "derived_hour_utc",
        "derived_dayofweek_utc",
    ]

    numeric_cols = []
    for col in df.columns:
        if col in {"time", "symbol", "month"}:
            continue
        if is_forbidden_feature_name(col):
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            valid_ratio = pd.to_numeric(df[col], errors="coerce").notna().mean()
            if valid_ratio >= 0.80:
                numeric_cols.append(col)

    selected: List[str] = []
    for col in preferred:
        if col in numeric_cols and col not in selected:
            selected.append(col)

    for col in numeric_cols:
        if col not in selected:
            selected.append(col)
        if len(selected) >= max_features:
            break

    return selected[:max_features]


def axis_inventory(plugin: Dict[str, Any], selected_features: List[str]) -> List[Dict[str, Any]]:
    axes = plugin.get("anomaly_discovery_axes")
    if not isinstance(axes, list):
        axes = []

    rows = []
    for axis in axes:
        rows.append({
            "axis_key": str(axis),
            "uses_outcome_as_discovery_feature": False,
            "selected_feature_count": len(selected_features),
            "selected_features": "|".join(selected_features),
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def negative_control_inventory(plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    controls = plugin.get("negative_controls")
    if not isinstance(controls, list):
        controls = []

    rows = []
    for control in controls:
        rows.append({
            "negative_control_key": str(control),
            "uses_outcome_as_discovery_feature": False,
            "true_null_required": True,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def build_consumption_report(
    contract: Dict[str, Any],
    plugin: Dict[str, Any],
    framework_status: Dict[str, Any],
    true_panel_state: Dict[str, Any],
    policy: Dict[str, Any],
    validation_state: Dict[str, Any],
    runtime_state: Dict[str, Any],
    guard_feed: Dict[str, Any],
    blocklist_path: Path,
) -> List[Dict[str, Any]]:
    checks = [
        ("CONTRACT_READY", contract.get("contract_status") == "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_READY", contract.get("contract_status"), "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_READY"),
        ("PLUGIN_KEY_MATCH", plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY, plugin.get("plugin_key"), EXPECTED_PLUGIN_KEY),
        ("FRAMEWORK_READY", framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL", framework_status.get("panel_status"), "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"),
        ("TRUE_PANEL_FALSE_POSITIVE_REPAIRED", true_panel_state.get("false_positive_methodology_repaired") is True, true_panel_state.get("false_positive_methodology_repaired"), True),
        ("TRUE_PANEL_ACTUAL_SIGNAL_ABSENT", true_panel_state.get("actual_signal_present") is False, true_panel_state.get("actual_signal_present"), False),
        ("POLICY_ACTIVE", policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE", policy.get("policy_status"), "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"),
        ("VALIDATOR_PASS", validation_state.get("validator_pass") is True, validation_state.get("validator_pass"), True),
        ("RUNTIME_BLOCKS_PLUGIN", runtime_state.get("plugin_expansion_allowed") is False, runtime_state.get("plugin_expansion_allowed"), False),
        ("GUARD_PASS", guard_feed.get("guard_pass") is True, guard_feed.get("guard_pass"), True),
        ("BLOCKLIST_EXISTS", blocklist_path.exists(), blocklist_path.exists(), True),
        ("PLUGIN_EXPANSION_BLOCKED", explicitly_blocked(plugin.get("plugin_expansion_allowed")), plugin.get("plugin_expansion_allowed", False), False),
        ("CANDIDATE_BLOCKED", plugin.get("candidate_generation_allowed") is False, plugin.get("candidate_generation_allowed"), False),
        ("FAMILY_RELEASE_BLOCKED", plugin.get("family_release_allowed") is False, plugin.get("family_release_allowed"), False),
        ("RUNTIME_TOUCH_BLOCKED", plugin.get("runtime_touch_allowed") is False, plugin.get("runtime_touch_allowed"), False),
        ("CAPITAL_BLOCKED", plugin.get("capital_change_allowed") is False, plugin.get("capital_change_allowed"), False),
        ("LIVE_BLOCKED", plugin.get("live_allowed") is False, plugin.get("live_allowed"), False),
        ("REAL_ORDERS_BLOCKED", plugin.get("real_orders_allowed") is False, plugin.get("real_orders_allowed"), False),
    ]

    return [
        {
            "check_key": key,
            "passed": bool(passed),
            "observed": observed,
            "required": required,
            "contract_id": contract.get("contract_id"),
            "research_key": contract.get("research_key"),
        }
        for key, passed, observed, required in checks
    ]


def compute_month_feature_scores(
    df: pd.DataFrame,
    canonical_months: List[str],
    selected_features: List[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    month_rows: List[Dict[str, Any]] = []
    axis_rows: List[Dict[str, Any]] = []

    canonical_df = df[df["month"].isin(canonical_months)].copy()

    for feature in selected_features:
        vals = pd.to_numeric(canonical_df[feature], errors="coerce")
        if vals.notna().sum() < 1000:
            continue

        feature_df = canonical_df[["month", "symbol", feature]].copy()
        feature_df[feature] = pd.to_numeric(feature_df[feature], errors="coerce")
        feature_df = feature_df.replace([np.inf, -np.inf], np.nan).dropna(subset=[feature])

        for side in ["high", "low"]:
            per_month_scores: List[float] = []
            per_month_counts: List[int] = []
            per_month_symbols: List[int] = []

            for month in canonical_months:
                mdf = feature_df[feature_df["month"] == month]
                if len(mdf) < 100:
                    month_score = 0.0
                    row_count = 0
                    symbol_count = 0
                    threshold = np.nan
                    feature_mean = np.nan
                    feature_std = np.nan
                    extreme_mean = np.nan
                else:
                    x = pd.to_numeric(mdf[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
                    feature_mean = float(x.mean())
                    feature_std = float(x.std(ddof=0)) if float(x.std(ddof=0)) > 1e-12 else 1.0

                    if side == "high":
                        threshold = float(x.quantile(0.90))
                        extreme = mdf[pd.to_numeric(mdf[feature], errors="coerce") >= threshold]
                    else:
                        threshold = float(x.quantile(0.10))
                        extreme = mdf[pd.to_numeric(mdf[feature], errors="coerce") <= threshold]

                    row_count = int(len(extreme))
                    symbol_count = int(extreme["symbol"].nunique()) if row_count else 0
                    extreme_mean = float(pd.to_numeric(extreme[feature], errors="coerce").mean()) if row_count else np.nan
                    zmean = abs((extreme_mean - feature_mean) / feature_std) if row_count else 0.0

                    coverage_boost = min(1.25, math.log1p(symbol_count) / math.log1p(285))
                    size_boost = min(1.25, math.log1p(row_count) / math.log1p(10000))
                    month_score = float(zmean * coverage_boost * size_boost)

                per_month_scores.append(month_score)
                per_month_counts.append(row_count)
                per_month_symbols.append(symbol_count)

                month_rows.append({
                    "feature": feature,
                    "side": side,
                    "month": month,
                    "threshold": threshold,
                    "feature_mean": feature_mean,
                    "feature_std": feature_std,
                    "extreme_mean": extreme_mean,
                    "row_count": row_count,
                    "symbol_count": symbol_count,
                    "month_anomaly_score": month_score,
                    "month_score_pass": month_score >= ANOMALY_MONTH_SCORE_THRESHOLD,
                    "uses_outcome_as_discovery_feature": False,
                })

            active_months = sum(1 for x in per_month_counts if x > 0)
            strict_months = sum(1 for x in per_month_scores if x >= ANOMALY_MONTH_SCORE_THRESHOLD)
            total_score = float(sum(per_month_scores))
            min_month_score = float(min(per_month_scores)) if per_month_scores else 0.0
            median_month_score = float(np.median(per_month_scores)) if per_month_scores else 0.0
            avg_symbol_count = float(np.mean(per_month_symbols)) if per_month_symbols else 0.0
            avg_row_count = float(np.mean(per_month_counts)) if per_month_counts else 0.0

            strict_12_anomaly_preview = bool(
                active_months >= 12
                and strict_months >= 12
                and total_score >= ANOMALY_TOTAL_SCORE_THRESHOLD
            )

            axis_rows.append({
                "axis_key": f"{feature}_{side}_extreme",
                "feature": feature,
                "side": side,
                "active_months": active_months,
                "strict_months": strict_months,
                "total_anomaly_score": total_score,
                "min_month_anomaly_score": min_month_score,
                "median_month_anomaly_score": median_month_score,
                "avg_symbol_count": avg_symbol_count,
                "avg_row_count": avg_row_count,
                "strict_12_anomaly_preview": strict_12_anomaly_preview,
                "uses_outcome_as_discovery_feature": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            })

    axis_rows = sorted(
        axis_rows,
        key=lambda x: (
            bool(x.get("strict_12_anomaly_preview")),
            float(x.get("total_anomaly_score", 0.0)),
            float(x.get("median_month_anomaly_score", 0.0)),
        ),
        reverse=True,
    )

    return month_rows, axis_rows


def true_null_replay(
    axis_rows: List[Dict[str, Any]],
    month_rows: List[Dict[str, Any]],
    controls: List[str],
    runs_per_control: int,
    gate_caps: Dict[str, Any],
    seed: int = 20260513,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = np.random.default_rng(seed)

    month_score_pool = np.array(
        [to_float(x.get("month_anomaly_score")) for x in month_rows],
        dtype="float64",
    )
    month_score_pool = month_score_pool[np.isfinite(month_score_pool)]

    if month_score_pool.size == 0:
        month_score_pool = np.array([0.0], dtype="float64")

    observed_strict_count = sum(1 for x in axis_rows if bool(x.get("strict_12_anomaly_preview")))
    observed_best_score = max([to_float(x.get("total_anomaly_score")) for x in axis_rows] or [0.0])

    null_run_rows: List[Dict[str, Any]] = []

    for control in controls:
        for run_id in range(1, runs_per_control + 1):
            if control == "side_flip_control":
                sample = -rng.choice(month_score_pool, size=12, replace=True)
                sample = np.abs(sample)
            elif control == "feature_label_permutation_control":
                sample = rng.permutation(rng.choice(month_score_pool, size=12, replace=True))
            elif control == "time_block_shuffle_control":
                if month_score_pool.size >= 12:
                    start = int(rng.integers(0, max(1, month_score_pool.size - 12)))
                    sample = month_score_pool[start : start + 12]
                    if sample.size < 12:
                        sample = rng.choice(month_score_pool, size=12, replace=True)
                else:
                    sample = rng.choice(month_score_pool, size=12, replace=True)
            else:
                sample = rng.choice(month_score_pool, size=12, replace=True)

            strict_months = int(np.sum(sample >= ANOMALY_MONTH_SCORE_THRESHOLD))
            total_score = float(np.sum(sample))
            min_score = float(np.min(sample))

            strict_random_hit = bool(strict_months >= 12 and total_score >= ANOMALY_TOTAL_SCORE_THRESHOLD)
            null_adjusted_hit = bool(strict_random_hit and total_score >= observed_best_score)

            null_run_rows.append({
                "negative_control": control,
                "run_id": run_id,
                "strict_months": strict_months,
                "total_anomaly_score": total_score,
                "min_month_anomaly_score": min_score,
                "strict_12_random_hit": strict_random_hit,
                "null_adjusted_random_hit": null_adjusted_hit,
                "observed_strict_12_anomaly_preview_count": observed_strict_count,
                "observed_best_total_anomaly_score": observed_best_score,
            })

    summary_rows: List[Dict[str, Any]] = []
    for control in controls:
        subset = [x for x in null_run_rows if x["negative_control"] == control]
        if not subset:
            continue
        totals = [to_float(x["total_anomaly_score"]) for x in subset]
        summary_rows.append({
            "negative_control": control,
            "runs": len(subset),
            "strict_12_any_random_hit_rate": float(np.mean([1.0 if x["strict_12_random_hit"] else 0.0 for x in subset])),
            "null_adjusted_any_random_hit_rate": float(np.mean([1.0 if x["null_adjusted_random_hit"] else 0.0 for x in subset])),
            "p50_total_anomaly_score": float(np.quantile(totals, 0.50)),
            "p90_total_anomaly_score": float(np.quantile(totals, 0.90)),
            "p95_total_anomaly_score": float(np.quantile(totals, 0.95)),
            "p99_total_anomaly_score": float(np.quantile(totals, 0.99)),
            "observed_strict_12_anomaly_preview_count": observed_strict_count,
            "observed_best_total_anomaly_score": observed_best_score,
        })

    max_allowed_strict = float(gate_caps.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)
    max_allowed_null = float(gate_caps.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)

    max_strict_rate = max([to_float(x["strict_12_any_random_hit_rate"]) for x in summary_rows] or [1.0])
    max_null_rate = max([to_float(x["null_adjusted_any_random_hit_rate"]) for x in summary_rows] or [1.0])

    policy_gate_rows = [
        {
            "gate_key": "ANOMALY_AXIS_COUNT",
            "passed": len(axis_rows) >= 6,
            "observed": len(axis_rows),
            "required": ">=6",
        },
        {
            "gate_key": "NEGATIVE_CONTROL_COUNT",
            "passed": len(controls) >= 5,
            "observed": len(controls),
            "required": ">=5",
        },
        {
            "gate_key": "MINIMUM_TRUE_NULL_RUNS",
            "passed": all(int(x["runs"]) >= runs_per_control for x in summary_rows),
            "observed": min([int(x["runs"]) for x in summary_rows] or [0]),
            "required": runs_per_control,
        },
        {
            "gate_key": "STRICT_12_RANDOM_HIT_RATE_CAP",
            "passed": max_strict_rate <= max_allowed_strict,
            "observed": max_strict_rate,
            "required": f"<= {max_allowed_strict}",
        },
        {
            "gate_key": "NULL_ADJUSTED_RANDOM_HIT_RATE_CAP",
            "passed": max_null_rate <= max_allowed_null,
            "observed": max_null_rate,
            "required": f"<= {max_allowed_null}",
        },
        {
            "gate_key": "OUTCOME_AGNOSTIC_ANOMALY_PREVIEW_PRESENT",
            "passed": observed_strict_count > 0,
            "observed": observed_strict_count,
            "required": ">0",
        },
        {
            "gate_key": "PLUGIN_EXPANSION_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "plugin_expansion_allowed=False",
        },
        {
            "gate_key": "CANDIDATE_GENERATION_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "candidate_generation_allowed=False",
        },
    ]

    return null_run_rows, summary_rows, policy_gate_rows


def summarize_policy_gates(policy_gate_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    failed = [x for x in policy_gate_rows if not bool(x.get("passed"))]
    return {
        "anomaly_policy_gate_pass": len(failed) == 0,
        "anomaly_policy_gate_fail_count": len(failed),
        "failed_gate_keys": [x.get("gate_key") for x in failed],
    }


def material_difference_report(contract: Dict[str, Any], route_hash: str, selected_route_hash: str, blocklist: Any) -> List[Dict[str, Any]]:
    blocked = set()
    for row in extract_blocked_routes(blocklist):
        if row.get("route_hash"):
            blocked.add(str(row.get("route_hash")))

    return [
        {
            "check_key": "CONTRACT_ROUTE_HASH_NOT_BLOCKED",
            "passed": route_hash not in blocked,
            "observed": route_hash,
            "required": "not in blocklist",
        },
        {
            "check_key": "SELECTED_QUEUE_ROUTE_HASH_NOT_BLOCKED",
            "passed": selected_route_hash not in blocked,
            "observed": selected_route_hash,
            "required": "not in blocklist",
        },
        {
            "check_key": "MATERIAL_DIFFERENCE_CLAIM_PRESENT",
            "passed": bool(contract.get("route_hash_payload")),
            "observed": "route_hash_payload present",
            "required": "material difference evidence",
        },
        {
            "check_key": "OUTCOME_AGNOSTIC_DISCOVERY",
            "passed": True,
            "observed": "outcome columns excluded from discovery features",
            "required": "no future return / pnl / outcome feature use",
        },
        {
            "check_key": "TRUE_NULL_REQUIRED",
            "passed": True,
            "observed": "true-null replay is part of runner gates",
            "required": "true source-panel null before signal claim",
        },
    ]


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def build_text_summary(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DISCOVERY RUNNER v1")
    lines.append("=" * 100)

    for key in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "contract_hash",
        "route_hash",
        "selected_queue_route_hash",
        "research_key",
        "plugin_key",
        "policy_hash",
        "row_count",
        "symbol_count",
        "raw_calendar_month_count",
        "canonical_policy_month_count",
        "selected_feature_count",
        "anomaly_axis_row_count",
        "strict_12_anomaly_preview_count",
        "negative_control_count",
        "true_null_runs_per_control",
        "total_true_null_run_rows",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "anomaly_policy_gate_pass",
        "anomaly_policy_gate_fail_count",
        "failed_gate_keys",
        "elapsed_seconds",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for row in result.get("policy_gate_rows", []):
        lines.append(f"{row.get('gate_key')}: passed={row.get('passed')} observed={row.get('observed')} required={row.get('required')}")

    lines.append("")
    lines.append("TOP ANOMALY SCORES")
    lines.append("-" * 100)
    for row in result.get("top_anomaly_score_rows", [])[:20]:
        lines.append(
            f"{row.get('axis_key')}: strict={row.get('strict_12_anomaly_preview')} "
            f"score={row.get('total_anomaly_score')} min_month={row.get('min_month_anomaly_score')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "schema_csv",
        "coverage_csv",
        "axis_inventory_csv",
        "negative_control_csv",
        "score_csv",
        "month_score_csv",
        "true_null_csv",
        "true_null_run_csv",
        "policy_gate_csv",
        "material_difference_csv",
        "consumption_csv",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS SOURCE PANEL ANOMALY DISCOVERY RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"policy_hash: {result.get('policy_hash')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"selected_feature_count: {result.get('selected_feature_count')}")
    print(f"anomaly_axis_row_count: {result.get('anomaly_axis_row_count')}")
    print(f"strict_12_anomaly_preview_count: {result.get('strict_12_anomaly_preview_count')}")
    print(f"negative_control_count: {result.get('negative_control_count')}")
    print(f"true_null_runs_per_control: {result.get('true_null_runs_per_control')}")
    print(f"total_true_null_run_rows: {result.get('total_true_null_run_rows')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"anomaly_policy_gate_pass: {result.get('anomaly_policy_gate_pass')}")
    print(f"anomaly_policy_gate_fail_count: {result.get('anomaly_policy_gate_fail_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('score_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    plugin = load_json(PLUGIN_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    source_panel_path = Path(contract.get("source_panel_path") or plugin.get("source_panel_path") or "")

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "selected_queue_route_hash": contract.get("selected_queue_route_hash"),
        "research_key": contract.get("research_key"),
        "plugin_key": contract.get("plugin_key"),
        "policy_hash": contract.get("policy_hash"),
        "source_panel_path": str(source_panel_path),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "schema_csv": str(OUT_SCHEMA_CSV),
        "coverage_csv": str(OUT_COVERAGE_CSV),
        "axis_inventory_csv": str(OUT_AXIS_INVENTORY_CSV),
        "negative_control_csv": str(OUT_NEGATIVE_CONTROL_CSV),
        "score_csv": str(OUT_SCORE_CSV),
        "month_score_csv": str(OUT_MONTH_SCORE_CSV),
        "true_null_csv": str(OUT_TRUE_NULL_CSV),
        "true_null_run_csv": str(OUT_TRUE_NULL_RUN_CSV),
        "policy_gate_csv": str(OUT_POLICY_GATE_CSV),
        "material_difference_csv": str(OUT_MATERIAL_DIFF_CSV),
        "consumption_csv": str(OUT_CONSUMPTION_CSV),
        **SAFETY_FLAGS,
    }

    try:
        consumption_rows = build_consumption_report(
            contract=contract,
            plugin=plugin,
            framework_status=framework_status,
            true_panel_state=true_panel_state,
            policy=policy,
            validation_state=validation_state,
            runtime_state=runtime_state,
            guard_feed=guard_feed,
            blocklist_path=BLOCKLIST_PATH,
        )
        write_csv(OUT_CONSUMPTION_CSV, consumption_rows)

        consumption_pass = all(bool(x.get("passed")) for x in consumption_rows)

        contract_ready = (
            contract.get("contract_status") == "SOURCE_PANEL_ANOMALY_DISCOVERY_CONTRACT_READY"
            and contract.get("research_key") == EXPECTED_RESEARCH_KEY
            and contract.get("plugin_key") == EXPECTED_PLUGIN_KEY
        )
        plugin_ready = (
            plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY
            and plugin.get("research_key") == EXPECTED_RESEARCH_KEY
            and explicitly_blocked(plugin.get("plugin_expansion_allowed"))
        )
        source_panel_exists = source_panel_path.exists()

        if not (contract_ready and plugin_ready and consumption_pass and source_panel_exists):
            result = {
                **base_result,
                "runner_status": "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_SOURCE_PANEL_ANOMALY_DISCOVERY_PREREQUISITES_NO_RELEASE",
                "reason": (
                    f"contract_ready={contract_ready}; plugin_ready={plugin_ready}; "
                    f"consumption_pass={consumption_pass}; source_panel_exists={source_panel_exists}"
                ),
                "consumption_rows": consumption_rows,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        print(f"Reading source panel: {source_panel_path}")
        df = pd.read_parquet(source_panel_path)

        if "time" not in df.columns or "symbol" not in df.columns:
            result = {
                **base_result,
                "runner_status": "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_BLOCKED_MISSING_TIME_OR_SYMBOL",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_SOURCE_PANEL_SCHEMA_NO_RELEASE",
                "reason": f"time_present={'time' in df.columns}; symbol_present={'symbol' in df.columns}",
                "row_count": int(len(df)),
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        df = df.copy()
        df["month"] = safe_month_from_time(df["time"])
        df["symbol"] = df["symbol"].astype(str)
        df = add_derived_features(df)

        df = df.dropna(subset=["month", "symbol"])
        row_count = int(len(df))
        symbol_count = int(df["symbol"].nunique())
        raw_months = sorted(df["month"].dropna().astype(str).unique().tolist())
        raw_calendar_month_count = len(raw_months)
        canonical_months = choose_canonical_months(df, required_count=12)
        canonical_policy_month_count = len(canonical_months)

        selected_features = select_discovery_features(df, max_features=14)

        schema_rows = schema_report(df, source_panel_path, selected_features)
        coverage_rows = coverage_report(df, canonical_months)
        axis_inventory_rows = axis_inventory(plugin, selected_features)
        negative_control_rows = negative_control_inventory(plugin)

        write_csv(OUT_SCHEMA_CSV, schema_rows)
        write_csv(OUT_COVERAGE_CSV, coverage_rows)
        write_csv(OUT_AXIS_INVENTORY_CSV, axis_inventory_rows)
        write_csv(OUT_NEGATIVE_CONTROL_CSV, negative_control_rows)

        if (
            row_count < 1000000
            or symbol_count < 200
            or canonical_policy_month_count != 12
            or len(selected_features) < 2
            or len(negative_control_rows) < 5
        ):
            result = {
                **base_result,
                "runner_status": "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_BLOCKED_PANEL_OR_FEATURE_COVERAGE_FAILED",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_PANEL_FEATURE_COVERAGE_NO_RELEASE",
                "reason": (
                    f"row_count={row_count}; symbol_count={symbol_count}; "
                    f"canonical_policy_month_count={canonical_policy_month_count}; "
                    f"selected_feature_count={len(selected_features)}; negative_control_count={len(negative_control_rows)}"
                ),
                "row_count": row_count,
                "symbol_count": symbol_count,
                "raw_calendar_month_count": raw_calendar_month_count,
                "canonical_policy_month_count": canonical_policy_month_count,
                "selected_features": selected_features,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        print(f"Computing anomaly axes: features={len(selected_features)}, canonical_months={canonical_policy_month_count}")
        month_score_rows, anomaly_score_rows = compute_month_feature_scores(
            df=df,
            canonical_months=canonical_months,
            selected_features=selected_features,
        )

        write_csv(OUT_MONTH_SCORE_CSV, month_score_rows)
        write_csv(OUT_SCORE_CSV, anomaly_score_rows)

        controls = [
            str(x.get("negative_control_key"))
            for x in negative_control_rows
            if x.get("negative_control_key")
        ]

        runs_per_control = max(
            1000,
            to_int(plugin.get("minimum_empirical_null_runs")),
            to_int(contract.get("minimum_empirical_null_runs")),
        )

        gate_caps = plugin.get("gate_caps")
        if not isinstance(gate_caps, dict):
            gate_caps = contract.get("gate_caps") if isinstance(contract.get("gate_caps"), dict) else {}

        print(f"Running true-null replay: controls={len(controls)}, runs_per_control={runs_per_control}")

        null_run_rows, true_null_summary_rows, policy_gate_rows = true_null_replay(
            axis_rows=anomaly_score_rows,
            month_rows=month_score_rows,
            controls=controls,
            runs_per_control=runs_per_control,
            gate_caps=gate_caps,
            seed=20260513,
        )

        material_rows = material_difference_report(
            contract=contract,
            route_hash=str(contract.get("route_hash")),
            selected_route_hash=str(contract.get("selected_queue_route_hash")),
            blocklist=blocklist,
        )

        write_csv(OUT_TRUE_NULL_RUN_CSV, null_run_rows)
        write_csv(OUT_TRUE_NULL_CSV, true_null_summary_rows)
        write_csv(OUT_POLICY_GATE_CSV, policy_gate_rows)
        write_csv(OUT_MATERIAL_DIFF_CSV, material_rows)

        gate_summary = summarize_policy_gates(policy_gate_rows)
        anomaly_policy_gate_pass = bool(gate_summary["anomaly_policy_gate_pass"])
        failed_gate_keys = gate_summary["failed_gate_keys"]

        max_strict_rate = max([to_float(x.get("strict_12_any_random_hit_rate")) for x in true_null_summary_rows] or [1.0])
        max_null_rate = max([to_float(x.get("null_adjusted_any_random_hit_rate")) for x in true_null_summary_rows] or [1.0])

        strict_preview_count = sum(1 for x in anomaly_score_rows if bool(x.get("strict_12_anomaly_preview")))

        material_difference_pass = all(bool(x.get("passed")) for x in material_rows)

        if anomaly_policy_gate_pass and material_difference_pass:
            runner_status = "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_PREVIEW_FOUND_TRUE_NULL_CLEAN_NOT_RELEASE"
            next_action = "BUILD_SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATOR_NO_RELEASE"
            reason = (
                f"strict_12_anomaly_preview_count={strict_preview_count}; true_null_caps_pass=True; "
                f"material_difference_pass=True; release_allowed=False"
            )
        elif strict_preview_count > 0:
            runner_status = "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_PREVIEW_FOUND_BUT_TRUE_NULL_OR_POLICY_FAIL"
            next_action = "BUILD_SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATOR_KEEP_ACTIONS_BLOCKED"
            reason = (
                f"strict_12_anomaly_preview_count={strict_preview_count}; failed_gates={failed_gate_keys}; "
                f"max_strict_rate={max_strict_rate}; max_null_rate={max_null_rate}; material_difference_pass={material_difference_pass}"
            )
        else:
            runner_status = "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_COMPLETE_NO_POLICY_LOCKED_ANOMALY_PREVIEW"
            next_action = "BUILD_SOURCE_PANEL_ANOMALY_DISCOVERY_EVALUATOR_OR_ROTATE_NO_RELEASE"
            reason = (
                f"strict_12_anomaly_preview_count=0; anomaly_axis_row_count={len(anomaly_score_rows)}; "
                f"failed_gates={failed_gate_keys}; material_difference_pass={material_difference_pass}"
            )

        result = {
            **base_result,
            "runner_status": runner_status,
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "reason": reason,
            "row_count": row_count,
            "symbol_count": symbol_count,
            "raw_calendar_month_count": raw_calendar_month_count,
            "canonical_policy_month_count": canonical_policy_month_count,
            "canonical_policy_months": canonical_months,
            "selected_feature_count": len(selected_features),
            "selected_features": selected_features,
            "anomaly_axis_row_count": len(anomaly_score_rows),
            "strict_12_anomaly_preview_count": strict_preview_count,
            "negative_control_count": len(controls),
            "true_null_runs_per_control": runs_per_control,
            "total_true_null_run_rows": len(null_run_rows),
            "max_strict_12_any_random_hit_rate": max_strict_rate,
            "max_null_adjusted_any_random_hit_rate": max_null_rate,
            "anomaly_policy_gate_pass": anomaly_policy_gate_pass,
            "anomaly_policy_gate_fail_count": gate_summary["anomaly_policy_gate_fail_count"],
            "failed_gate_keys": failed_gate_keys,
            "material_difference_pass": material_difference_pass,
            "top_anomaly_score_rows": anomaly_score_rows[:25],
            "true_null_summary_rows": true_null_summary_rows,
            "policy_gate_rows": policy_gate_rows,
            "material_difference_rows": material_rows,
            "consumption_rows": consumption_rows,
            "release_gate_feed": {
                "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_RAN": True,
                "SOURCE_PANEL_ANOMALY_PREVIEW_FOUND": strict_preview_count > 0,
                "SOURCE_PANEL_ANOMALY_TRUE_NULL_CLEAN": anomaly_policy_gate_pass,
                "MATERIAL_DIFFERENCE_PASS": material_difference_pass,
                "POLICY_LOCKED": True,
                "PLUGIN_EXPANSION_ALLOWED_FROM_THIS_RUNNER": False,
                "RELEASE_PASS_FROM_THIS_RUNNER": False,
                "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_RUNNER": False,
                "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_RUNNER": False,
                "FAMILY_RELEASE_ALLOWED_FROM_THIS_RUNNER": False,
                "RUNTIME_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
                "CAPITAL_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
                "ACTIVE_PAPER_ALLOWED_FROM_THIS_RUNNER": False,
                "LIVE_ALLOWED_FROM_THIS_RUNNER": False,
                "REAL_ORDERS_ALLOWED_FROM_THIS_RUNNER": False,
            },
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }

        write_json(OUT_JSON, result)
        write_text(OUT_TXT, build_text_summary(result))
        print_summary(result)
        return 0

    except Exception as exc:
        result = {
            **base_result,
            "runner_status": "SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_SOURCE_PANEL_ANOMALY_DISCOVERY_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(exc).__name__}: {exc}",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text(OUT_TXT, build_text_summary(result))
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

