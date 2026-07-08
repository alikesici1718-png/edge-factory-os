#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Symbol Cluster Segment Runner v1

Purpose:
- Consume Symbol Cluster Segment Contract v1.
- Build symbol/microstructure segments using pre-outcome features only.
- Run post-segmentation diagnostic references to test whether any segment has
  strict 12-of-12 canonical month preview structure.
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
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "symbol_cluster_segment_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_symbol_cluster_segment_runner"
OUT_JSON = OUT_DIR / "symbol_cluster_segment_runner_latest.json"
OUT_TXT = OUT_DIR / "symbol_cluster_segment_runner_latest.txt"
OUT_PROFILE_CSV = OUT_DIR / "symbol_cluster_segment_symbol_profiles_latest.csv"
OUT_MEMBERSHIP_CSV = OUT_DIR / "symbol_cluster_segment_membership_latest.csv"
OUT_DIAGNOSTIC_CSV = OUT_DIR / "symbol_cluster_segment_ranked_diagnostics_latest.csv"
OUT_MONTH_CSV = OUT_DIR / "symbol_cluster_segment_month_diagnostics_latest.csv"
OUT_CONCENTRATION_CSV = OUT_DIR / "symbol_cluster_segment_concentration_latest.csv"

RUNNER_NAME = "edge_factory_os_symbol_cluster_segment_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "SYMBOL_CLUSTER_SEGMENT_CONTRACT_READY"
REQUIRED_DIRECTION_QUEUE_KEY = "RD4_04_SYMBOL_CLUSTER_AND_MICROSTRUCTURE_SEGMENT_SEARCH"

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


def qcut_labels(series: pd.Series, labels: List[str], fallback: str) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if s.dropna().nunique() < len(labels):
        return pd.Series([fallback] * len(s), index=s.index, dtype="object")
    try:
        out = pd.qcut(s, q=len(labels), labels=labels, duplicates="drop")
        return out.astype("object").where(out.notna(), fallback).astype(str)
    except Exception:
        return pd.Series([fallback] * len(s), index=s.index, dtype="object")


def robust_scale_matrix(df: pd.DataFrame, cols: List[str]) -> np.ndarray:
    arrs = []
    for c in cols:
        s = pd.to_numeric(df[c], errors="coerce").replace([np.inf, -np.inf], np.nan)
        x = s.to_numpy(dtype=np.float64)
        finite = np.isfinite(x)
        if not finite.any():
            arrs.append(np.zeros(len(df), dtype=np.float64))
            continue
        med = float(np.nanmedian(x))
        q25 = float(np.nanpercentile(x, 25))
        q75 = float(np.nanpercentile(x, 75))
        scale = q75 - q25
        if not np.isfinite(scale) or abs(scale) < 1e-12:
            scale = float(np.nanstd(x))
        if not np.isfinite(scale) or abs(scale) < 1e-12:
            scale = 1.0
        z = (x - med) / scale
        z = np.nan_to_num(z, nan=0.0, posinf=5.0, neginf=-5.0)
        arrs.append(np.clip(z, -8, 8))
    return np.vstack(arrs).T.astype(np.float64)


