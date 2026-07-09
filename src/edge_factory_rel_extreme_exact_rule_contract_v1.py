#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Produces a frozen exact-rule contract JSON for the rel_extreme_reversion_short candidate by reading the latest OOS robustness and variant selector artifacts and locking in the chosen parameter values. Outputs the contract JSON and a state file to the edge_factory_rel_extreme_exact_rule_contract_v1 directory.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

WORKSPACE = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
CANDIDATE = "rel_extreme_reversion_short"

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_dir(root: Path, prefix: str) -> Optional[Path]:
    if not root.exists():
        return None
    ds = [x for x in root.iterdir() if x.is_dir() and x.name.startswith(prefix)]
    return sorted(ds, key=lambda x: x.stat().st_mtime, reverse=True)[0] if ds else None

def read_json(path: Optional[Path]) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def parse_variant_key(v: str) -> dict[str, Any]:
    out = {"variant_key": v}
    for part in str(v).split("|"):
        if "=" not in part:
            continue
        k, val = part.split("=", 1)
        out[k.strip()] = val.strip()

    def num(x):
        try:
            if str(x).lower() == "na":
                return None
            f = float(x)
            return int(f) if abs(f - int(f)) < 1e-9 else f
        except Exception:
            return x

    for k in ["L", "rel", "mkt", "coin", "h", "c"]:
        if k in out:
            out[k] = num(out[k])

    return out

def pass_rate(series: pd.Series, op: str, threshold: float) -> float:
    x = pd.to_numeric(series, errors="coerce")
    if x.notna().sum() == 0:
        return 0.0
    if op == ">=":
        return float((x >= threshold).mean())
    if op == "<=":
        return float((x <= threshold).mean())
    return 0.0

def numeric_desc(series: pd.Series) -> dict[str, Any]:
    x = pd.to_numeric(series, errors="coerce").dropna()
    if x.empty:
        return {}
    return {
        "non_null": int(x.notna().sum()),
        "min": float(x.min()),
        "q01": float(x.quantile(0.01)),
        "q05": float(x.quantile(0.05)),
        "median": float(x.median()),
        "mean": float(x.mean()),
        "q95": float(x.quantile(0.95)),
        "max": float(x.max()),
    }

def profit_factor(pnl: pd.Series) -> float:
    x = pd.to_numeric(pnl, errors="coerce").dropna()
    if x.empty:
        return 0.0
    wins = x[x > 0].sum()
    losses = -x[x < 0].sum()
    if losses <= 0:
        return 999999.0 if wins > 0 else 0.0
    return float(wins / losses)

