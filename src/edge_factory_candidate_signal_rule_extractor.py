#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY CANDIDATE SIGNAL RULE EXTRACTOR v1
===============================================

Purpose
-------
Extract / reconstruct the exact candidate signal rule needed before a sandbox-only
shadow paper logger can be built.

Current target:
    ret60_reversal_short

Why this exists
---------------
The promotion sandbox and shadow spec say:
    PARTIALLY_INFERRED_RET60_REVERSAL_NEEDS_EXACT_RULE

That means the candidate has passed evidence gates, but the OS must not build/run a
shadow logger until the entry rule is explicit enough to implement.

This module DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - edit MASTER_UPPER_SYSTEM
    - edit position sizing contract
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - read the latest shadow paper spec
    - inspect normalized_oos_trades candidate rows
    - detect candidate feature columns, side, hold/exit hints, thresholds and constants
    - inspect available candle/feature universe files for matching columns
    - produce an implementability verdict:
        RULE_EXACT_READY_FOR_LOGGER_BUILD
        RULE_PARTIAL_NEEDS_ORIGINAL_SCANNER
        RULE_BLOCKED_INSUFFICIENT_FEATURES
    - write a rule contract for a future sandbox-only logger

Run:
    python "C:\Users\alike\edge_factory_candidate_signal_rule_extractor.py"

Run one candidate:
    python "C:\Users\alike\edge_factory_candidate_signal_rule_extractor.py" --candidate ret60_reversal_short

Core rule
---------
This is extraction/specification only. It does not create or run a logger.
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

FAMILY_COLS = ["family_key", "family", "strategy", "strategy_key", "candidate_key", "candidate", "label", "name"]
SYMBOL_COLS = ["symbol", "inst_id", "instrument", "inst", "ticker", "coin"]
TIME_COLS = ["event_time", "exit_time", "entry_time", "timestamp", "time", "datetime", "date", "open_time", "close_time", "ts"]
PNL_COLS = ["pnl", "net_pnl_usdt", "pnl_usdt", "net_pnl", "gross_pnl_usdt", "profit"]
SIDE_COLS = ["side", "direction", "position_side", "trade_side"]
HOLD_COLS = ["hold_minutes", "hold_mins", "horizon_min", "horizon", "exit_minutes", "bars_hold", "hold"]
PRICE_COLS = ["entry_price", "exit_price", "price", "close", "mark_price"]

FEATURE_HINTS = ["ret", "z", "rank", "market", "volume", "vol", "close", "trend", "momentum", "rsi", "ema", "atr", "funding", "spread", "signal", "score"]
RET60_HINTS = ["ret60", "ret_60", "ret60m", "ret60_bps", "ret60m_bps", "ret_60m_bps", "60m", "60"]


@dataclass
class SourcePaths:
    normalized_trades: Optional[str]
    shadow_spec_state: Optional[str]
    shadow_spec_json: Optional[str]
    candle_inventory_manifest: Optional[str]
    feature_files: List[str]


@dataclass
class CandidateRuleProfile:
    candidate_key: str
    source_path: str
    rows_candidate: int
    symbols_candidate: int
    family_col: Optional[str]
    symbol_col: Optional[str]
    time_col: Optional[str]
    pnl_col: Optional[str]
    side_col: Optional[str]
    hold_col: Optional[str]
    side_distribution: Dict[str, int]
    hold_distribution: Dict[str, int]
    pnl_total: float
    pnl_avg: float
    pnl_pf: float
    win_rate: float
    feature_columns: List[str]
    ret60_like_columns: List[str]
    constant_columns: Dict[str, Any]
    numeric_quantiles: Dict[str, Dict[str, float]]
    candidate_feature_ranges: Dict[str, Dict[str, float]]
    sample_symbols: List[str]
    warnings: List[str]


@dataclass
class FeatureUniverseMatch:
    file_path: str
    file_format: str
    rows: int
    time_col: Optional[str]
    matched_columns: List[str]
    ret60_like_columns: List[str]
    symbols_detected: int
    coverage_days: float
    quality: str
    warnings: List[str]


@dataclass
class RuleHypothesis:
    candidate_key: str
    rule_status: str
    implementability_score: float
    inferred_side: Optional[str]
    inferred_hold_minutes: Optional[float]
    primary_feature: Optional[str]
    primary_feature_direction: Optional[str]
    threshold_hypothesis: Optional[float]
    threshold_operator: Optional[str]
    required_features: List[str]
    required_data_sources: List[str]
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]


@dataclass
class ExtractorState:
    generated_at: str
    workspace: str
    candidate_filter: Optional[str]
    candidates_seen: int
    rules_extracted: int
    exact_ready_count: int
    partial_count: int
    blocked_count: int
    logger_build_allowed_count: int
    shadow_start_allowed_count: int
    active_paper_allowed_count: int
    live_allowed: bool
    overall_state: str
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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


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


