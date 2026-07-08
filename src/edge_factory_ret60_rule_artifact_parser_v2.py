#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 RULE ARTIFACT PARSER v2
==========================================

Purpose
-------
Parse ret60_reversal_short exact-validator artifacts using the real schema discovered by:
    edge_factory_ret60_artifact_schema_inspector.py

Known useful columns from inspector:
    combined_sim_session_first: pnl, signal_ret60_bps, signal_ret240_bps, signal_ret10_bps,
                                signal_ret5_bps, signal_ret3_bps, signal_ret1_bps,
                                signal_range_bps, entry_range_bps, gross_ret, net_ret,
                                cost_bps, extra_slip_bps
    session_trades:            signal_ret60_bps, net_ret, gross_ret, cost_bps, extra_slip_bps, ...

v1 failed because it selected session_trades and did not correctly prioritize combined_sim pnl.
v2 ranks variants using combined_sim_session_first.pnl first.

It DOES NOT:
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
    - parse 64 ret60 exact-validator artifacts
    - pair combined_sim + session_trades files by variant
    - compute PnL/PF/WR from combined_sim.pnl when present
    - validate filename params against artifact columns:
        m75/m100 vs min signal_ret60_bps
        extra0/25/50/100 vs extra_slip_bps
        hold720/delayX from filename contract
        h8 as still-needs-semantic-confirmation unless hour/session column exists
    - select best candidate variant by robust metric score
    - write ret60 exact-ish rule contract for future semantic recovery / sandbox logger builder

Run:
    python "C:\Users\alike\edge_factory_ret60_rule_artifact_parser_v2.py"

Core rule
---------
Even if params are extracted, runtime remains blocked until semantic confirmation is complete.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_CANDIDATE = "ret60_reversal_short"

PARAM_RE = re.compile(
    r"(?P<prefix>combined_sim_session_first|session_trades)_(?P<candidate>ret60_reversal_short)_h(?P<h>\d+)_m(?P<m>\d+)_hold(?P<hold>\d+)_delay(?P<delay>\d+)_extra(?P<extra>\d+)\.csv$",
    re.IGNORECASE,
)

SYMBOL_COLS = ["symbol", "inst_id", "instrument", "inst", "ticker", "coin"]
TIME_COLS = ["event_time", "entry_time", "exit_time", "timestamp", "time", "datetime", "date", "open_time", "close_time", "ts"]
HOUR_COL_HINTS = ["hour", "session", "h_param", "signal_hour", "entry_hour"]

PNL_PRIORITY = ["pnl", "net_pnl", "net_pnl_usdt", "pnl_usdt", "profit"]
RET_PRIORITY = ["net_ret", "gross_ret", "return_bps", "ret_bps", "net_return_bps", "gross_return_bps"]


@dataclass
class Params:
    candidate_key: str
    artifact_type: str
    h: int
    m: int
    hold: int
    delay: int
    extra: int
    variant_key: str


@dataclass
class ArtifactData:
    path: str
    filename: str
    artifact_type: str
    variant_key: str
    h: int
    m: int
    hold: int
    delay: int
    extra: int
    rows: int
    columns: List[str]
    pnl_col: Optional[str]
    ret_col: Optional[str]
    symbol_col: Optional[str]
    time_col: Optional[str]
    hour_cols: List[str]
    total_pnl: float
    avg_pnl: float
    profit_factor: float
    win_rate: float
    trade_count: int
    symbol_count: int
    signal_ret60_min: Optional[float]
    signal_ret60_max: Optional[float]
    signal_ret60_median: Optional[float]
    extra_slip_values: List[float]
    cost_bps_values: List[float]
    warnings: List[str]


@dataclass
class ParamValidation:
    variant_key: str
    m_param: int
    m_semantics_status: str
    m_observed_min_signal_ret60_bps: Optional[float]
    m_observed_max_signal_ret60_bps: Optional[float]
    m_rule_hypothesis: str
    extra_param: int
    extra_semantics_status: str
    observed_extra_slip_bps_values: List[float]
    hold_param: int
    hold_semantics_status: str
    delay_param: int
    delay_semantics_status: str
    h_param: int
    h_semantics_status: str
    h_observed_columns: List[str]
    confirmed_components: int
    total_components: int
    warnings: List[str]


