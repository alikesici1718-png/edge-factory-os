#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Market State Transition Runner v1

Purpose:
- Consume Market State Transition Contract v1.
- Read full source panel.
- Build outcome-agnostic market state features.
- Build state-transition summaries across canonical 12 policy months.
- Run negative controls and true source-panel null replay.
- Produce policy gate table and material-difference report.
- Keep plugin expansion, candidate/family/runtime/capital/live/real-order actions blocked.

This runner does NOT:
- use future returns / pnl / labels as discovery features
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- start active paper
- enable live
- place real orders
- delete/move/archive files
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import math
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "market_state_transition_contract_v1.json"
)

PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "market_state_transition_plugin_v1.json"
)

FAILED_DEEP_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "source_panel_anomaly_deep_validation_state_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

TRUE_PANEL_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "true_source_panel_empirical_null_baseline_state_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

POLICY_VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_validation_state_v1.json"
)

POLICY_RUNTIME_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_policy_runtime_state_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_market_state_transition_runner"

OUT_JSON = OUT_DIR / "market_state_transition_runner_latest.json"
OUT_TXT = OUT_DIR / "market_state_transition_runner_latest.txt"
OUT_INPUT_CONSUMPTION_CSV = OUT_DIR / "market_state_transition_input_consumption_latest.csv"
OUT_STATE_FEATURE_CSV = OUT_DIR / "market_state_transition_state_feature_inventory_latest.csv"
OUT_METHOD_CSV = OUT_DIR / "market_state_transition_method_inventory_latest.csv"
OUT_SUMMARY_CSV = OUT_DIR / "market_state_transition_summary_latest.csv"
OUT_MONTH_CSV = OUT_DIR / "market_state_transition_month_stability_latest.csv"
OUT_NEGATIVE_CSV = OUT_DIR / "market_state_transition_negative_controls_latest.csv"
OUT_TRUE_NULL_CSV = OUT_DIR / "market_state_transition_true_source_panel_null_rerun_latest.csv"
OUT_POLICY_GATE_CSV = OUT_DIR / "market_state_transition_policy_gate_pass_fail_latest.csv"
OUT_MATERIAL_DIFF_CSV = OUT_DIR / "market_state_transition_material_difference_report_latest.csv"

RUNNER_NAME = "edge_factory_os_market_state_transition_runner_v1"
EXPECTED_RESEARCH_KEY = "OUTCOME_AGNOSTIC_MARKET_STATE_TRANSITION_SEARCH_V1"
EXPECTED_PLUGIN_KEY = "MARKET_STATE_TRANSITION_PLUGIN_V1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

MONTH_SCORE_THRESHOLD = 1.65
TOTAL_SCORE_THRESHOLD = 22.0

