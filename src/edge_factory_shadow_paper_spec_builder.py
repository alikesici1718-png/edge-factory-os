#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY SHADOW PAPER SPEC BUILDER v1
=========================================

Purpose
-------
Build a technical shadow-paper specification for promotion-sandbox candidates.

This module is the next step after:
    edge_factory_family_promotion_sandbox.py

It is intentionally NOT a paper starter and NOT a logger launcher.
It creates the specification that a future sandbox-only candidate logger must satisfy.

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
    - read latest promotion sandbox manifests
    - inspect candidate historical rows in normalized_oos_trades.csv
    - infer available columns/features for the candidate
    - produce a candidate-specific shadow-paper technical spec
    - define required native logging fields
    - define preflight gates before a future sandbox-only logger can be written/run
    - write reference-only commands and contracts
    - append evidence-only research ledger records unless disabled

Run:
    python "C:\Users\alike\edge_factory_shadow_paper_spec_builder.py"

Run one candidate:
    python "C:\Users\alike\edge_factory_shadow_paper_spec_builder.py" --candidate ret60_reversal_short

Core rule
---------
Spec is not execution. Shadow paper cannot start until a future sandbox-only logger exists,
passes preflight, and the user manually approves.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_SCRIPT_DIR = Path(r"C:\Users\alike")

FAMILY_COLS = ["family_key", "family", "strategy", "strategy_key", "candidate_key", "candidate", "label", "name"]
SYMBOL_COLS = ["symbol", "inst_id", "instrument", "inst", "ticker", "coin"]
TIME_COLS = ["event_time", "exit_time", "entry_time", "timestamp", "time", "datetime", "date", "open_time", "close_time", "ts"]
PNL_COLS = ["pnl", "net_pnl_usdt", "pnl_usdt", "net_pnl", "gross_pnl_usdt", "profit"]
SIDE_COLS = ["side", "direction", "position_side", "trade_side"]
PRICE_COLS = ["entry_price", "exit_price", "price", "close", "mark_price"]

FEATURE_HINTS = ["ret", "z", "rank", "market", "volume", "vol", "close", "trend", "momentum", "rsi", "ema", "atr", "funding", "spread", "signal"]


@dataclass
class SandboxCandidate:
    candidate_key: str
    sandbox_dir: str
    persistent_dir: str
    sandbox_status: str
    evidence_score: float
    shadow_paper_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    manifest_path: str


@dataclass
class CandidateDataProfile:
    candidate_key: str
    source_path: str
    family_col: Optional[str]
    symbol_col: Optional[str]
    time_col: Optional[str]
    pnl_col: Optional[str]
    side_col: Optional[str]
    rows_total_source: int
    rows_candidate: int
    symbols_candidate: int
    columns_count: int
    feature_columns: List[str]
    constant_columns: Dict[str, Any]
    numeric_ranges: Dict[str, Dict[str, float]]
    sample_symbols: List[str]
    warnings: List[str]


@dataclass
class SpecGate:
    gate_id: str
    category: str
    required_for_logger_build: bool
    required_for_shadow_start: bool
    passed: bool
    status: str
    reason: str


@dataclass
class ShadowSpecRecord:
    candidate_key: str
    spec_status: str
    spec_dir: str
    persistent_dir: str
    rows_candidate: int
    symbols_candidate: int
    feature_columns_detected: int
    signal_definition_status: str
    logger_build_allowed: bool
    shadow_start_allowed: bool
    active_paper_allowed: bool
    live_allowed: bool
    gates_passed_for_logger: int
    gates_required_for_logger: int
    gates_passed_for_shadow_start: int
    gates_required_for_shadow_start: int
    next_action: str
    reasons: List[str]
    warnings: List[str]


@dataclass
class BuilderState:
    generated_at: str
    workspace: str
    source_normalized_trades: Optional[str]
    sandbox_candidates_seen: int
    specs_created: int
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


def stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


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


def load_json(path: Path) -> Dict[str, Any]:
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