@dataclass
class VariantV2:
    variant_key: str
    candidate_key: str
    h: int
    m: int
    hold: int
    delay: int
    extra: int
    combined_path: Optional[str]
    session_path: Optional[str]
    metric_source: str
    pnl_col: Optional[str]
    ret_col: Optional[str]
    trade_count: int
    symbol_count: int
    total_pnl: float
    avg_pnl: float
    profit_factor: float
    win_rate: float
    worst_pnl: float
    best_pnl: float
    median_pnl: float
    score: float
    rank_status: str
    param_validation_status: str
    confirmed_components: int
    total_components: int
    warnings: List[str]


@dataclass
class RuleContractV2:
    candidate_key: str
    contract_status: str
    selected_variant_key: Optional[str]
    selected_metric_source: Optional[str]
    selected_artifact_path: Optional[str]
    side: str
    rule_family: str
    h_param: Optional[int]
    m_param: Optional[int]
    hold_minutes: Optional[int]
    delay_minutes_or_bars: Optional[int]
    extra_slip_bps: Optional[int]
    entry_rule_hypothesis: str
    exit_rule_hypothesis: str
    cost_model_hypothesis: str
    confirmed_components: int
    total_components: int
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]


@dataclass
class ParserStateV2:
    generated_at: str
    workspace: str
    artifact_dir: str
    candidate: str
    artifacts_seen: int
    artifacts_loaded: int
    variants_seen: int
    positive_variants: int
    selected_variant: Optional[str]
    parser_status: str
    contract_status: str
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    reasons: List[str]
    warnings: List[str]
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_key(x: Any) -> str:
    return str(x or "").strip().lower().replace(" ", "_")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_filename(path: Path) -> Optional[Params]:
    m = PARAM_RE.search(path.name)
    if not m:
        return None
    candidate = safe_key(m.group("candidate"))
    h = int(m.group("h"))
    mm = int(m.group("m"))
    hold = int(m.group("hold"))
    delay = int(m.group("delay"))
    extra = int(m.group("extra"))
    return Params(
        candidate_key=candidate,
        artifact_type=m.group("prefix").lower(),
        h=h,
        m=mm,
        hold=hold,
        delay=delay,
        extra=extra,
        variant_key=f"{candidate}_h{h}_m{mm}_hold{hold}_delay{delay}_extra{extra}",
    )


def find_col(df: pd.DataFrame, names: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): str(c) for c in df.columns}
    for name in names:
        if name.lower() in lookup:
            return lookup[name.lower()]
    return None


def find_symbol_col(df: pd.DataFrame) -> Optional[str]:
    col = find_col(df, SYMBOL_COLS)
    if col:
        return col
    for c in df.columns:
        low = str(c).lower()
        if any(x in low for x in ["symbol", "inst", "ticker", "coin"]):
            return str(c)
    return None


def find_time_col(df: pd.DataFrame) -> Optional[str]:
    col = find_col(df, TIME_COLS)
    if col:
        return col
    for c in df.columns:
        low = str(c).lower()
        if any(x in low for x in ["time", "date", "timestamp", "datetime"]):
            return str(c)
    return None


def find_hour_cols(df: pd.DataFrame) -> List[str]:
    out = []
    for c in df.columns:
        low = str(c).lower()
        if any(h in low for h in HOUR_COL_HINTS):
            out.append(str(c))
    return out


def profit_factor(pnl: pd.Series) -> float:
    pnl = pnl.dropna()
    if pnl.empty:
        return 0.0
    gains = float(pnl[pnl > 0].sum())
    losses = float((-pnl[pnl < 0]).sum())
    if losses <= 0:
        return 999999.0 if gains > 0 else 0.0
    return gains / losses


def unique_float_values(series: pd.Series, limit: int = 20) -> List[float]:
    vals = pd.to_numeric(series, errors="coerce").dropna().unique().tolist()
    vals = sorted(float(x) for x in vals)[:limit]
    return vals


