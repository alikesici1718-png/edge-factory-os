#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Null Model Permutation Baseline Runner v1

Purpose:
- Consume Null Model Permutation Baseline Contract v1.
- Consume previous Generic Research Runner diagnostics/negative controls/null models.
- Estimate false-positive rates for strict 12/12-style findings.
- Estimate null-adjusted random-hit rates.
- Produce a no-release baseline report.

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
from typing import Any, Dict, List, Optional, Tuple


BASE_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new")
REPO_DIR = Path(r"C:\Users\alike\OneDrive\Desktop\edge_lab_new\edge_factory_os_repo")

CONTRACT_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "contracts"
    / "null_model_permutation_baseline_contract_v1.json"
)

PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "null_model_permutation_baseline_plugin_v1.json"
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

OUT_DIR = BASE_DIR / "edge_factory_os_null_model_permutation_baseline_runner"
OUT_JSON = OUT_DIR / "null_model_permutation_baseline_runner_latest.json"
OUT_TXT = OUT_DIR / "null_model_permutation_baseline_runner_latest.txt"
OUT_RUN_CSV = OUT_DIR / "null_model_permutation_run_summary_latest.csv"
OUT_BASELINE_CSV = OUT_DIR / "null_model_baseline_false_positive_summary_latest.csv"
OUT_PVALUE_CSV = OUT_DIR / "null_model_empirical_p_value_table_latest.csv"
OUT_GUARD_CSV = OUT_DIR / "null_model_guard_consumption_report_latest.csv"

RUNNER_NAME = "edge_factory_os_null_model_permutation_baseline_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"
EXPECTED_PLUGIN_KEY = "NULL_MODEL_PERMUTATION_BASELINE_PLUGIN_V1"
EXPECTED_RESEARCH_KEY = "NULL_MODEL_AND_PERMUTATION_BASELINE_V1"

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
        for key in row.keys():
            if key not in fields:
                fields.append(key)

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
    s = str(value).strip().lower()
    return s in {"true", "1", "yes", "y", "pass"}


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


def build_guard_consumption_report(contract: Dict[str, Any], guard_feed: Dict[str, Any]) -> List[Dict[str, Any]]:
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


def normalize_diagnostic_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for row in rows:
        out.append({
            "source_type": row.get("diagnostic_type", "actual_feature"),
            "feature_name": row.get("feature_name"),
            "feature_family": row.get("feature_family"),
            "selection_direction": row.get("selection_direction"),
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "event_count": to_int(row.get("event_count")),
            "active_months": to_int(row.get("active_months")),
            "positive_months": to_int(row.get("positive_months")),
            "total_month_pnl_bps": to_float(row.get("total_month_pnl_bps")),
            "mean_bar_pnl_bps": to_float(row.get("mean_bar_pnl_bps")),
            "median_bar_pnl_bps": to_float(row.get("median_bar_pnl_bps")),
            "bar_win_rate": to_float(row.get("bar_win_rate")),
            "worst_month_bps": to_float(row.get("worst_month_bps")),
            "best_month_bps": to_float(row.get("best_month_bps")),
            "strict_12_pass": to_bool(row.get("strict_12_feature_signal_preview_pass")),
        })

    return out


def normalize_control_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for row in rows:
        out.append({
            "source_type": row.get("control_type", "negative_control"),
            "control_name": row.get("control_name", "unknown_control"),
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "event_count": to_int(row.get("event_count")),
            "active_months": to_int(row.get("active_months")),
            "positive_months": to_int(row.get("positive_months")),
            "total_month_pnl_bps": to_float(row.get("total_month_pnl_bps")),
            "mean_bar_pnl_bps": to_float(row.get("mean_bar_pnl_bps")),
            "median_bar_pnl_bps": to_float(row.get("median_bar_pnl_bps")),
            "bar_win_rate": to_float(row.get("bar_win_rate")),
            "worst_month_bps": to_float(row.get("worst_month_bps")),
            "best_month_bps": to_float(row.get("best_month_bps")),
            "strict_12_pass": to_bool(row.get("strict_12_control_preview_pass")),
        })

    return out


