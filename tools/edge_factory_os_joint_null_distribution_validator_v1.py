#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Joint Null Distribution Validator v1

Purpose:
- Stop escalation after external audit raised overfitting / multiple-testing risk.
- Consume latest Market State Transition Runner v1 output.
- Re-run the full market-state transition search procedure under procedural/joint nulls.
- Ask the correct question:
    P(null procedure finds >= observed strict_12 previews)
- Account for 160-axis search procedure instead of testing a single axis.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This module does NOT:
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

MARKET_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_market_state_transition_runner"
    / "market_state_transition_runner_latest.json"
)

MARKET_SUMMARY_CSV = (
    BASE_DIR
    / "edge_factory_os_market_state_transition_runner"
    / "market_state_transition_summary_latest.csv"
)

MARKET_CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "market_state_transition_contract_v1.json"
)

MARKET_PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "market_state_transition_plugin_v1.json"
)

FRAMEWORK_STATUS_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "status"
    / "framework_status_panel_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

TRUE_PANEL_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "true_source_panel_empirical_null_baseline_state_v1.json"
)

FAILED_ANOMALY_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "source_panel_anomaly_deep_validation_state_v1.json"
)

LESSON_INDEX_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_PATH = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

SOURCE_PANEL_PATH = (
    BASE_DIR
    / "edge_factory_feature_panels"
    / "post_impulse_drift_long_v1"
    / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet"
)

OUT_DIR = BASE_DIR / "edge_factory_os_joint_null_distribution_validator"

OUT_JSON = OUT_DIR / "joint_null_distribution_validator_latest.json"
OUT_TXT = OUT_DIR / "joint_null_distribution_validator_latest.txt"
OUT_RUNS_CSV = OUT_DIR / "joint_null_distribution_runs_latest.csv"
OUT_NULL_SUMMARY_CSV = OUT_DIR / "joint_null_distribution_summary_latest.csv"
OUT_POLICY_GATE_CSV = OUT_DIR / "joint_null_distribution_policy_gate_latest.csv"
OUT_OBSERVED_CSV = OUT_DIR / "joint_null_distribution_observed_market_state_latest.csv"

REPO_POLICY_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "joint_null_distribution_validation_state_v1.json"
)

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

RUNNER_NAME = "edge_factory_os_joint_null_distribution_validator_v1"

MONTH_SCORE_THRESHOLD = 1.65
TOTAL_SCORE_THRESHOLD = 22.0

# 1000 is the minimum audit-recommended number.
# You can temporarily reduce this only for debugging, not for decision.
MIN_JOINT_NULL_RUNS = 1000

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


def read_csv_rows(path: Path, limit: int | None = None) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if limit is not None and i >= limit:
                    break
                rows.append(dict(row))
    except Exception:
        return []
    return rows


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


