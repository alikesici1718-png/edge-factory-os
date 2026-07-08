from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd


def now_utc() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def get_last_time(df: pd.DataFrame, col: str):
    if df.empty or col not in df.columns:
        return None
    s = pd.to_datetime(df[col], utc=True, errors="coerce").dropna()
    return None if s.empty else s.iloc[-1]


def age_min(ts):
    if ts is None or pd.isna(ts):
        return None
    return (now_utc() - pd.Timestamp(ts).tz_convert("UTC")).total_seconds() / 60.0


def status(age, warn=5, bad=20):
    if age is None:
        return "NO_DATA"
    if age > bad:
        return "BAD"
    if age > warn:
        return "WARN"
    return "OK"


def print_table(df, title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    print("EMPTY" if df.empty else df.to_string(index=False))


def load_family_config(base: Path, family_config: str | None):
    if family_config:
        return json.loads(Path(family_config).read_text(encoding="utf-8-sig"))
    cfg = base / "family_config.json"
    if cfg.exists():
        return json.loads(cfg.read_text(encoding="utf-8-sig"))
    # fallback names
    return {
        "old_short": str(base / "live_blowoff_short_paper_realistic"),
        "session_short": str(base / "live_session_ret60_reversal_short_paper"),
        "impulse_long": str(base / "live_impulse_event_long_paper"),
        "market_relative_short": str(base / "live_market_relative_extreme_reversion_short_paper"),
        "weak_market_short": str(base / "live_weak_market_breakdown_short_paper"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v3")
    ap.add_argument("--family_config", default="")
    ap.add_argument("--show_tail", type=int, default=10)
    args = ap.parse_args()

    base = Path(args.base_dir)
    fams = load_family_config(base, args.family_config or None)

    rows = []
    for fam, folder_str in fams.items():
        folder = Path(folder_str)
        hb = safe_read_csv(folder / "heartbeat.csv")
        op = safe_read_csv(folder / "open_positions.csv")
        pe = safe_read_csv(folder / "pending_entries.csv")
        cl = safe_read_csv(folder / "closed_trades.csv")
        er = safe_read_csv(folder / "errors.csv")
        rj = safe_read_csv(folder / "rejected_entries.csv")

        last_hb = get_last_time(hb, "log_time")
        a = age_min(last_hb)

        rows.append({
            "family": fam,
            "folder_exists": folder.exists(),
            "heartbeat_status": status(a),
            "heartbeat_age_min": "" if a is None else round(a, 1),
            "equity": "" if hb.empty or "equity" not in hb.columns else hb["equity"].iloc[-1],
            "open": len(op),
            "pending": len(pe),
            "closed": len(cl),
            "rejected": len(rj),
            "errors": len(er),
            "last_signal_utc": get_last_time(safe_read_csv(folder / "signals.csv"), "signal_time") or "",
            "last_closed_utc": get_last_time(cl, "exit_time") or "",
            "last_error_utc": get_last_time(er, "log_time") or "",
        })

    summary = pd.DataFrame(rows)

    global_dir = base / "global_risk_manager"
    snap = safe_read_csv(global_dir / "global_risk_snapshot.csv")
    gate = safe_read_csv(global_dir / "global_gate_decisions.csv")
    vio = safe_read_csv(global_dir / "global_risk_violations.csv")
    gopen = safe_read_csv(global_dir / "global_open_positions.csv")
    gpend = safe_read_csv(global_dir / "global_pending_entries.csv")

    if not snap.empty:
        last_hb = get_last_time(snap, "log_time")
        a = age_min(last_hb)
        summary.loc[len(summary)] = {
            "family": "global_risk_manager",
            "folder_exists": global_dir.exists(),
            "heartbeat_status": status(a),
            "heartbeat_age_min": "" if a is None else round(a, 1),
            "equity": "notional=" + str(snap["open_notional_sum"].iloc[-1]) if "open_notional_sum" in snap.columns else "",
            "open": len(gopen),
            "pending": len(gpend),
            "closed": 0,
            "rejected": 0,
            "errors": 0,
            "last_signal_utc": "",
            "last_closed_utc": "",
            "last_error_utc": "",
        }

    print("\nEDGE FACTORY LIVE HEALTH CHECK v5")
    print("UTC now:", now_utc())
    print("Base:", base)
    print_table(summary, "SYSTEM SUMMARY")

    if not snap.empty:
        print_table(snap.tail(args.show_tail), "GLOBAL RISK SNAPSHOT - LAST ROWS")
    if not gopen.empty:
        cols = [c for c in ["family_key", "coin", "side", "strategy", "entry_time", "planned_exit_time", "notional", "entry_price"] if c in gopen.columns]
        print_table(gopen[cols], "GLOBAL OPEN POSITIONS")
    if not gpend.empty:
        cols = [c for c in ["family_key", "coin", "side", "strategy", "signal_time", "target_entry_time", "planned_exit_time", "signal_vol_quote"] if c in gpend.columns]
        print_table(gpend[cols], "GLOBAL PENDING ENTRIES")
    if not gate.empty:
        cols = [c for c in ["log_time", "decision", "reason", "family_key", "coin", "side", "signal_id", "target_entry_time", "planned_exit_time"] if c in gate.columns]
        print_table(gate[cols].tail(args.show_tail), "GLOBAL GATE DECISIONS - LAST ROWS")
    if not vio.empty:
        cols = [c for c in ["log_time", "severity", "violation_type", "family_key", "coin", "ref", "message"] if c in vio.columns]
        print_table(vio[cols].tail(args.show_tail), "GLOBAL RISK VIOLATIONS - LAST ROWS")

    print("\n" + "=" * 100)
    print("VERDICT")
    print("=" * 100)
    crit = 0
    if not snap.empty and "critical_violations" in snap.columns:
        crit = int(snap["critical_violations"].iloc[-1])
    bad = summary[summary["heartbeat_status"].isin(["BAD", "NO_DATA"])]

    if crit > 0:
        print("NOT OK: active global critical violation exists.")
    elif not bad.empty:
        print("WARN: some components have BAD/NO_DATA heartbeat.")
        print(bad[["family", "heartbeat_status", "heartbeat_age_min", "folder_exists"]].to_string(index=False))
    else:
        print("OK: gate-aware paper system looks healthy.")


if __name__ == "__main__":
    main()
