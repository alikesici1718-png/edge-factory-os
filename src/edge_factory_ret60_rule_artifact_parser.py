#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 RULE ARTIFACT PARSER v1
==========================================

Purpose
-------
Parse ret60_reversal_short exact-validator artifacts found by original scanner locator.

The locator found strong candidate artifacts under:
    <workspace>\session_top_exact_validator\
        combined_sim_session_first_ret60_reversal_short_h8_m75_hold720_delay10_extra100.csv
        session_trades_ret60_reversal_short_h8_m75_hold720_delay10_extra100.csv
        ...

This parser extracts:
    - filename rule parameters: h8, m75, hold720, delay10, extra100
    - CSV schema
    - trade-level metrics where possible
    - variant ranking
    - exact rule contract candidate

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
    - read session_top_exact_validator CSV artifacts
    - parse parameterized ret60 variants
    - compute simple metrics from session_trades files when columns permit
    - pair session_trades with combined_sim_session_first files
    - produce a rule contract candidate for future rule extractor v2 / sandbox logger

Run:
    python "C:\Users\alike\edge_factory_ret60_rule_artifact_parser.py"

Optional:
    python "C:\Users\alike\edge_factory_ret60_rule_artifact_parser.py" --candidate ret60_reversal_short

Core rule
---------
This is artifact parsing only. It cannot approve runtime by itself.
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

PNL_COLS = ["pnl", "net_pnl", "net_pnl_usdt", "pnl_usdt", "profit", "gross_pnl", "gross_pnl_usdt"]
SYMBOL_COLS = ["symbol", "inst_id", "instrument", "inst", "ticker", "coin"]
TIME_COLS = ["event_time", "entry_time", "exit_time", "timestamp", "time", "datetime", "date", "open_time", "close_time", "ts"]
SIDE_COLS = ["side", "direction", "position_side", "trade_side"]
RETURN_COLS = ["return_bps", "ret_bps", "return", "ret", "net_return_bps", "gross_return_bps"]

PARAM_RE = re.compile(
    r"(?P<prefix>combined_sim_session_first|session_trades)_(?P<candidate>ret60_reversal_short)_h(?P<h>\d+)_m(?P<m>\d+)_hold(?P<hold>\d+)_delay(?P<delay>\d+)_extra(?P<extra>\d+)\.csv$",
    re.IGNORECASE,
)


@dataclass
class ParsedParams:
    candidate_key: str
    artifact_type: str
    h_param: int
    m_param: int
    hold_param: int
    delay_param: int
    extra_param: int
    variant_key: str


@dataclass
class ArtifactRecord:
    path: str
    filename: str
    parsed: bool
    candidate_key: Optional[str]
    artifact_type: Optional[str]
    variant_key: Optional[str]
    h_param: Optional[int]
    m_param: Optional[int]
    hold_param: Optional[int]
    delay_param: Optional[int]
    extra_param: Optional[int]
    rows: int
    columns_count: int
    pnl_col: Optional[str]
    symbol_col: Optional[str]
    time_col: Optional[str]
    side_col: Optional[str]
    return_col: Optional[str]
    total_pnl: float
    avg_pnl: float
    profit_factor: float
    win_rate: float
    trade_count: int
    symbol_count: int
    side_distribution: str
    start_time: Optional[str]
    end_time: Optional[str]
    columns: str
    warnings: str


@dataclass
class VariantRecord:
    variant_key: str
    candidate_key: str
    h_param: int
    m_param: int
    hold_param: int
    delay_param: int
    extra_param: int
    has_session_trades: bool
    has_combined_sim: bool
    session_trades_path: Optional[str]
    combined_sim_path: Optional[str]
    trade_count: int
    symbol_count: int
    total_pnl: float
    avg_pnl: float
    profit_factor: float
    win_rate: float
    score: float
    rank_status: str
    rule_contract_status: str
    warnings: str


