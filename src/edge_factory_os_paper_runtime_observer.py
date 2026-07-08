#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
EDGE FACTORY OS PAPER RUNTIME OBSERVER v1
=========================================

Purpose
-------
Safe runtime observer for supervised paper mode in the self-improving Edge Factory OS.

This module is designed for the phase AFTER a human manually starts supervised paper.
But it is safe to run before paper starts too. In that case it reports:
    PAPER_NOT_STARTED

It does NOT start paper.
It does NOT start live.
It does NOT run loggers.
It does NOT execute PowerShell.
It does NOT run start_edge_factory_MASTER_UPPER_SYSTEM.ps1.
It does NOT mutate active config.
It does NOT run --apply.

What it checks
--------------
1) Is the paper runtime directory present?
2) Are expected family/runtime files appearing?
3) Are trade/log CSV files present?
4) Do trade/log CSV files contain native execution fields needed for later drift validation?
5) Are closed trades detected?
6) Should the OS keep waiting, run drift monitor, or repair paper runtime?

Run:
    python "C:\Users\alike\edge_factory_os_paper_runtime_observer.py"

Outputs:
    <workspace>\edge_factory_os_paper_runtime_observer\paper_runtime_YYYYMMDD_HHMMSS\
        os_paper_runtime_observer_report.md
        os_paper_runtime_observer_state.json
        os_paper_runtime_files.csv
        os_paper_runtime_csv_schema.csv
        os_paper_runtime_native_field_audit.csv

Core rule
---------
Observation only. No start/stop/kill actions are executed by this module.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


DEFAULT_WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_PAPER_DIR_NAME = "paper_run_gate_MASTER_UPPER_SYSTEM"

ACTIVE_FAMILIES = [
    "old_short",
    "impulse_long",
    "market_relative_short",
    "weak_market_short",
]

REQUIRED_NATIVE_FIELDS = [
    "family_key",
    "symbol",
    "side",
    "entry_time",
    "exit_time",
    "entry_price",
    "exit_price",
    "qty",
    "notional_usdt",
    "gross_pnl_usdt",
    "fee_usdt",
    "net_pnl_usdt",
    "gross_bps",
    "net_bps",
    "spread_bps_at_entry",
    "spread_bps_at_exit",
    "slippage_bps_est",
    "hold_seconds",
    "exit_reason",
    "strategy_signal_id",
]

# Some existing logs may use older/alternate field names. These aliases do not replace
# native requirements, but help the observer understand whether a file is close enough
# to inspect while still warning that native fields must be added/verified.
FIELD_ALIASES = {
    "family_key": ["family", "strategy", "strategy_key"],
    "symbol": ["inst", "inst_id", "instrument", "coin"],
    "net_pnl_usdt": ["pnl", "net_pnl", "pnl_usdt"],
    "notional_usdt": ["notional", "notional_usd", "order_notional"],
    "net_bps": ["return_bps", "ret_bps", "bps"],
    "entry_time": ["open_time", "entry_ts", "timestamp", "time"],
    "exit_time": ["close_time", "exit_ts"],
}


@dataclass
class RuntimeFile:
    path: str
    relative_path: str
    exists: bool
    size_bytes: int
    modified_at: Optional[str]
    suffix: str
    kind: str


@dataclass
class CsvSchema:
    path: str
    relative_path: str
    readable: bool
    rows_sampled: int
    columns: str
    error: Optional[str]


@dataclass
class NativeFieldAudit:
    path: str
    relative_path: str
    kind: str
    required_count: int
    present_required_count: int
    missing_required: str
    alias_present: str
    native_coverage: float
    status: str


