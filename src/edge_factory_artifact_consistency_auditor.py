#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY ARTIFACT CONSISTENCY AUDITOR v1
============================================

Purpose
-------
Schema / artifact consistency auditor for the Edge Factory OS.

Why this exists
---------------
The coin subset validator can only be trusted if the trade CSV schema is mapped correctly.
If a validator accidentally treats a parameter column as a symbol column, results like:
    best=TRUE
    worst=UNKNOWN
    best=-800
    worst=-1000
can appear. That means the robustness result may be contaminated by schema ambiguity.

This module audits source CSVs and validator outputs before the OS trusts robustness labels.

It DOES NOT:
    - start paper
    - start live
    - run loggers
    - mutate active config
    - promote strategies
    - change capital
    - run --apply

It DOES:
    - inspect latest rolling OOS / normalized trade CSV files
    - inspect latest candidate and coin-subset validator summaries
    - infer likely family/pnl/symbol/time columns
    - flag suspicious symbol columns / suspicious symbol values
    - flag impossible-looking PF/WR patterns
    - produce schema recommendations for future validators
    - optionally append an evidence-only research ledger result

Run:
    python "C:\Users\alike\edge_factory_artifact_consistency_auditor.py"

Outputs:
    <workspace>\edge_factory_artifact_consistency_auditor\artifact_audit_YYYYMMDD_HHMMSS\
        artifact_consistency_audit_report.md
        artifact_consistency_audit_state.json
        source_csv_schema_audit.csv
        validator_output_audit.csv
        schema_recommendations.json

Core rule
---------
This is a trust/audit layer. It can invalidate confidence in previous validator outputs,
but it never changes active system configuration.
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

FAMILY_COL_CANDIDATES = ["family_key", "family", "strategy", "strategy_key", "candidate", "candidate_key", "label", "name"]
PNL_COL_CANDIDATES = ["net_pnl_usdt", "pnl_usdt", "pnl", "net_pnl", "gross_pnl_usdt", "profit", "ret", "return"]
SYMBOL_COL_CANDIDATES = ["inst_id", "instrument", "symbol", "inst", "ticker", "coin", "asset"]
TIME_COL_CANDIDATES = ["exit_time", "entry_time", "timestamp", "time", "open_time", "close_time", "ts", "datetime", "date"]

BAD_SYMBOL_VALUES = {"true", "false", "unknown", "none", "nan", "null", "yes", "no"}


@dataclass
class CsvSchemaAudit:
    path: str
    kind: str
    rows_sampled: int
    total_columns: int
    family_col: Optional[str]
    pnl_col: Optional[str]
    symbol_col: Optional[str]
    time_col: Optional[str]
    symbol_unique_count: int
    suspicious_symbol_rate: float
    numeric_symbol_rate: float
    bad_symbol_examples: str
    verdict: str
    warnings: str
    columns: str


@dataclass
class ValidatorOutputAudit:
    path: str
    kind: str
    rows: int
    suspicious_rows: int
    suspicious_rate: float
    suspicious_fields: str
    verdict: str
    warnings: str


@dataclass
class AuditorState:
    generated_at: str
    workspace: str
    source_csv_count: int
    validator_output_count: int
    schema_pass_count: int
    schema_warn_count: int
    schema_fail_count: int
    validator_pass_count: int
    validator_warn_count: int
    validator_fail_count: int
    overall_verdict: str
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


def find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lookup = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lookup:
            return str(lookup[c.lower()])
    # fuzzy fallback for instrument-like columns, but avoid boolean/parameter columns.
    for col in df.columns:
        low = str(col).lower()
        if any(tok in low for tok in ["symbol", "inst", "instrument", "ticker"]):
            return str(col)
    return None


def discover_source_csvs(workspace: Path) -> List[Path]:
    paths: List[Path] = []
    roots = [
        workspace / "edge_factory_rolling_oos_validator",
        workspace / "edge_factory_rolling_oos_validator_v2",
    ]
    for root in roots:
        if root.exists():
            for p in root.rglob("*.csv"):
                name = p.name.lower()
                if any(tok in name for tok in ["trade", "normalized", "oos", "candidate"]):
                    paths.append(p)
    uniq = {str(p.resolve()).lower(): p for p in paths if p.exists() and p.is_file()}
    out = list(uniq.values())
    out.sort(key=lambda p: (p.stat().st_mtime, p.stat().st_size), reverse=True)
    return out[:50]


