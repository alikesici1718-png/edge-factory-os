#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Exit Risk Shape Runner v1

Purpose:
- Read Exit Risk Shape Contract v1.
- Use frozen/pre-outcome diagnostic reference events.
- Test whether exit/hold/MAE/MFE/risk-path shapes improve strict month stability.
- This is NOT candidate generation and NOT a family release.

Safety:
- READ_ONLY_RESEARCH only.
- No runtime touch.
- No launcher.
- No patch_runtime.
- No capital change.
- No active paper.
- No live.
- No real orders.
"""

from __future__ import annotations

import datetime as dt
import json
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "exit_risk_shape_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_exit_risk_shape_runner"
OUT_JSON = OUT_DIR / "exit_risk_shape_runner_latest.json"
OUT_TXT = OUT_DIR / "exit_risk_shape_runner_latest.txt"
OUT_RANKED_CSV = OUT_DIR / "exit_risk_shape_ranked_diagnostics_latest.csv"
OUT_MONTH_CSV = OUT_DIR / "exit_risk_shape_month_diagnostics_latest.csv"
OUT_REFERENCE_CSV = OUT_DIR / "exit_risk_shape_reference_events_latest.csv"

RUNNER_NAME = "edge_factory_os_exit_risk_shape_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "EXIT_RISK_SHAPE_CONTRACT_READY"
REQUIRED_DIRECTION_QUEUE_KEY = "RD4_03_EXIT_AND_RISK_SHAPE_SEARCH_INSTEAD_OF_ENTRY_SEARCH"

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
        raise ValueError(f"Missing required column. Tried={candidates}; available_sample={list(df.columns)[:80]}")
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
        ("okx", 20),
        ("swap", 20),
        ("285", 16),
        ("1y", 16),
        ("feature_panel", 12),
        ("dynamic", 8),
        ("full", 8),
        ("panel", 8),
        ("universe", 6),
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

    for p in contract.get("panel_candidates", []) or []:
        try:
            pp = Path(str(p))
            if pp.exists() and pp.is_file():
                candidates.append(pp)
        except Exception:
            pass

    if candidates:
        return sorted(candidates, key=score_panel_path, reverse=True)[0]

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


def derive_canonical_months(df: pd.DataFrame, canonical_policy_month_count: int) -> List[str]:
    raw_months = sorted([m for m in df["month"].dropna().unique().tolist() if isinstance(m, str)])
    if len(raw_months) <= canonical_policy_month_count:
        return raw_months

    counts = df.groupby("month", observed=True).size().sort_index()
    positive_counts = counts[counts > 0]

    if positive_counts.empty:
        return raw_months[-canonical_policy_month_count:]

    median_count = float(positive_counts.median())
    fullish = counts[counts >= median_count * 0.55].index.tolist()

    if len(fullish) >= canonical_policy_month_count:
        top = counts.loc[fullish].sort_values(ascending=False).head(canonical_policy_month_count).index.tolist()
        return sorted(top)

    return raw_months[-canonical_policy_month_count:]


def forward_rolling_max(series: pd.Series, window: int) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return s.shift(-1).iloc[::-1].rolling(window, min_periods=1).max().iloc[::-1]


def forward_rolling_min(series: pd.Series, window: int) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return s.shift(-1).iloc[::-1].rolling(window, min_periods=1).min().iloc[::-1]


def build_core_panel(raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Optional[str]]]:
    raw = normalize_columns(raw)

    time_col = pick_col(raw, ["time", "timestamp", "datetime", "date", "open_time", "ts"])
    symbol_col = pick_col(raw, ["symbol", "instid", "instrument", "ticker", "coin"])
    close_col = pick_col(raw, ["close", "c", "last", "price", "mark_price"])
    volume_col = pick_col(raw, ["volume", "vol", "quote_volume", "quote_vol", "volume_quote", "turnover"], required=False)
    high_col = pick_col(raw, ["high", "h"], required=False)
    low_col = pick_col(raw, ["low", "l"], required=False)

    keep = [time_col, symbol_col, close_col]
    if volume_col:
        keep.append(volume_col)
    if high_col:
        keep.append(high_col)
    if low_col:
        keep.append(low_col)

    df = raw[keep].copy()

    rename = {time_col: "time", symbol_col: "symbol", close_col: "close"}
    if volume_col:
        rename[volume_col] = "volume"
    if high_col:
        rename[high_col] = "high"
    if low_col:
        rename[low_col] = "low"

    df = df.rename(columns=rename)

    df["time"] = safe_datetime_utc_naive(df["time"])
    df["month"] = safe_month_from_time(df["time"])
    df["symbol"] = df["symbol"].astype(str)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    else:
        df["volume"] = np.nan

    if "high" in df.columns:
        df["high"] = pd.to_numeric(df["high"], errors="coerce")
    else:
        df["high"] = df["close"]

    if "low" in df.columns:
        df["low"] = pd.to_numeric(df["low"], errors="coerce")
    else:
        df["low"] = df["close"]

    df["high"] = df["high"].where(df["high"].notna(), df["close"])
    df["low"] = df["low"].where(df["low"].notna(), df["close"])

    df = df.dropna(subset=["time", "symbol", "close"]).sort_values(["symbol", "time"]).reset_index(drop=True)

    g = df.groupby("symbol", sort=False, observed=True)

    for w in [1, 3, 6, 12, 24]:
        prev = g["close"].shift(w)
        df[f"ret_{w}_bps"] = ((df["close"] / prev) - 1.0) * 10000.0

    for h in [1, 3, 6, 12, 24]:
        fut_close = g["close"].shift(-h)
        df[f"fut_ret_{h}_bps"] = ((fut_close / df["close"]) - 1.0) * 10000.0

    real_range = ((df["high"] - df["low"]) / df["close"]) * 10000.0
    proxy_range = df["ret_1_bps"].abs()
    df["entry_range_bps"] = real_range.where(real_range.notna(), proxy_range)

    df["coin_vol_6_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(6, min_periods=4).std())
    df["coin_vol_12_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(12, min_periods=6).std())

    for w in [3, 6, 12]:
        df[f"mkt_ret_{w}_bps"] = df.groupby("time", sort=False, observed=True)[f"ret_{w}_bps"].transform("mean")
        df[f"rel_ret_{w}_bps"] = df[f"ret_{w}_bps"] - df[f"mkt_ret_{w}_bps"]

    df["quote_liquidity_proxy"] = df["close"] * df["volume"]
    df["log_quote_liquidity_proxy"] = np.log1p(df["quote_liquidity_proxy"].clip(lower=0))
    if df["log_quote_liquidity_proxy"].notna().sum() == 0:
        df["log_quote_liquidity_proxy"] = 0.0

    for col in ["ret_3_bps", "ret_6_bps", "rel_ret_3_bps", "rel_ret_6_bps", "entry_range_bps", "coin_vol_6_bps", "log_quote_liquidity_proxy"]:
        df[f"{col}_rank_pct"] = df.groupby("time", sort=False, observed=True)[col].rank(pct=True)

    df["entry_range_bps_rank_pct"] = df["entry_range_bps_rank_pct"].fillna(0.5)
    df["coin_vol_6_bps_rank_pct"] = df["coin_vol_6_bps_rank_pct"].fillna(0.5)
    df["log_quote_liquidity_proxy_rank_pct"] = df["log_quote_liquidity_proxy_rank_pct"].fillna(1.0)

    # Forward high/low path for MAE/MFE style diagnostics.
    print("Computing forward path high/low for risk-shape diagnostics...")
    for h in [1, 3, 6, 12, 24]:
        df[f"future_high_{h}"] = g["high"].transform(lambda s, hh=h: forward_rolling_max(s, hh))
        df[f"future_low_{h}"] = g["low"].transform(lambda s, hh=h: forward_rolling_min(s, hh))

        df[f"long_mfe_{h}_bps"] = ((df[f"future_high_{h}"] / df["close"]) - 1.0) * 10000.0
        df[f"long_mae_{h}_bps"] = ((df[f"future_low_{h}"] / df["close"]) - 1.0) * 10000.0

        df[f"short_mfe_{h}_bps"] = ((df["close"] / df[f"future_low_{h}"]) - 1.0) * 10000.0
        df[f"short_mae_{h}_bps"] = ((df["close"] / df[f"future_high_{h}"]) - 1.0) * 10000.0

    column_map = {
        "time_col": time_col,
        "symbol_col": symbol_col,
        "close_col": close_col,
        "volume_col": volume_col,
        "high_col": high_col,
        "low_col": low_col,
    }

    return df.replace([np.inf, -np.inf], np.nan), column_map


def build_reference_event_specs() -> List[Dict[str, Any]]:
    """
    Frozen diagnostic reference events.
    These are not candidates and not release routes.
    They are simple pre-outcome reference slices used to ask:
    can exit/risk shape rescue month stability?
    """
    return [
        {
            "reference_id": "REF_LONG_STRONG_REL_LOWVOL",
            "side": "long",
            "rel_rank_min": 0.80,
            "ret_rank_min": 0.65,
            "vol_rank_max": 0.50,
            "range_rank_max": 0.70,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "REF_LONG_STRONG_REL_CALM_RANGE",
            "side": "long",
            "rel_rank_min": 0.75,
            "ret_rank_min": 0.60,
            "vol_rank_max": 0.40,
            "range_rank_max": 0.50,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "REF_LONG_BROAD_MOMENTUM",
            "side": "long",
            "rel_rank_min": 0.70,
            "ret_rank_min": 0.70,
            "vol_rank_max": 0.75,
            "range_rank_max": 0.85,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "REF_SHORT_WEAK_REL_HIGH_RETREV",
            "side": "short",
            "rel_rank_max": 0.20,
            "ret_rank_max": 0.35,
            "vol_rank_max": 0.60,
            "range_rank_max": 0.75,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "REF_SHORT_WEAK_REL_CALM_RANGE",
            "side": "short",
            "rel_rank_max": 0.25,
            "ret_rank_max": 0.40,
            "vol_rank_max": 0.45,
            "range_rank_max": 0.55,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "REF_LONG_LIQUID_TOP_REL",
            "side": "long",
            "rel_rank_min": 0.80,
            "ret_rank_min": 0.55,
            "vol_rank_max": 0.70,
            "range_rank_max": 0.80,
            "liq_rank_min": 0.60,
        },
        {
            "reference_id": "REF_SHORT_LIQUID_BOTTOM_REL",
            "side": "short",
            "rel_rank_max": 0.20,
            "ret_rank_max": 0.45,
            "vol_rank_max": 0.70,
            "range_rank_max": 0.80,
            "liq_rank_min": 0.60,
        },
    ]


def reference_mask(df: pd.DataFrame, spec: Dict[str, Any]) -> pd.Series:
    mask = pd.Series(True, index=df.index)

    if "rel_rank_min" in spec:
        mask &= df["rel_ret_3_bps_rank_pct"] >= float(spec["rel_rank_min"])
    if "rel_rank_max" in spec:
        mask &= df["rel_ret_3_bps_rank_pct"] <= float(spec["rel_rank_max"])

    if "ret_rank_min" in spec:
        mask &= df["ret_3_bps_rank_pct"] >= float(spec["ret_rank_min"])
    if "ret_rank_max" in spec:
        mask &= df["ret_3_bps_rank_pct"] <= float(spec["ret_rank_max"])

    mask &= df["coin_vol_6_bps_rank_pct"] <= float(spec.get("vol_rank_max", 1.0))
    mask &= df["entry_range_bps_rank_pct"] <= float(spec.get("range_rank_max", 1.0))
    mask &= df["log_quote_liquidity_proxy_rank_pct"] >= float(spec.get("liq_rank_min", 0.0))

    required = ["time", "month", "symbol", "close", "ret_3_bps", "rel_ret_3_bps"]
    for c in required:
        mask &= df[c].notna()

    return mask


def build_exit_shape_grid() -> List[Dict[str, Any]]:
    grid: List[Dict[str, Any]] = []

    # Fixed holds.
    for hold in [1, 3, 6, 12, 24]:
        for cost in [25.0, 50.0, 75.0]:
            grid.append({
                "exit_shape_id": f"FIXED_HOLD_{hold}_COST_{int(cost)}",
                "exit_type": "fixed_hold",
                "hold": hold,
                "cost_bps": cost,
            })

    # Conservative TP/SL approximation: if SL and TP both touched, assume SL first.
    for hold in [3, 6, 12, 24]:
        for tp in [50.0, 100.0, 150.0, 250.0]:
            for sl in [50.0, 100.0, 150.0, 250.0]:
                for cost in [50.0, 75.0]:
                    grid.append({
                        "exit_shape_id": f"TP_{int(tp)}_SL_{int(sl)}_HOLD_{hold}_COST_{int(cost)}",
                        "exit_type": "tp_sl_conservative",
                        "hold": hold,
                        "tp_bps": tp,
                        "sl_bps": sl,
                        "cost_bps": cost,
                    })

    # Breakeven after MFE threshold: rough diagnostic approximation.
    for hold in [6, 12, 24]:
        for mfe_trigger in [75.0, 125.0, 200.0]:
            for cost in [50.0, 75.0]:
                grid.append({
                    "exit_shape_id": f"BREAKEVEN_AFTER_MFE_{int(mfe_trigger)}_HOLD_{hold}_COST_{int(cost)}",
                    "exit_type": "breakeven_after_mfe",
                    "hold": hold,
                    "mfe_trigger_bps": mfe_trigger,
                    "cost_bps": cost,
                })

    return grid


def compute_exit_pnl(events: pd.DataFrame, side: str, shape: Dict[str, Any]) -> pd.Series:
    hold = int(shape["hold"])
    cost = float(shape.get("cost_bps", 50.0))

    if side == "long":
        fixed = events[f"fut_ret_{hold}_bps"]
        mfe = events[f"long_mfe_{hold}_bps"]
        mae = events[f"long_mae_{hold}_bps"]
    else:
        fixed = -events[f"fut_ret_{hold}_bps"]
        mfe = events[f"short_mfe_{hold}_bps"]
        mae = events[f"short_mae_{hold}_bps"]

    exit_type = shape["exit_type"]

    if exit_type == "fixed_hold":
        pnl = fixed - cost
        return pnl

    if exit_type == "tp_sl_conservative":
        tp = float(shape["tp_bps"])
        sl = float(shape["sl_bps"])

        hit_tp = mfe >= tp
        hit_sl = mae <= -sl

        pnl = fixed.copy()
        pnl = pnl.where(~hit_tp, tp)
        # Conservative: stop overrides TP when both touched.
        pnl = pnl.where(~hit_sl, -sl)
        pnl = pnl - cost
        return pnl

    if exit_type == "breakeven_after_mfe":
        trigger = float(shape["mfe_trigger_bps"])
        hit_trigger = mfe >= trigger

        # If MFE reaches trigger and fixed exit later loses, assume breakeven minus cost.
        pnl = fixed.copy()
        pnl = pnl.where(~(hit_trigger & (pnl < 0.0)), 0.0)
        pnl = pnl - cost
        return pnl

    return fixed - cost


def evaluate_reference_exit_shape(
    df: pd.DataFrame,
    spec: Dict[str, Any],
    shape: Dict[str, Any],
    canonical_months: List[str],
    canonical_policy_month_count: int,
) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    mask = reference_mask(df, spec)
    event_count = int(mask.sum())

    if event_count < 250:
        return None

    hold = int(shape["hold"])
    needed = [
        "time",
        "month",
        "symbol",
        f"fut_ret_{hold}_bps",
        f"long_mfe_{hold}_bps",
        f"long_mae_{hold}_bps",
        f"short_mfe_{hold}_bps",
        f"short_mae_{hold}_bps",
    ]

    events = df.loc[mask, needed].dropna().copy()
    if events.empty or len(events) < 250:
        return None

    symbol_count = int(events["symbol"].nunique())
    if symbol_count < 20:
        return None

    side = str(spec["side"])
    pnl = compute_exit_pnl(events, side=side, shape=shape)
    events["diagnostic_pnl_bps"] = pnl

    events = events.dropna(subset=["diagnostic_pnl_bps"])
    if events.empty or len(events) < 250:
        return None

    # Equal-weight by timestamp so dense symbol groups do not dominate too much.
    bar = events.groupby(["time", "month"], observed=True)["diagnostic_pnl_bps"].mean().reset_index()
    if len(bar) < 50:
        return None

    month_sum = bar.groupby("month", observed=True)["diagnostic_pnl_bps"].sum().reindex(canonical_months).fillna(0.0)
    month_count = bar.groupby("month", observed=True).size().reindex(canonical_months).fillna(0)

    active_months = int((month_count > 0).sum())
    positive_months = int((month_sum > 0.0).sum())
    total = float(month_sum.sum())

    strict_preview = (
        active_months >= canonical_policy_month_count
        and positive_months >= canonical_policy_month_count
        and total > 0.0
    )

    values = bar["diagnostic_pnl_bps"].to_numpy(dtype=np.float64)

    row = {
        "reference_id": spec["reference_id"],
        "side": side,
        "exit_shape_id": shape["exit_shape_id"],
        "exit_type": shape["exit_type"],
        "hold": int(shape["hold"]),
        "cost_bps": float(shape.get("cost_bps", 0.0)),
        "tp_bps": shape.get("tp_bps"),
        "sl_bps": shape.get("sl_bps"),
        "mfe_trigger_bps": shape.get("mfe_trigger_bps"),
        "event_count": int(len(events)),
        "bar_count": int(len(bar)),
        "symbol_count": symbol_count,
        "active_months": active_months,
        "positive_months": positive_months,
        "canonical_month_count": canonical_policy_month_count,
        "strict_12_exit_shape_preview_pass": bool(strict_preview),
        "total_month_pnl_bps": total,
        "mean_bar_pnl_bps": float(np.mean(values)),
        "median_bar_pnl_bps": float(np.median(values)),
        "bar_win_rate": float(np.mean(values > 0.0)),
        "worst_month_bps": float(month_sum.min()),
        "best_month_bps": float(month_sum.max()),
        "future_used_only_for_exit_diagnostic": True,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
    }

    month_rows: List[Dict[str, Any]] = []
    for month in canonical_months:
        month_rows.append({
            "reference_id": spec["reference_id"],
            "side": side,
            "exit_shape_id": shape["exit_shape_id"],
            "exit_type": shape["exit_type"],
            "hold": int(shape["hold"]),
            "month": month,
            "bar_count": int(month_count.loc[month]),
            "month_pnl_bps": float(month_sum.loc[month]),
            "positive_month": bool(month_sum.loc[month] > 0.0),
        })

    return row, month_rows


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS EXIT RISK SHAPE RUNNER v1")
    lines.append("=" * 100)

    for k in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "strict_policy_key",
        "canonical_policy_month_count",
        "raw_calendar_month_count",
        "symbol_count",
        "row_count",
        "reference_event_count",
        "exit_shape_count",
        "ranked_diagnostic_row_count",
        "strict_12_exit_shape_preview_count",
        "elapsed_seconds",
        "panel_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("TOP EXIT/RISK-SHAPE DIAGNOSTICS")
    lines.append("-" * 100)
    for row in result.get("top_exit_shape_diagnostics", [])[:10]:
        lines.append(
            f"{row.get('reference_id')} {row.get('side')} {row.get('exit_shape_id')} | "
            f"strict12={row.get('strict_12_exit_shape_preview_pass')} | "
            f"positive={row.get('positive_months')}/{row.get('canonical_month_count')} | "
            f"total={row.get('total_month_pnl_bps')} | worst={row.get('worst_month_bps')} | "
            f"events={row.get('event_count')} symbols={row.get('symbol_count')}"
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
        "ranked_diagnostics_csv",
        "month_diagnostics_csv",
        "reference_events_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS EXIT RISK SHAPE RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"reference_event_count: {result.get('reference_event_count')}")
    print(f"exit_shape_count: {result.get('exit_shape_count')}")
    print(f"ranked_diagnostic_row_count: {result.get('ranked_diagnostic_row_count')}")
    print(f"strict_12_exit_shape_preview_count: {result.get('strict_12_exit_shape_preview_count')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('ranked_diagnostics_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_PATH, default={})

    canonical_policy_month_count = int(contract.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "contract_path": str(CONTRACT_PATH),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "research_key": contract.get("research_key"),
        "direction_queue_key": contract.get("direction_queue_key"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "ranked_diagnostics_csv": str(OUT_RANKED_CSV),
        "month_diagnostics_csv": str(OUT_MONTH_CSV),
        "reference_events_csv": str(OUT_REFERENCE_CSV),
        **SAFETY_FLAGS,
    }

    try:
        prerequisite_pass = (
            contract.get("builder_status") == REQUIRED_BUILDER_STATUS
            and contract.get("direction_queue_key") == REQUIRED_DIRECTION_QUEUE_KEY
            and canonical_policy_month_count == 12
        )

        if not prerequisite_pass:
            result = {
                **base_result,
                "runner_status": "EXIT_RISK_SHAPE_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_EXIT_RISK_SHAPE_CONTRACT_NO_RELEASE",
                "reason": (
                    f"builder_status={contract.get('builder_status')}; "
                    f"direction_queue_key={contract.get('direction_queue_key')}; "
                    f"canonical_policy_month_count={canonical_policy_month_count}"
                ),
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
                "runner_status": "EXIT_RISK_SHAPE_RUNNER_BLOCKED_NO_PANEL_FOUND",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "LOCATE_FULL_UNIVERSE_PANEL_AND_RERUN_NO_RELEASE",
                "reason": "No parquet/csv panel found.",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        print(f"Loading panel: {panel_path}")
        raw = read_panel(panel_path)

        print("Building core panel and forward path diagnostics...")
        df, column_map = build_core_panel(raw)

        raw_months = sorted(df["month"].dropna().unique().tolist())
        canonical_months = derive_canonical_months(df, canonical_policy_month_count)

        references = build_reference_event_specs()
        exit_shapes = build_exit_shape_grid()

        ref_rows: List[Dict[str, Any]] = []
        for spec in references:
            m = reference_mask(df, spec)
            ref_rows.append({
                "reference_id": spec["reference_id"],
                "side": spec["side"],
                "event_count": int(m.sum()),
                "symbol_count": int(df.loc[m, "symbol"].nunique()) if int(m.sum()) > 0 else 0,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
            })

        pd.DataFrame(ref_rows).to_csv(OUT_REFERENCE_CSV, index=False)

        print(f"Rows={len(df):,}, symbols={df['symbol'].nunique()}, raw_months={len(raw_months)}, canonical_months={len(canonical_months)}")
        print(f"Reference events={len(references)}, exit shapes={len(exit_shapes)}, evaluations={len(references) * len(exit_shapes)}")

        ranked_rows: List[Dict[str, Any]] = []
        month_rows: List[Dict[str, Any]] = []

        total_jobs = len(references) * len(exit_shapes)
        job_i = 0

        for spec in references:
            for shape in exit_shapes:
                job_i += 1
                out = evaluate_reference_exit_shape(
                    df=df,
                    spec=spec,
                    shape=shape,
                    canonical_months=canonical_months,
                    canonical_policy_month_count=canonical_policy_month_count,
                )

                if out is not None:
                    row, mrows = out
                    ranked_rows.append(row)
                    month_rows.extend(mrows)

                if job_i % 100 == 0 or job_i == total_jobs:
                    print(f"Evaluated {job_i}/{total_jobs} | kept={len(ranked_rows)}")

        ranked = pd.DataFrame(ranked_rows)
        month_diag = pd.DataFrame(month_rows)

        strict_preview_count = 0
        top_exit_shape_diagnostics: List[Dict[str, Any]] = []

        if not ranked.empty:
            strict_preview_count = int(ranked["strict_12_exit_shape_preview_pass"].fillna(False).astype(bool).sum())
            ranked = ranked.sort_values(
                by=[
                    "strict_12_exit_shape_preview_pass",
                    "positive_months",
                    "total_month_pnl_bps",
                    "worst_month_bps",
                    "symbol_count",
                    "event_count",
                ],
                ascending=[False, False, False, False, False, False],
            ).reset_index(drop=True)
            ranked.to_csv(OUT_RANKED_CSV, index=False)
            top_exit_shape_diagnostics = ranked.head(20).to_dict(orient="records")
        else:
            pd.DataFrame().to_csv(OUT_RANKED_CSV, index=False)

        if not month_diag.empty:
            month_diag.to_csv(OUT_MONTH_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_MONTH_CSV, index=False)

        if strict_preview_count > 0:
            runner_status = "EXIT_RISK_SHAPE_RUNNER_STRICT_12_PREVIEW_FOUND_NOT_RELEASE_PASS"
            severity = "ATTENTION"
            next_action = "BUILD_EXIT_RISK_SHAPE_EVALUATOR_AND_DEEP_VALIDATION_KEEP_ACTIONS_BLOCKED"
            reason = (
                f"reference_event_count={len(references)}; exit_shape_count={len(exit_shapes)}; "
                f"ranked_diagnostic_row_count={len(ranked)}; "
                f"strict_12_exit_shape_preview_count={strict_preview_count}; preview_only_not_release"
            )
        else:
            runner_status = "EXIT_RISK_SHAPE_RUNNER_COMPLETE_NO_STRICT_EXIT_SHAPE_PREVIEW"
            severity = "ATTENTION"
            next_action = "BUILD_EXIT_RISK_SHAPE_EVALUATOR_OR_ROTATE_NO_RELEASE"
            reason = (
                f"reference_event_count={len(references)}; exit_shape_count={len(exit_shapes)}; "
                f"ranked_diagnostic_row_count={len(ranked)}; "
                "strict_12_exit_shape_preview_count=0"
            )

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
            "canonical_policy_month_count": canonical_policy_month_count,
            "canonical_policy_months": canonical_months,
            "reference_event_count": int(len(references)),
            "exit_shape_count": int(len(exit_shapes)),
            "reference_event_summary": ref_rows,
            "ranked_diagnostic_row_count": int(len(ranked)),
            "month_diagnostic_row_count": int(len(month_diag)),
            "strict_12_exit_shape_preview_count": int(strict_preview_count),
            "top_exit_shape_diagnostics": top_exit_shape_diagnostics,
            "diagnostic_integrity": {
                "new_entry_signal_search": False,
                "reference_events_are_frozen_diagnostics": True,
                "future_used_for_exit_path_diagnostic": True,
                "future_used_for_candidate_generation": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
            },
            "release_gate_feed": {
                "EXIT_RISK_SHAPE_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "STRICT_12_EXIT_SHAPE_PREVIEW_COUNT": int(strict_preview_count),
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
            "runner_status": "EXIT_RISK_SHAPE_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_EXIT_RISK_SHAPE_RUNNER_ERROR_NO_RELEASE",
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
