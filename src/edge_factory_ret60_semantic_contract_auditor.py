#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY RET60 SEMANTIC CONTRACT AUDITOR v1
===============================================

Purpose
-------
Audit the selected ret60_reversal_short v2 artifact contract and try to confirm the
remaining runtime semantics:
    - m_param      -> signal_ret60_bps threshold
    - extra_param  -> extra_slip_bps
    - delay_param  -> signal_time/event_time to entry_time delta, if timestamps exist
    - hold_param   -> entry_time to exit_time delta, if timestamps exist
    - h_param      -> hour/session filter, if hour/session columns or timestamp hours exist

This module is the safe next step after:
    edge_factory_ret60_rule_artifact_parser_v2.py

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
    - read the selected v2 ret60 rule contract
    - load selected combined_sim and matching session_trades artifacts
    - inspect timestamp and hour/session columns
    - compute candidate delay/hold deltas where possible
    - produce a semantic contract verdict
    - write a blueprint-readiness packet, not a runtime approval

Run:
    python "C:\Users\alike\edge_factory_ret60_semantic_contract_auditor.py"

Core rule
---------
Even if this confirms semantics, shadow start remains blocked until a sandbox-only logger,
preflight, and explicit manual approval exist.
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

TIME_HINTS = ["time", "timestamp", "date", "datetime"]
SIGNAL_TIME_HINTS = ["signal", "event", "candle", "source"]
ENTRY_TIME_HINTS = ["entry", "open", "start"]
EXIT_TIME_HINTS = ["exit", "close", "end"]
HOUR_HINTS = ["hour", "session", "h_param", "signal_hour", "entry_hour", "exit_hour"]

PARAM_RE = re.compile(
    r"(?P<candidate>ret60_reversal_short)_h(?P<h>\d+)_m(?P<m>\d+)_hold(?P<hold>\d+)_delay(?P<delay>\d+)_extra(?P<extra>\d+)",
    re.IGNORECASE,
)


@dataclass
class SelectedContract:
    candidate_key: str
    selected_variant_key: str
    selected_artifact_path: str
    combined_path: Optional[str]
    session_path: Optional[str]
    h_param: int
    m_param: int
    hold_param: int
    delay_param: int
    extra_param: int
    entry_rule_hypothesis: str
    exit_rule_hypothesis: str


@dataclass
class DeltaEvidence:
    artifact_type: str
    left_col: str
    right_col: str
    rows: int
    median_minutes: Optional[float]
    min_minutes: Optional[float]
    max_minutes: Optional[float]
    match_target: Optional[str]
    match_status: str
    note: str


@dataclass
class HourEvidence:
    artifact_type: str
    source_col: str
    method: str
    rows: int
    top_values: str
    target_h: int
    target_share: float
    match_status: str


@dataclass
class SemanticComponent:
    component: str
    target_value: str
    observed_value: str
    status: str
    confidence: float
    evidence: str


@dataclass
class SemanticAuditResult:
    candidate_key: str
    selected_variant_key: str
    audit_status: str
    blueprint_allowed: bool
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    confirmed_components: int
    total_components: int
    components: List[SemanticComponent]
    blockers: List[str]
    warnings: List[str]
    reasons: List[str]


@dataclass
class AuditorState:
    generated_at: str
    workspace: str
    candidate: str
    parser_v2_state_path: Optional[str]
    selected_artifact_path: Optional[str]
    combined_path: Optional[str]
    session_path: Optional[str]
    artifacts_loaded: int
    audit_status: str
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


def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def latest_parser_v2_dir(workspace: Path) -> Optional[Path]:
    return latest_child_dir(workspace / "edge_factory_ret60_rule_artifact_parser_v2", "ret60_rule_artifacts_v2_")


def parse_params_from_variant(variant: str) -> Optional[Dict[str, int]]:
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