def latest_promotion_sandbox_run(workspace: Path) -> Optional[Path]:
    return latest_child_dir(workspace / "edge_factory_family_promotion_sandbox", "promotion_sandbox_")


def discover_sandbox_candidates(workspace: Path, candidate_filter: Optional[str]) -> List[SandboxCandidate]:
    candidates: List[SandboxCandidate] = []
    persistent_root = workspace / "edge_factory_family_promotion_sandbox" / "sandboxes"
    if not persistent_root.exists():
        return []
    for manifest in persistent_root.rglob("sandbox_manifest.json"):
        obj = load_json(manifest)
        if not obj:
            continue
        ev = obj.get("candidate_evidence", {}) if isinstance(obj.get("candidate_evidence"), dict) else {}
        paths = obj.get("paths", {}) if isinstance(obj.get("paths"), dict) else {}
        permissions = obj.get("permissions", {}) if isinstance(obj.get("permissions"), dict) else {}
        key = safe_key(ev.get("candidate_key") or manifest.parent.name)
        if candidate_filter and key != safe_key(candidate_filter):
            continue
        status = str(obj.get("sandbox_status", ""))
        if status != "SANDBOX_READY_REVIEW_ONLY":
            continue
        candidates.append(SandboxCandidate(
            candidate_key=key,
            sandbox_dir=str(paths.get("run_dir") or manifest.parent),
            persistent_dir=str(paths.get("persistent_dir") or manifest.parent),
            sandbox_status=status,
            evidence_score=float(obj.get("evidence_score", 0.0) or 0.0),
            shadow_paper_allowed=bool(permissions.get("shadow_paper_allowed_reference_only", False)),
            active_paper_allowed=bool(permissions.get("active_paper_allowed", False)),
            live_allowed=bool(permissions.get("live_allowed", False)),
            manifest_path=str(manifest),
        ))
    candidates.sort(key=lambda c: c.candidate_key)
    return candidates


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


def load_candidate_rows(source: Path, candidate: str) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Optional[str]], List[str]]:
    warnings: List[str] = []
    head = pd.read_csv(source, nrows=2000)
    cols = {
        "family_col": find_col(head, FAMILY_COLS),
        "symbol_col": find_col(head, SYMBOL_COLS),
        "time_col": find_col(head, TIME_COLS),
        "pnl_col": find_col(head, PNL_COLS),
        "side_col": find_col(head, SIDE_COLS),
    }
    if not cols["family_col"]:
        raise ValueError("family/candidate column not found in normalized trades")

    # Full read is acceptable; normalized_oos_trades has already been used by earlier validators.
    df = pd.read_csv(source)
    fam = df[cols["family_col"]].astype(str).str.lower().str.strip()
    key = safe_key(candidate)
    mask = fam == key
    if not mask.any():
        mask = fam.str.contains(key, regex=False, na=False)
        if mask.any():
            warnings.append("used contains-match for candidate rows")
    cdf = df.loc[mask].copy()
    if cols["symbol_col"] and cols["symbol_col"] in cdf.columns:
        cdf["__symbol_norm"] = cdf[cols["symbol_col"]].map(normalize_symbol)
    return df, cdf, cols, warnings


