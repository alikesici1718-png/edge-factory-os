from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_full_universe_offline_backtest_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

UNIVERSE_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_universe_coverage_guard_v2"
    / "universe_coverage_guard_v2_latest.json"
)

RELEASE_GATE_V2_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_candidate_release_gate_v2"
    / "family_candidate_release_gate_v2_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"full_universe_offline_backtest_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "full_universe_offline_backtest_latest.json"
LATEST_MD = OUT_ROOT / "full_universe_offline_backtest_latest.md"

COST_BPS_TOTAL = 75.0

THRESHOLDS = [250, 300, 350, 400]
HOLD_HOURS = [3, 6, 12]
ENTRY_RANGE_CAPS = [None, 100, 250]
MKT_FILTERS = [
    {"name": "none", "mkt_ret3_min_bps": None, "mkt_ret6_min_bps": None},
    {"name": "mkt_ret3_ge_0", "mkt_ret3_min_bps": 0, "mkt_ret6_min_bps": None},
    {"name": "mkt_ret6_ge_0", "mkt_ret3_min_bps": None, "mkt_ret6_min_bps": 0},
]


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
        return float(v)
    except Exception:
        return default


def summarize_returns(df, ret_col: str) -> Dict[str, Any]:
    import numpy as np

    vals = df[ret_col].dropna()

    if len(vals) == 0:
        return {
            "trade_count": int(len(df)),
            "valid_return_count": 0,
            "win_rate": None,
            "mean_net_bps": None,
            "median_net_bps": None,
            "total_net_bps": None,
            "profit_factor": None,
            "best_net_bps": None,
            "worst_net_bps": None,
            "symbol_count": 0,
            "month_count": 0,
            "positive_month_rate": None,
        }

    wins = vals[vals > 0]
    losses = vals[vals < 0]

    pf = None
    if len(losses) > 0:
        loss_abs = abs(float(losses.sum()))
        if loss_abs > 0:
            pf = float(wins.sum()) / loss_abs
    elif len(wins) > 0:
        pf = 999.0

    month_stats = {}
    positive_month_rate = None

    if "month" in df.columns:
        month_sum = df.groupby("month")[ret_col].sum().dropna()
        month_stats = {str(k): float(v) for k, v in month_sum.items()}
        if len(month_sum) > 0:
            positive_month_rate = float((month_sum > 0).sum() / len(month_sum))

    symbol_count = int(df["symbol"].nunique()) if "symbol" in df.columns else 0

    return {
        "trade_count": int(len(df)),
        "valid_return_count": int(len(vals)),
        "win_count": int((vals > 0).sum()),
        "loss_count": int((vals < 0).sum()),
        "win_rate": float((vals > 0).mean()),
        "mean_net_bps": float(vals.mean()),
        "median_net_bps": float(vals.median()),
        "total_net_bps": float(vals.sum()),
        "profit_factor": pf,
        "best_net_bps": float(vals.max()),
        "worst_net_bps": float(vals.min()),
        "symbol_count": symbol_count,
        "month_count": int(len(month_stats)),
        "positive_month_rate": positive_month_rate,
        "monthly_total_net_bps": month_stats,
    }


def top_symbol_table(df, ret_col: str, limit: int = 15) -> Dict[str, Any]:
    if "symbol" not in df.columns or ret_col not in df.columns or len(df) == 0:
        return {
            "top_loss_symbols": [],
            "top_win_symbols": [],
        }

    grouped = df.groupby("symbol")[ret_col].agg(["count", "sum", "mean"]).reset_index()
    grouped = grouped.rename(columns={"count": "trade_count", "sum": "total_net_bps", "mean": "mean_net_bps"})

    losses = grouped.sort_values("total_net_bps", ascending=True).head(limit).to_dict("records")
    wins = grouped.sort_values("total_net_bps", ascending=False).head(limit).to_dict("records")

    return {
        "top_loss_symbols": losses,
        "top_win_symbols": wins,
    }


