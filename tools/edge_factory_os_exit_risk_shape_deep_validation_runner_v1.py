#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Exit Risk Shape Deep Validation Runner v1

Purpose:
- Consume Exit Risk Shape Deep Validation Contract v1.
- Replay strict 12/12 exit-shape preview rows independently.
- Validate route hash, full-universe replay, rolling/OOS, cost/slippage,
  concentration, month stability, and MAE/MFE path sanity.
- Keep all action flags blocked.

This runner does NOT:
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "exit_risk_shape_deep_validation_contract_latest.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_exit_risk_shape_deep_validation_runner"
OUT_JSON = OUT_DIR / "exit_risk_shape_deep_validation_runner_latest.json"
OUT_TXT = OUT_DIR / "exit_risk_shape_deep_validation_runner_latest.txt"
OUT_VALIDATION_CSV = OUT_DIR / "exit_risk_shape_deep_validation_results_latest.csv"
OUT_MONTH_CSV = OUT_DIR / "exit_risk_shape_deep_validation_months_latest.csv"
OUT_COST_CSV = OUT_DIR / "exit_risk_shape_deep_validation_cost_sensitivity_latest.csv"
OUT_SYMBOL_CSV = OUT_DIR / "exit_risk_shape_deep_validation_symbol_concentration_latest.csv"

RUNNER_NAME = "edge_factory_os_exit_risk_shape_deep_validation_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "EXIT_RISK_SHAPE_DEEP_VALIDATION_CONTRACT_READY"

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


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None or value == "":
            return default
        if isinstance(value, str) and value.strip().lower() in {"none", "nan", "null"}:
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

    for w in [3, 6, 12]:
        df[f"mkt_ret_{w}_bps"] = df.groupby("time", sort=False, observed=True)[f"ret_{w}_bps"].transform("mean")
        df[f"rel_ret_{w}_bps"] = df[f"ret_{w}_bps"] - df[f"mkt_ret_{w}_bps"]

    df["quote_liquidity_proxy"] = df["close"] * df["volume"]
    df["log_quote_liquidity_proxy"] = np.log1p(df["quote_liquidity_proxy"].clip(lower=0))
    if df["log_quote_liquidity_proxy"].notna().sum() == 0:
        df["log_quote_liquidity_proxy"] = 0.0

    for col in ["ret_3_bps", "rel_ret_3_bps", "entry_range_bps", "coin_vol_6_bps", "log_quote_liquidity_proxy"]:
        df[f"{col}_rank_pct"] = df.groupby("time", sort=False, observed=True)[col].rank(pct=True)

    df["entry_range_bps_rank_pct"] = df["entry_range_bps_rank_pct"].fillna(0.5)
    df["coin_vol_6_bps_rank_pct"] = df["coin_vol_6_bps_rank_pct"].fillna(0.5)
    df["log_quote_liquidity_proxy_rank_pct"] = df["log_quote_liquidity_proxy_rank_pct"].fillna(1.0)

    print("Computing forward high/low path for deep validation...")
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


