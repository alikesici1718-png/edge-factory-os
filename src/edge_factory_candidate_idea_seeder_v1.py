#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seeds the candidate idea bank with a predefined set of initial strategy ideas covering panic rebound, relative weakness snapback, and similar market regimes. Invokes the idea bank module via subprocess to register each seed idea and writes a seeder run report with success/failure status per idea.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

USERDIR = Path(r"C:\Users\alike")
WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_candidate_idea_seeder_v1"
IDEA_BANK = USERDIR / "edge_factory_candidate_idea_bank_v1.py"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_idea_bank(args: list[str]) -> dict[str, Any]:
    try:
        p = subprocess.run(
            [sys.executable, str(IDEA_BANK)] + args,
            capture_output=True,
            text=True,
            timeout=180,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout_tail": p.stdout[-4000:],
            "stderr_tail": p.stderr[-2000:],
            "args": args,
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": repr(e),
            "args": args,
        }

def main() -> int:
    out_dir = OUT_ROOT / f"candidate_idea_seeder_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    seed_ideas = [
        {
            "candidate_key": "market_panic_rebound_long_v1",
            "family_key": "panic_rebound_long",
            "side": "long",
            "edge": "When the whole market dumps sharply and a coin shows extreme negative move with stabilization, short-term mean reversion may occur.",
            "regime": "broad market panic / liquidation flush",
            "why": "Forced selling and liquidity cascades can overshoot; rebound candidates may appear after extreme downside dislocation.",
            "failure_modes": "trend crash continues, liquidity disappears, bounce is too slow, costs erase mean reversion",
            "universe": "OKX USDT swaps ready universe",
            "timeframe": "1h candles",
            "lookback_window": "6h to 24h",
            "required_columns": "symbol,time,close,coin_ret6_bps,coin_ret24_bps,mkt_ret6_bps,mkt_ret24_bps,entry_vol_quote,entry_range_bps",
            "entry_rule": "mkt_ret6_bps <= -250 and coin_ret6_bps <= -400 and entry_vol_quote >= liquidity_floor",
            "exit_rule": "fixed_hold_6h_or_12h",
            "hold_time": "6h",
            "cooldown": "24h per symbol"
        },
        {
            "candidate_key": "relative_weakness_snapback_long_v1",
            "family_key": "relative_snapback_long",
            "side": "long",
            "edge": "A coin that underperforms the market extremely over a short window may snap back if the market itself is not collapsing.",
            "regime": "neutral or mildly positive market with isolated coin weakness",
            "why": "Relative underperformance can be temporary liquidity imbalance rather than true information, creating rebound pressure.",
            "failure_modes": "coin-specific bad news, delisting/news risk, weak coin keeps trending down, low liquidity",
            "universe": "OKX USDT swaps ready universe",
            "timeframe": "1h candles",
            "lookback_window": "6h to 24h",
            "required_columns": "symbol,time,close,coin_ret6_bps,mkt_ret6_bps,rel_ret_bps,entry_vol_quote,entry_range_bps",
            "entry_rule": "rel_ret_bps <= -500 and mkt_ret6_bps >= -100 and entry_vol_quote >= liquidity_floor",
            "exit_rule": "fixed_hold_12h",
            "hold_time": "12h",
            "cooldown": "24h per symbol"
        },
        {
            "candidate_key": "extreme_blowoff_reversion_short_v1",
            "family_key": "extreme_reversion_short",
            "side": "short",
            "edge": "A coin that pumps far above the market over a short window may mean-revert after blowoff exhaustion.",
            "regime": "isolated speculative pump / relative overextension",
            "why": "Extreme relative outperformance often reflects temporary chase flow; after flow exhausts, reversion can dominate.",
            "failure_modes": "true listing/news repricing, squeeze continues, borrow/perp crowding, too many duplicate signals",
            "universe": "OKX USDT swaps ready universe",
            "timeframe": "1h candles",
            "lookback_window": "6h to 24h",
            "required_columns": "symbol,time,close,coin_ret6_bps,coin_ret24_bps,mkt_ret6_bps,rel_ret_bps,entry_vol_quote,entry_range_bps",
            "entry_rule": "coin_ret6_bps >= 300 and rel_ret_bps >= 600 and entry_vol_quote >= liquidity_floor",
            "exit_rule": "fixed_hold_24h",
            "hold_time": "24h",
            "cooldown": "24h per symbol"
        },
        {
            "candidate_key": "market_relative_continuation_short_v1",
            "family_key": "relative_continuation_short",
            "side": "short",
            "edge": "Coins showing strong downside relative momentum during weak market regimes may continue lower over short holds.",
            "regime": "bearish broad market / risk-off continuation",
            "why": "In risk-off regimes, weak coins can keep underperforming as liquidity rotates away and forced exits continue.",
            "failure_modes": "sharp relief rally, crowded short, market regime flips, weak signal overlaps with rebound family",
            "universe": "OKX USDT swaps ready universe",
            "timeframe": "1h candles",
            "lookback_window": "3h to 12h",
            "required_columns": "symbol,time,close,coin_ret3_bps,coin_ret6_bps,mkt_ret3_bps,mkt_ret6_bps,rel_ret_bps,entry_vol_quote",
            "entry_rule": "mkt_ret6_bps <= -150 and rel_ret_bps <= -300 and coin_ret3_bps <= -150",
            "exit_rule": "fixed_hold_6h",
            "hold_time": "6h",
            "cooldown": "12h per symbol"
        },
        {
            "candidate_key": "post_impulse_drift_long_v1",
            "family_key": "impulse_drift_long",
            "side": "long",
            "edge": "High-volume upside impulse with market confirmation may drift upward if not immediately mean-reverted.",
            "regime": "risk-on or sector-wide momentum",
            "why": "Strong confirmed impulse can attract continuation flow and delayed participation after breakout.",
            "failure_modes": "pump-and-dump, entry too late, impulse already exhausted, high spread symbols",
            "universe": "OKX USDT swaps ready universe",
            "timeframe": "1h candles",
            "lookback_window": "3h to 12h",
            "required_columns": "symbol,time,close,coin_ret3_bps,coin_ret6_bps,mkt_ret3_bps,mkt_ret6_bps,entry_vol_quote,entry_range_bps",
            "entry_rule": "coin_ret3_bps >= 250 and mkt_ret3_bps >= 50 and entry_vol_quote >= liquidity_floor",
            "exit_rule": "fixed_hold_6h",
            "hold_time": "6h",
            "cooldown": "12h per symbol"
        }
    ]

    results = []

    for idea in seed_ideas:
        args = []
        for k, v in idea.items():
            args.extend([f"--{k}", str(v)])
        result = run_idea_bank(args)
        results.append({
            "candidate_key": idea["candidate_key"],
            "family_key": idea["family_key"],
            "side": idea["side"],
            "ok": result["ok"],
            "returncode": result["returncode"],
            "stdout_tail": result["stdout_tail"],
            "stderr_tail": result["stderr_tail"],
        })

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "seeder_status": "CANDIDATE_IDEAS_SEEDED",
        "seed_count": len(seed_ideas),
        "success_count": sum(1 for r in results if r["ok"]),
        "results": results,
        "live_allowed": False,
        "active_paper_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Seeder only writes ideas to idea bank.",
            "Does not create contracts directly.",
            "Does not run backtests.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not promote candidates.",
            "Does not place orders."
        ]
    }

    state_path = out_dir / "candidate_idea_seeder_v1_state.json"
    csv_path = out_dir / "candidate_idea_seeder_v1_results.csv"
    report_path = out_dir / "candidate_idea_seeder_v1_report.md"

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    pd.DataFrame(results).to_csv(csv_path, index=False)

    md = []
    md.append("# Edge Factory Candidate Idea Seeder v1")
    md.append("")
    md.append(f"Status: `{state['seeder_status']}`")
    md.append(f"Seed count: `{state['seed_count']}`")
    md.append(f"Success count: `{state['success_count']}`")
    md.append("")
    md.append("## Seeded ideas")
    for r in results:
        md.append(f"- `{r['candidate_key']}` / `{r['family_key']}` / `{r['side']}` — ok `{r['ok']}`")
    md.append("")
    md.append("## Safety")
    md.append("- live_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY CANDIDATE IDEA SEEDER v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"seeder_status: {state['seeder_status']}")
    print(f"seed_count   : {state['seed_count']}")
    print(f"success_count: {state['success_count']}")
    print("live_allowed: False")
    print("active_paper_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("SEEDED IDEAS")
    print("-" * 100)
    print(pd.DataFrame(results)[["candidate_key","family_key","side","ok","returncode"]].to_string(index=False))
    print()
    print(f"State : {state_path}")
    print(f"CSV   : {csv_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    main()
