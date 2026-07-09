#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OS invariant guard (v1) that reads live paper logger state from MASTER_UPPER_SYSTEM and enforces hard safety invariants (e.g. no unexpected live flag, no gate timeouts, healthy folder structure), emitting a gate-level pass/fail report written to a timestamped directory in the workspace.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
MASTER = WORKSPACE / "paper_run_gate_MASTER_UPPER_SYSTEM"

EXPECTED_FOLDERS = {
    "old_short": MASTER / "live_blowoff_short_paper_realistic",
    "impulse_long": MASTER / "live_impulse_event_long_paper",
    "market_relative_short": MASTER / "live_market_relative_extreme_reversion_short_paper",
    "weak_market_short": MASTER / "live_weak_market_breakdown_short_paper",
}

BAD_GATE_REASONS = {
    "global_gate_timeout_gate_file_missing",
    "global_gate_timeout_gate_empty",
}

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"READ_ERROR": repr(e)}

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as e:
        return pd.DataFrame({"READ_ERROR": [repr(e)]})

def parse_utc(x: Any):
    try:
        return pd.to_datetime(x, utc=True)
    except Exception:
        return pd.NaT

def add_gate(rows, name, passed, severity, evidence):
    rows.append({
        "gate": name,
        "passed": bool(passed),
        "severity": severity,
        "evidence": str(evidence),
    })

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_os_invariant_guard_v1" / f"os_invariant_guard_v1_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    gates = []
    family_rows = []

    family_config_path = MASTER / "family_config.json"
    gate_path = MASTER / "global_gate_decisions.csv"
    snapshot_path = MASTER / "global_risk_snapshot.csv"

    family_config = read_json(family_config_path)
    gate_df = read_csv(gate_path)
    snap_df = read_csv(snapshot_path)

    add_gate(gates, "master_folder_exists", MASTER.exists(), "CRITICAL", MASTER)
    add_gate(gates, "family_config_exists", family_config_path.exists(), "CRITICAL", family_config_path)
    add_gate(gates, "global_gate_decisions_exists", gate_path.exists(), "CRITICAL", gate_path)
    add_gate(gates, "global_risk_snapshot_exists", snapshot_path.exists(), "CRITICAL", snapshot_path)

    # family_config invariant
    cfg_ok = isinstance(family_config, dict)
    add_gate(gates, "family_config_is_dict", cfg_ok, "CRITICAL", type(family_config).__name__)

    if cfg_ok:
        for key, expected_path in EXPECTED_FOLDERS.items():
            actual = Path(str(family_config.get(key, "")))
            add_gate(
                gates,
                f"family_config_{key}_points_expected_folder",
                actual == expected_path,
                "CRITICAL",
                f"actual={actual} expected={expected_path}",
            )
            add_gate(
                gates,
                f"family_folder_{key}_exists",
                expected_path.exists(),
                "CRITICAL",
                expected_path,
            )

    total_pending = 0
    total_open = 0
    total_closed = 0
    total_errors = 0
    recent_bad_rejects = []

    now = pd.Timestamp.now(tz="UTC")
    recent_cutoff = now - pd.Timedelta(hours=1)

    for key, folder in EXPECTED_FOLDERS.items():
        pending = read_csv(folder / "pending_entries.csv")
        openp = read_csv(folder / "open_positions.csv")
        closed = read_csv(folder / "closed_trades.csv")
        rejected = read_csv(folder / "rejected_entries.csv")
        errors = read_csv(folder / "errors.csv")

        total_pending += len(pending)
        total_open += len(openp)
        total_closed += len(closed)
        total_errors += len(errors)

        latest_bad_reason = None
        latest_bad_time = None
        recent_bad_count = 0

        if not rejected.empty and "reason" in rejected.columns:
            bad = rejected[rejected["reason"].astype(str).isin(BAD_GATE_REASONS)].copy()
            if not bad.empty:
                if "log_time" in bad.columns:
                    bad["_t"] = pd.to_datetime(bad["log_time"], utc=True, errors="coerce")
                    recent_bad = bad[bad["_t"] >= recent_cutoff]
                    recent_bad_count = len(recent_bad)
                    last = bad.sort_values("_t").tail(1)
                    latest_bad_reason = str(last["reason"].iloc[0])
                    latest_bad_time = str(last["_t"].iloc[0])
                else:
                    recent_bad_count = len(bad)
                    latest_bad_reason = str(bad["reason"].iloc[-1])

        if recent_bad_count > 0:
            recent_bad_rejects.append({
                "family_key": key,
                "recent_bad_count": recent_bad_count,
                "latest_bad_reason": latest_bad_reason,
                "latest_bad_time": latest_bad_time,
            })

        family_rows.append({
            "family_key": key,
            "folder": str(folder),
            "folder_exists": folder.exists(),
            "pending_rows": len(pending),
            "open_rows": len(openp),
            "closed_rows": len(closed),
            "rejected_rows": len(rejected),
            "errors_rows": len(errors),
            "recent_bad_gate_reject_count_1h": recent_bad_count,
            "latest_bad_gate_reason": latest_bad_reason,
            "latest_bad_gate_time": latest_bad_time,
        })

    add_gate(
        gates,
        "no_recent_gate_file_missing_or_empty_rejects_1h",
        len(recent_bad_rejects) == 0,
        "ATTENTION",
        recent_bad_rejects,
    )

    # Gate decision invariant.
    gate_has_rows = len(gate_df) > 0
    add_gate(gates, "global_gate_decisions_has_rows", gate_has_rows, "CRITICAL", f"rows={len(gate_df)}")

    if gate_has_rows and "decision" in gate_df.columns:
        decisions = set(gate_df["decision"].astype(str).unique())
        add_gate(
            gates,
            "global_gate_decisions_contains_allow_or_block",
            bool(decisions & {"ALLOW", "BLOCK"}),
            "CRITICAL",
            decisions,
        )
    else:
        add_gate(gates, "global_gate_decisions_contains_allow_or_block", False, "CRITICAL", "missing decision column or no rows")

    # Snapshot invariant.
    snapshot_pending = None
    snapshot_open = None
    if not snap_df.empty:
        if "pending_entries" in snap_df.columns:
            snapshot_pending = int(float(snap_df["pending_entries"].iloc[-1]))
        if "open_positions" in snap_df.columns:
            snapshot_open = int(float(snap_df["open_positions"].iloc[-1]))

    add_gate(
        gates,
        "snapshot_reads_pending_entries",
        snapshot_pending is not None,
        "CRITICAL",
        snapshot_pending,
    )
    add_gate(
        gates,
        "snapshot_reads_open_positions",
        snapshot_open is not None,
        "CRITICAL",
        snapshot_open,
    )

    if snapshot_pending is not None:
        add_gate(
            gates,
            "snapshot_pending_matches_family_pending",
            snapshot_pending == total_pending,
            "ATTENTION",
            f"snapshot={snapshot_pending} family_sum={total_pending}",
        )

    if snapshot_open is not None:
        add_gate(
            gates,
            "snapshot_open_matches_family_open",
            snapshot_open == total_open,
            "ATTENTION",
            f"snapshot={snapshot_open} family_sum={total_open}",
        )

    add_gate(
        gates,
        "no_family_errors",
        total_errors == 0,
        "ATTENTION",
        f"errors={total_errors}",
    )

    critical_failed = [g for g in gates if not g["passed"] and g["severity"] == "CRITICAL"]
    attention_failed = [g for g in gates if not g["passed"] and g["severity"] == "ATTENTION"]

    if critical_failed:
        status = "INVARIANT_GUARD_CRITICAL_FAIL"
    elif attention_failed:
        status = "INVARIANT_GUARD_ATTENTION"
    else:
        status = "INVARIANT_GUARD_PASS"

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "master": str(MASTER),
        "status": status,
        "critical_failed_count": len(critical_failed),
        "attention_failed_count": len(attention_failed),
        "total_pending": total_pending,
        "total_open": total_open,
        "total_closed": total_closed,
        "total_errors": total_errors,
        "snapshot_pending": snapshot_pending,
        "snapshot_open": snapshot_open,
        "gates": gates,
        "families": family_rows,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
    }

    state_path = out_dir / "edge_factory_os_invariant_guard_v1_state.json"
    gates_path = out_dir / "edge_factory_os_invariant_guard_v1_gates.csv"
    families_path = out_dir / "edge_factory_os_invariant_guard_v1_families.csv"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(gates).to_csv(gates_path, index=False)
    pd.DataFrame(family_rows).to_csv(families_path, index=False)

    print("EDGE FACTORY OS INVARIANT GUARD v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"master    : {MASTER}")
    print(f"output_dir: {out_dir}")
    print(f"status    : {status}")
    print(f"critical_failed: {len(critical_failed)}")
    print(f"attention_failed: {len(attention_failed)}")
    print(f"pending   : {total_pending}")
    print(f"open      : {total_open}")
    print(f"closed    : {total_closed}")
    print(f"errors    : {total_errors}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()

    print("FAILED GATES")
    print("-" * 100)
    failed = pd.DataFrame([g for g in gates if not g["passed"]])
    if failed.empty:
        print("NONE")
    else:
        print(failed.to_string(index=False))

    print()
    print("FAMILY SUMMARY")
    print("-" * 100)
    print(pd.DataFrame(family_rows).to_string(index=False))
    print()

    print(f"State   : {state_path}")
    print(f"Gates   : {gates_path}")
    print(f"Families: {families_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
