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

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_ret60_shadow_drift_monitor_v2" / f"ret60_shadow_drift_v2_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    obs_dir = latest_dir(WORKSPACE / "edge_factory_ret60_shadow_runtime_observer_v2", "ret60_shadow_runtime_observer_v2_")
    obs_path = obs_dir / "ret60_shadow_runtime_observer_v2_state.json" if obs_dir else None
    obs = read_json(obs_path)

    native_csv = Path(obs.get("native_csv", "")) if obs.get("native_csv") else None
    closed_csv = Path(obs.get("closed_csv", "")) if obs.get("closed_csv") else None

    gates = []

    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("observer_state_exists", bool(obs_path and obs_path.exists()), str(obs_path))
    gate("observer_passed", obs.get("observer_passed") is True, obs.get("observer_status"))
    gate("native_csv_exists", bool(native_csv and native_csv.exists()), str(native_csv))
    gate("closed_csv_exists", bool(closed_csv and closed_csv.exists()), str(closed_csv))
    gate("observer_live_blocked", obs.get("live_allowed") is False, obs.get("live_allowed"))
    gate("observer_active_paper_blocked", obs.get("active_paper_allowed") is False, obs.get("active_paper_allowed"))

    native_rows = 0
    closed_rows = 0
    net_pnl_sum = 0.0
    net_bps_mean = 0.0
    runtime_modes = []
    symbols = []
    source_basis = []
    sample_type = "UNKNOWN"
    market_drift_valid = False

    if native_csv and native_csv.exists():
        df = pd.read_csv(native_csv)
        native_rows = int(len(df))
        runtime_modes = sorted(df.get("runtime_mode", pd.Series(dtype=str)).astype(str).unique().tolist())
        symbols = sorted(df.get("symbol", pd.Series(dtype=str)).astype(str).unique().tolist())
        source_basis = sorted(df.get("source_candle_basis", pd.Series(dtype=str)).astype(str).unique().tolist())
        net_pnl_sum = float(pd.to_numeric(df.get("net_pnl_usdt", pd.Series(dtype=float)), errors="coerce").sum())
        net_bps_mean = float(pd.to_numeric(df.get("net_return_bps_native", pd.Series(dtype=float)), errors="coerce").mean())

        mode_text = " ".join(runtime_modes).lower()
        basis_text = " ".join(source_basis).lower()
        symbol_text = " ".join(symbols).lower()

        if "self_test" in mode_text or "test-usdt" in symbol_text:
            sample_type = "ENGINE_SELF_TEST_ONLY"
            market_drift_valid = False
        elif "shadow_runtime_file_replay" in mode_text or "shadow_replay" in mode_text:
            sample_type = "LOCAL_MARKET_CSV_REPLAY"
            market_drift_valid = native_rows > 0
        else:
            sample_type = "UNCLASSIFIED_RUNTIME_SAMPLE"
            market_drift_valid = False

    if closed_csv and closed_csv.exists():
        cdf = pd.read_csv(closed_csv)
        closed_rows = int(len(cdf))

    gate("native_rows_positive", native_rows > 0, native_rows)
    gate("closed_rows_positive", closed_rows > 0, closed_rows)
    gate("row_counts_match", native_rows == closed_rows and native_rows > 0, f"native={native_rows} closed={closed_rows}")
    gate("sample_type_classified", sample_type != "UNKNOWN", sample_type)
    gate("self_test_not_promoted_as_market_drift", sample_type != "ENGINE_SELF_TEST_ONLY" or market_drift_valid is False, sample_type)

    passed = sum(1 for g in gates if g["passed"])
    total = len(gates)

    if passed != total:
        status = "RET60_SHADOW_DRIFT_MONITOR_BLOCKED_BAD_RUNTIME_OUTPUT"
        next_action = "REPAIR_SHADOW_RUNTIME_OUTPUTS"
    elif sample_type == "ENGINE_SELF_TEST_ONLY":
        status = "RET60_SHADOW_DRIFT_MONITOR_PASS_ENGINE_SELF_TEST_ONLY_MARKET_DRIFT_BLOCKED"
        next_action = "RUN_RET60_ENGINE_ON_REAL_LOCAL_CANDLE_CSV_OR_BUILD_MARKET_DATA_FEED"
    elif sample_type == "LOCAL_MARKET_CSV_REPLAY" and market_drift_valid:
        status = "RET60_SHADOW_DRIFT_MONITOR_MARKET_REPLAY_SAMPLE_READY_FOR_BACKTEST_COMPARISON"
        next_action = "COMPARE_RET60_SHADOW_REPLAY_VS_BACKTEST_EXPECTATIONS"
    else:
        status = "RET60_SHADOW_DRIFT_MONITOR_BLOCKED_UNCLASSIFIED_SAMPLE"
        next_action = "CLASSIFY_RUNTIME_SAMPLE_SOURCE"

    result = {
        "candidate": CANDIDATE,
        "drift_status": status,
        "sample_type": sample_type,
        "market_drift_valid": market_drift_valid,
        "observer_state_path": str(obs_path) if obs_path else None,
        "native_csv": str(native_csv) if native_csv else None,
        "closed_csv": str(closed_csv) if closed_csv else None,
        "native_rows": native_rows,
        "closed_rows": closed_rows,
        "runtime_modes": runtime_modes,
        "symbols": symbols[:50],
        "source_basis": source_basis,
        "net_pnl_sum": net_pnl_sum,
        "net_bps_mean": net_bps_mean,
        "gates_passed": passed,
        "gates_total": total,
        "gates": gates,
        "profitability_interpretation": (
            "DO_NOT_USE_AS_EDGE_EVIDENCE_SELF_TEST_ONLY"
            if sample_type == "ENGINE_SELF_TEST_ONLY"
            else "CAN_BE_USED_FOR_DRIFT_ONLY_IF_SOURCE_IS_REAL_MARKET_CSV"
        ),
        "ready_for_active_paper_review": False,
        "ready_for_live_review": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": next_action,
    }

    write_json(out_dir / "ret60_shadow_drift_monitor_v2_state.json", result)
    pd.DataFrame(gates).to_csv(out_dir / "ret60_shadow_drift_monitor_v2_gates.csv", index=False)

    print("EDGE FACTORY RET60 SHADOW DRIFT MONITOR v2")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"drift_status: {status}")
    print(f"sample_type: {sample_type}")
    print(f"market_drift_valid: {market_drift_valid}")
    print(f"native_rows: {native_rows}")
    print(f"closed_rows: {closed_rows}")
    print(f"net_pnl_sum: {net_pnl_sum}")
    print(f"net_bps_mean: {net_bps_mean}")
    print(f"runtime_modes: {runtime_modes}")
    print(f"gates: {passed}/{total}")
    print("ready_for_active_paper_review: False")
    print("ready_for_live_review: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")

    if sample_type == "ENGINE_SELF_TEST_ONLY":
        print()
        print("IMPORTANT")
        print("-" * 100)
        print("This is engine self-test output only. Profit numbers are NOT market edge evidence.")
        print("Next: run the engine on real local candle CSV or build a real market data feed.")

    if passed != total:
        print()
        print("BLOCKERS")
        print("-" * 100)
        for g in gates:
            if not g["passed"]:
                print(f"- {g['gate']}: {g['reason']}")

    print()
    print(f"State: {out_dir / 'ret60_shadow_drift_monitor_v2_state.json'}")
    print(f"Gates: {out_dir / 'ret60_shadow_drift_monitor_v2_gates.csv'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
