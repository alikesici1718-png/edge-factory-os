"""
Reads live paper-run family trade logs and global risk manager outputs to produce a consolidated "what do we do now?" decision dashboard snapshot for the running v4 priority paper system.
Outputs a dashboard_snapshot.json to the live_decision_dashboard directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


# =============================================================================
# EDGE FACTORY LIVE DECISION DASHBOARD
# =============================================================================
#
# Purpose:
#   Not another logger.
#   Not a strategy.
#   This is the "what do we do now?" dashboard for the running v4 priority paper.
#
# It reads:
#   paper_run_gate_v4_priority/family_config.json
#   family open_positions.csv / closed_trades.csv / pending_entries.csv / rejected_entries.csv / errors.csv
#   global_risk_manager/global_risk_snapshot.csv
#   global_risk_manager/global_gate_decisions.csv
#   global_risk_manager/global_risk_violations.csv
#
# It outputs:
#   live_decision_dashboard/dashboard_snapshot.json
#   live_decision_dashboard/family_live_scorecard.csv
#   live_decision_dashboard/gate_block_summary.csv
#   live_decision_dashboard/action_recommendations.txt
#
# Usage:
#   python "C:\Users\alike\edge_factory_live_decision_dashboard.py"
#
# Or:
#   python "C:\Users\alike\edge_factory_live_decision_dashboard.py" --base_dir "C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_priority"
# =============================================================================


def utc_now() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    except Exception:
        return pd.DataFrame()


def safe_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def parse_time_col(df: pd.DataFrame, col: str) -> pd.Series:
    if df.empty or col not in df.columns:
        return pd.Series(dtype="datetime64[ns, UTC]")
    return pd.to_datetime(df[col], utc=True, errors="coerce")


def age_min(ts) -> float | None:
    if ts is None or pd.isna(ts):
        return None
    return (utc_now() - pd.Timestamp(ts).tz_convert("UTC")).total_seconds() / 60.0


def heartbeat_status(age: float | None, warn: float = 5, bad: float = 20) -> str:
    if age is None:
        return "NO_DATA"
    if age > bad:
        return "BAD"
    if age > warn:
        return "WARN"
    return "OK"


def normalize_closed(df: pd.DataFrame, family_key: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = x.get("family_key", family_key)
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "coin" not in x.columns:
        x["coin"] = ""
    x["coin"] = x["coin"].astype(str).str.upper()

    if "net_ret" not in x.columns:
        if "realistic_net_ret" in x.columns:
            x["net_ret"] = x["realistic_net_ret"]
        elif "gross_ret" in x.columns:
            x["net_ret"] = x["gross_ret"]
        elif "pnl" in x.columns and "notional" in x.columns:
            x["net_ret"] = pd.to_numeric(x["pnl"], errors="coerce") / pd.to_numeric(x["notional"], errors="coerce").replace(0, np.nan)
        else:
            x["net_ret"] = np.nan

    for c in ["pnl", "net_ret", "notional", "equity_after", "equity_before"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")
    for c in ["entry_time", "exit_time", "planned_exit_time", "signal_time"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")

    return x


def normalize_open(df: pd.DataFrame, family_key: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = x.get("family_key", family_key)
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "coin" not in x.columns:
        x["coin"] = ""
    x["coin"] = x["coin"].astype(str).str.upper()
    if "side" not in x.columns:
        x["side"] = "long" if "long" in family_key else "short"
    for c in ["entry_time", "planned_exit_time", "signal_time"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")
    for c in ["notional", "entry_price", "raw_entry_close"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")
    return x


def load_family_config(base: Path) -> dict[str, str]:
    cfg = safe_json(base / "family_config.json")
    if cfg:
        return cfg
    return {
        "old_short": str(base / "live_blowoff_short_paper_realistic"),
        "session_short": str(base / "live_session_ret60_reversal_short_paper"),
        "impulse_long": str(base / "live_impulse_event_long_paper"),
        "market_relative_short": str(base / "live_market_relative_extreme_reversion_short_paper"),
        "weak_market_short": str(base / "live_weak_market_breakdown_short_paper"),
    }


def profit_factor(rets: pd.Series) -> float:
    r = pd.to_numeric(rets, errors="coerce").dropna()
    if r.empty:
        return np.nan
    wins = r[r > 0].sum()
    losses = -r[r < 0].sum()
    if losses <= 0:
        return np.nan
    return float(wins / losses)


def closed_max_drawdown(closed: pd.DataFrame) -> float:
    if closed.empty:
        return 0.0
    x = closed.copy()
    if "exit_time" in x.columns:
        x = x.sort_values("exit_time")
    pnl = pd.to_numeric(x.get("pnl", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    eq = 1000.0 + pnl.cumsum()
    peak = eq.cummax()
    dd = eq / peak - 1.0
    return float(dd.min()) if len(dd) else 0.0


def family_decision(closed_n: int, pnl: float, pf: float, win_rate: float, avg_ret: float, max_dd: float, errors: int) -> str:
    if errors > 50:
        return "TECH_CHECK"
    if closed_n < 10:
        return "TOO_EARLY"
    if closed_n < 30:
        if pnl > 0 and (np.isnan(pf) or pf >= 1.1):
            return "EARLY_OK_KEEP"
        return "EARLY_WEAK_KEEP_SMALL"
    if closed_n < 100:
        if pnl > 0 and pf >= 1.2 and max_dd > -0.10:
            return "PROMISING_KEEP"
        if pnl < 0 and pf < 1.0:
            return "WATCH_FOR_DISABLE"
        return "MIXED_KEEP"
    # mature
    if pnl > 0 and pf >= 1.25 and max_dd > -0.15:
        return "PROMOTE_CANDIDATE"
    if pnl < 0 or pf < 1.0:
        return "DISABLE_CANDIDATE"
    return "KEEP_BASELINE"


def score_family(row: dict) -> float:
    closed_n = float(row.get("closed_trades", 0) or 0)
    pnl = float(row.get("realized_pnl", 0) or 0)
    pf = row.get("profit_factor", np.nan)
    wr = row.get("win_rate", np.nan)
    avg = row.get("avg_net_ret", np.nan)
    dd = float(row.get("closed_max_dd", 0) or 0)
    pf = 1.0 if pd.isna(pf) else float(pf)
    wr = 0.5 if pd.isna(wr) else float(wr)
    avg = 0.0 if pd.isna(avg) else float(avg)

    sample_bonus = min(closed_n / 100.0, 1.0)
    return float(
        pnl
        + 10.0 * max(0.0, pf - 1.0)
        + 5.0 * (wr - 0.5)
        + 100.0 * avg
        + sample_bonus
        - 20.0 * abs(min(0.0, dd))
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\paper_run_gate_v4_priority")
    ap.add_argument("--out_dir", default="")
    args = ap.parse_args()

    base = Path(args.base_dir)
    out = Path(args.out_dir) if args.out_dir else base / "live_decision_dashboard"
    out.mkdir(parents=True, exist_ok=True)

    fams = load_family_config(base)
    global_dir = base / "global_risk_manager"

    snap = safe_read_csv(global_dir / "global_risk_snapshot.csv")
    gate = safe_read_csv(global_dir / "global_gate_decisions.csv")
    vio = safe_read_csv(global_dir / "global_risk_violations.csv")
    gopen = safe_read_csv(global_dir / "global_open_positions.csv")
    gpend = safe_read_csv(global_dir / "global_pending_entries.csv")

    rows = []
    all_closed = []
    all_open = []

    for fam, folder_str in fams.items():
        folder = Path(folder_str)
        hb = safe_read_csv(folder / "heartbeat.csv")
        closed = normalize_closed(safe_read_csv(folder / "closed_trades.csv"), fam)
        opened = normalize_open(safe_read_csv(folder / "open_positions.csv"), fam)
        pending = safe_read_csv(folder / "pending_entries.csv")
        rejected = safe_read_csv(folder / "rejected_entries.csv")
        errors = safe_read_csv(folder / "errors.csv")

        if not closed.empty:
            all_closed.append(closed)
        if not opened.empty:
            all_open.append(opened)

        last_hb = None
        if not hb.empty and "log_time" in hb.columns:
            s = pd.to_datetime(hb["log_time"], utc=True, errors="coerce").dropna()
            last_hb = s.iloc[-1] if len(s) else None
        a = age_min(last_hb)

        rets = pd.to_numeric(closed.get("net_ret", pd.Series(dtype=float)), errors="coerce").dropna()
        pnl = float(pd.to_numeric(closed.get("pnl", pd.Series(dtype=float)), errors="coerce").sum()) if not closed.empty else 0.0
        pf = profit_factor(rets)
        wr = float((rets > 0).mean()) if len(rets) else np.nan
        avg = float(rets.mean()) if len(rets) else np.nan
        med = float(rets.median()) if len(rets) else np.nan
        worst = float(rets.min()) if len(rets) else np.nan
        best = float(rets.max()) if len(rets) else np.nan
        dd = closed_max_drawdown(closed)

        row = {
            "family_key": fam,
            "folder_exists": folder.exists(),
            "heartbeat_status": heartbeat_status(a),
            "heartbeat_age_min": "" if a is None else round(a, 1),
            "open_positions": len(opened),
            "pending_entries": len(pending),
            "closed_trades": len(closed),
            "rejected_entries": len(rejected),
            "errors": len(errors),
            "realized_pnl": pnl,
            "profit_factor": pf,
            "win_rate": wr,
            "avg_net_ret": avg,
            "median_net_ret": med,
            "worst_trade": worst,
            "best_trade": best,
            "closed_max_dd": dd,
        }
        row["score"] = score_family(row)
        row["decision"] = family_decision(len(closed), pnl, pf, wr, avg, dd, len(errors))
        rows.append(row)

    scorecard = pd.DataFrame(rows).sort_values(["score", "realized_pnl"], ascending=False).reset_index(drop=True)
    scorecard.to_csv(out / "family_live_scorecard.csv", index=False)

    # Gate block summary.
    if not gate.empty:
        block_summary = (
            gate.groupby(["family_key", "decision", "reason"])
            .size()
            .reset_index(name="count")
            .sort_values(["family_key", "decision", "count"], ascending=[True, True, False])
        )
    else:
        block_summary = pd.DataFrame(columns=["family_key", "decision", "reason", "count"])
    block_summary.to_csv(out / "gate_block_summary.csv", index=False)

    # Global latest snapshot.
    latest = {}
    if not snap.empty:
        latest = snap.iloc[-1].to_dict()

    crit = int(latest.get("critical_violations", 0) or 0) if latest else 0
    open_positions = int(latest.get("open_positions", len(gopen)) or 0) if latest else len(gopen)
    pending_entries = int(latest.get("pending_entries", len(gpend)) or 0) if latest else len(gpend)

    # Recommendations.
    recs = []
    recs.append(f"UTC now: {utc_now()}")
    recs.append(f"Base: {base}")
    recs.append("")
    recs.append("GLOBAL STATE")
    recs.append(f"- critical_violations: {crit}")
    recs.append(f"- open_positions: {open_positions}")
    recs.append(f"- pending_entries: {pending_entries}")
    if latest:
        recs.append(f"- short_open: {latest.get('short_open', '')}")
        recs.append(f"- long_open: {latest.get('long_open', '')}")
        recs.append(f"- allowed_pending: {latest.get('allowed_pending', '')}")
        recs.append(f"- blocked_pending: {latest.get('blocked_pending', '')}")
        recs.append(f"- weak_market_backup_only: {latest.get('weak_market_backup_only', '')}")
    recs.append("")

    if crit > 0:
        recs.append("ACTION: STOP ADDING ANYTHING. Fix critical risk violation first.")
    else:
        recs.append("ACTION: Live system is allowed to keep running.")

    bad_hb = scorecard[scorecard["heartbeat_status"].isin(["BAD", "NO_DATA"])]
    if not bad_hb.empty:
        recs.append("ACTION: Some logger heartbeats are BAD/NO_DATA. Check these windows:")
        for _, r in bad_hb.iterrows():
            recs.append(f"  - {r['family_key']}: {r['heartbeat_status']}")
    else:
        recs.append("ACTION: All family heartbeats look acceptable.")

    recs.append("")
    recs.append("FAMILY DECISIONS")
    for _, r in scorecard.iterrows():
        recs.append(
            f"- {r['family_key']}: {r['decision']} | closed={r['closed_trades']} "
            f"open={r['open_positions']} pnl={r['realized_pnl']:.4f} "
            f"PF={r['profit_factor'] if pd.notna(r['profit_factor']) else 'nan'} "
            f"WR={r['win_rate'] if pd.notna(r['win_rate']) else 'nan'}"
        )

    recs.append("")
    recs.append("NEXT RESEARCH TASKS")
    closed_total = int(scorecard["closed_trades"].sum()) if not scorecard.empty else 0
    if closed_total < 30:
        recs.append("- Live sample is still tiny. Do not promote/kill families from live PnL yet.")
        recs.append("- Offline work can continue: squeeze filter for weak_market/old_short and priority-backtest.")
    elif closed_total < 100:
        recs.append("- Start early live-vs-backtest comparison per family.")
        recs.append("- Check whether blocked signals would have performed better than allowed signals.")
    else:
        recs.append("- Start formal family promotion/retirement decisions.")
        recs.append("- Compare live PF/winrate against historical expected ranges.")

    recs.append("")
    recs.append("WATCH LIST")
    recs.append("- weak_market_short must remain backup/low priority unless market_relative is inactive.")
    recs.append("- market_relative_short should not exceed max 3 open.")
    recs.append("- same coin overlap must remain blocked.")
    recs.append("- if old_short keeps dominating live results, give it first slot priority permanently.")

    text = "\n".join(recs)
    (out / "action_recommendations.txt").write_text(text, encoding="utf-8")

    snapshot = {
        "log_time": str(utc_now()),
        "base_dir": str(base),
        "critical_violations": crit,
        "open_positions": open_positions,
        "pending_entries": pending_entries,
        "families": scorecard.to_dict("records"),
        "out_dir": str(out),
    }
    (out / "dashboard_snapshot.json").write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    # Console output.
    print("\n" + "=" * 100)
    print("EDGE FACTORY LIVE DECISION DASHBOARD")
    print("=" * 100)
    print(text)

    print("\n" + "=" * 100)
    print("FAMILY LIVE SCORECARD")
    print("=" * 100)
    show_cols = [
        "family_key", "decision", "score", "heartbeat_status", "open_positions", "pending_entries",
        "closed_trades", "realized_pnl", "profit_factor", "win_rate", "avg_net_ret",
        "worst_trade", "closed_max_dd", "rejected_entries", "errors",
    ]
    print(scorecard[show_cols].to_string(index=False) if not scorecard.empty else "EMPTY")

    print("\n" + "=" * 100)
    print("GATE BLOCK SUMMARY")
    print("=" * 100)
    print(block_summary.to_string(index=False) if not block_summary.empty else "EMPTY")

    print("\nSaved:")
    print(out)


if __name__ == "__main__":
    main()
