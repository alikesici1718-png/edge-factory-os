#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 ARTIFACT SCHEMA INSPECTOR v1
===============================================

Purpose
-------
Inspect ret60_reversal_short artifact CSV schemas after artifact parser found:
    RULE_PARAMS_EXTRACTED_NEEDS_SCANNER_SEMANTICS
    selectable_variants = 0
    pnl/pf/wr = 0 for all variants

This usually means:
    - PnL/return columns exist under unexpected names, OR
    - session_trades files are event/signal rows without realized PnL, OR
    - combined_sim files contain summary/equity information that the parser did not understand.

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
    - inspect all ret60 artifact CSVs under session_top_exact_validator
    - list columns by artifact type
    - detect numeric nonzero columns
    - detect possible pnl/return/equity/metric columns by name and distribution
    - compare session_trades vs combined_sim schemas
    - select candidate metric columns for parser v2
    - write schema inspection packet for next recovery step

Run:
    python "C:\Users\alike\edge_factory_ret60_artifact_schema_inspector.py"

Core rule
---------
This is schema inspection only. It cannot approve runtime.
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
DEFAULT_CANDIDATE = "ret60_reversal_short"

PARAM_RE = re.compile(
    r"(?P<prefix>combined_sim_session_first|session_trades)_(?P<candidate>ret60_reversal_short)_h(?P<h>\d+)_m(?P<m>\d+)_hold(?P<hold>\d+)_delay(?P<delay>\d+)_extra(?P<extra>\d+)\.csv$",
    re.IGNORECASE,
)

METRIC_NAME_HINTS = [
    "pnl", "profit", "return", "ret", "bps", "equity", "balance", "net", "gross",
    "win", "loss", "pf", "drawdown", "dd", "sharpe", "score", "edge", "avg",
    "total", "sum", "final", "cum", "cumulative", "fee", "cost"
]
SIGNAL_NAME_HINTS = [
    "ret60", "range_mean", "range", "z", "rank", "threshold", "m", "h", "delay",
    "extra", "signal", "score", "side", "session", "hour", "minute", "time", "symbol"
]


@dataclass
class ArtifactSchemaRecord:
    path: str
    filename: str
    artifact_type: str
    variant_key: str
    h_param: Optional[int]
    m_param: Optional[int]
    hold_param: Optional[int]
    delay_param: Optional[int]
    extra_param: Optional[int]
    rows: int
    columns_count: int
    columns: str
    metric_name_columns: str
    signal_name_columns: str
    numeric_columns_count: int
    nonzero_numeric_columns_count: int
    constant_columns_count: int
    possible_pnl_columns: str
    possible_return_columns: str
    possible_equity_columns: str
    possible_summary_columns: str
    top_numeric_columns_json: str
    sample_rows_json: str
    warnings: str


@dataclass
class ColumnCandidate:
    artifact_type: str
    column: str
    files_seen: int
    nonzero_files: int
    avg_non_null_rate: float
    avg_abs_mean: float
    min_value: float
    max_value: float
    score: float
    role_guess: str
    example_file: str


@dataclass
class InspectorState:
    generated_at: str
    workspace: str
    artifact_dir: str
    candidate: str
    artifacts_seen: int
    artifacts_loaded: int
    artifact_types: str
    unique_variants: int
    candidate_metric_columns: int
    candidate_signal_columns: int
    inspector_status: str
    next_action: str
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


def parse_filename(path: Path) -> Dict[str, Any]:
    m = PARAM_RE.search(path.name)
    if not m:
        return {
            "artifact_type": "UNKNOWN",
            "candidate": None,
            "h": None,
            "m": None,
            "hold": None,
            "delay": None,
            "extra": None,
            "variant_key": None,
        }
    candidate = safe_key(m.group("candidate"))
    h = int(m.group("h"))
    mm = int(m.group("m"))
    hold = int(m.group("hold"))
    delay = int(m.group("delay"))
    extra = int(m.group("extra"))
    return {
        "artifact_type": m.group("prefix").lower(),
        "candidate": candidate,
        "h": h,
        "m": mm,
        "hold": hold,
        "delay": delay,
        "extra": extra,
        "variant_key": f"{candidate}_h{h}_m{mm}_hold{hold}_delay{delay}_extra{extra}",
    }


