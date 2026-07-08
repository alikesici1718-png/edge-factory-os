#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"
SOURCE = WORKSPACE / "market_relative_divergence_scan_FAST" / "family_candidate_trades.csv"

OUTCOME_COLS = ["fwd_short_4", "fwd_short_8", "fwd_short_12", "fwd_short_24", "net_ret"]

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def profit_factor(x: pd.Series) -> float:
    y = pd.to_numeric(x, errors="coerce").dropna()
    if y.empty:
        return 0.0
    wins = y[y > 0].sum()
    losses = -y[y < 0].sum()
    if losses <= 0:
        return 999999.0 if wins > 0 else 0.0
    return float(wins / losses)

def max_drawdown_proxy(x: pd.Series) -> float:
    y = pd.to_numeric(x, errors="coerce").fillna(0.0)
    eq = y.cumsum()
    dd = eq - eq.cummax()
    return float(dd.min()) if len(dd) else 0.0

def choose_outcome(row: pd.Series) -> str:
    # If hold is 4/8/12/24 and matching fwd_short_H exists, use that.
    try:
        h = int(float(row.get("hold")))
        col = f"fwd_short_{h}"
        if col in row.index:
            return col
    except Exception:
        pass

    # Fallback: prefer net_ret only if present, then shorter short-horizon columns.
    for c in ["net_ret", "fwd_short_4", "fwd_short_8", "fwd_short_12", "fwd_short_24"]:
        if c in row.index:
            return c

    return ""

def summarize_variant(g: pd.DataFrame, variant: str) -> dict[str, Any]:
    first = g.iloc[0]
    outcome_col = choose_outcome(first)
    pnl = pd.to_numeric(g[outcome_col], errors="coerce") if outcome_col else pd.Series(dtype=float)

    coin_col = "coin" if "coin" in g.columns else None
    time_col = "entry_time" if "entry_time" in g.columns else ("time" if "time" in g.columns else None)

    d = {
        "candidate": CANDIDATE,
        "variant_key": variant,
        "outcome_col": outcome_col,
        "rows": int(len(g)),
        "symbol_count": int(g[coin_col].astype(str).nunique()) if coin_col else 0,
        "first_time": str(pd.to_datetime(g[time_col], errors="coerce", utc=True).min()) if time_col else None,
        "last_time": str(pd.to_datetime(g[time_col], errors="coerce", utc=True).max()) if time_col else None,
        "pnl_sum": float(pnl.sum()) if len(pnl) else 0.0,
        "pnl_mean": float(pnl.mean()) if len(pnl) else 0.0,
        "pnl_median": float(pnl.median()) if len(pnl) else 0.0,
        "win_rate": float((pnl > 0).mean()) if len(pnl) else 0.0,
        "profit_factor": profit_factor(pnl),
        "worst_trade": float(pnl.min()) if len(pnl) else 0.0,
        "best_trade": float(pnl.max()) if len(pnl) else 0.0,
        "drawdown_proxy": max_drawdown_proxy(pnl),
        "hold_values": "|".join(map(str, sorted(g["hold"].dropna().unique()))) if "hold" in g.columns else "",
    }

    # Extract likely static rule parameters from variant rows.
    for col in [
        "hold", "coin_threshold_bps", "rel_threshold_bps", "mkt_threshold_bps",
        "min_entry_vol_quote", "max_entry_range_bps"
    ]:
        if col in g.columns:
            vals = g[col].dropna().unique()
            if len(vals) <= 8:
                d[col] = "|".join(map(str, vals[:8]))
            else:
                d[col] = f"{len(vals)} unique"

    return d

def main():
    out_dir = WORKSPACE / "edge_factory_rel_extreme_variant_selector_v1" / f"rel_extreme_variant_select_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not SOURCE.exists():
        raise SystemExit(f"source missing: {SOURCE}")

    df = pd.read_csv(SOURCE)

    masks = []
    for c in df.columns:
        try:
            m = df[c].astype(str).str.contains(CANDIDATE, case=False, na=False)
            if m.any():
                masks.append(m)
        except Exception:
            pass

    if not masks:
        raise SystemExit("candidate rows not found")

    mask = masks[0]
    for m in masks[1:]:
        mask = mask | m

    cdf = df[mask].copy()

    if "variant_key" not in cdf.columns:
        raise SystemExit("variant_key missing; cannot select exact variant")

    rows = []
    for variant, g in cdf.groupby("variant_key"):
        rows.append(summarize_variant(g, str(variant)))

    sdf = pd.DataFrame(rows)

    # Conservative scoring: profit + breadth + sample - drawdown penalty.
    # Still NOT promotion. This only selects a candidate for replay.
    sdf["score"] = (
        sdf["pnl_mean"].fillna(0)
        * sdf["win_rate"].fillna(0)
        * (sdf["symbol_count"].fillna(0).clip(lower=1) ** 0.25)
        * (sdf["rows"].fillna(0).clip(lower=1) ** 0.10)
    )

    sdf = sdf.sort_values(
        ["profit_factor", "pnl_sum", "symbol_count", "rows"],
        ascending=[False, False, False, False],
    )

    selected = sdf.iloc[0].to_dict() if len(sdf) else {}

    cdf.to_csv(out_dir / "rel_extreme_candidate_rows.csv", index=False)
    sdf.to_csv(out_dir / "rel_extreme_variant_ranking.csv", index=False)

    status = "REL_EXTREME_VARIANT_SELECTED_FOR_REPLAY_REVIEW" if selected else "NO_VARIANT_SELECTED"

    warnings = [
        "This selector does not promote, start paper, or allow live.",
        "Outcome column is selected explicitly; coin_ret_bps is treated as feature, not PnL.",
        "Selected variant still requires exact rule extraction and real candle replay.",
    ]

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "candidate": CANDIDATE,
        "source": str(SOURCE),
        "output_dir": str(out_dir),
        "status": status,
        "candidate_rows": int(len(cdf)),
        "variant_count": int(sdf["variant_key"].nunique()) if len(sdf) else 0,
        "selected_variant": selected,
        "warnings": warnings,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "BUILD_REL_EXTREME_EXACT_RULE_EXTRACTOR_AND_MARKET_REPLAY",
    }

    write_json(out_dir / "rel_extreme_variant_selector_state.json", state)

    print("EDGE FACTORY REL EXTREME VARIANT SELECTOR v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"source    : {SOURCE}")
    print(f"output_dir: {out_dir}")
    print(f"status: {status}")
    print(f"candidate_rows: {len(cdf)}")
    print(f"variant_count: {sdf['variant_key'].nunique() if len(sdf) else 0}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("SELECTED VARIANT")
    print("-" * 100)
    print(json.dumps(selected, indent=2, ensure_ascii=False, default=str))
    print()
    print("TOP VARIANTS")
    print("-" * 100)
    print(sdf.head(20).to_string(index=False))
    print()
    print(f"State  : {out_dir / 'rel_extreme_variant_selector_state.json'}")
    print(f"Ranking: {out_dir / 'rel_extreme_variant_ranking.csv'}")
    print(f"Rows   : {out_dir / 'rel_extreme_candidate_rows.csv'}")

if __name__ == "__main__":
    main()
