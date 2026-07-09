#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adapts a validated offline experiment contract into a safe offline runner request by reading the latest contract validator state and contract JSON. Checks validation status and gate conditions, then writes a runner request JSON with resolved data source bindings if all blockers are cleared.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_contract_to_runner_adapter_v1"

def latest_dir(root: Path, prefix: str) -> Path | None:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    if not ds:
        return None
    return sorted(ds, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def nested_get(obj: dict[str, Any], dotted: str, default=None):
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def main() -> int:
    ap = argparse.ArgumentParser(description="Convert valid offline experiment contract to safe offline runner request.")
    ap.add_argument("--contract", default="", help="Optional contract path. Defaults to latest validated contract.")
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"contract_to_runner_adapter_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    validator_dir = latest_dir(WORKSPACE / "edge_factory_offline_experiment_contract_validator_v1", "contract_validator_v1_")
    validator_state_path = validator_dir / "offline_experiment_contract_validator_v1_state.json" if validator_dir else None
    validator = read_json(validator_state_path)

    contract_path = Path(args.contract) if args.contract else Path(str(validator.get("contract_path", "")))
    contract = read_json(contract_path)

    validation_status = validator.get("validation_status", "UNKNOWN")
    is_template = bool(validator.get("is_template", False))
    critical_failed = int(validator.get("critical_failed_count") or 0)
    attention_failed = int(validator.get("attention_failed_count") or 0)

    blockers = []
    reasons = []

    if not contract_path.exists():
        blockers.append("CONTRACT_PATH_MISSING")
    if validation_status != "CONTRACT_VALID_READY_FOR_OFFLINE_TESTING":
        blockers.append(f"VALIDATION_STATUS_NOT_RUNNER_READY:{validation_status}")
    if is_template:
        blockers.append("TEMPLATE_NOT_A_CANDIDATE")
    if critical_failed > 0:
        blockers.append(f"CRITICAL_VALIDATION_FAILURES:{critical_failed}")
    if attention_failed > 0:
        reasons.append(f"attention_fields_present:{attention_failed}")

    identity = contract.get("identity", {}) if isinstance(contract.get("identity"), dict) else {}
    candidate_key = identity.get("candidate_key", "")
    family_key = identity.get("family_key", "")
    side = identity.get("side", "")

    runner_request = None

    if blockers:
        adapter_status = "ADAPTER_BLOCKED_NO_RUNNER_REQUEST"
    else:
        adapter_status = "ADAPTER_RUNNER_REQUEST_READY"
        cost_model = contract.get("cost_model", {})
        total_cost_bps = cost_model.get("total_cost_bps")

        runner_request = {
            "request_version": "edge_factory_offline_runner_request_v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "candidate_key": candidate_key,
            "family_key": family_key,
            "side": side,
            "mode": "offline_backtest",
            "universe": nested_get(contract, "data_contract.universe"),
            "timeframe": nested_get(contract, "data_contract.timeframe"),
            "source_files": nested_get(contract, "data_contract.source_files", []),
            "required_columns": nested_get(contract, "data_contract.required_columns", []),
            "entry_rule": nested_get(contract, "signal_contract.entry_rule"),
            "exit_rule": nested_get(contract, "signal_contract.exit_rule"),
            "hold_time": nested_get(contract, "signal_contract.hold_time"),
            "cooldown": nested_get(contract, "signal_contract.cooldown"),
            "cost_bps": total_cost_bps,
            "validation_plan": contract.get("validation_plan", {}),
            "promotion_gates": contract.get("promotion_gates", {}),
            "output_dir": str(WORKSPACE / "edge_factory_offline_runner_outputs" / str(candidate_key)),
            "no_master_touch": True,
            "live_allowed": False,
            "active_paper_allowed": False,
            "capital_change_allowed": False,
        }

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "adapter_status": adapter_status,
        "validator_state_path": str(validator_state_path) if validator_state_path else None,
        "contract_path": str(contract_path),
        "validation_status": validation_status,
        "is_template": is_template,
        "critical_failed": critical_failed,
        "attention_failed": attention_failed,
        "candidate_key": candidate_key,
        "family_key": family_key,
        "side": side,
        "blockers": blockers,
        "reasons": reasons,
        "runner_request": runner_request,
        "runner_request_path": "",
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Adapter does not run experiments.",
            "Adapter does not touch MASTER_UPPER_SYSTEM.",
            "Adapter does not start processes.",
            "Adapter does not place orders.",
            "Adapter only emits runner_request.json if contract is valid and not template.",
        ],
    }

    state_path = out_dir / "contract_to_runner_adapter_v1_state.json"
    runner_path = out_dir / "offline_runner_request_v1.json"
    report_path = out_dir / "contract_to_runner_adapter_v1_report.md"

    if runner_request is not None:
        runner_path.write_text(json.dumps(runner_request, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        state["runner_request_path"] = str(runner_path)

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Contract-to-Runner Adapter v1")
    md.append("")
    md.append(f"Status: `{adapter_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Validation: `{validation_status}`")
    md.append(f"Is template: `{is_template}`")
    md.append("")
    md.append("## Blockers")
    if blockers:
        for b in blockers:
            md.append(f"- `{b}`")
    else:
        md.append("- None")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY CONTRACT TO RUNNER ADAPTER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"adapter_status: {adapter_status}")
    print(f"contract  : {contract_path}")
    print(f"validation_status: {validation_status}")
    print(f"is_template: {is_template}")
    print(f"candidate : {candidate_key}")
    print(f"blockers  : {blockers}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print(f"State : {state_path}")
    print(f"Report: {report_path}")
    if runner_request is not None:
        print(f"RunnerRequest: {runner_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
