#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Market Neutral Relative Value Archetype Runner v1
Patched/optimized diagnostic-only runner.

Safety contract:
- read-only research only
- no runtime touch
- no launcher
- no patch_runtime
- no candidate generation
- no family release
- no capital change
- no active paper
- no live
- no real orders

Main fixes:
1. Safe month helper prevents pandas timezone PeriodArray warning.
2. Feature/rank columns are computed once.
3. Rule evaluation avoids full panel copy per rule.
4. Uses vectorized np.bincount portfolio aggregation.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time as time_module
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_PATH = BASE_DIR / "edge_factory_os_research_direction_contracts" / "market_neutral_relative_value_archetype_contract_latest.json"

OUT_DIR = BASE_DIR / "edge_factory_os_market_neutral_relative_value_archetype_runner"
OUT_JSON = OUT_DIR / "market_neutral_relative_value_archetype_runner_latest.json"
OUT_CSV = OUT_DIR / "market_neutral_relative_value_archetype_ranked_rules_latest.csv"
OUT_TXT = OUT_DIR / "market_neutral_relative_value_archetype_runner_latest.txt"

RUNNER_NAME = "edge_factory_os_market_neutral_relative_value_archetype_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"


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


def now_utc_iso() -> str:
    return pd.Timestamp.utcnow().isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    tmp.replace(path)


