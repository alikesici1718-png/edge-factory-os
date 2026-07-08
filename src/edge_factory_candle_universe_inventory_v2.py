#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY CANDLE UNIVERSE INVENTORY v2
=========================================

v2 fixes the v1 false negative.

v1 assumed mostly long-format OHLCV files. Your current workspace also contains wide-format
1-year feature/candle matrices like:
    time | WIF_close | PEPE_close | DOGE_close | WIF_ret1m_bps | ...

v2 supports both:
    1) long OHLCV files: time, open, high, low, close, symbol
    2) wide feature/candle files: time, BASE_close, BASE_retXm_bps, ...

It DOES NOT:
    - start paper/live
    - run loggers
    - run strategies
    - mutate active config
    - promote candidates
    - change capital
    - run --apply

Run:
    python "C:\Users\alike\edge_factory_candle_universe_inventory_v2.py"

Outputs:
    <workspace>\edge_factory_candle_universe_inventory_v2\candle_inventory_v2_YYYYMMDD_HHMMSS\
        candle_universe_inventory_v2_report.md
        candle_universe_inventory_v2_state.json
        candle_symbol_coverage_v2.csv
        candle_file_inventory_v2.csv
        candle_universe_ready_symbols_v2.csv
        candle_vs_normalized_trade_symbol_gap_v2.csv
        candle_universe_manifest_v2.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

EXCLUDE_DIR_HINTS = [
    "edge_factory_os_",
    "edge_factory_research_result_ledger",
    "edge_factory_candidate_lab",
    "edge_factory_coin_subset_validator",
    "edge_factory_research_candidate_validator",
    "edge_factory_artifact_consistency_auditor",
    "edge_factory_schema_aware_validator_v2",
    "edge_factory_candle_universe_inventory",
    "edge_factory_candle_universe_inventory_v2",
    "paper_run_gate_",
    "live_",
]

TIME_COL_CANDIDATES = ["time", "timestamp", "ts", "datetime", "date", "open_time", "close_time"]
LONG_SYMBOL_COLS = ["symbol", "inst_id", "instrument", "inst", "ticker", "coin"]
LONG_OHLCV = {
    "open": ["open", "o"],
    "high": ["high", "h"],
    "low": ["low", "l"],
    "close": ["close", "c", "close_price"],
    "volume": ["volume", "vol", "base_volume", "quote_volume", "volume_usdt"],
}

# BASE_close, BASE_open, BASE_ret1m_bps, BASE_volume, etc.
WIDE_BASE_RE = re.compile(r"^([A-Z0-9]+)_(open|high|low|close|volume|vol|ret\d+[mhd]_bps|ret\d+min_bps)$", re.I)
SYMBOL_IN_PATH_RE = re.compile(r"([A-Z0-9]+)[-_]USDT[-_]SWAP|([A-Z0-9]+)-USDT-SWAP|([A-Z0-9]+)USDT", re.I)


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


@dataclass
class FileRecordV2:
    path: str
    relative_path: str
    suffix: str
    size_bytes: int
    file_format: str
    rows: int
    time_col: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    coverage_days: float
    symbols_detected: int
    symbols: str
    ready_symbols_in_file: int
    quality: str
    warnings: str
    columns_sample: str


@dataclass
class SymbolRecordV2:
    symbol: str
    source_format: str
    files: int
    best_file: str
    has_close: bool
    has_ohlc: bool
    has_features: bool
    rows: int
    earliest_start: Optional[str]
    latest_end: Optional[str]
    max_coverage_days: float
    quality: str
    warnings: str


@dataclass
class GapRecordV2:
    symbol: str
    in_candle_inventory: bool
    in_normalized_trades: bool
    candle_quality: Optional[str]
    normalized_trade_rows: Optional[int]
    status: str
    note: str


