#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO = WORKSPACE / "edge_factory_os_repo"
OUT_ROOT = WORKSPACE / "edge_factory_os_family_exposure_profiler_v1"

MONITORING_PATH = WORKSPACE / "edge_factory_os_monitoring_stack_runner_v4" / "monitoring_stack_latest.json"
SAMPLE_PATH = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"
AGING_PATH = WORKSPACE / "edge_factory_os_open_pending_aging_watcher_v2" / "open_pending_aging_watcher_latest.json"
BALANCE_PATH = WORKSPACE / "edge_factory_os_family_sample_balance_watcher_v1" / "family_sample_balance_watcher_latest.json"
TRIGGER_PATH = WORKSPACE / "edge_factory_os_trigger_engine_v1" / "os_trigger_engine_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"

HIGH_EXPOSURE_NO_CLOSED = 10
MEDIUM_EXPOSURE_NO_CLOSED = 1

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

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default

def as_float(v, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default

def sample_family_map(sample: dict) -> dict:
    out = {}
    rows = sample.get("family_counts", [])
    if isinstance(rows, list):
        for r in rows:
            key = str(r.get("family_key") or "")
            if not key:
                continue
            out[key] = {
                "open": as_int(r.get("open")),
                "pending": as_int(r.get("pending")),
                "closed": as_int(r.get("closed")),
                "errors": as_int(r.get("errors")),
                "rejected": as_int(r.get("rejected")),
            }
    return out

def aging_family_map(aging: dict) -> dict:
    out = {}
    rows = aging.get("queue_summaries", [])
    if isinstance(rows, list):
        for r in rows:
            key = str(r.get("family_key") or "")
            queue_type = str(r.get("queue_type") or "")
            if not key or not queue_type:
                continue

            if key not in out:
                out[key] = {}

            out[key][f"{queue_type}_rows"] = as_int(r.get("row_count"))
            out[key][f"{queue_type}_parsed"] = as_int(r.get("parsed_count"))
            out[key][f"{queue_type}_unknown"] = as_int(r.get("unknown_count"))
            out[key][f"{queue_type}_max_age_min"] = r.get("max_age_min", "")
            out[key][f"{queue_type}_median_age_min"] = r.get("median_age_min", "")
            out[key][f"{queue_type}_status"] = r.get("status", "")
            out[key][f"{queue_type}_reason"] = r.get("reason", "")
    return out

def balance_family_map(balance: dict) -> dict:
    out = {}
    rows = balance.get("families", [])
    if isinstance(rows, list):
        for r in rows:
            key = str(r.get("family_key") or "")
            if not key:
                continue
            out[key] = r
    return out

def classify_family(row: dict, total_closed: int) -> tuple[str, str, str]:
    open_count = as_int(row.get("open"))
    pending = as_int(row.get("pending"))
    closed = as_int(row.get("closed"))
    exposure = open_count + pending

    open_status = str(row.get("open_status") or "")
    pending_status = str(row.get("pending_status") or "")

    open_age_attention = open_status == "ATTENTION"
    pending_age_attention = pending_status == "ATTENTION"

    if open_age_attention or pending_age_attention:
        return (
            "ATTENTION",
            "FAMILY_QUEUE_AGE_ATTENTION",
            "Open/pending queue age crossed attention threshold.",
        )

    if closed == 0 and exposure >= HIGH_EXPOSURE_NO_CLOSED:
        return (
            "ATTENTION",
            "NO_CLOSED_HIGH_EXPOSURE",
            "Family has high open/pending exposure but no closed sample.",
        )

    if closed == 0 and exposure >= MEDIUM_EXPOSURE_NO_CLOSED:
        return (
            "INFO",
            "NO_CLOSED_LOW_EXPOSURE",
            "Family has exposure but no closed sample yet.",
        )

    if total_closed > 0 and closed > 0:
        closed_share = closed / total_closed
        if closed_share >= 0.75 and total_closed >= 5:
            return (
                "INFO",
                "DOMINANT_CLOSED_SAMPLE_FAMILY",
                "Closed sample is concentrated in this family.",
            )

    if closed > 0:
        return (
            "OK",
            "HAS_CLOSED_SAMPLE",
            "Family has closed sample.",
        )

    return (
        "OK",
        "INACTIVE_OR_EMPTY",
        "Family has no meaningful exposure.",
    )

def main() -> int:
    out_dir = OUT_ROOT / f"family_exposure_profiler_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    monitoring = read_json(MONITORING_PATH)
    sample = read_json(SAMPLE_PATH)
    aging = read_json(AGING_PATH)
    balance = read_json(BALANCE_PATH)
    trigger = read_json(TRIGGER_PATH)
    stack = read_json(STACK_PATH)

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    sfam = sample_family_map(sample)
    afam = aging_family_map(aging)
    bfam = balance_family_map(balance)

    all_families = sorted(set(sfam.keys()) | set(afam.keys()) | set(bfam.keys()))

    total_closed = as_int(sample.get("closed"))
    total_open = as_int(sample.get("open"))
    total_pending = as_int(sample.get("pending"))
    total_errors = as_int(sample.get("errors"))
    drift_remaining = as_int(sample.get("drift_remaining"))
    capital_remaining = as_int(sample.get("capital_remaining"))

    rows = []
    for family_key in all_families:
        s = sfam.get(family_key, {})
        a = afam.get(family_key, {})
        b = bfam.get(family_key, {})

        open_count = as_int(s.get("open"))
        pending = as_int(s.get("pending"))
        closed = as_int(s.get("closed"))
        errors = as_int(s.get("errors"))
        rejected = as_int(s.get("rejected"))

        exposure = open_count + pending
        closed_share = round(closed / total_closed, 4) if total_closed > 0 else 0.0
        exposure_share = round(exposure / max(1, total_open + total_pending), 4)

        row = {
            "family_key": family_key,
            "open": open_count,
            "pending": pending,
            "closed": closed,
            "errors": errors,
            "rejected": rejected,
            "exposure": exposure,
            "closed_share": closed_share,
            "exposure_share": exposure_share,

            "open_rows_direct": as_int(a.get("open_rows")),
            "pending_rows_direct": as_int(a.get("pending_rows")),
            "open_max_age_min": a.get("open_max_age_min", ""),
            "pending_max_age_min": a.get("pending_max_age_min", ""),
            "open_status": a.get("open_status", ""),
            "pending_status": a.get("pending_status", ""),

            "balance_severity": b.get("severity", ""),
            "balance_reason": b.get("reason", ""),
        }

        severity, profile_key, profile_reason = classify_family(row, total_closed)
        row["profile_severity"] = severity
        row["profile_key"] = profile_key
        row["profile_reason"] = profile_reason

        rows.append(row)

    attention_rows = [r for r in rows if r["profile_severity"] == "ATTENTION"]
    info_rows = [r for r in rows if r["profile_severity"] == "INFO"]

    runtime_ok = sample.get("runtime_ok") is True
    process_ok = sample.get("process_ok") is True
    health_ok = sample.get("health_ok") is True
    new_errors_since_ack = sample.get("new_errors_since_ack") is True
    stack_pass = stack.get("stack_status") == "STACK_PASS"

    monitoring_status = monitoring.get("monitoring_status")
    trigger_status = trigger.get("trigger_status")
    primary_trigger = trigger.get("primary_trigger", {})
    if not isinstance(primary_trigger, dict):
        primary_trigger = {}

    aging_status = aging.get("aging_status")
    snapshot_mismatch = aging.get("snapshot_mismatch")
    family_balance_status = balance.get("balance_status")

    if not runtime_ok or not process_ok or not health_ok:
        profiler_status = "FAMILY_EXPOSURE_RUNTIME_ATTENTION"
        next_action = "RUN_READ_ONLY_RUNTIME_DIAGNOSTICS"
    elif new_errors_since_ack:
        profiler_status = "FAMILY_EXPOSURE_NEW_ERRORS_ATTENTION"
        next_action = "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER"
    elif snapshot_mismatch:
        profiler_status = "FAMILY_EXPOSURE_SNAPSHOT_MISMATCH_ATTENTION"
        next_action = "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_READ_ONLY"
    elif attention_rows:
        profiler_status = "FAMILY_EXPOSURE_ATTENTION"
        next_action = "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE"
    elif info_rows:
        profiler_status = "FAMILY_EXPOSURE_INFO"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"
    else:
        profiler_status = "FAMILY_EXPOSURE_OK"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "profiler_status": profiler_status,
        "next_action": next_action,

        "monitoring_status": monitoring_status,
        "trigger_status": trigger_status,
        "primary_trigger": primary_trigger.get("trigger_key"),
        "aging_status": aging_status,
        "snapshot_mismatch": snapshot_mismatch,
        "family_balance_status": family_balance_status,

        "total_closed": total_closed,
        "total_open": total_open,
        "total_pending": total_pending,
        "total_errors": total_errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "attention_family_count": len(attention_rows),
        "info_family_count": len(info_rows),

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "new_errors_since_ack": new_errors_since_ack,
        "stack_pass": stack_pass,
        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,

        "families": rows,
        "attention_families": attention_rows,
        "info_families": info_rows,
    }

    state_path = out_dir / "family_exposure_profiler_v1_state.json"
    latest_path = OUT_ROOT / "family_exposure_profiler_latest.json"
    families_csv = out_dir / "family_exposure_profiler_v1_families.csv"
    attention_csv = out_dir / "family_exposure_profiler_v1_attention.csv"
    report_path = out_dir / "family_exposure_profiler_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    fieldnames = [
        "family_key", "open", "pending", "closed", "errors", "rejected",
        "exposure", "closed_share", "exposure_share",
        "open_rows_direct", "pending_rows_direct",
        "open_max_age_min", "pending_max_age_min",
        "open_status", "pending_status",
        "balance_severity", "balance_reason",
        "profile_severity", "profile_key", "profile_reason",
    ]

    with families_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with attention_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(attention_rows)

    md = []
    md.append("# Edge Factory OS Family Exposure Profiler v1")
    md.append("")
    md.append(f"profiler_status: `{profiler_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append("")
    md.append("## Attention families")
    if attention_rows:
        for r in attention_rows:
            md.append(f"- `{r['family_key']}` profile=`{r['profile_key']}` open=`{r['open']}` pending=`{r['pending']}` closed=`{r['closed']}` open_age=`{r['open_max_age_min']}` pending_age=`{r['pending_max_age_min']}`")
    else:
        md.append("- `NONE`")
    md.append("")
    md.append("## Info families")
    if info_rows:
        for r in info_rows:
            md.append(f"- `{r['family_key']}` profile=`{r['profile_key']}` open=`{r['open']}` pending=`{r['pending']}` closed=`{r['closed']}`")
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

    print("EDGE FACTORY OS FAMILY EXPOSURE PROFILER v1")
    print("=" * 100)
    print(f"profiler_status: {profiler_status}")
    print(f"next_action: {next_action}")
    print(f"monitoring_status={monitoring_status}")
    print(f"trigger_status={trigger_status} primary_trigger={primary_trigger.get('trigger_key')}")
    print(f"aging_status={aging_status} snapshot_mismatch={snapshot_mismatch}")
    print(f"family_balance_status={family_balance_status}")
    print(f"total_closed={total_closed} total_open={total_open} total_pending={total_pending} total_errors={total_errors}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"attention_family_count={len(attention_rows)} info_family_count={len(info_rows)}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"new_errors_since_ack={new_errors_since_ack} stack_pass={stack_pass} git_dirty={git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("FAMILY PROFILES")
    print("-" * 100)
    for r in sorted(rows, key=lambda x: (x["profile_severity"] != "ATTENTION", x["profile_severity"] != "INFO", -x["exposure"], x["family_key"])):
        print(
            f"{r['family_key']} | profile={r['profile_severity']}/{r['profile_key']} | "
            f"open={r['open']} pending={r['pending']} closed={r['closed']} exposure={r['exposure']} "
            f"open_age={r['open_max_age_min']} pending_age={r['pending_max_age_min']} | {r['profile_reason']}"
        )
    print()
    print(f"State    : {state_path}")
    print(f"Latest   : {latest_path}")
    print(f"Families : {families_csv}")
    print(f"Attention: {attention_csv}")
    print(f"Report   : {report_path}")

if __name__ == "__main__":
    main()
