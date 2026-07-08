#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 M-SEMANTIC RESOLVER v1
=========================================

Purpose
-------
Resolve the last blocker from ret60 semantic contract audit:
    m_threshold conflict: expected signal_ret60_bps >= 75, observed min negative.

The prior assumption was too narrow. For ret60_reversal_short, m75 may mean one of:
    - signal_ret60_bps >= +75
    - signal_ret60_bps <= -75
    - abs(signal_ret60_bps) >= 75
    - another ret60/range column threshold
    - filename search bucket, not a runtime threshold

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
    - read latest selected ret60 parser v2 / semantic audit artifacts
    - load selected combined_sim and session_trades CSVs
    - inspect all ret60/range/signal numeric columns
    - test candidate m-threshold interpretations
    - produce a conservative semantic verdict
    - allow blueprint only if an m-rule explains selected rows consistently

Run:
    python "C:\Users\alike\edge_factory_ret60_m_semantic_resolver.py"

Core rule
---------
Even if m is resolved, this is still not runtime approval. Shadow start remains blocked.
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
    r"(?P<candidate>ret60_reversal_short)_h(?P<h>\d+)_m(?P<m>\d+)_hold(?P<hold>\d+)_delay(?P<delay>\d+)_extra(?P<extra>\d+)",
    re.IGNORECASE,
)

COLUMN_HINTS = ["ret60", "ret_60", "60m", "range", "signal", "score", "z", "rank"]
PREFERRED_COLS = ["signal_ret60_bps", "range_mean_60m_bps", "ret60_bps", "ret_60m_bps"]


@dataclass
class SelectedPaths:
    candidate_key: str
    variant_key: str
    h: int
    m: int
    hold: int
    delay: int
    extra: int
    combined_path: Optional[str]
    session_path: Optional[str]
    parser_v2_state: Optional[str]
    semantic_audit_state: Optional[str]


@dataclass
class ColumnStats:
    artifact_type: str
    column: str
    rows: int
    non_null: int
    min_value: float
    q01: float
    q05: float
    q10: float
    median: float
    q90: float
    q95: float
    q99: float
    max_value: float
    mean_value: float
    negative_share: float
    positive_share: float
    abs_ge_m_share: float
    ge_pos_m_share: float
    le_neg_m_share: float
    warnings: List[str]


@dataclass
class RuleTest:
    artifact_type: str
    column: str
    rule_expression: str
    rows: int
    pass_count: int
    pass_share: float
    fail_count: int
    selectivity_note: str
    confidence: float
    status: str
    warnings: List[str]


@dataclass
class MSemanticVerdict:
    candidate_key: str
    variant_key: str
    m_param: int
    verdict_status: str
    selected_rule_expression: Optional[str]
    selected_column: Optional[str]
    selected_artifact_type: Optional[str]
    selected_pass_share: float
    m_semantics_confidence: float
    blueprint_allowed: bool
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    reasons: List[str]
    blockers: List[str]
    warnings: List[str]


@dataclass
class ResolverState:
    generated_at: str
    workspace: str
    candidate: str
    variant_key: Optional[str]
    combined_path: Optional[str]
    session_path: Optional[str]
    columns_tested: int
    rules_tested: int
    verdict_status: str
    blueprint_allowed: bool
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


