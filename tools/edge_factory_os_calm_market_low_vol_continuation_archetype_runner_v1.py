#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Calm Market Low-Vol Continuation Archetype Runner v1

Purpose:
- Run read-only/offline archetype scan for RD3_03:
  CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH.
- Search for low-volatility calm-market continuation patterns.
- Enforce STRICT_MONTH_STABILITY_12_OF_12 as preview policy.
- Never enable candidate/family/runtime/capital/live/real-order actions.

Safety:
- READ_ONLY_RESEARCH only.
- No runtime touch.
- No launcher.
- No patch_runtime.
- No candidate generation.
- No family release.
- No capital change.
- No active paper.
- No live.
- No real orders.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import time as time_module
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_PATH = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "calm_market_low_vol_continuation_archetype_contract_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_calm_market_low_vol_continuation_archetype_runner"
OUT_JSON = OUT_DIR / "calm_market_low_vol_continuation_archetype_runner_latest.json"
OUT_CSV = OUT_DIR / "calm_market_low_vol_continuation_archetype_ranked_rules_latest.csv"
OUT_TXT = OUT_DIR / "calm_market_low_vol_continuation_archetype_runner_latest.txt"

RUNNER_NAME = "edge_factory_os_calm_market_low_vol_continuation_archetype_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

REQUIRED_BUILDER_STATUS = "RESEARCH_DIRECTION_CONTRACT_V5_READY"
REQUIRED_DIRECTION_QUEUE_KEY = "RD3_03_CALM_MARKET_LOW_VOL_CONTINUATION_ARCHETYPE_SEARCH"

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
    except Exception:
        return default


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
        cc = str(c).strip()
        low = cc.lower().strip()
        low = low.replace(" ", "_").replace("-", "_")
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
        ("285", 15),
        ("1y", 15),
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
        BASE_DIR / "edge_factory_os_data",
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