def build_reference_event_specs() -> Dict[str, Dict[str, Any]]:
    specs = [
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
    return {x["reference_id"]: x for x in specs}


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

    for c in ["time", "month", "symbol", "close", "ret_3_bps", "rel_ret_3_bps"]:
        mask &= df[c].notna()

    return mask


def shape_from_preview(row: Dict[str, Any], extra_cost_bps: float = 0.0) -> Dict[str, Any]:
    cost = to_float(row.get("cost_bps"), 0.0) or 0.0
    hold = to_int(row.get("hold"), 1)

    shape = {
        "exit_shape_id": str(row.get("exit_shape_id")),
        "exit_type": str(row.get("exit_type")),
        "hold": hold,
        "cost_bps": cost + extra_cost_bps,
    }

    tp = to_float(row.get("tp_bps"), None)
    sl = to_float(row.get("sl_bps"), None)
    mfe_trigger = to_float(row.get("mfe_trigger_bps"), None)

    if tp is not None:
        shape["tp_bps"] = tp
    if sl is not None:
        shape["sl_bps"] = sl
    if mfe_trigger is not None:
        shape["mfe_trigger_bps"] = mfe_trigger

    return shape


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
        return fixed - cost

    if exit_type == "tp_sl_conservative":
        tp = float(shape["tp_bps"])
        sl = float(shape["sl_bps"])
        hit_tp = mfe >= tp
        hit_sl = mae <= -sl
        pnl = fixed.copy()
        pnl = pnl.where(~hit_tp, tp)
        pnl = pnl.where(~hit_sl, -sl)
        return pnl - cost

    if exit_type == "breakeven_after_mfe":
        trigger = float(shape["mfe_trigger_bps"])
        hit_trigger = mfe >= trigger
        pnl = fixed.copy()
        pnl = pnl.where(~(hit_trigger & (pnl < 0.0)), 0.0)
        return pnl - cost

    return fixed - cost


def replay_preview(
    df: pd.DataFrame,
    preview: Dict[str, Any],
    canonical_months: List[str],
    canonical_policy_month_count: int,
    extra_cost_bps: float = 0.0,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]:
    specs = build_reference_event_specs()

    reference_id = str(preview.get("reference_id"))
    spec = specs.get(reference_id)
    if spec is None:
        raise ValueError(f"Unknown reference_id from preview: {reference_id}")

    side = str(preview.get("side") or spec["side"])
    shape = shape_from_preview(preview, extra_cost_bps=extra_cost_bps)
    hold = int(shape["hold"])

    mask = reference_mask(df, spec)

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
    pnl = compute_exit_pnl(events, side=side, shape=shape)
    events["diagnostic_pnl_bps"] = pnl
    events = events.dropna(subset=["diagnostic_pnl_bps"]).copy()

    bar = events.groupby(["time", "month"], observed=True)["diagnostic_pnl_bps"].mean().reset_index()

    month_sum = bar.groupby("month", observed=True)["diagnostic_pnl_bps"].sum().reindex(canonical_months).fillna(0.0)
    month_count = bar.groupby("month", observed=True).size().reindex(canonical_months).fillna(0)

    active_months = int((month_count > 0).sum())
    positive_months = int((month_sum > 0.0).sum())
    total = float(month_sum.sum())
    strict_pass = active_months >= canonical_policy_month_count and positive_months >= canonical_policy_month_count and total > 0.0

    symbol_counts = events["symbol"].value_counts()
    symbol_count = int(symbol_counts.shape[0])
    top_symbol_share = float(symbol_counts.iloc[0] / len(events)) if len(events) > 0 and symbol_count > 0 else 1.0
    top5_symbol_share = float(symbol_counts.head(5).sum() / len(events)) if len(events) > 0 else 1.0

    values = bar["diagnostic_pnl_bps"].to_numpy(dtype=np.float64)

    result = {
        "reference_id": reference_id,
        "side": side,
        "exit_shape_id": str(preview.get("exit_shape_id")),
        "exit_type": str(preview.get("exit_type")),
        "hold": hold,
        "base_cost_bps": to_float(preview.get("cost_bps"), 0.0),
        "extra_cost_bps": float(extra_cost_bps),
        "effective_cost_bps": float(shape.get("cost_bps", 0.0)),
        "event_count": int(len(events)),
        "bar_count": int(len(bar)),
        "symbol_count": symbol_count,
        "top_symbol_share": top_symbol_share,
        "top5_symbol_share": top5_symbol_share,
        "active_months": active_months,
        "positive_months": positive_months,
        "canonical_month_count": canonical_policy_month_count,
        "strict_12_replay_pass": bool(strict_pass),
        "total_month_pnl_bps": total,
        "mean_bar_pnl_bps": float(np.mean(values)) if len(values) else 0.0,
        "median_bar_pnl_bps": float(np.median(values)) if len(values) else 0.0,
        "bar_win_rate": float(np.mean(values > 0.0)) if len(values) else 0.0,
        "worst_month_bps": float(month_sum.min()),
        "best_month_bps": float(month_sum.max()),
    }

    month_rows = []
    for m in canonical_months:
        month_rows.append({
            "reference_id": reference_id,
            "side": side,
            "exit_shape_id": str(preview.get("exit_shape_id")),
            "extra_cost_bps": float(extra_cost_bps),
            "month": m,
            "bar_count": int(month_count.loc[m]),
            "month_pnl_bps": float(month_sum.loc[m]),
            "positive_month": bool(month_sum.loc[m] > 0.0),
        })

    return result, month_rows, events


def rolling_oos_check(month_rows: List[Dict[str, Any]], canonical_months: List[str]) -> Dict[str, Any]:
    pnl_by_month = {r["month"]: float(r["month_pnl_bps"]) for r in month_rows if float(r.get("extra_cost_bps", 0.0)) == 0.0}
    vals = [pnl_by_month.get(m, 0.0) for m in canonical_months]

    thirds = [
        vals[0:4],
        vals[4:8],
        vals[8:12],
    ]

    third_sums = [float(sum(x)) for x in thirds]
    third_positive_counts = [int(sum(1 for v in x if v > 0.0)) for x in thirds]
    third_pass = all(s > 0.0 and pc == len(chunk) for s, pc, chunk in zip(third_sums, third_positive_counts, thirds))

    # Leave-one-quarter style rough rolling check.
    rolling_windows = []
    for start in range(0, max(1, len(vals) - 3)):
        chunk = vals[start:start + 4]
        if len(chunk) == 4:
            rolling_windows.append({
                "start_index": start,
                "sum": float(sum(chunk)),
                "positive_count": int(sum(1 for v in chunk if v > 0.0)),
                "pass": bool(sum(chunk) > 0.0 and all(v > 0.0 for v in chunk)),
            })

    rolling_pass = bool(rolling_windows and all(x["pass"] for x in rolling_windows))

    return {
        "third_sums": third_sums,
        "third_positive_counts": third_positive_counts,
        "third_split_pass": bool(third_pass),
        "rolling_4_month_window_count": len(rolling_windows),
        "rolling_4_month_all_positive_pass": bool(rolling_pass),
        "rolling_windows": rolling_windows,
    }


def route_hash_preflight(preview: Dict[str, Any]) -> Dict[str, Any]:
    route_payload = {
        "reference_id": preview.get("reference_id"),
        "side": preview.get("side"),
        "exit_shape_id": preview.get("exit_shape_id"),
        "exit_type": preview.get("exit_type"),
        "hold": preview.get("hold"),
        "cost_bps": preview.get("cost_bps"),
        "tp_bps": preview.get("tp_bps"),
        "sl_bps": preview.get("sl_bps"),
        "mfe_trigger_bps": preview.get("mfe_trigger_bps"),
        "policy": STRICT_POLICY_KEY,
    }
    validation_route_hash = stable_hash(route_payload)

    blocklist = load_json(BLOCKLIST_PATH, default={})
    blocked_hashes = set()

    if isinstance(blocklist, dict) and isinstance(blocklist.get("blocked_routes"), list):
        for x in blocklist["blocked_routes"]:
            if isinstance(x, dict) and x.get("route_hash"):
                blocked_hashes.add(str(x.get("route_hash")))
    elif isinstance(blocklist, list):
        for x in blocklist:
            if isinstance(x, dict) and x.get("route_hash"):
                blocked_hashes.add(str(x.get("route_hash")))

    return {
        "validation_route_hash": validation_route_hash,
        "route_hash_blocked": validation_route_hash in blocked_hashes,
        "known_blocked_route_count": len(blocked_hashes),
        "route_payload": route_payload,
    }


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = []
    for row in rows:
        for k in row.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    pd.DataFrame(rows)[fieldnames].to_csv(path, index=False)


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS EXIT RISK SHAPE DEEP VALIDATION RUNNER v1")
    lines.append("=" * 100)

    for k in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "strict_policy_key",
        "canonical_policy_month_count",
        "preview_count",
        "validation_result_count",
        "deep_validation_pass_count",
        "all_deep_validations_passed",
        "release_allowed",
        "elapsed_seconds",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("VALIDATION RESULTS")
    lines.append("-" * 100)
    for row in result.get("validation_results", []):
        lines.append(
            f"{row.get('reference_id')} {row.get('exit_shape_id')} | "
            f"deep_pass={row.get('deep_validation_pass')} | "
            f"strict={row.get('full_universe_replay_pass')} | "
            f"cost={row.get('cost_slippage_sensitivity_pass')} | "
            f"conc={row.get('symbol_concentration_pass')} | "
            f"rolling={row.get('rolling_oos_pass')} | "
            f"reason={row.get('failure_reasons')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in ["output_json", "output_txt", "validation_csv", "month_csv", "cost_csv", "symbol_csv"]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS EXIT RISK SHAPE DEEP VALIDATION RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"preview_count: {result.get('preview_count')}")
    print(f"validation_result_count: {result.get('validation_result_count')}")
    print(f"deep_validation_pass_count: {result.get('deep_validation_pass_count')}")
    print(f"all_deep_validations_passed: {result.get('all_deep_validations_passed')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"CSV : {result.get('validation_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_PATH, default={})

    canonical_policy_month_count = int(contract.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    strict_preview_rows = contract.get("strict_preview_rows")
    if not isinstance(strict_preview_rows, list):
        strict_preview_rows = []

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "contract_path": str(CONTRACT_PATH),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "research_key": contract.get("research_key"),
        "validation_queue_id": contract.get("validation_queue_id"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "validation_csv": str(OUT_VALIDATION_CSV),
        "month_csv": str(OUT_MONTH_CSV),
        "cost_csv": str(OUT_COST_CSV),
        "symbol_csv": str(OUT_SYMBOL_CSV),
        **SAFETY_FLAGS,
    }

    try:
        prerequisite_pass = (
            contract.get("builder_status") == REQUIRED_BUILDER_STATUS
            and canonical_policy_month_count == 12
            and len(strict_preview_rows) > 0
            and contract.get("release_gate_feed", {}).get("RELEASE_PASS_FROM_THIS_CONTRACT") is False
        )

        if not prerequisite_pass:
            result = {
                **base_result,
                "runner_status": "EXIT_RISK_SHAPE_DEEP_VALIDATION_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_DEEP_VALIDATION_CONTRACT_NO_RELEASE",
                "reason": (
                    f"builder_status={contract.get('builder_status')}; "
                    f"strict_preview_row_count={len(strict_preview_rows)}; "
                    f"canonical_policy_month_count={canonical_policy_month_count}"
                ),
                "release_allowed": False,
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
                "runner_status": "EXIT_RISK_SHAPE_DEEP_VALIDATION_RUNNER_BLOCKED_NO_PANEL_FOUND",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "LOCATE_FULL_UNIVERSE_PANEL_AND_RERUN_NO_RELEASE",
                "reason": "No parquet/csv panel found.",
                "release_allowed": False,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        print(f"Loading panel: {panel_path}")
        raw = read_panel(panel_path)

        print("Building core panel for independent replay...")
        df, column_map = build_core_panel(raw)

        raw_months = sorted(df["month"].dropna().unique().tolist())
        canonical_months = derive_canonical_months(df, canonical_policy_month_count)

        validation_rows: List[Dict[str, Any]] = []
        month_rows_all: List[Dict[str, Any]] = []
        cost_rows: List[Dict[str, Any]] = []
        symbol_rows: List[Dict[str, Any]] = []

        print(f"Running deep validation for {len(strict_preview_rows)} preview rows...")

        for idx, preview in enumerate(strict_preview_rows, start=1):
            print(f"Validating preview {idx}/{len(strict_preview_rows)}: {preview.get('reference_id')} {preview.get('exit_shape_id')}")

            preflight = route_hash_preflight(preview)

            base_replay, base_month_rows, events = replay_preview(
                df=df,
                preview=preview,
                canonical_months=canonical_months,
                canonical_policy_month_count=canonical_policy_month_count,
                extra_cost_bps=0.0,
            )

            rolling = rolling_oos_check(base_month_rows, canonical_months)

            # Cost/slippage stress.
            cost_checks = []
            for extra_cost in [0.0, 25.0, 50.0, 100.0]:
                replay, mrows, _events = replay_preview(
                    df=df,
                    preview=preview,
                    canonical_months=canonical_months,
                    canonical_policy_month_count=canonical_policy_month_count,
                    extra_cost_bps=extra_cost,
                )
                replay["validation_route_hash"] = preflight["validation_route_hash"]
                cost_rows.append(replay)
                cost_checks.append(replay)

            cost_stress_required = [x for x in cost_checks if float(x.get("extra_cost_bps", 0.0)) in {25.0, 50.0}]
            cost_slippage_sensitivity_pass = bool(cost_stress_required and all(x["strict_12_replay_pass"] for x in cost_stress_required))

            # Symbol concentration.
            symbol_counts = events["symbol"].value_counts()
            for symbol, count in symbol_counts.head(50).items():
                symbol_rows.append({
                    "validation_route_hash": preflight["validation_route_hash"],
                    "reference_id": preview.get("reference_id"),
                    "exit_shape_id": preview.get("exit_shape_id"),
                    "symbol": symbol,
                    "event_count": int(count),
                    "share": float(count / len(events)) if len(events) else 0.0,
                })

            symbol_concentration_pass = (
                base_replay["symbol_count"] >= 50
                and base_replay["top_symbol_share"] <= 0.20
                and base_replay["top5_symbol_share"] <= 0.50
            )

            # MAE/MFE path sanity: require enough events and not excessively dependent on tiny symbol universe.
            mae_mfe_path_sanity_pass = (
                base_replay["event_count"] >= 1000
                and base_replay["bar_count"] >= 250
                and base_replay["symbol_count"] >= 50
            )

            full_universe_replay_pass = bool(base_replay["strict_12_replay_pass"])
            month_stability_recheck_pass = bool(base_replay["positive_months"] == 12 and base_replay["active_months"] == 12)
            rolling_oos_pass = bool(rolling["third_split_pass"] and rolling["rolling_4_month_all_positive_pass"])
            route_hash_preflight_pass = not bool(preflight["route_hash_blocked"])

            failure_reasons = []
            if not route_hash_preflight_pass:
                failure_reasons.append("ROUTE_HASH_BLOCKED_OR_REPEAT_FAILURE")
            if not full_universe_replay_pass:
                failure_reasons.append("FULL_UNIVERSE_REPLAY_FAILED")
            if not rolling_oos_pass:
                failure_reasons.append("ROLLING_OR_OOS_SPLIT_FAILED")
            if not cost_slippage_sensitivity_pass:
                failure_reasons.append("COST_SLIPPAGE_SENSITIVITY_FAILED")
            if not symbol_concentration_pass:
                failure_reasons.append("SYMBOL_CONCENTRATION_FAILED")
            if not month_stability_recheck_pass:
                failure_reasons.append("MONTH_STABILITY_12_OF_12_RECHECK_FAILED")
            if not mae_mfe_path_sanity_pass:
                failure_reasons.append("MAE_MFE_PATH_SANITY_FAILED")

            deep_validation_pass = (
                route_hash_preflight_pass
                and full_universe_replay_pass
                and rolling_oos_pass
                and cost_slippage_sensitivity_pass
                and symbol_concentration_pass
                and month_stability_recheck_pass
                and mae_mfe_path_sanity_pass
            )

            row = {
                "validation_route_hash": preflight["validation_route_hash"],
                "reference_id": preview.get("reference_id"),
                "side": preview.get("side"),
                "exit_shape_id": preview.get("exit_shape_id"),
                "exit_type": preview.get("exit_type"),
                "hold": preview.get("hold"),
                "route_hash_preflight_pass": route_hash_preflight_pass,
                "full_universe_replay_pass": full_universe_replay_pass,
                "rolling_oos_pass": rolling_oos_pass,
                "cost_slippage_sensitivity_pass": cost_slippage_sensitivity_pass,
                "symbol_concentration_pass": symbol_concentration_pass,
                "month_stability_12_of_12_recheck_pass": month_stability_recheck_pass,
                "mae_mfe_path_sanity_pass": mae_mfe_path_sanity_pass,
                "deep_validation_pass": bool(deep_validation_pass),
                "release_allowed": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "event_count": base_replay["event_count"],
                "bar_count": base_replay["bar_count"],
                "symbol_count": base_replay["symbol_count"],
                "top_symbol_share": base_replay["top_symbol_share"],
                "top5_symbol_share": base_replay["top5_symbol_share"],
                "active_months": base_replay["active_months"],
                "positive_months": base_replay["positive_months"],
                "total_month_pnl_bps": base_replay["total_month_pnl_bps"],
                "worst_month_bps": base_replay["worst_month_bps"],
                "best_month_bps": base_replay["best_month_bps"],
                "third_sums": json.dumps(rolling["third_sums"]),
                "third_positive_counts": json.dumps(rolling["third_positive_counts"]),
                "rolling_4_month_window_count": rolling["rolling_4_month_window_count"],
                "failure_reasons": "|".join(failure_reasons) if failure_reasons else "",
            }

            validation_rows.append(row)

            for mr in base_month_rows:
                mr["validation_route_hash"] = preflight["validation_route_hash"]
                month_rows_all.append(mr)

        write_csv(OUT_VALIDATION_CSV, validation_rows)
        write_csv(OUT_MONTH_CSV, month_rows_all)
        write_csv(OUT_COST_CSV, cost_rows)
        write_csv(OUT_SYMBOL_CSV, symbol_rows)

        deep_pass_count = int(sum(1 for r in validation_rows if r.get("deep_validation_pass") is True))
        all_deep_validations_passed = bool(validation_rows and deep_pass_count == len(validation_rows))

        if deep_pass_count > 0:
            runner_status = "EXIT_RISK_SHAPE_DEEP_VALIDATION_RUNNER_PROMISING_NOT_RELEASE_PASS"
            severity = "ATTENTION"
            next_action = "BUILD_EXIT_RISK_SHAPE_DEEP_VALIDATION_EVALUATOR_KEEP_RELEASE_BLOCKED"
            reason = (
                f"deep_validation_pass_count={deep_pass_count}; "
                f"validation_result_count={len(validation_rows)}; "
                "release_allowed=False"
            )
        else:
            runner_status = "EXIT_RISK_SHAPE_DEEP_VALIDATION_RUNNER_FAILED_VALIDATION"
            severity = "ATTENTION"
            next_action = "BUILD_DEEP_VALIDATION_EVALUATOR_TO_CLOSE_OR_ROTATE_NO_RELEASE"
            reason = (
                f"deep_validation_pass_count=0; "
                f"validation_result_count={len(validation_rows)}; "
                "release_allowed=False"
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
            "preview_count": int(len(strict_preview_rows)),
            "validation_result_count": int(len(validation_rows)),
            "deep_validation_pass_count": deep_pass_count,
            "all_deep_validations_passed": all_deep_validations_passed,
            "validation_results": validation_rows,
            "release_allowed": False,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
            "release_gate_feed": {
                "EXIT_RISK_SHAPE_DEEP_VALIDATION_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "DEEP_VALIDATION_PASS_COUNT": deep_pass_count,
                "ALL_DEEP_VALIDATIONS_PASSED": all_deep_validations_passed,
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
            "runner_status": "EXIT_RISK_SHAPE_DEEP_VALIDATION_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_DEEP_VALIDATION_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(e).__name__}: {e}",
            "error_type": type(e).__name__,
            "error": str(e),
            "release_allowed": False,
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
