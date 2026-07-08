#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY CANDLE UNIVERSE INVENTORY v1
=========================================

Purpose
-------
Inventory the OKX 1-year candle universe for the Edge Factory OS.

The OS-level question this module answers:
    What is my actual candle research universe?
    Which symbols have enough 1-year candle coverage?
    Which symbols are missing / stale / too short?
    Which symbols appear in schema-clean validator trades but not in candle inventory?
    Which candle files are real trade-level OHLCV files vs unrelated outputs?

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - run validators
    - mutate active config
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - scan workspace for CSV/parquet candle-like files
    - identify OHLCV/timestamp columns
    - infer symbol and timeframe from file path / columns
    - compute coverage days, row count, start/end timestamps
    - classify coverage quality
    - compare candle symbols to latest schema-aware validator symbols/trade symbols
    - write inventory artifacts for later rolling retrain / universe-aware validators

Run:
    python "C:\Users\alike\edge_factory_candle_universe_inventory.py"

Optional:
    python "C:\Users\alike\edge_factory_candle_universe_inventory.py" --min_days 330
    python "C:\Users\alike\edge_factory_candle_universe_inventory.py" --max_files 20000

Outputs:
    <workspace>\edge_factory_candle_universe_inventory\candle_inventory_YYYYMMDD_HHMMSS\
        candle_universe_inventory_report.md
        candle_universe_inventory_state.json
        candle_file_inventory.csv
        candle_symbol_coverage.csv
        candle_universe_ready_symbols.csv
        candle_vs_validator_symbol_gap.csv
        candle_universe_manifest.json

Core rule
---------
This is an inventory/audit module only. It produces evidence for the research OS; it never trades.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

CANDLE_HINTS = ["candle", "candles", "kline", "klines", "ohlcv", "ohlc", "bars", "bar"]
EXCLUDE_DIR_HINTS = [
    "edge_factory_os_",
    "edge_factory_research_result_ledger",
    "edge_factory_candidate_lab",
    "edge_factory_coin_subset_validator",
    "edge_factory_research_candidate_validator",
    "edge_factory_artifact_consistency_auditor",
    "edge_factory_schema_aware_validator_v2",
    "edge_factory_candle_universe_inventory",
    "paper_run_gate_",
    "live_",
    "cache",  # cache can include panels, not raw candle universe; can be included with --include_cache if needed in later versions
]

TIME_COL_CANDIDATES = [
    "timestamp", "ts", "time", "datetime", "date", "open_time", "start_time", "candle_time", "bar_time"
]
OPEN_COL_CANDIDATES = ["open", "o"]
HIGH_COL_CANDIDATES = ["high", "h"]
LOW_COL_CANDIDATES = ["low", "l"]
CLOSE_COL_CANDIDATES = ["close", "c", "close_price"]
VOLUME_COL_CANDIDATES = ["volume", "vol", "base_volume", "quote_volume", "volume_usdt"]
SYMBOL_COL_CANDIDATES = ["symbol", "inst_id", "instrument", "inst", "ticker", "coin"]

TIMEFRAME_PATTERNS = [
    r"(?i)(?:^|[_\-\\/])(1m|3m|5m|15m|30m|1h|2h|4h|6h|12h|1d)(?:$|[_\-\.\\/])",
    r"(?i)(?:^|[_\-\\/])(1min|3min|5min|15min|30min)(?:$|[_\-\.\\/])",
]

SYMBOL_PATTERNS = [
    r"([A-Z0-9]+-USDT-SWAP)",
    r"([A-Z0-9]+_USDT_SWAP)",
    r"([A-Z0-9]+USDT)",
]


@dataclass
class CandleFileRecord:
    path: str
    relative_path: str
    suffix: str
    size_bytes: int
    rows_sampled: int
    total_rows_estimate: Optional[int]
    is_candle_like: bool
    symbol: Optional[str]
    timeframe: Optional[str]
    time_col: Optional[str]
    open_col: Optional[str]
    high_col: Optional[str]
    low_col: Optional[str]
    close_col: Optional[str]
    volume_col: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    coverage_days: float
    rows_per_day: float
    quality: str
    warnings: str
    columns: str


