#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RESEARCH CANDIDATE VALIDATOR v1
============================================

Purpose
-------
Offline validator for research candidate strategy families in the Edge Factory OS.

This module validates candidates inside the isolated candidate labs created by:
    edge_factory_candidate_lab_builder.py

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
    - read latest rolling OOS v2 / normalized OOS trade artifacts when available
    - extract candidate/family trade rows best-effort
    - compute conservative validation metrics
    - classify each candidate as WATCHLIST / NEEDS_MORE_DATA / REJECT / INCONCLUSIVE
    - write results into each lab's results folder
    - optionally record memory into the research result ledger

Run all research candidates:
    python "C:\Users\alike\edge_factory_research_candidate_validator.py"

Run one candidate:
    python "C:\Users\alike\edge_factory_research_candidate_validator.py" --candidate rel_extreme_reversion_short

Do not append result ledger:
    python "C:\Users\alike\edge_factory_research_candidate_validator.py" --no_ledger_append

Outputs:
    <workspace>\edge_factory_research_candidate_validator\candidate_validate_YYYYMMDD_HHMMSS\
        research_candidate_validator_report.md
        research_candidate_validator_state.json
        candidate_validation_summary.csv
        candidate_validation_results.json
        research_ledger_reference_commands.ps1

Per lab:
    <workspace>\edge_factory_candidate_lab\labs\<candidate>\results\candidate_validation_YYYYMMDD_HHMMSS.json
    <workspace>\edge_factory_candidate_lab\labs\<candidate>\results\candidate_validation_YYYYMMDD_HHMMSS.csv

Core rule
---------
Validator output is evidence only. Promotion requires future sandbox + manual review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

RESEARCH_CANDIDATES = {
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
}

ACTIVE_FAMILIES = {"old_short", "impulse_long", "market_relative_short", "weak_market_short"}

# Candidate validator is intentionally conservative. These are not promotion thresholds;
# they only decide whether a candidate deserves more research.
MIN_TRADES_WATCHLIST = 100
MIN_TRADES_NEEDS_MORE_DATA = 30
MIN_AVG_PNL_WATCHLIST = 0.0
MIN_PF_WATCHLIST = 1.15
MIN_POSITIVE_SYMBOL_RATE = 0.40
MIN_POSITIVE_SPLIT_RATE = 0.50

POSSIBLE_FAMILY_COLUMNS = [
    "family_key", "family", "strategy", "strategy_key", "candidate", "candidate_key", "label", "name"
]
POSSIBLE_PNL_COLUMNS = [
    "net_pnl_usdt", "pnl_usdt", "pnl", "net_pnl", "gross_pnl_usdt", "profit", "ret", "return"
]
POSSIBLE_SYMBOL_COLUMNS = [
    "symbol", "inst", "inst_id", "instrument", "coin", "ticker"
]
POSSIBLE_TIME_COLUMNS = [
    "exit_time", "entry_time", "timestamp", "time", "open_time", "close_time", "ts", "datetime", "date"
]


@dataclass
class SourceFile:
    key: str
    path: str
    exists: bool
    rows: int
    columns: str
    status: str
    message: str


@dataclass
class CandidateValidation:
    candidate_key: str
    lab_dir: str
    source_path: Optional[str]
    source_quality: str
    validation_status: str
    trade_count: int
    avg_pnl: float
    total_pnl: float
    profit_factor: float
    win_rate: float
    positive_symbol_rate: float
    positive_split_rate: float
    symbol_count: int
    split_count: int
    best_symbol: Optional[str]
    worst_symbol: Optional[str]
    reasons: List[str]
    warnings: List[str]
    evidence_json: str
    evidence_csv: str
    ledger_task_id: str
    ledger_result_status: str
    promotes_or_trades: bool
    live_allowed: bool