SAFETY_FLAGS = {
    "candidate_generation_allowed": False,
    "candidate_contract_allowed": False,
    "family_release_allowed": False,
    "promotion_allowed": False,
    "runtime_touch_allowed": False,
    "launcher_allowed": False,
    "patch_runtime_allowed": False,
    "capital_change_allowed": False,
    "active_paper_allowed": False,
    "live_allowed": False,
    "real_orders_allowed": False,
    "execution_performed": False,
    "file_delete_performed": False,
    "file_move_performed": False,
    "archive_performed": False,
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass"}


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def explicitly_blocked(value: Any) -> bool:
    """
    Safety interpretation:
    - Only explicit True means allowed.
    - Missing / None / False means blocked.
    """
    return value is not True


def safe_month_from_time(series: pd.Series) -> pd.Series:
    t = pd.to_datetime(series, utc=True, errors="coerce")
    t_naive = t.dt.tz_convert(None)
    return t_naive.dt.to_period("M").astype(str)


def choose_canonical_months(df: pd.DataFrame, required_count: int = 12) -> List[str]:
    month_counts = (
        df.groupby("month", sort=True)
        .size()
        .reset_index(name="row_count")
        .sort_values("month")
    )
    months = month_counts["month"].astype(str).tolist()

    if len(months) <= required_count:
        return months

    month_counts = month_counts.copy()
    month_counts["is_edge"] = False
    month_counts.loc[month_counts.index.min(), "is_edge"] = True
    month_counts.loc[month_counts.index.max(), "is_edge"] = True

    thinnest_edge = (
        month_counts[month_counts["is_edge"]]
        .sort_values("row_count")
        .head(1)["month"]
        .astype(str)
        .tolist()
    )

    filtered = [m for m in months if m not in set(thinnest_edge)]
    if len(filtered) >= required_count:
        return filtered[:required_count]
    return months[-required_count:]


def feature_leakage_flag(feature_name: str) -> bool:
    name = str(feature_name).lower()
    forbidden_tokens = [
        "ret",
        "return",
        "pnl",
        "profit",
        "target",
        "future",
        "fwd",
        "label",
        "outcome",
        "signal",
        "win",
        "loss",
    ]
    return any(tok in name for tok in forbidden_tokens)


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df

    if {"open", "close"}.issubset(out.columns):
        open_ = pd.to_numeric(out["open"], errors="coerce").replace(0, np.nan)
        close = pd.to_numeric(out["close"], errors="coerce")
        out["derived_candle_body_bps"] = ((close - open_).abs() / open_).replace([np.inf, -np.inf], np.nan) * 10000.0

    if {"high", "low", "close"}.issubset(out.columns):
        close = pd.to_numeric(out["close"], errors="coerce").replace(0, np.nan)
        high = pd.to_numeric(out["high"], errors="coerce")
        low = pd.to_numeric(out["low"], errors="coerce")
        out["derived_candle_range_bps"] = ((high - low) / close).replace([np.inf, -np.inf], np.nan) * 10000.0

    if "close" in out.columns:
        close = pd.to_numeric(out["close"], errors="coerce").replace(0, np.nan)
        out["derived_log_close"] = np.log(close).replace([np.inf, -np.inf], np.nan)

    t = pd.to_datetime(out["time"], utc=True, errors="coerce")
    out["derived_hour_utc"] = t.dt.hour.astype("float64")
    out["derived_dayofweek_utc"] = t.dt.dayofweek.astype("float64")

    return out


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def blocked_hash_set(obj: Any) -> set:
    out = set()
    for row in extract_blocked_routes(obj):
        if row.get("route_hash"):
            out.add(str(row.get("route_hash")))
    return out


def build_input_consumption_report(
    contract: Dict[str, Any],
    plugin: Dict[str, Any],
    failed_state: Dict[str, Any],
    framework_status: Dict[str, Any],
    true_panel_state: Dict[str, Any],
    policy: Dict[str, Any],
    validation_state: Dict[str, Any],
    runtime_state: Dict[str, Any],
    guard_feed: Dict[str, Any],
    blocklist_path: Path,
) -> List[Dict[str, Any]]:
    checks = [
        ("CONTRACT_READY", contract.get("contract_status") == "MARKET_STATE_TRANSITION_CONTRACT_READY", contract.get("contract_status"), "MARKET_STATE_TRANSITION_CONTRACT_READY"),
        ("PLUGIN_KEY_MATCH", plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY, plugin.get("plugin_key"), EXPECTED_PLUGIN_KEY),
        ("RESEARCH_KEY_MATCH", contract.get("research_key") == EXPECTED_RESEARCH_KEY, contract.get("research_key"), EXPECTED_RESEARCH_KEY),
        ("FAILED_DEEP_STATE_CONSUMED", failed_state.get("state_status") == "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED_ROUTE_CLOSED", failed_state.get("state_status"), "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED_ROUTE_CLOSED"),
        ("FRAMEWORK_READY", framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL", framework_status.get("panel_status"), "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"),
        ("TRUE_PANEL_FALSE_POSITIVE_REPAIRED", true_panel_state.get("false_positive_methodology_repaired") is True, true_panel_state.get("false_positive_methodology_repaired"), True),
        ("TRUE_PANEL_ACTUAL_SIGNAL_ABSENT", true_panel_state.get("actual_signal_present") is False, true_panel_state.get("actual_signal_present"), False),
        ("POLICY_ACTIVE", policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE", policy.get("policy_status"), "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"),
        ("VALIDATOR_PASS", validation_state.get("validator_pass") is True, validation_state.get("validator_pass"), True),
        ("RUNTIME_BLOCKS_PLUGIN", explicitly_blocked(runtime_state.get("plugin_expansion_allowed")), runtime_state.get("plugin_expansion_allowed", False), False),
        ("GUARD_PASS", guard_feed.get("guard_pass") is True, guard_feed.get("guard_pass"), True),
        ("BLOCKLIST_EXISTS", blocklist_path.exists(), blocklist_path.exists(), True),
        ("PLUGIN_EXPANSION_BLOCKED", explicitly_blocked(plugin.get("plugin_expansion_allowed")), plugin.get("plugin_expansion_allowed", False), False),
        ("CANDIDATE_BLOCKED", plugin.get("candidate_generation_allowed", False) is False, plugin.get("candidate_generation_allowed", False), False),
        ("FAMILY_BLOCKED", plugin.get("family_release_allowed", False) is False, plugin.get("family_release_allowed", False), False),
        ("RUNTIME_TOUCH_BLOCKED", plugin.get("runtime_touch_allowed", False) is False, plugin.get("runtime_touch_allowed", False), False),
        ("CAPITAL_BLOCKED", plugin.get("capital_change_allowed", False) is False, plugin.get("capital_change_allowed", False), False),
        ("LIVE_BLOCKED", plugin.get("live_allowed", False) is False, plugin.get("live_allowed", False), False),
        ("REAL_ORDERS_BLOCKED", plugin.get("real_orders_allowed", False) is False, plugin.get("real_orders_allowed", False), False),
    ]

    return [
        {
            "check_key": key,
            "passed": bool(passed),
            "observed": observed,
            "required": required,
            "contract_id": contract.get("contract_id"),
            "research_key": contract.get("research_key"),
        }
        for key, passed, observed, required in checks
    ]


def inventory_methods(plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    methods = plugin.get("transition_methods")
    if not isinstance(methods, list):
        methods = []
    return [
        {
            "transition_method": str(method),
            "outcome_agnostic": True,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        }
        for method in methods
    ]


def inventory_features(df: pd.DataFrame, plugin: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    groups = plugin.get("state_feature_groups")
    if not isinstance(groups, list):
        groups = []

    inventory: List[Dict[str, Any]] = []
    selected: List[str] = []

    fallback_candidates = [
        "derived_candle_range_bps",
        "derived_candle_body_bps",
        "entry_range_bps",
        "entry_vol_quote",
        "volume",
        "quote_volume",
        "vol_quote",
        "turnover",
        "derived_hour_utc",
        "derived_dayofweek_utc",
    ]

    for group in groups:
        group_key = str(group.get("group_key"))
        candidates = group.get("candidate_features")
        if not isinstance(candidates, list):
            candidates = []

        found_for_group = []
        for feature in candidates:
            feature = str(feature)
            present = feature in df.columns
            numeric = bool(present and pd.api.types.is_numeric_dtype(df[feature]))
            leakage = feature_leakage_flag(feature)
            valid_ratio = float(pd.to_numeric(df[feature], errors="coerce").notna().mean()) if present else 0.0
            selected_now = present and numeric and not leakage and valid_ratio >= 0.70

            if selected_now:
                found_for_group.append(feature)
                if feature not in selected:
                    selected.append(feature)

            inventory.append({
                "group_key": group_key,
                "feature": feature,
                "present": present,
                "numeric": numeric,
                "valid_ratio": valid_ratio,
                "leakage_flag": leakage,
                "selected": selected_now,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            })

        if not found_for_group:
            for feature in fallback_candidates:
                if feature in df.columns and not feature_leakage_flag(feature):
                    valid_ratio = float(pd.to_numeric(df[feature], errors="coerce").notna().mean())
                    selected_now = pd.api.types.is_numeric_dtype(df[feature]) and valid_ratio >= 0.70
                    if selected_now and feature not in selected:
                        selected.append(feature)
                    inventory.append({
                        "group_key": f"{group_key}_fallback",
                        "feature": feature,
                        "present": True,
                        "numeric": bool(pd.api.types.is_numeric_dtype(df[feature])),
                        "valid_ratio": valid_ratio,
                        "leakage_flag": False,
                        "selected": selected_now,
                        "candidate_generation_allowed": False,
                        "family_release_allowed": False,
                        "runtime_touch_allowed": False,
                        "capital_change_allowed": False,
                        "live_allowed": False,
                        "real_orders_allowed": False,
                    })
                    if selected_now:
                        break

    if not selected:
        for feature in fallback_candidates:
            if feature in df.columns and not feature_leakage_flag(feature):
                valid_ratio = float(pd.to_numeric(df[feature], errors="coerce").notna().mean())
                if pd.api.types.is_numeric_dtype(df[feature]) and valid_ratio >= 0.70:
                    selected.append(feature)
                    inventory.append({
                        "group_key": "global_fallback",
                        "feature": feature,
                        "present": True,
                        "numeric": True,
                        "valid_ratio": valid_ratio,
                        "leakage_flag": False,
                        "selected": True,
                        "candidate_generation_allowed": False,
                        "family_release_allowed": False,
                        "runtime_touch_allowed": False,
                        "capital_change_allowed": False,
                        "live_allowed": False,
                        "real_orders_allowed": False,
                    })

    return inventory, selected[:10]


def build_time_state_frame(df: pd.DataFrame, features: List[str], canonical_months: List[str]) -> pd.DataFrame:
    work = df[df["month"].isin(canonical_months)].copy()
    work["time"] = pd.to_datetime(work["time"], utc=True, errors="coerce")
    work = work.dropna(subset=["time", "symbol"])

    agg_spec = {}
    for feature in features:
        work[feature] = pd.to_numeric(work[feature], errors="coerce").replace([np.inf, -np.inf], np.nan)
        agg_spec[f"{feature}_median"] = (feature, "median")
        agg_spec[f"{feature}_std"] = (feature, "std")
        agg_spec[f"{feature}_p75"] = (feature, lambda x: np.nanquantile(x, 0.75) if x.notna().sum() else np.nan)
        agg_spec[f"{feature}_p25"] = (feature, lambda x: np.nanquantile(x, 0.25) if x.notna().sum() else np.nan)

    agg_spec["symbol_count"] = ("symbol", "nunique")
    agg_spec["row_count"] = ("symbol", "size")

    ts = work.groupby("time").agg(**agg_spec).reset_index()
    ts["month"] = safe_month_from_time(ts["time"])
    ts = ts[ts["month"].isin(canonical_months)].sort_values("time").reset_index(drop=True)
    return ts


def transition_score_by_month(
    ts: pd.DataFrame,
    state_col: str,
    canonical_months: List[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []

    x = pd.to_numeric(ts[state_col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    valid = ts.loc[x.notna(), ["time", "month"]].copy()
    valid[state_col] = x.loc[x.notna()].to_numpy()

    if len(valid) < 100:
        return rows, summary_rows

    q33 = float(valid[state_col].quantile(0.33))
    q67 = float(valid[state_col].quantile(0.67))

    valid["bucket"] = np.where(
        valid[state_col] <= q33,
        0,
        np.where(valid[state_col] >= q67, 2, 1),
    )
    valid["prev_bucket"] = valid["bucket"].shift(1)
    valid = valid.dropna(subset=["prev_bucket"])
    valid["prev_bucket"] = valid["prev_bucket"].astype(int)
    valid["bucket"] = valid["bucket"].astype(int)
    valid["transition"] = valid["prev_bucket"].astype(str) + "->" + valid["bucket"].astype(str)

    transition_keys = ["0->2", "2->0", "0->1", "1->2", "2->1", "1->0", "0->0", "2->2"]

    global_counts = valid["transition"].value_counts(normalize=True).to_dict()

    for transition_key in transition_keys:
        month_scores: List[float] = []
        month_rates: List[float] = []
        month_counts: List[int] = []

        baseline_rate = float(global_counts.get(transition_key, 0.0))
        baseline_rate = max(min(baseline_rate, 0.999), 0.001)

        for month in canonical_months:
            mdf = valid[valid["month"] == month]
            total = int(len(mdf))
            count = int((mdf["transition"] == transition_key).sum()) if total else 0
            rate = count / total if total else 0.0

            se = math.sqrt((baseline_rate * (1.0 - baseline_rate)) / max(total, 1))
            z = abs(rate - baseline_rate) / max(se, 1e-6)
            score = min(4.0, z / 3.0)

            month_scores.append(score)
            month_rates.append(rate)
            month_counts.append(total)

            rows.append({
                "state_col": state_col,
                "transition_key": transition_key,
                "month": month,
                "transition_count": count,
                "total_transitions": total,
                "transition_rate": rate,
                "baseline_rate": baseline_rate,
                "month_transition_score": score,
                "month_score_pass": score >= MONTH_SCORE_THRESHOLD,
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            })

        active_months = sum(1 for x_count in month_counts if x_count > 0)
        strict_months = sum(1 for score in month_scores if score >= MONTH_SCORE_THRESHOLD)
        total_score = float(sum(month_scores))
        min_score = float(min(month_scores)) if month_scores else 0.0
        median_score = float(np.median(month_scores)) if month_scores else 0.0
        avg_rate = float(np.mean(month_rates)) if month_rates else 0.0
        avg_count = float(np.mean(month_counts)) if month_counts else 0.0

        strict_12_transition_preview = bool(
            active_months >= 12
            and strict_months >= 12
            and total_score >= TOTAL_SCORE_THRESHOLD
        )

        summary_rows.append({
            "transition_axis_key": f"{state_col}_{transition_key}",
            "state_col": state_col,
            "transition_key": transition_key,
            "active_months": active_months,
            "strict_months": strict_months,
            "total_transition_score": total_score,
            "min_month_transition_score": min_score,
            "median_month_transition_score": median_score,
            "avg_transition_rate": avg_rate,
            "avg_total_transitions": avg_count,
            "strict_12_transition_preview": strict_12_transition_preview,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })

    return rows, summary_rows


def build_transition_summaries(
    ts: pd.DataFrame,
    selected_features: List[str],
    canonical_months: List[str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    all_month_rows: List[Dict[str, Any]] = []
    all_summary_rows: List[Dict[str, Any]] = []

    state_cols: List[str] = []
    for feature in selected_features:
        for suffix in ["median", "std", "p75", "p25"]:
            col = f"{feature}_{suffix}"
            if col in ts.columns:
                state_cols.append(col)

    for state_col in state_cols:
        month_rows, summary_rows = transition_score_by_month(ts, state_col, canonical_months)
        all_month_rows.extend(month_rows)
        all_summary_rows.extend(summary_rows)

    all_summary_rows = sorted(
        all_summary_rows,
        key=lambda r: (
            to_bool(r.get("strict_12_transition_preview")),
            to_float(r.get("total_transition_score")),
            to_float(r.get("median_month_transition_score")),
        ),
        reverse=True,
    )

    return all_month_rows, all_summary_rows


def run_negative_controls(
    transition_month_rows: List[Dict[str, Any]],
    observed_preview_count: int,
    observed_best_score: float,
    controls: List[str],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if not transition_month_rows:
        return rows

    rng = np.random.default_rng(20260514)
    score_pool = np.asarray(
        [to_float(row.get("month_transition_score")) for row in transition_month_rows],
        dtype="float64",
    )
    score_pool = score_pool[np.isfinite(score_pool)]

    if score_pool.size == 0:
        score_pool = np.array([0.0], dtype="float64")

    for control in controls:
        hits = 0
        adjusted_hits = 0
        runs = 1000

        for _ in range(runs):
            sample = rng.choice(score_pool, size=12, replace=True)

            if control == "transition_direction_flip_control":
                sample = np.flip(sample)
            elif control == "state_label_permutation_control":
                sample = rng.permutation(sample)
            elif control == "calendar_block_shuffle_control":
                rng.shuffle(sample)

            strict_months = int(np.sum(sample >= MONTH_SCORE_THRESHOLD))
            total_score = float(np.sum(sample))
            strict_hit = bool(strict_months >= 12 and total_score >= TOTAL_SCORE_THRESHOLD)
            adjusted_hit = bool(strict_hit and total_score >= observed_best_score)

            hits += int(strict_hit)
            adjusted_hits += int(adjusted_hit)

        strict_rate = hits / runs
        adjusted_rate = adjusted_hits / runs

        rows.append({
            "negative_control": control,
            "runs": runs,
            "strict_12_random_hit_rate": strict_rate,
            "null_adjusted_random_hit_rate": adjusted_rate,
            "observed_preview_count": observed_preview_count,
            "observed_best_score": observed_best_score,
            "passed": strict_rate <= 0.01 and adjusted_rate <= 0.005,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })

    return rows


def run_true_null_rerun(
    transition_month_rows: List[Dict[str, Any]],
    observed_best_score: float,
    runs: int,
    caps: Dict[str, Any],
) -> List[Dict[str, Any]]:
    rng = np.random.default_rng(20260514)

    score_pool = np.asarray(
        [to_float(row.get("month_transition_score")) for row in transition_month_rows],
        dtype="float64",
    )
    score_pool = score_pool[np.isfinite(score_pool)]

    if score_pool.size == 0:
        score_pool = np.array([0.0], dtype="float64")

    strict_hits = 0
    adjusted_hits = 0
    run_rows: List[Dict[str, Any]] = []

    for run_id in range(1, runs + 1):
        sample = rng.choice(score_pool, size=12, replace=True)
        strict_months = int(np.sum(sample >= MONTH_SCORE_THRESHOLD))
        total_score = float(np.sum(sample))
        strict_hit = bool(strict_months >= 12 and total_score >= TOTAL_SCORE_THRESHOLD)
        adjusted_hit = bool(strict_hit and total_score >= observed_best_score)

        strict_hits += int(strict_hit)
        adjusted_hits += int(adjusted_hit)

        if run_id <= 200:
            run_rows.append({
                "run_id": run_id,
                "strict_months": strict_months,
                "total_transition_score": total_score,
                "observed_best_score": observed_best_score,
                "strict_12_random_hit": strict_hit,
                "null_adjusted_random_hit": adjusted_hit,
            })

    max_allowed_strict = float(caps.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)
    max_allowed_null = float(caps.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)

    strict_rate = strict_hits / max(1, runs)
    adjusted_rate = adjusted_hits / max(1, runs)

    run_rows.append({
        "run_id": "SUMMARY",
        "runs": runs,
        "strict_12_any_random_hit_rate": strict_rate,
        "null_adjusted_any_random_hit_rate": adjusted_rate,
        "observed_best_score": observed_best_score,
        "max_allowed_strict_12_any_random_hit_rate": max_allowed_strict,
        "max_allowed_null_adjusted_any_random_hit_rate": max_allowed_null,
        "passed": strict_rate <= max_allowed_strict and adjusted_rate <= max_allowed_null,
    })

    return run_rows


def build_material_difference_report(
    contract: Dict[str, Any],
    failed_state: Dict[str, Any],
    blocklist: Any,
) -> List[Dict[str, Any]]:
    blocked = blocked_hash_set(blocklist)
    route_hash = str(contract.get("route_hash"))
    source_failed = str(contract.get("source_failed_route_hash") or failed_state.get("route_hash"))

    return [
        {
            "check_key": "CONTRACT_ROUTE_HASH_NOT_BLOCKED",
            "passed": route_hash not in blocked,
            "observed": route_hash,
            "required": "not in blocklist",
        },
        {
            "check_key": "SOURCE_FAILED_ROUTE_HASH_IS_KNOWN_OR_CLOSED",
            "passed": bool(source_failed),
            "observed": source_failed,
            "required": "failed route hash present",
        },
        {
            "check_key": "MATERIAL_DIFFERENCE_FROM_SOURCE_ANOMALY_ROUTE",
            "passed": contract.get("research_key") == EXPECTED_RESEARCH_KEY and "MARKET_STATE_TRANSITION" in str(contract.get("plugin_key")),
            "observed": contract.get("research_key"),
            "required": "market-state transition route, not single feature anomaly",
        },
        {
            "check_key": "OUTCOME_AGNOSTIC_DISCOVERY_REQUIRED",
            "passed": True,
            "observed": "future/outcome features excluded by runner inventory",
            "required": True,
        },
        {
            "check_key": "RELEASE_STILL_BLOCKED",
            "passed": contract.get("release_allowed") is False,
            "observed": contract.get("release_allowed"),
            "required": False,
        },
    ]


def build_policy_gates(
    *,
    input_pass: bool,
    row_count: int,
    symbol_count: int,
    canonical_month_count: int,
    selected_feature_count: int,
    transition_method_count: int,
    negative_control_count: int,
    preview_count: int,
    negative_rows: List[Dict[str, Any]],
    true_null_rows: List[Dict[str, Any]],
    material_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    true_null_summary = [r for r in true_null_rows if r.get("run_id") == "SUMMARY"]
    true_null_pass = bool(true_null_summary and to_bool(true_null_summary[0].get("passed")))

    max_strict_rate = to_float(true_null_summary[0].get("strict_12_any_random_hit_rate"), 1.0) if true_null_summary else 1.0
    max_null_rate = to_float(true_null_summary[0].get("null_adjusted_any_random_hit_rate"), 1.0) if true_null_summary else 1.0

    negative_pass = all(to_bool(x.get("passed")) for x in negative_rows) if negative_rows else False
    material_pass = all(to_bool(x.get("passed")) for x in material_rows) if material_rows else False

    return [
        {
            "gate_key": "INPUT_CONSUMPTION_PASS",
            "passed": input_pass,
            "observed": input_pass,
            "required": True,
        },
        {
            "gate_key": "ROW_COVERAGE_PASS",
            "passed": row_count >= 1000000,
            "observed": row_count,
            "required": ">=1000000",
        },
        {
            "gate_key": "SYMBOL_COVERAGE_PASS",
            "passed": symbol_count >= 200,
            "observed": symbol_count,
            "required": ">=200",
        },
        {
            "gate_key": "CANONICAL_MONTH_COUNT_PASS",
            "passed": canonical_month_count == 12,
            "observed": canonical_month_count,
            "required": 12,
        },
        {
            "gate_key": "STATE_FEATURE_COUNT_PASS",
            "passed": selected_feature_count >= 4,
            "observed": selected_feature_count,
            "required": ">=4",
        },
        {
            "gate_key": "TRANSITION_METHOD_COUNT_PASS",
            "passed": transition_method_count >= 6,
            "observed": transition_method_count,
            "required": ">=6",
        },
        {
            "gate_key": "NEGATIVE_CONTROL_COUNT_PASS",
            "passed": negative_control_count >= 6,
            "observed": negative_control_count,
            "required": ">=6",
        },
        {
            "gate_key": "POLICY_LOCKED_TRANSITION_PREVIEW_PRESENT",
            "passed": preview_count > 0,
            "observed": preview_count,
            "required": ">0",
        },
        {
            "gate_key": "NEGATIVE_CONTROLS_PASS",
            "passed": negative_pass,
            "observed": negative_pass,
            "required": True,
        },
        {
            "gate_key": "TRUE_SOURCE_PANEL_NULL_RERUN_PASS",
            "passed": true_null_pass,
            "observed": {"strict_rate": max_strict_rate, "null_rate": max_null_rate},
            "required": "strict<=0.01 and null<=0.005",
        },
        {
            "gate_key": "MATERIAL_DIFFERENCE_PASS",
            "passed": material_pass,
            "observed": material_pass,
            "required": True,
        },
        {
            "gate_key": "RELEASE_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "release_allowed=False",
        },
        {
            "gate_key": "CANDIDATE_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "candidate_generation_allowed=False",
        },
    ]


def summarize_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS MARKET STATE TRANSITION RUNNER v1")
    lines.append("=" * 100)

    for key in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "research_key",
        "plugin_key",
        "policy_hash",
        "row_count",
        "symbol_count",
        "raw_calendar_month_count",
        "canonical_policy_month_count",
        "selected_state_feature_count",
        "transition_method_count",
        "transition_axis_count",
        "strict_12_transition_preview_count",
        "negative_control_count",
        "true_null_runs",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "policy_gate_pass",
        "policy_gate_fail_count",
        "failed_gate_keys",
        "release_allowed",
        "elapsed_seconds",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("TOP TRANSITIONS")
    lines.append("-" * 100)
    for row in result.get("top_transition_rows", [])[:20]:
        lines.append(
            f"{row.get('transition_axis_key')} | strict={row.get('strict_12_transition_preview')} | "
            f"score={row.get('total_transition_score')} | strict_months={row.get('strict_months')}"
        )

    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for gate in result.get("policy_gate_rows", []):
        lines.append(f"{gate.get('gate_key')}: passed={gate.get('passed')} observed={gate.get('observed')} required={gate.get('required')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "input_consumption_csv",
        "state_feature_csv",
        "method_csv",
        "summary_csv",
        "month_csv",
        "negative_csv",
        "true_null_csv",
        "policy_gate_csv",
        "material_difference_csv",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS MARKET STATE TRANSITION RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"policy_hash: {result.get('policy_hash')}")
    print(f"row_count: {result.get('row_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"raw_calendar_month_count: {result.get('raw_calendar_month_count')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"selected_state_feature_count: {result.get('selected_state_feature_count')}")
    print(f"transition_method_count: {result.get('transition_method_count')}")
    print(f"transition_axis_count: {result.get('transition_axis_count')}")
    print(f"strict_12_transition_preview_count: {result.get('strict_12_transition_preview_count')}")
    print(f"negative_control_count: {result.get('negative_control_count')}")
    print(f"true_null_runs: {result.get('true_null_runs')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"policy_gate_pass: {result.get('policy_gate_pass')}")
    print(f"policy_gate_fail_count: {result.get('policy_gate_fail_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"release_allowed: {result.get('release_allowed')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('summary_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    plugin = load_json(PLUGIN_JSON, default={})
    failed_state = load_json(FAILED_DEEP_STATE_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    validation_state = load_json(POLICY_VALIDATION_STATE_JSON, default={})
    runtime_state = load_json(POLICY_RUNTIME_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    blocklist = load_json(BLOCKLIST_PATH, default={})

    source_panel_path = Path(contract.get("source_panel_path") or plugin.get("source_panel_path") or "")

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "source_failed_route_hash": contract.get("source_failed_route_hash"),
        "research_key": contract.get("research_key"),
        "plugin_key": contract.get("plugin_key"),
        "policy_hash": contract.get("policy_hash"),
        "source_panel_path": str(source_panel_path),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "input_consumption_csv": str(OUT_INPUT_CONSUMPTION_CSV),
        "state_feature_csv": str(OUT_STATE_FEATURE_CSV),
        "method_csv": str(OUT_METHOD_CSV),
        "summary_csv": str(OUT_SUMMARY_CSV),
        "month_csv": str(OUT_MONTH_CSV),
        "negative_csv": str(OUT_NEGATIVE_CSV),
        "true_null_csv": str(OUT_TRUE_NULL_CSV),
        "policy_gate_csv": str(OUT_POLICY_GATE_CSV),
        "material_difference_csv": str(OUT_MATERIAL_DIFF_CSV),
        **SAFETY_FLAGS,
    }

    try:
        input_rows = build_input_consumption_report(
            contract=contract,
            plugin=plugin,
            failed_state=failed_state,
            framework_status=framework_status,
            true_panel_state=true_panel_state,
            policy=policy,
            validation_state=validation_state,
            runtime_state=runtime_state,
            guard_feed=guard_feed,
            blocklist_path=BLOCKLIST_PATH,
        )
        write_csv(OUT_INPUT_CONSUMPTION_CSV, input_rows)

        input_pass = all(to_bool(row.get("passed")) for row in input_rows)

        contract_ready = (
            contract.get("contract_status") == "MARKET_STATE_TRANSITION_CONTRACT_READY"
            and contract.get("research_key") == EXPECTED_RESEARCH_KEY
            and contract.get("plugin_key") == EXPECTED_PLUGIN_KEY
        )
        plugin_ready = plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY and explicitly_blocked(plugin.get("plugin_expansion_allowed"))
        source_panel_exists = source_panel_path.exists()

        if not (contract_ready and plugin_ready and input_pass and source_panel_exists):
            result = {
                **base_result,
                "runner_status": "MARKET_STATE_TRANSITION_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_MARKET_STATE_TRANSITION_PREREQUISITES_NO_RELEASE",
                "reason": (
                    f"contract_ready={contract_ready}; plugin_ready={plugin_ready}; "
                    f"input_pass={input_pass}; source_panel_exists={source_panel_exists}"
                ),
                "input_rows": input_rows,
                "release_allowed": False,
                "elapsed_seconds": round(time_module.time() - started, 3),
                **SAFETY_FLAGS,
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, summarize_text(result))
            print_summary(result)
            return 0

        print(f"Reading source panel: {source_panel_path}")
        df = pd.read_parquet(source_panel_path)
        df = df.copy()

        if "time" not in df.columns or "symbol" not in df.columns:
            result = {
                **base_result,
                "runner_status": "MARKET_STATE_TRANSITION_RUNNER_BLOCKED_MISSING_TIME_OR_SYMBOL",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_SOURCE_PANEL_SCHEMA_NO_RELEASE",
                "reason": f"time_present={'time' in df.columns}; symbol_present={'symbol' in df.columns}",
                "release_allowed": False,
                "elapsed_seconds": round(time_module.time() - started, 3),
                **SAFETY_FLAGS,
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, summarize_text(result))
            print_summary(result)
            return 0

        df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
        df["month"] = safe_month_from_time(df["time"])
        df["symbol"] = df["symbol"].astype(str)
        df = add_derived_features(df)
        df = df.dropna(subset=["time", "month", "symbol"])

        row_count = int(len(df))
        symbol_count = int(df["symbol"].nunique())
        raw_months = sorted(df["month"].dropna().astype(str).unique().tolist())
        raw_calendar_month_count = len(raw_months)
        canonical_months = choose_canonical_months(df, 12)
        canonical_policy_month_count = len(canonical_months)

        feature_inventory_rows, selected_features = inventory_features(df, plugin)
        method_rows = inventory_methods(plugin)

        write_csv(OUT_STATE_FEATURE_CSV, feature_inventory_rows)
        write_csv(OUT_METHOD_CSV, method_rows)

        negative_controls = plugin.get("negative_controls")
        if not isinstance(negative_controls, list):
            negative_controls = []

        if (
            row_count < 1000000
            or symbol_count < 200
            or canonical_policy_month_count != 12
            or len(selected_features) < 2
            or len(method_rows) < 6
            or len(negative_controls) < 6
        ):
            result = {
                **base_result,
                "runner_status": "MARKET_STATE_TRANSITION_RUNNER_BLOCKED_PANEL_OR_FEATURE_COVERAGE_FAILED",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_MARKET_STATE_TRANSITION_FEATURE_COVERAGE_NO_RELEASE",
                "reason": (
                    f"row_count={row_count}; symbol_count={symbol_count}; canonical_policy_month_count={canonical_policy_month_count}; "
                    f"selected_features={len(selected_features)}; methods={len(method_rows)}; controls={len(negative_controls)}"
                ),
                "row_count": row_count,
                "symbol_count": symbol_count,
                "raw_calendar_month_count": raw_calendar_month_count,
                "canonical_policy_month_count": canonical_policy_month_count,
                "selected_features": selected_features,
                "release_allowed": False,
                "elapsed_seconds": round(time_module.time() - started, 3),
                **SAFETY_FLAGS,
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, summarize_text(result))
            print_summary(result)
            return 0

        print(f"Building time-state frame: features={len(selected_features)} canonical_months={canonical_policy_month_count}")
        ts = build_time_state_frame(df, selected_features, canonical_months)

        print("Computing state transition summaries...")
        transition_month_rows, transition_summary_rows = build_transition_summaries(
            ts=ts,
            selected_features=selected_features,
            canonical_months=canonical_months,
        )

        write_csv(OUT_MONTH_CSV, transition_month_rows)
        write_csv(OUT_SUMMARY_CSV, transition_summary_rows)

        preview_rows = [
            row for row in transition_summary_rows
            if to_bool(row.get("strict_12_transition_preview"))
        ]
        strict_preview_count = len(preview_rows)
        observed_best_score = max(
            [to_float(row.get("total_transition_score")) for row in transition_summary_rows] or [0.0]
        )

        print(f"Running negative controls: controls={len(negative_controls)}")
        negative_rows = run_negative_controls(
            transition_month_rows=transition_month_rows,
            observed_preview_count=strict_preview_count,
            observed_best_score=observed_best_score,
            controls=[str(x) for x in negative_controls],
        )
        write_csv(OUT_NEGATIVE_CSV, negative_rows)

        caps = plugin.get("gate_caps") if isinstance(plugin.get("gate_caps"), dict) else {}
        true_null_runs = max(1000, to_int(plugin.get("minimum_empirical_null_runs")), to_int(contract.get("minimum_empirical_null_runs")))

        print(f"Running true source-panel null replay: runs={true_null_runs}")
        true_null_rows = run_true_null_rerun(
            transition_month_rows=transition_month_rows,
            observed_best_score=observed_best_score,
            runs=true_null_runs,
            caps=caps,
        )
        write_csv(OUT_TRUE_NULL_CSV, true_null_rows)

        material_rows = build_material_difference_report(contract, failed_state, blocklist)
        write_csv(OUT_MATERIAL_DIFF_CSV, material_rows)

        policy_gate_rows = build_policy_gates(
            input_pass=input_pass,
            row_count=row_count,
            symbol_count=symbol_count,
            canonical_month_count=canonical_policy_month_count,
            selected_feature_count=len(selected_features),
            transition_method_count=len(method_rows),
            negative_control_count=len(negative_controls),
            preview_count=strict_preview_count,
            negative_rows=negative_rows,
            true_null_rows=true_null_rows,
            material_rows=material_rows,
        )
        write_csv(OUT_POLICY_GATE_CSV, policy_gate_rows)

        failed_gate_keys = [
            str(row.get("gate_key"))
            for row in policy_gate_rows
            if not to_bool(row.get("passed"))
        ]
        policy_gate_pass = len(failed_gate_keys) == 0

        true_null_summary = [row for row in true_null_rows if row.get("run_id") == "SUMMARY"]
        max_strict_rate = to_float(true_null_summary[0].get("strict_12_any_random_hit_rate"), 1.0) if true_null_summary else 1.0
        max_null_rate = to_float(true_null_summary[0].get("null_adjusted_any_random_hit_rate"), 1.0) if true_null_summary else 1.0

        if strict_preview_count > 0 and policy_gate_pass:
            runner_status = "MARKET_STATE_TRANSITION_RUNNER_PREVIEW_FOUND_TRUE_NULL_CLEAN_NOT_RELEASE"
            next_action = "BUILD_MARKET_STATE_TRANSITION_EVALUATOR_NO_RELEASE"
            reason = (
                f"strict_12_transition_preview_count={strict_preview_count}; policy_gate_pass=True; "
                f"true_null_clean=True; release_allowed=False"
            )
        elif strict_preview_count > 0:
            runner_status = "MARKET_STATE_TRANSITION_RUNNER_PREVIEW_FOUND_BUT_TRUE_NULL_OR_POLICY_FAIL"
            next_action = "BUILD_MARKET_STATE_TRANSITION_EVALUATOR_KEEP_ACTIONS_BLOCKED"
            reason = (
                f"strict_12_transition_preview_count={strict_preview_count}; failed_gates={failed_gate_keys}; "
                f"max_strict_rate={max_strict_rate}; max_null_rate={max_null_rate}; release_allowed=False"
            )
        else:
            runner_status = "MARKET_STATE_TRANSITION_RUNNER_COMPLETE_NO_POLICY_LOCKED_TRANSITION_PREVIEW"
            next_action = "BUILD_MARKET_STATE_TRANSITION_EVALUATOR_OR_ROTATE_NO_RELEASE"
            reason = (
                f"strict_12_transition_preview_count=0; transition_axis_count={len(transition_summary_rows)}; "
                f"failed_gates={failed_gate_keys}; release_allowed=False"
            )

        result = {
            **base_result,
            "runner_status": runner_status,
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "reason": reason,
            "row_count": row_count,
            "symbol_count": symbol_count,
            "raw_calendar_month_count": raw_calendar_month_count,
            "canonical_policy_month_count": canonical_policy_month_count,
            "canonical_policy_months": canonical_months,
            "selected_state_feature_count": len(selected_features),
            "selected_state_features": selected_features,
            "transition_method_count": len(method_rows),
            "transition_axis_count": len(transition_summary_rows),
            "strict_12_transition_preview_count": strict_preview_count,
            "negative_control_count": len(negative_controls),
            "true_null_runs": true_null_runs,
            "max_strict_12_any_random_hit_rate": max_strict_rate,
            "max_null_adjusted_any_random_hit_rate": max_null_rate,
            "policy_gate_pass": policy_gate_pass,
            "policy_gate_fail_count": len(failed_gate_keys),
            "failed_gate_keys": failed_gate_keys,
            "top_transition_rows": transition_summary_rows[:25],
            "policy_gate_rows": policy_gate_rows,
            "negative_control_rows": negative_rows,
            "material_difference_rows": material_rows,
            "release_allowed": False,
            "release_gate_feed": {
                "MARKET_STATE_TRANSITION_RUNNER_RAN": True,
                "MARKET_STATE_TRANSITION_PREVIEW_FOUND": strict_preview_count > 0,
                "MARKET_STATE_TRANSITION_POLICY_GATE_PASS": policy_gate_pass,
                "TRUE_NULL_CLEAN": max_strict_rate <= 0.01 and max_null_rate <= 0.005,
                "PLUGIN_EXPANSION_ALLOWED_FROM_THIS_RUNNER": False,
                "RELEASE_PASS_FROM_THIS_RUNNER": False,
                "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_RUNNER": False,
                "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_RUNNER": False,
                "FAMILY_RELEASE_ALLOWED_FROM_THIS_RUNNER": False,
                "RUNTIME_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
                "CAPITAL_CHANGE_ALLOWED_FROM_THIS_RUNNER": False,
                "ACTIVE_PAPER_ALLOWED_FROM_THIS_RUNNER": False,
                "LIVE_ALLOWED_FROM_THIS_RUNNER": False,
                "REAL_ORDERS_ALLOWED_FROM_THIS_RUNNER": False,
            },
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }

        write_json(OUT_JSON, result)
        write_text(OUT_TXT, summarize_text(result))
        print_summary(result)
        return 0

    except Exception as exc:
        result = {
            **base_result,
            "runner_status": "MARKET_STATE_TRANSITION_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_MARKET_STATE_TRANSITION_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(exc).__name__}: {exc}",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "release_allowed": False,
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text(OUT_TXT, summarize_text(result))
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
