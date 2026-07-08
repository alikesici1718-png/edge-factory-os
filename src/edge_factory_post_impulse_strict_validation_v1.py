#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
OUT_ROOT = WORKSPACE / "edge_factory_post_impulse_strict_validation_v1"

CANDIDATE_BASE = "post_impulse_drift_long_v1"
CANDIDATE_STRICT = "post_impulse_drift_long_strict_v1"
FAMILY = "impulse_drift_long"

IS_START = pd.Timestamp("2025-04-30 00:00:00", tz="UTC")
IS_END = pd.Timestamp("2025-12-31 23:00:00", tz="UTC")
OOS_START = pd.Timestamp("2026-01-01 00:00:00", tz="UTC")
OOS_END = pd.Timestamp("2026-04-29 23:00:00", tz="UTC")

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def latest_file(root: Path, pattern: str) -> Path | None:
    files = list(root.rglob(pattern)) if root.exists() else []
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"__read_error__": repr(e)}

def load_panel(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)

def profit_factor(s: pd.Series) -> float | None:
    gp = float(s[s > 0].sum())
    gl = float(-s[s < 0].sum())
    if gl <= 0:
        return None
    return gp / gl

def max_drawdown_bps(s: pd.Series) -> float:
    eq = s.fillna(0).cumsum()
    dd = eq - eq.cummax()
    return float(dd.min()) if len(dd) else 0.0

def metrics(trades: pd.DataFrame, label: str) -> dict[str, Any]:
    if trades.empty:
        return {
            "label": label,
            "trade_count": 0,
            "symbol_count": 0,
            "win_rate": None,
            "mean_net_bps": None,
            "median_net_bps": None,
            "profit_factor": None,
            "max_drawdown_bps": None,
            "total_net_bps": 0.0,
        }

    x = trades["net_ret_bps"]
    return {
        "label": label,
        "trade_count": int(len(trades)),
        "symbol_count": int(trades["symbol"].nunique()),
        "win_rate": float((x > 0).mean()),
        "mean_net_bps": float(x.mean()),
        "median_net_bps": float(x.median()),
        "profit_factor": profit_factor(x),
        "max_drawdown_bps": max_drawdown_bps(x),
        "total_net_bps": float(x.sum()),
    }

def apply_cooldown(signals: pd.DataFrame, cooldown_hours: int) -> pd.DataFrame:
    if signals.empty:
        return signals

    kept_parts = []
    cooldown = pd.Timedelta(hours=cooldown_hours)

    for sym, g in signals.sort_values(["symbol", "entry_time"]).groupby("symbol", sort=False):
        last_time = None
        keep_rows = []

        for idx, row in g.iterrows():
            t = row["entry_time"]
            if last_time is None or t >= last_time + cooldown:
                keep_rows.append(idx)
                last_time = t

        kept_parts.append(g.loc[keep_rows])

    if not kept_parts:
        return signals.iloc[0:0].copy()

    return pd.concat(kept_parts, ignore_index=True).sort_values(["entry_time", "symbol"]).reset_index(drop=True)

