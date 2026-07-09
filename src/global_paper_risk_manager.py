"""
Global paper risk manager (v1) that polls four family paper-run folders (old_short, impulse_long, market_relative_short, weak_market_short), builds a unified risk view of open positions and pending entries, and writes allow/block gate decisions based on configurable global and per-family position limits.
Runs in a continuous loop (or once with --once) and outputs risk snapshot, gate decisions, open positions, pending entries, closed trades, and violations CSVs to the paper_run_gate directory; no real orders are placed.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# =============================================================================
# GLOBAL PAPER RISK MANAGER / MONITOR
# =============================================================================
# REAL ORDERS: NO
#
# Reads the 4 paper family folders, builds a single global risk view, and writes
# allow/block recommendations for pending entries. This is a monitor/gate file
# producer; existing paper loggers will not obey it automatically unless patched.
# =============================================================================


def utc_now() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")


def iso(ts: Any) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.Timestamp(ts).tz_convert("UTC").isoformat().replace("+00:00", "Z")


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def append_csv(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            w.writeheader()
        w.writerow(row)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def normalize_time_col(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([pd.NaT] * len(df))
    return pd.to_datetime(df[col], utc=True, errors="coerce")


def infer_side(family_key: str, row: pd.Series | None = None) -> str:
    if row is not None:
        if "side" in row and str(row["side"]).lower() in {"long", "short"}:
            return str(row["side"]).lower()
    if family_key in {"old_short", "session_short", "market_relative_short"}:
        return "short"
    if family_key == "impulse_long":
        return "long"
    return ""


def normalize_open(df: pd.DataFrame, family_key: str, folder: Path) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = family_key
    x["source_folder"] = str(folder)
    if "position_id" not in x.columns:
        x["position_id"] = x["signal_id"].astype(str) if "signal_id" in x.columns else [f"{family_key}_open_{i}" for i in range(len(x))]
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    x["coin"] = x.get("coin", pd.Series([""] * len(x))).astype(str).str.upper()
    x["inst_id"] = x.get("inst_id", x["coin"] + "-USDT-SWAP").astype(str)
    x["strategy"] = x.get("strategy", x.get("family", family_key)).astype(str)
    x["signal_time"] = normalize_time_col(x, "signal_time")
    x["entry_time"] = normalize_time_col(x, "entry_time")
    x["planned_exit_time"] = normalize_time_col(x, "planned_exit_time")
    x["notional"] = pd.to_numeric(x["notional"], errors="coerce") if "notional" in x.columns else np.nan
    if "entry_price" not in x.columns and "raw_entry_close" in x.columns:
        x["entry_price"] = pd.to_numeric(x["raw_entry_close"], errors="coerce")
    elif "entry_price" not in x.columns:
        x["entry_price"] = np.nan
    x["entry_price"] = pd.to_numeric(x["entry_price"], errors="coerce")
    x["entry_vol_quote"] = pd.to_numeric(x["entry_vol_quote"], errors="coerce") if "entry_vol_quote" in x.columns else np.nan
    x["entry_range_bps"] = pd.to_numeric(x["entry_range_bps"], errors="coerce") if "entry_range_bps" in x.columns else np.nan
    x["side"] = [infer_side(family_key, row) for _, row in x.iterrows()]
    x["row_type"] = "open"
    x["global_position_key"] = x["family_key"].astype(str) + "::" + x["position_id"].astype(str)
    cols = ["row_type", "family_key", "position_id", "global_position_key", "coin", "inst_id", "side", "strategy", "signal_time", "entry_time", "planned_exit_time", "notional", "entry_price", "entry_vol_quote", "entry_range_bps", "source_folder"]
    return x[[c for c in cols if c in x.columns]].dropna(subset=["coin"])


def normalize_pending(df: pd.DataFrame, family_key: str, folder: Path) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = family_key
    x["source_folder"] = str(folder)
    if "signal_id" not in x.columns:
        x["signal_id"] = x["position_id"].astype(str) if "position_id" in x.columns else [f"{family_key}_pending_{i}" for i in range(len(x))]
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    x["coin"] = x.get("coin", pd.Series([""] * len(x))).astype(str).str.upper()
    x["inst_id"] = x.get("inst_id", x["coin"] + "-USDT-SWAP").astype(str)
    x["strategy"] = x.get("strategy", x.get("family", family_key)).astype(str)
    x["signal_time"] = normalize_time_col(x, "signal_time")
    x["target_entry_time"] = normalize_time_col(x, "target_entry_time")
    x["planned_exit_time"] = normalize_time_col(x, "planned_exit_time")
    x["signal_vol_quote"] = pd.to_numeric(x["signal_vol_quote"], errors="coerce") if "signal_vol_quote" in x.columns else np.nan
    x["signal_range_bps"] = pd.to_numeric(x["signal_range_bps"], errors="coerce") if "signal_range_bps" in x.columns else np.nan
    x["side"] = [infer_side(family_key, row) for _, row in x.iterrows()]
    x["row_type"] = "pending"
    x["global_signal_key"] = x["family_key"].astype(str) + "::" + x["signal_id"].astype(str)
    cols = ["row_type", "family_key", "signal_id", "global_signal_key", "coin", "inst_id", "side", "strategy", "signal_time", "target_entry_time", "planned_exit_time", "signal_vol_quote", "signal_range_bps", "source_folder"]
    return x[[c for c in cols if c in x.columns]].dropna(subset=["coin"])


def normalize_closed(df: pd.DataFrame, family_key: str, folder: Path) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["family_key"] = family_key
    x["source_folder"] = str(folder)
    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    x["coin"] = x.get("coin", pd.Series([""] * len(x))).astype(str).str.upper()
    x["signal_time"] = normalize_time_col(x, "signal_time")
    x["entry_time"] = normalize_time_col(x, "entry_time")
    x["exit_time"] = normalize_time_col(x, "exit_time")
    if "realistic_net_ret" in x.columns:
        x["net_ret"] = pd.to_numeric(x["realistic_net_ret"], errors="coerce")
    elif "net_ret" in x.columns:
        x["net_ret"] = pd.to_numeric(x["net_ret"], errors="coerce")
    else:
        x["net_ret"] = np.nan
    x["pnl"] = pd.to_numeric(x["pnl"], errors="coerce") if "pnl" in x.columns else np.nan
    x["notional"] = pd.to_numeric(x["notional"], errors="coerce") if "notional" in x.columns else np.nan
    x["strategy"] = x.get("strategy", x.get("family", family_key)).astype(str)
    x["side"] = [infer_side(family_key, row) for _, row in x.iterrows()]
    x["row_type"] = "closed"
    cols = ["row_type", "family_key", "coin", "side", "strategy", "signal_time", "entry_time", "exit_time", "notional", "net_ret", "pnl", "source_folder"]
    return x[[c for c in cols if c in x.columns]].dropna(subset=["coin"])


class GlobalRiskManager:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.base_dir = Path(args.base_dir)
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.families = {
            "old_short": self.base_dir / "live_blowoff_short_paper_realistic",
            "session_short": self.base_dir / "live_session_ret60_reversal_short_paper",
            "impulse_long": self.base_dir / "live_impulse_event_long_paper",
            "market_relative_short": self.base_dir / "live_market_relative_extreme_reversion_short_paper",
        }
        if args.family_config and Path(args.family_config).exists():
            cfg = json.loads(Path(args.family_config).read_text(encoding="utf-8-sig"))
            self.families = {k: Path(v) for k, v in cfg.items()}
        self.max_per_family = {
            "old_short": args.max_old_short,
            "session_short": args.max_session_short,
            "impulse_long": args.max_impulse_long,
            "market_relative_short": args.max_market_relative_short,
        }

    def load_all(self):
        opens, pendings, closed, health = [], [], [], []
        for family_key, folder in self.families.items():
            open_path = folder / "open_positions.csv"
            pending_path = folder / "pending_entries.csv"
            closed_path = folder / "closed_trades.csv"
            no = normalize_open(safe_read_csv(open_path), family_key, folder)
            npd = normalize_pending(safe_read_csv(pending_path), family_key, folder)
            nc = normalize_closed(safe_read_csv(closed_path), family_key, folder)
            if not no.empty:
                opens.append(no)
            if not npd.empty:
                pendings.append(npd)
            if not nc.empty:
                closed.append(nc)
            health.append({
                "family_key": family_key,
                "folder": str(folder),
                "folder_exists": folder.exists(),
                "open_rows": len(no),
                "pending_rows": len(npd),
                "closed_rows": len(nc),
                "open_file_exists": open_path.exists(),
                "pending_file_exists": pending_path.exists(),
                "closed_file_exists": closed_path.exists(),
            })
        return (
            pd.concat(opens, ignore_index=True) if opens else pd.DataFrame(),
            pd.concat(pendings, ignore_index=True) if pendings else pd.DataFrame(),
            pd.concat(closed, ignore_index=True) if closed else pd.DataFrame(),
            health,
        )

    def evaluate_current_violations(self, open_df: pd.DataFrame, pending_df: pd.DataFrame, health: list[dict]) -> pd.DataFrame:
        now = utc_now()
        rows = []
        def add(severity, vtype, msg, family="", coin="", ref=""):
            rows.append({"log_time": iso(now), "severity": severity, "violation_type": vtype, "family_key": family, "coin": coin, "ref": ref, "message": msg})
        for h in health:
            if not h["folder_exists"]:
                add("WARN", "missing_family_folder", f"Folder missing: {h['folder']}", h["family_key"])
            elif not h["open_file_exists"] and not h["pending_file_exists"] and not h["closed_file_exists"]:
                add("INFO", "family_not_started", f"No live files yet in {h['folder']}", h["family_key"])
        if open_df.empty:
            return pd.DataFrame(rows)
        if len(open_df) > self.args.global_max_positions:
            add("CRITICAL", "global_max_positions_exceeded", f"Open {len(open_df)} > limit {self.args.global_max_positions}")
        short_count = int((open_df["side"] == "short").sum())
        long_count = int((open_df["side"] == "long").sum())
        if short_count > self.args.max_short_positions:
            add("CRITICAL", "max_short_positions_exceeded", f"Short {short_count} > limit {self.args.max_short_positions}")
        if long_count > self.args.max_long_positions:
            add("CRITICAL", "max_long_positions_exceeded", f"Long {long_count} > limit {self.args.max_long_positions}")
        for fam, cnt in open_df["family_key"].value_counts().items():
            limit = self.max_per_family.get(str(fam), self.args.default_max_per_family)
            if int(cnt) > limit:
                add("CRITICAL", "max_per_family_exceeded", f"{fam} open {cnt} > limit {limit}", str(fam))
        for coin, cnt in open_df["coin"].value_counts().items():
            if int(cnt) > 1:
                sides = ",".join(sorted(open_df.loc[open_df["coin"] == coin, "side"].astype(str).unique()))
                add("CRITICAL", "same_coin_overlap", f"{coin} has {cnt} open positions; sides={sides}", coin=str(coin))
        for coin, g in open_df.groupby("coin"):
            sides = set(g["side"].astype(str))
            if "long" in sides and "short" in sides:
                add("CRITICAL", "opposite_direction_same_coin", f"{coin} has both long and short open", coin=str(coin))
        if "planned_exit_time" in open_df.columns:
            overdue = open_df.loc[(open_df["planned_exit_time"].notna()) & (open_df["planned_exit_time"] < now - pd.Timedelta(minutes=self.args.exit_grace_minutes))]
            for _, r in overdue.iterrows():
                add("WARN", "open_exit_overdue", f"Planned exit passed: {iso(r['planned_exit_time'])}", str(r["family_key"]), str(r["coin"]), str(r.get("position_id", "")))
        if not pending_df.empty and "target_entry_time" in pending_df.columns:
            stale = pending_df.loc[(pending_df["target_entry_time"].notna()) & (pending_df["target_entry_time"] < now - pd.Timedelta(minutes=self.args.pending_grace_minutes))]
            for _, r in stale.iterrows():
                add("WARN", "pending_entry_stale", f"Target entry passed: {iso(r['target_entry_time'])}", str(r["family_key"]), str(r["coin"]), str(r.get("signal_id", "")))
        return pd.DataFrame(rows)

    def gate_pending(self, open_df: pd.DataFrame, pending_df: pd.DataFrame) -> pd.DataFrame:
        now = utc_now()
        cols = ["log_time", "decision", "reason", "family_key", "signal_id", "coin", "side", "target_entry_time", "planned_exit_time", "signal_vol_quote", "signal_range_bps"]
        if pending_df.empty:
            return pd.DataFrame(columns=cols)
        current = open_df.copy() if not open_df.empty else pd.DataFrame(columns=["coin", "side", "family_key"])
        x = pending_df.copy()
        x["_target"] = x["target_entry_time"] if "target_entry_time" in x.columns else pd.NaT
        x["_vol"] = -pd.to_numeric(x.get("signal_vol_quote", np.nan), errors="coerce").fillna(0.0)
        x = x.sort_values(["_target", "_vol", "family_key", "coin"]).reset_index(drop=True)
        virtual = current.copy()
        rows = []
        for _, r in x.iterrows():
            family = str(r.get("family_key", ""))
            coin = str(r.get("coin", "")).upper()
            side = str(r.get("side", ""))
            decision, reason = "ALLOW", "ok"
            if len(virtual) >= self.args.global_max_positions:
                decision, reason = "BLOCK", "global_max_positions"
            elif coin in set(virtual.get("coin", pd.Series(dtype=str)).astype(str).str.upper()):
                decision, reason = "BLOCK", "same_coin_overlap_global"
            elif side == "short" and int((virtual.get("side", pd.Series(dtype=str)) == "short").sum()) >= self.args.max_short_positions:
                decision, reason = "BLOCK", "max_short_positions"
            elif side == "long" and int((virtual.get("side", pd.Series(dtype=str)) == "long").sum()) >= self.args.max_long_positions:
                decision, reason = "BLOCK", "max_long_positions"
            elif int((virtual.get("family_key", pd.Series(dtype=str)) == family).sum()) >= self.max_per_family.get(family, self.args.default_max_per_family):
                decision, reason = "BLOCK", "max_per_family"
            rows.append({
                "log_time": iso(now), "decision": decision, "reason": reason, "family_key": family,
                "signal_id": str(r.get("signal_id", r.get("global_signal_key", ""))), "coin": coin, "side": side,
                "target_entry_time": iso(r.get("target_entry_time", pd.NaT)), "planned_exit_time": iso(r.get("planned_exit_time", pd.NaT)),
                "signal_vol_quote": r.get("signal_vol_quote", np.nan), "signal_range_bps": r.get("signal_range_bps", np.nan),
            })
            if decision == "ALLOW":
                virtual = pd.concat([virtual, pd.DataFrame([{"coin": coin, "side": side, "family_key": family}])], ignore_index=True)
        return pd.DataFrame(rows, columns=cols)

    def summarize(self, open_df, pending_df, closed_df, violations, gate) -> dict:
        family_open = open_df["family_key"].value_counts().to_dict() if not open_df.empty else {}
        return {
            "log_time": iso(utc_now()),
            "open_positions": int(len(open_df)),
            "pending_entries": int(len(pending_df)),
            "closed_rows_total": int(len(closed_df)),
            "short_open": int((open_df["side"] == "short").sum()) if not open_df.empty else 0,
            "long_open": int((open_df["side"] == "long").sum()) if not open_df.empty else 0,
            "open_notional_sum": float(pd.to_numeric(open_df.get("notional", pd.Series(dtype=float)), errors="coerce").sum()) if not open_df.empty else 0.0,
            "closed_pnl_sum_from_family_logs": float(pd.to_numeric(closed_df.get("pnl", pd.Series(dtype=float)), errors="coerce").sum()) if not closed_df.empty else 0.0,
            "allowed_pending": int((gate["decision"] == "ALLOW").sum()) if not gate.empty else 0,
            "blocked_pending": int((gate["decision"] == "BLOCK").sum()) if not gate.empty else 0,
            "critical_violations": int((violations["severity"] == "CRITICAL").sum()) if not violations.empty and "severity" in violations.columns else 0,
            "warning_violations": int((violations["severity"] == "WARN").sum()) if not violations.empty and "severity" in violations.columns else 0,
            "global_max_positions": self.args.global_max_positions,
            "max_short_positions": self.args.max_short_positions,
            "max_long_positions": self.args.max_long_positions,
            "open_old_short": int(family_open.get("old_short", 0)),
            "open_session_short": int(family_open.get("session_short", 0)),
            "open_impulse_long": int(family_open.get("impulse_long", 0)),
            "open_market_relative_short": int(family_open.get("market_relative_short", 0)),
        }

    def run_once(self) -> dict:
        open_df, pending_df, closed_df, health = self.load_all()
        violations = self.evaluate_current_violations(open_df, pending_df, health)
        gate = self.gate_pending(open_df, pending_df)
        snapshot = self.summarize(open_df, pending_df, closed_df, violations, gate)
        write_csv(self.out_dir / "global_open_positions.csv", open_df)
        write_csv(self.out_dir / "global_pending_entries.csv", pending_df)
        write_csv(self.out_dir / "global_closed_trades.csv", closed_df)
        write_csv(self.out_dir / "global_gate_decisions.csv", gate)
        write_csv(self.out_dir / "global_risk_violations.csv", violations)
        write_csv(self.out_dir / "family_health.csv", pd.DataFrame(health))
        append_csv(self.out_dir / "global_risk_snapshot.csv", snapshot)
        (self.out_dir / "global_state.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        return snapshot

    def run_forever(self) -> None:
        print("=" * 90)
        print("GLOBAL PAPER RISK MANAGER / MONITOR")
        print("=" * 90)
        print("REAL ORDERS: NO")
        print("out_dir:", self.out_dir)
        for k, v in self.families.items():
            print(f"  {k}: {v}")
        print("limits:", {
            "global": self.args.global_max_positions,
            "short": self.args.max_short_positions,
            "long": self.args.max_long_positions,
            "per_family": self.max_per_family,
        })
        print("=" * 90)
        while True:
            try:
                snap = self.run_once()
                print(
                    f"[{snap['log_time']}] open={snap['open_positions']} short={snap['short_open']} long={snap['long_open']} "
                    f"pending={snap['pending_entries']} allow={snap['allowed_pending']} block={snap['blocked_pending']} "
                    f"crit={snap['critical_violations']} warn={snap['warning_violations']} "
                    f"pnl_sum={snap['closed_pnl_sum_from_family_logs']:.2f}"
                )
            except KeyboardInterrupt:
                print("\nStopped by user.")
                raise
            except Exception as e:
                append_csv(self.out_dir / "global_risk_violations.csv", {
                    "log_time": iso(utc_now()), "severity": "CRITICAL", "violation_type": "manager_exception",
                    "family_key": "", "coin": "", "ref": "", "message": f"{type(e).__name__}: {e}",
                })
                print("[ERROR]", type(e).__name__, e)
            time.sleep(self.args.poll_seconds)


def main() -> None:
    ap = argparse.ArgumentParser(description="Global paper risk manager/monitor for 4 strategy families.")
    ap.add_argument("--base_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
    ap.add_argument("--out_dir", default=r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\global_risk_manager")
    ap.add_argument("--family_config", default="")
    ap.add_argument("--global_max_positions", type=int, default=6)
    ap.add_argument("--max_short_positions", type=int, default=5)
    ap.add_argument("--max_long_positions", type=int, default=2)
    ap.add_argument("--default_max_per_family", type=int, default=3)
    ap.add_argument("--max_old_short", type=int, default=3)
    ap.add_argument("--max_session_short", type=int, default=2)
    ap.add_argument("--max_impulse_long", type=int, default=2)
    ap.add_argument("--max_market_relative_short", type=int, default=3)
    ap.add_argument("--pending_grace_minutes", type=int, default=15)
    ap.add_argument("--exit_grace_minutes", type=int, default=10)
    ap.add_argument("--poll_seconds", type=float, default=60.0)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    mgr = GlobalRiskManager(args)
    if args.once:
        print(json.dumps(mgr.run_once(), indent=2))
    else:
        mgr.run_forever()


if __name__ == "__main__":
    main()
