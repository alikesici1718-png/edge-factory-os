#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import numpy as np

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def profit_factor(x: pd.Series) -> float:
    y = pd.to_numeric(x, errors="coerce").dropna()
    if y.empty:
        return 0.0
    wins = y[y > 0].sum()
    losses = -y[y < 0].sum()
    if losses <= 0:
        return 999999.0 if wins > 0 else 0.0
    return float(wins / losses)

def dd_proxy(x: pd.Series) -> float:
    y = pd.to_numeric(x, errors="coerce").fillna(0.0)
    eq = y.cumsum()
    dd = eq - eq.cummax()
    return float(dd.min()) if len(dd) else 0.0

def summarize(label: str, df: pd.DataFrame, pnl_col: str = "net_return_bps") -> dict[str, Any]:
    if df.empty or pnl_col not in df.columns:
        return {
            "label": label,
            "trades": 0,
            "symbols": 0,
            "net_bps_sum": 0.0,
            "net_bps_mean": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "drawdown_proxy_bps": 0.0,
        }

    pnl = pd.to_numeric(df[pnl_col], errors="coerce").dropna()
    return {
        "label": label,
        "trades": int(len(pnl)),
        "symbols": int(df["symbol"].astype(str).nunique()) if "symbol" in df.columns else 0,
        "net_bps_sum": float(pnl.sum()),
        "net_bps_mean": float(pnl.mean()),
        "win_rate": float((pnl > 0).mean()),
        "profit_factor": profit_factor(pnl),
        "drawdown_proxy_bps": dd_proxy(pnl),
    }

def load_latest_replay() -> tuple[Path, dict[str, Any], pd.DataFrame]:
    d = latest_dir(WORKSPACE / "edge_factory_rel_extreme_real_candle_replay_v1", "rel_extreme_real_replay_")
    if not d:
        raise SystemExit("latest rel_extreme replay dir not found")

    state_path = d / "rel_extreme_real_candle_replay_state.json"
    state = read_json(state_path)

    trades_path = Path(state.get("trades_csv") or d / "rel_extreme_real_candle_replay_trades.csv")
    if not trades_path.exists():
        raise SystemExit(f"trades csv missing: {trades_path}")

    df = pd.read_csv(trades_path)
    return d, state, df

def build_monthly(df: pd.DataFrame) -> pd.DataFrame:
    t = df.copy()
    t["signal_time"] = pd.to_datetime(t["signal_time"], errors="coerce", utc=True)
    t = t.dropna(subset=["signal_time"])
    t["month"] = t["signal_time"].dt.to_period("M").astype(str)

    m = (
        t.groupby("month")
        .agg(
            trades=("net_return_bps", "count"),
            net_bps_sum=("net_return_bps", "sum"),
            net_bps_mean=("net_return_bps", "mean"),
            win_rate=("net_return_bps", lambda x: float((x > 0).mean())),
            profit_factor=("net_return_bps", profit_factor),
        )
        .reset_index()
        .sort_values("month")
    )
    return m

def time_splits(df: pd.DataFrame) -> pd.DataFrame:
    t = df.copy()
    t["signal_time"] = pd.to_datetime(t["signal_time"], errors="coerce", utc=True)
    t = t.dropna(subset=["signal_time"]).sort_values("signal_time").reset_index(drop=True)

    n = len(t)
    if n == 0:
        return pd.DataFrame()

    cuts = {
        "first_50pct": t.iloc[: int(n * 0.50)],
        "last_50pct": t.iloc[int(n * 0.50):],
        "first_70pct_train": t.iloc[: int(n * 0.70)],
        "last_30pct_oos": t.iloc[int(n * 0.70):],
        "last_20pct_oos": t.iloc[int(n * 0.80):],
    }

    max_time = t["signal_time"].max()
    cuts["last_90d"] = t[t["signal_time"] >= max_time - pd.Timedelta(days=90)]
    cuts["last_30d"] = t[t["signal_time"] >= max_time - pd.Timedelta(days=30)]

    return pd.DataFrame([summarize(k, v) for k, v in cuts.items()])

