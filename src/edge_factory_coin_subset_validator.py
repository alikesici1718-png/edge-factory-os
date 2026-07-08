#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY COIN SUBSET VALIDATOR v1
=====================================

Purpose
-------
Offline coin/symbol subset robustness validator for the Edge Factory OS.

This module answers the next OS-level question:
    Does a family/candidate work across a broad enough coin subset, or is it only
    carried by one/few symbols?

It is designed mainly for ACTIVE_FAMILY_ROBUSTNESS tasks:
    - old_short
    - impulse_long
    - market_relative_short
    - weak_market_short

It can also inspect research candidates if --include_candidates is passed.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - read candidate lab manifests
    - read rolling OOS / normalized trade CSV sources
    - compute per-symbol and time-split robustness
    - detect symbol concentration / one-coin dependency
    - classify robustness as ROBUST_COIN_FIT / CONCENTRATED_BUT_POSITIVE / WEAK_COIN_FIT / NEEDS_MORE_DATA / INCONCLUSIVE
    - write evidence into each lab's results folder
    - append evidence-only results to research ledger unless --no_ledger_append is used

Run active families:
    python "C:\Users\alike\edge_factory_coin_subset_validator.py"

Run one family:
    python "C:\Users\alike\edge_factory_coin_subset_validator.py" --family old_short

Include research candidates too:
    python "C:\Users\alike\edge_factory_coin_subset_validator.py" --include_candidates

Core rule
---------
A robustness pass is NOT promotion. It only creates evidence for later sandbox/manual review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")

ACTIVE_FAMILIES = {"old_short", "impulse_long", "market_relative_short", "weak_market_short"}
RESEARCH_CANDIDATES = {
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
}

POSSIBLE_FAMILY_COLUMNS = ["family_key", "family", "strategy", "strategy_key", "candidate", "candidate_key", "label", "name"]
POSSIBLE_PNL_COLUMNS = ["net_pnl_usdt", "pnl_usdt", "pnl", "net_pnl", "gross_pnl_usdt", "profit", "ret", "return"]
POSSIBLE_SYMBOL_COLUMNS = ["symbol", "inst", "inst_id", "instrument", "coin", "ticker"]
POSSIBLE_TIME_COLUMNS = ["exit_time", "entry_time", "timestamp", "time", "open_time", "close_time", "ts", "datetime", "date"]

MIN_TRADES = 100
MIN_SYMBOLS = 5
MIN_POSITIVE_SYMBOL_RATE = 0.45
MIN_POSITIVE_SPLIT_RATE = 0.50
MAX_TOP_SYMBOL_PNL_SHARE = 0.55
MAX_TOP_SYMBOL_TRADE_SHARE = 0.45
MIN_PROFIT_FACTOR = 1.10


@dataclass
class SourceFile:
    path: str
    exists: bool
    rows: int
    columns: str
    status: str
    message: str


@dataclass
class CoinSubsetResult:
    family_key: str
    lab_dir: str
    source_path: Optional[str]
    validation_status: str
    ledger_result_status: str
    trade_count: int
    symbol_count: int
    avg_pnl: float
    total_pnl: float
    profit_factor: float
    win_rate: float
    positive_symbol_rate: float
    positive_split_rate: float
    split_count: int
    top_symbol: Optional[str]
    worst_symbol: Optional[str]
    top_symbol_trade_share: float
    top_symbol_pnl_share: float
    symbol_hhi: float
    reasons: List[str]
    warnings: List[str]
    evidence_json: str
    evidence_csv: str
    ledger_task_id: str
    promotes_or_trades: bool
    live_allowed: bool


@dataclass
class ValidatorState:
    generated_at: str
    workspace: str
    targets_seen: int
    targets_validated: int
    robust_count: int
    concentrated_count: int
    weak_count: int
    needs_more_data_count: int
    inconclusive_count: int
    ledger_append_enabled: bool
    ledger_records_appended: int
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_key(x: str) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def optional_json(path: Optional[Path]) -> Any:
    if not path or not path.exists():
        return None
    try:
        return load_json(path)
    except Exception:
        return None


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def discover_labs(workspace: Path, family: Optional[str], include_candidates: bool) -> List[Path]:
    labs_root = workspace / "edge_factory_candidate_lab" / "labs"
    if not labs_root.exists():
        return []
    labs = [p for p in labs_root.iterdir() if p.is_dir()]
    out: List[Path] = []
    wanted = safe_key(family) if family else None
    for lab in labs:
        key = safe_key(lab.name)
        if wanted and key != wanted:
            continue
        if key in ACTIVE_FAMILIES or (include_candidates and key in RESEARCH_CANDIDATES):
            out.append(lab)
    return sorted(out, key=lambda p: p.name)


