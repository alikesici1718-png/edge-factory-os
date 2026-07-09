#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic tool that sweeps threshold and hold-duration parameter combinations for the post_impulse_drift_long candidate using the latest feature panel parquet/CSV, evaluating profit factor, win rate, and drawdown for each combination. Outputs a diagnostic state JSON and results CSV to the edge_factory_post_impulse_threshold_hold_diagnostic_v1 directory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_post_impulse_threshold_hold_diagnostic_v1"

CANDIDATE = "post_impulse_drift_long_v1"
FAMILY = "impulse_drift_long"

def latest_panel() -> Path | None:
    root = WORKSPACE / "edge_factory_feature_panels" / CANDIDATE
    files = list(root.rglob("*feature_panel_1h_dynamic.parquet")) + list(root.rglob("*feature_panel_1h_dynamic.csv"))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def load_panel(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)

def profit_factor(x: pd.Series) -> float | None:
    gp = float(x[x > 0].sum())
    gl = float(-x[x < 0].sum())
    if gl <= 0:
        return None
    return gp / gl

def max_drawdown_bps(x: pd.Series) -> float:
    eq = x.fillna(0).cumsum()
    dd = eq - eq.cummax()
    return float(dd.min()) if len(dd) else 0.0

def evaluate_combo(
    df: pd.DataFrame,
    coin_thr: float,
    mkt_thr: float,
    liq_q: float,
    range_cap_q: float | None,
    hold_hours: int,
    max_trades: int,
) -> dict[str, Any]:
    liq_floor = float(df["entry_vol_quote"].dropna().quantile(liq_q))

    mask = (
        (df["coin_ret3_bps"] >= coin_thr) &
        (df["mkt_ret3_bps"] >= mkt_thr) &
        (df["entry_vol_quote"] >= liq_floor)
    )

    range_cap = None
    if range_cap_q is not None:
        range_cap = float(df["entry_range_bps"].dropna().quantile(range_cap_q))
        mask = mask & (df["entry_range_bps"] <= range_cap)

    signals = df.loc[
        mask,
        ["time", "symbol", "close", "entry_vol_quote", "entry_range_bps", "coin_ret3_bps", "mkt_ret3_bps", "coin_ret6_bps", "mkt_ret6_bps"]
    ].copy()

    signals = signals.sort_values(["time", "symbol"]).head(max_trades)

    if signals.empty:
        return {
            "coin_thr": coin_thr,
            "mkt_thr": mkt_thr,
            "liq_q": liq_q,
            "range_cap_q": range_cap_q,
            "range_cap": range_cap,
            "hold_hours": hold_hours,
            "trade_count": 0,
            "symbol_count": 0,
            "win_rate": None,
            "mean_net_bps": None,
            "median_net_bps": None,
            "profit_factor": None,
            "max_drawdown_bps": None,
            "score": -9999,
            "status": "NO_SIGNALS",
        }

    fut = df[["time", "symbol", "close"]].sort_values(["symbol", "time"]).copy()
    fut["exit_time"] = fut.groupby("symbol")["time"].shift(-hold_hours)
    fut["exit_close"] = fut.groupby("symbol")["close"].shift(-hold_hours)

    trades = signals.merge(
        fut[["time", "symbol", "exit_time", "exit_close"]],
        on=["time", "symbol"],
        how="left",
    ).dropna(subset=["exit_time", "exit_close"]).copy()

    if trades.empty:
        return {
            "coin_thr": coin_thr,
            "mkt_thr": mkt_thr,
            "liq_q": liq_q,
            "range_cap_q": range_cap_q,
            "range_cap": range_cap,
            "hold_hours": hold_hours,
            "trade_count": 0,
            "symbol_count": 0,
            "win_rate": None,
            "mean_net_bps": None,
            "median_net_bps": None,
            "profit_factor": None,
            "max_drawdown_bps": None,
            "score": -9999,
            "status": "NO_CLOSED_TRADES",
        }

    total_cost_bps = 25.0
    trades["raw_ret_bps"] = ((trades["exit_close"] / trades["close"]) - 1.0) * 10000.0
    trades["net_ret_bps"] = trades["raw_ret_bps"] - total_cost_bps

    n = int(len(trades))
    sym_n = int(trades["symbol"].nunique())
    wr = float((trades["net_ret_bps"] > 0).mean())
    mean_net = float(trades["net_ret_bps"].mean())
    med_net = float(trades["net_ret_bps"].median())
    pf = profit_factor(trades["net_ret_bps"])
    dd = max_drawdown_bps(trades["net_ret_bps"])

    # Conservative score: require enough sample, positive mean, less-bad median, PF.
    sample_penalty = 0
    if n < 300:
        sample_penalty -= 60
    elif n < 600:
        sample_penalty -= 25

    median_penalty = min(0.0, med_net) * 0.15
    pf_score = ((pf or 0.0) - 1.0) * 100.0
    score = mean_net + pf_score + median_penalty + sample_penalty + min(sym_n, 100) * 0.05

    if n >= 300 and pf is not None and pf >= 1.10 and mean_net > 10 and med_net > -25:
        status = "PROMISING_DIAGNOSTIC"
    elif n >= 300 and pf is not None and pf >= 1.03 and mean_net > 0:
        status = "WEAK_POSITIVE_DIAGNOSTIC"
    else:
        status = "NOT_GOOD_ENOUGH"

    return {
        "coin_thr": coin_thr,
        "mkt_thr": mkt_thr,
        "liq_q": liq_q,
        "range_cap_q": range_cap_q,
        "range_cap": range_cap,
        "hold_hours": hold_hours,
        "trade_count": n,
        "symbol_count": sym_n,
        "win_rate": wr,
        "mean_net_bps": mean_net,
        "median_net_bps": med_net,
        "profit_factor": pf,
        "max_drawdown_bps": dd,
        "score": round(score, 4),
        "status": status,
    }

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--max_rows", type=int, default=500000)
    ap.add_argument("--max_trades", type=int, default=12000)
    args = ap.parse_args()

    out_dir = OUT_ROOT / f"post_impulse_threshold_hold_diagnostic_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    panel_path = latest_panel()
    blockers = []

    if not panel_path or not panel_path.exists():
        blockers.append("DYNAMIC_FEATURE_PANEL_NOT_FOUND")

    results = []
    top = None

    if not blockers:
        df = load_panel(panel_path)
        df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
        df = df.dropna(subset=["time", "symbol", "close"])
        df = df.sort_values("time")

        if len(df) > args.max_rows:
            df = df.tail(args.max_rows)

        df = df.sort_values(["symbol", "time"])

        for c in ["close", "entry_vol_quote", "entry_range_bps", "coin_ret3_bps", "mkt_ret3_bps", "coin_ret6_bps", "mkt_ret6_bps"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna(subset=["entry_vol_quote", "entry_range_bps", "coin_ret3_bps", "mkt_ret3_bps"])

        coin_thresholds = [200, 250, 300, 400, 500, 700]
        mkt_thresholds = [0, 25, 50, 75, 100, 150]
        liq_quantiles = [0.50, 0.60, 0.70, 0.80, 0.90]
        range_caps = [None, 0.90, 0.80, 0.70]
        holds = [3, 6, 9, 12]

        total = len(coin_thresholds) * len(mkt_thresholds) * len(liq_quantiles) * len(range_caps) * len(holds)
        done = 0

        for coin_thr in coin_thresholds:
            for mkt_thr in mkt_thresholds:
                for liq_q in liq_quantiles:
                    for range_q in range_caps:
                        for hold in holds:
                            done += 1
                            r = evaluate_combo(
                                df=df,
                                coin_thr=coin_thr,
                                mkt_thr=mkt_thr,
                                liq_q=liq_q,
                                range_cap_q=range_q,
                                hold_hours=hold,
                                max_trades=args.max_trades,
                            )
                            results.append(r)

                            if done % 100 == 0:
                                print(f"[diagnostic] {done}/{total} combos")

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        top = results[0] if results else None

    if blockers:
        diagnostic_status = "POST_IMPULSE_DIAGNOSTIC_BLOCKED"
        next_action = "FIX_PANEL_INPUT"
        recommendation = "NO_DECISION"
    elif not top:
        diagnostic_status = "POST_IMPULSE_DIAGNOSTIC_NO_RESULTS"
        next_action = "INSPECT_DIAGNOSTIC"
        recommendation = "NO_DECISION"
    elif top["status"] == "PROMISING_DIAGNOSTIC":
        diagnostic_status = "POST_IMPULSE_DIAGNOSTIC_PROMISING_COMBO_FOUND"
        next_action = "CREATE_REDESIGNED_CONTRACT_FROM_TOP_COMBO"
        recommendation = "REDESIGN_AND_RETEST"
    elif top["status"] == "WEAK_POSITIVE_DIAGNOSTIC":
        diagnostic_status = "POST_IMPULSE_DIAGNOSTIC_WEAK_POSITIVE_ONLY"
        next_action = "OPTIONAL_STRICTER_SEARCH_OR_ARCHIVE"
        recommendation = "KEEP_TESTING_NOT_PROMOTE"
    else:
        diagnostic_status = "POST_IMPULSE_DIAGNOSTIC_NO_GOOD_COMBO"
        next_action = "ARCHIVE_WAIT_SELECT_NEXT_CANDIDATE"
        recommendation = "ARCHIVE_WAIT"

    result_df = pd.DataFrame(results)
    result_csv = out_dir / "post_impulse_threshold_hold_diagnostic_v1_results.csv"
    top_csv = out_dir / "post_impulse_threshold_hold_diagnostic_v1_top50.csv"
    result_df.to_csv(result_csv, index=False)
    result_df.head(50).to_csv(top_csv, index=False)

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "candidate_key": CANDIDATE,
        "family_key": FAMILY,
        "diagnostic_status": diagnostic_status,
        "recommendation": recommendation,
        "next_action": next_action,
        "blockers": blockers,
        "panel_path": str(panel_path) if panel_path else "",
        "combo_count": len(results),
        "top_combo": top,
        "full_run_allowed": top is not None and top.get("status") == "PROMISING_DIAGNOSTIC",
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Diagnostic only searches thresholds/holds offline.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital.",
        ],
    }

    state_path = out_dir / "post_impulse_threshold_hold_diagnostic_v1_state.json"
    report_path = out_dir / "post_impulse_threshold_hold_diagnostic_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Post Impulse Threshold/Hold Diagnostic v1")
    md.append("")
    md.append(f"Status: `{diagnostic_status}`")
    md.append(f"Recommendation: `{recommendation}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Top combo")
    md.append("```json")
    md.append(json.dumps(top, indent=2, ensure_ascii=False, default=str))
    md.append("```")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY POST IMPULSE THRESHOLD/HOLD DIAGNOSTIC v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate : {CANDIDATE}")
    print(f"diagnostic_status: {diagnostic_status}")
    print(f"recommendation: {recommendation}")
    print(f"next_action: {next_action}")
    print(f"combo_count: {len(results)}")
    print(f"full_run_allowed: {state['full_run_allowed']}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("TOP 20 COMBOS")
    print("-" * 100)
    if not result_df.empty:
        cols = ["status","score","coin_thr","mkt_thr","liq_q","range_cap_q","hold_hours","trade_count","symbol_count","win_rate","mean_net_bps","median_net_bps","profit_factor","max_drawdown_bps"]
        print(result_df[cols].head(20).to_string(index=False))
    else:
        print("No results.")
    print()
    print(f"Results: {result_csv}")
    print(f"Top50  : {top_csv}")
    print(f"State  : {state_path}")
    print(f"Report : {report_path}")

if __name__ == "__main__":
    main()