@dataclass
class ValidatorState:
    generated_at: str
    workspace: str
    lab_root: str
    candidates_seen: int
    candidates_validated: int
    watchlist_count: int
    needs_more_data_count: int
    rejection_count: int
    inconclusive_count: int
    ledger_append_enabled: bool
    ledger_records_appended: int
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def safe_key(x: str) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


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


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def discover_labs(workspace: Path, candidate: Optional[str]) -> List[Path]:
    labs_root = workspace / "edge_factory_candidate_lab" / "labs"
    if not labs_root.exists():
        return []
    labs = [p for p in labs_root.iterdir() if p.is_dir()]
    if candidate:
        wanted = safe_key(candidate)
        labs = [p for p in labs if safe_key(p.name) == wanted]
    # Only research candidate labs for this module. Active family robustness is a separate module.
    out = []
    for lab in labs:
        manifest = optional_json(lab / "candidate_manifest.json")
        rec = manifest.get("lab_record") if isinstance(manifest, dict) and isinstance(manifest.get("lab_record"), dict) else {}
        key = safe_key(lab.name)
        if key in ACTIVE_FAMILIES:
            continue
        if rec and bool(rec.get("is_active_family", False)):
            continue
        out.append(lab)
    return sorted(out, key=lambda p: p.name)


def candidate_key_from_lab(lab: Path) -> str:
    manifest = optional_json(lab / "candidate_manifest.json")
    if isinstance(manifest, dict):
        key = manifest.get("candidate_key")
        if key:
            return safe_key(str(key))
    return safe_key(lab.name)


def discover_trade_sources(workspace: Path) -> List[Path]:
    paths: List[Path] = []

    # Most useful direct file from earlier validators.
    for root_name in ["edge_factory_rolling_oos_validator_v2", "edge_factory_rolling_oos_validator"]:
        root = workspace / root_name
        if root.exists():
            for p in root.rglob("*.csv"):
                name = p.name.lower()
                if any(tok in name for tok in ["trade", "normalized", "candidate", "oos", "summary"]):
                    paths.append(p)

    # Candidate labs may already contain results from manual experiments.
    lab_root = workspace / "edge_factory_candidate_lab" / "labs"
    if lab_root.exists():
        for p in lab_root.rglob("*.csv"):
            paths.append(p)

    # Deduplicate, prefer newest larger files.
    uniq: Dict[str, Path] = {str(p.resolve()).lower(): p for p in paths if p.exists() and p.is_file()}
    paths = list(uniq.values())
    paths.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return paths[:100]


def read_csv_light(path: Path, max_rows: Optional[int]) -> Tuple[Optional[pd.DataFrame], str]:
    try:
        if max_rows and max_rows > 0:
            return pd.read_csv(path, nrows=max_rows), "OK"
        return pd.read_csv(path), "OK"
    except Exception as e:
        return None, repr(e)


def source_file_record(key: str, path: Path, df: Optional[pd.DataFrame], status: str) -> SourceFile:
    if df is None:
        return SourceFile(key, str(path), path.exists(), 0, "", "ERROR", status)
    return SourceFile(key, str(path), path.exists(), int(len(df)), " | ".join(str(c) for c in df.columns), "OK", status)


def find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    return None


def dataframe_for_candidate(candidate: str, sources: List[Path], max_rows: Optional[int]) -> Tuple[Optional[pd.DataFrame], Optional[Path], List[SourceFile], List[str]]:
    warnings: List[str] = []
    source_records: List[SourceFile] = []
    ckey = safe_key(candidate)

    # Prefer files whose name contains candidate key.
    ordered = sorted(sources, key=lambda p: (0 if ckey in safe_key(p.name) or ckey in safe_key(str(p.parent)) else 1, -p.stat().st_mtime))

    best_df: Optional[pd.DataFrame] = None
    best_path: Optional[Path] = None
    best_score = -1

    for path in ordered:
        df, status = read_csv_light(path, max_rows=max_rows)
        source_records.append(source_file_record(path.name, path, df, status))
        if df is None or df.empty:
            continue

        family_col = find_col(df, POSSIBLE_FAMILY_COLUMNS)
        score = 0
        filtered = None

        if family_col:
            mask = df[family_col].astype(str).str.lower().str.contains(ckey, regex=False, na=False)
            if mask.any():
                filtered = df.loc[mask].copy()
                score += 100000 + len(filtered)
        else:
            # If file path itself is a candidate lab/result file, accept entire file only if it has PnL-like data.
            if ckey in safe_key(str(path)):
                filtered = df.copy()
                score += 1000 + len(filtered)

        if filtered is not None and not filtered.empty:
            pnl_col = find_col(filtered, POSSIBLE_PNL_COLUMNS)
            if pnl_col:
                score += 10000
            if score > best_score:
                best_score = score
                best_df = filtered
                best_path = path

    if best_df is None:
        warnings.append("No candidate-specific trade rows found in discovered OOS/candidate CSV sources.")
    return best_df, best_path, source_records, warnings