def artifact_dir_for(workspace: Path, artifact_dir: Optional[str]) -> Path:
    return Path(artifact_dir) if artifact_dir else workspace / "session_top_exact_validator"


def role_from_name(col: str) -> str:
    low = col.lower()
    if any(x in low for x in ["pnl", "profit", "net_usdt", "gross_usdt"]):
        return "POSSIBLE_PNL"
    if any(x in low for x in ["return", "ret", "bps"]):
        return "POSSIBLE_RETURN_OR_FEATURE"
    if any(x in low for x in ["equity", "balance", "cum", "cumulative"]):
        return "POSSIBLE_EQUITY"
    if any(x in low for x in ["pf", "win", "loss", "drawdown", "sharpe", "avg", "total", "final"]):
        return "POSSIBLE_SUMMARY_METRIC"
    if any(x in low for x in SIGNAL_NAME_HINTS):
        return "POSSIBLE_SIGNAL_OR_CONTEXT"
    return "UNKNOWN"


def inspect_numeric_columns(df: pd.DataFrame, max_cols: int = 80) -> Tuple[List[Dict[str, Any]], int, int, int]:
    rows: List[Dict[str, Any]] = []
    numeric_count = 0
    nonzero_count = 0
    constant_count = 0
    for col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce")
        non_null = int(s.notna().sum())
        if non_null == 0:
            continue
        numeric_count += 1
        vals = s.dropna()
        is_nonzero = bool((vals != 0).any())
        if is_nonzero:
            nonzero_count += 1
        if vals.nunique(dropna=True) <= 1:
            constant_count += 1
        low = str(col).lower()
        name_score = 0
        if any(h in low for h in METRIC_NAME_HINTS):
            name_score += 10
        if any(h in low for h in SIGNAL_NAME_HINTS):
            name_score += 3
        try:
            abs_mean = float(vals.abs().mean())
            mean = float(vals.mean())
            mn = float(vals.min())
            mx = float(vals.max())
            std = float(vals.std()) if non_null > 1 else 0.0
            non_null_rate = float(non_null / max(1, len(df)))
            score = name_score + (5 if is_nonzero else 0) + min(10, non_null_rate * 10) + (2 if std > 0 else 0)
            rows.append({
                "column": str(col),
                "role_guess": role_from_name(str(col)),
                "non_null": non_null,
                "non_null_rate": round(non_null_rate, 6),
                "nonzero": is_nonzero,
                "unique": int(vals.nunique(dropna=True)),
                "min": mn,
                "mean": mean,
                "abs_mean": abs_mean,
                "median": float(vals.median()),
                "max": mx,
                "std": std,
                "score": round(score, 6),
            })
        except Exception:
            pass
    rows.sort(key=lambda r: (r["score"], r["abs_mean"]), reverse=True)
    return rows[:max_cols], numeric_count, nonzero_count, constant_count


def json_sample(df: pd.DataFrame, rows: int = 3, cols: int = 40) -> str:
    try:
        sample = df.iloc[:rows, :cols].copy()
        return json.dumps(sample.to_dict(orient="records"), ensure_ascii=False, default=str)[:20000]
    except Exception as e:
        return json.dumps({"sample_error": str(e)}, ensure_ascii=False)


