#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY NATIVE BPS VALIDATOR v1
====================================

Purpose
-------
Offline data-quality / execution-quality validator for the Edge Factory OS.

This module addresses the preflight warning:
    estimated_bps_warning

The execution realism checker passed, but some family bps values were estimated from row
notional or proposed notional instead of native trade return_bps. That is acceptable for
paper-readiness, but not enough for live-readiness.

This module answers:
    1) Which families have native return_bps coverage?
    2) Which families rely on pnl/notional bps approximation?
    3) Which families rely on proposed-notional approximation?
    4) Does the current data quality allow paper preflight?
    5) Does the current data quality allow live?  Always NO at this stage.

It does NOT start paper/live trading.
It does NOT place orders.
It does NOT edit contract/logger files.

Run:
    python "C:\Users\alike\edge_factory_native_bps_validator.py"

Outputs:
    <workspace>\edge_factory_native_bps_validator\native_bps_YYYYMMDD_HHMMSS\
        native_bps_validation_report.md
        native_bps_validation.json
        native_bps_family_summary.csv
        native_bps_source_columns.csv
        native_bps_actions.json

Interpretation
--------------
PASS_FOR_PAPER means: paper can be used to gather native evidence.
PASS_FOR_LIVE is intentionally unreachable here unless a future paper/native source exists.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
KNOWN_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short", "session_short"]
ACTIVE_FAMILIES = ["old_short", "impulse_long", "market_relative_short", "weak_market_short"]

NATIVE_BPS_CANDIDATES = [
    "return_bps", "ret_bps", "net_bps", "gross_bps", "pnl_bps", "edge_bps",
    "return_after_fee_bps", "net_return_bps", "bps"
]
PNL_CANDIDATES = [
    "net_pnl", "net_pnl_usdt", "pnl_usdt", "pnl", "realized_pnl", "closed_pnl",
    "profit", "profit_usdt", "net_profit", "return_usdt", "ret_usdt", "trade_pnl", "pnl_after_fee"
]
NOTIONAL_CANDIDATES = [
    "notional", "notional_usdt", "entry_notional", "position_notional", "trade_notional", "size_usdt"
]
FAMILY_CANDIDATES = ["family_key", "family", "strategy_family", "strategy", "strategy_name", "system", "label"]
SYMBOL_CANDIDATES = ["symbol", "inst_id", "instrument", "coin", "ticker", "market", "asset"]


@dataclass
class FamilyBpsQuality:
    family_key: str
    proposed_notional: float
    trade_count: int
    native_bps_count: int
    row_notional_bps_count: int
    proposed_notional_bps_count: int
    no_bps_basis_count: int
    native_bps_coverage: float
    row_notional_coverage: float
    proposed_notional_coverage: float
    bps_quality_tier: str
    paper_gate: str
    live_gate: str
    gross_avg_bps_best_available: float
    gross_median_bps_best_available: float
    best_available_source: str
    reasons: List[str]


@dataclass
class SourceColumnAudit:
    source_file: str
    exists: bool
    readable: bool
    row_count: int
    columns: List[str]
    has_native_bps_col: bool
    native_bps_cols: List[str]
    has_pnl_col: bool
    pnl_cols: List[str]
    has_notional_col: bool
    notional_cols: List[str]
    inferred_family_hint: str


@dataclass
class NativeBpsAction:
    action_key: str
    family_key: str
    severity: str
    title: str
    reason: str
    safe_offline: bool
    suggested_next_module: str
    inputs: List[str]
    outputs: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def norm_col(x: Any) -> str:
    import re
    s = str(x).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        if isinstance(x, str):
            s = x.strip().lower()
            if s in {"", "none", "null", "nan", "inf", "infinity"}:
                return default
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except Exception:
        return default


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def find_cols(cols: Sequence[str], candidates: Sequence[str]) -> List[str]:
    norm_map = {norm_col(c): c for c in cols}
    found: List[str] = []
    for cand in candidates:
        key = norm_col(cand)
        if key in norm_map and norm_map[key] not in found:
            found.append(norm_map[key])
    return found