def discover_trade_sources(workspace: Path) -> List[Path]:
    paths: List[Path] = []
    for root_name in ["edge_factory_rolling_oos_validator_v2", "edge_factory_rolling_oos_validator"]:
        root = workspace / root_name
        if root.exists():
            for p in root.rglob("*.csv"):
                name = p.name.lower()
                if any(tok in name for tok in ["trade", "normalized", "candidate", "oos", "summary"]):
                    paths.append(p)
    uniq = {str(p.resolve()).lower(): p for p in paths if p.exists() and p.is_file()}
    out = list(uniq.values())
    out.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return out[:100]


def read_csv(path: Path, max_rows: Optional[int]) -> Tuple[Optional[pd.DataFrame], str]:
    try:
        if max_rows and max_rows > 0:
            return pd.read_csv(path, nrows=max_rows), "OK"
        return pd.read_csv(path), "OK"
    except Exception as e:
        return None, repr(e)


def find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    return None


def source_record(path: Path, df: Optional[pd.DataFrame], status: str) -> SourceFile:
    if df is None:
        return SourceFile(str(path), path.exists(), 0, "", "ERROR", status)
    return SourceFile(str(path), path.exists(), int(len(df)), " | ".join(str(c) for c in df.columns), "OK", status)


def dataframe_for_target(target: str, sources: List[Path], max_rows: Optional[int]) -> Tuple[Optional[pd.DataFrame], Optional[Path], List[SourceFile], List[str]]:
    warnings: List[str] = []
    source_records: List[SourceFile] = []
    key = safe_key(target)
    best_df: Optional[pd.DataFrame] = None
    best_path: Optional[Path] = None
    best_score = -1

    ordered = sorted(sources, key=lambda p: (0 if key in safe_key(p.name) or key in safe_key(str(p.parent)) else 1, -p.stat().st_mtime))
    for path in ordered:
        df, status = read_csv(path, max_rows=max_rows)
        source_records.append(source_record(path, df, status))
        if df is None or df.empty:
            continue
        family_col = find_col(df, POSSIBLE_FAMILY_COLUMNS)
        filtered = None
        score = 0
        if family_col:
            mask = df[family_col].astype(str).str.lower().str.contains(key, regex=False, na=False)
            if mask.any():
                filtered = df.loc[mask].copy()
                score += 100000 + len(filtered)
        elif key in safe_key(str(path)):
            filtered = df.copy()
            score += 1000 + len(filtered)
        if filtered is not None and not filtered.empty:
            if find_col(filtered, POSSIBLE_PNL_COLUMNS):
                score += 10000
            if find_col(filtered, POSSIBLE_SYMBOL_COLUMNS):
                score += 5000
            if score > best_score:
                best_score = score
                best_df = filtered
                best_path = path

    if best_df is None:
        warnings.append("No target-specific trade rows found in discovered CSV sources.")
    return best_df, best_path, source_records, warnings


def profit_factor(pnl: pd.Series) -> float:
    gains = float(pnl[pnl > 0].sum())
    losses = float((-pnl[pnl < 0]).sum())
    if losses <= 0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def split_stats(df: pd.DataFrame, pnl_col: str, time_col: Optional[str]) -> Tuple[float, int]:
    tmp = df.copy()
    tmp["__pnl"] = pd.to_numeric(tmp[pnl_col], errors="coerce")
    tmp = tmp.dropna(subset=["__pnl"])
    if tmp.empty:
        return 0.0, 0
    if time_col and time_col in tmp.columns:
        ts = pd.to_datetime(tmp[time_col], errors="coerce", utc=True)
        tmp["__split"] = ts.dt.strftime("%Y-%m")
        if tmp["__split"].isna().all():
            tmp["__split"] = pd.qcut(range(len(tmp)), q=min(4, len(tmp)), duplicates="drop")
    else:
        tmp["__split"] = pd.qcut(range(len(tmp)), q=min(4, len(tmp)), duplicates="drop")
    g = tmp.groupby("__split", dropna=True)["__pnl"].sum()
    if g.empty:
        return 0.0, 0
    return float((g > 0).mean()), int(len(g))