@dataclass
class StateV2:
    generated_at: str
    workspace: str
    files_scanned: int
    usable_files: int
    symbols_found: int
    ready_symbols: int
    feature_only_symbols: int
    partial_symbols: int
    weak_symbols: int
    normalized_trade_symbols_seen: int
    trade_symbols_missing_candle_inventory: int
    min_days_required: float
    overall_verdict: str
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def normalize_symbol(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    s = str(raw).strip().upper().replace("_", "-")
    if not s or s in {"NAN", "NONE", "NULL", "UNKNOWN", "TRUE", "FALSE"}:
        return None
    # Already OKX swap.
    if re.match(r"^[A-Z0-9]+-USDT-SWAP$", s):
        return s
    # BASE-USDT.
    if re.match(r"^[A-Z0-9]+-USDT$", s):
        return f"{s.split('-')[0]}-USDT-SWAP"
    # BASEUSDT.
    if re.match(r"^[A-Z0-9]+USDT$", s):
        return f"{s[:-4]}-USDT-SWAP"
    # Bare base: RAVE -> RAVE-USDT-SWAP. Reject numeric junk.
    if re.match(r"^[A-Z][A-Z0-9]{1,14}$", s):
        return f"{s}-USDT-SWAP"
    return None


def should_exclude(path: Path, workspace: Path) -> bool:
    try:
        rel = str(path.relative_to(workspace)).lower()
    except Exception:
        rel = str(path).lower()
    return any(h.lower() in rel for h in EXCLUDE_DIR_HINTS)


def discover_files(workspace: Path, max_files: int, include_parquet: bool) -> List[Path]:
    exts = {".csv"}
    if include_parquet:
        exts.update({".parquet", ".pq"})
    out: List[Path] = []
    for p in workspace.rglob("*"):
        if len(out) >= max_files:
            break
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if should_exclude(p, workspace):
            continue
        # Keep broad discovery: candle universe may be feature files, not named candle.
        out.append(p)
    out.sort(key=lambda x: (str(x.parent), x.name))
    return out[:max_files]


def read_head(path: Path, sample_rows: int) -> Tuple[Optional[pd.DataFrame], Optional[int], str]:
    try:
        if path.suffix.lower() == ".csv":
            head = pd.read_csv(path, nrows=sample_rows)
            rows = None
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    rows = max(0, sum(1 for _ in f) - 1)
            except Exception:
                pass
            return head, rows, "OK"
        df = pd.read_parquet(path)
        rows = len(df)
        return df.head(sample_rows), rows, "OK"
    except Exception as e:
        return None, None, repr(e)


def find_col(df: pd.DataFrame, options: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): str(c) for c in df.columns}
    for opt in options:
        if opt.lower() in lookup:
            return lookup[opt.lower()]
    for c in df.columns:
        low = str(c).lower()
        if options == TIME_COL_CANDIDATES and any(tok in low for tok in ["time", "timestamp", "date", "datetime"]):
            return str(c)
        if options == LONG_SYMBOL_COLS and any(tok in low for tok in ["symbol", "inst", "ticker", "coin"]):
            return str(c)
    return None


def parse_times(s: pd.Series) -> pd.Series:
    if s.empty:
        return pd.Series(dtype="datetime64[ns, UTC]")
    num = pd.to_numeric(s, errors="coerce")
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
    return pd.to_datetime(s, errors="coerce", utc=True)


def full_time_bounds_csv(path: Path, time_col: str) -> Tuple[Optional[str], Optional[str], float, List[str]]:
    warnings: List[str] = []
    min_ts = None
    max_ts = None
    try:
        for chunk in pd.read_csv(path, usecols=[time_col], chunksize=250000):
            ts = parse_times(chunk[time_col]).dropna()
            if ts.empty:
                continue
            cmin = ts.min()
            cmax = ts.max()
            min_ts = cmin if min_ts is None or cmin < min_ts else min_ts
            max_ts = cmax if max_ts is None or cmax > max_ts else max_ts
    except Exception as e:
        warnings.append(f"full time scan failed: {e}")
        return None, None, 0.0, warnings
    if min_ts is None or max_ts is None:
        warnings.append("no parseable timestamps in full scan")
        return None, None, 0.0, warnings
    days = max(0.0, float((max_ts - min_ts).total_seconds() / 86400.0))
    return min_ts.isoformat(), max_ts.isoformat(), days, warnings


def full_time_bounds(path: Path, time_col: str, head: pd.DataFrame) -> Tuple[Optional[str], Optional[str], float, List[str]]:
    if path.suffix.lower() == ".csv":
        return full_time_bounds_csv(path, time_col)
    try:
        df = pd.read_parquet(path, columns=[time_col])
        ts = parse_times(df[time_col]).dropna()
        if ts.empty:
            return None, None, 0.0, ["no parseable timestamps in parquet"]
        return ts.min().isoformat(), ts.max().isoformat(), max(0.0, float((ts.max() - ts.min()).total_seconds() / 86400.0)), []
    except Exception as e:
        return None, None, 0.0, [f"parquet time scan failed: {e}"]


