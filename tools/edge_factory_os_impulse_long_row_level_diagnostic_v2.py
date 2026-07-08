from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE = "edge_factory_os_impulse_long_row_level_diagnostic_v2"
NOW = datetime.now(timezone.utc)

REPO_DIR = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_DIR.parent
RUNTIME_DIR = BASE_DIR / "paper_run_gate_MASTER_UPPER_SYSTEM"

DRIFT_V3_LATEST = (
    BASE_DIR
    / "edge_factory_os_family_drift_review_v3"
    / "family_drift_review_v3_latest.json"
)

PRIMARY_LEDGER = RUNTIME_DIR / "live_impulse_event_long_paper" / "closed_trades.csv"

CONSISTENCY_LEDGERS = [
    RUNTIME_DIR / "global_closed_trades.csv",
    RUNTIME_DIR / "live_performance_report" / "live_closed_trades_all.csv",
]

OUT_ROOT = BASE_DIR / MODULE
RUN_DIR = OUT_ROOT / f"impulse_long_row_level_diagnostic_v2_{NOW.strftime('%Y%m%d_%H%M%S')}"
LATEST_JSON = OUT_ROOT / "impulse_long_row_level_diagnostic_v2_latest.json"
LATEST_MD = OUT_ROOT / "impulse_long_row_level_diagnostic_v2_latest.md"


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


def to_float(v: Any, default: Optional[float] = None) -> Optional[float]:
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

    for c in [s, s.replace(" ", "T")]:
        try:
            dt = datetime.fromisoformat(c)
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
    for k in ["family_key", "family", "family_name", "strategy", "source_family"]:
        if norm(row.get(k)) == "impulse_long":
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
        k = trade_key(row)
        if k in seen:
            continue
        seen.add(k)
        out.append(row)
    return out


