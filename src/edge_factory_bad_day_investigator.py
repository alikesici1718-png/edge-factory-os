from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


DEFAULT_BASE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_MASTER_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_master_optimizer"


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def profit_factor(s: pd.Series) -> float:
    r = pd.to_numeric(s, errors="coerce").dropna()
    if r.empty:
        return np.nan
    wins = r[r > 0].sum()
    losses = -r[r < 0].sum()
    return np.nan if losses <= 0 else float(wins / losses)


def normalize_sim(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    for c in ["entry_time", "exit_time"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")
    for c in ["net_ret_adj", "net_ret", "sim_pnl", "entry_vol_quote", "entry_range_bps", "coin_ret_bps", "mkt_ret_bps", "rel_ret_bps", "priority", "vol_priority"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")
    if "net_ret_adj" not in x.columns and "net_ret" in x.columns:
        x["net_ret_adj"] = x["net_ret"]
    if "date" not in x.columns:
        x["date"] = x["entry_time"].dt.strftime("%Y-%m-%d")
    if "accepted" in x.columns:
        x["accepted"] = x["accepted"].astype(str).str.lower().isin(["true", "1", "yes"])
    else:
        x["accepted"] = True
    if "trade_id" not in x.columns:
        x["trade_id"] = x["family_key"].astype(str) + "|" + x["coin"].astype(str) + "|" + x.index.astype(str)
    return x


def summarize_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if df.empty or group_col not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(group_col)
        .agg(
            trades=("trade_id", "count"),
            pnl=("sim_pnl", "sum"),
            avg_ret=("net_ret_adj", "mean"),
            median_ret=("net_ret_adj", "median"),
            win_rate=("net_ret_adj", lambda s: (s > 0).mean()),
            worst_trade=("net_ret_adj", "min"),
            best_trade=("net_ret_adj", "max"),
            pf=("net_ret_adj", profit_factor),
        )
        .reset_index()
        .sort_values("pnl")
    )


def feature_compare(good: pd.DataFrame, bad: pd.DataFrame) -> pd.DataFrame:
    rows = []
    features = ["entry_vol_quote", "entry_range_bps", "coin_ret_bps", "mkt_ret_bps", "rel_ret_bps", "priority", "vol_priority"]
    for f in features:
        if f not in good.columns or f not in bad.columns:
            continue
        gs = pd.to_numeric(good[f], errors="coerce").dropna()
        bs = pd.to_numeric(bad[f], errors="coerce").dropna()
        if len(gs) < 20 or len(bs) < 20:
            continue
        rows.append({
            "feature": f,
            "bad_mean": float(bs.mean()),
            "good_mean": float(gs.mean()),
            "bad_median": float(bs.median()),
            "good_median": float(gs.median()),
            "bad_p90": float(bs.quantile(0.90)),
            "good_p90": float(gs.quantile(0.90)),
            "bad_p10": float(bs.quantile(0.10)),
            "good_p10": float(gs.quantile(0.10)),
            "mean_diff_bad_minus_good": float(bs.mean() - gs.mean()),
            "median_diff_bad_minus_good": float(bs.median() - gs.median()),
            "abs_median_diff": float(abs(bs.median() - gs.median())),
        })
    return pd.DataFrame(rows).sort_values("abs_median_diff", ascending=False) if rows else pd.DataFrame()


def guard_candidates(acc: pd.DataFrame, bad_days: set[str], min_trades: int = 50) -> pd.DataFrame:
    rows = []
    if acc.empty:
        return pd.DataFrame()

    base_pnl = float(acc["sim_pnl"].sum())
    bad_total = int(acc["date"].astype(str).isin(bad_days).sum())

    def eval_guard(name: str, mask_keep: pd.Series):
        keep = mask_keep.fillna(False)
        kept = acc.loc[keep].copy()
        removed = acc.loc[~keep].copy()
        if len(kept) < min_trades:
            return
        bad_removed = int(removed["date"].astype(str).isin(bad_days).sum())
        rows.append({
            "guard": name,
            "kept_trades": len(kept),
            "removed_trades": len(removed),
            "kept_share": len(kept) / len(acc),
            "base_total_pnl": base_pnl,
            "kept_total_pnl": float(kept["sim_pnl"].sum()),
            "pnl_delta": float(kept["sim_pnl"].sum()) - base_pnl,
            "bad_day_trades_removed": bad_removed,
            "bad_day_trades_total": bad_total,
            "bad_day_removed_share": bad_removed / max(1, bad_total),
            "kept_avg_ret": float(kept["net_ret_adj"].mean()),
            "kept_pf": profit_factor(kept["net_ret_adj"]),
            "kept_worst_trade": float(kept["net_ret_adj"].min()),
        })

    if "entry_range_bps" in acc.columns:
        for th in [150, 200, 300, 500, 700, 1000, 1500]:
            eval_guard(f"entry_range_bps <= {th}", acc["entry_range_bps"] <= th)

    if "entry_vol_quote" in acc.columns:
        for th in [100_000, 250_000, 500_000, 1_000_000, 2_000_000, 5_000_000]:
            eval_guard(f"entry_vol_quote >= {th}", acc["entry_vol_quote"] >= th)

    for col in ["mkt_ret_bps", "coin_ret_bps", "rel_ret_bps"]:
        if col in acc.columns:
            qs = acc[col].dropna().quantile([0.1, 0.2, 0.8, 0.9]).to_dict()
            for q, th in qs.items():
                eval_guard(f"{col} >= q{q:.1f}({th:.1f})", acc[col] >= th)
                eval_guard(f"{col} <= q{q:.1f}({th:.1f})", acc[col] <= th)

    ordered = acc.sort_values("entry_time").copy()
    ordered["_family_day_rank"] = ordered.groupby(["date", "family_key"]).cumcount() + 1
    ordered["_short_day_rank"] = 0
    short_idx = ordered["side"].astype(str).eq("short")
    ordered.loc[short_idx, "_short_day_rank"] = ordered.loc[short_idx].groupby("date").cumcount() + 1

    for n in [3, 4, 5, 6, 8, 10]:
        eval_guard(f"post_alloc_short_entries_per_day <= {n}", ordered["_short_day_rank"].replace(0, np.nan) <= n)
    for n in [2, 3, 4, 5]:
        eval_guard(f"post_alloc_old_short_per_day <= {n}", ~((ordered["family_key"] == "old_short") & (ordered["_family_day_rank"] > n)))
    for n in [1, 2, 3]:
        eval_guard(f"post_alloc_market_relative_per_day <= {n}", ~((ordered["family_key"] == "market_relative_short") & (ordered["_family_day_rank"] > n)))

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["utility"] = (
        df["pnl_delta"] / max(1.0, abs(base_pnl)) * 5.0
        + df["bad_day_removed_share"] * 2.0
        + df["kept_pf"].fillna(1.0) * 0.2
        - (1.0 - df["kept_share"]).clip(lower=0) * 0.8
    )
    return df.sort_values("utility", ascending=False).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_dir", default=DEFAULT_BASE)
    ap.add_argument("--master_dir", default=DEFAULT_MASTER_DIR)
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--worst_n_days", type=int, default=30)
    args = ap.parse_args()

    base = Path(args.base_dir)
    master = Path(args.master_dir)
    out = Path(args.out_dir) if args.out_dir else base / "edge_factory_bad_day_investigation"
    out.mkdir(parents=True, exist_ok=True)

    sim_path = master / "recommended_sim_trades.csv"
    daily_path = master / "recommended_daily_pnl.csv"
    if not sim_path.exists():
        raise FileNotFoundError(f"Missing {sim_path}. Run edge_factory_master_optimizer.py first.")

    sim = normalize_sim(safe_read_csv(sim_path))
    acc = sim[sim["accepted"]].copy()

    daily = safe_read_csv(daily_path)
    if daily.empty:
        daily = (
            acc.groupby("date")
            .agg(trades=("trade_id", "count"), pnl=("sim_pnl", "sum"), avg_ret=("net_ret_adj", "mean"), worst_trade=("net_ret_adj", "min"))
            .reset_index()
            .sort_values("pnl")
        )

    daily = daily.sort_values("pnl").reset_index(drop=True)
    worst_days = daily.head(args.worst_n_days).copy()
    bad_set = set(worst_days["date"].astype(str).tolist())

    bad_trades = acc.loc[acc["date"].astype(str).isin(bad_set)].copy()
    good_trades = acc.loc[~acc["date"].astype(str).isin(bad_set)].copy()

    fam_bad = summarize_group(bad_trades, "family_key")
    fam_good = summarize_group(good_trades, "family_key")
    coin_bad = summarize_group(bad_trades, "coin")
    fc = feature_compare(good_trades, bad_trades)
    guards = guard_candidates(acc, bad_set)

    worst_days.to_csv(out / "worst_days.csv", index=False)
    bad_trades.to_csv(out / "worst_day_trade_breakdown.csv", index=False)
    fam_bad.to_csv(out / "family_bad_day_summary.csv", index=False)
    fam_good.to_csv(out / "family_good_day_summary.csv", index=False)
    coin_bad.to_csv(out / "coin_bad_day_summary.csv", index=False)
    fc.to_csv(out / "feature_bad_vs_good.csv", index=False)
    guards.to_csv(out / "bad_day_guard_candidates.csv", index=False)

    report = []
    report.append("EDGE FACTORY BAD-DAY INVESTIGATION REPORT")
    report.append("=" * 120)
    report.append(f"accepted_trades: {len(acc)}")
    report.append(f"worst_n_days: {args.worst_n_days}")
    report.append(f"out_dir: {out}")
    report.append("")
    report.append("WORST DAYS")
    report.append("-" * 120)
    report.append(worst_days.head(40).to_string(index=False))
    report.append("")
    report.append("BAD-DAY FAMILY BREAKDOWN")
    report.append("-" * 120)
    report.append(fam_bad.to_string(index=False) if not fam_bad.empty else "EMPTY")
    report.append("")
    report.append("GOOD-DAY FAMILY BREAKDOWN")
    report.append("-" * 120)
    report.append(fam_good.to_string(index=False) if not fam_good.empty else "EMPTY")
    report.append("")
    report.append("BAD-DAY COIN BREAKDOWN TOP 40")
    report.append("-" * 120)
    report.append(coin_bad.head(40).to_string(index=False) if not coin_bad.empty else "EMPTY")
    report.append("")
    report.append("FEATURE BAD VS GOOD")
    report.append("-" * 120)
    report.append(fc.to_string(index=False) if not fc.empty else "EMPTY")
    report.append("")
    report.append("BAD-DAY GUARD CANDIDATES")
    report.append("-" * 120)
    show = [c for c in ["guard", "utility", "kept_trades", "removed_trades", "kept_share", "pnl_delta", "bad_day_removed_share", "kept_pf", "kept_worst_trade"] if c in guards.columns]
    report.append(guards[show].head(50).to_string(index=False) if not guards.empty else "EMPTY")

    (out / "BAD_DAY_REPORT.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))


if __name__ == "__main__":
    main()
