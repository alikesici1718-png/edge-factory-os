from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_cost_sensitivity_matrix_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RUNNER_PLAN_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_runner_plan_v1"
    / "offline_research_runner_plan_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"cost_sensitivity_matrix_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "cost_sensitivity_matrix_latest.json"
LATEST_MD = OUT_ROOT / "cost_sensitivity_matrix_latest.md"


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


def find_plan_step(plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for step in plan.get("run_order") or []:
        if step.get("source_hypothesis_id") == "RH4_COST_SLIPPAGE_EDGE_TOO_THIN":
            return step
    return None


def summarize_pnl(rows: List[Dict[str, Any]], pnl_key: str = "pnl") -> Dict[str, Any]:
    values = []
    symbol_pnl = defaultdict(float)

    for row in rows:
        pnl = to_float(row.get(pnl_key), None)
        symbol = str(row.get("coin") or row.get("inst_id") or row.get("symbol") or "UNKNOWN")

        if pnl is not None:
            values.append(pnl)
            symbol_pnl[symbol] += pnl

    wins = [x for x in values if x > 0]
    losses = [x for x in values if x < 0]

    if not values:
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
        "pnl_count": len(values),
        "win_count": len(wins),
        "loss_count": len(losses),
        "win_rate": len(wins) / len(values),
        "total_pnl": sum(values),
        "mean_pnl": sum(values) / len(values),
        "best_pnl": max(values),
        "worst_pnl": min(values),
        "top_loss_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1])[:10],
        "top_win_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1], reverse=True)[:10],
    }


def normalize_trade(row: Dict[str, Any]) -> Dict[str, Any]:
    coin = str(get_value(row, ["coin", "inst_id", "symbol", "ticker"]) or "UNKNOWN")

    pnl = to_float(get_value(row, ["pnl", "realized_pnl", "net_pnl"]), None)
    net_ret = to_float(get_value(row, ["net_ret"]), None)
    gross_ret = to_float(get_value(row, ["gross_ret"]), None)

    fee_bps = to_float(get_value(row, ["fee_bps_total"]), 25.0)
    entry_slip_bps = to_float(get_value(row, ["entry_slip_bps"]), 25.0)
    exit_slip_bps = to_float(get_value(row, ["exit_slip_bps"]), 25.0)

    # Estimate notional from pnl/net_ret when possible.
    estimated_notional = None
    if pnl is not None and net_ret not in [None, 0]:
        estimated_notional = pnl / net_ret

    # If gross_ret missing but net_ret exists, infer gross_ret from current cost assumption.
    if gross_ret is None and net_ret is not None:
        current_cost_ret = ((fee_bps or 0.0) + (entry_slip_bps or 0.0) + (exit_slip_bps or 0.0)) / 10000.0
        gross_ret = net_ret + current_cost_ret

    return {
        "coin": coin,
        "pnl": pnl,
        "net_ret": net_ret,
        "gross_ret": gross_ret,
        "fee_bps_total": fee_bps,
        "entry_slip_bps": entry_slip_bps,
        "exit_slip_bps": exit_slip_bps,
        "estimated_notional": estimated_notional,
        "trade_key": trade_key(row),
    }


def scenario_cost_ret(scenario: Dict[str, Any]) -> float:
    fee = to_float(scenario.get("fee_bps_total"), 0.0) or 0.0
    entry = to_float(scenario.get("entry_slip_bps"), 0.0) or 0.0
    exit_ = to_float(scenario.get("exit_slip_bps"), 0.0) or 0.0
    return (fee + entry + exit_) / 10000.0