def latest_shadow_spec_run(workspace: Path) -> Optional[Path]:
    return latest_child_dir(workspace / "edge_factory_shadow_paper_spec_builder", "shadow_spec_")


def latest_candle_inventory_manifest(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_candle_universe_inventory_v2", "candle_inventory_v2_")
    if not d:
        return None
    p = d / "candle_universe_manifest_v2.json"
    return p if p.exists() else None


def discover_shadow_specs(workspace: Path, candidate_filter: Optional[str]) -> List[Path]:
    root = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes"
    if not root.exists():
        return []
    specs = [p for p in root.rglob("shadow_spec/shadow_paper_spec.json") if p.exists()]
    if candidate_filter:
        specs = [p for p in specs if safe_key(candidate_filter) in safe_key(str(p))]
    specs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return specs


def discover_feature_files(workspace: Path, max_files: int = 200) -> List[Path]:
    hits: List[Path] = []
    for p in workspace.rglob("*"):
        if len(hits) >= max_files:
            break
        if not p.is_file() or p.suffix.lower() not in {".csv", ".parquet", ".pq"}:
            continue
        s = str(p).lower()
        if any(skip in s for skip in ["edge_factory_shadow_paper_spec_builder", "edge_factory_candidate_signal_rule_extractor", "paper_run_gate_", "live_"]):
            continue
        name = p.name.lower()
        if any(h in name for h in ["feature", "features", "candle", "candles", "wide", "matrix", "ohlcv", "kline"]):
            hits.append(p)
    hits.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return hits[:max_files]


def find_col(df: pd.DataFrame, options: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): str(c) for c in df.columns}
    for opt in options:
        if opt.lower() in lookup:
            return lookup[opt.lower()]
    for c in df.columns:
        low = str(c).lower()
        if options == TIME_COLS and any(tok in low for tok in ["time", "date", "timestamp", "datetime"]):
            return str(c)
        if options == SYMBOL_COLS and any(tok in low for tok in ["symbol", "inst", "ticker", "coin"]):
            return str(c)
    return None


def normalize_symbol(raw: Any) -> Optional[str]:
    s = str(raw or "").strip().upper().replace("_", "-")
    if not s or s in {"UNKNOWN", "TRUE", "FALSE", "NONE", "NULL", "NAN"}:
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


def profit_factor(pnl: pd.Series) -> float:
    gains = float(pnl[pnl > 0].sum())
    losses = float((-pnl[pnl < 0]).sum())
    if losses <= 0:
        return 999999.0 if gains > 0 else 0.0
    return gains / losses


def detect_feature_columns(columns: Sequence[str]) -> List[str]:
    out: List[str] = []
    for col in columns:
        low = str(col).lower()
        if any(h in low for h in FEATURE_HINTS):
            out.append(str(col))
    return out


def detect_ret60_like(columns: Sequence[str]) -> List[str]:
    out = []
    for col in columns:
        low = str(col).lower()
        if "ret60" in low or "ret_60" in low or "60m" in low or "ret60m" in low:
            out.append(str(col))
    return out


def candidate_rows(source: Path, candidate: str) -> Tuple[pd.DataFrame, Dict[str, Optional[str]], List[str], int]:
    warnings: List[str] = []
    head = pd.read_csv(source, nrows=3000)
    cols = {
        "family_col": find_col(head, FAMILY_COLS),
        "symbol_col": find_col(head, SYMBOL_COLS),
        "time_col": find_col(head, TIME_COLS),
        "pnl_col": find_col(head, PNL_COLS),
        "side_col": find_col(head, SIDE_COLS),
        "hold_col": find_col(head, HOLD_COLS),
    }
    if not cols["family_col"]:
        raise ValueError("No family/candidate column found in normalized trades")
    df = pd.read_csv(source)
    fam = df[cols["family_col"]].astype(str).str.lower().str.strip()
    key = safe_key(candidate)
    mask = fam == key
    if not mask.any():
        mask = fam.str.contains(key, regex=False, na=False)
        if mask.any():
            warnings.append("used contains-match because exact candidate key produced no rows")
    cdf = df.loc[mask].copy()
    if cols["symbol_col"] and cols["symbol_col"] in cdf.columns:
        cdf["__symbol_norm"] = cdf[cols["symbol_col"]].map(normalize_symbol)
    if cols["pnl_col"] and cols["pnl_col"] in cdf.columns:
        cdf["__pnl"] = pd.to_numeric(cdf[cols["pnl_col"]], errors="coerce")
    return cdf, cols, warnings, int(len(df))


