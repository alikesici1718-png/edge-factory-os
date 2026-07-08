from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_month_regime_instability_diagnostic_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "research_direction_contract_latest.json"
)

FULL_UNIVERSE_EVAL_LATEST = (
    BASE_DIR
    / "edge_factory_os_full_universe_offline_backtest_evaluator_v1"
    / "full_universe_offline_backtest_evaluator_latest.json"
)

RELEASE_GATE_V4_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_candidate_release_gate_v4"
    / "family_candidate_release_gate_v4_latest.json"
)

LESSON_CHECKER_LATEST = (
    BASE_DIR
    / "edge_factory_os_lesson_memory_checker_v1"
    / "lesson_memory_checker_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"month_regime_instability_diagnostic_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "month_regime_instability_diagnostic_latest.json"
LATEST_MD = OUT_ROOT / "month_regime_instability_diagnostic_latest.md"

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
        return float(v)
    except Exception:
        return default


def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def finite_float(x: Any, default=None):
    try:
        y = float(x)
        if math.isfinite(y):
            return y
    except Exception:
        pass
    return default


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(CONTRACT_LATEST)
    full_eval = load_json(FULL_UNIVERSE_EVAL_LATEST)
    release_gate = load_json(RELEASE_GATE_V4_LATEST)
    lesson_checker = load_json(LESSON_CHECKER_LATEST)

    if contract is None:
        critical.append("research_direction_contract_latest_missing")
        contract = {}

    if full_eval is None:
        critical.append("full_universe_evaluator_latest_missing")
        full_eval = {}

    if release_gate is None:
        attention.append("release_gate_v4_latest_missing")
        release_gate = {}

    if lesson_checker is None:
        attention.append("lesson_checker_latest_missing")
        lesson_checker = {}

    research_key = safe_get(contract, ["research_direction", "research_key"])
    panel_path = safe_get(contract, ["universe_input", "panel_path"])
    repeat_same_route_allowed = safe_get(contract, ["blocked_route_guard", "repeat_same_route_allowed"])
    candidate_generation_allowed = safe_get(contract, ["candidate_generation_rules", "candidate_generation_allowed_from_this_contract"])

    if research_key != "RD1_MONTH_REGIME_INSTABILITY_FEATURES":
        critical.append(f"unexpected_research_key:{research_key}")

    if repeat_same_route_allowed is not False:
        critical.append("contract_does_not_block_same_route_repeat")

    if candidate_generation_allowed is not False:
        critical.append("contract_allows_candidate_generation_unexpectedly")

    if not panel_path:
        critical.append("panel_path_missing_from_contract")

    panel = Path(str(panel_path)) if panel_path else None

    if panel is None or not panel.exists():
        critical.append(f"panel_path_not_found:{panel_path}")

    best_candidate = full_eval.get("best_candidate") or {}
    best_params = best_candidate.get("params") or {}

    threshold = best_params.get("threshold_coin_ret3_bps")
    hold_hours = best_params.get("hold_hours")
    entry_range_cap = best_params.get("entry_range_cap_bps")
    mkt_filter = best_params.get("mkt_filter") or {}

    threshold = int(threshold or 350)
    hold_hours = int(hold_hours or 12)

    if critical:
        diagnostic_status = "MONTH_REGIME_INSTABILITY_DIAGNOSTIC_CRITICAL_BLOCKED"
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

        dump_json(RUN_DIR / "month_regime_instability_diagnostic_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS MONTH REGIME INSTABILITY DIAGNOSTIC v1")
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

    missing_cols = [c for c in required_cols if c not in df.columns]

    if missing_cols:
        critical.append(f"panel_missing_required_columns:{missing_cols}")

    if critical:
        diagnostic_status = "MONTH_REGIME_INSTABILITY_DIAGNOSTIC_CRITICAL_BLOCKED"
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

        # Cross-sectional timestamp-level market regime map.
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
            median_entry_range_bps=("entry_range_bps", "median"),
            mean_entry_range_bps=("entry_range_bps", "mean"),
            mean_entry_vol_quote=("entry_vol_quote", "mean"),
            median_entry_vol_quote=("entry_vol_quote", "median"),
        ).reset_index()

        # Breadth and shock shares.
        tmp = df[["time", "coin_ret3_bps", "coin_ret6_bps", "entry_range_bps", "entry_vol_quote"]].copy()
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

        month_features = time_features.groupby("month").agg(
            bar_count=("time", "count"),
            avg_symbol_count=("symbol_count", "mean"),
            avg_mean_coin_ret3_bps=("mean_coin_ret3_bps", "mean"),
            avg_median_coin_ret3_bps=("median_coin_ret3_bps", "mean"),
            avg_std_coin_ret3_bps=("std_coin_ret3_bps", "mean"),
            avg_mean_coin_ret6_bps=("mean_coin_ret6_bps", "mean"),
            avg_median_coin_ret6_bps=("median_coin_ret6_bps", "mean"),
            avg_mean_mkt_ret3_bps=("mean_mkt_ret3_bps", "mean"),
            avg_mean_mkt_ret6_bps=("mean_mkt_ret6_bps", "mean"),
            avg_entry_range_bps=("mean_entry_range_bps", "mean"),
            median_entry_range_bps=("median_entry_range_bps", "mean"),
            avg_entry_vol_quote=("mean_entry_vol_quote", "mean"),
            median_entry_vol_quote=("median_entry_vol_quote", "mean"),
            avg_breadth_ret3_pos=("breadth_ret3_pos", "mean"),
            avg_breadth_ret6_pos=("breadth_ret6_pos", "mean"),
            avg_impulse_250_share=("impulse_250_share", "mean"),
            avg_impulse_350_share=("impulse_350_share", "mean"),
            avg_large_range_share=("large_range_share", "mean"),
        ).reset_index()

        if len(route_df) > 0:
            route_month = route_df.groupby("month")[net_col].agg(["count", "sum", "mean", "median"]).reset_index()
            route_month = route_month.rename(columns={
                "count": "route_trade_count",
                "sum": "route_total_net_bps",
                "mean": "route_mean_net_bps",
                "median": "route_median_net_bps",
            })

            route_month_wr = route_df.assign(win=route_df[net_col] > 0).groupby("month")["win"].mean().reset_index()
            route_month_wr = route_month_wr.rename(columns={"win": "route_win_rate"})

            route_symbol_count = route_df.groupby("month")["symbol"].nunique().reset_index()
            route_symbol_count = route_symbol_count.rename(columns={"symbol": "route_symbol_count"})

            route_month = route_month.merge(route_month_wr, on="month", how="left")
            route_month = route_month.merge(route_symbol_count, on="month", how="left")
        else:
            route_month = pd.DataFrame(columns=[
                "month",
                "route_trade_count",
                "route_total_net_bps",
                "route_mean_net_bps",
                "route_median_net_bps",
                "route_win_rate",
                "route_symbol_count",
            ])

        month_table = month_features.merge(route_month, on="month", how="left")
        for c in ["route_trade_count", "route_total_net_bps", "route_mean_net_bps", "route_median_net_bps", "route_win_rate", "route_symbol_count"]:
            if c in month_table.columns:
                if c in ["route_trade_count", "route_symbol_count"]:
                    month_table[c] = month_table[c].fillna(0).astype(int)
                else:
                    month_table[c] = month_table[c].fillna(0.0)

        month_table["route_month_label"] = np.where(
            month_table["route_total_net_bps"] > 0,
            "GOOD_MONTH",
            np.where(month_table["route_total_net_bps"] < 0, "BAD_MONTH", "FLAT_OR_NO_ROUTE_MONTH"),
        )

        good_months = month_table[month_table["route_month_label"] == "GOOD_MONTH"].copy()
        bad_months = month_table[month_table["route_month_label"] == "BAD_MONTH"].copy()

        feature_cols = [
            "avg_mean_coin_ret3_bps",
            "avg_median_coin_ret3_bps",
            "avg_std_coin_ret3_bps",
            "avg_mean_coin_ret6_bps",
            "avg_median_coin_ret6_bps",
            "avg_mean_mkt_ret3_bps",
            "avg_mean_mkt_ret6_bps",
            "avg_entry_range_bps",
            "median_entry_range_bps",
            "avg_entry_vol_quote",
            "median_entry_vol_quote",
            "avg_breadth_ret3_pos",
            "avg_breadth_ret6_pos",
            "avg_impulse_250_share",
            "avg_impulse_350_share",
            "avg_large_range_share",
        ]

        feature_diff = []

        for col in feature_cols:
            good_mean = finite_float(good_months[col].mean()) if len(good_months) > 0 else None
            bad_mean = finite_float(bad_months[col].mean()) if len(bad_months) > 0 else None

            if good_mean is None or bad_mean is None:
                diff = None
                ratio = None
            else:
                diff = good_mean - bad_mean
                ratio = good_mean / bad_mean if bad_mean not in [0, None] else None

            feature_diff.append({
                "feature": col,
                "good_month_mean": good_mean,
                "bad_month_mean": bad_mean,
                "good_minus_bad": diff,
                "good_div_bad": ratio,
                "abs_diff_rank_key": abs(diff) if diff is not None else -1,
            })

        feature_diff.sort(key=lambda x: x["abs_diff_rank_key"], reverse=True)

        # Bucket diagnostics for non-candidate explanatory filters.
        explanatory_buckets = []

        bucket_specs = [
            ("avg_breadth_ret3_pos", [0.35, 0.45, 0.55, 0.65]),
            ("avg_std_coin_ret3_bps", [100, 150, 200, 250]),
            ("avg_entry_range_bps", [100, 150, 200, 250]),
            ("avg_impulse_250_share", [0.02, 0.05, 0.10, 0.15]),
            ("avg_mean_mkt_ret3_bps", [-50, 0, 50, 100]),
            ("avg_mean_mkt_ret6_bps", [-50, 0, 50, 100]),
        ]

        for feature, thresholds in bucket_specs:
            if feature not in month_table.columns:
                continue

            for thr in thresholds:
                subset_hi = month_table[month_table[feature] >= thr]
                subset_lo = month_table[month_table[feature] < thr]

                hi_total = finite_float(subset_hi["route_total_net_bps"].sum()) if len(subset_hi) else 0.0
                lo_total = finite_float(subset_lo["route_total_net_bps"].sum()) if len(subset_lo) else 0.0
                hi_pos_rate = finite_float((subset_hi["route_total_net_bps"] > 0).mean()) if len(subset_hi) else None
                lo_pos_rate = finite_float((subset_lo["route_total_net_bps"] > 0).mean()) if len(subset_lo) else None

                explanatory_buckets.append({
                    "feature": feature,
                    "threshold": thr,
                    "direction": ">=",
                    "hi_month_count": int(len(subset_hi)),
                    "lo_month_count": int(len(subset_lo)),
                    "hi_total_route_net_bps": hi_total,
                    "lo_total_route_net_bps": lo_total,
                    "hi_positive_month_rate": hi_pos_rate,
                    "lo_positive_month_rate": lo_pos_rate,
                    "diagnostic_score": (
                        abs((hi_pos_rate or 0) - (lo_pos_rate or 0)) * 100
                        + abs((hi_total or 0) - (lo_total or 0)) / 1000
                    ),
                })

        explanatory_buckets.sort(key=lambda x: x["diagnostic_score"], reverse=True)

        month_table_path = RUN_DIR / "month_regime_instability_month_table.csv"
        feature_diff_path = RUN_DIR / "month_regime_instability_feature_diff.json"
        explanatory_buckets_path = RUN_DIR / "month_regime_instability_explanatory_buckets.json"

        month_table.to_csv(month_table_path, index=False)
        dump_json(feature_diff_path, {"feature_diff": feature_diff})
        dump_json(explanatory_buckets_path, {"explanatory_buckets": explanatory_buckets})

        findings = []

        if len(bad_months) > 0:
            worst_month = bad_months.sort_values("route_total_net_bps", ascending=True).iloc[0].to_dict()
            findings.append({
                "finding_id": "MRD_F1_WORST_MONTH_IDENTIFIED",
                "severity": "INFO",
                "claim": "The blocked route has identifiable bad months in the full-universe panel.",
                "evidence": worst_month,
            })

        if feature_diff:
            top_feature = feature_diff[0]
            findings.append({
                "finding_id": "MRD_F2_TOP_GOOD_BAD_FEATURE_DIFFERENCE",
                "severity": "ATTENTION",
                "claim": "Good and bad months differ on at least one market/regime feature.",
                "evidence": top_feature,
                "note": "This is diagnostic only, not a release filter.",
            })

        if explanatory_buckets:
            top_bucket = explanatory_buckets[0]
            findings.append({
                "finding_id": "MRD_F3_TOP_EXPLANATORY_BUCKET",
                "severity": "ATTENTION",
                "claim": "A candidate explanatory feature bucket separates monthly outcomes.",
                "evidence": top_bucket,
                "note": "This cannot become a candidate without a new contract and full release gate.",
            })

        findings.append({
            "finding_id": "MRD_F4_BLOCKED_ROUTE_NOT_REOPENED",
            "severity": "CONTROL",
            "claim": "The diagnostic did not reopen or recommend the blocked route.",
            "evidence": {
                "blocked_route_hash": lesson_checker.get("route_hash"),
                "route_blocked_by_lesson_memory": lesson_checker.get("route_blocked_by_lesson_memory"),
                "repeat_same_route_allowed": repeat_same_route_allowed,
                "candidate_generation_allowed_from_this_contract": candidate_generation_allowed,
            },
        })

        diagnostic_status = "MONTH_REGIME_INSTABILITY_DIAGNOSTIC_COMPLETE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "EVALUATE_MONTH_REGIME_DIAGNOSTIC_AND_DECIDE_NEW_CONTRACT_OR_ARCHIVE"
        reason = (
            f"month_count={int(len(month_table))}; "
            f"good_months={int(len(good_months))}; "
            f"bad_months={int(len(bad_months))}; "
            f"route_trade_count={int(len(route_df))}"
        )

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),

            "diagnostic_status": diagnostic_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,

            "contract_source": str(CONTRACT_LATEST),
            "full_universe_eval_source": str(FULL_UNIVERSE_EVAL_LATEST),
            "release_gate_v4_source": str(RELEASE_GATE_V4_LATEST),
            "lesson_checker_source": str(LESSON_CHECKER_LATEST),

            "research_key": research_key,
            "contract_id": contract.get("contract_id"),
            "panel_path": str(panel),
            "panel_rows": int(len(df)),
            "panel_symbol_count": int(df["symbol"].nunique()),
            "panel_start": str(df["time"].min()),
            "panel_end": str(df["time"].max()),

            "blocked_route_reference": {
                "route_hash": lesson_checker.get("route_hash"),
                "route_blocked_by_lesson_memory": lesson_checker.get("route_blocked_by_lesson_memory"),
                "repeat_same_route_allowed": repeat_same_route_allowed,
                "candidate_generation_allowed_from_this_contract": candidate_generation_allowed,
            },

            "route_proxy_used_for_diagnostic_only": {
                "source_best_candidate_id": best_candidate.get("candidate_id"),
                "threshold_coin_ret3_bps": threshold,
                "hold_hours": hold_hours,
                "entry_range_cap_bps": entry_range_cap,
                "mkt_filter": mkt_filter,
                "cost_bps_total": COST_BPS_TOTAL,
                "route_trade_count": int(len(route_df)),
                "route_total_net_bps": finite_float(route_df[net_col].sum()) if len(route_df) else 0.0,
                "route_mean_net_bps": finite_float(route_df[net_col].mean()) if len(route_df) else None,
                "route_win_rate": finite_float((route_df[net_col] > 0).mean()) if len(route_df) else None,
            },

            "month_summary": {
                "month_count": int(len(month_table)),
                "good_month_count": int(len(good_months)),
                "bad_month_count": int(len(bad_months)),
                "flat_or_no_route_month_count": int((month_table["route_month_label"] == "FLAT_OR_NO_ROUTE_MONTH").sum()),
                "good_months": good_months[["month", "route_total_net_bps", "route_trade_count", "route_win_rate"]].to_dict("records"),
                "bad_months": bad_months[["month", "route_total_net_bps", "route_trade_count", "route_win_rate"]].to_dict("records"),
                "worst_months": month_table.sort_values("route_total_net_bps", ascending=True).head(5).to_dict("records"),
                "best_months": month_table.sort_values("route_total_net_bps", ascending=False).head(5).to_dict("records"),
            },

            "feature_diff_top_20": feature_diff[:20],
            "explanatory_buckets_top_20": explanatory_buckets[:20],

            "outputs": {
                "month_table_csv": str(month_table_path),
                "feature_diff_json": str(feature_diff_path),
                "explanatory_buckets_json": str(explanatory_buckets_path),
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
                    "feature_buckets_are_explanatory_not_release_filters",
                    "new_candidate_contract_required_before any candidate generation",
                    "release_gate_still_required",
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

    if critical:
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

    out_json = RUN_DIR / "month_regime_instability_diagnostic_v1_state.json"
    out_md = RUN_DIR / "month_regime_instability_diagnostic_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS MONTH REGIME INSTABILITY DIAGNOSTIC v1

diagnostic_status: {result.get("diagnostic_status")}  
severity: {result.get("severity")}  
allowed_scope: {result.get("allowed_scope")}  
next_action: {result.get("next_action")}  
reason: {result.get("reason")}

research_key: {result.get("research_key")}  
contract_id: {result.get("contract_id")}  
panel_path: {result.get("panel_path")}  
panel_rows: {result.get("panel_rows")}  
panel_symbol_count: {result.get("panel_symbol_count")}

## Blocked Route Reference

{json.dumps(result.get("blocked_route_reference"), indent=2, default=str)}

## Route Proxy Used For Diagnostic Only

{json.dumps(result.get("route_proxy_used_for_diagnostic_only"), indent=2, default=str)}

## Month Summary

{json.dumps(result.get("month_summary"), indent=2, default=str)[:16000]}

## Feature Diff Top 20

{json.dumps(result.get("feature_diff_top_20"), indent=2, default=str)}

## Explanatory Buckets Top 20

{json.dumps(result.get("explanatory_buckets_top_20"), indent=2, default=str)}

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
    print("EDGE FACTORY OS MONTH REGIME INSTABILITY DIAGNOSTIC v1")
    print("=" * 100)
    print(f"diagnostic_status: {result.get('diagnostic_status')}")
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
    print()
    print("BLOCKED ROUTE")
    print("-" * 100)
    print(result.get("blocked_route_reference"))
    print()
    print("ROUTE PROXY DIAGNOSTIC ONLY")
    print("-" * 100)
    print(result.get("route_proxy_used_for_diagnostic_only"))
    print()
    print("MONTH SUMMARY")
    print("-" * 100)
    ms = result.get("month_summary") or {}
    print(f"month_count: {ms.get('month_count')}")
    print(f"good_month_count: {ms.get('good_month_count')}")
    print(f"bad_month_count: {ms.get('bad_month_count')}")
    print("worst_months:")
    for row in (ms.get("worst_months") or [])[:5]:
        print(row)
    print("best_months:")
    for row in (ms.get("best_months") or [])[:5]:
        print(row)
    print()
    print("FEATURE DIFF TOP 10")
    print("-" * 100)
    for row in (result.get("feature_diff_top_20") or [])[:10]:
        print(row)
    print()
    print("EXPLANATORY BUCKETS TOP 10")
    print("-" * 100)
    for row in (result.get("explanatory_buckets_top_20") or [])[:10]:
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