@dataclass
class RuntimeDecision:
    generated_at: str
    runtime_status: str
    paper_dir: str
    paper_dir_exists: bool
    paper_dir_nonempty: bool
    closed_trades_detected: bool
    trade_csv_count: int
    log_csv_count: int
    native_ready_file_count: int
    native_partial_file_count: int
    native_missing_file_count: int
    active_family_evidence_count: int
    next_os_action: str
    blockers: List[str]
    warnings: List[str]
    reasons: List[str]
    live_allowed: bool
    hard_rules: List[str]


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_mtime(path: Path) -> Optional[str]:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except Exception:
        return None


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def classify_file(path: Path) -> str:
    name = path.name.lower()
    rel = str(path).lower()
    if "closed" in name and "trade" in name:
        return "closed_trades"
    if "trade" in name:
        return "trade_log"
    if "fill" in name:
        return "fill_log"
    if "position" in name:
        return "position_log"
    if "heartbeat" in name or "health" in name:
        return "health_log"
    if "error" in name or "exception" in name:
        return "error_log"
    if "paper" in rel and path.suffix.lower() == ".csv":
        return "paper_csv"
    if path.suffix.lower() == ".json":
        return "json"
    if path.suffix.lower() == ".log":
        return "text_log"
    return "other"


def collect_runtime_files(paper_dir: Path, max_files: int = 5000) -> List[RuntimeFile]:
    files: List[RuntimeFile] = []
    if not paper_dir.exists():
        return files
    count = 0
    for p in paper_dir.rglob("*"):
        if count >= max_files:
            break
        if not p.is_file():
            continue
        try:
            st = p.stat()
            files.append(RuntimeFile(
                path=str(p),
                relative_path=str(p.relative_to(paper_dir)),
                exists=True,
                size_bytes=int(st.st_size),
                modified_at=iso_mtime(p),
                suffix=p.suffix.lower(),
                kind=classify_file(p),
            ))
            count += 1
        except Exception:
            continue
    return files


def is_interesting_csv(runtime_file: RuntimeFile) -> bool:
    if runtime_file.suffix != ".csv":
        return False
    if runtime_file.size_bytes <= 0:
        return False
    return runtime_file.kind in {"closed_trades", "trade_log", "fill_log", "position_log", "paper_csv"}


def read_csv_schema(path: Path, paper_dir: Path, sample_rows: int) -> CsvSchema:
    try:
        # nrows is enough for schema and light sampling.
        df = pd.read_csv(path, nrows=sample_rows)
        return CsvSchema(
            path=str(path),
            relative_path=str(path.relative_to(paper_dir)),
            readable=True,
            rows_sampled=int(len(df)),
            columns=" | ".join(str(c) for c in df.columns),
            error=None,
        )
    except Exception as e:
        return CsvSchema(
            path=str(path),
            relative_path=str(path.relative_to(paper_dir)),
            readable=False,
            rows_sampled=0,
            columns="",
            error=repr(e),
        )


def audit_native_fields(schema: CsvSchema, kind: str) -> NativeFieldAudit:
    cols = [c.strip() for c in schema.columns.split(" | ") if c.strip()]
    colset = {c.lower() for c in cols}
    missing: List[str] = []
    present = 0
    alias_hits: List[str] = []

    for field in REQUIRED_NATIVE_FIELDS:
        if field.lower() in colset:
            present += 1
        else:
            missing.append(field)
            for alias in FIELD_ALIASES.get(field, []):
                if alias.lower() in colset:
                    alias_hits.append(f"{field}<={alias}")
                    break

    coverage = present / max(1, len(REQUIRED_NATIVE_FIELDS))
    if not schema.readable:
        status = "CSV_UNREADABLE"
    elif coverage >= 0.90:
        status = "NATIVE_FIELDS_STRONG"
    elif coverage >= 0.50 or alias_hits:
        status = "NATIVE_FIELDS_PARTIAL_OR_ALIAS"
    else:
        status = "NATIVE_FIELDS_MISSING"

    return NativeFieldAudit(
        path=schema.path,
        relative_path=schema.relative_path,
        kind=kind,
        required_count=len(REQUIRED_NATIVE_FIELDS),
        present_required_count=present,
        missing_required=" | ".join(missing),
        alias_present=" | ".join(alias_hits),
        native_coverage=round(float(coverage), 4),
        status=status,
    )


