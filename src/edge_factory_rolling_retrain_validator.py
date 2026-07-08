#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY ROLLING RETRAIN / TIME-OOS VALIDATOR v1
====================================================

Purpose
-------
Offline time out-of-sample / rolling robustness validator for the Edge Factory OS.

This module answers:
    Does a schema-clean family/candidate stay alive across time, or was it carried by
    one short period of the 1-year OKX candle universe?

It is designed to run after:
    - edge_factory_schema_aware_validator_v2.py
    - edge_factory_candle_universe_inventory_v2.py

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - promote strategies
    - change capital
    - run --apply
    - generate new strategy trades from raw candles

It DOES:
    - load normalized_oos_trades.csv as trade evidence
    - restrict to symbols with READY_1Y_COVERAGE if candle inventory v2 exists
    - validate active families and schema-clean research candidates
    - run chronological time splits / monthly stability checks
    - compute train/test fold metrics
    - classify targets as TIME_OOS_PASS / TIME_OOS_WATCHLIST / TIME_OOS_FAIL / NEEDS_MORE_DATA
    - write evidence and optionally append evidence-only records to research ledger

Run all schema-clean targets:
    python "C:\Users\alike\edge_factory_rolling_retrain_validator.py"

Run one target:
    python "C:\Users\alike\edge_factory_rolling_retrain_validator.py" --target ret60_reversal_short

Use row-order splits if source has no usable time column:
    python "C:\Users\alike\edge_factory_rolling_retrain_validator.py" --split_mode row_order

Core rule
---------
A pass is evidence only. It is not promotion and cannot alter the active system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

ACTIVE_FAMILIES = {"old_short", "impulse_long", "market_relative_short", "weak_market_short"}
PRIMARY_RESEARCH_CANDIDATES = {"ret60_reversal_short"}
OPTIONAL_RESEARCH_CANDIDATES = {
    "rel_extreme_reversion_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
}

FAMILY_COLS = ["family_key", "family", "strategy", "strategy_key", "candidate_key", "candidate", "label", "name"]
PNL_COLS = ["pnl", "net_pnl_usdt", "pnl_usdt", "net_pnl", "gross_pnl_usdt", "profit"]
SYMBOL_COLS = ["symbol", "inst_id", "instrument", "inst", "ticker", "coin"]
TIME_COLS = ["exit_time", "entry_time", "timestamp", "time", "datetime", "date", "open_time", "close_time", "ts"]

MIN_TOTAL_TRADES = 120
MIN_TEST_TRADES_PER_FOLD = 20
MIN_FOLDS = 4
MIN_TEST_POSITIVE_FOLD_RATE = 0.55
MIN_MONTH_POSITIVE_RATE = 0.50
MIN_TEST_AVG = 0.0
MIN_TEST_PF = 1.05
MAX_TEST_DD_TO_TOTAL = 0.80


@dataclass
class SourceSchema:
    source_path: str
    family_col: str
    pnl_col: str
    symbol_col: Optional[str]
    time_col: Optional[str]
    schema_source: str
    warnings: List[str]


@dataclass
class FoldResult:
    target_key: str
    fold_id: int
    split_label: str
    train_rows: int
    test_rows: int
    train_total: float
    test_total: float
    train_avg: float
    test_avg: float
    train_pf: float
    test_pf: float
    test_wr: float
    test_symbol_count: int
    test_positive_symbol_rate: float
    status: str


@dataclass
class TargetTimeOOSResult:
    target_key: str
    target_type: str
    source_path: str
    split_mode: str
    total_rows_raw: int
    rows_after_ready_universe_filter: int
    rows_after_cleaning: int
    dropped_non_ready_symbol_rows: int
    dropped_bad_pnl_rows: int
    fold_count: int
    valid_fold_count: int
    positive_test_fold_rate: float
    monthly_positive_rate: float
    total_pnl: float
    avg_pnl: float
    full_pf: float
    full_wr: float
    full_symbol_count: int
    test_total_sum: float
    test_avg_mean: float
    test_pf_aggregate: float
    worst_test_fold: float
    max_test_drawdown_proxy: float
    validation_status: str
    ledger_result_status: str
    reasons: List[str]
    warnings: List[str]
    evidence_json: str
    evidence_csv: str
    ledger_task_id: str
    live_allowed: bool
    promotes_or_trades: bool


