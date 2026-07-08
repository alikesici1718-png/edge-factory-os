#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def not_expired(expires_at: Any) -> bool:
    if not expires_at:
        return False
    try:
        dt = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        return now <= dt
    except Exception:
        return False

def latest_granted_approval_record(ws: Path) -> Optional[Path]:
    root = ws / "edge_factory_ret60_manual_shadow_approval_recorder"
    ledger = root / "master_ret60_manual_shadow_approval_ledger.jsonl"

    if ledger.exists():
        rows = []
        for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

        granted = [
            r for r in rows
            if r.get("manual_approval_granted") is True
            and r.get("shadow_start_allowed_by_approval_record") is True
            and r.get("live_allowed") is False
            and r.get("active_paper_allowed") is False
        ]

        if granted:
            latest = granted[-1]
            rp = latest.get("record_path")
            if rp and Path(rp).exists():
                return Path(rp)

    d = latest_dir(root, "ret60_manual_approval_")
    if not d:
        return None
    p = d / "ret60_manual_shadow_approval_record.json"
    return p if p.exists() else None

def main() -> int:
    ws = WORKSPACE
    out_dir = ws / "edge_factory_ret60_shadow_start_gate_v2" / f"ret60_shadow_start_gate_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pf_dir = latest_dir(ws / "edge_factory_ret60_sandbox_preflight_gate_v2", "ret60_sandbox_preflight_v2_")
    pf_path = pf_dir / "ret60_sandbox_preflight_v2_state.json" if pf_dir else None
    preflight = read_json(pf_path)

    approval_path = latest_granted_approval_record(ws)
    approval_record = read_json(approval_path)
    approval_state = approval_record.get("state", {})

    runtime_plan = preflight.get("runtime_plan", {})
    engine_path = runtime_plan.get("runtime_engine_path")
    sandbox_root = runtime_plan.get("sandbox_root")

    engine_text = ""
    if engine_path and Path(engine_path).exists():
        engine_text = Path(engine_path).read_text(encoding="utf-8", errors="replace")

    gates = []

    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("preflight_v2_exists", bool(pf_path and pf_path.exists()), pf_path)
    gate("preflight_v2_passed", preflight.get("preflight_passed") is True, preflight.get("preflight_status"))
    gate("ready_for_shadow_start_gate", preflight.get("ready_for_shadow_start_gate") is True, preflight.get("ready_for_shadow_start_gate"))
    gate("preflight_v2_not_expired", not_expired(preflight.get("expires_at")), preflight.get("expires_at"))

    gate("approval_record_exists", bool(approval_path and approval_path.exists()), approval_path)
    gate("manual_approval_granted", approval_state.get("manual_approval_granted") is True, approval_state.get("manual_approval_granted"))
    gate("approval_allows_shadow_reference", approval_state.get("shadow_start_allowed_by_approval_record") is True, approval_state.get("shadow_start_allowed_by_approval_record"))
    gate("approval_not_expired", not_expired(approval_state.get("expires_at")), approval_state.get("expires_at"))

    gate("engine_path_defined", bool(engine_path), engine_path)
    gate("engine_file_exists", bool(engine_path and Path(engine_path).exists()), engine_path)
    gate("sandbox_root_defined", bool(sandbox_root), sandbox_root)

    gate("engine_has_shadow_runtime_entrypoint", "--shadow_runtime" in engine_text, "")
    gate("engine_has_self_test_entrypoint", "--self_test" in engine_text, "")
    gate("engine_has_heartbeat_writer", "heartbeat_writer" in engine_text and "ret60_shadow_heartbeat.json" in engine_text, "")
    gate("engine_has_native_log_writer", "ret60_shadow_native_events.csv" in engine_text, "")
    gate("engine_has_closed_trade_writer", "ret60_shadow_closed_trades.csv" in engine_text, "")
    gate("engine_blocks_live", "LIVE_ALLOWED = False" in engine_text, "")
    gate("engine_blocks_active_paper", "ACTIVE_PAPER_ALLOWED = False" in engine_text, "")

    gate("preflight_live_blocked", preflight.get("live_allowed") is False, preflight.get("live_allowed"))
    gate("preflight_active_paper_blocked", preflight.get("active_paper_allowed") is False, preflight.get("active_paper_allowed"))
    gate("preflight_shadow_start_currently_blocked", preflight.get("shadow_start_allowed") is False, preflight.get("shadow_start_allowed"))
    gate("approval_live_blocked", approval_state.get("live_allowed") is False, approval_state.get("live_allowed"))
    gate("approval_active_paper_blocked", approval_state.get("active_paper_allowed") is False, approval_state.get("active_paper_allowed"))

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)
    all_ok = passed == total

    if all_ok:
        decision_status = "RET60_SHADOW_START_REFERENCE_READY_NOT_EXECUTED"
        start_reference_allowed = True
        next_action = "OPTIONALLY_RUN_SUPERVISED_RET60_SHADOW_SELF_TEST_OR_FILE_REPLAY"
    else:
        decision_status = "RET60_SHADOW_START_GATE_V2_BLOCKED"
        start_reference_allowed = False
        next_action = "REPAIR_SHADOW_START_GATE_V2_BLOCKERS"

    state = {
        "candidate": CANDIDATE,
        "decision_status": decision_status,
        "start_reference_allowed": start_reference_allowed,
        "shadow_runtime_start_executed": False,
        "runtime_engine_path": engine_path,
        "sandbox_root": sandbox_root,
        "preflight_v2_path": str(pf_path) if pf_path else None,
        "approval_record_path": str(approval_path) if approval_path else None,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "shadow_start_allowed": start_reference_allowed,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": next_action,
        "important": [
            "This module did not execute runtime.",
            "This module did not start active paper.",
            "This module did not start live.",
            "This module did not mutate active config.",
            "Reference command is commented and supervised only."
        ],
    }

    write_json(out_dir / "ret60_shadow_start_gate_v2_state.json", state)
    pd.DataFrame(gates).to_csv(out_dir / "ret60_shadow_start_gate_v2_gates.csv", index=False)

    ref = "# REFERENCE ONLY - SUPERVISED ONLY - DO NOT RUN AS LIVE\n"
    ref += "# This is file/self-test shadow only. It does not use exchange API and does not place orders.\n"
    if start_reference_allowed:
        ref += f'python "{engine_path}" --self_test --out_dir "{sandbox_root}"\n'
        ref += "\n# Optional future local CSV replay form:\n"
        ref += f'# python "{engine_path}" --shadow_runtime "C:\\path\\to\\local_candles.csv" --out_dir "{sandbox_root}"\n'
    else:
        ref += "# BLOCKED - gate did not allow a start reference.\n"

    (out_dir / "ret60_shadow_start_v2_COMMAND_REFERENCE_ONLY.ps1").write_text(ref, encoding="utf-8")

    print("EDGE FACTORY RET60 SHADOW START GATE v2")
    print("=" * 100)
    print(f"workspace : {ws}")
    print(f"output_dir: {out_dir}")
    print(f"decision_status: {decision_status}")
    print(f"start_reference_allowed: {start_reference_allowed}")
    print("shadow_runtime_start_executed: False")
    print(f"runtime_engine_path: {engine_path}")
    print(f"sandbox_root: {sandbox_root}")
    print(f"gates: {passed}/{total}")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if not all_ok:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print(f"State: {out_dir / 'ret60_shadow_start_gate_v2_state.json'}")
    print(f"Gates: {out_dir / 'ret60_shadow_start_gate_v2_gates.csv'}")
    print(f"Reference: {out_dir / 'ret60_shadow_start_v2_COMMAND_REFERENCE_ONLY.ps1'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