@dataclass
class RuleContractCandidate:
    candidate_key: str
    contract_status: str
    selected_variant_key: Optional[str]
    selected_artifact_path: Optional[str]
    inferred_side: str
    inferred_feature_family: str
    h_param: Optional[int]
    m_param: Optional[int]
    hold_minutes: Optional[int]
    delay_minutes_or_bars: Optional[int]
    extra_param: Optional[int]
    exact_threshold_semantics: str
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]


@dataclass
class ParserState:
    generated_at: str
    workspace: str
    artifact_dir: str
    candidate: str
    artifacts_seen: int
    artifacts_parsed: int
    variants_seen: int
    selectable_variants: int
    contract_status: str
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    overall_state: str
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


def find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): str(c) for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    for col in df.columns:
        low = str(col).lower()
        if candidates == TIME_COLS and any(tok in low for tok in ["time", "date", "timestamp", "datetime"]):
            return str(col)
        if candidates == SYMBOL_COLS and any(tok in low for tok in ["symbol", "inst", "ticker", "coin"]):
            return str(col)
        if candidates == PNL_COLS and any(tok in low for tok in ["pnl", "profit"]):
            return str(col)
        if candidates == SIDE_COLS and any(tok in low for tok in ["side", "direction"]):
            return str(col)
    return None


def parse_filename(path: Path) -> Optional[ParsedParams]:
    m = PARAM_RE.search(path.name)
    if not m:
        return None
    candidate = safe_key(m.group("candidate"))
    h = int(m.group("h"))
    mm = int(m.group("m"))
    hold = int(m.group("hold"))
    delay = int(m.group("delay"))
    extra = int(m.group("extra"))
    variant = f"{candidate}_h{h}_m{mm}_hold{hold}_delay{delay}_extra{extra}"
    return ParsedParams(
        candidate_key=candidate,
        artifact_type=m.group("prefix").lower(),
        h_param=h,
        m_param=mm,
        hold_param=hold,
        delay_param=delay,
        extra_param=extra,
        variant_key=variant,
    )


def profit_factor(pnl: pd.Series) -> float:
    if pnl.empty:
        return 0.0
    gains = float(pnl[pnl > 0].sum())
    losses = float((-pnl[pnl < 0]).sum())
    if losses <= 0:
        return 999999.0 if gains > 0 else 0.0
    return gains / losses


def parse_time_bounds(s: pd.Series) -> Tuple[Optional[str], Optional[str]]:
    if s.empty:
        return None, None
    num = pd.to_numeric(s, errors="coerce")
    try:
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
            ts = pd.to_datetime(num, unit=unit, errors="coerce", utc=True).dropna()
        else:
            ts = pd.to_datetime(s, errors="coerce", utc=True).dropna()
        if ts.empty:
            return None, None
        return ts.min().isoformat(), ts.max().isoformat()
    except Exception:
        return None, None


