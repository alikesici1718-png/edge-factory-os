#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "ret60_reversal_short"

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def profit_factor(pnl: pd.Series) -> float:
    pnl = pd.to_numeric(pnl, errors="coerce").dropna()
    wins = pnl[pnl > 0].sum()
    losses = -pnl[pnl < 0].sum()
    if losses <= 0:
        return 999999.0 if wins > 0 else 0.0
    return float(wins / losses)

def main() -> int:
    out_dir = WORKSPACE / "edge_factory_ret60_market_replay_decision_v4" / f"ret60_replay_decision_v4_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    replay_dir = latest_dir(WORKSPACE / "edge_factory_ret60_market_replay_v4_merge_asof", "ret60_market_replay_v4_")
    replay_state_path = replay_dir / "ret60_market_replay_v4_state.json" if replay_dir else None
    replay_state = read_json(replay_state_path)

    native_csv = Path(replay_state.get("native_csv", "")) if replay_state.get("native_csv") else None

    gates = []
    def gate(name: str, passed: bool, reason: str = ""):
        gates.append({"gate": name, "passed": bool(passed), "reason": str(reason)})

    gate("replay_state_exists", bool(replay_state_path and replay_state_path.exists()), replay_state_path)
    gate("native_csv_exists", bool(native_csv and native_csv.exists()), native_csv)
    gate("replay_has_signals", int(replay_state.get("trade_count") or 0) > 0, replay_state.get("trade_count"))
    gate("live_blocked", replay_state.get("live_allowed") is False, replay_state.get("live_allowed"))
    gate("active_paper_blocked", replay_state.get("active_paper_allowed") is False, replay_state.get("active_paper_allowed"))

    if not native_csv or not native_csv.exists():
        df = pd.DataFrame()
    else:
        df = pd.read_csv(native_csv)

    trade_count = int(len(df))
    symbol_count = int(df["symbol"].nunique()) if "symbol" in df.columns and len(df) else 0
    net_pnl = pd.to_numeric(df.get("net_pnl_usdt", pd.Series(dtype=float)), errors="coerce")
    net_bps = pd.to_numeric(df.get("net_return_bps_native", pd.Series(dtype=float)), errors="coerce")

    net_pnl_sum = float(net_pnl.sum()) if len(net_pnl) else 0.0
    net_bps_mean = float(net_bps.mean()) if len(net_bps) else 0.0
    win_rate = float((net_pnl > 0).mean()) if len(net_pnl) else 0.0
    pf = profit_factor(net_pnl)

    by_symbol = pd.DataFrame()
    if len(df) and "symbol" in df.columns:
        tmp = df.copy()
        tmp["net_pnl_usdt"] = pd.to_numeric(tmp["net_pnl_usdt"], errors="coerce")
        tmp["net_return_bps_native"] = pd.to_numeric(tmp["net_return_bps_native"], errors="coerce")
        by_symbol = (
            tmp.groupby("symbol")
            .agg(
                trades=("event_id", "count"),
                net_pnl_sum=("net_pnl_usdt", "sum"),
                net_bps_mean=("net_return_bps_native", "mean"),
                win_rate=("net_pnl_usdt", lambda x: float((pd.to_numeric(x, errors="coerce") > 0).mean())),
            )
            .reset_index()
            .sort_values("net_pnl_sum", ascending=False)
        )

    positive_symbols = int((by_symbol["net_pnl_sum"] > 0).sum()) if len(by_symbol) else 0
    negative_symbols = int((by_symbol["net_pnl_sum"] < 0).sum()) if len(by_symbol) else 0
    positive_symbol_rate = float(positive_symbols / symbol_count) if symbol_count else 0.0

    # Conservative OS decision rules.
    if trade_count <= 0:
        decision = "RET60_REJECT_NO_MARKET_REPLAY_TRADES"
        reason = "No market replay trades."
    elif net_pnl_sum <= 0 or net_bps_mean <= 0:
        decision = "RET60_REJECT_MARKET_REPLAY_NEGATIVE_EXPECTANCY"
        reason = "Market replay produced trades but net expectancy is negative."
    elif pf < 1.15:
        decision = "RET60_WATCHLIST_WEAK_PROFIT_FACTOR"
        reason = "Positive replay but PF is too weak for promotion."
    elif positive_symbol_rate < 0.55:
        decision = "RET60_WATCHLIST_WEAK_SYMBOL_DISTRIBUTION"
        reason = "Positive replay but symbol distribution is too narrow."
    else:
        decision = "RET60_WATCHLIST_POSITIVE_REPLAY_NEEDS_OOS_AND_SHADOW"
        reason = "Positive replay, but still requires OOS/shadow; not active/live."

    active_paper_allowed = False
    live_allowed = False

    result = {
        "candidate": CANDIDATE,
        "decision": decision,
        "reason": reason,
        "replay_state_path": str(replay_state_path) if replay_state_path else None,
        "native_csv": str(native_csv) if native_csv else None,
        "trade_count": trade_count,
        "symbol_count": symbol_count,
        "net_pnl_sum": net_pnl_sum,
        "net_bps_mean": net_bps_mean,
        "win_rate": win_rate,
        "profit_factor": pf,
        "positive_symbols": positive_symbols,
        "negative_symbols": negative_symbols,
        "positive_symbol_rate": positive_symbol_rate,
        "active_paper_allowed": active_paper_allowed,
        "live_allowed": live_allowed,
        "shadow_allowed": False,
        "promotion_allowed": False,
        "next_action": "MOVE_TO_BATCH_FAMILY_PIPELINE_OR_NEXT_CANDIDATE",
        "gates": gates,
        "gates_passed": sum(1 for g in gates if g["passed"]),
        "gates_total": len(gates),
    }

    write_json(out_dir / "ret60_market_replay_decision_v4_state.json", result)
    if len(by_symbol):
        by_symbol.to_csv(out_dir / "ret60_market_replay_decision_v4_by_symbol.csv", index=False)

    # Append safe research ledger. This does not mutate active config.
    ledger_dir = WORKSPACE / "edge_factory_research_result_ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "master_research_result_ledger.jsonl"
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "candidate": CANDIDATE,
            "module": "ret60_market_replay_decision_v4",
            "decision": decision,
            "trade_count": trade_count,
            "symbol_count": symbol_count,
            "net_pnl_sum": net_pnl_sum,
            "net_bps_mean": net_bps_mean,
            "win_rate": win_rate,
            "profit_factor": pf,
            "active_paper_allowed": False,
            "live_allowed": False,
            "state_path": str(out_dir / "ret60_market_replay_decision_v4_state.json"),
        }, ensure_ascii=False) + "\n")

    print("EDGE FACTORY RET60 MARKET REPLAY DECISION v4")
    print("=" * 100)
    print(f"output_dir: {out_dir}")
    print(f"decision: {decision}")
    print(f"reason: {reason}")
    print(f"trade_count: {trade_count}")
    print(f"symbol_count: {symbol_count}")
    print(f"net_pnl_sum: {net_pnl_sum}")
    print(f"net_bps_mean: {net_bps_mean}")
    print(f"win_rate: {win_rate}")
    print(f"profit_factor: {pf}")
    print(f"positive_symbols: {positive_symbols}")
    print(f"negative_symbols: {negative_symbols}")
    print(f"positive_symbol_rate: {positive_symbol_rate}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print(f"State: {out_dir / 'ret60_market_replay_decision_v4_state.json'}")
    print(f"By symbol: {out_dir / 'ret60_market_replay_decision_v4_by_symbol.csv'}")
    print(f"Ledger: {ledger_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