@dataclass
class SymbolCoverageRecord:
    symbol: str
    files: int
    timeframes: str
    total_rows_estimate: int
    earliest_start: Optional[str]
    latest_end: Optional[str]
    max_coverage_days: float
    best_file: str
    quality: str
    warnings: str


@dataclass
class SymbolGapRecord:
    symbol: str
    in_candle_inventory: bool
    in_schema_validator: bool
    in_normalized_trades: bool
    candle_quality: Optional[str]
    schema_validator_rows: Optional[int]
    normalized_trade_rows: Optional[int]
    status: str
    note: str


@dataclass
class InventoryState:
    generated_at: str
    workspace: str
    files_scanned: int
    candle_like_files: int
    symbols_found: int
    ready_symbols: int
    partial_symbols: int
    weak_symbols: int
    validator_symbols_seen: int
    normalized_trade_symbols_seen: int
    candle_missing_validator_symbols: int
    overall_verdict: str
    min_days_required: float
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def should_exclude(path: Path, workspace: Path, include_cache: bool) -> bool:
    try:
        rel = str(path.relative_to(workspace)).lower()
    except Exception:
        rel = str(path).lower()
    hints = EXCLUDE_DIR_HINTS.copy()
    if include_cache:
        hints = [h for h in hints if h != "cache"]
    return any(h.lower() in rel for h in hints)


def has_candle_hint(path: Path) -> bool:
    s = str(path).lower()
    return any(h in s for h in CANDLE_HINTS)


def discover_candidate_files(workspace: Path, max_files: int, include_cache: bool) -> List[Path]:
    exts = {".csv", ".parquet", ".pq"}
    out: List[Path] = []
    for p in workspace.rglob("*"):
        if len(out) >= max_files:
            break
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if should_exclude(p, workspace, include_cache):
            continue
        if has_candle_hint(p):
            out.append(p)
            continue
        # Also include files in folders named by symbols if extension is plausible, but keep conservative.
        parent_s = str(p.parent).lower()
        if any(h in parent_s for h in CANDLE_HINTS):
            out.append(p)
    out.sort(key=lambda p: (str(p.parent), p.name))
    return out[:max_files]


def read_sample(path: Path, sample_rows: int) -> Tuple[Optional[pd.DataFrame], Optional[int], str]:
    try:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(path, nrows=sample_rows)
            # Count rows cheaply-ish for CSV only if not enormous? This is okay for inventory, but avoid full read.
            total = None
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    total = max(0, sum(1 for _ in f) - 1)
            except Exception:
                total = None
            return df, total, "OK"
        if suffix in {".parquet", ".pq"}:
            df = pd.read_parquet(path)
            total = int(len(df))
            if len(df) > sample_rows:
                df = df.head(sample_rows).copy()
            return df, total, "OK"
        return None, None, "unsupported suffix"
    except Exception as e:
        return None, None, repr(e)


def find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): str(c) for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    for col in df.columns:
        low = str(col).lower()
        if candidates == TIME_COL_CANDIDATES and any(tok in low for tok in ["time", "date", "timestamp", "datetime"]):
            return str(col)
        if candidates == SYMBOL_COL_CANDIDATES and any(tok in low for tok in ["symbol", "inst", "instrument", "ticker", "coin"]):
            return str(col)
    return None


def infer_timeframe(path: Path) -> Optional[str]:
    s = str(path)
    for pat in TIMEFRAME_PATTERNS:
        m = re.search(pat, s)
        if m:
            tf = m.group(1).lower()
            return tf.replace("min", "m")
    return None