def load_selected_contract(workspace: Path, explicit_state: Optional[str]) -> Tuple[Optional[SelectedContract], Optional[Path], List[str]]:
    warnings: List[str] = []
    state_path = Path(explicit_state) if explicit_state else None
    if state_path is None:
        d = latest_parser_v2_dir(workspace)
        if d:
            state_path = d / "ret60_rule_artifact_parser_v2_state.json"
    obj = read_json(state_path)
    if not obj:
        warnings.append("parser v2 state not found or unreadable")
        return None, state_path, warnings

    contract_obj = obj.get("contract", {}) if isinstance(obj.get("contract"), dict) else {}
    variant = str(contract_obj.get("selected_variant_key") or "")
    selected_artifact = str(contract_obj.get("selected_artifact_path") or "")
    params = parse_params_from_variant(variant)
    if not params:
        warnings.append("selected variant params could not be parsed")
        return None, state_path, warnings

    combined_path = selected_artifact if "combined_sim_session_first" in selected_artifact else None
    session_path = None
    if selected_artifact:
        candidate_session = selected_artifact.replace("combined_sim_session_first_", "session_trades_")
        if Path(candidate_session).exists():
            session_path = candidate_session
    if combined_path is None and selected_artifact:
        candidate_combined = selected_artifact.replace("session_trades_", "combined_sim_session_first_")
        if Path(candidate_combined).exists():
            combined_path = candidate_combined

    return SelectedContract(
        candidate_key=safe_key(contract_obj.get("candidate_key") or DEFAULT_CANDIDATE),
        selected_variant_key=variant,
        selected_artifact_path=selected_artifact,
        combined_path=combined_path,
        session_path=session_path,
        h_param=params["h"],
        m_param=params["m"],
        hold_param=params["hold"],
        delay_param=params["delay"],
        extra_param=params["extra"],
        entry_rule_hypothesis=str(contract_obj.get("entry_rule_hypothesis") or ""),
        exit_rule_hypothesis=str(contract_obj.get("exit_rule_hypothesis") or ""),
    ), state_path, warnings


def parse_time_series(s: pd.Series) -> pd.Series:
    num = pd.to_numeric(s, errors="coerce")
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
        return pd.to_datetime(num, unit=unit, errors="coerce", utc=True)
    return pd.to_datetime(s, errors="coerce", utc=True)


def detect_time_cols(df: pd.DataFrame) -> List[str]:
    out = []
    for c in df.columns:
        low = str(c).lower()
        if any(h in low for h in TIME_HINTS):
            try:
                ts = parse_time_series(df[c])
                if ts.notna().sum() >= max(5, int(0.25 * len(df))):
                    out.append(str(c))
            except Exception:
                pass
    return out


def detect_hour_cols(df: pd.DataFrame) -> List[str]:
    out = []
    for c in df.columns:
        low = str(c).lower()
        if any(h in low for h in HOUR_HINTS):
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().sum() >= max(5, int(0.25 * len(df))):
                out.append(str(c))
    return out


def classify_time_col(col: str) -> str:
    low = col.lower()
    if any(h in low for h in ENTRY_TIME_HINTS):
        return "entry"
    if any(h in low for h in EXIT_TIME_HINTS):
        return "exit"
    if any(h in low for h in SIGNAL_TIME_HINTS):
        return "signal"
    return "generic"


def delta_minutes(df: pd.DataFrame, left: str, right: str) -> Tuple[int, Optional[float], Optional[float], Optional[float]]:
    a = parse_time_series(df[left])
    b = parse_time_series(df[right])
    tmp = pd.DataFrame({"a": a, "b": b}).dropna()
    if tmp.empty:
        return 0, None, None, None
    d = (tmp["b"] - tmp["a"]).dt.total_seconds() / 60.0
    d = d.dropna()
    if d.empty:
        return 0, None, None, None
    return int(len(d)), float(d.median()), float(d.min()), float(d.max())


