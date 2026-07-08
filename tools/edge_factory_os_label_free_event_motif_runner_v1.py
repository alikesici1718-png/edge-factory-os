#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Label-Free Event Motif Runner v1

Purpose:
- Mine recurring event motifs from pre-outcome return/range/vol/liquidity state bins.
- Use future returns only after motif discovery for diagnostic preview.
- Enforce STRICT_MONTH_STABILITY_12_OF_12 as preview policy.
- Keep all action flags blocked.

This runner does NOT:
- generate candidates
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

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "label_free_event_motif_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_label_free_event_motif_runner"
OUT_JSON = OUT_DIR / "label_free_event_motif_runner_latest.json"
OUT_TXT = OUT_DIR / "label_free_event_motif_runner_latest.txt"
OUT_RANKED_CSV = OUT_DIR / "label_free_event_motif_ranked_motifs_latest.csv"
OUT_FREQ_CSV = OUT_DIR / "label_free_event_motif_frequency_latest.csv"
OUT_MONTH_CSV = OUT_DIR / "label_free_event_motif_month_coverage_latest.csv"
OUT_SYMBOL_CSV = OUT_DIR / "label_free_event_motif_symbol_coverage_latest.csv"

RUNNER_NAME = "edge_factory_os_label_free_event_motif_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "LABEL_FREE_EVENT_MOTIF_CONTRACT_READY"
REQUIRED_DIRECTION_QUEUE_KEY = "RD4_02_LABEL_FREE_EVENT_MOTIF_MINING"

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
        low = str(c).strip().lower().replace(" ", "_").replace("-", "_")
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


def qcut_bin(series: pd.Series, labels: List[str], fallback_mid: str) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
    non_na = s.dropna()

    if non_na.nunique() < len(labels):
        return pd.Series([fallback_mid] * len(series), index=series.index, dtype="object")

    try:
        out = pd.qcut(s, q=len(labels), labels=labels, duplicates="drop")
        out = out.astype("object").where(out.notna(), fallback_mid)
        return out.astype(str)
    except Exception:
        return pd.Series([fallback_mid] * len(series), index=series.index, dtype="object")


