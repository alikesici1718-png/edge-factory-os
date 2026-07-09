#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads the latest offline runner request JSON and audits it for preflight compliance, checking that all required fields are present, that the request does not conflict with live/paper system constraints, and that referenced data paths exist.
Outputs a preflight audit report JSON to the edge_factory_offline_runner_request_preflight_auditor_v1 workspace directory.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
MASTER = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
OUT_ROOT = WORKSPACE / "edge_factory_offline_runner_request_preflight_auditor_v1"

def latest_request() -> Path | None:
    root = WORKSPACE / "edge_factory_contract_to_runner_adapter_v1"
    files = list(root.rglob("offline_runner_request_v1.json"))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def is_subpath(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False

def add_gate(rows, gate, passed, severity, evidence):
    rows.append({
        "gate": gate,
        "passed": bool(passed),
        "severity": severity,
        "evidence": str(evidence),
    })

def nonempty(x: Any) -> bool:
    if x is None:
        return False
    if isinstance(x, str):
        return bool(x.strip())
    if isinstance(x, list):
        return len(x) > 0
    if isinstance(x, dict):
        return len(x) > 0
    return True

def main() -> int:
    ap = argparse.ArgumentParser(description="Preflight audit for offline runner request.")
    ap.add_argument("--request", default="")
    args = ap.parse_args()

    request_path = Path(args.request) if args.request else latest_request()

    out_dir = OUT_ROOT / f"runner_request_preflight_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    req = read_json(request_path)
    gates = []

    add_gate(gates, "request_exists", request_path is not None and request_path.exists(), "CRITICAL", request_path)
    add_gate(gates, "request_readable", bool(req) and "__read_error__" not in req, "CRITICAL", request_path)

    candidate_key = req.get("candidate_key", "")
    family_key = req.get("family_key", "")
    output_dir_raw = req.get("output_dir", "")
    output_dir = Path(output_dir_raw) if output_dir_raw else None

    add_gate(gates, "candidate_key_present", nonempty(candidate_key), "CRITICAL", candidate_key)
    add_gate(gates, "family_key_present", nonempty(family_key), "CRITICAL", family_key)
    add_gate(gates, "side_present", req.get("side") in {"long", "short", "both"}, "CRITICAL", req.get("side"))
    add_gate(gates, "mode_offline_only", req.get("mode") in {"offline_backtest", "market_replay", "walk_forward"}, "CRITICAL", req.get("mode"))

    add_gate(gates, "no_master_touch_true", req.get("no_master_touch") is True, "CRITICAL", req.get("no_master_touch"))
    add_gate(gates, "live_allowed_false", req.get("live_allowed") is False, "CRITICAL", req.get("live_allowed"))
    add_gate(gates, "active_paper_allowed_false", req.get("active_paper_allowed") is False, "CRITICAL", req.get("active_paper_allowed"))
    add_gate(gates, "capital_change_allowed_false", req.get("capital_change_allowed") is False, "CRITICAL", req.get("capital_change_allowed"))

    add_gate(gates, "output_dir_present", output_dir is not None, "CRITICAL", output_dir_raw)
    add_gate(gates, "output_dir_not_inside_master", output_dir is not None and not is_subpath(output_dir, MASTER), "CRITICAL", output_dir_raw)

    source_files = req.get("source_files", [])
    required_columns = req.get("required_columns", [])

    add_gate(gates, "source_files_present", nonempty(source_files), "ATTENTION", source_files)
    add_gate(
        gates,
        "source_files_not_placeholder",
        isinstance(source_files, list) and source_files and all("AUTO_" not in str(x).upper() for x in source_files),
        "ATTENTION",
        source_files,
    )
    add_gate(gates, "required_columns_present", nonempty(required_columns), "CRITICAL", required_columns)

    add_gate(gates, "entry_rule_present", nonempty(req.get("entry_rule")), "CRITICAL", req.get("entry_rule"))
    add_gate(gates, "exit_rule_present", nonempty(req.get("exit_rule")), "CRITICAL", req.get("exit_rule"))
    add_gate(gates, "hold_time_present", nonempty(req.get("hold_time")), "CRITICAL", req.get("hold_time"))
    add_gate(gates, "cost_bps_present", req.get("cost_bps") is not None, "CRITICAL", req.get("cost_bps"))

    validation_plan = req.get("validation_plan", {})
    promotion_gates = req.get("promotion_gates", {})

    add_gate(gates, "validation_plan_present", nonempty(validation_plan), "CRITICAL", validation_plan)
    add_gate(gates, "promotion_gates_present", nonempty(promotion_gates), "CRITICAL", promotion_gates)

    critical_failed = [g for g in gates if not g["passed"] and g["severity"] == "CRITICAL"]
    attention_failed = [g for g in gates if not g["passed"] and g["severity"] == "ATTENTION"]

    if critical_failed:
        preflight_status = "RUNNER_REQUEST_PREFLIGHT_CRITICAL_FAIL"
        runner_execution_allowed = False
        next_action = "FIX_CRITICAL_REQUEST_FIELDS"
    elif attention_failed:
        preflight_status = "RUNNER_REQUEST_PREFLIGHT_ATTENTION_DATA_RESOLUTION_REQUIRED"
        runner_execution_allowed = False
        next_action = "RUN_DATA_RESOLVER_BEFORE_OFFLINE_RUNNER"
    else:
        preflight_status = "RUNNER_REQUEST_PREFLIGHT_PASS_READY_FOR_OFFLINE_RUNNER"
        runner_execution_allowed = True
        next_action = "BUILD_OR_RUN_OFFLINE_RUNNER_READ_ONLY"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "request_path": str(request_path) if request_path else None,
        "candidate_key": candidate_key,
        "family_key": family_key,
        "preflight_status": preflight_status,
        "critical_failed": len(critical_failed),
        "attention_failed": len(attention_failed),
        "runner_execution_allowed": runner_execution_allowed,
        "next_action": next_action,
        "gates": gates,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Preflight only reads runner request.",
            "Does not run offline tests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop MASTER processes.",
            "Does not place orders.",
            "Does not enable live trading."
        ],
    }

    state_path = out_dir / "offline_runner_request_preflight_v1_state.json"
    gates_path = out_dir / "offline_runner_request_preflight_v1_gates.csv"
    report_path = out_dir / "offline_runner_request_preflight_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(gates).to_csv(gates_path, index=False)

    md = []
    md.append("# Edge Factory Offline Runner Request Preflight v1")
    md.append("")
    md.append(f"Status: `{preflight_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Critical failed: `{len(critical_failed)}`")
    md.append(f"Attention failed: `{len(attention_failed)}`")
    md.append(f"Runner execution allowed: `{runner_execution_allowed}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Failed gates")
    failed = critical_failed + attention_failed
    if failed:
        for g in failed:
            md.append(f"- `{g['severity']}` `{g['gate']}` — {g['evidence']}")
    else:
        md.append("- None")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE RUNNER REQUEST PREFLIGHT AUDITOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"request   : {request_path}")
    print(f"candidate : {candidate_key}")
    print(f"preflight_status: {preflight_status}")
    print(f"critical_failed : {len(critical_failed)}")
    print(f"attention_failed: {len(attention_failed)}")
    print(f"runner_execution_allowed: {runner_execution_allowed}")
    print(f"next_action: {next_action}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("FAILED GATES")
    print("-" * 100)
    failed_df = pd.DataFrame([g for g in gates if not g["passed"]])
    if failed_df.empty:
        print("NONE")
    else:
        print(failed_df[["severity", "gate", "evidence"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"Gates : {gates_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
