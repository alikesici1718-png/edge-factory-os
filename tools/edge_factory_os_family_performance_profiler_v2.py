#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_family_performance_profiler_v2"

DEFAULT_BASE_DIR = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
PERFORMANCE_ANALYZER = Path(r"C:\Users\alike\edge_factory_live_performance_analyzer_v3.py")

GLOBAL_DRIFT_MIN_CLOSED = 20
FAMILY_MIN_CLOSED_SOFT = 5
FAMILY_MIN_CLOSED_HARD = 10

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_cmd(cmd: list[str], cwd: Path | None = None, timeout: int = 360) -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        return {
            "returncode": p.returncode,
            "stdout": p.stdout or "",
            "stderr": p.stderr or "",
            "exception": "",
        }
    except Exception as e:
        return {
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "exception": repr(e),
        }

def git_status() -> tuple[bool, str]:
    r = run_cmd(["git", "status", "--short"], cwd=REPO, timeout=40)
    out = (r.get("stdout") or "").strip()
    return bool(out), out

def as_float(v, default: float = 0.0) -> float:
    try:
        if v is None or str(v).strip() == "" or str(v).lower() == "nan":
            return default
        return float(v)
    except Exception:
        return default

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or str(v).strip() == "" or str(v).lower() == "nan":
            return default
        return int(float(v))
    except Exception:
        return default

def extract_scalar(stdout: str, key: str, default=None):
    pat = re.compile(rf"^{re.escape(key)}:\s*(.+?)\s*$", re.M)
    m = pat.search(stdout)
    if not m:
        return default
    return m.group(1).strip()

def extract_section(stdout: str, title: str) -> str:
    idx = stdout.find(title)
    if idx == -1:
        return ""

    part = stdout[idx:]
    lines = part.splitlines()

    # Skip title + separator lines; collect until next big title separator block.
    collected = []
    started = False
    header_seen = False

    for line in lines[2:]:
        stripped = line.strip()

        if stripped.startswith("=" * 20) and header_seen:
            break

        if not stripped:
            if started and header_seen:
                break
            continue

        if set(stripped) <= {"-", "="}:
            continue

        if not header_seen:
            header_seen = True
            started = True

        if started:
            collected.append(line.rstrip())

    return "\n".join(collected).strip()