def match_delta(median: Optional[float], target: int) -> str:
    if median is None:
        return "NO_EVIDENCE"
    if abs(median - target) <= 1e-6:
        return "EXACT_MATCH"
    if abs(median - target) <= 1.0:
        return "NEAR_MATCH_WITHIN_1_MIN"
    if target == 720 and abs(median - 720) <= 5:
        return "NEAR_HOLD_MATCH_WITHIN_5_MIN"
    return "NO_MATCH"


def audit_deltas(df: pd.DataFrame, artifact_type: str, contract: SelectedContract) -> List[DeltaEvidence]:
    cols = detect_time_cols(df)
    out: List[DeltaEvidence] = []
    for left in cols:
        for right in cols:
            if left == right:
                continue
            left_kind = classify_time_col(left)
            right_kind = classify_time_col(right)
            if left_kind == "exit" or right_kind == "signal":
                continue
            rows, med, mn, mx = delta_minutes(df, left, right)
            if rows <= 0 or med is None:
                continue
            target = None
            note = ""
            if left_kind == "entry" and right_kind == "exit":
                target = "hold"
                status = match_delta(med, contract.hold_param)
                note = f"entry-to-exit candidate for hold{contract.hold_param}"
            elif left_kind in {"signal", "generic"} and right_kind == "entry":
                target = "delay"
                status = match_delta(med, contract.delay_param)
                note = f"signal/generic-to-entry candidate for delay{contract.delay_param}"
            else:
                status = "UNCLASSIFIED_DELTA"
            out.append(DeltaEvidence(
                artifact_type=artifact_type,
                left_col=left,
                right_col=right,
                rows=rows,
                median_minutes=round(med, 8),
                min_minutes=round(mn, 8) if mn is not None else None,
                max_minutes=round(mx, 8) if mx is not None else None,
                match_target=target,
                match_status=status,
                note=note,
            ))
    out.sort(key=lambda x: (x.match_status not in {"EXACT_MATCH", "NEAR_MATCH_WITHIN_1_MIN", "NEAR_HOLD_MATCH_WITHIN_5_MIN"}, x.match_target or "", abs((x.median_minutes or 0))))
    return out


def hour_evidence_from_df(df: pd.DataFrame, artifact_type: str, contract: SelectedContract) -> List[HourEvidence]:
    out: List[HourEvidence] = []
    for col in detect_hour_cols(df):
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            continue
        rounded = s.round().astype(int)
        vc = rounded.value_counts().head(10)
        share = float((rounded == contract.h_param).mean())
        status = "TARGET_H_DOMINANT" if share >= 0.90 else ("TARGET_H_PRESENT" if share > 0 else "TARGET_H_NOT_PRESENT")
        out.append(HourEvidence(
            artifact_type=artifact_type,
            source_col=col,
            method="numeric_hour_column",
            rows=int(len(rounded)),
            top_values=" | ".join(f"{int(k)}:{int(v)}" for k, v in vc.items()),
            target_h=contract.h_param,
            target_share=round(share, 6),
            match_status=status,
        ))
    for col in detect_time_cols(df):
        ts = parse_time_series(df[col]).dropna()
        if ts.empty:
            continue
        hours = ts.dt.hour
        vc = hours.value_counts().head(10)
        share = float((hours == contract.h_param).mean())
        status = "TARGET_H_DOMINANT" if share >= 0.90 else ("TARGET_H_PRESENT" if share > 0 else "TARGET_H_NOT_PRESENT")
        out.append(HourEvidence(
            artifact_type=artifact_type,
            source_col=col,
            method="derived_utc_hour_from_timestamp",
            rows=int(len(hours)),
            top_values=" | ".join(f"{int(k)}:{int(v)}" for k, v in vc.items()),
            target_h=contract.h_param,
            target_share=round(share, 6),
            match_status=status,
        ))
    out.sort(key=lambda x: (x.match_status != "TARGET_H_DOMINANT", -x.target_share))
    return out