def profile_candidate(source: Path, candidate: str) -> CandidateRuleProfile:
    cdf, cols, warnings, total_rows = candidate_rows(source, candidate)
    feature_cols = detect_feature_columns(cdf.columns)
    ret60_cols = detect_ret60_like(cdf.columns)

    constants: Dict[str, Any] = {}
    numeric_quantiles: Dict[str, Dict[str, float]] = {}
    feature_ranges: Dict[str, Dict[str, float]] = {}

    if not cdf.empty:
        for col in cdf.columns:
            try:
                nunique = cdf[col].nunique(dropna=True)
                if 0 < nunique <= 5 and len(constants) < 50:
                    vals = cdf[col].dropna().unique().tolist()[:5]
                    constants[str(col)] = vals[0] if len(vals) == 1 else vals
            except Exception:
                pass

        for col in cdf.columns:
            if len(numeric_quantiles) >= 80:
                break
            s = pd.to_numeric(cdf[col], errors="coerce")
            if s.notna().sum() >= max(10, int(0.20 * len(cdf))):
                numeric_quantiles[str(col)] = {
                    "min": float(s.min()),
                    "q01": float(s.quantile(0.01)),
                    "q05": float(s.quantile(0.05)),
                    "q10": float(s.quantile(0.10)),
                    "median": float(s.median()),
                    "q90": float(s.quantile(0.90)),
                    "q95": float(s.quantile(0.95)),
                    "q99": float(s.quantile(0.99)),
                    "max": float(s.max()),
                    "non_null": int(s.notna().sum()),
                }

        for col in feature_cols:
            s = pd.to_numeric(cdf[col], errors="coerce")
            if s.notna().sum() > 0:
                feature_ranges[str(col)] = {
                    "min": float(s.min()),
                    "q05": float(s.quantile(0.05)),
                    "median": float(s.median()),
                    "q95": float(s.quantile(0.95)),
                    "max": float(s.max()),
                    "non_null": int(s.notna().sum()),
                }

    side_dist: Dict[str, int] = {}
    if cols.get("side_col") and cols["side_col"] in cdf.columns:
        side_dist = {str(k): int(v) for k, v in cdf[cols["side_col"]].astype(str).value_counts().to_dict().items()}
    hold_dist: Dict[str, int] = {}
    if cols.get("hold_col") and cols["hold_col"] in cdf.columns:
        hold_dist = {str(k): int(v) for k, v in cdf[cols["hold_col"]].astype(str).value_counts().head(20).to_dict().items()}

    pnl = cdf["__pnl"].dropna() if "__pnl" in cdf.columns else pd.Series(dtype=float)
    symbols = sorted(cdf["__symbol_norm"].dropna().astype(str).unique().tolist())[:80] if "__symbol_norm" in cdf.columns else []

    if not feature_cols:
        warnings.append("No feature-like columns found inside normalized candidate rows")
    if not ret60_cols and "ret60" in safe_key(candidate):
        warnings.append("Candidate name implies ret60 but no explicit ret60-like column found")
    if not side_dist:
        warnings.append("No side/direction column found; side must be inferred from candidate name")

    return CandidateRuleProfile(
        candidate_key=safe_key(candidate),
        source_path=str(source),
        rows_candidate=int(len(cdf)),
        symbols_candidate=int(cdf["__symbol_norm"].nunique()) if "__symbol_norm" in cdf.columns else 0,
        family_col=cols.get("family_col"),
        symbol_col=cols.get("symbol_col"),
        time_col=cols.get("time_col"),
        pnl_col=cols.get("pnl_col"),
        side_col=cols.get("side_col"),
        hold_col=cols.get("hold_col"),
        side_distribution=side_dist,
        hold_distribution=hold_dist,
        pnl_total=float(pnl.sum()) if not pnl.empty else 0.0,
        pnl_avg=float(pnl.mean()) if not pnl.empty else 0.0,
        pnl_pf=float(profit_factor(pnl)) if not pnl.empty else 0.0,
        win_rate=float((pnl > 0).mean()) if not pnl.empty else 0.0,
        feature_columns=feature_cols,
        ret60_like_columns=ret60_cols,
        constant_columns=constants,
        numeric_quantiles=numeric_quantiles,
        candidate_feature_ranges=feature_ranges,
        sample_symbols=symbols,
        warnings=warnings,
    )


def read_sample(path: Path, n: int = 2000) -> Tuple[Optional[pd.DataFrame], Optional[int], str]:
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, nrows=n)
            rows = None
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    rows = max(0, sum(1 for _ in f) - 1)
            except Exception:
                pass
            return df, rows, "OK"
        df = pd.read_parquet(path)
        rows = len(df)
        return df.head(n), rows, "OK"
    except Exception as e:
        return None, None, repr(e)


