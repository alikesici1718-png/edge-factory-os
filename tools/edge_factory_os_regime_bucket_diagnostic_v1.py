from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_regime_bucket_diagnostic_v1"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent

RUNNER_PLAN_LATEST = (
    BASE_DIR
    / "edge_factory_os_offline_research_runner_plan_v1"
    / "offline_research_runner_plan_latest.json"
)

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"regime_bucket_diagnostic_v1_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "regime_bucket_diagnostic_latest.json"
LATEST_MD = OUT_ROOT / "regime_bucket_diagnostic_latest.md"


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


def parse_dt(v: Any) -> Optional[datetime]:
    if not isinstance(v, str):
        return None

    s = v.strip()
    if not s:
        return None

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    for candidate in [s, s.replace(" ", "T")]:
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

    return None


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
        if step.get("source_hypothesis_id") == "RH3_LOW_PRECISION_ENTRY_OR_BAD_REGIME_FILTER":
            return step
    return None


def bucket_ret3(x: Optional[float]) -> str:
    if x is None:
        return "ret3_missing"
    if x < 0:
        return "ret3_negative"
    if x < 150:
        return "ret3_0_150"
    if x < 250:
        return "ret3_150_250"
    if x < 300:
        return "ret3_250_300"
    return "ret3_gt_300"


def bucket_ret6(x: Optional[float]) -> str:
    if x is None:
        return "ret6_missing"
    if x < 0:
        return "ret6_negative"
    if x < 150:
        return "ret6_0_150"
    if x < 300:
        return "ret6_150_300"
    if x < 500:
        return "ret6_300_500"
    return "ret6_gt_500"


def bucket_range(x: Optional[float]) -> str:
    if x is None:
        return "range_missing"
    if x < 100:
        return "range_lt_100"
    if x < 250:
        return "range_100_250"
    if x < 500:
        return "range_250_500"
    return "range_gt_500"


def bucket_mkt(x: Optional[float], label: str) -> str:
    if x is None:
        return f"{label}_missing"
    if x < -300:
        return f"{label}_lt_-300"
    if x < -100:
        return f"{label}_-300_-100"
    if x < 0:
        return f"{label}_-100_0"
    if x < 100:
        return f"{label}_0_100"
    if x < 300:
        return f"{label}_100_300"
    return f"{label}_gt_300"


def bucket_hour(hour: Optional[int]) -> str:
    if hour is None:
        return "hour_missing"
    if 0 <= hour < 4:
        return "hour_00_03"
    if 4 <= hour < 8:
        return "hour_04_07"
    if 8 <= hour < 12:
        return "hour_08_11"
    if 12 <= hour < 16:
        return "hour_12_15"
    if 16 <= hour < 20:
        return "hour_16_19"
    return "hour_20_23"


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    pnl_values = []
    symbol_pnl = defaultdict(float)

    for row in rows:
        pnl = to_float(row.get("_pnl"), None)
        symbol = str(row.get("_symbol") or "UNKNOWN")

        if pnl is not None:
            pnl_values.append(pnl)
            symbol_pnl[symbol] += pnl

    wins = [x for x in pnl_values if x > 0]
    losses = [x for x in pnl_values if x < 0]

    if not pnl_values:
        return {
            "trade_count": len(rows),
            "pnl_count": 0,
            "win_rate": None,
            "total_pnl": None,
            "mean_pnl": None,
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
        "top_loss_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1])[:10],
        "top_win_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1], reverse=True)[:10],
    }


def enrich_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(row)

    symbol = str(get_value(row, ["coin", "inst_id", "symbol", "ticker"]) or "UNKNOWN")
    pnl = to_float(get_value(row, ["pnl", "realized_pnl", "net_pnl"]), None)
    signal_ret3 = to_float(get_value(row, ["signal_ret3_bps", "coin_ret3_bps"]), None)
    signal_ret6 = to_float(get_value(row, ["signal_ret6_bps", "coin_ret6_bps"]), None)
    entry_range = to_float(get_value(row, ["entry_range_bps"]), None)
    mkt_ret3 = to_float(get_value(row, ["mkt_ret3_bps", "market_ret3_bps"]), None)
    mkt_ret6 = to_float(get_value(row, ["mkt_ret6_bps", "market_ret6_bps"]), None)
    net_ret = to_float(get_value(row, ["net_ret"]), None)
    gross_ret = to_float(get_value(row, ["gross_ret"]), None)

    exit_time = get_value(row, ["exit_time", "closed_at", "timestamp"])
    exit_dt = parse_dt(str(exit_time or ""))
    exit_hour = exit_dt.hour if exit_dt else None

    out["_symbol"] = symbol
    out["_pnl"] = pnl
    out["_signal_ret3_bps"] = signal_ret3
    out["_signal_ret6_bps"] = signal_ret6
    out["_entry_range_bps"] = entry_range
    out["_mkt_ret3_bps"] = mkt_ret3
    out["_mkt_ret6_bps"] = mkt_ret6
    out["_net_ret"] = net_ret
    out["_gross_ret"] = gross_ret
    out["_exit_hour_utc"] = exit_hour

    out["_bucket_ret3"] = bucket_ret3(signal_ret3)
    out["_bucket_ret6"] = bucket_ret6(signal_ret6)
    out["_bucket_entry_range"] = bucket_range(entry_range)
    out["_bucket_mkt_ret3"] = bucket_mkt(mkt_ret3, "mkt_ret3")
    out["_bucket_mkt_ret6"] = bucket_mkt(mkt_ret6, "mkt_ret6")
    out["_bucket_exit_hour"] = bucket_hour(exit_hour)

    return out


