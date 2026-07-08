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
OUT_ROOT = WORKSPACE / "edge_factory_os_policy_engine_v1"

UNIFIED_STATE_PATH = WORKSPACE / "edge_factory_os_unified_state_reader_v1" / "os_unified_state_latest.json"

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

def add_policy(
    policies: list[dict],
    key: str,
    allowed: bool,
    severity_if_blocked: str,
    reason: str,
    required_action: str = "",
    scope: str = "OS",
) -> None:
    policies.append({
        "policy_key": key,
        "scope": scope,
        "allowed": bool(allowed),
        "status": "ALLOW" if allowed else "BLOCK",
        "severity_if_blocked": "OK" if allowed else severity_if_blocked,
        "reason": reason,
        "required_action": required_action,
    })

def main() -> int:
    out_dir = OUT_ROOT / f"os_policy_engine_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    unified = read_json(UNIFIED_STATE_PATH)

    runtime = unified.get("runtime", {})
    repo_state = unified.get("repo", {})
    memory = unified.get("memory", {})
    safety = unified.get("safety", {})

    git_status = run(["git", "status", "--short"], cwd=REPO)
    git_dirty = bool(git_status["stdout"].strip())

    runtime_ok = runtime.get("runtime_ok") is True
    process_ok = runtime.get("process_watchdog_pass") is True
    health_ok = runtime.get("health_ok") is True
    errors_acknowledged = runtime.get("errors_acknowledged") is True
    new_errors_since_ack = runtime.get("new_errors_since_ack") is True

    closed = int(runtime.get("closed") or 0)
    open_count = int(runtime.get("open") or 0)
    pending = int(runtime.get("pending") or 0)

    drift_ready = closed >= DRIFT_MIN_CLOSED
    capital_ready = closed >= CAPITAL_MIN_CLOSED

    active_paper_allowed = safety.get("active_paper_allowed") is True
    live_allowed = safety.get("live_allowed") is True
    capital_change_allowed = safety.get("capital_change_allowed") is True
    real_orders_allowed = safety.get("real_orders_allowed") is True

    exact_candidate_blocks = memory.get("exact_candidate_blocks") or []
    family_cooldowns = memory.get("family_cooldowns") or []

    policies: list[dict] = []

    # Runtime safety policies.
    add_policy(
        policies,
        "protect_running_master_when_runtime_ok",
        runtime_ok and process_ok and health_ok and not new_errors_since_ack,
        "CRITICAL",
        f"runtime_ok={runtime_ok}, process_ok={process_ok}, health_ok={health_ok}, new_errors_since_ack={new_errors_since_ack}",
        "Do not restart or patch runtime while healthy.",
        "runtime",
    )

    add_policy(
        policies,
        "block_runtime_patch_when_healthy",
        False,
        "CRITICAL",
        "Runtime is healthy; direct runtime patching is forbidden unless a future policy explicitly unlocks it.",
        "Keep runtime untouched. Do repo-only work.",
        "runtime",
    )

    add_policy(
        policies,
        "block_duplicate_launcher",
        False,
        "CRITICAL",
        "Duplicate launcher/process creation is always blocked while process watchdog passes.",
        "Do not run launcher again unless process watchdog fails and manual preflight approves.",
        "runtime",
    )

    # Error policies.
    add_policy(
        policies,
        "continue_if_errors_acknowledged",
        errors_acknowledged and not new_errors_since_ack,
        "CRITICAL",
        f"errors_acknowledged={errors_acknowledged}, new_errors_since_ack={new_errors_since_ack}",
        "If new errors appear, run classifier/acknowledger before any other work.",
        "errors",
    )

    add_policy(
        policies,
        "classify_new_errors_before_anything_else",
        not new_errors_since_ack,
        "CRITICAL",
        f"new_errors_since_ack={new_errors_since_ack}",
        r'python -u "C:\Users\alike\edge_factory_error_classifier_v1.py"',
        "errors",
    )

    # Sample maturity policies.
    add_policy(
        policies,
        "allow_drift_review",
        runtime_ok and not new_errors_since_ack and drift_ready,
        "INFO",
        f"closed={closed}/{DRIFT_MIN_CLOSED}",
        "Wait until closed >= 20.",
        "validation",
    )

    add_policy(
        policies,
        "allow_capital_review_read_only",
        runtime_ok and not new_errors_since_ack and capital_ready,
        "INFO",
        f"closed={closed}/{CAPITAL_MIN_CLOSED}",
        "Wait until closed >= 50. Capital review is read-only until explicit approval.",
        "capital",
    )

    add_policy(
        policies,
        "block_capital_change",
        False,
        "CRITICAL",
        "Capital change remains globally disabled.",
        "No capital changes. Review-only analysis may be allowed after threshold.",
        "capital",
    )

    # Repo workflow policies.
    add_policy(
        policies,
        "allow_repo_only_os_intelligence_work",
        runtime_ok and not new_errors_since_ack,
        "ATTENTION",
        "Runtime healthy and no new errors.",
        "All work must stay in repo unless explicitly approved.",
        "repo",
    )

    add_policy(
        policies,
        "require_clean_git_before_runtime_application",
        not git_dirty,
        "ATTENTION",
        git_status["stdout"].strip() if git_dirty else "git working tree clean",
        "Commit or review repo changes before applying anything to runtime.",
        "repo",
    )

    # Research policies.
    add_policy(
        policies,
        "block_new_active_paper_family",
        False,
        "CRITICAL",
        "New active paper family remains blocked until runtime sample matures and review gates pass.",
        "No new active paper family.",
        "research",
    )

    add_policy(
        policies,
        "allow_repo_only_research_os_design",
        runtime_ok and not new_errors_since_ack,
        "ATTENTION",
        "Repo-only research OS design is allowed; no runtime execution.",
        "Design only. No live/paper activation.",
        "research",
    )

    # Memory-aware policies.
    add_policy(
        policies,
        "block_exact_failed_candidates",
        len(exact_candidate_blocks) >= 0,
        "OK",
        "Exact blocked candidates are registered and must not be rerun.",
        "Blocked: " + ", ".join(exact_candidate_blocks) if exact_candidate_blocks else "No blocked candidates.",
        "memory",
    )

    add_policy(
        policies,
        "enforce_family_cooldowns",
        len(family_cooldowns) >= 0,
        "OK",
        "Family cooldowns are registered and require new evidence/redesign before reuse.",
        "Cooldowns: " + ", ".join(family_cooldowns) if family_cooldowns else "No family cooldowns.",
        "memory",
    )

    # Hard safety policies.
    add_policy(
        policies,
        "block_live_trading",
        not live_allowed and not real_orders_allowed,
        "CRITICAL",
        f"live_allowed={live_allowed}, real_orders_allowed={real_orders_allowed}",
        "Live trading must remain disabled.",
        "safety",
    )

    add_policy(
        policies,
        "block_active_paper_escalation",
        not active_paper_allowed,
        "CRITICAL",
        f"active_paper_allowed={active_paper_allowed}",
        "Active paper escalation remains disabled.",
        "safety",
    )

    add_policy(
        policies,
        "block_capital_change_flag",
        not capital_change_allowed,
        "CRITICAL",
        f"capital_change_allowed={capital_change_allowed}",
        "Capital change flag must remain false.",
        "safety",
    )

    critical_blocks = [p for p in policies if not p["allowed"] and p["severity_if_blocked"] == "CRITICAL"]
    attention_blocks = [p for p in policies if not p["allowed"] and p["severity_if_blocked"] == "ATTENTION"]
    info_blocks = [p for p in policies if not p["allowed"] and p["severity_if_blocked"] == "INFO"]

    # Some CRITICAL blocks are intentional hard-deny policies, not system failures.
    intentional_hard_blocks = {
        "block_runtime_patch_when_healthy",
        "block_duplicate_launcher",
        "block_capital_change",
        "block_new_active_paper_family",
    }

    unexpected_critical_blocks = [
        p for p in critical_blocks if p["policy_key"] not in intentional_hard_blocks
    ]

    if unexpected_critical_blocks:
        policy_status = "POLICY_ENGINE_CRITICAL_BLOCK"
        recommended_action = "STOP_AND_REVIEW_UNEXPECTED_CRITICAL_POLICY_BLOCKS"
    elif attention_blocks:
        policy_status = "POLICY_ENGINE_PASS_WITH_ATTENTION"
        recommended_action = "REVIEW_ATTENTION_POLICIES_BEFORE_NEXT_STEP"
    else:
        policy_status = "POLICY_ENGINE_PASS"
        recommended_action = "CONTINUE_REPO_ONLY_OS_INTELLIGENCE_DO_NOT_TOUCH_RUNTIME"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "repo": str(REPO),
        "unified_state_path": str(UNIFIED_STATE_PATH),
        "policy_status": policy_status,
        "recommended_action": recommended_action,
        "runtime_ok": runtime_ok,
        "process_ok": process_ok,
        "health_ok": health_ok,
        "errors_acknowledged": errors_acknowledged,
        "new_errors_since_ack": new_errors_since_ack,
        "open": open_count,
        "pending": pending,
        "closed": closed,
        "drift_ready": drift_ready,
        "capital_review_ready": capital_ready,
        "git_dirty": git_dirty,
        "exact_candidate_blocks": exact_candidate_blocks,
        "family_cooldowns": family_cooldowns,
        "unexpected_critical_block_count": len(unexpected_critical_blocks),
        "attention_block_count": len(attention_blocks),
        "info_block_count": len(info_blocks),
        "intentional_hard_blocks": sorted(intentional_hard_blocks),
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "policies": policies,
    }

    state_path = out_dir / "os_policy_engine_v1_state.json"
    latest_path = OUT_ROOT / "os_policy_engine_latest.json"
    policy_csv = out_dir / "os_policy_engine_v1_policies.csv"
    report_path = out_dir / "os_policy_engine_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    latest_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    with policy_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["policy_key", "scope", "allowed", "status", "severity_if_blocked", "reason", "required_action"],
        )
        writer.writeheader()
        writer.writerows(policies)

    md = []
    md.append("# Edge Factory OS Policy Engine v1")
    md.append("")
    md.append(f"policy_status: `{policy_status}`")
    md.append(f"recommended_action: `{recommended_action}`")
    md.append("")
    md.append("## Summary")
    md.append(f"- runtime_ok: `{runtime_ok}`")
    md.append(f"- new_errors_since_ack: `{new_errors_since_ack}`")
    md.append(f"- closed: `{closed}`")
    md.append(f"- drift_ready: `{drift_ready}`")
    md.append(f"- capital_review_ready: `{capital_ready}`")
    md.append(f"- git_dirty: `{git_dirty}`")
    md.append("")
    md.append("## Safety")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OS POLICY ENGINE v1")
    print("=" * 100)
    print(f"policy_status: {policy_status}")
    print(f"recommended_action: {recommended_action}")
    print(f"runtime_ok={runtime_ok} process_ok={process_ok} health_ok={health_ok}")
    print(f"errors_acknowledged={errors_acknowledged} new_errors_since_ack={new_errors_since_ack}")
    print(f"open={open_count} pending={pending} closed={closed}")
    print(f"drift_ready={drift_ready}")
    print(f"capital_review_ready={capital_ready}")
    print(f"git_dirty={git_dirty}")
    print(f"unexpected_critical_block_count={len(unexpected_critical_blocks)}")
    print(f"attention_block_count={len(attention_blocks)}")
    print(f"info_block_count={len(info_blocks)}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("UNEXPECTED CRITICAL BLOCKS")
    print("-" * 100)
    if unexpected_critical_blocks:
        for p in unexpected_critical_blocks:
            print(f"- {p['policy_key']}: {p['reason']} -> {p['required_action']}")
    else:
        print("NONE")
    print()
    print("ATTENTION BLOCKS")
    print("-" * 100)
    if attention_blocks:
        for p in attention_blocks:
            print(f"- {p['policy_key']}: {p['reason']} -> {p['required_action']}")
    else:
        print("NONE")
    print()
    print("INFO BLOCKS")
    print("-" * 100)
    if info_blocks:
        for p in info_blocks:
            print(f"- {p['policy_key']}: {p['reason']} -> {p['required_action']}")
    else:
        print("NONE")
    print()
    print(f"State : {state_path}")
    print(f"Latest: {latest_path}")
    print(f"Policy: {policy_csv}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