def inspect_file(path: Path, max_rows: Optional[int]) -> ArtifactSchemaRecord:
    p = parse_filename(path)
    warnings: List[str] = []
    try:
        if max_rows and max_rows > 0:
            df = pd.read_csv(path, nrows=max_rows)
            # Count full rows cheaply.
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    full_rows = max(0, sum(1 for _ in f) - 1)
            except Exception:
                full_rows = len(df)
            if full_rows > len(df):
                warnings.append(f"sampled first {len(df)} rows out of {full_rows}")
        else:
            df = pd.read_csv(path)
            full_rows = len(df)
    except Exception as e:
        return ArtifactSchemaRecord(
            path=str(path), filename=path.name, artifact_type=str(p["artifact_type"]), variant_key=str(p["variant_key"]),
            h_param=p["h"], m_param=p["m"], hold_param=p["hold"], delay_param=p["delay"], extra_param=p["extra"],
            rows=0, columns_count=0, columns="", metric_name_columns="", signal_name_columns="",
            numeric_columns_count=0, nonzero_numeric_columns_count=0, constant_columns_count=0,
            possible_pnl_columns="", possible_return_columns="", possible_equity_columns="", possible_summary_columns="",
            top_numeric_columns_json="[]", sample_rows_json="[]", warnings=f"read failed: {e}"
        )

    cols = [str(c) for c in df.columns]
    metric_cols = [c for c in cols if any(h in c.lower() for h in METRIC_NAME_HINTS)]
    signal_cols = [c for c in cols if any(h in c.lower() for h in SIGNAL_NAME_HINTS)]
    pnl_cols = [c for c in cols if any(h in c.lower() for h in ["pnl", "profit"])]
    ret_cols = [c for c in cols if any(h in c.lower() for h in ["return", "ret", "bps"])]
    equity_cols = [c for c in cols if any(h in c.lower() for h in ["equity", "balance", "cum", "cumulative"])]
    summary_cols = [c for c in cols if any(h in c.lower() for h in ["pf", "win", "loss", "drawdown", "sharpe", "avg", "total", "final", "score"])]
    top_numeric, numeric_count, nonzero_count, constant_count = inspect_numeric_columns(df)

    return ArtifactSchemaRecord(
        path=str(path),
        filename=path.name,
        artifact_type=str(p["artifact_type"]),
        variant_key=str(p["variant_key"]),
        h_param=p["h"],
        m_param=p["m"],
        hold_param=p["hold"],
        delay_param=p["delay"],
        extra_param=p["extra"],
        rows=int(full_rows),
        columns_count=len(cols),
        columns=" | ".join(cols),
        metric_name_columns=" | ".join(metric_cols),
        signal_name_columns=" | ".join(signal_cols),
        numeric_columns_count=numeric_count,
        nonzero_numeric_columns_count=nonzero_count,
        constant_columns_count=constant_count,
        possible_pnl_columns=" | ".join(pnl_cols),
        possible_return_columns=" | ".join(ret_cols),
        possible_equity_columns=" | ".join(equity_cols),
        possible_summary_columns=" | ".join(summary_cols),
        top_numeric_columns_json=json.dumps(top_numeric, ensure_ascii=False, default=str),
        sample_rows_json=json_sample(df),
        warnings=" | ".join(warnings),
    )


def aggregate_column_candidates(records: List[ArtifactSchemaRecord]) -> List[ColumnCandidate]:
    # Re-open sampled top numeric json and aggregate by artifact_type/column.
    buckets: Dict[Tuple[str, str], List[Tuple[ArtifactSchemaRecord, Dict[str, Any]]]] = {}
    for rec in records:
        try:
            cols = json.loads(rec.top_numeric_columns_json)
        except Exception:
            cols = []
        for c in cols:
            key = (rec.artifact_type, str(c.get("column")))
            buckets.setdefault(key, []).append((rec, c))

    out: List[ColumnCandidate] = []
    for (atype, col), items in buckets.items():
        files_seen = len(items)
        nonzero_files = sum(1 for _, c in items if bool(c.get("nonzero")))
        rates = [float(c.get("non_null_rate", 0.0)) for _, c in items]
        abs_means = [float(c.get("abs_mean", 0.0)) for _, c in items]
        mins = [float(c.get("min", 0.0)) for _, c in items]
        maxs = [float(c.get("max", 0.0)) for _, c in items]
        role = role_from_name(col)
        name_bonus = 0.0
        if role == "POSSIBLE_PNL":
            name_bonus = 40.0
        elif role == "POSSIBLE_RETURN_OR_FEATURE":
            name_bonus = 25.0
        elif role == "POSSIBLE_EQUITY":
            name_bonus = 20.0
        elif role == "POSSIBLE_SUMMARY_METRIC":
            name_bonus = 15.0
        score = name_bonus + nonzero_files * 5 + files_seen * 2 + (sum(rates) / max(1, len(rates))) * 10
        out.append(ColumnCandidate(
            artifact_type=atype,
            column=col,
            files_seen=files_seen,
            nonzero_files=nonzero_files,
            avg_non_null_rate=round(sum(rates) / max(1, len(rates)), 6),
            avg_abs_mean=round(sum(abs_means) / max(1, len(abs_means)), 8),
            min_value=round(min(mins), 8),
            max_value=round(max(maxs), 8),
            score=round(score, 8),
            role_guess=role,
            example_file=items[0][0].path,
        ))
    out.sort(key=lambda x: (x.role_guess in {"POSSIBLE_PNL", "POSSIBLE_RETURN_OR_FEATURE", "POSSIBLE_EQUITY"}, x.score), reverse=True)
    return out


