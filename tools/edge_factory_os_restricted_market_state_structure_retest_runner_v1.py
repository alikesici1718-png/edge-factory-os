#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Restricted Market-State Structure Retest Runner v1

Purpose:
- Run exactly one bounded OFFLINE/READ-ONLY restricted market-state retest.
- Consume the restricted pre-registered contract and execution gate.
- Use a fixed omnibus transition-structure statistic, not broad axis search.
- Use procedural null models.
- Respect tiny alpha and route budget.
- If null resolution is insufficient for the tiny alpha, mark result as NOT VALIDATED.
- Keep holdout access forbidden.
- Keep candidate/family/runtime/capital/active-paper/live/real-order actions blocked.

This runner does NOT:
- generate candidates
- create candidate contracts
- release families
- touch runtime
- change capital
- access final holdout
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
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

FRAMEWORK_DIR = REPO_DIR / "edge_factory_os_framework"
POLICY_DIR = FRAMEWORK_DIR / "policies"
CONTRACT_DIR = FRAMEWORK_DIR / "contracts"
REGISTRY_DIR = FRAMEWORK_DIR / "registries"
QUEUE_DIR = FRAMEWORK_DIR / "queues"

SOURCE_PANEL_PATH = (
    BASE_DIR
    / "edge_factory_feature_panels"
    / "post_impulse_drift_long_v1"
    / "post_impulse_drift_long_v1_feature_panel_1h_dynamic.parquet"
)

CONTRACT_JSON = CONTRACT_DIR / "restricted_pre_registered_research_contract_proposal_v1.json"
EXECUTION_GATE_STATE_JSON = POLICY_DIR / "restricted_research_execution_gate_state_v1.json"
EXECUTION_POLICY_JSON = POLICY_DIR / "restricted_research_execution_policy_v1.json"
EXECUTION_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_research_execution_next_queue_v1.json"
BUDGET_ALLOCATION_JSON = POLICY_DIR / "restricted_research_budget_allocation_v1.json"

UNTOUCHED_HOLDOUT_REGISTRY_JSON = REGISTRY_DIR / "untouched_holdout_registry_v1.json"
HOLDOUT_ACCESS_CONTROL_JSON = POLICY_DIR / "holdout_access_control_policy_v1.json"
NESTED_VALIDATION_POLICY_JSON = POLICY_DIR / "nested_validation_policy_v1.json"
GLOBAL_ALPHA_ACCOUNTING_JSON = POLICY_DIR / "global_route_family_alpha_accounting_v1.json"
PROMISING_VAULT_JSON = POLICY_DIR / "promising_signal_vault_v1.json"

LESSON_INDEX_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "lesson_memory_index.json"
BLOCKLIST_JSON = BASE_DIR / "edge_factory_os_lesson_memory" / "candidate_route_blocklist.json"

OUT_DIR = BASE_DIR / "edge_factory_os_restricted_market_state_structure_retest_runner"
OUT_JSON = OUT_DIR / "restricted_market_state_structure_retest_runner_latest.json"
OUT_TXT = OUT_DIR / "restricted_market_state_structure_retest_runner_latest.txt"
OUT_SUMMARY_CSV = OUT_DIR / "restricted_market_state_structure_retest_summary_latest.csv"
OUT_NULL_CSV = OUT_DIR / "restricted_market_state_structure_retest_null_summary_latest.csv"

REPO_RETEST_STATE_JSON = POLICY_DIR / "restricted_market_state_structure_retest_state_v1.json"
REPO_BUDGET_CONSUMPTION_JSON = POLICY_DIR / "restricted_market_state_structure_retest_budget_consumption_v1.json"
REPO_NEXT_QUEUE_JSON = QUEUE_DIR / "restricted_market_state_structure_retest_next_queue_v1.json"

STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

NEXT_RESEARCH_KEY = "RD7_10_RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_EVALUATOR"
NEXT_MODULE = "edge_factory_os_restricted_market_state_structure_retest_evaluator_v1.py"