def read_artifact(path: Path) -> Optional[ArtifactData]:
    params = parse_filename(path)
    if not params:
        return None
    warnings: List[str] = []
    try:
        df = pd.read_csv(path)
    except Exception as e:
        warnings.append(f"read failed: {e}")
        return ArtifactData(
            path=str(path), filename=path.name, artifact_type=params.artifact_type, variant_key=params.variant_key,
            h=params.h, m=params.m, hold=params.hold, delay=params.delay, extra=params.extra,
            rows=0, columns=[], pnl_col=None, ret_col=None, symbol_col=None, time_col=None, hour_cols=[],
            total_pnl=0.0, avg_pnl=0.0, profit_factor=0.0, win_rate=0.0, trade_count=0, symbol_count=0,
            signal_ret60_min=None, signal_ret60_max=None, signal_ret60_median=None,
            extra_slip_values=[], cost_bps_values=[], warnings=warnings,
        )

    pnl_col = find_col(df, PNL_PRIORITY)
    ret_col = find_col(df, RET_PRIORITY)
    symbol_col = find_symbol_col(df)
    time_col = find_time_col(df)
    hour_cols = find_hour_cols(df)

    metric_col = pnl_col or ret_col
    pnl = pd.Series(dtype=float)
    if metric_col:
        pnl = pd.to_numeric(df[metric_col], errors="coerce").dropna()
        if not pnl_col and ret_col:
            warnings.append(f"using return column as metric proxy: {ret_col}")
    else:
        warnings.append("no pnl/return metric column found")

    symbol_count = 0
    if symbol_col and symbol_col in df.columns:
        symbol_count = int(df[symbol_col].dropna().astype(str).nunique())

    sig_min = sig_max = sig_med = None
    if "signal_ret60_bps" in df.columns:
        s = pd.to_numeric(df["signal_ret60_bps"], errors="coerce").dropna()
        if not s.empty:
            sig_min = float(s.min())
            sig_max = float(s.max())
            sig_med = float(s.median())

    extra_vals: List[float] = []
    if "extra_slip_bps" in df.columns:
        extra_vals = unique_float_values(df["extra_slip_bps"])
    cost_vals: List[float] = []
    if "cost_bps" in df.columns:
        cost_vals = unique_float_values(df["cost_bps"])

    return ArtifactData(
        path=str(path),
        filename=path.name,
        artifact_type=params.artifact_type,
        variant_key=params.variant_key,
        h=params.h,
        m=params.m,
        hold=params.hold,
        delay=params.delay,
        extra=params.extra,
        rows=int(len(df)),
        columns=[str(c) for c in df.columns],
        pnl_col=pnl_col,
        ret_col=ret_col,
        symbol_col=symbol_col,
        time_col=time_col,
        hour_cols=hour_cols,
        total_pnl=round(float(pnl.sum()), 8) if not pnl.empty else 0.0,
        avg_pnl=round(float(pnl.mean()), 8) if not pnl.empty else 0.0,
        profit_factor=round(float(profit_factor(pnl)), 8) if not pnl.empty else 0.0,
        win_rate=round(float((pnl > 0).mean()), 6) if not pnl.empty else 0.0,
        trade_count=int(len(pnl)) if not pnl.empty else int(len(df)),
        symbol_count=symbol_count,
        signal_ret60_min=round(sig_min, 8) if sig_min is not None else None,
        signal_ret60_max=round(sig_max, 8) if sig_max is not None else None,
        signal_ret60_median=round(sig_med, 8) if sig_med is not None else None,
        extra_slip_values=extra_vals,
        cost_bps_values=cost_vals,
        warnings=warnings,
    )


