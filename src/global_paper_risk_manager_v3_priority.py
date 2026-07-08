from __future__ import annotations

import argparse
import csv
import json
import re
import time
from pathlib import Path
from typing import Any

import pandas as pd


# =============================================================================
# GLOBAL PAPER RISK MANAGER v3 - PRIORITY ALLOCATOR
# =============================================================================
#
# This replaces global_paper_risk_manager_v2.py.
#
# It is still REAL ORDERS: NO.
#
# Main difference:
#   v2 = risk limits only
#   v3 = risk limits + family priority + backup-family rules
#
# Default family priority:
#   old_short              100
#   impulse_long            90
#   session_short           80
#   market_relative_short   70
#   weak_market_short       30
#
# Important rule:
#   weak_market_short is treated as backup/low-priority.
#   By default it is BLOCKED if market_relative_short already has open position(s)
#   or is being allowed in the current allocation cycle.
#
# Output files remain compatible with health_check_v5 and performance_analyzer_v3:
#   global_risk_snapshot.csv
#   global_open_positions.csv
#   global_pending_entries.csv
#   global_closed_trades.csv
#   global_gate_decisions.csv
#   global_risk_violations.csv
# =============================================================================


def now_utc() -> pd.Timestamp:
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


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def append_csv(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            w.writeheader()
        w.writerow(row)


_BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_]+$")


def parse_simple_value(raw: str) -> Any:
    txt = raw.strip()
    if not txt:
        raise ValueError("empty value")
    if (txt.startswith("'") and txt.endswith("'")) or (txt.startswith('"') and txt.endswith('"')):
        return txt[1:-1]

    low = txt.lower()
    if low == "true":
        return True
    if low == "false":
        return False

    try:
        if any(ch in txt for ch in ".eE"):
            return float(txt)
        return int(txt)
    except ValueError:
        if _BARE_KEY_RE.match(txt):
            return txt
        raise


def parse_bare_key_object(raw: str) -> dict:
    txt = raw.strip()
    if not (txt.startswith("{") and txt.endswith("}")):
        raise ValueError("bare-key object must be wrapped in braces")

    body = txt[1:-1].strip()
    if not body:
        return {}

    out = {}
    for item in body.split(","):
        if ":" not in item:
            raise ValueError(f"missing ':' in item {item!r}")
        key_raw, value_raw = item.split(":", 1)
        key = key_raw.strip()
        if (key.startswith("'") and key.endswith("'")) or (key.startswith('"') and key.endswith('"')):
            key = key[1:-1]
        if not _BARE_KEY_RE.match(key):
            raise ValueError(f"invalid key {key!r}")
        out[key] = parse_simple_value(value_raw)

    return out


def parse_json_arg(raw: str, default: dict) -> dict:
    txt = str(raw or "").strip()
    if not txt:
        return default
    if (txt.startswith("'") and txt.endswith("'")) or (txt.startswith('"') and txt.endswith('"')):
        txt = txt[1:-1].strip()
    try:
        parsed = json.loads(txt)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError(f"expected JSON object, got {type(parsed).__name__}")
    except Exception as json_error:
        try:
            parsed = json.loads(txt.replace(r"\"", '"'))
            if isinstance(parsed, dict):
                return parsed
            raise ValueError(f"expected JSON object, got {type(parsed).__name__}")
        except Exception:
            try:
                return parse_bare_key_object(txt)
            except Exception as bare_error:
                print(f"[WARN] JSON parse failed: {json_error}; bare-key parse failed: {bare_error}; raw={txt!r}; using default={default}")
        return default


def infer_side(family_key: str, df: pd.DataFrame) -> pd.Series:
    if "side" in df.columns:
        s = df["side"].astype(str).str.lower()
        s = s.where(s.isin(["long", "short"]), "")
    else:
        s = pd.Series([""] * len(df), index=df.index)

    default = "long" if "long" in family_key else "short"
    s = s.replace("", default)
    s = s.mask(~s.isin(["long", "short"]), default)
    return s


