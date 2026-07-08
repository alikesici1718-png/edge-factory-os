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
OUT_ROOT = WORKSPACE / "edge_factory_os_action_discipline_policy_v1"

MONITORING_PATH = WORKSPACE / "edge_factory_os_monitoring_stack_runner_v6" / "monitoring_stack_latest.json"
SAMPLE_PATH = WORKSPACE / "edge_factory_os_sample_maturity_watcher_v1" / "sample_maturity_watcher_latest.json"
TREND_PATH = WORKSPACE / "edge_factory_os_family_exposure_trend_watcher_v1" / "family_exposure_trend_watcher_latest.json"
PROFILER_PATH = WORKSPACE / "edge_factory_os_family_exposure_profiler_v1" / "family_exposure_profiler_latest.json"
STACK_PATH = WORKSPACE / "edge_factory_os_standard_stack_runner_v1" / "os_standard_stack_latest.json"

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

def add_rule(
    rows: list[dict],
    priority: int,
    rule_key: str,
    condition_met: bool,
    level: str,
    allowed_scope: str,
    recommended_action: str,
    reason: str,
    blocked_actions: str,
) -> None:
    rows.append({
        "priority": priority,
        "rule_key": rule_key,
        "condition_met": bool(condition_met),
        "level": level,
        "allowed_scope": allowed_scope,
        "recommended_action": recommended_action,
        "reason": reason,
        "blocked_actions": blocked_actions,
    })

def family_attention_names(data: dict, key: str) -> list[str]:
    rows = data.get(key, [])
    if not isinstance(rows, list):
        return []
    out = []
    for r in rows:
        if isinstance(r, dict):
            fam = str(r.get("family_key") or "")
            marker = str(r.get("trend_key") or r.get("profile_key") or "")
            if fam:
                out.append(f"{fam}:{marker}" if marker else fam)
    return out

def decide(rows: list[dict], git_dirty: bool) -> tuple[str, str, str, str, str]:
    active = sorted(
        [r for r in rows if r["condition_met"]],
        key=lambda x: x["priority"],
        reverse=True,
    )

    if not active:
        return (
            "ACTION_DISCIPLINE_OK_COLLECTING",
            "OK",
            "COLLECT_ONLY",
            "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
            "No active action rule.",
        )

    # Hard critical always wins unless it is only repo workflow.
    criticals = [r for r in active if r["level"] == "CRITICAL"]
    if criticals:
        r = criticals[0]
        return (
            f"ACTION_DISCIPLINE_{r['rule_key']}",
            "CRITICAL",
            r["allowed_scope"],
            r["recommended_action"],
            r["reason"],
        )

    if git_dirty:
        return (
            "ACTION_DISCIPLINE_REPO_ATTENTION",
            "ATTENTION",
            "REPO_ONLY_CLEANUP",
            "COMMIT_OR_REVIEW_REPO_CHANGES",
            "Repo is dirty; finish repo checkpoint before trusting downstream decisions.",
        )

    attentions = [r for r in active if r["level"] == "ATTENTION"]
    if attentions:
        r = attentions[0]
        return (
            f"ACTION_DISCIPLINE_{r['rule_key']}",
            "ATTENTION",
            r["allowed_scope"],
            r["recommended_action"],
            r["reason"],
        )

    infos = [r for r in active if r["level"] == "INFO"]
    if infos:
        r = infos[0]
        return (
            f"ACTION_DISCIPLINE_{r['rule_key']}",
            "INFO",
            r["allowed_scope"],
            r["recommended_action"],
            r["reason"],
        )

    r = active[0]
    return (
        f"ACTION_DISCIPLINE_{r['rule_key']}",
        r["level"],
        r["allowed_scope"],
        r["recommended_action"],
        r["reason"],
    )

