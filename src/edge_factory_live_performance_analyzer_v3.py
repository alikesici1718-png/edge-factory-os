from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


def utc_now():
    return pd.Timestamp.now(tz="UTC")


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def okx_last(inst_id: str, timeout=10):
    url = "https://www.okx.com/api/v5/market/ticker?" + urlencode({"instId": inst_id})
    req = Request(url, headers={"User-Agent": "edge-factory-perf-v3/1.0"})
    with urlopen(req, timeout=timeout) as r:
        js = json.loads(r.read().decode("utf-8"))
    if str(js.get("code")) != "0" or not js.get("data"):
        raise RuntimeError(f"ticker failed {inst_id}: {js}")
    return float(js["data"][0]["last"])


def infer_side(fam, df):
    if "side" in df.columns:
        s = df["side"].astype(str).str.lower()
        s = s.where(s.isin(["long", "short"]), "")
    else:
        s = pd.Series([""] * len(df), index=df.index)
    default = "long" if "long" in fam else "short"
    s = s.replace("", default)
    s = s.mask(~s.isin(["long", "short"]), default)
    return s


def load_family_config(base: Path, family_config: str | None):
    if family_config:
        return json.loads(Path(family_config).read_text(encoding="utf-8-sig"))
    cfg = base / "family_config.json"
    if cfg.exists():
        return json.loads(cfg.read_text(encoding="utf-8-sig"))
    return {}