def infer_family_from_path(path: str) -> str:
    s = str(path).lower().replace("-", "_")
    for fam in KNOWN_FAMILIES:
        if fam in s:
            return fam
    if "impulse" in s and "long" in s:
        return "impulse_long"
    if "market" in s and "relative" in s:
        return "market_relative_short"
    if "weak" in s and "market" in s:
        return "weak_market_short"
    if "old" in s and "short" in s:
        return "old_short"
    return "unknown"


def discover_artifacts(workspace: Path) -> Dict[str, Optional[Path]]:
    roots = {
        "execution_dir": (workspace / "edge_factory_execution_realism_checker", "execution_realism_"),
        "capital_dir": (workspace / "edge_factory_adaptive_capital_governor_v2", "capital_governor_"),
        "rolling_oos_dir": (workspace / "edge_factory_rolling_oos_validator", "rolling_oos_"),
        "preflight_dir": (workspace / "edge_factory_os_preflight", "preflight_"),
    }
    out: Dict[str, Optional[Path]] = {}
    for key, (root, prefix) in roots.items():
        out[key] = latest_child_dir(root, prefix)
    return out


def load_capital_notional_map(capital_dir: Optional[Path]) -> Dict[str, float]:
    if not capital_dir:
        return {}
    p = capital_dir / "capital_policy_proposal.json"
    if not p.exists():
        return {}
    obj = load_json(p)
    rows = obj.get("family_decisions") if isinstance(obj, dict) else []
    out: Dict[str, float] = {}
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict) and r.get("family_key"):
                out[str(r["family_key"])] = safe_float(r.get("proposed_notional"), 0.0)
    return out


def load_normalized_trades(rolling_oos_dir: Optional[Path]) -> Tuple[pd.DataFrame, Optional[Path]]:
    if not rolling_oos_dir:
        return pd.DataFrame(), None
    p = rolling_oos_dir / "normalized_oos_trades.csv"
    if not p.exists():
        return pd.DataFrame(), p
    df = pd.read_csv(p)
    for col in ["family_key", "symbol", "pnl", "return_bps", "notional", "source_file", "source_row"]:
        if col not in df.columns:
            df[col] = np.nan
    df["family_key"] = df["family_key"].astype(str)
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")
    df["return_bps"] = pd.to_numeric(df["return_bps"], errors="coerce")
    df["notional"] = pd.to_numeric(df["notional"], errors="coerce")
    return df, p


def audit_source_file(path_str: str) -> SourceColumnAudit:
    path = Path(path_str)
    if not path.exists():
        return SourceColumnAudit(path_str, False, False, 0, [], False, [], False, [], False, [], infer_family_from_path(path_str))
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, nrows=5)
            row_count = sum(1 for _ in open(path, "rb")) - 1 if path.exists() else 0
        elif path.suffix.lower() in {".parquet", ".pq"}:
            df = pd.read_parquet(path)
            row_count = len(df)
            df = df.head(5)
        elif path.suffix.lower() in {".json", ".jsonl"}:
            # We do a lightweight best effort only.
            if path.suffix.lower() == ".jsonl":
                df = pd.read_json(path, lines=True, nrows=5)
            else:
                obj = load_json(path)
                if isinstance(obj, list):
                    df = pd.DataFrame(obj[:5])
                    row_count = len(obj)
                elif isinstance(obj, dict):
                    rows = None
                    for key in ["trades", "rows", "records", "data", "results"]:
                        if isinstance(obj.get(key), list):
                            rows = obj[key]
                            break
                    if rows is not None:
                        df = pd.DataFrame(rows[:5])
                        row_count = len(rows)
                    else:
                        df = pd.DataFrame([obj])
                        row_count = 1
                else:
                    df = pd.DataFrame()
                    row_count = 0
        else:
            df = pd.DataFrame()
            row_count = 0
        cols = list(df.columns)
        native = find_cols(cols, NATIVE_BPS_CANDIDATES)
        pnl = find_cols(cols, PNL_CANDIDATES)
        notional = find_cols(cols, NOTIONAL_CANDIDATES)
        return SourceColumnAudit(
            source_file=path_str,
            exists=True,
            readable=True,
            row_count=int(row_count) if 'row_count' in locals() else 0,
            columns=[str(c) for c in cols],
            has_native_bps_col=bool(native),
            native_bps_cols=native,
            has_pnl_col=bool(pnl),
            pnl_cols=pnl,
            has_notional_col=bool(notional),
            notional_cols=notional,
            inferred_family_hint=infer_family_from_path(path_str),
        )
    except Exception:
        return SourceColumnAudit(path_str, True, False, 0, [], False, [], False, [], False, [], infer_family_from_path(path_str))