def validate_params(variant_key: str, params_source: ArtifactData, combined: Optional[ArtifactData], session: Optional[ArtifactData]) -> ParamValidation:
    warnings: List[str] = []
    src = session or combined or params_source
    total = 5
    confirmed = 0

    # m semantics: for m75/m100, session_trades signal_ret60_bps min should be near >= m.
    sig_min = None
    sig_max = None
    for cand in [session, combined]:
        if cand and cand.signal_ret60_min is not None:
            sig_min = cand.signal_ret60_min
            sig_max = cand.signal_ret60_max
            break
    if sig_min is not None:
        if sig_min >= src.m - 1e-6:
            m_status = "CONFIRMED_AS_MIN_SIGNAL_RET60_BPS_THRESHOLD"
            m_rule = f"signal_ret60_bps >= {src.m}"
            confirmed += 1
        else:
            m_status = "CONFLICT_WITH_SIGNAL_RET60_MIN"
            m_rule = f"expected signal_ret60_bps >= {src.m}, observed min {sig_min}"
            warnings.append("m parameter does not match observed min signal_ret60_bps")
    else:
        m_status = "UNKNOWN_NO_SIGNAL_RET60_COLUMN"
        m_rule = "UNKNOWN"
        warnings.append("signal_ret60_bps not available for m semantic validation")

    # extra semantics: extra_slip_bps values should equal extra param in combined or session.
    extra_vals = []
    for cand in [combined, session]:
        if cand and cand.extra_slip_values:
            extra_vals = cand.extra_slip_values
            break
    if extra_vals:
        if len(extra_vals) == 1 and abs(extra_vals[0] - src.extra) < 1e-9:
            extra_status = "CONFIRMED_AS_EXTRA_SLIP_BPS"
            confirmed += 1
        else:
            extra_status = "CONFLICT_OR_MULTIPLE_EXTRA_VALUES"
            warnings.append(f"extra param {src.extra} differs from extra_slip_bps values {extra_vals}")
    else:
        if src.extra == 0:
            extra_status = "ASSUMED_ZERO_EXTRA_SLIP_NO_COLUMN_VALUES"
            confirmed += 1
        else:
            extra_status = "UNKNOWN_NO_EXTRA_SLIP_COLUMN"
            warnings.append("extra_slip_bps not available for extra semantic validation")

    # hold semantics: filename gives hold720. Need column to fully confirm; otherwise partial.
    if src.hold > 0:
        hold_status = "PARAM_EXTRACTED_FROM_FILENAME_NEEDS_RUNTIME_EXIT_CONFIRMATION"
        confirmed += 1
    else:
        hold_status = "UNKNOWN"
        warnings.append("hold parameter missing or zero")

    # delay semantics: filename gives delayX. Need scanner code to know bars/minutes, but param extracted.
    if src.delay >= 0:
        delay_status = "PARAM_EXTRACTED_FROM_FILENAME_NEEDS_SCANNER_SEMANTICS"
        confirmed += 1
    else:
        delay_status = "UNKNOWN"
        warnings.append("delay parameter missing")

    # h semantics: try hour/session columns; otherwise unknown.
    h_cols = []
    for cand in [combined, session]:
        if cand and cand.hour_cols:
            h_cols.extend(cand.hour_cols)
    h_cols = sorted(set(h_cols))
    if h_cols:
        h_status = "HAS_HOUR_OR_SESSION_COLUMNS_NEEDS_VALUE_CHECK"
        confirmed += 1
    else:
        h_status = "PARAM_EXTRACTED_BUT_SEMANTICS_UNKNOWN"
        warnings.append("h parameter semantics not confirmed; no hour/session column detected")

    return ParamValidation(
        variant_key=variant_key,
        m_param=src.m,
        m_semantics_status=m_status,
        m_observed_min_signal_ret60_bps=sig_min,
        m_observed_max_signal_ret60_bps=sig_max,
        m_rule_hypothesis=m_rule,
        extra_param=src.extra,
        extra_semantics_status=extra_status,
        observed_extra_slip_bps_values=extra_vals,
        hold_param=src.hold,
        hold_semantics_status=hold_status,
        delay_param=src.delay,
        delay_semantics_status=delay_status,
        h_param=src.h,
        h_semantics_status=h_status,
        h_observed_columns=h_cols,
        confirmed_components=confirmed,
        total_components=total,
        warnings=warnings,
    )


def variant_score(total: float, avg: float, pf: float, wr: float, trades: int, symbols: int, confirmed: int, total_components: int) -> float:
    # Robust ranking: total pnl dominates, then PF/WR/breadth/trades/semantic confirmation.
    pf_capped = min(max(pf, 0.0), 20.0)
    confirmation_ratio = confirmed / max(1, total_components)
    return round(
        max(total, -1000000.0)
        + max(avg, -1000000.0) * 100.0
        + pf_capped * 50.0
        + wr * 100.0
        + min(symbols, 250) * 2.0
        + min(trades, 5000) * 0.03
        + confirmation_ratio * 100.0,
        8,
    )


