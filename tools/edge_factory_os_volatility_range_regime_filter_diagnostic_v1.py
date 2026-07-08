from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_volatility_range_regime_filter_diagnostic_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "volatility_range_regime_filter_contract_latest.json"
)

MONTH_REGIME_DIAG_LATEST = (
    BASE_DIR
    / "edge_factory_os_month_regime_instability_diagnostic_v1"
    / "month_regime_instability_diagnostic_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"volatility_range_regime_filter_diagnostic_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "volatility_range_regime_filter_diagnostic_latest.json"
LATEST_MD = OUT_ROOT / "volatility_range_regime_filter_diagnostic_latest.md"

COST_BPS_TOTAL = 75.0


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def fnum(v: Any, default=None):
    try:
        if v is None:
            return default
        x = float(v)
        return x if math.isfinite(x) else default
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def summarize_trade_df(df, ret_col: str, symbol_col: str = "symbol") -> Dict[str, Any]:
    if df is None or len(df) == 0 or ret_col not in df.columns:
        return {
            "trade_count": 0,
            "symbol_count": 0,
            "win_rate": None,
            "total_net_bps": 0.0,
            "mean_net_bps": None,
            "median_net_bps": None,
            "profit_factor": None,
        }

    vals = df[ret_col].dropna()

    if len(vals) == 0:
        return {
            "trade_count": int(len(df)),
            "symbol_count": int(df[symbol_col].nunique()) if symbol_col in df.columns else 0,
            "win_rate": None,
            "total_net_bps": 0.0,
            "mean_net_bps": None,
            "median_net_bps": None,
            "profit_factor": None,
        }

    wins = vals[vals > 0]
    losses = vals[vals < 0]

    pf = None
    if len(losses) > 0 and abs(float(losses.sum())) > 0:
        pf = float(wins.sum()) / abs(float(losses.sum()))
    elif len(wins) > 0:
        pf = 999.0

    return {
        "trade_count": int(len(df)),
        "valid_return_count": int(len(vals)),
        "symbol_count": int(df[symbol_col].nunique()) if symbol_col in df.columns else 0,
        "win_count": int((vals > 0).sum()),
        "loss_count": int((vals < 0).sum()),
        "win_rate": float((vals > 0).mean()),
        "total_net_bps": float(vals.sum()),
        "mean_net_bps": float(vals.mean()),
        "median_net_bps": float(vals.median()),
        "best_net_bps": float(vals.max()),
        "worst_net_bps": float(vals.min()),
        "profit_factor": pf,
    }


def summarize_month_subset(month_df, ret_col: str = "route_total_net_bps") -> Dict[str, Any]:
    if month_df is None or len(month_df) == 0:
        return {
            "month_count": 0,
            "positive_month_rate": None,
            "total_route_net_bps": 0.0,
            "mean_month_net_bps": None,
        }

    vals = month_df[ret_col].fillna(0.0)

    return {
        "month_count": int(len(month_df)),
        "positive_month_count": int((vals > 0).sum()),
        "negative_month_count": int((vals < 0).sum()),
        "positive_month_rate": float((vals > 0).mean()) if len(vals) else None,
        "total_route_net_bps": float(vals.sum()),
        "mean_month_net_bps": float(vals.mean()) if len(vals) else None,
        "worst_month": month_df.sort_values(ret_col, ascending=True).head(1).to_dict("records"),
        "best_month": month_df.sort_values(ret_col, ascending=False).head(1).to_dict("records"),
    }


def threshold_diagnostic(month_df, trade_df, feature: str, thresholds: List[float], ret_col: str) -> List[Dict[str, Any]]:
    out = []

    if feature not in month_df.columns and feature not in trade_df.columns:
        return out

    for threshold in thresholds:
        row: Dict[str, Any] = {
            "feature": feature,
            "threshold": threshold,
            "direction": ">=",
        }

        if feature in month_df.columns:
            hi_m = month_df[month_df[feature] >= threshold]
            lo_m = month_df[month_df[feature] < threshold]

            row["month_hi"] = summarize_month_subset(hi_m)
            row["month_lo"] = summarize_month_subset(lo_m)

            hi_total = row["month_hi"]["total_route_net_bps"]
            lo_total = row["month_lo"]["total_route_net_bps"]
            hi_pos = row["month_hi"]["positive_month_rate"] or 0.0
            lo_pos = row["month_lo"]["positive_month_rate"] or 0.0

            row["month_separation_score"] = abs(hi_total - lo_total) / 1000.0 + abs(hi_pos - lo_pos) * 100.0

        if feature in trade_df.columns:
            hi_t = trade_df[trade_df[feature] >= threshold]
            lo_t = trade_df[trade_df[feature] < threshold]

            row["trade_hi"] = summarize_trade_df(hi_t, ret_col)
            row["trade_lo"] = summarize_trade_df(lo_t, ret_col)

            hi_total_t = row["trade_hi"]["total_net_bps"]
            lo_total_t = row["trade_lo"]["total_net_bps"]
            hi_wr = row["trade_hi"]["win_rate"] or 0.0
            lo_wr = row["trade_lo"]["win_rate"] or 0.0

            row["trade_separation_score"] = abs(hi_total_t - lo_total_t) / 1000.0 + abs(hi_wr - lo_wr) * 100.0

        row["combined_score"] = float(row.get("month_separation_score", 0.0)) + float(row.get("trade_separation_score", 0.0))
        out.append(row)

    out.sort(key=lambda x: x.get("combined_score", 0.0), reverse=True)
    return out


def quantile_thresholds(series, quantiles: List[float]) -> List[float]:
    out = []
    try:
        s = series.dropna()
        for q in quantiles:
            out.append(float(s.quantile(q)))
    except Exception:
        pass
    return out


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(CONTRACT_LATEST)
    month_diag = load_json(MONTH_REGIME_DIAG_LATEST)

    if not isinstance(contract, dict):
        critical.append("volatility_range_regime_contract_latest_missing")
        contract = {}

    if not isinstance(month_diag, dict):
        attention.append("month_regime_diagnostic_latest_missing")
        month_diag = {}

    if contract.get("research_key") != "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if safe_get(contract, ["experiment_design", "diagnostic_only"]) is not True:
        critical.append("contract_not_diagnostic_only")

    if safe_get(contract, ["experiment_design", "candidate_generation_allowed_now"]) is not False:
        critical.append("contract_allows_candidate_generation_unexpectedly")

    if safe_get(contract, ["blocked_route_guard", "repeat_same_route_allowed"]) is not False:
        critical.append("contract_allows_repeat_same_route_unexpectedly")

    panel_path = safe_get(contract, ["universe_input", "panel_path"])

    if not panel_path:
        critical.append("panel_path_missing_from_contract")

    panel = Path(str(panel_path)) if panel_path else None

    if panel is None or not panel.exists():
        critical.append(f"panel_not_found:{panel_path}")

    route_proxy = month_diag.get("route_proxy_used_for_diagnostic_only") or {}

    threshold = int(route_proxy.get("threshold_coin_ret3_bps") or 350)
    hold_hours = int(route_proxy.get("hold_hours") or 12)
    entry_range_cap = route_proxy.get("entry_range_cap_bps")
    mkt_filter = route_proxy.get("mkt_filter") or {"name": "mkt_ret3_ge_0", "mkt_ret3_min_bps": 0, "mkt_ret6_min_bps": None}

    if critical:
        diagnostic_status = "VOLATILITY_RANGE_REGIME_DIAGNOSTIC_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CONTRACT_OR_PANEL_INPUT"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "diagnostic_status": diagnostic_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,
            "critical": critical,
            "attention": attention,
            "info": info,
            "safety": {
                "read_only": True,
                "offline_only": True,
                "mutate_runtime_allowed": False,
                "launcher_allowed": False,
                "patch_runtime_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "capital_change_allowed": False,
                "family_disable_allowed": False,
                "real_orders_allowed": False,
                "execution_performed": False,
            },
        }

        dump_json(RUN_DIR / "volatility_range_regime_filter_diagnostic_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS VOLATILITY RANGE REGIME FILTER DIAGNOSTIC v1")
        print("=" * 100)
        print(f"diagnostic_status: {diagnostic_status}")
        print(f"severity: {severity}")
        print(f"reason: {reason}")
        print(f"latest_json: {LATEST_JSON}")
        print("=" * 100)
        return 2

    import pandas as pd
    import numpy as np

    df = pd.read_parquet(panel)

    required_cols = [
        "time",
        "symbol",
        "close",
        "entry_vol_quote",
        "entry_range_bps",
        "coin_ret3_bps",
        "coin_ret6_bps",
        "mkt_ret3_bps",
        "mkt_ret6_bps",
    ]

    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        critical.append(f"panel_missing_columns:{missing}")

    if critical:
        diagnostic_status = "VOLATILITY_RANGE_REGIME_DIAGNOSTIC_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_PANEL_COLUMNS"
        reason = "; ".join(critical)
        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "diagnostic_status": diagnostic_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,
            "critical": critical,
            "attention": attention,
            "info": info,
            "safety": {
                "read_only": True,
                "offline_only": True,
                "mutate_runtime_allowed": False,
                "launcher_allowed": False,
                "patch_runtime_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "capital_change_allowed": False,
                "family_disable_allowed": False,
                "real_orders_allowed": False,
                "execution_performed": False,
            },
        }
    else:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        df = df.dropna(subset=["time", "symbol", "close"])
        df = df.sort_values(["symbol", "time"]).reset_index(drop=True)
        df["month"] = df["time"].dt.to_period("M").astype(str)

        future_col = f"future_close_{hold_hours}h"
        gross_col = f"gross_ret_{hold_hours}h_bps"
        net_col = f"net_ret_{hold_hours}h_bps"

        df[future_col] = df.groupby("symbol")["close"].shift(-hold_hours)
        df[gross_col] = ((df[future_col] / df["close"]) - 1.0) * 10000.0
        df[net_col] = df[gross_col] - COST_BPS_TOTAL

        route_mask = df["coin_ret3_bps"] >= threshold

        if entry_range_cap is not None:
            route_mask = route_mask & (df["entry_range_bps"] <= float(entry_range_cap))

        if isinstance(mkt_filter, dict):
            if mkt_filter.get("mkt_ret3_min_bps") is not None:
                route_mask = route_mask & (df["mkt_ret3_bps"] >= float(mkt_filter["mkt_ret3_min_bps"]))
            if mkt_filter.get("mkt_ret6_min_bps") is not None:
                route_mask = route_mask & (df["mkt_ret6_bps"] >= float(mkt_filter["mkt_ret6_min_bps"]))

        route_df = df.loc[route_mask].dropna(subset=[net_col]).copy()

        time_group = df.groupby("time")

        time_features = time_group.agg(
            symbol_count=("symbol", "nunique"),
            mean_coin_ret3_bps=("coin_ret3_bps", "mean"),
            median_coin_ret3_bps=("coin_ret3_bps", "median"),
            std_coin_ret3_bps=("coin_ret3_bps", "std"),
            mean_coin_ret6_bps=("coin_ret6_bps", "mean"),
            median_coin_ret6_bps=("coin_ret6_bps", "median"),
            mean_mkt_ret3_bps=("mkt_ret3_bps", "mean"),
            mean_mkt_ret6_bps=("mkt_ret6_bps", "mean"),
            mean_entry_range_bps=("entry_range_bps", "mean"),
            median_entry_range_bps=("entry_range_bps", "median"),
            mean_entry_vol_quote=("entry_vol_quote", "mean"),
            median_entry_vol_quote=("entry_vol_quote", "median"),
        ).reset_index()

        tmp = df[["time", "coin_ret3_bps", "coin_ret6_bps", "entry_range_bps"]].copy()
        tmp["breadth_ret3_pos"] = tmp["coin_ret3_bps"] > 0
        tmp["breadth_ret6_pos"] = tmp["coin_ret6_bps"] > 0
        tmp["impulse_250_share"] = tmp["coin_ret3_bps"] >= 250
        tmp["impulse_350_share"] = tmp["coin_ret3_bps"] >= 350
        tmp["large_range_share"] = tmp["entry_range_bps"] >= 250

        shares = tmp.groupby("time").agg(
            breadth_ret3_pos=("breadth_ret3_pos", "mean"),
            breadth_ret6_pos=("breadth_ret6_pos", "mean"),
            impulse_250_share=("impulse_250_share", "mean"),
            impulse_350_share=("impulse_350_share", "mean"),
            large_range_share=("large_range_share", "mean"),
        ).reset_index()

        time_features = time_features.merge(shares, on="time", how="left")
        time_features["month"] = time_features["time"].dt.to_period("M").astype(str)

        route_df = route_df.merge(time_features.drop(columns=["month"]), on="time", how="left")

        month_features = time_features.groupby("month").agg(
            bar_count=("time", "count"),
            avg_std_coin_ret3_bps=("std_coin_ret3_bps", "mean"),
            avg_entry_range_bps=("mean_entry_range_bps", "mean"),
            median_entry_range_bps=("median_entry_range_bps", "mean"),
            avg_entry_vol_quote=("mean_entry_vol_quote", "mean"),
            median_entry_vol_quote=("median_entry_vol_quote", "mean"),
            avg_large_range_share=("large_range_share", "mean"),
            avg_breadth_ret3_pos=("breadth_ret3_pos", "mean"),
            avg_breadth_ret6_pos=("breadth_ret6_pos", "mean"),
            avg_impulse_250_share=("impulse_250_share", "mean"),
            avg_impulse_350_share=("impulse_350_share", "mean"),
            avg_mean_mkt_ret3_bps=("mean_mkt_ret3_bps", "mean"),
            avg_mean_mkt_ret6_bps=("mean_mkt_ret6_bps", "mean"),
        ).reset_index()

        route_month = route_df.groupby("month")[net_col].agg(["count", "sum", "mean", "median"]).reset_index()
        route_month = route_month.rename(columns={
            "count": "route_trade_count",
            "sum": "route_total_net_bps",
            "mean": "route_mean_net_bps",
            "median": "route_median_net_bps",
        })

        wr = route_df.assign(win=route_df[net_col] > 0).groupby("month")["win"].mean().reset_index()
        wr = wr.rename(columns={"win": "route_win_rate"})
        sc = route_df.groupby("month")["symbol"].nunique().reset_index().rename(columns={"symbol": "route_symbol_count"})

        route_month = route_month.merge(wr, on="month", how="left").merge(sc, on="month", how="left")

        month_table = month_features.merge(route_month, on="month", how="left")
        for c in ["route_trade_count", "route_symbol_count"]:
            month_table[c] = month_table[c].fillna(0).astype(int)
        for c in ["route_total_net_bps", "route_mean_net_bps", "route_median_net_bps", "route_win_rate"]:
            month_table[c] = month_table[c].fillna(0.0)

        vol_thresholds = safe_get(contract, ["experiment_design", "seed_thresholds", "avg_std_coin_ret3_bps"], [150, 175, 200, 225, 250])
        range_thresholds = safe_get(contract, ["experiment_design", "seed_thresholds", "avg_entry_range_bps"], [150, 175, 200, 225, 250])
        large_range_thresholds = safe_get(contract, ["experiment_design", "seed_thresholds", "avg_large_range_share"], [0.10, 0.15, 0.20, 0.25])

        liquidity_q = safe_get(contract, ["experiment_design", "seed_thresholds", "avg_entry_vol_quote_quantiles"], [0.25, 0.50, 0.75])
        liquidity_thresholds_month = quantile_thresholds(month_table["avg_entry_vol_quote"], liquidity_q)
        liquidity_thresholds_trade = quantile_thresholds(route_df["mean_entry_vol_quote"], liquidity_q)

        diagnostics = []
        diagnostics += threshold_diagnostic(month_table, route_df, "avg_std_coin_ret3_bps", vol_thresholds, net_col)
        diagnostics += threshold_diagnostic(month_table, route_df, "avg_entry_range_bps", range_thresholds, net_col)
        diagnostics += threshold_diagnostic(month_table, route_df, "avg_large_range_share", large_range_thresholds, net_col)
        diagnostics += threshold_diagnostic(month_table, route_df, "avg_entry_vol_quote", liquidity_thresholds_month, net_col)

        # Trade-level versions.
        diagnostics += threshold_diagnostic(month_table, route_df, "std_coin_ret3_bps", vol_thresholds, net_col)
        diagnostics += threshold_diagnostic(month_table, route_df, "mean_entry_range_bps", range_thresholds, net_col)
        diagnostics += threshold_diagnostic(month_table, route_df, "mean_entry_vol_quote", liquidity_thresholds_trade, net_col)

        diagnostics.sort(key=lambda x: x.get("combined_score", 0.0), reverse=True)

        vol_high_thr = 200
        range_high_thr = 200
        liquidity_low_thr = float(route_df["mean_entry_vol_quote"].quantile(0.25)) if len(route_df) else 0.0

        route_df["regime_vol_high"] = route_df["std_coin_ret3_bps"] >= vol_high_thr
        route_df["regime_range_high"] = route_df["mean_entry_range_bps"] >= range_high_thr
        route_df["regime_liq_low"] = route_df["mean_entry_vol_quote"] <= liquidity_low_thr

        route_df["interaction_regime"] = (
            "vol_high=" + route_df["regime_vol_high"].astype(str)
            + "|range_high=" + route_df["regime_range_high"].astype(str)
            + "|liq_low=" + route_df["regime_liq_low"].astype(str)
        )

        interaction_rows = []
        for regime, sub in route_df.groupby("interaction_regime"):
            interaction_rows.append({
                "interaction_regime": str(regime),
                "summary": summarize_trade_df(sub, net_col),
            })

        interaction_rows.sort(
            key=lambda x: x["summary"].get("total_net_bps", 0.0),
            reverse=False,
        )

        month_table_path = RUN_DIR / "volatility_range_regime_month_table.csv"
        route_trade_table_path = RUN_DIR / "volatility_range_regime_route_trades.csv"
        diagnostics_path = RUN_DIR / "volatility_range_regime_threshold_diagnostics.json"
        interaction_path = RUN_DIR / "volatility_range_regime_interaction_grid.json"

        month_table.to_csv(month_table_path, index=False)
        route_df.to_csv(route_trade_table_path, index=False)
        dump_json(diagnostics_path, {"threshold_diagnostics": diagnostics})
        dump_json(interaction_path, {"interaction_grid": interaction_rows})

        top_diag = diagnostics[0] if diagnostics else None
        worst_interaction = interaction_rows[0] if interaction_rows else None
        best_interaction = interaction_rows[-1] if interaction_rows else None

        findings = []

        if top_diag:
            findings.append({
                "finding_id": "VRR_F1_TOP_EXPLANATORY_THRESHOLD",
                "severity": "ATTENTION",
                "claim": "A volatility/range/liquidity threshold separates route outcomes diagnostically.",
                "evidence": top_diag,
                "note": "This is explanatory only, not release approval.",
            })

        if worst_interaction:
            findings.append({
                "finding_id": "VRR_F2_WORST_INTERACTION_REGIME",
                "severity": "ATTENTION",
                "claim": "A volatility/range/liquidity interaction bucket has the worst route performance.",
                "evidence": worst_interaction,
                "note": "Interaction requires separate evaluator and contract before any candidate use.",
            })

        findings.append({
            "finding_id": "VRR_F3_CONTRACT_REMAINS_DIAGNOSTIC_ONLY",
            "severity": "CONTROL",
            "claim": "The runner did not create a candidate or reopen the blocked route.",
            "evidence": {
                "diagnostic_only": safe_get(contract, ["experiment_design", "diagnostic_only"]),
                "candidate_generation_allowed_now": safe_get(contract, ["experiment_design", "candidate_generation_allowed_now"]),
                "family_release_allowed_now": safe_get(contract, ["experiment_design", "family_release_allowed_now"]),
                "repeat_same_route_allowed": safe_get(contract, ["blocked_route_guard", "repeat_same_route_allowed"]),
            },
        })

        diagnostic_status = "VOLATILITY_RANGE_REGIME_FILTER_DIAGNOSTIC_COMPLETE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "EVALUATE_VOLATILITY_RANGE_REGIME_DIAGNOSTIC"
        reason = f"threshold_diagnostic_count={len(diagnostics)}; interaction_regime_count={len(interaction_rows)}; route_trade_count={len(route_df)}"

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),

            "diagnostic_status": diagnostic_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,

            "contract_source": str(CONTRACT_LATEST),
            "contract_id": contract.get("contract_id"),
            "research_key": contract.get("research_key"),

            "panel_path": str(panel),
            "panel_rows": int(len(df)),
            "panel_symbol_count": int(df["symbol"].nunique()),
            "panel_start": str(df["time"].min()),
            "panel_end": str(df["time"].max()),

            "route_proxy_used_for_diagnostic_only": {
                "threshold_coin_ret3_bps": threshold,
                "hold_hours": hold_hours,
                "entry_range_cap_bps": entry_range_cap,
                "mkt_filter": mkt_filter,
                "cost_bps_total": COST_BPS_TOTAL,
                "route_trade_count": int(len(route_df)),
                "route_total_net_bps": float(route_df[net_col].sum()) if len(route_df) else 0.0,
                "route_mean_net_bps": float(route_df[net_col].mean()) if len(route_df) else None,
                "route_win_rate": float((route_df[net_col] > 0).mean()) if len(route_df) else None,
            },

            "top_threshold_diagnostics": diagnostics[:20],
            "interaction_grid": interaction_rows,
            "worst_interaction_regime": worst_interaction,
            "best_interaction_regime": best_interaction,

            "outputs": {
                "month_table_csv": str(month_table_path),
                "route_trade_table_csv": str(route_trade_table_path),
                "threshold_diagnostics_json": str(diagnostics_path),
                "interaction_grid_json": str(interaction_path),
            },

            "findings": findings,

            "decision": {
                "candidate_generation_recommended_now": False,
                "family_release_recommended": False,
                "promotion_recommended": False,
                "runtime_change_recommended": False,
                "capital_change_recommended": False,
                "repeat_same_route_recommended": False,
                "why_no_action": [
                    "contract_is_diagnostic_only",
                    "blocked_route_known_failure",
                    "thresholds_are_explanatory_not_release_filters",
                    "separate_evaluator_required",
                    "new_candidate_contract_required_before any candidate generation",
                ],
            },

            "safety": {
                "read_only": True,
                "offline_only": True,
                "mutate_runtime_allowed": False,
                "launcher_allowed": False,
                "patch_runtime_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "capital_change_allowed": False,
                "family_disable_allowed": False,
                "real_orders_allowed": False,
                "execution_performed": True,
            },

            "critical": critical,
            "attention": attention,
            "info": info,
        }

    out_json = RUN_DIR / "volatility_range_regime_filter_diagnostic_v1_state.json"
    out_md = RUN_DIR / "volatility_range_regime_filter_diagnostic_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS VOLATILITY RANGE REGIME FILTER DIAGNOSTIC v1