def build_trades(
    df: pd.DataFrame,
    coin_thr: float,
    mkt_thr: float,
    liq_floor: float,
    range_cap: float,
    hold_hours: int,
    cooldown_hours: int,
    apply_cd: bool,
) -> pd.DataFrame:
    d = df.copy()

    mask = (
        (d["coin_ret3_bps"] >= coin_thr) &
        (d["mkt_ret3_bps"] >= mkt_thr) &
        (d["entry_vol_quote"] >= liq_floor) &
        (d["entry_range_bps"] <= range_cap)
    )

    signals = d.loc[
        mask,
        [
            "time", "symbol", "close", "entry_vol_quote", "entry_range_bps",
            "coin_ret3_bps", "mkt_ret3_bps", "coin_ret6_bps", "mkt_ret6_bps"
        ]
    ].copy()

    signals = signals.rename(columns={"time": "entry_time", "close": "entry_price"})
    signals = signals.sort_values(["entry_time", "symbol"]).reset_index(drop=True)

    if apply_cd:
        signals = apply_cooldown(signals, cooldown_hours)

    signals["exit_time"] = signals["entry_time"] + pd.Timedelta(hours=hold_hours)

    exit_lookup = d[["time", "symbol", "close"]].copy()
    exit_lookup = exit_lookup.rename(columns={"time": "exit_time", "close": "exit_price"})

    trades = signals.merge(
        exit_lookup,
        on=["symbol", "exit_time"],
        how="left",
    ).dropna(subset=["exit_price"]).copy()

    total_cost_bps = 25.0
    trades["candidate_key"] = CANDIDATE_STRICT
    trades["family_key"] = FAMILY
    trades["side"] = "long"
    trades["hold_hours"] = hold_hours
    trades["cooldown_hours"] = cooldown_hours if apply_cd else 0
    trades["raw_ret_bps"] = ((trades["exit_price"] / trades["entry_price"]) - 1.0) * 10000.0
    trades["cost_bps"] = total_cost_bps
    trades["net_ret_bps"] = trades["raw_ret_bps"] - total_cost_bps

    return trades.sort_values(["entry_time", "symbol"]).reset_index(drop=True)