def signed_return_bin(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
    med_abs = float(np.nanmedian(np.abs(s.to_numpy(dtype=np.float64)))) if s.notna().any() else 25.0
    if not np.isfinite(med_abs) or med_abs < 1e-9:
        med_abs = 25.0

    large = med_abs * 2.0
    medium = med_abs * 0.75

    arr = s.to_numpy(dtype=np.float64)
    out = np.full(len(arr), "flat", dtype=object)
    out[arr <= -large] = "large_down"
    out[(arr > -large) & (arr <= -medium)] = "medium_down"
    out[(arr >= medium) & (arr < large)] = "medium_up"
    out[arr >= large] = "large_up"
    out[~np.isfinite(arr)] = "flat"
    return pd.Series(out, index=series.index, dtype="object")


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

    for w in [1, 3, 6, 12, 24]:
        prev = g["close"].shift(w)
        df[f"ret_{w}_bps"] = ((df["close"] / prev) - 1.0) * 10000.0

    for h in [1, 3, 6, 12]:
        fut = g["close"].shift(-h)
        df[f"fut_ret_{h}_bps"] = ((fut / df["close"]) - 1.0) * 10000.0

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

    column_map = {
        "time_col": time_col,
        "symbol_col": symbol_col,
        "close_col": close_col,
        "volume_col": volume_col,
        "high_col": high_col,
        "low_col": low_col,
    }

    return df, column_map


def add_state_bins(df: pd.DataFrame) -> pd.DataFrame:
    """
    All bins are pre-outcome/present-state only. No future returns used here.
    """
    out = df.copy()

    out["ret3_bin"] = signed_return_bin(out["ret_3_bps"])
    out["ret6_bin"] = signed_return_bin(out["ret_6_bps"])
    out["rel3_bin"] = signed_return_bin(out["rel_ret_3_bps"])
    out["rel6_bin"] = signed_return_bin(out["rel_ret_6_bps"])

    out["range_bin"] = qcut_bin(out["entry_range_bps"], ["range_low", "range_mid", "range_high"], "range_mid")
    out["vol_bin"] = qcut_bin(out["coin_vol_6_bps"], ["vol_low", "vol_mid", "vol_high"], "vol_mid")
    out["liq_bin"] = qcut_bin(out["log_quote_liquidity_proxy"], ["liq_low", "liq_mid", "liq_high"], "liq_mid")

    # Cross-sectional rank bins by timestamp.
    for col, prefix in [
        ("ret_3_bps", "xr3"),
        ("ret_6_bps", "xr6"),
        ("rel_ret_3_bps", "xrel3"),
        ("rel_ret_6_bps", "xrel6"),
    ]:
        rank = out.groupby("time", sort=False, observed=True)[col].rank(pct=True)
        out[f"{prefix}_rank_bin"] = pd.cut(
            rank,
            bins=[-0.01, 0.33, 0.67, 1.01],
            labels=[f"{prefix}_weak", f"{prefix}_neutral", f"{prefix}_strong"],
        ).astype("object").where(rank.notna(), f"{prefix}_neutral").astype(str)

    # Compact token. This is the basic event alphabet.
    out["event_token"] = (
        out["ret3_bin"].astype(str)
        + "|"
        + out["rel3_bin"].astype(str)
        + "|"
        + out["range_bin"].astype(str)
        + "|"
        + out["vol_bin"].astype(str)
        + "|"
        + out["xrel3_rank_bin"].astype(str)
        + "|"
        + out["liq_bin"].astype(str)
    )

    # Simpler token for wider support / less overfitting.
    out["event_token_simple"] = (
        out["ret3_bin"].astype(str)
        + "|"
        + out["range_bin"].astype(str)
        + "|"
        + out["vol_bin"].astype(str)
        + "|"
        + out["xrel3_rank_bin"].astype(str)
    )

    return out


def build_sequence_keys(df: pd.DataFrame, token_col: str, lengths: List[int]) -> pd.DataFrame:
    """
    Build symbol-level rolling motif sequences using only current/past event tokens.
    """
    work = df[["time", "month", "symbol", token_col, "fut_ret_1_bps", "fut_ret_3_bps", "fut_ret_6_bps", "fut_ret_12_bps"]].copy()
    work[token_col] = work[token_col].astype(str)

    g = work.groupby("symbol", sort=False, observed=True)

    for n in lengths:
        parts = []
        for lag in range(n - 1, -1, -1):
            parts.append(g[token_col].shift(lag).astype("object"))

        key = parts[0]
        valid = key.notna()
        for part in parts[1:]:
            valid = valid & part.notna()
            key = key.astype(str) + ">" + part.astype(str)

        work[f"motif_seq_{n}"] = key.where(valid, None)

    return work


def build_market_sequence_keys(df: pd.DataFrame, lengths: List[int]) -> pd.DataFrame:
    """
    Timestamp cross-sectional event sequence motifs.
    This uses only current/past market-state summaries, not future.
    """
    state = df.groupby("time", sort=True, observed=True).agg(
        month=("month", "first"),
        ret3_mean=("ret_3_bps", "mean"),
        ret3_std=("ret_3_bps", "std"),
        rel3_std=("rel_ret_3_bps", "std"),
        range_median=("entry_range_bps", "median"),
        vol_median=("coin_vol_6_bps", "median"),
        liq_median=("log_quote_liquidity_proxy", "median"),
        fut_ret_1_bps=("fut_ret_1_bps", "mean"),
        fut_ret_3_bps=("fut_ret_3_bps", "mean"),
        fut_ret_6_bps=("fut_ret_6_bps", "mean"),
        fut_ret_12_bps=("fut_ret_12_bps", "mean"),
    ).reset_index()

    state["mret_bin"] = signed_return_bin(state["ret3_mean"])
    state["disp_bin"] = qcut_bin(state["ret3_std"], ["disp_low", "disp_mid", "disp_high"], "disp_mid")
    state["range_bin"] = qcut_bin(state["range_median"], ["range_low", "range_mid", "range_high"], "range_mid")
    state["vol_bin"] = qcut_bin(state["vol_median"], ["vol_low", "vol_mid", "vol_high"], "vol_mid")

    state["market_token"] = (
        state["mret_bin"].astype(str)
        + "|"
        + state["disp_bin"].astype(str)
        + "|"
        + state["range_bin"].astype(str)
        + "|"
        + state["vol_bin"].astype(str)
    )

    for n in lengths:
        parts = []
        for lag in range(n - 1, -1, -1):
            parts.append(state["market_token"].shift(lag).astype("object"))

        key = parts[0]
        valid = key.notna()
        for part in parts[1:]:
            valid = valid & part.notna()
            key = key.astype(str) + ">" + part.astype(str)

        state[f"market_motif_seq_{n}"] = key.where(valid, None)

    return state


def summarize_motifs(
    events: pd.DataFrame,
    motif_col: str,
    motif_level: str,
    canonical_months: List[str],
    canonical_policy_month_count: int,
    min_occurrences: int,
    max_motifs: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Discovery phase:
    - Select motifs by frequency only.
    Diagnostic phase:
    - Compute future-return metrics after frequency selection.
    """
    if motif_col not in events.columns:
        return [], [], [], []

    base_cols = ["time", "month", motif_col, "fut_ret_1_bps", "fut_ret_3_bps", "fut_ret_6_bps", "fut_ret_12_bps"]
    if "symbol" in events.columns:
        base_cols.append("symbol")

    work = events[base_cols].dropna(subset=[motif_col, "month"]).copy()
    if work.empty:
        return [], [], [], []

    freq = work.groupby(motif_col, observed=True).size().reset_index(name="occurrence_count")
    freq = freq[freq["occurrence_count"] >= min_occurrences].copy()
    if freq.empty:
        return [], [], [], []

    freq = freq.sort_values("occurrence_count", ascending=False).head(max_motifs).reset_index(drop=True)
    selected = set(freq[motif_col].astype(str).tolist())

    work[motif_col] = work[motif_col].astype(str)
    work = work[work[motif_col].isin(selected)].copy()
    if work.empty:
        return [], [], [], []

    ranked_rows: List[Dict[str, Any]] = []
    frequency_rows: List[Dict[str, Any]] = []
    month_rows: List[Dict[str, Any]] = []
    symbol_rows: List[Dict[str, Any]] = []

    freq_map = dict(zip(freq[motif_col].astype(str), freq["occurrence_count"].astype(int)))

    for motif_key in selected:
        mdf = work[work[motif_col] == motif_key].copy()
        if mdf.empty:
            continue

        occurrence_count = int(freq_map.get(motif_key, len(mdf)))
        active_months = int(mdf["month"].isin(canonical_months).groupby(mdf["month"]).any().reindex(canonical_months).fillna(False).sum())

        unique_symbols = int(mdf["symbol"].nunique()) if "symbol" in mdf.columns else 0
        top_symbol_share = 0.0
        if "symbol" in mdf.columns and len(mdf) > 0:
            top_symbol_share = float(mdf["symbol"].value_counts(normalize=True).iloc[0])

            sym_counts = mdf["symbol"].value_counts().head(30)
            for symbol, count in sym_counts.items():
                symbol_rows.append({
                    "motif_level": motif_level,
                    "motif_col": motif_col,
                    "motif_key": motif_key,
                    "symbol": symbol,
                    "occurrence_count": int(count),
                    "share": float(count / len(mdf)),
                })

        for _, frow in freq[freq[motif_col].astype(str) == motif_key].iterrows():
            frequency_rows.append({
                "motif_level": motif_level,
                "motif_col": motif_col,
                "motif_key": motif_key,
                "occurrence_count": int(frow["occurrence_count"]),
            })

        for h in [1, 3, 6, 12]:
            fut_col = f"fut_ret_{h}_bps"
            tmp = mdf.dropna(subset=[fut_col]).copy()
            if tmp.empty:
                continue

            month_sum = tmp.groupby("month", observed=True)[fut_col].mean().reindex(canonical_months).fillna(0.0)
            month_count = tmp.groupby("month", observed=True).size().reindex(canonical_months).fillna(0)

            positive_months = int((month_sum > 0.0).sum())
            active_months_h = int((month_count > 0).sum())
            total = float(month_sum.sum())

            strict_preview = (
                active_months_h >= canonical_policy_month_count
                and positive_months >= canonical_policy_month_count
                and total > 0.0
            )

            for m in canonical_months:
                month_rows.append({
                    "motif_level": motif_level,
                    "motif_col": motif_col,
                    "motif_key": motif_key,
                    "horizon": int(h),
                    "month": m,
                    "occurrence_count": int(month_count.loc[m]),
                    "diagnostic_mean_fut_ret_bps": float(month_sum.loc[m]),
                    "positive_month": bool(month_sum.loc[m] > 0.0),
                })

            ranked_rows.append({
                "motif_level": motif_level,
                "motif_col": motif_col,
                "motif_key": motif_key,
                "horizon": int(h),
                "occurrence_count": occurrence_count,
                "active_months": active_months_h,
                "positive_months": positive_months,
                "canonical_month_count": canonical_policy_month_count,
                "strict_12_motif_preview_pass": bool(strict_preview),
                "diagnostic_total_month_mean_fut_ret_bps": total,
                "diagnostic_mean_fut_ret_bps": float(tmp[fut_col].mean()),
                "diagnostic_median_fut_ret_bps": float(tmp[fut_col].median()),
                "diagnostic_win_rate": float((tmp[fut_col] > 0.0).mean()),
                "worst_month_bps": float(month_sum.min()),
                "best_month_bps": float(month_sum.max()),
                "unique_symbols": unique_symbols,
                "top_symbol_share": top_symbol_share,
                "motif_discovery_uses_future": False,
                "future_used_only_for_diagnostic": True,
            })

    return ranked_rows, frequency_rows, month_rows, symbol_rows


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS LABEL-FREE EVENT MOTIF RUNNER v1")
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
        "motif_count",
        "ranked_motif_row_count",
        "strict_12_motif_preview_count",
        "elapsed_seconds",
        "panel_path",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("TOP MOTIF DIAGNOSTICS")
    lines.append("-" * 100)
    for row in result.get("top_motif_diagnostics", [])[:10]:
        lines.append(
            f"{row.get('motif_level')} {row.get('motif_col')} h={row.get('horizon')} | "
            f"strict12={row.get('strict_12_motif_preview_pass')} | "
            f"positive={row.get('positive_months')}/{row.get('canonical_month_count')} | "
            f"total={row.get('diagnostic_total_month_mean_fut_ret_bps')} | "
            f"worst={row.get('worst_month_bps')} | occ={row.get('occurrence_count')} | "
            f"symbols={row.get('unique_symbols')}"
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
        "ranked_motifs_csv",
        "frequency_csv",
        "month_coverage_csv",
        "symbol_coverage_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS LABEL-FREE EVENT MOTIF RUNNER v1")
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
    print(f"motif_count: {result.get('motif_count')}")
    print(f"ranked_motif_row_count: {result.get('ranked_motif_row_count')}")
    print(f"strict_12_motif_preview_count: {result.get('strict_12_motif_preview_count')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('ranked_motifs_csv')}")
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
        "ranked_motifs_csv": str(OUT_RANKED_CSV),
        "frequency_csv": str(OUT_FREQ_CSV),
        "month_coverage_csv": str(OUT_MONTH_CSV),
        "symbol_coverage_csv": str(OUT_SYMBOL_CSV),
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
                "runner_status": "LABEL_FREE_EVENT_MOTIF_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_LABEL_FREE_EVENT_MOTIF_CONTRACT_NO_RELEASE",
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
                "runner_status": "LABEL_FREE_EVENT_MOTIF_RUNNER_BLOCKED_NO_PANEL_FOUND",
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

        print("Building pre-outcome state bins...")
        df = add_state_bins(df)

        raw_months = sorted(df["month"].dropna().unique().tolist())
        canonical_months = derive_canonical_months(df, canonical_policy_month_count)

        print(f"Rows={len(df):,}, symbols={df['symbol'].nunique()}, raw_months={len(raw_months)}, canonical_months={len(canonical_months)}")

        sequence_lengths = [3, 4, 6, 8, 12]

        print("Building symbol-level motif sequences...")
        symbol_events_simple = build_sequence_keys(df, token_col="event_token_simple", lengths=sequence_lengths)
        symbol_events_full = build_sequence_keys(df, token_col="event_token", lengths=[3, 4, 6])

        print("Building market-level motif sequences...")
        market_events = build_market_sequence_keys(df, lengths=sequence_lengths)

        ranked_rows: List[Dict[str, Any]] = []
        freq_rows: List[Dict[str, Any]] = []
        month_rows: List[Dict[str, Any]] = []
        symbol_rows: List[Dict[str, Any]] = []

        motif_jobs = []

        for n in sequence_lengths:
            motif_jobs.append(("symbol_event_sequence_simple", symbol_events_simple, f"motif_seq_{n}", max(250, int(len(df) * 0.001)), 300))
        for n in [3, 4, 6]:
            motif_jobs.append(("symbol_event_sequence_full", symbol_events_full, f"motif_seq_{n}", max(200, int(len(df) * 0.0008)), 250))
        for n in sequence_lengths:
            motif_jobs.append(("market_state_event_sequence", market_events, f"market_motif_seq_{n}", 20, 200))

        print(f"Motif jobs={len(motif_jobs)}")

        for i, (level, events, motif_col, min_occ, max_motifs) in enumerate(motif_jobs, start=1):
            print(f"Mining job {i}/{len(motif_jobs)} level={level} col={motif_col} min_occ={min_occ}")
            rr, fr, mr, sr = summarize_motifs(
                events=events,
                motif_col=motif_col,
                motif_level=level,
                canonical_months=canonical_months,
                canonical_policy_month_count=canonical_policy_month_count,
                min_occurrences=int(min_occ),
                max_motifs=int(max_motifs),
            )
            ranked_rows.extend(rr)
            freq_rows.extend(fr)
            month_rows.extend(mr)
            symbol_rows.extend(sr)
            print(f"  added ranked={len(rr)} freq={len(fr)} month={len(mr)} symbol={len(sr)}")

        ranked = pd.DataFrame(ranked_rows)
        freq = pd.DataFrame(freq_rows)
        month_cov = pd.DataFrame(month_rows)
        symbol_cov = pd.DataFrame(symbol_rows)

        motif_count = int(freq["motif_key"].nunique()) if not freq.empty and "motif_key" in freq.columns else 0
        strict_preview_count = 0
        top_motif_diagnostics: List[Dict[str, Any]] = []

        if not ranked.empty:
            strict_preview_count = int(ranked["strict_12_motif_preview_pass"].fillna(False).astype(bool).sum())
            ranked = ranked.sort_values(
                by=[
                    "strict_12_motif_preview_pass",
                    "positive_months",
                    "diagnostic_total_month_mean_fut_ret_bps",
                    "worst_month_bps",
                    "occurrence_count",
                    "unique_symbols",
                ],
                ascending=[False, False, False, False, False, False],
            ).reset_index(drop=True)
            ranked.to_csv(OUT_RANKED_CSV, index=False)
            top_motif_diagnostics = ranked.head(20).to_dict(orient="records")
        else:
            pd.DataFrame().to_csv(OUT_RANKED_CSV, index=False)

        if not freq.empty:
            freq.to_csv(OUT_FREQ_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_FREQ_CSV, index=False)

        if not month_cov.empty:
            month_cov.to_csv(OUT_MONTH_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_MONTH_CSV, index=False)

        if not symbol_cov.empty:
            symbol_cov.to_csv(OUT_SYMBOL_CSV, index=False)
        else:
            pd.DataFrame().to_csv(OUT_SYMBOL_CSV, index=False)

        if strict_preview_count > 0:
            runner_status = "LABEL_FREE_EVENT_MOTIF_RUNNER_STRICT_12_PREVIEW_FOUND_NOT_RELEASE_PASS"
            severity = "ATTENTION"
            next_action = "BUILD_LABEL_FREE_EVENT_MOTIF_EVALUATOR_AND_DEEP_VALIDATION_KEEP_ACTIONS_BLOCKED"
            reason = (
                f"motif_count={motif_count}; ranked_motif_row_count={len(ranked)}; "
                f"strict_12_motif_preview_count={strict_preview_count}; preview_only_not_release"
            )
        else:
            runner_status = "LABEL_FREE_EVENT_MOTIF_RUNNER_COMPLETE_NO_STRICT_MOTIF_PREVIEW"
            severity = "ATTENTION"
            next_action = "BUILD_LABEL_FREE_EVENT_MOTIF_EVALUATOR_OR_ROTATE_NO_RELEASE"
            reason = (
                f"motif_count={motif_count}; ranked_motif_row_count={len(ranked)}; "
                "strict_12_motif_preview_count=0"
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
            "sequence_lengths": sequence_lengths,
            "motif_jobs_count": int(len(motif_jobs)),
            "motif_count": motif_count,
            "frequency_row_count": int(len(freq)),
            "ranked_motif_row_count": int(len(ranked)),
            "month_coverage_row_count": int(len(month_cov)),
            "symbol_coverage_row_count": int(len(symbol_cov)),
            "strict_12_motif_preview_count": int(strict_preview_count),
            "top_motif_diagnostics": top_motif_diagnostics,
            "discovery_integrity": {
                "motif_discovery_uses_future": False,
                "future_used_only_for_diagnostic": True,
                "forbidden_inputs_excluded": [
                    "future_return",
                    "future_pnl",
                    "future_win_loss",
                    "month_outcome_label",
                    "manual_month_blacklist",
                    "manual_symbol_whitelist",
                    "post_outcome_selected_motif",
                ],
            },
            "release_gate_feed": {
                "LABEL_FREE_EVENT_MOTIF_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "STRICT_12_MOTIF_PREVIEW_COUNT": int(strict_preview_count),
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
            "runner_status": "LABEL_FREE_EVENT_MOTIF_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_LABEL_FREE_EVENT_MOTIF_RUNNER_ERROR_NO_RELEASE",
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
