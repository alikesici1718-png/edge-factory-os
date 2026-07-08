#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Regime First Cluster Runner v1

Purpose:
- Run RD4_01 regime-first unsupervised cluster research.
- Cluster market/month regimes using pre-outcome features only.
- Use future returns only AFTER clustering for diagnostic preview.
- Do NOT create candidates.
- Do NOT release families.
- Do NOT touch runtime/capital/live/real orders.

Safety:
- READ_ONLY_RESEARCH only.
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

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "regime_first_cluster_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_regime_first_cluster_runner"
OUT_JSON = OUT_DIR / "regime_first_cluster_runner_latest.json"
OUT_TXT = OUT_DIR / "regime_first_cluster_runner_latest.txt"
OUT_CLUSTER_SUMMARY_CSV = OUT_DIR / "regime_first_cluster_summary_latest.csv"
OUT_TIMESTAMP_MEMBERSHIP_CSV = OUT_DIR / "regime_first_timestamp_cluster_membership_latest.csv"
OUT_MONTH_MEMBERSHIP_CSV = OUT_DIR / "regime_first_month_cluster_membership_latest.csv"
OUT_FEATURE_CENTROIDS_CSV = OUT_DIR / "regime_first_cluster_feature_centroids_latest.csv"

RUNNER_NAME = "edge_factory_os_regime_first_cluster_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "REGIME_FIRST_CLUSTER_CONTRACT_READY"
REQUIRED_DIRECTION_QUEUE_KEY = "RD4_01_REGIME_FIRST_UNSUPERVISED_CLUSTER_SEARCH"

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
        cc = str(c).strip()
        low = cc.lower().strip().replace(" ", "_").replace("-", "_")
        rename[c] = low
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


def derive_canonical_months_from_time_state(time_state: pd.DataFrame, canonical_policy_month_count: int) -> List[str]:
    raw_months = sorted([m for m in time_state["month"].dropna().unique().tolist() if isinstance(m, str)])

    if len(raw_months) <= canonical_policy_month_count:
        return raw_months

    counts = time_state.groupby("month", observed=True).size().sort_index()
    positive_counts = counts[counts > 0]

    if positive_counts.empty:
        return raw_months[-canonical_policy_month_count:]

    median_count = float(positive_counts.median())
    fullish = counts[counts >= median_count * 0.55].index.tolist()

    if len(fullish) >= canonical_policy_month_count:
        top = counts.loc[fullish].sort_values(ascending=False).head(canonical_policy_month_count).index.tolist()
        return sorted(top)

    return raw_months[-canonical_policy_month_count:]


def percentile_rank_series(s: pd.Series) -> pd.Series:
    return s.rank(pct=True)


def robust_scale_matrix(df: pd.DataFrame, feature_cols: List[str]) -> Tuple[np.ndarray, Dict[str, Dict[str, float]]]:
    x = df[feature_cols].astype(float).replace([np.inf, -np.inf], np.nan)

    stats: Dict[str, Dict[str, float]] = {}
    arrays = []

    for c in feature_cols:
        col = x[c].to_numpy(dtype=np.float64)
        med = float(np.nanmedian(col)) if np.isfinite(col).any() else 0.0
        q25 = float(np.nanpercentile(col, 25)) if np.isfinite(col).any() else 0.0
        q75 = float(np.nanpercentile(col, 75)) if np.isfinite(col).any() else 1.0
        iqr = q75 - q25
        if not np.isfinite(iqr) or abs(iqr) < 1e-12:
            iqr = float(np.nanstd(col))
        if not np.isfinite(iqr) or abs(iqr) < 1e-12:
            iqr = 1.0

        scaled = (col - med) / iqr
        scaled = np.nan_to_num(scaled, nan=0.0, posinf=5.0, neginf=-5.0)
        scaled = np.clip(scaled, -8.0, 8.0)

        arrays.append(scaled)
        stats[c] = {"median": med, "q25": q25, "q75": q75, "scale": iqr}

    matrix = np.vstack(arrays).T.astype(np.float64)
    return matrix, stats