def main() -> int:
    out_dir = OUT_ROOT / f"action_discipline_policy_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    monitoring = read_json(MONITORING_PATH)
    sample = read_json(SAMPLE_PATH)
    trend = read_json(TREND_PATH)
    profiler = read_json(PROFILER_PATH)
    stack = read_json(STACK_PATH)

    git = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git["stdout"].strip())

    summary = monitoring.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    stack_status = summary.get("stack_status") or stack.get("stack_status")
    monitoring_status = monitoring.get("monitoring_status")
    monitoring_severity = monitoring.get("severity")

    closed = as_int(summary.get("closed", sample.get("closed")))
    open_count = as_int(summary.get("open", sample.get("open")))
    pending = as_int(summary.get("pending", sample.get("pending")))
    errors = as_int(summary.get("errors", sample.get("errors")))

    drift_remaining = max(0, DRIFT_MIN_CLOSED - closed)
    capital_remaining = max(0, CAPITAL_MIN_CLOSED - closed)

    runtime_ok = summary.get("runtime_ok") is True or sample.get("runtime_ok") is True
    process_ok = summary.get("process_ok") is True or sample.get("process_ok") is True
    health_ok = summary.get("health_ok") is True or sample.get("health_ok") is True
    new_errors_since_ack = summary.get("new_errors_since_ack") is True or sample.get("new_errors_since_ack") is True

    snapshot_mismatch = summary.get("snapshot_mismatch") is True
    aging_status = summary.get("aging_status")
    trigger_status = summary.get("trigger_status")
    primary_trigger = summary.get("primary_trigger")
    family_balance_status = summary.get("family_balance_status")
    exposure_status = summary.get("family_exposure_profiler_status") or profiler.get("profiler_status")
    trend_status = summary.get("family_exposure_trend_status") or trend.get("trend_status")

    trend_attention_count = as_int(summary.get("family_exposure_trend_attention_count", trend.get("attention_family_count")))
    exposure_attention_count = as_int(summary.get("family_exposure_attention_count", profiler.get("attention_family_count")))

    trend_attention_families = family_attention_names(trend, "attention_families")
    profiler_attention_families = family_attention_names(profiler, "attention_families")

    rules: list[dict] = []

    add_rule(
        rules,
        10000,
        "RUNTIME_HEALTH_CRITICAL",
        not runtime_ok or not process_ok or not health_ok,
        "CRITICAL",
        "READ_ONLY_DIAGNOSTICS",
        "RUN_READ_ONLY_RUNTIME_DIAGNOSTICS",
        f"runtime_ok={runtime_ok}, process_ok={process_ok}, health_ok={health_ok}",
        "runtime_patch, launcher, active_paper, live, capital",
    )

    add_rule(
        rules,
        9500,
        "NEW_ERROR_REVIEW_REQUIRED",
        new_errors_since_ack,
        "ATTENTION",
        "READ_ONLY_ERROR_REVIEW",
        "RUN_ERROR_CLASSIFIER_AND_ACKNOWLEDGER",
        "New errors appeared since acknowledgement.",
        "runtime_patch, launcher, active_paper, live, capital",
    )

    add_rule(
        rules,
        9200,
        "STANDARD_STACK_NOT_PASS",
        stack_status != "STACK_PASS",
        "ATTENTION",
        "READ_ONLY_STACK_REVIEW",
        "RUN_STANDARD_STACK_REVIEW",
        f"stack_status={stack_status}",
        "runtime_patch, launcher, active_paper, live, capital",
    )

    add_rule(
        rules,
        8900,
        "SNAPSHOT_MISMATCH_REVIEW",
        snapshot_mismatch,
        "ATTENTION",
        "READ_ONLY_SNAPSHOT_REFRESH",
        "REFRESH_SAMPLE_AND_AGING_SNAPSHOT_READ_ONLY",
        "Sample watcher and direct CSV counts disagree.",
        "runtime_patch, launcher, active_paper, live, capital",
    )

    add_rule(
        rules,
        8000,
        "CAPITAL_REVIEW_READY_READ_ONLY",
        closed >= CAPITAL_MIN_CLOSED,
        "INFO",
        "READ_ONLY_CAPITAL_REVIEW",
        "RUN_CAPITAL_REVIEW_READ_ONLY",
        f"closed={closed}/{CAPITAL_MIN_CLOSED}",
        "automatic capital change, live, runtime_patch",
    )

    add_rule(
        rules,
        7500,
        "DRIFT_REVIEW_READY_READ_ONLY",
        closed >= DRIFT_MIN_CLOSED and closed < CAPITAL_MIN_CLOSED,
        "INFO",
        "READ_ONLY_DRIFT_REVIEW",
        "RUN_DRIFT_REVIEW_READ_ONLY",
        f"closed={closed}/{DRIFT_MIN_CLOSED}",
        "runtime_patch, active_paper, live, capital",
    )

    add_rule(
        rules,
        7000,
        "WATCH_ONLY_FAMILY_EXPOSURE_TREND_ATTENTION",
        trend_status == "FAMILY_EXPOSURE_TREND_ATTENTION" and closed < DRIFT_MIN_CLOSED,
        "ATTENTION",
        "WATCH_ONLY",
        "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
        f"trend_attention_count={trend_attention_count}; families={';'.join(trend_attention_families)}; closed={closed}/{DRIFT_MIN_CLOSED}",
        "runtime_patch, launcher, active_paper, live, capital, promotion",
    )

    add_rule(
        rules,
        6900,
        "WATCH_ONLY_FAMILY_EXPOSURE_ATTENTION",
        exposure_status == "FAMILY_EXPOSURE_ATTENTION" and closed < DRIFT_MIN_CLOSED,
        "ATTENTION",
        "WATCH_ONLY",
        "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
        f"exposure_attention_count={exposure_attention_count}; families={';'.join(profiler_attention_families)}; closed={closed}/{DRIFT_MIN_CLOSED}",
        "runtime_patch, launcher, active_paper, live, capital, promotion",
    )

    add_rule(
        rules,
        6800,
        "WATCH_ONLY_TRIGGER_ATTENTION",
        trigger_status == "TRIGGER_ENGINE_ATTENTION" and closed < DRIFT_MIN_CLOSED,
        "ATTENTION",
        "WATCH_ONLY",
        "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
        f"primary_trigger={primary_trigger}; closed={closed}/{DRIFT_MIN_CLOSED}",
        "runtime_patch, launcher, active_paper, live, capital, promotion",
    )

    add_rule(
        rules,
        6600,
        "WATCH_ONLY_FAMILY_BALANCE_ATTENTION",
        family_balance_status == "FAMILY_SAMPLE_BALANCE_ATTENTION" and closed < DRIFT_MIN_CLOSED,
        "ATTENTION",
        "WATCH_ONLY",
        "CONTINUE_MONITORING_FAMILY_SAMPLE_BALANCE",
        f"family_balance_status={family_balance_status}; closed={closed}/{DRIFT_MIN_CLOSED}",
        "runtime_patch, launcher, active_paper, live, capital, promotion",
    )

    add_rule(
        rules,
        5000,
        "OPEN_PENDING_AGING_INFO",
        aging_status in {"OPEN_PENDING_AGING_INFO", "OPEN_PENDING_CONSISTENCY_INFO"},
        "INFO",
        "WATCH_ONLY",
        "CONTINUE_MONITORING_OPEN_PENDING_AGE",
        f"aging_status={aging_status}",
        "runtime_patch, launcher, active_paper, live, capital",
    )

    add_rule(
        rules,
        1000,
        "SAMPLE_BELOW_REVIEW_THRESHOLDS",
        closed < DRIFT_MIN_CLOSED,
        "INFO",
        "COLLECT_ONLY",
        "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
        f"closed={closed}; drift_remaining={drift_remaining}; capital_remaining={capital_remaining}",
        "runtime_patch, launcher, active_paper, live, capital",
    )

    action_status, severity, allowed_scope, recommended_action, reason = decide(rules, git_dirty)

    # Preview if current file is the only blocker.
    clean_status, clean_severity, clean_scope, clean_action, clean_reason = decide(rules, False)

    # Hard safety flags: this policy never allows actual mutation.
    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),

        "action_status": action_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "recommended_action": recommended_action,
        "reason": reason,

        "clean_repo_decision_preview": {
            "action_status": clean_status,
            "severity": clean_severity,
            "allowed_scope": clean_scope,
            "recommended_action": clean_action,
            "reason": clean_reason,
        },

        "monitoring_status": monitoring_status,
        "monitoring_severity": monitoring_severity,
        "stack_status": stack_status,
        "trigger_status": trigger_status,
        "primary_trigger": primary_trigger,
        "family_balance_status": family_balance_status,
        "family_exposure_profiler_status": exposure_status,
        "family_exposure_trend_status": trend_status,
        "aging_status": aging_status,

        "closed": closed,
        "open": open_count,
        "pending": pending,
        "errors": errors,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,

        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "new_errors_since_ack": new_errors_since_ack,
        "snapshot_mismatch": snapshot_mismatch,

        "trend_attention_families": trend_attention_families,
        "profiler_attention_families": profiler_attention_families,

        "git_dirty": git_dirty,
        "git_status_short": git["stdout"].strip(),

        "runtime_touch_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "rules": sorted(rules, key=lambda x: x["priority"], reverse=True),
    }

    out_dir.mkdir(parents=True, exist_ok=True)

    state_path = out_dir / "action_discipline_policy_v1_state.json"
    latest_path = OUT_ROOT / "action_discipline_policy_latest.json"
    rules_csv = out_dir / "action_discipline_policy_v1_rules.csv"
    report_path = out_dir / "action_discipline_policy_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    fieldnames = [
        "priority", "rule_key", "condition_met", "level", "allowed_scope",
        "recommended_action", "reason", "blocked_actions",
    ]

    with rules_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(state["rules"])

    md = []
    md.append("# Edge Factory OS Action Discipline Policy v1")
    md.append("")
    md.append(f"action_status: `{action_status}`")
    md.append(f"severity: `{severity}`")
    md.append(f"allowed_scope: `{allowed_scope}`")
    md.append(f"recommended_action: `{recommended_action}`")
    md.append(f"reason: `{reason}`")
    md.append("")
    md.append("## Clean repo decision preview")
    md.append(f"- action_status: `{clean_status}`")
    md.append(f"- severity: `{clean_severity}`")
    md.append(f"- allowed_scope: `{clean_scope}`")
    md.append(f"- recommended_action: `{clean_action}`")
    md.append(f"- reason: `{clean_reason}`")
    md.append("")
    md.append("## Active rules")
    for r in state["rules"]:
        if r["condition_met"]:
            md.append(f"- `{r['level']}` `{r['rule_key']}` scope=`{r['allowed_scope']}` action=`{r['recommended_action']}` reason=`{r['reason']}`")
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

    print("EDGE FACTORY OS ACTION DISCIPLINE POLICY v1")
    print("=" * 100)
    print(f"action_status: {action_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"recommended_action: {recommended_action}")
    print(f"reason: {reason}")
    print(f"git_dirty={git_dirty}")
    print()
    print("CLEAN REPO DECISION PREVIEW")
    print("-" * 100)
    print(f"action_status: {clean_status}")
    print(f"severity: {clean_severity}")
    print(f"allowed_scope: {clean_scope}")
    print(f"recommended_action: {clean_action}")
    print(f"reason: {clean_reason}")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"monitoring_status={monitoring_status}")
    print(f"stack_status={stack_status}")
    print(f"trigger_status={trigger_status} primary_trigger={primary_trigger}")
    print(f"family_exposure_trend_status={trend_status}")
    print(f"family_exposure_profiler_status={exposure_status}")
    print(f"family_balance_status={family_balance_status}")
    print(f"aging_status={aging_status}")
    print(f"closed={closed} open={open_count} pending={pending} errors={errors}")
    print(f"drift_remaining={drift_remaining} capital_remaining={capital_remaining}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"new_errors_since_ack={new_errors_since_ack} snapshot_mismatch={snapshot_mismatch}")
    print()
    print("ACTIVE RULES")
    print("-" * 100)
    active = [r for r in state["rules"] if r["condition_met"]]
    if active:
        for r in active:
            print(f"[{r['level']}] {r['rule_key']} | scope={r['allowed_scope']} | action={r['recommended_action']} | reason={r['reason']}")
    else:
        print("NONE")
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
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Rules : {rules_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