def records_df(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def build_status(records: List[ArtifactSchemaRecord], candidates: List[ColumnCandidate]) -> Tuple[str, str, List[str], List[str]]:
    reasons: List[str] = []
    warnings: List[str] = []
    pnl = [c for c in candidates if c.role_guess == "POSSIBLE_PNL" and c.nonzero_files > 0]
    ret = [c for c in candidates if c.role_guess == "POSSIBLE_RETURN_OR_FEATURE" and c.nonzero_files > 0]
    equity = [c for c in candidates if c.role_guess == "POSSIBLE_EQUITY" and c.nonzero_files > 0]
    summary = [c for c in candidates if c.role_guess == "POSSIBLE_SUMMARY_METRIC" and c.nonzero_files > 0]

    if pnl:
        status = "PNL_COLUMNS_FOUND_FOR_PARSER_V2"
        next_action = "BUILD_RET60_RULE_ARTIFACT_PARSER_V2_WITH_PNL_COLUMNS"
        reasons.append("nonzero PnL/profit-like columns were found")
    elif ret or equity or summary:
        status = "METRIC_COLUMNS_FOUND_NEEDS_MAPPING"
        next_action = "MAP_METRIC_COLUMNS_THEN_BUILD_PARSER_V2"
        reasons.append("metric-like columns exist, but no direct nonzero PnL column was found")
    else:
        status = "NO_METRIC_COLUMNS_FOUND_ARTIFACTS_ARE_SIGNAL_ONLY"
        next_action = "FIND_ORIGINAL_SCANNER_CODE_OR_REGENERATE_METRICS"
        warnings.append("artifacts appear to lack realized metric columns; they may be signal/event rows only")

    if records and all(r.possible_pnl_columns == "" for r in records):
        warnings.append("no column names containing pnl/profit found in any inspected artifact")
    return status, next_action, reasons, warnings


def write_report(path: Path, state: InspectorState, records: List[ArtifactSchemaRecord], candidates: List[ColumnCandidate]) -> None:
    lines = [
        "# Edge Factory Ret60 Artifact Schema Inspector Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Inspector status: **{state.inspector_status}**",
        f"Next action: **{state.next_action}**",
        f"Artifacts seen: **{state.artifacts_seen}**",
        f"Artifacts loaded: **{state.artifacts_loaded}**",
        f"Unique variants: **{state.unique_variants}**",
        f"Candidate metric columns: **{state.candidate_metric_columns}**",
        f"Candidate signal columns: **{state.candidate_signal_columns}**",
        f"Logger build allowed: **{state.logger_build_allowed}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Top column candidates",
        "",
    ]
    if candidates:
        lines += ["| Score | Type | Column | Role | Files | Nonzero files | Min | Max | Example |", "|---:|---|---|---|---:|---:|---:|---:|---|"]
        for c in candidates[:50]:
            lines.append(f"| {c.score} | {c.artifact_type} | `{c.column}` | {c.role_guess} | {c.files_seen} | {c.nonzero_files} | {c.min_value} | {c.max_value} | `{c.example_file}` |")
    else:
        lines.append("No numeric column candidates found.")

    lines += ["", "## Artifact schema sample", ""]
    if records:
        lines += ["| Artifact | Rows | Cols | PnL cols | Return cols | Equity cols | Summary cols |", "|---|---:|---:|---|---|---|---|"]
        for r in records[:40]:
            lines.append(f"| `{r.filename}` | {r.rows} | {r.columns_count} | {r.possible_pnl_columns} | {r.possible_return_columns} | {r.possible_equity_columns} | {r.possible_summary_columns} |")
    else:
        lines.append("No artifacts loaded.")

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
    lines += ["", "## Interpretation", "", "This module determines whether the ret60 artifacts contain real metric columns or only signal/event rows. If only signal/event rows exist, exact rule semantics still require scanner code or regeneration.", ""]
    write_text(path, "\n".join(lines))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Inspect ret60 artifact CSV schemas")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    p.add_argument("--artifact_dir", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--sample_rows", type=int, default=200000, help="0 means full read")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    candidate = safe_key(args.candidate)
    artifact_dir = artifact_dir_for(workspace, args.artifact_dir)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_artifact_schema_inspector"
    out_dir = out_root / f"ret60_artifact_schema_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    warnings: List[str] = []
    if not artifact_dir.exists():
        paths: List[Path] = []
        warnings.append(f"artifact dir not found: {artifact_dir}")
    else:
        paths = sorted(artifact_dir.glob(f"*{candidate}*.csv"))

    records = [inspect_file(p, None if int(args.sample_rows) <= 0 else int(args.sample_rows)) for p in paths]
    candidates = aggregate_column_candidates(records)
    status, next_action, reasons, status_warnings = build_status(records, candidates)
    warnings.extend(status_warnings)
    metric_cols = [c for c in candidates if c.role_guess in {"POSSIBLE_PNL", "POSSIBLE_RETURN_OR_FEATURE", "POSSIBLE_EQUITY", "POSSIBLE_SUMMARY_METRIC"}]
    signal_cols = [c for c in candidates if c.role_guess == "POSSIBLE_SIGNAL_OR_CONTEXT"]
    variants = sorted(set(r.variant_key for r in records if r.variant_key))

    state = InspectorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        artifact_dir=str(artifact_dir),
        candidate=candidate,
        artifacts_seen=len(paths),
        artifacts_loaded=len([r for r in records if r.rows > 0]),
        artifact_types=" | ".join(sorted(set(r.artifact_type for r in records))),
        unique_variants=len(variants),
        candidate_metric_columns=len(metric_cols),
        candidate_signal_columns=len(signal_cols),
        inspector_status=status,
        next_action=next_action,
        logger_build_allowed=False,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        reasons=["Ret60 artifact schemas were inspected offline."] + reasons,
        warnings=warnings,
        hard_rules=[
            "Schema inspector never starts paper/live.",
            "Schema inspector never mutates active config.",
            "Schema inspector never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Schema inspector cannot approve logger build by itself.",
            "Live remains blocked.",
        ],
    )

    state_path = out_dir / "ret60_artifact_schema_inspector_state.json"
    write_json(state_path, {"state": asdict(state), "records": [asdict(r) for r in records], "column_candidates": [asdict(c) for c in candidates]})
    records_df(records).to_csv(out_dir / "ret60_artifact_schema_inventory.csv", index=False)
    records_df(candidates).to_csv(out_dir / "ret60_artifact_column_candidates.csv", index=False)
    write_report(out_dir / "ret60_artifact_schema_inspector_report.md", state, records, candidates)

    print("EDGE FACTORY RET60 ARTIFACT SCHEMA INSPECTOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"artifact_dir: {artifact_dir}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"inspector_status: {state.inspector_status}")
    print(f"next_action: {state.next_action}")
    print(f"artifacts_seen: {state.artifacts_seen}")
    print(f"artifacts_loaded: {state.artifacts_loaded}")
    print(f"artifact_types: {state.artifact_types}")
    print(f"unique_variants: {state.unique_variants}")
    print(f"candidate_metric_columns: {state.candidate_metric_columns}")
    print(f"candidate_signal_columns: {state.candidate_signal_columns}")
    print("logger_build_allowed: False")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("")
    print("TOP COLUMN CANDIDATES")
    print("-" * 100)
    for c in candidates[:25]:
        print(f"score={c.score:8.2f} type={c.artifact_type:28s} role={c.role_guess:28s} files={c.files_seen:3d} nonzero={c.nonzero_files:3d} min={c.min_value: .6g} max={c.max_value: .6g} col={c.column}")
        print(f"     example={c.example_file}")
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
    print(f"Report : {out_dir / 'ret60_artifact_schema_inspector_report.md'}")
    print(f"State  : {state_path}")
    print(f"Columns: {out_dir / 'ret60_artifact_column_candidates.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
