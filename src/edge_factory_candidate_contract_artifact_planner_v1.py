#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_candidate_contract_artifact_planner_v1"

def latest_contract() -> Path | None:
    root = WORKSPACE / "edge_factory_candidate_contract_generator_v1"
    files = list(root.rglob("*_offline_experiment_contract_v1.json"))
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

def safe_key(x: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in str(x)).strip("_") or "unknown_candidate"

def main() -> int:
    ap = argparse.ArgumentParser(description="Fill artifact output paths for a candidate offline experiment contract.")
    ap.add_argument("--contract", default="")
    args = ap.parse_args()

    source_contract = Path(args.contract) if args.contract else latest_contract()

    out_dir = OUT_ROOT / f"artifact_planner_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    contract = read_json(source_contract)

    blockers = []
    if not source_contract or not source_contract.exists():
        blockers.append("SOURCE_CONTRACT_NOT_FOUND")
    if "__read_error__" in contract:
        blockers.append("SOURCE_CONTRACT_READ_ERROR")

    identity = contract.get("identity", {}) if isinstance(contract.get("identity"), dict) else {}
    candidate_key = safe_key(identity.get("candidate_key", "unknown_candidate"))
    family_key = safe_key(identity.get("family_key", "unknown_family"))

    candidate_output_root = WORKSPACE / "edge_factory_offline_runner_outputs" / candidate_key
    candidate_output_root.mkdir(parents=True, exist_ok=True)

    completed_contract_path = None

    if not blockers:
        contract["artifact_outputs"] = {
            "normalized_trades_csv": str(candidate_output_root / f"{candidate_key}_normalized_trades.csv"),
            "summary_csv": str(candidate_output_root / f"{candidate_key}_summary.csv"),
            "state_json": str(candidate_output_root / f"{candidate_key}_result_state.json"),
            "audit_csv": str(candidate_output_root / f"{candidate_key}_audit.csv"),
            "ledger_entry": str(candidate_output_root / f"{candidate_key}_ledger_entry.jsonl")
        }

        contract.setdefault("metadata", {})
        contract["metadata"]["artifact_planner_v1_completed_at"] = datetime.now(timezone.utc).isoformat()
        contract["metadata"]["source_contract"] = str(source_contract)
        contract["metadata"]["offline_output_root"] = str(candidate_output_root)

        completed_dir = out_dir / candidate_key
        completed_dir.mkdir(parents=True, exist_ok=True)
        completed_contract_path = completed_dir / f"{candidate_key}_offline_experiment_contract_v1_completed.json"
        completed_contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "planner_status": "ARTIFACT_OUTPUTS_FILLED" if not blockers else "ARTIFACT_PLANNER_BLOCKED",
        "source_contract": str(source_contract) if source_contract else None,
        "completed_contract": str(completed_contract_path) if completed_contract_path else "",
        "candidate_key": candidate_key,
        "family_key": family_key,
        "offline_output_root": str(candidate_output_root),
        "blockers": blockers,
        "validator_command": (
            f'python -u "C:\\Users\\alike\\edge_factory_offline_experiment_contract_validator_v1.py" --contract "{completed_contract_path}"'
            if completed_contract_path else ""
        ),
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Planner only fills artifact output paths.",
            "Does not run offline tests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not promote candidates.",
            "Does not place orders."
        ]
    }

    state_path = out_dir / "candidate_contract_artifact_planner_v1_state.json"
    report_path = out_dir / "candidate_contract_artifact_planner_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    report = []
    report.append("# Edge Factory Candidate Contract Artifact Planner v1")
    report.append("")
    report.append(f"Status: `{state['planner_status']}`")
    report.append(f"Candidate: `{candidate_key}`")
    report.append(f"Source contract: `{source_contract}`")
    report.append(f"Completed contract: `{completed_contract_path}`")
    report.append("")
    if state["validator_command"]:
        report.append("## Next validation command")
        report.append("```powershell")
        report.append(state["validator_command"])
        report.append("```")
    report.append("")
    report.append("## Safety")
    report.append("- live_allowed: `False`")
    report.append("- active_paper_allowed: `False`")
    report.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("EDGE FACTORY CANDIDATE CONTRACT ARTIFACT PLANNER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"planner_status: {state['planner_status']}")
    print(f"source_contract   : {source_contract}")
    print(f"completed_contract: {completed_contract_path}")
    print(f"candidate_key     : {candidate_key}")
    print(f"offline_output_root: {candidate_output_root}")
    print(f"blockers: {blockers}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    if state["validator_command"]:
        print("NEXT VALIDATION COMMAND")
        print("-" * 100)
        print(state["validator_command"])
    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