def inspect_feature_file(path: Path, candidate: str) -> FeatureUniverseMatch:
    warnings: List[str] = []
    df, rows, status = read_sample(path)
    if df is None:
        return FeatureUniverseMatch(str(path), "READ_ERROR", 0, None, [], [], 0, 0.0, "READ_ERROR", [status])

    time_col = find_col(df, TIME_COLS)
    matched_cols: List[str] = []
    ret60_cols: List[str] = []
    key = safe_key(candidate)
    base_hint = None
    if "ret60" in key:
        base_hint = "ret60"

    for col in df.columns:
        low = str(col).lower()
        if base_hint and base_hint in low:
            matched_cols.append(str(col))
            ret60_cols.append(str(col))
        elif any(h in low for h in ["ret60", "ret_60", "60m"]):
            matched_cols.append(str(col))
            ret60_cols.append(str(col))

    # Wide file symbol estimate from BASE_feature columns.
    symbols = set()
    for col in df.columns:
        m = re.match(r"^([A-Z0-9]+)_", str(col), flags=re.I)
        if m:
            sym = normalize_symbol(m.group(1))
            if sym:
                symbols.add(sym)

    coverage_days = 0.0
    if time_col and time_col in df.columns:
        ts = pd.to_datetime(df[time_col], errors="coerce", utc=True).dropna()
        if not ts.empty:
            coverage_days = float((ts.max() - ts.min()).total_seconds() / 86400.0)
            if rows and rows > len(df) and coverage_days > 0:
                # Sample coverage estimate is not full coverage; avoid overclaim.
                warnings.append("coverage_days is sample-only estimate")
    else:
        warnings.append("no time column detected in feature file sample")

    if ret60_cols:
        quality = "RET60_FEATURES_FOUND"
    elif matched_cols:
        quality = "FEATURE_MATCH_FOUND"
    else:
        quality = "NO_MATCH"
    return FeatureUniverseMatch(
        file_path=str(path),
        file_format="FEATURE_OR_CANDLE_FILE",
        rows=int(rows or len(df)),
        time_col=time_col,
        matched_columns=matched_cols[:200],
        ret60_like_columns=ret60_cols[:200],
        symbols_detected=len(symbols),
        coverage_days=round(coverage_days, 6),
        quality=quality,
        warnings=warnings,
    )


def infer_side(candidate: str, profile: CandidateRuleProfile) -> Tuple[Optional[str], List[str]]:
    warnings: List[str] = []
    if profile.side_distribution:
        top = max(profile.side_distribution.items(), key=lambda kv: kv[1])[0].lower()
        if "short" in top or top in {"sell", "-1"}:
            return "short", warnings
        if "long" in top or top in {"buy", "1"}:
            return "long", warnings
    key = safe_key(candidate)
    if "short" in key:
        warnings.append("side inferred from candidate name because side column is missing")
        return "short", warnings
    if "long" in key:
        warnings.append("side inferred from candidate name because side column is missing")
        return "long", warnings
    warnings.append("side could not be inferred")
    return None, warnings


def infer_hold(profile: CandidateRuleProfile) -> Tuple[Optional[float], List[str]]:
    warnings: List[str] = []
    if profile.hold_distribution:
        try:
            top = max(profile.hold_distribution.items(), key=lambda kv: kv[1])[0]
            return float(top), warnings
        except Exception:
            warnings.append("hold distribution found but top value is not numeric")
    # Look for constant horizon-ish columns.
    for col, val in profile.constant_columns.items():
        low = col.lower()
        if any(h in low for h in ["hold", "horizon", "exit", "minute", "min"]):
            try:
                if isinstance(val, list):
                    return float(val[0]), warnings
                return float(val), warnings
            except Exception:
                pass
    warnings.append("hold/exit horizon could not be inferred; future logger must define it")
    return None, warnings


