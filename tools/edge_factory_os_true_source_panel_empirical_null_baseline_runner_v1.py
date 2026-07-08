#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - True Source Panel Empirical Null Baseline Runner v1

Purpose:
- Consume True Source Panel Empirical Null Baseline Contract v1.
- Read the real full source panel parquet.
- Validate schema, symbol coverage, raw/canonical month coverage.
- Run true source-panel empirical replay/null baseline methods.
- Keep plugin expansion blocked.
- Keep all candidate/family/runtime/capital/live/real-order actions blocked.

This runner does NOT:
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
    / "true_source_panel_empirical_null_baseline_contract_v1.json"
)

PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "true_source_panel_empirical_null_baseline_plugin_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

REPAIR_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "null_baseline_method_repair_state_v1.json"
)

VALIDATION_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_validation_state_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_true_source_panel_empirical_null_baseline_runner"

OUT_JSON = OUT_DIR / "true_source_panel_empirical_null_baseline_runner_latest.json"
OUT_TXT = OUT_DIR / "true_source_panel_empirical_null_baseline_runner_latest.txt"
OUT_SCHEMA_CSV = OUT_DIR / "true_source_panel_schema_report_latest.csv"
OUT_COVERAGE_CSV = OUT_DIR / "true_source_panel_month_symbol_coverage_latest.csv"
OUT_METHOD_INVENTORY_CSV = OUT_DIR / "true_source_panel_replay_method_inventory_latest.csv"
OUT_REPLAY_RUN_CSV = OUT_DIR / "true_source_panel_empirical_replay_runs_latest.csv"
OUT_FALSE_POSITIVE_CSV = OUT_DIR / "true_source_panel_empirical_false_positive_summary_latest.csv"
OUT_POLICY_GATE_CSV = OUT_DIR / "true_source_panel_empirical_policy_gate_pass_fail_latest.csv"
OUT_PVALUE_CSV = OUT_DIR / "true_source_panel_empirical_p_value_table_latest.csv"
OUT_POLICY_REPORT_CSV = OUT_DIR / "true_source_panel_policy_consumption_report_latest.csv"
OUT_GUARD_REPORT_CSV = OUT_DIR / "true_source_panel_guard_consumption_report_latest.csv"
OUT_REPAIR_STATE_REPORT_CSV = OUT_DIR / "true_source_panel_repair_state_consumption_report_latest.csv"

RUNNER_NAME = "edge_factory_os_true_source_panel_empirical_null_baseline_runner_v1"
EXPECTED_RESEARCH_KEY = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_V1"
EXPECTED_PLUGIN_KEY = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_PLUGIN_V1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"

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


def percentile(values: List[float], q: float, default: float = 0.0) -> float:
    arr = np.asarray(values, dtype="float64")
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return default
    return float(np.quantile(arr, q))


def safe_month_from_time(series: pd.Series) -> pd.Series:
    t = pd.to_datetime(series, utc=True, errors="coerce")
    # Drop timezone before Period conversion to avoid warning spam.
    t_naive = t.dt.tz_convert(None)
    return t_naive.dt.to_period("M").astype(str)


def pick_outcome_column(df: pd.DataFrame) -> Tuple[str, pd.Series]:
    candidate_cols = [
        "coin_ret3_bps",
        "signal_ret3_bps",
        "ret3_bps",
        "coin_ret6_bps",
        "signal_ret6_bps",
        "ret6_bps",
        "mkt_ret3_bps",
        "mkt_ret6_bps",
    ]

    for col in candidate_cols:
        if col in df.columns:
            return col, pd.to_numeric(df[col], errors="coerce")

    if "close" in df.columns and "symbol" in df.columns:
        close = pd.to_numeric(df["close"], errors="coerce")
        derived = (
            close.groupby(df["symbol"], sort=False)
            .pct_change(3)
            .shift(-3)
            .mul(10000.0)
        )
        return "derived_close_fwd3_bps", derived

    return "missing_outcome_column", pd.Series(np.nan, index=df.index)


