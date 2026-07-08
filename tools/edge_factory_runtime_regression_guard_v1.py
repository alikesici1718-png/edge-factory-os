#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUNTIME = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
REPO = WORKSPACE / "edge_factory_os_repo"

OUT_ROOT = WORKSPACE / "edge_factory_runtime_regression_guard_v1"

RISK_MANAGER = USERDIR / "global_paper_risk_manager_v3_priority.py"

LOGGERS = [
    USERDIR / "old_short_gate_aware_live_paper_logger.py",
    USERDIR / "impulse_long_gate_aware_live_paper_logger.py",
    USERDIR / "market_relative_live_paper_logger.py",
    USERDIR / "weak_market_breakdown_short_live_paper_logger.py",
]

V5_LAUNCHER = USERDIR / "start_edge_factory_MASTER_UPPER_SYSTEM_v5_supervised.ps1"

V5_LOG_DIR = RUNTIME / "startup_logs_v5_supervised"

EXPECTED_PROCESS_PATTERNS = {
    "risk_manager": ["global_paper_risk_manager_v4_config.py", "global_paper_risk_manager_v3_priority.py"],
    "old_short_logger": ["old_short_gate_aware_live_paper_logger.py"],
    "impulse_long_logger": ["impulse_long_gate_aware_live_paper_logger.py"],
    "market_relative_logger": ["market_relative_live_paper_logger.py"],
    "weak_market_logger": ["weak_market_breakdown_short_live_paper_logger.py"],
    "autopilot_v4": ["edge_factory_os_autopilot_loop_v4.py"],
}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def latest_json(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    files = list(root.rglob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

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

def add_check(rows: list[dict], name: str, passed: bool, severity: str, evidence: str) -> None:
    rows.append({
        "check": name,
        "passed": bool(passed),
        "severity": "OK" if passed else severity,
        "evidence": evidence,
    })

def get_process_snapshot() -> str:
    ps = r"""
Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -match 'python|powershell' -and
    $_.CommandLine -match 'startup_runners_v5|global_paper_risk|gate_aware|market_relative|weak_market|autopilot_loop_v4'
} |
Select-Object ProcessId, Name, CommandLine |
Format-List
"""
    r = run(["powershell", "-NoProfile", "-Command", ps], timeout=30)
    return (r["stdout"] or "") + "\nSTDERR:\n" + (r["stderr"] or "")

def main() -> int:
    out_dir = OUT_ROOT / f"runtime_regression_guard_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []

    overlay_path = WORKSPACE / "edge_factory_os_command_center_v2_overlay" / "os_command_center_v2_overlay_latest.json"
    overlay = read_json(overlay_path)

    add_check(
        rows,
        "overlay_runtime_ok",
        overlay.get("runtime_ok") is True,
        "CRITICAL",
        f"path={overlay_path}; runtime_ok={overlay.get('runtime_ok')}; overlay_status={overlay.get('overlay_status')}",
    )

    add_check(
        rows,
        "overlay_next_action_do_not_touch",
        overlay.get("next_action") == "KEEP_RUNNING_COLLECT_SAMPLE_DO_NOT_TOUCH",
        "ATTENTION",
        f"next_action={overlay.get('next_action')}",
    )

    add_check(
        rows,
        "overlay_no_live_or_capital",
        overlay.get("live_allowed") is False and overlay.get("capital_change_allowed") is False,
        "CRITICAL",
        f"live_allowed={overlay.get('live_allowed')}; capital_change_allowed={overlay.get('capital_change_allowed')}",
    )

    ack_path = WORKSPACE / "edge_factory_error_acknowledger_v1" / "error_acknowledger_latest.json"
    ack = read_json(ack_path)

    add_check(
        rows,
        "error_acknowledger_clean",
        ack.get("acknowledged") is True
        and ack.get("logic_or_safety_error_count", 999) == 0
        and ack.get("unknown_error_count", 999) == 0,
        "CRITICAL",
        f"acknowledged={ack.get('acknowledged')}; logic={ack.get('logic_or_safety_error_count')}; unknown={ack.get('unknown_error_count')}",
    )

    risk_txt = read_text(RISK_MANAGER)
    add_check(
        rows,
        "risk_manager_signal_id_canonical_marker",
        "EDGE_FACTORY_CANONICAL_SIGNAL_ID_FALLBACK_V1" in risk_txt,
        "CRITICAL",
        str(RISK_MANAGER),
    )

    for logger in LOGGERS:
        txt = read_text(logger)
        add_check(
            rows,
            f"logger_require_global_gate_default_marker:{logger.name}",
            "EDGE_FACTORY_REQUIRE_GLOBAL_GATE_DEFAULT_TRUE_V1" in txt,
            "CRITICAL",
            str(logger),
        )
        add_check(
            rows,
            f"logger_no_global_gate_escape_exists:{logger.name}",
            "--no_global_gate" in txt,
            "ATTENTION",
            str(logger),
        )

    launcher_txt = read_text(V5_LAUNCHER)
    add_check(
        rows,
        "v5_supervised_launcher_exists",
        V5_LAUNCHER.exists(),
        "CRITICAL",
        str(V5_LAUNCHER),
    )
    add_check(
        rows,
        "v5_supervised_launcher_has_runner_loop",
        "while (`$true)" in launcher_txt or "while ($true)" in launcher_txt,
        "CRITICAL",
        "supervised restart loop marker",
    )
    add_check(
        rows,
        "v5_supervised_launcher_passes_require_global_gate",
        "--require_global_gate" in launcher_txt,
        "CRITICAL",
        "launcher must pass require_global_gate",
    )
    add_check(
        rows,
        "v5_supervised_launcher_passes_sizing_contract",
        "--sizing_contract" in launcher_txt,
        "CRITICAL",
        "launcher must pass sizing contract",
    )

    process_snapshot = get_process_snapshot()
    for component, patterns in EXPECTED_PROCESS_PATTERNS.items():
        found = any(p in process_snapshot for p in patterns)
        add_check(
            rows,
            f"process_running:{component}",
            found,
            "CRITICAL",
            " | ".join(patterns),
        )

    exception_hits = []
    if V5_LOG_DIR.exists():
        for p in sorted(V5_LOG_DIR.glob("*.combined.log")):
            txt = read_text(p)
            for line in txt.splitlines():
                if "EXCEPTION" in line or "ExitCode=999" in line:
                    exception_hits.append(f"{p.name}: {line}")
    add_check(
        rows,
        "v5_logs_no_exception_or_999",
        len(exception_hits) == 0,
        "CRITICAL",
        "\n".join(exception_hits[-20:]) if exception_hits else "no EXCEPTION / ExitCode=999 found",
    )

    exited_hits = []
    if V5_LOG_DIR.exists():
        for p in sorted(V5_LOG_DIR.glob("*.combined.log")):
            txt = read_text(p)
            for line in txt.splitlines():
                if "PROCESS EXITED" in line:
                    exited_hits.append(f"{p.name}: {line}")
    add_check(
        rows,
        "v5_logs_no_process_exited",
        len(exited_hits) == 0,
        "ATTENTION",
        "\n".join(exited_hits[-20:]) if exited_hits else "no PROCESS EXITED found",
    )

    git_status = run(["git", "status", "--short"], cwd=REPO)
    add_check(
        rows,
        "git_working_tree_clean",
        git_status["ok"] and git_status["stdout"].strip() == "",
        "ATTENTION",
        git_status["stdout"].strip() or "clean",
    )

    critical_failed = sum(1 for r in rows if not r["passed"] and r["severity"] == "CRITICAL")
    attention_failed = sum(1 for r in rows if not r["passed"] and r["severity"] == "ATTENTION")

    if critical_failed:
        status = "REGRESSION_GUARD_FAIL_CRITICAL"
        next_action = "DO_NOT_PATCH_RUNTIME_FIX_REPO_FIRST"
    elif attention_failed:
        status = "REGRESSION_GUARD_PASS_WITH_ATTENTION"
        next_action = "REVIEW_ATTENTION_BEFORE_RUNTIME_CHANGE"
    else:
        status = "REGRESSION_GUARD_PASS"
        next_action = "SAFE_TO_CONTINUE_REPO_ONLY_WORK"

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "runtime": str(RUNTIME),
        "repo": str(REPO),
        "status": status,
        "critical_failed": critical_failed,
        "attention_failed": attention_failed,
        "next_action": next_action,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "checks": rows,
    }

    state_path = out_dir / "runtime_regression_guard_v1_state.json"
    csv_path = out_dir / "runtime_regression_guard_v1_checks.csv"
    process_path = out_dir / "process_snapshot.txt"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    process_path.write_text(process_snapshot, encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "passed", "severity", "evidence"])
        writer.writeheader()
        writer.writerows(rows)

    print("EDGE FACTORY RUNTIME REGRESSION GUARD v1")
    print("=" * 100)
    print(f"status: {status}")
    print(f"critical_failed: {critical_failed}")
    print(f"attention_failed: {attention_failed}")
    print(f"next_action: {next_action}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("FAILED CHECKS")
    print("-" * 100)
    failed = [r for r in rows if not r["passed"]]
    if not failed:
        print("NONE")
    else:
        for r in failed:
            print(f"[{r['severity']}] {r['check']} -> {r['evidence']}")
    print()
    print(f"State  : {state_path}")
    print(f"Checks : {csv_path}")
    print(f"Process: {process_path}")

if __name__ == "__main__":
    main()