def symbol_metrics(df: pd.DataFrame, pnl_col: str, symbol_col: Optional[str]) -> Tuple[float, int, Optional[str], Optional[str], float, float, float]:
    if not symbol_col or symbol_col not in df.columns:
        return 0.0, 0, None, None, 1.0, 1.0, 1.0
    tmp = df[[symbol_col, pnl_col]].copy()
    tmp["__pnl"] = pd.to_numeric(tmp[pnl_col], errors="coerce")
    tmp = tmp.dropna(subset=["__pnl"])
    if tmp.empty:
        return 0.0, 0, None, None, 1.0, 1.0, 1.0
    g_pnl = tmp.groupby(symbol_col)["__pnl"].sum().sort_values()
    g_count = tmp.groupby(symbol_col)["__pnl"].count().sort_values(ascending=False)
    symbol_count = int(len(g_pnl))
    positive_symbol_rate = float((g_pnl > 0).mean()) if symbol_count else 0.0
    best_symbol = str(g_pnl.index[-1]) if symbol_count else None
    worst_symbol = str(g_pnl.index[0]) if symbol_count else None
    top_trade_share = float(g_count.iloc[0] / max(1, g_count.sum())) if not g_count.empty else 1.0
    positive_total = float(g_pnl[g_pnl > 0].sum())
    if positive_total > 0:
        top_pnl_share = float(g_pnl.max() / positive_total)
    else:
        top_pnl_share = 1.0
    shares = g_count / max(1, g_count.sum())
    hhi = float((shares ** 2).sum()) if not shares.empty else 1.0
    return positive_symbol_rate, symbol_count, best_symbol, worst_symbol, top_trade_share, top_pnl_share, hhi


def classify(trade_count: int, symbol_count: int, avg_pnl: float, pf: float, positive_symbol_rate: float, positive_split_rate: float, top_trade_share: float, top_pnl_share: float) -> Tuple[str, str, List[str], List[str]]:
    reasons: List[str] = []
    warnings: List[str] = []

    if trade_count <= 0:
        return "INCONCLUSIVE", "INCONCLUSIVE", ["No usable trade rows found."], warnings
    if trade_count < MIN_TRADES:
        reasons.append(f"Trade count {trade_count} is below robustness threshold {MIN_TRADES}.")
        return "NEEDS_MORE_DATA", "NEEDS_MORE_DATA", reasons, warnings
    if symbol_count and symbol_count < MIN_SYMBOLS:
        reasons.append(f"Symbol count {symbol_count} is below breadth threshold {MIN_SYMBOLS}.")
        return "CONCENTRATED_BUT_POSITIVE" if avg_pnl > 0 and pf >= MIN_PROFIT_FACTOR else "WEAK_COIN_FIT", "WATCHLIST" if avg_pnl > 0 else "REJECT", reasons, warnings

    pf_ok = math.isinf(pf) or pf >= MIN_PROFIT_FACTOR
    avg_ok = avg_pnl > 0
    sym_ok = positive_symbol_rate >= MIN_POSITIVE_SYMBOL_RATE if symbol_count else False
    split_ok = positive_split_rate >= MIN_POSITIVE_SPLIT_RATE
    trade_conc_ok = top_trade_share <= MAX_TOP_SYMBOL_TRADE_SHARE if symbol_count else False
    pnl_conc_ok = top_pnl_share <= MAX_TOP_SYMBOL_PNL_SHARE if symbol_count else False

    reasons.append("Average PnL is positive." if avg_ok else "Average PnL is not positive.")
    reasons.append("Profit factor passes robustness threshold." if pf_ok else "Profit factor is below robustness threshold.")
    reasons.append("Positive symbol rate passes breadth threshold." if sym_ok else "Positive symbol rate is weak.")
    reasons.append("Positive time-split rate passes threshold." if split_ok else "Positive time-split rate is weak.")
    reasons.append("Top-symbol trade concentration is acceptable." if trade_conc_ok else "Top-symbol trade concentration is high.")
    reasons.append("Top-symbol PnL concentration is acceptable." if pnl_conc_ok else "Top-symbol PnL concentration is high.")

    if avg_ok and pf_ok and sym_ok and split_ok and trade_conc_ok and pnl_conc_ok:
        return "ROBUST_COIN_FIT", "PASS", reasons, warnings
    if avg_ok and pf_ok and sym_ok and split_ok:
        return "CONCENTRATED_BUT_POSITIVE", "WATCHLIST", reasons, warnings
    if avg_ok and pf_ok:
        return "CONCENTRATED_BUT_POSITIVE", "WATCHLIST", reasons, warnings
    return "WEAK_COIN_FIT", "REJECT", reasons, warnings