def wide_symbols_from_columns(columns: Sequence[str]) -> Dict[str, Dict[str, bool]]:
    out: Dict[str, Dict[str, bool]] = {}
    for col in columns:
        m = WIDE_BASE_RE.match(str(col))
        if not m:
            continue
        base = m.group(1).upper()
        kind = m.group(2).lower()
        sym = normalize_symbol(base)
        if not sym:
            continue
        rec = out.setdefault(sym, {"open": False, "high": False, "low": False, "close": False, "volume": False, "features": False})
        if kind in rec:
            rec[kind] = True
        if kind.startswith("ret"):
            rec["features"] = True
    return out


def long_symbol_from_file(path: Path, head: pd.DataFrame, symbol_col: Optional[str]) -> Optional[str]:
    if symbol_col and symbol_col in head.columns:
        vals = head[symbol_col].dropna().astype(str)
        if not vals.empty:
            return normalize_symbol(vals.value_counts().index[0])
    s = str(path).upper().replace("_", "-")
    m = SYMBOL_IN_PATH_RE.search(s)
    if m:
        for group in m.groups():
            if group:
                return normalize_symbol(group)
    return None


def detect_file(path: Path, workspace: Path, sample_rows: int, min_days: float) -> Tuple[FileRecordV2, List[SymbolRecordV2]]:
    rel = str(path.relative_to(workspace)) if str(path).lower().startswith(str(workspace).lower()) else str(path)
    size = path.stat().st_size if path.exists() else 0
    head, total_rows, status = read_head(path, sample_rows)
    if head is None or head.empty:
        fr = FileRecordV2(str(path), rel, path.suffix.lower(), int(size), "READ_ERROR", 0, None, None, None, 0.0, 0, "", 0, "READ_ERROR", status, "")
        return fr, []

    time_col = find_col(head, TIME_COL_CANDIDATES)
    warnings: List[str] = []
    start_s = end_s = None
    days = 0.0
    if time_col:
        start_s, end_s, days, w = full_time_bounds(path, time_col, head)
        warnings.extend(w)
    else:
        warnings.append("missing time column")

    open_col = find_col(head, LONG_OHLCV["open"])
    high_col = find_col(head, LONG_OHLCV["high"])
    low_col = find_col(head, LONG_OHLCV["low"])
    close_col = find_col(head, LONG_OHLCV["close"])
    vol_col = find_col(head, LONG_OHLCV["volume"])
    symbol_col = find_col(head, LONG_SYMBOL_COLS)
    wide = wide_symbols_from_columns(head.columns)

    symbol_records: List[SymbolRecordV2] = []
    rows = int(total_rows or len(head))

    if wide:
        file_format = "WIDE_FEATURE_MATRIX"
        for sym, flags in wide.items():
            has_ohlc = bool(flags.get("open") and flags.get("high") and flags.get("low") and flags.get("close"))
            has_close = bool(flags.get("close"))
            has_features = bool(flags.get("features"))
            if days >= min_days and has_close:
                q = "READY_1Y_COVERAGE"
                sw = []
            elif days >= min_days and has_features:
                q = "FEATURE_ONLY_1Y_COVERAGE"
                sw = ["symbol has 1Y feature coverage but no close column"]
            elif days >= min_days * 0.75:
                q = "PARTIAL_COVERAGE"
                sw = ["partial coverage"]
            else:
                q = "WEAK_COVERAGE"
                sw = ["coverage below requirement"]
            symbol_records.append(SymbolRecordV2(sym, file_format, 1, str(path), has_close, has_ohlc, has_features, rows, start_s, end_s, round(days, 4), q, " | ".join(sw)))
    elif time_col and close_col:
        file_format = "LONG_OHLCV"
        sym = long_symbol_from_file(path, head, symbol_col)
        if sym:
            has_ohlc = bool(open_col and high_col and low_col and close_col)
            has_close = bool(close_col)
            if days >= min_days and has_close:
                q = "READY_1Y_COVERAGE"
                sw = []
            elif days >= min_days * 0.75:
                q = "PARTIAL_COVERAGE"
                sw = ["partial coverage"]
            else:
                q = "WEAK_COVERAGE"
                sw = ["coverage below requirement"]
            symbol_records.append(SymbolRecordV2(sym, file_format, 1, str(path), has_close, has_ohlc, False, rows, start_s, end_s, round(days, 4), q, " | ".join(sw)))
        else:
            warnings.append("long OHLCV-like file but symbol could not be inferred")
    else:
        file_format = "NON_CANDLE_OR_UNSUPPORTED"
        warnings.append("not long OHLCV and no wide BASE_* columns detected")

    ready_in_file = len([r for r in symbol_records if r.quality == "READY_1Y_COVERAGE"])
    if symbol_records:
        if ready_in_file:
            quality = "USABLE"
        elif any(r.quality == "FEATURE_ONLY_1Y_COVERAGE" for r in symbol_records):
            quality = "FEATURE_ONLY"
        else:
            quality = "WEAK"
    else:
        quality = "UNUSABLE"

    fr = FileRecordV2(
        path=str(path), relative_path=rel, suffix=path.suffix.lower(), size_bytes=int(size),
        file_format=file_format, rows=rows, time_col=time_col, start_time=start_s, end_time=end_s,
        coverage_days=round(days, 4), symbols_detected=len(symbol_records),
        symbols=" | ".join(r.symbol for r in symbol_records[:30]), ready_symbols_in_file=ready_in_file,
        quality=quality, warnings=" | ".join(warnings), columns_sample=" | ".join(str(c) for c in head.columns[:80])
    )
    return fr, symbol_records


