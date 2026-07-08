#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY ROLLING OUT-OF-SAMPLE VALIDATOR v1
===============================================

Purpose
-------
Offline validator for the Edge Factory OS.

This module tries to break candidate strategy families BEFORE paper/live boot.
It scans historical/backtest outputs, normalizes trade-like rows, then evaluates:

1) Time out-of-sample behavior
2) Rolling/monthly stability
3) Symbol/coin distribution robustness
4) Train-vs-test degradation
5) Bad-window concentration
6) Candidate lifecycle recommendation seed

It does NOT start paper trading.
It does NOT place orders.
It does NOT edit logger scripts.
It only reads historical files and writes validation outputs.

Run
---
    python "C:\Users\alike\edge_factory_rolling_oos_validator.py"

Optional explicit file:
    python "C:\Users\alike\edge_factory_rolling_oos_validator.py" --input_file "C:\path\to\trades.csv"

Default workspace:
    C:\Users\alike\OneDrive\Desktop\edge_lab_new

Outputs
-------
    <workspace>\edge_factory_rolling_oos_validator\rolling_oos_YYYYMMDD_HHMMSS\
        rolling_oos_report.md
        rolling_oos_family_summary.csv
        rolling_oos_family_summary.json
        rolling_oos_window_metrics.csv
        rolling_oos_symbol_metrics.csv
        rolling_oos_decisions.json
        normalized_oos_trades.csv
        source_file_scan.json

Decision labels
---------------
    STRONG_CANDIDATE
    PASS_CANDIDATE
    WATCH_WEAK_OOS
    REDUCE_OR_BACKUP_ONLY
    REJECT_OR_DISABLE
    INSUFFICIENT_DATA
    NO_USABLE_DATA

Important
---------
This is not a final trading verdict. It is a conservative offline filter.
Its job is to stop obviously fragile families from reaching paper/live too easily.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

KNOWN_FAMILIES = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
    "session_short",
]

ACTIVE_FAMILIES = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
]

# Current MASTER_UPPER_SYSTEM roles. Used only for reporting context.
CURRENT_ROLES = {
    "old_short": "CORE_ENGINE",
    "impulse_long": "HIGH_PRIORITY_DIVERSIFIER",
    "market_relative_short": "CAPPED_HALF_SIZE",
    "weak_market_short": "BACKUP_ONLY",
    "session_short": "DISABLED",
}

# Directories that are likely to contain useful historical/offline outputs.
PREFERRED_SCAN_DIRS = [
    "portfolio_family_overlap_validation",
    "edge_factory_master_optimizer",
    "edge_factory_bad_day_investigation",
    "edge_factory_guarded_allocator_optimizer",
    "edge_factory_capital_governor",
    "edge_factory_position_sizing_contract",
]

# Directories to skip because they are raw/heavy/live/generated-by-this-script.
SKIP_DIR_PATTERNS = [
    "edge_factory_rolling_oos_validator",
    "edge_factory_os_state",
    "edge_factory_drift_monitor",
    "paper_run_gate_master_upper_system",
    "live_",
    "paper_",
    "cache",
    "raw",
    "backup_",
    "__pycache__",
    ".git",
]


@dataclass
class SourceFileRecord:
    path: str
    status: str
    rows: int
    normalized_rows: int
    inferred_families: List[str]
    message: str


@dataclass
class Metrics:
    trade_count: int
    total_pnl: float
    avg_pnl: float
    median_pnl: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    p05_pnl: float
    p95_pnl: float
    avg_return_bps: Optional[float]
    median_return_bps: Optional[float]


@dataclass
class FamilyDecision:
    family_key: str
    current_role: str
    decision: str
    confidence: str
    reasons: List[str]
    metrics: Dict[str, Any]
    oos_metrics: Dict[str, Any]
    window_metrics: Dict[str, Any]
    symbol_metrics: Dict[str, Any]
    recommended_lifecycle_seed: str
    recommended_capital_hint: str


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def norm_col(c: Any) -> str:
    s = str(c).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def safe_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        if isinstance(x, str):
            s = x.strip().replace("%", "")
            if s == "" or s.lower() in {"none", "null", "nan", "inf", "infinity"}:
                return None
            return float(s)
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def find_col(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    mapping = {norm_col(c): c for c in df.columns}
    for cand in candidates:
        key = norm_col(cand)
        if key in mapping:
            return mapping[key]
    normed = [(norm_col(c), c) for c in df.columns]
    for cand in candidates:
        key = norm_col(cand)
        for nc, orig in normed:
            if key == nc or key in nc:
                return orig
    return None


def parse_time_series(s: pd.Series) -> pd.Series:
    if s is None:
        return pd.Series(pd.NaT, index=[])
    if pd.api.types.is_numeric_dtype(s):
        vals = pd.to_numeric(s, errors="coerce")
        med = vals.dropna().median() if vals.notna().any() else np.nan
        if pd.isna(med):
            return pd.to_datetime(vals, errors="coerce")
        if med > 1e17:
            return pd.to_datetime(vals, unit="ns", errors="coerce")
        if med > 1e14:
            return pd.to_datetime(vals, unit="us", errors="coerce")
        if med > 1e11:
            return pd.to_datetime(vals, unit="ms", errors="coerce")
        return pd.to_datetime(vals, unit="s", errors="coerce")
    return pd.to_datetime(s, errors="coerce")


def infer_family_from_text(text: str) -> Optional[str]:
    s = text.lower().replace("-", "_").replace(" ", "_")
    for fam in KNOWN_FAMILIES:
        if fam in s:
            return fam
    if "impulse" in s and "long" in s:
        return "impulse_long"
    if "market" in s and "relative" in s:
        return "market_relative_short"
    if "weak" in s and ("market" in s or "breakdown" in s):
        return "weak_market_short"
    if "old" in s and "short" in s:
        return "old_short"
    if "session" in s and "short" in s:
        return "session_short"
    return None


def normalize_family_value(x: Any, fallback_text: str = "") -> str:
    fam = infer_family_from_text(str(x)) if x is not None else None
    if fam:
        return fam
    fam = infer_family_from_text(fallback_text)
    if fam:
        return fam
    if x is None:
        return "unknown"
    s = str(x).strip().lower().replace("-", "_").replace(" ", "_")
    return s if s else "unknown"


def profit_factor(pnls: Sequence[float]) -> float:
    arr = np.asarray(list(pnls), dtype=float)
    if arr.size == 0:
        return 0.0
    gains = arr[arr > 0].sum()
    losses = -arr[arr < 0].sum()
    if losses <= 0 and gains > 0:
        return float("inf")
    if losses <= 0:
        return 0.0
    return float(gains / losses)


def max_drawdown(pnls: Sequence[float]) -> float:
    arr = np.asarray(list(pnls), dtype=float)
    if arr.size == 0:
        return 0.0
    equity = np.cumsum(arr)
    peak = np.maximum.accumulate(equity)
    dd = equity - peak
    return float(dd.min())


def compute_metrics(df: pd.DataFrame) -> Metrics:
    if df.empty:
        return Metrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, None)
    pnls = pd.to_numeric(df["pnl"], errors="coerce").dropna()
    if pnls.empty:
        return Metrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, None)
    rbps = pd.to_numeric(df.get("return_bps", pd.Series(dtype=float)), errors="coerce").dropna()
    return Metrics(
        trade_count=int(len(pnls)),
        total_pnl=float(pnls.sum()),
        avg_pnl=float(pnls.mean()),
        median_pnl=float(pnls.median()),
        win_rate=float((pnls > 0).mean()),
        profit_factor=profit_factor(pnls.tolist()),
        max_drawdown=max_drawdown(pnls.tolist()),
        p05_pnl=float(pnls.quantile(0.05)),
        p95_pnl=float(pnls.quantile(0.95)),
        avg_return_bps=float(rbps.mean()) if not rbps.empty else None,
        median_return_bps=float(rbps.median()) if not rbps.empty else None,
    )


