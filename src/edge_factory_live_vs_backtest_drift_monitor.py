#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY LIVE-vs-BACKTEST DRIFT MONITOR v1
================================================

Purpose
-------
First "nervous system" module for the Edge Factory OS.
It scans MASTER_UPPER_SYSTEM paper/live trade outputs, computes realized family-level
performance, compares it against backtest/reference expectations when available, and
emits machine-readable decisions for later modules:

    OK / WATCH / REDUCE / DISABLE_CANDIDATE / INSUFFICIENT_DATA / NO_REFERENCE

Designed for the current project layout:
    Workspace: C:\Users\alike\OneDrive\Desktop\edge_lab_new
    Runtime:   C:\Users\alike
    Paper dir: C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM

This script is intentionally conservative:
- It does NOT place trades.
- It does NOT edit logger scripts.
- It does NOT change capital allocation.
- It only reads logs and writes reports.

Recommended first run:
    python "C:\Users\alike\edge_factory_live_vs_backtest_drift_monitor.py" ^
      --base_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM" ^
      --workspace "C:\Users\alike\OneDrive\Desktop\edge_lab_new"

Optional with explicit reference file:
    python "C:\Users\alike\edge_factory_live_vs_backtest_drift_monitor.py" ^
      --base_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM" ^
      --workspace "C:\Users\alike\OneDrive\Desktop\edge_lab_new" ^
      --reference_file "C:\path\to\family_backtest_reference.csv"

Reference file accepted columns, flexible names:
    family_key / family / strategy
    trade_count / n / trades
    win_rate / wr
    avg_pnl / mean_pnl / expectancy / expectancy_usdt
    total_pnl
    profit_factor / pf
    max_drawdown / max_dd / max_dd_usdt
    avg_return_bps / mean_bps / expectancy_bps

Outputs
-------
Creates a timestamped folder under:
    <workspace>\edge_factory_drift_monitor\drift_report_YYYYMMDD_HHMMSS

Files:
    drift_family_summary.csv
    drift_family_summary.json
    drift_decisions.json
    drift_report.md
    normalized_trades.csv

Exit codes:
    0 = report completed
    2 = no usable trades found
    3 = fatal error
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


FAMILY_KEYS = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
    "session_short",
]

ACTIVE_FAMILY_KEYS = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
]

DEFAULT_WORKSPACE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_BASE_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_MASTER_UPPER_SYSTEM"
DEFAULT_SIZING_CONTRACT = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_position_sizing_contract\position_sizing_contract.json"


# Conservative defaults. These are not trading rules; they are monitoring thresholds.
DEFAULT_MIN_TRADES_FOR_DECISION = 30
DEFAULT_MIN_TRADES_FOR_HARD_DECISION = 80
DEFAULT_RECENT_WINDOW_TRADES = 50
DEFAULT_RECENT_WINDOW_DAYS = 3


@dataclass
class FamilyMetrics:
    family_key: str
    trade_count: int = 0
    first_trade_time: Optional[str] = None
    last_trade_time: Optional[str] = None
    unique_symbols: int = 0
    total_pnl: float = 0.0
    avg_pnl: float = 0.0
    median_pnl: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    avg_return_bps: Optional[float] = None
    median_return_bps: Optional[float] = None
    p05_pnl: float = 0.0
    p95_pnl: float = 0.0
    recent_trade_count: int = 0
    recent_total_pnl: float = 0.0
    recent_avg_pnl: float = 0.0
    recent_win_rate: float = 0.0
    recent_profit_factor: float = 0.0
    recent_max_drawdown: float = 0.0
    daily_bad_days: int = 0
    daily_good_days: int = 0
    worst_day_pnl: float = 0.0
    best_day_pnl: float = 0.0


@dataclass
class ReferenceMetrics:
    family_key: str
    trade_count: Optional[float] = None
    total_pnl: Optional[float] = None
    avg_pnl: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    max_drawdown: Optional[float] = None
    avg_return_bps: Optional[float] = None
    source: str = "unknown"


@dataclass
class DriftDecision:
    family_key: str
    status: str
    confidence: str
    reasons: List[str]
    live: Dict[str, Any]
    reference: Optional[Dict[str, Any]]
    drift: Dict[str, Any]
    recommended_next_action: str


# -----------------------------
# Utility helpers
# -----------------------------

def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        if isinstance(x, str):
            x = x.strip().replace("%", "")
            if x == "" or x.lower() in {"nan", "none", "null"}:
                return None
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def safe_int(x: Any) -> Optional[int]:
    v = safe_float(x)
    if v is None:
        return None
    return int(v)


def norm_col_name(c: str) -> str:
    c = str(c).strip().lower()
    c = re.sub(r"[^a-z0-9]+", "_", c)
    c = re.sub(r"_+", "_", c).strip("_")
    return c