def cluster_matrix(x: np.ndarray, k: int, random_state: int = 42) -> Tuple[np.ndarray, str]:
    """
    Prefer sklearn KMeans. Fallback to deterministic quantile composite clustering.
    """
    try:
        from sklearn.cluster import KMeans

        model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = model.fit_predict(x)
        return labels.astype(int), "sklearn_kmeans"
    except Exception:
        composite = np.nanmean(x, axis=1)
        composite = np.nan_to_num(composite, nan=0.0)
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

    rename = {
        time_col: "time",
        symbol_col: "symbol",
        close_col: "close",
    }
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
        df["high"] = np.nan

    if "low" in df.columns:
        df["low"] = pd.to_numeric(df["low"], errors="coerce")
    else:
        df["low"] = np.nan

    df = df.dropna(subset=["time", "symbol", "close"]).sort_values(["symbol", "time"]).reset_index(drop=True)

    g = df.groupby("symbol", sort=False, observed=True)

    ret_windows = [1, 3, 6, 12, 24]
    fut_windows = [1, 3, 6, 12]

    for w in ret_windows:
        prev = g["close"].shift(w)
        df[f"ret_{w}_bps"] = ((df["close"] / prev) - 1.0) * 10000.0

    for h in fut_windows:
        fut = g["close"].shift(-h)
        df[f"fut_ret_{h}_bps"] = ((fut / df["close"]) - 1.0) * 10000.0

    real_range = ((df["high"] - df["low"]) / df["close"]) * 10000.0
    proxy_range = df["ret_1_bps"].abs()
    df["entry_range_bps"] = real_range.where(real_range.notna(), proxy_range)

    df["quote_liquidity_proxy"] = df["close"] * df["volume"]
    df["log_quote_liquidity_proxy"] = np.log1p(df["quote_liquidity_proxy"].clip(lower=0))
    if df["log_quote_liquidity_proxy"].notna().sum() == 0:
        df["log_quote_liquidity_proxy"] = 0.0

    cols = {
        "time_col": time_col,
        "symbol_col": symbol_col,
        "close_col": close_col,
        "volume_col": volume_col,
        "high_col": high_col,
        "low_col": low_col,
    }

    return df, cols