def numeric_series(df: pd.DataFrame, col: Optional[str]) -> pd.Series:
    if not col or col not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[col], errors="coerce").dropna()


def profit_factor(pnl: pd.Series) -> float:
    if pnl.empty:
        return 0.0
    gains = float(pnl[pnl > 0].sum())
    losses = float((-pnl[pnl < 0]).sum())
    if losses <= 0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def split_positive_rate(df: pd.DataFrame, pnl_col: str, time_col: Optional[str]) -> Tuple[float, int]:
    if df.empty or pnl_col not in df.columns:
        return 0.0, 0
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
        n = len(tmp)
        bins = min(4, max(1, n))
        tmp["__split"] = pd.qcut(range(n), q=bins, duplicates="drop")
    g = tmp.groupby("__split", dropna=True)["__pnl"].sum()
    if g.empty:
        return 0.0, 0
    return float((g > 0).mean()), int(len(g))


def symbol_stats(df: pd.DataFrame, pnl_col: str, symbol_col: Optional[str]) -> Tuple[float, int, Optional[str], Optional[str]]:
    if not symbol_col or symbol_col not in df.columns or pnl_col not in df.columns:
        return 0.0, 0, None, None
    tmp = df[[symbol_col, pnl_col]].copy()
    tmp["__pnl"] = pd.to_numeric(tmp[pnl_col], errors="coerce")
    tmp = tmp.dropna(subset=["__pnl"])
    if tmp.empty:
        return 0.0, 0, None, None
    g = tmp.groupby(symbol_col)["__pnl"].sum().sort_values()
    if g.empty:
        return 0.0, 0, None, None
    return float((g > 0).mean()), int(len(g)), str(g.index[-1]), str(g.index[0])


def classify_candidate(trade_count: int, avg_pnl: float, pf: float, win_rate: float, pos_symbol_rate: float, pos_split_rate: float, symbol_count: int, split_count: int) -> Tuple[str, str, List[str], List[str]]:
    reasons: List[str] = []
    warnings: List[str] = []

    if trade_count <= 0:
        return "INCONCLUSIVE", "INCONCLUSIVE", ["No usable candidate trade rows were found."], warnings
    if trade_count < MIN_TRADES_NEEDS_MORE_DATA:
        return "NEEDS_MORE_DATA", "NEEDS_MORE_DATA", [f"Only {trade_count} trades; below minimum sample threshold."], warnings

    if math.isinf(pf):
        pf_ok = True
    else:
        pf_ok = pf >= MIN_PF_WATCHLIST

    avg_ok = avg_pnl > MIN_AVG_PNL_WATCHLIST
    enough = trade_count >= MIN_TRADES_WATCHLIST
    sym_ok = (symbol_count == 0) or (pos_symbol_rate >= MIN_POSITIVE_SYMBOL_RATE)
    split_ok = (split_count <= 1) or (pos_split_rate >= MIN_POSITIVE_SPLIT_RATE)

    if avg_ok:
        reasons.append("Average PnL is positive.")
    else:
        reasons.append("Average PnL is not positive.")
    if pf_ok:
        reasons.append("Profit factor passes watchlist threshold.")
    else:
        reasons.append("Profit factor is below watchlist threshold.")
    if enough:
        reasons.append("Trade sample is large enough for watchlist consideration.")
    else:
        reasons.append("Trade sample is not large enough for watchlist; needs more data.")
    if sym_ok:
        reasons.append("Symbol breadth is acceptable or unavailable.")
    else:
        reasons.append("Symbol breadth is weak.")
    if split_ok:
        reasons.append("Time split stability is acceptable or unavailable.")
    else:
        reasons.append("Time split stability is weak.")

    if avg_ok and pf_ok and enough and sym_ok and split_ok:
        return "WATCHLIST", "WATCHLIST", reasons, warnings
    if avg_ok and pf_ok and not enough:
        return "NEEDS_MORE_DATA", "NEEDS_MORE_DATA", reasons, warnings
    if not avg_ok or (not pf_ok and trade_count >= MIN_TRADES_WATCHLIST):
        return "REJECT", "REJECT", reasons, warnings
    return "INCONCLUSIVE", "INCONCLUSIVE", reasons, warnings