def bucket_table(rows: List[Dict[str, Any]], bucket_key: str) -> List[Dict[str, Any]]:
    groups = defaultdict(list)

    for row in rows:
        groups[str(row.get(bucket_key) or "missing")].append(row)

    table = []

    for bucket, bucket_rows in groups.items():
        summary = summarize_rows(bucket_rows)
        table.append({
            "bucket_key": bucket_key,
            "bucket": bucket,
            "summary": summary,
        })

    table.sort(
        key=lambda x: (
            x["summary"].get("total_pnl")
            if x["summary"].get("total_pnl") is not None
            else -999999,
            x["summary"].get("trade_count") or 0,
        ),
        reverse=True,
    )

    return table


def candidate_filter_results(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filters = [
        {
            "filter_id": "signal_ret3_ge_250",
            "description": "signal_ret3_bps >= 250",
            "fn": lambda r: (r.get("_signal_ret3_bps") is not None and r["_signal_ret3_bps"] >= 250),
        },
        {
            "filter_id": "signal_ret3_ge_300",
            "description": "signal_ret3_bps >= 300",
            "fn": lambda r: (r.get("_signal_ret3_bps") is not None and r["_signal_ret3_bps"] >= 300),
        },
        {
            "filter_id": "entry_range_lt_100",
            "description": "entry_range_bps < 100",
            "fn": lambda r: (r.get("_entry_range_bps") is not None and r["_entry_range_bps"] < 100),
        },
        {
            "filter_id": "entry_range_lt_250",
            "description": "entry_range_bps < 250",
            "fn": lambda r: (r.get("_entry_range_bps") is not None and r["_entry_range_bps"] < 250),
        },
        {
            "filter_id": "signal_ret3_ge_250_and_entry_range_lt_250",
            "description": "signal_ret3_bps >= 250 AND entry_range_bps < 250",
            "fn": lambda r: (
                r.get("_signal_ret3_bps") is not None
                and r["_signal_ret3_bps"] >= 250
                and r.get("_entry_range_bps") is not None
                and r["_entry_range_bps"] < 250
            ),
        },
        {
            "filter_id": "signal_ret3_ge_300_and_entry_range_lt_250",
            "description": "signal_ret3_bps >= 300 AND entry_range_bps < 250",
            "fn": lambda r: (
                r.get("_signal_ret3_bps") is not None
                and r["_signal_ret3_bps"] >= 300
                and r.get("_entry_range_bps") is not None
                and r["_entry_range_bps"] < 250
            ),
        },
    ]

    results = []

    for f in filters:
        selected = [r for r in rows if f["fn"](r)]
        excluded = [r for r in rows if not f["fn"](r)]

        results.append({
            "filter_id": f["filter_id"],
            "description": f["description"],
            "selected_summary": summarize_rows(selected),
            "excluded_summary": summarize_rows(excluded),
        })

    results.sort(
        key=lambda x: (
            x["selected_summary"].get("total_pnl")
            if x["selected_summary"].get("total_pnl") is not None
            else -999999,
            x["selected_summary"].get("trade_count") or 0,
        ),
        reverse=True,
    )

    return results


def run_regime_diagnostic(step: Dict[str, Any]) -> Dict[str, Any]:
    planned_inputs = step.get("planned_inputs") or {}
    primary_ledger = planned_inputs.get("primary_ledger")

    if not primary_ledger:
        return {
            "run_ok": False,
            "error": "primary_ledger_missing_from_plan_step",
        }

    ledger_path = Path(primary_ledger)

    raw_rows = read_csv(ledger_path)
    impulse_rows = dedupe([r for r in raw_rows if is_impulse_long(r)])
    enriched = [enrich_row(r) for r in impulse_rows]

    baseline = summarize_rows(enriched)

    bucket_tables = {
        "signal_ret3_bps": bucket_table(enriched, "_bucket_ret3"),
        "signal_ret6_bps": bucket_table(enriched, "_bucket_ret6"),
        "entry_range_bps": bucket_table(enriched, "_bucket_entry_range"),
        "mkt_ret3_bps": bucket_table(enriched, "_bucket_mkt_ret3"),
        "mkt_ret6_bps": bucket_table(enriched, "_bucket_mkt_ret6"),
        "exit_hour_utc": bucket_table(enriched, "_bucket_exit_hour"),
        "symbol": bucket_table(enriched, "_symbol"),
    }

    filters = candidate_filter_results(enriched)

    return {
        "run_ok": True,
        "primary_ledger": str(ledger_path),
        "input_rows": len(raw_rows),
        "impulse_rows": len(impulse_rows),
        "baseline": baseline,
        "bucket_tables": bucket_tables,
        "candidate_filter_results": filters,
        "available_columns_inferred": {
            "signal_ret3_bps": any(r.get("_signal_ret3_bps") is not None for r in enriched),
            "signal_ret6_bps": any(r.get("_signal_ret6_bps") is not None for r in enriched),
            "entry_range_bps": any(r.get("_entry_range_bps") is not None for r in enriched),
            "mkt_ret3_bps": any(r.get("_mkt_ret3_bps") is not None for r in enriched),
            "mkt_ret6_bps": any(r.get("_mkt_ret6_bps") is not None for r in enriched),
            "exit_hour_utc": any(r.get("_exit_hour_utc") is not None for r in enriched),
        },
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
        critical.append("rh3_regime_bucket_plan_step_missing")

    execution_allowed_now = bool(
        step
        and step.get("execution_allowed_now") is True
        and drift_gate_ready is True
    )

    diagnostic_result: Dict[str, Any] = {
        "run_ok": False,
        "skipped": True,
        "reason": "gate_blocked_or_execution_not_allowed",
    }

    if critical:
        diagnostic_status = "REGIME_BUCKET_DIAGNOSTIC_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_RUNNER_PLAN_INPUT"
        reason = "; ".join(critical)

    elif not execution_allowed_now:
        diagnostic_status = "REGIME_BUCKET_DIAGNOSTIC_GATE_BLOCKED"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_RUNNER_READY_UNTIL_DRIFT_GATE_READY"
        reason = f"closed={closed}; drift_remaining={drift_remaining}; execution_allowed_now=False"

    else:
        diagnostic_result = run_regime_diagnostic(step)

        if diagnostic_result.get("run_ok") is True:
            diagnostic_status = "REGIME_BUCKET_DIAGNOSTIC_COMPLETE"
            severity = "ATTENTION"
            allowed_scope = "OFFLINE_RESEARCH_ONLY"
            next_action = "REVIEW_REGIME_BUCKET_RESULTS_AND_FEED_RELEASE_GATE"
            reason = "regime bucket diagnostic completed read-only"
        else:
            diagnostic_status = "REGIME_BUCKET_DIAGNOSTIC_FAILED"
            severity = "CRITICAL"
            allowed_scope = "READ_ONLY_REVIEW"
            next_action = "INSPECT_REGIME_DIAGNOSTIC_FAILURE"
            reason = str(diagnostic_result.get("error"))

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "diagnostic_status": diagnostic_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "runner_plan_source": str(RUNNER_PLAN_LATEST),
        "source_hypothesis_id": "RH3_LOW_PRECISION_ENTRY_OR_BAD_REGIME_FILTER",
        "experiment_type": "regime_bucket_diagnostic",

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,
        "execution_allowed_now": execution_allowed_now,
        "execution_performed": bool(diagnostic_result.get("run_ok") is True),

        "plan_step": step,
        "diagnostic_result": diagnostic_result,

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

    out_json = RUN_DIR / "regime_bucket_diagnostic_v1_state.json"
    out_md = RUN_DIR / "regime_bucket_diagnostic_v1_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS REGIME BUCKET DIAGNOSTIC v1

diagnostic_status: {diagnostic_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

closed: {closed}  
drift_remaining: {drift_remaining}  
capital_remaining: {capital_remaining}  
drift_gate_ready: {drift_gate_ready}  
execution_allowed_now: {execution_allowed_now}  
execution_performed: {bool(diagnostic_result.get("run_ok") is True)}

diagnostic_result:
{json.dumps(diagnostic_result, indent=2, default=str)[:24000]}

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
    print("EDGE FACTORY OS REGIME BUCKET DIAGNOSTIC v1")
    print("=" * 100)
    print(f"diagnostic_status: {diagnostic_status}")
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
    print(f"execution_performed: {bool(diagnostic_result.get('run_ok') is True)}")
    print()
    print("DIAGNOSTIC RESULT")
    print("-" * 100)
    if diagnostic_result.get("run_ok") is True:
        print(f"primary_ledger: {diagnostic_result.get('primary_ledger')}")
        print(f"impulse_rows: {diagnostic_result.get('impulse_rows')}")
        print(f"baseline: {diagnostic_result.get('baseline')}")
        print("available_columns_inferred:")
        print(diagnostic_result.get("available_columns_inferred"))
        print("candidate_filter_results:")
        for row in diagnostic_result.get("candidate_filter_results") or []:
            print(row)
        print("bucket_tables:")
        for k, table in (diagnostic_result.get("bucket_tables") or {}).items():
            print(k)
            for row in table[:10]:
                print(row)
    else:
        print(diagnostic_result)
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