def read_artifact(path: Path, max_full_rows: int) -> ArtifactRecord:
    parsed = parse_filename(path)
    warnings: List[str] = []
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return ArtifactRecord(
            path=str(path), filename=path.name, parsed=bool(parsed), candidate_key=parsed.candidate_key if parsed else None,
            artifact_type=parsed.artifact_type if parsed else None, variant_key=parsed.variant_key if parsed else None,
            h_param=parsed.h_param if parsed else None, m_param=parsed.m_param if parsed else None,
            hold_param=parsed.hold_param if parsed else None, delay_param=parsed.delay_param if parsed else None,
            extra_param=parsed.extra_param if parsed else None, rows=0, columns_count=0, pnl_col=None,
            symbol_col=None, time_col=None, side_col=None, return_col=None, total_pnl=0.0, avg_pnl=0.0,
            profit_factor=0.0, win_rate=0.0, trade_count=0, symbol_count=0, side_distribution="",
            start_time=None, end_time=None, columns="", warnings=f"read failed: {e}"
        )
    if len(df) > max_full_rows:
        warnings.append(f"large file loaded rows={len(df)}; metrics computed on full file")

    pnl_col = find_col(df, PNL_COLS)
    symbol_col = find_col(df, SYMBOL_COLS)
    time_col = find_col(df, TIME_COLS)
    side_col = find_col(df, SIDE_COLS)
    return_col = find_col(df, RETURN_COLS)

    pnl = pd.Series(dtype=float)
    if pnl_col and pnl_col in df.columns:
        pnl = pd.to_numeric(df[pnl_col], errors="coerce").dropna()
    elif return_col and return_col in df.columns:
        # Do not pretend return is PnL; use as proxy only.
        pnl = pd.to_numeric(df[return_col], errors="coerce").dropna()
        warnings.append("using return column as pnl proxy because no pnl column found")
    else:
        warnings.append("no pnl/return column detected")

    symbol_count = 0
    if symbol_col and symbol_col in df.columns:
        symbol_count = int(df[symbol_col].dropna().astype(str).nunique())
    side_distribution = ""
    if side_col and side_col in df.columns:
        vc = df[side_col].dropna().astype(str).value_counts().head(10).to_dict()
        side_distribution = " | ".join(f"{k}:{v}" for k, v in vc.items())

    start_s = end_s = None
    if time_col and time_col in df.columns:
        start_s, end_s = parse_time_bounds(df[time_col])

    return ArtifactRecord(
        path=str(path),
        filename=path.name,
        parsed=bool(parsed),
        candidate_key=parsed.candidate_key if parsed else None,
        artifact_type=parsed.artifact_type if parsed else None,
        variant_key=parsed.variant_key if parsed else None,
        h_param=parsed.h_param if parsed else None,
        m_param=parsed.m_param if parsed else None,
        hold_param=parsed.hold_param if parsed else None,
        delay_param=parsed.delay_param if parsed else None,
        extra_param=parsed.extra_param if parsed else None,
        rows=int(len(df)),
        columns_count=int(len(df.columns)),
        pnl_col=pnl_col,
        symbol_col=symbol_col,
        time_col=time_col,
        side_col=side_col,
        return_col=return_col,
        total_pnl=round(float(pnl.sum()), 8) if not pnl.empty else 0.0,
        avg_pnl=round(float(pnl.mean()), 8) if not pnl.empty else 0.0,
        profit_factor=round(float(profit_factor(pnl)), 8) if not pnl.empty else 0.0,
        win_rate=round(float((pnl > 0).mean()), 6) if not pnl.empty else 0.0,
        trade_count=int(len(pnl)) if not pnl.empty else int(len(df)),
        symbol_count=symbol_count,
        side_distribution=side_distribution,
        start_time=start_s,
        end_time=end_s,
        columns=" | ".join(str(c) for c in df.columns),
        warnings=" | ".join(warnings),
    )


def discover_artifacts(workspace: Path, artifact_dir: Optional[str], candidate: str) -> Path:
    if artifact_dir:
        return Path(artifact_dir)
    p = workspace / "session_top_exact_validator"
    return p


def variant_score(rec: ArtifactRecord) -> float:
    score = 0.0
    score += max(0.0, rec.total_pnl)
    score += max(0.0, rec.avg_pnl) * 100.0
    score += min(max(0.0, rec.profit_factor), 100.0) * 10.0
    score += rec.win_rate * 50.0
    score += min(rec.symbol_count, 200) * 2.0
    score += min(rec.trade_count, 5000) * 0.02
    return round(score, 8)


