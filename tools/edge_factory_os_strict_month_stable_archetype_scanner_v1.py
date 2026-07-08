from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_strict_month_stable_archetype_scanner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "strict_month_stable_new_archetype_search_contract_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"strict_month_stable_archetype_scanner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "strict_month_stable_archetype_scanner_latest.json"
LATEST_MD = OUT_ROOT / "strict_month_stable_archetype_scanner_latest.md"

COST_BPS_TOTAL = 75.0


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, default=str)


def stable_hash(obj: Any) -> str:
    text = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


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
            "symbol_count": 0,
            "month_count": 0,
            "positive_month_count": 0,
            "negative_month_count": 0,
            "positive_month_rate": None,
            "total_net_bps": 0.0,
            "mean_net_bps": None,
            "win_rate": None,
            "profit_factor": None,
            "monthly_total_net_bps": {},
        }

    vals = df[ret_col].dropna()

    if len(vals) == 0:
        return {
            "trade_count": int(len(df)),
            "symbol_count": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
            "month_count": 0,
            "positive_month_count": 0,
            "negative_month_count": 0,
            "positive_month_rate": None,
            "total_net_bps": 0.0,
            "mean_net_bps": None,
            "win_rate": None,
            "profit_factor": None,
            "monthly_total_net_bps": {},
        }

    wins = vals[vals > 0]
    losses = vals[vals < 0]

    pf = None
    if len(losses) > 0 and abs(float(losses.sum())) > 0:
        pf = float(wins.sum()) / abs(float(losses.sum()))
    elif len(wins) > 0:
        pf = 999.0

    monthly_total = {}
    month_count = 0
    positive_month_count = 0
    negative_month_count = 0
    positive_month_rate = None

    if "month" in df.columns:
        m = df.groupby("month")[ret_col].sum().dropna()
        monthly_total = {str(k): float(v) for k, v in m.items()}
        month_count = int(len(m))
        if month_count:
            positive_month_count = int((m > 0).sum())
            negative_month_count = int((m < 0).sum())
            positive_month_rate = float((m > 0).mean())

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
        "positive_month_count": positive_month_count,
        "negative_month_count": negative_month_count,
        "positive_month_rate": positive_month_rate,
        "monthly_total_net_bps": monthly_total,
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


def symbol_concentration(df, ret_col: str) -> Dict[str, Any]:
    if df is None or len(df) == 0 or "symbol" not in df.columns or ret_col not in df.columns:
        return {
            "top_symbol_abs_share": None,
            "top_loss_symbols": [],
            "top_win_symbols": [],
        }

    grouped = df.groupby("symbol")[ret_col].agg(["count", "sum", "mean"]).reset_index()
    grouped = grouped.rename(columns={"count": "trade_count", "sum": "total_net_bps", "mean": "mean_net_bps"})

    total = float(df[ret_col].sum()) if len(df) else 0.0
    grouped["abs_share_of_total"] = grouped["total_net_bps"].abs() / max(abs(total), 1e-9)

    return {
        "top_symbol_abs_share": float(grouped["abs_share_of_total"].max()) if len(grouped) else None,
        "top_loss_symbols": grouped.sort_values("total_net_bps", ascending=True).head(8).to_dict("records"),
        "top_win_symbols": grouped.sort_values("total_net_bps", ascending=False).head(8).to_dict("records"),
    }


