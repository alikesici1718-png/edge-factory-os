#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Source Panel Anomaly Deep Validation Runner v1

Purpose:
- Consume Source Panel Anomaly Deep Validation Contract v1.
- Read full source panel.
- Validate the discovered anomaly preview under:
  - month holdout stability
  - symbol holdout stability
  - threshold perturbation
  - noise perturbation
  - negative controls rerun
  - true source-panel null rerun
  - outcome/feature leakage audits
  - calendar edge-month sensitivity
  - row/symbol/month coverage checks
- Keep candidate/family/runtime/capital/live/real-order actions blocked.

This runner does NOT:
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
    / "source_panel_anomaly_deep_validation_contract_v1.json"
)

PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "source_panel_anomaly_deep_validation_plugin_v1.json"
)

ANOMALY_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "source_panel_anomaly_discovery_state_v1.json"
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

PREVIEW_CSV = (
    BASE_DIR
    / "edge_factory_os_source_panel_anomaly_discovery_evaluator"
    / "source_panel_anomaly_preview_candidates_for_validation_latest.csv"
)

BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_source_panel_anomaly_deep_validation_runner"

OUT_JSON = OUT_DIR / "source_panel_anomaly_deep_validation_runner_latest.json"
OUT_TXT = OUT_DIR / "source_panel_anomaly_deep_validation_runner_latest.txt"
OUT_INPUT_CONSUMPTION_CSV = OUT_DIR / "source_panel_anomaly_deep_validation_input_consumption_latest.csv"
OUT_PREVIEW_CONSUMPTION_CSV = OUT_DIR / "source_panel_anomaly_deep_validation_preview_consumption_latest.csv"
OUT_MONTH_HOLDOUT_CSV = OUT_DIR / "source_panel_anomaly_month_holdout_stability_latest.csv"
OUT_SYMBOL_HOLDOUT_CSV = OUT_DIR / "source_panel_anomaly_symbol_holdout_stability_latest.csv"
OUT_THRESHOLD_PERTURB_CSV = OUT_DIR / "source_panel_anomaly_threshold_perturbation_latest.csv"
OUT_NOISE_PERTURB_CSV = OUT_DIR / "source_panel_anomaly_noise_perturbation_latest.csv"
OUT_NEGATIVE_CONTROL_CSV = OUT_DIR / "source_panel_anomaly_deep_negative_controls_latest.csv"
OUT_TRUE_NULL_RERUN_CSV = OUT_DIR / "source_panel_anomaly_deep_true_null_rerun_latest.csv"
OUT_LEAKAGE_AUDIT_CSV = OUT_DIR / "source_panel_anomaly_leakage_audit_latest.csv"
OUT_CALENDAR_EDGE_CSV = OUT_DIR / "source_panel_anomaly_calendar_edge_sensitivity_latest.csv"
OUT_GATE_CSV = OUT_DIR / "source_panel_anomaly_deep_validation_gate_table_latest.csv"
OUT_RESULTS_CSV = OUT_DIR / "source_panel_anomaly_deep_validation_results_latest.csv"

RUNNER_NAME = "edge_factory_os_source_panel_anomaly_deep_validation_runner_v1"
EXPECTED_RESEARCH_KEY = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_V1"
EXPECTED_PLUGIN_KEY = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_PLUGIN_V1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

MONTH_SCORE_THRESHOLD = 1.65
TOTAL_SCORE_THRESHOLD = 22.0

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


def read_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return [dict(row) for row in csv.DictReader(f)]
    except Exception:
        return []


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


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass"}


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def explicitly_blocked(value: Any) -> bool:
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


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df
    if {"open", "close"}.issubset(out.columns):
        open_ = pd.to_numeric(out["open"], errors="coerce").replace(0, np.nan)
        close = pd.to_numeric(out["close"], errors="coerce")
        out["derived_candle_body_bps"] = ((close - open_).abs() / open_).replace([np.inf, -np.inf], np.nan) * 10000.0

    if {"high", "low", "close"}.issubset(out.columns):
        close = pd.to_numeric(out["close"], errors="coerce").replace(0, np.nan)
        high = pd.to_numeric(out["high"], errors="coerce")
        low = pd.to_numeric(out["low"], errors="coerce")
        out["derived_candle_range_bps"] = ((high - low) / close).replace([np.inf, -np.inf], np.nan) * 10000.0

    if "close" in out.columns:
        close = pd.to_numeric(out["close"], errors="coerce").replace(0, np.nan)
        out["derived_log_close"] = np.log(close).replace([np.inf, -np.inf], np.nan)

    return out


def feature_leakage_flag(feature_name: str) -> bool:
    name = str(feature_name).lower()
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


