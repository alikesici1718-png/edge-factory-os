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
OUT_ROOT = WORKSPACE / "edge_factory_os_family_sample_balance_watcher_v1"

SAMPLE_PATH = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"
TRIGGER_PATH = WORKSPACE / "edge_factory_os_trigger_engine_v1" / "os_trigger_engine_latest.json"
JOURNAL_PATH = WORKSPACE / "edge_factory_os_state_transition_journal_v1" / "state_transition_journal_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"
POLICY_PATH = WORKSPACE / "edge_factory_os_policy_engine_v1" / "os_policy_engine_latest.json"

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

def as_int(value, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default

def as_float(value, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default

def family_rows_from_sample(sample: dict) -> list[dict]:
    rows = sample.get("family_counts", [])
    if isinstance(rows, list):
        return rows
    return []

def severity_for_family(open_count: int, pending: int, closed: int, total_closed: int) -> tuple[str, str]:
    exposure = open_count + pending

    if closed == 0 and exposure >= 10:
        return "ATTENTION", "high exposure/pending but zero closed sample"
    if closed == 0 and exposure > 0:
        return "INFO", "has exposure but no closed sample yet"
    if total_closed > 0 and closed / total_closed >= 0.80 and total_closed >= 5:
        return "INFO", "closed sample concentrated in this family"
    if closed > 0:
        return "OK", "has closed sample"
    return "OK", "inactive/no sample yet"

def main() -> int:
    out_dir = OUT_ROOT / f"family_sample_balance_watcher_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    sample = read_json(SAMPLE_PATH)
    trigger = read_json(TRIGGER_PATH)
    journal = read_json(JOURNAL_PATH)
    stack = read_json(STACK_PATH)
    policy = read_json(POLICY_PATH)

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    stack_pass = stack.get("stack_status") == "STACK_PASS"
    policy_pass = policy.get("policy_status") == "POLICY_ENGINE_PASS"

    total_closed = as_int(sample.get("closed"))
    total_open = as_int(sample.get("open"))
    total_pending = as_int(sample.get("pending"))
    total_errors = as_int(sample.get("errors"))

    drift_remaining = as_int(sample.get("drift_remaining"))
    capital_remaining = as_int(sample.get("capital_remaining"))
    drift_ready = sample.get("drift_ready") is True
    capital_ready = sample.get("capital_review_ready") is True

    runtime_ok = sample.get("runtime_ok") is True
    process_ok = sample.get("process_ok") is True
    health_ok = sample.get("health_ok") is True
    new_errors_since_ack = sample.get("new_errors_since_ack") is True

    family_rows = []
    attention_flags = []
    info_flags = []

    raw_rows = family_rows_from_sample(sample)

    for r in raw_rows:
        family_key = str(r.get("family_key") or "UNKNOWN")
        open_count = as_int(r.get("open"))
        pending = as_int(r.get("pending"))
        closed = as_int(r.get("closed"))
        errors = as_int(r.get("errors"))
        rejected = as_int(r.get("rejected"))

        exposure = open_count + pending
        closed_share = round(closed / total_closed, 4) if total_closed > 0 else 0.0
        exposure_share = round(exposure / max(1, total_open + total_pending), 4)

        severity, reason = severity_for_family(open_count, pending, closed, total_closed)

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
            "severity": severity,
            "reason": reason,
        }
        family_rows.append(row)

        if severity == "ATTENTION":
            attention_flags.append(row)
        elif severity == "INFO":
            info_flags.append(row)

    closed_families = [r for r in family_rows if r["closed"] > 0]
    zero_closed_with_exposure = [r for r in family_rows if r["closed"] == 0 and r["exposure"] > 0]

    max_closed_share = max([r["closed_share"] for r in family_rows], default=0.0)
    closed_family_count = len(closed_families)

    sample_balance_notes = []

    if total_closed < 20:
        sample_balance_notes.append("total_closed_below_drift_threshold")

    if closed_family_count <= 2 and total_closed >= 5:
        sample_balance_notes.append("closed_sample_concentrated_in_few_families")

    if zero_closed_with_exposure:
        sample_balance_notes.append("some_families_have_exposure_but_zero_closed")

    if max_closed_share >= 0.75 and total_closed >= 5:
        sample_balance_notes.append("dominant_family_closed_share_high")

    if attention_flags:
        balance_status = "FAMILY_SAMPLE_BALANCE_ATTENTION"
        next_action = "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE"
    elif sample_balance_notes:
        balance_status = "FAMILY_SAMPLE_BALANCE_COLLECTING"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"
    else:
        balance_status = "FAMILY_SAMPLE_BALANCE_OK"
        next_action = "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH"

    primary_trigger = trigger.get("primary_trigger", {})
    primary_trigger_key = primary_trigger.get("trigger_key") if isinstance(primary_trigger, dict) else ""

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "balance_status": balance_status,
        "next_action": next_action,

        "total_closed": total_closed,
        "total_open": total_open,
        "total_pending": total_pending,
        "total_errors": total_errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_ready": drift_ready,
        "capital_review_ready": capital_ready,

        "closed_family_count": closed_family_count,
        "zero_closed_with_exposure_count": len(zero_closed_with_exposure),
        "attention_family_count": len(attention_flags),
        "info_family_count": len(info_flags),
        "max_closed_share": max_closed_share,
        "sample_balance_notes": sample_balance_notes,

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "new_errors_since_ack": new_errors_since_ack,
        "stack_pass": stack_pass,
        "policy_pass": policy_pass,
        "trigger_status": trigger.get("trigger_status"),
        "primary_trigger": primary_trigger_key,
        "journal_status": journal.get("journal_status"),

        "git_dirty": git_dirty,
        "git_status_short": git_status["stdout"].strip(),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "execution_performed": False,

        "families": family_rows,
        "attention_flags": attention_flags,
        "info_flags": info_flags,
    }

    state_path = out_dir / "family_sample_balance_watcher_v1_state.json"
    latest_path = OUT_ROOT / "family_sample_balance_watcher_latest.json"
    family_csv = out_dir / "family_sample_balance_watcher_v1_families.csv"
    attention_csv = out_dir / "family_sample_balance_watcher_v1_attention.csv"
    report_path = out_dir / "family_sample_balance_watcher_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with family_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "open", "pending", "closed", "errors", "rejected",
                "exposure", "closed_share", "exposure_share", "severity", "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(family_rows)

    with attention_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_key", "open", "pending", "closed", "errors", "rejected",
                "exposure", "closed_share", "exposure_share", "severity", "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(attention_flags)

    md = []
    md.append("# Edge Factory OS Family Sample Balance Watcher v1")
    md.append("")
    md.append(f"balance_status: `{balance_status}`")
    md.append(f"next_action: `{next_action}`")
    md.append("")
    md.append("## Totals")
    md.append(f"- total_closed: `{total_closed}`")
    md.append(f"- total_open: `{total_open}`")
    md.append(f"- total_pending: `{total_pending}`")
    md.append(f"- closed_family_count: `{closed_family_count}`")
    md.append(f"- zero_closed_with_exposure_count: `{len(zero_closed_with_exposure)}`")
    md.append(f"- attention_family_count: `{len(attention_flags)}`")
    md.append("")
    md.append("## Notes")
    if sample_balance_notes:
        for n in sample_balance_notes:
            md.append(f"- `{n}`")
    else:
        md.append("- `NONE`")
    md.append("")
    md.append("## Attention families")
    if attention_flags:
        for r in attention_flags:
            md.append(f"- `{r['family_key']}` open=`{r['open']}` pending=`{r['pending']}` closed=`{r['closed']}` reason=`{r['reason']}`")
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

    print("EDGE FACTORY OS FAMILY SAMPLE BALANCE WATCHER v1")
    print("=" * 100)
    print(f"balance_status: {balance_status}")
    print(f"next_action: {next_action}")
    print(f"total_closed={total_closed} total_open={total_open} total_pending={total_pending} total_errors={total_errors}")
    print(f"closed_family_count={closed_family_count}")
    print(f"zero_closed_with_exposure_count={len(zero_closed_with_exposure)}")
    print(f"attention_family_count={len(attention_flags)}")
    print(f"max_closed_share={max_closed_share}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"new_errors_since_ack={new_errors_since_ack}")
    print(f"stack_pass={stack_pass} policy_pass={policy_pass}")
    print(f"trigger_status={trigger.get('trigger_status')} primary_trigger={primary_trigger_key}")
    print(f"git_dirty={git_dirty}")
    print("runtime_touch_allowed: False")
    print("launcher_allowed     : False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed : False")
    print("live_allowed         : False")
    print("capital_change_allowed: False")
    print("execution_performed  : False")
    print()
    print("SAMPLE BALANCE NOTES")
    print("-" * 100)
    if sample_balance_notes:
        for n in sample_balance_notes:
            print(f"- {n}")
    else:
        print("NONE")
    print()
    print("FAMILY ROWS")
    print("-" * 100)
    for r in sorted(family_rows, key=lambda x: (-x["exposure"], -x["closed"], x["family_key"])):
        print(f"{r['family_key']} | open={r['open']} pending={r['pending']} closed={r['closed']} exposure={r['exposure']} closed_share={r['closed_share']} severity={r['severity']} | {r['reason']}")
    print()
    print(f"State    : {state_path}")
    print(f"Latest   : {latest_path}")
    print(f"Families : {family_csv}")
    print(f"Attention: {attention_csv}")
    print(f"Report   : {report_path}")

if __name__ == "__main__":
    main()