def profile_candidate(source: Path, candidate: str) -> CandidateDataProfile:
    df, cdf, cols, warnings = load_candidate_rows(source, candidate)
    feature_cols: List[str] = []
    for col in cdf.columns:
        low = str(col).lower()
        if any(h in low for h in FEATURE_HINTS):
            feature_cols.append(str(col))

    constants: Dict[str, Any] = {}
    numeric_ranges: Dict[str, Dict[str, float]] = {}
    if not cdf.empty:
        for col in cdf.columns:
            try:
                nunique = cdf[col].nunique(dropna=True)
                if 0 < nunique <= 3 and len(constants) < 30:
                    vals = cdf[col].dropna().unique().tolist()[:3]
                    constants[str(col)] = vals[0] if len(vals) == 1 else vals
            except Exception:
                pass
        for col in cdf.columns:
            if len(numeric_ranges) >= 40:
                break
            s = pd.to_numeric(cdf[col], errors="coerce")
            if s.notna().sum() >= max(5, int(0.2 * len(cdf))):
                numeric_ranges[str(col)] = {
                    "min": float(s.min()),
                    "median": float(s.median()),
                    "max": float(s.max()),
                    "non_null": int(s.notna().sum()),
                }

    symbols = []
    if "__symbol_norm" in cdf.columns:
        symbols = sorted([x for x in cdf["__symbol_norm"].dropna().astype(str).unique().tolist()])[:50]

    if not feature_cols:
        warnings.append("no obvious feature columns found; exact signal rule may require original research code")
    if cols.get("time_col") and cols.get("time_col") == cols.get("symbol_col"):
        warnings.append("time column equals symbol column; ignoring time for spec")
        cols["time_col"] = None

    return CandidateDataProfile(
        candidate_key=safe_key(candidate),
        source_path=str(source),
        family_col=cols.get("family_col"),
        symbol_col=cols.get("symbol_col"),
        time_col=cols.get("time_col"),
        pnl_col=cols.get("pnl_col"),
        side_col=cols.get("side_col"),
        rows_total_source=int(len(df)),
        rows_candidate=int(len(cdf)),
        symbols_candidate=int(cdf["__symbol_norm"].nunique()) if "__symbol_norm" in cdf.columns else 0,
        columns_count=int(len(cdf.columns)),
        feature_columns=feature_cols,
        constant_columns=constants,
        numeric_ranges=numeric_ranges,
        sample_symbols=symbols,
        warnings=warnings,
    )


def build_gates(candidate: SandboxCandidate, profile: CandidateDataProfile) -> List[SpecGate]:
    gates: List[SpecGate] = []

    def add(gate_id: str, category: str, build_req: bool, start_req: bool, passed: bool, reason: str) -> None:
        gates.append(SpecGate(
            gate_id=gate_id,
            category=category,
            required_for_logger_build=build_req,
            required_for_shadow_start=start_req,
            passed=bool(passed),
            status="PASS" if passed else "FAIL",
            reason=reason,
        ))

    add("sandbox_ready", "sandbox", True, True, candidate.sandbox_status == "SANDBOX_READY_REVIEW_ONLY", "promotion sandbox must be ready")
    add("sandbox_shadow_reference_allowed", "sandbox", True, True, candidate.shadow_paper_allowed, "sandbox must allow reference-only shadow planning")
    add("active_paper_blocked", "safety", True, True, not candidate.active_paper_allowed, "active paper must remain blocked")
    add("live_blocked", "safety", True, True, not candidate.live_allowed, "live must remain blocked")
    add("candidate_rows_present", "data", True, True, profile.rows_candidate > 0, "candidate must have historical rows")
    add("candidate_rows_enough", "data", True, True, profile.rows_candidate >= 300, "candidate should have enough rows for spec confidence")
    add("candidate_symbols_enough", "data", True, True, profile.symbols_candidate >= 50, "candidate should have broad symbol coverage")
    add("family_col_detected", "schema", True, True, bool(profile.family_col), "family/candidate column required")
    add("symbol_col_detected", "schema", True, True, bool(profile.symbol_col), "symbol column required")
    add("pnl_col_detected", "schema", True, False, bool(profile.pnl_col), "pnl column required for backtest comparison, not live signal")
    add("feature_columns_detected", "signal", True, False, len(profile.feature_columns) > 0, "feature columns help infer signal adapter requirements")
    add("explicit_signal_rule_defined", "signal", False, True, False, "future shadow start requires exact signal rule extraction/implementation")
    add("candidate_logger_exists", "implementation", False, True, False, "future shadow start requires sandbox-only logger implementation")
    add("native_logging_contract_defined", "logging", True, True, True, "this spec defines required native logging fields")
    add("manual_shadow_start_required", "approval", False, True, False, "future shadow start requires explicit user approval")
    return gates