@dataclass
class ValidatorState:
    generated_at: str
    workspace: str
    source_path: str
    ready_universe_path: Optional[str]
    split_mode: str
    targets_seen: int
    targets_validated: int
    pass_count: int
    watchlist_count: int
    fail_count: int
    needs_more_data_count: int
    inconclusive_count: int
    ledger_append_enabled: bool
    ledger_records_appended: int
    overall_verdict: str
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_key(x: Any) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def optional_json(path: Optional[Path]) -> Any:
    if not path or not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def find_col(df: pd.DataFrame, options: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): str(c) for c in df.columns}
    for opt in options:
        if opt.lower() in lookup:
            return lookup[opt.lower()]
    for c in df.columns:
        low = str(c).lower()
        if options == TIME_COLS and any(tok in low for tok in ["time", "date", "timestamp", "datetime"]):
            return str(c)
        if options == SYMBOL_COLS and any(tok in low for tok in ["symbol", "inst", "instrument", "ticker", "coin"]):
            return str(c)
    return None


def normalize_symbol(raw: Any) -> Optional[str]:
    s = str(raw or "").strip().upper().replace("_", "-")
    if not s or s in {"NAN", "NONE", "NULL", "UNKNOWN", "TRUE", "FALSE"}:
        return None
    if re.match(r"^[A-Z0-9]+-USDT-SWAP$", s):
        return s
    if re.match(r"^[A-Z0-9]+-USDT$", s):
        return f"{s.split('-')[0]}-USDT-SWAP"
    if re.match(r"^[A-Z0-9]+USDT$", s):
        return f"{s[:-4]}-USDT-SWAP"
    if re.match(r"^[A-Z][A-Z0-9]{1,14}$", s):
        return f"{s}-USDT-SWAP"
    return None


def latest_normalized_trades(workspace: Path) -> Optional[Path]:
    paths: List[Path] = []
    for root_name in ["edge_factory_rolling_oos_validator", "edge_factory_rolling_oos_validator_v2"]:
        root = workspace / root_name
        if root.exists():
            paths.extend(root.rglob("normalized_oos_trades.csv"))
    paths = [p for p in paths if p.exists() and p.is_file()]
    if not paths:
        return None
    paths.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return paths[0]


def latest_schema_v2_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_schema_aware_validator_v2", "schema_aware_v2_")
    if not d:
        return None
    p = d / "schema_aware_validator_v2_state.json"
    return p if p.exists() else None