def discover_validator_outputs(workspace: Path) -> List[Path]:
    paths: List[Path] = []
    for root_name in ["edge_factory_coin_subset_validator", "edge_factory_research_candidate_validator"]:
        root = workspace / root_name
        if root.exists():
            for p in root.rglob("*.csv"):
                name = p.name.lower()
                if any(tok in name for tok in ["summary", "results", "validation"]):
                    paths.append(p)
    uniq = {str(p.resolve()).lower(): p for p in paths if p.exists() and p.is_file()}
    out = list(uniq.values())
    out.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return out[:80]


def is_numeric_like(x: str) -> bool:
    s = str(x).strip()
    if not s:
        return False
    try:
        float(s)
        return True
    except Exception:
        return False


def looks_like_symbol(x: str) -> bool:
    s = str(x).strip().upper()
    if not s:
        return False
    if s.lower() in BAD_SYMBOL_VALUES:
        return False
    if is_numeric_like(s):
        return False
    if len(s) > 20:
        return False
    # Allows RAVE, BTC, PIEVERSE, BTC-USDT-SWAP, etc.
    return bool(re.match(r"^[A-Z0-9][A-Z0-9_\-\/]{0,19}$", s))


def audit_symbol_series(series: pd.Series) -> Tuple[int, float, float, str]:
    vals = series.dropna().astype(str).str.strip()
    if vals.empty:
        return 0, 1.0, 1.0, "empty"
    sample = vals.head(5000)
    bad_mask = sample.apply(lambda x: not looks_like_symbol(x))
    numeric_mask = sample.apply(is_numeric_like)
    bad_examples = sorted(set(sample[bad_mask].head(20).astype(str).tolist()))
    return int(vals.nunique()), float(bad_mask.mean()), float(numeric_mask.mean()), " | ".join(bad_examples)


def classify_source_audit(symbol_col: Optional[str], suspicious_rate: float, numeric_rate: float, family_col: Optional[str], pnl_col: Optional[str]) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    if not pnl_col:
        warnings.append("missing pnl column")
    if not family_col:
        warnings.append("missing family/candidate column")
    if not symbol_col:
        warnings.append("missing symbol/instrument column")
        return "FAIL", warnings
    if suspicious_rate > 0.50 or numeric_rate > 0.30:
        warnings.append("symbol column appears contaminated by non-symbol/parameter values")
        return "FAIL", warnings
    if suspicious_rate > 0.10 or numeric_rate > 0.05:
        warnings.append("symbol column has suspicious values; validator outputs need caution")
        return "WARN", warnings
    if warnings:
        return "WARN", warnings
    return "PASS", warnings


def audit_source_csv(path: Path, sample_rows: int) -> CsvSchemaAudit:
    try:
        df = pd.read_csv(path, nrows=sample_rows)
    except Exception as e:
        return CsvSchemaAudit(str(path), "source_csv", 0, 0, None, None, None, None, 0, 1.0, 1.0, repr(e), "FAIL", f"read error: {e}", "")

    family_col = find_col(df, FAMILY_COL_CANDIDATES)
    pnl_col = find_col(df, PNL_COL_CANDIDATES)
    symbol_col = find_col(df, SYMBOL_COL_CANDIDATES)
    time_col = find_col(df, TIME_COL_CANDIDATES)
    if symbol_col and symbol_col in df.columns:
        unique_count, suspicious_rate, numeric_rate, bad_examples = audit_symbol_series(df[symbol_col])
    else:
        unique_count, suspicious_rate, numeric_rate, bad_examples = 0, 1.0, 1.0, "missing"
    verdict, warnings = classify_source_audit(symbol_col, suspicious_rate, numeric_rate, family_col, pnl_col)
    return CsvSchemaAudit(
        path=str(path),
        kind="source_csv",
        rows_sampled=int(len(df)),
        total_columns=int(len(df.columns)),
        family_col=family_col,
        pnl_col=pnl_col,
        symbol_col=symbol_col,
        time_col=time_col,
        symbol_unique_count=unique_count,
        suspicious_symbol_rate=round(suspicious_rate, 6),
        numeric_symbol_rate=round(numeric_rate, 6),
        bad_symbol_examples=bad_examples,
        verdict=verdict,
        warnings=" | ".join(warnings),
        columns=" | ".join(str(c) for c in df.columns),
    )