def validate_candidate(lab: Path, workspace: Path, sources: List[Path], stamp: str, max_rows: Optional[int]) -> Tuple[CandidateValidation, List[SourceFile]]:
    key = candidate_key_from_lab(lab)
    df, source_path, source_records, warnings = dataframe_for_candidate(key, sources, max_rows=max_rows)

    results_dir = lab / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    evidence_json = results_dir / f"candidate_validation_{stamp}.json"
    evidence_csv = results_dir / f"candidate_validation_{stamp}.csv"

    if df is None or df.empty:
        validation_status = "INCONCLUSIVE"
        ledger_status = "INCONCLUSIVE"
        reasons = ["No usable candidate-specific rows found. Candidate remains untested, not rejected by evidence."]
        rec = CandidateValidation(
            candidate_key=key,
            lab_dir=str(lab),
            source_path=str(source_path) if source_path else None,
            source_quality="NO_ROWS_FOUND",
            validation_status=validation_status,
            trade_count=0,
            avg_pnl=0.0,
            total_pnl=0.0,
            profit_factor=0.0,
            win_rate=0.0,
            positive_symbol_rate=0.0,
            positive_split_rate=0.0,
            symbol_count=0,
            split_count=0,
            best_symbol=None,
            worst_symbol=None,
            reasons=reasons,
            warnings=warnings,
            evidence_json=str(evidence_json),
            evidence_csv=str(evidence_csv),
            ledger_task_id=f"validate_candidate_{key}",
            ledger_result_status=ledger_status,
            promotes_or_trades=False,
            live_allowed=False,
        )
        write_json(evidence_json, {"validation": asdict(rec), "source_records": [asdict(x) for x in source_records]})
        pd.DataFrame([asdict(rec)]).to_csv(evidence_csv, index=False)
        return rec, source_records

    pnl_col = find_col(df, POSSIBLE_PNL_COLUMNS)
    symbol_col = find_col(df, POSSIBLE_SYMBOL_COLUMNS)
    time_col = find_col(df, POSSIBLE_TIME_COLUMNS)
    pnl = numeric_series(df, pnl_col)

    if pnl.empty:
        validation_status = "INCONCLUSIVE"
        ledger_status = "INCONCLUSIVE"
        reasons = ["Candidate rows were found, but no numeric PnL column was usable."]
        warnings.append(f"PnL column missing/unusable. Detected pnl_col={pnl_col}")
        trade_count = int(len(df))
        avg_pnl = total_pnl = pf = wr = 0.0
        pos_symbol_rate = 0.0
        symbol_count = 0
        best_symbol = worst_symbol = None
        pos_split_rate = 0.0
        split_count = 0
    else:
        trade_count = int(len(pnl))
        avg_pnl = float(pnl.mean())
        total_pnl = float(pnl.sum())
        pf = profit_factor(pnl)
        wr = float((pnl > 0).mean())
        pos_symbol_rate, symbol_count, best_symbol, worst_symbol = symbol_stats(df, pnl_col, symbol_col)
        pos_split_rate, split_count = split_positive_rate(df, pnl_col, time_col)
        validation_status, ledger_status, reasons, extra_warnings = classify_candidate(
            trade_count, avg_pnl, pf, wr, pos_symbol_rate, pos_split_rate, symbol_count, split_count
        )
        warnings.extend(extra_warnings)

    source_quality = "CANDIDATE_ROWS_WITH_PNL" if pnl_col and not pnl.empty else "CANDIDATE_ROWS_NO_PNL"
    rec = CandidateValidation(
        candidate_key=key,
        lab_dir=str(lab),
        source_path=str(source_path) if source_path else None,
        source_quality=source_quality,
        validation_status=validation_status,
        trade_count=trade_count,
        avg_pnl=round(avg_pnl, 8),
        total_pnl=round(total_pnl, 8),
        profit_factor=round(float(pf), 8) if not math.isinf(pf) else 999999.0,
        win_rate=round(wr, 6),
        positive_symbol_rate=round(pos_symbol_rate, 6),
        positive_split_rate=round(pos_split_rate, 6),
        symbol_count=symbol_count,
        split_count=split_count,
        best_symbol=best_symbol,
        worst_symbol=worst_symbol,
        reasons=reasons,
        warnings=warnings,
        evidence_json=str(evidence_json),
        evidence_csv=str(evidence_csv),
        ledger_task_id=f"validate_candidate_{key}",
        ledger_result_status=ledger_status,
        promotes_or_trades=False,
        live_allowed=False,
    )
    write_json(evidence_json, {"validation": asdict(rec), "source_records": [asdict(x) for x in source_records]})
    pd.DataFrame([asdict(rec)]).to_csv(evidence_csv, index=False)
    return rec, source_records