def percentile(values: List[float], q: float) -> Optional[float]:
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    pos = (len(values) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


def summarize(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {
            "count": 0,
            "sum": None,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "p25": None,
            "p75": None,
        }

    return {
        "count": len(values),
        "sum": sum(values),
        "mean": sum(values) / len(values),
        "median": percentile(values, 0.50),
        "min": min(values),
        "max": max(values),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
    }


def bucket_ret3(x: Optional[float]) -> str:
    if x is None:
        return "missing"
    if x < 0:
        return "ret3_negative"
    if x < 150:
        return "ret3_0_150"
    if x < 300:
        return "ret3_150_300"
    return "ret3_gt_300"


def bucket_range(x: Optional[float]) -> str:
    if x is None:
        return "missing"
    if x < 100:
        return "range_lt_100"
    if x < 250:
        return "range_100_250"
    if x < 500:
        return "range_250_500"
    return "range_gt_500"


def analyze(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    impulse_rows = dedupe([r for r in rows if is_impulse_long(r)])

    pnl_values = []
    net_ret_values = []
    gross_ret_values = []
    fee_values = []
    entry_slip_values = []
    exit_slip_values = []
    hold_values = []

    symbol_pnl = defaultdict(float)
    symbol_count = Counter()

    ret3_bucket_pnl = defaultdict(float)
    ret3_bucket_count = Counter()

    range_bucket_pnl = defaultdict(float)
    range_bucket_count = Counter()

    exit_hour_pnl = defaultdict(float)
    exit_hour_count = Counter()

    enriched = []

    for row in impulse_rows:
        coin = str(get_value(row, ["coin", "inst_id", "symbol", "ticker"]) or "UNKNOWN")

        pnl = to_float(get_value(row, ["pnl", "realized_pnl", "net_pnl"]), None)
        net_ret = to_float(get_value(row, ["net_ret"]), None)
        gross_ret = to_float(get_value(row, ["gross_ret"]), None)
        fee = to_float(get_value(row, ["fee_bps_total"]), None)
        entry_slip = to_float(get_value(row, ["entry_slip_bps"]), None)
        exit_slip = to_float(get_value(row, ["exit_slip_bps"]), None)
        hold = to_float(get_value(row, ["hold_minutes_actual", "hold_minutes"]), None)
        ret3 = to_float(get_value(row, ["signal_ret3_bps"]), None)
        entry_range = to_float(get_value(row, ["entry_range_bps"]), None)

        exit_time = get_value(row, ["exit_time", "closed_at", "timestamp"])
        exit_dt = parse_dt(str(exit_time or ""))
        exit_hour = exit_dt.hour if exit_dt else None

        if pnl is not None:
            pnl_values.append(pnl)
            symbol_pnl[coin] += pnl
            ret3_bucket_pnl[bucket_ret3(ret3)] += pnl
            range_bucket_pnl[bucket_range(entry_range)] += pnl
            if exit_hour is not None:
                exit_hour_pnl[exit_hour] += pnl

        if net_ret is not None:
            net_ret_values.append(net_ret)
        if gross_ret is not None:
            gross_ret_values.append(gross_ret)
        if fee is not None:
            fee_values.append(fee)
        if entry_slip is not None:
            entry_slip_values.append(entry_slip)
        if exit_slip is not None:
            exit_slip_values.append(exit_slip)
        if hold is not None:
            hold_values.append(hold)

        symbol_count[coin] += 1
        ret3_bucket_count[bucket_ret3(ret3)] += 1
        range_bucket_count[bucket_range(entry_range)] += 1
        if exit_hour is not None:
            exit_hour_count[exit_hour] += 1

        enriched.append({
            "trade_key": trade_key(row),
            "coin": coin,
            "pnl": pnl,
            "net_ret": net_ret,
            "gross_ret": gross_ret,
            "fee_bps_total": fee,
            "entry_slip_bps": entry_slip,
            "exit_slip_bps": exit_slip,
            "hold_minutes_actual": hold,
            "signal_ret3_bps": ret3,
            "entry_range_bps": entry_range,
            "exit_hour_utc": exit_hour,
            "entry_time": get_value(row, ["entry_time"]),
            "exit_time": exit_time,
            "close_id": get_value(row, ["close_id"]),
            "position_id": get_value(row, ["position_id"]),
        })

    wins = [x for x in pnl_values if x > 0]
    losses = [x for x in pnl_values if x < 0]

    gross_minus_net_sum_gap = None
    if gross_ret_values and net_ret_values and len(gross_ret_values) == len(net_ret_values):
        gross_minus_net_sum_gap = sum(gross_ret_values) - sum(net_ret_values)

    worst_trades = sorted(
        [r for r in enriched if r["pnl"] is not None],
        key=lambda x: x["pnl"]
    )[:10]

    best_trades = sorted(
        [r for r in enriched if r["pnl"] is not None],
        key=lambda x: x["pnl"],
        reverse=True
    )[:10]

    return {
        "available": bool(impulse_rows),
        "input_rows": len(rows),
        "impulse_rows_deduped": len(impulse_rows),
        "pnl_count": len(pnl_values),
        "win_count": len(wins),
        "loss_count": len(losses),
        "win_rate": len(wins) / len(pnl_values) if pnl_values else None,
        "pnl_summary": summarize(pnl_values),
        "net_ret_summary": summarize(net_ret_values),
        "gross_ret_summary": summarize(gross_ret_values),
        "fee_bps_summary": summarize(fee_values),
        "entry_slip_bps_summary": summarize(entry_slip_values),
        "exit_slip_bps_summary": summarize(exit_slip_values),
        "hold_minutes_summary": summarize(hold_values),
        "gross_minus_net_ret_sum_gap": gross_minus_net_sum_gap,
        "symbol_count_top": symbol_count.most_common(20),
        "top_loss_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1])[:20],
        "top_win_symbols": sorted(symbol_pnl.items(), key=lambda x: x[1], reverse=True)[:20],
        "ret3_bucket_count": dict(ret3_bucket_count),
        "ret3_bucket_pnl": dict(ret3_bucket_pnl),
        "entry_range_bucket_count": dict(range_bucket_count),
        "entry_range_bucket_pnl": dict(range_bucket_pnl),
        "exit_hour_count": dict(sorted(exit_hour_count.items())),
        "exit_hour_pnl": dict(sorted(exit_hour_pnl.items())),
        "worst_trades": worst_trades,
        "best_trades": best_trades,
    }


def consistency_check(primary: Dict[str, Any], consistency_paths: List[Path]) -> Dict[str, Any]:
    checks = []

    primary_keys = set()

    primary_rows = [r for r in read_csv(PRIMARY_LEDGER) if is_impulse_long(r)]
    for row in primary_rows:
        primary_keys.add(trade_key(row))

    for path in consistency_paths:
        rows = [r for r in read_csv(path) if is_impulse_long(r)]
        keys = {trade_key(r) for r in rows}

        overlap = len(primary_keys.intersection(keys))
        missing_from_consistency = len(primary_keys - keys)
        extra_in_consistency = len(keys - primary_keys)

        checks.append({
            "path": str(path),
            "exists": path.exists(),
            "impulse_rows": len(rows),
            "unique_trade_keys": len(keys),
            "overlap_with_primary": overlap,
            "missing_primary_trades": missing_from_consistency,
            "extra_consistency_trades": extra_in_consistency,
        })

    return {
        "primary_trade_keys": len(primary_keys),
        "checks": checks,
    }


def build_findings(summary: Dict[str, Any], drift_gate_ready: bool) -> List[Dict[str, Any]]:
    findings = []

    if not summary.get("available"):
        return [{
            "finding_id": "F0_NO_PRIMARY_ROW_LEVEL_DATA",
            "severity": "CRITICAL",
            "claim": "Primary impulse_long ledger has no usable row-level rows.",
            "evidence": "available=False",
            "next_action": "find/export primary ledger",
        }]

    win_rate = summary.get("win_rate")
    pnl_sum = (summary.get("pnl_summary") or {}).get("sum")
    pnl_mean = (summary.get("pnl_summary") or {}).get("mean")
    gross_gap = summary.get("gross_minus_net_ret_sum_gap")

    if win_rate is not None and win_rate < 0.35:
        findings.append({
            "finding_id": "F1_PRIMARY_LOW_WIN_RATE",
            "severity": "HIGH",
            "claim": "Primary ledger confirms impulse_long low win rate.",
            "evidence": f"win_rate={win_rate:.4f}; rows={summary.get('impulse_rows_deduped')}",
            "next_action": "split failures by symbol, signal_ret3_bps, entry_range_bps, exit_hour_utc",
        })

    if pnl_sum is not None and pnl_sum < 0:
        findings.append({
            "finding_id": "F2_PRIMARY_NEGATIVE_TOTAL_PNL",
            "severity": "HIGH",
            "claim": "Primary ledger confirms negative impulse_long total PnL.",
            "evidence": f"total_pnl={pnl_sum:.6f}; mean_pnl={pnl_mean}",
            "next_action": "find whether losses are concentrated in symbols/regime or generally negative",
        })

    top_loss_symbols = summary.get("top_loss_symbols") or []
    if top_loss_symbols and pnl_sum is not None and pnl_sum < 0:
        worst_symbol, worst_symbol_pnl = top_loss_symbols[0]
        if worst_symbol_pnl < 0 and abs(worst_symbol_pnl) >= abs(pnl_sum) * 0.30:
            findings.append({
                "finding_id": "F3_PRIMARY_SYMBOL_LOSS_CONCENTRATION",
                "severity": "MEDIUM_HIGH",
                "claim": "Primary ledger shows material symbol-level loss concentration.",
                "evidence": f"worst_symbol={worst_symbol}; worst_symbol_pnl={worst_symbol_pnl:.6f}; total_pnl={pnl_sum:.6f}",
                "next_action": "build symbol/regime concentration diagnostic before any family action",
            })

    if gross_gap is not None and gross_gap > 0:
        findings.append({
            "finding_id": "F4_PRIMARY_COST_GAP_PRESENT",
            "severity": "MEDIUM",
            "claim": "Primary ledger shows gross-to-net gap from cost/slippage assumptions.",
            "evidence": f"gross_minus_net_ret_sum_gap={gross_gap:.8f}",
            "next_action": "inspect if edge is too thin after fee+slippage",
        })

    if not drift_gate_ready:
        findings.append({
            "finding_id": "F5_GATE_NOT_READY",
            "severity": "CONTROL",
            "claim": "Global drift gate is not ready; no mutation allowed.",
            "evidence": "closed<20 and drift_remaining>0",
            "next_action": "wait for next closed trade, rerun v4, drift v3, diagnostic v2",
        })

    return findings


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    critical = []
    attention = []
    info = []

    drift = load_json(DRIFT_V3_LATEST) or {}

    closed = drift.get("closed")
    drift_remaining = drift.get("drift_remaining")
    capital_remaining = drift.get("capital_remaining")
    drift_gate_ready = bool(drift.get("drift_gate_ready") is True)

    if not PRIMARY_LEDGER.exists():
        critical.append(f"primary_ledger_missing:{PRIMARY_LEDGER}")

    primary_rows = read_csv(PRIMARY_LEDGER)
    primary_summary = analyze(primary_rows)

    consistency = consistency_check(primary_summary, CONSISTENCY_LEDGERS)

    findings = build_findings(primary_summary, drift_gate_ready)

    high_findings = [
        f for f in findings
        if str(f.get("severity")).upper() in {"HIGH", "MEDIUM_HIGH"}
    ]

    if critical:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_V2_CRITICAL_BLOCKED"
        severity = "CRITICAL"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "FIX_PRIMARY_LEDGER_SOURCE"
        reason = "; ".join(critical)
    elif high_findings and not drift_gate_ready:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_V2_PRE_THRESHOLD_ATTENTION"
        severity = "ATTENTION"
        allowed_scope = "COLLECT_ONLY"
        next_action = "KEEP_COLLECTING_NO_CAPITAL_CHANGE_RERUN_AT_DRIFT_GATE"
        reason = f"primary_high_or_medium_high_findings={len(high_findings)}; drift_gate_ready=False"
    elif high_findings:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_V2_ATTENTION"
        severity = "ATTENTION"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "BUILD_RESEARCH_HYPOTHESES_FROM_PRIMARY_ROW_LEVEL_FINDINGS"
        reason = f"primary_high_or_medium_high_findings={len(high_findings)}"
    else:
        diagnostic_status = "IMPULSE_LONG_ROW_LEVEL_DIAGNOSTIC_V2_INFO"
        severity = "INFO"
        allowed_scope = "READ_ONLY_REVIEW"
        next_action = "CONTINUE_MONITORING"
        reason = "no high-severity primary row-level finding"

    result = {
        "module": MODULE,
        "created_at_utc": NOW.isoformat(),

        "diagnostic_status": diagnostic_status,
        "severity": severity,
        "allowed_scope": allowed_scope,
        "next_action": next_action,
        "reason": reason,

        "primary_ledger": str(PRIMARY_LEDGER),
        "consistency_ledgers": [str(p) for p in CONSISTENCY_LEDGERS],

        "closed": closed,
        "drift_remaining": drift_remaining,
        "capital_remaining": capital_remaining,
        "drift_gate_ready": drift_gate_ready,

        "primary_summary": primary_summary,
        "consistency_check": consistency,
        "findings": findings,

        "mutate_runtime_allowed": False,
        "launcher_allowed": False,
        "patch_runtime_allowed": False,
        "active_paper_allowed": False,
        "live_allowed": False,
        "capital_change_allowed": False,
        "family_disable_allowed": False,
        "real_orders_allowed": False,
        "execution_performed": False,

        "critical": critical,
        "attention": attention,
        "info": info,
    }

    out_json = RUN_DIR / "impulse_long_row_level_diagnostic_v2_state.json"
    out_md = RUN_DIR / "impulse_long_row_level_diagnostic_v2_report.md"

    dump_json(out_json, result)
    dump_json(LATEST_JSON, result)

    md = f"""# EDGE FACTORY OS IMPULSE LONG ROW LEVEL DIAGNOSTIC v2

diagnostic_status: {diagnostic_status}  
severity: {severity}  
allowed_scope: {allowed_scope}  
next_action: {next_action}  
reason: {reason}

primary_ledger: {PRIMARY_LEDGER}  
consistency_ledgers: {[str(p) for p in CONSISTENCY_LEDGERS]}

closed: {closed}  
drift_remaining: {drift_remaining}  
capital_remaining: {capital_remaining}  
drift_gate_ready: {drift_gate_ready}

primary_summary:
{json.dumps(primary_summary, indent=2, default=str)}

consistency_check:
{json.dumps(consistency, indent=2, default=str)}

findings:
{json.dumps(findings, indent=2, default=str)}

mutate_runtime_allowed: False  
launcher_allowed: False  
patch_runtime_allowed: False  
active_paper_allowed: False  
live_allowed: False  
capital_change_allowed: False  
family_disable_allowed: False  
real_orders_allowed: False  
execution_performed: False

critical: {critical}  
attention: {attention}  
info: {info}
"""

    out_md.write_text(md, encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")

    print("=" * 100)
    print("EDGE FACTORY OS IMPULSE LONG ROW LEVEL DIAGNOSTIC v2")
    print("=" * 100)
    print(f"diagnostic_status: {diagnostic_status}")
    print(f"severity: {severity}")
    print(f"allowed_scope: {allowed_scope}")
    print(f"next_action: {next_action}")
    print(f"reason: {reason}")
    print()
    print("PRIMARY LEDGER")
    print("-" * 100)
    print(PRIMARY_LEDGER)
    print()
    print("GATE")
    print("-" * 100)
    print(f"closed: {closed}")
    print(f"drift_remaining: {drift_remaining}")
    print(f"capital_remaining: {capital_remaining}")
    print(f"drift_gate_ready: {drift_gate_ready}")
    print()
    print("PRIMARY SUMMARY")
    print("-" * 100)
    print(f"available: {primary_summary.get('available')}")
    print(f"input_rows: {primary_summary.get('input_rows')}")
    print(f"impulse_rows_deduped: {primary_summary.get('impulse_rows_deduped')}")
    print(f"win_rate: {primary_summary.get('win_rate')}")
    print(f"pnl_summary: {primary_summary.get('pnl_summary')}")
    print(f"net_ret_summary: {primary_summary.get('net_ret_summary')}")
    print(f"fee_bps_summary: {primary_summary.get('fee_bps_summary')}")
    print(f"entry_slip_bps_summary: {primary_summary.get('entry_slip_bps_summary')}")
    print(f"exit_slip_bps_summary: {primary_summary.get('exit_slip_bps_summary')}")
    print(f"top_loss_symbols: {primary_summary.get('top_loss_symbols')}")
    print(f"top_win_symbols: {primary_summary.get('top_win_symbols')}")
    print(f"ret3_bucket_pnl: {primary_summary.get('ret3_bucket_pnl')}")
    print(f"entry_range_bucket_pnl: {primary_summary.get('entry_range_bucket_pnl')}")
    print()
    print("CONSISTENCY CHECK")
    print("-" * 100)
    print(consistency)
    print()
    print("FINDINGS")
    print("-" * 100)
    for f in findings:
        print(f)
    print()
    print("SAFETY")
    print("-" * 100)
    print("mutate_runtime_allowed: False")
    print("launcher_allowed: False")
    print("patch_runtime_allowed: False")
    print("active_paper_allowed: False")
    print("live_allowed: False")
    print("capital_change_allowed: False")
    print("family_disable_allowed: False")
    print("real_orders_allowed: False")
    print("execution_performed: False")
    print()
    print(f"latest_json: {LATEST_JSON}")
    print("=" * 100)

    return 0 if severity != "CRITICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