def run_cost_sensitivity(step: Dict[str, Any]) -> Dict[str, Any]:
    planned_inputs = step.get("planned_inputs") or {}
    experiment_design = planned_inputs.get("experiment_design") or {}
    primary_ledger = planned_inputs.get("primary_ledger")

    if not primary_ledger:
        return {
            "run_ok": False,
            "error": "primary_ledger_missing_from_plan_step",
        }

    ledger_path = Path(primary_ledger)

    raw_rows = read_csv(ledger_path)
    impulse_rows = dedupe([r for r in raw_rows if is_impulse_long(r)])
    trades = [normalize_trade(r) for r in impulse_rows]

    baseline_rows = []
    for t in trades:
        baseline_rows.append({
            "coin": t["coin"],
            "pnl": t["pnl"],
        })

    baseline = summarize_pnl(baseline_rows)

    cost_scenarios = experiment_design.get("cost_scenarios") or [
        {"name": "current", "fee_bps_total": 25, "entry_slip_bps": 25, "exit_slip_bps": 25},
        {"name": "half_slippage", "fee_bps_total": 25, "entry_slip_bps": 12.5, "exit_slip_bps": 12.5},
        {"name": "fee_only", "fee_bps_total": 25, "entry_slip_bps": 0, "exit_slip_bps": 0},
        {"name": "stress", "fee_bps_total": 25, "entry_slip_bps": 35, "exit_slip_bps": 35},
    ]

    scenario_results = []

    for scenario in cost_scenarios:
        scenario_name = scenario.get("name")
        cost_ret = scenario_cost_ret(scenario)

        scenario_rows = []
        usable_count = 0
        missing_count = 0

        for t in trades:
            gross_ret = t.get("gross_ret")
            notional = t.get("estimated_notional")

            if gross_ret is None or notional is None:
                missing_count += 1
                continue

            scenario_net_ret = gross_ret - cost_ret
            scenario_pnl = scenario_net_ret * notional

            usable_count += 1

            scenario_rows.append({
                "coin": t["coin"],
                "pnl": scenario_pnl,
                "scenario_net_ret": scenario_net_ret,
                "gross_ret": gross_ret,
                "estimated_notional": notional,
            })

        summary = summarize_pnl(scenario_rows)

        scenario_results.append({
            "scenario_name": scenario_name,
            "cost_bps_total": (to_float(scenario.get("fee_bps_total"), 0.0) or 0.0)
                              + (to_float(scenario.get("entry_slip_bps"), 0.0) or 0.0)
                              + (to_float(scenario.get("exit_slip_bps"), 0.0) or 0.0),
            "scenario": scenario,
            "usable_trade_count": usable_count,
            "missing_trade_count": missing_count,
            "summary": summary,
        })

    ranked = sorted(
        scenario_results,
        key=lambda x: (
            x["summary"].get("total_pnl") if x["summary"].get("total_pnl") is not None else -999999,
            x["summary"].get("trade_count") or 0,
        ),
        reverse=True,
    )

    current_result = None
    for r in scenario_results:
        if r.get("scenario_name") == "current":
            current_result = r
            break

    gross_edge_possible = False
    if ranked:
        best_total = ranked[0]["summary"].get("total_pnl")
        if best_total is not None and best_total > baseline.get("total_pnl", -999999):
            gross_edge_possible = True

    return {
        "run_ok": True,
        "primary_ledger": str(ledger_path),
        "input_rows": len(raw_rows),
        "impulse_rows": len(impulse_rows),
        "baseline_current_logged_pnl": baseline,
        "scenario_results": scenario_results,
        "ranked_scenarios": ranked,
        "current_scenario_result": current_result,
        "gross_edge_possible_under_better_cost": gross_edge_possible,
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

    step = find_plan_step(plan)

    if step is None:
        critical.append("rh4_cost_sensitivity_plan_step_missing")

    execution_allowed_now = bool(
        step
        and step.get("execution_allowed_now") is True
        and drift_gate_ready is True
    )

    matrix_result: Dict[str, Any] = {
        "run_ok": False,
        "skipped": True,
        "reason": "gate_blocked_or_execution_not_allowed",
    }

    if critical:
        matrix_status = "COST_SENSITIVITY_MATRIX_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RUNNER_PLAN_INPUT"
        reason = "; ".join(critical)

    elif not execution_allowed_now:
        matrix_status = "COST_SENSITIVITY_MATRIX_GATE_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNER_READY_UNTIL_DRIFT_GATE_READY"
        reason = f"closed={closed}; drift_remaining={drift_remaining}; execution_allowed_now=False"

    else:
        matrix_result = run_cost_sensitivity(step)

        if matrix_result.get("run_ok") is True:
            matrix_status = "COST_SENSITIVITY_MATRIX_COMPLETE"
            severity = "ATTENTION"
            allowed_scope = "OFFLINE_RESEARCH_ONLY"
            next_action = "REVIEW_COST_SENSITIVITY_AND_FEED_RELEASE_GATE"
            reason = "cost sensitivity matrix completed read-only"
        else:
            matrix_status = "COST_SENSITIVITY_MATRIX_FAILED"
            severity = "CRITICAL"
            allowed_scope = "READ_ONLY_REVIEW"
            next_action = "INSPECT_COST_SENSITIVITY_FAILURE"
            reason = str(matrix_result.get("error"))

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "matrix_status": matrix_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "runner_plan_source": str(RUNNER_PLAN_LATEST),
        "source_hypothesis_id": "RH4_COST_SLIPPAGE_EDGE_TOO_THIN",
        "experiment_type": "cost_sensitivity_matrix",

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,
        "execution_allowed_now": execution_allowed_now,
        "execution_performed": bool(matrix_result.get("run_ok") is True),

        "plan_step": step,
        "matrix_result": matrix_result,

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

    out_json = RUN_DIR / "cost_sensitivity_matrix_v1_state.json"
    out_md = RUN_DIR / "cost_sensitivity_matrix_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS COST SENSITIVITY MATRIX v1

matrix_status: {matrix_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

closed: {closed}  
drift_remaining: {drift_remaining}  
capital_remaining: {capital_remaining}  
drift_gate_ready: {drift_gate_ready}  
execution_allowed_now: {execution_allowed_now}  
execution_performed: {bool(matrix_result.get("run_ok") is True)}

matrix_result:
{json.dumps(matrix_result, indent=2, default=str)[:20000]}

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

critical: {critical}  
attention: {attention}  
info: {info}
"""
    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS COST SENSITIVITY MATRIX v1")
    print("=" * 100)
    print(f"matrix_status: {matrix_status}")
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
    print(f"execution_performed: {bool(matrix_result.get('run_ok') is True)}")
    print()
    print("MATRIX RESULT")
    print("-" * 100)
    if matrix_result.get("run_ok") is True:
        print(f"primary_ledger: {matrix_result.get('primary_ledger')}")
        print(f"impulse_rows: {matrix_result.get('impulse_rows')}")
        print(f"baseline_current_logged_pnl: {matrix_result.get('baseline_current_logged_pnl')}")
        print("ranked_scenarios:")
        for row in matrix_result.get("ranked_scenarios") or []:
            print(row)
    else:
        print(matrix_result)
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
