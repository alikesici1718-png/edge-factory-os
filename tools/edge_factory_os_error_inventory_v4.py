#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
DEFAULT_BASE_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_error_inventory_v4"

NETWORK_MARKERS = [
    "gaierror", "getaddrinfo failed", "name resolution", "dns",
    "temporary failure in name resolution", "urlerror", "httperror",
    "remote disconnected", "remotedisconnected",
    "remote end closed connection without response",
    "connectionerror", "connection aborted",
    "connection reset", "ssl", "sslerror", "tls", "timeout",
    "timed out", "readtimeout", "connecttimeout", "max retries exceeded",
    "too many requests", "rate limit", "429", "502", "503", "504",
    "okx 1h fetch failed", "okx 1m fetch failed", "fetch failed",
    "exchange fetch", "network", "connection refused",
]

CODE_MARKERS = [
    "traceback", "keyerror", "indexerror", "typeerror", "attributeerror",
    "zerodivisionerror", "assertionerror", "unboundlocalerror",
    "nameerror", "syntaxerror", "importerror", "modulenotfounderror",
]

SAFETY_MARKERS = [
    "risk limit", "kill switch", "halt", "safety", "capital",
    "notional", "leverage", "real order", "live order", "max position",
    "exposure limit", "drawdown", "margin", "order rejected",
]

DATA_MARKERS = [
    "empty dataframe", "empty data", "missing column", "parse error",
    "bad csv", "schema", "malformed", "invalid datetime", "cannot parse",
]

TEXT_FIELDS = [
    "where", "error_type", "error", "message", "msg", "exception",
    "traceback", "details", "detail", "reason", "symbol", "coin",
]

TIME_FIELDS = ["log_time", "timestamp", "time", "ts", "created_at", "datetime"]

RECENT_MINUTES = 180
STALE_HOURS = 24

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def run(cmd: list[str], cwd: Path | None = None, timeout: int = 40) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": p.returncode,
            "stdout": p.stdout or "",
            "stderr": p.stderr or "",
        }
    except Exception as e:
        return {
            "returncode": None,
            "stdout": "",
            "stderr": repr(e),
        }