def parse_family_summary(stdout: str) -> list[dict]:
    """
    Robust parser for the fixed-width FAMILY SUMMARY block printed by
    edge_factory_live_performance_analyzer_v3.py.

    v1 could fail because pandas.read_fwf may parse the whole header as one column.
    v2 first uses whitespace-column parsing and only falls back later.
    """
    lines = stdout.splitlines()

    title_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "FAMILY SUMMARY":
            title_idx = i
            break

    if title_idx is None:
        return []

    # Find header line after title.
    header_idx = None
    for i in range(title_idx + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            continue
        if set(stripped) <= {"=", "-"}:
            continue
        if "family_key" in stripped and "closed_trades" in stripped:
            header_idx = i
            break

    if header_idx is None:
        return []

    header = lines[header_idx].strip()
    cols = re.split(r"\s{2,}", header)

    rows = []
    for line in lines[header_idx + 1:]:
        stripped = line.strip()

        if not stripped:
            break
        if set(stripped) <= {"=", "-"}:
            break
        if stripped.endswith("MTM") or stripped in {"OPEN POSITIONS MTM", "PENDING ENTRIES", "PORTFOLIO SNAPSHOT"}:
            break

        parts = re.split(r"\s{2,}", stripped)

        # Expected exact match.
        if len(parts) == len(cols):
            row = dict(zip(cols, parts))
            rows.append(row)
            continue

        # Sometimes spacing around the last long column can be weird.
        if len(parts) > len(cols):
            row = dict(zip(cols[:-1], parts[:len(cols)-1]))
            row[cols[-1]] = parts[len(cols)-1]
            rows.append(row)
            continue

        # Pad shorter rows instead of dropping them.
        if len(parts) >= 2:
            padded = parts + [""] * (len(cols) - len(parts))
            row = dict(zip(cols, padded[:len(cols)]))
            rows.append(row)

    # Keep only real family rows.
    clean = []
    for r in rows:
        fam = str(r.get("family_key", "")).strip()
        if not fam or fam.lower() == "nan":
            continue
        if fam in {"family_key", "FAMILY", "SUMMARY"}:
            continue
        clean.append(r)

    return clean


def classify_family(row: dict, global_closed: int) -> tuple[str, str, str, str]:
    family = str(row.get("family_key", "")).strip()

    closed = as_int(row.get("closed_trades"))
    realized = as_float(row.get("realized_pnl"))
    unrealized = as_float(row.get("unrealized_pnl"))
    total = as_float(row.get("total_pnl_realized_plus_unrealized"))
    win_rate = as_float(row.get("win_rate_closed"))
    avg_ret = as_float(row.get("avg_net_ret_closed"))

    if closed == 0:
        return (
            "NO_SAMPLE",
            "WAIT",
            "No closed trades yet.",
            "KEEP_COLLECTING_SAMPLE",
        )

    if global_closed < GLOBAL_DRIFT_MIN_CLOSED:
        # Before global threshold, only strong warnings, no action.
        if total < 0 and realized < 0 and closed >= FAMILY_MIN_CLOSED_SOFT:
            return (
                "EARLY_NEGATIVE_WATCH",
                "WATCH_ONLY",
                f"Negative early family result before global drift threshold: closed={closed}, realized={realized:.4f}, total={total:.4f}",
                "KEEP_COLLECTING_SAMPLE_DO_NOT_CHANGE_CAPITAL",
            )

        if realized > 0 and total > 0 and closed >= FAMILY_MIN_CLOSED_SOFT:
            return (
                "EARLY_POSITIVE_INFO",
                "INFO",
                f"Positive early family result, but global closed threshold not reached: closed={closed}, realized={realized:.4f}, total={total:.4f}",
                "KEEP_COLLECTING_SAMPLE",
            )

        return (
            "EARLY_INCONCLUSIVE",
            "INFO",
            f"Sample below global review threshold: global_closed={global_closed}/{GLOBAL_DRIFT_MIN_CLOSED}, family_closed={closed}",
            "KEEP_COLLECTING_SAMPLE",
        )

    # After 20 closed, become stricter but still read-only.
    if closed < FAMILY_MIN_CLOSED_SOFT:
        return (
            "INSUFFICIENT_FAMILY_SAMPLE",
            "INFO",
            f"Global threshold reached but this family has too few closed trades: closed={closed}",
            "WAIT_FOR_FAMILY_SAMPLE",
        )

    if total < 0 and realized < 0 and win_rate < 0.40:
        return (
            "NEGATIVE_FAMILY_REVIEW",
            "ATTENTION",
            f"Family negative after review threshold: closed={closed}, win_rate={win_rate:.2f}, realized={realized:.4f}, total={total:.4f}",
            "READ_ONLY_FAMILY_REVIEW",
        )

    if realized > 0 and total > 0 and win_rate >= 0.50:
        return (
            "POSITIVE_FAMILY_CONFIRMATION",
            "OK",
            f"Family positive after review threshold: closed={closed}, win_rate={win_rate:.2f}, realized={realized:.4f}, total={total:.4f}",
            "KEEP_COLLECTING_OR_CONFIRM",
        )

    return (
        "MIXED_FAMILY_REVIEW",
        "INFO",
        f"Mixed family result: closed={closed}, win_rate={win_rate:.2f}, avg_ret={avg_ret:.6f}, realized={realized:.4f}, total={total:.4f}",
        "READ_ONLY_REVIEW_IF_NEEDED",
    )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_dir", default=str(DEFAULT_BASE_DIR))
    args = ap.parse_args()

    base_dir = Path(args.base_dir)
    out_dir = OUT_ROOT / f"family_performance_profiler_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    git_dirty, git_short = git_status()

    cmd = [sys.executable, str(PERFORMANCE_ANALYZER), "--base_dir", str(base_dir)]
    result = run_cmd(cmd, cwd=REPO)

    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")

    start_equity = as_float(extract_scalar(stdout, "start_equity"))
    total_realized = as_float(extract_scalar(stdout, "total_realized_pnl"))
    total_unrealized = as_float(extract_scalar(stdout, "total_unrealized_pnl"))
    estimated_equity = as_float(extract_scalar(stdout, "estimated_equity"))
    open_positions = as_int(extract_scalar(stdout, "open_positions"))
    pending_entries = as_int(extract_scalar(stdout, "pending_entries"))
    closed_trades = as_int(extract_scalar(stdout, "closed_trades"))
    open_notional = as_float(extract_scalar(stdout, "open_notional"))

    family_rows_raw = parse_family_summary(stdout)

    family_rows = []
    for raw in family_rows_raw:
        row = {
            "family_key": str(raw.get("family_key", "")).strip(),
            "closed_trades": as_int(raw.get("closed_trades")),
            "open_positions": as_int(raw.get("open_positions")),
            "pending_entries": as_int(raw.get("pending_entries")),
            "realized_pnl": as_float(raw.get("realized_pnl")),
            "unrealized_pnl": as_float(raw.get("unrealized_pnl")),
            "open_notional": as_float(raw.get("open_notional")),
            "win_rate_closed": as_float(raw.get("win_rate_closed")),
            "avg_net_ret_closed": as_float(raw.get("avg_net_ret_closed")),
            "total_pnl_realized_plus_unrealized": as_float(raw.get("total_pnl_realized_plus_unrealized")),
        }

        profile_key, severity, reason, recommended_action = classify_family(row, closed_trades)
        row["profile_key"] = profile_key
        row["profile_severity"] = severity
        row["profile_reason"] = reason
        row["recommended_action"] = recommended_action
        family_rows.append(row)

    watch_rows = [r for r in family_rows if r["profile_severity"] == "WATCH_ONLY"]
    attention_rows = [r for r in family_rows if r["profile_severity"] == "ATTENTION"]
    no_sample_rows = [r for r in family_rows if r["profile_key"] == "NO_SAMPLE"]
    positive_rows = [r for r in family_rows if r["profile_key"] in {"EARLY_POSITIVE_INFO", "POSITIVE_FAMILY_CONFIRMATION"}]

    if result.get("returncode") != 0:
        profiler_status = "FAMILY_PERFORMANCE_PROFILER_RUN_ATTENTION"
        next_action = "REVIEW_PERFORMANCE_ANALYZER_ERROR"
    elif not family_rows:
        profiler_status = "FAMILY_PERFORMANCE_PARSE_ATTENTION"
        next_action = "FIX_FAMILY_SUMMARY_PARSER_BEFORE_USING_PROFILE"
    elif closed_trades < GLOBAL_DRIFT_MIN_CLOSED and watch_rows:
        profiler_status = "FAMILY_PERFORMANCE_EARLY_WATCH"
        next_action = "KEEP_COLLECTING_SAMPLE_DO_NOT_CHANGE_CAPITAL"
    elif closed_trades < GLOBAL_DRIFT_MIN_CLOSED:
        profiler_status = "FAMILY_PERFORMANCE_COLLECTING"
        next_action = "KEEP_COLLECTING_SAMPLE_DO_NOT_TOUCH"
    elif attention_rows:
        profiler_status = "FAMILY_PERFORMANCE_REVIEW_ATTENTION"
        next_action = "READ_ONLY_FAMILY_PERFORMANCE_REVIEW"
    else:
        profiler_status = "FAMILY_PERFORMANCE_OK_OR_INFO"
        next_action = "KEEP_RUNNING_OR_READ_ONLY_REVIEW"

    estimated_return_pct = ((estimated_equity - start_equity) / start_equity * 100.0) if start_equity else 0.0

    state = {
        "generated_at": now_iso(),
        "base_dir": str(base_dir),
        "performance_analyzer": str(PERFORMANCE_ANALYZER),
        "analyzer_returncode": result.get("returncode"),
        "analyzer_exception": result.get("exception", ""),
        "profiler_status": profiler_status,
        "next_action": next_action,

        "start_equity": start_equity,
        "total_realized_pnl": total_realized,
        "total_unrealized_pnl": total_unrealized,
        "estimated_equity": estimated_equity,
        "estimated_return_pct": estimated_return_pct,
        "open_positions": open_positions,
        "pending_entries": pending_entries,
        "closed_trades": closed_trades,
        "open_notional": open_notional,

        "global_drift_min_closed": GLOBAL_DRIFT_MIN_CLOSED,
        "drift_remaining": max(0, GLOBAL_DRIFT_MIN_CLOSED - closed_trades),

        "family_count": len(family_rows),
        "watch_family_count": len(watch_rows),
        "attention_family_count": len(attention_rows),
        "no_sample_family_count": len(no_sample_rows),
        "positive_family_count": len(positive_rows),

        "git_dirty": git_dirty,
        "git_status_short": git_short,

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "families": family_rows,
    }

    state_path = out_dir / "family_performance_profiler_v2_state.json"
    latest_path = OUT_ROOT / "family_performance_profiler_latest.json"
    families_csv = out_dir / "family_performance_profiler_v2_families.csv"
    analyzer_stdout_path = out_dir / "family_performance_profiler_v2_analyzer_stdout.txt"
    analyzer_stderr_path = out_dir / "family_performance_profiler_v2_analyzer_stderr.txt"
    report_path = out_dir / "family_performance_profiler_v2_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    analyzer_stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    analyzer_stderr_path.write_text(stderr, encoding="utf-8", errors="replace")

    fieldnames = [
        "family_key", "closed_trades", "open_positions", "pending_entries",
        "realized_pnl", "unrealized_pnl", "open_notional",
        "win_rate_closed", "avg_net_ret_closed",
        "total_pnl_realized_plus_unrealized",
        "profile_key", "profile_severity", "profile_reason",
        "recommended_action",
    ]

    with families_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(family_rows)

    md = []
    md.append("# Edge Factory OS Family Performance Profiler v1")
    md.append("")
    md.append(f"profiler_status: `{profiler_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"closed_trades: `{closed_trades}`")
    md.append(f"estimated_return_pct: `{estimated_return_pct:.4f}`")
    md.append("")
    md.append("## Families")
    for r in family_rows:
        md.append(
            f"- `{r['family_key']}` profile=`{r['profile_key']}` severity=`{r['profile_severity']}` "
            f"closed=`{r['closed_trades']}` realized=`{r['realized_pnl']:.4f}` "
            f"unrealized=`{r['unrealized_pnl']:.4f}` total=`{r['total_pnl_realized_plus_unrealized']:.4f}` "
            f"reason=`{r['profile_reason']}`"
        )
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- launcher_allowed: `False`")
    md.append("- patch_runtime_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- real_orders_allowed: `False`")
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS FAMILY PERFORMANCE PROFILER v2")
    print("=" * 100)
    print(f"profiler_status: {profiler_status}")
    print(f"next_action: {next_action}")
    print(f"base_dir: {base_dir}")
    print(f"closed_trades: {closed_trades}")
    print(f"drift_remaining: {max(0, GLOBAL_DRIFT_MIN_CLOSED - closed_trades)}")
    print(f"start_equity: {start_equity}")
    print(f"estimated_equity: {estimated_equity}")
    print(f"estimated_return_pct: {estimated_return_pct:.4f}")
    print(f"total_realized_pnl: {total_realized}")
    print(f"total_unrealized_pnl: {total_unrealized}")
    print(f"open_positions: {open_positions}")
    print(f"pending_entries: {pending_entries}")
    print(f"git_dirty={git_dirty}")
    print()
    print("FAMILY PERFORMANCE PROFILES")
    print("-" * 100)
    for r in sorted(family_rows, key=lambda x: (x["profile_severity"] not in {"ATTENTION", "WATCH_ONLY"}, x["profile_key"], x["family_key"])):
        print(
            f"{r['family_key']} | {r['profile_severity']}/{r['profile_key']} | "
            f"closed={r['closed_trades']} open={r['open_positions']} pending={r['pending_entries']} | "
            f"realized={r['realized_pnl']:.4f} unrealized={r['unrealized_pnl']:.4f} "
            f"total={r['total_pnl_realized_plus_unrealized']:.4f} "
            f"wr={r['win_rate_closed']:.3f} avg_ret={r['avg_net_ret_closed']:.6f} | "
            f"{r['recommended_action']}"
        )
        print(f"  reason: {r['profile_reason']}")
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
    print(f"State   : {state_path}")
    print(f"Latest  : {latest_path}")
    print(f"Families: {families_csv}")
    print(f"Stdout  : {analyzer_stdout_path}")
    print(f"Stderr  : {analyzer_stderr_path}")
    print(f"Report  : {report_path}")

if __name__ == "__main__":
    main()