def normalize_positions(df: pd.DataFrame, family_key: str, source_folder: Path, kind: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    x = df.copy()
    x["family_key"] = x.get("family_key", family_key)
    x["family_key"] = x["family_key"].astype(str).replace("", family_key)
    x["source_folder"] = str(source_folder)

    if "coin" not in x.columns and "inst_id" in x.columns:
        x["coin"] = x["inst_id"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    if "coin" not in x.columns:
        x["coin"] = ""
    x["coin"] = x["coin"].astype(str).str.upper()

    if "inst_id" not in x.columns:
        x["inst_id"] = x["coin"] + "-USDT-SWAP"

    x["side"] = infer_side(family_key, x)

    for c in ["signal_time", "target_entry_time", "entry_time", "exit_time", "planned_exit_time", "log_time"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], utc=True, errors="coerce")

    for c in ["notional", "entry_price", "signal_vol_quote", "entry_vol_quote", "pnl", "realistic_net_ret", "net_ret"]:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")

    # EDGE_FACTORY_CANONICAL_SIGNAL_ID_FALLBACK_V1
    # Canonical fallback must match logger-side IDs: COIN_STRATEGY_OR_FAMILY_YYYYMMDDTHHMMSSZ.
    # Preserve existing logger-provided signal_id whenever present; only fill missing/blank rows.
    if "target_entry_time" in x.columns:
        time_src = x["target_entry_time"]
    elif "signal_time" in x.columns:
        time_src = x["signal_time"]
    elif "log_time" in x.columns:
        time_src = x["log_time"]
    else:
        time_src = pd.Series([""] * len(x), index=x.index)
    base_time = pd.to_datetime(time_src, errors="coerce", utc=True).dt.strftime("%Y%m%dT%H%M%SZ").fillna("")
    if "strategy" in x.columns:
        id_part = x["strategy"].astype(str)
    elif "family" in x.columns:
        id_part = x["family"].astype(str)
    else:
        id_part = x["family_key"].astype(str)
    if "coin" in x.columns:
        coin_part = x["coin"].astype(str)
    elif "symbol" in x.columns:
        coin_part = x["symbol"].astype(str).str.replace("-USDT-SWAP", "", regex=False)
    else:
        coin_part = pd.Series(["UNKNOWN"] * len(x), index=x.index)
    fallback_signal_id = coin_part + "_" + id_part + "_" + base_time.astype(str)
    if "signal_id" not in x.columns:
        x["signal_id"] = fallback_signal_id
    else:
        sid_raw = x["signal_id"]
        sid_str = sid_raw.astype(str)
        blank_sid = sid_raw.isna() | sid_str.str.strip().isin(["", "nan", "None"])
        x["signal_id"] = sid_str
        x.loc[blank_sid, "signal_id"] = fallback_signal_id[blank_sid]

    if "strategy" not in x.columns:
        x["strategy"] = x.get("family", family_key)

    return x


class PriorityGlobalRiskManager:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        cfg_text = Path(args.family_config).read_text(encoding="utf-8-sig")
        self.family_config: dict[str, str] = json.loads(cfg_text)

        self.max_per_family = parse_json_arg(
            args.max_per_family_json,
            {
                "old_short": 3,
                "session_short": 2,
                "impulse_long": 2,
                "market_relative_short": 3,
                "weak_market_short": 1,
            },
        )
        self.family_priority = parse_json_arg(
            args.family_priority_json,
            {
                "old_short": 100,
                "impulse_long": 90,
                "session_short": 80,
                "market_relative_short": 70,
                "weak_market_short": 30,
            },
        )

        self.snapshot_path = self.out_dir / "global_risk_snapshot.csv"
        self.open_path = self.out_dir / "global_open_positions.csv"
        self.pending_path = self.out_dir / "global_pending_entries.csv"
        self.closed_path = self.out_dir / "global_closed_trades.csv"
        self.gate_path = self.out_dir / "global_gate_decisions.csv"
        self.violations_path = self.out_dir / "global_risk_violations.csv"
        self.config_copy_path = self.out_dir / "global_risk_config.json"

        self.config_copy_path.write_text(json.dumps({
            "family_config": self.family_config,
            "max_per_family": self.max_per_family,
            "family_priority": self.family_priority,
            "args": vars(args),
        }, indent=2), encoding="utf-8")

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        open_parts = []
        pending_parts = []
        closed_parts = []

        for family_key, folder_str in self.family_config.items():
            folder = Path(folder_str)

            open_df = normalize_positions(safe_read_csv(folder / "open_positions.csv"), family_key, folder, "open")
            pending_df = normalize_positions(safe_read_csv(folder / "pending_entries.csv"), family_key, folder, "pending")
            closed_df = normalize_positions(safe_read_csv(folder / "closed_trades.csv"), family_key, folder, "closed")

            if not open_df.empty:
                open_parts.append(open_df)
            if not pending_df.empty:
                pending_parts.append(pending_df)
            if not closed_df.empty:
                closed_parts.append(closed_df)

        open_all = pd.concat(open_parts, ignore_index=True) if open_parts else pd.DataFrame()
        pending_all = pd.concat(pending_parts, ignore_index=True) if pending_parts else pd.DataFrame()
        closed_all = pd.concat(closed_parts, ignore_index=True) if closed_parts else pd.DataFrame()

        return open_all, pending_all, closed_all

    def critical_violations(self, open_all: pd.DataFrame, pending_all: pd.DataFrame) -> list[dict]:
        rows = []
        t = iso(now_utc())

        open_count = len(open_all)
        short_open = int((open_all.get("side", pd.Series(dtype=str)).astype(str) == "short").sum()) if not open_all.empty else 0
        long_open = int((open_all.get("side", pd.Series(dtype=str)).astype(str) == "long").sum()) if not open_all.empty else 0

        if open_count > self.args.global_max_positions:
            rows.append({"log_time": t, "severity": "CRITICAL", "violation_type": "global_max_positions_exceeded", "family_key": "", "coin": "", "ref": "", "message": f"Open {open_count} > limit {self.args.global_max_positions}"})
        if short_open > self.args.max_short_positions:
            rows.append({"log_time": t, "severity": "CRITICAL", "violation_type": "max_short_positions_exceeded", "family_key": "", "coin": "", "ref": "", "message": f"Short {short_open} > limit {self.args.max_short_positions}"})
        if long_open > self.args.max_long_positions:
            rows.append({"log_time": t, "severity": "CRITICAL", "violation_type": "max_long_positions_exceeded", "family_key": "", "coin": "", "ref": "", "message": f"Long {long_open} > limit {self.args.max_long_positions}"})

        if not open_all.empty and "coin" in open_all.columns:
            dup = open_all.groupby("coin").size()
            for coin, n in dup[dup > 1].items():
                sides = ",".join(sorted(open_all.loc[open_all["coin"] == coin, "side"].astype(str).unique()))
                rows.append({"log_time": t, "severity": "CRITICAL", "violation_type": "same_coin_overlap", "family_key": "", "coin": coin, "ref": "", "message": f"{coin} has {int(n)} open positions; sides={sides}"})

        if not open_all.empty:
            fam_counts = open_all.groupby("family_key").size()
            for fam, n in fam_counts.items():
                lim = self.max_per_family.get(str(fam))
                if lim is not None and int(n) > int(lim):
                    rows.append({"log_time": t, "severity": "CRITICAL", "violation_type": "max_per_family_exceeded", "family_key": fam, "coin": "", "ref": "", "message": f"{fam} open {int(n)} > limit {lim}"})

        if not pending_all.empty and "target_entry_time" in pending_all.columns:
            cutoff = now_utc() - pd.Timedelta(minutes=self.args.pending_grace_minutes)
            stale = pending_all.loc[pending_all["target_entry_time"] < cutoff]
            for _, r in stale.head(100).iterrows():
                rows.append({
                    "log_time": t,
                    "severity": "WARN",
                    "violation_type": "pending_entry_stale",
                    "family_key": str(r.get("family_key", "")),
                    "coin": str(r.get("coin", "")),
                    "ref": str(r.get("signal_id", "")),
                    "message": f"Target entry passed: {iso(r.get('target_entry_time'))}",
                })

        return rows

    def make_gate_decisions(self, open_all: pd.DataFrame, pending_all: pd.DataFrame) -> pd.DataFrame:
        if pending_all.empty:
            return pd.DataFrame(columns=[
                "log_time", "decision", "reason", "family_key", "coin", "side",
                "signal_id", "target_entry_time", "planned_exit_time", "strategy",
                "priority", "signal_score",
            ])

        x = pending_all.copy()
        if "target_entry_time" in x.columns:
            x["_target_sort"] = pd.to_datetime(x["target_entry_time"], utc=True, errors="coerce")
        else:
            x["_target_sort"] = pd.NaT

        # Family priority first. Then higher volume. Then earlier target time.
        x["_priority"] = x["family_key"].astype(str).map(lambda f: int(self.family_priority.get(f, 0)))

        if "signal_vol_quote" in x.columns:
            x["_vol"] = pd.to_numeric(x["signal_vol_quote"], errors="coerce").fillna(0.0)
        elif "entry_vol_quote" in x.columns:
            x["_vol"] = pd.to_numeric(x["entry_vol_quote"], errors="coerce").fillna(0.0)
        else:
            x["_vol"] = 0.0

        # Optional extra signal scoring by family/volume.
        x["_signal_score"] = x["_priority"] * 1_000_000_000.0 + x["_vol"]

        x = x.sort_values(
            ["_priority", "_target_sort", "_vol", "family_key", "coin"],
            ascending=[False, True, False, True, True],
        ).reset_index(drop=True)

        open_coins = set(open_all["coin"].astype(str)) if not open_all.empty and "coin" in open_all.columns else set()
        allowed_coins = set()

        open_count = len(open_all)
        short_open = int((open_all.get("side", pd.Series(dtype=str)).astype(str) == "short").sum()) if not open_all.empty else 0
        long_open = int((open_all.get("side", pd.Series(dtype=str)).astype(str) == "long").sum()) if not open_all.empty else 0
        family_counts = open_all.groupby("family_key").size().to_dict() if not open_all.empty and "family_key" in open_all.columns else {}

        open_market_relative = int(family_counts.get("market_relative_short", 0))
        allowed_market_relative = 0

        rows = []
        t = iso(now_utc())

        for _, r in x.iterrows():
            fam = str(r.get("family_key", ""))
            coin = str(r.get("coin", "")).upper()
            side = str(r.get("side", "short")).lower()
            sid = str(r.get("signal_id", ""))

            decision = "ALLOW"
            reason = "ok"

            if coin in open_coins:
                decision, reason = "BLOCK", "same_coin_overlap_global"
            elif coin in allowed_coins:
                decision, reason = "BLOCK", "same_coin_overlap_pending"
            elif open_count >= self.args.global_max_positions:
                decision, reason = "BLOCK", "global_max_positions"
            elif side == "short" and short_open >= self.args.max_short_positions:
                decision, reason = "BLOCK", "max_short_positions"
            elif side == "long" and long_open >= self.args.max_long_positions:
                decision, reason = "BLOCK", "max_long_positions"
            elif fam in self.max_per_family and family_counts.get(fam, 0) >= int(self.max_per_family[fam]):
                decision, reason = "BLOCK", "max_per_family"
            elif (
                fam == "weak_market_short"
                and self.args.weak_market_backup_only
                and (open_market_relative + allowed_market_relative) > 0
            ):
                decision, reason = "BLOCK", "weak_market_backup_only_market_relative_active"

            if decision == "ALLOW":
                open_count += 1
                family_counts[fam] = family_counts.get(fam, 0) + 1
                allowed_coins.add(coin)
                if side == "short":
                    short_open += 1
                elif side == "long":
                    long_open += 1
                if fam == "market_relative_short":
                    allowed_market_relative += 1

            rows.append({
                "log_time": t,
                "decision": decision,
                "reason": reason,
                "family_key": fam,
                "coin": coin,
                "side": side,
                "signal_id": sid,
                "target_entry_time": iso(r.get("target_entry_time")) if "target_entry_time" in r else "",
                "planned_exit_time": iso(r.get("planned_exit_time")) if "planned_exit_time" in r else "",
                "strategy": str(r.get("strategy", "")),
                "priority": int(self.family_priority.get(fam, 0)),
                "signal_score": float(r.get("_signal_score", 0.0)),
            })

        return pd.DataFrame(rows)

    def run_once(self) -> None:
        open_all, pending_all, closed_all = self.load_all()

        gate = self.make_gate_decisions(open_all, pending_all)
        violations = self.critical_violations(open_all, pending_all)

        write_csv(self.open_path, open_all)
        write_csv(self.pending_path, pending_all)
        write_csv(self.closed_path, closed_all)
        write_csv(self.gate_path, gate)

        vdf = pd.DataFrame(violations)
        write_csv(self.violations_path, vdf)

        short_open = int((open_all.get("side", pd.Series(dtype=str)).astype(str) == "short").sum()) if not open_all.empty else 0
        long_open = int((open_all.get("side", pd.Series(dtype=str)).astype(str) == "long").sum()) if not open_all.empty else 0
        open_notional = float(pd.to_numeric(open_all.get("notional", pd.Series(dtype=float)), errors="coerce").sum()) if not open_all.empty else 0.0
        closed_pnl = float(pd.to_numeric(closed_all.get("pnl", pd.Series(dtype=float)), errors="coerce").sum()) if not closed_all.empty else 0.0

        fam_open = {}
        fam_pending = {}
        for fam in self.family_config:
            fam_open[f"open_{fam}"] = int((open_all.get("family_key", pd.Series(dtype=str)).astype(str) == fam).sum()) if not open_all.empty else 0
            fam_pending[f"pending_{fam}"] = int((pending_all.get("family_key", pd.Series(dtype=str)).astype(str) == fam).sum()) if not pending_all.empty else 0

        snapshot = {
            "log_time": iso(now_utc()),
            "open_positions": int(len(open_all)),
            "pending_entries": int(len(pending_all)),
            "closed_rows_total": int(len(closed_all)),
            "short_open": short_open,
            "long_open": long_open,
            "open_notional_sum": open_notional,
            "closed_pnl_sum_from_family_logs": closed_pnl,
            "allowed_pending": int((gate.get("decision", pd.Series(dtype=str)) == "ALLOW").sum()) if not gate.empty else 0,
            "blocked_pending": int((gate.get("decision", pd.Series(dtype=str)) == "BLOCK").sum()) if not gate.empty else 0,
            "critical_violations": int((vdf.get("severity", pd.Series(dtype=str)) == "CRITICAL").sum()) if not vdf.empty else 0,
            "warning_violations": int((vdf.get("severity", pd.Series(dtype=str)) == "WARN").sum()) if not vdf.empty else 0,
            "global_max_positions": int(self.args.global_max_positions),
            "max_short_positions": int(self.args.max_short_positions),
            "max_long_positions": int(self.args.max_long_positions),
            "weak_market_backup_only": bool(self.args.weak_market_backup_only),
            **fam_open,
            **fam_pending,
        }
        append_csv(self.snapshot_path, snapshot)

        print(
            f"[{snapshot['log_time']}] open={snapshot['open_positions']} pending={snapshot['pending_entries']} "
            f"allowed={snapshot['allowed_pending']} blocked={snapshot['blocked_pending']} "
            f"crit={snapshot['critical_violations']} warn={snapshot['warning_violations']}"
        )

    def run_forever(self) -> None:
        print("=" * 100)
        print("GLOBAL PAPER RISK MANAGER v3 - PRIORITY ALLOCATOR")
        print("=" * 100)
        print("REAL ORDERS: NO")
        print("out_dir:", self.out_dir)
        print("families:", json.dumps(self.family_config, indent=2))
        print("max_per_family:", self.max_per_family)
        print("family_priority:", self.family_priority)
        print("weak_market_backup_only:", self.args.weak_market_backup_only)
        print("=" * 100)

        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                print("\nStopped by user.")
                raise
            except Exception as e:
                append_csv(self.out_dir / "errors.csv", {
                    "log_time": iso(now_utc()),
                    "where": "main_loop",
                    "error_type": type(e).__name__,
                    "error": str(e),
                })
                print("[ERROR]", type(e).__name__, e)

            if self.args.once:
                break
            time.sleep(self.args.poll_seconds)


def main() -> None:
    ap = argparse.ArgumentParser(description="Global paper risk manager v3 priority allocator.")
    ap.add_argument("--family_config", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--global_max_positions", type=int, default=6)
    ap.add_argument("--max_short_positions", type=int, default=5)
    ap.add_argument("--max_long_positions", type=int, default=2)
    ap.add_argument("--max_per_family_json", default='{"old_short":3,"session_short":2,"impulse_long":2,"market_relative_short":3,"weak_market_short":1}')
    ap.add_argument("--family_priority_json", default='{"old_short":100,"impulse_long":90,"session_short":80,"market_relative_short":70,"weak_market_short":30}')
    ap.add_argument("--weak_market_backup_only", action="store_true", default=True)
    ap.add_argument("--allow_weak_market_alongside_market_relative", action="store_false", dest="weak_market_backup_only")
    ap.add_argument("--pending_grace_minutes", type=int, default=180)
    ap.add_argument("--poll_seconds", type=float, default=60.0)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()

    mgr = PriorityGlobalRiskManager(args)
    mgr.run_forever()


if __name__ == "__main__":
    main()