def infer_primary_feature(profile: CandidateRuleProfile, matches: List[FeatureUniverseMatch]) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[str], List[str], List[str]]:
    warnings: List[str] = []
    blockers: List[str] = []

    # Prefer explicit ret60-like columns in candidate rows; otherwise feature universe matches.
    candidates = profile.ret60_like_columns[:]
    if not candidates:
        for m in matches:
            candidates.extend(m.ret60_like_columns)
    candidates = list(dict.fromkeys(candidates))

    if not candidates:
        blockers.append("no ret60-like feature column found in candidate rows or feature universe")
        return None, None, None, None, warnings, blockers

    primary = candidates[0]
    direction = None
    threshold = None
    operator = None

    # If candidate rows contain the primary feature, estimate threshold from selected rows.
    if primary in profile.candidate_feature_ranges:
        q = profile.candidate_feature_ranges[primary]
        med = q.get("median")
        mn = q.get("min")
        mx = q.get("max")
        if med is not None:
            if med > 0:
                direction = "positive_extreme_or_reversal_context"
                operator = ">="
                threshold = q.get("q05", med)
            elif med < 0:
                direction = "negative_extreme_or_reversal_context"
                operator = "<="
                threshold = q.get("q95", med)
            else:
                direction = "near_zero_or_rank_based"
                operator = "UNKNOWN"
                threshold = None
                warnings.append("primary feature median is near zero; exact threshold cannot be inferred")
        if mn is not None and mx is not None and abs(mx - mn) < 1e-12:
            warnings.append("primary feature appears constant in selected rows; may be a parameter, not signal value")
    else:
        warnings.append("primary feature found in universe but not candidate rows; exact selected-row threshold unavailable")

    if threshold is None or operator is None or operator == "UNKNOWN":
        blockers.append("exact threshold/operator is not reconstructable from current artifacts")
    return primary, direction, threshold, operator, warnings, blockers


def build_rule_hypothesis(profile: CandidateRuleProfile, matches: List[FeatureUniverseMatch]) -> RuleHypothesis:
    reasons: List[str] = []
    warnings: List[str] = list(profile.warnings)
    blockers: List[str] = []

    side, side_w = infer_side(profile.candidate_key, profile)
    warnings.extend(side_w)
    hold, hold_w = infer_hold(profile)
    warnings.extend(hold_w)
    primary, direction, threshold, operator, feat_w, feat_blockers = infer_primary_feature(profile, matches)
    warnings.extend(feat_w)
    blockers.extend(feat_blockers)

    required_features: List[str] = []
    if primary:
        required_features.append(primary)
    required_sources = [m.file_path for m in matches if m.quality in {"RET60_FEATURES_FOUND", "FEATURE_MATCH_FOUND"}][:10]

    score = 0.0
    if profile.rows_candidate >= 300:
        score += 15
    if profile.symbols_candidate >= 50:
        score += 15
    if side:
        score += 15
    if hold is not None:
        score += 10
    if primary:
        score += 20
    if threshold is not None and operator and operator != "UNKNOWN":
        score += 20
    if required_sources:
        score += 5

    if side and primary and threshold is not None and operator and operator != "UNKNOWN" and required_sources:
        status = "RULE_EXACT_READY_FOR_LOGGER_BUILD"
        logger_allowed = True
        reasons.append("side, primary feature, threshold/operator, and feature source are available")
    elif side and primary and required_sources:
        status = "RULE_PARTIAL_NEEDS_ORIGINAL_SCANNER"
        logger_allowed = False
        blockers.append("exact threshold/operator still requires original scanner or candidate generator logic")
        reasons.append("side and feature source are available, but exact rule is incomplete")
    else:
        status = "RULE_BLOCKED_INSUFFICIENT_FEATURES"
        logger_allowed = False
        reasons.append("candidate rule is not implementable from current artifacts")

    if hold is None:
        blockers.append("hold/exit horizon must be defined before logger build")

    return RuleHypothesis(
        candidate_key=profile.candidate_key,
        rule_status=status,
        implementability_score=round(score, 4),
        inferred_side=side,
        inferred_hold_minutes=hold,
        primary_feature=primary,
        primary_feature_direction=direction,
        threshold_hypothesis=threshold,
        threshold_operator=operator,
        required_features=required_features,
        required_data_sources=required_sources,
        logger_build_allowed=logger_allowed,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        reasons=reasons,
        blockers=list(dict.fromkeys(blockers)),
        warnings=list(dict.fromkeys(warnings)),
    )


def append_ledger(workspace: Path, hyp: RuleHypothesis, evidence_path: Path) -> Optional[str]:
    try:
        root = workspace / "edge_factory_research_result_ledger"
        ledger = root / "master_research_result_ledger.jsonl"
        if hyp.rule_status == "RULE_EXACT_READY_FOR_LOGGER_BUILD":
            status = "PASS"
        elif hyp.rule_status == "RULE_PARTIAL_NEEDS_ORIGINAL_SCANNER":
            status = "WATCHLIST"
        else:
            status = "INCONCLUSIVE"
        raw = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "task_id": f"signal_rule_extraction_{hyp.candidate_key}",
            "result_status": status,
            "score": hyp.implementability_score,
            "summary": f"{hyp.candidate_key}: {hyp.rule_status}, side={hyp.inferred_side}, feature={hyp.primary_feature}, threshold={hyp.threshold_operator} {hyp.threshold_hypothesis}",
            "evidence_path": str(evidence_path),
            "family": None,
            "candidate": hyp.candidate_key,
            "tags": ["signal_rule_extraction", "sandbox", "offline", "no_runtime", "no_live"],
            "reviewer": "candidate_signal_rule_extractor_v1",
            "source": "edge_factory_candidate_signal_rule_extractor_v1",
            "safe_for_auto_promotion": False,
            "live_allowed": False,
            "notes": "Rule extraction only. Does not build/run logger.",
        }
        result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stable_hash(raw)}"
        row = {"result_id": result_id, **raw}
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
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


