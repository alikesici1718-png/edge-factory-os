from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_month_first_feature_discovery_runner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

CONTRACT_LATEST = (
    BASE_DIR
    / "edge_factory_os_research_direction_contracts"
    / "month_first_feature_discovery_contract_latest.json"
)

STRICT_POLICY_LATEST = (
    BASE_DIR
    / "edge_factory_os_policy_guards"
    / "strict_month_stability_policy_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"month_first_feature_discovery_runner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "month_first_feature_discovery_runner_latest.json"
LATEST_MD = OUT_ROOT / "month_first_feature_discovery_runner_latest.md"

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


def rank_feature_against_label(month_df, feature: str, label: str) -> Dict[str, Any]:
    import numpy as np

    clean = month_df[[feature, label]].dropna().copy()

    if len(clean) < 8:
        return {
            "feature": feature,
            "label": label,
            "available": False,
            "reason": "not_enough_month_rows",
        }

    qs = [0.25, 0.33, 0.50, 0.67, 0.75]
    tests = []

    for q in qs:
        try:
            threshold = float(clean[feature].quantile(q))
        except Exception:
            continue

        for direction in [">=", "<="]:
            if direction == ">=":
                selected = clean[clean[feature] >= threshold]
                excluded = clean[clean[feature] < threshold]
            else:
                selected = clean[clean[feature] <= threshold]
                excluded = clean[clean[feature] > threshold]

            if len(selected) < 3 or len(excluded) < 3:
                continue

            selected_mean = float(selected[label].mean())
            excluded_mean = float(excluded[label].mean())
            selected_positive_rate = float((selected[label] > 0).mean())
            excluded_positive_rate = float((excluded[label] > 0).mean())

            score = abs(selected_mean - excluded_mean) + abs(selected_positive_rate - excluded_positive_rate) * 100.0

            tests.append({
                "feature": feature,
                "label": label,
                "threshold": threshold,
                "direction": direction,
                "selected_month_count": int(len(selected)),
                "excluded_month_count": int(len(excluded)),
                "selected_mean_label": selected_mean,
                "excluded_mean_label": excluded_mean,
                "selected_positive_month_rate": selected_positive_rate,
                "excluded_positive_month_rate": excluded_positive_rate,
                "separation_score": score,
            })

    tests.sort(key=lambda x: x["separation_score"], reverse=True)

    return {
        "feature": feature,
        "label": label,
        "available": True,
        "best_test": tests[0] if tests else None,
        "top_tests": tests[:10],
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    contract = load_json(CONTRACT_LATEST)
    strict_policy = load_json(STRICT_POLICY_LATEST)

    if not isinstance(contract, dict):
        critical.append("month_first_feature_discovery_contract_latest_missing")
        contract = {}

    if not isinstance(strict_policy, dict):
        attention.append("strict_month_policy_latest_missing")
        strict_policy = {}

    if contract.get("research_key") != "MONTH_FIRST_FEATURE_DISCOVERY_V1":
        critical.append(f"unexpected_contract_key:{contract.get('research_key')}")

    if safe_get(contract, ["expected_next_module", "candidate_generation_allowed_after_contract"]) is not False:
        critical.append("contract_allows_candidate_generation_unexpectedly")

    if safe_get(contract, ["expected_next_module", "family_release_allowed_after_contract"]) is not False:
        critical.append("contract_allows_family_release_unexpectedly")

    panel_path = safe_get(contract, ["universe_input", "panel_path"])

    if not panel_path:
        critical.append("panel_path_missing_from_contract")

    panel = Path(str(panel_path)) if panel_path else None

    if panel is None or not panel.exists():
        critical.append(f"panel_not_found:{panel_path}")

    if critical:
        runner_status = "MONTH_FIRST_FEATURE_DISCOVERY_RUNNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_CONTRACT_OR_PANEL_INPUT"
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

        dump_json(RUN_DIR / "month_first_feature_discovery_runner_v1_state.json", result)
        dump_json(LATEST_JSON, result)

        print("=" * 100)
        print("EDGE FACTORY OS MONTH FIRST FEATURE DISCOVERY RUNNER v1")
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
        runner_status = "MONTH_FIRST_FEATURE_DISCOVERY_RUNNER_CRITICAL_BLOCKED"
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

        # Diagnostic outcome labels only. These are NOT live features.
        for hold in [3, 6, 12, 24]:
            future_col = f"future_close_{hold}h"
            gross_col = f"gross_long_{hold}h_bps"
            net_long = f"diag_label_long_net_{hold}h_bps"
            net_short = f"diag_label_short_net_{hold}h_bps"

            df[future_col] = df.groupby("symbol")["close"].shift(-hold)
            df[gross_col] = ((df[future_col] / df["close"]) - 1.0) * 10000.0
            df[net_long] = df[gross_col] - COST_BPS_TOTAL
            df[net_short] = (-df[gross_col]) - COST_BPS_TOTAL

        # Timestamp-level pre-outcome features.
        time_features = df.groupby("time").agg(
            symbol_count=("symbol", "nunique"),
            mean_coin_ret3_bps=("coin_ret3_bps", "mean"),
            median_coin_ret3_bps=("coin_ret3_bps", "median"),
            std_coin_ret3_bps=("coin_ret3_bps", "std"),
            mean_coin_ret6_bps=("coin_ret6_bps", "mean"),
            median_coin_ret6_bps=("coin_ret6_bps", "median"),
            std_coin_ret6_bps=("coin_ret6_bps", "std"),
            mean_mkt_ret3_bps=("mkt_ret3_bps", "mean"),
            mean_mkt_ret6_bps=("mkt_ret6_bps", "mean"),
            mean_entry_range_bps=("entry_range_bps", "mean"),
            median_entry_range_bps=("entry_range_bps", "median"),
            std_entry_range_bps=("entry_range_bps", "std"),
            mean_entry_vol_quote=("entry_vol_quote", "mean"),
            median_entry_vol_quote=("entry_vol_quote", "median"),
            std_entry_vol_quote=("entry_vol_quote", "std"),
        ).reset_index()

        tmp = df[["time", "coin_ret3_bps", "coin_ret6_bps", "entry_range_bps", "entry_vol_quote"]].copy()
        tmp["breadth_ret3_pos"] = tmp["coin_ret3_bps"] > 0
        tmp["breadth_ret3_neg"] = tmp["coin_ret3_bps"] < 0
        tmp["breadth_ret6_pos"] = tmp["coin_ret6_bps"] > 0
        tmp["breadth_ret6_neg"] = tmp["coin_ret6_bps"] < 0
        tmp["impulse_250_share"] = tmp["coin_ret3_bps"] >= 250
        tmp["impulse_350_share"] = tmp["coin_ret3_bps"] >= 350
        tmp["drop_250_share"] = tmp["coin_ret3_bps"] <= -250
        tmp["drop_350_share"] = tmp["coin_ret3_bps"] <= -350
        tmp["large_range_200_share"] = tmp["entry_range_bps"] >= 200
        tmp["large_range_300_share"] = tmp["entry_range_bps"] >= 300
        tmp["low_liq_share"] = tmp["entry_vol_quote"] <= tmp["entry_vol_quote"].quantile(0.25)

        shares = tmp.groupby("time").agg(
            breadth_ret3_pos=("breadth_ret3_pos", "mean"),
            breadth_ret3_neg=("breadth_ret3_neg", "mean"),
            breadth_ret6_pos=("breadth_ret6_pos", "mean"),
            breadth_ret6_neg=("breadth_ret6_neg", "mean"),
            impulse_250_share=("impulse_250_share", "mean"),
            impulse_350_share=("impulse_350_share", "mean"),
            drop_250_share=("drop_250_share", "mean"),
            drop_350_share=("drop_350_share", "mean"),
            large_range_200_share=("large_range_200_share", "mean"),
            large_range_300_share=("large_range_300_share", "mean"),
            low_liq_share=("low_liq_share", "mean"),
        ).reset_index()

        time_features = time_features.merge(shares, on="time", how="left")
        time_features["month"] = time_features["time"].dt.to_period("M").astype(str)

        # Month-level pre-outcome features.
        month_features = time_features.groupby("month").agg(
            bar_count=("time", "count"),
            avg_symbol_count=("symbol_count", "mean"),

            avg_mean_coin_ret3_bps=("mean_coin_ret3_bps", "mean"),
            avg_median_coin_ret3_bps=("median_coin_ret3_bps", "mean"),
            avg_std_coin_ret3_bps=("std_coin_ret3_bps", "mean"),

            avg_mean_coin_ret6_bps=("mean_coin_ret6_bps", "mean"),
            avg_median_coin_ret6_bps=("median_coin_ret6_bps", "mean"),
            avg_std_coin_ret6_bps=("std_coin_ret6_bps", "mean"),

            avg_mean_mkt_ret3_bps=("mean_mkt_ret3_bps", "mean"),
            avg_mean_mkt_ret6_bps=("mean_mkt_ret6_bps", "mean"),

            avg_entry_range_bps=("mean_entry_range_bps", "mean"),
            avg_median_entry_range_bps=("median_entry_range_bps", "mean"),
            avg_std_entry_range_bps=("std_entry_range_bps", "mean"),

            avg_entry_vol_quote=("mean_entry_vol_quote", "mean"),
            avg_median_entry_vol_quote=("median_entry_vol_quote", "mean"),
            avg_std_entry_vol_quote=("std_entry_vol_quote", "mean"),

            avg_breadth_ret3_pos=("breadth_ret3_pos", "mean"),
            avg_breadth_ret3_neg=("breadth_ret3_neg", "mean"),
            avg_breadth_ret6_pos=("breadth_ret6_pos", "mean"),
            avg_breadth_ret6_neg=("breadth_ret6_neg", "mean"),

            avg_impulse_250_share=("impulse_250_share", "mean"),
            avg_impulse_350_share=("impulse_350_share", "mean"),
            avg_drop_250_share=("drop_250_share", "mean"),
            avg_drop_350_share=("drop_350_share", "mean"),

            avg_large_range_200_share=("large_range_200_share", "mean"),
            avg_large_range_300_share=("large_range_300_share", "mean"),
            avg_low_liq_share=("low_liq_share", "mean"),
        ).reset_index()

        # Diagnostic labels aggregated per month.
        label_cols = []
        for hold in [3, 6, 12, 24]:
            for side in ["long", "short"]:
                col = f"diag_label_{side}_net_{hold}h_bps"
                label_cols.append(col)

        label_aggs = {}
        for col in label_cols:
            label_aggs[f"label_avg_{col}"] = (col, "mean")
            label_aggs[f"label_median_{col}"] = (col, "median")

        month_labels = df.groupby("month").agg(**label_aggs).reset_index()

        month_table = month_features.merge(month_labels, on="month", how="left")

        # Derived diagnostic labels: best broad side/hold per month.
        avg_label_cols = [c for c in month_table.columns if c.startswith("label_avg_diag_label_")]

        month_table["label_best_broad_avg_net_bps"] = month_table[avg_label_cols].max(axis=1)
        month_table["label_worst_broad_avg_net_bps"] = month_table[avg_label_cols].min(axis=1)

        def best_label_name(row):
            vals = row[avg_label_cols]
            if vals.isna().all():
                return None
            return vals.idxmax()

        month_table["label_best_broad_template"] = month_table.apply(best_label_name, axis=1)

        feature_cols = [
            c for c in month_table.columns
            if c not in ["month", "label_best_broad_template"]
            and not c.startswith("label_")
        ]

        discovery_labels = [
            "label_best_broad_avg_net_bps",
            "label_avg_diag_label_long_net_6h_bps",
            "label_avg_diag_label_long_net_12h_bps",
            "label_avg_diag_label_short_net_6h_bps",
            "label_avg_diag_label_short_net_12h_bps",
        ]

        feature_rankings = []
        for label in discovery_labels:
            if label not in month_table.columns:
                continue

            for feature in feature_cols:
                ranked = rank_feature_against_label(month_table, feature, label)
                if ranked.get("available") and ranked.get("best_test"):
                    feature_rankings.append(ranked)

        feature_rankings.sort(
            key=lambda x: safe_get(x, ["best_test", "separation_score"], 0.0),
            reverse=True,
        )

        # Month-level regime tags for readability.
        top_feature_candidates = []
        for row in feature_rankings[:30]:
            best = row.get("best_test") or {}
            top_feature_candidates.append({
                "feature": row.get("feature"),
                "label": row.get("label"),
                "threshold": best.get("threshold"),
                "direction": best.get("direction"),
                "selected_month_count": best.get("selected_month_count"),
                "selected_positive_month_rate": best.get("selected_positive_month_rate"),
                "selected_mean_label": best.get("selected_mean_label"),
                "excluded_mean_label": best.get("excluded_mean_label"),
                "separation_score": best.get("separation_score"),
            })

        month_table_path = RUN_DIR / "month_first_feature_table.csv"
        feature_rankings_path = RUN_DIR / "month_first_feature_rankings.json"

        month_table.to_csv(month_table_path, index=False)
        dump_json(feature_rankings_path, {"feature_rankings": feature_rankings[:500]})

        strict_min_active = int(safe_get(contract, ["strict_month_stability_policy", "min_active_months"], 12))
        strict_min_pos = int(safe_get(contract, ["strict_month_stability_policy", "min_positive_months"], 11))

        findings = []

        findings.append({
            "finding_id": "MFFD_F1_MONTH_FEATURE_TABLE_CREATED",
            "severity": "INFO",
            "claim": "Full-panel pre-outcome month-level feature table was created.",
            "evidence": {
                "month_count": int(len(month_table)),
                "feature_count": len(feature_cols),
                "label_count": len(discovery_labels),
                "month_table_path": str(month_table_path),
            },
        })

        if top_feature_candidates:
            findings.append({
                "finding_id": "MFFD_F2_TOP_PRE_OUTCOME_FEATURES_RANKED",
                "severity": "ATTENTION",
                "claim": "Pre-outcome month features were ranked against diagnostic outcome labels.",
                "evidence": {
                    "top_feature_candidates": top_feature_candidates[:10],
                },
                "interpretation": "These are feature-discovery hints only, not candidate filters or release evidence.",
            })
        else:
            findings.append({
                "finding_id": "MFFD_F2_NO_FEATURE_RANKINGS_AVAILABLE",
                "severity": "ATTENTION",
                "claim": "No feature rankings were generated.",
                "evidence": {
                    "feature_count": len(feature_cols),
                    "label_count": len(discovery_labels),
                },
            })

        runner_status = "MONTH_FIRST_FEATURE_DISCOVERY_RUNNER_COMPLETE"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_RESEARCH"
        next_action = "EVALUATE_MONTH_FIRST_FEATURE_DISCOVERY_RESULTS"
        reason = (
            f"month_count={len(month_table)}; "
            f"feature_count={len(feature_cols)}; "
            f"ranked_feature_count={len(feature_rankings)}"
        )

        result = {
            "module": MODULE,
            "created_at_utc": NOW.isoformat(),

            "runner_status": runner_status,
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

            "strict_month_policy": {
                "min_active_months": strict_min_active,
                "min_positive_months": strict_min_pos,
                "min_positive_month_rate": safe_get(contract, ["strict_month_stability_policy", "min_positive_month_rate"], 11 / 12),
            },

            "month_feature_table_summary": {
                "month_count": int(len(month_table)),
                "feature_count": len(feature_cols),
                "diagnostic_label_count": len(discovery_labels),
                "feature_columns": feature_cols,
                "diagnostic_label_columns": discovery_labels,
            },

            "top_feature_candidates": top_feature_candidates,
            "top_feature_rankings": feature_rankings[:50],

            "outputs": {
                "month_feature_table_csv": str(month_table_path),
                "feature_rankings_json": str(feature_rankings_path),
            },

            "findings": findings,

            "release_gate_feed": {
                "MONTH_FIRST_FEATURE_DISCOVERY_RAN": True,
                "MONTH_FEATURE_TABLE_CREATED": True,
                "FEATURE_RANKINGS_CREATED": bool(feature_rankings),
                "RELEASE_PASS_FROM_THIS_RUNNER": False,
                "status": runner_status,
            },

            "decision": {
                "candidate_generation_recommended_now": False,
                "candidate_contract_recommended_now": False,
                "family_release_recommended": False,
                "promotion_recommended": False,
                "runtime_change_recommended": False,
                "capital_change_recommended": False,
                "repeat_blocked_routes_recommended": False,
                "next_module": "edge_factory_os_month_first_feature_discovery_evaluator_v1.py",
                "why_no_action": [
                    "feature_discovery_only",
                    "diagnostic_labels_are_not_live_features",
                    "future_contract_required_before any candidate generation",
                    "strict_month_policy_required",
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

    out_json = RUN_DIR / "month_first_feature_discovery_runner_v1_state.json"
    out_md = RUN_DIR / "month_first_feature_discovery_runner_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS MONTH FIRST FEATURE DISCOVERY RUNNER v1

runner_status: {result.get("runner_status")}  
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

## Month Feature Table Summary

{json.dumps(result.get("month_feature_table_summary"), indent=2, default=str)[:12000]}

## Top Feature Candidates

{json.dumps(result.get("top_feature_candidates"), indent=2, default=str)[:18000]}

## Findings

{json.dumps(result.get("findings"), indent=2, default=str)}

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
    print("EDGE FACTORY OS MONTH FIRST FEATURE DISCOVERY RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print()
    print("MONTH FEATURE TABLE")
    print("-" * 100)
    print(json.dumps(result.get("month_feature_table_summary"), indent=2, default=str)[:5000])
    print()
    print("TOP FEATURE CANDIDATES")
    print("-" * 100)
    for row in (result.get("top_feature_candidates") or [])[:15]:
        print(row)
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