def determine_signal_status(profile: CandidateDataProfile) -> str:
    key = profile.candidate_key
    feature_names = " ".join(profile.feature_columns).lower()
    if "ret60" in key or "ret60" in feature_names or "ret60" in str(profile.constant_columns).lower():
        return "PARTIALLY_INFERRED_RET60_REVERSAL_NEEDS_EXACT_RULE"
    if profile.feature_columns:
        return "FEATURES_DETECTED_NEEDS_EXACT_RULE"
    return "NO_SIGNAL_FEATURES_DETECTED_NEEDS_RESEARCH_CODE"


def create_spec_files(workspace: Path, out_dir: Path, candidate: SandboxCandidate, profile: CandidateDataProfile, gates: List[SpecGate], stamp: str) -> ShadowSpecRecord:
    persistent = Path(candidate.persistent_dir) / "shadow_spec"
    run_dir = out_dir / "shadow_specs" / candidate.candidate_key
    persistent.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    build_required = [g for g in gates if g.required_for_logger_build]
    start_required = [g for g in gates if g.required_for_shadow_start]
    build_passed = [g for g in build_required if g.passed]
    start_passed = [g for g in start_required if g.passed]

    logger_build_allowed = len(build_passed) == len(build_required)
    shadow_start_allowed = False  # Always false in v1; logger + explicit approval required later.
    active_paper_allowed = False
    live_allowed = False
    signal_status = determine_signal_status(profile)

    warnings: List[str] = list(profile.warnings)
    reasons: List[str] = []
    if logger_build_allowed:
        spec_status = "SPEC_READY_FOR_SANDBOX_LOGGER_BUILD"
        next_action = "BUILD_SANDBOX_ONLY_CANDIDATE_LOGGER_ADAPTER"
        reasons.append("all logger-build gates passed")
    else:
        spec_status = "SPEC_BLOCKED_NEEDS_DATA_OR_SCHEMA_REPAIR"
        next_action = "REPAIR_SPEC_GATES_BEFORE_LOGGER_BUILD"
        warnings.append("one or more logger-build gates failed")
    if not shadow_start_allowed:
        warnings.append("shadow start remains blocked until sandbox logger exists and manual approval is recorded")

    native_logging_contract = {
        "required_fields": [
            "event_id",
            "event_time_utc",
            "candidate_key",
            "symbol",
            "side",
            "signal_name",
            "signal_version",
            "signal_features_json",
            "decision",
            "entry_reference_price",
            "exit_reference_price",
            "hold_minutes",
            "notional_usdt",
            "fee_bps_assumption",
            "spread_bps_at_signal",
            "slippage_bps_assumption",
            "paper_entry_time_utc",
            "paper_exit_time_utc",
            "paper_gross_pnl_usdt",
            "paper_net_pnl_usdt",
            "paper_return_bps_native",
            "source_candle_time_utc",
            "data_latency_ms",
        ],
        "forbidden": [
            "live_order_id",
            "real_exchange_order_id",
            "api_secret",
            "active_position_mutation",
        ],
        "notes": "All future shadow logs must include native return_bps and execution assumptions for drift comparison.",
    }

    spec = {
        "candidate": asdict(candidate),
        "profile": asdict(profile),
        "signal_definition_status": signal_status,
        "permissions": {
            "logger_build_allowed": logger_build_allowed,
            "shadow_start_allowed": shadow_start_allowed,
            "active_paper_allowed": active_paper_allowed,
            "live_allowed": live_allowed,
            "mutates_active_config": False,
            "changes_sizing_contract": False,
        },
        "native_logging_contract": native_logging_contract,
        "gates": [asdict(g) for g in gates],
        "next_action": next_action,
    }
    write_json(persistent / "shadow_paper_spec.json", spec)
    write_json(run_dir / "shadow_paper_spec.json", spec)
    pd.DataFrame([asdict(g) for g in gates]).to_csv(persistent / "shadow_paper_spec_gates.csv", index=False)
    pd.DataFrame([asdict(g) for g in gates]).to_csv(run_dir / "shadow_paper_spec_gates.csv", index=False)

    md = f"""# Shadow Paper Spec: `{candidate.candidate_key}`

Status: **{spec_status}**

## Candidate profile

- Historical rows: `{profile.rows_candidate}`
- Symbols: `{profile.symbols_candidate}`
- Source: `{profile.source_path}`
- Family column: `{profile.family_col}`
- Symbol column: `{profile.symbol_col}`
- Time column: `{profile.time_col}`
- PnL column: `{profile.pnl_col}`
- Feature columns detected: `{len(profile.feature_columns)}`
- Signal definition status: **{signal_status}**

## Permissions

- Logger build allowed: `{logger_build_allowed}`
- Shadow start allowed: `False`
- Active paper allowed: `False`
- Live allowed: `False`

## Important

This is a technical specification only. It does not start anything.

Before shadow paper can start, the OS still needs:

1. Exact signal rule extraction/implementation.
2. Sandbox-only candidate logger adapter.
3. Native logging contract audit.
4. Sandbox preflight.
5. Explicit manual approval.

## Feature columns sample

```text
{chr(10).join(profile.feature_columns[:80])}
```

## Sample symbols

```text
{chr(10).join(profile.sample_symbols[:80])}
```
"""
    write_text(persistent / "shadow_paper_spec.md", md)
    write_text(run_dir / "shadow_paper_spec.md", md)

    interface_py = f'''# REFERENCE ONLY - sandbox logger interface contract for {candidate.candidate_key}
# This file is not an active logger.
# It defines the expected shape for a future sandbox-only implementation.

CANDIDATE_KEY = "{candidate.candidate_key}"
SIGNAL_DEFINITION_STATUS = "{signal_status}"
ACTIVE_PAPER_ALLOWED = False
LIVE_ALLOWED = False

REQUIRED_LOG_FIELDS = {json.dumps(native_logging_contract["required_fields"], indent=4)}


def compute_signal_from_candle_snapshot(snapshot: dict) -> dict:
    """Future implementation placeholder.

    Must return a dict with:
        decision: "ENTER_SHORT" / "ENTER_LONG" / "NO_TRADE"
        side: "short" / "long" / None
        signal_features_json: JSON-serializable dict
        confidence: float

    Current status: exact signal rule still needs extraction from research code/artifacts.
    """
    raise NotImplementedError("Sandbox signal rule is not implemented yet.")
'''
    write_text(persistent / "candidate_logger_interface_contract_REFERENCE_ONLY.py", interface_py)
    write_text(run_dir / "candidate_logger_interface_contract_REFERENCE_ONLY.py", interface_py)

    reference_ps1 = f"""# REFERENCE ONLY - DO NOT EXECUTE
# Candidate: {candidate.candidate_key}
# Shadow start is blocked in spec v1.
# A future sandbox-only logger must be built and pass preflight first.
# No command is approved here.
"""
    write_text(persistent / "shadow_start_REFERENCE_ONLY.ps1", reference_ps1)
    write_text(run_dir / "shadow_start_REFERENCE_ONLY.ps1", reference_ps1)

    return ShadowSpecRecord(
        candidate_key=candidate.candidate_key,
        spec_status=spec_status,
        spec_dir=str(run_dir),
        persistent_dir=str(persistent),
        rows_candidate=profile.rows_candidate,
        symbols_candidate=profile.symbols_candidate,
        feature_columns_detected=len(profile.feature_columns),
        signal_definition_status=signal_status,
        logger_build_allowed=logger_build_allowed,
        shadow_start_allowed=shadow_start_allowed,
        active_paper_allowed=active_paper_allowed,
        live_allowed=live_allowed,
        gates_passed_for_logger=len(build_passed),
        gates_required_for_logger=len(build_required),
        gates_passed_for_shadow_start=len(start_passed),
        gates_required_for_shadow_start=len(start_required),
        next_action=next_action,
        reasons=reasons,
        warnings=warnings,
    )