def audit_sources(df: pd.DataFrame, max_files: int = 200) -> List[SourceColumnAudit]:
    if df.empty or "source_file" not in df.columns:
        return []
    files = [str(x) for x in df["source_file"].dropna().astype(str).unique().tolist()]
    # prioritize source files tied to known families
    files = sorted(files, key=lambda p: (infer_family_from_path(p) == "unknown", p))[:max_files]
    return [audit_source_file(p) for p in files]


def family_quality(df: pd.DataFrame, family_key: str, proposed_notional: float, source_audits: List[SourceColumnAudit]) -> FamilyBpsQuality:
    g = df[df["family_key"] == family_key].copy() if not df.empty else pd.DataFrame()
    if proposed_notional <= 0:
        return FamilyBpsQuality(
            family_key, proposed_notional, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0,
            "ZERO_NOTIONAL", "BLOCKED_ZERO_NOTIONAL", "LIVE_BLOCKED", 0.0, 0.0,
            "NONE", ["Family has zero proposed notional or is disabled."]
        )
    if g.empty:
        return FamilyBpsQuality(
            family_key, proposed_notional, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0,
            "NO_DATA", "PAPER_BLOCKED_NO_DATA", "LIVE_BLOCKED", 0.0, 0.0,
            "NONE", ["No normalized OOS rows found for this family."]
        )

    n = int(len(g))
    native_count = int(g["return_bps"].notna().sum())
    row_notional_count = int((g["return_bps"].isna() & g["pnl"].notna() & g["notional"].notna() & (g["notional"].abs() > 1e-12)).sum())
    proposed_count = int((g["return_bps"].isna() & g["pnl"].notna() & ~(g["notional"].notna() & (g["notional"].abs() > 1e-12))).sum())
    no_basis_count = n - native_count - row_notional_count - proposed_count

    native_cov = native_count / max(1, n)
    row_cov = row_notional_count / max(1, n)
    prop_cov = proposed_count / max(1, n)

    # Best available bps series.
    g["best_bps"] = np.nan
    g.loc[g["return_bps"].notna(), "best_bps"] = g.loc[g["return_bps"].notna(), "return_bps"]
    mask_row = g["best_bps"].isna() & g["pnl"].notna() & g["notional"].notna() & (g["notional"].abs() > 1e-12)
    g.loc[mask_row, "best_bps"] = g.loc[mask_row, "pnl"] / g.loc[mask_row, "notional"].abs() * 10000.0
    mask_prop = g["best_bps"].isna() & g["pnl"].notna() & (proposed_notional > 0)
    g.loc[mask_prop, "best_bps"] = g.loc[mask_prop, "pnl"] / proposed_notional * 10000.0
    bps = pd.to_numeric(g["best_bps"], errors="coerce").dropna()

    # Source-file native column audit, because normalized data may have lost columns.
    fam_source_files = set(g["source_file"].dropna().astype(str).unique().tolist()) if "source_file" in g.columns else set()
    fam_audits = [a for a in source_audits if a.source_file in fam_source_files or a.inferred_family_hint == family_key]
    has_native_source = any(a.has_native_bps_col for a in fam_audits)
    has_notional_source = any(a.has_notional_col for a in fam_audits)

    reasons: List[str] = []
    if native_cov >= 0.80:
        tier = "NATIVE_BPS_STRONG"
        paper_gate = "PASS_FOR_PAPER"
        reasons.append("Native return_bps coverage is strong.")
    elif native_cov >= 0.30:
        tier = "NATIVE_BPS_PARTIAL"
        paper_gate = "PASS_FOR_PAPER_WITH_WARNING"
        reasons.append("Native return_bps coverage is partial; paper confirmation required.")
    elif row_cov >= 0.50 or has_notional_source:
        tier = "ROW_NOTIONAL_ESTIMATED"
        paper_gate = "PASS_FOR_PAPER_WITH_WARNING"
        reasons.append("Bps is mostly estimated from pnl/notional; good enough for paper planning, not live.")
    elif prop_cov >= 0.50:
        tier = "PROPOSED_NOTIONAL_ESTIMATED"
        paper_gate = "PASS_FOR_PAPER_WITH_STRONG_WARNING"
        reasons.append("Bps is mostly estimated from proposed notional; this is weak evidence and must be replaced by paper/native logs.")
    else:
        tier = "INSUFFICIENT_BPS_BASIS"
        paper_gate = "PAPER_BLOCKED_FOR_THIS_FAMILY"
        reasons.append("No reliable bps basis found.")

    if has_native_source and native_cov < 0.30:
        reasons.append("Some source files appear to contain native bps columns, but normalized rows do not preserve them fully; validator/parser may need patching.")
    if not has_native_source:
        reasons.append("No native bps column found in audited source files for this family.")
    if family_key in {"market_relative_short", "weak_market_short"}:
        reasons.append("Family is backup/capped; native bps pass would not imply promotion.")

    live_gate = "LIVE_BLOCKED_UNTIL_PAPER_NATIVE_BPS_AND_DRIFT"
    source = "native" if native_cov >= 0.30 else "row_notional" if row_cov >= 0.50 else "proposed_notional" if prop_cov >= 0.50 else "none"

    return FamilyBpsQuality(
        family_key=family_key,
        proposed_notional=proposed_notional,
        trade_count=n,
        native_bps_count=native_count,
        row_notional_bps_count=row_notional_count,
        proposed_notional_bps_count=proposed_count,
        no_bps_basis_count=max(0, no_basis_count),
        native_bps_coverage=native_cov,
        row_notional_coverage=row_cov,
        proposed_notional_coverage=prop_cov,
        bps_quality_tier=tier,
        paper_gate=paper_gate,
        live_gate=live_gate,
        gross_avg_bps_best_available=float(bps.mean()) if not bps.empty else 0.0,
        gross_median_bps_best_available=float(bps.median()) if not bps.empty else 0.0,
        best_available_source=source,
        reasons=reasons,
    )


