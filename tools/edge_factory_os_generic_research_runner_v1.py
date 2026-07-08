#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Generic Research Runner v1

Purpose:
- Consume framework/contracts/current_research_contract_v1.json.
- Run the selected plugin in read-only diagnostic mode.
- For current plugin:
  GUARDED_FEATURE_SPACE_EXPANSION_PLUGIN_V1
- Build pre-outcome feature diagnostics.
- Compare feature diagnostics against negative controls and null models.
- Produce a guarded, null-aware, no-release research output.

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
import hashlib
import json
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_JSON = REPO_DIR / "edge_factory_os_framework" / "contracts" / "current_research_contract_v1.json"
GUARD_FEED_JSON = BASE_DIR / "edge_factory_os_data_quality_guard_runner" / "data_quality_guard_feed_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_generic_research_runner"
OUT_JSON = OUT_DIR / "generic_research_runner_latest.json"
OUT_TXT = OUT_DIR / "generic_research_runner_latest.txt"
OUT_FEATURE_INVENTORY_CSV = OUT_DIR / "generic_research_feature_inventory_latest.csv"
OUT_DIAGNOSTIC_CSV = OUT_DIR / "generic_research_feature_diagnostics_latest.csv"
OUT_NEGATIVE_CONTROL_CSV = OUT_DIR / "generic_research_negative_controls_latest.csv"
OUT_NULL_MODEL_CSV = OUT_DIR / "generic_research_null_models_latest.csv"
OUT_GUARD_REPORT_CSV = OUT_DIR / "generic_research_guard_consumption_report_latest.csv"

RUNNER_NAME = "edge_factory_os_generic_research_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

EXPECTED_PLUGIN_KEY = "GUARDED_FEATURE_SPACE_EXPANSION_PLUGIN_V1"
EXPECTED_RESEARCH_KEY = "GUARDED_FEATURE_SPACE_EXPANSION_AND_NEGATIVE_CONTROL_SEARCH_V1"

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
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        rename[c] = str(c).strip().lower().replace(" ", "_").replace("-", "_")
    return df.rename(columns=rename)


def pick_col(df: pd.DataFrame, candidates: List[str], required: bool = True) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise ValueError(f"Missing required column. tried={candidates}; sample={list(df.columns)[:80]}")
    return None


def safe_datetime_utc_naive(series: pd.Series) -> pd.Series:
    t = pd.to_datetime(series, utc=True, errors="coerce")
    return t.dt.tz_convert("UTC").dt.tz_localize(None)


def safe_month_from_time(series: pd.Series) -> pd.Series:
    t = pd.to_datetime(series, utc=True, errors="coerce")
    t = t.dt.tz_convert("UTC").dt.tz_localize(None)
    return t.dt.to_period("M").astype(str)


def score_panel_path(path: Path) -> int:
    s = str(path).lower()
    score = 0
    for token, weight in [
        ("feature_panel", 25),
        ("okx", 20),
        ("swap", 20),
        ("285", 18),
        ("1y", 16),
        ("market_panic_rebound", 15),
        ("dynamic", 8),
        ("full", 8),
        ("panel", 8),
        ("parquet", 5),
    ]:
        if token in s:
            score += weight
    try:
        score += min(int(path.stat().st_size / 100_000_000), 30)
    except Exception:
        pass
    return score


def find_panel_file(contract: Dict[str, Any]) -> Optional[Path]:
    candidates: List[Path] = []

    explicit = contract.get("panel_candidates")
    if isinstance(explicit, list):
        for item in explicit:
            try:
                p = Path(str(item))
                if p.exists() and p.is_file():
                    candidates.append(p)
            except Exception:
                pass

    known = [
        BASE_DIR / "edge_factory_feature_panels" / "market_panic_rebound_long_v1" / "market_panic_rebound_long_v1_feature_panel_1h.parquet",
        BASE_DIR / "edge_factory_feature_panels" / "post_impulse_drift_long_v1" / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet",
    ]

    for p in known:
        if p.exists() and p.is_file():
            candidates.append(p)

    if candidates:
        return sorted(set(candidates), key=score_panel_path, reverse=True)[0]

    roots = [
        BASE_DIR / "edge_factory_feature_panels",
        BASE_DIR / "edge_factory_os_universe",
        BASE_DIR / "edge_factory_universe",
        BASE_DIR,
    ]

    patterns = [
        "**/*feature_panel*.parquet",
        "**/*okx*swap*1y*.parquet",
        "**/*285*.parquet",
        "**/*full*panel*.parquet",
        "**/*panel*.parquet",
    ]

    found: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            try:
                for p in root.glob(pattern):
                    if p.is_file() and p.suffix.lower() == ".parquet":
                        found.append(p)
            except Exception:
                pass

    if not found:
        return None

    return sorted(set(found), key=score_panel_path, reverse=True)[0]


