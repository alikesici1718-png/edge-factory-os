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
OUT_ROOT = WORKSPACE / "edge_factory_os_family_exposure_trend_watcher_v1"

JOURNAL_MASTER = WORKSPACE / "edge_factory_os_state_transition_journal_v1" / "os_state_transition_journal_master.jsonl"
MONITORING_PATH = WORKSPACE / "edge_factory_os_monitoring_stack_runner_v5" / "monitoring_stack_latest.json"
PROFILER_PATH = WORKSPACE / "edge_factory_os_family_exposure_profiler_v1" / "family_exposure_profiler_latest.json"
SAMPLE_PATH = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"
AGING_PATH = WORKSPACE / "edge_factory_os_open_pending_aging_watcher_v2" / "open_pending_aging_watcher_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"

LOOKBACK_ENTRIES = 12
HIGH_EXPOSURE = 10
PERSISTENT_NO_CLOSED_COUNT = 3

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e), "__path__": str(path)}

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"__parse_error__": line[:300]})
    return rows

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

def profiler_family_map(profiler: dict) -> dict:
    out = {}
    rows = profiler.get("families", [])
    if isinstance(rows, list):
        for r in rows:
            key = str(r.get("family_key") or "")
            if key:
                out[key] = r
    return out

def journal_family_snapshots(history: list[dict]) -> dict:
    out = {}

    for idx, entry in enumerate(history):
        generated_at = entry.get("generated_at", "")
        families = entry.get("families", {})
        if not isinstance(families, dict):
            continue

        for family_key, r in families.items():
            if family_key not in out:
                out[family_key] = []

            open_count = as_int(r.get("open"))
            pending = as_int(r.get("pending"))
            closed = as_int(r.get("closed"))
            errors = as_int(r.get("errors"))
            exposure = open_count + pending

            out[family_key].append({
                "idx": idx,
                "generated_at": generated_at,
                "open": open_count,
                "pending": pending,
                "closed": closed,
                "errors": errors,
                "exposure": exposure,
            })

    return out

def consecutive_no_closed_exposure(snaps: list[dict]) -> int:
    count = 0
    for s in reversed(snaps):
        if as_int(s.get("closed")) == 0 and as_int(s.get("exposure")) > 0:
            count += 1
        else:
            break
    return count

def classify_trend(
    family_key: str,
    latest: dict,
    first: dict,
    profiler_row: dict,
    consecutive_no_closed: int,
    observation_count: int,
) -> tuple[str, str, str]:
    latest_exposure = as_int(latest.get("exposure"))
    first_exposure = as_int(first.get("exposure"))
    exposure_delta = latest_exposure - first_exposure

    latest_closed = as_int(latest.get("closed"))
    first_closed = as_int(first.get("closed"))
    closed_delta = latest_closed - first_closed

    latest_errors = as_int(latest.get("errors"))
    first_errors = as_int(first.get("errors"))
    errors_delta = latest_errors - first_errors

    profile_key = str(profiler_row.get("profile_key") or "")
    profile_severity = str(profiler_row.get("profile_severity") or "")

    if errors_delta > 0:
        return (
            "ATTENTION",
            "FAMILY_ERROR_COUNT_INCREASED",
            f"errors increased by {errors_delta}",
        )

    if profile_severity == "ATTENTION" and profile_key == "NO_CLOSED_HIGH_EXPOSURE":
        if consecutive_no_closed >= PERSISTENT_NO_CLOSED_COUNT:
            return (
                "ATTENTION",
                "PERSISTENT_NO_CLOSED_HIGH_EXPOSURE",
                f"high exposure without closed sample persisted for {consecutive_no_closed} observations",
            )
        return (
            "ATTENTION",
            "NO_CLOSED_HIGH_EXPOSURE_CURRENT",
            "current profiler says high exposure with no closed sample",
        )

    if latest_closed == 0 and latest_exposure >= HIGH_EXPOSURE:
        return (
            "ATTENTION",
            "NO_CLOSED_HIGH_EXPOSURE_BY_TREND",
            "latest exposure high and closed sample still zero",
        )

    if latest_closed == 0 and latest_exposure > 0:
        return (
            "INFO",
            "NO_CLOSED_LOW_EXPOSURE_BY_TREND",
            "family has exposure but no closed sample yet",
        )

    if closed_delta > 0 and exposure_delta <= 0:
        return (
            "OK",
            "CLOSED_SAMPLE_IMPROVING",
            f"closed increased by {closed_delta} while exposure did not increase",
        )

    if closed_delta > 0:
        return (
            "OK",
            "CLOSED_SAMPLE_PROGRESSING",
            f"closed increased by {closed_delta}",
        )

    if latest_closed > 0:
        return (
            "OK",
            "HAS_CLOSED_SAMPLE_STABLE",
            "family has closed sample and no worsening trigger",
        )

    return (
        "OK",
        "INACTIVE_OR_NO_EXPOSURE",
        "family has no meaningful exposure",
    )