def merge_symbol_records(records: List[SymbolRecordV2]) -> List[SymbolRecordV2]:
    by: Dict[str, List[SymbolRecordV2]] = {}
    for r in records:
        by.setdefault(r.symbol, []).append(r)
    out: List[SymbolRecordV2] = []
    for sym, rows in by.items():
        rows_sorted = sorted(rows, key=lambda r: (r.quality == "READY_1Y_COVERAGE", r.max_coverage_days, r.rows), reverse=True)
        best = rows_sorted[0]
        starts = [r.earliest_start for r in rows if r.earliest_start]
        ends = [r.latest_end for r in rows if r.latest_end]
        max_days = max(r.max_coverage_days for r in rows)
        total_rows = max(r.rows for r in rows)
        has_close = any(r.has_close for r in rows)
        has_ohlc = any(r.has_ohlc for r in rows)
        has_features = any(r.has_features for r in rows)
        if any(r.quality == "READY_1Y_COVERAGE" for r in rows):
            q = "READY_1Y_COVERAGE"
            w = ""
        elif any(r.quality == "FEATURE_ONLY_1Y_COVERAGE" for r in rows):
            q = "FEATURE_ONLY_1Y_COVERAGE"
            w = "1Y feature coverage exists but close/OHLC may be missing"
        elif max_days >= 247.5:
            q = "PARTIAL_COVERAGE"
            w = "best coverage partial"
        else:
            q = "WEAK_COVERAGE"
            w = "best coverage below requirement"
        out.append(SymbolRecordV2(sym, best.source_format, len(rows), best.best_file, has_close, has_ohlc, has_features, int(total_rows), min(starts) if starts else None, max(ends) if ends else None, round(max_days, 4), q, w))
    out.sort(key=lambda r: (r.quality != "READY_1Y_COVERAGE", r.symbol))
    return out


def latest_normalized_trades(workspace: Path) -> Optional[Path]:
    paths: List[Path] = []
    for root_name in ["edge_factory_rolling_oos_validator", "edge_factory_rolling_oos_validator_v2"]:
        root = workspace / root_name
        if root.exists():
            paths.extend(root.rglob("normalized_oos_trades.csv"))
    paths = [p for p in paths if p.exists()]
    if not paths:
        return None
    paths.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return paths[0]


def normalized_trade_symbol_counts(workspace: Path) -> Dict[str, int]:
    p = latest_normalized_trades(workspace)
    if not p:
        return {}
    try:
        head = pd.read_csv(p, nrows=5)
        sym_col = find_col(head, LONG_SYMBOL_COLS)
        if not sym_col:
            return {}
        counts: Dict[str, int] = {}
        for chunk in pd.read_csv(p, usecols=[sym_col], chunksize=250000):
            syms = chunk[sym_col].map(normalize_symbol).dropna()
            vc = syms.value_counts()
            for sym, cnt in vc.items():
                counts[str(sym)] = counts.get(str(sym), 0) + int(cnt)
        return counts
    except Exception:
        return {}