def month_breakdown(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()

    x = trades.copy()
    x["month"] = pd.to_datetime(x["entry_time"], utc=True).dt.to_period("M").astype(str)

    rows = []
    for m, g in x.groupby("month"):
        mm = metrics(g, m)
        rows.append(mm)

    return pd.DataFrame(rows)

def symbol_breakdown(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()

    rows = []
    for sym, g in trades.groupby("symbol"):
        mm = metrics(g, sym)
        rows.append(mm)

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values("trade_count", ascending=False)
    return out

def walk_forward_monthly(trades: pd.DataFrame) -> pd.DataFrame:
    return month_breakdown(trades)

def gate_decision(full_m: dict[str, Any], is_m: dict[str, Any], oos_m: dict[str, Any], months: pd.DataFrame, symbols: pd.DataFrame) -> tuple[str, list[str], list[str]]:
    blockers = []
    warnings = []

    full_pf = full_m.get("profit_factor") or 0.0
    oos_pf = oos_m.get("profit_factor") or 0.0
    full_mean = full_m.get("mean_net_bps") or -999.0
    oos_mean = oos_m.get("mean_net_bps") or -999.0
    full_median = full_m.get("median_net_bps") or -999.0
    oos_median = oos_m.get("median_net_bps") or -999.0

    if full_m["trade_count"] < 300:
        blockers.append(f"full_trade_count_low:{full_m['trade_count']}")
    if oos_m["trade_count"] < 75:
        blockers.append(f"oos_trade_count_low:{oos_m['trade_count']}")
    if full_m["symbol_count"] < 30:
        blockers.append(f"full_symbol_count_low:{full_m['symbol_count']}")
    if oos_m["symbol_count"] < 15:
        blockers.append(f"oos_symbol_count_low:{oos_m['symbol_count']}")

    if full_pf < 1.15:
        blockers.append(f"full_pf_below_1p15:{full_pf}")
    if oos_pf < 1.05:
        blockers.append(f"oos_pf_below_1p05:{oos_pf}")

    if full_mean <= 0:
        blockers.append(f"full_mean_not_positive:{full_mean}")
    if oos_mean <= 0:
        blockers.append(f"oos_mean_not_positive:{oos_mean}")

    if full_median < -10:
        blockers.append(f"full_median_too_negative:{full_median}")
    if oos_median < -20:
        blockers.append(f"oos_median_too_negative:{oos_median}")

    if not months.empty:
        positive_month_rate = float((months["mean_net_bps"] > 0).mean())
        positive_pf_month_rate = float((months["profit_factor"].fillna(0) > 1.0).mean())
        if positive_month_rate < 0.55:
            blockers.append(f"positive_month_rate_low:{positive_month_rate}")
        if positive_pf_month_rate < 0.55:
            warnings.append(f"positive_pf_month_rate_low:{positive_pf_month_rate}")
    else:
        blockers.append("month_breakdown_empty")

    if not symbols.empty and full_m["trade_count"] > 0:
        top_symbol_share = float(symbols["trade_count"].max() / full_m["trade_count"])
        if top_symbol_share > 0.10:
            warnings.append(f"top_symbol_concentration_high:{top_symbol_share}")
        if top_symbol_share > 0.20:
            blockers.append(f"top_symbol_concentration_extreme:{top_symbol_share}")

    # Decision levels.
    if blockers:
        return "STRICT_VALIDATION_FAIL_ARCHIVE_OR_REDESIGN", blockers, warnings

    if oos_pf >= 1.15 and oos_mean > 10 and oos_median >= 0:
        return "STRICT_VALIDATION_PASS_STRONG_OFFLINE_CANDIDATE", blockers, warnings

    return "STRICT_VALIDATION_PASS_WEAK_OFFLINE_CANDIDATE", blockers, warnings

def main() -> int:
    out_dir = OUT_ROOT / f"post_impulse_strict_validation_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    diagnostic_state_path = latest_file(
        WORKSPACE / "edge_factory_post_impulse_threshold_hold_diagnostic_v1",
        "post_impulse_threshold_hold_diagnostic_v1_state.json"
    )
    diagnostic = read_json(diagnostic_state_path)

    top_combo = diagnostic.get("top_combo") or {}

    # Fallback to known diagnostic result if needed.
    coin_thr = float(top_combo.get("coin_thr", 200))
    mkt_thr = float(top_combo.get("mkt_thr", 150))
    liq_q = float(top_combo.get("liq_q", 0.90))
    range_cap_q = float(top_combo.get("range_cap_q", 0.90))
    hold_hours = int(top_combo.get("hold_hours", 6))
    cooldown_hours = 12

    panel_path = latest_file(
        WORKSPACE / "edge_factory_feature_panels" / CANDIDATE_BASE,
        "*feature_panel_1h_dynamic.parquet"
    )
    if panel_path is None:
        panel_path = latest_file(
            WORKSPACE / "edge_factory_feature_panels" / CANDIDATE_BASE,
            "*feature_panel_1h_dynamic.csv"
        )

    blockers = []
    if not panel_path or not panel_path.exists():
        blockers.append("DYNAMIC_PANEL_NOT_FOUND")

    if diagnostic.get("diagnostic_status") != "POST_IMPULSE_DIAGNOSTIC_PROMISING_COMBO_FOUND":
        blockers.append(f"DIAGNOSTIC_NOT_PROMISING:{diagnostic.get('diagnostic_status')}")

    if blockers:
        state = {
            "generated_at": now_iso(),
            "workspace": str(WORKSPACE),
            "candidate_key": CANDIDATE_STRICT,
            "validation_status": "STRICT_VALIDATION_BLOCKED",
            "blockers": blockers,
            "promotion_allowed": False,
            "active_paper_allowed": False,
            "live_allowed": False,
            "capital_change_allowed": False,
        }
        state_path = out_dir / "post_impulse_strict_validation_v1_state.json"
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(json.dumps(state, indent=2, ensure_ascii=False, default=str))
        return

    df = load_panel(panel_path)
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df = df.dropna(subset=["time", "symbol", "close"])
    df = df.sort_values(["symbol", "time"])

    needed = ["coin_ret3_bps", "mkt_ret3_bps", "coin_ret6_bps", "mkt_ret6_bps", "entry_vol_quote", "entry_range_bps", "close"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise RuntimeError(f"Panel missing columns: {missing}")

    for c in needed:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Critical: quantile thresholds fit only on in-sample to reduce leakage.
    is_df = df[(df["time"] >= IS_START) & (df["time"] <= IS_END)].copy()
    if is_df.empty:
        raise RuntimeError("In-sample panel is empty")

    liq_floor_is = float(is_df["entry_vol_quote"].dropna().quantile(liq_q))
    range_cap_is = float(is_df["entry_range_bps"].dropna().quantile(range_cap_q))

    trades_cd = build_trades(
        df=df,
        coin_thr=coin_thr,
        mkt_thr=mkt_thr,
        liq_floor=liq_floor_is,
        range_cap=range_cap_is,
        hold_hours=hold_hours,
        cooldown_hours=cooldown_hours,
        apply_cd=True,
    )

    trades_no_cd = build_trades(
        df=df,
        coin_thr=coin_thr,
        mkt_thr=mkt_thr,
        liq_floor=liq_floor_is,
        range_cap=range_cap_is,
        hold_hours=hold_hours,
        cooldown_hours=0,
        apply_cd=False,
    )

    is_trades = trades_cd[(trades_cd["entry_time"] >= IS_START) & (trades_cd["entry_time"] <= IS_END)].copy()
    oos_trades = trades_cd[(trades_cd["entry_time"] >= OOS_START) & (trades_cd["entry_time"] <= OOS_END)].copy()

    full_m = metrics(trades_cd, "full_cooldown")
    is_m = metrics(is_trades, "in_sample_cooldown")
    oos_m = metrics(oos_trades, "out_of_sample_cooldown")
    no_cd_m = metrics(trades_no_cd, "full_no_cooldown_reference")

    months = month_breakdown(trades_cd)
    symbols = symbol_breakdown(trades_cd)
    folds = walk_forward_monthly(trades_cd)

    validation_status, gate_blockers, warnings = gate_decision(full_m, is_m, oos_m, months, symbols)

    if validation_status == "STRICT_VALIDATION_FAIL_ARCHIVE_OR_REDESIGN":
        next_action = "ARCHIVE_STRICT_VARIANT_OR_REDESIGN_WITH_NEW_EVIDENCE"
        full_run_allowed = False
    elif validation_status == "STRICT_VALIDATION_PASS_STRONG_OFFLINE_CANDIDATE":
        next_action = "CREATE_FULL_OFFLINE_BACKTEST_ARTIFACT_AND_RESULT_TO_LIFECYCLE"
        full_run_allowed = True
    else:
        next_action = "OPTIONAL_FULL_BACKTEST_WITH_CAUTION_OR_MORE_OOS"
        full_run_allowed = True

    trades_csv = out_dir / f"{CANDIDATE_STRICT}_strict_validation_trades.csv"
    trades_no_cd_csv = out_dir / f"{CANDIDATE_STRICT}_strict_validation_trades_no_cooldown_reference.csv"
    monthly_csv = out_dir / f"{CANDIDATE_STRICT}_strict_validation_monthly.csv"
    symbol_csv = out_dir / f"{CANDIDATE_STRICT}_strict_validation_symbol.csv"
    folds_csv = out_dir / f"{CANDIDATE_STRICT}_strict_validation_walkforward_monthly.csv"

    trades_cd.to_csv(trades_csv, index=False)
    trades_no_cd.to_csv(trades_no_cd_csv, index=False)
    months.to_csv(monthly_csv, index=False)
    symbols.to_csv(symbol_csv, index=False)
    folds.to_csv(folds_csv, index=False)

    state = {
        "generated_at": now_iso(),
        "workspace": str(WORKSPACE),
        "candidate_key": CANDIDATE_STRICT,
        "base_candidate_key": CANDIDATE_BASE,
        "family_key": FAMILY,
        "validation_status": validation_status,
        "next_action": next_action,
        "diagnostic_state_path": str(diagnostic_state_path) if diagnostic_state_path else "",
        "panel_path": str(panel_path),
        "rule": {
            "coin_ret3_bps_min": coin_thr,
            "mkt_ret3_bps_min": mkt_thr,
            "liquidity_quantile": liq_q,
            "liquidity_floor_fit_on_in_sample": liq_floor_is,
            "entry_range_quantile_cap": range_cap_q,
            "entry_range_cap_fit_on_in_sample": range_cap_is,
            "hold_hours": hold_hours,
            "cooldown_hours": cooldown_hours,
            "cost_bps": 25.0,
        },
        "metrics": {
            "full_cooldown": full_m,
            "in_sample_cooldown": is_m,
            "out_of_sample_cooldown": oos_m,
            "full_no_cooldown_reference": no_cd_m,
        },
        "gate_blockers": gate_blockers,
        "warnings": warnings,
        "positive_month_rate": float((months["mean_net_bps"] > 0).mean()) if not months.empty else None,
        "positive_pf_month_rate": float((months["profit_factor"].fillna(0) > 1.0).mean()) if not months.empty else None,
        "top_symbol_share": float(symbols["trade_count"].max() / full_m["trade_count"]) if not symbols.empty and full_m["trade_count"] else None,
        "outputs": {
            "trades_csv": str(trades_csv),
            "trades_no_cooldown_reference_csv": str(trades_no_cd_csv),
            "monthly_csv": str(monthly_csv),
            "symbol_csv": str(symbol_csv),
            "folds_csv": str(folds_csv),
        },
        "full_run_allowed": full_run_allowed,
        "promotion_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "hard_rules": [
            "Strict validation only.",
            "Uses in-sample-only fitted liquidity/range thresholds.",
            "Applies 12h cooldown per symbol.",
            "Does not touch MASTER_UPPER_SYSTEM.",
            "Does not start/stop processes.",
            "Does not place orders.",
            "Does not enable live trading.",
            "Does not change capital.",
            "Does not create active paper family."
        ],
    }

    state_path = out_dir / "post_impulse_strict_validation_v1_state.json"
    report_path = out_dir / "post_impulse_strict_validation_v1_report.md"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    md = []
    md.append("# Edge Factory Post Impulse Strict Validation v1")
    md.append("")
    md.append(f"Validation status: `{validation_status}`")
    md.append(f"Next action: `{next_action}`")
    md.append("")
    md.append("## Rule")
    md.append("```json")
    md.append(json.dumps(state["rule"], indent=2, ensure_ascii=False, default=str))
    md.append("```")
    md.append("")
    md.append("## Metrics")
    md.append("```json")
    md.append(json.dumps(state["metrics"], indent=2, ensure_ascii=False, default=str))
    md.append("```")
    md.append("")
    md.append("## Gate blockers")
    if gate_blockers:
        for b in gate_blockers:
            md.append(f"- `{b}`")
    else:
        md.append("- None")
    md.append("")
    md.append("## Warnings")
    if warnings:
        for w in warnings:
            md.append(f"- `{w}`")
    else:
        md.append("- None")
    md.append("")
    md.append("## Safety")
    md.append("- promotion_allowed: `False`")
    md.append("- active_paper_allowed: `False`")
    md.append("- live_allowed: `False`")
    md.append("- capital_change_allowed: `False`")
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("EDGE FACTORY POST IMPULSE STRICT VALIDATION v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"candidate : {CANDIDATE_STRICT}")
    print(f"validation_status: {validation_status}")
    print(f"next_action: {next_action}")
    print(f"full_run_allowed: {full_run_allowed}")
    print("promotion_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print()
    print("RULE")
    print("-" * 100)
    print(json.dumps(state["rule"], indent=2, ensure_ascii=False, default=str))
    print()
    print("METRICS")
    print("-" * 100)
    print(json.dumps(state["metrics"], indent=2, ensure_ascii=False, default=str))
    print()
    print("GATE BLOCKERS")
    print("-" * 100)
    if gate_blockers:
        for b in gate_blockers:
            print("-", b)
    else:
        print("NONE")
    print()
    print("WARNINGS")
    print("-" * 100)
    if warnings:
        for w in warnings:
            print("-", w)
    else:
        print("NONE")
    print()
    print(f"Trades : {trades_csv}")
    print(f"Monthly: {monthly_csv}")
    print(f"Symbol : {symbol_csv}")
    print(f"Folds  : {folds_csv}")
    print(f"State  : {state_path}")
    print(f"Report : {report_path}")

if __name__ == "__main__":
    main()