def write_candidate_outputs(workspace: Path, out_dir: Path, profile: CandidateRuleProfile, matches: List[FeatureUniverseMatch], hyp: RuleHypothesis, stamp: str) -> Path:
    persistent = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes" / hyp.candidate_key / "signal_rule"
    run_dir = out_dir / "candidates" / hyp.candidate_key
    persistent.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    obj = {
        "profile": asdict(profile),
        "feature_universe_matches": [asdict(m) for m in matches],
        "rule_hypothesis": asdict(hyp),
        "permissions": {
            "logger_build_allowed": hyp.logger_build_allowed,
            "shadow_start_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "mutates_active_config": False,
        },
    }
    for d in [persistent, run_dir]:
        write_json(d / "candidate_signal_rule_contract.json", obj)
        pd.DataFrame([asdict(m) for m in matches]).to_csv(d / "feature_universe_matches.csv", index=False)

    md = f"""# Candidate Signal Rule Extraction: `{hyp.candidate_key}`

Status: **{hyp.rule_status}**

## Inferred rule components

- Side: `{hyp.inferred_side}`
- Hold minutes: `{hyp.inferred_hold_minutes}`
- Primary feature: `{hyp.primary_feature}`
- Feature direction: `{hyp.primary_feature_direction}`
- Threshold hypothesis: `{hyp.threshold_operator} {hyp.threshold_hypothesis}`
- Implementability score: `{hyp.implementability_score}`

## Permissions

- Logger build allowed: `{hyp.logger_build_allowed}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Required features

```text
{chr(10).join(hyp.required_features)}
```

## Required data sources

```text
{chr(10).join(hyp.required_data_sources)}
```

## Blockers

```text
{chr(10).join(hyp.blockers) if hyp.blockers else 'none'}
```

## Warnings

```text
{chr(10).join(hyp.warnings) if hyp.warnings else 'none'}
```

## Interpretation

This extraction is evidence only. It does not build or run a logger.
If status is `RULE_PARTIAL_NEEDS_ORIGINAL_SCANNER`, find the original candidate scanner/backtest code that generated `{hyp.candidate_key}` and extract the exact threshold/entry rule.
"""
    write_text(persistent / "candidate_signal_rule_contract.md", md)
    write_text(run_dir / "candidate_signal_rule_contract.md", md)

    interface = f'''# REFERENCE ONLY - extracted signal contract for {hyp.candidate_key}
# This is not an active logger.

CANDIDATE_KEY = "{hyp.candidate_key}"
RULE_STATUS = "{hyp.rule_status}"
LOGGER_BUILD_ALLOWED = {hyp.logger_build_allowed!r}
SHADOW_START_ALLOWED = False
ACTIVE_PAPER_ALLOWED = False
LIVE_ALLOWED = False

INFERRED_SIDE = {hyp.inferred_side!r}
INFERRED_HOLD_MINUTES = {hyp.inferred_hold_minutes!r}
PRIMARY_FEATURE = {hyp.primary_feature!r}
THRESHOLD_OPERATOR = {hyp.threshold_operator!r}
THRESHOLD_HYPOTHESIS = {hyp.threshold_hypothesis!r}
REQUIRED_FEATURES = {json.dumps(hyp.required_features, indent=4)}
REQUIRED_DATA_SOURCES = {json.dumps(hyp.required_data_sources, indent=4)}
BLOCKERS = {json.dumps(hyp.blockers, indent=4)}


def compute_candidate_signal(snapshot: dict) -> dict:
    """Reference-only placeholder.

    Must not be used until RULE_STATUS is exact and a sandbox-only logger is built.
    """
    raise NotImplementedError("Signal rule extraction is not approved for runtime yet.")
'''
    write_text(persistent / "extracted_signal_contract_REFERENCE_ONLY.py", interface)
    write_text(run_dir / "extracted_signal_contract_REFERENCE_ONLY.py", interface)
    return run_dir / "candidate_signal_rule_contract.json"