def component(component: str, target: Any, observed: Any, status: str, confidence: float, evidence: str) -> SemanticComponent:
    return SemanticComponent(str(component), str(target), str(observed), str(status), float(confidence), str(evidence))


def audit_semantics(contract: SelectedContract, dfs: Dict[str, pd.DataFrame], deltas: List[DeltaEvidence], hours: List[HourEvidence]) -> SemanticAuditResult:
    comps: List[SemanticComponent] = []
    blockers: List[str] = []
    warnings: List[str] = []
    reasons: List[str] = []

    # m threshold
    sig_sources = []
    for atype, df in dfs.items():
        if "signal_ret60_bps" in df.columns:
            s = pd.to_numeric(df["signal_ret60_bps"], errors="coerce").dropna()
            if not s.empty:
                sig_sources.append((atype, float(s.min()), float(s.max()), float(s.median())))
    if sig_sources:
        atype, mn, mx, med = sig_sources[0]
        if mn >= contract.m_param - 1e-9:
            comps.append(component("m_threshold", f"signal_ret60_bps >= {contract.m_param}", f"{atype} min={mn} median={med} max={mx}", "CONFIRMED", 1.0, "signal_ret60_bps minimum respects m parameter"))
            reasons.append("m parameter confirmed as signal_ret60_bps threshold")
        else:
            comps.append(component("m_threshold", f">= {contract.m_param}", f"min={mn}", "CONFLICT", 0.0, "observed min below m parameter"))
            blockers.append("m threshold conflicts with observed signal_ret60_bps")
    else:
        comps.append(component("m_threshold", f">= {contract.m_param}", "missing signal_ret60_bps", "UNCONFIRMED", 0.0, "no signal_ret60_bps column"))
        blockers.append("m threshold unconfirmed")

    # extra slip
    extra_sources = []
    for atype, df in dfs.items():
        if "extra_slip_bps" in df.columns:
            vals = sorted(pd.to_numeric(df["extra_slip_bps"], errors="coerce").dropna().unique().tolist())
            if vals:
                extra_sources.append((atype, [float(x) for x in vals[:20]]))
    if extra_sources:
        atype, vals = extra_sources[0]
        if len(vals) == 1 and abs(vals[0] - contract.extra_param) <= 1e-9:
            comps.append(component("extra_slip", contract.extra_param, vals, "CONFIRMED", 1.0, f"{atype}.extra_slip_bps equals extra param"))
            reasons.append("extra parameter confirmed as extra_slip_bps")
        else:
            comps.append(component("extra_slip", contract.extra_param, vals, "CONFLICT_OR_MIXED", 0.25, "extra_slip_bps values do not uniquely match extra"))
            warnings.append("extra_slip has mixed/conflicting values")
    else:
        status = "CONFIRMED_ASSUMED_ZERO" if contract.extra_param == 0 else "UNCONFIRMED"
        conf = 0.75 if contract.extra_param == 0 else 0.0
        comps.append(component("extra_slip", contract.extra_param, "no extra_slip_bps column", status, conf, "zero extra may mean no extra slip column"))
        if contract.extra_param != 0:
            blockers.append("extra_slip unconfirmed")

    # hold
    hold_matches = [d for d in deltas if d.match_target == "hold" and d.match_status in {"EXACT_MATCH", "NEAR_MATCH_WITHIN_1_MIN", "NEAR_HOLD_MATCH_WITHIN_5_MIN"}]
    if hold_matches:
        d = hold_matches[0]
        comps.append(component("hold", contract.hold_param, f"{d.artifact_type}: {d.left_col}->{d.right_col} median={d.median_minutes}", "CONFIRMED_FROM_TIMESTAMPS", 1.0, d.note))
        reasons.append("hold parameter confirmed from timestamp delta")
    else:
        comps.append(component("hold", contract.hold_param, "no matching entry->exit timestamp delta", "UNCONFIRMED", 0.25, "filename param exists but timestamp proof missing"))
        blockers.append("hold exit implementation must be confirmed or implemented exactly from scanner")

    # delay
    delay_matches = [d for d in deltas if d.match_target == "delay" and d.match_status in {"EXACT_MATCH", "NEAR_MATCH_WITHIN_1_MIN"}]
    if delay_matches:
        d = delay_matches[0]
        comps.append(component("delay", contract.delay_param, f"{d.artifact_type}: {d.left_col}->{d.right_col} median={d.median_minutes}", "CONFIRMED_FROM_TIMESTAMPS", 1.0, d.note))
        reasons.append("delay parameter confirmed from timestamp delta")
    else:
        comps.append(component("delay", contract.delay_param, "no matching signal/event->entry timestamp delta", "UNCONFIRMED", 0.25, "filename param exists but timestamp proof missing"))
        blockers.append("delay implementation must be confirmed or implemented exactly from scanner")

    # h/session
    dominant = [h for h in hours if h.match_status == "TARGET_H_DOMINANT"]
    present = [h for h in hours if h.match_status == "TARGET_H_PRESENT"]
    if dominant:
        h = dominant[0]
        comps.append(component("h_session", contract.h_param, f"{h.artifact_type}.{h.source_col} target_share={h.target_share}; top={h.top_values}", "CONFIRMED_DOMINANT", 1.0, h.method))
        reasons.append("h parameter confirmed by hour/session evidence")
    elif present:
        h = present[0]
        comps.append(component("h_session", contract.h_param, f"{h.artifact_type}.{h.source_col} target_share={h.target_share}; top={h.top_values}", "PARTIAL_PRESENT_NOT_DOMINANT", 0.5, h.method))
        warnings.append("h value appears but is not dominant; h may not mean UTC hour")
    else:
        comps.append(component("h_session", contract.h_param, "no matching hour/session evidence", "UNCONFIRMED", 0.25, "filename param exists but semantic proof missing"))
        warnings.append("h parameter semantics remain unclear")

    confirmed = len([c for c in comps if c.status.startswith("CONFIRMED")])
    total = len(comps)

    # Blueprint allowed if m + extra confirmed and at least hold OR delay confirmed; runtime remains blocked.
    m_ok = any(c.component == "m_threshold" and c.status == "CONFIRMED" for c in comps)
    extra_ok = any(c.component == "extra_slip" and c.status.startswith("CONFIRMED") for c in comps)
    hold_ok = any(c.component == "hold" and c.status.startswith("CONFIRMED") for c in comps)
    delay_ok = any(c.component == "delay" and c.status.startswith("CONFIRMED") for c in comps)

    if m_ok and extra_ok and hold_ok and delay_ok:
        audit_status = "SEMANTICS_CONFIRMED_FOR_LOGGER_BLUEPRINT"
        blueprint_allowed = True
        reasons.append("m, extra, hold, and delay are confirmed enough for blueprint generation")
    elif m_ok and extra_ok:
        audit_status = "SEMANTICS_PARTIAL_BLUEPRINT_WITH_BLOCKERS"
        blueprint_allowed = True
        warnings.append("blueprint can be drafted, but runtime blockers remain")
    else:
        audit_status = "SEMANTICS_BLOCKED_INSUFFICIENT_PROOF"
        blueprint_allowed = False

    return SemanticAuditResult(
        candidate_key=contract.candidate_key,
        selected_variant_key=contract.selected_variant_key,
        audit_status=audit_status,
        blueprint_allowed=blueprint_allowed,
        logger_build_allowed=False,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        confirmed_components=confirmed,
        total_components=total,
        components=comps,
        blockers=list(dict.fromkeys(blockers)),
        warnings=list(dict.fromkeys(warnings)),
        reasons=list(dict.fromkeys(reasons)),
    )