def find_first_col(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    cols = {norm_col_name(c): c for c in df.columns}
    for cand in candidates:
        key = norm_col_name(cand)
        if key in cols:
            return cols[key]
    # fuzzy contains fallback
    normed = [(norm_col_name(c), c) for c in df.columns]
    for cand in candidates:
        key = norm_col_name(cand)
        for nc, orig in normed:
            if key == nc or key in nc:
                return orig
    return None


def parse_time_series(s: pd.Series) -> pd.Series:
    if s is None:
        return pd.Series(pd.NaT, index=[])
    # Numeric timestamps: support seconds / ms / us / ns roughly.
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
    return pd.to_datetime(s, errors="coerce", utc=False)


def profit_factor(pnls: pd.Series) -> float:
    pnls = pd.to_numeric(pnls, errors="coerce").dropna()
    gains = pnls[pnls > 0].sum()
    losses = -pnls[pnls < 0].sum()
    if losses <= 0 and gains > 0:
        return float("inf")
    if losses <= 0:
        return 0.0
    return float(gains / losses)


def max_drawdown_from_pnl(pnls: Sequence[float]) -> float:
    if len(pnls) == 0:
        return 0.0
    equity = np.cumsum(np.asarray(pnls, dtype=float))
    peak = np.maximum.accumulate(equity)
    dd = equity - peak
    return float(dd.min()) if len(dd) else 0.0


def pct_change_safe(live: Optional[float], ref: Optional[float]) -> Optional[float]:
    if live is None or ref is None:
        return None
    if abs(ref) < 1e-12:
        return None
    return float((live - ref) / abs(ref))


def ratio_safe(live: Optional[float], ref: Optional[float]) -> Optional[float]:
    if live is None or ref is None:
        return None
    if abs(ref) < 1e-12:
        return None
    return float(live / ref)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Sizing contract reading
# -----------------------------

def load_sizing_contract(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def infer_expected_notional(contract: Dict[str, Any], family_key: str) -> Optional[float]:
    """Try several likely shapes without assuming the exact contract schema."""
    if not contract:
        return None

    direct_keys = [
        "expected_notional",
        "notional_usdt",
        "default_notional",
        "target_notional",
    ]

    # Shape: {"families": {"old_short": {"expected_notional": 50}}}
    fams = contract.get("families") or contract.get("family_contracts") or contract.get("family_sizing")
    if isinstance(fams, dict) and family_key in fams:
        node = fams[family_key]
        if isinstance(node, dict):
            for k in direct_keys:
                v = safe_float(node.get(k))
                if v is not None:
                    return v
        else:
            v = safe_float(node)
            if v is not None:
                return v

    # Shape: {"expected_notional": {"old_short": 50}}
    for top_key in direct_keys + ["family_notional", "notional_by_family", "expected_notional_by_family"]:
        node = contract.get(top_key)
        if isinstance(node, dict):
            v = safe_float(node.get(family_key))
            if v is not None:
                return v

    # Shape using pct + base equity.
    base_equity = safe_float(contract.get("base_equity")) or safe_float(contract.get("base_equity_usdt"))
    if base_equity is not None:
        pct_maps = [
            contract.get("family_pct"),
            contract.get("family_notional_pct"),
            contract.get("notional_pct_by_family"),
        ]
        for m in pct_maps:
            if isinstance(m, dict):
                pct = safe_float(m.get(family_key))
                if pct is not None:
                    if pct > 1.0:
                        pct = pct / 100.0
                    return float(base_equity * pct)

    return None


# -----------------------------
# Trade file discovery and normalization
# -----------------------------

def is_probably_trade_file(path: Path) -> bool:
    if path.suffix.lower() not in {".csv", ".json", ".jsonl", ".parquet", ".pq"}:
        return False
    name = path.name.lower()
    parent = str(path.parent).lower()
    positive = ["trade", "trades", "fill", "fills", "paper", "closed", "position"]
    negative = ["summary", "report", "decision", "health", "dashboard", "config", "contract", "optimizer", "backtest_reference"]
    if any(n in name for n in negative):
        return False
    return any(p in name for p in positive) or any(fam in parent for fam in ACTIVE_FAMILY_KEYS)


def discover_trade_files(base_dir: Path) -> List[Path]:
    if not base_dir.exists():
        return []
    files: List[Path] = []
    for root, _, filenames in os.walk(base_dir):
        root_path = Path(root)
        for fn in filenames:
            p = root_path / fn
            if is_probably_trade_file(p):
                files.append(p)
    files = sorted(set(files), key=lambda p: str(p).lower())
    return files


def read_table(path: Path) -> Optional[pd.DataFrame]:
    try:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            # Try normal CSV first, then tolerant fallback.
            try:
                return pd.read_csv(path)
            except Exception:
                return pd.read_csv(path, engine="python", on_bad_lines="skip")
        if suffix in {".parquet", ".pq"}:
            return pd.read_parquet(path)
        if suffix == ".jsonl":
            return pd.read_json(path, lines=True)
        if suffix == ".json":
            with path.open("r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, list):
                return pd.DataFrame(obj)
            if isinstance(obj, dict):
                for key in ["trades", "rows", "data", "records"]:
                    if isinstance(obj.get(key), list):
                        return pd.DataFrame(obj[key])
                # Single record dict fallback.
                return pd.DataFrame([obj])
    except Exception:
        return None
    return None


def infer_family_from_path_or_df(path: Path, df: pd.DataFrame) -> Optional[str]:
    for col in ["family_key", "family", "strategy_family", "strategy", "logger", "system"]:
        c = find_first_col(df, [col])
        if c is not None:
            vals = df[c].dropna().astype(str).str.lower().tolist()
            joined = " ".join(vals[:50])
            for fam in FAMILY_KEYS:
                if fam in joined:
                    return fam
            # Common script strategy aliases.
            if "impulse" in joined and "long" in joined:
                return "impulse_long"
            if "market_relative" in joined or "relative" in joined:
                return "market_relative_short"
            if "weak_market" in joined or "breakdown" in joined:
                return "weak_market_short"
            if "old_short" in joined:
                return "old_short"

    s = str(path).lower().replace("-", "_")
    for fam in FAMILY_KEYS:
        if fam in s:
            return fam
    if "impulse" in s and "long" in s:
        return "impulse_long"
    if "market_relative" in s or "relative_short" in s:
        return "market_relative_short"
    if "weak_market" in s or "breakdown" in s:
        return "weak_market_short"
    if "old_short" in s:
        return "old_short"
    return None


def normalize_trade_df(path: Path, df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    raw = df.copy()
    raw.columns = [str(c) for c in raw.columns]

    family = infer_family_from_path_or_df(path, raw) or "unknown"

    pnl_col = find_first_col(raw, [
        "net_pnl", "pnl_usdt", "pnl", "realized_pnl", "closed_pnl",
        "net_profit", "profit_usdt", "ret_usdt", "return_usdt",
        "pnl_after_fee", "net_pnl_usdt", "gross_pnl",
    ])
    ret_bps_col = find_first_col(raw, [
        "net_bps", "return_bps", "ret_bps", "pnl_bps", "edge_bps",
        "return_after_fee_bps", "net_return_bps", "bps",
    ])
    symbol_col = find_first_col(raw, ["symbol", "inst_id", "instrument", "coin", "ticker", "market"])
    side_col = find_first_col(raw, ["side", "direction", "position_side", "trade_side"])
    status_col = find_first_col(raw, ["status", "state", "trade_status", "position_status"])
    id_col = find_first_col(raw, ["trade_id", "id", "order_id", "position_id", "signal_id", "entry_id"])
    qty_col = find_first_col(raw, ["qty", "quantity", "size", "contracts", "amount"])
    notional_col = find_first_col(raw, ["notional", "notional_usdt", "entry_notional", "position_notional"])

    time_col = find_first_col(raw, [
        "close_time", "exit_time", "closed_at", "exit_ts", "close_ts", "timestamp",
        "time", "datetime", "created_at", "entry_time", "entry_ts",
    ])

    out = pd.DataFrame(index=raw.index)
    out["source_file"] = str(path)
    out["source_row"] = np.arange(len(raw))
    out["family_key"] = family

    if id_col:
        out["trade_id"] = raw[id_col].astype(str)
    else:
        out["trade_id"] = out["source_file"] + "#" + out["source_row"].astype(str)

    if symbol_col:
        out["symbol"] = raw[symbol_col].astype(str)
    else:
        out["symbol"] = "unknown"

    if side_col:
        out["side"] = raw[side_col].astype(str).str.lower()
    else:
        out["side"] = "unknown"

    if time_col:
        out["event_time"] = parse_time_series(raw[time_col])
    else:
        out["event_time"] = pd.NaT

    if pnl_col:
        out["pnl"] = pd.to_numeric(raw[pnl_col], errors="coerce")
    else:
        out["pnl"] = np.nan

    if ret_bps_col:
        out["return_bps"] = pd.to_numeric(raw[ret_bps_col], errors="coerce")
    else:
        out["return_bps"] = np.nan

    if qty_col:
        out["qty"] = pd.to_numeric(raw[qty_col], errors="coerce")
    else:
        out["qty"] = np.nan

    if notional_col:
        out["notional"] = pd.to_numeric(raw[notional_col], errors="coerce")
    else:
        out["notional"] = np.nan

    if status_col:
        out["status"] = raw[status_col].astype(str).str.lower()
    else:
        out["status"] = "unknown"

    # Keep only likely closed/realized trades. If status is unknown, pnl presence is enough.
    status = out["status"].fillna("unknown").astype(str).str.lower()
    closed_mask = (
        status.str.contains("closed|close|exit|filled|done|realized", regex=True)
        | (status == "unknown")
        | (out["pnl"].notna())
    )
    out = out[closed_mask].copy()

    # Need at least pnl or return_bps to be useful. For decision quality, pnl is primary.
    out = out[(out["pnl"].notna()) | (out["return_bps"].notna())].copy()

    # If pnl missing but return_bps and notional exist, estimate pnl.
    missing_pnl = out["pnl"].isna() & out["return_bps"].notna() & out["notional"].notna()
    out.loc[missing_pnl, "pnl"] = out.loc[missing_pnl, "notional"] * out.loc[missing_pnl, "return_bps"] / 10000.0

    out = out[out["pnl"].notna()].copy()
    if out.empty:
        return out

    # Remove rows that are obviously still open placeholders.
    out = out[~out["status"].astype(str).str.contains("open|pending|active", regex=True, na=False)].copy()

    return out


def load_all_trades(base_dir: Path) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    files = discover_trade_files(base_dir)
    frames: List[pd.DataFrame] = []
    file_report: List[Dict[str, Any]] = []

    for path in files:
        df = read_table(path)
        if df is None or df.empty:
            file_report.append({"file": str(path), "status": "skip_empty_or_unreadable", "rows": 0, "normalized_rows": 0})
            continue
        norm = normalize_trade_df(path, df)
        file_report.append({
            "file": str(path),
            "status": "ok" if not norm.empty else "skip_no_closed_pnl_rows",
            "rows": int(len(df)),
            "normalized_rows": int(len(norm)),
            "family_key": None if norm.empty else str(norm["family_key"].iloc[0]),
        })
        if not norm.empty:
            frames.append(norm)

    if not frames:
        return pd.DataFrame(), file_report

    trades = pd.concat(frames, ignore_index=True)
    trades["event_time"] = pd.to_datetime(trades["event_time"], errors="coerce")
    trades["pnl"] = pd.to_numeric(trades["pnl"], errors="coerce")
    trades["return_bps"] = pd.to_numeric(trades["return_bps"], errors="coerce")
    trades = trades[trades["pnl"].notna()].copy()

    # Deduplication: prefer family+trade_id where available; else exact file row.
    trades["dedupe_key"] = trades["family_key"].astype(str) + "|" + trades["trade_id"].astype(str)
    before = len(trades)
    trades = trades.drop_duplicates(subset=["dedupe_key"], keep="last").copy()
    after = len(trades)

    # If many loggers reused blank ids, dedupe_key may over-deduplicate. Rescue with file+row when too aggressive.
    if before > 0 and after < before * 0.5:
        trades = pd.concat(frames, ignore_index=True)
        trades["event_time"] = pd.to_datetime(trades["event_time"], errors="coerce")
        trades["pnl"] = pd.to_numeric(trades["pnl"], errors="coerce")
        trades = trades[trades["pnl"].notna()].copy()
        trades["dedupe_key"] = trades["source_file"].astype(str) + "|" + trades["source_row"].astype(str)
        trades = trades.drop_duplicates(subset=["dedupe_key"], keep="last").copy()

    trades = trades.sort_values(["event_time", "source_file", "source_row"], na_position="last").reset_index(drop=True)
    return trades, file_report


# -----------------------------
# Metrics
# -----------------------------

def compute_family_metrics(trades: pd.DataFrame, recent_window_trades: int, recent_window_days: int) -> Dict[str, FamilyMetrics]:
    result: Dict[str, FamilyMetrics] = {}
    if trades.empty:
        return result

    for family_key, g in trades.groupby("family_key", dropna=False):
        family_key = str(family_key)
        g = g.copy().sort_values("event_time", na_position="last")
        pnls = pd.to_numeric(g["pnl"], errors="coerce").dropna()
        if pnls.empty:
            continue

        times = pd.to_datetime(g["event_time"], errors="coerce")
        valid_times = times.dropna()
        first_time = valid_times.min().isoformat() if not valid_times.empty else None
        last_time = valid_times.max().isoformat() if not valid_times.empty else None

        # Recent subset: union of last N trades and last D days if timestamps exist.
        recent_by_n = g.tail(max(1, recent_window_trades))
        if not valid_times.empty:
            cutoff = valid_times.max() - pd.Timedelta(days=recent_window_days)
            recent_by_days = g[times >= cutoff]
            recent = pd.concat([recent_by_n, recent_by_days]).drop_duplicates(subset=["dedupe_key"])
        else:
            recent = recent_by_n
        recent_pnls = pd.to_numeric(recent["pnl"], errors="coerce").dropna()

        ret_bps = pd.to_numeric(g.get("return_bps", pd.Series(dtype=float)), errors="coerce").dropna()

        # Daily distribution.
        daily_bad_days = 0
        daily_good_days = 0
        worst_day_pnl = float(pnls.min())
        best_day_pnl = float(pnls.max())
        if not valid_times.empty:
            tmp = g.copy()
            tmp["date"] = pd.to_datetime(tmp["event_time"], errors="coerce").dt.date
            daily = tmp.dropna(subset=["date"]).groupby("date")["pnl"].sum()
            if not daily.empty:
                daily_bad_days = int((daily < 0).sum())
                daily_good_days = int((daily > 0).sum())
                worst_day_pnl = float(daily.min())
                best_day_pnl = float(daily.max())

        metrics = FamilyMetrics(
            family_key=family_key,
            trade_count=int(len(pnls)),
            first_trade_time=first_time,
            last_trade_time=last_time,
            unique_symbols=int(g["symbol"].nunique(dropna=True)) if "symbol" in g.columns else 0,
            total_pnl=float(pnls.sum()),
            avg_pnl=float(pnls.mean()),
            median_pnl=float(pnls.median()),
            win_rate=float((pnls > 0).mean()),
            profit_factor=profit_factor(pnls),
            max_drawdown=max_drawdown_from_pnl(pnls.tolist()),
            avg_return_bps=float(ret_bps.mean()) if not ret_bps.empty else None,
            median_return_bps=float(ret_bps.median()) if not ret_bps.empty else None,
            p05_pnl=float(pnls.quantile(0.05)),
            p95_pnl=float(pnls.quantile(0.95)),
            recent_trade_count=int(len(recent_pnls)),
            recent_total_pnl=float(recent_pnls.sum()) if not recent_pnls.empty else 0.0,
            recent_avg_pnl=float(recent_pnls.mean()) if not recent_pnls.empty else 0.0,
            recent_win_rate=float((recent_pnls > 0).mean()) if not recent_pnls.empty else 0.0,
            recent_profit_factor=profit_factor(recent_pnls) if not recent_pnls.empty else 0.0,
            recent_max_drawdown=max_drawdown_from_pnl(recent_pnls.tolist()) if not recent_pnls.empty else 0.0,
            daily_bad_days=daily_bad_days,
            daily_good_days=daily_good_days,
            worst_day_pnl=worst_day_pnl,
            best_day_pnl=best_day_pnl,
        )
        result[family_key] = metrics

    return result


# -----------------------------
# Reference loading
# -----------------------------

def row_get(row: Dict[str, Any], candidates: Sequence[str]) -> Optional[Any]:
    norm_map = {norm_col_name(k): v for k, v in row.items()}
    for c in candidates:
        key = norm_col_name(c)
        if key in norm_map:
            return norm_map[key]
    return None


def normalize_family_key(x: Any) -> Optional[str]:
    if x is None:
        return None
    s = str(x).strip().lower().replace("-", "_").replace(" ", "_")
    for fam in FAMILY_KEYS:
        if fam in s:
            return fam
    if "impulse" in s and "long" in s:
        return "impulse_long"
    if "relative" in s:
        return "market_relative_short"
    if "weak" in s or "breakdown" in s:
        return "weak_market_short"
    if "session" in s:
        return "session_short"
    return s if s else None


def parse_reference_rows(rows: List[Dict[str, Any]], source: str) -> Dict[str, ReferenceMetrics]:
    refs: Dict[str, ReferenceMetrics] = {}
    for row in rows:
        fam_raw = row_get(row, ["family_key", "family", "strategy_family", "strategy", "name", "label"])
        fam = normalize_family_key(fam_raw)
        if not fam or fam == "unknown":
            # Try finding family names inside any value.
            joined = " ".join(str(v) for v in row.values()).lower().replace("-", "_")
            fam = None
            for fk in FAMILY_KEYS:
                if fk in joined:
                    fam = fk
                    break
        if not fam:
            continue

        wr = safe_float(row_get(row, ["win_rate", "wr", "hit_rate", "winrate"]))
        if wr is not None and wr > 1.0:
            wr = wr / 100.0

        pf = safe_float(row_get(row, ["profit_factor", "pf"]))
        max_dd = safe_float(row_get(row, ["max_drawdown", "max_dd", "max_dd_usdt", "drawdown"]))
        # Normalize drawdown as negative if source used positive magnitude.
        if max_dd is not None and max_dd > 0:
            max_dd = -abs(max_dd)

        refs[fam] = ReferenceMetrics(
            family_key=fam,
            trade_count=safe_float(row_get(row, ["trade_count", "trades", "n", "count"])),
            total_pnl=safe_float(row_get(row, ["total_pnl", "net_pnl", "pnl", "total_return_usdt"])),
            avg_pnl=safe_float(row_get(row, ["avg_pnl", "mean_pnl", "expectancy", "expectancy_usdt", "pnl_per_trade"])),
            win_rate=wr,
            profit_factor=pf,
            max_drawdown=max_dd,
            avg_return_bps=safe_float(row_get(row, ["avg_return_bps", "mean_bps", "expectancy_bps", "avg_bps"])),
            source=source,
        )
    return refs


def load_reference_file(path: Optional[Path]) -> Dict[str, ReferenceMetrics]:
    if not path or not path.exists():
        return {}
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
            rows = df.to_dict(orient="records")
            return parse_reference_rows(rows, str(path))
        if path.suffix.lower() in {".json", ".jsonl"}:
            if path.suffix.lower() == ".jsonl":
                df = pd.read_json(path, lines=True)
                return parse_reference_rows(df.to_dict(orient="records"), str(path))
            with path.open("r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, list):
                return parse_reference_rows(obj, str(path))
            if isinstance(obj, dict):
                # Shape: {"old_short": {metrics...}}
                rows: List[Dict[str, Any]] = []
                for k, v in obj.items():
                    if isinstance(v, dict):
                        r = dict(v)
                        r.setdefault("family_key", k)
                        rows.append(r)
                if rows:
                    return parse_reference_rows(rows, str(path))
                for key in ["families", "results", "summary", "data"]:
                    if isinstance(obj.get(key), list):
                        return parse_reference_rows(obj[key], str(path))
                    if isinstance(obj.get(key), dict):
                        rows = []
                        for k, v in obj[key].items():
                            if isinstance(v, dict):
                                r = dict(v)
                                r.setdefault("family_key", k)
                                rows.append(r)
                        return parse_reference_rows(rows, str(path))
    except Exception:
        return {}
    return {}


def discover_reference_candidates(workspace: Path) -> List[Path]:
    if not workspace.exists():
        return []
    candidates: List[Path] = []
    positive = ["reference", "backtest", "validation", "optimizer", "summary", "family", "portfolio"]
    negative = ["trade", "trades", "normalized", "drift_report", "decision", "health"]
    for root, _, filenames in os.walk(workspace):
        # Avoid newly generated output folder loops becoming huge.
        if "edge_factory_drift_monitor" in str(root).lower():
            continue
        for fn in filenames:
            p = Path(root) / fn
            if p.suffix.lower() not in {".csv", ".json", ".jsonl"}:
                continue
            name = p.name.lower()
            if any(n in name for n in negative):
                continue
            if any(pos in name for pos in positive):
                candidates.append(p)
    # Recent and likely first.
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return candidates[:100]


def load_best_available_references(workspace: Path, explicit_reference: Optional[Path]) -> Tuple[Dict[str, ReferenceMetrics], List[str]]:
    notes: List[str] = []
    if explicit_reference:
        refs = load_reference_file(explicit_reference)
        notes.append(f"explicit_reference={explicit_reference} loaded_families={sorted(refs.keys())}")
        return refs, notes

    merged: Dict[str, ReferenceMetrics] = {}
    for p in discover_reference_candidates(workspace):
        refs = load_reference_file(p)
        if not refs:
            continue
        for fam, ref in refs.items():
            if fam not in merged:
                merged[fam] = ref
        if all(fam in merged for fam in ACTIVE_FAMILY_KEYS):
            break
    notes.append(f"auto_reference_loaded_families={sorted(merged.keys())}")
    return merged, notes


# -----------------------------
# Decision logic
# -----------------------------

def compare_and_decide(
    metrics: FamilyMetrics,
    ref: Optional[ReferenceMetrics],
    min_trades: int,
    min_hard_trades: int,
) -> DriftDecision:
    reasons: List[str] = []
    drift: Dict[str, Any] = {}

    live_dict = asdict(metrics)
    ref_dict = asdict(ref) if ref else None

    if metrics.trade_count < min_trades:
        return DriftDecision(
            family_key=metrics.family_key,
            status="INSUFFICIENT_DATA",
            confidence="low",
            reasons=[f"trade_count {metrics.trade_count} < min_trades {min_trades}"],
            live=live_dict,
            reference=ref_dict,
            drift={},
            recommended_next_action="keep running; do not change allocation from this sample alone",
        )

    if ref is None:
        # No backtest baseline. Still catch obvious live failure.
        status = "NO_REFERENCE"
        confidence = "medium" if metrics.trade_count >= min_hard_trades else "low"
        if metrics.total_pnl < 0 and metrics.recent_total_pnl < 0 and metrics.profit_factor < 0.85:
            status = "WATCH"
            reasons.append("negative total and recent live pnl with weak profit factor, but no reference baseline exists")
        else:
            reasons.append("no usable backtest/reference metrics found")
        return DriftDecision(
            family_key=metrics.family_key,
            status=status,
            confidence=confidence,
            reasons=reasons,
            live=live_dict,
            reference=None,
            drift={},
            recommended_next_action="create or pass an explicit family backtest reference file; keep monitoring live distribution",
        )

    avg_pnl_ratio = ratio_safe(metrics.avg_pnl, ref.avg_pnl)
    wr_delta = None if ref.win_rate is None else float(metrics.win_rate - ref.win_rate)
    pf_ratio = ratio_safe(metrics.profit_factor if math.isfinite(metrics.profit_factor) else None, ref.profit_factor)
    dd_ratio = None
    if ref.max_drawdown is not None and abs(ref.max_drawdown) > 1e-12:
        dd_ratio = abs(metrics.max_drawdown) / abs(ref.max_drawdown)
    bps_ratio = ratio_safe(metrics.avg_return_bps, ref.avg_return_bps)

    drift.update({
        "avg_pnl_ratio_live_vs_ref": avg_pnl_ratio,
        "win_rate_delta_live_minus_ref": wr_delta,
        "profit_factor_ratio_live_vs_ref": pf_ratio,
        "drawdown_magnitude_ratio_live_vs_ref": dd_ratio,
        "avg_return_bps_ratio_live_vs_ref": bps_ratio,
    })

    score = 0

    # Expectancy drift.
    if ref.avg_pnl is not None:
        if metrics.avg_pnl < 0 <= ref.avg_pnl:
            score -= 3
            reasons.append("live avg_pnl is negative while reference avg_pnl is non-negative")
        elif avg_pnl_ratio is not None and avg_pnl_ratio < 0.35:
            score -= 2
            reasons.append(f"live avg_pnl is severely below reference ratio={avg_pnl_ratio:.2f}")
        elif avg_pnl_ratio is not None and avg_pnl_ratio < 0.65:
            score -= 1
            reasons.append(f"live avg_pnl is below reference ratio={avg_pnl_ratio:.2f}")
        elif avg_pnl_ratio is not None and avg_pnl_ratio >= 0.80:
            score += 1
            reasons.append(f"live avg_pnl is close to reference ratio={avg_pnl_ratio:.2f}")

    # Win-rate drift.
    if wr_delta is not None:
        if wr_delta <= -0.12:
            score -= 2
            reasons.append(f"live win_rate is much lower than reference delta={wr_delta:.3f}")
        elif wr_delta <= -0.07:
            score -= 1
            reasons.append(f"live win_rate is lower than reference delta={wr_delta:.3f}")
        elif wr_delta >= -0.03:
            score += 1
            reasons.append(f"live win_rate is near/above reference delta={wr_delta:.3f}")

    # PF drift.
    if ref.profit_factor is not None and pf_ratio is not None:
        if metrics.profit_factor < 1.0 and ref.profit_factor >= 1.1:
            score -= 2
            reasons.append("live profit_factor is below 1 while reference is profitable")
        elif pf_ratio < 0.55:
            score -= 2
            reasons.append(f"live profit_factor is severely below reference ratio={pf_ratio:.2f}")
        elif pf_ratio < 0.75:
            score -= 1
            reasons.append(f"live profit_factor is below reference ratio={pf_ratio:.2f}")
        elif pf_ratio >= 0.85:
            score += 1
            reasons.append(f"live profit_factor is close to reference ratio={pf_ratio:.2f}")

    # Drawdown drift. Drawdown is negative; compare absolute magnitude.
    if dd_ratio is not None:
        if dd_ratio > 2.0:
            score -= 2
            reasons.append(f"live drawdown magnitude is >2x reference dd_ratio={dd_ratio:.2f}")
        elif dd_ratio > 1.5:
            score -= 1
            reasons.append(f"live drawdown magnitude is elevated dd_ratio={dd_ratio:.2f}")

    # Recent deterioration matters but should not instantly kill.
    if metrics.recent_trade_count >= max(10, min_trades // 2):
        if metrics.recent_total_pnl < 0 and metrics.recent_profit_factor < 0.8:
            score -= 1
            reasons.append("recent window is negative with weak recent profit factor")
        if metrics.recent_avg_pnl < 0 < metrics.avg_pnl:
            score -= 1
            reasons.append("recent avg_pnl turned negative while full live avg_pnl is positive")

    # Live-only hard red flags.
    if metrics.total_pnl < 0 and metrics.avg_pnl < 0 and metrics.profit_factor < 0.75:
        score -= 2
        reasons.append("live total pnl, avg pnl, and profit factor are all bad")

    if not reasons:
        reasons.append("no major drift symptoms detected")

    hard_sample = metrics.trade_count >= min_hard_trades
    if score >= 1:
        status = "OK"
    elif score == 0:
        status = "WATCH"
    elif score in {-1, -2}:
        status = "WATCH"
    elif score in {-3, -4}:
        status = "REDUCE" if hard_sample else "WATCH"
    else:
        status = "DISABLE_CANDIDATE" if hard_sample else "REDUCE"

    if metrics.trade_count >= min_hard_trades:
        confidence = "high"
    elif metrics.trade_count >= min_trades:
        confidence = "medium"
    else:
        confidence = "low"

    action_map = {
        "OK": "keep current allocation; continue monitoring",
        "WATCH": "do not increase allocation; inspect recent trades and wait for more sample",
        "REDUCE": "candidate for capital reduction by governor; do not disable automatically without lifecycle confirmation",
        "DISABLE_CANDIDATE": "candidate for lifecycle disable/kill-switch review; require confirmation from additional checks",
    }

    return DriftDecision(
        family_key=metrics.family_key,
        status=status,
        confidence=confidence,
        reasons=reasons,
        live=live_dict,
        reference=ref_dict,
        drift=drift,
        recommended_next_action=action_map.get(status, "continue monitoring"),
    )


# -----------------------------
# Reporting
# -----------------------------

def write_json(path: Path, obj: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_markdown_report(
    path: Path,
    base_dir: Path,
    workspace: Path,
    trades: pd.DataFrame,
    metrics_by_family: Dict[str, FamilyMetrics],
    decisions: List[DriftDecision],
    file_report: List[Dict[str, Any]],
    reference_notes: List[str],
    contract: Dict[str, Any],
) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Live-vs-Backtest Drift Monitor Report")
    lines.append("")
    lines.append(f"Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"Base dir: `{base_dir}`")
    lines.append(f"Workspace: `{workspace}`")
    lines.append("")

    lines.append("## Executive summary")
    lines.append("")
    if trades.empty:
        lines.append("No usable closed trades found.")
    else:
        total_pnl = float(pd.to_numeric(trades["pnl"], errors="coerce").sum())
        lines.append(f"Total normalized trades: **{len(trades)}**")
        lines.append(f"Total live/paper PnL across detected families: **{total_pnl:.6f} USDT**")
        lines.append("")
        status_counts: Dict[str, int] = {}
        for d in decisions:
            status_counts[d.status] = status_counts.get(d.status, 0) + 1
        lines.append("Decision counts: " + ", ".join(f"**{k}={v}**" for k, v in sorted(status_counts.items())))
    lines.append("")

    lines.append("## Family decisions")
    lines.append("")
    lines.append("| Family | Status | Confidence | Trades | Total PnL | Avg PnL | Win rate | PF | Max DD | Action |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for d in decisions:
        m = d.live
        pf = m.get("profit_factor")
        pf_txt = "inf" if pf == float("inf") or str(pf) == "inf" else f"{float(pf):.3f}" if pf is not None else "n/a"
        lines.append(
            f"| {d.family_key} | {d.status} | {d.confidence} | "
            f"{m.get('trade_count', 0)} | {float(m.get('total_pnl', 0)):.6f} | "
            f"{float(m.get('avg_pnl', 0)):.6f} | {float(m.get('win_rate', 0)):.2%} | "
            f"{pf_txt} | {float(m.get('max_drawdown', 0)):.6f} | {d.recommended_next_action} |"
        )
    lines.append("")

    for d in decisions:
        lines.append(f"### {d.family_key}")
        lines.append("")
        lines.append(f"Status: **{d.status}** / confidence: **{d.confidence}**")
        lines.append("")
        lines.append("Reasons:")
        for r in d.reasons:
            lines.append(f"- {r}")
        if d.drift:
            lines.append("")
            lines.append("Drift:")
            for k, v in d.drift.items():
                if v is None:
                    lines.append(f"- `{k}`: n/a")
                else:
                    lines.append(f"- `{k}`: {float(v):.6f}")
        lines.append("")

    lines.append("## Reference loading notes")
    lines.append("")
    for n in reference_notes:
        lines.append(f"- {n}")
    lines.append("")

    lines.append("## File scan")
    lines.append("")
    lines.append("| File | Status | Rows | Normalized rows | Family |")
    lines.append("|---|---:|---:|---:|---:|")
    for fr in file_report[:200]:
        lines.append(
            f"| `{fr.get('file')}` | {fr.get('status')} | {fr.get('rows')} | "
            f"{fr.get('normalized_rows')} | {fr.get('family_key') or ''} |"
        )
    if len(file_report) > 200:
        lines.append(f"\n_File report truncated: {len(file_report) - 200} more files._")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------
# Main
# -----------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory live-vs-backtest drift monitor")
    p.add_argument("--base_dir", default=DEFAULT_BASE_DIR, help="MASTER_UPPER_SYSTEM paper/live output directory")
    p.add_argument("--workspace", default=DEFAULT_WORKSPACE, help="edge_lab_new workspace directory")
    p.add_argument("--sizing_contract", default=DEFAULT_SIZING_CONTRACT, help="position_sizing_contract.json path")
    p.add_argument("--reference_file", default=None, help="optional explicit backtest/reference CSV or JSON")
    p.add_argument("--out_dir", default=None, help="optional output directory; default workspace/edge_factory_drift_monitor")
    p.add_argument("--min_trades", type=int, default=DEFAULT_MIN_TRADES_FOR_DECISION)
    p.add_argument("--min_hard_trades", type=int, default=DEFAULT_MIN_TRADES_FOR_HARD_DECISION)
    p.add_argument("--recent_window_trades", type=int, default=DEFAULT_RECENT_WINDOW_TRADES)
    p.add_argument("--recent_window_days", type=int, default=DEFAULT_RECENT_WINDOW_DAYS)
    p.add_argument("--include_session_short", action="store_true", help="include disabled session_short in report if found")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    base_dir = Path(args.base_dir)
    workspace = Path(args.workspace)
    sizing_contract_path = Path(args.sizing_contract) if args.sizing_contract else None
    explicit_ref = Path(args.reference_file) if args.reference_file else None

    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_drift_monitor"
    report_dir = out_root / f"drift_report_{now_stamp()}"
    ensure_dir(report_dir)

    run_meta = {
        "base_dir": str(base_dir),
        "workspace": str(workspace),
        "sizing_contract": str(sizing_contract_path) if sizing_contract_path else None,
        "reference_file": str(explicit_ref) if explicit_ref else None,
        "report_dir": str(report_dir),
        "args": vars(args),
    }

    try:
        contract = load_sizing_contract(sizing_contract_path)
        trades, file_report = load_all_trades(base_dir)

        write_json(report_dir / "file_scan_report.json", file_report)
        write_json(report_dir / "run_meta.json", run_meta)

        if trades.empty:
            write_markdown_report(
                report_dir / "drift_report.md",
                base_dir=base_dir,
                workspace=workspace,
                trades=trades,
                metrics_by_family={},
                decisions=[],
                file_report=file_report,
                reference_notes=["no trades loaded"],
                contract=contract,
            )
            print("EDGE FACTORY DRIFT MONITOR")
            print("No usable closed trades found.")
            print(f"Report dir: {report_dir}")
            return 2

        # Optional: filter disabled session_short unless asked.
        if not args.include_session_short:
            trades = trades[trades["family_key"] != "session_short"].copy()

        # Add expected notional from sizing contract when available.
        trades["expected_notional_from_contract"] = trades["family_key"].map(
            lambda fam: infer_expected_notional(contract, str(fam))
        )

        metrics_by_family = compute_family_metrics(
            trades,
            recent_window_trades=args.recent_window_trades,
            recent_window_days=args.recent_window_days,
        )

        refs, reference_notes = load_best_available_references(workspace, explicit_ref)

        # Ensure active families appear in decisions even if no trades yet.
        decisions: List[DriftDecision] = []
        family_order = ACTIVE_FAMILY_KEYS + sorted(k for k in metrics_by_family.keys() if k not in ACTIVE_FAMILY_KEYS)
        seen = set()
        for fam in family_order:
            if fam in seen:
                continue
            seen.add(fam)
            if fam in metrics_by_family:
                d = compare_and_decide(
                    metrics_by_family[fam],
                    refs.get(fam),
                    min_trades=args.min_trades,
                    min_hard_trades=args.min_hard_trades,
                )
            else:
                d = DriftDecision(
                    family_key=fam,
                    status="INSUFFICIENT_DATA",
                    confidence="low",
                    reasons=["no normalized closed trades found for this active family"],
                    live=asdict(FamilyMetrics(family_key=fam)),
                    reference=asdict(refs[fam]) if fam in refs else None,
                    drift={},
                    recommended_next_action="keep logger running or inspect whether this family is inactive by design",
                )
            decisions.append(d)

        # Persist outputs.
        summary_rows = []
        for fam, m in metrics_by_family.items():
            row = asdict(m)
            row["expected_notional_from_contract"] = infer_expected_notional(contract, fam)
            if fam in refs:
                row["reference_source"] = refs[fam].source
                row["reference_avg_pnl"] = refs[fam].avg_pnl
                row["reference_win_rate"] = refs[fam].win_rate
                row["reference_profit_factor"] = refs[fam].profit_factor
                row["reference_max_drawdown"] = refs[fam].max_drawdown
            summary_rows.append(row)

        summary_df = pd.DataFrame(summary_rows).sort_values("family_key") if summary_rows else pd.DataFrame()
        summary_df.to_csv(report_dir / "drift_family_summary.csv", index=False)
        write_json(report_dir / "drift_family_summary.json", summary_rows)
        write_json(report_dir / "drift_decisions.json", [asdict(d) for d in decisions])

        # Keep normalized trades for debugging but avoid Excel-breaking timezone objects.
        trades_out = trades.copy()
        trades_out["event_time"] = trades_out["event_time"].astype(str)
        trades_out.to_csv(report_dir / "normalized_trades.csv", index=False)

        write_markdown_report(
            report_dir / "drift_report.md",
            base_dir=base_dir,
            workspace=workspace,
            trades=trades,
            metrics_by_family=metrics_by_family,
            decisions=decisions,
            file_report=file_report,
            reference_notes=reference_notes,
            contract=contract,
        )

        print("EDGE FACTORY DRIFT MONITOR v1")
        print("=" * 80)
        print(f"base_dir     : {base_dir}")
        print(f"workspace    : {workspace}")
        print(f"report_dir   : {report_dir}")
        print(f"trades       : {len(trades)}")
        print("")
        print("FAMILY DECISIONS")
        print("-" * 80)
        for d in decisions:
            m = d.live
            print(
                f"{d.family_key:24s} status={d.status:20s} conf={d.confidence:6s} "
                f"trades={int(m.get('trade_count', 0)):5d} "
                f"pnl={float(m.get('total_pnl', 0.0)): .6f} "
                f"wr={float(m.get('win_rate', 0.0)): .2%} "
                f"pf={m.get('profit_factor')}"
            )
            for r in d.reasons[:3]:
                print(f"  - {r}")
        print("")
        print(f"Open report: {report_dir / 'drift_report.md'}")
        return 0

    except Exception as e:
        err = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "run_meta": run_meta,
        }
        ensure_dir(report_dir)
        write_json(report_dir / "fatal_error.json", err)
        print("FATAL ERROR in Edge Factory Drift Monitor")
        print(str(e))
        print(f"Details: {report_dir / 'fatal_error.json'}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