def validate_lab(lab: Path, workspace: Path, sources: List[Path], stamp: str, max_rows: Optional[int]) -> Tuple[CoinSubsetResult, List[SourceFile]]:
    key = safe_key(lab.name)
    df, source_path, src_records, warnings = dataframe_for_target(key, sources, max_rows=max_rows)
    results_dir = lab / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    evidence_json = results_dir / f"coin_subset_validation_{stamp}.json"
    evidence_csv = results_dir / f"coin_subset_validation_{stamp}.csv"

    if df is None or df.empty:
        rec = CoinSubsetResult(
            family_key=key,
            lab_dir=str(lab),
            source_path=str(source_path) if source_path else None,
            validation_status="INCONCLUSIVE",
            ledger_result_status="INCONCLUSIVE",
            trade_count=0,
            symbol_count=0,
            avg_pnl=0.0,
            total_pnl=0.0,
            profit_factor=0.0,
            win_rate=0.0,
            positive_symbol_rate=0.0,
            positive_split_rate=0.0,
            split_count=0,
            top_symbol=None,
            worst_symbol=None,
            top_symbol_trade_share=0.0,
            top_symbol_pnl_share=0.0,
            symbol_hhi=0.0,
            reasons=["No usable target-specific trade rows found."],
            warnings=warnings,
            evidence_json=str(evidence_json),
            evidence_csv=str(evidence_csv),
            ledger_task_id=f"coin_subset_robustness_{key}",
            promotes_or_trades=False,
            live_allowed=False,
        )
        write_json(evidence_json, {"validation": asdict(rec), "source_files": [asdict(s) for s in src_records]})
        pd.DataFrame([asdict(rec)]).to_csv(evidence_csv, index=False)
        return rec, src_records

    pnl_col = find_col(df, POSSIBLE_PNL_COLUMNS)
    symbol_col = find_col(df, POSSIBLE_SYMBOL_COLUMNS)
    time_col = find_col(df, POSSIBLE_TIME_COLUMNS)
    if not pnl_col:
        rec = CoinSubsetResult(
            family_key=key,
            lab_dir=str(lab),
            source_path=str(source_path) if source_path else None,
            validation_status="INCONCLUSIVE",
            ledger_result_status="INCONCLUSIVE",
            trade_count=int(len(df)),
            symbol_count=0,
            avg_pnl=0.0,
            total_pnl=0.0,
            profit_factor=0.0,
            win_rate=0.0,
            positive_symbol_rate=0.0,
            positive_split_rate=0.0,
            split_count=0,
            top_symbol=None,
            worst_symbol=None,
            top_symbol_trade_share=0.0,
            top_symbol_pnl_share=0.0,
            symbol_hhi=0.0,
            reasons=["Rows found but no numeric PnL column was detected."],
            warnings=warnings + ["missing pnl column"],
            evidence_json=str(evidence_json),
            evidence_csv=str(evidence_csv),
            ledger_task_id=f"coin_subset_robustness_{key}",
            promotes_or_trades=False,
            live_allowed=False,
        )
        write_json(evidence_json, {"validation": asdict(rec), "source_files": [asdict(s) for s in src_records]})
        pd.DataFrame([asdict(rec)]).to_csv(evidence_csv, index=False)
        return rec, src_records

    pnl = pd.to_numeric(df[pnl_col], errors="coerce").dropna()
    trade_count = int(len(pnl))
    avg_pnl = float(pnl.mean()) if trade_count else 0.0
    total_pnl = float(pnl.sum()) if trade_count else 0.0
    pf = profit_factor(pnl)
    wr = float((pnl > 0).mean()) if trade_count else 0.0
    psr, symbol_count, best, worst, top_trade_share, top_pnl_share, hhi = symbol_metrics(df, pnl_col, symbol_col)
    split_rate, split_count = split_stats(df, pnl_col, time_col)
    status, ledger_status, reasons, extra_warnings = classify(trade_count, symbol_count, avg_pnl, pf, psr, split_rate, top_trade_share, top_pnl_share)
    warnings.extend(extra_warnings)

    rec = CoinSubsetResult(
        family_key=key,
        lab_dir=str(lab),
        source_path=str(source_path) if source_path else None,
        validation_status=status,
        ledger_result_status=ledger_status,
        trade_count=trade_count,
        symbol_count=symbol_count,
        avg_pnl=round(avg_pnl, 8),
        total_pnl=round(total_pnl, 8),
        profit_factor=round(float(pf), 8) if not math.isinf(pf) else 999999.0,
        win_rate=round(wr, 6),
        positive_symbol_rate=round(psr, 6),
        positive_split_rate=round(split_rate, 6),
        split_count=split_count,
        top_symbol=best,
        worst_symbol=worst,
        top_symbol_trade_share=round(top_trade_share, 6),
        top_symbol_pnl_share=round(top_pnl_share, 6),
        symbol_hhi=round(hhi, 6),
        reasons=reasons,
        warnings=warnings,
        evidence_json=str(evidence_json),
        evidence_csv=str(evidence_csv),
        ledger_task_id=f"coin_subset_robustness_{key}",
        promotes_or_trades=False,
        live_allowed=False,
    )
    write_json(evidence_json, {"validation": asdict(rec), "source_files": [asdict(s) for s in src_records]})
    pd.DataFrame([asdict(rec)]).to_csv(evidence_csv, index=False)
    return rec, src_records


