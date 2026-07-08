#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY SCHEMA-AWARE VALIDATOR v2
======================================

Purpose
-------
Replace provisional candidate/coin-subset results with schema-aware validation.

Why v2 exists
-------------
Artifact audit found previous validator outputs contained impossible symbol values like:
    TRUE, UNKNOWN, -800, -1000
That means previous validator results must be treated as provisional until a validator uses
the audited source CSV and audited column mapping.

This validator uses ONLY a real trade-level source, preferably:
    edge_factory_rolling_oos_validator\rolling_oos_*\normalized_oos_trades.csv

It DOES NOT use summary/metric CSVs as trade rows.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - read latest artifact consistency audit recommendations when available
    - load the audited trade source and explicit columns
    - validate active families and research candidates from candidate labs
    - reject/flag rows with bad symbol values
    - compute schema-clean symbol breadth, concentration, PF, WR, and split stability
    - write v2 evidence
    - append evidence-only records to research ledger unless --no_ledger_append is used

Run all labs:
    python "C:\Users\alike\edge_factory_schema_aware_validator_v2.py"

Run one target:
    python "C:\Users\alike\edge_factory_schema_aware_validator_v2.py" --target ret60_reversal_short

Active only:
    python "C:\Users\alike\edge_factory_schema_aware_validator_v2.py" --active_only

Candidates only:
    python "C:\Users\alike\edge_factory_schema_aware_validator_v2.py" --candidates_only

Core rule
---------
A v2 pass is evidence only. It is not promotion and cannot alter active system config.
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
RESEARCH_CANDIDATES = {
    "rel_extreme_reversion_short",
    "ret60_reversal_short",
    "relative_weakness_snapback_long",
    "market_panic_rebound_long",
    "capitulation_reversal_long",
}

BAD_SYMBOL_VALUES = {"true", "false", "unknown", "none", "nan", "null", "yes", "no", ""}

# These thresholds are intentionally conservative. They are not promotion thresholds.
MIN_TRADES_ROBUST = 100
MIN_SYMBOLS_ROBUST = 5
MIN_POS_SYMBOL_RATE = 0.45
MIN_POS_SPLIT_RATE = 0.50
MAX_TOP_TRADE_SHARE = 0.45
MAX_TOP_PNL_SHARE = 0.60
MIN_PF = 1.10


@dataclass
class SchemaConfig:
    source_path: str
    family_col: str
    pnl_col: str
    symbol_col: str
    time_col: Optional[str]
    source: str
    warnings: List[str]


@dataclass
class TargetValidationV2:
    target_key: str
    target_type: str
    lab_dir: str
    source_path: str
    schema_source: str
    validation_status: str
    ledger_result_status: str
    raw_rows: int
    clean_rows: int
    dropped_bad_symbol_rows: int
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
    bad_symbol_examples: str
    reasons: List[str]
    warnings: List[str]
    evidence_json: str
    evidence_csv: str
    ledger_task_id: str
    promotes_or_trades: bool
    live_allowed: bool


