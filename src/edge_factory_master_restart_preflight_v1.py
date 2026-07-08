#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
RUN = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"
OUT_ROOT = WORKSPACE / "edge_factory_master_restart_preflight_v1"

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        try:
            return pd.read_csv(path, engine="python")
        except Exception:
            return pd.DataFrame()

def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def main():
    out_dir = OUT_ROOT / f"master_restart_preflight_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    family_config = read_json(RUN / "family_config.json")
    families = family_config.get("families", family_config) if isinstance(family_config, dict) else {}

    gate = read_csv(RUN / "global_gate_decisions.csv")
    if not gate.empty:
        gate.columns = [str(c).strip() for c in gate.columns]

    gate_keys = set()
    decision_counts = {}
    if not gate.empty and {"family_key", "signal_id"}.issubset(gate.columns):
        gate["__key"] = gate["family_key"].astype(str) + "||" + gate["signal_id"].astype(str)
        gate_keys = set(gate["__key"])
        if "decision" in gate.columns:
            decision_counts = gate["decision"].astype(str).value_counts().to_dict()

    pending_rows = []
    error_rows = []

    for fk, folder_raw in families.items():
        folder = Path(str(folder_raw))
        pending = read_csv(folder / "pending_entries.csv")
        errors = read_csv(folder / "errors.csv")

        if not pending.empty:
            pending.columns = [str(c).strip() for c in pending.columns]
            if "signal_id" in pending.columns:
                for _, r in pending.iterrows():
                    sid = str(r.get("signal_id", ""))
                    key = str(fk) + "||" + sid
                    pending_rows.append({
                        "family_key": fk,
                        "signal_id": sid,
                        "matched_in_gate": key in gate_keys,
                        "coin": str(r.get("coin", r.get("symbol", ""))),
                        "target_entry_time": str(r.get("target_entry_time", r.get("signal_time", ""))),
                    })

        if not errors.empty:
            errors.columns = [str(c).strip() for c in errors.columns]
            tail = errors.tail(20).copy()
            tail["family_key"] = fk
            error_rows.extend(tail.to_dict("records"))

    pending_df = pd.DataFrame(pending_rows)
    errors_df = pd.DataFrame(error_rows)

    if not pending_df.empty:
        pending_match_rate = float(pending_df["matched_in_gate"].mean())
        pending_unmatched = int((~pending_df["matched_in_gate"]).sum())
    else:
        pending_match_rate = None
        pending_unmatched = 0

    autopilot_state_path = WORKSPACE / "edge_factory_os_autopilot_loop_v4" / "edge_factory_os_autopilot_v4_latest_state.json"
    autopilot = read_json(autopilot_state_path)

    latest_command_center = latest_file(WORKSPACE / "edge_factory_os_command_center_v1", "edge_factory_os_command_center_v1_state.json")
    command_center = read_json(latest_command_center) if latest_command_center else {}

    blockers = []
    warnings = []

    if pending_unmatched > 0:
        blockers.append(f"PENDING_GATE_SIGNAL_ID_MISMATCH:{pending_unmatched}")

    if not gate.empty and decision_counts.get("ALLOW", 0) == 0:
        warnings.append("NO_ALLOW_IN_LAST_GATE_DECISIONS_CAN_BE_NORMAL_IF_LIMITS_FULL")

    if len(errors_df) > 0:
        warnings.append(f"ERROR_ROWS_EXIST_IN_FAMILY_ERROR_LOGS:{len(errors_df)}")

    ap_sev = autopilot.get("severity") or autopilot.get("autopilot_severity")
    ap_status = autopilot.get("status") or autopilot.get("autopilot_status")
    if ap_sev and str(ap_sev).upper() not in {"OK", "NONE"}:
        warnings.append(f"AUTOPILOT_SEVERITY:{ap_sev}")

    if blockers:
        preflight_status = "RESTART_PREFLIGHT_BLOCKED"
        restart_allowed = False
    else:
        preflight_status = "RESTART_PREFLIGHT_PASS_WITH_WARNINGS" if warnings else "RESTART_PREFLIGHT_PASS"
        restart_allowed = True

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "run": str(RUN),
        "preflight_status": preflight_status,
        "restart_allowed": restart_allowed,
        "blockers": blockers,
        "warnings": warnings,
        "gate_rows": int(len(gate)),
        "gate_decision_counts": decision_counts,
        "pending_rows_checked": int(len(pending_df)),
        "pending_match_rate": pending_match_rate,
        "pending_unmatched": pending_unmatched,
        "family_error_rows_tail_count": int(len(errors_df)),
        "autopilot_state_path": str(autopilot_state_path),
        "autopilot_status": ap_status,
        "autopilot_severity": ap_sev,
        "latest_command_center_state": str(latest_command_center) if latest_command_center else "",
    }

    state_path = out_dir / "master_restart_preflight_v1_state.json"
    pending_csv = out_dir / "master_restart_preflight_v1_pending_gate_match.csv"
    errors_csv = out_dir / "master_restart_preflight_v1_error_tail.csv"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pending_df.to_csv(pending_csv, index=False)
    errors_df.to_csv(errors_csv, index=False)

    print("EDGE FACTORY MASTER RESTART PREFLIGHT v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"run       : {RUN}")
    print(f"out_dir   : {out_dir}")
    print(f"preflight_status: {preflight_status}")
    print(f"restart_allowed : {restart_allowed}")
    print(f"gate_decision_counts: {decision_counts}")
    print(f"pending_rows_checked: {len(pending_df)}")
    print(f"pending_match_rate  : {pending_match_rate}")
    print(f"pending_unmatched   : {pending_unmatched}")
    print(f"family_error_rows_tail_count: {len(errors_df)}")
    print(f"autopilot_status  : {ap_status}")
    print(f"autopilot_severity: {ap_sev}")
    print()
    print("BLOCKERS")
    print("-" * 100)
    print("\n".join(f"- {x}" for x in blockers) if blockers else "NONE")
    print()
    print("WARNINGS")
    print("-" * 100)
    print("\n".join(f"- {x}" for x in warnings) if warnings else "NONE")
    print()
    print("RECENT ERROR TAIL")
    print("-" * 100)
    if errors_df.empty:
        print("NONE")
    else:
        print(errors_df.tail(20).to_string(index=False))
    print()
    print(f"State  : {state_path}")
    print(f"Pending: {pending_csv}")
    print(f"Errors : {errors_csv}")

if __name__ == "__main__":
    main()