def read_csv_rows(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    try:
        sample = text[:4096]
        dialect = csv.Sniffer().sniff(sample)
    except Exception:
        dialect = csv.excel

    try:
        reader = csv.DictReader(text.splitlines(), dialect=dialect)
        return [dict(row) for row in reader]
    except Exception:
        return []

def parse_time_value(v: str) -> datetime | None:
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def extract_time(row: dict) -> str:
    for k in TIME_FIELDS:
        if k in row:
            dt = parse_time_value(str(row.get(k) or ""))
            if dt:
                return dt.isoformat()
    return ""

def extract_text(row: dict) -> str:
    vals = []
    for k in TEXT_FIELDS:
        if k in row and row[k] not in (None, ""):
            vals.append(f"{k}={row[k]}")
    if not vals:
        for k, v in row.items():
            if k.lower() in TIME_FIELDS:
                continue
            if v not in (None, ""):
                vals.append(f"{k}={v}")
    return " | ".join(vals)

def contains_any(text: str, markers: list[str]) -> bool:
    t = text.lower()
    return any(m in t for m in markers)

def classify(text: str) -> tuple[str, str, str]:
    t = text.lower()

    # v3 priority: OKX fetch failures with gaierror/getaddrinfo are network warnings,
    # even if the row's error_type says RuntimeError.
    if contains_any(t, NETWORK_MARKERS):
        return (
            "NETWORK_OR_EXCHANGE_FETCH_WARNING",
            "ACKNOWLEDGEABLE_WARNING",
            "Network/exchange fetch marker found, including gaierror/getaddrinfo/OKX fetch failed.",
        )

    if contains_any(t, SAFETY_MARKERS):
        return (
            "SAFETY_OR_RISK_ERROR",
            "CRITICAL",
            "Risk/order/capital/position related marker found.",
        )

    if contains_any(t, CODE_MARKERS):
        return (
            "CODE_OR_LOGIC_ERROR",
            "CRITICAL",
            "Python/code exception marker found.",
        )

    if contains_any(t, DATA_MARKERS):
        return (
            "DATA_OR_PARSE_WARNING",
            "ATTENTION",
            "Data/schema/parse marker found.",
        )

    return (
        "UNKNOWN_ERROR",
        "CRITICAL",
        "No known marker matched; manual review required.",
    )

def infer_family(path: Path, row: dict) -> str:
    text = (str(path) + " " + extract_text(row)).lower()
    if "old_short" in text:
        return "old_short"
    if "impulse" in text:
        return "impulse_long"
    if "market_relative" in text:
        return "market_relative_short"
    if "weak_market" in text:
        return "weak_market_short"
    if "risk" in text:
        return "risk_manager"
    return "unknown"

def make_signature(row: dict, text: str, error_class: str) -> str:
    where = str(row.get("where") or "").strip()
    error_type = str(row.get("error_type") or row.get("exception") or "").strip()
    error = str(row.get("error") or row.get("message") or row.get("msg") or text).strip()
    error = " ".join(error.split())[:260]

    # Normalize coin-specific OKX fetch errors into grouped signatures.
    low = error.lower()
    if "okx 1h fetch failed" in low and "getaddrinfo failed" in low:
        error = "OKX 1H fetch failed: gaierror/getaddrinfo failed"
    elif "okx 1m fetch failed" in low and "getaddrinfo failed" in low:
        error = "OKX 1m fetch failed: gaierror/getaddrinfo failed"
    elif "getaddrinfo failed" in low:
        error = "Network DNS getaddrinfo failed"
    elif "remote end closed connection without response" in low or "remotedisconnected" in low:
        error = "Network remote disconnected without response"

    return f"{error_class}|{where}|{error_type}|{error}"

def recency_bucket(latest_time: str, now: datetime) -> tuple[str, str]:
    dt = parse_time_value(latest_time)
    if not dt:
        return "UNKNOWN_TIME", "No parseable timestamp."

    age_min = (now - dt).total_seconds() / 60.0
    if age_min <= RECENT_MINUTES:
        return "RECENT_ACTIVE", f"latest_age_min={round(age_min, 2)}"
    if age_min >= STALE_HOURS * 60:
        return "STALE_HISTORICAL", f"latest_age_hours={round(age_min / 60.0, 2)}"
    return "INTERMEDIATE", f"latest_age_hours={round(age_min / 60.0, 2)}"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_dir", default=str(DEFAULT_BASE_DIR))
    args = ap.parse_args()

    base_dir = Path(args.base_dir)
    out_dir = OUT_ROOT / f"error_inventory_v4_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)

    git = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool((git.get("stdout") or "").strip())

    candidate_files = []
    if base_dir.exists():
        for p in base_dir.rglob("*"):
            if p.is_file() and "error" in p.name.lower() and p.suffix.lower() in {".csv", ".txt", ".log"}:
                candidate_files.append(p)

    classified_rows = []
    file_rows = []

    for path in sorted(candidate_files):
        if path.suffix.lower() == ".csv":
            rows = read_csv_rows(path)
        else:
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                lines = []
            rows = [{"line": line} for line in lines if line.strip()]

        file_rows.append({
            "path": str(path),
            "row_count": len(rows),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat() if path.exists() else "",
        })

        for i, row in enumerate(rows):
            text = extract_text(row)
            event_time = extract_time(row)
            error_class, severity, reason = classify(text)
            family = infer_family(path, row)
            signature = make_signature(row, text, error_class)

            classified_rows.append({
                "source_file": str(path),
                "family": family,
                "row_index": i,
                "event_time": event_time,
                "signature": signature,
                "error_class": error_class,
                "severity": severity,
                "classification_reason": reason,
                "classification_text": text[:3000],
            })

    groups = {}
    for r in classified_rows:
        sig = r["signature"]
        if sig not in groups:
            groups[sig] = {
                "signature": sig,
                "error_class": r["error_class"],
                "severity": r["severity"],
                "families": set(),
                "source_files": set(),
                "count": 0,
                "first_time": "",
                "latest_time": "",
                "sample_text": r["classification_text"],
            }

        g = groups[sig]
        g["count"] += 1
        g["families"].add(r["family"])
        g["source_files"].add(r["source_file"])

        t = r["event_time"]
        if t:
            if not g["first_time"] or t < g["first_time"]:
                g["first_time"] = t
            if not g["latest_time"] or t > g["latest_time"]:
                g["latest_time"] = t

    group_rows = []
    for g in groups.values():
        bucket, age_detail = recency_bucket(g["latest_time"], now)
        group_rows.append({
            "signature": g["signature"],
            "error_class": g["error_class"],
            "severity": g["severity"],
            "count": g["count"],
            "families": ";".join(sorted(g["families"])),
            "source_files": ";".join(sorted(g["source_files"])),
            "first_time": g["first_time"],
            "latest_time": g["latest_time"],
            "recency_bucket": bucket,
            "age_detail": age_detail,
            "sample_text": g["sample_text"][:3000],
        })

    by_class = defaultdict(int)
    by_severity = defaultdict(int)
    by_recency = defaultdict(int)

    for r in classified_rows:
        by_class[r["error_class"]] += 1
        by_severity[r["severity"]] += 1

    for g in group_rows:
        by_recency[g["recency_bucket"]] += 1

    critical_groups = [g for g in group_rows if g["severity"] == "CRITICAL"]
    recent_critical_groups = [g for g in critical_groups if g["recency_bucket"] == "RECENT_ACTIVE"]
    unknown_groups = [g for g in group_rows if g["error_class"] == "UNKNOWN_ERROR"]
    acknowledgeable_groups = [g for g in group_rows if g["severity"] == "ACKNOWLEDGEABLE_WARNING"]

    if recent_critical_groups:
        inventory_status = "ERROR_INVENTORY_RECENT_CRITICAL_REVIEW_REQUIRED"
        next_action = "READ_RECENT_CRITICAL_ERRORS_MANUALLY"
    elif unknown_groups:
        inventory_status = "ERROR_INVENTORY_UNKNOWN_REVIEW_REQUIRED"
        next_action = "READ_UNKNOWN_ERRORS_MANUALLY"
    elif critical_groups:
        inventory_status = "ERROR_INVENTORY_STALE_CRITICALS_PRESENT"
        next_action = "CONFIRM_STALE_CRITICALS_THEN_ACKNOWLEDGE_OR_ARCHIVE"
    elif acknowledgeable_groups:
        inventory_status = "ERROR_INVENTORY_ACKNOWLEDGEABLE_NETWORK_WARNINGS"
        next_action = "ACKNOWLEDGE_NETWORK_WARNINGS_IF_NO_NEW_LOGIC_ERRORS"
    else:
        inventory_status = "ERROR_INVENTORY_EMPTY_OR_NO_ERRORS"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"

    state = {
        "generated_at": now_iso(),
        "base_dir": str(base_dir),
        "inventory_status": inventory_status,
        "next_action": next_action,
        "error_file_count": len(candidate_files),
        "error_row_count": len(classified_rows),
        "error_group_count": len(group_rows),
        "critical_group_count": len(critical_groups),
        "recent_critical_group_count": len(recent_critical_groups),
        "unknown_group_count": len(unknown_groups),
        "acknowledgeable_group_count": len(acknowledgeable_groups),
        "by_class": dict(by_class),
        "by_severity": dict(by_severity),
        "by_recency": dict(by_recency),
        "git_dirty": git_dirty,
        "git_status_short": (git.get("stdout") or "").strip(),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,
    }

    state_path = out_dir / "error_inventory_v4_state.json"
    latest_path = OUT_ROOT / "error_inventory_latest.json"
    files_csv = out_dir / "error_inventory_v4_files.csv"
    rows_csv = out_dir / "error_inventory_v4_classified_rows.csv"
    groups_csv = out_dir / "error_inventory_v4_groups.csv"
    critical_groups_csv = out_dir / "error_inventory_v4_critical_groups.csv"
    report_path = out_dir / "error_inventory_v4_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    with files_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "row_count", "size_bytes", "modified_at"])
        writer.writeheader()
        writer.writerows(file_rows)

    with rows_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_file", "family", "row_index", "event_time", "signature",
                "error_class", "severity", "classification_reason", "classification_text",
            ],
        )
        writer.writeheader()
        writer.writerows(classified_rows)

    group_fields = [
        "signature", "error_class", "severity", "count", "families",
        "source_files", "first_time", "latest_time", "recency_bucket",
        "age_detail", "sample_text",
    ]

    group_rows_sorted = sorted(
        group_rows,
        key=lambda x: (
            x["severity"] != "CRITICAL",
            x["recency_bucket"] != "RECENT_ACTIVE",
            -int(x["count"]),
            x["signature"],
        ),
    )

    with groups_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=group_fields)
        writer.writeheader()
        writer.writerows(group_rows_sorted)

    with critical_groups_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=group_fields)
        writer.writeheader()
        writer.writerows([g for g in group_rows_sorted if g["severity"] == "CRITICAL"])

    report = []
    report.append("# Edge Factory OS Error Inventory v3")
    report.append("")
    report.append(f"inventory_status: `{inventory_status}`")
    report.append(f"next_action: `{next_action}`")
    report.append(f"error_row_count: `{len(classified_rows)}`")
    report.append(f"error_group_count: `{len(group_rows)}`")
    report.append(f"critical_group_count: `{len(critical_groups)}`")
    report.append(f"recent_critical_group_count: `{len(recent_critical_groups)}`")
    report.append(f"unknown_group_count: `{len(unknown_groups)}`")
    report.append("")
    report.append("## Groups")
    for g in group_rows_sorted:
        report.append(
            f"- `{g['severity']}` `{g['error_class']}` count=`{g['count']}` "
            f"recency=`{g['recency_bucket']}` latest=`{g['latest_time']}` "
            f"signature=`{g['signature']}`"
        )
    report.append("")
    report.append("## Safety")
    report.append("- runtime_touch_allowed: `False`")
    report.append("- launcher_allowed: `False`")
    report.append("- patch_runtime_allowed: `False`")
    report.append("- active_paper_allowed: `False`")
    report.append("- live_allowed: `False`")
    report.append("- capital_change_allowed: `False`")
    report.append("- real_orders_allowed: `False`")
    report.append("- execution_performed: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS ERROR INVENTORY v4")
    print("=" * 100)
    print(f"inventory_status: {inventory_status}")
    print(f"next_action: {next_action}")
    print(f"base_dir: {base_dir}")
    print(f"error_file_count: {len(candidate_files)}")
    print(f"error_row_count: {len(classified_rows)}")
    print(f"error_group_count: {len(group_rows)}")
    print(f"critical_group_count: {len(critical_groups)}")
    print(f"recent_critical_group_count: {len(recent_critical_groups)}")
    print(f"unknown_group_count: {len(unknown_groups)}")
    print(f"acknowledgeable_group_count: {len(acknowledgeable_groups)}")
    print(f"git_dirty={git_dirty}")
    print()
    print("BY CLASS")
    print("-" * 100)
    for k, v in sorted(by_class.items(), key=lambda x: (-x[1], x[0])):
        print(f"{k}: {v}")
    print()
    print("BY RECENCY GROUPS")
    print("-" * 100)
    for k, v in sorted(by_recency.items(), key=lambda x: (-x[1], x[0])):
        print(f"{k}: {v}")
    print()
    print("TOP GROUPS")
    print("-" * 100)
    for g in group_rows_sorted[:20]:
        print(
            f"{g['severity']} | {g['error_class']} | count={g['count']} | "
            f"recency={g['recency_bucket']} | latest={g['latest_time']} | {g['signature'][:240]}"
        )
    print()
    print("SAFETY")
    print("-" * 100)
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("real_orders_allowed  : False")
    print("execution_performed  : False")
    print()
    print(f"State          : {state_path}")
    print(f"Latest         : {latest_path}")
    print(f"Files          : {files_csv}")
    print(f"Rows           : {rows_csv}")
    print(f"Groups         : {groups_csv}")
    print(f"CriticalGroups : {critical_groups_csv}")
    print(f"Report         : {report_path}")

if __name__ == "__main__":
    main()