def records_df(items: List[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in items])


def write_outputs(workspace: Path, out_dir: Path, state: AuditorState, contract: SelectedContract, result: SemanticAuditResult, deltas: List[DeltaEvidence], hours: List[HourEvidence]) -> None:
    persistent = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes" / contract.candidate_key / "semantic_contract"
    persistent.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": asdict(state),
        "selected_contract": asdict(contract),
        "semantic_audit_result": asdict(result),
        "delta_evidence": [asdict(d) for d in deltas],
        "hour_evidence": [asdict(h) for h in hours],
    }
    for d in [out_dir, persistent]:
        write_json(d / "ret60_semantic_contract_audit_state.json", payload)
        write_json(d / "ret60_semantic_contract.json", {"selected_contract": asdict(contract), "semantic_audit_result": asdict(result)})
        records_df(result.components).to_csv(d / "ret60_semantic_components.csv", index=False)
        records_df(deltas).to_csv(d / "ret60_time_delta_evidence.csv", index=False)
        records_df(hours).to_csv(d / "ret60_hour_evidence.csv", index=False)

    md = f"""# Ret60 Semantic Contract Audit

Candidate: `{result.candidate_key}`
Selected variant: `{result.selected_variant_key}`
Audit status: **{result.audit_status}**

## Permissions

- Blueprint allowed: `{result.blueprint_allowed}`
- Logger build allowed: `False`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Components

| Component | Target | Observed | Status | Confidence |
|---|---|---|---:|---:|
"""
    for c in result.components:
        md += f"| {c.component} | {c.target_value} | {c.observed_value} | {c.status} | {c.confidence} |\n"
    md += "\n## Blockers\n\n```text\n" + ("\n".join(result.blockers) if result.blockers else "none") + "\n```\n"
    md += "\n## Warnings\n\n```text\n" + ("\n".join(result.warnings) if result.warnings else "none") + "\n```\n"
    for d in [out_dir, persistent]:
        write_text(d / "ret60_semantic_contract_audit.md", md)


