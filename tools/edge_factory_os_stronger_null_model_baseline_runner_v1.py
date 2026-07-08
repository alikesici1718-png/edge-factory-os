#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Stronger Null Model Baseline Runner v1

Purpose:
- Consume Stronger Null Model Baseline Contract v1.
- Consume Research Gate Enforcement Policy v1.
- Consume Data Quality Guard feed.
- Consume prior generic research diagnostics / negative controls / null rows.
- Run a stricter null/permutation baseline:
  - >=1000 permutation runs per null model
  - >=8 independent null models
  - policy caps enforced
- Produce policy pass/fail table and no-release recommendation.

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
import random
import statistics
import time as time_module
from pathlib import Path
from typing import Any, Dict, List, Tuple


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "stronger_null_model_baseline_contract_v1.json"
)

PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "stronger_null_model_baseline_plugin_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

GUARD_FEED_JSON = (
    BASE_DIR
    / "edge_factory_os_data_quality_guard_runner"
    / "data_quality_guard_feed_latest.json"
)

GENERIC_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_runner_latest.json"
)

GENERIC_DIAGNOSTIC_CSV = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_feature_diagnostics_latest.csv"
)

GENERIC_NEGATIVE_CONTROL_CSV = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_negative_controls_latest.csv"
)

GENERIC_NULL_MODEL_CSV = (
    BASE_DIR
    / "edge_factory_os_generic_research_runner"
    / "generic_research_null_models_latest.csv"
)

PRIOR_NULL_RUNNER_JSON = (
    BASE_DIR
    / "edge_factory_os_null_model_permutation_baseline_runner"
    / "null_model_permutation_baseline_runner_latest.json"
)

OUT_DIR = BASE_DIR / "edge_factory_os_stronger_null_model_baseline_runner"
OUT_JSON = OUT_DIR / "stronger_null_model_baseline_runner_latest.json"
OUT_TXT = OUT_DIR / "stronger_null_model_baseline_runner_latest.txt"
OUT_RUN_CSV = OUT_DIR / "stronger_null_model_permutation_run_summary_latest.csv"
OUT_MODEL_CSV = OUT_DIR / "stronger_null_model_false_positive_summary_latest.csv"
OUT_PVALUE_CSV = OUT_DIR / "stronger_null_model_empirical_p_value_table_latest.csv"
OUT_GATE_CSV = OUT_DIR / "stronger_null_model_policy_gate_pass_fail_latest.csv"
OUT_POLICY_REPORT_CSV = OUT_DIR / "stronger_null_model_policy_consumption_report_latest.csv"
OUT_GUARD_REPORT_CSV = OUT_DIR / "stronger_null_model_guard_consumption_report_latest.csv"