def append_ledger(workspace: Path, rec: ShadowSpecRecord) -> Optional[str]:
    try:
        root = workspace / "edge_factory_research_result_ledger"
        ledger = root / "master_research_result_ledger.jsonl"
        status = "PASS" if rec.logger_build_allowed else "WATCHLIST"
        raw = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "task_id": f"shadow_paper_spec_{rec.candidate_key}",
            "result_status": status,
            "score": rec.gates_passed_for_logger / max(1, rec.gates_required_for_logger),
            "summary": f"{rec.candidate_key}: {rec.spec_status}, logger_build_allowed={rec.logger_build_allowed}, shadow_start_allowed={rec.shadow_start_allowed}, signal={rec.signal_definition_status}",
            "evidence_path": str(Path(rec.spec_dir) / "shadow_paper_spec.json"),
            "family": None,
            "candidate": rec.candidate_key,
            "tags": ["shadow_paper_spec", "sandbox", "offline", "no_active_paper", "no_live"],
            "reviewer": "shadow_paper_spec_builder_v1",
            "source": "edge_factory_shadow_paper_spec_builder_v1",
            "safe_for_auto_promotion": False,
            "live_allowed": False,
            "notes": "Spec only. Shadow start blocked until logger/preflight/manual approval.",
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


def records_df(records: List[ShadowSpecRecord]) -> pd.DataFrame:
    rows = []
    for r in records:
        d = asdict(r)
        d["reasons"] = " | ".join(r.reasons)
        d["warnings"] = " | ".join(r.warnings)
        rows.append(d)
    return pd.DataFrame(rows)