diagnostic_status: {result.get("diagnostic_status")}  
severity: {result.get("severity")}  
allowed_scope: {result.get("allowed_scope")}  
next_action: {result.get("next_action")}  
reason: {result.get("reason")}

panel_path: {result.get("panel_path")}  
panel_rows: {result.get("panel_rows")}  
panel_symbol_count: {result.get("panel_symbol_count")}

## Route Proxy Used For Diagnostic Only

{json.dumps(result.get("route_proxy_used_for_diagnostic_only"), indent=2, default=str)}

## Top Threshold Diagnostics

{json.dumps(result.get("top_threshold_diagnostics"), indent=2, default=str)[:24000]}

## Interaction Grid

{json.dumps(result.get("interaction_grid"), indent=2, default=str)[:16000]}

## Findings

{json.dumps(result.get("findings"), indent=2, default=str)}

## Decision

{json.dumps(result.get("decision"), indent=2, default=str)}

## Safety

read_only: True  
offline_only: True  
mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: {safe_get(result, ["safety", "execution_performed"])}

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS VOLATILITY RANGE REGIME FILTER DIAGNOSTIC v1")
    print("=" * 100)
    print(f"diagnostic_status: {result.get('diagnostic_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print()
    print("ROUTE PROXY DIAGNOSTIC ONLY")
    print("-" * 100)
    print(result.get("route_proxy_used_for_diagnostic_only"))
    print()
    print("TOP THRESHOLD DIAGNOSTICS")
    print("-" * 100)
    for row in (result.get("top_threshold_diagnostics") or [])[:10]:
        print(row)
    print()
    print("INTERACTION GRID")
    print("-" * 100)
    for row in (result.get("interaction_grid") or [])[:10]:
        print(row)
    print()
    print("DECISION")
    print("-" * 100)
    print(json.dumps(result.get("decision"), indent=2, default=str))
    print()
    print("SAFETY")
    print("-" * 100)
    print("read_only: True")
    print("offline_only: True")
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print(f"execution_performed: {safe_get(result, ['safety', 'execution_performed'])}")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if result.get("severity") != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