def build_variants(artifacts: List[ArtifactData]) -> Tuple[List[VariantV2], List[ParamValidation]]:
    by: Dict[str, List[ArtifactData]] = {}
    for a in artifacts:
        by.setdefault(a.variant_key, []).append(a)

    variants: List[VariantV2] = []
    validations: List[ParamValidation] = []
    for key, rows in by.items():
        combined = next((r for r in rows if r.artifact_type == "combined_sim_session_first"), None)
        session = next((r for r in rows if r.artifact_type == "session_trades"), None)
        metric = combined or session or rows[0]
        val = validate_params(key, metric, combined, session)
        validations.append(val)

        # Prefer combined pnl. If no combined pnl, fallback to session ret/pnl.
        rank_status = ""
        if metric.pnl_col == "pnl" and metric.total_pnl > 0 and metric.profit_factor >= 1.05:
            rank_status = "SELECTABLE_POSITIVE_PNL"
        elif metric.total_pnl > 0 and metric.profit_factor >= 1.05:
            rank_status = "SELECTABLE_POSITIVE_METRIC_PROXY"
        elif metric.total_pnl > 0:
            rank_status = "POSITIVE_BUT_WEAK_PF"
        else:
            rank_status = "WEAK_OR_NEGATIVE_METRICS"

        score = variant_score(metric.total_pnl, metric.avg_pnl, metric.profit_factor, metric.win_rate, metric.trade_count, metric.symbol_count, val.confirmed_components, val.total_components)
        worst = best = med = 0.0
        try:
            df = pd.read_csv(metric.path)
            col = metric.pnl_col or metric.ret_col
            if col and col in df.columns:
                s = pd.to_numeric(df[col], errors="coerce").dropna()
                if not s.empty:
                    worst = float(s.min())
                    best = float(s.max())
                    med = float(s.median())
        except Exception:
            pass

        warnings: List[str] = []
        for r in rows:
            warnings.extend(r.warnings)
        warnings.extend(val.warnings)
        variants.append(VariantV2(
            variant_key=key,
            candidate_key=metric.variant_key.split("_h")[0],
            h=metric.h,
            m=metric.m,
            hold=metric.hold,
            delay=metric.delay,
            extra=metric.extra,
            combined_path=combined.path if combined else None,
            session_path=session.path if session else None,
            metric_source=metric.artifact_type,
            pnl_col=metric.pnl_col,
            ret_col=metric.ret_col,
            trade_count=metric.trade_count,
            symbol_count=metric.symbol_count,
            total_pnl=metric.total_pnl,
            avg_pnl=metric.avg_pnl,
            profit_factor=metric.profit_factor,
            win_rate=metric.win_rate,
            worst_pnl=round(worst, 8),
            best_pnl=round(best, 8),
            median_pnl=round(med, 8),
            score=score,
            rank_status=rank_status,
            param_validation_status=f"{val.confirmed_components}/{val.total_components}",
            confirmed_components=val.confirmed_components,
            total_components=val.total_components,
            warnings=warnings,
        ))

    variants.sort(key=lambda v: (v.rank_status not in {"SELECTABLE_POSITIVE_PNL", "SELECTABLE_POSITIVE_METRIC_PROXY"}, -v.score, -v.total_pnl, -v.symbol_count))
    return variants, validations