def append_research_ledger(workspace: Path, rec: CandidateValidation, reviewer: str = "candidate_validator_v1") -> str:
    root = workspace / "edge_factory_research_result_ledger"
    ledger = root / "master_research_result_ledger.jsonl"
    result_raw = {
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "task_id": rec.ledger_task_id,
        "result_status": rec.ledger_result_status,
        "score": rec.avg_pnl,
        "summary": f"{rec.candidate_key}: {rec.validation_status}, trades={rec.trade_count}, avg={rec.avg_pnl}, pf={rec.profit_factor}",
        "evidence_path": rec.evidence_json,
        "family": None,
        "candidate": rec.candidate_key,
        "tags": ["candidate_validation", "offline", "no_promotion"],
        "reviewer": reviewer,
    }
    result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(result_raw)}"
    row = {
        "result_id": result_id,
        **result_raw,
        "source": "edge_factory_research_candidate_validator_v1",
        "safe_for_auto_promotion": False,
        "live_allowed": False,
        "notes": "Evidence-only candidate validation. No promotion or config mutation.",
    }
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    # Refresh CSV best effort.
    rows = []
    try:
        with ledger.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        pd.DataFrame(rows).to_csv(root / "master_research_result_ledger.csv", index=False)
    except Exception:
        pass
    return result_id


def validations_df(vals: List[CandidateValidation]) -> pd.DataFrame:
    rows = []
    for v in vals:
        d = asdict(v)
        d["reasons"] = " | ".join(v.reasons)
        d["warnings"] = " | ".join(v.warnings)
        rows.append(d)
    return pd.DataFrame(rows)


def sources_df(srcs: List[SourceFile]) -> pd.DataFrame:
    return pd.DataFrame([asdict(s) for s in srcs])