@dataclass
class ValidatorStateV2:
    generated_at: str
    workspace: str
    schema_source: str
    trade_source: str
    family_col: str
    pnl_col: str
    symbol_col: str
    time_col: Optional[str]
    targets_seen: int
    targets_validated: int
    robust_count: int
    concentrated_count: int
    weak_count: int
    needs_more_data_count: int
    inconclusive_count: int
    schema_warning_count: int
    ledger_append_enabled: bool
    ledger_records_appended: int
    overall_verdict: str
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


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def discover_latest_schema_recommendations(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_artifact_consistency_auditor", "artifact_audit_")
    if not d:
        return None
    p = d / "schema_recommendations.json"
    return p if p.exists() else None


def discover_normalized_trades(workspace: Path) -> Optional[Path]:
    candidates: List[Path] = []
    root = workspace / "edge_factory_rolling_oos_validator"
    if root.exists():
        candidates.extend(root.rglob("normalized_oos_trades.csv"))
    root2 = workspace / "edge_factory_rolling_oos_validator_v2"
    if root2.exists():
        candidates.extend(root2.rglob("normalized_oos_trades.csv"))
    candidates = [p for p in candidates if p.exists() and p.is_file()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return candidates[0]


def infer_columns(df: pd.DataFrame) -> Tuple[str, str, str, Optional[str], List[str]]:
    warnings: List[str] = []
    lower = {str(c).lower(): str(c) for c in df.columns}

    def pick(options: List[str], required: bool = True) -> Optional[str]:
        for o in options:
            if o.lower() in lower:
                return lower[o.lower()]
        if required:
            warnings.append(f"missing required column among {options}")
        return None

    family_col = pick(["family_key", "family", "strategy", "strategy_key", "candidate_key", "candidate"])
    pnl_col = pick(["pnl", "net_pnl_usdt", "pnl_usdt", "net_pnl", "gross_pnl_usdt"])
    symbol_col = pick(["symbol", "inst_id", "instrument", "inst", "ticker", "coin"])
    time_col = pick(["exit_time", "entry_time", "timestamp", "time", "date", "datetime"], required=False)

    if not family_col or not pnl_col or not symbol_col:
        raise ValueError(f"Cannot infer required schema. family={family_col}, pnl={pnl_col}, symbol={symbol_col}, warnings={warnings}")
    return family_col, pnl_col, symbol_col, time_col, warnings


def load_schema_config(workspace: Path, explicit_source: Optional[str]) -> SchemaConfig:
    warnings: List[str] = []
    rec_path = discover_latest_schema_recommendations(workspace)
    rec = optional_json(rec_path) if rec_path else None

    source_path: Optional[Path] = Path(explicit_source) if explicit_source else None
    family_col = pnl_col = symbol_col = time_col = None
    schema_source = "inferred_from_trade_source"

    if isinstance(rec, dict):
        rec_source = rec.get("recommended_source_path")
        cols = rec.get("recommended_columns") if isinstance(rec.get("recommended_columns"), dict) else {}
        if not source_path and rec_source:
            source_path = Path(str(rec_source))
        family_col = cols.get("family_col")
        pnl_col = cols.get("pnl_col")
        symbol_col = cols.get("symbol_col")
        time_col = cols.get("time_col")
        schema_source = str(rec_path)

    if source_path is None or not source_path.exists():
        source_path = discover_normalized_trades(workspace)
        if source_path is None:
            raise FileNotFoundError("No normalized_oos_trades.csv found. Run rolling OOS validator first.")
        warnings.append("Schema recommendations missing or source invalid; using latest normalized_oos_trades.csv.")

    # Validate that source is actually a trade-level normalized file, not a summary.
    if "normalized_oos_trades" not in source_path.name.lower():
        warnings.append(f"Recommended source is not named normalized_oos_trades.csv: {source_path}")

    sample = pd.read_csv(source_path, nrows=5000)
    if not family_col or not pnl_col or not symbol_col:
        family_col, pnl_col, symbol_col, time_col2, w = infer_columns(sample)
        if not time_col:
            time_col = time_col2
        warnings.extend(w)
    else:
        for col_name, col in [("family_col", family_col), ("pnl_col", pnl_col), ("symbol_col", symbol_col)]:
            if col not in sample.columns:
                warnings.append(f"recommended {col_name}={col} not in source; falling back to inference")
                family_col, pnl_col, symbol_col, time_col2, w = infer_columns(sample)
                if not time_col:
                    time_col = time_col2
                warnings.extend(w)
                break

    # Guardrail: time_col must not accidentally be the symbol column.
    # Artifact auditor v1 may recommend time_col=symbol due a fuzzy fallback bug.
    if time_col and str(time_col).lower() == str(symbol_col).lower():
        warnings.append(f"invalid time_col={time_col}; same as symbol_col, forcing time_col=None")
        time_col = None

    # Guardrail: require time_col to look date/time-like by name.
    if time_col:
        low_time = str(time_col).lower()
        if not any(tok in low_time for tok in ["time", "date", "ts", "datetime"]):
            warnings.append(f"invalid time_col={time_col}; does not look like a time/date column, forcing time_col=None")
            time_col = None

    return SchemaConfig(
        source_path=str(source_path),
        family_col=str(family_col),
        pnl_col=str(pnl_col),
        symbol_col=str(symbol_col),
        time_col=str(time_col) if time_col else None,
        source=schema_source,
        warnings=warnings,
    )


def discover_labs(workspace: Path, target: Optional[str], active_only: bool, candidates_only: bool) -> List[Path]:
    root = workspace / "edge_factory_candidate_lab" / "labs"
    if not root.exists():
        return []
    labs = [p for p in root.iterdir() if p.is_dir()]
    out: List[Path] = []
    wanted = safe_key(target) if target else None
    for lab in labs:
        key = safe_key(lab.name)
        if wanted and key != wanted:
            continue
        is_active = key in ACTIVE_FAMILIES
        is_candidate = key in RESEARCH_CANDIDATES
        if active_only and not is_active:
            continue
        if candidates_only and not is_candidate:
            continue
        if is_active or is_candidate:
            out.append(lab)
    return sorted(out, key=lambda p: (0 if safe_key(p.name) in ACTIVE_FAMILIES else 1, p.name))


def looks_like_symbol(x: Any) -> bool:
    s = str(x).strip().upper()
    if s.lower() in BAD_SYMBOL_VALUES:
        return False
    if not s:
        return False
    try:
        float(s)
        return False
    except Exception:
        pass
    if len(s) > 25:
        return False
    return bool(re.match(r"^[A-Z0-9][A-Z0-9_\-\/]{0,24}$", s))


def clean_target_df(df: pd.DataFrame, cfg: SchemaConfig, target: str) -> Tuple[pd.DataFrame, int, str, List[str]]:
    warnings: List[str] = []
    key = safe_key(target)
    fam = df[cfg.family_col].astype(str).str.lower().str.strip()
    # Exact match first; fallback contains only if exact empty.
    mask = fam == key
    if not mask.any():
        mask = fam.str.contains(key, regex=False, na=False)
        if mask.any():
            warnings.append("used contains-match for family_key because exact match found no rows")
    tdf = df.loc[mask].copy()
    raw_rows = int(len(tdf))
    if tdf.empty:
        return tdf, 0, "", warnings
    tdf["__symbol_raw"] = tdf[cfg.symbol_col].astype(str).str.strip().str.upper()
    bad_mask = ~tdf["__symbol_raw"].apply(looks_like_symbol)
    bad_vals = tdf.loc[bad_mask, "__symbol_raw"].head(20).astype(str).tolist()
    bad_examples = " | ".join(sorted({str(x) for x in bad_vals}))
    dropped = int(bad_mask.sum())
    if dropped:
        warnings.append(f"dropped {dropped} rows with invalid symbol values")
    tdf = tdf.loc[~bad_mask].copy()
    tdf["__pnl"] = pd.to_numeric(tdf[cfg.pnl_col], errors="coerce")
    pnl_bad = int(tdf["__pnl"].isna().sum())
    if pnl_bad:
        warnings.append(f"dropped {pnl_bad} rows with non-numeric pnl")
    tdf = tdf.dropna(subset=["__pnl"])
    return tdf, dropped, bad_examples, warnings


def profit_factor(pnl: pd.Series) -> float:
    gains = float(pnl[pnl > 0].sum())
    losses = float((-pnl[pnl < 0]).sum())
    if losses <= 0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def split_rate(tdf: pd.DataFrame, cfg: SchemaConfig) -> Tuple[float, int]:
    if tdf.empty:
        return 0.0, 0
    tmp = tdf.copy()
    if cfg.time_col and cfg.time_col in tmp.columns:
        ts = pd.to_datetime(tmp[cfg.time_col], errors="coerce", utc=True)
        tmp["__split"] = ts.dt.strftime("%Y-%m")
        if tmp["__split"].isna().all():
            tmp["__split"] = pd.qcut(range(len(tmp)), q=min(4, max(1, len(tmp))), duplicates="drop")
    else:
        tmp["__split"] = pd.qcut(range(len(tmp)), q=min(4, max(1, len(tmp))), duplicates="drop")
    g = tmp.groupby("__split", dropna=True)["__pnl"].sum()
    if g.empty:
        return 0.0, 0
    return float((g > 0).mean()), int(len(g))


def symbol_metrics(tdf: pd.DataFrame) -> Tuple[float, int, Optional[str], Optional[str], float, float, float]:
    if tdf.empty:
        return 0.0, 0, None, None, 1.0, 1.0, 1.0
    g_pnl = tdf.groupby("__symbol_raw")["__pnl"].sum().sort_values()
    g_count = tdf.groupby("__symbol_raw")["__pnl"].count().sort_values(ascending=False)
    if g_pnl.empty:
        return 0.0, 0, None, None, 1.0, 1.0, 1.0
    symbol_count = int(len(g_pnl))
    pos_symbol_rate = float((g_pnl > 0).mean())
    best_symbol = str(g_pnl.index[-1])
    worst_symbol = str(g_pnl.index[0])
    top_trade_share = float(g_count.iloc[0] / max(1, g_count.sum())) if not g_count.empty else 1.0
    positive_total = float(g_pnl[g_pnl > 0].sum())
    top_pnl_share = float(g_pnl.max() / positive_total) if positive_total > 0 else 1.0
    shares = g_count / max(1, g_count.sum())
    hhi = float((shares ** 2).sum()) if not shares.empty else 1.0
    return pos_symbol_rate, symbol_count, best_symbol, worst_symbol, top_trade_share, top_pnl_share, hhi


def classify_target(trade_count: int, symbol_count: int, avg_pnl: float, pf: float, win_rate: float, pos_symbol_rate: float, pos_split_rate: float, top_trade_share: float, top_pnl_share: float) -> Tuple[str, str, List[str], List[str]]:
    reasons: List[str] = []
    warnings: List[str] = []
    if trade_count <= 0:
        return "INCONCLUSIVE", "INCONCLUSIVE", ["No clean trade rows after schema-aware filtering."], warnings
    if trade_count < MIN_TRADES_ROBUST:
        reasons.append(f"Clean trade count {trade_count} below threshold {MIN_TRADES_ROBUST}.")
        return "NEEDS_MORE_DATA", "NEEDS_MORE_DATA", reasons, warnings
    if symbol_count < MIN_SYMBOLS_ROBUST:
        reasons.append(f"Clean symbol count {symbol_count} below threshold {MIN_SYMBOLS_ROBUST}.")
        if avg_pnl > 0 and (math.isinf(pf) or pf >= MIN_PF):
            return "CONCENTRATED_BUT_POSITIVE", "WATCHLIST", reasons, warnings
        return "WEAK_COIN_FIT", "REJECT", reasons, warnings

    avg_ok = avg_pnl > 0
    pf_ok = math.isinf(pf) or pf >= MIN_PF
    sym_ok = pos_symbol_rate >= MIN_POS_SYMBOL_RATE
    split_ok = pos_split_rate >= MIN_POS_SPLIT_RATE
    trade_conc_ok = top_trade_share <= MAX_TOP_TRADE_SHARE
    pnl_conc_ok = top_pnl_share <= MAX_TOP_PNL_SHARE

    reasons.append("Average PnL positive." if avg_ok else "Average PnL not positive.")
    reasons.append("Profit factor passes threshold." if pf_ok else "Profit factor below threshold.")
    reasons.append("Positive symbol rate passes threshold." if sym_ok else "Positive symbol rate weak.")
    reasons.append("Positive split rate passes threshold." if split_ok else "Positive split rate weak.")
    reasons.append("Top trade share acceptable." if trade_conc_ok else "Top trade share concentrated.")
    reasons.append("Top PnL share acceptable." if pnl_conc_ok else "Top PnL share concentrated.")

    if avg_ok and pf_ok and sym_ok and split_ok and trade_conc_ok and pnl_conc_ok:
        return "ROBUST_COIN_FIT_SCHEMA_CLEAN", "PASS", reasons, warnings
    if avg_ok and pf_ok and sym_ok and split_ok:
        return "CONCENTRATED_BUT_POSITIVE_SCHEMA_CLEAN", "WATCHLIST", reasons, warnings
    if avg_ok and pf_ok:
        return "CONCENTRATED_BUT_POSITIVE_SCHEMA_CLEAN", "WATCHLIST", reasons, warnings
    return "WEAK_COIN_FIT_SCHEMA_CLEAN", "REJECT", reasons, warnings


def validate_target(lab: Path, df: pd.DataFrame, cfg: SchemaConfig, stamp: str) -> TargetValidationV2:
    target = safe_key(lab.name)
    target_type = "ACTIVE_FAMILY" if target in ACTIVE_FAMILIES else "RESEARCH_CANDIDATE"
    results_dir = lab / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    evidence_json = results_dir / f"schema_aware_validation_v2_{stamp}.json"
    evidence_csv = results_dir / f"schema_aware_validation_v2_{stamp}.csv"

    raw_target_rows = int((df[cfg.family_col].astype(str).str.lower().str.strip() == target).sum())
    tdf, dropped_bad, bad_examples, warnings = clean_target_df(df, cfg, target)
    pnl = tdf["__pnl"] if "__pnl" in tdf.columns else pd.Series(dtype=float)
    trade_count = int(len(pnl))
    avg_pnl = float(pnl.mean()) if trade_count else 0.0
    total_pnl = float(pnl.sum()) if trade_count else 0.0
    pf = profit_factor(pnl) if trade_count else 0.0
    wr = float((pnl > 0).mean()) if trade_count else 0.0
    psr, symbol_count, best, worst, top_trade, top_pnl, hhi = symbol_metrics(tdf)
    psplit, split_count = split_rate(tdf, cfg)
    status, ledger_status, reasons, w2 = classify_target(trade_count, symbol_count, avg_pnl, pf, wr, psr, psplit, top_trade, top_pnl)
    warnings.extend(w2)

    if math.isinf(pf):
        pf_out = 999999.0
        warnings.append("profit factor is infinite because no clean losing PnL rows were found")
    else:
        pf_out = round(float(pf), 8)

    rec = TargetValidationV2(
        target_key=target,
        target_type=target_type,
        lab_dir=str(lab),
        source_path=cfg.source_path,
        schema_source=cfg.source,
        validation_status=status,
        ledger_result_status=ledger_status,
        raw_rows=raw_target_rows,
        clean_rows=int(len(tdf)),
        dropped_bad_symbol_rows=dropped_bad,
        trade_count=trade_count,
        symbol_count=symbol_count,
        avg_pnl=round(avg_pnl, 8),
        total_pnl=round(total_pnl, 8),
        profit_factor=pf_out,
        win_rate=round(wr, 6),
        positive_symbol_rate=round(psr, 6),
        positive_split_rate=round(psplit, 6),
        split_count=split_count,
        top_symbol=best,
        worst_symbol=worst,
        top_symbol_trade_share=round(top_trade, 6),
        top_symbol_pnl_share=round(top_pnl, 6),
        symbol_hhi=round(hhi, 6),
        bad_symbol_examples=bad_examples,
        reasons=reasons,
        warnings=warnings,
        evidence_json=str(evidence_json),
        evidence_csv=str(evidence_csv),
        ledger_task_id=f"schema_aware_v2_{target}",
        promotes_or_trades=False,
        live_allowed=False,
    )
    write_json(evidence_json, {"validation": asdict(rec), "schema_config": asdict(cfg)})
    pd.DataFrame([asdict(rec)]).to_csv(evidence_csv, index=False)
    return rec


def append_ledger(workspace: Path, rec: TargetValidationV2) -> Optional[str]:
    try:
        root = workspace / "edge_factory_research_result_ledger"
        ledger = root / "master_research_result_ledger.jsonl"
        raw = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "task_id": rec.ledger_task_id,
            "result_status": rec.ledger_result_status,
            "score": rec.positive_symbol_rate,
            "summary": f"{rec.target_key}: {rec.validation_status}, clean_trades={rec.trade_count}, symbols={rec.symbol_count}, avg={rec.avg_pnl}, pf={rec.profit_factor}",
            "evidence_path": rec.evidence_json,
            "family": rec.target_key if rec.target_type == "ACTIVE_FAMILY" else None,
            "candidate": rec.target_key if rec.target_type == "RESEARCH_CANDIDATE" else None,
            "tags": ["schema_aware_v2", "coin_subset", "offline", "no_promotion"],
            "reviewer": "schema_aware_validator_v2",
            "source": "edge_factory_schema_aware_validator_v2",
            "safe_for_auto_promotion": False,
            "live_allowed": False,
            "notes": "Schema-clean evidence-only validation. No promotion or active config mutation.",
        }
        result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"
        row = {"result_id": result_id, **raw}
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        # refresh csv best effort
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


def results_df(results: List[TargetValidationV2]) -> pd.DataFrame:
    rows = []
    for r in results:
        d = asdict(r)
        d["reasons"] = " | ".join(r.reasons)
        d["warnings"] = " | ".join(r.warnings)
        rows.append(d)
    return pd.DataFrame(rows)


def write_report(path: Path, state: ValidatorStateV2, results: List[TargetValidationV2], cfg: SchemaConfig) -> None:
    lines = [
        "# Edge Factory Schema-Aware Validator v2 Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall verdict: **{state.overall_verdict}**",
        f"Trade source: `{state.trade_source}`",
        f"Schema source: `{state.schema_source}`",
        f"Columns: family=`{state.family_col}`, pnl=`{state.pnl_col}`, symbol=`{state.symbol_col}`, time=`{state.time_col}`",
        f"Targets seen: **{state.targets_seen}**",
        f"Targets validated: **{state.targets_validated}**",
        f"Robust: **{state.robust_count}**",
        f"Concentrated: **{state.concentrated_count}**",
        f"Weak: **{state.weak_count}**",
        f"Needs more data: **{state.needs_more_data_count}**",
        f"Inconclusive: **{state.inconclusive_count}**",
        f"Ledger records appended: **{state.ledger_records_appended}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Reasons",
        "",
    ]
    for reason in state.reasons:
        lines.append(f"- {reason}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Results", ""]
    if results:
        lines += ["| Target | Type | Status | Raw | Clean | Dropped bad symbol | Symbols | Pos symbol | Top trade | Top PnL | PF |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in results:
            lines.append(f"| {r.target_key} | {r.target_type} | {r.validation_status} | {r.raw_rows} | {r.clean_rows} | {r.dropped_bad_symbol_rows} | {r.symbol_count} | {r.positive_symbol_rate} | {r.top_symbol_trade_share} | {r.top_symbol_pnl_share} | {r.profit_factor} |")
    else:
        lines.append("No results.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "This is the replacement evidence after artifact audit. Prefer these v2 results over earlier provisional candidate/coin-subset validator outputs.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory schema-aware validator v2")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--source", default=None, help="Explicit trade-level CSV source")
    p.add_argument("--target", default=None)
    p.add_argument("--active_only", action="store_true")
    p.add_argument("--candidates_only", action="store_true")
    p.add_argument("--out_dir", default=None)
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_schema_aware_validator_v2"
    out_dir = out_root / f"schema_aware_v2_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_schema_config(workspace, args.source)
    df = pd.read_csv(cfg.source_path)
    labs = discover_labs(workspace, args.target, bool(args.active_only), bool(args.candidates_only))
    results: List[TargetValidationV2] = []
    ledger_count = 0
    warnings: List[str] = list(cfg.warnings)

    for lab in labs:
        rec = validate_target(lab, df, cfg, stamp)
        results.append(rec)
        if not args.no_ledger_append:
            rid = append_ledger(workspace, rec)
            if rid:
                ledger_count += 1
            else:
                warnings.append(f"ledger append failed for {rec.target_key}")

    robust = len([r for r in results if r.validation_status == "ROBUST_COIN_FIT_SCHEMA_CLEAN"])
    concentrated = len([r for r in results if r.validation_status == "CONCENTRATED_BUT_POSITIVE_SCHEMA_CLEAN"])
    weak = len([r for r in results if r.validation_status == "WEAK_COIN_FIT_SCHEMA_CLEAN"])
    needs = len([r for r in results if r.validation_status == "NEEDS_MORE_DATA"])
    inconc = len([r for r in results if r.validation_status == "INCONCLUSIVE"])

    if not labs:
        warnings.append("No target labs discovered. Run candidate_lab_builder first or check filters.")
    if any(r.dropped_bad_symbol_rows > 0 for r in results):
        warnings.append("Some rows were dropped due to invalid symbol values. v2 results are cleaner than v1 but source still contains minor bad symbols.")

    if weak > 0 or inconc > 0:
        overall = "WARN"
    elif warnings:
        overall = "WARN"
    else:
        overall = "PASS"

    state = ValidatorStateV2(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        schema_source=cfg.source,
        trade_source=cfg.source_path,
        family_col=cfg.family_col,
        pnl_col=cfg.pnl_col,
        symbol_col=cfg.symbol_col,
        time_col=cfg.time_col,
        targets_seen=len(labs),
        targets_validated=len(results),
        robust_count=robust,
        concentrated_count=concentrated,
        weak_count=weak,
        needs_more_data_count=needs,
        inconclusive_count=inconc,
        schema_warning_count=len(cfg.warnings),
        ledger_append_enabled=not bool(args.no_ledger_append),
        ledger_records_appended=ledger_count,
        overall_verdict=overall,
        live_allowed=False,
        reasons=[
            "Schema-aware validation used audited trade-level source only.",
            "Summary/metric CSVs were not used as trade rows.",
            "Results are evidence-only and cannot promote or trade.",
        ],
        warnings=warnings,
        hard_rules=[
            "Schema-aware validator v2 never starts paper/live.",
            "Schema-aware validator v2 never mutates active config.",
            "Schema-aware validator v2 never promotes candidates automatically.",
            "v2 evidence supersedes earlier provisional validator outputs.",
            "Live remains blocked.",
        ],
    )

    result_obj = {"state": asdict(state), "schema_config": asdict(cfg), "results": [asdict(r) for r in results]}
    state_path = out_dir / "schema_aware_validator_v2_state.json"
    write_json(state_path, result_obj)
    write_json(out_dir / "schema_aware_validator_v2_results.json", [asdict(r) for r in results])
    results_df(results).to_csv(out_dir / "schema_aware_validator_v2_summary.csv", index=False)
    write_report(out_dir / "schema_aware_validator_v2_report.md", state, results, cfg)

    print("EDGE FACTORY SCHEMA-AWARE VALIDATOR v2")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_verdict: {state.overall_verdict}")
    print(f"trade_source: {state.trade_source}")
    print(f"schema_source: {state.schema_source}")
    print(f"columns: family={state.family_col} pnl={state.pnl_col} symbol={state.symbol_col} time={state.time_col}")
    print(f"targets_seen={state.targets_seen} validated={state.targets_validated}")
    print(f"robust={state.robust_count} concentrated={state.concentrated_count} weak={state.weak_count} needs={state.needs_more_data_count} inconclusive={state.inconclusive_count}")
    print(f"ledger_append_enabled={state.ledger_append_enabled} ledger_records_appended={state.ledger_records_appended}")
    print("live_allowed: False")
    print("")
    print("RESULTS")
    print("-" * 100)
    for r in results:
        print(f"{r.target_key:40s} {r.target_type:18s} status={r.validation_status:36s} raw={r.raw_rows:7d} clean={r.clean_rows:7d} drop_bad={r.dropped_bad_symbol_rows:5d} symbols={r.symbol_count:4d} pos_sym={r.positive_symbol_rate:.2%} top_trade={r.top_symbol_trade_share:.2%} top_pnl={r.top_symbol_pnl_share:.2%} pf={r.profit_factor:.3f}")
        print(f"     best={r.top_symbol} worst={r.worst_symbol}")
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
    print(f"Report : {out_dir / 'schema_aware_validator_v2_report.md'}")
    print(f"State  : {state_path}")
    print(f"Summary: {out_dir / 'schema_aware_validator_v2_summary.csv'}")
    return 0 if state.overall_verdict != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