def append_research_ledger(workspace: Path, rec: CoinSubsetResult) -> str:
    root = workspace / "edge_factory_research_result_ledger"
    ledger = root / "master_research_result_ledger.jsonl"
    raw = {
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "task_id": rec.ledger_task_id,
        "result_status": rec.ledger_result_status,
        "score": rec.positive_symbol_rate,
        "summary": f"{rec.family_key}: {rec.validation_status}, trades={rec.trade_count}, symbols={rec.symbol_count}, pos_symbol_rate={rec.positive_symbol_rate}, top_trade_share={rec.top_symbol_trade_share}",
        "evidence_path": rec.evidence_json,
        "family": rec.family_key if rec.family_key in ACTIVE_FAMILIES else None,
        "candidate": rec.family_key if rec.family_key in RESEARCH_CANDIDATES else None,
        "tags": ["coin_subset", "offline", "no_promotion"],
        "reviewer": "coin_subset_validator_v1",
    }
    result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"
    row = {
        "result_id": result_id,
        **raw,
        "source": "edge_factory_coin_subset_validator_v1",
        "safe_for_auto_promotion": False,
        "live_allowed": False,
        "notes": "Evidence-only coin subset robustness validation. No promotion or config mutation.",
    }
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    try:
        rows = []
        with ledger.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        pd.DataFrame(rows).to_csv(root / "master_research_result_ledger.csv", index=False)
    except Exception:
        pass
    return result_id