def audit_validator_output(path: Path, sample_rows: int) -> ValidatorOutputAudit:
    try:
        df = pd.read_csv(path, nrows=sample_rows)
    except Exception as e:
        return ValidatorOutputAudit(str(path), "validator_output", 0, 0, 1.0, "read_error", "FAIL", f"read error: {e}")

    warnings: List[str] = []
    suspicious_fields: List[str] = []
    suspicious_rows = 0

    # Audit fields produced by our validators.
    for col in ["top_symbol", "worst_symbol", "best_symbol"]:
        if col in df.columns:
            vals = df[col].dropna().astype(str)
            bad = vals.apply(lambda x: not looks_like_symbol(x))
            if not vals.empty and bad.any():
                suspicious_rows = max(suspicious_rows, int(bad.sum()))
                examples = "|".join(vals[bad].head(10).tolist())
                suspicious_fields.append(f"{col}:{examples}")

    for col in ["profit_factor"]:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce")
            huge = vals >= 999999
            if huge.any():
                suspicious_fields.append(f"{col}:999999_or_inf_count={int(huge.sum())}")
                warnings.append("profit factor has infinite/huge values; check loss rows and PnL mapping")

    for col in ["win_rate"]:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce")
            perfect = vals >= 0.999
            if perfect.any():
                suspicious_fields.append(f"{col}:perfect_count={int(perfect.sum())}")
                warnings.append("perfect win rate appears; check whether source includes losses")

    suspicious_rate = suspicious_rows / max(1, len(df))
    if suspicious_fields:
        verdict = "WARN"
    else:
        verdict = "PASS"
    if suspicious_rate > 0.30:
        verdict = "FAIL"
    return ValidatorOutputAudit(
        path=str(path),
        kind="validator_output",
        rows=int(len(df)),
        suspicious_rows=int(suspicious_rows),
        suspicious_rate=round(float(suspicious_rate), 6),
        suspicious_fields=" | ".join(suspicious_fields),
        verdict=verdict,
        warnings=" | ".join(warnings),
    )


def df_from_dataclasses(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def build_recommendations(source_audits: List[CsvSchemaAudit], output_audits: List[ValidatorOutputAudit]) -> Dict[str, Any]:
    best_sources = [a for a in source_audits if a.verdict == "PASS"]
    warn_sources = [a for a in source_audits if a.verdict == "WARN"]
    fail_sources = [a for a in source_audits if a.verdict == "FAIL"]
    suspicious_outputs = [a for a in output_audits if a.verdict in {"WARN", "FAIL"}]

    recommended_symbol_col = None
    recommended_family_col = None
    recommended_pnl_col = None
    recommended_time_col = None
    if best_sources:
        a = best_sources[0]
        recommended_symbol_col = a.symbol_col
        recommended_family_col = a.family_col
        recommended_pnl_col = a.pnl_col
        recommended_time_col = a.time_col

    return {
        "recommended_source_path": best_sources[0].path if best_sources else (warn_sources[0].path if warn_sources else None),
        "recommended_columns": {
            "family_col": recommended_family_col,
            "pnl_col": recommended_pnl_col,
            "symbol_col": recommended_symbol_col,
            "time_col": recommended_time_col,
        },
        "source_pass_count": len(best_sources),
        "source_warn_count": len(warn_sources),
        "source_fail_count": len(fail_sources),
        "suspicious_validator_output_count": len(suspicious_outputs),
        "recommendations": [
            "Do not trust coin-subset labels that used suspicious symbol values such as TRUE, UNKNOWN, -800, -1000.",
            "Patch validators to require an explicit symbol/instrument column from schema recommendations when available.",
            "Treat PF=999999 or WR=100% as a data-quality warning until source rows are manually inspected.",
            "Only use ROBUST_COIN_FIT after schema audit passes or after validator v2 uses audited column mapping.",
        ],
    }


def append_ledger(workspace: Path, state: AuditorState, out_state_path: Path) -> Optional[str]:
    try:
        root = workspace / "edge_factory_research_result_ledger"
        ledger = root / "master_research_result_ledger.jsonl"
        raw = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "task_id": "build_artifact_consistency_auditor",
            "result_status": "PASS" if state.overall_verdict != "FAIL" else "WATCHLIST",
            "score": 1.0 if state.overall_verdict == "PASS" else 0.5,
            "summary": f"Artifact consistency auditor ran. verdict={state.overall_verdict}, schema_warn={state.schema_warn_count}, schema_fail={state.schema_fail_count}, validator_warn={state.validator_warn_count}, validator_fail={state.validator_fail_count}",
            "evidence_path": str(out_state_path),
            "family": None,
            "candidate": None,
            "tags": ["artifact_consistency", "schema_audit", "offline", "no_promotion"],
            "reviewer": "artifact_consistency_auditor_v1",
            "source": "edge_factory_artifact_consistency_auditor_v1",
            "safe_for_auto_promotion": False,
            "live_allowed": False,
            "notes": "Evidence-only artifact/schema audit. No active config mutation.",
        }
        result_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.sha256(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest()[:16]}"
        row = {"result_id": result_id, **raw}
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
        return result_id
    except Exception:
        return None


