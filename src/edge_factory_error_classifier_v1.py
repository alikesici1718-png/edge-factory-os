#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classifies errors from the paper run logs into network warnings, logic/safety errors, and unknown errors by scanning log CSVs and JSON files in the MASTER_UPPER_SYSTEM paper run directory. Reads global gate decisions, risk snapshots, and violation logs, then writes a classifier state JSON with severity labels and error counts.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUN = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
OUT_ROOT = WORKSPACE / "edge_factory_error_classifier_v1"

NETWORK_PATTERNS = [
    "Remote end closed connection",
    "RemoteDisconnected",
    "handshake operation timed out",
    "TimeoutError",
    "URLError",
    "OKX fetch failed",
    "OKX 1m fetch failed",
    "OKX 1H fetch failed",
    "connection",
    "timeout",
    "timed out",
]

LOGIC_PATTERNS = [
    "KeyError",
    "ValueError",
    "TypeError",
    "IndexError",
    "NameError",
    "Traceback",
    "signal_id",
    "position",
    "sizing",
    "capital",
    "gate mismatch",
    "order",
    "live",
]

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

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

def classify_error(row: dict) -> tuple[str, str]:
    text = " ".join(str(v) for v in row.values())

    for p in LOGIC_PATTERNS:
        if p.lower() in text.lower():
            return "LOGIC_OR_SAFETY_ERROR", p

    for p in NETWORK_PATTERNS:
        if p.lower() in text.lower():
            return "NETWORK_OR_EXCHANGE_FETCH_WARNING", p

    return "UNKNOWN_REVIEW_REQUIRED", "no_pattern_match"

def main():
    out_dir = OUT_ROOT / f"error_classifier_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    family_config = read_json(RUN / "family_config.json")
    families = family_config if isinstance(family_config, dict) else {}

    rows = []
    for family_key, folder_raw in families.items():
        folder = Path(str(folder_raw))
        err_path = folder / "errors.csv"
        df = read_csv(err_path)

        if df.empty:
            continue

        df.columns = [str(c).strip() for c in df.columns]

        for _, r in df.iterrows():
            row = r.to_dict()
            cls, reason = classify_error(row)
            rows.append({
                "family_key": family_key,
                "error_path": str(err_path),
                "classification": cls,
                "classification_reason": reason,
                "log_time": row.get("log_time", ""),
                "where": row.get("where", ""),
                "inst_id": row.get("inst_id", ""),
                "error_type": row.get("error_type", ""),
                "error": row.get("error", ""),
            })

    result = pd.DataFrame(rows)

    if result.empty:
        status = "ERROR_CLASSIFIER_NO_ERRORS"
        severity = "OK"
        logic_count = 0
        network_count = 0
        unknown_count = 0
        acknowledge_network_warnings_allowed = True
    else:
        counts = result["classification"].value_counts().to_dict()
        logic_count = int(counts.get("LOGIC_OR_SAFETY_ERROR", 0))
        network_count = int(counts.get("NETWORK_OR_EXCHANGE_FETCH_WARNING", 0))
        unknown_count = int(counts.get("UNKNOWN_REVIEW_REQUIRED", 0))

        if logic_count > 0:
            status = "ERROR_CLASSIFIER_LOGIC_OR_SAFETY_ERRORS_PRESENT"
            severity = "CRITICAL"
            acknowledge_network_warnings_allowed = False
        elif unknown_count > 0:
            status = "ERROR_CLASSIFIER_UNKNOWN_ERRORS_REVIEW_REQUIRED"
            severity = "ATTENTION"
            acknowledge_network_warnings_allowed = False
        elif network_count > 0:
            status = "ERROR_CLASSIFIER_NETWORK_WARNINGS_ONLY"
            severity = "WARNING"
            acknowledge_network_warnings_allowed = True
        else:
            status = "ERROR_CLASSIFIER_OK"
            severity = "OK"
            acknowledge_network_warnings_allowed = True

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "run": str(RUN),
        "status": status,
        "severity": severity,
        "total_errors": int(len(result)),
        "logic_or_safety_error_count": logic_count,
        "network_warning_count": network_count,
        "unknown_error_count": unknown_count,
        "acknowledge_network_warnings_allowed": acknowledge_network_warnings_allowed,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "does_not_modify_error_files": True,
        "next_action": "ACKNOWLEDGE_NETWORK_WARNINGS_READ_ONLY" if acknowledge_network_warnings_allowed and network_count > 0 else "REVIEW_ERRORS",
    }

    state_path = out_dir / "error_classifier_v1_state.json"
    csv_path = out_dir / "error_classifier_v1_errors.csv"
    report_path = out_dir / "error_classifier_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    result.to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory Error Classifier v1")
    md.append("")
    md.append(f"Status: `{status}`")
    md.append(f"Severity: `{severity}`")
    md.append(f"Total errors: `{len(result)}`")
    md.append(f"Network warnings: `{network_count}`")
    md.append(f"Logic/safety errors: `{logic_count}`")
    md.append(f"Unknown errors: `{unknown_count}`")
    md.append("")
    md.append("## Safety")
    md.append("- Does not delete or modify error files.")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY ERROR CLASSIFIER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"run       : {RUN}")
    print(f"out_dir   : {out_dir}")
    print(f"status    : {status}")
    print(f"severity  : {severity}")
    print(f"total_errors: {len(result)}")
    print(f"network_warning_count: {network_count}")
    print(f"logic_or_safety_error_count: {logic_count}")
    print(f"unknown_error_count: {unknown_count}")
    print(f"acknowledge_network_warnings_allowed: {acknowledge_network_warnings_allowed}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("CLASSIFIED ERRORS")
    print("-" * 100)
    if result.empty:
        print("NONE")
    else:
        print(result[["family_key","classification","classification_reason","log_time","where","inst_id","error_type","error"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"CSV   : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