def top_symbol_dependency(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    by_sym = (
        df.groupby("symbol")
        .agg(net_bps_sum=("net_return_bps", "sum"), trades=("net_return_bps", "count"))
        .reset_index()
        .sort_values("net_bps_sum", ascending=False)
    )

    rows = [summarize("all_symbols", df)]

    for n in [1, 3, 5, 10, 20]:
        top = set(by_sym.head(n)["symbol"].astype(str))
        sub = df[~df["symbol"].astype(str).isin(top)].copy()
        row = summarize(f"exclude_top_{n}_symbols", sub)
        row["excluded_symbols"] = ",".join(list(top)[:20])
        rows.append(row)

    return pd.DataFrame(rows)

def cost_stress(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    t = df.copy()

    if "gross_return_bps" in t.columns:
        gross = pd.to_numeric(t["gross_return_bps"], errors="coerce")
    else:
        current_cost = pd.to_numeric(t.get("cost_bps", 25.0), errors="coerce").fillna(25.0)
        gross = pd.to_numeric(t["net_return_bps"], errors="coerce") + current_cost

    rows = []
    for cost in [0, 25, 50, 75, 100, 150, 200]:
        tmp = t.copy()
        tmp["stress_net_bps"] = gross - float(cost)
        row = summarize(f"cost_{cost}_bps", tmp, "stress_net_bps")
        row["cost_bps"] = cost
        rows.append(row)

    return pd.DataFrame(rows)

def capped_per_signal_time(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    t = df.copy()
    t["signal_time"] = pd.to_datetime(t["signal_time"], errors="coerce", utc=True)
    t = t.dropna(subset=["signal_time"])

    # When many symbols trigger in the same hour, choose strongest relative signal first.
    sort_cols = []
    for c in ["rel_ret_bps", "coin_ret6_bps", "net_return_bps"]:
        if c in t.columns:
            sort_cols.append(c)

    rows = [summarize("uncapped_all_signals", t)]

    if not sort_cols:
        return pd.DataFrame(rows)

    for cap in [1, 2, 3, 5, 10, 20]:
        ranked = (
            t.sort_values(["signal_time"] + sort_cols, ascending=[True] + [False] * len(sort_cols))
            .groupby("signal_time")
            .head(cap)
            .copy()
        )
        row = summarize(f"cap_{cap}_signals_per_hour", ranked)
        row["cap_per_hour"] = cap
        rows.append(row)

    return pd.DataFrame(rows)

def concurrency_profile(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}

    t = df.copy()
    t["entry_time"] = pd.to_datetime(t["entry_time"], errors="coerce", utc=True)
    t["exit_time"] = pd.to_datetime(t["exit_time"], errors="coerce", utc=True)
    t = t.dropna(subset=["entry_time", "exit_time"])

    events = []
    for _, r in t.iterrows():
        events.append((r["entry_time"], 1))
        events.append((r["exit_time"], -1))

    if not events:
        return {}

    ev = pd.DataFrame(events, columns=["time", "delta"]).sort_values("time")
    ev["open_count"] = ev["delta"].cumsum()

    return {
        "max_concurrent_positions": int(ev["open_count"].max()),
        "mean_event_open_count": float(ev["open_count"].mean()),
        "q95_event_open_count": float(ev["open_count"].quantile(0.95)),
        "q99_event_open_count": float(ev["open_count"].quantile(0.99)),
    }

def main():
    out_dir = WORKSPACE / "edge_factory_rel_extreme_oos_robustness_v1" / f"rel_extreme_oos_robust_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    replay_dir, replay_state, df = load_latest_replay()

    if df.empty:
        raise SystemExit("latest replay trades empty")

    df["net_return_bps"] = pd.to_numeric(df["net_return_bps"], errors="coerce")
    df = df.dropna(subset=["net_return_bps"]).copy()

    base = summarize("base_full_replay", df)
    monthly = build_monthly(df)
    splits = time_splits(df)
    topdep = top_symbol_dependency(df)
    costs = cost_stress(df)
    capped = capped_per_signal_time(df)
    concurrency = concurrency_profile(df)

    monthly.to_csv(out_dir / "rel_extreme_monthly_robustness.csv", index=False)
    splits.to_csv(out_dir / "rel_extreme_time_splits.csv", index=False)
    topdep.to_csv(out_dir / "rel_extreme_top_symbol_dependency.csv", index=False)
    costs.to_csv(out_dir / "rel_extreme_cost_stress.csv", index=False)
    capped.to_csv(out_dir / "rel_extreme_signal_cap_stress.csv", index=False)

    # Gate decisions.
    months_with_enough = monthly[monthly["trades"] >= 100].copy()
    positive_month_rate = float((months_with_enough["net_bps_sum"] > 0).mean()) if len(months_with_enough) else 0.0
    weak_month_count = int((months_with_enough["profit_factor"] < 1.10).sum()) if len(months_with_enough) else 0

    last30 = splits[splits["label"] == "last_30d"].iloc[0].to_dict() if "last_30d" in set(splits["label"]) else {}
    last90 = splits[splits["label"] == "last_90d"].iloc[0].to_dict() if "last_90d" in set(splits["label"]) else {}
    oos30 = splits[splits["label"] == "last_30pct_oos"].iloc[0].to_dict() if "last_30pct_oos" in set(splits["label"]) else {}

    cost50 = costs[costs["cost_bps"] == 50].iloc[0].to_dict()
    cost100 = costs[costs["cost_bps"] == 100].iloc[0].to_dict()

    excl_top10 = topdep[topdep["label"] == "exclude_top_10_symbols"].iloc[0].to_dict()
    cap5 = capped[capped["label"] == "cap_5_signals_per_hour"].iloc[0].to_dict() if "cap_5_signals_per_hour" in set(capped["label"]) else {}

    gates = []
    def gate(name, passed, value, threshold):
        gates.append({
            "gate": name,
            "passed": bool(passed),
            "value": value,
            "threshold": threshold,
        })

    gate("base_profit_factor", base["profit_factor"] >= 1.25, base["profit_factor"], ">=1.25")
    gate("base_win_rate", base["win_rate"] >= 0.55, base["win_rate"], ">=0.55")
    gate("symbol_breadth", base["symbols"] >= 50, base["symbols"], ">=50")
    gate("positive_month_rate", positive_month_rate >= 0.80, positive_month_rate, ">=0.80")
    gate("weak_month_count", weak_month_count <= 2, weak_month_count, "<=2")
    gate("last_30pct_oos_pf", float(oos30.get("profit_factor", 0)) >= 1.20, oos30.get("profit_factor"), ">=1.20")
    gate("last_90d_pf", float(last90.get("profit_factor", 0)) >= 1.15, last90.get("profit_factor"), ">=1.15")
    gate("cost_50bps_pf", float(cost50.get("profit_factor", 0)) >= 1.20, cost50.get("profit_factor"), ">=1.20")
    gate("cost_100bps_pf", float(cost100.get("profit_factor", 0)) >= 1.05, cost100.get("profit_factor"), ">=1.05")
    gate("exclude_top10_pf", float(excl_top10.get("profit_factor", 0)) >= 1.15, excl_top10.get("profit_factor"), ">=1.15")
    gate("cap5_per_hour_pf", float(cap5.get("profit_factor", 0)) >= 1.10, cap5.get("profit_factor"), ">=1.10")

    passed_count = sum(1 for g in gates if g["passed"])
    total_gates = len(gates)

    if passed_count == total_gates:
        status = "REL_EXTREME_ROBUSTNESS_PASS_READY_FOR_SHADOW_SPEC_REVIEW"
        next_action = "BUILD_SHADOW_SPEC_BUT_REQUIRE_MANUAL_APPROVAL"
    elif passed_count >= total_gates - 2:
        status = "REL_EXTREME_ROBUSTNESS_WATCHLIST_STRONG_BUT_HAS_WARNINGS"
        next_action = "INVESTIGATE_FAILED_GATES_BEFORE_SHADOW"
    else:
        status = "REL_EXTREME_ROBUSTNESS_FAIL_OR_NEEDS_REWORK"
        next_action = "REJECT_OR_REWORK_RULE"

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "source_replay_dir": str(replay_dir),
        "source_replay_state": replay_state,
        "output_dir": str(out_dir),
        "status": status,
        "base": base,
        "positive_month_rate": positive_month_rate,
        "weak_month_count": weak_month_count,
        "concurrency": concurrency,
        "gates_passed": passed_count,
        "gates_total": total_gates,
        "gates": gates,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": next_action,
        "warnings": [
            "This module does not start paper/live.",
            "This module does not promote the candidate.",
            "High concurrency may make raw uncapped performance unrealistic.",
            "If cap-per-hour stress fails, strategy needs allocator-level throttling before shadow.",
        ],
    }

    write_json(out_dir / "rel_extreme_oos_robustness_state.json", state)
    pd.DataFrame(gates).to_csv(out_dir / "rel_extreme_robustness_gates.csv", index=False)

    print("EDGE FACTORY REL EXTREME OOS ROBUSTNESS v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"source_replay_dir: {replay_dir}")
    print(f"gates: {passed_count}/{total_gates}")
    print(f"positive_month_rate: {positive_month_rate}")
    print(f"weak_month_count: {weak_month_count}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("BASE")
    print("-" * 100)
    print(json.dumps(base, indent=2, ensure_ascii=False))
    print()
    print("CONCURRENCY")
    print("-" * 100)
    print(json.dumps(concurrency, indent=2, ensure_ascii=False))
    print()
    print("GATES")
    print("-" * 100)
    print(pd.DataFrame(gates).to_string(index=False))
    print()
    print("TIME SPLITS")
    print("-" * 100)
    print(splits.to_string(index=False))
    print()
    print("COST STRESS")
    print("-" * 100)
    print(costs.to_string(index=False))
    print()
    print("TOP SYMBOL DEPENDENCY")
    print("-" * 100)
    print(topdep.to_string(index=False))
    print()
    print("CAP PER SIGNAL HOUR")
    print("-" * 100)
    print(capped.to_string(index=False))
    print()
    print(f"State  : {out_dir / 'rel_extreme_oos_robustness_state.json'}")
    print(f"Gates  : {out_dir / 'rel_extreme_robustness_gates.csv'}")
    print(f"Monthly: {out_dir / 'rel_extreme_monthly_robustness.csv'}")

if __name__ == "__main__":
    main()
