from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_offline_threshold_sweep_runner_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RUNNER_PLAN_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_runner_plan_v1"
    / "offline_research_runner_plan_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"offline_threshold_sweep_runner_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "offline_threshold_sweep_runner_latest.json"
LATEST_MD = OUT_ROOT / "offline_threshold_sweep_runner_latest.md"


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


def norm(x: Any) -> str:
    return str(x or "").strip().lower()


def to_float(v: Any, default=None):
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return float(int(v))
        if isinstance(v, (int, float)):
            x = float(v)
            if math.isnan(x):
                return default
            return x
        if isinstance(v, str):
            s = v.strip().replace(",", "").replace("%", "")
            if not s:
                return default
            return float(s)
    except Exception:
        return default
    return default


def read_csv(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows

    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["_source_file"] = str(path)
                rows.append(row)
    except Exception:
        pass

    return rows


def get_value(row: Dict[str, Any], names: List[str]) -> Any:
    lower = {norm(k): k for k in row.keys()}

    for name in names:
        n = norm(name)
        if n in lower:
            return row.get(lower[n])

    for k in row.keys():
        nk = norm(k)
        for name in names:
            if norm(name) in nk:
                return row.get(k)

    return None


def is_impulse_long(row: Dict[str, Any]) -> bool:
    for key in ["family_key", "family", "family_name", "strategy", "source_family"]:
        if norm(row.get(key)) == "impulse_long":
            return True

    return "impulse_long" in json.dumps(row, default=str).lower()


def trade_key(row: Dict[str, Any]) -> str:
    parts = [
        get_value(row, ["close_id"]),
        get_value(row, ["position_id"]),
        get_value(row, ["signal_id"]),
        get_value(row, ["inst_id", "coin"]),
        get_value(row, ["entry_time"]),
        get_value(row, ["exit_time"]),
        get_value(row, ["entry_price"]),
        get_value(row, ["exit_price"]),
    ]
    return "|".join(str(x or "") for x in parts)


def dedupe(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []

    for row in rows:
        key = trade_key(row)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)

    return out


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    pnl_values = []
    symbols = {}

    for row in rows:
        pnl = to_float(get_value(row, ["pnl", "realized_pnl", "net_pnl"]), None)
        coin = str(get_value(row, ["coin", "inst_id", "symbol", "ticker"]) or "UNKNOWN")

        if pnl is not None:
            pnl_values.append(pnl)
            symbols[coin] = symbols.get(coin, 0.0) + pnl

    wins = [x for x in pnl_values if x > 0]
    losses = [x for x in pnl_values if x < 0]

    if not pnl_values:
        return {
            "trade_count": len(rows),
            "pnl_count": 0,
            "win_rate": None,
            "total_pnl": None,
            "mean_pnl": None,
            "best_pnl": None,
            "worst_pnl": None,
            "top_loss_symbols": [],
            "top_win_symbols": [],
        }

    return {
        "trade_count": len(rows),
        "pnl_count": len(pnl_values),
        "win_count": len(wins),
        "loss_count": len(losses),
        "win_rate": len(wins) / len(pnl_values),
        "total_pnl": sum(pnl_values),
        "mean_pnl": sum(pnl_values) / len(pnl_values),
        "best_pnl": max(pnl_values),
        "worst_pnl": min(pnl_values),
        "top_loss_symbols": sorted(symbols.items(), key=lambda x: x[1])[:10],
        "top_win_symbols": sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:10],
    }