def normalize_symbol(raw: str) -> Optional[str]:
    if not raw:
        return None
    s = str(raw).strip().upper().replace("_", "-")
    if s.endswith("-USDT-SWAP"):
        return s
    if s.endswith("USDT") and "-" not in s:
        base = s[:-4]
        return f"{base}-USDT-SWAP" if base else None
    if re.match(r"^[A-Z0-9]+-USDT$", s):
        base = s.split("-")[0]
        return f"{base}-USDT-SWAP"
    return s if re.match(r"^[A-Z0-9]+-USDT-SWAP$", s) else None


def infer_symbol(path: Path, df: Optional[pd.DataFrame], symbol_col: Optional[str]) -> Optional[str]:
    if df is not None and symbol_col and symbol_col in df.columns:
        vals = df[symbol_col].dropna().astype(str).str.strip().str.upper()
        if not vals.empty:
            common = vals.value_counts().index[0]
            norm = normalize_symbol(str(common))
            if norm:
                return norm
    s = str(path).upper().replace("_", "-")
    for pat in SYMBOL_PATTERNS:
        m = re.search(pat, s)
        if m:
            norm = normalize_symbol(m.group(1))
            if norm:
                return norm
    # fallback: parent folder may be BASE or BASE-USDT-SWAP
    for part in reversed(path.parts):
        p = str(part).upper().replace("_", "-")
        norm = normalize_symbol(p)
        if norm:
            return norm
    return None