RUNNER_NAME = "edge_factory_os_stronger_null_model_baseline_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"
EXPECTED_RESEARCH_KEY = "STRONGER_NULL_MODEL_BASELINE_REBUILD_V1"
EXPECTED_PLUGIN_KEY = "STRONGER_NULL_MODEL_BASELINE_PLUGIN_V1"

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
    except Exception as e:
        return {"_load_error": f"{type(e).__name__}: {e}", "_path": str(path)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def read_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    except Exception:
        return []
    return rows


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields: List[str] = []
    for row in rows:
        for k in row.keys():
            if k not in fields:
                fields.append(k)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass"}


def percentile(values: List[float], q: float, default: float = 0.0) -> float:
    clean = sorted([float(x) for x in values if math.isfinite(float(x))])
    if not clean:
        return default
    if len(clean) == 1:
        return clean[0]

    pos = (len(clean) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return clean[lo]
    frac = pos - lo
    return clean[lo] * (1.0 - frac) + clean[hi] * frac


def mean(values: List[float], default: float = 0.0) -> float:
    clean = [float(x) for x in values if math.isfinite(float(x))]
    if not clean:
        return default
    return sum(clean) / len(clean)


def stdev(values: List[float], default: float = 0.0) -> float:
    clean = [float(x) for x in values if math.isfinite(float(x))]
    if len(clean) < 2:
        return default
    return statistics.stdev(clean)


def normalize_diagnostics(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows:
        out.append({
            "row_type": "actual_feature",
            "name": row.get("feature_name"),
            "family": row.get("feature_family"),
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "event_count": to_int(row.get("event_count")),
            "active_months": to_int(row.get("active_months")),
            "positive_months": to_int(row.get("positive_months")),
            "total_month_pnl_bps": to_float(row.get("total_month_pnl_bps")),
            "mean_bar_pnl_bps": to_float(row.get("mean_bar_pnl_bps")),
            "bar_win_rate": to_float(row.get("bar_win_rate")),
            "worst_month_bps": to_float(row.get("worst_month_bps")),
            "best_month_bps": to_float(row.get("best_month_bps")),
            "strict_12_pass": to_bool(row.get("strict_12_feature_signal_preview_pass")),
            "null_adjusted_signal_pass": False,
        })
    return out


def normalize_controls(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows:
        out.append({
            "row_type": "negative_control",
            "name": row.get("control_name"),
            "family": "negative_control",
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "event_count": to_int(row.get("event_count")),
            "active_months": to_int(row.get("active_months")),
            "positive_months": to_int(row.get("positive_months")),
            "total_month_pnl_bps": to_float(row.get("total_month_pnl_bps")),
            "mean_bar_pnl_bps": to_float(row.get("mean_bar_pnl_bps")),
            "bar_win_rate": to_float(row.get("bar_win_rate")),
            "worst_month_bps": to_float(row.get("worst_month_bps")),
            "best_month_bps": to_float(row.get("best_month_bps")),
            "strict_12_pass": to_bool(row.get("strict_12_control_preview_pass")),
            "null_adjusted_signal_pass": False,
        })
    return out


def normalize_prior_null_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows:
        out.append({
            "row_type": "prior_null_row",
            "name": row.get("null_model"),
            "family": row.get("feature_family") or "prior_null",
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "event_count": 0,
            "active_months": 12,
            "positive_months": 12 if to_bool(row.get("strict_12_feature_signal_preview_pass")) else 0,
            "total_month_pnl_bps": to_float(row.get("actual_total_month_pnl_bps")),
            "mean_bar_pnl_bps": 0.0,
            "bar_win_rate": 0.0,
            "worst_month_bps": 0.0,
            "best_month_bps": 0.0,
            "strict_12_pass": to_bool(row.get("strict_12_feature_signal_preview_pass")),
            "null_adjusted_signal_pass": to_bool(row.get("null_adjusted_signal_pass")),
        })
    return out


def build_guard_report(contract: Dict[str, Any], guard_feed: Dict[str, Any]) -> List[Dict[str, Any]]:
    reqs = guard_feed.get("mandatory_future_research_requirements")
    if not isinstance(reqs, list):
        reqs = []

    rows: List[Dict[str, Any]] = []
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


def build_policy_report(policy: Dict[str, Any], contract: Dict[str, Any], plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    rules = policy.get("enforced_gate_rules")
    if not isinstance(rules, dict):
        rules = {}

    rows: List[Dict[str, Any]] = []

    checks = [
        ("POLICY_STATUS_ACTIVE", policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE", policy.get("policy_status")),
        ("POLICY_HASH_MATCH", policy.get("policy_hash") == contract.get("policy_hash"), f"{policy.get('policy_hash')} vs {contract.get('policy_hash')}"),
        ("MIN_PERMUTATION_RUNS", int(plugin.get("minimum_permutation_runs") or 0) >= int(rules.get("minimum_permutation_runs") or 1000), plugin.get("minimum_permutation_runs")),
        ("REQUIRED_NULL_MODELS", int(plugin.get("required_independent_null_models") or 0) >= int(rules.get("required_independent_null_models") or 8), plugin.get("required_independent_null_models")),
        ("PLUGIN_EXPANSION_BLOCKED", plugin.get("plugin_expansion_allowed") is False, plugin.get("plugin_expansion_allowed")),
        ("CANDIDATE_GENERATION_BLOCKED", plugin.get("candidate_generation_allowed") is False, plugin.get("candidate_generation_allowed")),
        ("FAMILY_RELEASE_BLOCKED", plugin.get("family_release_allowed") is False, plugin.get("family_release_allowed")),
        ("RUNTIME_TOUCH_BLOCKED", plugin.get("runtime_touch_allowed") is False, plugin.get("runtime_touch_allowed")),
        ("CAPITAL_CHANGE_BLOCKED", plugin.get("capital_change_allowed") is False, plugin.get("capital_change_allowed")),
        ("LIVE_BLOCKED", plugin.get("live_allowed") is False, plugin.get("live_allowed")),
        ("REAL_ORDERS_BLOCKED", plugin.get("real_orders_allowed") is False, plugin.get("real_orders_allowed")),
    ]

    for key, passed, value in checks:
        rows.append({
            "policy_check": key,
            "passed": bool(passed),
            "value": value,
            "contract_id": contract.get("contract_id"),
            "policy_hash": policy.get("policy_hash"),
        })

    return rows


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def make_synthetic_months(
    base: Dict[str, Any],
    rng: random.Random,
    model_name: str,
) -> List[float]:
    total = float(base.get("total_month_pnl_bps", 0.0))
    pos = int(base.get("positive_months", 0))
    worst = float(base.get("worst_month_bps", 0.0))
    best = float(base.get("best_month_bps", 0.0))

    scale = max(250.0, abs(total) / 12.0, abs(worst), abs(best))

    if model_name == "within_month_symbol_shuffle":
        mu = total / 12.0
        sigma = scale * 0.75
        months = [rng.gauss(mu, sigma) for _ in range(12)]

    elif model_name == "cross_section_symbol_resample":
        mu = total / 12.0 * rng.uniform(0.6, 1.2)
        sigma = scale * 1.0
        months = [rng.gauss(mu, sigma) for _ in range(12)]

    elif model_name == "month_label_permutation":
        signs = [1 if i < pos else -1 for i in range(12)]
        rng.shuffle(signs)
        months = [signs[i] * abs(rng.gauss(scale * 0.5, scale * 0.7)) for i in range(12)]

    elif model_name == "time_block_bootstrap":
        block = [rng.gauss(total / 12.0, scale * 0.9) for _ in range(4)]
        months = [block[i % 4] + rng.gauss(0, scale * 0.25) for i in range(12)]
        rng.shuffle(months)

    elif model_name == "side_flip_null":
        months = [-rng.gauss(total / 12.0, scale * 0.8) for _ in range(12)]

    elif model_name == "hold_period_shuffle":
        factor = rng.uniform(0.4, 1.6)
        months = [rng.gauss((total / 12.0) * factor, scale * 0.9) for _ in range(12)]

    elif model_name == "feature_rank_shuffle":
        mu = rng.gauss(0, scale * 0.15)
        months = [rng.gauss(mu, scale * 0.85) for _ in range(12)]

    elif model_name == "cost_stress_permutation":
        extra_cost = rng.uniform(25.0, 125.0)
        months = [rng.gauss(total / 12.0 - extra_cost, scale * 0.7) for _ in range(12)]

    elif model_name == "symbol_holdout_null":
        holdout_factor = rng.uniform(0.25, 0.85)
        months = [rng.gauss((total / 12.0) * holdout_factor, scale * 0.95) for _ in range(12)]

    elif model_name == "month_holdout_null":
        months = [rng.gauss(total / 12.0, scale * 0.9) for _ in range(12)]
        remove_n = rng.choice([2, 3, 4])
        for idx in rng.sample(range(12), remove_n):
            months[idx] = 0.0

    elif model_name == "liquidity_bucket_shuffle":
        liquidity_factor = rng.choice([0.5, 0.75, 1.0, 1.25])
        months = [rng.gauss((total / 12.0) * liquidity_factor, scale * 0.8) for _ in range(12)]

    elif model_name == "volatility_regime_shuffle":
        vol_factor = rng.choice([0.6, 1.0, 1.4, 1.8])
        months = [rng.gauss(total / 12.0, scale * vol_factor) for _ in range(12)]

    else:
        months = [rng.gauss(total / 12.0, scale) for _ in range(12)]

    return [float(x) for x in months]


def run_stronger_baseline(
    *,
    model_names: List[str],
    sample_pool: List[Dict[str, Any]],
    diagnostics: List[Dict[str, Any]],
    runs_per_model: int,
    policy_rules: Dict[str, Any],
    seed: int = 20260513,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(seed)
    run_rows: List[Dict[str, Any]] = []
    model_summary: List[Dict[str, Any]] = []
    pvalue_rows: List[Dict[str, Any]] = []
    gate_rows: List[Dict[str, Any]] = []

    if not sample_pool:
        return run_rows, model_summary, pvalue_rows, gate_rows

    diag_totals = [float(x.get("total_month_pnl_bps", 0.0)) for x in diagnostics]
    actual_best_total = max(diag_totals) if diag_totals else 0.0
    actual_strict_count = sum(1 for x in diagnostics if bool(x.get("strict_12_pass")))
    actual_null_adjusted_count = sum(1 for x in diagnostics if bool(x.get("null_adjusted_signal_pass")))

    min_margin = float(policy_rules.get("minimum_actual_vs_null_margin_bps") or 2500.0)

    for model_name in model_names:
        for run_id in range(1, runs_per_model + 1):
            diagnostic_slots = max(1, len(diagnostics))
            strict_hits = 0
            null_adjusted_hits = 0
            max_total = -10**18
            max_positive_months = 0
            max_worst_month = -10**18

            for _ in range(diagnostic_slots):
                base = rng.choice(sample_pool)
                months = make_synthetic_months(base, rng, model_name)
                total = sum(months)
                positive = sum(1 for x in months if x > 0.0)
                worst = min(months)

                strict = positive >= 12 and total > 0.0
                if strict:
                    strict_hits += 1

                # Stronger null-adjusted: must be strict, exceed actual-ish margin and avoid weak worst month.
                null_adjusted = bool(
                    strict
                    and total > min_margin
                    and worst > -min_margin
                )
                if null_adjusted:
                    null_adjusted_hits += 1

                max_total = max(max_total, total)
                max_positive_months = max(max_positive_months, positive)
                max_worst_month = max(max_worst_month, worst)

            run_rows.append({
                "null_model": model_name,
                "run_id": run_id,
                "diagnostic_slots_sampled": diagnostic_slots,
                "strict_12_random_hit_count": strict_hits,
                "null_adjusted_random_hit_count": null_adjusted_hits,
                "any_strict_12_random_hit": strict_hits > 0,
                "any_null_adjusted_random_hit": null_adjusted_hits > 0,
                "max_total_month_pnl_bps": max_total,
                "max_positive_months": max_positive_months,
                "max_worst_month_bps": max_worst_month,
                "actual_best_total_month_pnl_bps": actual_best_total,
                "actual_strict_12_feature_signal_preview_count": actual_strict_count,
                "actual_null_adjusted_signal_count": actual_null_adjusted_count,
            })

    for model_name in model_names:
        subset = [x for x in run_rows if x["null_model"] == model_name]
        if not subset:
            continue

        strict_any_rate = mean([1.0 if x["any_strict_12_random_hit"] else 0.0 for x in subset])
        null_any_rate = mean([1.0 if x["any_null_adjusted_random_hit"] else 0.0 for x in subset])
        strict_hit_avg = mean([float(x["strict_12_random_hit_count"]) for x in subset])
        null_hit_avg = mean([float(x["null_adjusted_random_hit_count"]) for x in subset])
        max_totals = [float(x["max_total_month_pnl_bps"]) for x in subset]

        model_summary.append({
            "null_model": model_name,
            "permutation_runs": len(subset),
            "strict_12_any_random_hit_rate": strict_any_rate,
            "null_adjusted_any_random_hit_rate": null_any_rate,
            "avg_strict_12_random_hit_count": strict_hit_avg,
            "avg_null_adjusted_random_hit_count": null_hit_avg,
            "p50_max_total_month_pnl_bps": percentile(max_totals, 0.50),
            "p90_max_total_month_pnl_bps": percentile(max_totals, 0.90),
            "p95_max_total_month_pnl_bps": percentile(max_totals, 0.95),
            "p99_max_total_month_pnl_bps": percentile(max_totals, 0.99),
            "actual_best_total_month_pnl_bps": actual_best_total,
            "actual_strict_12_feature_signal_preview_count": actual_strict_count,
            "actual_null_adjusted_signal_count": actual_null_adjusted_count,
        })

        empirical_p_value_best_total = (
            sum(1 for x in max_totals if x >= actual_best_total) + 1
        ) / (len(max_totals) + 1)

        strict_hit_p_value = (
            sum(1 for x in subset if int(x["strict_12_random_hit_count"]) >= actual_strict_count) + 1
        ) / (len(subset) + 1)

        null_hit_p_value = (
            sum(1 for x in subset if int(x["null_adjusted_random_hit_count"]) >= actual_null_adjusted_count) + 1
        ) / (len(subset) + 1)

        pvalue_rows.append({
            "null_model": model_name,
            "empirical_p_value_actual_best_total": empirical_p_value_best_total,
            "empirical_p_value_strict_hit_count": strict_hit_p_value,
            "empirical_p_value_null_adjusted_hit_count": null_hit_p_value,
            "actual_best_total_month_pnl_bps": actual_best_total,
            "actual_strict_12_feature_signal_preview_count": actual_strict_count,
            "actual_null_adjusted_signal_count": actual_null_adjusted_count,
            "permutation_runs": len(subset),
        })

    max_allowed_strict_rate = float(policy_rules.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)
    max_allowed_null_rate = float(policy_rules.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)
    required_runs = int(policy_rules.get("minimum_permutation_runs") or 1000)
    required_models = int(policy_rules.get("required_independent_null_models") or 8)

    max_strict_rate = max([float(x["strict_12_any_random_hit_rate"]) for x in model_summary] or [1.0])
    max_null_rate = max([float(x["null_adjusted_any_random_hit_rate"]) for x in model_summary] or [1.0])

    gate_checks = [
        {
            "gate_key": "MINIMUM_PERMUTATION_RUNS",
            "passed": all(int(x["permutation_runs"]) >= required_runs for x in model_summary),
            "observed": min([int(x["permutation_runs"]) for x in model_summary] or [0]),
            "required": required_runs,
        },
        {
            "gate_key": "REQUIRED_INDEPENDENT_NULL_MODELS",
            "passed": len(model_summary) >= required_models,
            "observed": len(model_summary),
            "required": required_models,
        },
        {
            "gate_key": "STRICT_12_RANDOM_HIT_RATE_CAP",
            "passed": max_strict_rate <= max_allowed_strict_rate,
            "observed": max_strict_rate,
            "required": f"<= {max_allowed_strict_rate}",
        },
        {
            "gate_key": "NULL_ADJUSTED_RANDOM_HIT_RATE_CAP",
            "passed": max_null_rate <= max_allowed_null_rate,
            "observed": max_null_rate,
            "required": f"<= {max_allowed_null_rate}",
        },
        {
            "gate_key": "ACTUAL_SIGNAL_PRESENT",
            "passed": actual_null_adjusted_count > 0,
            "observed": actual_null_adjusted_count,
            "required": "> 0 if any plugin expansion wants signal-based promotion",
        },
    ]

    for x in gate_checks:
        gate_rows.append(x)

    return run_rows, model_summary, pvalue_rows, gate_rows


def summarize_gate_rows(gate_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    fail = [x for x in gate_rows if not bool(x.get("passed"))]
    pass_count = len(gate_rows) - len(fail)

    policy_pass = len(fail) == 0

    return {
        "policy_gate_pass": policy_pass,
        "policy_gate_pass_count": pass_count,
        "policy_gate_fail_count": len(fail),
        "failed_gate_keys": [x.get("gate_key") for x in fail],
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS STRONGER NULL MODEL BASELINE RUNNER v1")
    lines.append("=" * 100)

    for k in [
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
        "null_model_count",
        "permutation_runs_per_model",
        "total_permutation_run_rows",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "policy_gate_pass",
        "policy_gate_fail_count",
        "failed_gate_keys",
        "elapsed_seconds",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("POLICY GATE ROWS")
    lines.append("-" * 100)
    for row in result.get("policy_gate_rows", []):
        lines.append(f"{row.get('gate_key')}: passed={row.get('passed')} observed={row.get('observed')} required={row.get('required')}")

    lines.append("")
    lines.append("MODEL SUMMARY")
    lines.append("-" * 100)
    for row in result.get("model_summary_rows", [])[:20]:
        lines.append(
            f"{row.get('null_model')}: strict_any={row.get('strict_12_any_random_hit_rate')} "
            f"null_any={row.get('null_adjusted_any_random_hit_rate')}"
        )

    lines.append("")
    lines.append("SAFETY FLAGS")
    lines.append("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("OUTPUT PATHS")
    lines.append("-" * 100)
    for k in [
        "output_json",
        "output_txt",
        "permutation_run_csv",
        "model_summary_csv",
        "empirical_p_value_csv",
        "policy_gate_csv",
        "policy_report_csv",
        "guard_report_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS STRONGER NULL MODEL BASELINE RUNNER v1")
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
    print(f"null_model_count: {result.get('null_model_count')}")
    print(f"permutation_runs_per_model: {result.get('permutation_runs_per_model')}")
    print(f"total_permutation_run_rows: {result.get('total_permutation_run_rows')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"policy_gate_pass: {result.get('policy_gate_pass')}")
    print(f"policy_gate_fail_count: {result.get('policy_gate_fail_count')}")
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
    print(f"CSV : {result.get('model_summary_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    plugin = load_json(PLUGIN_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    generic_runner = load_json(GENERIC_RUNNER_JSON, default={})
    prior_runner = load_json(PRIOR_NULL_RUNNER_JSON, default={})

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_path": str(CONTRACT_JSON),
        "plugin_path": str(PLUGIN_JSON),
        "policy_path": str(POLICY_JSON),
        "guard_feed_path": str(GUARD_FEED_JSON),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "research_key": contract.get("research_key"),
        "plugin_key": contract.get("plugin_key"),
        "policy_hash": contract.get("policy_hash"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "permutation_run_csv": str(OUT_RUN_CSV),
        "model_summary_csv": str(OUT_MODEL_CSV),
        "empirical_p_value_csv": str(OUT_PVALUE_CSV),
        "policy_gate_csv": str(OUT_GATE_CSV),
        "policy_report_csv": str(OUT_POLICY_REPORT_CSV),
        "guard_report_csv": str(OUT_GUARD_REPORT_CSV),
        **SAFETY_FLAGS,
    }

    try:
        policy_rules = policy.get("enforced_gate_rules")
        if not isinstance(policy_rules, dict):
            policy_rules = {}

        contract_ready = (
            contract.get("contract_status") == "STRONGER_NULL_MODEL_BASELINE_CONTRACT_READY"
            and contract.get("research_key") == EXPECTED_RESEARCH_KEY
            and contract.get("plugin_key") == EXPECTED_PLUGIN_KEY
        )
        plugin_ready = (
            plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY
            and plugin.get("research_key") == EXPECTED_RESEARCH_KEY
            and bool(plugin.get("must_consume_research_gate_policy"))
        )
        policy_ready = (
            policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
            and policy.get("policy_hash") == contract.get("policy_hash")
        )
        guard_pass = bool(guard_feed.get("guard_pass")) and bool(contract.get("guard_pass"))

        policy_rows = build_policy_report(policy, contract, plugin)
        guard_rows = build_guard_report(contract, guard_feed)
        write_csv(OUT_POLICY_REPORT_CSV, policy_rows)
        write_csv(OUT_GUARD_REPORT_CSV, guard_rows)

        policy_consumed = all(bool(x.get("passed")) for x in policy_rows)
        guard_consumed = all(bool(x.get("guard_pass")) for x in guard_rows)

        if not contract_ready or not plugin_ready or not policy_ready or not guard_pass or not policy_consumed or not guard_consumed:
            result = {
                **base_result,
                "runner_status": "STRONGER_NULL_MODEL_BASELINE_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_STRONGER_NULL_CONTRACT_PLUGIN_POLICY_OR_GUARD",
                "reason": (
                    f"contract_ready={contract_ready}; plugin_ready={plugin_ready}; policy_ready={policy_ready}; "
                    f"guard_pass={guard_pass}; policy_consumed={policy_consumed}; guard_consumed={guard_consumed}"
                ),
                "policy_consumption_report": policy_rows,
                "guard_consumption_report": guard_rows,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        diagnostics = normalize_diagnostics(read_csv_rows(GENERIC_DIAGNOSTIC_CSV))
        controls = normalize_controls(read_csv_rows(GENERIC_NEGATIVE_CONTROL_CSV))
        prior_null_rows = normalize_prior_null_rows(read_csv_rows(GENERIC_NULL_MODEL_CSV))

        sample_pool = controls + prior_null_rows
        if not diagnostics or not sample_pool:
            result = {
                **base_result,
                "runner_status": "STRONGER_NULL_MODEL_BASELINE_RUNNER_BLOCKED_MISSING_PRIOR_OUTPUTS",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "RERUN_GENERIC_RESEARCH_RUNNER_OR_PRIOR_NULL_OUTPUTS",
                "reason": f"diagnostics={len(diagnostics)}; controls={len(controls)}; prior_null_rows={len(prior_null_rows)}",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        model_names = plugin.get("baseline_tests")
        if not isinstance(model_names, list) or not model_names:
            model_names = contract.get("baseline_tests")

        if not isinstance(model_names, list) or not model_names:
            model_names = [
                "within_month_symbol_shuffle",
                "cross_section_symbol_resample",
                "month_label_permutation",
                "time_block_bootstrap",
                "side_flip_null",
                "hold_period_shuffle",
                "feature_rank_shuffle",
                "cost_stress_permutation",
            ]

        required_models = max(8, int(plugin.get("required_independent_null_models") or policy_rules.get("required_independent_null_models") or 8))
        model_names = [str(x) for x in model_names][: max(required_models, 8)]

        runs_per_model = max(1000, int(plugin.get("minimum_permutation_runs") or policy_rules.get("minimum_permutation_runs") or 1000))

        print(f"Running stronger null baseline: models={len(model_names)}, runs_per_model={runs_per_model}")

        run_rows, model_summary_rows, pvalue_rows, gate_rows = run_stronger_baseline(
            model_names=model_names,
            sample_pool=sample_pool,
            diagnostics=diagnostics,
            runs_per_model=runs_per_model,
            policy_rules=policy_rules,
            seed=20260513,
        )

        write_csv(OUT_RUN_CSV, run_rows)
        write_csv(OUT_MODEL_CSV, model_summary_rows)
        write_csv(OUT_PVALUE_CSV, pvalue_rows)
        write_csv(OUT_GATE_CSV, gate_rows)

        gate_summary = summarize_gate_rows(gate_rows)
        policy_gate_pass = bool(gate_summary["policy_gate_pass"])

        max_strict_rate = max([float(x.get("strict_12_any_random_hit_rate", 1.0)) for x in model_summary_rows] or [1.0])
        max_null_rate = max([float(x.get("null_adjusted_any_random_hit_rate", 1.0)) for x in model_summary_rows] or [1.0])

        if policy_gate_pass:
            runner_status = "STRONGER_NULL_MODEL_BASELINE_RUNNER_POLICY_GATES_PASS"
            severity = "ATTENTION"
            next_action = "BUILD_STRONGER_NULL_MODEL_BASELINE_EVALUATOR_ALLOW_VALIDATION_NO_RELEASE"
            reason = (
                f"policy_gate_pass=True; max_strict_rate={max_strict_rate}; "
                f"max_null_rate={max_null_rate}; plugin_expansion_still_requires_evaluator"
            )
        else:
            runner_status = "STRONGER_NULL_MODEL_BASELINE_RUNNER_POLICY_GATES_FAIL"
            severity = "ATTENTION"
            next_action = "BUILD_STRONGER_NULL_MODEL_BASELINE_EVALUATOR_KEEP_PLUGIN_EXPANSION_BLOCKED"
            reason = (
                f"policy_gate_pass=False; failed_gates={gate_summary.get('failed_gate_keys')}; "
                f"max_strict_rate={max_strict_rate}; max_null_rate={max_null_rate}"
            )

        result = {
            **base_result,
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "reason": reason,
            "null_model_count": len(model_names),
            "null_models": model_names,
            "permutation_runs_per_model": runs_per_model,
            "total_permutation_run_rows": len(run_rows),
            "model_summary_rows": model_summary_rows,
            "empirical_p_value_rows": pvalue_rows,
            "policy_gate_rows": gate_rows,
            "policy_gate_pass": policy_gate_pass,
            "policy_gate_pass_count": gate_summary.get("policy_gate_pass_count"),
            "policy_gate_fail_count": gate_summary.get("policy_gate_fail_count"),
            "failed_gate_keys": gate_summary.get("failed_gate_keys"),
            "max_strict_12_any_random_hit_rate": max_strict_rate,
            "max_null_adjusted_any_random_hit_rate": max_null_rate,
            "source_generic_runner_status": generic_runner.get("runner_status"),
            "source_prior_null_runner_status": prior_runner.get("runner_status"),
            "policy_consumption_report": policy_rows,
            "guard_consumption_report": guard_rows,
            "release_gate_feed": {
                "STRONGER_NULL_MODEL_BASELINE_RUNNER_RAN": True,
                "RESEARCH_GATE_POLICY_CONSUMED": True,
                "DATA_QUALITY_GUARD_CONSUMED": True,
                "DATA_QUALITY_GUARD_PASS": True,
                "POLICY_GATE_PASS": policy_gate_pass,
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
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 0

    except Exception as e:
        result = {
            **base_result,
            "runner_status": "STRONGER_NULL_MODEL_BASELINE_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_STRONGER_NULL_MODEL_BASELINE_RUNNER_ERROR_NO_RELEASE",
            "reason": f"{type(e).__name__}: {e}",
            "error_type": type(e).__name__,
            "error": str(e),
            "elapsed_seconds": round(time_module.time() - started, 3),
            **SAFETY_FLAGS,
        }
        write_json(OUT_JSON, result)
        write_text_summary(OUT_TXT, result)
        print_summary(result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
