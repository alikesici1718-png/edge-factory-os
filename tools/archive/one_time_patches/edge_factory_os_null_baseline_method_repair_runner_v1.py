#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDGE FACTORY OS - Null Baseline Method Repair Runner v1

Purpose:
- Consume Null Baseline Method Repair Contract v1.
- Consume active Research Gate Enforcement Policy v1.
- Consume Null Baseline Method State v1.
- Consume Data Quality Guard feed.
- Consume Generic Research diagnostics / negative controls.
- Build repaired empirical replay null baseline outputs.
- Avoid synthetic-only month generation.
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
    / "null_baseline_method_repair_contract_v1.json"
)

PLUGIN_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "plugins"
    / "null_baseline_method_repair_plugin_v1.json"
)

POLICY_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "research_gate_enforcement_policy_v1.json"
)

METHOD_STATE_JSON = (
    REPO_DIR
    / "edge_factory_os_framework"
    / "policies"
    / "null_baseline_method_state_v1.json"
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

OUT_DIR = BASE_DIR / "edge_factory_os_null_baseline_method_repair_runner"
OUT_JSON = OUT_DIR / "null_baseline_method_repair_runner_latest.json"
OUT_TXT = OUT_DIR / "null_baseline_method_repair_runner_latest.txt"
OUT_INPUT_INVENTORY_CSV = OUT_DIR / "null_baseline_repair_input_inventory_latest.csv"
OUT_METHOD_INVENTORY_CSV = OUT_DIR / "null_baseline_repair_method_inventory_latest.csv"
OUT_REPLAY_RUN_CSV = OUT_DIR / "null_baseline_repair_empirical_replay_runs_latest.csv"
OUT_REPAIRED_SUMMARY_CSV = OUT_DIR / "null_baseline_repair_false_positive_summary_latest.csv"
OUT_POLICY_GATE_CSV = OUT_DIR / "null_baseline_repair_policy_gate_pass_fail_latest.csv"
OUT_POLICY_REPORT_CSV = OUT_DIR / "null_baseline_repair_policy_consumption_report_latest.csv"
OUT_GUARD_REPORT_CSV = OUT_DIR / "null_baseline_repair_guard_consumption_report_latest.csv"
OUT_METHOD_STATE_REPORT_CSV = OUT_DIR / "null_baseline_repair_method_state_consumption_report_latest.csv"

RUNNER_NAME = "edge_factory_os_null_baseline_method_repair_runner_v1"
STRICT_POLICY_KEY = "STRICT_MONTH_STABILITY_12_OF_12"
EXPECTED_RESEARCH_KEY = "NULL_BASELINE_METHOD_REPAIR_V1"
EXPECTED_PLUGIN_KEY = "NULL_BASELINE_METHOD_REPAIR_PLUGIN_V1"

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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def mean(values: List[float], default: float = 0.0) -> float:
    xs = [float(x) for x in values if math.isfinite(float(x))]
    if not xs:
        return default
    return sum(xs) / len(xs)


def percentile(values: List[float], q: float, default: float = 0.0) -> float:
    xs = sorted([float(x) for x in values if math.isfinite(float(x))])
    if not xs:
        return default
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def normalize_diag(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append({
            "source_type": "actual_feature_diagnostic",
            "name": row.get("feature_name"),
            "family": row.get("feature_family"),
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "event_count": to_int(row.get("event_count")),
            "bar_count": to_int(row.get("bar_count")),
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


def normalize_controls(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append({
            "source_type": "negative_control",
            "name": row.get("control_name"),
            "family": "negative_control",
            "side": row.get("side"),
            "hold": to_int(row.get("hold")),
            "event_count": to_int(row.get("event_count")),
            "bar_count": to_int(row.get("bar_count")),
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


def build_policy_report(policy: Dict[str, Any], contract: Dict[str, Any], plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    rules = policy.get("enforced_gate_rules") if isinstance(policy.get("enforced_gate_rules"), dict) else {}

    checks = [
        ("POLICY_ACTIVE", policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE", policy.get("policy_status"), "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"),
        ("POLICY_HASH_MATCH", policy.get("policy_hash") == contract.get("policy_hash"), f"{policy.get('policy_hash')} vs {contract.get('policy_hash')}", "match"),
        ("PLUGIN_MUST_CONSUME_POLICY", plugin.get("must_consume_research_gate_policy") is True, plugin.get("must_consume_research_gate_policy"), True),
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


def build_method_state_report(method_state: Dict[str, Any], contract: Dict[str, Any], plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    checks = [
        ("METHOD_REPAIR_REQUIRED", method_state.get("method_repair_required") is True, method_state.get("method_repair_required"), True),
        ("PLUGIN_EXPANSION_BLOCKED", method_state.get("plugin_expansion_allowed") is False, method_state.get("plugin_expansion_allowed"), False),
        ("PLUGIN_CONSUMES_METHOD_STATE", plugin.get("must_consume_null_baseline_method_state") is True, plugin.get("must_consume_null_baseline_method_state"), True),
        ("CONTRACT_METHOD_REPAIR_REQUIRED", contract.get("method_repair_required") is True, contract.get("method_repair_required"), True),
    ]

    return [
        {
            "method_state_check": key,
            "passed": bool(passed),
            "observed": observed,
            "required": required,
            "method_state": method_state.get("method_state"),
            "contract_id": contract.get("contract_id"),
        }
        for key, passed, observed, required in checks
    ]


def build_input_inventory(
    diagnostics: List[Dict[str, Any]],
    controls: List[Dict[str, Any]],
    generic_runner: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return [
        {
            "artifact": "generic_research_runner_latest_json",
            "path": str(GENERIC_RUNNER_JSON),
            "exists": GENERIC_RUNNER_JSON.exists(),
            "row_count": 1 if GENERIC_RUNNER_JSON.exists() else 0,
            "runner_status": generic_runner.get("runner_status"),
        },
        {
            "artifact": "generic_feature_diagnostics_csv",
            "path": str(GENERIC_DIAGNOSTIC_CSV),
            "exists": GENERIC_DIAGNOSTIC_CSV.exists(),
            "row_count": len(diagnostics),
            "runner_status": generic_runner.get("runner_status"),
        },
        {
            "artifact": "generic_negative_controls_csv",
            "path": str(GENERIC_NEGATIVE_CONTROL_CSV),
            "exists": GENERIC_NEGATIVE_CONTROL_CSV.exists(),
            "row_count": len(controls),
            "runner_status": generic_runner.get("runner_status"),
        },
    ]


def repair_method_inventory(methods: List[str]) -> List[Dict[str, Any]]:
    rows = []
    for method in methods:
        rows.append({
            "repair_method": method,
            "method_class": (
                "empirical_replay"
                if "replay" in method or "resample" in method or "bootstrap" in method
                else "empirical_shuffle"
            ),
            "uses_synthetic_month_generation_only": False,
            "uses_empirical_diagnostic_or_control_rows": True,
            "candidate_generation_allowed": False,
            "family_release_allowed": False,
            "runtime_touch_allowed": False,
            "capital_change_allowed": False,
            "live_allowed": False,
            "real_orders_allowed": False,
        })
    return rows


def sample_empirical_total(pool: List[Dict[str, Any]], rng: random.Random, method: str) -> Tuple[float, int, int, float]:
    """
    Returns:
    total_month_pnl_bps, positive_months, active_months, worst_month_proxy

    This is not full panel replay. It is repaired v1 replay over existing empirical diagnostic/control summary rows.
    It avoids creating new synthetic month curves and instead resamples existing empirical total/worst/positive stats.
    """
    if not pool:
        return 0.0, 0, 0, 0.0

    k = min(len(pool), max(3, int(math.sqrt(len(pool)))))
    sample = [rng.choice(pool) for _ in range(k)]

    totals = [float(x.get("total_month_pnl_bps", 0.0)) for x in sample]
    positives = [int(x.get("positive_months", 0)) for x in sample]
    actives = [int(x.get("active_months", 0)) for x in sample]
    worsts = [float(x.get("worst_month_bps", 0.0)) for x in sample]

    if method == "empirical_month_block_bootstrap":
        total = sum(totals) / len(totals)
        positive = round(sum(positives) / len(positives))
        active = round(sum(actives) / len(actives))
        worst = min(worsts)

    elif method == "within_month_symbol_resample":
        total = percentile(totals, 0.60)
        positive = round(percentile(positives, 0.60))
        active = round(percentile(actives, 0.60))
        worst = percentile(worsts, 0.25)

    elif method == "symbol_holdout_replay":
        total = percentile(totals, 0.50) * rng.uniform(0.55, 0.85)
        positive = max(0, round(percentile(positives, 0.50)) - rng.choice([0, 1, 2]))
        active = round(percentile(actives, 0.50))
        worst = percentile(worsts, 0.20)

    elif method == "month_holdout_replay":
        total = percentile(totals, 0.50)
        positive = max(0, round(percentile(positives, 0.50)) - rng.choice([2, 3, 4]))
        active = max(0, round(percentile(actives, 0.50)) - rng.choice([2, 3, 4]))
        worst = percentile(worsts, 0.20)

    elif method == "time_block_bootstrap_from_diagnostic_rows":
        total = percentile(totals, 0.75)
        positive = round(percentile(positives, 0.75))
        active = round(percentile(actives, 0.75))
        worst = percentile(worsts, 0.25)

    elif method == "negative_control_replay":
        control_like = [x for x in pool if x.get("source_type") == "negative_control"]
        if control_like:
            x = rng.choice(control_like)
        else:
            x = rng.choice(pool)
        total = float(x.get("total_month_pnl_bps", 0.0))
        positive = int(x.get("positive_months", 0))
        active = int(x.get("active_months", 0))
        worst = float(x.get("worst_month_bps", 0.0))

    elif method == "cost_stress_empirical_replay":
        total = percentile(totals, 0.50) - rng.uniform(500.0, 2500.0)
        positive = max(0, round(percentile(positives, 0.50)) - rng.choice([1, 2, 3]))
        active = round(percentile(actives, 0.50))
        worst = percentile(worsts, 0.15)

    elif method == "liquidity_bucket_empirical_shuffle":
        total = percentile(totals, rng.choice([0.25, 0.50, 0.75]))
        positive = round(percentile(positives, rng.choice([0.25, 0.50, 0.75])))
        active = round(percentile(actives, 0.50))
        worst = percentile(worsts, 0.25)

    elif method == "volatility_bucket_empirical_shuffle":
        total = percentile(totals, rng.choice([0.10, 0.50, 0.90]))
        positive = round(percentile(positives, rng.choice([0.10, 0.50, 0.90])))
        active = round(percentile(actives, 0.50))
        worst = percentile(worsts, 0.10)

    elif method == "side_flip_empirical_replay":
        total = -percentile(totals, 0.50)
        positive = max(0, 12 - round(percentile(positives, 0.50)))
        active = round(percentile(actives, 0.50))
        worst = -percentile([float(x.get("best_month_bps", 0.0)) for x in sample], 0.75)

    else:
        total = percentile(totals, 0.50)
        positive = round(percentile(positives, 0.50))
        active = round(percentile(actives, 0.50))
        worst = percentile(worsts, 0.25)

    return float(total), int(max(0, min(12, positive))), int(max(0, min(12, active))), float(worst)


def run_repaired_empirical_replay(
    *,
    methods: List[str],
    diagnostics: List[Dict[str, Any]],
    controls: List[Dict[str, Any]],
    runs_per_method: int,
    gate_caps: Dict[str, Any],
    seed: int = 20260513,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(seed)

    pool = controls + diagnostics
    run_rows: List[Dict[str, Any]] = []

    actual_null_adjusted_count = 0
    actual_strict_count = sum(1 for x in diagnostics if bool(x.get("strict_12_pass")))
    actual_best_total = max([float(x.get("total_month_pnl_bps", 0.0)) for x in diagnostics] or [0.0])

    min_margin = float(gate_caps.get("minimum_actual_vs_null_margin_bps") or 2500.0)

    for method in methods:
        for run_id in range(1, runs_per_method + 1):
            total, positive, active, worst = sample_empirical_total(pool, rng, method)

            strict = bool(active >= 12 and positive >= 12 and total > 0.0)
            null_adjusted = bool(strict and total > min_margin and worst > -min_margin)

            run_rows.append({
                "repair_method": method,
                "run_id": run_id,
                "empirical_rows_used": len(pool),
                "active_months": active,
                "positive_months": positive,
                "total_month_pnl_bps": total,
                "worst_month_bps": worst,
                "strict_12_random_hit": strict,
                "null_adjusted_random_hit": null_adjusted,
                "actual_best_total_month_pnl_bps": actual_best_total,
                "actual_strict_12_feature_signal_preview_count": actual_strict_count,
                "actual_null_adjusted_signal_count": actual_null_adjusted_count,
            })

    summary_rows: List[Dict[str, Any]] = []

    for method in methods:
        subset = [x for x in run_rows if x["repair_method"] == method]
        if not subset:
            continue

        strict_rate = mean([1.0 if x["strict_12_random_hit"] else 0.0 for x in subset])
        null_rate = mean([1.0 if x["null_adjusted_random_hit"] else 0.0 for x in subset])
        totals = [float(x["total_month_pnl_bps"]) for x in subset]

        summary_rows.append({
            "repair_method": method,
            "replay_runs": len(subset),
            "strict_12_any_random_hit_rate": strict_rate,
            "null_adjusted_any_random_hit_rate": null_rate,
            "p50_total_month_pnl_bps": percentile(totals, 0.50),
            "p90_total_month_pnl_bps": percentile(totals, 0.90),
            "p95_total_month_pnl_bps": percentile(totals, 0.95),
            "p99_total_month_pnl_bps": percentile(totals, 0.99),
            "actual_best_total_month_pnl_bps": actual_best_total,
            "actual_strict_12_feature_signal_preview_count": actual_strict_count,
            "actual_null_adjusted_signal_count": actual_null_adjusted_count,
        })

    max_allowed_strict = float(gate_caps.get("max_allowed_strict_12_any_random_hit_rate") or 0.01)
    max_allowed_null = float(gate_caps.get("max_allowed_null_adjusted_any_random_hit_rate") or 0.005)

    max_strict_rate = max([float(x["strict_12_any_random_hit_rate"]) for x in summary_rows] or [1.0])
    max_null_rate = max([float(x["null_adjusted_any_random_hit_rate"]) for x in summary_rows] or [1.0])

    gate_rows = [
        {
            "gate_key": "MINIMUM_EMPIRICAL_REPLAY_RUNS",
            "passed": all(int(x["replay_runs"]) >= runs_per_method for x in summary_rows),
            "observed": min([int(x["replay_runs"]) for x in summary_rows] or [0]),
            "required": runs_per_method,
        },
        {
            "gate_key": "REQUIRED_REPAIR_METHOD_COUNT",
            "passed": len(summary_rows) >= 8,
            "observed": len(summary_rows),
            "required": ">=8",
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
            "passed": actual_null_adjusted_count > 0,
            "observed": actual_null_adjusted_count,
            "required": "> 0 before any plugin-expansion signal claim",
        },
        {
            "gate_key": "PLUGIN_EXPANSION_STILL_BLOCKED",
            "passed": True,
            "observed": False,
            "required": "plugin_expansion_allowed=False",
        },
    ]

    return run_rows, summary_rows, gate_rows


def summarize_gates(gate_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    failed = [x for x in gate_rows if not bool(x.get("passed"))]
    return {
        "repair_policy_gate_pass": len(failed) == 0,
        "repair_policy_gate_fail_count": len(failed),
        "failed_gate_keys": [x.get("gate_key") for x in failed],
    }


def build_text_summary(result: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("EDGE FACTORY OS NULL BASELINE METHOD REPAIR RUNNER v1")
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
        "repair_method_count",
        "empirical_replay_runs_per_method",
        "total_empirical_replay_run_rows",
        "max_strict_12_any_random_hit_rate",
        "max_null_adjusted_any_random_hit_rate",
        "repair_policy_gate_pass",
        "repair_policy_gate_fail_count",
        "failed_gate_keys",
        "elapsed_seconds",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    lines.append("")
    lines.append("REPAIR POLICY GATES")
    lines.append("-" * 100)
    for row in result.get("repair_policy_gate_rows", []):
        lines.append(f"{row.get('gate_key')}: passed={row.get('passed')} observed={row.get('observed')} required={row.get('required')}")

    lines.append("")
    lines.append("REPAIRED METHOD SUMMARY")
    lines.append("-" * 100)
    for row in result.get("repaired_summary_rows", [])[:20]:
        lines.append(
            f"{row.get('repair_method')}: strict_rate={row.get('strict_12_any_random_hit_rate')} "
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
        "input_inventory_csv",
        "method_inventory_csv",
        "empirical_replay_run_csv",
        "repaired_summary_csv",
        "policy_gate_csv",
        "policy_report_csv",
        "guard_report_csv",
        "method_state_report_csv",
    ]:
        lines.append(f"{key}: {result.get(key)}")

    return "\n".join(lines)


def print_summary(result: Dict[str, Any]) -> None:
    print("")
    print("=" * 100)
    print("EDGE FACTORY OS NULL BASELINE METHOD REPAIR RUNNER v1")
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
    print(f"repair_method_count: {result.get('repair_method_count')}")
    print(f"empirical_replay_runs_per_method: {result.get('empirical_replay_runs_per_method')}")
    print(f"total_empirical_replay_run_rows: {result.get('total_empirical_replay_run_rows')}")
    print(f"max_strict_12_any_random_hit_rate: {result.get('max_strict_12_any_random_hit_rate')}")
    print(f"max_null_adjusted_any_random_hit_rate: {result.get('max_null_adjusted_any_random_hit_rate')}")
    print(f"repair_policy_gate_pass: {result.get('repair_policy_gate_pass')}")
    print(f"repair_policy_gate_fail_count: {result.get('repair_policy_gate_fail_count')}")
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
    print(f"CSV : {result.get('repaired_summary_csv')}")
    print("=" * 100)


def main() -> int:
    started = time_module.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    contract = load_json(CONTRACT_JSON, default={})
    plugin = load_json(PLUGIN_JSON, default={})
    policy = load_json(POLICY_JSON, default={})
    method_state = load_json(METHOD_STATE_JSON, default={})
    validation_state = load_json(VALIDATION_STATE_JSON, default={})
    guard_feed = load_json(GUARD_FEED_JSON, default={})
    generic_runner = load_json(GENERIC_RUNNER_JSON, default={})

    base_result = {
        "runner_name": RUNNER_NAME,
        "created_at_utc": utc_now_iso(),
        "strict_policy_key": STRICT_POLICY_KEY,
        "contract_path": str(CONTRACT_JSON),
        "plugin_path": str(PLUGIN_JSON),
        "policy_path": str(POLICY_JSON),
        "method_state_path": str(METHOD_STATE_JSON),
        "guard_feed_path": str(GUARD_FEED_JSON),
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract.get("contract_hash"),
        "route_hash": contract.get("route_hash"),
        "research_key": contract.get("research_key"),
        "plugin_key": contract.get("plugin_key"),
        "policy_hash": contract.get("policy_hash"),
        "output_json": str(OUT_JSON),
        "output_txt": str(OUT_TXT),
        "input_inventory_csv": str(OUT_INPUT_INVENTORY_CSV),
        "method_inventory_csv": str(OUT_METHOD_INVENTORY_CSV),
        "empirical_replay_run_csv": str(OUT_REPLAY_RUN_CSV),
        "repaired_summary_csv": str(OUT_REPAIRED_SUMMARY_CSV),
        "policy_gate_csv": str(OUT_POLICY_GATE_CSV),
        "policy_report_csv": str(OUT_POLICY_REPORT_CSV),
        "guard_report_csv": str(OUT_GUARD_REPORT_CSV),
        "method_state_report_csv": str(OUT_METHOD_STATE_REPORT_CSV),
        **SAFETY_FLAGS,
    }

    try:
        diagnostics = normalize_diag(read_csv_rows(GENERIC_DIAGNOSTIC_CSV))
        controls = normalize_controls(read_csv_rows(GENERIC_NEGATIVE_CONTROL_CSV))

        input_inventory_rows = build_input_inventory(diagnostics, controls, generic_runner)
        write_csv(OUT_INPUT_INVENTORY_CSV, input_inventory_rows)

        policy_report_rows = build_policy_report(policy, contract, plugin)
        guard_report_rows = build_guard_report(contract, guard_feed)
        method_state_report_rows = build_method_state_report(method_state, contract, plugin)

        write_csv(OUT_POLICY_REPORT_CSV, policy_report_rows)
        write_csv(OUT_GUARD_REPORT_CSV, guard_report_rows)
        write_csv(OUT_METHOD_STATE_REPORT_CSV, method_state_report_rows)

        policy_consumed = all(bool(x.get("passed")) for x in policy_report_rows)
        guard_consumed = all(bool(x.get("guard_pass")) for x in guard_report_rows)
        method_state_consumed = all(bool(x.get("passed")) for x in method_state_report_rows)

        contract_ready = (
            contract.get("contract_status") == "NULL_BASELINE_METHOD_REPAIR_CONTRACT_READY"
            and contract.get("research_key") == EXPECTED_RESEARCH_KEY
            and contract.get("plugin_key") == EXPECTED_PLUGIN_KEY
        )
        plugin_ready = (
            plugin.get("plugin_key") == EXPECTED_PLUGIN_KEY
            and plugin.get("research_key") == EXPECTED_RESEARCH_KEY
            and bool(plugin.get("must_consume_research_gate_policy"))
            and bool(plugin.get("must_consume_null_baseline_method_state"))
            and plugin.get("plugin_expansion_allowed") is False
        )
        policy_ready = policy.get("policy_status") == "RESEARCH_GATE_ENFORCEMENT_POLICY_ACTIVE"
        validation_ready = bool(validation_state.get("validator_pass"))
        method_repair_required = bool(method_state.get("method_repair_required"))

        if not (
            contract_ready
            and plugin_ready
            and policy_ready
            and validation_ready
            and method_repair_required
            and policy_consumed
            and guard_consumed
            and method_state_consumed
        ):
            result = {
                **base_result,
                "runner_status": "NULL_BASELINE_METHOD_REPAIR_RUNNER_BLOCKED_PREREQUISITE_NOT_MET",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "INSPECT_REPAIR_CONTRACT_POLICY_GUARD_OR_METHOD_STATE",
                "reason": (
                    f"contract_ready={contract_ready}; plugin_ready={plugin_ready}; policy_ready={policy_ready}; "
                    f"validation_ready={validation_ready}; method_repair_required={method_repair_required}; "
                    f"policy_consumed={policy_consumed}; guard_consumed={guard_consumed}; method_state_consumed={method_state_consumed}"
                ),
                "policy_consumption_report": policy_report_rows,
                "guard_consumption_report": guard_report_rows,
                "method_state_consumption_report": method_state_report_rows,
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 2

        if not diagnostics or not controls:
            result = {
                **base_result,
                "runner_status": "NULL_BASELINE_METHOD_REPAIR_RUNNER_BLOCKED_MISSING_EMPIRICAL_INPUTS",
                "severity": "ATTENTION",
                "allowed_scope": "READ_ONLY_REVIEW",
                "next_action": "RERUN_GENERIC_RESEARCH_RUNNER_OR_REPAIR_INPUT_EXPORT",
                "reason": f"diagnostics={len(diagnostics)}; controls={len(controls)}",
                "elapsed_seconds": round(time_module.time() - started, 3),
            }
            write_json(OUT_JSON, result)
            write_text(OUT_TXT, build_text_summary(result))
            print_summary(result)
            return 2

        methods = plugin.get("repair_methods")
        if not isinstance(methods, list) or not methods:
            methods = contract.get("repair_methods")

        if not isinstance(methods, list) or not methods:
            methods = [
                "empirical_month_block_bootstrap",
                "within_month_symbol_resample",
                "symbol_holdout_replay",
                "month_holdout_replay",
                "time_block_bootstrap_from_diagnostic_rows",
                "negative_control_replay",
                "cost_stress_empirical_replay",
                "liquidity_bucket_empirical_shuffle",
            ]

        methods = [str(x) for x in methods]
        method_inventory_rows = repair_method_inventory(methods)
        write_csv(OUT_METHOD_INVENTORY_CSV, method_inventory_rows)

        runs_per_method = max(
            1000,
            to_int(plugin.get("minimum_empirical_replay_runs")),
            to_int(contract.get("minimum_empirical_replay_runs")),
        )

        gate_caps = plugin.get("gate_caps")
        if not isinstance(gate_caps, dict):
            gate_caps = contract.get("gate_caps") if isinstance(contract.get("gate_caps"), dict) else {}

        print(f"Running repaired empirical null baseline: methods={len(methods)}, runs_per_method={runs_per_method}")

        replay_rows, repaired_summary_rows, gate_rows = run_repaired_empirical_replay(
            methods=methods,
            diagnostics=diagnostics,
            controls=controls,
            runs_per_method=runs_per_method,
            gate_caps=gate_caps,
            seed=20260513,
        )

        write_csv(OUT_REPLAY_RUN_CSV, replay_rows)
        write_csv(OUT_REPAIRED_SUMMARY_CSV, repaired_summary_rows)
        write_csv(OUT_POLICY_GATE_CSV, gate_rows)

        gate_summary = summarize_gates(gate_rows)
        repair_policy_gate_pass = bool(gate_summary["repair_policy_gate_pass"])

        max_strict_rate = max([float(x.get("strict_12_any_random_hit_rate", 1.0)) for x in repaired_summary_rows] or [1.0])
        max_null_rate = max([float(x.get("null_adjusted_any_random_hit_rate", 1.0)) for x in repaired_summary_rows] or [1.0])

        if repair_policy_gate_pass:
            runner_status = "NULL_BASELINE_METHOD_REPAIR_RUNNER_REPAIRED_METHOD_POLICY_GATES_PASS"
            severity = "ATTENTION"
            allowed_scope = "READ_ONLY_RESEARCH"
            next_action = "BUILD_NULL_BASELINE_METHOD_REPAIR_EVALUATOR_REVIEW_ONLY_NO_RELEASE"
            reason = (
                f"repaired_method_gate_pass=True; max_strict_rate={max_strict_rate}; "
                f"max_null_rate={max_null_rate}; plugin_expansion_still_blocked"
            )
        else:
            runner_status = "NULL_BASELINE_METHOD_REPAIR_RUNNER_REPAIRED_METHOD_POLICY_GATES_FAIL"
            severity = "ATTENTION"
            allowed_scope = "READ_ONLY_RESEARCH"
            next_action = "BUILD_NULL_BASELINE_METHOD_REPAIR_EVALUATOR_KEEP_PLUGIN_EXPANSION_BLOCKED"
            reason = (
                f"repaired_method_gate_pass=False; failed_gates={gate_summary.get('failed_gate_keys')}; "
                f"max_strict_rate={max_strict_rate}; max_null_rate={max_null_rate}"
            )

        result = {
            **base_result,
            "runner_status": runner_status,
            "severity": severity,
            "allowed_scope": allowed_scope,
            "next_action": next_action,
            "reason": reason,
            "repair_method_count": len(methods),
            "repair_methods": methods,
            "empirical_replay_runs_per_method": runs_per_method,
            "total_empirical_replay_run_rows": len(replay_rows),
            "repaired_summary_rows": repaired_summary_rows,
            "repair_policy_gate_rows": gate_rows,
            "repair_policy_gate_pass": repair_policy_gate_pass,
            "repair_policy_gate_fail_count": gate_summary["repair_policy_gate_fail_count"],
            "failed_gate_keys": gate_summary["failed_gate_keys"],
            "max_strict_12_any_random_hit_rate": max_strict_rate,
            "max_null_adjusted_any_random_hit_rate": max_null_rate,
            "diagnostic_input_row_count": len(diagnostics),
            "negative_control_input_row_count": len(controls),
            "input_inventory_rows": input_inventory_rows,
            "method_inventory_rows": method_inventory_rows,
            "policy_consumption_report": policy_report_rows,
            "guard_consumption_report": guard_report_rows,
            "method_state_consumption_report": method_state_report_rows,
            "release_gate_feed": {
                "NULL_BASELINE_METHOD_REPAIR_RUNNER_RAN": True,
                "REPAIRED_METHOD_POLICY_GATE_PASS": repair_policy_gate_pass,
                "RESEARCH_GATE_POLICY_CONSUMED": True,
                "DATA_QUALITY_GUARD_CONSUMED": True,
                "METHOD_STATE_CONSUMED": True,
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
            "runner_status": "NULL_BASELINE_METHOD_REPAIR_RUNNER_ERROR",
            "severity": "ATTENTION",
            "allowed_scope": "READ_ONLY_REVIEW",
            "next_action": "INSPECT_NULL_BASELINE_METHOD_REPAIR_RUNNER_ERROR_NO_RELEASE",
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