def score_month_subset(
    df: pd.DataFrame,
    feature: str,
    side: str,
    months: List[str],
    quantile: float = 0.90,
    noise_scale: float = 0.0,
    seed: int = 20260513,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rng = np.random.default_rng(seed)
    rows: List[Dict[str, Any]] = []
    scores: List[float] = []
    row_counts: List[int] = []
    symbol_counts: List[int] = []

    for month in months:
        mdf = df[df["month"] == month].copy()
        x = pd.to_numeric(mdf[feature], errors="coerce").replace([np.inf, -np.inf], np.nan)
        mdf = mdf.loc[x.notna()].copy()
        x = pd.to_numeric(mdf[feature], errors="coerce")

        if len(mdf) < 100:
            score = 0.0
            threshold = np.nan
            extreme_mean = np.nan
            feature_mean = np.nan
            feature_std = np.nan
            rc = 0
            sc = 0
        else:
            if noise_scale > 0:
                std = float(x.std(ddof=0)) if float(x.std(ddof=0)) > 1e-12 else 1.0
                x = x + rng.normal(0.0, std * noise_scale, size=len(x))

            feature_mean = float(x.mean())
            feature_std = float(x.std(ddof=0)) if float(x.std(ddof=0)) > 1e-12 else 1.0

            if side == "high":
                threshold = float(x.quantile(quantile))
                mask = x >= threshold
            else:
                threshold = float(x.quantile(1.0 - quantile))
                mask = x <= threshold

            extreme = mdf.loc[mask]
            ex = x.loc[mask]
            rc = int(mask.sum())
            sc = int(extreme["symbol"].nunique()) if rc else 0
            extreme_mean = float(ex.mean()) if rc else np.nan
            zmean = abs((extreme_mean - feature_mean) / feature_std) if rc else 0.0
            coverage_boost = min(1.25, math.log1p(sc) / math.log1p(285))
            size_boost = min(1.25, math.log1p(rc) / math.log1p(10000))
            score = float(zmean * coverage_boost * size_boost)

        scores.append(score)
        row_counts.append(rc)
        symbol_counts.append(sc)

        rows.append({
            "month": month,
            "feature": feature,
            "side": side,
            "quantile": quantile,
            "noise_scale": noise_scale,
            "threshold": threshold,
            "feature_mean": feature_mean,
            "feature_std": feature_std,
            "extreme_mean": extreme_mean,
            "row_count": rc,
            "symbol_count": sc,
            "month_score": score,
            "month_pass": score >= MONTH_SCORE_THRESHOLD,
        })

    summary = {
        "active_months": len(months),
        "strict_months": int(sum(1 for x in scores if x >= MONTH_SCORE_THRESHOLD)),
        "total_score": float(sum(scores)),
        "min_month_score": float(min(scores)) if scores else 0.0,
        "median_month_score": float(np.median(scores)) if scores else 0.0,
        "avg_row_count": float(np.mean(row_counts)) if row_counts else 0.0,
        "avg_symbol_count": float(np.mean(symbol_counts)) if symbol_counts else 0.0,
        "strict_12_pass": bool(len(months) >= 12 and sum(1 for x in scores if x >= MONTH_SCORE_THRESHOLD) >= 12 and sum(scores) >= TOTAL_SCORE_THRESHOLD),
    }

    return rows, summary


def run_month_holdout(df: pd.DataFrame, feature: str, side: str, months: List[str]) -> List[Dict[str, Any]]:
    rows = []
    holdout_sets = [
        ("drop_first_month", months[1:]),
        ("drop_last_month", months[:-1]),
        ("drop_first_two_months", months[2:]),
        ("drop_last_two_months", months[:-2]),
        ("drop_alternating_even", [m for i, m in enumerate(months) if i % 2 == 1]),
        ("drop_alternating_odd", [m for i, m in enumerate(months) if i % 2 == 0]),
    ]

    for name, train_months in holdout_sets:
        _, summary = score_month_subset(df, feature, side, train_months, quantile=0.90)
        rows.append({
            "test_key": "month_holdout_stability",
            "variant": name,
            "month_count": len(train_months),
            **summary,
            "passed": summary["strict_months"] >= max(6, int(len(train_months) * 0.75)) and summary["median_month_score"] >= MONTH_SCORE_THRESHOLD,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def stable_symbol_fold(symbol: str, fold_count: int = 5) -> int:
    total = sum(ord(ch) for ch in str(symbol))
    return total % fold_count


def run_symbol_holdout(df: pd.DataFrame, feature: str, side: str, months: List[str]) -> List[Dict[str, Any]]:
    rows = []
    work = df.copy()
    work["symbol_fold"] = work["symbol"].map(lambda s: stable_symbol_fold(s, 5))

    for fold in range(5):
        subset = work[work["symbol_fold"] != fold].copy()
        _, summary = score_month_subset(subset, feature, side, months, quantile=0.90)
        rows.append({
            "test_key": "symbol_holdout_stability",
            "variant": f"exclude_symbol_fold_{fold}",
            "excluded_fold": fold,
            "remaining_symbol_count": int(subset["symbol"].nunique()),
            **summary,
            "passed": summary["strict_12_pass"] and summary["avg_symbol_count"] >= 100,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def run_threshold_perturbation(df: pd.DataFrame, feature: str, side: str, months: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for q in [0.85, 0.875, 0.90, 0.925, 0.95]:
        _, summary = score_month_subset(df, feature, side, months, quantile=q)
        rows.append({
            "test_key": "feature_threshold_perturbation",
            "variant": f"quantile_{q}",
            "quantile": q,
            **summary,
            "passed": summary["strict_12_pass"],
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def run_noise_perturbation(df: pd.DataFrame, feature: str, side: str, months: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for noise in [0.01, 0.025, 0.05, 0.075, 0.10]:
        _, summary = score_month_subset(df, feature, side, months, quantile=0.90, noise_scale=noise, seed=20260513 + int(noise * 1000))
        rows.append({
            "test_key": "feature_value_noise_perturbation",
            "variant": f"noise_{noise}",
            "noise_scale": noise,
            **summary,
            "passed": summary["strict_12_pass"],
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def run_calendar_edge_sensitivity(df: pd.DataFrame, feature: str, side: str, months: List[str]) -> List[Dict[str, Any]]:
    variants = [
        ("canonical_default", months),
        ("drop_first_keep_11", months[1:]),
        ("drop_last_keep_11", months[:-1]),
        ("middle_10", months[1:-1]),
    ]
    rows = []
    for name, test_months in variants:
        _, summary = score_month_subset(df, feature, side, test_months, quantile=0.90)
        min_required = max(8, int(len(test_months) * 0.75))
        rows.append({
            "test_key": "calendar_edge_month_sensitivity",
            "variant": name,
            "month_count": len(test_months),
            **summary,
            "passed": summary["strict_months"] >= min_required and summary["median_month_score"] >= MONTH_SCORE_THRESHOLD,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def run_negative_controls(df: pd.DataFrame, feature: str, side: str, months: List[str]) -> List[Dict[str, Any]]:
    rows = []
    controls = [
        "side_flip_control",
        "month_shuffle_control",
        "feature_label_permutation_control",
        "symbol_shuffle_control",
        "time_block_shuffle_control",
    ]

    rng = np.random.default_rng(20260513)

    base_feature = pd.to_numeric(df[feature], errors="coerce").copy()

    for control in controls:
        work = df.copy()

        if control == "side_flip_control":
            control_side = "low" if side == "high" else "high"
            _, summary = score_month_subset(work, feature, control_side, months, quantile=0.90)

        elif control == "month_shuffle_control":
            shuffled_months = work["month"].to_numpy().copy()
            rng.shuffle(shuffled_months)
            work["month"] = shuffled_months
            _, summary = score_month_subset(work, feature, side, months, quantile=0.90)

        elif control == "feature_label_permutation_control":
            shuffled = base_feature.to_numpy().copy()
            rng.shuffle(shuffled)
            work[feature] = shuffled
            _, summary = score_month_subset(work, feature, side, months, quantile=0.90)

        elif control == "symbol_shuffle_control":
            shuffled_symbols = work["symbol"].to_numpy().copy()
            rng.shuffle(shuffled_symbols)
            work["symbol"] = shuffled_symbols
            _, summary = score_month_subset(work, feature, side, months, quantile=0.90)

        else:
            shuffled_feature = base_feature.to_numpy().copy()
            block = max(100, min(5000, len(shuffled_feature) // 100))
            if len(shuffled_feature) > block:
                chunks = [shuffled_feature[i:i+block] for i in range(0, len(shuffled_feature), block)]
                rng.shuffle(chunks)
                work[feature] = np.concatenate(chunks)[:len(work)]
            _, summary = score_month_subset(work, feature, side, months, quantile=0.90)

        rows.append({
            "test_key": "negative_controls_rerun",
            "negative_control": control,
            **summary,
            "passed": not summary["strict_12_pass"],
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })

    return rows


def run_true_null_rerun(df: pd.DataFrame, feature: str, side: str, months: List[str], runs: int, caps: Dict[str, Any]) -> List[Dict[str, Any]]:
    _, base_summary = score_month_subset(df, feature, side, months, quantile=0.90)
    observed_score = float(base_summary.get("total_score", 0.0))

    month_rows, _ = score_month_subset(df, feature, side, months, quantile=0.90)
    pool = np.asarray([to_float(x.get("month_score")) for x in month_rows], dtype="float64")
    pool = pool[np.isfinite(pool)]
    if pool.size == 0:
        pool = np.array([0.0], dtype="float64")

    rng = np.random.default_rng(20260513)
    strict_hits = 0
    null_hits = 0
    run_rows = []

    for i in range(1, runs + 1):
        sample = rng.choice(pool, size=12, replace=True)
        strict_months = int(np.sum(sample >= MONTH_SCORE_THRESHOLD))
        total_score = float(np.sum(sample))
        strict_hit = bool(strict_months >= 12 and total_score >= TOTAL_SCORE_THRESHOLD)
        null_hit = bool(strict_hit and total_score >= observed_score)

        strict_hits += int(strict_hit)
        null_hits += int(null_hit)

        if i <= 200:
            run_rows.append({
                "test_key": "true_source_panel_null_rerun",
                "run_id": i,
                "strict_months": strict_months,
                "total_score": total_score,
                "observed_score": observed_score,
                "strict_random_hit": strict_hit,
                "null_adjusted_random_hit": null_hit,
            })

    max_allowed_strict = float(caps.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)
    max_allowed_null = float(caps.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)

    strict_rate = strict_hits / max(1, runs)
    null_rate = null_hits / max(1, runs)

    run_rows.append({
        "test_key": "true_source_panel_null_rerun_summary",
        "run_id": "SUMMARY",
        "runs": runs,
        "strict_12_any_random_hit_rate": strict_rate,
        "null_adjusted_any_random_hit_rate": null_rate,
        "observed_score": observed_score,
        "max_allowed_strict_12_any_random_hit_rate": max_allowed_strict,
        "max_allowed_null_adjusted_any_random_hit_rate": max_allowed_null,
        "passed": strict_rate <= max_allowed_strict and null_rate <= max_allowed_null,
    })

    return run_rows


def run_leakage_audit(feature: str, contract: Dict[str, Any], plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    rows.append({
        "audit_key": "feature_name_leakage_audit",
        "observed": feature,
        "passed": not feature_leakage_flag(feature),
        "required": "feature name must not contain future/outcome/return/pnl/label tokens",
    })
    rows.append({
        "audit_key": "contract_release_blocked",
        "observed": contract.get("release_allowed"),
        "passed": contract.get("release_allowed") is False,
        "required": False,
    })
    rows.append({
        "audit_key": "plugin_candidate_blocked",
        "observed": plugin.get("candidate_generation_allowed", False),
        "passed": plugin.get("candidate_generation_allowed", False) is False,
        "required": False,
    })
    rows.append({
        "audit_key": "plugin_family_blocked",
        "observed": plugin.get("family_release_allowed", False),
        "passed": plugin.get("family_release_allowed", False) is False,
        "required": False,
    })
    rows.append({
        "audit_key": "plugin_runtime_blocked",
        "observed": plugin.get("runtime_touch_allowed", False),
        "passed": plugin.get("runtime_touch_allowed", False) is False,
        "required": False,
    })
    rows.append({
        "audit_key": "plugin_live_blocked",
        "observed": plugin.get("live_allowed", False),
        "passed": plugin.get("live_allowed", False) is False,
        "required": False,
    })
    return rows


def build_input_consumption_report(
    contract: Dict[str, Any],
    plugin: Dict[str, Any],
    anomaly_state: Dict[str, Any],
    framework_status: Dict[str, Any],
    true_panel_state: Dict[str, Any],
    policy: Dict[str, Any],
    validation_state: Dict[str, Any],
    runtime_state: Dict[str, Any],
    guard_feed: Dict[str, Any],
) -> List[Dict[str, Any]]:
    checks = [
        ("CONTRACT_READY", contract.get("contract_status") == "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_READY", contract.get("contract_status"), "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_READY"),
        ("PLUGIN_KEY_MATCH", plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY, plugin.get("plugin_key"), EXPECTED_PLUGIN_KEY),
        ("ANOMALY_STATE_READY", anomaly_state.get("state_status") == "SOURCE_PANEL_ANOMALY_PREVIEW_FOUND_TRUE_NULL_CLEAN_DEEP_VALIDATION_REQUIRED", anomaly_state.get("state_status"), "SOURCE_PANEL_ANOMALY_PREVIEW_FOUND_TRUE_NULL_CLEAN_DEEP_VALIDATION_REQUIRED"),
        ("FRAMEWORK_STATUS_READY", framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL", framework_status.get("panel_status"), "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"),
        ("TRUE_PANEL_FALSE_POSITIVE_REPAIRED", true_panel_state.get("false_positive_methodology_repaired") is True, true_panel_state.get("false_positive_methodology_repaired"), True),
        ("TRUE_PANEL_ACTUAL_SIGNAL_ABSENT", true_panel_state.get("actual_signal_present") is False, true_panel_state.get("actual_signal_present"), False),
        ("POLICY_ACTIVE", policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE", policy.get("policy_status"), "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"),
        ("VALIDATOR_PASS", validation_state.get("validator_pass") is True, validation_state.get("validator_pass"), True),
        ("RUNTIME_BLOCKS_PLUGIN", explicitly_blocked(runtime_state.get("plugin_expansion_allowed")), runtime_state.get("plugin_expansion_allowed", False), False),
        ("GUARD_PASS", guard_feed.get("guard_pass") is True, guard_feed.get("guard_pass"), True),
        ("PLUGIN_EXPANSION_BLOCKED", explicitly_blocked(plugin.get("plugin_expansion_allowed")), plugin.get("plugin_expansion_allowed", False), False),
        ("CANDIDATE_BLOCKED", plugin.get("candidate_generation_allowed", False) is False, plugin.get("candidate_generation_allowed", False), False),
        ("FAMILY_BLOCKED", plugin.get("family_release_allowed", False) is False, plugin.get("family_release_allowed", False), False),
        ("RUNTIME_TOUCH_BLOCKED", plugin.get("runtime_touch_allowed", False) is False, plugin.get("runtime_touch_allowed", False), False),
        ("CAPITAL_BLOCKED", plugin.get("capital_change_allowed", False) is False, plugin.get("capital_change_allowed", False), False),
        ("LIVE_BLOCKED", plugin.get("live_allowed", False) is False, plugin.get("live_allowed", False), False),
        ("REAL_ORDERS_BLOCKED", plugin.get("real_orders_allowed", False) is False, plugin.get("real_orders_allowed", False), False),
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


def build_preview_consumption_report(preview_rows: List[Dict[str, Any]], contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    top = preview_rows[0] if preview_rows else {}
    checks = [
        ("PREVIEW_ROW_PRESENT", len(preview_rows) > 0, len(preview_rows), ">0"),
        ("PREVIEW_FEATURE_MATCH", str(top.get("feature")) == str(contract.get("preview_feature")), top.get("feature"), contract.get("preview_feature")),
        ("PREVIEW_SIDE_MATCH", str(top.get("side")) == str(contract.get("preview_side")), top.get("side"), contract.get("preview_side")),
        ("PREVIEW_AXIS_MATCH", str(top.get("axis_key")) == str(contract.get("preview_axis_key")), top.get("axis_key"), contract.get("preview_axis_key")),
        ("PREVIEW_IS_STRICT_12", to_bool(top.get("strict_12_anomaly_preview")), top.get("strict_12_anomaly_preview"), True),
    ]
    return [
        {
            "check_key": key,
            "passed": bool(passed),
            "observed": observed,
            "required": required,
        }
        for key, passed, observed, required in checks
    ]


def summarize_test_rows(rows: List[Dict[str, Any]], test_key: str) -> Dict[str, Any]:
    subset = [r for r in rows if r.get("test_key") == test_key or str(r.get("test_key", "")).startswith(test_key)]
    if not subset:
        return {
            "test_key": test_key,
            "test_count": 0,
            "pass_count": 0,
            "fail_count": 1,
            "passed": False,
        }
    pass_count = sum(1 for r in subset if to_bool(r.get("passed")))
    return {
        "test_key": test_key,
        "test_count": len(subset),
        "pass_count": pass_count,
        "fail_count": len(subset) - pass_count,
        "passed": pass_count == len(subset),
    }


def build_gate_table(
    *,
    input_pass: bool,
    preview_pass: bool,
    leakage_rows: List[Dict[str, Any]],
    month_rows: List[Dict[str, Any]],
    symbol_rows: List[Dict[str, Any]],
    threshold_rows: List[Dict[str, Any]],
    noise_rows: List[Dict[str, Any]],
    negative_rows: List[Dict[str, Any]],
    true_null_rows: List[Dict[str, Any]],
    calendar_rows: List[Dict[str, Any]],
    row_count: int,
    symbol_count: int,
    canonical_month_count: int,
) -> List[Dict[str, Any]]:
    true_null_summary = [r for r in true_null_rows if r.get("run_id") == "SUMMARY"]
    true_null_pass = bool(true_null_summary and to_bool(true_null_summary[0].get("passed")))

    gates = [
        {
            "gate_key": "INPUT_CONSUMPTION_PASS",
            "passed": input_pass,
            "observed": input_pass,
            "required": True,
        },
        {
            "gate_key": "PREVIEW_CONSUMPTION_PASS",
            "passed": preview_pass,
            "observed": preview_pass,
            "required": True,
        },
        {
            "gate_key": "ROW_COVERAGE_PASS",
            "passed": row_count >= 1000000,
            "observed": row_count,
            "required": ">=1000000",
        },
        {
            "gate_key": "SYMBOL_COVERAGE_PASS",
            "passed": symbol_count >= 200,
            "observed": symbol_count,
            "required": ">=200",
        },
        {
            "gate_key": "CANONICAL_MONTH_COUNT_PASS",
            "passed": canonical_month_count == 12,
            "observed": canonical_month_count,
            "required": 12,
        },
        summarize_test_rows(month_rows, "month_holdout_stability"),
        summarize_test_rows(symbol_rows, "symbol_holdout_stability"),
        summarize_test_rows(threshold_rows, "feature_threshold_perturbation"),
        summarize_test_rows(noise_rows, "feature_value_noise_perturbation"),
        summarize_test_rows(negative_rows, "negative_controls_rerun"),
        {
            "gate_key": "TRUE_SOURCE_PANEL_NULL_RERUN_PASS",
            "passed": true_null_pass,
            "observed": true_null_summary[0] if true_null_summary else None,
            "required": "strict/null rates below policy caps",
        },
        {
            "gate_key": "LEAKAGE_AUDIT_PASS",
            "passed": all(to_bool(x.get("passed")) for x in leakage_rows),
            "observed": sum(1 for x in leakage_rows if not to_bool(x.get("passed"))),
            "required": "0 failed leakage checks",
        },
        summarize_test_rows(calendar_rows, "calendar_edge_month_sensitivity"),
        {
            "gate_key": "RELEASE_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "release_allowed=False",
        },
        {
            "gate_key": "CANDIDATE_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "candidate_generation_allowed=False",
        },
    ]

    normalized = []
    for gate in gates:
        if "gate_key" not in gate and "test_key" in gate:
            gate["gate_key"] = str(gate["test_key"]).upper()
        normalized.append(gate)

    return normalized


def build_text_summary(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SOURCE PANEL ANOMALY DEEP VALIDATION RUNNER v1")
    lines.append("=" * 100)

    for key in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "research_key",
        "plugin_key",
        "policy_hash",
        "preview_axis_key",
        "preview_feature",
        "preview_side",
        "row_count",
        "symbol_count",
        "raw_calendar_month_count",
        "canonical_policy_month_count",
        "deep_validation_gate_pass",
        "deep_validation_gate_fail_count",
        "failed_gate_keys",
        "validation_test_count",
        "validation_pass_count",
        "validation_fail_count",
        "release_allowed",
        "elapsed_seconds",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("DEEP VALIDATION GATES")
    lines.append("-" * 100)
    for row in result.get("gate_rows", []):
        lines.append(f"{row.get('gate_key')}: passed={row.get('passed')} observed={row.get('observed')} required={row.get('required')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "input_consumption_csv",
        "preview_consumption_csv",
        "month_holdout_csv",
        "symbol_holdout_csv",
        "threshold_perturb_csv",
        "noise_perturb_csv",
        "negative_control_csv",
        "true_null_rerun_csv",
        "leakage_audit_csv",
        "calendar_edge_csv",
        "gate_csv",
        "results_csv",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS SOURCE PANEL ANOMALY DEEP VALIDATION RUNNER v1")
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
    print(f"preview_axis_key: {result.get('preview_axis_key')}")
    print(f"preview_feature: {result.get('preview_feature')}")
    print(f"preview_side: {result.get('preview_side')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"deep_validation_gate_pass: {result.get('deep_validation_gate_pass')}")
    print(f"deep_validation_gate_fail_count: {result.get('deep_validation_gate_fail_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"validation_test_count: {result.get('validation_test_count')}")
    print(f"validation_pass_count: {result.get('validation_pass_count')}")
    print(f"validation_fail_count: {result.get('validation_fail_count')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('results_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    plugin = load_json(PLUGIN_JSON, default={})
    anomaly_state = load_json(ANOMALY_STATE_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    preview_rows = read_csv_rows(PREVIEW_CSV)

    source_panel_path = Path(contract.get("source_panel_path") or plugin.get("source_panel_path") or "")
    feature = str(contract.get("preview_feature") or plugin.get("preview_feature") or "")
    side = str(contract.get("preview_side") or plugin.get("preview_side") or "high")
    preview_axis_key = str(contract.get("preview_axis_key") or plugin.get("preview_axis_key") or "")

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "source_anomaly_route_hash": contract.get("source_anomaly_route_hash"),
        "research_key": contract.get("research_key"),
        "plugin_key": contract.get("plugin_key"),
        "policy_hash": contract.get("policy_hash"),
        "preview_axis_key": preview_axis_key,
        "preview_feature": feature,
        "preview_side": side,
        "source_panel_path": str(source_panel_path),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "input_consumption_csv": str(OUT_INPUT_CONSUMPTION_CSV),
        "preview_consumption_csv": str(OUT_PREVIEW_CONSUMPTION_CSV),
        "month_holdout_csv": str(OUT_MONTH_HOLDOUT_CSV),
        "symbol_holdout_csv": str(OUT_SYMBOL_HOLDOUT_CSV),
        "threshold_perturb_csv": str(OUT_THRESHOLD_PERTURB_CSV),
        "noise_perturb_csv": str(OUT_NOISE_PERTURB_CSV),
        "negative_control_csv": str(OUT_NEGATIVE_CONTROL_CSV),
        "true_null_rerun_csv": str(OUT_TRUE_NULL_RERUN_CSV),
        "leakage_audit_csv": str(OUT_LEAKAGE_AUDIT_CSV),
        "calendar_edge_csv": str(OUT_CALENDAR_EDGE_CSV),
        "gate_csv": str(OUT_GATE_CSV),
        "results_csv": str(OUT_RESULTS_CSV),
        **SAFETY_FLAGS,
    }

    try:
        input_rows = build_input_consumption_report(
            contract=contract,
            plugin=plugin,
            anomaly_state=anomaly_state,
            framework_status=framework_status,
            true_panel_state=true_panel_state,
            policy=policy,
            validation_state=validation_state,
            runtime_state=runtime_state,
            guard_feed=guard_feed,
        )
        preview_consumption_rows = build_preview_consumption_report(preview_rows, contract)

        write_csv(OUT_INPUT_CONSUMPTION_CSV, input_rows)
        write_csv(OUT_PREVIEW_CONSUMPTION_CSV, preview_consumption_rows)

        input_pass = all(to_bool(x.get("passed")) for x in input_rows)
        preview_pass = all(to_bool(x.get("passed")) for x in preview_consumption_rows)

        contract_ready = (
            contract.get("contract_status") == "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_CONTRACT_READY"
            and contract.get("research_key") == EXPECTED_RESEARCH_KEY
            and contract.get("plugin_key") == EXPECTED_PLUGIN_KEY
        )
        plugin_ready = plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY and explicitly_blocked(plugin.get("plugin_expansion_allowed"))
        source_panel_exists = source_panel_path.exists()

        if not (contract_ready and plugin_ready and input_pass and preview_pass and source_panel_exists and feature):
            result = {
                **base_result,
                "runner_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_PREREQUISITES_NO_RELEASE",
                "reason": (
                    f"contract_ready={contract_ready}; plugin_ready={plugin_ready}; input_pass={input_pass}; "
                    f"preview_pass={preview_pass}; source_panel_exists={source_panel_exists}; feature_present={bool(feature)}"
                ),
                "input_rows": input_rows,
                "preview_consumption_rows": preview_consumption_rows,
                "release_allowed": False,
                "elapsed_seconds": round(time_module.time() - started, 3),
                **SAFETY_FLAGS,
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        print(f"Reading source panel: {source_panel_path}")
        df = pd.read_parquet(source_panel_path)
        df = df.copy()
        df["month"] = safe_month_from_time(df["time"])
        df["symbol"] = df["symbol"].astype(str)
        df = add_derived_features(df)
        df = df.dropna(subset=["month", "symbol"])

        if feature not in df.columns:
            result = {
                **base_result,
                "runner_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_BLOCKED_PREVIEW_FEATURE_MISSING",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_PREVIEW_FEATURE_OR_DERIVED_FEATURE_BUILDER_NO_RELEASE",
                "reason": f"preview_feature_missing={feature}",
                "release_allowed": False,
                "elapsed_seconds": round(time_module.time() - started, 3),
                **SAFETY_FLAGS,
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        row_count = int(len(df))
        symbol_count = int(df["symbol"].nunique())
        raw_months = sorted(df["month"].dropna().astype(str).unique().tolist())
        raw_calendar_month_count = len(raw_months)
        canonical_months = choose_canonical_months(df, 12)
        canonical_policy_month_count = len(canonical_months)

        df = df[df["month"].isin(canonical_months)].copy()
        df[feature] = pd.to_numeric(df[feature], errors="coerce")
        df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[feature])

        print("Running deep validation tests...")

        month_rows = run_month_holdout(df, feature, side, canonical_months)
        symbol_rows = run_symbol_holdout(df, feature, side, canonical_months)
        threshold_rows = run_threshold_perturbation(df, feature, side, canonical_months)
        noise_rows = run_noise_perturbation(df, feature, side, canonical_months)
        negative_rows = run_negative_controls(df, feature, side, canonical_months)
        leakage_rows = run_leakage_audit(feature, contract, plugin)
        calendar_rows = run_calendar_edge_sensitivity(df, feature, side, canonical_months)

        caps = plugin.get("gate_caps") if isinstance(plugin.get("gate_caps"), dict) else {}
        null_runs = max(1000, to_int(plugin.get("minimum_empirical_null_runs")), to_int(contract.get("minimum_empirical_null_runs")))
        true_null_rows = run_true_null_rerun(df, feature, side, canonical_months, null_runs, caps)

        write_csv(OUT_MONTH_HOLDOUT_CSV, month_rows)
        write_csv(OUT_SYMBOL_HOLDOUT_CSV, symbol_rows)
        write_csv(OUT_THRESHOLD_PERTURB_CSV, threshold_rows)
        write_csv(OUT_NOISE_PERTURB_CSV, noise_rows)
        write_csv(OUT_NEGATIVE_CONTROL_CSV, negative_rows)
        write_csv(OUT_TRUE_NULL_RERUN_CSV, true_null_rows)
        write_csv(OUT_LEAKAGE_AUDIT_CSV, leakage_rows)
        write_csv(OUT_CALENDAR_EDGE_CSV, calendar_rows)

        gate_rows = build_gate_table(
            input_pass=input_pass,
            preview_pass=preview_pass,
            leakage_rows=leakage_rows,
            month_rows=month_rows,
            symbol_rows=symbol_rows,
            threshold_rows=threshold_rows,
            noise_rows=noise_rows,
            negative_rows=negative_rows,
            true_null_rows=true_null_rows,
            calendar_rows=calendar_rows,
            row_count=row_count,
            symbol_count=symbol_count,
            canonical_month_count=canonical_policy_month_count,
        )

        failed_gates = [str(x.get("gate_key")) for x in gate_rows if not to_bool(x.get("passed"))]
        deep_validation_gate_pass = len(failed_gates) == 0

        validation_summaries = [
            summarize_test_rows(month_rows, "month_holdout_stability"),
            summarize_test_rows(symbol_rows, "symbol_holdout_stability"),
            summarize_test_rows(threshold_rows, "feature_threshold_perturbation"),
            summarize_test_rows(noise_rows, "feature_value_noise_perturbation"),
            summarize_test_rows(negative_rows, "negative_controls_rerun"),
            summarize_test_rows(calendar_rows, "calendar_edge_month_sensitivity"),
        ]

        true_null_summary = [r for r in true_null_rows if r.get("run_id") == "SUMMARY"]
        validation_summaries.append({
            "test_key": "true_source_panel_null_rerun",
            "test_count": 1,
            "pass_count": 1 if true_null_summary and to_bool(true_null_summary[0].get("passed")) else 0,
            "fail_count": 0 if true_null_summary and to_bool(true_null_summary[0].get("passed")) else 1,
            "passed": bool(true_null_summary and to_bool(true_null_summary[0].get("passed"))),
        })
        validation_summaries.append({
            "test_key": "leakage_audit",
            "test_count": len(leakage_rows),
            "pass_count": sum(1 for r in leakage_rows if to_bool(r.get("passed"))),
            "fail_count": sum(1 for r in leakage_rows if not to_bool(r.get("passed"))),
            "passed": all(to_bool(r.get("passed")) for r in leakage_rows),
        })

        validation_test_count = len(validation_summaries)
        validation_pass_count = sum(1 for r in validation_summaries if to_bool(r.get("passed")))
        validation_fail_count = validation_test_count - validation_pass_count

        write_csv(OUT_GATE_CSV, gate_rows)
        write_csv(OUT_RESULTS_CSV, validation_summaries)

        if deep_validation_gate_pass:
            runner_status = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_PASS_REVIEW_ONLY_NO_RELEASE"
            next_action = "BUILD_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_EVALUATOR_REVIEW_ONLY_NO_RELEASE"
            reason = (
                f"deep_validation_gate_pass=True; validation_pass_count={validation_pass_count}; "
                f"validation_fail_count={validation_fail_count}; release_allowed=False"
            )
        else:
            runner_status = "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_FAILED_VALIDATION"
            next_action = "BUILD_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_EVALUATOR_CLOSE_OR_REDESIGN_NO_RELEASE"
            reason = (
                f"deep_validation_gate_pass=False; failed_gates={failed_gates}; "
                f"validation_pass_count={validation_pass_count}; validation_fail_count={validation_fail_count}; release_allowed=False"
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
            "deep_validation_gate_pass": deep_validation_gate_pass,
            "deep_validation_gate_fail_count": len(failed_gates),
            "failed_gate_keys": failed_gates,
            "validation_test_count": validation_test_count,
            "validation_pass_count": validation_pass_count,
            "validation_fail_count": validation_fail_count,
            "input_consumption_pass": input_pass,
            "preview_consumption_pass": preview_pass,
            "release_allowed": False,
            "gate_rows": gate_rows,
            "validation_summaries": validation_summaries,
            "release_gate_feed": {
                "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_RAN": True,
                "DEEP_VALIDATION_GATE_PASS": deep_validation_gate_pass,
                "VALIDATION_PASS_COUNT": validation_pass_count,
                "VALIDATION_FAIL_COUNT": validation_fail_count,
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
            "runner_status": "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(exc).__name__}: {exc}",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "release_allowed": False,
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text(OUT_TXT, build_text_summary(result))
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