def write_report(path: Path, state: AuditorState, result: SemanticAuditResult) -> None:
    lines = [
        "# Edge Factory Ret60 Semantic Contract Auditor Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Audit status: **{result.audit_status}**",
        f"Selected variant: `{result.selected_variant_key}`",
        f"Artifacts loaded: **{state.artifacts_loaded}**",
        f"Confirmed components: **{result.confirmed_components}/{result.total_components}**",
        f"Blueprint allowed: **{result.blueprint_allowed}**",
        f"Logger build allowed: **{result.logger_build_allowed}**",
        f"Shadow start allowed: **{result.shadow_start_allowed}**",
        f"Live allowed: **{result.live_allowed}**",
        "",
        "## Components",
        "",
        "| Component | Target | Observed | Status | Confidence | Evidence |",
        "|---|---|---|---:|---:|---|",
    ]
    for c in result.components:
        lines.append(f"| {c.component} | {c.target_value} | {c.observed_value} | {c.status} | {c.confidence} | {c.evidence} |")
    lines += ["", "## Reasons", ""]
    for r in state.reasons + result.reasons:
        lines.append(f"- {r}")
    if result.blockers:
        lines += ["", "## Blockers", ""]
        for b in result.blockers:
            lines.append(f"- {b}")
    warnings = state.warnings + result.warnings
    if warnings:
        lines += ["", "## Warnings", ""]
        for w in warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    write_text(path, "\n".join(lines))


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Audit ret60 selected variant semantics")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    p.add_argument("--parser_state", default=None)
    p.add_argument("--out_dir", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    candidate = safe_key(args.candidate)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_ret60_semantic_contract_auditor"
    out_dir = out_root / f"ret60_semantic_audit_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    contract, parser_state_path, warnings = load_selected_contract(workspace, args.parser_state)
    dfs: Dict[str, pd.DataFrame] = {}
    artifacts_loaded = 0
    if contract:
        for atype, pstr in [("combined", contract.combined_path), ("session", contract.session_path)]:
            if pstr and Path(pstr).exists():
                try:
                    dfs[atype] = pd.read_csv(pstr)
                    artifacts_loaded += 1
                except Exception as e:
                    warnings.append(f"failed to read {atype} artifact: {e}")
            else:
                warnings.append(f"missing {atype} artifact path")

    if not contract:
        dummy = SemanticAuditResult(candidate, "", "SEMANTICS_BLOCKED_NO_CONTRACT", False, False, False, False, False, 0, 5, [], ["selected contract missing"], warnings, [])
        state = AuditorState(datetime.now().isoformat(timespec="seconds"), str(workspace), candidate, str(parser_state_path) if parser_state_path else None, None, None, None, 0, dummy.audit_status, False, False, False, False, False, ["semantic auditor could not load selected parser v2 contract"], warnings, ["No runtime action allowed"])
        write_json(out_dir / "ret60_semantic_contract_audit_state.json", {"state": asdict(state), "semantic_audit_result": asdict(dummy)})
        print("EDGE FACTORY RET60 SEMANTIC CONTRACT AUDITOR v1")
        print("=" * 100)
        print(f"audit_status: {dummy.audit_status}")
        print("live_allowed: False")
        return 0

    deltas: List[DeltaEvidence] = []
    hours: List[HourEvidence] = []
    for atype, df in dfs.items():
        deltas.extend(audit_deltas(df, atype, contract))
        hours.extend(hour_evidence_from_df(df, atype, contract))

    result = audit_semantics(contract, dfs, deltas, hours)
    state = AuditorState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        candidate=candidate,
        parser_v2_state_path=str(parser_state_path) if parser_state_path else None,
        selected_artifact_path=contract.selected_artifact_path,
        combined_path=contract.combined_path,
        session_path=contract.session_path,
        artifacts_loaded=artifacts_loaded,
        audit_status=result.audit_status,
        blueprint_allowed=result.blueprint_allowed,
        logger_build_allowed=False,
        shadow_start_allowed=False,
        active_paper_allowed=False,
        live_allowed=False,
        reasons=["Semantic auditor inspected selected ret60 v2 artifact contract offline."],
        warnings=warnings,
        hard_rules=[
            "Semantic auditor never starts paper/live.",
            "Semantic auditor never mutates active config.",
            "Semantic auditor never edits MASTER_UPPER_SYSTEM or sizing contract.",
            "Blueprint permission is not runtime permission.",
            "Shadow start still requires sandbox logger, preflight, and manual approval.",
            "Live remains blocked.",
        ],
    )

    write_outputs(workspace, out_dir, state, contract, result, deltas, hours)
    write_report(out_dir / "ret60_semantic_contract_auditor_report.md", state, result)

    print("EDGE FACTORY RET60 SEMANTIC CONTRACT AUDITOR v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"candidate : {candidate}")
    print(f"output_dir: {out_dir}")
    print(f"parser_v2_state: {state.parser_v2_state_path}")
    print(f"selected_variant: {contract.selected_variant_key}")
    print(f"combined_path: {contract.combined_path}")
    print(f"session_path : {contract.session_path}")
    print(f"audit_status: {result.audit_status}")
    print(f"confirmed_components: {result.confirmed_components}/{result.total_components}")
    print(f"blueprint_allowed: {result.blueprint_allowed}")
    print("logger_build_allowed: False")
    print("shadow_start_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("")
    print("COMPONENTS")
    print("-" * 100)
    for c in result.components:
        print(f"{c.component:16s} status={c.status:34s} conf={c.confidence:.2f} target={c.target_value} observed={c.observed_value}")
    if result.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in result.blockers:
            print(f"- {b}")
    if state.warnings or result.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in state.warnings + result.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not mutate active config, and did not promote any strategy.")
    print("")
    print(f"Report : {out_dir / 'ret60_semantic_contract_auditor_report.md'}")
    print(f"State  : {out_dir / 'ret60_semantic_contract_audit_state.json'}")
    print(f"Components: {out_dir / 'ret60_semantic_components.csv'}")
    return 0




if __name__ == "__main__":
    raise SystemExit(main())