def build_contract(candidate: str, variants: List[VariantV2], validations: List[ParamValidation]) -> RuleContractV2:
    reasons: List[str] = []
    blockers: List[str] = []
    warnings: List[str] = []

    selected = next((v for v in variants if v.rank_status == "SELECTABLE_POSITIVE_PNL"), None)
    if not selected:
        selected = next((v for v in variants if v.rank_status == "SELECTABLE_POSITIVE_METRIC_PROXY"), None)
    if not selected and variants:
        selected = variants[0]

    val = next((x for x in validations if selected and x.variant_key == selected.variant_key), None)

    if selected and val:
        reasons.append("best variant selected using combined_sim pnl-aware ranking")
        if val.m_semantics_status == "CONFIRMED_AS_MIN_SIGNAL_RET60_BPS_THRESHOLD":
            reasons.append("m parameter confirmed against signal_ret60_bps minimum")
        else:
            blockers.append("m parameter threshold semantics not fully confirmed")
        if val.extra_semantics_status == "CONFIRMED_AS_EXTRA_SLIP_BPS" or val.extra_semantics_status == "ASSUMED_ZERO_EXTRA_SLIP_NO_COLUMN_VALUES":
            reasons.append("extra parameter mapped to extra_slip_bps or zero-slip assumption")
        else:
            blockers.append("extra parameter semantics not fully confirmed")
        if "UNKNOWN" in val.h_semantics_status:
            blockers.append("h parameter semantics still unknown; likely session/hour filter but not proven")
        else:
            warnings.append("h parameter has candidate hour/session columns but value semantics still need scanner confirmation")
        blockers.append("delay semantics need scanner confirmation before runtime")
        blockers.append("hold exit implementation must be matched exactly before runtime")

        # We allow next-stage logger blueprint only if m + extra + metric are confirmed enough, not runtime.
        enough_for_blueprint = (
            selected.rank_status == "SELECTABLE_POSITIVE_PNL"
            and val.m_semantics_status == "CONFIRMED_AS_MIN_SIGNAL_RET60_BPS_THRESHOLD"
            and val.confirmed_components >= 3
        )
        if enough_for_blueprint:
            contract_status = "RULE_CONTRACT_READY_FOR_LOGGER_BLUEPRINT_NOT_RUNTIME"
            logger_build_allowed = False
            reasons.append("contract is strong enough for blueprint generation, but not runtime logger execution")
        else:
            contract_status = "RULE_CONTRACT_PARTIAL_NEEDS_SCANNER_SEMANTICS"
            logger_build_allowed = False
    else:
        contract_status = "RULE_CONTRACT_BLOCKED_NO_VARIANT"
        logger_build_allowed = False
        blockers.append("no variant available")

    if selected:
        entry_rule = f"candidate={candidate}; side=short; signal_ret60_bps >= {selected.m}; h={selected.h}; delay={selected.delay}; extra_slip_bps={selected.extra}"
        exit_rule = f"fixed_hold_{selected.hold}_minutes_or_bars_NEEDS_CONFIRMATION"
        cost_rule = "cost_bps from artifact, usually 25 bps; extra_slip_bps from filename extra param"
    else:
        entry_rule = "UNKNOWN"
        exit_rule = "UNKNOWN"
        cost_rule = "UNKNOWN"

    return RuleContractV2(
        candidate_key=candidate,
        contract_status=contract_status,
        selected_variant_key=selected.variant_key if selected else None,
        selected_metric_source=selected.metric_source if selected else None,
        selected_artifact_path=selected.combined_path or selected.session_path if selected else None,
        side="short",
        rule_family="ret60 reversal short",
        h_param=selected.h if selected else None,
        m_param=selected.m if selected else None,
        hold_minutes=selected.hold if selected else None,
        delay_minutes_or_bars=selected.delay if selected else None,
        extra_slip_bps=selected.extra if selected else None,
        entry_rule_hypothesis=entry_rule,
        exit_rule_hypothesis=exit_rule,
        cost_model_hypothesis=cost_rule,
        confirmed_components=selected.confirmed_components if selected else 0,
        total_components=selected.total_components if selected else 0,
        logger_build_allowed=logger_build_allowed,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
    )


def records_df(items: List[Any]) -> pd.DataFrame:
    rows = []
    for x in items:
        d = asdict(x)
        for k, v in list(d.items()):
            if isinstance(v, list):
                d[k] = " | ".join(str(i) for i in v)
        rows.append(d)
    return pd.DataFrame(rows)