def extract_lessons(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return [x for x in obj["lessons"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def extract_blocked_routes(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("blocked_routes"), list):
        return [x for x in obj["blocked_routes"] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def select_features_from_runner_or_plugin(
    df: pd.DataFrame,
    runner: Dict[str, Any],
    plugin: Dict[str, Any],
) -> List[str]:
    from_runner = runner.get("selected_state_features")
    if isinstance(from_runner, list):
        selected = [
            str(x)
            for x in from_runner
            if str(x) in df.columns and not feature_leakage_flag(str(x))
        ]
        if selected:
            return selected[:10]

    groups = plugin.get("state_feature_groups")
    candidates: List[str] = []
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, dict):
                continue
            feats = group.get("candidate_features")
            if isinstance(feats, list):
                candidates.extend([str(x) for x in feats])

    fallback = [
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
    candidates.extend(fallback)

    selected = []
    for feature in candidates:
        if feature in selected:
            continue
        if feature not in df.columns:
            continue
        if feature_leakage_flag(feature):
            continue
        x = pd.to_numeric(df[feature], errors="coerce")
        if x.notna().mean() >= 0.70:
            selected.append(feature)

    return selected[:10]


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


def transition_axis_scores_for_ts(
    ts: pd.DataFrame,
    state_cols: List[str],
    canonical_months: List[str],
) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []

    transition_keys = ["0->2", "2->0", "0->1", "1->2", "2->1", "1->0", "0->0", "2->2"]

    for state_col in state_cols:
        x = pd.to_numeric(ts[state_col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        valid = ts.loc[x.notna(), ["time", "month"]].copy()
        valid[state_col] = x.loc[x.notna()].to_numpy()

        if len(valid) < 100:
            continue

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

        global_counts = valid["transition"].value_counts(normalize=True).to_dict()

        for transition_key in transition_keys:
            scores = []
            counts = []

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
                scores.append(score)
                counts.append(total)

            active_months = sum(1 for c in counts if c > 0)
            strict_months = sum(1 for s in scores if s >= MONTH_SCORE_THRESHOLD)
            total_score = float(sum(scores))
            min_score = float(min(scores)) if scores else 0.0
            median_score = float(np.median(scores)) if scores else 0.0

            strict_12 = bool(
                active_months >= 12
                and strict_months >= 12
                and total_score >= TOTAL_SCORE_THRESHOLD
            )

            summaries.append({
                "transition_axis_key": f"{state_col}_{transition_key}",
                "state_col": state_col,
                "transition_key": transition_key,
                "active_months": active_months,
                "strict_months": strict_months,
                "total_transition_score": total_score,
                "min_month_transition_score": min_score,
                "median_month_transition_score": median_score,
                "strict_12_transition_preview": strict_12,
            })

    summaries = sorted(
        summaries,
        key=lambda r: (
            to_bool(r.get("strict_12_transition_preview")),
            to_float(r.get("total_transition_score")),
            to_float(r.get("median_month_transition_score")),
        ),
        reverse=True,
    )

    return summaries


def make_null_ts(
    ts: pd.DataFrame,
    state_cols: List[str],
    canonical_months: List[str],
    null_model: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    null_ts = ts.copy()

    if null_model == "month_block_shuffle":
        shuffled_months = list(canonical_months)
        rng.shuffle(shuffled_months)
        mapping = dict(zip(canonical_months, shuffled_months))
        null_ts["month"] = null_ts["month"].map(mapping).fillna(null_ts["month"])

    elif null_model == "time_block_shuffle":
        block_size = 24 * 7
        idx_blocks = [
            np.arange(i, min(i + block_size, len(null_ts)))
            for i in range(0, len(null_ts), block_size)
        ]
        rng.shuffle(idx_blocks)
        new_order = np.concatenate(idx_blocks)
        for col in state_cols:
            null_ts[col] = null_ts[col].to_numpy()[new_order]

    elif null_model == "state_col_independent_block_shuffle":
        block_size = 24 * 7
        for col in state_cols:
            values = null_ts[col].to_numpy().copy()
            blocks = [
                np.arange(i, min(i + block_size, len(values)))
                for i in range(0, len(values), block_size)
            ]
            rng.shuffle(blocks)
            order = np.concatenate(blocks)
            null_ts[col] = values[order]

    elif null_model == "within_month_time_shuffle":
        for month in canonical_months:
            mask = null_ts["month"] == month
            idx = np.where(mask.to_numpy())[0]
            if len(idx) <= 1:
                continue
            shuffled_idx = idx.copy()
            rng.shuffle(shuffled_idx)
            for col in state_cols:
                values = null_ts[col].to_numpy(copy=True)
                values[idx] = values[shuffled_idx]
                null_ts[col] = values

    else:
        # Conservative fallback: block shuffle, not row shuffle.
        block_size = 24 * 7
        idx_blocks = [
            np.arange(i, min(i + block_size, len(null_ts)))
            for i in range(0, len(null_ts), block_size)
        ]
        rng.shuffle(idx_blocks)
        new_order = np.concatenate(idx_blocks)
        for col in state_cols:
            null_ts[col] = null_ts[col].to_numpy()[new_order]

    return null_ts


def run_joint_null_distribution(
    ts: pd.DataFrame,
    state_cols: List[str],
    canonical_months: List[str],
    observed_preview_count: int,
    observed_best_score: float,
    runs_per_model: int,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    null_models = [
        "month_block_shuffle",
        "time_block_shuffle",
        "state_col_independent_block_shuffle",
        "within_month_time_shuffle",
    ]

    all_runs: List[Dict[str, Any]] = []

    for model_idx, null_model in enumerate(null_models):
        rng = np.random.default_rng(20260514 + model_idx * 10000)

        for run_id in range(1, runs_per_model + 1):
            if run_id == 1 or run_id % 25 == 0 or run_id == runs_per_model:
                print(f"JOINT_NULL_PROGRESS null_model={null_model} run={run_id}/{runs_per_model}", flush=True)

            null_ts = make_null_ts(
                ts=ts,
                state_cols=state_cols,
                canonical_months=canonical_months,
                null_model=null_model,
                rng=rng,
            )

            summaries = transition_axis_scores_for_ts(
                ts=null_ts,
                state_cols=state_cols,
                canonical_months=canonical_months,
            )

            strict_count = sum(1 for r in summaries if to_bool(r.get("strict_12_transition_preview")))
            best_score = max([to_float(r.get("total_transition_score")) for r in summaries] or [0.0])
            top_axis = summaries[0].get("transition_axis_key") if summaries else None

            all_runs.append({
                "null_model": null_model,
                "run_id": run_id,
                "null_transition_axis_count": len(summaries),
                "null_strict_12_transition_preview_count": strict_count,
                "null_best_total_transition_score": best_score,
                "null_top_axis": top_axis,
                "hit_ge_observed_preview_count": strict_count >= observed_preview_count,
                "hit_ge_observed_best_score": best_score >= observed_best_score,
                "joint_hit_ge_count_and_score": strict_count >= observed_preview_count and best_score >= observed_best_score,
            })

    summary_rows: List[Dict[str, Any]] = []

    for null_model in null_models:
        subset = [r for r in all_runs if r["null_model"] == null_model]
        if not subset:
            continue

        preview_counts = [to_int(r.get("null_strict_12_transition_preview_count")) for r in subset]
        best_scores = [to_float(r.get("null_best_total_transition_score")) for r in subset]

        summary_rows.append({
            "null_model": null_model,
            "runs": len(subset),
            "observed_preview_count": observed_preview_count,
            "observed_best_score": observed_best_score,
            "p_ge_observed_preview_count": float(np.mean([1.0 if r["hit_ge_observed_preview_count"] else 0.0 for r in subset])),
            "p_ge_observed_best_score": float(np.mean([1.0 if r["hit_ge_observed_best_score"] else 0.0 for r in subset])),
            "p_joint_ge_count_and_score": float(np.mean([1.0 if r["joint_hit_ge_count_and_score"] else 0.0 for r in subset])),
            "mean_null_preview_count": float(np.mean(preview_counts)),
            "p95_null_preview_count": float(np.quantile(preview_counts, 0.95)),
            "p99_null_preview_count": float(np.quantile(preview_counts, 0.99)),
            "mean_null_best_score": float(np.mean(best_scores)),
            "p95_null_best_score": float(np.quantile(best_scores, 0.95)),
            "p99_null_best_score": float(np.quantile(best_scores, 0.99)),
            "passed_count_gate": float(np.mean([1.0 if r["hit_ge_observed_preview_count"] else 0.0 for r in subset])) <= 0.01,
            "passed_joint_gate": float(np.mean([1.0 if r["joint_hit_ge_count_and_score"] else 0.0 for r in subset])) <= 0.005,
        })

    return all_runs, summary_rows


def build_policy_gates(
    *,
    observed_preview_count: int,
    observed_axis_count: int,
    observed_best_score: float,
    runs_per_model: int,
    null_summary_rows: List[Dict[str, Any]],
    lesson_count: int,
    blocked_route_count: int,
) -> List[Dict[str, Any]]:
    max_p_ge_count = max([to_float(r.get("p_ge_observed_preview_count"), 1.0) for r in null_summary_rows] or [1.0])
    max_p_joint = max([to_float(r.get("p_joint_ge_count_and_score"), 1.0) for r in null_summary_rows] or [1.0])

    # This is intentionally harsh after external audit.
    # Route exploration pressure requires far stricter gates.
    effective_comparison_count = max(1, observed_axis_count + blocked_route_count * observed_axis_count)
    bonferroni_alpha = 0.05 / effective_comparison_count

    return [
        {
            "gate_key": "PROCEDURAL_NULL_RUNS_MINIMUM_PASS",
            "passed": runs_per_model >= MIN_JOINT_NULL_RUNS,
            "observed": runs_per_model,
            "required": f">={MIN_JOINT_NULL_RUNS}",
        },
        {
            "gate_key": "OBSERVED_PREVIEW_COUNT_PRESENT",
            "passed": observed_preview_count > 0,
            "observed": observed_preview_count,
            "required": ">0",
        },
        {
            "gate_key": "PROCEDURAL_NULL_COUNT_P_VALUE_PASS",
            "passed": max_p_ge_count <= 0.01,
            "observed": max_p_ge_count,
            "required": "<=0.01",
        },
        {
            "gate_key": "PROCEDURAL_NULL_JOINT_P_VALUE_PASS",
            "passed": max_p_joint <= 0.005,
            "observed": max_p_joint,
            "required": "<=0.005",
        },
        {
            "gate_key": "GLOBAL_MULTIPLE_TESTING_PRESSURE_RECORDED",
            "passed": blocked_route_count > 0 and lesson_count > 0,
            "observed": {"lesson_count": lesson_count, "blocked_route_count": blocked_route_count},
            "required": "lesson/blocklist history must be consumed",
        },
        {
            "gate_key": "BONFERRONI_PRESSURE_DIAGNOSTIC_PASS",
            "passed": max_p_joint <= bonferroni_alpha,
            "observed": {"max_p_joint": max_p_joint, "bonferroni_alpha": bonferroni_alpha, "effective_comparison_count": effective_comparison_count},
            "required": "max_p_joint <= 0.05 / effective_comparison_count",
        },
        {
            "gate_key": "CANDIDATE_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "candidate_generation_allowed=False",
        },
        {
            "gate_key": "RELEASE_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "family_release_allowed=False",
        },
        {
            "gate_key": "LIVE_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "live_allowed=False",
        },
    ]


def build_text(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS JOINT NULL DISTRIBUTION VALIDATOR v1")
    lines.append("=" * 100)

    for key in [
        "validator_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "observed_runner_status",
        "observed_transition_axis_count",
        "observed_strict_12_transition_preview_count",
        "observed_best_total_transition_score",
        "joint_null_model_count",
        "runs_per_null_model",
        "total_joint_null_runs",
        "max_p_ge_observed_preview_count",
        "max_p_joint_ge_count_and_score",
        "joint_null_policy_gate_pass",
        "joint_null_policy_gate_fail_count",
        "failed_gate_keys",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "elapsed_seconds",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("NULL SUMMARY")
    lines.append("-" * 100)
    for row in result.get("null_summary_rows", []):
        lines.append(
            f"{row.get('null_model')}: "
            f"p_count={row.get('p_ge_observed_preview_count')} "
            f"p_joint={row.get('p_joint_ge_count_and_score')} "
            f"mean_count={row.get('mean_null_preview_count')} "
            f"p99_count={row.get('p99_null_preview_count')}"
        )

    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for row in result.get("policy_gate_rows", []):
        lines.append(f"{row.get('gate_key')}: passed={row.get('passed')} observed={row.get('observed')} required={row.get('required')}")

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for key in [
        "output_json",
        "output_txt",
        "runs_csv",
        "null_summary_csv",
        "policy_gate_csv",
        "observed_csv",
        "repo_policy_state_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS JOINT NULL DISTRIBUTION VALIDATOR v1")
    print("=" * 100)
    print(f"validator_status: {result.get('validator_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"observed_runner_status: {result.get('observed_runner_status')}")
    print(f"observed_transition_axis_count: {result.get('observed_transition_axis_count')}")
    print(f"observed_strict_12_transition_preview_count: {result.get('observed_strict_12_transition_preview_count')}")
    print(f"observed_best_total_transition_score: {result.get('observed_best_total_transition_score')}")
    print(f"joint_null_model_count: {result.get('joint_null_model_count')}")
    print(f"runs_per_null_model: {result.get('runs_per_null_model')}")
    print(f"total_joint_null_runs: {result.get('total_joint_null_runs')}")
    print(f"max_p_ge_observed_preview_count: {result.get('max_p_ge_observed_preview_count')}")
    print(f"max_p_joint_ge_count_and_score: {result.get('max_p_joint_ge_count_and_score')}")
    print(f"joint_null_policy_gate_pass: {result.get('joint_null_policy_gate_pass')}")
    print(f"joint_null_policy_gate_fail_count: {result.get('joint_null_policy_gate_fail_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('null_summary_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPO_POLICY_STATE_JSON.parent.mkdir(parents=True, exist_ok=True)

    market_runner = load_json(MARKET_RUNNER_JSON, default={})
    contract = load_json(MARKET_CONTRACT_JSON, default={})
    plugin = load_json(MARKET_PLUGIN_JSON, default={})
    framework_status = load_json(FRAMEWORK_STATUS_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    true_panel_state = load_json(TRUE_PANEL_STATE_JSON, default={})
    failed_anomaly_state = load_json(FAILED_ANOMALY_STATE_JSON, default={})
    lessons = extract_lessons(load_json(LESSON_INDEX_PATH, default={}))
    blocked_routes = extract_blocked_routes(load_json(BLOCKLIST_PATH, default={}))
    market_summary_rows = read_csv_rows(MARKET_SUMMARY_CSV)

    observed_preview_count = to_int(market_runner.get("strict_12_transition_preview_count"))
    observed_axis_count = to_int(market_runner.get("transition_axis_count"))
    observed_runner_status = str(market_runner.get("runner_status"))
    observed_best_score = max([to_float(r.get("total_transition_score")) for r in market_summary_rows] or [0.0])

    base_result = {
        "validator_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "observed_runner_status": observed_runner_status,
        "observed_transition_axis_count": observed_axis_count,
        "observed_strict_12_transition_preview_count": observed_preview_count,
        "observed_best_total_transition_score": observed_best_score,
        "market_contract_id": contract.get("contract_id"),
        "market_route_hash": contract.get("route_hash"),
        "policy_hash": market_runner.get("policy_hash") or contract.get("policy_hash"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "runs_csv": str(OUT_RUNS_CSV),
        "null_summary_csv": str(OUT_NULL_SUMMARY_CSV),
        "policy_gate_csv": str(OUT_POLICY_GATE_CSV),
        "observed_csv": str(OUT_OBSERVED_CSV),
        "repo_policy_state_json": str(REPO_POLICY_STATE_JSON),
        **SAFETY_FLAGS,
    }

    observed_rows = [
        {
            "observed_runner_status": observed_runner_status,
            "observed_transition_axis_count": observed_axis_count,
            "observed_strict_12_transition_preview_count": observed_preview_count,
            "observed_best_total_transition_score": observed_best_score,
            "market_contract_id": contract.get("contract_id"),
            "market_route_hash": contract.get("route_hash"),
            "policy_hash": market_runner.get("policy_hash") or contract.get("policy_hash"),
        }
    ]
    write_csv(OUT_OBSERVED_CSV, observed_rows)

    prerequisite_pass = (
        observed_runner_status == "MARKET_STATE_TRANSITION_RUNNER_PREVIEW_FOUND_TRUE_NULL_CLEAN_NOT_RELEASE"
        and observed_preview_count > 0
        and observed_axis_count >= 100
        and contract.get("contract_status") == "MARKET_STATE_TRANSITION_CONTRACT_READY"
        and plugin.get("plugin_key") == "MARKET_STATE_TRANSITION_PLUGIN_V1"
        and framework_status.get("panel_status") == "FRAMEWORK_STATUS_PANEL_READY_POLICY_LOCKED_NO_ACTUAL_SIGNAL"
        and policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
        and bool(true_panel_state.get("false_positive_methodology_repaired"))
        and not bool(true_panel_state.get("actual_signal_present"))
        and failed_anomaly_state.get("state_status") == "SOURCE_PANEL_ANOMALY_DEEP_VALIDATION_FAILED_ROUTE_CLOSED"
        and SOURCE_PANEL_PATH.exists()
    )

    if not prerequisite_pass:
        result = {
            **base_result,
            "validator_status": "JOINT_NULL_DISTRIBUTION_VALIDATOR_BLOCKED_PREREQUISITE_NOT_MET",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_JOINT_NULL_VALIDATOR_PREREQUISITES_NO_RELEASE",
            "reason": (
                f"observed_runner_status={observed_runner_status}; observed_preview_count={observed_preview_count}; "
                f"observed_axis_count={observed_axis_count}; source_panel_exists={SOURCE_PANEL_PATH.exists()}"
            ),
            "joint_null_policy_gate_pass": False,
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text(OUT_TXT, build_text(result))
        print_summary(result)
        return 0

    print(f"Reading source panel: {SOURCE_PANEL_PATH}")
    df = pd.read_parquet(SOURCE_PANEL_PATH)
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df["month"] = safe_month_from_time(df["time"])
    df["symbol"] = df["symbol"].astype(str)
    df = add_derived_features(df)
    df = df.dropna(subset=["time", "month", "symbol"])

    canonical_months = choose_canonical_months(df, 12)
    selected_features = select_features_from_runner_or_plugin(df, market_runner, plugin)

    print(f"Building time-state frame: selected_features={len(selected_features)}")
    ts = build_time_state_frame(df, selected_features, canonical_months)

    state_cols: List[str] = []
    for feature in selected_features:
        for suffix in ["median", "std", "p75", "p25"]:
            col = f"{feature}_{suffix}"
            if col in ts.columns:
                state_cols.append(col)

    # Recompute observed using the same local procedure for comparability.
    observed_summaries = transition_axis_scores_for_ts(ts, state_cols, canonical_months)
    local_observed_preview_count = sum(1 for r in observed_summaries if to_bool(r.get("strict_12_transition_preview")))
    local_observed_best_score = max([to_float(r.get("total_transition_score")) for r in observed_summaries] or [0.0])

    # Use the stricter observed count/score from actual runner vs recomputation.
    effective_observed_preview_count = max(observed_preview_count, local_observed_preview_count)
    effective_observed_best_score = max(observed_best_score, local_observed_best_score)

    runs_per_model = MIN_JOINT_NULL_RUNS

    print(
        f"Running procedural/joint null: state_cols={len(state_cols)}, "
        f"observed_preview_count={effective_observed_preview_count}, runs_per_model={runs_per_model}"
    )

    null_run_rows, null_summary_rows = run_joint_null_distribution(
        ts=ts,
        state_cols=state_cols,
        canonical_months=canonical_months,
        observed_preview_count=effective_observed_preview_count,
        observed_best_score=effective_observed_best_score,
        runs_per_model=runs_per_model,
    )

    write_csv(OUT_RUNS_CSV, null_run_rows)
    write_csv(OUT_NULL_SUMMARY_CSV, null_summary_rows)

    max_p_count = max([to_float(r.get("p_ge_observed_preview_count"), 1.0) for r in null_summary_rows] or [1.0])
    max_p_joint = max([to_float(r.get("p_joint_ge_count_and_score"), 1.0) for r in null_summary_rows] or [1.0])

    policy_gate_rows = build_policy_gates(
        observed_preview_count=effective_observed_preview_count,
        observed_axis_count=observed_axis_count,
        observed_best_score=effective_observed_best_score,
        runs_per_model=runs_per_model,
        null_summary_rows=null_summary_rows,
        lesson_count=len(lessons),
        blocked_route_count=len(blocked_routes),
    )
    write_csv(OUT_POLICY_GATE_CSV, policy_gate_rows)

    failed_gates = [str(r.get("gate_key")) for r in policy_gate_rows if not to_bool(r.get("passed"))]
    joint_null_policy_gate_pass = len(failed_gates) == 0

    if joint_null_policy_gate_pass:
        validator_status = "JOINT_NULL_DISTRIBUTION_VALIDATOR_PASS_BUT_RESEARCH_ONLY"
        next_action = "BUILD_MARKET_STATE_TRANSITION_EVALUATOR_ONLY_AFTER_AUDIT_REVIEW_NO_RELEASE"
        reason = (
            f"procedural_null_pass=True; max_p_count={max_p_count}; max_p_joint={max_p_joint}; "
            f"promotion_still_blocked=True"
        )
    else:
        validator_status = "JOINT_NULL_DISTRIBUTION_VALIDATOR_FAIL_RESEARCH_METHODOLOGY_REPAIR_REQUIRED"
        next_action = "BUILD_GLOBAL_MULTIPLE_TESTING_LEDGER_AND_RESEARCH_BUDGET_POLICY_NO_RELEASE"
        reason = (
            f"procedural_null_pass=False; failed_gates={failed_gates}; "
            f"max_p_count={max_p_count}; max_p_joint={max_p_joint}; market_state_preview_not_validated=True"
        )

    policy_state = {
        "state_name": "edge_factory_os_joint_null_distribution_validation_state_v1",
        "created_at_utc": utc_now_iso(),
        "validator_status": validator_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "observed_runner_status": observed_runner_status,
        "observed_transition_axis_count": observed_axis_count,
        "observed_strict_12_transition_preview_count": observed_preview_count,
        "local_observed_strict_12_transition_preview_count": local_observed_preview_count,
        "effective_observed_preview_count": effective_observed_preview_count,
        "effective_observed_best_score": effective_observed_best_score,
        "joint_null_model_count": len(null_summary_rows),
        "runs_per_null_model": runs_per_model,
        "total_joint_null_runs": len(null_run_rows),
        "max_p_ge_observed_preview_count": max_p_count,
        "max_p_joint_ge_count_and_score": max_p_joint,
        "joint_null_policy_gate_pass": joint_null_policy_gate_pass,
        "failed_gate_keys": failed_gates,
        "market_state_preview_validated": joint_null_policy_gate_pass,
        "candidate_generation_allowed": False,
        "candidate_contract_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "next_action": next_action,
    }
    write_json(REPO_POLICY_STATE_JSON, policy_state)

    result = {
        **base_result,
        "validator_status": validator_status,
        "severity": "ATTENTION",
        "allowed_scope": "READ_ONLY_RESEARCH",
        "next_action": next_action,
        "reason": reason,
        "canonical_policy_months": canonical_months,
        "selected_features": selected_features,
        "state_col_count": len(state_cols),
        "local_observed_strict_12_transition_preview_count": local_observed_preview_count,
        "local_observed_best_total_transition_score": local_observed_best_score,
        "effective_observed_preview_count": effective_observed_preview_count,
        "effective_observed_best_score": effective_observed_best_score,
        "joint_null_model_count": len(null_summary_rows),
        "runs_per_null_model": runs_per_model,
        "total_joint_null_runs": len(null_run_rows),
        "null_summary_rows": null_summary_rows,
        "policy_gate_rows": policy_gate_rows,
        "max_p_ge_observed_preview_count": max_p_count,
        "max_p_joint_ge_count_and_score": max_p_joint,
        "joint_null_policy_gate_pass": joint_null_policy_gate_pass,
        "joint_null_policy_gate_fail_count": len(failed_gates),
        "failed_gate_keys": failed_gates,
        "release_gate_feed": {
            "JOINT_NULL_DISTRIBUTION_VALIDATOR_RAN": True,
            "MARKET_STATE_PREVIEW_VALIDATED_BY_PROCEDURAL_NULL": joint_null_policy_gate_pass,
            "PROCEDURAL_NULL_MAX_P_GE_COUNT": max_p_count,
            "PROCEDURAL_NULL_MAX_P_JOINT": max_p_joint,
            "RELEASE_PASS_FROM_THIS_VALIDATOR": False,
            "CANDIDATE_GENERATION_ALLOWED_FROM_THIS_VALIDATOR": False,
            "CANDIDATE_CONTRACT_ALLOWED_FROM_THIS_VALIDATOR": False,
            "FAMILY_RELEASE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "RUNTIME_CHANGE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "CAPITAL_CHANGE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "ACTIVE_PAPER_ALLOWED_FROM_THIS_VALIDATOR": False,
            "LIVE_ALLOWED_FROM_THIS_VALIDATOR": False,
            "REAL_ORDERS_ALLOWED_FROM_THIS_VALIDATOR": False,
        },
        "elapsed_seconds": round(time_module.time() - started, 3),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