def normalize_null_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for row in rows:
        out.append({
            "null_model": row.get("null_model", "unknown_null"),
            "feature_name": row.get("feature_name"),
            "feature_family": row.get("feature_family"),
            "selection_direction": row.get("selection_direction"),
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "actual_total_month_pnl_bps": to_float(row.get("actual_total_month_pnl_bps")),
            "control_p50_total_month_pnl_bps": to_float(row.get("control_p50_total_month_pnl_bps")),
            "control_p90_total_month_pnl_bps": to_float(row.get("control_p90_total_month_pnl_bps")),
            "control_p95_total_month_pnl_bps": to_float(row.get("control_p95_total_month_pnl_bps")),
            "control_best_total_month_pnl_bps": to_float(row.get("control_best_total_month_pnl_bps")),
            "strict_12_feature_signal_preview_pass": to_bool(row.get("strict_12_feature_signal_preview_pass")),
            "null_adjusted_signal_pass": to_bool(row.get("null_adjusted_signal_pass")),
        })

    return out


def sample_control_like(
    controls: List[Dict[str, Any]],
    rng: random.Random,
    baseline_test: str,
) -> Dict[str, Any]:
    base = dict(rng.choice(controls))

    positive = int(base.get("positive_months", 0))
    active = int(base.get("active_months", 0))
    total = float(base.get("total_month_pnl_bps", 0.0))
    worst = float(base.get("worst_month_bps", 0.0))

    # Different null/permutation modes perturb the same empirical controls in distinct ways.
    if baseline_test == "random_feature_decile_baseline":
        pass

    elif baseline_test == "within_month_symbol_shuffle_baseline":
        total = total * rng.uniform(0.75, 1.25)
        positive = max(0, min(12, positive + rng.choice([-1, 0, 0, 1])))

    elif baseline_test == "month_label_permutation_baseline":
        # Reassign monthly signs under empirical positive probability.
        p = max(0.0, min(1.0, positive / 12.0 if active else 0.5))
        positive = sum(1 for _ in range(12) if rng.random() < p)
        total = total * rng.uniform(0.5, 1.5)

    elif baseline_test == "time_block_permutation_baseline":
        total = total + rng.gauss(0.0, max(1000.0, abs(total) * 0.20))
        positive = max(0, min(12, positive + rng.choice([-2, -1, 0, 1, 2])))

    elif baseline_test == "side_flip_baseline":
        total = -total
        positive = 12 - positive

    elif baseline_test == "hold_period_shuffle_baseline":
        total = total * rng.uniform(0.6, 1.4)
        active = 12
        positive = max(0, min(12, positive + rng.choice([-1, 0, 1])))

    elif baseline_test == "cost_perturbation_baseline":
        extra_cost = rng.uniform(0.0, 75.0)
        total = total - extra_cost * max(1, int(base.get("event_count", 0)) / 100.0)
        positive = max(0, min(12, positive - rng.choice([0, 0, 1])))

    elif baseline_test == "feature_rank_shuffle_baseline":
        total = total + rng.gauss(0.0, max(500.0, abs(total) * 0.10))
        positive = max(0, min(12, positive + rng.choice([-1, 0, 1])))

    strict = active >= 12 and positive >= 12 and total > 0.0

    base.update({
        "baseline_test": baseline_test,
        "active_months": active,
        "positive_months": positive,
        "total_month_pnl_bps": total,
        "worst_month_bps": worst,
        "strict_12_pass": strict,
    })

    return base