def parse_time_series(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(dtype="datetime64[ns, UTC]")
    # Numeric timestamps: infer seconds/ms/us/ns by magnitude.
    num = pd.to_numeric(series, errors="coerce")
    if num.notna().mean() > 0.80:
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


def detect_candle_like(df: pd.DataFrame) -> Tuple[bool, Dict[str, Optional[str]], List[str]]:
    warnings: List[str] = []
    time_col = find_col(df, TIME_COL_CANDIDATES)
    open_col = find_col(df, OPEN_COL_CANDIDATES)
    high_col = find_col(df, HIGH_COL_CANDIDATES)
    low_col = find_col(df, LOW_COL_CANDIDATES)
    close_col = find_col(df, CLOSE_COL_CANDIDATES)
    volume_col = find_col(df, VOLUME_COL_CANDIDATES)
    symbol_col = find_col(df, SYMBOL_COL_CANDIDATES)

    required = [time_col, open_col, high_col, low_col, close_col]
    is_like = all(required)
    if not is_like:
        missing = []
        if not time_col: missing.append("time")
        if not open_col: missing.append("open")
        if not high_col: missing.append("high")
        if not low_col: missing.append("low")
        if not close_col: missing.append("close")
        warnings.append("missing candle columns: " + ",".join(missing))
    return is_like, {
        "time_col": time_col,
        "open_col": open_col,
        "high_col": high_col,
        "low_col": low_col,
        "close_col": close_col,
        "volume_col": volume_col,
        "symbol_col": symbol_col,
    }, warnings


def classify_quality(coverage_days: float, rows: int, min_days: float, is_candle_like: bool, symbol: Optional[str]) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    if not is_candle_like:
        return "NOT_CANDLE", ["file is not candle-like"]
    if not symbol:
        warnings.append("symbol could not be inferred")
        return "WEAK_NO_SYMBOL", warnings
    if coverage_days >= min_days:
        return "READY_1Y_COVERAGE", warnings
    if coverage_days >= min_days * 0.75:
        warnings.append("coverage is partial but close to requirement")
        return "PARTIAL_COVERAGE", warnings
    if rows > 0 and coverage_days <= 0:
        warnings.append("could not compute meaningful time coverage")
        return "UNKNOWN_COVERAGE", warnings
    warnings.append("coverage is too short")
    return "WEAK_COVERAGE", warnings


def audit_file(path: Path, workspace: Path, sample_rows: int, min_days: float) -> CandleFileRecord:
    rel = str(path.relative_to(workspace)) if str(path).lower().startswith(str(workspace).lower()) else str(path)
    size = path.stat().st_size if path.exists() else 0
    df, total_rows, status = read_sample(path, sample_rows)
    if df is None:
        return CandleFileRecord(
            path=str(path), relative_path=rel, suffix=path.suffix.lower(), size_bytes=int(size),
            rows_sampled=0, total_rows_estimate=total_rows, is_candle_like=False, symbol=None,
            timeframe=infer_timeframe(path), time_col=None, open_col=None, high_col=None, low_col=None,
            close_col=None, volume_col=None, start_time=None, end_time=None, coverage_days=0.0,
            rows_per_day=0.0, quality="READ_ERROR", warnings=status, columns=""
        )

    is_like, cols, warnings = detect_candle_like(df)
    tf = infer_timeframe(path)
    symbol = infer_symbol(path, df, cols.get("symbol_col"))
    start_s = end_s = None
    coverage_days = 0.0
    rows_per_day = 0.0
    if is_like and cols.get("time_col") and cols["time_col"] in df.columns:
        ts = parse_time_series(df[cols["time_col"]]).dropna()
        if not ts.empty:
            start = ts.min()
            end = ts.max()
            start_s = start.isoformat()
            end_s = end.isoformat()
            coverage_days = max(0.0, float((end - start).total_seconds() / 86400.0))
            row_count = int(total_rows or len(df))
            rows_per_day = float(row_count / coverage_days) if coverage_days > 0 else 0.0
        else:
            warnings.append("time column could not be parsed")
    quality, qwarn = classify_quality(coverage_days, int(total_rows or len(df)), min_days, is_like, symbol)
    warnings.extend(qwarn)

    return CandleFileRecord(
        path=str(path),
        relative_path=rel,
        suffix=path.suffix.lower(),
        size_bytes=int(size),
        rows_sampled=int(len(df)),
        total_rows_estimate=int(total_rows) if total_rows is not None else None,
        is_candle_like=bool(is_like),
        symbol=symbol,
        timeframe=tf,
        time_col=cols.get("time_col"),
        open_col=cols.get("open_col"),
        high_col=cols.get("high_col"),
        low_col=cols.get("low_col"),
        close_col=cols.get("close_col"),
        volume_col=cols.get("volume_col"),
        start_time=start_s,
        end_time=end_s,
        coverage_days=round(coverage_days, 4),
        rows_per_day=round(rows_per_day, 4),
        quality=quality,
        warnings=" | ".join(warnings),
        columns=" | ".join(str(c) for c in df.columns),
    )


def summarize_symbols(records: List[CandleFileRecord], min_days: float) -> List[SymbolCoverageRecord]:
    usable = [r for r in records if r.is_candle_like and r.symbol]
    by_symbol: Dict[str, List[CandleFileRecord]] = {}
    for r in usable:
        by_symbol.setdefault(str(r.symbol), []).append(r)
    out: List[SymbolCoverageRecord] = []
    for symbol, rows in by_symbol.items():
        rows_sorted = sorted(rows, key=lambda r: (r.coverage_days, r.total_rows_estimate or 0), reverse=True)
        best = rows_sorted[0]
        starts = [r.start_time for r in rows if r.start_time]
        ends = [r.end_time for r in rows if r.end_time]
        max_cov = max(r.coverage_days for r in rows)
        total_rows = sum(int(r.total_rows_estimate or 0) for r in rows)
        tfs = sorted(set(str(r.timeframe) for r in rows if r.timeframe))
        warnings = []
        if max_cov >= min_days:
            quality = "READY_1Y_COVERAGE"
        elif max_cov >= min_days * 0.75:
            quality = "PARTIAL_COVERAGE"
            warnings.append("best coverage is partial")
        else:
            quality = "WEAK_COVERAGE"
            warnings.append("best coverage below requirement")
        out.append(SymbolCoverageRecord(
            symbol=symbol,
            files=len(rows),
            timeframes=" | ".join(tfs),
            total_rows_estimate=int(total_rows),
            earliest_start=min(starts) if starts else None,
            latest_end=max(ends) if ends else None,
            max_coverage_days=round(max_cov, 4),
            best_file=best.path,
            quality=quality,
            warnings=" | ".join(warnings),
        ))
    out.sort(key=lambda r: (r.quality != "READY_1Y_COVERAGE", r.symbol))
    return out


def latest_schema_v2_summary(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_schema_aware_validator_v2", "schema_aware_v2_")
    if not d:
        return None
    p = d / "schema_aware_validator_v2_summary.csv"
    return p if p.exists() else None


def latest_normalized_trades(workspace: Path) -> Optional[Path]:
    paths = []
    root = workspace / "edge_factory_rolling_oos_validator"
    if root.exists():
        paths.extend(root.rglob("normalized_oos_trades.csv"))
    root2 = workspace / "edge_factory_rolling_oos_validator_v2"
    if root2.exists():
        paths.extend(root2.rglob("normalized_oos_trades.csv"))
    paths = [p for p in paths if p.exists()]
    if not paths:
        return None
    paths.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return paths[0]


def symbols_from_schema_v2(workspace: Path) -> Dict[str, int]:
    p = latest_schema_v2_summary(workspace)
    if not p:
        return {}
    try:
        df = pd.read_csv(p)
        if "top_symbol" not in df.columns and "worst_symbol" not in df.columns:
            return {}
        syms: Dict[str, int] = {}
        for col in ["top_symbol", "worst_symbol"]:
            if col in df.columns:
                for v in df[col].dropna().astype(str):
                    n = normalize_symbol(v)
                    if n:
                        syms[n] = syms.get(n, 0) + 1
        return syms
    except Exception:
        return {}


def symbols_from_normalized_trades(workspace: Path) -> Dict[str, int]:
    p = latest_normalized_trades(workspace)
    if not p:
        return {}
    try:
        # Read only symbol column if possible.
        df_head = pd.read_csv(p, nrows=5)
        sym_col = find_col(df_head, SYMBOL_COL_CANDIDATES)
        if not sym_col:
            return {}
        counts: Dict[str, int] = {}
        for chunk in pd.read_csv(p, usecols=[sym_col], chunksize=200000):
            vc = chunk[sym_col].dropna().astype(str).map(normalize_symbol).dropna().value_counts()
            for sym, cnt in vc.items():
                counts[str(sym)] = counts.get(str(sym), 0) + int(cnt)
        return counts
    except Exception:
        return {}


def build_gap(symbol_records: List[SymbolCoverageRecord], schema_symbols: Dict[str, int], trade_symbols: Dict[str, int]) -> List[SymbolGapRecord]:
    candle_map = {r.symbol: r for r in symbol_records}
    all_symbols = sorted(set(candle_map) | set(schema_symbols) | set(trade_symbols))
    out: List[SymbolGapRecord] = []
    for sym in all_symbols:
        in_candle = sym in candle_map
        in_schema = sym in schema_symbols
        in_trades = sym in trade_symbols
        quality = candle_map[sym].quality if in_candle else None
        if in_trades and not in_candle:
            status = "TRADE_SYMBOL_MISSING_CANDLE_INVENTORY"
            note = "symbol appears in normalized trades but no candle file was inventoried"
        elif in_candle and quality != "READY_1Y_COVERAGE":
            status = "CANDLE_COVERAGE_NOT_READY"
            note = "candle file exists but coverage is below requirement"
        elif in_candle and not in_trades:
            status = "CANDLE_SYMBOL_NO_VALIDATOR_TRADES"
            note = "symbol has candle coverage but did not appear in normalized trades"
        else:
            status = "OK"
            note = "symbol coverage and validator/trade evidence align"
        out.append(SymbolGapRecord(
            symbol=sym,
            in_candle_inventory=in_candle,
            in_schema_validator=in_schema,
            in_normalized_trades=in_trades,
            candle_quality=quality,
            schema_validator_rows=schema_symbols.get(sym),
            normalized_trade_rows=trade_symbols.get(sym),
            status=status,
            note=note,
        ))
    return out


def records_df(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def write_report(path: Path, state: InventoryState, symbol_records: List[SymbolCoverageRecord], gaps: List[SymbolGapRecord]) -> None:
    lines = [
        "# Edge Factory Candle Universe Inventory Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall verdict: **{state.overall_verdict}**",
        f"Files scanned: **{state.files_scanned}**",
        f"Candle-like files: **{state.candle_like_files}**",
        f"Symbols found: **{state.symbols_found}**",
        f"Ready 1Y symbols: **{state.ready_symbols}**",
        f"Partial symbols: **{state.partial_symbols}**",
        f"Weak symbols: **{state.weak_symbols}**",
        f"Validator symbols seen: **{state.validator_symbols_seen}**",
        f"Normalized trade symbols seen: **{state.normalized_trade_symbols_seen}**",
        f"Trade symbols missing candle inventory: **{state.candle_missing_validator_symbols}**",
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
    lines += ["", "## Ready symbols sample", ""]
    ready = [r for r in symbol_records if r.quality == "READY_1Y_COVERAGE"]
    if ready:
        lines += ["| Symbol | Days | Rows | Timeframes | Best file |", "|---|---:|---:|---|---|"]
        for r in ready[:50]:
            lines.append(f"| {r.symbol} | {r.max_coverage_days} | {r.total_rows_estimate} | {r.timeframes} | `{r.best_file}` |")
    else:
        lines.append("No ready symbols found.")
    lines += ["", "## Gap sample", ""]
    bad_gaps = [g for g in gaps if g.status != "OK"]
    if bad_gaps:
        lines += ["| Status | Symbol | Candle quality | Trade rows | Note |", "|---:|---|---|---:|---|"]
        for g in bad_gaps[:80]:
            lines.append(f"| {g.status} | {g.symbol} | {g.candle_quality} | {g.normalized_trade_rows} | {g.note} |")
    else:
        lines.append("No major gaps found.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "This module defines the actual candle research universe for future rolling retrain and family-fit validators. It is inventory evidence only and cannot start paper/live or promote strategies.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory candle universe inventory")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--min_days", type=float, default=330.0)
    p.add_argument("--sample_rows", type=int, default=5000)
    p.add_argument("--max_files", type=int, default=20000)
    p.add_argument("--include_cache", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_candle_universe_inventory"
    out_dir = out_root / f"candle_inventory_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = discover_candidate_files(workspace, int(args.max_files), bool(args.include_cache))
    file_records = [audit_file(p, workspace, int(args.sample_rows), float(args.min_days)) for p in files]
    symbol_records = summarize_symbols(file_records, float(args.min_days))
    schema_symbols = symbols_from_schema_v2(workspace)
    trade_symbols = symbols_from_normalized_trades(workspace)
    gaps = build_gap(symbol_records, schema_symbols, trade_symbols)

    ready = len([r for r in symbol_records if r.quality == "READY_1Y_COVERAGE"])
    partial = len([r for r in symbol_records if r.quality == "PARTIAL_COVERAGE"])
    weak = len([r for r in symbol_records if r.quality not in {"READY_1Y_COVERAGE", "PARTIAL_COVERAGE"}])
    missing_trade_symbols = len([g for g in gaps if g.status == "TRADE_SYMBOL_MISSING_CANDLE_INVENTORY"])
    warnings: List[str] = []
    reasons: List[str] = ["Candle universe inventory ran offline."]

    if ready == 0:
        verdict = "FAIL_NO_READY_CANDLE_UNIVERSE"
        warnings.append("No symbols met ready 1Y candle coverage requirement.")
    elif missing_trade_symbols > 0:
        verdict = "WARN_SYMBOL_GAPS"
        warnings.append("Some normalized-trade symbols were not found in candle inventory scan.")
    else:
        verdict = "PASS_CANDLE_UNIVERSE_INVENTORIED"
        reasons.append("Ready candle universe was inventoried successfully.")

    if not files:
        warnings.append("No candle-like files found. Check workspace layout or candle file naming.")

    state = InventoryState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        files_scanned=len(files),
        candle_like_files=len([r for r in file_records if r.is_candle_like]),
        symbols_found=len(symbol_records),
        ready_symbols=ready,
        partial_symbols=partial,
        weak_symbols=weak,
        validator_symbols_seen=len(schema_symbols),
        normalized_trade_symbols_seen=len(trade_symbols),
        candle_missing_validator_symbols=missing_trade_symbols,
        overall_verdict=verdict,
        min_days_required=float(args.min_days),
        live_allowed=False,
        reasons=reasons,
        warnings=warnings,
        hard_rules=[
            "Candle universe inventory never starts paper/live.",
            "Candle universe inventory never mutates active config.",
            "Candle universe inventory never promotes strategies.",
            "Inventory evidence must feed later rolling retrain validators, not direct trading.",
            "Live remains blocked.",
        ],
    )

    manifest = {
        "state": asdict(state),
        "ready_symbols": [asdict(r) for r in symbol_records if r.quality == "READY_1Y_COVERAGE"],
        "partial_symbols": [asdict(r) for r in symbol_records if r.quality == "PARTIAL_COVERAGE"],
        "symbol_gap_counts": pd.Series([g.status for g in gaps]).value_counts().to_dict() if gaps else {},
    }

    state_path = out_dir / "candle_universe_inventory_state.json"
    write_json(state_path, {"state": asdict(state), "manifest": manifest})
    write_json(out_dir / "candle_universe_manifest.json", manifest)
    records_df(file_records).to_csv(out_dir / "candle_file_inventory.csv", index=False)
    records_df(symbol_records).to_csv(out_dir / "candle_symbol_coverage.csv", index=False)
    records_df([r for r in symbol_records if r.quality == "READY_1Y_COVERAGE"]).to_csv(out_dir / "candle_universe_ready_symbols.csv", index=False)
    records_df(gaps).to_csv(out_dir / "candle_vs_validator_symbol_gap.csv", index=False)
    write_report(out_dir / "candle_universe_inventory_report.md", state, symbol_records, gaps)

    print("EDGE FACTORY CANDLE UNIVERSE INVENTORY v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_verdict: {state.overall_verdict}")
    print(f"files_scanned: {state.files_scanned}")
    print(f"candle_like_files: {state.candle_like_files}")
    print(f"symbols_found: {state.symbols_found}")
    print(f"ready_symbols: {state.ready_symbols}")
    print(f"partial_symbols: {state.partial_symbols}")
    print(f"weak_symbols: {state.weak_symbols}")
    print(f"validator_symbols_seen: {state.validator_symbols_seen}")
    print(f"normalized_trade_symbols_seen: {state.normalized_trade_symbols_seen}")
    print(f"trade_symbols_missing_candle_inventory: {state.candle_missing_validator_symbols}")
    print("live_allowed: False")
    print("")
    print("READY SYMBOLS SAMPLE")
    print("-" * 100)
    for r in [x for x in symbol_records if x.quality == "READY_1Y_COVERAGE"][:30]:
        print(f"{r.symbol:24s} days={r.max_coverage_days:8.2f} files={r.files:3d} rows={r.total_rows_estimate:8d} tf={r.timeframes}")
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
    print(f"Report : {out_dir / 'candle_universe_inventory_report.md'}")
    print(f"State  : {state_path}")
    print(f"Ready  : {out_dir / 'candle_universe_ready_symbols.csv'}")
    print(f"Gaps   : {out_dir / 'candle_vs_validator_symbol_gap.csv'}")
    return 0 if not state.overall_verdict.startswith("FAIL") else 2


if __name__ == "__main__":
    raise SystemExit(main())
