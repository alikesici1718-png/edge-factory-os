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
OUT_ROOT = WORKSPACE / "edge_factory_os_family_performance_discipline_v1"

PERF_LATEST = WORKSPACE / "edge_factory_os_family_performance_profiler_v2" / "family_performance_profiler_latest.json"

DRIFT_MIN_CLOSED = 20
CAPITAL_MIN_CLOSED = 50

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
        return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as e:
        return {"returncode": None, "stdout": "", "stderr": repr(e)}

def as_int(v, default: int = 0) -> int:
    try:
        if v is None or str(v).strip() == "" or str(v).lower() == "nan":
            return default
        return int(float(v))
    except Exception:
        return default

def as_float(v, default: float = 0.0) -> float:
    try:
        if v is None or str(v).strip() == "" or str(v).lower() == "nan":
            return default
        return float(v)
    except Exception:
        return default

def classify_family_discipline(f: dict, global_closed: int) -> tuple[str, str, str, str, str]:
    family = str(f.get("family_key") or "")
    profile_key = str(f.get("profile_key") or "")
    profile_severity = str(f.get("profile_severity") or "")
    closed = as_int(f.get("closed_trades"))
    realized = as_float(f.get("realized_pnl"))
    unrealized = as_float(f.get("unrealized_pnl"))
    total = as_float(f.get("total_pnl_realized_plus_unrealized"))
    win_rate = as_float(f.get("win_rate_closed"))

    if closed == 0:
        return (
            "FAMILY_NO_SAMPLE_WAIT",
            "INFO",
            "WAIT_FOR_SAMPLE",
            "KEEP_COLLECTING_SAMPLE",
            f"{family} has no closed trades yet.",
        )

    if global_closed < DRIFT_MIN_CLOSED:
        if profile_key == "EARLY_NEGATIVE_WATCH" or profile_severity == "WATCH_ONLY":
            return (
                "FAMILY_EARLY_NEGATIVE_WATCH_ONLY",
                "ATTENTION",
                "WATCH_ONLY",
                "KEEP_COLLECTING_SAMPLE_DO_NOT_CHANGE_CAPITAL",
                f"{family} is negative before drift threshold: closed={closed}, win_rate={win_rate:.3f}, realized={realized:.4f}, unrealized={unrealized:.4f}, total={total:.4f}; global_closed={global_closed}/{DRIFT_MIN_CLOSED}",
            )

        if profile_key == "EARLY_POSITIVE_INFO":
            return (
                "FAMILY_EARLY_POSITIVE_INFO",
                "INFO",
                "COLLECT_ONLY",
                "KEEP_COLLECTING_SAMPLE",
                f"{family} is positive early but global sample is still below threshold: closed={closed}, total={total:.4f}",
            )

        return (
            "FAMILY_EARLY_INCONCLUSIVE",
            "INFO",
            "COLLECT_ONLY",
            "KEEP_COLLECTING_SAMPLE",
            f"{family} is inconclusive before global drift threshold: family_closed={closed}, global_closed={global_closed}/{DRIFT_MIN_CLOSED}",
        )

    # At/after drift threshold: still no mutation, only read-only review.
    if profile_key == "EARLY_NEGATIVE_WATCH" or total < 0:
        return (
            "FAMILY_NEGATIVE_DRIFT_REVIEW_READY",
            "ATTENTION",
            "READ_ONLY_FAMILY_DRIFT_REVIEW",
            "RUN_READ_ONLY_FAMILY_DRIFT_REVIEW",
            f"{family} is negative and global drift threshold is reached: closed={closed}, win_rate={win_rate:.3f}, realized={realized:.4f}, unrealized={unrealized:.4f}, total={total:.4f}",
        )

    if total > 0 and realized > 0:
        return (
            "FAMILY_POSITIVE_CONFIRMATION_REVIEW",
            "INFO",
            "READ_ONLY_CONFIRMATION_REVIEW",
            "RUN_READ_ONLY_FAMILY_CONFIRMATION_REVIEW",
            f"{family} is positive after drift threshold: closed={closed}, win_rate={win_rate:.3f}, total={total:.4f}",
        )

    return (
        "FAMILY_MIXED_DRIFT_REVIEW",
        "INFO",
        "READ_ONLY_FAMILY_DRIFT_REVIEW",
        "RUN_READ_ONLY_FAMILY_DRIFT_REVIEW",
        f"{family} is mixed after drift threshold: closed={closed}, realized={realized:.4f}, total={total:.4f}",
    )

