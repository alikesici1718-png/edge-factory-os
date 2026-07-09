"""
Reads live paper-run family closed_trades and open_positions CSVs and fetches current OKX market prices to compute per-family realized and unrealized performance metrics (PnL, win rate, drawdown, Sharpe).
Outputs a performance snapshot JSON and prints a formatted report to stdout.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


API_BASE = "https://www.okx.com"
TICKER_ENDPOINT = "/api/v5/market/ticker"


def utc_now() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def okx_last_price(inst_id: str, timeout: int = 10) -> float:
    url = f"{API_BASE}{TICKER_ENDPOINT}?{urlencode({'instId': inst_id})}"
    req = Request(url, headers={"User-Agent": "edge-factory-live-performance-analyzer/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        js = json.loads(resp.read().decode("utf-8"))
    if str(js.get("code")) != "0" or not js.get("data"):
        raise RuntimeError(f"OKX ticker failed for {inst_id}: {js}")
    return float(js["data"][0]["last"])


def infer_side(family_key: str, df: pd.DataFrame) -> pd.Series:
    if "side" in df.columns:
        s = df["side"].astype(str).str.lower()
        s = s.where(s.isin(["long", "short"]), "")
    else:
        s = pd.Series([""] * len(df), index=df.index)

    if family_key in {"old_short", "session_short", "market_relative_short"}:
        s = s.replace("", "short")
        s = s.mask(~s.isin(["long", "short"]), "short")
    elif family_key == "impulse_long":
        s = s.replace("", "long")
        s = s.mask(~s.isin(["long", "short"]), "long")
    return s


def normalize_open(df: pd.DataFrame, family_key: str, folder: Path) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = family_key
    x["source_folder"] = str(folder)

    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "inst_id" not in x.columns and "coin" in x.columns:
        x["inst_id"] = x["coin"].astype(str).str.upper() + "-USDT-SWAP"

    x["coin"] = x.get("coin", pd.Series([""] * len(x))).astype(str).str.upper()
    x["inst_id"] = x.get("inst_id", x["coin"] + "-USDT-SWAP").astype(str)
    x["side"] = infer_side(family_key, x)
    x["entry_time"] = pd.to_datetime(x.get("entry_time", pd.NaT), utc=True, errors="coerce")
    x["planned_exit_time"] = pd.to_datetime(x.get("planned_exit_time", pd.NaT), utc=True, errors="coerce")

    for col in ["notional", "entry_price", "raw_entry_close", "entry_vol_quote", "entry_range_bps"]:
        if col not in x.columns:
            x[col] = np.nan
        x[col] = pd.to_numeric(x[col], errors="coerce")

    x["entry_price"] = x["entry_price"].fillna(x["raw_entry_close"])
    if "position_id" not in x.columns:
        x["position_id"] = [f"{family_key}_{i}" for i in range(len(x))]

    keep = [
        "family_key", "position_id", "coin", "inst_id", "side",
        "entry_time", "planned_exit_time", "notional", "entry_price",
        "raw_entry_close", "entry_vol_quote", "entry_range_bps", "source_folder",
    ]
    extra = [c for c in ["strategy", "signal_time", "coin_ret_bps", "market_ret_bps", "rel_ret_bps"] if c in x.columns]
    return x[[c for c in keep + extra if c in x.columns]].copy()


def normalize_closed(df: pd.DataFrame, family_key: str, folder: Path) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = family_key
    x["source_folder"] = str(folder)

    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    x["coin"] = x.get("coin", pd.Series([""] * len(x))).astype(str).str.upper()

    if "net_ret" not in x.columns and "realistic_net_ret" in x.columns:
        x["net_ret"] = x["realistic_net_ret"]
    if "net_ret" not in x.columns:
        x["net_ret"] = np.nan
    if "pnl" not in x.columns:
        x["pnl"] = np.nan
    if "notional" not in x.columns:
        x["notional"] = np.nan

    x["entry_time"] = pd.to_datetime(x.get("entry_time", pd.NaT), utc=True, errors="coerce")
    x["exit_time"] = pd.to_datetime(x.get("exit_time", pd.NaT), utc=True, errors="coerce")
    x["net_ret"] = pd.to_numeric(x["net_ret"], errors="coerce")
    x["pnl"] = pd.to_numeric(x["pnl"], errors="coerce")
    x["notional"] = pd.to_numeric(x["notional"], errors="coerce")
    x["side"] = infer_side(family_key, x)

    keep = [
        "family_key", "coin", "side", "entry_time", "exit_time",
        "notional", "net_ret", "pnl", "source_folder",
    ]
    extra = [c for c in ["strategy", "exit_reason", "stress_net_ret", "stress_pnl", "equity_after"] if c in x.columns]
    return x[[c for c in keep + extra if c in x.columns]].copy()


def normalize_pending(df: pd.DataFrame, family_key: str, folder: Path) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = family_key
    x["source_folder"] = str(folder)

    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "inst_id" not in x.columns and "coin" in x.columns:
        x["inst_id"] = x["coin"].astype(str).str.upper() + "-USDT-SWAP"

    x["coin"] = x.get("coin", pd.Series([""] * len(x))).astype(str).str.upper()
    x["side"] = infer_side(family_key, x)
    x["signal_time"] = pd.to_datetime(x.get("signal_time", pd.NaT), utc=True, errors="coerce")
    x["target_entry_time"] = pd.to_datetime(x.get("target_entry_time", pd.NaT), utc=True, errors="coerce")
    x["planned_exit_time"] = pd.to_datetime(x.get("planned_exit_time", pd.NaT), utc=True, errors="coerce")

    for col in ["signal_vol_quote", "signal_range_bps"]:
        if col not in x.columns:
            x[col] = np.nan
        x[col] = pd.to_numeric(x[col], errors="coerce")

    keep = [
        "family_key", "coin", "side", "signal_time", "target_entry_time",
        "planned_exit_time", "signal_vol_quote", "signal_range_bps", "source_folder",
    ]
    extra = [c for c in ["strategy", "signal_id", "coin_ret_bps", "market_ret_bps", "rel_ret_bps"] if c in x.columns]
    return x[[c for c in keep + extra if c in x.columns]].copy()


def mtm_open_positions(open_df: pd.DataFrame, no_mtm: bool) -> pd.DataFrame:
    if open_df.empty:
        return open_df

    x = open_df.copy()
    x["last_price"] = np.nan
    x["unrealized_ret"] = np.nan
    x["unrealized_pnl"] = np.nan
    x["mtm_error"] = ""

    if no_mtm:
        return x

    cache: dict[str, float] = {}
    for idx, row in x.iterrows():
        inst = str(row["inst_id"])
        try:
            if inst not in cache:
                cache[inst] = okx_last_price(inst)
            last = cache[inst]
            entry = float(row["entry_price"])
            notional = float(row["notional"])
            side = str(row["side"]).lower()

            if not np.isfinite(entry) or entry <= 0 or not np.isfinite(notional):
                raise ValueError("bad entry/notional")

            if side == "short":
                ret = entry / last - 1.0
            elif side == "long":
                ret = last / entry - 1.0
            else:
                raise ValueError(f"unknown side={side}")

            x.loc[idx, "last_price"] = last
            x.loc[idx, "unrealized_ret"] = ret
            x.loc[idx, "unrealized_pnl"] = notional * ret
        except Exception as e:
            x.loc[idx, "mtm_error"] = f"{type(e).__name__}: {e}"

    return x


def summarize_family(closed: pd.DataFrame, open_mtm: pd.DataFrame, pending: pd.DataFrame, families: list[str]) -> pd.DataFrame:
    rows = []
    for fam in families:
        c = closed[closed["family_key"] == fam] if not closed.empty else pd.DataFrame()
        o = open_mtm[open_mtm["family_key"] == fam] if not open_mtm.empty else pd.DataFrame()
        p = pending[pending["family_key"] == fam] if not pending.empty else pd.DataFrame()

        realized_pnl = float(pd.to_numeric(c.get("pnl", pd.Series(dtype=float)), errors="coerce").sum()) if not c.empty else 0.0
        unrealized_pnl = float(pd.to_numeric(o.get("unrealized_pnl", pd.Series(dtype=float)), errors="coerce").sum()) if not o.empty else 0.0
        notional_open = float(pd.to_numeric(o.get("notional", pd.Series(dtype=float)), errors="coerce").sum()) if not o.empty else 0.0

        net_rets = pd.to_numeric(c.get("net_ret", pd.Series(dtype=float)), errors="coerce").dropna()
        rows.append({
            "family_key": fam,
            "closed_trades": len(c),
            "open_positions": len(o),
            "pending_entries": len(p),
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl_realized_plus_unrealized": realized_pnl + unrealized_pnl,
            "open_notional": notional_open,
            "win_rate_closed": float((net_rets > 0).mean()) if len(net_rets) else np.nan,
            "avg_net_ret_closed": float(net_rets.mean()) if len(net_rets) else np.nan,
            "wins_closed": int((net_rets > 0).sum()) if len(net_rets) else 0,
            "losses_closed": int((net_rets < 0).sum()) if len(net_rets) else 0,
        })

    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Live performance analyzer for Edge Factory paper system.")
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\live_performance_report")
    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--no_mtm", action="store_true")
    args = ap.parse_args()

    base = Path(args.base_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    folders = {
        "old_short": base / "live_blowoff_short_paper_realistic",
        "session_short": base / "live_session_ret60_reversal_short_paper",
        "impulse_long": base / "live_impulse_event_long_paper",
        "market_relative_short": base / "live_market_relative_extreme_reversion_short_paper",
    }

    open_parts = []
    closed_parts = []
    pending_parts = []
    for fam, folder in folders.items():
        open_parts.append(normalize_open(safe_read_csv(folder / "open_positions.csv"), fam, folder))
        closed_parts.append(normalize_closed(safe_read_csv(folder / "closed_trades.csv"), fam, folder))
        pending_parts.append(normalize_pending(safe_read_csv(folder / "pending_entries.csv"), fam, folder))

    open_df = pd.concat([x for x in open_parts if not x.empty], ignore_index=True) if any(not x.empty for x in open_parts) else pd.DataFrame()
    closed_df = pd.concat([x for x in closed_parts if not x.empty], ignore_index=True) if any(not x.empty for x in closed_parts) else pd.DataFrame()
    pending_df = pd.concat([x for x in pending_parts if not x.empty], ignore_index=True) if any(not x.empty for x in pending_parts) else pd.DataFrame()

    open_mtm = mtm_open_positions(open_df, args.no_mtm)
    families = list(folders.keys())
    family_summary = summarize_family(closed_df, open_mtm, pending_df, families)

    total_realized = float(family_summary["realized_pnl"].sum()) if not family_summary.empty else 0.0
    total_unrealized = float(family_summary["unrealized_pnl"].sum()) if not family_summary.empty else 0.0
    total_open_notional = float(family_summary["open_notional"].sum()) if not family_summary.empty else 0.0
    est_equity = args.start_equity + total_realized + total_unrealized

    family_summary.to_csv(out / "live_family_summary.csv", index=False)
    open_mtm.to_csv(out / "live_open_mtm.csv", index=False)
    closed_df.to_csv(out / "live_closed_trades_all.csv", index=False)
    pending_df.to_csv(out / "live_pending_all.csv", index=False)

    snapshot = {
        "log_time": str(utc_now()),
        "start_equity": args.start_equity,
        "total_realized_pnl": total_realized,
        "total_unrealized_pnl": total_unrealized,
        "estimated_equity": est_equity,
        "open_positions": int(len(open_mtm)),
        "pending_entries": int(len(pending_df)),
        "closed_trades": int(len(closed_df)),
        "open_notional": total_open_notional,
        "mtm_enabled": not args.no_mtm,
    }
    (out / "live_report_snapshot.json").write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    print("\nEDGE FACTORY LIVE PERFORMANCE ANALYZER")
    print("UTC now:", utc_now())
    print("Base:", base)

    print("\n" + "=" * 100)
    print("PORTFOLIO SNAPSHOT")
    print("=" * 100)
    for k, v in snapshot.items():
        print(f"{k}: {v}")

    print("\n" + "=" * 100)
    print("FAMILY SUMMARY")
    print("=" * 100)
    print(family_summary.to_string(index=False) if not family_summary.empty else "EMPTY")

    print("\n" + "=" * 100)
    print("OPEN POSITIONS MTM")
    print("=" * 100)
    if open_mtm.empty:
        print("EMPTY")
    else:
        show = [c for c in [
            "family_key", "coin", "side", "entry_time", "planned_exit_time",
            "notional", "entry_price", "last_price", "unrealized_ret", "unrealized_pnl", "mtm_error"
        ] if c in open_mtm.columns]
        print(open_mtm[show].to_string(index=False))

    print("\n" + "=" * 100)
    print("PENDING ENTRIES")
    print("=" * 100)
    if pending_df.empty:
        print("EMPTY")
    else:
        show = [c for c in [
            "family_key", "coin", "side", "signal_time", "target_entry_time",
            "planned_exit_time", "signal_vol_quote", "signal_range_bps"
        ] if c in pending_df.columns]
        print(pending_df[show].to_string(index=False))

    print("\nSaved:")
    print(out / "live_family_summary.csv")
    print(out / "live_open_mtm.csv")
    print(out / "live_closed_trades_all.csv")
    print(out / "live_pending_all.csv")
    print(out / "live_report_snapshot.json")


if __name__ == "__main__":
    main()