def build_time_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build timestamp-level regime state from pre-outcome features.
    Future return columns are added later only for diagnostics, not for clustering inputs.
    """

    agg_spec = {
        "symbol": "count",
        "ret_1_bps": ["mean", "median", "std"],
        "ret_3_bps": ["mean", "median", "std"],
        "ret_6_bps": ["mean", "median", "std"],
        "ret_12_bps": ["mean", "median", "std"],
        "ret_24_bps": ["mean", "median", "std"],
        "entry_range_bps": ["mean", "median", "std"],
        "log_quote_liquidity_proxy": ["mean", "median", "std"],
    }

    time_state = df.groupby("time", sort=True, observed=True).agg(agg_spec)
    time_state.columns = ["_".join([str(x) for x in c if str(x) != ""]) for c in time_state.columns]
    time_state = time_state.reset_index()

    time_state = time_state.rename(columns={"symbol_count": "symbol_count"})

    first_month = df.groupby("time", sort=True, observed=True)["month"].first().reset_index()
    time_state = time_state.merge(first_month, on="time", how="left")

    for w in [1, 3, 6, 12, 24]:
        r = df[f"ret_{w}_bps"]
        tmp = pd.DataFrame({
            "time": df["time"],
            f"ret_{w}_pos_share": (r > 0).astype(float),
            f"ret_{w}_neg_share": (r < 0).astype(float),
            f"ret_{w}_abs_median_input": r.abs(),
        })

        extra = tmp.groupby("time", sort=True, observed=True).agg({
            f"ret_{w}_pos_share": "mean",
            f"ret_{w}_neg_share": "mean",
            f"ret_{w}_abs_median_input": "median",
        }).reset_index()

        extra = extra.rename(columns={f"ret_{w}_abs_median_input": f"ret_{w}_abs_median"})
        time_state = time_state.merge(extra, on="time", how="left")

    for h in [1, 3, 6, 12]:
        fut = df.groupby("time", sort=True, observed=True)[f"fut_ret_{h}_bps"].mean().reset_index()
        fut = fut.rename(columns={f"fut_ret_{h}_bps": f"diagnostic_fut_mkt_ret_{h}_bps"})
        time_state = time_state.merge(fut, on="time", how="left")

    time_state = time_state.replace([np.inf, -np.inf], np.nan)

    # Timestamp-level ranks across time, not within time.
    rank_source_cols = [
        c for c in time_state.columns
        if c not in {"time", "month"}
        and not c.startswith("diagnostic_fut_")
    ]

    for c in rank_source_cols:
        time_state[f"{c}_time_rank_pct"] = percentile_rank_series(time_state[c])

    return time_state


def build_month_state(time_state: pd.DataFrame, timestamp_feature_cols: List[str]) -> pd.DataFrame:
    month_state = time_state.groupby("month", sort=True, observed=True)[timestamp_feature_cols].agg(["mean", "median", "std"]).reset_index()
    month_state.columns = [
        "_".join([str(x) for x in c if str(x) != ""]).rstrip("_")
        if isinstance(c, tuple)
        else str(c)
        for c in month_state.columns
    ]

    count = time_state.groupby("month", sort=True, observed=True).size().reset_index(name="timestamp_count")
    month_state = month_state.merge(count, on="month", how="left")

    for h in [1, 3, 6, 12]:
        col = f"diagnostic_fut_mkt_ret_{h}_bps"
        if col in time_state.columns:
            diag = time_state.groupby("month", sort=True, observed=True)[col].sum().reset_index()
            diag = diag.rename(columns={col: f"diagnostic_month_sum_fut_mkt_ret_{h}_bps"})
            month_state = month_state.merge(diag, on="month", how="left")

    return month_state.replace([np.inf, -np.inf], np.nan)


def evaluate_timestamp_clusters(
    time_state: pd.DataFrame,
    labels: np.ndarray,
    k: int,
    method: str,
    feature_cols: List[str],
    canonical_months: List[str],
    canonical_policy_month_count: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    work = time_state.copy()
    work["cluster_k"] = int(k)
    work["cluster_id"] = labels.astype(int)
    work["cluster_method"] = method

    summary_rows: List[Dict[str, Any]] = []
    centroid_rows: List[Dict[str, Any]] = []
    membership_rows: List[Dict[str, Any]] = []

    for _, row in work[["time", "month", "cluster_k", "cluster_id", "cluster_method"]].iterrows():
        membership_rows.append({
            "level": "timestamp_market_state",
            "time": str(row["time"]),
            "month": row["month"],
            "cluster_k": int(row["cluster_k"]),
            "cluster_id": int(row["cluster_id"]),
            "cluster_method": row["cluster_method"],
        })

    for cluster_id in sorted(work["cluster_id"].dropna().unique().tolist()):
        cdf = work[work["cluster_id"] == cluster_id].copy()
        if cdf.empty:
            continue

        active_month_counts = cdf.groupby("month", observed=True).size().reindex(canonical_months).fillna(0)
        active_months = int((active_month_counts > 0).sum())

        centroid = cdf[feature_cols].mean(numeric_only=True).to_dict()
        for feature_name, value in centroid.items():
            centroid_rows.append({
                "level": "timestamp_market_state",
                "cluster_k": int(k),
                "cluster_id": int(cluster_id),
                "feature": feature_name,
                "centroid_value": float(value) if pd.notna(value) else None,
            })

        for horizon in [1, 3, 6, 12]:
            diag_col = f"diagnostic_fut_mkt_ret_{horizon}_bps"
            if diag_col not in cdf.columns:
                continue

            month_sum = cdf.groupby("month", observed=True)[diag_col].sum().reindex(canonical_months).fillna(0.0)
            positive_months = int((month_sum > 0.0).sum())
            total = float(month_sum.sum())
            strict_preview = (
                active_months >= canonical_policy_month_count
                and positive_months >= canonical_policy_month_count
                and total > 0.0
            )

            summary_rows.append({
                "level": "timestamp_market_state",
                "cluster_k": int(k),
                "cluster_id": int(cluster_id),
                "cluster_method": method,
                "diagnostic_horizon": int(horizon),
                "timestamp_count": int(len(cdf)),
                "active_months": active_months,
                "positive_months": positive_months,
                "canonical_month_count": canonical_policy_month_count,
                "strict_12_cluster_preview_pass": bool(strict_preview),
                "total_diagnostic_fut_mkt_ret_bps": total,
                "mean_diagnostic_fut_mkt_ret_bps": float(cdf[diag_col].mean()),
                "median_diagnostic_fut_mkt_ret_bps": float(cdf[diag_col].median()),
                "worst_month_bps": float(month_sum.min()),
                "best_month_bps": float(month_sum.max()),
                "month_net_bps": {str(m): float(v) for m, v in month_sum.to_dict().items()},
            })

    return summary_rows, membership_rows, centroid_rows


def evaluate_month_clusters(
    month_state: pd.DataFrame,
    labels: np.ndarray,
    k: int,
    method: str,
    feature_cols: List[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    work = month_state.copy()
    work["cluster_k"] = int(k)
    work["cluster_id"] = labels.astype(int)
    work["cluster_method"] = method

    membership_rows: List[Dict[str, Any]] = []
    centroid_rows: List[Dict[str, Any]] = []

    for _, row in work[["month", "cluster_k", "cluster_id", "cluster_method"]].iterrows():
        membership_rows.append({
            "level": "month_market_state",
            "month": row["month"],
            "cluster_k": int(row["cluster_k"]),
            "cluster_id": int(row["cluster_id"]),
            "cluster_method": row["cluster_method"],
        })

    for cluster_id in sorted(work["cluster_id"].dropna().unique().tolist()):
        cdf = work[work["cluster_id"] == cluster_id].copy()
        centroid = cdf[feature_cols].mean(numeric_only=True).to_dict()
        for feature_name, value in centroid.items():
            centroid_rows.append({
                "level": "month_market_state",
                "cluster_k": int(k),
                "cluster_id": int(cluster_id),
                "feature": feature_name,
                "centroid_value": float(value) if pd.notna(value) else None,
            })

    return membership_rows, centroid_rows


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS REGIME FIRST CLUSTER RUNNER v1")
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
        "timestamp_count",
        "month_state_count",
        "symbol_count",
        "row_count",
        "cluster_grid_count",
        "strict_12_cluster_preview_count",
        "elapsed_seconds",
        "panel_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("TOP CLUSTER DIAGNOSTICS")
    lines.append("-" * 100)
    for row in result.get("top_cluster_diagnostics", [])[:10]:
        lines.append(
            f"k={row.get('cluster_k')} cluster={row.get('cluster_id')} h={row.get('diagnostic_horizon')} | "
            f"strict12={row.get('strict_12_cluster_preview_pass')} | "
            f"positive={row.get('positive_months')}/{row.get('canonical_month_count')} | "
            f"total={row.get('total_diagnostic_fut_mkt_ret_bps')} | "
            f"worst={row.get('worst_month_bps')} | timestamps={row.get('timestamp_count')}"
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
        "cluster_summary_csv",
        "timestamp_membership_csv",
        "month_membership_csv",
        "feature_centroids_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS REGIME FIRST CLUSTER RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"timestamp_count: {result.get('timestamp_count')}")
    print(f"month_state_count: {result.get('month_state_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"cluster_grid_count: {result.get('cluster_grid_count')}")
    print(f"strict_12_cluster_preview_count: {result.get('strict_12_cluster_preview_count')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('cluster_summary_csv')}")
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
        "cluster_summary_csv": str(OUT_CLUSTER_SUMMARY_CSV),
        "timestamp_membership_csv": str(OUT_TIMESTAMP_MEMBERSHIP_CSV),
        "month_membership_csv": str(OUT_MONTH_MEMBERSHIP_CSV),
        "feature_centroids_csv": str(OUT_FEATURE_CENTROIDS_CSV),
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
                "runner_status": "REGIME_FIRST_CLUSTER_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_REGIME_FIRST_CONTRACT_NO_RELEASE",
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
                "runner_status": "REGIME_FIRST_CLUSTER_RUNNER_BLOCKED_NO_PANEL_FOUND",
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

        print("Building timestamp market-state table...")
        time_state = build_time_state(df)

        raw_months = sorted(time_state["month"].dropna().unique().tolist())
        canonical_months = derive_canonical_months_from_time_state(time_state, canonical_policy_month_count)

        timestamp_feature_cols = [
            c for c in time_state.columns
            if c not in {"time", "month"}
            and not c.startswith("diagnostic_fut_")
            and pd.api.types.is_numeric_dtype(time_state[c])
        ]

        # Prefer rank-normalized features for clustering to keep scale stable.
        timestamp_rank_cols = [c for c in timestamp_feature_cols if c.endswith("_time_rank_pct")]
        if len(timestamp_rank_cols) >= 10:
            timestamp_cluster_features = timestamp_rank_cols
        else:
            timestamp_cluster_features = timestamp_feature_cols

        print("Building month market-state table...")
        month_state = build_month_state(time_state, timestamp_cluster_features)

        month_feature_cols = [
            c for c in month_state.columns
            if c != "month"
            and not c.startswith("diagnostic_")
            and pd.api.types.is_numeric_dtype(month_state[c])
        ]

        print(f"Rows={len(df):,}, symbols={df['symbol'].nunique()}, timestamps={len(time_state):,}, months={len(raw_months)}")
        print(f"Timestamp features={len(timestamp_cluster_features)}, Month features={len(month_feature_cols)}")

        cluster_ks = [3, 4, 5, 6, 8]

        timestamp_x, timestamp_scale_stats = robust_scale_matrix(time_state, timestamp_cluster_features)
        month_x, month_scale_stats = robust_scale_matrix(month_state, month_feature_cols) if len(month_state) >= 3 else (np.empty((0, 0)), {})

        all_cluster_summary_rows: List[Dict[str, Any]] = []
        all_timestamp_membership_rows: List[Dict[str, Any]] = []
        all_month_membership_rows: List[Dict[str, Any]] = []
        all_centroid_rows: List[Dict[str, Any]] = []

        print("Running timestamp-level clusters...")
        for k in cluster_ks:
            if len(time_state) < k:
                continue

            labels, method = cluster_matrix(timestamp_x, k=k, random_state=42 + k)
            summary_rows, membership_rows, centroid_rows = evaluate_timestamp_clusters(
                time_state=time_state,
                labels=labels,
                k=k,
                method=method,
                feature_cols=timestamp_cluster_features,
                canonical_months=canonical_months,
                canonical_policy_month_count=canonical_policy_month_count,
            )

            all_cluster_summary_rows.extend(summary_rows)
            all_timestamp_membership_rows.extend(membership_rows)
            all_centroid_rows.extend(centroid_rows)
            print(f"Timestamp cluster k={k} method={method} summary_rows={len(summary_rows)}")

        print("Running month-level clusters...")
        for k in [3, 4, 5]:
            if len(month_state) < k or month_x.size == 0:
                continue

            labels, method = cluster_matrix(month_x, k=k, random_state=84 + k)
            membership_rows, centroid_rows = evaluate_month_clusters(
                month_state=month_state,
                labels=labels,
                k=k,
                method=method,
                feature_cols=month_feature_cols,
            )

            all_month_membership_rows.extend(membership_rows)
            all_centroid_rows.extend(centroid_rows)
            print(f"Month cluster k={k} method={method} membership_rows={len(membership_rows)}")

        cluster_summary = pd.DataFrame(all_cluster_summary_rows)
        timestamp_membership = pd.DataFrame(all_timestamp_membership_rows)
        month_membership = pd.DataFrame(all_month_membership_rows)
        centroids = pd.DataFrame(all_centroid_rows)

        strict_preview_count = 0
        top_cluster_diagnostics: List[Dict[str, Any]] = []

        if not cluster_summary.empty:
            strict_preview_count = int(cluster_summary["strict_12_cluster_preview_pass"].fillna(False).astype(bool).sum())
            cluster_summary = cluster_summary.sort_values(
                by=[
                    "strict_12_cluster_preview_pass",
                    "positive_months",
                    "total_diagnostic_fut_mkt_ret_bps",
                    "worst_month_bps",
                    "timestamp_count",
                ],
                ascending=[False, False, False, False, False],
            ).reset_index(drop=True)
            cluster_summary.to_csv(OUT_CLUSTER_SUMMARY_CSV, index=False)
            top_cluster_diagnostics = cluster_summary.head(20).to_dict(orient="records")
        else:
            pd.DataFrame().to_csv(OUT_CLUSTER_SUMMARY_CSV, index=False)

        if not timestamp_membership.empty:
            timestamp_membership.to_csv(OUT_TIMESTAMP_MEMBERSHIP_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_TIMESTAMP_MEMBERSHIP_CSV, index=False)

        if not month_membership.empty:
            month_membership.to_csv(OUT_MONTH_MEMBERSHIP_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_MONTH_MEMBERSHIP_CSV, index=False)

        if not centroids.empty:
            centroids.to_csv(OUT_FEATURE_CENTROIDS_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_FEATURE_CENTROIDS_CSV, index=False)

        if strict_preview_count > 0:
            runner_status = "REGIME_FIRST_CLUSTER_RUNNER_PREVIEW_CLUSTERS_FOUND_NOT_RELEASE_PASS"
            severity = "ATTENTION"
            next_action = "BUILD_REGIME_FIRST_CLUSTER_EVALUATOR_KEEP_ALL_ACTIONS_BLOCKED"
            reason = (
                f"cluster_grid_count={len(cluster_ks)}; "
                f"strict_12_cluster_preview_count={strict_preview_count}; "
                "preview_only_not_release"
            )
        else:
            runner_status = "REGIME_FIRST_CLUSTER_RUNNER_COMPLETE_NO_STRICT_CLUSTER_PREVIEW"
            severity = "ATTENTION"
            next_action = "BUILD_REGIME_FIRST_CLUSTER_EVALUATOR_OR_NEXT_RESEARCH_QUEUE_NO_RELEASE"
            reason = (
                f"cluster_grid_count={len(cluster_ks)}; "
                "strict_12_cluster_preview_count=0"
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
            "timestamp_count": int(len(time_state)),
            "month_state_count": int(len(month_state)),
            "raw_calendar_month_count": int(len(raw_months)),
            "raw_calendar_months": raw_months,
            "canonical_policy_month_count": canonical_policy_month_count,
            "canonical_policy_months": canonical_months,
            "timestamp_cluster_feature_count": int(len(timestamp_cluster_features)),
            "month_cluster_feature_count": int(len(month_feature_cols)),
            "timestamp_cluster_features": timestamp_cluster_features,
            "month_cluster_features": month_feature_cols,
            "timestamp_scale_stats": timestamp_scale_stats,
            "month_scale_stats": month_scale_stats,
            "cluster_k_grid": cluster_ks,
            "cluster_grid_count": int(len(cluster_ks)),
            "cluster_summary_row_count": int(len(all_cluster_summary_rows)),
            "timestamp_membership_row_count": int(len(all_timestamp_membership_rows)),
            "month_membership_row_count": int(len(all_month_membership_rows)),
            "centroid_row_count": int(len(all_centroid_rows)),
            "strict_12_cluster_preview_count": int(strict_preview_count),
            "top_cluster_diagnostics": top_cluster_diagnostics,
            "diagnostic_note": (
                "Cluster inputs use only pre-outcome features. diagnostic_fut_mkt_ret_* is used only after clustering "
                "to inspect whether discovered regimes have future-return structure. This is not a release pass."
            ),
            "release_gate_feed": {
                "REGIME_FIRST_CLUSTER_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "STRICT_12_CLUSTER_PREVIEW_COUNT": int(strict_preview_count),
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
            "runner_status": "REGIME_FIRST_CLUSTER_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_REGIME_CLUSTER_RUNNER_ERROR_NO_RELEASE_NO_RUNTIME_ACTION",
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