def split_oos(df, time_col: str = "time") -> Dict[str, Any]:
    if time_col not in df.columns or len(df) == 0:
        return {
            "train": df,
            "oos": df.iloc[0:0],
            "split_time": None,
        }

    sorted_times = df[time_col].dropna().sort_values()

    if len(sorted_times) == 0:
        return {
            "train": df,
            "oos": df.iloc[0:0],
            "split_time": None,
        }

    split_idx = int(len(sorted_times) * 0.70)
    split_idx = min(max(split_idx, 0), len(sorted_times) - 1)
    split_time = sorted_times.iloc[split_idx]

    return {
        "train": df[df[time_col] <= split_time],
        "oos": df[df[time_col] > split_time],
        "split_time": str(split_time),
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    universe = load_json(UNIVERSE_V2_LATEST)
    release_gate = load_json(RELEASE_GATE_V2_LATEST)

    if universe is None:
        critical.append("universe_guard_v2_latest_missing")
        universe = {}

    if release_gate is None:
        attention.append("release_gate_v2_latest_missing")
        release_gate = {}

    universe_status = universe.get("universe_status")
    universe_pass = universe_status == "UNIVERSE_COVERAGE_GUARD_V2_PASS_FULL_1Y_OKX_SWAP_PANEL_READY"

    panel_path = None
    best_manifest = universe.get("best_universe_manifest") or {}

    if isinstance(best_manifest, dict):
        panel_path = best_manifest.get("panel_path")

    if not universe_pass:
        critical.append(f"universe_guard_not_full_pass:{universe_status}")

    if not panel_path:
        critical.append("panel_path_missing_from_universe_guard")

    panel = Path(str(panel_path)) if panel_path else None

    if panel is None or not panel.exists():
        critical.append(f"panel_path_not_exists:{panel_path}")

    if critical:
        backtest_status = "FULL_UNIVERSE_OFFLINE_BACKTEST_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_UNIVERSE_PANEL_INPUT"
        reason = "; ".join(critical)

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),
            "backtest_status": backtest_status,
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

        dump_json(RUN_DIR / "full_universe_offline_backtest_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS FULL UNIVERSE OFFLINE BACKTEST v1")
        print("=" * 100)
        print(f"backtest_status: {backtest_status}")
        print(f"severity: {severity}")
        print(f"reason: {reason}")
        print(f"latest_json: {LATEST_JSON}")
        print("=" * 100)

        return 2

    import pandas as pd
    import numpy as np

    df = pd.read_parquet(panel)

    required_cols = ["time", "symbol", "close", "coin_ret3_bps", "entry_range_bps"]

    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        critical.append(f"missing_required_panel_columns:{missing}")

    if critical:
        backtest_status = "FULL_UNIVERSE_OFFLINE_BACKTEST_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_PANEL_COLUMNS"
        reason = "; ".join(critical)
    else:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        df = df.dropna(subset=["time", "symbol", "close"])
        df = df.sort_values(["symbol", "time"]).reset_index(drop=True)

        df["month"] = df["time"].dt.to_period("M").astype(str)

        for hold in HOLD_HOURS:
            future_col = f"future_close_{hold}h"
            gross_col = f"gross_ret_{hold}h_bps"
            net_col = f"net_ret_{hold}h_bps"

            df[future_col] = df.groupby("symbol")["close"].shift(-hold)
            df[gross_col] = ((df[future_col] / df["close"]) - 1.0) * 10000.0
            df[net_col] = df[gross_col] - COST_BPS_TOTAL

        all_results = []

        for threshold in THRESHOLDS:
            for hold in HOLD_HOURS:
                ret_col = f"net_ret_{hold}h_bps"

                for entry_cap in ENTRY_RANGE_CAPS:
                    for mkt_filter in MKT_FILTERS:
                        mask = df["coin_ret3_bps"] >= threshold

                        if entry_cap is not None:
                            mask = mask & (df["entry_range_bps"] <= entry_cap)

                        if mkt_filter.get("mkt_ret3_min_bps") is not None and "mkt_ret3_bps" in df.columns:
                            mask = mask & (df["mkt_ret3_bps"] >= float(mkt_filter["mkt_ret3_min_bps"]))

                        if mkt_filter.get("mkt_ret6_min_bps") is not None and "mkt_ret6_bps" in df.columns:
                            mask = mask & (df["mkt_ret6_bps"] >= float(mkt_filter["mkt_ret6_min_bps"]))

                        trades = df.loc[mask].dropna(subset=[ret_col]).copy()

                        split = split_oos(trades, "time")
                        train = split["train"]
                        oos = split["oos"]

                        summary_all = summarize_returns(trades, ret_col)
                        summary_train = summarize_returns(train, ret_col)
                        summary_oos = summarize_returns(oos, ret_col)
                        symbols = top_symbol_table(trades, ret_col)

                        result_row = {
                            "candidate_id": (
                                f"impulse_long_full_universe_ret3_ge_{threshold}"
                                f"_hold_{hold}h"
                                f"_range_{entry_cap if entry_cap is not None else 'none'}"
                                f"_{mkt_filter['name']}"
                            ),
                            "threshold_coin_ret3_bps": threshold,
                            "hold_hours": hold,
                            "entry_range_cap_bps": entry_cap,
                            "mkt_filter": mkt_filter,
                            "cost_bps_total": COST_BPS_TOTAL,
                            "split_time": split["split_time"],
                            "summary_all": summary_all,
                            "summary_train": summary_train,
                            "summary_oos": summary_oos,
                            "symbol_concentration": symbols,
                        }

                        all_results.append(result_row)

        ranked = sorted(
            all_results,
            key=lambda r: (
                r["summary_oos"].get("mean_net_bps") if r["summary_oos"].get("mean_net_bps") is not None else -999999,
                r["summary_oos"].get("profit_factor") if r["summary_oos"].get("profit_factor") is not None else -999999,
                r["summary_oos"].get("trade_count") or 0,
            ),
            reverse=True,
        )

        # Strict candidate-quality preview. This is not release approval.
        promising = []
        rejected = []

        for r in ranked:
            all_s = r["summary_all"]
            tr_s = r["summary_train"]
            oos_s = r["summary_oos"]

            trade_count = int(all_s.get("trade_count") or 0)
            oos_count = int(oos_s.get("trade_count") or 0)
            mean_oos = fnum(oos_s.get("mean_net_bps"), -999999)
            mean_train = fnum(tr_s.get("mean_net_bps"), -999999)
            pf_oos = fnum(oos_s.get("profit_factor"), 0)
            win_oos = fnum(oos_s.get("win_rate"), 0)
            pos_month = fnum(all_s.get("positive_month_rate"), 0)

            pass_preview = (
                trade_count >= 300
                and oos_count >= 75
                and mean_train > 0
                and mean_oos > 0
                and pf_oos is not None
                and pf_oos >= 1.10
                and win_oos is not None
                and win_oos >= 0.45
                and pos_month is not None
                and pos_month >= 0.55
            )

            x = dict(r)
            x["candidate_quality_preview_pass"] = bool(pass_preview)

            if pass_preview:
                promising.append(x)
            else:
                if len(rejected) < 20:
                    rejected.append(x)

        out_candidates_path = RUN_DIR / "full_universe_offline_backtest_ranked_candidates.json"
        dump_json(out_candidates_path, {"ranked": ranked[:200], "promising": promising[:50]})

        backtest_status = "FULL_UNIVERSE_OFFLINE_BACKTEST_COMPLETE"
        severity = "ATTENTION"
        allowed_scope = "OFFLINE_RESEARCH_ONLY"
        next_action = "EVALUATE_FULL_UNIVERSE_BACKTEST_FOR_RELEASE_GATE"
        reason = f"candidate_result_count={len(all_results)}; promising_preview_count={len(promising)}"

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),

            "backtest_status": backtest_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,

            "universe_guard_source": str(UNIVERSE_V2_LATEST),
            "release_gate_source": str(RELEASE_GATE_V2_LATEST),
            "panel_path": str(panel),
            "panel_rows": int(len(df)),
            "panel_symbol_count": int(df["symbol"].nunique()),
            "panel_start": str(df["time"].min()),
            "panel_end": str(df["time"].max()),

            "grid": {
                "thresholds": THRESHOLDS,
                "hold_hours": HOLD_HOURS,
                "entry_range_caps": ENTRY_RANGE_CAPS,
                "mkt_filters": MKT_FILTERS,
                "cost_bps_total": COST_BPS_TOTAL,
            },

            "candidate_result_count": len(all_results),
            "promising_preview_count": len(promising),
            "ranked_top_20": ranked[:20],
            "promising_preview_top_20": promising[:20],
            "rejected_preview_top_20": rejected[:20],
            "ranked_candidates_path": str(out_candidates_path),

            "release_gate_feed": {
                "FULL_UNIVERSE_OFFLINE_BACKTEST_RAN": True,
                "FULL_UNIVERSE_OFFLINE_BACKTEST_PASS_PREVIEW": bool(len(promising) > 0),
                "status": "FULL_UNIVERSE_OFFLINE_BACKTEST_COMPLETE",
                "release_allowed_from_this_test_alone": False,
                "note": "This runner produces full-universe evidence. A separate evaluator must decide pass/fail for release gate.",
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

    out_json = RUN_DIR / "full_universe_offline_backtest_v1_state.json"
    out_md = RUN_DIR / "full_universe_offline_backtest_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS FULL UNIVERSE OFFLINE BACKTEST v1

backtest_status: {result.get("backtest_status")}  
severity: {result.get("severity")}  
allowed_scope: {result.get("allowed_scope")}  
next_action: {result.get("next_action")}  
reason: {result.get("reason")}

panel_path: {result.get("panel_path")}  
panel_rows: {result.get("panel_rows")}  
panel_symbol_count: {result.get("panel_symbol_count")}  
panel_start: {result.get("panel_start")}  
panel_end: {result.get("panel_end")}

candidate_result_count: {result.get("candidate_result_count")}  
promising_preview_count: {result.get("promising_preview_count")}

## Ranked Top 20

{json.dumps(result.get("ranked_top_20"), indent=2, default=str)[:24000]}

## Promising Preview Top 20

{json.dumps(result.get("promising_preview_top_20"), indent=2, default=str)[:12000]}

## Release Gate Feed

{json.dumps(result.get("release_gate_feed"), indent=2, default=str)}

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
execution_performed: True

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS FULL UNIVERSE OFFLINE BACKTEST v1")
    print("=" * 100)
    print(f"backtest_status: {result.get('backtest_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print()
    print("PANEL")
    print("-" * 100)
    print(f"panel_path: {result.get('panel_path')}")
    print(f"panel_rows: {result.get('panel_rows')}")
    print(f"panel_symbol_count: {result.get('panel_symbol_count')}")
    print(f"panel_start: {result.get('panel_start')}")
    print(f"panel_end: {result.get('panel_end')}")
    print()
    print("RESULT SUMMARY")
    print("-" * 100)
    print(f"candidate_result_count: {result.get('candidate_result_count')}")
    print(f"promising_preview_count: {result.get('promising_preview_count')}")
    print()
    print("TOP RANKED CANDIDATES")
    print("-" * 100)
    for row in (result.get("ranked_top_20") or [])[:10]:
        print(row["candidate_id"])
        print(f"  all: {row['summary_all']}")
        print(f"  train: {row['summary_train']}")
        print(f"  oos: {row['summary_oos']}")
        print()
    print("RELEASE GATE FEED")
    print("-" * 100)
    print(result.get("release_gate_feed"))
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
    print("execution_performed: True")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if result.get("severity") != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
