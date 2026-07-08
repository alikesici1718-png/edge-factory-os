from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_regime_filtered_candidate_backtest_runner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CANDIDATE_CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_candidate_contracts"
    / "regime_filtered_impulse_candidate_contract_latest.json"
)

CANDIDATE_LESSON_CHECKER_LATEST = (
    BASE_DIR
    / "edge_factory_os_candidate_route_lesson_memory_checker_v1"
    / "candidate_route_lesson_memory_checker_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"regime_filtered_candidate_backtest_runner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "regime_filtered_candidate_backtest_runner_latest.json"
LATEST_MD = OUT_ROOT / "regime_filtered_candidate_backtest_runner_latest.md"


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


def inum(v: Any, default=0):
    try:
        if v is None:
            return default
        return int(float(v))
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def summarize_trades(df, ret_col: str) -> Dict[str, Any]:
    if df is None or len(df) == 0 or ret_col not in df.columns:
        return {
            "trade_count": 0,
            "valid_return_count": 0,
            "symbol_count": 0,
            "win_rate": None,
            "total_net_bps": 0.0,
            "mean_net_bps": None,
            "median_net_bps": None,
            "profit_factor": None,
            "positive_month_rate": None,
            "month_count": 0,
        }

    vals = df[ret_col].dropna()

    if len(vals) == 0:
        return {
            "trade_count": int(len(df)),
            "valid_return_count": 0,
            "symbol_count": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
            "win_rate": None,
            "total_net_bps": 0.0,
            "mean_net_bps": None,
            "median_net_bps": None,
            "profit_factor": None,
            "positive_month_rate": None,
            "month_count": 0,
        }

    wins = vals[vals > 0]
    losses = vals[vals < 0]

    pf = None
    if len(losses) > 0 and abs(float(losses.sum())) > 0:
        pf = float(wins.sum()) / abs(float(losses.sum()))
    elif len(wins) > 0:
        pf = 999.0

    month_count = 0
    positive_month_rate = None
    monthly_total = {}

    if "month" in df.columns:
        m = df.groupby("month")[ret_col].sum().dropna()
        month_count = int(len(m))
        if month_count > 0:
            positive_month_rate = float((m > 0).mean())
            monthly_total = {str(k): float(v) for k, v in m.items()}

    return {
        "trade_count": int(len(df)),
        "valid_return_count": int(len(vals)),
        "symbol_count": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
        "win_count": int((vals > 0).sum()),
        "loss_count": int((vals < 0).sum()),
        "win_rate": float((vals > 0).mean()),
        "total_net_bps": float(vals.sum()),
        "mean_net_bps": float(vals.mean()),
        "median_net_bps": float(vals.median()),
        "best_net_bps": float(vals.max()),
        "worst_net_bps": float(vals.min()),
        "profit_factor": pf,
        "month_count": month_count,
        "positive_month_rate": positive_month_rate,
        "monthly_total_net_bps": monthly_total,
    }


def symbol_concentration(df, ret_col: str, limit: int = 15) -> Dict[str, Any]:
    if df is None or len(df) == 0 or ret_col not in df.columns or "symbol" not in df.columns:
        return {
            "top_loss_symbols": [],
            "top_win_symbols": [],
            "top_symbol_abs_share": None,
        }

    grouped = df.groupby("symbol")[ret_col].agg(["count", "sum", "mean"]).reset_index()
    grouped = grouped.rename(columns={"count": "trade_count", "sum": "total_net_bps", "mean": "mean_net_bps"})

    total = float(df[ret_col].sum())
    grouped["abs_share_of_total"] = grouped["total_net_bps"].abs() / max(abs(total), 1e-9)

    top_losses = grouped.sort_values("total_net_bps", ascending=True).head(limit).to_dict("records")
    top_wins = grouped.sort_values("total_net_bps", ascending=False).head(limit).to_dict("records")

    top_abs_share = None
    if len(grouped) > 0:
        top_abs_share = float(grouped["abs_share_of_total"].max())

    return {
        "top_loss_symbols": top_losses,
        "top_win_symbols": top_wins,
        "top_symbol_abs_share": top_abs_share,
    }


def split_train_oos(df):
    if df is None or len(df) == 0 or "time" not in df.columns:
        return {
            "train": df,
            "oos": df.iloc[0:0] if df is not None else None,
            "split_time": None,
        }

    times = df["time"].dropna().sort_values()

    if len(times) == 0:
        return {
            "train": df,
            "oos": df.iloc[0:0],
            "split_time": None,
        }

    split_idx = int(len(times) * 0.70)
    split_idx = max(0, min(split_idx, len(times) - 1))
    split_time = times.iloc[split_idx]

    return {
        "train": df[df["time"] <= split_time],
        "oos": df[df["time"] > split_time],
        "split_time": str(split_time),
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(CANDIDATE_CONTRACT_LATEST)
    lesson_check = load_json(CANDIDATE_LESSON_CHECKER_LATEST)

    if not isinstance(contract, dict):
        critical.append("candidate_contract_latest_missing")
        contract = {}

    if not isinstance(lesson_check, dict):
        critical.append("candidate_route_lesson_memory_checker_latest_missing")
        lesson_check = {}

    if contract.get("candidate_key") != "REGIME_FILTERED_IMPULSE_ROUTE_CANDIDATE_V1":
        critical.append(f"unexpected_candidate_key:{contract.get('candidate_key')}")

    if lesson_check.get("checker_status") != "CANDIDATE_ROUTE_LESSON_MEMORY_PASS_NEW_ROUTE":
        critical.append(f"lesson_memory_not_pass_new_route:{lesson_check.get('checker_status')}")

    if safe_get(lesson_check, ["release_gate_feed", "backtest_allowed_by_lesson_memory"]) is not True:
        critical.append("backtest_not_allowed_by_lesson_memory")

    candidate_route_hash = contract.get("candidate_route_hash")
    lesson_route_hash = lesson_check.get("candidate_route_hash")

    if candidate_route_hash != lesson_route_hash:
        critical.append(f"route_hash_mismatch:contract={candidate_route_hash};lesson={lesson_route_hash}")

    panel_path = safe_get(contract, ["universe_input", "panel_path"])

    if not panel_path:
        critical.append("panel_path_missing_from_contract")

    panel = Path(str(panel_path)) if panel_path else None

    if panel is None or not panel.exists():
        critical.append(f"panel_path_not_found:{panel_path}")

    base_rules = safe_get(contract, ["candidate_definition", "base_signal_rules"], {}) or {}
    regime_rules = safe_get(contract, ["candidate_definition", "new_regime_filter_rules"], {}) or {}

    coin_ret3_min = fnum(base_rules.get("coin_ret3_bps_min"), 350.0)
    hold_hours = inum(base_rules.get("hold_hours"), 12)
    entry_range_cap = fnum(base_rules.get("entry_range_cap_bps"), None)
    market_filter = base_rules.get("market_filter") or {}
    cost_bps_total = fnum(base_rules.get("cost_bps_total"), 75.0)

    std_max = fnum(regime_rules.get("std_coin_ret3_bps_max"), 200.0)
    mean_range_max = fnum(regime_rules.get("mean_entry_range_bps_max"), 200.0)

    if critical:
        runner_status = "REGIME_FILTERED_CANDIDATE_BACKTEST_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_INPUTS_BEFORE_BACKTEST"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "runner_status": runner_status,
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

        dump_json(RUN_DIR / "regime_filtered_candidate_backtest_runner_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS REGIME FILTERED CANDIDATE BACKTEST RUNNER v1")
        print("=" * 100)
        print(f"runner_status: {runner_status}")
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
        critical.append(f"panel_missing_required_columns:{missing}")

    if critical:
        runner_status = "REGIME_FILTERED_CANDIDATE_BACKTEST_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_PANEL_COLUMNS"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "runner_status": runner_status,
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
        df[net_col] = df[gross_col] - float(cost_bps_total or 75.0)

        # Pre-outcome cross-sectional regime features at each timestamp.
        time_group = df.groupby("time")
        time_features = time_group.agg(
            symbol_count=("symbol", "nunique"),
            std_coin_ret3_bps=("coin_ret3_bps", "std"),
            mean_entry_range_bps=("entry_range_bps", "mean"),
            mean_entry_vol_quote=("entry_vol_quote", "mean"),
            median_entry_vol_quote=("entry_vol_quote", "median"),
            mean_mkt_ret3_bps=("mkt_ret3_bps", "mean"),
            mean_mkt_ret6_bps=("mkt_ret6_bps", "mean"),
        ).reset_index()

        # Low liquidity cutoff is computed from pre-outcome timestamp-level liquidity.
        liquidity_cutoff = float(time_features["mean_entry_vol_quote"].quantile(0.25))

        time_features["regime_vol_high"] = time_features["std_coin_ret3_bps"] >= float(std_max or 200.0)
        time_features["regime_range_high"] = time_features["mean_entry_range_bps"] >= float(mean_range_max or 200.0)
        time_features["regime_liq_low"] = time_features["mean_entry_vol_quote"] <= liquidity_cutoff

        df = df.merge(time_features, on="time", how="left")

        # Baseline old route, used only as comparison. New candidate adds regime filters.
        baseline_mask = df["coin_ret3_bps"] >= float(coin_ret3_min or 350.0)

        if entry_range_cap is not None:
            baseline_mask = baseline_mask & (df["entry_range_bps"] <= float(entry_range_cap))

        if isinstance(market_filter, dict):
            if market_filter.get("mkt_ret3_min_bps") is not None:
                baseline_mask = baseline_mask & (df["mkt_ret3_bps"] >= float(market_filter["mkt_ret3_min_bps"]))
            if market_filter.get("mkt_ret6_min_bps") is not None:
                baseline_mask = baseline_mask & (df["mkt_ret6_bps"] >= float(market_filter["mkt_ret6_min_bps"]))

        regime_mask = (
            (df["regime_vol_high"] == False)
            & (df["regime_range_high"] == False)
            & (df["regime_liq_low"] == False)
        )

        candidate_mask = baseline_mask & regime_mask

        baseline_trades = df.loc[baseline_mask].dropna(subset=[net_col]).copy()
        candidate_trades = df.loc[candidate_mask].dropna(subset=[net_col]).copy()
        excluded_by_regime = df.loc[baseline_mask & (~regime_mask)].dropna(subset=[net_col]).copy()

        split_candidate = split_train_oos(candidate_trades)
        split_baseline = split_train_oos(baseline_trades)

        candidate_summary = {
            "all": summarize_trades(candidate_trades, net_col),
            "train": summarize_trades(split_candidate["train"], net_col),
            "oos": summarize_trades(split_candidate["oos"], net_col),
            "split_time": split_candidate["split_time"],
        }

        baseline_summary = {
            "all": summarize_trades(baseline_trades, net_col),
            "train": summarize_trades(split_baseline["train"], net_col),
            "oos": summarize_trades(split_baseline["oos"], net_col),
            "split_time": split_baseline["split_time"],
        }

        excluded_summary = {
            "all": summarize_trades(excluded_by_regime, net_col),
        }

        candidate_symbols = symbol_concentration(candidate_trades, net_col)
        baseline_symbols = symbol_concentration(baseline_trades, net_col)

        monthly_table = candidate_trades.groupby("month")[net_col].agg(["count", "sum", "mean", "median"]).reset_index()
        if len(monthly_table) > 0:
            monthly_table = monthly_table.rename(
                columns={
                    "count": "trade_count",
                    "sum": "total_net_bps",
                    "mean": "mean_net_bps",
                    "median": "median_net_bps",
                }
            )
            wr = candidate_trades.assign(win=candidate_trades[net_col] > 0).groupby("month")["win"].mean().reset_index()
            wr = wr.rename(columns={"win": "win_rate"})
            sym = candidate_trades.groupby("month")["symbol"].nunique().reset_index().rename(columns={"symbol": "symbol_count"})
            monthly_table = monthly_table.merge(wr, on="month", how="left").merge(sym, on="month", how="left")
        else:
            monthly_table = pd.DataFrame(columns=["month", "trade_count", "total_net_bps", "mean_net_bps", "median_net_bps", "win_rate", "symbol_count"])

        candidate_trade_path = RUN_DIR / "regime_filtered_candidate_trades.csv"
        baseline_trade_path = RUN_DIR / "regime_filtered_candidate_baseline_trades.csv"
        monthly_table_path = RUN_DIR / "regime_filtered_candidate_monthly_table.csv"

        candidate_trades.to_csv(candidate_trade_path, index=False)
        baseline_trades.to_csv(baseline_trade_path, index=False)
        monthly_table.to_csv(monthly_table_path, index=False)

        # Preview only. Evaluator will make formal pass/fail.
        all_s = candidate_summary["all"]
        train_s = candidate_summary["train"]
        oos_s = candidate_summary["oos"]

        preview_checks = {
            "all_trade_count": {
                "pass": (all_s.get("trade_count") or 0) >= 300,
                "value": all_s.get("trade_count"),
                "required": 300,
            },
            "oos_trade_count": {
                "pass": (oos_s.get("trade_count") or 0) >= 75,
                "value": oos_s.get("trade_count"),
                "required": 75,
            },
            "all_mean_positive": {
                "pass": (all_s.get("mean_net_bps") is not None and all_s.get("mean_net_bps") > 0),
                "value": all_s.get("mean_net_bps"),
                "required": ">0",
            },
            "train_mean_positive": {
                "pass": (train_s.get("mean_net_bps") is not None and train_s.get("mean_net_bps") > 0),
                "value": train_s.get("mean_net_bps"),
                "required": ">0",
            },
            "oos_mean_positive": {
                "pass": (oos_s.get("mean_net_bps") is not None and oos_s.get("mean_net_bps") > 0),
                "value": oos_s.get("mean_net_bps"),
                "required": ">0",
            },
            "train_profit_factor": {
                "pass": (train_s.get("profit_factor") is not None and train_s.get("profit_factor") >= 1.10),
                "value": train_s.get("profit_factor"),
                "required": ">=1.10",
            },
            "oos_profit_factor": {
                "pass": (oos_s.get("profit_factor") is not None and oos_s.get("profit_factor") >= 1.10),
                "value": oos_s.get("profit_factor"),
                "required": ">=1.10",
            },
            "oos_win_rate": {
                "pass": (oos_s.get("win_rate") is not None and oos_s.get("win_rate") >= 0.45),
                "value": oos_s.get("win_rate"),
                "required": ">=0.45",
            },
            "all_positive_month_rate": {
                "pass": (all_s.get("positive_month_rate") is not None and all_s.get("positive_month_rate") >= 0.55),
                "value": all_s.get("positive_month_rate"),
                "required": ">=0.55",
            },
            "oos_positive_month_rate": {
                "pass": (oos_s.get("positive_month_rate") is not None and oos_s.get("positive_month_rate") >= 0.50),
                "value": oos_s.get("positive_month_rate"),
                "required": ">=0.50",
            },
            "symbol_concentration": {
                "pass": (
                    candidate_symbols.get("top_symbol_abs_share") is None
                    or candidate_symbols.get("top_symbol_abs_share") <= 0.50
                ),
                "value": candidate_symbols.get("top_symbol_abs_share"),
                "required": "<=0.50",
            },
        }

        preview_passed = [k for k, v in preview_checks.items() if v.get("pass") is True]
        preview_failed = [k for k, v in preview_checks.items() if v.get("pass") is not True]

        preview_pass = len(preview_failed) == 0

        runner_status = "REGIME_FILTERED_CANDIDATE_BACKTEST_COMPLETE"
        severity = "ATTENTION"
        allowed_scope = "OFFLINE_RESEARCH_ONLY"
        next_action = "EVALUATE_REGIME_FILTERED_CANDIDATE_BACKTEST"
        reason = (
            f"candidate_trades={candidate_summary['all'].get('trade_count')}; "
            f"baseline_trades={baseline_summary['all'].get('trade_count')}; "
            f"preview_pass={preview_pass}"
        )

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),

            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,

            "candidate_contract_source": str(CANDIDATE_CONTRACT_LATEST),
            "lesson_checker_source": str(CANDIDATE_LESSON_CHECKER_LATEST),

            "candidate_key": contract.get("candidate_key"),
            "contract_id": contract.get("contract_id"),
            "candidate_route_hash": candidate_route_hash,

            "panel_path": str(panel),
            "panel_rows": int(len(df)),
            "panel_symbol_count": int(df["symbol"].nunique()),
            "panel_start": str(df["time"].min()),
            "panel_end": str(df["time"].max()),

            "rules_used": {
                "coin_ret3_min": coin_ret3_min,
                "hold_hours": hold_hours,
                "entry_range_cap": entry_range_cap,
                "market_filter": market_filter,
                "cost_bps_total": cost_bps_total,
                "std_coin_ret3_bps_max": std_max,
                "mean_entry_range_bps_max": mean_range_max,
                "liquidity_cutoff_q25_mean_entry_vol_quote": liquidity_cutoff,
                "target_interaction_regime": "vol_high=False|range_high=False|liq_low=False",
            },

            "baseline_summary_old_route_comparison_only": baseline_summary,
            "candidate_summary": candidate_summary,
            "excluded_by_regime_summary": excluded_summary,

            "candidate_symbol_concentration": candidate_symbols,
            "baseline_symbol_concentration": baseline_symbols,

            "preview_release_checks": preview_checks,
            "preview_passed_checks": preview_passed,
            "preview_failed_checks": preview_failed,
            "preview_candidate_quality_pass": preview_pass,

            "outputs": {
                "candidate_trades_csv": str(candidate_trade_path),
                "baseline_trades_csv": str(baseline_trade_path),
                "monthly_table_csv": str(monthly_table_path),
            },

            "release_gate_feed": {
                "REGIME_FILTERED_CANDIDATE_BACKTEST_RAN": True,
                "REGIME_FILTERED_CANDIDATE_PREVIEW_PASS": preview_pass,
                "status": runner_status,
                "candidate_route_hash": candidate_route_hash,
                "release_allowed_from_this_runner_alone": False,
            },

            "decision": {
                "candidate_generation_recommended_now": False,
                "family_release_recommended": False,
                "promotion_recommended": False,
                "runtime_change_recommended": False,
                "capital_change_recommended": False,
                "repeat_known_failed_route_recommended": False,
                "why_no_action": [
                    "runner_is_offline_research_only",
                    "separate_evaluator_required",
                    "release_gate_required",
                    "no_runtime_or_capital_action_allowed",
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

    out_json = RUN_DIR / "regime_filtered_candidate_backtest_runner_v1_state.json"
    out_md = RUN_DIR / "regime_filtered_candidate_backtest_runner_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS REGIME FILTERED CANDIDATE BACKTEST RUNNER v1

runner_status: {result.get("runner_status")}  
severity: {result.get("severity")}  
allowed_scope: {result.get("allowed_scope")}  
next_action: {result.get("next_action")}  
reason: {result.get("reason")}

candidate_key: {result.get("candidate_key")}  
contract_id: {result.get("contract_id")}  
candidate_route_hash: {result.get("candidate_route_hash")}

panel_path: {result.get("panel_path")}  
panel_rows: {result.get("panel_rows")}  
panel_symbol_count: {result.get("panel_symbol_count")}

## Rules Used

{json.dumps(result.get("rules_used"), indent=2, default=str)}

## Candidate Summary

{json.dumps(result.get("candidate_summary"), indent=2, default=str)}

## Baseline Old Route Comparison Only

{json.dumps(result.get("baseline_summary_old_route_comparison_only"), indent=2, default=str)}

## Excluded By Regime Summary

{json.dumps(result.get("excluded_by_regime_summary"), indent=2, default=str)}

## Preview Checks

{json.dumps(result.get("preview_release_checks"), indent=2, default=str)}

preview_candidate_quality_pass: {result.get("preview_candidate_quality_pass")}  
preview_passed_checks: {result.get("preview_passed_checks")}  
preview_failed_checks: {result.get("preview_failed_checks")}

## Release Gate Feed

{json.dumps(result.get("release_gate_feed"), indent=2, default=str)}

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
    print("EDGE FACTORY OS REGIME FILTERED CANDIDATE BACKTEST RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print()
    print("CANDIDATE")
    print("-" * 100)
    print(f"candidate_key: {result.get('candidate_key')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"candidate_route_hash: {result.get('candidate_route_hash')}")
    print()
    print("RULES USED")
    print("-" * 100)
    print(json.dumps(result.get("rules_used"), indent=2, default=str))
    print()
    print("CANDIDATE SUMMARY")
    print("-" * 100)
    print(json.dumps(result.get("candidate_summary"), indent=2, default=str))
    print()
    print("BASELINE OLD ROUTE COMPARISON ONLY")
    print("-" * 100)
    print(json.dumps(result.get("baseline_summary_old_route_comparison_only"), indent=2, default=str))
    print()
    print("PREVIEW CHECKS")
    print("-" * 100)
    print(f"preview_candidate_quality_pass: {result.get('preview_candidate_quality_pass')}")
    print(f"preview_passed_checks: {result.get('preview_passed_checks')}")
    print(f"preview_failed_checks: {result.get('preview_failed_checks')}")
    print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result.get("release_gate_feed"))
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