RNG_SEED = 20260514
RUNS_PER_NULL_MODEL = 1000
MIN_TRANSITION_GROUP_COUNT = 12

NULL_MODELS = [
    "month_block_shuffle",
    "time_block_shuffle",
    "state_label_within_month_shuffle",
    "within_month_outcome_shuffle",
]

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
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def extract_list(obj: Any, key: str) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        return [x for x in obj[key] if isinstance(x, dict)]
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def route_hash_blocked(blocked_routes: List[Dict[str, Any]], route_hash: str) -> bool:
    return route_hash in {str(x.get("route_hash")) for x in blocked_routes if isinstance(x, dict)}


def finite_float(x: Any, default: float = 0.0) -> float:
    try:
        val = float(x)
        if math.isfinite(val):
            return val
    except Exception:
        pass
    return default


def assign_tertile(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    q1 = s.quantile(1.0 / 3.0)
    q2 = s.quantile(2.0 / 3.0)

    if not np.isfinite(q1) or not np.isfinite(q2) or q1 == q2:
        rank_pct = s.rank(method="average", pct=True)
        return pd.Series(
            np.select(
                [rank_pct <= 1.0 / 3.0, rank_pct <= 2.0 / 3.0],
                ["low", "mid"],
                default="high",
            ),
            index=series.index,
        )

    return pd.Series(
        np.select(
            [s <= q1, s <= q2],
            ["low", "mid"],
            default="high",
        ),
        index=series.index,
    )


def make_month(series: pd.Series) -> pd.Series:
    # Avoid timezone drop warnings by making the timestamp naive only for month labels.
    try:
        return series.dt.tz_convert(None).dt.to_period("M").astype(str)
    except Exception:
        return series.dt.tz_localize(None).dt.to_period("M").astype(str)


def build_time_state_frame(panel_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    if not panel_path.exists():
        raise FileNotFoundError(str(panel_path))

    print(f"Reading source panel: {panel_path}", flush=True)
    df = pd.read_parquet(panel_path)

    required = ["time", "symbol", "open", "high", "low", "close", "coin_ret3_bps"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"missing required columns: {missing}")

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df = df.dropna(subset=["time", "symbol", "open", "high", "low", "close", "coin_ret3_bps"])

    for col in ["open", "high", "low", "close", "coin_ret3_bps"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["open", "high", "low", "close", "coin_ret3_bps"])
    df = df[df["open"] > 0]

    df["derived_candle_body_bps"] = (df["close"] - df["open"]).abs() / df["open"] * 10000.0

    if "entry_range_bps" in df.columns:
        df["derived_range_bps"] = pd.to_numeric(df["entry_range_bps"], errors="coerce")
    else:
        df["derived_range_bps"] = (df["high"] - df["low"]).abs() / df["open"] * 10000.0

    if "entry_vol_quote" in df.columns:
        vol = pd.to_numeric(df["entry_vol_quote"], errors="coerce").clip(lower=0)
        df["derived_liq_log"] = np.log1p(vol)
    else:
        df["derived_liq_log"] = np.nan

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["derived_candle_body_bps", "derived_range_bps", "derived_liq_log", "coin_ret3_bps"])

    raw_months = sorted(make_month(df["time"]).dropna().unique().tolist())
    canonical_months = raw_months[-12:] if len(raw_months) >= 12 else raw_months

    df["month"] = make_month(df["time"])
    df = df[df["month"].isin(canonical_months)]

    print(
        f"Building fixed market-state time frame: rows={len(df)}, symbols={df['symbol'].nunique()}, canonical_months={len(canonical_months)}",
        flush=True,
    )

    time_state = (
        df.groupby("time", as_index=False)
        .agg(
            body_median_bps=("derived_candle_body_bps", "median"),
            range_median_bps=("derived_range_bps", "median"),
            liq_median_log=("derived_liq_log", "median"),
            outcome_coin_ret3_median_bps=("coin_ret3_bps", "median"),
            symbol_count_at_time=("symbol", "nunique"),
        )
        .sort_values("time")
        .reset_index(drop=True)
    )

    time_state["month"] = make_month(time_state["time"])
    time_state = time_state[time_state["month"].isin(canonical_months)].copy()

    # Fixed tertile states. No post-hoc threshold expansion.
    time_state["body_state"] = assign_tertile(time_state["body_median_bps"])
    time_state["range_state"] = assign_tertile(time_state["range_median_bps"])
    time_state["liq_state"] = assign_tertile(time_state["liq_median_log"])

    time_state["composite_state"] = (
        "B:" + time_state["body_state"].astype(str)
        + "|R:" + time_state["range_state"].astype(str)
        + "|L:" + time_state["liq_state"].astype(str)
    )

    time_state["prev_composite_state"] = time_state["composite_state"].shift(1)
    time_state["prev_time"] = time_state["time"].shift(1)

    # Avoid transitions across missing/large gaps or month boundaries.
    delta_hours = (time_state["time"] - time_state["prev_time"]).dt.total_seconds() / 3600.0
    same_month = time_state["month"] == time_state["month"].shift(1)
    time_state["transition_label"] = np.where(
        (delta_hours <= 2.0) & same_month & time_state["prev_composite_state"].notna(),
        time_state["prev_composite_state"].astype(str) + " -> " + time_state["composite_state"].astype(str),
        np.nan,
    )

    valid = time_state.dropna(subset=["transition_label", "outcome_coin_ret3_median_bps"]).copy()

    meta = {
        "source_panel_path": str(panel_path),
        "raw_panel_row_count_after_clean": int(len(df)),
        "raw_symbol_count": int(df["symbol"].nunique()),
        "raw_calendar_month_count": int(len(raw_months)),
        "canonical_policy_month_count": int(len(canonical_months)),
        "canonical_months_rule": "last_12_calendar_months_deterministic_no_holdout",
        "canonical_months": canonical_months,
        "timestamp_count": int(len(time_state)),
        "valid_transition_timestamp_count": int(len(valid)),
        "unique_composite_state_count": int(time_state["composite_state"].nunique()),
        "unique_transition_label_count": int(valid["transition_label"].nunique()),
    }

    return valid, meta


def compute_omnibus_score(labels: np.ndarray, outcomes: np.ndarray, min_group_count: int = MIN_TRANSITION_GROUP_COUNT) -> Dict[str, Any]:
    tmp = pd.DataFrame({"label": labels, "outcome": outcomes})
    tmp = tmp.replace([np.inf, -np.inf], np.nan).dropna()
    if len(tmp) < min_group_count * 2:
        return {
            "score_eta2": 0.0,
            "group_count": 0,
            "used_group_count": 0,
            "sample_count": int(len(tmp)),
            "max_abs_group_mean_bps": 0.0,
            "overall_mean_bps": 0.0,
        }

    grp = tmp.groupby("label")["outcome"].agg(["count", "mean"])
    grp = grp[grp["count"] >= min_group_count]
    if len(grp) < 2:
        return {
            "score_eta2": 0.0,
            "group_count": int(tmp["label"].nunique()),
            "used_group_count": int(len(grp)),
            "sample_count": int(len(tmp)),
            "max_abs_group_mean_bps": float(grp["mean"].abs().max()) if len(grp) else 0.0,
            "overall_mean_bps": float(tmp["outcome"].mean()),
        }

    filtered = tmp[tmp["label"].isin(grp.index)].copy()
    overall = float(filtered["outcome"].mean())
    total_ss = float(((filtered["outcome"] - overall) ** 2).sum())
    if total_ss <= 0 or not math.isfinite(total_ss):
        eta2 = 0.0
    else:
        grp2 = filtered.groupby("label")["outcome"].agg(["count", "mean"])
        between_ss = float((grp2["count"] * ((grp2["mean"] - overall) ** 2)).sum())
        eta2 = max(0.0, between_ss / total_ss)

    return {
        "score_eta2": float(eta2),
        "group_count": int(tmp["label"].nunique()),
        "used_group_count": int(len(grp)),
        "sample_count": int(len(filtered)),
        "max_abs_group_mean_bps": float(grp["mean"].abs().max()),
        "overall_mean_bps": overall,
    }


def make_month_block_shuffle_y(y: np.ndarray, months: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    unique_months = list(dict.fromkeys(months.tolist()))
    blocks = [y[months == m].copy() for m in unique_months]
    perm = rng.permutation(len(blocks))
    y_null = np.concatenate([blocks[i] for i in perm])
    if len(y_null) != len(y):
        raise RuntimeError("month block shuffle length mismatch")
    return y_null


def make_within_month_shuffle_y(y: np.ndarray, months: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    y_null = y.copy()
    for m in np.unique(months):
        idx = np.where(months == m)[0]
        y_null[idx] = y_null[idx][rng.permutation(len(idx))]
    return y_null


def make_state_label_within_month_shuffle(labels: np.ndarray, months: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    labels_null = labels.copy()
    for m in np.unique(months):
        idx = np.where(months == m)[0]
        labels_null[idx] = labels_null[idx][rng.permutation(len(idx))]
    return labels_null


def run_nulls(valid: pd.DataFrame, observed_score: float) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    labels = valid["transition_label"].astype(str).to_numpy(copy=True)
    y = pd.to_numeric(valid["outcome_coin_ret3_median_bps"], errors="coerce").to_numpy(copy=True)
    months = valid["month"].astype(str).to_numpy(copy=True)

    rng = np.random.default_rng(RNG_SEED)
    null_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []

    print(
        f"Running restricted procedural nulls: models={len(NULL_MODELS)}, runs_per_model={RUNS_PER_NULL_MODEL}, observed_score={observed_score}",
        flush=True,
    )

    for model in NULL_MODELS:
        hits = 0
        scores: List[float] = []

        for run_id in range(1, RUNS_PER_NULL_MODEL + 1):
            if run_id == 1 or run_id % 100 == 0 or run_id == RUNS_PER_NULL_MODEL:
                print(f"RESTRICTED_RETEST_NULL_PROGRESS null_model={model} run={run_id}/{RUNS_PER_NULL_MODEL}", flush=True)

            null_labels = labels
            null_y = y

            if model == "month_block_shuffle":
                null_y = make_month_block_shuffle_y(y, months, rng)
            elif model == "time_block_shuffle":
                shift = int(rng.integers(1, len(y)))
                null_y = np.roll(y, shift)
            elif model == "state_label_within_month_shuffle":
                null_labels = make_state_label_within_month_shuffle(labels, months, rng)
            elif model == "within_month_outcome_shuffle":
                null_y = make_within_month_shuffle_y(y, months, rng)
            else:
                raise RuntimeError(f"unknown null model: {model}")

            score_info = compute_omnibus_score(null_labels, null_y)
            score = float(score_info["score_eta2"])
            scores.append(score)
            if score >= observed_score:
                hits += 1

            null_rows.append({
                "null_model": model,
                "run_id": run_id,
                "score_eta2": score,
                "ge_observed": score >= observed_score,
            })

        p_empirical = (hits + 1.0) / (RUNS_PER_NULL_MODEL + 1.0)
        min_resolvable_p = 1.0 / (RUNS_PER_NULL_MODEL + 1.0)

        summary_rows.append({
            "null_model": model,
            "runs": RUNS_PER_NULL_MODEL,
            "hits_ge_observed": hits,
            "p_empirical_plus_one": p_empirical,
            "min_resolvable_p_plus_one": min_resolvable_p,
            "null_score_mean": float(np.mean(scores)) if scores else 0.0,
            "null_score_p95": float(np.quantile(scores, 0.95)) if scores else 0.0,
            "null_score_max": float(np.max(scores)) if scores else 0.0,
        })

    return null_rows, summary_rows


def build_text(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS RESTRICTED MARKET-STATE STRUCTURE RETEST RUNNER v1")
    lines.append("=" * 100)

    for key in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "route_hash",
        "route_family",
        "alpha_budget",
        "route_budget",
        "source_row_count",
        "symbol_count",
        "canonical_policy_month_count",
        "timestamp_count",
        "valid_transition_timestamp_count",
        "unique_transition_label_count",
        "observed_score_eta2",
        "max_p_empirical_plus_one",
        "min_resolvable_p_plus_one",
        "alpha_resolution_pass",
        "restricted_retest_policy_gate_pass",
        "offline_research_execution_performed",
        "broad_strategy_search_allowed",
        "holdout_access_allowed",
        "candidate_generation_allowed",
        "family_release_allowed",
        "runtime_touch_allowed",
        "capital_change_allowed",
        "active_paper_allowed",
        "live_allowed",
        "real_orders_allowed",
        "next_recommended_research_key",
        "next_module",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("CORE DECISION")
    lines.append("-" * 100)
    lines.append("This was a single restricted offline retest, not strategy release.")
    lines.append("If alpha resolution is insufficient, the result is not validated even if null hits are low.")
    lines.append("No candidate, family release, runtime, capital, active paper, live, or real order action is allowed.")

    lines.append("")
    lines.append("NULL SUMMARY")
    lines.append("-" * 100)
    for row in result.get("null_summary_rows", []):
        lines.append(json.dumps(row, ensure_ascii=False))

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
        "summary_csv",
        "null_summary_csv",
        "retest_state_json",
        "budget_consumption_json",
        "next_queue_json",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS RESTRICTED MARKET-STATE STRUCTURE RETEST RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"route_hash: {result.get('route_hash')}")
    print(f"route_family: {result.get('route_family')}")
    print(f"alpha_budget: {result.get('alpha_budget')}")
    print(f"route_budget: {result.get('route_budget')}")
    print(f"source_row_count: {result.get('source_row_count')}")
    print(f"symbol_count: {result.get('symbol_count')}")
    print(f"canonical_policy_month_count: {result.get('canonical_policy_month_count')}")
    print(f"timestamp_count: {result.get('timestamp_count')}")
    print(f"valid_transition_timestamp_count: {result.get('valid_transition_timestamp_count')}")
    print(f"unique_transition_label_count: {result.get('unique_transition_label_count')}")
    print(f"observed_score_eta2: {result.get('observed_score_eta2')}")
    print(f"max_p_empirical_plus_one: {result.get('max_p_empirical_plus_one')}")
    print(f"min_resolvable_p_plus_one: {result.get('min_resolvable_p_plus_one')}")
    print(f"alpha_resolution_pass: {result.get('alpha_resolution_pass')}")
    print(f"restricted_retest_policy_gate_pass: {result.get('restricted_retest_policy_gate_pass')}")
    print(f"offline_research_execution_performed: {result.get('offline_research_execution_performed')}")
    print(f"next_recommended_research_key: {result.get('next_recommended_research_key')}")
    print(f"next_module: {result.get('next_module')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for key, value in SAFETY_FLAGS.items():
        print(f"{key}: {value}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('summary_csv')}")
    print(f"NULL: {result.get('null_summary_csv')}")
    print("=" * 100)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, {})
    execution_gate = load_json(EXECUTION_GATE_STATE_JSON, {})
    execution_policy = load_json(EXECUTION_POLICY_JSON, {})
    execution_queue = load_json(EXECUTION_NEXT_QUEUE_JSON, {})
    budget = load_json(BUDGET_ALLOCATION_JSON, {})
    holdout_registry = load_json(UNTOUCHED_HOLDOUT_REGISTRY_JSON, {})
    holdout_access = load_json(HOLDOUT_ACCESS_CONTROL_JSON, {})
    nested = load_json(NESTED_VALIDATION_POLICY_JSON, {})
    alpha_accounting = load_json(GLOBAL_ALPHA_ACCOUNTING_JSON, {})
    vault = load_json(PROMISING_VAULT_JSON, {})
    lessons = extract_list(load_json(LESSON_INDEX_JSON, {}), "lessons")
    blocked_routes = extract_list(load_json(BLOCKLIST_JSON, {}), "blocked_routes")
    vault_items = extract_list(vault, "vault_items")

    contract_id = contract.get("contract_id")
    route_hash = str(contract.get("route_hash") or "")
    route_family = str(contract.get("route_family") or "")
    route_is_blocked = route_hash_blocked(blocked_routes, route_hash)

    alpha_budget = finite_float(execution_gate.get("alpha_budget"), 0.0)
    route_budget = int(execution_gate.get("route_budget") or 0)

    prereq = {
        "execution_gate_pass": execution_gate.get("execution_gate_pass") is True,
        "restricted_runner_allowed": execution_gate.get("restricted_offline_research_runner_allowed") is True,
        "execution_policy_active": execution_policy.get("policy_status") == "RESTRICTED_RESEARCH_EXECUTION_POLICY_ACTIVE_OFFLINE_ONLY",
        "queue_ready": execution_queue.get("queue_status") == "RESTRICTED_RESEARCH_EXECUTION_NEXT_QUEUE_READY",
        "contract_ready": contract.get("contract_status") == "RESTRICTED_RESEARCH_CONTRACT_PROPOSAL_READY_NOT_EXECUTABLE",
        "route_hash_not_blocked": not route_is_blocked,
        "route_budget_one": route_budget == 1,
        "alpha_budget_positive": alpha_budget > 0.0,
        "holdout_not_selected": holdout_registry.get("holdout_selected") is False,
        "holdout_not_peeked": holdout_registry.get("holdout_peeked") is False,
        "holdout_access_forbidden": holdout_access.get("holdout_access_allowed_now") is False,
        "nested_ready": nested.get("policy_status") == "NESTED_VALIDATION_POLICY_READY_STRATEGY_SEARCH_LOCKED",
        "alpha_accounting_pass": alpha_accounting.get("global_alpha_accounting_pass") is True,
        "vault_active": vault.get("vault_status") == "PROMISING_SIGNAL_VAULT_ACTIVE_RELEASE_BLOCKED" and len(vault_items) >= 1,
        "source_panel_exists": SOURCE_PANEL_PATH.exists(),
    }

    if not all(prereq.values()):
        failed_prereq = [k for k, v in prereq.items() if not v]
        result = {
            "runner_name": "edge_factory_os_restricted_market_state_structure_retest_runner_v1",
            "created_at_utc": utc_now_iso(),
            "runner_status": "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_PREREQUISITES_NO_RELEASE",
            "reason": f"failed_prerequisites={failed_prereq}",
            "failed_prerequisites": failed_prereq,
            "contract_id": contract_id,
            "route_hash": route_hash,
            "route_family": route_family,
            "alpha_budget": alpha_budget,
            "route_budget": route_budget,
            "offline_research_execution_performed": False,
            "restricted_retest_policy_gate_pass": False,
            "next_recommended_research_key": None,
            "next_module": None,
            "output_json": str(OUT_JSON),
            "output_txt": str(OUT_TXT),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text(OUT_TXT, build_text(result))
        print_summary(result)
        return 2

    valid, meta = build_time_state_frame(SOURCE_PANEL_PATH)

    labels = valid["transition_label"].astype(str).to_numpy(copy=True)
    outcomes = pd.to_numeric(valid["outcome_coin_ret3_median_bps"], errors="coerce").to_numpy(copy=True)

    observed_info = compute_omnibus_score(labels, outcomes)
    observed_score = float(observed_info["score_eta2"])

    null_rows, null_summary_rows = run_nulls(valid, observed_score)

    max_p_empirical = max(float(row["p_empirical_plus_one"]) for row in null_summary_rows) if null_summary_rows else 1.0
    min_resolvable_p = min(float(row["min_resolvable_p_plus_one"]) for row in null_summary_rows) if null_summary_rows else 1.0

    alpha_resolution_pass = min_resolvable_p <= alpha_budget
    p_value_pass = max_p_empirical <= alpha_budget
    restricted_retest_policy_gate_pass = bool(alpha_resolution_pass and p_value_pass)

    if restricted_retest_policy_gate_pass:
        runner_status = "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_RUNNER_POLICY_GATE_PASS_RESEARCH_ONLY"
        reason = "restricted omnibus market-state retest passed empirical null and alpha resolution, research-only; no release allowed"
    elif not alpha_resolution_pass:
        runner_status = "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_RUNNER_UNDERPOWERED_FOR_TINY_ALPHA_NO_VALIDATION"
        reason = "null run count cannot resolve the tiny global alpha budget; result is not validated even if empirical hits are low"
    else:
        runner_status = "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_RUNNER_POLICY_GATE_FAIL_NO_VALIDATION"
        reason = "restricted omnibus market-state retest failed empirical procedural null gate"

    severity = "ATTENTION"
    allowed_scope = "OFFLINE_RESEARCH_ONLY"
    next_action = "BUILD_RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_EVALUATOR_NO_CANDIDATES_NO_RELEASE"

    summary_rows = [
        {
            "contract_id": contract_id,
            "route_hash": route_hash,
            "route_family": route_family,
            "alpha_budget": alpha_budget,
            "route_budget": route_budget,
            "observed_score_eta2": observed_score,
            "observed_group_count": observed_info.get("group_count"),
            "observed_used_group_count": observed_info.get("used_group_count"),
            "observed_sample_count": observed_info.get("sample_count"),
            "observed_max_abs_group_mean_bps": observed_info.get("max_abs_group_mean_bps"),
            "observed_overall_mean_bps": observed_info.get("overall_mean_bps"),
            "max_p_empirical_plus_one": max_p_empirical,
            "min_resolvable_p_plus_one": min_resolvable_p,
            "alpha_resolution_pass": alpha_resolution_pass,
            "p_value_pass": p_value_pass,
            "restricted_retest_policy_gate_pass": restricted_retest_policy_gate_pass,
            "source_row_count": meta.get("raw_panel_row_count_after_clean"),
            "symbol_count": meta.get("raw_symbol_count"),
            "timestamp_count": meta.get("timestamp_count"),
            "valid_transition_timestamp_count": meta.get("valid_transition_timestamp_count"),
            "unique_transition_label_count": meta.get("unique_transition_label_count"),
        }
    ]

    budget_consumption = {
        "consumption_name": "edge_factory_os_restricted_market_state_structure_retest_budget_consumption_v1",
        "created_at_utc": utc_now_iso(),
        "consumption_status": "RESTRICTED_RESEARCH_ROUTE_BUDGET_CONSUMED_ONCE",
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget_consumed": alpha_budget,
        "route_budget_consumed": 1,
        "offline_research_execution_performed": True,
        "trading_execution_performed": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        **SAFETY_FLAGS,
    }

    retest_state = {
        "state_name": "edge_factory_os_restricted_market_state_structure_retest_state_v1",
        "created_at_utc": utc_now_iso(),
        "runner_status": runner_status,
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget,
        "route_budget": route_budget,
        "observed_score_eta2": observed_score,
        "max_p_empirical_plus_one": max_p_empirical,
        "min_resolvable_p_plus_one": min_resolvable_p,
        "alpha_resolution_pass": alpha_resolution_pass,
        "p_value_pass": p_value_pass,
        "restricted_retest_policy_gate_pass": restricted_retest_policy_gate_pass,
        "offline_research_execution_performed": True,
        "broad_strategy_search_allowed": False,
        "holdout_access_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        **SAFETY_FLAGS,
    }

    next_queue = {
        "queue_name": "edge_factory_os_restricted_market_state_structure_retest_next_queue_v1",
        "created_at_utc": utc_now_iso(),
        "queue_status": "RESTRICTED_MARKET_STATE_STRUCTURE_RETEST_NEXT_QUEUE_READY",
        "top_next_research_key": NEXT_RESEARCH_KEY,
        "top_next_module": NEXT_MODULE,
        "research_execution_allowed_now": False,
        "candidate_generation_allowed": False,
        "family_release_allowed": False,
        "runtime_touch_allowed": False,
        "capital_change_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "real_orders_allowed": False,
        "next_steps": [
            {
                "research_key": NEXT_RESEARCH_KEY,
                "module": NEXT_MODULE,
                "priority": 100,
                "allowed_scope": "REPO_ONLY_OS_INTELLIGENCE",
                "purpose": "Evaluate restricted retest result and decide whether route is invalid, underpowered, or requires governance redesign.",
                "candidate_generation_allowed": False,
                "family_release_allowed": False,
                "runtime_touch_allowed": False,
                "capital_change_allowed": False,
                "active_paper_allowed": False,
                "live_allowed": False,
                "real_orders_allowed": False,
            }
        ],
        **SAFETY_FLAGS,
    }

    write_csv(OUT_SUMMARY_CSV, summary_rows)
    write_csv(OUT_NULL_CSV, null_summary_rows)
    write_json(REPO_RETEST_STATE_JSON, retest_state)
    write_json(REPO_BUDGET_CONSUMPTION_JSON, budget_consumption)
    write_json(REPO_NEXT_QUEUE_JSON, next_queue)

    result = {
        "runner_name": "edge_factory_os_restricted_market_state_structure_retest_runner_v1",
        "created_at_utc": utc_now_iso(),
        "runner_status": runner_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,
        "contract_id": contract_id,
        "route_hash": route_hash,
        "route_family": route_family,
        "alpha_budget": alpha_budget,
        "route_budget": route_budget,
        "source_row_count": meta.get("raw_panel_row_count_after_clean"),
        "symbol_count": meta.get("raw_symbol_count"),
        "raw_calendar_month_count": meta.get("raw_calendar_month_count"),
        "canonical_policy_month_count": meta.get("canonical_policy_month_count"),
        "canonical_months": meta.get("canonical_months"),
        "timestamp_count": meta.get("timestamp_count"),
        "valid_transition_timestamp_count": meta.get("valid_transition_timestamp_count"),
        "unique_composite_state_count": meta.get("unique_composite_state_count"),
        "unique_transition_label_count": meta.get("unique_transition_label_count"),
        "observed_score_eta2": observed_score,
        "observed_score_info": observed_info,
        "max_p_empirical_plus_one": max_p_empirical,
        "min_resolvable_p_plus_one": min_resolvable_p,
        "alpha_resolution_pass": alpha_resolution_pass,
        "p_value_pass": p_value_pass,
        "restricted_retest_policy_gate_pass": restricted_retest_policy_gate_pass,
        "null_model_count": len(NULL_MODELS),
        "runs_per_null_model": RUNS_PER_NULL_MODEL,
        "total_null_runs": len(NULL_MODELS) * RUNS_PER_NULL_MODEL,
        "null_summary_rows": null_summary_rows,
        "offline_research_execution_performed": True,
        "broad_strategy_search_allowed": False,
        "holdout_access_allowed": False,
        "next_recommended_research_key": NEXT_RESEARCH_KEY,
        "next_module": NEXT_MODULE,
        "retest_state": retest_state,
        "budget_consumption": budget_consumption,
        "next_queue": next_queue,
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "summary_csv": str(OUT_SUMMARY_CSV),
        "null_summary_csv": str(OUT_NULL_CSV),
        "retest_state_json": str(REPO_RETEST_STATE_JSON),
        "budget_consumption_json": str(REPO_BUDGET_CONSUMPTION_JSON),
        "next_queue_json": str(REPO_NEXT_QUEUE_JSON),
        **SAFETY_FLAGS,
    }

    write_json(OUT_JSON, result)
    write_text(OUT_TXT, build_text(result))
    print_summary(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
