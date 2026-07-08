from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


# =============================================================================
# EDGE FACTORY GUARDED ALLOCATOR OPTIMIZER
# =============================================================================
#
# Purpose:
#   Take bad-day findings and test them inside the REAL allocator simulation,
#   not merely as post-allocation removal.
#
# It answers:
#   Which defensive guard is actually worth using?
#
# Inputs:
#   portfolio_family_overlap_validation/normalized_trades.csv
#   edge_factory_master_optimizer/recommended_daily_pnl.csv  (optional, for worst-day reference)
#
# Outputs:
#   edge_factory_guarded_allocator_optimizer/
#       guarded_scenario_summary.csv
#       guarded_best_sim_trades.csv
#       guarded_best_family_pnl.csv
#       guarded_best_daily_pnl.csv
#       guarded_optimizer_report.txt
#
# Usage:
#   python "C:\Users\alike\edge_factory_guarded_allocator_optimizer.py"
# =============================================================================


DEFAULT_BASE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_VALIDATION_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\portfolio_family_overlap_validation"
DEFAULT_MASTER_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_master_optimizer"

BASE_MAX_PER_FAMILY = {
    "old_short": 3,
    "impulse_long": 2,
    "market_relative_short": 3,
    "weak_market_short": 2,
}
BASE_PRIORITY = {
    "old_short": 100,
    "impulse_long": 150,
    "market_relative_short": 70,
    "weak_market_short": 30,
}
BASE_FRACTION = {
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

    x["entry_time"] = pd.to_datetime(x["entry_time"], utc=True, errors="coerce")
    x["exit_time"] = pd.to_datetime(x["exit_time"], utc=True, errors="coerce")

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
    x["family_key"] = x["family_key"].astype(str)
    x["side"] = x["side"].astype(str).str.lower()
    x["entry_date"] = x["entry_time"].dt.strftime("%Y-%m-%d")
    x["entry_month"] = x["entry_time"].dt.strftime("%Y-%m")

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
        raise FileNotFoundError(f"Missing normalized trades: {p}")
    return normalize_trades(safe_read_csv(p))


def filter_trades(
    trades: pd.DataFrame,
    *,
    min_entry_vol_quote: float | None = None,
    max_entry_range_bps: float | None = None,
    exclude_coins: set[str] | None = None,
    family_specific_min_vol: dict[str, float] | None = None,
    family_specific_max_range: dict[str, float] | None = None,
) -> tuple[pd.DataFrame, dict]:
    x = trades.copy()
    before = len(x)
    removed = {}

    if exclude_coins:
        mask = ~x["coin"].isin({c.upper() for c in exclude_coins})
        removed["exclude_coins"] = int((~mask).sum())
        x = x.loc[mask].copy()

    if min_entry_vol_quote is not None and "entry_vol_quote" in x.columns:
        mask = x["entry_vol_quote"] >= min_entry_vol_quote
        removed[f"min_entry_vol_quote_{min_entry_vol_quote}"] = int((~mask).sum())
        x = x.loc[mask].copy()

    if max_entry_range_bps is not None and "entry_range_bps" in x.columns:
        mask = x["entry_range_bps"] <= max_entry_range_bps
        removed[f"max_entry_range_bps_{max_entry_range_bps}"] = int((~mask).sum())
        x = x.loc[mask].copy()

    if family_specific_min_vol and "entry_vol_quote" in x.columns:
        for fam, th in family_specific_min_vol.items():
            mask = ~((x["family_key"] == fam) & (x["entry_vol_quote"] < th))
            removed[f"{fam}_min_vol_{th}"] = int((~mask).sum())
            x = x.loc[mask].copy()

    if family_specific_max_range and "entry_range_bps" in x.columns:
        for fam, th in family_specific_max_range.items():
            mask = ~((x["family_key"] == fam) & (x["entry_range_bps"] > th))
            removed[f"{fam}_max_range_{th}"] = int((~mask).sum())
            x = x.loc[mask].copy()

    removed["before"] = before
    removed["after"] = len(x)
    removed["total_removed"] = before - len(x)
    return x.reset_index(drop=True), removed


def simulate(
    trades: pd.DataFrame,
    *,
    name: str,
    start_equity: float,
    global_max_positions: int = 6,
    max_short_positions: int = 5,
    max_long_positions: int = 2,
    max_per_family: dict[str, int] | None = None,
    family_priority: dict[str, int] | None = None,
    capital_fraction: dict[str, float] | None = None,
    exclude_families: set[str] | None = None,
    weak_market_backup_only: bool = True,
    max_entries_per_day: int | None = None,
    max_short_entries_per_day: int | None = None,
    max_family_entries_per_day: dict[str, int] | None = None,
    daily_loss_stop_pct: float | None = None,
    extra_cost_bps: float = 0.0,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    max_per_family = max_per_family or BASE_MAX_PER_FAMILY
    family_priority = family_priority or BASE_PRIORITY
    capital_fraction = capital_fraction or BASE_FRACTION

    x = trades.copy()
    if exclude_families:
        x = x.loc[~x["family_key"].isin(exclude_families)].copy()

    x["net_ret_adj"] = pd.to_numeric(x["net_ret"], errors="coerce") - extra_cost_bps / 10000.0
    x["priority"] = x["family_key"].map(lambda f: int(family_priority.get(str(f), 0)))
    x["vol_priority"] = pd.to_numeric(x.get("entry_vol_quote", pd.Series([0] * len(x))), errors="coerce").fillna(0.0)
    x = x.sort_values(["entry_time", "priority", "vol_priority"], ascending=[True, False, False]).reset_index(drop=True)

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
    curve_rows = [{"time": x["entry_time"].min() if len(x) else pd.NaT, "equity": equity, "open_positions": 0, "event": "start"}]

    daily_entry_count: dict[str, int] = {}
    daily_short_count: dict[str, int] = {}
    daily_family_count: dict[tuple[str, str], int] = {}
    daily_realized_pnl: dict[str, float] = {}

    def open_counts():
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
        row = x.loc[tid]
        fam = str(row["family_key"])
        coin = str(row["coin"])
        side = str(row["side"]).lower()
        entry_date = str(row["entry_date"])
        event_date = pd.Timestamp(ts).strftime("%Y-%m-%d")

        if typ == 0:
            if tid not in open_pos:
                continue
            pos = open_pos.pop(tid)
            pnl = pos["notional"] * float(row["net_ret_adj"])
            equity += pnl
            daily_realized_pnl[event_date] = daily_realized_pnl.get(event_date, 0.0) + pnl
            x.loc[tid, "sim_pnl"] = pnl
            x.loc[tid, "equity_after_exit"] = equity
            curve_rows.append({"time": ts, "equity": equity, "open_positions": len(open_pos), "event": f"exit_{fam}_{coin}"})
            continue

        global_n, short_n, long_n, fam_counts, open_coins = open_counts()

        reason = ""
        if coin in open_coins:
            reason = "same_coin_overlap_global"
        elif global_n >= global_max_positions:
            reason = "global_max_positions"
        elif side == "short" and short_n >= max_short_positions:
            reason = "max_short_positions"
        elif side == "long" and long_n >= max_long_positions:
            reason = "max_long_positions"
        elif fam_counts.get(fam, 0) >= int(max_per_family.get(fam, 999999)):
            reason = "max_per_family"
        elif fam == "weak_market_short" and weak_market_backup_only and fam_counts.get("market_relative_short", 0) > 0:
            reason = "weak_market_backup_only_market_relative_active"
        elif max_entries_per_day is not None and daily_entry_count.get(entry_date, 0) >= max_entries_per_day:
            reason = "max_entries_per_day"
        elif max_short_entries_per_day is not None and side == "short" and daily_short_count.get(entry_date, 0) >= max_short_entries_per_day:
            reason = "max_short_entries_per_day"
        elif max_family_entries_per_day and fam in max_family_entries_per_day and daily_family_count.get((entry_date, fam), 0) >= max_family_entries_per_day[fam]:
            reason = "max_family_entries_per_day"
        elif daily_loss_stop_pct is not None and daily_realized_pnl.get(entry_date, 0.0) <= -abs(daily_loss_stop_pct) * start_equity:
            reason = "daily_loss_stop"

        if reason:
            x.loc[tid, "reject_reason"] = reason
            continue

        notional = equity * float(capital_fraction.get(fam, 0.05))
        x.loc[tid, "accepted"] = True
        x.loc[tid, "sim_notional"] = notional
        open_pos[tid] = {"family_key": fam, "coin": coin, "side": side, "notional": notional}

        daily_entry_count[entry_date] = daily_entry_count.get(entry_date, 0) + 1
        if side == "short":
            daily_short_count[entry_date] = daily_short_count.get(entry_date, 0) + 1
        daily_family_count[(entry_date, fam)] = daily_family_count.get((entry_date, fam), 0) + 1

        curve_rows.append({"time": ts, "equity": equity, "open_positions": len(open_pos), "event": f"entry_{fam}_{coin}"})

    curve = pd.DataFrame(curve_rows).sort_values("time").reset_index(drop=True)
    sim = x.copy()
    acc = sim[sim["accepted"]].copy()
    rets = pd.to_numeric(acc["net_ret_adj"], errors="coerce").dropna()
    final = float(curve["equity"].iloc[-1]) if len(curve) else start_equity

    daily = daily_pnl(sim)
    worst_day_pnl = float(daily["pnl"].min()) if not daily.empty else 0.0
    worst_5_day_sum = float(daily.head(5)["pnl"].sum()) if not daily.empty else 0.0
    worst_30_day_sum = float(daily.head(30)["pnl"].sum()) if not daily.empty else 0.0

    stats = {
        "scenario": name,
        "input_trades": int(len(x)),
        "accepted_trades": int(len(acc)),
        "rejected_trades": int((~sim["accepted"]).sum()) if len(sim) else 0,
        "final_equity": final,
        "portfolio_total_return": float(final / start_equity - 1.0),
        "portfolio_max_drawdown": max_drawdown(curve["equity"].to_numpy(float)) if len(curve) else 0.0,
        "max_open_seen": int(curve["open_positions"].max()) if len(curve) else 0,
        "profit_factor": profit_factor(rets),
        "win_rate": float((rets > 0).mean()) if len(rets) else np.nan,
        "avg_net_ret": float(rets.mean()) if len(rets) else np.nan,
        "median_net_ret": float(rets.median()) if len(rets) else np.nan,
        "worst_trade": float(rets.min()) if len(rets) else np.nan,
        "best_trade": float(rets.max()) if len(rets) else np.nan,
        "worst_day_pnl": worst_day_pnl,
        "worst_5_day_sum": worst_5_day_sum,
        "worst_30_day_sum": worst_30_day_sum,
        "global_max_positions": global_max_positions,
        "max_short_positions": max_short_positions,
        "max_long_positions": max_long_positions,
        "max_entries_per_day": "" if max_entries_per_day is None else max_entries_per_day,
        "max_short_entries_per_day": "" if max_short_entries_per_day is None else max_short_entries_per_day,
        "daily_loss_stop_pct": "" if daily_loss_stop_pct is None else daily_loss_stop_pct,
        "max_family_entries_per_day": json.dumps(max_family_entries_per_day or {}, sort_keys=True),
        "max_per_family": json.dumps(max_per_family, sort_keys=True),
        "family_priority": json.dumps(family_priority, sort_keys=True),
        "capital_fraction": json.dumps(capital_fraction, sort_keys=True),
    }
    return stats, curve, sim


def family_pnl(sim: pd.DataFrame) -> pd.DataFrame:
    if sim.empty:
        return pd.DataFrame()
    acc = sim[sim["accepted"]].copy()
    if acc.empty:
        return pd.DataFrame()
    return (
        acc.groupby("family_key")
        .agg(
            trades=("trade_id", "count"),
            pnl=("sim_pnl", "sum"),
            avg_ret=("net_ret_adj", "mean"),
            median_ret=("net_ret_adj", "median"),
            win_rate=("net_ret_adj", lambda s: (s > 0).mean()),
            worst_trade=("net_ret_adj", "min"),
            best_trade=("net_ret_adj", "max"),
        )
        .reset_index()
        .sort_values("pnl", ascending=False)
    )


def daily_pnl(sim: pd.DataFrame) -> pd.DataFrame:
    if sim.empty:
        return pd.DataFrame()
    acc = sim[sim["accepted"]].copy()
    if acc.empty:
        return pd.DataFrame()
    acc["date"] = acc["entry_time"].dt.strftime("%Y-%m-%d")
    return (
        acc.groupby("date")
        .agg(
            trades=("trade_id", "count"),
            pnl=("sim_pnl", "sum"),
            avg_ret=("net_ret_adj", "mean"),
            worst_trade=("net_ret_adj", "min"),
        )
        .reset_index()
        .sort_values("pnl")
    )


def run_grid(trades: pd.DataFrame, args) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    rows = []
    curves = {}
    sims = {}

    def add(name: str, filtered: pd.DataFrame | None = None, filter_meta: dict | None = None, **kwargs):
        t = filtered if filtered is not None else trades
        st, curve, sim = simulate(t, name=name, start_equity=args.start_equity, exclude_families={"session_short"}, **kwargs)
        st["filter_meta"] = json.dumps(filter_meta or {}, sort_keys=True)
        rows.append(st)
        curves[name] = curve
        sims[name] = sim

    # Base master.
    add("MASTER_RECOMMENDED_BASE")

    # Actual allocator guards from bad-day investigator.
    for n in [2, 3, 4, 5]:
        add(f"OLD_DAILY_CAP_{n}", max_family_entries_per_day={"old_short": n})
    for n in [1, 2, 3]:
        add(f"MARKET_RELATIVE_DAILY_CAP_{n}", max_family_entries_per_day={"market_relative_short": n})
    for n in [3, 4, 5, 6, 8, 10]:
        add(f"SHORT_DAILY_CAP_{n}", max_short_entries_per_day=n)

    # Combos.
    add("GUARD_OLD4_MARKET2", max_family_entries_per_day={"old_short": 4, "market_relative_short": 2})
    add("GUARD_OLD4_MARKET1", max_family_entries_per_day={"old_short": 4, "market_relative_short": 1})
    add("GUARD_OLD3_MARKET2", max_family_entries_per_day={"old_short": 3, "market_relative_short": 2})
    add("GUARD_OLD4_SHORT6", max_family_entries_per_day={"old_short": 4}, max_short_entries_per_day=6)
    add("GUARD_OLD3_SHORT6", max_family_entries_per_day={"old_short": 3}, max_short_entries_per_day=6)
    add("GUARD_OLD4_MARKET2_SHORT6", max_family_entries_per_day={"old_short": 4, "market_relative_short": 2}, max_short_entries_per_day=6)

    # Liquidity/range filters as pre-filter, not post-removal.
    for th in [250_000, 500_000, 1_000_000, 2_000_000]:
        ft, meta = filter_trades(trades, min_entry_vol_quote=th)
        add(f"FILTER_MIN_VOL_{int(th)}", filtered=ft, filter_meta=meta)

    for th in [300, 500, 700, 1000, 1500]:
        ft, meta = filter_trades(trades, max_entry_range_bps=th)
        add(f"FILTER_MAX_RANGE_{int(th)}", filtered=ft, filter_meta=meta)

    # Family-specific filters, less destructive than global.
    for th in [250_000, 500_000, 1_000_000]:
        ft, meta = filter_trades(trades, family_specific_min_vol={"old_short": th, "market_relative_short": th})
        add(f"FILTER_SHORT_FAMS_MIN_VOL_{int(th)}", filtered=ft, filter_meta=meta)

    for th in [300, 500, 700, 1000]:
        ft, meta = filter_trades(trades, family_specific_max_range={"old_short": th, "market_relative_short": th})
        add(f"FILTER_SHORT_FAMS_MAX_RANGE_{int(th)}", filtered=ft, filter_meta=meta)

    # Coin blacklist research only. These are overfit-prone; use only if they survive OOS later.
    worst_coin_sets = {
        "BLACKLIST_TOP3_BAD_COINS": {"RAVE", "RLS", "CORE"},
        "BLACKLIST_TOP5_BAD_COINS": {"RAVE", "RLS", "CORE", "ENSO", "NOT"},
        "BLACKLIST_TOP10_BAD_COINS": {"RAVE", "RLS", "CORE", "ENSO", "NOT", "BEAT", "ESP", "STABLE", "ONT", "JELLYJELLY"},
    }
    for name, coins in worst_coin_sets.items():
        ft, meta = filter_trades(trades, exclude_coins=coins)
        add(name, filtered=ft, filter_meta=meta)

    # Defensive capital sizing research.
    frac_low_market = {**BASE_FRACTION, "market_relative_short": 0.025}
    frac_low_old = {**BASE_FRACTION, "old_short": 0.04}
    frac_low_shorts = {**BASE_FRACTION, "old_short": 0.04, "market_relative_short": 0.025, "weak_market_short": 0.015}
    add("SIZE_MARKET_RELATIVE_HALF", capital_fraction=frac_low_market)
    add("SIZE_OLD_4PCT", capital_fraction=frac_low_old)
    add("SIZE_SHORTS_DEFENSIVE", capital_fraction=frac_low_shorts)

    df = pd.DataFrame(rows)
    # Raw utility: prefer high return but penalize drawdown/worst days/too many trades.
    df["guard_utility"] = (
        df["portfolio_total_return"].astype(float)
        + df["profit_factor"].fillna(1.0).astype(float) * 0.4
        + df["portfolio_max_drawdown"].astype(float) * 4.0
        + (df["worst_day_pnl"].astype(float) / args.start_equity) * 1.5
        + (df["worst_30_day_sum"].astype(float) / args.start_equity) * 0.25
        - (df["max_open_seen"].astype(float) - 6).clip(lower=0) * 0.3
    )
    df = df.sort_values("guard_utility", ascending=False).reset_index(drop=True)
    return df, curves, sims


def main() -> None:
    ap = argparse.ArgumentParser(description="Retest bad-day guard candidates inside allocator simulation.")
    ap.add_argument("--base_dir", default=DEFAULT_BASE)
    ap.add_argument("--validation_dir", default=DEFAULT_VALIDATION_DIR)
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--start_equity", type=float, default=1000.0)
    args = ap.parse_args()

    base = Path(args.base_dir)
    out = Path(args.out_dir) if args.out_dir else base / "edge_factory_guarded_allocator_optimizer"
    out.mkdir(parents=True, exist_ok=True)

    trades = load_trades(args.validation_dir)
    summary, curves, sims = run_grid(trades, args)
    summary.to_csv(out / "guarded_scenario_summary.csv", index=False)

    best = str(summary.iloc[0]["scenario"])
    sims[best].to_csv(out / "guarded_best_sim_trades.csv", index=False)
    curves[best].to_csv(out / "guarded_best_equity_curve.csv", index=False)
    family_pnl(sims[best]).to_csv(out / "guarded_best_family_pnl.csv", index=False)
    daily_pnl(sims[best]).to_csv(out / "guarded_best_daily_pnl.csv", index=False)

    base_name = "MASTER_RECOMMENDED_BASE"
    if base_name in sims:
        sims[base_name].to_csv(out / "base_sim_trades.csv", index=False)
        family_pnl(sims[base_name]).to_csv(out / "base_family_pnl.csv", index=False)
        daily_pnl(sims[base_name]).to_csv(out / "base_daily_pnl.csv", index=False)

    cols = [
        "scenario", "guard_utility", "accepted_trades", "final_equity", "portfolio_total_return",
        "portfolio_max_drawdown", "profit_factor", "win_rate", "avg_net_ret",
        "worst_trade", "worst_day_pnl", "worst_5_day_sum", "worst_30_day_sum",
        "max_open_seen", "max_short_entries_per_day", "max_family_entries_per_day", "filter_meta",
    ]

    report = []
    report.append("EDGE FACTORY GUARDED ALLOCATOR OPTIMIZER REPORT")
    report.append("=" * 130)
    report.append(f"input_trades: {len(trades)}")
    report.append(f"out_dir: {out}")
    report.append("")
    report.append("TOP SCENARIOS BY GUARD UTILITY")
    report.append("-" * 130)
    report.append(summary[[c for c in cols if c in summary.columns]].head(60).to_string(index=False))
    report.append("")
    report.append(f"BEST SCENARIO: {best}")
    report.append("-" * 130)
    report.append("BEST FAMILY PNL")
    report.append(family_pnl(sims[best]).to_string(index=False))
    report.append("")
    report.append("BEST WORST DAYS")
    report.append(daily_pnl(sims[best]).head(30).to_string(index=False))
    if base_name in sims:
        report.append("")
        report.append("BASE FAMILY PNL")
        report.append("-" * 130)
        report.append(family_pnl(sims[base_name]).to_string(index=False))
        report.append("")
        report.append("BASE WORST DAYS")
        report.append(daily_pnl(sims[base_name]).head(30).to_string(index=False))

    (out / "GUARDED_ALLOCATOR_REPORT.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))


if __name__ == "__main__":
    main()