def norm_open(df, fam, folder):
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = x.get("family_key", fam)
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "coin" not in x.columns:
        x["coin"] = ""
    x["coin"] = x["coin"].astype(str).str.upper()
    if "inst_id" not in x.columns:
        x["inst_id"] = x["coin"] + "-USDT-SWAP"
    x["side"] = infer_side(fam, x)
    for c in ["entry_time", "planned_exit_time"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")
    for c in ["notional", "entry_price", "raw_entry_close"]:
        if c not in x.columns:
            x[c] = np.nan
        x[c] = pd.to_numeric(x[c], errors="coerce")
    x["entry_price"] = x["entry_price"].fillna(x["raw_entry_close"])
    x["source_folder"] = str(folder)
    return x


def norm_closed(df, fam, folder):
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = x.get("family_key", fam)
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "coin" not in x.columns:
        x["coin"] = ""
    x["coin"] = x["coin"].astype(str).str.upper()
    x["side"] = infer_side(fam, x)
    if "net_ret" not in x.columns and "realistic_net_ret" in x.columns:
        x["net_ret"] = x["realistic_net_ret"]
    for c in ["entry_time", "exit_time"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")
    for c in ["pnl", "net_ret", "notional"]:
        if c not in x.columns:
            x[c] = np.nan
        x[c] = pd.to_numeric(x[c], errors="coerce")
    x["source_folder"] = str(folder)
    return x


def norm_pending(df, fam, folder):
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = x.get("family_key", fam)
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "coin" not in x.columns:
        x["coin"] = ""
    x["coin"] = x["coin"].astype(str).str.upper()
    x["side"] = infer_side(fam, x)
    for c in ["signal_time", "target_entry_time", "planned_exit_time"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")
    x["source_folder"] = str(folder)
    return x


def mtm(open_df, no_mtm):
    if open_df.empty:
        return open_df
    x = open_df.copy()
    x["last_price"] = np.nan
    x["unrealized_ret"] = np.nan
    x["unrealized_pnl"] = np.nan
    x["mtm_error"] = ""
    if no_mtm:
        return x
    cache = {}
    for i, r in x.iterrows():
        try:
            inst = str(r["inst_id"])
            if inst not in cache:
                cache[inst] = okx_last(inst)
            last = cache[inst]
            entry = float(r["entry_price"])
            notional = float(r["notional"])
            side = str(r["side"])
            if side == "short":
                ret = entry / last - 1.0
            else:
                ret = last / entry - 1.0
            x.loc[i, "last_price"] = last
            x.loc[i, "unrealized_ret"] = ret
            x.loc[i, "unrealized_pnl"] = notional * ret
        except Exception as e:
            x.loc[i, "mtm_error"] = f"{type(e).__name__}: {e}"
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v3")
    ap.add_argument("--family_config", default="")
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--start_equity", type=float, default=1000.0)
    ap.add_argument("--no_mtm", action="store_true")
    args = ap.parse_args()

    base = Path(args.base_dir)
    out = Path(args.out_dir) if args.out_dir else base / "live_performance_report"
    out.mkdir(parents=True, exist_ok=True)

    fams = load_family_config(base, args.family_config or None)
    opens, closeds, pends = [], [], []
    for fam, folder_str in fams.items():
        folder = Path(folder_str)
        opens.append(norm_open(safe_read_csv(folder / "open_positions.csv"), fam, folder))
        closeds.append(norm_closed(safe_read_csv(folder / "closed_trades.csv"), fam, folder))
        pends.append(norm_pending(safe_read_csv(folder / "pending_entries.csv"), fam, folder))

    open_df = pd.concat([x for x in opens if not x.empty], ignore_index=True) if any(not x.empty for x in opens) else pd.DataFrame()
    closed_df = pd.concat([x for x in closeds if not x.empty], ignore_index=True) if any(not x.empty for x in closeds) else pd.DataFrame()
    pending_df = pd.concat([x for x in pends if not x.empty], ignore_index=True) if any(not x.empty for x in pends) else pd.DataFrame()

    open_mtm = mtm(open_df, args.no_mtm)

    rows = []
    for fam in fams:
        c = closed_df[closed_df["family_key"].astype(str) == fam] if not closed_df.empty else pd.DataFrame()
        o = open_mtm[open_mtm["family_key"].astype(str) == fam] if not open_mtm.empty else pd.DataFrame()
        p = pending_df[pending_df["family_key"].astype(str) == fam] if not pending_df.empty else pd.DataFrame()
        rets = pd.to_numeric(c.get("net_ret", pd.Series(dtype=float)), errors="coerce").dropna()
        rows.append({
            "family_key": fam,
            "closed_trades": len(c),
            "open_positions": len(o),
            "pending_entries": len(p),
            "realized_pnl": float(pd.to_numeric(c.get("pnl", pd.Series(dtype=float)), errors="coerce").sum()) if not c.empty else 0.0,
            "unrealized_pnl": float(pd.to_numeric(o.get("unrealized_pnl", pd.Series(dtype=float)), errors="coerce").sum()) if not o.empty else 0.0,
            "open_notional": float(pd.to_numeric(o.get("notional", pd.Series(dtype=float)), errors="coerce").sum()) if not o.empty else 0.0,
            "win_rate_closed": float((rets > 0).mean()) if len(rets) else np.nan,
            "avg_net_ret_closed": float(rets.mean()) if len(rets) else np.nan,
        })
    family_summary = pd.DataFrame(rows)
    family_summary["total_pnl_realized_plus_unrealized"] = family_summary["realized_pnl"] + family_summary["unrealized_pnl"]

    total_realized = float(family_summary["realized_pnl"].sum()) if not family_summary.empty else 0.0
    total_unrealized = float(family_summary["unrealized_pnl"].sum()) if not family_summary.empty else 0.0

    snapshot = {
        "log_time": str(utc_now()),
        "start_equity": args.start_equity,
        "total_realized_pnl": total_realized,
        "total_unrealized_pnl": total_unrealized,
        "estimated_equity": args.start_equity + total_realized + total_unrealized,
        "open_positions": int(len(open_mtm)),
        "pending_entries": int(len(pending_df)),
        "closed_trades": int(len(closed_df)),
        "open_notional": float(pd.to_numeric(open_mtm.get("notional", pd.Series(dtype=float)), errors="coerce").sum()) if not open_mtm.empty else 0.0,
        "mtm_enabled": not args.no_mtm,
    }

    family_summary.to_csv(out / "live_family_summary.csv", index=False)
    open_mtm.to_csv(out / "live_open_mtm.csv", index=False)
    closed_df.to_csv(out / "live_closed_trades_all.csv", index=False)
    pending_df.to_csv(out / "live_pending_all.csv", index=False)
    (out / "live_report_snapshot.json").write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    print("\nEDGE FACTORY LIVE PERFORMANCE ANALYZER v3")
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
        cols = [c for c in ["family_key", "coin", "side", "entry_time", "planned_exit_time", "notional", "entry_price", "last_price", "unrealized_ret", "unrealized_pnl", "mtm_error"] if c in open_mtm.columns]
        print(open_mtm[cols].to_string(index=False))

    print("\n" + "=" * 100)
    print("PENDING ENTRIES")
    print("=" * 100)
    if pending_df.empty:
        print("EMPTY")
    else:
        cols = [c for c in ["family_key", "coin", "side", "signal_time", "target_entry_time", "planned_exit_time", "signal_vol_quote"] if c in pending_df.columns]
        print(pending_df[cols].tail(40).to_string(index=False))

    print("\nSaved:", out)


if __name__ == "__main__":
    main()