def read_table(path: Path) -> Optional[pd.DataFrame]:
    try:
        suf = path.suffix.lower()
        if suf == ".csv":
            try:
                return pd.read_csv(path)
            except Exception:
                return pd.read_csv(path, engine="python", on_bad_lines="skip")
        if suf in {".parquet", ".pq"}:
            return pd.read_parquet(path)
        if suf == ".jsonl":
            return pd.read_json(path, lines=True)
        if suf == ".json":
            with path.open("r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, list):
                return pd.DataFrame(obj)
            if isinstance(obj, dict):
                for key in ["trades", "closed_trades", "rows", "records", "data", "results", "summary"]:
                    node = obj.get(key)
                    if isinstance(node, list):
                        return pd.DataFrame(node)
                # Dict of family -> metrics/trades.
                rows: List[Dict[str, Any]] = []
                for k, v in obj.items():
                    if isinstance(v, dict):
                        r = dict(v)
                        r.setdefault("family_key", k)
                        rows.append(r)
                if rows:
                    return pd.DataFrame(rows)
                return pd.DataFrame([obj])
    except Exception:
        return None
    return None


def is_skip_dir(path: Path) -> bool:
    s = str(path).lower().replace("-", "_")
    return any(pat in s for pat in SKIP_DIR_PATTERNS)


def is_candidate_file(path: Path) -> bool:
    if path.suffix.lower() not in {".csv", ".json", ".jsonl", ".parquet", ".pq"}:
        return False
    s = str(path).lower().replace("-", "_")
    if is_skip_dir(path.parent):
        return False
    positive_terms = [
        "trade", "trades", "backtest", "family", "portfolio", "validation",
        "optimizer", "result", "summary", "candidate", "walkforward", "walk_forward",
        "oos", "out_of_sample", "pnl",
    ]
    negative_terms = [
        "contract", "config", "state_report", "task_queue", "scan", "health",
        "readme", "requirements", "file_scan", "normalized_oos",
    ]
    if any(t in s for t in negative_terms):
        return False
    if any(fam in s for fam in KNOWN_FAMILIES):
        return True
    return any(t in s for t in positive_terms)


def discover_files(workspace: Path, input_file: Optional[Path]) -> List[Path]:
    if input_file:
        return [input_file] if input_file.exists() else []

    files: List[Path] = []

    # Prefer known output directories first.
    for d in PREFERRED_SCAN_DIRS:
        root = workspace / d
        if not root.exists():
            continue
        for r, dirs, fns in os.walk(root):
            rpath = Path(r)
            dirs[:] = [x for x in dirs if not is_skip_dir(rpath / x)]
            for fn in fns:
                p = rpath / fn
                if is_candidate_file(p):
                    files.append(p)

    # Then shallow scan workspace for useful result files, avoiding raw/cache/live.
    for r, dirs, fns in os.walk(workspace):
        rpath = Path(r)
        if is_skip_dir(rpath):
            dirs[:] = []
            continue
        # Avoid scanning too deeply into unrelated huge directories by relying on skip patterns.
        dirs[:] = [x for x in dirs if not is_skip_dir(rpath / x)]
        for fn in fns:
            p = rpath / fn
            if is_candidate_file(p):
                files.append(p)

    # De-dupe and sort newest first.
    unique = sorted(set(files), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return unique[:300]


def normalize_trade_like_rows(path: Path, df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    raw = df.copy()
    raw.columns = [str(c) for c in raw.columns]
    path_text = str(path)

    family_col = find_col(raw, [
        "family_key", "family", "strategy_family", "strategy", "strategy_name",
        "system", "label", "candidate", "family_name",
    ])
    symbol_col = find_col(raw, ["symbol", "inst_id", "instrument", "coin", "ticker", "market", "asset"])
    side_col = find_col(raw, ["side", "direction", "position_side", "trade_side"])
    variant_col = find_col(raw, ["variant", "param_set", "config", "config_name", "model", "rule", "setup"])

    time_col = find_col(raw, [
        "close_time", "exit_time", "closed_at", "exit_ts", "close_ts",
        "entry_time", "open_time", "timestamp", "time", "datetime", "date",
        "day", "month", "period", "bar_time", "signal_time",
    ])

    pnl_col = find_col(raw, [
        "net_pnl", "net_pnl_usdt", "pnl_usdt", "pnl", "realized_pnl", "closed_pnl",
        "profit", "profit_usdt", "net_profit", "return_usdt", "ret_usdt",
        "trade_pnl", "pnl_after_fee", "total_pnl",
    ])
    return_bps_col = find_col(raw, [
        "return_bps", "ret_bps", "net_bps", "pnl_bps", "edge_bps", "bps",
        "avg_return_bps", "mean_bps", "expectancy_bps",
    ])
    return_pct_col = find_col(raw, [
        "return_pct", "ret_pct", "pct_return", "return", "ret", "net_return",
        "avg_return", "mean_return",
    ])
    notional_col = find_col(raw, ["notional", "notional_usdt", "entry_notional", "position_notional"])
    status_col = find_col(raw, ["status", "state", "trade_status", "position_status"])
    id_col = find_col(raw, ["trade_id", "id", "order_id", "position_id", "signal_id", "entry_id"])

    # A usable file needs pnl OR return information.
    if pnl_col is None and return_bps_col is None and return_pct_col is None:
        return pd.DataFrame()

    out = pd.DataFrame(index=raw.index)
    out["source_file"] = str(path)
    out["source_row"] = np.arange(len(raw))

    if family_col:
        out["family_key"] = raw[family_col].apply(lambda x: normalize_family_value(x, path_text))
    else:
        out["family_key"] = normalize_family_value(None, path_text)

    if symbol_col:
        out["symbol"] = raw[symbol_col].astype(str).str.upper().str.strip()
    else:
        out["symbol"] = "UNKNOWN"

    if side_col:
        out["side"] = raw[side_col].astype(str).str.lower().str.strip()
    else:
        out["side"] = "unknown"

    if variant_col:
        out["variant"] = raw[variant_col].astype(str).str.strip()
    else:
        out["variant"] = "default"

    if time_col:
        out["event_time"] = parse_time_series(raw[time_col])
    else:
        out["event_time"] = pd.NaT

    if id_col:
        out["trade_id"] = raw[id_col].astype(str)
    else:
        out["trade_id"] = out["source_file"] + "#" + out["source_row"].astype(str)

    if pnl_col:
        out["pnl"] = pd.to_numeric(raw[pnl_col], errors="coerce")
    else:
        out["pnl"] = np.nan

    if return_bps_col:
        out["return_bps"] = pd.to_numeric(raw[return_bps_col], errors="coerce")
    elif return_pct_col:
        # Assume percentage if abs values are large-ish, decimal return if small.
        rp = pd.to_numeric(raw[return_pct_col], errors="coerce")
        med_abs = rp.dropna().abs().median() if rp.notna().any() else np.nan
        if pd.notna(med_abs) and med_abs <= 1.0:
            out["return_bps"] = rp * 10000.0
        else:
            out["return_bps"] = rp * 100.0
    else:
        out["return_bps"] = np.nan

    if notional_col:
        out["notional"] = pd.to_numeric(raw[notional_col], errors="coerce")
    else:
        out["notional"] = np.nan

    if status_col:
        out["status"] = raw[status_col].astype(str).str.lower().str.strip()
    else:
        out["status"] = "unknown"

    # If pnl missing but bps and notional available, estimate pnl.
    mask_est = out["pnl"].isna() & out["return_bps"].notna() & out["notional"].notna()
    out.loc[mask_est, "pnl"] = out.loc[mask_est, "notional"] * out.loc[mask_est, "return_bps"] / 10000.0

    # If this is a summary-level file with avg pnl or total pnl repeated, it may still normalize.
    # Keep rows with numeric pnl only; the report will reveal if rows are trade-level or summary-like.
    out = out[out["pnl"].notna()].copy()
    if out.empty:
        return out

    # Exclude open/pending rows if status exists.
    status = out["status"].astype(str).str.lower()
    out = out[~status.str.contains("open|pending|active|running", regex=True, na=False)].copy()

    # Keep only known or inferable families when possible. Unknowns are allowed but reported lower priority.
    out["dedupe_key"] = out["family_key"].astype(str) + "|" + out["trade_id"].astype(str) + "|" + out["source_file"].astype(str)
    return out


def load_all_trades(workspace: Path, input_file: Optional[Path]) -> Tuple[pd.DataFrame, List[SourceFileRecord]]:
    files = discover_files(workspace, input_file)
    frames: List[pd.DataFrame] = []
    records: List[SourceFileRecord] = []

    for p in files:
        df = read_table(p)
        if df is None or df.empty:
            records.append(SourceFileRecord(str(p), "SKIP", 0, 0, [], "unreadable or empty"))
            continue
        norm = normalize_trade_like_rows(p, df)
        fams = sorted(norm["family_key"].dropna().astype(str).unique().tolist()) if not norm.empty else []
        status = "OK" if not norm.empty else "SKIP"
        msg = "normalized trade-like rows" if not norm.empty else "no pnl/return trade-like rows detected"
        records.append(SourceFileRecord(str(p), status, int(len(df)), int(len(norm)), fams, msg))
        if not norm.empty:
            frames.append(norm)

    if not frames:
        return pd.DataFrame(), records

    trades = pd.concat(frames, ignore_index=True)
    trades["event_time"] = pd.to_datetime(trades["event_time"], errors="coerce")
    trades["pnl"] = pd.to_numeric(trades["pnl"], errors="coerce")
    trades["return_bps"] = pd.to_numeric(trades["return_bps"], errors="coerce")
    trades = trades[trades["pnl"].notna()].copy()

    # Deduplicate conservatively.
    before = len(trades)
    trades = trades.drop_duplicates(subset=["dedupe_key"], keep="last").copy()
    after = len(trades)
    if after < before * 0.35:
        # If IDs are too generic, use source row instead.
        trades["dedupe_key"] = trades["source_file"].astype(str) + "|" + trades["source_row"].astype(str)
        trades = trades.drop_duplicates(subset=["dedupe_key"], keep="last").copy()

    trades = trades.sort_values(["event_time", "source_file", "source_row"], na_position="last").reset_index(drop=True)
    return trades, records


def assign_time_windows(df: pd.DataFrame, min_windows: int) -> pd.Series:
    times = pd.to_datetime(df["event_time"], errors="coerce")
    if times.notna().sum() >= max(10, min_windows):
        span_days = (times.max() - times.min()).days if pd.notna(times.max()) and pd.notna(times.min()) else 0
        if span_days >= 90:
            return times.dt.to_period("M").astype(str)
        if span_days >= 21:
            iso = times.dt.isocalendar()
            return iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)

    # Fallback: chronological folds.
    n = len(df)
    k = max(min_windows, min(10, max(2, n // 50)))
    order = np.arange(n)
    folds = np.floor(order / max(1, math.ceil(n / k))).astype(int) + 1
    folds = np.minimum(folds, k)
    return pd.Series([f"fold_{x:02d}" for x in folds], index=df.index)


def build_window_metrics(trades: pd.DataFrame, min_windows: int) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    rows: List[Dict[str, Any]] = []
    for fam, g in trades.groupby("family_key", dropna=False):
        g = g.copy().sort_values("event_time", na_position="last").reset_index(drop=True)
        g["window"] = assign_time_windows(g, min_windows=min_windows)
        for window, w in g.groupby("window", sort=True):
            m = compute_metrics(w)
            rows.append({
                "family_key": str(fam),
                "window": str(window),
                "start_time": pd.to_datetime(w["event_time"], errors="coerce").min(),
                "end_time": pd.to_datetime(w["event_time"], errors="coerce").max(),
                **asdict(m),
                "unique_symbols": int(w["symbol"].nunique(dropna=True)) if "symbol" in w.columns else 0,
            })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["start_time"] = out["start_time"].astype(str)
        out["end_time"] = out["end_time"].astype(str)
    return out


def build_symbol_metrics(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty or "symbol" not in trades.columns:
        return pd.DataFrame()
    rows: List[Dict[str, Any]] = []
    for (fam, symbol), g in trades.groupby(["family_key", "symbol"], dropna=False):
        m = compute_metrics(g)
        rows.append({
            "family_key": str(fam),
            "symbol": str(symbol),
            **asdict(m),
        })
    return pd.DataFrame(rows)


def chronological_train_test_metrics(df: pd.DataFrame, test_fraction: float) -> Tuple[Metrics, Metrics, Dict[str, Any]]:
    if df.empty:
        z = compute_metrics(df)
        return z, z, {}
    g = df.copy().sort_values("event_time", na_position="last").reset_index(drop=True)
    n = len(g)
    split = int(max(1, min(n - 1, math.floor(n * (1.0 - test_fraction))))) if n >= 2 else n
    train = g.iloc[:split].copy()
    test = g.iloc[split:].copy()
    train_m = compute_metrics(train)
    test_m = compute_metrics(test)
    avg_ratio = None
    if abs(train_m.avg_pnl) > 1e-12:
        avg_ratio = test_m.avg_pnl / abs(train_m.avg_pnl)
    pf_ratio = None
    if train_m.profit_factor not in {0.0, float("inf")} and math.isfinite(train_m.profit_factor):
        pf_ratio = test_m.profit_factor / train_m.profit_factor if math.isfinite(test_m.profit_factor) else None
    extra = {
        "train_trade_count": train_m.trade_count,
        "test_trade_count": test_m.trade_count,
        "test_fraction_actual": test_m.trade_count / max(1, n),
        "oos_avg_pnl_ratio_vs_train_abs": avg_ratio,
        "oos_pf_ratio_vs_train": pf_ratio,
        "oos_win_rate_delta": test_m.win_rate - train_m.win_rate,
    }
    return train_m, test_m, extra


def max_consecutive_negative(values: Sequence[float]) -> int:
    best = 0
    cur = 0
    for v in values:
        if v < 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def summarize_windows(fam: str, window_df: pd.DataFrame, min_window_trades: int) -> Dict[str, Any]:
    w = window_df[window_df["family_key"] == fam].copy() if not window_df.empty else pd.DataFrame()
    if w.empty:
        return {
            "window_count": 0,
            "valid_window_count": 0,
            "positive_window_rate": None,
            "positive_valid_window_rate": None,
            "worst_window_pnl": None,
            "best_window_pnl": None,
            "worst_window_avg_pnl": None,
            "max_consecutive_negative_windows": 0,
            "window_avg_pnl_cv": None,
            "low_trade_windows": 0,
        }
    w["total_pnl"] = pd.to_numeric(w["total_pnl"], errors="coerce")
    w["avg_pnl"] = pd.to_numeric(w["avg_pnl"], errors="coerce")
    valid = w[w["trade_count"] >= min_window_trades].copy()
    vals = w["total_pnl"].fillna(0.0).tolist()
    avg_vals = valid["avg_pnl"].dropna().tolist()
    cv = None
    if len(avg_vals) >= 2 and abs(np.mean(avg_vals)) > 1e-12:
        cv = float(np.std(avg_vals, ddof=1) / abs(np.mean(avg_vals)))
    return {
        "window_count": int(len(w)),
        "valid_window_count": int(len(valid)),
        "positive_window_rate": float((w["total_pnl"] > 0).mean()) if len(w) else None,
        "positive_valid_window_rate": float((valid["total_pnl"] > 0).mean()) if len(valid) else None,
        "worst_window_pnl": float(w["total_pnl"].min()) if len(w) else None,
        "best_window_pnl": float(w["total_pnl"].max()) if len(w) else None,
        "worst_window_avg_pnl": float(w["avg_pnl"].min()) if len(w) else None,
        "max_consecutive_negative_windows": max_consecutive_negative(vals),
        "window_avg_pnl_cv": cv,
        "low_trade_windows": int((w["trade_count"] < min_window_trades).sum()),
    }


def summarize_symbols(fam: str, symbol_df: pd.DataFrame, min_symbol_trades: int) -> Dict[str, Any]:
    s = symbol_df[symbol_df["family_key"] == fam].copy() if not symbol_df.empty else pd.DataFrame()
    if s.empty:
        return {
            "symbol_count": 0,
            "valid_symbol_count": 0,
            "positive_symbol_rate": None,
            "positive_valid_symbol_rate": None,
            "worst_symbol_pnl": None,
            "best_symbol_pnl": None,
            "top3_abs_pnl_concentration": None,
            "low_trade_symbols": 0,
        }
    s["total_pnl"] = pd.to_numeric(s["total_pnl"], errors="coerce")
    valid = s[s["trade_count"] >= min_symbol_trades].copy()
    abs_total = s["total_pnl"].abs().sum()
    top3_conc = None
    if abs_total > 1e-12:
        top3_conc = float(s["total_pnl"].abs().sort_values(ascending=False).head(3).sum() / abs_total)
    return {
        "symbol_count": int(len(s)),
        "valid_symbol_count": int(len(valid)),
        "positive_symbol_rate": float((s["total_pnl"] > 0).mean()) if len(s) else None,
        "positive_valid_symbol_rate": float((valid["total_pnl"] > 0).mean()) if len(valid) else None,
        "worst_symbol_pnl": float(s["total_pnl"].min()) if len(s) else None,
        "best_symbol_pnl": float(s["total_pnl"].max()) if len(s) else None,
        "top3_abs_pnl_concentration": top3_conc,
        "low_trade_symbols": int((s["trade_count"] < min_symbol_trades).sum()),
    }


def decision_for_family(
    fam: str,
    full_m: Metrics,
    train_m: Metrics,
    test_m: Metrics,
    oos_extra: Dict[str, Any],
    win_sum: Dict[str, Any],
    sym_sum: Dict[str, Any],
    min_trades: int,
    min_windows: int,
    min_test_trades: int,
) -> FamilyDecision:
    reasons: List[str] = []
    score = 0

    if full_m.trade_count < min_trades:
        return FamilyDecision(
            family_key=fam,
            current_role=CURRENT_ROLES.get(fam, "UNKNOWN"),
            decision="INSUFFICIENT_DATA",
            confidence="low",
            reasons=[f"trade_count {full_m.trade_count} < min_trades {min_trades}"],
            metrics=asdict(full_m),
            oos_metrics={"train": asdict(train_m), "test": asdict(test_m), **oos_extra},
            window_metrics=win_sum,
            symbol_metrics=sym_sum,
            recommended_lifecycle_seed="KEEP_UNCHANGED_UNTIL_MORE_DATA",
            recommended_capital_hint="NO_CHANGE_FROM_THIS_VALIDATOR",
        )

    # Full-sample basic edge.
    if full_m.total_pnl <= 0 or full_m.avg_pnl <= 0:
        score -= 4
        reasons.append("full-sample total/avg pnl is not positive")
    else:
        score += 1
        reasons.append("full-sample total and avg pnl are positive")

    if full_m.profit_factor < 1.0:
        score -= 3
        reasons.append("full-sample profit factor is below 1")
    elif full_m.profit_factor < 1.10:
        score -= 1
        reasons.append("full-sample profit factor is only slightly above 1")
    elif full_m.profit_factor >= 1.25:
        score += 1
        reasons.append("full-sample profit factor is acceptable")

    # OOS split.
    if test_m.trade_count < min_test_trades:
        score -= 1
        reasons.append(f"test/OOS trade_count {test_m.trade_count} < min_test_trades {min_test_trades}")
    else:
        if test_m.total_pnl <= 0 or test_m.avg_pnl <= 0:
            score -= 4
            reasons.append("test/OOS total or avg pnl is not positive")
        else:
            score += 2
            reasons.append("test/OOS total and avg pnl are positive")

        if train_m.avg_pnl > 0 and test_m.avg_pnl < train_m.avg_pnl * 0.35:
            score -= 2
            reasons.append("test/OOS avg pnl degraded below 35% of train avg pnl")
        elif train_m.avg_pnl > 0 and test_m.avg_pnl >= train_m.avg_pnl * 0.65:
            score += 1
            reasons.append("test/OOS avg pnl retained at least 65% of train avg pnl")

    # Window robustness.
    positive_valid_window_rate = win_sum.get("positive_valid_window_rate")
    valid_window_count = win_sum.get("valid_window_count") or 0
    if valid_window_count < min_windows:
        score -= 1
        reasons.append(f"valid_window_count {valid_window_count} < min_windows {min_windows}")
    else:
        if positive_valid_window_rate is not None and positive_valid_window_rate < 0.50:
            score -= 3
            reasons.append("less than half of valid rolling windows are profitable")
        elif positive_valid_window_rate is not None and positive_valid_window_rate < 0.60:
            score -= 1
            reasons.append("rolling window profitability is weak")
        elif positive_valid_window_rate is not None and positive_valid_window_rate >= 0.70:
            score += 2
            reasons.append("rolling window profitability is strong")

    max_neg = win_sum.get("max_consecutive_negative_windows") or 0
    if max_neg >= 3:
        score -= 2
        reasons.append(f"max consecutive negative windows is high: {max_neg}")
    elif max_neg == 0 and valid_window_count >= min_windows:
        score += 1
        reasons.append("no consecutive negative rolling-window streak detected")

    cv = win_sum.get("window_avg_pnl_cv")
    if cv is not None:
        if cv > 3.0:
            score -= 1
            reasons.append("window avg pnl is very unstable")
        elif cv < 1.5:
            score += 1
            reasons.append("window avg pnl stability is acceptable")

    # Symbol robustness.
    valid_symbol_count = sym_sum.get("valid_symbol_count") or 0
    pos_symbol_rate = sym_sum.get("positive_valid_symbol_rate")
    top3_conc = sym_sum.get("top3_abs_pnl_concentration")
    if valid_symbol_count >= 5:
        if pos_symbol_rate is not None and pos_symbol_rate < 0.45:
            score -= 2
            reasons.append("less than 45% of valid symbols are profitable")
        elif pos_symbol_rate is not None and pos_symbol_rate >= 0.60:
            score += 1
            reasons.append("symbol distribution profitability is acceptable")
        if top3_conc is not None and top3_conc > 0.75:
            score -= 1
            reasons.append("PnL is highly concentrated in top 3 symbols")
    else:
        reasons.append("symbol robustness check is limited because valid_symbol_count is low")

    # Current role-specific conservatism.
    if fam == "market_relative_short" and score <= 1:
        reasons.append("current role is already capped/half-size; weak validation supports keeping it reduced")
    if fam == "weak_market_short" and score <= 2:
        reasons.append("current role is backup-only; validation must be strong before promotion")

    if score >= 6:
        decision = "STRONG_CANDIDATE"
        lifecycle = "PROMOTE_OR_KEEP_ACTIVE"
        capital_hint = "ELIGIBLE_FOR_NORMAL_OR_HIGH_PRIORITY_SIZE_AFTER_OTHER_CHECKS"
        confidence = "high"
    elif score >= 3:
        decision = "PASS_CANDIDATE"
        lifecycle = "KEEP_ACTIVE"
        capital_hint = "KEEP_CURRENT_SIZE_OR_SMALL_INCREASE_ONLY_AFTER_EXECUTION_CHECK"
        confidence = "medium"
    elif score >= 0:
        decision = "WATCH_WEAK_OOS"
        lifecycle = "KEEP_ACTIVE_BUT_MONITOR"
        capital_hint = "NO_INCREASE"
        confidence = "medium"
    elif score >= -3:
        decision = "REDUCE_OR_BACKUP_ONLY"
        lifecycle = "REDUCE_OR_BACKUP_ONLY"
        capital_hint = "REDUCE_SIZE_OR_KEEP_BACKUP_ONLY"
        confidence = "medium"
    else:
        decision = "REJECT_OR_DISABLE"
        lifecycle = "DISABLE_CANDIDATE"
        capital_hint = "ZERO_OR_NEAR_ZERO_UNTIL_REVALIDATED"
        confidence = "high" if full_m.trade_count >= min_trades * 2 else "medium"

    return FamilyDecision(
        family_key=fam,
        current_role=CURRENT_ROLES.get(fam, "UNKNOWN"),
        decision=decision,
        confidence=confidence,
        reasons=reasons,
        metrics=asdict(full_m),
        oos_metrics={"train": asdict(train_m), "test": asdict(test_m), **oos_extra},
        window_metrics=win_sum,
        symbol_metrics=sym_sum,
        recommended_lifecycle_seed=lifecycle,
        recommended_capital_hint=capital_hint,
    )


def validate_families(
    trades: pd.DataFrame,
    min_trades: int,
    min_windows: int,
    min_window_trades: int,
    min_symbol_trades: int,
    min_test_trades: int,
    test_fraction: float,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[FamilyDecision]]:
    window_df = build_window_metrics(trades, min_windows=min_windows)
    symbol_df = build_symbol_metrics(trades)
    decisions: List[FamilyDecision] = []

    if trades.empty:
        return window_df, symbol_df, decisions

    families = sorted(trades["family_key"].dropna().astype(str).unique().tolist())
    # Prefer known active families first in report ordering.
    order = [f for f in ACTIVE_FAMILIES if f in families] + [f for f in families if f not in ACTIVE_FAMILIES]

    for fam in order:
        g = trades[trades["family_key"] == fam].copy().sort_values("event_time", na_position="last")
        full_m = compute_metrics(g)
        train_m, test_m, oos_extra = chronological_train_test_metrics(g, test_fraction=test_fraction)
        win_sum = summarize_windows(fam, window_df, min_window_trades=min_window_trades)
        sym_sum = summarize_symbols(fam, symbol_df, min_symbol_trades=min_symbol_trades)
        decisions.append(decision_for_family(
            fam=fam,
            full_m=full_m,
            train_m=train_m,
            test_m=test_m,
            oos_extra=oos_extra,
            win_sum=win_sum,
            sym_sum=sym_sum,
            min_trades=min_trades,
            min_windows=min_windows,
            min_test_trades=min_test_trades,
        ))

    # Add active families with no data as explicit insufficient data.
    present = {d.family_key for d in decisions}
    for fam in ACTIVE_FAMILIES:
        if fam not in present:
            z = compute_metrics(pd.DataFrame(columns=["pnl", "return_bps"]))
            decisions.append(FamilyDecision(
                family_key=fam,
                current_role=CURRENT_ROLES.get(fam, "UNKNOWN"),
                decision="NO_USABLE_DATA",
                confidence="low",
                reasons=["no normalized historical/backtest rows found for this active family"],
                metrics=asdict(z),
                oos_metrics={"train": asdict(z), "test": asdict(z)},
                window_metrics={},
                symbol_metrics={},
                recommended_lifecycle_seed="NEEDS_HISTORICAL_VALIDATION_BEFORE_PROMOTION",
                recommended_capital_hint="NO_INCREASE",
            ))

    return window_df, symbol_df, decisions


def family_summary_dataframe(decisions: List[FamilyDecision]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for d in decisions:
        m = d.metrics
        o = d.oos_metrics
        test = o.get("test", {}) if isinstance(o.get("test"), dict) else {}
        train = o.get("train", {}) if isinstance(o.get("train"), dict) else {}
        w = d.window_metrics
        s = d.symbol_metrics
        rows.append({
            "family_key": d.family_key,
            "current_role": d.current_role,
            "decision": d.decision,
            "confidence": d.confidence,
            "trade_count": m.get("trade_count"),
            "total_pnl": m.get("total_pnl"),
            "avg_pnl": m.get("avg_pnl"),
            "win_rate": m.get("win_rate"),
            "profit_factor": m.get("profit_factor"),
            "max_drawdown": m.get("max_drawdown"),
            "train_trade_count": train.get("trade_count"),
            "train_avg_pnl": train.get("avg_pnl"),
            "train_profit_factor": train.get("profit_factor"),
            "test_trade_count": test.get("trade_count"),
            "test_avg_pnl": test.get("avg_pnl"),
            "test_profit_factor": test.get("profit_factor"),
            "oos_avg_pnl_ratio_vs_train_abs": o.get("oos_avg_pnl_ratio_vs_train_abs"),
            "oos_win_rate_delta": o.get("oos_win_rate_delta"),
            "window_count": w.get("window_count"),
            "valid_window_count": w.get("valid_window_count"),
            "positive_valid_window_rate": w.get("positive_valid_window_rate"),
            "max_consecutive_negative_windows": w.get("max_consecutive_negative_windows"),
            "symbol_count": s.get("symbol_count"),
            "valid_symbol_count": s.get("valid_symbol_count"),
            "positive_valid_symbol_rate": s.get("positive_valid_symbol_rate"),
            "top3_abs_pnl_concentration": s.get("top3_abs_pnl_concentration"),
            "recommended_lifecycle_seed": d.recommended_lifecycle_seed,
            "recommended_capital_hint": d.recommended_capital_hint,
            "reason_summary": " | ".join(d.reasons[:5]),
        })
    return pd.DataFrame(rows)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_report_md(
    path: Path,
    workspace: Path,
    trades: pd.DataFrame,
    source_records: List[SourceFileRecord],
    decisions: List[FamilyDecision],
    summary_df: pd.DataFrame,
    window_df: pd.DataFrame,
    symbol_df: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Rolling OOS Validator Report")
    lines.append("")
    lines.append(f"Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"Workspace: `{workspace}`")
    lines.append("")

    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"Normalized rows: **{len(trades)}**")
    if not trades.empty:
        fams = sorted(trades["family_key"].dropna().astype(str).unique().tolist())
        lines.append(f"Detected families: **{', '.join(fams)}**")
        if pd.to_datetime(trades["event_time"], errors="coerce").notna().any():
            t = pd.to_datetime(trades["event_time"], errors="coerce")
            lines.append(f"Time range: `{t.min()}` → `{t.max()}`")
    lines.append("")

    lines.append("## Family decisions")
    lines.append("")
    if summary_df.empty:
        lines.append("No usable family data found.")
    else:
        lines.append("| Family | Role | Decision | Confidence | Trades | PnL | Avg PnL | WR | PF | OOS Avg | Pos Windows | Pos Symbols | Lifecycle seed |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for _, r in summary_df.iterrows():
            pf = r.get("profit_factor")
            pf_txt = "inf" if str(pf) == "inf" else (f"{float(pf):.3f}" if pd.notna(pf) else "")
            wr = r.get("win_rate")
            wr_txt = f"{float(wr):.2%}" if pd.notna(wr) else ""
            posw = r.get("positive_valid_window_rate")
            posw_txt = f"{float(posw):.2%}" if pd.notna(posw) else ""
            poss = r.get("positive_valid_symbol_rate")
            poss_txt = f"{float(poss):.2%}" if pd.notna(poss) else ""
            test_avg = r.get("test_avg_pnl")
            test_avg_txt = f"{float(test_avg):.6f}" if pd.notna(test_avg) else ""
            lines.append(
                f"| {r.get('family_key')} | {r.get('current_role')} | {r.get('decision')} | {r.get('confidence')} | "
                f"{r.get('trade_count')} | {float(r.get('total_pnl') or 0):.6f} | {float(r.get('avg_pnl') or 0):.6f} | "
                f"{wr_txt} | {pf_txt} | {test_avg_txt} | {posw_txt} | {poss_txt} | {r.get('recommended_lifecycle_seed')} |"
            )
    lines.append("")

    for d in decisions:
        lines.append(f"### {d.family_key}")
        lines.append("")
        lines.append(f"Decision: **{d.decision}** / confidence: **{d.confidence}** / current role: `{d.current_role}`")
        lines.append("")
        lines.append("Reasons:")
        for reason in d.reasons:
            lines.append(f"- {reason}")
        lines.append("")
        lines.append(f"Lifecycle seed: `{d.recommended_lifecycle_seed}`")
        lines.append(f"Capital hint: `{d.recommended_capital_hint}`")
        lines.append("")

    lines.append("## Source file scan")
    lines.append("")
    lines.append("| Status | Rows | Normalized | Families | File | Message |")
    lines.append("|---|---:|---:|---|---|---|")
    for rec in source_records[:150]:
        fams = ", ".join(rec.inferred_families)
        lines.append(f"| {rec.status} | {rec.rows} | {rec.normalized_rows} | {fams} | `{rec.path}` | {rec.message} |")
    if len(source_records) > 150:
        lines.append(f"\n_Source scan truncated: {len(source_records) - 150} more files._")
    lines.append("")

    lines.append("## Parameters")
    lines.append("")
    for k, v in vars(args).items():
        lines.append(f"- `{k}` = `{v}`")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This validator is deliberately hostile to fragile edges. A weak decision here does not prove the family is useless, but it means the family should not be promoted before further evidence.")
    lines.append("Paper/live trading is not required for this report. This is an offline OS control-plane check.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory rolling OOS validator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="edge_lab_new workspace")
    p.add_argument("--input_file", default=None, help="optional explicit CSV/JSON/Parquet file to validate")
    p.add_argument("--out_dir", default=None, help="optional output root")
    p.add_argument("--min_trades", type=int, default=100, help="minimum trades for family-level decision")
    p.add_argument("--min_windows", type=int, default=4, help="minimum valid time windows")
    p.add_argument("--min_window_trades", type=int, default=10, help="minimum trades for a valid rolling window")
    p.add_argument("--min_symbol_trades", type=int, default=8, help="minimum trades for a valid symbol check")
    p.add_argument("--min_test_trades", type=int, default=25, help="minimum chronological OOS/test trades")
    p.add_argument("--test_fraction", type=float, default=0.30, help="last fraction of trades used as chronological OOS/test")
    p.add_argument("--family_filter", default=None, help="comma-separated family keys to keep")
    p.add_argument("--keep_unknown", action="store_true", help="keep unknown family rows")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    input_file = Path(args.input_file) if args.input_file else None
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_rolling_oos_validator"
    out_dir = out_root / f"rolling_oos_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        trades, source_records = load_all_trades(workspace, input_file=input_file)

        if not trades.empty and args.family_filter:
            keep = {x.strip() for x in args.family_filter.split(",") if x.strip()}
            trades = trades[trades["family_key"].isin(keep)].copy()

        if not trades.empty and not args.keep_unknown:
            trades = trades[trades["family_key"] != "unknown"].copy()

        if trades.empty:
            write_json(out_dir / "source_file_scan.json", [asdict(x) for x in source_records])
            write_json(out_dir / "rolling_oos_decisions.json", [])
            pd.DataFrame().to_csv(out_dir / "normalized_oos_trades.csv", index=False)
            pd.DataFrame().to_csv(out_dir / "rolling_oos_family_summary.csv", index=False)
            write_json(out_dir / "rolling_oos_family_summary.json", [])
            write_report_md(
                out_dir / "rolling_oos_report.md",
                workspace=workspace,
                trades=trades,
                source_records=source_records,
                decisions=[],
                summary_df=pd.DataFrame(),
                window_df=pd.DataFrame(),
                symbol_df=pd.DataFrame(),
                args=args,
            )
            print("EDGE FACTORY ROLLING OOS VALIDATOR v1")
            print("No usable historical/backtest trade-like rows found.")
            print(f"Report dir: {out_dir}")
            return 2

        window_df, symbol_df, decisions = validate_families(
            trades=trades,
            min_trades=args.min_trades,
            min_windows=args.min_windows,
            min_window_trades=args.min_window_trades,
            min_symbol_trades=args.min_symbol_trades,
            min_test_trades=args.min_test_trades,
            test_fraction=args.test_fraction,
        )
        summary_df = family_summary_dataframe(decisions)

        # Save outputs.
        write_json(out_dir / "source_file_scan.json", [asdict(x) for x in source_records])
        write_json(out_dir / "rolling_oos_decisions.json", [asdict(x) for x in decisions])
        write_json(out_dir / "rolling_oos_family_summary.json", summary_df.to_dict(orient="records"))
        summary_df.to_csv(out_dir / "rolling_oos_family_summary.csv", index=False)
        window_df.to_csv(out_dir / "rolling_oos_window_metrics.csv", index=False)
        symbol_df.to_csv(out_dir / "rolling_oos_symbol_metrics.csv", index=False)

        trades_out = trades.copy()
        trades_out["event_time"] = trades_out["event_time"].astype(str)
        trades_out.to_csv(out_dir / "normalized_oos_trades.csv", index=False)

        write_report_md(
            out_dir / "rolling_oos_report.md",
            workspace=workspace,
            trades=trades,
            source_records=source_records,
            decisions=decisions,
            summary_df=summary_df,
            window_df=window_df,
            symbol_df=symbol_df,
            args=args,
        )

        print("EDGE FACTORY ROLLING OOS VALIDATOR v1")
        print("=" * 100)
        print(f"workspace : {workspace}")
        print(f"output_dir: {out_dir}")
        print(f"rows      : {len(trades)}")
        print("")
        print("FAMILY OOS DECISIONS")
        print("-" * 100)
        for d in decisions:
            m = d.metrics
            pf = m.get("profit_factor")
            pf_txt = "inf" if str(pf) == "inf" else f"{float(pf):.3f}" if pf is not None else "n/a"
            print(
                f"{d.family_key:24s} role={d.current_role:24s} decision={d.decision:24s} "
                f"conf={d.confidence:6s} trades={int(m.get('trade_count', 0)):5d} "
                f"pnl={float(m.get('total_pnl', 0.0)): .6f} avg={float(m.get('avg_pnl', 0.0)): .6f} "
                f"wr={float(m.get('win_rate', 0.0)): .2%} pf={pf_txt}"
            )
            for r in d.reasons[:4]:
                print(f"  - {r}")
        print("")
        print(f"Open report: {out_dir / 'rolling_oos_report.md'}")
        print(f"Summary    : {out_dir / 'rolling_oos_family_summary.csv'}")
        print(f"Decisions  : {out_dir / 'rolling_oos_decisions.json'}")
        return 0

    except Exception as e:
        err = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "workspace": str(workspace),
            "input_file": str(input_file) if input_file else None,
        }
        write_json(out_dir / "fatal_error.json", err)
        print("FATAL ERROR in Edge Factory Rolling OOS Validator")
        print(str(e))
        print(f"Details: {out_dir / 'fatal_error.json'}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