def family_evidence_count(files: List[RuntimeFile], audits: List[NativeFieldAudit]) -> int:
    text = "\n".join([f.relative_path.lower() for f in files] + [a.relative_path.lower() for a in audits])
    count = 0
    for fam in ACTIVE_FAMILIES:
        if fam.lower() in text:
            count += 1
    return count


def closed_trades_detected(files: List[RuntimeFile], audits: List[NativeFieldAudit]) -> bool:
    for f in files:
        if f.kind == "closed_trades" and f.size_bytes > 100:
            return True
    # Some logs may not be named closed_trades but contain exit fields and rows.
    for a in audits:
        if a.kind in {"closed_trades", "trade_log", "paper_csv"} and "exit_time" not in a.missing_required and a.status in {"NATIVE_FIELDS_STRONG", "NATIVE_FIELDS_PARTIAL_OR_ALIAS"}:
            return True
    return False


def build_decision(workspace: Path, paper_dir: Path, files: List[RuntimeFile], schemas: List[CsvSchema], audits: List[NativeFieldAudit]) -> RuntimeDecision:
    exists = paper_dir.exists()
    nonempty = bool(files)
    trade_csv_count = len([f for f in files if f.suffix == ".csv" and f.kind in {"closed_trades", "trade_log", "fill_log", "paper_csv"}])
    log_csv_count = len([f for f in files if f.suffix == ".csv"])
    native_ready = len([a for a in audits if a.status == "NATIVE_FIELDS_STRONG"])
    native_partial = len([a for a in audits if a.status == "NATIVE_FIELDS_PARTIAL_OR_ALIAS"])
    native_missing = len([a for a in audits if a.status in {"NATIVE_FIELDS_MISSING", "CSV_UNREADABLE"}])
    family_count = family_evidence_count(files, audits)
    closed = closed_trades_detected(files, audits)

    blockers: List[str] = []
    warnings: List[str] = []
    reasons: List[str] = []

    if not exists:
        status = "PAPER_NOT_STARTED"
        next_action = "KEEP_WAITING_OR_USE_MANUAL_APPROVAL_GATE"
        reasons.append("Paper runtime directory does not exist.")
    elif exists and not nonempty:
        status = "PAPER_DIR_EXISTS_BUT_EMPTY"
        next_action = "CHECK_WHETHER_PAPER_LAUNCHER_STARTED_CORRECTLY"
        warnings.append("Paper directory exists but contains no files.")
        reasons.append("Paper may not have started or has not produced logs yet.")
    elif trade_csv_count == 0:
        status = "PAPER_RUNTIME_SEEN_NO_TRADE_LOGS_YET"
        next_action = "WAIT_FOR_TRADE_LOGS_AND_HEALTH_CHECK"
        warnings.append("Runtime files exist, but no trade CSV/log evidence was detected.")
        reasons.append("Paper may be running but has not produced trade logs yet.")
    elif native_ready == 0 and native_partial == 0:
        status = "PAPER_RUNTIME_LOGGING_CONTRACT_MISSING_NATIVE_FIELDS"
        next_action = "PATCH_OR_VERIFY_PAPER_LOG_NATIVE_FIELDS_BEFORE_DRIFT"
        blockers.append("native_execution_fields_missing")
        reasons.append("Trade/log CSVs exist but native execution fields are missing or unreadable.")
    elif not closed:
        status = "PAPER_RUNNING_WAITING_FOR_CLOSED_TRADES"
        next_action = "WAIT_FOR_CLOSED_TRADES_THEN_RUN_DRIFT_MONITOR"
        warnings.append("Native/partial logs exist, but closed trade sample is not ready.")
        reasons.append("Paper runtime evidence exists; drift monitor should wait for closed trades.")
    else:
        status = "PAPER_RUNNING_READY_FOR_DRIFT_CHECK"
        next_action = "RUN_LIVE_VS_BACKTEST_DRIFT_MONITOR"
        reasons.append("Closed trade evidence detected; drift validation can be run next.")

    if family_count < len(ACTIVE_FAMILIES) and exists and nonempty:
        warnings.append(f"Only {family_count}/{len(ACTIVE_FAMILIES)} active families detected in runtime file paths/schema evidence.")

    return RuntimeDecision(
        generated_at=datetime.now().isoformat(timespec="seconds"),
        runtime_status=status,
        paper_dir=str(paper_dir),
        paper_dir_exists=exists,
        paper_dir_nonempty=nonempty,
        closed_trades_detected=closed,
        trade_csv_count=trade_csv_count,
        log_csv_count=log_csv_count,
        native_ready_file_count=native_ready,
        native_partial_file_count=native_partial,
        native_missing_file_count=native_missing,
        active_family_evidence_count=family_count,
        next_os_action=next_action,
        blockers=blockers,
        warnings=warnings,
        reasons=reasons,
        live_allowed=False,
        hard_rules=[
            "Observer never starts paper/live.",
            "Observer never stops or kills processes.",
            "Observer never mutates active config.",
            "Live remains blocked.",
            "Drift monitor should run only after closed paper trades exist.",
        ],
    )