def add_feature_table(
    raw: pd.DataFrame,
    time_col: str,
    symbol_col: str,
    close_col: str,
    volume_col: Optional[str],
    high_col: Optional[str],
    low_col: Optional[str],
) -> pd.DataFrame:
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
    hold_windows = [1, 3, 6, 12]

    for w in ret_windows:
        prev = g["close"].shift(w)
        df[f"ret_{w}_bps"] = ((df["close"] / prev) - 1.0) * 10000.0

    for h in hold_windows:
        fut = g["close"].shift(-h)
        df[f"fut_ret_{h}_bps"] = ((fut / df["close"]) - 1.0) * 10000.0

    for w in ret_windows:
        rcol = f"ret_{w}_bps"
        df[f"mkt_ret_{w}_bps"] = df.groupby("time", sort=False, observed=True)[rcol].transform("mean")
        df[f"rel_ret_{w}_bps"] = df[rcol] - df[f"mkt_ret_{w}_bps"]

    df["coin_vol_6_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(6, min_periods=4).std())
    df["coin_vol_12_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(12, min_periods=6).std())
    df["coin_vol_24_bps"] = g["ret_1_bps"].transform(lambda s: s.rolling(24, min_periods=12).std())

    # Market volatility by timestamp: cross-sectional std of 1-bar returns.
    df["mkt_cross_vol_1_bps"] = df.groupby("time", sort=False, observed=True)["ret_1_bps"].transform("std")
    df["mkt_cross_vol_3_bps"] = df.groupby("time", sort=False, observed=True)["ret_3_bps"].transform("std")
    df["mkt_cross_vol_6_bps"] = df.groupby("time", sort=False, observed=True)["ret_6_bps"].transform("std")

    # Entry range proxy: real high-low range if available, otherwise abs recent return proxy.
    real_range = ((df["high"] - df["low"]) / df["close"]) * 10000.0
    proxy_range = df["ret_1_bps"].abs()
    df["entry_range_bps"] = real_range.where(real_range.notna(), proxy_range)

    # Liquidity rank. If volume unusable, pass-through.
    df["quote_liquidity_proxy"] = df["close"] * df["volume"]
    df["log_quote_liquidity_proxy"] = np.log1p(df["quote_liquidity_proxy"].clip(lower=0))
    df["liq_rank_pct"] = df.groupby("time", sort=False, observed=True)["log_quote_liquidity_proxy"].rank(pct=True)

    if df["liq_rank_pct"].notna().sum() == 0:
        df["liq_rank_pct"] = 1.0
        df["liquidity_filter_mode"] = "PASS_THROUGH_NO_USABLE_LIQUIDITY_COLUMN"
    else:
        df["liq_rank_pct"] = df["liq_rank_pct"].fillna(0.5)
        df["liquidity_filter_mode"] = "RANKED_LIQUIDITY_AVAILABLE"

    rank_features = [
        "coin_vol_6_bps",
        "coin_vol_12_bps",
        "coin_vol_24_bps",
        "mkt_cross_vol_1_bps",
        "mkt_cross_vol_3_bps",
        "mkt_cross_vol_6_bps",
        "entry_range_bps",
        "ret_3_bps",
        "ret_6_bps",
        "ret_12_bps",
        "rel_ret_3_bps",
        "rel_ret_6_bps",
        "rel_ret_12_bps",
    ]

    # Rank features correctly:
    # - coin/entry features are cross-sectional and should be ranked within each timestamp.
    # - market-wide volatility features are timestamp-level; every symbol has the same value
    #   at a given timestamp. Ranking them within the same timestamp makes their pct-rank
    #   approximately 0.50+, which silently kills filters like <=0.25/<=0.35/<=0.50.
    #   Therefore market volatility must be ranked across timestamps, then merged back.
    timestamp_level_rank_features = {
        "mkt_cross_vol_1_bps",
        "mkt_cross_vol_3_bps",
        "mkt_cross_vol_6_bps",
    }

    for col in rank_features:
        if col not in df.columns:
            continue

        rank_col = f"{col}__rank_pct"

        if col in timestamp_level_rank_features:
            time_rank = (
                df[["time", col]]
                .dropna()
                .drop_duplicates(subset=["time"])
                .sort_values("time")
                .copy()
            )
            time_rank[rank_col] = time_rank[col].rank(pct=True)
            df = df.merge(time_rank[["time", rank_col]], on="time", how="left")
        else:
            df[rank_col] = df.groupby("time", sort=False, observed=True)[col].rank(pct=True)

    needed = [
        "time",
        "month",
        "symbol",
        "close",
        "liq_rank_pct",
        "liquidity_filter_mode",
        "entry_range_bps",
        "coin_vol_6_bps",
        "coin_vol_12_bps",
        "coin_vol_24_bps",
        "mkt_cross_vol_1_bps",
        "mkt_cross_vol_3_bps",
        "mkt_cross_vol_6_bps",
        "ret_3_bps",
        "ret_6_bps",
        "ret_12_bps",
        "mkt_ret_3_bps",
        "mkt_ret_6_bps",
        "mkt_ret_12_bps",
        "rel_ret_3_bps",
        "rel_ret_6_bps",
        "rel_ret_12_bps",
        "fut_ret_1_bps",
        "fut_ret_3_bps",
        "fut_ret_6_bps",
        "fut_ret_12_bps",
    ]

    for col in rank_features:
        r = f"{col}__rank_pct"
        if r in df.columns:
            needed.append(r)

    needed = [c for c in needed if c in df.columns]
    return df[needed].replace([np.inf, -np.inf], np.nan)


@dataclass
class RuleResult:
    rule_id: str
    hold_bars: int
    trend_horizon: int
    vol_window: int
    trend_min_bps: float
    trend_max_bps: float
    rel_min_bps: float
    mkt_min_bps: float
    coin_vol_rank_max: float
    mkt_vol_rank_max: float
    range_rank_max: float
    min_liq_rank: float
    cost_bps: float
    active_months: int
    positive_months: int
    canonical_month_count: int
    strict_12_subset_pass: bool
    event_count: int
    portfolio_bar_count: int
    symbol_count: int
    total_net_bps: float
    mean_bar_net_bps: float
    median_bar_net_bps: float
    positive_bar_rate: float
    worst_month_bps: float
    best_month_bps: float
    month_net_bps: Dict[str, float]
    fail_reasons: List[str]


def evaluate_rule_fast(
    df: pd.DataFrame,
    canonical_months: List[str],
    canonical_policy_month_count: int,
    hold_bars: int,
    trend_horizon: int,
    vol_window: int,
    trend_min_bps: float,
    trend_max_bps: float,
    rel_min_bps: float,
    mkt_min_bps: float,
    coin_vol_rank_max: float,
    mkt_vol_rank_max: float,
    range_rank_max: float,
    min_liq_rank: float,
    cost_bps: float,
) -> Optional[RuleResult]:
    fut_col = f"fut_ret_{hold_bars}_bps"
    trend_col = f"ret_{trend_horizon}_bps"
    rel_col = f"rel_ret_{trend_horizon}_bps"
    mkt_col = f"mkt_ret_{trend_horizon}_bps"
    coin_vol_rank_col = f"coin_vol_{vol_window}_bps__rank_pct"

    # Use closest market vol rank.
    if vol_window <= 6:
        mkt_vol_rank_col = "mkt_cross_vol_3_bps__rank_pct"
    else:
        mkt_vol_rank_col = "mkt_cross_vol_6_bps__rank_pct"

    range_rank_col = "entry_range_bps__rank_pct"

    required = [
        "time",
        "month",
        "symbol",
        "liq_rank_pct",
        fut_col,
        trend_col,
        rel_col,
        mkt_col,
        coin_vol_rank_col,
        mkt_vol_rank_col,
        range_rank_col,
    ]

    for c in required:
        if c not in df.columns:
            return None

    work = df[required].dropna()
    if work.empty:
        return None

    month_mask = work["month"].isin(canonical_months).to_numpy()
    if not month_mask.any():
        return None

    fut = work[fut_col].to_numpy(dtype=np.float64)
    trend = work[trend_col].to_numpy(dtype=np.float64)
    rel = work[rel_col].to_numpy(dtype=np.float64)
    mkt = work[mkt_col].to_numpy(dtype=np.float64)
    coin_vol_rank = work[coin_vol_rank_col].to_numpy(dtype=np.float64)
    mkt_vol_rank = work[mkt_vol_rank_col].to_numpy(dtype=np.float64)
    range_rank = work[range_rank_col].to_numpy(dtype=np.float64)
    liq_rank = work["liq_rank_pct"].to_numpy(dtype=np.float64)

    signal_mask = (
        month_mask
        & (trend >= trend_min_bps)
        & (trend <= trend_max_bps)
        & (rel >= rel_min_bps)
        & (mkt >= mkt_min_bps)
        & (coin_vol_rank <= coin_vol_rank_max)
        & (mkt_vol_rank <= mkt_vol_rank_max)
        & (range_rank <= range_rank_max)
        & (liq_rank >= min_liq_rank)
    )

    event_count = int(signal_mask.sum())
    if event_count < 100:
        return None

    selected = work.loc[signal_mask, ["time", "month", "symbol"]].copy()
    selected["fut"] = fut[signal_mask] - cost_bps

    symbol_count = int(selected["symbol"].nunique())
    if symbol_count < 25:
        return None

    # Equal-weight per timestamp portfolio.
    bar = selected.groupby(["time", "month"], observed=True)["fut"].mean().reset_index(name="bar_net_bps")
    portfolio_bar_count = int(len(bar))
    if portfolio_bar_count < 50:
        return None

    month_net = bar.groupby("month", observed=True)["bar_net_bps"].sum().reindex(canonical_months).fillna(0.0)

    active_months = int((month_net != 0.0).sum())
    positive_months = int((month_net > 0.0).sum())
    total_net_bps = float(month_net.sum())

    strict = (
        active_months >= canonical_policy_month_count
        and positive_months >= canonical_policy_month_count
        and total_net_bps > 0.0
    )

    fail_reasons: List[str] = []
    if active_months < canonical_policy_month_count:
        fail_reasons.append(f"active_months_below_{canonical_policy_month_count}")
    if positive_months < canonical_policy_month_count:
        fail_reasons.append(f"positive_months_below_{canonical_policy_month_count}")
    if total_net_bps <= 0.0:
        fail_reasons.append("total_net_bps_not_positive")
    if symbol_count < 50:
        fail_reasons.append("symbol_count_below_50_soft_warning")

    rule_id = (
        f"calm_low_vol_cont|hold={hold_bars}|trend={trend_horizon}|vol={vol_window}|"
        f"trend=[{trend_min_bps},{trend_max_bps}]|rel>={rel_min_bps}|mkt>={mkt_min_bps}|"
        f"coinvol_rank<={coin_vol_rank_max}|mktvol_rank<={mkt_vol_rank_max}|"
        f"range_rank<={range_rank_max}|liq>={min_liq_rank}|cost={cost_bps}"
    )

    vals = bar["bar_net_bps"].to_numpy(dtype=np.float64)

    return RuleResult(
        rule_id=rule_id,
        hold_bars=int(hold_bars),
        trend_horizon=int(trend_horizon),
        vol_window=int(vol_window),
        trend_min_bps=float(trend_min_bps),
        trend_max_bps=float(trend_max_bps),
        rel_min_bps=float(rel_min_bps),
        mkt_min_bps=float(mkt_min_bps),
        coin_vol_rank_max=float(coin_vol_rank_max),
        mkt_vol_rank_max=float(mkt_vol_rank_max),
        range_rank_max=float(range_rank_max),
        min_liq_rank=float(min_liq_rank),
        cost_bps=float(cost_bps),
        active_months=active_months,
        positive_months=positive_months,
        canonical_month_count=canonical_policy_month_count,
        strict_12_subset_pass=bool(strict),
        event_count=event_count,
        portfolio_bar_count=portfolio_bar_count,
        symbol_count=symbol_count,
        total_net_bps=total_net_bps,
        mean_bar_net_bps=float(np.mean(vals)),
        median_bar_net_bps=float(np.median(vals)),
        positive_bar_rate=float(np.mean(vals > 0.0)),
        worst_month_bps=float(month_net.min()),
        best_month_bps=float(month_net.max()),
        month_net_bps={str(k): float(v) for k, v in month_net.to_dict().items()},
        fail_reasons=fail_reasons,
    )


def build_rule_grid() -> List[Dict[str, Any]]:
    grid: List[Dict[str, Any]] = []

    holds = [1, 3, 6, 12]
    trend_horizons = [3, 6, 12]
    vol_windows = [6, 12, 24]

    trend_ranges = [
        (10.0, 150.0),
        (25.0, 250.0),
        (50.0, 350.0),
        (0.0, 200.0),
    ]

    rel_mins = [0.0, 15.0, 30.0]
    mkt_mins = [-25.0, 0.0, 15.0]
    coin_vol_rank_maxes = [0.20, 0.30, 0.40]
    mkt_vol_rank_maxes = [0.25, 0.35, 0.50]
    range_rank_maxes = [0.35, 0.50, 0.65]
    min_liq_ranks = [0.0, 0.20]
    costs = [25.0, 50.0, 75.0]

    for hold in holds:
        for th in trend_horizons:
            for vw in vol_windows:
                for tr_min, tr_max in trend_ranges:
                    for rel_min in rel_mins:
                        for mkt_min in mkt_mins:
                            for coin_v in coin_vol_rank_maxes:
                                for mkt_v in mkt_vol_rank_maxes:
                                    for range_v in range_rank_maxes:
                                        for liq in min_liq_ranks:
                                            for cost in costs:
                                                # Keep grid bounded but diverse.
                                                if hold > 6 and cost == 25.0:
                                                    continue
                                                if th == 12 and hold == 1:
                                                    continue
                                                if tr_min >= tr_max:
                                                    continue
                                                grid.append({
                                                    "hold_bars": hold,
                                                    "trend_horizon": th,
                                                    "vol_window": vw,
                                                    "trend_min_bps": tr_min,
                                                    "trend_max_bps": tr_max,
                                                    "rel_min_bps": rel_min,
                                                    "mkt_min_bps": mkt_min,
                                                    "coin_vol_rank_max": coin_v,
                                                    "mkt_vol_rank_max": mkt_v,
                                                    "range_rank_max": range_v,
                                                    "min_liq_rank": liq,
                                                    "cost_bps": cost,
                                                })

    # Cap to a deterministic but still broad set so runtime stays acceptable.
    # 3,888-ish evaluations is enough for this branch without exploding runtime.
    dedup: Dict[str, Dict[str, Any]] = {}
    for item in grid:
        key = json.dumps(item, sort_keys=True)
        dedup[key] = item

    return list(dedup.values())[:4000]


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS CALM MARKET LOW-VOL CONTINUATION ARCHETYPE RUNNER v1")
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
        "rules_tested",
        "valid_rule_count",
        "strict_12_subset_pass_count",
        "elapsed_seconds",
        "panel_path",
        "ranked_rules_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("TOP RULES")
    lines.append("-" * 100)
    for r in result.get("top_rules", [])[:10]:
        lines.append(
            f"{r.get('rule_id')} | strict12={r.get('strict_12_subset_pass')} | "
            f"positive={r.get('positive_months')}/{r.get('canonical_month_count')} | "
            f"total={r.get('total_net_bps')} | worst={r.get('worst_month_bps')} | "
            f"symbols={r.get('symbol_count')} | events={r.get('event_count')}"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS CALM MARKET LOW-VOL CONTINUATION ARCHETYPE RUNNER v1")
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
    print(f"rules_tested: {result.get('rules_tested')}")
    print(f"valid_rule_count: {result.get('valid_rule_count')}")
    print(f"strict_12_subset_pass_count: {result.get('strict_12_subset_pass_count')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    if result.get("ranked_rules_csv"):
        print(f"CSV : {result.get('ranked_rules_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_PATH, default={})

    canonical_policy_month_count = int(contract.get("canonical_policy_month_count") or 12)
    if canonical_policy_month_count != 12:
        canonical_policy_month_count = 12

    prerequisite_pass = (
        contract.get("builder_status") == REQUIRED_BUILDER_STATUS
        and contract.get("direction_queue_key") == REQUIRED_DIRECTION_QUEUE_KEY
        and canonical_policy_month_count == 12
    )

    base_result: Dict[str, Any] = {
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
        "ranked_rules_csv": str(OUT_CSV),
        "summary_path": str(OUT_TXT),
        **SAFETY_FLAGS,
    }

    try:
        if not prerequisite_pass:
            result = {
                **base_result,
                "runner_status": "CALM_MARKET_LOW_VOL_CONTINUATION_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_CONTRACT_BUILDER_V5_OUTPUT_NO_RELEASE",
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
                "runner_status": "CALM_MARKET_LOW_VOL_CONTINUATION_RUNNER_BLOCKED_NO_PANEL_FOUND",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "LOCATE_FULL_UNIVERSE_PANEL_AND_RERUN_NO_RELEASE",
                "reason": "No parquet panel found from contract panel_candidates or workspace search.",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        print(f"Loading panel: {panel_path}")
        raw = read_panel(panel_path)
        raw = normalize_columns(raw)

        time_col = pick_col(raw, ["time", "timestamp", "datetime", "date", "open_time", "ts"])
        symbol_col = pick_col(raw, ["symbol", "instid", "instrument", "ticker", "coin"])
        close_col = pick_col(raw, ["close", "c", "last", "price", "mark_price"])
        volume_col = pick_col(raw, ["volume", "vol", "quote_volume", "quote_vol", "volume_quote", "turnover"], required=False)
        high_col = pick_col(raw, ["high", "h"], required=False)
        low_col = pick_col(raw, ["low", "l"], required=False)

        print(f"Columns: time={time_col}, symbol={symbol_col}, close={close_col}, volume={volume_col}, high={high_col}, low={low_col}")
        print("Building feature table once...")
        df = add_feature_table(raw, time_col, symbol_col, close_col, volume_col, high_col, low_col)

        raw_months = sorted(df["month"].dropna().unique().tolist())
        canonical_months = derive_canonical_months(df, canonical_policy_month_count)

        rule_grid = build_rule_grid()

        print(f"Rows={len(df):,}, symbols={df['symbol'].nunique()}, raw_months={len(raw_months)}, canonical_months={len(canonical_months)}")
        print(f"Rules scheduled={len(rule_grid)}")
        print(f"Liquidity mode sample={df['liquidity_filter_mode'].dropna().iloc[0] if 'liquidity_filter_mode' in df.columns and df['liquidity_filter_mode'].notna().any() else 'UNKNOWN'}")

        results: List[RuleResult] = []
        strict_count = 0

        for i, params in enumerate(rule_grid, start=1):
            rr = evaluate_rule_fast(
                df=df,
                canonical_months=canonical_months,
                canonical_policy_month_count=canonical_policy_month_count,
                **params,
            )

            if rr is not None:
                results.append(rr)
                if rr.strict_12_subset_pass:
                    strict_count += 1

            if i % 250 == 0 or i == len(rule_grid):
                print(f"Evaluated {i}/{len(rule_grid)} | valid={len(results)} | strict12={strict_count}")

        rows = [asdict(r) for r in results]
        ranked = pd.DataFrame(rows)

        if ranked.empty:
            runner_status = "CALM_MARKET_LOW_VOL_CONTINUATION_RUNNER_NO_VALID_RULES"
            severity = "ATTENTION"
            next_action = "BUILD_EVALUATOR_TO_CLOSE_OR_EXPAND_SEARCH_SPACE_NO_RELEASE"
            reason = f"rules_tested={len(rule_grid)}; valid_rule_count=0"
            ranked_csv = None
            top_rules: List[Dict[str, Any]] = []
        else:
            ranked = ranked.sort_values(
                by=[
                    "strict_12_subset_pass",
                    "positive_months",
                    "total_net_bps",
                    "worst_month_bps",
                    "symbol_count",
                    "event_count",
                ],
                ascending=[False, False, False, False, False, False],
            ).reset_index(drop=True)

            ranked.to_csv(OUT_CSV, index=False)
            ranked_csv = str(OUT_CSV)

            top_rules = ranked.head(20).to_dict(orient="records")

            if strict_count > 0:
                runner_status = "CALM_MARKET_LOW_VOL_CONTINUATION_RUNNER_STRICT_12_PREVIEW_FOUND_NOT_RELEASE_PASS"
                severity = "ATTENTION"
                next_action = "BUILD_EVALUATOR_AND_DEEP_VALIDATION_KEEP_ALL_ACTIONS_BLOCKED"
                reason = (
                    f"rules_tested={len(rule_grid)}; valid_rule_count={len(results)}; "
                    f"strict_12_subset_pass_count={strict_count}; preview_only_not_release"
                )
            else:
                runner_status = "CALM_MARKET_LOW_VOL_CONTINUATION_RUNNER_BRANCH_NO_STRICT_12_PASS"
                severity = "ATTENTION"
                next_action = "BUILD_EVALUATOR_TO_CLOSE_OR_ROTATE_BRANCH_NO_RELEASE"
                reason = (
                    f"rules_tested={len(rule_grid)}; valid_rule_count={len(results)}; "
                    "strict_12_subset_pass_count=0"
                )

        result = {
            **base_result,
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "reason": reason,
            "panel_path": str(panel_path),
            "time_col": time_col,
            "symbol_col": symbol_col,
            "close_col": close_col,
            "volume_col": volume_col,
            "high_col": high_col,
            "low_col": low_col,
            "row_count": int(len(df)),
            "symbol_count": int(df["symbol"].nunique()),
            "raw_calendar_month_count": int(len(raw_months)),
            "raw_calendar_months": raw_months,
            "canonical_policy_month_count": canonical_policy_month_count,
            "canonical_policy_months": canonical_months,
            "rules_tested": int(len(rule_grid)),
            "valid_rule_count": int(len(results)),
            "strict_12_subset_pass_count": int(strict_count),
            "ranked_rules_csv": ranked_csv,
            "top_rules": top_rules,
            "release_gate_feed": {
                "CALM_MARKET_LOW_VOL_CONTINUATION_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "STRICT_12_SUBSET_PASS_COUNT": int(strict_count),
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
            "runner_status": "CALM_MARKET_LOW_VOL_CONTINUATION_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_RUNNER_ERROR_NO_RELEASE_NO_RUNTIME_ACTION",
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