def flatten_values(obj: Any) -> Iterable[Any]:
    if isinstance(obj, dict):
        for v in obj.values():
            yield from flatten_values(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from flatten_values(v)
    else:
        yield obj


def score_panel_path(path: Path) -> int:
    name = str(path).lower()
    score = 0
    for token, weight in [
        ("okx", 10),
        ("swap", 10),
        ("full", 8),
        ("1y", 8),
        ("one_year", 8),
        ("285", 7),
        ("panel", 7),
        ("universe", 6),
        ("ohlcv", 5),
        ("features", 4),
        ("parquet", 4),
    ]:
        if token in name:
            score += weight
    if path.suffix.lower() == ".parquet":
        score += 10
    if path.suffix.lower() == ".csv":
        score += 2
    try:
        score += min(int(path.stat().st_size / 50_000_000), 20)
    except Exception:
        pass
    return score


def find_panel_file(contract: Dict[str, Any]) -> Optional[Path]:
    explicit_candidates: List[Path] = []

    for v in flatten_values(contract):
        if isinstance(v, str):
            s = v.strip().strip('"')
            if s.lower().endswith((".parquet", ".csv", ".csv.gz")):
                p = Path(s)
                if p.exists():
                    explicit_candidates.append(p)

    if explicit_candidates:
        explicit_candidates = sorted(explicit_candidates, key=score_panel_path, reverse=True)
        return explicit_candidates[0]

    search_roots = [
        BASE_DIR,
        BASE_DIR / "edge_factory_universe",
        BASE_DIR / "edge_factory_universe_cache",
        BASE_DIR / "edge_factory_os_universe",
        BASE_DIR / "edge_factory_os_universe_cache",
        BASE_DIR / "edge_factory_os_data",
        BASE_DIR / "edge_factory_data",
    ]

    patterns = [
        "**/*okx*swap*1y*panel*.parquet",
        "**/*okx*swap*full*panel*.parquet",
        "**/*285*panel*.parquet",
        "**/*universe*panel*.parquet",
        "**/*panel*.parquet",
        "**/*ohlcv*.parquet",
        "**/*features*.parquet",
        "**/*okx*swap*1y*panel*.csv",
        "**/*285*panel*.csv",
        "**/*panel*.csv",
    ]

    found: Dict[Path, int] = {}

    for root in search_roots:
        if not root.exists():
            continue
        for pattern in patterns:
            try:
                for p in root.glob(pattern):
                    if p.is_file() and p.suffix.lower() in {".parquet", ".csv"}:
                        found[p] = score_panel_path(p)
            except Exception:
                continue

    if not found:
        return None

    return sorted(found.items(), key=lambda kv: kv[1], reverse=True)[0][0]


def read_panel(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported panel file: {path}")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        cc = str(c).strip()
        low = cc.lower().strip()
        low = low.replace(" ", "_").replace("-", "_")
        rename[c] = low
    df = df.rename(columns=rename)
    return df


def pick_col(df: pd.DataFrame, candidates: List[str], required: bool = True) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise ValueError(f"Missing required column. Tried: {candidates}. Available sample: {list(df.columns)[:50]}")
    return None


def safe_month_from_time(time_series: pd.Series) -> pd.Series:
    """
    Fix for:
    UserWarning: Converting to PeriodArray/Index representation will drop timezone information.

    We parse as UTC, then explicitly remove timezone before to_period("M").
    """
    t = pd.to_datetime(time_series, utc=True, errors="coerce")
    t = t.dt.tz_convert("UTC").dt.tz_localize(None)
    return t.dt.to_period("M").astype(str)


def safe_datetime_utc_naive(time_series: pd.Series) -> pd.Series:
    t = pd.to_datetime(time_series, utc=True, errors="coerce")
    return t.dt.tz_convert("UTC").dt.tz_localize(None)


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
        # If 13 calendar buckets exist because of partial edge months, use the most observation-dense 12.
        top = counts.loc[fullish].sort_values(ascending=False).head(canonical_policy_month_count).index.tolist()
        return sorted(top)

    return raw_months[-canonical_policy_month_count:]


def add_core_features(df: pd.DataFrame, price_col: str, symbol_col: str, time_col: str, volume_col: Optional[str]) -> Tuple[pd.DataFrame, List[str], List[int]]:
    df = df[[c for c in [time_col, symbol_col, price_col, volume_col] if c is not None and c in df.columns]].copy()

    if time_col != "time":
        df = df.rename(columns={time_col: "time"})
    if symbol_col != "symbol":
        df = df.rename(columns={symbol_col: "symbol"})
    if price_col != "close":
        df = df.rename(columns={price_col: "close"})
    if volume_col and volume_col != "volume":
        df = df.rename(columns={volume_col: "volume"})

    df["time"] = safe_datetime_utc_naive(df["time"])
    df["month"] = safe_month_from_time(df["time"])
    df["symbol"] = df["symbol"].astype(str)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    else:
        df["volume"] = np.nan

    df = df.dropna(subset=["time", "symbol", "close"]).sort_values(["symbol", "time"]).reset_index(drop=True)

    # One computation pass. No per-rule full copy.
    windows = [1, 3, 6, 12, 24]
    hold_windows = [1, 3, 6, 12]

    g = df.groupby("symbol", sort=False, observed=True)

    for w in windows:
        prev = g["close"].shift(w)
        df[f"ret_{w}_bps"] = ((df["close"] / prev) - 1.0) * 10000.0

    for h in hold_windows:
        fut = g["close"].shift(-h)
        df[f"fut_ret_{h}_bps"] = ((fut / df["close"]) - 1.0) * 10000.0

    # Cross-sectional market return per timestamp.
    for w in windows:
        col = f"ret_{w}_bps"
        df[f"mkt_ret_{w}_bps"] = df.groupby("time", sort=False, observed=True)[col].transform("mean")
        df[f"rel_ret_{w}_bps"] = df[col] - df[f"mkt_ret_{w}_bps"]

    # Rolling realized volatility by symbol.
    df["volatility_6"] = g["ret_1_bps"].transform(lambda s: s.rolling(6, min_periods=4).std())
    df["volatility_12"] = g["ret_1_bps"].transform(lambda s: s.rolling(12, min_periods=6).std())
    df["volatility_24"] = g["ret_1_bps"].transform(lambda s: s.rolling(24, min_periods=12).std())

    # Liquidity proxy.
    df["quote_liquidity_proxy"] = df["close"] * df["volume"]
    df["log_quote_liquidity_proxy"] = np.log1p(df["quote_liquidity_proxy"].clip(lower=0))

    # Relative liquidity deviation.
    df["liq_rank_pct"] = df.groupby("time", sort=False, observed=True)["log_quote_liquidity_proxy"].rank(pct=True)


    # Diagnostic safety fallback:
    # If the panel has no usable volume/liquidity data, liq_rank_pct becomes all NaN.
    # NaN >= min_liq_rank is always False, so every rule is silently killed.
    # For read-only research only, use pass-through liquidity when no usable liquidity exists.
    if df["liq_rank_pct"].notna().sum() == 0:
        df["liq_rank_pct"] = 1.0
        df["liquidity_filter_mode"] = "PASS_THROUGH_NO_USABLE_LIQUIDITY_COLUMN"
    else:
        df["liq_rank_pct"] = df["liq_rank_pct"].fillna(0.5)
        df["liquidity_filter_mode"] = "RANKED_LIQUIDITY_AVAILABLE"
    candidate_features = [
        "rel_ret_1_bps",
        "rel_ret_3_bps",
        "rel_ret_6_bps",
        "rel_ret_12_bps",
        "rel_ret_24_bps",
        "volatility_6",
        "volatility_12",
        "volatility_24",
        "log_quote_liquidity_proxy",
    ]

    features = [c for c in candidate_features if c in df.columns and df[c].notna().sum() > 1000]

    needed = ["time", "month", "symbol", "close", "liq_rank_pct"] + features + [f"fut_ret_{h}_bps" for h in hold_windows]
    df = df[needed].replace([np.inf, -np.inf], np.nan)

    # Compute percentile ranks once per feature.
    for feature in features:
        df[f"{feature}__rank_pct"] = df.groupby("time", sort=False, observed=True)[feature].rank(pct=True)

    return df, features, hold_windows


@dataclass
class RuleResult:
    rule_id: str
    feature: str
    direction: str
    quantile: float
    hold_bars: int
    min_liq_rank: float
    active_months: int
    positive_months: int
    canonical_month_count: int
    strict_12_subset_pass: bool
    event_count: int
    portfolio_bar_count: int
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
    feature: str,
    hold_bars: int,
    direction: str,
    q: float,
    min_liq_rank: float,
    canonical_months: List[str],
    canonical_policy_month_count: int,
    cost_bps_per_portfolio_bar: float = 4.0,
) -> Optional[RuleResult]:
    rank_col = f"{feature}__rank_pct"
    fut_col = f"fut_ret_{hold_bars}_bps"

    sub_cols = ["time", "month", rank_col, fut_col, "liq_rank_pct"]
    work = df[sub_cols].dropna()
    if work.empty:
        return None

    valid_month_mask = work["month"].isin(canonical_months).to_numpy()
    if not valid_month_mask.any():
        return None

    ranks = work[rank_col].to_numpy(dtype=np.float64)
    fut = work[fut_col].to_numpy(dtype=np.float64)
    liq = work["liq_rank_pct"].to_numpy(dtype=np.float64)

    liq_mask = liq >= min_liq_rank
    low_mask = (ranks <= q) & liq_mask & valid_month_mask
    high_mask = (ranks >= (1.0 - q)) & liq_mask & valid_month_mask

    if direction == "mean_revert":
        long_mask = low_mask
        short_mask = high_mask
    elif direction == "momentum":
        long_mask = high_mask
        short_mask = low_mask
    else:
        return None

    event_count = int(long_mask.sum() + short_mask.sum())
    if event_count < 100:
        return None

    time_codes, time_uniques = pd.factorize(work["time"], sort=True)
    month_for_time = pd.Series(work["month"].to_numpy()).groupby(time_codes).first().to_numpy()

    n_times = len(time_uniques)

    long_count = np.bincount(time_codes[long_mask], minlength=n_times).astype(np.float64)
    short_count = np.bincount(time_codes[short_mask], minlength=n_times).astype(np.float64)

    both = (long_count > 0) & (short_count > 0)
    portfolio_bar_count = int(both.sum())
    if portfolio_bar_count < 50:
        return None

    long_sum = np.bincount(time_codes[long_mask], weights=fut[long_mask], minlength=n_times)
    short_sum = np.bincount(time_codes[short_mask], weights=fut[short_mask], minlength=n_times)

    long_avg = np.zeros(n_times, dtype=np.float64)
    short_avg = np.zeros(n_times, dtype=np.float64)

    long_avg[both] = long_sum[both] / long_count[both]
    short_avg[both] = short_sum[both] / short_count[both]

    bar_ret = long_avg[both] - short_avg[both] - cost_bps_per_portfolio_bar
    bar_months = month_for_time[both]

    if len(bar_ret) == 0:
        return None

    month_df = pd.DataFrame({"month": bar_months, "net_bps": bar_ret})
    month_net = month_df.groupby("month", observed=True)["net_bps"].sum().reindex(canonical_months).fillna(0.0)

    active_months = int((month_net != 0.0).sum())
    positive_months = int((month_net > 0.0).sum())

    strict_pass = (
        active_months >= canonical_policy_month_count
        and positive_months >= canonical_policy_month_count
        and float(month_net.sum()) > 0.0
    )

    fail_reasons = []
    if active_months < canonical_policy_month_count:
        fail_reasons.append(f"active_months_below_{canonical_policy_month_count}")
    if positive_months < canonical_policy_month_count:
        fail_reasons.append(f"positive_months_below_{canonical_policy_month_count}")
    if float(month_net.sum()) <= 0.0:
        fail_reasons.append("total_net_bps_not_positive")

    rule_id = f"{feature}|{direction}|q={q}|hold={hold_bars}|liq>={min_liq_rank}"

    return RuleResult(
        rule_id=rule_id,
        feature=feature,
        direction=direction,
        quantile=float(q),
        hold_bars=int(hold_bars),
        min_liq_rank=float(min_liq_rank),
        active_months=active_months,
        positive_months=positive_months,
        canonical_month_count=canonical_policy_month_count,
        strict_12_subset_pass=bool(strict_pass),
        event_count=event_count,
        portfolio_bar_count=portfolio_bar_count,
        total_net_bps=float(month_net.sum()),
        mean_bar_net_bps=float(np.mean(bar_ret)),
        median_bar_net_bps=float(np.median(bar_ret)),
        positive_bar_rate=float(np.mean(bar_ret > 0.0)),
        worst_month_bps=float(month_net.min()),
        best_month_bps=float(month_net.max()),
        month_net_bps={str(k): float(v) for k, v in month_net.to_dict().items()},
        fail_reasons=fail_reasons,
    )


def build_rule_grid(features: List[str], hold_windows: List[int]) -> List[Tuple[str, int, str, float, float]]:
    directions = ["mean_revert", "momentum"]
    quantiles = [0.10, 0.15, 0.20]
    min_liq_ranks = [0.00, 0.20, 0.40]

    grid = []
    for feature in features:
        for hold in hold_windows:
            for direction in directions:
                for q in quantiles:
                    for min_liq in min_liq_ranks:
                        grid.append((feature, hold, direction, q, min_liq))
    return grid


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_PATH)

    canonical_policy_month_count = int(
        contract.get("canonical_policy_month_count")
        or contract.get("strict_policy", {}).get("canonical_policy_month_count", 12)
        or 12
    )

    if canonical_policy_month_count != 12:
        # Force current project rule.
        canonical_policy_month_count = 12

    result: Dict[str, Any] = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": now_utc_iso(),
        "runner_status": "MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_RUNNER_STARTED",
        "severity": "INFO",
        "allowed_scope": "READ_ONLY_RESEARCH",
        "next_action": "RUNNER_IN_PROGRESS",
        "strict_policy_key": STRICT_POLICY_KEY,
        "canonical_policy_month_count": canonical_policy_month_count,
        "contract_path": str(CONTRACT_PATH),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        **SAFETY_FLAGS,
    }

    try:
        panel_path = find_panel_file(contract)
        result["panel_path"] = str(panel_path) if panel_path else None

        if panel_path is None:
            result.update({
                "runner_status": "MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_RUNNER_BLOCKED_NO_PANEL_FOUND",
                "severity": "ATTENTION",
                "next_action": "LOCATE_FULL_1Y_OKX_SWAP_PANEL_AND_RERUN",
                "error": "No parquet/csv panel file found from contract paths or BASE_DIR search.",
            })
            write_json(OUT_JSON, result)
            print_summary(result)
            return 2

        print(f"Loading panel: {panel_path}")
        raw = read_panel(panel_path)
        raw = normalize_columns(raw)

        time_col = pick_col(raw, ["time", "timestamp", "datetime", "date", "open_time", "ts"])
        symbol_col = pick_col(raw, ["symbol", "instid", "instrument", "ticker", "coin"])
        price_col = pick_col(raw, ["close", "c", "last", "price", "mark_price"])
        volume_col = pick_col(raw, ["volume", "vol", "quote_volume", "quote_vol", "volume_quote", "turnover"], required=False)

        print(f"Columns: time={time_col}, symbol={symbol_col}, price={price_col}, volume={volume_col}")
        print("Precomputing feature table once...")
        df, features, hold_windows = add_core_features(raw, price_col, symbol_col, time_col, volume_col)

        raw_months = sorted(df["month"].dropna().unique().tolist())
        canonical_months = derive_canonical_months(df, canonical_policy_month_count)

        rule_grid = build_rule_grid(features, hold_windows)
        print(f"Prepared rows={len(df):,}, symbols={df['symbol'].nunique()}, raw_months={len(raw_months)}, canonical_months={len(canonical_months)}")
        print(f"Features={len(features)}, rules={len(rule_grid)}")

        results: List[RuleResult] = []
        strict_pass_count = 0

        for i, (feature, hold, direction, q, min_liq) in enumerate(rule_grid, start=1):
            rr = evaluate_rule_fast(
                df=df,
                feature=feature,
                hold_bars=hold,
                direction=direction,
                q=q,
                min_liq_rank=min_liq,
                canonical_months=canonical_months,
                canonical_policy_month_count=canonical_policy_month_count,
            )
            if rr is not None:
                results.append(rr)
                if rr.strict_12_subset_pass:
                    strict_pass_count += 1

            if i % 100 == 0 or i == len(rule_grid):
                print(f"Evaluated {i}/{len(rule_grid)} rules | kept={len(results)} | strict12={strict_pass_count}")

        rows = [asdict(r) for r in results]
        ranked = pd.DataFrame(rows)

        if ranked.empty:
            runner_status = "MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_RUNNER_NO_VALID_RULES"
            next_action = "ROTATE_OR_BUILD_NEXT_RESEARCH_DIRECTION_NO_RELEASE"
            severity = "ATTENTION"
        else:
            ranked = ranked.sort_values(
                by=["strict_12_subset_pass", "positive_months", "total_net_bps", "worst_month_bps"],
                ascending=[False, False, False, False],
            ).reset_index(drop=True)
            ranked.to_csv(OUT_CSV, index=False)

            if strict_pass_count > 0:
                runner_status = "MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_RUNNER_STRICT_12_PREVIEW_FOUND_NOT_RELEASE_PASS"
                next_action = "BUILD_EVALUATOR_AND_RELEASE_GATE_REVIEW_KEEP_ACTIONS_BLOCKED"
                severity = "ATTENTION"
            else:
                runner_status = "MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_RUNNER_BRANCH_NO_STRICT_12_PASS"
                next_action = "BUILD_EVALUATOR_TO_CLOSE_OR_ROTATE_BRANCH_NO_RELEASE"
                severity = "ATTENTION"

        top_rules = []
        if not ranked.empty:
            for _, row in ranked.head(20).iterrows():
                d = row.to_dict()
                if isinstance(d.get("month_net_bps"), str):
                    pass
                top_rules.append(d)

        result.update({
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "panel_path": str(panel_path),
            "row_count": int(len(df)),
            "symbol_count": int(df["symbol"].nunique()),
            "raw_calendar_month_count": int(len(raw_months)),
            "raw_calendar_months": raw_months,
            "canonical_policy_month_count": canonical_policy_month_count,
            "canonical_policy_months": canonical_months,
            "feature_count": int(len(features)),
            "features": features,
            "rules_tested": int(len(rule_grid)),
            "valid_rule_count": int(len(results)),
            "strict_12_subset_pass_count": int(strict_pass_count),
            "ranked_rules_csv": str(OUT_CSV) if not ranked.empty else None,
            "top_rules": top_rules,
            "release_gate_feed": {
                "MARKET_NEUTRAL_RELATIVE_VALUE_RUNNER_RAN": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "STRICT_12_SUBSET_PASS_COUNT": int(strict_pass_count),
                "RELEASE_PASS_FROM_THIS_RUNNER": False,
                "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_RUNNER": False,
                "FAMILY_RELEASE_ALLOWED_FROM_THIS_RUNNER": False,
            },
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        })

        write_json(OUT_JSON, result)
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 0

    except Exception as e:
        result.update({
            "runner_status": "MARKET_NEUTRAL_RELATIVE_VALUE_ARCHETYPE_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": "INSPECT_RUNNER_ERROR_NO_RELEASE_NO_RUNTIME_ACTION",
            "error_type": type(e).__name__,
            "error": str(e),
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        })
        write_json(OUT_JSON, result)
        print_summary(result)
        return 1


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS MARKET NEUTRAL RELATIVE VALUE ARCHETYPE RUNNER v1")
    lines.append("=" * 100)
    for k in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "strict_policy_key",
        "canonical_policy_month_count",
        "raw_calendar_month_count",
        "feature_count",
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
            f"total_net_bps={r.get('total_net_bps')} | worst_month={r.get('worst_month_bps')}"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS MARKET NEUTRAL RELATIVE VALUE ARCHETYPE RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"strict_policy_key: {result.get('strict_policy_key')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
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
    print(f"JSON: {OUT_JSON}")
    if result.get("ranked_rules_csv"):
        print(f"CSV : {result.get('ranked_rules_csv')}")
    print("=" * 100)


if __name__ == "__main__":
    raise SystemExit(main())