def write_outputs(workspace: Path, out_dir: Path, state: ParserStateV2, contract: RuleContractV2, variants: List[VariantV2], validations: List[ParamValidation], artifacts: List[ArtifactData]) -> None:
    persistent = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes" / contract.candidate_key / "rule_artifacts_v2"
    persistent.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": asdict(state),
        "contract": asdict(contract),
        "variants": [asdict(v) for v in variants],
        "param_validations": [asdict(v) for v in validations],
        "artifacts": [asdict(a) for a in artifacts],
    }
    for d in [out_dir, persistent]:
        write_json(d / "ret60_rule_artifact_parser_v2_state.json", payload)
        write_json(d / "ret60_rule_contract_v2.json", {"contract": asdict(contract)})
        records_df(variants).to_csv(d / "ret60_variant_ranking_v2.csv", index=False)
        records_df(validations).to_csv(d / "ret60_param_validation_v2.csv", index=False)
        records_df(artifacts).to_csv(d / "ret60_artifact_inventory_v2.csv", index=False)

    md = f"""# Ret60 Rule Contract v2

Candidate: `{contract.candidate_key}`

Status: **{contract.contract_status}**

## Selected variant

- Variant: `{contract.selected_variant_key}`
- Metric source: `{contract.selected_metric_source}`
- Artifact: `{contract.selected_artifact_path}`
- Side: `{contract.side}`
- h_param: `{contract.h_param}`
- m_param: `{contract.m_param}`
- hold: `{contract.hold_minutes}`
- delay: `{contract.delay_minutes_or_bars}`
- extra_slip_bps: `{contract.extra_slip_bps}`

## Hypotheses

- Entry rule: `{contract.entry_rule_hypothesis}`
- Exit rule: `{contract.exit_rule_hypothesis}`
- Cost model: `{contract.cost_model_hypothesis}`

## Permissions

- Logger build allowed: `{contract.logger_build_allowed}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Reasons

```text
{chr(10).join(contract.reasons) if contract.reasons else 'none'}
```

## Blockers

```text
{chr(10).join(contract.blockers) if contract.blockers else 'none'}
```

## Interpretation

Parser v2 is PnL-aware and can rank variants. However, it still does not approve runtime.
The next safe step is a logger blueprint or scanner-semantic recovery, not active paper.
"""
    for d in [out_dir, persistent]:
        write_text(d / "ret60_rule_contract_v2.md", md)