def build_variants(records: List[ArtifactRecord]) -> List[VariantRecord]:
    by: Dict[str, List[ArtifactRecord]] = {}
    for r in records:
        if r.parsed and r.variant_key:
            by.setdefault(r.variant_key, []).append(r)
    variants: List[VariantRecord] = []
    for key, rows in by.items():
        session = next((r for r in rows if r.artifact_type == "session_trades"), None)
        combined = next((r for r in rows if r.artifact_type == "combined_sim_session_first"), None)
        metric_source = session or combined or rows[0]
        score = variant_score(metric_source)
        if metric_source.trade_count <= 0:
            rank_status = "NO_TRADE_METRICS"
        elif metric_source.total_pnl > 0 and metric_source.profit_factor >= 1.05:
            rank_status = "SELECTABLE_METRIC_POSITIVE"
        else:
            rank_status = "WEAK_METRICS"
        rule_status = "PARAMS_EXTRACTED_NEEDS_SEMANTIC_CONFIRMATION"
        variants.append(VariantRecord(
            variant_key=key,
            candidate_key=str(metric_source.candidate_key),
            h_param=int(metric_source.h_param or 0),
            m_param=int(metric_source.m_param or 0),
            hold_param=int(metric_source.hold_param or 0),
            delay_param=int(metric_source.delay_param or 0),
            extra_param=int(metric_source.extra_param or 0),
            has_session_trades=session is not None,
            has_combined_sim=combined is not None,
            session_trades_path=session.path if session else None,
            combined_sim_path=combined.path if combined else None,
            trade_count=int(metric_source.trade_count),
            symbol_count=int(metric_source.symbol_count),
            total_pnl=float(metric_source.total_pnl),
            avg_pnl=float(metric_source.avg_pnl),
            profit_factor=float(metric_source.profit_factor),
            win_rate=float(metric_source.win_rate),
            score=score,
            rank_status=rank_status,
            rule_contract_status=rule_status,
            warnings=" | ".join([r.warnings for r in rows if r.warnings]),
        ))
    variants.sort(key=lambda v: (v.rank_status != "SELECTABLE_METRIC_POSITIVE", -v.score, -v.symbol_count, -v.trade_count))
    return variants


def infer_contract(candidate: str, variants: List[VariantRecord]) -> RuleContractCandidate:
    reasons: List[str] = []
    warnings: List[str] = []
    blockers: List[str] = []
    selected = next((v for v in variants if v.rank_status == "SELECTABLE_METRIC_POSITIVE" and v.has_session_trades), None)
    if not selected:
        selected = variants[0] if variants else None

    if selected:
        reasons.append("filename parameters were extracted from exact-validator artifact")
        if selected.has_session_trades:
            reasons.append("session_trades artifact exists for selected variant")
        else:
            warnings.append("selected variant has no session_trades artifact")
        contract_status = "RULE_PARAMS_EXTRACTED_SEMANTICS_PARTIAL"
        blockers.append("m_param semantics must be confirmed from original scanner code")
        blockers.append("h_param semantics must be confirmed from original scanner code")
        blockers.append("delay/extra semantics must be confirmed before runtime")
        logger_allowed = False
    else:
        contract_status = "RULE_PARAMS_NOT_FOUND"
        blockers.append("no parseable ret60 exact-validator artifacts found")
        logger_allowed = False

    return RuleContractCandidate(
        candidate_key=safe_key(candidate),
        contract_status=contract_status,
        selected_variant_key=selected.variant_key if selected else None,
        selected_artifact_path=selected.session_trades_path or selected.combined_sim_path if selected else None,
        inferred_side="short",
        inferred_feature_family="ret60_reversal_short / 60m return reversal",
        h_param=selected.h_param if selected else None,
        m_param=selected.m_param if selected else None,
        hold_minutes=selected.hold_param if selected else None,
        delay_minutes_or_bars=selected.delay_param if selected else None,
        extra_param=selected.extra_param if selected else None,
        exact_threshold_semantics="UNKNOWN_PARAM_M_SEMANTICS_NEEDS_SCANNER_CODE",
        logger_build_allowed=logger_allowed,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
    )


def records_df(records: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(r) for r in records])


