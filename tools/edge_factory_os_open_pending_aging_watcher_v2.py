#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUNTIME = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_open_pending_aging_watcher_v2"

SAMPLE_PATH = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"
FAMILY_BALANCE_PATH = WORKSPACE / "edge_factory_os_family_sample_balance_watcher_v1" / "family_sample_balance_watcher_latest.json"
TRIGGER_PATH = WORKSPACE / "edge_factory_os_trigger_engine_v1" / "os_trigger_engine_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"

OPEN_INFO_MINUTES = 24 * 60
OPEN_ATTENTION_MINUTES = 48 * 60
PENDING_INFO_MINUTES = 3 * 60
PENDING_ATTENTION_MINUTES = 12 * 60

OPEN_TIME_COLUMNS = [
    "entry_time", "open_time", "opened_at", "entry_utc", "signal_time",
    "created_at", "created_utc", "timestamp", "time", "log_time",
]

PENDING_TIME_COLUMNS = [
    "pending_time", "created_at", "created_utc", "signal_time", "entry_time",
    "timestamp", "time", "log_time",
]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

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
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": repr(e),
        }

def read_csv_rows(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []

def parse_dt(value) -> datetime | None:
    if value is None:
        return None

    s = str(value).strip()
    if not s or s.lower() in {"nan", "none", "null"}:
        return None

    try:
        x = float(s)
        if x > 1_000_000_000_000:
            return datetime.fromtimestamp(x / 1000.0, tz=timezone.utc)
        if x > 1_000_000_000:
            return datetime.fromtimestamp(x, tz=timezone.utc)
    except Exception:
        pass

    s2 = s.replace("Z", "+00:00")

    try:
        dt = datetime.fromisoformat(s2)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue

    return None

def find_row_time(row: dict, preferred_columns: list[str]) -> tuple[datetime | None, str, str]:
    lower_map = {str(k).lower(): k for k in row.keys()}

    for col in preferred_columns:
        original = lower_map.get(col.lower())
        if original is not None:
            dt = parse_dt(row.get(original))
            if dt is not None:
                return dt, str(original), str(row.get(original))

    keywords = ["time", "utc", "date", "created", "open", "entry", "signal", "log"]
    for k, v in row.items():
        kl = str(k).lower()
        if any(word in kl for word in keywords):
            dt = parse_dt(v)
            if dt is not None:
                return dt, str(k), str(v)

    return None, "", ""

def age_minutes(dt: datetime | None, now: datetime) -> float | None:
    if dt is None:
        return None
    return round((now - dt).total_seconds() / 60.0, 2)

def summarize_ages(ages: list[float]) -> dict:
    if not ages:
        return {
            "parsed_count": 0,
            "max_age_min": "",
            "median_age_min": "",
            "mean_age_min": "",
        }

    return {
        "parsed_count": len(ages),
        "max_age_min": round(max(ages), 2),
        "median_age_min": round(median(ages), 2),
        "mean_age_min": round(mean(ages), 2),
    }

def classify_queue(queue_type: str, count: int, parsed_count: int, unknown_count: int, max_age) -> tuple[str, str]:
    if count == 0:
        return "OK", "empty queue"

    if parsed_count == 0:
        if count >= 10:
            return "ATTENTION", "many rows but no parseable timestamps"
        return "INFO", "rows exist but no parseable timestamps"

    threshold_info = OPEN_INFO_MINUTES if queue_type == "open" else PENDING_INFO_MINUTES
    threshold_attention = OPEN_ATTENTION_MINUTES if queue_type == "open" else PENDING_ATTENTION_MINUTES

    try:
        max_age_float = float(max_age)
    except Exception:
        max_age_float = 0.0

    if max_age_float >= threshold_attention:
        return "ATTENTION", f"{queue_type} max age exceeds attention threshold"
    if max_age_float >= threshold_info:
        return "INFO", f"{queue_type} max age exceeds info threshold"

    if unknown_count > 0:
        return "INFO", f"{queue_type} has some rows with unknown age"

    return "OK", f"{queue_type} ages within threshold"

def as_int(value, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default

def load_family_config() -> dict:
    path = RUNTIME / "family_config.json"
    data = read_json(path)
    if isinstance(data, dict):
        return data
    return {}

def sample_family_map(sample: dict) -> dict:
    out = {}
    rows = sample.get("family_counts", [])
    if isinstance(rows, list):
        for r in rows:
            family_key = str(r.get("family_key") or "")
            if not family_key:
                continue
            out[family_key] = {
                "open": as_int(r.get("open")),
                "pending": as_int(r.get("pending")),
                "closed": as_int(r.get("closed")),
                "errors": as_int(r.get("errors")),
            }
    return out

def analyze_family_queue(
    family_key: str,
    folder: Path,
    queue_type: str,
    csv_name: str,
    time_columns: list[str],
    now: datetime,
) -> tuple[dict, list[dict]]:
    path = folder / csv_name
    rows = read_csv_rows(path)

    row_outputs = []
    ages = []
    unknown_count = 0
    oldest_time = ""
    oldest_age = None

    for idx, row in enumerate(rows, start=1):
        dt, time_col, raw_time = find_row_time(row, time_columns)
        age = age_minutes(dt, now)

        if age is None:
            unknown_count += 1
        else:
            ages.append(age)
            if oldest_age is None or age > oldest_age:
                oldest_age = age
                oldest_time = dt.isoformat()

        symbol = (
            row.get("symbol")
            or row.get("inst_id")
            or row.get("instrument")
            or row.get("coin")
            or row.get("ticker")
            or ""
        )

        row_outputs.append({
            "family_key": family_key,
            "queue_type": queue_type,
            "row_index": idx,
            "symbol": symbol,
            "time_column": time_col,
            "raw_time": raw_time,
            "parsed_time_utc": dt.isoformat() if dt else "",
            "age_minutes": age if age is not None else "",
            "csv_path": str(path),
        })

    summary_ages = summarize_ages(ages)

    status, reason = classify_queue(
        queue_type=queue_type,
        count=len(rows),
        parsed_count=summary_ages["parsed_count"],
        unknown_count=unknown_count,
        max_age=summary_ages["max_age_min"],
    )

    summary = {
        "family_key": family_key,
        "queue_type": queue_type,
        "csv_path": str(path),
        "folder_exists": folder.exists(),
        "row_count": len(rows),
        "parsed_count": summary_ages["parsed_count"],
        "unknown_count": unknown_count,
        "max_age_min": summary_ages["max_age_min"],
        "median_age_min": summary_ages["median_age_min"],
        "mean_age_min": summary_ages["mean_age_min"],
        "oldest_time_utc": oldest_time,
        "status": status,
        "reason": reason,
    }

    return summary, row_outputs

def build_consistency_rows(sample: dict, direct_counts: dict) -> list[dict]:
    rows = []
    smap = sample_family_map(sample)
    all_families = sorted(set(smap.keys()) | set(direct_counts.keys()))

    for family_key in all_families:
        s = smap.get(family_key, {})
        d = direct_counts.get(family_key, {})

        sample_open = as_int(s.get("open"))
        sample_pending = as_int(s.get("pending"))
        direct_open = as_int(d.get("open"))
        direct_pending = as_int(d.get("pending"))

        open_delta = direct_open - sample_open
        pending_delta = direct_pending - sample_pending

        mismatch = open_delta != 0 or pending_delta != 0

        severity = "ATTENTION" if abs(open_delta) + abs(pending_delta) >= 2 else ("INFO" if mismatch else "OK")
        reason = "direct CSV count differs from sample watcher latest" if mismatch else "sample watcher and direct CSV counts agree"

        rows.append({
            "family_key": family_key,
            "sample_open": sample_open,
            "direct_open": direct_open,
            "open_delta_direct_minus_sample": open_delta,
            "sample_pending": sample_pending,
            "direct_pending": direct_pending,
            "pending_delta_direct_minus_sample": pending_delta,
            "mismatch": mismatch,
            "severity": severity,
            "reason": reason,
        })

    return rows

def main() -> int:
    out_dir = OUT_ROOT / f"open_pending_aging_watcher_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)

    sample = read_json(SAMPLE_PATH)
    balance = read_json(FAMILY_BALANCE_PATH)
    trigger = read_json(TRIGGER_PATH)
    stack = read_json(STACK_PATH)
    policy = read_json(POLICY_PATH)
    family_config = load_family_config()

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    queue_summaries = []
    row_details = []
    direct_counts = {}

    for family_key, folder_raw in family_config.items():
        folder = Path(str(folder_raw))

        open_summary, open_rows = analyze_family_queue(
            family_key=family_key,
            folder=folder,
            queue_type="open",
            csv_name="open_positions.csv",
            time_columns=OPEN_TIME_COLUMNS,
            now=now,
        )
        pending_summary, pending_rows = analyze_family_queue(
            family_key=family_key,
            folder=folder,
            queue_type="pending",
            csv_name="pending_entries.csv",
            time_columns=PENDING_TIME_COLUMNS,
            now=now,
        )

        queue_summaries.extend([open_summary, pending_summary])
        row_details.extend(open_rows)
        row_details.extend(pending_rows)

        direct_counts[family_key] = {
            "open": open_summary["row_count"],
            "pending": pending_summary["row_count"],
        }

    consistency_rows = build_consistency_rows(sample, direct_counts)

    attention_queues = [q for q in queue_summaries if q["status"] == "ATTENTION"]
    info_queues = [q for q in queue_summaries if q["status"] == "INFO"]

    consistency_attention = [r for r in consistency_rows if r["severity"] == "ATTENTION"]
    consistency_info = [r for r in consistency_rows if r["severity"] == "INFO"]

    runtime_ok = sample.get("runtime_ok") is True
    process_ok = sample.get("process_ok") is True
    health_ok = sample.get("health_ok") is True
    new_errors_since_ack = sample.get("new_errors_since_ack") is True
    stack_pass = stack.get("stack_status") == "STACK_PASS"
    policy_pass = policy.get("policy_status") == "POLICY_ENGINE_PASS"

    sample_total_open = as_int(sample.get("open"))
    sample_total_pending = as_int(sample.get("pending"))
    direct_total_open = sum(as_int(v.get("open")) for v in direct_counts.values())
    direct_total_pending = sum(as_int(v.get("pending")) for v in direct_counts.values())

    total_open_delta = direct_total_open - sample_total_open
    total_pending_delta = direct_total_pending - sample_total_pending

    total_closed = as_int(sample.get("closed"))
    total_errors = as_int(sample.get("errors"))
    drift_remaining = as_int(sample.get("drift_remaining"))
    capital_remaining = as_int(sample.get("capital_remaining"))

    snapshot_mismatch = bool(total_open_delta != 0 or total_pending_delta != 0 or consistency_attention or consistency_info)

    if attention_queues:
        aging_status = "OPEN_PENDING_AGING_ATTENTION"
        next_action = "REVIEW_OPEN_PENDING_AGE_READ_ONLY"
    elif consistency_attention:
        aging_status = "OPEN_PENDING_CONSISTENCY_ATTENTION"
        next_action = "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_READ_ONLY"
    elif consistency_info or snapshot_mismatch:
        aging_status = "OPEN_PENDING_CONSISTENCY_INFO"
        next_action = "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_LATER"
    elif info_queues:
        aging_status = "OPEN_PENDING_AGING_INFO"
        next_action = "CONTINUE_MONITORING_OPEN_PENDING_AGE"
    else:
        aging_status = "OPEN_PENDING_AGING_OK"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "runtime": str(RUNTIME),
        "repo": str(REPO),

        "aging_status": aging_status,
        "next_action": next_action,
        "queue_summary_count": len(queue_summaries),
        "row_detail_count": len(row_details),
        "attention_queue_count": len(attention_queues),
        "info_queue_count": len(info_queues),

        "consistency_attention_count": len(consistency_attention),
        "consistency_info_count": len(consistency_info),
        "snapshot_mismatch": snapshot_mismatch,
        "sample_total_open": sample_total_open,
        "direct_total_open": direct_total_open,
        "total_open_delta_direct_minus_sample": total_open_delta,
        "sample_total_pending": sample_total_pending,
        "direct_total_pending": direct_total_pending,
        "total_pending_delta_direct_minus_sample": total_pending_delta,

        "total_closed": total_closed,
        "total_errors": total_errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "new_errors_since_ack": new_errors_since_ack,
        "stack_pass": stack_pass,
        "policy_pass": policy_pass,
        "trigger_status": trigger.get("trigger_status"),
        "primary_trigger": (trigger.get("primary_trigger") or {}).get("trigger_key") if isinstance(trigger.get("primary_trigger"), dict) else "",
        "family_balance_status": balance.get("balance_status"),

        "open_info_minutes": OPEN_INFO_MINUTES,
        "open_attention_minutes": OPEN_ATTENTION_MINUTES,
        "pending_info_minutes": PENDING_INFO_MINUTES,
        "pending_attention_minutes": PENDING_ATTENTION_MINUTES,

        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,

        "queue_summaries": queue_summaries,
        "attention_queues": attention_queues,
        "info_queues": info_queues,
        "consistency_rows": consistency_rows,
        "consistency_attention": consistency_attention,
        "consistency_info": consistency_info,
    }

    state_path = out_dir / "open_pending_aging_watcher_v2_state.json"
    latest_path = OUT_ROOT / "open_pending_aging_watcher_latest.json"
    summary_csv = out_dir / "open_pending_aging_watcher_v2_queue_summary.csv"
    rows_csv = out_dir / "open_pending_aging_watcher_v2_row_details.csv"
    attention_csv = out_dir / "open_pending_aging_watcher_v2_attention.csv"
    consistency_csv = out_dir / "open_pending_aging_watcher_v2_consistency.csv"
    report_path = out_dir / "open_pending_aging_watcher_v2_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "queue_type", "csv_path", "folder_exists",
                "row_count", "parsed_count", "unknown_count", "max_age_min",
                "median_age_min", "mean_age_min", "oldest_time_utc",
                "status", "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(queue_summaries)

    with rows_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "queue_type", "row_index", "symbol",
                "time_column", "raw_time", "parsed_time_utc",
                "age_minutes", "csv_path",
            ],
        )
        writer.writeheader()
        writer.writerows(row_details)

    with attention_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "queue_type", "csv_path", "folder_exists",
                "row_count", "parsed_count", "unknown_count", "max_age_min",
                "median_age_min", "mean_age_min", "oldest_time_utc",
                "status", "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(attention_queues)

    with consistency_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "sample_open", "direct_open", "open_delta_direct_minus_sample",
                "sample_pending", "direct_pending", "pending_delta_direct_minus_sample",
                "mismatch", "severity", "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(consistency_rows)

    md = []
    md.append("# Edge Factory OS Open/Pending Aging Watcher v2")
    md.append("")
    md.append(f"aging_status: `{aging_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"snapshot_mismatch: `{snapshot_mismatch}`")
    md.append("")
    md.append("## Totals")
    md.append(f"- sample_total_open: `{sample_total_open}`")
    md.append(f"- direct_total_open: `{direct_total_open}`")
    md.append(f"- total_open_delta_direct_minus_sample: `{total_open_delta}`")
    md.append(f"- sample_total_pending: `{sample_total_pending}`")
    md.append(f"- direct_total_pending: `{direct_total_pending}`")
    md.append(f"- total_pending_delta_direct_minus_sample: `{total_pending_delta}`")
    md.append("")
    md.append("## Consistency attention")
    if consistency_attention:
        for r in consistency_attention:
            md.append(f"- `{r['family_key']}` openΔ=`{r['open_delta_direct_minus_sample']}` pendingΔ=`{r['pending_delta_direct_minus_sample']}` reason=`{r['reason']}`")
    else:
        md.append("- `NONE`")
    md.append("")
    md.append("## Queue attention")
    if attention_queues:
        for q in attention_queues:
            md.append(f"- `{q['family_key']}` `{q['queue_type']}` rows=`{q['row_count']}` max_age_min=`{q['max_age_min']}` reason=`{q['reason']}`")
    else:
        md.append("- `NONE`")
    md.append("")
    md.append("## Safety")
    md.append("- runtime_touch_allowed: `False`")
    md.append("- launcher_allowed: `False`")
    md.append("- patch_runtime_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    md.append("- execution_performed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS OPEN/PENDING AGING WATCHER v2")
    print("=" * 100)
    print(f"aging_status: {aging_status}")
    print(f"next_action: {next_action}")
    print(f"queue_summary_count={len(queue_summaries)}")
    print(f"row_detail_count={len(row_details)}")
    print(f"attention_queue_count={len(attention_queues)}")
    print(f"info_queue_count={len(info_queues)}")
    print(f"consistency_attention_count={len(consistency_attention)}")
    print(f"consistency_info_count={len(consistency_info)}")
    print(f"snapshot_mismatch={snapshot_mismatch}")
    print(f"sample_total_open={sample_total_open} direct_total_open={direct_total_open} delta={total_open_delta}")
    print(f"sample_total_pending={sample_total_pending} direct_total_pending={direct_total_pending} delta={total_pending_delta}")
    print(f"total_closed={total_closed} total_errors={total_errors}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"new_errors_since_ack={new_errors_since_ack}")
    print(f"stack_pass={stack_pass} policy_pass={policy_pass}")
    print(f"trigger_status={trigger.get('trigger_status')} primary_trigger={state['primary_trigger']}")
    print(f"family_balance_status={balance.get('balance_status')}")
    print(f"git_dirty={git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("QUEUE SUMMARIES")
    print("-" * 100)
    for q in sorted(queue_summaries, key=lambda x: (x["status"] != "ATTENTION", x["status"] != "INFO", x["family_key"], x["queue_type"])):
        print(f"{q['family_key']} | {q['queue_type']} | rows={q['row_count']} parsed={q['parsed_count']} unknown={q['unknown_count']} max_age_min={q['max_age_min']} status={q['status']} | {q['reason']}")
    print()
    print("CONSISTENCY")
    print("-" * 100)
    for r in consistency_rows:
        print(f"{r['family_key']} | open sample={r['sample_open']} direct={r['direct_open']} Δ={r['open_delta_direct_minus_sample']} | pending sample={r['sample_pending']} direct={r['direct_pending']} Δ={r['pending_delta_direct_minus_sample']} | {r['severity']}")
    print()
    print("ATTENTION QUEUES")
    print("-" * 100)
    if attention_queues:
        for q in attention_queues:
            print(f"- {q['family_key']} {q['queue_type']} rows={q['row_count']} max_age_min={q['max_age_min']} reason={q['reason']}")
    else:
        print("NONE")
    print()
    print(f"State      : {state_path}")
    print(f"Latest     : {latest_path}")
    print(f"Summary    : {summary_csv}")
    print(f"Rows       : {rows_csv}")
    print(f"Attention  : {attention_csv}")
    print(f"Consistency: {consistency_csv}")
    print(f"Report     : {report_path}")

if __name__ == "__main__":
    main()