def cluster_matrix(x: np.ndarray, k: int, random_state: int = 42) -> Tuple[np.ndarray, str]:
    try:
        from sklearn.cluster import KMeans
        model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = model.fit_predict(x)
        return labels.astype(int), "sklearn_kmeans"
    except Exception:
        composite = np.nanmean(x, axis=1)
        ranks = pd.Series(composite).rank(pct=True).to_numpy()
        labels = np.minimum((ranks * k).astype(int), k - 1)
        return labels.astype(int), "fallback_quantile_composite"


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

    for h in [1, 3, 6, 12]:
        fut_close = g["close"].shift(-h)
        df[f"fut_ret_{h}_bps"] = ((fut_close / df["close"]) - 1.0) * 10000.0

    real_range = ((df["high"] - df["low"]) / df["close"]) * 10000.0
    proxy_range = df["ret_1_bps"].abs()
    df["entry_range_bps"] = real_range.where(real_range.notna(), proxy_range)

    df["coin_vol_6_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(6, min_periods=4).std())
    df["coin_vol_12_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(12, min_periods=6).std())
    df["trend_persistence_3"] = g["ret_3_bps"].transform(lambda s: s.rolling(24, min_periods=12).apply(lambda x: np.mean(np.sign(x[1:]) == np.sign(x[:-1])) if len(x) > 1 else np.nan, raw=True))

    for w in [3, 6, 12]:
        df[f"mkt_ret_{w}_bps"] = df.groupby("time", sort=False, observed=True)[f"ret_{w}_bps"].transform("mean")
        df[f"rel_ret_{w}_bps"] = df[f"ret_{w}_bps"] - df[f"mkt_ret_{w}_bps"]

    df["quote_liquidity_proxy"] = df["close"] * df["volume"]
    df["log_quote_liquidity_proxy"] = np.log1p(df["quote_liquidity_proxy"].clip(lower=0))
    if df["log_quote_liquidity_proxy"].notna().sum() == 0:
        df["log_quote_liquidity_proxy"] = 0.0

    for col in [
        "ret_3_bps",
        "ret_6_bps",
        "rel_ret_3_bps",
        "rel_ret_6_bps",
        "entry_range_bps",
        "coin_vol_6_bps",
        "log_quote_liquidity_proxy",
    ]:
        df[f"{col}_rank_pct"] = df.groupby("time", sort=False, observed=True)[col].rank(pct=True)

    df["entry_range_bps_rank_pct"] = df["entry_range_bps_rank_pct"].fillna(0.5)
    df["coin_vol_6_bps_rank_pct"] = df["coin_vol_6_bps_rank_pct"].fillna(0.5)
    df["log_quote_liquidity_proxy_rank_pct"] = df["log_quote_liquidity_proxy_rank_pct"].fillna(1.0)

    column_map = {
        "time_col": time_col,
        "symbol_col": symbol_col,
        "close_col": close_col,
        "volume_col": volume_col,
        "high_col": high_col,
        "low_col": low_col,
    }

    return df.replace([np.inf, -np.inf], np.nan), column_map


def build_symbol_profiles(df: pd.DataFrame) -> pd.DataFrame:
    base = df.groupby("symbol", observed=True).agg(
        row_count=("time", "count"),
        active_month_count=("month", "nunique"),
        median_liquidity=("log_quote_liquidity_proxy", "median"),
        mean_liquidity=("log_quote_liquidity_proxy", "mean"),
        median_range_bps=("entry_range_bps", "median"),
        mean_range_bps=("entry_range_bps", "mean"),
        median_vol_6_bps=("coin_vol_6_bps", "median"),
        mean_vol_6_bps=("coin_vol_6_bps", "mean"),
        median_abs_ret3_bps=("ret_3_bps", lambda s: float(np.nanmedian(np.abs(s)))),
        mean_abs_ret3_bps=("ret_3_bps", lambda s: float(np.nanmean(np.abs(s)))),
        median_rel3_bps=("rel_ret_3_bps", "median"),
        mean_rel3_bps=("rel_ret_3_bps", "mean"),
        trend_persistence_3=("trend_persistence_3", "median"),
        pos_ret3_share=("ret_3_bps", lambda s: float(np.nanmean(s > 0))),
        large_move_share=("ret_3_bps", lambda s: float(np.nanmean(np.abs(s) > np.nanmedian(np.abs(s)) * 2)) if s.notna().any() else 0.0),
    ).reset_index()

    # crude market beta proxy from symbol ret vs market ret
    beta_rows = []
    for symbol, sdf in df[["symbol", "ret_3_bps", "mkt_ret_3_bps"]].dropna().groupby("symbol", observed=True):
        x = sdf["mkt_ret_3_bps"].to_numpy(dtype=np.float64)
        y = sdf["ret_3_bps"].to_numpy(dtype=np.float64)

        finite_mask = np.isfinite(x) & np.isfinite(y)
        x = x[finite_mask]
        y = y[finite_mask]

        if len(x) < 50 or np.var(x) <= 1e-12:
            beta = 1.0
            corr = 0.0
        else:
            cov_xy = float(np.cov(x, y, ddof=0)[0, 1])
            var_x = float(np.var(x))
            beta = cov_xy / var_x if var_x > 1e-12 else 1.0

            corr_matrix = np.corrcoef(x, y)
            corr_value = corr_matrix[0, 1] if corr_matrix.shape == (2, 2) else 0.0
            corr = float(corr_value) if np.isfinite(corr_value) else 0.0

        beta_rows.append({"symbol": symbol, "market_beta_proxy": beta, "market_corr_proxy": corr})

    beta_df = pd.DataFrame(beta_rows)
    if not beta_df.empty:
        base = base.merge(beta_df, on="symbol", how="left")
    else:
        base["market_beta_proxy"] = 1.0
        base["market_corr_proxy"] = 0.0

    for col in [
        "median_liquidity",
        "median_range_bps",
        "median_vol_6_bps",
        "median_abs_ret3_bps",
        "trend_persistence_3",
        "market_beta_proxy",
        "market_corr_proxy",
    ]:
        base[col] = pd.to_numeric(base[col], errors="coerce")
        base[f"{col}_rank_pct"] = base[col].rank(pct=True)

    base["liq_tier"] = qcut_labels(base["median_liquidity"], ["liq_low", "liq_mid", "liq_high"], "liq_mid")
    base["vol_tier"] = qcut_labels(base["median_vol_6_bps"], ["vol_low", "vol_mid", "vol_high"], "vol_mid")
    base["range_tier"] = qcut_labels(base["median_range_bps"], ["range_low", "range_mid", "range_high"], "range_mid")
    base["trend_tier"] = qcut_labels(base["trend_persistence_3"], ["trend_low", "trend_mid", "trend_high"], "trend_mid")
    base["beta_tier"] = qcut_labels(base["market_beta_proxy"], ["beta_low", "beta_mid", "beta_high"], "beta_mid")

    return base.replace([np.inf, -np.inf], np.nan)


def build_segment_membership(profiles: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for _, row in profiles.iterrows():
        symbol = row["symbol"]

        memberships = [
            ("LIQUIDITY_TIER", row["liq_tier"]),
            ("VOLATILITY_TIER", row["vol_tier"]),
            ("RANGE_TIER", row["range_tier"]),
            ("TREND_PERSISTENCE_TIER", row["trend_tier"]),
            ("BETA_TIER", row["beta_tier"]),
            ("LIQ_X_VOL", f"{row['liq_tier']}|{row['vol_tier']}"),
            ("RANGE_X_TREND", f"{row['range_tier']}|{row['trend_tier']}"),
            ("BETA_X_VOL", f"{row['beta_tier']}|{row['vol_tier']}"),
        ]

        for segment_type, segment_id in memberships:
            rows.append({
                "symbol": symbol,
                "segment_type": segment_type,
                "segment_id": str(segment_id),
                "segment_method": "pre_outcome_quantile_bucket",
            })

    feature_cols = [
        "median_liquidity",
        "median_range_bps",
        "median_vol_6_bps",
        "median_abs_ret3_bps",
        "trend_persistence_3",
        "market_beta_proxy",
        "market_corr_proxy",
        "active_month_count",
    ]

    x = robust_scale_matrix(profiles, feature_cols)
    for k in [3, 4, 5, 6]:
        if len(profiles) < k:
            continue
        labels, method = cluster_matrix(x, k=k, random_state=100 + k)
        for symbol, label in zip(profiles["symbol"].tolist(), labels.tolist()):
            rows.append({
                "symbol": symbol,
                "segment_type": f"SYMBOL_PROFILE_CLUSTER_K{k}",
                "segment_id": f"cluster_{int(label)}",
                "segment_method": method,
            })

    membership = pd.DataFrame(rows)

    # Drop tiny segments later during diagnostic, but keep full membership table for audit.
    return membership


def build_reference_event_specs() -> List[Dict[str, Any]]:
    return [
        {
            "reference_id": "SEG_REF_LONG_STRONG_REL",
            "side": "long",
            "rel_rank_min": 0.75,
            "ret_rank_min": 0.60,
            "vol_rank_max": 0.80,
            "range_rank_max": 0.90,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "SEG_REF_LONG_CALM_STRONG_REL",
            "side": "long",
            "rel_rank_min": 0.75,
            "ret_rank_min": 0.55,
            "vol_rank_max": 0.50,
            "range_rank_max": 0.60,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "SEG_REF_SHORT_WEAK_REL",
            "side": "short",
            "rel_rank_max": 0.25,
            "ret_rank_max": 0.40,
            "vol_rank_max": 0.80,
            "range_rank_max": 0.90,
            "liq_rank_min": 0.00,
        },
        {
            "reference_id": "SEG_REF_SHORT_CALM_WEAK_REL",
            "side": "short",
            "rel_rank_max": 0.25,
            "ret_rank_max": 0.45,
            "vol_rank_max": 0.50,
            "range_rank_max": 0.60,
            "liq_rank_min": 0.00,
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

    for c in ["time", "month", "symbol", "close", "ret_3_bps", "rel_ret_3_bps"]:
        mask &= df[c].notna()

    return mask


def evaluate_segment_reference(
    df: pd.DataFrame,
    segment_symbols: List[str],
    segment_type: str,
    segment_id: str,
    reference: Dict[str, Any],
    hold: int,
    cost_bps: float,
    canonical_months: List[str],
    canonical_policy_month_count: int,
) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]]:
    if len(segment_symbols) < 8:
        return None

    seg_mask = df["symbol"].isin(segment_symbols)
    ref_mask = reference_mask(df, reference)
    work = df.loc[seg_mask & ref_mask, ["time", "month", "symbol", f"fut_ret_{hold}_bps"]].dropna().copy()

    if len(work) < 250:
        return None

    side = reference["side"]
    if side == "long":
        work["diagnostic_pnl_bps"] = work[f"fut_ret_{hold}_bps"] - cost_bps
    else:
        work["diagnostic_pnl_bps"] = -work[f"fut_ret_{hold}_bps"] - cost_bps

    bar = work.groupby(["time", "month"], observed=True)["diagnostic_pnl_bps"].mean().reset_index()
    if len(bar) < 50:
        return None

    month_sum = bar.groupby("month", observed=True)["diagnostic_pnl_bps"].sum().reindex(canonical_months).fillna(0.0)
    month_count = bar.groupby("month", observed=True).size().reindex(canonical_months).fillna(0)

    active_months = int((month_count > 0).sum())
    positive_months = int((month_sum > 0.0).sum())
    total = float(month_sum.sum())

    strict_preview = active_months >= canonical_policy_month_count and positive_months >= canonical_policy_month_count and total > 0.0

    symbol_counts = work["symbol"].value_counts()
    top_symbol_share = float(symbol_counts.iloc[0] / len(work)) if len(work) else 1.0
    top5_symbol_share = float(symbol_counts.head(5).sum() / len(work)) if len(work) else 1.0

    values = bar["diagnostic_pnl_bps"].to_numpy(dtype=np.float64)

    diag = {
        "segment_type": segment_type,
        "segment_id": segment_id,
        "segment_symbol_count": int(len(segment_symbols)),
        "reference_id": reference["reference_id"],
        "side": side,
        "hold": int(hold),
        "cost_bps": float(cost_bps),
        "event_count": int(len(work)),
        "bar_count": int(len(bar)),
        "active_months": active_months,
        "positive_months": positive_months,
        "canonical_month_count": canonical_policy_month_count,
        "strict_12_segment_preview_pass": bool(strict_preview),
        "total_month_pnl_bps": total,
        "mean_bar_pnl_bps": float(np.mean(values)),
        "median_bar_pnl_bps": float(np.median(values)),
        "bar_win_rate": float(np.mean(values > 0.0)),
        "worst_month_bps": float(month_sum.min()),
        "best_month_bps": float(month_sum.max()),
        "top_symbol_share": top_symbol_share,
        "top5_symbol_share": top5_symbol_share,
        "future_used_only_for_diagnostic": True,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
    }

    month_rows = []
    for m in canonical_months:
        month_rows.append({
            "segment_type": segment_type,
            "segment_id": segment_id,
            "reference_id": reference["reference_id"],
            "side": side,
            "hold": int(hold),
            "cost_bps": float(cost_bps),
            "month": m,
            "bar_count": int(month_count.loc[m]),
            "month_pnl_bps": float(month_sum.loc[m]),
            "positive_month": bool(month_sum.loc[m] > 0.0),
        })

    concentration_rows = []
    for symbol, count in symbol_counts.head(20).items():
        concentration_rows.append({
            "segment_type": segment_type,
            "segment_id": segment_id,
            "reference_id": reference["reference_id"],
            "side": side,
            "hold": int(hold),
            "symbol": symbol,
            "event_count": int(count),
            "share": float(count / len(work)),
        })

    return diag, month_rows, concentration_rows


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS SYMBOL CLUSTER SEGMENT RUNNER v1")
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
        "segment_membership_count",
        "segment_diagnostic_row_count",
        "strict_12_segment_preview_count",
        "elapsed_seconds",
        "panel_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("TOP SEGMENT DIAGNOSTICS")
    lines.append("-" * 100)
    for row in result.get("top_segment_diagnostics", [])[:10]:
        lines.append(
            f"{row.get('segment_type')}={row.get('segment_id')} {row.get('reference_id')} {row.get('side')} h={row.get('hold')} | "
            f"strict12={row.get('strict_12_segment_preview_pass')} | "
            f"positive={row.get('positive_months')}/{row.get('canonical_month_count')} | "
            f"total={row.get('total_month_pnl_bps')} | worst={row.get('worst_month_bps')} | "
            f"events={row.get('event_count')} seg_symbols={row.get('segment_symbol_count')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in ["output_json", "output_txt", "profile_csv", "membership_csv", "diagnostic_csv", "month_csv", "concentration_csv"]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS SYMBOL CLUSTER SEGMENT RUNNER v1")
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
    print(f"segment_membership_count: {result.get('segment_membership_count')}")
    print(f"segment_diagnostic_row_count: {result.get('segment_diagnostic_row_count')}")
    print(f"strict_12_segment_preview_count: {result.get('strict_12_segment_preview_count')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"CSV : {result.get('diagnostic_csv')}")
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
        "profile_csv": str(OUT_PROFILE_CSV),
        "membership_csv": str(OUT_MEMBERSHIP_CSV),
        "diagnostic_csv": str(OUT_DIAGNOSTIC_CSV),
        "month_csv": str(OUT_MONTH_CSV),
        "concentration_csv": str(OUT_CONCENTRATION_CSV),
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
                "runner_status": "SYMBOL_CLUSTER_SEGMENT_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_SYMBOL_CLUSTER_SEGMENT_CONTRACT_NO_RELEASE",
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
                "runner_status": "SYMBOL_CLUSTER_SEGMENT_RUNNER_BLOCKED_NO_PANEL_FOUND",
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

        print("Building core panel...")
        df, column_map = build_core_panel(raw)

        raw_months = sorted(df["month"].dropna().unique().tolist())
        canonical_months = derive_canonical_months(df, canonical_policy_month_count)

        print("Building pre-outcome symbol profiles...")
        profiles = build_symbol_profiles(df)
        profiles.to_csv(OUT_PROFILE_CSV, index=False)

        print("Building segment membership...")
        membership = build_segment_membership(profiles)
        membership.to_csv(OUT_MEMBERSHIP_CSV, index=False)

        refs = build_reference_event_specs()
        holds = [3, 6, 12]
        costs = [50.0, 75.0]

        diag_rows: List[Dict[str, Any]] = []
        month_rows: List[Dict[str, Any]] = []
        conc_rows: List[Dict[str, Any]] = []

        segment_groups = membership.groupby(["segment_type", "segment_id"], observed=True)["symbol"].apply(list).reset_index()
        segment_groups["segment_symbol_count"] = segment_groups["symbol"].apply(len)

        # Keep segments with usable breadth; still diagnostic-only.
        segment_groups = segment_groups[segment_groups["segment_symbol_count"] >= 8].copy()

        total_jobs = len(segment_groups) * len(refs) * len(holds) * len(costs)
        job_i = 0

        print(f"Symbols={df['symbol'].nunique()}, segments={len(segment_groups)}, refs={len(refs)}, jobs={total_jobs}")

        for _, srow in segment_groups.iterrows():
            segment_type = str(srow["segment_type"])
            segment_id = str(srow["segment_id"])
            segment_symbols = list(srow["symbol"])

            for ref in refs:
                for hold in holds:
                    for cost in costs:
                        job_i += 1
                        out = evaluate_segment_reference(
                            df=df,
                            segment_symbols=segment_symbols,
                            segment_type=segment_type,
                            segment_id=segment_id,
                            reference=ref,
                            hold=hold,
                            cost_bps=cost,
                            canonical_months=canonical_months,
                            canonical_policy_month_count=canonical_policy_month_count,
                        )

                        if out is not None:
                            diag, mrows, crows = out
                            diag_rows.append(diag)
                            month_rows.extend(mrows)
                            conc_rows.extend(crows)

                        if job_i % 250 == 0 or job_i == total_jobs:
                            print(f"Evaluated {job_i}/{total_jobs} | kept={len(diag_rows)}")

        diag = pd.DataFrame(diag_rows)
        month_diag = pd.DataFrame(month_rows)
        conc = pd.DataFrame(conc_rows)

        strict_count = 0
        top_segment_diagnostics: List[Dict[str, Any]] = []

        if not diag.empty:
            strict_count = int(diag["strict_12_segment_preview_pass"].fillna(False).astype(bool).sum())
            diag = diag.sort_values(
                by=[
                    "strict_12_segment_preview_pass",
                    "positive_months",
                    "total_month_pnl_bps",
                    "worst_month_bps",
                    "segment_symbol_count",
                    "event_count",
                ],
                ascending=[False, False, False, False, False, False],
            ).reset_index(drop=True)
            diag.to_csv(OUT_DIAGNOSTIC_CSV, index=False)
            top_segment_diagnostics = diag.head(20).to_dict(orient="records")
        else:
            pd.DataFrame().to_csv(OUT_DIAGNOSTIC_CSV, index=False)

        if not month_diag.empty:
            month_diag.to_csv(OUT_MONTH_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_MONTH_CSV, index=False)

        if not conc.empty:
            conc.to_csv(OUT_CONCENTRATION_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_CONCENTRATION_CSV, index=False)

        if strict_count > 0:
            runner_status = "SYMBOL_CLUSTER_SEGMENT_RUNNER_STRICT_12_PREVIEW_FOUND_NOT_RELEASE_PASS"
            severity = "ATTENTION"
            next_action = "BUILD_SYMBOL_CLUSTER_SEGMENT_EVALUATOR_AND_DEEP_VALIDATION_KEEP_ACTIONS_BLOCKED"
            reason = (
                f"segment_diagnostic_row_count={len(diag)}; "
                f"strict_12_segment_preview_count={strict_count}; preview_only_not_release"
            )
        elif len(diag) > 0:
            runner_status = "SYMBOL_CLUSTER_SEGMENT_RUNNER_COMPLETE_NO_STRICT_SEGMENT_PREVIEW"
            severity = "ATTENTION"
            next_action = "BUILD_SYMBOL_CLUSTER_SEGMENT_EVALUATOR_OR_ROTATE_NO_RELEASE"
            reason = (
                f"segment_diagnostic_row_count={len(diag)}; "
                "strict_12_segment_preview_count=0"
            )
        else:
            runner_status = "SYMBOL_CLUSTER_SEGMENT_RUNNER_NO_VALID_SEGMENT_DIAGNOSTICS"
            severity = "ATTENTION"
            next_action = "BUILD_SYMBOL_CLUSTER_SEGMENT_EVALUATOR_TO_CLOSE_OR_EXPAND_NO_RELEASE"
            reason = "segment_diagnostic_row_count=0"

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
            "profile_row_count": int(len(profiles)),
            "segment_membership_count": int(len(membership)),
            "segment_group_count": int(len(segment_groups)),
            "segment_diagnostic_row_count": int(len(diag)),
            "month_diagnostic_row_count": int(len(month_diag)),
            "concentration_row_count": int(len(conc)),
            "strict_12_segment_preview_count": int(strict_count),
            "top_segment_diagnostics": top_segment_diagnostics,
            "diagnostic_integrity": {
                "segment_discovery_uses_future": False,
                "future_used_only_for_post_segment_diagnostic": True,
                "manual_symbol_whitelist": False,
                "manual_month_blacklist": False,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
            },
            "release_gate_feed": {
                "SYMBOL_CLUSTER_SEGMENT_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "STRICT_12_SEGMENT_PREVIEW_COUNT": int(strict_count),
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
            "runner_status": "SYMBOL_CLUSTER_SEGMENT_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_SYMBOL_CLUSTER_SEGMENT_RUNNER_ERROR_NO_RELEASE",
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