def records_df(profiles: List[CandidateRuleProfile], hyps: List[RuleHypothesis]) -> pd.DataFrame:
    rows = []
    pmap = {p.candidate_key: p for p in profiles}
    for h in hyps:
        p = pmap.get(h.candidate_key)
        rows.append({
            "candidate_key": h.candidate_key,
            "rule_status": h.rule_status,
            "implementability_score": h.implementability_score,
            "logger_build_allowed": h.logger_build_allowed,
            "shadow_start_allowed": h.shadow_start_allowed,
            "active_paper_allowed": h.active_paper_allowed,
            "live_allowed": h.live_allowed,
            "inferred_side": h.inferred_side,
            "inferred_hold_minutes": h.inferred_hold_minutes,
            "primary_feature": h.primary_feature,
            "threshold_operator": h.threshold_operator,
            "threshold_hypothesis": h.threshold_hypothesis,
            "rows_candidate": p.rows_candidate if p else None,
            "symbols_candidate": p.symbols_candidate if p else None,
            "feature_columns": len(p.feature_columns) if p else None,
            "ret60_like_columns": len(p.ret60_like_columns) if p else None,
            "blockers": " | ".join(h.blockers),
            "warnings": " | ".join(h.warnings),
        })
    return pd.DataFrame(rows)