def find_rh1_plan_step(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for step in plan.get("run_order") or []:
        if step.get("source_hypothesis_id") == "RH1_IMPULSE_STRENGTH_THRESHOLD_TOO_LOW":
            return step
    return None


def run_threshold_sweep(step: Dict[str, Any]) -> Dict[str, Any]:
    planned_inputs = step.get("planned_inputs") or {}
    experiment_design = planned_inputs.get("experiment_design") or {}

    primary_ledger = planned_inputs.get("primary_ledger")
    if not primary_ledger:
        return {
            "run_ok": False,
            "error": "primary_ledger_missing_from_plan_step",
            "results": [],
        }

    ledger_path = Path(primary_ledger)

    rows = read_csv(ledger_path)
    impulse_rows = dedupe([r for r in rows if is_impulse_long(r)])

    parameter_grid = experiment_design.get("parameter_grid") or {}
    thresholds = parameter_grid.get("signal_ret3_min_bps") or [150, 200, 250, 300, 350, 400]
    entry_range_caps = parameter_grid.get("entry_range_max_bps") or [None]

    results = []

    for threshold in thresholds:
        for entry_cap in entry_range_caps:
            filtered = []

            for row in impulse_rows:
                ret3 = to_float(get_value(row, ["signal_ret3_bps"]), None)
                entry_range = to_float(get_value(row, ["entry_range_bps"]), None)

                if ret3 is None:
                    continue

                if ret3 < float(threshold):
                    continue

                if entry_cap is not None:
                    if entry_range is None:
                        continue
                    if entry_range > float(entry_cap):
                        continue

                filtered.append(row)

            summary = summarize_rows(filtered)

            results.append({
                "signal_ret3_min_bps": threshold,
                "entry_range_max_bps": entry_cap,
                "summary": summary,
            })

    baseline = summarize_rows(impulse_rows)

    ranked = sorted(
        results,
        key=lambda r: (
            r["summary"].get("total_pnl") if r["summary"].get("total_pnl") is not None else -999999,
            r["summary"].get("trade_count") or 0,
        ),
        reverse=True,
    )

    return {
        "run_ok": True,
        "primary_ledger": str(ledger_path),
        "input_rows": len(rows),
        "impulse_rows": len(impulse_rows),
        "baseline": baseline,
        "results": results,
        "ranked_results": ranked,
    }


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical: List[str] = []
    attention: List[str] = []
    info: List[str] = []

    plan = load_json(RUNNER_PLAN_LATEST)

    if plan is None:
        critical.append("runner_plan_latest_missing_or_unreadable")
        plan = {}

    drift_gate_ready = bool(plan.get("drift_gate_ready") is True)
    closed = plan.get("closed")
    drift_remaining = plan.get("drift_remaining")
    capital_remaining = plan.get("capital_remaining")

    rh1_step = find_rh1_plan_step(plan)

    if rh1_step is None:
        critical.append("rh1_threshold_sweep_plan_step_missing")

    execution_allowed_now = bool(
        rh1_step
        and rh1_step.get("execution_allowed_now") is True
        and drift_gate_ready is True
    )

    sweep_result: Dict[str, Any] = {
        "run_ok": False,
        "skipped": True,
        "reason": "gate_blocked_or_execution_not_allowed",
    }

    if critical:
        runner_status = "OFFLINE_THRESHOLD_SWEEP_RUNNER_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RUNNER_PLAN_INPUT"
        reason = "; ".join(critical)

    elif not execution_allowed_now:
        runner_status = "OFFLINE_THRESHOLD_SWEEP_RUNNER_GATE_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNER_READY_UNTIL_DRIFT_GATE_READY"
        reason = f"closed={closed}; drift_remaining={drift_remaining}; execution_allowed_now=False"

    else:
        sweep_result = run_threshold_sweep(rh1_step)

        if sweep_result.get("run_ok") is True:
            runner_status = "OFFLINE_THRESHOLD_SWEEP_RUNNER_COMPLETE"
            severity = "ATTENTION"
            allowed_scope = "OFFLINE_RESEARCH_ONLY"
            next_action = "REVIEW_THRESHOLD_SWEEP_RESULTS_AND_FEED_LESSON_MEMORY"
            reason = "offline threshold sweep completed read-only"
        else:
            runner_status = "OFFLINE_THRESHOLD_SWEEP_RUNNER_FAILED"
            severity = "CRITICAL"
            allowed_scope = "READ_ONLY_REVIEW"
            next_action = "INSPECT_THRESHOLD_SWEEP_FAILURE"
            reason = str(sweep_result.get("error"))

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "runner_status": runner_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "runner_plan_source": str(RUNNER_PLAN_LATEST),
        "source_hypothesis_id": "RH1_IMPULSE_STRENGTH_THRESHOLD_TOO_LOW",
        "experiment_type": "threshold_sweep",

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,
        "execution_allowed_now": execution_allowed_now,
        "execution_performed": bool(sweep_result.get("run_ok") is True),

        "plan_step": rh1_step,
        "sweep_result": sweep_result,

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
        },

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "offline_threshold_sweep_runner_v1_state.json"
    out_md = RUN_DIR / "offline_threshold_sweep_runner_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md_lines = [
        "# EDGE FACTORY OS OFFLINE THRESHOLD SWEEP RUNNER v1",
        "",
        f"runner_status: {runner_status}",
        f"severity: {severity}",
        f"allowed_scope: {allowed_scope}",
        f"next_action: {next_action}",
        f"reason: {reason}",
        "",
        "## Gate",
        "",
        f"closed: {closed}",
        f"drift_remaining: {drift_remaining}",
        f"capital_remaining: {capital_remaining}",
        f"drift_gate_ready: {drift_gate_ready}",
        f"execution_allowed_now: {execution_allowed_now}",
        f"execution_performed: {bool(sweep_result.get('run_ok') is True)}",
        "",
        "## Sweep Result",
        "",
        json.dumps(sweep_result, indent=2, default=str)[:12000],
        "",
        "## Safety",
        "",
        "read_only: True",
        "offline_only: True",
        "mutate_runtime_allowed: False",
        "launcher_allowed: False",
        "patch_runtime_allowed: False",
        "active_paper_allowed: False",
        "live_allowed: False",
        "capital_change_allowed: False",
        "family_disable_allowed: False",
        "real_orders_allowed: False",
        "",
        f"critical: {critical}",
        f"attention: {attention}",
        f"info: {info}",
    ]

    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    LATEST_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS OFFLINE THRESHOLD SWEEP RUNNER v1")
    print("=" * 100)
    print(f"runner_status: {runner_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("GATE")
    print("-" * 100)
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print(f"execution_allowed_now: {execution_allowed_now}")
    print(f"execution_performed: {bool(sweep_result.get('run_ok') is True)}")
    print()
    print("SWEEP RESULT")
    print("-" * 100)
    if sweep_result.get("run_ok") is True:
        print(f"primary_ledger: {sweep_result.get('primary_ledger')}")
        print(f"impulse_rows: {sweep_result.get('impulse_rows')}")
        print(f"baseline: {sweep_result.get('baseline')}")
        print("top ranked results:")
        for row in (sweep_result.get("ranked_results") or [])[:10]:
            print(row)
    else:
        print(sweep_result)
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
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