def main() -> int:
    out_dir = OUT_ROOT / f"family_performance_discipline_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    perf = read_json(PERF_LATEST)
    git = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool((git.get("stdout") or "").strip())

    global_closed = as_int(perf.get("closed_trades"))
    drift_remaining = max(0, DRIFT_MIN_CLOSED - global_closed)
    capital_remaining = max(0, CAPITAL_MIN_CLOSED - global_closed)

    families = perf.get("families", [])
    if not isinstance(families, list):
        families = []

    rows = []
    for f in families:
        key, severity, allowed_scope, action, reason = classify_family_discipline(f, global_closed)
        row = {
            "family_key": f.get("family_key"),
            "closed_trades": as_int(f.get("closed_trades")),
            "open_positions": as_int(f.get("open_positions")),
            "pending_entries": as_int(f.get("pending_entries")),
            "realized_pnl": as_float(f.get("realized_pnl")),
            "unrealized_pnl": as_float(f.get("unrealized_pnl")),
            "total_pnl": as_float(f.get("total_pnl_realized_plus_unrealized")),
            "win_rate_closed": as_float(f.get("win_rate_closed")),
            "profile_key": f.get("profile_key"),
            "profile_severity": f.get("profile_severity"),
            "discipline_key": key,
            "discipline_severity": severity,
            "allowed_scope": allowed_scope,
            "recommended_action": action,
            "discipline_reason": reason,
        }
        rows.append(row)

    attention_rows = [r for r in rows if r["discipline_severity"] == "ATTENTION"]
    negative_watch = [r for r in rows if r["discipline_key"] in {"FAMILY_EARLY_NEGATIVE_WATCH_ONLY", "FAMILY_NEGATIVE_DRIFT_REVIEW_READY"}]

    if not rows:
        discipline_status = "FAMILY_PERFORMANCE_DISCIPLINE_PARSE_ATTENTION"
        next_action = "FIX_OR_RUN_FAMILY_PERFORMANCE_PROFILER"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
    elif global_closed < DRIFT_MIN_CLOSED and negative_watch:
        discipline_status = "FAMILY_PERFORMANCE_DISCIPLINE_EARLY_WATCH"
        next_action = "KEEP_COLLECTING_SAMPLE_DO_NOT_CHANGE_CAPITAL"
        severity = "ATTENTION"
        allowed_scope = "WATCH_ONLY"
    elif global_closed < DRIFT_MIN_CLOSED:
        discipline_status = "FAMILY_PERFORMANCE_DISCIPLINE_COLLECT_ONLY"
        next_action = "KEEP_COLLECTING_SAMPLE_DO_NOT_TOUCH"
        severity = "OK"
        allowed_scope = "COLLECT_ONLY"
    elif attention_rows:
        discipline_status = "FAMILY_PERFORMANCE_DISCIPLINE_REVIEW_READY"
        next_action = "RUN_READ_ONLY_FAMILY_DRIFT_REVIEW"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_FAMILY_DRIFT_REVIEW"
    else:
        discipline_status = "FAMILY_PERFORMANCE_DISCIPLINE_OK_OR_INFO"
        next_action = "KEEP_RUNNING_OR_READ_ONLY_CONFIRMATION"
        severity = "INFO"
        allowed_scope = "READ_ONLY_REVIEW"

    state = {
        "generated_at": now_iso(),
        "discipline_status": discipline_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,

        "profiler_status": perf.get("profiler_status"),
        "profiler_next_action": perf.get("next_action"),

        "closed_trades": global_closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "estimated_equity": as_float(perf.get("estimated_equity")),
        "estimated_return_pct": as_float(perf.get("estimated_return_pct")),
        "total_realized_pnl": as_float(perf.get("total_realized_pnl")),
        "total_unrealized_pnl": as_float(perf.get("total_unrealized_pnl")),

        "family_count": len(rows),
        "attention_family_count": len(attention_rows),
        "negative_watch_family_count": len(negative_watch),
        "attention_families": [r["family_key"] for r in attention_rows],
        "negative_watch_families": [r["family_key"] for r in negative_watch],

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

        "families": rows,
    }

    state_path = out_dir / "family_performance_discipline_v1_state.json"
    latest_path = OUT_ROOT / "family_performance_discipline_latest.json"
    families_csv = out_dir / "family_performance_discipline_v1_families.csv"
    report_path = out_dir / "family_performance_discipline_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    fields = [
        "family_key", "closed_trades", "open_positions", "pending_entries",
        "realized_pnl", "unrealized_pnl", "total_pnl", "win_rate_closed",
        "profile_key", "profile_severity", "discipline_key",
        "discipline_severity", "allowed_scope", "recommended_action",
        "discipline_reason",
    ]

    with families_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    md = []
    md.append("# Edge Factory OS Family Performance Discipline v1")
    md.append("")
    md.append(f"discipline_status: `{discipline_status}`")
    md.append(f"severity: `{severity}`")
    md.append(f"allowed_scope: `{allowed_scope}`")
    md.append(f"next_action: `{next_action}`")
    md.append(f"closed_trades: `{global_closed}`")
    md.append(f"drift_remaining: `{drift_remaining}`")
    md.append("")
    md.append("## Families")
    for r in rows:
        md.append(f"- `{r['family_key']}` `{r['discipline_severity']}` `{r['discipline_key']}` action=`{r['recommended_action']}` reason=`{r['discipline_reason']}`")
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

    print("EDGE FACTORY OS FAMILY PERFORMANCE DISCIPLINE v1")
    print("=" * 100)
    print(f"discipline_status: {discipline_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"profiler_status={perf.get('profiler_status')}")
    print(f"closed_trades={global_closed} drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"estimated_equity={state['estimated_equity']}")
    print(f"estimated_return_pct={state['estimated_return_pct']}")
    print(f"realized={state['total_realized_pnl']} unrealized={state['total_unrealized_pnl']}")
    print(f"attention_family_count={len(attention_rows)} negative_watch_family_count={len(negative_watch)}")
    print(f"git_dirty={git_dirty}")
    print()
    print("FAMILY DISCIPLINE")
    print("-" * 100)
    for r in rows:
        print(f"{r['family_key']} | {r['discipline_severity']}/{r['discipline_key']} | scope={r['allowed_scope']} | action={r['recommended_action']}")
        print(f"  reason: {r['discipline_reason']}")
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
    print(f"Report  : {report_path}")

if __name__ == "__main__":
    main()