def latest_ready_universe(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_candle_universe_inventory_v2", "candle_inventory_v2_")
    if not d:
        return None
    p = d / "candle_universe_ready_symbols_v2.csv"
    return p if p.exists() else None


def load_schema(workspace: Path, explicit_source: Optional[str]) -> SourceSchema:
    warnings: List[str] = []
    source = Path(explicit_source) if explicit_source else latest_normalized_trades(workspace)
    if source is None or not source.exists():
        raise FileNotFoundError("normalized_oos_trades.csv not found")

    head = pd.read_csv(source, nrows=1000)
    family_col = find_col(head, FAMILY_COLS)
    pnl_col = find_col(head, PNL_COLS)
    symbol_col = find_col(head, SYMBOL_COLS)
    time_col = find_col(head, TIME_COLS)

    # Optional: use schema-aware v2 state only as a consistency check, not as authority for time_col.
    schema_state_path = latest_schema_v2_state(workspace)
    schema_source = str(schema_state_path) if schema_state_path else "inferred_from_normalized_trades"
    obj = optional_json(schema_state_path)
    if isinstance(obj, dict):
        state = obj.get("state") if isinstance(obj.get("state"), dict) else {}
        for name, current, recommended in [
            ("family_col", family_col, state.get("family_col")),
            ("pnl_col", pnl_col, state.get("pnl_col")),
            ("symbol_col", symbol_col, state.get("symbol_col")),
        ]:
            if recommended and current and str(recommended) != str(current):
                warnings.append(f"schema v2 {name}={recommended} differs from inferred {current}; using inferred")

    if not family_col or not pnl_col:
        raise ValueError(f"Required columns missing. family_col={family_col}, pnl_col={pnl_col}, columns={list(head.columns)}")
    if time_col and symbol_col and str(time_col).lower() == str(symbol_col).lower():
        warnings.append("time_col inferred same as symbol_col; forcing row_order time splits")
        time_col = None
    return SourceSchema(str(source), str(family_col), str(pnl_col), str(symbol_col) if symbol_col else None, str(time_col) if time_col else None, schema_source, warnings)


def parse_time_series(series: pd.Series) -> pd.Series:
    num = pd.to_numeric(series, errors="coerce")
    if num.notna().mean() > 0.85:
        med = float(num.dropna().median()) if not num.dropna().empty else 0.0
        if med > 1e17:
            unit = "ns"
        elif med > 1e14:
            unit = "us"
        elif med > 1e11:
            unit = "ms"
        else:
            unit = "s"
        return pd.to_datetime(num, unit=unit, errors="coerce", utc=True)
    return pd.to_datetime(series, errors="coerce", utc=True)


def load_ready_symbols(path: Optional[Path]) -> Tuple[set[str], List[str]]:
    warnings: List[str] = []
    if path is None or not path.exists():
        warnings.append("ready candle universe not found; no ready-symbol filter will be applied")
        return set(), warnings
    try:
        df = pd.read_csv(path)
        if "symbol" not in df.columns:
            warnings.append("ready universe file has no symbol column")
            return set(), warnings
        syms = set(df["symbol"].dropna().map(normalize_symbol).dropna().astype(str))
        return syms, warnings
    except Exception as e:
        warnings.append(f"failed to load ready universe: {e}")
        return set(), warnings


def discover_targets(workspace: Path, target: Optional[str], active_only: bool, candidates_only: bool, include_optional_candidates: bool) -> List[str]:
    if target:
        return [safe_key(target)]
    targets: set[str] = set()
    if not candidates_only:
        targets.update(ACTIVE_FAMILIES)
    if not active_only:
        targets.update(PRIMARY_RESEARCH_CANDIDATES)
        if include_optional_candidates:
            targets.update(OPTIONAL_RESEARCH_CANDIDATES)
    return sorted(targets)


def clean_source_for_target(df: pd.DataFrame, schema: SourceSchema, target: str, ready_symbols: set[str], use_ready_filter: bool) -> Tuple[pd.DataFrame, int, int, int, List[str]]:
    warnings: List[str] = []
    fam = df[schema.family_col].astype(str).str.lower().str.strip()
    key = safe_key(target)
    mask = fam == key
    if not mask.any():
        mask = fam.str.contains(key, regex=False, na=False)
        if mask.any():
            warnings.append("used contains-match because exact family key found no rows")
    tdf = df.loc[mask].copy()
    raw_rows = int(len(tdf))
    if tdf.empty:
        return tdf, raw_rows, 0, 0, warnings

    bad_symbol_drop = 0
    non_ready_drop = 0
    if schema.symbol_col and schema.symbol_col in tdf.columns:
        tdf["__symbol"] = tdf[schema.symbol_col].map(normalize_symbol)
        bad = tdf["__symbol"].isna()
        bad_symbol_drop = int(bad.sum())
        if bad_symbol_drop:
            warnings.append(f"dropped {bad_symbol_drop} rows with invalid symbols")
        tdf = tdf.loc[~bad].copy()
        if use_ready_filter and ready_symbols:
            non_ready = ~tdf["__symbol"].isin(ready_symbols)
            non_ready_drop = int(non_ready.sum())
            if non_ready_drop:
                warnings.append(f"dropped {non_ready_drop} rows outside ready candle universe")
            tdf = tdf.loc[~non_ready].copy()
    else:
        tdf["__symbol"] = "UNKNOWN"
        warnings.append("symbol column missing; symbol breadth metrics disabled")

    tdf["__pnl"] = pd.to_numeric(tdf[schema.pnl_col], errors="coerce")
    bad_pnl = int(tdf["__pnl"].isna().sum())
    if bad_pnl:
        warnings.append(f"dropped {bad_pnl} rows with non-numeric pnl")
    tdf = tdf.dropna(subset=["__pnl"]).copy()

    if schema.time_col and schema.time_col in tdf.columns:
        tdf["__time"] = parse_time_series(tdf[schema.time_col])
        if tdf["__time"].notna().sum() < max(10, int(0.5 * len(tdf))):
            warnings.append("time column parse failed for many rows; row_order splits should be preferred")
            tdf["__time"] = pd.NaT
    else:
        tdf["__time"] = pd.NaT
    return tdf, raw_rows, bad_symbol_drop, non_ready_drop, warnings


def profit_factor(pnl: pd.Series) -> float:
    gains = float(pnl[pnl > 0].sum())
    losses = float((-pnl[pnl < 0]).sum())
    if losses <= 0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def max_drawdown_proxy(pnl_values: pd.Series) -> float:
    if pnl_values.empty:
        return 0.0
    eq = pnl_values.cumsum()
    dd = eq - eq.cummax()
    return float(dd.min()) if not dd.empty else 0.0


def symbol_positive_rate(df: pd.DataFrame) -> Tuple[int, float]:
    if df.empty or "__symbol" not in df.columns:
        return 0, 0.0
    g = df.groupby("__symbol")["__pnl"].sum()
    if g.empty:
        return 0, 0.0
    return int(len(g)), float((g > 0).mean())


def create_splits(tdf: pd.DataFrame, split_mode: str, folds: int) -> Tuple[List[Tuple[str, pd.DataFrame, pd.DataFrame]], str, List[str]]:
    warnings: List[str] = []
    if tdf.empty:
        return [], split_mode, warnings
    use_time = split_mode == "time" or (split_mode == "auto" and "__time" in tdf.columns and tdf["__time"].notna().sum() >= max(10, int(0.7 * len(tdf))))
    if use_time:
        tdf2 = tdf.dropna(subset=["__time"]).sort_values("__time").copy()
        if tdf2.empty:
            warnings.append("time split requested but no parseable time; falling back to row_order")
            use_time = False
        else:
            # Prefer month splits if enough months exist.
            tdf2["__period"] = tdf2["__time"].dt.strftime("%Y-%m")
            periods = sorted(tdf2["__period"].dropna().unique().tolist())
            if len(periods) >= MIN_FOLDS + 1:
                splits = []
                for i in range(1, len(periods)):
                    train_periods = periods[:i]
                    test_period = periods[i]
                    train = tdf2[tdf2["__period"].isin(train_periods)].copy()
                    test = tdf2[tdf2["__period"] == test_period].copy()
                    splits.append((f"month_{test_period}", train, test))
                return splits, "time_monthly_expanding", warnings
            warnings.append("not enough monthly periods; using chronological quantile folds")
            # Fall through to quantile time order below.
            ordered = tdf2
    else:
        ordered = tdf.sort_index().copy()

    n = len(ordered)
    if n < folds * 2:
        return [], "row_order_insufficient", warnings
    fold_size = max(1, n // folds)
    splits = []
    for i in range(1, folds):
        train_end = i * fold_size
        test_end = (i + 1) * fold_size if i < folds - 1 else n
        train = ordered.iloc[:train_end].copy()
        test = ordered.iloc[train_end:test_end].copy()
        splits.append((f"fold_{i}", train, test))
    mode = "time_quantile_expanding" if use_time else "row_order_expanding"
    return splits, mode, warnings


def aggregate_metrics(df: pd.DataFrame) -> Dict[str, float]:
    pnl = df["__pnl"] if "__pnl" in df.columns else pd.Series(dtype=float)
    if pnl.empty:
        return {"rows": 0, "total": 0.0, "avg": 0.0, "pf": 0.0, "wr": 0.0, "symbols": 0, "pos_symbol_rate": 0.0}
    symbols, psr = symbol_positive_rate(df)
    pf = profit_factor(pnl)
    return {
        "rows": int(len(pnl)),
        "total": float(pnl.sum()),
        "avg": float(pnl.mean()),
        "pf": 999999.0 if math.isinf(pf) else float(pf),
        "wr": float((pnl > 0).mean()),
        "symbols": symbols,
        "pos_symbol_rate": psr,
    }


def validate_target(target: str, df: pd.DataFrame, schema: SourceSchema, ready_symbols: set[str], use_ready_filter: bool, split_mode: str, folds: int, stamp: str, out_dir: Path, workspace: Path) -> Tuple[TargetTimeOOSResult, List[FoldResult]]:
    tdf, raw_rows, bad_sym_drop, non_ready_drop, warnings = clean_source_for_target(df, schema, target, ready_symbols, use_ready_filter)
    splits, actual_split_mode, split_warnings = create_splits(tdf, split_mode, folds)
    warnings.extend(split_warnings)

    fold_results: List[FoldResult] = []
    for i, (label, train, test) in enumerate(splits, start=1):
        tr = aggregate_metrics(train)
        te = aggregate_metrics(test)
        if te["rows"] < MIN_TEST_TRADES_PER_FOLD:
            status = "TOO_FEW_TEST_TRADES"
        elif te["total"] > 0 and te["avg"] > MIN_TEST_AVG and te["pf"] >= MIN_TEST_PF:
            status = "PASS"
        elif te["total"] > 0:
            status = "WEAK_PASS"
        else:
            status = "FAIL"
        fold_results.append(FoldResult(
            target_key=target,
            fold_id=i,
            split_label=label,
            train_rows=int(tr["rows"]),
            test_rows=int(te["rows"]),
            train_total=round(tr["total"], 8),
            test_total=round(te["total"], 8),
            train_avg=round(tr["avg"], 8),
            test_avg=round(te["avg"], 8),
            train_pf=round(tr["pf"], 8),
            test_pf=round(te["pf"], 8),
            test_wr=round(te["wr"], 6),
            test_symbol_count=int(te["symbols"]),
            test_positive_symbol_rate=round(te["pos_symbol_rate"], 6),
            status=status,
        ))

    full = aggregate_metrics(tdf)
    valid_folds = [f for f in fold_results if f.test_rows >= MIN_TEST_TRADES_PER_FOLD]
    positive_fold_rate = float(sum(1 for f in valid_folds if f.test_total > 0) / len(valid_folds)) if valid_folds else 0.0
    test_total_sum = float(sum(f.test_total for f in valid_folds)) if valid_folds else 0.0
    test_avg_mean = float(sum(f.test_avg for f in valid_folds) / len(valid_folds)) if valid_folds else 0.0
    all_test_pnls = pd.Series([f.test_total for f in valid_folds], dtype=float)
    worst_test = float(all_test_pnls.min()) if not all_test_pnls.empty else 0.0
    dd_proxy = abs(max_drawdown_proxy(all_test_pnls)) if not all_test_pnls.empty else 0.0
    test_gains = float(all_test_pnls[all_test_pnls > 0].sum()) if not all_test_pnls.empty else 0.0
    test_losses = float((-all_test_pnls[all_test_pnls < 0]).sum()) if not all_test_pnls.empty else 0.0
    test_pf_agg = 999999.0 if test_losses <= 0 and test_gains > 0 else (test_gains / test_losses if test_losses > 0 else 0.0)

    # Monthly positive rate, independent from train/test if time exists.
    monthly_positive_rate = 0.0
    if "__time" in tdf.columns and tdf["__time"].notna().sum() > 0:
        tmp = tdf.dropna(subset=["__time"]).copy()
        tmp["__month"] = tmp["__time"].dt.strftime("%Y-%m")
        g = tmp.groupby("__month")["__pnl"].sum()
        monthly_positive_rate = float((g > 0).mean()) if not g.empty else 0.0
    else:
        # fallback: use fold positive rate
        monthly_positive_rate = positive_fold_rate

    reasons: List[str] = []
    if raw_rows <= 0:
        status = "INCONCLUSIVE"
        ledger_status = "INCONCLUSIVE"
        reasons.append("No rows found for target in normalized trade source.")
    elif full["rows"] < MIN_TOTAL_TRADES:
        status = "NEEDS_MORE_DATA"
        ledger_status = "NEEDS_MORE_DATA"
        reasons.append(f"Clean rows {full['rows']} below total threshold {MIN_TOTAL_TRADES}.")
    elif len(valid_folds) < MIN_FOLDS:
        status = "NEEDS_MORE_DATA"
        ledger_status = "NEEDS_MORE_DATA"
        reasons.append(f"Valid folds {len(valid_folds)} below threshold {MIN_FOLDS}.")
    else:
        avg_ok = test_avg_mean > MIN_TEST_AVG
        pf_ok = test_pf_agg >= MIN_TEST_PF
        fold_ok = positive_fold_rate >= MIN_TEST_POSITIVE_FOLD_RATE
        month_ok = monthly_positive_rate >= MIN_MONTH_POSITIVE_RATE
        dd_ok = (dd_proxy <= abs(test_total_sum) * MAX_TEST_DD_TO_TOTAL) if test_total_sum != 0 else False
        reasons.append("Mean test average is positive." if avg_ok else "Mean test average is not positive.")
        reasons.append("Aggregate test PF passes threshold." if pf_ok else "Aggregate test PF is below threshold.")
        reasons.append("Positive test fold rate passes threshold." if fold_ok else "Positive test fold rate is weak.")
        reasons.append("Monthly/fold positive rate passes threshold." if month_ok else "Monthly/fold positive rate is weak.")
        reasons.append("Drawdown proxy is acceptable." if dd_ok else "Drawdown proxy is high relative to total test result.")
        if avg_ok and pf_ok and fold_ok and month_ok and dd_ok:
            status = "TIME_OOS_PASS"
            ledger_status = "PASS"
        elif avg_ok and pf_ok and (fold_ok or month_ok):
            status = "TIME_OOS_WATCHLIST"
            ledger_status = "WATCHLIST"
        else:
            status = "TIME_OOS_FAIL"
            ledger_status = "REJECT"

    target_type = "ACTIVE_FAMILY" if target in ACTIVE_FAMILIES else "RESEARCH_CANDIDATE"
    target_dir = out_dir / "targets" / target
    target_dir.mkdir(parents=True, exist_ok=True)
    evidence_json = target_dir / f"rolling_time_oos_{stamp}.json"
    evidence_csv = target_dir / f"rolling_time_oos_folds_{stamp}.csv"

    result = TargetTimeOOSResult(
        target_key=target,
        target_type=target_type,
        source_path=schema.source_path,
        split_mode=actual_split_mode,
        total_rows_raw=raw_rows,
        rows_after_ready_universe_filter=raw_rows - non_ready_drop,
        rows_after_cleaning=int(full["rows"]),
        dropped_non_ready_symbol_rows=non_ready_drop,
        dropped_bad_pnl_rows=0,
        fold_count=len(fold_results),
        valid_fold_count=len(valid_folds),
        positive_test_fold_rate=round(positive_fold_rate, 6),
        monthly_positive_rate=round(monthly_positive_rate, 6),
        total_pnl=round(full["total"], 8),
        avg_pnl=round(full["avg"], 8),
        full_pf=round(full["pf"], 8),
        full_wr=round(full["wr"], 6),
        full_symbol_count=int(full["symbols"]),
        test_total_sum=round(test_total_sum, 8),
        test_avg_mean=round(test_avg_mean, 8),
        test_pf_aggregate=round(test_pf_agg, 8),
        worst_test_fold=round(worst_test, 8),
        max_test_drawdown_proxy=round(dd_proxy, 8),
        validation_status=status,
        ledger_result_status=ledger_status,
        reasons=reasons,
        warnings=warnings,
        evidence_json=str(evidence_json),
        evidence_csv=str(evidence_csv),
        ledger_task_id=f"rolling_time_oos_{target}",
        live_allowed=False,
        promotes_or_trades=False,
    )
    write_json(evidence_json, {"result": asdict(result), "folds": [asdict(f) for f in fold_results], "schema": asdict(schema)})
    pd.DataFrame([asdict(f) for f in fold_results]).to_csv(evidence_csv, index=False)
    return result, fold_results


def append_ledger(workspace: Path, result: TargetTimeOOSResult) -> Optional[str]:
    try:
        root = workspace / "edge_factory_research_result_ledger"
        ledger = root / "master_research_result_ledger.jsonl"
        raw = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "task_id": result.ledger_task_id,
            "result_status": result.ledger_result_status,
            "score": result.positive_test_fold_rate,
            "summary": f"{result.target_key}: {result.validation_status}, clean_rows={result.rows_after_cleaning}, positive_folds={result.positive_test_fold_rate}, test_total={result.test_total_sum}, test_pf={result.test_pf_aggregate}",
            "evidence_path": result.evidence_json,
            "family": result.target_key if result.target_type == "ACTIVE_FAMILY" else None,
            "candidate": result.target_key if result.target_type == "RESEARCH_CANDIDATE" else None,
            "tags": ["rolling_time_oos", "offline", "no_promotion"],
            "reviewer": "rolling_retrain_validator_v1",
            "source": "edge_factory_rolling_retrain_validator_v1",
            "safe_for_auto_promotion": False,
            "live_allowed": False,
            "notes": "Evidence-only time-OOS validation. No promotion or config mutation.",
        }
        result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"
        row = {"result_id": result_id, **raw}
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        # refresh CSV best effort
        rows = []
        with ledger.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        pd.DataFrame(rows).to_csv(root / "master_research_result_ledger.csv", index=False)
        return result_id
    except Exception:
        return None


def results_df(results: List[TargetTimeOOSResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        d = asdict(r)
        d["reasons"] = " | ".join(r.reasons)
        d["warnings"] = " | ".join(r.warnings)
        rows.append(d)
    return pd.DataFrame(rows)


def folds_df(folds: List[FoldResult]) -> pd.DataFrame:
    return pd.DataFrame([asdict(f) for f in folds])


def write_report(path: Path, state: ValidatorState, results: List[TargetTimeOOSResult]) -> None:
    lines = [
        "# Edge Factory Rolling Retrain / Time-OOS Validator Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall verdict: **{state.overall_verdict}**",
        f"Source: `{state.source_path}`",
        f"Ready universe: `{state.ready_universe_path}`",
        f"Split mode: **{state.split_mode}**",
        f"Targets validated: **{state.targets_validated}**",
        f"Pass/watchlist/fail/needs/inconclusive: **{state.pass_count}/{state.watchlist_count}/{state.fail_count}/{state.needs_more_data_count}/{state.inconclusive_count}**",
        f"Ledger records appended: **{state.ledger_records_appended}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Reasons",
        "",
    ]
    for r in state.reasons:
        lines.append(f"- {r}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Results", ""]
    if results:
        lines += ["| Target | Type | Status | Clean rows | Folds | Pos fold rate | Month pos | Test total | Test PF | Worst fold | Symbols |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in results:
            lines.append(f"| {r.target_key} | {r.target_type} | {r.validation_status} | {r.rows_after_cleaning} | {r.valid_fold_count} | {r.positive_test_fold_rate} | {r.monthly_positive_rate} | {r.test_total_sum} | {r.test_pf_aggregate} | {r.worst_test_fold} | {r.full_symbol_count} |")
    else:
        lines.append("No targets validated.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "This validator is a time stability gate. PASS/WATCHLIST is still evidence only and cannot promote a family or candidate. Failed targets should be demoted in future lifecycle review, not automatically traded.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory rolling retrain / time-OOS validator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--source", default=None)
    p.add_argument("--target", default=None)
    p.add_argument("--active_only", action="store_true")
    p.add_argument("--candidates_only", action="store_true")
    p.add_argument("--include_optional_candidates", action="store_true")
    p.add_argument("--split_mode", choices=["auto", "time", "row_order"], default="auto")
    p.add_argument("--folds", type=int, default=8)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--no_ready_universe_filter", action="store_true")
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_rolling_retrain_validator"
    out_dir = out_root / f"rolling_time_oos_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    schema = load_schema(workspace, args.source)
    ready_path = latest_ready_universe(workspace)
    ready_symbols, ready_warnings = load_ready_symbols(ready_path)
    source_df = pd.read_csv(schema.source_path)
    targets = discover_targets(workspace, args.target, bool(args.active_only), bool(args.candidates_only), bool(args.include_optional_candidates))

    warnings = list(schema.warnings) + ready_warnings
    results: List[TargetTimeOOSResult] = []
    folds_all: List[FoldResult] = []
    ledger_count = 0

    for target in targets:
        result, folds = validate_target(
            target=target,
            df=source_df,
            schema=schema,
            ready_symbols=ready_symbols,
            use_ready_filter=not bool(args.no_ready_universe_filter),
            split_mode=str(args.split_mode),
            folds=int(args.folds),
            stamp=stamp,
            out_dir=out_dir,
            workspace=workspace,
        )
        results.append(result)
        folds_all.extend(folds)
        if not args.no_ledger_append:
            rid = append_ledger(workspace, result)
            if rid:
                ledger_count += 1
            else:
                warnings.append(f"ledger append failed for {target}")

    pass_count = len([r for r in results if r.validation_status == "TIME_OOS_PASS"])
    watch_count = len([r for r in results if r.validation_status == "TIME_OOS_WATCHLIST"])
    fail_count = len([r for r in results if r.validation_status == "TIME_OOS_FAIL"])
    needs_count = len([r for r in results if r.validation_status == "NEEDS_MORE_DATA"])
    inc_count = len([r for r in results if r.validation_status == "INCONCLUSIVE"])

    if fail_count > 0 or inc_count > 0:
        overall = "WARN_SOME_TARGETS_FAILED_OR_INCONCLUSIVE"
    elif needs_count > 0:
        overall = "WARN_SOME_TARGETS_NEED_MORE_DATA"
    elif pass_count > 0 and watch_count == 0:
        overall = "PASS_TIME_OOS_VALIDATED"
    else:
        overall = "WATCHLIST_TIME_OOS_MIXED"

    state = ValidatorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        source_path=schema.source_path,
        ready_universe_path=str(ready_path) if ready_path else None,
        split_mode=str(args.split_mode),
        targets_seen=len(targets),
        targets_validated=len(results),
        pass_count=pass_count,
        watchlist_count=watch_count,
        fail_count=fail_count,
        needs_more_data_count=needs_count,
        inconclusive_count=inc_count,
        ledger_append_enabled=not bool(args.no_ledger_append),
        ledger_records_appended=ledger_count,
        overall_verdict=overall,
        live_allowed=False,
        reasons=[
            "Rolling/time-OOS validation ran offline using normalized trade evidence.",
            "Ready candle universe filter was applied unless disabled.",
            "Results are evidence-only and cannot promote or trade.",
        ],
        warnings=warnings,
        hard_rules=[
            "Rolling retrain validator never starts paper/live.",
            "Rolling retrain validator never mutates active config.",
            "Rolling retrain validator never promotes candidates automatically.",
            "PASS is evidence only, not promotion.",
            "Live remains blocked.",
        ],
    )

    state_path = out_dir / "rolling_time_oos_state.json"
    write_json(state_path, {"state": asdict(state), "schema": asdict(schema), "results": [asdict(r) for r in results], "folds": [asdict(f) for f in folds_all]})
    results_df(results).to_csv(out_dir / "rolling_time_oos_summary.csv", index=False)
    folds_df(folds_all).to_csv(out_dir / "rolling_time_oos_folds.csv", index=False)
    write_report(out_dir / "rolling_time_oos_report.md", state, results)

    print("EDGE FACTORY ROLLING RETRAIN / TIME-OOS VALIDATOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_verdict: {state.overall_verdict}")
    print(f"source: {state.source_path}")
    print(f"ready_universe: {state.ready_universe_path}")
    print(f"schema: family={schema.family_col} pnl={schema.pnl_col} symbol={schema.symbol_col} time={schema.time_col}")
    print(f"targets_seen={state.targets_seen} validated={state.targets_validated}")
    print(f"pass={state.pass_count} watchlist={state.watchlist_count} fail={state.fail_count} needs_more_data={state.needs_more_data_count} inconclusive={state.inconclusive_count}")
    print(f"ledger_append_enabled={state.ledger_append_enabled} ledger_records_appended={state.ledger_records_appended}")
    print("live_allowed: False")
    print("")
    print("RESULTS")
    print("-" * 100)
    for r in results:
        print(f"{r.target_key:32s} {r.target_type:18s} status={r.validation_status:22s} clean={r.rows_after_cleaning:7d} folds={r.valid_fold_count:3d} pos_fold={r.positive_test_fold_rate:.2%} month_pos={r.monthly_positive_rate:.2%} test_total={r.test_total_sum: .4f} test_pf={r.test_pf_aggregate:.3f} worst={r.worst_test_fold: .4f} symbols={r.full_symbol_count}")
        for reason in r.reasons[:3]:
            print(f"     - {reason}")
        if r.warnings:
            print(f"     warnings: {' | '.join(r.warnings[:3])}")
    if state.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'rolling_time_oos_report.md'}")
    print(f"State  : {state_path}")
    print(f"Summary: {out_dir / 'rolling_time_oos_summary.csv'}")
    print(f"Folds  : {out_dir / 'rolling_time_oos_folds.csv'}")
    return 0 if not state.overall_verdict.startswith("FAIL") else 2


if __name__ == "__main__":
    raise SystemExit(main())