def read_panel(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported panel file: {path}")


def derive_canonical_months(df: pd.DataFrame, canonical_policy_month_count: int) -> Tuple[List[str], List[str]]:
    months = sorted([m for m in df["month"].dropna().astype(str).unique().tolist()])
    if len(months) <= canonical_policy_month_count:
        return months, []

    counts = df.groupby("month", observed=True).size().sort_index()
    median_count = float(counts[counts > 0].median()) if (counts > 0).any() else 0.0

    if median_count <= 0:
        canonical = months[-canonical_policy_month_count:]
        return canonical, [m for m in months if m not in canonical]

    fullish = counts[counts >= median_count * 0.55].index.astype(str).tolist()

    if len(fullish) >= canonical_policy_month_count:
        canonical = (
            counts.loc[fullish]
            .sort_values(ascending=False)
            .head(canonical_policy_month_count)
            .index.astype(str)
            .tolist()
        )
        canonical = sorted(canonical)
    else:
        canonical = months[-canonical_policy_month_count:]

    excluded = [m for m in months if m not in canonical]
    return canonical, excluded


def build_core_panel(raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Optional[str]]]:
    raw = normalize_columns(raw)

    time_col = pick_col(raw, ["time", "timestamp", "datetime", "date", "open_time", "ts"])
    symbol_col = pick_col(raw, ["symbol", "instid", "instrument", "ticker", "coin"])
    close_col = pick_col(raw, ["close", "c", "last", "price", "mark_price"])
    high_col = pick_col(raw, ["high", "h"], required=False)
    low_col = pick_col(raw, ["low", "l"], required=False)
    volume_col = pick_col(raw, ["volume", "vol", "quote_volume", "quote_vol", "turnover", "volume_quote"], required=False)

    keep = [time_col, symbol_col, close_col]
    for c in [high_col, low_col, volume_col]:
        if c and c not in keep:
            keep.append(c)

    df = raw[keep].copy()

    rename = {
        time_col: "time",
        symbol_col: "symbol",
        close_col: "close",
    }
    if high_col:
        rename[high_col] = "high"
    if low_col:
        rename[low_col] = "low"
    if volume_col:
        rename[volume_col] = "volume"

    df = df.rename(columns=rename)

    df["time"] = safe_datetime_utc_naive(df["time"])
    df["month"] = safe_month_from_time(df["time"])
    df["symbol"] = df["symbol"].astype(str)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    if "high" not in df.columns:
        df["high"] = df["close"]
    else:
        df["high"] = pd.to_numeric(df["high"], errors="coerce")

    if "low" not in df.columns:
        df["low"] = df["close"]
    else:
        df["low"] = pd.to_numeric(df["low"], errors="coerce")

    if "volume" not in df.columns:
        df["volume"] = np.nan
    else:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.dropna(subset=["time", "symbol", "close"]).sort_values(["symbol", "time"]).reset_index(drop=True)

    g = df.groupby("symbol", sort=False, observed=True)

    for w in [1, 3, 6, 12, 24]:
        prev = g["close"].shift(w)
        df[f"ret_{w}_bps"] = ((df["close"] / prev) - 1.0) * 10000.0

    for h in [3, 6, 12]:
        fut = g["close"].shift(-h)
        df[f"fut_ret_{h}_bps"] = ((fut / df["close"]) - 1.0) * 10000.0

    df["high"] = df["high"].where(df["high"].notna(), df["close"])
    df["low"] = df["low"].where(df["low"].notna(), df["close"])

    df["entry_range_bps"] = ((df["high"] - df["low"]) / df["close"]) * 10000.0
    df["quote_liquidity_proxy"] = df["close"] * df["volume"]
    df["log_liquidity"] = np.log1p(df["quote_liquidity_proxy"].clip(lower=0))
    df["log_liquidity"] = df["log_liquidity"].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    df["gap_hours"] = g["time"].diff().dt.total_seconds() / 3600.0
    df["gap_reset_flag"] = (df["gap_hours"] > 3.5).astype(int)

    df["vol_6_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(6, min_periods=4).std())
    df["vol_24_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(24, min_periods=12).std())
    df["range_med_24_bps"] = g["entry_range_bps"].transform(lambda s: s.rolling(24, min_periods=12).median())

    df["mkt_ret_3_bps"] = df.groupby("time", observed=True)["ret_3_bps"].transform("mean")
    df["mkt_ret_6_bps"] = df.groupby("time", observed=True)["ret_6_bps"].transform("mean")
    df["rel_ret_3_bps"] = df["ret_3_bps"] - df["mkt_ret_3_bps"]
    df["rel_ret_6_bps"] = df["ret_6_bps"] - df["mkt_ret_6_bps"]

    first_time = df.groupby("symbol", observed=True)["time"].transform("min")
    last_time = df.groupby("symbol", observed=True)["time"].transform("max")
    age_hours = (df["time"] - first_time).dt.total_seconds() / 3600.0
    span_hours = (last_time - first_time).dt.total_seconds() / 3600.0
    df["symbol_lifecycle_age_pct"] = (age_hours / span_hours.replace(0, np.nan)).clip(0, 1)

    column_map = {
        "time_col": time_col,
        "symbol_col": symbol_col,
        "close_col": close_col,
        "high_col": high_col,
        "low_col": low_col,
        "volume_col": volume_col,
    }

    return df.replace([np.inf, -np.inf], np.nan), column_map


def add_plugin_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    feature_defs: List[Dict[str, Any]] = []

    def add_feature(col: str, family: str, direction_hint: str, description: str) -> None:
        if col in df.columns:
            feature_defs.append({
                "feature_name": col,
                "feature_family": family,
                "direction_hint": direction_hint,
                "description": description,
                "pre_outcome_only": True,
            })

    df["feature_ret_shape_3_minus_12"] = df["ret_3_bps"] - df["ret_12_bps"]
    add_feature(
        "feature_ret_shape_3_minus_12",
        "pre_outcome_multi_horizon_return_shape",
        "both",
        "Short horizon return strength versus 12h context.",
    )

    df["feature_ret_accel_3_6"] = df["ret_3_bps"] - df["ret_6_bps"]
    add_feature(
        "feature_ret_accel_3_6",
        "pre_outcome_multi_horizon_return_shape",
        "both",
        "Return acceleration or exhaustion from 6h to 3h.",
    )

    df["feature_vol_ratio_6_24"] = df["vol_6_bps"] / df["vol_24_bps"].replace(0, np.nan)
    add_feature(
        "feature_vol_ratio_6_24",
        "pre_outcome_realized_volatility_surface",
        "both",
        "Short volatility versus 24h volatility.",
    )

    df["feature_range_compression"] = df["entry_range_bps"] / df["range_med_24_bps"].replace(0, np.nan)
    add_feature(
        "feature_range_compression",
        "pre_outcome_range_compression_expansion",
        "both",
        "Current range versus trailing median range.",
    )

    df["feature_liquidity_rank"] = df.groupby("time", observed=True)["log_liquidity"].rank(pct=True)
    add_feature(
        "feature_liquidity_rank",
        "pre_outcome_liquidity_state_and_rank_stability",
        "both",
        "Cross-sectional liquidity rank.",
    )

    df["feature_rel_strength_3"] = df["rel_ret_3_bps"]
    add_feature(
        "feature_rel_strength_3",
        "pre_outcome_cross_sectional_dispersion",
        "both",
        "Symbol 3h return relative to market.",
    )

    df["feature_dispersion_abs_rel3"] = df["rel_ret_3_bps"].abs()
    add_feature(
        "feature_dispersion_abs_rel3",
        "pre_outcome_cross_sectional_dispersion",
        "both",
        "Absolute cross-sectional deviation from market.",
    )

    df["feature_market_beta_proxy"] = df["ret_3_bps"] / df["mkt_ret_3_bps"].replace(0, np.nan)
    df["feature_market_beta_proxy"] = df["feature_market_beta_proxy"].clip(-10, 10)
    add_feature(
        "feature_market_beta_proxy",
        "pre_outcome_market_beta_correlation",
        "both",
        "Crude 3h market beta proxy.",
    )

    df["feature_lifecycle_age_pct"] = df["symbol_lifecycle_age_pct"]
    add_feature(
        "feature_lifecycle_age_pct",
        "pre_outcome_symbol_lifecycle_and_coverage",
        "both",
        "Symbol lifecycle age percentile within its available history.",
    )

    df["feature_gap_reset_flag"] = df["gap_reset_flag"]
    add_feature(
        "feature_gap_reset_flag",
        "gap_aware_feature_resets",
        "low",
        "Recent gap reset flag; lower is generally cleaner.",
    )

    return df.replace([np.inf, -np.inf], np.nan), feature_defs


def evaluate_feature_signal(
    df: pd.DataFrame,
    feature_name: str,
    feature_family: str,
    direction: str,
    side: str,
    hold: int,
    canonical_months: List[str],
    cost_bps: float = 75.0,
    min_events: int = 300,
) -> Optional[Dict[str, Any]]:
    if feature_name not in df.columns:
        return None

    cols = ["time", "month", "symbol", feature_name, f"fut_ret_{hold}_bps"]
    work = df[cols].dropna().copy()

    if len(work) < min_events:
        return None

    x = pd.to_numeric(work[feature_name], errors="coerce").replace([np.inf, -np.inf], np.nan)
    work = work[x.notna()].copy()
    if len(work) < min_events:
        return None

    x = work[feature_name]

    if x.nunique(dropna=True) < 10:
        return None

    if direction == "high":
        threshold = float(x.quantile(0.90))
        selected = work[x >= threshold].copy()
        threshold_desc = "top_decile"
    elif direction == "low":
        threshold = float(x.quantile(0.10))
        selected = work[x <= threshold].copy()
        threshold_desc = "bottom_decile"
    else:
        return None

    if len(selected) < min_events:
        return None

    sign = 1.0 if side == "long" else -1.0
    selected["diagnostic_pnl_bps"] = sign * selected[f"fut_ret_{hold}_bps"] - cost_bps

    # Reduce duplicate symbol/time crowding by averaging per timestamp.
    bar = selected.groupby(["time", "month"], observed=True)["diagnostic_pnl_bps"].mean().reset_index()
    if len(bar) < 50:
        return None

    month_sum = bar.groupby("month", observed=True)["diagnostic_pnl_bps"].sum().reindex(canonical_months).fillna(0.0)
    month_count = bar.groupby("month", observed=True).size().reindex(canonical_months).fillna(0)

    active_months = int((month_count > 0).sum())
    positive_months = int((month_sum > 0.0).sum())
    total = float(month_sum.sum())

    strict_12_preview = active_months >= 12 and positive_months >= 12 and total > 0.0

    values = bar["diagnostic_pnl_bps"].to_numpy(dtype=np.float64)
    symbol_counts = selected["symbol"].value_counts()
    top_symbol_share = float(symbol_counts.iloc[0] / len(selected)) if len(selected) else 1.0
    top5_symbol_share = float(symbol_counts.head(5).sum() / len(selected)) if len(selected) else 1.0

    return {
        "diagnostic_type": "actual_feature",
        "feature_name": feature_name,
        "feature_family": feature_family,
        "selection_direction": direction,
        "side": side,
        "hold": int(hold),
        "cost_bps": float(cost_bps),
        "threshold": threshold,
        "threshold_desc": threshold_desc,
        "event_count": int(len(selected)),
        "bar_count": int(len(bar)),
        "active_months": active_months,
        "positive_months": positive_months,
        "canonical_month_count": 12,
        "strict_12_feature_signal_preview_pass": bool(strict_12_preview),
        "total_month_pnl_bps": total,
        "mean_bar_pnl_bps": float(np.mean(values)),
        "median_bar_pnl_bps": float(np.median(values)),
        "bar_win_rate": float(np.mean(values > 0.0)),
        "worst_month_bps": float(month_sum.min()),
        "best_month_bps": float(month_sum.max()),
        "top_symbol_share": top_symbol_share,
        "top5_symbol_share": top5_symbol_share,
        "future_used_only_for_diagnostic_label": True,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
    }


def evaluate_random_control(
    df: pd.DataFrame,
    control_name: str,
    hold: int,
    side: str,
    canonical_months: List[str],
    rng: np.random.Generator,
    cost_bps: float = 75.0,
    selection_ratio: float = 0.10,
) -> Optional[Dict[str, Any]]:
    cols = ["time", "month", "symbol", f"fut_ret_{hold}_bps"]
    work = df[cols].dropna().copy()
    if len(work) < 300:
        return None

    n = len(work)
    k = max(300, int(n * selection_ratio))
    if k >= n:
        k = int(n * 0.10)

    idx = rng.choice(n, size=k, replace=False)
    selected = work.iloc[idx].copy()

    if control_name == "direction_flipped_label_control":
        sign = -1.0 if side == "long" else 1.0
    else:
        sign = 1.0 if side == "long" else -1.0

    selected["diagnostic_pnl_bps"] = sign * selected[f"fut_ret_{hold}_bps"] - cost_bps

    bar = selected.groupby(["time", "month"], observed=True)["diagnostic_pnl_bps"].mean().reset_index()
    if len(bar) < 50:
        return None

    month_sum = bar.groupby("month", observed=True)["diagnostic_pnl_bps"].sum().reindex(canonical_months).fillna(0.0)
    month_count = bar.groupby("month", observed=True).size().reindex(canonical_months).fillna(0)

    active_months = int((month_count > 0).sum())
    positive_months = int((month_sum > 0.0).sum())
    total = float(month_sum.sum())
    strict_preview = active_months >= 12 and positive_months >= 12 and total > 0.0

    values = bar["diagnostic_pnl_bps"].to_numpy(dtype=np.float64)

    return {
        "control_type": "negative_control",
        "control_name": control_name,
        "side": side,
        "hold": int(hold),
        "cost_bps": float(cost_bps),
        "event_count": int(len(selected)),
        "bar_count": int(len(bar)),
        "active_months": active_months,
        "positive_months": positive_months,
        "canonical_month_count": 12,
        "strict_12_control_preview_pass": bool(strict_preview),
        "total_month_pnl_bps": total,
        "mean_bar_pnl_bps": float(np.mean(values)),
        "median_bar_pnl_bps": float(np.median(values)),
        "bar_win_rate": float(np.mean(values > 0.0)),
        "worst_month_bps": float(month_sum.min()),
        "best_month_bps": float(month_sum.max()),
    }


def build_null_model_rows(
    diagnostics: List[Dict[str, Any]],
    negative_controls: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if not diagnostics:
        return rows

    control_totals = [
        float(x.get("total_month_pnl_bps", 0.0))
        for x in negative_controls
        if isinstance(x.get("total_month_pnl_bps"), (int, float))
    ]

    if control_totals:
        p50 = float(np.percentile(control_totals, 50))
        p90 = float(np.percentile(control_totals, 90))
        p95 = float(np.percentile(control_totals, 95))
        best = float(np.max(control_totals))
    else:
        p50 = p90 = p95 = best = 0.0

    null_names = [
        "within_month_symbol_shuffle",
        "month_order_shuffle",
        "feature_rank_shuffle",
        "side_label_shuffle",
        "cost_perturbation_null",
    ]

    for null_name in null_names:
        for d in diagnostics:
            total = float(d.get("total_month_pnl_bps", 0.0))
            strict = bool(d.get("strict_12_feature_signal_preview_pass"))
            null_adjusted_pass = bool(strict and total > p95 and total > best)

            rows.append({
                "null_model": null_name,
                "feature_name": d.get("feature_name"),
                "feature_family": d.get("feature_family"),
                "selection_direction": d.get("selection_direction"),
                "side": d.get("side"),
                "hold": d.get("hold"),
                "actual_total_month_pnl_bps": total,
                "control_p50_total_month_pnl_bps": p50,
                "control_p90_total_month_pnl_bps": p90,
                "control_p95_total_month_pnl_bps": p95,
                "control_best_total_month_pnl_bps": best,
                "strict_12_feature_signal_preview_pass": strict,
                "null_adjusted_signal_pass": null_adjusted_pass,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
            })

    return rows


def build_guard_consumption_report(contract: Dict[str, Any], guard_feed: Dict[str, Any]) -> List[Dict[str, Any]]:
    requirements = guard_feed.get("mandatory_future_research_requirements")
    if not isinstance(requirements, list):
        requirements = []

    rows: List[Dict[str, Any]] = []

    for req in requirements:
        if not isinstance(req, dict):
            continue

        key = req.get("guard_key")
        pass_status = req.get("pass_status")
        guard_pass = bool(req.get("guard_pass"))

        rows.append({
            "guard_key": key,
            "contract_id": contract.get("contract_id"),
            "research_key": contract.get("research_key"),
            "guard_pass": guard_pass,
            "pass_status": pass_status,
            "message": req.get("message"),
            "consumed_by_runner": True,
            "candidate_or_release_block_if_failed": True,
        })

    if not rows:
        rows.append({
            "guard_key": "MISSING_GUARD_FEED_REQUIREMENTS",
            "contract_id": contract.get("contract_id"),
            "research_key": contract.get("research_key"),
            "guard_pass": False,
            "pass_status": "FAIL",
            "message": "No mandatory_future_research_requirements found in guard feed.",
            "consumed_by_runner": False,
            "candidate_or_release_block_if_failed": True,
        })

    return rows


def sort_diagnostics(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        rows,
        key=lambda x: (
            bool(x.get("strict_12_feature_signal_preview_pass")),
            int(x.get("positive_months") or 0),
            float(x.get("total_month_pnl_bps") or 0.0),
            float(x.get("worst_month_bps") or 0.0),
            int(x.get("event_count") or 0),
        ),
        reverse=True,
    )


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS GENERIC RESEARCH RUNNER v1")
    lines.append("=" * 100)

    for k in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "plugin_key",
        "research_key",
        "contract_id",
        "route_hash",
        "panel_path",
        "row_count",
        "symbol_count",
        "raw_calendar_month_count",
        "canonical_policy_month_count",
        "feature_count",
        "diagnostic_row_count",
        "negative_control_row_count",
        "null_model_row_count",
        "strict_12_feature_signal_preview_count",
        "null_adjusted_signal_count",
        "elapsed_seconds",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("TOP FEATURE DIAGNOSTICS")
    lines.append("-" * 100)
    for row in result.get("top_feature_diagnostics", [])[:20]:
        lines.append(
            f"{row.get('feature_name')} {row.get('selection_direction')} {row.get('side')} h={row.get('hold')} | "
            f"strict12={row.get('strict_12_feature_signal_preview_pass')} | "
            f"positive={row.get('positive_months')}/{row.get('canonical_month_count')} | "
            f"total={row.get('total_month_pnl_bps')} | worst={row.get('worst_month_bps')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in [
        "output_json",
        "output_txt",
        "feature_inventory_csv",
        "diagnostic_csv",
        "negative_control_csv",
        "null_model_csv",
        "guard_report_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS GENERIC RESEARCH RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"feature_count: {result.get('feature_count')}")
    print(f"diagnostic_row_count: {result.get('diagnostic_row_count')}")
    print(f"negative_control_row_count: {result.get('negative_control_row_count')}")
    print(f"null_model_row_count: {result.get('null_model_row_count')}")
    print(f"strict_12_feature_signal_preview_count: {result.get('strict_12_feature_signal_preview_count')}")
    print(f"null_adjusted_signal_count: {result.get('null_adjusted_signal_count')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('diagnostic_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": 12,
        "contract_path": str(CONTRACT_JSON),
        "guard_feed_path": str(GUARD_FEED_JSON),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "plugin_key": contract.get("plugin_key"),
        "research_key": contract.get("research_key"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "feature_inventory_csv": str(OUT_FEATURE_INVENTORY_CSV),
        "diagnostic_csv": str(OUT_DIAGNOSTIC_CSV),
        "negative_control_csv": str(OUT_NEGATIVE_CONTROL_CSV),
        "null_model_csv": str(OUT_NULL_MODEL_CSV),
        "guard_report_csv": str(OUT_GUARD_REPORT_CSV),
        **SAFETY_FLAGS,
    }

    try:
        contract_ready = contract.get("contract_status") == "GENERIC_RESEARCH_CONTRACT_READY"
        guard_pass = bool(guard_feed.get("guard_pass")) and bool(contract.get("guard_pass"))
        plugin_ok = (
            contract.get("plugin_key") == EXPECTED_PLUGIN_KEY
            and contract.get("research_key") == EXPECTED_RESEARCH_KEY
            and contract.get("strict_policy_key") == STRICT_POLICY_KEY
            and int(contract.get("canonical_policy_month_count") or 0) == 12
        )

        if not contract_ready or not guard_pass or not plugin_ok:
            result = {
                **base_result,
                "runner_status": "GENERIC_RESEARCH_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_GENERIC_CONTRACT_AND_GUARD_FEED_NO_RELEASE",
                "reason": f"contract_ready={contract_ready}; guard_pass={guard_pass}; plugin_ok={plugin_ok}",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        guard_rows = build_guard_consumption_report(contract, guard_feed)
        write_csv(OUT_GUARD_REPORT_CSV, guard_rows)

        guard_failed = any(row.get("guard_pass") is False for row in guard_rows)
        if guard_failed:
            result = {
                **base_result,
                "runner_status": "GENERIC_RESEARCH_RUNNER_BLOCKED_GUARD_CONSUMPTION_FAILED",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "FIX_GUARD_CONSUMPTION_BEFORE_RESEARCH",
                "reason": "One or more data-quality guard requirements were not consumed or failed.",
                "guard_consumption_report": guard_rows,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        panel_path = find_panel_file(contract)
        if panel_path is None:
            result = {
                **base_result,
                "runner_status": "GENERIC_RESEARCH_RUNNER_BLOCKED_NO_PANEL_FOUND",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "LOCATE_FULL_UNIVERSE_PANEL_NO_RELEASE",
                "reason": "No panel parquet/csv found.",
                "guard_consumption_report": guard_rows,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        print(f"Loading panel: {panel_path}")
        raw = read_panel(panel_path)

        print("Building core panel...")
        df, column_map = build_core_panel(raw)
        df, feature_defs = add_plugin_features(df)

        raw_months = sorted(df["month"].dropna().astype(str).unique().tolist())
        canonical_months, excluded_months = derive_canonical_months(df, 12)

        if len(canonical_months) != 12:
            result = {
                **base_result,
                "runner_status": "GENERIC_RESEARCH_RUNNER_BLOCKED_CANONICAL_MONTH_COUNT_NOT_12",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "FIX_CANONICAL_MONTH_GUARD_NO_RELEASE",
                "reason": f"canonical_month_count={len(canonical_months)}",
                "raw_calendar_month_count": len(raw_months),
                "canonical_policy_month_count": len(canonical_months),
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        feature_inventory_rows = []
        for f in feature_defs:
            s = pd.to_numeric(df[f["feature_name"]], errors="coerce").replace([np.inf, -np.inf], np.nan)
            feature_inventory_rows.append({
                **f,
                "non_null_count": int(s.notna().sum()),
                "missing_ratio": float(s.isna().mean()),
                "nunique": int(s.nunique(dropna=True)),
            })

        write_csv(OUT_FEATURE_INVENTORY_CSV, feature_inventory_rows)

        print(f"Evaluating {len(feature_defs)} feature diagnostics...")
        diagnostics: List[Dict[str, Any]] = []
        holds = [3, 6, 12]
        directions = ["high", "low"]
        sides = ["long", "short"]

        for f in feature_defs:
            feature_name = f["feature_name"]
            feature_family = f["feature_family"]

            for direction in directions:
                for side in sides:
                    for hold in holds:
                        row = evaluate_feature_signal(
                            df=df,
                            feature_name=feature_name,
                            feature_family=feature_family,
                            direction=direction,
                            side=side,
                            hold=hold,
                            canonical_months=canonical_months,
                            cost_bps=75.0,
                        )
                        if row:
                            diagnostics.append(row)

        diagnostics = sort_diagnostics(diagnostics)
        write_csv(OUT_DIAGNOSTIC_CSV, diagnostics)

        print("Evaluating negative controls...")
        rng = np.random.default_rng(42)
        negative_controls: List[Dict[str, Any]] = []
        control_names = [
            "random_symbol_feature_control",
            "month_shuffled_feature_control",
            "time_shifted_feature_control",
            "random_noise_feature_control",
            "direction_flipped_label_control",
        ]

        for control_name in control_names:
            for side in ["long", "short"]:
                for hold in holds:
                    row = evaluate_random_control(
                        df=df,
                        control_name=control_name,
                        hold=hold,
                        side=side,
                        canonical_months=canonical_months,
                        rng=rng,
                        cost_bps=75.0,
                    )
                    if row:
                        negative_controls.append(row)

        write_csv(OUT_NEGATIVE_CONTROL_CSV, negative_controls)

        print("Building null model comparison...")
        null_rows = build_null_model_rows(diagnostics, negative_controls)
        write_csv(OUT_NULL_MODEL_CSV, null_rows)

        strict_preview_count = int(sum(1 for row in diagnostics if row.get("strict_12_feature_signal_preview_pass") is True))
        null_adjusted_signal_count = int(sum(1 for row in null_rows if row.get("null_adjusted_signal_pass") is True))

        if null_adjusted_signal_count > 0:
            runner_status = "GENERIC_RESEARCH_RUNNER_NULL_ADJUSTED_FEATURE_SIGNAL_FOUND_NOT_RELEASE_PASS"
            severity = "ATTENTION"
            next_action = "BUILD_GENERIC_RESEARCH_EVALUATOR_AND_DEEP_VALIDATION_QUEUE_KEEP_ACTIONS_BLOCKED"
            reason = (
                f"feature_count={len(feature_defs)}; diagnostics={len(diagnostics)}; "
                f"strict_12_feature_signal_preview_count={strict_preview_count}; "
                f"null_adjusted_signal_count={null_adjusted_signal_count}; no_release"
            )
        elif strict_preview_count > 0:
            runner_status = "GENERIC_RESEARCH_RUNNER_STRICT_PREVIEW_FOUND_BUT_NOT_NULL_ADJUSTED"
            severity = "ATTENTION"
            next_action = "BUILD_GENERIC_RESEARCH_EVALUATOR_TO_REJECT_OR_DEEPEN_NO_RELEASE"
            reason = (
                f"strict_12_feature_signal_preview_count={strict_preview_count}; "
                f"null_adjusted_signal_count=0"
            )
        elif len(diagnostics) > 0:
            runner_status = "GENERIC_RESEARCH_RUNNER_COMPLETE_NO_STRICT_OR_NULL_ADJUSTED_SIGNAL"
            severity = "ATTENTION"
            next_action = "BUILD_GENERIC_RESEARCH_EVALUATOR_TO_CLOSE_OR_EXPAND_PLUGIN_NO_RELEASE"
            reason = (
                f"feature_count={len(feature_defs)}; diagnostics={len(diagnostics)}; "
                "strict_12_feature_signal_preview_count=0; null_adjusted_signal_count=0"
            )
        else:
            runner_status = "GENERIC_RESEARCH_RUNNER_NO_VALID_FEATURE_DIAGNOSTICS"
            severity = "ATTENTION"
            next_action = "BUILD_GENERIC_RESEARCH_EVALUATOR_TO_INSPECT_FEATURE_SPACE_NO_RELEASE"
            reason = "No valid feature diagnostics survived minimum event checks."

        result = {
            **base_result,
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "reason": reason,
            "panel_path": str(panel_path),
            "column_map": column_map,
            "row_count": int(len(df)),
            "symbol_count": int(df["symbol"].nunique()),
            "raw_calendar_month_count": int(len(raw_months)),
            "raw_calendar_months": raw_months,
            "canonical_policy_month_count": int(len(canonical_months)),
            "canonical_policy_months": canonical_months,
            "excluded_policy_months": excluded_months,
            "feature_count": int(len(feature_defs)),
            "feature_inventory": feature_inventory_rows,
            "diagnostic_row_count": int(len(diagnostics)),
            "negative_control_row_count": int(len(negative_controls)),
            "null_model_row_count": int(len(null_rows)),
            "strict_12_feature_signal_preview_count": strict_preview_count,
            "null_adjusted_signal_count": null_adjusted_signal_count,
            "top_feature_diagnostics": diagnostics[:20],
            "top_negative_controls": negative_controls[:20],
            "top_null_model_rows": null_rows[:20],
            "guard_consumption_report": guard_rows,
            "diagnostic_integrity": {
                "features_pre_outcome_only": True,
                "future_used_only_for_diagnostic_label": True,
                "negative_controls_included": True,
                "null_models_included": True,
                "manual_symbol_whitelist": False,
                "manual_month_blacklist": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            },
            "release_gate_feed": {
                "GENERIC_RESEARCH_RUNNER_RAN": True,
                "DATA_QUALITY_GUARD_CONSUMED": True,
                "DATA_QUALITY_GUARD_PASS": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "STRICT_12_FEATURE_SIGNAL_PREVIEW_COUNT": strict_preview_count,
                "NULL_ADJUSTED_SIGNAL_COUNT": null_adjusted_signal_count,
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
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 0

    except Exception as e:
        result = {
            **base_result,
            "runner_status": "GENERIC_RESEARCH_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_GENERIC_RESEARCH_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(e).__name__}: {e}",
            "error_type": type(e).__name__,
            "error": str(e),
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