def write_report(path: Path, state: ExtractorState, profiles: List[CandidateRuleProfile], hyps: List[RuleHypothesis]) -> None:
    lines = [
        "# Edge Factory Candidate Signal Rule Extractor Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall state: **{state.overall_state}**",
        f"Candidates seen: **{state.candidates_seen}**",
        f"Rules extracted: **{state.rules_extracted}**",
        f"Exact ready: **{state.exact_ready_count}**",
        f"Partial: **{state.partial_count}**",
        f"Blocked: **{state.blocked_count}**",
        f"Logger build allowed: **{state.logger_build_allowed_count}**",
        f"Shadow start allowed: **{state.shadow_start_allowed_count}**",
        f"Active paper allowed: **{state.active_paper_allowed_count}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Rule results",
        "",
    ]
    if hyps:
        lines += ["| Candidate | Status | Score | Side | Hold | Feature | Threshold | Logger build | Shadow start |", "|---|---:|---:|---|---:|---|---|---:|---:|"]
        for h in hyps:
            lines.append(f"| {h.candidate_key} | {h.rule_status} | {h.implementability_score} | {h.inferred_side} | {h.inferred_hold_minutes} | {h.primary_feature} | {h.threshold_operator} {h.threshold_hypothesis} | {h.logger_build_allowed} | {h.shadow_start_allowed} |")
    else:
        lines.append("No rule hypotheses produced.")
    lines += ["", "## Reasons", ""]
    for r in state.reasons:
        lines.append(f"- {r}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "The extractor tries to reconstruct the signal rule, but it will block runtime if the exact threshold/operator cannot be proven from artifacts. This prevents building a weak or fake sandbox logger.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory candidate signal rule extractor")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=None)
    p.add_argument("--source", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_candidate_signal_rule_extractor"
    out_dir = out_root / f"signal_rule_extract_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = Path(args.source) if args.source else latest_normalized_trades(workspace)
    shadow_specs = discover_shadow_specs(workspace, args.candidate)
    feature_files = discover_feature_files(workspace)
    candle_manifest = latest_candle_inventory_manifest(workspace)
    shadow_run = latest_shadow_spec_run(workspace)

    warnings: List[str] = []
    profiles: List[CandidateRuleProfile] = []
    matches_all: Dict[str, List[FeatureUniverseMatch]] = {}
    hyps: List[RuleHypothesis] = []
    ledger_count = 0

    if source is None or not source.exists():
        warnings.append("normalized_oos_trades source not found")
    if not shadow_specs:
        warnings.append("no shadow paper specs found; run shadow_paper_spec_builder first")

    if source and source.exists():
        for spec_path in shadow_specs:
            spec = read_json(spec_path)
            cand = spec.get("candidate", {}) if isinstance(spec.get("candidate"), dict) else {}
            key = safe_key(cand.get("candidate_key") or spec_path.parts[-3])
            if args.candidate and key != safe_key(args.candidate):
                continue
            try:
                profile = profile_candidate(source, key)
                profiles.append(profile)
                matches = [inspect_feature_file(p, key) for p in feature_files]
                matches = [m for m in matches if m.quality in {"RET60_FEATURES_FOUND", "FEATURE_MATCH_FOUND"}]
                matches.sort(key=lambda m: (m.quality != "RET60_FEATURES_FOUND", -m.symbols_detected, -m.rows))
                matches_all[key] = matches[:20]
                hyp = build_rule_hypothesis(profile, matches[:20])
                hyps.append(hyp)
                evidence_path = write_candidate_outputs(workspace, out_dir, profile, matches[:20], hyp, stamp)
                if not args.no_ledger_append:
                    rid = append_ledger(workspace, hyp, evidence_path)
                    if rid:
                        ledger_count += 1
                    else:
                        warnings.append(f"ledger append failed for {key}")
            except Exception as e:
                warnings.append(f"failed to extract rule for {key}: {e}")

    exact = len([h for h in hyps if h.rule_status == "RULE_EXACT_READY_FOR_LOGGER_BUILD"])
    partial = len([h for h in hyps if h.rule_status == "RULE_PARTIAL_NEEDS_ORIGINAL_SCANNER"])
    blocked = len([h for h in hyps if h.rule_status == "RULE_BLOCKED_INSUFFICIENT_FEATURES"])
    logger_allowed = len([h for h in hyps if h.logger_build_allowed])
    shadow_allowed = len([h for h in hyps if h.shadow_start_allowed])
    active_allowed = len([h for h in hyps if h.active_paper_allowed])

    if exact:
        overall = "RULE_EXTRACTION_READY_FOR_LOGGER_BUILD"
    elif partial:
        overall = "RULE_EXTRACTION_PARTIAL_NEEDS_ORIGINAL_SCANNER"
    elif hyps:
        overall = "RULE_EXTRACTION_BLOCKED"
    else:
        overall = "NO_RULES_EXTRACTED"

    state = ExtractorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate_filter=args.candidate,
        candidates_seen=len(shadow_specs),
        rules_extracted=len(hyps),
        exact_ready_count=exact,
        partial_count=partial,
        blocked_count=blocked,
        logger_build_allowed_count=logger_allowed,
        shadow_start_allowed_count=shadow_allowed,
        active_paper_allowed_count=active_allowed,
        live_allowed=False,
        overall_state=overall,
        reasons=[
            "Signal rule extractor inspected sandbox shadow specs and normalized trade evidence.",
            "Runtime remains blocked unless exact signal rule is proven.",
        ],
        warnings=warnings,
        hard_rules=[
            "Signal rule extractor never starts paper/live.",
            "Signal rule extractor never mutates active config.",
            "Signal rule extractor never edits MASTER_UPPER_SYSTEM.",
            "Signal rule extractor never edits position sizing contract.",
            "Partial rule extraction cannot be used for runtime.",
            "Live remains blocked.",
        ],
    )

    sources = SourcePaths(
        normalized_trades=str(source) if source else None,
        shadow_spec_state=str(shadow_run / "shadow_paper_spec_builder_state.json") if shadow_run and (shadow_run / "shadow_paper_spec_builder_state.json").exists() else None,
        shadow_spec_json=str(shadow_specs[0]) if shadow_specs else None,
        candle_inventory_manifest=str(candle_manifest) if candle_manifest else None,
        feature_files=[str(p) for p in feature_files[:50]],
    )

    state_path = out_dir / "candidate_signal_rule_extractor_state.json"
    write_json(state_path, {
        "state": asdict(state),
        "sources": asdict(sources),
        "profiles": [asdict(p) for p in profiles],
        "feature_matches": {k: [asdict(m) for m in v] for k, v in matches_all.items()},
        "rule_hypotheses": [asdict(h) for h in hyps],
    })
    records_df(profiles, hyps).to_csv(out_dir / "candidate_signal_rule_summary.csv", index=False)
    write_report(out_dir / "candidate_signal_rule_extractor_report.md", state, profiles, hyps)

    print("EDGE FACTORY CANDIDATE SIGNAL RULE EXTRACTOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_state: {state.overall_state}")
    print(f"normalized_trades: {sources.normalized_trades}")
    print(f"shadow_specs_seen: {state.candidates_seen}")
    print(f"rules_extracted: {state.rules_extracted}")
    print(f"exact_ready={state.exact_ready_count} partial={state.partial_count} blocked={state.blocked_count}")
    print(f"logger_build_allowed_count={state.logger_build_allowed_count}")
    print(f"shadow_start_allowed_count={state.shadow_start_allowed_count}")
    print(f"active_paper_allowed_count={state.active_paper_allowed_count}")
    print(f"ledger_records_appended={ledger_count}")
    print("live_allowed: False")
    print("")
    print("RULES")
    print("-" * 100)
    for h in hyps:
        print(f"{h.candidate_key:32s} status={h.rule_status:42s} score={h.implementability_score:6.2f} side={h.inferred_side} hold={h.inferred_hold_minutes} feature={h.primary_feature} threshold={h.threshold_operator} {h.threshold_hypothesis} logger_build={h.logger_build_allowed}")
        if h.reasons:
            print(f"     - {' | '.join(h.reasons[:3])}")
        if h.blockers:
            print(f"     blockers: {' | '.join(h.blockers[:4])}")
        if h.warnings:
            print(f"     warnings: {' | '.join(h.warnings[:4])}")
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
    print(f"Report : {out_dir / 'candidate_signal_rule_extractor_report.md'}")
    print(f"State  : {state_path}")
    print(f"Summary: {out_dir / 'candidate_signal_rule_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
