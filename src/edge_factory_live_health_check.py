"""
Reads live paper-run family CSV logs (heartbeat, positions, trades, errors) and global risk manager outputs to assess the operational health of all running strategy families.
Prints a health status table to stdout, flagging families as OK, WARN, or BAD based on heartbeat age and critical risk violations.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


# =============================================================================
# EDGE FACTORY LIVE HEALTH CHECK v3
# =============================================================================
#
# v2 fixed manager heartbeat.
# v3 additionally treats GLOBAL CRITICAL VIOLATIONS as NOT OK.
#
# Usage:
#   python "C:\Users\alike\edge_factory_live_health_check.py"
# =============================================================================


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


def age_minutes(ts) -> float | None:
    if ts is None or pd.isna(ts):
        return None
    return (now_utc() - pd.Timestamp(ts).tz_convert("UTC")).total_seconds() / 60.0


def status_from_age(age: float | None, warn_min: float, bad_min: float) -> str:
    if age is None:
        return "NO_DATA"
    if age > bad_min:
        return "BAD"
    if age > warn_min:
        return "WARN"
    return "OK"


def summarize_family(name: str, folder: Path, warn_min: float, bad_min: float) -> dict:
    if name == "global_risk_manager":
        heartbeat = safe_read_csv(folder / "global_risk_snapshot.csv")
        open_pos = safe_read_csv(folder / "global_open_positions.csv")
        pending = safe_read_csv(folder / "global_pending_entries.csv")
        closed = safe_read_csv(folder / "global_closed_trades.csv")
        errors = pd.DataFrame()
        rejected = pd.DataFrame()
    else:
        heartbeat = safe_read_csv(folder / "heartbeat.csv")
        open_pos = safe_read_csv(folder / "open_positions.csv")
        pending = safe_read_csv(folder / "pending_entries.csv")
        closed = safe_read_csv(folder / "closed_trades.csv")
        errors = safe_read_csv(folder / "errors.csv")
        rejected = safe_read_csv(folder / "rejected_entries.csv")

    last_hb = get_last_time(heartbeat, "log_time")
    hb_age = age_minutes(last_hb)
    hb_status = status_from_age(hb_age, warn_min, bad_min)

    signals = safe_read_csv(folder / "signals.csv")
    last_signal = get_last_time(signals, "signal_time")
    if name == "market_relative_short" and last_signal is None:
        last_signal = get_last_time(safe_read_csv(folder / "market_snapshot.csv"), "signal_time")

    last_closed = get_last_time(closed, "exit_time")
    last_error = get_last_time(errors, "log_time")

    stale_minutes = 150 if name in {"market_relative_short", "global_risk_manager"} else 30
    stale_pending = 0
    if not pending.empty and "target_entry_time" in pending.columns:
        target_times = pd.to_datetime(pending["target_entry_time"], utc=True, errors="coerce")
        stale_pending = int((target_times < now_utc() - pd.Timedelta(minutes=stale_minutes)).sum())

    overdue_open = 0
    if not open_pos.empty and "planned_exit_time" in open_pos.columns:
        exit_times = pd.to_datetime(open_pos["planned_exit_time"], utc=True, errors="coerce")
        overdue_open = int((exit_times < now_utc() - pd.Timedelta(minutes=30)).sum())

    equity_or_notional = ""
    if name == "global_risk_manager" and not heartbeat.empty and "open_notional_sum" in heartbeat.columns:
        try:
            equity_or_notional = "notional=" + str(float(heartbeat["open_notional_sum"].iloc[-1]))
        except Exception:
            pass
    elif not heartbeat.empty and "equity" in heartbeat.columns:
        try:
            equity_or_notional = float(heartbeat["equity"].iloc[-1])
        except Exception:
            pass

    return {
        "family": name,
        "folder_exists": folder.exists(),
        "heartbeat_status": hb_status,
        "heartbeat_age_min": "" if hb_age is None else round(hb_age, 1),
        "equity_or_notional": equity_or_notional,
        "open": len(open_pos),
        "pending": len(pending),
        "closed": len(closed),
        "rejected": len(rejected),
        "errors": len(errors),
        "stale_pending": stale_pending,
        "overdue_open": overdue_open,
        "last_signal_utc": "" if last_signal is None else str(last_signal),
        "last_closed_utc": "" if last_closed is None else str(last_closed),
        "last_error_utc": "" if last_error is None else str(last_error),
    }


def print_table(df: pd.DataFrame, title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    print("EMPTY" if df.empty else df.to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser(description="Health check for Edge Factory live paper system v3.")
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    ap.add_argument("--heartbeat_warn_min", type=float, default=5.0)
    ap.add_argument("--heartbeat_bad_min", type=float, default=20.0)
    ap.add_argument("--show_tail", type=int, default=10)
    args = ap.parse_args()

    base = Path(args.base_dir)
    folders = {
        "old_short": base / "live_blowoff_short_paper_realistic",
        "session_short": base / "live_session_ret60_reversal_short_paper",
        "impulse_long": base / "live_impulse_event_long_paper",
        "market_relative_short": base / "live_market_relative_extreme_reversion_short_paper",
        "global_risk_manager": base / "global_risk_manager",
    }

    summary = pd.DataFrame([
        summarize_family(name, folder, args.heartbeat_warn_min, args.heartbeat_bad_min)
        for name, folder in folders.items()
    ])

    print("\nEDGE FACTORY LIVE HEALTH CHECK v3")
    print("UTC now:", now_utc())
    print("Base:", base)

    print_table(summary[[
        "family", "folder_exists", "heartbeat_status", "heartbeat_age_min",
        "equity_or_notional", "open", "pending", "closed", "rejected", "errors",
        "stale_pending", "overdue_open", "last_signal_utc", "last_closed_utc", "last_error_utc"
    ]], "SYSTEM SUMMARY")

    global_dir = folders["global_risk_manager"]
    risk_snapshot = safe_read_csv(global_dir / "global_risk_snapshot.csv")
    gate = safe_read_csv(global_dir / "global_gate_decisions.csv")
    violations = safe_read_csv(global_dir / "global_risk_violations.csv")
    global_open = safe_read_csv(global_dir / "global_open_positions.csv")
    global_pending = safe_read_csv(global_dir / "global_pending_entries.csv")

    if not risk_snapshot.empty:
        print_table(risk_snapshot.tail(args.show_tail), "GLOBAL RISK SNAPSHOT - LAST ROWS")

    if not global_open.empty:
        cols = [c for c in ["family_key", "coin", "side", "strategy", "entry_time", "planned_exit_time", "notional", "entry_price"] if c in global_open.columns]
        print_table(global_open[cols], "GLOBAL OPEN POSITIONS")

    if not global_pending.empty:
        cols = [c for c in ["family_key", "coin", "side", "strategy", "signal_time", "target_entry_time", "planned_exit_time", "signal_vol_quote"] if c in global_pending.columns]
        print_table(global_pending[cols], "GLOBAL PENDING ENTRIES")

    if not gate.empty:
        cols = [c for c in ["log_time", "decision", "reason", "family_key", "coin", "side", "target_entry_time", "planned_exit_time"] if c in gate.columns]
        print_table(gate[cols].tail(args.show_tail), "GLOBAL GATE DECISIONS - LAST ROWS")

    recent_violations = pd.DataFrame()
    if not violations.empty:
        cols = [c for c in ["log_time", "severity", "violation_type", "family_key", "coin", "ref", "message"] if c in violations.columns]
        recent_violations = violations[cols].tail(args.show_tail).copy()
        print_table(recent_violations, "GLOBAL RISK VIOLATIONS - LAST ROWS")

    error_rows = []
    for name, folder in folders.items():
        e = safe_read_csv(folder / "errors.csv")
        if not e.empty:
            t = e.tail(3).copy()
            t["family"] = name
            error_rows.append(t)
    if error_rows:
        print_table(pd.concat(error_rows, ignore_index=True).tail(args.show_tail), "LATEST FAMILY ERRORS")
    else:
        print("\nNo family errors found.")

    bad = summary[summary["heartbeat_status"].isin(["BAD", "NO_DATA"])]
    warn = summary[summary["heartbeat_status"].eq("WARN")]
    stale = summary[(summary["stale_pending"] > 0) | (summary["overdue_open"] > 0)]

    active_critical = pd.DataFrame()
    if not risk_snapshot.empty:
        last = risk_snapshot.iloc[-1]
        try:
            if int(last.get("critical_violations", 0)) > 0:
                active_critical = recent_violations[
                    recent_violations.get("severity", pd.Series(dtype=str)).astype(str).str.upper().eq("CRITICAL")
                ].copy()
        except Exception:
            pass

    print("\n" + "=" * 100)
    print("VERDICT")
    print("=" * 100)

    if not active_critical.empty:
        print("NOT OK: active GLOBAL CRITICAL violation exists.")
        print(active_critical.to_string(index=False))
    elif bad.empty and warn.empty and stale.empty:
        print("OK: live paper system looks healthy from files.")
    else:
        if not bad.empty:
            print("BAD / NO_DATA heartbeat:")
            print(bad[["family", "heartbeat_status", "heartbeat_age_min", "folder_exists"]].to_string(index=False))
        if not warn.empty:
            print("\nWARN heartbeat:")
            print(warn[["family", "heartbeat_status", "heartbeat_age_min"]].to_string(index=False))
        if not stale.empty:
            print("\nSTALE pending / overdue open:")
            print(stale[["family", "stale_pending", "overdue_open"]].to_string(index=False))

    if not risk_snapshot.empty:
        last = risk_snapshot.iloc[-1]
        try:
            if int(last["open_positions"]) >= int(last["global_max_positions"]):
                print("\nINFO: Global position limit is full; new pending entries should be blocked until exits occur.")
        except Exception:
            pass


if __name__ == "__main__":
    main()