def run_permutation_baseline(
    *,
    baseline_tests: List[str],
    diagnostics: List[Dict[str, Any]],
    controls: List[Dict[str, Any]],
    null_rows: List[Dict[str, Any]],
    runs: int,
    rng_seed: int = 20260513,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(rng_seed)

    if not controls:
        controls = diagnostics[:]

    if not controls:
        return [], [], []

    diag_count = max(1, len(diagnostics))
    actual_best_total = max([float(x.get("total_month_pnl_bps", 0.0)) for x in diagnostics] or [0.0])
    actual_strict_count = sum(1 for x in diagnostics if bool(x.get("strict_12_pass")))
    actual_null_adjusted_count = sum(1 for x in null_rows if bool(x.get("null_adjusted_signal_pass")))

    control_totals = [float(x.get("total_month_pnl_bps", 0.0)) for x in controls]
    control_p95 = percentile(control_totals, 0.95)
    control_best = max(control_totals) if control_totals else 0.0

    run_rows: List[Dict[str, Any]] = []

    for baseline_test in baseline_tests:
        for run_id in range(1, runs + 1):
            sampled = [
                sample_control_like(controls, rng, baseline_test)
                for _ in range(diag_count)
            ]

            strict_hits = sum(1 for x in sampled if bool(x.get("strict_12_pass")))
            max_total = max([float(x.get("total_month_pnl_bps", 0.0)) for x in sampled] or [0.0])
            max_positive_months = max([int(x.get("positive_months", 0)) for x in sampled] or [0])
            max_active_months = max([int(x.get("active_months", 0)) for x in sampled] or [0])

            null_adjusted_hits = sum(
                1
                for x in sampled
                if bool(x.get("strict_12_pass"))
                and float(x.get("total_month_pnl_bps", 0.0)) > control_p95
                and float(x.get("total_month_pnl_bps", 0.0)) > control_best
            )

            any_strict = strict_hits > 0
            any_null_adjusted = null_adjusted_hits > 0

            run_rows.append({
                "baseline_test": baseline_test,
                "run_id": run_id,
                "diagnostic_slots_sampled": diag_count,
                "strict_12_random_hit_count": strict_hits,
                "null_adjusted_random_hit_count": null_adjusted_hits,
                "any_strict_12_random_hit": any_strict,
                "any_null_adjusted_random_hit": any_null_adjusted,
                "max_total_month_pnl_bps": max_total,
                "max_positive_months": max_positive_months,
                "max_active_months": max_active_months,
                "control_p95_total_month_pnl_bps": control_p95,
                "control_best_total_month_pnl_bps": control_best,
                "actual_best_total_month_pnl_bps": actual_best_total,
                "actual_strict_12_feature_signal_preview_count": actual_strict_count,
                "actual_null_adjusted_signal_count": actual_null_adjusted_count,
            })

    summary_rows: List[Dict[str, Any]] = []

    for baseline_test in baseline_tests:
        subset = [x for x in run_rows if x["baseline_test"] == baseline_test]
        if not subset:
            continue

        strict_any_rate = mean([1.0 if x["any_strict_12_random_hit"] else 0.0 for x in subset])
        null_any_rate = mean([1.0 if x["any_null_adjusted_random_hit"] else 0.0 for x in subset])
        avg_strict_hits = mean([float(x["strict_12_random_hit_count"]) for x in subset])
        avg_null_hits = mean([float(x["null_adjusted_random_hit_count"]) for x in subset])
        max_total_values = [float(x["max_total_month_pnl_bps"]) for x in subset]

        if null_any_rate > 0.10 or strict_any_rate > 0.25:
            interpretation = "FALSE_POSITIVE_RISK_HIGH"
        elif null_any_rate > 0.02 or strict_any_rate > 0.05:
            interpretation = "FALSE_POSITIVE_RISK_MODERATE"
        else:
            interpretation = "FALSE_POSITIVE_RISK_LOW"

        summary_rows.append({
            "baseline_test": baseline_test,
            "permutation_runs": len(subset),
            "strict_12_any_random_hit_rate": strict_any_rate,
            "null_adjusted_any_random_hit_rate": null_any_rate,
            "avg_strict_12_random_hit_count": avg_strict_hits,
            "avg_null_adjusted_random_hit_count": avg_null_hits,
            "p50_max_total_month_pnl_bps": percentile(max_total_values, 0.50),
            "p90_max_total_month_pnl_bps": percentile(max_total_values, 0.90),
            "p95_max_total_month_pnl_bps": percentile(max_total_values, 0.95),
            "p99_max_total_month_pnl_bps": percentile(max_total_values, 0.99),
            "actual_best_total_month_pnl_bps": actual_best_total,
            "actual_strict_12_feature_signal_preview_count": actual_strict_count,
            "actual_null_adjusted_signal_count": actual_null_adjusted_count,
            "interpretation": interpretation,
        })

    pvalue_rows: List[Dict[str, Any]] = []

    for baseline_test in baseline_tests:
        subset = [x for x in run_rows if x["baseline_test"] == baseline_test]
        if not subset:
            continue

        max_totals = [float(x["max_total_month_pnl_bps"]) for x in subset]
        empirical_p_value_best_total = (
            sum(1 for x in max_totals if x >= actual_best_total) + 1
        ) / (len(max_totals) + 1)

        strict_hit_p_value = (
            sum(1 for x in subset if int(x["strict_12_random_hit_count"]) >= actual_strict_count) + 1
        ) / (len(subset) + 1)

        null_adjusted_hit_p_value = (
            sum(1 for x in subset if int(x["null_adjusted_random_hit_count"]) >= actual_null_adjusted_count) + 1
        ) / (len(subset) + 1)

        pvalue_rows.append({
            "baseline_test": baseline_test,
            "empirical_p_value_actual_best_total": empirical_p_value_best_total,
            "empirical_p_value_strict_hit_count": strict_hit_p_value,
            "empirical_p_value_null_adjusted_hit_count": null_adjusted_hit_p_value,
            "actual_best_total_month_pnl_bps": actual_best_total,
            "actual_strict_12_feature_signal_preview_count": actual_strict_count,
            "actual_null_adjusted_signal_count": actual_null_adjusted_count,
            "permutation_runs": len(subset),
        })

    return run_rows, summary_rows, pvalue_rows


def summarize_baseline(summary_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not summary_rows:
        return {
            "overall_false_positive_assessment": "NO_BASELINE_ROWS",
            "max_strict_12_any_random_hit_rate": None,
            "max_null_adjusted_any_random_hit_rate": None,
        }

    max_strict_rate = max(float(x.get("strict_12_any_random_hit_rate", 0.0)) for x in summary_rows)
    max_null_rate = max(float(x.get("null_adjusted_any_random_hit_rate", 0.0)) for x in summary_rows)
    high_count = sum(1 for x in summary_rows if x.get("interpretation") == "FALSE_POSITIVE_RISK_HIGH")
    moderate_count = sum(1 for x in summary_rows if x.get("interpretation") == "FALSE_POSITIVE_RISK_MODERATE")

    if high_count > 0:
        assessment = "FALSE_POSITIVE_BASELINE_HIGH_TIGHTEN_RESEARCH_GATES"
        recommendation = "Tighten null-adjusted thresholds and do not expand plugin until baseline gates are stricter."
    elif moderate_count > 0:
        assessment = "FALSE_POSITIVE_BASELINE_MODERATE_USE_STRONGER_NULL_ADJUSTMENT"
        recommendation = "Plugin expansion may continue only with stricter null/permutation reporting."
    else:
        assessment = "FALSE_POSITIVE_BASELINE_LOW_PLUGIN_EXPANSION_ALLOWED_UNDER_GUARD"
        recommendation = "It is acceptable to expand the feature plugin under data-quality guard, still no candidate/release."

    return {
        "overall_false_positive_assessment": assessment,
        "recommendation": recommendation,
        "max_strict_12_any_random_hit_rate": max_strict_rate,
        "max_null_adjusted_any_random_hit_rate": max_null_rate,
        "high_false_positive_baseline_count": high_count,
        "moderate_false_positive_baseline_count": moderate_count,
    }


def write_text_summary(path: Path, result: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS NULL MODEL PERMUTATION BASELINE RUNNER v1")
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
        "baseline_test_count",
        "permutation_runs_per_test",
        "total_permutation_run_rows",
        "overall_false_positive_assessment",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "elapsed_seconds",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    lines.append("")
    lines.append("BASELINE SUMMARY")
    lines.append("-" * 100)
    for row in result.get("baseline_summary_rows", []):
        lines.append(
            f"{row.get('baseline_test')}: strict_any={row.get('strict_12_any_random_hit_rate')} "
            f"null_any={row.get('null_adjusted_any_random_hit_rate')} "
            f"interp={row.get('interpretation')}"
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
        "baseline_summary_csv",
        "empirical_p_value_csv",
        "guard_report_csv",
    ]:
        lines.append(f"{k}: {result.get(k)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS NULL MODEL PERMUTATION BASELINE RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {result.get('runner_status')}")
    print(f"severity: {result.get('severity')}")
    print(f"allowed_scope: {result.get('allowed_scope')}")
    print(f"next_action: {result.get('next_action')}")
    print(f"reason: {result.get('reason')}")
    print(f"contract_id: {result.get('contract_id')}")
    print(f"research_key: {result.get('research_key')}")
    print(f"plugin_key: {result.get('plugin_key')}")
    print(f"baseline_test_count: {result.get('baseline_test_count')}")
    print(f"permutation_runs_per_test: {result.get('permutation_runs_per_test')}")
    print(f"total_permutation_run_rows: {result.get('total_permutation_run_rows')}")
    print(f"overall_false_positive_assessment: {result.get('overall_false_positive_assessment')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"elapsed_seconds: {result.get('elapsed_seconds')}")
    print("")
    print("SAFETY")
    print("-" * 100)
    for k, v in SAFETY_FLAGS.items():
        print(f"{k}: {v}")
    print("")
    print(f"JSON: {result.get('output_json')}")
    print(f"TXT : {result.get('output_txt')}")
    print(f"CSV : {result.get('baseline_summary_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    plugin = load_json(PLUGIN_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    generic_runner = load_json(GENERIC_RUNNER_JSON, default={})

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_path": str(CONTRACT_JSON),
        "plugin_path": str(PLUGIN_JSON),
        "guard_feed_path": str(GUARD_FEED_JSON),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "research_key": contract.get("research_key"),
        "plugin_key": contract.get("plugin_key"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "permutation_run_csv": str(OUT_RUN_CSV),
        "baseline_summary_csv": str(OUT_BASELINE_CSV),
        "empirical_p_value_csv": str(OUT_PVALUE_CSV),
        "guard_report_csv": str(OUT_GUARD_CSV),
        **SAFETY_FLAGS,
    }

    try:
        contract_ready = bool(contract.get("contract_id")) and contract.get("research_key") == EXPECTED_RESEARCH_KEY
        plugin_ready = plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY and plugin.get("research_key") == EXPECTED_RESEARCH_KEY
        guard_pass = bool(guard_feed.get("guard_pass")) and bool(contract.get("guard_pass"))

        if not contract_ready or not plugin_ready or not guard_pass:
            result = {
                **base_result,
                "runner_status": "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_NULL_MODEL_CONTRACT_PLUGIN_OR_GUARD_NO_RELEASE",
                "reason": f"contract_ready={contract_ready}; plugin_ready={plugin_ready}; guard_pass={guard_pass}",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        guard_rows = build_guard_consumption_report(contract, guard_feed)
        write_csv(OUT_GUARD_CSV, guard_rows)

        if any(row.get("guard_pass") is False for row in guard_rows):
            result = {
                **base_result,
                "runner_status": "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_BLOCKED_GUARD_CONSUMPTION_FAILED",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "FIX_GUARD_CONSUMPTION_BEFORE_NULL_BASELINE",
                "reason": "One or more guard feed requirements failed or were not consumed.",
                "guard_consumption_report": guard_rows,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        diagnostic_rows = normalize_diagnostic_rows(read_csv_rows(GENERIC_DIAGNOSTIC_CSV))
        control_rows = normalize_control_rows(read_csv_rows(GENERIC_NEGATIVE_CONTROL_CSV))
        null_rows = normalize_null_rows(read_csv_rows(GENERIC_NULL_MODEL_CSV))

        if not diagnostic_rows or not control_rows:
            result = {
                **base_result,
                "runner_status": "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_BLOCKED_MISSING_PRIOR_OUTPUTS",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "RERUN_GENERIC_RESEARCH_RUNNER_OR_REBUILD_PRIOR_OUTPUTS",
                "reason": f"diagnostic_rows={len(diagnostic_rows)}; control_rows={len(control_rows)}; null_rows={len(null_rows)}",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text_summary(OUT_TXT, result)
            print_summary(result)
            return 2

        baseline_tests = plugin.get("baseline_tests")
        if not isinstance(baseline_tests, list) or not baseline_tests:
            baseline_tests = contract.get("baseline_tests") if isinstance(contract.get("baseline_tests"), list) else []

        if not baseline_tests:
            baseline_tests = [
                "random_feature_decile_baseline",
                "within_month_symbol_shuffle_baseline",
                "month_label_permutation_baseline",
                "time_block_permutation_baseline",
                "side_flip_baseline",
                "hold_period_shuffle_baseline",
                "cost_perturbation_baseline",
                "feature_rank_shuffle_baseline",
            ]

        runs = max(50, to_int(plugin.get("minimum_permutation_runs") or contract.get("minimum_permutation_runs"), 200))

        print(f"Running null/permutation baseline: tests={len(baseline_tests)}, runs_per_test={runs}")

        run_rows, summary_rows, pvalue_rows = run_permutation_baseline(
            baseline_tests=[str(x) for x in baseline_tests],
            diagnostics=diagnostic_rows,
            controls=control_rows,
            null_rows=null_rows,
            runs=runs,
        )

        write_csv(OUT_RUN_CSV, run_rows)
        write_csv(OUT_BASELINE_CSV, summary_rows)
        write_csv(OUT_PVALUE_CSV, pvalue_rows)

        baseline_summary = summarize_baseline(summary_rows)
        assessment = baseline_summary["overall_false_positive_assessment"]

        if assessment == "FALSE_POSITIVE_BASELINE_HIGH_TIGHTEN_RESEARCH_GATES":
            runner_status = "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_FALSE_POSITIVE_RISK_HIGH"
            severity = "ATTENTION"
            next_action = "BUILD_NULL_MODEL_EVALUATOR_TIGHTEN_RESEARCH_GATES_NO_RELEASE"
        elif assessment == "FALSE_POSITIVE_BASELINE_MODERATE_USE_STRONGER_NULL_ADJUSTMENT":
            runner_status = "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_FALSE_POSITIVE_RISK_MODERATE"
            severity = "ATTENTION"
            next_action = "BUILD_NULL_MODEL_EVALUATOR_STRENGTHEN_NULL_GATES_NO_RELEASE"
        elif assessment == "FALSE_POSITIVE_BASELINE_LOW_PLUGIN_EXPANSION_ALLOWED_UNDER_GUARD":
            runner_status = "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_FALSE_POSITIVE_RISK_LOW"
            severity = "ATTENTION"
            next_action = "BUILD_NULL_MODEL_EVALUATOR_ALLOW_PLUGIN_EXPANSION_UNDER_GUARD_NO_RELEASE"
        else:
            runner_status = "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_ATTENTION"
            severity = "ATTENTION"
            next_action = "BUILD_NULL_MODEL_EVALUATOR_REVIEW_BASELINE_NO_RELEASE"

        reason = (
            f"baseline_tests={len(baseline_tests)}; runs_per_test={runs}; "
            f"max_strict_rate={baseline_summary.get('max_strict_12_any_random_hit_rate')}; "
            f"max_null_rate={baseline_summary.get('max_null_adjusted_any_random_hit_rate')}; "
            f"assessment={assessment}"
        )

        result = {
            **base_result,
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": "READ_ONLY_RESEARCH",
            "next_action": next_action,
            "reason": reason,
            "baseline_test_count": len(baseline_tests),
            "baseline_tests": baseline_tests,
            "permutation_runs_per_test": runs,
            "total_permutation_run_rows": len(run_rows),
            "baseline_summary_rows": summary_rows,
            "empirical_p_value_rows": pvalue_rows,
            "overall_false_positive_assessment": assessment,
            "recommendation": baseline_summary.get("recommendation"),
            "max_strict_12_any_random_hit_rate": baseline_summary.get("max_strict_12_any_random_hit_rate"),
            "max_null_adjusted_any_random_hit_rate": baseline_summary.get("max_null_adjusted_any_random_hit_rate"),
            "high_false_positive_baseline_count": baseline_summary.get("high_false_positive_baseline_count"),
            "moderate_false_positive_baseline_count": baseline_summary.get("moderate_false_positive_baseline_count"),
            "source_generic_runner_status": generic_runner.get("runner_status"),
            "source_feature_count": generic_runner.get("feature_count"),
            "source_diagnostic_row_count": generic_runner.get("diagnostic_row_count"),
            "source_negative_control_row_count": generic_runner.get("negative_control_row_count"),
            "source_null_model_row_count": generic_runner.get("null_model_row_count"),
            "source_strict_12_feature_signal_preview_count": generic_runner.get("strict_12_feature_signal_preview_count"),
            "source_null_adjusted_signal_count": generic_runner.get("null_adjusted_signal_count"),
            "guard_consumption_report": guard_rows,
            "release_gate_feed": {
                "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_RAN": True,
                "DATA_QUALITY_GUARD_CONSUMED": True,
                "DATA_QUALITY_GUARD_PASS": True,
                "STRICT_MONTH_STABILITY_12_OF_12": True,
                "FALSE_POSITIVE_BASELINE_ASSESSMENT": assessment,
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
            "runner_status": "NULL_MODEL_PERMUTATION_BASELINE_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_NULL_MODEL_PERMUTATION_BASELINE_RUNNER_ERROR_NO_RELEASE",
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