def main():
    out_dir = WORKSPACE / "edge_factory_rel_extreme_exact_rule_contract_v1" / f"rel_extreme_rule_contract_{stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    sel_dir = latest_dir(WORKSPACE / "edge_factory_rel_extreme_variant_selector_v1", "rel_extreme_variant_select_")
    sel_state_path = sel_dir / "rel_extreme_variant_selector_state.json" if sel_dir else None
    sel_state = read_json(sel_state_path)

    selected = sel_state.get("selected_variant") or {}
    variant_key = selected.get("variant_key")
    rows_path = sel_dir / "rel_extreme_candidate_rows.csv" if sel_dir else None

    if not variant_key or not rows_path or not rows_path.exists():
        raise SystemExit("selected variant or candidate rows missing; run rel_extreme_variant_selector first")

    params = parse_variant_key(str(variant_key))
    L = int(params.get("L"))
    rel_thr = params.get("rel")
    coin_thr = params.get("coin")
    side = str(params.get("side", "short"))
    hold = int(params.get("h"))
    cost_bps = float(params.get("c") or 0)

    df = pd.read_csv(rows_path)
    vdf = df[df["variant_key"].astype(str) == str(variant_key)].copy()

    if vdf.empty:
        raise SystemExit("selected variant rows not found")

    coin_col = "coin"
    time_col = "entry_time" if "entry_time" in vdf.columns else ("time" if "time" in vdf.columns else None)
    outcome_col = str(selected.get("outcome_col") or f"fwd_short_{hold}")

    coin_ret_col = f"coin_ret{L}_bps"
    mkt_ret_col = f"mkt_ret{L}_bps"

    if coin_ret_col not in vdf.columns and "coin_ret_bps" in vdf.columns:
        coin_ret_col = "coin_ret_bps"
    if mkt_ret_col not in vdf.columns and "mkt_ret_bps" in vdf.columns:
        mkt_ret_col = "mkt_ret_bps"

    audits = []

    def add_audit(name, col, op, threshold):
        if col not in vdf.columns:
            audits.append({
                "component": name,
                "column": col,
                "status": "MISSING_COLUMN",
                "pass_rate": 0.0,
                "operator": op,
                "threshold": threshold,
            })
            return
        audits.append({
            "component": name,
            "column": col,
            "status": "CHECKED",
            "operator": op,
            "threshold": threshold,
            "pass_rate": pass_rate(vdf[col], op, float(threshold)),
            "desc": numeric_desc(vdf[col]),
        })

    side_status = "CONFIRMED_SHORT" if side == "short" else "UNEXPECTED_SIDE"

    add_audit("coin_threshold", coin_ret_col, ">=", float(coin_thr))

    if rel_thr is not None:
        if "rel_ret_bps" in vdf.columns:
            add_audit("relative_threshold_direct", "rel_ret_bps", ">=", float(rel_thr))
        elif coin_ret_col in vdf.columns and mkt_ret_col in vdf.columns:
            vdf["_rel_calc_bps"] = pd.to_numeric(vdf[coin_ret_col], errors="coerce") - pd.to_numeric(vdf[mkt_ret_col], errors="coerce")
            add_audit("relative_threshold_calc", "_rel_calc_bps", ">=", float(rel_thr))
        else:
            audits.append({
                "component": "relative_threshold",
                "column": "rel_ret_bps or coin-mkt",
                "status": "MISSING_RELATIVE_INPUTS",
                "pass_rate": 0.0,
                "operator": ">=",
                "threshold": rel_thr,
            })

    if outcome_col in vdf.columns:
        pnl = pd.to_numeric(vdf[outcome_col], errors="coerce")
        outcome_status = "OUTCOME_CONFIRMED"
        outcome_summary = {
            "outcome_col": outcome_col,
            "non_null": int(pnl.notna().sum()),
            "sum": float(pnl.sum()),
            "mean": float(pnl.mean()),
            "median": float(pnl.median()),
            "win_rate": float((pnl > 0).mean()),
            "profit_factor": profit_factor(pnl),
            "min": float(pnl.min()),
            "max": float(pnl.max()),
        }
    else:
        outcome_status = "OUTCOME_MISSING"
        outcome_summary = {"outcome_col": outcome_col}

    if time_col:
        ts = pd.to_datetime(vdf[time_col], errors="coerce", utc=True)
        time_summary = {
            "time_col": time_col,
            "first_time": str(ts.min()) if ts.notna().any() else None,
            "last_time": str(ts.max()) if ts.notna().any() else None,
            "non_null": int(ts.notna().sum()),
        }
    else:
        time_summary = {"time_col": None}

    symbol_count = int(vdf[coin_col].astype(str).nunique()) if coin_col in vdf.columns else 0

    audit_df = pd.DataFrame(audits)
    audit_df.to_csv(out_dir / "rel_extreme_rule_component_audit.csv", index=False)

    min_pass = float(audit_df["pass_rate"].min()) if len(audit_df) else 0.0
    all_components_confirmed = bool(
        len(audit_df)
        and min_pass >= 0.99
        and outcome_status == "OUTCOME_CONFIRMED"
        and side_status == "CONFIRMED_SHORT"
    )

    contract_status = (
        "REL_EXTREME_RULE_CONTRACT_CONFIRMED_FOR_MARKET_REPLAY"
        if all_components_confirmed
        else "REL_EXTREME_RULE_CONTRACT_PARTIAL_NEEDS_REVIEW"
    )

    rule_contract = {
        "candidate": CANDIDATE,
        "variant_key": variant_key,
        "side": side,
        "side_status": side_status,
        "lookback_hours": L,
        "coin_return_column": coin_ret_col,
        "coin_threshold_bps": coin_thr,
        "market_return_column": mkt_ret_col if mkt_ret_col in vdf.columns else None,
        "relative_threshold_bps": rel_thr,
        "hold_hours": hold,
        "cost_bps_from_variant": cost_bps,
        "outcome_col": outcome_col,
        "symbol_col": coin_col,
        "time_col": time_col,
        "rows": int(len(vdf)),
        "symbol_count": symbol_count,
        "component_min_pass_rate": min_pass,
        "contract_status": contract_status,
        "active_paper_allowed": False,
        "live_allowed": False,
        "rule_expression_hypothesis": f"side=short; coin_ret_{L}h_bps >= {coin_thr}; relative_ret_{L}h_bps >= {rel_thr}; hold={hold}h",
        "warnings": [
            "This is still an artifact-derived rule contract, not live/paper permission.",
            "Must be replayed from real local candle data before any shadow/paper consideration.",
            "cost_bps_from_variant is recorded but replay must define execution cost explicitly.",
        ],
    }

    write_json(out_dir / "rel_extreme_rule_contract.json", rule_contract)

    state = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "selector_state": str(sel_state_path),
        "source_rows": str(rows_path),
        "output_dir": str(out_dir),
        "contract_status": contract_status,
        "selected_variant": selected,
        "parsed_params": params,
        "rule_contract": rule_contract,
        "component_audits": audits,
        "outcome_status": outcome_status,
        "outcome_summary": outcome_summary,
        "time_summary": time_summary,
        "active_paper_allowed": False,
        "live_allowed": False,
        "next_action": "BUILD_REL_EXTREME_REAL_CANDLE_MARKET_REPLAY" if all_components_confirmed else "INSPECT_RULE_COMPONENT_FAILURES",
    }

    write_json(out_dir / "rel_extreme_exact_rule_contract_state.json", state)

    print("EDGE FACTORY REL EXTREME EXACT RULE CONTRACT v1")
    print("=" * 100)
    print(f"workspace : {WORKSPACE}")
    print(f"output_dir: {out_dir}")
    print(f"contract_status: {contract_status}")
    print(f"variant_key: {variant_key}")
    print(f"side_status: {side_status}")
    print(f"lookback_hours: {L}")
    print(f"coin_threshold_bps: {coin_thr}")
    print(f"relative_threshold_bps: {rel_thr}")
    print(f"hold_hours: {hold}")
    print(f"rows: {len(vdf)}")
    print(f"symbol_count: {symbol_count}")
    print(f"outcome_status: {outcome_status}")
    print(f"component_min_pass_rate: {min_pass}")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print()
    print("COMPONENT AUDIT")
    print("-" * 100)
    print(audit_df.to_string(index=False))
    print()
    print("OUTCOME SUMMARY")
    print("-" * 100)
    print(json.dumps(outcome_summary, indent=2, ensure_ascii=False, default=str))
    print()
    print(f"State   : {out_dir / 'rel_extreme_exact_rule_contract_state.json'}")
    print(f"Contract: {out_dir / 'rel_extreme_rule_contract.json'}")
    print(f"Audit   : {out_dir / 'rel_extreme_rule_component_audit.csv'}")

if __name__ == "__main__":
    main()