def write_contract_outputs(workspace: Path, out_dir: Path, contract: RuleContractCandidate, variants: List[VariantRecord], records: List[ArtifactRecord]) -> None:
    persistent = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes" / contract.candidate_key / "rule_artifacts"
    persistent.mkdir(parents=True, exist_ok=True)

    payload = {
        "contract": asdict(contract),
        "variants": [asdict(v) for v in variants],
        "artifacts": [asdict(r) for r in records],
        "permissions": {
            "logger_build_allowed": contract.logger_build_allowed,
            "shadow_start_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "mutates_active_config": False,
        },
    }
    for d in [out_dir, persistent]:
        write_json(d / "ret60_rule_artifact_contract.json", payload)
        records_df(variants).to_csv(d / "ret60_variant_ranking.csv", index=False)
        records_df(records).to_csv(d / "ret60_artifact_inventory.csv", index=False)

    md = f"""# Ret60 Rule Artifact Contract

Candidate: `{contract.candidate_key}`

Status: **{contract.contract_status}**

## Selected variant

- Variant: `{contract.selected_variant_key}`
- Artifact: `{contract.selected_artifact_path}`
- Side: `{contract.inferred_side}`
- Feature family: `{contract.inferred_feature_family}`
- h_param: `{contract.h_param}`
- m_param: `{contract.m_param}`
- hold_minutes: `{contract.hold_minutes}`
- delay_minutes_or_bars: `{contract.delay_minutes_or_bars}`
- extra_param: `{contract.extra_param}`
- Threshold semantics: `{contract.exact_threshold_semantics}`

## Permissions

- Logger build allowed: `{contract.logger_build_allowed}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Blockers

```text
{chr(10).join(contract.blockers) if contract.blockers else 'none'}
```

## Interpretation

Filename parameters are now extracted, but semantic meaning is still partial.
Do not build a runtime logger until `h`, `m`, `delay`, and `extra` semantics are confirmed from original scanner code.
"""
    for d in [out_dir, persistent]:
        write_text(d / "ret60_rule_artifact_contract.md", md)


