#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Audits signal_id naming contract compliance across live paper logger source files and paper-run output CSVs by reading source code, sampling signal_id values from closed-trade CSVs, and classifying their format against the canonical COIN_STRATEGY_YYYYMMDDTHHMMSSZ shape.
Outputs a JSON audit state report to a stamped directory summarising compliant and non-compliant signal_id patterns per logger.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUN = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
OUT_ROOT = WORKSPACE / "edge_factory_signal_id_contract_auditor_v1"

SOURCE_FILES = [
    USERDIR / "global_paper_risk_manager_v3_priority.py",
    USERDIR / "global_paper_risk_manager_v4_config.py",
    USERDIR / "old_short_gate_aware_live_paper_logger.py",
    USERDIR / "impulse_long_gate_aware_live_paper_logger.py",
    USERDIR / "market_relative_live_paper_logger.py",
    USERDIR / "weak_market_breakdown_short_live_paper_logger.py",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        try:
            return pd.read_csv(path, engine="python")
        except Exception:
            return pd.DataFrame()

def norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    low = {c.lower(): c for c in df.columns}
    for x in candidates:
        if x.lower() in low:
            return low[x.lower()]
    return None

def sample_values(df: pd.DataFrame, col: str | None, n: int = 10) -> list[str]:
    if df.empty or not col or col not in df.columns:
        return []
    vals = df[col].dropna().astype(str).drop_duplicates().head(n).tolist()
    return vals

def infer_id_shape(s: str) -> str:
    # expected possibilities:
    # family_coin_YYYY...
    # coin_family_YYYY...
    parts = str(s).split("_")
    if len(parts) < 3:
        return "UNKNOWN_SHORT"

    last = parts[-1]
    first = parts[0]
    second = parts[1] if len(parts) > 1 else ""

    if re.search(r"\d{8}T\d{6}Z", last):
        if first in {"old", "market", "weak", "impulse"} or "short" in first or "long" in first:
            return "MAYBE_FAMILY_FIRST"
        if second in {"old", "market", "weak", "impulse"} or "short" in second or "long" in second:
            return "MAYBE_COIN_FIRST"
        return "TIME_SUFFIX_UNKNOWN_PREFIX"

    return "UNKNOWN_NO_TIME_SUFFIX"

def extract_signal_id_code(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return [{"file": str(path), "exists": False, "line": None, "text": "MISSING"}]

    txt = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rows = []
    for i, line in enumerate(txt, start=1):
        low = line.lower()
        if "signal_id" in low or "family_key" in low and "coin" in low and "base_time" in low:
            rows.append({
                "file": str(path),
                "exists": True,
                "line": i,
                "text": line.strip()[:500],
            })
    return rows[:80]

def main() -> int:
    out_dir = OUT_ROOT / f"signal_id_contract_audit_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    family_config_path = RUN / "family_config.json"
    family_config = read_json(family_config_path)

    families = {}
    if isinstance(family_config, dict):
        families = family_config.get("families", family_config)
    if not isinstance(families, dict):
        families = {}

    gate_path = RUN / "global_gate_decisions.csv"
    snapshot_path = RUN / "global_risk_snapshot.csv"

    gate = norm_cols(read_csv(gate_path))
    snapshot = norm_cols(read_csv(snapshot_path))

    family_rows = []
    all_family_signals = []

    for family_key, folder_raw in families.items():
        folder = Path(str(folder_raw))
        files = {
            "pending": folder / "pending_entries.csv",
            "open": folder / "open_positions.csv",
            "closed": folder / "closed_trades.csv",
            "rejected": folder / "rejected_entries.csv",
            "signals": folder / "signals.csv",
            "errors": folder / "errors.csv",
        }

        summary = {
            "family_key": family_key,
            "folder": str(folder),
            "folder_exists": folder.exists(),
        }

        for name, p in files.items():
            df = norm_cols(read_csv(p))
            summary[f"{name}_rows"] = int(len(df))
            sig_col = find_col(df, ["signal_id", "id", "signal"])
            coin_col = find_col(df, ["coin", "symbol", "inst_id", "instId"])
            time_col = find_col(df, ["target_entry_time", "signal_time", "entry_time", "time", "log_time"])

            summary[f"{name}_signal_id_col"] = sig_col or ""
            summary[f"{name}_coin_col"] = coin_col or ""
            summary[f"{name}_time_col"] = time_col or ""
            summary[f"{name}_signal_id_samples"] = " | ".join(sample_values(df, sig_col, 5))

            if sig_col:
                temp = df.copy()
                temp["__source_file"] = name
                temp["__family_key"] = family_key
                temp["__folder"] = str(folder)
                temp["__signal_id"] = temp[sig_col].astype(str)
                if coin_col:
                    temp["__coin"] = temp[coin_col].astype(str)
                else:
                    temp["__coin"] = ""
                if time_col:
                    temp["__time"] = temp[time_col].astype(str)
                else:
                    temp["__time"] = ""
                all_family_signals.append(temp[["__family_key", "__source_file", "__signal_id", "__coin", "__time"]])

        family_rows.append(summary)

    family_summary = pd.DataFrame(family_rows)

    if all_family_signals:
        family_signals = pd.concat(all_family_signals, ignore_index=True)
    else:
        family_signals = pd.DataFrame(columns=["__family_key", "__source_file", "__signal_id", "__coin", "__time"])

    # Gate summary
    if not gate.empty:
        gate_sig_col = find_col(gate, ["signal_id"])
        gate_family_col = find_col(gate, ["family_key"])
        gate_decision_col = find_col(gate, ["decision"])
        gate_reason_col = find_col(gate, ["reason"])
        gate_coin_col = find_col(gate, ["coin", "symbol"])
    else:
        gate_sig_col = gate_family_col = gate_decision_col = gate_reason_col = gate_coin_col = None

    decision_counts = {}
    if gate_decision_col:
        decision_counts = gate[gate_decision_col].astype(str).value_counts().to_dict()

    gate_samples = sample_values(gate, gate_sig_col, 20)
    family_samples = family_signals["__signal_id"].dropna().astype(str).drop_duplicates().head(20).tolist()

    gate_shapes = {x: infer_id_shape(x) for x in gate_samples}
    family_shapes = {x: infer_id_shape(x) for x in family_samples}

    # Match test: family signal_id should appear in gate for same family_key.
    match_rows = []
    if not gate.empty and gate_sig_col and gate_family_col and not family_signals.empty:
        gate_keyed = gate[[gate_family_col, gate_sig_col]].copy()
        gate_keyed.columns = ["family_key", "signal_id"]
        gate_keyed["family_key"] = gate_keyed["family_key"].astype(str)
        gate_keyed["signal_id"] = gate_keyed["signal_id"].astype(str)
        gate_keyed["gate_match_key"] = gate_keyed["family_key"] + "||" + gate_keyed["signal_id"]

        gate_keys = set(gate_keyed["gate_match_key"].tolist())

        for _, r in family_signals.iterrows():
            fk = str(r["__family_key"])
            sid = str(r["__signal_id"])
            src = str(r["__source_file"])
            key = fk + "||" + sid
            match_rows.append({
                "family_key": fk,
                "source_file": src,
                "signal_id": sid,
                "coin": r["__coin"],
                "time": r["__time"],
                "matched_in_gate_same_family_signal_id": key in gate_keys,
                "signal_id_shape": infer_id_shape(sid),
            })

    match_df = pd.DataFrame(match_rows)

    if not match_df.empty:
        match_by_source = match_df.groupby(["family_key", "source_file"]).agg(
            rows=("signal_id", "count"),
            matched=("matched_in_gate_same_family_signal_id", "sum"),
        ).reset_index()
        match_by_source["match_rate"] = match_by_source["matched"] / match_by_source["rows"]
    else:
        match_by_source = pd.DataFrame()

    code_rows = []
    for p in SOURCE_FILES:
        code_rows.extend(extract_signal_id_code(p))
    code_df = pd.DataFrame(code_rows)

    # Verdict logic
    findings = []
    severity = "OK"

    if gate.empty:
        findings.append("GATE_FILE_EMPTY_OR_UNREADABLE")
        severity = "ATTENTION"

    if gate_decision_col and "ALLOW" not in decision_counts:
        findings.append("NO_ALLOW_ROWS_IN_GATE_DECISIONS")
        severity = "ATTENTION"

    if not match_by_source.empty:
        bad = match_by_source[(match_by_source["rows"] > 0) & (match_by_source["match_rate"] < 0.20)]
        if not bad.empty:
            findings.append("LOW_SIGNAL_ID_MATCH_RATE_BETWEEN_FAMILY_FILES_AND_GATE")
            severity = "CRITICAL"

    # Special quick pattern mismatch heuristic
    gate_shape_set = set(gate_shapes.values())
    fam_shape_set = set(family_shapes.values())
    if "MAYBE_FAMILY_FIRST" in gate_shape_set and "MAYBE_COIN_FIRST" in fam_shape_set:
        findings.append("POSSIBLE_FAMILY_FIRST_VS_COIN_FIRST_SIGNAL_ID_MISMATCH")
        severity = "CRITICAL"
    if "MAYBE_COIN_FIRST" in gate_shape_set and "MAYBE_FAMILY_FIRST" in fam_shape_set:
        findings.append("POSSIBLE_COIN_FIRST_VS_FAMILY_FIRST_SIGNAL_ID_MISMATCH")
        severity = "CRITICAL"

    if not findings:
        findings.append("NO_OBVIOUS_SIGNAL_ID_CONTRACT_FAILURE_FOUND")

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "run": str(RUN),
        "severity": severity,
        "findings": findings,
        "gate_path": str(gate_path),
        "gate_rows": int(len(gate)),
        "gate_decision_counts": decision_counts,
        "gate_signal_id_col": gate_sig_col or "",
        "gate_family_col": gate_family_col or "",
        "gate_signal_id_samples": gate_samples,
        "gate_signal_id_shapes": gate_shapes,
        "family_signal_id_samples": family_samples,
        "family_signal_id_shapes": family_shapes,
        "family_count": len(families),
        "source_scan_rows": int(len(code_df)),
        "hard_rules": [
            "Read-only auditor.",
            "Does not modify scripts.",
            "Does not touch MASTER runtime.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not change capital."
        ],
    }

    state_path = out_dir / "signal_id_contract_audit_v1_state.json"
    family_csv = out_dir / "signal_id_contract_audit_v1_family_summary.csv"
    match_csv = out_dir / "signal_id_contract_audit_v1_match_detail.csv"
    match_source_csv = out_dir / "signal_id_contract_audit_v1_match_by_source.csv"
    code_csv = out_dir / "signal_id_contract_audit_v1_source_scan.csv"
    report_path = out_dir / "signal_id_contract_audit_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    family_summary.to_csv(family_csv, index=False)
    match_df.to_csv(match_csv, index=False)
    match_by_source.to_csv(match_source_csv, index=False)
    code_df.to_csv(code_csv, index=False)

    md = []
    md.append("# Edge Factory Signal ID Contract Audit v1")
    md.append("")
    md.append(f"Severity: `{severity}`")
    md.append("")
    md.append("## Findings")
    for x in findings:
        md.append(f"- `{x}`")
    md.append("")
    md.append("## Gate decision counts")
    md.append("```json")
    md.append(json.dumps(decision_counts, indent=2, ensure_ascii=False, default=str))
    md.append("```")
    md.append("")
    md.append("## Gate signal_id samples")
    for x in gate_samples[:20]:
        md.append(f"- `{x}` -> `{infer_id_shape(x)}`")
    md.append("")
    md.append("## Family signal_id samples")
    for x in family_samples[:20]:
        md.append(f"- `{x}` -> `{infer_id_shape(x)}`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY SIGNAL ID CONTRACT AUDITOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"run       : {RUN}")
    print(f"output_dir: {out_dir}")
    print(f"severity  : {severity}")
    print(f"gate_rows : {len(gate)}")
    print(f"gate_decision_counts: {decision_counts}")
    print()
    print("FINDINGS")
    print("-" * 100)
    for x in findings:
        print("-", x)
    print()
    print("GATE SIGNAL_ID SAMPLES")
    print("-" * 100)
    for x in gate_samples[:10]:
        print(f"{x} -> {infer_id_shape(x)}")
    print()
    print("FAMILY SIGNAL_ID SAMPLES")
    print("-" * 100)
    for x in family_samples[:10]:
        print(f"{x} -> {infer_id_shape(x)}")
    print()
    print("MATCH BY SOURCE")
    print("-" * 100)
    if not match_by_source.empty:
        print(match_by_source.to_string(index=False))
    else:
        print("No match data.")
    print()
    print("SOURCE SCAN")
    print("-" * 100)
    if not code_df.empty:
        print(code_df.head(80).to_string(index=False))
    else:
        print("No source scan rows.")
    print()
    print(f"State       : {state_path}")
    print(f"Family      : {family_csv}")
    print(f"MatchDetail : {match_csv}")
    print(f"MatchSource : {match_source_csv}")
    print(f"SourceScan  : {code_csv}")
    print(f"Report      : {report_path}")

if __name__ == "__main__":
    main()