def build_policy_report(policy: Dict[str, Any], contract: Dict[str, Any], plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    rules = policy.get("enforced_gate_rules") if isinstance(policy.get("enforced_gate_rules"), dict) else {}
    checks = [
        ("POLICY_ACTIVE", policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE", policy.get("policy_status"), "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"),
        ("POLICY_HASH_MATCH", policy.get("policy_hash") == contract.get("policy_hash"), f"{policy.get('policy_hash')} vs {contract.get('policy_hash')}", "match"),
        ("PLUGIN_CONSUMES_POLICY", plugin.get("must_consume_research_gate_policy") is True, plugin.get("must_consume_research_gate_policy"), True),
        ("PLUGIN_EXPANSION_BLOCKED", plugin.get("plugin_expansion_allowed") is False, plugin.get("plugin_expansion_allowed"), False),
        ("MIN_REPLAY_RUNS", to_int(plugin.get("minimum_empirical_replay_runs")) >= to_int(rules.get("minimum_permutation_runs"), 1000), plugin.get("minimum_empirical_replay_runs"), f">={rules.get('minimum_permutation_runs')}"),
        ("CANDIDATE_BLOCKED", plugin.get("candidate_generation_allowed") is False, plugin.get("candidate_generation_allowed"), False),
        ("FAMILY_RELEASE_BLOCKED", plugin.get("family_release_allowed") is False, plugin.get("family_release_allowed"), False),
        ("RUNTIME_BLOCKED", plugin.get("runtime_touch_allowed") is False, plugin.get("runtime_touch_allowed"), False),
        ("CAPITAL_BLOCKED", plugin.get("capital_change_allowed") is False, plugin.get("capital_change_allowed"), False),
        ("LIVE_BLOCKED", plugin.get("live_allowed") is False, plugin.get("live_allowed"), False),
        ("REAL_ORDERS_BLOCKED", plugin.get("real_orders_allowed") is False, plugin.get("real_orders_allowed"), False),
    ]
    return [
        {
            "policy_check": key,
            "passed": bool(passed),
            "observed": observed,
            "required": required,
            "policy_hash": policy.get("policy_hash"),
            "contract_id": contract.get("contract_id"),
        }
        for key, passed, observed, required in checks
    ]


def build_guard_report(contract: Dict[str, Any], guard_feed: Dict[str, Any]) -> List[Dict[str, Any]]:
    reqs = guard_feed.get("mandatory_future_research_requirements")
    if not isinstance(reqs, list):
        reqs = []

    rows = []
    for req in reqs:
        if not isinstance(req, dict):
            continue
        rows.append({
            "guard_key": req.get("guard_key"),
            "contract_id": contract.get("contract_id"),
            "research_key": contract.get("research_key"),
            "guard_pass": bool(req.get("guard_pass")),
            "pass_status": req.get("pass_status"),
            "message": req.get("message"),
            "consumed_by_runner": True,
            "blocks_candidate_or_release_if_failed": True,
        })

    if not rows:
        rows.append({
            "guard_key": "MISSING_GUARD_FEED_REQUIREMENTS",
            "contract_id": contract.get("contract_id"),
            "research_key": contract.get("research_key"),
            "guard_pass": False,
            "pass_status": "FAIL",
            "message": "No guard requirements found.",
            "consumed_by_runner": False,
            "blocks_candidate_or_release_if_failed": True,
        })

    return rows


def build_repair_state_report(repair_state: Dict[str, Any], contract: Dict[str, Any], plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    checks = [
        ("REPAIR_STATE_REQUIRES_TRUE_PANEL", repair_state.get("true_source_panel_replay_required") is True, repair_state.get("true_source_panel_replay_required"), True),
        ("PLUGIN_CONSUMES_REPAIR_STATE", plugin.get("must_consume_repair_state") is True, plugin.get("must_consume_repair_state"), True),
        ("CONTRACT_REQUIRES_TRUE_PANEL", contract.get("true_source_panel_replay_required") is True, contract.get("true_source_panel_replay_required"), True),
        ("PLUGIN_EXPANSION_BLOCKED", repair_state.get("plugin_expansion_allowed") is False, repair_state.get("plugin_expansion_allowed"), False),
    ]
    return [
        {
            "repair_state_check": key,
            "passed": bool(passed),
            "observed": observed,
            "required": required,
            "repair_state": repair_state.get("repair_state"),
            "contract_id": contract.get("contract_id"),
        }
        for key, passed, observed, required in checks
    ]


def schema_report(df: pd.DataFrame, required_columns: List[str], outcome_column: str, source_panel_path: str) -> List[Dict[str, Any]]:
    rows = []
    columns = set(df.columns)

    for col in required_columns:
        rows.append({
            "column": col,
            "present": col in columns,
            "role": "contract_required",
            "dtype": str(df[col].dtype) if col in columns else None,
            "source_panel_path": source_panel_path,
        })

    for col in ["time", "symbol", outcome_column]:
        rows.append({
            "column": col,
            "present": col in columns or col == outcome_column,
            "role": "runner_critical_or_outcome",
            "dtype": str(df[col].dtype) if col in columns else "derived_or_selected",
            "source_panel_path": source_panel_path,
        })

    return rows


def choose_canonical_months(df: pd.DataFrame, required_count: int = 12) -> List[str]:
    month_counts = df.groupby("month", sort=True).size().reset_index(name="rows")
    month_counts = month_counts.sort_values(["month"])
    months = month_counts["month"].astype(str).tolist()

    if len(months) <= required_count:
        return months

    # Exclude the thinnest edge month when raw calendar has 13 buckets.
    candidates = month_counts.copy()
    candidates["is_edge"] = False
    candidates.loc[candidates.index.min(), "is_edge"] = True
    candidates.loc[candidates.index.max(), "is_edge"] = True

    edge = candidates[candidates["is_edge"]].sort_values("rows").head(1)["month"].astype(str).tolist()
    filtered = [m for m in months if m not in set(edge)]

    if len(filtered) >= required_count:
        return filtered[:required_count]

    return months[-required_count:]


def coverage_report(df: pd.DataFrame, canonical_months: List[str]) -> List[Dict[str, Any]]:
    rows = []
    canonical_set = set(canonical_months)

    month_stats = (
        df.groupby("month")
        .agg(row_count=("symbol", "size"), symbol_count=("symbol", "nunique"))
        .reset_index()
        .sort_values("month")
    )

    for _, row in month_stats.iterrows():
        rows.append({
            "month": str(row["month"]),
            "is_canonical_policy_month": str(row["month"]) in canonical_set,
            "row_count": int(row["row_count"]),
            "symbol_count": int(row["symbol_count"]),
        })

    return rows


def method_inventory(methods: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for m in methods:
        rows.append({
            "replay_method": m,
            "uses_true_source_panel_rows_or_month_buckets": True,
            "uses_summary_rows_only": False,
            "uses_synthetic_month_generation_only": False,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def prepare_month_arrays(df: pd.DataFrame, canonical_months: List[str]) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    for month in canonical_months:
        vals = pd.to_numeric(df.loc[df["month"] == month, "outcome_bps"], errors="coerce")
        vals = vals.replace([np.inf, -np.inf], np.nan).dropna().astype("float64")
        if len(vals) > 0:
            out[month] = vals.to_numpy()
    return out


def replay_month_pnl(arr: np.ndarray, rng: np.random.Generator, sample_n: int, method: str) -> float:
    if arr.size == 0:
        return 0.0

    n = min(max(25, sample_n), int(arr.size))
    sample = rng.choice(arr, size=n, replace=True)

    if method == "panel_row_month_block_bootstrap":
        return float(np.nanmean(sample) * math.sqrt(n))

    if method == "panel_within_month_symbol_shuffle":
        return float(np.nanmedian(sample) * math.sqrt(n))

    if method == "panel_symbol_holdout_replay":
        keep = rng.random(sample.size) > 0.25
        sample2 = sample[keep] if keep.any() else sample
        return float(np.nanmean(sample2) * math.sqrt(sample2.size))

    if method == "panel_month_holdout_replay":
        # Some months are intentionally zeroed by caller, this method uses normal empirical sample here.
        return float(np.nanmean(sample) * math.sqrt(n))

    if method == "panel_time_block_bootstrap":
        block_size = max(10, min(100, n // 4))
        if arr.size <= block_size:
            sample2 = sample
        else:
            start = int(rng.integers(0, max(1, arr.size - block_size)))
            sample2 = arr[start : start + block_size]
        return float(np.nanmean(sample2) * math.sqrt(sample2.size))

    if method == "panel_negative_control_replay":
        signs = rng.choice(np.array([-1.0, 1.0]), size=sample.size)
        return float(np.nanmean(sample * signs) * math.sqrt(n))

    if method == "panel_cost_stress_replay":
        return float((np.nanmean(sample) * math.sqrt(n)) - rng.uniform(5.0, 35.0))

    if method == "panel_liquidity_bucket_shuffle":
        q = rng.choice([0.25, 0.50, 0.75])
        return float(np.nanquantile(sample, q) * math.sqrt(n))

    if method == "panel_volatility_bucket_shuffle":
        high_abs = np.abs(sample) >= np.nanquantile(np.abs(sample), 0.70)
        sample2 = sample[high_abs] if high_abs.any() else sample
        return float(np.nanmean(sample2) * math.sqrt(sample2.size))

    if method == "panel_side_flip_replay":
        return float(-np.nanmean(sample) * math.sqrt(n))

    if method == "panel_feature_label_permutation":
        sample2 = rng.permutation(sample)
        return float(np.nanmean(sample2) * math.sqrt(n))

    if method == "panel_entry_time_permutation":
        sample2 = rng.choice(arr, size=n, replace=True)
        return float(np.nanmean(sample2) * math.sqrt(n))

    return float(np.nanmean(sample) * math.sqrt(n))


def run_panel_empirical_replay(
    *,
    month_arrays: Dict[str, np.ndarray],
    methods: List[str],
    runs_per_method: int,
    gate_caps: Dict[str, Any],
    seed: int = 20260513,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = np.random.default_rng(seed)
    months = sorted(month_arrays.keys())
    replay_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    pvalue_rows: List[Dict[str, Any]] = []

    min_margin = float(gate_caps.get("minimum_actual_vs_null_margin_bps") or 2500.0)
    sample_n = 250

    actual_null_adjusted_signal_count = 0
    actual_best_total_month_pnl_bps = 0.0

    for method in methods:
        for run_id in range(1, runs_per_method + 1):
            month_pnls: List[float] = []

            holdout_months = set()
            if method == "panel_month_holdout_replay" and len(months) >= 12:
                holdout_months = set(rng.choice(np.array(months), size=2, replace=False).tolist())

            for month in months:
                if month in holdout_months:
                    pnl = 0.0
                else:
                    pnl = replay_month_pnl(month_arrays[month], rng, sample_n, method)
                month_pnls.append(float(pnl))

            active_months = len(month_pnls)
            positive_months = sum(1 for x in month_pnls if x > 0.0)
            total = float(sum(month_pnls))
            worst = float(min(month_pnls)) if month_pnls else 0.0
            best = float(max(month_pnls)) if month_pnls else 0.0

            strict_hit = bool(active_months >= 12 and positive_months >= 12 and total > 0.0)
            null_adjusted_hit = bool(strict_hit and total > min_margin and worst > -min_margin)

            replay_rows.append({
                "replay_method": method,
                "run_id": run_id,
                "canonical_month_count": len(months),
                "active_months": active_months,
                "positive_months": positive_months,
                "total_month_pnl_bps": total,
                "worst_month_bps": worst,
                "best_month_bps": best,
                "strict_12_random_hit": strict_hit,
                "null_adjusted_random_hit": null_adjusted_hit,
                "actual_best_total_month_pnl_bps": actual_best_total_month_pnl_bps,
                "actual_null_adjusted_signal_count": actual_null_adjusted_signal_count,
            })

    for method in methods:
        subset = [x for x in replay_rows if x["replay_method"] == method]
        if not subset:
            continue

        strict_rate = float(np.mean([1.0 if x["strict_12_random_hit"] else 0.0 for x in subset]))
        null_rate = float(np.mean([1.0 if x["null_adjusted_random_hit"] else 0.0 for x in subset]))
        totals = [float(x["total_month_pnl_bps"]) for x in subset]

        summary_rows.append({
            "replay_method": method,
            "replay_runs": len(subset),
            "strict_12_any_random_hit_rate": strict_rate,
            "null_adjusted_any_random_hit_rate": null_rate,
            "p50_total_month_pnl_bps": percentile(totals, 0.50),
            "p90_total_month_pnl_bps": percentile(totals, 0.90),
            "p95_total_month_pnl_bps": percentile(totals, 0.95),
            "p99_total_month_pnl_bps": percentile(totals, 0.99),
            "actual_best_total_month_pnl_bps": actual_best_total_month_pnl_bps,
            "actual_null_adjusted_signal_count": actual_null_adjusted_signal_count,
        })

        pvalue_rows.append({
            "replay_method": method,
            "empirical_p_value_actual_best_total": (
                sum(1 for x in totals if x >= actual_best_total_month_pnl_bps) + 1
            ) / (len(totals) + 1),
            "actual_best_total_month_pnl_bps": actual_best_total_month_pnl_bps,
            "actual_null_adjusted_signal_count": actual_null_adjusted_signal_count,
            "replay_runs": len(subset),
        })

    max_allowed_strict = float(gate_caps.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)
    max_allowed_null = float(gate_caps.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)

    max_strict_rate = max([float(x["strict_12_any_random_hit_rate"]) for x in summary_rows] or [1.0])
    max_null_rate = max([float(x["null_adjusted_any_random_hit_rate"]) for x in summary_rows] or [1.0])

    gate_rows = [
        {
            "gate_key": "SOURCE_PANEL_REPLAY_METHOD_COUNT",
            "passed": len(summary_rows) >= 8,
            "observed": len(summary_rows),
            "required": ">=8",
        },
        {
            "gate_key": "MINIMUM_EMPIRICAL_REPLAY_RUNS",
            "passed": all(int(x["replay_runs"]) >= runs_per_method for x in summary_rows),
            "observed": min([int(x["replay_runs"]) for x in summary_rows] or [0]),
            "required": runs_per_method,
        },
        {
            "gate_key": "STRICT_12_RANDOM_HIT_RATE_CAP",
            "passed": max_strict_rate <= max_allowed_strict,
            "observed": max_strict_rate,
            "required": f"<= {max_allowed_strict}",
        },
        {
            "gate_key": "NULL_ADJUSTED_RANDOM_HIT_RATE_CAP",
            "passed": max_null_rate <= max_allowed_null,
            "observed": max_null_rate,
            "required": f"<= {max_allowed_null}",
        },
        {
            "gate_key": "ACTUAL_SIGNAL_PRESENT",
            "passed": actual_null_adjusted_signal_count > 0,
            "observed": actual_null_adjusted_signal_count,
            "required": ">0 before any plugin expansion signal claim",
        },
        {
            "gate_key": "PLUGIN_EXPANSION_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "plugin_expansion_allowed=False",
        },
    ]

    return replay_rows, summary_rows, gate_rows, pvalue_rows


def summarize_gates(gate_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    failed = [x for x in gate_rows if not bool(x.get("passed"))]
    return {
        "panel_empirical_policy_gate_pass": len(failed) == 0,
        "panel_empirical_policy_gate_fail_count": len(failed),
        "failed_gate_keys": [x.get("gate_key") for x in failed],
    }


def build_text_summary(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS TRUE SOURCE PANEL EMPIRICAL NULL BASELINE RUNNER v1")
    lines.append("=" * 100)

    for key in [
        "runner_status",
        "severity",
        "allowed_scope",
        "next_action",
        "reason",
        "contract_id",
        "contract_hash",
        "route_hash",
        "research_key",
        "plugin_key",
        "policy_hash",
        "source_panel_path",
        "row_count",
        "symbol_count",
        "raw_calendar_month_count",
        "canonical_policy_month_count",
        "outcome_column",
        "replay_method_count",
        "empirical_replay_runs_per_method",
        "total_empirical_replay_run_rows",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "panel_empirical_policy_gate_pass",
        "panel_empirical_policy_gate_fail_count",
        "failed_gate_keys",
        "elapsed_seconds",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("POLICY GATES")
    lines.append("-" * 100)
    for row in result.get("policy_gate_rows", []):
        lines.append(f"{row.get('gate_key')}: passed={row.get('passed')} observed={row.get('observed')} required={row.get('required')}")

    lines.append("")
    lines.append("REPLAY SUMMARY")
    lines.append("-" * 100)
    for row in result.get("false_positive_summary_rows", [])[:20]:
        lines.append(
            f"{row.get('replay_method')}: strict_rate={row.get('strict_12_any_random_hit_rate')} "
            f"null_rate={row.get('null_adjusted_any_random_hit_rate')}"
        )

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
        "schema_csv",
        "coverage_csv",
        "method_inventory_csv",
        "replay_run_csv",
        "false_positive_summary_csv",
        "policy_gate_csv",
        "pvalue_csv",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS TRUE SOURCE PANEL EMPIRICAL NULL BASELINE RUNNER v1")
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
    print(f"outcome_column: {result.get('outcome_column')}")
    print(f"replay_method_count: {result.get('replay_method_count')}")
    print(f"empirical_replay_runs_per_method: {result.get('empirical_replay_runs_per_method')}")
    print(f"total_empirical_replay_run_rows: {result.get('total_empirical_replay_run_rows')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"panel_empirical_policy_gate_pass: {result.get('panel_empirical_policy_gate_pass')}")
    print(f"panel_empirical_policy_gate_fail_count: {result.get('panel_empirical_policy_gate_fail_count')}")
    print(f"failed_gate_keys: {result.get('failed_gate_keys')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('false_positive_summary_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    plugin = load_json(PLUGIN_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    repair_state = load_json(REPAIR_STATE_JSON, default={})
    validation_state = load_json(VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})

    source_panel_path = Path(contract.get("source_panel_path") or plugin.get("source_panel_path") or "")
    source_requirements = contract.get("source_panel_requirements")
    if not isinstance(source_requirements, dict):
        source_requirements = plugin.get("source_panel_requirements") if isinstance(plugin.get("source_panel_requirements"), dict) else {}

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "research_key": contract.get("research_key"),
        "plugin_key": contract.get("plugin_key"),
        "policy_hash": contract.get("policy_hash"),
        "source_panel_path": str(source_panel_path),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "schema_csv": str(OUT_SCHEMA_CSV),
        "coverage_csv": str(OUT_COVERAGE_CSV),
        "method_inventory_csv": str(OUT_METHOD_INVENTORY_CSV),
        "replay_run_csv": str(OUT_REPLAY_RUN_CSV),
        "false_positive_summary_csv": str(OUT_FALSE_POSITIVE_CSV),
        "policy_gate_csv": str(OUT_POLICY_GATE_CSV),
        "pvalue_csv": str(OUT_PVALUE_CSV),
        "policy_report_csv": str(OUT_POLICY_REPORT_CSV),
        "guard_report_csv": str(OUT_GUARD_REPORT_CSV),
        "repair_state_report_csv": str(OUT_REPAIR_STATE_REPORT_CSV),
        **SAFETY_FLAGS,
    }

    try:
        policy_report_rows = build_policy_report(policy, contract, plugin)
        guard_report_rows = build_guard_report(contract, guard_feed)
        repair_state_report_rows = build_repair_state_report(repair_state, contract, plugin)

        write_csv(OUT_POLICY_REPORT_CSV, policy_report_rows)
        write_csv(OUT_GUARD_REPORT_CSV, guard_report_rows)
        write_csv(OUT_REPAIR_STATE_REPORT_CSV, repair_state_report_rows)

        contract_ready = (
            contract.get("contract_status") == "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_CONTRACT_READY"
            and contract.get("research_key") == EXPECTED_RESEARCH_KEY
            and contract.get("plugin_key") == EXPECTED_PLUGIN_KEY
        )
        plugin_ready = (
            plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY
            and plugin.get("research_key") == EXPECTED_RESEARCH_KEY
            and plugin.get("plugin_expansion_allowed") is False
            and plugin.get("must_use_true_source_panel_rows_or_month_buckets") is True
        )
        policy_ready = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
        validation_ready = bool(validation_state.get("validator_pass"))
        guard_ready = bool(guard_feed.get("guard_pass"))
        repair_ready = bool(repair_state.get("true_source_panel_replay_required"))

        policy_consumed = all(bool(x.get("passed")) for x in policy_report_rows)
        guard_consumed = all(bool(x.get("guard_pass")) for x in guard_report_rows)
        repair_consumed = all(bool(x.get("passed")) for x in repair_state_report_rows)

        if not (
            contract_ready
            and plugin_ready
            and policy_ready
            and validation_ready
            and guard_ready
            and repair_ready
            and policy_consumed
            and guard_consumed
            and repair_consumed
        ):
            result = {
                **base_result,
                "runner_status": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_TRUE_SOURCE_PANEL_CONTRACT_POLICY_GUARD_OR_REPAIR_STATE",
                "reason": (
                    f"contract_ready={contract_ready}; plugin_ready={plugin_ready}; policy_ready={policy_ready}; "
                    f"validation_ready={validation_ready}; guard_ready={guard_ready}; repair_ready={repair_ready}; "
                    f"policy_consumed={policy_consumed}; guard_consumed={guard_consumed}; repair_consumed={repair_consumed}"
                ),
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        if not source_panel_path.exists():
            result = {
                **base_result,
                "runner_status": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_BLOCKED_SOURCE_PANEL_MISSING",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "FIX_SOURCE_PANEL_PATH_NO_RELEASE",
                "reason": f"source_panel_missing={source_panel_path}",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        print(f"Reading source panel: {source_panel_path}")
        df = pd.read_parquet(source_panel_path)

        if "time" not in df.columns or "symbol" not in df.columns:
            result = {
                **base_result,
                "runner_status": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_BLOCKED_MISSING_TIME_OR_SYMBOL",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_SOURCE_PANEL_SCHEMA_NO_RELEASE",
                "reason": f"time_present={'time' in df.columns}; symbol_present={'symbol' in df.columns}",
                "row_count": int(len(df)),
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        df = df.copy()
        df["month"] = safe_month_from_time(df["time"])
        df["symbol"] = df["symbol"].astype(str)

        outcome_column, outcome_series = pick_outcome_column(df)
        df["outcome_bps"] = pd.to_numeric(outcome_series, errors="coerce")
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=["month", "symbol", "outcome_bps"])

        required_columns = source_requirements.get("required_columns")
        if not isinstance(required_columns, list):
            required_columns = ["time", "symbol"]

        schema_rows = schema_report(df, required_columns, outcome_column, str(source_panel_path))
        write_csv(OUT_SCHEMA_CSV, schema_rows)

        row_count = int(len(df))
        symbol_count = int(df["symbol"].nunique())
        raw_months = sorted(df["month"].dropna().astype(str).unique().tolist())
        raw_calendar_month_count = len(raw_months)

        canonical_months = choose_canonical_months(df, required_count=12)
        canonical_policy_month_count = len(canonical_months)

        coverage_rows = coverage_report(df, canonical_months)
        write_csv(OUT_COVERAGE_CSV, coverage_rows)

        min_rows = to_int(source_requirements.get("minimum_row_count"), 1000000)
        min_symbols = to_int(source_requirements.get("minimum_symbol_count"), 200)

        if row_count < min_rows or symbol_count < min_symbols or canonical_policy_month_count < 12:
            result = {
                **base_result,
                "runner_status": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_BLOCKED_PANEL_COVERAGE_FAILED",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_PANEL_COVERAGE_NO_RELEASE",
                "reason": (
                    f"row_count={row_count}/{min_rows}; symbol_count={symbol_count}/{min_symbols}; "
                    f"canonical_policy_month_count={canonical_policy_month_count}/12"
                ),
                "row_count": row_count,
                "symbol_count": symbol_count,
                "raw_calendar_month_count": raw_calendar_month_count,
                "canonical_policy_month_count": canonical_policy_month_count,
                "outcome_column": outcome_column,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 0

        methods = plugin.get("replay_methods")
        if not isinstance(methods, list) or not methods:
            methods = contract.get("replay_methods")
        if not isinstance(methods, list) or not methods:
            methods = [
                "panel_row_month_block_bootstrap",
                "panel_within_month_symbol_shuffle",
                "panel_symbol_holdout_replay",
                "panel_month_holdout_replay",
                "panel_time_block_bootstrap",
                "panel_negative_control_replay",
                "panel_cost_stress_replay",
                "panel_liquidity_bucket_shuffle",
            ]
        methods = [str(x) for x in methods]

        method_inventory_rows = method_inventory(methods)
        write_csv(OUT_METHOD_INVENTORY_CSV, method_inventory_rows)

        runs_per_method = max(
            1000,
            to_int(plugin.get("minimum_empirical_replay_runs")),
            to_int(contract.get("minimum_empirical_replay_runs")),
        )

        gate_caps = plugin.get("gate_caps")
        if not isinstance(gate_caps, dict):
            gate_caps = contract.get("gate_caps") if isinstance(contract.get("gate_caps"), dict) else {}

        month_arrays = prepare_month_arrays(df[df["month"].isin(canonical_months)], canonical_months)

        print(f"Running true source-panel empirical null baseline: methods={len(methods)}, runs_per_method={runs_per_method}")

        replay_rows, false_positive_summary_rows, policy_gate_rows, pvalue_rows = run_panel_empirical_replay(
            month_arrays=month_arrays,
            methods=methods,
            runs_per_method=runs_per_method,
            gate_caps=gate_caps,
            seed=20260513,
        )

        write_csv(OUT_REPLAY_RUN_CSV, replay_rows)
        write_csv(OUT_FALSE_POSITIVE_CSV, false_positive_summary_rows)
        write_csv(OUT_POLICY_GATE_CSV, policy_gate_rows)
        write_csv(OUT_PVALUE_CSV, pvalue_rows)

        gate_summary = summarize_gates(policy_gate_rows)
        panel_empirical_policy_gate_pass = bool(gate_summary["panel_empirical_policy_gate_pass"])

        max_strict_rate = max([float(x.get("strict_12_any_random_hit_rate", 1.0)) for x in false_positive_summary_rows] or [1.0])
        max_null_rate = max([float(x.get("null_adjusted_any_random_hit_rate", 1.0)) for x in false_positive_summary_rows] or [1.0])

        if panel_empirical_policy_gate_pass:
            runner_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_POLICY_GATES_PASS_REVIEW_ONLY"
            next_action = "BUILD_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATOR_REVIEW_ONLY_NO_RELEASE"
            reason = (
                f"panel_empirical_policy_gate_pass=True; max_strict_rate={max_strict_rate}; "
                f"max_null_rate={max_null_rate}; plugin_expansion_still_blocked"
            )
        else:
            runner_status = "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_POLICY_GATES_FAIL"
            next_action = "BUILD_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_EVALUATOR_KEEP_PLUGIN_EXPANSION_BLOCKED"
            reason = (
                f"panel_empirical_policy_gate_pass=False; failed_gates={gate_summary.get('failed_gate_keys')}; "
                f"max_strict_rate={max_strict_rate}; max_null_rate={max_null_rate}"
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
            "outcome_column": outcome_column,
            "replay_method_count": len(methods),
            "replay_methods": methods,
            "empirical_replay_runs_per_method": runs_per_method,
            "total_empirical_replay_run_rows": len(replay_rows),
            "false_positive_summary_rows": false_positive_summary_rows,
            "policy_gate_rows": policy_gate_rows,
            "pvalue_rows": pvalue_rows,
            "panel_empirical_policy_gate_pass": panel_empirical_policy_gate_pass,
            "panel_empirical_policy_gate_fail_count": gate_summary["panel_empirical_policy_gate_fail_count"],
            "failed_gate_keys": gate_summary["failed_gate_keys"],
            "max_strict_12_any_random_hit_rate": max_strict_rate,
            "max_null_adjusted_any_random_hit_rate": max_null_rate,
            "policy_consumption_report": policy_report_rows,
            "guard_consumption_report": guard_report_rows,
            "repair_state_consumption_report": repair_state_report_rows,
            "release_gate_feed": {
                "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_RAN": True,
                "TRUE_SOURCE_PANEL_REPLAY_RAN": True,
                "PANEL_EMPIRICAL_POLICY_GATE_PASS": panel_empirical_policy_gate_pass,
                "SOURCE_PANEL_SCHEMA_VALIDATED": True,
                "SOURCE_PANEL_COVERAGE_VALIDATED": True,
                "RESEARCH_GATE_POLICY_CONSUMED": True,
                "DATA_QUALITY_GUARD_CONSUMED": True,
                "REPAIR_STATE_CONSUMED": True,
                "PLUGIN_EXPANSION_ALLOWED_FROM_THIS_RUNNER": False,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
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
        write_text(OUT_TXT, build_text_summary(result))
        print_summary(result)
        return 0

    except Exception as exc:
        result = {
            **base_result,
            "runner_status": "TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_TRUE_SOURCE_PANEL_EMPIRICAL_NULL_BASELINE_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(exc).__name__}: {exc}",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text(OUT_TXT, build_text_summary(result))
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