def write_report(path: Path, state: ParserState, contract: RuleContractCandidate, variants: List[VariantRecord]) -> None:
    lines = [
        "# Edge Factory Ret60 Rule Artifact Parser Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall state: **{state.overall_state}**",
        f"Artifact dir: `{state.artifact_dir}`",
        f"Artifacts seen: **{state.artifacts_seen}**",
        f"Artifacts parsed: **{state.artifacts_parsed}**",
        f"Variants seen: **{state.variants_seen}**",
        f"Selectable variants: **{state.selectable_variants}**",
        f"Contract status: **{contract.contract_status}**",
        f"Selected variant: `{contract.selected_variant_key}`",
        f"Logger build allowed: **{contract.logger_build_allowed}**",
        f"Live allowed: **{contract.live_allowed}**",
        "",
        "## Top variants",
        "",
    ]
    if variants:
        lines += ["| Score | Variant | Rank status | Trades | Symbols | Total | PF | WR |", "|---:|---|---|---:|---:|---:|---:|---:|"]
        for v in variants[:30]:
            lines.append(f"| {v.score} | {v.variant_key} | {v.rank_status} | {v.trade_count} | {v.symbol_count} | {v.total_pnl} | {v.profit_factor} | {v.win_rate} |")
    else:
        lines.append("No variants parsed.")
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
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Parse ret60 rule artifacts from session_top_exact_validator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    p.add_argument("--artifact_dir", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--max_full_rows", type=int, default=2_000_000)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    candidate = safe_key(args.candidate)
    stamp = now_stamp()
    artifact_dir = discover_artifacts(workspace, args.artifact_dir, candidate)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_rule_artifact_parser"
    out_dir = out_root / f"ret60_rule_artifacts_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    warnings: List[str] = []
    paths: List[Path] = []
    if artifact_dir.exists():
        paths = sorted(artifact_dir.glob(f"*{candidate}*.csv"))
    else:
        warnings.append(f"artifact dir does not exist: {artifact_dir}")

    records = [read_artifact(p, int(args.max_full_rows)) for p in paths]
    parsed_records = [r for r in records if r.parsed]
    variants = build_variants(parsed_records)
    contract = infer_contract(candidate, variants)
    selectable = len([v for v in variants if v.rank_status == "SELECTABLE_METRIC_POSITIVE"])

    if contract.contract_status == "RULE_PARAMS_EXTRACTED_SEMANTICS_PARTIAL":
        overall = "RULE_PARAMS_EXTRACTED_NEEDS_SCANNER_SEMANTICS"
    elif records:
        overall = "ARTIFACTS_FOUND_BUT_RULE_PARAMS_NOT_EXTRACTED"
    else:
        overall = "NO_RET60_ARTIFACTS_FOUND"

    state = ParserState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        artifact_dir=str(artifact_dir),
        candidate=candidate,
        artifacts_seen=len(records),
        artifacts_parsed=len(parsed_records),
        variants_seen=len(variants),
        selectable_variants=selectable,
        contract_status=contract.contract_status,
        logger_build_allowed=contract.logger_build_allowed,
        shadow_start_allowed=contract.shadow_start_allowed,
        active_paper_allowed=contract.active_paper_allowed,
        live_allowed=False,
        overall_state=overall,
        reasons=[
            "Ret60 exact-validator artifacts were parsed offline.",
            "Filename parameters are evidence but not sufficient for runtime semantics.",
        ],
        warnings=warnings,
        hard_rules=[
            "Ret60 artifact parser never starts paper/live.",
            "Ret60 artifact parser never mutates active config.",
            "Ret60 artifact parser never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Logger build remains blocked until parameter semantics are confirmed.",
            "Live remains blocked.",
        ],
    )

    state_path = out_dir / "ret60_rule_artifact_parser_state.json"
    write_json(state_path, {"state": asdict(state), "contract": asdict(contract), "variants": [asdict(v) for v in variants], "artifacts": [asdict(r) for r in records]})
    records_df(records).to_csv(out_dir / "ret60_artifact_inventory.csv", index=False)
    records_df(variants).to_csv(out_dir / "ret60_variant_ranking.csv", index=False)
    write_contract_outputs(workspace, out_dir, contract, variants, records)
    write_report(out_dir / "ret60_rule_artifact_parser_report.md", state, contract, variants)

    print("EDGE FACTORY RET60 RULE ARTIFACT PARSER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"artifact_dir: {artifact_dir}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"overall_state: {state.overall_state}")
    print(f"artifacts_seen: {state.artifacts_seen}")
    print(f"artifacts_parsed: {state.artifacts_parsed}")
    print(f"variants_seen: {state.variants_seen}")
    print(f"selectable_variants: {state.selectable_variants}")
    print(f"contract_status: {contract.contract_status}")
    print(f"selected_variant: {contract.selected_variant_key}")
    print(f"selected_artifact: {contract.selected_artifact_path}")
    print(f"params: h={contract.h_param} m={contract.m_param} hold={contract.hold_minutes} delay={contract.delay_minutes_or_bars} extra={contract.extra_param}")
    print(f"logger_build_allowed: {contract.logger_build_allowed}")
    print(f"shadow_start_allowed: {contract.shadow_start_allowed}")
    print(f"active_paper_allowed: {contract.active_paper_allowed}")
    print("live_allowed: False")
    print("")
    print("TOP VARIANTS")
    print("-" * 100)
    for v in variants[:15]:
        print(f"score={v.score:12.4f} {v.variant_key:70s} status={v.rank_status:28s} trades={v.trade_count:6d} symbols={v.symbol_count:4d} total={v.total_pnl: .4f} pf={v.profit_factor:.3f} wr={v.win_rate:.2%}")
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
    print(f"Report : {out_dir / 'ret60_rule_artifact_parser_report.md'}")
    print(f"State  : {state_path}")
    print(f"Variants: {out_dir / 'ret60_variant_ranking.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