def latest_child_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_json_optional(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def parse_params(variant: str) -> Optional[Dict[str, int]]:
    m = PARAM_RE.search(variant or "")
    if not m:
        return None
    return {
        "h": int(m.group("h")),
        "m": int(m.group("m")),
        "hold": int(m.group("hold")),
        "delay": int(m.group("delay")),
        "extra": int(m.group("extra")),
    }


def latest_parser_v2_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_rule_artifact_parser_v2", "ret60_rule_artifacts_v2_")
    if not d:
        return None
    p = d / "ret60_rule_artifact_parser_v2_state.json"
    return p if p.exists() else None


def latest_semantic_state(workspace: Path) -> Optional[Path]:
    d = latest_child_dir(workspace / "edge_factory_ret60_semantic_contract_auditor", "ret60_semantic_audit_")
    if not d:
        return None
    p = d / "ret60_semantic_contract_audit_state.json"
    return p if p.exists() else None


def load_selected_paths(workspace: Path, explicit_parser_state: Optional[str], explicit_semantic_state: Optional[str]) -> Tuple[Optional[SelectedPaths], List[str]]:
    warnings: List[str] = []
    parser_path = Path(explicit_parser_state) if explicit_parser_state else latest_parser_v2_state(workspace)
    semantic_path = Path(explicit_semantic_state) if explicit_semantic_state else latest_semantic_state(workspace)

    parser_obj = read_json_optional(parser_path)
    contract = parser_obj.get("contract", {}) if isinstance(parser_obj.get("contract"), dict) else {}
    variant = str(contract.get("selected_variant_key") or "")
    selected_artifact = str(contract.get("selected_artifact_path") or "")

    if not variant:
        # Try semantic state fallback.
        sem_obj = read_json_optional(semantic_path)
        sc = sem_obj.get("selected_contract", {}) if isinstance(sem_obj.get("selected_contract"), dict) else {}
        variant = str(sc.get("selected_variant_key") or "")
        selected_artifact = str(sc.get("selected_artifact_path") or selected_artifact or "")

    params = parse_params(variant)
    if not params:
        warnings.append("selected variant params could not be parsed")
        return None, warnings

    combined = selected_artifact if "combined_sim_session_first" in selected_artifact else None
    session = None
    if selected_artifact:
        maybe_session = selected_artifact.replace("combined_sim_session_first_", "session_trades_")
        maybe_combined = selected_artifact.replace("session_trades_", "combined_sim_session_first_")
        if Path(maybe_session).exists():
            session = maybe_session
        if combined is None and Path(maybe_combined).exists():
            combined = maybe_combined
    if combined and not Path(combined).exists():
        warnings.append(f"combined artifact missing: {combined}")
    if session and not Path(session).exists():
        warnings.append(f"session artifact missing: {session}")

    return SelectedPaths(
        candidate_key=DEFAULT_CANDIDATE,
        variant_key=variant,
        h=params["h"],
        m=params["m"],
        hold=params["hold"],
        delay=params["delay"],
        extra=params["extra"],
        combined_path=combined,
        session_path=session,
        parser_v2_state=str(parser_path) if parser_path else None,
        semantic_audit_state=str(semantic_path) if semantic_path else None,
    ), warnings


def candidate_columns(df: pd.DataFrame) -> List[str]:
    cols = []
    for c in df.columns:
        low = str(c).lower()
        if any(h in low for h in COLUMN_HINTS):
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().sum() >= max(5, int(0.5 * len(df))):
                cols.append(str(c))
    cols = sorted(cols, key=lambda c: (c not in PREFERRED_COLS, c))
    return cols


def calc_stats(df: pd.DataFrame, artifact_type: str, col: str, m: int) -> Optional[ColumnStats]:
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return None
    warnings: List[str] = []
    if s.nunique() <= 1:
        warnings.append("constant column")
    return ColumnStats(
        artifact_type=artifact_type,
        column=col,
        rows=int(len(df)),
        non_null=int(len(s)),
        min_value=round(float(s.min()), 8),
        q01=round(float(s.quantile(0.01)), 8),
        q05=round(float(s.quantile(0.05)), 8),
        q10=round(float(s.quantile(0.10)), 8),
        median=round(float(s.median()), 8),
        q90=round(float(s.quantile(0.90)), 8),
        q95=round(float(s.quantile(0.95)), 8),
        q99=round(float(s.quantile(0.99)), 8),
        max_value=round(float(s.max()), 8),
        mean_value=round(float(s.mean()), 8),
        negative_share=round(float((s < 0).mean()), 8),
        positive_share=round(float((s > 0).mean()), 8),
        abs_ge_m_share=round(float((s.abs() >= m).mean()), 8),
        ge_pos_m_share=round(float((s >= m).mean()), 8),
        le_neg_m_share=round(float((s <= -m).mean()), 8),
        warnings=warnings,
    )


def add_rule_tests(df: pd.DataFrame, artifact_type: str, col: str, m: int) -> List[RuleTest]:
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return []
    rules: List[Tuple[str, pd.Series, str]] = [
        (f"{col} >= {m}", s >= m, "positive threshold"),
        (f"{col} <= -{m}", s <= -m, "negative threshold"),
        (f"abs({col}) >= {m}", s.abs() >= m, "absolute magnitude threshold"),
        (f"{col} <= {m}", s <= m, "upper-bound threshold; may be non-selective"),
        (f"{col} >= -{m}", s >= -m, "lower-bound threshold; may be non-selective"),
    ]
    out: List[RuleTest] = []
    for expr, mask, note in rules:
        pass_count = int(mask.sum())
        rows = int(len(mask))
        share = pass_count / max(1, rows)
        fail_count = rows - pass_count
        if share >= 0.999:
            status = "CONSISTENT_WITH_SELECTED_ROWS"
            confidence = 0.85
        elif share >= 0.95:
            status = "MOSTLY_CONSISTENT_WITH_SELECTED_ROWS"
            confidence = 0.65
        elif share <= 0.01:
            status = "REJECTED_BY_SELECTED_ROWS"
            confidence = 0.0
        else:
            status = "PARTIAL_NOT_EXACT"
            confidence = 0.25
        # Prefer selective-looking rules, penalize trivially broad upper/lower bounds.
        warnings: List[str] = []
        if expr.endswith(f"<= {m}") or expr.endswith(f">= -{m}"):
            warnings.append("broad rule can explain selected rows but may not be the actual scanner filter")
            confidence *= 0.5
        out.append(RuleTest(
            artifact_type=artifact_type,
            column=col,
            rule_expression=expr,
            rows=rows,
            pass_count=pass_count,
            pass_share=round(share, 8),
            fail_count=fail_count,
            selectivity_note=note,
            confidence=round(confidence, 6),
            status=status,
            warnings=warnings,
        ))
    return out


def resolve_m(paths: SelectedPaths, dfs: Dict[str, pd.DataFrame]) -> Tuple[MSemanticVerdict, List[ColumnStats], List[RuleTest]]:
    stats: List[ColumnStats] = []
    tests: List[RuleTest] = []
    for atype, df in dfs.items():
        for col in candidate_columns(df):
            st = calc_stats(df, atype, col, paths.m)
            if st:
                stats.append(st)
            tests.extend(add_rule_tests(df, atype, col, paths.m))

    # Highest-confidence exact-ish tests first. Prefer session rows, preferred columns, non-broad rules.
    def rank(t: RuleTest) -> Tuple[float, int, int, float]:
        preferred = 1 if t.column in PREFERRED_COLS else 0
        session = 1 if t.artifact_type == "session" else 0
        broad_penalty = 1 if t.warnings else 0
        return (t.confidence, preferred, session, t.pass_share - broad_penalty)

    consistent = [t for t in tests if t.status in {"CONSISTENT_WITH_SELECTED_ROWS", "MOSTLY_CONSISTENT_WITH_SELECTED_ROWS"}]
    consistent.sort(key=rank, reverse=True)
    selected = consistent[0] if consistent else None

    reasons: List[str] = []
    blockers: List[str] = []
    warnings: List[str] = []

    if selected:
        reasons.append(f"m-param candidate rule found: {selected.rule_expression} on {selected.artifact_type}")
        # Strongest acceptable rules: direct signal_ret60 with positive/negative/abs threshold.
        direct = selected.column == "signal_ret60_bps" and not selected.warnings and selected.pass_share >= 0.95
        if direct:
            status = "M_SEMANTICS_RESOLVED_DIRECT_SIGNAL_RULE"
            blueprint = True
            conf = selected.confidence
        else:
            status = "M_SEMANTICS_PARTIAL_RULE_CANDIDATE"
            blueprint = True if selected.pass_share >= 0.999 and selected.confidence >= 0.5 else False
            conf = selected.confidence
            warnings.append("selected m-rule is not a direct high-confidence signal_ret60 rule or may be broad")
    else:
        status = "M_SEMANTICS_BLOCKED_NO_CONSISTENT_RULE"
        blueprint = False
        conf = 0.0
        blockers.append("no tested m-threshold interpretation explains selected artifact rows")

    # Add diagnostic warning if direct positive rule failed but negative/abs works.
    direct_tests = [t for t in tests if t.column == "signal_ret60_bps"]
    pos = next((t for t in direct_tests if t.rule_expression == f"signal_ret60_bps >= {paths.m}"), None)
    neg = next((t for t in direct_tests if t.rule_expression == f"signal_ret60_bps <= -{paths.m}"), None)
    absv = next((t for t in direct_tests if t.rule_expression == f"abs(signal_ret60_bps) >= {paths.m}"), None)
    if pos and pos.pass_share < 0.5:
        warnings.append(f"old assumption signal_ret60_bps >= {paths.m} is weak: pass_share={pos.pass_share}")
    if neg and neg.pass_share >= 0.95:
        reasons.append(f"negative-threshold interpretation is consistent: {neg.rule_expression} pass_share={neg.pass_share}")
    if absv and absv.pass_share >= 0.95:
        reasons.append(f"absolute-threshold interpretation is consistent: {absv.rule_expression} pass_share={absv.pass_share}")

    return MSemanticVerdict(
        candidate_key=paths.candidate_key,
        variant_key=paths.variant_key,
        m_param=paths.m,
        verdict_status=status,
        selected_rule_expression=selected.rule_expression if selected else None,
        selected_column=selected.column if selected else None,
        selected_artifact_type=selected.artifact_type if selected else None,
        selected_pass_share=selected.pass_share if selected else 0.0,
        m_semantics_confidence=round(conf, 6),
        blueprint_allowed=blueprint,
        logger_build_allowed=False,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        reasons=list(dict.fromkeys(reasons)),
        blockers=list(dict.fromkeys(blockers)),
        warnings=list(dict.fromkeys(warnings)),
    ), stats, tests


def records_df(items: List[Any]) -> pd.DataFrame:
    rows = []
    for x in items:
        d = asdict(x)
        for k, v in list(d.items()):
            if isinstance(v, list):
                d[k] = " | ".join(str(i) for i in v)
        rows.append(d)
    return pd.DataFrame(rows)


def write_outputs(workspace: Path, out_dir: Path, state: ResolverState, paths: Optional[SelectedPaths], verdict: Optional[MSemanticVerdict], stats: List[ColumnStats], tests: List[RuleTest]) -> None:
    persistent = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes" / DEFAULT_CANDIDATE / "m_semantics"
    persistent.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": asdict(state),
        "selected_paths": asdict(paths) if paths else None,
        "m_semantic_verdict": asdict(verdict) if verdict else None,
        "column_stats": [asdict(s) for s in stats],
        "rule_tests": [asdict(t) for t in tests],
    }
    for d in [out_dir, persistent]:
        write_json(d / "ret60_m_semantic_resolver_state.json", payload)
        if verdict:
            write_json(d / "ret60_m_semantic_contract.json", {"m_semantic_verdict": asdict(verdict)})
        records_df(stats).to_csv(d / "ret60_m_column_stats.csv", index=False)
        records_df(tests).to_csv(d / "ret60_m_rule_tests.csv", index=False)

    md = f"""# Ret60 M-Semantic Resolver

Status: **{state.verdict_status}**

## Verdict

- Variant: `{paths.variant_key if paths else None}`
- m: `{paths.m if paths else None}`
- Selected rule: `{verdict.selected_rule_expression if verdict else None}`
- Pass share: `{verdict.selected_pass_share if verdict else None}`
- Blueprint allowed: `{verdict.blueprint_allowed if verdict else False}`
- Logger build allowed: `False`
- Shadow start allowed: `False`
- Live allowed: `False`

## Reasons

```text
{chr(10).join(verdict.reasons if verdict else state.reasons)}
```

## Blockers

```text
{chr(10).join(verdict.blockers if verdict else []) or 'none'}
```

## Warnings

```text
{chr(10).join((state.warnings if state else []) + (verdict.warnings if verdict else [])) or 'none'}
```
"""
    for d in [out_dir, persistent]:
        write_text(d / "ret60_m_semantic_resolver_report.md", md)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Resolve ret60 m parameter semantics")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    p.add_argument("--parser_state", default=None)
    p.add_argument("--semantic_state", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    candidate = safe_key(args.candidate)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_m_semantic_resolver"
    out_dir = out_root / f"ret60_m_semantics_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    warnings: List[str] = []
    paths, load_warnings = load_selected_paths(workspace, args.parser_state, args.semantic_state)
    warnings.extend(load_warnings)

    dfs: Dict[str, pd.DataFrame] = {}
    if paths:
        for atype, pstr in [("combined", paths.combined_path), ("session", paths.session_path)]:
            if pstr and Path(pstr).exists():
                try:
                    dfs[atype] = pd.read_csv(pstr)
                except Exception as e:
                    warnings.append(f"failed to read {atype}: {e}")
            else:
                warnings.append(f"missing {atype} artifact")

    if paths and dfs:
        verdict, stats, tests = resolve_m(paths, dfs)
        verdict_status = verdict.verdict_status
        blueprint = verdict.blueprint_allowed
    else:
        verdict = None
        stats = []
        tests = []
        verdict_status = "M_SEMANTICS_BLOCKED_NO_ARTIFACTS"
        blueprint = False
        warnings.append("could not load selected artifacts for m semantic resolution")

    state = ResolverState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=candidate,
        variant_key=paths.variant_key if paths else None,
        combined_path=paths.combined_path if paths else None,
        session_path=paths.session_path if paths else None,
        columns_tested=len(stats),
        rules_tested=len(tests),
        verdict_status=verdict_status,
        blueprint_allowed=blueprint,
        logger_build_allowed=False,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        reasons=["M-semantic resolver tested threshold interpretations on selected ret60 artifacts."],
        warnings=warnings,
        hard_rules=[
            "M-semantic resolver never starts paper/live.",
            "M-semantic resolver never mutates active config.",
            "M-semantic resolver never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Blueprint permission is not runtime permission.",
            "Shadow start still requires sandbox logger, preflight, and manual approval.",
            "Live remains blocked.",
        ],
    )

    write_outputs(workspace, out_dir, state, paths, verdict, stats, tests)

    print("EDGE FACTORY RET60 M-SEMANTIC RESOLVER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"variant: {paths.variant_key if paths else None}")
    print(f"combined_path: {paths.combined_path if paths else None}")
    print(f"session_path : {paths.session_path if paths else None}")
    print(f"verdict_status: {state.verdict_status}")
    print(f"columns_tested: {state.columns_tested}")
    print(f"rules_tested: {state.rules_tested}")
    if verdict:
        print(f"selected_rule: {verdict.selected_rule_expression}")
        print(f"selected_artifact_type: {verdict.selected_artifact_type}")
        print(f"selected_pass_share: {verdict.selected_pass_share:.6f}")
        print(f"m_semantics_confidence: {verdict.m_semantics_confidence:.3f}")
    print(f"blueprint_allowed: {state.blueprint_allowed}")
    print("logger_build_allowed: False")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("")
    print("TOP RULE TESTS")
    print("-" * 100)
    for t in sorted(tests, key=lambda x: (x.confidence, x.pass_share), reverse=True)[:20]:
        print(f"conf={t.confidence:.3f} pass={t.pass_share:.2%} status={t.status:36s} type={t.artifact_type:8s} rule={t.rule_expression}")
        if t.warnings:
            print(f"     warnings: {' | '.join(t.warnings)}")
    if verdict and verdict.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in verdict.blockers:
            print(f"- {b}")
    all_warnings = state.warnings + (verdict.warnings if verdict else [])
    if all_warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in all_warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'ret60_m_semantic_resolver_report.md'}")
    print(f"State  : {out_dir / 'ret60_m_semantic_resolver_state.json'}")
    print(f"Rules  : {out_dir / 'ret60_m_rule_tests.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
