from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_BASE = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new"
DEFAULT_VALIDATION_DIR = r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\portfolio_family_overlap_validation"

DEFAULT_MAX_PER_FAMILY = {
    "old_short": 3,
    "session_short": 2,
    "impulse_long": 2,
    "market_relative_short": 3,
    "weak_market_short": 1,
}
DEFAULT_PRIORITY = {
    "old_short": 100,
    "impulse_long": 90,
    "session_short": 80,
    "market_relative_short": 70,
    "weak_market_short": 30,
}
DEFAULT_FRACTION = {
    "old_short": 0.05,
    "session_short": 0.05,
    "impulse_long": 0.05,
    "market_relative_short": 0.05,
    "weak_market_short": 0.025,
}


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def parse_json_arg(raw: str, default: dict) -> dict:
    txt = str(raw or "").strip()
    if not txt:
        return default
    if (txt.startswith("'") and txt.endswith("'")) or (txt.startswith('"') and txt.endswith('"')):
        txt = txt[1:-1].strip()
    try:
        return json.loads(txt)
    except Exception:
        return default


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
    if df.empty:
        return df
    x = df.copy()
    if "entry_time" not in x.columns and "signal_time" in x.columns:
        x["entry_time"] = x["signal_time"]
    if "exit_time" not in x.columns and "planned_exit_time" in x.columns:
        x["exit_time"] = x["planned_exit_time"]
    if "net_ret" not in x.columns:
        if "realistic_net_ret" in x.columns:
            x["net_ret"] = x["realistic_net_ret"]
        elif "gross_ret" in x.columns:
            x["net_ret"] = x["gross_ret"]
        elif "pnl" in x.columns and "notional" in x.columns:
            x["net_ret"] = pd.to_numeric(x["pnl"], errors="coerce") / pd.to_numeric(x["notional"], errors="coerce").replace(0, np.nan)
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "side" not in x.columns:
        x["side"] = np.where(x["family_key"].astype(str).str.contains("long"), "long", "short")
    for c in ["entry_time", "exit_time"]:
        x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")
    for c in ["net_ret", "entry_vol_quote", "entry_range_bps", "coin_ret_bps", "mkt_ret_bps", "rel_ret_bps"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    if "entry_vol_quote" not in x.columns:
        x["entry_vol_quote"] = 0.0
    x["coin"] = x["coin"].astype(str).str.upper()
    x = x.dropna(subset=["family_key", "coin", "entry_time", "exit_time", "net_ret"]).copy()
    x = x.loc[x["exit_time"] > x["entry_time"]].copy()
    if "trade_id" not in x.columns:
        x["trade_id"] = x["family_key"].astype(str) + "|" + x["coin"].astype(str) + "|" + x["entry_time"].astype(str) + "|" + x.index.astype(str)
    x["date"] = x["entry_time"].dt.strftime("%Y-%m-%d")
    x["month"] = x["entry_time"].dt.strftime("%Y-%m")
    return x.reset_index(drop=True)


def load_trades(validation_dir: str) -> pd.DataFrame:
    val = Path(validation_dir)
    norm = val / "normalized_trades.csv"
    if norm.exists():
        return normalize_trades(safe_read_csv(norm))
    raise FileNotFoundError(f"Bulunamadı: {norm}. Önce portfolio_family_overlap_validator.py çalıştır.")


def simulate_allocator(
    trades: pd.DataFrame,
    start_equity: float,
    global_max_positions: int,
    max_short_positions: int,
    max_long_positions: int,
    max_per_family: dict[str, int],
    family_priority: dict[str, int],
    capital_fraction: dict[str, float],
    weak_market_backup_only: bool = True,
    exclude_families: set[str] | None = None,
    extra_cost_bps: float = 0.0,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
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
    curve_rows = [{"time": x["entry_time"].min(), "equity": equity, "open_positions": 0, "event": "start"}]

    def counts():
        vals = list(open_pos.values())
        fam = {}
        coins = set()
        short_n = 0
        long_n = 0
        for p in vals:
            fam[p["family_key"]] = fam.get(p["family_key"], 0) + 1
            coins.add(p["coin"])
            short_n += int(p["side"] == "short")
            long_n += int(p["side"] == "long")
        return len(vals), short_n, long_n, fam, coins

    for ts, typ, tid in events:
        row = x.loc[tid]
        fam = str(row["family_key"])
        coin = str(row["coin"])
        side = str(row["side"]).lower()
        if typ == 0:
            if tid not in open_pos:
                continue
            pos = open_pos.pop(tid)
            pnl = pos["notional"] * float(row["net_ret_adj"])
            equity += pnl
            x.loc[tid, "sim_pnl"] = pnl
            x.loc[tid, "equity_after_exit"] = equity
            curve_rows.append({"time": ts, "equity": equity, "open_positions": len(open_pos), "event": f"exit_{fam}_{coin}"})
            continue

        global_n, short_n, long_n, by_family, open_coins = counts()
        reason = ""
        if coin in open_coins:
            reason = "same_coin_overlap_global"
        elif global_n >= global_max_positions:
            reason = "global_max_positions"
        elif side == "short" and short_n >= max_short_positions:
            reason = "max_short_positions"
        elif side == "long" and long_n >= max_long_positions:
            reason = "max_long_positions"
        elif by_family.get(fam, 0) >= int(max_per_family.get(fam, 999999)):
            reason = "max_per_family"
        elif fam == "weak_market_short" and weak_market_backup_only and by_family.get("market_relative_short", 0) > 0:
            reason = "weak_market_backup_only_market_relative_active"
        if reason:
            x.loc[tid, "reject_reason"] = reason
            continue
        frac = float(capital_fraction.get(fam, 0.05))
        notional = equity * frac
        x.loc[tid, "accepted"] = True
        x.loc[tid, "sim_notional"] = notional
        open_pos[tid] = {"family_key": fam, "coin": coin, "side": side, "notional": notional}
        curve_rows.append({"time": ts, "equity": equity, "open_positions": len(open_pos), "event": f"entry_{fam}_{coin}"})

    curve = pd.DataFrame(curve_rows).sort_values("time").reset_index(drop=True)
    sim = x.copy()
    acc = sim[sim["accepted"]].copy()
    rets = pd.to_numeric(acc["net_ret_adj"], errors="coerce").dropna()
    final = float(curve["equity"].iloc[-1]) if len(curve) else start_equity
    stats = {
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
    }
    return stats, curve, sim


def priority_backtest(trades: pd.DataFrame, out: Path, args) -> None:
    out.mkdir(parents=True, exist_ok=True)
    base_max = parse_json_arg(args.max_per_family_json, DEFAULT_MAX_PER_FAMILY)
    base_pri = parse_json_arg(args.family_priority_json, DEFAULT_PRIORITY)
    base_frac = parse_json_arg(args.capital_fraction_json, DEFAULT_FRACTION)
    rows, curves, sims = [], {}, {}

    def add(name, gmax=6, smax=5, lmax=2, maxfam=None, pri=None, frac=None, backup=True, exclude=None, cost=0):
        st, curve, sim = simulate_allocator(
            trades, args.start_equity, gmax, smax, lmax,
            maxfam or base_max, pri or base_pri, frac or base_frac,
            weak_market_backup_only=backup, exclude_families=set(exclude or []), extra_cost_bps=cost
        )
        st.update({"scenario": name, "global_max": gmax, "short_max": smax, "weak_backup": backup, "extra_cost_bps": cost})
        rows.append(st); curves[name] = curve; sims[name] = sim

    add("live_v4_priority")
    add("without_weak_market", exclude=["weak_market_short"])
    add("weak_allowed_not_backup", backup=False)
    add("market_relative_max_1", maxfam={**base_max, "market_relative_short": 1})
    add("market_relative_max_2", maxfam={**base_max, "market_relative_short": 2})
    add("market_relative_max_4", maxfam={**base_max, "market_relative_short": 4})
    add("global_max_4_short4", gmax=4, smax=4)
    add("global_max_5", gmax=5)
    add("short_max_3", smax=3)
    add("short_max_4", smax=4)
    add("old_max_2", maxfam={**base_max, "old_short": 2})
    add("old_max_4", maxfam={**base_max, "old_short": 4})
    add("no_session_short", exclude=["session_short"])
    add("no_market_relative", exclude=["market_relative_short"])
    add("no_session_no_market_relative", exclude=["session_short", "market_relative_short"])
    add("all_plus_50bps", cost=50)
    add("all_plus_100bps", cost=100)
    add("market_before_old", pri={**base_pri, "market_relative_short": 110, "old_short": 100})
    add("impulse_top_priority", pri={**base_pri, "impulse_long": 120})
    add("market_before_session", pri={**base_pri, "market_relative_short": 85, "session_short": 70})

    df = pd.DataFrame(rows).sort_values(["portfolio_total_return", "portfolio_max_drawdown"], ascending=[False, False]).reset_index(drop=True)
    df.to_csv(out / "priority_scenario_summary.csv", index=False)
    best = str(df.iloc[0]["scenario"])
    curves[best].to_csv(out / "best_equity_curve.csv", index=False)
    sims[best].to_csv(out / "best_sim_trades.csv", index=False)
    sims["live_v4_priority"].to_csv(out / "live_v4_sim_trades.csv", index=False)
    acc = sims["live_v4_priority"].loc[sims["live_v4_priority"]["accepted"]].copy()
    fam = acc.groupby("family_key").agg(trades=("trade_id", "count"), pnl=("sim_pnl", "sum"), avg_ret=("net_ret_adj", "mean"), win_rate=("net_ret_adj", lambda s: (s > 0).mean())).reset_index().sort_values("pnl", ascending=False)
    rej = sims["live_v4_priority"].loc[~sims["live_v4_priority"]["accepted"]].groupby(["family_key", "reject_reason"]).size().reset_index(name="count").sort_values("count", ascending=False)
    fam.to_csv(out / "live_v4_family_pnl.csv", index=False)
    rej.to_csv(out / "live_v4_reject_summary.csv", index=False)
    report = []
    report.append("PRIORITY ALLOCATOR BACKTEST REPORT")
    report.append("=" * 100)
    report.append(f"input_trades: {len(trades)}")
    report.append(f"out_dir: {out}")
    report.append("")
    report.append("TOP SCENARIOS")
    report.append("-" * 100)
    cols = ["scenario", "accepted_trades", "final_equity", "portfolio_total_return", "portfolio_max_drawdown", "profit_factor", "win_rate", "worst_trade", "max_open_seen"]
    report.append(df[cols].head(30).to_string(index=False))
    report.append("")
    report.append("LIVE_V4 FAMILY PNL")
    report.append("-" * 100)
    report.append(fam.to_string(index=False))
    report.append("")
    report.append("LIVE_V4 REJECT SUMMARY")
    report.append("-" * 100)
    report.append(rej.head(40).to_string(index=False))
    (out / "priority_allocator_report.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))


def blocked_audit(trades: pd.DataFrame, out: Path, args) -> None:
    out.mkdir(parents=True, exist_ok=True)
    maxfam = parse_json_arg(args.max_per_family_json, DEFAULT_MAX_PER_FAMILY)
    pri = parse_json_arg(args.family_priority_json, DEFAULT_PRIORITY)
    _, _, sim = simulate_allocator(trades, args.start_equity, 6, 5, 2, maxfam, pri, DEFAULT_FRACTION, True)
    sim.to_csv(out / "gate_audit_all_trades.csv", index=False)
    rows = []
    for (fam, accepted), g in sim.groupby(["family_key", "accepted"]):
        r = pd.to_numeric(g["net_ret"], errors="coerce").dropna()
        rows.append({
            "family_key": fam, "bucket": "allowed" if accepted else "blocked", "trades": len(g),
            "avg_ret": float(r.mean()) if len(r) else np.nan, "median_ret": float(r.median()) if len(r) else np.nan,
            "sum_ret": float(r.sum()) if len(r) else 0.0, "win_rate": float((r > 0).mean()) if len(r) else np.nan,
            "profit_factor": profit_factor(r), "worst_trade": float(r.min()) if len(r) else np.nan,
        })
    avb = pd.DataFrame(rows).sort_values(["family_key", "bucket"])
    reason_rows = []
    blocked = sim.loc[~sim["accepted"]].copy()
    for (fam, reason), g in blocked.groupby(["family_key", "reject_reason"]):
        r = pd.to_numeric(g["net_ret"], errors="coerce").dropna()
        reason_rows.append({
            "family_key": fam, "reject_reason": reason, "blocked_trades": len(g),
            "avg_ret_if_taken": float(r.mean()) if len(r) else np.nan,
            "median_ret_if_taken": float(r.median()) if len(r) else np.nan,
            "sum_ret_if_taken": float(r.sum()) if len(r) else 0.0,
            "win_rate_if_taken": float((r > 0).mean()) if len(r) else np.nan,
            "profit_factor_if_taken": profit_factor(r), "worst_trade_if_taken": float(r.min()) if len(r) else np.nan,
        })
    reason = pd.DataFrame(reason_rows).sort_values(["avg_ret_if_taken", "sum_ret_if_taken"], ascending=[False, False])
    missed = blocked.sort_values("net_ret", ascending=False).head(200)
    avb.to_csv(out / "allowed_vs_blocked_summary.csv", index=False)
    reason.to_csv(out / "blocked_reason_quality.csv", index=False)
    missed.to_csv(out / "missed_winners_top200.csv", index=False)
    report = []
    report.append("BLOCKED SIGNAL AUDITOR REPORT")
    report.append("=" * 100)
    report.append(f"input_trades: {len(trades)}")
    report.append(f"out_dir: {out}")
    report.append("")
    report.append("ALLOWED VS BLOCKED")
    report.append("-" * 100)
    report.append(avb.to_string(index=False))
    report.append("")
    report.append("BLOCKED REASON QUALITY")
    report.append("-" * 100)
    report.append(reason.head(50).to_string(index=False))
    report.append("")
    report.append("MISSED WINNERS TOP 30")
    report.append("-" * 100)
    cols = [c for c in ["family_key", "coin", "entry_time", "exit_time", "net_ret", "reject_reason", "entry_vol_quote", "entry_range_bps"] if c in missed.columns]
    report.append(missed[cols].head(30).to_string(index=False))
    (out / "blocked_signal_auditor_report.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))


def family_stats(df: pd.DataFrame) -> dict:
    r = pd.to_numeric(df["net_ret"], errors="coerce").dropna()
    return {
        "trades": int(len(df)), "coins": int(df["coin"].nunique()) if "coin" in df.columns else 0,
        "sum_ret": float(r.sum()) if len(r) else 0.0,
        "avg_ret": float(r.mean()) if len(r) else np.nan,
        "median_ret": float(r.median()) if len(r) else np.nan,
        "win_rate": float((r > 0).mean()) if len(r) else np.nan,
        "profit_factor": profit_factor(r),
        "worst_trade": float(r.min()) if len(r) else np.nan,
        "p05_ret": float(r.quantile(0.05)) if len(r) else np.nan,
        "best_trade": float(r.max()) if len(r) else np.nan,
    }


def squeeze_search(trades: pd.DataFrame, out: Path, min_trades: int) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    num_cols = [c for c in ["entry_range_bps", "entry_vol_quote", "coin_ret_bps", "mkt_ret_bps", "rel_ret_bps"] if c in trades.columns]
    for fam in [f for f in trades["family_key"].dropna().unique() if "short" in str(f)]:
        base = trades.loc[trades["family_key"] == fam].copy()
        if len(base) < min_trades:
            continue
        base_st = family_stats(base)
        rows.append({"family_key": fam, "filter": "BASE", "kept_share": 1.0, "pf_delta": 0.0, "worst_delta": 0.0, "avg_delta": 0.0, **base_st})
        tests = []
        if "entry_range_bps" in num_cols:
            for th in [100, 150, 200, 300, 400, 500, 700, 1000, 1500, 2000]:
                tests.append((f"entry_range_bps <= {th}", base["entry_range_bps"] <= th))
        if "entry_vol_quote" in num_cols:
            for th in [100_000, 250_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000]:
                tests.append((f"entry_vol_quote >= {th}", base["entry_vol_quote"] >= th))
        for col in ["coin_ret_bps", "mkt_ret_bps", "rel_ret_bps"]:
            if col in num_cols and base[col].notna().sum() >= min_trades:
                for q in [0.1, 0.2, 0.8, 0.9]:
                    th = float(base[col].dropna().quantile(q))
                    tests.append((f"{col} >= q{q:.1f}({th:.1f})", base[col] >= th))
                    tests.append((f"{col} <= q{q:.1f}({th:.1f})", base[col] <= th))
        if "entry_range_bps" in num_cols and "entry_vol_quote" in num_cols:
            for rth in [200, 300, 500, 700, 1000]:
                for vth in [250_000, 500_000, 1_000_000, 2_000_000]:
                    tests.append((f"entry_range_bps <= {rth} AND entry_vol_quote >= {vth}", (base["entry_range_bps"] <= rth) & (base["entry_vol_quote"] >= vth)))
        for name, mask in tests:
            filt = base.loc[mask.fillna(False)].copy()
            if len(filt) < min_trades:
                continue
            st = family_stats(filt)
            pf_delta = (st["profit_factor"] if not pd.isna(st["profit_factor"]) else 0) - (base_st["profit_factor"] if not pd.isna(base_st["profit_factor"]) else 0)
            worst_delta = (st["worst_trade"] if not pd.isna(st["worst_trade"]) else 0) - (base_st["worst_trade"] if not pd.isna(base_st["worst_trade"]) else 0)
            avg_delta = (st["avg_ret"] if not pd.isna(st["avg_ret"]) else 0) - (base_st["avg_ret"] if not pd.isna(base_st["avg_ret"]) else 0)
            rows.append({"family_key": fam, "filter": name, "kept_share": len(filt) / len(base), "pf_delta": pf_delta, "worst_delta": worst_delta, "avg_delta": avg_delta, **st})
    res = pd.DataFrame(rows)
    if not res.empty:
        res["filter_score"] = res["pf_delta"].fillna(0) * 2 + res["worst_delta"].fillna(0) * 10 + res["avg_delta"].fillna(0) * 20 + np.minimum(res["trades"] / 1000.0, 1.0) - (1.0 - res["kept_share"]).clip(lower=0) * 0.5
        res = res.sort_values(["family_key", "filter_score"], ascending=[True, False]).reset_index(drop=True)
    res.to_csv(out / "squeeze_filter_candidates.csv", index=False)
    top = res.loc[res["filter"] != "BASE"].groupby("family_key", group_keys=False).head(20) if not res.empty else pd.DataFrame()
    top.to_csv(out / "squeeze_filter_top_by_family.csv", index=False)
    report = []
    report.append("SQUEEZE FILTER SEARCH REPORT")
    report.append("=" * 100)
    report.append(f"input_trades: {len(trades)}")
    report.append(f"out_dir: {out}")
    report.append("")
    report.append("TOP FILTERS BY FAMILY")
    report.append("-" * 100)
    cols = ["family_key", "filter", "filter_score", "trades", "kept_share", "sum_ret", "avg_ret", "profit_factor", "win_rate", "worst_trade", "p05_ret", "pf_delta", "worst_delta", "avg_delta"]
    report.append(top[[c for c in cols if c in top.columns]].to_string(index=False) if not top.empty else "EMPTY")
    (out / "squeeze_filter_report.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n" + "\n".join(report))


def main() -> None:
    ap = argparse.ArgumentParser(description="Edge Factory offline optimizer: priority backtest + blocked audit + squeeze filter search.")
    ap.add_argument("--mode", choices=["all", "priority", "blocked", "squeeze"], default="all")
    ap.add_argument("--base_dir", default=DEFAULT_BASE)
    ap.add_argument("--validation_dir", default=DEFAULT_VALIDATION_DIR)
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--max_per_family_json", default=json.dumps(DEFAULT_MAX_PER_FAMILY))
    ap.add_argument("--family_priority_json", default=json.dumps(DEFAULT_PRIORITY))
    ap.add_argument("--capital_fraction_json", default=json.dumps(DEFAULT_FRACTION))
    ap.add_argument("--min_trades", type=int, default=50)
    args = ap.parse_args()

    base = Path(args.base_dir)
    out_root = Path(args.out_dir) if args.out_dir else base / "edge_factory_offline_optimizer"
    out_root.mkdir(parents=True, exist_ok=True)
    trades = load_trades(args.validation_dir)
    trades.to_csv(out_root / "input_normalized_trades.csv", index=False)
    print(f"Loaded normalized trades: {len(trades)}")
    print(f"out_root: {out_root}")

    if args.mode in ["all", "priority"]:
        priority_backtest(trades, out_root / "priority_allocator_backtest", args)
    if args.mode in ["all", "blocked"]:
        blocked_audit(trades, out_root / "blocked_signal_audit", args)
    if args.mode in ["all", "squeeze"]:
        squeeze_search(trades, out_root / "squeeze_filter_search", args.min_trades)

    print("\nDONE")
    print(out_root)


if __name__ == "__main__":
    main()