def write_report(path: Path, state: ParserStateV2, contract: RuleContractV2, variants: List[VariantV2]) -> None:
    lines = [
        "# Edge Factory Ret60 Rule Artifact Parser v2 Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Parser status: **{state.parser_status}**",
        f"Contract status: **{contract.contract_status}**",
        f"Artifacts loaded: **{state.artifacts_loaded}**",
        f"Variants seen: **{state.variants_seen}**",
        f"Positive variants: **{state.positive_variants}**",
        f"Selected variant: `{contract.selected_variant_key}`",
        f"Logger build allowed: **{contract.logger_build_allowed}**",
        f"Live allowed: **{contract.live_allowed}**",
        "",
        "## Top variants",
        "",
    ]
    if variants:
        lines += ["| Score | Variant | Status | Total PnL | PF | WR | Trades | Symbols | Params confirmed |", "|---:|---|---|---:|---:|---:|---:|---:|---:|"]
        for v in variants[:40]:
            lines.append(f"| {v.score} | {v.variant_key} | {v.rank_status} | {v.total_pnl} | {v.profit_factor} | {v.win_rate} | {v.trade_count} | {v.symbol_count} | {v.param_validation_status} |")
    else:
        lines.append("No variants found.")
    lines += ["", "## Reasons", ""]
    for r in state.reasons:
        lines.append(f"- {r}")
    for r in contract.reasons:
        lines.append(f"- {r}")
    if contract.blockers:
        lines += ["", "## Blockers", ""]
        for b in contract.blockers:
            lines.append(f"- {b}")
    warnings = state.warnings + contract.warnings
    if warnings:
        lines += ["", "## Warnings", ""]
        for w in warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    write_text(path, "\n".join(lines))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ret60 PnL-aware rule artifact parser v2")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    p.add_argument("--artifact_dir", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    candidate = safe_key(args.candidate)
    artifact_dir = Path(args.artifact_dir) if args.artifact_dir else workspace / "session_top_exact_validator"
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_rule_artifact_parser_v2"
    out_dir = out_root / f"ret60_rule_artifacts_v2_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    warnings: List[str] = []
    if not artifact_dir.exists():
        paths: List[Path] = []
        warnings.append(f"artifact dir does not exist: {artifact_dir}")
    else:
        paths = sorted(artifact_dir.glob(f"*{candidate}*.csv"))

    artifacts = [a for a in (read_artifact(p) for p in paths) if a is not None]
    variants, validations = build_variants(artifacts)
    contract = build_contract(candidate, variants, validations)
    positive = len([v for v in variants if v.rank_status in {"SELECTABLE_POSITIVE_PNL", "SELECTABLE_POSITIVE_METRIC_PROXY", "POSITIVE_BUT_WEAK_PF"}])

    if variants and positive > 0:
        parser_status = "PNL_AWARE_VARIANTS_RANKED"
    elif variants:
        parser_status = "VARIANTS_PARSED_BUT_NO_POSITIVE_METRIC"
    else:
        parser_status = "NO_VARIANTS_PARSED"

    state = ParserStateV2(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        artifact_dir=str(artifact_dir),
        candidate=candidate,
        artifacts_seen=len(paths),
        artifacts_loaded=len([a for a in artifacts if a.rows > 0]),
        variants_seen=len(variants),
        positive_variants=positive,
        selected_variant=contract.selected_variant_key,
        parser_status=parser_status,
        contract_status=contract.contract_status,
        logger_build_allowed=contract.logger_build_allowed,
        shadow_start_allowed=contract.shadow_start_allowed,
        active_paper_allowed=contract.active_paper_allowed,
        live_allowed=False,
        reasons=[
            "Parser v2 used combined_sim pnl-aware ranking.",
            "Parameter validation was performed against signal_ret60_bps and extra_slip_bps where possible.",
        ],
        warnings=warnings,
        hard_rules=[
            "Ret60 parser v2 never starts paper/live.",
            "Ret60 parser v2 never mutates active config.",
            "Ret60 parser v2 never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Runtime remains blocked until scanner semantics and preflight are complete.",
            "Live remains blocked.",
        ],
    )

    write_outputs(workspace, out_dir, state, contract, variants, validations, artifacts)
    write_report(out_dir / "ret60_rule_artifact_parser_v2_report.md", state, contract, variants)

    print("EDGE FACTORY RET60 RULE ARTIFACT PARSER v2")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"artifact_dir: {artifact_dir}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"parser_status: {state.parser_status}")
    print(f"contract_status: {contract.contract_status}")
    print(f"artifacts_seen: {state.artifacts_seen}")
    print(f"artifacts_loaded: {state.artifacts_loaded}")
    print(f"variants_seen: {state.variants_seen}")
    print(f"positive_variants: {state.positive_variants}")
    print(f"selected_variant: {contract.selected_variant_key}")
    print(f"selected_artifact: {contract.selected_artifact_path}")
    print(f"entry_rule_hypothesis: {contract.entry_rule_hypothesis}")
    print(f"exit_rule_hypothesis: {contract.exit_rule_hypothesis}")
    print(f"logger_build_allowed: {contract.logger_build_allowed}")
    print(f"shadow_start_allowed: {contract.shadow_start_allowed}")
    print(f"active_paper_allowed: {contract.active_paper_allowed}")
    print("live_allowed: False")
    print("")
    print("TOP VARIANTS")
    print("-" * 100)
    for v in variants[:20]:
        print(f"score={v.score:12.4f} {v.variant_key:70s} status={v.rank_status:30s} total={v.total_pnl: .4f} avg={v.avg_pnl: .6f} pf={v.profit_factor:.3f} wr={v.win_rate:.2%} trades={v.trade_count:5d} symbols={v.symbol_count:4d} params={v.param_validation_status}")
    if contract.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in contract.blockers:
            print(f"- {b}")
    if state.warnings or contract.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings + contract.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'ret60_rule_artifact_parser_v2_report.md'}")
    print(f"State  : {out_dir / 'ret60_rule_artifact_parser_v2_state.json'}")
    print(f"Variants: {out_dir / 'ret60_variant_ranking_v2.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