def write_report(path: Path, state: BuilderState, records: List[ShadowSpecRecord]) -> None:
    lines = [
        "# Edge Factory Shadow Paper Spec Builder Report",
        "",
        f"Generated: `{state.generated_at}`",
        f"Overall state: **{state.overall_state}**",
        f"Candidates seen: **{state.sandbox_candidates_seen}**",
        f"Specs created: **{state.specs_created}**",
        f"Logger build allowed: **{state.logger_build_allowed_count}**",
        f"Shadow start allowed: **{state.shadow_start_allowed_count}**",
        f"Active paper allowed: **{state.active_paper_allowed_count}**",
        f"Live allowed: **{state.live_allowed}**",
        "",
        "## Specs",
        "",
    ]
    if records:
        lines += ["| Candidate | Status | Rows | Symbols | Signal status | Logger build | Shadow start | Next |", "|---|---:|---:|---:|---|---:|---:|---|"]
        for r in records:
            lines.append(f"| {r.candidate_key} | {r.spec_status} | {r.rows_candidate} | {r.symbols_candidate} | {r.signal_definition_status} | {r.logger_build_allowed} | {r.shadow_start_allowed} | {r.next_action} |")
    else:
        lines.append("No shadow specs created.")
    lines += ["", "## Reasons", ""]
    for reason in state.reasons:
        lines.append(f"- {reason}")
    if state.warnings:
        lines += ["", "## Warnings", ""]
        for w in state.warnings:
            lines.append(f"- {w}")
    lines += ["", "## Hard rules", ""]
    for rule in state.hard_rules:
        lines.append(f"- {rule}")
    lines += ["", "## Interpretation", "", "This module only specifies the sandbox logger requirements. It intentionally blocks shadow start until exact signal logic, a sandbox-only logger, preflight, and manual approval exist.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory shadow paper spec builder")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--candidate", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--source", default=None)
    p.add_argument("--no_ledger_append", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    stamp = now_stamp()
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_shadow_paper_spec_builder"
    out_dir = out_root / f"shadow_spec_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = Path(args.source) if args.source else latest_normalized_trades(workspace)
    warnings: List[str] = []
    records: List[ShadowSpecRecord] = []
    ledger_count = 0

    candidates = discover_sandbox_candidates(workspace, args.candidate)
    if not candidates:
        warnings.append("No sandbox-ready candidates found. Run family_promotion_sandbox first.")
    if source is None or not source.exists():
        warnings.append("normalized_oos_trades source not found; cannot build data-backed specs")
    else:
        for candidate in candidates:
            try:
                profile = profile_candidate(source, candidate.candidate_key)
                gates = build_gates(candidate, profile)
                rec = create_spec_files(workspace, out_dir, candidate, profile, gates, stamp)
                records.append(rec)
                if not args.no_ledger_append:
                    rid = append_ledger(workspace, rec)
                    if rid:
                        ledger_count += 1
                    else:
                        warnings.append(f"ledger append failed for {candidate.candidate_key}")
            except Exception as e:
                warnings.append(f"failed to build spec for {candidate.candidate_key}: {e}")

    logger_allowed = len([r for r in records if r.logger_build_allowed])
    shadow_allowed = len([r for r in records if r.shadow_start_allowed])
    active_allowed = len([r for r in records if r.active_paper_allowed])
    if records and logger_allowed == len(records):
        overall = "SPEC_READY_FOR_SANDBOX_LOGGER_BUILD"
    elif records:
        overall = "SPEC_CREATED_WITH_BLOCKED_GATES"
    else:
        overall = "NO_SPEC_CREATED"

    state = BuilderState(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        workspace=str(workspace),
        source_normalized_trades=str(source) if source else None,
        sandbox_candidates_seen=len(candidates),
        specs_created=len(records),
        logger_build_allowed_count=logger_allowed,
        shadow_start_allowed_count=shadow_allowed,
        active_paper_allowed_count=active_allowed,
        live_allowed=False,
        overall_state=overall,
        reasons=[
            "Shadow paper spec builder read promotion sandbox candidates.",
            "Specs are technical contracts only and do not start any runtime.",
        ],
        warnings=warnings,
        hard_rules=[
            "Shadow paper spec builder never starts paper/live.",
            "Shadow paper spec builder never mutates active config.",
            "Shadow paper spec builder never edits MASTER_UPPER_SYSTEM.",
            "Shadow paper spec builder never edits position sizing contract.",
            "Shadow start requires future sandbox logger, preflight, and manual approval.",
            "Live remains blocked.",
        ],
    )

    state_path = out_dir / "shadow_paper_spec_builder_state.json"
    write_json(state_path, {"state": asdict(state), "specs": [asdict(r) for r in records]})
    records_df(records).to_csv(out_dir / "shadow_paper_spec_summary.csv", index=False)
    write_report(out_dir / "shadow_paper_spec_builder_report.md", state, records)

    print("EDGE FACTORY SHADOW PAPER SPEC BUILDER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"output_dir: {out_dir}")
    print(f"overall_state: {state.overall_state}")
    print(f"source_normalized_trades: {state.source_normalized_trades}")
    print(f"sandbox_candidates_seen: {state.sandbox_candidates_seen}")
    print(f"specs_created: {state.specs_created}")
    print(f"logger_build_allowed_count: {state.logger_build_allowed_count}")
    print(f"shadow_start_allowed_count: {state.shadow_start_allowed_count}")
    print(f"active_paper_allowed_count: {state.active_paper_allowed_count}")
    print(f"ledger_records_appended: {ledger_count}")
    print("live_allowed: False")
    print("")
    print("SPECS")
    print("-" * 100)
    for r in records:
        print(f"{r.candidate_key:32s} status={r.spec_status:40s} rows={r.rows_candidate:6d} symbols={r.symbols_candidate:4d} features={r.feature_columns_detected:3d} logger_build={r.logger_build_allowed} shadow_start={r.shadow_start_allowed}")
        print(f"     signal: {r.signal_definition_status}")
        print(f"     persistent: {r.persistent_dir}")
        print(f"     next: {r.next_action}")
        if r.warnings:
            print(f"     warnings: {' | '.join(r.warnings[:4])}")
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
    print(f"Report : {out_dir / 'shadow_paper_spec_builder_report.md'}")
    print(f"State  : {state_path}")
    print(f"Summary: {out_dir / 'shadow_paper_spec_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
