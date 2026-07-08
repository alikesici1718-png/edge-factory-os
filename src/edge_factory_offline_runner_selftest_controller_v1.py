#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_offline_runner_selftest_controller_v1"

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern))
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

def load_panel(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Offline runner self-test controller for a validated candidate.")
    ap.add_argument("--max_rows", type=int, default=250000)
    ap.add_argument("--hold_hours", type=int, default=6)
    ap.add_argument("--liquidity_quantile", type=float, default=0.50)
    ap.add_argument("--max_selftest_trades", type=int, default=5000)
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"offline_runner_selftest_controller_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    quality_state_path = latest_file(
        WORKSPACE / "edge_factory_feature_panel_quality_auditor_v1",
        "feature_panel_quality_audit_v1_state.json"
    )
    quality = read_json(quality_state_path)

    contract_path = latest_file(
        WORKSPACE / "edge_factory_candidate_contract_artifact_planner_v1",
        "market_panic_rebound_long_v1_offline_experiment_contract_v1_completed.json"
    )
    contract = read_json(contract_path)

    request_path = latest_file(
        WORKSPACE / "edge_factory_contract_to_runner_adapter_v1",
        "offline_runner_request_v1.json"
    )
    request = read_json(request_path)

    blockers = []

    if quality.get("audit_status") != "FEATURE_PANEL_QUALITY_PASS":
        blockers.append(f"PANEL_QUALITY_NOT_PASS:{quality.get('audit_status')}")

    if quality.get("runner_panel_allowed") is not True:
        blockers.append("RUNNER_PANEL_NOT_ALLOWED")

    panel_path = Path(str(quality.get("panel_path", ""))) if quality.get("panel_path") else None
    if not panel_path or not panel_path.exists():
        blockers.append("FEATURE_PANEL_NOT_FOUND")

    if not contract or "__read_error__" in contract:
        blockers.append("CONTRACT_NOT_READABLE")

    if not request or "__read_error__" in request:
        blockers.append("RUNNER_REQUEST_NOT_READABLE")

    candidate_key = quality.get("candidate_key") or request.get("candidate_key") or "UNKNOWN"
    family_key = request.get("family_key") or contract.get("identity", {}).get("family_key") or "UNKNOWN"

    output_root = WORKSPACE / "edge_factory_offline_runner_outputs" / str(candidate_key)
    output_root.mkdir(parents=True, exist_ok=True)

    plan = {
        "plan_version": "edge_factory_offline_runner_selftest_plan_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_key": candidate_key,
        "family_key": family_key,
        "panel_path": str(panel_path) if panel_path else "",
        "contract_path": str(contract_path) if contract_path else "",
        "request_path": str(request_path) if request_path else "",
        "side": "long",
        "entry_rule": "mkt_ret6_bps <= -250 and coin_ret6_bps <= -400 and entry_vol_quote >= liquidity_floor",
        "exit_rule": f"fixed_hold_{args.hold_hours}h",
        "hold_hours": args.hold_hours,
        "liquidity_floor_method": f"entry_vol_quote quantile {args.liquidity_quantile}",
        "max_rows": args.max_rows,
        "max_selftest_trades": args.max_selftest_trades,
        "safety": {
            "touch_master": False,
            "run_full_backtest": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
            "real_orders": False,
        }
    }

    trades = pd.DataFrame()
    summary = {}
    selftest_status = "OFFLINE_RUNNER_SELFTEST_BLOCKED"
    next_action = "FIX_BLOCKERS"

    if not blockers:
        df = load_panel(panel_path)

        required = [
            "time", "symbol", "close", "entry_vol_quote",
            "coin_ret6_bps", "mkt_ret6_bps",
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            blockers.append(f"PANEL_MISSING_REQUIRED_COLUMNS:{missing}")
        else:
            df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
            df = df.dropna(subset=["time", "symbol", "close"])
            df = df.sort_values(["symbol", "time"])

            # Keep self-test bounded. We use the most recent max_rows so the path is fast but realistic.
            if len(df) > args.max_rows:
                df = df.sort_values("time").tail(args.max_rows).sort_values(["symbol", "time"])

            for c in ["close", "entry_vol_quote", "coin_ret6_bps", "mkt_ret6_bps"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")

            liq_series = df["entry_vol_quote"].replace([np.inf, -np.inf], np.nan).dropna()
            liquidity_floor = float(liq_series.quantile(args.liquidity_quantile)) if len(liq_series) else 0.0

            signal_mask = (
                (df["mkt_ret6_bps"] <= -250.0) &
                (df["coin_ret6_bps"] <= -400.0) &
                (df["entry_vol_quote"] >= liquidity_floor)
            )

            signals = df.loc[signal_mask, ["time", "symbol", "close", "entry_vol_quote", "coin_ret6_bps", "mkt_ret6_bps"]].copy()
            signals = signals.sort_values(["time", "symbol"]).head(args.max_selftest_trades)

            if signals.empty:
                selftest_status = "OFFLINE_RUNNER_SELFTEST_NO_SIGNALS"
                next_action = "RELAX_OR_REVIEW_SIGNAL_THRESHOLDS"
                summary = {
                    "liquidity_floor": liquidity_floor,
                    "signals": 0,
                    "tested_rows": int(len(df)),
                    "tested_symbols": int(df["symbol"].nunique()),
                }
            else:
                future = df[["time", "symbol", "close"]].copy()
                future = future.sort_values(["symbol", "time"])
                future["exit_time"] = future.groupby("symbol")["time"].shift(-args.hold_hours)
                future["exit_close"] = future.groupby("symbol")["close"].shift(-args.hold_hours)

                merged = signals.merge(
                    future[["time", "symbol", "exit_time", "exit_close"]],
                    on=["time", "symbol"],
                    how="left",
                )

                merged = merged.dropna(subset=["exit_time", "exit_close"]).copy()

                fee_bps = float(contract.get("cost_model", {}).get("fee_bps", 5.0))
                slippage_bps = float(contract.get("cost_model", {}).get("slippage_bps", 20.0))
                total_cost_bps = float(contract.get("cost_model", {}).get("total_cost_bps", fee_bps + slippage_bps))

                merged["side"] = "long"
                merged["entry_price"] = merged["close"]
                merged["raw_ret_bps"] = ((merged["exit_close"] / merged["entry_price"]) - 1.0) * 10000.0
                merged["cost_bps"] = total_cost_bps
                merged["net_ret_bps"] = merged["raw_ret_bps"] - total_cost_bps
                merged["candidate_key"] = candidate_key
                merged["family_key"] = family_key
                merged = merged.rename(columns={"time": "entry_time"})

                trades = merged[[
                    "candidate_key", "family_key", "symbol", "side",
                    "entry_time", "exit_time", "entry_price", "exit_close",
                    "entry_vol_quote", "coin_ret6_bps", "mkt_ret6_bps",
                    "raw_ret_bps", "cost_bps", "net_ret_bps"
                ]].copy()

                if trades.empty:
                    selftest_status = "OFFLINE_RUNNER_SELFTEST_NO_CLOSED_TEST_TRADES"
                    next_action = "INSPECT_HOLD_TIME_OR_SIGNAL_TIMES"
                else:
                    win_rate = float((trades["net_ret_bps"] > 0).mean())
                    mean_net = float(trades["net_ret_bps"].mean())
                    median_net = float(trades["net_ret_bps"].median())
                    trade_count = int(len(trades))
                    symbol_count = int(trades["symbol"].nunique())

                    gross_profit = float(trades.loc[trades["net_ret_bps"] > 0, "net_ret_bps"].sum())
                    gross_loss = float(-trades.loc[trades["net_ret_bps"] < 0, "net_ret_bps"].sum())
                    profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

                    summary = {
                        "liquidity_floor": liquidity_floor,
                        "tested_rows": int(len(df)),
                        "tested_symbols": int(df["symbol"].nunique()),
                        "signal_count": int(len(signals)),
                        "closed_selftest_trades": trade_count,
                        "trade_symbol_count": symbol_count,
                        "win_rate": win_rate,
                        "mean_net_ret_bps": mean_net,
                        "median_net_ret_bps": median_net,
                        "profit_factor": profit_factor,
                        "fee_bps": fee_bps,
                        "slippage_bps": slippage_bps,
                        "total_cost_bps": total_cost_bps,
                    }

                    if trade_count < 5:
                        selftest_status = "OFFLINE_RUNNER_SELFTEST_PASS_LOW_SAMPLE"
                        next_action = "FULL_OFFLINE_RUNNER_PLAN_ALLOWED_BUT_EXPECT_LOW_SIGNAL_RATE"
                    else:
                        selftest_status = "OFFLINE_RUNNER_SELFTEST_PASS"
                        next_action = "BUILD_FULL_OFFLINE_RUNNER_OR_RUN_OFFLINE_BACKTEST_CONTROLLER"

    trades_csv = out_dir / f"{candidate_key}_selftest_trades.csv"
    summary_json = out_dir / f"{candidate_key}_selftest_summary.json"
    plan_json = out_dir / "offline_runner_selftest_plan_v1.json"

    trades.to_csv(trades_csv, index=False)
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    plan_json.write_text(json.dumps(plan, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "candidate_key": candidate_key,
        "family_key": family_key,
        "selftest_status": selftest_status,
        "blockers": blockers,
        "summary": summary,
        "plan_path": str(plan_json),
        "trades_csv": str(trades_csv),
        "summary_json": str(summary_json),
        "next_action": next_action,
        "full_offline_runner_allowed": selftest_status in {
            "OFFLINE_RUNNER_SELFTEST_PASS",
            "OFFLINE_RUNNER_SELFTEST_PASS_LOW_SAMPLE",
        },
        "runner_execution_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Self-test only; not full backtest.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop MASTER processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital.",
        ],
    }

    state_path = out_dir / "offline_runner_selftest_controller_v1_state.json"
    report_path = out_dir / "offline_runner_selftest_controller_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Offline Runner Self-Test Controller v1")
    md.append("")
    md.append(f"Status: `{selftest_status}`")
    md.append(f"Candidate: `{candidate_key}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Summary")
    md.append("```json")
    md.append(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    md.append("```")
    md.append("")
    md.append("## Outputs")
    md.append(f"- Trades: `{trades_csv}`")
    md.append(f"- Summary: `{summary_json}`")
    md.append(f"- Plan: `{plan_json}`")
    md.append("")
    md.append("## Safety")
    md.append("- runner_execution_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY OFFLINE RUNNER SELF-TEST CONTROLLER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate : {candidate_key}")
    print(f"family    : {family_key}")
    print(f"selftest_status: {selftest_status}")
    print(f"blockers: {blockers}")
    print(f"next_action: {next_action}")
    print(f"full_offline_runner_allowed: {state['full_offline_runner_allowed']}")
    print("runner_execution_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    print()
    print(f"Trades : {trades_csv}")
    print(f"Summary: {summary_json}")
    print(f"Plan   : {plan_json}")
    print(f"State  : {state_path}")
    print(f"Report : {report_path}")

if __name__ == "__main__":
    main()