def files_df(files: List[RuntimeFile]) -> pd.DataFrame:
    return pd.DataFrame([asdict(f) for f in files])


def schemas_df(schemas: List[CsvSchema]) -> pd.DataFrame:
    return pd.DataFrame([asdict(s) for s in schemas])


def audits_df(audits: List[NativeFieldAudit]) -> pd.DataFrame:
    return pd.DataFrame([asdict(a) for a in audits])


def write_report(path: Path, decision: RuntimeDecision, files: List[RuntimeFile], schemas: List[CsvSchema], audits: List[NativeFieldAudit]) -> None:
    lines: List[str] = []
    lines.append("# Edge Factory OS Paper Runtime Observer Report")
    lines.append("")
    lines.append(f"Generated: `{decision.generated_at}`")
    lines.append(f"Runtime status: **{decision.runtime_status}**")
    lines.append(f"Next OS action: **{decision.next_os_action}**")
    lines.append(f"Paper dir: `{decision.paper_dir}`")
    lines.append(f"Paper dir exists: **{decision.paper_dir_exists}**")
    lines.append(f"Paper dir nonempty: **{decision.paper_dir_nonempty}**")
    lines.append(f"Closed trades detected: **{decision.closed_trades_detected}**")
    lines.append(f"Live allowed: **{decision.live_allowed}**")
    lines.append("")

    lines.append("## Runtime summary")
    lines.append("")
    lines.append(f"- Files found: **{len(files)}**")
    lines.append(f"- Trade CSV count: **{decision.trade_csv_count}**")
    lines.append(f"- Log CSV count: **{decision.log_csv_count}**")
    lines.append(f"- Native-ready files: **{decision.native_ready_file_count}**")
    lines.append(f"- Native-partial/alias files: **{decision.native_partial_file_count}**")
    lines.append(f"- Native-missing/unreadable files: **{decision.native_missing_file_count}**")
    lines.append(f"- Active family evidence count: **{decision.active_family_evidence_count}/{len(ACTIVE_FAMILIES)}**")
    lines.append("")

    lines.append("## Reasons")
    lines.append("")
    for r in decision.reasons:
        lines.append(f"- {r}")
    lines.append("")

    if decision.blockers:
        lines.append("## Blockers")
        lines.append("")
        for b in decision.blockers:
            lines.append(f"- `{b}`")
        lines.append("")

    if decision.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in decision.warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Native field audit")
    lines.append("")
    if not audits:
        lines.append("No CSV schemas were audited.")
    else:
        lines.append("| File | Kind | Status | Coverage | Missing | Aliases |")
        lines.append("|---|---|---:|---:|---|---|")
        for a in audits[:30]:
            lines.append(f"| `{a.relative_path}` | {a.kind} | {a.status} | {a.native_coverage:.2f} | {a.missing_required} | {a.alias_present} |")
    lines.append("")

    lines.append("## Hard rules")
    lines.append("")
    for r in decision.hard_rules:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    if decision.runtime_status == "PAPER_NOT_STARTED":
        lines.append("Paper has not started. This is expected before manual supervised paper launch. The OS should remain in gate/approval state.")
    elif decision.runtime_status == "PAPER_RUNNING_READY_FOR_DRIFT_CHECK":
        lines.append("Paper runtime has closed trade evidence. The next OS-level validator is live-vs-backtest drift monitor. Live remains blocked.")
    else:
        lines.append("Paper runtime has partial evidence or needs more data. Continue observing; do not move to live.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Edge Factory OS paper runtime observer")
    p.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    p.add_argument("--paper_dir", default=None)
    p.add_argument("--out_dir", default=None)
    p.add_argument("--sample_rows", type=int, default=100)
    p.add_argument("--max_files", type=int, default=5000)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    workspace = Path(args.workspace)
    paper_dir = Path(args.paper_dir) if args.paper_dir else workspace / DEFAULT_PAPER_DIR_NAME
    out_root = Path(args.out_dir) if args.out_dir else workspace / "edge_factory_os_paper_runtime_observer"
    out_dir = out_root / f"paper_runtime_{now_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = collect_runtime_files(paper_dir, max_files=int(args.max_files))
    interesting = [f for f in files if is_interesting_csv(f)]
    schemas: List[CsvSchema] = []
    audits: List[NativeFieldAudit] = []
    for f in interesting[:200]:
        p = Path(f.path)
        schema = read_csv_schema(p, paper_dir, sample_rows=int(args.sample_rows))
        schemas.append(schema)
        audits.append(audit_native_fields(schema, f.kind))

    decision = build_decision(workspace, paper_dir, files, schemas, audits)

    write_json(out_dir / "os_paper_runtime_observer_state.json", {
        "decision": asdict(decision),
        "files": [asdict(f) for f in files],
        "csv_schemas": [asdict(s) for s in schemas],
        "native_field_audit": [asdict(a) for a in audits],
    })
    files_df(files).to_csv(out_dir / "os_paper_runtime_files.csv", index=False)
    schemas_df(schemas).to_csv(out_dir / "os_paper_runtime_csv_schema.csv", index=False)
    audits_df(audits).to_csv(out_dir / "os_paper_runtime_native_field_audit.csv", index=False)
    write_report(out_dir / "os_paper_runtime_observer_report.md", decision, files, schemas, audits)

    print("EDGE FACTORY OS PAPER RUNTIME OBSERVER v1")
    print("=" * 100)
    print(f"workspace : {workspace}")
    print(f"paper_dir : {paper_dir}")
    print(f"output_dir: {out_dir}")
    print(f"runtime_status: {decision.runtime_status}")
    print(f"next_os_action: {decision.next_os_action}")
    print(f"paper_dir_exists={decision.paper_dir_exists} nonempty={decision.paper_dir_nonempty}")
    print(f"closed_trades_detected={decision.closed_trades_detected}")
    print(f"trade_csv_count={decision.trade_csv_count} log_csv_count={decision.log_csv_count}")
    print(f"native_ready={decision.native_ready_file_count} native_partial={decision.native_partial_file_count} native_missing={decision.native_missing_file_count}")
    print(f"active_family_evidence={decision.active_family_evidence_count}/{len(ACTIVE_FAMILIES)}")
    print("live_allowed: False")
    print("")
    print("REASONS")
    print("-" * 100)
    for r in decision.reasons:
        print(f"- {r}")
    if decision.blockers:
        print("")
        print("BLOCKERS")
        print("-" * 100)
        for b in decision.blockers:
            print(f"- {b}")
    if decision.warnings:
        print("")
        print("WARNINGS")
        print("-" * 100)
        for w in decision.warnings:
            print(f"- {w}")
    print("")
    print("IMPORTANT")
    print("-" * 100)
    print("This module did not start paper/live, did not run loggers, and did not mutate config.")
    print("")
    print(f"Report: {out_dir / 'os_paper_runtime_observer_report.md'}")
    print(f"State : {out_dir / 'os_paper_runtime_observer_state.json'}")
    return 0 if decision.runtime_status not in {"PAPER_RUNTIME_LOGGING_CONTRACT_MISSING_NATIVE_FIELDS"} else 2



if __name__ == "__main__":
    raise SystemExit(main())