def build_actions(family_summaries: List[FamilyBpsQuality]) -> List[NativeBpsAction]:
    actions: List[NativeBpsAction] = []
    for f in family_summaries:
        if f.bps_quality_tier in {"PROPOSED_NOTIONAL_ESTIMATED", "INSUFFICIENT_BPS_BASIS"}:
            actions.append(NativeBpsAction(
                action_key=f"native_bps_required_{f.family_key}",
                family_key=f.family_key,
                severity="REQUIRED_FOR_LIVE",
                title=f"Collect native/paper bps for {f.family_key}",
                reason=f"Current tier={f.bps_quality_tier}; live must remain blocked.",
                safe_offline=True,
                suggested_next_module="paper_runtime_with_native_bps_logging",
                inputs=["paper closed trades with entry/exit/notional/fees/spread"],
                outputs=["native_bps_family_summary.csv", "paper_drift_decisions.json"],
            ))
        elif f.bps_quality_tier == "ROW_NOTIONAL_ESTIMATED":
            actions.append(NativeBpsAction(
                action_key=f"row_notional_bps_review_{f.family_key}",
                family_key=f.family_key,
                severity="WARNING",
                title=f"Review row-notional bps quality for {f.family_key}",
                reason="Row-notional bps is usable for paper planning but not final live validation.",
                safe_offline=True,
                suggested_next_module="edge_factory_paper_boot_plan.py",
                inputs=["normalized_oos_trades.csv", "source files"],
                outputs=["paper plan with native bps logging fields"],
            ))

    actions.append(NativeBpsAction(
        action_key="build_paper_boot_plan",
        family_key="SYSTEM",
        severity="NEXT_MODULE",
        title="Build paper boot plan with native bps logging requirements",
        reason="Native bps cannot be fully proven offline if historical files lack native fields. The paper plan must force native logging.",
        safe_offline=True,
        suggested_next_module="edge_factory_paper_boot_plan.py",
        inputs=["native_bps_validation.json", "paper_boot_decision.json", "kill_switch_policy.json"],
        outputs=["paper_boot_plan.md", "paper_runtime_expected_files.json"],
    ))
    return actions