def main() -> int:
    out_dir = OUT_ROOT / f"family_exposure_trend_watcher_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    history_all = read_jsonl(JOURNAL_MASTER)
    history = history_all[-LOOKBACK_ENTRIES:] if len(history_all) > LOOKBACK_ENTRIES else history_all

    monitoring = read_json(MONITORING_PATH)
    profiler = read_json(PROFILER_PATH)
    sample = read_json(SAMPLE_PATH)
    aging = read_json(AGING_PATH)
    stack = read_json(STACK_PATH)

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    profiler_map = profiler_family_map(profiler)
    family_snaps = journal_family_snapshots(history)

    all_families = sorted(set(family_snaps.keys()) | set(profiler_map.keys()))

    rows = []

    for family_key in all_families:
        snaps = family_snaps.get(family_key, [])
        profiler_row = profiler_map.get(family_key, {})

        if snaps:
            first = snaps[0]
            latest = snaps[-1]
        else:
            first = {
                "open": as_int(profiler_row.get("open")),
                "pending": as_int(profiler_row.get("pending")),
                "closed": as_int(profiler_row.get("closed")),
                "errors": as_int(profiler_row.get("errors")),
                "exposure": as_int(profiler_row.get("open")) + as_int(profiler_row.get("pending")),
                "generated_at": "",
            }
            latest = dict(first)

        observation_count = len(snaps)
        consecutive_no_closed = consecutive_no_closed_exposure(snaps)

        severity, trend_key, trend_reason = classify_trend(
            family_key=family_key,
            latest=latest,
            first=first,
            profiler_row=profiler_row,
            consecutive_no_closed=consecutive_no_closed,
            observation_count=observation_count,
        )

        open_delta = as_int(latest.get("open")) - as_int(first.get("open"))
        pending_delta = as_int(latest.get("pending")) - as_int(first.get("pending"))
        closed_delta = as_int(latest.get("closed")) - as_int(first.get("closed"))
        errors_delta = as_int(latest.get("errors")) - as_int(first.get("errors"))
        exposure_delta = as_int(latest.get("exposure")) - as_int(first.get("exposure"))

        row = {
            "family_key": family_key,
            "observation_count": observation_count,
            "first_time": first.get("generated_at", ""),
            "latest_time": latest.get("generated_at", ""),

            "first_open": as_int(first.get("open")),
            "latest_open": as_int(latest.get("open")),
            "open_delta": open_delta,

            "first_pending": as_int(first.get("pending")),
            "latest_pending": as_int(latest.get("pending")),
            "pending_delta": pending_delta,

            "first_closed": as_int(first.get("closed")),
            "latest_closed": as_int(latest.get("closed")),
            "closed_delta": closed_delta,

            "first_errors": as_int(first.get("errors")),
            "latest_errors": as_int(latest.get("errors")),
            "errors_delta": errors_delta,

            "first_exposure": as_int(first.get("exposure")),
            "latest_exposure": as_int(latest.get("exposure")),
            "exposure_delta": exposure_delta,

            "consecutive_no_closed_exposure": consecutive_no_closed,

            "current_profile_severity": profiler_row.get("profile_severity", ""),
            "current_profile_key": profiler_row.get("profile_key", ""),
            "current_profile_reason": profiler_row.get("profile_reason", ""),
            "open_max_age_min": profiler_row.get("open_max_age_min", ""),
            "pending_max_age_min": profiler_row.get("pending_max_age_min", ""),

            "trend_severity": severity,
            "trend_key": trend_key,
            "trend_reason": trend_reason,
        }

        rows.append(row)

    attention_rows = [r for r in rows if r["trend_severity"] == "ATTENTION"]
    info_rows = [r for r in rows if r["trend_severity"] == "INFO"]

    runtime_ok = sample.get("runtime_ok") is True
    process_ok = sample.get("process_ok") is True
    health_ok = sample.get("health_ok") is True
    new_errors_since_ack = sample.get("new_errors_since_ack") is True
    stack_pass = stack.get("stack_status") == "STACK_PASS"

    snapshot_mismatch = aging.get("snapshot_mismatch") is True
    monitoring_status = monitoring.get("monitoring_status")
    profiler_status = profiler.get("profiler_status")

    total_closed = as_int(sample.get("closed"))
    total_open = as_int(sample.get("open"))
    total_pending = as_int(sample.get("pending"))
    total_errors = as_int(sample.get("errors"))
    drift_remaining = as_int(sample.get("drift_remaining"))
    capital_remaining = as_int(sample.get("capital_remaining"))

    if not runtime_ok or not process_ok or not health_ok:
        trend_status = "FAMILY_EXPOSURE_TREND_RUNTIME_ATTENTION"
        next_action = "RUN_READ_ONLY_RUNTIME_DIAGNOSTICS"
    elif new_errors_since_ack:
        trend_status = "FAMILY_EXPOSURE_TREND_NEW_ERRORS_ATTENTION"
        next_action = "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER"
    elif snapshot_mismatch:
        trend_status = "FAMILY_EXPOSURE_TREND_SNAPSHOT_MISMATCH_ATTENTION"
        next_action = "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_READ_ONLY"
    elif attention_rows:
        trend_status = "FAMILY_EXPOSURE_TREND_ATTENTION"
        next_action = "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE"
    elif info_rows:
        trend_status = "FAMILY_EXPOSURE_TREND_INFO"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"
    else:
        trend_status = "FAMILY_EXPOSURE_TREND_OK"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "trend_status": trend_status,
        "next_action": next_action,

        "lookback_entries": LOOKBACK_ENTRIES,
        "history_total_count": len(history_all),
        "history_used_count": len(history),

        "monitoring_status": monitoring_status,
        "profiler_status": profiler_status,
        "stack_pass": stack_pass,
        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "new_errors_since_ack": new_errors_since_ack,
        "snapshot_mismatch": snapshot_mismatch,

        "total_closed": total_closed,
        "total_open": total_open,
        "total_pending": total_pending,
        "total_errors": total_errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "attention_family_count": len(attention_rows),
        "info_family_count": len(info_rows),

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

    state_path = out_dir / "family_exposure_trend_watcher_v1_state.json"
    latest_path = OUT_ROOT / "family_exposure_trend_watcher_latest.json"
    families_csv = out_dir / "family_exposure_trend_watcher_v1_families.csv"
    attention_csv = out_dir / "family_exposure_trend_watcher_v1_attention.csv"
    report_path = out_dir / "family_exposure_trend_watcher_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    fieldnames = [
        "family_key", "observation_count", "first_time", "latest_time",
        "first_open", "latest_open", "open_delta",
        "first_pending", "latest_pending", "pending_delta",
        "first_closed", "latest_closed", "closed_delta",
        "first_errors", "latest_errors", "errors_delta",
        "first_exposure", "latest_exposure", "exposure_delta",
        "consecutive_no_closed_exposure",
        "current_profile_severity", "current_profile_key", "current_profile_reason",
        "open_max_age_min", "pending_max_age_min",
        "trend_severity", "trend_key", "trend_reason",
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
    md.append("# Edge Factory OS Family Exposure Trend Watcher v1")
    md.append("")
    md.append(f"trend_status: `{trend_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"history_used_count: `{len(history)}`")
    md.append("")
    md.append("## Attention families")
    if attention_rows:
        for r in attention_rows:
            md.append(f"- `{r['family_key']}` trend=`{r['trend_key']}` exposure=`{r['latest_exposure']}` closed=`{r['latest_closed']}` consecutive_no_closed=`{r['consecutive_no_closed_exposure']}` reason=`{r['trend_reason']}`")
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

    print("EDGE FACTORY OS FAMILY EXPOSURE TREND WATCHER v1")
    print("=" * 100)
    print(f"trend_status: {trend_status}")
    print(f"next_action: {next_action}")
    print(f"lookback_entries={LOOKBACK_ENTRIES} history_total_count={len(history_all)} history_used_count={len(history)}")
    print(f"monitoring_status={monitoring_status}")
    print(f"profiler_status={profiler_status}")
    print(f"total_closed={total_closed} total_open={total_open} total_pending={total_pending} total_errors={total_errors}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"attention_family_count={len(attention_rows)} info_family_count={len(info_rows)}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"new_errors_since_ack={new_errors_since_ack} snapshot_mismatch={snapshot_mismatch} stack_pass={stack_pass} git_dirty={git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("FAMILY TRENDS")
    print("-" * 100)
    for r in sorted(rows, key=lambda x: (x["trend_severity"] != "ATTENTION", x["trend_severity"] != "INFO", -x["latest_exposure"], x["family_key"])):
        print(
            f"{r['family_key']} | trend={r['trend_severity']}/{r['trend_key']} | "
            f"exposure {r['first_exposure']}->{r['latest_exposure']} Δ={r['exposure_delta']} | "
            f"closed {r['first_closed']}->{r['latest_closed']} Δ={r['closed_delta']} | "
            f"consecutive_no_closed={r['consecutive_no_closed_exposure']} | {r['trend_reason']}"
        )
    print()
    print(f"State    : {state_path}")
    print(f"Latest   : {latest_path}")
    print(f"Families : {families_csv}")
    print(f"Attention: {attention_csv}")
    print(f"Report   : {report_path}")

if __name__ == "__main__":
    main()
