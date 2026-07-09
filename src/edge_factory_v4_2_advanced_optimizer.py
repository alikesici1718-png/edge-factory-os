"""
Advanced optimizer (v4.2) that reads family trade CSV files from a base directory, computes per-strategy performance metrics (profit factor, max drawdown, Sharpe-like ratios), applies family-level position limits and priority weights, and outputs an optimised portfolio allocation JSON.
Accepts command-line arguments for base directory, family config, max-per-family limits, and validation directory; outputs allocation results to a JSON file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_BASE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_VALIDATION_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\portfolio_family_overlap_validation"

DEFAULT_MAX_PER_FAMILY = {
    "old_short": 3,
    "impulse_long": 2,
    "market_relative_short": 3,
    "weak_market_short": 1,
}
DEFAULT_PRIORITY = {
    "old_short": 100,
    "impulse_long": 90,
    "market_relative_short": 70,
    "weak_market_short": 30,
}
DEFAULT_FRACTION = {
    "old_short": 0.05,
    "impulse_long": 0.05,
    "market_relative_short": 0.05,
    "weak_market_short": 0.025,
}


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def profit_factor(rets: pd.Series) -> float:
    r = pd.to_numeric(rets, errors="coerce").dropna()
    if r.empty:
        return np.nan
    wins = r[r > 0].sum()
    losses = -r[r < 0].sum()
    return np.nan if losses <= 0 else float(wins / losses)


def max_drawdown(eq: np.ndarray) -> float:
    if len(eq) == 0:
        return 0.0
    eq = np.asarray(eq, dtype=float)
    peak = np.maximum.accumulate(eq)
    return float((eq / peak - 1.0).min())


def normalize_trades(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    if x.empty:
        return x

    for c in ["entry_time", "exit_time"]:
        x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")

    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "coin" not in x.columns:
        x["coin"] = ""

    if "side" not in x.columns:
        x["side"] = np.where(x["family_key"].astype(str).str.contains("long"), "long", "short")

    if "entry_vol_quote" not in x.columns:
        x["entry_vol_quote"] = 0.0

    for c in ["net_ret", "entry_vol_quote", "entry_range_bps", "coin_ret_bps", "mkt_ret_bps", "rel_ret_bps"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    x = x.dropna(subset=["family_key", "coin", "side", "entry_time", "exit_time", "net_ret"]).copy()
    x = x.loc[x["exit_time"] > x["entry_time"]].copy()
    x["coin"] = x["coin"].astype(str).str.upper()

    if "trade_id" not in x.columns:
        x["trade_id"] = (
            x["family_key"].astype(str) + "|" +
            x["coin"].astype(str) + "|" +
            x["entry_time"].astype(str) + "|" +
            x["exit_time"].astype(str) + "|" +
            x.index.astype(str)
        )

    return x.reset_index(drop=True)


def load_trades(validation_dir: str) -> pd.DataFrame:
    p = Path(validation_dir) / "normalized_trades.csv"
    if not p.exists():
        raise FileNotFoundError(
            f"normalized_trades.csv yok: {p}\n"
            "Önce portfolio_family_overlap_validator.py çalıştırılmış olmalı."
        )
    return normalize_trades(safe_read_csv(p))


def simulate(
    trades: pd.DataFrame,
    *,
    name: str,
    start_equity: float,
    global_max: int,
    short_max: int,
    long_max: int,
    max_per_family: dict[str, int],
    priority: dict[str, int],
    fraction: dict[str, float],
    exclude_families: set[str] | None = None,
    weak_backup: bool = True,
    extra_cost_bps: float = 0.0,
    reserve_impulse_slot: bool = False,
    protect_impulse_when_pending_same_bar: bool = False,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    x = trades.copy()
    if exclude_families:
        x = x.loc[~x["family_key"].isin(exclude_families)].copy()

    # v4.1 removed session_short; default scenarios will exclude it.
    x["net_ret_adj"] = pd.to_numeric(x["net_ret"], errors="coerce") - extra_cost_bps / 10000.0
    x["priority"] = x["family_key"].map(lambda f: int(priority.get(str(f), 0)))
    x["vol_priority"] = pd.to_numeric(x["entry_vol_quote"], errors="coerce").fillna(0.0)

    # Same timestamp allocation: priority first, then liquidity.
    x = x.sort_values(["entry_time", "priority", "vol_priority"], ascending=[True, False, False]).reset_index(drop=True)

    # For impulse protection: know whether an impulse signal exists at same timestamp.
    same_bar_impulse_times = set(
        x.loc[x["family_key"].astype(str) == "impulse_long", "entry_time"].dropna().astype(str).tolist()
    )

    events = []
    for tid, r in x.iterrows():
        events.append((r["exit_time"], 0, tid))
        events.append((r["entry_time"], 1, tid))
    events.sort(key=lambda z: (z[0], z[1], z[2]))

    x["accepted"] = False
    x["reject_reason"] = ""
    x["sim_notional"] = np.nan
    x["sim_pnl"] = np.nan
    x["equity_after_exit"] = np.nan

    equity = float(start_equity)
    open_pos: dict[int, dict] = {}
    curve_rows = [{"time": x["entry_time"].min(), "equity": equity, "open_positions": 0, "event": "start"}]

    def counts():
        fam = {}
        coins = set()
        short_n = 0
        long_n = 0
        for p in open_pos.values():
            fam[p["family_key"]] = fam.get(p["family_key"], 0) + 1
            coins.add(p["coin"])
            short_n += int(p["side"] == "short")
            long_n += int(p["side"] == "long")
        return len(open_pos), short_n, long_n, fam, coins

    for ts, typ, tid in events:
        r = x.loc[tid]
        fam = str(r["family_key"])
        coin = str(r["coin"])
        side = str(r["side"]).lower()

        if typ == 0:
            if tid not in open_pos:
                continue
            pos = open_pos.pop(tid)
            pnl = pos["notional"] * float(r["net_ret_adj"])
            equity += pnl
            x.loc[tid, "sim_pnl"] = pnl
            x.loc[tid, "equity_after_exit"] = equity
            curve_rows.append({"time": ts, "equity": equity, "open_positions": len(open_pos), "event": f"exit_{fam}_{coin}"})
            continue

        global_n, short_n, long_n, fam_counts, open_coins = counts()

        reason = ""
        if coin in open_coins:
            reason = "same_coin_overlap_global"
        elif global_n >= global_max:
            reason = "global_max_positions"
        elif side == "short" and short_n >= short_max:
            reason = "max_short_positions"
        elif side == "long" and long_n >= long_max:
            reason = "max_long_positions"
        elif fam_counts.get(fam, 0) >= int(max_per_family.get(fam, 999999)):
            reason = "max_per_family"
        elif fam == "weak_market_short" and weak_backup and fam_counts.get("market_relative_short", 0) > 0:
            reason = "weak_market_backup_only_market_relative_active"
        elif reserve_impulse_slot and side == "short" and long_n == 0 and global_n >= global_max - 1:
            reason = "reserve_impulse_slot"
        elif protect_impulse_when_pending_same_bar and side == "short" and str(r["entry_time"]) in same_bar_impulse_times:
            reason = "same_bar_impulse_protection"

        if reason:
            x.loc[tid, "reject_reason"] = reason
            continue

        notional = equity * float(fraction.get(fam, 0.05))
        x.loc[tid, "accepted"] = True
        x.loc[tid, "sim_notional"] = notional
        open_pos[tid] = {"family_key": fam, "coin": coin, "side": side, "notional": notional}
        curve_rows.append({"time": ts, "equity": equity, "open_positions": len(open_pos), "event": f"entry_{fam}_{coin}"})

    curve = pd.DataFrame(curve_rows).sort_values("time").reset_index(drop=True)
    sim = x.copy()
    acc = sim.loc[sim["accepted"]].copy()
    rets = pd.to_numeric(acc["net_ret_adj"], errors="coerce").dropna()
    final = float(curve["equity"].iloc[-1]) if len(curve) else start_equity

    stats = {
        "scenario": name,
        "input_trades": int(len(x)),
        "accepted_trades": int(len(acc)),
        "rejected_trades": int((~sim["accepted"]).sum()),
        "final_equity": final,
        "portfolio_total_return": float(final / start_equity - 1.0),
        "portfolio_max_drawdown": max_drawdown(curve["equity"].to_numpy(float)),
        "max_open_seen": int(curve["open_positions"].max()) if len(curve) else 0,
        "profit_factor": profit_factor(rets),
        "win_rate": float((rets > 0).mean()) if len(rets) else np.nan,
        "avg_net_ret": float(rets.mean()) if len(rets) else np.nan,
        "median_net_ret": float(rets.median()) if len(rets) else np.nan,
        "worst_trade": float(rets.min()) if len(rets) else np.nan,
        "best_trade": float(rets.max()) if len(rets) else np.nan,
        "global_max": global_max,
        "short_max": short_max,
        "long_max": long_max,
        "weak_backup": weak_backup,
        "reserve_impulse_slot": reserve_impulse_slot,
        "protect_impulse_same_bar": protect_impulse_when_pending_same_bar,
        "extra_cost_bps": extra_cost_bps,
        "max_per_family": json.dumps(max_per_family, sort_keys=True),
        "priority": json.dumps(priority, sort_keys=True),
    }
    return stats, curve, sim


def run_grid(trades: pd.DataFrame, args) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    scenarios = []
    curves = {}
    sims = {}

    def add(
        name,
        *,
        global_max=6,
        short_max=5,
        long_max=2,
        maxfam=None,
        priority=None,
        fraction=None,
        weak_backup=True,
        reserve_impulse=False,
        same_bar_impulse=False,
        cost=0.0,
    ):
        st, curve, sim = simulate(
            trades,
            name=name,
            start_equity=args.start_equity,
            global_max=global_max,
            short_max=short_max,
            long_max=long_max,
            max_per_family=maxfam or DEFAULT_MAX_PER_FAMILY,
            priority=priority or DEFAULT_PRIORITY,
            fraction=fraction or DEFAULT_FRACTION,
            exclude_families={"session_short"},
            weak_backup=weak_backup,
            reserve_impulse_slot=reserve_impulse,
            protect_impulse_when_pending_same_bar=same_bar_impulse,
            extra_cost_bps=cost,
        )
        scenarios.append(st)
        curves[name] = curve
        sims[name] = sim

    # Current upper candidate.
    add("v4_1_no_session_base")

    # Slot/risk variants.
    for g in [4, 5, 6, 7]:
        add(f"global_max_{g}", global_max=g, short_max=min(5, g))
    for s in [3, 4, 5]:
        add(f"short_max_{s}", short_max=s)
    for m in [1, 2, 3, 4]:
        add(f"market_relative_max_{m}", maxfam={**DEFAULT_MAX_PER_FAMILY, "market_relative_short": m})
    for o in [2, 3, 4]:
        add(f"old_short_max_{o}", maxfam={**DEFAULT_MAX_PER_FAMILY, "old_short": o})

    # Impulse protection / priority variants.
    add("impulse_priority_120", priority={**DEFAULT_PRIORITY, "impulse_long": 120})
    add("impulse_priority_150", priority={**DEFAULT_PRIORITY, "impulse_long": 150})
    add("reserve_impulse_slot", reserve_impulse=True)
    add("same_bar_impulse_protection", same_bar_impulse=True)
    add("impulse_top_plus_reserve", priority={**DEFAULT_PRIORITY, "impulse_long": 150}, reserve_impulse=True)
    add("impulse_top_same_bar_protect", priority={**DEFAULT_PRIORITY, "impulse_long": 150}, same_bar_impulse=True)

    # Weak-market variants.
    add("weak_not_backup", weak_backup=False)
    add("weak_disabled", maxfam={**DEFAULT_MAX_PER_FAMILY, "weak_market_short": 0})
    add("weak_max_2_backup", maxfam={**DEFAULT_MAX_PER_FAMILY, "weak_market_short": 2})

    # Cost stress.
    for c in [25, 50, 75, 100]:
        add(f"cost_plus_{int(c)}bps", cost=c)

    # Combined candidates.
    add("candidate_A_impulse_top_market3", priority={**DEFAULT_PRIORITY, "impulse_long": 150})
    add("candidate_B_impulse_top_market2", priority={**DEFAULT_PRIORITY, "impulse_long": 150}, maxfam={**DEFAULT_MAX_PER_FAMILY, "market_relative_short": 2})
    add("candidate_C_no_weak_impulse_top", priority={**DEFAULT_PRIORITY, "impulse_long": 150}, maxfam={**DEFAULT_MAX_PER_FAMILY, "weak_market_short": 0})
    add("candidate_D_short4_market3", short_max=4)
    add("candidate_E_global5_market3", global_max=5, short_max=4)
    add("candidate_F_old3_market3_impulse150_weak0", priority={**DEFAULT_PRIORITY, "impulse_long": 150}, maxfam={**DEFAULT_MAX_PER_FAMILY, "weak_market_short": 0})

    df = pd.DataFrame(scenarios)
    df = df.sort_values(["portfolio_total_return", "portfolio_max_drawdown"], ascending=[False, False]).reset_index(drop=True)
    return df, curves, sims


def diagnostics(sim: pd.DataFrame) -> dict[str, pd.DataFrame]:
    out = {}
    if sim.empty:
        return out
    acc = sim.loc[sim["accepted"]].copy()
    if acc.empty:
        return out
    out["family_pnl"] = (
        acc.groupby("family_key")
        .agg(
            trades=("trade_id", "count"),
            pnl=("sim_pnl", "sum"),
            avg_ret=("net_ret_adj", "mean"),
            median_ret=("net_ret_adj", "median"),
            win_rate=("net_ret_adj", lambda s: (s > 0).mean()),
            worst_trade=("net_ret_adj", "min"),
        )
        .reset_index()
        .sort_values("pnl", ascending=False)
    )
    rej = sim.loc[~sim["accepted"]].copy()
    out["reject_summary"] = (
        rej.groupby(["family_key", "reject_reason"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    acc["date"] = acc["entry_time"].dt.strftime("%Y-%m-%d")
    out["worst_days"] = (
        acc.groupby("date")
        .agg(trades=("trade_id", "count"), pnl=("sim_pnl", "sum"), avg_ret=("net_ret_adj", "mean"))
        .reset_index()
        .sort_values("pnl")
        .head(50)
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Advanced v4.2 optimizer for no-session edge factory allocator.")
    ap.add_argument("--validation_dir", default=DEFAULT_VALIDATION_DIR)
    ap.add_argument("--base_dir", default=DEFAULT_BASE)
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--start_equity", type=float, default=1000.0)
    args = ap.parse_args()

    base = Path(args.base_dir)
    out = Path(args.out_dir) if args.out_dir else base / "edge_factory_v4_2_advanced_optimizer"
    out.mkdir(parents=True, exist_ok=True)

    trades = load_trades(args.validation_dir)
    scenarios, curves, sims = run_grid(trades, args)
    scenarios.to_csv(out / "v4_2_scenario_summary.csv", index=False)

    best = str(scenarios.iloc[0]["scenario"])
    curves[best].to_csv(out / "best_equity_curve.csv", index=False)
    sims[best].to_csv(out / "best_sim_trades.csv", index=False)

    base_name = "v4_1_no_session_base"
    if base_name in sims:
        sims[base_name].to_csv(out / "v4_1_base_sim_trades.csv", index=False)

    diag = diagnostics(sims[best])
    for name, df in diag.items():
        df.to_csv(out / f"best_{name}.csv", index=False)

    base_diag = diagnostics(sims[base_name]) if base_name in sims else {}
    for name, df in base_diag.items():
        df.to_csv(out / f"v4_1_base_{name}.csv", index=False)

    cols = [
        "scenario", "accepted_trades", "final_equity", "portfolio_total_return",
        "portfolio_max_drawdown", "profit_factor", "win_rate", "avg_net_ret",
        "worst_trade", "max_open_seen", "global_max", "short_max",
        "reserve_impulse_slot", "protect_impulse_same_bar", "extra_cost_bps"
    ]

    report = []
    report.append("EDGE FACTORY v4.2 ADVANCED OPTIMIZER REPORT")
    report.append("=" * 110)
    report.append(f"input_trades: {len(trades)}")
    report.append(f"out_dir: {out}")
    report.append("")
    report.append("TOP SCENARIOS")
    report.append("-" * 110)
    report.append(scenarios[cols].head(40).to_string(index=False))
    report.append("")
    report.append(f"BEST SCENARIO: {best}")
    report.append("-" * 110)
    if diag:
        report.append("BEST FAMILY PNL")
        report.append(diag["family_pnl"].to_string(index=False))
        report.append("")
        report.append("BEST REJECT SUMMARY")
        report.append(diag["reject_summary"].head(40).to_string(index=False))
        report.append("")
        report.append("BEST WORST DAYS")
        report.append(diag["worst_days"].head(30).to_string(index=False))
    report.append("")
    report.append("BASE v4.1 NO SESSION FAMILY PNL")
    report.append("-" * 110)
    if base_diag:
        report.append(base_diag["family_pnl"].to_string(index=False))

    (out / "v4_2_optimizer_report.txt").write_text("\n".join(report), encoding="utf-8")

    print("\n" + "\n".join(report))


if __name__ == "__main__":
    main()