def results_df(results: List[CoinSubsetResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        d = asdict(r)
        d["reasons"] = " | ".join(r.reasons)
        d["warnings"] = " | ".join(r.warnings)
        rows.append(d)
    return pd.DataFrame(rows)


def sources_df(sources: List[SourceFile]) -> pd.DataFrame:
    return pd.DataFrame([asdict(s) for s in sources])


def write_report(path: Path, state: ValidatorState, results: List[CoinSubsetResult], sources: List[SourceFile]) -> None:
    lines = [
        "# Edge Factory Coin Subset Validator Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Targets seen: **{state.targets_seen}**",
        f"Targets validated: **{state.targets_validated}**",
        f"Robust: **{state.robust_count}**",
        f"Concentrated: **{state.concentrated_count}**",
        f"Weak: **{state.weak_count}**",
        f"Needs more data: **{state.needs_more_data_count}**",
        f"Inconclusive: **{state.inconclusive_count}**",
        f"Ledger append enabled: **{state.ledger_append_enabled}**",
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
        lines += ["| Family | Status | Trades | Symbols | Pos symbol rate | Top trade share | Top PnL share | PF |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for r in results:
            lines.append(f"| {r.family_key} | {r.validation_status} | {r.trade_count} | {r.symbol_count} | {r.positive_symbol_rate} | {r.top_symbol_trade_share} | {r.top_symbol_pnl_share} | {r.profit_factor} |")
    else:
        lines.append("No targets validated.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "This module measures coin-family fit and symbol concentration. A pass is evidence only, not promotion. Weak or concentrated results should feed later lifecycle/sandbox review.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory coin subset validator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--family", default=None)
    p.add_argument("--include_candidates", action="store_true")
    p.add_argument("--out_dir", default=None)
    p.add_argument("--max_rows", type=int, default=0)
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_coin_subset_validator"
    out_dir = out_root / f"coin_subset_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    labs = discover_labs(workspace, args.family, bool(args.include_candidates))
    sources = discover_trade_sources(workspace)
    max_rows = None if int(args.max_rows) <= 0 else int(args.max_rows)

    results: List[CoinSubsetResult] = []
    source_records_all: List[SourceFile] = []
    warnings: List[str] = []
    ledger_count = 0

    for lab in labs:
        rec, src_records = validate_lab(lab, workspace, sources, stamp, max_rows=max_rows)
        results.append(rec)
        source_records_all.extend(src_records)
        if not args.no_ledger_append:
            try:
                append_research_ledger(workspace, rec)
                ledger_count += 1
            except Exception as e:
                warnings.append(f"failed ledger append for {rec.family_key}: {e}")

    if not labs:
        warnings.append("No target labs found. Run candidate_lab_builder first or check --family filter.")
    if not sources:
        warnings.append("No OOS/normalized CSV sources found.")

    robust = len([r for r in results if r.validation_status == "ROBUST_COIN_FIT"])
    concentrated = len([r for r in results if r.validation_status == "CONCENTRATED_BUT_POSITIVE"])
    weak = len([r for r in results if r.validation_status == "WEAK_COIN_FIT"])
    needs = len([r for r in results if r.validation_status == "NEEDS_MORE_DATA"])
    inconc = len([r for r in results if r.validation_status == "INCONCLUSIVE"])

    state = ValidatorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        targets_seen=len(labs),
        targets_validated=len(results),
        robust_count=robust,
        concentrated_count=concentrated,
        weak_count=weak,
        needs_more_data_count=needs,
        inconclusive_count=inconc,
        ledger_append_enabled=not bool(args.no_ledger_append),
        ledger_records_appended=ledger_count,
        live_allowed=False,
        reasons=[
            "Coin subset robustness was validated offline.",
            "Results are evidence-only and cannot promote or trade.",
        ],
        warnings=warnings,
        hard_rules=[
            "Coin subset validator never starts paper/live.",
            "Coin subset validator never mutates active config.",
            "Coin subset validator never promotes candidates automatically.",
            "ROBUST_COIN_FIT is evidence only, not promotion.",
            "Live remains blocked.",
        ],
    )

    result_obj = {"state": asdict(state), "results": [asdict(r) for r in results], "source_files": [asdict(s) for s in source_records_all]}
    write_json(out_dir / "coin_subset_validator_state.json", result_obj)
    write_json(out_dir / "coin_subset_validation_results.json", [asdict(r) for r in results])
    results_df(results).to_csv(out_dir / "coin_subset_validation_summary.csv", index=False)
    sources_df(source_records_all).to_csv(out_dir / "coin_subset_source_files.csv", index=False)
    write_report(out_dir / "coin_subset_validator_report.md", state, results, source_records_all)

    print("EDGE FACTORY COIN SUBSET VALIDATOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"family_filter: {args.family}")
    print(f"include_candidates: {args.include_candidates}")
    print(f"targets_seen: {state.targets_seen}")
    print(f"targets_validated: {state.targets_validated}")
    print(f"robust={state.robust_count} concentrated={state.concentrated_count} weak={state.weak_count} needs_more_data={state.needs_more_data_count} inconclusive={state.inconclusive_count}")
    print(f"ledger_append_enabled={state.ledger_append_enabled} ledger_records_appended={state.ledger_records_appended}")
    print("live_allowed: False")
    print("")
    print("RESULTS")
    print("-" * 100)
    for r in results:
        print(f"{r.family_key:40s} status={r.validation_status:26s} trades={r.trade_count:7d} symbols={r.symbol_count:4d} pos_sym={r.positive_symbol_rate:.2%} top_trade={r.top_symbol_trade_share:.2%} top_pnl={r.top_symbol_pnl_share:.2%} pf={r.profit_factor:.3f}")
        print(f"     best={r.top_symbol} worst={r.worst_symbol}")
        print(f"     evidence={r.evidence_json}")
        for reason in r.reasons[:3]:
            print(f"     - {reason}")
    if warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'coin_subset_validator_report.md'}")
    print(f"State  : {out_dir / 'coin_subset_validator_state.json'}")
    print(f"Summary: {out_dir / 'coin_subset_validation_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