def summary_df(rows: List[FamilyBpsQuality]) -> pd.DataFrame:
    return pd.DataFrame([asdict(r) for r in rows])


def source_df(rows: List[SourceColumnAudit]) -> pd.DataFrame:
    out = []
    for r in rows:
        d = asdict(r)
        for k in ["columns", "native_bps_cols", "pnl_cols", "notional_cols"]:
            d[k] = " | ".join(str(x) for x in d[k])
        out.append(d)
    return pd.DataFrame(out)


def write_report(path: Path, context: Dict[str, Any], families: List[FamilyBpsQuality], sources: List[SourceColumnAudit], actions: List[NativeBpsAction]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory Native BPS Validation Report")
    lines.append("")
    lines.append(f"Generated: `{context['generated_at']}`")
    lines.append(f"Workspace: `{context['workspace']}`")
    lines.append(f"Normalized trades: `{context.get('normalized_trades_path')}`")
    lines.append("")

    lines.append("## Executive decision")
    lines.append("")
    lines.append(f"Paper data-quality gate: **{context['paper_quality_gate']}**")
    lines.append(f"Live data-quality gate: **{context['live_quality_gate']}**")
    lines.append("")

    lines.append("## Family BPS quality")
    lines.append("")
    lines.append("| Family | Tier | Trades | Native cov | Row-notional cov | Proposed-notional cov | Paper gate | Live gate | Avg bps | Source |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for f in families:
        lines.append(
            f"| {f.family_key} | {f.bps_quality_tier} | {f.trade_count} | {f.native_bps_coverage:.2%} | "
            f"{f.row_notional_coverage:.2%} | {f.proposed_notional_coverage:.2%} | {f.paper_gate} | {f.live_gate} | "
            f"{f.gross_avg_bps_best_available:.4f} | {f.best_available_source} |"
        )
    lines.append("")

    lines.append("## Family reasoning")
    lines.append("")
    for f in families:
        lines.append(f"### {f.family_key}")
        for r in f.reasons:
            lines.append(f"- {r}")
        lines.append("")

    lines.append("## Source column audit")
    lines.append("")
    lines.append(f"Audited source files: **{len(sources)}**")
    native_count = sum(1 for s in sources if s.has_native_bps_col)
    notional_count = sum(1 for s in sources if s.has_notional_col)
    lines.append(f"- Files with native bps columns: **{native_count}**")
    lines.append(f"- Files with notional columns: **{notional_count}**")
    lines.append("")

    lines.append("## Actions")
    lines.append("")
    lines.append("| Severity | Family | Action | Next module | Reason |")
    lines.append("|---|---:|---|---|---|")
    for a in actions:
        lines.append(f"| {a.severity} | {a.family_key} | {a.title} | `{a.suggested_next_module}` | {a.reason} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This module is allowed to keep paper readiness open, but it cannot unlock live. If historical sources lack native bps, the only honest path is paper logging with native execution fields, then drift validation.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory native bps validator")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--max_source_files", type=int, default=200)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_native_bps_validator"
    out_dir = out_root / f"native_bps_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = discover_artifacts(workspace)
    notionals = load_capital_notional_map(artifacts.get("capital_dir"))
    trades, trades_path = load_normalized_trades(artifacts.get("rolling_oos_dir"))
    sources = audit_sources(trades, max_files=args.max_source_files)

    families: List[FamilyBpsQuality] = []
    for fam in KNOWN_FAMILIES:
        proposed = notionals.get(fam, 0.0)
        families.append(family_quality(trades, fam, proposed, sources))

    # Paper quality gate: allow paper unless a positive-notional active family is blocked for no data.
    paper_blockers = [f.family_key for f in families if f.proposed_notional > 0 and f.paper_gate.startswith("PAPER_BLOCKED")]
    strong_warnings = [f.family_key for f in families if f.proposed_notional > 0 and f.bps_quality_tier == "PROPOSED_NOTIONAL_ESTIMATED"]
    if paper_blockers:
        paper_gate = "PAPER_BLOCKED_BPS_DATA_MISSING"
    elif strong_warnings:
        paper_gate = "PAPER_ALLOWED_WITH_STRONG_BPS_WARNINGS"
    else:
        paper_gate = "PAPER_ALLOWED_BPS_QUALITY_ACCEPTABLE"

    live_gate = "LIVE_BLOCKED_UNTIL_PAPER_NATIVE_BPS_AND_DRIFT"
    actions = build_actions(families)

    context = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "artifacts": {k: str(v) if v else None for k, v in artifacts.items()},
        "normalized_trades_path": str(trades_path) if trades_path else None,
        "trade_rows": int(len(trades)),
        "paper_quality_gate": paper_gate,
        "live_quality_gate": live_gate,
        "paper_blockers": paper_blockers,
        "strong_warnings": strong_warnings,
    }

    result = {
        "context": context,
        "family_quality": [asdict(f) for f in families],
        "source_column_audit": [asdict(s) for s in sources],
        "actions": [asdict(a) for a in actions],
        "hard_rules": [
            "Native bps validation does not unlock live by itself.",
            "If bps is estimated from proposed notional, paper/native logging is mandatory.",
            "Backup families cannot be promoted from bps quality alone.",
        ],
    }

    write_json(out_dir / "native_bps_validation.json", result)
    write_json(out_dir / "native_bps_actions.json", [asdict(a) for a in actions])
    summary_df(families).to_csv(out_dir / "native_bps_family_summary.csv", index=False)
    source_df(sources).to_csv(out_dir / "native_bps_source_columns.csv", index=False)
    write_report(out_dir / "native_bps_validation_report.md", context, families, sources, actions)

    print("EDGE FACTORY NATIVE BPS VALIDATOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"rows      : {len(trades)}")
    print(f"paper_gate: {paper_gate}")
    print(f"live_gate : {live_gate}")
    print("")
    print("FAMILY BPS QUALITY")
    print("-" * 100)
    for f in families:
        print(
            f"{f.family_key:24s} notional={f.proposed_notional:8.4f} tier={f.bps_quality_tier:30s} "
            f"trades={f.trade_count:7d} native={f.native_bps_coverage:7.2%} row_notional={f.row_notional_coverage:7.2%} "
            f"proposed={f.proposed_notional_coverage:7.2%} paper={f.paper_gate}"
        )
        for r in f.reasons[:3]:
            print(f"  - {r}")
    print("")
    print("NEXT ACTIONS")
    print("-" * 100)
    for a in actions[:8]:
        print(f"{a.severity:18s} {a.family_key:24s} -> {a.suggested_next_module}: {a.title}")
    print("")
    print(f"Open report: {out_dir / 'native_bps_validation_report.md'}")
    print(f"JSON       : {out_dir / 'native_bps_validation.json'}")
    print(f"Summary    : {out_dir / 'native_bps_family_summary.csv'}")
    return 0 if not paper_blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