def evaluate_rule(df, rule: Dict[str, Any], blocked_hashes: set, strict_rule: Dict[str, Any]) -> Dict[str, Any]:
    side = rule["side"]
    hold_hours = int(rule["hold_hours"])

    if side == "long":
        ret_col = f"net_long_{hold_hours}h_bps"
    else:
        ret_col = f"net_short_{hold_hours}h_bps"

    mask = rule["mask"]
    trades = df.loc[mask].dropna(subset=[ret_col]).copy()

    route_signature = {
        "archetype_key": rule["archetype_key"],
        "side": side,
        "hold_hours": hold_hours,
        "params": rule["params"],
    }

    route_hash = stable_hash(route_signature)

    split = split_train_oos(trades)

    all_s = summarize_trades(trades, ret_col)
    train_s = summarize_trades(split["train"], ret_col)
    oos_s = summarize_trades(split["oos"], ret_col)
    sym = symbol_concentration(trades, ret_col)

    min_active_months = int(strict_rule.get("min_active_months", 12))
    min_positive_months = int(strict_rule.get("min_positive_months", 11))
    min_positive_month_rate = float(strict_rule.get("min_positive_month_rate", 11 / 12))

    strict_month_pass = (
        all_s.get("month_count", 0) >= min_active_months
        and all_s.get("positive_month_count", 0) >= min_positive_months
        and (all_s.get("positive_month_rate") is not None and all_s.get("positive_month_rate") >= min_positive_month_rate)
    )

    checks = {
        "route_not_blocked": {
            "pass": route_hash not in blocked_hashes,
            "value": route_hash,
            "required": "not in candidate_route_blocklist",
        },
        "all_trade_count": {
            "pass": all_s.get("trade_count", 0) >= 300,
            "value": all_s.get("trade_count"),
            "required": ">=300",
        },
        "oos_trade_count": {
            "pass": oos_s.get("trade_count", 0) >= 75,
            "value": oos_s.get("trade_count"),
            "required": ">=75",
        },
        "strict_month_stability_11_of_12": {
            "pass": strict_month_pass,
            "value": {
                "month_count": all_s.get("month_count"),
                "positive_month_count": all_s.get("positive_month_count"),
                "positive_month_rate": all_s.get("positive_month_rate"),
            },
            "required": f"month_count>={min_active_months} AND positive_month_count>={min_positive_months}",
        },
        "all_mean_positive": {
            "pass": fnum(all_s.get("mean_net_bps"), -999999) > 0,
            "value": all_s.get("mean_net_bps"),
            "required": ">0",
        },
        "train_mean_positive": {
            "pass": fnum(train_s.get("mean_net_bps"), -999999) > 0,
            "value": train_s.get("mean_net_bps"),
            "required": ">0",
        },
        "oos_mean_positive": {
            "pass": fnum(oos_s.get("mean_net_bps"), -999999) > 0,
            "value": oos_s.get("mean_net_bps"),
            "required": ">0",
        },
        "train_profit_factor": {
            "pass": fnum(train_s.get("profit_factor"), 0) >= 1.10,
            "value": train_s.get("profit_factor"),
            "required": ">=1.10",
        },
        "oos_profit_factor": {
            "pass": fnum(oos_s.get("profit_factor"), 0) >= 1.10,
            "value": oos_s.get("profit_factor"),
            "required": ">=1.10",
        },
        "symbol_concentration": {
            "pass": sym.get("top_symbol_abs_share") is None or fnum(sym.get("top_symbol_abs_share"), 999) <= 0.50,
            "value": sym.get("top_symbol_abs_share"),
            "required": "<=0.50",
        },
    }

    passed = [k for k, v in checks.items() if v.get("pass") is True]
    failed = [k for k, v in checks.items() if v.get("pass") is not True]

    # Scanner score only. This is not release approval.
    score = 0.0
    score += 100 if strict_month_pass else 0
    score += min(all_s.get("positive_month_count", 0), 12) * 6
    score += min(all_s.get("trade_count", 0), 1000) / 20
    score += max(fnum(all_s.get("mean_net_bps"), 0) or 0, 0) / 2
    score += max(fnum(train_s.get("profit_factor"), 0) or 0, 0) * 5
    score += max(fnum(oos_s.get("profit_factor"), 0) or 0, 0) * 5
    score -= len(failed) * 20

    return {
        "route_hash": route_hash,
        "route_hash_blocked": route_hash in blocked_hashes,
        "archetype_key": rule["archetype_key"],
        "side": side,
        "hold_hours": hold_hours,
        "params": rule["params"],
        "route_signature": route_signature,

        "all": all_s,
        "train": train_s,
        "oos": oos_s,
        "split_time": split["split_time"],
        "symbol_concentration": sym,

        "strict_month_stability_pass": strict_month_pass,
        "checks": checks,
        "passed_checks": passed,
        "failed_checks": failed,

        "scanner_preview_all_checks_pass": len(failed) == 0,
        "scanner_score": score,

        "candidate_generation_allowed_now": False,
        "family_release_allowed_now": False,
        "runtime_change_allowed_now": False,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(CONTRACT_LATEST)

    if not isinstance(contract, dict):
        critical.append("strict_month_stable_new_archetype_contract_missing")
        contract = {}

    if contract.get("research_key") != "STRICT_MONTH_STABLE_NEW_ARCHETYPE_SEARCH_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if safe_get(contract, ["required_scanner_behavior", "candidate_generation_allowed_now"]) is not False:
        critical.append("contract_allows_candidate_generation_unexpectedly")

    if safe_get(contract, ["required_scanner_behavior", "family_release_allowed_now"]) is not False:
        critical.append("contract_allows_family_release_unexpectedly")

    panel_path = safe_get(contract, ["universe_input", "panel_path"])

    if not panel_path:
        critical.append("panel_path_missing_from_contract")

    panel = Path(str(panel_path)) if panel_path else None

    if panel is None or not panel.exists():
        critical.append(f"panel_not_found:{panel_path}")

    blocked_hashes = set(safe_get(contract, ["lesson_memory_context", "blocked_route_hashes"], []) or [])

    strict_rule = {
        "min_active_months": int(safe_get(contract, ["strict_month_stability_policy", "min_active_months"], 12)),
        "min_positive_months": int(safe_get(contract, ["strict_month_stability_policy", "min_positive_months"], 11)),
        "min_positive_month_rate": float(safe_get(contract, ["strict_month_stability_policy", "min_positive_month_rate"], 11 / 12)),
    }

    if critical:
        scanner_status = "STRICT_MONTH_STABLE_ARCHETYPE_SCANNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CONTRACT_OR_PANEL_INPUT"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "scanner_status": scanner_status,
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

        dump_json(RUN_DIR / "strict_month_stable_archetype_scanner_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS STRICT MONTH STABLE ARCHETYPE SCANNER v1")
        print("=" * 100)
        print(f"scanner_status: {scanner_status}")
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
        "open",
        "high",
        "low",
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
        scanner_status = "STRICT_MONTH_STABLE_ARCHETYPE_SCANNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_PANEL_COLUMNS"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "scanner_status": scanner_status,
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

        for hold in [3, 6, 12]:
            future_col = f"future_close_{hold}h"
            gross_long = f"gross_long_{hold}h_bps"
            net_long = f"net_long_{hold}h_bps"
            net_short = f"net_short_{hold}h_bps"

            df[future_col] = df.groupby("symbol")["close"].shift(-hold)
            df[gross_long] = ((df[future_col] / df["close"]) - 1.0) * 10000.0
            df[net_long] = df[gross_long] - COST_BPS_TOTAL
            df[net_short] = (-df[gross_long]) - COST_BPS_TOTAL

        # Timestamp-level pre-outcome market context.
        time_features = df.groupby("time").agg(
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
        tmp["breadth_ret3_neg"] = tmp["coin_ret3_bps"] < 0
        tmp["breadth_ret6_pos"] = tmp["coin_ret6_bps"] > 0
        tmp["breadth_ret6_neg"] = tmp["coin_ret6_bps"] < 0
        tmp["impulse_250_share"] = tmp["coin_ret3_bps"] >= 250
        tmp["drop_250_share"] = tmp["coin_ret3_bps"] <= -250
        tmp["large_range_share"] = tmp["entry_range_bps"] >= 250

        shares = tmp.groupby("time").agg(
            breadth_ret3_pos=("breadth_ret3_pos", "mean"),
            breadth_ret3_neg=("breadth_ret3_neg", "mean"),
            breadth_ret6_pos=("breadth_ret6_pos", "mean"),
            breadth_ret6_neg=("breadth_ret6_neg", "mean"),
            impulse_250_share=("impulse_250_share", "mean"),
            drop_250_share=("drop_250_share", "mean"),
            large_range_share=("large_range_share", "mean"),
        ).reset_index()

        time_features = time_features.merge(shares, on="time", how="left")
        q25_liq = float(time_features["mean_entry_vol_quote"].quantile(0.25))

        df = df.merge(time_features, on="time", how="left")

        rules: List[Dict[str, Any]] = []

        # 1) Relative weakness snapback long.
        for hold in [6, 12]:
            for coin_thr in [-100, -200, -300]:
                for mkt_min in [-100, -50, 0]:
                    for range_cap in [100, 150, 200]:
                        mask = (
                            (df["coin_ret3_bps"] <= coin_thr)
                            & (df["mkt_ret3_bps"] >= mkt_min)
                            & (df["entry_range_bps"] <= range_cap)
                            & (df["std_coin_ret3_bps"] <= 250)
                        )
                        rules.append({
                            "archetype_key": "relative_weakness_snapback_long",
                            "side": "long",
                            "hold_hours": hold,
                            "params": {
                                "coin_ret3_bps_max": coin_thr,
                                "mkt_ret3_bps_min": mkt_min,
                                "entry_range_bps_max": range_cap,
                                "std_coin_ret3_bps_max": 250,
                            },
                            "mask": mask,
                        })

        # 2) Panic rebound with strict regime guard.
        for hold in [6, 12]:
            for mkt6_max in [-100, -200, -300]:
                for breadth_pos_max in [0.35, 0.45]:
                    for coin_ret6_max in [-100, -200]:
                        mask = (
                            (df["mkt_ret6_bps"] <= mkt6_max)
                            & (df["coin_ret6_bps"] <= coin_ret6_max)
                            & (df["breadth_ret3_pos"] <= breadth_pos_max)
                            & (df["mean_entry_vol_quote"] > q25_liq)
                        )
                        rules.append({
                            "archetype_key": "panic_rebound_with_strict_regime_guard",
                            "side": "long",
                            "hold_hours": hold,
                            "params": {
                                "mkt_ret6_bps_max": mkt6_max,
                                "coin_ret6_bps_max": coin_ret6_max,
                                "breadth_ret3_pos_max": breadth_pos_max,
                                "mean_entry_vol_quote_gt_q25": True,
                            },
                            "mask": mask,
                        })

        # 3) Failed breakout reversion short.
        for hold in [3, 6, 12]:
            for coin_thr in [250, 350, 500]:
                for mkt_max in [-50, 0, 50]:
                    for range_min in [100, 150, 200]:
                        mask = (
                            (df["coin_ret3_bps"] >= coin_thr)
                            & (df["mkt_ret3_bps"] <= mkt_max)
                            & (df["entry_range_bps"] >= range_min)
                            & (df["breadth_ret3_pos"] <= 0.60)
                        )
                        rules.append({
                            "archetype_key": "failed_breakout_reversion_short",
                            "side": "short",
                            "hold_hours": hold,
                            "params": {
                                "coin_ret3_bps_min": coin_thr,
                                "mkt_ret3_bps_max": mkt_max,
                                "entry_range_bps_min": range_min,
                                "breadth_ret3_pos_max": 0.60,
                            },
                            "mask": mask,
                        })

        # 4) Market relative continuation short.
        for hold in [6, 12]:
            for coin_max in [-100, -200, -300]:
                for mkt_max in [-50, 0]:
                    for breadth_neg_min in [0.45, 0.55]:
                        mask = (
                            (df["coin_ret3_bps"] <= coin_max)
                            & (df["mkt_ret3_bps"] <= mkt_max)
                            & (df["breadth_ret3_neg"] >= breadth_neg_min)
                            & (df["entry_vol_quote"] > 0)
                        )
                        rules.append({
                            "archetype_key": "market_relative_continuation_short",
                            "side": "short",
                            "hold_hours": hold,
                            "params": {
                                "coin_ret3_bps_max": coin_max,
                                "mkt_ret3_bps_max": mkt_max,
                                "breadth_ret3_neg_min": breadth_neg_min,
                            },
                            "mask": mask,
                        })

        # 5) Liquidity shock mean reversion.
        for hold in [3, 6, 12]:
            for range_min in [200, 300, 400]:
                for coin_abs in [200, 350, 500]:
                    mask_long = (
                        (df["entry_range_bps"] >= range_min)
                        & (df["coin_ret3_bps"] <= -coin_abs)
                        & (df["mean_entry_vol_quote"] > q25_liq)
                    )
                    rules.append({
                        "archetype_key": "liquidity_shock_mean_reversion_long",
                        "side": "long",
                        "hold_hours": hold,
                        "params": {
                            "entry_range_bps_min": range_min,
                            "coin_ret3_bps_max": -coin_abs,
                            "mean_entry_vol_quote_gt_q25": True,
                        },
                        "mask": mask_long,
                    })

                    mask_short = (
                        (df["entry_range_bps"] >= range_min)
                        & (df["coin_ret3_bps"] >= coin_abs)
                        & (df["mean_entry_vol_quote"] > q25_liq)
                    )
                    rules.append({
                        "archetype_key": "liquidity_shock_mean_reversion_short",
                        "side": "short",
                        "hold_hours": hold,
                        "params": {
                            "entry_range_bps_min": range_min,
                            "coin_ret3_bps_min": coin_abs,
                            "mean_entry_vol_quote_gt_q25": True,
                        },
                        "mask": mask_short,
                    })

        # 6) Breadth extreme reversal.
        for hold in [6, 12]:
            for breadth_neg_min in [0.60, 0.70]:
                for coin_max in [-100, -200]:
                    mask = (
                        (df["breadth_ret3_neg"] >= breadth_neg_min)
                        & (df["coin_ret3_bps"] <= coin_max)
                        & (df["mean_entry_vol_quote"] > q25_liq)
                    )
                    rules.append({
                        "archetype_key": "breadth_extreme_reversal_long",
                        "side": "long",
                        "hold_hours": hold,
                        "params": {
                            "breadth_ret3_neg_min": breadth_neg_min,
                            "coin_ret3_bps_max": coin_max,
                            "mean_entry_vol_quote_gt_q25": True,
                        },
                        "mask": mask,
                    })

                for coin_min in [100, 200]:
                    mask = (
                        (df["breadth_ret3_pos"] >= 0.60)
                        & (df["coin_ret3_bps"] >= coin_min)
                        & (df["mean_entry_vol_quote"] > q25_liq)
                    )
                    rules.append({
                        "archetype_key": "breadth_extreme_reversal_short",
                        "side": "short",
                        "hold_hours": hold,
                        "params": {
                            "breadth_ret3_pos_min": 0.60,
                            "coin_ret3_bps_min": coin_min,
                            "mean_entry_vol_quote_gt_q25": True,
                        },
                        "mask": mask,
                    })

        results = []
        for rule in rules:
            try:
                result = evaluate_rule(df, rule, blocked_hashes, strict_rule)
                results.append(result)
            except Exception as exc:
                attention.append(f"rule_failed:{rule.get('archetype_key')}:{exc}")

        results.sort(key=lambda x: x.get("scanner_score", 0), reverse=True)

        strict_month_passes = [r for r in results if r.get("strict_month_stability_pass") is True]
        full_preview_passes = [r for r in results if r.get("scanner_preview_all_checks_pass") is True]
        blocked_hash_hits = [r for r in results if r.get("route_hash_blocked") is True]

        scoreboard_path = RUN_DIR / "strict_month_stable_archetype_scoreboard.json"
        scoreboard_csv_path = RUN_DIR / "strict_month_stable_archetype_scoreboard.csv"

        dump_json(scoreboard_path, {"scoreboard": results[:500]})

        flat_rows = []
        for r in results:
            flat_rows.append({
                "scanner_score": r.get("scanner_score"),
                "archetype_key": r.get("archetype_key"),
                "side": r.get("side"),
                "hold_hours": r.get("hold_hours"),
                "route_hash": r.get("route_hash"),
                "route_hash_blocked": r.get("route_hash_blocked"),
                "strict_month_stability_pass": r.get("strict_month_stability_pass"),
                "preview_all_checks_pass": r.get("scanner_preview_all_checks_pass"),
                "trade_count": safe_get(r, ["all", "trade_count"]),
                "symbol_count": safe_get(r, ["all", "symbol_count"]),
                "month_count": safe_get(r, ["all", "month_count"]),
                "positive_month_count": safe_get(r, ["all", "positive_month_count"]),
                "positive_month_rate": safe_get(r, ["all", "positive_month_rate"]),
                "total_net_bps": safe_get(r, ["all", "total_net_bps"]),
                "mean_net_bps": safe_get(r, ["all", "mean_net_bps"]),
                "win_rate": safe_get(r, ["all", "win_rate"]),
                "profit_factor": safe_get(r, ["all", "profit_factor"]),
                "train_pf": safe_get(r, ["train", "profit_factor"]),
                "oos_pf": safe_get(r, ["oos", "profit_factor"]),
                "failed_checks": ",".join(r.get("failed_checks") or []),
            })

        pd.DataFrame(flat_rows).to_csv(scoreboard_csv_path, index=False)

        scanner_status = "STRICT_MONTH_STABLE_ARCHETYPE_SCANNER_COMPLETE"
        severity = "ATTENTION"
        allowed_scope = "OFFLINE_RESEARCH_ONLY"

        if full_preview_passes:
            next_action = "EVALUATE_STRICT_MONTH_STABLE_ARCHETYPE_SCOREBOARD"
            reason = f"rules_tested={len(results)}; full_preview_pass_count={len(full_preview_passes)}; strict_month_pass_count={len(strict_month_passes)}"
        elif strict_month_passes:
            next_action = "EVALUATE_STRICT_MONTH_PASSING_ARCHETYPES_WITH_FAILED_OTHER_CHECKS"
            reason = f"rules_tested={len(results)}; strict_month_pass_count={len(strict_month_passes)}; full_preview_pass_count=0"
        else:
            next_action = "RECORD_NO_STRICT_MONTH_STABLE_ARCHETYPE_FOUND_OR_EXPAND_SEARCH_SPACE"
            reason = f"rules_tested={len(results)}; strict_month_pass_count=0; full_preview_pass_count=0"

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),

            "scanner_status": scanner_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,

            "contract_source": str(CONTRACT_LATEST),
            "contract_id": contract.get("contract_id"),
            "contract_hash": contract.get("contract_hash"),
            "research_key": contract.get("research_key"),

            "panel_path": str(panel),
            "panel_rows": int(len(df)),
            "panel_symbol_count": int(df["symbol"].nunique()),
            "panel_start": str(df["time"].min()),
            "panel_end": str(df["time"].max()),

            "strict_month_policy": strict_rule,
            "blocked_route_hashes": sorted(blocked_hashes),

            "rules_tested": len(results),
            "strict_month_pass_count": len(strict_month_passes),
            "full_preview_pass_count": len(full_preview_passes),
            "blocked_hash_hit_count": len(blocked_hash_hits),

            "top_scoreboard": results[:30],
            "top_strict_month_passes": strict_month_passes[:20],
            "top_full_preview_passes": full_preview_passes[:20],
            "blocked_hash_hits": blocked_hash_hits[:20],

            "outputs": {
                "scoreboard_json": str(scoreboard_path),
                "scoreboard_csv": str(scoreboard_csv_path),
            },

            "release_gate_feed": {
                "STRICT_MONTH_STABLE_ARCHETYPE_SCANNER_RAN": True,
                "STRICT_MONTH_STABLE_ARCHETYPE_FOUND": bool(strict_month_passes),
                "FULL_PREVIEW_PASS_ARCHETYPE_FOUND": bool(full_preview_passes),
                "RELEASE_PASS_FROM_THIS_SCANNER": False,
                "status": scanner_status,
            },

            "decision": {
                "candidate_generation_recommended_now": False,
                "candidate_contract_recommended_preview": bool(full_preview_passes),
                "family_release_recommended": False,
                "promotion_recommended": False,
                "runtime_change_recommended": False,
                "capital_change_recommended": False,
                "repeat_blocked_routes_recommended": False,
                "next_module": "edge_factory_os_strict_month_stable_archetype_evaluator_v1.py",
                "why_no_action": [
                    "scanner_only",
                    "candidate_contract_required_before any candidate generation",
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

    out_json = RUN_DIR / "strict_month_stable_archetype_scanner_v1_state.json"
    out_md = RUN_DIR / "strict_month_stable_archetype_scanner_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS STRICT MONTH STABLE ARCHETYPE SCANNER v1

scanner_status: {result.get("scanner_status")}  
severity: {result.get("severity")}  
allowed_scope: {result.get("allowed_scope")}  
next_action: {result.get("next_action")}  
reason: {result.get("reason")}

contract_id: {result.get("contract_id")}  
research_key: {result.get("research_key")}  
panel_path: {result.get("panel_path")}  
panel_rows: {result.get("panel_rows")}  
panel_symbol_count: {result.get("panel_symbol_count")}

## Strict Month Policy

{json.dumps(result.get("strict_month_policy"), indent=2, default=str)}

rules_tested: {result.get("rules_tested")}  
strict_month_pass_count: {result.get("strict_month_pass_count")}  
full_preview_pass_count: {result.get("full_preview_pass_count")}  
blocked_hash_hit_count: {result.get("blocked_hash_hit_count")}

## Top Scoreboard

{json.dumps(result.get("top_scoreboard"), indent=2, default=str)[:30000]}

## Top Strict Month Passes

{json.dumps(result.get("top_strict_month_passes"), indent=2, default=str)[:18000]}

## Top Full Preview Passes

{json.dumps(result.get("top_full_preview_passes"), indent=2, default=str)[:18000]}

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
    print("EDGE FACTORY OS STRICT MONTH STABLE ARCHETYPE SCANNER v1")
    print("=" * 100)
    print(f"scanner_status: {result.get('scanner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print()
    print("SUMMARY")
    print("-" * 100)
    print(f"rules_tested: {result.get('rules_tested')}")
    print(f"strict_month_pass_count: {result.get('strict_month_pass_count')}")
    print(f"full_preview_pass_count: {result.get('full_preview_pass_count')}")
    print(f"blocked_hash_hit_count: {result.get('blocked_hash_hit_count')}")
    print()
    print("TOP SCOREBOARD")
    print("-" * 100)
    for row in (result.get("top_scoreboard") or [])[:10]:
        print({
            "score": row.get("scanner_score"),
            "archetype": row.get("archetype_key"),
            "side": row.get("side"),
            "hold": row.get("hold_hours"),
            "route_hash": row.get("route_hash"),
            "strict_month_pass": row.get("strict_month_stability_pass"),
            "preview_all_checks_pass": row.get("scanner_preview_all_checks_pass"),
            "trade_count": safe_get(row, ["all", "trade_count"]),
            "month_count": safe_get(row, ["all", "month_count"]),
            "positive_month_count": safe_get(row, ["all", "positive_month_count"]),
            "positive_month_rate": safe_get(row, ["all", "positive_month_rate"]),
            "mean_net_bps": safe_get(row, ["all", "mean_net_bps"]),
            "pf": safe_get(row, ["all", "profit_factor"]),
            "failed": row.get("failed_checks"),
        })
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