def write_report(path: Path, state: AuditorState, source_audits: List[CsvSchemaAudit], output_audits: List[ValidatorOutputAudit], recs: Dict[str, Any]) -> None:
    lines = [
        "# Edge Factory Artifact Consistency Auditor Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall verdict: **{state.overall_verdict}**",
        f"Source CSV count: **{state.source_csv_count}**",
        f"Validator output count: **{state.validator_output_count}**",
        f"Schema pass/warn/fail: **{state.schema_pass_count}/{state.schema_warn_count}/{state.schema_fail_count}**",
        f"Validator pass/warn/fail: **{state.validator_pass_count}/{state.validator_warn_count}/{state.validator_fail_count}**",
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
    lines += ["", "## Schema recommendations", "", "```json", json.dumps(recs, indent=2, ensure_ascii=False), "```", ""]
    lines += ["## Source CSV audit", ""]
    if source_audits:
        lines += ["| Verdict | Rows | Family | PnL | Symbol | Suspicious symbol rate | Bad examples | Path |", "|---:|---:|---|---|---|---:|---|---|"]
        for a in source_audits[:30]:
            lines.append(f"| {a.verdict} | {a.rows_sampled} | {a.family_col} | {a.pnl_col} | {a.symbol_col} | {a.suspicious_symbol_rate} | {a.bad_symbol_examples} | `{a.path}` |")
    else:
        lines.append("No source CSVs found.")
    lines += ["", "## Validator output audit", ""]
    if output_audits:
        lines += ["| Verdict | Rows | Suspicious fields | Path |", "|---:|---:|---|---|"]
        for a in output_audits[:40]:
            lines.append(f"| {a.verdict} | {a.rows} | {a.suspicious_fields} | `{a.path}` |")
    else:
        lines.append("No validator output CSVs found.")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "If this report shows WARN/FAIL, previous validator outputs should be treated as provisional. Patch validators to use audited column mappings before making lifecycle or promotion decisions.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory artifact consistency auditor")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--out_dir", default=None)
    p.add_argument("--sample_rows", type=int, default=5000)
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_artifact_consistency_auditor"
    out_dir = out_root / f"artifact_audit_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source_paths = discover_source_csvs(workspace)
    output_paths = discover_validator_outputs(workspace)
    source_audits = [audit_source_csv(p, int(args.sample_rows)) for p in source_paths]
    output_audits = [audit_validator_output(p, int(args.sample_rows)) for p in output_paths]

    sp = len([a for a in source_audits if a.verdict == "PASS"])
    sw = len([a for a in source_audits if a.verdict == "WARN"])
    sf = len([a for a in source_audits if a.verdict == "FAIL"])
    vp = len([a for a in output_audits if a.verdict == "PASS"])
    vw = len([a for a in output_audits if a.verdict == "WARN"])
    vf = len([a for a in output_audits if a.verdict == "FAIL"])

    warnings: List[str] = []
    reasons: List[str] = ["Artifact/schema audit ran offline."]
    if sf > 0 or vf > 0:
        verdict = "FAIL"
        warnings.append("At least one source or validator output failed schema consistency checks.")
    elif sw > 0 or vw > 0:
        verdict = "WARN"
        warnings.append("Some artifacts have suspicious schema/output values; downstream validator labels are provisional.")
    else:
        verdict = "PASS"
        reasons.append("No major schema consistency problems detected in sampled artifacts.")

    # Specific warning for suspicious outputs we have seen.
    if any("TRUE" in a.suspicious_fields.upper() or "UNKNOWN" in a.suspicious_fields.upper() or "-800" in a.suspicious_fields for a in output_audits):
        warnings.append("Validator outputs include TRUE/UNKNOWN/-800-like symbol values; coin subset classifications need v2 schema mapping before trust.")

    state = AuditorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        source_csv_count=len(source_audits),
        validator_output_count=len(output_audits),
        schema_pass_count=sp,
        schema_warn_count=sw,
        schema_fail_count=sf,
        validator_pass_count=vp,
        validator_warn_count=vw,
        validator_fail_count=vf,
        overall_verdict=verdict,
        live_allowed=False,
        reasons=reasons,
        warnings=warnings,
        hard_rules=[
            "Artifact consistency auditor never starts paper/live.",
            "Artifact consistency auditor never mutates active config.",
            "Artifact consistency auditor never promotes candidates automatically.",
            "WARN/FAIL means downstream research labels are provisional until fixed.",
            "Live remains blocked.",
        ],
    )

    recs = build_recommendations(source_audits, output_audits)
    state_path = out_dir / "artifact_consistency_audit_state.json"
    result_obj = {
        "state": asdict(state),
        "source_csv_audit": [asdict(a) for a in source_audits],
        "validator_output_audit": [asdict(a) for a in output_audits],
        "schema_recommendations": recs,
    }
    write_json(state_path, result_obj)
    write_json(out_dir / "schema_recommendations.json", recs)
    df_from_dataclasses(source_audits).to_csv(out_dir / "source_csv_schema_audit.csv", index=False)
    df_from_dataclasses(output_audits).to_csv(out_dir / "validator_output_audit.csv", index=False)
    write_report(out_dir / "artifact_consistency_audit_report.md", state, source_audits, output_audits, recs)

    ledger_id = None
    if not args.no_ledger_append:
        ledger_id = append_ledger(workspace, state, state_path)

    print("EDGE FACTORY ARTIFACT CONSISTENCY AUDITOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_verdict: {state.overall_verdict}")
    print(f"source_csv_count: {state.source_csv_count} pass={state.schema_pass_count} warn={state.schema_warn_count} fail={state.schema_fail_count}")
    print(f"validator_output_count: {state.validator_output_count} pass={state.validator_pass_count} warn={state.validator_warn_count} fail={state.validator_fail_count}")
    print(f"ledger_result_id: {ledger_id}")
    print("live_allowed: False")
    print("")
    print("WARNINGS")
    print("-" * 100)
    if state.warnings:
        for w in state.warnings:
            print(f"- {w}")
    else:
        print("none")
    print("")
    print("TOP SOURCE AUDIT")
    print("-" * 100)
    for a in source_audits[:10]:
        print(f"{a.verdict:5s} rows={a.rows_sampled:6d} family={a.family_col} pnl={a.pnl_col} symbol={a.symbol_col} suspicious={a.suspicious_symbol_rate:.2%} numeric={a.numeric_symbol_rate:.2%}")
        print(f"     path={a.path}")
        if a.bad_symbol_examples:
            print(f"     bad_examples={a.bad_symbol_examples}")
    print("")
    print("TOP VALIDATOR OUTPUT AUDIT")
    print("-" * 100)
    for a in output_audits[:10]:
        print(f"{a.verdict:5s} rows={a.rows:5d} suspicious={a.suspicious_rate:.2%} fields={a.suspicious_fields}")
        print(f"     path={a.path}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'artifact_consistency_audit_report.md'}")
    print(f"State  : {state_path}")
    print(f"Schema : {out_dir / 'schema_recommendations.json'}")
    return 0 if state.overall_verdict != "FAIL" else 2

if __name__ == "__main__":
    raise SystemExit(main())