def write_reference_commands(path: Path, vals: List[CandidateValidation]) -> None:
    lines = [
        "# EDGE FACTORY RESEARCH LEDGER RECORD COMMANDS - REFERENCE ONLY",
        f"# Generated: {datetime.now().isoformat(timespec='seconds')}",
        "# The validator may already append to the ledger unless --no_ledger_append was used.",
        "# Commands below are comments only.",
        "",
    ]
    for v in vals:
        summary = f"{v.candidate_key}: {v.validation_status}, trades={v.trade_count}, avg={v.avg_pnl}, pf={v.profit_factor}"
        cmd = (
            f'python "C:\\Users\\alike\\edge_factory_research_result_ledger.py" '
            f'--record_result --task_id "{v.ledger_task_id}" --result_status "{v.ledger_result_status}" '
            f'--score {v.avg_pnl} --candidate "{v.candidate_key}" --tags "candidate_validation,offline,no_promotion" '
            f'--summary "{summary}" --evidence_path "{v.evidence_json}"'
        )
        lines.append(f"# {cmd}")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, state: ValidatorState, vals: List[CandidateValidation], source_files: List[SourceFile]) -> None:
    lines = [
        "# Edge Factory Research Candidate Validator Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Candidates seen: **{state.candidates_seen}**",
        f"Candidates validated: **{state.candidates_validated}**",
        f"Watchlist: **{state.watchlist_count}**",
        f"Needs more data: **{state.needs_more_data_count}**",
        f"Rejections: **{state.rejection_count}**",
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
    lines += ["", "## Candidate results", ""]
    if vals:
        lines += ["| Candidate | Status | Trades | Avg PnL | PF | WR | Pos symbols | Pos splits |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for v in vals:
            lines.append(f"| {v.candidate_key} | {v.validation_status} | {v.trade_count} | {v.avg_pnl} | {v.profit_factor} | {v.win_rate} | {v.positive_symbol_rate} | {v.positive_split_rate} |")
    else:
        lines.append("No candidates validated.")
    lines += ["", "## Source files inspected", ""]
    if source_files:
        lines += ["| Status | Rows | Path | Columns |", "|---:|---:|---|---|"]
        for s in source_files[:40]:
            lines.append(f"| {s.status} | {s.rows} | `{s.path}` | {s.columns[:200]} |")
    else:
        lines.append("No source files discovered.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "This validator produces research evidence only. WATCHLIST does not mean promotion. Any promotion discussion requires future sandbox, robustness validators, paper drift evidence, and manual review.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory research candidate validator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--max_rows", type=int, default=0, help="0 means full CSV read")
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_research_candidate_validator"
    out_dir = out_root / f"candidate_validate_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    labs = discover_labs(workspace, args.candidate)
    sources = discover_trade_sources(workspace)
    max_rows = None if int(args.max_rows) <= 0 else int(args.max_rows)

    validations: List[CandidateValidation] = []
    all_source_records: List[SourceFile] = []
    warnings: List[str] = []
    ledger_count = 0

    for lab in labs:
        rec, src_records = validate_candidate(lab, workspace, sources, stamp, max_rows=max_rows)
        validations.append(rec)
        all_source_records.extend(src_records)
        if not args.no_ledger_append:
            try:
                append_research_ledger(workspace, rec)
                ledger_count += 1
            except Exception as e:
                warnings.append(f"failed to append research ledger for {rec.candidate_key}: {e}")

    watchlist = len([v for v in validations if v.validation_status == "WATCHLIST"])
    needs = len([v for v in validations if v.validation_status == "NEEDS_MORE_DATA"])
    reject = len([v for v in validations if v.validation_status == "REJECT"])
    inconclusive = len([v for v in validations if v.validation_status == "INCONCLUSIVE"])

    if not labs:
        warnings.append("No research candidate labs found. Run edge_factory_candidate_lab_builder.py first.")
    if not sources:
        warnings.append("No OOS/candidate CSV sources found. Validator can only produce inconclusive/no-source outputs.")

    state = ValidatorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        lab_root=str(workspace / "edge_factory_candidate_lab" / "labs"),
        candidates_seen=len(labs),
        candidates_validated=len(validations),
        watchlist_count=watchlist,
        needs_more_data_count=needs,
        rejection_count=reject,
        inconclusive_count=inconclusive,
        ledger_append_enabled=not bool(args.no_ledger_append),
        ledger_records_appended=ledger_count,
        live_allowed=False,
        reasons=[
            "Research candidate labs were validated offline.",
            "Results are evidence-only and cannot promote or trade.",
        ],
        warnings=warnings,
        hard_rules=[
            "Research candidate validator never starts paper/live.",
            "Research candidate validator never mutates active config.",
            "Research candidate validator never promotes candidates automatically.",
            "WATCHLIST is not promotion; it only means more research is justified.",
            "Live remains blocked.",
        ],
    )

    result = {
        "state": asdict(state),
        "validations": [asdict(v) for v in validations],
        "source_files": [asdict(s) for s in all_source_records],
    }
    write_json(out_dir / "research_candidate_validator_state.json", result)
    write_json(out_dir / "candidate_validation_results.json", [asdict(v) for v in validations])
    validations_df(validations).to_csv(out_dir / "candidate_validation_summary.csv", index=False)
    sources_df(all_source_records).to_csv(out_dir / "candidate_validation_source_files.csv", index=False)
    write_reference_commands(out_dir / "research_ledger_reference_commands.ps1", validations)
    write_report(out_dir / "research_candidate_validator_report.md", state, validations, all_source_records)

    print("EDGE FACTORY RESEARCH CANDIDATE VALIDATOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"candidate_filter: {args.candidate}")
    print(f"candidates_seen: {state.candidates_seen}")
    print(f"candidates_validated: {state.candidates_validated}")
    print(f"watchlist={state.watchlist_count} needs_more_data={state.needs_more_data_count} reject={state.rejection_count} inconclusive={state.inconclusive_count}")
    print(f"ledger_append_enabled={state.ledger_append_enabled} ledger_records_appended={state.ledger_records_appended}")
    print("live_allowed: False")
    print("")
    print("RESULTS")
    print("-" * 100)
    for v in validations:
        print(f"{v.candidate_key:40s} status={v.validation_status:16s} trades={v.trade_count:6d} avg={v.avg_pnl: .6f} pf={v.profit_factor: .3f} wr={v.win_rate:.2%}")
        print(f"     source: {v.source_path}")
        print(f"     evidence: {v.evidence_json}")
        for r in v.reasons[:3]:
            print(f"     - {r}")
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
    print(f"Report : {out_dir / 'research_candidate_validator_report.md'}")
    print(f"State  : {out_dir / 'research_candidate_validator_state.json'}")
    print(f"Summary: {out_dir / 'candidate_validation_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