def build_gap(symbols: List[SymbolRecordV2], trade_counts: Dict[str, int]) -> List[GapRecordV2]:
    cmap = {r.symbol: r for r in symbols}
    all_syms = sorted(set(cmap) | set(trade_counts))
    out: List[GapRecordV2] = []
    for sym in all_syms:
        in_candle = sym in cmap
        in_trades = sym in trade_counts
        q = cmap[sym].quality if in_candle else None
        if in_trades and not in_candle:
            status = "TRADE_SYMBOL_MISSING_CANDLE_INVENTORY"
            note = "symbol appears in normalized trades but no candle/feature file was inventoried"
        elif in_candle and q not in {"READY_1Y_COVERAGE", "FEATURE_ONLY_1Y_COVERAGE"}:
            status = "CANDLE_COVERAGE_NOT_READY"
            note = "symbol exists but coverage is below requirement"
        elif in_candle and not in_trades:
            status = "CANDLE_SYMBOL_NO_NORMALIZED_TRADES"
            note = "symbol has candle/feature coverage but did not appear in normalized trades"
        else:
            status = "OK"
            note = "symbol appears aligned"
        out.append(GapRecordV2(sym, in_candle, in_trades, q, trade_counts.get(sym), status, note))
    return out


def records_df(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def write_report(path: Path, state: StateV2, symbols: List[SymbolRecordV2], gaps: List[GapRecordV2]) -> None:
    ready = [s for s in symbols if s.quality == "READY_1Y_COVERAGE"]
    feat = [s for s in symbols if s.quality == "FEATURE_ONLY_1Y_COVERAGE"]
    bad_gaps = [g for g in gaps if g.status != "OK"]
    lines = [
        "# Edge Factory Candle Universe Inventory v2 Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall verdict: **{state.overall_verdict}**",
        f"Files scanned: **{state.files_scanned}**",
        f"Usable files: **{state.usable_files}**",
        f"Symbols found: **{state.symbols_found}**",
        f"Ready 1Y symbols: **{state.ready_symbols}**",
        f"Feature-only 1Y symbols: **{state.feature_only_symbols}**",
        f"Normalized trade symbols seen: **{state.normalized_trade_symbols_seen}**",
        f"Trade symbols missing candle inventory: **{state.trade_symbols_missing_candle_inventory}**",
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
    if ready:
        lines += ["| Symbol | Days | Rows | Format | Has OHLC | Best file |", "|---|---:|---:|---|---:|---|"]
        for r in ready[:80]:
            lines.append(f"| {r.symbol} | {r.max_coverage_days} | {r.rows} | {r.source_format} | {r.has_ohlc} | `{r.best_file}` |")
    else:
        lines.append("No ready symbols found.")
    if feat:
        lines += ["", "## Feature-only 1Y symbols sample", "", "| Symbol | Days | Rows | Best file |", "|---|---:|---:|---|"]
        for r in feat[:50]:
            lines.append(f"| {r.symbol} | {r.max_coverage_days} | {r.rows} | `{r.best_file}` |")
    lines += ["", "## Gap sample", ""]
    if bad_gaps:
        lines += ["| Status | Symbol | Candle quality | Trade rows | Note |", "|---:|---|---|---:|---|"]
        for g in bad_gaps[:100]:
            lines.append(f"| {g.status} | {g.symbol} | {g.candle_quality} | {g.normalized_trade_rows} | {g.note} |")
    else:
        lines.append("No major symbol gaps found.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "v2 supports wide candle/feature matrices and full-file time coverage scans. Use this inventory, not v1, for future rolling retrain and universe-aware validators.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory candle universe inventory v2")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--min_days", type=float, default=330.0)
    p.add_argument("--sample_rows", type=int, default=2000)
    p.add_argument("--max_files", type=int, default=30000)
    p.add_argument("--include_parquet", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_candle_universe_inventory_v2"
    out_dir = out_root / f"candle_inventory_v2_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = discover_files(workspace, int(args.max_files), bool(args.include_parquet))
    file_records: List[FileRecordV2] = []
    symbol_file_records: List[SymbolRecordV2] = []
    for p in files:
        fr, sr = detect_file(p, workspace, int(args.sample_rows), float(args.min_days))
        file_records.append(fr)
        symbol_file_records.extend(sr)

    symbol_records = merge_symbol_records(symbol_file_records)
    trade_counts = normalized_trade_symbol_counts(workspace)
    gaps = build_gap(symbol_records, trade_counts)

    ready = len([s for s in symbol_records if s.quality == "READY_1Y_COVERAGE"])
    feat = len([s for s in symbol_records if s.quality == "FEATURE_ONLY_1Y_COVERAGE"])
    partial = len([s for s in symbol_records if s.quality == "PARTIAL_COVERAGE"])
    weak = len([s for s in symbol_records if s.quality == "WEAK_COVERAGE"])
    missing_trade = len([g for g in gaps if g.status == "TRADE_SYMBOL_MISSING_CANDLE_INVENTORY"])

    warnings: List[str] = []
    reasons = ["Candle universe inventory v2 ran offline.", "v2 supports wide feature/candle matrices and long OHLCV files."]
    if ready == 0 and feat == 0:
        verdict = "FAIL_NO_READY_OR_FEATURE_1Y_UNIVERSE"
        warnings.append("No symbols reached 1Y ready or feature-only coverage.")
    elif missing_trade > 0:
        verdict = "WARN_SYMBOL_GAPS"
        warnings.append("Some normalized-trade symbols were not found in candle inventory.")
    else:
        verdict = "PASS_CANDLE_UNIVERSE_INVENTORIED_V2"
        reasons.append("Candle/feature universe coverage was inventoried successfully.")

    state = StateV2(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        files_scanned=len(files),
        usable_files=len([f for f in file_records if f.quality in {"USABLE", "FEATURE_ONLY"}]),
        symbols_found=len(symbol_records),
        ready_symbols=ready,
        feature_only_symbols=feat,
        partial_symbols=partial,
        weak_symbols=weak,
        normalized_trade_symbols_seen=len(trade_counts),
        trade_symbols_missing_candle_inventory=missing_trade,
        min_days_required=float(args.min_days),
        overall_verdict=verdict,
        live_allowed=False,
        reasons=reasons,
        warnings=warnings,
        hard_rules=[
            "Candle universe inventory v2 never starts paper/live.",
            "Candle universe inventory v2 never mutates active config.",
            "Candle universe inventory v2 never promotes strategies.",
            "Inventory evidence feeds later rolling retrain validators only.",
            "Live remains blocked.",
        ],
    )

    manifest = {
        "state": asdict(state),
        "ready_symbols": [asdict(s) for s in symbol_records if s.quality == "READY_1Y_COVERAGE"],
        "feature_only_symbols": [asdict(s) for s in symbol_records if s.quality == "FEATURE_ONLY_1Y_COVERAGE"],
        "symbol_gap_counts": pd.Series([g.status for g in gaps]).value_counts().to_dict() if gaps else {},
    }

    state_path = out_dir / "candle_universe_inventory_v2_state.json"
    write_json(state_path, {"state": asdict(state), "manifest": manifest})
    write_json(out_dir / "candle_universe_manifest_v2.json", manifest)
    records_df(file_records).to_csv(out_dir / "candle_file_inventory_v2.csv", index=False)
    records_df(symbol_records).to_csv(out_dir / "candle_symbol_coverage_v2.csv", index=False)
    records_df([s for s in symbol_records if s.quality == "READY_1Y_COVERAGE"]).to_csv(out_dir / "candle_universe_ready_symbols_v2.csv", index=False)
    records_df(gaps).to_csv(out_dir / "candle_vs_normalized_trade_symbol_gap_v2.csv", index=False)
    write_report(out_dir / "candle_universe_inventory_v2_report.md", state, symbol_records, gaps)

    print("EDGE FACTORY CANDLE UNIVERSE INVENTORY v2")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_verdict: {state.overall_verdict}")
    print(f"files_scanned: {state.files_scanned}")
    print(f"usable_files: {state.usable_files}")
    print(f"symbols_found: {state.symbols_found}")
    print(f"ready_symbols: {state.ready_symbols}")
    print(f"feature_only_symbols: {state.feature_only_symbols}")
    print(f"partial_symbols: {state.partial_symbols}")
    print(f"weak_symbols: {state.weak_symbols}")
    print(f"normalized_trade_symbols_seen: {state.normalized_trade_symbols_seen}")
    print(f"trade_symbols_missing_candle_inventory: {state.trade_symbols_missing_candle_inventory}")
    print("live_allowed: False")
    print("")
    print("READY SYMBOLS SAMPLE")
    print("-" * 100)
    for s in [x for x in symbol_records if x.quality == "READY_1Y_COVERAGE"][:30]:
        print(f"{s.symbol:24s} days={s.max_coverage_days:8.2f} rows={s.rows:8d} files={s.files:3d} fmt={s.source_format} ohlc={s.has_ohlc}")
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
    print(f"Report : {out_dir / 'candle_universe_inventory_v2_report.md'}")
    print(f"State  : {state_path}")
    print(f"Ready  : {out_dir / 'candle_universe_ready_symbols_v2.csv'}")
    print(f"Gaps   : {out_dir / 'candle_vs_normalized_trade_symbol_gap_v2.csv'}")
    return 0 if not state.overall_verdict.startswith("FAIL") else 2


if __name__ == "__main__":
    raise SystemExit(main())
